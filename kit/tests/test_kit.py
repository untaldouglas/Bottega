import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INIT = ROOT / "scripts/init_bottega_project.py"
PREFLIGHT = ROOT / "scripts/bottega_preflight.py"
GATE = ROOT / "scripts/gate_check.py"

class KitTests(unittest.TestCase):
    def run_script(self, script, *args):
        return subprocess.run([sys.executable, str(script), *map(str,args)], cwd=ROOT, capture_output=True, text=True)

    def test_init_dry_run_does_not_write(self):
        with tempfile.TemporaryDirectory() as d:
            target=Path(d)/"new"
            r=self.run_script(INIT,"--target",target,"--product-name","Sintético","--slug","demo-kit","--owner","Test","--dry-run")
            self.assertEqual(r.returncode,0,r.stderr); self.assertFalse(target.exists()); self.assertIn('"dry_run": true',r.stdout)

    def test_invalid_slug_and_unconfirmed_remote(self):
        with tempfile.TemporaryDirectory() as d:
            base=["--target",Path(d)/"x","--product-name","x","--slug","Bad_slug","--owner","x"]
            self.assertNotEqual(self.run_script(INIT,*base).returncode,0)
            base[5]="valid-slug"
            self.assertNotEqual(self.run_script(INIT,*base,"--create-private-repo","--repo-name","x").returncode,0)

    def test_scaffold_and_gate(self):
        with tempfile.TemporaryDirectory() as d:
            target=Path(d)/"new"
            r=self.run_script(INIT,"--target",target,"--product-name","Sintético","--slug","demo-kit","--owner","Test")
            self.assertEqual(r.returncode,0,r.stderr)
            g=self.run_script(GATE,"--project",target)
            self.assertEqual(g.returncode,0,g.stdout); self.assertTrue(json.loads(g.stdout)["ok"])

    def test_help_and_preflight(self):
        for script in (INIT,PREFLIGHT,GATE): self.assertEqual(self.run_script(script,"--help").returncode,0)
        r=self.run_script(PREFLIGHT,"--dry-run"); self.assertIn("fallback_policy",r.stdout)

if __name__ == "__main__": unittest.main()
