"""
Tests del adapter Hermes ↔ ClinicalConversationalPort — PymIA.

Validan:
- Traducción correcta de vocabulario Hermes → clínico → Hermes.
- reply_text clínico presente en el caso canónico.
- payload contiene anamnesis y laboratorio.
- output sin ningún campo/término de jobs, workflows, orchestration.
- metadata de entrada preservada en payload, nunca enviada al kernel.
- adapter usa ClinicalConversationalPort internamente (boundary respetado).
- offline total: sin red, sin LLM, sin env vars.
"""
import pytest
from unittest.mock import MagicMock, patch

from pymia.hermes.adapter import (
    HermesAdapter,
    HermesInput,
    HermesOutput,
    HermesPayload,
)
from pymia.interfaces.conversational_port import ClinicalConversationalPort


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def adapter() -> HermesAdapter:
    """Adapter listo para usar en tests. Sin LLM, sin red, sin env vars."""
    return HermesAdapter()


@pytest.fixture
def canonical_input() -> HermesInput:
    """Caso canónico: el dueño no sabe si gana plata."""
    return HermesInput(
        tenant_id="tenant_hermes_001",
        channel="telegram",
        message_text="vendo mucho pero no se si gano plata",
        metadata={"message_id": "msg_001", "user_id": "usr_42"},
    )


@pytest.fixture
def canonical_output(adapter: HermesAdapter, canonical_input: HermesInput) -> HermesOutput:
    """Output del caso canónico, reutilizable en múltiples tests."""
    return adapter.handle(canonical_input)


# ---------------------------------------------------------------------------
# Tests de status y modo (caso canónico)
# ---------------------------------------------------------------------------


def test_canonical_status_ok(canonical_output: HermesOutput):
    """El caso canónico debe retornar status 'ok'."""
    assert canonical_output.status == "ok"


def test_canonical_mode_anamnesis_inicial(canonical_output: HermesOutput):
    """El modo debe ser 'anamnesis_inicial' para el caso canónico."""
    assert canonical_output.mode == "anamnesis_inicial"


# ---------------------------------------------------------------------------
# Tests de reply_text (caso canónico)
# ---------------------------------------------------------------------------


def test_canonical_reply_text_is_present(canonical_output: HermesOutput):
    """reply_text no debe ser None ni vacío para el caso canónico."""
    assert canonical_output.reply_text is not None
    assert len(canonical_output.reply_text.strip()) > 0


def test_canonical_reply_text_contains_symptom(canonical_output: HermesOutput):
    """reply_text debe registrar el síntoma declarado por el dueño."""
    assert "Registré este síntoma operacional" in canonical_output.reply_text


def test_canonical_reply_text_contains_hypothesis(canonical_output: HermesOutput):
    """reply_text debe contener la hipótesis prioritaria."""
    assert "Hipótesis inicial prioritaria" in canonical_output.reply_text


def test_canonical_reply_text_contains_evidence_request(canonical_output: HermesOutput):
    """reply_text debe solicitar evidencia para validar las hipótesis."""
    assert "Para confirmar o refutar estas hipótesis necesito" in canonical_output.reply_text


# ---------------------------------------------------------------------------
# Tests de payload (caso canónico)
# ---------------------------------------------------------------------------


def test_canonical_payload_contains_anamnesis(canonical_output: HermesOutput):
    """El payload debe contener la estructura de anamnesis."""
    assert canonical_output.payload.anamnesis is not None


def test_canonical_payload_anamnesis_hipotesis_not_empty(canonical_output: HermesOutput):
    """El payload debe contener hipótesis iniciales."""
    assert len(canonical_output.payload.anamnesis.hipotesis_iniciales) > 0


def test_canonical_payload_contains_laboratorio(canonical_output: HermesOutput):
    """El payload debe contener el contrato de laboratorio."""
    assert canonical_output.payload.laboratorio is not None


