"""Tests de contratos tipados del Laboratorio de Análisis PyME MVP.

Cubre:
- Creación válida de todos los contratos
- Validaciones de error por campo obligatorio
- Propiedades de corrección P1–P3, P5–P6
"""
import pytest

from app.laboratorio_pyme.tipos import TipoLaboratorio
from app.laboratorio_pyme.contracts import (
    LaboratorioPymeCase,
    LaboratorioSelection,
    EvidenceRequirement,
    DiagnosticFinding,
    LaboratorioReportDraft,
)

# ---------------------------------------------------------------------------
# Constantes de módulo (no fixtures de pytest)
# ---------------------------------------------------------------------------
CLIENTE = "cliente-001"
CASE = "case-001"
LAB = TipoLaboratorio.analisis_comercial


# ---------------------------------------------------------------------------
# Creación válida
# ---------------------------------------------------------------------------

def test_laboratorio_pyme_case_valido():
    caso = LaboratorioPymeCase(
        cliente_id=CLIENTE, case_id=CASE, dueno_nombre="Juan",
        laboratorios=[LAB], estado="borrador", creado_en="2024-01-01T00:00:00"
    )
    assert caso.cliente_id == CLIENTE
    assert caso.case_id == CASE
    assert caso.estado == "borrador"


def test_laboratorio_selection_valida():
    sel = LaboratorioSelection(cliente_id=CLIENTE, case_id=CASE, laboratorios_seleccionados=[LAB])
    assert sel.cliente_id == CLIENTE
    assert sel.laboratorios_seleccionados == [LAB]


def test_evidence_requirement_valido():
    req = EvidenceRequirement(
        cliente_id=CLIENTE, case_id=CASE, laboratorio=LAB,
        descripcion="Ventas del último año", obligatorio=True
    )
    assert req.cliente_id == CLIENTE
    assert req.obligatorio is True


def test_diagnostic_finding_valido():
    f = DiagnosticFinding(
        cliente_id=CLIENTE, finding_id="f-001", case_id=CASE,
        laboratorio=LAB, hallazgo="Caída de ventas", prioridad="alta",
        impacto_estimado="Moderado"
    )
    assert f.cliente_id == CLIENTE
    assert f.prioridad == "alta"


def test_laboratorio_report_draft_valido():
    draft = LaboratorioReportDraft(
        cliente_id=CLIENTE, report_id="r-001", case_id=CASE,
        hallazgos=[], estado_borrador="pendiente_revision", generado_en="2024-01-01T00:00:00"
    )
    assert draft.cliente_id == CLIENTE
    assert draft.estado_borrador == "pendiente_revision"


# ---------------------------------------------------------------------------
# Validación de cliente_id vacío
# ---------------------------------------------------------------------------

def test_case_cliente_id_vacio_lanza_error():
    with pytest.raises(ValueError, match="cliente_id"):
        LaboratorioPymeCase(
            cliente_id="", case_id=CASE, dueno_nombre="Juan",
            laboratorios=[LAB], estado="borrador", creado_en="2024-01-01T00:00:00"
        )


def test_selection_cliente_id_vacio_lanza_error():
    with pytest.raises(ValueError, match="cliente_id"):
        LaboratorioSelection(cliente_id="", case_id=CASE, laboratorios_seleccionados=[LAB])


def test_evidence_cliente_id_vacio_lanza_error():
    with pytest.raises(ValueError, match="cliente_id"):
        EvidenceRequirement(
            cliente_id="", case_id=CASE, laboratorio=LAB,
            descripcion="desc", obligatorio=True
        )


def test_finding_cliente_id_vacio_lanza_error():
    with pytest.raises(ValueError, match="cliente_id"):
        DiagnosticFinding(
            cliente_id="", finding_id="f-001", case_id=CASE,
            laboratorio=LAB, hallazgo="hallazgo", prioridad="alta",
            impacto_estimado="Moderado"
        )


