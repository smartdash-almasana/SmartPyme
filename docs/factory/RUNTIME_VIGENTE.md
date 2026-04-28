---
status: CANONICO v1
created: 2026-04-28
replaces:
  - DOC-001
  - DOC-005
  - DOC-006
validates_with: grep -rn "hermes_factory_runner\|telegram_factory_control\|run_sfma_cycle" README.md docs factory prompts infra .github --exclude-dir=.git || true
---

# Runtime Vigente SmartPyme Factory

## Fuente de verdad única

El runtime conversacional vigente de SmartPyme Factory es **Hermes Gateway externo**.

SmartPyme no contiene un cerebro autónomo de producción. El repositorio SmartPyme contiene:

- contratos;
- TaskSpecs;
- gates;
- evidencia;
- documentación operativa;
- adaptadores finos para que Hermes Gateway invoque operaciones controladas.

## Componentes vigentes

| Componente | Estado | Ruta |
|---|---|---|
| Hermes Gateway | VIGENTE | `/home/neoalmasana/.hermes/venv/bin/hermes` |
| Hermes Agent repo | VIGENTE | `/opt/smartpyme-factory/repos/hermes-agent` |
| SmartPyme repo | FUENTE DE VERDAD | `/opt/smartpyme-factory/repos/SmartPyme` |
| Adaptador interno | VIGENTE | `factory/hermes_control_cli.py` |
| Quick commands installer | VIGENTE | `factory/install_hermes_telegram_control.py` |

## Runners legacy prohibidos

Los siguientes artefactos no son runtime vigente y no deben ser ejecutados por systemd, GitHub Actions, Gateway ni scripts de operación:

```text
scripts/hermes_factory_runner.py
scripts/telegram_factory_control.py
run_sfma_cycle.sh
```

Cualquier mención restante a esos nombres debe aparecer solo como `LEGACY`, `DEPRECATED`, `PROHIBIDO`, `NO OPERATIVO` o dentro de documentación histórica.

## Verificación operativa

```bash
cd /home/neoalmasana && /home/neoalmasana/.hermes/venv/bin/hermes gateway status
```

```bash
cd /home/neoalmasana && ps -ef | grep -E "hermes_factory_runner|telegram_factory_control" | grep -v grep || true
```

El segundo comando debe devolver vacío.

## Historial de Cambios

- 2026-04-28 — Creado por remediación P0 para cerrar DOC-001, DOC-005 y DOC-006. Declara Hermes Gateway como único runtime conversacional vigente y runners legacy como prohibidos/no operativos.
