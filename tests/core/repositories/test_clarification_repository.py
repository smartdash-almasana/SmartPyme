import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from app.contracts.clarification_contract import Clarification
from app.repositories.clarification_repository import ClarificationRepository


def _db_path() -> Path:
    base = Path(__file__).resolve().parents[2] / "fixtures" / "tmp_clarification_repository"
    base.mkdir(parents=True, exist_ok=True)
    return base / f"clarifications-{uuid.uuid4().hex[:8]}.db"


def _clarification(
    clarification_id: str = "clarif-1",
    *,
    job_id: str | None = "job-1",
    question: str = "¿El monto es correcto?",
    reason: str = "Diferencia detectada",
    status: str = "pending",
    blocking: bool = True,
    answer: str | None = None,
    traceable_origin: dict | None = None,
) -> Clarification:
    return Clarification(
        clarification_id=clarification_id,
        job_id=job_id,
        question=question,
        reason=reason,
        status=status,
        blocking=blocking,
        answer=answer,
        traceable_origin=traceable_origin or {},
    )


def test_clarification_repository_save_and_list_pending():
    repo = ClarificationRepository(_db_path())
    repo.save(_clarification("c-1"))

    pending = repo.list_pending()
    assert len(pending) == 1
    c = pending[0]
    assert c.clarification_id == "c-1"
    assert c.status == "pending"
    assert c.blocking is True


def test_clarification_repository_save_batch():
    repo = ClarificationRepository(_db_path())
    repo.save_batch([
        _clarification("c-1", job_id="job-a"),
        _clarification("c-2", job_id="job-b"),
        _clarification("c-3", job_id="job-a"),
    ])

    all_pending = repo.list_pending()
    assert len(all_pending) == 3

    job_a_pending = repo.list_pending(job_id="job-a")
    assert len(job_a_pending) == 2

    job_b_pending = repo.list_pending(job_id="job-b")
    assert len(job_b_pending) == 1


def test_clarification_repository_idempotent_by_clarification_id():
    repo = ClarificationRepository(_db_path())
    repo.save(_clarification("c-1", question="Pregunta original"))
    repo.save(_clarification("c-1", question="Pregunta actualizada"))

    pending = repo.list_pending()
    assert len(pending) == 1
    assert pending[0].question == "Pregunta actualizada"


def test_clarification_repository_mark_answered():
    repo = ClarificationRepository(_db_path())
    repo.save(_clarification("c-1"))

    repo.mark_answered("c-1", answer="Sí, el monto es correcto.")

    pending = repo.list_pending()
    assert len(pending) == 0


def test_clarification_repository_has_pending_true():
    repo = ClarificationRepository(_db_path())
    repo.save(_clarification("c-1", blocking=True))

    assert repo.has_pending() is True


def test_clarification_repository_has_pending_false_when_answered():
    repo = ClarificationRepository(_db_path())
    repo.save(_clarification("c-1", blocking=True))
    repo.mark_answered("c-1", answer="Confirmado.")

    assert repo.has_pending() is False


def test_clarification_repository_has_pending_false_when_non_blocking():
    repo = ClarificationRepository(_db_path())
    repo.save(_clarification("c-1", blocking=False))

    # Non-blocking clarifications do not count as blockers.
    assert repo.has_pending() is False


def test_clarification_repository_has_pending_scoped_by_job_id():
    repo = ClarificationRepository(_db_path())
    repo.save(_clarification("c-1", job_id="job-x", blocking=True))
    repo.save(_clarification("c-2", job_id="job-y", blocking=True))

    assert repo.has_pending(job_id="job-x") is True
    assert repo.has_pending(job_id="job-y") is True

    repo.mark_answered("c-1", answer="OK")
    assert repo.has_pending(job_id="job-x") is False
    assert repo.has_pending(job_id="job-y") is True


def test_clarification_repository_preserves_traceable_origin():
    origin = {"finding_id": "f-1", "metric": "price"}
    repo = ClarificationRepository(_db_path())
    repo.save(_clarification("c-1", traceable_origin=origin))

    pending = repo.list_pending()
    assert pending[0].traceable_origin == origin


def test_clarification_repository_list_pending_empty():
    repo = ClarificationRepository(_db_path())
    assert repo.list_pending() == []
    assert repo.has_pending() is False
