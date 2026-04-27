#!/usr/bin/env python3
"""Run a SmartPyme Codex Builder task through the real Codex CLI.

This adapter is intentionally small and fail-closed. It does not pretend that
Codex is an internal Python API. It invokes the supported local CLI:

    codex exec ...

Codex must be installed and authenticated on the machine where this script runs.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_TASK = "factory/tasks/template_codex_task.yaml"


def run(cmd: list[str], cwd: Path, timeout: int) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
        check=False,
    )


def ensure_codex() -> str:
    codex = shutil.which("codex")
    if not codex:
        raise SystemExit("BLOCKED_CODEX_CLI_NOT_FOUND: install with npm i -g @openai/codex and authenticate Codex")
    return codex


def ensure_repo(repo: Path) -> None:
    if not repo.exists():
        raise SystemExit(f"BLOCKED_REPO_NOT_FOUND: {repo}")
    if not (repo / ".git").exists():
        raise SystemExit(f"BLOCKED_NOT_GIT_REPO: {repo}")


def read_task(repo: Path, task_path: str) -> str:
    path = repo / task_path
    if not path.exists():
        raise SystemExit(f"BLOCKED_CODEX_TASK_NOT_FOUND: {task_path}")
    return path.read_text(encoding="utf-8")


def build_prompt(task: str) -> str:
    return f"""Actua como Codex Builder controlado para SmartPyme.

REGLAS OBLIGATORIAS:
- Cumpli CODEX.md y AGENTS.md.
- No inventes rutas, dependencias ni contratos.
- Opera solo dentro del repo actual.
- Ejecuta una unidad pequena.
- Si falta contexto, responde BLOCKED.
- Si modificas archivos, deja evidencia verificable.
- No hagas refactor global.

TAREA YAML:
{task}

SALIDA FINAL OBLIGATORIA:
VEREDICTO
ARCHIVOS_MODIFICADOS
VERIFICACION_FISICA
TESTS
EVIDENCIA
DIFF
BLOQUEOS
RIESGOS
"""


def write_evidence(repo: Path, task_path: str, command: list[str], output: str, returncode: int) -> Path:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    safe_task = Path(task_path).stem.replace(" ", "_")
    evidence_dir = repo / "factory" / "evidence" / f"codex_{safe_task}_{ts}"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "task_path": task_path,
        "returncode": returncode,
        "command": command,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    (evidence_dir / "codex_runner.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    (evidence_dir / "codex_output.txt").write_text(output, encoding="utf-8")
    return evidence_dir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--task", default=DEFAULT_TASK)
    parser.add_argument("--timeout", type=int, default=3600)
    parser.add_argument("--full-auto", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo = Path(args.repo).expanduser().resolve()
    ensure_repo(repo)
    codex = ensure_codex()
    task = read_task(repo, args.task)
    prompt = build_prompt(task)

    cmd = [codex, "exec"]
    if args.full_auto:
        cmd.append("--full-auto")
    if args.json:
        cmd.append("--json")
    cmd.append(prompt)

    result = run(cmd, cwd=repo, timeout=args.timeout)
    print(result.stdout)
    evidence_dir = write_evidence(repo, args.task, cmd[:-1] + ["<prompt>"], result.stdout, result.returncode)
    print(f"CODEX_EVIDENCE={evidence_dir}")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
