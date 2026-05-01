from pathlib import Path

from factory.adapters.app_bridge.agent_loop.multiagent_task_loop import (
    MultiagentTask,
    load_task,
    save_task,
)
from factory.adapters.app_bridge.agent_loop.queue_runner import run_one_queued_task
from app.mcp.tools.queue_list_tool import list_factory_queue, get_next_factory_task

DEFAULT_TASKS_DIR = Path("factory/multiagent/tasks")
DEFAULT_EVIDENCE_DIR = Path("factory/multiagent/evidence")


def get_factory_queue_summary(tasks_dir: str | Path | None = None) -> dict:
    """
    Obtiene un resumen de la cola operativa.
    """
    path = Path(tasks_dir) if tasks_dir else DEFAULT_TASKS_DIR
    res = list_factory_queue(path, include_done=True)
    next_task = get_next_factory_task(path)
    
    return {
        "status": "ok",
        "total": res["total"],
        "counts": res["counts"],
        "next_task": next_task["task"]
    }


def get_factory_queue_details(
    tasks_dir: str | Path | None = None, 
    include_done: bool = False
) -> dict:
    """
    Obtiene los detalles completos de la cola operativa.
    """
    path = Path(tasks_dir) if tasks_dir else DEFAULT_TASKS_DIR
    return list_factory_queue(path, include_done=include_done)


def get_next_task_preview(tasks_dir: str | Path | None = None) -> dict:
    """
    Obtiene una vista previa de la próxima tarea pendiente sin ejecutarla.
    """
    from factory.adapters.app_bridge.agent_loop.queue_runner import find_next_pending_task
    
    path = Path(tasks_dir) if tasks_dir else DEFAULT_TASKS_DIR
    task = find_next_pending_task(path)
    
    if task is None:
        return {"status": "idle", "task": None}
    
    return {
        "status": "ok",
        "task": {
            "task_id": task.task_id,
            "objective": task.objective,
            "task_type": task.task_type,
            "status": task.status
        }
    }


def execute_one_task_by_id(
    task_id: str, 
    tasks_dir: str | Path | None = None,
    evidence_dir: str | Path | None = None
) -> dict:
    """
    Ejecuta exactamente la tarea con el ID proporcionado si está pendiente.
    """
    from factory.adapters.app_bridge.agent_loop.queue_runner import (
        BUSINESS_TASK_TYPES,
        run_one_business_task,
    )
    from factory.adapters.app_bridge.agent_loop.multiagent_task_loop import (
        load_task,
        run_persisted_multiagent_task_cycle
    )

    tasks_path = Path(tasks_dir) if tasks_dir else DEFAULT_TASKS_DIR
    evidence_path = Path(evidence_dir) if evidence_dir else DEFAULT_EVIDENCE_DIR
    
    task = load_task(task_id, tasks_path)
    if task is None:
        return {
            "status": "error",
            "task_id": task_id,
            "reason": f"Task {task_id} not found"
        }
    
    if task.status != "pending":
        return {
            "status": "error",
            "task_id": task_id,
            "reason": f"Task {task_id} is in status {task.status}, expected pending"
        }

    if task.task_type in BUSINESS_TASK_TYPES:
        return run_one_business_task(task, tasks_path, evidence_path)

    result = run_persisted_multiagent_task_cycle(task.task_id, tasks_path, evidence_path)
    if result is None:
        return {
            "status": "error",
            "task_id": task_id,
            "reason": "TASK_LOAD_FAILED"
        }

    return {
        "status": result.status,
        "task_id": result.task_id,
        "report_path": result.report_path,
        "blocking_reason": result.blocking_reason,
    }


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
