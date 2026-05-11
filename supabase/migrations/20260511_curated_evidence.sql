-- curated_evidence
-- Persistencia soberana de CuratedEvidenceRecord para flujo BEM/diagnóstico.
-- Multi-tenant obligatorio por tenant_id.

create table if not exists public.curated_evidence (
  id uuid primary key default gen_random_uuid(),
  tenant_id text not null,
  evidence_id text not null,
  kind text not null,
  payload jsonb not null,
  source_metadata jsonb not null,
  received_at timestamptz not null,
  created_at timestamptz not null default now(),
  unique (tenant_id, evidence_id)
);

create index if not exists idx_curated_evidence_tenant_received_at
  on public.curated_evidence (tenant_id, received_at desc);

