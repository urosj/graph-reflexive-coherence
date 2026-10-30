"""Focused pressure on P9-10.2's new checks; no native campaign rerun."""

from copy import deepcopy
import math
import unittest

import p9102_verification as v


class VerificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = v.targets.load(v.ROOT, "C_OS")[0]["evidence"]["v2"]

    def test_independent_tree_discriminates_alternative_sums_and_overflow(self):
        large = float(2**53)
        self.assertEqual(v.charge_oracle([large, 1., 1.]), large)
        self.assertEqual(v.charge_oracle([1., 1., large]), large + 2)
        self.assertEqual(v.charge_oracle([large, 1., 1., 1.]), large + 2)
        self.assertEqual(v.charge_oracle([]), 0.)
        self.assertEqual(v.charge_oracle([math.ulp(0.)]), math.ulp(0.))
        for values in ([math.inf], [math.nan], [-1.]):
            with self.subTest(values=values), self.assertRaises(ValueError):
                v.charge_oracle(values)
        with self.assertRaises((ValueError, OverflowError)):
            v.charge_oracle([float.fromhex('0x1.fffffffffffffp+1023')] * 2)

    def test_exact_tolerance_does_not_round_admission_outwards(self):
        tiny = float.fromhex("0x1.5555555555555p-53")
        actual = math.nextafter(3., math.inf)
        self.assertEqual(tiny * 3., actual - 3.)
        self.assertFalse(v.charge_expected([actual], 3., 0., tiny)["admitted"])
        self.assertTrue(v.charge_expected([actual], 3., 0., math.nextafter(tiny, math.inf))["admitted"])

    def test_receipt_parent_endpoint_and_delta_substitutions_fail(self):
        e = self.record
        v.ledger_check(e["final_checkpoint"]["owner"], e["enabled_continuation"])
        for kind in ("parent", "endpoint", "duplicate", "commit", "delta", "observable"):
            with self.subTest(kind=kind):
                owner = deepcopy(e["final_checkpoint"]["owner"])
                result = deepcopy(e["enabled_continuation"])
                if kind in ("parent", "endpoint"):
                    r = owner["receipts"][-1]
                    r["identity_payload"]["core"][
                        "parent_receipt_ids" if kind == "parent" else "source_state_digest"
                    ] = [] if kind == "parent" else "unrelated"
                    # Reseal so the semantic check, not a stale content hash, rejects.
                    r["receipt_id"] = "grc-receipt-sha256:" + v.sha(v.rfc8785.dumps(r["identity_payload"]))
                elif kind == "duplicate":
                    owner["receipts"].append(owner["receipts"][0])
                elif kind == "commit":
                    result["time"] += 1
                elif kind == "delta":
                    result["emitted_receipts"] = result["emitted_receipts"][:-1]
                else:
                    result["observables"] = v.thaw(result["observables"])
                    result["observables"]["charge"]["residual"] = 1
                with self.assertRaises(ValueError):
                    v.ledger_check(owner, result)

    def test_native_execution_is_explicitly_forbidden(self):
        from pygrc.models import GRC9V4
        from pygrc.models import grc_9_v4_basin, grc_v4_transport
        with v.no_native_runs():
            for fn in (GRC9V4.from_config, GRC9V4.from_state,
                       grc_9_v4_basin._read_once, grc_v4_transport.provisional_continuity):
                with self.subTest(fn=fn), self.assertRaises(AssertionError):
                    fn(None)


if __name__ == "__main__":
    unittest.main()
