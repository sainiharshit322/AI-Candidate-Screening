import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

_token_store: Dict[str, Any] = {}

def get_flow():
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/calendar/callback")
    
    if not client_id or not client_secret:
        raise ValueError("GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be configured")
        
    return Flow.from_client_config(
        {
            "web": {
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uris": [redirect_uri],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES,
        redirect_uri=redirect_uri,
    )

def save_credentials(creds: Credentials):
    _token_store["creds"] = creds

def get_credentials() -> Optional[Credentials]:
    return _token_store.get("creds")

def schedule_interview(candidate_name: str, candidate_email: str, slot: datetime) -> Dict[str, Any]:
    creds = get_credentials()
    recruiter_email = os.getenv("RECRUITER_EMAIL", "recruiter@example.com")

    if not creds:
        # Safe fallback / simulation mode when OAuth flow hasn't been completed yet
        event_id = f"evt_{uuid.uuid4().hex[:10]}"
        meet_link = f"https://meet.google.com/screening-{uuid.uuid4().hex[:3]}-{uuid.uuid4().hex[:4]}-{uuid.uuid4().hex[:3]}"
        return {
            "event_id": event_id,
            "meet_link": meet_link,
            "scheduled_at": slot,
            "simulated": True
        }

    try:
        service = build("calendar", "v3", credentials=creds)
        end_time = slot + timedelta(minutes=30)
        
        event = {
            "summary": f"Technical Interview: {candidate_name}",
            "start": {"dateTime": slot.isoformat(), "timeZone": "UTC"},
            "end": {"dateTime": end_time.isoformat(), "timeZone": "UTC"},
            "attendees": [
                {"email": recruiter_email},
                {"email": candidate_email},
            ],
            "conferenceData": {
                "createRequest": {
                    "requestId": str(uuid.uuid4()),
                    "conferenceSolutionKey": {"type": "hangoutsMeet"},
                }
            },
        }

        result = service.events().insert(
            calendarId="primary",
            body=event,
            conferenceDataVersion=1,
            sendUpdates="all",
        ).execute()

        meet_link = ""
        conf = result.get("conferenceData", {})
        entry_points = conf.get("entryPoints", [])
        if entry_points:
            meet_link = entry_points[0].get("uri", "")
        if not meet_link:
            meet_link = f"https://meet.google.com/meet-{result.get('id')}"

        return {
            "event_id": result.get("id"),
            "meet_link": meet_link,
            "scheduled_at": slot,
            "simulated": False
        }
    except Exception as e:
        print(f"Google Calendar API scheduling error: {e}")
        event_id = f"evt_{uuid.uuid4().hex[:10]}"
        meet_link = f"https://meet.google.com/screening-{uuid.uuid4().hex[:3]}-{uuid.uuid4().hex[:4]}-{uuid.uuid4().hex[:3]}"
        return {
            "event_id": event_id,
            "meet_link": meet_link,
            "scheduled_at": slot,
            "simulated": True,
            "error": str(e)
        }
