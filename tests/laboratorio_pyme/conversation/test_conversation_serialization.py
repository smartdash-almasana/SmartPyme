"""Tests de serialización/deserialización de ConversationState.

Verifica roundtrip completo: state → dict → state.
Sin DB, sin Supabase, sin engine obligatorio.
"""

from __future__ import annotations

import json

from app.laboratorio_pyme.conversation.engine import procesar_mensaje
from app.laboratorio_pyme.conversation.serialization import (
    conversation_state_from_dict,
    conversation_state_to_dict,
)
from app.laboratorio_pyme.conversation.state import (
    ConversationState,
    FaseConversacion,
    crear_estado_inicial,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _roundtrip(state: ConversationState) -> ConversationState:
    """Serializa y deserializa un estado. Simula persistencia en DB."""
    data = conversation_state_to_dict(state)
    return conversation_state_from_dict(data)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_serializa_estado_inicial():
    state = crear_estado_inicial("cliente_serial_001")

    data = conversation_state_to_dict(state)

    assert data["cliente_id"] == "cliente_serial_001"
    assert data["fase"] == FaseConversacion.ANAMNESIS_GENERAL.value
    assert data["dolor_principal"] is None
    assert data["hipotesis_activas"] == []
    assert data["historial_mensajes"] == []
    assert data["historial_preguntas"] == []
    assert data["evidencia_requerida"] == []
    assert data["evidencia_confirmada"] == []


def test_resultado_es_json_compatible():
    state = crear_estado_inicial("cliente_json")
    procesar_mensaje(state, "vendo mucho pero no queda plata")

    data = conversation_state_to_dict(state)

    # No debe lanzar excepción
    serializado = json.dumps(data)
    assert isinstance(serializado, str)
    assert len(serializado) > 0


def test_roundtrip_estado_con_hipotesis_activa():
    state = crear_estado_inicial("cliente_roundtrip_hip")
    procesar_mensaje(state, "vendo mucho pero no queda plata")

    assert len(state.hipotesis_activas) > 0
    hipotesis_original = state.hipotesis_activas[0]

    reconstruido = _roundtrip(state)

    assert len(reconstruido.hipotesis_activas) == len(state.hipotesis_activas)

    hip_rec = reconstruido.hipotesis_activas[0]
    assert hip_rec.codigo == hipotesis_original.codigo
    assert hip_rec.nombre == hipotesis_original.nombre
    assert hip_rec.peso == hipotesis_original.peso
    assert hip_rec.dimension == hipotesis_original.dimension
    assert hip_rec.evidencia_faltante == hipotesis_original.evidencia_faltante
    assert hip_rec.evidencia_confirmada == hipotesis_original.evidencia_confirmada
    assert hip_rec.subsistemas_afectados == hipotesis_original.subsistemas_afectados


def test_roundtrip_conserva_historial_mensajes_y_preguntas():
    state = crear_estado_inicial("cliente_roundtrip_hist")
    procesar_mensaje(state, "tengo mucho stock parado")
    procesar_mensaje(state, "además los costos subieron")

    reconstruido = _roundtrip(state)

    assert reconstruido.historial_mensajes == state.historial_mensajes
    assert reconstruido.historial_preguntas == state.historial_preguntas
    assert reconstruido.ultima_pregunta == state.ultima_pregunta
    assert reconstruido.dolor_principal == state.dolor_principal


def test_roundtrip_conserva_evidencia_requerida_y_confirmada():
    state = crear_estado_inicial("cliente_roundtrip_ev")
    # "ventas" activa marcar_evidencia_recibida → mueve a confirmada
    procesar_mensaje(state, "tengo ventas registradas y también stock parado")

    reconstruido = _roundtrip(state)

    assert reconstruido.evidencia_requerida == state.evidencia_requerida
    assert reconstruido.evidencia_confirmada == state.evidencia_confirmada
    assert reconstruido.datos_conocidos == state.datos_conocidos


def test_roundtrip_conserva_fase():
    state = crear_estado_inicial("cliente_roundtrip_fase")
    procesar_mensaje(state, "vendo mucho pero no queda plata")

    fase_original = state.fase
    reconstruido = _roundtrip(state)

    assert reconstruido.fase == fase_original
    assert isinstance(reconstruido.fase, FaseConversacion)


def test_roundtrip_conserva_dimension_foco():
    state = crear_estado_inicial("cliente_roundtrip_dim")
    procesar_mensaje(state, "no queda plata y pierdo horas haciendo todo manual")

    reconstruido = _roundtrip(state)

    assert reconstruido.dimension_foco == "ambas"


def test_tolera_campos_opcionales_faltantes():
    # Dict mínimo: solo cliente_id obligatorio
    data_minimo = {"cliente_id": "cliente_minimo"}

    reconstruido = conversation_state_from_dict(data_minimo)

    assert reconstruido.cliente_id == "cliente_minimo"
    assert reconstruido.fase == FaseConversacion.ANAMNESIS_GENERAL
    assert reconstruido.dolor_principal is None
    assert reconstruido.dimension_foco is None
    assert reconstruido.ultima_pregunta is None
    assert reconstruido.hipotesis_activas == []
    assert reconstruido.historial_mensajes == []
    assert reconstruido.historial_preguntas == []
    assert reconstruido.evidencia_requerida == []
    assert reconstruido.evidencia_confirmada == []
    assert reconstruido.datos_conocidos == []
    assert reconstruido.incertidumbres == []


def test_fase_string_se_convierte_a_enum():
    data = {
        "cliente_id": "cliente_fase_str",
        "fase": "recoleccion_evidencia",
    }

    reconstruido = conversation_state_from_dict(data)

    assert reconstruido.fase == FaseConversacion.RECOLECCION_EVIDENCIA
    assert isinstance(reconstruido.fase, FaseConversacion)
