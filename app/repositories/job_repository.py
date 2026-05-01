import json
import sqlite3
from pathlib import Path

from app.contracts.job_contract import Job, JobStatus


class JobRepository:
    def __init__(self, cliente_id: str, db_path: str | Path):
        if not cliente_id or not cliente_id.strip():
            raise ValueError("cliente_id is required")

        self.cliente_id = cliente_id
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS background_jobs (
                    cliente_id TEXT NOT NULL,
                    job_id TEXT NOT NULL,
                    job_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    payload TEXT,
                    result TEXT,
                    error_log TEXT,
                    traceable_origin TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (cliente_id, job_id)
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_jobs_cliente
                ON background_jobs(cliente_id)
            """)

    def create(self, job: Job):
        if job.cliente_id != self.cliente_id:
            raise ValueError("cliente_id mismatch")

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO background_jobs
                (cliente_id, job_id, job_type, status, payload, traceable_origin)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                self.cliente_id,
                job.job_id,
                job.job_type,
                job.status.value,
                json.dumps(job.payload or {}),
                json.dumps(job.traceable_origin or {}),
            ))

    def get(self, job_id: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM background_jobs WHERE cliente_id = ? AND job_id = ?",
                (self.cliente_id, job_id),
            ).fetchone()
            if not row:
                return None

            return Job(
                job_id=row["job_id"],
                cliente_id=row["cliente_id"],
                job_type=row["job_type"],
                status=JobStatus(row["status"]),
                payload=json.loads(row["payload"]) if row["payload"] else {},
                result=json.loads(row["result"]) if row["result"] else None,
                error_log=row["error_log"],
                traceable_origin=(
                    json.loads(row["traceable_origin"])
                    if row["traceable_origin"]
                    else {}
                ),
            )

    def list_jobs(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT job_id FROM background_jobs WHERE cliente_id = ? ORDER BY created_at DESC",
                (self.cliente_id,),
            ).fetchall()
        return [self.get(r["job_id"]) for r in rows]

    def mark_running(self, job_id: str):
        self._update_status(job_id, JobStatus.RUNNING)

    def mark_success(self, job_id: str, result: dict):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE background_jobs "
                "SET status=?, result=?, updated_at=CURRENT_TIMESTAMP "
                "WHERE cliente_id=? AND job_id=?",
                (JobStatus.SUCCESS.value, json.dumps(result or {}), self.cliente_id, job_id),
            )

    def mark_failed(self, job_id: str, error_log: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE background_jobs "
                "SET status=?, error_log=?, updated_at=CURRENT_TIMESTAMP "
                "WHERE cliente_id=? AND job_id=?",
                (JobStatus.FAILED.value, error_log, self.cliente_id, job_id),
            )

    def _update_status(self, job_id: str, status: JobStatus):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE background_jobs "
                "SET status=?, updated_at=CURRENT_TIMESTAMP "
                "WHERE cliente_id=? AND job_id=?",
                (status.value, self.cliente_id, job_id),
            )
