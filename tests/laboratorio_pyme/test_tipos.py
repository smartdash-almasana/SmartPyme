from app.laboratorio_pyme.tipos import TipoLaboratorio


def test_cinco_valores():
    """TipoLaboratorio tiene exactamente cinco miembros."""
    assert len(TipoLaboratorio) == 5


def test_acceso_por_nombre():
    """Cada valor es accesible por nombre."""
    assert TipoLaboratorio.analisis_comercial
    assert TipoLaboratorio.analisis_stock
    assert TipoLaboratorio.analisis_financiero
    assert TipoLaboratorio.analisis_compras
    assert TipoLaboratorio.analisis_automatizacion


def test_valor_string_coincide_con_nombre():
    """El .value de cada miembro coincide con su nombre."""
    for miembro in TipoLaboratorio:
        assert miembro.value == miembro.name


def test_tipo_laboratorio_es_string():
    """TipoLaboratorio extiende str — cada miembro es usable como string."""
    assert isinstance(TipoLaboratorio.analisis_comercial, str)
    assert TipoLaboratorio.analisis_financiero == "analisis_financiero"
