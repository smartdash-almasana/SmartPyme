from pathlib import Path

from app.adapters.telegram_adapter import TelegramAdapter
from app.contracts.bem_evidence_contract import BemDocumentType, BemEvidenceStatus
from app.factory.agent_loop.multiagent_task_loop import load_task
from app.mcp.tools.factory_control_tool import enqueue_factory_task
from app.repositories.evidence_candidate_repository import EvidenceCandidateRepository
from app.services.document_intake_service import DocumentIntakeService
from app.services.identity_service import IdentityService


def _document_update(user_id: int, file_id: str, file_name: str, mime_type: str) -> dict:
    return {
        "message": {
            "from": {"id": user_id},
            "document": {
                "file_id": file_id,
                "file_name": file_name,
                "mime_type": mime_type,
            },
        }
    }


def _linked_identity(tmp_path: Path, user_id: int = 111, cliente_id: str = "pyme_A") -> IdentityService:
    identity = IdentityService(tmp_path / "identity.db")
    identity.create_onboarding_token("token-a", cliente_id)
    linked = identity.link_telegram_user(user_id, "token-a")
    assert linked["status"] == "linked"
    return identity


def test_telegram_document_intake_persists_evidence_candidate_and_queues_task(tmp_path):
    tasks_dir = tmp_path / "tasks"
    evidence_db = tmp_path / "evidence_candidates.db"
    identity = _linked_identity(tmp_path)

    def enqueuer(task_id, objective, task_type=None, payload=None):
        return enqueue_factory_task(
            task_id=task_id,
            objective=objective,
            tasks_dir=tasks_dir,
            task_type=task_type,
            payload=payload,
        )

    adapter = TelegramAdapter(
        identity_service=identity,
        factory_task_enqueuer=enqueuer,
        document_intake_service=DocumentIntakeService(evidence_db),
    )

    response = adapter.handle_update(
        _document_update(111, "file-123", "factura.pdf", "application/pdf")
    )

    assert response["status"] == "queued"
    assert response["cliente_id"] == "pyme_A"
    assert response["evidence_candidate"]["cliente_id"] == "pyme_A"
    assert response["evidence_candidate"]["status"] == BemEvidenceStatus.CANDIDATE.value
    assert response["evidence_candidate"]["document_type"] == BemDocumentType.UNKNOWN.value
    assert response["evidence_candidate"]["metadata"]["origin"] == "telegram"
    assert response["evidence_candidate"]["metadata"]["truth_status"] == "candidate_not_fact"
    assert response["evidence_candidate"]["metadata"]["bem_real_used"] is False

    evidence_id = response["evidence_candidate"]["evidence_id"]
    persisted = EvidenceCandidateRepository("pyme_A", evidence_db).get(evidence_id)
    assert persisted is not None
    assert persisted.cliente_id == "pyme_A"
    assert persisted.status == BemEvidenceStatus.CANDIDATE
    assert persisted.document_type == BemDocumentType.UNKNOWN
    assert persisted.storage_ref == "telegram_file:file-123"

    task = load_task(response["task"]["task_id"], tasks_dir)
    assert task is not None
    assert task.status == "pending"
    assert task.task_type is None
    assert "Procesar evidencia Telegram" in task.objective


def test_evidence_candidate_repository_isolated_by_cliente_id(tmp_path):
    service = DocumentIntakeService(tmp_path / "evidence_candidates.db")
    candidate = service.register_telegram_document_candidate(
        cliente_id="pyme_A",
        telegram_user_id=111,
        file_id="file-123",
        file_name="ventas.csv",
        mime_type="text/csv",
    )

    assert EvidenceCandidateRepository("pyme_A", tmp_path / "evidence_candidates.db").get(
        candidate.evidence_id
    ) is not None
    assert EvidenceCandidateRepository("pyme_B", tmp_path / "evidence_candidates.db").get(
        candidate.evidence_id
    ) is None


def test_telegram_document_intake_rejects_unlinked_user_without_candidate(tmp_path):
    evidence_db = tmp_path / "evidence_candidates.db"
    identity = IdentityService(tmp_path / "identity.db")
    adapter = TelegramAdapter(
        identity_service=identity,
        document_intake_service=DocumentIntakeService(evidence_db),
    )

    response = adapter.handle_update(
        _document_update(999, "file-999", "factura.pdf", "application/pdf")
    )

    assert response["status"] == "unauthorized"
    assert not evidence_db.exists()


def test_telegram_document_intake_rejects_unsupported_document_without_candidate(tmp_path):
    evidence_db = tmp_path / "evidence_candidates.db"
    identity = _linked_identity(tmp_path)
    adapter = TelegramAdapter(
        identity_service=identity,
        document_intake_service=DocumentIntakeService(evidence_db),
    )

    response = adapter.handle_update(
        _document_update(111, "file-zip", "archivo.zip", "application/zip")
    )

    assert response["status"] == "unsupported_document"
    assert not evidence_db.exists()
