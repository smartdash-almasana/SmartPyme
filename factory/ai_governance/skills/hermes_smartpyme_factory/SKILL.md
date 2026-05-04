## Automatización de Calidad (Lifecycle)

Cada TaskSpec ejecutada por esta skill debe garantizar el cumplimiento de los estándares de código de SmartPyme:

1. TESTS_RUN: Toda ejecución debe concluir con pruebas sobre los archivos tocados.
2. RUFF_RUN: Se debe aplicar `ruff check` sobre archivos Python modificados cuando corresponda.
3. El resultado del análisis debe persistirse en evidencia si la TaskSpec lo exige.
4. Ninguna TaskSpec Python puede cerrarse sin pytest y ruff check, salvo bloqueo documentado.
5. `ruff --fix` solo puede ejecutarse con autorización expresa.

remediation: protocolo de capas, fases y ruteo por modelo
platforms: [linux]
metadata:
  hermes:
    category: devops
    tags: [smartpyme, factory, multiagent, governance, taskspec, hermes, layers]
---

# Hermes SmartPyme Factory

## Estado de este skill

Este skill queda subordinado a:

```text
docs/factory/FACTORY_CONTRATO_OPERATIVO.md
factory/ai_governance/taskspec.schema.json
factory/ai_governance/skills/smartpyme_layer_work_protocol/SKILL.md
factory/ai_governance/skills/smartpyme_minimal_code_integration/SKILL.md
```

La unidad de trabajo vigente de SmartPyme Factory es **TaskSpec YAML** en:

```text
factory/ai_governance/tasks/<task_id>.yaml
```

Los hallazgos markdown en `factory/hallazgos/**` quedan como **legacy / cantera / insumo historico**. No son cola operativa vigente.

## Regla obligatoria de fase y modo

Toda TaskSpec o prompt operativo debe declarar:

```text
layer
phase
model_target
operational_mode
```

Equivalente en prompts:

```text
CAPA:
FASE:
MODEL_TARGET:
MODO:
```

Si falta capa/fase:

```text
BLOCKED_LAYER_PHASE_MISSING
```

Si falta modelo destino:

```text
BLOCKED_MODEL_TARGET_MISSING
```

Si falta modo operativo:

```text
BLOCKED_MODE_MISSING
```

Si el modelo destino no es válido:

```text
BLOCKED_MODEL_TARGET_INVALID
```

Si el modo operativo no es válido:

```text
BLOCKED_MODE_INVALID
```

Si modo y fase se contradicen:

```text
BLOCKED_MODE_PHASE_CONFLICT
```

Valores permitidos de `operational_mode`:

```text
ANALYSIS_ONLY
WRITE_AUTHORIZED
TEST_ONLY
CLOSE_ONLY
DOC_ONLY
BLOCKED_REVIEW
```

**Importante:** `ARCHIVOS_PERMITIDOS` no autoriza escritura sin `MODO: WRITE_AUTHORIZED`. `ANALYSIS_ONLY` nunca puede escribir, parchear, copiar, commiter ni pushear.

## Ruteo operativo

```text
CODEX: código delicado, refactor, integración con riesgo, tests complejos.
DEEPSEEK_4_PRO: tarea larga, integración de varios contratos, fallback cuando 3.2 se traba.
DEEPSEEK_3_2: auditoría acotada, verificación documental, contratos mínimos, tests puntuales.
```

Hermes no debe preguntar qué modelo usar. Debe respetar `model_target` de la TaskSpec o `MODEL_TARGET` del prompt.

## Activador operativo

El comando owner vigente es:

```text
/avanzar
```

Hermes Gateway debe intentar un solo ciclo sobre una unica TaskSpec `pending`, respetando repo, capa, fase, modelo destino, gate, alcance permitido, evidencia y auditoria.

## Modelo

