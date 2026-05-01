import pytest
from pydantic import ValidationError
from app.ai.schemas.owner_message_interpretation import OwnerMessageInterpretation
from app.ai.agents.owner_message_interpreter_agent import build_owner_message_interpreter_agent, HAS_PYDANTIC_AI

def test_schema_acepta_datos_validos():
    data = {
        "rubro_posible": "Kiosco",
        "dolores_detectados": ("no tengo stock",),
        "fuentes_mencionadas": ("Excel",),
        "datos_mencionados": ("ventas mensuales",),
        "hipotesis_sistema": ("Posible descalce de stock",),
        "preguntas_sugeridas": ("¿Cada cuánto haces inventario?",),
        "nivel_confianza": 0.85,
        "necesita_confirmacion": True
    }
    interpretation = OwnerMessageInterpretation(**data)
    assert interpretation.rubro_posible == "Kiosco"
    assert interpretation.nivel_confianza == 0.85

def test_schema_rechaza_nivel_confianza_fuera_de_rango():
    with pytest.raises(ValidationError):
        OwnerMessageInterpretation(nivel_confianza=1.1)
    
    with pytest.raises(ValidationError):
        OwnerMessageInterpretation(nivel_confianza=-0.1)

def test_defaults_de_tuplas_vacias_funcionan():
    interpretation = OwnerMessageInterpretation()
    assert interpretation.dolores_detectados == ()
    assert interpretation.fuentes_mencionadas == ()
    assert interpretation.nivel_confianza == 0.0

def test_necesita_confirmacion_es_bool():
    interpretation = OwnerMessageInterpretation(necesita_confirmacion=False)
    assert interpretation.necesita_confirmacion is False

def test_import_y_factory_defensiva_no_fallan_si_falta_pydantic_ai():
    # El import ya se realizó arriba sin fallar
    agent = build_owner_message_interpreter_agent("gpt-4o")
    if not HAS_PYDANTIC_AI:
        assert agent is None
    else:
        # Si por alguna razón estuviera instalado en el entorno de test
        assert agent is not None
