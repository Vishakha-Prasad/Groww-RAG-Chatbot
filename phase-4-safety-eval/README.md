## Phase 4 – Safety, Guardrails & Evaluation

This module implements **Phase 4** of the architecture:

- Performs **post-generation checks** on answers produced by Phase 3.
- Enforces:
  - No investment advice / recommendations / comparisons.
  - No handling of **personal information**.
  - Presence of at least one **allowed-domain source URL** (e.g. `groww.in`).
- Provides a simple **evaluation harness** over a small test set of queries.

This layer is designed to be called from the chat backend (Phase 5) after an answer is generated.

---

## Components

### 1. `guardrails.py`

Contains rules to validate an answer:

- `check_answer(answer: str) -> dict`
  - Returns:
    - `has_advice_language: bool`
    - `has_personal_info_language: bool`
    - `has_allowed_source_url: bool`
    - `issues: list[str]` – human-readable flags.
- Investment-advice detection:
  - Looks for phrases like:
    - “should I invest”, “you should invest”, “best fund”, “better than”, “recommend”, “suggest”, “buy”, “sell”.
- Personal-info detection:
  - Same patterns as Phase 3 (PAN, Aadhaar, phone, email, address, account number, “my portfolio”, “my holdings”, etc.).
- Source URL check:
  - Searches `answer` for at least one URL substring containing `"groww.in"`.

The chat backend can use this result to:

- Decide whether to return the answer as-is.
- Or replace it with a safer fallback message if any issues are detected.

### 2. `eval_sample.py`

A minimal evaluation script that:

- Uses `phase-3-query-orchestration.answer_query`.
- Applies `check_answer` on each answer.
- Prints a small report.

> This is intentionally very light-weight; you can expand it into a more formal test suite as the project evolves.

---

## Usage

From the project root, to run the sample evaluation:

```bash
python phase-4-safety-eval/eval_sample.py
```

This will:

- Run a handful of sample queries (factual, advice-seeking, personal-info).
- Print out:
  - The answer.
  - The guardrail flags from `check_answer`.

In a production backend (Phase 5), you’d typically:

1. Call `answer_query` from Phase 3.
2. Pass `result["answer"]` into `check_answer`.
3. If any **critical issues** (e.g. advice or personal info) are found:
   - Replace the answer with a scoped refusal before returning to the user.

