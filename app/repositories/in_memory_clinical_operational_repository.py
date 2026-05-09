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
    FindingRecord,
    FindingSeverity,
    FindingStatus,
    FormulaExecution,
    OperationalCase,
    OperationalCaseCandidate,
    OperationalCaseStatus,
    PathologyCandidate,
    ReceptionRecord,
    VariableObservation,
)
from app.repositories.clinical_operational_repository_port import (
    ClinicalOperationalRepositoryPort,
)


def _require_non_empty(value: str, field_name: str) -> None:
    """Fail-closed: rechaza strings vacíos o solo espacios."""
    if not value or not value.strip():
        raise ValueError(f"{field_name} no puede ser vacío: {value!r}")


class InMemoryClinicalOperationalRepository(ClinicalOperationalRepositoryPort):
    """Repositorio in-memory para los 9 contratos clínico-operacionales.

    Almacena registros en dicts indexados por (tenant_id, id).
    Cada operación valida tenant_id antes de tocar el store.

    Implementa ClinicalOperationalRepositoryPort.
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
        # dict[(tenant_id, candidate_id), OperationalCaseCandidate]
        self._case_candidates: dict[tuple[str, str], OperationalCaseCandidate] = {}
        # dict[(tenant_id, case_id), OperationalCase]
        self._cases: dict[tuple[str, str], OperationalCase] = {}
        # dict[(tenant_id, finding_id), FindingRecord]
        self._findings: dict[tuple[str, str], FindingRecord] = {}

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

    # ------------------------------------------------------------------
    # OperationalCaseCandidate
    # ------------------------------------------------------------------

    def save_case_candidate(
        self, record: OperationalCaseCandidate
    ) -> OperationalCaseCandidate:
        """Persiste o actualiza un OperationalCaseCandidate (upsert por tenant+id)."""
        _require_non_empty(record.tenant_id, "tenant_id")
        _require_non_empty(record.candidate_id, "candidate_id")
        key = (record.tenant_id, record.candidate_id)
        self._case_candidates[key] = record
        return record

    def get_case_candidate(
        self, tenant_id: str, candidate_id: str
    ) -> OperationalCaseCandidate | None:
        """Devuelve el OperationalCaseCandidate del tenant, o None si no existe."""
        _require_non_empty(tenant_id, "tenant_id")
        _require_non_empty(candidate_id, "candidate_id")
        return self._case_candidates.get((tenant_id, candidate_id))

    def list_case_candidates(
        self, tenant_id: str
    ) -> list[OperationalCaseCandidate]:
        """Devuelve todos los OperationalCaseCandidate del tenant."""
        _require_non_empty(tenant_id, "tenant_id")
        return [
            record
            for (tid, _), record in self._case_candidates.items()
            if tid == tenant_id
        ]

    def list_case_candidates_for_reception(
        self, tenant_id: str, reception_id: str
    ) -> list[OperationalCaseCandidate]:
        """Devuelve OperationalCaseCandidate del tenant vinculados a una reception."""
        _require_non_empty(tenant_id, "tenant_id")
        _require_non_empty(reception_id, "reception_id")
        return [
            record
            for (tid, _), record in self._case_candidates.items()
            if tid == tenant_id and record.source_reception_id == reception_id
        ]

    def list_case_candidates_by_primary_pathology(
        self, tenant_id: str, pathology_code: str
    ) -> list[OperationalCaseCandidate]:
        """Devuelve OperationalCaseCandidate del tenant con el primary_pathology_code dado."""
        _require_non_empty(tenant_id, "tenant_id")
        _require_non_empty(pathology_code, "pathology_code")
        return [
            record
            for (tid, _), record in self._case_candidates.items()
            if tid == tenant_id and record.primary_pathology_code == pathology_code
        ]

    # ------------------------------------------------------------------
    # OperationalCase
    # ------------------------------------------------------------------

    def save_case(self, record: OperationalCase) -> OperationalCase:
        """Persiste o actualiza un OperationalCase (upsert por tenant+id)."""
        _require_non_empty(record.tenant_id, "tenant_id")
        _require_non_empty(record.case_id, "case_id")
        key = (record.tenant_id, record.case_id)
        self._cases[key] = record
        return record

    def get_case(
        self, tenant_id: str, case_id: str
    ) -> OperationalCase | None:
        """Devuelve el OperationalCase del tenant, o None si no existe."""
        _require_non_empty(tenant_id, "tenant_id")
        _require_non_empty(case_id, "case_id")
        return self._cases.get((tenant_id, case_id))

    def list_cases(self, tenant_id: str) -> list[OperationalCase]:
        """Devuelve todos los OperationalCase del tenant."""
        _require_non_empty(tenant_id, "tenant_id")
        return [
            record
            for (tid, _), record in self._cases.items()
            if tid == tenant_id
        ]

    def list_cases_for_reception(
        self, tenant_id: str, reception_id: str
    ) -> list[OperationalCase]:
        """Devuelve OperationalCase del tenant vinculados a una reception."""
        _require_non_empty(tenant_id, "tenant_id")
        _require_non_empty(reception_id, "reception_id")
        return [
            record
            for (tid, _), record in self._cases.items()
            if tid == tenant_id and record.source_reception_id == reception_id
        ]

    def list_cases_by_primary_pathology(
        self, tenant_id: str, pathology_code: str
    ) -> list[OperationalCase]:
        """Devuelve OperationalCase del tenant con el primary_pathology_code dado."""
        _require_non_empty(tenant_id, "tenant_id")
        _require_non_empty(pathology_code, "pathology_code")
        return [
            record
            for (tid, _), record in self._cases.items()
            if tid == tenant_id and record.primary_pathology_code == pathology_code
        ]

    def list_cases_by_status(
        self, tenant_id: str, status: OperationalCaseStatus
    ) -> list[OperationalCase]:
        """Devuelve OperationalCase del tenant con el status dado."""
        _require_non_empty(tenant_id, "tenant_id")
        _require_non_empty(status, "status")
        return [
            record
            for (tid, _), record in self._cases.items()
            if tid == tenant_id and record.status == status
        ]

    # ------------------------------------------------------------------
    # FindingRecord
    # ------------------------------------------------------------------

    def save_finding(self, record: FindingRecord) -> FindingRecord:
        """Persiste o actualiza un FindingRecord (upsert por tenant+id)."""
        _require_non_empty(record.tenant_id, "tenant_id")
        _require_non_empty(record.finding_id, "finding_id")
        key = (record.tenant_id, record.finding_id)
        self._findings[key] = record
        return record

    def get_finding(
        self, tenant_id: str, finding_id: str
    ) -> FindingRecord | None:
        """Devuelve el FindingRecord del tenant, o None si no existe."""
        _require_non_empty(tenant_id, "tenant_id")
        _require_non_empty(finding_id, "finding_id")
        return self._findings.get((tenant_id, finding_id))

    def list_findings(self, tenant_id: str) -> list[FindingRecord]:
        """Devuelve todos los FindingRecord del tenant."""
        _require_non_empty(tenant_id, "tenant_id")
        return [
            record
            for (tid, _), record in self._findings.items()
            if tid == tenant_id
        ]

    def list_findings_for_case(
        self, tenant_id: str, case_id: str
    ) -> list[FindingRecord]:
        """Devuelve FindingRecord del tenant vinculados a un case_id."""
        _require_non_empty(tenant_id, "tenant_id")
        _require_non_empty(case_id, "case_id")
        return [
            record
            for (tid, _), record in self._findings.items()
            if tid == tenant_id and record.case_id == case_id
        ]

    def list_findings_by_status(
        self, tenant_id: str, status: FindingStatus
    ) -> list[FindingRecord]:
        """Devuelve FindingRecord del tenant con el status dado."""
        _require_non_empty(tenant_id, "tenant_id")
        _require_non_empty(status, "status")
        return [
            record
            for (tid, _), record in self._findings.items()
            if tid == tenant_id and record.status == status
        ]

    def list_findings_by_severity(
        self, tenant_id: str, severity: FindingSeverity
    ) -> list[FindingRecord]:
        """Devuelve FindingRecord del tenant con la severity dada."""
        _require_non_empty(tenant_id, "tenant_id")
        _require_non_empty(severity, "severity")
        return [
            record
            for (tid, _), record in self._findings.items()
            if tid == tenant_id and record.severity == severity
        ]

    def list_findings_requiring_human_review(
        self, tenant_id: str
    ) -> list[FindingRecord]:
        """Devuelve FindingRecord del tenant donde human_review_required == True."""
        _require_non_empty(tenant_id, "tenant_id")
        return [
            record
            for (tid, _), record in self._findings.items()
            if tid == tenant_id and record.human_review_required is True
        ]
