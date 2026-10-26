#!/usr/bin/env python3
"""Validate authenticated smoke contract; adapters are opt-in and never shell input."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path

def main():
 p=argparse.ArgumentParser(); p.add_argument('--adapter',type=Path,required=True); p.add_argument('--scenario',type=Path,required=True); p.add_argument('--format',choices=['json','text'],default='json'); p.add_argument('--read-only',action='store_true'); a=p.parse_args(); errors=[]
 try: adapter=json.loads(a.adapter.read_text()); scenario=json.loads(a.scenario.read_text())
 except (OSError,json.JSONDecodeError) as e: errors.append({'code':'AUTH000','safe_value':type(e).__name__,'message':'invalid contract'}); adapter=scenario={}
 if scenario.get('schema_version')!='guardrails/v1': errors.append({'code':'AUTH000','message':'unsupported schema'})
 if not scenario.get('allowed_hosts') or not all(r.get('fixture_id','').startswith('USER-') for r in scenario.get('roles',[])): errors.append({'code':'AUTH001','message':'synthetic identities required'})
 if any('password' in json.dumps(x).lower() or 'token' in json.dumps(x).lower() for x in (adapter,scenario)): errors.append({'code':'SECURITY001','message':'secret-like field rejected'})
 if not scenario.get('state_probe',{}).get('must_equal'): errors.append({'code':'AUTH002','message':'before/after equality required'})
 out={'schema_version':'guardrails/v1','verdict':'FAIL' if errors else 'BLOCKED','exit_code':1 if errors else 3,'issues':errors,'mode':'read-only','observations':[],'note':'runtime adapter execution is opt-in'}
 print('AUTH_SMOKE_'+out['verdict'] if a.format=='text' else json.dumps(out,ensure_ascii=False,sort_keys=True,separators=(',',':'))); return out['exit_code']
if __name__=='__main__': sys.exit(main())
