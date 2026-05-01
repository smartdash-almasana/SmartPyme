
from factory.adapters.telegram_superowner_adapter import TelegramSuperownerAdapter
from factory.core.task_spec import TaskSpec
from factory.core.task_spec_store import TaskSpecStore


def _update(user_id: int, text: str) -> dict:
    return {"message": {"from": {"id": user_id}, "text": text}}


def _task(task_id="FM_017"):
    return TaskSpec(
        task_id=task_id,
        title="Inspección Telegram",
        objective="Agregar comandos de inspección",
        allowed_paths=["factory", "tests/factory"],
        forbidden_paths=["app"],
        acceptance_criteria=["inspección operativa disponible"],
        validation_commands=["pytest fake"],
    )


def test_superowner_blocked_lists_blocked_tasks(tmp_path):
    store = TaskSpecStore(tmp_path / "taskspecs")
    store.enqueue(_task("FM_017_A"))
    store.enqueue(_task("FM_017_B"))
    store.mark_blocked("FM_017_A", "VALIDATION_FAILED")
    adapter = TelegramSuperownerAdapter(superowner_telegram_user_id=111, store=store)

    response = adapter.handle_update(_update(111, "/blocked"))

    assert response["status"] == "ok"
    assert response["blocked_count"] == 1
    assert response["blocked_tasks"][0]["task_id"] == "FM_017_A"
    assert response["blocked_tasks"][0]["blocking_reason"] == "VALIDATION_FAILED"
    assert "FM_017_A" in response["message"]


def test_superowner_blocked_empty(tmp_path):
    store = TaskSpecStore(tmp_path / "taskspecs")
    adapter = TelegramSuperownerAdapter(superowner_telegram_user_id=111, store=store)

    response = adapter.handle_update(_update(111, "/blocked"))

    assert response["status"] == "ok"
    assert response["blocked_count"] == 0
    assert response["blocked_tasks"] == []
    assert response["message"] == "No hay tareas bloqueadas."


def test_superowner_evidence_reads_registered_evidence_files(tmp_path):
    store = TaskSpecStore(tmp_path / "taskspecs")
    evidence_path = tmp_path / "evidence" / "FM_017" / "report.txt"
    evidence_path.parent.mkdir(parents=True)
    evidence_path.write_text("evidencia verificable", encoding="utf-8")
    store.enqueue(_task("FM_017"))
    store.mark_in_progress("FM_017")
    store.mark_done("FM_017", evidence_paths=[str(evidence_path)])
    adapter = TelegramSuperownerAdapter(superowner_telegram_user_id=111, store=store)

    response = adapter.handle_update(_update(111, "/evidence FM_017"))

    assert response["status"] == "ok"
    assert response["task_id"] == "FM_017"
    assert response["evidence_count"] == 1
    assert response["evidence"][0]["exists"] is True
    assert response["evidence"][0]["content"] == "evidencia verificable"
    assert response["evidence"][0]["truncated"] is False


def test_superowner_evidence_reports_missing_registered_file(tmp_path):
    store = TaskSpecStore(tmp_path / "taskspecs")
    missing_path = tmp_path / "evidence" / "missing.txt"
    store.enqueue(_task("FM_017"))
    store.mark_in_progress("FM_017")
    store.mark_done("FM_017", evidence_paths=[str(missing_path)])
    adapter = TelegramSuperownerAdapter(superowner_telegram_user_id=111, store=store)

    response = adapter.handle_update(_update(111, "/evidence FM_017"))

    assert response["status"] == "ok"
    assert response["evidence_count"] == 1
    assert response["evidence"][0]["exists"] is False
    assert response["evidence"][0]["content"] == ""


def test_superowner_evidence_not_found(tmp_path):
    store = TaskSpecStore(tmp_path / "taskspecs")
    adapter = TelegramSuperownerAdapter(superowner_telegram_user_id=111, store=store)

    response = adapter.handle_update(_update(111, "/evidence missing"))

    assert response["status"] == "not_found"
    assert response["task_id"] == "missing"
    assert response["evidence"] == []


def test_superowner_evidence_rejects_invalid_command(tmp_path):
    store = TaskSpecStore(tmp_path / "taskspecs")
    adapter = TelegramSuperownerAdapter(superowner_telegram_user_id=111, store=store)

    response = adapter.handle_update(_update(111, "/evidence"))

    assert response["status"] == "unsupported_command"


def test_superowner_inspection_rejects_non_superowner(tmp_path):
    store = TaskSpecStore(tmp_path / "taskspecs")
    adapter = TelegramSuperownerAdapter(superowner_telegram_user_id=111, store=store)

    blocked = adapter.handle_update(_update(999, "/blocked"))
    evidence = adapter.handle_update(_update(999, "/evidence FM_017"))

    assert blocked["status"] == "unauthorized"
    assert evidence["status"] == "unauthorized"
