from __future__ import annotations

import json
import subprocess
from pathlib import Path

from factory.contracts.sandbox import SandboxExecutionResult
from factory.core.queue_runner import run_one_sovereign_task
from factory.core.task_spec import TaskSpec, write_task_spec


def _init_repo(repo: Path) -> None:
    subprocess.run(["git", "init"], cwd=repo, check=True)
    (repo / ".gitignore").write_text("*.pyc\n__pycache__/", encoding="utf-8")
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo, check=True)


def _gate_path(tmp_path: Path) -> Path:
    gate_path = tmp_path / "AUDIT_GATE.md"
    gate_path.write_text("status: OPEN\n", encoding="utf-8")
    return gate_path


def _safe_task(task_id: str, *, command: str = "python -c \"print('ok')\"") -> TaskSpec:
    return TaskSpec(
        task_id=task_id,
        title="Test commit plan",
        objective="Test commit plan creation",
        allowed_paths=["src", "factory/evidence"],
        forbidden_paths=[],
        acceptance_criteria=["It works"],
        validation_commands=[command],
        metadata={"commit_on_success": True, "operational_mode": "test"},
    )


def test_commit_plan_created_on_success(tmp_path: Path, monkeypatch) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    _init_repo(repo_root)

    tasks_dir = tmp_path / "tasks"
    (tasks_dir / "pending").mkdir(parents=True)
    evidence_dir = tmp_path / "evidence"

    task = _safe_task("test-commit-task")
    write_task_spec(task, tasks_dir / "pending" / f"{task.task_id}.json")

    (repo_root / "src").mkdir()
    (repo_root / "src" / "main.py").write_text("print('hello')", encoding="utf-8")

    class FakeDockerExecutor:
        def execute(self, request):
            return SandboxExecutionResult(
                task_id=request.task_id,
                command=request.command,
                returncode=0,
                stdout="OK\n",
                stderr="",
                blocked=False,
                requires_human_approval=False,
                reasons=[],
            )

    monkeypatch.setattr("factory.core.queue_runner.DockerExecutor", FakeDockerExecutor)

    result = run_one_sovereign_task(
        tasks_dir=tasks_dir,
        evidence_dir=evidence_dir,
        gate_path=_gate_path(tmp_path),
        repo_root=repo_root,
    )

    assert result["status"] == "done"
    assert result["commit_plan_path"] is not None

    commit_plan_path = Path(result["commit_plan_path"])
    assert commit_plan_path.exists()

    plan = json.loads(commit_plan_path.read_text(encoding="utf-8"))
    assert plan["task_id"] == "test-commit-task"
    assert plan["blocked"] is False
    assert "src/main.py" in plan["changed_files"]


def test_commit_plan_not_created_when_task_blocks(tmp_path: Path, monkeypatch) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    _init_repo(repo_root)

    tasks_dir = tmp_path / "tasks"
    (tasks_dir / "pending").mkdir(parents=True)
    evidence_dir = tmp_path / "evidence"

    task = _safe_task("test-commit-task-fail", command="python -c \"raise SystemExit(1)\"")
    write_task_spec(task, tasks_dir / "pending" / f"{task.task_id}.json")

    class FakeDockerExecutor:
        def execute(self, request):
            return SandboxExecutionResult(
                task_id=request.task_id,
                command=request.command,
                returncode=1,
                stdout="",
                stderr="forced failure",
                blocked=False,
                requires_human_approval=False,
                reasons=[],
            )

    monkeypatch.setattr("factory.core.queue_runner.DockerExecutor", FakeDockerExecutor)

    result = run_one_sovereign_task(
        tasks_dir=tasks_dir,
        evidence_dir=evidence_dir,
        gate_path=_gate_path(tmp_path),
        repo_root=repo_root,
    )

    assert result["status"] == "blocked"
    assert result.get("commit_plan_path") is None
