#!/usr/bin/env python3
"""Diagnóstico local de proveedores Hermes sin gastar tokens.

Objetivo:
- detectar credenciales/configuración disponible para agentes Hermes
- distinguir AUTH_MISSING vs CONFIG_PRESENT
- recomendar un provider operativo antes de lanzar loops

Este script NO llama APIs externas y NO consume tokens.
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


DEFAULT_HERMES_HOME = Path("~/.hermes").expanduser()
DEFAULT_HERMES_REPO = Path("/opt/smartpyme-factory/repos/hermes-agent")
DEFAULT_SMARTPYME_REPO = Path("/opt/smartpyme-factory/repos/SmartPyme")


@dataclass(frozen=True)
class ProviderCheck:
    provider: str
    status: str
    evidence: list[str]
    recommendation: str


@dataclass(frozen=True)
class HermesDoctorReport:
    hermes_home: str
    hermes_repo: str
    smartpyme_repo: str
    providers: list[ProviderCheck]
    recommended_provider: str | None
    safe_to_run_loop: bool
    notes: list[str]


def _exists(path: Path) -> bool:
    try:
        return path.exists()
    except OSError:
        return False


def _env_present(names: Iterable[str]) -> list[str]:
    return [name for name in names if os.environ.get(name)]


def _file_present(paths: Iterable[Path]) -> list[str]:
    return [str(path) for path in paths if _exists(path)]


def _status_from_evidence(evidence: list[str]) -> str:
    return "CONFIG_PRESENT" if evidence else "AUTH_MISSING"


def check_codex(hermes_home: Path) -> ProviderCheck:
    evidence = []
    evidence.extend(f"env:{name}" for name in _env_present(["OPENAI_API_KEY", "CODEX_HOME"]))
    evidence.extend(
        f"file:{path}"
        for path in _file_present(
            [
                hermes_home / "codex.json",
                hermes_home / "auth.json",
                Path("~/.codex/auth.json").expanduser(),
                Path("~/.config/codex/auth.json").expanduser(),
            ]
        )
    )
    status = _status_from_evidence(evidence)
    recommendation = (
        "Codex parece configurable. Probar con prompt liviano antes de loop."
        if status == "CONFIG_PRESENT"
        else "Codex sin credenciales detectadas. Ejecutar `hermes auth` o `hermes model`."
    )
    return ProviderCheck("codex", status, evidence, recommendation)


def check_gemini_vertex(hermes_home: Path) -> ProviderCheck:
    evidence = []
    evidence.extend(
        f"env:{name}"
        for name in _env_present(
            [
                "GOOGLE_CLOUD_PROJECT",
                "GCP_PROJECT",
                "GCLOUD_PROJECT",
                "GOOGLE_APPLICATION_CREDENTIALS",
                "GEMINI_API_KEY",
                "GOOGLE_API_KEY",
            ]
        )
    )
    evidence.extend(
        f"file:{path}"
        for path in _file_present(
            [
                Path("~/.config/gcloud/application_default_credentials.json").expanduser(),
                hermes_home / "config.yaml",
            ]
        )
    )
    status = _status_from_evidence(evidence)
    recommendation = (
        "Gemini/Vertex parece disponible. Recomendado como builder temporal."
        if status == "CONFIG_PRESENT"
        else "No se detectó configuración Gemini/Vertex. Revisar gcloud auth application-default login o API key."
    )
    return ProviderCheck("gemini_vertex", status, evidence, recommendation)


def check_deepseek() -> ProviderCheck:
    evidence = []
    evidence.extend(
        f"env:{name}"
        for name in _env_present(["DEEPSEEK_API_KEY", "OPENROUTER_API_KEY"])
    )
    status = _status_from_evidence(evidence)
    recommendation = (
        "DeepSeek/OpenRouter parece disponible. Recomendado como auditor/refuerzo."
        if status == "CONFIG_PRESENT"
        else "No se detectó DeepSeek/OpenRouter. Configurar API key si se usará como auditor."
    )
    return ProviderCheck("deepseek", status, evidence, recommendation)


def check_openrouter() -> ProviderCheck:
    evidence = []
    evidence.extend(f"env:{name}" for name in _env_present(["OPENROUTER_API_KEY"]))
    status = _status_from_evidence(evidence)
    recommendation = (
        "OpenRouter parece disponible. Puede rutear Gemini, DeepSeek, Qwen u otros."
        if status == "CONFIG_PRESENT"
        else "OpenRouter no disponible por env."
    )
    return ProviderCheck("openrouter", status, evidence, recommendation)


def choose_provider(providers: list[ProviderCheck]) -> str | None:
    priority = ["gemini_vertex", "deepseek", "openrouter", "codex"]
    by_name = {provider.provider: provider for provider in providers}
    for name in priority:
        provider = by_name.get(name)
        if provider and provider.status == "CONFIG_PRESENT":
            return name
    return None


def build_report(hermes_home: Path, hermes_repo: Path, smartpyme_repo: Path) -> HermesDoctorReport:
    providers = [
        check_codex(hermes_home),
        check_gemini_vertex(hermes_home),
        check_deepseek(),
        check_openrouter(),
    ]
    recommended_provider = choose_provider(providers)
    notes = [
        "Este diagnóstico no llama APIs externas y no consume tokens.",
        "CONFIG_PRESENT no garantiza cuota; solo confirma credenciales/config local detectables.",
        "Antes de correr loops, ejecutar un prompt liviano: `Responde solo con OK si estás disponible.`",
    ]
    if not _exists(hermes_repo):
        notes.append(f"Hermes repo no encontrado en {hermes_repo}")
    if not _exists(smartpyme_repo):
        notes.append(f"SmartPyme repo no encontrado en {smartpyme_repo}")

    return HermesDoctorReport(
        hermes_home=str(hermes_home),
        hermes_repo=str(hermes_repo),
        smartpyme_repo=str(smartpyme_repo),
        providers=providers,
        recommended_provider=recommended_provider,
        safe_to_run_loop=recommended_provider is not None,
        notes=notes,
    )


def print_human(report: HermesDoctorReport) -> None:
    print("HERMES_PROVIDER_DOCTOR")
    print(f"hermes_home={report.hermes_home}")
    print(f"hermes_repo={report.hermes_repo}")
    print(f"smartpyme_repo={report.smartpyme_repo}")
    print("")
    for provider in report.providers:
        print(f"[{provider.provider}] {provider.status}")
        for item in provider.evidence:
            print(f"  - {item}")
        print(f"  recommendation: {provider.recommendation}")
        print("")
    print(f"recommended_provider={report.recommended_provider or 'NONE'}")
    print(f"safe_to_run_loop={str(report.safe_to_run_loop).lower()}")
    print("")
    print("notes:")
    for note in report.notes:
        print(f"- {note}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Diagnóstico local de providers Hermes")
    parser.add_argument("--json", action="store_true", help="emitir JSON")
    parser.add_argument("--hermes-home", default=str(DEFAULT_HERMES_HOME))
    parser.add_argument("--hermes-repo", default=str(DEFAULT_HERMES_REPO))
    parser.add_argument("--smartpyme-repo", default=str(DEFAULT_SMARTPYME_REPO))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(
        hermes_home=Path(args.hermes_home).expanduser(),
        hermes_repo=Path(args.hermes_repo).expanduser(),
        smartpyme_repo=Path(args.smartpyme_repo).expanduser(),
    )
    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        print_human(report)
    return 0 if report.safe_to_run_loop else 2


if __name__ == "__main__":
    raise SystemExit(main())
