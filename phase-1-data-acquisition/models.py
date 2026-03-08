from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict

from schemes import SchemeConfig, SchemeType


@dataclass
class SchemeSnapshot:
    """
    Normalized snapshot of one scheme page.

    All major sections are stored as text blocks, ready for indexing in later RAG phases.
    """

    id: str
    name: str
    url: str
    scheme_type: SchemeType

    performance_text: str
    fundamentals_text: str
    returns_calculator_text: str
    category_returns_text: str
    about_text: str
    similar_schemes_text: str

    def to_dict(self) -> Dict[str, object]:
        """Convert the dataclass to a plain dict suitable for JSON serialization."""
        return asdict(self)

    @classmethod
    def empty_for(cls, cfg: SchemeConfig) -> "SchemeSnapshot":
        """Create an empty snapshot for a given scheme config."""
        return cls(
            id=cfg.id,
            name=cfg.name,
            url=cfg.url,
            scheme_type=cfg.scheme_type,
            performance_text="",
            fundamentals_text="",
            returns_calculator_text="",
            category_returns_text="",
            about_text="",
            similar_schemes_text="",
        )


__all__ = ["SchemeSnapshot"]

