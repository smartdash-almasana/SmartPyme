import pytest
from app.contracts.confirmed_context_contract import ConfirmedOperationalContext


def test_crea_contexto_confirmado_desde_selection_result_valido():
    selection_result = {
        "status": "SELECTION_CONFIRMED",
        "item_id": "TAX_COM_001",
        "tipo_operativo_confirmado": "tienda_minorista",
        "familia_smartpyme": "comercio",
        "required_data": ["ticket_promedio", "stock"],
        "possible_pathologies": ["margen_invisible"],
        "suggested_formulas": ["FORM_001"]
    }
    
    ctx = ConfirmedOperationalContext.from_selection_result("C1", selection_result)
    
    assert ctx.cliente_id == "C1"
    assert ctx.selected_item_id == "TAX_COM_001"
    assert ctx.tipo_operativo_confirmado == "tienda_minorista"
    assert ctx.familia_smartpyme == "comercio"
    assert ctx.required_data == ("ticket_promedio", "stock")
    assert ctx.possible_pathologies == ("margen_invisible",)
    assert ctx.suggested_formulas == ("FORM_001",)


def test_convierte_listas_a_tuples():
    selection_result = {
        "status": "SELECTION_CONFIRMED",
        "item_id": "ID",
        "tipo_operativo_confirmado": "TIPO",
        "familia_smartpyme": "FAM",
        "required_data": ["A", "B"]
    }
    ctx = ConfirmedOperationalContext.from_selection_result("C1", selection_result)
    assert isinstance(ctx.required_data, tuple)


def test_mantiene_cliente_id_explicito():
    selection_result = {
        "status": "SELECTION_CONFIRMED",
        "item_id": "ID",
        "tipo_operativo_confirmado": "TIPO",
        "familia_smartpyme": "FAM"
    }
    ctx = ConfirmedOperationalContext.from_selection_result("CLIENTE_ESPECIFICO", selection_result)
    assert ctx.cliente_id == "CLIENTE_ESPECIFICO"


def test_falla_si_status_no_es_selection_confirmed():
    selection_result = {"status": "UNKNOWN"}
    with pytest.raises(ValueError, match="Invalid selection result status"):
        ConfirmedOperationalContext.from_selection_result("C1", selection_result)
