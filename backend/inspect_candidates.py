from db.supabase_client import supabase, mock_db

def inspect():
    print("--- INSPECTING CANDIDATES & EVALUATIONS ---")
    if supabase:
        try:
            c_res = supabase.table("candidates").select("*").execute()
            candidates = c_res.data or []
            e_res = supabase.table("evaluations").select("*").execute()
            evaluations = e_res.data or []
            eval_map = {ev.get("candidate_id"): ev for ev in evaluations if ev.get("candidate_id")}

            print(f"Total candidates in Supabase: {len(candidates)}")
            for c in candidates:
                ev = eval_map.get(c["id"], {})
                print(f"ID: {c['id']} | Name: {c.get('name')} | Stage: '{c.get('stage')}' | TotalScore: {ev.get('total_score')} | TestCode: {ev.get('test_code')} | TestLA: {ev.get('test_la')}")
        except Exception as e:
            print(f"Supabase query error: {e}")
    else:
        print(f"Mock DB candidates count: {len(mock_db.candidates)}")

if __name__ == "__main__":
    inspect()
