import pytest

from app.contracts.evidence_contract import CanonicalRowCandidate


def test_canonical_row_cliente_id_required():
    with pytest.raises(ValueError):
        CanonicalRowCandidate(
            cliente_id="",
            canonical_row_id="canonical-1",
            fact_candidate_id="fact-1",
            evidence_id="ev-1",
            job_id=None,
            plan_id=None,
            entity_type="amount",
            row={"fact_type": "amount", "value": "100.00"},
        )


def test_canonical_row_cliente_id_present():
    row = CanonicalRowCandidate(
        cliente_id="cliente-1",
        canonical_row_id="canonical-1",
        fact_candidate_id="fact-1",
        evidence_id="ev-1",
        job_id=None,
        plan_id=None,
        entity_type="amount",
        row={"fact_type": "amount", "value": "100.00"},
    )

    assert row.cliente_id == "cliente-1"
