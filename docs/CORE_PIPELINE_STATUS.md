# Core Pipeline Status

## 1. Resumen Ejecutivo
Este documento certifica el estado del pipeline de procesamiento de datos de SmartPyme después del commit `7b4753e`. El pipeline es funcional, estable y determinístico desde la ingesta de `facts` hasta la generación de mensajes legibles por humanos (`messages`). El contrato de salida `PipelineResult` está consolidado y es la única fuente de verdad sobre el resultado de un ciclo de procesamiento.

## 2. Estado Validado del Pipeline
El pipeline sigue un flujo lineal y secuencial. La nueva capa de comunicación genera mensajes a partir de los hallazgos, preparando el sistema para la interacción humana.
`facts → canonical → entity → comparison → hallazgos → persistencia → mensajes → PipelineResult`

**Estado:** `ESTABLE`
**Última Validación:** 42 tests pasados / 0 fallidos.

## 3. Tabla de Componentes Existentes
| Componente                          | Ruta                                                 | Rol en el Pipeline                                     |
| ----------------------------------- | ---------------------------------------------------- | ------------------------------------------------------ |
| `FactRepository`                    | `app/repositories/fact_repository.py`                | Provee los datos crudos (facts) de entrada.            |
| `FactExtractionService`             | `app/services/fact_extraction_service.py`            | Orquesta la extracción de facts.                       |
| `CanonicalRepository`               | `app/repositories/canonical_repository.py`           | Almacena y provee datos en formato canónico.           |
| `CanonicalizationService`           | `app/services/canonicalization_service.py`           | Transforma `facts` en `canonical`.                     |
| `EntityContract`                    | `app/contracts/entity_contract.py`                   | Define la estructura de una entidad de negocio.        |
| `EntityRepository`                  | `app/repositories/entity_repository.py`              | Almacena y provee entidades de negocio.                |
| `EntityResolutionService`           | `app/services/entity_resolution_service.py`          | Resuelve y enriquece `canonical` para crear `entities`. |
| `ComparisonService`                 | `app/services/comparison_service.py`                 | Compara `entities` contra fuentes de verdad.           |
| `FindingsService`                   | `app/services/findings_service.py`                   | Genera `findings` (hallazgos) a partir de `comparison`. |
| `FindingCommunicationService`       | `app/services/finding_communication_service.py`      | Convierte `findings` en `messages` legibles.           |
| `PipelineContract`                  | `app/contracts/pipeline_contract.py`                 | Define los contratos de datos del pipeline.            |
| `CommunicationContract`             | `app/contracts/communication_contract.py`            | Define la estructura de `FindingMessage`.              |
| `Pipeline`                          | `app/core/pipeline.py`                               | Orquesta el flujo completo del pipeline.               |

## 4. Contratos de Salida
El pipeline ahora produce dos contratos principales: `PipelineResult` para el estado general y `FindingMessage` para la comunicación.

### Contrato `PipelineResult`
```python
@dataclass
class PipelineCounts:
    facts: int
    canonical: int
    entities: int
    validated_entities: int
    comparison: int
    findings: int
    messages: int

@dataclass
class PipelineResult:
    status: str
    job_id: str
    plan_id: str
    facts: list
    canonical: list
    entities: list
    comparison: list
    findings: list
    messages: list  # This is the PipelineResult.messages field
    counts: PipelineCounts
    errors: list
```

### Contrato `FindingMessage`
Representa un hallazgo traducido a un formato notificable.
```python
@dataclass
class FindingMessage:
    channel: str  # ej: "internal", "whatsapp"
    recipient: str
    title: str
    body: str
    finding_id: str
    metadata: dict
```

## 5. Tests que Validan Cada Capa
La capa de comunicación es validada por tests que aseguran:
- La correcta instanciación del `FindingCommunicationService`.
- La generación de `messages` si y solo si hay `findings` y un servicio de comunicación configurado.
- El contenido y formato de los mensajes se alinea con el `FindingMessage` contract.

## 6. Reglas de Negocio Preservadas
Todas las reglas anteriores se mantienen. Se añade una nueva:
- **Mensajes desde Hallazgos:** Los `messages` solo se generan a partir de `findings` validados. Si no hay `findings`, `messages` será una lista vacía.

## 7. Qué NO Está Implementado
La capa de comunicación es interna. **No se envían notificaciones reales.**
- **Canales de Salida:** No hay integración real con WhatsApp, Telegram, UI, etc. El canal es `internal`.
- Action Engine (ej. correcciones automáticas)
- UI (Interfaz de Usuario)
- Integración de Hermes en el flujo core
- Runtime de Terraform/GCP
- Multitenancy
- Permisos y Roles
- "Clarification loop" productivo

## 8. Riesgos Técnicos Actuales
1.  **Escalabilidad de Repositorios en Memoria:** Sin cambios. Sigue siendo un riesgo para grandes volúmenes de datos.
2.  **Gestión de Canales:** La lógica de enrutamiento de mensajes a diferentes canales (cuando existan) es un placeholder.
3.  **Single-Tenant:** Sin cambios.

## 9. Próximo Paso Recomendado
**Conectar el `FindingCommunicationService` a un broker de mensajería (como RabbitMQ o Kafka) o a una API de notificaciones.** Esto permitirá que los mensajes generados se envíen realmente a través de canales externos y habilitará la capa de UI/notificación.

## 10. Criterio para no Romper este Contrato
Cualquier cambio futuro en el pipeline debe:
1.  **Ser compatible con `PipelineResult` y `FindingMessage`:** Mantener retrocompatibilidad.
2.  **Añadir tests de integración:** Validar el flujo de `findings` a `messages` y su correcto formato.
3.  **Respetar las reglas de negocio:** No generar mensajes sin un hallazgo cuantificado.
