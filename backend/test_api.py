import io
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_all_endpoints():
    print("--- 1. Testing Root Endpoint ---")
    res = client.get("/")
    print(f"GET /: status={res.status_code}, json={res.json()}")
    assert res.status_code == 200

    print("\n--- 2. Testing Candidates List (Empty initial state) ---")
    res = client.get("/api/candidates")
    print(f"GET /api/candidates: status={res.status_code}, count={len(res.json())}")
    assert res.status_code == 200

    print("\n--- 3. Testing Candidates CSV Upload ---")
    sample_csv = (
        "S.No,Name,Email,College,Branch,CGPA,Best AI Project,Research Work,GitHub,Resume\n"
        "1,Alice Smith,alice@example.com,MIT,CS,9.2,LLM Chatbot,Transformer Paper,https://github.com/alice,https://example.com/resume.pdf\n"
        "2,Bob Jones,bob@example.com,Stanford,EE,8.5,Vision Model,CVPR Workshop,https://github.com/bob,https://example.com/bob.pdf\n"
    )
    file_bytes = sample_csv.encode("utf-8")
    res = client.post(
        "/api/candidates/upload",
        files={"file": ("candidates.csv", io.BytesIO(file_bytes), "text/csv")}
    )
    print(f"POST /api/candidates/upload: status={res.status_code}, response={res.json()}")
    assert res.status_code == 200
    assert res.json()["inserted"] == 2

    print("\n--- 4. Testing Candidates List (After upload) ---")
    res = client.get("/api/candidates")
    candidates = res.json()
    print(f"GET /api/candidates: status={res.status_code}, count={len(candidates)}")
    assert res.status_code == 200
    assert len(candidates) == 2
    alice = candidates[0]
    alice_id = alice["id"]

    print("\n--- 5. Testing Single Candidate Retrieval ---")
    res = client.get(f"/api/candidates/{alice_id}")
    print(f"GET /api/candidates/{alice_id}: status={res.status_code}, name={res.json().get('name')}")
    assert res.status_code == 200

    print("\n--- 6. Testing Stage Update ---")
    res = client.patch(f"/api/candidates/{alice_id}/stage", json={"stage": "evaluated"})
    print(f"PATCH /api/candidates/{alice_id}/stage: status={res.status_code}, response={res.json()}")
    assert res.status_code == 200

    print("\n--- 7. Testing Test Results CSV Upload ---")
    results_csv = (
        "Email,Test LA,Test Code\n"
        "alice@example.com,85.0,90.0\n"
        "bob@example.com,70.0,80.0\n"
    )
    res = client.post(
        "/api/candidates/upload-results",
        files={"file": ("results.csv", io.BytesIO(results_csv.encode("utf-8")), "text/csv")}
    )
    print(f"POST /api/candidates/upload-results: status={res.status_code}, response={res.json()}")
    assert res.status_code == 200
    assert res.json()["updated"] == 2

    print("\n--- 8. Verifying Scores After Test Results Upload ---")
    res = client.get(f"/api/candidates/{alice_id}")
    alice_updated = res.json()
    print(f"Updated Candidate: total_score={alice_updated.get('total_score')}, stage={alice_updated.get('stage')}")
    assert alice_updated.get("stage") == "test_done"
    assert alice_updated.get("total_score") is not None

    print("\nSUCCESS: ALL ENDPOINTS TESTED SUCCESSFULLY!")

if __name__ == "__main__":
    test_all_endpoints()
