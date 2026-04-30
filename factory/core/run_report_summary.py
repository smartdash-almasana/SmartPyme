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
