-- SMARTGRAPH_SCHEMA_V0.sql
-- SmartPyme SmartGraph baseline schema (SQL/Supabase oriented)
-- Scope: node/edge/alias/claim with tenant isolation and epistemic traceability

create extension if not exists pgcrypto;

create table if not exists smartgraph_nodes (
    id uuid primary key default gen_random_uuid(),
    tenant_id uuid not null,
    node_type text not null,
    canonical_key text not null,
    label text not null,
    description text null,
    source_table text null,
    source_id uuid null,
    status text not null default 'ACTIVE',
    confidence numeric null check (confidence is null or (confidence >= 0 and confidence <= 1)),
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique (tenant_id, node_type, canonical_key)
);

create table if not exists smartgraph_edges (
    id uuid primary key default gen_random_uuid(),
    tenant_id uuid not null,
    from_node_id uuid not null references smartgraph_nodes(id) on delete restrict,
    to_node_id uuid not null references smartgraph_nodes(id) on delete restrict,
    edge_type text not null,
    claim_type text not null,
    confidence numeric null check (confidence is null or (confidence >= 0 and confidence <= 1)),
    evidence_ids uuid[] not null default '{}',
    source_table text null,
    source_id uuid null,
    valid_from timestamptz null,
    valid_until timestamptz null,
    observed_at timestamptz null,
    status text not null default 'ACTIVE',
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    check (from_node_id <> to_node_id)
);

create table if not exists smartgraph_aliases (
    id uuid primary key default gen_random_uuid(),
    tenant_id uuid not null,
    node_id uuid not null references smartgraph_nodes(id) on delete cascade,
    alias text not null,
    alias_normalized text not null,
    language text null,
    source_table text null,
    source_id uuid null,
    confidence numeric null check (confidence is null or (confidence >= 0 and confidence <= 1)),
    status text not null default 'ACTIVE',
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique (tenant_id, node_id, alias_normalized)
);

create table if not exists smartgraph_claims (
    id uuid primary key default gen_random_uuid(),
    tenant_id uuid not null,
    claim_type text not null,
    claim_status text not null,
    statement text not null,
    subject_node_id uuid null references smartgraph_nodes(id) on delete set null,
    object_node_id uuid null references smartgraph_nodes(id) on delete set null,
    edge_id uuid null references smartgraph_edges(id) on delete set null,
    confidence numeric null check (confidence is null or (confidence >= 0 and confidence <= 1)),
    evidence_ids uuid[] not null default '{}',
    requires_human_review boolean not null default false,
    reviewed_by text null,
    reviewed_at timestamptz null,
    review_decision text null,
    valid_from timestamptz null,
    valid_until timestamptz null,
    observed_at timestamptz null,
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index if not exists idx_sg_nodes_tenant on smartgraph_nodes (tenant_id);
create index if not exists idx_sg_edges_tenant on smartgraph_edges (tenant_id);
create index if not exists idx_sg_aliases_tenant on smartgraph_aliases (tenant_id);
create index if not exists idx_sg_claims_tenant on smartgraph_claims (tenant_id);
create index if not exists idx_sg_aliases_norm on smartgraph_aliases (tenant_id, alias_normalized);
create index if not exists idx_sg_claims_status on smartgraph_claims (tenant_id, claim_status);

-- NOTE:
-- 1) No LLM direct writes: enforced at application/service boundary.
-- 2) Human-review gating for SUPPORTED claims is enforced by repository/service logic.
-- 3) Graphify is not a runtime dependency of this schema.
