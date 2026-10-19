#!/usr/bin/env python3
"""Validate Bottega gates, manifests, hashes and workflow coherence."""
from __future__ import annotations
import argparse, hashlib, json, re, sys
from pathlib import Path
STATES={"draft","preflight","in_progress","validation","blocked","accepted","closed"}
COUNTERS={"delivery_attempt","provider_retry","validation_attempt","operational_cleanup"}

def yaml_value(text, key):
    m=re.search(rf"^\s*{re.escape(key)}:\s*[\"']?([^\"'\n]+)", text, re.M)
    return m.group(1).strip() if m else None

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project",type=Path,required=True)
    p.add_argument("--format",choices=("json","markdown"),default="json")
    p.add_argument("--dry-run",action="store_true")
    a=p.parse_args(); root=a.project.resolve(); errors=[]; checks=[]
    for name in ("PROJECT-BRIEF.yaml","ACCEPTANCE-MANIFEST.yaml","WORKFLOW-STATE.json"):
        ok=(root/name).is_file(); checks.append({"check":name,"ok":ok})
        if not ok: errors.append(f"falta {name}")
    state={}
    if not errors:
        try: state=json.loads((root/"WORKFLOW-STATE.json").read_text())
        except (OSError,json.JSONDecodeError) as e: errors.append(f"estado inválido: {type(e).__name__}")
    if state:
        if state.get("state") not in STATES: errors.append("state no pertenece al conjunto tipado")
        if set(state.get("counters",{})) != COUNTERS: errors.append("contadores separados incompletos")
        if state.get("circuit_breaker",{}).get("first_429_opens") is not True: errors.append("política 429 ausente")
    manifest=root/"ACCEPTANCE-MANIFEST.yaml"
    if manifest.is_file() and "requirements:" not in manifest.read_text(): errors.append("manifiesto sin requirements")
    runs=root/"runs"
    evidence_count=0
    if runs.is_dir():
        for f in runs.glob("*/attempts/*/manifest.json"):
            evidence_count+=1
            try:
                data=json.loads(f.read_text()); declared=data.get("sha256","")
                payload=data.get("payload")
                if payload is not None and declared != hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",", ":")).encode()).hexdigest(): errors.append(f"hash inválido: {f}")
            except (OSError,json.JSONDecodeError): errors.append(f"evidencia inválida: {f}")
    result={"project":str(root),"dry_run":a.dry_run,"checks":checks,"evidence_manifests":evidence_count,"errors":errors,"ok":not errors}
    if a.format=="markdown": print("# Gate check\n\n"+"\n".join(f"- {k}: {v}" for k,v in result.items()))
    else: print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if not errors else 1
if __name__=="__main__": sys.exit(main())
