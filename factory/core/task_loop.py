import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Callable


@dataclass
class MultiagentTask:
    task_id: str
    objective: str
    status: str = "pending"
    task_type: str | None = None
    payload: dict = field(default_factory=dict)
    plan: list[str] = field(default_factory=list)
    output: dict | None = None
    audit: dict | None = None
    report_path: str | None = None
    blocking_reason: str | None = None


Planner = Callable[[MultiagentTask], list[str]]
Builder = Callable[[MultiagentTask], dict]
Auditor = Callable[[MultiagentTask], dict]
Reporter = Callable[[MultiagentTask, Path], str]


def task_to_dict(task: MultiagentTask) -> dict:
    return asdict(task)


def task_from_dict(data: dict) -> MultiagentTask:
    return MultiagentTask(
        task_id=data["task_id"],
        objective=data["objective"],
        status=data.get("status", "pending"),
        task_type=data.get("task_type"),
        payload=data.get("payload") or {},
        plan=data.get("plan", []),
        output=data.get("output"),
        audit=data.get("audit"),
        report_path=data.get("report_path"),
        blocking_reason=data.get("blocking_reason"),
    )


def save_task(task: MultiagentTask, tasks_dir: str | Path) -> str:
    target_dir = Path(tasks_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / f"{_safe_path_segment(task.task_id)}.json"
    path.write_text(json.dumps(task_to_dict(task), ensure_ascii=False, indent=2), encoding="utf-8")
    return str(path)


def load_task(task_id: str, tasks_dir: str | Path) -> MultiagentTask | None:
    path = Path(tasks_dir) / f"{_safe_path_segment(task_id)}.json"
    if not path.exists():
        return None
    return task_from_dict(json.loads(path.read_text(encoding="utf-8")))


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
    path = evidence_dir / f"{_safe_path_segment(task.task_id)}.txt"
    path.write_text(
        "\n".join([
            f"task_id={task.task_id}",
            f"status={task.status}",
            f"objective={task.objective}",
            f"task_type={task.task_type}",
            f"payload={task.payload}",
            f"plan={task.plan}",
            f"output={task.output}",
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


def run_persisted_multiagent_task_cycle(
    task_id: str,
    tasks_dir: str | Path,
    evidence_dir: str | Path,
    planner: Planner = default_planner,
    builder: Builder = default_builder,
    auditor: Auditor = default_auditor,
    reporter: Reporter = default_reporter,
) -> MultiagentTask | None:
    task = load_task(task_id, tasks_dir)
    if task is None:
        return None

    result = run_multiagent_task_cycle(
        task,
        evidence_dir,
        planner=planner,
        builder=builder,
        auditor=auditor,
        reporter=reporter,
    )
    save_task(result, tasks_dir)
    return result


_WINDOWS_FORBIDDEN_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1F]')


def _safe_path_segment(value: str) -> str:
    text = str(value).strip()
    if not text:
        return "task"

    # Windows-safe file segment while preserving readable intent.
    sanitized = _WINDOWS_FORBIDDEN_CHARS.sub("-", text)
    sanitized = re.sub(r"\s+", "_", sanitized)
    sanitized = sanitized.rstrip(". ")
    return sanitized or "task"
