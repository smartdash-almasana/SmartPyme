from __future__ import annotations

from pathlib import Path

from factory.core.factory_help import build_factory_help_payload, format_factory_help_message
from factory.core.run_report import (
    FactoryRunReport,
    build_factory_run_report,
    list_factory_run_reports,
    read_factory_run_report,
    read_factory_run_report_markdown,
    read_last_factory_run_report,
    write_factory_run_report,
)
from factory.core.run_report_summary import (
    build_factory_health_summary,
    build_failed_paths_summary,
    build_run_report_summary,
    format_factory_health_summary,
    format_failed_paths_summary,
    format_run_report_summary,
)
from factory.core.task_spec import TaskSpec, TaskSpecStatus
from factory.core.task_spec_runner import TaskSpecRunner, TaskSpecRunResult
from factory.core.task_spec_store import TaskSpecStore
from factory.core.task_spec_templates import build_task_spec_from_template, list_template_names

DEFAULT_TASKS_DIR = Path("factory/taskspecs")
DEFAULT_EVIDENCE_DIR = Path("factory/evidence/taskspecs")
MAX_EVIDENCE_CHARS = 3500
MAX_RUN_BATCH_SIZE = 10
MAX_REPORT_MARKDOWN_CHARS = 3500


class TelegramSuperownerAdapter:
    """Telegram control plane for the multiagent factory superowner."""

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

        exact_handlers = {
            "/factory_help": self._handle_factory_help,
            "/status_factory": self._handle_status_factory,
            "/factory_health": self._handle_factory_health,
            "/run_one": self._handle_run_one,
            "/last_report": self._handle_last_report,
            "/run_report_summary": self._handle_run_report_summary,
            "/failed_paths": self._handle_failed_paths,
            "/templates": self._handle_templates,
            "/tasks_pending": self._handle_tasks_pending,
            "/blocked": self._handle_blocked,
        }
        if text in exact_handlers:
            return exact_handlers[text](user_id)

        prefix_handlers = [
            ("/run_batch", self._handle_run_batch),
            ("/report ", self._handle_report),
            ("/enqueue_template ", self._handle_enqueue_template),
            ("/retry_blocked ", self._handle_retry_blocked),
            ("/diff", self._handle_diff),
            ("/evidence ", self._handle_evidence),
            ("/task ", self._handle_task_status),
            ("/enqueue_dev ", self._handle_enqueue_dev),
        ]
        for prefix, handler in prefix_handlers:
            if text.startswith(prefix):
                return handler(user_id, text)

        return {
            "status": "unsupported_command",
            "telegram_user_id": str(user_id),
            "message": (
                "Comando no soportado. Usá /factory_help, /status_factory, /factory_health, "
                "/tasks_pending, /blocked, /retry_blocked <task_id>, /task <task_id>, "
                "/diff <task_id>, /failed_paths, /evidence <task_id>, /enqueue_dev <objetivo>, "
                "/enqueue_template <template> <objetivo>, /templates, /run_one, /run_batch <n>, "
                "/last_report, /run_report_summary, /report <report_id>."
            ),
        }

    def _handle_factory_help(self, user_id: str | int) -> dict:
        payload = build_factory_help_payload()
        return {
            "status": "ok",
            "telegram_user_id": str(user_id),
            "help": payload,
            "message": format_factory_help_message(payload),
        }

    def _handle_status_factory(self, user_id: str | int) -> dict:
        counts = self.store.counts()
        next_task = self.store.next_pending()
        return {
            "status": "ok",
            "telegram_user_id": str(user_id),
            "counts": counts,
            "next_pending_task_id": next_task.task_id if next_task else None,
            "message": self._format_status_message(
                counts, next_task.task_id if next_task else None
            ),
        }

    def _handle_factory_health(self, user_id: str | int) -> dict:
        next_task = self.store.next_pending()
        summary = build_factory_health_summary(
            queue_counts=self.store.counts(),
            next_pending_task_id=next_task.task_id if next_task else None,
            last_report=read_last_factory_run_report(self.evidence_dir),
        )
        return {
            "status": "ok",
            "telegram_user_id": str(user_id),
            "health": summary,
            "message": format_factory_health_summary(summary),
        }

    def _handle_tasks_pending(self, user_id: str | int) -> dict:
        pending = [
            self._serialize_task_summary(task) for task in self.store.list(TaskSpecStatus.PENDING)
        ]
        return {
            "status": "ok",
            "telegram_user_id": str(user_id),
            "pending_count": len(pending),
            "pending_tasks": pending,
            "message": f"Tareas pendientes: {len(pending)}.",
        }

    def _handle_blocked(self, user_id: str | int) -> dict:
        blocked = [
            self._serialize_blocked_task(task) for task in self.store.list(TaskSpecStatus.BLOCKED)
        ]
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
            return self._invalid(user_id, "Formato inválido. Usá /retry_blocked <task_id>.")
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
            return self._invalid(user_id, "Formato inválido. Usá /evidence <task_id>.")
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

    def _handle_diff(self, user_id: str | int, text: str) -> dict:
        parts = text.split(maxsplit=1)
        if len(parts) != 2 or not parts[1].strip():
            return self._invalid(user_id, "Formato inválido. Usá /diff <task_id>.")
        task_id = parts[1].strip()
        report_diff = self._find_changed_paths_in_reports(task_id)
        if report_diff is not None:
            changed_paths, report_id = report_diff
            return self._diff_response(user_id, task_id, changed_paths, "run_report", report_id)
        task = self.store.get(task_id)
        if task is None:
            return {
                "status": "not_found",
                "telegram_user_id": str(user_id),
                "task_id": task_id,
                "changed_paths": [],
                "message": f"Tarea no encontrada: {task_id}.",
            }
        return self._diff_response(
            user_id, task_id, self._find_changed_paths_in_task_evidence(task), "task_evidence", None
        )

    def _handle_last_report(self, user_id: str | int) -> dict:
        report = read_last_factory_run_report(self.evidence_dir)
        if report is None:
            return {
                "status": "not_found",
                "telegram_user_id": str(user_id),
                "message": "No hay reportes de ejecución registrados.",
            }
        return self._report_response(user_id, report)

    def _handle_run_report_summary(self, user_id: str | int) -> dict:
        report = read_last_factory_run_report(self.evidence_dir)
        if report is None:
            return {
                "status": "not_found",
                "telegram_user_id": str(user_id),
                "message": "No hay reportes de ejecución registrados.",
            }
        summary = build_run_report_summary(report)
        return {
            "status": "ok",
            "telegram_user_id": str(user_id),
            "summary": summary,
            "message": format_run_report_summary(summary),
        }

    def _handle_failed_paths(self, user_id: str | int) -> dict:
        report = read_last_factory_run_report(self.evidence_dir)
        if report is None:
            return {
                "status": "not_found",
                "telegram_user_id": str(user_id),
                "message": "No hay reportes de ejecución registrados.",
            }
        summary = build_failed_paths_summary(report)
        return {
            "status": "ok",
            "telegram_user_id": str(user_id),
            "summary": summary,
            "message": format_failed_paths_summary(summary),
        }

    def _handle_report(self, user_id: str | int, text: str) -> dict:
        parts = text.split(maxsplit=1)
        if len(parts) != 2 or not parts[1].strip():
            return self._invalid(user_id, "Formato inválido. Usá /report <report_id>.")
        report_id = parts[1].strip()
        report = read_factory_run_report(report_id, self.evidence_dir)
        if report is None:
            return {
                "status": "not_found",
                "telegram_user_id": str(user_id),
                "report_id": report_id,
                "message": f"Reporte no encontrado: {report_id}.",
            }
        return self._report_response(user_id, report)

    def _handle_templates(self, user_id: str | int) -> dict:
        templates = list_template_names()
        return {
            "status": "ok",
            "telegram_user_id": str(user_id),
            "templates": templates,
            "message": "Templates disponibles: " + ", ".join(templates),
        }

    def _handle_enqueue_template(self, user_id: str | int, text: str) -> dict:
        parsed = _parse_enqueue_template(text)
        if parsed is None:
            return self._invalid(
                user_id, "Formato inválido. Usá /enqueue_template <template> <objetivo>."
            )
        template_name, objective = parsed
        try:
            task = build_task_spec_from_template(
                template_name,
                objective,
                metadata={"origin": "telegram_superowner", "telegram_user_id": str(user_id)},
            )
        except ValueError as exc:
            return {
                "status": "invalid_template",
                "telegram_user_id": str(user_id),
                "template": template_name,
                "message": str(exc),
            }
        path = self.store.enqueue(task)
        queued = {
            "status": "queued",
            "task_id": task.task_id,
            "task_type": "taskspec_template",
            "template": template_name,
            "path": path,
        }
        return {
            "status": "queued",
            "telegram_user_id": str(user_id),
            "task": queued,
            "message": f"TaskSpec template encolada: {task.task_id} ({template_name}).",
        }

    def _handle_task_status(self, user_id: str | int, text: str) -> dict:
        parts = text.split(maxsplit=1)
        if len(parts) != 2 or not parts[1].strip():
            return self._invalid(user_id, "Formato inválido. Usá /task <task_id>.")
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
            return self._invalid(user_id, "Formato inválido. Usá /enqueue_dev <objetivo>.")
        return self._handle_enqueue_template(
            user_id, f"/enqueue_template code_change {parts[1].strip()}"
        )

    def _handle_run_one(self, user_id: str | int) -> dict:
        result = self.runner.run_next()
        if result.task_id is None:
            payload = {"status": "idle", "task_id": None, "reason": result.blocking_reason}
            report, report_paths = self._write_run_report("run_one", 1, [])
            return {
                "status": "idle",
                "telegram_user_id": str(user_id),
                "result": payload,
                "run_report": report.to_dict(),
                "run_report_paths": report_paths,
                "message": self._format_run_message(payload),
            }
        payload = self._serialize_run_result(result)
        report, report_paths = self._write_run_report("run_one", 1, [result])
        return {
            "status": result.status.value,
            "telegram_user_id": str(user_id),
            "result": payload,
            "run_report": report.to_dict(),
            "run_report_paths": report_paths,
            "message": self._format_run_message(payload),
        }

    def _handle_run_batch(self, user_id: str | int, text: str) -> dict:
        parsed = _parse_batch_size(text)
        if parsed is None or parsed < 1 or parsed > MAX_RUN_BATCH_SIZE:
            return self._invalid(
                user_id,
                f"Formato inválido. Usá /run_batch <n>, con 1 <= n <= {MAX_RUN_BATCH_SIZE}.",
            )
        raw_results = []
        for _ in range(parsed):
            result = self.runner.run_next()
            if result.task_id is None:
                break
            raw_results.append(result)
        results = [self._serialize_run_result(result) for result in raw_results]
        done_count = sum(1 for result in results if result["status"] == TaskSpecStatus.DONE.value)
        blocked_count = sum(
            1 for result in results if result["status"] == TaskSpecStatus.BLOCKED.value
        )
        report, report_paths = self._write_run_report("run_batch", parsed, raw_results)
        return {
            "status": "ok",
            "telegram_user_id": str(user_id),
            "requested": parsed,
            "executed_count": len(results),
            "done_count": done_count,
            "blocked_count": blocked_count,
            "results": results,
            "run_report": report.to_dict(),
            "run_report_paths": report_paths,
            "message": self._format_run_batch_message(parsed, results, done_count, blocked_count),
        }

    def _write_run_report(
        self, run_type: str, requested_count: int, results: list[TaskSpecRunResult]
    ):
        report = build_factory_run_report(
            run_type=run_type,
            requested_count=requested_count,
            results=results,
            metadata={"source": "telegram_superowner"},
        )
        return report, write_factory_run_report(report, self.evidence_dir)

    def _report_response(self, user_id: str | int, report: FactoryRunReport) -> dict:
        markdown = read_factory_run_report_markdown(report.report_id, self.evidence_dir) or ""
        truncated = len(markdown) > MAX_REPORT_MARKDOWN_CHARS
        if truncated:
            markdown = markdown[:MAX_REPORT_MARKDOWN_CHARS]
        return {
            "status": "ok",
            "telegram_user_id": str(user_id),
            "report": report.to_dict(),
            "markdown": markdown,
            "truncated": truncated,
            "message": self._format_report_message(report),
        }

    def _diff_response(
        self,
        user_id: str | int,
        task_id: str,
        changed_paths: list[str],
        source: str,
        report_id: str | None,
    ) -> dict:
        return {
            "status": "ok",
            "telegram_user_id": str(user_id),
            "task_id": task_id,
            "source": source,
            "report_id": report_id,
            "changed_paths_count": len(changed_paths),
            "changed_paths": changed_paths,
            "message": self._format_diff_message(task_id, changed_paths, source),
        }

    def _find_changed_paths_in_reports(self, task_id: str) -> tuple[list[str], str] | None:
        reports = sorted(
            list_factory_run_reports(self.evidence_dir),
            key=lambda report: report.created_at,
            reverse=True,
        )
        for report in reports:
            for result in report.task_results:
                if result.task_id == task_id:
                    return list(result.changed_paths), report.report_id
        return None

    def _find_changed_paths_in_task_evidence(self, task: TaskSpec) -> list[str]:
        for evidence_path in task.evidence_paths:
            path = Path(evidence_path)
            if path.name == "paths.txt" and path.exists():
                return _parse_changed_paths_report(path.read_text(encoding="utf-8"))
        return []

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
        return {"path": evidence_path, "exists": exists, "content": content, "truncated": truncated}

    def _extract_user_id(self, update_dict: dict) -> int | str | None:
        return ((update_dict.get("message") or {}).get("from") or {}).get("id")

    def _extract_text(self, update_dict: dict) -> str:
        return ((update_dict.get("message") or {}).get("text") or "").strip()

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

    def _serialize_run_result(self, result: TaskSpecRunResult) -> dict:
        return {
            "status": result.status.value,
            "task_id": result.task_id,
            "evidence_paths": result.evidence_paths,
            "blocking_reason": result.blocking_reason,
            "changed_paths": result.changed_paths,
            "path_errors": result.path_errors,
            "command_results": [
                {
                    "command": item.command,
                    "exit_code": item.exit_code,
                    "stdout": item.stdout,
                    "stderr": item.stderr,
                }
                for item in result.command_results
            ],
        }

    def _invalid(self, user_id: str | int, message: str) -> dict:
        return {"status": "invalid_command", "telegram_user_id": str(user_id), "message": message}

    def _format_status_message(self, counts: dict, next_pending_task_id: str | None) -> str:
        return (
            f"Factoría: pending={counts.get('pending', 0)}, "
            f"in_progress={counts.get('in_progress', 0)}, "
            f"done={counts.get('done', 0)}, blocked={counts.get('blocked', 0)}. "
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

    def _format_run_batch_message(
        self, requested: int, results: list[dict], done_count: int, blocked_count: int
    ) -> str:
        return (
            f"Run batch solicitado={requested}, ejecutado={len(results)}, "
            f"done={done_count}, blocked={blocked_count}."
        )

    def _format_report_message(self, report: FactoryRunReport) -> str:
        return (
            f"Reporte {report.report_id}: type={report.run_type}, "
            f"executed={report.executed_count}, done={report.done_count}, "
            f"blocked={report.blocked_count}, idle={report.idle}."
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

    def _format_diff_message(self, task_id: str, changed_paths: list[str], source: str) -> str:
        if not changed_paths:
            return f"Diff para {task_id}: 0 archivos modificados registrados en {source}."
        return f"Diff para {task_id}: {len(changed_paths)} archivos desde {source}: " + ", ".join(
            changed_paths
        )


def _parse_batch_size(text: str) -> int | None:
    parts = text.split()
    if len(parts) != 2 or parts[0] != "/run_batch":
        return None
    try:
        return int(parts[1])
    except ValueError:
        return None


def _parse_enqueue_template(text: str) -> tuple[str, str] | None:
    parts = text.split(maxsplit=2)
    if len(parts) != 3 or parts[0] != "/enqueue_template":
        return None
    template_name = parts[1].strip()
    objective = parts[2].strip()
    if not template_name or not objective:
        return None
    return template_name, objective


def _parse_changed_paths_report(content: str) -> list[str]:
    changed_paths: list[str] = []
    in_changed_paths = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped == "changed_paths:":
            in_changed_paths = True
            continue
        if stripped == "path_errors:":
            break
        if in_changed_paths and stripped:
            changed_paths.append(stripped)
    return changed_paths
