from factory.adapters.telegram_superowner_adapter import TelegramSuperownerAdapter
from factory.core.run_report import build_factory_run_report, write_factory_run_report
from factory.core.run_report_summary import build_run_report_summary, format_run_report_summary
from factory.core.task_spec import TaskSpecStatus
from factory.core.task_spec_runner import CommandResult, TaskSpecRunResult
from factory.core.task_spec_store import TaskSpecStore


def _update(user_id: int, text: str) -> dict:
    return {"message": {"from": {"id": user_id}, "text": text}}


def _report():
    return build_factory_run_report(
        run_type="run_batch",
        requested_count=2,
        results=[
            TaskSpecRunResult(
                status=TaskSpecStatus.DONE,
                task_id="FM_027_A",
                evidence_paths=["evidence/a.txt"],
                command_results=[CommandResult("pytest a", 0)],
                changed_paths=[
                    "factory/core/run_report_summary.py",
                    "factory/adapters/telegram_superowner_adapter.py",
                ],
            ),
            TaskSpecRunResult(
                status=TaskSpecStatus.BLOCKED,
                task_id="FM_027_B",
                evidence_paths=["evidence/b.txt"],
                blocking_reason="PATH_VALIDATION_FAILED",
                command_results=[CommandResult("pytest b", 0)],
                changed_paths=[
                    "factory/core/run_report_summary.py",
                    "tests/factory/test_run_report_summary_fm_027.py",
                ],
                path_errors=["PATH_NOT_ALLOWED: docs/x.md"],
            ),
        ],
    )


def test_build_run_report_summary_aggregates_changed_paths_and_tasks():
    summary = build_run_report_summary(_report())

    assert summary["run_type"] == "run_batch"
    assert summary["executed_count"] == 2
    assert summary["done_count"] == 1
    assert summary["blocked_count"] == 1
    assert summary["blocked_task_ids"] == ["FM_027_B"]
    assert summary["changed_paths_count"] == 3
    assert summary["changed_paths"] == [
        "factory/adapters/telegram_superowner_adapter.py",
        "factory/core/run_report_summary.py",
        "tests/factory/test_run_report_summary_fm_027.py",
    ]
    assert summary["affected_tasks"][0]["task_id"] == "FM_027_A"
    assert summary["affected_tasks"][1]["changed_paths_count"] == 2


def test_format_run_report_summary_returns_compact_message():
    summary = build_run_report_summary(_report())
    message = format_run_report_summary(summary)

    assert summary["report_id"] in message
    assert "executed=2" in message
    assert "done=1" in message
    assert "blocked=1" in message
    assert "changed_paths=3" in message


def test_telegram_run_report_summary_returns_latest_report_summary(tmp_path):
    evidence_dir = tmp_path / "evidence"
    report = _report()
    write_factory_run_report(report, evidence_dir)
    adapter = TelegramSuperownerAdapter(
        superowner_telegram_user_id=111,
        evidence_dir=evidence_dir,
        store=TaskSpecStore(tmp_path / "taskspecs"),
    )

    response = adapter.handle_update(_update(111, "/run_report_summary"))

    assert response["status"] == "ok"
    assert response["summary"]["report_id"] == report.report_id
    assert response["summary"]["executed_count"] == 2
    assert response["summary"]["changed_paths_count"] == 3
    assert "changed_paths=3" in response["message"]


def test_telegram_run_report_summary_handles_missing_report(tmp_path):
    adapter = TelegramSuperownerAdapter(
        superowner_telegram_user_id=111,
        evidence_dir=tmp_path / "evidence",
        store=TaskSpecStore(tmp_path / "taskspecs"),
    )

    response = adapter.handle_update(_update(111, "/run_report_summary"))

    assert response["status"] == "not_found"


def test_telegram_run_report_summary_rejects_non_superowner(tmp_path):
    adapter = TelegramSuperownerAdapter(
        superowner_telegram_user_id=111,
        evidence_dir=tmp_path / "evidence",
        store=TaskSpecStore(tmp_path / "taskspecs"),
    )

    response = adapter.handle_update(_update(999, "/run_report_summary"))

    assert response["status"] == "unauthorized"
