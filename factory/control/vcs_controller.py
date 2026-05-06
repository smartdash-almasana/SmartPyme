from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from factory.core.task_spec import TaskSpec, validate_changed_paths


@dataclass(frozen=True)
class CommitPlan:
    task_id: str
    branch: str
    base_commit: str
    changed_files: list[str]
    allowed_paths_valid: bool
    evidence_manifest_complete: bool
    commit_message: str
    pr_title: str
    pr_body: str
    blocked: bool
    blocking_reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "branch": self.branch,
            "base_commit": self.base_commit,
            "changed_files": self.changed_files,
            "allowed_paths_valid": self.allowed_paths_valid,
            "evidence_manifest_complete": self.evidence_manifest_complete,
            "commit_message": self.commit_message,
            "pr_title": self.pr_title,
            "pr_body": self.pr_body,
            "blocked": self.blocked,
            "blocking_reasons": self.blocking_reasons,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)


def create_commit_plan(
    task: TaskSpec,
    changed_files: list[str],
    evidence_manifest: dict[str, Any],
    branch: str,
    base_commit: str,
) -> CommitPlan:
    blocking_reasons: list[str] = []

    path_validation = validate_changed_paths(task, changed_files)
    if not path_validation.valid:
        blocking_reasons.extend(path_validation.errors)

    if not evidence_manifest.get("complete", False):
        blocking_reasons.append("EVIDENCE_MANIFEST_INCOMPLETE")

    if not changed_files:
        blocking_reasons.append("NO_CHANGED_FILES")

    commit_message = f"feat({task.metadata.get('module', 'default')}): {task.title}\n\n{task.objective}"
    pr_title = f"feat({task.metadata.get('module', 'default')}): {task.title}"
    pr_body = f"Tarea: {task.task_id}\n\n{task.objective}"

    return CommitPlan(
        task_id=task.task_id,
        branch=branch,
        base_commit=base_commit,
        changed_files=changed_files,
        allowed_paths_valid=path_validation.valid,
        evidence_manifest_complete=evidence_manifest.get("complete", False),
        commit_message=commit_message,
        pr_title=pr_title,
        pr_body=pr_body,
        blocked=bool(blocking_reasons),
        blocking_reasons=blocking_reasons,
    )
