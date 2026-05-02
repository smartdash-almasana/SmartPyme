# SmartPyme — Modelos Operativos, Síntomas, Casos y Diagnóstico

## Estado
Documento conceptual de arquitectura.

## Propósito
Consolidar la lógica aparecida en la conversación sobre cómo SmartPyme debe pasar de una demanda verbal del dueño a un caso operativo investigable, un diagnóstico documentado, una propuesta y una nueva decisión trazable.

Este documento no describe únicamente código. Describe el lenguaje interno del sistema.

---

# 1. Principio general

SmartPyme no debe comportarse como un chatbot que responde suelto.

SmartPyme debe comportarse como un sistema operativo de negocio que:

1. recibe una demanda,
2. interpreta el dolor,
3. separa dato válido de ruido,
4. verifica condiciones,
5. formula hipótesis investigables,
6. construye un caso,
7. investiga con evidencia,
8. genera diagnóstico,
9. propone una acción,
10. pregunta al dueño,
11. registra la decisión,
12. ejecuta solo con autorización trazable.

Frase guía:

> El sistema no es código. Es sentido → evidencia → diagnóstico → propuesta → confirmación → acción controlada.

---

# 2. Regla soberana

La regla central de SmartPyme es:

> SmartPyme no decide. SmartPyme propone. El dueño confirma.

Esto implica:

- La IA interpreta, pero no decide.
- Pydantic valida estructura, pero no decide negocio.
- El core determinístico protege la verdad operacional.
- El dueño confirma, corrige, rechaza o autoriza.
- Ninguna ejecución ocurre sin una decisión registrada.
- Ninguna acción corre sin autorización trazable.

---

# 3. Diferencia entre pedir, entender y actuar

No todo mensaje del dueño debe convertirse en un trabajo.

Hay al menos dos grandes tipos de intención:

## 3.1 Intención operativa

Ejemplos:

- “Revisame el stock.”
- “Conciliame ventas contra banco.”
- “Investigá si estoy perdiendo margen.”

Este tipo de mensaje puede terminar en:

- propuesta de trabajo,
- confirmación del dueño,
- creación de Job,
- autorización,
- ejecución controlada.

## 3.2 Intención pedagógica o cognitiva

Ejemplos:

- “¿Cómo calculo bien los costos?”
- “¿Cómo sé si estoy perdiendo plata?”
- “¿Cómo alinear precios con inflación?”
- “¿Cómo conseguir mejores proveedores?”

Este tipo de mensaje no necesariamente crea un Job. Puede requerir:

- explicación,
- guía,
- marco conceptual,
- ejemplo,
- pregunta de continuidad.

Regla:

> Hay pedidos para actuar y pedidos para entender.

El sistema debe poder preguntar:

> ¿Querés que te informe o querés que me encargue yo y lo haga por vos?

---

# 4. La pregunta como instrumento de precisión

El lenguaje humano es ambiguo. Genera confusión. Por eso SmartPyme necesita preguntas precisas.

La pregunta no es un adorno conversacional. Es una herramienta de determinación.

La pregunta produce:

- evidencia conversacional,
- aclaración,
- autorización,
- respaldo,
- trazabilidad.

Ejemplo:

> Para poder avanzar con este reporte necesito el Excel/listado de ventas del período, el costo de reposición o facturas de proveedores, y el período que querés revisar. Con eso puedo investigar si existe pérdida de margen y entregarte un reporte completo. Cuando lo tengas, me lo mandás y seguimos.

Regla de interacción:

> No invasivo en tono. Duro en condiciones.

El sistema no debe hacer 80 preguntas a la vez. Pero sí debe decir con precisión qué falta y por qué.

---

# 5. El dueño como fuente

El dueño es fuente de:

- demanda,
- documentación,
- convalidación,
- contexto,
- evidencia,
- autorización,
- corrección,
- prioridad.

Cuando falta información, la pelota vuelve al dueño.

