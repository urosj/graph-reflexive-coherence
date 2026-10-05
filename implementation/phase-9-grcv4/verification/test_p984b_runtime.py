"""Focused P9-8.4b capture, oracle independence and fail-closed pressure."""

from copy import deepcopy
from dataclasses import replace
import unittest
from unittest.mock import patch

import p984b_runtime as run


class RuntimeContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = run.make_manifest()
        cls.case = next(
            c for c in cls.manifest["cases"] if c["fixture_id"] == run.PINNED
        )

    def test_exact_sixteen_cases_and_all_ten_family_register(self):
        cases = self.manifest["cases"]
        self.assertEqual(len(cases), 16)
        self.assertEqual(len({c["case_id"] for c in cases}), 16)
        rows = self.manifest["coverage_rows"]
        self.assertEqual(len(rows), 322)
        self.assertEqual(len({r["family"] for r in rows}), 10)
        self.assertEqual(
            sum(r["disposition"] == "scheduled_C_OS_companion" for r in rows), 32
        )
        self.assertFalse(self.manifest["user_accepted"])
        self.assertFalse(self.manifest["aggregate_closed"])

    def test_independent_target_matches_retained_baseline_without_expansion(self):
        with patch.object(
            run.native,
            "GRC9V4COSExpansion",
            side_effect=AssertionError("production oracle"),
        ):
            expected = run.independent_target(self.manifest, self.case)
        original = run.GeometryStageInputs.from_payload(
            run.read(run.SEEDS)["states"]["C_OS"]["target"]["inputs"]
        )
        self.assertEqual(expected.geometry.reference, original.geometry.reference)
        self.assertEqual(expected.current, original.current)
        self.assertEqual(expected.reset, original.reset)
        self.assertNotEqual(expected.current, expected.reset)

    def test_all_layout_oracles_keep_exact_ports_and_fresh_complete_references(self):
        for case in self.manifest["cases"]:
            with self.subTest(case=case["fixture_id"]):
                expected = run.independent_target(self.manifest, case)
                graph = expected.geometry.reference.graph
                n = case["oracle"]["event_identity"]["canonical_module_node_count"]
                self.assertEqual(len(graph.live_node_ids), 9 + n)
                self.assertEqual(len(graph.live_edge_ids), 8 + n)
                self.assertEqual(
                    set(
                        expected.geometry.reference.profile.params_resolved.candidate.W_C_tr
                    ),
                    set(graph.live_edge_ids),
                )
                for role in ("current", "reset"):
                    self.assertEqual(
                        sum(map(run.Fraction, getattr(expected, role).C)),
                        sum(
                            map(
                                run.Fraction,
                                self.manifest["expected_source"]["inputs"][role]["C"],
                            )
                        ),
                    )

    def test_dense_oracle_does_not_call_native_current_or_os(self):
        inputs = run.GeometryStageInputs.from_payload(self.manifest["initial_inputs"])
        with (
            patch.object(
                run.native,
                "CandidateCCurrent",
                side_effect=AssertionError("native oracle"),
            ),
            patch.object(
                run, "CandidateCOSPass", side_effect=AssertionError("native OS")
            ),
        ):
            result = run.dense_os(inputs)
        self.assertEqual(set(result), set(self.case["comparison"]["quantities"]))
        self.assertEqual(len(result["C"]), 10)

    def test_comparator_rejects_nonfinite_shapes_norms_budgets_and_changed_values(self):
        policy = self.case["comparison"]
        for actual, expected in [
            ([float("nan")], [0]),
            ([0], [float("inf")]),
            ([0], [[0]]),
            ([], []),
            ([1], [0]),
        ]:
            with (
                self.subTest(actual=actual, expected=expected),
                self.assertRaises(ValueError),
            ):
                run.comparison(actual, expected, policy, "C")
        for field, value in [
            ("norm", "l2"),
            ("atol", float("inf")),
            ("atol", -1),
            ("rtol", True),
        ]:
            with self.subTest(field=field), self.assertRaises(ValueError):
                run.comparison([0], [0], {**policy, field: value}, "C")
        self.assertTrue(run.comparison([0], [0], policy, "C")["passed"])

    def test_rehashed_changed_manifest_is_not_accepted(self):
        for field, value in [("atol", 1), ("norm", "l2")]:
            changed = deepcopy(self.manifest)
            changed["cases"][0]["comparison"][field] = value
            with self.assertRaisesRegex(ValueError, "declared case builder"):
                run.check_manifest(run.seal(changed))

    def test_timeout_preserves_missing_stages_without_event_or_pass(self):
        with patch.object(
            run, "independent_target", side_effect=run.BudgetExpired("injected timeout")
        ):
            result = run.execute_cos(self.manifest, self.case)
        self.assertFalse(result["event_committed"])
        self.assertEqual(result["outcome"], "incomplete_case")
        self.assertEqual(result["first_failure"]["outcome"], "incomplete_budget")
        self.assertTrue(result["unexecuted_dependent_stages"])

    def test_source_reset_mutation_blocks_before_event(self):
        step = run.ProvisionalCandidateCOSStep

        # Change the delivered next_inputs without changing the underlying kernel.
        def corrupt_output(inputs):
            from types import SimpleNamespace

            actual = step(inputs)
            return SimpleNamespace(
                os_pass=actual.os_pass,
                next_inputs=replace(
                    actual.next_inputs, reset=actual.next_inputs.current
                ),
            )

        with patch.object(run, "ProvisionalCandidateCOSStep", corrupt_output):
            result = run.execute_cos(self.manifest, self.case)
        self.assertFalse(result["event_committed"])
        self.assertEqual(result["first_failure"]["stage"], "source_schedule")
        self.assertIn("reset changed", result["first_failure"]["message"])

    def test_frozen_checks_are_mechanics_not_committed_events(self):
        records = run.frozen_mechanics()
        self.assertEqual(len(records), 17)
        self.assertTrue(
            all(
                r["passed"] and not r["event_committed"] and not r["numerical_executed"]
                for r in records
            )
        )

    @classmethod
    def successful_result(cls):
        if not hasattr(cls, "retained"):
            case = cls.manifest["cases"][0]
            row = run.execute_cos(cls.manifest, case)
            if row["outcome"] != "passed_named_case":
                raise AssertionError(row["first_failure"])
            cls.retained = run.seal(
                {
                    "manifest_digest": cls.manifest["record_digest"],
                    "requested_case_ids": [case["case_id"]],
                    "cases": [row],
                    "user_accepted": False,
                    "aggregate_closed": False,
                }
            )
        return deepcopy(cls.retained)

    def test_actual_d30_run_and_retained_independent_reconstruction(self):
        result = self.successful_result()
        self.assertEqual(run.validate_results(self.manifest, result)["passed_cases"], 1)
        case = result["cases"][0]
        self.assertEqual(len(case["actual_admission_reads"]), 4)
        self.assertEqual(
            len(case["actual_receipts"]), len(case["checkpoint"]["receipts"])
        )
        self.assertEqual(len(case["observations"]), 23)

    def test_rehashed_missing_case_role_stage_and_acceptance_promotions(self):
        def corrupt_result(mutate):
            value = self.successful_result()
            mutate(value)
            with self.assertRaises((ValueError, KeyError)):
                run.validate_results(self.manifest, run.seal(value))

        corrupt_result(lambda r: r["cases"].clear())
        corrupt_result(lambda r: r.update(user_accepted=True))
        corrupt_result(lambda r: r["cases"][0]["stages"].pop())
        corrupt_result(lambda r: r["cases"][0]["observations"].pop())
        corrupt_result(lambda r: r["cases"][0]["actual_admission_reads"].pop())
        corrupt_result(lambda r: r["cases"][0].update(event_committed=False))
        corrupt_result(
            lambda r: r["cases"][0]["actual_target"]["inputs"]["reset"][
                "C"
            ].__setitem__(0, 999)
        )

    def test_rehashed_matching_fake_comparison_still_fails_independent_oracle(self):
        record = self.successful_result()
        item = record["cases"][0]["observations"][0]["comparisons"][0]
        item["actual"][0] = item["expected"][0] = 123
        item["maximum_error"] = max(
            abs(a - b) for a, b in zip(item["actual"], item["expected"], strict=True)
        )
        with self.assertRaisesRegex(ValueError, "oracle operand/result drift"):
            run.validate_results(self.manifest, run.seal(record))

    def test_actual_missing_reset_admission_is_not_a_case_pass(self):
        original = run.native._cos_readmit

        def skip_reset(state):
            if len(state.inputs.current.C) == 10:
                return original(state)
            for _ in range(2):
                run.native.CandidateCOSPass(replace(state.inputs, dt=1))

        with patch.object(run.native, "_cos_readmit", skip_reset):
            row = run.execute_cos(self.manifest, self.manifest["cases"][0])
        self.assertTrue(row["event_committed"])
        self.assertEqual(row["outcome"], "incomplete_case")
        self.assertIn("admission operand", row["first_failure"]["message"])
        self.assertTrue(row["unexecuted_dependent_stages"])


if __name__ == "__main__":
    unittest.main()
