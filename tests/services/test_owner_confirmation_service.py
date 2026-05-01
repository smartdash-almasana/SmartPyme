import pytest
from app.services.owner_confirmation_service import OwnerConfirmationService


@pytest.fixture
def service():
    return OwnerConfirmationService()


def test_sin_candidatos_devuelve_no_candidates(service):
    res = service.build_confirmation(())
    assert res["status"] == "NO_CANDIDATES"
    assert res["candidates"] == []


def test_candidatos_invalidos_devuelve_no_valid_candidates(service):
    res = service.build_confirmation(("INVALID_1", "INVALID_2"))
    assert res["status"] == "NO_VALID_CANDIDATES"
    assert res["candidates"] == []


def test_candidato_valido_devuelve_owner_confirmation_required(service):
    # TAX_COM_005 is "kiosco_polirrubro"
    res = service.build_confirmation(("TAX_COM_005",))
    assert res["status"] == "OWNER_CONFIRMATION_REQUIRED"
    assert len(res["candidates"]) == 1
    
    cand = res["candidates"][0]
    assert cand["item_id"] == "TAX_COM_005"
    assert cand["tipo_operativo"] == "kiosco_polirrubro"
    assert cand["familia_smartpyme"] == "comercio"


def test_incluye_confirmation_question(service):
    res = service.build_confirmation(("TAX_COM_005",))
    cand = res["candidates"][0]
    assert cand["confirmation_question"] == "¿Tu negocio se parece más a: kiosco_polirrubro?"


def test_incluye_missing_data_y_required_questions(service):
    res = service.build_confirmation(("TAX_COM_005",))
    cand = res["candidates"][0]
    # Kiosco requires "tickets_diarios", etc.
    assert "tickets_diarios" in cand["missing_data"]
    assert len(cand["required_questions"]) > 0
    assert "¿Cuánto ganás por categoría?" in cand["required_questions"]


def test_incluye_possible_pathologies_y_suggested_formulas(service):
    res = service.build_confirmation(("TAX_COM_005",))
    cand = res["candidates"][0]
    assert "autoexplotacion" in cand["possible_pathologies"]
    assert "FORM_022" in cand["suggested_formulas"]


def test_ignora_ids_invalidos_si_hay_otros_validos(service):
    res = service.build_confirmation(("TAX_COM_005", "INVALID_ID"))
    assert res["status"] == "OWNER_CONFIRMATION_REQUIRED"
    assert len(res["candidates"]) == 1
    assert res["candidates"][0]["item_id"] == "TAX_COM_005"


def test_respeta_provided_data_parcial(service):
    provided = {"tickets_diarios": 150}
    res = service.build_confirmation(("TAX_COM_005",), provided_data=provided)
    cand = res["candidates"][0]
    assert "tickets_diarios" not in cand["missing_data"]
    assert "alquiler" in cand["missing_data"]
