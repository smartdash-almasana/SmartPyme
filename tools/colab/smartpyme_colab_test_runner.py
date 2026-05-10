"""
SmartPyme Colab Test Runner
===========================
Script reproducible para Google Colab.
Ejecutar celda por celda o como script completo.

Salida: /content/colab_test_report_YYYY-MM-DD.md  (descarga manual)
Sin Drive. Sin secrets. Sin push automático.
"""

import subprocess
import sys
import os
from datetime import datetime

# ---------------------------------------------------------------------------
# CONFIGURACIÓN
# ---------------------------------------------------------------------------

REPO_URL = "https://github.com/smartdash-almasana/SmartPyme.git"
BRANCH = "product/laboratorio-mvp-vendible"
REPO_DIR = "/content/SmartPyme"
REPORT_DIR = "/content"

FOCAL_TESTS = [
    "tests/contracts/test_operational_case_contract.py",
    "tests/repositories/test_operational_case_repository.py",
    "tests/test_mcp_operational_case_bridge.py",
    "tests/contracts/test_operational_claims.py",
    "tests/services/test_operational_interview_engine.py",
]

# ---------------------------------------------------------------------------
# UTILIDADES
# ---------------------------------------------------------------------------

def run(cmd: list[str], cwd: str | None = None) -> tuple[int, str, str]:
    """Ejecuta un comando y devuelve (returncode, stdout, stderr)."""
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout, result.stderr


def section(title: str) -> str:
    bar = "=" * 60
    return f"\n{bar}\n## {title}\n{bar}\n"


# ---------------------------------------------------------------------------
# BLOQUE A — CLONE + CHECKOUT
# ---------------------------------------------------------------------------

def bloque_a_clone() -> dict:
    print(section("BLOQUE A — Clone y checkout"))

    if os.path.exists(REPO_DIR):
        print(f"[INFO] Repo ya existe en {REPO_DIR}. Haciendo pull.")
        rc, out, err = run(["git", "pull"], cwd=REPO_DIR)
    else:
        print(f"[INFO] Clonando {REPO_URL}")
        rc, out, err = run(["git", "clone", REPO_URL, REPO_DIR])

    if rc != 0:
        return {"status": "BLOCKED", "detail": f"clone/pull falló:\n{err}"}

    rc, out, err = run(["git", "checkout", BRANCH], cwd=REPO_DIR)
    if rc != 0:
        return {"status": "BLOCKED", "detail": f"checkout falló:\n{err}"}

    rc, commit_hash, _ = run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO_DIR)
    rc2, branch_out, _ = run(["git", "branch", "--show-current"], cwd=REPO_DIR)

    print(f"[OK] Rama: {branch_out.strip()}  Commit: {commit_hash.strip()}")
    return {
        "status": "OK",
        "commit": commit_hash.strip(),
        "branch": branch_out.strip(),
    }


# ---------------------------------------------------------------------------
# BLOQUE B — INSTALACIÓN
# ---------------------------------------------------------------------------

def bloque_b_install() -> dict:
    print(section("BLOQUE B — Instalación de dependencias"))

    bootstrap = os.path.join(REPO_DIR, "requirements-bootstrap.txt")
    dev = os.path.join(REPO_DIR, "requirements-dev.txt")

    lines = []
    for req_file in [bootstrap, dev]:
        if os.path.exists(req_file):
            print(f"[INFO] Instalando {req_file}")
            rc, out, err = run(
                [sys.executable, "-m", "pip", "install", "-r", req_file, "-q"]
            )
            lines.append(f"pip install {req_file}: rc={rc}")
            if rc != 0:
                lines.append(f"  STDERR: {err[:400]}")
        else:
            lines.append(f"[WARN] No encontrado: {req_file}")

    rc_py, py_ver, _ = run([sys.executable, "--version"])
    print(f"[INFO] Python: {py_ver.strip()}")
    lines.append(f"Python: {py_ver.strip()}")

    return {"status": "OK", "detail": "\n".join(lines)}


# ---------------------------------------------------------------------------
# BLOQUE C — COLECCIÓN
# ---------------------------------------------------------------------------

def bloque_c_collect() -> dict:
    print(section("BLOQUE C — Colección de tests (collect-only)"))

    rc, out, err = run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q"],
        cwd=REPO_DIR,
    )

    combined = out + err
    status = "OK" if rc == 0 else "PARTIAL"
    print(combined[:1000])
    return {"status": status, "output": combined}


# ---------------------------------------------------------------------------
# BLOQUE D — TESTS FOCALES
# ---------------------------------------------------------------------------

