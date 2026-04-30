#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

import yaml


def main() -> int:
    repo = Path(os.environ.get("SMARTPYME_REPO", ".")).resolve()
    config = Path(os.environ.get("HERMES_CONFIG_PATH", "~/.hermes/config.yaml")).expanduser()

    expected_repo_markers = [
        repo / ".git",
        repo / "AGENTS.md",
        repo / "GEMINI.md",
        repo / "factory",
    ]
    missing_markers = [str(path) for path in expected_repo_markers if not path.exists()]
    if missing_markers:
        raise SystemExit("ERROR_NOT_SMARTPYME_REPO: missing " + ", ".join(missing_markers))
    if not config.exists():
        raise SystemExit(f"ERROR_MISSING_HERMES_CONFIG: {config}")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = config.with_name(f"{config.name}.bak.terminal-cwd-{stamp}")
    shutil.copy2(config, backup)

    data = yaml.safe_load(config.read_text(encoding="utf-8", errors="replace")) or {}
    if not isinstance(data, dict):
        raise SystemExit("ERROR_INVALID_HERMES_CONFIG")

    terminal = data.setdefault("terminal", {})
    if not isinstance(terminal, dict):
        raise SystemExit("ERROR_INVALID_TERMINAL_SECTION")

    previous_cwd = terminal.get("cwd")
    terminal["cwd"] = str(repo)

    # Keep backend as configured. For backend=local no Docker mount is required.
    # Do not modify docker_volumes or docker_mount_cwd_to_workspace here.
    config.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")

    print("HERMES_TERMINAL_REPO_CWD_OK")
    print(f"backup={backup}")
    print(f"previous_cwd={previous_cwd}")
    print(f"terminal.cwd={repo}")
    print(f"terminal.backend={terminal.get('backend')}")
    print(f"docker_mount_cwd_to_workspace={terminal.get('docker_mount_cwd_to_workspace')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
