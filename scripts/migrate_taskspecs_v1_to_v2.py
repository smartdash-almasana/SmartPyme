#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[1]
TASK_DIR = ROOT / "factory" / "ai_governance" / "tasks"
SCHEMA_PATH = ROOT / "factory" / "ai_governance" / "schemas" / "taskspec.schema.json"
TASK_ID_RE = re.compile(r"^TASK-[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{3}$")
SAFE_PATH_RE = re.compile(r"^[a-zA-Z0-9_./-]+$")
VALID_STATUSES = {
    "PENDING",
    "ASSIGNED",
    "BUILDING",
    "WAITING_AUDIT",
    "AUDITING",
    "AUDIT_PASSED",
    "AUDIT_REJECTED",
    "AUDIT_BLOCKED",
    "BACK_TO_BUILD",
    "ESCALATED",
    "AWAITING_HUMAN_MERGE",
    "MERGED",
    "CLOSED",
    "ABANDONED",
    "CANCELLED",
}
STATUS_ALIASES = {
    "DONE": "CLOSED",
    "VALIDADO": "AUDIT_PASSED",
    "CORRECTO": "AUDIT_PASSED",
    "NO_VALIDADO": "AUDIT_REJECTED",
    "BLOCKED": "ESCALATED",
    "IN_PROGRESS": "BUILDING",
    "INPROGRESS": "BUILDING",
    "OPEN": "PENDING",
}


def git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError("YAML root must be object")
    return data


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def replace_tenant(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            ("cliente_id" if k == "tenant_id" else k): replace_tenant(v) for k, v in value.items()
        }
    if isinstance(value, list):
        return [replace_tenant(v) for v in value]
    if isinstance(value, str):
        return value.replace("tenant_id", "cliente_id")
    return value


def normalize_status(value: Any) -> str:
    status = str(value or "PENDING").upper()
    status = STATUS_ALIASES.get(status, status)
    return status if status in VALID_STATUSES else "PENDING"


def safe_allowed(paths: Any, fallback: str) -> list[str]:
    cleaned = []
    for raw in as_list(paths):
        item = str(raw).strip()
        if item and SAFE_PATH_RE.match(item):
            cleaned.append(item)
    return cleaned or [fallback]


def safe_forbidden(paths: Any) -> list[str]:
    return [str(raw).strip() for raw in as_list(paths) if str(raw).strip()]


def command_items(value: Any) -> list[dict[str, Any]]:
    out = []
    for item in as_list(value):
        if isinstance(item, dict):
            cmd = str(item.get("command") or "true")
            desc = str(item.get("description") or cmd)
            code = int(item.get("expected_exit_code", 0))
        else:
            cmd = "true"
            desc = str(item)
            code = 0
        out.append({"command": cmd, "description": desc, "expected_exit_code": code})
    return out


def acceptance_items(value: Any) -> list[dict[str, Any]]:
    raw = as_list(value) or ["TaskSpec legacy migrada a contrato v2.0.0"]
    out = []
    for item in raw:
        if isinstance(item, dict):
            desc = str(
                item.get("description") or item.get("criterion") or "Criterio legacy migrado"
            )
            cmd = str(item.get("verification_command") or "true")
            pattern = str(item.get("expected_output_pattern") or ".*")
            required = [str(x) for x in as_list(item.get("required_files"))]
        else:
            desc = str(item)
            cmd = "true"
            pattern = ".*"
            required = []
        if len(desc) < 10:
            desc = f"{desc} — criterio legacy migrado"
        out.append(
            {
                "description": desc,
                "verification_command": cmd,
                "expected_output_pattern": pattern,
                "required_files": required,
            }
        )
    return out


