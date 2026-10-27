"""Pruebas de contrato del core I2."""
import json,tempfile,unittest
from pathlib import Path
from kit.taller.domain import Policy, grant_hash, verify_grant, TallerError, append_manifest
from kit.taller.application import TallerService
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
if __name__=="__main__": unittest.main()
