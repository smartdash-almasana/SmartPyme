import pytest

from app.modules.findings_engine import procesar_extraccion_bruta


def test_engine_construye_instancias_reales_serializadas():
    mock_data = [{
        "cliente_id": "pyme_a",
        "entidad_origen": "ORD-ML-99912",
        "patologia_id": "IVA_DESGLOSE_ERROR",
        "nivel_severidad": "alto",
        "monto_detectado": "2500.50",
        "diferencia": "45.00",
        "alicuota_iva": "21.00",
        "fuente_a": "MercadoLibre",
        "fuente_b": "AFIP/ERP"
    }]
    
    resultado = procesar_extraccion_bruta(mock_data)
    assert len(resultado) == 1
    assert resultado[0]["cliente_id"] == "pyme_a"
    assert resultado[0]["entidad_origen"] == "ORD-ML-99912"
    assert resultado[0]["monto_detectado"] == "2500.50"


def test_engine_deriva_diferencia_matematicamente():
    mock_data = [{
        "cliente_id": "pyme_a",
        "entidad_origen": "ORD-AFIP-777",
        "patologia_id": "FORMATO_CSV_CAOTICO_AR",
        "monto_detectado": "100.50",
        "monto_esperado": "100.00",
        "diferencia": "9999.00",
        "alicuota_iva": "21.00"
    }]
    
    resultado = procesar_extraccion_bruta(mock_data)
    assert len(resultado) == 1
    assert resultado[0]["cliente_id"] == "pyme_a"
    assert resultado[0]["diferencia"] == "0.50"


def test_engine_asume_severidad_por_defecto_desde_catalogo():
    mock_data = [{
        "cliente_id": "pyme_a",
        "entidad_origen": "ORD-AFIP-777",
        "patologia_id": "FORMATO_CSV_CAOTICO_AR",
        "monto_detectado": "0.00",
        "diferencia": "0.00",
        "alicuota_iva": "0"
    }]
    
    resultado = procesar_extraccion_bruta(mock_data)
    assert len(resultado) == 1
    assert resultado[0]["cliente_id"] == "pyme_a"
    assert resultado[0]["nivel_severidad"] == "medio"


def test_engine_bloquea_cliente_id_inexistente_o_vacio():
    sin_cliente = [{
        "entidad_origen": "ORD-ML-99912",
        "patologia_id": "IVA_DESGLOSE_ERROR",
        "nivel_severidad": "alto",
        "monto_detectado": "2500.50",
        "diferencia": "45.00",
        "alicuota_iva": "21.00",
    }]
    cliente_vacio = [dict(sin_cliente[0], cliente_id="   ")]

    with pytest.raises(ValueError):
        procesar_extraccion_bruta(sin_cliente)
    with pytest.raises(ValueError):
        procesar_extraccion_bruta(cliente_vacio)


def test_engine_bloquea_patologia_id_invalido_o_inexistente():
    mock_data = [{
        "cliente_id": "pyme_a",
        "entidad_origen": "ORD-ML-XXX",
        "patologia_id": "PATOLOGIA_NO_INVENTADA",
        "monto_detectado": "2500.50",
        "diferencia": "45.00",
        "alicuota_iva": "21.00"
    }]
    
    with pytest.raises(ValueError, match="Patología no reconocida por el sistema auditado"):
        procesar_extraccion_bruta(mock_data)


def test_engine_explota_antes_de_salir_con_float():
    mock_data_float = [{
        "cliente_id": "pyme_a",
        "entidad_origen": "ORD-ML-99913",
        "patologia_id": "IVA_DESGLOSE_ERROR",
        "nivel_severidad": "medio",
        "monto_detectado": 2500.50,
        "diferencia": "45.00",
        "alicuota_iva": "21.00"
    }]
    
    with pytest.raises(ValueError, match="float values are strictly forbidden"):
        procesar_extraccion_bruta(mock_data_float)
