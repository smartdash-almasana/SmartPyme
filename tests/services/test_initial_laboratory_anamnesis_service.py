"""
Tests para el servicio de anamnesis inicial del laboratorio.
"""
import pytest
from app.services.initial_laboratory_anamnesis_service import InitialLaboratoryAnamnesisService


@pytest.fixture
def service() -> InitialLaboratoryAnamnesisService:
    """
    Fixture que retorna una instancia del servicio de anamnesis.
    """
    return InitialLaboratoryAnamnesisService()


def test_service_with_specific_claim_triggers_pipeline(service: InitialLaboratoryAnamnesisService):
    """
    Valida que un claim específico active el AdmissionPipelineV1 y que
    la salida del servicio sea el mensaje formateado correcto.
    """
    tenant_id = "test_tenant"
    channel = "test_channel"
    claim = "vendemos mucho pero no queda plata"

    result = service.process(tenant_id=tenant_id, channel=channel, text=claim)

    assert result is not None

    # Validar que el mensaje formateado sea el correcto
    assert "Registré este síntoma operacional: vendemos mucho pero no queda plata." in result.message
    assert "hipótesis inicial prioritaria:\ntensión de caja." in result.message.lower()
    assert "Para confirmar o refutar estas hipótesis necesito:" in result.message
    assert "costos, extractos, lista de precios si aplica, movimientos de caja, ventas" in result.message

    # Validar que los datos crudos aún estén en el contrato de anamnesis
    hypotheses = result.anamnesis.hipotesis_iniciales
    assert "Tensión de caja" in hypotheses
    assert "Fuga operativa" in hypotheses
    assert "Margen erosionado" in hypotheses


def test_service_with_generic_signal_falls_back_to_default(service: InitialLaboratoryAnamnesisService):
    """
    Valida que un claim que no activa el pipeline específico pero sí una señal
    genérica, utilice la lógica de fallback.
    """
    tenant_id = "test_tenant"
    channel = "test_channel"
    claim = "creo que no estoy ganando plata"

    result = service.process(tenant_id=tenant_id, channel=channel, text=claim)

    assert result is not None

    # Validar que se usen las hipótesis por defecto
    hypotheses = result.anamnesis.hipotesis_iniciales
    assert "margen erosionado" in hypotheses
    assert "costos desactualizados" in hypotheses

    # Validar que se pida la evidencia por defecto
    evidence = result.laboratorio.evidencia_requerida
    assert "ventas del período" in evidence


def test_service_with_no_signal_returns_none(service: InitialLaboratoryAnamnesisService):
    """
    Valida que un claim sin ninguna señal operacional no retorne resultado.
    """
    tenant_id = "test_tenant"
    channel = "test_channel"
    claim = "hola, cómo estás?"

    result = service.process(tenant_id=tenant_id, channel=channel, text=claim)

    assert result is None
