"""Focused A_CI root, history, independent-equation and rollback pressure."""

from copy import deepcopy
from dataclasses import replace
import unittest
from unittest.mock import patch

import p984b_aci_runtime as r
from tests.models.test_grc_9_v4_aci import native_effects, request_for

b = r.b


class ACITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        context = b.exact_backend(b.ExactBackend.FLINT)
        context.__enter__()
        cls.addClassCleanup(context.__exit__, None, None, None)
        cls.manifest = r.make_manifest()
        cls.shared, cls.seed = r.run_source(cls.manifest)
        cls.case = r.bind_case(
            cls.seed,
            next(c for c in cls.manifest["cases"] if c["fixture_id"] == b.PINNED),
        )
        cls.request = b.GRC9V4ExpansionRequestInput.from_payload(cls.case["request"])
        cls.owner, outcome, cls.event = r.event_capture(cls.seed, cls.request)
        assert outcome.committed, cls.event["failure"]
        cls.target = r.check_event(cls.seed, cls.case, cls.event)
        cls.before = replace(cls.target.inputs, dt=b.DT)
        cls.step, cls.after = r.checked_step(
            cls.before, cls.target.differential_reference
        )

    def test_all_sixteen_layouts_and_independent_reset(self):
        self.assertEqual(len(self.manifest["cases"]), 16)
        self.assertEqual(
            len(
                {
                    i
                    for c in self.manifest["cases"]
                    for i in c["coverage_binding"]["cell_ids"]
                }
            ),
            32,
        )
        self.assertNotEqual(self.seed.inputs.current.C, self.seed.inputs.reset.C)
        self.assertNotEqual(self.seed.inputs.current.W_A, self.seed.inputs.reset.W_A)
        self.assertEqual(
            self.shared["source_step"]["poststate"]["reset"],
            self.manifest["initial_inputs"]["reset"],
        )
        self.assertEqual(
            self.case["request"]["source_state_digest"], self.seed.scientific_digest
        )

    def test_full_root_geometry_domain_recipe_and_source_mutations(self):
        original = self.event["admission_reads"][0]["root"]
        for field in ("H", "source", "generated", "recipe", "bounds", "readback"):
            value = deepcopy(original)
            if field == "recipe":
                value[field] = "ci_analytic_residual_enclosure_binary64_v2"
            elif field == "bounds":
                value[field]["contraction_upper"] = "1"
            elif field == "readback":
                value[field][0] *= -1
            else:
                value[field][0][0] += 1e-8
            cert = value.pop("independent_certificate")
            value = b.seal(value)
            cert["selected_root_digest"] = value["record_digest"]
            value["independent_certificate"] = cert
            with self.subTest(field=field), self.assertRaises(ValueError):
                r.check_root(self.seed.inputs, self.seed.differential_reference, value)

    def test_writer_inputs_and_single_write_are_actual_consumption(self):
        for field in ("point_identity", "C", "W_A", "J", "count", "drive"):
            value = deepcopy(self.step)
            target = value["writer_targets"][0]
            if field == "point_identity":
                target[field] = "stale-root"
            elif field == "C":
                target[field] = list(self.before.current.C)
            elif field == "W_A":
                target[field] = list(self.after.current.W_A)
            elif field == "J":
                target[field] = value["root"]["baseline"]
            elif field == "drive":
                target["target"][0] *= 2
                value["log_writes"][0]["target"][0] *= 2
            else:
                value["log_writes"] *= 2
            with self.subTest(field=field), self.assertRaises(ValueError):
                r.check_step(self.before, self.target.differential_reference, value)

    def test_stale_restart_continuity_and_reset_substitutions(self):
        for field in ("restart", "current", "reset", "carrier"):
            value = deepcopy(self.step)
            if field == "restart":
                value[field] = value["root"]
            elif field == "current":
                value["selection_current"] = value["root"]["baseline"]
            elif field == "reset":
                value["poststate"]["reset"] = value["poststate"]["current"]
            else:
                value["carrier_writes"] = 1
            with self.subTest(field=field), self.assertRaises(ValueError):
                r.check_step(self.before, self.target.differential_reference, value)

    def test_wrong_map_lineage_trigger_publication_and_writer_surface(self):
        for field in (
            "W",
            "references",
            "trigger",
            "publication",
            "surface",
            "history",
        ):
            value = deepcopy(self.event)
            if field == "W":
                value["actual_target"]["inputs"]["current"]["W_A"][0] += 0.01
            elif field == "references":
                value["checkpoint"]["reference_currents"][0]["roles"]["reset"][
                    "target"
                ][0] += 1
            elif field == "trigger":
                value["detections"][0]["current"] = self.shared["source_step"]["root"][
                    "J"
                ]
            elif field == "publication":
                value["publication"][0]["writer_surfaces"] = 2
            elif field == "surface":
                value["writer_surfaces"][2]["W_A"] = list(self.target.inputs.reset.W_A)
            else:
                value["receipts"][0]["identity_payload"]["history"]["candidate"][
                    "disposition"
                ] = "target_initializer"
            with self.subTest(field=field), self.assertRaises(ValueError):
                r.check_event(self.seed, self.case, value)

    def test_retained_check_does_not_execute_native_roots_or_steps(self):
        with (
            patch.object(
                r, "CandidateCIRoot", side_effect=AssertionError("native root")
            ),
            patch.object(
                r,
                "ProvisionalCandidateCIStep",
                side_effect=AssertionError("native step"),
            ),
        ):
            r.check_step(self.before, self.target.differential_reference, self.step)
            r.check_event(self.seed, self.case, self.event)

    def test_independent_scientific_effects_and_wrong_equation_rejection(self):
        effects = native_effects(self.seed, self.target)
        self.assertEqual(len(effects), 18)
        self.assertTrue(all(row["minimum_margin_ratio"] > 1 for row in effects))
        value = deepcopy(self.step["root"])
        value["source"] = [[2 * x for x in row] for row in value["source"]]
        with self.assertRaises(ValueError):
            r.independent_certificate(self.before, value)

    def test_original_phase_one_shares_have_no_silent_repair(self):
        case = deepcopy(
            next(
                c
                for c in self.manifest["cases"]
                if c["request"]["target_effective_degree"] == 52
                and c["request"]["growth_phase"] == 1
            )
        )
        case["request"]["resource_distribution"] = [0.5, 0.25, 0.25]
        case = r.bind_case(self.seed, case)
        with self.assertRaisesRegex(ValueError, "negative|nonpositive"):
            r.preflight(r.independent_target(self.seed, case))

    def test_both_role_target_domain_rejections_and_late_failure_are_atomic(self):
        negative = r.authority(
            r.predecessor()["rejection_expectations"]["target_domain"]["source_role"]
        )
        # Accepted mathematical counterexample, placed independently in each role.
        for role in r.ROLES:
            source = replace(
                self.seed, inputs=replace(self.seed.inputs, **{role: negative})
            )
            owner = r.native.GRC9V4ACIOperation(source)
            before = owner.checkpoint()
            outcome = owner.expand(request_for(source, self.request))
            self.assertFalse(outcome.committed)
            self.assertEqual(outcome.failure.stage, "target_readmission")
            self.assertEqual(owner.checkpoint(), before)
        # Current-as-reset control identifies a genuinely reset-only failure.
        control = replace(
            self.seed, inputs=replace(self.seed.inputs, reset=self.seed.inputs.current)
        )
        self.assertTrue(
            r.native.GRC9V4ACIOperation(control)
            .expand(request_for(control, self.request))
            .committed
        )
        owner = r.native.GRC9V4ACIOperation(self.seed)
        before = owner.checkpoint()
        with (
            patch.object(
                r.native,
                "make_commit_receipts",
                side_effect=RuntimeError("late publication"),
            ),
            self.assertRaises(RuntimeError),
        ):
            owner.expand(self.request)
        self.assertEqual(owner.checkpoint(), before)


if __name__ == "__main__":
    unittest.main(verbosity=2)
