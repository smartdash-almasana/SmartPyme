from pathlib import Path

from factory.core.task_loop import (
    MultiagentTask,
    load_task,
    run_persisted_multiagent_task_cycle,
    save_task,
)

BUSINESS_TASK_TYPES: set[str] = set()


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

    if task.task_type in BUSINESS_TASK_TYPES:
        return _block_product_runtime_task(task, tasks_dir, evidence_dir)

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


def _block_product_runtime_task(
    task: MultiagentTask,
    tasks_dir: str | Path,
    evidence_dir: str | Path,
) -> dict:
    task.status = "blocked"
    task.blocking_reason = "PRODUCT_RUNTIME_TASK_NOT_ALLOWED_IN_FACTORY_CORE"
    task.audit = {"status": "blocked", "reason": task.blocking_reason}
    task.report_path = _write_block_report(task, Path(evidence_dir))
    save_task(task, tasks_dir)
    return {
        "status": task.status,
        "task_id": task.task_id,
        "report_path": task.report_path,
        "blocking_reason": task.blocking_reason,
    }


def _write_block_report(task: MultiagentTask, evidence_dir: Path) -> str:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    path = evidence_dir / f"{task.task_id}.txt"
    path.write_text(
        "\n".join(
            [
                f"task_id={task.task_id}",
                f"status={task.status}",
                f"task_type={task.task_type}",
                f"blocking_reason={task.blocking_reason}",
            ]
        ),
        encoding="utf-8",
    )
    return str(path)