El sistema debe poder decir:

> Me estás dando poco material para ayudarte. Puedo avanzar cuando me des la información mínima necesaria.

No es un rechazo hostil. Es un bloqueo sano.

Regla:

> SmartPyme espera, no inventa.

---

# 6. Curación de datos: la diálisis del sistema

Antes de que un dato entre al core, debe pasar por curación.

La curación responde:

> ¿Este dato es válido en sí mismo?

Valida:

1. PRESENCE: existe el dato.
2. STRUCTURE: tiene tipo correcto.
3. DOMAIN: tiene sentido en su dominio.
4. RELEVANCE: aplica a la skill o al caso.

Ejemplos de rechazo:

- archivo vacío,
- foto en negro,
- monto negativo donde no corresponde,
- fecha inválida,
- campo numérico con texto absurdo,
- variable irrelevante para esa skill,
- evidencia que no sirve para el trabajo pedido.

Regla:

> La basura se separa del alimento.

Sin curación:

- se contamina el core,
- se guardan datos corruptos,
- se generan diagnósticos falsos,
- se pierde confianza.

---

# 7. Conditions: condiciones para trabajar

Curación y condiciones no son lo mismo.

## Curation

Pregunta:

> ¿El dato es válido?

## Conditions

Pregunta:

> ¿Con estos datos alcanza para ejecutar esta tarea?

Ejemplo BOM / producción:

Si el dueño pide cálculo de producción pero solo manda catálogo de producto terminado y precio final, no alcanza.

Faltan:

- materia prima,
- cantidad por producto,
- costo unitario,
- merma,
- tiempos,
- fórmula de producción.

Regla:

> Primero se valida el dato. Después se valida si alcanza.

Otra formulación:

> No puede haber flujo de trabajo si no están dadas las condiciones necesarias para ese flujo.

---

# 8. Job, DecisionRecord y autorización

## 8.1 Job

Un Job es una orden de trabajo.

No prueba que el trabajo esté autorizado. Solo representa una unidad operativa posible.

## 8.2 DecisionRecord

Un DecisionRecord registra qué decidió el dueño.

Tipos:

- INFORMAR,
- EJECUTAR,
- RECHAZAR.

Regla:

> Si no está registrado, no ocurrió.

## 8.3 Authorization Gate

El guardia de autorización verifica si la decisión del dueño abre la puerta de ese Job específico.

Pregunta:

> ¿Existe autorización válida del dueño para ejecutar este trabajo?

Verifica:

- mismo cliente_id,
- mismo job_id,
- decisión tipo EJECUTAR,
- Job en estado permitido,
- no cruzar cliente,
- no ejecutar Jobs finalizados o ya corriendo.

Analogía:

> El Job es una orden de trabajo. El DecisionRecord es la firma del dueño. El AuthorizationGate verifica que la firma corresponda a esa orden.

Regla:

> Sin autorización trazable, no hay ejecución.

---

# 9. RUNNING no significa resuelto

Cuando un Job pasa a RUNNING, eso no significa que el diagnóstico esté hecho.

Significa:

> Este trabajo fue autorizado y puede entrar al taller.

La frontera correcta es:

- Executor: abre la puerta.
- Runner: prepara o ejecuta el trabajo.
- Motor técnico: hace cálculo, investigación o diagnóstico.

Frase:

> El Executor abre la puerta. El Runner hace entrar el trabajo al taller.

---

# 10. OperationalCase: el expediente operativo

El caso operativo no es la skill.

La skill es una capacidad técnica.

El OperationalCase es la situación concreta del dueño preparada para ser investigada.

Debe reunir:

- demanda original,
- dolor/enunciado,
- cliente_id,
- job_id,
- skill_id,
- hipótesis investigable,
- taxonomía del negocio,
- variables curadas,
- evidencia disponible,
- condiciones validadas,
- fórmula aplicable,
- patología posible,
- referencias necesarias,
- plan de investigación.

