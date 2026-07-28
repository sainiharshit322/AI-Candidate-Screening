from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone
import os
import uuid
from db.supabase_client import supabase, mock_db
from services.calendar_service import get_flow, save_credentials, schedule_interview
from services.email_service import send_interview_invite

router = APIRouter()

@router.get("/auth")
async def google_auth():
    try:
        flow = get_flow()
        authorization_url, state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent"
        )
        return RedirectResponse(authorization_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initiate Google OAuth: {str(e)}")

@router.get("/callback")
async def google_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code from Google")
    try:
        flow = get_flow()
        flow.fetch_token(code=code)
        creds = flow.credentials
        save_credentials(creds)
        return {"status": "success", "message": "Google Calendar OAuth authorization successful! You can return to the screening app."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OAuth callback failed: {str(e)}")

@router.post("/schedule")
async def schedule_interviews(threshold: Optional[float] = None):
    # Minimum overall score threshold for scheduling interviews (strictly >= 70%)
    min_threshold = threshold if threshold is not None else 70.0

    candidates_to_schedule = []

    if supabase:
        try:
            c_res = supabase.table("candidates").select("*").execute()
            all_candidates = c_res.data or []
            
            try:
                e_res = supabase.table("evaluations").select("*").execute()
                evaluations = e_res.data or []
            except Exception:
                evaluations = []

            # Map candidate_id -> best evaluation record containing test results
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

            for c in all_candidates:
                cand_id = c["id"]
                stage = c.get("stage")
                ev = eval_map.get(cand_id, {})
                
                total_score = ev.get("total_score") if ev.get("total_score") is not None else c.get("total_score")
                if total_score is None:
                    total_score = 0.0

                test_code = ev.get("test_code") if ev.get("test_code") is not None else c.get("test_code")
                test_la = ev.get("test_la") if ev.get("test_la") is not None else c.get("test_la")

                # Strictly require test completion (stage test_done/interview_scheduled or test scores present) AND overall score >= 70%
                has_completed_test = stage in ["test_done", "interview_scheduled"] or test_code is not None or test_la is not None

                if has_completed_test and total_score >= min_threshold:
                    candidates_to_schedule.append(c)

        except Exception as e:
            print(f"Supabase candidate query error in schedule_interviews: {e}")
            all_c = mock_db.get_candidates()
            for c in all_c:
                has_test = c.get("stage") in ["test_done", "interview_scheduled"] or c.get("test_code") is not None
                if has_test and (c.get("total_score") or 0.0) >= min_threshold:
                    candidates_to_schedule.append(c)
    else:
        all_c = mock_db.get_candidates()
        for c in all_c:
            has_test = c.get("stage") in ["test_done", "interview_scheduled"] or c.get("test_code") is not None
            if has_test and (c.get("total_score") or 0.0) >= min_threshold:
                candidates_to_schedule.append(c)

    # Calculate starting slot: next business day at 10:00 AM UTC
    now = datetime.now(timezone.utc)
    next_day = now + timedelta(days=1)
    while next_day.weekday() >= 5:  # 5=Saturday, 6=Sunday
        next_day += timedelta(days=1)
    
    current_slot = next_day.replace(hour=10, minute=0, second=0, microsecond=0)

    scheduled_results = []

    for cand in candidates_to_schedule:
        cand_id = cand["id"]
        name = cand.get("name") or "Candidate"
        email = cand.get("email")
        if not email:
            continue

        sched_res = schedule_interview(name, email, current_slot)
        event_id = sched_res.get("event_id")
        meet_link = sched_res.get("meet_link")

        interview_record = {
            "id": str(uuid.uuid4()),
            "candidate_id": cand_id,
            "scheduled_at": current_slot.isoformat(),
            "google_meet_link": meet_link,
            "calendar_event_id": event_id
        }

        if supabase:
            try:
                supabase.table("interviews").insert(interview_record).execute()
                supabase.table("candidates").update({"stage": "interview_scheduled"}).eq("id", cand_id).execute()
            except Exception as e:
                print(f"Supabase insert interview error: {e}")
                mock_db.interviews.append(interview_record)
                for mc in mock_db.candidates:
                    if mc.get("id") == cand_id:
                        mc["stage"] = "interview_scheduled"
        else:
            mock_db.interviews.append(interview_record)
            for mc in mock_db.candidates:
                if mc.get("id") == cand_id:
                    mc["stage"] = "interview_scheduled"

        # Send interview invite email strictly to sainiharshit322@gmail.com
        send_interview_invite(name, email, current_slot, meet_link)

        scheduled_results.append({
            "candidate_id": cand_id,
            "candidate_name": name,
            "candidate_email": email,
            "scheduled_at": current_slot.isoformat(),
            "google_meet_link": meet_link,
            "calendar_event_id": event_id
        })

        current_slot += timedelta(minutes=45)
        if current_slot.hour >= 16:
            current_slot += timedelta(days=1)
            while current_slot.weekday() >= 5:
                current_slot += timedelta(days=1)
            current_slot = current_slot.replace(hour=10, minute=0, second=0, microsecond=0)

    return {"scheduled_count": len(scheduled_results), "interviews": scheduled_results}
