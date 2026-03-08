from __future__ import annotations

from typing import Iterable, List, Dict

from bs4 import BeautifulSoup


def html_to_clean_lines(html: str) -> List[str]:
    """
    Convert raw HTML to a list of cleaned text lines.

    - Removes script/style/noscript tags.
    - Collapses whitespace.
    """
    soup = BeautifulSoup(html, "lxml")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    # Normalize and split into lines
    lines = [line.strip() for line in text.splitlines()]
    # Drop empty lines here; section extractors can reintroduce spacing if needed.
    return [line for line in lines if line]


def _normalize(s: str) -> str:
    return s.strip().casefold()


def build_header_index(
    lines: List[str],
    header_aliases: Dict[str, Iterable[str]],
) -> Dict[str, List[int]]:
    """
    Build an index of header -> list of line indices where it appears.

    header_aliases:
        logical_header_name -> list of possible textual variants.
    """
    index: Dict[str, List[int]] = {name: [] for name in header_aliases.keys()}
    normalized_lines = [_normalize(l) for l in lines]

    for logical_name, aliases in header_aliases.items():
        alias_norm = [_normalize(a) for a in aliases]
        for i, line_norm in enumerate(normalized_lines):
            if any(line_norm == a or line_norm.startswith(a) for a in alias_norm):
                index[logical_name].append(i)

    return index


def extract_section_text(
    lines: List[str],
    header_index: Dict[str, List[int]],
    target_header: str,
    all_section_headers: Iterable[str],
) -> str:
    """
    Extract text belonging to a logical section.

    We:
    - Find the first occurrence of the target header.
    - Collect subsequent lines until we hit another known section header.
    """
    positions = header_index.get(target_header) or []
    if not positions:
        return ""

    start_idx = positions[0] + 1
    max_idx = len(lines)

    # Build a flat set of all header line indices (except the starting header),
    # so we know when to stop.
    stop_indices = set()
    for header_name, indices in header_index.items():
        if header_name == target_header:
            # Skip the first occurrence (the one we are extracting from),
            # but any subsequent occurrences should stop the section.
            if len(indices) > 1:
                stop_indices.update(indices[1:])
            continue
        stop_indices.update(indices)

    collected: List[str] = []
    for i in range(start_idx, max_idx):
        if i in stop_indices:
            break
        collected.append(lines[i])

    return "\n".join(collected).strip()


__all__ = [
    "html_to_clean_lines",
    "build_header_index",
    "extract_section_text",
]

