from __future__ import annotations

from types import SimpleNamespace
import unittest

from pygrc.landscapes import (
    LandscapeInferenceWindow,
    audit_checkpoint_budget,
    build_landscape_inference_checkpoint_graph,
    build_landscape_inference_evidence_substrate,
    extract_landscape_inference_candidate_paths,
    summarize_landscape_inference_path_flux_stability,
    summarize_landscape_inference_path_persistence,
)
from pygrc.telemetry.schema import GraphCheckpointArtifact, RunTelemetryIdentity


def _identity() -> RunTelemetryIdentity:
    return RunTelemetryIdentity(
        run_id="substrate_run",
        model_family="grc9v3",
        params_identity="params",
    )


def _checkpoint(
    *,
    checkpoint_id: str,
    step_index: int,
    node_ids: tuple[int, ...] = (1, 2, 3),
    include_edge_2_3: bool = True,
    bridge_in_payload: bool = True,
    bridge_in_extension: bool = False,
) -> GraphCheckpointArtifact:
    edge_records: list[dict[str, object]] = [
        {
            "edge_id": 11,
            "source_node_id": 1,
            "source_port_id": 1,
            "target_node_id": 2,
            "target_port_id": 2,
            "conductance": 4.0,
            "signed_flux": 2.0,
            "geometric_length": 3.0,
            "payload": {
                "grcl9v3_source_construct_id": "source_a",
                "temporal_delay": 4.0,
                **({"grcl9v3_edge_kind": "bridge"} if bridge_in_payload else {}),
            },
        }
    ]
    if include_edge_2_3:
        edge_records.append(
            {
                "edge_id": 12,
                "source_node_id": 2,
                "source_port_id": 3,
                "target_node_id": 3,
                "target_port_id": 4,
                "conductance": 1.5,
                "signed_flux": 1.0,
                "payload": {"grcl9v3_motif_id": "motif_a", "flux_coupling": 0.75},
            }
        )
    return GraphCheckpointArtifact(
        identity=_identity(),
        checkpoint_id=checkpoint_id,
        step_index=step_index,
        time=float(step_index),
        checkpoint_label=f"step_{step_index}",
        checkpoint_reason="test",
        graph_kind="port_graph",
        node_count=len(node_ids),
        edge_count=len(edge_records),
        node_records=tuple(
            {
                "node_id": node_id,
                "coherence": float(node_id),
                "quadrature_weight": 2.0 if node_id == 1 else 1.0,
                "sink_flag": node_id == 1,
                "basin_id": "1" if node_id in (1, 2) else "3",
                "basin_mass": 2.5 if node_id == 1 else 1.0,
                "parent_id": None if node_id == 1 else 1,
                "depth": 0 if node_id == 1 else 1,
                **({"gradient_norm": 0.01} if node_id == 1 else {}),
                **({"signed_hessian_row_basis": [0.2, 0.4, 0.3]} if node_id == 2 else {}),
                **({"tensor": [[2.0, 0.0], [0.0, 5.0]]} if node_id == 3 else {}),
                "payload": {
                    "grcl9v3_source_construct_id": f"node_source_{node_id}",
                    "grcl9v3_motif_id": "motif_a",
                    **({"tensor_anisotropy": 0.25} if node_id == 2 else {}),
                },
            }
            for node_id in node_ids
        ),
        edge_records=tuple(edge_records),
        family_extensions={
            "grc9v3": {
                "contract_version": "test",
                "port_overlay": {
                    "by_node": {
                        "1": {"occupied_ports": [1, 5, 9], "free_ports": [2]},
                        "2": {"occupied_ports": [3], "free_ports": [1, 2]},
                    }
                },
                "node_overlay": {
                    "3": {"min_signed_hessian": 0.05},
                },
                "edge_overlay": {
                    "12": {"geometric_length": 5.0, "temporal_delay": 6.0},
                },
            },
            "grcl9v3": {
                "bridge_edge_ids": [11] if bridge_in_extension else [],
            },
            "grc9": {
                "budget_target": 7.0,
            },
        },
    )


