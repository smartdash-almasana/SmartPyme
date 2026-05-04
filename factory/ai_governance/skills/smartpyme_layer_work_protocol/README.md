# smartpyme_layer_work_protocol

## Propósito operativo

Este protocolo gobierna cómo se trabaja cada capa de SmartPyme Factory.

No es teoría. Es una regla de ejecución para evitar deriva, auditorías infinitas y cambios sin cierre.

## Ciclo obligatorio por capa

Cada capa se trabaja siempre en este orden:

```text
1. DEFINIR
2. CONTRATAR
3. IMPLEMENTAR
4. INTEGRAR
5. AUDITAR
6. CERRAR
7. DOCUMENTAR
```

No se puede saltar de fase sin cierre explícito.

---

## Etiqueta obligatoria de ruteo por prompt

Todo prompt operativo debe salir ya etiquetado con modelo destino.

No se pregunta qué modelo usar. El copiloto define el ruteo según dificultad, riesgo y tipo de tarea.

Campo obligatorio:

```text
MODEL_TARGET:
```

Valores permitidos:

```text
CODEX
DEEPSEEK_4_PRO
DEEPSEEK_3_2
```

Si falta `MODEL_TARGET`, el agente debe responder:

```text
BLOCKED_MODEL_TARGET_MISSING
```

Si el valor no está permitido, debe responder:

```text
BLOCKED_MODEL_TARGET_INVALID
```

### Criterio de ruteo

```text
CODEX:
  código delicado, refactor, integración con riesgo, tests complejos.

DEEPSEEK_4_PRO:
  tarea larga, razonamiento fuerte, integración de varios contratos, recuperación cuando DeepSeek 3.2 se traba.

DEEPSEEK_3_2:
  patch chico, auditoría acotada, verificación documental simple, contratos mínimos, tests puntuales.
```

Regla:

```text
El modelo se elige por dificultad y riesgo, no por costumbre.
```

---

## 1. DEFINIR

Objetivo:

```text
Aclarar qué significa la capa y qué frontera semántica tiene.
```

Salida obligatoria:

```text
CAPA:
PROPOSITO:
ENTRA:
SALE:
NO_HACE:
CONTRATOS_ESPERADOS:
MODEL_TARGET:
BLOQUEOS:
```

Regla:

```text
Si no se puede decir qué entra, qué sale y qué no hace, no se implementa.
```

---

## 2. CONTRATAR

Objetivo:

```text
Crear o ajustar contratos mínimos de código.
```

Permitido:

```text
app/contracts/
tests/contracts/
```

Salida obligatoria:

```text
VEREDICTO:
CONTRATOS_CREADOS:
TESTS:
MODEL_TARGET:
LIMITES:
NEXT_STEP:
```

Reglas:

- Contratos primero.
- Integración después.
- No tocar pipeline.
- No tocar orquestadores.
- No tocar MCP.
- No tocar documentación conceptual.

---

## 3. IMPLEMENTAR

Objetivo:

```text
Completar la pieza mínima interna de la capa.
```

Permitido:

```text
Máximo 2 archivos productivos.
Máximo 1 archivo de test.
```

Reglas:

- No rediseñar.
- No auditar repo completo.
- No abrir otros frentes.
- Si falta punto claro: BLOCKED_IMPLEMENTATION_POINT.

---

## 4. INTEGRAR

Objetivo:

```text
Conectar la pieza al punto existente más cercano del flujo.
```

Antes de modificar, el agente debe declarar:

```text
PUNTO_DE_INTEGRACION:
ARCHIVOS_A_MODIFICAR:
TEST_A_MODIFICAR:
MODEL_TARGET:
```

Límites:

```text
Máximo 5 archivos leídos.
Máximo 2 búsquedas.
Máximo 2 archivos productivos modificados.
Máximo 1 test modificado.
```

Bloqueos:

```text
BLOCKED_INTEGRATION_POINT
BLOCKED_SCOPE_VIOLATION
BLOCKED_CONTRACT_UNCERTAINTY
BLOCKED_MODEL_TARGET_MISSING
BLOCKED_MODEL_TARGET_INVALID
```

Regla:

```text
Si no puede integrarse con lectura corta, no se integra: se bloquea.
```

---

## 5. AUDITAR

Objetivo:

```text
Verificar el patch ya hecho contra la capa definida.
```

La auditoría NO debe buscar nueva arquitectura.

Debe revisar solo:

```text
- si respetó la capa;
- si tocó archivos permitidos;
- si los tests pasan;
- si introdujo decisión, diagnóstico o ejecución donde no corresponde;
- si dejó worktree sucio;
- si requiere corrección mínima;
- si el MODEL_TARGET fue adecuado al riesgo.
```

Salida obligatoria:

```text
VEREDICTO:
ARCHIVOS_REVISADOS:
CUMPLE_CAPA:
MODEL_TARGET:
MODEL_TARGET_ADECUADO:
VIOLACIONES:
TEST_RESULT:
CORRECCION_MINIMA:
NEXT_STEP:
```

---

## 6. CERRAR

Objetivo:

```text
Dejar la rama limpia y sincronizada.
```

Cierre válido:

```text
TESTS_PASS
COMMIT
PUSH
GIT_STATUS_CLEAN
```

Salida obligatoria:

```text
VEREDICTO:
RAMA:
COMMIT:
PUSH_RESULT:
GIT_STATUS:
MODEL_TARGET:
NEXT_STEP:
```

Sin cierre no se abre otra capa.

---

## 7. DOCUMENTAR

Objetivo:

```text
Documentar lo construido después del cierre técnico.
```

Regla:

```text
El paper/doc no se escribe antes del cierre técnico.
```

El documento debe describir:

```text
- qué capa se cerró;
- qué contratos existen;
- qué integración se hizo;
- qué límites quedan;
- cuál es el próximo frente;
- qué modelo fue usado para cada prompt operativo.
```

No debe inventar futuro ni abrir arquitectura nueva.

---

## Protocolo actual para Capa 03

Estado:

```text
CAPA: 03
FLUJO: OperationalCase -> DiagnosticReport -> ActionProposal
CONTRATOS: creados y testeados
INTEGRACION: pendiente
AUDITORIA: pendiente después de integración
CIERRE: pendiente después de auditoría
DOCUMENTACION: solo después del cierre
```

Ruteo recomendado para Capa 03:

```text
CONTRATAR: DEEPSEEK_3_2
INTEGRAR: DEEPSEEK_4_PRO o CODEX según riesgo del punto de integración
AUDITAR: DEEPSEEK_3_2
DOCUMENTAR: DEEPSEEK_3_2
```

Reglas semánticas de Capa 03:

```text
OperationalCase no diagnostica.
DiagnosticReport no ejecuta.
ActionProposal no autoriza.
El dueño decide.
Sin evidencia trazable no hay diagnóstico confirmado.
Sin comparación entre fuentes no hay hallazgo fuerte.
Sin diferencia cuantificada no hay hallazgo accionable.
```

## Formato mínimo para cualquier próximo prompt

Todo próximo prompt debe empezar así:

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

Si falta CAPA o FASE, el agente debe responder:

```text
BLOCKED_LAYER_PHASE_MISSING
```

Si falta MODEL_TARGET, el agente debe responder:

```text
BLOCKED_MODEL_TARGET_MISSING
```
