# NEXT CYCLE — SmartPyme Factory

status: READY_FOR_HERMES
updated_by: ChatGPT_Director_Auditor
source_of_truth:
  - docs/factory/FACTORY_CONTRATO_OPERATIVO.md
  - factory/ai_governance/skills/hermes_smartpyme_factory/SKILL.md
  - factory/ai_governance/taskspec.schema.json

## Ciclo vigente

Hermes Gateway debe ejecutar una unica TaskSpec YAML `pending` desde:

```text
factory/ai_governance/tasks/*.yaml
```

La TaskSpec prioritaria autorizada para el proximo `/avanzar` es:

```text
factory/ai_governance/tasks/0000_hermes_avanzar_dispatch_real_001.yaml
```

## Motivo

El contenido anterior de `NEXT_CYCLE.md` apuntaba a `core-reconciliacion-v1`, un frente legacy/desalineado con el contrato operativo vigente.

El contrato vigente establece que:

- Hermes Gateway externo es el runtime conversacional.
- La unidad de trabajo vigente es TaskSpec YAML.
- `/avanzar` debe ejecutar un unico ciclo con pull, lectura canonica, schema, alcance, tests, evidencia y gate.
- No deben reactivarse runners legacy ni scripts paralelos.

## Regla de ejecucion

Hermes debe seguir la TaskSpec tal como esta escrita. Este archivo no reemplaza ni extiende el schema.

## Comando esperado del owner

```text
/avanzar
```

## Criterio de cierre del ciclo

El ciclo solo puede cerrar si deja evidencia reproducible en:

```text
factory/evidence/hermes_avanzar_dispatch_real_001/
```

con, como minimo:

```text
cycle.md
commands.txt
git_status.txt
git_diff.patch
tests.txt
decision.txt
```

## Prohibiciones

- No ejecutar `scripts/hermes_factory_runner.py`.
- No ejecutar `scripts/telegram_factory_control.py`.
- No ejecutar `run_sfma_cycle.sh`.
- No tocar `app/**`, `core/**` ni `services/**` en este ciclo.
- No seleccionar hallazgos markdown como cola operativa.
