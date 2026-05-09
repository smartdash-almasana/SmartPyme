"""Tests del InMemoryClinicalOperationalRepository.

Verifica aislamiento soberano por tenant_id, upsert semántico,
fail-closed ante IDs vacíos y filtrado correcto por reception.

Sin DB, sin red, sin dependencias externas.
"""

from __future__ import annotations

import pytest

from app.contracts.clinical_operational_contracts import (
    DocumentIngestion,
    EvidenceRecord,
    FindingRecord,
    FormulaExecution,
    OperationalCase,
    OperationalCaseCandidate,
    PathologyCandidate,
    ReceptionRecord,
    VariableObservation,
)
from app.repositories.in_memory_clinical_operational_repository import (
    InMemoryClinicalOperationalRepository,
)


# ---------------------------------------------------------------------------
# Helpers de fixtures mínimos
# ---------------------------------------------------------------------------

def _make_reception(
    tenant_id: str = "tenant_a",
    reception_id: str = "rec_001",
    original_message: str = "no me cierra la caja",
    status: str = "RECEIVED",
    **kwargs,
) -> ReceptionRecord:
    return ReceptionRecord(
        reception_id=reception_id,
        tenant_id=tenant_id,
        channel="telegram",
        original_message=original_message,
        status=status,
        **kwargs,
    )


def _make_evidence(
    tenant_id: str = "tenant_a",
    evidence_id: str = "ev_001",
    status: str = "RECEIVED",
    linked_reception_id: str | None = None,
    source_type: str = "excel",
    **kwargs,
) -> EvidenceRecord:
    return EvidenceRecord(
        evidence_id=evidence_id,
        tenant_id=tenant_id,
        source_type=source_type,
        status=status,
        linked_reception_id=linked_reception_id,
        **kwargs,
    )


def _repo() -> InMemoryClinicalOperationalRepository:
    return InMemoryClinicalOperationalRepository()


# ===========================================================================
# ReceptionRecord — tests
# ===========================================================================

def test_guarda_y_recupera_reception():
    repo = _repo()
    rec = _make_reception()
    repo.save_reception(rec)

    resultado = repo.get_reception("tenant_a", "rec_001")

    assert resultado is not None
    assert resultado.reception_id == "rec_001"
    assert resultado.tenant_id == "tenant_a"


def test_upsert_reception_pisa_registro_previo():
    repo = _repo()
    rec_v1 = _make_reception(original_message="versión 1")
    rec_v2 = _make_reception(original_message="versión 2")

    repo.save_reception(rec_v1)
    repo.save_reception(rec_v2)

    resultado = repo.get_reception("tenant_a", "rec_001")
    assert resultado is not None
    assert resultado.original_message == "versión 2"


def test_no_permite_leer_reception_de_otro_tenant():
    repo = _repo()
    rec = _make_reception(tenant_id="tenant_a", reception_id="rec_001")
    repo.save_reception(rec)

    resultado = repo.get_reception("tenant_b", "rec_001")

    assert resultado is None


def test_list_receptions_filtra_por_tenant():
    repo = _repo()
    repo.save_reception(_make_reception(tenant_id="tenant_a", reception_id="rec_001"))
    repo.save_reception(_make_reception(tenant_id="tenant_a", reception_id="rec_002"))
    repo.save_reception(_make_reception(tenant_id="tenant_b", reception_id="rec_003"))

    resultado = repo.list_receptions("tenant_a")

    assert len(resultado) == 2
    ids = {r.reception_id for r in resultado}
    assert ids == {"rec_001", "rec_002"}


def test_list_receptions_tenant_sin_registros_devuelve_lista_vacia():
    repo = _repo()

    resultado = repo.list_receptions("tenant_sin_datos")

    assert resultado == []


def test_tenant_id_vacio_falla_en_save_reception():
    repo = _repo()
    with pytest.raises((ValueError, Exception)):
        # El contrato Pydantic ya rechaza tenant_id vacío
        _make_reception(tenant_id="")


def test_tenant_id_espacios_falla_en_get_reception():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.get_reception("   ", "rec_001")


def test_tenant_id_espacios_falla_en_list_receptions():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.list_receptions("   ")


def test_reception_id_vacio_falla_en_get_reception():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.get_reception("tenant_a", "")


def test_reception_id_espacios_falla_en_get_reception():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.get_reception("tenant_a", "   ")


# ===========================================================================
# EvidenceRecord — tests
# ===========================================================================

def test_guarda_y_recupera_evidence():
    repo = _repo()
    ev = _make_evidence()
    repo.save_evidence(ev)

    resultado = repo.get_evidence("tenant_a", "ev_001")

    assert resultado is not None
    assert resultado.evidence_id == "ev_001"
    assert resultado.tenant_id == "tenant_a"


def test_upsert_evidence_pisa_registro_previo():
    repo = _repo()
    ev_v1 = _make_evidence(source_type="excel")
    ev_v2 = _make_evidence(source_type="pdf")

    repo.save_evidence(ev_v1)
    repo.save_evidence(ev_v2)

    resultado = repo.get_evidence("tenant_a", "ev_001")
    assert resultado is not None
    assert resultado.source_type == "pdf"


def test_no_permite_leer_evidence_de_otro_tenant():
    repo = _repo()
    ev = _make_evidence(tenant_id="tenant_a", evidence_id="ev_001")
    repo.save_evidence(ev)

    resultado = repo.get_evidence("tenant_b", "ev_001")

    assert resultado is None


def test_list_evidence_filtra_por_tenant():
    repo = _repo()
    repo.save_evidence(_make_evidence(tenant_id="tenant_a", evidence_id="ev_001"))
    repo.save_evidence(_make_evidence(tenant_id="tenant_a", evidence_id="ev_002"))
    repo.save_evidence(_make_evidence(tenant_id="tenant_b", evidence_id="ev_003"))

    resultado = repo.list_evidence("tenant_a")

    assert len(resultado) == 2
    ids = {e.evidence_id for e in resultado}
    assert ids == {"ev_001", "ev_002"}


