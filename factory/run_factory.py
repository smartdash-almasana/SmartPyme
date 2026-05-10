import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Callable

from factory.topology_catalog import load_topology_catalog

BASE_DIR = Path(__file__).resolve().parents[1]
FACTORY_DIR = BASE_DIR / "factory"
HALLAZGOS_DIR = FACTORY_DIR / "hallazgos"
PENDING_DIR = HALLAZGOS_DIR / "pending"
IN_PROGRESS_DIR = HALLAZGOS_DIR / "in_progress"
BLOCKED_DIR = HALLAZGOS_DIR / "blocked"
DONE_DIR = HALLAZGOS_DIR / "done"
AUDITOR_PATH = FACTORY_DIR / "gemini_slice_auditor.py"
ALLOWED_ROOTS = {"app", "tests", "factory"}


def find_newest_hallazgo(directory: Path) -> Path | None:
    files = list(directory.glob("*.md"))
    if not files:
        return None
    return max(files, key=lambda path: path.stat().st_mtime)


def _snapshot_markdown_files(directory: Path) -> set[Path]:
    return {path.resolve() for path in directory.glob("*.md")}


def _detect_new_hallazgos(before: set[Path], directory: Path) -> list[Path]:
    current = [path for path in directory.glob("*.md")]
    return [path for path in current if path.resolve() not in before]


def _read_estado(content: str) -> str:
    for line in content.splitlines():
        stripped = line.strip().lower()
        if stripped.startswith("- estado:"):
            return stripped.replace("- estado:", "", 1).strip()
    return "pending"


def _read_modulo_objetivo(content: str) -> str | None:
    for line in content.splitlines():
        stripped = line.strip().lower()
        if stripped.startswith("- modulo_objetivo:"):
            modulo = stripped.replace("- modulo_objetivo:", "", 1).strip()
            return modulo or None
    return None


def _read_cantera_raiz(content: str) -> str | None:
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("- cantera_raiz:"):
            value = stripped.split(":", 1)[1].strip()
            return value or None
    return None


def _upsert_meta_field(content: str, field_name: str, field_value: str) -> str:
    lines = content.splitlines()
    meta_header = None
    meta_end = None
    for idx, line in enumerate(lines):
        if line.strip() == "## META":
            meta_header = idx
            continue
        if meta_header is not None and line.startswith("## "):
            meta_end = idx
            break
    if meta_header is None:
        return content
    if meta_end is None:
        meta_end = len(lines)

    prefix = f"- {field_name}:"
    for idx in range(meta_header + 1, meta_end):
        if lines[idx].strip().lower().startswith(prefix.lower()):
            lines[idx] = f"- {field_name}: {field_value}"
            return "\n".join(lines) + ("\n" if content.endswith("\n") else "")

    insert_at = meta_end
    lines.insert(insert_at, f"- {field_name}: {field_value}")
    return "\n".join(lines) + ("\n" if content.endswith("\n") else "")


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


def _has_open_question(content: str) -> bool:
    section_lines = _extract_section_lines(content, "## PREGUNTA_AL_OWNER")
    meaningful = [line.strip() for line in section_lines if line.strip()]
    if not meaningful:
        return False
    if len(meaningful) == 1 and meaningful[0].lower() in {"- null", "null"}:
        return False
    return True


def _extract_target_paths(content: str) -> list[str]:
    proposal_lines = _extract_section_lines(content, "## PROPUESTA_DE_PORTADO")
    targets: list[str] = []
    for line in proposal_lines:
        stripped = line.strip()
        if stripped.startswith("- "):
            target = _sanitize_target_path_token(stripped[2:].strip())
            if target:
                targets.append(target)
    return targets


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

    # Normalizar separadores Windows → forward slash para compatibilidad cross-platform.
    # Solo afecta la representación del string; las validaciones de seguridad
    # (ALLOWED_ROOTS, src/ check) operan sobre el path normalizado.
    token = token.replace("\\", "/")

    return token


