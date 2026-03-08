# Phase 6 – Scheduler & Automated Data Refresh

This module keeps the chatbot's knowledge base up to date by periodically
re-crawling Groww scheme pages and rebuilding the TF-IDF index.

## How It Works

The scheduler runs two steps in sequence:

1. **Phase 1 Re-scrape** – Calls `phase-1-data-acquisition/scrape_all.py` to
   re-fetch scheme pages from Groww and update the JSON snapshots in `out/`.
2. **Phase 2 Re-index** – Calls `phase-2-knowledge-base/build_index.py` to
   rebuild the TF-IDF index (`index.pkl`) from the updated snapshots.

All runs are logged to `refresh_log.json` for auditability.

## Usage

```bash
# One-time full refresh (re-scrape + re-index):
python scheduler.py

# Dry-run (preview what would happen, no changes):
python scheduler.py --dry-run

# Start as a background daemon (runs every 24 hours):
python scheduler.py --daemon

# Custom interval (e.g., every 12 hours):
python scheduler.py --daemon --interval 12
```

## Requirements

- Python 3.10+
- `schedule` package (only needed for `--daemon` mode): `pip install schedule`
- Phases 1 and 2 must be set up and functional.

## Log Format

Each refresh produces a JSON entry in `refresh_log.json`:

```json
{
  "started_at": "2026-03-08T14:00:00+00:00",
  "finished_at": "2026-03-08T14:01:23+00:00",
  "dry_run": false,
  "steps": [
    {"step": "Phase 1 – Re-scrape Groww pages", "status": "ok"},
    {"step": "Phase 2 – Rebuild TF-IDF index", "status": "ok"}
  ],
  "overall": "ok"
}
```
