# SmartPyme Factory — Contrato operativo vigente

## Verdad de runtime

El runtime activo de la factoria autonoma es `scripts/hermes_factory_runner.py`.

La cola activa de trabajo es:

```text
factory/ai_governance/tasks/*.yaml
```

No debe tratarse `factory/hallazgos/*` como cola activa de este runner. Esa estructura queda como antecedente historico o runtime alternativo no activo hasta nueva decision explicita.

## Flujo operativo

```text
Telegram / Gate
→ scripts/hermes_factory_runner.py
→ factory/ai_governance/tasks/*.yaml
→ scripts/codex_builder_runner.py
→ scripts/factory_post_cycle_control.py
→ factory/evidence/
→ factory/control/AUDIT_GATE.md
→ auto commit + push si ciclo OK
→ Telegram notify
```

## Gate

Estados que permiten dispatch:

- `APPROVED`
- `OPEN`
- `RUN`

Estados bloqueantes:

- `WAITING_AUDIT`
- `BLOCKED`
- `HOLD`

Reglas:

- `WAITING_AUDIT` bloquea todo nuevo dispatch.
- `REJECTED` reabre la ultima tarea registrada por el gate.
- Todo ciclo cerrado vuelve a `WAITING_AUDIT`.
- No hay loop ciego: cada ciclo requiere auditoria o apertura explicita.

## Unidad de trabajo

Una tarea de factoria es un YAML gobernado en:

```text
factory/ai_governance/tasks/<task_id>.yaml
```

Campos minimos esperados:

```yaml
task_id: string
mode: string
status: pending | in_progress | done | blocked | rejected
human_required: boolean
objective: string
allowed_files: []
forbidden_files: []
forbidden_actions: []
acceptance_criteria: []
validation_commands: []
report_required: []
```

## Roles

| Rol | Responsabilidad |
|---|---|
| ChatGPT director tecnico | detectar deriva, proponer specs/tareas, auditar arquitectura |
| Hermes | operador conversacional / orquestador por MCP |
| Gemini | razonamiento arquitectonico, specs, prompts industriales |
| Codex | construccion de codigo bajo tarea cerrada |
| SmartPyme kernel | verdad operativa: jobs, evidencia, clarifications, estado |
| Humano owner | aprueba, rechaza o bloquea por gate |

## Produccion de codigo

Todo cambio productivo debe seguir:

```text
objetivo → task YAML → gate → dispatch → patch → tests → evidencia → WAITING_AUDIT → aprobacion humana
```

Ningun agente valida su propio trabajo.

## Reescritura de specs y skills

La factoria puede reescribir specs, prompts y skills solo bajo tarea gobernada.

Patron obligatorio:

```text
detectar deriva → crear tarea YAML → limitar allowed_files → validar diff → evidencia → WAITING_AUDIT
```

Prohibido:

- modificar runtime sin tarea explicita;
- crear skills ejecutables sin contrato y tests;
- registrar una skill sin executor real o estado explicitamente bloqueado;
- usar documentacion historica como runtime vigente.

## Anti-alucinacion

Reglas minimas:

- no afirmar runtime sin archivo citado o grep;
- no crear codigo sin criterios de aceptacion;
- no declarar cierre sin evidencia;
- no usar skeletons como produccion;
- no avanzar si el gate esta bloqueado;
- no generar hallazgos sin entidad, diferencia cuantificada y evidencia.

## Validacion minima de contrato

Comandos esperados:

```bash
grep -R "TASKS_DIR\|factory/ai_governance/tasks" -n scripts/hermes_factory_runner.py factory/ai_governance/tasks/*.yaml docs/factory/*.md
grep -R "WAITING_AUDIT\|TASK_DISPATCH\|AUTO_PUSH_OK" -n scripts/hermes_factory_runner.py docs/factory/*.md
git status --short
```
