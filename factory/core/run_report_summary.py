from __future__ import annotations

from typing import Any

from factory.core.run_report import FactoryRunReport


def build_run_report_summary(report: FactoryRunReport) -> dict[str, Any]:
    changed_paths = sorted(
        {
            path
            for result in report.task_results
            for path in result.changed_paths
        }
    )
    affected_tasks = [
        {
            "task_id": result.task_id,
            "status": result.status,
            "blocking_reason": result.blocking_reason,
            "changed_paths_count": len(result.changed_paths),
            "changed_paths": list(result.changed_paths),
        }
        for result in report.task_results
    ]
    return {
        "report_id": report.report_id,
        "run_type": report.run_type,
        "requested_count": report.requested_count,
        "executed_count": report.executed_count,
        "done_count": report.done_count,
        "blocked_count": report.blocked_count,
        "idle": report.idle,
        "task_ids": [result.task_id for result in report.task_results],
        "blocked_task_ids": [
            result.task_id
            for result in report.task_results
            if result.status == "blocked"
        ],
        "changed_paths_count": len(changed_paths),
        "changed_paths": changed_paths,
        "affected_tasks": affected_tasks,
    }


def build_failed_paths_summary(report: FactoryRunReport) -> dict[str, Any]:
    failed_tasks = [
        {
            "task_id": result.task_id,
            "status": result.status,
            "blocking_reason": result.blocking_reason,
            "path_errors_count": len(result.path_errors),
            "path_errors": list(result.path_errors),
        }
        for result in report.task_results
        if result.path_errors
    ]
    all_path_errors = [
        error
        for task in failed_tasks
        for error in task["path_errors"]
    ]
    return {
        "report_id": report.report_id,
        "run_type": report.run_type,
        "executed_count": report.executed_count,
        "blocked_count": report.blocked_count,
        "failed_tasks_count": len(failed_tasks),
        "path_errors_count": len(all_path_errors),
        "path_errors": all_path_errors,
        "failed_tasks": failed_tasks,
    }


def build_factory_health_summary(
    *,
    queue_counts: dict[str, int],
    next_pending_task_id: str | None,
    last_report: FactoryRunReport | None,
) -> dict[str, Any]:
    if last_report is None:
        return {
            "queue_counts": dict(queue_counts),
            "next_pending_task_id": next_pending_task_id,
            "has_report": False,
            "last_report": None,
            "changed_paths_count": 0,
            "changed_paths": [],
            "path_errors_count": 0,
            "path_errors": [],
            "health_status": _derive_health_status(queue_counts, None, 0),
        }

    report_summary = build_run_report_summary(last_report)
    failed_summary = build_failed_paths_summary(last_report)
    return {
        "queue_counts": dict(queue_counts),
        "next_pending_task_id": next_pending_task_id,
        "has_report": True,
        "last_report": {
            "report_id": last_report.report_id,
            "run_type": last_report.run_type,
            "executed_count": last_report.executed_count,
            "done_count": last_report.done_count,
            "blocked_count": last_report.blocked_count,
            "idle": last_report.idle,
            "created_at": last_report.created_at,
        },
        "changed_paths_count": report_summary["changed_paths_count"],
        "changed_paths": report_summary["changed_paths"],
        "path_errors_count": failed_summary["path_errors_count"],
        "path_errors": failed_summary["path_errors"],
        "failed_tasks": failed_summary["failed_tasks"],
        "health_status": _derive_health_status(
            queue_counts,
            last_report,
            failed_summary["path_errors_count"],
        ),
    }


def format_run_report_summary(summary: dict[str, Any]) -> str:
    if summary["idle"]:
        return f"Último reporte {summary['report_id']}: idle, sin tareas ejecutadas."

    changed_paths = summary["changed_paths"]
    changed_part = "sin archivos modificados" if not changed_paths else ", ".join(changed_paths)
    return (
        f"Último reporte {summary['report_id']}: "
        f"type={summary['run_type']}, "
        f"executed={summary['executed_count']}, "
        f"done={summary['done_count']}, "
        f"blocked={summary['blocked_count']}, "
        f"changed_paths={summary['changed_paths_count']} ({changed_part})."
    )


def format_failed_paths_summary(summary: dict[str, Any]) -> str:
    if summary["path_errors_count"] == 0:
        return f"Último reporte {summary['report_id']}: sin path_errors registrados."

    task_parts = [
        f"{task['task_id']}={task['path_errors_count']}"
        for task in summary["failed_tasks"]
    ]
    return (
        f"Último reporte {summary['report_id']}: "
        f"path_errors={summary['path_errors_count']}, "
        f"failed_tasks={summary['failed_tasks_count']} "
        f"({', '.join(task_parts)})."
    )


def format_factory_health_summary(summary: dict[str, Any]) -> str:
    counts = summary["queue_counts"]
    report = summary["last_report"]
    report_part = "sin reportes" if report is None else (
        f"last_report={report['report_id']} executed={report['executed_count']} "
        f"done={report['done_count']} blocked={report['blocked_count']}"
    )
    return (
        f"Factory health: status={summary['health_status']}; "
        f"queue pending={counts.get('pending', 0)}, in_progress={counts.get('in_progress', 0)}, "
        f"done={counts.get('done', 0)}, blocked={counts.get('blocked', 0)}; "
        f"next={summary['next_pending_task_id'] or 'none'}; "
        f"{report_part}; "
        f"changed_paths={summary['changed_paths_count']}; "
        f"path_errors={summary['path_errors_count']}."
    )


def _derive_health_status(
    queue_counts: dict[str, int],
    last_report: FactoryRunReport | None,
    path_errors_count: int,
) -> str:
    if path_errors_count > 0:
        return "attention_required"
    if queue_counts.get("blocked", 0) > 0:
        return "blocked_tasks"
    if last_report is not None and last_report.blocked_count > 0:
        return "last_run_blocked"
    if queue_counts.get("pending", 0) > 0:
        return "pending_work"
    return "ok"