def test_draft_cliente_id_vacio_lanza_error():
    with pytest.raises(ValueError, match="cliente_id"):
        LaboratorioReportDraft(
            cliente_id="", report_id="r-001", case_id=CASE,
            hallazgos=[], estado_borrador="pendiente_revision", generado_en="2024-01-01T00:00:00"
        )


# ---------------------------------------------------------------------------
# Validación de otros campos obligatorios
# ---------------------------------------------------------------------------

def test_case_case_id_vacio_lanza_error():
    with pytest.raises(ValueError, match="case_id"):
        LaboratorioPymeCase(
            cliente_id=CLIENTE, case_id="", dueno_nombre="Juan",
            laboratorios=[LAB], estado="borrador", creado_en="2024-01-01T00:00:00"
        )


def test_case_dueno_nombre_vacio_lanza_error():
    with pytest.raises(ValueError, match="dueno_nombre"):
        LaboratorioPymeCase(
            cliente_id=CLIENTE, case_id=CASE, dueno_nombre="",
            laboratorios=[LAB], estado="borrador", creado_en="2024-01-01T00:00:00"
        )


def test_case_laboratorios_vacios_lanza_error():
    with pytest.raises(ValueError, match="laboratorios"):
        LaboratorioPymeCase(
            cliente_id=CLIENTE, case_id=CASE, dueno_nombre="Juan",
            laboratorios=[], estado="borrador", creado_en="2024-01-01T00:00:00"
        )


def test_selection_laboratorios_vacios_lanza_error():
    with pytest.raises(ValueError, match="laboratorios_seleccionados"):
        LaboratorioSelection(cliente_id=CLIENTE, case_id=CASE, laboratorios_seleccionados=[])


def test_evidence_descripcion_vacia_lanza_error():
    with pytest.raises(ValueError, match="descripcion"):
        EvidenceRequirement(
            cliente_id=CLIENTE, case_id=CASE, laboratorio=LAB,
            descripcion="", obligatorio=True
        )


def test_finding_hallazgo_vacio_lanza_error():
    with pytest.raises(ValueError, match="hallazgo"):
        DiagnosticFinding(
            cliente_id=CLIENTE, finding_id="f-001", case_id=CASE,
            laboratorio=LAB, hallazgo="", prioridad="alta",
            impacto_estimado="Moderado"
        )


def test_finding_prioridad_invalida_lanza_error():
    with pytest.raises(ValueError, match="prioridad"):
        DiagnosticFinding(
            cliente_id=CLIENTE, finding_id="f-001", case_id=CASE,
            laboratorio=LAB, hallazgo="hallazgo", prioridad="urgente",
            impacto_estimado="Moderado"
        )


def test_finding_prioridades_validas():
    for p in ("alta", "media", "baja"):
        f = DiagnosticFinding(
            cliente_id=CLIENTE, finding_id="f-001", case_id=CASE,
            laboratorio=LAB, hallazgo="hallazgo", prioridad=p,
            impacto_estimado="Moderado"
        )
        assert f.prioridad == p


def test_draft_estado_borrador_invalido_lanza_error():
    with pytest.raises(ValueError, match="estado_borrador"):
        LaboratorioReportDraft(
            cliente_id=CLIENTE, report_id="r-001", case_id=CASE,
            hallazgos=[], estado_borrador="en_revision", generado_en="2024-01-01T00:00:00"
        )


# ---------------------------------------------------------------------------
# Propiedades de corrección P1–P3, P5–P6
# ---------------------------------------------------------------------------

def test_p1_invariante_coleccion_laboratorios():
    """P1: LaboratorioPymeCase preserva exactamente N laboratorios en el mismo orden."""
    labs = [TipoLaboratorio.analisis_comercial, TipoLaboratorio.analisis_stock]
    caso = LaboratorioPymeCase(
        cliente_id=CLIENTE, case_id=CASE, dueno_nombre="Juan",
        laboratorios=labs, estado="borrador", creado_en="2024-01-01T00:00:00"
    )
    assert len(caso.laboratorios) == len(labs)
    assert list(caso.laboratorios) == labs


