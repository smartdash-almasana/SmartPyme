from pathlib import Path

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.dependencies import get_active_client
from app.repositories.entity_repository import EntityRepository

router = APIRouter()


class EntitiesDbPath(BaseModel):
    entities: str


async def get_entities_db_path() -> EntitiesDbPath:
    return EntitiesDbPath(entities="data/entities.db")


@router.get("/entities")
async def list_entities(
    entity_type: str | None = None,
    cliente_id: str = Depends(get_active_client),
    db_path: EntitiesDbPath = Depends(get_entities_db_path),
):
    repo = EntityRepository(cliente_id, Path(db_path.entities))
    entities = repo.list_entities(entity_type=entity_type)

    return {
        "cliente_id": cliente_id,
        "count": len(entities),
        "entities": [
            {
                "entity_id": entity.entity_id,
                "entity_type": entity.entity_type,
                "attributes": entity.attributes,
                "linked_canonical_rows": entity.linked_canonical_rows,
                "validation_status": entity.validation_status,
                "errors": entity.errors,
            }
            for entity in entities
        ],
    }
