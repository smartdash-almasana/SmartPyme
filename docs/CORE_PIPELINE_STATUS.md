# Core Pipeline Status

## 1. Resumen Ejecutivo
Este documento certifica el estado del pipeline de procesamiento de datos de SmartPyme después del commit `1eea994`. El pipeline introduce un "Clarification Gate" que detiene la ejecución si existen bloqueos pendientes, asegurando que el procesamiento no avance sin la información necesaria. El pipeline es funcional, estable y determinístico. El contrato `PipelineResult` refleja el estado final, incluyendo un posible estado `BLOCKED`.

## 2. Estado Validado del Pipeline
El pipeline incorpora un "gate" de clarificación al inicio del flujo. Si se detectan bloqueos pendientes para el `job_id` actual, el pipeline se detiene y retorna un estado `BLOCKED`.
`facts → canonical → entity → CLARIFICATION GATE → comparison → hallazgos → persistencia → mensajes → PipelineResult`

**Estado:** `ESTABLE`
**Última Validación:** 51 tests pasados / 0 fallidos.

## 3. Tabla de Componentes Existentes
| Componente                          | Ruta                                                 | Rol en el Pipeline                                     |
| ----------------------------------- | ---------------------------------------------------- | ------------------------------------------------------ |
| `FactRepository`                    | `app/repositories/fact_repository.py`                | Provee los datos crudos (facts) de entrada.            |
| `...`                               | `...`                                                | `...`                                                  |
| `ClarificationService`              | `app/services/clarification_service.py`              | **Gate:** Verifica si hay bloqueos pendientes.         |
| `ComparisonService`                 | `app/services/comparison_service.py`                 | Compara `entities` contra fuentes de verdad.           |
| `FindingsService`                   | `app/services/findings_service.py`                   | Genera `findings` (hallazgos) a partir de `comparison`. |
| `FindingCommunicationService`       | `app/services/finding_communication_service.py`      | Convierte `findings` en `messages` legibles.           |
| `Pipeline`                          | `app/core/pipeline.py`                               | Orquesta el flujo completo del pipeline.               |

## 4. Contratos de Salida

### Contrato `PipelineResult`
El contrato se extiende para incluir la razón del bloqueo y formalizar los estados posibles.
- **Status posibles:** `OK`, `BLOCKED`, `ERROR`.

```python
@dataclass
class PipelineCounts:
    # ... sin cambios
    messages: int

@dataclass
class PipelineResult:
    status: str  # "OK", "BLOCKED", "ERROR"
    job_id: str
    plan_id: str
    blocking_reason: str | None = None  # This is the PipelineResult.blocking_reason field

    facts: list
    canonical: list
    entities: list
    comparison: list
    findings: list
    messages: list
    counts: PipelineCounts
    errors: list
```

### Contrato `FindingMessage`
(Sin cambios)

## 5. Tests que Validan Cada Capa
Se han añadido tests específicos para el "Clarification Gate" que validan:
- Si `clarification_service` detecta un bloqueo, el pipeline retorna `status="BLOCKED"`.
- El campo `blocking_reason` se popula correctamente.
- Las etapas posteriores (comparison, findings, messages) no se ejecutan y sus respectivos campos en `PipelineResult` son listas vacías.
- Si no hay bloqueos, el pipeline continúa su ejecución normalmente y retorna `status="OK"`.

## 6. Reglas de Negocio Preservadas
Se añade una regla crítica para la integridad del sistema:
- **No avanzar con bloqueos pendientes:** El pipeline no debe procesar datos potencialmente ambiguos o incompletos. El `ClarificationService` actúa como un gatekeeper que detiene el flujo hasta que las dudas sean resueltas por un humano o un sistema externo.

## 7. Qué NO Está Implementado
El `ClarificationService` actual es un gate. La lógica para **generar y enviar las preguntas de clarificación** a un usuario o sistema externo no está implementada.
- **Canales de Salida para Clarificación:** No hay integración con UI, email, o APIs para enviar las preguntas.
- **Canales de Salida para Mensajes:** Sin cambios. Sigue siendo `internal`.
- Action Engine
- UI (Interfaz de Usuario)
- Integración de Hermes
- Multitenancy, Permisos, etc.

## 8. Riesgos Técnicos Actuales
1.  **Resolución de Bloqueos Manual:** Actualmente, un bloqueo debe ser resuelto manualmente en la capa de persistencia. No hay un flujo de trabajo automatizado para la resolución.
2.  **Escalabilidad de Repositorios en Memoria:** Sin cambios.
3.  **Single-Tenant:** Sin cambios.

## 9. Próximo Paso Recomendado
**Implementar el `ClarificationLoop` completo.** Esto implica desarrollar la lógica para:
1.  Generar una pregunta notificable a partir de un `pending_blocker`.
2.  Enviar esa pregunta a través de un canal (ej. API, webhook, email).
3.  Proveer un endpoint para recibir la respuesta y desbloquear el `job_id`.

## 10. Criterio para no Romper este Contrato
(Sin cambios)
