"""
Tests — AdmissionService mínimo
TS_ADM_002_ADMISSION_SERVICE_MINIMO

Valida el comportamiento determinístico de AdmissionService.process().

Casos:
  1. Perales stock  → INESTABILIDAD, area=stock, Person Paulita, evidencia DUDA, tarea PENDING
  2. Perales caja   → SANGRIA, area=caja, Person contador, evidencia DUDA, tarea PENDING
  3. Genérico       → OPTIMIZACION, area=mixto, next_step pide aclaración, sin diagnóstico
"""

import pytest

from app.contracts.admission_contract import InitialCaseAdmission
from app.services.admission_service import AdmissionService


@pytest.fixture
def service() -> AdmissionService:
    return AdmissionService()


# ---------------------------------------------------------------------------
# Test 1 — Caso Perales stock
# ---------------------------------------------------------------------------


def test_perales_stock_clinical_phase(service: AdmissionService):
    """Mensaje de stock debe producir clinical_phase INESTABILIDAD."""
    result = service.process(
        cliente_id="cliente_perales",
        owner_message="No sé cuánto stock tengo. Paulita tiene un Excel.",
    )
    assert result.clinical_phase == "INESTABILIDAD"


def test_perales_stock_area(service: AdmissionService):
    """Mensaje de stock debe producir area=stock."""
    result = service.process(
        cliente_id="cliente_perales",
        owner_message="No sé cuánto stock tengo. Paulita tiene un Excel.",
    )
    assert result.demand.area == "stock"


def test_perales_stock_person_paulita(service: AdmissionService):
    """Mensaje con Paulita debe incluir Person con name='Paulita'."""
    result = service.process(
        cliente_id="cliente_perales",
        owner_message="No sé cuánto stock tengo. Paulita tiene un Excel.",
    )
    names = [p.name for p in result.people]
    assert "Paulita" in names


def test_perales_stock_evidence_duda(service: AdmissionService):
    """Debe existir al menos una EvidenceItem con epistemic_state=DUDA."""
    result = service.process(
        cliente_id="cliente_perales",
        owner_message="No sé cuánto stock tengo. Paulita tiene un Excel.",
    )
    assert len(result.evidence) > 0
    assert any(ev.epistemic_state == "DUDA" for ev in result.evidence)


def test_perales_stock_task_pending(service: AdmissionService):
    """Debe existir al menos una EvidenceTask con status=PENDING."""
    result = service.process(
        cliente_id="cliente_perales",
        owner_message="No sé cuánto stock tengo. Paulita tiene un Excel.",
    )
    assert len(result.tasks) > 0
    assert all(t.status == "PENDING" for t in result.tasks)


def test_perales_stock_no_operational_case(service: AdmissionService):
    """El resultado debe ser InitialCaseAdmission, no un OperationalCase."""
    result = service.process(
        cliente_id="cliente_perales",
        owner_message="No sé cuánto stock tengo. Paulita tiene un Excel.",
    )
    assert isinstance(result, InitialCaseAdmission)
    # No debe tener atributos propios de OperationalCase
    assert not hasattr(result, "hypothesis")
    assert not hasattr(result, "job_id")
    assert not hasattr(result, "skill_id")


# ---------------------------------------------------------------------------
# Test 2 — Caso Perales caja
# ---------------------------------------------------------------------------


def test_perales_caja_clinical_phase(service: AdmissionService):
    """Mensaje de caja/plata debe producir clinical_phase SANGRIA."""
    result = service.process(
        cliente_id="cliente_perales",
        owner_message="No sé dónde se me va la plata. Tengo caja blanca, caja negra y contador.",
    )
    assert result.clinical_phase == "SANGRIA"


def test_perales_caja_area(service: AdmissionService):
    """Mensaje de caja debe producir area=caja."""
    result = service.process(
        cliente_id="cliente_perales",
        owner_message="No sé dónde se me va la plata. Tengo caja blanca, caja negra y contador.",
    )
    assert result.demand.area == "caja"


