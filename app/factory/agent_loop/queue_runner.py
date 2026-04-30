from pathlib import Path

from app.factory.agent_loop.multiagent_task_loop import (
    MultiagentTask,
    load_task,
    run_persisted_multiagent_task_cycle,
)


def list_task_ids(tasks_dir: str | Path) -> list[str]:
    directory = Path(tasks_dir)
    if not directory.exists():
        return []
    return sorted(path.stem for path in directory.glob("*.json"))


def find_next_pending_task(tasks_dir: str | Path) -> MultiagentTask | None:
    for task_id in list_task_ids(tasks_dir):
        task = load_task(task_id, tasks_dir)
        if task is not None and task.status == "pending":
            return task
    return None


def run_one_queued_task(tasks_dir: str | Path, evidence_dir: str | Path) -> dict:
    task = find_next_pending_task(tasks_dir)
    if task is None:
        return {
            "status": "idle",
            "task_id": None,
            "reason": "NO_PENDING_TASK",
        }

    result = run_persisted_multiagent_task_cycle(task.task_id, tasks_dir, evidence_dir)
    if result is None:
        return {
            "status": "blocked",
            "task_id": task.task_id,
            "reason": "TASK_LOAD_FAILED",
        }

    return {
        "status": result.status,
        "task_id": result.task_id,
        "report_path": result.report_path,
        "blocking_reason": result.blocking_reason,
    }
