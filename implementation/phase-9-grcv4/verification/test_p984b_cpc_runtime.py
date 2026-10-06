"""C_PC campaign pressure: actual operands, whole history, independent laws."""

import unittest
from copy import deepcopy
from dataclasses import replace
from unittest.mock import patch

import numpy as np
import p984b_cpc_runtime as r
from test_p980_os_effect_witness import separation

b = r.b


class CPCTests(unittest.TestCase):
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

    def test_seventeen_subjects_34_distinct_cells_literal_reset_not_dropped(self):
        self.assertEqual(len(self.manifest["cases"]), 17)
        self.assertEqual(
            len(
                {
                    x
                    for c in self.manifest["cases"]
                    for x in c["coverage_binding"]["cell_ids"]
                }
            ),
            34,
        )
        self.assertEqual(
            self.manifest["cases"][-1]["fixture_id"], "G9-EXPAND-C-PC-CARRIER-RESET"
        )
        self.assertNotEqual(self.seed.inputs.current.Z_4, self.seed.inputs.reset.Z_4)
        self.assertEqual(
            self.shared["source_step"]["poststate"]["reset"],
            self.manifest["initial_inputs"]["reset"],
        )

    def test_all_layouts_independent_admission_preflight(self):
        for case in self.manifest["cases"]:
            with self.subTest(case=case["fixture_id"]):
                target = r.independent_target(self.manifest, case)
                for role in r.ROLES:
                    r.truth(r.role_input(target, role))
                prediction = r.preflight(target)
                # list(ndarray) leaves numpy.float64 scalars, which the strict
                # scientific JSON codec intentionally rejects.
                b.check_digest(b.seal(prediction))
                self.assertEqual([len(prediction[k]) for k in r.ROLES], [10, 10])

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
            for channel in ("geometry", "feedback", "modulation"):
                control = exact["high"].read(
                    "C", exact["c"], None, exact["H"], **{channel: False}
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

    def test_zero_target_formation_then_delayed_geometry(self):
        before = r.role_input(self.target.inputs, "current", dt=b.DT)
        self.assertFalse(any(before.current.Z_4))
        step, value = r.perform_step(before)
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
            (r.native.GRC9V4CPCExpansion, "carrier_archive_payload"),
        ):
            owner = r.native.GRC9V4CPCOperation(self.seed)
            before = owner.checkpoint()
            with patch.object(
                target, name, side_effect=ValueError("injected late fault")
            ):
                result = owner.expand(self.request)
            self.assertFalse(result.committed)
            self.assertEqual(before, owner.checkpoint())
            self.assertEqual(owner.carrier_archives, ())


if __name__ == "__main__":
    unittest.main()
