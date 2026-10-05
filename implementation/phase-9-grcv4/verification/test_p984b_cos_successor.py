"""Focused reporting/consumption pressure and named phase-one successors."""

from copy import deepcopy
from dataclasses import replace
import unittest
from unittest.mock import patch

import p984b_cos_successor as successor

base = successor.base


class CaptureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        manifest = base.read(base.INPUTS)
        cls.policy = manifest["cases"][0]["comparison"]
        inputs = base.GeometryStageInputs.from_payload(manifest["initial_inputs"])
        with base.exact_backend(base.ExactBackend.FLINT):
            step = base.ProvisionalCandidateCOSStep(inputs)
        cls.capture = successor.step_capture(step)

    def test_actual_consumer_and_post_refresh_agree(self):
        before, after = successor.check_step(self.capture, self.policy)
        self.assertEqual(after.step_index, before.step_index + 1)

    def test_selection_cannot_substitute_predictor_even_for_similar_values(self):
        changed = deepcopy(self.capture)
        changed["selection"]["inputs"] = changed["pass"]["predictor"]["descriptor"][
            "inputs"
        ]
        with self.assertRaisesRegex(ValueError, "consume the captured corrector"):
            successor.check_step(changed, self.policy)

    def test_read_operand_source_and_alternate_flat_surface_are_bound(self):
        for field, value in (
            ("read_current", [0] * 9),
            ("read_source_identity", "foreign"),
            ("causal_flat", [0] * 9),
        ):
            changed = deepcopy(self.capture)
            changed["pass"]["predictor"][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                successor.check_step(changed, self.policy)

    def test_resource_and_delivered_poststate_cannot_disagree(self):
        for field in ("resource", "poststate"):
            changed = deepcopy(self.capture)
            value = changed[field] if field == "resource" else changed[field]["current"]
            value["C"][0] += 1e-4
            with self.subTest(field=field), self.assertRaises(ValueError):
                successor.check_step(changed, self.policy)

    def test_final_refresh_cannot_silently_keep_precontinuity_resource(self):
        changed = deepcopy(self.capture)
        changed["final"] = changed["pass"]["corrector"]
        with self.assertRaisesRegex(ValueError, "final refresh"):
            successor.check_step(changed, self.policy)

    def test_consumption_check_uses_no_native_reexecution(self):
        with (
            patch.object(
                base,
                "ProvisionalCandidateCOSStep",
                side_effect=AssertionError("native rerun"),
            ),
            patch.object(
                base, "CandidateCOSPass", side_effect=AssertionError("native rerun")
            ),
        ):
            successor.check_step(self.capture, self.policy)


class DesignTests(unittest.TestCase):
    def test_only_two_named_requests_change_and_original_failures_remain_failures(self):
        previous = base.read(base.INPUTS)
        new = successor.make_manifest()
        self.assertEqual(new["initial_inputs"], previous["initial_inputs"])
        self.assertEqual(new["expected_source"], previous["expected_source"])
        self.assertEqual(len(new["cases"]), 2)
        for case in new["cases"]:
            old = next(
                c
                for c in previous["cases"]
                if c["case_id"] == case["predecessor_case_id"]
            )
            changed = {
                k for k in case["request"] if case["request"][k] != old["request"][k]
            }
            self.assertEqual(changed, {"operation_id", "resource_distribution"})
            self.assertEqual(case["comparison"], old["comparison"])
            self.assertEqual(case["schedule"], old["schedule"])
            self.assertNotEqual(case["oracle"]["event_id"], old["oracle"]["event_id"])
        report = successor.summary(previous, base.read(base.RESULTS))
        self.assertEqual(report["complete_cases"], 14)
        self.assertEqual(report["events_committed"], 16)
        self.assertFalse(report["native_trajectories_rerun"])
        self.assertFalse(report["all_required_cases_passed"])
        self.assertEqual(sum(not r["case_passed"] for r in report["cases"]), 2)
        self.assertTrue(
            all(
                r["consumption_evidence"] == "not_captured_in_original_run"
                for r in report["cases"]
            )
        )

    def test_enabled_independent_preflight_positive_for_both_roles_chiralities(self):
        manifest = successor.make_manifest()
        for case in manifest["cases"]:
            target = base.independent_target(manifest, case)
            for role in ("current", "reset"):
                with self.subTest(case=case["case_id"], role=role):
                    rates = case["design"]["successor_zero_node_rates"][role]
                    self.assertTrue(
                        all(base.Fraction(r["uncoupled_rate_exact"]) > 0 for r in rates)
                    )
                    inputs = replace(target, current=getattr(target, role), dt=base.DT)
                    for _ in range(10):
                        expected = base.dense_os(inputs)
                        self.assertGreater(float(min(expected["C"])), 1e-5)
                        inputs = replace(
                            inputs,
                            current=base.GRCV4AuthoritativeState(
                                tuple(map(float, expected["C"])), None, None
                            ),
                        )

    def test_rehashed_design_change_is_rejected(self):
        manifest = successor.make_manifest()
        manifest["cases"][0]["request"]["resource_distribution"] = [0.5, 0.25, 0.25]
        with self.assertRaisesRegex(ValueError, "fixed design"):
            successor.check_manifest(base.seal(manifest))


class RetainedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = base.read(successor.INPUTS)
        cls.results = base.read(successor.RESULTS)

    def test_retained_two_successors_without_native_rerun(self):
        successor.check_manifest(self.manifest)
        with (
            patch.object(
                base,
                "ProvisionalCandidateCOSStep",
                side_effect=AssertionError("native rerun"),
            ),
            patch.object(
                base, "CandidateCOSPass", side_effect=AssertionError("native rerun")
            ),
        ):
            summary = successor.validate(self.manifest, self.results)
        self.assertEqual(summary["complete_cases"], 2)
        self.assertTrue(summary["all_required_cases_passed"])
        self.assertFalse(summary["native_trajectories_rerun"])
        self.assertFalse(summary["user_accepted"])
        self.assertFalse(summary["P9_8_4b_closed"])

    def test_consistent_reported_actuals_cannot_bypass_consumption_links(self):
        row = deepcopy(self.results["cases"][0])
        # Corrupt only the reporting surface. The live captured consumer remains
        # independent of that extraction, even if a caller rehashes the record.
        observation = row["observations"][0]
        for comparison in observation["comparisons"]:
            if comparison["quantity"] == "corrector_J":
                comparison["actual"] = comparison["expected"] = [0] * 9
        with self.assertRaisesRegex(ValueError, "reported actual"):
            successor.check_consumption(row, self.manifest, self.manifest["cases"][0])

    def test_missing_capture_wrong_selection_and_false_summary_fail_closed(self):
        for mutation in ("capture", "selection", "summary"):
            result = deepcopy(self.results)
            row = result["cases"][0]
            if mutation == "capture":
                row["consumption_evidence"].pop()
            elif mutation == "selection":
                row["consumption_evidence"][0]["value"]["selection"]["current"][0] += (
                    1e-5
                )
            else:
                row["case_passed"] = False
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                successor.validate(self.manifest, base.seal(result))


if __name__ == "__main__":
    unittest.main()
