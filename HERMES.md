# HERMES — Gobernanza Operativa SmartPyme

Este archivo es el contexto de proyecto prioritario para Hermes. Según la documentación oficial de Hermes Agent, `HERMES.md` / `.hermes.md` tiene prioridad sobre `AGENTS.md` como contexto de proyecto. Por eso este archivo contiene solo reglas operativas duras, no teoría.

## Ruta canónica de trabajo

La ruta operativa autorizada en VM es:

```text
/opt/smartpyme-factory/repos/SmartPyme
```

Antes de cualquier análisis o escritura, Hermes debe confirmar:

```bash
pwd
git branch --show-current
git rev-parse HEAD
git status --short
```

Si `pwd` no coincide con la ruta canónica, Hermes debe reportar `BLOCKED_WRONG_CWD` y no escribir.

## Modos obligatorios

### ANALYSIS_ONLY

Si el pedido indica analizar, inspeccionar, reportar alcance, listar archivos, mostrar plan, auditoría previa, no escribir todavía o equivalente:

- no escribir;
- no crear archivos;
- no borrar archivos;
- no mover archivos;
- no formatear código;
- solo lectura, búsqueda, baseline y reporte.

Veredicto obligatorio:

```text
VEREDICTO: ANALYSIS_ONLY
```

### WRITE_AUTHORIZED

Hermes solo puede escribir si la orden incluye autorización explícita de escritura, por ejemplo:

- autorizado a escribir;
- autorizado a implementar;
- aplicar cambio;
- modificar archivos;
- crear tests;
- implementar ahora.

Si no hay autorización explícita, el modo por defecto es `ANALYSIS_ONLY`.

### STOP_AND_REPORT

Si el Owner o GPT Auditor dice stop, pará, detener, no sigas, bloqueo, esperá, cortá, reporte o equivalente:

1. detener ejecución;
2. no escribir más;
3. reportar:

```bash
pwd
git branch --show-current
git rev-parse HEAD
git status --short
git diff --stat
git diff --name-only
```

Veredicto obligatorio:

```text
VEREDICTO: STOP_AND_REPORT
```

## Destrucción cero

Prohibido ejecutar operaciones destructivas sobre el repositorio salvo autorización textual expresa del Owner y alcance cerrado.

Prohibido por defecto:

- `rm`;
- `rm -rf`;
- `unlink`;
- `rmdir`;
- `find ... -delete`;
- sobrescribir archivos con contenido vacío;
- eliminar tests existentes;
- borrar evidencia.

Alternativas permitidas:

- `git checkout -- <archivo>` para revertir un archivo concreto;
- edición mínima y verificable;
- comentar o reemplazar lógica solo dentro del archivo autorizado.

## Alcance estricto

Hermes solo puede tocar rutas explícitamente autorizadas por la Task Spec.

Si detecta necesidad de tocar más archivos, refactor global, migración o cambio transversal:

```text
VEREDICTO: BLOCKED_SCOPE_EXPANSION
```

## Protocolo de cierre

Todo cambio autorizado debe seguir:

```text
WRITE -> VERIFY -> INSPECT -> TEST -> REPORT
```

No existe `PASS` válido sin:

- `git diff --stat`;
- lista de archivos modificados;
- verificación física del archivo;
- inspección del símbolo o rango relevante;
- test mínimo ejecutado y pasado, o bloqueo explícito si el entorno impide correrlo.

## Formato mínimo de reporte

```text
VEREDICTO: PASS | FAIL | BLOCKED | ANALYSIS_ONLY | STOP_AND_REPORT
PWD:
BRANCH:
HEAD:
SUMMARY_DIFF:
ARCHIVOS_MODIFICADOS:
VERIFICACION_FISICA:
TEST_COMMAND:
TEST_RESULT:
LIMITES:
NEXT_RECOMMENDED_STEP:
```

## Relación con otros archivos

- `AGENTS.md`: contrato general multiagente.
- `GEMINI.md`: reglas específicas de Gemini.
- `CODEX.md`: reglas específicas de Codex.
- `.gemini/skills/lean_audit_vm_protocol/SKILL.md`: skill operativo usado por Hermes/Gemini.

Ante conflicto, aplicar la regla más restrictiva.