def test_canonical_payload_laboratorio_evidencia_not_empty(canonical_output: HermesOutput):
    """El laboratorio en el payload debe tener evidencia requerida."""
    assert len(canonical_output.payload.laboratorio.evidencia_requerida) > 0


def test_canonical_payload_preserves_input_metadata(
    adapter: HermesAdapter, canonical_input: HermesInput
):
    """
    El adapter debe preservar la metadata original de HermesInput en el payload.
    La metadata no debe ser interpretada ni enviada al kernel clínico.
    """
    output = adapter.handle(canonical_input)
    assert output.payload.input_metadata == canonical_input.metadata
    assert output.payload.input_metadata["message_id"] == "msg_001"
    assert output.payload.input_metadata["user_id"] == "usr_42"


def test_empty_metadata_is_preserved(adapter: HermesAdapter):
    """Metadata vacía debe preservarse como dict vacío en el payload."""
    output = adapter.handle(HermesInput(
        tenant_id="tenant_001",
        channel="api",
        message_text="vendo mucho pero no se si gano plata",
        metadata={},
    ))
    assert output.payload.input_metadata == {}


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


def test_reply_text_contains_no_forbidden_terms(canonical_output: HermesOutput):
    """
    reply_text NO debe contener ningún término de factoría, orchestration ni jobs.
    Garantiza que el adapter no filtra contaminación hacia Hermes.
    """
    reply_lower = canonical_output.reply_text.lower()
    for term in _FORBIDDEN_TERMS:
        assert term not in reply_lower, (
            f"Término prohibido '{term}' encontrado en reply_text. "
            "El adapter está filtrando contaminación."
        )


def test_hermes_output_contract_has_no_forbidden_fields():
    """
    HermesOutput no debe declarar campos de jobs ni orchestration.
    Valida que el contrato de salida Hermes permanece limpio.
    """
    output_fields = set(HermesOutput.model_fields.keys())
    forbidden = {"job_id", "workflow_id", "authorization", "decision_type", "orchestration_context"}
    assert not (output_fields & forbidden), (
        f"Campos prohibidos en HermesOutput: {output_fields & forbidden}"
    )


def test_hermes_input_contract_has_no_forbidden_fields():
    """
    HermesInput no debe declarar campos de jobs ni orchestration.
    Valida que el contrato de entrada Hermes permanece limpio.
    """
    input_fields = set(HermesInput.model_fields.keys())
    forbidden = {"job_id", "workflow_id", "authorization", "decision_type", "create_job"}
    assert not (input_fields & forbidden), (
        f"Campos prohibidos en HermesInput: {input_fields & forbidden}"
    )


def test_hermes_payload_contract_has_no_forbidden_fields():
    """
    HermesPayload no debe declarar campos de jobs ni orchestration.
    """
    payload_fields = set(HermesPayload.model_fields.keys())
    forbidden = {"job_id", "workflow_id", "decision_type", "orchestration_context"}
    assert not (payload_fields & forbidden), (
        f"Campos prohibidos en HermesPayload: {payload_fields & forbidden}"
    )


# ---------------------------------------------------------------------------
# Tests de boundary interno: el adapter usa ClinicalConversationalPort
# ---------------------------------------------------------------------------


def test_adapter_uses_clinical_port_internally():
    """
    Verifica que el adapter usa ClinicalConversationalPort como única
    dependencia clínica. No debe instanciar directamente servicios del kernel.
    """
    adapter = HermesAdapter()
    assert hasattr(adapter, "_port")
    assert isinstance(adapter._port, ClinicalConversationalPort)


