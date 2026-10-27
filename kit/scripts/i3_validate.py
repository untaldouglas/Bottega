"""Valida gates I3 sin instalar ni arrancar Frappe."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "docs/increment3/source-evidence-manifest.json"

def validate() -> list[str]:
    errors: list[str] = []
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("status") != "VALIDATED_FOR_REVIEW_ONLY": errors.append("manifest status")
    if manifest.get("runtime_gate") != "BLOCKED_UNTIL_IMAGE_OS_GATE_AND_BENCH_GPL_REVIEW_PASS": errors.append("runtime gate")
    for source in manifest["sources"]:
        if not source["official"] or source["http_status"] != 200: errors.append(source["source_id"] + ": official/status")
        if source["ref"] == "latest": errors.append(source["source_id"] + ": latest")
    for path in (ROOT / "bench-gpl-review").glob("*.json"):
        if json.loads(path.read_text())["decision"] != "BLOCKED": errors.append("GPL gate must remain blocked")
    for path in (ROOT / "image-os-gate").glob("*.json"):
        gate = json.loads(path.read_text())
        if gate["decision"] != "BLOCKED" or gate.get("latest_forbidden") is not True: errors.append("image gate")
    compose = (ROOT / "sandbox/compose.yaml").read_text()
    if "internal: true" not in compose or '127.0.0.1:' not in compose: errors.append("network isolation")
    if '"latest"' in compose or ":latest" in compose: errors.append("latest image")
    return errors

if __name__ == "__main__":
    errors = validate()
    print(json.dumps({"status": "PASS" if not errors else "BLOCKED", "errors": errors}, sort_keys=True))
    raise SystemExit(0 if not errors else 1)
