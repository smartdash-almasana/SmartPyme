---
name: hallazgo_executor
description: Ejecuta hallazgos validados con control fail-closed y cierre de estado en la factoria SmartPyme.
---

# Hallazgo Executor

## Propósito
Ejecutar hallazgos escritos por Gemini sobre el repositorio objetivo, con control fail-closed y validación mínima obligatoria.

## Repo objetivo
E:\BuenosPasos\smartbridge\SmartPyme

## Entrada
Un único archivo markdown tomado desde:
- E:\BuenosPasos\smartbridge\SmartPyme\factory\hallazgos\pending

## Flujo operativo
1. Leer exactamente un hallazgo desde `pending`.
2. Validar que el hallazgo contenga:
   - `modulo_objetivo`
   - `rutas_fuente`
   - `top_slices`
   - `propuesta_de_portado`
   - `reglas_de_ejecucion`
   - `criterio_de_cierre`
3. Si falta alguno de los campos requeridos, no ejecutar cambios: completar `BLOQUEO` y mover a `blocked`.
4. Si está completo, mover el hallazgo a `in_progress` antes de actuar.
5. Aplicar solo cambios mínimos en SmartPyme, estrictamente dentro del alcance declarado.
6. Correr solo tests necesarios del módulo afectado.
7. Si todo sale bien:
   - completar `EJECUCION_CODEX`
   - mover hallazgo a `done`
8. Si aparece duda, conflicto o falta de contexto:
   - NO continuar
   - completar `BLOQUEO`
   - mover hallazgo a `blocked`

## Restricciones duras
- no explorar cantera por cuenta propia
- no buscar nuevos slices por cuenta propia
- no modificar módulos fuera del alcance del hallazgo
- no hacer refactor global
- no inventar contratos, rutas o dependencias
- no cerrar un hallazgo sin verificación mínima
- preguntar antes que asumir
