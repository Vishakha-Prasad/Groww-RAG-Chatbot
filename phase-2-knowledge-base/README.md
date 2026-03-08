## Phase 2 – Knowledge Base Preparation & Indexing

This module implements **Phase 2** of the architecture: turning the Phase 1 scheme snapshots into a **retrieval-ready knowledge base**.

It:

- Reads the JSON snapshots produced by `phase-1-data-acquisition` from `phase-1-data-acquisition/out/`.
- Converts each scheme’s major text sections into **document chunks** with metadata.
- Builds a simple **TF‑IDF–based vector index** for these chunks using scikit‑learn.
- Writes the index to `phase-2-knowledge-base/index.pkl` for later use in the RAG backend.

This gives you a local, dependency-light retrieval layer you can call from the chat backend.

---

## Inputs

- Phase 1 output JSON files (one per scheme), e.g.:
  - `phase-1-data-acquisition/out/hdfc_nifty_1d_rate_liquid_etf.json`
  - `phase-1-data-acquisition/out/hdfc_small_cap_fund_direct_growth.json`
  - `phase-1-data-acquisition/out/hdfc_nifty_50_index_fund_direct_growth.json`
  - `phase-1-data-acquisition/out/hdfc_retirement_savings_fund_equity_plan_direct_growth.json`
  - `phase-1-data-acquisition/out/hdfc_multi_asset_allocation_fund_direct_growth.json`

Each JSON must be a serialized `SchemeSnapshot` (see Phase 1).

---

## Data model

`models.py` defines a `DocumentChunk`:

- `id`: unique ID for this chunk.
- `scheme_id`: ID of the parent scheme (from Phase 1).
- `scheme_name`: human-readable name.
- `attribute_type`: which section this chunk comes from, one of:
  - `performance`
  - `fundamentals`
  - `returns_calculator`
  - `category_returns`
  - `about`
  - `similar_schemes`
- `source_url`: Groww URL for the scheme (used later for citations).
- `text`: the actual text content (potentially multi-line).

The Phase 2 index stores:

- A list of all `DocumentChunk` objects (via metadata dicts).
- A TF‑IDF vectorizer.
- A TF‑IDF matrix of shape `(num_chunks, vocab_size)`.

---

## Building the index (running Phase 2)

From the project root:

```bash
pip install -r phase-2-knowledge-base/requirements.txt

# Make sure Phase 1 snapshots exist (run Phase 1 scraper first if needed)
python phase-1-data-acquisition/scrape_all.py

# Build the TF-IDF index over all scheme sections
python phase-2-knowledge-base/build_index.py
```

This will create:

- `phase-2-knowledge-base/index.pkl` – pickled dict with:
  - `vectorizer`: fitted `TfidfVectorizer` instance.
  - `matrix`: TF‑IDF sparse matrix (`scipy.sparse`).
  - `chunks`: list of metadata dicts for each `DocumentChunk`.

The script prints a short summary:

- How many JSON snapshots were loaded.
- How many chunks were indexed.
- Basic stats on the vocabulary size.

---

## Using the index (example pattern)

In later phases (backend), you can:

1. Load `index.pkl`.
2. Convert a user query to TF‑IDF using the stored vectorizer.
3. Compute cosine similarity against the stored matrix.
4. Take the top‑k chunks and read their `scheme_id`, `attribute_type`, `source_url`, and `text` for answer generation.

This can be upgraded to a neural embedding index later without changing the higher-level orchestration logic.

