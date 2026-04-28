# Auditoría del Blueprint "SmartPyme Factory v2.0"

**Auditor**: Arquitecto Senior — Sistemas Agénticos · Contratos · Documentación Empresarial
**Artefacto auditado**: Blueprint v2.0 + Prompt de Implementación "Bootstrap SmartPyme Factory v2.0" enviado por el Owner.
**Estado base**: Reporte previo (`SMARTPYME_AUDITORIA_DOCUMENTAL.md`, hallazgos F-001…F-045).
**Resultado**: Aceptable como **dirección estratégica**. **Inadmisible** como prompt ejecutable sin las correcciones marcadas.

---

## 1. Veredicto Ejecutivo (≤300 palabras)

El blueprint **acierta en la dirección** (runtime único = Hermes Gateway externo, doble agente Codex/Gemini bajo TaskSpec, supervisión humana por Telegram, schemas formales, observabilidad mínima). Resuelve estructuralmente F-001 (runtimes contradictorios), F-005/F-007 (Gemini Builder obsoleto), F-013 (TaskSpec con comandos shell), F-029 (schemas BuildReport/AuditReport), F-038 (idempotencia Telegram).

Pero introduce **doce defectos técnicos concretos** que harían fallar el bootstrap o invalidarían la seguridad del sistema:

1. **Endpoint MCP HTTP inexistente** — el bridge real es FastMCP **stdio** (`mcp_smartpyme_bridge.py:289 mcp.run()`). El blueprint declara `endpoint: "http://localhost:8080/mcp"`. Hermes nunca conectará.
2. **Sexto vocabulario de veredictos** — añade `BUILD_SUCCESS/FAILED/BLOCKED` y `AUDIT_PASSED/REJECTED/BLOCKED/INCOMPLETE` sin reconciliar con los cinco previos.
3. **HMAC en `callback_data` excede 64 bytes** — Telegram rechaza el botón.
4. **`tenant_id`** reintroduce divergencia con `cliente_id` (F-019/F-033).
5. **Variable substitution `${TELEGRAM_BOT_TOKEN}` en YAML** no es estándar — Hermes recibe el literal.
6. **`PYTHONPATH=/opt/.../SmartPyme`** en systemd contradice `docs/HERMES_VM_SETUP.md` y crea shadowing de imports.
7. **Orden de fases invertido** — Phase 1 levanta systemd antes de que existan skills/contratos; el servicio arranca en vacío.
8. **Sin máquina de estados de recuperación** — crash mid-build deja TaskSpec huérfano.
9. **Sin migración de las 21 TaskSpecs vigentes** ni los 5 hallazgos pending.
10. **`max_tokens: 128000` y `session_ttl: 3600`** son números arbitrarios sin justificación; cortos para ciclos reales.
11. **Sin contrato de rollback / canary / release versioning** post-merge.
12. **Sin política de costos/circuit-breaker global** ante retry storms.

**Riesgo si se ejecuta tal cual**: ALTO. El servicio levantará pero Hermes no podrá hablar con el bridge MCP, los botones Telegram fallarán por overflow de `callback_data`, y los crashes dejarán la cola corrupta. **Recomendación**: aplicar las correcciones de §3 antes de iniciar Phase 1.

---

## 2. Lo que el blueprint hace bien (preservar)

| Tema | Fortaleza | Mantener |
|---|---|---|
| Runtime único | Designa Hermes Gateway como único orquestador | Sí, alineado con FACTORY_CONTRATO_OPERATIVO.md v3 |
| Schemas formales | `taskspec.schema.json` v2, `build_report.schema.json`, `audit_report.schema.json` | Sí, F-029 cerrado |
| Roles separados | Codex=Builder, Gemini=Auditor, GPT=Director | Sí, alineado con AGENTS.md jerarquía 1-6 |
| Verification commands | `acceptance_criteria` con `verification_command` y `expected_output_pattern` | Sí, F-037 cerrado |
| Telegram allowlist | `from_user.id` (no solo `chat_id`) | Sí, F-032 parcialmente cerrado |
| Estados explícitos | PENDING → ASSIGNED → BUILDING → WAITING_AUDIT → AUDITING → CLOSED | Sí, mejor que ambigüedad previa |
| Observabilidad mínima | Eventos JSON estructurados + métricas Prometheus-like | Sí, F-034 abordado |
| Phased rollout | 6 fases con dependencias declaradas | Sí, pero reordenar (ver §3.7) |

