# Evidence Pipeline Runtime Map

**Fecha:** 2026-05-12  
**Rama:** product/laboratorio-mvp-vendible  
**Propósito:** Documentar el pipeline operacional REAL actualmente observable del producto.

---

## 1. ENTRYPOINTS

El runtime expone los siguientes puntos de entrada operacionales:

### 1.1 Telegram Webhook
- **Path:** `/webhook/telegram` (POST)
- **Router:** `app/api/telegram_webhook_router.py`
- **Adapter:** `app/adapters/telegram_adapter.py`
- **Función:** Recibe updates de Telegram y delega al adapter para procesamiento

### 1.2 BEM Webhook (Curated Evidence)
- **Paths:**
  - `/webhooks/bem` (POST) — recibe evidencia curada
  - `/webhooks/bem/{tenant_id}` (GET) — lista evidencia por tenant
  - `/webhooks/bem/{tenant_id}/{evidence_id}` (GET) — detalle de evidencia
- **Router:** `app/api/bem_webhook_router.py`
- **Adapter:** `app/services/bem_curated_evidence_adapter.py`
- **Repository:** `app/repositories/curated_evidence_repository.py`

### 1.3 BEM Submit
- **Path:** `/bem/submit` (POST)
- **Router:** `app/api/bem_submit_router.py`
- **Service:** `app/services/bem_submit_service.py`
- **Client:** `app/services/bem_client.py`
- **Función:** Envía payloads a BEM y registra runs en `data/bem_runs.db`

### 1.4 Diagnostic Router
- **Paths:**
  - `/diagnostico/{tenant_id}/informe` (GET) — informe Markdown exportable
  - `/diagnostico/{tenant_id}` (GET) — JSON con findings
- **Router:** `app/api/diagnostic_router.py`
- **Service:** `app/services/basic_operational_diagnostic_service.py`
- **Builder:** `app/services/markdown_diagnostic_report_builder.py`

### 1.5 API v1 Endpoints
- **Process:** `/process` (POST) — ejecuta pipeline de texto a texto
- **Findings:** endpoints de hallazgos
- **Formulas:** cálculo de fórmulas
- **Jobs:** gestión de trabajos
- **Pathologies:** patologías operacionales
- **Router:** `app/api/v1/api.py`

### 1.6 MCP Tools (Control Plane)
- **Directorio:** `app/mcp/tools/`
- **Funciones:**
  - `list_factory_queue()` — lista cola operativa
  - `get_next_factory_task()` — obtiene próxima tarea pendiente
- **Nota:** MCP es CONTROL_PLANE, acoplado temporalmente a factory adapters

---

## 2. INGESTION FLOW

Flujo de ingestión documental observable:

### 2.1 Upload
- **Service:** `services/document_ingestion_service.py`
- **Método:** `ingest_pdfs(pdf_paths: list[Path])`
- **Evidence Root:** `evidence_store/` (configurable)

### 2.2 Parsing
- **Componente:** `extraction/docling_parser.py`
- **Función:** `parse_pdf(pdf_path: Path) -> SourceDocument`
- **Estrategia:**
  1. Docling (primary)
  2. OCR fallback (`extraction/ocr_fallback.py`)
  3. Plain text fallback
- **Metadata:** `extraction/metadata_extractor.py`

### 2.3 Extraction
- **Componente:** `extraction/` como SHARED_RUNTIME_COMPONENTS
- **Archivos:**
  - `docling_parser.py` — parseo estructurado
  - `chunker.py` — división en chunks recuperables
  - `metadata_extractor.py` — extracción de metadatos
  - `ocr_fallback.py` — fallback OCR

### 2.4 Chunking
- **Componente:** `extraction/chunker.py`
- **Función:** `split_document(document: SourceDocument) -> list[DocumentChunk]`
- **Estrategia:**
  - LangChain RecursiveCharacterTextSplitter (primary)
  - Fixed window fallback (secundario)
- **Configuración default:** chunk_size=800, chunk_overlap=120

### 2.5 Normalization
- **Modelos:** `models/document_models.py`
  - `SourceDocument` — documento fuente canonical
  - `DocumentChunk` — fragmento atómico recuperable
  - `EvidenceRef` — puntero de citación
  - `RetrievalHit` — candidato recuperado con confianza
  - `DocumentQuery` — consulta documental
  - `DocumentIngestionResult` — resultado de ingestión

---

## 3. EVIDENCE FLOW

Flujo de evidencia desde ingreso hasta persistencia:

### 3.1 Curated Evidence
- **Contract:** `app/contracts/bem_payloads.py`
  - `CuratedEvidenceRecord` — registro de evidencia curada
- **Adapter:** `app/services/bem_curated_evidence_adapter.py`
  - `build_curated_evidence(tenant_id, payload)` — construye record
- **Repository:** `app/repositories/curated_evidence_repository.py`
  - Backend SQLite en `data/curated_evidence.db`
  - Métodos: `create()`, `list_by_tenant()`, `get_by_evidence_id()`

