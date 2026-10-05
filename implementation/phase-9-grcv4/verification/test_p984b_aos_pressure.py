"""Scientific falsification probes, separate from the frozen oracle campaign."""

from copy import deepcopy
from fractions import Fraction as Q
import unittest
from unittest.mock import patch

import numpy as np
from test_p980_os_effect_witness import check_geometry_stages

import p984b_aos_pressure as pressure

oracle, aos, common = pressure.oracle, pressure.aos, pressure.common
EVIDENCE = {}


class ScientificPressureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        manifest = common.read(oracle.INPUTS)
        oracle.check_manifest(manifest)
        cls.d30 = manifest["cases"][0]
        cls.phase_one = [
            c
            for c in manifest["cases"]
            if c["request"]["target_effective_degree"] == 52
            and c["request"]["growth_phase"] == 1
        ]
        cls.original = next(
            c for c in manifest["cases"] if c["fixture_id"] == common.PINNED
        )
        cls.original_bytes = (common.ROOT / oracle.RESULTS).read_bytes()

    @classmethod
    def tearDownClass(cls):
        if cls.original_bytes != (common.ROOT / oracle.RESULTS).read_bytes():
            raise AssertionError("scientific pressure rewrote frozen campaign")

    def test_mechanism_controls_and_frozen_budget_blind_spots(self):
        rows = EVIDENCE["mechanisms"] = []
        robust = {
            "stale_predictor_current",
            "corrector_readback_disabled",
            "frozen_history",
            "writer_uses_incoming_C",
        }
        for case in [self.d30, *self.phase_one]:
            for role in oracle.ROLES:
                row = pressure.mechanism_pressure(case, role)
                rows.append(row)
                self.assertEqual(set(row["controls"]), set(pressure.MODES))
                for name, result in row["controls"].items():
                    with self.subTest(case=case["fixture_id"], role=role, control=name):
                        self.assertGreater(Q(result["exact_law_difference_lower"]), 0)
                        self.assertLess(
                            Q(result["enabled_full_error"]), Q(result["frozen_budget"])
                        )
                        self.assertLess(
                            Q(result["control_full_error"]), Q(result["frozen_budget"])
                        )
                        if name in robust:
                            self.assertTrue(result["effect_separated"])
                            self.assertTrue(result["wrong_value_proved_outside_budget"])
                            self.assertTrue(result["oracle_gate_rejected"])
        # Deliberately do not demand that every wrong law exceed a finite
        # accuracy tolerance. Exact stage consumption remains a native duty.
        EVIDENCE["mechanism_summary"] = {
            "controls": len(rows) * len(pressure.MODES),
            "budget_blind_spots": [
                {
                    "fixture_id": r["fixture_id"],
                    "role": r["role"],
                    "control": name,
                    "effect_separated": v["effect_separated"],
                }
                for r in rows
                for name, v in r["controls"].items()
                if not v["oracle_gate_rejected"]
            ],
        }

    def test_nearby_resource_and_history_corners(self):
        rows = EVIDENCE["nearby"] = pressure.nearby_pressure(self.phase_one)
        self.assertEqual(len(rows), 16)
        for row in rows:
            oracle.check_certificate(row["certificate"])
            self.assertGreater(Q(row["certificate"]["C_lower"]), 0)

    def test_original_phase_one_shares_are_checked_as_a_not_c(self):
        rows = EVIDENCE["original_share_controls"] = pressure.phase_one_share_controls(
            self.phase_one
        )
        self.assertEqual(len(rows), 4)
        # Record actual A outcomes; C's negative result is not an assertion
        # about A. Either disposition must have an independent signed bound.
        for row in rows:
            if row["proved_negative_resource"]:
                self.assertLess(Q(row["C_min_upper"]), 0)
                self.assertLess(row["represented_C_min"], 0)
            else:
                self.assertGreaterEqual(Q(row["C_min_lower"]), 0)
            self.assertGreater(Q(row["W_min_lower"]), 0)

    def test_split_boundary_proves_inside_and_outside_not_just_large_residual_bound(
        self,
    ):
        row = EVIDENCE["split_boundary"] = pressure.split_boundary(self.original)
        self.assertLess(Q(row["offset_bracket_width"]), Q(1, 2**18))
        self.assertEqual(row["inside"]["disposition"], "inside")
        self.assertEqual(row["outside"]["disposition"], "outside")
        self.assertGreater(Q(row["outside"]["rayleigh_absolute_lower"]), Q(aos.SPLIT))
        for side in ("inside", "outside"):
            v = row[side]
            self.assertGreater(Q(v["C_min_lower"]), 0)
            self.assertGreater(Q(v["W_min_lower"]), 0)
            self.assertGreater(Q(v["regularity_lower"]), Q(1, 2))
            self.assertLess(Q(v["geometry_upper"]), Q(1, 2))

    def test_continuity_timestep_boundary_without_rebinding_production(self):
        row = EVIDENCE["resource_boundary"] = pressure.resource_boundary(self.d30)
        below, above = row["probes"]
        self.assertGreater(Q(below["C_min_lower"]), 0)
        self.assertLess(Q(above["C_min_upper"]), 0)
        self.assertLess(row["fixed_dt"], below["dt"])
        for value in row["probes"]:
            self.assertLess(Q(value["full_C_error"]), aos.RESOURCE_ERROR)

    def test_floor_certificate_boundary_and_strict_positive_history(self):
        row = EVIDENCE["floor_and_history"] = pressure.floor_and_history_boundaries(
            self.d30
        )
        below, above = row["floor"]
        self.assertGreater(Q(below["smooth_drive_lower"]), Q(1, 2))
        self.assertLess(Q(above["smooth_drive_upper"]), Q(1, 2))
        self.assertEqual(below["disposition"], "certified_inactive_floor")
        self.assertEqual(above["disposition"], "outside_smooth_certificate")
        self.assertTrue(all(x == 0.5 for x in above["clipped_drive"]))
        self.assertTrue(all(x == 0 for x in above["current"]))
        oracle.check_certificate(row["tiny_positive_history"]["certificate"])
        self.assertEqual(len(row["nonpositive_history"]), 2)

    def test_zero_current_is_lawful_and_does_not_freeze_history(self):
        graph = self.d30["target"]["port_graph"]
        base = self.d30["target"]["roles"]["current"]["authoritative"]
        rows = EVIDENCE["zero_current_controls"] = []
        for resource in (0.0, 2.0):
            state = aos.authority([resource] * len(base["C"]), base["W_A"])
            row = oracle.evaluate(
                aos.PaperAOS(graph), state, "zero_current_probe", "current", 1
            )
            output = row["output"]
            self.assertEqual(output["C"], state["C"])
            for name in (
                "current",
                "predictor_current",
                "baseline",
                "predictor_readback",
                "corrector_readback",
            ):
                self.assertTrue(all(x == 0 for x in output[name]))
            self.assertEqual(output["H"], np.eye(len(graph["edges"])).tolist())
            self.assertEqual(output["H"], output["regenerated"])
            self.assertNotEqual(output["W_A"], state["W_A"])
            rows.append(row)

    def test_stage_consumption_catches_substitutions_even_below_output_tolerance(self):
        graph = self.d30["target"]["port_graph"]
        state = self.d30["target"]["roles"]["current"]["authoritative"]
        paper = aos.PaperAOS(graph)
        reads, writes = [], []
        read, write = paper.read, paper.write

        def capture_read(c, w, h=None):
            value = read(c, w, h)
            reads.append(value)
            return value

        def capture_write(c, w, j):
            writes.append({"C": tuple(c), "W_A": tuple(w), "J": tuple(j)})
            return write(c, w, j)

        with (
            patch.object(paper, "read", capture_read),
            patch.object(paper, "write", capture_write),
        ):
            paper.step(state["C"], state["W_A"])
        self.assertEqual(len(reads), 2)
        self.assertEqual(len(writes), 1)
        expected_c = (
            paper.mp.matrix(state["C"])
            - paper.mp.mpf(aos.DT) * paper.B * reads[1]["current"]
        )

        def check_writer(value):
            self.assertEqual(value["C"], tuple(expected_c))
            self.assertEqual(value["W_A"], tuple(state["W_A"]))
            self.assertEqual(value["J"], tuple(reads[1]["current"]))

        check_writer(writes[0])
        for field, wrong in (("C", state["C"]), ("J", reads[0]["current"])):
            mutated = dict(writes[0], **{field: tuple(wrong)})
            with self.assertRaises(AssertionError):
                check_writer(mutated)
        staged = aos.StagedRows(graph["live_node_ids"], graph["edges"], aos.PARAMS)
        _, _, actual = staged.ordinary_os(
            "A", np.array(state["C"]), np.array(state["W_A"])
        )
        check_geometry_stages(actual, len(graph["edges"]))
        wrong = deepcopy(actual)
        wrong["regenerated"] = wrong["H"].copy()
        with self.assertRaisesRegex(
            AssertionError, "regenerated is not assembled from read source"
        ):
            check_geometry_stages(wrong, len(graph["edges"]))
        EVIDENCE["stage_consumption"] = {
            "fixture_id": self.d30["fixture_id"],
            "role": "current",
            "paper_writer_calls": 1,
            "paper_read_calls": 2,
            "writer_final_C_and_corrector_J_exact_operands": True,
            "incoming_C_and_predictor_J_substitutions_rejected": True,
            "staged_regeneration_substitution_rejected": True,
            "scope": "research_evaluator_consumption_only_native_capture_still_required",
        }


if __name__ == "__main__":
    unittest.main()
