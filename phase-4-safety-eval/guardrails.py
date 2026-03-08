from __future__ import annotations

import re
from typing import Dict, List


ADVICE_PATTERNS = [
    r"\byou should invest\b",
    r"\bshould i invest\b",
    r"\byou should buy\b",
    r"\bbuy\b",
    r"\bsell\b",
    r"\brecommend\b",
    r"\bsuggest\b",
    r"\bbest fund\b",
    r"\bbetter than\b",
]

PERSONAL_INFO_PATTERNS = [
    r"\bmy\s+pan\b",
    r"\bpan\s+number\b",
    r"\bpan\s+details\b",
    r"\bpan\s+card\s+details\b",
    r"\bwhat\s+is\s+(?:my\s+)?pan\b",
    r"\baadhaar\b",
    r"\baadhar\b",
    r"\bmobile\s*number\b",
    r"\bphone\s*number\b",
    r"\bemail\b",
    r"\bemail\s*id\b",
    r"\baddress\b",
    r"\baccount\s*number\b",
    r"\bifsc\b",
    r"\bupi\b",
    r"\bmy\s+portfolio\b",
    r"\bmy\s+holdings\b",
]

ALLOWED_SOURCE_SUBSTRINGS = ["groww.in"]


def _contains_pattern(text: str, patterns: List[str]) -> bool:
    t = text.lower()
    for p in patterns:
        if re.search(p, t):
            return True
    return False


def _has_allowed_source_url(text: str) -> bool:
    t = text.lower()
    return any(sub in t for sub in ALLOWED_SOURCE_SUBSTRINGS)


def check_answer(answer: str) -> Dict[str, object]:
    """
    Run basic safety checks on an answer string.

    Returns a dict with boolean flags and issue descriptions.
    """
    has_advice = _contains_pattern(answer, ADVICE_PATTERNS)
    has_personal = _contains_pattern(answer, PERSONAL_INFO_PATTERNS)
    has_source = _has_allowed_source_url(answer)

    issues: List[str] = []
    if has_advice:
        issues.append("contains_advice_language")
    if has_personal:
        issues.append("contains_personal_info_language")
    if not has_source:
        issues.append("missing_allowed_source_url")

    return {
        "has_advice_language": has_advice,
        "has_personal_info_language": has_personal,
        "has_allowed_source_url": has_source,
        "issues": issues,
    }


__all__ = ["check_answer"]

