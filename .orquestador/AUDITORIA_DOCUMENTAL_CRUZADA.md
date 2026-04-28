# AUDITORÍA DOCUMENTAL CRUZADA — SMARTPYME FACTORY

## Estado

OBLIGATORIA antes de activar Hermes Gateway en modo productivo.

## Objetivo

Auditar la documentación, specs, skills, contratos y evidencias del repo para detectar contradicciones que puedan impedir operar SmartPyme Factory con Hermes.

## Auditores

1. Gemini Auditor externo: lee el repo y emite informe independiente.
2. GPT Orquestador: no aprueba su propio trabajo; solo consolida hallazgos y prepara remediación bajo gate humano.

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

## Formato de salida exigido a Gemini

El auditor debe entregar:

1. VEREDICTO
2. MATRIZ DE CONTRADICCIONES
3. ARCHIVOS CANÓNICOS
4. ARCHIVOS LEGACY / DEPRECABLES
5. BLOQUEOS P0/P1/P2
6. REMEDIACIÓN PROPUESTA
7. COMANDOS DE VALIDACIÓN
8. LISTA DE ARCHIVOS QUE NO DEBEN TOCARSE

## Regla de confianza

Un hallazgo solo es válido si cita archivo y línea o fragmento inequívoco.

## Resultado esperado

Archivo de salida:

`factory/ai_governance/evidence/documental_cross_audit_20260428/gemini_audit_report.md`

No se activa systemd ni se migran TaskSpecs reales durante esta auditoría.
