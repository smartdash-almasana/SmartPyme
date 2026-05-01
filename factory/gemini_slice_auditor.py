from __future__ import annotations

import argparse
import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from google import genai

ROOT_DESTINO = Path(r"E:\BuenosPasos\smartbridge\SmartPyme")
DEFAULT_OUTPUT_DIR = ROOT_DESTINO / "factory" / "hallazgos" / "pending"
EXCLUDED_PARTS = {".git", ".venv", "__pycache__"}
REQUIRED_HALLAZGO_MARKERS = ("# HALLAZGO", "## META", "## OBJETIVO")
ALLOWED_DESTINATION_ROOTS = ("app/", "tests/", "factory/")
MODULE_ALLOWED_TARGETS: dict[str, list[str]] = {
    "clarification": [
        r"app\core\clarification\models.py",
        r"app\core\clarification\service.py",
        r"app\core\clarification\persistence.py",
        r"tests\core\test_clarification_service.py",
    ],
    "reconciliation": [
        r"app\core\reconciliation\models.py",
        r"app\core\reconciliation\service.py",
        r"tests\core\test_reconciliation_service.py",
    ],
    "validation": [
        r"app\core\validation\models.py",
        r"app\core\validation\service.py",
        r"tests\core\test_validation_service.py",
    ],
}
MODULE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "clarification": ("clarif", "uncert", "question", "human", "pending", "block", "decision"),
    "reconciliation": ("recon", "match", "diff", "discrep", "order_id", "duplicate", "missing"),
    "validation": ("valid", "rule", "check", "constraint", "schema", "reject"),
}
FORBIDDEN_PATH_HINTS = (
    "src\\",
    "src/",
    "workflow.py",
    "rules.py",
    "api",
    "routes",
    "adapters",
    "message_processing",
    "profiling",
    "smokes",
)


@dataclass(frozen=True)
class AuditConfig:
    modulo_objetivo: str
    repo_destino: Path
    rutas_fuente: list[Path]
    output_dir: Path
    model: str
    max_chars_per_file: int = 12000
    max_files_per_repo: int = 12


def read_text_file(path: Path, max_chars: int) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="latin-1", errors="ignore")
    return text[:max_chars]


def is_excluded_path(path: Path) -> bool:
    lowered_parts = {part.lower() for part in path.parts}
    return any(excluded in lowered_parts for excluded in EXCLUDED_PARTS)


def candidate_files(repo_path: Path, max_files: int, modulo_objetivo: str) -> list[Path]:
    keywords = MODULE_KEYWORDS.get(
        modulo_objetivo.lower(),
        ("clarif", "recon", "valid", "pending", "block"),
    )
    allowed_suffixes = {".py", ".md", ".txt", ".json", ".yaml", ".yml"}

    candidates: list[Path] = []
    for path in repo_path.rglob("*"):
        if not path.is_file():
            continue
        if is_excluded_path(path):
            continue
        if path.suffix.lower() not in allowed_suffixes:
            continue

        lowered = str(path).lower()
        if any(
            token in lowered
            for token in ("workflow.py", "rules.py", "route", "adapter", "profiling", "smoke")
        ):
            continue
        if any(keyword in lowered for keyword in keywords):
            candidates.append(path)

    if len(candidates) >= max_files:
        return sorted(candidates)[:max_files]

    extra: list[Path] = []
    for path in repo_path.rglob("*.py"):
        if is_excluded_path(path):
            continue
        extra.append(path)

    merged = list(dict.fromkeys(sorted(candidates) + sorted(extra)))
    return merged[:max_files]


