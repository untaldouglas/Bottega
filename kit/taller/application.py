"""Casos de uso Taller con store local JSON append-only simplificado."""
from __future__ import annotations
import json, os
from pathlib import Path
from .domain import Result, TallerError, Policy, verify_grant, sha256_canonical, append_manifest, scan_safe
from .adapters.synthetic import execute

class TallerService:
    def __init__(self, root: str | Path): self.root=Path(root); self.root.mkdir(parents=True, exist_ok=True)
    def _path(self, iid): return self.root / iid / "case.json"
    def _load(self, iid):
        p=self._path(iid)
        if not p.is_file(): raise TallerError("IO_ERROR", "iniciativa no encontrada")
        return json.loads(p.read_text())
    def _save(self, iid, s):
        d=self.root/iid; d.mkdir(parents=True,exist_ok=True); tmp=d/"case.json.tmp"; tmp.write_text(json.dumps(s,ensure_ascii=False,sort_keys=True,indent=2)+"\n"); os.replace(tmp,d/"case.json")
    def create(self, initiative: dict, grant: dict, policy: Policy, now: str) -> Result:
        iid=initiative.get("initiative_id","")
        if not iid or not initiative.get("owner_id") or not initiative.get("scope"): return Result("BLOCKED","SCHEMA_INVALID","owner y scope son obligatorios")
        if initiative.get("data_classification") not in {"SYNTHETIC","SYNTHETIC_FIXTURE"}: return Result("BLOCKED","DATA_CLASSIFICATION_BLOCKED","sólo datos sintéticos")
        findings=scan_safe(initiative)
        if findings: return Result("BLOCKED",findings[0]["code"],"contenido fuera de alcance")
        try: verify_grant(grant,"operator-local-synthetic","create_initiative",f"initiative:{iid}",initiative["data_classification"],"local-sandbox",now)
        except TallerError as e: return Result("BLOCKED",e.code,e.message_safe)
        s={**initiative,"schema_version":"taller-initiative/v1","operator_grant":grant,"policy":{"id":policy.policy_id,"provider":policy.provider,"model":policy.model},"execution_state":"READY","review_state":"NOT_REVIEWED","decisions":{"product":"NOT_ACCEPTED","release":"NOT_READY","publication":"NOT_AUTHORIZED"},"revision":0,"events":[],"manifests":[],"idempotency":{}}
        self._save(iid,s); return Result("PASS",revision=0,data={"initiative_id":iid})
    def start(self, iid: str, stage_id: str, key: str, operator: str, expected: int, now: str) -> Result:
        s=self._load(iid)
        if key in s["idempotency"]:
            old=s["idempotency"][key]; return Result(status=old["status"], error_code=old.get("error_code"), message_safe=old.get("message_safe", ""), revision=old.get("revision", 0), event_refs=old.get("event_refs", []), manifest_ref=old.get("manifest_ref"), idempotent_replay=True, data=old.get("data", {}))
        if len(key)<16: return Result("BLOCKED","SCHEMA_INVALID","idempotency_key inválida")
        if expected != s["revision"]: return Result("BLOCKED","PERSISTENCE_CONFLICT","revision distinta")
        try: verify_grant(s["operator_grant"],operator,"start_run",f"initiative:{iid}",s["data_classification"],"local-sandbox",now)
        except TallerError as e: return Result("BLOCKED",e.code,e.message_safe)
        if s["execution_state"] not in {"READY","PAUSED"}: return Result("BLOCKED","POLICY_BLOCKED","estado no ejecutable")
        out=execute({"capability":"synthetic.action.v1","input":{"fixture":stage_id}})
        payload={"stage_id":stage_id,"artifact":out["artifact"],"sha256":out["sha256"],"classification":"SYNTHETIC"}
        man=append_manifest(s["manifests"][-1] if s["manifests"] else None,payload,len(s["manifests"])+1)
        s["manifests"].append(man); s["execution_state"]="CLOSED"; s["revision"]+=1; ev=f"EVT-{s['revision']:06d}"; s["events"].append({"event_id":ev,"event_type":"RUN_COMPLETED","manifest_ref":man["chain_sha256"]})
        r=Result("PASS",revision=s["revision"],event_refs=[ev],manifest_ref=man["chain_sha256"],data={"artifact":out["artifact"],"counters":{"delivery_attempt":1,"provider_retry":0,"validation_attempt":1,"operational_cleanup":0}})
        s["idempotency"][key]=r.as_dict(); self._save(iid,s); return r
    def pause(self,iid,key,operator,expected,reason,now):
        s=self._load(iid)
        if expected!=s["revision"]: return Result("BLOCKED","PERSISTENCE_CONFLICT","revision distinta")
        try: verify_grant(s["operator_grant"],operator,"pause_run",f"initiative:{iid}",s["data_classification"],"local-sandbox",now)
        except TallerError as e: return Result("BLOCKED",e.code,e.message_safe)
        s["execution_state"]="PAUSED"; s["revision"]+=1; s["events"].append({"event_id":f"EVT-{s['revision']:06d}","event_type":"RUN_PAUSED","reason":reason}); self._save(iid,s); return Result("PASS",revision=s["revision"])
    def resume(self,iid,key,operator,expected,now):
        s=self._load(iid)
        if expected!=s["revision"]: return Result("BLOCKED","PERSISTENCE_CONFLICT","revision distinta")
        try: verify_grant(s["operator_grant"],operator,"resume_run",f"initiative:{iid}",s["data_classification"],"local-sandbox",now)
        except TallerError as e: return Result("BLOCKED",e.code,e.message_safe)
        if s["execution_state"]=="CLOSED": return Result("PASS",revision=s["revision"],idempotent_replay=True,message_safe="acción ya confirmada")
        s["execution_state"]="READY"; self._save(iid,s); return self.start(iid,"STAGE-01",key,operator,s["revision"],now)
