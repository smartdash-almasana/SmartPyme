from app.mcp.tools.factory_control_tool import (
    enqueue_factory_task,
    get_factory_task_status,
    run_factory_once,
)


def test_factory_control_enqueue_and_status(tmp_path):
    tasks_dir = tmp_path / "tasks"

    queued = enqueue_factory_task("h1", "hacer prueba", tasks_dir=tasks_dir)
    status = get_factory_task_status("h1", tasks_dir=tasks_dir)

    assert queued["status"] == "queued"
    assert status["status"] == "pending"
    assert status["task_id"] == "h1"
    assert status["objective"] == "hacer prueba"


def test_factory_control_run_once(tmp_path):
    tasks_dir = tmp_path / "tasks"
    evidence_dir = tmp_path / "evidence"

    enqueue_factory_task("h2", "ejecutar ciclo", tasks_dir=tasks_dir)
    run_result = run_factory_once(tasks_dir=tasks_dir, evidence_dir=evidence_dir)
    status = get_factory_task_status("h2", tasks_dir=tasks_dir)

    assert run_result["status"] == "done"
    assert run_result["task_id"] == "h2"
    assert status["status"] == "done"
    assert status["report_path"] is not None


def test_factory_control_missing_task(tmp_path):
    status = get_factory_task_status("missing", tasks_dir=tmp_path)

    assert status["status"] == "not_found"
    assert status["task_id"] == "missing"
