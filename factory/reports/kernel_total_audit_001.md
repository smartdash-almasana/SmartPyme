# kernel_total_audit_001

task_id: kernel_total_audit_001
mode: architecture_engineering_audit
sha: 9027f933bdfff85280b65e35f03a4987c58dc8e8
fecha_utc: 2026-04-28

## VEREDICTO_EJECUTIVO

VEREDICTO: INCOMPLETO.

La auditoria encuentra un kernel real, no un repositorio vacio: existen bridge MCP,
jobs SQLite, clarifications SQLite, evidence store JSONL, ingesta documental minima,
retrieval lexical/BM25 opcional, pipeline interno de facts/canonical/entity/comparison,
reconciliacion deterministica CSV/montos, hallazgos y contratos de acciones con
confirmacion. La distancia contra el producto final sigue siendo alta porque esas piezas
no forman todavia un flujo producto end-to-end para PyMEs.

El cierre queda fail-closed por tres motivos verificables: el repo ya estaba sucio en
`factory/control/**` antes de esta auditoria, `python` y `pytest` global no existen en
PATH, y `.venv` no puede colectar el suite completo por dependencias/modulos faltantes.
No se modifico codigo fuente.

## MAPA_KERNEL_REAL

Codigo real evidenciado:

- `mcp_smartpyme_bridge.py`: bridge MCP principal con `FastMCP("SmartPyme-Bridge")` y 7 tools: `create_job`, `get_job_status`, `list_pending_validations`, `resolve_clarification`, `save_clarification`, `get_evidence`, `ingest_document`. Evidencia: `factory/evidence/kernel_total_audit_001/mcp_bridge_source.txt`.
- `app/factory/orchestrator/*`: modelos, transiciones y persistencia SQLite de jobs. Evidencia: `factory/evidence/kernel_total_audit_001/grep_kernel_signals.txt`.
- `app/core/clarification/*` y `app/repositories/clarification_repository.py`: clarifications persistidas en SQLite y repositorio separado para pipeline interno.
- `services/document_ingestion_service.py`, `services/document_query_service.py`, `services/retrieval_service.py`, `extraction/*`, `models/document_models.py`: ingesta, chunking, citation index y retrieval local. Evidencia: `document_ingestion_source.txt`, `retrieval_source.txt`.
- `app/repositories/raw_document_registry.py`: registro de documentos originales con hash SHA-256.
- `app/services/fact_extraction_service.py`, `canonicalization_service.py`, `entity_resolution_service.py`, `comparison_service.py`, `findings_service.py`: pipeline interno de datos operativos, mayormente no expuesto por MCP.
- `app/core/reconciliation/service.py`: reconciliacion deterministica, CSV, jobs, warnings, HITL, MercadoLibre parcial y summary. Evidencia: `reconciliation_service_source.txt`.
- `app/core/hallazgos/*`: dominio de hallazgos de negocio y motor desde resultados de reconciliacion. Evidencia: `hallazgos_service_source.txt`.
- `app/services/action_proposal_service.py`, `action_decision_service.py`, `action_execution_service.py`, `app/contracts/action_contract.py`: propuestas, decision y ejecucion interna con guardas.
- `scripts/hermes_factory_runner.py`, `factory/ai_governance/tasks/*.yaml`, `factory/control/*`: factoria Hermes real segun docs canonicos.

Documentacion o antecedente, no runtime probado por si solo:

- `docs/RAW_RAG_INGESTION_ARCHITECTURE.md`, `docs/RAG_RETRIEVAL_PLAN.md`, `docs/archive/**`.
- `factory/hallazgos/**`: antecedente/dominio historico; `docs/SMARTPYME_OS_ACTUAL.md` dice que no es la cola activa del runner actual.
- `factory/local_mcp_server.py`: skeleton local con tools basicas; no es el bridge producto.

## CAPAS_IMPLEMENTADAS

