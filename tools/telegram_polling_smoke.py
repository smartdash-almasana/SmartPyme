from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any
from urllib import parse as urllib_parse
from urllib import request as urllib_request
from urllib.error import HTTPError, URLError

from app.adapters.telegram_adapter import TelegramAdapter


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run one-shot Telegram polling smoke for XLSX updates.")
    parser.add_argument("--offset", type=int, required=False, help="Optional Telegram getUpdates offset")
    parser.add_argument("--timeout", type=int, default=0, help="getUpdates timeout seconds (default: 0)")
    return parser


def _load_env_local(path: Path = Path(".env.local")) -> dict[str, str]:
    if not path.exists() or not path.is_file():
        return {}
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        raw = line.strip()
        if not raw or raw.startswith("#") or "=" not in raw:
            continue
        key, value = raw.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            values[key] = value
    return values


def _resolve_setting(cli_value: str | None, env_name: str, env_local: dict[str, str]) -> str:
    if isinstance(cli_value, str) and cli_value.strip():
        return cli_value.strip()
    env_value = os.getenv(env_name, "").strip()
    if env_value:
        return env_value
    local_value = env_local.get(env_name, "").strip()
    if local_value:
        return local_value
    return ""


def _safe_dict(data: dict[str, Any]) -> dict[str, Any]:
    blocked = ("token", "api_key", "secret", "password")
    out: dict[str, Any] = {}
    for k, v in data.items():
        key = str(k).lower()
        if any(b in key for b in blocked):
            continue
        out[k] = v
    return out


def _get_updates(token: str, offset: int | None, timeout: int) -> list[dict[str, Any]]:
    query: dict[str, Any] = {"timeout": timeout}
    if offset is not None:
        query["offset"] = offset
    qs = urllib_parse.urlencode(query)
    url = f"https://api.telegram.org/bot{token}/getUpdates?{qs}"
    try:
        with urllib_request.urlopen(url, timeout=20.0) as response:
            raw = response.read().decode("utf-8")
    except HTTPError as exc:
        raise RuntimeError(f"telegram getUpdates HTTP {exc.code}") from exc
    except URLError as exc:
        raise RuntimeError("telegram getUpdates network error") from exc

    payload = json.loads(raw)
    if not isinstance(payload, dict) or not payload.get("ok"):
        raise RuntimeError("telegram getUpdates failed")
    result = payload.get("result")
    if not isinstance(result, list):
        raise RuntimeError("telegram getUpdates invalid result")
    return [item for item in result if isinstance(item, dict)]


def _is_xlsx_update(update: dict[str, Any]) -> bool:
    message = update.get("message")
    if not isinstance(message, dict):
        return False
    document = message.get("document")
    if not isinstance(document, dict):
        return False
    file_name = document.get("file_name")
    return isinstance(file_name, str) and file_name.lower().endswith(".xlsx")


def run(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    env_local = _load_env_local()
    token = _resolve_setting(None, "TELEGRAM_BOT_TOKEN", env_local)
    if not token:
        print("TELEGRAM_BOT_TOKEN is required", file=sys.stderr)
        return 2

    try:
        updates = _get_updates(token=token, offset=args.offset, timeout=args.timeout)
    except (RuntimeError, ValueError, TypeError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    adapter = TelegramAdapter(telegram_bot_token=token)
    xlsx_updates = [u for u in updates if _is_xlsx_update(u)]
    processed = 0
    last_update_id: int | None = None

    for update in xlsx_updates:
        update_id = update.get("update_id")
        if isinstance(update_id, int):
            last_update_id = update_id
        result = adapter.handle_update(update)
        safe = _safe_dict(result if isinstance(result, dict) else {"status": "invalid_result"})
        message = update.get("message", {})
        document = message.get("document", {}) if isinstance(message, dict) else {}
        print(
            json.dumps(
                {
                    "update_id": update_id,
                    "file_name": document.get("file_name"),
                    "file_id": document.get("file_id"),
                    "adapter_status": safe.get("status"),
                    "adapter_message": safe.get("message"),
                },
                ensure_ascii=False,
            )
        )
        processed += 1

    summary: dict[str, Any] = {
        "updates_total": len(updates),
        "xlsx_updates": len(xlsx_updates),
        "processed": processed,
    }
    if last_update_id is not None:
        summary["next_offset"] = last_update_id + 1
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
