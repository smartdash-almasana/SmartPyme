from factory.adapters.telegram_superowner_adapter import TelegramSuperownerAdapter
from factory.core.run_report import build_factory_run_report, write_factory_run_report
from factory.core.run_report_summary import build_failed_paths_summary, format_failed_paths_summary
from factory.core.task_spec import TaskSpecStatus
from factory.core.task_spec_runner import CommandResult, TaskSpecRunResult
from factory.core.task_spec_store import TaskSpecStore


def _update(user_id: int, text: str) -> dict:
    return {"message": {"from": {"id": user_id}, "text": text}}


def _report_with_failed_paths():
    return build_factory_run_report(
        run_type="run_batch",
        requested_count=2,
        results=[
            TaskSpecRunResult(
                status=TaskSpecStatus.DONE,
                task_id="FM_028_A",
                evidence_paths=["evidence/a.txt"],
                command_results=[CommandResult("pytest a", 0)],
                changed_paths=["factory/core/run_report_summary.py"],
                path_errors=[],
            ),
            TaskSpecRunResult(
                status=TaskSpecStatus.BLOCKED,
                task_id="FM_028_B",
                evidence_paths=["evidence/b.txt"],
                blocking_reason="PATH_VALIDATION_FAILED",
                command_results=[CommandResult("pytest b", 0)],
                changed_paths=["app/services/runtime.py", "docs/x.md"],
                path_errors=[
                    "FORBIDDEN_PATH_MODIFIED: app/services/runtime.py",
                    "PATH_NOT_ALLOWED: docs/x.md",
                ],
            ),
        ],
    )


def test_build_failed_paths_summary_groups_path_errors_by_task():
    summary = build_failed_paths_summary(_report_with_failed_paths())

    assert summary["run_type"] == "run_batch"
    assert summary["executed_count"] == 2
    assert summary["blocked_count"] == 1
    assert summary["failed_tasks_count"] == 1
    assert summary["path_errors_count"] == 2
    assert summary["path_errors"] == [
        "FORBIDDEN_PATH_MODIFIED: app/services/runtime.py",
        "PATH_NOT_ALLOWED: docs/x.md",
    ]
    assert summary["failed_tasks"][0]["task_id"] == "FM_028_B"
    assert summary["failed_tasks"][0]["path_errors_count"] == 2


def test_format_failed_paths_summary_returns_compact_message():
    summary = build_failed_paths_summary(_report_with_failed_paths())
    message = format_failed_paths_summary(summary)

    assert summary["report_id"] in message
    assert "path_errors=2" in message
    assert "failed_tasks=1" in message
    assert "FM_028_B=2" in message


def test_telegram_failed_paths_returns_latest_report_failed_paths(tmp_path):
    evidence_dir = tmp_path / "evidence"
    report = _report_with_failed_paths()
    write_factory_run_report(report, evidence_dir)
    adapter = TelegramSuperownerAdapter(
        superowner_telegram_user_id=111,
        evidence_dir=evidence_dir,
        store=TaskSpecStore(tmp_path / "taskspecs"),
    )

    response = adapter.handle_update(_update(111, "/failed_paths"))

    assert response["status"] == "ok"
    assert response["summary"]["report_id"] == report.report_id
    assert response["summary"]["failed_tasks_count"] == 1
    assert response["summary"]["path_errors_count"] == 2
    assert response["summary"]["failed_tasks"][0]["task_id"] == "FM_028_B"
    assert "path_errors=2" in response["message"]


def test_telegram_failed_paths_handles_report_without_path_errors(tmp_path):
    evidence_dir = tmp_path / "evidence"
    report = build_factory_run_report(
        run_type="run_one",
        requested_count=1,
        results=[
            TaskSpecRunResult(
                status=TaskSpecStatus.DONE,
                task_id="FM_028_C",
                evidence_paths=["evidence/c.txt"],
                command_results=[CommandResult("pytest c", 0)],
                changed_paths=["factory/core/run_report_summary.py"],
            )
        ],
    )
    write_factory_run_report(report, evidence_dir)
    adapter = TelegramSuperownerAdapter(
        superowner_telegram_user_id=111,
        evidence_dir=evidence_dir,
        store=TaskSpecStore(tmp_path / "taskspecs"),
    )

    response = adapter.handle_update(_update(111, "/failed_paths"))

    assert response["status"] == "ok"
    assert response["summary"]["path_errors_count"] == 0
    assert response["summary"]["failed_tasks"] == []
    assert "sin path_errors" in response["message"]


def test_telegram_failed_paths_handles_missing_report(tmp_path):
    adapter = TelegramSuperownerAdapter(
        superowner_telegram_user_id=111,
        evidence_dir=tmp_path / "evidence",
        store=TaskSpecStore(tmp_path / "taskspecs"),
    )

    response = adapter.handle_update(_update(111, "/failed_paths"))

    assert response["status"] == "not_found"


def test_telegram_failed_paths_rejects_non_superowner(tmp_path):
    adapter = TelegramSuperownerAdapter(
        superowner_telegram_user_id=111,
        evidence_dir=tmp_path / "evidence",
        store=TaskSpecStore(tmp_path / "taskspecs"),
    )

    response = adapter.handle_update(_update(999, "/failed_paths"))

    assert response["status"] == "unauthorized"
