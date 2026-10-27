"""Auditor determinista, read-only y fail-closed para expedientes I2."""
from __future__ import annotations
from kit.taller.domain import TallerError, grant_hash, scan_safe, sha256_canonical, verify_manifest_chain

CA_IDS = ["CA-002", *[f"CA-{n:03d}" for n in range(4, 12)], *[f"CA-{n:03d}" for n in range(16, 21)]]

def audit(snapshot: dict, reviewer_id: str) -> dict:
    checks = []
    implementers = {s.get("implementer_id") for s in snapshot.get("stages", []) if isinstance(s, dict) and s.get("implementer_id")}
    findings = scan_safe(snapshot)
    classification_ok = snapshot.get("classification") in {"SYNTHETIC", "SYNTHETIC_FIXTURE"}
    checks.append({"id":"CA-002","status":"PASS" if snapshot.get("owner_id") and snapshot.get("scope") and classification_ok else "BLOCKED","reason":"brief, clasificación y scope"})
    stages_ok = snapshot.get("stages") and all(isinstance(s, dict) and "dependencies" in s and "gate" in s for s in snapshot["stages"])
    checks.append({"id":"CA-004","status":"PASS" if stages_ok else "BLOCKED","reason":"dependencias y gates"})
    checks.append({"id":"CA-005","status":"PASS" if snapshot.get("manifests") else "NEEDS_WORK","reason":"trazabilidad"})
    checks.append({"id":"CA-006","status":"BLOCKED" if not reviewer_id or reviewer_id in implementers else "PASS","reason":"independencia"})
    decisions = snapshot.get("decisions", {})
    checks.append({"id":"CA-007","status":"PASS" if set(("product", "release", "publication")) <= decisions.keys() else "BLOCKED","reason":"decisiones separadas"})
    checks.append({"id":"CA-008","status":"PASS" if decisions.get("publication") == "NOT_AUTHORIZED" else "BLOCKED","reason":"autorización humana"})
    policy = snapshot.get("policy", {})
    checks.append({"id":"CA-009","status":"PASS" if policy.get("fallback") in {"none", "authorized"} and policy.get("network") == "deny-all" and policy.get("subprocess") == "deny-all" else "BLOCKED","reason":"política de proveedor"})
    counters = snapshot.get("counters", {})
    checks.append({"id":"CA-010","status":"PASS" if snapshot.get("manifests") else "NEEDS_WORK","reason":"manifiestos"})
    checks.append({"id":"CA-011","status":"PASS" if all(k in counters for k in ("delivery_attempt", "provider_retry", "validation_attempt", "operational_cleanup")) else "BLOCKED","reason":"contadores separados"})
    checks.append({"id":"CA-012","status":"BLOCKED" if findings else "PASS","reason":"scan recursivo"})
    checks.append({"id":"CA-016","status":"PASS" if snapshot.get("review_state") in {"NOT_REVIEWED", "REVIEWED"} else "BLOCKED","reason":"retrospectiva separada"})
    checks.append({"id":"CA-017","status":"PASS" if snapshot.get("execution_state") in {"READY", "PAUSED", "CLOSED"} else "BLOCKED","reason":"reanudación"})
    grant = snapshot.get("operator_grant")
    grant_ok = isinstance(grant, dict) and grant.get("grant_sha256") == grant_hash(grant) and grant.get("operator_id") and grant.get("operations") and grant.get("resource_scope")
    checks.append({"id":"CA-018","status":"PASS" if grant_ok else "BLOCKED","reason":"grant válido y expediente"})
    packet = snapshot.get("review_packet", {})
    checks.append({"id":"CA-019","status":"PASS" if all(packet.get(k) for k in ("Summary", "Evidence", "Merge Danger")) else "BLOCKED","reason":"paquete de revisión"})
    checks.append({"id":"CA-020","status":"PASS" if decisions.get("publication") != "AUTHORIZED" else "BLOCKED","reason":"no autorización implícita"})
    ledger = snapshot.get("provider_ledger")
    ledger_fields = {"requested_provider", "requested_model", "effective_provider", "effective_model", "selection_reason", "fallback", "network", "subprocess", "cost"}
    ledger_ok = isinstance(ledger, list) and bool(ledger)
    for entry in ledger or []:
        ledger_ok = ledger_ok and isinstance(entry, dict) and ledger_fields <= entry.keys()
        if isinstance(entry, dict):
            cost = entry.get("cost", {})
            ledger_ok = ledger_ok and isinstance(cost, dict) and {"class", "amount"} <= cost.keys()
            ledger_ok = ledger_ok and entry.get("requested_provider") == policy.get("provider") and entry.get("requested_model") == policy.get("model")
            ledger_ok = ledger_ok and entry.get("fallback") in {"none", "authorized"}
            if entry.get("fallback") == "none":
                ledger_ok = ledger_ok and entry.get("effective_provider") == policy.get("provider") and entry.get("effective_model") == policy.get("model")
    checks.append({"id":"CA-009-LEDGER","status":"PASS" if ledger_ok else "BLOCKED","reason":"provider_ledger completo y consistente"})
    try:
        verify_manifest_chain(snapshot.get("manifests", []), snapshot.get("events", [])); chain_ok = True
    except (TallerError, TypeError): chain_ok = False
    refs = {m.get("chain_sha256") for m in snapshot.get("manifests", []) if isinstance(m, dict)}
    required_ref_events = {"RUN_COMPLETED"}
    if any((e.get("event_type") in required_ref_events and not e.get("manifest_ref")) or (e.get("manifest_ref") not in refs) for e in snapshot.get("events", []) if isinstance(e, dict)): chain_ok = False
    if not chain_ok:
        for c in checks:
            if c["id"] in {"CA-005", "CA-010", "CA-017", "CA-018"}: c["status"] = "BLOCKED"
    blocked = (["grant"] if not grant_ok else []) + (["scan"] if findings else []) + (["manifest-chain"] if not chain_ok else []) + (["provider-ledger"] if not ledger_ok else [])
    verdict = "BLOCKED" if any(c["status"] == "BLOCKED" for c in checks) else ("NEEDS_WORK" if any(c["status"] == "NEEDS_WORK" for c in checks) else "PASS")
    return {"schema_version":"taller-audit/v1","audit_id":"AUDIT-"+sha256_canonical(snapshot)[:10].upper(),"initiative_id":snapshot.get("initiative_id"),"snapshot_sha256":"sha256:"+sha256_canonical(snapshot),"reviewer_id":reviewer_id,"implementer_ids":sorted(x for x in implementers if isinstance(x, str)),"verdict":verdict,"checks":checks,"product_decision":decisions.get("product","NOT_ACCEPTED"),"release_decision":decisions.get("release","NOT_READY"),"publication_decision":decisions.get("publication","NOT_AUTHORIZED"),"findings":blocked}