def migrate_one(path: Path, seq: int, head_sha: str) -> dict[str, Any]:
    original = replace_tenant(load_yaml(path))
    old_id = str(original.get("task_id") or original.get("id") or original.get("name") or path.stem)
    task_id = old_id if TASK_ID_RE.match(old_id) else f"TASK-2026-04-28-{seq:03d}"
    runtime = original.get("runtime") if isinstance(original.get("runtime"), dict) else {}
    context = original.get("context") if isinstance(original.get("context"), dict) else {}
    commands = original.get("commands") if isinstance(original.get("commands"), dict) else {}
    gate = original.get("gate") if isinstance(original.get("gate"), dict) else {}
    agent = str(runtime.get("target_agent") or "codex")
    if agent not in {"codex", "gemini", "gpt_director"}:
        agent = "codex"
    priority = str(original.get("priority") or "P2")
    if priority not in {"P0", "P1", "P2", "P3"}:
        priority = "P2"
    created_by = str(original.get("created_by") or "gpt_director")
    if created_by not in {"human_owner", "gpt_director", "hermes_gateway"}:
        created_by = "gpt_director"
    title = str(original.get("title") or original.get("name") or path.stem)
    title = title[:200] if len(title) >= 5 else f"Task {path.stem}"
    base_commit = str(context.get("base_commit") or "")
    if not re.match(r"^[a-f0-9]{7,40}$", base_commit):
        base_commit = head_sha
    return {
        "taskspec_version": "2.0.0",
        "task_id": task_id,
        "title": title,
        "created_at": str(original.get("created_at") or datetime.now(timezone.utc).isoformat()),
        "created_by": created_by,
        "priority": priority,
        "cliente_id": str(original.get("cliente_id") or "smartpyme-core"),
        "runtime": {
            "target_skill": str(runtime.get("target_skill") or "factory_bounded_builder"),
            "target_agent": agent,
            "max_retries": int(runtime.get("max_retries", 3)),
            "timeout_minutes": int(runtime.get("timeout_minutes", 45)),
        },
        "context": {
            "repo_ref": str(context.get("repo_ref") or "main"),
            "base_commit": base_commit,
            "canonical_docs": [str(x) for x in as_list(context.get("canonical_docs"))],
        },
        "scope": {
            "allowed_files": safe_allowed(
                original.get("allowed_files"), f"factory/ai_governance/tasks/{path.name}"
            ),
            "forbidden_files": safe_forbidden(original.get("forbidden_files")),
        },
        "commands": {
            "preflight": command_items(
                commands.get("preflight") or original.get("preflight_commands")
            ),
            "post": command_items(commands.get("post") or original.get("post_commands")),
        },
        "acceptance_criteria": acceptance_items(
            original.get("acceptance_criteria")
            or original.get("criterios_aceptacion")
            or original.get("validation")
        ),
        "gate": {
            "required_audit": bool(gate.get("required_audit", True)),
            "auto_merge": bool(gate.get("auto_merge", False)),
        },
        "status": normalize_status(original.get("status")),
        "retry_count": int(original.get("retry_count") or 0),
        "evidence_path": str(original.get("evidence_path") or ""),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    allowed_schema_keys = set(schema["properties"].keys())
    files = sorted(TASK_DIR.glob("*.yaml"))
    head_sha = git_head()
    print(f"Found {len(files)} TaskSpec files.")
    print(f"base_commit={head_sha}")
    valid = 0
    errors = 0
    for seq, path in enumerate(files, start=1):
        try:
            migrated = migrate_one(path, seq, head_sha)
            extra = set(migrated.keys()) - allowed_schema_keys
            if extra:
                raise ValueError(f"extra keys not allowed by schema: {sorted(extra)}")
            validate(instance=migrated, schema=schema)
            valid += 1
            print(f"  ✓ {path.name} -> {migrated['task_id']}")
            if args.execute:
                backup = path.with_suffix(path.suffix + ".v1.bak")
                if not backup.exists():
                    backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
                path.write_text(
                    yaml.safe_dump(migrated, sort_keys=False, allow_unicode=True), encoding="utf-8"
                )
        except Exception as exc:
            errors += 1
            print(f"  ✗ {path.name}: {exc}")
    print(f"\nSummary: {valid} valid, {errors} errors")
    if not args.execute:
        print("This was a dry run. Use --execute to apply changes.")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
