# Hermes Orchestrator Contract — SmartPyme Factory

**Estado:** DEPRECATED — ver `docs/factory/FACTORY_CONTRATO_OPERATIVO.md`  
**Versión:** v1.1-deprecated  
**Remediación:** P0-2 — TaskSpec YAML reemplaza hallazgos markdown como cola operativa  
**Fecha:** 2026-04-28

> Este documento queda como referencia histórica. No define el runtime vigente de SmartPyme Factory.
>
> La fuente canónica vigente es:
>
> ```text
> docs/factory/FACTORY_CONTRATO_OPERATIVO.md
> factory/ai_governance/taskspec.schema.json
> factory/ai_governance/tasks/*.yaml
> ```

## Motivo de deprecación

Este documento declaraba que Hermes gobernaba el ciclo de trabajo sobre hallazgos markdown y que la unidad oficial era el hallazgo markdown. Esa definición fue reemplazada por el contrato operativo vigente.

La unidad de trabajo vigente de SmartPyme Factory es:

```text
TaskSpec YAML en factory/ai_governance/tasks/<task_id>.yaml
```

Los hallazgos markdown en `factory/hallazgos/**` quedan como:

- legacy;
- cantera documental;
- insumo histórico;
- material convertible manualmente a TaskSpec YAML.

No son cola operativa vigente.

## Regla de autoridad

Si este documento contradice alguno de los siguientes archivos, prevalecen siempre los documentos canónicos:

```text
docs/factory/FACTORY_CONTRATO_OPERATIVO.md
factory/ai_governance/taskspec.schema.json
factory/ai_governance/tasks/*.yaml
```

## Regla de bloqueo

Cualquier agente que intente usar este documento para ejecutar un ciclo basado en hallazgos markdown debe responder:

```text
BLOCKED_LEGACY_CONTRACT
```

El ciclo solo puede continuar si existe una TaskSpec YAML validable contra `factory/ai_governance/taskspec.schema.json`.

## Verificación esperada

```bash
cd /opt/smartpyme-factory/repos/SmartPyme && grep -n "DEPRECATED\|TaskSpec YAML\|BLOCKED_LEGACY_CONTRACT" factory/ai_governance/hermes_orchestrator_contract.md
```