def test_list_evidence_for_reception_devuelve_solo_vinculadas():
    repo = _repo()
    ev_vinculada = _make_evidence(
        evidence_id="ev_001",
        status="LINKED",
        linked_reception_id="rec_001",
    )
    ev_otra_reception = _make_evidence(
        evidence_id="ev_002",
        status="LINKED",
        linked_reception_id="rec_002",
    )
    ev_sin_vincular = _make_evidence(
        evidence_id="ev_003",
        status="RECEIVED",
    )

    repo.save_evidence(ev_vinculada)
    repo.save_evidence(ev_otra_reception)
    repo.save_evidence(ev_sin_vincular)

    resultado = repo.list_evidence_for_reception("tenant_a", "rec_001")

    assert len(resultado) == 1
    assert resultado[0].evidence_id == "ev_001"


def test_list_evidence_for_reception_sin_vinculadas_devuelve_vacia():
    repo = _repo()
    repo.save_evidence(_make_evidence(evidence_id="ev_001", status="RECEIVED"))

    resultado = repo.list_evidence_for_reception("tenant_a", "rec_999")

    assert resultado == []


def test_list_evidence_tenant_sin_registros_devuelve_lista_vacia():
    repo = _repo()

    resultado = repo.list_evidence("tenant_sin_datos")

    assert resultado == []


def test_tenant_id_vacio_falla_en_save_evidence():
    repo = _repo()
    with pytest.raises((ValueError, Exception)):
        _make_evidence(tenant_id="")


def test_tenant_id_espacios_falla_en_get_evidence():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.get_evidence("   ", "ev_001")


def test_tenant_id_espacios_falla_en_list_evidence():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.list_evidence("   ")


def test_tenant_id_espacios_falla_en_list_evidence_for_reception():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.list_evidence_for_reception("   ", "rec_001")


def test_evidence_id_vacio_falla_en_get_evidence():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.get_evidence("tenant_a", "")


def test_evidence_id_espacios_falla_en_get_evidence():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.get_evidence("tenant_a", "   ")


# ===========================================================================
# Aislamiento cruzado tenant_a / tenant_b
# ===========================================================================

def test_aislamiento_completo_entre_tenants():
    repo = _repo()

    repo.save_reception(_make_reception(tenant_id="tenant_a", reception_id="rec_001"))
    repo.save_evidence(_make_evidence(tenant_id="tenant_a", evidence_id="ev_001"))

    assert repo.get_reception("tenant_b", "rec_001") is None
    assert repo.get_evidence("tenant_b", "ev_001") is None
    assert repo.list_receptions("tenant_b") == []
    assert repo.list_evidence("tenant_b") == []


# ---------------------------------------------------------------------------
# Helpers adicionales para DocumentIngestion y VariableObservation
# ---------------------------------------------------------------------------

def _make_ingestion(
    tenant_id: str = "tenant_a",
    ingestion_id: str = "ing_001",
    evidence_id: str = "ev_001",
    provider: str = "manual",
    source_type: str = "excel",
    status: str = "RECEIVED",
    **kwargs,
) -> DocumentIngestion:
    return DocumentIngestion(
        ingestion_id=ingestion_id,
        tenant_id=tenant_id,
        evidence_id=evidence_id,
        provider=provider,
        source_type=source_type,
        status=status,
        **kwargs,
    )


def _make_observation(
    tenant_id: str = "tenant_a",
    observation_id: str = "obs_001",
    evidence_id: str = "ev_001",
    variable_code: str = "margen_bruto",
    status: str = "OBSERVED",
    ingestion_id: str | None = None,
    **kwargs,
) -> VariableObservation:
    return VariableObservation(
        observation_id=observation_id,
        tenant_id=tenant_id,
        variable_code=variable_code,
        evidence_id=evidence_id,
        status=status,
        ingestion_id=ingestion_id,
        **kwargs,
    )


# ===========================================================================
# DocumentIngestion — tests
# ===========================================================================

def test_guarda_y_recupera_ingestion():
    repo = _repo()
    ing = _make_ingestion()
    repo.save_ingestion(ing)

    resultado = repo.get_ingestion("tenant_a", "ing_001")

    assert resultado is not None
    assert resultado.ingestion_id == "ing_001"
    assert resultado.tenant_id == "tenant_a"


def test_upsert_ingestion_pisa_registro_previo():
    repo = _repo()
    ing_v1 = _make_ingestion(source_type="excel")
    ing_v2 = _make_ingestion(source_type="pdf")

    repo.save_ingestion(ing_v1)
    repo.save_ingestion(ing_v2)

    resultado = repo.get_ingestion("tenant_a", "ing_001")
    assert resultado is not None
    assert resultado.source_type == "pdf"


def test_no_permite_leer_ingestion_de_otro_tenant():
    repo = _repo()
    ing = _make_ingestion(tenant_id="tenant_a", ingestion_id="ing_001")
    repo.save_ingestion(ing)

    resultado = repo.get_ingestion("tenant_b", "ing_001")

    assert resultado is None


def test_list_ingestions_filtra_por_tenant():
    repo = _repo()
    repo.save_ingestion(_make_ingestion(tenant_id="tenant_a", ingestion_id="ing_001"))
    repo.save_ingestion(_make_ingestion(tenant_id="tenant_a", ingestion_id="ing_002"))
    repo.save_ingestion(_make_ingestion(tenant_id="tenant_b", ingestion_id="ing_003"))

    resultado = repo.list_ingestions("tenant_a")

    assert len(resultado) == 2
    ids = {i.ingestion_id for i in resultado}
    assert ids == {"ing_001", "ing_002"}


def test_list_ingestions_for_evidence_devuelve_solo_vinculadas():
    repo = _repo()
    repo.save_ingestion(_make_ingestion(ingestion_id="ing_001", evidence_id="ev_001"))
    repo.save_ingestion(_make_ingestion(ingestion_id="ing_002", evidence_id="ev_002"))
    repo.save_ingestion(_make_ingestion(ingestion_id="ing_003", evidence_id="ev_001"))

    resultado = repo.list_ingestions_for_evidence("tenant_a", "ev_001")

    assert len(resultado) == 2
    ids = {i.ingestion_id for i in resultado}
    assert ids == {"ing_001", "ing_003"}


