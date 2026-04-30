from app.factory.agent_loop.multiagent_task_loop import (
    MultiagentTask,
    save_task,
    load_task,
    run_persisted_multiagent_task_cycle,
)


def test_save_and_load_task(tmp_path):
    task = MultiagentTask(task_id="t1", objective="persist test")

    save_task(task, tmp_path)
    loaded = load_task("t1", tmp_path)

    assert loaded is not None
    assert loaded.task_id == "t1"
    assert loaded.objective == "persist test"


def test_run_persisted_cycle(tmp_path):
    task = MultiagentTask(task_id="t2", objective="cycle test")
    save_task(task, tmp_path)

    result = run_persisted_multiagent_task_cycle("t2", tmp_path, tmp_path)

    assert result is not None
    assert result.status == "done"

    loaded = load_task("t2", tmp_path)
    assert loaded.status == "done"
