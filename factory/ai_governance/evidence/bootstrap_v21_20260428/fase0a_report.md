# Fase 0A — Diagnóstico Forense SmartPyme
Fecha: 2026-04-28T19:46:42+00:00
Repo: /home/neoalmasana/smartpyme-factory/repos/SmartPyme

## 1. Runtimes y Legacy Detectados
| Archivo | Ubicación | Estado |
|---|---|---|
| hermes_factory_runner.py | — | NO ENCONTRADO |
| telegram_factory_control.py | — | NO ENCONTRADO |
| install_telegram_control_service.sh | scripts/install_telegram_control_service.sh | EXISTE (37 líneas) |
| hermes-factory-pool.service | infra/systemd/hermes-factory-pool.service | EXISTE (15 líneas) |
| hermes_loop.py | factory/orchestrator/hermes_loop.py | EXISTE (111 líneas) |
| continuous_factory.py | factory/continuous_factory.py | EXISTE (461 líneas) |
| multiagent_runner.py | factory/multiagent_runner.py | EXISTE (339 líneas) |
| run_factory.py | factory/run_factory.py | EXISTE (517 líneas) |
| run_codex_worker.py | factory/run_codex_worker.py | EXISTE (484 líneas) |
| agent.py | agent.py | EXISTE (7 líneas) |
| run_sfma_cycle.sh | — | NO ENCONTRADO |
| smartpyme-sfma.service | — | NO ENCONTRADO |

## 2. TaskSpecs
- Total archivos .yaml en tasks/: 21
- Nombres:
  - 0000_hermes_avanzar_dispatch_real_001.yaml (SIN_VERSION)
  - 0000_hermes_professional_reset_001.yaml (SIN_VERSION)
  - 0000_incident_hermes_breakdown_001.yaml (SIN_VERSION)
  - 0000_legacy_isolation_001.yaml (SIN_VERSION)
  - 0000_telegram_control_idempotency_001.yaml (SIN_VERSION)
  - 000_environment_contract_python_001.yaml (SIN_VERSION)
  - 000_repo_clean_contract_001.yaml (SIN_VERSION)
  - audit_context_bundle_001.yaml (SIN_VERSION)
  - core_reconciliacion_v1.yaml (SIN_VERSION)
  - factory_contract_alignment_001.yaml (SIN_VERSION)
  - factory_observability_status_v1.yaml (SIN_VERSION)
  - gpt_director_auditor_bootstrap_001.yaml (SIN_VERSION)
  - hermes_comandos_telegram_001.yaml (SIN_VERSION)
  - kernel_total_audit_001.yaml (SIN_VERSION)
  - product_final_concept_audit_001.yaml (SIN_VERSION)
  - source_of_truth_001.yaml (SIN_VERSION)
  - task_loop_001.yaml (SIN_VERSION)
  - task_priority_hardening_001.yaml (SIN_VERSION)
  - telegram_cycle_closed_notify_v1.yaml (SIN_VERSION)
  - telegram_delivery_setup_v1.yaml (SIN_VERSION)
  - telegram_human_notifications_001.yaml (SIN_VERSION)

## 3. Hallazgos
- pending/: 3 archivos
- done/: 3 archivos
- in_progress/: 0 archivos
- blocked/: 0 archivos

## 4. Campo prohibido vs cliente_id
- campo prohibido (tenant_id): 7 ocurrencias
- cliente_id: 32 ocurrencias

## 5. Variable de path Python prohibida
- Referencias encontradas: 0

## 6. MCP Bridge
- Transporte: stdio (mcp.run() detectado)

## 7. Config Hermes
- Config encontrada: /home/neoalmasana/.hermes/config.yaml

## 8. Telegram
- telegram_notify.py: 324 líneas
  - Sin parse_mode
  - print() encontrados: 3
- Allowlist: NO ENCONTRADA

## 9. app/core/ vs core/
- app/core/: 13 items, último commit: 7f6e231 Factory cycle: factory/ai_governance/tasks/audit_context_bundle_001.yaml
sin commits
- core/: 6 items, último commit: 63fbbf9 feat: add Mercado Libre OAuth integration layer
sin commits

## 10. Skills
- /home/neoalmasana/smartpyme-factory/repos/SmartPyme/factory/ai_governance/skills/factory_auditor/SKILL.md
- /home/neoalmasana/smartpyme-factory/repos/SmartPyme/factory/ai_governance/skills/factory_bounded_builder/SKILL.md
- /home/neoalmasana/smartpyme-factory/repos/SmartPyme/factory/ai_governance/skills/gpt_director_auditor.yaml
- /home/neoalmasana/smartpyme-factory/repos/SmartPyme/factory/ai_governance/skills/hermes_control_telegram.yaml
- /home/neoalmasana/smartpyme-factory/repos/SmartPyme/factory/ai_governance/skills/hermes_smartpyme_factory/SKILL.md

---
