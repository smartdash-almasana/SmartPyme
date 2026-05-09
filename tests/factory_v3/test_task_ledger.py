from pathlib import Path

from factory_v3.contracts.entities import TaskEnvelope, TaskState
from factory_v3.ledgers.task_ledger import TaskLedger


def test_task_ledger_tracks_state_transitions(tmp_path: Path):
    ledger = TaskLedger(ledger_path=str(tmp_path / "task_ledger.jsonl"))

    task = TaskEnvelope(
        objective="build runtime",
        assigned_agent="coder-agent",
    )

    ledger.create_task(task, producer_id="planner-agent")

    ledger.transition_task(
        task_id=task.task_id,
        previous_state=TaskState.PENDING,
        next_state=TaskState.ACTIVE,
        producer_id="coder-agent",
    )

    ledger.transition_task(
        task_id=task.task_id,
        previous_state=TaskState.ACTIVE,
        next_state=TaskState.DONE,
        producer_id="coder-agent",
    )

    latest = ledger.get_latest_state(task.task_id)

    assert latest == TaskState.DONE
