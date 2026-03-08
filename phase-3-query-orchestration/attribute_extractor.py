from __future__ import annotations

import re
from typing import List, Optional

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from retriever import RetrievedChunk


def _normalize_text(chunks: List[RetrievedChunk]) -> str:
    """Join chunk texts into a single whitespace-normalized string."""
    parts = []
    for c in chunks:
        parts.append(" ".join(c.text.split()))
    return " ".join(parts)


def _extract_expense_ratio(chunks: List[RetrievedChunk]) -> Optional[str]:
    text = _normalize_text(chunks)
    m = re.search(
        r"expense\s*ratio\s*(?:[:\-]|of)?\s*([0-9]+(?:\.[0-9]+)?)\s*%?",
        text,
        flags=re.IGNORECASE,
    )
    if not m:
        return None
    # Ensure the returned string includes a percent sign
    return f"expense ratio is {m.group(1)}%"


def _extract_exit_load(chunks: List[RetrievedChunk]) -> Optional[str]:
    text = _normalize_text(chunks)
    # Try to capture the main exit load sentence, allowing optional colon/dash and percent.
    m = re.search(
        r"(exit\s*load\s*[:\-]?\s*([0-9]+(?:\.[0-9]+)?)\s*%?)",
        text,
        flags=re.IGNORECASE,
    )
    if not m:
        return None
    # Return the captured phrase without trailing punctuation.
    return m.group(1).strip()


def _extract_min_sip(chunks: List[RetrievedChunk]) -> Optional[str]:
    text = _normalize_text(chunks)
    # Pattern: "Minimum SIP Investment is set to ₹100"
    m = re.search(
        r"minimum\s+sip\s+investment\s+is\s+set\s+to\s*₹?\s*([\d,]+)",
        text,
        flags=re.IGNORECASE,
    )
    if not m:
        # Pattern: "Min. for SIP ₹100"
        m = re.search(
            r"min\.\s*for\s*sip\s*₹?\s*([\d,]+)",
            text,
            flags=re.IGNORECASE,
        )
    if not m:
        # Additional pattern: "SIP ₹100"
        m = re.search(
            r"sip\s*₹?\s*([\d,]+)",
            text,
            flags=re.IGNORECASE,
        )
    if not m:
        return None
    return f"minimum SIP investment is ₹{m.group(1)}."


def _extract_min_lumpsum(chunks: List[RetrievedChunk]) -> Optional[str]:
    text = _normalize_text(chunks)
    # Pattern: "Minimum Lumpsum Investment is set to ₹100"
    m = re.search(
        r"minimum\s+lumpsum\s+investment\s+is\s+set\s+to\s*₹?\s*([\d,]+)",
        text,
        flags=re.IGNORECASE,
    )
    if not m:
        # Pattern: "Min. for 1st investment ₹100"
        m = re.search(
            r"min\.\s*for\s*1st\s*investment\s*₹?\s*([\d,]+)",
            text,
            flags=re.IGNORECASE,
        )
    if not m:
        # Additional pattern: "Lumpsum ₹100"
        m = re.search(
            r"lumpsum\s*₹?\s*([\d,]+)",
            text,
            flags=re.IGNORECASE,
        )
    if not m:
        return None
    return f"minimum lumpsum investment is ₹{m.group(1)}."


def _extract_lock_in(chunks: List[RetrievedChunk]) -> Optional[str]:
    text = _normalize_text(chunks)
    # Look for phrases like "5Y Lock-in", "Lock‑in period: 5 years", or "lock‑in 5Y".
    m = re.search(
        r"(\d+\s*Y\s*lock-?in|lock-?in(?:\s*period)?\s*[:\-]?\s*\d+\s*Y?)",
        text,
        flags=re.IGNORECASE,
    )
    if not m:
        return None
    return m.group(1).strip()