---

## 3. Hallazgos críticos del Blueprint

### B-001 · MCP transport: HTTP inexistente
**Severidad**: CRÍTICA

El blueprint configura:
```yaml
mcp:
  smartpyme_bridge:
    endpoint: "http://localhost:8080/mcp"
    timeout: 30
    retry: 3
```

Pero el bridge real (`mcp_smartpyme_bridge.py:288-289`) declara explícitamente:
```python
# El servidor corre por defecto en modo stdio para ser consumido por Hermes
mcp.run()
```

`FastMCP("SmartPyme-Bridge").run()` por defecto lanza **stdio** (no HTTP). `docs/HERMES_MCP_RUNTIME.md` confirma:
```yaml
mcp_servers:
  smartpyme:
    enabled: true
    command: "C:/Python314/python.exe"
    args:
      - "...mcp_smartpyme_bridge.py"
```

**Es un servidor stdio que Hermes lanza como subproceso**, no un servicio HTTP escuchando en :8080.

**Corrección obligatoria**:
```yaml
mcp:
  servers:
    smartpyme:
      transport: "stdio"
      command: "/opt/smartpyme-factory/repos/SmartPyme/.venv/bin/python"
      args:
        - "/opt/smartpyme-factory/repos/SmartPyme/mcp_smartpyme_bridge.py"
      env:
        SMARTPYME_REPO: "/opt/smartpyme-factory/repos/SmartPyme"
      timeout_seconds: 30
      restart_on_crash: true
```

Si quieren HTTP, hay que **implementar el bridge HTTP primero** (no es trivial, FastMCP soporta HTTP/SSE pero requiere `mcp.run(transport="sse")` o equivalente y reverse proxy).

---

### B-002 · Sexto vocabulario de veredictos
**Severidad**: ALTA (recreación de F-012)

El blueprint introduce:
- Builder: `BUILD_SUCCESS | BUILD_FAILED | BUILD_BLOCKED`
- Auditor: `AUDIT_PASSED | AUDIT_REJECTED | AUDIT_BLOCKED | AUDIT_INCOMPLETE`

Pero no mapea contra:
- `AGENTS.md/CODEX.md`: `CORRECTO | NO_VALIDADO | BLOCKED | INCOMPLETO`
- `auditor_rules.yaml`: `VALIDADO | NO_VALIDADO | BLOCKED`
- `gpt_director_auditor.yaml`: `APPROVED | REJECTED | BLOCKED | NO_VALIDADO`

**Resultado**: F-012 se reabre, ahora con seis dialectos en vez de cinco.

**Corrección obligatoria** — crear `factory/ai_governance/contracts/verdict_enum.yaml` con un único enum por capa y mapeos explícitos:

```yaml
verdict_enum:
  version: "1.0.0"
  layers:
    builder:
      success: "BUILD_SUCCESS"
      failure: "BUILD_FAILED"
      blocked: "BUILD_BLOCKED"
      incomplete: "BUILD_INCOMPLETE"
    auditor:
      success: "AUDIT_PASSED"
      failure: "AUDIT_REJECTED"
      blocked: "AUDIT_BLOCKED"
      incomplete: "AUDIT_INCOMPLETE"
    director:
      approve: "APPROVED"
      reject: "REJECTED"
      block: "BLOCKED"
      defer: "NEEDS_REVIEW"
  cross_layer_mapping:
    AUDIT_PASSED: { equivalent_to: ["VALIDADO", "CORRECTO"] }
    AUDIT_REJECTED: { equivalent_to: ["NO_VALIDADO", "REJECTED"] }
    AUDIT_BLOCKED: { equivalent_to: ["BLOCKED"] }
  deprecated:
    - "FALLÓ"
    - "OK"
    - "NO_VALIDADO"
```

Toda la documentación previa debe refactorizarse en una sola TaskSpec antes de que la factoría arranque.

---

### B-003 · `callback_data` excede 64 bytes con HMAC
**Severidad**: CRÍTICA

El blueprint propone:
> Callback encoding: `cycle_id|action|nonce|hmac`

Telegram **límite duro**: `callback_data` ≤ **64 bytes UTF-8**.

Cuenta realista: 36+3+8+8+64 = **119 bytes** → Telegram responde HTTP 400 `BUTTON_DATA_INVALID`.

