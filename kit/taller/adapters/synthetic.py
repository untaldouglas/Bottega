"""Adaptador único I2: función local, determinista y no billable."""
from __future__ import annotations
from ..domain import TallerError, canonical_json, sha256_bytes

def execute(request: dict) -> dict:
    if request.get("capability") != "synthetic.action.v1": raise TallerError("POLICY_BLOCKED", "capability no permitida")
    if any(k in request for k in ("url", "command", "shell", "secret", "token")): raise TallerError("OUT_OF_SCOPE", "payload no permitido")
    payload = {"schema_version":"synthetic-artifact/v1", "fixture":request.get("input", {}).get("fixture", "FIXTURE-DEFAULT"), "result":"synthetic-pass", "classification":"SYNTHETIC"}
    raw = canonical_json(payload).encode()
    return {"artifact":payload, "sha256":"sha256:" + sha256_bytes(raw), "size_bytes":len(raw), "mime":"application/json", "effective_provider":"synthetic-local", "effective_model":"synthetic-action-v1", "cost_class":"SYNTHETIC_NON_BILLABLE", "cost_amount":0, "fallback":"none"}
