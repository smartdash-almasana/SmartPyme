# SmartGraph — Schema Mínimo Node/Edge

## Objetivo
Definir el contrato mínimo de persistencia para SmartGraph sobre SQL/Supabase, compatible con adapters actuales.

## Node (smartgraph_nodes)
Campos mínimos:
- id (uuid, pk)
- tenant_id (uuid, not null)
- node_type (text, not null)
- canonical_key (text, not null)
- label (text, not null)
- description (text, null)
- source_table (text, null)
- source_id (uuid, null)
- status (text, not null, default ACTIVE)
- confidence (numeric, null, check 0..1)
- metadata (jsonb, not null default {})
- created_at (timestamptz, not null)
- updated_at (timestamptz, not null)

Restricción mínima:
- unique (tenant_id, node_type, canonical_key)

## Edge (smartgraph_edges)
Campos mínimos:
- id (uuid, pk)
- tenant_id (uuid, not null)
- from_node_id (uuid, not null)
- to_node_id (uuid, not null)
- edge_type (text, not null)
- claim_type (text, not null)
- confidence (numeric, null, check 0..1)
- evidence_ids (uuid[], not null default {})
- source_table (text, null)
- source_id (uuid, null)
- valid_from (timestamptz, null)
- valid_until (timestamptz, null)
- observed_at (timestamptz, null)
- status (text, not null, default ACTIVE)
- metadata (jsonb, not null default {})
- created_at (timestamptz, not null)
- updated_at (timestamptz, not null)

Reglas:
- from_node_id <> to_node_id
- FK tenant-safe por validación en aplicación + políticas SQL

## Alias (smartgraph_aliases)
Campos mínimos:
- id, tenant_id, node_id, alias, alias_normalized, language, confidence, status, metadata, created_at, updated_at
- unique (tenant_id, node_id, alias_normalized)

## Claim (smartgraph_claims)
Campos mínimos:
- id, tenant_id, claim_type, claim_status, statement
- subject_node_id, object_node_id, edge_id (opcionales)
- confidence (0..1), evidence_ids (uuid[])
- requires_human_review (bool)
- reviewed_by, reviewed_at, review_decision
- valid_from, valid_until, observed_at
- metadata, created_at, updated_at

Regla de gobernanza:
- `SUPPORTED` requiere evidencia o revisión humana para INFERRED/AMBIGUOUS/HYPOTHESIS.
- Si `requires_human_review=true`, entonces `SUPPORTED` requiere `reviewed_by` y `review_decision`.
