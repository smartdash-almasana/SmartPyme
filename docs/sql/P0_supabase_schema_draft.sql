-- NO EJECUTAR - DRAFT DE DISEÑO
-- SmartPyme P0 schema draft
-- Objetivo: tablas core P0 con aislamiento soberano por cliente_id
-- Nota: se usa TEXT para IDs funcionales para compatibilidad con contratos/repos actuales.

-- Extensión recomendada, si no existe:
-- create extension if not exists pgcrypto;

-- -------------------------------------------------------------------
-- utilitario updated_at
-- -------------------------------------------------------------------
create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

-- -------------------------------------------------------------------
-- clientes
-- -------------------------------------------------------------------
create table public.clientes (
  cliente_id text primary key,
  nombre text,
  status text not null default 'active',
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamz not null default now(),
  updated_at timestamptz not null default now(),
  check (length(trim(cliente_id)) > 0)
);

create trigger trg_clientes_updated_at
before update on public.clientes
for each row execute function public.set_updated_at();

-- -------------------------------------------------------------------
-- jobs
-- -------------------------------------------------------------------
create table public.jobs (
  cliente_id text not null,
  job_id text not null,
  job_type text not null,
  status text not null,
  payload jsonb not null default '{}'::jsonb,
  result jsonb,
  metadata jsonb not null default '{}'::jsonb,
  error_log text,
  traceable_origin jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  primary key (cliente_id, job_id),
  foreign key (cliente_id) references public.clientes (cliente_id) on delete restrict,
  check (length(trim(cliente_id)) > 0),
  check (length(trim(job_id)) > 0)
);

create trigger trg_jobs_updated_at
before update on public.jobs
for each row execute function public.set_updated_at();

-- -------------------------------------------------------------------
-- operational_cases
-- -------------------------------------------------------------------
create table public.operational_cases (
  cliente_id text not null,
  case_id text not null,
  job_id text,
  status text not null,
  payload jsonb not null default '{}'::jsonb,
  result jsonb,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  primary key (cliente_id, case_id),
  foreign key (cliente_id) references public.clientes (cliente_id) on delete restrict,
  foreign key (cliente_id, job_id) references public.jobs (cliente_id, job_id) on delete set null,
  check (length(trim(cliente_id)) > 0),
  check (length(trim(case_id)) > 0)
);

create trigger trg_operational_cases_updated_at
before update on public.operational_cases
for each row execute function public.set_updated_at();

-- -------------------------------------------------------------------
-- reports
-- -------------------------------------------------------------------
create table public.reports (
  cliente_id text not null,
  report_id text not null,
  case_id text,
  job_id text,
  status text not null default 'draft',
  payload jsonb not null default '{}'::jsonb,
  result jsonb,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  primary key (cliente_id, report_id),
  foreign key (cliente_id) references public.clientes (cliente_id) on delete restrict,
  foreign key (cliente_id, case_id) references public.operational_cases (cliente_id, case_id) on delete set null,
  foreign key (cliente_id, job_id) references public.jobs (cliente_id, job_id) on delete set null,
  check (length(trim(cliente_id)) > 0),
  check (length(trim(report_id)) > 0)
);

create trigger trg_reports_updated_at
before update on public.reports
for each row execute function public.set_updated_at();

-- -------------------------------------------------------------------
-- decisions
-- -------------------------------------------------------------------
create table public.decisions (
  cliente_id text not null,
  decision_id text not null,
  case_id text,
  report_id text,
  decision_type text not null,
  decision_value text,
  rationale jsonb not null default '{}'::jsonb,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  primary key (cliente_id, decision_id),
  foreign key (cliente_id) references public.clientes (cliente_id) on delete restrict,
  foreign key (cliente_id, case_id) references public.operational_cases (cliente_id, case_id) on delete set null,
  foreign key (cliente_id, report_id) references public.reports (cliente_id, report_id) on delete set null,
  check (length(trim(cliente_id)) > 0),
  check (length(trim(decision_id)) > 0)
);

create trigger trg_decisions_updated_at
before update on public.decisions
for each row execute function public.set_updated_at();

-- -------------------------------------------------------------------
-- evidence_candidates
-- -------------------------------------------------------------------
create table public.evidence_candidates (
  cliente_id text not null,
  evidence_id text not null,
  job_id text,
  case_id text,
  evidence_type text,
  payload jsonb not null default '{}'::jsonb,
  result jsonb,
  metadata jsonb not null default '{}'::jsonb,
  score numeric(6,5),
  status text not null default 'candidate',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  primary key (cliente_id, evidence_id),
  foreign key (cliente_id) references public.clientes (cliente_id) on delete restrict,
  foreign key (cliente_id, job_id) references public.jobs (cliente_id, job_id) on delete set null,
  foreign key (cliente_id, case_id) references public.operational_cases (cliente_id, case_id) on delete set null,
  check (length(trim(cliente_id)) > 0),
  check (length(trim(evidence_id)) > 0)
);

create trigger trg_evidence_candidates_updated_at
before update on public.evidence_candidates
for each row execute function public.set_updated_at();

-- -------------------------------------------------------------------
-- Índices P0
-- -------------------------------------------------------------------
create index idx_jobs_cliente_created_at on public.jobs (cliente_id, created_at desc);
create index idx_jobs_cliente_status on public.jobs (cliente_id, status);

create index idx_cases_cliente_created_at on public.operational_cases (cliente_id, created_at desc);
create index idx_cases_cliente_status on public.operational_cases (cliente_id, status);
create index idx_cases_cliente_job_id on public.operational_cases (cliente_id, job_id);

create index idx_reports_cliente_created_at on public.reports (cliente_id, created_at desc);
create index idx_reports_cliente_case_id on public.reports (cliente_id, case_id);
create index idx_reports_cliente_job_id on public.reports (cliente_id, job_id);

create index idx_decisions_cliente_created_at on public.decisions (cliente_id, created_at desc);
create index idx_decisions_cliente_report_id on public.decisions (cliente_id, report_id);
create index idx_decisions_cliente_case_id on public.decisions (cliente_id, case_id);

create index idx_evidence_cliente_created_at on public.evidence_candidates (cliente_id, created_at desc);
create index idx_evidence_cliente_job_id on public.evidence_candidates (cliente_id, job_id);
create index idx_evidence_cliente_case_id on public.evidence_candidates (cliente_id, case_id);
create index idx_evidence_payload_gin on public.evidence_candidates using gin (payload);
