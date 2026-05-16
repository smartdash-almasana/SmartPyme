"""
CLI Demo — PymIA Laboratorio Inicial.

Caso canónico offline/determinístico:
    python -m pymia.cli.demo "vendo mucho pero no sé si gano plata"

Sin LLM. Sin env vars. Sin red.
"""
from __future__ import annotations

import sys
import uuid

from pymia.pipeline.admission.v1.pipeline import AdmissionPipelineV1
from pymia.pipeline.admission.v1.response_formatter import AdmissionResponseFormatterV1


_SEPARATOR = "-" * 60
_HEADER = "=" * 60


def _print_section(title: str, body: str) -> None:
    print(f"\n{_SEPARATOR}")
    print(f"  {title}")
    print(_SEPARATOR)
    print(body)


def run_demo(claim: str) -> None:
    """Ejecuta el pipeline clinico y muestra el resultado en consola."""
    print(f"\n{_HEADER}")
    print("  PymIA - Laboratorio Inicial PyME")
    print(_HEADER)
    print(f"\n  INPUT: \"{claim}\"")

    pipeline = AdmissionPipelineV1()
    pyme_id = uuid.uuid4()
    artifact, state = pipeline.run(pyme_id=pyme_id, claim=claim)

    # — Síntoma detectado —
    symptom_text = artifact.symptoms[0].claim if artifact.symptoms else "(ninguno)"
    _print_section("SÍNTOMA DETECTADO", f"  {symptom_text}")

    # — Hipótesis —
    if artifact.hypotheses:
        primary = None
        if artifact.primary_hypothesis_id:
            for h in artifact.hypotheses:
                if h.node_id == artifact.primary_hypothesis_id:
                    primary = h
                    break
        if primary is None:
            primary = artifact.hypotheses[0]

        _print_section(
            "HIPÓTESIS PRIORITARIA",
            f"  {primary.description}  (score: {primary.confidence_score})\n"
            f"  Señales detectadas: {', '.join(primary.reasoning_trace)}",
        )

        secondaries = [h for h in artifact.hypotheses if h.node_id != primary.node_id]
        if secondaries:
            lines = "\n".join(
                f"  • {h.description}  (score: {h.confidence_score})" for h in secondaries
            )
            _print_section("HIPÓTESIS SECUNDARIAS", lines)

        all_evidence = sorted(
            {e for h in artifact.hypotheses for e in h.evidence_required}
        )
        _print_section(
            "EVIDENCIA REQUERIDA",
            "\n".join(f"  – {e}" for e in all_evidence),
        )
    else:
        _print_section(
            "HIPÓTESIS",
            "  No se generaron hipótesis automáticas para este relato.\n"
            "  El síntoma fue capturado; se requiere más contexto.",
        )

    # — Estado clínico —
    _print_section("ESTADO DE ADMISIÓN", f"  {state.state}")

    # — Respuesta formateada (mensaje sobrio para el dueño) —
    formatter = AdmissionResponseFormatterV1()
    formatted = formatter.format_response(artifact)
    if formatted:
        _print_section("MENSAJE CLÍNICO PARA EL DUEÑO", formatted)

    print(f"\n{_HEADER}\n")


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "\nUso: python -m pymia.cli.demo \"<relato del dueño>\"\n"
            "\nEjemplo:\n"
            "  python -m pymia.cli.demo \"vendo mucho pero no sé si gano plata\"\n"
        )
        sys.exit(1)

    claim = " ".join(sys.argv[1:])
    run_demo(claim)


if __name__ == "__main__":
    main()
