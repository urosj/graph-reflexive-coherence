"""Regression for the two discovered D52 phase-one continuation rejections.

These are negative controls for the named recipe, not successful coverage or
a finding that phase-one expansion is impossible under every lawful request.
"""

from dataclasses import replace
import unittest

import p984b_runtime as run
from pygrc.models.grc_v4_step import ResourceBoundaryError


class PhaseOneContinuationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = run.read(run.INPUTS)
        cls.results = run.read(run.RESULTS)

    def test_both_actual_zero_extra_nodes_have_independently_negative_first_step(self):
        failures = [
            row
            for row in self.results["cases"]
            if row["outcome"] != "passed_named_case"
        ]
        self.assertEqual(len(failures), 2)
        for row in failures:
            case = next(
                c for c in self.manifest["cases"] if c["case_id"] == row["case_id"]
            )
            with (
                self.subTest(case=case["fixture_id"]),
                run.exact_backend(run.ExactBackend.FLINT),
            ):
                self.assertEqual(case["request"]["target_effective_degree"], 52)
                self.assertEqual(case["request"]["growth_phase"], 1)
                self.assertTrue(row["event_committed"])
                self.assertEqual(row["first_failure"]["stage"], "target_continuation")
                self.assertEqual(row["first_failure"]["role"], "current")
                self.assertEqual(len(row["observations"]), 1)  # source beat only
                target = run.independent_target(self.manifest, case)
                inputs = replace(target, dt=run.DT)
                expected = run.dense_os(inputs)
                index = int(expected["C"].argmin())
                node = inputs.geometry.reference.graph.live_node_ids[index]
                self.assertTrue(node.endswith("/extra/1/1"))
                self.assertEqual(inputs.current.C[index], 0)
                self.assertLess(expected["C"][index], -0.00035)
                self.assertGreater(expected["C"][index], -0.00036)
                with self.assertRaisesRegex(ResourceBoundaryError, "nonnegative"):
                    run.ProvisionalCandidateCOSStep(inputs)
                # There is no positive lower timestep that repairs a negative
                # rate at a zero resource: OS reads do not depend on dt.
                smaller = run.dense_os(replace(inputs, dt=run.DT / 2))
                self.assertAlmostEqual(
                    smaller["C"][index], expected["C"][index] / 2, places=15
                )

    def test_d52_other_phases_are_real_passes_and_failed_roles_stay_unexecuted(self):
        for row in self.results["cases"]:
            case = next(
                c for c in self.manifest["cases"] if c["case_id"] == row["case_id"]
            )
            if case["request"]["target_effective_degree"] != 52:
                continue
            if case["request"]["growth_phase"] == 1:
                self.assertFalse(row["user_accepted"])
                self.assertTrue(
                    any(
                        s["role"] == "reset" and s["stage"] == "target_continuation"
                        for s in row["unexecuted_dependent_stages"]
                    )
                )
                self.assertTrue(
                    all(o["stage"] != "final_read" for o in row["observations"])
                )
            else:
                self.assertEqual(row["outcome"], "passed_named_case")
                self.assertEqual(len(row["observations"]), 23)


if __name__ == "__main__":
    unittest.main()
