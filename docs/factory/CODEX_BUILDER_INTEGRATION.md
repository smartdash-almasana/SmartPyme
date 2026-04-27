# Codex Builder Integration — SmartPyme Factory

## Objetivo

Integrar Codex como Builder formal dentro del loop de factoría SmartPyme sin convertirlo en autoridad arquitectónica.

## Modelo correcto

```text
ChatGPT director técnico externo
→ escribe/ajusta NEXT_CYCLE.md y contratos
→ Hermes lee el repo y orquesta
→ Codex ejecuta construcción o review acotado
→ tests/evidencia validan
→ Hermes registra resultado
```

## Rol de Codex

Codex es un Builder / Reviewer de código.

Puede:
- modificar archivos dentro del alcance de una tarea;
- proponer patches;
- correr comandos de verificación;
- ejecutar tests acotados;
- devolver diff, evidencia y bloqueo si falta contexto.

No puede:
- decidir roadmap;
- cambiar arquitectura canónica;
- tocar múltiples frentes en un ciclo;
- declarar éxito sin evidencia;
- inventar rutas, dependencias, APIs o contratos;
- usar memoria conversacional como estado.

## Contrato de entrada para Codex

Toda tarea enviada a Codex debe tener este formato mínimo:

```yaml
task_id: string
role: codex_builder
objective: string
allowed_files:
  - path
forbidden_files:
  - path
acceptance_criteria:
  - criterion
validation_commands:
  - command
evidence_required:
  - factory/evidence/<task_id>/cycle.md
  - factory/evidence/<task_id>/commands.txt
  - factory/evidence/<task_id>/git_diff.patch
  - factory/evidence/<task_id>/tests.txt
```

## Contrato de salida de Codex

```text
VEREDICTO
ARCHIVOS_MODIFICADOS
VERIFICACION_FISICA
TESTS
EVIDENCIA
DIFF
BLOQUEOS
RIESGOS
```

Estados válidos:

```text
CORRECTO
NO_VALIDADO
BLOCKED
INCOMPLETO
```

## Anti-alucinación

Codex debe bloquear si:

- no encuentra un archivo requerido;
- no existe contrato de entorno para ejecutar comandos;
- una dependencia no está declarada;
- el alcance exige tocar core sin autorización;
- no puede generar evidencia reproducible;
- el test no se puede ejecutar.

Mensaje obligatorio:

```text
BLOCKED: falta contexto verificable
```

## Modos de integración admitidos

### Fase 1 — Contrato por repo

Hermes crea o consume una tarea en `factory/control/NEXT_CYCLE.md` o `factory/tasks/` con formato compatible con Codex.

Codex trabaja sobre el repo usando su conexión GitHub/desktop y devuelve cambios por commit/PR.

### Fase 2 — MCP/CLI bridge

Crear herramientas controladas:

```text
codex_create_task
codex_run_review
codex_check_status
codex_fetch_result
```

Cada tool debe devolver:

```json
{
  "task_id": "...",
  "status": "CORRECTO|BLOCKED|NO_VALIDADO|INCOMPLETO",
  "evidence_path": "factory/evidence/...",
  "changed_files": [],
  "summary": "..."
}
```

### Fase 3 — Pool multiagente

Hermes asigna tareas a:

```text
Architect → Builder(Codex) → Auditor → Tests
```

Ningún agente valida su propio trabajo.

## Regla de cierre

Codex solo puede cerrar como `CORRECTO` si hay:

- archivos reales modificados;
- verificación física;
- test o bloqueo justificado;
- evidencia en `factory/evidence/<task_id>/`;
- diff revisable.

Sin eso:

```text
NO_VALIDADO
```

## Prioridad actual

Antes de usar Codex sobre features de negocio, debe cerrarse:

1. contrato de tareas Codex;
2. template de tarea;
3. mecanismo de evidencia;
4. integración con NEXT_CYCLE;
5. contrato de entorno Python;
6. Ruff/Pytest canónicos.
