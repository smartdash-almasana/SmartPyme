from app.factory.agent_loop.multiagent_task_loop import MultiagentTask, save_task
from app.factory.agent_loop.queue_runner import run_one_queued_task


def test_run_one_pending_task(tmp_path):
    task = MultiagentTask(task_id="q1", objective="queue test")
    save_task(task, tmp_path)

    result = run_one_queued_task(tmp_path, tmp_path)

    assert result["task_id"] == "q1"
    assert result["status"] == "done"


def test_queue_idle(tmp_path):
    result = run_one_queued_task(tmp_path, tmp_path)

    assert result["status"] == "idle"
    assert result["task_id"] is None
