import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "smoke_http.py"


FAKE_CURL = """#!/usr/bin/env python3
import pathlib
import sys

state = pathlib.Path(sys.argv[1])
sequence = sys.argv[2]
index = int(state.read_text()) if state.exists() else 0
state.write_text(str(index + 1))
result = sequence.split(',')[min(index, len(sequence.split(',')) - 1)]
if result == 'fail':
    print('transient curl error', file=sys.stderr)
    raise SystemExit(1)
raise SystemExit(0)
"""


class SmokeHttpTests(unittest.TestCase):
    def run_smoke(self, sequence, attempts=4):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            curl = root / "curl"
            curl.write_text(FAKE_CURL)
            curl.chmod(curl.stat().st_mode | stat.S_IXUSR)
            state = root / "state"
            curl_wrapper = root / "curl-wrapper"
            curl_wrapper.write_text(
                f"#!/bin/sh\nexec {sys.executable} {curl} {state} {sequence} \"$@\"\n"
            )
            curl_wrapper.chmod(curl_wrapper.stat().st_mode | stat.S_IXUSR)
            return subprocess.run(
                [sys.executable, str(SCRIPT), "--url", "http://example.test/",
                 "--attempts", str(attempts), "--interval", "0", "--curl", str(curl_wrapper)],
                capture_output=True, text=True,
            )

    def test_delayed_availability_passes_and_hides_transient_errors(self):
        result = self.run_smoke("fail,fail,success,success")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("transient curl error", result.stderr)

    def test_never_available_fails_after_all_attempts(self):
        result = self.run_smoke("fail", attempts=3)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("after 3 attempts", result.stderr)
        self.assertNotIn("transient curl error", result.stderr)

    def test_final_explicit_check_failure_is_not_hidden(self):
        result = self.run_smoke("success,fail")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("container readiness check failed", result.stderr)
        self.assertIn("transient curl error", result.stderr)


if __name__ == "__main__":
    unittest.main()
