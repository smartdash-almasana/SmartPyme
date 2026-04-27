# SmartPyme Factory — Loop industrial de documentacion

## Proposito

Este documento define el loop profesional de documentacion para la factoria multiagente de SmartPyme.

La documentacion no es texto accesorio: es una capa de control del producto. Toda arquitectura, ingenieria, prompting, skill o spec debe quedar versionada, validable y alineada con el runtime real.

## Familias documentales

| Familia | Ubicacion sugerida | Funcion |
|---|---|---|
| Arquitectura | `docs/` | define sistema, capas, limites y decisiones permanentes |
| Ingenieria | `docs/factory/` y `docs/` | define runtime real, contratos, validaciones y procedimientos |
| Prompting | `docs/factory/prompts/` | define prompts industriales versionados para agentes |
| Skills | `docs/SKILLS_CATALOGO_SMARTPYME.md` | define contratos de capacidades antes de runtime |
| Tareas gobernadas | `factory/ai_governance/tasks/*.yaml` | cola activa de fabricacion y mejora |
| Evidencia | `factory/evidence/` | salida auditable de ciclos ejecutados |

## Loop documental

```text
observar runtime real
→ detectar deriva documental o necesidad nueva
→ crear task YAML gobernada
→ actualizar doc/spec/prompt minimo
→ validar con grep/diff/tests si aplica
→ registrar evidencia
→ cerrar ciclo en WAITING_AUDIT
→ aprobacion humana
```

## Tipos de deriva

| Tipo | Sintoma | Accion |
|---|---|---|
| Deriva de runtime | doc dice una ruta, codigo usa otra | corregir doc y marcar legado |
| Deriva de naming | dos nombres para el mismo concepto | normalizar y registrar alias legado |
| Deriva de skill | skill documentada sin executor real | marcar conceptual/partial/pending |
| Deriva de prompt | prompt no exige schema/evidencia | endurecer contrato de salida |
| Deriva de arquitectura | blueprint contradice runtime actual | actualizar doc operativo, no reescribir producto |

## Prompting industrial

Todo prompt de agente debe declarar:

- rol exacto;
- objetivo unico;
- contexto operativo minimo;
- archivos permitidos;
- archivos prohibidos;
- acciones prohibidas;
- criterios de aceptacion;
- comandos de validacion;
- formato de reporte;
- regla de bloqueo.

Plantilla minima:

```text
ROLE: <agente>
OBJETIVO: <uno solo>
CONTEXTO: <runtime real>
ALLOWED_FILES: <lista cerrada>
FORBIDDEN_FILES: <lista cerrada>
FORBIDDEN_ACTIONS: <lista cerrada>
ACCEPTANCE: <checks observables>
VALIDATION: <comandos>
REPORT: VEREDICTO / ARCHIVOS / VALIDACION / SHA
```

## Reescritura automatica de specs y skills

Permitida solo bajo gobernanza.

Condiciones:

- debe existir una tarea YAML en `factory/ai_governance/tasks/`;
- debe declarar `allowed_files`;
- debe declarar `forbidden_files`;
- debe tener validacion reproducible;
- no puede registrar runtime inexistente como implementado;
- debe cerrar con evidencia y gate humano.

Estados documentales recomendados:

```text
conceptual → partial → implemented → validated → deprecated
```

## Memoria por capas

| Capa | Fuente |
|---|---|
| Corto plazo | `factory/control/FACTORY_STATUS.md`, ultimo gate, ultima evidencia |
| Operativa | `scripts/hermes_factory_runner.py`, tasks YAML, evidence |
| Arquitectonica | `docs/SMARTPYME_OS_ACTUAL.md`, `docs/HERMES_MCP_RUNTIME.md`, roadmap |
| Skills | `docs/SKILLS_CATALOGO_SMARTPYME.md` |
| Historica | `docs/archive/` y archivos legacy degradados |

## QA documental

Antes de cerrar una tarea documental:

```bash
git diff -- <archivos>
grep -R "factory/ai_governance/tasks" -n docs factory/ai_governance/tasks scripts/hermes_factory_runner.py
grep -R "WAITING_AUDIT\|evidencia\|allowed_files\|forbidden_files" -n docs/factory factory/ai_governance/tasks
git status --short
```

## QA de codigo generado

Todo cambio de codigo debe exigir, segun aplique:

- `pytest` especifico;
- `ruff` o linter Python si esta disponible;
- validacion de contrato/schema;
- diff de archivos modificados;
- evidencia en `factory/evidence/`;
- reporte con estado del gate.

## Autoridad y responsabilidad

| Actor | Autoridad |
|---|---|
| Owner humano | aprueba/rechaza ciclos |
| ChatGPT director tecnico | define siguiente paso, audita deriva, produce specs/tareas |
| Hermes | opera conversacion y tools MCP |
| Gemini | razona arquitectura/specs/prompting |
| Codex | implementa bajo contrato |
| Runner | ejecuta el ciclo, no decide producto |

## Regla final

La factoria puede perfeccionarse a si misma, pero no puede liberarse de gobernanza.

Toda mejora de arquitectura, ingenieria, prompt, skill o spec debe pasar por:

```text
tarea gobernada → validacion → evidencia → WAITING_AUDIT → decision humana
```
