"""New two-remainder domain pressure; accepted numerical policy unchanged."""

from fractions import Fraction as Q
import unittest

import p984c_aos_oracle as oracle
import p984b_aos_pressure as pressure


class BoundaryDomainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.case = next(c for c in oracle.base.read(oracle.INPUTS)["cases"] if "D38-E1-P1" in c["case_id"])

    def test_split_admission_boundary_preserves_positive_histories(self):
        result = pressure.split_boundary(self.case)
        self.assertEqual(result["inside"]["disposition"], "inside")
        self.assertEqual(result["outside"]["disposition"], "outside")
        self.assertLess(Q(result["offset_bracket_width"]), Q(1, 2**18))

    def test_resource_boundary_is_not_silent_step_clipping(self):
        result = pressure.resource_boundary(self.case)
        below, above = result["probes"]
        self.assertGreater(Q(below["C_min_lower"]), 0)
        self.assertLess(Q(above["C_min_upper"]), 0)
        self.assertEqual(result["fixed_dt"], oracle.aos.DT)

    def test_history_and_floor_domain_not_widened(self):
        result = pressure.floor_and_history_boundaries(self.case)
        self.assertEqual([r["disposition"] for r in result["floor"]],
            ["certified_inactive_floor", "outside_smooth_certificate"])
        self.assertTrue(all(r["paper_rejected"] and r["interval_rejected"] for r in result["nonpositive_history"]))
        oracle.previous.check_certificate(result["tiny_positive_history"]["certificate"])


if __name__ == "__main__":
    unittest.main()
