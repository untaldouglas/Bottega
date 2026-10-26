#!/usr/bin/env python3
"""Create a safe Bottega project scaffold."""
from __future__ import annotations
import argparse, json, re, shutil, subprocess, sys
from pathlib import Path

SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "templates"
FILES = {
    "PROJECT-BRIEF.yaml": TEMPLATES / "PROJECT-BRIEF.yaml",
    "ACCEPTANCE-MANIFEST.yaml": TEMPLATES / "ACCEPTANCE-MANIFEST.yaml",
    "WORKFLOW-STATE.json": TEMPLATES / "WORKFLOW-STATE.json",
    "templates/EVIDENCE-MANIFEST.json": TEMPLATES / "EVIDENCE-MANIFEST.json",
    "REVIEW-PACKET.md": TEMPLATES / "REVIEW-PACKET.md",
    "TEST-SEAMS.yaml": TEMPLATES / "TEST-SEAMS.yaml",
    "gate-record.json": TEMPLATES / "GATE-RECORD.json",
    "traceability.json": TEMPLATES / "TRACEABILITY-MANIFEST.json",
    "authenticated-smoke.json": TEMPLATES / "AUTHENTICATED-SMOKE.json",
    "navigation-smoke.json": TEMPLATES / "NAVIGATION-SMOKE.json",
    "preflight.json": TEMPLATES / "PREFLIGHT-CONFIG.json",
}

def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--target", type=Path, required=True)
    p.add_argument("--product-name", required=True)
    p.add_argument("--slug", required=True)
    p.add_argument("--owner", required=True)
    p.add_argument("--org", default="")
    p.add_argument("--repo-name", default="")
    p.add_argument("--init-git", action="store_true")
    p.add_argument("--create-private-repo", action="store_true")
    p.add_argument("--confirm-private-repo", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    return p.parse_args()

def main():
    a = parse_args()
    if not SLUG.fullmatch(a.slug):
        print("error: --slug debe usar kebab-case (a-z, 0-9 y guiones)", file=sys.stderr)
        return 2
    if a.create_private_repo and not a.confirm_private_repo:
        print("error: crear repo requiere --confirm-private-repo", file=sys.stderr)
        return 2
    if a.create_private_repo and not a.repo_name:
        print("error: crear repo requiere --repo-name proporcionado por el usuario", file=sys.stderr)
        return 2
    target = a.target.expanduser().resolve()
    plan = [f"crear directorio {target}", f"copiar {len(FILES)} plantillas", "crear runs/ y .gitkeep"]
    if a.init_git: plan.append("inicializar git local")
    if a.create_private_repo: plan.append(f"crear repositorio privado {a.org}/{a.repo_name}")
    if a.dry_run:
        print(json.dumps({"dry_run": True, "plan": plan}, ensure_ascii=False, indent=2))
        return 0
    target.mkdir(parents=True, exist_ok=True)
    for name, source in FILES.items():
        text = source.read_text(encoding="utf-8")
        if name == "PROJECT-BRIEF.yaml":
            text = text.replace('"BOTTEGA-EXAMPLE-001"', f'"{a.slug.upper()}-001"')
            text = text.replace('"Producto de ejemplo"', json.dumps(a.product_name, ensure_ascii=False))
            text = text.replace('"producto-de-ejemplo"', a.slug)
            text = text.replace('"Owner por asignar"', json.dumps(a.owner, ensure_ascii=False))
            if a.org: text = text.replace('"organizacion-ejemplo"', json.dumps(a.org))
        destination = target / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(text, encoding="utf-8")
    (target / "runs").mkdir(exist_ok=True)
    (target / "runs" / ".gitkeep").write_text("", encoding="utf-8")
    for name in (".gitignore", ".prettierignore", ".dockerignore"):
        shutil.copy2(ROOT / name, target / name)
    if a.init_git:
        subprocess.run(["git", "init", "--quiet", str(target)], check=True)
    if a.create_private_repo:
        repo_ref = f"{a.org}/{a.repo_name}" if a.org else a.repo_name
        cmd = ["gh", "repo", "create", repo_ref, "--private", "--source", str(target)]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    print(json.dumps({"created": str(target), "private_repo_created": a.create_private_repo}, ensure_ascii=False))
    return 0

if __name__ == "__main__": sys.exit(main())
