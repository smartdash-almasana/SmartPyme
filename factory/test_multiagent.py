import json
from pathlib import Path

from factory.multiagent_runner import FactoryRunner


def _bitacora_test_path(nombre: str) -> Path:
    base = Path("SmartPyme/.tmp_factory_tests")
    base.mkdir(parents=True, exist_ok=True)
    bitacora = base / nombre
    if bitacora.exists():
        bitacora.unlink()
    return bitacora


def test_runner_ejecuta_y_valida_correctamente_sin_romper_core():
    bitacora = _bitacora_test_path("execution_log_core.jsonl")
    runner = FactoryRunner(bitacora_path=bitacora)
    res = runner.fabricar("Ajustar app/core/ para test de humo usando triada.")

    assert res["estado_final"] == "exitoso"
    assert "director" in res["estado_etapas"]
    assert "writer" in res["estado_etapas"]
    assert "validator" in res["estado_etapas"]
    assert "Tests pasaron correctamente" in res["estado_etapas"]["validator"]["logs"]


def test_contratos_roles_input_output_son_consistentes():
    runner = FactoryRunner(bitacora_path=_bitacora_test_path("execution_log_contracts.jsonl"))
    res = runner.fabricar("Validar contratos explícitos por rol")

    director = res["estado_etapas"]["director"]
    writer = res["estado_etapas"]["writer"]
    validator = res["estado_etapas"]["validator"]

    assert set(director.keys()) == {"input", "output"}
    assert set(writer.keys()) == {"input", "output"}
    assert set(validator.keys()) == {"input", "output", "logs"}

    assert set(director["input"].keys()) == {"objetivo"}
    assert set(director["output"].keys()) == {
        "atomo_id",
        "area",
        "origen_seleccion",
        "siguiente_atomo_sugerido",
        "secuencia_sugerida",
        "objetivo_mapeado",
        "plan_corto",
        "subagente_writer",
        "razon_writer",
        "subagente_validator",
        "razon_validator",
    }
    assert set(writer["input"].keys()) == {"objetivo_mapeado", "plan_corto", "subagente_writer"}
    assert set(writer["output"].keys()) == {"archivos_tocados", "status", "subagente_ejecutado"}
    assert set(validator["input"].keys()) == {"archivos_tocados", "subagente_validator"}
    assert set(validator["output"].keys()) == {"veredicto", "logs", "tests_corridos", "subagente_ejecutado"}


def test_bitacora_local_creada_con_secuencia_auditable():
    bitacora = _bitacora_test_path("execution_log_traceability.jsonl")
    runner = FactoryRunner(bitacora_path=bitacora)
    res = runner.fabricar("Registrar ejecución de fábrica auditable")

    assert bitacora.exists()
    entries = [json.loads(line) for line in bitacora.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(entries) == 1
    entry = entries[0]

    assert entry["atomo_id"]
    assert entry["origen_seleccion"] in {"planner", "fallback"}
    assert isinstance(entry["secuencia_sugerida"], list)
    assert entry["objetivo"] == "Registrar ejecución de fábrica auditable"
    assert entry["plan_corto"]
    assert entry["rol_ejecutado"] == "validator"
    assert entry["subagente_writer"] in {"writer_core", "writer_pipeline"}
    assert entry["subagente_validator"] in {"validator_contracts", "validator_tests"}
    assert entry["razon_writer"]
    assert entry["razon_validator"]
    assert isinstance(entry["archivos_tocados"], list)
    assert isinstance(entry["tests_corridos"], list)
    assert entry["veredicto_final"] == res["estado_final"]
    assert entry["archivos_tocados"] == res["estado_etapas"]["writer"]["output"]["archivos_tocados"]
    assert entry["tests_corridos"] == res["estado_etapas"]["validator"]["output"]["tests_corridos"]


def test_routing_correcto_por_tipo_de_atomo():
    runner = FactoryRunner(bitacora_path=_bitacora_test_path("execution_log_routing.jsonl"))

    res_core = runner.fabricar("Cambiar app/core/ para hardening")
    assert res_core["estado_etapas"]["director"]["output"]["subagente_writer"] == "writer_core"

    res_pipeline = runner.fabricar("Ajustar app/orchestration/ en flujo principal")
    assert res_pipeline["estado_etapas"]["director"]["output"]["subagente_writer"] == "writer_pipeline"


def test_validadores_diferenciados_segun_objetivo():
    runner = FactoryRunner(bitacora_path=_bitacora_test_path("execution_log_validators.jsonl"))

    res_contracts = runner.fabricar("Refinar contratos y tipado de catálogo")
    assert res_contracts["estado_etapas"]["director"]["output"]["subagente_validator"] == "validator_contracts"
    assert res_contracts["estado_etapas"]["validator"]["output"]["subagente_ejecutado"] == "validator_contracts"
    assert res_contracts["estado_etapas"]["validator"]["output"]["tests_corridos"] == ["contract_check"]

    res_general = runner.fabricar("Corregir comportamiento general de ejecución")
    assert res_general["estado_etapas"]["director"]["output"]["subagente_validator"] == "validator_tests"
    assert res_general["estado_etapas"]["validator"]["output"]["subagente_ejecutado"] == "validator_tests"


def test_director_selecciona_por_catalogo():
    runner = FactoryRunner(bitacora_path=_bitacora_test_path("execution_log_catalog_selection.jsonl"))
    res = runner.fabricar("Ajustar app/orchestration/ en pipeline principal")

    director_output = res["estado_etapas"]["director"]["output"]
    assert director_output["origen_seleccion"] == "planner"
    assert director_output["atomo_id"] == "atomo_pipeline_flujo_smoke"
    assert director_output["subagente_writer"] == "writer_pipeline"
    assert director_output["subagente_validator"] == "validator_tests"
    assert 2 <= len(director_output["secuencia_sugerida"]) <= 4


def test_director_caida_fallback_si_no_hay_match_catalogo():
    runner = FactoryRunner(bitacora_path=_bitacora_test_path("execution_log_fallback_selection.jsonl"))
    res = runner.fabricar("Objetivo no catalogado zeta omega delta")

    director_output = res["estado_etapas"]["director"]["output"]
    assert director_output["origen_seleccion"] == "fallback"
    assert director_output["atomo_id"] == "fallback_heuristico"
    assert director_output["secuencia_sugerida"] == ["fallback_heuristico"]


def test_bitacora_registra_atomo_y_origen_seleccion():
    bitacora = _bitacora_test_path("execution_log_catalog_traceability.jsonl")
    runner = FactoryRunner(bitacora_path=bitacora)
    runner.fabricar("Refinar contratos y tipado de catálogo")

    entry = json.loads(bitacora.read_text(encoding="utf-8").strip())
    assert entry["atomo_id"] == "atomo_catalogo_contratos"
    assert entry["origen_seleccion"] == "planner"
    assert entry["siguiente_atomo_sugerido"] == "atomo_factoria_contratos"
    assert entry["secuencia_sugerida"] == ["atomo_catalogo_contratos", "atomo_factoria_contratos"]


def test_planner_fallback_controlado_si_no_hay_cadena_explicita():
    runner = FactoryRunner(bitacora_path=_bitacora_test_path("execution_log_planner_fallback_chain.jsonl"))
    res = runner.fabricar("Trabajo de factoria sin cadena explicita")
    director_output = res["estado_etapas"]["director"]["output"]

    assert director_output["atomo_id"] == "atomo_factoria_contratos"
    assert director_output["origen_seleccion"] == "fallback"
    assert director_output["secuencia_sugerida"] == ["atomo_factoria_contratos"]
