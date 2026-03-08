from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

# Define logs location relative to this file
OPS_DIR = Path(__file__).resolve().parent
LOG_FILE = OPS_DIR / "chat_events.jsonl"

def append_event_log(event: Dict[str, Any]) -> None:
    """
    Append a structured event to a JSONL file.
    Automatically adds a UTC timestamp.
    """
    try:
        # Ensure timestamp is present
        if "timestamp" not in event:
            event["timestamp"] = datetime.now(timezone.utc).isoformat()
        
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    except Exception as e:
        # Fallback to standard logging if file write fails
        logging.error(f"Failed to append to log file: {e}")
        logging.error(f"Event: {json.dumps(event)}")
