from app.orchestration.pipeline import ejecutar_pipeline_extraccion


def test_pipeline_flujo_feliz():
    input_data = [{
        "entidad_origen": "FACTURA_001",
        "patologia_id": "FORMATO_CSV_CAOTICO_AR",
        "nivel_severidad": "medio",
        "monto_detectado": "0.00",
        "diferencia": "0.00",
        "alicuota_iva": "0"
    }]
    res = ejecutar_pipeline_extraccion(input_data)
    assert res["status"] == "success"
    assert len(res["hallazgos_procesados"]) == 1
    assert len(res["errores"]) == 0

def test_pipeline_input_invalido_con_float_falla_explicito():
    input_data = [{
        "entidad_origen": "FACTURA_001",
        "patologia_id": "FORMATO_CSV_CAOTICO_AR",
        "nivel_severidad": "medio",
        "monto_detectado": 1500.5, # Float prohibido
        "diferencia": "0.00",
        "alicuota_iva": "0"
    }]
    res = ejecutar_pipeline_extraccion(input_data)
    assert res["status"] == "error"
    assert len(res["hallazgos_procesados"]) == 0
    assert len(res["errores"]) == 1
    assert "float values are strictly forbidden" in res["errores"][0]

def test_pipeline_input_incompleto_bloqueo_explicito():
    input_data = [{
        "entidad_origen": "FACTURA_001"
        # falta todo el resto de campos mandatados por HallazgoOperativo
    }]
    res = ejecutar_pipeline_extraccion(input_data)
    assert res["status"] == "error"
    assert "Error de valor crítico" in res["errores"][0]

def test_pipeline_input_estructura_mal_formada():
    input_data = {"entidad_origen": "No soy una lista"}
    res = ejecutar_pipeline_extraccion(input_data)
    assert res["status"] == "error"
    assert "El payload de entrada debe ser obligatoriamente una lista" in res["errores"][0]
