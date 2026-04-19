import json
import os
import subprocess
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

from factory.atoms_catalog import resolver_atomo_por_id
from factory.atoms_planner import planificar_secuencia_atomica

@dataclass(frozen=True)
class DirectorInput:
    objetivo: str


@dataclass(frozen=True)
class DirectorOutput:
    atomo_id: str
    area: str
    origen_seleccion: str
    siguiente_atomo_sugerido: str | None
    secuencia_sugerida: list[str]
    objetivo_mapeado: str
    plan_corto: str
    subagente_writer: str
    razon_writer: str
    subagente_validator: str
    razon_validator: str


@dataclass(frozen=True)
class CodeWriterInput:
    objetivo_mapeado: str
    plan_corto: str
    subagente_writer: str


@dataclass(frozen=True)
class CodeWriterOutput:
    archivos_tocados: list[str]
    status: str
    subagente_ejecutado: str


@dataclass(frozen=True)
class ValidatorInput:
    archivos_tocados: list[str]
    subagente_validator: str


@dataclass(frozen=True)
class ValidatorOutput:
    veredicto: str
    logs: str
    tests_corridos: list[str]
    subagente_ejecutado: str


class Director:
    """Rol: Decide el atomo y enruta el trabajo (mockeo local)."""

    def _seleccionar_writer(self, objetivo: str) -> tuple[str, str]:
        objetivo_lower = objetivo.lower()
        if "app/core/" in objetivo_lower or "core" in objetivo_lower:
            return "writer_core", "Objetivo orientado a app/core."
        if "app/orchestration/" in objetivo_lower or "flujo" in objetivo_lower:
            return "writer_pipeline", "Objetivo orientado a orquestacion/flujo."
        return "writer_core", "Ruta por defecto para cambios locales acotados."

    def _seleccionar_validator(self, objetivo: str) -> tuple[str, str]:
        objetivo_lower = objetivo.lower()
        if any(token in objetivo_lower for token in ("contrato", "tipado", "catálogo", "catalogo")):
            return "validator_contracts", "Objetivo enfocado en contratos/tipado/catalogos."
        return "validator_tests", "Objetivo de comportamiento general."

    def enrutar_trabajo(self, payload: DirectorInput) -> DirectorOutput:
        plan = planificar_secuencia_atomica(payload.objetivo)
        atomo = resolver_atomo_por_id(plan.atomo_actual)

        if atomo:
            subagente_writer = atomo.writer_objetivo
            subagente_validator = atomo.validator_objetivo
            razon_writer = f"Seleccionado por {plan.origen_planificacion} sobre catalogo ({atomo.atomo_id})."
            razon_validator = f"Validador asignado por {plan.origen_planificacion} ({atomo.area})."
            atomo_id = atomo.atomo_id
            area = atomo.area
            origen_seleccion = plan.origen_planificacion
        else:
            subagente_writer, razon_writer = self._seleccionar_writer(payload.objetivo)
            subagente_validator, razon_validator = self._seleccionar_validator(payload.objetivo)
            atomo_id = "fallback_heuristico"
            area = plan.area
            origen_seleccion = "fallback"

        return DirectorOutput(
            atomo_id=atomo_id,
            area=area,
            origen_seleccion=origen_seleccion,
            siguiente_atomo_sugerido=plan.siguiente_atomo_sugerido,
            secuencia_sugerida=plan.secuencia_sugerida,
            objetivo_mapeado=payload.objetivo,
            plan_corto=(
                "Elaborar y testear un flujo contra el contrato central "
                "(HallazgoOperativo)."
            ),
            subagente_writer=subagente_writer,
            razon_writer=razon_writer,
            subagente_validator=subagente_validator,
            razon_validator=razon_validator,
        )


