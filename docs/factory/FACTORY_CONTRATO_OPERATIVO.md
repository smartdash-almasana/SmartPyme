# SmartPyme Factory — Contrato operativo vigente

Estado: CANONICO v3 — Hermes profesional en castellano

## Verdad de runtime

El runtime activo de la factoria autonoma es Hermes Gateway.

```text
Telegram → Hermes Gateway → quick commands / skills → Repo → Tests → Evidencia → Auditoria → Decision humana
```

Queda deprecado cualquier runtime basado en runners caseros o bots paralelos.

## Prohibiciones operativas

No ejecutar ni reactivar:

```text
scripts/telegram_factory_control.py
scripts/hermes_factory_runner.py
```

Si alguno de esos procesos aparece activo, se considera contaminacion legacy y debe detenerse antes de cualquier ciclo.

## Cola activa de trabajo

La cola activa sigue siendo versionada en el repo:

```text
factory/ai_governance/tasks/*.yaml
```

Cada tarea debe respetar:

```text
factory/ai_governance/taskspec.schema.json
```

## Entrada canónica de ChatGPT / Director-Auditor

Todo ciclo de direccion debe arrancar por:

```text
ChatGPT.md
GPT.md
AGENTS.md
docs/factory/GPT_DIRECTOR_AUDITOR.md
prompts/GPT_DIRECTOR_AUDITOR_PROMPT.md
factory/ai_governance/skills/gpt_director_auditor.yaml
factory/ai_governance/taskspec.schema.json
factory/control/*
factory/evidence/*
```

## Flujo operativo profesional

```text
Owner por Telegram
→ Hermes Gateway
→ quick command o skill
→ git pull --ff-only origin main
→ lectura de archivos canonicos
→ seleccion de una unica TaskSpec pending
→ validacion de allowed_files / forbidden_files
→ tests obligatorios
→ evidencia en factory/evidence/
→ gate WAITING_AUDIT
→ Auditor externo revisa
→ owner aprueba, rechaza o bloquea
```

## Comandos Telegram vigentes en castellano

Los comandos deben implementarse como quick commands o skills de Hermes, no como scripts paralelos:

```text
/estado      → diagnostico de gateway, repo, gate, tarea activa y evidencia reciente
/actualizar  → git pull --ff-only origin main y reporte de commit actual
/pausar      → pausar factoria escribiendo estado PAUSED/HOLD en factory/control
/reanudar    → reabrir gate bajo estado OPEN/RUN si no hay auditoria pendiente
/avanzar     → ejecutar un unico ciclo: pull → leer canonicos → tomar proxima TaskSpec → test/evidencia → WAITING_AUDIT
/auditar     → revisar evidencia reciente y emitir APPROVED/REJECTED/BLOCKED/NO_VALIDADO
```

No usar nombres en ingles como mando principal del owner.

## Regla obligatoria de `/avanzar`

El primer paso de `/avanzar` es siempre:

```bash
cd /opt/smartpyme-factory/repos/SmartPyme && git pull --ff-only origin main
```

Si el pull falla, el ciclo queda BLOCKED y no se ejecuta nada mas.

## Gate

Estados que permiten dispatch:

- `APPROVED`
- `OPEN`
- `RUN`

Estados bloqueantes:

- `WAITING_AUDIT`
- `BLOCKED`
- `HOLD`
- `PAUSED`

Reglas:

- `WAITING_AUDIT` bloquea nuevo dispatch hasta auditoria.
- `PAUSED` o `HOLD` bloquean `/avanzar`.
- `REJECTED` reabre o corrige la ultima tarea registrada por el gate.
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

## Roles

| Rol | Responsabilidad |
|---|---|
| Owner humano | aprueba, pausa, reanuda o bloquea |
| ChatGPT Director-Auditor | define prioridad, audita evidencia, escribe specs |
| Hermes Gateway | recibe comandos Telegram y ejecuta quick commands/skills |
| Skill Director | lee canonicos, gate y tareas; decide un unico proximo ciclo |
| Builder/Codex/Gemini | ejecuta cambios bajo TaskSpec cerrada cuando Hermes lo delega |
| Auditor | revisa diff, tests y evidencia; no valida trabajo propio |
| SmartPyme kernel | verdad operativa: jobs, evidencia, clarifications, estado |

## Produccion de codigo

Todo cambio productivo debe seguir:

```text
objetivo → TaskSpec → gate → dispatch Hermes → patch → tests → evidencia → WAITING_AUDIT → aprobacion humana
```

Ningun agente valida su propio trabajo.

## Reescritura de specs y skills

La factoria puede reescribir specs, prompts y skills solo bajo tarea gobernada:

```text
detectar deriva → crear tarea YAML → limitar allowed_files → validar diff → evidencia → WAITING_AUDIT
```

Prohibido:

- modificar runtime sin tarea explicita;
- crear skills ejecutables sin contrato y tests;
- registrar una skill sin executor real o estado explicitamente bloqueado;
- usar documentacion historica como runtime vigente;
- reintroducir scripts legacy.

## Anti-alucinacion

Reglas minimas:

- no afirmar runtime sin archivo, comando o evidencia;
- no crear codigo sin criterios de aceptacion;
- no declarar cierre sin evidencia;
- no usar skeletons como produccion;
- no avanzar si el gate esta bloqueado;
- no generar hallazgos sin entidad, diferencia cuantificada y evidencia;
- no confiar en memoria si contradice repo, tests o logs.

## Validacion minima de contrato

```bash
cd /opt/smartpyme-factory/repos/SmartPyme && grep -R "Hermes Gateway\|telegram_factory_control.py\|hermes_factory_runner.py\|git pull --ff-only" -n ChatGPT.md GPT.md docs/factory factory/ai_governance | head -120
cd /opt/smartpyme-factory/repos/SmartPyme && git status --short
cd /home/neoalmasana && ps -ef | grep -E "telegram_factory_control|hermes_factory_runner" | grep -v grep || true
```

## Criterio de aceptacion

- Hermes Gateway es el unico runtime conversacional.
- `/avanzar` empieza con `git pull --ff-only origin main`.
- `/pausar` pausa sin matar la VM ni romper Gateway.
- No hay procesos legacy activos.
- La evidencia de cada ciclo queda en `factory/evidence/`.
- La decision final queda en gate y requiere auditoria.
