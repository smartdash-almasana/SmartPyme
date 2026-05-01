import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path

from app.factory.orchestrator.models import Job

# Consistent pattern with clarifications persistence
DEFAULT_DB_PATH = Path(__file__).resolve().parents[3] / "data" / "jobs.db"

def _get_db_path() -> Path:
    raw_path = os.getenv("SMARTPYME_JOBS_DB")
    if raw_path:
        return Path(raw_path)
    return DEFAULT_DB_PATH

def _get_connection() -> sqlite3.Connection:
    db_path = _get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row # Allows accessing columns by name
    return conn

def init_jobs_db() -> None:
    with _get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                job_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                current_state TEXT,
                skill_id TEXT,
                payload_json TEXT,
                blocking_reason TEXT,
                evidence_count INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        _ensure_column(connection, "skill_id", "TEXT")
        _ensure_column(connection, "payload_json", "TEXT")


def _ensure_column(connection: sqlite3.Connection, column_name: str, column_type: str) -> None:
    columns = {
        str(row["name"])
        for row in connection.execute("PRAGMA table_info(jobs)").fetchall()
    }
    if column_name not in columns:
        connection.execute(f"ALTER TABLE jobs ADD COLUMN {column_name} {column_type}")


def _serialize_payload(payload: dict) -> str:
    return json.dumps(payload or {}, ensure_ascii=False, sort_keys=True)


def _parse_payload(payload_json: str | None) -> dict:
    if not payload_json:
        return {}
    try:
        parsed = json.loads(payload_json)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}

def save_job(job: Job) -> None:
    init_jobs_db()
    now = datetime.utcnow().isoformat()
    with _get_connection() as connection:
        # Check if job exists
        cursor = connection.execute("SELECT job_id FROM jobs WHERE job_id = ?", (job.job_id,))
        exists = cursor.fetchone()

        if exists:
            # Update existing job
            connection.execute(
                """
                UPDATE jobs SET
                    status = ?,
                    current_state = ?,
                    skill_id = ?,
                    payload_json = ?,
                    blocking_reason = ?,
                    updated_at = ?
                WHERE job_id = ?
                """,
                (
                    job.status,
                    job.current_state,
                    job.skill_id,
                    _serialize_payload(job.payload),
                    job.blocking_reason,
                    now,
                    job.job_id,
                )
            )
        else:
            # Insert new job
            connection.execute(
                """
                INSERT INTO jobs (
                    job_id,
                    status,
                    current_state,
                    skill_id,
                    payload_json,
                    blocking_reason,
                    evidence_count,
                    created_at,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job.job_id,
                    job.status,
                    job.current_state,
                    job.skill_id,
                    _serialize_payload(job.payload),
                    job.blocking_reason,
                    0,
                    now,
                    now,
                )
            )

def get_job(job_id: str) -> dict | None:
    init_jobs_db()
    with _get_connection() as connection:
        cursor = connection.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,))
        row = cursor.fetchone()

    if row:
        job_data = dict(row)
        job_data["payload"] = _parse_payload(job_data.get("payload_json"))
        return job_data
    return None