def validate_hallazgo(
    file_path: Path,
    repo_root: Path = BASE_DIR,
    require_cantera_raiz: bool = False,
) -> tuple[bool, str]:
    content = file_path.read_text(encoding="utf-8")
    topology_catalog = load_topology_catalog(repo_root / "factory" / "topology_catalog.json")

    required_sections = [
        "# HALLAZGO",
        "## META",
        "## OBJETIVO",
        "## PROPUESTA_DE_PORTADO",
        "## REGLAS_DE_EJECUCION",
        "## CRITERIO_DE_CIERRE",
    ]
    for section in required_sections:
        if section not in content:
            return False, f"SECCION_FALTANTE: {section}"

    if _has_open_question(content):
        return False, "PREGUNTA_ABIERTA: completar decision del owner antes de ejecutar."

    if require_cantera_raiz and not _read_cantera_raiz(content):
        return False, "CANTERA_RAIZ_FALTANTE: metadata obligatoria para execute_ready."

    target_paths = _extract_target_paths(content)
    if not target_paths:
        return False, "RUTAS_DESTINO_VACIAS: no hay rutas en PROPUESTA_DE_PORTADO."

    modulo_objetivo = _read_modulo_objetivo(content)
    if topology_catalog is not None:
        if not modulo_objetivo:
            return False, "MODULO_OBJETIVO_FALTANTE: requerido por topologia rectora."
        if not topology_catalog.is_known_layer(modulo_objetivo):
            return False, f"CAPA_OBJETIVO_INVALIDA: {modulo_objetivo}"

    normalized_targets: list[str] = []
    repo_root_resolved = repo_root.resolve()
    for raw_path in target_paths:
        normalized = raw_path.lower()
        if "src\\" in normalized or "src/" in normalized:
            return False, f"RUTA_SRC_BLOQUEADA: {raw_path}"

        candidate = Path(raw_path)
        relative = candidate
        if candidate.is_absolute():
            try:
                relative = candidate.resolve().relative_to(repo_root_resolved)
            except ValueError:
                return False, f"RUTA_FUERA_REPO: {raw_path}"

        if not relative.parts:
            return False, f"RUTA_INVALIDA: {raw_path}"

        if relative.parts[0] not in ALLOWED_ROOTS:
            return False, f"RAIZ_NO_AUTORIZADA: {raw_path}"

        normalized_targets.append(str(relative).replace("\\", "/").lower())

    if topology_catalog is not None and modulo_objetivo:
        allowed_targets = topology_catalog.allowed_target_paths_for_layer(modulo_objetivo)
        if allowed_targets:
            for target in normalized_targets:
                if target not in allowed_targets:
                    return False, f"RUTA_FUERA_DE_CAPA: {target} no pertenece a {modulo_objetivo}"

    return True, "VALIDACION_OK"


def _resolve_unique_destination(destination_dir: Path, original_name: str) -> Path:
    base_candidate = destination_dir / original_name
    if not base_candidate.exists():
        return base_candidate

    stem = Path(original_name).stem
    suffix = Path(original_name).suffix
    index = 1
    while True:
        candidate = destination_dir / f"{stem}-{index:02d}{suffix}"
        if not candidate.exists():
            return candidate
        index += 1


def move_hallazgo(file_path: Path, destination_dir: Path) -> Path:
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = _resolve_unique_destination(destination_dir, file_path.name)
    shutil.move(str(file_path), str(destination))
    return destination


def _ensure_hallazgo_dirs(
    *,
    pending_dir: Path,
    in_progress_dir: Path,
    blocked_dir: Path,
    done_dir: Path,
) -> None:
    pending_dir.mkdir(parents=True, exist_ok=True)
    in_progress_dir.mkdir(parents=True, exist_ok=True)
    blocked_dir.mkdir(parents=True, exist_ok=True)
    done_dir.mkdir(parents=True, exist_ok=True)


def move_hallazgo_to_blocked(file_path: Path, blocked_dir: Path) -> Path:
    blocked_dir.mkdir(parents=True, exist_ok=True)
    candidate = _resolve_unique_destination(blocked_dir, file_path.name)
    shutil.move(str(file_path), str(candidate))
    return candidate


