# ADR-EP-001: SmartGraph Epistemic Contract

**Status:** Accepted

**Contexto:**

SmartPyme requiere un contrato epistemológico explícito para representar estado de verdad operacional sin colapsar incertidumbre en hechos no verificados. El sistema necesita separar evidencia confirmada, señales y formulaciones hipotéticas, mantener trazabilidad de ambigüedad y bloquear decisiones cuando la certeza no es suficiente.

**Decisión:**

SmartGraph se define como grafo de estado de verdad y adopta los siguientes tipos de nodo epistemológico:

* **FactNode:** representa hechos confirmados con evidencia suficiente y trazable.
* **SignalNode:** representa señales observables con valor informativo parcial, aún sin cierre de verdad.
* **HypothesisNode:** representa hipótesis de trabajo; nunca equivale a hecho confirmado.

El contrato incorpora:

* **Tensión multidimensional:** cada afirmación se evalúa por coherencia documental, operacional, temporal y de fuente.
* **Propagación de certeza:** la certeza se propaga de manera controlada por relaciones del grafo, sin promoción automática de hipótesis a hecho.
* **Bloqueo en cascada:** cuando un nodo crítico queda ambiguo o sin evidencia mínima, los nodos dependientes quedan bloqueados.
* **Clarification Gate:** toda ambigüedad relevante debe resolverse por evidencia adicional o decisión humana explícita antes de continuar.

Reglas no negociables:

* Un **HypothesisNode** nunca muta a **FactNode** por inferencia interna; se requiere nueva evidencia validable.
* La ambigüedad no se maquilla: bloquea flujo o demanda evidencia.

**Consecuencias:**

* Mejora la auditabilidad del razonamiento y de las decisiones operativas.
* Reduce falsos positivos por sobreconfianza inferencial.
* Introduce mayor fricción deliberada en escenarios ambiguos, priorizando seguridad epistemológica sobre velocidad.
* Exige instrumentación explícita para gestionar estados bloqueados y rutas de clarificación.

**No decisiones:**

* No define todavía el contrato técnico de APIs, esquemas JSON o clases de implementación.
* No define persistencia física específica (motor, tablas, índices).
* No habilita escritura autónoma de LLM sobre estado confirmado sin validación externa.
