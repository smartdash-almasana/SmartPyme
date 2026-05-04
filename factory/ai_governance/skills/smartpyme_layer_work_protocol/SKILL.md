## SmartPyme Layer Work Protocol

metadata:
  hermes:
    category: governance
    tags: [smartpyme, layer, phase, model-target, protocol]
---

# smartpyme_layer_work_protocol

## Regla obligatoria

Toda orden operativa debe declarar:

```text
CAPA:
FASE:
MODEL_TARGET:
OBJETIVO:
ARCHIVOS_PERMITIDOS:
PROHIBIDO:
TEST:
SALIDA:
```

Si falta CAPA o FASE, responder:

```text
BLOCKED_LAYER_PHASE_MISSING
```

Si falta MODEL_TARGET, responder:

```text
BLOCKED_MODEL_TARGET_MISSING
```

Valores permitidos de MODEL_TARGET:

```text
CODEX
DEEPSEEK_4_PRO
DEEPSEEK_3_2
```

Si el valor no corresponde, responder:

```text
BLOCKED_MODEL_TARGET_INVALID
```

## Ciclo por capa

```text
DEFINIR -> CONTRATAR -> IMPLEMENTAR -> INTEGRAR -> AUDITAR -> CERRAR -> DOCUMENTAR
```

No abrir otra fase sin cierre explícito de la anterior.

## Fases

### DEFINIR

Aclarar qué entra, qué sale y qué no hace la capa.

### CONTRATAR

Crear contratos mínimos y tests de contrato. No integrar.

### IMPLEMENTAR

Completar una pieza mínima interna. No rediseñar.

### INTEGRAR

Conectar al punto existente más cercano. Antes de modificar, declarar:

```text
PUNTO_DE_INTEGRACION:
ARCHIVOS_A_MODIFICAR:
TEST_A_MODIFICAR:
MODEL_TARGET:
```

### AUDITAR

Auditar solo el patch ya hecho. No buscar arquitectura nueva.

### CERRAR

Cierre válido:

```text
TESTS_PASS
COMMIT
PUSH
GIT_STATUS_CLEAN
```

### DOCUMENTAR

Solo después del cierre técnico.

## Ruteo por modelo

```text
CODEX: código delicado, refactor, integración con riesgo, tests complejos.
DEEPSEEK_4_PRO: tarea larga, razonamiento fuerte, integración de varios contratos, fallback si 3.2 se traba.
DEEPSEEK_3_2: patch chico, auditoría acotada, verificación documental, contratos mínimos, tests puntuales.
```

El modelo se elige por dificultad y riesgo. No se pregunta.

## Capa 03 vigente

```text
CAPA: 03
FLUJO: OperationalCase -> DiagnosticReport -> ActionProposal
CONTRATOS: creados y testeados
INTEGRACION: en curso
AUDITORIA: después de integración
CIERRE: después de auditoría
DOCUMENTACION: solo después del cierre
```

Reglas:

```text
OperationalCase no diagnostica.
DiagnosticReport no ejecuta.
ActionProposal no autoriza.
El dueño decide.
Sin evidencia trazable no hay diagnóstico confirmado.
Sin comparación entre fuentes no hay hallazgo fuerte.
Sin diferencia cuantificada no hay hallazgo accionable.
```
