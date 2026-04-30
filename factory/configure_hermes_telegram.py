#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

import yaml


def main() -> int:
    config = Path(os.environ.get("HERMES_CONFIG_PATH", "~/.hermes/config.yaml")).expanduser()
    token_from_env = os.environ.get("HERMES_TELEGRAM_TOKEN", "").strip()

    if not config.exists():
        raise SystemExit(f"ERROR_MISSING_HERMES_CONFIG: {config}")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = config.with_name(f"{config.name}.bak.telegram-{stamp}")
    shutil.copy2(config, backup)

    data = yaml.safe_load(config.read_text(encoding="utf-8", errors="replace")) or {}
    if not isinstance(data, dict):
        raise SystemExit("ERROR_INVALID_HERMES_CONFIG")

    platforms = data.setdefault("platforms", {})
    if not isinstance(platforms, dict):
        raise SystemExit("ERROR_INVALID_PLATFORMS_SECTION")

    telegram = platforms.setdefault("telegram", {})
    if not isinstance(telegram, dict):
        raise SystemExit("ERROR_INVALID_TELEGRAM_SECTION")

    existing_token = str(telegram.get("token") or "").strip()
    token = token_from_env or existing_token
    if not token:
        raise SystemExit(
            "ERROR_MISSING_TELEGRAM_TOKEN: set HERMES_TELEGRAM_TOKEN or configure platforms.telegram.token"
        )

    extra = telegram.setdefault("extra", {})
    if extra is None:
        extra = {}
        telegram["extra"] = extra
    if not isinstance(extra, dict):
        raise SystemExit("ERROR_INVALID_TELEGRAM_EXTRA_SECTION")

    telegram["enabled"] = True
    telegram["token"] = token
    extra["polling"] = True

    data.setdefault("unauthorized_dm_behavior", "pair")

    config.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")

    print("HERMES_TELEGRAM_CONFIG_OK")
    print(f"backup={backup}")
    print("telegram.enabled=True")
    print("telegram.extra.polling=True")
    print(f"token_present={bool(token)}")
    print("token_printed=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
