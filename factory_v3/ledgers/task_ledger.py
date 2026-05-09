from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

from factory_v3.contracts.entities import TaskEnvelope, TaskState
from factory_v3.contracts.task_events import TaskEvent, TaskEventType


class TaskLedger:
    def __init__(self, ledger_path: str = "factory_v3/runtime/task_ledger.jsonl"):
        self.ledger_path = Path(ledger_path)
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.ledger_path.exists():
            self.ledger_path.touch()

    def append_event(self, event: TaskEvent) -> None:
        with self.ledger_path.open("a", encoding="utf-8") as handle:
            handle.write(event.model_dump_json())
            handle.write("\n")

    def create_task(self, task: TaskEnvelope, producer_id: str) -> TaskEvent:
        event = TaskEvent(
            task_id=task.task_id,
            event_type=TaskEventType.CREATED,
            producer_id=producer_id,
            next_state=task.status,
            metadata={
                "objective": task.objective,
                "assigned_agent": task.assigned_agent,
                "dependencies": task.dependencies,
            },
        )

        self.append_event(event)
        return event

    def transition_task(
        self,
        *,
        task_id: str,
        previous_state: TaskState,
        next_state: TaskState,
        producer_id: str,
        reason: Optional[str] = None,
    ) -> TaskEvent:
        event = TaskEvent(
            task_id=task_id,
            event_type=TaskEventType.STATE_CHANGED,
            producer_id=producer_id,
            previous_state=previous_state,
            next_state=next_state,
            reason=reason,
        )

        self.append_event(event)
        return event

    def get_events(self, task_id: str) -> List[TaskEvent]:
        results: List[TaskEvent] = []

        with self.ledger_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()

                if not line:
                    continue

                payload = json.loads(line)
                event = TaskEvent(**payload)

                if event.task_id == task_id:
                    results.append(event)

        return results

    def get_latest_state(self, task_id: str) -> Optional[TaskState]:
        latest_state = None

        for event in self.get_events(task_id):
            if event.next_state is not None:
                latest_state = event.next_state

        return latest_state

    def get_tasks_by_state(self, state: TaskState) -> List[str]:
        latest_states = {}

        with self.ledger_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()

                if not line:
                    continue

                payload = json.loads(line)
                event = TaskEvent(**payload)

                if event.next_state is not None:
                    latest_states[event.task_id] = event.next_state

        return [
            task_id
            for task_id, task_state in latest_states.items()
            if task_state == state
        ]
