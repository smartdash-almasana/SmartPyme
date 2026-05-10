import sys
import unittest
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# google-genai es una dependencia opcional. Si no está instalada (VM sin GPU,
# entorno CI mínimo), se skipea todo el archivo sin romper la colección.
gsa = pytest.importorskip(
    "factory.gemini_slice_auditor",
    reason="factory.gemini_slice_auditor requiere google-genai (dependencia opcional)",
)


class GeminiSliceAuditorTests(unittest.TestCase):
    def test_normalizes_owner_question_to_null_when_proposal_is_executable(self) -> None:
        source = """# HALLAZGO

## META
- id: t1
- estado: pending
- modulo_objetivo: reconciliation

## OBJETIVO
objetivo

## PROPUESTA_DE_PORTADO
### Crear o modificar solo:
- app\\core\\reconciliation\\service.py
- tests\\core\\test_reconciliation_service.py

## PREGUNTA_AL_OWNER
- ¿Cómo se integra action_jobs?
"""
        normalized = gsa._normalize_owner_question_when_not_blocked(source)
        self.assertIn("## PREGUNTA_AL_OWNER\n- null", normalized)
        self.assertNotIn("¿Cómo se integra action_jobs?", normalized)

    def test_keeps_owner_question_when_proposal_is_not_executable(self) -> None:
        source = """# HALLAZGO

## META
- id: t2
- estado: pending
- modulo_objetivo: reconciliation

## OBJETIVO
objetivo

## PROPUESTA_DE_PORTADO
### Crear o modificar solo:
- null

## PREGUNTA_AL_OWNER
- ¿Falta definir integración?
"""
        normalized = gsa._normalize_owner_question_when_not_blocked(source)
        self.assertIn("¿Falta definir integración?", normalized)

    def test_normalizes_propuesta_de_portado_to_allowed_roots_only(self) -> None:
        source = """# HALLAZGO

## META
- id: t3
- estado: pending
- modulo_objetivo: reconciliation

## OBJETIVO
objetivo

## PROPUESTA_DE_PORTADO
### Crear o modificar solo:
- Adoptar `WarningItem` de `backend\\schemas.py` y renombrarlo a `ReconciliationIssue`.
- backend\\schemas.py
- app\\core\\reconciliation\\service.py
- tests\\core\\test_reconciliation_service.py

## PREGUNTA_AL_OWNER
- null
"""
        normalized = gsa._normalize_propuesta_de_portado(source, "reconciliation")
        self.assertIn("- app/core/reconciliation/service.py", normalized)
        self.assertIn("- tests/core/test_reconciliation_service.py", normalized)
        self.assertNotIn("backend\\schemas.py", normalized)
        self.assertNotIn("Adoptar `WarningItem`", normalized)

    def test_fallbacks_to_module_allowed_targets_when_no_valid_destination_remains(self) -> None:
        source = """# HALLAZGO

## META
- id: t4
- estado: pending
- modulo_objetivo: reconciliation

## OBJETIVO
objetivo

## PROPUESTA_DE_PORTADO
### Crear o modificar solo:
- Adoptar X de backend\\schemas.py y renombrarlo a Z
- backend\\schemas.py

## PREGUNTA_AL_OWNER
- null
"""
        normalized = gsa._normalize_propuesta_de_portado(source, "reconciliation")
        self.assertIn("- app/core/reconciliation/models.py", normalized)
        self.assertIn("- app/core/reconciliation/service.py", normalized)
        self.assertNotIn("backend\\schemas.py", normalized)

    def test_removes_parenthetical_suffix_from_destination_paths(self) -> None:
        source = """# HALLAZGO

## META
- id: t5
- estado: pending
- modulo_objetivo: validation

## OBJETIVO
objetivo

## PROPUESTA_DE_PORTADO
### Crear o modificar solo:
- app/core/validation/service.py (basado en backend/validators.py)
- tests/core/test_validation_service.py (ajustar casos)

## PREGUNTA_AL_OWNER
- null
"""
        normalized = gsa._normalize_propuesta_de_portado(source, "validation")
        self.assertIn("- app/core/validation/service.py", normalized)
        self.assertIn("- tests/core/test_validation_service.py", normalized)
        self.assertNotIn("(basado en", normalized)
        self.assertNotIn("(ajustar casos)", normalized)

    def test_extracts_clean_path_when_line_has_inline_explanation(self) -> None:
        source = """# HALLAZGO

## META
- id: t6
- estado: pending
- modulo_objetivo: reconciliation

## OBJETIVO
objetivo

## PROPUESTA_DE_PORTADO
### Crear o modificar solo:
- Adoptar lógica de backend/schemas.py en app/core/reconciliation/service.py con cambios mínimos

## PREGUNTA_AL_OWNER
- null
"""
        normalized = gsa._normalize_propuesta_de_portado(source, "reconciliation")
        self.assertIn("- app/core/reconciliation/service.py", normalized)
        self.assertNotIn("backend/schemas.py", normalized)
        self.assertNotIn("Adoptar lógica", normalized)


if __name__ == "__main__":
    unittest.main()
