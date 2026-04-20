# SKILL: gap_detector

## NOMBRE DEL SKILL
gap_detector

## PROPÓSITO
Identificar inconsistencias críticas y riesgos de deriva entre la lógica encontrada en cantera y los requerimientos determinísticos de SmartPyme.

## CUÁNDO USARLO
- Al evaluar la viabilidad de un slice clasificado como A o B.
- Durante la preparación de las reglas de ejecución de un Hallazgo.

## CUÁNDO NO USARLO
- Para corregir código existente.
- Para diseñar nuevas arquitecturas sin base en cantera.

## INPUT ESPERADO
- Slices candidatos clasificados.
- Contratos de datos (Pydantic models, JSON Schema) actuales del módulo objetivo en SmartPyme.

## OUTPUT ESPERADO
- Lista de Gaps (campos faltantes, tipos incompatibles) y Riesgos Arquitectónicos (dependencias circulares, drift de estado).

## REGLAS OBLIGATORIAS
1. Detectar si el slice asume estados globales que no existen en SmartPyme.
2. Identificar si hay uso implícito de variables de entorno o configuraciones no portadas.
3. Evaluar el impacto de la ausencia de validación humana en flujos críticos portados.

## CRITERIO DE BLOQUEO
- Si el gap detectado requiere un rediseño estructural del core de SmartPyme.
- Si el riesgo arquitectónico compromete el principio de Fail-Closed.

## EJEMPLO MÍNIMO DE USO
Input: Porting `save_clarification` from SQLite bridge to SmartPyme Auditor core.
Output: Gap - `audit_trail` dependency uses different interface. Risk - Implicit tenant scoping missing in source.

## RELACIÓN CON LOS DEMÁS SKILLS
Enriquece el análisis de `slice_classifier` y provee las `DUDAS_DETECTADAS` a `hallazgo_writer`.
