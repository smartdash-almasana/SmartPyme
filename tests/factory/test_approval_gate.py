from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from factory.contracts.sandbox import SandboxExecutionResult
from factory.core.queue_runner import run_one_sovereign_task
from factory.core.task_spec import TaskSpec, TaskSpecStatus
from factory.core.task_spec_store import TaskSpecStore


@pytest.fixture
def task_store(tmp_path: Path) -> TaskSpecStore:
    return TaskSpecStore(tmp_path / "taskspecs")


@pytest.fixture
def evidence_dir(tmp_path: Path) -> Path:
    return tmp_path / "evidence"


def _gate_path(tmp_path: Path) -> Path:
    gate_path = tmp_path / "AUDIT_GATE.md"
    gate_path.write_text("status: OPEN\n", encoding="utf-8")
    return gate_path


def _approval_command() -> str:
    return "git " + "push origin main"


def _task(task_id: str, command: str) -> TaskSpec:
    return TaskSpec(
        task_id=task_id,
        title=f"Task {task_id}",
        objective="Validate approval gate behavior",
        allowed_paths=["."],
        forbidden_paths=[],
        acceptance_criteria=["approval gate works"],
        validation_commands=[command],
        metadata={"operational_mode": "test"},
    )


def test_dangerous_command_moves_to_waiting_for_approval_without_docker_execution(
    task_store: TaskSpecStore,
    evidence_dir: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    docker_executor = MagicMock()
    monkeypatch.setattr("factory.core.queue_runner.DockerExecutor", lambda: docker_executor)

    command = _approval_command()
    task_store.enqueue(_task("TASK_APPROVAL", command))

    result = run_one_sovereign_task(
        tasks_dir=task_store.root_dir,
        evidence_dir=evidence_dir,
        gate_path=_gate_path(tmp_path),
    )

    assert result["status"] == TaskSpecStatus.WAITING_FOR_APPROVAL.value
    assert result["task_id"] == "TASK_APPROVAL"
    assert "COMMAND_REQUIRES_APPROVAL" in result["blocking_reason"]
    assert command in result["blocking_reason"]
    docker_executor.execute.assert_not_called()

    final_task = task_store.get("TASK_APPROVAL")
    assert final_task is not None
    assert final_task.status == TaskSpecStatus.WAITING_FOR_APPROVAL
    assert final_task.blocking_reason is not None
    assert "COMMAND_REQUIRES_APPROVAL" in final_task.blocking_reason


def test_safe_command_continues_to_normal_docker_execution(
    task_store: TaskSpecStore,
    evidence_dir: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    docker_executor = MagicMock()
    docker_executor.execute.return_value = SandboxExecutionResult(
        task_id="TASK_SAFE_APPROVAL_GATE",
        command="python -c \"print('ok')\"",
        returncode=0,
        stdout="ok\n",
        stderr="",
        blocked=False,
        requires_human_approval=False,
        reasons=[],
    )
    monkeypatch.setattr("factory.core.queue_runner.DockerExecutor", lambda: docker_executor)
    monkeypatch.setattr("factory.core.queue_runner._git_changed_paths", lambda repo_root: [])

    task_store.enqueue(_task("TASK_SAFE_APPROVAL_GATE", "python -c \"print('ok')\""))

    result = run_one_sovereign_task(
        tasks_dir=task_store.root_dir,
        evidence_dir=evidence_dir,
        gate_path=_gate_path(tmp_path),
    )

    assert result["status"] == TaskSpecStatus.DONE.value
    assert result["blocking_reason"] is None
    docker_executor.execute.assert_called_once()

    final_task = task_store.get("TASK_SAFE_APPROVAL_GATE")
    assert final_task is not None
    assert final_task.status == TaskSpecStatus.DONE


def test_store_lists_waiting_for_approval_tasks(task_store: TaskSpecStore) -> None:
    task_store.enqueue(_task("TASK_STORE_APPROVAL", _approval_command()))

    moved = task_store.mark_waiting_for_approval(
        "TASK_STORE_APPROVAL",
        "COMMAND_REQUIRES_APPROVAL",
    )

    assert moved.status == TaskSpecStatus.WAITING_FOR_APPROVAL
    waiting = task_store.list(TaskSpecStatus.WAITING_FOR_APPROVAL)
    assert [task.task_id for task in waiting] == ["TASK_STORE_APPROVAL"]
    assert task_store.counts()[TaskSpecStatus.WAITING_FOR_APPROVAL.value] == 1
