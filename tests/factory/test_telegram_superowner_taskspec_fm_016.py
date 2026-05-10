from pathlib import Path

from factory.adapters.telegram_superowner_adapter import TelegramSuperownerAdapter
from factory.core.task_spec import TaskSpecStatus
from factory.core.task_spec_runner import CommandResult, TaskSpecRunner
from factory.core.task_spec_store import TaskSpecStore


def _update(user_id: int, text: str) -> dict:
    return {"message": {"from": {"id": user_id}, "text": text}}


def _ok_runner(command: str) -> CommandResult:
    return CommandResult(command=command, exit_code=0, stdout="ok", stderr="")


def test_superowner_enqueue_dev_creates_real_taskspec(tmp_path):
    store = TaskSpecStore(tmp_path / "taskspecs")
    runner = TaskSpecRunner(store, evidence_dir=tmp_path / "evidence", command_runner=_ok_runner)
    adapter = TelegramSuperownerAdapter(
        superowner_telegram_user_id=111,
        store=store,
        runner=runner,
    )

    response = adapter.handle_update(
        _update(111, "/enqueue_dev Crear TaskSpec real desde Telegram")
    )

    assert response["status"] == "queued"
    assert response["task"]["task_type"] == "taskspec_template"

    task_id = response["task"]["task_id"]
    task = store.get(task_id)
    assert task is not None
    assert task.status == TaskSpecStatus.PENDING
    assert task.objective == "Crear TaskSpec real desde Telegram"
    assert task.metadata["origin"] == "telegram_superowner"
    assert task.allowed_paths == ["factory", "tests/factory"]
    assert "app" in task.forbidden_paths


def test_superowner_status_pending_and_task_read_use_taskspec_store(tmp_path):
    store = TaskSpecStore(tmp_path / "taskspecs")
    runner = TaskSpecRunner(store, evidence_dir=tmp_path / "evidence", command_runner=_ok_runner)
    adapter = TelegramSuperownerAdapter(
        superowner_telegram_user_id=111,
        store=store,
        runner=runner,
    )
    queued = adapter.handle_update(_update(111, "/enqueue_dev Implementar runner"))
    task_id = queued["task"]["task_id"]

    status = adapter.handle_update(_update(111, "/status_factory"))
    pending = adapter.handle_update(_update(111, "/tasks_pending"))
    task_status = adapter.handle_update(_update(111, f"/task {task_id}"))

    assert status["status"] == "ok"
    assert status["counts"] == {"pending": 1, "in_progress": 0, "done": 0, "blocked": 0,
                                "waiting_for_approval": 0}
    assert status["next_pending_task_id"] == task_id
    assert pending["pending_count"] == 1
    assert pending["pending_tasks"][0]["task_id"] == task_id
    assert task_status["status"] == "pending"
    assert task_status["task"]["task_id"] == task_id
    assert task_status["task"]["status"] == "pending"


def test_superowner_run_one_executes_taskspec_runner_and_marks_done(tmp_path):
    store = TaskSpecStore(tmp_path / "taskspecs")
    runner = TaskSpecRunner(
        store,
        evidence_dir=tmp_path / "evidence",
        changed_paths_provider=lambda task: ["factory/core/task_spec_runner.py"],
        command_runner=_ok_runner,
    )
    adapter = TelegramSuperownerAdapter(
        superowner_telegram_user_id=111,
        store=store,
        runner=runner,
    )
    queued = adapter.handle_update(_update(111, "/enqueue_dev Ejecutar TaskSpec"))
    task_id = queued["task"]["task_id"]

    run = adapter.handle_update(_update(111, "/run_one"))
    task_status = adapter.handle_update(_update(111, f"/task {task_id}"))

    assert run["status"] == "done"
    assert run["result"]["task_id"] == task_id
    assert len(run["result"]["evidence_paths"]) == 2
    assert all(Path(path).exists() for path in run["result"]["evidence_paths"])
    assert task_status["status"] == "done"
    assert task_status["task"]["evidence_paths"] == run["result"]["evidence_paths"]


def test_superowner_run_one_blocks_failed_taskspec(tmp_path):
    def fail_runner(command: str) -> CommandResult:
        return CommandResult(command=command, exit_code=1, stdout="", stderr="boom")

    store = TaskSpecStore(tmp_path / "taskspecs")
    runner = TaskSpecRunner(store, evidence_dir=tmp_path / "evidence", command_runner=fail_runner)
    adapter = TelegramSuperownerAdapter(
        superowner_telegram_user_id=111,
        store=store,
        runner=runner,
    )
    queued = adapter.handle_update(_update(111, "/enqueue_dev Fallar validación"))
    task_id = queued["task"]["task_id"]

    run = adapter.handle_update(_update(111, "/run_one"))
    task_status = adapter.handle_update(_update(111, f"/task {task_id}"))

    assert run["status"] == "blocked"
    assert run["result"]["blocking_reason"].startswith("VALIDATION_COMMAND_FAILED")
    assert task_status["status"] == "blocked"
    assert task_status["task"]["blocking_reason"].startswith("VALIDATION_COMMAND_FAILED")


def test_superowner_run_one_idle_with_no_pending_tasks(tmp_path):
    store = TaskSpecStore(tmp_path / "taskspecs")
    runner = TaskSpecRunner(store, evidence_dir=tmp_path / "evidence", command_runner=_ok_runner)
    adapter = TelegramSuperownerAdapter(
        superowner_telegram_user_id=111,
        store=store,
        runner=runner,
    )

    run = adapter.handle_update(_update(111, "/run_one"))

    assert run["status"] == "idle"
    assert run["result"]["reason"] == "NO_PENDING_TASK"


def test_superowner_still_rejects_non_superowner(tmp_path):
    adapter = TelegramSuperownerAdapter(
        superowner_telegram_user_id=111,
        store=TaskSpecStore(tmp_path / "taskspecs"),
    )

    response = adapter.handle_update(_update(999, "/status_factory"))

    assert response["status"] == "unauthorized"
