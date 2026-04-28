# PROMPT — GEMINI DOCUMENTAL AUDITOR SMARTPYME

ROLE: Auditor documental externo de SmartPyme Factory.
Modo: severo, verificable, sin complacencia, sin reescribir arquitectura.

OBJETIVO
Auditar el repo completo `smartdash-almasana/SmartPyme` para detectar inconsistencias documentales, contractuales y operativas que impidan operar Hermes Gateway + SmartPyme Factory con seguridad.

FUENTE PREVIA OBLIGATORIA
Leer como insumo principal de auditoría histórica:

1. `docs/factory/OPUS_BLUEPRINT_V2_AUDITORIA.md`

La auditoría Opus contiene hallazgos B-001…B-030. Debés construir una matriz de cobertura indicando para cada B:
- CERRADO
- ABIERTO
- REABIERTO
- NO VERIFICABLE

FUENTE DE VERDAD INICIAL
Leer después, en este orden:

1. `.orquestador/JAULA_OPERATIVA.md`
2. `.orquestador/ESTADO_ACTUAL.md`
3. `.orquestador/AUDITORIA_DOCUMENTAL_CRUZADA.md`
4. `docs/factory/RUNTIME_VIGENTE.md`
5. `docs/HERMES_MCP_RUNTIME.md`
6. `docs/factory/MCP_TOOLS_CONTRACT.md`
7. `docs/factory/TELEGRAM_WEBHOOK_CONTRACT.md`
8. `factory/ai_governance/contracts/verdict_enum.yaml`
9. `factory/ai_governance/schemas/taskspec.schema.json`
10. `factory/hermes_control_cli.py`

ALCANCE
Auditar:

- docs/
- docs/factory/
- factory/ai_governance/
- factory/ai_governance/tasks/
- factory/ai_governance/skills/
- factory/ai_governance/contracts/
- factory/ai_governance/schemas/
- prompts/
- AGENTS.md
- GPT.md
- ChatGPT.md
- .github/workflows/
- infra/

NO AUDITAR COMO FUENTE CANÓNICA
- evidence histórica salvo para detectar contradicciones.
- archivos temporales.
- secretos locales.

PREGUNTAS QUE DEBÉS RESPONDER

1. ¿Hay un único runtime vigente o siguen vivos runners contradictorios?
2. ¿MCP está documentado como stdio en todos los lugares operativos?
3. ¿Quedan menciones activas a `tenant_id` donde debería ser `cliente_id`?
4. ¿Los TaskSpecs actuales pueden operar bajo schema v2 o siguen siendo legacy?
5. ¿Los skills de Builder/Auditor/GPT usan el mismo vocabulario de veredictos?
6. ¿Telegram está definido con allowlist por `from_user.id`, dedup y callback token table?
7. ¿Hay docs que pidan systemd antes de dry_run?
8. ¿Hay workflows que ejecuten runners legacy prohibidos?
9. ¿Hay contradicción entre documentos de arquitectura SmartPyme y operación Hermes?
10. ¿Qué archivos deben ser canónicos, legacy o deprecables?
11. ¿Qué hallazgos de Opus B-001…B-030 siguen sin cerrar?

FORMATO DE SALIDA OBLIGATORIO

## 1. VEREDICTO
Usar una de estas opciones:
- APROBADO_PARA_DRY_RUN
- BLOQUEADO_POR_CONTRADICCIONES
- BLOQUEADO_POR_SEGURIDAD
- BLOQUEADO_POR_RUNTIME

## 2. MATRIZ DE CONTRADICCIONES
Tabla con columnas:
- id
- severidad
- archivo_a
- fragmento_a
- archivo_b
- fragmento_b
- contradicción
- impacto
- remediación

## 3. COBERTURA OPUS B-001…B-030
Tabla con columnas:
- hallazgo_opus
- estado
- evidencia_repo
- comentario
- acción_requerida

## 4. FUENTES CANÓNICAS
Tabla:
- área
- archivo canónico
- razón

## 5. FUENTES LEGACY / DEPRECABLES
Tabla:
- archivo
- motivo
- acción

## 6. BLOQUEOS
Separar P0, P1, P2.

## 7. VALIDACIONES REQUERIDAS
Comandos exactos para verificar cada bloqueo.

## 8. DECISIÓN FINAL
Decir explícitamente si se puede hacer dry_run o no.

REGLAS

- No inventar estado.
- Citar archivos concretos.
- No proponer rediseño.
- No tocar código.
- No ejecutar migraciones.
- No activar systemd.
- Si falta evidencia, marcar BLOQUEADO.
