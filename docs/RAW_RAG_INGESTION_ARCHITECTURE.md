# RAW/RAG ingestion architecture para SmartPyme

## Veredicto de adaptacion

El material RAG auxiliar aporta buenas reglas de ingestion, metadata, retrieval y anti-alucinacion, pero no gobierna SmartPyme. SmartPyme mantiene su arquitectura:

`Hermes Agent -> MCP Bridge -> SmartPyme OS -> Jobs / Evidence / Clarifications -> Hallazgos`

La adaptacion correcta es local y progresiva: fortalecer EvidenceStore actual antes de pensar en Supabase, Storage externo o vector DB.

## Flujo SmartPyme

```text
RAW document
-> RawDocument
-> DocumentRecord
-> EvidenceChunk
-> RetrievalResult
-> ExtractedFactCandidate
-> CanonicalRowCandidate
-> Entity Resolution
-> Reconciliacion
-> Hallazgos
```

## Diferencias obligatorias

| concepto | que es | que no es | estado actual |
|---|---|---|---|
| Documento original | Archivo recibido tal como llega al sistema. | No es evidencia atomica ni fact. | Pendiente como registry formal. |
| RawDocument | Registro local del documento original con hash SHA-256 de archivo, ruta, job, plan y metadata. | No contiene interpretacion de negocio. | Implementado minimo en SQLite. |
| DocumentRecord | Resultado parseado del documento. | No es chunk recuperable por si solo. | Parcial via `SourceDocument`. |
| EvidenceChunk | Fragmento recuperable con texto, pagina y metadata. | No es fact de negocio validado. | Parcial via `DocumentChunk`. |
| Evidence / evidence_id | Identificador trazable de un chunk usado como prueba. | No es conclusion ni hallazgo. | Implementado como `chunk_id`. |
| RetrievalResult | Resultado de busqueda sobre evidencia. | No crea facts. | Parcial via `RetrievalHit`. |
| ExtractedFactCandidate | Candidato estructurado extraido desde evidencia. | No es fila canonica ni dato final. | Pendiente. |
| CanonicalRowCandidate | Fila normalizada candidata para comparacion. | No debe reconciliar entidades ambiguas. | Pendiente. |

## Reglas

1. RAG recupera evidencia, no crea facts.
2. LLM no genera facts sin schema validable.
3. Todo fact candidate debe apuntar a `evidence_id`.
4. Aritmetica y reconciliacion van por core deterministico.
5. Si falta evidencia suficiente, se responde con fallback y se genera clarification si aplica.
6. No hay hallazgo sin diferencia cuantificada.
7. No hay accion sin confirmacion.
8. Hermes conversa y llama MCP; SmartPyme persiste y decide estados.

## Flujo operativo con Hermes

1. Hermes recibe pedido del duenio.
2. Hermes llama `mcp_smartpyme_create_job` si hay objetivo operativo.
3. Hermes llama `mcp_smartpyme_ingest_document` para documentos locales.
4. SmartPyme registra `RawDocument` en SQLite antes de parsear.
5. SmartPyme guarda `DocumentRecord` y `EvidenceChunk` en EvidenceStore local.
6. Hermes puede pedir evidencia puntual con `mcp_smartpyme_get_evidence`.
7. En fases futuras, SmartPyme recuperara evidencia por texto/metadata y propondra fact candidates.
8. SmartPyme bloqueara ante incertidumbre usando clarifications.

## Que queda local ahora

- Jobs SQLite.
- Clarifications SQLite.
- RawDocument registry SQLite (`SMARTPYME_RAW_DOCUMENTS_DB`).
- EvidenceStore JSONL.
- Raw documents JSONL.
- Chunks JSONL.
- Citation index JSON.
- Retrieval lexical/BM25 opcional en memoria.

## Que queda para despues

| destino futuro | que iria ahi | condicion previa |
|---|---|---|
| Supabase | registros normalizados, jobs, documentos, hallazgos, auditoria | interfaces locales estables |
| Storage | documentos originales binarios | RawDocument registry local y reglas de retencion cerradas |
| Vector DB | embeddings de EvidenceChunk | retrieval local y metadata contract cerrados |
| Reranker | reordenamiento top-k | queries y metricas reales |
| Embeddings | busqueda semantica | corpus limpio y hashes idempotentes |

## Adaptacion del material RAG

| elemento auxiliar | decision SmartPyme |
|---|---|
| Docling/OCR | Mantener como parser/fallback, ya existe base parcial. |
| Metadata | Incorporar progresivamente con hash de archivo y tipo documental. |
| Chunking | Mantener actual, formalizar EvidenceChunk. |
| Chroma/Qdrant | No ahora; fase futura despues de EvidenceRepository local. |
| Streamlit/FastAPI | No aplica al runtime actual Hermes/MCP. |
| Grounded prompting | Convertir en reglas anti-alucinacion y validacion de citas. |
| Auditor financiero | Adaptar como core deterministico: reconciliation y hallazgos. |
| LangChain/LangGraph/CrewAI | No incorporar como dependencia obligatoria. |
