from __future__ import annotations

from phase-3-query-orchestration.chat_pipeline import answer_query
from guardrails import check_answer


SAMPLE_QUERIES = [
    "What is the expense ratio of HDFC NIFTY 50 Index Fund Direct Growth?",
    "How can I download my HDFC Small Cap Fund statement on Groww?",
    "Should I invest in HDFC Retirement Savings Fund?",
    "What is my PAN number?",
]


def main() -> None:
    for q in SAMPLE_QUERIES:
        print("=" * 80)
        print(f"Query: {q}")
        result = answer_query(q)
        answer = result["answer"]
        print("\nAnswer:")
        print(answer)

        safety = check_answer(answer)
        print("\nGuardrail flags:")
        for key, value in safety.items():
            print(f"  {key}: {value}")


if __name__ == "__main__":
    main()

