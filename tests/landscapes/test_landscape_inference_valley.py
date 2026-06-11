from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import unittest

from pygrc.landscapes import (
    LandscapeInferenceWindow,
    build_landscape_inference_evidence_substrate,
    build_minimal_landscape_inference_seed,
    classify_landscape_valley_candidates,
    infer_landscape_valley_seed,
    select_emitted_landscape_valley_candidates,
    validate_landscape_inference_seed_extensions,
    validate_landscape_seed,
)
from pygrc.telemetry.schema import (
    GraphCheckpointArtifact,
    RunTelemetryIdentity,
    RunTelemetrySummary,
)


def _identity() -> RunTelemetryIdentity:
    return RunTelemetryIdentity(
        run_id="valley_run",
        model_family="grc9v3",
        params_identity="params",
        requested_steps=3,
    )


def _summary(identity: RunTelemetryIdentity) -> RunTelemetrySummary:
    return RunTelemetrySummary(
        identity=identity,
        completed_steps=3,
        final_step_index=2,
        initial_time=0.0,
        final_time=0.2,
        total_event_count=0,
        event_counts_by_kind={},
        initial_observables={},
        final_observables={},
        resolved_params={"evolution": {"dt": 0.1}},
        family_extensions={"grc9v3": {"contract_version": "test"}},
    )


def _checkpoint(
    *,
    checkpoint_id: str,
    step_index: int,
    include_edge_2_3: bool = True,
    bridge_edge_ids: tuple[int, ...] = (),
    node_2_basin: str | None = None,
) -> GraphCheckpointArtifact:
    edge_records: list[dict[str, object]] = [
        {
            "edge_id": 11,
            "source_node_id": 1,
            "target_node_id": 2,
            "conductance": 2.0,
            "signed_flux": 1.0,
            "geometric_length": 1.5,
            "temporal_delay": 0.25,
            "flux_coupling": 0.75,
            "payload": {"grcl9v3_edge_kind": "bridge"} if 11 in bridge_edge_ids else {},
        }
    ]
    if include_edge_2_3:
        edge_records.append(
            {
                "edge_id": 12,
                "source_node_id": 2,
                "target_node_id": 3,
                "conductance": 1.25,
                "signed_flux": 0.5,
                "geometric_length": 2.0,
                "temporal_delay": 0.5,
                "flux_coupling": 0.5,
                "payload": {"grcl9v3_edge_kind": "bridge"} if 12 in bridge_edge_ids else {},
            }
        )
    node_2_record: dict[str, object] = {
        "node_id": 2,
        "coherence": 0.5,
    }
    if node_2_basin is not None:
        node_2_record.update(
            {
                "basin_id": node_2_basin,
                "sink_flag": True,
                "basin_mass": 0.5,
            }
        )
    return GraphCheckpointArtifact(
        identity=_identity(),
        checkpoint_id=checkpoint_id,
        step_index=step_index,
        time=float(step_index) * 0.1,
        checkpoint_label=f"step_{step_index}",
        checkpoint_reason="valley_test",
        graph_kind="weighted_graph",
        node_count=3,
        edge_count=len(edge_records),
        node_records=(
            {
                "node_id": 1,
                "coherence": 2.0,
                "sink_flag": True,
                "basin_id": "1",
                "basin_mass": 2.0,
            },
            node_2_record,
            {
                "node_id": 3,
                "coherence": 3.0,
                "sink_flag": True,
                "basin_id": "3",
                "basin_mass": 3.0,
            },
        ),
        edge_records=tuple(edge_records),
        family_extensions={"grc9v3": {"contract_version": "test"}},
    )


def _load_result(
    checkpoints: tuple[GraphCheckpointArtifact, ...],
) -> SimpleNamespace:
    identity = _identity()
    pack = SimpleNamespace(
        run_summary=_summary(identity),
        step_rows=(),
        event_rows=(),
        graph_checkpoints=checkpoints,
        graph_checkpoint_index=None,
    )
    window = LandscapeInferenceWindow(start_step=0, end_step=2, policy="whole_run")
    root = Path("outputs") / "grc9v3" / "landscape_inference" / "sessions" / "S0004"
    return SimpleNamespace(
        artifact_root=root,
        telemetry_pack=pack,
        source_runtime_family="grc9v3",
        inference_window=window,
        inferred_seed=build_minimal_landscape_inference_seed(
            pack,
            artifact_root=root,
            source_runtime_family="grc9v3",
            inference_window=window,
        ),
    )


