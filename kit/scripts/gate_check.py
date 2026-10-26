#!/usr/bin/env python3
"""Validate guardrails/v1 manifests without mutation."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"lib"))
from guardrails import validate_gate, validate_traceability

def main():
 p=argparse.ArgumentParser(); p.add_argument('--project',type=Path,required=True); p.add_argument('--manifest',type=Path,action='append'); p.add_argument('--evidence-root',type=Path); p.add_argument('--repo-ref'); p.add_argument('--format',choices=['json','text'],default='json'); p.add_argument('--read-only',action='store_true'); p.add_argument('--strict',action='store_true'); a=p.parse_args()
 manifests=a.manifest or ([a.project/'gate-record.json'] if (a.project/'gate-record.json').exists() else []); results=[]
 if not manifests:
  required=('PROJECT-BRIEF.yaml','ACCEPTANCE-MANIFEST.yaml','WORKFLOW-STATE.json')
  missing=[x for x in required if not (a.project/x).is_file()]
  result={'schema_version':'legacy','verdict':'FAIL' if missing else 'PASS','exit_code':1 if missing else 0,'ok':not missing,'checks':[{'check':x,'ok':x not in missing} for x in required],'errors':missing}
  print(json.dumps(result,ensure_ascii=False,sort_keys=True,separators=(',',':'))); return result['exit_code']
 for f in manifests:
  try:
   data=json.loads(f.read_text()); result=validate_traceability(data,a.evidence_root,a.repo_ref) if 'trace' in f.name.lower() else validate_gate(data,a.evidence_root)
  except (OSError,json.JSONDecodeError) as e: result={'schema_version':'guardrails/v1','verdict':'FAIL','exit_code':2,'counts':{'errors':1,'warnings':0},'issues':[{'code':'CLI001','severity':'error','path':str(f),'safe_value':type(e).__name__,'message':'cannot read manifest'}]}
  result['manifest']=str(f); results.append(result)
 out={'schema_version':'guardrails/v1','verdict':'FAIL' if any(x['verdict']=='FAIL' for x in results) else ('WARN' if any(x['verdict']=='WARN' for x in results) else 'PASS'),'exit_code':1 if any(x['exit_code'] for x in results) else 0,'results':results}
 out['ok'] = out['exit_code'] == 0
 if a.format=='text': print(('TRACEABILITY_' if 'trace' in str(manifests[0]).lower() else 'GATE_STATE_')+out['verdict'])
 else: print(json.dumps(out,ensure_ascii=False,sort_keys=True,separators=(',',':')))
 return out['exit_code']
if __name__=='__main__': sys.exit(main())