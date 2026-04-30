import subprocess


def test_enqueue_creates_task(tmp_path):
    tasks_dir = tmp_path / "tasks"

    result = subprocess.run(
        [
            "python",
            "-m",
            "app.factory.agent_loop.enqueue_task",
            "--task-id",
            "e1",
            "--objective",
            "test enqueue",
            "--tasks-dir",
            str(tasks_dir),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "e1" in result.stdout


def test_enqueue_file_exists(tmp_path):
    tasks_dir = tmp_path / "tasks"

    subprocess.run(
        [
            "python",
            "-m",
            "app.factory.agent_loop.enqueue_task",
            "--task-id",
            "e2",
            "--objective",
            "test enqueue",
            "--tasks-dir",
            str(tasks_dir),
        ],
        capture_output=True,
        text=True,
    )

    assert (tasks_dir / "e2.json").exists()
