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

from grv6_methods import (  # noqa: E402
    branch_current_control,
    canonical_cycle_seed,
    diagnose_boundary_state_candidates,
    deterministic_seed_coordinate,
    evaluate_orbit,
    minimize_return_residual,
    multiplier_continuation_audit,
    oriented_incidence,
    proper_divisors,
)
from pygrc.models import GRC9V3  # noqa: E402
from state_codec import BranchCoordinateChart  # noqa: E402


class GRV6ReturnOrbitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = json.loads(
            (ROOT / "configs/grv6_current_recurrence.json").read_text(encoding="utf-8")
        )
        registry = json.loads(
            (ROOT / "outputs/fixed_branch_registry.json").read_text(encoding="utf-8")
        )["payload"]["branches"]
        cls.homogeneous = next(
            row for row in registry if row["branch_id"] == "grv2-f1-001"
        )
        cls.triangle = next(
            row for row in registry if row["branch_id"] == "grv2-f3-033"
        )
        cls.ill_conditioned = next(
            row for row in registry if row["branch_id"] == "grv2-f1-009"
        )
        cls.boundary = next(
            row for row in registry if row["branch_id"] == "grv2-f1-004"
        )
        cls.homogeneous_model = GRC9V3.load(
            str(REPO_ROOT / cls.homogeneous["state_snapshot_path"])
        )
        cls.triangle_model = GRC9V3.load(
            str(REPO_ROOT / cls.triangle["state_snapshot_path"])
        )
        cls.ill_conditioned_model = GRC9V3.load(
            str(REPO_ROOT / cls.ill_conditioned["state_snapshot_path"])
        )
        cls.boundary_model = GRC9V3.load(
            str(REPO_ROOT / cls.boundary["state_snapshot_path"])
        )

    def test_contract_freezes_complete_search_without_post_outcome_selection(
        self,
    ) -> None:
        self.assertEqual(48, self.config["source_scope"]["expected_branch_count"])
        self.assertEqual([2, 3, 4, 5, 6, 8], self.config["orbit_search"]["periods"])
        self.assertEqual(256, self.config["orbit_search"]["search_budget_per_period"])
        self.assertFalse(
            self.config["source_scope"]["post_outcome_branch_selection_allowed"]
        )
        self.assertFalse(
            self.config["claim_boundary"]["no_orbit_found_is_global_nonexistence_proof"]
        )

    def test_triangle_cycle_seed_is_divergence_free(self) -> None:
        incidence, _, _ = oriented_incidence(self.triangle_model)
        seed = canonical_cycle_seed(
            self.triangle_model,
            rank_tolerance=self.config["edge_space"]["rank_tolerance"],
        )
        self.assertIsNotNone(seed)
        assert seed is not None
        self.assertLess(np.linalg.norm(incidence @ seed), 1e-12)

    def test_cycle_seed_is_overwritten_and_sign_even_control_passes(self) -> None:
        row = branch_current_control(
            self.triangle_model,
            self.triangle["branch_id"],
            self.triangle["fixture_id"],
            self.config,
        )
        self.assertEqual(2, len(row["cycle_seed_rows"]))
        self.assertTrue(
            all(
                cycle["classification"]
                == "cycle_seed_overwritten_by_native_potential_flow"
                for cycle in row["cycle_seed_rows"]
            )
        )
        self.assertTrue(
            row["sign_even_magnitude_matched"]["conductance_write_sign_even"]
        )
        self.assertTrue(row["budget_conservation_passed"])
        self.assertTrue(row["topology_and_noncurrent_categorical_state_clean"])
        self.assertEqual(2, row["edge_space"]["incidence_rank"])
        self.assertEqual(1, row["edge_space"]["cycle_dimension"])
        self.assertLessEqual(
            row["edge_space"]["projected_cycle_gram_condition_number"],
            self.config["edge_space"]["condition_limit"],
        )
        self.assertTrue(
            all(
                cycle["seed_certification"]["certified_before_runtime"]
                for cycle in row["cycle_seed_rows"]
            )
        )
        stage_pair = row["cycle_seed_stage_trace_pair"]
        self.assertIsNotNone(stage_pair)
        assert stage_pair is not None
        self.assertTrue(stage_pair["orientation_overwritten_at_first_transport"])
        self.assertTrue(stage_pair["both_manual_stage_traces_match_complete_step"])
        self.assertTrue(stage_pair["both_transport_kernel_traces_match_public_wrapper"])
        required_stages = {
            "after_first_conductance_formation",
            "after_first_potential_reconstruction",
            "after_first_native_current_reconstruction",
            "after_final_conductance_formation",
            "after_final_potential_reconstruction",
            "after_final_native_current_reconstruction",
        }
        for sign in ("positive", "negative"):
            trace = stage_pair[sign]
            self.assertTrue(trace["both_transport_kernel_traces_match_public_wrapper"])
            self.assertTrue(
                required_stages.issubset({row["stage"] for row in trace["stages"]})
            )
            self.assertTrue(
                trace["first_transport_kernel_audit"][
                    "kernel_vs_public_wrapper_transport_surface_equal"
                ]
            )
            self.assertTrue(
                trace["final_transport_kernel_audit"][
                    "kernel_vs_public_wrapper_transport_surface_equal"
                ]
            )
        self.assertEqual(
            4,
            len(row["cycle_activity_amplitude_ladder"]),
        )
        self.assertTrue(
            all(
                item["quadratic_response_passed"]
                and item["positive_seed_certification"]["certified_before_runtime"]
                and item["negative_seed_certification"]["certified_before_runtime"]
                and not item["budget_projection_changed_state"]
                and not item["conductance_floor_active"]
                and not item["events_or_topology_changed"]
                for item in row["cycle_activity_amplitude_ladder"]
            )
        )
        largest = row["cycle_activity_amplitude_ladder"][-1]
        for sign in ("positive", "negative"):
            certification = largest[f"{sign}_seed_certification"]
            self.assertEqual("satisfied", certification["divergence_gate_status"])
            self.assertEqual("satisfied", certification["cycle_membership_status"])
            self.assertTrue(
                certification["event_eligibility_audit"][
                    "no_event_eligibility_crossing"
                ]
            )
            self.assertLessEqual(
                certification["seed_divergence_l2"],
                certification["seed_divergence_effective_tolerance"],
            )
            self.assertLessEqual(
                certification["cycle_membership_reconstruction_l2"],
                certification["cycle_membership_effective_tolerance"],
            )
            self.assertLessEqual(
                certification["seed_divergence_relative_to_l2"],
                self.config["edge_space"]["seed_divergence_relative_tolerance"],
            )

    def test_generic_activity_seed_marks_cycle_gates_not_applicable(self) -> None:
        row = branch_current_control(
            self.homogeneous_model,
            self.homogeneous["branch_id"],
            self.homogeneous["fixture_id"],
            self.config,
        )
        for item in row["finite_activity_amplitude_ladder"]:
            for sign in ("positive", "negative"):
                certification = item[f"{sign}_seed_certification"]
                self.assertFalse(certification["require_divergence_free"])
                self.assertFalse(certification["require_cycle_membership"])
                self.assertEqual(
                    "not_applicable", certification["divergence_gate_status"]
                )
                self.assertEqual(
                    "not_applicable", certification["cycle_membership_status"]
                )

    def test_blocked_return_search_serializes_condition_diagnostics(self) -> None:
        chart = BranchCoordinateChart.from_model(self.ill_conditioned_model, ("C", "W"))
        seed, _ = deterministic_seed_coordinate(chart, 56, 2, self.config)
        result = minimize_return_residual(chart, seed, 2, self.config)
        self.assertEqual(
            "return_jacobian_ill_conditioned_no_regularization", result["status"]
        )
        diagnostic = result["last_return_jacobian_diagnostic"]
        self.assertIsNotNone(diagnostic)
        assert diagnostic is not None
        self.assertEqual("blocked", diagnostic["condition_gate_result"])
        self.assertFalse(diagnostic["regularization_applied"])
        self.assertGreater(diagnostic["finite_difference_step"], 0.0)
        self.assertTrue(diagnostic["singular_values_descending"])
        self.assertEqual(64, len(diagnostic["jacobian_sha256"]))

    def test_exceptional_search_row_is_replayed_as_boundary_state(self) -> None:
        chart = BranchCoordinateChart.from_model(self.boundary_model, ("C", "W"))
        seed, seed_record = deterministic_seed_coordinate(chart, 243, 8, self.config)
        minimization = minimize_return_residual(chart, seed, 8, self.config)
        self.assertEqual("converged_candidate", minimization["status"])
        source_row = {
            "search_id": "p08-s243",
            "period": 8,
            "candidate_index": 243,
            "branch_id": self.boundary["branch_id"],
            "fixture_id": self.boundary["fixture_id"],
            **seed_record,
            **minimization,
            "evaluation": evaluate_orbit(
                chart,
                np.asarray(minimization["root_coordinate"], dtype=float),
                8,
                self.config,
            ),
        }
        diagnostic = diagnose_boundary_state_candidates(
            [source_row], {source_row["branch_id"]: chart}, self.config
        )
        self.assertEqual(1, diagnostic["candidate_count"])
        row = diagnostic["rows"][0]
        self.assertEqual(
            "budget_projection_supported_current_state", row["classification"]
        )
        self.assertTrue(row["all_replay_modes_equal"])
        self.assertTrue(row["detailed_stage_trace"]["budget_projection_active"])
        self.assertTrue(row["detailed_stage_trace"]["positivity_boundary_active"])
        self.assertTrue(
            row["old_current_reset_control"]["old_current_reset_future_equal"]
        )
        self.assertFalse(row["old_J_independent_causal_state_supported"])
        self.assertFalse(row["T_A05_contradiction_candidate"])
        self.assertFalse(row["return_orbit_evidence_opened"])

    def test_exact_zero_symmetry_is_certified_only_on_F1_control(self) -> None:
        homogeneous = branch_current_control(
            self.homogeneous_model,
            self.homogeneous["branch_id"],
            self.homogeneous["fixture_id"],
            self.config,
        )
        triangle = branch_current_control(
            self.triangle_model,
            self.triangle["branch_id"],
            self.triangle["fixture_id"],
            self.config,
        )
        self.assertEqual(
            "exact_zero_invariant", homogeneous["exact_zero_classification"]
        )
        self.assertTrue(
            homogeneous["exact_zero_symmetry_audit"][
                "full_orientation_relevant_symmetry_certified"
            ]
        )
        self.assertEqual(
            "nonsymmetric_state_zero_input_with_bounded_potential_flow_residual",
            triangle["exact_zero_classification"],
        )
        self.assertFalse(
            triangle["exact_zero_symmetry_audit"][
                "full_orientation_relevant_symmetry_certified"
            ]
        )

    def test_periodic_search_rejects_fixed_point_as_proper_divisor(self) -> None:
        chart = BranchCoordinateChart.from_model(self.homogeneous_model, ("C", "W"))
        coordinate = chart.encode_model(self.homogeneous_model)
        result = evaluate_orbit(chart, coordinate, 2, self.config)
        self.assertTrue(result["physical_return"])
        self.assertFalse(result["primitive_period_supported"])
        self.assertEqual(
            "rejected_proper_divisor_or_period_one_fixed_point",
            result["classification"],
        )
        self.assertEqual([1], proper_divisors(2))
        self.assertEqual([1, 2, 4], proper_divisors(8))

    def test_multiplier_audit_uses_json_null_for_empty_complex_set(self) -> None:
        grv3 = json.loads(
            (ROOT / "outputs/complete_step_jacobians.json").read_text(encoding="utf-8")
        )["payload"]
        audit = multiplier_continuation_audit(grv3, self.config)
        json.dumps(audit, allow_nan=False)
        for row in audit["rows"]:
            if row["complex_multiplier_eligible_count"] == 0:
                self.assertIsNone(row["minimum_complex_unit_circle_distance"])
                self.assertFalse(row["complex_unit_circle_continuation_candidate"])


if __name__ == "__main__":
    unittest.main()