def test_list_ingestions_for_evidence_sin_vinculadas_devuelve_vacia():
    repo = _repo()
    repo.save_ingestion(_make_ingestion(ingestion_id="ing_001", evidence_id="ev_001"))

    resultado = repo.list_ingestions_for_evidence("tenant_a", "ev_999")

    assert resultado == []


def test_tenant_id_espacios_falla_en_save_ingestion():
    repo = _repo()
    with pytest.raises((ValueError, Exception)):
        _make_ingestion(tenant_id="")


def test_tenant_id_espacios_falla_en_get_ingestion():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.get_ingestion("   ", "ing_001")


def test_tenant_id_espacios_falla_en_list_ingestions():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.list_ingestions("   ")


def test_tenant_id_espacios_falla_en_list_ingestions_for_evidence():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.list_ingestions_for_evidence("   ", "ev_001")


def test_ingestion_id_vacio_falla_en_get_ingestion():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.get_ingestion("tenant_a", "")


def test_ingestion_id_espacios_falla_en_get_ingestion():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.get_ingestion("tenant_a", "   ")


def test_evidence_id_vacio_falla_en_list_ingestions_for_evidence():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.list_ingestions_for_evidence("tenant_a", "")


def test_evidence_id_espacios_falla_en_list_ingestions_for_evidence():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.list_ingestions_for_evidence("tenant_a", "   ")


# ===========================================================================
# VariableObservation — tests
# ===========================================================================

def test_guarda_y_recupera_observation():
    repo = _repo()
    obs = _make_observation()
    repo.save_observation(obs)

    resultado = repo.get_observation("tenant_a", "obs_001")

    assert resultado is not None
    assert resultado.observation_id == "obs_001"
    assert resultado.tenant_id == "tenant_a"


def test_upsert_observation_pisa_registro_previo():
    repo = _repo()
    obs_v1 = _make_observation(variable_code="margen_bruto")
    obs_v2 = _make_observation(variable_code="costo_total")

    repo.save_observation(obs_v1)
    repo.save_observation(obs_v2)

    resultado = repo.get_observation("tenant_a", "obs_001")
    assert resultado is not None
    assert resultado.variable_code == "costo_total"


def test_no_permite_leer_observation_de_otro_tenant():
    repo = _repo()
    obs = _make_observation(tenant_id="tenant_a", observation_id="obs_001")
    repo.save_observation(obs)

    resultado = repo.get_observation("tenant_b", "obs_001")

    assert resultado is None


def test_list_observations_filtra_por_tenant():
    repo = _repo()
    repo.save_observation(_make_observation(tenant_id="tenant_a", observation_id="obs_001"))
    repo.save_observation(_make_observation(tenant_id="tenant_a", observation_id="obs_002"))
    repo.save_observation(_make_observation(tenant_id="tenant_b", observation_id="obs_003"))

    resultado = repo.list_observations("tenant_a")

    assert len(resultado) == 2
    ids = {o.observation_id for o in resultado}
    assert ids == {"obs_001", "obs_002"}


def test_list_observations_for_evidence_devuelve_solo_vinculadas():
    repo = _repo()
    repo.save_observation(_make_observation(observation_id="obs_001", evidence_id="ev_001"))
    repo.save_observation(_make_observation(observation_id="obs_002", evidence_id="ev_002"))
    repo.save_observation(_make_observation(observation_id="obs_003", evidence_id="ev_001"))

    resultado = repo.list_observations_for_evidence("tenant_a", "ev_001")

    assert len(resultado) == 2
    ids = {o.observation_id for o in resultado}
    assert ids == {"obs_001", "obs_003"}


def test_list_observations_for_ingestion_devuelve_solo_vinculadas():
    repo = _repo()
    repo.save_observation(_make_observation(
        observation_id="obs_001", ingestion_id="ing_001"
    ))
    repo.save_observation(_make_observation(
        observation_id="obs_002", ingestion_id="ing_002"
    ))
    repo.save_observation(_make_observation(
        observation_id="obs_003", ingestion_id="ing_001"
    ))

    resultado = repo.list_observations_for_ingestion("tenant_a", "ing_001")

    assert len(resultado) == 2
    ids = {o.observation_id for o in resultado}
    assert ids == {"obs_001", "obs_003"}


def test_list_observations_for_ingestion_sin_vinculadas_devuelve_vacia():
    repo = _repo()
    repo.save_observation(_make_observation(observation_id="obs_001", ingestion_id=None))

    resultado = repo.list_observations_for_ingestion("tenant_a", "ing_999")

    assert resultado == []


def test_tenant_id_espacios_falla_en_save_observation():
    repo = _repo()
    with pytest.raises((ValueError, Exception)):
        _make_observation(tenant_id="")


def test_tenant_id_espacios_falla_en_get_observation():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.get_observation("   ", "obs_001")


def test_tenant_id_espacios_falla_en_list_observations():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.list_observations("   ")


def test_tenant_id_espacios_falla_en_list_observations_for_evidence():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.list_observations_for_evidence("   ", "ev_001")


def test_tenant_id_espacios_falla_en_list_observations_for_ingestion():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.list_observations_for_ingestion("   ", "ing_001")


def test_observation_id_vacio_falla_en_get_observation():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.get_observation("tenant_a", "")


def test_observation_id_espacios_falla_en_get_observation():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.get_observation("tenant_a", "   ")


def test_evidence_id_vacio_falla_en_list_observations_for_evidence():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.list_observations_for_evidence("tenant_a", "")


def test_ingestion_id_vacio_falla_en_list_observations_for_ingestion():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.list_observations_for_ingestion("tenant_a", "")


# ---------------------------------------------------------------------------
# Helpers para PathologyCandidate y FormulaExecution
# ---------------------------------------------------------------------------

def _make_pathology_candidate(
    tenant_id: str = "tenant_a",
    candidate_id: str = "cand_001",
    pathology_code: str = "margen_erosionado",
    status: str = "CANDIDATE",
    source_reception_id: str | None = None,
    **kwargs,
) -> PathologyCandidate:
    return PathologyCandidate(
        candidate_id=candidate_id,
        tenant_id=tenant_id,
        pathology_code=pathology_code,
        status=status,
        source_reception_id=source_reception_id,
        **kwargs,
    )


