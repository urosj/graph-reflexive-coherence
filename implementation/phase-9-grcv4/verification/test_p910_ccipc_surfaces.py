"""Composite family uses the shared retained API/browser/notebook checks."""
from fractions import Fraction
import unittest

import test_p910_cpc_surfaces as shared


class CCIPCSurfaces(shared.CPCSurfaces):
    FAMILY = "C_CI_PC"
    ACCEPTED = False
    REMAINING = ["A_CI_PC", "C_RG2b", "A_RG2b"]
    HISTORICAL_FAMILY = "C_PC"
    CELL = "p910-ccipc-basin"
    VARIABLE = "phase9_ccipc_basin"

    def test_complete_composite_root_and_honest_error_scope(self):
        for case in self.evidence["direct_target"]["observations"]:
            for role in ("current", "reset"):
                root = case["selected_roots"][role]
                self.assertEqual(root["selected_inputs"]["stage"], "cipc_trial")
                self.assertEqual(root["recipe"]["inputs"]["current"]["Z_4"],
                                 case["saved_native_state"]["inputs"][role]["Z_4"])
                self.assertEqual(root["selected_inputs"]["current"],
                                 root["recipe"]["inputs"]["current"])
                self.assertTrue(root["certificate"])
                self.assertGreater(root["evaluations"], 0)
                self.assertEqual(case["realization_checks"][role], "full_J_H_root_old_Z_domain_certificate_bound")
                equation = case["role_equations"][role]
                self.assertFalse(equation["exact_root_signs_claimed"])
                self.assertLess(Fraction(equation["current_error_upper"]), Fraction(1, 2**40))
                tolerance = case["saved_native_state"]["inputs"]["reference"]["profile"]["params_resolved"]["realization"]["tolerance"]
                self.assertLess(Fraction(equation["geometry_residual_upper"]), Fraction(tolerance))


if __name__ == "__main__":
    unittest.main()
