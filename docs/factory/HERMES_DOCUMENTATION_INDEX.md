# Hermes Documentation Index — SmartPyme Factory

## Estado

CANÓNICO DOCUMENTAL v1.

Este archivo no define runtime por sí mismo. Ordena las fuentes que deben leerse para entender cómo Hermes se integra con SmartPyme Factory.

## Objetivo

Evitar pérdida de contexto entre chats, agentes y sesiones. Toda intervención documental u operativa debe empezar por este índice y por la jaula operativa.

## Regla de lectura mínima

Antes de proponer cambios sobre Hermes/SmartPyme Factory, leer en este orden:

1. `.orquestador/JAULA_OPERATIVA.md`
2. `.orquestador/ESTADO_ACTUAL.md`
3. `docs/factory/HERMES_DOCUMENTATION_INDEX.md`
4. `docs/factory/RUNTIME_VIGENTE.md`
5. `docs/HERMES_MCP_RUNTIME.md`
6. `docs/factory/MCP_TOOLS_CONTRACT.md`
7. `docs/factory/TELEGRAM_WEBHOOK_CONTRACT.md`
8. `docs/factory/OPUS_BLUEPRINT_V2_AUDITORIA.md`
9. `factory/ai_governance/contracts/verdict_enum.yaml`
10. `factory/ai_governance/schemas/taskspec.schema.json`

## Hermes oficial — fuentes externas imprescindibles

| Tema | Fuente |
|---|---|
| Home documentación | https://hermes-agent.nousresearch.com/docs/ |
| Repositorio oficial | https://github.com/NousResearch/hermes-agent |
| Producto / overview | https://nousresearch.com/hermes-agent/ |
| CLI commands | https://hermes-agent.nousresearch.com/docs/reference/cli-commands |
| Messaging Gateway | https://hermes-agent.nousresearch.com/docs/ |
| MCP integration | https://hermes-agent.nousresearch.com/docs/ |
| Skills system | https://hermes-agent.nousresearch.com/docs/ |
| Memory system | https://hermes-agent.nousresearch.com/docs/ |
| Context files | https://hermes-agent.nousresearch.com/docs/ |
| Security / sandboxing | https://hermes-agent.nousresearch.com/docs/ |

## Hermes según documentación oficial

Hermes tiene dos entradas principales:

1. CLI interactiva: `hermes`.
2. Messaging Gateway: `hermes gateway`, usado para Telegram, Discord, Slack, WhatsApp, Signal y otros canales.

Hermes puede operar desde una VM o servidor persistente, con memoria, skills, toolsets, MCP y gateway conversacional.

Para SmartPyme Factory, Hermes no es el core del negocio. Hermes es el orquestador conversacional y operativo que invoca herramientas controladas de SmartPyme.

## SmartPyme — interpretación vigente

| Área | Fuente interna | Decisión |
|---|---|---|
| Runtime conversacional | `docs/factory/RUNTIME_VIGENTE.md` | Hermes Gateway externo |
| MCP | `docs/HERMES_MCP_RUNTIME.md` y `docs/factory/MCP_TOOLS_CONTRACT.md` | stdio, no HTTP |
| Control local | `factory/hermes_control_cli.py` | adaptador interno, no cerebro autónomo |
| Telegram | `docs/factory/TELEGRAM_WEBHOOK_CONTRACT.md` | allowlist por `from_user.id`, token table, MarkdownV2 |
| Veredictos | `factory/ai_governance/contracts/verdict_enum.yaml` | vocabulario único requerido |
| TaskSpecs | `factory/ai_governance/schemas/taskspec.schema.json` | v2.0.0 requerido para cola activa |
| Auditoría Opus | `docs/factory/OPUS_BLUEPRINT_V2_AUDITORIA.md` | fuente histórica de bloqueos B-001…B-030 |

## Qué es Hermes dentro de SmartPyme Factory

Hermes debe:

- recibir comandos humanos por Telegram o CLI;
- leer contexto del proyecto;
- ejecutar skills;
- invocar tools MCP de SmartPyme por stdio;
- llamar al adaptador `factory/hermes_control_cli.py` para acciones controladas;
- entregar evidencia, estado y bloqueos al owner;
- coordinar ciclos de builder/auditor/director cuando existan gates validados.

Hermes no debe:

- escribir directo en bases SQLite de SmartPyme;
- saltar MCP para modificar estado de negocio;
- activar runners legacy;
- tocar core Python sin TaskSpec;
- ejecutar systemd antes de dry-run validado;
- inventar estado operativo no devuelto por herramientas o evidencia.

## Estado de fase documental

Escala corta del blueprint v2.1:

| Fase | Descripción | Estado documental actual |
|---|---|---|
| 0 | Pre-flight, naming, legacy, TaskSpecs, evidencia | INCOMPLETA |
| 1 | Contratos mínimos, schemas, Telegram, MCP, budgets | PARCIAL |
| 2 | Primer ciclo dry-run con mocks | NO HABILITADA |
| 3 | Infra/systemd y activación gradual | PROHIBIDA POR AHORA |

El repo no debe tratarse como listo para Fase 2/3 hasta cerrar los bloqueos documentales P0: vocabulario de veredictos y `cliente_id` activo vs `cliente_id` canónico.

## Bloqueos documentales vigentes

1. `gemini_audit_report.md` fue generado localmente pero no está garantizado como evidencia versionada en GitHub.
2. Hay contradicción de veredictos entre alias legacy y vocabulario canónico.
3. Hay referencias activas sospechosas a `cliente_id` fuera de evidencia histórica.
4. TaskSpecs legacy/SIN_VERSION fueron detectadas por Fase 0A; migración real sigue prohibida sin gate.
5. Allowlist real de Telegram no debe versionarse con secretos; solo `.example` pertenece al repo.

## Próximo paso documental seguro

Crear una remediación documental GPT que cierre solo:

1. vocabulario de veredictos;
2. `cliente_id` activo vs `cliente_id`;
3. registro versionado de evidencias críticas ya existentes localmente cuando estén disponibles.

No activar Hermes Gateway hasta que la documentación y evidencia cierren esos bloqueos.
