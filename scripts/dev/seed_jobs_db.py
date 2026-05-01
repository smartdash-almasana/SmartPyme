# This is a standalone script to seed the jobs database for validation.

from app.orchestrator.models import STATE_CREATED, Job
from app.orchestrator.persistence import init_jobs_db, save_job


def seed():
    print("Initializing jobs database...")
    init_jobs_db()
    
    print("Seeding with test job 'seed-job-001'...")
    
    # Create a simple job object that matches the model
    # We are in CREATED state, so some fields can be None
    seed_job = Job(
        job_id="seed-job-001",
        current_state=STATE_CREATED,
        status="created",
        skill_id="test_skill",
        payload={"message": "hello from seed"},
        output=None,
        blocking_reason=None,
        error_code=None
    )
    
    save_job(seed_job)
    
    print("Seeding complete.")

if __name__ == "__main__":
    seed()
