# Core Pipeline Status

## 1. Resumen Ejecutivo
Este documento certifica el estado del pipeline de procesamiento de datos de SmartPyme después del commit `4111a24`. El pipeline es funcional, estable y determinístico desde la ingesta de `facts` hasta la generación de `findings`. El contrato de salida `PipelineResult` está consolidado y es la única fuente de verdad sobre el resultado de un ciclo de procesamiento.

## 2. Estado Validado del Pipeline
El pipeline sigue un flujo lineal y secuencial, donde cada etapa depende de la anterior. El estado actual, validado por tests unitarios y de integración, es:
`facts → canonical → entity → comparison → findings → PipelineResult`

**Estado:** `ESTABLE`
**Última Validación:** 34 tests pasados / 0 fallidos.

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
| `PipelineContract`                  | `app/contracts/pipeline_contract.py`                 | Define los contratos de datos del pipeline.            |
| `Pipeline`                          | `app/core/pipeline.py`                               | Orquesta el flujo completo del pipeline.               |

## 4. Contrato `PipelineResult`
El pipeline garantiza la entrega de un único objeto `PipelineResult` al finalizar su ejecución.

```python
@dataclass
class PipelineCounts:
    facts: int
    canonical: int
    entities: int
    validated_entities: int
    comparison: int
    findings: int

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
    counts: PipelineCounts
    errors: list
```

## 5. Tests que Validan Cada Capa
La estabilidad del pipeline se asegura con tests específicos para cada componente clave, garantizando que los contratos entre capas se respeten. Los tests relevantes se encuentran en los módulos de test correspondientes a cada servicio y repositorio.

## 6. Reglas de Negocio Preservadas
El pipeline actual respeta las siguientes reglas de negocio no negociables:
- **No IA en el core:** El flujo es 100% determinístico.
- **No inferencia:** Datos faltantes no se inventan. El sistema es "fail-closed".
- **Entidades validadas son inmutables:** No se degradan a `pending_validation`.
- **Hallazgos cuantificados:** Todo hallazgo incluye `entidad`, `diferencia cuantificada` y `comparación explícita`.
- **Sin diferencias, no hay hallazgos:** El pipeline devuelve `findings=[]` si no se detectan anomalías.
- **Preservación de decisiones humanas:** Las validaciones manuales previas se respetan en ciclos futuros.

## 7. Qué NO Está Implementado
La funcionalidad actual se limita estrictamente al pipeline de datos. Los siguientes componentes son futuros y NO forman parte del core actual:
- Communication Layer (ej. notificaciones)
- Action Engine (ej. correcciones automáticas)
- UI (Interfaz de Usuario)
- Integración de Hermes en el flujo core
- Runtime de Terraform/GCP
- Persistencia de hallazgos en un repositorio dedicado
- Multitenancy
- Permisos y Roles
- Salida por WhatsApp/Telegram
- "Clarification loop" productivo

## 8. Riesgos Técnicos Actuales
1.  **Escalabilidad de Repositorios en Memoria:** Los repositorios actuales son in-memory, lo que limita el volumen de datos procesables.
2.  **Ausencia de Persistencia de Hallazgos:** Los `findings` se generan pero no se almacenan para análisis histórico.
3.  **Single-Tenant:** La arquitectura actual no soporta separación de datos por cliente.

## 9. Próximo Paso Recomendado
**Implementar la capa de persistencia para los `PipelineResult` y sus `findings`** en una base de datos. Esto desacoplará la generación de hallazgos de su consumo y permitirá el análisis histórico.

## 10. Criterio para no Romper este Contrato
Cualquier cambio futuro en el pipeline debe:
1.  **Ser compatible con el contrato `PipelineResult`:** No se deben eliminar campos. Se pueden añadir nuevos campos si es necesario, pero manteniendo la retrocompatibilidad.
2.  **Añadir tests de integración:** Cualquier nueva funcionalidad debe tener tests que validen su comportamiento dentro del pipeline completo.
3.  **Respetar las reglas de negocio:** No se debe introducir lógica no determinística ni violar los principios de "fail-closed" y cuantificación de hallazgos.
