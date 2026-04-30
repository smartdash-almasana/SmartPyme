from __future__ import annotations

from pathlib import Path
from typing import Callable
from uuid import uuid4

from app.factory.agent_loop.queue_runner import find_next_pending_task, list_task_ids
from app.mcp.tools.factory_control_tool import (
    DEFAULT_EVIDENCE_DIR,
    DEFAULT_TASKS_DIR,
    enqueue_factory_task,
    get_factory_task_status,
    run_factory_once,
)

FactoryEnqueuer = Callable[..., dict]
FactoryRunner = Callable[..., dict]
FactoryStatusReader = Callable[..., dict]


class FactorySuperownerTelegramAdapter:
    """Telegram control plane for the SmartPyme multiagent factory superowner.

    This adapter is intentionally separate from the operational TelegramAdapter used by
    SmartPyme clients/owners. It controls development-factory tasks only.
    """

    def __init__(
        self,
        superowner_telegram_user_id: str | int,
        tasks_dir: str | Path = DEFAULT_TASKS_DIR,
        evidence_dir: str | Path = DEFAULT_EVIDENCE_DIR,
        factory_enqueuer: FactoryEnqueuer = enqueue_factory_task,
        factory_runner: FactoryRunner = run_factory_once,
        factory_status_reader: FactoryStatusReader = get_factory_task_status,
    ) -> None:
        if not str(superowner_telegram_user_id).strip():
            raise ValueError("superowner_telegram_user_id is required")
        self.superowner_telegram_user_id = str(superowner_telegram_user_id)
        self.tasks_dir = Path(tasks_dir)
        self.evidence_dir = Path(evidence_dir)
        self.factory_enqueuer = factory_enqueuer
        self.factory_runner = factory_runner
        self.factory_status_reader = factory_status_reader

    def handle_update(self, update_dict: dict) -> dict:
        user_id = self._extract_user_id(update_dict)
        text = self._extract_text(update_dict)

        if user_id is None:
            return {"status": "security_error", "message": "Falta telegram_user_id."}
        if str(user_id) != self.superowner_telegram_user_id:
            return {
                "status": "unauthorized",
                "telegram_user_id": str(user_id),
                "message": "Usuario no autorizado para controlar la factoría.",
            }

        if text == "/status_factory":
            return self._handle_status_factory(user_id)
        if text == "/run_one":
            return self._handle_run_one(user_id)
        if text == "/tasks_pending":
            return self._handle_tasks_pending(user_id)
        if text.startswith("/task "):
            return self._handle_task_status(user_id, text)
        if text.startswith("/enqueue_dev "):
            return self._handle_enqueue_dev(user_id, text)

        return {
            "status": "unsupported_command",
            "telegram_user_id": str(user_id),
            "message": (
                "Comando no soportado. Usá /status_factory, /tasks_pending, "
                "/task <task_id>, /enqueue_dev <objetivo>, /run_one."
            ),
        }

    def _handle_status_factory(self, user_id: str | int) -> dict:
        task_ids = list_task_ids(self.tasks_dir)
        counts = {"pending": 0, "in_progress": 0, "done": 0, "blocked": 0, "unknown": 0}
        for task_id in task_ids:
            status = self.factory_status_reader(task_id, tasks_dir=self.tasks_dir)
            state = status.get("status", "unknown")
            counts[state if state in counts else "unknown"] += 1

        next_task = find_next_pending_task(self.tasks_dir)
        return {
            "status": "ok",
            "telegram_user_id": str(user_id),
            "counts": counts,
            "next_pending_task_id": next_task.task_id if next_task else None,
            "message": self._format_status_message(counts, next_task.task_id if next_task else None),
        }

    def _handle_tasks_pending(self, user_id: str | int) -> dict:
        pending = []
        for task_id in list_task_ids(self.tasks_dir):
            task_status = self.factory_status_reader(task_id, tasks_dir=self.tasks_dir)
            if task_status.get("status") == "pending":
                pending.append(
                    {
                        "task_id": task_status["task_id"],
                        "objective": task_status.get("objective"),
                        "task_type": task_status.get("task_type"),
                    }
                )

        return {
            "status": "ok",
            "telegram_user_id": str(user_id),
            "pending_count": len(pending),
            "pending_tasks": pending,
            "message": f"Tareas pendientes: {len(pending)}.",
        }

    def _handle_task_status(self, user_id: str | int, text: str) -> dict:
        parts = text.split(maxsplit=1)
        if len(parts) != 2 or not parts[1].strip():
            return {
                "status": "invalid_command",
                "telegram_user_id": str(user_id),
                "message": "Formato inválido. Usá /task <task_id>.",
            }

        task_id = parts[1].strip()
        status = self.factory_status_reader(task_id, tasks_dir=self.tasks_dir)
        return {
            "status": status.get("status"),
            "telegram_user_id": str(user_id),
            "task": status,
            "message": self._format_task_message(status),
        }

    def _handle_enqueue_dev(self, user_id: str | int, text: str) -> dict:
        parts = text.split(maxsplit=1)
        if len(parts) != 2 or not parts[1].strip():
            return {
                "status": "invalid_command",
                "telegram_user_id": str(user_id),
                "message": "Formato inválido. Usá /enqueue_dev <objetivo>.",
            }

        objective = parts[1].strip()
        task_id = f"dev:{uuid4()}"
        queued = self.factory_enqueuer(
            task_id=task_id,
            objective=objective,
            tasks_dir=self.tasks_dir,
            task_type="dev_task",
            payload={"origin": "telegram_superowner", "objective": objective},
        )
        return {
            "status": "queued",
            "telegram_user_id": str(user_id),
            "task": queued,
            "message": f"Tarea dev encolada: {task_id}.",
        }

    def _handle_run_one(self, user_id: str | int) -> dict:
        result = self.factory_runner(tasks_dir=self.tasks_dir, evidence_dir=self.evidence_dir)
        return {
            "status": result.get("status"),
            "telegram_user_id": str(user_id),
            "result": result,
            "message": self._format_run_message(result),
        }

    def _extract_user_id(self, update_dict: dict) -> int | str | None:
        message = update_dict.get("message") or {}
        user = message.get("from") or {}
        return user.get("id")

    def _extract_text(self, update_dict: dict) -> str:
        message = update_dict.get("message") or {}
        return (message.get("text") or "").strip()

    def _format_status_message(self, counts: dict, next_pending_task_id: str | None) -> str:
        return (
            "Factoría: "
            f"pending={counts.get('pending', 0)}, "
            f"in_progress={counts.get('in_progress', 0)}, "
            f"done={counts.get('done', 0)}, "
            f"blocked={counts.get('blocked', 0)}. "
            f"Próxima: {next_pending_task_id or 'ninguna'}."
        )

    def _format_task_message(self, status: dict) -> str:
        if status.get("status") == "not_found":
            return f"Tarea no encontrada: {status.get('task_id')}."
        return (
            f"Tarea {status.get('task_id')}: {status.get('status')}. "
            f"Objetivo: {status.get('objective')}. "
            f"Bloqueo: {status.get('blocking_reason') or 'no'}."
        )

    def _format_run_message(self, result: dict) -> str:
        if result.get("status") == "idle":
            return "Factoría idle: no hay tareas pendientes."
        return (
            f"Run one: task_id={result.get('task_id')} "
            f"status={result.get('status')} "
            f"blocking_reason={result.get('blocking_reason') or 'no'}."
        )