Regla central:

> El caso no arranca con diagnóstico. Arranca con hipótesis investigable.

Ejemplo incorrecto:

> Revisar pérdida de margen.

Ejemplo correcto:

> Investigar si existe pérdida de margen en el almacén X durante el período Y.

---

# 11. Hipótesis, diagnóstico y hallazgo

El sistema no debe afirmar el problema al inicio.

Debe formular una hipótesis y verificarla.

Secuencia:

1. Dolor expresado.
2. Hipótesis investigable.
3. Recolección/curación de evidencia.
4. Comparación contra referencias.
5. Diagnóstico.
6. Hallazgo localizado.
7. Propuesta.
8. Confirmación del dueño.
9. Acción controlada.

Diferencias:

- Dolor expresado no es hecho probado.
- Hipótesis no es hallazgo.
- Hallazgo no es acción.
- Diagnóstico confirmado requiere evidencia.

Ejemplo:

Demanda:

> Creo que estoy perdiendo plata.

Hipótesis:

> Investigar si existe pérdida económica asociada a margen, stock, precio, costos o conciliación.

Diagnóstico:

> Se detecta pérdida de margen en la familia lácteos por diferencia entre costo de reposición y precio de venta.

Hallazgo:

> Producto X tiene margen real 8% menor al margen objetivo durante marzo.

---

# 12. Modelo clínico SmartPyme

La analogía médica es útil y estructural.

## Correspondencias

| Clínica | SmartPyme |
|---|---|
| Paciente | PyME |
| Historia clínica | Historia operativa del negocio |
| Dolor | Demanda del dueño |
| Síntoma | Señal observable |
| Patología | Patrón de daño operativo |
| Diagnóstico | Hallazgo confirmado |
| Tratamiento | Propuesta de acción |
| Buena práctica | Conducta saludable del negocio |
| Seguimiento | Medición posterior |

Secuencia clínica-operativa:

> Dolor del dueño → síntoma operativo → hipótesis patológica → evidencia → diagnóstico → tratamiento/propuesta → seguimiento.

Ejemplo:

Síntomas observados:

- costos no actualizados,
- precios finales desalineados,
- facturas de proveedor con aumentos no trasladados.

Hipótesis:

> Investigar si existe pérdida de margen por desactualización de costos.

Diagnóstico:

> Confirmado.

Patología asociada:

> Desalineación costo-precio.

Tratamiento sugerido:

> Actualizar matriz de costos y revisar familias críticas.

---

# 13. Síntomas operativos

Un síntoma operativo es una señal de posible daño, fricción o desorden.

Ejemplos de síntomas:

- dolor o estrés del dueño,
- repetición innecesaria de trabajos,
- exceso de tareas manuales,
- falta de automatización,
- desorden documental,
- caos administrativo,
- flujo de caja desajustado,
- mezcla de dinero formal e informal,
- costos mal calculados,
- precios desactualizados,
- stock inconsistente,
- proveedores caros,
- ROI insuficiente,
- pérdida de información,
- exceso o falta de personal,
- dependencia excesiva del dueño,
- decisiones tomadas por intuición sin evidencia,
- planillas Excel duplicadas,
- conciliaciones manuales recurrentes,
- compras sin comparación,
- ventas sin análisis de margen,
- crecimiento sin sistema.

El dolor es una entrada, pero no alcanza. El sistema debe traducirlo a síntomas observables.

---

# 14. Catálogo de patologías PyME

Una patología es un patrón de daño operativo que se repite en distintos negocios.

Ejemplos:

- desalineación costo-precio,
- pérdida de margen,
- fuga de stock,
- conciliación bancaria deficiente,
- caja opaca,
- sobrecarga administrativa,
- dependencia extrema del dueño,
- subautomatización,
- inversión sin ROI,
- proveedor no competitivo,
- precios atrasados frente a inflación,
- estructura de personal desbalanceada,
- documentación insuficiente,
- ventas sin trazabilidad,
- compras sin control,
- producción sin BOM confiable,
- inventario sin conteo físico,
- crecimiento caótico,
- sistema informal no auditable.

