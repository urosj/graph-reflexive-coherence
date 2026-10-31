"""A composite root/history evidence through the shared family UI/API."""
from fractions import Fraction
import unittest

import test_p910_ccipc_surfaces as shared


class ACIPCSurfaces(shared.CCIPCSurfaces):
    FAMILY = "A_CI_PC"
    ACCEPTED = False
    REMAINING = ["C_RG2b", "A_RG2b"]
    HISTORICAL_FAMILY = "C_CI_PC"
    CELL = "p910-acipc-basin"
    VARIABLE = "phase9_acipc_basin"

    def test_A_history_backend_and_positive_denominator_are_bound(self):
        from pygrc.models.grc_9_v4_topology import GRC9V4CandidateADifferentialReference
        for case in self.evidence["direct_target"]["observations"]:
            for role in ("current", "reset"):
                state = case["saved_native_state"]["inputs"]
                root = case["selected_roots"][role]
                self.assertEqual(root["selected_inputs"]["current"]["W_A"], state[role]["W_A"])
                backend = GRC9V4CandidateADifferentialReference.from_payload(root["recipe"]["differential_reference"])
                self.assertEqual(backend.to_payload()["port_graph"], state["reference"]["graph"])
                self.assertEqual(backend.identity, state["reference"]["profile"]["params_resolved"]["candidate"]["descriptor_backend_id"])
                self.assertGreater(Fraction(case["role_equations"][role]["positive_denominator_lower"]), 0)
                self.assertTrue(case["role_equations"][role]["exact_fixed_geometry_cycle_exclusion"])


if __name__ == "__main__":
    unittest.main()
