# FACTORY V3 — Artifact Protocol

## Principio central

Artifacts reemplazan:
- paso de variables en memoria
- contexto implícito
- acoplamiento directo entre agentes

Artifacts = APIs internas persistentes.

## Formatos

- YAML
- JSON
- Markdown

## Tipos iniciales

- PlanArtifact
- ArchitectureArtifact
- CodeArtifact
- ReviewArtifact
- SecurityArtifact
- DecisionArtifact
- ReleaseArtifact

## Campos obligatorios

artifact_id:
artifact_type:
task_id:
tenant_id:
created_by_agent:
created_at:
parent_artifacts:
purpose:
evidence:
outputs:
next_expected_agent:
integrity_hash:

## Reglas

- todo artifact debe ser trazable
- todo artifact debe ser persistente
- artifacts pueden reiniciarse aisladamente
- ningún agente consume memoria implícita
- artifacts deben ser compatibles con futura exposición A2A

## Ejemplo conceptual

planner_agent
→ plan.yaml

coder_agent
→ lee plan.yaml
→ genera code_patch.yaml

reviewer_agent
→ lee ambos artifacts
→ genera review.md

## Ledger

Artifact ledger:
- append only
- auditable
- reproducible
- restartable

## Relación con ADK

ADK Artifacts
→ mapean directamente sobre Artifact Protocol SmartPyme.

## Relación con A2A

Artifacts son payloads interoperables entre agentes.
