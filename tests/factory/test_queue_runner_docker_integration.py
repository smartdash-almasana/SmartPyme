
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
    return TaskSpecStore(tmp_path)


@pytest.fixture
def evidence_dir(tmp_path: Path) -> Path:
    return tmp_path / "evidence"


def test_run_safe_command_with_docker(
    task_store: TaskSpecStore, evidence_dir: Path, monkeypatch
):
    # Mock DockerExecutor
    mock_docker_executor = MagicMock()
    mock_docker_executor.execute.return_value = SandboxExecutionResult(
        task_id="TASK_SAFE",
        command="ls -l",
        returncode=0,
        stdout="safe command output",
        stderr="",
        blocked=False,
    )
    monkeypatch.setattr(
        "factory.core.queue_runner.DockerExecutor", lambda: mock_docker_executor
    )
    monkeypatch.setattr("factory.core.queue_runner._git_changed_paths", lambda repo_root: [])

    # Create and enqueue a task
    task = TaskSpec(
        task_id="TASK_SAFE",
        title="Test safe command",
        objective="test",
        allowed_paths=["."],
        forbidden_paths=[],
        acceptance_criteria=["test"],
        validation_commands=["ls -l"],
        metadata={"operational_mode": "test"},
    )
    task_store.enqueue(task)

    # Create a dummy AUDIT_GATE file
    gate_path = task_store.root_dir.parent / "AUDIT_GATE.md"
    gate_path.write_text("status: OPEN")

    # Run the task
    result = run_one_sovereign_task(
        tasks_dir=task_store.root_dir,
        evidence_dir=evidence_dir,
        gate_path=gate_path,
    )

    # Assertions
    assert result["status"] == "done"
    assert result["task_id"] == "TASK_SAFE"
    assert result["blocking_reason"] is None

    final_task = task_store.get("TASK_SAFE")
    assert final_task is not None
    assert final_task.status == TaskSpecStatus.DONE

    mock_docker_executor.execute.assert_called_once()
    
def test_run_dangerous_command_blocked(
    task_store: TaskSpecStore, evidence_dir: Path, monkeypatch
):
    # Mock DockerExecutor to return blocked
    mock_docker_executor = MagicMock()
    mock_docker_executor.execute.return_value = SandboxExecutionResult(
        task_id="TASK_DANGEROUS",
        command="git push",
        returncode=126,
        stdout="",
        stderr="Command blocked by policy before Docker execution.",
        blocked=True,
        reasons=["DANGEROUS_COMMAND_PATTERN:^git\\s+push"],
    )
    monkeypatch.setattr(
        "factory.core.queue_runner.DockerExecutor", lambda: mock_docker_executor
    )
    monkeypatch.setattr("factory.core.queue_runner._git_changed_paths", lambda repo_root: [])

    task = TaskSpec(
        task_id="TASK_DANGEROUS",
        title="Test dangerous command",
        objective="test",
        allowed_paths=["."],
        forbidden_paths=[],
        acceptance_criteria=["test"],
        validation_commands=["git push"],
        metadata={"operational_mode": "test"},
    )
    task_store.enqueue(task)
    gate_path = task_store.root_dir.parent / "AUDIT_GATE.md"
    gate_path.write_text("status: OPEN")

    result = run_one_sovereign_task(
        tasks_dir=task_store.root_dir,
        evidence_dir=evidence_dir,
        gate_path=gate_path,
    )

    assert result["status"] == "blocked"
    assert result["task_id"] == "TASK_DANGEROUS"
    assert "COMMAND_BLOCKED" in result["blocking_reason"]
    assert "DANGEROUS_COMMAND_PATTERN" in result["blocking_reason"]

    final_task = task_store.get("TASK_DANGEROUS")
    assert final_task.status == TaskSpecStatus.BLOCKED


def test_run_command_failure(
    task_store: TaskSpecStore, evidence_dir: Path, monkeypatch
):
    mock_docker_executor = MagicMock()
    mock_docker_executor.execute.return_value = SandboxExecutionResult(
        task_id="TASK_FAIL",
        command="exit 1",
        returncode=1,
        stdout="",
        stderr="Error",
        blocked=False,
    )
    monkeypatch.setattr(
        "factory.core.queue_runner.DockerExecutor", lambda: mock_docker_executor
    )
    monkeypatch.setattr("factory.core.queue_runner._git_changed_paths", lambda repo_root: [])

    task = TaskSpec(
        task_id="TASK_FAIL",
        title="Test command failure",
        objective="test",
        allowed_paths=["."],
        forbidden_paths=[],
        acceptance_criteria=["test"],
        validation_commands=["exit 1"],
        metadata={"operational_mode": "test"},
    )
    task_store.enqueue(task)
    gate_path = task_store.root_dir.parent / "AUDIT_GATE.md"
    gate_path.write_text("status: OPEN")

    result = run_one_sovereign_task(
        tasks_dir=task_store.root_dir,
        evidence_dir=evidence_dir,
        gate_path=gate_path,
    )

    assert result["status"] == "blocked"
    assert result["task_id"] == "TASK_FAIL"
    assert "COMMAND_FAILED" in result["blocking_reason"]

    final_task = task_store.get("TASK_FAIL")
    assert final_task.status == TaskSpecStatus.BLOCKED


def test_docker_unavailable(
    task_store: TaskSpecStore, evidence_dir: Path, monkeypatch
):
    mock_docker_executor = MagicMock()
    mock_docker_executor.execute.return_value = SandboxExecutionResult(
        task_id="TASK_UNAVAILABLE",
        command="ls -l",
        returncode=1,
        stdout="",
        stderr="Docker daemon not available.",
        blocked=True,
        reasons=["DOCKER_UNAVAILABLE"],
    )
    monkeypatch.setattr(
        "factory.core.queue_runner.DockerExecutor", lambda: mock_docker_executor
    )
    monkeypatch.setattr("factory.core.queue_runner._git_changed_paths", lambda repo_root: [])

    task = TaskSpec(
        task_id="TASK_UNAVAILABLE",
        title="Test docker unavailable",
        objective="test",
        allowed_paths=["."],
        forbidden_paths=[],
        acceptance_criteria=["test"],
        validation_commands=["ls -l"],
        metadata={"operational_mode": "test"},
    )
    task_store.enqueue(task)
    gate_path = task_store.root_dir.parent / "AUDIT_GATE.md"
    gate_path.write_text("status: OPEN")

    result = run_one_sovereign_task(
        tasks_dir=task_store.root_dir,
        evidence_dir=evidence_dir,
        gate_path=gate_path,
    )

    assert result["status"] == "blocked"
    assert result["task_id"] == "TASK_UNAVAILABLE"
    assert "COMMAND_BLOCKED" in result["blocking_reason"]
    assert "DOCKER_UNAVAILABLE" in result["blocking_reason"]

    final_task = task_store.get("TASK_UNAVAILABLE")
    assert final_task.status == TaskSpecStatus.BLOCKED

