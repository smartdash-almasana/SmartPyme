# SKILL: slice_classifier

## NOMBRE DEL SKILL
slice_classifier

## PROPÓSITO
Evaluar la calidad, determinismo y compatibilidad de los slices encontrados en la cantera para determinar su estrategia de portado.

## CUÁNDO USARLO
- Después de que `cantera_audit` identifique piezas potenciales.
- Antes de consolidar el análisis en un Hallazgo.

## CUÁNDO NO USARLO
- Para analizar código interno de SmartPyme.
- Para proponer implementaciones nuevas desde cero.

## INPUT ESPERADO
- Lista de slices candidatos (código o referencia funcional).

## OUTPUT ESPERADO
- Clasificación A/B/C/D para cada slice con justificación técnica basada en arquitectura SmartPyme.

## REGLAS OBLIGATORIAS
1. **A (Adoptar):** Lógica pura, determinística, sin efectos secundarios, portable casi directo.
2. **B (Adaptar):** Lógica útil pero requiere ajuste de contratos, tipos o inyección de dependencias locales.
3. **C (Referencia):** Solo útil como guía conceptual; la implementación original es incompatible.
4. **D (Descartar):** Código con efectos secundarios, dependencias de terceros no autorizadas o lógica "fuzzy".
5. Priorizar el determinismo Python sobre cualquier otra métrica.

## CRITERIO DE BLOQUEO
- Si el slice depende de lógica propietaria de la cantera que no puede ser replicada o portada.
- Si el slice utiliza librerías prohibidas en el core (ej: pandas, frameworks pesados).

## EJEMPLO MÍNIMO DE USO
Input: Function `compute_similarity` using `SequenceMatcher`.
Output: Class A - Pure logic, uses standard library, fully compatible.

## RELACIÓN CON LOS DEMÁS SKILLS
Recibe el output de `cantera_audit` y entrega el ranking de calidad a `hallazgo_writer` y `gap_detector`.
