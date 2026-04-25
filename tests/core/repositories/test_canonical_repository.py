import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from app.contracts.evidence_contract import CanonicalRowCandidate
from app.repositories.canonical_repository import CanonicalRepository


def _db_path() -> Path:
    base = Path(__file__).resolve().parents[2] / "fixtures" / "tmp_canonical_repository"
    base.mkdir(parents=True, exist_ok=True)
    return base / f"canonical-{uuid.uuid4().hex[:8]}.db"


def _canonical_row(
    canonical_row_id: str,
    *,
    fact_candidate_id: str = "fact-1",
    evidence_id: str = "ev-1",
    entity_type: str = "amount",
) -> CanonicalRowCandidate:
    return CanonicalRowCandidate(
        canonical_row_id=canonical_row_id,
        fact_candidate_id=fact_candidate_id,
        evidence_id=evidence_id,
        job_id=None,
        plan_id=None,
        entity_type=entity_type,
        row={"fact_type": entity_type, "value": "100.00"},
    )


def test_canonical_repository_init_save_and_list():
    repo = CanonicalRepository(_db_path())
    row = _canonical_row("row-1")

    repo.save(row)
    rows = repo.list_canonical_rows()

    assert len(rows) == 1
    assert rows[0] == row


def test_canonical_repository_save_is_idempotent_by_canonical_row_id():
    repo = CanonicalRepository(_db_path())
    repo.save(_canonical_row("row-1"))
    repo.save(_canonical_row("row-1"))

    assert len(repo.list_canonical_rows()) == 1


def test_canonical_repository_save_batch():
    repo = CanonicalRepository(_db_path())
    repo.save_batch([
        _canonical_row("row-1", evidence_id="ev-1"),
        _canonical_row("row-2", evidence_id="ev-2", entity_type="date"),
    ])

    assert len(repo.list_canonical_rows()) == 2


def test_canonical_repository_filters_by_evidence_id():
    repo = CanonicalRepository(_db_path())
    repo.save_batch([
        _canonical_row("row-1", evidence_id="ev-1"),
        _canonical_row("row-2", evidence_id="ev-2"),
    ])

    rows = repo.list_canonical_rows(evidence_id="ev-2")

    assert len(rows) == 1
    assert rows[0].canonical_row_id == "row-2"


def test_canonical_repository_filters_by_entity_type():
    repo = CanonicalRepository(_db_path())
    repo.save_batch([
        _canonical_row("row-1", entity_type="amount"),
        _canonical_row("row-2", entity_type="date"),
    ])

    rows = repo.list_canonical_rows(entity_type="date")

    assert len(rows) == 1
    assert rows[0].entity_type == "date"