def test_p2_round_trip_serializacion_case():
    """P2: to_dict() + reconstrucción produce campos equivalentes."""
    labs = [TipoLaboratorio.analisis_financiero]
    caso = LaboratorioPymeCase(
        cliente_id=CLIENTE, case_id=CASE, dueno_nombre="Ana",
        laboratorios=labs, estado="borrador", creado_en="2024-01-01T00:00:00"
    )
    d = caso.to_dict()
    caso2 = LaboratorioPymeCase(
        cliente_id=d["cliente_id"],
        case_id=d["case_id"],
        dueno_nombre=d["dueno_nombre"],
        laboratorios=[TipoLaboratorio(v) for v in d["laboratorios"]],
        estado=d["estado"],
        creado_en=d["creado_en"],
    )
    assert caso.cliente_id == caso2.cliente_id
    assert caso.case_id == caso2.case_id
    assert caso.dueno_nombre == caso2.dueno_nombre
    assert caso.laboratorios == caso2.laboratorios
    assert caso.estado == caso2.estado


def test_p3_invariante_coleccion_hallazgos_serializacion():
    """P3: to_dict() de LaboratorioReportDraft preserva cantidad de hallazgos."""
    f1 = DiagnosticFinding(
        cliente_id=CLIENTE, finding_id="f-001", case_id=CASE,
        laboratorio=LAB, hallazgo="Hallazgo 1", prioridad="alta",
        impacto_estimado="Alto"
    )
    f2 = DiagnosticFinding(
        cliente_id=CLIENTE, finding_id="f-002", case_id=CASE,
        laboratorio=LAB, hallazgo="Hallazgo 2", prioridad="baja",
        impacto_estimado="Bajo"
    )
    draft = LaboratorioReportDraft(
        cliente_id=CLIENTE, report_id="r-001", case_id=CASE,
        hallazgos=[f1, f2], estado_borrador="pendiente_revision",
        generado_en="2024-01-01T00:00:00"
    )
    d = draft.to_dict()
    assert len(d["hallazgos"]) == len(draft.hallazgos)


def test_p5_fidelidad_serializacion_prioridad():
    """P5: to_dict() preserva el valor de prioridad sin transformación."""
    for p in ("alta", "media", "baja"):
        f = DiagnosticFinding(
            cliente_id=CLIENTE, finding_id="f-001", case_id=CASE,
            laboratorio=LAB, hallazgo="hallazgo", prioridad=p,
            impacto_estimado="Moderado"
        )
        d = f.to_dict()
        assert d["prioridad"] == p


def test_p6_rechazo_prioridad_invalida():
    """P6: DiagnosticFinding rechaza prioridades fuera del conjunto permitido."""
    with pytest.raises(ValueError, match="prioridad"):
        DiagnosticFinding(
            cliente_id=CLIENTE, finding_id="f-001", case_id=CASE,
            laboratorio=LAB, hallazgo="hallazgo", prioridad="critica",
            impacto_estimado="Moderado"
        )


# ---------------------------------------------------------------------------
# TS_LAB_CONTRACTUAL_CORE_ALIGNMENT_V1
# Prueba que cliente_id es el primer campo y que los campos core opcionales
# existen y defaulean a None en todos los contratos relevantes.
# ---------------------------------------------------------------------------

def test_cliente_id_es_primer_campo_en_case():
    """cliente_id debe ser el primer campo de LaboratorioPymeCase."""
    import dataclasses
    fields = [f.name for f in dataclasses.fields(LaboratorioPymeCase)]
    assert fields[0] == "cliente_id"


def test_cliente_id_es_primer_campo_en_selection():
    """cliente_id debe ser el primer campo de LaboratorioSelection."""
    import dataclasses
    fields = [f.name for f in dataclasses.fields(LaboratorioSelection)]
    assert fields[0] == "cliente_id"


def test_cliente_id_es_primer_campo_en_evidence():
    """cliente_id debe ser el primer campo de EvidenceRequirement."""
    import dataclasses
    fields = [f.name for f in dataclasses.fields(EvidenceRequirement)]
    assert fields[0] == "cliente_id"


