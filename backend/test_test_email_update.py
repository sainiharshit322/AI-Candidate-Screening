import io
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_email_update_from_test_results():
    print("--- 1. Upload Candidate with Original Email ---")
    csv_data = "S.No,Name,Email,College,Branch,CGPA,Best AI Project,Research Work,GitHub,Resume\n1,Alice Smith,alice.college@university.edu,MIT,CS,9.5,AI Chatbot,Paper,https://github.com/torvalds,https://example.com/resume.pdf\n"
    res = client.post("/api/candidates/upload", files={"file": ("cand.csv", io.BytesIO(csv_data.encode("utf-8")), "text/csv")})
    assert res.status_code == 200

    cand_res = client.get("/api/candidates")
    alice = cand_res.json()[0]
    alice_id = alice["id"]
    print(f"Original Email: {alice['email']}")
    assert alice["email"] == "alice.college@university.edu"

    print("\n--- 2. Upload Test Results with Candidate's Personal Email ---")
    # Test results CSV uses personal email
    test_results_csv = "S.No,Email,Test LA,Test Code\n1,sainiharshit322@gmail.com,92,95\n"
    res = client.post("/api/candidates/upload-results", files={"file": ("results.csv", io.BytesIO(test_results_csv.encode("utf-8")), "text/csv")})
    print(f"Upload Results Response: {res.json()}")
    assert res.status_code == 200
    assert res.json()["updated"] == 1

    print("\n--- 3. Verify Candidate Email Updated to Personal Email ---")
    cand_updated = client.get(f"/api/candidates/{alice_id}").json()
    print(f"Updated Candidate Email: {cand_updated['email']}, Stage: {cand_updated['stage']}")
    assert cand_updated["email"] == "sainiharshit322@gmail.com"
    assert cand_updated["stage"] == "test_done"

    print("\n--- 4. Schedule Interview (Invite Sent to New Personal Email) ---")
    sched_res = client.post("/api/calendar/schedule?threshold=50")
    print(f"Scheduled Interview: {sched_res.json()}")
    assert sched_res.status_code == 200
    scheduled_email = sched_res.json()["interviews"][0]["candidate_email"]
    print(f"Interview Invite Target Email: {scheduled_email}")
    assert scheduled_email == "sainiharshit322@gmail.com"

    print("\nSUCCESS: CANDIDATE TEST EMAIL UPDATE VERIFIED!")

if __name__ == "__main__":
    test_email_update_from_test_results()
