-- SmartGraph Schema V0
-- Fecha: 2026-05-09
-- Estado: draft versionable / no ejecutar automáticamente
-- Relación: docs/architecture/SMARTGRAPH_SCHEMA_MINIMO_NODE_EDGE.md
--
-- Propósito:
--   Definir una primera forma SQL/Supabase-compatible para la memoria estructural SmartGraph.
--
-- Regla crítica:
--   Este archivo NO habilita escritura directa del LLM.
--   Toda escritura futura debe pasar por servicios/repositorios determinísticos.

-- ============================================================
-- Extensions
-- ============================================================

create extension if not exists pgcrypto;

-- ============================================================
-- smartgraph_nodes
-- ============================================================

create table if not exists smartgraph_nodes (
  id uuid primary key default gen_random_uuid(),

  tenant_id uuid not null,

  node_type text not null,
  canonical_key text not null,
  label text not null,
  description text,

  source_table text,
  source_id uuid,

  status text not null default 'ACTIVE',
  confidence numeric,

  metadata jsonb not null default '{}'::jsonb,

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),

  constraint smartgraph_nodes_confidence_range
    check (confidence is null or (confidence >= 0 and confidence <= 1)),

  constraint smartgraph_nodes_status_check
    check (status in ('ACTIVE', 'INACTIVE', 'DEPRECATED', 'ARCHIVED')),

  constraint smartgraph_nodes_node_type_not_blank
    check (length(trim(node_type)) > 0),

  constraint smartgraph_nodes_canonical_key_not_blank
    check (length(trim(canonical_key)) > 0),

  constraint smartgraph_nodes_label_not_blank
    check (length(trim(label)) > 0),

  constraint smartgraph_nodes_unique_canonical
    unique (tenant_id, node_type, canonical_key)
);

create index if not exists idx_smartgraph_nodes_tenant
  on smartgraph_nodes (tenant_id);

create index if not exists idx_smartgraph_nodes_type
  on smartgraph_nodes (tenant_id, node_type);

create index if not exists idx_smartgraph_nodes_source
  on smartgraph_nodes (tenant_id, source_table, source_id);

-- ============================================================
-- smartgraph_edges
-- ============================================================

create table if not exists smartgraph_edges (
  id uuid primary key default gen_random_uuid(),

  tenant_id uuid not null,

  from_node_id uuid not null references smartgraph_nodes(id) on delete cascade,
  to_node_id uuid not null references smartgraph_nodes(id) on delete cascade,

  edge_type text not null,
  claim_type text not null,
  confidence numeric,

  valid_from timestamptz,
  valid_until timestamptz,
  observed_at timestamptz,

  source_table text,
  source_id uuid,

  evidence_ids uuid[] not null default '{}',

  status text not null default 'ACTIVE',
  metadata jsonb not null default '{}'::jsonb,

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),

  constraint smartgraph_edges_confidence_range
    check (confidence is null or (confidence >= 0 and confidence <= 1)),

  constraint smartgraph_edges_claim_type_check
    check (claim_type in ('EXTRACTED', 'INFERRED', 'AMBIGUOUS', 'HYPOTHESIS', 'VALIDATED')),

  constraint smartgraph_edges_status_check
    check (status in ('ACTIVE', 'INACTIVE', 'DEPRECATED', 'ARCHIVED', 'REJECTED')),

  constraint smartgraph_edges_edge_type_not_blank
    check (length(trim(edge_type)) > 0),

  constraint smartgraph_edges_no_self_edge
    check (from_node_id <> to_node_id),

  constraint smartgraph_edges_valid_interval
    check (valid_until is null or valid_from is null or valid_until >= valid_from)
);

create index if not exists idx_smartgraph_edges_tenant
  on smartgraph_edges (tenant_id);

create index if not exists idx_smartgraph_edges_from
  on smartgraph_edges (tenant_id, from_node_id);

create index if not exists idx_smartgraph_edges_to
  on smartgraph_edges (tenant_id, to_node_id);

create index if not exists idx_smartgraph_edges_type
  on smartgraph_edges (tenant_id, edge_type);

create index if not exists idx_smartgraph_edges_claim_type
  on smartgraph_edges (tenant_id, claim_type);

