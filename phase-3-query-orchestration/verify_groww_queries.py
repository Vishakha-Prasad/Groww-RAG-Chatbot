import sys
from pathlib import Path

# Add orchestration dir to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT / "phase-3-query-orchestration"))

from chat_pipeline import answer_query

test_queries = [
    "How do I download my mutual fund statement?",
    "What schemes are available on Groww?",
    "How to get capital gains report?",
    "what is the help center link of groww?"
]

print("--- Verifying General Groww Queries ---")
for q in test_queries:
    print(f"\nQuery: {q}")
    result = answer_query(q)
    print(f"Intent: {result['intent']}")
    print(f"Answer: {result['answer']}")
    print("-" * 20)
