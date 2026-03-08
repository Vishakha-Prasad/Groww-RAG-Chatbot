from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import List, Dict, Any

# Define log location relative to this file
OPS_DIR = Path(__file__).resolve().parent
LOG_FILE = OPS_DIR / "chat_events.jsonl"

def load_events() -> List[Dict[str, Any]]:
    """Load all events from the JSONL log file."""
    if not LOG_FILE.exists():
        return []
    
    events = []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return events

def print_summary() -> None:
    """Print a human-readable summary of chatbot operations."""
    events = load_events()
    total = len(events)
    
    print("=" * 60)
    print(f"CHatBot2 Operations Dashboard | Total Interactions: {total}")
    print("=" * 60)
    
    if total == 0:
        print("No log events found. Start chatting to generate data!")
        return

    # Latency distribution
    latencies = [e.get("latency_sec", 0.0) for e in events if "latency_sec" in e]
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    max_latency = max(latencies) if latencies else 0
    
    print(f"Latency: Avg {avg_latency:.2f}s | Max {max_latency:.2f}s")
    
    # Intent distribution
    intents = Counter(e.get("intent", "UNKNOWN") for e in events)
    print("\nIntents:")
    for intent, count in intents.items():
        percentage = (count / total) * 100
        print(f"  - {intent:<20}: {count} ({percentage:.1f}%)")
    
    # Recent activity
    print("\nRecent Activity (Last 5):")
    for e in events[-5:]:
        ts = e.get("timestamp", "N/A").split(".")[0].replace("T", " ")
        q = e.get("query", "")
        summary = e.get("answer_summary", "")
        print(f"  [{ts}] Q: {q[:50]}")
        print(f"           A: {summary}")
    
    print("=" * 60)

if __name__ == "__main__":
    print_summary()
