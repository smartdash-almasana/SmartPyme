import decimal
from typing import Any


def calcular_diferencia_absoluta(monto_detectado: Any, monto_esperado: Any) -> decimal.Decimal:
    """
    Calcula determinísticamente la diferencia absoluta entre dos montos para SmartCounter.
    Rechaza floats y aspersiones NaN/Infinity explícitamente.
    """
    if isinstance(monto_detectado, float) or isinstance(monto_esperado, float):
        raise ValueError("float values are strictly forbidden for monetary operations.")

    decimal.getcontext().prec = 28

    try:
        d1 = (
            monto_detectado
            if isinstance(monto_detectado, decimal.Decimal)
            else decimal.Decimal(str(monto_detectado))
        )
        d2 = (
            monto_esperado
            if isinstance(monto_esperado, decimal.Decimal)
            else decimal.Decimal(str(monto_esperado))
        )
    except decimal.InvalidOperation:
        raise ValueError(
            "Error extrayendo Decimal nativo: los datos no son parseables como dinero."
        )

    if d1.is_nan() or d2.is_nan() or d1.is_infinite() or d2.is_infinite():
        raise ValueError(
            "Los valores matemáticos NaN o Infinity están estrictamente prohibidos en el motor fiscal."
        )

    return abs(d1 - d2)
