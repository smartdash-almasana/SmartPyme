from __future__ import annotations

from factory.control.vcs_controller import create_commit_plan
from factory.core.task_spec import TaskSpec, TaskSpecStatus


def test_create_commit_plan_valid():
    task = TaskSpec(
        task_id="test-task",
        title="Implement feature",
        objective="Implement the new feature",
        allowed_paths=["src"],
        forbidden_paths=[],
        acceptance_criteria=["It works"],
        validation_commands=["echo OK"],
        metadata={"module": "test"},
    )
    changed_files = ["src/main.py"]
    evidence_manifest = {"complete": True}
    branch = "main"
    base_commit = "abcdef"

    plan = create_commit_plan(
        task, changed_files, evidence_manifest, branch, base_commit
    )

    assert not plan.blocked
    assert plan.allowed_paths_valid
    assert plan.evidence_manifest_complete
    assert "feat(test): Implement feature" in plan.commit_message
    assert "feat(test): Implement feature" in plan.pr_title


def test_create_commit_plan_blocked_by_incomplete_evidence():
    task = TaskSpec(
        task_id="test-task",
        title="Implement feature",
        objective="Implement the new feature",
        allowed_paths=["src"],
        forbidden_paths=[],
        acceptance_criteria=["It works"],
        validation_commands=["echo OK"],
    )
    changed_files = ["src/main.py"]
    evidence_manifest = {"complete": False}

    plan = create_commit_plan(task, changed_files, evidence_manifest, "main", "abcdef")

    assert plan.blocked
    assert "EVIDENCE_MANIFEST_INCOMPLETE" in plan.blocking_reasons


def test_create_commit_plan_blocked_by_no_changed_files():
    task = TaskSpec(
        task_id="test-task",
        title="Implement feature",
        objective="Implement the new feature",
        allowed_paths=["src"],
        forbidden_paths=[],
        acceptance_criteria=["It works"],
        validation_commands=["echo OK"],
    )
    changed_files = []
    evidence_manifest = {"complete": True}

    plan = create_commit_plan(task, changed_files, evidence_manifest, "main", "abcdef")

    assert plan.blocked
    assert "NO_CHANGED_FILES" in plan.blocking_reasons


def test_create_commit_plan_blocked_by_forbidden_path():
    task = TaskSpec(
        task_id="test-task",
        title="Implement feature",
        objective="Implement the new feature",
        allowed_paths=["src"],
        forbidden_paths=["dont-touch"],
        acceptance_criteria=["It works"],
        validation_commands=["echo OK"],
    )
    changed_files = ["dont-touch/file.txt"]
    evidence_manifest = {"complete": True}

    plan = create_commit_plan(task, changed_files, evidence_manifest, "main", "abcdef")

    assert plan.blocked
    assert any("FORBIDDEN_PATH_MODIFIED" in reason for reason in plan.blocking_reasons)