create index if not exists idx_smartgraph_edges_source
  on smartgraph_edges (tenant_id, source_table, source_id);

-- ============================================================
-- smartgraph_aliases
-- ============================================================

create table if not exists smartgraph_aliases (
  id uuid primary key default gen_random_uuid(),

  tenant_id uuid not null,
  node_id uuid not null references smartgraph_nodes(id) on delete cascade,

  alias text not null,
  alias_normalized text not null,
  language text,

  source_table text,
  source_id uuid,
  confidence numeric,

  status text not null default 'ACTIVE',
  metadata jsonb not null default '{}'::jsonb,

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),

  constraint smartgraph_aliases_confidence_range
    check (confidence is null or (confidence >= 0 and confidence <= 1)),

  constraint smartgraph_aliases_status_check
    check (status in ('ACTIVE', 'INACTIVE', 'DEPRECATED', 'ARCHIVED', 'REJECTED')),

  constraint smartgraph_aliases_alias_not_blank
    check (length(trim(alias)) > 0),

  constraint smartgraph_aliases_alias_normalized_not_blank
    check (length(trim(alias_normalized)) > 0),

  constraint smartgraph_aliases_unique_alias
    unique (tenant_id, alias_normalized, node_id)
);

create index if not exists idx_smartgraph_aliases_tenant
  on smartgraph_aliases (tenant_id);

create index if not exists idx_smartgraph_aliases_node
  on smartgraph_aliases (tenant_id, node_id);

create index if not exists idx_smartgraph_aliases_alias_normalized
  on smartgraph_aliases (tenant_id, alias_normalized);

-- ============================================================
-- smartgraph_claims
-- ============================================================

create table if not exists smartgraph_claims (
  id uuid primary key default gen_random_uuid(),

  tenant_id uuid not null,
  claim_type text not null,
  claim_status text not null,

  subject_node_id uuid references smartgraph_nodes(id) on delete set null,
  object_node_id uuid references smartgraph_nodes(id) on delete set null,
  edge_id uuid references smartgraph_edges(id) on delete set null,

  statement text not null,
  confidence numeric,

  evidence_ids uuid[] not null default '{}',

  requires_human_review boolean not null default false,
  reviewed_by text,
  reviewed_at timestamptz,
  review_decision text,

  valid_from timestamptz,
  valid_until timestamptz,
  observed_at timestamptz,

  metadata jsonb not null default '{}'::jsonb,

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),

  constraint smartgraph_claims_confidence_range
    check (confidence is null or (confidence >= 0 and confidence <= 1)),

  constraint smartgraph_claims_claim_type_check
    check (claim_type in ('EXTRACTED', 'INFERRED', 'AMBIGUOUS', 'HYPOTHESIS', 'VALIDATED')),

  constraint smartgraph_claims_status_check
    check (claim_status in ('CANDIDATE', 'ACTIVE', 'SUPPORTED', 'REJECTED', 'DEPRECATED', 'BLOCKED')),

  constraint smartgraph_claims_statement_not_blank
    check (length(trim(statement)) > 0),

  constraint smartgraph_claims_valid_interval
    check (valid_until is null or valid_from is null or valid_until >= valid_from),

  constraint smartgraph_claims_review_consistency
    check (
      (reviewed_at is null and review_decision is null)
      or
      (reviewed_at is not null and review_decision is not null)
    )
);

create index if not exists idx_smartgraph_claims_tenant
  on smartgraph_claims (tenant_id);

create index if not exists idx_smartgraph_claims_type_status
  on smartgraph_claims (tenant_id, claim_type, claim_status);

create index if not exists idx_smartgraph_claims_subject
  on smartgraph_claims (tenant_id, subject_node_id);

create index if not exists idx_smartgraph_claims_object
  on smartgraph_claims (tenant_id, object_node_id);

create index if not exists idx_smartgraph_claims_edge
  on smartgraph_claims (tenant_id, edge_id);

-- ============================================================
-- Notes
-- ============================================================

-- Futuro posible:
--   1. triggers updated_at
--   2. RLS por tenant_id
--   3. enums SQL para node_type / edge_type
--   4. tablas de exportación graph.json
--   5. repository port SmartGraph
--   6. tests contract-first
