import pytest
import decimal
from app.core.entities import HallazgoOperativo

def test_hallazgo_operativo_valido_con_strings_decimales():
    h = HallazgoOperativo(
        entidad_origen="tx_123",
        patologia_id="IVA_ERR",
        nivel_severidad="alto",
        monto_detectado="150000.25",
        diferencia="1200.10",
        alicuota_iva="21.00"
    )
    assert isinstance(h.monto_detectado, decimal.Decimal)
    assert h.monto_detectado == decimal.Decimal("150000.25")
    assert isinstance(h.diferencia, decimal.Decimal)
    assert h.diferencia == decimal.Decimal("1200.10")
    assert isinstance(h.alicuota_iva, decimal.Decimal)
    assert h.alicuota_iva == decimal.Decimal("21.00")

def test_hallazgo_operativo_rechaza_float_en_campos_monetarios():
    with pytest.raises(ValueError, match="float values are strictly forbidden"):
        HallazgoOperativo(
            entidad_origen="tx_123",
            patologia_id="IVA_ERR",
            nivel_severidad="alto",
            monto_detectado=150000.25,  # Es float!
            diferencia="1200.10",
            alicuota_iva="21.00"
        )
        
    with pytest.raises(ValueError, match="float values are strictly forbidden"):
        HallazgoOperativo(
            entidad_origen="tx_123",
            patologia_id="IVA_ERR",
            nivel_severidad="alto",
            monto_detectado="150000.25",
            diferencia=1200.10,  # Es float!
            alicuota_iva="21.00"
        )

def test_hallazgo_operativo_preserva_precision_decimal():
    high_precision_str = "0.1234567891234567891234567891"
    h = HallazgoOperativo(
        entidad_origen="tx_123",
        patologia_id="IVA_ERR",
        nivel_severidad="alto",
        monto_detectado=high_precision_str,
        diferencia="0",
        alicuota_iva="0"
    )
    assert str(h.monto_detectado) == high_precision_str

def test_hallazgo_operativo_rechaza_strings_invalidos():
    invalid_inputs = ["abc", "", "   ", "NaN", "Infinity", "-Infinity"]
    for inv in invalid_inputs:
        with pytest.raises(ValueError):
            HallazgoOperativo(
                entidad_origen="tx_123",
                patologia_id="IVA_ERR",
                nivel_severidad="alto",
                monto_detectado=inv,
                diferencia="0",
                alicuota_iva="0"
            )

def test_hallazgo_operativo_normaliza_severidad():
    h = HallazgoOperativo(
        entidad_origen="tx_123",
        patologia_id="IVA_ERR",
        nivel_severidad="ALTO",
        monto_detectado="0",
        diferencia="0",
        alicuota_iva="0"
    )
    assert h.nivel_severidad == "alto"
    
    h2 = HallazgoOperativo(
        entidad_origen="tx_123",
        patologia_id="IVA_ERR",
        nivel_severidad="Critico",
        monto_detectado="0",
        diferencia="0",
        alicuota_iva="0"
    )
    assert h2.nivel_severidad == "critico"
