import unittest
from kit.auditor import audit
class AuditorTests(unittest.TestCase):
 def test_self_review_blocked_and_decisions_orthogonal(self):
  s={"initiative_id":"I","owner_id":"O","scope":{"included":["synthetic-action"]},"stages":[{"implementer_id":"bot"}],"decisions":{"product":"PRODUCT_PASS","release":"NOT_READY","publication":"NOT_AUTHORIZED"},"manifests":[{"chain_sha256":"sha256:x"}]}
  r=audit(s,"bot"); self.assertEqual(r["verdict"],"BLOCKED"); self.assertEqual(r["publication_decision"],"NOT_AUTHORIZED")
 def test_valid_independent_audit_passes(self):
  s={"initiative_id":"I","owner_id":"O","scope":{"included":["synthetic-action"]},"stages":[{"implementer_id":"bot"}],"decisions":{"product":"NOT_ACCEPTED","release":"NOT_READY","publication":"NOT_AUTHORIZED"},"manifests":[{"chain_sha256":"sha256:x"}]}
  self.assertEqual(audit(s,"reviewer")["verdict"],"PASS")
