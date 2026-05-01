import pytest
from app.contracts.anamnesis_contract import AnamnesisInput, DeclaredBusinessContext
from app.services.anamnesis_service import AnamnesisService


@pytest.fixture
def service():
    return AnamnesisService()


def test_crea_contexto_vacio_si_no_recibe_current_context(service):
    data = AnamnesisInput(cliente_id="C1", owner_message="Hola")
    res = service.process(data)
    
    assert res.cliente_id == "C1"
    assert res.context.cliente_id == "C1"
    assert res.context.rubro_declarado is None
    assert res.status == "NEEDS_MORE_CONTEXT"
    assert len(res.context.preguntas_pendientes) == 5


def test_detecta_rubro_y_empleados_desde_mensaje_simple(service):
    data = AnamnesisInput(cliente_id="C1", owner_message="Tengo un kiosco y somos 3 personas")
    res = service.process(data)
    
    assert res.context.rubro_declarado == "kiosco"
    assert res.context.empleados_declarados == 3
    assert "rubro_declarado" in res.extracted_fields
    assert "empleados_declarados" in res.extracted_fields


def test_detecta_canales_de_venta_y_fuentes_datos(service):
    data = AnamnesisInput(
        cliente_id="C1", 
        owner_message="Vendo por mercado libre y anoto todo en un excel"
    )
    res = service.process(data)
    
    assert "mercado libre" in res.context.canales_venta
    assert "excel" in res.context.fuentes_datos
    assert "canales_venta" in res.extracted_fields
    assert "fuentes_datos" in res.extracted_fields


def test_detecta_dolores_declarados(service):
    data = AnamnesisInput(
        cliente_id="C1", 
        owner_message="El problema es que no sé si gano plata y pierdo tiempo"
    )
    res = service.process(data)
    
    assert "no sé si gano" in res.context.dolores_declarados
    assert "pierdo tiempo" in res.context.dolores_declarados
    assert "dolores_declarados" in res.extracted_fields


def test_fusiona_contexto_previo_sin_duplicar_valores(service):
    prev_ctx = DeclaredBusinessContext(
        cliente_id="C1",
        rubro_declarado="kiosco",
        canales_venta=("local",)
    )
    data = AnamnesisInput(
        cliente_id="C1",
        owner_message="También vendo por whatsapp y en el local",
        current_context=prev_ctx
    )
    res = service.process(data)
    
    assert res.context.rubro_declarado == "kiosco"
    assert "local" in res.context.canales_venta
    assert "whatsapp" in res.context.canales_venta
    assert len(res.context.canales_venta) == 2 # "local" was already there


def test_genera_preguntas_pendientes_cuando_faltan_campos(service):
    data = AnamnesisInput(cliente_id="C1", owner_message="Tengo un taller")
    res = service.process(data)
    
    assert res.status == "NEEDS_MORE_CONTEXT"
    assert "¿A qué se dedica principalmente tu negocio?" not in res.context.preguntas_pendientes
    assert "¿Cuántas personas trabajan en el negocio?" in res.context.preguntas_pendientes


def test_devuelve_context_updated_cuando_contexto_minimo_esta_completo(service):
    msg = (
        "Soy contador, somos 2 empleados. Vendo servicios por whatsapp. "
        "Uso sistema y el problema es que me deben mucho."
    )
    data = AnamnesisInput(cliente_id="C1", owner_message=msg)
    res = service.process(data)
    
    assert res.status == "CONTEXT_UPDATED"
    assert len(res.context.preguntas_pendientes) == 0


def test_mantiene_cliente_id_explicito(service):
    data = AnamnesisInput(cliente_id="CLIENTE_X", owner_message="Hola")
    res = service.process(data)
    
    assert res.cliente_id == "CLIENTE_X"
    assert res.context.cliente_id == "CLIENTE_X"


def test_error_si_cliente_id_no_coincide_con_contexto(service):
    prev_ctx = DeclaredBusinessContext(cliente_id="C1")
    data = AnamnesisInput(cliente_id="C2", owner_message="Hola", current_context=prev_ctx)
    
    with pytest.raises(ValueError, match="Mismatch de cliente_id"):
        service.process(data)


def test_genera_candidatos_taxonomia(service):
    data = AnamnesisInput(cliente_id="C1", owner_message="Tengo un kiosco")
    res = service.process(data)
    
    assert len(res.context.taxonomia_candidata_ids) > 0
    assert "TAX_COM_005" in res.context.taxonomia_candidata_ids


def test_no_decide_tipo_operativo_probable(service):
    data = AnamnesisInput(cliente_id="C1", owner_message="Tengo un kiosco")
    res = service.process(data)
    
    # Aunque haya candidatos, no debe elegir uno automáticamente todavía
    assert res.context.tipo_operativo_probable is None


def test_conserva_tipo_operativo_probable_previo(service):
    prev_ctx = DeclaredBusinessContext(
        cliente_id="C1",
        tipo_operativo_probable="mi_tipo_fijo"
    )
    data = AnamnesisInput(
        cliente_id="C1", 
        owner_message="Tengo un kiosco",
        current_context=prev_ctx
    )
    res = service.process(data)
    
    assert res.context.tipo_operativo_probable == "mi_tipo_fijo"


def test_sin_candidatos_deja_tupla_vacia(service):
    data = AnamnesisInput(cliente_id="C1", owner_message="Hola")
    res = service.process(data)
    
    assert res.context.taxonomia_candidata_ids == ()