def process_pending_hallazgos(
    *,
    pending_dir: Path = PENDING_DIR,
    in_progress_dir: Path = IN_PROGRESS_DIR,
    blocked_dir: Path = BLOCKED_DIR,
    done_dir: Path = DONE_DIR,
    repo_root: Path = BASE_DIR,
) -> dict[str, object]:
    _ensure_hallazgo_dirs(
        pending_dir=pending_dir,
        in_progress_dir=in_progress_dir,
        blocked_dir=blocked_dir,
        done_dir=done_dir,
    )

    files = sorted(
        pending_dir.glob("*.md"),
        key=lambda path: path.stat().st_mtime,
    )
    summary: dict[str, object] = {
        "total": len(files),
        "processed": 0,
        "moved_to_in_progress": [],
        "moved_to_done": [],
        "moved_to_blocked": [],
    }

    for hallazgo in files:
        is_valid, reason = validate_hallazgo(hallazgo, repo_root=repo_root)
        if not is_valid:
            moved = move_hallazgo_to_blocked(hallazgo, blocked_dir)
            summary["moved_to_blocked"].append(
                {"archivo": str(moved), "motivo": reason}
            )
            summary["processed"] += 1
            continue

        content = hallazgo.read_text(encoding="utf-8")
        estado_meta = _read_estado(content)
        if estado_meta == "done":
            moved = move_hallazgo(hallazgo, done_dir)
            summary["moved_to_done"].append(str(moved))
        else:
            moved = move_hallazgo(hallazgo, in_progress_dir)
            summary["moved_to_in_progress"].append(str(moved))
        summary["processed"] += 1

    return summary


def run_auditor(
    modulo: str,
    rutas_fuente: list[str],
    repo_destino: str,
    model: str | None = None,
    timeout_seconds: int | None = None,
) -> None:
    if not AUDITOR_PATH.exists():
        raise RuntimeError(f"AUDITOR_NO_ENCONTRADO: {AUDITOR_PATH}")

    if not rutas_fuente:
        raise ValueError("RUTAS_FUENTE_INVALIDAS: se requiere al menos una ruta fuente.")

    if not os.environ.get("GOOGLE_CLOUD_PROJECT"):
        raise RuntimeError("AUDITOR_ENV_MISSING: GOOGLE_CLOUD_PROJECT")

    command = [
        sys.executable,
        str(AUDITOR_PATH),
        "--modulo",
        modulo,
        "--rutas-fuente",
        *rutas_fuente,
        "--repo-destino",
        repo_destino,
    ]
    if model:
        command.extend(["--model", model])

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(
            f"AUDITOR_TIMEOUT: supero {timeout_seconds}s para modulo={modulo}"
        ) from exc
    if result.returncode != 0:
        raise RuntimeError(f"AUDITOR_ERROR: {result.stderr.strip()}")


