"""Deterministic, read-only validators for guardrails/v1."""
from __future__ import annotations
import hashlib, json, os, re
from pathlib import Path
from typing import Any

SHA = re.compile(r"^[0-9a-f]{64}$")
SCHEMA = "guardrails/v1"

def issue(code: str, path: str, value: Any, message: str, severity="error") -> dict[str, Any]:
    safe = value if isinstance(value, (str, int, float, bool)) or value is None else type(value).__name__
    return {"code": code, "severity": severity, "path": path, "safe_value": safe, "message": message}

def report(kind: str, errors: list[dict], warnings=None, observations=None) -> dict[str, Any]:
    warnings = warnings or []; observations = observations or []
    return {"schema_version": SCHEMA, "verdict": "FAIL" if errors else ("WARN" if warnings else "PASS"),
            "exit_code": 1 if errors else 0, "counts": {"errors": len(errors), "warnings": len(warnings)},
            "issues": errors + warnings, "observations": observations, "kind": kind}

def _common(data, errors):
    if not isinstance(data, dict): errors.append(issue("SCHEMA001", "$", data, "object required")); return
    if data.get("schema_version") != SCHEMA: errors.append(issue("SCHEMA002", "schema_version", data.get("schema_version"), "unsupported schema"))
    ref = data.get("evaluated_ref") or data.get("ref_sha")
    if ref is not None and not SHA.fullmatch(str(ref)): errors.append(issue("GATE001", "evaluated_ref", ref, "full SHA-256 required"))

def validate_gate(data: dict, evidence_root: Path | None = None) -> dict:
    errors=[]; warnings=[]; _common(data, errors)
    records=data.get("records", [data] if isinstance(data, dict) and "gate_id" in data else [])
    if not records: errors.append(issue("GATE002", "records", records, "at least one record required"))
    seen=set()
    for i,r in enumerate(records):
        p=f"records[{i}]"
        if not isinstance(r,dict): errors.append(issue("GATE003",p,r,"record must be object")); continue
        rid=r.get("gate_instance_id") or r.get("gate_id")
        if rid in seen: errors.append(issue("GATE014",p+".gate_instance_id",rid,"duplicate gate record"))
        seen.add(rid)
        for key in ("gate_id","scope","status","verdict_kind","ref_sha","issued_at","evidence","evidence_scope","issuer","authorization_granted","prohibited_limits"):
            if key not in r: errors.append(issue("GATE005",p+"."+key,None,"required field missing"))
        if r.get("ref_sha") is not None and not SHA.fullmatch(str(r.get("ref_sha"))): errors.append(issue("GATE001",p+".ref_sha",r.get("ref_sha"),"full SHA-256 required"))
        if r.get("verdict_kind") not in ("verdict","authorization"): errors.append(issue("GATE007",p+".verdict_kind",r.get("verdict_kind"),"invalid kind"))
        status=str(r.get("status", "")); grants=set(r.get("authorization_granted") or []); limits=set(r.get("prohibited_limits") or [])
        if status in {"TECHNICAL_PASS","FIDELITY_PASS"} and grants & {"USER_ACCEPTANCE","RELEASE_READY","PRODUCTION_AUTHORIZED","PUBLICATION_PUBLIC_AUTHORIZED"}:
            errors.append(issue("GATE006",p+".authorization_granted",list(grants),"technical verdict cannot imply authorization"))
        if grants & limits: errors.append(issue("GATE009",p+".authorization_granted",list(grants & limits),"grant conflicts with prohibited limit"))
        if r.get("fallback") not in (None,"none") and not isinstance(r.get("fallback"),dict): errors.append(issue("GATE011",p+".fallback",r.get("fallback"),"fallback must be explicit object"))
        if r.get("ref_relation") is None and r.get("historical") is True: errors.append(issue("GATE004",p+".ref_relation",None,"historical relation required"))
        ev=r.get("evidence") or []
        if not ev: errors.append(issue("GATE016",p+".evidence",ev,"evidence required"))
        if evidence_root:
            for j,e in enumerate(ev):
                path=e.get("path") if isinstance(e,dict) else None
                if not path or Path(path).is_absolute() or ".." in Path(path).parts: errors.append(issue("PATH001",f"{p}.evidence[{j}].path",path,"relative safe path required")); continue
                resolved=(evidence_root / path).resolve()
                if evidence_root.resolve() not in resolved.parents and resolved != evidence_root.resolve(): errors.append(issue("PATH001",f"{p}.evidence[{j}].path",path,"path escapes evidence root"))
                elif not resolved.is_file(): errors.append(issue("GATE016",f"{p}.evidence[{j}].path",path,"evidence not found"))
    return report("gate",errors,warnings)

def validate_traceability(data: dict, evidence_root: Path | None = None, observed_ref: str | None = None) -> dict:
    errors=[]; warnings=[]; _common(data, errors); reqs=data.get("requirements",[]) if isinstance(data,dict) else []
    ids=set(); covered=partial=uncovered=0
    for i,r in enumerate(reqs):
        p=f"requirements[{i}]"; rid=r.get("requirement_id") if isinstance(r,dict) else None
        if rid in ids: errors.append(issue("TRACE004",p+".requirement_id",rid,"duplicate ID"))
        ids.add(rid); tests=r.get("tests",[]) if isinstance(r,dict) else []; ev=r.get("evidence",[]) if isinstance(r,dict) else []
        if not tests: errors.append(issue("TRACE001",p+".tests",tests,"required test missing"))
        if not ev: errors.append(issue("TRACE002",p+".evidence",ev,"evidence missing"))
        if r.get("status") == "stale" or any(isinstance(e,dict) and observed_ref and e.get("evaluated_ref") != observed_ref for e in ev): warnings.append(issue("TRACE003",p,"historical","evidence is stale", "warning")); partial+=1
        elif tests and ev: covered+=1
        else: uncovered+=1
    total=len(reqs); coverage={"required":total,"covered":covered,"partial":partial,"uncovered":uncovered}
    out=report("traceability",errors,warnings); out["coverage"]=coverage; return out

def validate_navigation(data: dict) -> dict:
    errors=[]; warnings=[]; _common(data,errors)
    hosts=set(data.get("allowed_hosts",[])); statuses=set(data.get("allowed_statuses",[]))
    for i,obs in enumerate(data.get("observations", data.get("requests",[]))):
        host=obs.get("host"); status=obs.get("status"); p=f"observations[{i}]"
        if host not in hosts: errors.append(issue("NAV003",p+".host",host,"external host denied"))
        if status not in statuses and not any(k.get("status")==status and k.get("decision_ref") for k in data.get("known_errors",[]) if isinstance(k,dict)):
            errors.append(issue("NAV002",p+".status",status,"status not allowlisted"))
    if data.get("diagnostic_routes_are_not_canonical") and data.get("canonical_start") in data.get("diagnostic_routes",[]): errors.append(issue("NAV001","canonical_start",data.get("canonical_start"),"diagnostic route cannot be canonical"))
    return report("navigation",errors,warnings)

def safe_json(value: Any) -> str: return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
def sha256_payload(value: Any) -> str: return hashlib.sha256(safe_json(value).encode()).hexdigest()
