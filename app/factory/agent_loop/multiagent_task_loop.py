from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable


@dataclass
class MultiagentTask:
    task_id: str
    objective: str
    status: str = "pending"
    plan: list[str] = field(default_factory=list)
    output: dict | None = None
    audit: dict | None = None
    report_path: str | None = None
    blocking_reason: str | None = None


Planner = Callable[[MultiagentTask], list[str]]
Builder = Callable[[MultiagentTask], dict]
Auditor = Callable[[MultiagentTask], dict]
Reporter = Callable[[MultiagentTask, Path], str]


def default_planner(task: MultiagentTask) -> list[str]:
    return [task.objective]


def default_builder(task: MultiagentTask) -> dict:
    return {"status": "built", "task_id": task.task_id, "objective": task.objective}


def default_auditor(task: MultiagentTask) -> dict:
    if task.output is None:
        return {"status": "blocked", "reason": "OUTPUT_MISSING"}
    return {"status": "passed", "reason": "AUDIT_OK"}


def default_reporter(task: MultiagentTask, evidence_dir: Path) -> str:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    path = evidence_dir / f"{task.task_id}.txt"
    path.write_text(
        "\n".join([
            f"task_id={task.task_id}",
            f"status={task.status}",
            f"objective={task.objective}",
            f"plan={task.plan}",
            f"audit={task.audit}",
        ]),
        encoding="utf-8",
    )
    return str(path)


def run_multiagent_task_cycle(
    task: MultiagentTask,
    evidence_dir: str | Path,
    planner: Planner = default_planner,
    builder: Builder = default_builder,
    auditor: Auditor = default_auditor,
    reporter: Reporter = default_reporter,
) -> MultiagentTask:
    if task.status != "pending":
        task.status = "blocked"
        task.blocking_reason = "TASK_NOT_PENDING"
        task.report_path = reporter(task, Path(evidence_dir))
        return task

    task.status = "in_progress"
    task.plan = planner(task)
    task.output = builder(task)
    task.audit = auditor(task)

    if task.audit.get("status") != "passed":
        task.status = "blocked"
        task.blocking_reason = task.audit.get("reason", "AUDIT_FAILED")
    else:
        task.status = "done"

    task.report_path = reporter(task, Path(evidence_dir))
    return task
