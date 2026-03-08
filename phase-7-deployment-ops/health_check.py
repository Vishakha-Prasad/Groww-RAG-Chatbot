from __future__ import annotations

import sys
from pathlib import Path

# Setup paths for Phase 3 and 4 imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "phase-3-query-orchestration"))
sys.path.insert(0, str(PROJECT_ROOT / "phase-4-safety-eval"))

def run_health_check() -> None:
    """Run a basic health check on all phases of the system."""
    print("=" * 60)
    print("CHatBot2 System Health Check")
    print("=" * 60)
    
    # 1. Phase 1 – Data Acquisition
    p1_dir = PROJECT_ROOT / "phase-1-data-acquisition" / "out"
    if p1_dir.exists() and any(p1_dir.glob("*.json")):
        print("[OK] Phase 1: Data Acquisition (JSON snapshots found)")
    else:
        print("[FAIL] Phase 1: No data snapshots found in phase-1-data-acquisition/out")
    
    # 2. Phase 2 – Knowledge Base
    p2_index = PROJECT_ROOT / "phase-2-knowledge-base" / "index.pkl"
    if p2_index.exists():
        print("[OK] Phase 2: Knowledge Base (index.pkl found)")
    else:
        print("[FAIL] Phase 2: No index found in phase-2-knowledge-base/index.pkl")
    
    # 3. Phase 3 & 4 – Orchestration & Safety
    try:
        from chat_pipeline import answer_query
        from guardrails import check_answer
        
        # Simple factual query to test end-to-end
        test_q = "What is the expense ratio of HDFC Small Cap Fund?"
        res = answer_query(test_q)
        ans = res.get("answer", "")
        
        if "expense ratio" in ans.lower() or "0.45%" in ans:
            print("[OK] Phase 3 & 4: Orchestration & Safety (test query successful)")
        else:
            print(f"[WARN] Phase 3: Unexpected answer to test query: {ans[:100]}...")
            
    except Exception as e:
        print(f"[FAIL] Phase 3 & 4: Orchestration/Safety test failed: {e}")
    
    # 4. Phase 6 – Scheduler
    p6_log = PROJECT_ROOT / "phase-6-scheduler-refresh" / "refresh_log.json"
    if p6_log.exists():
        print("[OK] Phase 6: Scheduler (refresh logs found)")
    else:
        print("[WARN] Phase 6: No refresh logs found in phase-6-scheduler-refresh")
        
    print("=" * 60)

if __name__ == "__main__":
    run_health_check()
