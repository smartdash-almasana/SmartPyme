#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Iterable

import yaml

TOKEN_RE = re.compile(r"\b\d{6,}:[A-Za-z0-9_-]{20,}\b")
KEY_RE = re.compile(r"(telegram|bot|token|gateway|platforms)", re.IGNORECASE)

SEARCH_FILES = [
    "~/.hermes/config.yaml",
    "~/.hermes/.env",
    "~/.hermes/auth.json",
    "~/.hermes/gateway_state.json",
    "~/.hermes/gateway.lock",
    "~/.bashrc",
    "~/.profile",
    "~/.bash_profile",
    "~/.zshrc",
]

SEARCH_DIRS = [
    "~/.config",
    "~/.local/share",
]

ENV_KEYS = [
    "TELEGRAM_BOT_TOKEN",
    "HERMES_TELEGRAM_TOKEN",
    "BOT_TOKEN",
    "TELEGRAM_TOKEN",
    "HERMES_CONFIG_PATH",
    "HERMES_HOME",
]


def main() -> int:
    hermes_home = Path(os.environ.get("HERMES_HOME", "~/.hermes")).expanduser()
    config_path = Path(
        os.environ.get("HERMES_CONFIG_PATH", str(hermes_home / "config.yaml"))
    ).expanduser()

    print("HERMES_TELEGRAM_TOKEN_SOURCE_AUDIT")
    print(f"hermes_home={hermes_home}")
    print(f"config_path={config_path}")
    print()

    _print_env_sources()
    print()
    _print_config_token_check(config_path)
    print()
    _print_file_hits(_iter_candidate_files())
    return 0


def _print_env_sources() -> None:
    print("=== ENV SOURCES ===")
    for key in ENV_KEYS:
        value = os.environ.get(key)
        print(f"{key}: present={bool(value)} masked={_mask(value)}")


def _print_config_token_check(config_path: Path) -> None:
    print("=== CONFIG TELEGRAM TOKEN CHECK ===")
    if not config_path.exists():
        print(f"missing_config={config_path}")
        return
    config = yaml.safe_load(config_path.read_text(encoding="utf-8", errors="replace")) or {}
    token = str(config.get("platforms", {}).get("telegram", {}).get("token") or "").strip()
    print(f"config_token_present={bool(token)}")
    print(f"config_token_masked={_mask(token)}")
    if not token:
        return
    try:
        data = json.loads(
            urllib.request.urlopen(f"https://api.telegram.org/bot{token}/getMe", timeout=20)
            .read()
            .decode()
        )
        print(f"telegram_getMe_ok={data.get('ok')}")
        print(f"telegram_username={data.get('result', {}).get('username')}")
        print(f"telegram_bot_id={data.get('result', {}).get('id')}")
    except urllib.error.HTTPError as exc:
        print("telegram_getMe_ok=False")
        print(f"telegram_http_status={exc.code}")
        print(f"telegram_error_body={exc.read().decode(errors='replace')}")
    except Exception as exc:  # noqa: BLE001
        print("telegram_getMe_ok=False")
        print(f"telegram_error={type(exc).__name__}: {exc}")


def _iter_candidate_files() -> Iterable[Path]:
    seen: set[Path] = set()
    for raw in SEARCH_FILES:
        path = Path(raw).expanduser()
        if path.exists() and path.is_file() and path not in seen:
            seen.add(path)
            yield path

    for raw_dir in SEARCH_DIRS:
        root = Path(raw_dir).expanduser()
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path in seen:
                continue
            name = path.name.lower()
            if any(
                part in name for part in ("env", "config", "telegram", "hermes", "gateway", "token")
            ):
                seen.add(path)
                yield path


def _print_file_hits(files: Iterable[Path]) -> None:
    print("=== FILE HITS MASKED ===")
    hit_count = 0
    for path in files:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        lines = text.splitlines()
        matching_lines = []
        token_hits = TOKEN_RE.findall(text)
        for index, line in enumerate(lines, start=1):
            if KEY_RE.search(line) or TOKEN_RE.search(line):
                matching_lines.append((index, _mask(line)))
        if token_hits or matching_lines:
            hit_count += 1
            print(f"--- {path} ---")
            if token_hits:
                unique = sorted({_mask(token) for token in token_hits})
                print("tokens_found_masked:")
                for token in unique:
                    print(f"  - {token}")
            for index, line in matching_lines[:60]:
                print(f"L{index}: {line}")
    print(f"files_with_hits={hit_count}")


def _mask(value: str | None) -> str:
    if not value:
        return ""

    def replace(match: re.Match[str]) -> str:
        token = match.group(0)
        prefix, _, secret = token.partition(":")
        tail = secret[-4:] if len(secret) >= 4 else ""
        return f"{prefix}:***{tail}"

    masked = TOKEN_RE.sub(replace, str(value))
    if len(masked) > 240:
        return masked[:240] + "..."
    return masked


if __name__ == "__main__":
    raise SystemExit(main())
