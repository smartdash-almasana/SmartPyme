from pathlib import Path

from app.mcp.tools.factory_control_tool import (
    enqueue_factory_task,
    get_factory_task_status,
    run_factory_once,
)


def test_hermes_factory_operational_smoke(tmp_path):
    tasks_dir = tmp_path / "tasks"
    evidence_dir = tmp_path / "evidence"

    queued = enqueue_factory_task(
        task_id="smoke1",
        objective="validar puente operativo hermes factoría",
        tasks_dir=tasks_dir,
    )

    assert queued["status"] == "queued"

    before = get_factory_task_status("smoke1", tasks_dir=tasks_dir)
    assert before["status"] == "pending"

    run_result = run_factory_once(tasks_dir=tasks_dir, evidence_dir=evidence_dir)
    assert run_result["status"] == "done"
    assert run_result["task_id"] == "smoke1"

    after = get_factory_task_status("smoke1", tasks_dir=tasks_dir)
    assert after["status"] == "done"
    assert after["report_path"] is not None
    assert after["audit"]["status"] == "passed"

    report_path = Path(after["report_path"])
    assert report_path.exists()
    assert "smoke1" in report_path.read_text(encoding="utf-8")
