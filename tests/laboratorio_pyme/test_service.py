"""Tests del servicio orquestador LaboratorioService.

Cubre:
- Flujo básico de los tres métodos públicos
- Propagación de errores del contrato
- Propiedad P4: unicidad de case_id
- Propiedad P7: estado inicial siempre 'borrador'
- Propiedad P8: preservación de hallazgos en borrador
"""
import pytest

from app.laboratorio_pyme.contracts import DiagnosticFinding, LaboratorioReportDraft
from app.laboratorio_pyme.service import LaboratorioService
from app.laboratorio_pyme.tipos import TipoLaboratorio

CLIENTE = "cliente-001"
CASE = "case-001"
LAB = TipoLaboratorio.analisis_comercial


def _make_finding(finding_id: str = "f-001") -> DiagnosticFinding:
    return DiagnosticFinding(
        cliente_id=CLIENTE,
        finding_id=finding_id,
        case_id=CASE,
        laboratorio=LAB,
        hallazgo="Caída de ventas detectada",
        prioridad="alta",
        impacto_estimado="Moderado",
    )


# ---------------------------------------------------------------------------
# crear_caso
# ---------------------------------------------------------------------------

def test_crear_caso_retorna_case_con_estado_borrador():
    svc = LaboratorioService()
    caso = svc.crear_caso(CLIENTE, "Juan", [LAB])
    assert caso.estado == "borrador"
    assert caso.cliente_id == CLIENTE
    assert caso.dueno_nombre == "Juan"
    assert caso.laboratorios == [LAB]


def test_crear_caso_case_id_no_vacio():
    svc = LaboratorioService()
    caso = svc.crear_caso(CLIENTE, "Juan", [LAB])
    assert caso.case_id
    assert len(caso.case_id) > 0


def test_crear_caso_dueno_nombre_vacio_propaga_error():
    svc = LaboratorioService()
    with pytest.raises(ValueError, match="dueno_nombre"):
        svc.crear_caso(CLIENTE, "", [LAB])


def test_crear_caso_laboratorios_vacios_propaga_error():
    svc = LaboratorioService()
    with pytest.raises(ValueError, match="laboratorios"):
        svc.crear_caso(CLIENTE, "Juan", [])


def test_crear_caso_cliente_id_vacio_propaga_error():
    svc = LaboratorioService()
    with pytest.raises(ValueError, match="cliente_id"):
        svc.crear_caso("", "Juan", [LAB])


# ---------------------------------------------------------------------------
# crear_selection
# ---------------------------------------------------------------------------

def test_crear_selection_retorna_selection_con_case_id_correcto():
    svc = LaboratorioService()
    sel = svc.crear_selection(CLIENTE, CASE, [LAB])
    assert sel.cliente_id == CLIENTE
    assert sel.case_id == CASE
    assert sel.laboratorios_seleccionados == [LAB]


def test_crear_selection_cliente_id_vacio_propaga_error():
    svc = LaboratorioService()
    with pytest.raises(ValueError, match="cliente_id"):
        svc.crear_selection("", CASE, [LAB])


# ---------------------------------------------------------------------------
# crear_borrador_informe
# ---------------------------------------------------------------------------

def test_crear_borrador_informe_retorna_draft_pendiente_revision():
    svc = LaboratorioService()
    draft = svc.crear_borrador_informe(CLIENTE, CASE, [])
    assert draft.estado_borrador == "pendiente_revision"
    assert draft.cliente_id == CLIENTE
    assert draft.case_id == CASE


def test_crear_borrador_informe_cliente_id_vacio_propaga_error():
    svc = LaboratorioService()
    with pytest.raises(ValueError, match="cliente_id"):
        svc.crear_borrador_informe("", CASE, [])


# ---------------------------------------------------------------------------
# Propiedad P4: unicidad de case_id
# ---------------------------------------------------------------------------

def test_p4_unicidad_case_id():
    """P4: Dos llamadas a crear_caso producen case_id distintos."""
    svc = LaboratorioService()
    c1 = svc.crear_caso(CLIENTE, "Juan", [LAB])
    c2 = svc.crear_caso(CLIENTE, "Juan", [LAB])
    assert c1.case_id != c2.case_id


