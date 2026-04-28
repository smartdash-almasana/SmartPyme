# Rate Limits and Costs — SmartPyme Factory

## Política

La factoría debe evitar tormentas de retry y gasto no controlado.

## Límites iniciales

```yaml
cost_governance:
  monthly_token_budget:
    codex: 5000000
    gemini: 10000000
    gpt_director: 1000000
  global_circuit_breaker:
    max_audit_failures_per_hour: 10
    on_trip: PAUSE_FACTORY_AND_NOTIFY_OWNER
    cooldown_minutes: 60
  retry_policy:
    same_taskspec_max_attempts: 3
    after_3_failures: ESCALATE_TO_DIRECTOR
    diff_progress_required: true
```

## Activación

`factory/control/circuit_breaker.py` implementa la base local.
