# Evidence contract SmartPyme

## Proposito

Definir la frontera entre documento, evidencia recuperable, candidato de fact y fila canonica. Este documento no reemplaza el runtime actual; lo ordena para futuras implementaciones.

## Contratos

### RawDocument

| campo | detalle |
|---|---|
| proposito | Registrar el archivo original recibido. |
| campos minimos | `raw_document_id`, `file_path`, `filename`, `file_hash_sha256`, `size_bytes`, `mime_type`, `job_id`, `plan_id`, `source_id`, `metadata`, `created_at` |
| required fields | `raw_document_id`, `file_path`, `filename`, `file_hash_sha256`, `size_bytes`, `created_at` |
| relacion con job_id | Opcional pero recomendada para ingestas ligadas a un job. |
| relacion con plan_id | Opcional, heredada del OperationalPlanContract. |
| relacion con evidence_id | Uno a muchos: RawDocument produce EvidenceChunks. |
| estado actual | implemented minimo via `app/repositories/raw_document_registry.py` y SQLite local. |

Persistencia actual:

| campo SQLite | detalle |
|---|---|
| `raw_document_id` | ID estable derivado del hash: `raw_<sha256 corto>`. |
| `file_path` | Ruta absoluta del archivo original, sin copiarlo ni moverlo. |
| `file_hash_sha256` | Hash SHA-256 del archivo original, distinto del hash de texto extraido. |
| `metadata_json` | Metadata auxiliar serializada, sin interpretacion de negocio. |

### DocumentRecord

| campo | detalle |
|---|---|
| proposito | Representar el documento parseado y su metadata. |
| campos minimos | `document_id`, `raw_document_id`, `job_id`, `plan_id`, `filename`, `parser`, `text_hash`, `page_count`, `metadata` |
| required fields | `document_id`, `raw_document_id`, `filename`, `parser`, `text_hash` |
| relacion con job_id | Debe conservar el job si existe. |
| relacion con plan_id | Debe conservar el plan si existe. |
| relacion con evidence_id | Uno a muchos: un DocumentRecord genera EvidenceChunks. |
| estado actual | partial via `SourceDocument` |

### EvidenceChunk

| campo | detalle |
|---|---|
| proposito | Fragmento atomico recuperable y citable. |
| campos minimos | `evidence_id`, `document_id`, `raw_document_id`, `job_id`, `plan_id`, `filename`, `page`, `text`, `chunk_order`, `metadata` |
| required fields | `evidence_id`, `document_id`, `filename`, `page`, `text`, `chunk_order` |
| relacion con job_id | Filtrable por job cuando exista. |
| relacion con plan_id | Filtrable por plan cuando exista. |
| relacion con evidence_id | Es el identificador primario de evidencia. |
| estado actual | partial via `DocumentChunk.chunk_id` |

### RetrievalResult

| campo | detalle |
|---|---|
| proposito | Resultado de busqueda sobre EvidenceChunks. |
| campos minimos | `query_id`, `evidence_id`, `document_id`, `job_id`, `plan_id`, `score`, `text`, `citation`, `metadata` |
| required fields | `query_id`, `evidence_id`, `score`, `text`, `citation` |
| relacion con job_id | Debe permitir filtro por job. |
| relacion con plan_id | Debe permitir filtro por plan. |
| relacion con evidence_id | Apunta siempre a un EvidenceChunk. |
| estado actual | partial via `RetrievalHit` |

### ExtractedFactCandidate

| campo | detalle |
|---|---|
| proposito | Candidato de hecho estructurado extraido desde evidencia. |
| campos minimos | `fact_candidate_id`, `evidence_id`, `job_id`, `plan_id`, `schema_name`, `data`, `confidence`, `extraction_method`, `validation_status`, `errors` |
| required fields | `fact_candidate_id`, `evidence_id`, `schema_name`, `data`, `validation_status` |
| relacion con job_id | Obligatoria cuando el fact nace de un job. |
| relacion con plan_id | Obligatoria cuando el fact nace de un plan. |
| relacion con evidence_id | Obligatoria; no hay fact sin evidencia. |
| estado actual | pending |

### CanonicalRowCandidate

| campo | detalle |
|---|---|
| proposito | Fila normalizada candidata para entity resolution y reconciliacion. |
| campos minimos | `canonical_row_id`, `fact_candidate_id`, `evidence_id`, `job_id`, `plan_id`, `entity_type`, `row`, `validation_status`, `errors` |
| required fields | `canonical_row_id`, `fact_candidate_id`, `evidence_id`, `entity_type`, `row`, `validation_status` |
| relacion con job_id | Debe conservar trazabilidad operativa. |
| relacion con plan_id | Debe conservar trazabilidad del plan. |
| relacion con evidence_id | Hereda evidence_id del fact candidate. |
| estado actual | pending |

## Leyes

- No fact sin evidencia.
- No canonical row sin schema.
- No reconciliacion con entidades ambiguas.
- No hallazgo sin diferencia cuantificada.
- No respuesta grounded sin citas validables.