def _extract_riskometer(chunks: List[RetrievedChunk]) -> Optional[str]:
    text = _normalize_text(chunks)
    # Common risk labels seen on Groww: Very High Risk, High Risk, Moderate, Low, etc.
    m = re.search(
        r"\b(very high risk|high risk|moderately high risk|moderate risk|low risk|very low risk|medium risk)\b",
        text,
        flags=re.IGNORECASE,
    )
    if not m:
        # Also capture "Medium" or "Moderate" as a standalone word followed by risk
        m = re.search(
            r"\b(medium|moderate)\b",
            text,
            flags=re.IGNORECASE,
        )
        if m:
             return f"riskometer rating is {m.group(1).title()} Risk."
    if not m:
        return None
    return f"riskometer rating is {m.group(1).title()}."


def _extract_benchmark(chunks: List[RetrievedChunk]) -> Optional[str]:
    text = _normalize_text(chunks)
    # Mutual fund pages often have "Fund benchmark NIFTY..."
    m = re.search(
        r"(fund\s+benchmark\s*[A-Za-z0-9 \u0026\-:]+)",
        text,
        flags=re.IGNORECASE,
    )
    if not m:
        # ETF page: "Benchmark Nifty 1D Rate TRI"
        m = re.search(
            r"(benchmark\s+[A-Za-z0-9 \u0026\-:]+)",
            text,
            flags=re.IGNORECASE,
        )
    if not m:
        # Additional pattern: "Benchmark: NIFTY 50"
        m = re.search(
            r"benchmark\s*[:\-]\s*([A-Za-z0-9 \u0026\-:]+)",
            text,
            flags=re.IGNORECASE,
        )
    if not m:
        return None
    # For the third case, we return just the captured index name in m.group(1)
    # but the first two capture the whole phrase.
    try:
        return m.group(1).strip()
    except IndexError:
        return m.group(0).strip()


def extract_structured_answer(
    query: str,
    chunks: List[RetrievedChunk],
) -> Optional[str]:
    """
    Try to derive a direct factual answer from retrieved chunks for common attributes,
    without calling the LLM.

    Returns a short, human-readable fragment (without scheme name or source URL),
    or None if nothing could be extracted.
    """
    q = query.lower()

    if "expense ratio" in q or ("expense" in q and "ratio" in q):
        return _extract_expense_ratio(chunks)

    if "exit load" in q:
        return _extract_exit_load(chunks)

    if "sip" in q:
        return _extract_min_sip(chunks)

    if "lumpsum" in q or "lump sum" in q or "1st investment" in q:
        return _extract_min_lumpsum(chunks)

    if "lock in" in q or "lock-in" in q:
        return _extract_lock_in(chunks)

    if "riskometer" in q or "risk level" in q or "risk profile" in q:
        return _extract_riskometer(chunks)

    if "benchmark" in q or "index" in q:
        return _extract_benchmark(chunks)

    if "statement" in q or "download" in q or "report" in q:
        return _extract_statement_download(chunks)

    # General Groww help (schemes, help center)
    return _extract_groww_general_help(chunks)

__all__ = ["extract_structured_answer", "_extract_statement_download"]


def _extract_statement_download(chunks: List[RetrievedChunk]) -> Optional[str]:
    """
    Extract statement download instructions from retrieved chunks.
    Looks for step-by-step instructions on how to download statements from Groww.
    """
    for chunk in chunks:
        text = chunk.text.lower()
        # Look for the statement steps specifically
        if ("how to download" in text or "statement" in text or "report" in text) and (
            "log in" in text or "profile" in text or "reports" in text
        ):
            # Try to capture the numbered list starting from "1. Log in"
            m = re.search(r"(1\.\s+Log\s+in.*)", chunk.text, flags=re.DOTALL | re.IGNORECASE)
            if m:
                return m.group(1).strip()

    # Generic fallback
    combined_text = _normalize_text(chunks).lower()
    if "download" in combined_text or "statement" in combined_text or "report" in combined_text:
        return (
            "You can download mutual fund statements (Transaction, Capital Gains, Tax Proofs) "
            "from the 'Reports' section in the 'You' (Profile) tab on Groww."
        )

    return None


def _extract_groww_general_help(chunks: List[RetrievedChunk]) -> Optional[str]:
    """
    Search chunks for general Groww platform information.
    Looks for available schemes info or general help content.
    """
    for chunk in chunks:
        text = chunk.text.lower()
        # Look for available schemes info
        if "available schemes" in text or "explore available hdfc schemes" in text:
            return chunk.text.strip()

    return None
