import pytest

from factory.adapters.telegram_superowner_adapter import TelegramSuperownerAdapter
from factory.core.task_spec import TaskSpec, TaskSpecStatus
from factory.core.task_spec_store import TaskSpecStore


def _update(user_id: int, text: str) -> dict:
    return {"message": {"from": {"id": user_id}, "text": text}}


def _task(task_id="FM_018"):
    return TaskSpec(
        task_id=task_id,
        title="Retry blocked",
        objective="Reintentar TaskSpec bloqueada",
        allowed_paths=["factory", "tests/factory"],
        forbidden_paths=["app"],
        acceptance_criteria=["blocked vuelve a pending con trazabilidad"],
        validation_commands=["pytest fake"],
    )


def test_store_retry_blocked_moves_task_back_to_pending_with_metadata(tmp_path):
    store = TaskSpecStore(tmp_path / "taskspecs")
    store.enqueue(_task())
    store.mark_blocked("FM_018", "VALIDATION_FAILED")

    retried = store.retry_blocked("FM_018", retried_by="telegram:111")

    assert retried.status == TaskSpecStatus.PENDING
    assert retried.blocking_reason is None
    assert retried.evidence_paths == []
    assert retried.metadata["retry_count"] == 1
    assert retried.metadata["retry_history"] == [
        {
            "previous_status": "blocked",
            "previous_blocking_reason": "VALIDATION_FAILED",
            "retried_by": "telegram:111",
        }
    ]
    assert store.counts() == {"pending": 1, "in_progress": 0, "done": 0, "blocked": 0,
                              "waiting_for_approval": 0}


def test_store_retry_blocked_rejects_non_blocked_task(tmp_path):
    store = TaskSpecStore(tmp_path / "taskspecs")
    store.enqueue(_task())

    with pytest.raises(ValueError, match="Only blocked TaskSpec can be retried"):
        store.retry_blocked("FM_018")


def test_store_retry_blocked_missing_task_raises(tmp_path):
    store = TaskSpecStore(tmp_path / "taskspecs")

    with pytest.raises(FileNotFoundError, match="TaskSpec not found"):
        store.retry_blocked("missing")


def test_superowner_retry_blocked_command_moves_to_pending(tmp_path):
    store = TaskSpecStore(tmp_path / "taskspecs")
    store.enqueue(_task())
    store.mark_blocked("FM_018", "PATH_VALIDATION_FAILED")
    adapter = TelegramSuperownerAdapter(superowner_telegram_user_id=111, store=store)

    response = adapter.handle_update(_update(111, "/retry_blocked FM_018"))
    status = adapter.handle_update(_update(111, "/task FM_018"))

    assert response["status"] == "queued"
    assert response["task"]["status"] == "pending"
    assert response["task"]["metadata"]["retry_count"] == 1
    assert response["task"]["metadata"]["retry_history"][0]["retried_by"] == "telegram:111"
    assert status["status"] == "pending"


def test_superowner_retry_blocked_command_reports_missing_task(tmp_path):
    store = TaskSpecStore(tmp_path / "taskspecs")
    adapter = TelegramSuperownerAdapter(superowner_telegram_user_id=111, store=store)

    response = adapter.handle_update(_update(111, "/retry_blocked missing"))

    assert response["status"] == "not_found"
    assert response["task_id"] == "missing"


def test_superowner_retry_blocked_command_reports_invalid_transition(tmp_path):
    store = TaskSpecStore(tmp_path / "taskspecs")
    store.enqueue(_task())
    adapter = TelegramSuperownerAdapter(superowner_telegram_user_id=111, store=store)

    response = adapter.handle_update(_update(111, "/retry_blocked FM_018"))

    assert response["status"] == "invalid_transition"
    assert response["task_id"] == "FM_018"
    assert response["message"] == "Only blocked TaskSpec can be retried"


def test_superowner_retry_blocked_rejects_non_superowner(tmp_path):
    store = TaskSpecStore(tmp_path / "taskspecs")
    store.enqueue(_task())
    store.mark_blocked("FM_018", "VALIDATION_FAILED")
    adapter = TelegramSuperownerAdapter(superowner_telegram_user_id=111, store=store)

    response = adapter.handle_update(_update(999, "/retry_blocked FM_018"))

    assert response["status"] == "unauthorized"
    assert store.get("FM_018").status == TaskSpecStatus.BLOCKED
