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
from sweep_temporal_and_spatial_thresholds import _plain_config  # noqa: E402


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

    def test_claim_ceiling_preserves_full_map_and_global_boundaries(self) -> None:
        claims = self.config["claim_boundary"]
        self.assertFalse(claims["frozen_comparator_is_complete_step_map"])
        self.assertFalse(claims["universal_threshold_identity_may_be_supported"])
        self.assertFalse(
            claims["spatial_hessians_never_correlate_with_temporal_transitions"]
        )
        self.assertFalse(claims["continuation_supported"])
        self.assertFalse(claims["readback_supported"])


if __name__ == "__main__":
    unittest.main()
