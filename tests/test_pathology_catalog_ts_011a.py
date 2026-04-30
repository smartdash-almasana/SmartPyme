from app.catalog.pathologies import (
    PATHOLOGY_CATALOG,
    get_pathology_definition,
    get_pathology_metadata,
    list_pathology_definitions,
)
from app.contracts.pathology_contract import PathologyDefinition, PathologySeverity


def test_catalog_contains_baseline_pathology():
    definition = get_pathology_definition("margen_bruto_negativo")

    assert definition is not None
    assert definition.formula_id == "margen_bruto"
    assert definition.severity == PathologySeverity.HIGH


def test_catalog_definitions_are_typed():
    definitions = list_pathology_definitions()

    assert definitions
    assert all(isinstance(definition, PathologyDefinition) for definition in definitions)


def test_catalog_ids_match_keys():
    for pathology_id, definition in PATHOLOGY_CATALOG.items():
        assert definition.pathology_id == pathology_id
        assert definition.formula_id
        assert definition.description
        assert definition.suggested_action
        assert definition.severity in PathologySeverity


def test_catalog_has_metadata_for_each_pathology():
    for pathology_id in PATHOLOGY_CATALOG:
        metadata = get_pathology_metadata(pathology_id)
        assert metadata["category"]
        assert "impact_capital_time" in metadata
        assert "requires_formula" in metadata


def test_catalog_includes_industrial_candidates():
    expected = {
        "trampa_producto_ads_negativo",
        "venta_bajo_costo",
        "falla_precision_int64",
        "limbo_liquidaciones_ml",
        "clasificacion_iva_lesiva",
    }

    assert expected.issubset(set(PATHOLOGY_CATALOG))
