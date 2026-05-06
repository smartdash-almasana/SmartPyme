#!/usr/bin/env python3
"""Configure Hermes Agent for SmartPyme Factory.

Local/idempotent script for the VM.

Purpose:
- keep Hermes pointed at the SmartPyme repo;
- load SmartPyme skills from the versioned repo directory;
- reduce long-running/loop-prone behavior;
- keep model/runtime settings explicit for the current Gemini stage.

This script edits only ~/.hermes/config.yaml and creates a timestamped backup.
It does not touch SmartPyme product code.
"""

from __future__ import annotations

import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

SKILL_RELATIVE_DIR = Path("factory/ai_governance/skills")
SKILL_NAME = "hermes_smartpyme_factory"
EXPECTED_MODEL = "google/gemini-2.5-pro"
EXPECTED_PROVIDER = "google"
EXPECTED_BASE_URL = (
    "https://us-central1-aiplatform.googleapis.com/v1/"
    "projects/smartseller-490511/locations/us-central1/"
    "publishers/google/models/gemini-2.5-pro:generateContent"
)

# Keep this conservative. The local observed config uses `hermes-cli`.
REQUIRED_TOOLSETS = ["hermes-cli"]


def _ensure_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _append_unique(items: list[Any], value: str) -> None:
    if value not in items:
        items.append(value)


def _set_runtime_discipline(config: dict[str, Any]) -> None:
    """Set short-cycle defaults for Hermes operation."""

    model = config.setdefault("model", {})
    model["default"] = EXPECTED_MODEL
    model["provider"] = EXPECTED_PROVIDER
    model["base_url"] = EXPECTED_BASE_URL
    model["api_mode"] = "chat_completions"
    model["context_length"] = int(model.get("context_length") or 128000)

    providers = config.setdefault("providers", {})
    google = providers.setdefault("google", {})
    google["request_timeout_seconds"] = 120
    google["stale_timeout_seconds"] = 300
    google_models = google.setdefault("models", {})
    gemini = google_models.setdefault(EXPECTED_MODEL, {})
    gemini["timeout_seconds"] = 120
    gemini["stale_timeout_seconds"] = 300
    gemini["base_url"] = EXPECTED_BASE_URL

    # No automatic fallback during critical factory cycles; model mismatch must be visible.
    config["fallback_providers"] = []

    agent = config.setdefault("agent", {})
    agent["max_turns"] = 18
    agent["gateway_timeout"] = 600
    agent["restart_drain_timeout"] = 60
    agent["api_max_retries"] = 1
    agent["gateway_timeout_warning"] = 180
    agent["gateway_notify_interval"] = 60
    agent["reasoning_effort"] = "medium"

    display = config.setdefault("display", {})
    display["streaming"] = True
    display["interim_assistant_messages"] = False
    display["personality"] = "default"
    display["final_response_markdown"] = "strip"

    compression = config.setdefault("compression", {})
    compression["enabled"] = True
    compression["protect_last_n"] = 20

    memory = config.setdefault("memory", {})
    # Keep memory available but small; prompts still forbid session_search unless explicit.
    memory["memory_enabled"] = bool(memory.get("memory_enabled", True))
    memory["user_profile_enabled"] = bool(memory.get("user_profile_enabled", True))


def _configure_skills(config: dict[str, Any], skill_dir_text: str) -> None:
    """Support both known Hermes config shapes.

    Historical SmartPyme docs mention `skills.external_dirs`.
    The versioned Hermes template mentions `hermes.skills.search_paths`.
    To remove drift, we write both keys idempotently.
    """

    skills = config.setdefault("skills", {})
    external_dirs = _ensure_list(skills.get("external_dirs"))
    _append_unique(external_dirs, skill_dir_text)
    skills["external_dirs"] = external_dirs

    search_paths = _ensure_list(skills.get("search_paths"))
    _append_unique(search_paths, skill_dir_text)
    skills["search_paths"] = search_paths

    hermes = config.setdefault("hermes", {})
    hermes_skills = hermes.setdefault("skills", {})
    hermes_search_paths = _ensure_list(hermes_skills.get("search_paths"))
    _append_unique(hermes_search_paths, skill_dir_text)
    hermes_skills["search_paths"] = hermes_search_paths


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
        print("Run Hermes setup first.")
        return 4

    backup_path = config_path.with_suffix(
        config_path.suffix + ".bak." + datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    )
    shutil.copy2(config_path, backup_path)

    with config_path.open("r", encoding="utf-8") as fh:
        config = yaml.safe_load(fh) or {}

    _set_runtime_discipline(config)
    _configure_skills(config, str(skill_dir))

    existing_toolsets = _ensure_list(config.get("toolsets"))
    for toolset in REQUIRED_TOOLSETS:
        _append_unique(existing_toolsets, toolset)
    config["toolsets"] = existing_toolsets

    terminal = config.setdefault("terminal", {})
    terminal["cwd"] = str(repo_root)
    terminal["timeout"] = 300
    terminal["persistent_shell"] = True

    with config_path.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(config, fh, sort_keys=False, allow_unicode=True)

    print("OK_HERMES_SMARTPYME_CONFIGURED")
    print(f"repo_root={repo_root}")
    print(f"skill_dir={skill_dir}")
    print(f"skill_file={skill_file}")
    print(f"config={config_path}")
    print(f"backup={backup_path}")
    print(f"model={config['model']['default']}")
    print(f"provider={config['model']['provider']}")
    print(f"max_turns={config['agent']['max_turns']}")
    print(f"gateway_timeout={config['agent']['gateway_timeout']}")
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