- Hermes Gateway = orquestador operativo externo.
- SmartPyme repo = fuente de verdad versionada.
- TaskSpec YAML = unidad de trabajo vigente.
- Capa/Fase = frontera operativa.
- Model target = ruteo obligatorio.
- Evidencia = condicion de cierre.
- GPT Director-Auditor = autoridad externa ante bloqueo, auditoria o decision arquitectonica.

## Workspace valido

Hermes solo puede operar sobre:

```text
/opt/smartpyme-factory/repos/SmartPyme
/home/neoalmasana/smartpyme-factory/repos/SmartPyme
```

Precheck obligatorio:

```text
pwd
git remote -v
git status --short
git log --oneline -1
```

Si el workspace o el remote no coinciden con `smartdash-almasana/SmartPyme`, debe responder:

```text
BLOCKED_WRONG_WORKSPACE
```

## Unidad de trabajo vigente

Cada TaskSpec debe validar contra:

```text
factory/ai_governance/taskspec.schema.json
```

Campos minimos vigentes:

```yaml
task_id: string
mode: create_only | patch_only | governance | product
operational_mode: ANALYSIS_ONLY | WRITE_AUTHORIZED | TEST_ONLY | CLOSE_ONLY | DOC_ONLY | BLOCKED_REVIEW
layer: string
phase: DEFINIR | CONTRATAR | IMPLEMENTAR | INTEGRAR | AUDITAR | CERRAR | DOCUMENTAR
model_target: CODEX | DEEPSEEK_4_PRO | DEEPSEEK_3_2
status: pending | in_progress | submitted | blocked | validated | rejected
objective: string
allowed_files: []
forbidden_files: []
required_tests: []
acceptance_criteria: []
preflight_commands: []
post_commands: []
max_files_read: integer optional
max_searches: integer optional
```

Mientras el schema mantenga `additionalProperties: false`, no se deben introducir campos adicionales no declarados.

## Ciclo minimo

1. Confirmar workspace, rama y estado.
2. Validar TaskSpec contra schema.
3. Verificar `layer`, `phase`, `model_target` y `operational_mode`.
4. Validar coherencia `operational_mode` + `phase`.
5. Seleccionar una sola TaskSpec `pending`.
6. Validar `allowed_files`, `forbidden_files`, tests y criterios.
7. Si la fase es INTEGRAR, aplicar `smartpyme_minimal_code_integration`.
8. Ejecutar solo el alcance permitido según `operational_mode`.
9. Exigir evidencia reproducible.
10. Cerrar con tests, diff, status y decisión.
11. No abrir otra fase sin cierre explícito.

## Reglas específicas para INTEGRAR

Para fase INTEGRAR, antes de modificar debe declarar:

```text
PUNTO_DE_INTEGRACION:
ARCHIVOS_A_MODIFICAR:
TEST_A_MODIFICAR:
MODEL_TARGET:
```

Límites por defecto si la TaskSpec no define otros:

```text
ARCHIVOS_LEIDOS <= 5
BUSQUEDAS <= 2
ARCHIVOS_PRODUCTIVOS_MODIFICADOS <= 2
ARCHIVOS_TEST_MODIFICADOS <= 1
```

Si no hay punto claro:

```text
BLOCKED_INTEGRATION_POINT
```

## Reglas específicas para AUDITAR

La auditoría revisa el patch existente. No busca nueva arquitectura.

Debe revisar solo:

```text
- capa/fase/model_target;
- archivos permitidos;
- tests;
- violaciones semánticas;
- worktree;
- corrección mínima si aplica.
```

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
- No saltar de fase sin cierre explícito.
- No ejecutar auditoría repo-wide si la fase es INTEGRAR o AUDITAR acotado.

## Salida final de ciclo

```text
VEREDICTO_CICLO: submitted | blocked | idle
TASKSPEC:
CAPA:
FASE:
MODEL_TARGET:
AGENTES_USADOS:
ARCHIVOS_TOCADOS:
EVIDENCIA:
TESTS:
COMMIT:
RIESGOS:
NEXT_STEP:
```
