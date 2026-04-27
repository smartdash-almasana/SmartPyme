#!/usr/bin/env python3
"""Run one or many Hermes SmartPyme Factory cycles.

This runner does not implement the factory logic itself. It is only a safe
launcher for Hermes Agent using the official non-interactive CLI:

    hermes chat -s hermes_smartpyme_factory -q "..."

Hermes remains the orchestrator. The repo remains the source of truth.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


SKILL = "hermes_smartpyme_factory"
DEFAULT_INTERVAL_SECONDS = 900
VALID_REPO_SUFFIXES = ("smartpyme-factory/repos/SmartPyme", "actions-runner/_work/SmartPyme/SmartPyme")


PROMPT = """Ejecuta un ciclo SmartPyme Factory.

Reglas obligatorias:
- usar el skill hermes_smartpyme_factory
- operar solo desde el workspace actual
- un solo hallazgo o roadmap por ciclo
- maximo tres agentes: Architect, Builder, Auditor
- si no hay pending ni roadmap activo, responder idle
- guardar evidencia en factory/evidence
- usar git diff, git status y validaciones del hallazgo
- si se toca Python, ejecutar pytest especifico y ruff check sobre alcance tocado
- cerrar en done o blocked solamente con evidencia
- hacer commit y push solo si el cierre es consistente

Salida final requerida:
VEREDICTO_CICLO
HALLAZGO_O_ROADMAP
EVIDENCIA
TESTS
COMMIT
PUSH
RIESGOS
"""


def run(cmd: list[str], cwd: Path, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
        check=False,
    )


def ensure_repo(repo: Path) -> None:
    if not repo.exists():
        raise SystemExit(f"BLOCKED_REPO_NOT_FOUND: {repo}")
    if not (repo / ".git").exists():
        raise SystemExit(f"BLOCKED_NOT_GIT_REPO: {repo}")
    if not any(suffix in str(repo) for suffix in VALID_REPO_SUFFIXES):
        raise SystemExit(f"BLOCKED_UNEXPECTED_REPO_PATH: {repo}")


def ensure_hermes() -> str:
    hermes = os.environ.get("HERMES_BIN") or "hermes"
    probe = subprocess.run([hermes, "--version"], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if probe.returncode != 0:
        raise SystemExit("BLOCKED_HERMES_NOT_AVAILABLE")
    return hermes


def write_run_log(repo: Path, payload: dict) -> Path:
    log_dir = repo / "factory" / "runner_logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = log_dir / f"hermes_factory_runner_{ts}.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def one_cycle(repo: Path, hermes: str, timeout: int) -> int:
    started = datetime.now(timezone.utc).isoformat()
    pre = run(["git", "status", "--short"], cwd=repo, timeout=60)
    if pre.returncode != 0:
        print(pre.stdout)
        return pre.returncode

    pull = run(["git", "pull", "--rebase", "origin", "main"], cwd=repo, timeout=180)
    print(pull.stdout)
    if pull.returncode != 0:
        payload = {
            "status": "blocked",
            "reason": "git_pull_failed",
            "started_at": started,
            "output": pull.stdout,
        }
        log_path = write_run_log(repo, payload)
        print(f"RUNNER_LOG={log_path}")
        return pull.returncode

    cmd = [
        hermes,
        "chat",
        "--quiet",
                "--toolsets",
        "terminal,file,skills,delegation,todo",
        "--query",
        PROMPT,
    ]
    result = run(cmd, cwd=repo, timeout=timeout)
    print(result.stdout)

    payload = {
        "status": "ok" if result.returncode == 0 else "blocked",
        "returncode": result.returncode,
        "started_at": started,
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "hermes_output": result.stdout,
    }
    log_path = write_run_log(repo, payload)
    print(f"RUNNER_LOG={log_path}")
    return result.returncode


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default="~/smartpyme-factory/repos/SmartPyme")
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--loop", action="store_true")
    parser.add_argument("--interval", type=int, default=DEFAULT_INTERVAL_SECONDS)
    parser.add_argument("--timeout", type=int, default=3600)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo = Path(args.repo).expanduser().resolve()
    ensure_repo(repo)
    hermes = ensure_hermes()

    if not args.loop:
        return one_cycle(repo, hermes, args.timeout)

    while True:
        code = one_cycle(repo, hermes, args.timeout)
        print(f"CYCLE_EXIT={code}")
        sys.stdout.flush()
        time.sleep(args.interval)


if __name__ == "__main__":
    raise SystemExit(main())
