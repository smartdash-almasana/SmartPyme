## Automatización de Calidad (Lifecycle)

Cada TaskSpec ejecutada por esta skill debe garantizar el cumplimiento de los estándares de código de SmartPyme:

1. TESTS_RUN: Toda ejecución debe concluir con un suite de pruebas (pytest) sobre los archivos tocados.
2. RUFF_RUN: Se debe aplicar `ruff check` sobre los archivos modificados.
3. El resultado del análisis de código debe persistirse en `factory/evidence/<task_id>/ruff.txt`.
4. REGLA: Ninguna TaskSpec Python puede ser cerrada sin haber pasado pytest y ruff check.
5. REGLA: `ruff --fix` solo debe ejecutarse si la TaskSpec contiene la autorización expresa.

remediation: P0-2 — TaskSpec YAML reemplaza hallazgos markdown como cola operativa
platforms: [linux]
metadata:
  hermes:
    category: devops
    tags: [smartpyme, factory, multiagent, governance, taskspec, hermes]
---

# Hermes SmartPyme Factory

## Estado de este skill

Este skill queda subordinado a:

```text
docs/factory/FACTORY_CONTRATO_OPERATIVO.md
factory/ai_governance/taskspec.schema.json
```

La unidad de trabajo vigente de SmartPyme Factory es **TaskSpec YAML** en:

```text
factory/ai_governance/tasks/<task_id>.yaml
```

Los hallazgos markdown en `factory/hallazgos/**` quedan como **legacy / cantera / insumo historico**. No son cola operativa vigente.

## Activador operativo

El comando owner vigente es:

```text
/avanzar
```

Hermes Gateway debe intentar un solo ciclo sobre una unica TaskSpec `pending`, respetando repo, gate, alcance permitido, evidencia y auditoria.

## Modelo

- Hermes Gateway = orquestador operativo externo.
- SmartPyme repo = fuente de verdad versionada.
- TaskSpec YAML = unidad de trabajo vigente.
- Evidencia = condicion de cierre.
- GPT Director-Auditor = autoridad externa ante bloqueo, auditoria o decision arquitectonica.

## Workspace valido

Hermes solo puede operar sobre:

```text
/home/neoalmasana/smartpyme-factory/repos/SmartPyme
/opt/smartpyme-factory/repos/SmartPyme
```

Precheck obligatorio:

```bash
pwd
git remote -v
git status --short
git log --oneline -1
```

Si el workspace o el remote no coinciden con `smartdash-almasana/SmartPyme`, debe responder `BLOCKED_WRONG_WORKSPACE`.

## Unidad de trabajo vigente

Cada TaskSpec debe validar contra:

```text
factory/ai_governance/taskspec.schema.json
```

Campos minimos vigentes:

```yaml
task_id: string
mode: create_only | patch_only | governance | product
status: pending | in_progress | submitted | blocked | validated | rejected
human_required: boolean
objective: string
allowed_files: []
forbidden_files: []
required_tests: []
acceptance_criteria: []
preflight_commands: []
post_commands: []
```

Mientras el schema mantenga `additionalProperties: false`, no se deben introducir campos adicionales.

## Hallazgos markdown legacy / cantera

Directorios legacy:

```text
factory/hallazgos/pending
factory/hallazgos/in_progress
factory/hallazgos/done
factory/hallazgos/blocked
```

Uso permitido:

- cantera documental;
- insumo historico;
- material para convertir manualmente a TaskSpec YAML;
- referencia de auditoria legacy.

Uso prohibido:

- seleccionar un hallazgo markdown como unidad ejecutable;
- mover estados de `factory/hallazgos/**` como runtime vigente;
- declarar un ciclo cerrado sin TaskSpec YAML y evidencia asociada.

## Ciclo minimo

1. `git pull --ff-only origin main`.
2. Leer canonicos: `GPT.md`, `AGENTS.md`, `docs/factory/FACTORY_CONTRATO_OPERATIVO.md`.
3. Revisar gate en `factory/control/`.
4. Seleccionar una sola TaskSpec `pending`.
5. Validar schema, `allowed_files`, `forbidden_files`, tests y criterios.
6. Delegar Builder con alcance permitido.
7. Exigir evidencia reproducible.
8. Delegar Auditor separado.
9. Dejar evidencia en `factory/evidence/<task_id>/`.
10. Pasar a gate de auditoria externa o decision humana.

## Evidencia obligatoria

Minimo aceptable por TaskSpec:

```text
factory/evidence/<task_id>/cycle.md
factory/evidence/<task_id>/commands.txt
factory/evidence/<task_id>/git_status.txt
factory/evidence/<task_id>/git_diff.patch
factory/evidence/<task_id>/tests.txt
factory/evidence/<task_id>/decision.txt
```

Sin evidencia verificable, el ciclo queda `BLOCKED` o `NEEDS_REVIEW` segun la capa que emite el veredicto.

## Reglas duras

- Builder no audita.
- Auditor no corrige.
- Hermes no valida su propio trabajo.
- No tocar `app/**`, `core/**`, `services/**` o tests sin TaskSpec explicita.
- No inventar archivos, datos ni estado.
- Usar `cliente_id`; `tenant_id` es bug documental o tecnico.
- Bridge MCP SmartPyme: stdio, no HTTP.
- No activar infraestructura antes de tests, dry-run y gate validos.

## Salida final de ciclo

```text
VEREDICTO_CICLO: submitted | blocked | idle
TASKSPEC:
AGENTES_USADOS:
ARCHIVOS_TOCADOS:
EVIDENCIA:
TESTS:
COMMIT:
RIESGOS:
```
