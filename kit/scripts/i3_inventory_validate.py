"""Gate de inventario I3: recalcula tamaño y SHA-256 de cada fuente saneada.

Sólo lectura. Verifica que el source-evidence-manifest (autoritativo, fuera del
repo) referencia archivos existentes con tamaño y hash exactos, que no hay
duplicados de source_id, que no hay secretos en la evidencia y que las fuentes
son oficiales. Exit 0 = INVENTORY_PASS; 3 = BLOCKED.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
# Sólo material de credencial real (claves privadas y tokens de proveedores),
# no palabras aisladas como "password"/"token" que aparecen legítimamente en
# licencias, READMEs y descripciones de advisories públicos.
SECRET_RE = re.compile(
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----"
    r"|ghp_[0-9A-Za-z]{20,}"
    r"|github_pat_[0-9A-Za-z_]{20,}"
    r"|AKIA[0-9A-Z]{16}"
    r"|ASIA[0-9A-Z]{16}"
    r"|xox[baprs]-[0-9A-Za-z-]{10,}"
)
DENYLIST = ("erpnext", "erp-next", "hrms", "frappe_hrms")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", type=Path,
                   default=Path("/home/dagalindo/.hermes/profiles/directorit/cache/scratch/bottega-2-increment3/source-evidence-manifest.json"))
    p.add_argument("--evidence-dir", type=Path,
                   default=Path("/home/dagalindo/.hermes/profiles/directorit/cache/scratch/bottega-2-increment3/source-evidence"))
    a = p.parse_args()

    manifest = json.loads(a.manifest.read_text(encoding="utf-8"))
    base = Path(manifest.get("base_directory") or a.evidence_dir).expanduser()
    errors: list[str] = []

    if manifest.get("status") != "INVENTORY_PASS":
        errors.append("manifest status must be INVENTORY_PASS")
    if manifest.get("runtime_gate") != "PASS_FOR_SANDBOX_VALIDATION":
        errors.append("runtime_gate must be PASS_FOR_SANDBOX_VALIDATION")

    seen: set[str] = set()
    for source in manifest.get("sources", []):
        sid = source.get("source_id")
        if sid in seen:
            errors.append(f"{sid}: duplicate source_id")
        seen.add(sid)

        url = str(source.get("url_exact") or "")
        if "latest" in url.lower():
            errors.append(f"{sid}: latest in url")
        if any(token in url.lower() for token in DENYLIST):
            errors.append(f"{sid}: ERPNext/HRMS reference in url")
        if not source.get("officiality_check"):
            errors.append(f"{sid}: missing officiality_check")

        rel = source.get("sanitized_file")
        if not rel:
            errors.append(f"{sid}: missing sanitized_file")
            continue
        # sanitized_file may be "source-evidence/<name>" or bare "<name>"
        name = Path(rel).name
        fp = base / name
        if not fp.is_file():
            errors.append(f"{sid}: evidence file not found: {fp}")
            continue
        rec_size = source.get("size_bytes")
        rec_sha = source.get("sha256")
        actual_size = fp.stat().st_size
        actual_sha = sha256(fp)
        if not isinstance(rec_size, int) or rec_size != actual_size:
            errors.append(f"{sid}: size mismatch (recorded {rec_size}, actual {actual_size})")
        if not (isinstance(rec_sha, str) and SHA256_RE.fullmatch(rec_sha)):
            errors.append(f"{sid}: sha256 must be 64 hex")
        elif rec_sha != actual_sha:
            errors.append(f"{sid}: sha256 mismatch")
        # secret scan on evidence
        try:
            text = fp.read_text(encoding="utf-8", errors="replace")
        except OSError:
            text = ""
        if SECRET_RE.search(text):
            errors.append(f"{sid}: secret-like content in evidence")

    # confirm advisory counts are recorded in sbom (if present)
    sbom_path = a.evidence_dir.parent / "sbom.json"
    if sbom_path.is_file():
        sbom = json.loads(sbom_path.read_text(encoding="utf-8"))
        adv = sbom.get("advisories") or {}
        if not isinstance(adv.get("frappe_advisory_count"), int):
            errors.append("sbom missing frappe_advisory_count")

    status = "INVENTORY_PASS" if not errors else "BLOCKED"
    print(json.dumps({"gate": "INVENTORY", "status": status, "errors": errors}, sort_keys=True))
    return 0 if not errors else 3


if __name__ == "__main__":
    sys.exit(main())
