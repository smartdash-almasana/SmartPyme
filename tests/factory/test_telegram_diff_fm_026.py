
from factory.adapters.telegram_superowner_adapter import TelegramSuperownerAdapter
from factory.core.run_report import build_factory_run_report, write_factory_run_report
from factory.core.task_spec import TaskSpec, TaskSpecStatus
from factory.core.task_spec_runner import CommandResult, TaskSpecRunResult
from factory.core.task_spec_store import TaskSpecStore


def _update(user_id: int, text: str) -> dict:
    return {"message": {"from": {"id": user_id}, "text": text}}


def _task(task_id="FM_026"):
    return TaskSpec(
        task_id=task_id,
        title="Telegram diff",
        objective="Exponer changed_paths por Telegram",
        allowed_paths=["factory", "tests/factory"],
        forbidden_paths=["app"],
        acceptance_criteria=["/diff task_id disponible"],
        validation_commands=["pytest fake"],
    )


def test_diff_command_returns_changed_paths_from_latest_run_report(tmp_path):
    evidence_dir = tmp_path / "evidence"
    report = build_factory_run_report(
        run_type="run_one",
        requested_count=1,
        results=[
            TaskSpecRunResult(
                status=TaskSpecStatus.DONE,
                task_id="FM_026",
                evidence_paths=["evidence/paths.txt"],
                command_results=[CommandResult("pytest fake", 0)],
                changed_paths=[
                    "factory/adapters/telegram_superowner_adapter.py",
                    "tests/factory/test_telegram_diff_fm_026.py",
                ],
            )
        ],
    )
    write_factory_run_report(report, evidence_dir)
    adapter = TelegramSuperownerAdapter(
        superowner_telegram_user_id=111,
        evidence_dir=evidence_dir,
        store=TaskSpecStore(tmp_path / "taskspecs"),
    )

    response = adapter.handle_update(_update(111, "/diff FM_026"))

    assert response["status"] == "ok"
    assert response["task_id"] == "FM_026"
    assert response["source"] == "run_report"
    assert response["report_id"] == report.report_id
    assert response["changed_paths_count"] == 2
    assert response["changed_paths"] == [
        "factory/adapters/telegram_superowner_adapter.py",
        "tests/factory/test_telegram_diff_fm_026.py",
    ]
    assert "FM_026" in response["message"]


def test_diff_command_falls_back_to_task_paths_evidence(tmp_path):
    store = TaskSpecStore(tmp_path / "taskspecs")
    paths_file = tmp_path / "evidence" / "FM_026" / "paths.txt"
    paths_file.parent.mkdir(parents=True)
    paths_file.write_text(
        "task_id=FM_026\n"
        "section=changed_paths\n"
        "changed_paths:\n"
        "factory/core/run_report.py\n"
        "tests/factory/test_telegram_diff_fm_026.py\n"
        "path_errors:\n",
        encoding="utf-8",
    )
    store.enqueue(_task("FM_026"))
    store.mark_in_progress("FM_026")
    store.mark_done("FM_026", evidence_paths=[str(paths_file)])
    adapter = TelegramSuperownerAdapter(
        superowner_telegram_user_id=111,
        evidence_dir=tmp_path / "evidence",
        store=store,
    )

    response = adapter.handle_update(_update(111, "/diff FM_026"))

    assert response["status"] == "ok"
    assert response["source"] == "task_evidence"
    assert response["report_id"] is None
    assert response["changed_paths"] == [
        "factory/core/run_report.py",
        "tests/factory/test_telegram_diff_fm_026.py",
    ]


def test_diff_command_returns_empty_list_when_task_has_no_paths(tmp_path):
    store = TaskSpecStore(tmp_path / "taskspecs")
    store.enqueue(_task("FM_026"))
    adapter = TelegramSuperownerAdapter(superowner_telegram_user_id=111, store=store)

    response = adapter.handle_update(_update(111, "/diff FM_026"))

    assert response["status"] == "ok"
    assert response["source"] == "task_evidence"
    assert response["changed_paths_count"] == 0
    assert response["changed_paths"] == []


def test_diff_command_reports_missing_task(tmp_path):
    adapter = TelegramSuperownerAdapter(
        superowner_telegram_user_id=111,
        evidence_dir=tmp_path / "evidence",
        store=TaskSpecStore(tmp_path / "taskspecs"),
    )

    response = adapter.handle_update(_update(111, "/diff missing"))

    assert response["status"] == "not_found"
    assert response["task_id"] == "missing"
    assert response["changed_paths"] == []


def test_diff_command_rejects_invalid_command(tmp_path):
    adapter = TelegramSuperownerAdapter(
        superowner_telegram_user_id=111,
        store=TaskSpecStore(tmp_path / "taskspecs"),
    )

    response = adapter.handle_update(_update(111, "/diff"))

    assert response["status"] == "invalid_command"


def test_diff_command_rejects_non_superowner(tmp_path):
    adapter = TelegramSuperownerAdapter(
        superowner_telegram_user_id=111,
        store=TaskSpecStore(tmp_path / "taskspecs"),
    )

    response = adapter.handle_update(_update(999, "/diff FM_026"))

    assert response["status"] == "unauthorized"
