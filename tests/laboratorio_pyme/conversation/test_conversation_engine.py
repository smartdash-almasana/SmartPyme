from __future__ import annotations

from app.laboratorio_pyme.conversation.engine import procesar_mensaje
from app.laboratorio_pyme.conversation.state import crear_estado_inicial



def test_activa_margen_y_caja():
    state = crear_estado_inicial("cliente_001")

    result = procesar_mensaje(
        state,
        "vendo mucho pero no queda plata",
    )

    assert "margen_erosionado" in result["hipotesis_activas"]
    assert "caja_inconsistente" in result["hipotesis_activas"]



def test_activa_stock_inmovilizado():
    state = crear_estado_inicial("cliente_002")

    result = procesar_mensaje(
        state,
        "tengo mucho stock parado",
    )

    assert "stock_inmovilizado" in result["hipotesis_activas"]



def test_activa_tiempo_perdido():
    state = crear_estado_inicial("cliente_003")

    result = procesar_mensaje(
        state,
        "pierdo mucho tiempo en tareas repetitivas",
    )

    assert "tiempo_perdido" in result["hipotesis_activas"]



def test_no_repite_pregunta():
    state = crear_estado_inicial("cliente_004")

    r1 = procesar_mensaje(state, "vendo mucho pero no queda plata")
    r2 = procesar_mensaje(state, "vendo mucho pero no queda plata")

    assert r1["proxima_pregunta"] == r2["proxima_pregunta"]
    assert len(state["historial_preguntas"]) == 1



def test_conserva_cliente_id():
    state = crear_estado_inicial("cliente_777")

    result = procesar_mensaje(state, "tengo problemas de caja")

    assert result["cliente_id"] == "cliente_777"



def test_no_genera_diagnostico_final():
    state = crear_estado_inicial("cliente_888")

    result = procesar_mensaje(state, "hay problemas con precios")

    assert result["diagnostico_final"] is None