def test_perales_caja_person_contador(service: AdmissionService):
    """Mensaje con contador debe incluir Person con name='contador'."""
    result = service.process(
        cliente_id="cliente_perales",
        owner_message="No sé dónde se me va la plata. Tengo caja blanca, caja negra y contador.",
    )
    names = [p.name for p in result.people]
    assert "contador" in names


def test_perales_caja_evidence_duda(service: AdmissionService):
    """Debe existir al menos una EvidenceItem con epistemic_state=DUDA."""
    result = service.process(
        cliente_id="cliente_perales",
        owner_message="No sé dónde se me va la plata. Tengo caja blanca, caja negra y contador.",
    )
    assert len(result.evidence) > 0
    assert any(ev.epistemic_state == "DUDA" for ev in result.evidence)


def test_perales_caja_task_pending(service: AdmissionService):
    """Debe existir al menos una EvidenceTask con status=PENDING."""
    result = service.process(
        cliente_id="cliente_perales",
        owner_message="No sé dónde se me va la plata. Tengo caja blanca, caja negra y contador.",
    )
    assert len(result.tasks) > 0
    assert all(t.status == "PENDING" for t in result.tasks)


def test_perales_caja_next_step_not_empty(service: AdmissionService):
    """next_step no debe estar vacío."""
    result = service.process(
        cliente_id="cliente_perales",
        owner_message="No sé dónde se me va la plata. Tengo caja blanca, caja negra y contador.",
    )
    assert result.next_step.strip() != ""


# ---------------------------------------------------------------------------
# Test 3 — Caso genérico
# ---------------------------------------------------------------------------


def test_generic_clinical_phase(service: AdmissionService):
    """Mensaje genérico debe producir clinical_phase OPTIMIZACION."""
    result = service.process(
        cliente_id="cliente_generico",
        owner_message="Quiero mejorar mi negocio.",
    )
    assert result.clinical_phase == "OPTIMIZACION"


def test_generic_area_mixto(service: AdmissionService):
    """Mensaje genérico debe producir area=mixto."""
    result = service.process(
        cliente_id="cliente_generico",
        owner_message="Quiero mejorar mi negocio.",
    )
    assert result.demand.area == "mixto"


def test_generic_next_step_asks_clarification(service: AdmissionService):
    """next_step del caso genérico debe pedir aclaración concreta."""
    result = service.process(
        cliente_id="cliente_generico",
        owner_message="Quiero mejorar mi negocio.",
    )
    # Debe contener una pregunta o solicitud de más información
    next_lower = result.next_step.lower()
    has_question = "?" in result.next_step
    has_clarification_words = any(
        w in next_lower
        for w in ["contame", "qué área", "que area", "necesito entender", "más detalle", "mas detalle"]
    )
    assert has_question or has_clarification_words, (
        f"next_step no pide aclaración: '{result.next_step}'"
    )


def test_generic_no_diagnosis(service: AdmissionService):
    """El caso genérico no debe generar síntomas ni patologías inventadas."""
    result = service.process(
        cliente_id="cliente_generico",
        owner_message="Quiero mejorar mi negocio.",
    )
    # Para el caso genérico no se inventan síntomas ni patologías específicas
    assert isinstance(result, InitialCaseAdmission)
    assert result.clinical_phase == "OPTIMIZACION"
    # No debe tener atributos de OperationalCase
    assert not hasattr(result, "hypothesis")
    assert not hasattr(result, "job_id")


# ---------------------------------------------------------------------------
# Test adicional — case_id y cliente_id se propagan correctamente
# ---------------------------------------------------------------------------


def test_case_id_and_cliente_id_propagated(service: AdmissionService):
    """case_id debe ser un UUID no vacío y cliente_id debe coincidir con el input."""
    result = service.process(
        cliente_id="cliente_test_123",
        owner_message="No sé cuánto stock tengo.",
    )
    assert result.cliente_id == "cliente_test_123"
    assert result.case_id != ""
    # UUID v4 tiene 36 caracteres con guiones
    assert len(result.case_id) == 36
