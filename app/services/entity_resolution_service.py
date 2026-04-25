from __future__ import annotations

import hashlib
from typing import Any

from app.contracts.evidence_contract import CanonicalRowCandidate
from app.contracts.entity_contract import Entity
from app.repositories.entity_repository import EntityRepository


class EntityResolutionService:
    def __init__(self, repository: EntityRepository) -> None:
        self.repository = repository

    def resolve_entities(
        self, canonical_rows: list[CanonicalRowCandidate], job_id: str | None = None, plan_id: str | None = None
    ) -> dict[str, Any]:
        
        entities = self._resolve_rows(canonical_rows, job_id=job_id, plan_id=plan_id)
        self.repository.save_batch(entities)
        return {
            "status": "RESOLVED",
            "job_id": job_id,
            "plan_id": plan_id,
            "entities_count": len(entities),
            "entity_ids": [entity.entity_id for entity in entities],
        }

    def _resolve_rows(
        self, canonical_rows: list[CanonicalRowCandidate], job_id: str | None = None, plan_id: str | None = None
    ) -> list[Entity]:
        entities = []
        for row in canonical_rows:
            # This is a very basic resolution logic. It will create a new entity for each canonical row.
            # A more advanced implementation would try to find existing entities and merge them.
            
            entity_type = row.entity_type
            attributes = row.row
            
            # Try to find an existing entity with the same attributes.
            # This is a simplification. A real implementation would have more complex matching logic.
            existing_entity = self.repository.find_by_attribute(entity_type, 'value', attributes.get('value'))
            
            if existing_entity:
                # If an entity with the same attribute value exists, we link the new canonical row to it.
                # This is a very basic form of entity resolution.
                updated_attributes = existing_entity.attributes.copy()
                updated_attributes.update(attributes)

                # Preserve "validated" status — a human decision must not be degraded.
                preserved_status = (
                    existing_entity.validation_status
                    if existing_entity.validation_status == "validated"
                    else "pending_validation"
                )

                # Deduplicate linked canonical rows.
                existing_rows = list(existing_entity.linked_canonical_rows)
                if row.canonical_row_id not in existing_rows:
                    existing_rows.append(row.canonical_row_id)

                updated_entity = Entity(
                    entity_id=existing_entity.entity_id,
                    entity_type=existing_entity.entity_type,
                    attributes=updated_attributes,
                    linked_canonical_rows=existing_rows,
                    validation_status=preserved_status,
                )
                entities.append(updated_entity)
            else:
                # If no existing entity is found, create a new one.
                entity_id = _build_entity_id(row.canonical_row_id, entity_type)
                new_entity = Entity(
                    entity_id=entity_id,
                    entity_type=entity_type,
                    attributes=attributes,
                    linked_canonical_rows=[row.canonical_row_id],
                    validation_status='pending_validation'
                )
                entities.append(new_entity)

        return entities


def _build_entity_id(canonical_row_id: str, entity_type: str) -> str:
    digest = hashlib.sha256(f"{canonical_row_id}:{entity_type}".encode()).hexdigest()
    return f"entity_{digest[:16]}"
