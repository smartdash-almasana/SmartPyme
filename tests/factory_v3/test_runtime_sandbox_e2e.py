from pathlib import Path

from factory_v3.contracts.entities import (
    AgentCard,
    AgentRole,
    ArtifactType,
    TaskEnvelope,
)
from factory_v3.ledgers.artifact_ledger import ArtifactLedger
from factory_v3.ledgers.task_ledger import TaskLedger
from factory_v3.runtime.context_rehydrator import ContextRehydrator
from factory_v3.runtime.runtime_snapshot import RuntimeSnapshot
from factory_prefect.contracts.sandbox import SandboxExecutionRequest
from factory_v3.runtime.sandbox_bridge import SandboxBridge


def test_runtime_sandbox_end_to_end(tmp_path: Path):
    task_ledger = TaskLedger(
        ledger_path=str(tmp_path / "task_ledger.jsonl")
    )

    artifact_ledger = ArtifactLedger(
        ledger_path=str(tmp_path / "artifact_ledger.jsonl")
    )

    task = TaskEnvelope(
        objective="Execute sandbox runtime",
        assigned_agent="sandbox-agent",
    )

    task_ledger.create_task(
        task,
        producer_id="planner-agent",
    )

    agent = AgentCard(
        agent_id="sandbox-agent",
        role=AgentRole.CODER,
        capabilities=["sandbox_execution"],
    )

    bridge = SandboxBridge()

    result = bridge.execute(
        SandboxExecutionRequest(
            task_id=task.task_id,
            command="python -c \"print('sandbox_ok')\"",
            timeout_seconds=30,
            network_disabled=True,
        )
    )

    if result.blocked and "DOCKER_UNAVAILABLE" in result.reasons:
        import pytest
        pytest.skip("Docker unavailable in this environment")

    assert result.returncode == 0
    assert "sandbox_ok" in result.stdout

    artifact_file = tmp_path / "sandbox_output.txt"
    artifact_file.write_text(result.stdout, encoding="utf-8")

    artifact = artifact_ledger.register_file(
        task_id=task.task_id,
        artifact_type=ArtifactType.TEST_REPORT,
        storage_path=str(artifact_file),
        producer_id=agent.agent_id,
    )

    rehydrator = ContextRehydrator(
        task_ledger=task_ledger,
        artifact_ledger=artifact_ledger,
    )

    snapshot = rehydrator.rebuild_task_context(task.task_id)

    assert snapshot.task_id == task.task_id
    assert artifact.artifact_id in snapshot.artifact_ids
    assert snapshot.event_count >= 1
