#!/usr/bin/env python3
"""Checks documentation plus deterministic secret/PII safeguards."""
from __future__ import annotations
import re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {'.git', 'node_modules', 'dist', 'build', 'coverage', 'playwright-report', 'test-results', '.cache', '__pycache__'}
SECRET = re.compile(r'(?i)(?:api[_-]?key|password|passwd|secret|token)\s*[:=]\s*["\'][^"\']{8,}["\']')
PII = re.compile(r'(?i)\b(?:DUI|NIT|student[_ -]?id|phone|tel[eé]fono)\s*[:=]\s*[A-Z0-9][A-Z0-9 -]{5,}\b')
PATCH_POLICY = ROOT/'docs/product/BOTTEGA-2-FRAPPE-PATCH-POLICY.md'
PATCH_POLICY_REQUIRED = (
    'v16.53.0', 'latest', 'framework_major', 'frappe_tag', 'frappe_commit',
    'python_version', 'node_version', 'mariadb_version',
    'redis_or_valkey_version', 'yarn_version', 'os_image_digest',
    'licencias', 'advisories', 'SBOM', 'procedencia', 'backup', 'restore',
    'rollback', 'candidate|validated|rejected', 'patches posteriores',
)

def files():
    for p in ROOT.rglob('*'):
        if p.is_file() and not EXCLUDED.intersection(p.parts) and p.suffix.lower() in {'.md', '.yaml', '.yml', '.json', '.py', '.js', '.ts'}:
            yield p

def main():
    findings=[]
    if not PATCH_POLICY.is_file():
        findings.append('missing Frappe patch policy')
    else:
        policy = PATCH_POLICY.read_text(encoding='utf-8')
        findings.extend(
            f'Frappe patch policy missing required marker: {marker}'
            for marker in PATCH_POLICY_REQUIRED if marker not in policy
        )
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
