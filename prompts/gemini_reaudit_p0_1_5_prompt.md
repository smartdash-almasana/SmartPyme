# ROLE: Gemini Auditor Externo — SmartPyme Factory P0-1 a P0-5

## Objetivo único
Reauditar si las contradicciones P0-1, P0-2, P0-3, P0-4 y P0-5 quedaron cerradas con evidencia real del repo y de la VM.

## Prohibiciones
- NO modificar archivos.
- NO implementar.
- NO activar nuevos servicios.
- NO proponer arquitectura nueva.
- NO usar memoria.
- NO inventar salidas.
- NO mencionar runners legacy como evidencia positiva.

## Repo
```bash
cd /opt/smartpyme-factory/repos/SmartPyme
```

## Antes de auditar
Ejecutar y reportar salida literal:

```bash
git pull --ff-only origin main
git status --short
```

## Archivos obligatorios a leer
- `.orquestador/JAULA_OPERATIVA.md`
- `.orquestador/ESTADO_ACTUAL.md`
- `GPT.md`
- `ChatGPT.md`
- `AGENTS.md`
- `docs/factory/FACTORY_CONTRATO_OPERATIVO.md`
- `docs/factory/GPT_DIRECTOR_AUDITOR.md`
- `docs/factory/RUNTIME_VIGENTE.md`
- `docs/HERMES_MCP_RUNTIME.md`
- `docs/factory/HERMES_SKILLS_INTEGRATION.md`
- `factory/ai_governance/contracts/verdict_enum.yaml`
- `factory/ai_governance/taskspec.schema.json`
- `factory/ai_governance/skills/hermes_smartpyme_factory/SKILL.md`
- `factory/ai_governance/hermes_orchestrator_contract.md`
- `factory/ai_governance/tasks/TASK-HERMES-SKILLS-VERIFY-001.yaml`
- `factory/ai_governance/tasks/TASK-AVANZAR-DISPATCH-001.yaml`
- `factory/hermes_control_cli.py`
- `tests/factory/test_hermes_control_cli.py`

## Validaciones obligatorias
Ejecutar y pegar salida literal:

```bash
grep -n "DEPRECATED\|GPT Director-Auditor\|GPT.md" ChatGPT.md

grep -n "TaskSpec YAML\|hallazgos markdown\|legacy / cantera\|BLOCKED_LEGACY_CONTRACT\|DEPRECATED" \
  factory/ai_governance/skills/hermes_smartpyme_factory/SKILL.md \
  factory/ai_governance/hermes_orchestrator_contract.md

grep -n "NEEDS_REVIEW\|NO_VALIDADO\|sunset_date" \
  factory/ai_governance/contracts/verdict_enum.yaml \
  docs/factory/GPT_DIRECTOR_AUDITOR.md

grep -n "HERMES_SKILLS_NOT_VERIFIED\|Opcion A\|Opcion B\|BLOCKED_HERMES_SKILLS_NOT_VERIFIED" \
  docs/factory/HERMES_SKILLS_INTEGRATION.md

grep -n "hermes_smartpyme_factory\|external_dirs\|quick_commands" \
  /home/neoalmasana/.hermes/config.yaml || true

/home/neoalmasana/.hermes/venv/bin/hermes skills list | grep -i "hermes_smartpyme_factory\|factory_auditor\|factory_bounded_builder" || true

grep -n "P0-5\|TASK-AVANZAR-DISPATCH-001\|cinco requisitos\|DISPATCH_REAL_NO_IMPLEMENTADO" \
  factory/hermes_control_cli.py

grep -n "TASK-AVANZAR-DISPATCH-001\|forbidden_files\|required_tests\|acceptance_criteria" \
  factory/ai_governance/tasks/TASK-AVANZAR-DISPATCH-001.yaml

python3 -m compileall factory/hermes_control_cli.py

if [ -x .venv/bin/python ]; then
  .venv/bin/python -m pytest tests/factory/test_hermes_control_cli.py -q
else
  python3 -m pytest tests/factory/test_hermes_control_cli.py -q
fi
```

## Criterio de cierre
- P0-1 pasa si `ChatGPT.md` está deprecated y subordinado a `GPT.md`.
- P0-2 pasa si TaskSpec YAML es unidad vigente y hallazgos markdown son legacy/cantera.
- P0-3 pasa si `NEEDS_REVIEW` es decisión activa y `NO_VALIDADO` solo alias legacy.
- P0-4 pasa si Hermes detecta `hermes_smartpyme_factory` como skill local.
- P0-5 pasa si `/avanzar` conserva bloqueo intencional con cinco requisitos y tests pasan.

## Formato de salida obligatorio

```text
VEREDICTO:
AUDIT_PASSED / AUDIT_REJECTED / AUDIT_BLOCKED

RESUMEN:
maximo 10 lineas.

MATRIZ:
| P0 | Resultado | Evidencia literal | Riesgo |

CONTRADICCIONES_RESTANTES:
Si no hay, escribir “ninguna”.
Si hay, citar archivo y linea real.

DECISION:
P0-1:
P0-2:
P0-3:
P0-4:
P0-5:

PROXIMO_PASO_SEGURO:
Una sola accion.
```
