## Phase 3 – Query Understanding & Retrieval Orchestration

This module implements **Phase 3** of the architecture:

- Interprets user questions (intent + basic entity recognition).
- Retrieves relevant context from the **Phase 2 TF‑IDF index** (embeddings).
- Enforces **scope rules**:
  - Only facts about the configured HDFC schemes.
  - No investment advice or recommendations.
  - No handling of **personal information** (PAN, Aadhaar, phone, email, address, portfolio details, etc.).
- Calls a **Groq LLM** to generate answers that are:
  - Fully **grounded in retrieved context** only.
  - Refuse to answer when context is missing or question is out-of-scope.

> The chatbot must not answer from the LLM’s own prior knowledge; it must only use information present in retrieved chunks. Personal-information questions are treated as out-of-scope.

---

## Components

### 1. `intent.py`

Implements lightweight intent and scope detection:

- `classify_intent(query: str) -> str`
  - Returns one of:
    - `"FACT_ATTRIBUTE_QUERY"`
    - `"STATEMENT_DOWNLOAD_QUERY"`
    - `"META_QUERY"`
    - `"OUT_OF_SCOPE"`
- `is_personal_info_query(query: str) -> bool`
  - Detects obvious personal info patterns (PAN, Aadhaar, phone, email, address, “my portfolio”, “my holdings”, etc.).
  - If `True`, we always treat the query as **out-of-scope** and respond accordingly (no retrieval, no LLM call).

### 2. `retriever.py`

Loads and queries the Phase 2 TF‑IDF index:

- On import, loads `phase-2-knowledge-base/index.pkl`:
  - `vectorizer`
  - `matrix`
  - `chunks` (metadata for each `DocumentChunk`)
- `retrieve_top_k(query: str, k: int = 5, min_score: float = 0.0) -> list[dict]`
  - Vectorizes the query and computes cosine similarity to all chunks.
  - Returns top‑k chunks with:
    - `text`
    - `scheme_id`
    - `scheme_name`
    - `attribute_type`
    - `source_url`
    - `score`
  - If all scores are below `min_score`, returns an empty list to signal “no confident context”.

### 3. `llm_client.py`

Wraps the **Groq** LLM using API keys in `.env`:

- Reads:
  - `GROQ_API_KEY`
  - `GROQ_MODEL` (e.g. `llama-3.1-8b-instant` or another supported model)
- Exposes:

```python
generate_answer_with_groq(
    user_query: str,
    context_chunks: list[dict],
) -> str
```

- Constructs a strong **system prompt** that enforces:
  - Use **only** the provided context chunks.
  - Do **not** use any external or prior knowledge.
  - If the context does not contain the answer, respond with:
    - A clear “I don’t know / cannot find this in the provided information” message, and
    - Suggest checking the official Groww scheme page.
  - No investment advice or recommendations.
  - No handling of personal information, even if the user asks for it.
  - Every answer must include at least one **source URL** taken from the chunk metadata.

### 4. `chat_pipeline.py`

High-level, end-to-end orchestration for a single-turn query:

- `answer_query(query: str) -> dict`
  - Steps:
    1. Run `is_personal_info_query`:
       - If `True`, return an out-of-scope refusal (no retrieval, no LLM).
    2. Run `classify_intent`:
       - If `OUT_OF_SCOPE`, return a scoped refusal.
    3. Run `retrieve_top_k` against Phase 2 index:
       - If no chunks (or all scores are too low), return a “cannot answer from current data” message plus a generic Groww link.
    4. Call `generate_answer_with_groq` with the query + retrieved chunks.
  - Returns:
    - `"answer"`: final text from Groq.
    - `"used_chunks"`: list of chunk metadata used as context (for debugging / tracing).

If run as a script:

```bash
python phase-3-query-orchestration/chat_pipeline.py
```

It will:

- Prompt once on stdin for a question.
- Print the structured answer JSON to stdout.

> Note: Running this requires:
> - A valid `.env` file at the project root with Groq credentials.
> - A built TF‑IDF index from Phase 2 (`phase-2-knowledge-base/index.pkl`).

---

## Environment variables (`.env`)

At the project root (`ChatBot2/.env`), define:

```bash
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
```

You can change `GROQ_MODEL` to any supported Groq chat model. The Phase 3 code will load these values automatically via `python-dotenv`.