Regla:

> La investigación confirma o descarta patologías; no las afirma de entrada.

---

# 15. Modelos operativos PyME

No alcanza con patologías sueltas. Las patologías aparecen dentro de modelos operativos.

SmartPyme necesita modelos para comprender el caos de la PyME latinoamericana.

Ejemplos de modelos:

- modelo comercial,
- modelo de compras,
- modelo de ventas,
- modelo de costos,
- modelo de stock,
- modelo productivo,
- modelo financiero,
- modelo administrativo,
- modelo familiar/personalista,
- modelo de expansión,
- modelo de proveedores,
- modelo de recursos humanos,
- modelo documental,
- modelo de automatización,
- modelo de caja,
- modelo de margen,
- modelo de precios,
- modelo de crecimiento.

Estructura:

> Modelo PyME → síntomas típicos → patologías posibles → variables necesarias → evidencia requerida → fórmulas/comparaciones → diagnóstico → propuesta.

Analogía meteorológica:

> No hay una causa única. Hay sistemas de variables interactuando.

Por eso SmartPyme necesita un atlas clínico-operativo de la PyME latinoamericana.

---

# 16. PyME latinoamericana: rasgos del dominio

El sistema debe reconocer que muchas PyMEs latinoamericanas no funcionan como organizaciones corporativas profesionalizadas.

Rasgos frecuentes:

- orden personalista según el dueño,
- baja digitalización,
- documentación fragmentada,
- supervivencia operativa,
- resiliencia informal,
- decisiones basadas en memoria o intuición,
- mezcla de canales,
- Excel como sistema nervioso real,
- WhatsApp como archivo operativo,
- información dispersa,
- baja automatización,
- dependencia de empleados clave,
- falta de procedimientos,
- dificultad para medir ROI,
- informalidad financiera,
- urgencias permanentes.

Esto no debe ser juzgado moralmente. Debe ser modelado.

SmartPyme debe llevar al negocio:

> de menos saludable a más saludable.

---

# 17. Buena práctica como conducta saludable

La buena práctica es el equivalente a una conducta saludable del negocio.

Ejemplos:

- actualizar costos periódicamente,
- comparar proveedores,
- conciliar ventas y banco,
- separar caja formal e informal,
- registrar decisiones,
- automatizar tareas repetitivas,
- reducir dependencia del dueño,
- documentar procesos,
- medir márgenes por familia,
- revisar stock físico vs teórico,
- usar evidencia antes de decidir,
- calcular ROI antes de invertir,
- construir tableros simples,
- tener trazabilidad de precios,
- revisar producción con BOM confiable.

El sistema no solo detecta enfermedad. También orienta hacia prácticas más sanas.

---

# 18. DiagnosticReport

El DiagnosticReport es el documento de resultado investigativo.

Debe incluir:

- hypothesis,
- diagnosis_status:
  - CONFIRMED,
  - NOT_CONFIRMED,
  - INSUFFICIENT_EVIDENCE,
- findings,
- evidence_used,
- formulas_used,
- quantified_impact,
- reasoning_summary,
- proposed_next_actions,
- owner_question.

Regla:

> Sin hallazgo con evidencia, diferencia cuantificada y comparación de fuentes, no hay diagnóstico confirmado.

El reporte debe ordenar documentalmente lo investigado.

Debe responder:

1. qué se investigó,
2. con qué evidencia,
3. qué fórmulas se aplicaron,
4. qué se encontró,
5. dónde se localiza el problema,
6. cuánto impacta,
7. qué se recomienda,
8. qué decisión debe tomar el dueño.

---

# 19. Hallazgo válido

