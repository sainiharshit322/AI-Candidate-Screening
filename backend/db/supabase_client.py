import os
import uuid
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

supabase = None

if SUPABASE_URL and SUPABASE_SERVICE_KEY:
    try:
        from supabase import create_client, Client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    except Exception as e:
        print(f"Warning: Failed to initialize Supabase client: {e}")

# In-memory fallback store when Supabase client is not available or for offline testing
class MockSupabase:
    def __init__(self):
        self.candidates: List[Dict[str, Any]] = []
        self.job_descriptions: List[Dict[str, Any]] = []
        self.evaluations: List[Dict[str, Any]] = []
        self.interviews: List[Dict[str, Any]] = []

    def upsert_candidate(self, candidate_data: Dict[str, Any]) -> str:
        email = candidate_data.get("email")
        for idx, c in enumerate(self.candidates):
            if c.get("email") == email:
                updated = {**c, **candidate_data}
                self.candidates[idx] = updated
                return updated["id"]
        
        new_id = str(uuid.uuid4())
        new_candidate = {
            "id": new_id,
            "stage": "uploaded",
            **candidate_data
        }
        self.candidates.append(new_candidate)
        return new_id

    def get_candidates(self) -> List[Dict[str, Any]]:
        results = []
        for c in self.candidates:
            # find latest evaluation
            eval_data = next((e for e in reversed(self.evaluations) if e.get("candidate_id") == c["id"]), {})
            eval_copy = dict(eval_data)
            eval_id = eval_copy.pop("id", None)
            joined = {
                **c,
                **eval_copy,
                "evaluation_id": eval_id
            }
            results.append(joined)
        return results

mock_db = MockSupabase()

def get_supabase_client():
    return supabase
