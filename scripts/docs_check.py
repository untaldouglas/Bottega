#!/usr/bin/env python3
"""Checks documentation plus deterministic secret/PII safeguards."""
from __future__ import annotations
import re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {'.git', 'node_modules', 'dist', 'build', 'coverage', 'playwright-report', 'test-results', '.cache', '__pycache__'}
SECRET = re.compile(r'(?i)(?:api[_-]?key|password|passwd|secret|token)\s*[:=]\s*["\'][^"\']{8,}["\']')
PII = re.compile(r'(?i)\b(?:DUI|NIT|student[_ -]?id|phone|tel[eé]fono)\s*[:=]\s*[A-Z0-9][A-Z0-9 -]{5,}\b')

def files():
    for p in ROOT.rglob('*'):
        if p.is_file() and not EXCLUDED.intersection(p.parts) and p.suffix.lower() in {'.md', '.yaml', '.yml', '.json', '.py', '.js', '.ts'}:
            yield p

def main():
    findings=[]
    for path in files():
        try: text=path.read_text(encoding='utf-8')
        except UnicodeDecodeError: continue
        scrub=re.sub(r'```.*?```','',text,flags=re.S)
        if SECRET.search(scrub): findings.append(f'secret pattern en {path.relative_to(ROOT)}')
        if PII.search(scrub): findings.append(f'PII pattern en {path.relative_to(ROOT)}')
    scanner=ROOT/'app01/scripts/scan-secrets.mjs'
    if scanner.is_file():
        run=subprocess.run(['node',str(scanner)],cwd=ROOT/'app01',text=True,capture_output=True)
        if run.returncode: findings.append('existing secret scan failed')
    if findings:
        print('docs-check: FAIL ('+str(len(findings))+' findings)')
        for finding in findings: print(finding)
        return 1
    print('docs-check: OK (secret scan integrated; deterministic PII scan: 0 findings; generated/dependencies excluded)')
    return 0
if __name__ == '__main__': sys.exit(main())
