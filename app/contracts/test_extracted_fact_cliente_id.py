import pytest

from app.contracts.evidence_contract import ExtractedFactCandidate


def test_cliente_id_required():
    with pytest.raises(ValueError):
        ExtractedFactCandidate(
            cliente_id="",
            fact_candidate_id="f1",
            evidence_id="e1",
            job_id=None,
            plan_id=None,
            schema_name="s",
            data={},
            confidence=1.0,
            extraction_method="test",
        )


def test_cliente_id_present():
    fact = ExtractedFactCandidate(
        cliente_id="c1",
        fact_candidate_id="f1",
        evidence_id="e1",
        job_id=None,
        plan_id=None,
        schema_name="s",
        data={},
        confidence=1.0,
        extraction_method="test",
    )

    assert fact.cliente_id == "c1"
