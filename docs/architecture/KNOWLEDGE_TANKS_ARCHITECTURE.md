# SmartPyme — Arquitectura de Tanques de Conocimiento

## Estado

Documento conceptual crítico.

Este documento desarrolla la idea de que los catálogos de SmartPyme no son solamente “paquetes de dominio”, sino **tanques de conocimiento desmontables y combinables**.

La intuición central:

```text
El core opera.
Los tanques alimentan.
El dominio se arma combinando tanques.
```

---

## Propósito

Definir una arquitectura conceptual donde el sistema operativo organizacional pueda funcionar sobre distintos tipos de organizaciones mediante la combinación de tanques de conocimiento.

Esto permite especializar SmartPyme para:

```text
- PyMEs generales;
- gastronomía;
- metalúrgica;
- agro;
- petróleo;
- salud;
- educación;
- logística;
- retail;
- industria textil;
- servicios profesionales;
- organizaciones sociales;
- otros rubros.
```

Sin reescribir el core.

---

## Principio central

```text
El sistema operativo es estable.
El conocimiento es desmontable.
Los tanques se montan según el cliente, rubro y problema.
```

---

## Diferencia entre core y tanques

### Core operativo

El core conserva la estructura general:

```text
recepción
→ conversación mayéutica
→ interpretación
→ curación
→ condiciones
→ hipótesis
→ caso operativo
→ investigación
→ reporte diagnóstico
→ propuesta
→ decisión registrada
→ autorización
→ acción controlada
→ trazabilidad
```

El core no debería saber de gastronomía, metalurgia, clínica o agricultura en forma rígida.

---

### Tanques de conocimiento

Los tanques contienen la base semántica, técnica y operativa que alimenta al sistema.

Pueden contener:

```text
- síntomas;
- patologías;
- fórmulas;
- protocolos;
- variables;
- evidencias;
- benchmarks;
- buenas prácticas;
- preguntas mayéuticas;
- lenguaje del rubro;
- riesgos típicos;
- modelos operativos;
- criterios de diagnóstico;
- criterios de impacto;
- skills especializadas.
```

---

## Qué es un tanque de conocimiento

Un tanque de conocimiento es un módulo semántico y operativo que puede conectarse al sistema para darle conocimiento sobre un área.

Ejemplo:

```text
tanque_contabilidad
tanque_finanzas
tanque_impuestos
tanque_compras
tanque_proveedores
tanque_gastronomia
tanque_metalurgica
tanque_agro
tanque_salud
```

Cada tanque contiene conocimiento específico, pero el sistema conserva el mismo método de operación.

---

## Tanques transversales

Los tanques transversales son comunes a muchas organizaciones.

Ejemplos:

```text
- contabilidad;
- finanzas;
- impuestos;
- compras;
- proveedores;
- ventas;
- caja y banco;
- costos básicos;
- recursos humanos;
- documentación administrativa;
- gestión de clientes;
- gestión de stock;
- facturación;
- cumplimiento normativo.
```

Estos tanques no pertenecen a un rubro específico.

Una clínica, una metalúrgica y una pyme gastronómica pueden compartir:

```text
contabilidad
finanzas
impuestos
proveedores
caja/banco
recursos humanos
```

---

## Tanques sectoriales

Los tanques sectoriales son propios de un rubro o actividad.

Ejemplos:

```text
- gastronomía;
- metalúrgica;
- agricultura;
- petróleo;
- salud;
- educación;
- logística;
- retail;
- industria textil;
- construcción;
- software;
- transporte;
- hotelería;
- servicios profesionales.
```

Cada rubro tiene su propia sintomatología, sus patologías típicas y sus buenas prácticas.

---

## Ejemplo: cliente gastronómico

Un cliente gastronómico podría usar:

```text
tanque_contabilidad
+ tanque_finanzas
+ tanque_compras
+ tanque_proveedores
+ tanque_stock
+ tanque_recursos_humanos
+ tanque_gastronomia
```

### Síntomas posibles

```text
- desperdicio de materia prima;
- margen bajo por plato;
- compras mal planificadas;
- exceso de personal en ciertos turnos;
- faltantes de insumos críticos;
- ventas altas pero caja baja;
- platos rentables invisibles;
- platos populares no rentables.
```

### Evidencia típica

```text
- compras de proveedores;
- recetas;
- comandas;
- ventas por producto;
- stock de cocina;
- turnos de personal;
- mermas;
- precios de menú.
```

### Patologías posibles

```text
- receta sin costo actualizado;
- merma no medida;
- proveedor caro;
- precio de menú desalineado;
- compras reactivas;
- exceso de personal por turno;
- falta de ingeniería de menú.
```

---

## Ejemplo: cliente metalúrgico

