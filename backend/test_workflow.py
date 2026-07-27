import io
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_full_recruitment_workflow():
    print("--- 1. Saving Job Description ---")
    jd_res = client.post("/api/evaluate/job-description", json={
        "title": "Senior AI Engineer",
        "content": "Expert in Python, PyTorch, Transformers, Computer Vision, and scalable REST APIs."
    })
    assert jd_res.status_code == 200
    jd_id = jd_res.json()["id"]

    print("\n--- 2. Uploading Candidates CSV ---")
    csv_data = (
        "S.No,Name,Email,College,Branch,CGPA,Best AI Project,Research Work,GitHub,Resume\n"
        "1,Top AI Candidate,sainiharshit322@gmail.com,DTU,CS,9.5,Deep Learning Vision Transformer,NeurIPS Paper,https://github.com/torvalds,https://example.com/resume.pdf\n"
    )
    upload_res = client.post("/api/candidates/upload", files={"file": ("candidates.csv", io.BytesIO(csv_data.encode("utf-8")), "text/csv")})
    assert upload_res.status_code == 200

    print("\n--- 3. Running Stage 1 Evaluation (Resume & GitHub fit score ONLY, test scores NOT included) ---")
    eval_res = client.post("/api/evaluate", json={"job_description_id": jd_id})
    assert eval_res.status_code == 200

    c_res = client.get("/api/candidates")
    candidates = c_res.json()
    cand = candidates[0]
    print(f"Initial Candidate Score (Resume + GitHub): {cand.get('total_score')} (Test Code={cand.get('test_code')}, Stage={cand.get('stage')})")
    assert cand.get("test_code") is None
    assert cand.get("stage") == "evaluated"

    print("\n--- 4. Shortlisting Candidates (Score >= 60%) & Sending Test Links ---")
    email_res = client.post("/api/email/send-test-links?threshold=60")
    print(f"Test links sent: {email_res.json()}")
    assert email_res.status_code == 200
    assert email_res.json()["sent_count"] > 0

    print("\n--- 5. Uploading Test Results & Recalculating Final Overall Composite Score ---")
    results_csv = "Email,Test LA,Test Code\nsainiharshit322@gmail.com,95.0,98.0\n"
    results_res = client.post("/api/candidates/upload-results", files={"file": ("results.csv", io.BytesIO(results_csv.encode("utf-8")), "text/csv")})
    assert results_res.status_code == 200

    c_updated_res = client.get(f"/api/candidates/{cand['id']}")
    cand_updated = c_updated_res.json()
    print(f"Final Composite Score (Resume + GitHub + Test Code + Test LA + CGPA): {cand_updated.get('total_score')}, Stage={cand_updated.get('stage')}")
    assert cand_updated.get("stage") == "test_done"
    assert cand_updated.get("total_score") is not None

    print("\n--- 6. Scheduling Interviews for Top Candidates (Final Score >= 75%) ---")
    sched_res = client.post("/api/calendar/schedule?threshold=75")
    print(f"Interview Scheduling Response: {sched_res.json()}")
    assert sched_res.status_code == 200
    assert sched_res.json()["scheduled_count"] > 0

    c_final_res = client.get(f"/api/candidates/{cand['id']}")
    print(f"Final Stage for {c_final_res.json().get('name')}: {c_final_res.json().get('stage')}")
    assert c_final_res.json().get("stage") == "interview_scheduled"

    print("\nSUCCESS: MULTI-STAGE RECRUITMENT WORKFLOW TESTED AND VERIFIED!")

if __name__ == "__main__":
    test_full_recruitment_workflow()
