from __future__ import annotations

import json
from pathlib import Path

from factory.core.task_spec import TaskSpec, TaskSpecStatus
from factory.orchestrator.evidence_store import EvidenceStore


def test_evidence_store_writes_all_files(tmp_path: Path) -> None:
    repo_root = tmp_path
    store = EvidenceStore(repo_root)
    task_id = "test-task-123"
    task = TaskSpec(
        task_id=task_id,
        title="Test Task",
        objective="Test objective",
        allowed_paths=["/"],
        forbidden_paths=[],
        acceptance_criteria=["all good"],
        validation_commands=["echo 'ok'"],
    )

    # Act
    store.write_cycle_evidence(task, "in_progress", None, "OPEN")
    store.write_command_evidence(task_id, [{"command": "echo 'hello'", "returncode": 0, "stdout": "hello", "stderr": ""}])
    store.write_git_evidence(task_id, "git status", "git diff")
    store.write_decision_evidence(task_id, "done", None)
    store.write_execution_result(
        task=task,
        final_status="done",
        blocking_reason=None,
        command_results=[],
        started_at="2024-01-01T00:00:00Z",
        finished_at="2024-01-01T00:01:00Z",
        branch="main",
        commit_hash="abc1234",
    )
    store.write_evidence_manifest(
        task=task,
        branch="main",
        commit_hash="abc1234",
        gate_status_after="WAITING_AUDIT",
    )
    store.write_audit_decision(
        task=task,
        final_status="done",
        blocking_reason=None,
        commit_hash="abc1234",
        manifest_path=store.evidence_dir(task_id) / "evidence_manifest.json",
    )

    # Assert
    evidence_dir = repo_root / "factory" / "evidence" / task_id
    assert (evidence_dir / "cycle.md").exists()
    assert (evidence_dir / "commands.txt").exists()
    assert (evidence_dir / "git_status.txt").exists()
    assert (evidence_dir / "git_diff.patch").exists()
    assert (evidence_dir / "tests.txt").exists()
    assert (evidence_dir / "decision.txt").exists()
    assert (evidence_dir / "execution_result.json").exists()
    assert (evidence_dir / "evidence_manifest.json").exists()
    assert (evidence_dir / "audit_decision.json").exists()