def build_prompt(config: AuditConfig, repo_path: Path, files: list[Path]) -> str:
    modulo_key = config.modulo_objetivo.lower()
    allowed_targets = MODULE_ALLOWED_TARGETS.get(modulo_key)
    if not allowed_targets:
        allowed_targets = [r"app\core\<modulo>\models.py", r"app\core\<modulo>\service.py"]
    allowed_targets_text = "\n".join(f"- {target}" for target in allowed_targets)
    forbidden_hints_text = ", ".join(FORBIDDEN_PATH_HINTS)

    file_sections: list[str] = []
    for file_path in files:
        rel = file_path.relative_to(repo_path)
        content = read_text_file(file_path, config.max_chars_per_file)
        file_sections.append(
            f"\n### ARCHIVO: {file_path}\n### RUTA_RELATIVA: {rel}\n```text\n{content}\n```\n"
        )

    joined_files = "\n".join(file_sections)

    return f"""
ROLE: Auditor técnico de cantera + clasificador de slices. Modo ejecución. Sin teoría.

OBJETIVO
Analizar esta ruta local como cantera para el módulo {config.modulo_objetivo} de SmartPyme.

RUTA_CANTERA
{repo_path}

REPO_DESTINO
{config.repo_destino}

MODULO_OBJETIVO
{config.modulo_objetivo}

DEFINICION_OPERATIVA DEL MODULO
- human-in-the-loop
- uncertainty resolution
- pending validation
- blocking workflow
- persistence of human decision
- question generation
- clarification state
- fail-closed

INSTRUCCIONES
1. Analizá solo los archivos provistos.
2. Detectá piezas útiles para el módulo objetivo.
3. Clasificá cada pieza como:
   - A = adoptar casi directo
   - B = adaptar
   - C = referencia conceptual
   - D = descartar
4. Priorizá piezas ya implementadas, concretas y reutilizables.
5. No inventes archivos no visibles.
6. No escribas código.
7. No refactorices.
8. Si no hay material útil, decilo con claridad.
9. Debés generar un hallazgo ejecutable para SmartPyme, con alcance mínimo y determinístico.

REGLAS ESTRICTAS DE SALIDA (OBLIGATORIAS)
- Rutas destino permitidas SOLO para {config.modulo_objetivo}:
{allowed_targets_text}
- NO proponer rutas fuera de `app\\core\\...` y `tests\\core\\...`
- NO proponer nada que contenga: {forbidden_hints_text}
- Máximo 3 archivos en `## PROPUESTA_DE_PORTADO`.
- Priorizar slices de lógica pura y determinística (funciones/modelos/core).
- Evitar documentos extensos, snapshots, glue code de framework
  y código de infraestructura como TOP_SLICES.
- Si no hay slices adecuados para ese alcance mínimo:
  dejarlo explícitamente bloqueado en el hallazgo.
- No inventar rutas: usar solo rutas reales observadas o rutas permitidas exactas de portado.

FORMATO OBLIGATORIO
Respondé SOLO en markdown con esta estructura exacta:

# HALLAZGO

## META
- id:
- estado: pending
- modulo_objetivo: {config.modulo_objetivo}
- prioridad:
- origen: gemini-vertex
- repo_destino: {config.repo_destino}

## OBJETIVO
<una frase>

## RUTAS_FUENTE
- <ruta 1>
- <ruta 2>

## SLICES_CANDIDATOS
### Slice 1
- ruta:
- tipo:
- resumen:
- clasificacion:
- motivo:

## TOP_SLICES
1. <ruta>
2. <ruta>

## PROPUESTA_DE_PORTADO
### Crear o modificar solo:
- <ruta destino 1>
- <ruta destino 2>

## REGLAS_DE_EJECUCION
- no tocar otros módulos salvo imports mínimos imprescindibles
- no refactor global
- no inventar rutas
- fail-closed obligatorio
- humano en el loop obligatorio
- si falta contexto, bloquear y preguntar
- correr tests mínimos del módulo

## CRITERIO_DE_CIERRE
- módulo compila
- tests mínimos pasan
- comportamiento de bloqueo queda preservado

## DUDAS_DETECTADAS
- ninguna (si aplica)

## PREGUNTA_AL_OWNER
- null (si aplica)

ARCHIVOS A ANALIZAR
{joined_files}
""".strip()


def build_no_files_fallback(config: AuditConfig, repo_path: Path) -> str:
    return f"""# HALLAZGO

## META
- id: H-{datetime.now().strftime("%Y%m%d-%H%M")}-000
- estado: pending
- modulo_objetivo: {config.modulo_objetivo}
- prioridad: baja
- origen: gemini-vertex
- repo_destino: {config.repo_destino}

## OBJETIVO
No se encontraron archivos candidatos visibles para el módulo objetivo.

## RUTAS_FUENTE
- {repo_path}

## SLICES_CANDIDATOS
### Slice 1
- ruta: null
- tipo: null
- resumen: Sin material visible útil en el escaneo inicial.
- clasificacion: D
- motivo: No hubo archivos candidatos.

## TOP_SLICES
1. null

## PROPUESTA_DE_PORTADO
### Crear o modificar solo:
- null

## REGLAS_DE_EJECUCION
- no tocar otros módulos salvo imports mínimos imprescindibles
- no refactor global
- no inventar rutas
- fail-closed obligatorio
- humano en el loop obligatorio
- si falta contexto, bloquear y preguntar
- correr tests mínimos del módulo

## CRITERIO_DE_CIERRE
- reevaluar cantera con otro filtro

## DUDAS_DETECTADAS
- ninguna

## PREGUNTA_AL_OWNER
- null
"""


