"""Pruebas de contrato del core I2."""
import json,tempfile,unittest
from pathlib import Path
from kit.taller.domain import Policy, grant_hash, verify_grant, TallerError, append_manifest
from kit.taller.application import TallerService
from kit.taller.adapters.synthetic import SyntheticProvider
class TallerCoreTests(unittest.TestCase):
 def grant(self):
  g={"schema_version":"operator-grant/v1","grant_id":"GRANT-SYN-001","operator_id":"operator-local-synthetic","issuer_id":"director-local-synthetic","role":"operador_taller","operations":["create_initiative","start_run","pause_run","resume_run"],"resource_scope":["initiative:INITIATIVE-SYNTHETIC-01"],"data_classification":["SYNTHETIC"],"environment":"local-sandbox","expires_at":"2026-12-31T23:59:59Z","revoked_at":None}; g["grant_sha256"]=grant_hash(g); return g
 def init(self): return {"initiative_id":"INITIATIVE-SYNTHETIC-01","owner_id":"owner-local-synthetic","scope":{"included":["synthetic-action"]},"data_classification":"SYNTHETIC","environment":"local-sandbox","stages":[]}
 def test_grant_fail_closed(self):
  g=self.grant(); verify_grant(g,g["operator_id"],"create_initiative","initiative:INITIATIVE-SYNTHETIC-01","SYNTHETIC","local-sandbox","2026-10-27T00:00:00Z"); g["grant_sha256"]="sha256:tampered"
  with self.assertRaisesRegex(TallerError,"hash"): verify_grant(g,g["operator_id"],"create_initiative","initiative:INITIATIVE-SYNTHETIC-01","SYNTHETIC","local-sandbox","2026-10-27T00:00:00Z")
 def test_idempotent_and_manifest_chain(self):
  with tempfile.TemporaryDirectory() as d:
   svc=TallerService(d); r=svc.create(self.init(),self.grant(),Policy(),"2026-10-27T00:00:00Z"); self.assertEqual(r.status,"PASS")
   a=svc.start("INITIATIVE-SYNTHETIC-01","STAGE-01","idem-key-00000001","operator-local-synthetic",0,"2026-10-27T00:00:00Z"); b=svc.start("INITIATIVE-SYNTHETIC-01","STAGE-01","idem-key-00000001","operator-local-synthetic",0,"2026-10-27T00:00:00Z"); self.assertFalse(a.idempotent_replay); self.assertTrue(b.idempotent_replay)
   snap=json.loads((Path(d)/"INITIATIVE-SYNTHETIC-01"/"case.json").read_text()); self.assertEqual(len(snap["manifests"]),1); self.assertEqual(snap["decisions"]["publication"],"NOT_AUTHORIZED")
 def test_manifest_append_only(self):
  a=append_manifest(None,{"x":1},1); b=append_manifest(a,{"x":2},2); self.assertEqual(b["previous_manifest_sha256"],a["chain_sha256"])
 def test_closed_pause_resume_is_terminal(self):
  with tempfile.TemporaryDirectory() as d:
   svc=TallerService(d); svc.create(self.init(),self.grant(),Policy(),"2026-10-27T00:00:00Z")
   done=svc.start("INITIATIVE-SYNTHETIC-01","STAGE-01","closed-key-000001","operator-local-synthetic",0,"2026-10-27T00:00:00Z")
   paused=svc.pause("INITIATIVE-SYNTHETIC-01","pause-key-000001","operator-local-synthetic",done.revision,"reason","2026-10-27T00:00:00Z")
   resumed=svc.resume("INITIATIVE-SYNTHETIC-01","resume-key-000001","operator-local-synthetic",done.revision,"2026-10-27T00:00:00Z")
   self.assertEqual(paused.status,"BLOCKED"); self.assertEqual(resumed.status,"BLOCKED")
   snap=json.loads((Path(d)/"INITIATIVE-SYNTHETIC-01"/"case.json").read_text()); self.assertEqual(len(snap["manifests"]),1)
 def test_manifest_tampering_blocks_load(self):
  with tempfile.TemporaryDirectory() as d:
   svc=TallerService(d); svc.create(self.init(),self.grant(),Policy(),"2026-10-27T00:00:00Z"); svc.start("INITIATIVE-SYNTHETIC-01","STAGE-01","tamper-key-00001","operator-local-synthetic",0,"2026-10-27T00:00:00Z")
   p=Path(d)/"INITIATIVE-SYNTHETIC-01"/"manifests.ndjson"; p.write_text(p.read_text().replace("synthetic-pass","altered"))
   with self.assertRaises(TallerError): svc.start("INITIATIVE-SYNTHETIC-01","STAGE-01","next-key-000001","operator-local-synthetic",1,"2026-10-27T00:00:00Z")
 def test_first_429_opens_circuit_without_fallback(self):
  with tempfile.TemporaryDirectory() as d:
   provider=SyntheticProvider([429, 200]); svc=TallerService(d, provider)
   svc.create(self.init(),self.grant(),Policy(),"2026-10-27T00:00:00Z")
   r=svc.start("INITIATIVE-SYNTHETIC-01","STAGE-01","429-key-00000001","operator-local-synthetic",0,"2026-10-27T00:00:00Z")
   self.assertEqual(r.error_code,"PROVIDER_429"); self.assertEqual(provider.calls,1)
   snap=json.loads((Path(d)/"INITIATIVE-SYNTHETIC-01"/"case.json").read_text())
   self.assertEqual(snap["circuit_state"],"OPEN"); self.assertEqual(snap["counters"]["provider_retry"],1)
   self.assertEqual(snap["manifests"],[]); self.assertEqual(snap["events"][-1]["event_type"],"PROVIDER_429")
   self.assertEqual(svc.resume("INITIATIVE-SYNTHETIC-01","resume-429-key-0001","operator-local-synthetic",r.revision,"2026-10-27T00:00:00Z").error_code,"CIRCUIT_OPEN")
 def test_real_pause_resume_has_one_effect_and_keeps_reason(self):
  with tempfile.TemporaryDirectory() as d:
   svc=TallerService(d); svc.create(self.init(),self.grant(),Policy(),"2026-10-27T00:00:00Z")
   def interrupt(service, iid):
    snap=json.loads((Path(d)/iid/"case.json").read_text())
    service.pause(iid,"pause-real-key-0001","operator-local-synthetic",snap["revision"],"operator interruption","2026-10-27T00:00:00Z")
   paused=svc.start("INITIATIVE-SYNTHETIC-01","STAGE-01","run-real-key-000001","operator-local-synthetic",0,"2026-10-27T00:00:00Z",execution_hook=interrupt)
   self.assertEqual(paused.error_code,"INTERRUPTED")
   resumed=svc.resume("INITIATIVE-SYNTHETIC-01","resume-real-key-001","operator-local-synthetic",paused.revision,"2026-10-27T00:00:00Z")
   self.assertEqual(resumed.status,"PASS")
   snap=json.loads((Path(d)/"INITIATIVE-SYNTHETIC-01"/"case.json").read_text())
   self.assertEqual(len(snap["manifests"]),1); self.assertEqual(snap["execution_state"],"CLOSED")
   self.assertEqual([e["reason"] for e in snap["events"] if e["event_type"]=="RUN_PAUSED"],["operator interruption"])
if __name__=="__main__": unittest.main()
