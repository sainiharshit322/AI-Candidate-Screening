from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
import os
import uuid
from models.schemas import (
    JobDescriptionCreate,
    JobDescriptionResponse,
    EvaluateRequest,
    EvaluationResponse,
    CandidateResponse
)
from db.supabase_client import supabase, mock_db
from services.resume_parser import download_and_parse_resume
from services.github_service import analyze_github
from services.ai_evaluator import evaluate_candidate

router = APIRouter()

@router.post("/job-description", response_model=JobDescriptionResponse)
async def create_job_description(jd: JobDescriptionCreate):
    jd_id = str(uuid.uuid4())
    title = jd.title or "Job Description"
    content = jd.content

    if supabase:
        try:
            res = supabase.table("job_descriptions").insert({
                "id": jd_id,
                "title": title,
                "content": content
            }).execute()
            if res.data:
                return res.data[0]
        except Exception as e:
            print(f"Supabase JD insert error: {e}")
    
    mock_jd = {"id": jd_id, "title": title, "content": content}
    mock_db.job_descriptions.append(mock_jd)
    return mock_jd

@router.post("", response_model=Dict[str, int])
async def trigger_evaluation(req: EvaluateRequest):
    jd_id = req.job_description_id
    jd_content = ""
    
    # 1. Fetch Job Description (by ID or fallback to latest)
    if supabase:
        try:
            if jd_id and jd_id not in ["default-job-description-id", "latest", "default"]:
                jd_res = supabase.table("job_descriptions").select("*").eq("id", jd_id).execute()
                if jd_res.data:
                    jd_content = jd_res.data[0].get("content", "")
            
            if not jd_content:
                latest_res = supabase.table("job_descriptions").select("*").order("created_at", desc=True).limit(1).execute()
                if latest_res.data:
                    jd_content = latest_res.data[0].get("content", "")
                    jd_id = latest_res.data[0].get("id")
        except Exception as e:
            print(f"Supabase JD fetch error: {e}")

    if not jd_content:
        if jd_id:
            mock_jd = next((j for j in mock_db.job_descriptions if j.get("id") == jd_id), None)
            if mock_jd:
                jd_content = mock_jd.get("content", "")
        if not jd_content and mock_db.job_descriptions:
            mock_jd = mock_db.job_descriptions[-1]
            jd_content = mock_jd.get("content", "")
            jd_id = mock_jd.get("id")

    if not jd_content:
        jd_content = "Software Engineer proficient in Python, AI/ML models, system design, and database architecture."
        jd_id = str(uuid.uuid4())

    # 2. Fetch candidates to evaluate (uploaded stage or all candidates)
    candidates_to_eval = []
    if supabase:
        try:
            c_res = supabase.table("candidates").select("*").eq("stage", "uploaded").execute()
            candidates_to_eval = c_res.data or []
            if not candidates_to_eval:
                c_all = supabase.table("candidates").select("*").execute()
                candidates_to_eval = c_all.data or []
        except Exception as e:
            candidates_to_eval = [c for c in mock_db.candidates if c.get("stage") == "uploaded"] or mock_db.candidates
    else:
        candidates_to_eval = [c for c in mock_db.candidates if c.get("stage") == "uploaded"] or mock_db.candidates

    evaluated_count = 0

    # 3. Process each candidate (Stage 1: Resume + GitHub fit score only)
    for cand in candidates_to_eval:
        cand_id = cand["id"]
        resume_url = cand.get("resume_url") or ""
        github_url = cand.get("github_url") or ""
        cgpa = cand.get("cgpa") or 0.0

        # Step A: Parse Resume
        resume_text = await download_and_parse_resume(resume_url)

        # Step B: GitHub Analysis
        gh_result = analyze_github(github_url)
        github_score = gh_result.get("score", 0.0)
        github_summary = gh_result.get("summary", "")

        # Step C: Gemini AI Fit Evaluation
        ai_result = await evaluate_candidate(cand, jd_content, resume_text)
        ai_score = ai_result.get("score", 50.0)
        ai_reasoning = ai_result.get("reasoning", "")
        ai_strengths = ai_result.get("strengths", [])
        ai_gaps = ai_result.get("gaps", [])

        # Step D: Initial Score Calculation (Normalized based ONLY on Resume + GitHub + CGPA)
        cgpa_score = min((cgpa / 10.0) * 100.0, 100.0)
        
        # Initial score formula prior to test results: (35% AI + 25% GitHub + 5% CGPA) / 0.65
        initial_score = round(
            (ai_score * 0.35 + github_score * 0.25 + cgpa_score * 0.05) / 0.65,
            2
        )

        eval_data = {
            "id": str(uuid.uuid4()),
            "candidate_id": cand_id,
            "job_description_id": jd_id,
            "resume_text": resume_text,
            "ai_score": ai_score,
            "ai_reasoning": ai_reasoning,
            "ai_strengths": ai_strengths,
            "ai_gaps": ai_gaps,
            "github_score": github_score,
            "github_summary": github_summary,
            "test_la": None,
            "test_code": None,
            "total_score": initial_score
        }

        # Step E: Save evaluation & update stage
        if supabase:
            try:
                supabase.table("evaluations").insert(eval_data).execute()
                supabase.table("candidates").update({"stage": "evaluated"}).eq("id", cand_id).execute()
            except Exception as e:
                print(f"Supabase eval insert error: {e}")
                mock_db.evaluations.append(eval_data)
                cand["stage"] = "evaluated"
        else:
            mock_db.evaluations.append(eval_data)
            cand["stage"] = "evaluated"

        evaluated_count += 1

    return {"evaluated": evaluated_count}

@router.get("/results", response_model=List[CandidateResponse])
async def get_evaluation_results(threshold: Optional[float] = None):
    min_threshold = threshold if threshold is not None else float(os.getenv("SHORTLIST_THRESHOLD", "60"))
    
    if supabase:
        try:
            c_res = supabase.table("candidates").select("*").execute()
            candidates = c_res.data or []
            
            try:
                e_res = supabase.table("evaluations").select("*").execute()
                evaluations = e_res.data or []
            except Exception:
                evaluations = []

            eval_map = {}
            for ev in evaluations:
                cid = ev.get("candidate_id")
                if cid:
                    eval_map[cid] = ev

            results = []
            for c in candidates:
                latest_eval = eval_map.get(c["id"], {})
                total_score = latest_eval.get("total_score") or 0.0
                if total_score >= min_threshold:
                    c_data = {
                        **c,
                        "evaluation_id": latest_eval.get("id"),
                        "total_score": total_score,
                        "ai_score": latest_eval.get("ai_score"),
                        "ai_reasoning": latest_eval.get("ai_reasoning"),
                        "ai_strengths": latest_eval.get("ai_strengths"),
                        "ai_gaps": latest_eval.get("ai_gaps"),
                        "github_score": latest_eval.get("github_score"),
                        "github_summary": latest_eval.get("github_summary"),
                        "test_la": latest_eval.get("test_la"),
                        "test_code": latest_eval.get("test_code"),
                    }
                    results.append(c_data)
            results.sort(key=lambda x: x.get("total_score", 0.0), reverse=True)
            return results
        except Exception as e:
            print(f"Supabase fetch results error: {e}")
    
    all_candidates = mock_db.get_candidates()
    shortlisted = [c for c in all_candidates if (c.get("total_score") or 0.0) >= min_threshold]
    shortlisted.sort(key=lambda x: (x.get("total_score") or 0.0), reverse=True)
    return shortlisted
