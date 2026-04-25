# RAG retrieval plan SmartPyme

## Estado actual

SmartPyme recupera evidencia principalmente por `evidence_id` mediante `mcp_smartpyme_get_evidence`, leyendo `EvidenceStore` JSONL. La ingesta actual genera chunks y citation index local.

Tambien existe `RetrievalService`, con BM25 de LangChain si esta disponible y fallback por solapamiento de tokens en memoria. No esta expuesto por MCP.

## Retrieval actual

| modo | estado | archivo | observacion |
|---|---|---|---|
| Por `evidence_id` | implemented | `mcp_smartpyme_bridge.py` | Lee `document_chunks/chunks.jsonl`. |
| Citation index | partial | `services/document_ingestion_service.py` | Genera `citation_index/citations.json`. |
| Texto en memoria | partial | `services/retrieval_service.py` | No persiste indice. |
| Metadata filter | pending | no evidenciado | Requiere metadata contract. |
| Embeddings | pending | protocolo `VectorIndex` | No hay adapter concreto. |
| Reranking | pending | no evidenciado | Futuro. |

## Busqueda futura por texto

1. Cargar EvidenceChunks desde repository local.
2. Filtrar por `job_id`, `plan_id` y metadata si existen.
3. Buscar por texto con BM25/fallback local.
4. Devolver `RetrievalResult` con `evidence_id`, score y cita.
5. Si score insuficiente, devolver fallback de evidencia insuficiente.

## Busqueda futura por metadata

Filtros previstos:

- `job_id`
- `plan_id`
- `cliente_id`
- fecha o periodo
- tipo de documento
- filename
- page
- file_hash_sha256 / source_hash
- entity_type cuando exista canonical row

## Embeddings futuros

No se incorporan Chroma/Qdrant ahora. Orden correcto:

1. EvidenceRepository local.
2. Metadata y hash estables.
3. Retrieval local por texto/metadata.
4. Metricas de recall sobre consultas reales.
5. Adapter de embeddings.
6. Vector DB local.
7. Supabase/Storage/vector adapter si hace falta.

## Reranking futuro

Reranking solo aplica cuando:

- ya existe retrieval local estable;
- hay mas de un candidato relevante;
- hay set de evaluacion con citas esperadas;
- el costo/latencia esta medido.

## Fallback por evidencia insuficiente

Respuesta canonica:

`No tengo evidencia documental suficiente para responder con certeza.`

Accion:

- Si la falta de evidencia bloquea una decision, crear clarification.
- Si es consulta exploratoria, devolver vacio trazable sin inventar.

## Limites anti-alucinacion

- El LLM puede resumir evidencia recuperada.
- El LLM no crea facts sin schema validable.
- El LLM no hace aritmetica.
- La suma, diferencia, conciliacion y severidad van por core deterministico.
- Toda afirmacion factica debe tener cita.
- Si no hay cita, no se acepta como output final.

## Validacion de citas

Cada respuesta grounded debe poder reconstruirse desde:

- `evidence_id`
- `filename`
- `page`
- `excerpt`
- `source_id` o `document_id`
- `job_id` y `plan_id` cuando existan

Un output sin cita o con cita no recuperable debe bloquearse o derivar a clarification.