**Corrección obligatoria** — server-side token table:

1. Generar `callback_id = secrets.token_urlsafe(16)`.
2. Guardar `(callback_id, cycle_id, action, expires_at, hmac)` en SQLite local.
3. Enviar solo `callback_id` en `callback_data`.
4. Validar al recibir.

---

### B-004 · `tenant_id` vs `cliente_id` — divergencia naming reintroducida
**Severidad**: ALTA (recreación de F-019/F-033)

Blueprint:
```yaml
tenant_id: "smartpyme-core"
```

Código real:
```python
cliente_id: str
```

**Decisión obligatoria antes de Phase 2**: elegir uno y refactorizar todo. Recomendación: usar **`cliente_id`** y eliminar `tenant_id` del blueprint.

---

### B-005 · Variable substitution en YAML
**Severidad**: ALTA

YAML **no expande variables** automáticamente. Sin loader o `envsubst`, Hermes recibe el string literal `"${TELEGRAM_BOT_TOKEN}"`.

**Corrección obligatoria**: usar `envsubst` en el bootstrap o loader Python documentado.

---

### B-006 · `PYTHONPATH` colisión
**Severidad**: ALTA

Blueprint:
```ini
Environment="PYTHONPATH=/opt/smartpyme-factory/repos/SmartPyme"
```

**Corrección obligatoria**: quitar `PYTHONPATH` del unit file. Instalar SmartPyme por `pip install -e` en el venv de Hermes.

---

### B-007 · Orden de fases inverso
**Severidad**: ALTA

Phase 1 arranca systemd antes de que existan skills/contratos/handlers, causando restart loop.

Orden corregido:

| Phase | Contenido |
|---|---|
| 1 | Pre-flight & limpieza |
| 2 | Contratos y schemas |
| 3 | Skills y prompts |
| 4 | Adaptadores internos |
| 5 | Tests y validación local |
| 6 | Infra/systemd y bootstrap script |
| 7 | Documentación de operación + observabilidad |

---

### B-008 · Máquina de estados sin recovery
**Severidad**: ALTA

Faltan timeouts, retry limits, ABANDONED, ESCALATED, CANCELLED y watchdog.

---

### B-009 · Sin migración de TaskSpecs existentes ni hallazgos
**Severidad**: ALTA

Sin migración, las 21 TaskSpecs v1 no validan contra schema v2 y la cola se queda vacía.

---

### B-010 · `max_tokens` y `session_ttl` arbitrarios
**Severidad**: MEDIA

Falta `docs/AGENT_CONTEXT_BUDGET.md` con números y políticas reales.

---

### B-011 · Sin contrato de release / rollback / canary
**Severidad**: ALTA

Crear `docs/RELEASE_CONTRACT.md` con SemVer, tag obligatorio, changelog, rollback y feature flags.

---

### B-012 · Sin política de costos / circuit breaker
**Severidad**: ALTA

Crear `docs/RATE_LIMITS_AND_COSTS.md` con presupuestos y circuit breaker.

---

## 4. Hallazgos secundarios B-013…B-030

- B-013: `runtime.target_agent` confunde skill con agente.
- B-014: allowlist con dos identidades (`chat_id` y `user_id`).
- B-015: Telegram MarkdownV2 sin escape automático.
- B-016: sin DR/backup de SQLite.
- B-017: `hermes gateway start --skills-path` sin verificar.
- B-018: concurrencia indefinida.
- B-019: `runtime_mode: production` desde día 1.
- B-020: docs operativas demasiado tarde.
- B-021: sin contrato de logs estructurados.
- B-022: `taskspec_version: 2.0.0` sin compat matrix.
- B-023: `tenant_id: smartpyme-core` no es tenant.
- B-024: sin separación dev/test/prod en config.
- B-025: bootstrap requiere dependencias sin instalación.
- B-026: comandos Telegram nuevos sin TaskSpec.
- B-027: `/auditar` ambiguo.
- B-028: wizard `/nueva_tarea` no especificado.
- B-029: sin migración legacy.
- B-030: acceptance criteria mezcla modelos de validación.

---

## 5. Plan de Remediación del Blueprint

### Phase 0 — Pre-flight obligatoria

- Archivar legacy definitivo.
- Tag de rollback.
- Migración TaskSpec v1 → v2 con dry-run.
- Decidir `cliente_id` vs `tenant_id`.
- Decidir `app/core/` vs `core/`.
- Crear `verdict_enum.yaml`.

