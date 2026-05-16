"""
Tests del puerto conversacional clínico — PymIA.

Validan que el boundary entre la interfaz externa y el kernel clínico
sea limpio: modo correcto, mensaje clínico presente, evidencia disponible,
y ausencia total de conceptos de factoría/orchestration/jobs.
"""
import pytest

from pymia.interfaces.conversational_port import (
    ClinicalConversationalPort,
    ConversationalInput,
    ConversationalOutput,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def port() -> ClinicalConversationalPort:
    """Puerto conversacional listo para usar en tests."""
    return ClinicalConversationalPort()


@pytest.fixture
def canonical_input() -> ConversationalInput:
    """Caso canónico: el dueño no sabe si gana plata."""
    return ConversationalInput(
        tenant_id="tenant_test_001",
        channel="test",
        text="vendo mucho pero no se si gano plata",
    )


@pytest.fixture
def canonical_output(port: ClinicalConversationalPort, canonical_input: ConversationalInput) -> ConversationalOutput:
    """Output del caso canónico, reutilizable en múltiples tests."""
    return port.handle(canonical_input)


# ---------------------------------------------------------------------------
# Tests de modo y status (caso canónico)
# ---------------------------------------------------------------------------


def test_canonical_case_status_ok(canonical_output: ConversationalOutput):
    """El caso canónico siempre debe retornar status 'ok'."""
    assert canonical_output.status == "ok"


def test_canonical_case_mode_anamnesis_inicial(canonical_output: ConversationalOutput):
    """El modo debe ser 'anamnesis_inicial' para el caso canónico."""
    assert canonical_output.mode == "anamnesis_inicial"


# ---------------------------------------------------------------------------
# Tests del mensaje clínico (caso canónico)
# ---------------------------------------------------------------------------


def test_canonical_case_message_is_present(canonical_output: ConversationalOutput):
    """El mensaje no debe ser None ni vacío."""
    assert canonical_output.message is not None
    assert len(canonical_output.message.strip()) > 0


def test_canonical_case_message_contains_symptom(canonical_output: ConversationalOutput):
    """El mensaje debe registrar el síntoma declarado por el dueño."""
    assert "Registré este síntoma operacional" in canonical_output.message


def test_canonical_case_message_contains_primary_hypothesis(canonical_output: ConversationalOutput):
    """El mensaje debe contener la hipótesis prioritaria."""
    assert "Hipótesis inicial prioritaria" in canonical_output.message


def test_canonical_case_message_contains_evidence_request(canonical_output: ConversationalOutput):
    """El mensaje debe solicitar evidencia para validar las hipótesis."""
    assert "Para confirmar o refutar estas hipótesis necesito" in canonical_output.message


# ---------------------------------------------------------------------------
# Tests de evidencia requerida (caso canónico)
# ---------------------------------------------------------------------------


def test_canonical_case_laboratorio_is_present(canonical_output: ConversationalOutput):
    """El contrato de laboratorio debe estar presente en el output."""
    assert canonical_output.laboratorio is not None


def test_canonical_case_evidencia_requerida_not_empty(canonical_output: ConversationalOutput):
    """La evidencia requerida no debe estar vacía."""
    assert len(canonical_output.laboratorio.evidencia_requerida) > 0


def test_canonical_case_evidencia_contains_ventas(canonical_output: ConversationalOutput):
    """La evidencia debe incluir 'ventas' como mínimo para el caso de rentabilidad."""
    evidencia = canonical_output.laboratorio.evidencia_requerida
    assert any("ventas" in e.lower() for e in evidencia)


def test_canonical_case_hipotesis_iniciales_not_empty(canonical_output: ConversationalOutput):
    """Deben generarse hipótesis iniciales."""
    assert len(canonical_output.anamnesis.hipotesis_iniciales) > 0


# ---------------------------------------------------------------------------
# Tests de boundary — ausencia de contaminación
# ---------------------------------------------------------------------------


_FORBIDDEN_TERMS = [
    "job",
    "workflow",
    "authorization",
    "approve",
    "orchestration",
    "create_job",
    "decision_type",
    "factory",
    "mcp",
]


def test_message_contains_no_forbidden_terms(canonical_output: ConversationalOutput):
    """
    El mensaje clínico NO debe contener ningún término de factoría,
    orchestration ni jobs. Garantiza la soberanía del kernel clínico.
    """
    message_lower = canonical_output.message.lower()
    for term in _FORBIDDEN_TERMS:
        assert term not in message_lower, (
            f"Término prohibido '{term}' encontrado en el mensaje clínico. "
            "El boundary está contaminado."
        )


def test_output_has_no_job_fields(canonical_output: ConversationalOutput):
    """
    El ConversationalOutput no debe exponer campos de jobs ni orchestration.
    Valida que el contrato de salida permanece limpio.
    """
    output_fields = set(ConversationalOutput.model_fields.keys())
    forbidden_fields = {"job_id", "workflow_id", "authorization", "decision_type", "orchestration_context"}
    contamination = output_fields & forbidden_fields
    assert not contamination, f"Campos prohibidos en el output: {contamination}"


def test_input_has_no_job_fields():
    """
    El ConversationalInput no debe exponer campos de jobs ni orchestration.
    Valida que el contrato de entrada permanece limpio.
    """
    input_fields = set(ConversationalInput.model_fields.keys())
    forbidden_fields = {"job_id", "workflow_id", "authorization", "decision_type", "create_job"}
    contamination = input_fields & forbidden_fields
    assert not contamination, f"Campos prohibidos en el input: {contamination}"


# ---------------------------------------------------------------------------
# Tests de casos no canónicos
# ---------------------------------------------------------------------------


def test_no_signal_case_returns_no_signal_status(port: ClinicalConversationalPort):
    """Texto sin señal clínica debe retornar status 'no_signal'."""
    output = port.handle(
        ConversationalInput(
            tenant_id="tenant_test_002",
            channel="test",
            text="hola, como estas?",
        )
    )
    assert output.status == "no_signal"
    assert output.mode == "no_signal"
    assert output.message is None
    assert output.anamnesis is None
    assert output.laboratorio is None


def test_no_signal_case_message_not_forbidden_either(port: ClinicalConversationalPort):
    """Incluso en no_signal, el output no debe tener campos prohibidos."""
    output = port.handle(
        ConversationalInput(
            tenant_id="tenant_test_003",
            channel="test",
            text="nada relevante aqui",
        )
    )
    output_fields = set(ConversationalOutput.model_fields.keys())
    forbidden_fields = {"job_id", "workflow_id", "authorization", "decision_type"}
    assert not (output_fields & forbidden_fields)


def test_inventory_symptom_triggers_anamnesis(port: ClinicalConversationalPort):
    """Síntoma de inventario también debe producir mode 'anamnesis_inicial'."""
    output = port.handle(
        ConversationalInput(
            tenant_id="tenant_test_004",
            channel="test",
            text="tengo mucho stock parado y no sale",
        )
    )
    assert output.status == "ok"
    assert output.mode == "anamnesis_inicial"
    assert output.message is not None
    assert output.laboratorio is not None


def test_port_is_stateless(port: ClinicalConversationalPort):
    """
    El port es stateless: dos llamadas con el mismo input
    deben producir outputs equivalentes (mismo status y mode).
    """
    inp = ConversationalInput(
        tenant_id="tenant_test_005",
        channel="test",
        text="vendo mucho pero no se si gano plata",
    )
    out1 = port.handle(inp)
    out2 = port.handle(inp)

    assert out1.status == out2.status
    assert out1.mode == out2.mode
    assert out1.message == out2.message


def test_port_respects_tenant_isolation(port: ClinicalConversationalPort):
    """
    El port no debe mezclar datos entre tenants.
    Cada output debe reflejar el tenant_id de su input.
    """
    out_a = port.handle(ConversationalInput(
        tenant_id="tenant_A",
        channel="test",
        text="vendo mucho pero no se si gano plata",
    ))
    out_b = port.handle(ConversationalInput(
        tenant_id="tenant_B",
        channel="test",
        text="vendo mucho pero no se si gano plata",
    ))

    assert out_a.anamnesis.tenant_id == "tenant_A"
    assert out_b.anamnesis.tenant_id == "tenant_B"
    assert out_a.anamnesis.tenant_id != out_b.anamnesis.tenant_id
