import io
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_phase3_communication_and_scheduling():
    print("--- 1. Setting Up Evaluated and Test Done Candidates ---")
    # Upload sample candidates
    csv_data = (
        "S.No,Name,Email,College,Branch,CGPA,Best AI Project,Research Work,GitHub,Resume\n"
        "1,Grace Hopper,sainiharshit322@gmail.com,Vassar,Math,9.9,Compiler AI,COBOL Paper,https://github.com/torvalds,https://example.com/resume.pdf\n"
    )
    res = client.post("/api/candidates/upload", files={"file": ("candidates.csv", io.BytesIO(csv_data.encode("utf-8")), "text/csv")})
    assert res.status_code == 200

    # Save JD & evaluate
    jd_res = client.post("/api/evaluate/job-description", json={"title": "Lead Engineer", "content": "PyTorch, AI models, Python, system design"})
    jd_id = jd_res.json()["id"]
    client.post("/api/evaluate", json={"job_description_id": jd_id})

    print("\n--- 2. Testing Test Link Email Dispatch (POST /api/email/send-test-links) ---")
    email_res = client.post("/api/email/send-test-links?threshold=40")
    print(f"POST /api/email/send-test-links: status={email_res.status_code}, response={email_res.json()}")
    assert email_res.status_code == 200
    assert email_res.json()["sent_count"] > 0

    print("\n--- 3. Uploading Test Results to Move Stage to 'test_done' ---")
    results_csv = (
        "Email,Test LA,Test Code\n"
        "sainiharshit322@gmail.com,95.0,98.0\n"
    )
    res = client.post("/api/candidates/upload-results", files={"file": ("results.csv", io.BytesIO(results_csv.encode("utf-8")), "text/csv")})
    assert res.status_code == 200

    print("\n--- 4. Testing Google Calendar Scheduling (POST /api/calendar/schedule) ---")
    sched_res = client.post("/api/calendar/schedule?threshold=40")
    print(f"POST /api/calendar/schedule: status={sched_res.status_code}, response={sched_res.json()}")
    assert sched_res.status_code == 200
    assert sched_res.json()["scheduled_count"] > 0

    interviews = sched_res.json()["interviews"]
    first_interview = interviews[0]
    print(f"Scheduled Interview for {first_interview.get('candidate_name')}: Slot={first_interview.get('scheduled_at')}, Meet Link={first_interview.get('google_meet_link')}")
    assert first_interview.get("google_meet_link") is not None

    print("\n--- 5. Testing Candidate Stage after Scheduling ---")
    cand_res = client.get(f"/api/candidates/{first_interview['candidate_id']}")
    cand = cand_res.json()
    print(f"Candidate {cand.get('name')} Stage: {cand.get('stage')}")
    assert cand.get("stage") == "interview_scheduled"

    print("\nSUCCESS: PHASE 3 COMMUNICATION & SCHEDULING TESTED SUCCESSFULLY!")

if __name__ == "__main__":
    test_phase3_communication_and_scheduling()
