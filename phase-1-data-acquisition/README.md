## Phase 1 – Data Acquisition & Normalization

This module implements **Phase 1** of the architecture: crawling and parsing Groww pages for the target HDFC schemes, and extracting the key textual sections needed for the RAG chatbot.

For each scheme, we:

- Fetch the HTML from its **Groww** page.
- Strip scripts/styles and reduce to a clean text representation.
- Extract the following sections (when present):
  - **Performance**
  - **Fundamentals**
  - **Return calculator**
  - **Category returns / Returns and rankings**
  - **About / investment objective**
  - **Similar ETFs / Compare similar funds**
- Persist the result as **JSON** files (one per scheme) under `out/`.

This is intentionally text-centric: later phases can further enrich and structure the data if needed.

---

## Target schemes and URLs

We currently support the following HDFC schemes (Phase 1 scope):

- **ETF**
  - HDFC Nifty 1D Rate Liquid ETF – Growth  
    - `https://groww.in/etfs/hdfc-nifty-d-rate-liquid-etf`
- **Mutual funds**
  - HDFC Small Cap Fund – Direct Growth  
    - `https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth`
  - HDFC NIFTY 50 Index Fund – Direct Growth  
    - `https://groww.in/mutual-funds/hdfc-nifty-50-index-fund-direct-growth`
  - HDFC Retirement Savings Fund Equity Plan – Direct Growth  
    - `https://groww.in/mutual-funds/hdfc-retirement-savings-fund-equity-plan-direct-growth`
  - HDFC Multi Asset Allocation Fund – Direct Growth  
    - `https://groww.in/mutual-funds/hdfc-multi-asset-allocation-fund-direct-growth`

The list of schemes is defined in `schemes.py`.

---

## Data model

The main normalized object is `SchemeSnapshot` (see `models.py`):

- **Metadata**
  - `id`: stable internal identifier (snake_case).
  - `name`: display name from config.
  - `scheme_type`: `"etf"` or `"mutual_fund"`.
  - `url`: canonical Groww URL.
- **Sections** (all stored as plain text, ready for RAG):
  - `performance_text`
  - `fundamentals_text`
  - `returns_calculator_text`
  - `category_returns_text`
  - `about_text`
  - `similar_schemes_text`

If a section cannot be found, the corresponding field is set to an empty string.

---

## How it works

### 1. Fetching HTML

`scrape_all.py` uses `requests` to download each scheme page:

- Handles timeouts and HTTP errors.
- Saves a copy of the raw HTML into `raw/{scheme_id}.html` for debugging.

### 2. Cleaning text

`parser_utils.py`:

- Uses `BeautifulSoup` (with `lxml`) to drop `<script>`, `<style>`, `<noscript>` tags.
- Converts the page to a plain text representation with `\n` separators.

### 3. Extracting sections

`parsers.py` contains generic helpers:

- We treat the cleaned page text as a sequence of lines.
- For each logical section we look for a header line (case-insensitive), using aliases:
  - Performance → `["Performance"]`
  - Fundamentals → `["Fundamentals"]`
  - Return calculator → `["Return calculator"]`
  - Category returns → `["Category returns", "Returns and rankings"]`
  - About / Objective → `["About", "About HDFC", "About HDFC Small Cap Fund", "About HDFC NIFTY 50 Index Fund", "About HDFC Retirement Savings Fund Equity Plan Direct Growth", "About HDFC Multi Asset Allocation Fund Direct Growth"]`
  - Similar / compare → `["Similar ETFs", "Compare similar funds"]`
- For each header we:
  - Take all subsequent non-empty lines until we hit another known section header.
  - Join them into a multi-line string for that section.

The same generic parser is used for both the ETF and mutual fund pages.

---

## Running the scraper

From the project root:

```bash
pip install -r phase-1-data-acquisition/requirements.txt
python -m phase-1-data-acquisition.scrape_all
```

This will:

- Create `phase-1-data-acquisition/raw/` with raw HTML snapshots.
- Create `phase-1-data-acquisition/out/` with one JSON file per scheme, e.g.:
  - `hdfc_nifty_1d_rate_liquid_etf.json`
  - `hdfc_small_cap_fund_direct_growth.json`
  - `hdfc_nifty_50_index_fund_direct_growth.json`
  - `hdfc_retirement_savings_fund_equity_plan_direct_growth.json`
  - `hdfc_multi_asset_allocation_fund_direct_growth.json`

Each JSON file is a serialized `SchemeSnapshot`.

---

## Notes and limitations

- This is a **best-effort text scraper** against Groww’s current page structure.
  - If Groww significantly changes layout or wording of section headers, parsers may need to be updated.
- Numeric values (e.g., NAV, returns) are currently kept as **text** inside their sections.
  - Later phases can add more structured parsing on top of this representation if required.
- Network access and terms-of-use:
  - Use reasonable request rates (no aggressive crawling).
  - Respect Groww’s robots and terms in an actual deployment.

