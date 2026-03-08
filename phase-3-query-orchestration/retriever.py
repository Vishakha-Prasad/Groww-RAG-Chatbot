from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

# Heavy imports are optional; they are only needed for actual retrieval.
try:
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity
except Exception:  # pragma: no cover
    np = None
    cosine_similarity = None


PROJECT_ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = PROJECT_ROOT / "phase-2-knowledge-base" / "index.pkl"


@dataclass
class RetrievedChunk:
    text: str
    scheme_id: str
    scheme_name: str
    attribute_type: str
    source_url: str
    score: float


_INDEX: Dict[str, Any] | None = None


def _load_index() -> Dict[str, Any]:
    global _INDEX  # noqa: PLW0603
    if _INDEX is not None:
        return _INDEX

    if not INDEX_PATH.exists():
        raise FileNotFoundError(
            f"Phase 2 index not found at {INDEX_PATH}. "
            "Run phase-2-knowledge-base/build_index.py first."
        )

    import pickle

    with INDEX_PATH.open("rb") as f:
        _INDEX = pickle.load(f)
    return _INDEX


def retrieve_top_k(query: str, k: int = 5, min_score: float = 0.0) -> List[RetrievedChunk]:
    """
    Retrieve top-k chunks from the TF-IDF index for a given query.

    If all similarity scores are below `min_score`, returns an empty list.
    """
    index = _load_index()
    vectorizer = index["vectorizer"]
    matrix = index["matrix"]
    chunks_meta = index["chunks"]

    query_vec = vectorizer.transform([query])
    sims = cosine_similarity(query_vec, matrix)[0]

    if not np.any(sims):
        return []

    top_indices = np.argsort(sims)[::-1][:k]

    results: List[RetrievedChunk] = []
    for idx in top_indices:
        score = float(sims[idx])
        if score < min_score:
            continue
        meta = chunks_meta[int(idx)]
        results.append(
            RetrievedChunk(
                text=meta["text"],
                scheme_id=meta["scheme_id"],
                scheme_name=meta["scheme_name"],
                attribute_type=meta["attribute_type"],
                source_url=meta["source_url"],
                score=score,
            )
        )

    return results


__all__ = ["RetrievedChunk", "retrieve_top_k"]