- MCP minimo operacional en codigo: `mcp_smartpyme_bridge.py` registra tools reales y conecta jobs, clarifications, evidencia e ingesta documental.
- Jobs: `create_job` crea `OperationalPlanContract`, persiste job `CREATED`, `get_job_status` lee SQLite.
- Clarifications: creacion/listado/resolucion con persistencia SQLite.
- Evidence store local: documentos, chunks y citation index en JSONL/JSON.
- Raw document registry: calcula SHA-256 y deduplica documentos originales.
- Ingesta documental de archivo unico: `ingest_document` registra documento, ejecuta `DocumentIngestionService` y devuelve `raw_document_id`, hash, chunks y evidence IDs.
- Reconciliacion CSV/montos: `reconcile_csv_sources` lee 2 CSV, normaliza campos numericos y devuelve hallazgos por entidad.
- Hallazgos de negocio acotados: `HallazgoEngine` transforma diferencias en entidad, diferencia cuantificada y fuentes.
- Contratos de accion: existen propuesta, decision y ejecucion interna con confirmacion previa.

## CAPAS_PARCIALES

- OCR/document parsing: `parse_pdf` existe por import desde ingesta, pero el entorno no acredita `docling`, `pytesseract` ni `pdf2image`.
- Retrieval/RAG: `RetrievalService` tiene fallback lexical y BM25 opcional por LangChain, pero no hay indice persistente, embeddings ni tool MCP de consulta documental.
- EvidenceRepository: hay JSONL y registry, pero falta repositorio unificado con filtros por job, plan, fuente, metadata y lifecycle.
- Facts/canonical rows: existen contratos, repositorios SQLite y servicios, pero la extraccion es regex simple para amount/date/CUIT y no esta integrada al bridge MCP.
- Entity resolution: servicio basico por atributo `value`; no resuelve identidad distribuida de clientes, proveedores o SKUs con ambiguedad real.
- Comparison/findings: existen servicios internos, pero no hay pipeline end-to-end expuesto como tool producto.
- Hallazgos: dominio real, pero persistencia durable y exposicion MCP quedan parciales.
- MercadoLibre: hay adaptadores/repositorios/tests, pero faltan dependencias (`httpx`) y no esta integrado como flujo PyME general.
- Hermes/factory: runner y gate reales, pero el estado del repo muestra cambios de control no atribuibles a esta auditoria.

## CAPAS_AUSENTES

- Reparacion y analisis Excel real: no hay servicio `.xlsx/.xls`, no aparece `openpyxl` como dependencia activa, y el parser CSV no cubre Excel corrupto o multihoja.
- OCR operativo validado: faltan dependencias Python y binarios externos; no hay E2E OCR con documento escaneado.
- RAG documental robusto: faltan embeddings, vector index persistente, metadata filters, reranking, evaluacion de recall y tool MCP de busqueda.
- Dominios cerrados de stock, ventas, compras y pagos: hay reconciliacion generica, no modelos/servicios completos por dominio.
- Reconciliacion multi-fuente distribuida end-to-end: falta flujo `ingesta -> normalizacion -> ER -> comparacion -> hallazgos -> clarificacion -> accion`.
- Action engine externo: no hay adaptadores versionados para ejecutar acciones administrativas reales; correctamente no se ejecuta nada sin confirmacion.
- API/UI producto: `APIRouter`/FastAPI no aparecen como runtime principal; borde activo es MCP.
- QA canonico cerrado: entorno no cumple `docs/factory/PYTHON_ENVIRONMENT_CONTRACT.md`.

## MCP_Y_HERMES_REAL

Bridge producto real:

- Ruta: `mcp_smartpyme_bridge.py`.
- Evidencia: `factory/evidence/kernel_total_audit_001/mcp_bridge_source.txt`.
- Tools: `create_job`, `get_job_status`, `list_pending_validations`, `resolve_clarification`, `save_clarification`, `get_evidence`, `ingest_document`.
- Limitacion: `.venv` falla al importar tests MCP por `ModuleNotFoundError: No module named 'mcp'`.

MCP/factory alterno:

