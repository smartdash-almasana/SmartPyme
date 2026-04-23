# Hallazgo Gatekeeper

## Propósito
Determinar si un hallazgo está listo para ejecución local en SmartPyme, con política fail-closed.

## Cuándo usarlo
- Antes de mover un hallazgo a `in_progress`.
- Antes de ejecutar un cambio de código basado en hallazgo.
- Cuando se necesita validar seguridad de rutas y consistencia mínima.

## Cuándo no usarlo
- Cuando el hallazgo ya está `done` y no requiere ejecución.
- Cuando no existe archivo de hallazgo.
- Cuando se está en tareas fuera de factory.

## Input esperado
- Archivo `.md` de hallazgo en `factory/hallazgos/pending`.
- Validación de secciones obligatorias del contrato.
- Revisión de `PREGUNTA_AL_OWNER`.
- Rutas listadas en `PROPUESTA_DE_PORTADO`.

## Output esperado
- Decisión binaria: listo o bloqueado.
- Motivo claro de bloqueo cuando no está listo.
- Estado de salida alineado (`blocked` o `in_progress`/`done`).

## Reglas obligatorias
- Fail-closed obligatorio.
- Bloquear si hay preguntas abiertas del owner.
- Bloquear si hay rutas `src\...` o rutas fuera de SmartPyme.
- Bloquear si hay deriva de alcance (rutas no autorizadas o ambiguas).
- Bloquear si la cantidad de archivos destino excede el límite definido por el runner.

## Criterio de bloqueo
- `PREGUNTA_AL_OWNER` no nula.
- Secciones críticas faltantes.
- Más archivos destino que los permitidos por política del runner.
- Rutas no autorizadas (`app/`, `tests/`, `factory/` son las únicas válidas).

## Ejemplo mínimo
```text
Entrada: hallazgo con ruta "src/reconciliation/service.py"
Salida esperada: blocked
Motivo: RUTA_SRC_BLOQUEADA
```
