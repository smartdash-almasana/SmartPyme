from __future__ import annotations

import os
from pathlib import Path


# Keep pytest temp artifacts in a stable local folder and avoid accidental
# collection inside transient tmp trees under tests/.
pytest_plugins: list[str] = []
collect_ignore_glob = [
    "tests/tmp/*",
]


def pytest_configure(config) -> None:  # type: ignore[no-untyped-def]
    preferred_root = Path(".tmp/pytest_local").resolve()
    fallback_root = Path(".tmp/pytest_local2").resolve()
    root = preferred_root
    try:
        (preferred_root / ".write_check").mkdir(parents=True, exist_ok=True)
        os.rmdir(preferred_root / ".write_check")
    except OSError:
        root = fallback_root

    basetemp = root / f"run_{os.getpid()}"
    basetemp.mkdir(parents=True, exist_ok=True)
    config.option.basetemp = str(basetemp)
