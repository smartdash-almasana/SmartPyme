import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.repositories.clarification_repository import ClarificationRepository
from app.services.clarification_service import ClarificationService


def _db_path() -> Path:
    base = Path(__file__).resolve().parents[1] / "fixtures" / "tmp_clarification_service"
    base.mkdir(parents=True, exist_ok=True)
    return base / f"clarifications-{uuid.uuid4().hex[:8]}.db"


def _make_service() -> ClarificationService:
    return ClarificationService(ClarificationRepository(_db_path()))


def test_create_blocking_clarification_returns_clarification():
    service = _make_service()
    c = service.create_blocking_clarification(
        question="¿El monto es correcto?",
        reason="Diferencia detectada",
        job_id="job-1",
    )

    assert c.clarification_id.startswith("clarif_")
    assert c.question == "¿El monto es correcto?"
    assert c.reason == "Diferencia detectada"
    assert c.job_id == "job-1"
    assert c.status == "pending"
    assert c.blocking is True
    assert c.answer is None


def test_create_blocking_clarification_persists():
    service = _make_service()
    service.create_blocking_clarification(
        question="¿El CUIT es válido?",
        reason="No encontrado en padrón",
        job_id="job-2",
    )

    assert service.has_pending_blockers(job_id="job-2") is True


def test_create_blocking_clarification_id_is_deterministic():
    repo = ClarificationRepository(_db_path())
    service = ClarificationService(repo)

    c1 = service.create_blocking_clarification(
        question="¿Mismo monto?", reason="Diferencia", job_id="job-x"
    )
    c2 = service.create_blocking_clarification(
        question="¿Mismo monto?", reason="Diferencia", job_id="job-x"
    )

    assert c1.clarification_id == c2.clarification_id
    # Idempotent save — still only one pending.
    assert len(service.repository.list_pending()) == 1


def test_answer_clarification_removes_from_pending():
    service = _make_service()
    c = service.create_blocking_clarification(
        question="¿Confirmar diferencia?",
        reason="Monto distinto",
        job_id="job-3",
    )

    assert service.has_pending_blockers(job_id="job-3") is True

    service.answer_clarification(c.clarification_id, answer="Confirmado.")

    assert service.has_pending_blockers(job_id="job-3") is False


def test_has_pending_blockers_false_when_no_clarifications():
    service = _make_service()
    assert service.has_pending_blockers() is False
    assert service.has_pending_blockers(job_id="job-none") is False


def test_has_pending_blockers_scoped_by_job_id():
    service = _make_service()
    service.create_blocking_clarification(
        question="¿Monto A?", reason="Diferencia A", job_id="job-a"
    )
    service.create_blocking_clarification(
        question="¿Monto B?", reason="Diferencia B", job_id="job-b"
    )

    assert service.has_pending_blockers(job_id="job-a") is True
    assert service.has_pending_blockers(job_id="job-b") is True
    assert service.has_pending_blockers(job_id="job-c") is False


def test_create_blocking_clarification_preserves_traceable_origin():
    service = _make_service()
    origin = {"finding_id": "f-99", "metric": "amount"}
    c = service.create_blocking_clarification(
        question="¿Diferencia esperada?",
        reason="Monto fuera de rango",
        job_id="job-trace",
        traceable_origin=origin,
    )

    assert c.traceable_origin == origin
    pending = service.repository.list_pending(job_id="job-trace")
    assert pending[0].traceable_origin == origin
