## Phase 0 – Requirements, Compliance & Data Scope

This document captures the **functional scope**, **compliance boundaries**, and **data constraints** for the Groww mutual fund RAG chatbot. It operationalizes Phase 0 of the architecture described in `ARCHITECTURE.md`.

---

## 1. Problem Statement (Phase 1 Scope)

- Build a **RAG chatbot** that answers **factual questions** about the following HDFC mutual fund schemes using **only official public pages** (primarily Groww for Phase 1):
  - HDFC Small Cap Fund
  - HDFC NIFTY50 Equal Weight Index Fund
  - HDFC Retirement Savings Fund
  - HDFC Multi-Asset Active FoF Direct-Growth
- Primary starting page:
  - [`Groww Mutual Funds Explore`](https://groww.in/mutual-funds/user/explore)

The chatbot should:

- Provide **fact-based responses** only.
- Include **at least one source link** to an official page in every answer.
- Explicitly state that it does **not provide investment advice**.

---

## 2. In-Scope Question Types (Phase 1)

For the 4 HDFC schemes listed above, the bot may answer factual questions such as:

- **Expense ratio**
  - “What is the expense ratio of HDFC Small Cap Fund (Direct-Growth)?”
- **Exit load**
  - “What is the exit load for HDFC NIFTY50 Equal Weight Index Fund?”
- **Minimum SIP / minimum lump sum**
  - “What is the minimum SIP amount for HDFC Retirement Savings Fund on Groww?”
  - “What is the minimum lumpsum investment for HDFC Multi-Asset Active FoF Direct-Growth?”
- **Lock-in / ELSS**
  - “Does HDFC Retirement Savings Fund have a lock-in period?”
  - “Is this scheme an ELSS fund and what is the lock-in?”
- **Riskometer**
  - “What is the riskometer level of HDFC Small Cap Fund?”
- **Benchmark**
  - “What is the benchmark index for HDFC NIFTY50 Equal Weight Index Fund?”
- **How to download statements on Groww**
  - “How do I download my statement for HDFC Small Cap Fund on Groww?”
  - “Steps to get mutual fund statement from Groww for HDFC Retirement Savings Fund.”

For any such question, the chatbot:

- Must answer only if the information is present in the ingested official pages.
- Must cite **at least one** relevant Groww (or approved) link as the source.

---

## 3. Out-of-Scope / Disallowed Queries

The chatbot must **not** answer (and should instead respond with a polite refusal and a reminder of its scope) for all of the following:

- **Investment recommendations and advice**
  - “Should I invest in HDFC Small Cap Fund?”
  - “Is HDFC NIFTY50 Equal Weight Index Fund good for retirement?”
  - “Which HDFC fund is best for me?”
- **Comparisons and rankings**
  - “Is HDFC Small Cap Fund better than other small cap funds?”
  - “Which is better: HDFC Retirement Savings Fund or [another fund]?”
- **Portfolio construction / asset allocation**
  - “How much should I allocate to HDFC Multi-Asset Active FoF Direct-Growth?”
  - “Create a mutual fund portfolio for me.”
- **Tax or personalized financial planning**
  - “How much tax will I save by investing in this fund?”
  - “What is the best way to plan my retirement with HDFC funds?”
- **Non-Groww operational flows**
  - “How do I download statements from some other platform?”
  - “How do I open an account with another broker?”

For these queries, the bot should:

- Explain that it is limited to **factual scheme information and Groww-specific operational steps**.
- Avoid suggesting any particular action or fund.

---

## 4. Data Sources & Allowed Domains

**Authoritative primary source (Phase 1):**

- Groww website:
  - Explore/listing page: [`https://groww.in/mutual-funds/user/explore`](https://groww.in/mutual-funds/user/explore)
  - Individual scheme detail pages under `https://groww.in/mutual-funds/…`

**Allowed domains for citations:**

- `groww.in` (Phase 1)
  - Scheme detail pages.
  - Groww help/FAQ pages (for statement download steps, if needed).

**Future/optional sources (to be explicitly enabled later):**

- Official HDFC Mutual Fund AMC pages for the same schemes.

The system must **not** fabricate URLs or cite non-official pages.

---

## 5. Answer Formatting & Citation Rules

Every chatbot answer must satisfy all of the following:

- **Factual and neutral tone**
  - No prescriptive language like “you should”, “you must”, “this is the best”.
- **At least one source link**
  - Use a markdown-style link, e.g.:
    - `Source: [Groww – HDFC Small Cap Fund](https://groww.in/...)`
  - The URL must be from an **allowed domain**.
- **Clear scope and disclaimer**
  - Include a short disclaimer, such as:
    - “This is general information from the official page and is not investment advice.”
  - If the answer is incomplete or approximate (e.g. when some detail is not found), state that explicitly.
- **No hallucinated facts**
  - If a field is unavailable in the ingested data:
    - The bot should say it cannot find that information and direct the user to the appropriate source page instead of guessing.

---

## 6. Non-Functional Requirements

- **Accuracy**
  - Answers must reflect the latest ingested data.
  - If data is stale or last updated date is available, the system may optionally expose “as of” information.
- **Latency**
  - Target: sub-second retrieval, and overall response time within acceptable UX limits for a chat application (e.g. 1–3 seconds depending on LLM calls).
- **Availability**
  - The chat API should handle normal user load with graceful degradation if vector DB or crawler is temporarily unavailable.
- **Privacy**
  - Do not log personally identifiable information beyond what is strictly needed for debugging.
  - If user identifiers are logged, they must be anonymized or tokenized.

---

## 7. Interface Expectations for Later Phases

These are expectations from later technical phases, captured now to keep Phase 0 concrete:

- **From Phase 1 (Data Acquisition & Normalization)**
  - A structured `Scheme` record per target scheme, including:
    - Expense ratio, exit load, min SIP, min lump sum, lock-in, riskometer, benchmark, and statement download instructions (if present).
    - Source URL and last fetched timestamp for each record.
- **From Phase 2 (Knowledge Base & Indexing)**
  - A vector index and fact store that can be queried by:
    - `(scheme_name, attribute_type)` for precise fields.
    - Free-text queries for context (RAG).
- **From Phase 3 (Query Orchestration)**
  - A well-defined contract for:
    - Input: user utterance (and short context).
    - Output: intended scheme, attribute(s), and raw retrieved context.
- **From Phase 4 (Safety)**
  - A mechanism to automatically detect and block:
    - Advice & recommendations.
    - Comparisons and “which is best” style answers.

---

## 8. Phase 0 Deliverables

- This `README.md` as the canonical **requirements and safety specification**.
- Alignment between:
  - In-scope vs out-of-scope questions.
  - Allowed domains for data and citations.
  - Answer formatting rules (source links + disclaimer).
- A clear foundation for:
  - Phase 1 implementation in `phase-1-data-acquisition/`.
  - Subsequent phases (knowledge base, orchestration, frontend/backend, scheduler).

