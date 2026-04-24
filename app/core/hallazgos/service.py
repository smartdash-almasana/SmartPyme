import hashlib
from typing import Any, Optional, Dict
from dataclasses import replace
from app.core.hallazgos.models import (
    Hallazgo, 
    FindingSeverity, 
    FindingType, 
    FindingStatus,
    MismatchEvidence, 
    MissingEvidence
)
from app.core.reconciliation.models import ReconciliationResult, QuantifiedDiscrepancy
from app.core.repositories.hallazgo_repository import HallazgoRepository

class HallazgoEngine:
    """Motor endurecido para la generación de hallazgos determinísticos."""

    CRITICAL_THRESHOLD = 500.0

    @staticmethod
    def generate_dedupe_key(tipo: str, entidad_id: str, field_name: str = "") -> str:
        return f"{tipo}:{entidad_id}:{field_name}".strip(":")

    @staticmethod
    def generate_id(dedupe_key: str) -> str:
        return hashlib.sha256(dedupe_key.encode()).hexdigest()

    def get_mismatch_severity(self, delta: float | None) -> FindingSeverity:
        if delta is None:
            return "warning"
        return "critical" if abs(delta) >= self.CRITICAL_THRESHOLD else "warning"

    def transform(self, result: ReconciliationResult, entidad_tipo: str = "order") -> list[Hallazgo]:
        hallazgos = []

        for mismatch in result.mismatches:
            dedupe_key = self.generate_dedupe_key("mismatch", mismatch.key, mismatch.field_name)
            evidence: MismatchEvidence = {
                "field": mismatch.field_name,
                "value_a": mismatch.value_a,
                "value_b": mismatch.value_b,
                "delta": mismatch.delta
            }
            hallazgos.append(Hallazgo(
                id=self.generate_id(dedupe_key),
                tipo="mismatch_valor",
                severidad=self.get_mismatch_severity(mismatch.delta),
                entidad_id=mismatch.key,
                entidad_tipo=entidad_tipo,
                diferencia_cuantificada=mismatch.delta,
                evidencia=evidence,
                dedupe_key=dedupe_key
            ))

        for missing in result.missing_in_a:
            entity_id = str(missing.root.get("id", "unknown"))
            dedupe_key = self.generate_dedupe_key("missing_a", entity_id)
            evidence: MissingEvidence = {"missing_in": "source_a", "data": missing.root}
            hallazgos.append(Hallazgo(
                id=self.generate_id(dedupe_key),
                tipo="faltante_en_fuente",
                severidad="critical",
                entidad_id=entity_id,
                entidad_tipo=entidad_tipo,
                diferencia_cuantificada="missing_a",
                evidencia=evidence,
                dedupe_key=dedupe_key
            ))

        for missing in result.missing_in_b:
            entity_id = str(missing.root.get("id", "unknown"))
            dedupe_key = self.generate_dedupe_key("missing_b", entity_id)
            evidence: MissingEvidence = {"missing_in": "source_b", "data": missing.root}
            hallazgos.append(Hallazgo(
                id=self.generate_id(dedupe_key),
                tipo="faltante_en_fuente",
                severidad="critical",
                entidad_id=entity_id,
                entidad_tipo=entidad_tipo,
                diferencia_cuantificada="missing_b",
                evidencia=evidence,
                dedupe_key=dedupe_key
            ))

        return self.deduplicate(hallazgos)

    def deduplicate(self, hallazgos: list[Hallazgo]) -> list[Hallazgo]:
        unique = {}
        for h in hallazgos:
            unique[h.dedupe_key] = h
        return list(unique.values())

class HallazgoService:
    """Servicio de lectura y gestión de ciclo de vida de hallazgos."""

    def __init__(self, repository: HallazgoRepository):
        self.repository = repository

    def get_findings(
        self, 
        status: Optional[FindingStatus] = None,
        severity: Optional[FindingSeverity] = None,
        tipo: Optional[FindingType] = None
    ) -> list[Hallazgo]:
        """Consulta hallazgos con filtros determinísticos."""
        return self.repository.list_all(status=status, severity=severity, tipo=tipo)

    def get_summary(self) -> Dict[str, Any]:
        """Genera un resumen estadístico de los hallazgos persistidos."""
        all_findings = self.repository.list_all()
        
        summary = {
            "total": len(all_findings),
            "by_status": {s: 0 for s in ["pending", "in_progress", "done", "blocked"]},
            "by_severity": {sev: 0 for s, sev in [("", "info"), ("", "warning"), ("", "critical")]},
            "critical_pending": 0
        }
        
        for h in all_findings:
            summary["by_status"][h.status] += 1
            summary["by_severity"][h.severidad] += 1
            if h.severidad == "critical" and h.status == "pending":
                summary["critical_pending"] += 1
                
        return summary

    def update_status(self, hallazgo_id: str, new_status: FindingStatus) -> Optional[Hallazgo]:
        """Actualiza el estado de un hallazgo existente."""
        hallazgo = self.repository.get_by_id(hallazgo_id)
        if not hallazgo:
            return None
            
        updated = replace(hallazgo, status=new_status)
        self.repository.save(updated)
        return updated
