"""Valida gates I3 (post-PASS humano) sin arrancar Frappe.

Este validador es determinista y sólo lectura: comprueba que el inventario,
el gate GPL y el gate de imagen/OS reflejan el PASS autorizado por Douglas y
que el sandbox mantiene aislamiento. No instala ni arranca nada.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "docs/increment3/source-evidence-manifest.json"
GPL_GATE = ROOT / "bench-gpl-review/candidate-frappe-v16.53.0.json"
IMAGE_GATE = ROOT / "image-os-gate/candidate-frappe-v16.53.0.json"
COMPOSE = ROOT / "sandbox/compose.yaml"
ENV_EXAMPLE = ROOT / "sandbox/.env.example"

ACCEPTED_DIGEST = "sha256:9b629e83e1a517e01eaf7a36362563c0c7f620d3e4747f7dcf79564e290b7b48"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
DENYLIST = ("erpnext", "erp-next", "hrms", "frappe_hrms")


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate() -> list[str]:
    errors: list[str] = []

    # --- Inventario / source-evidence-manifest ---
    manifest = _read_json(MANIFEST)
    if manifest.get("status") != "INVENTORY_PASS":
        errors.append("manifest status must be INVENTORY_PASS")
    if manifest.get("runtime_gate") != "PASS_FOR_SANDBOX_VALIDATION":
        errors.append("manifest runtime_gate must be PASS_FOR_SANDBOX_VALIDATION")
    tuple_ = manifest.get("tuple") or {}
    if tuple_.get("os_image_digest") != ACCEPTED_DIGEST:
        errors.append("manifest tuple os_image_digest mismatch")
    if tuple_.get("architecture") != "linux/amd64":
        errors.append("manifest tuple architecture must be linux/amd64")
    seen = set()
    for source in manifest.get("sources", []):
        sid = source.get("source_id")
        if sid in seen:
            errors.append(f"duplicate source_id {sid}")
        seen.add(sid)
        if not source.get("officiality_check"):
            errors.append(f"{sid}: missing officiality_check")
        if source.get("http_status") != 200:
            errors.append(f"{sid}: http_status must be 200")
        ref = str(source.get("ref") or source.get("url_exact") or "").lower()
        if "latest" in ref:
            errors.append(f"{sid}: latest is forbidden")
        size = source.get("size_bytes")
        if not isinstance(size, int) or size < 0:
            errors.append(f"{sid}: size_bytes must be a non-negative integer")
        sha = source.get("sha256")
        if not (isinstance(sha, str) and SHA256_RE.fullmatch(sha)):
            errors.append(f"{sid}: sha256 must be 64 lowercase hex chars")

    # --- GPL gate ---
    gpl = _read_json(GPL_GATE)
    if gpl.get("decision") != "PASS":
        errors.append("GPL gate decision must be PASS")
    if gpl.get("owner") != "Douglas Galindo":
        errors.append("GPL gate owner must be Douglas Galindo")
    if gpl.get("distribution") != "none":
        errors.append("GPL gate distribution must be none")

    # --- Image/OS gate ---
    image = _read_json(IMAGE_GATE)
    if image.get("decision") != "PASS":
        errors.append("image gate decision must be PASS")
    if image.get("accepted") is not True:
        errors.append("image gate accepted must be true")
    if image.get("digest") != ACCEPTED_DIGEST:
        errors.append("image gate digest mismatch")
    if image.get("architecture") != "linux/amd64":
        errors.append("image gate architecture must be linux/amd64")
    if image.get("latest_forbidden") is not True:
        errors.append("image gate latest_forbidden must be true")

    # --- Sandbox compose ---
    compose = COMPOSE.read_text(encoding="utf-8")
    if "internal: true" not in compose:
        errors.append("network must be internal (no egress)")
    if "127.0.0.1:" not in compose:
        errors.append("HTTP must bind only to 127.0.0.1")
    if compose.count("ports:") != 1:
        errors.append("only the app service may publish a port (DB/cache no host ports)")
    if '":latest"' in compose or ":latest " in compose or ":latest\n" in compose:
        errors.append("compose must not reference latest")
    if "cap_drop" not in compose or "ALL" not in compose:
        errors.append("compose must drop all capabilities")
    if "user:" not in compose:
        errors.append("compose must run non-root user")
    if "@sha256:" not in compose:
        errors.append("compose DB/cache images must be pinned by digest")
    lower = compose.lower()
    if any(token in lower for token in DENYLIST):
        errors.append("compose must not reference ERPNext/HRMS")

    # --- Dockerfile base ---
    dockerfile = (ROOT / "sandbox/Dockerfile").read_text(encoding="utf-8")
    if ACCEPTED_DIGEST not in dockerfile:
        errors.append("Dockerfile must pin the accepted base image digest")

    # --- .env.example ---
    env = ENV_EXAMPLE.read_text(encoding="utf-8")
    if "synthetic" not in env:
        errors.append(".env.example must use synthetic values only")
    lower_env = env.lower()
    if any(token in lower_env for token in DENYLIST):
        errors.append(".env.example must not reference ERPNext/HRMS")

    return errors


if __name__ == "__main__":
    errors = validate()
    print(json.dumps({"status": "PASS" if not errors else "BLOCKED", "errors": errors}, sort_keys=True))
    raise SystemExit(0 if not errors else 1)
