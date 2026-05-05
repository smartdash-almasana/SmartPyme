from __future__ import annotations

import json
import subprocess
from pathlib import Path

from factory.core.queue_runner import run_one_queued_task
from factory.core.task_spec import TaskSpec
from factory.core.task_spec_store import TaskSpecStore


def _open_gate(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# AUDIT GATE\n\nstatus: OPEN\n", encoding="utf-8")


def _closed_gate(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# AUDIT GATE\n\nstatus: CLOSED\n", encoding="utf-8")


def _init_git_repo(path: Path) -> None:
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=path, check=True)
    (path / "README.md").write_text("test repo\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=path, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=path, check=True, capture_output=True, text=True)


def _task(task_id: str = "TS_TEST_001") -> TaskSpec:
    return TaskSpec(
        task_id=task_id,
        title="Dummy sovereign task",
        objective="Validate sovereign runner over one pending TaskSpec",
        allowed_paths=["allowed"],
        forbidden_paths=["forbidden"],
        acceptance_criteria=["runner closes one task"],
        validation_commands=["python3 -c print(123)"],
        metadata={
            "operational_mode": "WRITE_AUTHORIZED",
            "model_target": "DEEPSEEK_4_PRO",
            "provider_target": "OPENROUTER",
            "executor_target": "HERMES",
            "preflight_commands": ["python3 -c print(456)"],
        },
    )


def test_sovereign_runner_blocks_when_gate_closed(tmp_path):
    tasks_dir = tmp_path / "taskspecs"
    evidence_dir = tmp_path / "evidence"
    gate_path = tmp_path / "AUDIT_GATE.md"
    _closed_gate(gate_path)
    TaskSpecStore(tasks_dir).enqueue(_task())

    result = run_one_queued_task(
        tasks_dir,
        evidence_dir,
        use_sovereign=True,
        gate_path=gate_path,
        repo_root=tmp_path,
    )

    assert result["status"] == "blocked"
    assert result["reason"] == "AUDIT_GATE_CLOSED"


def test_sovereign_runner_takes_pending_task_and_creates_evidence(tmp_path):
    tasks_dir = tmp_path / "taskspecs"
    evidence_dir = tmp_path / "evidence"
    gate_path = tmp_path / "AUDIT_GATE.md"
    _open_gate(gate_path)
    TaskSpecStore(tasks_dir).enqueue(_task())

    result = run_one_queued_task(
        tasks_dir,
        evidence_dir,
        use_sovereign=True,
        gate_path=gate_path,
        repo_root=tmp_path,
    )

    assert result["task_id"] == "TS_TEST_001"
    task_evidence = evidence_dir / "TS_TEST_001"
    for filename in (
        "cycle.md",
        "commands.txt",
        "git_status.txt",
        "git_diff.patch",
        "tests.txt",
        "decision.txt",
        "execution_result.json",
        "evidence_manifest.json",
        "audit_decision.json",
    ):
        assert (task_evidence / filename).exists()


def test_sovereign_runner_moves_task_to_final_state_and_waiting_audit(tmp_path):
    tasks_dir = tmp_path / "taskspecs"
    evidence_dir = tmp_path / "evidence"
    gate_path = tmp_path / "AUDIT_GATE.md"
    _open_gate(gate_path)
    store = TaskSpecStore(tasks_dir)
    store.enqueue(_task())

    result = run_one_queued_task(
        tasks_dir,
        evidence_dir,
        use_sovereign=True,
        gate_path=gate_path,
        repo_root=tmp_path,
    )

    assert result["status"] in {"done", "blocked"}
    assert store.next_pending() is None
    assert "status: WAITING_AUDIT" in gate_path.read_text(encoding="utf-8")


def test_sovereign_runner_writes_evidence_manifest_json(tmp_path):
    tasks_dir = tmp_path / "taskspecs"
    evidence_dir = tmp_path / "evidence"
    gate_path = tmp_path / "AUDIT_GATE.md"
    _open_gate(gate_path)
    TaskSpecStore(tasks_dir).enqueue(_task())

    result = run_one_queued_task(
        tasks_dir,
        evidence_dir,
        use_sovereign=True,
        gate_path=gate_path,
        repo_root=tmp_path,
    )

    manifest_path = Path(result["evidence_manifest_path"])
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["task_id"] == "TS_TEST_001"
    assert manifest["evidence_dir"] == str(evidence_dir / "TS_TEST_001")
    assert manifest["gate_status_after"] == "WAITING_AUDIT"
    assert manifest["complete"] is True
    assert manifest["required_files"]["cycle"].endswith("cycle.md")
    assert manifest["required_files"]["decision"].endswith("decision.txt")


def test_sovereign_runner_writes_execution_result_json(tmp_path):
    tasks_dir = tmp_path / "taskspecs"
    evidence_dir = tmp_path / "evidence"
    gate_path = tmp_path / "AUDIT_GATE.md"
    _open_gate(gate_path)
    TaskSpecStore(tasks_dir).enqueue(_task())

    result = run_one_queued_task(
        tasks_dir,
        evidence_dir,
        use_sovereign=True,
        gate_path=gate_path,
        repo_root=tmp_path,
    )

    execution_result_path = Path(result["execution_result_path"])
    execution_result = json.loads(execution_result_path.read_text(encoding="utf-8"))
    assert execution_result["task_id"] == "TS_TEST_001"
    assert execution_result["status"] in {"done", "blocked"}
    assert execution_result["executor_real"] == "HERMES"
    assert execution_result["model_real"] == "DEEPSEEK_4_PRO"
    assert execution_result["provider_real"] == "OPENROUTER"
    assert execution_result["commands_run"][0]["command"] == "python3 -c print(456)"
    assert execution_result["commands_run"][0]["returncode"] == 0
    assert execution_result["commit_hash"]
    assert execution_result["branch"] is not None


def test_sovereign_runner_writes_audit_decision_json(tmp_path):
    tasks_dir = tmp_path / "taskspecs"
    evidence_dir = tmp_path / "evidence"
    gate_path = tmp_path / "AUDIT_GATE.md"
    _open_gate(gate_path)
    TaskSpecStore(tasks_dir).enqueue(_task())

    result = run_one_queued_task(
        tasks_dir,
        evidence_dir,
        use_sovereign=True,
        gate_path=gate_path,
        repo_root=tmp_path,
    )

    audit_decision_path = Path(result["audit_decision_path"])
    audit_decision = json.loads(audit_decision_path.read_text(encoding="utf-8"))
    assert audit_decision["task_id"] == "TS_TEST_001"
    assert audit_decision["decision"] in {"PASS", "BLOCKED"}
    assert audit_decision["auditor"] == "sovereign_task_loop_v1"
    assert audit_decision["checked_commit"]
    assert audit_decision["checked_evidence_dir"] == str(evidence_dir / "TS_TEST_001")
    assert audit_decision["required_human_action"] is False
    assert audit_decision["next_gate_status"] in {"OPEN", "WAITING_AUDIT"}


def test_sovereign_runner_writes_human_escalation_json_when_required(tmp_path):
    tasks_dir = tmp_path / "taskspecs"
    evidence_dir = tmp_path / "evidence"
    gate_path = tmp_path / "AUDIT_GATE.md"
    _open_gate(gate_path)
    task = TaskSpec(
        task_id="TS_TEST_ESCALATE",
        title="Human escalation task",
        objective="Validate human escalation file emission",
        allowed_paths=["allowed"],
        forbidden_paths=[],
        acceptance_criteria=["human escalation is emitted"],
        validation_commands=["python3 -c print(1)"],
        metadata={
            "operational_mode": "WRITE_AUTHORIZED",
            "model_target": "DEEPSEEK_4_PRO",
            "human_required": True,
            "human_reason": "Rotate exposed key before continuing",
            "decision_needed": "Confirm key rotation",
            "human_options": ["ROTATE_KEY", "STOP_FACTORY"],
            "recommended_option": "ROTATE_KEY",
        },
    )
    TaskSpecStore(tasks_dir).enqueue(task)

    result = run_one_queued_task(
        tasks_dir,
        evidence_dir,
        use_sovereign=True,
        gate_path=gate_path,
        repo_root=tmp_path,
    )

    escalation_path = Path(result["human_escalation_path"])
    escalation = json.loads(escalation_path.read_text(encoding="utf-8"))
    assert escalation["task_id"] == "TS_TEST_ESCALATE"
    assert escalation["escalation_type"] == "HUMAN_REQUIRED"
    assert escalation["reason"] == "Rotate exposed key before continuing"
    assert escalation["decision_needed"] == "Confirm key rotation"
    assert escalation["options"] == ["ROTATE_KEY", "STOP_FACTORY"]
    assert escalation["recommended_option"] == "ROTATE_KEY"
    assert escalation["safe_to_continue"] is False


def test_sovereign_runner_blocks_missing_operational_mode(tmp_path):
    tasks_dir = tmp_path / "taskspecs"
    evidence_dir = tmp_path / "evidence"
    gate_path = tmp_path / "AUDIT_GATE.md"
    _open_gate(gate_path)
    task = TaskSpec(
        task_id="TS_TEST_002",
        title="Missing mode task",
        objective="Validate missing operational mode blocks task",
        allowed_paths=["allowed"],
        forbidden_paths=[],
        acceptance_criteria=["mode is required"],
        validation_commands=["python3 -c print(1)"],
        metadata={"model_target": "DEEPSEEK_4_PRO"},
    )
    TaskSpecStore(tasks_dir).enqueue(task)

    result = run_one_queued_task(
        tasks_dir,
        evidence_dir,
        use_sovereign=True,
        gate_path=gate_path,
        repo_root=tmp_path,
    )

    assert result["status"] == "blocked"
    assert result["blocking_reason"] == "BLOCKED_MODE_MISSING"


def test_sovereign_runner_blocks_untracked_path_outside_allowed_paths(tmp_path):
    _init_git_repo(tmp_path)
    tasks_dir = tmp_path / "taskspecs"
    evidence_dir = tmp_path / "evidence"
    gate_path = tmp_path / "AUDIT_GATE.md"
    _open_gate(gate_path)
    task = TaskSpec(
        task_id="TS_TEST_UNTRACKED_FORBIDDEN",
        title="Untracked path validation task",
        objective="Validate untracked files are included in path guardrails",
        allowed_paths=["allowed"],
        forbidden_paths=["forbidden"],
        acceptance_criteria=["untracked forbidden path blocks task"],
        validation_commands=["python3 -c open('forbidden/new.txt','w').write('bad')"],
        metadata={"operational_mode": "WRITE_AUTHORIZED", "model_target": "DEEPSEEK_4_PRO"},
    )
    TaskSpecStore(tasks_dir).enqueue(task)
    (tmp_path / "forbidden").mkdir()

    result = run_one_queued_task(
        tasks_dir,
        evidence_dir,
        use_sovereign=True,
        gate_path=gate_path,
        repo_root=tmp_path,
    )

    assert result["status"] == "blocked"
    assert "FORBIDDEN_PATH_MODIFIED: forbidden/new.txt" in result["blocking_reason"]
    assert "PATH_NOT_ALLOWED: forbidden/new.txt" in result["blocking_reason"]
