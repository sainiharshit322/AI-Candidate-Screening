from fastapi import APIRouter, UploadFile, File, HTTPException, Body
from typing import List, Dict, Any, Optional
import pandas as pd
import io
import uuid
import os
from models.schemas import (
    CandidateResponse,
    StageUpdate,
    UploadResponse,
    UploadResultsResponse
)
from db.supabase_client import supabase, mock_db

router = APIRouter()

def clean_str(val: Any) -> Optional[str]:
    if pd.isna(val) or val is None:
        return None
    s = str(val).strip()
    return s if s else None

def clean_float(val: Any) -> Optional[float]:
    if pd.isna(val) or val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None

def clean_int(val: Any) -> Optional[int]:
    if pd.isna(val) or val is None:
        return None
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return None

@router.post("/upload", response_model=UploadResponse)
async def upload_candidates_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    contents = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV file: {str(e)}")
    
    # Standardize column names (lowercase, stripped)
    column_mapping = {}
    for col in df.columns:
        norm = col.strip().lower().replace(".", "_").replace(" ", "_")
        column_mapping[col] = norm
    df = df.rename(columns=column_mapping)
    
    # Column matching
    email_col = next((c for c in df.columns if "email" in c), None)
    if not email_col:
        raise HTTPException(status_code=400, detail="CSV must contain an 'email' column")
    
    name_col = next((c for c in df.columns if "name" in c), None)
    s_no_col = next((c for c in df.columns if "s_no" in c or "sno" in c or "s" in c), None)
    college_col = next((c for c in df.columns if "college" in c or "university" in c), None)
    branch_col = next((c for c in df.columns if "branch" in c or "dept" in c or "major" in c), None)
    cgpa_col = next((c for c in df.columns if "cgpa" in c or "gpa" in c), None)
    ai_proj_col = next((c for c in df.columns if "project" in c or "ai" in c), None)
    research_col = next((c for c in df.columns if "research" in c or "paper" in c), None)
    github_col = next((c for c in df.columns if "github" in c), None)
    resume_col = next((c for c in df.columns if "resume" in c or "cv" in c), None)

    inserted_count = 0
    updated_count = 0

    for _, row in df.iterrows():
        email = clean_str(row.get(email_col))
        if not email:
            continue
        
        candidate_data = {
            "s_no": clean_int(row.get(s_no_col)) if s_no_col else None,
            "name": clean_str(row.get(name_col)) if name_col else None,
            "email": email,
            "college": clean_str(row.get(college_col)) if college_col else None,
            "branch": clean_str(row.get(branch_col)) if branch_col else None,
            "cgpa": clean_float(row.get(cgpa_col)) if cgpa_col else None,
            "best_ai_project": clean_str(row.get(ai_proj_col)) if ai_proj_col else None,
            "research_work": clean_str(row.get(research_col)) if research_col else None,
            "github_url": clean_str(row.get(github_col)) if github_col else None,
            "resume_url": clean_str(row.get(resume_col)) if resume_col else None,
            "stage": "uploaded"
        }

        if supabase:
            try:
                # Check if candidate exists
                res = supabase.table("candidates").select("id").eq("email", email).execute()
                if res.data and len(res.data) > 0:
                    supabase.table("candidates").update(candidate_data).eq("email", email).execute()
                    updated_count += 1
                else:
                    supabase.table("candidates").insert(candidate_data).execute()
                    inserted_count += 1
            except Exception as e:
                # Fallback to mock_db if query fails
                is_update = any(c.get("email") == email for c in mock_db.candidates)
                mock_db.upsert_candidate(candidate_data)
                if is_update:
                    updated_count += 1
                else:
                    inserted_count += 1
        else:
            is_update = any(c.get("email") == email for c in mock_db.candidates)
            mock_db.upsert_candidate(candidate_data)
            if is_update:
                updated_count += 1
            else:
                inserted_count += 1

    return {"inserted": inserted_count, "updated": updated_count}