- Ruta: `factory/mcp_bridge/server.py` y `factory/mcp_bridge/tools.py`.
- Tools locales: `read_file`, `list_files`, `git_status`, `run_tests`, `move_hallazgo_state`.
- Riesgo: puede confundirse con bridge producto; debe quedar documentado como herramienta local/factory.

Hermes:

- `docs/SMARTPYME_OS_ACTUAL.md` y `docs/HERMES_MCP_RUNTIME.md` declaran `scripts/hermes_factory_runner.py` como runner de factoria y `factory/ai_governance/tasks/*.yaml` como cola activa.
- `factory/control/NEXT_CYCLE.md` apunta a `core-reconciliacion-v1`, no a esta auditoria; la tarea actual viene del YAML del usuario y de `factory/ai_governance/tasks/kernel_total_audit_001.yaml` en inventario.

## TESTS_LINTERS_QA

Comandos requeridos ejecutados y guardados:

- `git status --short`: `factory/evidence/kernel_total_audit_001/git_status.txt`.
- `find . -maxdepth 3 -type f | sort | sed 's#^./##' | head -300`: `files_scoped.txt`.
- `python -m compileall app core services scripts factory || true`: `compileall_python.txt`, falla porque `python` no existe.
- `pytest -q || true`: `pytest_global.txt`, falla porque `pytest` no existe.
- `grep -R "def \|class \|@mcp.tool\|FastMCP\|APIRouter" ... | head -300`: `grep_kernel_signals.txt`.
- `find factory/evidence ...`: `recent_evidence_files.txt`.
- `find factory/bugs ...`: `recent_bugs_files.txt`, `factory/bugs` no existe.

Validaciones adicionales:

- `python3 -m compileall app core services scripts factory`: pasa, evidencia en `compileall_python3.txt`.
- `python3 -m pytest -q`: falla, `No module named pytest`, evidencia en `pytest_python3.txt`.
- `python3 -m ruff check app core services scripts factory`: falla, `No module named ruff`, evidencia en `ruff_python3.txt`.
- `.venv/bin/python -m pytest -q`: falla en coleccion con 8 errores: `httpx`, `app.repositories.action_execution_repository`, `mcp`, `factory.agent_min`, `google` e import mismatch entre `tests/core/test_orchestrator.py` y `tests/factory/test_orchestrator.py`. Evidencia: `pytest_venv.txt`.
- `.venv/bin/python -m ruff ...`: falla, `No module named ruff`, evidencia en `ruff_venv.txt`.

## ERRORES_RECURRENTES_SEMANA

Evidencia revisada: `recurrent_errors_scan.txt`, `recent_evidence_files.txt`, `recent_runner_logs.txt`, `factory_status_snapshot.txt`, `audit_gate_snapshot.txt`.

- Contrato de entorno incompleto: se repiten bloqueos por ausencia de `python`, `pytest`, `ruff`, `polars` y dependencias de tests. Recomendacion: cerrar un `pyproject.toml` minimo y bootstrap reproducible antes de nuevas features.
- Repo sucio fuera de alcance: `factory/control/.telegram_control_offset`, `AUDIT_GATE.md` y `PRIORITY_BOARD.md` aparecian modificados antes de esta auditoria. Recomendacion: separar cambios de control en ciclo propio.
- Dependencias faltantes de tests: `httpx`, `mcp`, `google`, `ruff`, `pytest` global. Recomendacion: declarar extras o aislar tests por marcador.
- Modulos referenciados inexistentes: `app.repositories.action_execution_repository`, `factory.agent_min`. Recomendacion: decidir si se crean, se renombran imports o se archivan tests legacy.
- Import mismatch de pytest por nombres duplicados `test_orchestrator.py`. Recomendacion: configurar paquetes de tests o renombrar modulos.
- Ruido de `__pycache__` en grep. Recomendacion: excluir cache en comandos de auditoria (`-path '*/__pycache__' -prune`) sin borrar evidencia.

