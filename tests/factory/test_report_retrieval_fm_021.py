from pathlib import Path

from factory.adapters.telegram_superowner_adapter import TelegramSuperownerAdapter
from factory.core.run_report import (
    build_factory_run_report,
    read_factory_run_report,
    read_last_factory_run_report,
    write_factory_run_report,
)
from factory.core.task_spec import TaskSpecStatus
from factory.core.task_spec_runner import CommandResult, TaskSpecRunResult
from factory.core.task_spec_store import TaskSpecStore


def _update(user_id: int, text: str) -> dict:
    return {"message": {"from": {"id": user_id}, "text": text}}


def _report(task_id: str, status=TaskSpecStatus.DONE):
    return build_factory_run_report(
        run_type="run_one",
        requested_count=1,
        results=[
            TaskSpecRunResult(
                status=status,
                task_id=task_id,
                evidence_paths=[f"evidence/{task_id}.txt"],
                command_results=[CommandResult("pytest fake", 0 if status == TaskSpecStatus.DONE else 1)],
                blocking_reason=None if status == TaskSpecStatus.DONE else "VALIDATION_FAILED",
            )
        ],
    )


def test_read_factory_run_report_by_id_and_last(tmp_path):
    evidence_dir = tmp_path / "evidence"
    first = _report("FM_021_A")
    second = _report("FM_021_B")
    write_factory_run_report(first, evidence_dir)
    write_factory_run_report(second, evidence_dir)

    loaded = read_factory_run_report(first.report_id, evidence_dir)
    last = read_last_factory_run_report(evidence_dir)

    assert loaded is not None
    assert loaded.report_id == first.report_id
    assert loaded.task_results[0].task_id == "FM_021_A"
    assert last is not None
    assert last.report_id in {first.report_id, second.report_id}
    assert last.created_at >= first.created_at


def test_last_report_command_returns_latest_report(tmp_path):
    evidence_dir = tmp_path / "evidence"
    first = _report("FM_021_A")
    second = _report("FM_021_B")
    write_factory_run_report(first, evidence_dir)
    write_factory_run_report(second, evidence_dir)
    adapter = TelegramSuperownerAdapter(
        superowner_telegram_user_id=111,
        evidence_dir=evidence_dir,
        store=TaskSpecStore(tmp_path / "taskspecs"),
    )

    response = adapter.handle_update(_update(111, "/last_report"))

    assert response["status"] == "ok"
    assert response["report"]["report_id"] in {first.report_id, second.report_id}
    assert "# Factory Run Report" in response["markdown"]
    assert response["truncated"] is False


def test_report_command_returns_report_by_id(tmp_path):
    evidence_dir = tmp_path / "evidence"
    report = _report("FM_021_A")
    write_factory_run_report(report, evidence_dir)
    adapter = TelegramSuperownerAdapter(
        superowner_telegram_user_id=111,
        evidence_dir=evidence_dir,
        store=TaskSpecStore(tmp_path / "taskspecs"),
    )

    response = adapter.handle_update(_update(111, f"/report {report.report_id}"))

    assert response["status"] == "ok"
    assert response["report"]["report_id"] == report.report_id
    assert response["report"]["task_results"][0]["task_id"] == "FM_021_A"
    assert "FM_021_A" in response["markdown"]


def test_report_commands_handle_missing_reports(tmp_path):
    evidence_dir = tmp_path / "evidence"
    adapter = TelegramSuperownerAdapter(
        superowner_telegram_user_id=111,
        evidence_dir=evidence_dir,
        store=TaskSpecStore(tmp_path / "taskspecs"),
    )

    last = adapter.handle_update(_update(111, "/last_report"))
    specific = adapter.handle_update(_update(111, "/report missing"))

    assert last["status"] == "not_found"
    assert specific["status"] == "not_found"
    assert specific["report_id"] == "missing"


def test_report_command_rejects_invalid_command(tmp_path):
    adapter = TelegramSuperownerAdapter(
        superowner_telegram_user_id=111,
        store=TaskSpecStore(tmp_path / "taskspecs"),
    )

    response = adapter.handle_update(_update(111, "/report"))

    assert response["status"] == "unsupported_command"


def test_report_command_truncates_long_markdown(tmp_path):
    evidence_dir = tmp_path / "evidence"
    report = _report("FM_021_LONG")
    paths = write_factory_run_report(report, evidence_dir)
    Path(paths["markdown_path"]).write_text("x" * 5000, encoding="utf-8")
    adapter = TelegramSuperownerAdapter(
        superowner_telegram_user_id=111,
        evidence_dir=evidence_dir,
        store=TaskSpecStore(tmp_path / "taskspecs"),
    )

    response = adapter.handle_update(_update(111, f"/report {report.report_id}"))

    assert response["status"] == "ok"
    assert response["truncated"] is True
    assert len(response["markdown"]) == 3500


def test_report_commands_reject_non_superowner(tmp_path):
    evidence_dir = tmp_path / "evidence"
    report = _report("FM_021_A")
    write_factory_run_report(report, evidence_dir)
    adapter = TelegramSuperownerAdapter(
        superowner_telegram_user_id=111,
        evidence_dir=evidence_dir,
        store=TaskSpecStore(tmp_path / "taskspecs"),
    )

    last = adapter.handle_update(_update(999, "/last_report"))
    specific = adapter.handle_update(_update(999, f"/report {report.report_id}"))

    assert last["status"] == "unauthorized"
    assert specific["status"] == "unauthorized"
