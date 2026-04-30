from pathlib import Path

from app.core.pipeline import Pipeline
from app.repositories.canonical_repository import CanonicalRepository
from app.repositories.entity_repository import EntityRepository
from app.repositories.fact_repository import FactRepository
from app.repositories.finding_repository import FindingRepository
from app.repositories.job_repository import JobRepository


class JobWorker:
    def __init__(self, cliente_id: str, db_base_path: str | Path):
        if not cliente_id:
            raise ValueError("cliente_id is required for JobWorker")

        self.cliente_id = cliente_id
        self.db_base_path = Path(db_base_path)
        self.db_base_path.mkdir(parents=True, exist_ok=True)

        self.jobs = JobRepository(cliente_id, self.db_base_path / "jobs.db")
        self.facts = FactRepository(self.db_base_path / "facts.db")
        self.canonical = CanonicalRepository(self.db_base_path / "canonical.db")
        self.entities = EntityRepository(cliente_id, self.db_base_path / "entities.db")
        self.findings = FindingRepository(cliente_id, self.db_base_path / "findings.db")

    def run(self, job_id: str, payload: dict):
        job = self.jobs.get(job_id)
        if job is None:
            return None

        self.jobs.mark_running(job_id)

        try:
            pipeline = Pipeline(
                cliente_id=self.cliente_id,
                fact_repo=self.facts,
                canonical_repo=self.canonical,
                entity_repo=self.entities,
                finding_repo=self.findings,
            )

            result = pipeline.process_texts(
                payload["evidence_id_a"],
                payload["text_a"],
                payload["evidence_id_b"],
                payload["text_b"],
                job_id=job_id,
            )

            self.jobs.mark_success(job_id, {
                "status": result.status,
                "findings": len(result.findings),
            })
            return result

        except Exception as exc:
            self.jobs.mark_failed(job_id, str(exc))
            return None
