import unittest
from kit.frappe import FrappeAdapter, FrappeProfile, RuntimeGate
from kit.scripts.i3_validate import validate

class I3Tests(unittest.TestCase):
    def test_inventory_and_sandbox_are_fail_closed(self):
        self.assertEqual(validate(), [])
        self.assertEqual(FrappeAdapter().metadata()["gate"], "BLOCKED")

    def test_latest_and_real_provider_rejected(self):
        with self.assertRaises(ValueError):
            FrappeProfile(version="latest")
        with self.assertRaises(ValueError):
            FrappeProfile(provider="real-provider")

    def test_runtime_commands_require_gate(self):
        with self.assertRaisesRegex(RuntimeError, "bloqueado"):
            FrappeAdapter().command("install")
        adapter = FrappeAdapter(gate=RuntimeGate.PASS)
        self.assertEqual(adapter.command("migrate"), ["bench", "migrate"])

if __name__ == "__main__":
    unittest.main()
