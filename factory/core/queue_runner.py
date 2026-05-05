from __future__ import annotations

import json
import shlex
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from factory.core.task_loop import (
    MultiagentTask,
    load_task,
    run_persisted_multiagent_task_cycle,
    save_task,
)
from factory.core.task_spec import TaskSpec, validate_changed_paths
from factory.core.task_spec_store import TaskSpecStore

BUSINESS_TASK_TYPES: set[str] = set()
ALLOWED_GATE_STATUSES = {"OPEN", "APPROVED", "RUN"}
WAITING_AUDIT_STATUS = "WAITING_AUDIT"
EVIDENCE_MANIFEST_FILENAME = "evidence_manifest.json"
MINIMUM_EVIDENCE_FILES = (
    "cycle.md",
    "commands.txt",
    "git_status.txt",
    "git_diff.patch",
    "tests.txt",
    "decision.txt",
)


def list_task_ids(tasks_dir: str | Path) -> list[str]:
    directory = Path(tasks_dir)
    if not directory.exists():
        return []
    return sorted(path.stem for path in directory.glob("*.json"))


def find_next_pending_task(tasks_dir: str | Path) -> MultiagentTask | None:
    for task_id in list_task_ids(tasks_dir):
        task = load_task(task_id, tasks_dir)
        if task is not None and task.status == "pending":
            return task
    return None


def run_one_queued_task(
    tasks_dir: str | Path,
    evidence_dir: str | Path,
    *,
    use_sovereign: bool = False,
    gate_path: str | Path = Path("factory/control/AUDIT_GATE.md"),
    repo_root: str | Path = Path("."),
) -> dict:
    if use_sovereign:
        return run_one_sovereign_task(
            tasks_dir=tasks_dir,
            evidence_dir=evidence_dir,
            gate_path=gate_path,
            repo_root=repo_root,
        )

    task = find_next_pending_task(tasks_dir)
    if task is None:
        return {
            "status": "idle",
            "task_id": None,
            "reason": "NO_PENDING_TASK",
        }

    if task.task_type in BUSINESS_TASK_TYPES:
        return _block_product_runtime_task(task, tasks_dir, evidence_dir)

    result = run_persisted_multiagent_task_cycle(task.task_id, tasks_dir, evidence_dir)
    if result is None:
        return {
            "status": "blocked",
            "task_id": task.task_id,
            "reason": "TASK_LOAD_FAILED",
        }

    return {
        "status": result.status,
        "task_id": result.task_id,
        "report_path": result.report_path,
        "blocking_reason": result.blocking_reason,
    }


def run_one_sovereign_task(
    tasks_dir: str | Path,
    evidence_dir: str | Path,
    *,
    gate_path: str | Path = Path("factory/control/AUDIT_GATE.md"),
    repo_root: str | Path = Path("."),
) -> dict:
    gate_path = Path(gate_path)
    repo_root = Path(repo_root)
    gate_status = _read_gate_status(gate_path)
    if gate_status not in ALLOWED_GATE_STATUSES:
        return {
            "status": "blocked",
            "task_id": None,
            "reason": "AUDIT_GATE_CLOSED",
            "gate_status": gate_status,
        }

    store = TaskSpecStore(tasks_dir)
    pending_task = store.next_pending()
    if pending_task is None:
        return {
            "status": "idle",
            "task_id": None,
            "reason": "NO_PENDING_TASKSPEC",
            "gate_status": gate_status,
        }

    task = store.mark_in_progress(pending_task.task_id)
    task_evidence_dir = Path(evidence_dir) / task.task_id
    _create_minimum_evidence_files(task, task_evidence_dir, gate_status)

    blocking_reason: str | None = None
    command_results: list[dict[str, object]] = []

    operational_mode = task.metadata.get("operational_mode")
    if not operational_mode:
        blocking_reason = "BLOCKED_MODE_MISSING"
    else:
        command_results = _run_commands(_sovereign_commands(task), repo_root)
        blocking_reason = _first_command_failure(command_results)

    _write_command_evidence(task_evidence_dir, command_results)
    _write_git_evidence(task_evidence_dir, repo_root)

    if blocking_reason is None:
        path_validation = validate_changed_paths(task, _git_changed_paths(repo_root))
        if not path_validation.valid:
            blocking_reason = ";".join(path_validation.errors)

    evidence_paths = [str(task_evidence_dir / name) for name in MINIMUM_EVIDENCE_FILES]
    if blocking_reason is None:
        final_task = store.mark_done(task.task_id, evidence_paths=evidence_paths)
        final_status = final_task.status.value
    else:
        final_task = store.mark_blocked(task.task_id, blocking_reason=blocking_reason)
        final_status = final_task.status.value

    _write_decision_evidence(task_evidence_dir, final_status, blocking_reason)
    _write_cycle_evidence(task_evidence_dir, task, final_status, blocking_reason)
    _write_waiting_audit_gate(gate_path, task.task_id, final_status, blocking_reason)
    manifest_path = _write_evidence_manifest(
        task=task,
        task_evidence_dir=task_evidence_dir,
        branch=_current_branch(repo_root),
        commit_hash=_current_commit(repo_root),
        gate_status_after=WAITING_AUDIT_STATUS,
    )

    return {
        "status": final_status,
        "task_id": task.task_id,
        "evidence_dir": str(task_evidence_dir),
        "evidence_manifest_path": str(manifest_path),
        "evidence_paths": [*evidence_paths, str(manifest_path)],
        "blocking_reason": blocking_reason,
        "gate_status": WAITING_AUDIT_STATUS,
    }


