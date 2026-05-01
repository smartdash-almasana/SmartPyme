from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from factory.core.git_diff_detector import get_changed_paths
from factory.core.task_spec import TaskSpec, TaskSpecStatus, validate_changed_paths
from factory.core.task_spec_store import TaskSpecStore

ChangedPathsProvider = Callable[[TaskSpec], list[str]]
CommandRunner = Callable[[str], "CommandResult"]


@dataclass(frozen=True)
class CommandResult:
    command: str
    exit_code: int
    stdout: str = ""
    stderr: str = ""

    @property
    def ok(self) -> bool:
        return self.exit_code == 0


@dataclass(frozen=True)
class TaskSpecRunResult:
    status: TaskSpecStatus
    task_id: str | None
    evidence_paths: list[str] = field(default_factory=list)
    blocking_reason: str | None = None
    command_results: list[CommandResult] = field(default_factory=list)
    changed_paths: list[str] = field(default_factory=list)
    path_errors: list[str] = field(default_factory=list)


class TaskSpecRunner:
    def __init__(
        self,
        store: TaskSpecStore,
        evidence_dir: str | Path = Path("factory/evidence/taskspecs"),
        changed_paths_provider: ChangedPathsProvider | None = None,
        command_runner: CommandRunner | None = None,
    ) -> None:
        self.store = store
        self.evidence_dir = Path(evidence_dir)
        self.changed_paths_provider = changed_paths_provider
        self.command_runner = command_runner or run_shell_command

    def run_next(self) -> TaskSpecRunResult:
        task = self.store.next_pending()
        if task is None:
            return TaskSpecRunResult(
                status=TaskSpecStatus.PENDING, task_id=None, blocking_reason="NO_PENDING_TASK"
            )
        return self.run_task(task.task_id)

    def run_task(self, task_id: str) -> TaskSpecRunResult:
        try:
            task = self.store.mark_in_progress(task_id)
        except FileNotFoundError:
            return TaskSpecRunResult(
                status=TaskSpecStatus.BLOCKED, task_id=task_id, blocking_reason="TASK_NOT_FOUND"
            )
        except ValueError as exc:
            return TaskSpecRunResult(
                status=TaskSpecStatus.BLOCKED, task_id=task_id, blocking_reason=str(exc)
            )

        evidence_dir = self.evidence_dir / task.task_id
        evidence_dir.mkdir(parents=True, exist_ok=True)

        command_results = [self.command_runner(command) for command in task.validation_commands]
        command_report_path = self._write_command_report(task, evidence_dir, command_results)

        changed_paths = (
            self.changed_paths_provider(task)
            if self.changed_paths_provider is not None
            else get_changed_paths()
        )
        path_validation = validate_changed_paths(task, changed_paths)
        path_report_path = self._write_path_report(
            task, evidence_dir, changed_paths, path_validation.errors
        )

        evidence_paths = [command_report_path, path_report_path]

        failed_commands = [result.command for result in command_results if not result.ok]
        if failed_commands:
            blocking_reason = "VALIDATION_COMMAND_FAILED: " + "; ".join(failed_commands)
            self.store.mark_blocked(task.task_id, blocking_reason)
            return TaskSpecRunResult(
                status=TaskSpecStatus.BLOCKED,
                task_id=task.task_id,
                evidence_paths=evidence_paths,
                blocking_reason=blocking_reason,
                command_results=command_results,
                changed_paths=changed_paths,
                path_errors=path_validation.errors,
            )

        if not path_validation.valid:
            blocking_reason = "PATH_VALIDATION_FAILED"
            self.store.mark_blocked(task.task_id, blocking_reason)
            return TaskSpecRunResult(
                status=TaskSpecStatus.BLOCKED,
                task_id=task.task_id,
                evidence_paths=evidence_paths,
                blocking_reason=blocking_reason,
                command_results=command_results,
                changed_paths=changed_paths,
                path_errors=path_validation.errors,
            )

        self.store.mark_done(task.task_id, evidence_paths=evidence_paths)
        return TaskSpecRunResult(
            status=TaskSpecStatus.DONE,
            task_id=task.task_id,
            evidence_paths=evidence_paths,
            command_results=command_results,
            changed_paths=changed_paths,
            path_errors=[],
        )

    def _write_command_report(
        self,
        task: TaskSpec,
        evidence_dir: Path,
        command_results: list[CommandResult],
    ) -> str:
        path = evidence_dir / "commands.txt"
        lines = [f"task_id={task.task_id}", "section=validation_commands"]
        for result in command_results:
            lines.extend(
                [
                    "---",
                    f"command={result.command}",
                    f"exit_code={result.exit_code}",
                    "stdout:",
                    result.stdout,
                    "stderr:",
                    result.stderr,
                ]
            )
        path.write_text("\n".join(lines), encoding="utf-8")
        return str(path)

    def _write_path_report(
        self,
        task: TaskSpec,
        evidence_dir: Path,
        changed_paths: list[str],
        errors: list[str],
    ) -> str:
        path = evidence_dir / "paths.txt"
        lines = [
            f"task_id={task.task_id}",
            "section=changed_paths",
            "changed_paths:",
            *changed_paths,
            "path_errors:",
            *errors,
        ]
        path.write_text("\n".join(lines), encoding="utf-8")
        return str(path)


def run_shell_command(command: str) -> CommandResult:
    completed = subprocess.run(
        command,
        shell=True,
        text=True,
        capture_output=True,
        check=False,
    )
    return CommandResult(
        command=command,
        exit_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )
