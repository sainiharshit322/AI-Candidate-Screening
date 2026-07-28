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

def base_email(email_str: str) -> str:
    if not email_str:
        return ""
    em = email_str.lower().strip()
    if "+" in em and "@" in em:
        parts = em.split("@")
        user = parts[0].split("+")[0]
        return f"{user}@{parts[1]}"
    return em

@router.post("/upload", response_model=UploadResponse)
async def upload_candidates_csv(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    contents = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV file: {str(e)}")
    
    column_mapping = {}
    for col in df.columns:
        norm = str(col).strip().lower().replace(".", "_").replace(" ", "_")
        column_mapping[col] = norm
    df = df.rename(columns=column_mapping)
    
    def find_col(df_cols, patterns):
        for pat in patterns:
            for col in df_cols:
                if pat == col or pat in col:
                    return col
        return None

    email_col = find_col(df.columns, ["email", "e_mail", "mail"])
    if not email_col:
        raise HTTPException(status_code=400, detail="CSV must contain an 'email' column")
    
    name_col = find_col(df.columns, ["name", "candidate_name", "candidate", "full_name", "applicant"])
    s_no_col = find_col(df.columns, ["s_no", "sno", "sl_no", "sr_no", "s.no", "serial"])
    college_col = find_col(df.columns, ["college", "university", "institute", "school"])
    branch_col = find_col(df.columns, ["branch", "department", "dept", "stream", "major", "degree"])
    cgpa_col = find_col(df.columns, ["cgpa", "gpa", "percentage", "marks", "score"])
    ai_proj_col = find_col(df.columns, ["best_ai_project", "ai_project", "project", "best_project"])
    research_col = find_col(df.columns, ["research_work", "research", "publication", "paper"])
    github_col = find_col(df.columns, ["github_url", "github", "git"])
    resume_col = find_col(df.columns, ["resume_url", "resume", "cv", "drive"])

    inserted_count = 0
    updated_count = 0
    seen_emails_in_file = {}

    for idx, row in df.iterrows():
        raw_email = clean_str(row.get(email_col))
        if not raw_email:
            continue
        
        s_no_val = clean_int(row.get(s_no_col)) if s_no_col else (idx + 1)
        name_val = clean_str(row.get(name_col)) or f"Candidate {s_no_val}"
        
        if raw_email in seen_emails_in_file:
            seen_emails_in_file[raw_email] += 1
            if "@" in raw_email:
                parts = raw_email.split("@")
                email = f"{parts[0]}+s{s_no_val}@{parts[1]}"
            else:
                email = f"{raw_email}_{s_no_val}"
        else:
            seen_emails_in_file[raw_email] = 1
            email = raw_email

        candidate_data = {
            "s_no": s_no_val,
            "name": name_val,
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
                res = supabase.table("candidates").select("id").eq("email", email).execute()
                if res.data and len(res.data) > 0:
                    supabase.table("candidates").update(candidate_data).eq("email", email).execute()
                    updated_count += 1
                else:
                    supabase.table("candidates").insert(candidate_data).execute()
                    inserted_count += 1
            except Exception as e:
                print(f"Supabase candidate upsert error for {email}: {e}")
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
            c_res = supabase.table("candidates").select("*").execute()
            candidates = c_res.data or []
            
            try:
                e_res = supabase.table("evaluations").select("*").execute()
                evaluations = e_res.data or []
            except Exception as ee:
                evaluations = []

            eval_map = {}
            for ev in evaluations:
                cid = ev.get("candidate_id")
                if cid:
                    existing = eval_map.get(cid)
                    if not existing:
                        eval_map[cid] = ev
                    else:
                        if ev.get("test_code") is not None or (ev.get("total_score") or 0) > (existing.get("total_score") or 0):
                            eval_map[cid] = ev

            output = []
            for c in candidates:
                latest_eval = eval_map.get(c["id"], {})
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
            print(f"Error listing candidates from Supabase: {e}")
            return mock_db.get_candidates()
    else:
        return mock_db.get_candidates()

@router.get("/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(candidate_id: str):
    if supabase:
        try:
            res = supabase.table("candidates").select("*").eq("id", candidate_id).execute()
            if not res.data:
                raise HTTPException(status_code=404, detail="Candidate not found")
            c = res.data[0]
            
            try:
                e_res = supabase.table("evaluations").select("*").eq("candidate_id", candidate_id).execute()
                evals = e_res.data or []
                latest_eval = evals[-1] if evals else {}
            except Exception:
                latest_eval = {}

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
        except Exception as e:
            print(f"Error getting single candidate: {e}")
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

@router.delete("/clear-all")
async def clear_all_candidates():
    if supabase:
        try:
            res = supabase.table("candidates").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            count = len(res.data) if res.data else 0
            mock_db.candidates.clear()
            mock_db.evaluations.clear()
            mock_db.interviews.clear()
            return {"success": True, "count": count}
        except Exception as e:
            print(f"Supabase clear all error: {e}")
            count = len(mock_db.candidates)
            mock_db.candidates.clear()
            mock_db.evaluations.clear()
            mock_db.interviews.clear()
            return {"success": True, "count": count}
    else:
        count = len(mock_db.candidates)
        mock_db.candidates.clear()
        mock_db.evaluations.clear()
        mock_db.interviews.clear()
        return {"success": True, "count": count}

@router.delete("/{candidate_id}")
async def delete_candidate(candidate_id: str):
    if supabase:
        try:
            supabase.table("candidates").delete().eq("id", candidate_id).execute()
            mock_db.candidates = [c for c in mock_db.candidates if c.get("id") != candidate_id]
            mock_db.evaluations = [e for e in mock_db.evaluations if e.get("candidate_id") != candidate_id]
            mock_db.interviews = [i for i in mock_db.interviews if i.get("candidate_id") != candidate_id]
            return {"success": True, "deleted_id": candidate_id}
        except Exception as e:
            print(f"Error deleting candidate from Supabase: {e}")
            mock_db.candidates = [c for c in mock_db.candidates if c.get("id") != candidate_id]
            mock_db.evaluations = [e for e in mock_db.evaluations if e.get("candidate_id") != candidate_id]
            mock_db.interviews = [i for i in mock_db.interviews if i.get("candidate_id") != candidate_id]
            return {"success": True, "deleted_id": candidate_id}
    else:
        mock_db.candidates = [c for c in mock_db.candidates if c.get("id") != candidate_id]
        mock_db.evaluations = [e for e in mock_db.evaluations if e.get("candidate_id") != candidate_id]
        mock_db.interviews = [i for i in mock_db.interviews if i.get("candidate_id") != candidate_id]
        return {"success": True, "deleted_id": candidate_id}

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
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    contents = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV file: {str(e)}")

    column_mapping = {col: str(col).strip().lower().replace(" ", "_") for col in df.columns}
    df = df.rename(columns=column_mapping)

    def find_col(df_cols, patterns):
        for pat in patterns:
            for col in df_cols:
                if pat == col or pat in col:
                    return col
        return None

    email_col = find_col(df.columns, ["email", "e_mail", "mail"])
    s_no_col = find_col(df.columns, ["s_no", "sno", "sl_no", "sr_no", "s.no", "serial"])
    name_col = find_col(df.columns, ["name", "candidate_name", "candidate", "full_name"])
    la_col = find_col(df.columns, ["test_la", "la", "la_score"])
    code_col = find_col(df.columns, ["test_code", "code", "coding", "coding_score"])

    # Fetch all existing candidates ordered by s_no
    all_candidates = []
    if supabase:
        try:
            c_res = supabase.table("candidates").select("*").order("s_no").execute()
            all_candidates = c_res.data or []
        except Exception:
            all_candidates = mock_db.get_candidates()
    else:
        all_candidates = mock_db.get_candidates()

    updated_count = 0
    unmatched_emails = []
    used_candidate_ids = set()
    seen_test_emails = {}

    for row_idx, row in df.iterrows():
        raw_test_email = clean_str(row.get(email_col)) if email_col else None
        s_no_val = clean_int(row.get(s_no_col)) if s_no_col else None
        name_val = clean_str(row.get(name_col)) if name_col else None

        test_la = clean_float(row.get(la_col)) if la_col else 0.0
        test_code = clean_float(row.get(code_col)) if code_col else 0.0

        candidate = None

        # Matching Strategy 1: Match by s_no
        if s_no_val is not None:
            candidate = next((c for c in all_candidates if c["id"] not in used_candidate_ids and c.get("s_no") == s_no_val), None)

        # Matching Strategy 2: Match by candidate name
        if not candidate and name_val:
            candidate = next((c for c in all_candidates if c["id"] not in used_candidate_ids and c.get("name") and c.get("name").lower() == name_val.lower()), None)

        # Matching Strategy 3: Match by exact email
        if not candidate and raw_test_email:
            candidate = next((c for c in all_candidates if c["id"] not in used_candidate_ids and c.get("email") == raw_test_email), None)

        # Matching Strategy 4: Row position fallback among unused candidates
        if not candidate:
            unused = [c for c in all_candidates if c["id"] not in used_candidate_ids]
            if unused:
                candidate = unused[0]

        if not candidate:
            if raw_test_email:
                unmatched_emails.append(raw_test_email)
            continue

        cand_id = candidate["id"]
        used_candidate_ids.add(cand_id)
        cgpa = candidate.get("cgpa") or 0.0

        # Handle duplicate email input in test results CSV safely:
        # Create a unique email alias if raw_test_email is repeated in test results CSV
        if raw_test_email and "@" in raw_test_email:
            if raw_test_email in seen_test_emails:
                seen_test_emails[raw_test_email] += 1
                parts = raw_test_email.split("@")
                target_email = f"{parts[0]}+test{seen_test_emails[raw_test_email]}@{parts[1]}"
            else:
                seen_test_emails[raw_test_email] = 1
                target_email = raw_test_email
        else:
            target_email = candidate["email"]

        if supabase:
            try:
                # 1. Update Candidate stage to test_done (and update email if unique)
                try:
                    supabase.table("candidates").update({
                        "email": target_email,
                        "stage": "test_done"
                    }).eq("id", cand_id).execute()
                except Exception:
                    # If Supabase unique constraint triggers on duplicate email, update stage without throwing error
                    supabase.table("candidates").update({
                        "stage": "test_done"
                    }).eq("id", cand_id).execute()

                # 2. Update Evaluation record (test_la, test_code, total_score)
                eval_res = supabase.table("evaluations").select("*").eq("candidate_id", cand_id).execute()
                if eval_res.data:
                    eval_data = eval_res.data[-1]
                    ai_score = eval_data.get("ai_score") or 50.0
                    github_score = eval_data.get("github_score") or 0.0
                    
                    total_score = round(
                        ai_score * 0.35 +
                        github_score * 0.25 +
                        (test_code or 0.0) * 0.25 +
                        (test_la or 0.0) * 0.10 +
                        min((cgpa / 10.0) * 100.0, 100.0) * 0.05,
                        2
                    )
                    
                    supabase.table("evaluations").update({
                        "test_la": test_la,
                        "test_code": test_code,
                        "total_score": total_score
                    }).eq("id", eval_data["id"]).execute()
                else:
                    total_score = round(
                        (test_code or 0.0) * 0.25 +
                        (test_la or 0.0) * 0.10 +
                        min((cgpa / 10.0) * 100.0, 100.0) * 0.05,
                        2
                    )
                    supabase.table("evaluations").insert({
                        "id": str(uuid.uuid4()),
                        "candidate_id": cand_id,
                        "test_la": test_la,
                        "test_code": test_code,
                        "total_score": total_score
                    }).execute()
                
                updated_count += 1
            except Exception as e:
                print(f"Error updating test results for candidate {cand_id}: {e}")
        else:
            candidate["email"] = target_email
            candidate["stage"] = "test_done"
            eval_data = next((e for e in mock_db.evaluations if e.get("candidate_id") == cand_id), None)
            ai_score = eval_data.get("ai_score") if eval_data else 50.0
            github_score = eval_data.get("github_score") if eval_data else 0.0
            total_score = round(
                ai_score * 0.35 +
                github_score * 0.25 +
                (test_code or 0.0) * 0.25 +
                (test_la or 0.0) * 0.10 +
                min((cgpa / 10.0) * 100.0, 100.0) * 0.05,
                2
            )
            if eval_data:
                eval_data["test_la"] = test_la
                eval_data["test_code"] = test_code
                eval_data["total_score"] = total_score
            else:
                mock_db.evaluations.append({
                    "id": str(uuid.uuid4()),
                    "candidate_id": cand_id,
                    "test_la": test_la,
                    "test_code": test_code,
                    "total_score": total_score
                })
            updated_count += 1

    return {"updated": updated_count, "unmatched_emails": unmatched_emails}
