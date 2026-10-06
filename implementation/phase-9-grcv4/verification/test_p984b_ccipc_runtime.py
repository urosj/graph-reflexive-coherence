"""C_CI+PC companion pressure: joint roots, signed reads and one source writer."""

import unittest
from copy import deepcopy
from unittest.mock import patch

import numpy as np
import p984b_ccipc_runtime as r

b = r.b


class CCIPCTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        backend = b.exact_backend(b.ExactBackend.FLINT)
        backend.__enter__()
        cls.addClassCleanup(backend.__exit__, None, None, None)
        cls.manifest = r.make_manifest()
        cls.shared, cls.seed = r.run_source(cls.manifest)
        cls.case = next(c for c in cls.manifest["cases"] if c["fixture_id"] == b.PINNED)
        cls.request = b.GRC9V4ExpansionRequestInput.from_payload(cls.case["request"])
        cls.owner, outcome, cls.event = r.event_capture(cls.seed, cls.request)
        assert outcome.committed, cls.event["failure"]
        cls.target = r.check_event(cls.seed, cls.case, cls.event)

    def test_sixteen_subjects_32_distinct_cells_both_histories(self):
        self.assertEqual(len(self.manifest["cases"]), 16)
        ids = [
            x for c in self.manifest["cases"] for x in c["coverage_binding"]["cell_ids"]
        ]
        self.assertEqual(len(set(ids)), 32)
        self.assertTrue(all("::C_CI_PC::" in x for x in ids))
        self.assertNotEqual(self.seed.inputs.current.Z_4, self.seed.inputs.reset.Z_4)
        self.assertEqual(
            self.shared["source_step"]["poststate"]["reset"],
            self.manifest["initial_inputs"]["reset"],
        )

    def test_all_layouts_independent_composite_chart_and_first_continuity(self):
        for case in self.manifest["cases"]:
            with self.subTest(case=case["fixture_id"]):
                target = r.independent_target(self.manifest, case)
                chart = r.chart_record(target)
                self.assertEqual(chart, case["independent_target_chart"])
                self.assertGreater(r.Q(chart["source_slack"]), 0)
                self.assertLess(r.Q(chart["contraction_upper"]), 1)
                graph = target.geometry.reference.graph.port_graph.to_payload()
                for role in r.ROLES:
                    authority = getattr(target, role)
                    out = r.oracle.independent_root(graph, authority.C, authority.Z_4)
                    exact = r.oracle.certify(graph, authority.C, authority.Z_4, out)
                    c, _ = r.oracle.step_truth(exact)
                    self.assertGreaterEqual(min(float(x.a) for x in c), 0)

    def test_composite_domain_and_slack_are_whole_chart_requirements(self):
        graph = self.seed.inputs.geometry.reference.graph.port_graph.to_payload()
        with self.assertRaisesRegex(ValueError, "B_2R"):
            r.oracle.chart(
                graph, geometry_radius=r.Q(np.nextafter(r.oracle.ROOT_RADIUS, 0))
            )
        with self.assertRaisesRegex(ValueError, "strict uniform source slack"):
            r.oracle.chart(graph, resource=r.Q(1600))

    def test_whole_carrier_references_and_publication_substitutions(self):
        for change in (
            "archive",
            "reset_archive",
            "archive_order",
            "loss",
            "trigger",
            "roles",
            "publication",
            "target_carrier",
            "reference",
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
                elif change == "reference":
                    value["checkpoint"]["reference_currents"][0]["roles"]["current"][
                        "target"
                    ][-1] = 0.01
                else:
                    value["actual_target"]["inputs"]["current"]["Z_4"][0] = 1 / 16
                with self.assertRaises(ValueError):
                    r.check_event(self.seed, self.case, value)

    def test_actual_current_same_root_source_and_single_writer_operands(self):
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

    def test_signed_vectors_cannot_hide_in_unchanged_outer_product(self):
        before = b.GeometryStageInputs.from_payload(self.manifest["initial_inputs"])
        original = self.shared["source_step"]["read"]
        for key in ("readback", "flat"):
            value = deepcopy(original)
            value[key] = [-x for x in value[key]]
            cert = r.independent_certificate(before, value)
            self.assertGreater(
                r.Q(cert["bounds"][key + "_error"]), r.LIMITS[key + "_error"]
            )
        value = deepcopy(original)
        value["H"] = np.eye(len(value["J"])).tolist()
        with self.assertRaisesRegex(ValueError, "root error"):
            r.independent_certificate(before, value)

    def test_rehashed_generated_geometry_and_slack_do_not_bypass_check(self):
        before = b.GeometryStageInputs.from_payload(self.manifest["initial_inputs"])
        for change in ("old_z_omitted", "slack", "root_count"):
            value = deepcopy(self.shared["source_step"]["read"])
            cert = value.pop("independent_certificate")
            value.pop("record_digest")
            if change == "old_z_omitted":
                value["generated"][0][0] -= before.current.Z_4[0] * r.oracle.KAPPA
            elif change == "slack":
                value["bounds"]["uniform_source_slack"] = "0"
            else:
                value["evaluations"] = 0
            value = b.seal(value)
            value["independent_certificate"] = {
                **cert,
                "selected_read_digest": value["record_digest"],
            }
            with self.subTest(change=change), self.assertRaises(ValueError):
                r.check_read(before, value)

    def test_zero_target_has_instantaneous_geometry_then_one_carrier_write(self):
        before = r.role_input(self.target.inputs, "current", dt=b.DT)
        self.assertFalse(any(before.current.Z_4))
        step, value = r.perform_step(before)
        self.assertNotEqual(
            value["read"]["H"], np.eye(len(value["read"]["J"])).tolist()
        )
        self.assertTrue(any(step.next_inputs.current.Z_4))
        self.assertGreater(r.writer_effect(before, value)["minimum_margin_ratio"], 1)

    def test_independent_producer_and_retained_checks_need_no_native_solver(self):
        before = b.GeometryStageInputs.from_payload(self.manifest["initial_inputs"])
        with (
            patch.object(
                r,
                "CandidateCIRoot",
                side_effect=AssertionError("native root forbidden"),
            ),
            patch.object(
                r,
                "ProvisionalCandidateCIStep",
                side_effect=AssertionError("native step forbidden"),
            ),
        ):
            r.check_step(before, self.shared["source_step"], numerics=True)
            graph = before.geometry.reference.graph.port_graph.to_payload()
            out = r.oracle.independent_root(graph, before.current.C, before.current.Z_4)
            r.oracle.certify(graph, before.current.C, before.current.Z_4, out)

    def test_publication_faults_preserve_owner_archives_and_reference_currents(self):
        for target, name in (
            (r.native, "make_commit_receipts"),
            (r.native.GRC9V4CCIPCExpansion, "carrier_archive_payload"),
        ):
            owner = r.native.GRC9V4CCIPCOperation(self.seed)
            before = owner.checkpoint()
            with patch.object(
                target, name, side_effect=ValueError("injected late fault")
            ):
                outcome = owner.expand(self.request)
            self.assertFalse(outcome.committed)
            self.assertEqual(before, owner.checkpoint())
            self.assertEqual(owner.carrier_archives, ())


if __name__ == "__main__":
    unittest.main()
