from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import Dict, List

from sklearn.feature_extraction.text import TfidfVectorizer

from models import DocumentChunk


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PHASE1_OUT_DIR = PROJECT_ROOT / "phase-1-data-acquisition" / "out"
PHASE2_DIR = PROJECT_ROOT / "phase-2-knowledge-base"
INDEX_PATH = PHASE2_DIR / "index.pkl"


SECTION_ATTRIBUTE_MAP: Dict[str, str] = {
    "performance_text": "performance",
    "fundamentals_text": "fundamentals",
    "returns_calculator_text": "returns_calculator",
    "category_returns_text": "category_returns",
    "about_text": "about",
    "similar_schemes_text": "similar_schemes",
}


def load_scheme_snapshots() -> List[Dict]:
    """
    Load all Phase 1 scheme snapshots (JSON) into memory.
    """
    if not PHASE1_OUT_DIR.exists():
        print(f"[WARN] Phase 1 output directory does not exist: {PHASE1_OUT_DIR}")
        return []

    snapshots: List[Dict] = []
    for path in sorted(PHASE1_OUT_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            snapshots.append(data)
        except Exception as exc:  # noqa: BLE001
            print(f"[ERROR] Failed to load JSON from {path}: {exc}")
    return snapshots


def build_chunks(snapshots: List[Dict]) -> List[DocumentChunk]:
    """
    Turn scheme snapshots into individual document chunks.
    """
    chunks: List[DocumentChunk] = []
    for snap in snapshots:
        scheme_id = snap.get("id", "")
        scheme_name = snap.get("name", "")
        url = snap.get("url", "")

        for field_name, attr_type in SECTION_ATTRIBUTE_MAP.items():
            text_val = snap.get(field_name, "") or ""
            text_val = str(text_val).strip()
            if not text_val:
                continue

            chunk_id = f"{scheme_id}::{attr_type}"
            chunk = DocumentChunk(
                id=chunk_id,
                scheme_id=scheme_id,
                scheme_name=scheme_name,
                attribute_type=attr_type,
                source_url=url,
                text=text_val,
            )
            chunks.append(chunk)

    return chunks


def build_tfidf_index(chunks: List[DocumentChunk]) -> Dict[str, object]:
    """
    Build a TF-IDF index over all chunk texts.
    """
    if not chunks:
        raise ValueError("No chunks to index. Ensure Phase 1 outputs are present.")

    corpus = [c.text for c in chunks]
    vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        lowercase=True,
    )
    matrix = vectorizer.fit_transform(corpus)

    index = {
        "vectorizer": vectorizer,
        "matrix": matrix,
        "chunks": [c.to_metadata() for c in chunks],
    }
    return index


def save_index(index: Dict[str, object]) -> None:
    PHASE2_DIR.mkdir(parents=True, exist_ok=True)
    with INDEX_PATH.open("wb") as f:
        pickle.dump(index, f, protocol=pickle.HIGHEST_PROTOCOL)


def main() -> None:
    print(f"Loading scheme snapshots from: {PHASE1_OUT_DIR}")
    snapshots = load_scheme_snapshots()
    print(f"Loaded {len(snapshots)} snapshot files.")

    chunks = build_chunks(snapshots)
    print(f"Built {len(chunks)} document chunks.")

    if not chunks:
        print("[WARN] No chunks created; index will not be written.")
        return

    print("Building TF-IDF index...")
    index = build_tfidf_index(chunks)

    save_index(index)
    vocab_size = len(index["vectorizer"].vocabulary_)
    print(f"[OK] Index written to: {INDEX_PATH}")
    print(f"Chunks indexed: {len(chunks)}, vocabulary size: {vocab_size}")


if __name__ == "__main__":
    main()

