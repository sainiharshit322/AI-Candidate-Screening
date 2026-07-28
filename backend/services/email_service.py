import resend
import os
from datetime import datetime
from typing import Any, Dict

# Strict recipient override: ALL emails are sent directly to sainiharshit322@gmail.com
TEST_RECIPIENT_EMAIL = "sainiharshit322@gmail.com"

def get_resend_client():
    api_key = os.getenv("RESEND_API_KEY")
    if api_key:
        resend.api_key = api_key
    return api_key

def send_test_link(candidate_name: str, candidate_email: str, test_link: str) -> Dict[str, Any]:
    api_key = get_resend_client()
    if not api_key:
        print(f"Skipping test link email for {candidate_name}: RESEND_API_KEY missing")
        return {"status": "skipped", "reason": "RESEND_API_KEY missing"}
    
    from_email = os.getenv("RESEND_FROM_EMAIL", "onboarding@resend.dev")
    name_display = candidate_name or "Candidate"
    
    # Always send to sainiharshit322@gmail.com
    payload = {
        "from": from_email,
        "to": TEST_RECIPIENT_EMAIL,
        "subject": f"Assessment Test: {name_display} ({candidate_email})",
        "html": f"""
        <p>Hi {name_display},</p>
        <p>Congratulations! You've been shortlisted for the next round.</p>
        <p>Please complete your assessment within 7 days:</p>
        <p><a href="{test_link}">Start Assessment →</a></p>
        <p>Best of luck!</p>
        <hr/>
        <p style="font-size: 11px; color: #888;">(Sent to {TEST_RECIPIENT_EMAIL} for candidate {name_display} / {candidate_email})</p>
        """
    }

    try:
        r = resend.Emails.send(payload)
        return {"status": "sent", "recipient": TEST_RECIPIENT_EMAIL, "candidate": candidate_email, "response": r}
    except Exception as e:
        print(f"Resend error sending test email for {name_display}: {e}")
        return {"status": "error", "error": str(e)}

def send_interview_invite(candidate_name: str, candidate_email: str, scheduled_at: Any, meet_link: str) -> Dict[str, Any]:
    api_key = get_resend_client()
    if not api_key:
        print(f"Skipping interview invite for {candidate_name}: RESEND_API_KEY missing")
        return {"status": "skipped", "reason": "RESEND_API_KEY missing"}

    from_email = os.getenv("RESEND_FROM_EMAIL", "onboarding@resend.dev")
    name_display = candidate_name or "Candidate"
    
    if isinstance(scheduled_at, datetime):
        formatted_date = scheduled_at.strftime('%A, %B %d %Y at %I:%M %p UTC')
    else:
        formatted_date = str(scheduled_at)

    # Always send to sainiharshit322@gmail.com
    payload = {
        "from": from_email,
        "to": TEST_RECIPIENT_EMAIL,
        "subject": f"Interview Scheduled: {name_display} ({candidate_email})",
        "html": f"""
        <p>Hi {name_display},</p>
        <p>Your interview has been scheduled for <strong>{formatted_date}</strong>.</p>
        <p>Join via Google Meet: <a href="{meet_link}">{meet_link}</a></p>
        <p>See you soon!</p>
        <hr/>
        <p style="font-size: 11px; color: #888;">(Sent to {TEST_RECIPIENT_EMAIL} for candidate {name_display} / {candidate_email})</p>
        """
    }

    try:
        r = resend.Emails.send(payload)
        return {"status": "sent", "recipient": TEST_RECIPIENT_EMAIL, "candidate": candidate_email, "response": r}
    except Exception as e:
        print(f"Resend error sending interview invite for {name_display}: {e}")
        return {"status": "error", "error": str(e)}
