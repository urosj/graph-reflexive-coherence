from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "src"))

from pygrc.models import GRC9V3  # noqa: E402

from compute_complete_step_jacobian import (  # noqa: E402
    GRV2_RECEIPT_SHA256,
    codec_audit,
    stratum_and_jacobian_audit,
)
from state_codec import BranchCoordinateChart  # noqa: E402


class GRV3CausalStateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = json.loads(
            (ROOT / "configs/grv3_causal_state.json").read_text(encoding="utf-8")
        )
        cls.tolerances = json.loads(
            (ROOT / "configs/numerical_tolerances.json").read_text(encoding="utf-8")
        )
        cls.nonnormal = json.loads(
            (ROOT / "configs/nonnormal_control.json").read_text(encoding="utf-8")
        )
        cls.fast_slow = json.loads(
            (ROOT / "configs/fast_slow_control.json").read_text(encoding="utf-8")
        )
        cls.model = GRC9V3.load(str(ROOT / "outputs/branches/grv2-f1-001.json"))

    def test_branch_scope_is_frozen_before_spectra(self) -> None:
        scope = self.config["branch_scope"]
        self.assertEqual(48, scope["expected_selected_branch_count"])
        self.assertFalse(scope["symmetry_reduction_for_execution"])
        self.assertTrue(scope["symmetry_orbits_are_interpretive_only"])
        self.assertFalse(scope["post_spectrum_branch_selection_allowed"])
        receipt = json.loads(
            (ROOT / "outputs/gates/grv2_result_receipt.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(GRV2_RECEIPT_SHA256, receipt["receipt_payload_sha256"])

    def test_cwj_chart_round_trips_without_aliasing(self) -> None:
        chart = BranchCoordinateChart.from_model(self.model, ("C", "W", "J"))
        coordinate = chart.encode_model(self.model)
        decoded = chart.decode_model(coordinate)
        self.assertTrue(np.array_equal(coordinate, chart.encode_model(decoded)))
        decoded_state = decoded.get_state()
        decoded_state.nodes[chart.node_order[0]].coherence += 0.01
        self.assertNotEqual(
            decoded_state.nodes[chart.node_order[0]].coherence,
            self.model.get_state().nodes[chart.node_order[0]].coherence,
        )

    def test_reference_branch_passes_bounded_cwj_codec(self) -> None:
        chart = BranchCoordinateChart.from_model(self.model, ("C", "W", "J"))
        audit = codec_audit(self.model, chart, self.config, self.tolerances)
        self.assertTrue(audit["bounded_causal_closure_passed"])
        self.assertFalse(audit["global_markov_sufficiency_claimed"])
        self.assertEqual([1, 2, 5, 10], audit["horizons"])

    def test_zero_current_identity_margin_blocks_classical_jacobian(self) -> None:
        chart = BranchCoordinateChart.from_model(self.model, ("C", "W", "J"))
        audit = stratum_and_jacobian_audit(
            self.model,
            chart,
            self.config,
            self.tolerances,
            self.nonnormal,
            self.fast_slow,
        )
        self.assertEqual(
            0.0, audit["baseline_stratum_margins"]["current_sign_identity"]
        )
        self.assertEqual(
            "blocked_non_smooth_stratum",
            audit["square_transition_jacobian_status"],
        )
        self.assertIsNone(audit["jacobian"])
        self.assertTrue(audit["stratum_blocked_is_not_unconverged"])
        self.assertFalse(
            any(row["derivative_column_admitted"] for row in audit["column_audits"])
        )

    def test_p3_manifest_prohibits_runtime_and_existing_test_changes(self) -> None:
        manifest = json.loads(
            (ROOT / "configs/p3_manifest.json").read_text(encoding="utf-8")
        )
        boundaries = manifest["protected_boundaries"]
        self.assertFalse(boundaries["runtime_change_authorized"])
        self.assertFalse(boundaries["src_change_authorized"])
        self.assertFalse(boundaries["existing_test_change_authorized"])

    def test_every_codec_admitted_reduction_must_reach_grv3_b_c(self) -> None:
        contract = self.config["grv3_a"]
        self.assertTrue(
            contract["evaluate_every_codec_admitted_reduction_under_grv3_b_and_grv3_c"]
        )
        self.assertFalse(contract["post_result_primary_coordinate_selection_allowed"])

    def test_spectral_interpretation_thresholds_are_explicit_and_frozen(self) -> None:
        spectral = self.config["grv3_spectral"]
        self.assertEqual(0.9, spectral["stable_slow_minimum_magnitude"])
        self.assertEqual(1e-6, spectral["neutral_magnitude_tolerance"])
        self.assertEqual(1e-6, spectral["eigenvalue_cluster_membership_tolerance"])
        self.assertEqual(1e-8, spectral["invariant_subspace_residual_max"])
        self.assertFalse(spectral["post_result_threshold_adjustment_allowed"])

    def test_nonuniform_reference_admits_reduced_not_full_coordinate(self) -> None:
        model = GRC9V3.load(str(ROOT / "outputs/branches/grv2-f2-017.json"))
        full = BranchCoordinateChart.from_model(model, ("C", "W", "J"))
        reduced = BranchCoordinateChart.from_model(model, ("C", "W"))
        full_result = stratum_and_jacobian_audit(
            model,
            full,
            self.config,
            self.tolerances,
            self.nonnormal,
            self.fast_slow,
        )
        reduced_result = stratum_and_jacobian_audit(
            model,
            reduced,
            self.config,
            self.tolerances,
            self.nonnormal,
            self.fast_slow,
        )
        self.assertEqual(
            "blocked_non_smooth_stratum",
            full_result["square_transition_jacobian_status"],
        )
        self.assertEqual(
            "admitted", reduced_result["square_transition_jacobian_status"]
        )
        self.assertTrue(reduced_result["smooth_response_jacobians"])
        self.assertEqual(
            "computed_and_converged", reduced_result["response_jacobian_status"]
        )
        self.assertTrue(reduced_result["spectral_convergence"]["passed"])
        self.assertEqual(
            0.9,
            reduced_result["spectral_convergence"][
                "subspace_partition_minimum_magnitude"
            ],
        )
        self.assertTrue(reduced_result["temporal_mode_diagnostics"]["modes"])
        self.assertIn(
            "individual_eigenvector_condition_passed",
            reduced_result["temporal_mode_diagnostics"]["nonnormal_control"],
        )
        self.assertIn(
            "status",
            reduced_result["temporal_mode_diagnostics"]["fast_slow_control"],
        )
        self.assertTrue(
            all(
                not mode["retention_interpretation_allowed"]
                for mode in reduced_result["temporal_mode_diagnostics"]["modes"]
            )
        )


if __name__ == "__main__":
    unittest.main()