Un cliente metalúrgico podría usar:

```text
tanque_contabilidad
+ tanque_finanzas
+ tanque_compras
+ tanque_proveedores
+ tanque_produccion_industrial
+ tanque_metalurgica
+ tanque_mantenimiento
```

### Síntomas posibles

```text
- costo real de pieza desconocido;
- demora de producción;
- desperdicio de material;
- retrabajo;
- máquinas paradas;
- presupuestos mal calculados;
- margen bajo por orden de trabajo.
```

### Evidencia típica

```text
- órdenes de producción;
- listas de materiales;
- tiempos de máquina;
- costos de insumos;
- horas hombre;
- desperdicio;
- mantenimiento;
- presupuestos;
- facturas de compra.
```

### Patologías posibles

```text
- BOM incompleto;
- tiempos productivos mal estimados;
- merma no imputada;
- mantenimiento reactivo;
- presupuesto sin costos indirectos;
- costo de mano de obra subestimado;
- cuello de botella de máquina.
```

---

## Ejemplo: cliente agro

Un cliente agro podría usar:

```text
tanque_contabilidad
+ tanque_finanzas
+ tanque_impuestos
+ tanque_compras
+ tanque_agro
+ tanque_logistica
+ tanque_maquinaria
```

### Síntomas posibles

```text
- costo por hectárea poco claro;
- baja rentabilidad por campaña;
- insumos caros;
- mala planificación de siembra;
- maquinaria ociosa o sobredemandada;
- logística ineficiente;
- baja trazabilidad de gastos.
```

### Evidencia típica

```text
- insumos;
- semillas;
- fertilizantes;
- combustible;
- maquinaria;
- hectáreas trabajadas;
- rindes;
- fletes;
- precios de venta;
- contratos.
```

### Patologías posibles

```text
- costo por hectárea subestimado;
- insumos no imputados;
- logística cara;
- maquinaria mal asignada;
- rendimiento menor al esperado;
- mala planificación financiera de campaña.
```

---

## Ejemplo: clínica de salud

Un cliente de salud podría usar:

```text
tanque_contabilidad
+ tanque_finanzas
+ tanque_rrhh
+ tanque_salud
+ tanque_turnos
+ tanque_facturacion_medica
```

### Síntomas posibles

```text
- demoras en turnos;
- baja ocupación de agenda;
- prestaciones no facturadas;
- historias clínicas incompletas;
- pacientes que abandonan tratamiento;
- saturación de recepción;
- baja rentabilidad por prestación.
```

### Evidencia típica

```text
- agenda de turnos;
- historias clínicas;
- autorizaciones de obras sociales;
- facturación;
- prestaciones realizadas;
- tiempos de atención;
- ausentismo;
- nómina profesional.
```

### Patologías posibles

```text
- cuello de botella asistencial;
- agenda mal distribuida;
- facturación incompleta;
- falta de seguimiento del paciente;
- documentación clínica incompleta;
- mala asignación de profesionales.
```

---

## Diferencia entre Domain Pack y Knowledge Tank

### Knowledge Tank

Un tanque es una unidad modular de conocimiento.

Ejemplo:

```text
tanque_contabilidad
tanque_gastronomia
tanque_stock
```

### Domain Pack

Un paquete de dominio es una combinación de tanques.

Ejemplo:

```text
domain_pack_pyme_gastronomica =
  tanque_contabilidad
  + tanque_finanzas
  + tanque_compras
  + tanque_proveedores
  + tanque_stock
  + tanque_gastronomia
```

Entonces:

```text
Knowledge Tank = unidad modular.
Domain Pack = ensamble de tanques para un tipo de cliente.
```

---

## Arquitectura conceptual

```text
Organizational Operating System
│
├── Core operativo
│   ├── recepción
│   ├── conversación
│   ├── curación
│   ├── condiciones
│   ├── casos
│   ├── reportes
│   ├── decisiones
│   ├── autorización
│   └── trazabilidad
│
├── Tanques transversales
│   ├── contabilidad
│   ├── finanzas
│   ├── impuestos
│   ├── compras
│   ├── proveedores
│   ├── caja/banco
│   └── recursos humanos
│
└── Tanques sectoriales
    ├── gastronomía
    ├── metalúrgica
    ├── agro
    ├── salud
    ├── educación
    ├── logística
    └── retail
```

---

## Cómo se arma un cliente

Cuando se incorpora un cliente, el sistema podría definir:

```text
organization_id
organization_type
domain_pack
knowledge_tanks_enabled
disabled_tanks
custom_tanks
```

Ejemplo:

```yaml
organization_id: cliente_123
organization_type: pyme_gastronomica

knowledge_tanks_enabled:
  - contabilidad
  - finanzas
  - compras
  - proveedores
  - stock
  - gastronomia
  - recursos_humanos
```

