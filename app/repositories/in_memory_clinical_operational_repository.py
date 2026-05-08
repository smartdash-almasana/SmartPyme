from __future__ import annotations

from app.contracts.clinical_operational_contracts import EvidenceRecord, ReceptionRecord


class InMemoryClinicalOperationalRepository:
    """Persistencia tactica in-memory para contratos clinico-operacionales base.

    Solo guarda y recupera ReceptionRecord y EvidenceRecord.
    No contiene logica clinica ni de decision.
    """

    def __init__(self) -> None:
        self._receptions: dict[tuple[str, str], ReceptionRecord] = {}
        self._evidence: dict[tuple[str, str], EvidenceRecord] = {}

    @staticmethod
    def _validate_tenant_id(tenant_id: str) -> str:
        if not tenant_id or not tenant_id.strip():
            raise ValueError("tenant_id no puede ser vacio")
        return tenant_id.strip()

    @staticmethod
    def _validate_reception_id(reception_id: str) -> str:
        if not reception_id or not reception_id.strip():
            raise ValueError("reception_id no puede ser vacio")
        return reception_id.strip()

    @staticmethod
    def _validate_evidence_id(evidence_id: str) -> str:
        if not evidence_id or not evidence_id.strip():
            raise ValueError("evidence_id no puede ser vacio")
        return evidence_id.strip()

    def save_reception(self, record: ReceptionRecord) -> ReceptionRecord:
        tenant_id = self._validate_tenant_id(record.tenant_id)
        key = (tenant_id, record.reception_id)
        self._receptions[key] = record
        return record

    def get_reception(self, tenant_id: str, reception_id: str) -> ReceptionRecord | None:
        valid_tenant_id = self._validate_tenant_id(tenant_id)
        valid_reception_id = self._validate_reception_id(reception_id)
        return self._receptions.get((valid_tenant_id, valid_reception_id))

    def list_receptions(self, tenant_id: str) -> list[ReceptionRecord]:
        valid_tenant_id = self._validate_tenant_id(tenant_id)
        return [
            record
            for (record_tenant_id, _), record in self._receptions.items()
            if record_tenant_id == valid_tenant_id
        ]

    def save_evidence(self, record: EvidenceRecord) -> EvidenceRecord:
        tenant_id = self._validate_tenant_id(record.tenant_id)
        key = (tenant_id, record.evidence_id)
        self._evidence[key] = record
        return record

    def get_evidence(self, tenant_id: str, evidence_id: str) -> EvidenceRecord | None:
        valid_tenant_id = self._validate_tenant_id(tenant_id)
        valid_evidence_id = self._validate_evidence_id(evidence_id)
        return self._evidence.get((valid_tenant_id, valid_evidence_id))

    def list_evidence(self, tenant_id: str) -> list[EvidenceRecord]:
        valid_tenant_id = self._validate_tenant_id(tenant_id)
        return [
            record
            for (record_tenant_id, _), record in self._evidence.items()
            if record_tenant_id == valid_tenant_id
        ]

    def list_evidence_for_reception(self, tenant_id: str, reception_id: str) -> list[EvidenceRecord]:
        valid_tenant_id = self._validate_tenant_id(tenant_id)
        valid_reception_id = self._validate_reception_id(reception_id)
        return [
            record
            for (record_tenant_id, _), record in self._evidence.items()
            if record_tenant_id == valid_tenant_id and record.linked_reception_id == valid_reception_id
        ]
