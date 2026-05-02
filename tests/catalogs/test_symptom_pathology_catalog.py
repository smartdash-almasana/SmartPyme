import pytest
from app.catalogs.symptom_pathology_catalog import (
    get_symptom, get_candidate_pathologies, get_candidate_skills,
    get_required_variables, get_required_evidence, get_mayeutic_questions
)

def test_get_symptom():
    symptom = get_symptom("sospecha_perdida_margen")
    assert symptom is not None
    assert symptom["id"] == "sospecha_perdida_margen"

def test_get_candidate_pathologies():
    pathologies = get_candidate_pathologies("sospecha_perdida_margen")
    assert len(pathologies) > 0
    assert "erosión_tarifaria" in pathologies

def test_get_candidate_skills():
    skills = get_candidate_skills("sospecha_faltante_stock")
    assert "conciliacion_inventario" in skills

def test_get_required_variables():
    vars = get_required_variables("descuadre_caja_banco")
    assert "saldo_contable" in vars

def test_get_required_evidence():
    evidence = get_required_evidence("exceso_trabajo_manual")
    assert "matriz_tiempos" in evidence

def test_get_mayeutic_questions():
    questions = get_mayeutic_questions("incertidumbre_costo_produccion")
    assert len(questions) > 0
