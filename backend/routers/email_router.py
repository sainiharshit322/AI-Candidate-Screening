from fastapi import APIRouter, HTTPException, Body, Query
from typing import List, Dict, Any, Optional
import os
from db.supabase_client import supabase, mock_db
from services.email_service import send_test_link, send_interview_invite

router = APIRouter()

@router.post("/send-test-links")
async def send_test_links(threshold: Optional[float] = None):
    min_threshold = threshold if threshold is not None else float(os.getenv("SHORTLIST_THRESHOLD", "60"))
    test_link = os.getenv("TEST_LINK", "https://example.com/assessment")

    candidates_to_send = []

    if supabase:
        try:
            res = supabase.table("candidates").select("*, evaluations(*)").eq("stage", "evaluated").execute()
            all_eval = res.data or []
            for c in all_eval:
                evals = c.get("evaluations", [])
                latest_eval = evals[-1] if evals else {}
                total_score = latest_eval.get("total_score") or 0.0
                if total_score >= min_threshold:
                    candidates_to_send.append(c)
        except Exception as e:
            print(f"Supabase candidate fetch error: {e}")
            all_c = mock_db.get_candidates()
            candidates_to_send = [
                c for c in all_c 
                if c.get("stage") == "evaluated" and (c.get("total_score") or 0.0) >= min_threshold
            ]
    else:
        all_c = mock_db.get_candidates()
        candidates_to_send = [
            c for c in all_c 
            if c.get("stage") == "evaluated" and (c.get("total_score") or 0.0) >= min_threshold
        ]

    sent_count = 0
    results = []

    for c in candidates_to_send:
        name = c.get("name") or "Candidate"
        email = c.get("email")
        if not email:
            continue
        
        email_res = send_test_link(name, email, test_link)
        sent_count += 1
        results.append({"candidate_id": c["id"], "email": email, "status": email_res.get("status")})

        # Update candidate stage to test_sent
        cand_id = c["id"]
        if supabase:
            try:
                supabase.table("candidates").update({"stage": "test_sent"}).eq("id", cand_id).execute()
            except Exception:
                for mc in mock_db.candidates:
                    if mc.get("id") == cand_id:
                        mc["stage"] = "test_sent"
        else:
            for mc in mock_db.candidates:
                if mc.get("id") == cand_id:
                    mc["stage"] = "test_sent"

    return {"sent_count": sent_count, "results": results}

@router.post("/send-interview")
async def send_interview(
    candidate_id: str = Body(..., embed=True),
    meet_link: Optional[str] = Body(None, embed=True),
    scheduled_at: Optional[str] = Body(None, embed=True)
):
    candidate = None
    if supabase:
        try:
            res = supabase.table("candidates").select("*").eq("id", candidate_id).execute()
            if res.data:
                candidate = res.data[0]
        except Exception:
            pass
            
    if not candidate:
        all_c = mock_db.get_candidates()
        candidate = next((c for c in all_c if c.get("id") == candidate_id), None)

    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    email = candidate.get("email")
    name = candidate.get("name") or "Candidate"
    
    link = meet_link or "https://meet.google.com/demo-screening"
    date_str = scheduled_at or "Upcoming scheduled slot"

    res = send_interview_invite(name, email, date_str, link)
    return {"status": "success", "result": res}
