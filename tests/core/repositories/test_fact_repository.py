import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from app.contracts.evidence_contract import ExtractedFactCandidate
from app.repositories.fact_repository import FactRepository


def _db_path() -> Path:
    base = Path(__file__).resolve().parents[2] / "fixtures" / "tmp_fact_repository"
    base.mkdir(parents=True, exist_ok=True)
    return base / f"facts-{uuid.uuid4().hex[:8]}.db"


def _fact(
    fact_candidate_id: str,
    *,
    evidence_id: str = "ev-1",
    fact_type: str = "amount",
) -> ExtractedFactCandidate:
    return ExtractedFactCandidate(
        fact_candidate_id=fact_candidate_id,
        evidence_id=evidence_id,
        job_id=None,
        plan_id=None,
        schema_name=f"simple_{fact_type}",
        data={"fact_type": fact_type, "value": "100.00"},
        confidence=1.0,
        extraction_method="test",
    )


def test_fact_repository_init_save_and_list():
    repo = FactRepository(_db_path())
    fact = _fact("fact-1")

    repo.save(fact)
    facts = repo.list_facts()

    assert len(facts) == 1
    assert facts[0] == fact


def test_fact_repository_save_is_idempotent_by_fact_candidate_id():
    repo = FactRepository(_db_path())
    repo.save(_fact("fact-1"))
    repo.save(_fact("fact-1"))

    assert len(repo.list_facts()) == 1


def test_fact_repository_save_batch():
    repo = FactRepository(_db_path())
    repo.save_batch([
        _fact("fact-1", evidence_id="ev-1"),
        _fact("fact-2", evidence_id="ev-2", fact_type="date"),
    ])

    assert len(repo.list_facts()) == 2


def test_fact_repository_filters_by_evidence_id():
    repo = FactRepository(_db_path())
    repo.save_batch([
        _fact("fact-1", evidence_id="ev-1"),
        _fact("fact-2", evidence_id="ev-2"),
    ])

    facts = repo.list_facts(evidence_id="ev-2")

    assert len(facts) == 1
    assert facts[0].fact_candidate_id == "fact-2"


def test_fact_repository_filters_by_fact_type():
    repo = FactRepository(_db_path())
    repo.save_batch([
        _fact("fact-1", fact_type="amount"),
        _fact("fact-2", fact_type="date"),
    ])

    facts = repo.list_facts(fact_type="date")

    assert len(facts) == 1
    assert facts[0].data["fact_type"] == "date"