---

## Activación por demanda

No todos los tanques se usan todo el tiempo.

Una demanda activa ciertos tanques.

Ejemplo:

```text
“Creo que pierdo margen con algunos platos.”
```

Activa:

```text
tanque_gastronomia
tanque_costos
tanque_compras
tanque_proveedores
tanque_ventas
```

Ejemplo:

```text
“No me cierra el banco.”
```

Activa:

```text
tanque_finanzas
tanque_caja_banco
tanque_ventas
tanque_contabilidad
```

---

## Método común con tanques distintos

La conversación sigue siendo mayéutica:

```text
preguntar poco,
preguntar claro,
preguntar lo necesario.
```

Pero las preguntas dependen de los tanques activos.

### Gastronomía

```text
¿Tenés recetas, costos de ingredientes y ventas por plato?
```

### Metalúrgica

```text
¿Tenés lista de materiales, tiempos de máquina y costo de insumos?
```

### Clínica

```text
¿Tenés agenda de turnos, tiempos de atención y prestaciones facturadas?
```

---

## Método interno con tanques distintos

El método hipotético-deductivo sigue igual.

```text
dolor
→ síntoma
→ hipótesis
→ evidencia requerida
→ prueba
→ diagnóstico
```

Pero cada tanque define:

```text
- cómo se formula el síntoma;
- qué patologías pueden estar asociadas;
- qué evidencia se necesita;
- qué fórmulas o protocolos aplican;
- qué hallazgos son válidos;
- qué impacto se mide.
```

---

## Relación con el catálogo síntoma-patología

El `SymptomPathologyCatalog` debería estar organizado por tanques.

Ejemplo:

```text
tanque_gastronomia.symptoms
tanque_metalurgica.symptoms
tanque_finanzas.symptoms
tanque_stock.symptoms
```

Esto permite que un mismo sistema responda distinto según el dominio.

---

## Relación con evidencias

Cada tanque debe declarar qué evidencias entiende.

Ejemplo:

### Tanque contabilidad

```text
- facturas;
- recibos;
- libros contables;
- liquidaciones;
- declaraciones fiscales.
```

### Tanque gastronomía

```text
- recetas;
- comandas;
- ventas por plato;
- stock de cocina;
- compras de insumos;
- mermas.
```

### Tanque salud

```text
- historia clínica;
- turnos;
- prestaciones;
- autorizaciones;
- evolución de pacientes;
- facturación médica.
```

---

## Relación con fórmulas y protocolos

No todos los tanques usan fórmulas matemáticas simples.

Algunos usan:

```text
- fórmulas;
- reglas;
- protocolos;
- checklists;
- benchmarks;
- buenas prácticas;
- indicadores.
```

Ejemplo:

### Finanzas

```text
margen
flujo de caja
conciliación
capital de trabajo
```

### Gastronomía

```text
food cost
margen por plato
merma
rotación de insumos
```

### Salud

```text
tiempo de espera
ocupación de agenda
tasa de ausentismo
prestaciones no facturadas
```

---

## Relación con buenas prácticas

Cada tanque puede declarar buenas prácticas.

Ejemplo:

### Tanque proveedores

```text
- comparar precios por período;
- detectar aumentos no trasladados;
- revisar concentración de proveedores;
- validar condiciones de pago.
```

### Tanque gastronomía

```text
- costear receta por ingrediente;
- medir merma;
- revisar rentabilidad por plato;
- controlar compras frecuentes.
```

### Tanque metalúrgica

```text
- costear por orden de producción;
- imputar horas máquina;
- medir desperdicio;
- incluir costos indirectos.
```

---

## Relación con patologías

Cada tanque trae patologías propias.

Ejemplo:

### Tanque caja/banco

```text
- conciliación fallida;
- retiros no documentados;
- comisiones no imputadas;
- diferencias por medio de pago.
```

### Tanque stock

```text
- merma;
- robo hormiga;
- compras no asentadas;
- ventas no registradas;
- error de inventario.
```

### Tanque producción

```text
- BOM incompleto;
- cuello de botella;
- tiempo productivo mal estimado;
- costos indirectos no imputados.
```

---

## Relación con reportes

El `DiagnosticReport` debe poder usar el lenguaje del tanque activo.

Ejemplo:

### Reporte PyME financiero

```text
Se detecta una diferencia de $350.000 entre ventas POS y depósitos bancarios durante marzo.
```

### Reporte gastronómico

```text
El plato X muestra un food cost estimado de 48%, superior al objetivo del 32%.
```

### Reporte salud

```text
La agenda de traumatología muestra una demora promedio de 18 días, con concentración de turnos en dos franjas horarias.
```

---

## Relación con impacto

