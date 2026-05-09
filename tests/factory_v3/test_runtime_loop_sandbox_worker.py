import pytest
from pathlib import Path
from factory_v3.contracts.entities import ArtifactType, TaskEnvelope, TaskState
from factory_v3.ledgers.artifact_ledger import ArtifactLedger
from factory_v3.ledgers.task_ledger import TaskLedger
from factory_v3.runtime.context_rehydrator import ContextRehydrator
from factory_v3.runtime.runtime_sandbox_worker import RuntimeSandboxWorker
from factory_v3.runtime.sandbox_bridge import SandboxBridge


def test_runtime_loop_sandbox_worker_happy_path(tmp_path: Path):
    # 1. Setup
    task_ledger = TaskLedger(ledger_path=str(tmp_path / "task_ledger.jsonl"))
    artifact_ledger = ArtifactLedger(ledger_path=str(tmp_path / "artifact_ledger.jsonl"))
    sandbox_bridge = SandboxBridge()
    worker = RuntimeSandboxWorker(
        task_ledger=task_ledger,
        artifact_ledger=artifact_ledger,
        sandbox_bridge=sandbox_bridge,
        work_dir=tmp_path,
    )

    # 2. Crear task PENDING
    task = TaskEnvelope(objective="Test the worker loop", assigned_agent="test-agent")
    task_ledger.create_task(task, producer_id="test-planner")

    assert task_ledger.get_latest_state(task.task_id) == TaskState.PENDING

    # 3. Worker procesa la tarea
    command = "python -c \"print('worker_ok')\""
    try:
        worker.run_one(task_id=task.task_id, command=command)
    except Exception as e:
        if "Docker daemon not available" in str(e):
            pytest.skip("Docker unavailable in this environment")
        raise

    # 4. Validar estado final
    assert task_ledger.get_latest_state(task.task_id) == TaskState.DONE

    # 5. Validar artifact
    artifact = artifact_ledger.get_latest_artifact(task.task_id, ArtifactType.TEST_REPORT)
    assert artifact is not None
    assert artifact.producer_id == "sandbox-worker"
    
    artifact_path = Path(artifact.storage_path)
    assert artifact_path.exists()
    assert "worker_ok" in artifact_path.read_text()

    # 6. Validar reconstrucción de contexto
    rehydrator = ContextRehydrator(task_ledger, artifact_ledger)
    snapshot = rehydrator.rebuild_task_context(task.task_id)

    assert snapshot.task_id == task.task_id
    assert snapshot.state == TaskState.DONE
    assert artifact.artifact_id in snapshot.artifact_ids
