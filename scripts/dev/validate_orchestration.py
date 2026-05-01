# End-to-end validation script for the orchestrator with persistence.
import json
import os
import uuid

from app.factory.orchestrator.models import STATE_CREATED, Job
from app.factory.orchestrator.persistence import _get_db_path, init_jobs_db, save_job
from app.factory.orchestrator.service import orchestrate_job
from app.factory.skills.registry import SkillRegistry


# Define a dummy skill for the orchestrator to execute
def echo_skill(payload: dict) -> dict:
    message = payload.get("message", "default_message")
    return {"status": "ok", "output": {"echo": message}}

def validate():
    # 1. Clean and initialize the database
    db_path = _get_db_path()
    if os.path.exists(db_path):
        os.remove(db_path)
    init_jobs_db()
    print(f"Database initialized at: {db_path}")

    # 2. Register the dummy skill
    skill_registry = SkillRegistry()
    skill_registry.register("echo_skill", echo_skill)
    print("Dummy 'echo_skill' registered.")

    # 3. Create a new Job and save its initial state
    job_id = f"orch-val-{uuid.uuid4().hex[:8]}"
    new_job = Job(
        job_id=job_id,
        current_state=STATE_CREATED,
        status="created",
        skill_id="echo_skill",
        payload={"message": "Persistence works!"}
    )
    save_job(new_job)
    print(f"Initial job created and saved with job_id: {job_id}")

    # 4. Run the orchestration
    print("Running orchestrate_job...")
    final_job_state = orchestrate_job(new_job, registry=skill_registry)

    # 5. Print the final state from the orchestrator's return value
    print("--- Orchestrator Final State ---")
    print(f"  Job ID: {final_job_state.job_id}")
    print(f"  Status: {final_job_state.status}")
    print(f"  State: {final_job_state.current_state}")
    print(f"  Output: {json.dumps(final_job_state.output)}")

if __name__ == "__main__":
    validate()
