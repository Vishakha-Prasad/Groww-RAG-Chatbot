from __future__ import annotations

from typing import Dict, Iterable

from models import SchemeSnapshot
from parser_utils import html_to_clean_lines, build_header_index, extract_section_text
from schemes import SchemeConfig


SECTION_HEADER_ALIASES: Dict[str, Iterable[str]] = {
    "performance": ["Performance"],
    "fundamentals": ["Fundamentals"],
    "returns_calculator": ["Return calculator"],
    # ETF uses "Category returns", mutual fund pages often use "Returns and rankings"
    "category_returns": ["Category returns", "Returns and rankings"],
    # "About" headings vary slightly across pages; include common variants
    "about": [
        "About",
        "About HDFC Small Cap Fund",
        "About HDFC NIFTY 50 Index Fund Direct Growth",
        "About HDFC Retirement Savings Fund Equity Plan Direct Growth",
        "About HDFC Multi Asset Allocation Fund Direct Growth",
        "About HDFC Nifty 1D Rate Liquid ETF - Growth",
    ],
    # ETF uses "Similar ETFs", mutual funds use "Compare similar funds"
    "similar": ["Similar ETFs", "Compare similar funds"],
}


def parse_scheme_page(html: str, cfg: SchemeConfig) -> SchemeSnapshot:
    """
    Parse a Groww scheme page into a SchemeSnapshot.

    This is a text-centric, best-effort parser that relies primarily on
    visible section headers. It is intentionally generic across both ETF
    and mutual fund layouts.
    """
    lines = html_to_clean_lines(html)
    header_index = build_header_index(lines, SECTION_HEADER_ALIASES)

    performance_text = extract_section_text(
        lines, header_index, target_header="performance", all_section_headers=SECTION_HEADER_ALIASES.keys()
    )
    fundamentals_text = extract_section_text(
        lines, header_index, target_header="fundamentals", all_section_headers=SECTION_HEADER_ALIASES.keys()
    )
    returns_calculator_text = extract_section_text(
        lines,
        header_index,
        target_header="returns_calculator",
        all_section_headers=SECTION_HEADER_ALIASES.keys(),
    )
    category_returns_text = extract_section_text(
        lines,
        header_index,
        target_header="category_returns",
        all_section_headers=SECTION_HEADER_ALIASES.keys(),
    )
    about_text = extract_section_text(
        lines, header_index, target_header="about", all_section_headers=SECTION_HEADER_ALIASES.keys()
    )
    similar_schemes_text = extract_section_text(
        lines, header_index, target_header="similar", all_section_headers=SECTION_HEADER_ALIASES.keys()
    )

    snapshot = SchemeSnapshot(
        id=cfg.id,
        name=cfg.name,
        url=cfg.url,
        scheme_type=cfg.scheme_type,
        performance_text=performance_text,
        fundamentals_text=fundamentals_text,
        returns_calculator_text=returns_calculator_text,
        category_returns_text=category_returns_text,
        about_text=about_text,
        similar_schemes_text=similar_schemes_text,
    )
    return snapshot


__all__ = ["parse_scheme_page"]

