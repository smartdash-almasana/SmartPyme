from factory.adapters.telegram_superowner_adapter import TelegramSuperownerAdapter
from factory.core.task_spec import TaskSpec
from factory.core.task_spec_runner import CommandResult
from factory.core.task_spec_store import TaskSpecStore

SUPEROWNER_ID = 111


def _update(user_id: int, text: str) -> dict:
    return {"message": {"from": {"id": user_id}, "text": text}}


def _task(task_id: str, title: str = "Smoke task") -> TaskSpec:
    return TaskSpec(
        task_id=task_id,
        title=title,
        objective="Validar smoke integral de comandos Telegram Factory",
        allowed_paths=["factory", "tests/factory"],
        forbidden_paths=["app"],
        acceptance_criteria=["comando responde"],
        validation_commands=["pytest smoke"],
    )


def _ok_runner(command: str) -> CommandResult:
    return CommandResult(command=command, exit_code=0, stdout="ok", stderr="")


def _adapter(tmp_path):
    store = TaskSpecStore(tmp_path / "taskspecs")
    runner = None
    adapter = TelegramSuperownerAdapter(
        superowner_telegram_user_id=SUPEROWNER_ID,
        evidence_dir=tmp_path / "evidence",
        store=store,
        runner=runner,
    )
    adapter.runner.command_runner = _ok_runner
    adapter.runner.changed_paths_provider = lambda task: [
        "factory/adapters/telegram_superowner_adapter.py"
    ]
    return adapter, store


def test_telegram_factory_commands_smoke_full_owner_flow(tmp_path):
    adapter, store = _adapter(tmp_path)

    assert adapter.handle_update(_update(999, "/factory_help"))["status"] == "unauthorized"
    assert adapter.handle_update(_update(SUPEROWNER_ID, "/factory_help"))["status"] == "ok"
    assert adapter.handle_update(_update(SUPEROWNER_ID, "/factory_health"))["status"] == "ok"
    assert adapter.handle_update(_update(SUPEROWNER_ID, "/status_factory"))["status"] == "ok"
    assert adapter.handle_update(_update(SUPEROWNER_ID, "/templates"))["status"] == "ok"

    store.enqueue(_task("FM_031_PENDING"))
    pending_response = adapter.handle_update(_update(SUPEROWNER_ID, "/tasks_pending"))
    assert pending_response["status"] == "ok"
    assert pending_response["pending_count"] == 1

    task_response = adapter.handle_update(_update(SUPEROWNER_ID, "/task FM_031_PENDING"))
    assert task_response["status"] == "pending"

    run_response = adapter.handle_update(_update(SUPEROWNER_ID, "/run_one"))
    assert run_response["status"] == "done"
    assert run_response["result"]["changed_paths"] == [
        "factory/adapters/telegram_superowner_adapter.py"
    ]
    report_id = run_response["run_report"]["report_id"]

    assert adapter.handle_update(_update(SUPEROWNER_ID, "/last_report"))["status"] == "ok"
    assert adapter.handle_update(_update(SUPEROWNER_ID, "/run_report_summary"))["status"] == "ok"
    assert adapter.handle_update(_update(SUPEROWNER_ID, "/failed_paths"))["status"] == "ok"
    assert adapter.handle_update(_update(SUPEROWNER_ID, f"/report {report_id}"))["status"] == "ok"

    diff_response = adapter.handle_update(_update(SUPEROWNER_ID, "/diff FM_031_PENDING"))
    assert diff_response["status"] == "ok"
    assert diff_response["source"] == "run_report"
    assert diff_response["changed_paths"] == ["factory/adapters/telegram_superowner_adapter.py"]

    evidence_response = adapter.handle_update(_update(SUPEROWNER_ID, "/evidence FM_031_PENDING"))
    assert evidence_response["status"] == "ok"
    assert evidence_response["evidence_count"] == 2

    health_response = adapter.handle_update(_update(SUPEROWNER_ID, "/factory_health"))
    assert health_response["status"] == "ok"
    assert health_response["health"]["has_report"] is True


def test_telegram_factory_commands_smoke_blocked_recovery_flow(tmp_path):
    adapter, store = _adapter(tmp_path)
    store.enqueue(_task("FM_031_BLOCKED"))
    store.mark_blocked("FM_031_BLOCKED", "SMOKE_BLOCK")

    blocked_response = adapter.handle_update(_update(SUPEROWNER_ID, "/blocked"))
    assert blocked_response["status"] == "ok"
    assert blocked_response["blocked_count"] == 1

    retry_response = adapter.handle_update(_update(SUPEROWNER_ID, "/retry_blocked FM_031_BLOCKED"))
    assert retry_response["status"] == "queued"

    run_response = adapter.handle_update(_update(SUPEROWNER_ID, "/run_batch 1"))
    assert run_response["status"] == "ok"
    assert run_response["executed_count"] == 1
    assert run_response["done_count"] == 1


def test_telegram_factory_commands_smoke_invalid_and_missing_inputs(tmp_path):
    adapter, _store = _adapter(tmp_path)

    assert (
        adapter.handle_update(_update(SUPEROWNER_ID, "/unknown"))["status"]
        == "unsupported_command"
    )
    assert adapter.handle_update(_update(SUPEROWNER_ID, "/diff"))["status"] == "invalid_command"
    assert adapter.handle_update(_update(SUPEROWNER_ID, "/report missing"))["status"] == "not_found"
    assert adapter.handle_update(_update(SUPEROWNER_ID, "/task missing"))["status"] == "not_found"
    assert (
        adapter.handle_update(_update(SUPEROWNER_ID, "/evidence missing"))["status"]
        == "not_found"
    )
