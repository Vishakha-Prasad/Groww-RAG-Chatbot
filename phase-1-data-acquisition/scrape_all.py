from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

import requests

from parsers import parse_scheme_page
from schemes import SCHEMES, SchemeConfig

PROJECT_ROOT = Path(__file__).resolve().parent
RAW_DIR = PROJECT_ROOT / "raw"
OUT_DIR = PROJECT_ROOT / "out"


def fetch_html(cfg: SchemeConfig, timeout: float = 15.0) -> str:
    """
    Fetch the HTML for a given scheme configuration from Groww.

    Raises:
        requests.HTTPError on non-2xx responses.
    """
    response = requests.get(cfg.url, timeout=timeout)
    response.raise_for_status()
    return response.text


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def save_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def save_json(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def scrape_scheme(cfg: SchemeConfig) -> Optional[str]:
    """
    Fetch, parse and persist data for a single scheme.

    Returns:
        Path to the JSON output file as a string, or None if scraping failed.
    """
    try:
        html = fetch_html(cfg)
    except Exception as exc:  # noqa: BLE001
        print(f"[ERROR] Failed to fetch {cfg.url}: {exc}")
        return None

    # Save raw HTML for debugging.
    ensure_dir(RAW_DIR)
    raw_path = RAW_DIR / f"{cfg.id}.html"
    save_text(raw_path, html)

    snapshot = parse_scheme_page(html, cfg)

    ensure_dir(OUT_DIR)
    out_path = OUT_DIR / f"{cfg.id}.json"
    save_json(out_path, snapshot.to_dict())

    print(f"[OK] Scraped {cfg.name} -> {out_path}")
    return str(out_path)


def main() -> None:
    print("Starting Phase 1 scraping for HDFC schemes...")
    print(f"Output directory: {OUT_DIR}")
    print()

    for cfg in SCHEMES:
        scrape_scheme(cfg)

    print("\nDone.")


if __name__ == "__main__":
    main()

