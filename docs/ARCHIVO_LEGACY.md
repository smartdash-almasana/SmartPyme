# Archivo legacy propuesto

Este documento no borra archivos. Clasifica que debe dejar de gobernar la arquitectura activa y registra movimientos seguros de archivo.

## Documentos desactualizados o degradados

| archivo / concepto | problema | accion recomendada |
|---|---|---|
| `README.md` | Decia "sin codigo funcional todavia", contradiciendo bridge MCP, SQLite y E2E actuales. | Actualizado. |
| `docs/archive/smarttimes_full_architecture.md` | Mezcla SmartTimes/SmartPyme, HermesBot, MCP conceptual por capas y n8n. | Archivado como historico. |
| `docs/archive/80.000pdf.md` | Propuesta RAG generica; trata Hermes como no estandar y propone otras arquitecturas. | Archivado como referencia historica de exploracion. |
| `docs/topologia.txt` | Texto rector de factoria, util pero anterior al runtime Hermes/MCP actual. | Conservar como contexto de factory, no como contrato runtime. |
| `docs/ARQUITECTURA_NORMALIZADA.md` | Sigue siendo util, pero no incorpora Hermes como operador ni MCP real activo. | Actualizar o subordinar a `SMARTPYME_OS_ACTUAL.md` para runtime. |
| `docs/FUENTES_Y_JERARQUIA.md` | Jerarquia previa no reflejaba ubicacion de docs archivados. | Referencias de archivo actualizadas. |
| `docs/archive/FUENTES_DEPRECABLES.md` | Correcto como antecedente, incompleto para estado Hermes/MCP. | Sincronizar con este archivo. |
| `docs/archive/factory_hallazgos_cierre_2026-04-23.md` | Cierre puntual de factory/hallazgos; no gobierna runtime SmartPyme OS. | Archivado como evidencia historica. |

## Skeletons conceptuales

| archivo / concepto | problema | accion recomendada |
|---|---|---|
| `factory/mcp_bridge/server.py` | Potencial confusion con bridge MCP real de raiz. | Marcar como factory/skeleton si no participa del runtime Hermes. |
| `factory/mcp_bridge/tools.py` | Puede parecer registro MCP activo alternativo. | Documentar como no-runtime salvo evidencia contraria. |
| `factory/local_mcp_server.py` | Nombre sugiere server MCP paralelo. | Clasificar como experimento/local hasta validacion. |
| `app/orchestration/pipeline.py` | Pipeline antiguo fuera de `app/core` y con `findings_engine`. | Revisar si es legado frente a `app/core/orchestrator`. |
| `app/modules/findings_engine.py` | Naming viejo `findings`; posible dominio previo. | Mantener solo si hay adapter tecnico necesario. |
| `app/modules/test_findings_engine.py` | Test del modulo anterior. | Clasificar con el modulo. |
| `app/user_layer`, `app/system_growth`, `app/source_connectors`, `app/knowledge`, `app/memory` | Directorios de capas conceptuales sin evidencia de runtime MCP activo. | No borrar; marcar como conceptual pendiente. |

## Scripts temporales de validacion / seed

| archivo / concepto | problema | accion recomendada |
|---|---|---|
| `scripts/dev/validate_orchestration.py` | Script manual de validacion; no es contrato runtime. | Movido a utilidades dev. |
| `scripts/dev/seed_jobs_db.py` | Seed manual de SQLite. | Movido a utilidades dev. |
| `scripts/dev/seed_clarifications_db.py` | Seed manual de SQLite; elimina DB antes de sembrar. | Movido a utilidades dev. |
| `scripts/dev/seed_evidence_store.py` | Seed manual de EvidenceStore. | Movido a utilidades dev y ajustado a raiz del repo. |
| `tests/fixtures/test_document.txt` | Archivo de prueba. | Movido a fixtures. |
| `tests/e2e/validate_bridge_e2e.py` | Es validacion importante, pero hace cleanup agresivo. | Conservado; fixture temporal aislado en `tests/fixtures/`. |

## Directorios temporales

| archivo / concepto | problema | accion recomendada |
|---|---|---|
| `tmp*` en raiz | Directorios temporales numerosos, algunos con acceso denegado. | Inventariar y archivar/eliminar solo con aprobacion. |
| `codex_hallazgos_*` | Artefactos temporales de ejecucion. | Revisar contenido y proponer limpieza. |
| `codex_tmp_hallazgos_smoke_*` | Artefacto temporal de smoke. | Revisar contenido y proponer limpieza. |
| `factory/logs/pytest_tmp` | Temporal con acceso denegado en busqueda. | Revisar permisos antes de decidir accion. |

## Nombres viejos y conceptos que ya no gobiernan

| concepto | problema | accion recomendada |
|---|---|---|
| Bot propio interno | Hermes Agent es el operador conversacional actual. | No usar como arquitectura activa. |
| Orquestador conversacional interno | Hermes ocupa ese rol por fuera del core. | Relegar a historico salvo contrato nuevo. |
| Hermes externo/secundario | Hermes es runtime conversacional activo. | Corregir documentos que lo traten como secundario. |
| Bridge MCP stub | El bridge raiz tiene tools reales. | Reemplazar por "bridge MCP real con alcance minimo". |
| SmartSync como nombre principal | Alias legado. | Usar SmartPyme. |
| SmartTimes como nombre principal | Naming historico/documental. | Usar SmartPyme. |
| `findings` como termino de negocio | El termino rector en castellano es hallazgos. | Mantener `findings` solo como nombre tecnico legado existente. |
| n8n como componente canonico | No es runtime evidenciado de SmartPyme OS. | No usar como arquitectura activa. |
| MCP conceptual Data/Context/Action/AI | No coincide con tools registradas reales. | Separar como idea futura, no runtime. |
