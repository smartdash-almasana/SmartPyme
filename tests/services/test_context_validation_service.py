import pytest
from app.services.context_validation_service import ContextValidationService
from app.services.operational_taxonomy_service import OperationalTaxonomyService


@pytest.fixture
def service():
    return ContextValidationService()


def test_unknown_item_returns_unknown_taxonomy(service):
    res = service.validate("NON_EXISTENT_ID")
    assert res["status"] == "UNKNOWN_TAXONOMY"
    assert res["item_id"] == "NON_EXISTENT_ID"
    assert res["tipo_operativo"] is None


def test_known_item_without_provided_data_returns_needs_more_context(service):
    # TAX_COM_005 is "kiosco_polirrubro"
    res = service.validate("TAX_COM_005")
    assert res["status"] == "NEEDS_MORE_CONTEXT"
    assert res["item_id"] == "TAX_COM_005"
    assert len(res["missing_data"]) > 0
    # Should include questions from catalog
    assert len(res["questions"]) > 0
    assert "¿Cuánto ganás por categoría?" in res["questions"]


def test_known_item_with_partial_data_returns_correct_missing_data(service):
    # TAX_COM_005 requires:
    # ["tickets_diarios", "alquiler", "facturacion_servicios", "margen_ponderado", "horas_apertura"]
    provided = {
        "tickets_diarios": 100,
        "alquiler": 50000
    }
    res = service.validate("TAX_COM_005", provided_data=provided)
    assert res["status"] == "NEEDS_MORE_CONTEXT"
    assert "facturacion_servicios" in res["missing_data"]
    assert "margen_ponderado" in res["missing_data"]
    assert "horas_apertura" in res["missing_data"]
    assert "tickets_diarios" not in res["missing_data"]


def test_known_item_with_all_minimum_data_returns_context_ready(service):
    provided = {
        "tickets_diarios": 100,
        "alquiler": 50000,
        "facturacion_servicios": 10000,
        "margen_ponderado": 0.2,
        "horas_apertura": 14
    }
    res = service.validate("TAX_COM_005", provided_data=provided)
    assert res["status"] == "CONTEXT_READY"
    assert len(res["missing_data"]) == 0
    # Questions should be empty when READY
    assert res["questions"] == []


def test_returns_possible_pathologies_and_suggested_formulas(service):
    res = service.validate("TAX_COM_005")
    # TAX_COM_005 has pathologies like "autoexplotacion"
    assert "autoexplotacion" in res["possible_pathologies"]
    # and formulas like "FORM_022"
    assert "FORM_022" in res["suggested_formulas"]


def test_no_llm_or_external_calls(service):
    # This is a unit test that runs locally and deterministically
    import time
    start = time.time()
    res = service.validate("TAX_COM_005")
    end = time.time()
    # Should be very fast (under 100ms) as it's just a lookup
    assert (end - start) < 0.1
    assert res["status"] == "NEEDS_MORE_CONTEXT"


def test_validate_operational_conditions_complete_ok(service):
    # Testing with skill_reconcile_bank_vs_pos
    variables = {"pos_total": 1000, "bank_total": 950, "periodo": "2026-04"}
    evidence = ["pos_report", "bank_statement"]
    
    res = service.validate_operational_conditions(
        skill_id="skill_reconcile_bank_vs_pos",
        variables=variables,
        evidence=evidence
    )
    
    assert res["status"] == "CONDITIONS_OK"
    assert res["skill_id"] == "skill_reconcile_bank_vs_pos"


def test_validate_operational_conditions_missing_variable(service):
    variables = {"pos_total": 1000} # missing bank_total and periodo
    evidence = ["pos_report", "bank_statement"]
    
    res = service.validate_operational_conditions(
        skill_id="skill_reconcile_bank_vs_pos",
        variables=variables,
        evidence=evidence
    )
    
    assert res["status"] == "CONDITIONS_MISSING"
    assert "bank_total" in res["missing_variables"]
    assert "periodo" in res["missing_variables"]
    assert res["missing_evidence"] == []


def test_validate_operational_conditions_missing_evidence(service):
    variables = {"pos_total": 1000, "bank_total": 950, "periodo": "2026-04"}
    evidence = ["pos_report"] # missing bank_statement
    
    res = service.validate_operational_conditions(
        skill_id="skill_reconcile_bank_vs_pos",
        variables=variables,
        evidence=evidence
    )
    
    assert res["status"] == "CONDITIONS_MISSING"
    assert res["missing_variables"] == []
    assert "bank_statement" in res["missing_evidence"]


def test_validate_operational_conditions_invalid_types(service):
    res = service.validate_operational_conditions(
        skill_id="skill_reconcile_bank_vs_pos",
        variables=["not-a-dict"], # type: ignore
        evidence={"not-a-list": True} # type: ignore
    )
    
    assert res["status"] == "CONDITIONS_INVALID"
    assert res["reason"] == "INVALID_INPUT_TYPES"


def test_validate_operational_conditions_unknown_skill(service):
    res = service.validate_operational_conditions(
        skill_id="skill_non_existent",
        variables={},
        evidence=[]
    )
    
    assert res["status"] == "UNKNOWN_SKILL"