def _substrate(
    checkpoints: tuple[GraphCheckpointArtifact, ...],
):
    return build_landscape_inference_evidence_substrate(_load_result(checkpoints))


class LandscapeInferenceValleyTest(unittest.TestCase):
    def test_valley_classifier_accepts_persistent_flux_path_between_basins(self) -> None:
        substrate = _substrate(
            (
                _checkpoint(checkpoint_id="c0", step_index=0),
                _checkpoint(checkpoint_id="c1", step_index=1),
                _checkpoint(checkpoint_id="c2", step_index=2),
            )
        )

        candidates = classify_landscape_valley_candidates(substrate, runtime_family="grc9v3")

        self.assertEqual(1, len(candidates))
        candidate = candidates[0]
        self.assertEqual("accepted", candidate.status)
        self.assertEqual("1", candidate.from_basin_id)
        self.assertEqual("3", candidate.to_basin_id)
        self.assertEqual((1, 2, 3), candidate.path_node_ids)
        self.assertEqual((11, 12), candidate.path_edge_ids)
        self.assertEqual(1.25, candidate.bottleneck_conductance)
        self.assertEqual(1.5, candidate.total_abs_flux)
        self.assertEqual(3, candidate.persistence_steps)
        self.assertEqual(3.5, candidate.total_geometric_length)
        self.assertEqual(0.75, candidate.total_temporal_delay)
        self.assertEqual(0.625, candidate.mean_flux_coupling)
        self.assertEqual("none", candidate.bridge_ambiguity_tier)
        self.assertEqual(3, candidate.flux_observed_steps)
        self.assertEqual(1.0, candidate.flux_observed_fraction)
        self.assertGreater(candidate.flux_stability_score, 0.0)
        self.assertEqual("stable_repeated_flux", candidate.flux_stability_mode)
        self.assertGreater(candidate.significance_score, 0.0)
        self.assertGreater(candidate.ranking_score, 0.0)
        self.assertEqual(
            "status>non_bridge>significance>persistence>"
            "flux_stability>flux_support>bottleneck_conductance>shorter_path",
            candidate.ranking_reason,
        )
        self.assertEqual("1__3", candidate.deduplication_group_id)
        self.assertFalse(candidate.emitted)

    def test_valley_classifier_rejects_bridge_only_path(self) -> None:
        substrate = _substrate(
            (
                _checkpoint(checkpoint_id="c0", step_index=0, bridge_edge_ids=(11, 12)),
                _checkpoint(checkpoint_id="c1", step_index=1, bridge_edge_ids=(11, 12)),
                _checkpoint(checkpoint_id="c2", step_index=2, bridge_edge_ids=(11, 12)),
            )
        )

        candidates = classify_landscape_valley_candidates(substrate, runtime_family="grc9v3")

        self.assertEqual(1, len(candidates))
        self.assertEqual("rejected", candidates[0].status)
        self.assertEqual("bridge_only_path", candidates[0].rejection_reason)
        self.assertEqual("bridge_only", candidates[0].bridge_ambiguity_tier)
        self.assertEqual((11, 12), candidates[0].bridge_edge_ids)

    def test_valley_classifier_records_path_rupture(self) -> None:
        substrate = _substrate(
            (
                _checkpoint(checkpoint_id="c0", step_index=0),
                _checkpoint(checkpoint_id="c1", step_index=1, include_edge_2_3=False),
                _checkpoint(checkpoint_id="c2", step_index=2),
            )
        )

        candidates = classify_landscape_valley_candidates(substrate, runtime_family="grc9v3")

        self.assertEqual(1, len(candidates))
        self.assertEqual("rejected", candidates[0].status)
        self.assertEqual("path_ruptured_across_window", candidates[0].rejection_reason)
        self.assertEqual(1, candidates[0].ruptured_count)
        self.assertIn((2, 3), candidates[0].missing_edge_pairs)

    def test_valley_classifier_rejects_stable_basin_interior(self) -> None:
        substrate = _substrate(
            (
                _checkpoint(checkpoint_id="c0", step_index=0, node_2_basin="2"),
                _checkpoint(checkpoint_id="c1", step_index=1, node_2_basin="2"),
                _checkpoint(checkpoint_id="c2", step_index=2, node_2_basin="2"),
            )
        )

        candidates = classify_landscape_valley_candidates(substrate, runtime_family="grc9v3")
        candidate = next(
            item for item in candidates if item.from_basin_id == "1" and item.to_basin_id == "3"
        )

        self.assertEqual("rejected", candidate.status)
        self.assertEqual("stable_basin_interior_on_path", candidate.rejection_reason)
        self.assertEqual((2,), candidate.intermediate_basin_node_ids)

    def test_valley_seed_emission_validates(self) -> None:
        load_result = _load_result(
            (
                _checkpoint(checkpoint_id="c0", step_index=0),
                _checkpoint(checkpoint_id="c1", step_index=1),
                _checkpoint(checkpoint_id="c2", step_index=2),
            )
        )
        substrate = build_landscape_inference_evidence_substrate(load_result)

        seed = infer_landscape_valley_seed(load_result, substrate=substrate)

        validate_landscape_seed(seed)
        validate_landscape_inference_seed_extensions(seed)
        self.assertEqual(3, len(seed.primitives))
        valley = seed.primitives[-1]
        self.assertEqual("valley", valley.type)
        self.assertEqual("valley_channel", valley.role)
        self.assertEqual("observed_basin_1", valley.from_id)
        self.assertEqual("observed_basin_3", valley.to_id)
        inference = valley.extensions["landscape_inference"]
        self.assertEqual("observed", inference["authority"])
        self.assertEqual([11, 12], inference["evidence"]["edge_ids"])
        self.assertEqual([1, 2, 3], inference["evidence"]["path_node_ids"])
        self.assertEqual(1, seed.extensions["landscape_inference_valley_summary"]["observed_valley_count"])
        self.assertEqual(
            1,
            seed.extensions["landscape_inference_valley_summary"]["raw_accepted_candidate_count"],
        )
        self.assertTrue(valley.extensions["landscape_inference_valley"]["emitted"])

    def test_deduplication_keeps_stronger_path_per_endpoint_pair(self) -> None:
        checkpoint = GraphCheckpointArtifact(
            identity=_identity(),
            checkpoint_id="c0",
            step_index=0,
            time=0.0,
            checkpoint_label="step_0",
            checkpoint_reason="valley_test",
            graph_kind="weighted_graph",
            node_count=4,
            edge_count=4,
            node_records=(
                {"node_id": 1, "coherence": 1.0, "sink_flag": True, "basin_id": "1"},
                {"node_id": 2, "coherence": 1.0},
                {"node_id": 3, "coherence": 1.0, "sink_flag": True, "basin_id": "3"},
                {"node_id": 4, "coherence": 1.0},
            ),
            edge_records=(
                {
                    "edge_id": 11,
                    "source_node_id": 1,
                    "target_node_id": 2,
                    "conductance": 1.0,
                    "signed_flux": 0.2,
                },
                {
                    "edge_id": 12,
                    "source_node_id": 2,
                    "target_node_id": 3,
                    "conductance": 1.0,
                    "signed_flux": 0.2,
                },
                {
                    "edge_id": 13,
                    "source_node_id": 1,
                    "target_node_id": 4,
                    "conductance": 2.0,
                    "signed_flux": 2.0,
                },
                {
                    "edge_id": 14,
                    "source_node_id": 4,
                    "target_node_id": 3,
                    "conductance": 2.0,
                    "signed_flux": 2.0,
                },
            ),
            family_extensions={"grc9v3": {"contract_version": "test"}},
        )
        load_result = _load_result(
            (
                checkpoint,
                GraphCheckpointArtifact(**{**checkpoint.__dict__, "checkpoint_id": "c1", "step_index": 1}),
                GraphCheckpointArtifact(**{**checkpoint.__dict__, "checkpoint_id": "c2", "step_index": 2}),
            )
        )
        substrate = build_landscape_inference_evidence_substrate(load_result)
        candidates = classify_landscape_valley_candidates(substrate, runtime_family="grc9v3")

        accepted = tuple(candidate for candidate in candidates if candidate.status == "accepted")
        emitted = select_emitted_landscape_valley_candidates(candidates)
        seed = infer_landscape_valley_seed(load_result, substrate=substrate)

        self.assertGreater(len(accepted), 1)
        self.assertEqual(1, len(emitted))
        self.assertEqual((1, 4, 3), emitted[0].path_node_ids)
        self.assertTrue(emitted[0].emitted)
        self.assertEqual(3, len(seed.primitives))
        self.assertEqual(
            len(accepted) - 1,
            seed.extensions["landscape_inference_valley_summary"]["deduplicated_candidate_count"],
        )


if __name__ == "__main__":
    unittest.main()
