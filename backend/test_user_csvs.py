import io
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_user_actual_csv_files():
    print("--- 1. Uploading candidate_dataset (1).xlsx - Response.csv ---")
    with open("../candidate_dataset (1).xlsx - Response.csv", "rb") as f:
        resp_csv = f.read()

    upload_res = client.post("/api/candidates/upload", files={"file": ("Response.csv", io.BytesIO(resp_csv), "text/csv")})
    print(f"Response CSV Upload Result: {upload_res.json()}")
    assert upload_res.status_code == 200

    print("\n--- 2. Triggering AI + GitHub Screening ---")
    jd_res = client.post("/api/evaluate/job-description", json={"title": "AI Engineer", "content": "PyTorch, Python, Vision, Transformers"})
    jd_id = jd_res.json()["id"]
    eval_res = client.post("/api/evaluate", json={"job_description_id": jd_id})
    print(f"Evaluation Result: {eval_res.json()}")
    assert eval_res.status_code == 200

    print("\n--- 3. Uploading candidate_dataset (1).xlsx - Test Result.csv ---")
    with open("../candidate_dataset (1).xlsx - Test Result.csv", "rb") as f:
        test_csv = f.read()

    results_res = client.post("/api/candidates/upload-results", files={"file": ("Test Result.csv", io.BytesIO(test_csv), "text/csv")})
    print(f"Test Result CSV Upload Response: {results_res.json()}")
    assert results_res.status_code == 200
    assert results_res.json()["updated"] == 8

    print("\n--- 4. Checking Updated Candidate Scores ---")
    c_res = client.get("/api/candidates")
    candidates = c_res.json()
    print(f"Total Candidates in Database: {len(candidates)}")
    for c in candidates:
        print(f"Candidate S.No {c.get('s_no')}: {c.get('name')} | Stage: {c.get('stage')} | Test Code: {c.get('test_code')} | Test LA: {c.get('test_la')} | Total Score: {c.get('total_score')}")

    print("\nSUCCESS: ALL CANDIDATES FROM USER'S TEST RESULT CSV UPDATED!")

if __name__ == "__main__":
    test_user_actual_csv_files()
