"""Repositorio in-memory para persistencia táctica clínico-operacional.

Responsabilidad:
    Persistencia táctica in-memory para tests y futura orquestación.

Regla rectora:
    IA interpreta. Determinístico decide. Evidencia gobierna. Dueño confirma.

Este repositorio:
    - NO diagnostica.
    - NO clasifica.
    - NO calcula.
    - NO emite hallazgos.
    - NO decide por el dueño.

Garantías:
    - Aislamiento soberano por tenant_id: un tenant nunca lee registros de otro.
    - Fail-closed: tenant_id y cualquier ID específico vacíos lanzan ValueError.
    - Upsert por (tenant_id, id): save pisa el registro previo del mismo par.
    - Sin DB, sin red, sin dependencias externas.
"""

from __future__ import annotations

from app.contracts.clinical_operational_contracts import (
    DocumentIngestion,
    EvidenceRecord,
    FormulaExecution,
    PathologyCandidate,
    ReceptionRecord,
    VariableObservation,
)


def _require_non_empty(value: str, field_name: str) -> None:
    """Fail-closed: rechaza strings vacíos o solo espacios."""
    if not value or not value.strip():
        raise ValueError(f"{field_name} no puede ser vacío: {value!r}")


class InMemoryClinicalOperationalRepository:
    """Repositorio in-memory para ReceptionRecord y EvidenceRecord.

    Almacena registros en dicts indexados por (tenant_id, id).
    Cada operación valida tenant_id antes de tocar el store.
    """

    def __init__(self) -> None:
        # dict[(tenant_id, reception_id), ReceptionRecord]
        self._receptions: dict[tuple[str, str], ReceptionRecord] = {}
        # dict[(tenant_id, evidence_id), EvidenceRecord]
        self._evidence: dict[tuple[str, str], EvidenceRecord] = {}
        # dict[(tenant_id, ingestion_id), DocumentIngestion]
        self._ingestions: dict[tuple[str, str], DocumentIngestion] = {}
        # dict[(tenant_id, observation_id), VariableObservation]
        self._observations: dict[tuple[str, str], VariableObservation] = {}
        # dict[(tenant_id, candidate_id), PathologyCandidate]
        self._pathology_candidates: dict[tuple[str, str], PathologyCandidate] = {}
        # dict[(tenant_id, execution_id), FormulaExecution]
        self._formula_executions: dict[tuple[str, str], FormulaExecution] = {}

    # ------------------------------------------------------------------
    # ReceptionRecord
    # ------------------------------------------------------------------

    def save_reception(self, record: ReceptionRecord) -> ReceptionRecord:
        """Persiste o actualiza un ReceptionRecord (upsert por tenant+id).

        El contrato Pydantic ya valida tenant_id y reception_id no vacíos.
        El repositorio valida adicionalmente para fail-closed explícito.
        """
        _require_non_empty(record.tenant_id, "tenant_id")
        _require_non_empty(record.reception_id, "reception_id")
        key = (record.tenant_id, record.reception_id)
        self._receptions[key] = record
        return record

    def get_reception(
        self, tenant_id: str, reception_id: str
    ) -> ReceptionRecord | None:
        """Devuelve el ReceptionRecord del tenant, o None si no existe."""
        _require_non_empty(tenant_id, "tenant_id")
        _require_non_empty(reception_id, "reception_id")
        return self._receptions.get((tenant_id, reception_id))

    def list_receptions(self, tenant_id: str) -> list[ReceptionRecord]:
        """Devuelve todos los ReceptionRecord del tenant, en orden de inserción."""
        _require_non_empty(tenant_id, "tenant_id")
        return [
            record
            for (tid, _), record in self._receptions.items()
            if tid == tenant_id
        ]

    # ------------------------------------------------------------------
    # EvidenceRecord
    # ------------------------------------------------------------------

    def save_evidence(self, record: EvidenceRecord) -> EvidenceRecord:
        """Persiste o actualiza un EvidenceRecord (upsert por tenant+id)."""
        _require_non_empty(record.tenant_id, "tenant_id")
        _require_non_empty(record.evidence_id, "evidence_id")
        key = (record.tenant_id, record.evidence_id)
        self._evidence[key] = record
        return record

    def get_evidence(
        self, tenant_id: str, evidence_id: str
    ) -> EvidenceRecord | None:
        """Devuelve el EvidenceRecord del tenant, o None si no existe."""
        _require_non_empty(tenant_id, "tenant_id")
        _require_non_empty(evidence_id, "evidence_id")
        return self._evidence.get((tenant_id, evidence_id))

    def list_evidence(self, tenant_id: str) -> list[EvidenceRecord]:
        """Devuelve todos los EvidenceRecord del tenant."""
        _require_non_empty(tenant_id, "tenant_id")
        return [
            record
            for (tid, _), record in self._evidence.items()
            if tid == tenant_id
        ]

    def list_evidence_for_reception(
        self, tenant_id: str, reception_id: str
    ) -> list[EvidenceRecord]:
        """Devuelve EvidenceRecord del tenant vinculados a una reception."""
        _require_non_empty(tenant_id, "tenant_id")
        _require_non_empty(reception_id, "reception_id")
        return [
            record
            for (tid, _), record in self._evidence.items()
            if tid == tenant_id and record.linked_reception_id == reception_id
        ]

    # ------------------------------------------------------------------
    # DocumentIngestion
    # ------------------------------------------------------------------

    def save_ingestion(self, record: DocumentIngestion) -> DocumentIngestion:
        """Persiste o actualiza un DocumentIngestion (upsert por tenant+id)."""
        _require_non_empty(record.tenant_id, "tenant_id")
        _require_non_empty(record.ingestion_id, "ingestion_id")
        key = (record.tenant_id, record.ingestion_id)
        self._ingestions[key] = record
        return record

    def get_ingestion(
        self, tenant_id: str, ingestion_id: str
    ) -> DocumentIngestion | None:
        """Devuelve el DocumentIngestion del tenant, o None si no existe."""
        _require_non_empty(tenant_id, "tenant_id")
        _require_non_empty(ingestion_id, "ingestion_id")
        return self._ingestions.get((tenant_id, ingestion_id))

    def list_ingestions(self, tenant_id: str) -> list[DocumentIngestion]:
        """Devuelve todos los DocumentIngestion del tenant."""
        _require_non_empty(tenant_id, "tenant_id")
        return [
            record
            for (tid, _), record in self._ingestions.items()
            if tid == tenant_id
        ]

    def list_ingestions_for_evidence(
        self, tenant_id: str, evidence_id: str
    ) -> list[DocumentIngestion]:
        """Devuelve DocumentIngestion del tenant vinculados a una evidence."""
        _require_non_empty(tenant_id, "tenant_id")
        _require_non_empty(evidence_id, "evidence_id")
        return [
            record
            for (tid, _), record in self._ingestions.items()
            if tid == tenant_id and record.evidence_id == evidence_id
        ]

    # ------------------------------------------------------------------
    # VariableObservation
    # ------------------------------------------------------------------

    def save_observation(self, record: VariableObservation) -> VariableObservation:
        """Persiste o actualiza un VariableObservation (upsert por tenant+id)."""
        _require_non_empty(record.tenant_id, "tenant_id")
        _require_non_empty(record.observation_id, "observation_id")
        key = (record.tenant_id, record.observation_id)
        self._observations[key] = record
        return record

    def get_observation(
        self, tenant_id: str, observation_id: str
    ) -> VariableObservation | None:
        """Devuelve el VariableObservation del tenant, o None si no existe."""
        _require_non_empty(tenant_id, "tenant_id")
        _require_non_empty(observation_id, "observation_id")
        return self._observations.get((tenant_id, observation_id))

    def list_observations(self, tenant_id: str) -> list[VariableObservation]:
        """Devuelve todos los VariableObservation del tenant."""
        _require_non_empty(tenant_id, "tenant_id")
        return [
            record
            for (tid, _), record in self._observations.items()
            if tid == tenant_id
        ]

    def list_observations_for_evidence(
        self, tenant_id: str, evidence_id: str
    ) -> list[VariableObservation]:
        """Devuelve VariableObservation del tenant vinculados a una evidence."""
        _require_non_empty(tenant_id, "tenant_id")
        _require_non_empty(evidence_id, "evidence_id")
        return [
            record
            for (tid, _), record in self._observations.items()
            if tid == tenant_id and record.evidence_id == evidence_id
        ]

    def list_observations_for_ingestion(
        self, tenant_id: str, ingestion_id: str
    ) -> list[VariableObservation]:
        """Devuelve VariableObservation del tenant vinculados a una ingestion."""
        _require_non_empty(tenant_id, "tenant_id")
        _require_non_empty(ingestion_id, "ingestion_id")
        return [
            record
            for (tid, _), record in self._observations.items()
            if tid == tenant_id and record.ingestion_id == ingestion_id
        ]

    # ------------------------------------------------------------------
    # PathologyCandidate
    # ------------------------------------------------------------------

    def save_pathology_candidate(
        self, record: PathologyCandidate
    ) -> PathologyCandidate:
        """Persiste o actualiza un PathologyCandidate (upsert por tenant+id)."""
        _require_non_empty(record.tenant_id, "tenant_id")
        _require_non_empty(record.candidate_id, "candidate_id")
        key = (record.tenant_id, record.candidate_id)
        self._pathology_candidates[key] = record
        return record

    def get_pathology_candidate(
        self, tenant_id: str, candidate_id: str
    ) -> PathologyCandidate | None:
        """Devuelve el PathologyCandidate del tenant, o None si no existe."""
        _require_non_empty(tenant_id, "tenant_id")
        _require_non_empty(candidate_id, "candidate_id")
        return self._pathology_candidates.get((tenant_id, candidate_id))

    def list_pathology_candidates(
        self, tenant_id: str
    ) -> list[PathologyCandidate]:
        """Devuelve todos los PathologyCandidate del tenant."""
        _require_non_empty(tenant_id, "tenant_id")
        return [
            record
            for (tid, _), record in self._pathology_candidates.items()
            if tid == tenant_id
        ]

    def list_pathology_candidates_for_reception(
        self, tenant_id: str, reception_id: str
    ) -> list[PathologyCandidate]:
        """Devuelve PathologyCandidate del tenant vinculados a una reception."""
        _require_non_empty(tenant_id, "tenant_id")
        _require_non_empty(reception_id, "reception_id")
        return [
            record
            for (tid, _), record in self._pathology_candidates.items()
            if tid == tenant_id and record.source_reception_id == reception_id
        ]

    def list_pathology_candidates_by_code(
        self, tenant_id: str, pathology_code: str
    ) -> list[PathologyCandidate]:
        """Devuelve PathologyCandidate del tenant con el pathology_code dado."""
        _require_non_empty(tenant_id, "tenant_id")
        _require_non_empty(pathology_code, "pathology_code")
        return [
            record
            for (tid, _), record in self._pathology_candidates.items()
            if tid == tenant_id and record.pathology_code == pathology_code
        ]

    # ------------------------------------------------------------------
    # FormulaExecution
    # ------------------------------------------------------------------

    def save_formula_execution(
        self, record: FormulaExecution
    ) -> FormulaExecution:
        """Persiste o actualiza un FormulaExecution (upsert por tenant+id)."""
        _require_non_empty(record.tenant_id, "tenant_id")
        _require_non_empty(record.execution_id, "execution_id")
        key = (record.tenant_id, record.execution_id)
        self._formula_executions[key] = record
        return record

    def get_formula_execution(
        self, tenant_id: str, execution_id: str
    ) -> FormulaExecution | None:
        """Devuelve el FormulaExecution del tenant, o None si no existe."""
        _require_non_empty(tenant_id, "tenant_id")
        _require_non_empty(execution_id, "execution_id")
        return self._formula_executions.get((tenant_id, execution_id))

    def list_formula_executions(
        self, tenant_id: str
    ) -> list[FormulaExecution]:
        """Devuelve todos los FormulaExecution del tenant."""
        _require_non_empty(tenant_id, "tenant_id")
        return [
            record
            for (tid, _), record in self._formula_executions.items()
            if tid == tenant_id
        ]

    def list_formula_executions_by_formula(
        self, tenant_id: str, formula_code: str
    ) -> list[FormulaExecution]:
        """Devuelve FormulaExecution del tenant con el formula_code dado."""
        _require_non_empty(tenant_id, "tenant_id")
        _require_non_empty(formula_code, "formula_code")
        return [
            record
            for (tid, _), record in self._formula_executions.items()
            if tid == tenant_id and record.formula_code == formula_code
        ]

    def list_formula_executions_for_observation(
        self, tenant_id: str, observation_id: str
    ) -> list[FormulaExecution]:
        """Devuelve FormulaExecution del tenant que contienen observation_id
        en su lista input_observation_ids."""
        _require_non_empty(tenant_id, "tenant_id")
        _require_non_empty(observation_id, "observation_id")
        return [
            record
            for (tid, _), record in self._formula_executions.items()
            if tid == tenant_id and observation_id in record.input_observation_ids
        ]