## TRAZABILIDAD_ROADMAP_PRODUCTO_FINAL

| Producto final esperado | Estado real | Evidencia | Recomendacion |
|---|---|---|---|
| Reparar y analizar Excel de clientes | Ausente | grep Excel/openpyxl solo muestra docs/antecedentes | Crear contrato `SpreadsheetIngestionService` antes de features. |
| Automatizar tareas administrativas | Parcial | action proposal/decision/execution internos | Exponer workflow con confirmacion humana y adaptadores no destructivos. |
| Interpretar stock, ventas, compras, pagos | Parcial bajo reconciliacion generica | `app/core/reconciliation/service.py` | Definir modelos de dominio y fixtures por vertical. |
| Leer documentacion masiva trazable | Parcial | `DocumentIngestionService`, JSONL evidence | Batch ingestion + EvidenceRepository + retrieval MCP. |
| Reconciliar fuentes distribuidas | Parcial | `reconcile_csv_sources`, amount reconciliation | Integrar canonical rows/entity resolution antes de multi-fuente. |
| Hallazgos accionables con entidad/diferencia/fuente | Parcial real | `HallazgoEngine`, tests de reconciliacion | Persistencia durable y lifecycle MCP. |
| Pedir clarificaciones ante incertidumbre | Implementado minimo | clarifications SQLite + MCP tools | Filtrar por owner/job y conectar a pipeline de reconciliacion. |
| Recomendar acciones sin ejecutar sin humano | Parcial correcto | action services con guardas | Mantener fail-closed y registrar decision/evidencia. |

## RIESGOS_DE_DERIVA

- Confundir documentacion o `docs/archive/**` con runtime real.
- Tratar `factory/hallazgos/**` como cola activa pese a que los docs canonicos dicen que la cola activa es `factory/ai_governance/tasks/*.yaml`.
- Seguir agregando tests/features sin contrato de entorno, aumentando `NO_VALIDADO`.
- Duplicar bridges MCP (`mcp_smartpyme_bridge.py`, `factory/mcp_bridge/*`, `factory/local_mcp_server.py`) sin una etiqueta operacional clara.
- Mezclar `findings` tecnico legado y `hallazgos` de negocio sin contrato de lifecycle.
- Saltar de CSV/reconciliacion a RAG/Excel sin cerrar EvidenceRepository y canonical rows.

## ROADMAP_DIARIO_PROPUESTO_12_HITOS

1. Cerrar entorno canonico Python. Objetivo producto: que todo avance sea verificable. Archivos probables: `pyproject.toml`, `docs/factory/PYTHON_ENVIRONMENT_CONTRACT.md`, `scripts/check_python_environment.sh`. Exito: `python`, `pytest`, `ruff`, `polars` disponibles o bloqueo documentado.
2. Reparar coleccion de tests sin cambiar negocio. Objetivo producto: baseline QA. Archivos probables: `tests/**`, config pytest. Exito: `pytest --collect-only` sin errores.
3. Separar tests legacy/factory de core. Objetivo producto: evitar falsos rojos. Archivos probables: pytest config, `tests/factory/**`. Exito: suites `core`, `factory`, `e2e` ejecutables por separado.
4. Declarar bridge MCP unico. Objetivo producto: borde estable Hermes-SmartPyme. Archivos probables: `docs/HERMES_MCP_RUNTIME.md`, `factory/mcp_bridge/README.md`. Exito: tabla de runtimes con uno marcado producto.
5. EvidenceRepository local. Objetivo producto: trazabilidad consultable. Archivos probables: `app/repositories/evidence_repository.py`, tests. Exito: CRUD/filtros por `evidence_id`, `source_id`, `job_id`.
6. Tool MCP de busqueda documental. Objetivo producto: consultar documentos con citas. Archivos probables: `mcp_smartpyme_bridge.py`, `services/document_query_service.py`, tests e2e. Exito: query devuelve chunks, score, source y clarification si baja confianza.
7. Batch ingestion controlada. Objetivo producto: documentacion masiva. Archivos probables: `services/document_ingestion_service.py`, tests. Exito: lote idempotente con errores por archivo y resumen.
8. Contrato CSV/Excel inicial. Objetivo producto: entrada de clientes PyME. Archivos probables: nuevo servicio spreadsheet, tests fixture. Exito: CSV y XLSX simple producen filas canonicas o bloqueo por dependencia.
9. Canonical rows desde evidencia. Objetivo producto: normalizar antes de comparar. Archivos probables: `app/services/canonicalization_service.py`, repositorios, tests. Exito: evidence -> canonical rows con validacion.
10. Entity resolution con incertidumbre. Objetivo producto: reconciliar fuentes distribuidas. Archivos probables: `entity_resolution_service.py`, `clarification_service.py`, tests. Exito: match exacto, ambiguo y bloqueante con clarification.
11. Persistencia durable de hallazgos. Objetivo producto: hallazgos accionables auditables. Archivos probables: `app/core/repositories/hallazgo_repository.py`, SQLite impl, tests. Exito: guardar/listar/transicionar estado con evidencia.
12. Action workflow no destructivo por MCP. Objetivo producto: recomendar sin ejecutar sin humano. Archivos probables: action services, MCP bridge, tests. Exito: propuesta -> decision humana -> ejecucion mock registrada.

