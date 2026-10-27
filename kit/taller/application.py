"""Casos de uso Taller con store local JSON append-only simplificado."""
from __future__ import annotations
import json, os
from pathlib import Path
from .domain import Result, TallerError, Policy, verify_grant, append_manifest, scan_safe, verify_manifest_chain
from .adapters.synthetic import SyntheticProvider

class TallerService:
    def __init__(self, root: str | Path, provider=None):
        self.root=Path(root); self.root.mkdir(parents=True, exist_ok=True)
        self.provider = provider or SyntheticProvider()
    def _path(self, iid): return self.root / iid / "case.json"
    def _manifest_path(self, iid): return self.root / iid / "manifests.ndjson"
    def _load(self, iid):
        p=self._path(iid)
        if not p.is_file(): raise TallerError("IO_ERROR", "iniciativa no encontrada")
        s = json.loads(p.read_text())
        persisted = []
        mp = self._manifest_path(iid)
        if mp.exists():
            for line in mp.read_text(encoding="utf-8").splitlines():
                if not line: raise TallerError("HASH_MISMATCH", "manifiesto truncado")
                try: persisted.append(json.loads(line))
                except json.JSONDecodeError: raise TallerError("HASH_MISMATCH", "manifiesto ilegible")
        if persisted != s.get("manifests", []): raise TallerError("HASH_MISMATCH", "histórico de manifiestos no coincide")
        verify_manifest_chain(persisted, s.get("events", [])); return s
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
        s={**initiative,"schema_version":"taller-initiative/v1","operator_grant":grant,"classification":"SYNTHETIC","policy":{"id":policy.policy_id,"provider":policy.provider,"model":policy.model,"fallback":policy.fallback,"network":policy.network,"subprocess":policy.subprocess},"execution_state":"READY","circuit_state":"CLOSED","review_state":"NOT_REVIEWED","decisions":{"product":"NOT_ACCEPTED","release":"NOT_READY","publication":"NOT_AUTHORIZED"},"stages":[{"stage_id":"STAGE-01","dependencies":[],"gate":{"status":"APPROVED","evidence":"synthetic-grant"},"implementer_id":"operator-local-synthetic"}],"counters":{"delivery_attempt":0,"provider_retry":0,"validation_attempt":0,"operational_cleanup":0},"provider_ledger":[],"review_packet":{"Summary":"synthetic local run","Evidence":"manifests and event chain","Merge Danger":"none"},"revision":0,"events":[],"manifests":[],"idempotency":{}}
        self._save(iid,s); self._manifest_path(iid).touch(); return Result("PASS",revision=0,data={"initiative_id":iid})
    def start(self, iid: str, stage_id: str, key: str, operator: str, expected: int, now: str, execution_hook=None) -> Result:
        s=self._load(iid)
        if key in s["idempotency"]:
            old=s["idempotency"][key]; return Result(status=old["status"], error_code=old.get("error_code"), message_safe=old.get("message_safe", ""), revision=old.get("revision", 0), event_refs=old.get("event_refs", []), manifest_ref=old.get("manifest_ref"), idempotent_replay=True, data=old.get("data", {}))
        if len(key)<16: return Result("BLOCKED","SCHEMA_INVALID","idempotency_key inválida")
        if expected != s["revision"]: return Result("BLOCKED","PERSISTENCE_CONFLICT","revision distinta")
        try: verify_grant(s["operator_grant"],operator,"start_run",f"initiative:{iid}",s["data_classification"],"local-sandbox",now)
        except TallerError as e: return Result("BLOCKED",e.code,e.message_safe)
        if s["execution_state"] not in {"READY","PAUSED"}: return Result("BLOCKED","POLICY_BLOCKED","estado no ejecutable")
        if s.get("circuit_state", "CLOSED") == "OPEN": return Result("BLOCKED","CIRCUIT_OPEN","circuito de proveedor abierto")
        s["execution_state"]="RUNNING"; s["revision"]+=1
        started=f"EVT-{s['revision']:06d}"; s["events"].append({"event_id":started,"event_type":"RUN_STARTED"})
        self._save(iid,s)
        if execution_hook is not None: execution_hook(self, iid)
        s=self._load(iid)
        if s["execution_state"] == "PAUSED": return Result("BLOCKED","INTERRUPTED", "ejecución pausada", revision=s["revision"])
        out=self.provider.execute({"capability":"synthetic.action.v1","input":{"fixture":stage_id}})
        ledger={"requested_provider":s["policy"]["provider"],"requested_model":s["policy"]["model"],"effective_provider":out.get("effective_provider","synthetic-local"),"effective_model":out.get("effective_model","synthetic-action-v1"),"selection_reason":"primary","fallback":"none","network":"deny-all","subprocess":"deny-all","cost":{"class":"SYNTHETIC_NON_BILLABLE","amount":out.get("cost_amount",0)}}
        s["provider_ledger"].append(ledger)
        if out.get("status_code") == 429:
            s["circuit_state"]="OPEN"; s["execution_state"]="PAUSED"; s["counters"]["provider_retry"]+=1; s["revision"]+=1
            ev=f"EVT-{s['revision']:06d}"; s["events"].append({"event_id":ev,"event_type":"PROVIDER_429"}); self._save(iid,s)
            return Result("BLOCKED","PROVIDER_429","primer 429 abrió el circuito",revision=s["revision"],event_refs=[ev],data={"counters":s["counters"]})
        payload={"stage_id":stage_id,"artifact":out["artifact"],"sha256":out["sha256"],"classification":"SYNTHETIC"}
        man=append_manifest(s["manifests"][-1] if s["manifests"] else None,payload,len(s["manifests"])+1)
        with self._manifest_path(iid).open("a", encoding="utf-8") as stream: stream.write(json.dumps(man, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")
        s["manifests"].append(man); s["execution_state"]="CLOSED"; s["revision"]+=1; ev=f"EVT-{s['revision']:06d}"; s["events"].append({"event_id":ev,"event_type":"RUN_COMPLETED","manifest_ref":man["chain_sha256"]}); s["counters"].update(delivery_attempt=1, validation_attempt=1)
        r=Result("PASS",revision=s["revision"],event_refs=[ev],manifest_ref=man["chain_sha256"],data={"artifact":out["artifact"],"counters":{"delivery_attempt":1,"provider_retry":0,"validation_attempt":1,"operational_cleanup":0}})
        s["idempotency"][key]=r.as_dict(); self._save(iid,s); return r
    def pause(self,iid,key,operator,expected,reason,now):
        s=self._load(iid)
        if key in s["idempotency"]: return Result("PASS", revision=s["revision"], idempotent_replay=True, message_safe="pausa ya registrada")
        if expected!=s["revision"]: return Result("BLOCKED","PERSISTENCE_CONFLICT","revision distinta")
        try: verify_grant(s["operator_grant"],operator,"pause_run",f"initiative:{iid}",s["data_classification"],"local-sandbox",now)
        except TallerError as e: return Result("BLOCKED",e.code,e.message_safe)
        if s["execution_state"] != "RUNNING": return Result("BLOCKED","POLICY_BLOCKED","sólo una ejecución activa puede pausarse")
        s["execution_state"]="PAUSED"; s["revision"]+=1; s["events"].append({"event_id":f"EVT-{s['revision']:06d}","event_type":"RUN_PAUSED","reason":reason}); r=Result("PASS",revision=s["revision"]); s["idempotency"][key]=r.as_dict(); self._save(iid,s); return r
    def resume(self,iid,key,operator,expected,now):
        s=self._load(iid)
        if expected!=s["revision"]: return Result("BLOCKED","PERSISTENCE_CONFLICT","revision distinta")
        try: verify_grant(s["operator_grant"],operator,"resume_run",f"initiative:{iid}",s["data_classification"],"local-sandbox",now)
        except TallerError as e: return Result("BLOCKED",e.code,e.message_safe)
        if key in s["idempotency"]: return Result("PASS", revision=s["revision"], idempotent_replay=True, message_safe="reanudación ya registrada")
        if s["execution_state"]=="CLOSED": return Result("BLOCKED","POLICY_BLOCKED","una ejecución cerrada es terminal")
        if s.get("circuit_state") == "OPEN": return Result("BLOCKED","CIRCUIT_OPEN","circuito de proveedor abierto")
        s["execution_state"]="READY"; self._save(iid,s); return self.start(iid,"STAGE-01",key,operator,s["revision"],now)