def _block_product_runtime_task(
    task: MultiagentTask,
    tasks_dir: str | Path,
    evidence_dir: str | Path,
) -> dict:
    task.status = "blocked"
    task.blocking_reason = "PRODUCT_RUNTIME_TASK_NOT_ALLOWED_IN_FACTORY_CORE"
    task.audit = {"status": "blocked", "reason": task.blocking_reason}
    task.report_path = _write_block_report(task, Path(evidence_dir))
    save_task(task, tasks_dir)
    return {
        "status": task.status,
        "task_id": task.task_id,
        "report_path": task.report_path,
        "blocking_reason": task.blocking_reason,
    }


def _write_block_report(task: MultiagentTask, evidence_dir: Path) -> str:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    path = evidence_dir / f"{task.task_id}.txt"
    path.write_text(
        "\n".join(
            [
                f"task_id={task.task_id}",
                f"status={task.status}",
                f"task_type={task.task_type}",
                f"blocking_reason={task.blocking_reason}",
            ]
        ),
        encoding="utf-8",
    )
    return str(path)


def _read_gate_status(gate_path: Path) -> str:
    if not gate_path.exists():
        return "MISSING"
    for line in gate_path.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("status:"):
            return line.split(":", 1)[1].strip()
    return "UNKNOWN"


