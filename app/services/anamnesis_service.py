from __future__ import annotations

import re

from app.contracts.anamnesis_contract import (
    AnamnesisInput,
    AnamnesisResult,
    DeclaredBusinessContext,
)


class AnamnesisService:
    def __init__(self):
        self._rubro_keywords = {
            "kiosco": "kiosco",
            "almacén": "almacén",
            "almacen": "almacén",
            "panadería": "panadería",
            "panaderia": "panadería",
            "restaurante": "restaurante",
            "taller": "taller",
            "ferretería": "ferretería",
            "ferreteria": "ferretería",
            "contable": "estudio contable",
            "contador": "estudio contable",
            "ecommerce": "ecommerce",
            "mercado libre": "mercado libre",
            "distribuidora": "distribuidora",
        }

        self._canal_keywords = [
            "local",
            "mercado libre",
            "instagram",
            "whatsapp",
            "web",
            "delivery",
            "mayorista",
            "minorista",
        ]

        self._fuente_keywords = [
            "excel",
            "pdf",
            "whatsapp",
            "mercado pago",
            "mercado libre",
            "banco",
            "sistema",
            "pos",
        ]

        self._dolores_phrases = [
            "compro caro",
            "no sé si gano",
            "no se si gano",
            "pierdo tiempo",
            "no tengo stock",
            "me deben",
            "no me cierra la caja",
            "todo depende de mí",
            "todo depende de mi",
        ]

        self._empleados_patterns = [
            r"\b(\d+)\s+empleados\b",
            r"\b(\d+)\s+personas\b",
            r"\bsomos\s+(\d+)\b",
            r"\btrabajan\s+(\d+)\b",
        ]

    def process(self, data: AnamnesisInput) -> AnamnesisResult:
        if data.current_context and data.current_context.cliente_id != data.cliente_id:
            raise ValueError(
                f"Mismatch de cliente_id: context={data.current_context.cliente_id}, "
                f"input={data.cliente_id}"
            )

        msg = data.owner_message.lower()
        ctx = data.current_context or DeclaredBusinessContext(cliente_id=data.cliente_id)
        
        extracted_fields = []
        
        # Rubro
        rubro = ctx.rubro_declarado
        for kw, val in self._rubro_keywords.items():
            if kw in msg:
                rubro = val
                extracted_fields.append("rubro_declarado")
                break
        
        # Empleados
        empleados = ctx.empleados_declarados
        for pattern in self._empleados_patterns:
            match = re.search(pattern, msg)
            if match:
                empleados = int(match.group(1))
                extracted_fields.append("empleados_declarados")
                break
        
        # Canales Venta
        new_canales = list(ctx.canales_venta)
        for kw in self._canal_keywords:
            if kw in msg and kw not in new_canales:
                new_canales.append(kw)
                if "canales_venta" not in extracted_fields:
                    extracted_fields.append("canales_venta")
        
        # Fuentes Datos
        new_fuentes = list(ctx.fuentes_datos)
        for kw in self._fuente_keywords:
            if kw in msg and kw not in new_fuentes:
                new_fuentes.append(kw)
                if "fuentes_datos" not in extracted_fields:
                    extracted_fields.append("fuentes_datos")
        
        # Dolores
        new_dolores = list(ctx.dolores_declarados)
        for ph in self._dolores_phrases:
            if ph in msg and ph not in new_dolores:
                new_dolores.append(ph)
                if "dolores_declarados" not in extracted_fields:
                    extracted_fields.append("dolores_declarados")

        # Preguntas Pendientes
        preguntas = []
        if rubro is None:
            preguntas.append("¿A qué se dedica principalmente tu negocio?")
        if empleados is None:
            preguntas.append("¿Cuántas personas trabajan en el negocio?")
        if not new_canales:
            preguntas.append("¿Por qué canales vendés?")
        if not new_fuentes:
            preguntas.append("¿Dónde registrás ventas, compras, stock o cobros?")
        if not new_dolores:
            preguntas.append("¿Cuál es hoy el dolor principal: dinero, tiempo, stock, ventas, cobranza u orden?")

        new_ctx = DeclaredBusinessContext(
            cliente_id=data.cliente_id,
            rubro_declarado=rubro,
            tipo_operativo_probable=ctx.tipo_operativo_probable, # No logic yet for this
            empleados_declarados=empleados,
            canales_venta=tuple(new_canales),
            fuentes_datos=tuple(new_fuentes),
            dolores_declarados=tuple(new_dolores),
            preguntas_pendientes=tuple(preguntas)
        )

        status = "CONTEXT_UPDATED" if not preguntas else "NEEDS_MORE_CONTEXT"

        return AnamnesisResult(
            cliente_id=data.cliente_id,
            context=new_ctx,
            extracted_fields=tuple(extracted_fields),
            status=status
        )
