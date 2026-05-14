-- SmartPyme - SAFE rollback (STAGING DESIGN)
-- MODE: DESIGN_ONLY / NO_APPLY
-- CRITICAL WARNING:
-- This rollback is intentionally SAFE and keeps anon closed.
-- Do NOT restore broad anon/authenticated DML by default.

BEGIN;

-- 1) Drop hardening policies
DROP POLICY IF EXISTS p_clientes_sel_tenant ON public.clientes;

DROP POLICY IF EXISTS p_jobs_sel_tenant ON public.jobs;
DROP POLICY IF EXISTS p_jobs_ins_tenant ON public.jobs;
DROP POLICY IF EXISTS p_jobs_upd_tenant ON public.jobs;
DROP POLICY IF EXISTS p_jobs_del_tenant ON public.jobs;

DROP POLICY IF EXISTS p_operational_cases_sel_tenant ON public.operational_cases;
DROP POLICY IF EXISTS p_operational_cases_ins_tenant ON public.operational_cases;
DROP POLICY IF EXISTS p_operational_cases_upd_tenant ON public.operational_cases;
DROP POLICY IF EXISTS p_operational_cases_del_tenant ON public.operational_cases;

DROP POLICY IF EXISTS p_reports_sel_tenant ON public.reports;
DROP POLICY IF EXISTS p_reports_ins_tenant ON public.reports;
DROP POLICY IF EXISTS p_reports_upd_tenant ON public.reports;
DROP POLICY IF EXISTS p_reports_del_tenant ON public.reports;

DROP POLICY IF EXISTS p_decisions_sel_tenant ON public.decisions;
DROP POLICY IF EXISTS p_decisions_ins_tenant ON public.decisions;
DROP POLICY IF EXISTS p_decisions_upd_tenant ON public.decisions;
DROP POLICY IF EXISTS p_decisions_del_tenant ON public.decisions;

DROP POLICY IF EXISTS p_evidence_candidates_sel_tenant ON public.evidence_candidates;
DROP POLICY IF EXISTS p_evidence_candidates_ins_tenant ON public.evidence_candidates;
DROP POLICY IF EXISTS p_evidence_candidates_upd_tenant ON public.evidence_candidates;
DROP POLICY IF EXISTS p_evidence_candidates_del_tenant ON public.evidence_candidates;

DROP POLICY IF EXISTS p_curated_evidence_sel_tenant ON public.curated_evidence;
DROP POLICY IF EXISTS p_curated_evidence_ins_tenant ON public.curated_evidence;
DROP POLICY IF EXISTS p_curated_evidence_upd_tenant ON public.curated_evidence;
DROP POLICY IF EXISTS p_curated_evidence_del_tenant ON public.curated_evidence;

-- 2) Keep RLS + FORCE ON (fail-closed)
ALTER TABLE public.clientes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.operational_cases ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.decisions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.evidence_candidates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.curated_evidence ENABLE ROW LEVEL SECURITY;

ALTER TABLE public.clientes FORCE ROW LEVEL SECURITY;
ALTER TABLE public.jobs FORCE ROW LEVEL SECURITY;
ALTER TABLE public.operational_cases FORCE ROW LEVEL SECURITY;
ALTER TABLE public.reports FORCE ROW LEVEL SECURITY;
ALTER TABLE public.decisions FORCE ROW LEVEL SECURITY;
ALTER TABLE public.evidence_candidates FORCE ROW LEVEL SECURITY;
ALTER TABLE public.curated_evidence FORCE ROW LEVEL SECURITY;

-- 3) Restore only secure minimum grants (not broad defaults)
REVOKE ALL ON TABLE
  public.clientes,
  public.jobs,
  public.operational_cases,
  public.reports,
  public.decisions,
  public.evidence_candidates,
  public.curated_evidence
FROM anon;

REVOKE ALL ON TABLE
  public.clientes,
  public.jobs,
  public.operational_cases,
  public.reports,
  public.decisions,
  public.evidence_candidates,
  public.curated_evidence
FROM authenticated;

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE
  public.clientes,
  public.jobs,
  public.operational_cases,
  public.reports,
  public.decisions,
  public.evidence_candidates,
  public.curated_evidence
TO service_role;

GRANT SELECT ON TABLE public.clientes TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE
  public.jobs,
  public.operational_cases,
  public.reports,
  public.decisions,
  public.evidence_candidates,
  public.curated_evidence
TO authenticated;

-- 4) Drop helper
DROP FUNCTION IF EXISTS public.request_tenant_key();

-- Optional UNSAFE rollback block (commented):
-- WARNING: Reopens critical multi-tenant risk.
-- ALTER TABLE public.curated_evidence DISABLE ROW LEVEL SECURITY;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE
--   public.clientes, public.jobs, public.operational_cases, public.reports,
--   public.decisions, public.evidence_candidates, public.curated_evidence
-- TO anon, authenticated;

COMMIT;
