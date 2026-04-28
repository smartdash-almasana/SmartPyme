# AUDITORÍA DOCUMENTAL CRUZADA — SMARTPYME FACTORY

## Estado

OBLIGATORIA antes de activar Hermes Gateway en modo productivo.

## Fuente previa obligatoria

La auditoría de Opus queda incorporada como evidencia histórica y referencia bloqueante:

- `docs/factory/OPUS_BLUEPRINT_V2_AUDITORIA.md`

Regla: cualquier auditoría posterior debe contrastar el estado actual del repo contra los hallazgos B-001…B-030 de Opus y marcar explícitamente cuáles quedaron cerrados, cuáles siguen abiertos y cuáles fueron reabiertos por cambios posteriores.

## Decisión operativa de agentes

Copilot queda excluido del circuito SmartPyme Factory.

El circuito vigente queda reducido a:

1. Gemini Auditor externo: lee el repo local desde la instancia y emite informe independiente.
2. GPT Orquestador: ejecuta remediación documental/contractual bajo jaula operativa y no se autoaprueba.
3. Gemini Auditor externo: reaudita la remediación y decide si se habilita `dry_run`.

## Objetivo

Auditar la documentación, specs, skills, contratos y evidencias del repo para detectar contradicciones que puedan impedir operar SmartPyme Factory con Hermes.

## Auditores

1. Opus: auditoría histórica del Blueprint v2.0, incorporada como referencia documental.
2. Gemini Auditor externo: lee el repo y emite informe independiente contra la auditoría Opus y el estado actual.
3. GPT Orquestador: no aprueba su propio trabajo; solo consolida hallazgos y prepara remediación bajo gate humano.

## Alcance obligatorio

- `.orquestador/`
- `docs/`
- `docs/factory/`
- `factory/ai_governance/`
- `factory/ai_governance/tasks/`
- `factory/ai_governance/skills/`
- `factory/ai_governance/contracts/`
- `factory/ai_governance/schemas/`
- `prompts/`
- `ChatGPT.md`
- `GPT.md`
- `AGENTS.md`
- `.github/workflows/`
- `infra/`

## Ejes de auditoría

1. Runtime vigente: Hermes Gateway externo vs runners legacy.
2. MCP: stdio vs HTTP inexistente.
3. Naming: `cliente_id` vs `tenant_id`.
4. TaskSpecs: v1/v2, schema, estados, prioridad, gate.
5. Veredictos: vocabulario único vs dialectos previos.
6. Telegram: allowlist, callback <=64 bytes, MarkdownV2, dedup.
7. systemd: no activación temprana, sin PYTHONPATH.
8. Seguridad: secretos fuera del repo.
9. Evidencia: qué es canónico y qué es histórico.
10. Consistencia entre docs, skills, prompts y código de control.
11. Cobertura de remediación de B-001…B-030 del informe Opus.

## Formato de salida exigido a Gemini

El auditor debe entregar:

1. VEREDICTO
2. MATRIZ DE CONTRADICCIONES
3. COBERTURA OPUS B-001…B-030
4. ARCHIVOS CANÓNICOS
5. ARCHIVOS LEGACY / DEPRECABLES
6. BLOQUEOS P0/P1/P2
7. REMEDIACIÓN PROPUESTA
8. COMANDOS DE VALIDACIÓN
9. LISTA DE ARCHIVOS QUE NO DEBEN TOCARSE

## Formato de remediación exigido a GPT

GPT debe crear o actualizar evidencia en:

`factory/ai_governance/evidence/documental_cross_audit_20260428/gpt_remediation_report.md`

El reporte debe indicar:

1. VEREDICTO
2. ARCHIVOS MODIFICADOS
3. BLOQUEOS GEMINI CERRADOS
4. BLOQUEOS OPUS RELACIONADOS
5. VALIDACIONES EJECUTADAS
6. BLOQUEOS RESTANTES
7. PRÓXIMO PASO SEGURO

## Regla de confianza

Un hallazgo solo es válido si cita archivo y línea o fragmento inequívoco.

## Resultado esperado

Archivo de salida de Gemini:

`factory/ai_governance/evidence/documental_cross_audit_20260428/gemini_audit_report.md`

Archivo de salida de GPT:

`factory/ai_governance/evidence/documental_cross_audit_20260428/gpt_remediation_report.md`

No se activa systemd ni se migran TaskSpecs reales durante esta auditoría/remediación documental.
