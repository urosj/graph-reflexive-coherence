import hashlib
import unittest

import p984b_crg2b_retry as retry

b = retry.b


class RetryTests(unittest.TestCase):
    def setUp(self):
        self.cases = [
            {"case_id": str(i), "execution_budget_seconds": 900} for i in range(16)
        ]
        self.manifest = b.seal({"cases": self.cases})
        self.header = {
            "manifest_digest": self.manifest["record_digest"],
            "cases": [],
            "native_runtime_executed": True,
            "user_accepted": False,
            "aggregate_closed": False,
        }
        self.rows = [
            {
                "case_id": c["case_id"],
                "input_digest": b.digest(c),
                "case_passed": True,
                "first_failure": None,
            }
            for c in self.cases[:15]
        ]
        self.rows[-1].update(
            case_passed=False,
            outcome="incomplete_case",
            first_failure={"kind": "BudgetExpired"},
        )

    def raw(self):
        return b"".join(
            b.canonical_json_bytes(b.seal(r)) + b"\n" for r in [self.header, *self.rows]
        )

    def test_retains_failed_row_and_original_prefix(self):
        raw = self.raw()
        prefix, failure = retry.failed_attempt(
            raw, self.manifest, hashlib.sha256(raw).hexdigest()
        )
        self.assertEqual(len(prefix.splitlines()), 15)
        self.assertFalse(failure["case_passed"])

    def test_numerical_failure_is_not_an_operational_timeout(self):
        self.rows[-1]["first_failure"] = {"kind": "ValueError"}
        raw = self.raw()
        with self.assertRaisesRegex(ValueError, "operational timeout"):
            retry.failed_attempt(raw, self.manifest, hashlib.sha256(raw).hexdigest())

    def test_changed_prefix_rejects_even_with_new_outer_hash(self):
        self.rows[3]["case_id"] = "foreign"
        raw = self.raw()
        with self.assertRaises(ValueError):
            retry.failed_attempt(raw, self.manifest, hashlib.sha256(raw).hexdigest())

    def test_bytes_and_partial_publication_are_bound(self):
        raw = self.raw()
        with self.assertRaisesRegex(ValueError, "evidence drift"):
            retry.failed_attempt(raw, self.manifest, "0" * 64)
        raw = raw[:-1]
        with self.assertRaisesRegex(ValueError, "framing"):
            retry.failed_attempt(raw, self.manifest, hashlib.sha256(raw).hexdigest())


if __name__ == "__main__":
    unittest.main()
