import argparse
import json
from pathlib import Path

from app.factory.agent_loop.queue_runner import run_one_queued_task


DEFAULT_TASKS_DIR = Path("factory/multiagent/tasks")
DEFAULT_EVIDENCE_DIR = Path("factory/multiagent/evidence")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one SmartPyme multiagent queued task")
    parser.add_argument("--tasks-dir", default=str(DEFAULT_TASKS_DIR))
    parser.add_argument("--evidence-dir", default=str(DEFAULT_EVIDENCE_DIR))
    args = parser.parse_args()

    result = run_one_queued_task(args.tasks_dir, args.evidence_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))

    if result["status"] == "blocked":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
