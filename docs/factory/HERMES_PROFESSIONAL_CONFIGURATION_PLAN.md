# HERMES PROFESSIONAL CONFIGURATION PLAN — SmartPyme

Estado: CANONICO v1

## 1. Estado actual

La factoria SmartPyme hoy opera sobre una arquitectura híbrida no profesional:

- Control por Telegram implementado con scripts Python custom
- Runner (`hermes_factory_runner.py`) actuando como orquestador
- Codex integrado como builder
- Gemini NO integrado como auditor real
- Skills de Hermes no formalizadas
- MCP no implementado como capa oficial

Consecuencia:

```text
Sistema funcional pero inestable, con gobernanza incompleta
```

---

## 2. Arquitectura objetivo (Hermes profesional)

```text
Owner (Telegram)
  → Hermes Gateway
  → SmartPyme Factory Skill
  → Guards (REPO_CLEAN + ENVIRONMENT)
  → Task Orchestrator
  → Codex Builder (subagente)
  → Gemini Auditor (subagente)
  → Evidence Layer
  → Human Audit Gate
```

---

## 3. Componentes requeridos

### 3.1 Hermes Core

- Configuracion central Hermes (`~/.hermes/config.yaml`)
- Context files del proyecto (`AGENTS.md`, `.hermes.md`)

### 3.2 Gateway

- Uso de gateway Hermes (Telegram)
- Eliminación progresiva del bot casero

### 3.3 Skills

Definir como mínimo:

```text
smartpyme_factory
repo_clean
environment_setup
telegram_control
codex_builder
gemini_auditor
```

Cada skill debe ser:

- reproducible
- versionada
- invocable como comando

### 3.4 MCP (Model Context Protocol)

SmartPyme debe exponerse como tools:

```text
- ingest_document
- query_evidence
- task_status
- repo_status
```

---

## 4. Contratos obligatorios

```text
REPO_CLEAN
ENVIRONMENT_CONTRACT
TELEGRAM_IDEMPOTENCY
EVIDENCE_GATE
HUMAN_AUDIT_GATE
```

Ningun ciclo puede ejecutarse si estos contratos fallan.

---

## 5. Integración de agentes

### Codex (Builder)

- Ejecuta bajo task spec
- No decide
- No audita

### Gemini (Auditor)

Debe integrarse como:

```text
- subagente Hermes (delegate_task)
  o
- skill auditora
  o
- tool MCP verificable
```

Si no hay evidencia → NO está integrado

---

## 6. Plan de migración

### Fase 1 — Congelamiento

- No agregar features
- No más parches

### Fase 2 — Guards

- Implementar REPO_CLEAN real
- Implementar ENVIRONMENT

### Fase 3 — Telegram

- Botones idempotentes
- Sin loops

### Fase 4 — Skills

- Extraer lógica a skills Hermes

### Fase 5 — MCP

- Exponer SmartPyme como tools

### Fase 6 — Multiagente

- Integrar Codex como builder
- Integrar Gemini como auditor

### Fase 7 — Reactivación

- Volver a ejecutar tareas de producto

---

## 7. Regla final

```text
Sin Hermes profesional → no hay factoría
```

```text
Sin contratos → no hay ejecución
```

```text
Sin evidencia → no hay aprobación
```