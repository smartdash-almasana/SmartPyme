# Regla de Bloqueo

## 1. PRINCIPIO
Si hay duda, no ejecuta y pregunta.

## 2. DISPARADORES DE BLOQUEO
- archivo destino no claro
- clasificación del slice no es A o B
- contradicción con arquitectura real
- dependencia crítica no declarada
- cambio exige tocar más módulos de los permitidos
- tests fallan y la causa no está clara
- contratos incompatibles
- más de una interpretación razonable

## 3. ACCION OBLIGATORIA
- detener ejecución
- no modificar más archivos
- completar sección BLOQUEO
- mover hallazgo a blocked

## 4. FORMATO EXACTO DE PREGUNTA AL OWNER
Usar este formato markdown, sin ambigüedad y con decisión explícita:

```markdown
## PREGUNTA_AL_OWNER
Contexto breve: <1-2 líneas con el conflicto puntual>
Decisión requerida: <qué debe decidir el owner>
Opciones:
- A) <opción 1>
- B) <opción 2>
Impacto: <qué se bloquea si no responde>
```

Ejemplo corto:

```markdown
## PREGUNTA_AL_OWNER
Contexto breve: El hallazgo indica portar validación de saldo, pero hay dos destinos posibles (`src/cobranzas/validator.py` o `src/facturacion/validator.py`).
Decisión requerida: Confirmar archivo destino único para aplicar el cambio.
Opciones:
- A) `src/cobranzas/validator.py`
- B) `src/facturacion/validator.py`
Impacto: Sin esta definición no se puede continuar sin riesgo de modificar el módulo equivocado.
```
