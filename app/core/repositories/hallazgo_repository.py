from typing import Protocol, runtime_checkable

from app.core.hallazgos.models import FindingSeverity, FindingStatus, FindingType, Hallazgo


@runtime_checkable
class HallazgoRepository(Protocol):
    """Interfaz determinística para la persistencia y consulta de hallazgos."""
    
    def save(self, hallazgo: Hallazgo) -> None:
        """Guarda o actualiza un hallazgo."""
        ...

    def get_by_id(self, hallazgo_id: str) -> Hallazgo | None:
        """Busca un hallazgo por su ID único."""
        ...

    def get_by_dedupe_key(self, dedupe_key: str) -> Hallazgo | None:
        """Busca un hallazgo por su clave de deduplicación."""
        ...

    def list_all(
        self, 
        status: FindingStatus | None = None,
        severity: FindingSeverity | None = None,
        tipo: FindingType | None = None
    ) -> list[Hallazgo]:
        """Lista hallazgos aplicando filtros opcionales."""
        ...

class MemoryHallazgoRepository:
    """Implementación en memoria con soporte de filtrado."""

    def __init__(self):
        self._storage: dict[str, Hallazgo] = {}
        self._dedupe_index: dict[str, str] = {}

    def save(self, hallazgo: Hallazgo) -> None:
        self._storage[hallazgo.id] = hallazgo
        self._dedupe_index[hallazgo.dedupe_key] = hallazgo.id

    def get_by_id(self, hallazgo_id: str) -> Hallazgo | None:
        return self._storage.get(hallazgo_id)

    def get_by_dedupe_key(self, dedupe_key: str) -> Hallazgo | None:
        hallazgo_id = self._dedupe_index.get(dedupe_key)
        if not hallazgo_id:
            return None
        return self._storage.get(hallazgo_id)

    def list_all(
        self, 
        status: FindingStatus | None = None,
        severity: FindingSeverity | None = None,
        tipo: FindingType | None = None
    ) -> list[Hallazgo]:
        findings = list(self._storage.values())
        
        if status:
            findings = [h for h in findings if h.status == status]
        if severity:
            findings = [h for h in findings if h.severidad == severity]
        if tipo:
            findings = [h for h in findings if h.tipo == tipo]
            
        return findings
