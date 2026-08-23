from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from branch_continuation import (  # noqa: E402
    branch_match_record,
    classify_discrete_spectrum,
    match_real_invariant_clusters,
)
from sweep_temporal_and_spatial_thresholds import (  # noqa: E402
    _ce1_threshold_separation,
    _selected_source_branch_path_map,
    _plain_config,
)


class GRV7SpatialTemporalThresholdTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = json.loads(
            (ROOT / "configs/grv7_spatial_temporal_thresholds.json").read_text(
                encoding="utf-8"
            )
        )

    def test_paths_and_selection_are_frozen_before_spectra(self) -> None:
        self.assertEqual(6, len(self.config["paths"]))
        self.assertEqual(
            48, self.config["source_scope"]["expected_source_branch_count"]
        )
        self.assertFalse(
            self.config["source_scope"][
                "post_spectrum_branch_or_path_selection_allowed"
            ]
        )
        path_ids = {row["path_id"] for row in self.config["paths"]}
        self.assertIn("F1_scale_structural_path", path_ids)
        self.assertIn("F1_dt_flip_path", path_ids)
        self.assertIn("F2_dt_nonuniform_path", path_ids)
        self.assertIn("F3_eta_nonuniform_path", path_ids)

    def test_branch_match_fails_closed_on_topology_or_state_change(self) -> None:
        valid = branch_match_record(
            previous_nodes=[0, 1],
            current_nodes=[0, 1],
            previous_edges=[0],
            current_edges=[0],
            previous_coherence=[2.0, 2.0],
            current_coherence=[2.0, 2.0],
            previous_total=4.0,
            current_total=4.0,
            maximum_state_l2=1e-8,
            maximum_total_delta=1e-10,
        )
        self.assertTrue(valid["passed"])
        topology = branch_match_record(
            previous_nodes=[0, 1],
            current_nodes=[0, 1, 2],
            previous_edges=[0],
            current_edges=[0, 1],
            previous_coherence=[2.0, 2.0],
            current_coherence=[2.0, 2.0, 0.0],
            previous_total=4.0,
            current_total=4.0,
            maximum_state_l2=1e-8,
            maximum_total_delta=1e-10,
        )
        self.assertFalse(topology["passed"])
        state = branch_match_record(
            previous_nodes=[0, 1],
            current_nodes=[0, 1],
            previous_edges=[0],
            current_edges=[0],
            previous_coherence=[2.0, 2.0],
            current_coherence=[1.9, 2.1],
            previous_total=4.0,
            current_total=4.0,
            maximum_state_l2=1e-8,
            maximum_total_delta=1e-10,
        )
        self.assertFalse(state["passed"])

    def test_nested_immutable_parameter_mapping_is_thawed(self) -> None:
        from types import MappingProxyType

        source = MappingProxyType(
            {"dt": 0.1, "evolution": MappingProxyType({"eta": 0.5})}
        )
        thawed = _plain_config(source)
        self.assertEqual({"dt": 0.1, "evolution": {"eta": 0.5}}, thawed)
        thawed["evolution"]["eta"] = 1.0
        self.assertEqual(0.5, source["evolution"]["eta"])

    def test_real_invariant_cluster_matching_ignores_index_order(self) -> None:
        match = match_real_invariant_clusters(
            [0.4 + 0.3j, 0.4 - 0.3j, 0.8 + 0j],
            [0.8 + 0j, 0.41 - 0.3j, 0.41 + 0.3j],
            complex_pair_tolerance=1e-8,
            maximum_centroid_distance=0.02,
        )
        self.assertTrue(match["passed"])
        self.assertEqual(2, match["previous_cluster_count"])

    def test_threshold_classification_keeps_distinct_surfaces(self) -> None:
        thresholds = self.config["thresholds"]
        kwargs = {
            "threshold_tolerance": thresholds["discrete_multiplier_tolerance"],
            "complex_imaginary_floor": thresholds["complex_imaginary_floor"],
        }
        self.assertTrue(
            classify_discrete_spectrum([1.0 + 0j], **kwargs)["plus_one_reached"]
        )
        self.assertTrue(
            classify_discrete_spectrum([0.5 + 0j], **kwargs)[
                "stable_interior_reached"
            ]
        )
        self.assertTrue(
            classify_discrete_spectrum([-1.0 + 0j], **kwargs)["minus_one_reached"]
        )
        self.assertTrue(
            classify_discrete_spectrum([0.0 + 1.0j, 0.0 - 1.0j], **kwargs)[
                "complex_unit_circle_reached"
            ]
        )

    def test_load_bearing_operator_contract_is_typed(self) -> None:
        self.assertEqual(
            [
                "operator_identity",
                "branch_identity",
                "reduction_validity",
                "critical_subspace_identity",
                "uncertainty_separated_threshold_relation",
                "categorical_boundary_separation",
            ],
            self.config["scientific_discriminator_priority"],
        )
        operators = self.config["operator_contract"]
        self.assertEqual(
            {
                "H_row",
                "H_signed",
                "H_WLS",
                "H_cont_W_star",
                "A_W_H_cont_W_star",
                "A_full",
            },
            {key for key in operators if not key.endswith("allowed") and key != "cross_operator_comparison_requires_common_domain_or_declared_embedding"},
        )
        for operator_id in (
            "H_row",
            "H_signed",
            "H_WLS",
            "H_cont_W_star",
            "A_W_H_cont_W_star",
            "A_full",
        ):
            self.assertEqual(
                {"domain", "metric", "sign_convention", "threshold_rule"},
                set(operators[operator_id]),
            )
        self.assertFalse(operators["cross_operator_eigenvalue_index_pairing_allowed"])

    def test_reduction_contract_does_not_invent_current_slaving(self) -> None:
        contract = self.config["reduction_admissibility_contract"]
        self.assertEqual(
            "clamped_counterfactual_not_current_slaving",
            contract["frozen_W_comparator_kind"],
        )
        self.assertFalse(contract["current_slaving_used"])
        self.assertEqual(
            "not_applicable_no_current_slaving_or_feedback_elimination",
            contract["I_minus_B_eff_invertibility_requirement"],
        )
        self.assertEqual(
            "comparison_blocked_not_threshold_disagreement",
            contract["failed_reduction_or_stratum_gate_classification"],
        )

    def test_ce1_separation_uses_nearest_off_threshold_witnesses(self) -> None:
        rows = []
        for eigenvalue, multiplier in (
            (-2.0, 1.4),
            (-1.0, 1.2),
            (0.0, 1.0),
            (1.0, 0.8),
            (2.0, 0.6),
        ):
            rows.append(
                {
                    "analytical_continuation_hessian": {
                        "eigenvalues": [eigenvalue]
                    },
                    "frozen_W_temporal_comparator": {
                        "multipliers": [
                            {"real": multiplier, "imag": 0.0}
                        ]
                    },
                }
            )
        audit = _ce1_threshold_separation(rows, self.config)
        self.assertTrue(audit["passed"])
        self.assertAlmostEqual(
            1.0 - self.config["thresholds"]["spatial_zero_tolerance"],
            audit["minimum_off_threshold_separation_margin"],
        )

    def test_decisive_subspace_claim_is_exactly_one_dimensional(self) -> None:
        matrix = json.loads(
            (ROOT / "outputs/spatial_temporal_threshold_matrix.json").read_text(
                encoding="utf-8"
            )
        )["payload"]
        path_by_id = {row["path_id"]: row for row in matrix["path_rows"]}
        decisive = [
            row
            for row in matrix["counterexamples"]
            if row.get("status") == "supported"
        ]
        self.assertEqual(2, len(decisive))
        for counterexample in decisive:
            audit = counterexample["critical_subspace_audit"]
            self.assertEqual(1, audit["critical_subspace_dimension"])
            self.assertEqual(0.0, audit["principal_angle_radians"])
            self.assertEqual(0.0, audit["projector_distance_l2"])
            for row in path_by_id[counterexample["path_id"]]["primary_points"]:
                self.assertEqual(
                    1,
                    len(row["analytical_continuation_hessian"]["eigenvalues"]),
                )
                self.assertEqual(
                    1,
                    len(row["frozen_W_temporal_comparator"]["multipliers"]),
                )

    def test_claim_ceiling_preserves_full_map_and_global_boundaries(self) -> None:
        claims = self.config["claim_boundary"]
        self.assertFalse(claims["frozen_comparator_is_complete_step_map"])
        self.assertTrue(
            claims[
                "reduced_spatial_continuation_temporal_non_equivalence_may_be_supported"
            ]
        )
        self.assertFalse(
            claims[
                "runtime_spatial_vs_full_temporal_non_equivalence_may_be_supported"
            ]
        )
        self.assertFalse(claims["universal_threshold_identity_may_be_supported"])
        self.assertFalse(
            claims["spatial_hessians_never_correlate_with_temporal_transitions"]
        )
        self.assertFalse(claims["continuation_supported"])
        self.assertFalse(claims["readback_supported"])

    def test_all_selected_source_branches_have_explicit_path_roles(self) -> None:
        mapping = _selected_source_branch_path_map(self.config)
        self.assertEqual(7, len(mapping))
        self.assertTrue(all(row["fully_accounted"] for row in mapping))
        by_id = {row["source_branch_id"]: row for row in mapping}
        self.assertEqual(
            {"F2_dt_nonuniform_path", "F2_eta_nonuniform_path"},
            {use["path_id"] for use in by_id["grv2-f2-018"]["path_uses"]},
        )
        self.assertTrue(
            all(
                use["role"] == "symmetry_partner"
                for use in by_id["grv2-f2-018"]["path_uses"]
            )
        )


if __name__ == "__main__":
    unittest.main()
