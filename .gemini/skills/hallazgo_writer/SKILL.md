# SKILL: hallazgo_writer

## NOMBRE DEL SKILL
hallazgo_writer

## PROPÓSITO
Consolidar de forma atómica y precisa todo el análisis de auditoría, clasificación y seguridad en el formato estándar de Hallazgo Operativo.

## CUÁNDO USARLO
- Como cierre de la fase de auditoría de cantera para un módulo.
- Cuando se tiene una propuesta de portado validada y lista para ejecución por otro agente.

## CUÁNDO NO USARLO
- Mientras existan dudas críticas no resueltas sobre la viabilidad de los slices.
- Si no se ha realizado la validación de seguridad de rutas.

## INPUT ESPERADO
- Output de `cantera_audit`, `slice_classifier`, `gap_detector` y `route_guard`.
- ID de hallazgo (si es provisto por el orquestador).

## OUTPUT ESPERADO
- Archivo Markdown completo siguiendo la estructura definida en `GEMINI.md`.

## REGLAS OBLIGATORIAS
1. Respetar el ID de hallazgo si viene definido por el flujo; en su defecto, dejar en blanco o usar placeholder neutral. No inventar convenciones de ID no autorizadas.
2. Listar únicamente los `TOP_SLICES` (los de clasificación A o B más críticos).
3. Incluir las `REGLAS_DE_EJECUCION` innegociables (no refactor, fail-closed, humano en loop).
4. Asegurar que la `PROPUESTA_DE_PORTADO` solo incluya rutas validadas por `route_guard`.
5. Mantener tono técnico, operativo y libre de teoría.

## CRITERIO DE BLOQUEO
- Si falta información obligatoria para completar alguna sección del template.
- Si existe una contradicción insalvable entre los inputs de los demás skills.

## EJEMPLO MÍNIMO DE USO
Input: Validated slice for `entities` and safe path.
Output: # HALLAZGO ... META ... OBJETIVO: Portar lógica de resolución de entidades ...

## RELACIÓN CON LOS DEMÁS SKILLS
Es el consumidor final de la cadena de skills. Depende de la coherencia de todos los pasos anteriores para generar un hallazgo de alta fidelidad.
