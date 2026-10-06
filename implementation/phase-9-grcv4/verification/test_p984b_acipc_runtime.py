"""A_CI_PC campaign pressure: actual operands, whole history, independent laws."""

import unittest
from copy import deepcopy
from dataclasses import replace
from unittest.mock import patch

import numpy as np
import p984b_acipc_runtime as r
from test_p980_os_effect_witness import separation

b = r.b


class ACIPCTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        backend = b.exact_backend(b.ExactBackend.FLINT)
        backend.__enter__()
        cls.addClassCleanup(backend.__exit__, None, None, None)
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

    def test_sixteen_subjects_32_distinct_cells_both_histories(self):
        self.assertEqual(len(self.manifest["cases"]), 16)
        self.assertEqual(
            len(
                {
                    x
                    for c in self.manifest["cases"]
                    for x in c["coverage_binding"]["cell_ids"]
                }
            ),
            32,
        )
        self.assertNotIn(
            "G9-EXPAND-C-PC-CARRIER-RESET",
            [c["fixture_id"] for c in self.manifest["cases"]],
        )
        self.assertNotEqual(self.seed.inputs.current.Z_4, self.seed.inputs.reset.Z_4)
        self.assertEqual(
            self.shared["source_step"]["poststate"]["reset"],
            self.manifest["initial_inputs"]["reset"],
        )

    def test_all_layouts_independent_admission_first_continuation(self):
        for case in self.manifest["cases"]:
            with self.subTest(case=case["fixture_id"]):
                target = r.independent_target(self.seed, r.bind_case(self.seed, case))
                graph = target.inputs.geometry.reference.graph.port_graph.to_payload()
                proof = r.oracle.whole_chart(graph)
                self.assertGreater(r.Q(proof["strict_source_slack"]), 0)
                for role in r.ROLES:
                    old = getattr(target.inputs, role)
                    out = r.oracle.PaperACIPC(graph).step(old.C, old.W_A, old.Z_4)
                    r.oracle.check_step(graph, old.C, old.W_A, old.Z_4, out)
                    b.check_digest(b.seal(out))

    def test_whole_carrier_history_and_stage_substitutions_rejected(self):
        for change in (
            "archive",
            "reset_archive",
            "archive_order",
            "loss",
            "trigger",
            "roles",
            "publication",
            "target_carrier",
        ):
            with self.subTest(change=change):
                value = deepcopy(self.event)
                if change in ("archive", "reset_archive"):
                    value["checkpoint"]["carrier_archives"][0]["history_content"][
                        "content"
                    ][0 if change == "archive" else -1] += 0.01
                elif change == "archive_order":
                    value["checkpoint"]["carrier_archives"][0][
                        "source_edge_ids"
                    ].reverse()
                elif change == "loss":
                    value["receipts"][0]["identity_payload"]["core"][
                        "information_losses"
                    ] = []
                elif change == "trigger":
                    value["detections"][0]["current"] = self.shared["source_step"][
                        "read"
                    ]["J"]
                elif change == "roles":
                    value["admission_reads"][1]["reset_read"] = value[
                        "admission_reads"
                    ][1]["read"]
                elif change == "publication":
                    value["publication"][0]["admission_pairs"] = 1
                else:
                    value["actual_target"]["inputs"]["current"]["Z_4"][0] = 1 / 16
                with self.assertRaises(ValueError):
                    r.check_event(self.seed, self.case, value)

    def test_continuity_and_single_incoming_source_writer_consumption(self):
        before = b.GeometryStageInputs.from_payload(self.manifest["initial_inputs"])
        for change in (
            "wrong_current",
            "post_source",
            "double_write",
            "wrong_old_z",
            "stale_final",
            "reset_write",
        ):
            value = deepcopy(self.shared["source_step"])
            if change == "wrong_current":
                value["selection_current"] = value["read"]["baseline"]
            elif change == "post_source":
                value["carrier_calls"][0]["source"] = [
                    x for row in value["restart"]["source"] for x in row
                ]
            elif change == "double_write":
                value["carrier_calls"] *= 2
            elif change == "wrong_old_z":
                value["carrier_calls"][0]["Z"] = list(before.reset.Z_4)
            elif change == "stale_final":
                value["restart"] = value["read"]
            else:
                value["poststate"]["reset"] = value["poststate"]["current"]
            with self.subTest(change=change), self.assertRaises(ValueError):
                r.check_step(before, value)

    def test_full_formula_wrong_laws_resolved_above_error_and_ulp(self):
        # Source has actual nonzero old Z. Zero target Z is lawfully neutral.
        for role in r.ROLES:
            before = r.role_input(self.seed.inputs, role)
            exact = r.truth(before)
            value = self.event["admission_reads"][0][
                "read" if role == "current" else "reset_read"
            ]
            for channel in ("geometry", "feedback"):
                control = exact["high"].read(
                    "A", exact["c"], exact["w"], exact["H"], **{channel: False}
                )
                nominal = np.array([float(x.mid) for x in control["J"]])
                separation(
                    np.array(value["J"]), nominal, exact["read"]["J"], control["J"]
                )
                changed = deepcopy(value)
                changed["J"] = nominal.tolist()
                certificate = r.independent_certificate(before, changed)
                self.assertGreater(
                    r.Q(certificate["bounds"]["current_error"]),
                    r.LIMITS["current_error"],
                )

    def test_zero_target_has_instantaneous_geometry_and_next_written_history(self):
        before = r.role_input(self.target.inputs, "current", dt=b.DT)
        self.assertFalse(any(before.current.Z_4))
        step, value = r.perform_step(before)
        self.assertNotEqual(
            value["read"]["H"], [list(x) for x in before.geometry.one_form_hodge.matrix]
        )
        self.assertTrue(any(step.next_inputs.current.Z_4))
        self.assertNotEqual(value["read"]["H"], value["restart"]["H"])
        self.assertNotEqual(value["read"]["source"], value["restart"]["source"])
        zero = replace(
            step.next_inputs.current, Z_4=(0.0,) * len(step.next_inputs.current.Z_4)
        )
        control = replace(
            step.next_inputs,
            current=zero,
            geometry=r.geometry(step.next_inputs, zero),
            dt=0,
        )
        exact = r.truth(replace(step.next_inputs, dt=0))
        other = r.truth(control)
        separation(
            np.array(value["restart"]["J"]),
            np.array([float(x.mid) for x in other["read"]["J"]]),
            exact["read"]["J"],
            other["read"]["J"],
        )

    def test_publication_faults_leave_owner_and_archives_untouched(self):
        for target, name in (
            (r.native, "make_commit_receipts"),
            (r.native.GRC9V4ACIPCExpansion, "carrier_archive_payload"),
        ):
            owner = r.native.GRC9V4ACIPCOperation(self.seed)
            before = owner.checkpoint()
            with patch.object(
                target, name, side_effect=ValueError("injected late fault")
            ):
                result = owner.expand(self.request)
            self.assertFalse(result.committed)
            self.assertEqual(before, owner.checkpoint())
            self.assertEqual(owner.carrier_archives, ())

    def test_signed_readback_and_flat_do_not_hide_behind_outer_product(self):
        before = r.role_input(self.seed.inputs, "current")
        original = self.event["admission_reads"][0]["read"]
        for field in ("readback", "flat"):
            value = deepcopy(original)
            cert = value.pop("independent_certificate")
            value[field] = [-x for x in value[field]]
            value = b.seal(value)
            cert["selected_read_digest"] = value["record_digest"]
            value["independent_certificate"] = cert
            with self.subTest(field=field), self.assertRaises(ValueError):
                r.check_read(before, value, numerics=True)

    def test_W_writer_stage_substitutions_and_counts_fail(self):
        before = b.GeometryStageInputs.from_payload(self.manifest["initial_inputs"])
        for change in ("C", "W_A", "J", "drive", "count", "written_W"):
            value = deepcopy(self.shared["source_step"])
            target = value["writer_targets"][0]
            if change == "C":
                target["C"] = list(before.current.C)
            elif change == "W_A":
                target["W_A"] = value["poststate"]["current"]["W_A"]
            elif change == "J":
                target["J"] = value["read"]["baseline"]
            elif change == "drive":
                target["target"][0] *= 2
                value["log_writes"][0]["target"][0] *= 2
            elif change == "count":
                value["log_writes"] *= 2
            else:
                value["poststate"]["current"]["W_A"] = list(before.current.W_A)
            with self.subTest(change=change), self.assertRaises(ValueError):
                r.check_step(before, value)

    def test_each_W_and_Z_effect_reaches_the_next_current_above_error(self):
        for role in r.ROLES:
            before = r.role_input(self.target.inputs, role, dt=b.DT)
            _, value = r.perform_step(before)
            effects = r.writer_effects(before, value)
            self.assertEqual(len(effects), 9)
            self.assertGreater(
                min(x["minimum_margin_ratio"] for x in effects.values()), 1
            )

    def test_reset_only_writer_surface_rejection_prevents_publication(self):
        owner = r.native.GRC9V4ACIPCOperation(self.seed)
        checkpoint = owner.checkpoint()
        original = r.native.candidate_a_writer_target
        calls = []

        def fault(point, c):
            calls.append(point.identity)
            if len(calls) == 4:
                raise ValueError("target reset writer admission fault")
            return original(point, c)

        with patch.object(r.native, "candidate_a_writer_target", fault):
            outcome = owner.expand(self.request)
        self.assertFalse(outcome.committed)
        self.assertEqual(len(calls), 4)
        self.assertEqual(owner.checkpoint(), checkpoint)
        self.assertEqual(owner.carrier_archives, ())

    def test_complete_root_ablations_use_independent_equations(self):
        from pygrc.models import grc_v4_ci as ci

        forbidden = AssertionError("native counterfactual solve forbidden")
        for role, key in (("current", "read"), ("reset", "reset_read")):
            before = r.role_input(self.target.inputs, role)
            value = self.event["admission_reads"][1][key]
            with (
                patch.object(ci, "CandidateCIRoot", side_effect=forbidden),
                patch.object(r, "CandidateCIRoot", side_effect=forbidden),
            ):
                effects = r.effect_checks(before, value)
            self.assertEqual(
                set(effects), {"geometry", "feedback", "instantaneous_source_vs_PC"}
            )
            self.assertGreater(
                min(x["minimum_margin_ratio"] for x in effects.values()), 1
            )

    def test_composite_ball_and_strict_slack_are_not_PC_admission(self):
        graph = self.target.inputs.geometry.reference.graph.port_graph.to_payload()
        with self.assertRaisesRegex(ValueError, "B_2R"):
            r.oracle.whole_chart(
                graph, geometry_radius=r.Q(float(np.nextafter(r.oracle.ROOT_RADIUS, 0)))
            )
        chart = r.oracle.whole_chart(graph)
        with self.assertRaisesRegex(ValueError, "strict uniform source"):
            r.oracle.whole_chart(graph, radius=r.Q(chart["source_frobenius_upper"]))

    def test_rehashed_recipe_geometry_slack_and_drive_do_not_bypass_equations(self):
        before = r.role_input(self.seed.inputs, "current")
        original = self.event["admission_reads"][0]["read"]
        for field in ("recipe", "generated", "slack", "drive"):
            value = deepcopy(original)
            cert = value.pop("independent_certificate")
            if field == "recipe":
                value["recipe"] = "cipc_same_root_source_enclosed_zoh_binary64_v1"
            elif field == "generated":
                value["generated"][0][0] += 2**-30
            elif field == "slack":
                value["bounds"]["uniform_source_slack"] = "0"
            else:
                value["W_hat_A"][0] *= 2
            value = b.seal(value)
            cert["selected_read_digest"] = value["record_digest"]
            value["independent_certificate"] = cert
            with self.subTest(field=field), self.assertRaises(ValueError):
                r.check_read(before, value, numerics=True)

    def test_W_lineage_new_seed_and_reference_map_are_independent_channels(self):
        source = set(self.seed.inputs.geometry.reference.graph.live_edge_ids)
        ids = self.target.inputs.geometry.reference.graph.live_edge_ids
        for role in r.ROLES:
            for old_edge in (True, False):
                value = deepcopy(self.event)
                index = next(i for i, e in enumerate(ids) if (e in source) == old_edge)
                value["actual_target"]["inputs"][role]["W_A"][index] += 2**-20
                with (
                    self.subTest(role=role, old_edge=old_edge),
                    self.assertRaises(ValueError),
                ):
                    r.check_event(self.seed, self.case, value)
        value = deepcopy(self.event)
        value["checkpoint"]["reference_currents"][0]["roles"]["reset"]["target"][0] += 1
        with self.assertRaises(ValueError):
            r.check_event(self.seed, self.case, value)

    def test_independent_root_and_writer_certificates_need_no_native_execution(self):
        from pygrc.models import grc_v4_ci as ci

        before = b.GeometryStageInputs.from_payload(self.manifest["initial_inputs"])
        forbidden = AssertionError("native execution forbidden")
        with (
            patch.object(ci, "CandidateCIRoot", side_effect=forbidden),
            patch.object(r, "CandidateCIRoot", side_effect=forbidden),
            patch.object(r, "ProvisionalCandidateCIStep", side_effect=forbidden),
            patch.object(
                r.native.GRC9V4ACIPCOperation, "expand", side_effect=forbidden
            ),
        ):
            r.check_step(before, self.shared["source_step"], numerics=True)
            r.check_event(self.seed, self.case, self.event, numerics=True)
            for role in r.ROLES:
                self.assertTrue(
                    all(
                        v["minimum_margin_ratio"] > 1
                        for v in self.shared["source_history_effects"][role].values()
                    )
                )


if __name__ == "__main__":
    unittest.main()
