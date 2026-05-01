import subprocess
import sys
from pathlib import Path
from factory.adapters.app_bridge.agent_loop.multiagent_task_loop import MultiagentTask, save_task


def test_cli_runner_executes_one_task(tmp_path):
    tasks_dir = tmp_path / "tasks"
    evidence_dir = tmp_path / "evidence"

    task = MultiagentTask(task_id="cli1", objective="cli test")
    save_task(task, tasks_dir)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "factory.adapters.app_bridge.agent_loop.run_queue_once",
            "--tasks-dir",
            str(tasks_dir),
            "--evidence-dir",
            str(evidence_dir),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "cli1" in result.stdout


def test_cli_runner_idle(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "factory.adapters.app_bridge.agent_loop.run_queue_once",
            "--tasks-dir",
            str(tmp_path),
            "--evidence-dir",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "idle" in result.stdout.lower()