Cada tanque puede aportar métricas de impacto.

Ejemplo:

### Finanzas

```text
amount
currency
percentage
risk_level
```

### Producción

```text
units
time_saved
scrap_rate
machine_hours
```

### Salud

```text
patients_affected
waiting_time
billing_loss
clinical_risk
```

El contrato de impacto debe ser extensible.

---

## Riesgos arquitectónicos

### 1. Contaminar el core

Riesgo:

```text
meter semántica de PyME directamente en el core
```

Mitigación:

```text
todo concepto sectorial debe vivir en tanques
```

---

### 2. Tanques demasiado grandes

Riesgo:

```text
crear tanques gigantes imposibles de mantener
```

Mitigación:

```text
separar transversales y sectoriales
```

---

### 3. Solapamiento entre tanques

Riesgo:

```text
finanzas y gastronomía definen margen de forma incompatible
```

Mitigación:

```text
jerarquía de resolución:
core → tanque transversal → tanque sectorial → override del cliente
```

---

### 4. Preguntas contradictorias

Riesgo:

```text
dos tanques piden evidencia distinta para el mismo síntoma
```

Mitigación:

```text
resolver por skill activa e hipótesis investigable
```

---

### 5. Falsa portabilidad

Riesgo:

```text
creer que cambiar nombres alcanza para cambiar de dominio
```

Mitigación:

```text
cada tanque debe incluir síntomas, patologías, evidencia, fórmulas/protocolos y buenas prácticas reales
```

---

## Jerarquía sugerida

```text
Core
→ Knowledge Tank transversal
→ Knowledge Tank sectorial
→ configuración del cliente
→ evidencia real del caso
```

---

## Reglas futuras de implementación

1. Todo tanque debe tener `tank_id`.
2. Todo tanque debe declarar qué síntomas aporta.
3. Todo tanque debe declarar qué patologías aporta.
4. Todo tanque debe declarar qué evidencias entiende.
5. Todo tanque debe declarar qué skills habilita.
6. Todo tanque debe declarar preguntas mayéuticas.
7. Todo tanque debe declarar métricas de impacto.
8. Ningún tanque debe ejecutar lógica por sí mismo.
9. El core debe consultar tanques, no depender de ellos rígidamente.
10. Un cliente puede tener múltiples tanques activos.

---

## Posible estructura técnica futura

```text
app/catalogs/knowledge_tanks/
  __init__.py
  registry.py
  base.py
  transversal/
    accounting.py
    finance.py
    taxes.py
    suppliers.py
  sectors/
    gastronomy.py
    metallurgy.py
    agro.py
    health.py
```

---

## Contrato conceptual de KnowledgeTank

```python
KnowledgeTank:
    tank_id: str
    name: str
    type: "TRANSVERSAL" | "SECTORIAL" | "CLIENT_CUSTOM"
    symptoms: list
    pathologies: list
    evidence_types: list
    skills: list
    formulas_or_protocols: list
    mayeutic_questions: list
    impact_metrics: list
    good_practices: list
```

---

## Contrato conceptual de DomainAssembly

```python
DomainAssembly:
    organization_id: str
    domain_id: str
    enabled_tanks: list[str]
    priority_order: list[str]
    overrides: dict
```

---

## Diferencia entre tanque y skill

El tanque contiene conocimiento.

La skill ejecuta una capacidad técnica.

Ejemplo:

```text
tanque_gastronomia conoce:
- food cost;
- recetas;
- mermas;
- rentabilidad por plato.

skill_food_cost_audit ejecuta:
- cálculo concreto de costo por plato;
- comparación contra precio de venta;
- hallazgo de margen.
```

---

## Diferencia entre tanque y catálogo

Un tanque puede contener varios catálogos.

Ejemplo:

```text
tanque_gastronomia:
  - symptom_catalog
  - pathology_catalog
  - evidence_catalog
  - formula_catalog
  - good_practices_catalog
```

---

## Diferencia entre tanque y domain pack

Un domain pack es una combinación de tanques.

Ejemplo:

```text
domain_pack_gastronomia =
  tanque_contabilidad
  + tanque_finanzas
  + tanque_proveedores
  + tanque_stock
  + tanque_gastronomia
```

---

## Frase final

SmartPyme no debe ser una colección rígida de funciones PyME.

Debe ser un sistema operativo organizacional alimentado por tanques de conocimiento desmontables.

La potencia estratégica está en que el mismo motor pueda operar sobre distintos mundos organizacionales:

```text
misma arquitectura,
distintos tanques,
distintas narrativas,
distintas patologías,
distintas evidencias,
distintos reportes.
```

El core no sabe todo.  
El core sabe operar.

Los tanques saben de dominio.  
El sistema completo sabe investigar.
