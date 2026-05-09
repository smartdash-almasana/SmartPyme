from pathlib import Path

from factory_v3.contracts.entities import ArtifactType
from factory_v3.ledgers.artifact_ledger import ArtifactLedger


def test_artifact_ledger_registers_and_discovers_latest_artifact(tmp_path: Path):
    artifact_file = tmp_path / "plan.txt"
    artifact_file.write_text("plan content", encoding="utf-8")

    ledger = ArtifactLedger(ledger_path=str(tmp_path / "ledger.jsonl"))

    artifact = ledger.register_file(
        task_id="task-1",
        artifact_type=ArtifactType.PLAN,
        storage_path=str(artifact_file),
        producer_id="planner-agent",
    )

    latest = ledger.get_latest_artifact("task-1", ArtifactType.PLAN)

    assert latest is not None
    assert latest.artifact_id == artifact.artifact_id
    assert latest.content_hash == artifact.content_hash
    assert latest.read_content() == "plan content"
