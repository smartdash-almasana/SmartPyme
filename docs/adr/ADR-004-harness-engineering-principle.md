# ADR-004 — Harness Engineering como principio rector de SmartPyme

Fecha: 2026-05-09  
Estado: Aceptado  
Ámbito: SmartPyme producto + SmartPyme Factory  
Tipo: Decisión arquitectónica conceptual y operativa

---

## 1. Contexto

SmartPyme está evolucionando en dos frentes complementarios:

1. **Producto**: Laboratorio Conversacional PyME y motor clínico-operacional para recibir caos real, pedir evidencia, detectar síntomas, producir hallazgos y sugerir tratamientos operativos.
2. **Factoría**: línea industrial asistida por IA para fabricar piezas de software mediante TaskSpecs, contratos, políticas, sandbox, evidencia, PRs y aprobación humana.

En ambos frentes aparece el mismo riesgo:

```text
confundir inteligencia del modelo con confiabilidad del sistema.
```

Un modelo más potente puede razonar mejor, pero no garantiza por sí solo:

- trazabilidad;
- permisos correctos;
- evidencia suficiente;
- límites de ejecución;
- salidas verificables;
- reversibilidad;
- seguridad operacional;
- coherencia arquitectónica acumulativa.

Por eso SmartPyme adopta explícitamente el principio de **Harness Engineering**.

---

## 2. Definición

En SmartPyme, un agente no se define solamente por el modelo que usa.

Se define por la composición:

```text
Agente = Modelo + Harness
```

Donde:

```text
Modelo = LLM o runtime inteligente usado para razonar, clasificar, redactar, auditar o construir.

Harness = conjunto de restricciones, contratos, permisos, herramientas, contexto, evidencia, observabilidad, estados y controles humanos que rodean al modelo.
```

La calidad del sistema depende menos de “qué tan inteligente es el modelo” y más de:

```text
qué tan bien está diseñado el harness que lo contiene.
```

---

## 3. Decisión

SmartPyme adopta Harness Engineering como principio rector transversal.

Decisión formal:

```text
SmartPyme no se diseña alrededor de modelos.
SmartPyme se diseña alrededor de harnesses verificables.
```

Esto significa que ningún modelo, agente o flujo inteligente debe operar como entidad libre.

Debe operar dentro de un harness explícito que defina:

- entrada esperada;
- salida esperada;
- herramientas permitidas;
- permisos;
- evidencia requerida;
- estados válidos;
- criterios de bloqueo;
- criterios de éxito;
- logs;
- trazabilidad;
- revisión humana cuando corresponda;
- modo de recuperación ante error.

---

## 4. Aplicación en SmartPyme Producto

En el producto, Harness Engineering se traduce en agentes clínico-operacionales que no diagnostican por intuición libre.

Deben operar bajo este patrón:

```text
Recepción
→ clasificación
→ pedido de evidencia
→ análisis acotado
→ hallazgo verificable
→ recomendación operacional
→ registro por tenant
```

El modelo puede ayudar a interpretar lenguaje humano, formular preguntas y redactar hallazgos.

Pero el harness gobierna:

- qué evidencia se necesita;
- cuándo bloquear;
- qué microservicio corresponde;
- qué salida es válida;
- qué se registra;
- qué no se puede afirmar;
- qué debe quedar trazado.

### Regla de producto

```text
Sin evidencia suficiente, el agente no diagnostica.
Devuelve NEEDS_EVIDENCE, BLOCKED o UNSUPPORTED.
```

### Ejemplo

Pedido del cliente:

```text
“Vendo mucho, pero no me queda plata.”
```

El modelo puede interpretar el síntoma como posible problema de margen.

Pero el harness debe exigir:

```text
ventas del período
+
costos/lista de precios/facturas proveedoras
+
período de análisis
```

Recién después puede producir un hallazgo como:

```text
Producto X tiene precio de venta pero no tiene costo asociado.
No puede calcularse margen hasta completar evidencia de costo.
```

---

## 5. Aplicación en SmartPyme Factory

En la factoría, Harness Engineering se traduce en una línea de producción gobernada.

El patrón rector es:

```text
TaskSpec
→ contratos
→ policies
→ sandbox
→ evidencia
→ review
→ PR
```

El modelo puede implementar, auditar, refactorizar o documentar.

Pero el harness define:

- archivo permitido;
- archivo prohibido;
- modo de ejecución;
- herramientas habilitadas;
- comandos de verificación;
- contrato de salida;
- condición PASS / PARTIAL / BLOCKED;
- evidencia mínima;
- frontera GitHub / PR;
- aprobación humana antes de integrar.