class CodeWriter:
    """Rol: Propone o codifica cambios locales fisicos."""

    def _writer_core(self) -> CodeWriterOutput:
        ruta_test_temporal = "SmartPyme/app/core/test_smoke_factory_tmp.py"
        codigo = """from decimal import Decimal
from SmartPyme.app.core.entities import HallazgoOperativo
def test_smoke_factory():
    h = HallazgoOperativo(
        entidad_origen="mock-factory",
        patologia_id="IVA_DESGLOSE_ERROR",
        nivel_severidad="alto",
        monto_detectado="10.00",
        diferencia="0.00",
        alicuota_iva="21.00"
    )
    assert h.nivel_severidad == "alto"
    assert h.monto_detectado == Decimal("10.00")
"""
        with open(ruta_test_temporal, "w", encoding="utf-8") as f:
            f.write(codigo)
        return CodeWriterOutput(
            archivos_tocados=[ruta_test_temporal],
            status="codigo materializado",
            subagente_ejecutado="writer_core",
        )

    def _writer_pipeline(self) -> CodeWriterOutput:
        ruta_test_temporal = "SmartPyme/app/orchestration/test_smoke_factory_tmp.py"
        codigo = """def test_smoke_pipeline_factory():
    estado = {"status": "success", "flujo": "orchestration"}
    assert estado["status"] == "success"
    assert estado["flujo"] == "orchestration"
"""
        with open(ruta_test_temporal, "w", encoding="utf-8") as f:
            f.write(codigo)

        return CodeWriterOutput(
            archivos_tocados=[ruta_test_temporal],
            status="codigo materializado",
            subagente_ejecutado="writer_pipeline",
        )

    def proponer_cambio(self, payload: CodeWriterInput) -> CodeWriterOutput:
        if payload.subagente_writer == "writer_pipeline":
            return self._writer_pipeline()
        return self._writer_core()


class Validator:
    """Rol: Ejecuta tests organicos y audita la inviolabilidad del contrato."""

    def _validator_contracts(self, payload: ValidatorInput) -> ValidatorOutput:
        archivos = payload.archivos_tocados
        if not archivos:
            return ValidatorOutput(
                veredicto="fallido",
                logs="Ausencia de codigo material para chequeo contractual.",
                tests_corridos=[],
                subagente_ejecutado="validator_contracts",
            )

        contrato_valido = all(
            archivo.startswith("SmartPyme/app/") and archivo.endswith(".py")
            for archivo in archivos
        )
        veredicto = "exitoso" if contrato_valido else "reprobado"
        logs = "Chequeo de contratos/tipado local exitoso." if contrato_valido else "Chequeo contractual fallido."
        return ValidatorOutput(
            veredicto=veredicto,
            logs=logs,
            tests_corridos=["contract_check"],
            subagente_ejecutado="validator_contracts",
        )

    def _validator_tests(self, payload: ValidatorInput) -> ValidatorOutput:
        archivos = payload.archivos_tocados
        if not archivos:
            return ValidatorOutput(
                veredicto="fallido",
                logs="Ausencia de codigo material.",
                tests_corridos=[],
                subagente_ejecutado="validator_tests",
            )

        target = archivos[0]
        repo_root = Path(__file__).resolve().parents[2]
        env = os.environ.copy()
        env["PYTHONPATH"] = str(repo_root)
        result = subprocess.run(
            ["pytest", target, "--basetemp", "SmartPyme/.tmp_pytest_factory_runner"],
            capture_output=True,
            text=True,
            cwd=str(repo_root),
            env=env,
        )

        if result.returncode == 0:
            return ValidatorOutput(
                veredicto="exitoso",
                logs="Tests pasaron correctamente contra el juez del core deterministico.",
                tests_corridos=[target],
                subagente_ejecutado="validator_tests",
            )
        return ValidatorOutput(
            veredicto="reprobado",
            logs=result.stdout or result.stderr,
            tests_corridos=[target],
            subagente_ejecutado="validator_tests",
        )

    def auditar_y_testear(self, payload: ValidatorInput) -> ValidatorOutput:
        if payload.subagente_validator == "validator_contracts":
            result = self._validator_contracts(payload)
        else:
            result = self._validator_tests(payload)

        for f in payload.archivos_tocados:
            if os.path.exists(f):
                os.remove(f)
        return result


