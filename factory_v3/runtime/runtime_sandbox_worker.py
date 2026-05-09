from __future__ import annotations

from pathlib import Path
from factory_v3.contracts.entities import ArtifactType, TaskState
from factory_v3.ledgers.artifact_ledger import ArtifactLedger
from factory_v3.ledgers.task_ledger import TaskLedger
from factory_v3.runtime.sandbox_bridge import SandboxBridge
from factory_prefect.contracts.sandbox import SandboxExecutionRequest


class RuntimeSandboxWorker:
    def __init__(
        self,
        task_ledger: TaskLedger,
        artifact_ledger: ArtifactLedger,
        sandbox_bridge: SandboxBridge,
        work_dir: Path,
    ):
        self.task_ledger = task_ledger
        self.artifact_ledger = artifact_ledger
        self.sandbox_bridge = sandbox_bridge
        self.work_dir = work_dir
        self.work_dir.mkdir(exist_ok=True)

    def run_one(self, task_id: str, command: str) -> None:
        task_state = self.task_ledger.get_latest_state(task_id)
        if task_state is None:
            # O manejar como un error si se espera que la tarea siempre exista
            return

        request = SandboxExecutionRequest(
            task_id=task_id,
            command=command,
        )

        result = self.sandbox_bridge.execute(request)

        if result.blocked:
            self.task_ledger.transition_task(
                task_id=task_id,
                previous_state=task_state,
                next_state=TaskState.FAILED,
                producer_id="sandbox-worker",
                reason=f"Execution blocked: {', '.join(result.reasons)}",
            )
            return

        if result.returncode == 0:
            artifact_path = self.work_dir / f"{task_id}_stdout.txt"
            artifact_path.write_text(result.stdout, encoding="utf-8")

            self.artifact_ledger.register_file(
                task_id=task_id,
                artifact_type=ArtifactType.TEST_REPORT,
                storage_path=str(artifact_path),
                producer_id="sandbox-worker",
            )

            self.task_ledger.transition_task(
                task_id=task_id,
                previous_state=task_state,
                next_state=TaskState.DONE,
                producer_id="sandbox-worker",
            )
        else:
            self.task_ledger.transition_task(
                task_id=task_id,
                previous_state=task_state,
                next_state=TaskState.FAILED,
                producer_id="sandbox-worker",
                reason=f"Execution failed with return code {result.returncode}",
            )
