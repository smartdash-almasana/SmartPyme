from app.core.pipeline import Pipeline
from app.repositories.entity_repository import EntityRepository
from app.repositories.fact_repository import FactRepository
from app.repositories.canonical_repository import CanonicalRepository


def test_pipeline_propagates_cliente_id(tmp_path):
    db = tmp_path / "entities.db"

    cliente_id = "pyme_x"

    pipeline = Pipeline(
        cliente_id,
        FactRepository(tmp_path / "facts.db"),
        CanonicalRepository(tmp_path / "canonical.db"),
        EntityRepository(cliente_id, db),
    )

    result = pipeline.process_texts(
        "ev1", "Factura 1 $100",
        "ev2", "Factura 1 $200",
    )

    assert result.cliente_id == cliente_id
