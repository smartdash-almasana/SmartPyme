"""Heartbeat y watchdog mínimo para SmartPyme Factory v2.1."""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

DEFAULT_HEARTBEAT_PATH = Path("factory/control/heartbeat.json")


def write_heartbeat(path: str | Path = DEFAULT_HEARTBEAT_PATH, status: str = "healthy") -> dict[str, Any]:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "status": status,
    }
    target.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def read_heartbeat(path: str | Path = DEFAULT_HEARTBEAT_PATH) -> dict[str, Any] | None:
    target = Path(path)
    if not target.exists():
        return None
    return json.loads(target.read_text(encoding="utf-8"))


def is_stale(path: str | Path = DEFAULT_HEARTBEAT_PATH, max_age_seconds: int = 300) -> bool:
    payload = read_heartbeat(path)
    if not payload:
        return True
    timestamp = datetime.fromisoformat(payload["timestamp"])
    return datetime.now(timezone.utc) - timestamp > timedelta(seconds=max_age_seconds)
