# SmartPyme Clinical Kernel — Risks and Roadmap

## Estado

Documento conceptual de arquitectura y continuidad.

Este documento consolida dos piezas de razonamiento estratégico:

1. Qué puede romper o destruir el sistema arquitectónico SmartPyme.
2. Roadmap realista para evolucionar desde el Laboratorio Inicial MVP hacia un Kernel Pericial auditable.

No es una especificación de implementación inmediata.

No habilita persistencia, multiagentes ni MathEngine en el ciclo actual.

---

# 1. Para qué sirve esta arquitectura

SmartPyme existe porque muchas PyMEs viven con alta opacidad operacional.

El dueño o responsable suele tener síntomas:

```text
vendo mucho pero no queda plata
el stock no coincide
cada vez trabajamos más y estamos peor
la caja no cierra
el contador ve una cosa y la operación otra
```

El problema no es solamente falta de software.

El problema es falta de integración entre:

- narrativa humana;
- documentación;
- matemática empresarial;
- taxonomía del rubro;
- conocimiento situado del dueño;
- evidencia trazable;
- tensiones operacionales.

SmartPyme intenta convertir esa confusión en reducción dirigida de incertidumbre.

Frase rectora:

> SmartPyme no produce conocimiento estéril.
> Produce claridad operacional accionable.

---

# 2. Validación Estratégica

La dirección de desarrollo queda conceptualmente habilitada bajo una condición estricta:

```text
seguir desarrollando sí,
pero solo si se conserva la disciplina arquitectónica.
```

Lo valioso no es usar IA.

Lo valioso es sostener un sistema donde:

```text
la evidencia limita,
la matemática estructura,
la taxonomía contextualiza,
y el humano conserva soberanía operacional.
```

Esta arquitectura merece continuidad porque evita trampas frecuentes del mercado:

- dashboards vacíos;
- copilotos que improvisan;
- agentes que alucinan;
- ERPs mudos;
- automatización sin trazabilidad;
- diagnóstico sin evidencia;
- autonomía mágica sin contratos.

---

# 3. Qué puede destruir el sistema

## 3.1 Destructor principal: IA mágica

El mayor riesgo no es un competidor externo.

El mayor riesgo es degradar el sistema hacia:

```text
hagamos que el agente decida solo
```

Eso rompe:

- trazabilidad;
- coherencia;
- evidencia;
- relación fórmula/hipótesis/tensión;
- soberanía humana;
- auditabilidad.

Si el LLM empieza a decidir sin contrato, SmartPyme deja de ser laboratorio y se convierte en chatbot plausible.

---

## 3.2 Complejidad prematura

Riesgo:

- multiagentes demasiado temprano;
- graph memory antes de coherencia;
- persistencia masiva sin núcleo estable;
- autonomía operativa prematura;
- automatización de decisiones antes de cálculo auditable.

Resultado probable:

```text
sistema grande sin columna vertebral
```

---

## 3.3 Romanticismo técnico

Riesgo:

```text
enamorarse de la arquitectura
y olvidar el dolor real del dueño
```

El dueño no compra ontologías.

Compra:

- claridad;
- menos pérdida;
- menos caos;
- menos ceguera operacional;
- mejores decisiones.

---

## 3.4 Paranoia documental

Si el sistema pide demasiada evidencia, se vuelve inviable.

Regla:

```text
pedir la mínima evidencia
que maximiza reducción de incertidumbre
```

No convertir el laboratorio en tortura administrativa.

---

## 3.5 Pérdida de soberanía humana

Si el dueño siente que la máquina impone realidad, rechaza el sistema.

El humano debe conservar:

- validación;
- contexto;
- capacidad de corregir;
- derecho a contradecir;
- rol dentro del circuito de evidencia.

---

# 4. Amenazas externas

## 4.1 ERPs con capa clínica

Un ERP grande podría incorporar:

- trazabilidad;
- diagnóstico incremental;
- tensión operacional;
- evidencia contextual.

Pero su dificultad estructural será operar sobre caos real sin exigir orden previo.

---

## 4.2 Verticales hiper especializados

Un sistema especializado en gastronomía, retail, logística o industria podría competir si posee conocimiento taxonómico profundo.

Esto confirma que los tanques de conocimiento son activos estratégicos.

---

# 5. Fortaleza diferencial

La fortaleza de SmartPyme es no depender únicamente del LLM.

El valor está en:

- contratos;
- fisiología operacional;
- taxonomías;
- DAGs matemáticos;
- coherentización;
- circuitos de evidencia;
- observabilidad;
- HumanKnowledgeMap;
- manejo explícito de incertidumbre.

Frase rectora:

> Los LLMs se comoditizan.
> La disciplina epistemológica no.

---

# 6. Roadmap Realista

## Fase 0 — Blindaje del Núcleo MVP