def _make_formula_execution(
    tenant_id: str = "tenant_a",
    execution_id: str = "exec_001",
    formula_code: str = "margen_bruto_pct",
    status: str = "BLOCKED",
    input_observation_ids: list[str] | None = None,
    **kwargs,
) -> FormulaExecution:
    return FormulaExecution(
        execution_id=execution_id,
        tenant_id=tenant_id,
        formula_code=formula_code,
        status=status,
        input_observation_ids=input_observation_ids or [],
        blocking_reason="sin variables disponibles" if status == "BLOCKED" else None,
        **kwargs,
    )


# ===========================================================================
# PathologyCandidate — tests
# ===========================================================================

def test_guarda_y_recupera_pathology_candidate():
    repo = _repo()
    cand = _make_pathology_candidate()
    repo.save_pathology_candidate(cand)

    resultado = repo.get_pathology_candidate("tenant_a", "cand_001")

    assert resultado is not None
    assert resultado.candidate_id == "cand_001"
    assert resultado.tenant_id == "tenant_a"


def test_upsert_pathology_candidate_pisa_registro_previo():
    repo = _repo()
    cand_v1 = _make_pathology_candidate(pathology_code="margen_erosionado")
    cand_v2 = _make_pathology_candidate(pathology_code="caja_inconsistente")

    repo.save_pathology_candidate(cand_v1)
    repo.save_pathology_candidate(cand_v2)

    resultado = repo.get_pathology_candidate("tenant_a", "cand_001")
    assert resultado is not None
    assert resultado.pathology_code == "caja_inconsistente"


def test_no_permite_leer_pathology_candidate_de_otro_tenant():
    repo = _repo()
    cand = _make_pathology_candidate(tenant_id="tenant_a", candidate_id="cand_001")
    repo.save_pathology_candidate(cand)

    resultado = repo.get_pathology_candidate("tenant_b", "cand_001")

    assert resultado is None


def test_list_pathology_candidates_filtra_por_tenant():
    repo = _repo()
    repo.save_pathology_candidate(
        _make_pathology_candidate(tenant_id="tenant_a", candidate_id="cand_001")
    )
    repo.save_pathology_candidate(
        _make_pathology_candidate(tenant_id="tenant_a", candidate_id="cand_002")
    )
    repo.save_pathology_candidate(
        _make_pathology_candidate(tenant_id="tenant_b", candidate_id="cand_003")
    )

    resultado = repo.list_pathology_candidates("tenant_a")

    assert len(resultado) == 2
    ids = {c.candidate_id for c in resultado}
    assert ids == {"cand_001", "cand_002"}


def test_list_pathology_candidates_for_reception_devuelve_solo_vinculados():
    repo = _repo()
    repo.save_pathology_candidate(
        _make_pathology_candidate(candidate_id="cand_001", source_reception_id="rec_001")
    )
    repo.save_pathology_candidate(
        _make_pathology_candidate(candidate_id="cand_002", source_reception_id="rec_002")
    )
    repo.save_pathology_candidate(
        _make_pathology_candidate(candidate_id="cand_003", source_reception_id="rec_001")
    )

    resultado = repo.list_pathology_candidates_for_reception("tenant_a", "rec_001")

    assert len(resultado) == 2
    ids = {c.candidate_id for c in resultado}
    assert ids == {"cand_001", "cand_003"}


def test_list_pathology_candidates_for_reception_sin_vinculados_devuelve_vacia():
    repo = _repo()
    repo.save_pathology_candidate(
        _make_pathology_candidate(candidate_id="cand_001", source_reception_id="rec_001")
    )

    resultado = repo.list_pathology_candidates_for_reception("tenant_a", "rec_999")

    assert resultado == []


def test_list_pathology_candidates_by_code_devuelve_solo_ese_codigo():
    repo = _repo()
    repo.save_pathology_candidate(
        _make_pathology_candidate(candidate_id="cand_001", pathology_code="margen_erosionado")
    )
    repo.save_pathology_candidate(
        _make_pathology_candidate(candidate_id="cand_002", pathology_code="caja_inconsistente")
    )
    repo.save_pathology_candidate(
        _make_pathology_candidate(candidate_id="cand_003", pathology_code="margen_erosionado")
    )

    resultado = repo.list_pathology_candidates_by_code("tenant_a", "margen_erosionado")

    assert len(resultado) == 2
    ids = {c.candidate_id for c in resultado}
    assert ids == {"cand_001", "cand_003"}


def test_tenant_id_espacios_falla_en_save_pathology_candidate():
    repo = _repo()
    with pytest.raises((ValueError, Exception)):
        _make_pathology_candidate(tenant_id="")


def test_tenant_id_espacios_falla_en_get_pathology_candidate():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.get_pathology_candidate("   ", "cand_001")


def test_tenant_id_espacios_falla_en_list_pathology_candidates():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.list_pathology_candidates("   ")


def test_tenant_id_espacios_falla_en_list_pathology_candidates_for_reception():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.list_pathology_candidates_for_reception("   ", "rec_001")


def test_tenant_id_espacios_falla_en_list_pathology_candidates_by_code():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.list_pathology_candidates_by_code("   ", "margen_erosionado")


def test_candidate_id_vacio_falla_en_get_pathology_candidate():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.get_pathology_candidate("tenant_a", "")


def test_reception_id_vacio_falla_en_list_pathology_candidates_for_reception():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.list_pathology_candidates_for_reception("tenant_a", "")


def test_pathology_code_vacio_falla_en_list_pathology_candidates_by_code():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.list_pathology_candidates_by_code("tenant_a", "")


# ===========================================================================
# FormulaExecution — tests
# ===========================================================================

def test_guarda_y_recupera_formula_execution():
    repo = _repo()
    exec_ = _make_formula_execution()
    repo.save_formula_execution(exec_)

    resultado = repo.get_formula_execution("tenant_a", "exec_001")

    assert resultado is not None
    assert resultado.execution_id == "exec_001"
    assert resultado.tenant_id == "tenant_a"