Un hallazgo válido debe contener:

- entity,
- finding_type,
- measured_difference,
- compared_sources,
- evidence_used,
- severity,
- recommendation.

Regla persistente:

> Todo hallazgo debe expresar entidad específica, diferencia cuantificada y comparación explícita de fuentes.

Ejemplo:

> Producto “Leche Entera 1L” presenta margen real 8% menor al margen objetivo durante marzo, comparando factura de proveedor del 2026-03-10 contra ventas POS del mismo período.

Esto es distinto de:

> Hay problemas de margen.

El segundo enunciado no sirve como hallazgo operativo.

---

# 20. QuantifiedImpact

El impacto no debe ser solo un número flotante.

Puede expresarse como:

- amount,
- currency,
- percentage,
- units,
- time_saved,
- risk_level.

Ejemplos:

- pérdida estimada: ARS 320.000,
- diferencia de margen: 8%,
- unidades afectadas: 145,
- tiempo manual perdido: 12 horas/semana,
- riesgo: HIGH.

Regla:

> Todo impacto debe ser tan cuantificable como la evidencia permita.

Si no alcanza la evidencia:

> diagnosis_status = INSUFFICIENT_EVIDENCE.

---

# 21. ValidatedCaseRecord

Cuando el caso está consolidado, la evidencia está vinculada y el reporte está generado, debe quedar un registro auditable.

Ese registro es el ValidatedCaseRecord.

No es lo mismo que DecisionRecord.

| Registro | Qué prueba |
|---|---|
| DecisionRecord | qué decidió o autorizó el dueño |
| OperationalCase | qué expediente se armó para investigar |
| DiagnosticReport | qué se encontró y cómo se documentó |
| ValidatedCaseRecord | que el caso quedó consolidado/cerrado con evidencia |

Regla:

> Si no queda registrado, no es auditable. Si no es auditable, no sirve como prueba de valor.

---

# 22. Pregunta final al dueño

El reporte no debe cerrar con una orden. Debe cerrar con una pregunta.

Ejemplos:

> ¿Querés que SmartPyme te ayude a ejecutar esta corrección?

> ¿Querés que preparemos un plan de acción para corregir precios, proveedores o costos?

> ¿Querés dejar este reporte como cierre de diagnóstico?

Esto mantiene al dueño en control.

Distinción:

- Reporte = qué se descubrió.
- Propuesta = qué conviene hacer.
- Pregunta = quién decide el próximo paso.

Regla:

> El sistema investiga. El reporte documenta. La propuesta orienta. El dueño decide.

---

# 23. Trazabilidad de decisiones e impacto económico

Cada decisión del dueño debe registrarse con:

- fecha,
- hora,
- cliente_id,
- propuesta del sistema,
- respuesta del dueño,
- overrides,
- job_id si corresponde,
- resultado posterior.

Esto permite demostrar:

- qué decisión se tomó,
- cuándo se tomó,
- sobre qué evidencia,
- qué acción habilitó,
- qué impacto económico produjo.

Ejemplo de cadena de valor:

1. El dueño autorizó investigar precios.
2. Se creó Job.
3. Se armó OperationalCase.
4. Se produjo DiagnosticReport.
5. Se confirmó pérdida de margen.
6. Se propuso corrección.
7. El dueño autorizó ajustar matriz.
8. Se midió mejora posterior.

Así SmartPyme puede demostrar:

- dinero ganado,
- dinero que se dejó de perder,
- horas recuperadas,
- riesgo reducido.

---

# 24. MCP Bridge

El MCP Bridge es la capa de enchufe/protocolo entre Hermes Runtime y los componentes internos de SmartPyme.

Flujo:

> Hermes Runtime → MCP Bridge → herramientas internas → servicios/repositorios/orquestadores.

El MCP Bridge no decide negocio.

No interpreta por su cuenta.

No ejecuta skills por sí mismo.

Es una ventanilla segura con contratos explícitos.

