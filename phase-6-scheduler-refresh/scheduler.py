from __future__ import annotations

"""
Phase 6 – Scheduler & Automated Data Refresh

Orchestrates periodic re-crawling of Groww scheme pages (Phase 1)
and re-building the TF-IDF index (Phase 2) so the chatbot's knowledge
base stays current.

Usage:
    # Full refresh (re-scrape + re-index):
    python scheduler.py

    # Dry-run (show what would happen, no network/disk changes):
    python scheduler.py --dry-run

    # Start as a background scheduler (runs every 24h):
    python scheduler.py --daemon
"""

import argparse
import json
import logging
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

try:
    import schedule  # type: ignore
except ImportError:
    schedule = None


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PHASE1_DIR = PROJECT_ROOT / "phase-1-data-acquisition"
PHASE2_DIR = PROJECT_ROOT / "phase-2-knowledge-base"
LOG_PATH = Path(__file__).resolve().parent / "refresh_log.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)


def _run_step(description: str, cmd: list[str], cwd: Path, dry_run: bool = False) -> Dict[str, Any]:
    """Run a subprocess step and return a status dict."""
    log.info("Step: %s", description)
    if dry_run:
        log.info("  [DRY-RUN] Would run: %s (in %s)", " ".join(cmd), cwd)
        return {"step": description, "status": "dry-run", "detail": "skipped"}

    try:
        result = subprocess.run(
            cmd,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=300,
        )
        if result.returncode != 0:
            log.error("  FAILED (exit code %d)\n%s", result.returncode, result.stderr[:500])
            return {
                "step": description,
                "status": "failed",
                "exit_code": result.returncode,
                "stderr": result.stderr[:500],
            }
        log.info("  OK")
        return {"step": description, "status": "ok", "stdout_tail": result.stdout[-300:] if result.stdout else ""}
    except subprocess.TimeoutExpired:
        log.error("  TIMEOUT after 300s")
        return {"step": description, "status": "timeout"}
    except FileNotFoundError as exc:
        log.error("  NOT FOUND: %s", exc)
        return {"step": description, "status": "error", "detail": str(exc)}


def run_refresh(dry_run: bool = False) -> Dict[str, Any]:
    """
    Execute the full refresh pipeline:
      1. Re-scrape Groww pages (Phase 1)
      2. Re-build TF-IDF index (Phase 2)
    
    Returns a summary dict with timestamps and per-step results.
    """
    started_at = datetime.now(timezone.utc).isoformat()
    log.info("=" * 60)
    log.info("DATA REFRESH STARTED at %s", started_at)
    log.info("=" * 60)

    steps = []

    # --- Phase 1: Re-scrape ---
    scrape_script = PHASE1_DIR / "scrape_all.py"
    if scrape_script.exists():
        step = _run_step(
            "Phase 1 – Re-scrape Groww pages",
            [sys.executable, str(scrape_script)],
            cwd=PHASE1_DIR,
            dry_run=dry_run,
        )
        steps.append(step)
    else:
        log.warning("Scrape script not found at %s – skipping Phase 1 scrape.", scrape_script)
        steps.append({"step": "Phase 1 – Re-scrape", "status": "skipped", "detail": "script not found"})

    # --- Phase 2: Re-build index ---
    build_script = PHASE2_DIR / "build_index.py"
    if build_script.exists():
        step = _run_step(
            "Phase 2 – Rebuild TF-IDF index",
            [sys.executable, str(build_script)],
            cwd=PHASE2_DIR,
            dry_run=dry_run,
        )
        steps.append(step)
    else:
        log.warning("Index builder not found at %s – skipping Phase 2 build.", build_script)
        steps.append({"step": "Phase 2 – Rebuild index", "status": "skipped", "detail": "script not found"})

    finished_at = datetime.now(timezone.utc).isoformat()

    summary: Dict[str, Any] = {
        "started_at": started_at,
        "finished_at": finished_at,
        "dry_run": dry_run,
        "steps": steps,
        "overall": "ok" if all(s["status"] in ("ok", "dry-run", "skipped") for s in steps) else "failed",
    }

    # Persist log
    if not dry_run:
        _append_log(summary)

    log.info("=" * 60)
    log.info("DATA REFRESH FINISHED – overall: %s", summary["overall"])
    log.info("=" * 60)

    return summary


def _append_log(entry: Dict[str, Any]) -> None:
    """Append a refresh entry to the JSON log file."""
    history: list = []
    if LOG_PATH.exists():
        try:
            history = json.loads(LOG_PATH.read_text(encoding="utf-8"))
        except Exception:
            history = []

    history.append(entry)

    # Keep only the last 100 entries
    history = history[-100:]
    LOG_PATH.write_text(json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8")
    log.info("Log written to %s", LOG_PATH)


def run_daemon(interval_hours: int = 24) -> None:
    """Run the scheduler as a daemon, refreshing every `interval_hours`."""
    if schedule is None:
        log.error(
            "The 'schedule' package is required for daemon mode. "
            "Install it with: pip install schedule"
        )
        sys.exit(1)

    log.info("Starting scheduler daemon – refresh every %d hour(s).", interval_hours)
    schedule.every(interval_hours).hours.do(run_refresh)

    # Also run once immediately
    run_refresh()

    while True:
        schedule.run_pending()
        time.sleep(60)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Phase 6 – Groww Data Refresh Scheduler",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen without making changes.",
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as a background scheduler (requires 'schedule' package).",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=24,
        help="Refresh interval in hours (default: 24). Only used with --daemon.",
    )
    args = parser.parse_args()

    if args.daemon:
        run_daemon(interval_hours=args.interval)
    else:
        summary = run_refresh(dry_run=args.dry_run)
        print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