## PREGUNTAS_PARA_GPT_DIRECTOR

- Confirmar si el siguiente ciclo debe ser entorno canonico o limpieza de tests; ambos bloquean validacion, pero entorno es prerequisito.
- Definir si `factory/mcp_bridge/*` queda como herramienta local o se archiva como runtime historico.
- Decidir si `factory/agent_min` debe existir o si sus tests se consideran legacy.
- Priorizar Excel antes de RAG robusto solo si el owner confirma que spreadsheets son el primer valor comercial.
- Definir naming canonico entre `findings` tecnico y `hallazgos` de negocio.

## HALLAZGOS_TECNICOS

- Ruta: `mcp_smartpyme_bridge.py`. Evidencia: lines 19-279 en `mcp_bridge_source.txt`. Hallazgo: bridge real existe, pero depende de `mcp` no instalado en `.venv`. Recomendacion: declarar dependencia y test e2e importable.
- Ruta: `services/document_ingestion_service.py`. Evidencia: `document_ingestion_source.txt`. Hallazgo: ingesta sobrescribe JSONL al escribir (`open("w")`) y opera por archivo/lote simple. Recomendacion: decidir append/idempotencia antes de batch masivo.
- Ruta: `services/retrieval_service.py`. Evidencia: `retrieval_source.txt`. Hallazgo: retrieval no persiste indice y depende opcionalmente de LangChain no acreditado. Recomendacion: EvidenceRepository + BM25 local cerrado antes de embeddings.
- Ruta: `app/services/fact_extraction_service.py`. Evidencia: regex amount/date/CUIT en salida inspeccionada. Hallazgo: extraccion real es deterministica simple. Recomendacion: no venderla como interpretacion documental completa.
- Ruta: `app/services/entity_resolution_service.py`. Evidencia: match por atributo `value`. Hallazgo: ER es basico y no cubre entidades distribuidas complejas. Recomendacion: agregar scoring/clarifications antes de multi-fuente.
- Ruta: `app/core/reconciliation/service.py`. Evidencia: CSV y amount reconciliation. Hallazgo: capa de reconciliacion es la mas madura, pero no esta conectada end-to-end al bridge. Recomendacion: exponerla solo despues de canonical rows.
- Ruta: `tests/**`. Evidencia: `pytest_venv.txt`. Hallazgo: suite completo no colecta. Recomendacion: arreglar dependencias/modulos o aislar legacy.
- Ruta: `factory/control/**`. Evidencia: `git_status.txt`. Hallazgo: cambios preexistentes fuera de alcance. Recomendacion: no aprobar auditoria como `CORRECTO` hasta separar/explicar esos cambios.
