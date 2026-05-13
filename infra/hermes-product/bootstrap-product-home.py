from __future__ import annotations

import os
from pathlib import Path

import yaml

SMARTPYME_REPO = Path(
    os.getenv("SMARTPYME_REPO", "/opt/smartpyme-factory/repos/SmartPyme")
)
PRODUCT_HOME = Path(
    os.getenv("HERMES_PRODUCT_HOME", "/home/neoalmasana/.hermes-smartpyme-product")
)
OVERLAY_PATH = SMARTPYME_REPO / "infra" / "hermes-product" / "product-config-overlay.yaml"
CONFIG_PATH = PRODUCT_HOME / "config.yaml"


def deep_merge(base: dict, overlay: dict) -> dict:
    result = dict(base)
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def main() -> None:
    PRODUCT_HOME.mkdir(parents=True, exist_ok=True)
    for child in ("logs", "sessions", "cron", "memories", "cache/documents"):
        (PRODUCT_HOME / child).mkdir(parents=True, exist_ok=True)

    base = {}
    if CONFIG_PATH.exists():
        loaded = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            base = loaded

    overlay = yaml.safe_load(OVERLAY_PATH.read_text(encoding="utf-8"))
    if not isinstance(overlay, dict):
        raise RuntimeError(f"invalid overlay: {OVERLAY_PATH}")

    merged = deep_merge(base, overlay)
    CONFIG_PATH.write_text(
        yaml.safe_dump(merged, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    print(f"Wrote {CONFIG_PATH}")


if __name__ == "__main__":
    main()
