from pathlib import Path

from factory.adapters.app_bridge.agent_loop.multiagent_task_loop import (
    MultiagentTask,
    load_task,
    save_task,
)
from factory.adapters.app_bridge.agent_loop.queue_runner import run_one_queued_task

DEFAULT_TASKS_DIR = Path("factory/multiagent/tasks")
DEFAULT_EVIDENCE_DIR = Path("factory/multiagent/evidence")


def enqueue_factory_task(
    task_id: str,
    objective: str,
    tasks_dir: str | Path = DEFAULT_TASKS_DIR,
    task_type: str | None = None,
    payload: dict | None = None,
) -> dict:
    task = MultiagentTask(
        task_id=task_id,
        objective=objective,
        task_type=task_type,
        payload=payload or {},
    )
    path = save_task(task, tasks_dir)
    return {
        "status": "queued",
        "task_id": task_id,
        "task_type": task_type,
        "path": path,
    }


def run_factory_once(
    tasks_dir: str | Path = DEFAULT_TASKS_DIR,
    evidence_dir: str | Path = DEFAULT_EVIDENCE_DIR,
) -> dict:
    return run_one_queued_task(tasks_dir, evidence_dir)


def get_factory_task_status(
    task_id: str,
    tasks_dir: str | Path = DEFAULT_TASKS_DIR,
) -> dict:
    task = load_task(task_id, tasks_dir)
    if task is None:
        return {
            "status": "not_found",
            "task_id": task_id,
        }

    return {
        "status": task.status,
        "task_id": task.task_id,
        "objective": task.objective,
        "task_type": task.task_type,
        "payload": task.payload,
        "output": task.output,
        "report_path": task.report_path,
        "blocking_reason": task.blocking_reason,
        "plan": task.plan,
        "audit": task.audit,
    }
