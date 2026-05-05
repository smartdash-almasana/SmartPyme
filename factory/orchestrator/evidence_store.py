from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from factory.core.task_spec import TaskSpec

EVIDENCE_MANIFEST_FILENAME = "evidence_manifest.json"
EXECUTION_RESULT_FILENAME = "execution_result.json"
AUDIT_DECISION_FILENAME = "audit_decision.json"
HUMAN_ESCALATION_FILENAME = "human_escalation.json"
MINIMUM_EVIDENCE_FILES = (
    "cycle.md",
    "commands.txt",
    "git_status.txt",
    "git_diff.patch",
    "tests.txt",
    "decision.txt",
)


@dataclass(frozen=True)
class EvidenceStore:
    repo_root: Path

    @property
    def evidence_root(self) -> Path:
        return self.repo_root / "factory" / "evidence"

    def evidence_dir(self, task_id: str) -> Path:
        safe_id = _safe_hallazgo_id(task_id)
        directory = self.evidence_root / safe_id
        directory.mkdir(parents=True, exist_ok=True)
        return directory

    def write_text(self, task_id: str, filename: str, content: str) -> Path:
        path = self.evidence_dir(task_id) / filename
        path.write_text(content, encoding="utf-8")
        return path

    def write_json(self, task_id: str, filename: str, data: dict[str, Any]) -> Path:
        path = self.evidence_dir(task_id) / filename
        path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True),
            encoding="utf-8",
        )
        return path

    def write_cycle_evidence(
        self,
        task: TaskSpec,
        final_status: str,
        blocking_reason: str | None,
        gate_status: str | None = None,
    ) -> None:
        lines = [
            f"# Sovereign TaskLoop Cycle: {task.task_id}",
            "",
            f"task_id: {task.task_id}",
            f"title: {task.title}",
            f"status: {final_status}",
            f"operational_mode: {task.metadata.get('operational_mode')}",
            f"model_target: {task.metadata.get('model_target')}",
            f"gate_status_start: {gate_status or 'recorded_in_initial_cycle'}",
            f"blocking_reason: {blocking_reason or ''}",
        ]
        self.write_text(task.task_id, "cycle.md", "\n".join(lines) + "\n")

    def write_command_evidence(
        self, task_id: str, command_results: list[dict[str, object]]
    ) -> None:
        if not command_results:
            return

        command_lines: list[str] = []
        test_lines: list[str] = []
        for result in command_results:
            block = [
                f"$ {result['command']}",
                f"returncode={result['returncode']}",
                "stdout:",
                str(result["stdout"]),
                "stderr:",
                str(result["stderr"]),
                "---",
            ]
            command_lines.extend(block)
            test_lines.extend(block)

        self.write_text(task_id, "commands.txt", "\n".join(command_lines))
        self.write_text(task_id, "tests.txt", "\n".join(test_lines))

    def write_git_evidence(self, task_id: str, git_status: str, git_diff: str) -> None:
        self.write_text(task_id, "git_status.txt", git_status)
        self.write_text(task_id, "git_diff.patch", git_diff)

    def write_decision_evidence(
        self, task_id: str, final_status: str, blocking_reason: str | None
    ) -> None:
        content = f"status={final_status}\nblocking_reason={blocking_reason or ''}\n"
        self.write_text(task_id, "decision.txt", content)

    def write_execution_result(
        self,
        *,
        task: TaskSpec,
        final_status: str,
        blocking_reason: str | None,
        command_results: list[dict[str, object]],
        started_at: str,
        finished_at: str,
        branch: str,
        commit_hash: str,
    ) -> Path:
        task_evidence_dir = self.evidence_dir(task.task_id)
        result = {
            "task_id": task.task_id,
            "status": final_status,
            "executor_real": (
                task.metadata.get("executor_target")
                or task.metadata.get("executor")
                or "UNKNOWN"
            ),
            "model_real": task.metadata.get("model_target"),
            "provider_real": task.metadata.get("provider_target"),
            "started_at": started_at,
            "finished_at": finished_at,
            "commands_run": [
                {
                    "command": command_result["command"],
                    "returncode": command_result["returncode"],
                    "stdout_path": str(task_evidence_dir / "commands.txt"),
                    "stderr_path": str(task_evidence_dir / "commands.txt"),
                }
                for command_result in command_results
            ],
            "files_changed": _changed_files_from_git_status(
                task_evidence_dir / "git_status.txt"
            ),
            "commit_hash": commit_hash,
            "branch": branch,
            "push_status": "not_applicable_in_local_runner",
            "blocking_reason": blocking_reason,
        }
        return self.write_json(task.task_id, EXECUTION_RESULT_FILENAME, result)

    def write_evidence_manifest(
        self,
        *,
        task: TaskSpec,
        branch: str,
        commit_hash: str,
        gate_status_after: str,
    ) -> Path:
        task_evidence_dir = self.evidence_dir(task.task_id)
        required_files = {
            name: str(task_evidence_dir / name) for name in MINIMUM_EVIDENCE_FILES
        }
        manifest = {
            "task_id": task.task_id,
            "evidence_dir": str(task_evidence_dir),
            "required_files": required_files,
            "commit_hash": commit_hash,
            "branch": branch,
            "gate_status_after": gate_status_after,
            "complete": all(Path(path).exists() for path in required_files.values()),
        }
        return self.write_json(task.task_id, EVIDENCE_MANIFEST_FILENAME, manifest)

    def write_audit_decision(
        self,
        *,
        task: TaskSpec,
        final_status: str,
        blocking_reason: str | None,
        commit_hash: str,
        manifest_path: Path,
    ) -> Path:
        escalation_needed = self._human_escalation_required(task, blocking_reason)
        decision = "PASS" if final_status == "done" else "BLOCKED"
        if escalation_needed:
            decision = "HUMAN_REQUIRED"
        result = {
            "task_id": task.task_id,
            "decision": decision,
            "auditor": "sovereign_task_loop_v1",
            "checked_commit": commit_hash,
            "checked_evidence_dir": str(self.evidence_dir(task.task_id)),
            "checked_evidence_manifest": str(manifest_path),
            "summary": self._audit_summary(decision, blocking_reason),
            "risks": [] if decision == "PASS" else [blocking_reason],
            "required_human_action": escalation_needed,
            "next_gate_status": "OPEN" if decision == "PASS" else "WAITING_AUDIT",
            "next_milestone": task.metadata.get("next_milestone"),
        }
        return self.write_json(task.task_id, AUDIT_DECISION_FILENAME, result)

    def write_human_escalation_if_required(
        self,
        *,
        task: TaskSpec,
        blocking_reason: str | None,
    ) -> Path | None:
        if not self._human_escalation_required(task, blocking_reason):
            return None
        escalation_type = str(task.metadata.get("escalation_type") or "HUMAN_REQUIRED")
        reason = str(
            task.metadata.get("human_reason")
            or blocking_reason
            or "Human decision required"
        )
        result = {
            "task_id": task.task_id,
            "escalation_type": escalation_type,
            "severity": str(task.metadata.get("human_severity") or "HIGH"),
            "reason": reason,
            "decision_needed": str(task.metadata.get("decision_needed") or reason),
            "options": list(
                task.metadata.get("human_options") or ["APPROVE", "STOP_FACTORY"]
            ),
            "recommended_option": task.metadata.get("recommended_option"),
            "safe_to_continue": bool(task.metadata.get("safe_to_continue", False)),
        }
        return self.write_json(task.task_id, HUMAN_ESCALATION_FILENAME, result)

    def _human_escalation_required(
        self, task: TaskSpec, blocking_reason: str | None
    ) -> bool:
        if bool(task.metadata.get("human_required")):
            return True
        reason = (blocking_reason or "").lower()
        return any(
            token in reason
            for token in ("secret", "credential", "token", "key", "billing")
        )

    def _audit_summary(self, decision: str, blocking_reason: str | None) -> str:
        if decision == "PASS":
            return "Sovereign TaskLoop cycle completed with required evidence."
        if decision == "HUMAN_REQUIRED":
            return f"Sovereign TaskLoop cycle requires human decision: {blocking_reason}"
        return f"Sovereign TaskLoop cycle blocked: {blocking_reason}"


def _safe_hallazgo_id(value: str) -> str:
    cleaned = "".join(
        ch if ch.isalnum() or ch in {"-", "_", "."} else "-" for ch in value.strip()
    )
    return cleaned or "unknown-hallazgo"


def _changed_files_from_git_status(git_status_path: Path) -> list[str]:
    if not git_status_path.exists():
        return []
    changed: list[str] = []
    for line in git_status_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        changed.append(line[3:].strip() if len(line) > 3 else line.strip())
    return changed
