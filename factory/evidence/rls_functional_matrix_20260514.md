# RLS Functional Matrix 2026-05-14

- Project ref: `msfcjyssiaqegxbpkdai`
- Environment: `staging/dev`
- Method: `psql + SET LOCAL ROLE authenticated + request.jwt.claims`
- Executed at (UTC): `2026-05-14T19:56:03.505356+00:00`
- Verdict: **PASS**

## Results

| Test | Expected | Obtained | Status | Note |
|---|---|---|---|---|
| T1 jobs own INSERT | ALLOW | ALLOW | PASS |  |
| T2 jobs cross INSERT | DENY | DENY | PASS | ERROR:  new row violates row-level security policy for table "jobs" |
| T3 jobs cross SELECT count | 0 | 0 | PASS |  |
| T4 jobs UPDATE tenant change | DENY | DENY | PASS | ERROR:  new row violates row-level security policy for table "jobs" |
| T5 curated own INSERT | ALLOW | ALLOW | PASS |  |
| T6 curated cross INSERT | DENY | DENY | PASS | ERROR:  new row violates row-level security policy for table "curated_evidence" |
| T7 curated cross SELECT count | 0 | 0 | PASS |  |
| T8 no-claim INSERT deny | DENY | DENY | PASS | ERROR:  new row violates row-level security policy for table "jobs" |
| T9 cleanup | 0/0 | 0/0 | PASS |  |

## Temp Data

- Prefix: `rls_test_20260514_`
- Created job ids: `rls_test_20260514_job_own_cc9dd770, rls_test_20260514_job_cross_b3e4a104, rls_test_20260514_job_update_ebd325f1"
- Created evidence ids: `rls_test_20260514_ev_own_b6a82824, rls_test_20260514_ev_cross_b54b20e2"
- Cleanup verification counts: jobs=0, curated_evidence=0

## Safety Confirmation

- Auth modified: NO
- Schema modified: NO
- Public persistent test data: NO
- Production touched: NO
- Secrets printed: NO
