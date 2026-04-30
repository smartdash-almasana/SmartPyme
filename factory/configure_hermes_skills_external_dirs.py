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

    smartpyme_skills_dir = Path(
        os.environ.get("SMARTPYME_SKILLS_DIR", str(repo / "factory/ai_governance/skills"))
    ).resolve()
    gemini_skills_dir = Path(
        os.environ.get("SMARTPYME_GEMINI_SKILLS_DIR", str(repo / ".gemini/skills"))
    ).resolve()

    required_files = [
        smartpyme_skills_dir / "hermes_smartpyme_factory/SKILL.md",
        smartpyme_skills_dir / "factory_bounded_builder/SKILL.md",
        smartpyme_skills_dir / "factory_auditor/SKILL.md",
        gemini_skills_dir / "lean_audit_vm_protocol.md",
        gemini_skills_dir / "write_verify_protocol.md",
    ]

    for required_file in required_files:
        if not required_file.exists():
            raise SystemExit(f"ERROR_MISSING_SKILL: {required_file}")
    if not config.exists():
        raise SystemExit(f"ERROR_MISSING_HERMES_CONFIG: {config}")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = config.with_name(f"{config.name}.bak.smartpyme-skills-{stamp}")
    shutil.copy2(config, backup)

    data = yaml.safe_load(config.read_text(encoding="utf-8", errors="replace")) or {}
    if not isinstance(data, dict):
        raise SystemExit("ERROR_INVALID_HERMES_CONFIG")

    skills = data.setdefault("skills", {})
    if not isinstance(skills, dict):
        raise SystemExit("ERROR_INVALID_SKILLS_SECTION")

    dirs = skills.setdefault("external_dirs", [])
    if dirs is None:
        dirs = []
        skills["external_dirs"] = dirs
    if not isinstance(dirs, list):
        raise SystemExit("ERROR_INVALID_EXTERNAL_DIRS")

    targets = [str(smartpyme_skills_dir), str(gemini_skills_dir)]
    changed = False
    for target in targets:
        if target not in dirs:
            dirs.append(target)
            changed = True

    config.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")

    print("HERMES_SKILLS_EXTERNAL_DIRS_OK")
    print(f"backup={backup}")
    print(f"changed={changed}")
    print("external_dirs:")
    for item in dirs:
        print(f"- {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
