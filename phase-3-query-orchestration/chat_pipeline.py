import json
import time
import os
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

# Ensure we can import from logger_utils in Phase 7
PHASE7_DIR = Path(__file__).resolve().parent.parent / "phase-7-deployment-ops"
if str(PHASE7_DIR) not in sys.path:
    sys.path.append(str(PHASE7_DIR))

try:
    from logger_utils import append_event_log
except ImportError:
    # Safe fallback if not in a dev/ops env
    append_event_log = None

from intent import classify_intent, is_personal_info_query
from llm_client import generate_answer_with_groq
from retriever import retrieve_top_k
from attribute_extractor import extract_structured_answer


def answer_query(query: str) -> Dict[str, Any]:
    """
    End-to-end single-turn query handler for Phase 3.
    """
    start_time = time.perf_counter()
    q = query.strip()
    
    # We will build the event log as we go
    event_log: Dict[str, Any] = {
        "query": q,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    
    if not q:
        res = {
            "answer": "Please provide a question about one of the supported HDFC schemes.",
            "used_chunks": [],
            "intent": "INVALID",
        }
        _log_and_return(event_log, res, start_time)
        return res

    # 1. Personal information guard
    if is_personal_info_query(q):
        res = {
            "answer": (
                "I cannot help with questions involving personal or sensitive information "
                "such as PAN, Aadhaar, phone numbers, email, addresses, or portfolio-specific details. "
                "Please ask only factual questions about the supported HDFC mutual fund schemes on Groww."
            ),
            "used_chunks": [],
            "intent": "OUT_OF_SCOPE",
        }
        _log_and_return(event_log, res, start_time)
        return res

    # 2. Intent classification
    intent = classify_intent(q)
    event_log["intent"] = intent
    if intent == "OUT_OF_SCOPE":
        res = {
            "answer": (
                "I can only provide factual information about the supported HDFC mutual fund schemes on Groww, "
                "such as expense ratio, exit load, minimum SIP, lock-in, riskometer, benchmark, "
                "and how to download statements. I cannot provide investment advice, comparisons, "
                "or handle personal information."
            ),
            "used_chunks": [],
            "intent": intent,
        }
        _log_and_return(event_log, res, start_time)
        return res

    # 3. Retrieval from Phase 2 index
    # Use a small positive threshold to avoid extremely weak matches.
    retrieved = retrieve_top_k(q, k=5, min_score=0.05)
    used_chunks = [asdict(r) for r in retrieved]

    if not retrieved:
        if intent in ["FACT_ATTRIBUTE_QUERY", "OUT_OF_SCOPE"]:
            # No confident context for scheme-specific or OOS: return grounded refusal.
            res = {
                "answer": (
                    "I am unable to answer this question from the information currently stored in my data. "
                    "Please refer to the official Groww pages for the latest details on HDFC mutual fund schemes, "
                    "for example: https://groww.in/mutual-funds/user/explore"
                ),
                "used_chunks": [],
                "intent": intent,
            }
            _log_and_return(event_log, res, start_time)
            return res
        # For general queries, we'll let the LLM try even without specific context (outsourcing data)
        used_chunks = []

    # 4. Try to answer directly from retrieved text for common attributes or platform help
    structured_fragment = extract_structured_answer(q, retrieved)
    if structured_fragment and intent in ["FACT_ATTRIBUTE_QUERY", "GROWW_GENERAL_QUERY"]:
        # Build a concise answer including scheme name and at least one source URL.
        primary_chunk = retrieved[0]
        scheme_name = primary_chunk.scheme_name
        source_url = primary_chunk.source_url
        
        # If it's a general platform query, we might not want the "For [Scheme], the..." prefix
        if intent == "GROWW_GENERAL_QUERY":
            answer_text = f"{structured_fragment}\nSource: {source_url}"
        else:
            answer_text = (
                f"For {scheme_name}, the {structured_fragment} "
                f"Source: {source_url}"
            )

        res = {
            "answer": answer_text,
            "used_chunks": used_chunks,
            "intent": intent,
        }
        _log_and_return(event_log, res, start_time)
        return res

    # 5. Call Groq LLM with retrieved context only if no structured answer
    # Convert RetrievedChunk objects into simple dicts for the LLM client.
    context_for_llm = [
        {
            "text": r.text,
            "scheme_id": r.scheme_id,
            "scheme_name": r.scheme_name,
            "attribute_type": r.attribute_type,
            "source_url": r.source_url,
            "score": r.score,
        }
        for r in retrieved
    ]

    try:
        answer_text = generate_answer_with_groq(q, context_for_llm)
    except Exception as exc:  # noqa: BLE001
        # Defensive fallback: if the LLM call fails (e.g. invalid API key or network),
        # return a safe, non-hallucinated message instead of crashing.
        answer_text = (
            "I’m unable to generate an answer right now due to an internal error. "
            "Please refer to the official Groww pages for the latest details on HDFC mutual fund schemes, "
            "for example: https://groww.in/mutual-funds/user/explore"
        )

    res = {
        "answer": answer_text,
        "used_chunks": used_chunks,
        "intent": intent,
    }
    _log_and_return(event_log, res, start_time)
    return res


def _log_and_return(event_log: Dict[str, Any], res: Dict[str, Any], start_time: float) -> None:
    """Helper to finalize the event log and call the logging utility."""
    latency = time.perf_counter() - start_time
    event_log["latency_sec"] = round(latency, 4)
    event_log["answer_summary"] = (res["answer"][:100] + "...") if len(res["answer"]) > 100 else res["answer"]
    event_log["answer_len"] = len(res["answer"])
    event_log["num_chunks"] = len(res.get("used_chunks", []))
    event_log["intent"] = res.get("intent", "UNKNOWN")
    
    if append_event_log:
        append_event_log(event_log)


if __name__ == "__main__":
    try:
        user_q = input("Enter your question about HDFC schemes on Groww: ").strip()
    except EOFError:  # noqa: PERF203
        user_q = ""

    result = answer_query(user_q)
    print(json.dumps(result, indent=2, ensure_ascii=False))