### 3.2 Persistence
- **Evidence Store Structure:**
  ```
  evidence_store/
  ├── raw_documents/
  │   └── documents.jsonl
  ├── document_chunks/
  │   └── chunks.jsonl
  ├── citation_index/
  │   └── citations.json
  └── vector_index/
      └── (opcional)
  ```

### 3.3 Contracts & DTOs
- **Contratos principales:**
  - `app/contracts/evidence_contract.py`
  - `app/contracts/bem_evidence_contract.py`
  - `app/contracts/bem_payloads.py`
- **Payloads:**
  - `CuratedEvidenceRecord` — evidencia curada con tenant_id, evidence_id, kind, payload, trace_id, received_at
  - `BemRun` — registro de ejecución BEM

### 3.4 Retrieval
- **Service:** `services/retrieval_service.py`
- **Clases:**
  - `RetrievalService` — servicio de recuperación
  - `VectorIndex` — índice vectorial (opcional)
- **Métodos:**
  - `add_chunks(chunks)` — agrega chunks al índice
  - `retrieve(query, k)` — recupera k chunks relevantes

---

## 4. DIAGNOSTIC FLOW

Flujo de diagnóstico operacional:

### 4.1 Operational Rules
- **Service:** `app/services/basic_operational_diagnostic_service.py`
- **Características:**
  - Sin IA, sin LLM, sin embeddings, sin graph
  - Solo reglas explícitas
  - Determinístico, fail-closed
- **Reglas implementadas:**
  - `VENTA_BAJO_COSTO` — precio_venta < costo_unitario (HIGH)
  - `RENTABILIDAD_NULA` — precio_venta == costo_unitario (HIGH)
  - (otras reglas según evidencia)

### 4.2 Diagnosis Execution
- **Service:** `BasicOperationalDiagnosticService`
- **Método:** `build_report(tenant_id: str) -> dict`
- **Proceso:**
  1. Obtiene evidencia del tenant via repository
  2. Aplica reglas explícitas a cada payload
  3. Genera findings con severidad
  4. Retorna reporte estructurado

### 4.3 Findings Generation
- **Core:** `app/core/findings/`
  - `models.py` — modelos de findings
  - `service.py` — servicio de findings
- **Modules:** `app/modules/findings_engine.py`
- **Contracts:** `app/contracts/diagnostic_report.py`

### 4.4 Reports/Artifacts
- **Builder:** `app/services/markdown_diagnostic_report_builder.py`
  - `build_markdown_report(report: dict) -> str`
- **Output:** Markdown exportable con Content-Disposition header
- **Filename:** `diagnostico-{tenant_id}.md`

---

## 5. SHARED RUNTIME COMPONENTS

Componentes compartidos que son parte del runtime operacional:

### 5.1 extraction/*

**NO es AI_RESEARCH experimental.** Es runtime operacional de ingestión en el hot path del producto.

#### 5.1.1 parse_pdf (`extraction/docling_parser.py`)
- **Función:** `parse_pdf(pdf_path: Path) -> SourceDocument`
- **Uso:** Hot path de ingestión documental
- **Dependencias:** Docling (primary), OCR fallback, plain text fallback
- **Estado:** Operacional, consolidado, parte del runtime

#### 5.1.2 split_document (`extraction/chunker.py`)
- **Función:** `split_document(document: SourceDocument) -> list[DocumentChunk]`
- **Uso:** División de documentos en chunks recuperables
- **Estrategia:** LangChain (primary), fixed window (fallback)
- **Estado:** Operacional, consolidado, parte del runtime

#### 5.1.3 metadata_extractor (`extraction/metadata_extractor.py`)
- **Función:** `build_document_metadata(pdf_path, text) -> dict`
- **Uso:** Extracción de metadatos para trazabilidad

#### 5.1.4 ocr_fallback (`extraction/ocr_fallback.py`)
- **Función:** `run_ocr_fallback(pdf_path: Path) -> str`
- **Uso:** Fallback cuando Docling no extrae texto

### 5.2 models/document_models.py
- **Propósito:** Modelos canónicos del dominio documental
- **Clases:** `SourceDocument`, `DocumentChunk`, `EvidenceRef`, `RetrievalHit`, `DocumentQuery`, `DocumentIngestionResult`
- **Estado:** Runtime consolidado

### 5.3 services/document_ingestion_service.py
- **Propósito:** Orquestación de parsing, chunking, persistencia e indexación
- **Método:** `ingest_pdfs(pdf_paths: list[Path]) -> DocumentIngestionResult`
- **Dependencias:** `extraction/parse_pdf`, `extraction/split_document`
- **Estado:** Runtime operacional activo

---

## 6. OUTPUT ARTIFACTS

Productos generados por el pipeline:

### 6.1 Telegram Responses
- **Formato:** Dict JSON sanitizado
- **Router:** `app/api/telegram_webhook_router.py`
- **Sanitización:** Bloquea tokens, api_keys, secrets, passwords

