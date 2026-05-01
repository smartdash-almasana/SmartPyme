from pathlib import Path

from app.mcp.tools.queue_list_tool import get_next_factory_task, list_factory_queue
from factory.adapters.app_bridge.agent_loop.multiagent_task_loop import MultiagentTask, save_task


def test_queue_list_empty_returns_total_zero(tmp_path):
    tasks_dir = tmp_path / "tasks"
    result = list_factory_queue(tasks_dir)
    assert result["status"] == "ok"
    assert result["total"] == 0
    assert result["tasks"] == []


def test_queue_list_includes_pending(tmp_path):
    tasks_dir = tmp_path / "tasks"
    save_task(MultiagentTask(task_id="t1", objective="obj1", status="pending"), tasks_dir)

    result = list_factory_queue(tasks_dir)
    assert result["total"] == 1
    assert result["tasks"][0]["task_id"] == "t1"
    assert result["tasks"][0]["status"] == "pending"


def test_queue_list_excludes_done_by_default(tmp_path):
    tasks_dir = tmp_path / "tasks"
    save_task(MultiagentTask(task_id="t1", objective="obj1", status="done"), tasks_dir)
    save_task(MultiagentTask(task_id="t2", objective="obj2", status="pending"), tasks_dir)

    result = list_factory_queue(tasks_dir)
    assert result["total"] == 2
    assert len(result["tasks"]) == 1
    assert result["tasks"][0]["task_id"] == "t2"


def test_queue_list_includes_done_if_requested(tmp_path):
    tasks_dir = tmp_path / "tasks"
    save_task(MultiagentTask(task_id="t1", objective="obj1", status="done"), tasks_dir)

    result = list_factory_queue(tasks_dir, include_done=True)
    assert len(result["tasks"]) == 1
    assert result["tasks"][0]["task_id"] == "t1"


def test_get_next_factory_task_returns_first_pending(tmp_path):
    tasks_dir = tmp_path / "tasks"
    save_task(MultiagentTask(task_id="t1", objective="obj1", status="done"), tasks_dir)
    save_task(MultiagentTask(task_id="t2", objective="obj2", status="pending"), tasks_dir)
    save_task(MultiagentTask(task_id="t3", objective="obj3", status="pending"), tasks_dir)

    result = get_next_factory_task(tasks_dir)
    assert result["status"] == "ok"
    assert result["task"]["task_id"] == "t2"


def test_get_next_factory_task_returns_none_if_none_pending(tmp_path):
    tasks_dir = tmp_path / "tasks"
    save_task(MultiagentTask(task_id="t1", objective="obj1", status="done"), tasks_dir)

    result = get_next_factory_task(tasks_dir)
    assert result["status"] == "ok"
    assert result["task"] is None


def test_queue_list_supports_subfolders(tmp_path):
    tasks_dir = tmp_path / "tasks"
    pending_dir = tasks_dir / "pending"
    done_dir = tasks_dir / "done"

    save_task(MultiagentTask(task_id="t_p", objective="obj_p", status="pending"), pending_dir)
    save_task(MultiagentTask(task_id="t_d", objective="obj_d", status="done"), done_dir)

    result = list_factory_queue(tasks_dir, include_done=True)
    assert result["total"] == 2
    assert result["counts"]["pending"] == 1
    assert result["counts"]["done"] == 1
    ids = {t["task_id"] for t in result["tasks"]}
    assert ids == {"t_p", "t_d"}
