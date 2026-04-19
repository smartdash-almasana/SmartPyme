import pytest
import decimal
from app.core.calculators import calcular_diferencia_absoluta

def test_calculadora_diferencia_positiva():
    res = calcular_diferencia_absoluta("15.55", "10.00")
    assert isinstance(res, decimal.Decimal)
    assert res == decimal.Decimal("5.55")

def test_calculadora_flujo_cero():
    res = calcular_diferencia_absoluta("21.00", "21")
    assert res == decimal.Decimal("0.00")

def test_calculadora_prohibe_float():
    with pytest.raises(ValueError, match="float values are strictly forbidden"):
        calcular_diferencia_absoluta(10.50, "10.00") # detectado=float
    
    with pytest.raises(ValueError, match="float values are strictly forbidden"):
        calcular_diferencia_absoluta("10.50", 10.00) # esperado=float

def test_calculadora_prohibe_ruido_logico():
    with pytest.raises(ValueError):
        calcular_diferencia_absoluta("100.00", "NaN")
    with pytest.raises(ValueError):
        calcular_diferencia_absoluta("Infinity", "100.00")
