#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

import yaml


def main() -> int:
    repo = Path(os.environ.get('SMARTPYME_REPO', '.')).resolve()
    config = Path(os.environ.get('HERMES_CONFIG_PATH', '~/.hermes/config.yaml')).expanduser()
    skills_dir = Path(os.environ.get('SMARTPYME_SKILLS_DIR', str(repo / 'factory/ai_governance/skills'))).resolve()
    expected = skills_dir / 'hermes_smartpyme_factory/SKILL.md'

    if not expected.exists():
        raise SystemExit(f'ERROR_MISSING_SKILL: {expected}')
    if not config.exists():
        raise SystemExit(f'ERROR_MISSING_HERMES_CONFIG: {config}')

    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup = config.with_name(f'{config.name}.bak.p0-4-{stamp}')
    shutil.copy2(config, backup)

    data = yaml.safe_load(config.read_text(encoding='utf-8', errors='replace')) or {}
    if not isinstance(data, dict):
        raise SystemExit('ERROR_INVALID_HERMES_CONFIG')

    skills = data.setdefault('skills', {})
    if not isinstance(skills, dict):
        raise SystemExit('ERROR_INVALID_SKILLS_SECTION')

    dirs = skills.setdefault('external_dirs', [])
    if dirs is None:
        dirs = []
        skills['external_dirs'] = dirs
    if not isinstance(dirs, list):
        raise SystemExit('ERROR_INVALID_EXTERNAL_DIRS')

    value = str(skills_dir)
    changed = value not in dirs
    if changed:
        dirs.append(value)

    config.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding='utf-8')
    print('HERMES_SKILLS_EXTERNAL_DIRS_OK')
    print(f'backup={backup}')
    print(f'external_dir={value}')
    print(f'changed={changed}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
