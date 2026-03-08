## RAG Chatbot for Groww Mutual Funds – Phase-wise Architecture

This document describes a phase-wise architecture for a **Retrieval-Augmented Generation (RAG)** chatbot focused on **Groww mutual funds**, initially limited to HDFC schemes:

- **HDFC Small Cap Fund**
- **HDFC NIFTY50 Equal Weight Index Fund**
- **HDFC Retirement Savings Fund**
- **HDFC Multi-Asset Active FoF Direct-Growth**

Primary reference directory: [`Groww Mutual Funds Explore`](https://groww.in/mutual-funds/user/explore).

The chatbot:

- Answers **factual questions only** (no advice) about:
  - Expense ratio
  - Exit load
  - Minimum SIP / minimum lump sum
  - Lock-in (ELSS / other constraints)
  - Riskometer
  - Benchmark
  - How to download statements (from Groww)
- Uses **only official public pages** (primarily Groww pages for Phase 1).
- Includes **at least one source link** in **every** answer.
- Uses an **LLM (Groq)** strictly in a **retrieval-grounded** way:
  - The chatbot must **only** answer using information present in retrieved embeddings / scheme snapshots.
  - If the answer is not supported by retrieved context, it must say it does not know or direct the user to the official page.
- Treats any request for **personal information** (e.g. PAN, Aadhaar, phone number, email, address, portfolio-specific details) as **out of scope** and does not answer such questions.

Each phase below will correspond to a folder when implementation is requested, using this naming pattern:

- `phase-0-requirements/`
- `phase-1-data-acquisition/`
- `phase-2-knowledge-base/`
- `phase-3-query-orchestration/`
- `phase-4-safety-eval/`
- `phase-5-app-backend-frontend/`
- `phase-6-scheduler-refresh/`
- `phase-7-deployment-ops/`
- `phase-8-extensions/`

---

## Phase 0 – Requirements, Compliance & Data Scope

**Goals**

- Precisely define scope, compliance constraints, data sources, and functional/non-functional requirements.

**Key decisions**

- **Scope of questions (Phase 1):**
  - **Allowed**:
    - Expense ratio
    - Exit load
    - Minimum SIP and minimum lump sum
    - Lock-in period (including whether the scheme is ELSS)
    - Riskometer level
    - Benchmark index
    - How to download account/transaction statements related to these schemes on Groww
  - **Not allowed**:
    - “Should I invest?”, “Is this good for me?”, “Which is better?”
    - Portfolio construction, asset allocation, tax or personalized advice
    - Cross-platform guidance (only Groww flows are in scope)
- **Authoritative sources** (Phase 1):
  - Groww scheme pages and related sections under [`https://groww.in/mutual-funds/user/explore`](https://groww.in/mutual-funds/user/explore).
  - If needed later: official AMC HDFC mutual fund scheme pages (future extension).
- **Answer policy**:
  - Every answer:
    - Must be **purely factual** and clearly avoid recommendations.
    - Must include **≥ 1 source link** to an allowed domain (e.g. `groww.in` scheme page or relevant help article).
    - Must include a short disclaimer like: “This is for general information only and is not investment advice.”
  - If the information is not found in the knowledge base:
    - The bot should say it cannot find that specific detail and point the user to the most relevant scheme page.
- **Data freshness strategy**:
  - Phase 1: daily or scheduled re-crawl (coordinated by Phase 6).
  - Later: configurable frequency and optional on-demand refresh.

**Outputs**

- Requirements and safety specification (implemented in `phase-0-requirements/`).
- Clear mapping of “allowed vs disallowed” question types with examples.
- List of canonical URLs for each of the 4 HDFC schemes.

---

## Phase 1 – Data Acquisition & Normalization (HDFC – 4 Schemes)

**Goals**

- From public Groww pages, collect and normalize factual content for the 4 target HDFC schemes into a clean, machine-readable schema.

**Main components**

- **`crawler-service`**
  - Inputs:
    - Root page: [`Groww Mutual Funds Explore`](https://groww.in/mutual-funds/user/explore).
    - Seed filters: AMC = HDFC, target scheme names.
  - Outputs:
    - Raw HTML and/or JSON snapshots for:
      - The explore/listing page (for navigation and basic info).
      - Each scheme’s detail page.
- **`mf-parser`**
  - Extracts structured fields and readable text sections per scheme, e.g.:
    - Name, AMC, category/subcategory.
    - Plan (e.g. “Direct-Growth”).
    - Expense ratio (value, as-of date, raw text).
    - Exit load (human-readable rules; optional structured slabs).
    - Minimum SIP, minimum lump sum (normalized to numeric amounts).
    - Lock-in period (months, ELSS flag, raw description).
    - Riskometer label + short description.
    - Benchmark name and type.
    - Any Groww-documented instructions for statement downloads.
  - Produces a canonical `Scheme` document for each scheme.

**Data schema (conceptual)**

- `Scheme`:
  - Identification: `id`, `name`, `amc`, `plan`, `category`, `subcategory`.
  - Key facts: `expense_ratio`, `exit_load`, `min_sip`, `min_lumpsum`, `lock_in_period`, `riskometer`, `benchmark`.
  - Support text:
    - `statement_download_instructions`: ordered steps for Groww.
    - `full_text_sections`: array of `{ section_title, body_text }`.
  - Metadata: `source_url`, `source_last_fetched_at`.

**Storage**

- **Structured store**:
  - Relational (Postgres/SQLite) or document store.
  - Used for precise fact lookups.
- **Raw/long text store**:
  - Underlying text for RAG (later used by Phase 2).

---

## Phase 2 – Knowledge Base Preparation & Indexing (RAG Layer)

**Goals**

- Turn raw and structured data into a **retrieval-ready knowledge base** for the RAG pipeline.

**Main components**

- **`doc-preprocessor`**
  - Converts `full_text_sections` and important descriptions into documents like:
    - “HDFC Small Cap Fund – Key Facts”
    - “HDFC Small Cap Fund – Exit Load”
    - “HDFC Small Cap Fund – Riskometer”
  - Adds metadata per document:
    - `scheme_id`, `scheme_name`, `attribute_type` (e.g. `expense_ratio`, `exit_load`, `statement_download`), `source_url`.
  - Chunks documents into overlapping segments (e.g. 300–500 tokens).
- **`embedding-service`**
  - Generates vector embeddings for each chunk using a chosen model.
- **`vector-store`**
  - Stores:
    - Embeddings
    - Chunk text
    - Metadata (including `source_url` and `attribute_type`)
  - Supports filtered search (e.g. restrict to HDFC, or to a specific scheme).
- **`fact-store` (structured index)**
  - Backed by the structured DB from Phase 1.
  - Offers precise lookups for:
    - `(scheme, attribute_type)` → normalized values + canonical `source_url`.

---

## Phase 3 – Query Understanding & Retrieval Orchestration

**Goals**

- Interpret user questions, decide what data to fetch, and orchestrate retrieval from both the structured `fact-store` and the `vector-store`.
- Ensure that all downstream LLM calls (Groq) are **fully grounded** in retrieved context, never in the model’s own prior knowledge.

**Main components**

- **`intent-classifier`**
  - Classifies user queries into buckets such as:
    - `FACT_ATTRIBUTE_QUERY`
    - `STATEMENT_DOWNLOAD_QUERY`
    - `META_QUERY` (e.g. “What can you answer?”)
    - `OUT_OF_SCOPE` (advice, comparisons, non-Groww, **personal information**, etc.)
- **`entity-extractor`**
  - Extracts:
    - Scheme name (mapped to internal `scheme_id` via alias table).
    - Attribute types (expense ratio, exit load, minimum SIP, etc.).
- **`retrieval-orchestrator`**
  - For `FACT_ATTRIBUTE_QUERY`:
    - Prefer `fact-store` for exact values.
    - Optionally enrich with contextual chunks from `vector-store`.
  - For `STATEMENT_DOWNLOAD_QUERY`:
    - Target chunks with `attribute_type = statement_download`.
    - Fall back to general Groww help content if necessary.
  - For `OUT_OF_SCOPE`:
    - Avoid knowledge base retrieval; route to guardrail logic and return a scoped refusal.
  - For **all answerable queries**:
    - Perform retrieval first (from embeddings / snapshots).
    - If retrieval returns **no sufficiently relevant chunks**, do **not** answer using the LLM’s own knowledge; instead, say the answer is unavailable and link to the most relevant scheme page.
    - Pass only the retrieved chunks plus the user query into the Groq LLM, with strong instructions to:
      - Use **only** the provided context.
      - Say “I don’t know” or similar if the context does not contain the answer.

Outputs from Phase 3:

- A compact **retrieval bundle**:
  - Recognized intent and entities.
  - Retrieved facts and relevant text chunks.
  - Associated `source_url` set.
  - A **Groq-ready prompt payload** for later phases, including:
    - The user query.
    - Selected context chunks.
    - System instructions enforcing retrieval-grounding and scope (no advice, no personal information handling).

---

## Phase 4 – Safety, Guardrails & Evaluation

**Goals**

- Ensure that responses are **non-advisory**, low-hallucination, and always sourced.

**Guardrails**

- **No-advice / no-comparison rules**:
  - Rule-based filter for phrases like “you should invest”, “best fund”, “better than”, “buy/sell”, etc.
  - Optional LLM-based safety check to flag:
    - Personalized recommendations.
    - Cross-scheme recommendations.
    - Tax or portfolio advice.
- **Source enforcement**:
  - Every answer must contain **at least one** URL from an approved domain list (`groww.in` in Phase 1).
  - If missing, the pipeline regenerates or appends the appropriate scheme link.

**Evaluation**

- **Test set** of queries:
  - Positive: each allowed attribute, per scheme.
  - Negative: advice-seeking, cross-scheme comparisons, unsupported tasks.
- **Metrics**:
  - Factual accuracy vs ground truth from Groww.
  - Presence & quality of citations.
  - Rate of blocked/flagged unsafe answers.

---

## Phase 5 – Chat Application Backend & Frontend

**Goals**

- Build the **user-facing chat experience** and the **application backend** that uses Phases 2–4.

### Backend (to be implemented in `phase-5-app-backend-frontend/`)

- **`chat-backend` service**
  - Exposes an API endpoint (e.g. `POST /chat`) consumed by the frontend.
  - Coordinates:
    - Intent classification and entity extraction (Phase 3).
    - Retrieval from `fact-store` and `vector-store` (Phases 2–3).
    - Safety checks (Phase 4).
    - Response generation via a **Groq LLM**, constrained by system prompts that:
      - Enforce use of **only retrieved context** from embeddings / snapshots.
      - Forbid investment advice and personal information handling.
      - Require an explicit “I don’t know” style response when context is insufficient.
  - Manages short-term conversation context per user session.
  - Returns:
    - Plain-language answer.
    - Highlighted facts (structured payload for UI).
    - List of `source_urls` used for citations.

### Frontend (to be implemented in `phase-5-app-backend-frontend/`)

- **Web UI** (SPA or simple web app):
  - Chat-style interface (message bubbles).
  - Optional scheme selector (helps disambiguate scheme names).
  - Shows:
    - Bot answer text.
    - Highlighted key values (expense ratio, minimum SIP, etc.).
    - Explicit source link(s) for each answer (clickable links to Groww).
    - A visible disclaimer: “No investment advice; information may change; refer to official pages.”
  - Optional features:
    - Clear indication of which scheme is being discussed.
    - Basic session history within a page.

---

## Phase 6 – Scheduler & Automated Data Refresh

**Goals**

- Keep the knowledge base up to date by **periodically refreshing data** from Groww and re-running dependent phases.

**Main components**

- **`scheduler-service`** (cron, Airflow, or similar):
  - On a fixed schedule (e.g. daily, or configurable):
    1. Triggers **Phase 1**:
       - Run `crawler-service` to re-fetch scheme pages from Groww.
       - Run `mf-parser` to update structured facts and text sections.
    2. Triggers **Phase 2**:
       - Re-run `doc-preprocessor`.
       - Update embeddings via `embedding-service`.
       - Upsert into `vector-store` and `fact-store`.
    3. Optionally runs automated **smoke tests** (subset of Phase 4 evaluation).
  - Maintains status logs:
    - Last successful crawl time per scheme.
    - What changed (e.g. expense ratio updated).

**Data freshness strategy**

- Use **idempotent upserts** so re-runs are safe.
- Make freshness visible to the chat layer (e.g. “data as of DD-MM-YYYY” if required).

---

## Phase 7 – Deployment, Monitoring & Operations

**Goals**

- Deploy the system reliably and observe its behavior in real usage.

**Main components**

- **Deployment**
  - Containerize:
    - `chat-backend`
    - `crawler-service` and `mf-parser`
    - `embedding-service`
    - `scheduler-service`
  - Deploy to a chosen environment (cloud or on-prem).
- **Monitoring & logging**
  - Collect:
    - Chat API latencies, error rates.
    - Scheduler job statuses and failures.
    - Vector-store and DB health.
  - Log (with privacy in mind):
    - User queries.
    - Retrieved sources.
    - Final outputs and safety violations (if any).
- **Alerting**
  - Alerts for:
    - Persistent crawl failures (e.g. Groww page structure changes).
    - High error rates in chat API.
    - Increased rate of “I don’t know / out of scope” answers.

---

## Phase 8 – Future Extensions

**Potential directions**

- **Broader coverage**:
  - Additional HDFC schemes.
  - Other AMCs and categories (within the same safety constraints).
- **Richer attributes**:
  - Performance metrics, rolling returns, risk statistics (still no recommendations).
  - More operational FAQs (e.g. KYC, folio details) as allowed by requirements.
- **Multi-lingual support**:
  - Support for additional Indian languages with the same guardrails.
- **User experience enhancements**:
  - Suggested follow-up questions.
  - Richer formatting of answers (tables for exit load slabs, etc.).