def test_adapter_passes_correct_fields_to_port():
    """
    Verifica que el adapter mapea los campos de HermesInput correctamente
    hacia ConversationalInput — sin pasar metadata al kernel.
    """
    with patch.object(
        ClinicalConversationalPort,
        "handle",
        wraps=ClinicalConversationalPort().handle,
    ) as mock_handle:
        adapter = HermesAdapter()
        adapter._port = MagicMock(wraps=ClinicalConversationalPort())

        adapter.handle(HermesInput(
            tenant_id="tenant_spy",
            channel="spy_channel",
            message_text="vendo mucho pero no se si gano plata",
            metadata={"secret": "this_must_not_reach_kernel"},
        ))

        call_args = adapter._port.handle.call_args
        clinical_input = call_args[0][0]

        # Los tres campos requeridos deben estar presentes
        assert clinical_input.tenant_id == "tenant_spy"
        assert clinical_input.channel == "spy_channel"
        assert clinical_input.text == "vendo mucho pero no se si gano plata"

        # La metadata NO debe haber llegado al kernel
        assert not hasattr(clinical_input, "metadata")
        assert not hasattr(clinical_input, "secret")


# ---------------------------------------------------------------------------
# Tests de casos no canónicos
# ---------------------------------------------------------------------------


def test_no_signal_returns_no_signal_status(adapter: HermesAdapter):
    """Texto sin señal clínica debe retornar status 'no_signal'."""
    output = adapter.handle(HermesInput(
        tenant_id="tenant_002",
        channel="telegram",
        message_text="hola, como estas?",
        metadata={},
    ))
    assert output.status == "no_signal"
    assert output.mode == "no_signal"
    assert output.reply_text is None
    assert output.payload.anamnesis is None
    assert output.payload.laboratorio is None


def test_no_signal_preserves_metadata(adapter: HermesAdapter):
    """Incluso en no_signal, la metadata de entrada debe estar en el payload."""
    output = adapter.handle(HermesInput(
        tenant_id="tenant_003",
        channel="api",
        message_text="sin señal operacional aqui",
        metadata={"trace_id": "trace_xyz"},
    ))
    assert output.payload.input_metadata["trace_id"] == "trace_xyz"


def test_inventory_symptom_produces_anamnesis(adapter: HermesAdapter):
    """Síntoma de inventario también debe activar mode 'anamnesis_inicial'."""
    output = adapter.handle(HermesInput(
        tenant_id="tenant_004",
        channel="telegram",
        message_text="tengo mucho stock parado y no sale",
        metadata={},
    ))
    assert output.status == "ok"
    assert output.mode == "anamnesis_inicial"
    assert output.reply_text is not None
    assert output.payload.anamnesis is not None
    assert output.payload.laboratorio is not None


def test_adapter_is_stateless(adapter: HermesAdapter):
    """
    El adapter es stateless: dos llamadas idénticas producen
    outputs equivalentes (mismo status, mode y reply_text).
    """
    inp = HermesInput(
        tenant_id="tenant_005",
        channel="test",
        message_text="vendo mucho pero no se si gano plata",
        metadata={"run": 1},
    )
    out1 = adapter.handle(inp)
    inp2 = inp.model_copy(update={"metadata": {"run": 2}})
    out2 = adapter.handle(inp2)

    assert out1.status == out2.status
    assert out1.mode == out2.mode
    assert out1.reply_text == out2.reply_text


def test_adapter_respects_tenant_isolation(adapter: HermesAdapter):
    """
    El adapter no mezcla datos entre tenants.
    Cada output debe reflejar el tenant del input correspondiente.
    """
    out_a = adapter.handle(HermesInput(
        tenant_id="tenant_A",
        channel="test",
        message_text="vendo mucho pero no se si gano plata",
        metadata={},
    ))
    out_b = adapter.handle(HermesInput(
        tenant_id="tenant_B",
        channel="test",
        message_text="vendo mucho pero no se si gano plata",
        metadata={},
    ))

    assert out_a.payload.anamnesis.tenant_id == "tenant_A"
    assert out_b.payload.anamnesis.tenant_id == "tenant_B"
    assert out_a.payload.anamnesis.tenant_id != out_b.payload.anamnesis.tenant_id
