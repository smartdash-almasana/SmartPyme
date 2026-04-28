# ESTADO ACTUAL — SMARTPYME FACTORY

## Fecha

2026-04-28

## Repo VM

`/home/neoalmasana/smartpyme-factory/repos/SmartPyme`

## GitHub

`smartdash-almasana/SmartPyme`

## Último commit limpio conocido en VM antes del bootstrap remoto

`b0da6cd9c3c34267306227c89a00540cd1932176`

## Situación actual registrada

- La VM tenía cambios locales antes de los commits remotos nuevos.
- `main` remoto fue modificado con archivos de bootstrap v2.1.
- No se activó systemd.
- No se migraron TaskSpecs con `--execute`.
- No se tocó core Python.
- No se tocó `mcp_smartpyme_bridge.py`.
- Fase 0A fue ejecutada localmente y produjo `fase0a_report.md`.
- El migrador TaskSpec validó `21 valid, 0 errors` en dry-run local.
- Gemini produjo `factory/ai_governance/evidence/documental_cross_audit_20260428/gemini_audit_report.md`.
- Gemini bloqueó por dos contradicciones críticas: vocabulario de veredictos y `tenant_id` vs `cliente_id`.
- Copilot queda fuera del circuito por decisión humana.

## Circuito de agentes vigente

- GPT Orquestador: remedia bajo jaula operativa.
- Gemini Auditor: audita y reaudita con independencia.
- Copilot: excluido del circuito.

## Archivos locales sensibles detectados

No borrar ni pisar:

- `factory/config/telegram.local.env`
- `factory/install_hermes_telegram_control.py`

## Estado de seguridad

No se debe activar ningún servicio hasta validar:

- repo local alineado;
- config real de Hermes;
- token Telegram fuera del repo;
- allowlist real;
- `/estado` funcionando;
- `dry_run` completo.

## Próxima acción permitida

GPT puede remediar únicamente los dos bloqueos Gemini P0/P1:

1. vocabulario de veredictos;
2. `tenant_id` activo vs `cliente_id` canónico.

La remediación debe generar:

`factory/ai_governance/evidence/documental_cross_audit_20260428/gpt_remediation_report.md`

## Regla inmediata

No avanzar a activación, migración real ni systemd hasta reauditoría Gemini posterior.
