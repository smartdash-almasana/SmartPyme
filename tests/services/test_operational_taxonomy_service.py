import json
from pathlib import Path

import pytest

from app.services.operational_taxonomy_service import OperationalTaxonomyService


def test_operational_taxonomy_loads_default_catalog():
    service = OperationalTaxonomyService()

    assert service.catalog["catalog_id"] == "taxonomia_operativa_pyme_argentina_v0"
    assert service.catalog["version"] == "0.1"
    assert len(service.list_items()) >= 6
    assert "comercio" in service.list_families()


def test_operational_taxonomy_gets_item_questions_and_data():
    service = OperationalTaxonomyService()

    item = service.get_item("TAX_COM_001")

    assert item is not None
    assert item["tipo_operativo"] == "tienda_minorista_familiar"
    assert "¿Qué vendés principalmente?" in service.get_questions("TAX_COM_001")
    assert "ventas_mensuales" in service.get_minimum_data("TAX_COM_001")


def test_operational_taxonomy_lists_by_family():
    service = OperationalTaxonomyService()

    commerce_items = service.list_by_family("comercio")

    assert {item["id"] for item in commerce_items} >= {"TAX_COM_001", "TAX_COM_002"}
    assert service.list_by_family("familia_inexistente") == []


def test_operational_taxonomy_returns_empty_tuples_for_unknown_item():
    service = OperationalTaxonomyService()

    assert service.get_item("NO_EXISTE") is None
    assert service.get_questions("NO_EXISTE") == ()
    assert service.get_minimum_data("NO_EXISTE") == ()


def test_operational_taxonomy_rejects_invalid_intensity(tmp_path: Path):
    catalog_path = tmp_path / "invalid_taxonomy.json"
    catalog_path.write_text(
        json.dumps(
            {
                "catalog_id": "taxonomia_operativa_pyme_argentina_v0",
                "version": "0.1",
                "description": "invalid",
                "criteria": "invalid",
                "items": [
                    {
                        "id": "TAX_BAD",
                        "actividad_oficial_referencia": {
                            "fuente": "CLAE/ClaNAE",
                            "seccion": "Comercio",
                            "division_o_grupo": "Comercio",
                            "codigo_clae_aproximado": None,
                            "keywords_clae": ["x"],
                            "confianza_mapeo_oficial": "media",
                            "validacion_requerida": True,
                        },
                        "familia_smartpyme": "comercio",
                        "tipo_operativo": "bad",
                        "derivada_operativa": True,
                        "ejemplos_argentinos": ["x"],
                        "modelo_ingresos": "x",
                        "intensidad": {
                            "stock": "muy alta",
                            "personal": "baja",
                            "tiempo": "media",
                            "documentacion": "alta",
                        },
                        "senales_anamnesis": ["x"],
                        "preguntas_al_dueno": ["x"],
                        "datos_minimos_a_pedir": ["x"],
                        "patologias_probables": ["x"],
                        "formulas_utiles": ["x"],
                        "buenas_practicas_asociadas": ["x"],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="invalid values"):
        OperationalTaxonomyService(catalog_path)
