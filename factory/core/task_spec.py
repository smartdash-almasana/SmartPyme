from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class TaskSpecStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class TaskSpec:
    task_id: str
    title: str
    objective: str
    allowed_paths: list[str]
    forbidden_paths: list[str]
    acceptance_criteria: list[str]
    validation_commands: list[str]
    status: TaskSpecStatus = TaskSpecStatus.PENDING
    evidence_paths: list[str] = field(default_factory=list)
    blocking_reason: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _require_non_empty(self.task_id, "task_id")
        _require_non_empty(self.title, "title")
        _require_non_empty(self.objective, "objective")
        _require_non_empty_list(self.allowed_paths, "allowed_paths")
        _require_non_empty_list(self.acceptance_criteria, "acceptance_criteria")
        _require_non_empty_list(self.validation_commands, "validation_commands")
        _require_string_list(self.forbidden_paths, "forbidden_paths")
        _require_string_list(self.evidence_paths, "evidence_paths")

        if not isinstance(self.status, TaskSpecStatus):
            object.__setattr__(self, "status", TaskSpecStatus(self.status))

        if self.status == TaskSpecStatus.BLOCKED and not self.blocking_reason:
            raise ValueError("blocking_reason is required when status is blocked")

        if self.status == TaskSpecStatus.DONE and not self.evidence_paths:
            raise ValueError("evidence_paths is required when status is done")

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def with_status(
        self,
        status: TaskSpecStatus | str,
        *,
        evidence_paths: list[str] | None = None,
        blocking_reason: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> "TaskSpec":
        next_status = status if isinstance(status, TaskSpecStatus) else TaskSpecStatus(status)
        return TaskSpec(
            task_id=self.task_id,
            title=self.title,
            objective=self.objective,
            allowed_paths=list(self.allowed_paths),
            forbidden_paths=list(self.forbidden_paths),
            acceptance_criteria=list(self.acceptance_criteria),
            validation_commands=list(self.validation_commands),
            status=next_status,
            evidence_paths=list(evidence_paths if evidence_paths is not None else self.evidence_paths),
            blocking_reason=blocking_reason,
            metadata=dict(metadata if metadata is not None else self.metadata),
        )


@dataclass(frozen=True)
class TaskSpecValidationResult:
    valid: bool
    errors: list[str] = field(default_factory=list)


def task_spec_from_dict(data: dict[str, Any]) -> TaskSpec:
    return TaskSpec(
        task_id=data["task_id"],
        title=data["title"],
        objective=data["objective"],
        allowed_paths=list(data.get("allowed_paths") or []),
        forbidden_paths=list(data.get("forbidden_paths") or []),
        acceptance_criteria=list(data.get("acceptance_criteria") or []),
        validation_commands=list(data.get("validation_commands") or []),
        status=TaskSpecStatus(data.get("status", TaskSpecStatus.PENDING.value)),
        evidence_paths=list(data.get("evidence_paths") or []),
        blocking_reason=data.get("blocking_reason"),
        metadata=dict(data.get("metadata") or {}),
    )


def task_spec_from_json(content: str) -> TaskSpec:
    return task_spec_from_dict(json.loads(content))


def validate_changed_paths(task: TaskSpec, changed_paths: list[str]) -> TaskSpecValidationResult:
    errors: list[str] = []
    for changed_path in changed_paths:
        normalized = _normalize_path(changed_path)
        if _matches_any(normalized, task.forbidden_paths):
            errors.append(f"FORBIDDEN_PATH_MODIFIED: {changed_path}")
        if not _matches_any(normalized, task.allowed_paths):
            errors.append(f"PATH_NOT_ALLOWED: {changed_path}")
    return TaskSpecValidationResult(valid=not errors, errors=errors)


def write_task_spec(task: TaskSpec, path: str | Path) -> str:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(task.to_json(), encoding="utf-8")
    return str(target)


def read_task_spec(path: str | Path) -> TaskSpec:
    return task_spec_from_json(Path(path).read_text(encoding="utf-8"))


def _require_non_empty(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required")


def _require_non_empty_list(value: list[str], field_name: str) -> None:
    _require_string_list(value, field_name)
    if not value:
        raise ValueError(f"{field_name} must not be empty")


def _require_string_list(value: list[str], field_name: str) -> None:
    if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
        raise ValueError(f"{field_name} must be a list of non-empty strings")


def _normalize_path(value: str) -> str:
    return value.replace("\\", "/").strip().lstrip("./")


def _matches_any(path: str, patterns: list[str]) -> bool:
    normalized_patterns = [_normalize_path(pattern) for pattern in patterns]
    return any(path == pattern or path.startswith(f"{pattern.rstrip('/')}/") for pattern in normalized_patterns)
