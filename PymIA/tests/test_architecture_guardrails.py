import os
from pathlib import Path

def test_architecture_guardrails_sections():
    """
    Verifica que ARCHITECTURE_GUARDRAILS.md contenga las secciones obligatorias.
    """
    repo_root = Path(__file__).parent.parent
    guardrails_path = repo_root / "ARCHITECTURE_GUARDRAILS.md"
    
    assert guardrails_path.exists(), f"El archivo {guardrails_path} no existe"
    
    with open(guardrails_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    required_sections = [
        "1. SOURCE_OF_TRUTH_HIERARCHY",
        "2. PROHIBICIONES ABSOLUTAS",
        "3. HERMES_BOUNDARY",
        "4. DOCUMENTATION_POLICY",
        "5. TEST_POLICY",
        "6. ACCEPTANCE_CRITERIA"
    ]
    
    for section in required_sections:
        assert section in content, f"Falta la sección obligatoria: {section}"
