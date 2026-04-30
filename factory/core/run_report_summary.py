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
