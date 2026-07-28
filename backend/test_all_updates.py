import io
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_full_pipeline():
    print("--- 1. Uploading Candidates CSV ---")
    # Read the dataset CSV
    with open("../candidate_dataset (1).xlsx - Response.csv", "rb") as f:
        csv_bytes = f.read()

    upload_res = client.post("/api/candidates/upload", files={"file": ("candidate_dataset.csv", io.BytesIO(csv_bytes), "text/csv")})
    print(f"Upload Result: {upload_res.json()}")
    assert upload_res.status_code == 200

    print("\n--- 2. Triggering AI + GitHub Screening ---")
    jd_res = client.post("/api/evaluate/job-description", json={"title": "AI Engineer", "content": "PyTorch, Python, Vision, Transformers"})
    jd_id = jd_res.json()["id"]
    eval_res = client.post("/api/evaluate", json={"job_description_id": jd_id})
    print(f"Evaluation Result: {eval_res.json()}")
    assert eval_res.status_code == 200

    print("\n--- 3. One-Click Send Test Links (Score >= 60%) ---")
    email_res = client.post("/api/email/send-test-links?threshold=60")
    print(f"Send Test Links Result: {email_res.json()}")
    assert email_res.status_code == 200

    print("\n--- 4. Uploading Test Results CSV ---")
    results_csv = (
        "s_no,email,test_la,test_code\n"
        "1,utkrisht.buttolia@mynachiketa.com,90,95\n"
        "2,utkrisht.buttolia@mynachiketa.com,85,88\n"
        "3,utkrisht.buttolia@mynachiketa.com,80,82\n"
        "4,utkrisht.buttolia@mynachiketa.com,75,78\n"
        "5,utkrisht.buttolia@mynachiketa.com,70,72\n"
    )
    results_res = client.post("/api/candidates/upload-results", files={"file": ("results.csv", io.BytesIO(results_csv.encode("utf-8")), "text/csv")})
    print(f"Upload Results Response: {results_res.json()}")
    assert results_res.status_code == 200
    assert results_res.json()["updated"] > 0

    print("\n--- 5. One-Click Schedule Interviews (Score >= 75%) ---")
    sched_res = client.post("/api/calendar/schedule?threshold=75")
    print(f"Schedule Interviews Result: {sched_res.json()}")
    assert sched_res.status_code == 200

    print("\nSUCCESS: PIPELINE FULLY VERIFIED!")

if __name__ == "__main__":
    test_full_pipeline()
