"""Port (Protocol) para repositorio clínico-operacional.

Define la interfaz formal que toda implementación de repositorio
clínico-operacional debe cumplir.

Responsabilidad:
    Contrato de persistencia para los 9 tipos de registros clínico-operacionales.

Garantías esperadas de cualquier implementación:
    - Aislamiento soberano por tenant_id.
    - Fail-closed ante IDs vacíos.
    - Upsert semántico por (tenant_id, id).
    - Sin lógica de negocio, diagnóstico ni clasificación.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

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


@runtime_checkable
class ClinicalOperationalRepositoryPort(Protocol):
    """Protocol que define la interfaz de persistencia clínico-operacional.

    Toda implementación concreta (in-memory, Supabase, etc.) debe cumplir
    con estas firmas exactas.
    """

    # ------------------------------------------------------------------
    # ReceptionRecord
    # ------------------------------------------------------------------

    def save_reception(self, record: ReceptionRecord) -> ReceptionRecord:
        """Persiste o actualiza un ReceptionRecord (upsert por tenant+id)."""
        ...

    def get_reception(
        self, tenant_id: str, reception_id: str
    ) -> ReceptionRecord | None:
        """Devuelve el ReceptionRecord del tenant, o None si no existe."""
        ...

    def list_receptions(self, tenant_id: str) -> list[ReceptionRecord]:
        """Devuelve todos los ReceptionRecord del tenant."""
        ...

    # ------------------------------------------------------------------
    # EvidenceRecord
    # ------------------------------------------------------------------

    def save_evidence(self, record: EvidenceRecord) -> EvidenceRecord:
        """Persiste o actualiza un EvidenceRecord (upsert por tenant+id)."""
        ...

    def get_evidence(
        self, tenant_id: str, evidence_id: str
    ) -> EvidenceRecord | None:
        """Devuelve el EvidenceRecord del tenant, o None si no existe."""
        ...

    def list_evidence(self, tenant_id: str) -> list[EvidenceRecord]:
        """Devuelve todos los EvidenceRecord del tenant."""
        ...

    def list_evidence_for_reception(
        self, tenant_id: str, reception_id: str
    ) -> list[EvidenceRecord]:
        """Devuelve EvidenceRecord del tenant vinculados a una reception."""
        ...

    # ------------------------------------------------------------------
    # DocumentIngestion
    # ------------------------------------------------------------------

    def save_ingestion(self, record: DocumentIngestion) -> DocumentIngestion:
        """Persiste o actualiza un DocumentIngestion (upsert por tenant+id)."""
        ...

    def get_ingestion(
        self, tenant_id: str, ingestion_id: str
    ) -> DocumentIngestion | None:
        """Devuelve el DocumentIngestion del tenant, o None si no existe."""
        ...

    def list_ingestions(self, tenant_id: str) -> list[DocumentIngestion]:
        """Devuelve todos los DocumentIngestion del tenant."""
        ...

    def list_ingestions_for_evidence(
        self, tenant_id: str, evidence_id: str
    ) -> list[DocumentIngestion]:
        """Devuelve DocumentIngestion del tenant vinculados a una evidence."""
        ...

    # ------------------------------------------------------------------
    # VariableObservation
    # ------------------------------------------------------------------

    def save_observation(self, record: VariableObservation) -> VariableObservation:
        """Persiste o actualiza un VariableObservation (upsert por tenant+id)."""
        ...

    def get_observation(
        self, tenant_id: str, observation_id: str
    ) -> VariableObservation | None:
        """Devuelve el VariableObservation del tenant, o None si no existe."""
        ...

    def list_observations(self, tenant_id: str) -> list[VariableObservation]:
        """Devuelve todos los VariableObservation del tenant."""
        ...

    def list_observations_for_evidence(
        self, tenant_id: str, evidence_id: str
    ) -> list[VariableObservation]:
        """Devuelve VariableObservation del tenant vinculados a una evidence."""
        ...

    def list_observations_for_ingestion(
        self, tenant_id: str, ingestion_id: str
    ) -> list[VariableObservation]:
        """Devuelve VariableObservation del tenant vinculados a una ingestion."""
        ...

    # ------------------------------------------------------------------
    # PathologyCandidate
    # ------------------------------------------------------------------

    def save_pathology_candidate(
        self, record: PathologyCandidate
    ) -> PathologyCandidate:
        """Persiste o actualiza un PathologyCandidate (upsert por tenant+id)."""
        ...

    def get_pathology_candidate(
        self, tenant_id: str, candidate_id: str
    ) -> PathologyCandidate | None:
        """Devuelve el PathologyCandidate del tenant, o None si no existe."""
        ...

    def list_pathology_candidates(
        self, tenant_id: str
    ) -> list[PathologyCandidate]:
        """Devuelve todos los PathologyCandidate del tenant."""
        ...

    def list_pathology_candidates_for_reception(
        self, tenant_id: str, reception_id: str
    ) -> list[PathologyCandidate]:
        """Devuelve PathologyCandidate del tenant vinculados a una reception."""
        ...

    def list_pathology_candidates_by_code(
        self, tenant_id: str, pathology_code: str
    ) -> list[PathologyCandidate]:
        """Devuelve PathologyCandidate del tenant con el pathology_code dado."""
        ...

    # ------------------------------------------------------------------
    # FormulaExecution
    # ------------------------------------------------------------------

    def save_formula_execution(
        self, record: FormulaExecution
    ) -> FormulaExecution:
        """Persiste o actualiza un FormulaExecution (upsert por tenant+id)."""
        ...

    def get_formula_execution(
        self, tenant_id: str, execution_id: str
    ) -> FormulaExecution | None:
        """Devuelve el FormulaExecution del tenant, o None si no existe."""
        ...

    def list_formula_executions(
        self, tenant_id: str
    ) -> list[FormulaExecution]:
        """Devuelve todos los FormulaExecution del tenant."""
        ...

    def list_formula_executions_by_formula(
        self, tenant_id: str, formula_code: str
    ) -> list[FormulaExecution]:
        """Devuelve FormulaExecution del tenant con el formula_code dado."""
        ...

    def list_formula_executions_for_observation(
        self, tenant_id: str, observation_id: str
    ) -> list[FormulaExecution]:
        """Devuelve FormulaExecution del tenant que contienen observation_id
        en su lista input_observation_ids."""
        ...

    # ------------------------------------------------------------------
    # OperationalCaseCandidate
    # ------------------------------------------------------------------

    def save_case_candidate(
        self, record: OperationalCaseCandidate
    ) -> OperationalCaseCandidate:
        """Persiste o actualiza un OperationalCaseCandidate (upsert por tenant+id)."""
        ...

    def get_case_candidate(
        self, tenant_id: str, candidate_id: str
    ) -> OperationalCaseCandidate | None:
        """Devuelve el OperationalCaseCandidate del tenant, o None si no existe."""
        ...

    def list_case_candidates(
        self, tenant_id: str
    ) -> list[OperationalCaseCandidate]:
        """Devuelve todos los OperationalCaseCandidate del tenant."""
        ...

    def list_case_candidates_for_reception(
        self, tenant_id: str, reception_id: str
    ) -> list[OperationalCaseCandidate]:
        """Devuelve OperationalCaseCandidate del tenant vinculados a una reception."""
        ...

    def list_case_candidates_by_primary_pathology(
        self, tenant_id: str, pathology_code: str
    ) -> list[OperationalCaseCandidate]:
        """Devuelve OperationalCaseCandidate del tenant con el primary_pathology_code dado."""
        ...

    # ------------------------------------------------------------------
    # OperationalCase
    # ------------------------------------------------------------------

    def save_case(self, record: OperationalCase) -> OperationalCase:
        """Persiste o actualiza un OperationalCase (upsert por tenant+id)."""
        ...

    def get_case(
        self, tenant_id: str, case_id: str
    ) -> OperationalCase | None:
        """Devuelve el OperationalCase del tenant, o None si no existe."""
        ...

    def list_cases(self, tenant_id: str) -> list[OperationalCase]:
        """Devuelve todos los OperationalCase del tenant."""
        ...

    def list_cases_for_reception(
        self, tenant_id: str, reception_id: str
    ) -> list[OperationalCase]:
        """Devuelve OperationalCase del tenant vinculados a una reception."""
        ...

    def list_cases_by_primary_pathology(
        self, tenant_id: str, pathology_code: str
    ) -> list[OperationalCase]:
        """Devuelve OperationalCase del tenant con el primary_pathology_code dado."""
        ...

    def list_cases_by_status(
        self, tenant_id: str, status: str
    ) -> list[OperationalCase]:
        """Devuelve OperationalCase del tenant con el status dado."""
        ...

    # ------------------------------------------------------------------
    # FindingRecord
    # ------------------------------------------------------------------

    def save_finding(self, record: FindingRecord) -> FindingRecord:
        """Persiste o actualiza un FindingRecord (upsert por tenant+id)."""
        ...

    def get_finding(
        self, tenant_id: str, finding_id: str
    ) -> FindingRecord | None:
        """Devuelve el FindingRecord del tenant, o None si no existe."""
        ...

    def list_findings(self, tenant_id: str) -> list[FindingRecord]:
        """Devuelve todos los FindingRecord del tenant."""
        ...

    def list_findings_for_case(
        self, tenant_id: str, case_id: str
    ) -> list[FindingRecord]:
        """Devuelve FindingRecord del tenant vinculados a un case_id."""
        ...

    def list_findings_by_status(
        self, tenant_id: str, status: str
    ) -> list[FindingRecord]:
        """Devuelve FindingRecord del tenant con el status dado."""
        ...

    def list_findings_by_severity(
        self, tenant_id: str, severity: str
    ) -> list[FindingRecord]:
        """Devuelve FindingRecord del tenant con la severity dada."""
        ...

    def list_findings_requiring_human_review(
        self, tenant_id: str
    ) -> list[FindingRecord]:
        """Devuelve FindingRecord del tenant donde human_review_required == True."""
        ...
