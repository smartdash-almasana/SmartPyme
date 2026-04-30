import argparse
import json
from pathlib import Path

from app.factory.agent_loop.multiagent_task_loop import MultiagentTask, save_task


DEFAULT_TASKS_DIR = Path("factory/multiagent/tasks")


def main() -> int:
    parser = argparse.ArgumentParser(description="Enqueue one SmartPyme multiagent task")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--objective", required=True)
    parser.add_argument("--tasks-dir", default=str(DEFAULT_TASKS_DIR))
    args = parser.parse_args()

    task = MultiagentTask(task_id=args.task_id, objective=args.objective)
    path = save_task(task, args.tasks_dir)

    print(json.dumps({
        "status": "queued",
        "task_id": task.task_id,
        "path": path,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