### 6.2 Reports
- **Formato:** Markdown exportable
- **Endpoint:** `/diagnostico/{tenant_id}/informe`
- **Content-Type:** `text/markdown`
- **Header:** `Content-Disposition: attachment; filename="diagnostico-{tenant_id}.md"`

### 6.3 Evidence Payloads
- **Formato:** JSON curado
- **Contract:** `CuratedEvidenceRecord`
- **Campos:** tenant_id, evidence_id, kind, payload, trace_id, received_at
- **Persistencia:** SQLite `data/curated_evidence.db`

### 6.4 Diagnosis Artifacts
- **Formato:** JSON estructurado
- **Contenido:** findings, evidence_count, severidades
- **Endpoint:** `/diagnostico/{tenant_id}`
- **Severidades:** LOW, MEDIUM, HIGH

### 6.5 BEM Run Records
- **Persistencia:** SQLite `data/bem_runs.db`
- **Repository:** `app/repositories/bem_run_repository.py`
- **Campos:** tenant_id, run_id, workflow_id, status, timestamps

---

## 7. DIRECTORIO RUNTIME OBSERVABLE

### 7.1 PRODUCT_RUNTIME
```
app/
├── api/                  # Routers HTTP (Telegram, BEM, Diagnostic, v1)
├── core/                 # Pipeline, findings, hallazgos, validación
├── services/             # Servicios operacionales (diagnosis, findings, bem)
├── repositories/         # Repositorios SQLite (evidence, runs, facts, entities)
├── contracts/            # Contratos y payloads (bem_payloads, evidence_contract)
├── adapters/             # Adapters (telegram, bem_curated_evidence)
├── modules/              # Módulos (findings_engine)
└── mcp/                  # CONTROL_PLANE (tools de inspección de cola)
```

### 7.2 SHARED_RUNTIME_COMPONENTS
```
extraction/
├── docling_parser.py     # parse_pdf — runtime operacional
├── chunker.py            # split_document — runtime operacional
├── metadata_extractor.py # build_document_metadata
└── ocr_fallback.py       # run_ocr_fallback

services/
├── document_ingestion_service.py  # Orquestador de ingestión
├── document_query_service.py      # Consultas documentales
└── retrieval_service.py           # Recuperación de chunks

models/
└── document_models.py    # Modelos canónicos documentales
```

### 7.3 CONTROL_PLANE
```
app/mcp/tools/
├── queue_list_tool.py    # list_factory_queue, get_next_factory_task
└── ...                   # (otras tools de control)
```

---

## 8. POLÍTICA ACTUAL DE BOUNDARIES

1. **No nuevas contaminaciones:** PRODUCT_RUNTIME no puede importar de factory*, experiments*
2. **Deuda explícita:** `app/mcp/*` está excepcionado como CONTROL_PLANE temporal
3. **Shared runtime reconocido:** `extraction/*` es componente operacional, no experimental
4. **Boundaries auditables:** Script `scripts/guard_product_boundaries.py` verifica enforcement

### Clasificación de Dependencias

| Categoría | Patrones | Tratamiento |
|-----------|----------|-------------|
| FORBIDDEN_DEPENDENCIES | `factory*`, `factory_v2*`, `factory_v3*`, `experiments*` | Bloqueado — contaminación prohibida |
| TECHNICAL_DEBT_EXCEPTIONS | `app/mcp/*` | Permitido — deuda técnica explícita (CONTROL_PLANE) |
| SHARED_RUNTIME_COMPONENTS | `extraction/*` | Permitido — runtime operacional consolidado |

---

## 9. RATIONALE DE CLASIFICACIÓN

### Por qué extraction/* es SHARED_RUNTIME_COMPONENTS

- `parse_pdf` y `split_document` están en el **hot path** de ingestión
- Son usados por `DocumentIngestionService` en producción
- No son experimentos de AI_RESEARCH
- Son componentes funcionales del runtime de producto
- Su remoción o movimiento rompería el pipeline operacional

### Por qué app/mcp/* es TECHNICAL_DEBT_EXCEPTIONS

- MCP es **CONTROL_PLANE**, no PRODUCT_RUNTIME puro
- Está acoplado a `factory.adapters.app_bridge.*` por diseño temporal
- No es contaminación accidental — es arquitectura deliberada transitoria
- Requiere refactor futuro para desacoplar, pero mientras tanto está excepcionado
- No debe tratarse como simple violación — tiene rationale arquitectónico

### Diferencia entre categorías

| Aspecto | Factory Contamination | Technical Debt | Shared Runtime |
|---------|----------------------|----------------|----------------|
| Origen | Import accidental/no autorizado | Acoplamiento deliberado temporal | Componente funcional consolidado |
| Tratamiento | Bloquear | Excepcionar con tracking | Reconocer como runtime |
| Acción futura | Corregir | Refactor planificado | Mantener estable |
| Ejemplo | `from factory_v3.*` | `app/mcp → factory.adapters` | `services → extraction` |

---

**Fin del documento.**
