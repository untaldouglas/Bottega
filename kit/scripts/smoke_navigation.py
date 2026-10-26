#!/usr/bin/env python3
"""Validate navigation smoke policy without opening a browser."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'lib'))
from guardrails import validate_navigation

def main():
 p=argparse.ArgumentParser(); p.add_argument('--adapter',type=Path,required=True); p.add_argument('--scenario',type=Path,required=True); p.add_argument('--format',choices=['json','text'],default='json'); p.add_argument('--read-only',action='store_true'); a=p.parse_args()
 try: data=json.loads(a.scenario.read_text())
 except (OSError,json.JSONDecodeError) as e: data={'schema_version':'bad','error':type(e).__name__}
 out=validate_navigation(data); out['mode']='read-only'; out['note']='browser execution is adapter opt-in'
 print('NAVIGATION_'+out['verdict'] if a.format=='text' else json.dumps(out,ensure_ascii=False,sort_keys=True,separators=(',',':'))); return out['exit_code']
if __name__=='__main__': sys.exit(main())
