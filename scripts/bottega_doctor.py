#!/usr/bin/env python3
"""Valida que Bottega esté listo para usarse (solo lectura, idempotente).

Comprueba los prerrequisitos externos del método: herramientas de plataforma,
el plugin `mattpocock-skills` en Hermes y los seis perfiles (Bots). No muta
nada: emite PASS/FAIL/WARN y el comando exacto para corregir cada fallo.

Uso:
  python3 scripts/bottega_doctor.py              # informe legible
  python3 scripts/bottega_doctor.py --bootstrap  # informe + checklist ordenado
  python3 scripts/bottega_doctor.py --format json
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys

# Perfiles canónicos del método (un Bot por etapa).
BOTTEGA_PROFILES = [
    ("andrea-verrocchio", "Andrea del Verrocchio · requisitos y FRD"),
    ("leonardo-da-vinci", "Leonardo da Vinci · alternativas y solución"),
    ("donatello-ux", "Donatello · UX y diseño de producto"),
    ("filippo-brunelleschi", "Filippo Brunelleschi · arquitectura técnica"),
    ("michelangelo-buonarroti", "Michelangelo Buonarroti · implementación y TDD"),
    ("raffaello-sanzio", "Raffaello Sanzio · revisión independiente"),
]
PLUGIN = "mattpocock-skills"
REQUIRED_TOOLS = ["python3", "git", "hermes"]
OPTIONAL_TOOLS = ["node", "npm", "docker", "gh"]


def which(name: str) -> bool:
    return shutil.which(name) is not None


def run(cmd, timeout=20):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.SubprocessError):
        return None


def hermes_available() -> bool:
    return which("hermes")


def plugin_state():
    r = run(["hermes", "plugins", "list", "--plain", "--no-bundled"])
    if r is None or r.returncode != 0:
        return "unknown"
    for line in r.stdout.splitlines():
        parts = line.split()
        if parts and parts[-1] == PLUGIN:
            return parts[0]  # enabled / disabled / not enabled
    return "missing"


def profile_info(slug):
    r = run(["hermes", "profile", "show", slug])
    if r is None or r.returncode != 0:
        return None
    model = None
    for line in r.stdout.splitlines():
        if line.startswith("Model:"):
            model = line.split(":", 1)[1].strip()
    return model


def collect():
    checks = []
    for tool in REQUIRED_TOOLS:
        ok = which(tool)
        checks.append({
            "id": f"tool:{tool}",
            "status": "pass" if ok else "fail",
            "detail": f"herramienta {tool}",
            "fix": None if ok else f"instala {tool} antes de continuar",
        })
    for tool in OPTIONAL_TOOLS:
        ok = which(tool)
        checks.append({
            "id": f"tool:{tool}",
            "status": "pass" if ok else "warn",
            "detail": f"herramienta opcional {tool}",
            "fix": None if ok else f"{tool} solo se necesita para construir productos (app01, docker, PRs)",
        })

    if hermes_available():
        state = plugin_state()
        if state == "enabled":
            checks.append({"id": "plugin", "status": "pass",
                           "detail": f"plugin {PLUGIN} instalado y habilitado", "fix": None})
        elif state in ("disabled", "not enabled"):
            checks.append({"id": "plugin", "status": "fail",
                           "detail": f"plugin {PLUGIN} instalado pero no habilitado",
                           "fix": f"hermes plugins enable {PLUGIN}"})
        elif state == "missing":
            checks.append({"id": "plugin", "status": "fail",
                           "detail": f"plugin {PLUGIN} no instalado",
                           "fix": f"hermes plugins install --enable mattpocock/skills"})
        else:
            checks.append({"id": "plugin", "status": "fail",
                           "detail": f"no se pudo consultar el plugin {PLUGIN}",
                           "fix": "revisa `hermes plugins list`"})
    else:
        checks.append({"id": "plugin", "status": "fail",
                       "detail": f"plugin {PLUGIN} (no verificado: hermes no disponible)",
                       "fix": "instala Hermes primero"})

    for slug, desc in BOTTEGA_PROFILES:
        if not hermes_available():
            checks.append({"id": f"profile:{slug}", "status": "fail",
                           "detail": f"perfil {slug} ({desc}) — no verificado",
                           "fix": "instala Hermes primero"})
            continue
        model = profile_info(slug)
        if model is None:
            checks.append({"id": f"profile:{slug}", "status": "fail",
                           "detail": f"perfil {slug} ({desc})",
                           "fix": f"hermes profile create {slug} --clone-from default --description 'Bottega · {desc}'"})
        elif model in ("", "auto", "—", "-"):
            checks.append({"id": f"profile:{slug}", "status": "warn",
                           "detail": f"perfil {slug} ({desc}) sin modelo explícito",
                           "fix": f"hermes -p {slug} model"})
        else:
            checks.append({"id": f"profile:{slug}", "status": "pass",
                           "detail": f"perfil {slug} ({desc}) — {model}", "fix": None})
    return checks


def render_human(checks):
    marks = {"pass": "PASS", "fail": "FAIL", "warn": "WARN"}
    for c in checks:
        print(f"[{marks[c['status']]}] {c['detail']}")
        if c.get("fix"):
            print(f"      → {c['fix']}")
    fails = [c for c in checks if c["status"] == "fail"]
    warns = [c for c in checks if c["status"] == "warn"]
    print()
    if fails:
        print(f"Resumen: {len(fails)} fallo(s), {len(warns)} advertencia(s) — Bottega NO está listo.")
        print("\nPara corregir:")
        for c in fails:
            print(f"  · {c['fix']}")
    else:
        print(f"Resumen: Bottega listo ({len(warns)} advertencia(s) opcionales).")


def bootstrap_checklist(checks):
    """Checklist ordenado de instalación, con estado y comando exacto."""
    by_id = {c["id"]: c for c in checks}
    print("\nInstalación ordenada (de cero a listo):\n")

    def step(done_id, label, command):
        c = by_id.get(done_id)
        state = "✓ listo" if (c and c["status"] == "pass") else "→ pendiente"
        print(f"{state}  {label}")
        if not (c and c["status"] == "pass"):
            print(f"      {command}")

    step("tool:hermes", "1. Hermes Agent (orquestador)",
         "curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash")
    step("plugin", "2. Skills de Matt Pocock (plugin)",
         f"hermes plugins install --enable mattpocock/skills")
    for slug, desc in BOTTEGA_PROFILES:
        step(f"profile:{slug}", f"3. Perfil {slug} ({desc})",
             f"hermes profile create {slug} --clone-from default --description 'Bottega · {desc}'")
    print("  4. Configura modelo/provider por perfil: hermes -p <perfil> model")
    print("  5. Verifica con: make doctor")
    print("\nLos pasos de creación de perfiles requieren decisión humana (qué modelo/provider usa cada Bot).")


def main(argv=None):
    p = argparse.ArgumentParser(description="Valida que Bottega esté listo (solo lectura).")
    p.add_argument("--bootstrap", action="store_true", help="imprime además el checklist ordenado de instalación")
    p.add_argument("--format", choices=("human", "json"), default="human")
    args = p.parse_args(argv)
    checks = collect()
    ready = all(c["status"] != "fail" for c in checks)
    if args.format == "json":
        summary = {"pass": sum(c["status"] == "pass" for c in checks),
                   "fail": sum(c["status"] == "fail" for c in checks),
                   "warn": sum(c["status"] == "warn" for c in checks)}
        print(json.dumps({"ready": ready, "summary": summary, "checks": checks},
                         ensure_ascii=False, indent=2))
    else:
        render_human(checks)
        if args.bootstrap:
            bootstrap_checklist(checks)
    return 0 if ready else 1


if __name__ == "__main__":
    sys.exit(main())