Estado: en curso.

Objetivo:

```text
cerrar coherencia contractual mínima
antes de escalar complejidad
```

Componentes:

- AdmissionPipelineV1;
- DDIArtifact;
- primary_hypothesis_id;
- formatter determinístico;
- reasoning trace;
- required_evidence;
- tests;
- fallback seguro.

Paso inmediato:

```text
AdmissionResponseFormatterV1
→ obedecer primary_hypothesis_id
→ tests específicos
```

No abrir todavía:

- persistencia;
- graph memory;
- multiagentes;
- autonomía.

---

## Fase 1 — Anamnesis Constitutiva

Objetivo:

```text
transformar onboarding
en baseline epistemológica
```

Componentes:

- TaxonomyHypothesis;
- HumanKnowledgeMap;
- ObservabilityBaseline;
- OperationalMaturityIndex;
- raw_narrative_stream;
- síntomas iniciales.

Resultado:

```text
organismo operacional inicializado
```

---

## Fase 2 — Catálogos Fisiológicos

Objetivo:

```text
externalizar conocimiento de dominio
```

Crear:

- FormulaCatalog;
- PathologyCatalog;
- TaxonomyCatalog;
- NormalityPolicyCatalog.

Con:

- versionado;
- tenant policies;
- thresholds;
- dependencias;
- fórmulas conectadas.

Resultado:

```text
kernel desacoplado del dominio
```

---

## Fase 3 — MathEngine V1

Objetivo:

```text
pasar de heurística narrativa
a fisiología computable
```

Capacidades:

- DAG matemático;
- propagación;
- variables trazables;
- INSUFFICIENT_DATA;
- cálculo incremental;
- causalidad fisiológica.

Salida:

```text
Verdad Computada
```

No diagnóstico todavía.

---

## Fase 4 — PathologyEvaluator

Objetivo:

```text
convertir cálculo en tensión operacional
```

Capacidades:

- thresholds;
- comparación contextual;
- severidad;
- anomalías;
- TensionNodes;
- fail-closed.

Salida:

```text
estado fisiológico auditable
```

---

## Fase 5 — Coherentización

Objetivo:

```text
evitar fractura cognitiva interna
```

Componentes:

- AdmissionCoherenceGuard;
- validación narrativa ↔ fórmula ↔ evidencia;
- resolución de contradicciones;
- manejo de disonancia;
- EvidenceConflict states.

Regla:

```text
la contradicción no rompe;
dinamiza ciclos
```

---

## Fase 6 — Persistencia Clínica

Objetivo:

```text
dar memoria longitudinal al organismo
```

Incluye:

- snapshots DDI;
- timeline operacional;
- evolución de patologías;
- aprendizaje longitudinal;
- trazabilidad histórica.

Recién acá:

- Supabase clínico;
- graph persistence;
- longitudinal memory.

---

## Fase 7 — OCR / BEM / Ingesta

Objetivo:

```text
alimentar automáticamente variables y evidencia
```

Entradas:

- PDF;
- Excel;
- extractos;
- POS;
- ERP;
- bancos;
- WhatsApp/documental.

Regla:

```text
BEM no diagnostica;
solo cura evidencia
```

---

## Fase 8 — Runtime Conversacional Real

Objetivo:

```text
convertir el laboratorio
en organismo vivo continuo
```

Capacidades:

- sesiones persistentes;
- ciclos clínicos;
- seguimiento;
- alertas;
- recalculado incremental;
- loops de aclaración.

---

## Fase 9 — Multiagente

Última fase. No antes.

Prerequisitos:

- fisiología estable;
- coherencia;
- contratos;
- trazabilidad;
- memoria;
- cálculo;
- taxonomía.

Agentes posibles:

- Hermes;
- Auditor;
- Intake;
- MathAgent;
- EvidenceAgent;
- TaxonomyAgent.

Sin esos prerequisitos:

```text
multiagentes = caos amplificado
```

---

## Fase 10 — Kernel Universal

Objetivo:

```text
desacoplar completamente el dominio PyME
```

Resultado final:

```text
Sistema Operativo Pericial
```

Dominios enchufables:

- auditoría;
- fraude;
- industria;
- legal;
- compliance;
- salud operacional;
- logística;
- gobierno;
- supply chain.

---

# 7. Secuencia Rectora

El orden importa.

La secuencia correcta es:

```text
coherencia
→ fisiología
→ tensión
→ memoria
→ automatización
→ multiagencia
```

No al revés.

---

# 8. Veredicto

El sistema puede morir si se vuelve espectáculo de IA en vez de laboratorio operacional serio.

Pero si conserva:

- disciplina;
- contratos;
- trazabilidad;
- coherencia;
- reducción honesta de incertidumbre;
- soberanía humana;

puede transformarse en una categoría nueva.
