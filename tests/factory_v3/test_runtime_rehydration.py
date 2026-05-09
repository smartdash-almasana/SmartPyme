from pathlib import Path

from factory_v3.contracts.entities import ArtifactType, TaskEnvelope
from factory_v3.ledgers.artifact_ledger import ArtifactLedger
from factory_v3.ledgers.task_ledger import TaskLedger
from factory_v3.runtime.context_rehydrator import ContextRehydrator


def test_context_rehydrator_rebuilds_runtime_snapshot(tmp_path: Path):
    artifact_file = tmp_path / "artifact.txt"
    artifact_file.write_text("runtime context", encoding="utf-8")

    task_ledger = TaskLedger(ledger_path=str(tmp_path / "task_ledger.jsonl"))
    artifact_ledger = ArtifactLedger(ledger_path=str(tmp_path / "artifact_ledger.jsonl"))

    task = TaskEnvelope(
        objective="rehydrate runtime",
        assigned_agent="runtime-agent",
    )

    task_ledger.create_task(task, producer_id="planner-agent")

    artifact = artifact_ledger.register_file(
        task_id=task.task_id,
        artifact_type=ArtifactType.PLAN,
        storage_path=str(artifact_file),
        producer_id="planner-agent",
    )

    rehydrator = ContextRehydrator(
        task_ledger=task_ledger,
        artifact_ledger=artifact_ledger,
    )

    snapshot = rehydrator.rebuild_task_context(task.task_id)

    assert snapshot.task_id == task.task_id
    assert artifact.artifact_id in snapshot.artifact_ids
    assert snapshot.event_count >= 1