def test_upsert_formula_execution_pisa_registro_previo():
    repo = _repo()
    exec_v1 = _make_formula_execution(formula_code="margen_bruto_pct")
    exec_v2 = _make_formula_execution(formula_code="rotacion_stock")

    repo.save_formula_execution(exec_v1)
    repo.save_formula_execution(exec_v2)

    resultado = repo.get_formula_execution("tenant_a", "exec_001")
    assert resultado is not None
    assert resultado.formula_code == "rotacion_stock"


def test_no_permite_leer_formula_execution_de_otro_tenant():
    repo = _repo()
    exec_ = _make_formula_execution(tenant_id="tenant_a", execution_id="exec_001")
    repo.save_formula_execution(exec_)

    resultado = repo.get_formula_execution("tenant_b", "exec_001")

    assert resultado is None


def test_list_formula_executions_filtra_por_tenant():
    repo = _repo()
    repo.save_formula_execution(
        _make_formula_execution(tenant_id="tenant_a", execution_id="exec_001")
    )
    repo.save_formula_execution(
        _make_formula_execution(tenant_id="tenant_a", execution_id="exec_002")
    )
    repo.save_formula_execution(
        _make_formula_execution(tenant_id="tenant_b", execution_id="exec_003")
    )

    resultado = repo.list_formula_executions("tenant_a")

    assert len(resultado) == 2
    ids = {e.execution_id for e in resultado}
    assert ids == {"exec_001", "exec_002"}


def test_list_formula_executions_by_formula_devuelve_solo_ese_codigo():
    repo = _repo()
    repo.save_formula_execution(
        _make_formula_execution(execution_id="exec_001", formula_code="margen_bruto_pct")
    )
    repo.save_formula_execution(
        _make_formula_execution(execution_id="exec_002", formula_code="rotacion_stock")
    )
    repo.save_formula_execution(
        _make_formula_execution(execution_id="exec_003", formula_code="margen_bruto_pct")
    )

    resultado = repo.list_formula_executions_by_formula("tenant_a", "margen_bruto_pct")

    assert len(resultado) == 2
    ids = {e.execution_id for e in resultado}
    assert ids == {"exec_001", "exec_003"}


def test_list_formula_executions_for_observation_devuelve_solo_las_que_contienen_obs():
    repo = _repo()
    repo.save_formula_execution(
        _make_formula_execution(
            execution_id="exec_001",
            input_observation_ids=["obs_001", "obs_002"],
        )
    )
    repo.save_formula_execution(
        _make_formula_execution(
            execution_id="exec_002",
            input_observation_ids=["obs_003"],
        )
    )
    repo.save_formula_execution(
        _make_formula_execution(
            execution_id="exec_003",
            input_observation_ids=["obs_001"],
        )
    )

    resultado = repo.list_formula_executions_for_observation("tenant_a", "obs_001")

    assert len(resultado) == 2
    ids = {e.execution_id for e in resultado}
    assert ids == {"exec_001", "exec_003"}


def test_list_formula_executions_for_observation_sin_match_devuelve_vacia():
    repo = _repo()
    repo.save_formula_execution(
        _make_formula_execution(
            execution_id="exec_001",
            input_observation_ids=["obs_001"],
        )
    )

    resultado = repo.list_formula_executions_for_observation("tenant_a", "obs_999")

    assert resultado == []


def test_tenant_id_espacios_falla_en_save_formula_execution():
    repo = _repo()
    with pytest.raises((ValueError, Exception)):
        _make_formula_execution(tenant_id="")


def test_tenant_id_espacios_falla_en_get_formula_execution():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.get_formula_execution("   ", "exec_001")


def test_tenant_id_espacios_falla_en_list_formula_executions():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.list_formula_executions("   ")


def test_tenant_id_espacios_falla_en_list_formula_executions_by_formula():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.list_formula_executions_by_formula("   ", "margen_bruto_pct")


def test_tenant_id_espacios_falla_en_list_formula_executions_for_observation():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.list_formula_executions_for_observation("   ", "obs_001")


def test_execution_id_vacio_falla_en_get_formula_execution():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.get_formula_execution("tenant_a", "")


def test_formula_code_vacio_falla_en_list_formula_executions_by_formula():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.list_formula_executions_by_formula("tenant_a", "")


def test_observation_id_vacio_falla_en_list_formula_executions_for_observation():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.list_formula_executions_for_observation("tenant_a", "")


# ---------------------------------------------------------------------------
# Helpers para OperationalCaseCandidate y OperationalCase
# ---------------------------------------------------------------------------

def _make_case_candidate(
    tenant_id: str = "tenant_a",
    candidate_id: str = "cc_001",
    source_reception_id: str = "rec_001",
    status: str = "DRAFT",
    primary_pathology_code: str | None = None,
    **kwargs,
) -> OperationalCaseCandidate:
    return OperationalCaseCandidate(
        candidate_id=candidate_id,
        tenant_id=tenant_id,
        source_reception_id=source_reception_id,
        status=status,
        primary_pathology_code=primary_pathology_code,
        **kwargs,
    )


def _make_case(
    tenant_id: str = "tenant_a",
    case_id: str = "case_001",
    candidate_id: str = "cc_001",
    source_reception_id: str = "rec_001",
    primary_pathology_code: str = "margen_erosionado",
    status: str = "CLARIFICATION_REQUIRED",
    next_step: str = "solicitar datos de ventas",
    clarification_question: str | None = None,
    **kwargs,
) -> OperationalCase:
    # Si status requiere clarification_question y no se pasó, usar default
    if status == "CLARIFICATION_REQUIRED" and clarification_question is None:
        clarification_question = "¿Cuál fue el margen del último trimestre?"
    return OperationalCase(
        case_id=case_id,
        tenant_id=tenant_id,
        candidate_id=candidate_id,
        source_reception_id=source_reception_id,
        primary_pathology_code=primary_pathology_code,
        status=status,
        next_step=next_step,
        clarification_question=clarification_question,
        **kwargs,
    )


# ===========================================================================
# OperationalCaseCandidate — tests
# ===========================================================================

def test_guarda_y_recupera_case_candidate():
    repo = _repo()
    cc = _make_case_candidate()
    repo.save_case_candidate(cc)

    resultado = repo.get_case_candidate("tenant_a", "cc_001")

    assert resultado is not None
    assert resultado.candidate_id == "cc_001"
    assert resultado.tenant_id == "tenant_a"


