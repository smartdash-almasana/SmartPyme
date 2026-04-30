import pytest
import decimal
from pydantic import ValidationError
from app.core.entities import HallazgoOperativo


def _hallazgo_payload(**overrides):
    payload = {
        "cliente_id": "pyme_a",
        "entidad_origen": "tx_123",
        "patologia_id": "IVA_ERR",
        "nivel_severidad": "alto",
        "monto_detectado": "150000.25",
        "diferencia": "1200.10",
        "alicuota_iva": "21.00",
    }
    payload.update(overrides)
    return payload


def test_hallazgo_operativo_valido_con_strings_decimales():
    h = HallazgoOperativo(**_hallazgo_payload())
    assert h.cliente_id == "pyme_a"
    assert isinstance(h.monto_detectado, decimal.Decimal)
    assert h.monto_detectado == decimal.Decimal("150000.25")
    assert isinstance(h.diferencia, decimal.Decimal)
    assert h.diferencia == decimal.Decimal("1200.10")
    assert isinstance(h.alicuota_iva, decimal.Decimal)
    assert h.alicuota_iva == decimal.Decimal("21.00")


def test_hallazgo_operativo_requiere_cliente_id_no_vacio():
    with pytest.raises(ValidationError):
        HallazgoOperativo(**_hallazgo_payload(cliente_id=""))

    with pytest.raises(ValidationError):
        HallazgoOperativo(**_hallazgo_payload(cliente_id="   "))

    payload = _hallazgo_payload()
    payload.pop("cliente_id")
    with pytest.raises(ValidationError):
        HallazgoOperativo(**payload)


def test_hallazgo_operativo_normaliza_cliente_id():
    h = HallazgoOperativo(**_hallazgo_payload(cliente_id="  pyme_a  "))
    assert h.cliente_id == "pyme_a"


def test_hallazgo_operativo_rechaza_float_en_campos_monetarios():
    with pytest.raises(ValueError, match="float values are strictly forbidden"):
        HallazgoOperativo(**_hallazgo_payload(monto_detectado=150000.25))
        
    with pytest.raises(ValueError, match="float values are strictly forbidden"):
        HallazgoOperativo(**_hallazgo_payload(diferencia=1200.10))


def test_hallazgo_operativo_preserva_precision_decimal():
    high_precision_str = "0.1234567891234567891234567891"
    h = HallazgoOperativo(
        **_hallazgo_payload(
            monto_detectado=high_precision_str,
            diferencia="0",
            alicuota_iva="0",
        )
    )
    assert str(h.monto_detectado) == high_precision_str


def test_hallazgo_operativo_rechaza_strings_invalidos():
    invalid_inputs = ["abc", "", "   ", "NaN", "Infinity", "-Infinity"]
    for inv in invalid_inputs:
        with pytest.raises(ValueError):
            HallazgoOperativo(**_hallazgo_payload(monto_detectado=inv, diferencia="0", alicuota_iva="0"))


def test_hallazgo_operativo_normaliza_severidad():
    h = HallazgoOperativo(**_hallazgo_payload(nivel_severidad="ALTO", monto_detectado="0", diferencia="0", alicuota_iva="0"))
    assert h.nivel_severidad == "alto"
    
    h2 = HallazgoOperativo(**_hallazgo_payload(nivel_severidad="Critico", monto_detectado="0", diferencia="0", alicuota_iva="0"))
    assert h2.nivel_severidad == "critico"
