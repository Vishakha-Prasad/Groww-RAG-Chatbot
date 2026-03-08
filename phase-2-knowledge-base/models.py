from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict


@dataclass
class DocumentChunk:
    """
    A single retrieval unit in the knowledge base.

    Each chunk is tied to a specific scheme and a specific attribute/section
    (e.g. performance, fundamentals, about).
    """

    id: str
    scheme_id: str
    scheme_name: str
    attribute_type: str
    source_url: str
    text: str

    def to_metadata(self) -> Dict[str, str]:
        """
        Convert to a metadata dict that can be serialized alongside vector data.
        """
        return asdict(self)


__all__ = ["DocumentChunk"]

