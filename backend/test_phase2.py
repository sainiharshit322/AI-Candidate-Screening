import io
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_phase2_evaluation_pipeline():
    print("--- 1. Saving Job Description ---")
    jd_payload = {
        "title": "Senior AI / Machine Learning Engineer",
        "content": "Looking for an expert AI/ML engineer proficient in Python, PyTorch, LLMs, Transformer architectures, and building production backend services."
    }
    jd_res = client.post("/api/evaluate/job-description", json=jd_payload)
    print(f"POST /api/evaluate/job-description: status={jd_res.status_code}, json={jd_res.json()}")
    assert jd_res.status_code == 200
    jd_id = jd_res.json()["id"]

    print("\n--- 2. Uploading Candidates CSV ---")
    sample_csv = (
        "S.No,Name,Email,College,Branch,CGPA,Best AI Project,Research Work,GitHub,Resume\n"
        "1,Dr. Evelyn Vance,evelyn@example.com,Stanford,CS,9.8,LLM Fine Tuning Pipeline,NeurIPS Paper on Transformers,https://github.com/torvalds,https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf\n"
        "2,Charlie Brown,charlie@example.com,State Univ,Arts,5.5,Basic Calculator,None,https://github.com/nonexistent_user_xyz,https://example.com/invalid_resume.pdf\n"
    )
    file_bytes = sample_csv.encode("utf-8")
    upload_res = client.post(
        "/api/candidates/upload",
        files={"file": ("candidates.csv", io.BytesIO(file_bytes), "text/csv")}
    )
    print(f"POST /api/candidates/upload: status={upload_res.status_code}, response={upload_res.json()}")
    assert upload_res.status_code == 200

    print("\n--- 3. Triggering Candidate Evaluation Pipeline ---")
    eval_res = client.post("/api/evaluate", json={"job_description_id": jd_id})
    print(f"POST /api/evaluate: status={eval_res.status_code}, response={eval_res.json()}")
    assert eval_res.status_code == 200

    print("\n--- 4. Checking Evaluated Candidates ---")
    cand_res = client.get("/api/candidates")
    candidates = cand_res.json()
    print(f"Candidates Count: {len(candidates)}")
    for c in candidates:
        print(f"Candidate {c.get('name')}: Stage={c.get('stage')}, AI Score={c.get('ai_score')}, GitHub Score={c.get('github_score')}, Total Score={c.get('total_score')}")
        assert c.get("stage") == "evaluated"
        assert c.get("total_score") is not None

    print("\n--- 5. Checking Shortlisted Results ---")
    results_res = client.get("/api/evaluate/results?threshold=40")
    results = results_res.json()
    print(f"Shortlisted Candidates (>=40): {len(results)}")
    assert results_res.status_code == 200

    print("\nSUCCESS: PHASE 2 EVALUATION PIPELINE TESTED SUCCESSFULLY!")

if __name__ == "__main__":
    test_phase2_evaluation_pipeline()
