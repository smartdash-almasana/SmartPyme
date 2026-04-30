from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from factory.core.task_spec import TaskSpecStatus
from factory.core.task_spec_runner import TaskSpecRunResult


@dataclass(frozen=True)
class FactoryTaskRunSummary:
    task_id: str | None
    status: str
    evidence_paths: list[str] = field(default_factory=list)
    blocking_reason: str | None = None
    command_exit_codes: list[int] = field(default_factory=list)
    path_errors: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class FactoryRunReport:
    report_id: str
    run_type: str
    requested_count: int
    executed_count: int
    done_count: int
    blocked_count: int
    idle: bool
    task_results: list[FactoryTaskRunSummary]
    created_at: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def to_markdown(self) -> str:
        lines = [
            f"# Factory Run Report {self.report_id}",
            "",
            f"- run_type: {self.run_type}",
            f"- requested_count: {self.requested_count}",
            f"- executed_count: {self.executed_count}",
            f"- done_count: {self.done_count}",
            f"- blocked_count: {self.blocked_count}",
            f"- idle: {self.idle}",
            f"- created_at: {self.created_at}",
            "",
            "## Task Results",
        ]
        if not self.task_results:
            lines.append("- No task executed.")
            return "\n".join(lines)

        for result in self.task_results:
            lines.extend(
                [
                    f"### {result.task_id}",
                    f"- status: {result.status}",
                    f"- blocking_reason: {result.blocking_reason or 'none'}",
                    f"- command_exit_codes: {result.command_exit_codes}",
                    f"- path_errors: {result.path_errors}",
                    "- evidence_paths:",
                ]
            )
            if result.evidence_paths:
                lines.extend(f"  - {path}" for path in result.evidence_paths)
            else:
                lines.append("  - none")
        return "\n".join(lines)


def build_factory_run_report(
    *,
    run_type: str,
    requested_count: int,
    results: list[TaskSpecRunResult],
    metadata: dict[str, Any] | None = None,
) -> FactoryRunReport:
    summaries = [_summarize_task_result(result) for result in results if result.task_id is not None]
    done_count = sum(1 for item in summaries if item.status == TaskSpecStatus.DONE.value)
    blocked_count = sum(1 for item in summaries if item.status == TaskSpecStatus.BLOCKED.value)
    return FactoryRunReport(
        report_id=f"factory-run-{uuid4()}",
        run_type=run_type,
        requested_count=requested_count,
        executed_count=len(summaries),
        done_count=done_count,
        blocked_count=blocked_count,
        idle=len(summaries) == 0,
        task_results=summaries,
        created_at=datetime.now(timezone.utc).isoformat(),
        metadata=dict(metadata or {}),
    )


def write_factory_run_report(report: FactoryRunReport, evidence_dir: str | Path) -> dict[str, str]:
    directory = Path(evidence_dir) / "run_reports"
    directory.mkdir(parents=True, exist_ok=True)
    json_path = directory / f"{report.report_id}.json"
    md_path = directory / f"{report.report_id}.md"
    json_path.write_text(report.to_json(), encoding="utf-8")
    md_path.write_text(report.to_markdown(), encoding="utf-8")
    return {"json_path": str(json_path), "markdown_path": str(md_path)}


def _summarize_task_result(result: TaskSpecRunResult) -> FactoryTaskRunSummary:
    return FactoryTaskRunSummary(
        task_id=result.task_id,
        status=result.status.value,
        evidence_paths=list(result.evidence_paths),
        blocking_reason=result.blocking_reason,
        command_exit_codes=[command.exit_code for command in result.command_results],
        path_errors=list(result.path_errors),
    )