def _write_waiting_audit_gate(
    gate_path: Path,
    task_id: str,
    final_status: str,
    blocking_reason: str | None,
) -> None:
    gate_path.parent.mkdir(parents=True, exist_ok=True)
    reason = blocking_reason or f"task_{final_status}"
    gate_path.write_text(
        "\n".join(
            [
                "# AUDIT GATE",
                "",
                f"status: {WAITING_AUDIT_STATUS}",
                f"updated_at: {datetime.now(UTC).isoformat()}",
                "updated_by: sovereign_task_loop_v1",
                f"task_id: {task_id}",
                f"reason: {reason}",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _sovereign_commands(task: TaskSpec) -> list[str]:
    metadata = task.metadata or {}
    return [
        *list(metadata.get("preflight_commands") or []),
        *list(task.validation_commands),
        *list(metadata.get("post_commands") or []),
    ]


def _run_commands(commands: list[str], repo_root: Path) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    for command in commands:
        completed = subprocess.run(
            shlex.split(command),
            cwd=repo_root,
            text=True,
            capture_output=True,
            check=False,
        )
        results.append(
            {
                "command": command,
                "returncode": completed.returncode,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
            }
        )
        if completed.returncode != 0:
            break
    return results


def _first_command_failure(command_results: list[dict[str, object]]) -> str | None:
    for result in command_results:
        if result["returncode"] != 0:
            return f"COMMAND_FAILED: {result['command']}"
    return None


def _create_minimum_evidence_files(
    task: TaskSpec,
    task_evidence_dir: Path,
    gate_status: str,
) -> None:
    task_evidence_dir.mkdir(parents=True, exist_ok=True)
    for filename in MINIMUM_EVIDENCE_FILES:
        (task_evidence_dir / filename).write_text("", encoding="utf-8")
    _write_cycle_evidence(task_evidence_dir, task, "in_progress", None, gate_status)


def _write_cycle_evidence(
    task_evidence_dir: Path,
    task: TaskSpec,
    final_status: str,
    blocking_reason: str | None,
    gate_status: str | None = None,
) -> None:
    lines = [
        f"# Sovereign TaskLoop Cycle: {task.task_id}",
        "",
        f"task_id: {task.task_id}",
        f"title: {task.title}",
        f"status: {final_status}",
        f"operational_mode: {task.metadata.get('operational_mode')}",
        f"model_target: {task.metadata.get('model_target')}",
        f"gate_status_start: {gate_status or 'recorded_in_initial_cycle'}",
        f"blocking_reason: {blocking_reason or ''}",
    ]
    (task_evidence_dir / "cycle.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_command_evidence(
    task_evidence_dir: Path,
    command_results: list[dict[str, object]],
) -> None:
    command_lines: list[str] = []
    test_lines: list[str] = []
    for result in command_results:
        block = [
            f"$ {result['command']}",
            f"returncode={result['returncode']}",
            "stdout:",
            str(result["stdout"]),
            "stderr:",
            str(result["stderr"]),
            "---",
        ]
        command_lines.extend(block)
        test_lines.extend(block)
    (task_evidence_dir / "commands.txt").write_text(
        "\n".join(command_lines),
        encoding="utf-8",
    )
    (task_evidence_dir / "tests.txt").write_text(
        "\n".join(test_lines),
        encoding="utf-8",
    )


def _write_git_evidence(task_evidence_dir: Path, repo_root: Path) -> None:
    (task_evidence_dir / "git_status.txt").write_text(
        _run_git(["status", "--short"], repo_root),
        encoding="utf-8",
    )
    (task_evidence_dir / "git_diff.patch").write_text(
        _run_git(["diff"], repo_root),
        encoding="utf-8",
    )


def _write_decision_evidence(
    task_evidence_dir: Path,
    final_status: str,
    blocking_reason: str | None,
) -> None:
    (task_evidence_dir / "decision.txt").write_text(
        "\n".join(
            [
                f"status={final_status}",
                f"blocking_reason={blocking_reason or ''}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def _write_evidence_manifest(
    *,
    task: TaskSpec,
    task_evidence_dir: Path,
    branch: str,
    commit_hash: str,
    gate_status_after: str,
) -> Path:
    required_files = {
        "cycle": str(task_evidence_dir / "cycle.md"),
        "commands": str(task_evidence_dir / "commands.txt"),
        "git_status": str(task_evidence_dir / "git_status.txt"),
        "git_diff": str(task_evidence_dir / "git_diff.patch"),
        "tests": str(task_evidence_dir / "tests.txt"),
        "decision": str(task_evidence_dir / "decision.txt"),
    }
    manifest_path = task_evidence_dir / EVIDENCE_MANIFEST_FILENAME
    manifest = {
        "task_id": task.task_id,
        "evidence_dir": str(task_evidence_dir),
        "required_files": required_files,
        "commit_hash": commit_hash,
        "branch": branch,
        "gate_status_after": gate_status_after,
        "complete": all(Path(path).exists() for path in required_files.values()),
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest_path


def _run_git(args: list[str], repo_root: Path) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    return completed.stdout.strip() if completed.returncode == 0 else completed.stderr.strip()


def _git_changed_paths(repo_root: Path) -> list[str]:
    output = _run_git(["diff", "--name-only"], repo_root)
    return [line.strip() for line in output.splitlines() if line.strip()]


def _current_branch(repo_root: Path) -> str:
    return _run_git(["branch", "--show-current"], repo_root)


def _current_commit(repo_root: Path) -> str:
    return _run_git(["rev-parse", "--short", "HEAD"], repo_root)
