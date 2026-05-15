# Clinical Mathematical Kernel and Human Cognitive Loop

## Propósito

Este documento consolida la evolución conceptual del Laboratorio Inicial SmartPyme hacia un sistema clínico-operacional auditable.

La tesis central es:

> SmartPyme no calcula totales.
> SmartPyme computa estados de salud operacional.

El sistema deja de ser un chatbot financiero o un software administrativo clásico y pasa a funcionar como un motor de reducción dirigida de incertidumbre.

---

# 1. Cambio Ontológico

El núcleo real del sistema no es la PyME.

El núcleo real es:

```text
motor de reducción dirigida de incertidumbre
sobre sistemas complejos auditables
```

La especialización PyME surge solamente por:

- FormulaCatalog
- PathologyCatalog
- evidencia documental
- ontología semántica
- políticas del tenant

Si esos catálogos cambian, el mismo kernel puede operar sobre:

- auditoría forense
- compliance
- fraude documental
- operaciones industriales
- análisis legal
- sistemas clínicos

---

# 2. El Dueño no es un Usuario Final

El sistema no reemplaza al conocedor.

El dueño, gerente o responsable operacional es:

```text
HumanKnowledgeNode
```

Es una fuente cognitiva situada dentro del circuito de evidencia.

El sistema debe:

- hacerlo pensar;
- obligarlo a ordenar conocimiento;
- separar intuición de evidencia;
- detectar contradicciones;
- pedir aclaraciones dirigidas;
- incorporar conocimiento contextual no documentado.

Frase canónica:

> SmartPyme no reemplaza al conocedor.
> Lo convierte en parte activa del circuito de evidencia.

---

# 3. Pipeline Cognitivo-Operacional

```text
narrativa humana
→ hipótesis
→ fórmulas/reglas
→ variables faltantes
→ evidencia requerida
→ pregunta dirigida al conocedor
→ documento o aclaración
→ cálculo/tensión
→ nueva pregunta mejor
```

La narrativa no produce diagnósticos.

La narrativa activa hipótesis.

Las hipótesis activan fórmulas.

Las fórmulas exigen variables.

Las variables exigen evidencia.

La evidencia habilita cálculo.

El cálculo produce tensión o descarta sospecha.

---

# 4. Arquitectura del Matematizador Pericial

## 4.1 Principio Central

La matemática no es una herramienta auxiliar.

Es:

```text
el marco de leyes físicas
contra el cual se estrella la narrativa
para extraer la realidad operacional
```

---

## 4.2 Separación en Tres Capas

```text
+-------------------------------------------------------------------------+
| Layer 1: FormulaCatalog                                                 |
| (Definición estática de leyes matemáticas, exigencias e invariantes)    |
+------------------------------------+------------------------------------+
                                     | Prové esquema/expresión
                                     v
+-------------------------------------------------------------------------+
| Layer 2: MathEngine / Matematizador                                     |
| (Evaluador puramente reactivo. Valida procedencia, computa o declara   |
| INSUFFICIENT_DATA compilando variables faltantes de forma determinista) |
+------------------------------------+------------------------------------+
                                     | Inyecta Cómputo / Hecho
                                     v
+-------------------------------------------------------------------------+
| Layer 3: PathologyEvaluator                                             |
| (Contrasta la Verdad Computada contra las condiciones del catálogo y   |
| los límites del tenant. Dispara la Tensión)                             |
+-------------------------------------------------------------------------+
```

---

# 5. Axiomas del Matematizador

## Axioma 1 — Variable Trazable

El matematizador no recibe números planos.

Recibe:

```text
Variables con procedencia
```

Cada variable debe declarar:

- valor matemático;
- source_id;
- evidence_id/fact_id;
- tenant_id;
- confidence;
- timestamp;
- origen humano o documental.

Si no existe trazabilidad:

```text
NO CALCULAR
```

---

## Axioma 2 — DAG Fisiológico

Las fórmulas viven dentro de un:

```text
grafo acíclico dirigido
```

Ejemplo:

```text
Costo Unitario
→ CMV
→ Margen Bruto
→ Margen Neto
→ Punto de Equilibrio
→ Flujo de Caja
```

Los cambios en variables raíz deben propagarse automáticamente.

El sistema también debe poder recorrer el DAG hacia atrás para aislar causas raíz.

---

## Axioma 3 — INSUFFICIENT_DATA

La falta de datos no es excepción técnica.

Es:

```text
estado clínico ejecutable
```

Ejemplo:

```text
FormulaNode: margen_bruto
required_inputs:
- ventas
- cmv

available:
- ventas

missing:
- cmv

state:
INSUFFICIENT_DATA
```

El sistema compila automáticamente:

- missing_variables
- incertidumbre activa
- evidencia requerida
- pregunta dirigida

---

## Axioma 4 — Tensión Patológica

El cálculo no produce diagnóstico.

Produce:

```text
Verdad Computada
```

Luego:

```text
PathologyEvaluator
```

contrasta:

- resultado matemático;
- tenant_policy;
- thresholds;
- patologías conocidas.

El resultado es:

```text
TensionNode
```

No opinión.

No intuición.

Desvío explícito y auditable.

---

# 6. Coherencia Cognitiva

La contradicción no debe romper el sistema.

Debe:

```text
abrir tensión
→ reducir confianza
→ pedir evidencia dirigida
→ esperar nuevo ciclo semántico/documental
```

Frase canónica:

> SmartPyme no resuelve la disonancia inventando certeza.
> La metaboliza abriendo ciclos de evidencia, semántica y documentación.

---

# 7. Justificación Documental

El sistema no debe pedir documentos arbitrariamente.

Cada evidencia debe justificar:

```text
qué incógnita matemática intenta cerrar
```

Frase canónica:

> SmartPyme no pide evidencia para acumular documentos.
> Pide evidencia para cerrar incógnitas matemáticas asociadas a hipótesis activas.

---

# 8. Fórmulas como Entidades de Primer Nivel

Las fórmulas no deben existir como helpers ocultos.

Deben modelarse explícitamente:

```text
FormulaNode
```

Ejemplo conceptual:

```text
FormulaNode:
MargenBruto

requiere:
- ventas
- costo_mercaderia

deriva:
- rentabilidad_operativa

impacta:
- caja
- pricing
- reposición

patologías_asociadas:
- margen erosionado
- precio mal calculado
- inflación oculta
```

---

# 9. Veredicto Arquitectónico

SmartPyme evoluciona hacia:

```text
Sistema Operativo Pericial
```

o:

```text
Kernel Epistemológico Auditable
```

La PyME es solamente el primer organismo operacional sobre el cual validar esta fisiología.
