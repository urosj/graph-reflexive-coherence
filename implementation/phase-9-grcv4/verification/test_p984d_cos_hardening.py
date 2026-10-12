"""Pressure the hardening's proof interface without another native campaign."""

from copy import deepcopy
from dataclasses import replace
from fractions import Fraction as Q
import unittest
from unittest.mock import patch

from flint import ctx
import p984d_cos_hardening as h


class HardeningTests(unittest.TestCase):
    def test_interval_scope_and_selector_guard(self):
        m = h.b.read(h.prior.INPUTS)
        t = replace(h.prior.target(m, h.center(m)), dt=h.b.DT)
        with ctx.workprec(h.BITS):
            after, _, domain = h.interval_os(t)
            self.assertGreater(
                min(h.lower(after[i, 0]) for i in range(after.nrows())), 0
            )
            self.assertGreater(Q(domain["selector_gap_lower"]), 0)
            # A disconnected graph cannot inherit the constant-sector formula.
            with patch.object(
                h, "connected_unit_tree", side_effect=ValueError("disconnected")
            ):
                with self.assertRaisesRegex(ValueError, "disconnected"):
                    h.interval_os(t)
        self.assertEqual(h.charge((1.0, 2.0, 3.0)), 6.0)

    def test_saved_sign_and_represented_continuity_mutations(self):
        m = h.b.read(h.prior.INPUTS)
        v = h.prior.previous.expand(h.b.read(h.prior.RESULTS)["execution"])
        i = m["cases"].index(h.center(m))
        row = v["cases"][i]
        i = next(
            i
            for i, o in enumerate(row["observations"])
            if o["stage"] == "target_continuation"
            and o["role"] == "current"
            and o["beat"] == 1
        )
        captured = row["consumption_evidence"][i]["value"]
        with (
            patch.object(
                h.b, "dense_os", side_effect=AssertionError("dense oracle forbidden")
            ),
            patch.object(
                h.b,
                "ProvisionalCandidateCOSStep",
                side_effect=AssertionError("native forbidden"),
            ),
        ):
            cert = h.point_sign(captured)
            self.assertGreater(Q(cert["minimum_sign_separation"]), 0)
            altered = deepcopy(captured)
            altered["poststate"]["current"]["C"][0] += 1e-8
            with self.assertRaisesRegex(ValueError, "represented continuity"):
                h.point_sign(altered)

    def test_retained_report_scope_and_resealed_mutations(self):
        d, r = h.b.read(h.INPUTS), h.b.read(h.RESULTS)
        self.assertFalse(h.check(d, r)["public_ordinary_step_owner_tested"])
        for kind in ("drop", "sign", "acceptance", "predecessor"):
            bad = deepcopy(r)
            if kind == "drop":
                bad["signs"].pop()
            elif kind == "sign":
                bad["signs"][0]["minimum_sign_separation"] = "-1"
            elif kind == "acceptance":
                bad["user_accepted"] = True
            else:
                bad["inputs_digest"] = "0" * 64
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                h.check(d, h.b.seal(bad))


if __name__ == "__main__":
    unittest.main()
