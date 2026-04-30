import json
import subprocess


def test_enqueue_then_run_once_e2e(tmp_path):
    tasks_dir = tmp_path / "tasks"
    evidence_dir = tmp_path / "evidence"

    enqueue = subprocess.run(
        [
            "python",
            "-m",
            "app.factory.agent_loop.enqueue_task",
            "--task-id",
            "e2e1",
            "--objective",
            "end to end smoke",
            "--tasks-dir",
            str(tasks_dir),
        ],
        capture_output=True,
        text=True,
    )

    assert enqueue.returncode == 0
    assert (tasks_dir / "e2e1.json").exists()

    run = subprocess.run(
        [
            "python",
            "-m",
            "app.factory.agent_loop.run_queue_once",
            "--tasks-dir",
            str(tasks_dir),
            "--evidence-dir",
            str(evidence_dir),
        ],
        capture_output=True,
        text=True,
    )

    assert run.returncode == 0
    assert "e2e1" in run.stdout

    task_data = json.loads((tasks_dir / "e2e1.json").read_text(encoding="utf-8"))
    assert task_data["status"] == "done"
    assert task_data["report_path"] is not None

    report_path = tmp_path / "evidence" / "e2e1.txt"
    assert report_path.exists()
