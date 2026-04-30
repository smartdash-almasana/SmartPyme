from app.factory.agent_loop.multiagent_task_loop import (
    MultiagentTask,
    run_multiagent_task_cycle,
)


def test_multiagent_task_flow(tmp_path):
    task = MultiagentTask(task_id="t1", objective="test objective")

    result = run_multiagent_task_cycle(task, tmp_path)

    assert result.status == "done"
    assert result.plan != []
    assert result.output is not None
    assert result.audit["status"] == "passed"
    assert result.report_path is not None


def test_multiagent_blocks_when_not_pending(tmp_path):
    task = MultiagentTask(task_id="t2", objective="test", status="in_progress")

    result = run_multiagent_task_cycle(task, tmp_path)

    assert result.status == "blocked"
    assert result.blocking_reason == "TASK_NOT_PENDING"
