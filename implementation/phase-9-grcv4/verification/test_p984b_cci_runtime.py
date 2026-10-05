"""Focused C_CI scientific, history and negative-path pressure, not a campaign."""

from copy import deepcopy
from dataclasses import replace
import unittest
from unittest.mock import patch

import numpy as np
import p984b_cci_runtime as r
from tests.models.test_grc_v4_ci import configure
from test_p980_os_effect_witness import separation

b = r.b


class CCITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.backend = b.exact_backend(b.ExactBackend.FLINT)
        cls.backend.__enter__()
        cls.addClassCleanup(cls.backend.__exit__, None, None, None)
        cls.manifest = r.make_manifest()
        cls.shared, cls.seed = r.run_source(cls.manifest)
        cls.case = next(c for c in cls.manifest["cases"] if c["fixture_id"] == b.PINNED)
        cls.request = b.GRC9V4ExpansionRequestInput.from_payload(cls.case["request"])
        cls.owner, outcome, cls.event = r.event_capture(cls.seed, cls.request)
        assert outcome.committed, cls.event["failure"]
        cls.target = r.check_event(cls.seed, cls.case, cls.event)

    def test_full_manifest_and_distinct_role_schedule(self):
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
        self.assertNotEqual(self.seed.inputs.current, self.seed.inputs.reset)
        self.assertEqual(
            self.shared["source_step"]["poststate"]["reset"],
            self.manifest["initial_inputs"]["reset"],
        )
        self.assertTrue(
            all(
                c["schedule"]["target_beats_per_role"] == 10
                for c in self.manifest["cases"]
            )
        )

    def test_represented_continuity_is_not_one_round_exact_arithmetic(self):
        from pygrc.models.grc_v4_geometry import VertexScalar, PhysicalFlux
        from pygrc.models.grc_v4_transport import provisional_continuity

        before = b.GeometryStageInputs.from_payload(self.manifest["initial_inputs"])
        before = replace(
            before,
            current=b.GRCV4AuthoritativeState(
                (before.dt, *before.current.C[1:]), None, None
            ),
        )
        j = (1.0, 2**-53, *((0.0,) * 7))
        actual = provisional_continuity(
            VertexScalar(before.geometry.reference.graph, before.current.C),
            PhysicalFlux(before.geometry.reference.graph, j),
            before.dt,
            differential=before.geometry.reference.differential,
        )
        self.assertEqual(r.represented_continuity(before, j), actual.values)
        self.assertEqual(actual.values[0], 0.0)
        # A once-rounded exact expression would instead give -2^-65.
        self.assertNotEqual(actual.values[0], -(2**-65))

    def test_joint_root_geometry_and_certificate_cannot_degrade_to_current(self):
        before = self.seed.inputs
        original = self.event["admission_reads"][0]["root"]
        for key, mutate in (
            ("H", lambda v: v[0].__setitem__(0, v[0][0] + 1e-6)),
            ("generated", lambda v: v[0].__setitem__(0, v[0][0] + 1e-6)),
            ("source", lambda v: v[0].__setitem__(0, 2 * v[0][0])),
            ("bounds", lambda v: v.__setitem__("contraction_upper", "1")),
        ):
            with self.subTest(key=key):
                value = deepcopy(original)
                mutate(value[key])
                cert = value.pop("independent_certificate")
                value = b.seal(value)
                cert["selected_root_digest"] = value["record_digest"]
                value["independent_certificate"] = cert
                with self.assertRaises(ValueError):
                    r.check_root(before, value)

    def test_continuity_wrong_current_and_stale_restart_rejected(self):
        before = b.GeometryStageInputs.from_payload(self.manifest["initial_inputs"])
        original = self.shared["source_step"]
        for change in ("current", "restart", "reset", "writer"):
            with self.subTest(change=change):
                value = deepcopy(original)
                if change == "current":
                    value["selection_current"] = value["root"]["baseline"]
                elif change == "restart":
                    value["restart"] = value["root"]
                elif change == "reset":
                    value["poststate"]["reset"] = value["poststate"]["current"]
                else:
                    value["carrier_writes"] = 1
                with self.assertRaises(ValueError):
                    r.check_step(before, value)

    def test_receipt_reference_role_and_trigger_substitutions_rejected(self):
        for change in ("references", "roles", "trigger", "publication"):
            with self.subTest(change=change):
                value = deepcopy(self.event)
                if change == "references":
                    value["checkpoint"]["reference_currents"][0]["roles"]["current"][
                        "target"
                    ][0] += 1
                elif change == "roles":
                    value["admission_reads"][1]["reset_root"] = value[
                        "admission_reads"
                    ][1]["root"]
                elif change == "trigger":
                    value["detections"][0]["current"] = self.shared["source_step"][
                        "root"
                    ]["J"]
                else:
                    value["publication"][0]["admission_pairs"] = 1
                with self.assertRaises(ValueError):
                    r.check_event(self.seed, self.case, value)

    def test_effect_separation_and_wrong_law_interval_rejection(self):
        # Retain accepted meaning: fixed-selected-H path ablations, not
        # alternate-root effects or a stability assertion.
        for role, key in (("current", "root"), ("reset", "reset_root")):
            inputs = replace(
                self.target.inputs, current=getattr(self.target.inputs, role)
            )
            value = self.event["admission_reads"][1][key]
            model = r.independent_model(inputs)
            output = {k: np.array(value[k]) for k in ("H", "J", "baseline", "source")}
            truth = r.numerical.certify_read(
                model,
                "C",
                "CI",
                np.array(inputs.current.C),
                None,
                None,
                output["H"],
                output,
            )
            for channel in ("modulation", "feedback", "geometry"):
                control = model.read(
                    "C",
                    np.array(inputs.current.C),
                    None,
                    output["H"],
                    **{channel: False},
                )
                exact = truth["high"].read(
                    "C", truth["c"], None, truth["H"], **{channel: False}
                )
                self.assertGreater(
                    separation(
                        output["J"], control["J"], truth["read"]["J"], exact["J"]
                    )["minimum_margin_ratio"],
                    1,
                )
            wrong = deepcopy(value)
            wrong["source"] = (2 * output["source"]).tolist()
            with self.assertRaises(ValueError):
                r.independent_certificate(inputs, wrong)

    def test_original_phase_one_shares_fail_independent_continuation(self):
        case = deepcopy(
            next(
                c
                for c in self.manifest["cases"]
                if c["request"]["target_effective_degree"] == 52
                and c["request"]["growth_phase"] == 1
            )
        )
        # No native campaign or retuning: the explicit control changes just
        # the simplex recipe. Target labels are irrelevant to this stencil.
        case["request"]["resource_distribution"] = [0.5, 0.25, 0.25]
        target = b.independent_target(self.manifest, case)
        with self.assertRaisesRegex(ValueError, "negative"):
            r.preflight(target)

    def test_reset_only_domain_rejection_and_late_failure_are_atomic(self):
        before = configure(self.seed.inputs, radius=3e-6, gain=0.5, tolerance=2**-44)
        seed = replace(self.seed, inputs=before)
        request = replace(
            self.request,
            source_state_digest=seed.scientific_digest,
            target_profile_template_id=native_template(seed),
        )
        owner = r.native.GRC9V4CCIOperation(seed)
        checkpoint = owner.checkpoint()
        outcome = owner.expand(request)
        self.assertFalse(outcome.committed)
        self.assertEqual(outcome.failure.stage, "target_readmission")
        self.assertEqual(checkpoint, owner.checkpoint())
        # Passing current-as-reset control proves the reset-only distinction.
        seed2 = replace(seed, inputs=replace(before, reset=before.current))
        control = replace(request, source_state_digest=seed2.scientific_digest)
        self.assertTrue(r.native.GRC9V4CCIOperation(seed2).expand(control).committed)
        owner = r.native.GRC9V4CCIOperation(self.seed)
        checkpoint = owner.checkpoint()
        published = owner.state
        with patch.object(
            r.native,
            "make_commit_receipts",
            side_effect=ValueError("late publication pressure"),
        ):
            outcome = owner.expand(self.request)
        self.assertFalse(outcome.committed)
        self.assertEqual(owner.checkpoint(), checkpoint)
        self.assertIs(owner.state, published)


def native_template(seed):
    from pygrc.models.grc_9_v4_expansion import cci_profile_template

    return cci_profile_template(seed.inputs.geometry.reference).profile_template_id


if __name__ == "__main__":
    unittest.main(verbosity=2)
