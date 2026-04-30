from pathlib import Path

from factory.adapters.telegram_superowner_adapter import TelegramSuperownerAdapter
from factory.core.run_report import build_factory_run_report, write_factory_run_report
from factory.core.task_spec import TaskSpec, TaskSpecStatus
from factory.core.task_spec_runner import CommandResult, TaskSpecRunResult, TaskSpecRunner
from factory.core.task_spec_store import TaskSpecStore


def _update(user_id: int, text: str) -> dict:
    return {"message": {"from": {"id": user_id}, "text": text}}


def _task(task_id: str):
    return TaskSpec(
        task_id=task_id,
        title=f"Reporte {task_id}",
        objective=f"Ejecutar {task_id}",
        allowed_paths=["factory", "tests/factory"],
        forbidden_paths=["app"],
        acceptance_criteria=["report consolidado generado"],
        validation_commands=["pytest fake"],
    )


def _ok_runner(command: str) -> CommandResult:
    return CommandResult(command=command, exit_code=0, stdout="ok", stderr="")


def test_build_factory_run_report_summarizes_results():
    report = build_factory_run_report(
        run_type="run_batch",
        requested_count=2,
        results=[
            TaskSpecRunResult(
                status=TaskSpecStatus.DONE,
                task_id="FM_020_A",
                evidence_paths=["evidence/a.txt"],
                command_results=[CommandResult("pytest a", 0)],
            ),
            TaskSpecRunResult(
                status=TaskSpecStatus.BLOCKED,
                task_id="FM_020_B",
                evidence_paths=["evidence/b.txt"],
                blocking_reason="VALIDATION_FAILED",
                command_results=[CommandResult("pytest b", 1)],
                path_errors=["PATH_NOT_ALLOWED: app/x.py"],
            ),
        ],
        metadata={"source": "test"},
    )

    assert report.run_type == "run_batch"
    assert report.requested_count == 2
    assert report.executed_count == 2
    assert report.done_count == 1
    assert report.blocked_count == 1
    assert report.idle is False
    assert report.task_results[0].task_id == "FM_020_A"
    assert report.task_results[1].blocking_reason == "VALIDATION_FAILED"
    assert report.metadata["source"] == "test"


def test_write_factory_run_report_writes_json_and_markdown(tmp_path):
    report = build_factory_run_report(
        run_type="run_one",
        requested_count=1,
        results=[
            TaskSpecRunResult(
                status=TaskSpecStatus.DONE,
                task_id="FM_020_A",
                evidence_paths=["evidence/a.txt"],
                command_results=[CommandResult("pytest a", 0)],
            )
        ],
    )

    paths = write_factory_run_report(report, tmp_path / "evidence")

    json_path = Path(paths["json_path"])
    markdown_path = Path(paths["markdown_path"])
    assert json_path.exists()
    assert markdown_path.exists()
    assert "FM_020_A" in json_path.read_text(encoding="utf-8")
    assert "# Factory Run Report" in markdown_path.read_text(encoding="utf-8")
    assert "FM_020_A" in markdown_path.read_text(encoding="utf-8")


def test_telegram_run_one_includes_run_report_paths(tmp_path):
    store = TaskSpecStore(tmp_path / "taskspecs")
    store.enqueue(_task("FM_020_A"))
    runner = TaskSpecRunner(
        store,
        evidence_dir=tmp_path / "evidence" / "taskspecs",
        changed_paths_provider=lambda task: ["factory/core/run_report.py"],
        command_runner=_ok_runner,
    )
    adapter = TelegramSuperownerAdapter(
        superowner_telegram_user_id=111,
        evidence_dir=tmp_path / "evidence" / "taskspecs",
        store=store,
        runner=runner,
    )

    response = adapter.handle_update(_update(111, "/run_one"))

    assert response["status"] == "done"
    assert response["run_report"]["run_type"] == "run_one"
    assert response["run_report"]["executed_count"] == 1
    assert response["run_report"]["done_count"] == 1
    assert Path(response["run_report_paths"]["json_path"]).exists()
    assert Path(response["run_report_paths"]["markdown_path"]).exists()


def test_telegram_run_batch_includes_consolidated_report(tmp_path):
    store = TaskSpecStore(tmp_path / "taskspecs")
    store.enqueue(_task("FM_020_A"))
    store.enqueue(_task("FM_020_B"))
    runner = TaskSpecRunner(
        store,
        evidence_dir=tmp_path / "evidence" / "taskspecs",
        changed_paths_provider=lambda task: ["factory/core/run_report.py"],
        command_runner=_ok_runner,
    )
    adapter = TelegramSuperownerAdapter(
        superowner_telegram_user_id=111,
        evidence_dir=tmp_path / "evidence" / "taskspecs",
        store=store,
        runner=runner,
    )

    response = adapter.handle_update(_update(111, "/run_batch 2"))

    assert response["status"] == "ok"
    assert response["run_report"]["run_type"] == "run_batch"
    assert response["run_report"]["requested_count"] == 2
    assert response["run_report"]["executed_count"] == 2
    assert response["run_report"]["done_count"] == 2
    assert response["run_report"]["blocked_count"] == 0
    assert Path(response["run_report_paths"]["json_path"]).exists()
    assert Path(response["run_report_paths"]["markdown_path"]).exists()


def test_telegram_run_one_idle_writes_idle_report(tmp_path):
    store = TaskSpecStore(tmp_path / "taskspecs")
    runner = TaskSpecRunner(store, evidence_dir=tmp_path / "evidence" / "taskspecs")
    adapter = TelegramSuperownerAdapter(
        superowner_telegram_user_id=111,
        evidence_dir=tmp_path / "evidence" / "taskspecs",
        store=store,
        runner=runner,
    )

    response = adapter.handle_update(_update(111, "/run_one"))

    assert response["status"] == "idle"
    assert response["run_report"]["idle"] is True
    assert response["run_report"]["executed_count"] == 0
    assert Path(response["run_report_paths"]["json_path"]).exists()
    assert Path(response["run_report_paths"]["markdown_path"]).exists()
