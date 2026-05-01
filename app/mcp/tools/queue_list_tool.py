from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from factory.adapters.app_bridge.agent_loop.multiagent_task_loop import load_task, task_to_dict
from factory.adapters.app_bridge.agent_loop.queue_runner import find_next_pending_task


def list_factory_queue(tasks_dir: str | Path, include_done: bool = False) -> dict[str, Any]:
    """
    Lista las tareas en la cola operativa.

    Args:
        tasks_dir: Directorio donde se encuentran los archivos JSON de las tareas.
        include_done: Si es True, incluye las tareas con estado 'done' en la lista.

    Returns:
        Un diccionario con el estado de la cola, conteos y lista de tareas.
    """
    tasks_dir_path = Path(tasks_dir)
    if not tasks_dir_path.exists():
        return {"status": "ok", "total": 0, "counts": {}, "tasks": []}

    # Soportamos subcarpetas/estados si la cola usa estructura jerárquica
    json_files = sorted(tasks_dir_path.rglob("*.json"))

    all_tasks = []
    for path in json_files:
        try:
            # load_task espera (task_id, tasks_dir)
            task = load_task(path.stem, path.parent)
            if task:
                task_dict = task_to_dict(task)
                task_dict["path"] = str(path)
                all_tasks.append(task_dict)
        except Exception:  # pragma: no cover
            continue

    counts = Counter(t["status"] for t in all_tasks)

    filtered_tasks = all_tasks
    if not include_done:
        filtered_tasks = [t for t in all_tasks if t["status"] != "done"]

    return {
        "status": "ok",
        "total": len(all_tasks),
        "counts": dict(counts),
        "tasks": [
            {
                "task_id": t["task_id"],
                "status": t["status"],
                "path": t["path"],
                "objective": t.get("objective", ""),
                "task_type": t.get("task_type"),
            }
            for t in filtered_tasks
        ],
    }


def get_next_factory_task(tasks_dir: str | Path) -> dict[str, Any]:
    """
    Retorna la próxima tarea pendiente en la cola.

    Args:
        tasks_dir: Directorio donde se encuentran los archivos JSON de las tareas.

    Returns:
        Un diccionario con el estado de la operación y los datos de la tarea si existe.
    """
    # find_next_pending_task solo busca en el primer nivel según su implementación actual
    task = find_next_pending_task(tasks_dir)
    return {"status": "ok", "task": task_to_dict(task) if task else None}
