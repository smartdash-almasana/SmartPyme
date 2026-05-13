from __future__ import annotations

import os
from datetime import UTC, datetime
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
SOUL_PATH = PRODUCT_HOME / "SOUL.md"
SOUL_SOURCE_PATH = SMARTPYME_REPO / "infra" / "hermes-product" / "SOUL.md"


def _backup(path: Path) -> None:
    if not path.exists():
        return
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    backup_path = path.with_name(f"{path.name}.backup-{stamp}")
    path.replace(backup_path)


def main() -> None:
    PRODUCT_HOME.mkdir(parents=True, exist_ok=True)
    for child in ("logs", "sessions", "cron", "memories", "cache/documents"):
        (PRODUCT_HOME / child).mkdir(parents=True, exist_ok=True)

    config = yaml.safe_load(OVERLAY_PATH.read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        raise RuntimeError(f"invalid product config: {OVERLAY_PATH}")

    _backup(CONFIG_PATH)
    CONFIG_PATH.write_text(
        yaml.safe_dump(config, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )

    if SOUL_SOURCE_PATH.exists():
        _backup(SOUL_PATH)
        SOUL_PATH.write_text(SOUL_SOURCE_PATH.read_text(encoding="utf-8"), encoding="utf-8")

    print(f"Wrote clean config: {CONFIG_PATH}")
    print(f"Wrote product soul: {SOUL_PATH}")


if __name__ == "__main__":
    main()
