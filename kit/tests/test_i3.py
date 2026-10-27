import json
import unittest
from pathlib import Path

from kit.frappe import FrappeAdapter, FrappeProfile, RuntimeGate
from kit.scripts.i3_validate import validate

ROOT = Path(__file__).resolve().parents[2]
ACCEPTED_DIGEST = "sha256:9b629e83e1a517e01eaf7a36362563c0c7f620d3e4747f7dcf79564e290b7b48"


class I3Tests(unittest.TestCase):
    def test_inventory_and_gates_pass(self):
        self.assertEqual(validate(), [])

    def test_gpl_gate_is_pass_internal_only(self):
        gate = json.loads((ROOT / "bench-gpl-review/candidate-frappe-v16.53.0.json").read_text())
        self.assertEqual(gate["decision"], "PASS")
        self.assertEqual(gate["distribution"], "none")

    def test_image_os_gate_accepts_exact_digest(self):
        gate = json.loads((ROOT / "image-os-gate/candidate-frappe-v16.53.0.json").read_text())
        self.assertEqual(gate["decision"], "PASS")
        self.assertTrue(gate["accepted"])
        self.assertEqual(gate["digest"], ACCEPTED_DIGEST)
        self.assertEqual(gate["architecture"], "linux/amd64")
        self.assertTrue(gate["latest_forbidden"])

    def test_latest_and_real_provider_rejected(self):
        with self.assertRaises(ValueError):
            FrappeProfile(version="latest")
        with self.assertRaises(ValueError):
            FrappeProfile(provider="real-provider")
        with self.assertRaises(ValueError):
            FrappeProfile(environment="production")

    def test_erpnext_hrms_denylist_rejected(self):
        for bad in ("erpnext", "erp-next", "hrms", "frappe_hrms"):
            with self.assertRaises(ValueError):
                FrappeProfile(provider=bad)

    def test_runtime_commands_require_gate(self):
        with self.assertRaisesRegex(RuntimeError, "bloqueado"):
            FrappeAdapter().command("install")
        adapter = FrappeAdapter(gate=RuntimeGate.PASS)
        self.assertEqual(adapter.command("migrate"), ["bench", "migrate"])
        self.assertEqual(adapter.command("backup"), ["bench", "backup"])
        self.assertEqual(adapter.command("restore"), ["bench", "restore"])
        self.assertEqual(adapter.command("uninstall"), ["bench", "drop-site"])

    def test_unknown_operation_rejected(self):
        adapter = FrappeAdapter(gate=RuntimeGate.PASS)
        with self.assertRaises(ValueError):
            adapter.command("deploy-to-prod")


if __name__ == "__main__":
    unittest.main()
