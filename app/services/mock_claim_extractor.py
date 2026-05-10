from __future__ import annotations

from app.contracts.operational_claims import ClaimType


class MockClaimExtractor:
    """Rule-based offline extractor for basic operational claims."""

    _KEYWORDS: tuple[tuple[ClaimType, tuple[str, ...]], ...] = (
        (ClaimType.DEUDA_COBRANZA, ("deuda", "cobranza", "mora")),
        (ClaimType.STOCK, ("stock", "inventario", "faltante")),
        (ClaimType.VENTAS, ("venta", "ventas", "ticket")),
        (ClaimType.COSTOS, ("costo", "costos", "gasto", "gastos")),
        (ClaimType.MARGEN, ("margen", "rentabilidad")),
        (ClaimType.PROVEEDOR, ("proveedor", "proveedores")),
        (ClaimType.CLIENTE, ("cliente", "clientes")),
        (ClaimType.FACTURACION, ("factura", "facturacion", "facturación")),
    )

    def extract(self, message: str) -> list[tuple[ClaimType, str]]:
        text = message.lower()
        found: list[tuple[ClaimType, str]] = []
        for claim_type, keywords in self._KEYWORDS:
            if any(keyword in text for keyword in keywords):
                found.append((claim_type, message.strip()))
        return found