def build_invalid_model_fallback(
    config: AuditConfig,
    repo_path: Path,
    reason: str,
) -> str:
    return f"""# HALLAZGO

## META
- id: H-{datetime.now().strftime("%Y%m%d-%H%M")}-INVALID
- estado: pending
- modulo_objetivo: {config.modulo_objetivo}
- prioridad: media
- origen: gemini-vertex
- repo_destino: {config.repo_destino}

## OBJETIVO
La salida del modelo fue inválida o vacía y el hallazgo quedó bloqueado para revisión manual.

## RUTAS_FUENTE
- {repo_path}

## SLICES_CANDIDATOS
### Slice 1
- ruta: null
- tipo: salida_modelo_invalida
- resumen: El auditor no recibió markdown válido con la estructura mínima requerida.
- clasificacion: D
- motivo: {reason}

## TOP_SLICES
1. null

## PROPUESTA_DE_PORTADO
### Crear o modificar solo:
- null

## REGLAS_DE_EJECUCION
- no tocar otros módulos salvo imports mínimos imprescindibles
- no refactor global
- no inventar rutas
- fail-closed obligatorio
- humano en el loop obligatorio
- si falta contexto, bloquear y preguntar
- correr tests mínimos del módulo

## CRITERIO_DE_CIERRE
- repetir auditoría con salida válida del modelo
- verificar contexto enviado
- confirmar estructura mínima del hallazgo

## DUDAS_DETECTADAS
- salida del modelo inválida o incompleta

## PREGUNTA_AL_OWNER
- null
"""


def is_valid_hallazgo_markdown(content: str) -> bool:
    normalized = content.strip()
    if not normalized:
        return False
    return all(marker in normalized for marker in REQUIRED_HALLAZGO_MARKERS)


def call_gemini(prompt: str, model: str) -> str:
    client = genai.Client(
        vertexai=True,
        project=os.environ["GOOGLE_CLOUD_PROJECT"],
        location=os.environ.get("GOOGLE_CLOUD_LOCATION", "global"),
    )

    response = client.models.generate_content(
        model=model,
        contents=prompt,
    )
    return (response.text or "").strip()


def sanitize_slug(value: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "-" for ch in value)
    while "--" in cleaned:
        cleaned = cleaned.replace("--", "-")
    return cleaned.strip("-")


def _extract_section_lines(content: str, section_title: str) -> list[str]:
    lines = content.splitlines()
    start_index = None
    for index, line in enumerate(lines):
        if line.strip() == section_title:
            start_index = index + 1
            break
    if start_index is None:
        return []

    collected: list[str] = []
    for line in lines[start_index:]:
        if line.startswith("## "):
            break
        collected.append(line)
    return collected


def _sanitize_target_path_token(raw_token: str) -> str:
    token = raw_token.strip()
    if not token:
        return ""

    if token.startswith("[") and "](" in token and token.endswith(")"):
        paren_index = token.rfind("](")
        if paren_index != -1:
            token = token[paren_index + 2 : -1].strip()

    wrappers = ("`", "'", '"', "<", ">")
    while token and token[0] in wrappers:
        token = token[1:].strip()
    while token and token[-1] in wrappers:
        token = token[:-1].strip()

    normalized = token.replace("\\", "/")
    match = re.search(r"(?i)\b(app|tests|factory)/[a-z0-9_./-]+", normalized)
    if not match:
        return ""
    return match.group(0).rstrip(".,;:")


def _normalize_path_style(path: str) -> str:
    return path.replace("\\", "/").strip()


def _is_allowed_destination_path(path: str) -> bool:
    normalized = _normalize_path_style(path).lower()
    return any(normalized.startswith(root) for root in ALLOWED_DESTINATION_ROOTS)


def _normalize_propuesta_de_portado(content: str, modulo_objetivo: str) -> str:
    section_title = "## PROPUESTA_DE_PORTADO"
    if section_title not in content:
        return content

    lines = content.splitlines()
    start_index = None
    end_index = None
    for idx, line in enumerate(lines):
        if line.strip() == section_title:
            start_index = idx
            continue
        if start_index is not None and line.startswith("## "):
            end_index = idx
            break
    if start_index is None:
        return content
    if end_index is None:
        end_index = len(lines)

    raw_lines = lines[start_index + 1 : end_index]
    normalized_targets: list[str] = []
    for line in raw_lines:
        stripped = line.strip()
        if not stripped.startswith("- "):
            continue
        candidate = _sanitize_target_path_token(stripped[2:].strip())
        if not candidate:
            continue
        normalized = _normalize_path_style(candidate)
        if normalized.lower() in {"null", "none"}:
            continue
        if not _is_allowed_destination_path(normalized):
            continue
        if normalized not in normalized_targets:
            normalized_targets.append(normalized)

    if not normalized_targets:
        allowed_targets = MODULE_ALLOWED_TARGETS.get(modulo_objetivo.lower(), [])
        for target in allowed_targets:
            normalized = _normalize_path_style(target)
            if _is_allowed_destination_path(normalized) and normalized not in normalized_targets:
                normalized_targets.append(normalized)
            if len(normalized_targets) >= 2:
                break

    if not normalized_targets:
        normalized_targets = [f"app/core/{modulo_objetivo.lower()}/service.py"]

    normalized_targets = normalized_targets[:3]
    replacement = [
        section_title,
        "### Crear o modificar solo:",
        *[f"- {target}" for target in normalized_targets],
    ]
    merged = lines[:start_index] + replacement + lines[end_index:]
    return "\n".join(merged).strip() + "\n"


