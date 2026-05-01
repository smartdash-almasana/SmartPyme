from factory.adapters.telegram_superowner_adapter import TelegramSuperownerAdapter
from factory.core.run_report import build_factory_run_report, write_factory_run_report
from factory.core.run_report_summary import (
    build_factory_health_summary,
    format_factory_health_summary,
)
from factory.core.task_spec import TaskSpec, TaskSpecStatus
from factory.core.task_spec_runner import CommandResult, TaskSpecRunResult
from factory.core.task_spec_store import TaskSpecStore


def _update(user_id: int, text: str) -> dict:
    return {"message": {"from": {"id": user_id}, "text": text}}


def _task(task_id="FM_029"):
    return TaskSpec(
        task_id=task_id,
        title="Factory health",
        objective="Exponer salud compacta por Telegram",
        allowed_paths=["factory", "tests/factory"],
        forbidden_paths=["app"],
        acceptance_criteria=["/factory_health disponible"],
        validation_commands=["pytest fake"],
    )


def _report_with_attention():
    return build_factory_run_report(
        run_type="run_batch",
        requested_count=2,
        results=[
            TaskSpecRunResult(
                status=TaskSpecStatus.DONE,
                task_id="FM_029_A",
                evidence_paths=["evidence/a.txt"],
                command_results=[CommandResult("pytest a", 0)],
                changed_paths=["factory/core/run_report_summary.py"],
            ),
            TaskSpecRunResult(
                status=TaskSpecStatus.BLOCKED,
                task_id="FM_029_B",
                evidence_paths=["evidence/b.txt"],
                blocking_reason="PATH_VALIDATION_FAILED",
                command_results=[CommandResult("pytest b", 0)],
                changed_paths=["app/services/runtime.py"],
                path_errors=["FORBIDDEN_PATH_MODIFIED: app/services/runtime.py"],
            ),
        ],
    )


def test_build_factory_health_summary_combines_queue_and_last_report():
    report = _report_with_attention()
    summary = build_factory_health_summary(
        queue_counts={"pending": 1, "in_progress": 0, "done": 2, "blocked": 1},
        next_pending_task_id="FM_029_NEXT",
        last_report=report,
    )

    assert summary["health_status"] == "attention_required"
    assert summary["queue_counts"]["pending"] == 1
    assert summary["next_pending_task_id"] == "FM_029_NEXT"
    assert summary["has_report"] is True
    assert summary["last_report"]["report_id"] == report.report_id
    assert summary["last_report"]["blocked_count"] == 1
    assert summary["changed_paths_count"] == 2
    assert summary["path_errors_count"] == 1
    assert summary["path_errors"] == ["FORBIDDEN_PATH_MODIFIED: app/services/runtime.py"]


def test_format_factory_health_summary_returns_compact_message():
    summary = build_factory_health_summary(
        queue_counts={"pending": 1, "in_progress": 0, "done": 2, "blocked": 1},
        next_pending_task_id="FM_029_NEXT",
        last_report=_report_with_attention(),
    )
    message = format_factory_health_summary(summary)

    assert "Factory health" in message
    assert "status=attention_required" in message
    assert "pending=1" in message
    assert "next=FM_029_NEXT" in message
    assert "changed_paths=2" in message
    assert "path_errors=1" in message


def test_telegram_factory_health_returns_queue_and_last_report_health(tmp_path):
    store = TaskSpecStore(tmp_path / "taskspecs")
    store.enqueue(_task("FM_029_NEXT"))
    store.enqueue(_task("FM_029_BLOCKED"))
    store.mark_blocked("FM_029_BLOCKED", "VALIDATION_FAILED")
    evidence_dir = tmp_path / "evidence"
    report = _report_with_attention()
    write_factory_run_report(report, evidence_dir)
    adapter = TelegramSuperownerAdapter(
        superowner_telegram_user_id=111,
        evidence_dir=evidence_dir,
        store=store,
    )

    response = adapter.handle_update(_update(111, "/factory_health"))

    assert response["status"] == "ok"
    assert response["health"]["health_status"] == "attention_required"
    assert response["health"]["queue_counts"]["pending"] == 1
    assert response["health"]["queue_counts"]["blocked"] == 1
    assert response["health"]["next_pending_task_id"] == "FM_029_NEXT"
    assert response["health"]["last_report"]["report_id"] == report.report_id
    assert response["health"]["path_errors_count"] == 1
    assert "Factory health" in response["message"]


def test_telegram_factory_health_handles_missing_report(tmp_path):
    store = TaskSpecStore(tmp_path / "taskspecs")
    store.enqueue(_task("FM_029_NEXT"))
    adapter = TelegramSuperownerAdapter(
        superowner_telegram_user_id=111,
        evidence_dir=tmp_path / "evidence",
        store=store,
    )

    response = adapter.handle_update(_update(111, "/factory_health"))

    assert response["status"] == "ok"
    assert response["health"]["has_report"] is False
    assert response["health"]["last_report"] is None
    assert response["health"]["health_status"] == "pending_work"
    assert "sin reportes" in response["message"]


def test_telegram_factory_health_rejects_non_superowner(tmp_path):
    adapter = TelegramSuperownerAdapter(
        superowner_telegram_user_id=111,
        evidence_dir=tmp_path / "evidence",
        store=TaskSpecStore(tmp_path / "taskspecs"),
    )

    response = adapter.handle_update(_update(999, "/factory_health"))

    assert response["status"] == "unauthorized"
