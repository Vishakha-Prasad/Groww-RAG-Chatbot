from __future__ import annotations

import os

from chat_pipeline import answer_query


def test_personal_info_query() -> None:
    q = "What is my PAN number and how is it used?"
    result = answer_query(q)
    assert result["intent"] == "OUT_OF_SCOPE"
    assert "personal or sensitive information" in result["answer"]


def test_advice_query() -> None:
    q = "Should I invest in HDFC Small Cap Fund?"
    result = answer_query(q)
    assert result["intent"] == "OUT_OF_SCOPE"
    assert "investment advice" in result["answer"]


def test_factual_query_smoke() -> None:
    """
    Smoke test for a valid factual query.

    If GROQ_API_KEY is not properly configured, we skip the LLM call expectation
    and only check that the pipeline returns a non-empty answer string.
    """
    q = "What is the expense ratio of HDFC NIFTY 50 Index Fund Direct Growth?"
    result = answer_query(q)
    answer = result["answer"]
    assert isinstance(answer, str)
    assert answer.strip() != ""


if __name__ == "__main__":
    # Simple runner
    tests = [
        ("personal_info", test_personal_info_query),
        ("advice", test_advice_query),
        ("factual_smoke", test_factual_query_smoke),
    ]
    failures = 0
    for name, fn in tests:
        try:
            fn()
            print(f"[OK] {name}")
        except AssertionError as exc:
            failures += 1
            print(f"[FAIL] {name}: {exc}")
        except Exception as exc:  # noqa: BLE001
            failures += 1
            print(f"[ERROR] {name}: {exc}")

    if failures:
        raise SystemExit(1)
    raise SystemExit(0)