def test_upsert_case_candidate_pisa_registro_previo():
    repo = _repo()
    cc_v1 = _make_case_candidate(status="DRAFT")
    cc_v2 = _make_case_candidate(status="NEEDS_EVIDENCE", evidence_gap_codes=["ventas_periodo"])

    repo.save_case_candidate(cc_v1)
    repo.save_case_candidate(cc_v2)

    resultado = repo.get_case_candidate("tenant_a", "cc_001")
    assert resultado is not None
    assert resultado.status == "NEEDS_EVIDENCE"


def test_no_permite_leer_case_candidate_de_otro_tenant():
    repo = _repo()
    cc = _make_case_candidate(tenant_id="tenant_a", candidate_id="cc_001")
    repo.save_case_candidate(cc)

    resultado = repo.get_case_candidate("tenant_b", "cc_001")

    assert resultado is None


def test_list_case_candidates_filtra_por_tenant():
    repo = _repo()
    repo.save_case_candidate(_make_case_candidate(tenant_id="tenant_a", candidate_id="cc_001"))
    repo.save_case_candidate(_make_case_candidate(tenant_id="tenant_a", candidate_id="cc_002"))
    repo.save_case_candidate(_make_case_candidate(tenant_id="tenant_b", candidate_id="cc_003"))

    resultado = repo.list_case_candidates("tenant_a")

    assert len(resultado) == 2
    ids = {c.candidate_id for c in resultado}
    assert ids == {"cc_001", "cc_002"}


def test_list_case_candidates_for_reception_devuelve_solo_vinculados():
    repo = _repo()
    repo.save_case_candidate(_make_case_candidate(candidate_id="cc_001", source_reception_id="rec_001"))
    repo.save_case_candidate(_make_case_candidate(candidate_id="cc_002", source_reception_id="rec_002"))
    repo.save_case_candidate(_make_case_candidate(candidate_id="cc_003", source_reception_id="rec_001"))

    resultado = repo.list_case_candidates_for_reception("tenant_a", "rec_001")

    assert len(resultado) == 2
    ids = {c.candidate_id for c in resultado}
    assert ids == {"cc_001", "cc_003"}


def test_list_case_candidates_for_reception_sin_vinculados_devuelve_vacia():
    repo = _repo()
    repo.save_case_candidate(_make_case_candidate(candidate_id="cc_001", source_reception_id="rec_001"))

    resultado = repo.list_case_candidates_for_reception("tenant_a", "rec_999")

    assert resultado == []


def test_list_case_candidates_by_primary_pathology_devuelve_solo_ese_codigo():
    repo = _repo()
    repo.save_case_candidate(
        _make_case_candidate(candidate_id="cc_001", primary_pathology_code="margen_erosionado")
    )
    repo.save_case_candidate(
        _make_case_candidate(candidate_id="cc_002", primary_pathology_code="caja_inconsistente")
    )
    repo.save_case_candidate(
        _make_case_candidate(candidate_id="cc_003", primary_pathology_code="margen_erosionado")
    )

    resultado = repo.list_case_candidates_by_primary_pathology("tenant_a", "margen_erosionado")

    assert len(resultado) == 2
    ids = {c.candidate_id for c in resultado}
    assert ids == {"cc_001", "cc_003"}


def test_tenant_id_espacios_falla_en_save_case_candidate():
    repo = _repo()
    with pytest.raises((ValueError, Exception)):
        _make_case_candidate(tenant_id="")


def test_tenant_id_espacios_falla_en_get_case_candidate():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.get_case_candidate("   ", "cc_001")


def test_tenant_id_espacios_falla_en_list_case_candidates():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.list_case_candidates("   ")


def test_tenant_id_espacios_falla_en_list_case_candidates_for_reception():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.list_case_candidates_for_reception("   ", "rec_001")


def test_tenant_id_espacios_falla_en_list_case_candidates_by_primary_pathology():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.list_case_candidates_by_primary_pathology("   ", "margen_erosionado")


def test_candidate_id_vacio_falla_en_get_case_candidate():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.get_case_candidate("tenant_a", "")


def test_reception_id_vacio_falla_en_list_case_candidates_for_reception():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.list_case_candidates_for_reception("tenant_a", "")


def test_pathology_code_vacio_falla_en_list_case_candidates_by_primary_pathology():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.list_case_candidates_by_primary_pathology("tenant_a", "")


# ===========================================================================
# OperationalCase — tests
# ===========================================================================

def test_guarda_y_recupera_case():
    repo = _repo()
    case = _make_case()
    repo.save_case(case)

    resultado = repo.get_case("tenant_a", "case_001")

    assert resultado is not None
    assert resultado.case_id == "case_001"
    assert resultado.tenant_id == "tenant_a"


def test_upsert_case_pisa_registro_previo():
    repo = _repo()
    case_v1 = _make_case(next_step="paso 1")
    case_v2 = _make_case(next_step="paso 2")

    repo.save_case(case_v1)
    repo.save_case(case_v2)

    resultado = repo.get_case("tenant_a", "case_001")
    assert resultado is not None
    assert resultado.next_step == "paso 2"


def test_no_permite_leer_case_de_otro_tenant():
    repo = _repo()
    case = _make_case(tenant_id="tenant_a", case_id="case_001")
    repo.save_case(case)

    resultado = repo.get_case("tenant_b", "case_001")

    assert resultado is None


def test_list_cases_filtra_por_tenant():
    repo = _repo()
    repo.save_case(_make_case(tenant_id="tenant_a", case_id="case_001"))
    repo.save_case(_make_case(tenant_id="tenant_a", case_id="case_002"))
    repo.save_case(_make_case(tenant_id="tenant_b", case_id="case_003"))

    resultado = repo.list_cases("tenant_a")

    assert len(resultado) == 2
    ids = {c.case_id for c in resultado}
    assert ids == {"case_001", "case_002"}


def test_list_cases_for_reception_devuelve_solo_vinculados():
    repo = _repo()
    repo.save_case(_make_case(case_id="case_001", source_reception_id="rec_001"))
    repo.save_case(_make_case(case_id="case_002", source_reception_id="rec_002"))
    repo.save_case(_make_case(case_id="case_003", source_reception_id="rec_001"))

    resultado = repo.list_cases_for_reception("tenant_a", "rec_001")

    assert len(resultado) == 2
    ids = {c.case_id for c in resultado}
    assert ids == {"case_001", "case_003"}


