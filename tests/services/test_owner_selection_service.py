import pytest
from app.services.owner_selection_service import OwnerSelectionService


@pytest.fixture
def service():
    return OwnerSelectionService()


def test_seleccion_desconocida_devuelve_unknown_selection(service):
    res = service.confirm_selection(("TAX_COM_001",), "INVALID_ID")
    assert res["status"] == "UNKNOWN_SELECTION"


def test_seleccion_fuera_de_candidatos_devuelve_selection_not_in_candidates(service):
    # TAX_COM_001 exists in catalog but is not in provided candidate_ids
    res = service.confirm_selection(("TAX_COM_005",), "TAX_COM_001")
    assert res["status"] == "SELECTION_NOT_IN_CANDIDATES"


def test_seleccion_valida_devuelve_selection_confirmed(service):
    # TAX_COM_005 is "kiosco_polirrubro"
    res = service.confirm_selection(("TAX_COM_005", "TAX_COM_001"), "TAX_COM_005")
    assert res["status"] == "SELECTION_CONFIRMED"
    assert res["item_id"] == "TAX_COM_005"
    assert res["tipo_operativo_confirmado"] == "kiosco_polirrubro"
    assert res["familia_smartpyme"] == "comercio"


def test_devuelve_campos_de_taxonomia_confirmada(service):
    res = service.confirm_selection(("TAX_COM_005",), "TAX_COM_005")
    assert res["status"] == "SELECTION_CONFIRMED"
    
    # Check fields from catalog
    assert "tickets_diarios" in res["required_data"]
    assert "autoexplotacion" in res["possible_pathologies"]
    assert "FORM_022" in res["suggested_formulas"]


def test_no_acepta_seleccion_automatica_si_candidate_ids_esta_vacio(service):
    res = service.confirm_selection((), "TAX_COM_005")
    assert res["status"] == "SELECTION_NOT_IN_CANDIDATES"
