import pytest
from app.catalogs.symptom_pathology_catalog import (
    get_symptom, list_symptoms, get_candidate_pathologies, 
    get_required_knowledge, get_research_questions
)

def test_symptom_structure():
    symptom = get_symptom("sospecha_perdida_margen")
    assert symptom["symptom_id"] == "sospecha_perdida_margen"
    assert "required_knowledge" in symptom
    assert "research_questions" in symptom

def test_list_symptoms():
    symptoms = list_symptoms()
    assert len(symptoms) == 5

def test_knowledge_and_research():
    knowledge = get_required_knowledge("sospecha_faltante_stock")
    assert "control_inventario" in knowledge
    questions = get_research_questions("sospecha_faltante_stock")
    assert len(questions) > 0