@router.get("", response_model=List[CandidateResponse])
async def list_candidates():
    if supabase:
        try:
            res = supabase.table("candidates").select("*, evaluations(*)").execute()
            candidates = res.data or []
            output = []
            for c in candidates:
                evals = c.get("evaluations", [])
                latest_eval = evals[-1] if evals else {}
                c_data = {
                    **c,
                    "evaluation_id": latest_eval.get("id"),
                    "total_score": latest_eval.get("total_score"),
                    "ai_score": latest_eval.get("ai_score"),
                    "ai_reasoning": latest_eval.get("ai_reasoning"),
                    "ai_strengths": latest_eval.get("ai_strengths"),
                    "ai_gaps": latest_eval.get("ai_gaps"),
                    "github_score": latest_eval.get("github_score"),
                    "github_summary": latest_eval.get("github_summary"),
                    "test_la": latest_eval.get("test_la"),
                    "test_code": latest_eval.get("test_code"),
                }
                output.append(c_data)
            return output
        except Exception as e:
            return mock_db.get_candidates()
    else:
        return mock_db.get_candidates()

@router.get("/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(candidate_id: str):
    if supabase:
        try:
            res = supabase.table("candidates").select("*, evaluations(*)").eq("id", candidate_id).execute()
            if not res.data:
                raise HTTPException(status_code=404, detail="Candidate not found")
            c = res.data[0]
            evals = c.get("evaluations", [])
            latest_eval = evals[-1] if evals else {}
            return {
                **c,
                "evaluation_id": latest_eval.get("id"),
                "total_score": latest_eval.get("total_score"),
                "ai_score": latest_eval.get("ai_score"),
                "ai_reasoning": latest_eval.get("ai_reasoning"),
                "ai_strengths": latest_eval.get("ai_strengths"),
                "ai_gaps": latest_eval.get("ai_gaps"),
                "github_score": latest_eval.get("github_score"),
                "github_summary": latest_eval.get("github_summary"),
                "test_la": latest_eval.get("test_la"),
                "test_code": latest_eval.get("test_code"),
            }
        except HTTPException:
            raise
        except Exception:
            candidates = mock_db.get_candidates()
            for c in candidates:
                if c.get("id") == candidate_id:
                    return c
            raise HTTPException(status_code=404, detail="Candidate not found")
    else:
        candidates = mock_db.get_candidates()
        for c in candidates:
            if c.get("id") == candidate_id:
                return c
        raise HTTPException(status_code=404, detail="Candidate not found")

@router.patch("/{candidate_id}/stage")
async def update_stage(candidate_id: str, stage_update: StageUpdate):
    stage = stage_update.stage
    if supabase:
        try:
            res = supabase.table("candidates").update({"stage": stage}).eq("id", candidate_id).execute()
            return {"success": True, "stage": stage}
        except Exception:
            for c in mock_db.candidates:
                if c.get("id") == candidate_id:
                    c["stage"] = stage
                    return {"success": True, "stage": stage}
            raise HTTPException(status_code=404, detail="Candidate not found")
    else:
        for c in mock_db.candidates:
            if c.get("id") == candidate_id:
                c["stage"] = stage
                return {"success": True, "stage": stage}
        raise HTTPException(status_code=404, detail="Candidate not found")

@router.post("/upload-results", response_model=UploadResultsResponse)
async def upload_test_results(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    contents = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV file: {str(e)}")

    column_mapping = {col: col.strip().lower().replace(" ", "_") for col in df.columns}
    df = df.rename(columns=column_mapping)

    email_col = next((c for c in df.columns if "email" in c), None)
    if not email_col:
        raise HTTPException(status_code=400, detail="CSV must contain an 'email' column")

    la_col = next((c for c in df.columns if "la" in c), None)
    code_col = next((c for c in df.columns if "code" in c or "coding" in c), None)

    updated_count = 0
    unmatched_emails = []

    for _, row in df.iterrows():
        email = clean_str(row.get(email_col))
        if not email:
            continue

        test_la = clean_float(row.get(la_col)) if la_col else 0.0
        test_code = clean_float(row.get(code_col)) if code_col else 0.0

        if supabase:
            try:
                cand_res = supabase.table("candidates").select("*").eq("email", email).execute()
                if not cand_res.data:
                    unmatched_emails.append(email)
                    continue
                
                candidate = cand_res.data[0]
                cand_id = candidate["id"]
                cgpa = candidate.get("cgpa") or 0.0

                eval_res = supabase.table("evaluations").select("*").eq("candidate_id", cand_id).execute()
                if eval_res.data:
                    eval_data = eval_res.data[-1]
                    ai_score = eval_data.get("ai_score") or 0.0
                    github_score = eval_data.get("github_score") or 0.0
                    
                    total_score = (
                        ai_score * 0.35 +
                        github_score * 0.25 +
                        (test_code or 0.0) * 0.25 +
                        (test_la or 0.0) * 0.10 +
                        min((cgpa / 10.0) * 100.0, 100.0) * 0.05
                    )
                    
                    supabase.table("evaluations").update({
                        "test_la": test_la,
                        "test_code": test_code,
                        "total_score": round(total_score, 2)
                    }).eq("id", eval_data["id"]).execute()
                else:
                    total_score = (
                        (test_code or 0.0) * 0.25 +
                        (test_la or 0.0) * 0.10 +
                        min((cgpa / 10.0) * 100.0, 100.0) * 0.05
                    )
                    supabase.table("evaluations").insert({
                        "candidate_id": cand_id,
                        "test_la": test_la,
                        "test_code": test_code,
                        "total_score": round(total_score, 2)
                    }).execute()
                
                supabase.table("candidates").update({"stage": "test_done"}).eq("id", cand_id).execute()
                updated_count += 1
            except Exception:
                # Mock DB fallback
                found = False
                for c in mock_db.candidates:
                    if c.get("email") == email:
                        found = True
                        cand_id = c["id"]
                        cgpa = c.get("cgpa") or 0.0
                        eval_data = next((e for e in mock_db.evaluations if e.get("candidate_id") == cand_id), None)
                        if eval_data:
                            eval_data["test_la"] = test_la
                            eval_data["test_code"] = test_code
                            ai_score = eval_data.get("ai_score") or 0.0
                            github_score = eval_data.get("github_score") or 0.0
                            total_score = (
                                ai_score * 0.35 +
                                github_score * 0.25 +
                                (test_code or 0.0) * 0.25 +
                                (test_la or 0.0) * 0.10 +
                                min((cgpa / 10.0) * 100.0, 100.0) * 0.05
                            )
                            eval_data["total_score"] = round(total_score, 2)
                        else:
                            total_score = (
                                (test_code or 0.0) * 0.25 +
                                (test_la or 0.0) * 0.10 +
                                min((cgpa / 10.0) * 100.0, 100.0) * 0.05
                            )
                            mock_db.evaluations.append({
                                "id": str(uuid.uuid4()),
                                "candidate_id": cand_id,
                                "test_la": test_la,
                                "test_code": test_code,
                                "total_score": round(total_score, 2)
                            })
                        c["stage"] = "test_done"
                        updated_count += 1
                        break
                if not found:
                    unmatched_emails.append(email)
        else:
            found = False
            for c in mock_db.candidates:
                if c.get("email") == email:
                    found = True
                    cand_id = c["id"]
                    cgpa = c.get("cgpa") or 0.0
                    eval_data = next((e for e in mock_db.evaluations if e.get("candidate_id") == cand_id), None)
                    if eval_data:
                        eval_data["test_la"] = test_la
                        eval_data["test_code"] = test_code
                        ai_score = eval_data.get("ai_score") or 0.0
                        github_score = eval_data.get("github_score") or 0.0
                        total_score = (
                            ai_score * 0.35 +
                            github_score * 0.25 +
                            (test_code or 0.0) * 0.25 +
                            (test_la or 0.0) * 0.10 +
                            min((cgpa / 10.0) * 100.0, 100.0) * 0.05
                        )
                        eval_data["total_score"] = round(total_score, 2)
                    else:
                        total_score = (
                            (test_code or 0.0) * 0.25 +
                            (test_la or 0.0) * 0.10 +
                            min((cgpa / 10.0) * 100.0, 100.0) * 0.05
                        )
                        mock_db.evaluations.append({
                            "id": str(uuid.uuid4()),
                            "candidate_id": cand_id,
                            "test_la": test_la,
                            "test_code": test_code,
                            "total_score": round(total_score, 2)
                        })
                    c["stage"] = "test_done"
                    updated_count += 1
                    break
            if not found:
                unmatched_emails.append(email)

    return {"updated": updated_count, "unmatched_emails": unmatched_emails}
