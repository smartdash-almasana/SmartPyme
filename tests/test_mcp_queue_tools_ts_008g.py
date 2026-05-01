import pytest
import json
from pathlib import Path
from app.mcp.tools.factory_control_tool import (
    get_factory_queue_summary,
    get_factory_queue_details,
    enqueue_factory_task
)
from mcp_smartpyme_bridge import mcp

@pytest.fixture
def temp_tasks_dir(tmp_path):
    d = tmp_path / "tasks"
    d.mkdir()
    return d

def test_summary_empty(temp_tasks_dir):
    res = get_factory_queue_summary(tasks_dir=temp_tasks_dir)
    assert res["status"] == "ok"
    assert res["total"] == 0
    assert res["counts"] == {}
    assert res["next_task"] is None

def test_details_with_pending(temp_tasks_dir):
    enqueue_factory_task("task-1", "Objective 1", tasks_dir=temp_tasks_dir)
    
    res = get_factory_queue_details(tasks_dir=temp_tasks_dir)
    assert res["status"] == "ok"
    assert len(res["tasks"]) == 1
    assert res["tasks"][0]["task_id"] == "task-1"
    assert res["tasks"][0]["status"] == "pending"

def test_details_exclude_done(temp_tasks_dir):
    enqueue_factory_task("task-pending", "Pending", tasks_dir=temp_tasks_dir)
    
    # Create a done task manually
    done_path = temp_tasks_dir / "task-done.json"
    done_path.write_text(json.dumps({
        "task_id": "task-done",
        "status": "done",
        "objective": "Done task"
    }))
    
    # Exclude done (default)
    res = get_factory_queue_details(tasks_dir=temp_tasks_dir, include_done=False)
    assert len(res["tasks"]) == 1
    assert res["tasks"][0]["task_id"] == "task-pending"
    
    # Include done
    res_all = get_factory_queue_details(tasks_dir=temp_tasks_dir, include_done=True)
    assert len(res_all["tasks"]) == 2
    ids = [t["task_id"] for t in res_all["tasks"]]
    assert "task-done" in ids

import asyncio

def test_bridge_exposure():
    async def get_tools():
        return await mcp.list_tools()
    
    tools = asyncio.run(get_tools())
    tool_names = [t.name for t in tools]
    assert "factory_get_queue_summary" in tool_names
    assert "factory_get_queue_details" in tool_names

def test_summary_serialization(temp_tasks_dir):
    enqueue_factory_task("task-1", "Obj", tasks_dir=temp_tasks_dir)
    res = get_factory_queue_summary(tasks_dir=temp_tasks_dir)
    
    # Check if serializable
    dumped = json.dumps(res)
    loaded = json.loads(dumped)
    assert loaded["status"] == "ok"
    assert loaded["total"] == 1
    assert loaded["next_task"]["task_id"] == "task-1"