# ---------------------------------------------------------------------------
# Propiedad P7: estado inicial siempre 'borrador'
# ---------------------------------------------------------------------------

def test_p7_estado_inicial_siempre_borrador():
    """P7: crear_caso siempre produce estado='borrador'."""
    svc = LaboratorioService()
    for nombre in ("Ana", "Carlos", "María"):
        caso = svc.crear_caso(CLIENTE, nombre, [LAB])
        assert caso.estado == "borrador"


# ---------------------------------------------------------------------------
# Propiedad P8: preservación de hallazgos en borrador
# ---------------------------------------------------------------------------

def test_p8_preservacion_hallazgos_en_borrador():
    """P8: crear_borrador_informe preserva todos los hallazgos sin modificarlos."""
    svc = LaboratorioService()
    f1 = _make_finding("f-001")
    f2 = _make_finding("f-002")
    f3 = _make_finding("f-003")
    hallazgos = [f1, f2, f3]
    draft = svc.crear_borrador_informe(CLIENTE, CASE, hallazgos)
    assert len(draft.hallazgos) == 3
    assert draft.hallazgos == hallazgos


def test_p8_borrador_sin_hallazgos():
    """P8 edge case: borrador con lista vacía de hallazgos."""
    svc = LaboratorioService()
    draft = svc.crear_borrador_informe(CLIENTE, CASE, [])
    assert len(draft.hallazgos) == 0
    assert draft.hallazgos == []


# ---------------------------------------------------------------------------
# TS_LAB_CONTRACTUAL_CORE_ALIGNMENT_V1
# Prueba que el servicio preserva los identificadores core cuando se proveen.
# ---------------------------------------------------------------------------

def test_crear_caso_preserva_job_id_y_user_id():
    """Service preserva job_id y user_id en el caso creado."""
    svc = LaboratorioService()
    caso = svc.crear_caso(CLIENTE, "Juan", [LAB], job_id="job-abc", user_id="user-xyz")
    assert caso.job_id == "job-abc"
    assert caso.user_id == "user-xyz"


def test_crear_caso_sin_core_ids_son_none():
    """Service produce job_id=None y user_id=None cuando no se proveen."""
    svc = LaboratorioService()
    caso = svc.crear_caso(CLIENTE, "Juan", [LAB])
    assert caso.job_id is None
    assert caso.user_id is None


def test_crear_selection_preserva_job_id():
    """Service preserva job_id en la selección creada."""
    svc = LaboratorioService()
    sel = svc.crear_selection(CLIENTE, CASE, [LAB], job_id="job-abc")
    assert sel.job_id == "job-abc"


def test_crear_selection_sin_job_id_es_none():
    """Service produce job_id=None en selección cuando no se provee."""
    svc = LaboratorioService()
    sel = svc.crear_selection(CLIENTE, CASE, [LAB])
    assert sel.job_id is None


def test_crear_borrador_preserva_job_id_decision_id_user_id():
    """Service preserva job_id, decision_id y user_id en el borrador."""
    svc = LaboratorioService()
    draft = svc.crear_borrador_informe(
        CLIENTE, CASE, [],
        job_id="job-abc", decision_id="dec-001", user_id="user-xyz"
    )
    assert draft.job_id == "job-abc"
    assert draft.decision_id == "dec-001"
    assert draft.user_id == "user-xyz"


def test_crear_borrador_sin_core_ids_son_none():
    """Service produce job_id=None, decision_id=None, user_id=None cuando no se proveen."""
    svc = LaboratorioService()
    draft = svc.crear_borrador_informe(CLIENTE, CASE, [])
    assert draft.job_id is None
    assert draft.decision_id is None
    assert draft.user_id is None


def test_draft_es_transiente_no_tiene_metodo_save():
    """LaboratorioReportDraft retornado por el servicio no tiene métodos de persistencia."""
    svc = LaboratorioService()
    draft = svc.crear_borrador_informe(CLIENTE, CASE, [])
    assert not hasattr(draft, "save")
    assert not hasattr(draft, "persist")
    assert not hasattr(draft, "commit")