### Phase 1 — Contratos y schemas

- `taskspec.schema.json`
- `build_report.schema.json`
- `audit_report.schema.json`
- `gateway_to_smartpyme.schema.json`
- `state_machine.schema.json`
- `HERMES_GATEWAY_API_CONTRACT.md`
- `TELEGRAM_WEBHOOK_CONTRACT.md`
- `MULTI_TENANT_ISOLATION_CONTRACT.md`
- `AGENT_CONTEXT_BUDGET.md`
- `RATE_LIMITS_AND_COSTS.md`
- `RELEASE_CONTRACT.md`
- `DR_AND_BACKUP_CONTRACT.md`
- `SECURITY_CONTRACT.md`
- `OBSERVABILITY_CONTRACT.md`
- `MCP_TOOLS_CONTRACT.md`

### Phase 2 — Skills y prompts

Actualizar skills y prompts para vocabulario unificado, runtime Hermes y edge cases Telegram.

### Phase 3 — Adaptadores internos

- `telegram_handler.py`
- `telegram_escape.py`
- `heartbeat.py`
- `circuit_breaker.py`
- `factory/hermes_control_cli.py`
- `factory/telegram_notify.py`
- partición por `cliente_id`

### Phase 4 — Tests

- Telegram handler.
- Hermes control CLI.
- TaskSpec validation.
- State machine recovery.
- dry_run e2e.
- circuit breaker.
- backup/restore.
- contract tests.

### Phase 7 — Activación gradual

| # | Acción |
|---|---|
| 7.1 | Activar Hermes en modo `dry_run` durante 24h con TaskSpec sintética |
| 7.2 | Activar primer ciclo real con tarea P3 |
| 7.3 | Monitor 7 días |
| 7.4 | Escalar a P0/P1 |

---

## 6. Checklist de Verificación del Blueprint Refinado

### Coherencia interna

- [ ] No contiene `${VAR}` sin loader.
- [ ] Vocabulario de veredictos único.
- [ ] Un solo término: `cliente_id` o `tenant_id`.
- [ ] MCP transport declarado como `stdio`.
- [ ] `callback_data` ≤64 bytes verificable.
- [ ] State machine cubre recovery.
- [ ] Phase ordering correcto.

### Coherencia con repo actual

- [ ] `mcp_smartpyme_bridge.py` confirma stdio.
- [ ] `app/contracts/operational_plan_contract.py` y blueprint usan mismo nombre.
- [ ] Unit file no usa `PYTHONPATH`.
- [ ] 21 TaskSpecs v1 tienen migración o deprecación.
- [ ] `factory/hallazgos/` resuelto.

### Cobertura previa

- [ ] F-001/F-003/F-004/F-009/F-010/F-040/F-041 cerrados.
- [ ] F-005/F-006/F-007 documentados.
- [ ] F-013/F-037 cubiertos.
- [ ] F-016/F-017/F-038 cubiertos.
- [ ] F-019 con plan ejecutable.
- [ ] F-026/F-027/F-028 con números reales.
- [ ] F-029 entregables.
- [ ] F-032 doc canónico.

### Operacional

- [ ] Modo `dry_run` testable end-to-end.
- [ ] Watchdog + heartbeat verificable.
- [ ] Circuit breaker simulable en test.
- [ ] Backup SQLite y restore probados.
- [ ] Rollback ensayado en pre-flight.

---

## 7. Veredicto Final

**Blueprint v2.0 original**: `NO_VALIDADO` para ejecución inmediata.

**Blueprint v2.1 refinado**: `APPROVED conditional` — listo solo para ejecución en modo `dry_run` durante 24h antes de producción.

**Recomendación al Owner**:

1. No iniciar Phase 1 del blueprint original.
2. Reescribir blueprint incorporando B-001 a B-030.
3. Ejecutar Phase 0 pre-flight primero.
4. Entrar a Phase 1 solo cuando Phase 0 esté validada.
5. Reservar activación para el final, en modo `dry_run` antes de Telegram real.

Cualquier ciclo cerrado como `CORRECTO` en producción antes de migración multi-tenant viola aislamiento entre pymes y expone al SaaS a fuga de datos cliente-cliente. No es aceptable lanzar a producción sin esa partición.

---

**Fin del reporte de auditoría del blueprint.**
