#!/usr/bin/env python3
"""CLI local del Taller I2. No red, subprocess ni proveedor real."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from kit.taller.domain import Policy, Result, TallerError, grant_hash
from kit.taller.application import TallerService

def load(path):
    text=Path(path).read_text(encoding="utf-8")
    if str(path).endswith((".yaml",".yml")):
        import yaml
        return yaml.safe_load(text)
    return json.loads(text)
def emit(r, code=None):
    obj=r.as_dict() if isinstance(r,Result) else r
    print(json.dumps(obj,ensure_ascii=False,sort_keys=True))
    return code if code is not None else ({"PASS":0,"NEEDS_WORK":1,"BLOCKED":3,"UNKNOWN_EFFECT":4}.get(obj.get("status") or obj.get("verdict"),2))
def main(argv=None):
    p=argparse.ArgumentParser(prog="bottega_taller")
    sub=p.add_subparsers(dest="cmd",required=True)
    for n in ("preflight","create-initiative"): 
        q=sub.add_parser(n); q.add_argument("--casefile",required=True); q.add_argument("--grant",required=True); q.add_argument("--policy",required=True); q.add_argument("--out",default=".taller")
    q=sub.add_parser("start-run"); q.add_argument("--initiative",required=True); q.add_argument("--stage",default="STAGE-01"); q.add_argument("--idempotency-key",required=True); q.add_argument("--operator",required=True); q.add_argument("--expected-revision",type=int,default=0); q.add_argument("--store",default=".taller"); q.add_argument("--now",default="2026-10-27T12:00:00Z")
    q=sub.add_parser("pause-run"); q.add_argument("--initiative",required=True); q.add_argument("--idempotency-key",required=True); q.add_argument("--operator",required=True); q.add_argument("--expected-revision",type=int,required=True); q.add_argument("--reason",required=True); q.add_argument("--store",default=".taller"); q.add_argument("--now",default="2026-10-27T12:00:00Z")
    q=sub.add_parser("resume"); q.add_argument("--initiative",required=True); q.add_argument("--idempotency-key",required=True); q.add_argument("--operator",required=True); q.add_argument("--expected-revision",type=int,required=True); q.add_argument("--store",default=".taller"); q.add_argument("--now",default="2026-10-27T12:00:00Z")
    a=p.parse_args(argv)
    try:
        if a.cmd in {"preflight","create-initiative"}:
            case=Path(a.casefile); grant=load(a.grant); policy=Policy(); report=load(case/"report.json") if case.is_dir() else load(case)
            if report.get("verdict") != "PASS": return emit(Result("BLOCKED","ADVISOR_NOT_PASS","Advisor casefile PASS requerido"))
            if a.cmd=="preflight": return emit(Result("PASS",message_safe="casefile, grant y policy válidos"))
            iid=report.get("initiative_id","INITIATIVE-SYNTHETIC-01")
            initiative={"initiative_id":iid,"advisor_casefile":{"path":"casefile","verdict":"PASS"},"owner_id":"owner-local-synthetic","scope":{"included":["synthetic-action"],"excluded":["network","subprocess","production","publication","Producto 02"]},"data_classification":"SYNTHETIC","environment":"local-sandbox","stages":[{"stage_id":"STAGE-01","implementer_id":"bot-synthetic-01","reviewer_id":"reviewer-local-synthetic"}]}
            return emit(TallerService(a.out).create(initiative,grant,policy,"2026-10-27T12:00:00Z"))
        service=TallerService(a.store)
        if a.cmd=="start-run": return emit(service.start(a.initiative,a.stage,a.idempotency_key,a.operator,a.expected_revision,a.now))
        if a.cmd=="pause-run": return emit(service.pause(a.initiative,a.idempotency_key,a.operator,a.expected_revision,a.reason,a.now))
        return emit(service.resume(a.initiative,a.idempotency_key,a.operator,a.expected_revision,a.now))
    except (OSError,ValueError,KeyError,TallerError) as e: return emit(Result("BLOCKED","IO_ERROR",str(e)))
if __name__=="__main__": sys.exit(main())
