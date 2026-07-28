import resend
import os
from datetime import datetime
from typing import Any, Dict

def get_resend_client():
    api_key = os.getenv("RESEND_API_KEY")
    if api_key:
        resend.api_key = api_key
    return api_key

def send_test_link(candidate_name: str, candidate_email: str, test_link: str) -> Dict[str, Any]:
    api_key = get_resend_client()
    if not api_key:
        print(f"Skipping test link email to {candidate_email}: RESEND_API_KEY missing")
        return {"status": "skipped", "reason": "RESEND_API_KEY missing"}
    
    from_email = os.getenv("RESEND_FROM_EMAIL", "onboarding@resend.dev")
    fallback_email = os.getenv("RECRUITER_EMAIL", "sainiharshit322@gmail.com")
    name_display = candidate_name or "Candidate"
    
    payload = {
        "from": from_email,
        "to": candidate_email,
        "subject": "Next Step: Complete Your Technical Assessment",
        "html": f"""
        <p>Hi {name_display},</p>
        <p>Congratulations! You've been shortlisted for the next round.</p>
        <p>Please complete your assessment within 7 days:</p>
        <p><a href="{test_link}">Start Assessment →</a></p>
        <p>Best of luck!</p>
        """
    }

    try:
        r = resend.Emails.send(payload)
        return {"status": "sent", "recipient": candidate_email, "response": r}
    except Exception as e:
        print(f"Resend error sending to {candidate_email}: {e}. Retrying sending test mail to {fallback_email}")
        try:
            payload["to"] = fallback_email
            payload["subject"] = f"[Test Mail for {name_display}] Complete Your Technical Assessment ({candidate_email})"
            r = resend.Emails.send(payload)
            return {"status": "sent_fallback", "recipient": fallback_email, "original_target": candidate_email, "response": r}
        except Exception as e2:
            print(f"Fallback email send failed: {e2}")
            return {"status": "error", "error": str(e2)}

def send_interview_invite(candidate_name: str, candidate_email: str, scheduled_at: Any, meet_link: str) -> Dict[str, Any]:
    api_key = get_resend_client()
    if not api_key:
        print(f"Skipping interview invite to {candidate_email}: RESEND_API_KEY missing")
        return {"status": "skipped", "reason": "RESEND_API_KEY missing"}

    from_email = os.getenv("RESEND_FROM_EMAIL", "onboarding@resend.dev")
    fallback_email = os.getenv("RECRUITER_EMAIL", "sainiharshit322@gmail.com")
    name_display = candidate_name or "Candidate"
    
    if isinstance(scheduled_at, datetime):
        formatted_date = scheduled_at.strftime('%A, %B %d %Y at %I:%M %p UTC')
    else:
        formatted_date = str(scheduled_at)

    payload = {
        "from": from_email,
        "to": candidate_email,
        "subject": "Interview Scheduled",
        "html": f"""
        <p>Hi {name_display},</p>
        <p>Your interview has been scheduled for <strong>{formatted_date}</strong>.</p>
        <p>Join via Google Meet: <a href="{meet_link}">{meet_link}</a></p>
        <p>See you soon!</p>
        """
    }

    try:
        r = resend.Emails.send(payload)
        return {"status": "sent", "recipient": candidate_email, "response": r}
    except Exception as e:
        print(f"Resend error sending interview invite to {candidate_email}: {e}. Retrying sending interview mail to {fallback_email}")
        try:
            payload["to"] = fallback_email
            payload["subject"] = f"[Interview Mail for {name_display}] Interview Scheduled ({candidate_email})"
            r = resend.Emails.send(payload)
            return {"status": "sent_fallback", "recipient": fallback_email, "original_target": candidate_email, "response": r}
        except Exception as e2:
            print(f"Fallback interview email send failed: {e2}")
            return {"status": "error", "error": str(e2)}
