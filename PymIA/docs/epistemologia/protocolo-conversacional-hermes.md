# ADR-EP-002: Hermes Conversational Epistemic Protocol

**Status:** Accepted

**Contexto:**

Hermes debe operar como infraestructura epistemológica conversacional y no como generador de respuestas opacas. SmartPyme necesita que cada interacción exprese estado de verdad verificable, nivel de incertidumbre y dependencia de decisiones humanas.

**Decisión:**

Hermes se formaliza como canal conversacional de estado de verdad. Su salida comunica estado operativo y evidencia, no "respuestas mágicas".

Estados epistemológicos obligatorios:

* **CONFIRMADO**
* **INFERIDO**
* **PENDIENTE**
* **BLOQUEADO**
* **DECISION_REQUERIDA**

Modos de copilotaje autorizados:

* **DIOS:** "modo de máxima soberanía del dueño y mínimo margen interpretativo del sistema; solo acciones determinísticas, datos duros y bloqueo ante ambigüedad".
* **HIBRIDO:** ejecución compartida entre automatización y validación humana frecuente.
* **INVESTIGADOR:** foco en recolección de evidencia y reducción de incertidumbre antes de actuar.

Toda entrega conversacional operativa debe incluir el **6-Step Report**:

1. qué tenemos
2. qué alcanzamos
3. qué todavía no sabemos
4. qué falta
5. qué decisión del dueño desbloquea
6. qué dato duro certifica

**Consecuencias:**

* Aumenta la transparencia de estado y reduce ambigüedad de coordinación.
* Estandariza la comunicación entre owner, Hermes y builders/auditores.
* Hace visible el costo de incertidumbre y acelera desbloqueos humanos correctos.
* Impone disciplina de reporte, evitando cierres prematuros sin dato duro.

**No decisiones:**

* No define aún implementación de interfaz (CLI, Telegram, panel, etc.).
* No fija todavía políticas de rate limit, reintentos o priorización de colas.
* No reemplaza contratos de evidencia ni validaciones técnicas del pipeline.
