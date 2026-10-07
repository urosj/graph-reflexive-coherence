"""Scientific discrimination and resealed adversaries; no native rerun."""

from copy import deepcopy
from dataclasses import replace
import unittest

import p984c_cos as run


class BoundaryPressureTests(unittest.TestCase):
    def test_predictor_substitution_exceeds_frozen_budget_in_all_64_roles(self):
        manifest = run.base.read(run.INPUTS)
        for case in manifest["cases"]:
            target = run.base.independent_target(manifest, case)
            for role in run.boundary.ROLES:
                with self.subTest(case=case["case_id"], role=role):
                    expected = run.base.dense_os(replace(target, current=getattr(target, role), dt=run.base.DT))
                    self.assertGreater(min(expected["C"]), 0)
                    # This is equation-level discrimination, not rejection due
                    # to a stale descriptor/hash after a value mutation.
                    with self.assertRaises(ValueError):
                        run.base.comparison(expected["predictor_J"], expected["corrector_J"], case["comparison"], "wrong_stage_J")

    def test_resealed_wrong_current_and_wrong_geometry_fail_numerically(self):
        manifest = run.base.read(run.INPUTS)
        record = run.base.read(run.RESULTS)
        row = next(r for r in run.expand(record["execution"])["cases"] if "D38-E1-P1" in r["case_id"])
        case = next(c for c in manifest["cases"] if c["case_id"] == row["case_id"])
        for role in run.boundary.ROLES:
            index = next(i for i,o in enumerate(row["observations"]) if o["stage"] == "target_continuation" and o["role"] == role)
            passed = row["consumption_evidence"][index]["value"]["pass"]
            wrong = deepcopy(passed["corrector"])
            wrong["current"] = wrong["read_current"] = deepcopy(passed["predictor"]["current"])
            with self.assertRaisesRegex(ValueError, "point_J"):
                run.consumer.check_point(wrong, case["comparison"])
            wrong = deepcopy(passed)
            wrong["corrector"] = deepcopy(passed["predictor"])
            # Both individual points remain correctly bound and numerically
            # valid; their composition must reject omitted generated geometry.
            run.consumer.check_point(wrong["corrector"], case["comparison"])
            with self.assertRaises(ValueError):
                run.consumer.check_pass(wrong, case["comparison"])


if __name__ == "__main__":
    unittest.main()
