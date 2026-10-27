#!/usr/bin/env python3
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from kit.auditor import audit
p=argparse.ArgumentParser(); s=p.add_subparsers(dest="cmd",required=True); q=s.add_parser("check"); q.add_argument("--initiative",required=True); q.add_argument("--snapshot",required=True); q.add_argument("--reviewer",required=True)
a=p.parse_args()
if a.cmd=="check":
    snap=json.loads(Path(a.snapshot).read_text()); out=audit(snap,a.reviewer); print(json.dumps(out,ensure_ascii=False,sort_keys=True)); sys.exit({"PASS":0,"NEEDS_WORK":1,"BLOCKED":3}[out["verdict"]])
