from __future__ import annotations

from pathlib import Path

from factory.core.task_spec import TaskSpec, TaskSpecStatus, read_task_spec, write_task_spec


STATE_DIRS = {
    TaskSpecStatus.PENDING: "pending",
    TaskSpecStatus.IN_PROGRESS: "in_progress",
    TaskSpecStatus.DONE: "done",
    TaskSpecStatus.BLOCKED: "blocked",
}


class TaskSpecStore:
    def __init__(self, root_dir: str | Path = Path("factory/taskspecs")) -> None:
        self.root_dir = Path(root_dir)
        self._init_dirs()

    def enqueue(self, task: TaskSpec) -> str:
        if task.status != TaskSpecStatus.PENDING:
            raise ValueError("Only pending TaskSpec can be enqueued")
        self._ensure_task_id_absent(task.task_id)
        return self._write(task)

    def get(self, task_id: str) -> TaskSpec | None:
        for status in TaskSpecStatus:
            path = self._path_for(status, task_id)
            if path.exists():
                return read_task_spec(path)
        return None

    def list(self, status: TaskSpecStatus | str | None = None) -> list[TaskSpec]:
        if status is not None:
            return self._list_status(_coerce_status(status))

        tasks: list[TaskSpec] = []
        for state in TaskSpecStatus:
            tasks.extend(self._list_status(state))
        return sorted(tasks, key=lambda task: task.task_id)

    def next_pending(self) -> TaskSpec | None:
        pending = self._list_status(TaskSpecStatus.PENDING)
        if not pending:
            return None
        return sorted(pending, key=lambda task: task.task_id)[0]

    def mark_in_progress(self, task_id: str) -> TaskSpec:
        task = self._require(task_id)
        if task.status != TaskSpecStatus.PENDING:
            raise ValueError("Only pending TaskSpec can move to in_progress")
        return self._move(task, task.with_status(TaskSpecStatus.IN_PROGRESS))

    def mark_done(self, task_id: str, evidence_paths: list[str]) -> TaskSpec:
        task = self._require(task_id)
        if task.status != TaskSpecStatus.IN_PROGRESS:
            raise ValueError("Only in_progress TaskSpec can move to done")
        return self._move(
            task,
            task.with_status(TaskSpecStatus.DONE, evidence_paths=evidence_paths),
        )

    def mark_blocked(self, task_id: str, blocking_reason: str) -> TaskSpec:
        task = self._require(task_id)
        if task.status not in {TaskSpecStatus.PENDING, TaskSpecStatus.IN_PROGRESS}:
            raise ValueError("Only pending or in_progress TaskSpec can move to blocked")
        return self._move(
            task,
            task.with_status(TaskSpecStatus.BLOCKED, blocking_reason=blocking_reason),
        )

    def counts(self) -> dict[str, int]:
        return {status.value: len(self._list_status(status)) for status in TaskSpecStatus}

    def _init_dirs(self) -> None:
        for dirname in STATE_DIRS.values():
            (self.root_dir / dirname).mkdir(parents=True, exist_ok=True)

    def _ensure_task_id_absent(self, task_id: str) -> None:
        if self.get(task_id) is not None:
            raise ValueError(f"TaskSpec already exists: {task_id}")

    def _require(self, task_id: str) -> TaskSpec:
        task = self.get(task_id)
        if task is None:
            raise FileNotFoundError(f"TaskSpec not found: {task_id}")
        return task

    def _move(self, old_task: TaskSpec, new_task: TaskSpec) -> TaskSpec:
        old_path = self._path_for(old_task.status, old_task.task_id)
        if old_path.exists():
            old_path.unlink()
        self._write(new_task)
        return new_task

    def _write(self, task: TaskSpec) -> str:
        return write_task_spec(task, self._path_for(task.status, task.task_id))

    def _list_status(self, status: TaskSpecStatus) -> list[TaskSpec]:
        directory = self.root_dir / STATE_DIRS[status]
        if not directory.exists():
            return []
        return [read_task_spec(path) for path in sorted(directory.glob("*.json"))]

    def _path_for(self, status: TaskSpecStatus, task_id: str) -> Path:
        return self.root_dir / STATE_DIRS[status] / f"{task_id}.json"


def _coerce_status(status: TaskSpecStatus | str) -> TaskSpecStatus:
    return status if isinstance(status, TaskSpecStatus) else TaskSpecStatus(status)
