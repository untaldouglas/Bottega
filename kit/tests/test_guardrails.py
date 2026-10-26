import json, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
LIB=ROOT/'lib'; sys.path.insert(0,str(LIB))
from guardrails import validate_gate, validate_traceability, validate_navigation, sha256_payload

SHA='0'*64
class GuardrailTests(unittest.TestCase):
 def base(self):
  return {'schema_version':'guardrails/v1','records':[{'gate_id':'g','gate_instance_id':'g1','scope':'sandbox','status':'TECHNICAL_PASS','verdict_kind':'verdict','ref_sha':SHA,'issued_at':'2026-01-01T00:00:00Z','evidence':[{'path':'x'}],'evidence_scope':'synthetic','issuer':'test','authorization_granted':[],'prohibited_limits':['production']}]}
 def test_valid_gate_and_conflicting_authorization(self):
  self.assertEqual(validate_gate(self.base())['exit_code'],0)
  x=self.base(); x['records'][0]['authorization_granted']=['PRODUCTION_AUTHORIZED']; self.assertIn('GATE006', [i['code'] for i in validate_gate(x)['issues']])
 def test_traceability_fail_closed(self):
  x={'schema_version':'guardrails/v1','requirements':[{'requirement_id':'R','tests':[],'evidence':[]}]}
  out=validate_traceability(x); self.assertEqual(out['exit_code'],1); self.assertEqual(out['coverage']['required'],1)
 def test_navigation_egress(self):
  x={'schema_version':'guardrails/v1','allowed_hosts':['127.0.0.1'],'allowed_statuses':[200],'observations':[{'host':'evil.test','status':200}]}
  self.assertIn('NAV003',[i['code'] for i in validate_navigation(x)['issues']])
 def test_deterministic_hash(self): self.assertEqual(sha256_payload({'b':1,'a':2}),sha256_payload({'a':2,'b':1}))
 def test_cli_negative(self):
  with tempfile.TemporaryDirectory() as d:
   f=Path(d)/'gate.json'; f.write_text(json.dumps({'schema_version':'bad'}))
   r=subprocess.run([sys.executable,str(ROOT/'scripts/gate_check.py'),'--project',d,'--manifest',f],capture_output=True,text=True)
   self.assertEqual(r.returncode,1); self.assertIn('SCHEMA002',r.stdout)
if __name__=='__main__': unittest.main()
