"""Adaptador único I2: función local, determinista y no billable."""
from __future__ import annotations
from ..domain import TallerError, canonical_json, sha256_bytes


class SyntheticProvider:
    """Proveedor falso determinista: nunca usa red ni subprocess."""

    def __init__(self, statuses: list[int] | None = None):
        self.statuses = list(statuses or [200])
        self.calls = 0

    def execute(self, request: dict) -> dict:
        self.calls += 1
        status = self.statuses.pop(0) if self.statuses else 200
        if status == 429:
            return {"status_code": 429, "effective_provider": "synthetic-local",
                    "effective_model": "synthetic-action-v1", "cost_amount": 0}
        if status != 200:
            raise TallerError("PROVIDER_ERROR", "proveedor sintético rechazó el intento")
        return execute(request)

def execute(request: dict) -> dict:
    if request.get("capability") != "synthetic.action.v1": raise TallerError("POLICY_BLOCKED", "capability no permitida")
    if any(k in request for k in ("url", "command", "shell", "secret", "token")): raise TallerError("OUT_OF_SCOPE", "payload no permitido")
    payload = {"schema_version":"synthetic-artifact/v1", "fixture":request.get("input", {}).get("fixture", "FIXTURE-DEFAULT"), "result":"synthetic-pass", "classification":"SYNTHETIC"}
    raw = canonical_json(payload).encode()
    return {"artifact":payload, "sha256":"sha256:" + sha256_bytes(raw), "size_bytes":len(raw), "mime":"application/json", "effective_provider":"synthetic-local", "effective_model":"synthetic-action-v1", "cost_class":"SYNTHETIC_NON_BILLABLE", "cost_amount":0, "fallback":"none"}
