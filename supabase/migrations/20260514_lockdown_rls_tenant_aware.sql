-- SmartPyme - Supabase RLS hardening (STAGING DESIGN)
-- MODE: DESIGN_ONLY / NO_APPLY
-- Identity contract:
--   1) JWT app_metadata.tenant_id = canonical claim
--   2) JWT app_metadata.cliente_id = legacy fallback (temporary)
--   3) No claim => deny

BEGIN;

-- 0) Helper: canonical tenant resolver (tenant_id first, cliente_id fallback)
CREATE OR REPLACE FUNCTION public.request_tenant_key()
RETURNS text
LANGUAGE sql
STABLE
AS $$
  SELECT COALESCE(
    NULLIF(auth.jwt() ->> 'tenant_id', ''),
    NULLIF(auth.jwt() ->> 'cliente_id', '')
  );
$$;

-- 1) Revoke broad access first
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

-- 2) Grants (minimum secure operational profile)
-- anon: closed
-- service_role: full backend operations
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE
  public.clientes,
  public.jobs,
  public.operational_cases,
  public.reports,
  public.decisions,
  public.evidence_candidates,
  public.curated_evidence
TO service_role;

-- authenticated:
-- clientes = SELECT only (coherent with policy set)
GRANT SELECT ON TABLE public.clientes TO authenticated;

-- tenant-scoped operational tables
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE
  public.jobs,
  public.operational_cases,
  public.reports,
  public.decisions,
  public.evidence_candidates,
  public.curated_evidence
TO authenticated;

-- If app later requires editar cliente:
-- GRANT UPDATE ON TABLE public.clientes TO authenticated;
-- plus add UPDATE policy for clientes.

-- 3) Ensure RLS enabled in all 7 tables
ALTER TABLE public.clientes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.operational_cases ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.decisions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.evidence_candidates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.curated_evidence ENABLE ROW LEVEL SECURITY;

-- 4) Cleanup prior policy names (idempotent)
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

-- 5) Policies

-- clientes: SELECT only for authenticated tenant
CREATE POLICY p_clientes_sel_tenant ON public.clientes
  FOR SELECT TO authenticated
  USING (cliente_id = public.request_tenant_key());

-- jobs
CREATE POLICY p_jobs_sel_tenant ON public.jobs
  FOR SELECT TO authenticated
  USING (cliente_id = public.request_tenant_key());
CREATE POLICY p_jobs_ins_tenant ON public.jobs
  FOR INSERT TO authenticated
  WITH CHECK (cliente_id = public.request_tenant_key());
CREATE POLICY p_jobs_upd_tenant ON public.jobs
  FOR UPDATE TO authenticated
  USING (cliente_id = public.request_tenant_key())
  WITH CHECK (cliente_id = public.request_tenant_key());
CREATE POLICY p_jobs_del_tenant ON public.jobs
  FOR DELETE TO authenticated
  USING (cliente_id = public.request_tenant_key());

-- operational_cases
CREATE POLICY p_operational_cases_sel_tenant ON public.operational_cases
  FOR SELECT TO authenticated
  USING (cliente_id = public.request_tenant_key());
CREATE POLICY p_operational_cases_ins_tenant ON public.operational_cases
  FOR INSERT TO authenticated
  WITH CHECK (cliente_id = public.request_tenant_key());
CREATE POLICY p_operational_cases_upd_tenant ON public.operational_cases
  FOR UPDATE TO authenticated
  USING (cliente_id = public.request_tenant_key())
  WITH CHECK (cliente_id = public.request_tenant_key());
CREATE POLICY p_operational_cases_del_tenant ON public.operational_cases
  FOR DELETE TO authenticated
  USING (cliente_id = public.request_tenant_key());

-- reports
CREATE POLICY p_reports_sel_tenant ON public.reports
  FOR SELECT TO authenticated
  USING (cliente_id = public.request_tenant_key());
CREATE POLICY p_reports_ins_tenant ON public.reports
  FOR INSERT TO authenticated
  WITH CHECK (cliente_id = public.request_tenant_key());
CREATE POLICY p_reports_upd_tenant ON public.reports
  FOR UPDATE TO authenticated
  USING (cliente_id = public.request_tenant_key())
  WITH CHECK (cliente_id = public.request_tenant_key());
CREATE POLICY p_reports_del_tenant ON public.reports
  FOR DELETE TO authenticated
  USING (cliente_id = public.request_tenant_key());

-- decisions
CREATE POLICY p_decisions_sel_tenant ON public.decisions
  FOR SELECT TO authenticated
  USING (cliente_id = public.request_tenant_key());
CREATE POLICY p_decisions_ins_tenant ON public.decisions
  FOR INSERT TO authenticated
  WITH CHECK (cliente_id = public.request_tenant_key());
CREATE POLICY p_decisions_upd_tenant ON public.decisions
  FOR UPDATE TO authenticated
  USING (cliente_id = public.request_tenant_key())
  WITH CHECK (cliente_id = public.request_tenant_key());
CREATE POLICY p_decisions_del_tenant ON public.decisions
  FOR DELETE TO authenticated
  USING (cliente_id = public.request_tenant_key());

-- evidence_candidates
CREATE POLICY p_evidence_candidates_sel_tenant ON public.evidence_candidates
  FOR SELECT TO authenticated
  USING (cliente_id = public.request_tenant_key());
CREATE POLICY p_evidence_candidates_ins_tenant ON public.evidence_candidates
  FOR INSERT TO authenticated
  WITH CHECK (cliente_id = public.request_tenant_key());
CREATE POLICY p_evidence_candidates_upd_tenant ON public.evidence_candidates
  FOR UPDATE TO authenticated
  USING (cliente_id = public.request_tenant_key())
  WITH CHECK (cliente_id = public.request_tenant_key());
CREATE POLICY p_evidence_candidates_del_tenant ON public.evidence_candidates
  FOR DELETE TO authenticated
  USING (cliente_id = public.request_tenant_key());

-- curated_evidence: tenant_id-based
CREATE POLICY p_curated_evidence_sel_tenant ON public.curated_evidence
  FOR SELECT TO authenticated
  USING (tenant_id = public.request_tenant_key());
CREATE POLICY p_curated_evidence_ins_tenant ON public.curated_evidence
  FOR INSERT TO authenticated
  WITH CHECK (tenant_id = public.request_tenant_key());
CREATE POLICY p_curated_evidence_upd_tenant ON public.curated_evidence
  FOR UPDATE TO authenticated
  USING (tenant_id = public.request_tenant_key())
  WITH CHECK (tenant_id = public.request_tenant_key());
CREATE POLICY p_curated_evidence_del_tenant ON public.curated_evidence
  FOR DELETE TO authenticated
  USING (tenant_id = public.request_tenant_key());

-- 6) FORCE RLS in all 7 tables
ALTER TABLE public.clientes FORCE ROW LEVEL SECURITY;
ALTER TABLE public.jobs FORCE ROW LEVEL SECURITY;
ALTER TABLE public.operational_cases FORCE ROW LEVEL SECURITY;
ALTER TABLE public.reports FORCE ROW LEVEL SECURITY;
ALTER TABLE public.decisions FORCE ROW LEVEL SECURITY;
ALTER TABLE public.evidence_candidates FORCE ROW LEVEL SECURITY;
ALTER TABLE public.curated_evidence FORCE ROW LEVEL SECURITY;

COMMIT;