def test_list_cases_for_reception_sin_vinculados_devuelve_vacia():
    repo = _repo()
    repo.save_case(_make_case(case_id="case_001", source_reception_id="rec_001"))

    resultado = repo.list_cases_for_reception("tenant_a", "rec_999")

    assert resultado == []


def test_list_cases_by_primary_pathology_devuelve_solo_ese_codigo():
    repo = _repo()
    repo.save_case(_make_case(case_id="case_001", primary_pathology_code="margen_erosionado"))
    repo.save_case(_make_case(case_id="case_002", primary_pathology_code="caja_inconsistente"))
    repo.save_case(_make_case(case_id="case_003", primary_pathology_code="margen_erosionado"))

    resultado = repo.list_cases_by_primary_pathology("tenant_a", "margen_erosionado")

    assert len(resultado) == 2
    ids = {c.case_id for c in resultado}
    assert ids == {"case_001", "case_003"}


def test_list_cases_by_status_devuelve_solo_ese_status():
    repo = _repo()
    repo.save_case(_make_case(case_id="case_001", status="CLARIFICATION_REQUIRED"))
    repo.save_case(_make_case(case_id="case_002", status="INSUFFICIENT_EVIDENCE",
                              insufficiency_reason="faltan datos de ventas",
                              clarification_question=None))
    repo.save_case(_make_case(case_id="case_003", status="CLARIFICATION_REQUIRED"))

    resultado = repo.list_cases_by_status("tenant_a", "CLARIFICATION_REQUIRED")

    assert len(resultado) == 2
    ids = {c.case_id for c in resultado}
    assert ids == {"case_001", "case_003"}


def test_list_cases_by_status_sin_match_devuelve_vacia():
    repo = _repo()
    repo.save_case(_make_case(case_id="case_001", status="CLARIFICATION_REQUIRED"))

    resultado = repo.list_cases_by_status("tenant_a", "REJECTED_OUT_OF_SCOPE")

    assert resultado == []


def test_tenant_id_espacios_falla_en_save_case():
    repo = _repo()
    with pytest.raises((ValueError, Exception)):
        _make_case(tenant_id="")


def test_tenant_id_espacios_falla_en_get_case():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.get_case("   ", "case_001")


def test_tenant_id_espacios_falla_en_list_cases():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.list_cases("   ")


def test_tenant_id_espacios_falla_en_list_cases_for_reception():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.list_cases_for_reception("   ", "rec_001")


def test_tenant_id_espacios_falla_en_list_cases_by_primary_pathology():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.list_cases_by_primary_pathology("   ", "margen_erosionado")


def test_tenant_id_espacios_falla_en_list_cases_by_status():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.list_cases_by_status("   ", "CLARIFICATION_REQUIRED")


def test_case_id_vacio_falla_en_get_case():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.get_case("tenant_a", "")


def test_reception_id_vacio_falla_en_list_cases_for_reception():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.list_cases_for_reception("tenant_a", "")


def test_pathology_code_vacio_falla_en_list_cases_by_primary_pathology():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.list_cases_by_primary_pathology("tenant_a", "")


def test_status_vacio_falla_en_list_cases_by_status():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.list_cases_by_status("tenant_a", "")

# ---------------------------------------------------------------------------
# Helper para FindingRecord
# ---------------------------------------------------------------------------

def _make_finding(
    tenant_id: str = "tenant_a",
    finding_id: str = "finding_001",
    case_id: str = "case_001",
    title: str = "Margen bruto por debajo del umbral",
    description: str = "El margen bruto cayó un 12% respecto al trimestre anterior",
    severity: str = "MEDIUM",
    status: str = "DRAFT",
    human_review_required: bool = False,
    **kwargs,
) -> FindingRecord:
    return FindingRecord(
        finding_id=finding_id,
        tenant_id=tenant_id,
        case_id=case_id,
        title=title,
        description=description,
        severity=severity,
        status=status,
        human_review_required=human_review_required,
        **kwargs,
    )


# ===========================================================================
# FindingRecord — tests
# ===========================================================================

def test_guarda_y_recupera_finding():
    repo = _repo()
    finding = _make_finding()
    repo.save_finding(finding)

    resultado = repo.get_finding("tenant_a", "finding_001")

    assert resultado is not None
    assert resultado.finding_id == "finding_001"
    assert resultado.tenant_id == "tenant_a"


def test_upsert_finding_pisa_registro_previo():
    repo = _repo()
    f_v1 = _make_finding(title="Título original")
    f_v2 = _make_finding(title="Título actualizado")

    repo.save_finding(f_v1)
    repo.save_finding(f_v2)

    resultado = repo.get_finding("tenant_a", "finding_001")
    assert resultado is not None
    assert resultado.title == "Título actualizado"


def test_no_permite_leer_finding_de_otro_tenant():
    repo = _repo()
    finding = _make_finding(tenant_id="tenant_a", finding_id="finding_001")
    repo.save_finding(finding)

    resultado = repo.get_finding("tenant_b", "finding_001")

    assert resultado is None


def test_list_findings_filtra_por_tenant():
    repo = _repo()
    repo.save_finding(_make_finding(tenant_id="tenant_a", finding_id="finding_001"))
    repo.save_finding(_make_finding(tenant_id="tenant_a", finding_id="finding_002"))
    repo.save_finding(_make_finding(tenant_id="tenant_b", finding_id="finding_003"))

    resultado = repo.list_findings("tenant_a")

    assert len(resultado) == 2
    ids = {f.finding_id for f in resultado}
    assert ids == {"finding_001", "finding_002"}


def test_list_findings_tenant_sin_registros_devuelve_lista_vacia():
    repo = _repo()

    resultado = repo.list_findings("tenant_sin_datos")

    assert resultado == []