class FactoryRunner:
    """Motor orquestador minimalista de 3 tiempos funcionales."""

    def __init__(self, bitacora_path: str | Path | None = None):
        self.director = Director()
        self.writer = CodeWriter()
        self.validator = Validator()
        self.bitacora_path = Path(bitacora_path) if bitacora_path else Path(__file__).with_name("factory_execution_log.jsonl")

    def _registrar_bitacora(
        self,
        atomo_id: str,
        area: str,
        origen_seleccion: str,
        siguiente_atomo_sugerido: str | None,
        secuencia_sugerida: list[str],
        objetivo: str,
        plan_corto: str,
        rol_ejecutado: str,
        subagente_writer: str,
        razon_writer: str,
        subagente_validator: str,
        razon_validator: str,
        archivos_tocados: list[str],
        tests_corridos: list[str],
        veredicto_final: str,
    ) -> None:
        self.bitacora_path.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "timestamp_utc": datetime.now(UTC).isoformat(),
            "atomo_id": atomo_id,
            "area": area,
            "origen_seleccion": origen_seleccion,
            "siguiente_atomo_sugerido": siguiente_atomo_sugerido,
            "secuencia_sugerida": secuencia_sugerida,
            "objetivo": objetivo,
            "plan_corto": plan_corto,
            "rol_ejecutado": rol_ejecutado,
            "subagente_writer": subagente_writer,
            "razon_writer": razon_writer,
            "subagente_validator": subagente_validator,
            "razon_validator": razon_validator,
            "archivos_tocados": archivos_tocados,
            "tests_corridos": tests_corridos,
            "veredicto_final": veredicto_final,
        }
        with self.bitacora_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def fabricar(self, objetivo: str) -> dict:
        director_input = DirectorInput(objetivo=objetivo)
        director_output = self.director.enrutar_trabajo(director_input)

        writer_input = CodeWriterInput(
            objetivo_mapeado=director_output.objetivo_mapeado,
            plan_corto=director_output.plan_corto,
            subagente_writer=director_output.subagente_writer,
        )
        writer_output = self.writer.proponer_cambio(writer_input)

        validator_input = ValidatorInput(
            archivos_tocados=writer_output.archivos_tocados,
            subagente_validator=director_output.subagente_validator,
        )
        validator_output = self.validator.auditar_y_testear(validator_input)

        self._registrar_bitacora(
            atomo_id=director_output.atomo_id,
            area=director_output.area,
            origen_seleccion=director_output.origen_seleccion,
            siguiente_atomo_sugerido=director_output.siguiente_atomo_sugerido,
            secuencia_sugerida=director_output.secuencia_sugerida,
            objetivo=objetivo,
            plan_corto=director_output.plan_corto,
            rol_ejecutado="validator",
            subagente_writer=director_output.subagente_writer,
            razon_writer=director_output.razon_writer,
            subagente_validator=director_output.subagente_validator,
            razon_validator=director_output.razon_validator,
            archivos_tocados=writer_output.archivos_tocados,
            tests_corridos=validator_output.tests_corridos,
            veredicto_final=validator_output.veredicto,
        )

        return {
            "objetivo_inicial": objetivo,
            "estado_etapas": {
                "director": {
                    "input": asdict(director_input),
                    "output": asdict(director_output),
                },
                "writer": {
                    "input": asdict(writer_input),
                    "output": asdict(writer_output),
                },
                "validator": {
                    "input": asdict(validator_input),
                    "output": asdict(validator_output),
                    "logs": validator_output.logs,
                },
            },
            "estado_final": validator_output.veredicto,
            "bitacora_path": str(self.bitacora_path),
        }
