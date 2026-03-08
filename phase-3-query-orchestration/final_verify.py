import sys
from pathlib import Path

# Add orchestration dir to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT / "phase-3-query-orchestration"))

from chat_pipeline import answer_query

queries = [
    "how to download groww statement download?", # Platform help
    "What are the available HDFC schemes on Groww?", # Schemes
    "What is the benchmark for HDFC Nifty 1D Rate Liquid ETF?", # Benchmark (Fact)
    "What can you do for me?" # Meta
]

print("--- Final Verification ---")
for q in queries:
    print(f"\nQuery: {q}")
    result = answer_query(q)
    print(f"Intent: {result['intent']}")
    print(f"Answer: {result['answer']}")
    print("-" * 20)