def test_cliente_id_es_primer_campo_en_finding():
    """cliente_id debe ser el primer campo de DiagnosticFinding."""
    import dataclasses
    fields = [f.name for f in dataclasses.fields(DiagnosticFinding)]
    assert fields[0] == "cliente_id"


def test_cliente_id_es_primer_campo_en_draft():
    """cliente_id debe ser el primer campo de LaboratorioReportDraft."""
    import dataclasses
    fields = [f.name for f in dataclasses.fields(LaboratorioReportDraft)]
    assert fields[0] == "cliente_id"


def test_case_core_ids_default_none():
    """LaboratorioPymeCase: job_id y user_id defaulean a None."""
    caso = LaboratorioPymeCase(
        cliente_id=CLIENTE, case_id=CASE, dueno_nombre="Juan",
        laboratorios=[LAB], estado="borrador", creado_en="2024-01-01T00:00:00"
    )
    assert caso.job_id is None
    assert caso.user_id is None


def test_case_acepta_job_id_y_user_id():
    """LaboratorioPymeCase preserva job_id y user_id cuando se proveen."""
    caso = LaboratorioPymeCase(
        cliente_id=CLIENTE, case_id=CASE, dueno_nombre="Juan",
        laboratorios=[LAB], estado="borrador", creado_en="2024-01-01T00:00:00",
        job_id="job-abc", user_id="user-xyz"
    )
    assert caso.job_id == "job-abc"
    assert caso.user_id == "user-xyz"


def test_finding_core_ids_default_none():
    """DiagnosticFinding: job_id y decision_id defaulean a None."""
    f = DiagnosticFinding(
        cliente_id=CLIENTE, finding_id="f-001", case_id=CASE,
        laboratorio=LAB, hallazgo="hallazgo", prioridad="alta",
        impacto_estimado="Moderado"
    )
    assert f.job_id is None
    assert f.decision_id is None


def test_finding_acepta_job_id_y_decision_id():
    """DiagnosticFinding preserva job_id y decision_id cuando se proveen."""
    f = DiagnosticFinding(
        cliente_id=CLIENTE, finding_id="f-001", case_id=CASE,
        laboratorio=LAB, hallazgo="hallazgo", prioridad="alta",
        impacto_estimado="Moderado",
        job_id="job-abc", decision_id="dec-001"
    )
    assert f.job_id == "job-abc"
    assert f.decision_id == "dec-001"


def test_draft_core_ids_default_none():
    """LaboratorioReportDraft: job_id, decision_id y user_id defaulean a None."""
    draft = LaboratorioReportDraft(
        cliente_id=CLIENTE, report_id="r-001", case_id=CASE,
        hallazgos=[], estado_borrador="pendiente_revision", generado_en="2024-01-01T00:00:00"
    )
    assert draft.job_id is None
    assert draft.decision_id is None
    assert draft.user_id is None


def test_draft_acepta_core_ids():
    """LaboratorioReportDraft preserva job_id, decision_id y user_id cuando se proveen."""
    draft = LaboratorioReportDraft(
        cliente_id=CLIENTE, report_id="r-001", case_id=CASE,
        hallazgos=[], estado_borrador="pendiente_revision", generado_en="2024-01-01T00:00:00",
        job_id="job-abc", decision_id="dec-001", user_id="user-xyz"
    )
    assert draft.job_id == "job-abc"
    assert draft.decision_id == "dec-001"
    assert draft.user_id == "user-xyz"


def test_draft_es_transiente_no_tiene_metodo_save():
    """LaboratorioReportDraft no expone métodos de persistencia (save, persist, commit)."""
    draft = LaboratorioReportDraft(
        cliente_id=CLIENTE, report_id="r-001", case_id=CASE,
        hallazgos=[], estado_borrador="pendiente_revision", generado_en="2024-01-01T00:00:00"
    )
    assert not hasattr(draft, "save")
    assert not hasattr(draft, "persist")
    assert not hasattr(draft, "commit")
    assert not hasattr(draft, "insert")
