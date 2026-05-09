# FACTORY V3 — Agent Lifecycle

## Entidades

### AgentCard
Describe:
- nombre
- propósito
- inputs
- outputs
- allowed_tools
- forbidden_actions
- approval_requirements

### Task
Unidad de trabajo persistente.

### Artifact
Output persistente de agente.

### ApprovalState
Estado HITL.

### FailureState
Estado de fallo controlado.

## Estados mínimos

- RECEIVED
- PLANNING
- READY
- WORKING
- INPUT_REQUIRED
- AUTH_REQUIRED
- REVIEW
- BLOCKED
- FAILED
- COMPLETED
- REJECTED

## Ciclo de agente

1. descubre artifacts disponibles
2. valida lineage/task
3. consume artifact
4. ejecuta trabajo
5. genera artifact nuevo
6. declara next_expected_agent
7. solicita approval si corresponde

## INPUT_REQUIRED

Se usa cuando:
- falta evidencia
- artifact inválido
- contexto insuficiente

## AUTH_REQUIRED

Se usa cuando:
- merge
- ejecución sensible
- acceso crítico
- modificación persistente

## FAILED

Fallo técnico.

Debe persistir:
- traceback
- artifact involucrado
- agent responsable
- timestamp

## BLOCKED

Bloqueo operativo o policy.

## REJECTED

Task no soportado o inseguro.

## Regla principal

Los agentes NO comparten contexto implícito.

Toda continuidad ocurre vía artifacts persistentes.
