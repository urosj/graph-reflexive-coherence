"""Focused native stage/lifecycle pressure; retained campaign tests run separately."""

from copy import deepcopy
from dataclasses import replace
import unittest
from unittest.mock import patch

import p984b_aos_runtime as runtime

base, aos, oracle, capture, native = (
    runtime.base,
    runtime.aos,
    runtime.oracle,
    runtime.capture,
    runtime.native,
)


class NativeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = runtime.make_manifest()
        cls.accepted, cls.expected = runtime.accepted_oracle()
        with base.exact_backend(base.ExactBackend.FLINT):
            cls.shared, cls.seed = runtime.run_source(cls.manifest, cls.expected)
            cls.case = cls.manifest["cases"][0]
            cls.oracle_case = cls.accepted["cases"][0]
            cls.result = runtime.execute_case(
                cls.seed,
                cls.case,
                cls.oracle_case,
                cls.expected["cases"][0],
                cls.expected["shared_observations"],
            )
        if not cls.result["case_passed"]:
            raise AssertionError(cls.result["first_failure"])
        cls.target = runtime.seed_from_payload(cls.result["event"]["actual_target"])
        cls.before = replace(cls.target.inputs, dt=aos.DT)
        cls.step = cls.result["continuation"][0]["step"]

    def test_exact_population_and_immutable_accepted_prerequisite(self):
        self.assertEqual(len(self.manifest["cases"]), 16)
        self.assertEqual(
            len(
                {
                    v
                    for c in self.manifest["cases"]
                    for v in c["coverage_binding"]["cell_ids"]
                }
            ),
            32,
        )
        with (
            patch.object(runtime, "ACCEPTANCE_SHA", "unaccepted"),
            self.assertRaisesRegex(ValueError, "review changed"),
        ):
            runtime.accepted_oracle()
        changed = deepcopy(self.manifest)
        changed["cases"].pop()
        with self.assertRaisesRegex(ValueError, "population drift"):
            runtime.check_manifest(base.seal(changed))

    def test_source_and_both_native_continuations_are_not_nominal_substitutes(self):
        self.assertTrue(self.result["event_committed"])
        self.assertEqual(len(self.result["continuation"]), 20)
        self.assertEqual(set(self.result["final_reads"]), set(oracle.ROLES))
        self.assertEqual(
            self.result["actual_request"]["source_state_digest"],
            self.seed.scientific_digest,
        )
        self.assertEqual(
            self.result["actual_request"]["history_policy"],
            aos.history_policy(
                capture.authority(self.seed.inputs.current),
                capture.authority(self.seed.inputs.reset),
            ),
        )
        self.assertTrue(self.result["event"]["replay_identical"])

    def test_writer_predictor_and_incoming_resource_substitution_rejected(self):
        for field in ("point_identity", "J", "C", "W_A"):
            changed = deepcopy(self.step)
            w = changed["pass"]["trace"]["writer_targets"][0]
            if field == "point_identity":
                w[field] = changed["pass"]["predictor"]["identity"]
            elif field == "J":
                w[field] = changed["pass"]["predictor"]["current"]
            elif field == "C":
                w[field] = list(self.before.current.C)
            else:
                w[field] = changed["poststate"]["W_A"]
            with (
                self.subTest(field=field),
                self.assertRaisesRegex(ValueError, "writer operand substitution"),
            ):
                capture.check_step(
                    changed, self.before, self.target.differential_reference
                )

    def test_regeneration_substitution_rejected_even_with_small_split(self):
        changed = deepcopy(self.step)
        passed = changed["pass"]
        passed["regenerated"] = passed["H"]
        passed["trace"]["geometry"][1]["H"] = passed["H"]
        self.assertTrue(
            aos.split_admitted(
                passed["H"],
                passed["regenerated"],
                self.before.geometry.reference.pairings.one_form.matrix,
                runtime.Q(aos.SPLIT),
            )
        )
        with self.assertRaisesRegex(ValueError, "own predictor/corrector source"):
            capture.check_step(changed, self.before, self.target.differential_reference)

    def test_final_read_and_writer_count_cannot_be_silently_changed(self):
        for field in ("final", "restart", "count", "rebuild"):
            changed = deepcopy(self.step)
            if field in ("final", "restart"):
                changed[field] = changed["pass"]["corrector"]
            elif field == "count":
                changed["pass"]["trace"]["log_writes"] *= 2
            else:
                changed["pass"]["trace"]["rebuilds"][3]["W_A"] = changed["poststate"][
                    "W_A"
                ]
            with self.subTest(field=field), self.assertRaises(ValueError):
                capture.check_step(
                    changed, self.before, self.target.differential_reference
                )

    def test_consumption_validation_does_not_execute_native_steps_or_reads(self):
        with (
            patch.object(
                capture.steps,
                "ProvisionalCandidateAOSStep",
                side_effect=AssertionError("native step"),
            ),
            patch.object(
                capture.realizations,
                "CandidateAOSPass",
                side_effect=AssertionError("native pass"),
            ),
            patch.object(
                capture.candidate,
                "CandidateACurrent",
                side_effect=AssertionError("native current"),
            ),
        ):
            capture.check_step(
                self.step, self.before, self.target.differential_reference
            )

    def test_missing_admission_and_altered_reference_lineage_rejected(self):
        for mutation in ("admission", "publication", "reference", "history", "state"):
            event = deepcopy(self.result["event"])
            if mutation == "admission":
                event["admission_reads"].pop()
            elif mutation == "publication":
                event["publication_observations"][0][
                    "admission_reads_before_receipts"
                ] = 2
            elif mutation == "reference":
                event["checkpoint"]["reference_currents"][0]["roles"]["reset"][
                    "target"
                ][0] += 1
            elif mutation == "history":
                event["receipts"][0]["identity_payload"]["history"]["candidate"][
                    "disposition"
                ] = "target_initializer"
            else:
                event["actual_target"]["inputs"]["reset"]["W_A"][0] += 1e-6
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                runtime.check_event(
                    event,
                    self.seed,
                    runtime.fresh_request(self.seed, self.oracle_case),
                    self.oracle_case,
                )

    def test_reset_only_split_rejection_and_late_failure_are_atomic(self):
        original = next(
            c for c in self.accepted["cases"] if c["fixture_id"] == base.PINNED
        )
        with base.exact_backend(base.ExactBackend.FLINT):
            # Changing only reset W to .99 is already outside source admission;
            # do not mislabel that as target-only rejection.
            invalid_source = replace(
                self.seed,
                inputs=replace(
                    self.seed.inputs,
                    reset=replace(
                        self.seed.inputs.reset,
                        W_A=(0.99,) * len(self.seed.inputs.reset.W_A),
                    ),
                ),
            )
            with self.assertRaisesRegex(
                capture.realizations.OSStageError, "split tolerance"
            ):
                native.GRC9V4AOSOperation(invalid_source)
            negative = runtime.state(
                oracle.predecessor()["rejection_expectations"]["target_split"][
                    "source_role"
                ]
            )
            for role in oracle.ROLES:
                seed = replace(
                    self.seed, inputs=replace(self.seed.inputs, **{role: negative})
                )
                owner = native.GRC9V4AOSOperation(seed)
                before, identity = owner.checkpoint(), owner.state
                result = owner.expand(runtime.fresh_request(seed, original))
                self.assertFalse(result.committed)
                self.assertEqual(result.failure.stage, "target_readmission")
                self.assertIn("split tolerance", result.failure.message)
                self.assertIs(owner.state, identity)
                self.assertEqual(owner.checkpoint(), before)
            owner = native.GRC9V4AOSOperation(self.seed)
            before, identity = owner.checkpoint(), owner.state
            with patch.object(
                native,
                "_event_receipts",
                side_effect=ValueError("injected late receipt failure"),
            ):
                result = owner.expand(
                    runtime.fresh_request(self.seed, self.oracle_case)
                )
            self.assertFalse(result.committed)
            self.assertEqual(result.failure.stage, "commit")
            self.assertIs(owner.state, identity)
            self.assertEqual(owner.checkpoint(), before)

    def test_committed_event_is_not_successful_case_when_continuation_fails(self):
        with (
            base.exact_backend(base.ExactBackend.FLINT),
            patch.object(
                runtime,
                "checked_step",
                side_effect=ValueError("injected continuation failure"),
            ),
        ):
            result = runtime.execute_case(
                self.seed,
                self.case,
                self.oracle_case,
                self.expected["cases"][0],
                self.expected["shared_observations"],
            )
        self.assertTrue(result["event_committed"])
        self.assertFalse(result["case_passed"])
        self.assertEqual(result["outcome"], "incomplete_case")
        self.assertEqual(result["first_failure"]["stage"], "target_continuation")


class RetainedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest, cls.results = (
            base.read(runtime.INPUTS),
            base.read(runtime.RESULTS),
        )

    def test_all_32_cells_have_complete_native_evidence_not_acceptance(self):
        runtime.check_manifest(self.manifest)
        report = runtime.validate(self.manifest, self.results)
        self.assertEqual(report["successful_history_cells"], 32)
        self.assertFalse(report["user_accepted"])
        self.assertFalse(report["native_trajectories_rerun"])
        self.assertFalse(report["interval_equations_recomputed"])

    def test_rehashed_missing_history_and_false_acceptance_are_rejected(self):
        for field in ("case", "continuation", "final", "acceptance"):
            value = deepcopy(self.results)
            if field == "case":
                value["cases"].pop()
            elif field == "continuation":
                value["cases"][0]["continuation"].pop()
            elif field == "final":
                value["cases"][0]["final_reads"].pop("reset")
            else:
                value["user_accepted"] = True
            with self.subTest(field=field), self.assertRaises(ValueError):
                runtime.validate(self.manifest, base.seal(value))


if __name__ == "__main__":
    unittest.main()
