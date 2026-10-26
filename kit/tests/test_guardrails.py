import json, subprocess, sys, tempfile, unittest, threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
LIB=ROOT/'lib'; sys.path.insert(0,str(LIB))
from guardrails import validate_gate, validate_traceability, validate_navigation, sha256_payload

SHA='0'*40
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

 def test_auth_smoke_executes_declarative_read_only_adapter(self):
  class Handler(BaseHTTPRequestHandler):
   def do_GET(self):
    payload={"/identity":{"actorId":"USER-A","serverActorId":"USER-A"},"/own":{"owned":True},"/cross":{},"/probe":{"unchanged":True}}
    body=json.dumps(payload.get(self.path,{})).encode(); self.send_response(200 if self.path != '/cross' else 403); self.end_headers(); self.wfile.write(body)
   def log_message(self,*args): pass
  server=HTTPServer(('127.0.0.1',0),Handler); thread=threading.Thread(target=server.serve_forever,daemon=True); thread.start()
  try:
   with tempfile.TemporaryDirectory() as d:
    root=Path(d); base=f'http://127.0.0.1:{server.server_port}'
    adapter={'schema_version':'guardrails/v1','base_url':base,'allowed_hosts':['127.0.0.1'],'operations':[{'id':'identity','path':'/identity','kind':'read_identity'},{'id':'own_read','path':'/own'},{'id':'cross_read','path':'/cross','kind':'read_other_owned'},{'id':'forbidden_mutation','path':'/probe','kind':'mutation_forbidden'}]}
    scenario={'schema_version':'guardrails/v1','roles':[{'fixture_id':'USER-A'}],'operations':[{'id':'identity','expected':'200'},{'id':'own_read','expected':'200'},{'id':'cross_read','expected':'403|404'},{'id':'forbidden_mutation','expected':'200'}],'state_probe':{'before':'same','must_equal':True}}
    ap=root/'a.json'; sp=root/'s.json'; ap.write_text(json.dumps(adapter)); sp.write_text(json.dumps(scenario))
    r=subprocess.run([sys.executable,str(ROOT/'scripts/smoke_authenticated.py'),'--adapter',ap,'--scenario',sp,'--read-only'],capture_output=True,text=True)
    self.assertEqual(r.returncode,0,r.stdout); self.assertIn('PASS',r.stdout)
  finally: server.shutdown(); server.server_close()

 def test_smokes_reject_command_and_navigation_blocks_without_runtime(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); a={'schema_version':'guardrails/v1','base_url':'http://127.0.0.1:1','allowed_hosts':['127.0.0.1'],'command':'; rm -rf /'}; s={'schema_version':'guardrails/v1','canonical_start':'/login','allowed_hosts':['127.0.0.1']}
   ap=root/'a.json'; sp=root/'s.json'; ap.write_text(json.dumps(a)); sp.write_text(json.dumps(s))
   r=subprocess.run([sys.executable,str(ROOT/'scripts/smoke_navigation.py'),'--adapter',ap,'--scenario',sp,'--read-only'],capture_output=True,text=True)
   self.assertNotEqual(r.returncode,0); self.assertIn('SECURITY002',r.stdout)
if __name__=='__main__': unittest.main()
