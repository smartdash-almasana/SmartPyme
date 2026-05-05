#!/usr/bin/env python3
"""Entrypoint mínimo para ejecutar un ciclo del TaskLoop soberano.

Este módulo proporciona una CLI simple que invoca run_one_queued_task()
con use_sovereign=True, respetando los paths por defecto del Factory.

Uso:

    python3 -m factory.core.run_taskloop_once --mode sovereign
    python3 -m factory.core.run_taskloop_once --mode multiagent

Verificación post-cierre:

    python3 -m factory.core.run_taskloop_once --check-remote-sync --compact

La salida es un objeto JSON compacto con el resultado del ciclo o de la
verificación remota.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from factory.core.queue_runner import run_one_queued_task

DONE_REMOTE_SYNCED = "DONE_REMOTE_SYNCED"
BLOCKED_REMOTE_SYNC = "BLOCKED_REMOTE_SYNC"


def _run_git(repo_root: Path, args: list[str]) -> tuple[int, str, str]:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    return completed.returncode, completed.stdout.strip(), completed.stderr.strip()


def check_remote_sync(repo_root: str | Path = ".", remote: str = "origin") -> dict[str, Any]:
    """Verifica que HEAD local exista en el remoto de la rama activa.

    Esta verificación es post-cierre. Debe ejecutarse después de commit/push.

    Regla operativa: un hito solo puede considerarse DONE real si:
    - el worktree está limpio;
    - hay rama local activa;
    - existe HEAD local;
    - el commit remoto de origin/<branch> coincide con HEAD local.
    """
    root = Path(repo_root)

    status_code, status_out, status_err = _run_git(root, ["status", "--short"])
    if status_code != 0:
        return {
            "remote_sync_status": BLOCKED_REMOTE_SYNC,
            "remote_sync_ok": False,
            "remote_sync_reason": f"GIT_STATUS_FAILED: {status_err}",
        }
    if status_out:
        return {
            "remote_sync_status": BLOCKED_REMOTE_SYNC,
            "remote_sync_ok": False,
            "remote_sync_reason": "DIRTY_WORKTREE",
            "git_status": status_out,
        }

    branch_code, branch, branch_err = _run_git(root, ["branch", "--show-current"])
    if branch_code != 0 or not branch:
        return {
            "remote_sync_status": BLOCKED_REMOTE_SYNC,
            "remote_sync_ok": False,
            "remote_sync_reason": f"BRANCH_UNAVAILABLE: {branch_err}",
        }

    head_code, head, head_err = _run_git(root, ["rev-parse", "HEAD"])
    if head_code != 0 or not head:
        return {
            "remote_sync_status": BLOCKED_REMOTE_SYNC,
            "remote_sync_ok": False,
            "remote_sync_reason": f"HEAD_UNAVAILABLE: {head_err}",
            "branch": branch,
        }

    remote_code, remote_head, remote_err = _run_git(
        root,
        ["ls-remote", remote, f"refs/heads/{branch}"],
    )
    if remote_code != 0:
        return {
            "remote_sync_status": BLOCKED_REMOTE_SYNC,
            "remote_sync_ok": False,
            "remote_sync_reason": f"LS_REMOTE_FAILED: {remote_err}",
            "branch": branch,
            "local_head": head,
        }

    remote_sha = remote_head.split()[0] if remote_head else ""
    if remote_sha != head:
        return {
            "remote_sync_status": BLOCKED_REMOTE_SYNC,
            "remote_sync_ok": False,
            "remote_sync_reason": "REMOTE_HEAD_MISMATCH",
            "branch": branch,
            "local_head": head,
            "remote_head": remote_sha,
        }

    return {
        "remote_sync_status": DONE_REMOTE_SYNCED,
        "remote_sync_ok": True,
        "remote_sync_reason": None,
        "branch": branch,
        "local_head": head,
        "remote_head": remote_sha,
    }


def _filtered_result(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": result.get("status"),
        "task_id": result.get("task_id"),
        "evidence_dir": result.get("evidence_dir"),
        "evidence_manifest_path": result.get("evidence_manifest_path"),
        "execution_result_path": result.get("execution_result_path"),
        "audit_decision_path": result.get("audit_decision_path"),
        "human_escalation_path": result.get("human_escalation_path"),
        "blocking_reason": result.get("blocking_reason") or result.get("reason"),
        "gate_status": result.get("gate_status"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="factory.core.run_taskloop_once",
        description="Ejecuta un ciclo del TaskLoop soberano de SmartPyme Factory.",
        epilog="Defaults: tasks_dir='factory/taskspecs', evidence_dir='factory/evidence/taskspecs', gate_path='factory/control/AUDIT_GATE.md'",
    )
    parser.add_argument(
        "--mode",
        choices=["sovereign", "multiagent"],
        default="sovereign",
        help="Tipo de runner a usar (default: sovereign)",
    )
    parser.add_argument(
        "--tasks-dir",
        default="factory/taskspecs",
        help="Directorio raíz de TaskSpecs (default: factory/taskspecs)",
    )
    parser.add_argument(
        "--evidence-dir",
        default="factory/evidence/taskspecs",
        help="Directorio base para evidencias (default: factory/evidence/taskspecs)",
    )
    parser.add_argument(
        "--gate-path",
        default="factory/control/AUDIT_GATE.md",
        help="Ruta al archivo de control AUDIT_GATE.md (default: factory/control/AUDIT_GATE.md)",
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Raíz del repositorio (default: directorio actual)",
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Salida JSON sin indentación (default: indentado)",
    )
    parser.add_argument(
        "--check-remote-sync",
        action="store_true",
        help="Verificación post-cierre: confirma que HEAD local coincide con origin/<branch>.",
    )

    args = parser.parse_args()
    indent = None if args.compact else 2

    if args.check_remote_sync:
        json.dump(check_remote_sync(args.repo_root), sys.stdout, ensure_ascii=False, indent=indent)
        sys.stdout.write("\n")
        return

    result = run_one_queued_task(
        tasks_dir=args.tasks_dir,
        evidence_dir=args.evidence_dir,
        use_sovereign=(args.mode == "sovereign"),
        gate_path=args.gate_path,
        repo_root=args.repo_root,
    )

    json.dump(_filtered_result(result), sys.stdout, ensure_ascii=False, indent=indent)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
