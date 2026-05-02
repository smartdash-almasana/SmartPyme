import pytest
from app.catalogs.symptom_pathology_catalog import (
    SYMPTOM_PATHOLOGY_CATALOG,
    SymptomEntry,
    list_symptoms,
    get_symptom,
    require_symptom,
    get_candidate_pathologies,
    get_candidate_skills,
    get_required_variables,
    get_required_evidence,
    get_mayeutic_questions,
)

def test_list_symptoms_returns_five_ids():
    symptoms = list_symptoms()
    assert isinstance(symptoms, tuple)
    assert len(symptoms) == 5
    expected_ids = (
        "sospecha_perdida_margen",
        "sospecha_faltante_stock",
        "descuadre_caja_banco",
        "exceso_trabajo_manual",
        "incertidumbre_costo_produccion",
    )
    assert set(symptoms) == set(expected_ids)

def test_get_symptom_with_known_id_returns_correct_entry():
    symptom_id = "sospecha_perdida_margen"
    entry = get_symptom(symptom_id)
    assert isinstance(entry, SymptomEntry)
    assert entry.symptom_id == symptom_id

def test_get_symptom_with_unknown_id_returns_none():
    symptom_id = "unknown_symptom"
    entry = get_symptom(symptom_id)
    assert entry is None

def test_require_symptom_with_unknown_id_raises_keyerror():
    symptom_id = "unknown_symptom"
    with pytest.raises(KeyError, match=f"Symptom ID '{symptom_id}' not found in catalog."):
        require_symptom(symptom_id)

def test_skills_specific_mappings():
    # 5. Skills específicas:
    assert get_candidate_skills("sospecha_perdida_margen") == ("skill_margin_leak_audit",)
    assert get_candidate_skills("sospecha_faltante_stock") == ("skill_stock_loss_detect",)
    assert get_candidate_skills("descuadre_caja_banco") == ("skill_reconcile_bank_vs_pos",)
    assert get_candidate_skills("exceso_trabajo_manual") == ("skill_process_automation_audit",)
    assert get_candidate_skills("incertidumbre_costo_produccion") == ("skill_bom_cost_audit",)

def test_evidence_required_contains_expected_elements():
    # 6. Evidencia requerida contiene elementos esperados:
    assert any(item in get_required_evidence("sospecha_perdida_margen") for item in ("facturas_proveedor", "lista_costos"))
    assert any(item in get_required_evidence("descuadre_caja_banco") for item in ("extracto_bancario", "reporte_pos"))
    assert "inventario_fisico" in get_required_evidence("sospecha_faltante_stock")
    assert any(item in get_required_evidence("exceso_trabajo_manual") for item in ("descripcion_flujo", "archivos_excel"))
    assert any(item in get_required_evidence("incertidumbre_costo_produccion") for item in ("receta_o_BOM", "lista_costos"))

def test_hypotheses_do_not_start_with_hay():
    # 7. Ninguna hipótesis empieza con "Hay ".
    for symptom_id in list_symptoms():
        entry = get_symptom(symptom_id)
        assert not entry.hipotesis_template.startswith("Hay "), f"Hypothesis for {symptom_id} starts with 'Hay '"

def test_hypotheses_contain_investigar():
    # 8. Todas las hipótesis contienen "Investigar".
    for symptom_id in list_symptoms():
        entry = get_symptom(symptom_id)
        assert "Investigar" in entry.hipotesis_template, f"Hypothesis for {symptom_id} does not contain 'Investigar'"

def test_all_entries_have_non_empty_mayeutic_questions():
    # 9. Todas las entradas tienen preguntas mayéuticas no vacías.
    for symptom_id in list_symptoms():
        questions = get_mayeutic_questions(symptom_id)
        assert isinstance(questions, tuple)
        assert len(questions) > 0, f"Symptom {symptom_id} has empty mayeutic questions"
        assert len(questions) >= 4, f"Symptom {symptom_id} has less than 4 mayeutic questions"


def test_results_of_lists_are_tuples():
    # 10. Resultados de listas son tuplas.
    symptom_id = "sospecha_perdida_margen"
    assert isinstance(list_symptoms(), tuple)
    assert isinstance(get_candidate_pathologies(symptom_id), tuple)
    assert isinstance(get_candidate_skills(symptom_id), tuple)
    assert isinstance(get_required_variables(symptom_id), tuple)
    assert isinstance(get_required_evidence(symptom_id), tuple)
    assert isinstance(get_mayeutic_questions(symptom_id), tuple)

def test_functions_do_not_mutate_catalog():
    # 11. Las funciones no mutan SYMPTOM_PATHOLOGY_CATALOG.
    original_catalog_len = len(SYMPTOM_PATHOLOGY_CATALOG)
    list_symptoms()
    get_symptom("sospecha_perdida_margen")
    get_candidate_pathologies("sospecha_perdida_margen")
    assert len(SYMPTOM_PATHOLOGY_CATALOG) == original_catalog_len

def test_get_list_functions_return_empty_tuple_for_unknown_id():
    # 12. Las funciones get_* para ID desconocido devuelven ().
    unknown_id = "non_existent_id"
    assert get_candidate_pathologies(unknown_id) == ()
    assert get_candidate_skills(unknown_id) == ()
    assert get_required_variables(unknown_id) == ()
    assert get_required_evidence(unknown_id) == ()
    assert get_mayeutic_questions(unknown_id) == ()

from app.catalogs.symptom_pathology_catalog import match_symptom_from_dolores

def test_match_symptom_from_dolores_specific_matches():
    assert match_symptom_from_dolores(("pierdo plata",)) == "sospecha_perdida_margen"
    assert match_symptom_from_dolores(("no sé si me falta stock",)) == "sospecha_faltante_stock"
    assert match_symptom_from_dolores(("no me cierra la caja",)) == "descuadre_caja_banco"
    assert match_symptom_from_dolores(("trabajo demasiado manual",)) == "exceso_trabajo_manual"
    assert match_symptom_from_dolores(("no sé cuánto me cuesta fabricar",)) == "incertidumbre_costo_produccion"

def test_match_symptom_from_dolores_no_match():
    assert match_symptom_from_dolores(("dolor inexistente",)) is None
    assert match_symptom_from_dolores(("otro dolor cualquiera", "nada que ver")) is None

def test_match_symptom_from_dolores_tolerance_case_and_spaces():
    assert match_symptom_from_dolores(("  PIERDO plata  ",)) == "sospecha_perdida_margen"
    assert match_symptom_from_dolores(("  NO sé SI me FALTA stock ",)) == "sospecha_faltante_stock"

def test_match_symptom_from_dolores_respects_catalog_order():
    # Adding a dolor that exists in multiple symptoms, but
    # 'sospecha_perdida_margen' appears first in the catalog for "no sé" related phrases
    assert match_symptom_from_dolores(("no sé",)) == "sospecha_perdida_margen"

def test_match_symptom_from_dolores_multiple_input_dolores():
    assert match_symptom_from_dolores(("dolor inexistente", "pierdo plata")) == "sospecha_perdida_margen"
    assert match_symptom_from_dolores(("no me cierra la caja", "no sé si me falta stock")) == "sospecha_faltante_stock"