Frase:

> Hermes no entra al core por la ventana. Hermes entra por MCP, con herramientas limitadas y contratos explícitos.

---

# 25. Hermes Runtime vs Hermes Factory

Debe mantenerse la separación:

## Hermes Factory

Construye SmartPyme.

- genera prompts,
- escribe código,
- audita,
- ejecuta tests,
- sincroniza repo.

## Hermes Runtime

Opera dentro de SmartPyme.

- recibe demandas,
- llama herramientas MCP,
- orquesta pasos,
- devuelve propuestas o pedidos de aclaración,
- registra decisiones.

Regla:

> No mezclar Hermes Factory con Hermes Runtime.

---

# 26. Estado actual del flujo implementado

Hasta este punto, el sistema ya tiene una cadena estable:

1. Recepción del pedido.
2. Interpretación blanda.
3. Curación de datos.
4. Validación de condiciones.
5. Propuesta de Job.
6. Confirmación del dueño.
7. DecisionRecord.
8. AuthorizationGate.
9. Job pasa a RUNNING.
10. OperationalCase se crea si hay contexto suficiente.
11. Si falta contexto, se pide aclaración al dueño.

Frontera actual:

> OperationalCase existe. Todavía no hay investigación técnica ni DiagnosticReport.

---

# 27. Próximo frente conceptual

El próximo frente no debería ser ejecutar motores a ciegas.

Debe ser:

> OperationalCase → investigación técnica → DiagnosticReport.

Pero antes hay que definir el marco clínico-operativo:

- síntomas,
- patologías,
- modelos operativos PyME,
- referencias,
- fórmulas,
- criterios para CONFIRMED / NOT_CONFIRMED / INSUFFICIENT_EVIDENCE.

Propuesta de próximo documento:

> PYME_OPERATIONAL_MODELS_SYMPTOMS_AND_PATHOLOGIES.md

Objetivo:

> construir el atlas clínico-operativo de la PyME latinoamericana.

---

# 28. Frases rectoras

- SmartPyme no decide: propone; el dueño confirma.
- El dueño decide, pero el sistema protege la coherencia.
- No invasivo en tono. Duro en condiciones.
- La basura se separa del alimento.
- Primero se valida el dato. Después se valida si alcanza.
- Sin autorización trazable, no hay ejecución.
- El caso no arranca con diagnóstico. Arranca con hipótesis investigable.
- El dueño expresa dolor. El sistema traduce síntomas. La investigación confirma o descarta patologías.
- Sin hallazgo con evidencia, diferencia cuantificada y comparación de fuentes, no hay diagnóstico confirmado.
- El sistema investiga. El reporte documenta. La propuesta orienta. El dueño decide.
- Si no queda registrado, no es auditable. Si no es auditable, no sirve como prueba de valor.
- SmartPyme espera, no inventa.

---

# 29. Resumen ejecutivo

SmartPyme debe funcionar como una ingeniería conversacional, semántica y operativa para PyMEs.

No se trata solo de automatizar tareas. Se trata de construir un sistema que pueda:

- escuchar el dolor del dueño,
- convertirlo en hipótesis,
- pedir la evidencia correcta,
- protegerse de datos basura,
- verificar condiciones,
- armar un expediente,
- investigar,
- diagnosticar,
- documentar,
- proponer,
- preguntar,
- registrar decisiones,
- ejecutar solo con autorización,
- medir impacto.

La analogía médica ayuda porque ordena el caos:

> paciente, síntomas, historia clínica, patología, diagnóstico, tratamiento y seguimiento.

La analogía meteorológica también ayuda porque la PyME es un sistema de variables:

> pocas constantes, muchas variables, interacción entre flujos, fricciones, presiones y desórdenes.

SmartPyme necesita modelos propios para entender ese caos.

Ese es el diferencial:

> No vender software. Construir inteligencia operativa para PyMEs reales.