# SKILL: cantera_audit

## NOMBRE DEL SKILL
cantera_audit

## PROPÓSITO
Escanear repositorios de cantera autorizados para identificar funciones, modelos o clases que resuelvan la lógica requerida por el módulo objetivo en SmartPyme.

## CUÁNDO USARLO
- Al inicio de una nueva tarea de auditoría o portado.
- Cuando se requiere localizar lógica de referencia para un módulo específico.

## CUÁNDO NO USARLO
- Para realizar modificaciones en el código de SmartPyme.
- Para búsquedas genéricas de documentación o teoría.

## INPUT ESPERADO
- `modulo_objetivo`: Nombre del módulo en SmartPyme (ej: clarification).
- `canteras`: Lista de rutas raíz autorizadas definidas en GEMINI.md.

## OUTPUT ESPERADO
- Lista detallada de archivos y bloques de código (slices) candidatos con ubicación absoluta, tipo de objeto y resumen funcional.

## REGLAS OBLIGATORIAS
1. Solo buscar en las rutas raíz de cantera autorizadas.
2. Identificar explícitamente el tipo de objeto (clase, función, constante, modelo).
3. Resumir la lógica en términos operativos de negocio (ej: "Validador de CUIT determinístico").
4. No suponer la existencia de archivos no listados por las herramientas de búsqueda.

## CRITERIO DE BLOQUEO
- Si las rutas de cantera no son accesibles o el acceso es denegado.
- Si la lógica encontrada viola frontalmente la arquitectura canónica de SmartPyme.

## EJEMPLO MÍNIMO DE USO
Input: modulo_objetivo="clarification", cantera="E:\BuenosPasos\smartcounter"
Output: Found slice `save_clarifications` in `app/services/clarification_service.py` (Function: persists uncertainties to SQLite).

## RELACIÓN CON LOS DEMÁS SKILLS
Provee la materia prima (slices candidatos) para que `slice_classifier` los evalúe y `hallazgo_writer` los documente.
