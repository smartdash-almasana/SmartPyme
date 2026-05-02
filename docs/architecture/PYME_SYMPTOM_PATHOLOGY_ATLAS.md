# SmartPyme — Atlas clínico-operativo de síntomas y patologías PyME

## Principio central
El sistema no pide datos porque sí.
Pide datos porque una hipótesis necesita variables y evidencia para ser verificada.

## Flujo semántico
dolor expresado
→ síntoma operativo
→ patología posible
→ hipótesis investigable
→ skill candidata
→ variables necesarias
→ evidencia requerida
→ diagnóstico

## Definiciones
- **Dolor del dueño:** formulación humana del problema.
- **Síntoma operativo:** señal observable traducida por el sistema.
- **Patología PyME:** patrón recurrente de daño, fricción o desorden operativo.
- **Hipótesis investigable:** formulación verificable, no diagnóstico.
- **Skill:** capacidad técnica para investigar.
- **Variables necesarias:** datos escalares mínimos.
- **Evidencia requerida:** documentos/fuentes necesarios para contrastar.

## Ejemplos iniciales

### 1. Pérdida de margen
**Dolor:**
“Creo que estoy perdiendo plata / margen.”

**Síntomas posibles:**
- margen percibido menor al esperado
- precios desactualizados
- costos de proveedor cambiantes
- descuentos no controlados
- ventas sin costo real asociado

**Patologías posibles:**
- desalineación costo-precio
- costos de reposición no actualizados
- descuentos o promociones mal aplicadas
- mix de productos deteriorado
- comisiones/impuestos no incorporados
- merma o pérdida de stock que afecta margen real

**Hipótesis:**
“Investigar si existe pérdida de margen por desalineación entre costos reales y precios de venta durante un período determinado.”

**Skill candidata:**
`skill_margin_leak_audit`

**Variables necesarias:**
- período
- productos o familias
- markup_objetivo o margen esperado
- costo_reposicion si está disponible
- precio_venta_real si está disponible

**Evidencia requerida:**
- ventas / POS / Excel de ventas
- facturas de proveedores
- listas de precios o costos
- reportes de descuentos/promociones si existen
- inventario/merma si aplica

**Justificación:**
Para investigar margen hay que comparar precio real cobrado contra costo real o costo de reposición. Sin ventas y costos no se puede confirmar ni descartar pérdida de margen.

### 2. Desorden de stock
**Dolor:** “No sé si me falta stock”
**Síntoma:** sospecha de pérdida o desorden de inventario
**Patologías:** merma, robo hormiga, carga incorrecta, ventas no registradas, compras no asentadas
**Skill:** `skill_stock_loss_detect`
**Evidencia:** inventario físico, ventas POS, compras, ajustes de stock

### 3. Conciliación de caja/banco
**Dolor:** “No me cierra la caja / banco”
**Síntoma:** diferencia entre cobros, ventas y depósitos
**Patologías:** conciliación bancaria fallida, ventas no registradas, comisiones no consideradas, retiros no documentados
**Skill:** `skill_reconcile_bank_vs_pos`
**Evidencia:** extracto bancario, reporte POS, caja diaria, período

### 4. Exceso de manualidad
**Dolor:** “Trabajo demasiado manual”
**Síntoma:** repetición operativa innecesaria
**Patologías:** falta de automatización, dependencia de personas, duplicación de carga, riesgo de error humano
**Skill:** `skill_process_automation_audit`
**Evidencia:** descripción del flujo, archivos usados, frecuencia, personas involucradas, tiempo dedicado

### 5. Incertidumbre productiva
**Dolor:** “No sé si gano plata con producir esto”
**Síntoma:** incertidumbre de costo productivo
**Patologías:** BOM incompleto, costos indirectos no imputados, materia prima sin costo actualizado, mano de obra no considerada
**Skill:** `skill_bom_cost_audit`
**Evidencia:** lista de materiales, cantidades, costos unitarios, producción estimada, precio final

## Reglas semánticas
- Dolor expresado no es diagnóstico.
- Síntoma no es patología confirmada.
- Patología posible no es hallazgo.
- Hallazgo requiere evidencia, comparación y diferencia cuantificada.
- Si falta evidencia mínima, se pide aclaración.
- No se crea `OperationalCase` sin material suficiente.

## Relación con catálogos existentes
Este atlas es la capa anterior a:
- `operational_conditions_catalog.py`

El atlas responde: **“¿Por qué esta demanda lleva a esta skill?”**
El catálogo de condiciones responde: **“¿Qué datos hacen falta para ejecutar esta skill?”**

## Relación con el dueño
El dueño es fuente de demanda, contexto, documentos, convalidación y autorización.
El sistema debe ser **no invasivo en tono** pero **duro en condiciones**.

---
*Nota: Este documento describe el marco conceptual y no implica que todos los componentes estén implementados como código.*