def _has_executable_proposal(content: str) -> bool:
    proposal_lines = _extract_section_lines(content, "## PROPUESTA_DE_PORTADO")
    targets = [line.strip() for line in proposal_lines if line.strip().startswith("- ")]
    if not targets:
        return False
    normalized = [line[2:].strip().lower() for line in targets]
    return all(value not in {"null", "- null"} for value in normalized)


def _normalize_owner_question_when_not_blocked(content: str) -> str:
    if "## PREGUNTA_AL_OWNER" not in content:
        return content
    if not _has_executable_proposal(content):
        return content

    lines = content.splitlines()
    start_index = None
    end_index = None
    for idx, line in enumerate(lines):
        if line.strip() == "## PREGUNTA_AL_OWNER":
            start_index = idx
            continue
        if start_index is not None and line.startswith("## "):
            end_index = idx
            break
    if start_index is None:
        return content
    if end_index is None:
        end_index = len(lines)

    replacement = ["## PREGUNTA_AL_OWNER", "- null"]
    merged = lines[:start_index] + replacement + lines[end_index:]
    return "\n".join(merged).strip() + "\n"


def write_hallazgo(output_dir: Path, modulo: str, source_repo: Path, content: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    slug = sanitize_slug(f"{modulo}-{source_repo.name}")
    filename = f"{timestamp}-{slug}.md"
    out_path = output_dir / filename
    out_path.write_text(content, encoding="utf-8")
    return out_path


def audit_single_repo(config: AuditConfig, repo_path: Path) -> Path:
    files = candidate_files(repo_path, config.max_files_per_repo, config.modulo_objetivo)
    if not files:
        fallback = build_no_files_fallback(config, repo_path)
        return write_hallazgo(config.output_dir, config.modulo_objetivo, repo_path, fallback)

    prompt = build_prompt(config, repo_path, files)
    result_md = call_gemini(prompt, config.model)

    if not result_md:
        result_md = build_invalid_model_fallback(
            config=config,
            repo_path=repo_path,
            reason="response.text llegó vacío o solo whitespace.",
        )
    elif not is_valid_hallazgo_markdown(result_md):
        result_md = build_invalid_model_fallback(
            config=config,
            repo_path=repo_path,
            reason="faltan marcadores mínimos obligatorios: # HALLAZGO / ## META / ## OBJETIVO.",
        )
    else:
        result_md = _normalize_propuesta_de_portado(result_md, config.modulo_objetivo)
        result_md = _normalize_owner_question_when_not_blocked(result_md)

    return write_hallazgo(config.output_dir, config.modulo_objetivo, repo_path, result_md)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Auditor de slices con Gemini Vertex.")
    parser.add_argument(
        "--modulo",
        required=True,
        help="Módulo objetivo, por ejemplo: clarification",
    )
    parser.add_argument(
        "--repo-destino",
        default=str(ROOT_DESTINO),
        help="Ruta del repo destino SmartPyme.",
    )
    parser.add_argument(
        "--rutas-fuente",
        nargs="+",
        required=True,
        help="Lista de rutas cantera a auditar.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Carpeta donde escribir hallazgos .md",
    )
    parser.add_argument(
        "--model",
        default="gemini-2.5-flash-lite",
        help="Modelo Vertex Gemini.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    config = AuditConfig(
        modulo_objetivo=args.modulo,
        repo_destino=Path(args.repo_destino),
        rutas_fuente=[Path(p) for p in args.rutas_fuente],
        output_dir=Path(args.output_dir),
        model=args.model,
    )

    missing_env = [name for name in ("GOOGLE_CLOUD_PROJECT",) if not os.environ.get(name)]
    if missing_env:
        raise SystemExit(f"Faltan variables de entorno obligatorias: {', '.join(missing_env)}")

    print("=== GEMINI SLICE AUDITOR ===")
    print(f"Modulo objetivo: {config.modulo_objetivo}")
    print(f"Repo destino: {config.repo_destino}")
    print(f"Output dir: {config.output_dir}")
    print(f"Modelo: {config.model}")
    print()

    for repo_path in config.rutas_fuente:
        print(f"[AUDITANDO] {repo_path}")
        out = audit_single_repo(config, repo_path)
        print(f"[OK] Hallazgo escrito en: {out}")


if __name__ == "__main__":
    main()
