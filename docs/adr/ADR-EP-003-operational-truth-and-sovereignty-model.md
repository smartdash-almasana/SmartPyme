# ADR-EP-003: Operational Truth and Sovereignty Model

**Status:** Accepted

**Contexto:**

SmartPyme necesita distinguir entre verdad factual verificable, verdad operativa declarada por el dueño y conflictos entre ambas. Sin ese modelo, el sistema puede perder trazabilidad, sobrescribir hechos o degradar gobernanza en decisiones críticas.

**Decisión:**

Se adoptan los siguientes nodos y artefactos epistemológicos:

* **HumanInputNode:** captura input explícito del dueño/humano con contexto, momento y alcance.
* **OperationalTruthNode:** representa una verdad operativa vigente para conducción del sistema.
* **TruthConflict:** registra divergencias entre verdad documental/factual y verdad operativa declarada.

Reglas del modelo:

* La verdad del dueño no sobrescribe un **FactNode** confirmado.
* Un **OperationalTruthNode** requiere vigencia temporal explícita para evitar absolutización indefinida.
* Si verdad documental y verdad operativa divergen, se crea un **TruthConflict** formal.
* El sistema mantiene persistencia histórica para auditoría de cambios, conflictos y resoluciones.

**Consecuencias:**

* Preserva soberanía humana sin degradar integridad factual del sistema.
* Permite operar bajo criterios de negocio temporales sin falsificar evidencia histórica.
* Hace auditable cuándo, por qué y con qué alcance se activó una verdad operativa.
* Incrementa la complejidad de gobernanza al requerir gestión explícita de conflictos de verdad.

**No decisiones:**

* No define aún mecanismo de resolución automática de `TruthConflict`.
* No establece en esta etapa políticas de expiración por tipo de `OperationalTruthNode`.
* No implementa todavía contratos de almacenamiento ni APIs de consulta de historial.