def run_factory(
    *,
    modo: str,
    modulo: str,
    rutas_fuente: list[str],
    repo_destino: str,
    model: str | None = None,
    commit_mode: str = "disabled",
    auditor_timeout_seconds: int | None = None,
    pending_dir: Path = PENDING_DIR,
    in_progress_dir: Path = IN_PROGRESS_DIR,
    blocked_dir: Path = BLOCKED_DIR,
    done_dir: Path = DONE_DIR,
    repo_root: Path = BASE_DIR,
    auditor_runner: Callable[[str, list[str], str, str | None, int | None], None] = run_auditor,
) -> dict[str, str]:
    if commit_mode != "disabled":
        raise ValueError(
            "COMMIT_MODE_NO_IMPLEMENTADO: solo se permite commit_mode=disabled por ahora."
        )

    if Path(repo_destino).resolve() != repo_root.resolve():
        raise ValueError("REPO_DESTINO_INVALIDO: debe ser el repositorio SmartPyme local.")
    if not isinstance(rutas_fuente, list) or not all(
        isinstance(ruta, str) and ruta.strip() for ruta in rutas_fuente
    ):
        raise ValueError("RUTAS_FUENTE_INVALIDAS: debe ser list[str] no vacio.")

    topology_catalog = load_topology_catalog(repo_root / "factory" / "topology_catalog.json")
    if topology_catalog is not None:
        if not topology_catalog.is_known_layer(modulo):
            raise ValueError(f"CAPA_OBJETIVO_INVALIDA: {modulo}")
        for ruta_fuente in rutas_fuente:
            if not topology_catalog.can_excavate(ruta_fuente, modulo):
                raise ValueError(
                    f"CANTERA_NO_HABILITADA_PARA_CAPA: cantera={ruta_fuente} capa={modulo}"
                )

    _ensure_hallazgo_dirs(
        pending_dir=pending_dir,
        in_progress_dir=in_progress_dir,
        blocked_dir=blocked_dir,
        done_dir=done_dir,
    )
    before = _snapshot_markdown_files(pending_dir)
    auditor_runner(modulo, rutas_fuente, repo_destino, model, auditor_timeout_seconds)

    new_hallazgos = _detect_new_hallazgos(before, pending_dir)
    if not new_hallazgos:
        raise RuntimeError(
            "HALLAZGO_NUEVO_NO_ENCONTRADO: auditor no genero hallazgo nuevo en pending."
        )
    hallazgo = max(new_hallazgos, key=lambda path: path.stat().st_mtime)

    cantera_raiz = rutas_fuente[0]
    content_with_cantera = _upsert_meta_field(
        hallazgo.read_text(encoding="utf-8"),
        "cantera_raiz",
        cantera_raiz,
    )
    hallazgo.write_text(content_with_cantera, encoding="utf-8")

    if modo == "audit_only":
        return {
            "estado": "pending",
            "archivo": str(hallazgo),
            "motivo": "AUDIT_ONLY",
            "unit_id": f"{rutas_fuente[0]}::{modulo}",
        }

    is_valid, reason = validate_hallazgo(
        hallazgo,
        repo_root=repo_root,
        require_cantera_raiz=True,
    )
    if not is_valid:
        moved = move_hallazgo_to_blocked(hallazgo, blocked_dir)
        return {
            "estado": "blocked",
            "archivo": str(moved),
            "motivo": f"VALIDACION_BLOCKED: {reason}",
            "unit_id": f"{rutas_fuente[0]}::{modulo}",
        }

    content = hallazgo.read_text(encoding="utf-8")
    estado_meta = _read_estado(content)

    if estado_meta == "done":
        moved = move_hallazgo(hallazgo, done_dir)
        return {
            "estado": "done",
            "archivo": str(moved),
            "motivo": "ESTADO_META_DONE",
            "unit_id": f"{rutas_fuente[0]}::{modulo}",
        }

    moved = move_hallazgo(hallazgo, in_progress_dir)
    return {
        "estado": "in_progress",
        "archivo": str(moved),
        "motivo": "READY_FOR_CODEX",
        "unit_id": f"{rutas_fuente[0]}::{modulo}",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Runner local de factoria SmartPyme")
    parser.add_argument(
        "--modo",
        choices=["audit_only", "execute_ready", "process_pending"],
        required=True,
    )
    parser.add_argument("--modulo", required=False)
    parser.add_argument("--rutas-fuente", nargs="+", required=False)
    parser.add_argument("--repo-destino", required=True)
    parser.add_argument("--model", required=False)
    parser.add_argument("--commit-mode", required=False, default="disabled")
    parser.add_argument("--auditor-timeout-seconds", type=int, required=False)
    args = parser.parse_args()

    try:
        if args.modo == "process_pending":
            result = process_pending_hallazgos(
                pending_dir=PENDING_DIR,
                in_progress_dir=IN_PROGRESS_DIR,
                blocked_dir=BLOCKED_DIR,
                done_dir=DONE_DIR,
                repo_root=BASE_DIR,
            )
            print(json.dumps(result, ensure_ascii=False))
            return 0

        if not args.modulo:
            raise ValueError("MODULO_REQUERIDO: usar --modulo en audit_only/execute_ready.")
        if not args.rutas_fuente:
            raise ValueError(
                "RUTAS_FUENTE_REQUERIDAS: usar --rutas-fuente en audit_only/execute_ready."
            )

        result = run_factory(
            modo=args.modo,
            modulo=args.modulo,
            rutas_fuente=args.rutas_fuente,
            repo_destino=args.repo_destino,
            model=args.model,
            commit_mode=args.commit_mode,
            auditor_timeout_seconds=args.auditor_timeout_seconds,
        )
    except Exception as error:  # fail-closed
        print(str(error))
        return 1

    print(f"estado={result['estado']}")
    print(f"archivo={result['archivo']}")
    print(f"motivo={result['motivo']}")
    if result["estado"] == "blocked":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