def test_list_findings_for_case_devuelve_solo_vinculados():
    repo = _repo()
    repo.save_finding(_make_finding(finding_id="finding_001", case_id="case_001"))
    repo.save_finding(_make_finding(finding_id="finding_002", case_id="case_002"))
    repo.save_finding(_make_finding(finding_id="finding_003", case_id="case_001"))

    resultado = repo.list_findings_for_case("tenant_a", "case_001")

    assert len(resultado) == 2
    ids = {f.finding_id for f in resultado}
    assert ids == {"finding_001", "finding_003"}


def test_list_findings_for_case_sin_vinculados_devuelve_vacia():
    repo = _repo()
    repo.save_finding(_make_finding(finding_id="finding_001", case_id="case_001"))

    resultado = repo.list_findings_for_case("tenant_a", "case_999")

    assert resultado == []


def test_list_findings_by_status_devuelve_solo_ese_status():
    repo = _repo()
    repo.save_finding(_make_finding(finding_id="finding_001", status="DRAFT"))
    repo.save_finding(_make_finding(finding_id="finding_002", status="NEEDS_REVIEW"))
    repo.save_finding(_make_finding(finding_id="finding_003", status="DRAFT"))

    resultado = repo.list_findings_by_status("tenant_a", "DRAFT")

    assert len(resultado) == 2
    ids = {f.finding_id for f in resultado}
    assert ids == {"finding_001", "finding_003"}


def test_list_findings_by_status_sin_match_devuelve_vacia():
    repo = _repo()
    repo.save_finding(_make_finding(finding_id="finding_001", status="DRAFT"))

    resultado = repo.list_findings_by_status("tenant_a", "REJECTED")

    assert resultado == []


def test_list_findings_by_severity_devuelve_solo_esa_severity():
    repo = _repo()
    repo.save_finding(_make_finding(finding_id="finding_001", severity="MEDIUM"))
    repo.save_finding(_make_finding(finding_id="finding_002", severity="LOW"))
    repo.save_finding(_make_finding(finding_id="finding_003", severity="MEDIUM"))

    resultado = repo.list_findings_by_severity("tenant_a", "MEDIUM")

    assert len(resultado) == 2
    ids = {f.finding_id for f in resultado}
    assert ids == {"finding_001", "finding_003"}


def test_list_findings_by_severity_sin_match_devuelve_vacia():
    repo = _repo()
    repo.save_finding(_make_finding(finding_id="finding_001", severity="LOW"))

    resultado = repo.list_findings_by_severity("tenant_a", "HIGH")

    assert resultado == []


def test_list_findings_requiring_human_review_devuelve_solo_los_que_requieren():
    repo = _repo()
    # CRITICAL siempre requiere human_review_required=True por contrato
    repo.save_finding(_make_finding(
        finding_id="finding_001",
        severity="CRITICAL",
        human_review_required=True,
    ))
    repo.save_finding(_make_finding(
        finding_id="finding_002",
        severity="LOW",
        human_review_required=False,
    ))
    repo.save_finding(_make_finding(
        finding_id="finding_003",
        severity="HIGH",
        human_review_required=True,
    ))

    resultado = repo.list_findings_requiring_human_review("tenant_a")

    assert len(resultado) == 2
    ids = {f.finding_id for f in resultado}
    assert ids == {"finding_001", "finding_003"}


def test_list_findings_requiring_human_review_sin_match_devuelve_vacia():
    repo = _repo()
    repo.save_finding(_make_finding(finding_id="finding_001", human_review_required=False))

    resultado = repo.list_findings_requiring_human_review("tenant_a")

    assert resultado == []


def test_aislamiento_findings_entre_tenants():
    repo = _repo()
    repo.save_finding(_make_finding(tenant_id="tenant_a", finding_id="finding_001"))
    repo.save_finding(_make_finding(tenant_id="tenant_b", finding_id="finding_001"))

    resultado_a = repo.list_findings("tenant_a")
    resultado_b = repo.list_findings("tenant_b")

    assert len(resultado_a) == 1
    assert len(resultado_b) == 1
    assert resultado_a[0].tenant_id == "tenant_a"
    assert resultado_b[0].tenant_id == "tenant_b"


# ---------------------------------------------------------------------------
# Fail-closed: tenant_id vacío en todos los métodos de FindingRecord
# ---------------------------------------------------------------------------

def test_tenant_id_vacio_falla_en_save_finding():
    repo = _repo()
    with pytest.raises((ValueError, Exception)):
        _make_finding(tenant_id="")


def test_tenant_id_espacios_falla_en_save_finding():
    repo = _repo()
    with pytest.raises((ValueError, Exception)):
        _make_finding(tenant_id="   ")


def test_tenant_id_espacios_falla_en_get_finding():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.get_finding("   ", "finding_001")


def test_tenant_id_espacios_falla_en_list_findings():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.list_findings("   ")


def test_tenant_id_espacios_falla_en_list_findings_for_case():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.list_findings_for_case("   ", "case_001")


def test_tenant_id_espacios_falla_en_list_findings_by_status():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.list_findings_by_status("   ", "DRAFT")


def test_tenant_id_espacios_falla_en_list_findings_by_severity():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.list_findings_by_severity("   ", "LOW")


def test_tenant_id_espacios_falla_en_list_findings_requiring_human_review():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.list_findings_requiring_human_review("   ")


# ---------------------------------------------------------------------------
# Fail-closed: IDs específicos vacíos
# ---------------------------------------------------------------------------

def test_finding_id_vacio_falla_en_get_finding():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.get_finding("tenant_a", "")


def test_finding_id_espacios_falla_en_get_finding():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.get_finding("tenant_a", "   ")


def test_case_id_vacio_falla_en_list_findings_for_case():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.list_findings_for_case("tenant_a", "")


def test_case_id_espacios_falla_en_list_findings_for_case():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.list_findings_for_case("tenant_a", "   ")


def test_status_vacio_falla_en_list_findings_by_status():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.list_findings_by_status("tenant_a", "")


def test_status_espacios_falla_en_list_findings_by_status():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.list_findings_by_status("tenant_a", "   ")


def test_severity_vacio_falla_en_list_findings_by_severity():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.list_findings_by_severity("tenant_a", "")


def test_severity_espacios_falla_en_list_findings_by_severity():
    repo = _repo()
    with pytest.raises(ValueError):
        repo.list_findings_by_severity("tenant_a", "   ")
