import unittest
from kit.auditor import audit
from kit.taller.domain import append_manifest, grant_hash, scan_safe

class AuditorTests(unittest.TestCase):
 def grant(self):
  g={"schema_version":"operator-grant/v1","grant_id":"G","operator_id":"operator-local-synthetic","operations":["start_run"],"resource_scope":["initiative:I"],"data_classification":["SYNTHETIC"],"environment":"local-sandbox","expires_at":"2099-12-31T23:59:59Z","revoked_at":None}
  g["grant_sha256"]=grant_hash(g); return g
 def valid(self):
  m=append_manifest(None,{"stage_id":"STAGE-01","classification":"SYNTHETIC"},1)
  return {"initiative_id":"I","owner_id":"O","scope":{"included":["synthetic-action"]},"classification":"SYNTHETIC","operator_grant":self.grant(),"policy":{"fallback":"none","network":"deny-all"},"stages":[{"stage_id":"STAGE-01","dependencies":[],"gate":{"status":"APPROVED"},"implementer_id":"bot"}],"decisions":{"product":"NOT_ACCEPTED","release":"NOT_READY","publication":"NOT_AUTHORIZED"},"execution_state":"CLOSED","review_state":"NOT_REVIEWED","counters":{"delivery_attempt":1,"provider_retry":0,"validation_attempt":1,"operational_cleanup":0},"provider_ledger":[{"provider":"synthetic-local","model":"synthetic-action-v1","fallback":"none"}],"review_packet":{"Summary":"s","Evidence":"e","Merge Danger":"d"},"manifests":[m],"events":[{"manifest_ref":m["chain_sha256"]}]}
 def test_self_review_blocked_and_decisions_orthogonal(self):
  s=self.valid(); r=audit(s,"bot"); self.assertEqual(r["verdict"],"BLOCKED"); self.assertEqual(r["publication_decision"],"NOT_AUTHORIZED")
 def test_valid_independent_audit_passes(self):
  self.assertEqual(audit(self.valid(),"reviewer")["verdict"],"PASS")
 def test_forged_manifest_blocked(self):
  s=self.valid(); s["manifests"][0]["chain_sha256"]="sha256:forged"
  self.assertEqual(audit(s,"reviewer")["verdict"],"BLOCKED")
 def test_secret_in_key_blocked_without_value(self):
  self.assertEqual(scan_safe({"token-key":"safe"})[0]["code"],"OUT_OF_SCOPE")
if __name__=="__main__": unittest.main()
