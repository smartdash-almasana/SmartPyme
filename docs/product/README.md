# SmartPyme — Índice Rector de Arquitectura de Capas

## Estado

DOCUMENTO RECTOR — ÍNDICE CANÓNICO v1.0  
**Fecha:** Mayo 2026  
**Alcance:** Capas 00 a 03 — cerradas y alineadas.  
**Capa 04+:** fuera del alcance actual.

---

## Frase rectora

> **Capa 03 no diagnostica. Capa 03 determina si existe un caso investigable.**

Ninguna capa diagnostica antes de Capa 04+.

---

## Tabla canónica de capas

| Capa | Nombre | Entrada | Output | Documento rector |
|---|---|---|---|---|
| **00** | Canal y Entrada Cruda | Evento externo (Telegram, WhatsApp, web, archivo, audio) | `RawInboundEvent` | [SMARTPYME_CAPA_00_CANAL_ENTRADA_CRUDA.md](./SMARTPYME_CAPA_00_CANAL_ENTRADA_CRUDA.md) |
| **01** | Admisión e Interpretación de Intención | `RawInboundEvent` | `InitialCaseAdmission` + `OwnerDemandCandidate` | [SMARTPYME_CAPA_01_ADMISION_EPISTEMOLOGICA.md](./SMARTPYME_CAPA_01_ADMISION_EPISTEMOLOGICA.md) |
| **1.5** | Normalización Documental, Entidades y Tiempo | `RawInboundEvent` (evidencia cruda) + `InitialCaseAdmission` (contexto) | `NormalizedEvidencePackage` | [SMARTPYME_CAPA_015_NORMALIZACION_DOCUMENTAL_ENTIDADES_TIEMPO.md](./SMARTPYME_CAPA_015_NORMALIZACION_DOCUMENTAL_ENTIDADES_TIEMPO.md) |
| **02** | Activación de Conocimiento e Hipótesis Candidata | `InitialCaseAdmission` + `NormalizedEvidencePackage` | `OperationalCaseCandidate` | [SMARTPYME_CAPA_02_ACTIVACION_CONOCIMIENTO_INVESTIGACION.md](./SMARTPYME_CAPA_02_ACTIVACION_CONOCIMIENTO_INVESTIGACION.md) |
| **03** | Apertura del Caso Operativo | `OperationalCaseCandidate` | `OperationalCase` | [SMARTPYME_CAPA_03_DIAGNOSTICO_VALIDACION_OPERATIVA.md](./SMARTPYME_CAPA_03_DIAGNOSTICO_VALIDACION_OPERATIVA.md) |
| **04+** | Investigación, diagnóstico, hallazgos, propuesta, decisión | `OperationalCase` | — | *Fuera del alcance actual* |

---

## Flujo canónico

```text
Canal externo
  ↓
Capa 00  → RawInboundEvent
  ↓
Capa 01  → InitialCaseAdmission + OwnerDemandCandidate
  ↓
Capa 1.5 → NormalizedEvidencePackage
  ↓
Capa 02  → OperationalCaseCandidate
  ↓
Capa 03  → OperationalCase
           (READY_FOR_INVESTIGATION | CLARIFICATION_REQUIRED |
            INSUFFICIENT_EVIDENCE | REJECTED_OUT_OF_SCOPE)
  ↓
Capa 04+ → Investigación, diagnóstico, hallazgos, propuesta, decisión
           (fuera del alcance actual)
```

---

## Reglas de frontera

### Sobre diagnóstico

```text
Ninguna capa diagnostica antes de Capa 04+.
Capa 03 no produce DiagnosticReport.
Capa 03 determina si existe un caso investigable.
```

### Sobre propuestas y decisiones

```text
Capa 02 no propone acción.
Capa 02 no produce DecisionRecord ni AuthorizationGate.
Capa 03 no produce ActionProposal ni DecisionDraft.
```

### Sobre semántica de dominio

```text
Las fases clínicas, patologías, síntomas y semántica PyME
viven en catálogos, Domain Packs o Knowledge Tanks.
Ninguna capa las hardcodea en el core.
Capa 01 puede mencionar candidatos conversacionales (hints),
pero no los confirma como hechos.
```

### Sobre preguntas mayéuticas

```text
Capa 1.5 no formula preguntas mayéuticas de negocio al dueño.
Capa 1.5 produce next_step técnico.
La pregunta al dueño la formula Capa 01 (si es de intención)
o Capa 02 (si es de evidencia para hipótesis).
```

### Sobre candidatos conversacionales

```text
clinical_phase_hint   → candidato de Capa 01, no hecho confirmado
symptoms_hint         → candidatos de Capa 01, no síntomas confirmados
pathologies_hint      → candidatos de Capa 01, no patologías confirmadas
```

Capa 1.5 los usa como orientación para priorizar.  
Capa 02 los valida contra el Knowledge Tank activo.

### Sobre evidencia cruda

```text
Capa 00 registra sin interpretar.
Capa 01 interpreta intención, no contenido documental.
Capa 1.5 normaliza contenido documental.
Capa 02 consume variables limpias, no documentos crudos.
```

---

## Estado documental de cada capa

| Capa | Estado | Versión |
|---|---|---|
| 00 | RECTOR v1.0 | Mayo 2026 |
| 01 | RECTOR v2.0 | Mayo 2026 |
| 1.5 | RECTOR v1.1 | Mayo 2026 |
| 02 | RECTOR v4.0 | Mayo 2026 |
| 03 | RECTOR v2.0 | Mayo 2026 |
| 04+ | Fuera del alcance actual | — |

---

## Contratos Python implementados

| Capa | Contrato | Archivo |
|---|---|---|
| 01 | `InitialCaseAdmission`, `OwnerDemand`, `EvidenceItem`, `EvidenceTask` | `app/contracts/admission_contract.py` |
| 01 | `AdmissionService` | `app/services/admission_service.py` |
| 1.5 | `NormalizedEvidencePackage`, `CleanVariable`, `TemporalWindow`, etc. | `app/contracts/normalization_contract.py` |
| 1.5 | `NormalizationService` | `app/services/normalization_service.py` |
| 02 | `OperationalCaseCandidate`, `InvestigationGraph`, `EvidenceGap`, etc. | `app/contracts/investigation_contract.py` |
| 00 | `RawInboundEvent` | Pendiente: `TS_000_001_CONTRATO_RAW_INBOUND_EVENT` |
| 01 | `OwnerDemandCandidate`, `IntentType` | Pendiente: `TS_ADM_003_OWNER_DEMAND_CANDIDATE` |
| 03 | `OperationalCase` (v2) | Pendiente: `TS_030_001_CONTRATO_OPERATIONAL_CASE` |

---

## Próximos pasos sugeridos

```text
TS_000_001_CONTRATO_RAW_INBOUND_EVENT
  app/contracts/inbound_contract.py
  → RawInboundEvent con todos los campos de Capa 00

TS_ADM_003_OWNER_DEMAND_CANDIDATE
  app/contracts/admission_contract.py
  → OwnerDemandCandidate + IntentType
  → clinical_phase_hint como Optional[str] (no Literal)

TS_030_001_CONTRATO_OPERATIONAL_CASE
  app/contracts/operational_case_v2_contract.py
  → OperationalCase con 4 estados
  → validación cruzada por estado
```