def bloque_d_focal() -> dict:
    print(section("BLOQUE D — Tests focales"))

    results = {}
    overall = "PASS"

    for test_path in FOCAL_TESTS:
        full_path = os.path.join(REPO_DIR, test_path)
        if not os.path.exists(full_path):
            results[test_path] = "SKIP — archivo no encontrado"
            overall = "PARTIAL"
            continue

        rc, out, err = run(
            [sys.executable, "-m", "pytest", test_path, "-q", "--tb=short"],
            cwd=REPO_DIR,
        )
        combined = (out + err).strip()
        label = "PASS" if rc == 0 else "FAIL"
        if label == "FAIL" and overall == "PASS":
            overall = "FAIL"
        results[test_path] = f"{label}\n{combined[-600:]}"
        print(f"  [{label}] {test_path}")

    return {"status": overall, "results": results}


# ---------------------------------------------------------------------------
# BLOQUE E — PYTEST GLOBAL
# ---------------------------------------------------------------------------

def bloque_e_global() -> dict:
    print(section("BLOQUE E — pytest global"))

    rc, out, err = run(
        [sys.executable, "-m", "pytest", "tests", "-q", "--tb=no", "--ignore=tests/tmp"],
        cwd=REPO_DIR,
    )
    combined = (out + err).strip()
    status = "PASS" if rc == 0 else "PARTIAL"
    print(combined[-800:])
    return {"status": status, "output": combined}


# ---------------------------------------------------------------------------
# BLOQUE F — GENERAR REPORTE
# ---------------------------------------------------------------------------

def bloque_f_report(
    clone: dict,
    install: dict,
    collect: dict,
    focal: dict,
    global_: dict,
) -> str:
    fecha = datetime.utcnow().strftime("%Y-%m-%d")
    hora = datetime.utcnow().strftime("%H:%M UTC")

    # Clasificación final
    statuses = [clone["status"], collect["status"], focal["status"], global_["status"]]
    if "BLOCKED" in statuses:
        clasificacion = "BLOCKED"
    elif "FAIL" in statuses:
        clasificacion = "FAIL"
    elif "PARTIAL" in statuses:
        clasificacion = "PARTIAL"
    else:
        clasificacion = "PASS"

    lines = [
        f"# Colab Test Report — {fecha}",
        "",
        "## Metadata",
        "",
        f"- fecha: {fecha} {hora}",
        f"- commit: {clone.get('commit', 'N/A')}",
        f"- rama: {clone.get('branch', 'N/A')}",
        f"- python: {sys.version.split()[0]}",
        f"- entorno: Google Colab (efímero)",
        f"- clasificacion: **{clasificacion}**",
        "",
        "---",
        "",
        "## Bloque A — Clone",
        "",
        f"Estado: {clone['status']}",
        clone.get("detail", ""),
        "",
        "## Bloque B — Instalación",
        "",
        install.get("detail", ""),
        "",
        "## Bloque C — Colección",
        "",
        f"Estado: {collect['status']}",
        "```",
        collect.get("output", "")[:1500],
        "```",
        "",
        "## Bloque D — Tests focales",
        "",
        f"Estado global: {focal['status']}",
        "",
    ]

    for path, result in focal.get("results", {}).items():
        lines.append(f"### `{path}`")
        lines.append("```")
        lines.append(result)
        lines.append("```")
        lines.append("")

    lines += [
        "## Bloque E — pytest global",
        "",
        f"Estado: {global_['status']}",
        "```",
        global_.get("output", "")[:2000],
        "```",
        "",
        "---",
        "",
        "## Clasificación final",
        "",
        f"**{clasificacion}**",
        "",
        "## Próximo microciclo",
        "",
        "<!-- completar manualmente -->",
        "",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    print("\n=== SmartPyme Colab Test Runner ===\n")

    clone = bloque_a_clone()
    if clone["status"] == "BLOCKED":
        print(f"[BLOCKED] No se puede continuar: {clone['detail']}")
        sys.exit(1)

    install = bloque_b_install()
    collect = bloque_c_collect()
    focal = bloque_d_focal()
    global_ = bloque_e_global()

    report_md = bloque_f_report(clone, install, collect, focal, global_)

    fecha = datetime.utcnow().strftime("%Y-%m-%d")
    report_path = os.path.join(REPORT_DIR, f"colab_test_report_{fecha}.md")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_md)

    print(section("REPORTE GENERADO"))
    print(f"Archivo: {report_path}")
    print("Descargá el archivo manualmente desde el panel de archivos de Colab.")
    print("\n--- RESUMEN ---")
    print(report_md[:800])


if __name__ == "__main__":
    main()
