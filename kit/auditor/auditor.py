"""Auditor determinista y read-only."""
from __future__ import annotations
from kit.taller.domain import sha256_canonical, scan_safe

def audit(snapshot: dict, reviewer_id: str) -> dict:
    implementers={s.get("implementer_id") for s in snapshot.get("stages",[]) if s.get("implementer_id")}
    checks=[]
    checks.append({"id":"CA-002","status":"PASS" if snapshot.get("owner_id") and snapshot.get("scope") else "BLOCKED","reason":"owner/scope"})
    checks.append({"id":"CA-006","status":"BLOCKED" if reviewer_id in implementers else "PASS","reason":"independencia"})
    checks.append({"id":"CA-008","status":"PASS" if snapshot.get("decisions",{}).get("publication")=="NOT_AUTHORIZED" else "BLOCKED","reason":"decisiones separadas"})
    checks.append({"id":"CA-010","status":"PASS" if snapshot.get("manifests",[]) else "NEEDS_WORK","reason":"manifiesto"})
    findings=scan_safe(snapshot)
    if findings: checks.append({"id":"CA-012","status":"BLOCKED","reason":"scan limpio requerido"})
    verdict="BLOCKED" if any(c["status"]=="BLOCKED" for c in checks) else ("NEEDS_WORK" if any(c["status"]=="NEEDS_WORK" for c in checks) else "PASS")
    return {"schema_version":"taller-audit/v1","audit_id":"AUDIT-"+sha256_canonical(snapshot)[:10].upper(),"initiative_id":snapshot.get("initiative_id"),"snapshot_sha256":"sha256:"+sha256_canonical(snapshot),"reviewer_id":reviewer_id,"implementer_ids":sorted(implementers),"verdict":verdict,"checks":checks,"product_decision":snapshot.get("decisions",{}).get("product","NOT_ACCEPTED"),"release_decision":snapshot.get("decisions",{}).get("release","NOT_READY"),"publication_decision":"NOT_AUTHORIZED"}
