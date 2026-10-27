"""Reglas puras I2: fail-closed, hashes, límites y estados ortogonales."""
from __future__ import annotations
import hashlib, json, re
from dataclasses import dataclass, field
from typing import Any

LIMITS = {"max_stages": 3, "max_artifacts_stage": 5, "max_artifacts_initiative": 12, "max_delivery_attempts": 2, "max_validation_attempts": 2, "max_duration_seconds": 300, "max_artifact_bytes": 65536}
FORBIDDEN = re.compile(r"(?i)(producto\s*02|frappe|producci[oó]n|publicaci[oó]n|release|merge|secret|token|password|/home/|\.env|\.ssh)")

class TallerError(Exception):
    def __init__(self, code: str, message: str = "condición bloqueada"):
        super().__init__(message); self.code = code; self.message_safe = message

def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"

def sha256_bytes(data: bytes) -> str: return hashlib.sha256(data).hexdigest()
def sha256_canonical(value: Any) -> str: return sha256_bytes(canonical_json(value).encode())

def scan_safe(value: Any, path: str = "$", findings: list[dict] | None = None) -> list[dict]:
    findings = findings if findings is not None else []
    if isinstance(value, dict):
        for k, v in value.items(): scan_safe(v, f"{path}.{k}", findings)
    elif isinstance(value, list):
        for i, v in enumerate(value): scan_safe(v, f"{path}[{i}]", findings)
    elif isinstance(value, str) and FORBIDDEN.search(value):
        findings.append({"code": "OUT_OF_SCOPE", "path": path, "message": "contenido fuera de alcance o sensible"})
    return findings

def grant_hash(grant: dict) -> str:
    body = {k: v for k, v in grant.items() if k not in {"grant_sha256", "signature_or_hash"}}
    return "sha256:" + sha256_canonical(body)

def verify_grant(grant: dict | None, operator_id: str, operation: str, scope: str, classification: str, environment: str, now: str) -> None:
    if not grant: raise TallerError("AUTHZ_MISSING", "grant explícito requerido")
    required = ("grant_id", "operator_id", "operations", "resource_scope", "data_classification", "environment", "expires_at")
    if any(not grant.get(k) for k in required): raise TallerError("AUTHZ_AMBIGUOUS", "grant incompleto")
    if grant.get("operator_id") != operator_id or operator_id in {"", "*"}: raise TallerError("AUTHZ_AMBIGUOUS", "operador no coincide")
    if operation not in grant["operations"] or scope not in grant["resource_scope"]: raise TallerError("SCOPE_BLOCKED", "operación o scope no autorizado")
    if classification not in grant["data_classification"] or grant.get("environment") != environment: raise TallerError("AUTHZ_AMBIGUOUS", "clasificación o entorno no autorizado")
    if grant.get("revoked_at") is not None or now >= grant["expires_at"]: raise TallerError("AUTHZ_REVOKED_OR_EXPIRED", "grant expirado o revocado")
    expected = grant_hash(grant)
    supplied = grant.get("grant_sha256") or grant.get("signature_or_hash")
    if supplied != expected: raise TallerError("HASH_MISMATCH", "hash de grant inválido")

@dataclass(frozen=True)
class Policy:
    policy_id: str = "taller-i2-v1"
    provider: str = "synthetic-local"
    model: str = "synthetic-action-v1"
    fallback: str = "none"
    network: str = "deny-all"
    subprocess: str = "deny-all"
    limits: dict[str, int] = field(default_factory=lambda: dict(LIMITS))

@dataclass
class Result:
    status: str
    error_code: str | None = None
    message_safe: str = ""
    revision: int = 0
    event_refs: list[str] = field(default_factory=list)
    manifest_ref: str | None = None
    idempotent_replay: bool = False
    effective_provider: str = "synthetic-local"
    effective_model: str = "synthetic-action-v1"
    data: dict[str, Any] = field(default_factory=dict)
    def as_dict(self) -> dict[str, Any]:
        return {"schema_version":"taller-result/v1", "status":self.status, "error_code":self.error_code, "message_safe":self.message_safe, "revision":self.revision, "event_refs":self.event_refs, "manifest_ref":self.manifest_ref, "idempotent_replay":self.idempotent_replay, "effective_provider":self.effective_provider, "effective_model":self.effective_model, **self.data}

def append_manifest(previous: dict | None, payload: dict, sequence: int) -> dict:
    prev = previous.get("chain_sha256") if previous else None
    body = {"schema_version":"evidence-manifest/v1", "sequence_no":sequence, "payload":payload, "previous_manifest_sha256":prev}
    body["payload_sha256"] = "sha256:" + sha256_canonical(payload)
    body["chain_sha256"] = "sha256:" + sha256_canonical(body)
    body["immutable"] = True
    return body
