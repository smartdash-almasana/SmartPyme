import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.repositories.fact_repository import FactRepository
from app.services.fact_extraction_service import FactExtractionService


def _db_path() -> Path:
    base = Path(__file__).resolve().parents[1] / "fixtures" / "tmp_fact_extraction"
    base.mkdir(parents=True, exist_ok=True)
    return base / f"facts-{uuid.uuid4().hex[:8]}.db"


def test_extract_from_evidence_detects_amount_date_and_cuit():
    repo = FactRepository(_db_path())
    service = FactExtractionService(repo)

    result = service.extract_from_evidence(
        cliente_id="test-client",
        evidence_id="ev-1",
        text="Factura 20-12345678-3 emitida el 15/04/2026 por $1500.25.",
    )
    facts = repo.list_facts(evidence_id="ev-1")

    assert result["status"] == "EXTRACTED"
    assert result["evidence_id"] == "ev-1"
    assert result["facts_count"] == 3
    assert len(result["fact_ids"]) == 3
    assert {fact.data["fact_type"] for fact in facts} == {"amount", "date", "cuit"}
    assert {fact.data["value"] for fact in facts} >= {"1500.25", "15/04/2026", "20-12345678-3"}


def test_extract_from_evidence_without_known_data_returns_zero():
    repo = FactRepository(_db_path())
    service = FactExtractionService(repo)

    result = service.extract_from_evidence(
        cliente_id="test-client",
        evidence_id="ev-empty",
        text="Texto sin datos estructurados.",
    )

    assert result == {
        "status": "EXTRACTED",
        "evidence_id": "ev-empty",
        "facts_count": 0,
        "fact_ids": [],
    }
    assert repo.list_facts(evidence_id="ev-empty") == []
