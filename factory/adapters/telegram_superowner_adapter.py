from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from factory.core.task_spec import TaskSpec, TaskSpecStatus
from factory.core.task_spec_runner import TaskSpecRunner
from factory.core.task_spec_store import TaskSpecStore


DEFAULT_TASKS_DIR = Path("factory/taskspecs")
DEFAULT_EVIDENCE_DIR = Path("factory/evidence/taskspecs")
DEFAULT_ALLOWED_PATHS = ["factory", "tests/factory"]
DEFAULT_FORBIDDEN_PATHS = ["app", "data", ".git"]
DEFAULT_VALIDATION_COMMANDS = [
    "PYTHONPATH=. pytest tests/factory/test_task_spec_contract_fm_013.py tests/factory/test_task_spec_store_fm_014.py tests/factory/test_task_spec_runner_fm_015.py"
]
MAX_EVIDENCE_CHARS = 3500


class TelegramSuperownerAdapter:
    """Telegram control plane for the multiagent factory superowner.

    This adapter belongs to the factory package and controls development TaskSpec
    items only. It does not depend on SmartPyme runtime modules under app/.
    """

    def __init__(
        self,
        superowner_telegram_user_id: str | int,
        tasks_dir: str | Path = DEFAULT_TASKS_DIR,
        evidence_dir: str | Path = DEFAULT_EVIDENCE_DIR,
        store: TaskSpecStore | None = None,
        runner: TaskSpecRunner | None = None,
    ) -> None:
        if not str(superowner_telegram_user_id).strip():
            raise ValueError("superowner_telegram_user_id is required")
        self.superowner_telegram_user_id = str(superowner_telegram_user_id)
        self.tasks_dir = Path(tasks_dir)
        self.evidence_dir = Path(evidence_dir)
        self.store = store or TaskSpecStore(self.tasks_dir)
        self.runner = runner or TaskSpecRunner(self.store, evidence_dir=self.evidence_dir)

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
        if text == "/blocked":
            return self._handle_blocked(user_id)
        if text.startswith("/retry_blocked "):
            return self._handle_retry_blocked(user_id, text)
        if text.startswith("/evidence "):
            return self._handle_evidence(user_id, text)
        if text.startswith("/task "):
            return self._handle_task_status(user_id, text)
        if text.startswith("/enqueue_dev "):
            return self._handle_enqueue_dev(user_id, text)

        return {
            "status": "unsupported_command",
            "telegram_user_id": str(user_id),
            "message": (
                "Comando no soportado. Usá /status_factory, /tasks_pending, "
                "/blocked, /retry_blocked <task_id>, /task <task_id>, "
                "/evidence <task_id>, /enqueue_dev <objetivo>, /run_one."
            ),
        }

    def _handle_status_factory(self, user_id: str | int) -> dict:
        counts = self.store.counts()
        next_task = self.store.next_pending()
        return {
            "status": "ok",
            "telegram_user_id": str(user_id),
            "counts": counts,
            "next_pending_task_id": next_task.task_id if next_task else None,
            "message": self._format_status_message(counts, next_task.task_id if next_task else None),
        }

    def _handle_tasks_pending(self, user_id: str | int) -> dict:
        pending_tasks = self.store.list(TaskSpecStatus.PENDING)
        pending = [self._serialize_task_summary(task) for task in pending_tasks]
        return {
            "status": "ok",
            "telegram_user_id": str(user_id),
            "pending_count": len(pending),
            "pending_tasks": pending,
            "message": f"Tareas pendientes: {len(pending)}.",
        }

    def _handle_blocked(self, user_id: str | int) -> dict:
        blocked_tasks = self.store.list(TaskSpecStatus.BLOCKED)
        blocked = [self._serialize_blocked_task(task) for task in blocked_tasks]
        return {
            "status": "ok",
            "telegram_user_id": str(user_id),
            "blocked_count": len(blocked),
            "blocked_tasks": blocked,
            "message": self._format_blocked_message(blocked),
        }

    def _handle_retry_blocked(self, user_id: str | int, text: str) -> dict:
        parts = text.split(maxsplit=1)
        if len(parts) != 2 or not parts[1].strip():
            return {
                "status": "invalid_command",
                "telegram_user_id": str(user_id),
                "message": "Formato inválido. Usá /retry_blocked <task_id>.",
            }

        task_id = parts[1].strip()
        try:
            task = self.store.retry_blocked(task_id, retried_by=f"telegram:{user_id}")
        except FileNotFoundError:
            return {
                "status": "not_found",
                "telegram_user_id": str(user_id),
                "task_id": task_id,
                "message": f"Tarea no encontrada: {task_id}.",
            }
        except ValueError as exc:
            return {
                "status": "invalid_transition",
                "telegram_user_id": str(user_id),
                "task_id": task_id,
                "message": str(exc),
            }

        return {
            "status": "queued",
            "telegram_user_id": str(user_id),
            "task": self._serialize_task(task),
            "message": f"Tarea bloqueada devuelta a pending: {task_id}.",
        }

    def _handle_evidence(self, user_id: str | int, text: str) -> dict:
        parts = text.split(maxsplit=1)
        if len(parts) != 2 or not parts[1].strip():
            return {
                "status": "invalid_command",
                "telegram_user_id": str(user_id),
                "message": "Formato inválido. Usá /evidence <task_id>.",
            }

        task_id = parts[1].strip()
        task = self.store.get(task_id)
        if task is None:
            return {
                "status": "not_found",
                "telegram_user_id": str(user_id),
                "task_id": task_id,
                "evidence": [],
                "message": f"Tarea no encontrada: {task_id}.",
            }

        evidence = [self._read_evidence_path(path) for path in task.evidence_paths]
        return {
            "status": "ok",
            "telegram_user_id": str(user_id),
            "task_id": task_id,
            "evidence_count": len(evidence),
            "evidence": evidence,
            "message": self._format_evidence_message(task_id, evidence),
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
        task = self.store.get(task_id)
        if task is None:
            payload = {"status": "not_found", "task_id": task_id}
            return {
                "status": "not_found",
                "telegram_user_id": str(user_id),
                "task": payload,
                "message": self._format_task_message(payload),
            }

        payload = self._serialize_task(task)
        return {
            "status": task.status.value,
            "telegram_user_id": str(user_id),
            "task": payload,
            "message": self._format_task_message(payload),
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
        task_id = f"dev-{uuid4()}"
        task = TaskSpec(
            task_id=task_id,
            title=_title_from_objective(objective),
            objective=objective,
            allowed_paths=list(DEFAULT_ALLOWED_PATHS),
            forbidden_paths=list(DEFAULT_FORBIDDEN_PATHS),
            acceptance_criteria=["La tarea dev produce evidencia verificable o queda bloqueada con motivo."],
            validation_commands=list(DEFAULT_VALIDATION_COMMANDS),
            metadata={"origin": "telegram_superowner", "telegram_user_id": str(user_id)},
        )
        path = self.store.enqueue(task)
        queued = {
            "status": "queued",
            "task_id": task.task_id,
            "task_type": "taskspec_dev",
            "path": path,
        }
        return {
            "status": "queued",
            "telegram_user_id": str(user_id),
            "task": queued,
            "message": f"TaskSpec dev encolada: {task_id}.",
        }

    def _handle_run_one(self, user_id: str | int) -> dict:
        result = self.runner.run_next()
        if result.task_id is None:
            payload = {
                "status": "idle",
                "task_id": None,
                "reason": result.blocking_reason,
            }
            return {
                "status": "idle",
                "telegram_user_id": str(user_id),
                "result": payload,
                "message": self._format_run_message(payload),
            }

        payload = {
            "status": result.status.value,
            "task_id": result.task_id,
            "evidence_paths": result.evidence_paths,
            "blocking_reason": result.blocking_reason,
            "path_errors": result.path_errors,
            "command_results": [
                {
                    "command": command_result.command,
                    "exit_code": command_result.exit_code,
                    "stdout": command_result.stdout,
                    "stderr": command_result.stderr,
                }
                for command_result in result.command_results
            ],
        }
        return {
            "status": result.status.value,
            "telegram_user_id": str(user_id),
            "result": payload,
            "message": self._format_run_message(payload),
        }

    def _extract_user_id(self, update_dict: dict) -> int | str | None:
        message = update_dict.get("message") or {}
        user = message.get("from") or {}
        return user.get("id")

    def _extract_text(self, update_dict: dict) -> str:
        message = update_dict.get("message") or {}
        return (message.get("text") or "").strip()

    def _serialize_task_summary(self, task: TaskSpec) -> dict:
        return {
            "task_id": task.task_id,
            "title": task.title,
            "objective": task.objective,
            "status": task.status.value,
        }

    def _serialize_blocked_task(self, task: TaskSpec) -> dict:
        return {
            "task_id": task.task_id,
            "title": task.title,
            "objective": task.objective,
            "blocking_reason": task.blocking_reason,
            "evidence_paths": task.evidence_paths,
        }

    def _serialize_task(self, task: TaskSpec) -> dict:
        return task.to_dict()

    def _read_evidence_path(self, evidence_path: str) -> dict:
        path = Path(evidence_path)
        exists = path.exists()
        content = ""
        truncated = False
        if exists:
            content = path.read_text(encoding="utf-8")
            if len(content) > MAX_EVIDENCE_CHARS:
                content = content[:MAX_EVIDENCE_CHARS]
                truncated = True
        return {
            "path": evidence_path,
            "exists": exists,
            "content": content,
            "truncated": truncated,
        }

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
            return f"Tarea no encontrada: {status.get('task_id')} ."
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

    def _format_blocked_message(self, blocked: list[dict]) -> str:
        if not blocked:
            return "No hay tareas bloqueadas."
        return "Tareas bloqueadas: " + ", ".join(
            f"{item['task_id']} ({item.get('blocking_reason') or 'sin motivo'})" for item in blocked
        )

    def _format_evidence_message(self, task_id: str, evidence: list[dict]) -> str:
        if not evidence:
            return f"La tarea {task_id} no tiene evidencia registrada."
        existing = sum(1 for item in evidence if item["exists"])
        return f"Evidencia para {task_id}: {existing}/{len(evidence)} archivos disponibles."


def _title_from_objective(objective: str) -> str:
    title = objective.strip().split("\n", maxsplit=1)[0]
    return title[:80] or "Tarea dev"
