from __future__ import annotations

import re
from typing import Literal


Intent = Literal[
    "FACT_ATTRIBUTE_QUERY",
    "STATEMENT_DOWNLOAD_QUERY",
    "GROWW_GENERAL_QUERY",
    "META_QUERY",
    "OUT_OF_SCOPE",
]


PERSONAL_INFO_PATTERNS = [
    r"\bpan\b",
    r"\baadhaar\b",
    r"\baadhar\b",
    r"\baadhaar\s*number\b",
    r"\baadhar\s*number\b",
    r"\bmobile\s*number\b",
    r"\bphone\s*number\b",
    r"\bcontact\s*number\b",
    r"\bemail\b",
    r"\bemail\s*id\b",
    r"\baddress\b",
    r"\bdate\s*of\s*birth\b",
    r"\bdob\b",
    r"\baccount\s*number\b",
    r"\bifsc\b",
    r"\bupi\b",
    r"\bportfolio\b",
    r"\bmy\s+investments\b",
    r"\bmy\s+holdings\b",
]


def is_personal_info_query(query: str) -> bool:
    """Return True if the query appears to involve personal/sensitive information."""
    q = query.lower()
    for pattern in PERSONAL_INFO_PATTERNS:
        if re.search(pattern, q):
            return True
    return False


def classify_intent(query: str) -> Intent:
    """
    Very lightweight intent classifier based on keywords.

    This is intentionally simple; later phases or implementations can swap in
    an LLM-based classifier while keeping the same interface.
    """
    q = query.lower()

    # Hard out-of-scope: personal info or explicit advice / comparison.
    if is_personal_info_query(q):
        return "OUT_OF_SCOPE"

    advice_keywords = [
        "should i invest",
        "is this good",
        "which is better",
        "best fund",
        "recommend",
        "suggest",
        "buy or sell",
    ]
    if any(k in q for k in advice_keywords):
        return "OUT_OF_SCOPE"
    # Statement / report download
    if "statement" in q or "download" in q or "account statement" in q:
        return "GROWW_GENERAL_QUERY"

    # Meta / capability questions
    meta_keywords = [
        "what can you answer",
        "what can you do",
        "what questions can i ask",
        "help",
        "scope",
    ]
    if any(k in q for k in meta_keywords):
        return "META_QUERY"

    # Other Groww-related queries (available schemes, what is groww, etc.)
    groww_general_keywords = [
        "available schemes",
        "which schemes",
        "groww feature",
        "how to open account",
        "kyc",
        "help center",
        "customer care",
        "available funds",
    ]
    if any(k in q for k in groww_general_keywords) or "groww" in q:
        return "GROWW_GENERAL_QUERY"

    # Default to factual attribute queries for this domain.
    return "FACT_ATTRIBUTE_QUERY"


__all__ = ["Intent", "is_personal_info_query", "classify_intent"]

