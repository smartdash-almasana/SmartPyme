import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.contracts.evidence_contract import ExtractedFactCandidate
from app.repositories.canonical_repository import CanonicalRepository
from app.services.canonicalization_service import CanonicalizationService


def _db_path() -> Path:
    base = Path(__file__).resolve().parents[1] / "fixtures" / "tmp_canonicalization"
    base.mkdir(parents=True, exist_ok=True)
    return base / f"canonical-{uuid.uuid4().hex[:8]}.db"


def _fact(fact_candidate_id: str, *, fact_type: str, value: str) -> ExtractedFactCandidate:
    return ExtractedFactCandidate(
        fact_candidate_id=fact_candidate_id,
        evidence_id="ev-1",
        job_id=None,
        plan_id=None,
        schema_name=f"simple_{fact_type}",
        data={"fact_type": fact_type, "value": value},
        confidence=1.0,
        extraction_method="test",
    )


def test_canonicalize_facts_creates_canonical_rows():
    repo = CanonicalRepository(_db_path())
    service = CanonicalizationService(repo)

    facts = [
        _fact("fact-1", fact_type="amount", value="100.00"),
        _fact("fact-2", fact_type="date", value="2026-04-25"),
    ]
    result = service.canonicalize_facts(facts, job_id="job-1")

    rows = repo.list_canonical_rows()

    assert result["status"] == "CANONICALIZED"
    assert result["job_id"] == "job-1"
    assert result["canonical_rows_count"] == 2
    assert len(result["canonical_row_ids"]) == 2

    assert len(rows) == 2
    assert {row.entity_type for row in rows} == {"amount", "date"}
    assert {row.row["value"] for row in rows} == {"100.00", "2026-04-25"}


def test_canonicalize_facts_with_empty_list_returns_zero():
    repo = CanonicalRepository(_db_path())
    service = CanonicalizationService(repo)

    result = service.canonicalize_facts([], job_id="job-2")

    assert result == {
        "status": "CANONICALIZED",
        "job_id": "job-2",
        "plan_id": None,
        "canonical_rows_count": 0,
        "canonical_row_ids": [],
    }
    assert repo.list_canonical_rows() == []
