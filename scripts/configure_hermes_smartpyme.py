#!/usr/bin/env python3
"""Configure Hermes Agent for SmartPyme Factory.

This script is intentionally local/idempotent. It edits ~/.hermes/config.yaml
so Hermes discovers the SmartPyme Factory skill directly from this repository
using the official Hermes `skills.external_dirs` mechanism.
"""

from __future__ import annotations

import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import yaml

REQUIRED_TOOLSETS = ["terminal", "file", "skills", "delegation", "todo"]
SKILL_RELATIVE_DIR = Path("factory/ai_governance/skills")
SKILL_NAME = "hermes_smartpyme_factory"


def main() -> int:
    repo_root = Path.cwd().resolve()
    skill_dir = repo_root / SKILL_RELATIVE_DIR
    skill_file = skill_dir / SKILL_NAME / "SKILL.md"

    if not (repo_root / ".git").exists():
        print("BLOCKED_NOT_GIT_REPO")
        print(f"pwd={repo_root}")
        return 2

    if not skill_file.exists():
        print("BLOCKED_SKILL_NOT_FOUND")
        print(f"missing={skill_file}")
        return 3

    config_path = Path.home() / ".hermes" / "config.yaml"
    if not config_path.exists():
        print("BLOCKED_HERMES_CONFIG_NOT_FOUND")
        print("Run hermes doctor --fix first.")
        return 4

    backup_path = config_path.with_suffix(
        config_path.suffix + ".bak." + datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    )
    shutil.copy2(config_path, backup_path)

    with config_path.open("r", encoding="utf-8") as fh:
        config = yaml.safe_load(fh) or {}

    skills = config.setdefault("skills", {})
    external_dirs = skills.setdefault("external_dirs", [])
    skill_dir_text = str(skill_dir)
    if skill_dir_text not in external_dirs:
        external_dirs.append(skill_dir_text)

    existing_toolsets = config.get("toolsets")
    if not isinstance(existing_toolsets, list):
        existing_toolsets = []
    for toolset in REQUIRED_TOOLSETS:
        if toolset not in existing_toolsets:
            existing_toolsets.append(toolset)
    config["toolsets"] = existing_toolsets

    terminal = config.setdefault("terminal", {})
    terminal["cwd"] = str(repo_root)

    with config_path.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(config, fh, sort_keys=False, allow_unicode=True)

    print("OK_HERMES_SMARTPYME_CONFIGURED")
    print(f"repo_root={repo_root}")
    print(f"skill_dir={skill_dir}")
    print(f"skill_file={skill_file}")
    print(f"config={config_path}")
    print(f"backup={backup_path}")
    print("toolsets=" + ",".join(config["toolsets"]))

    hermes = shutil.which("hermes")
    if hermes:
        print("\nVERIFYING_HERMES_SKILL_DISCOVERY")
        result = subprocess.run(
            [hermes, "skills", "list"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=90,
            check=False,
        )
        print(result.stdout)
        if SKILL_NAME not in result.stdout and "smartpyme" not in result.stdout.lower():
            print("WARN_SKILL_NOT_VISIBLE_IN_LIST")
            return 5
    else:
        print("WARN_HERMES_COMMAND_NOT_FOUND")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
