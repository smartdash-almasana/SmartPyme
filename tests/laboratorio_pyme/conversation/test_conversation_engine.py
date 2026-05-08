from __future__ import annotations

from app.laboratorio_pyme.conversation.engine import procesar_mensaje
from app.laboratorio_pyme.conversation.state import (
    ConversationState,
    FaseConversacion,
    crear_estado_inicial,
)


def test_activa_margen_y_caja():
    state = crear_estado_inicial("cliente_001")
    result = procesar_mensaje(state, "vendo mucho pero no queda plata")

    assert any(
        h in result["hipotesis_activas"]
        for h in ["margen_erosionado", "caja_inconsistente"]
    )


def test_activa_stock_inmovilizado():
    state = crear_estado_inicial("cliente_002")
    result = procesar_mensaje(state, "tengo mucho stock parado")

    assert "stock_inmovilizado" in result["hipotesis_activas"]


def test_activa_tiempo_perdido():
    state = crear_estado_inicial("cliente_003")
    result = procesar_mensaje(state, "pierdo mucho tiempo en tareas repetidas")

    assert "tiempo_perdido" in result["hipotesis_activas"]


def test_no_repite_pregunta():
    state = crear_estado_inicial("cliente_004")

    r1 = procesar_mensaje(state, "vendo mucho pero no queda plata")
    r2 = procesar_mensaje(state, "vendo mucho pero no queda plata")

    assert r1["pregunta"] != r2["pregunta"]
    assert len(state.historial_preguntas) >= 2


def test_conserva_cliente_id():
    state = crear_estado_inicial("cliente_777")

    result = procesar_mensaje(state, "tengo problemas de caja")

    assert result["cliente_id"] == "cliente_777"


def test_no_genera_diagnostico_final():
    state = crear_estado_inicial("cliente_888")

    result = procesar_mensaje(state, "hay problemas con precios")

    assert result["diagnostico_emitido"] is False
    assert result["diagnostico_final"] is None


def test_detecta_dimension_dinero():
    state = crear_estado_inicial("cliente_dim_1")

    result = procesar_mensaje(state, "subieron los costos y no me cierra")

    assert result["dimension_detectada"] == "dinero"


def test_detecta_dimension_tiempo():
    state = crear_estado_inicial("cliente_dim_2")

    result = procesar_mensaje(state, "pierdo tiempo con procesos manuales")

    assert result["dimension_detectada"] == "tiempo"


def test_detecta_dimension_ambas():
    state = crear_estado_inicial("cliente_dim_3")

    result = procesar_mensaje(
        state,
        "no queda plata y pierdo horas haciendo todo manual",
    )

    assert result["dimension_detectada"] == "ambas"


def test_historial_mensajes_acumula():
    state = ConversationState(cliente_id="cliente_historial")

    procesar_mensaje(state, "primer mensaje")
    procesar_mensaje(state, "segundo mensaje")

    assert len(state.historial_mensajes) == 2


def test_fase_cambia_con_hipotesis_y_evidencia():
    state = crear_estado_inicial("cliente_fase")

    assert state.fase == FaseConversacion.ANAMNESIS_GENERAL

    procesar_mensaje(state, "vendo mucho pero no queda plata")

    assert state.fase != FaseConversacion.ANAMNESIS_GENERAL


def test_resultado_tiene_estructura_clinica():
    state = crear_estado_inicial("cliente_estructura")

    result = procesar_mensaje(state, "problema de caja")

    claves_esperadas = {
        "pregunta",
        "proxima_pregunta",
        "hipotesis_activas",
        "evidencia_requerida",
        "dimension_detectada",
        "diagnostico_emitido",
        "diagnostico_final",
    }

    assert claves_esperadas.issubset(set(result.keys()))