class LandscapeInferenceSubstrateTest(unittest.TestCase):
    def test_checkpoint_graph_normalizes_adjacency_ports_provenance_and_bridge_tags(self) -> None:
        graph = build_landscape_inference_checkpoint_graph(_checkpoint(checkpoint_id="c1", step_index=1))

        self.assertEqual((2,), graph.adjacency[1])
        self.assertEqual((1, 3), graph.adjacency[2])
        self.assertEqual((11,), graph.bridge_edge_ids)
        self.assertIn("source_tag", graph.bridge_detection_modes)
        self.assertTrue(graph.port_matrix_available)
        self.assertTrue(graph.nodes[1].port_matrix[0][0])
        self.assertTrue(graph.nodes[1].port_matrix[1][1])
        self.assertTrue(graph.nodes[1].port_matrix[2][2])
        self.assertTrue(graph.provenance_available)
        self.assertEqual("source_a", graph.edges[11].provenance["grcl9v3_source_construct_id"])
        self.assertTrue(graph.nodes[1].sink_flag)
        self.assertEqual("1", graph.nodes[1].basin_id)
        self.assertEqual(2.5, graph.nodes[1].basin_mass)
        self.assertEqual("1", graph.nodes[2].parent_id)
        self.assertEqual(1, graph.nodes[2].depth)
        self.assertEqual(0.01, graph.nodes[1].gradient_norm)
        self.assertEqual(0.2, graph.nodes[2].min_signed_hessian)
        self.assertEqual(7.0, graph.nodes[3].tensor_trace)
        self.assertEqual(3.0, graph.nodes[3].tensor_anisotropy)
        self.assertEqual(3.0, graph.edges[11].geometric_length)
        self.assertEqual(4.0, graph.edges[11].temporal_delay)
        self.assertEqual(5.0, graph.edges[12].geometric_length)
        self.assertEqual(6.0, graph.edges[12].temporal_delay)
        self.assertEqual(0.75, graph.edges[12].flux_coupling)

    def test_bridge_detection_uses_family_extension_when_payload_tag_is_absent(self) -> None:
        graph = build_landscape_inference_checkpoint_graph(
            _checkpoint(
                checkpoint_id="c1",
                step_index=1,
                bridge_in_payload=False,
                bridge_in_extension=True,
            )
        )

        self.assertEqual((11,), graph.bridge_edge_ids)
        self.assertEqual("family_extension", graph.edges[11].bridge_detection_mode)

    def test_candidate_paths_compute_aggregates_and_can_exclude_bridge_paths(self) -> None:
        graph = build_landscape_inference_checkpoint_graph(_checkpoint(checkpoint_id="c1", step_index=1))

        paths = extract_landscape_inference_candidate_paths(graph, (1,), (3,))
        self.assertEqual(1, len(paths))
        path = paths[0]
        self.assertEqual((1, 2, 3), path.node_ids)
        self.assertEqual((11, 12), path.edge_ids)
        self.assertEqual(1.5, path.bottleneck_conductance)
        self.assertEqual(3.0, path.total_abs_flux)
        self.assertEqual((11,), path.bridge_edge_ids)

        no_bridge_paths = extract_landscape_inference_candidate_paths(
            graph,
            (1,),
            (3,),
            include_bridge_paths=False,
        )
        self.assertEqual((), no_bridge_paths)

    def test_path_persistence_detects_rupture_across_checkpoint_window(self) -> None:
        load_result = SimpleNamespace(
            source_runtime_family="grc9v3",
            inference_window=LandscapeInferenceWindow(
                start_step=0,
                end_step=2,
                policy="whole_run",
            ),
            telemetry_pack=SimpleNamespace(
                graph_checkpoints=(
                    _checkpoint(checkpoint_id="c0", step_index=0),
                    _checkpoint(checkpoint_id="c1", step_index=1, include_edge_2_3=False),
                    _checkpoint(checkpoint_id="c2", step_index=2, node_ids=(1, 2), include_edge_2_3=False),
                )
            ),
        )
        substrate = build_landscape_inference_evidence_substrate(load_result)

        persistence = summarize_landscape_inference_path_persistence(substrate, (1, 2, 3))

        self.assertFalse(substrate.diagnostic_only)
        self.assertEqual(3, persistence.checkpoint_count)
        self.assertEqual(1, persistence.present_count)
        self.assertEqual(2, persistence.ruptured_count)
        self.assertEqual((3,), persistence.missing_node_ids)
        self.assertIn((2, 3), persistence.missing_edge_pairs)

    def test_path_flux_stability_scores_repeated_checkpoint_flux(self) -> None:
        load_result = SimpleNamespace(
            source_runtime_family="grc9v3",
            inference_window=LandscapeInferenceWindow(
                start_step=0,
                end_step=2,
                policy="whole_run",
            ),
            telemetry_pack=SimpleNamespace(
                graph_checkpoints=(
                    _checkpoint(checkpoint_id="c0", step_index=0),
                    _checkpoint(checkpoint_id="c1", step_index=1),
                    _checkpoint(checkpoint_id="c2", step_index=2),
                )
            ),
        )
        substrate = build_landscape_inference_evidence_substrate(load_result)

        stability = summarize_landscape_inference_path_flux_stability(substrate, (1, 2, 3))

        self.assertEqual(3, stability.checkpoint_count)
        self.assertEqual(3, stability.observed_count)
        self.assertEqual(1.0, stability.observed_fraction)
        self.assertEqual((3.0, 3.0, 3.0), stability.flux_series)
        self.assertEqual(3.0, stability.mean_abs_flux)
        self.assertEqual(1.0, stability.stability_score)
        self.assertEqual("stable_repeated_flux", stability.stability_mode)

    def test_short_checkpoint_series_is_diagnostic_only_by_default(self) -> None:
        load_result = SimpleNamespace(
            source_runtime_family="grc9v3",
            inference_window=LandscapeInferenceWindow(start_step=0, end_step=1, policy="whole_run"),
            telemetry_pack=SimpleNamespace(
                graph_checkpoints=(
                    _checkpoint(checkpoint_id="c0", step_index=0),
                    _checkpoint(checkpoint_id="c1", step_index=1),
                )
            ),
        )

        substrate = build_landscape_inference_evidence_substrate(load_result)

        self.assertTrue(substrate.diagnostic_only)

    def test_budget_audit_uses_checkpoint_weights_and_reports_error(self) -> None:
        audit = audit_checkpoint_budget(_checkpoint(checkpoint_id="c1", step_index=1))

        self.assertTrue(audit.budget_available)
        self.assertEqual("checkpoint_weight", audit.quadrature_weight_mode)
        self.assertEqual(7.0, audit.budget_sum)
        self.assertEqual(7.0, audit.budget_target)
        self.assertEqual(0.0, audit.budget_error)
        self.assertEqual("conserved_zero", audit.budget_accountability)


if __name__ == "__main__":
    unittest.main()
