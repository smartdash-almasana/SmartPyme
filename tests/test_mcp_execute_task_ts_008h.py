import pytest
import json
import asyncio
from pathlib import Path
from app.mcp.tools.factory_control_tool import (
    get_next_task_preview,
    execute_one_task_by_id,
    enqueue_factory_task
)
from mcp_smartpyme_bridge import mcp

@pytest.fixture
def temp_dirs(tmp_path):
    tasks = tmp_path / "tasks"
    evidence = tmp_path / "evidence"
    tasks.mkdir()
    evidence.mkdir()
    return tasks, evidence

def test_preview_empty(temp_dirs):
    tasks_dir, _ = temp_dirs
    res = get_next_task_preview(tasks_dir=tasks_dir)
    assert res["status"] == "idle"
    assert res["task"] is None

def test_preview_pending(temp_dirs):
    tasks_dir, _ = temp_dirs
    enqueue_factory_task("task-1", "Obj 1", tasks_dir=tasks_dir)
    
    # Preview should not change status
    res = get_next_task_preview(tasks_dir=tasks_dir)
    assert res["status"] == "ok"
    assert res["task"]["task_id"] == "task-1"
    assert res["task"]["status"] == "pending"
    
    # Verify file is still pending
    with open(tasks_dir / "task-1.json", "r") as f:
        data = json.load(f)
        assert data["status"] == "pending"

def test_execute_nonexistent(temp_dirs):
    tasks_dir, _ = temp_dirs
    res = execute_one_task_by_id("no-task", tasks_dir=tasks_dir)
    assert res["status"] == "error"
    assert "not found" in res["reason"]

def test_execute_reject_done(temp_dirs):
    tasks_dir, _ = temp_dirs
    path = tasks_dir / "task-done.json"
    path.write_text(json.dumps({
        "task_id": "task-done",
        "status": "done",
        "objective": "done"
    }))
    
    res = execute_one_task_by_id("task-done", tasks_dir=tasks_dir)
    assert res["status"] == "error"
    assert "expected pending" in res["reason"]

def test_execute_pending_success(temp_dirs):
    tasks_dir, evidence_dir = temp_dirs
    enqueue_factory_task("task-run", "Run me", tasks_dir=tasks_dir)
    
    res = execute_one_task_by_id("task-run", tasks_dir=tasks_dir, evidence_dir=evidence_dir)
    assert res["status"] == "done"
    assert res["task_id"] == "task-run"
    
    # Verify file is now done
    with open(tasks_dir / "task-run.json", "r") as f:
        data = json.load(f)
        assert data["status"] == "done"

def test_bridge_registration():
    async def get_tools():
        return await mcp.list_tools()
    
    tools = asyncio.run(get_tools())
    tool_names = [t.name for t in tools]
    assert "factory_preview_next_task" in tool_names
    assert "factory_execute_task" in tool_names
