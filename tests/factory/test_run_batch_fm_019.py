from factory.adapters.telegram_superowner_adapter import TelegramSuperownerAdapter
from factory.core.task_spec import TaskSpec, TaskSpecStatus
from factory.core.task_spec_runner import CommandResult, TaskSpecRunner
from factory.core.task_spec_store import TaskSpecStore


def _update(user_id: int, text: str) -> dict:
    return {"message": {"from": {"id": user_id}, "text": text}}


def _task(task_id: str):
    return TaskSpec(
        task_id=task_id,
        title=f"Batch {task_id}",
        objective=f"Ejecutar {task_id}",
        allowed_paths=["factory", "tests/factory"],
        forbidden_paths=["app"],
        acceptance_criteria=["batch ejecuta tareas pendientes"],
        validation_commands=["pytest fake"],
    )


def _ok_runner(command: str) -> CommandResult:
    return CommandResult(command=command, exit_code=0, stdout="ok", stderr="")


def test_run_batch_executes_requested_pending_tasks(tmp_path):
    store = TaskSpecStore(tmp_path / "taskspecs")
    store.enqueue(_task("FM_019_A"))
    store.enqueue(_task("FM_019_B"))
    store.enqueue(_task("FM_019_C"))
    runner = TaskSpecRunner(
        store,
        evidence_dir=tmp_path / "evidence",
        changed_paths_provider=lambda task: ["factory/core/task_spec_runner.py"],
        command_runner=_ok_runner,
    )
    adapter = TelegramSuperownerAdapter(superowner_telegram_user_id=111, store=store, runner=runner)

    response = adapter.handle_update(_update(111, "/run_batch 2"))

    assert response["status"] == "ok"
    assert response["requested"] == 2
    assert response["executed_count"] == 2
    assert response["done_count"] == 2
    assert response["blocked_count"] == 0
    assert [item["task_id"] for item in response["results"]] == ["FM_019_A", "FM_019_B"]
    assert store.get("FM_019_A").status == TaskSpecStatus.DONE
    assert store.get("FM_019_B").status == TaskSpecStatus.DONE
    assert store.get("FM_019_C").status == TaskSpecStatus.PENDING


def test_run_batch_stops_when_queue_becomes_empty(tmp_path):
    store = TaskSpecStore(tmp_path / "taskspecs")
    store.enqueue(_task("FM_019_A"))
    runner = TaskSpecRunner(
        store,
        evidence_dir=tmp_path / "evidence",
        changed_paths_provider=lambda task: ["factory/core/task_spec_runner.py"],
        command_runner=_ok_runner,
    )
    adapter = TelegramSuperownerAdapter(superowner_telegram_user_id=111, store=store, runner=runner)

    response = adapter.handle_update(_update(111, "/run_batch 5"))

    assert response["status"] == "ok"
    assert response["requested"] == 5
    assert response["executed_count"] == 1
    assert response["done_count"] == 1
    assert response["blocked_count"] == 0


def test_run_batch_reports_blocked_tasks_and_continues(tmp_path):
    store = TaskSpecStore(tmp_path / "taskspecs")
    store.enqueue(_task("FM_019_A"))
    store.enqueue(_task("FM_019_B"))

    def runner_for(command: str) -> CommandResult:
        return CommandResult(command=command, exit_code=1, stdout="", stderr="boom")

    runner = TaskSpecRunner(
        store,
        evidence_dir=tmp_path / "evidence",
        changed_paths_provider=lambda task: ["factory/core/task_spec_runner.py"],
        command_runner=runner_for,
    )
    adapter = TelegramSuperownerAdapter(superowner_telegram_user_id=111, store=store, runner=runner)

    response = adapter.handle_update(_update(111, "/run_batch 2"))

    assert response["status"] == "ok"
    assert response["executed_count"] == 2
    assert response["done_count"] == 0
    assert response["blocked_count"] == 2
    assert all(item["status"] == "blocked" for item in response["results"])
    assert store.get("FM_019_A").status == TaskSpecStatus.BLOCKED
    assert store.get("FM_019_B").status == TaskSpecStatus.BLOCKED


def test_run_batch_rejects_invalid_sizes(tmp_path):
    adapter = TelegramSuperownerAdapter(
        superowner_telegram_user_id=111,
        store=TaskSpecStore(tmp_path / "taskspecs"),
    )

    bad_zero = adapter.handle_update(_update(111, "/run_batch 0"))
    bad_large = adapter.handle_update(_update(111, "/run_batch 11"))
    bad_text = adapter.handle_update(_update(111, "/run_batch many"))
    bad_missing = adapter.handle_update(_update(111, "/run_batch"))

    assert bad_zero["status"] == "invalid_command"
    assert bad_large["status"] == "invalid_command"
    assert bad_text["status"] == "invalid_command"
    assert bad_missing["status"] == "invalid_command"


def test_run_batch_rejects_non_superowner(tmp_path):
    store = TaskSpecStore(tmp_path / "taskspecs")
    store.enqueue(_task("FM_019_A"))
    adapter = TelegramSuperownerAdapter(superowner_telegram_user_id=111, store=store)

    response = adapter.handle_update(_update(999, "/run_batch 1"))

    assert response["status"] == "unauthorized"
    assert store.get("FM_019_A").status == TaskSpecStatus.PENDING
