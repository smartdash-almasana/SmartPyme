import pytest
from app.services.data_curation_service import DataCurationService


@pytest.fixture
def service():
    return DataCurationService()


def test_curation_ok_complete(service):
    variables = {"pos_total": "1000.50", "bank_total": 950, "periodo": "2026-04"}
    evidence = ["pos_report", "bank_statement"]
    
    res = service.curate_input(
        skill_id="skill_reconcile_bank_vs_pos",
        variables=variables,
        evidence=evidence,
        objective="Test"
    )
    
    assert res.status == "CURATION_OK"
    assert res.cleaned_payload["variables"]["pos_total"] == 1000.5
    assert res.cleaned_payload["variables"]["periodo"] == "2026-04"


def test_curation_filters_irrelevant_keys(service):
    variables = {"pos_total": 1000, "junk": "data"}
    evidence = ["pos_report", "virus.exe"]
    
    res = service.curate_input(
        skill_id="skill_reconcile_bank_vs_pos",
        variables=variables,
        evidence=evidence,
        objective="Test"
    )
    
    assert "junk" not in res.cleaned_payload["variables"]
    assert "virus.exe" not in res.cleaned_payload["evidence"]


def test_curation_invalid_domain_negative(service):
    variables = {"pos_total": -100}
    
    res = service.curate_input(
        skill_id="skill_reconcile_bank_vs_pos",
        variables=variables,
        evidence=[],
        objective="Test"
    )
    
    assert res.status == "CURATION_INVALID"
    assert "INVALID_RANGE: pos_total" in res.errors[0]


def test_curation_invalid_periodo_format(service):
    variables = {"periodo": "2026/04"}
    
    res = service.curate_input(
        skill_id="skill_reconcile_bank_vs_pos",
        variables=variables,
        evidence=[],
        objective="Test"
    )
    
    assert res.status == "CURATION_INVALID"
    assert "INVALID_FORMAT: periodo" in res.errors[0]


def test_curation_insufficient_missing_required(service):
    variables = {"pos_total": 1000} # missing bank_total, periodo, evidence
    
    res = service.curate_input(
        skill_id="skill_reconcile_bank_vs_pos",
        variables=variables,
        evidence=[],
        objective="Test"
    )
    
    assert res.status == "CURATION_INSUFFICIENT"


def test_curation_invalid_null_field(service):
    variables = {"pos_total": None}
    
    res = service.curate_input(
        skill_id="skill_reconcile_bank_vs_pos",
        variables=variables,
        evidence=[],
        objective="Test"
    )
    
    assert res.status == "CURATION_INVALID"
    assert "FIELD_NULL: pos_total" in res.errors[0]
