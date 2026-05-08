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


def test_mensaje_con_contexto_llena_anamnesis_contexto():
    state = crear_estado_inicial("cliente_contexto")

    procesar_mensaje(
        state,
        "Tengo un kiosco, somos 3, urgente hoy: proceso de caja afectado desde hace 3 meses, "
        "pierdo 200000 y 10 horas por semana.",
    )

    contexto = state.anamnesis_contexto
    assert contexto["rubro"] == "kiosco"
    assert contexto["tamano_aprox"] == "micro"
    assert contexto["urgencia"] == "alta"
    assert contexto["proceso_afectado"] == "tesoreria_caja"
    assert contexto["periodo_problema"] == "desde hace 3 meses"
    assert contexto["impacto_economico_estimado"] == "200000"
    assert contexto["impacto_tiempo"] == "10 horas"


def test_segundo_mensaje_no_borra_contexto_previo():
    state = crear_estado_inicial("cliente_contexto_no_borra")

    procesar_mensaje(state, "Tengo un kiosco con problemas de caja desde hace 2 meses.")
    contexto_1 = dict(state.anamnesis_contexto)

    procesar_mensaje(state, "Necesito ayuda para ordenar esto.")
    contexto_2 = state.anamnesis_contexto

    assert contexto_2["rubro"] == contexto_1["rubro"]
    assert contexto_2["proceso_afectado"] == contexto_1["proceso_afectado"]
    assert contexto_2["periodo_problema"] == contexto_1["periodo_problema"]


def test_engine_agrega_incertidumbres_controladas_si_faltan_datos_clave():
    state = crear_estado_inicial("cliente_incertidumbres")

    result = procesar_mensaje(state, "Vendo mucho pero no queda plata.")

    incertidumbres = set(result["incertidumbres"])
    assert "falta_rubro" in incertidumbres
    assert "falta_periodo_problema" in incertidumbres
    assert "falta_impacto" in incertidumbres


def test_questions_prioriza_repregunta_clinica_antes_de_evidencia_documental():
    state = crear_estado_inicial("cliente_prioridad_clinica")

    result = procesar_mensaje(state, "Vendo mucho pero no queda plata.")

    assert result["pregunta"] == "Para entender mejor el caso: en que rubro esta tu negocio?"