### Regla de factoría

```text
Ningún agente de fabricación modifica el core sin TaskSpec explícito, sandbox y evidencia.
```

---

## 6. Componentes mínimos de un Harness SmartPyme

Todo harness operacional debe declarar, como mínimo:

| Componente | Pregunta que responde |
|---|---|
| `purpose` | ¿Para qué existe este agente o flujo? |
| `input_contract` | ¿Qué entrada acepta? |
| `output_contract` | ¿Qué salida válida debe producir? |
| `allowed_tools` | ¿Qué herramientas puede usar? |
| `forbidden_actions` | ¿Qué tiene prohibido hacer? |
| `required_evidence` | ¿Qué evidencia necesita para avanzar? |
| `state_model` | ¿Qué estados puede atravesar? |
| `failure_modes` | ¿Cómo bloquea o degrada? |
| `observability` | ¿Qué registra? |
| `human_gate` | ¿Cuándo requiere aprobación humana? |
| `recovery_policy` | ¿Cómo se recupera de errores? |

---

## 7. Estados recomendados

Para producto:

```text
RECEIVED
CLASSIFIED
NEEDS_EVIDENCE
READY_TO_PROCESS
PROCESSING
DELIVERED
BLOCKED
UNSUPPORTED
```

Para factoría:

```text
RECEIVED
VALIDATED
APPROVED
RUNNING
SANDBOXED
REVIEWED
PR_READY
PASS
PARTIAL
BLOCKED
REJECTED
```

---

## 8. Relación con modelos

Los modelos son intercambiables dentro del harness.

Ejemplos:

```text
Gemini puede ser buen lector/auditor.
Codex puede ser buen constructor de código.
DeepSeek puede ser buen ejecutor barato para lectura o prompts acotados.
Kimi puede ser buen razonador/auditor puntual.
```

Pero ningún modelo define por sí mismo la arquitectura.

Regla:

```text
El modelo ejecuta capacidad probabilística.
El harness preserva estructura determinística.
```

Por eso, cambiar de modelo no debe romper:

- contratos;
- estados;
- evidencia;
- logs;
- criterios de salida;
- permisos;
- seguridad.

---

## 9. Anti-patrones prohibidos

Quedan marcados como anti-patrones:

```text
modelo omnisciente sin contrato;
agente libre con herramientas amplias;
prompt gigante como única arquitectura;
diagnóstico sin evidencia;
ejecución sin sandbox;
modificación de core sin TaskSpec;
memoria automática no gobernada;
mezcla de producto, runtime, orquestación y dominio;
selección de modelo como sustituto de diseño de sistema;
HITL decorativo sin poder real de bloqueo.
```

---

## 10. Consecuencias

### Consecuencias positivas

- Menor deriva arquitectónica.
- Mayor seguridad operacional.
- Mejor trazabilidad.
- Agentes más reemplazables.
- Menos dependencia de un proveedor/modelo.
- Mejor economía de tokens.
- Mayor compatibilidad con PRs, evidencia y revisión humana.
- Producto más confiable ante clientes PyME reales.

### Costos

- Más diseño inicial de contratos.
- Menos velocidad aparente en tareas improvisadas.
- Necesidad de mantener artefactos de harness.
- Mayor disciplina para no convertir cada idea en agente libre.

La decisión es aceptada porque SmartPyme prioriza:

```text
confiabilidad > espectacularidad
trazabilidad > magia
harness > modelo aislado
```

---

## 11. Implicancia para roadmap

No se debe agregar un framework multiagente nuevo solo por promesa conceptual.

Antes de adoptar cualquier framework, debe responderse:

```text
¿Mejora el harness?
¿Mejora contratos?
¿Mejora permisos?
¿Mejora trazabilidad?
¿Mejora evidencia?
¿Mejora HITL?
¿Reduce deriva?
```

Si la respuesta es no, no se adopta.

---

## 12. Frase rectora

```text
SmartPyme no busca modelos sueltos más brillantes.
Busca sistemas inteligentes mejor contenidos.
```

---

## 13. Cierre

Harness Engineering consolida una intuición ya presente en SmartPyme:

```text
la inteligencia útil no nace del modelo solo,
sino del sistema que lo encuadra,
lo limita,
lo observa,
lo audita,
y lo obliga a producir evidencia accionable.
```

En producto, esto protege al cliente de diagnósticos sin base.

En factoría, esto protege al repositorio de ejecución caótica.

En ambos casos, el harness es la verdadera frontera entre IA experimental y software operativo confiable.
