from pathlib import Path

from factory.core.run_report import (
    build_factory_run_report,
    factory_run_report_from_dict,
    write_factory_run_report,
)
from factory.core.task_spec import TaskSpec, TaskSpecStatus
from factory.core.task_spec_runner import CommandResult, TaskSpecRunResult, TaskSpecRunner
from factory.core.task_spec_store import TaskSpecStore


def _task(task_id="FM_025"):
    return TaskSpec(
        task_id=task_id,
        title="Reportar changed_paths reales",
        objective="Incluir changed_paths en FactoryRunReport",
        allowed_paths=["factory/core", "tests/factory"],
        forbidden_paths=["app"],
        acceptance_criteria=["run report contiene changed_paths"],
        validation_commands=["pytest fake"],
    )


def _ok_runner(command: str) -> CommandResult:
    return CommandResult(command=command, exit_code=0, stdout="ok", stderr="")


def test_task_spec_runner_result_exposes_changed_paths(tmp_path):
    store = TaskSpecStore(tmp_path / "taskspecs")
    store.enqueue(_task())
    runner = TaskSpecRunner(
        store,
        evidence_dir=tmp_path / "evidence",
        changed_paths_provider=lambda task: [
            "factory/core/run_report.py",
            "tests/factory/test_run_report_changed_paths_fm_025.py",
        ],
        command_runner=_ok_runner,
    )

    result = runner.run_task("FM_025")

    assert result.status == TaskSpecStatus.DONE
    assert result.changed_paths == [
        "factory/core/run_report.py",
        "tests/factory/test_run_report_changed_paths_fm_025.py",
    ]


def test_factory_run_report_includes_changed_paths_in_dict_json_and_markdown(tmp_path):
    report = build_factory_run_report(
        run_type="run_one",
        requested_count=1,
        results=[
            TaskSpecRunResult(
                status=TaskSpecStatus.DONE,
                task_id="FM_025",
                evidence_paths=["evidence/paths.txt"],
                command_results=[CommandResult("pytest fake", 0)],
                changed_paths=[
                    "factory/core/run_report.py",
                    "tests/factory/test_run_report_changed_paths_fm_025.py",
                ],
            )
        ],
    )

    data = report.to_dict()
    markdown = report.to_markdown()
    paths = write_factory_run_report(report, tmp_path / "evidence")

    assert data["task_results"][0]["changed_paths"] == [
        "factory/core/run_report.py",
        "tests/factory/test_run_report_changed_paths_fm_025.py",
    ]
    assert "- changed_paths:" in markdown
    assert "factory/core/run_report.py" in markdown
    assert "changed_paths" in Path(paths["json_path"]).read_text(encoding="utf-8")
    assert "factory/core/run_report.py" in Path(paths["markdown_path"]).read_text(encoding="utf-8")


def test_factory_run_report_from_dict_keeps_changed_paths():
    report = factory_run_report_from_dict(
        {
            "report_id": "factory-run-test",
            "run_type": "run_one",
            "requested_count": 1,
            "executed_count": 1,
            "done_count": 1,
            "blocked_count": 0,
            "idle": False,
            "created_at": "2026-04-30T00:00:00+00:00",
            "metadata": {},
            "task_results": [
                {
                    "task_id": "FM_025",
                    "status": "done",
                    "evidence_paths": [],
                    "blocking_reason": None,
                    "command_exit_codes": [0],
                    "changed_paths": ["factory/core/run_report.py"],
                    "path_errors": [],
                }
            ],
        }
    )

    assert report.task_results[0].changed_paths == ["factory/core/run_report.py"]


def test_factory_run_report_from_dict_supports_legacy_reports_without_changed_paths():
    report = factory_run_report_from_dict(
        {
            "report_id": "factory-run-legacy",
            "run_type": "run_one",
            "requested_count": 1,
            "executed_count": 1,
            "done_count": 1,
            "blocked_count": 0,
            "idle": False,
            "created_at": "2026-04-30T00:00:00+00:00",
            "metadata": {},
            "task_results": [
                {
                    "task_id": "FM_020",
                    "status": "done",
                    "evidence_paths": [],
                    "blocking_reason": None,
                    "command_exit_codes": [0],
                    "path_errors": [],
                }
            ],
        }
    )

    assert report.task_results[0].changed_paths == []
