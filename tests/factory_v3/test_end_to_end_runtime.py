from pathlib import Path

from factory_v3.contracts.entities import (
    AgentCard,
    AgentRole,
    ArtifactType,
    TaskEnvelope,
)
from factory_v3.ledgers.artifact_ledger import ArtifactLedger
from factory_v3.ledgers.task_ledger import TaskLedger
from factory_v3.prompting.prompt_builder import PromptBuilder
from factory_v3.runtime.agent_executor import AgentExecutor
from factory_v3.runtime.context_rehydrator import ContextRehydrator
from factory_v3.runtime.runtime_snapshot import RuntimeSnapshot


def test_end_to_end_runtime_cycle(tmp_path: Path):
    task_ledger = TaskLedger(
        ledger_path=str(tmp_path / "task_ledger.jsonl")
    )

    artifact_ledger = ArtifactLedger(
        ledger_path=str(tmp_path / "artifact_ledger.jsonl")
    )

    task = TaskEnvelope(
        objective="Generate runtime artifact",
        assigned_agent="coder-agent",
    )

    task_ledger.create_task(
        task,
        producer_id="planner-agent",
    )

    agent = AgentCard(
        agent_id="coder-agent",
        role=AgentRole.CODER,
        capabilities=["write_artifact"],
    )

    prompt_builder = PromptBuilder()

    prompt_artifact = prompt_builder.build(
        task_id=task.task_id,
        agent_id=agent.agent_id,
        role="coder",
        instruction="Generate a runtime artifact.",
        artifacts=["Runtime specification"],
        constraints=["respect output schema"],
    )

    output_file = tmp_path / "runtime_output.txt"
    output_file.write_text(
        prompt_artifact.rendered_prompt,
        encoding="utf-8",
    )

    registered_artifact = artifact_ledger.register_file(
        task_id=task.task_id,
        artifact_type=ArtifactType.CODE_PATCH,
        storage_path=str(output_file),
        producer_id=agent.agent_id,
    )

    rehydrator = ContextRehydrator(
        task_ledger=task_ledger,
        artifact_ledger=artifact_ledger,
    )

    executor = AgentExecutor(
        task_ledger=task_ledger,
        rehydrator=rehydrator,
    )

    def runtime_callable(snapshot: RuntimeSnapshot):
        assert registered_artifact.artifact_id in snapshot.artifact_ids
        return {
            "task_id": snapshot.task_id,
            "artifact_count": len(snapshot.artifact_ids),
        }

    result = executor.execute(
        task=task,
        agent=agent,
        execution_callable=runtime_callable,
    )

    rebuilt_snapshot = rehydrator.rebuild_task_context(task.task_id)

    assert result["task_id"] == task.task_id
    assert rebuilt_snapshot.artifact_ids
    assert rebuilt_snapshot.event_count >= 1
