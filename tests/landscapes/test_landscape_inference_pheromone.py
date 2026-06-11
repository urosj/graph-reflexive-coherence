from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import unittest

from pygrc.landscapes import (
    LandscapeInferenceWindow,
    build_landscape_inference_evidence_substrate,
    build_minimal_landscape_inference_seed,
    classify_landscape_pheromone_candidates,
    infer_landscape_pheromone_seed,
    validate_landscape_inference_seed_extensions,
    validate_landscape_seed,
)
from pygrc.telemetry.schema import (
    EventTelemetryRow,
    GraphCheckpointArtifact,
    RunTelemetryIdentity,
    RunTelemetrySummary,
)


def _identity() -> RunTelemetryIdentity:
    return RunTelemetryIdentity(
        run_id="pheromone_run",
        model_family="grc9v3",
        params_identity="params",
        requested_steps=4,
    )


def _summary(identity: RunTelemetryIdentity) -> RunTelemetrySummary:
    return RunTelemetrySummary(
        identity=identity,
        completed_steps=4,
        final_step_index=3,
        initial_time=0.0,
        final_time=0.3,
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
    flux: float = 0.5,
    conductance: float = 1.0,
    include_edge: bool = True,
    bridge: bool = False,
    stable_interior: bool = False,
) -> GraphCheckpointArtifact:
    node_2: dict[str, object] = {"node_id": 2, "coherence": 0.5}
    if stable_interior:
        node_2.update({"sink_flag": True, "basin_id": "2", "basin_mass": 0.5})
    edges: list[dict[str, object]] = [
        {
            "edge_id": 11,
            "source_node_id": 1,
            "target_node_id": 2,
            "conductance": conductance,
            "signed_flux": flux,
            "payload": {"grcl9v3_edge_kind": "bridge"} if bridge else {},
        }
    ]
    if include_edge:
        edges.append(
            {
                "edge_id": 12,
                "source_node_id": 2,
                "target_node_id": 3,
                "conductance": conductance,
                "signed_flux": flux,
                "payload": {"grcl9v3_edge_kind": "bridge"} if bridge else {},
            }
        )
    return GraphCheckpointArtifact(
        identity=_identity(),
        checkpoint_id=checkpoint_id,
        step_index=step_index,
        time=float(step_index) * 0.1,
        checkpoint_label=f"step_{step_index}",
        checkpoint_reason="pheromone_test",
        graph_kind="weighted_graph",
        node_count=3,
        edge_count=len(edges),
        node_records=(
            {
                "node_id": 1,
                "coherence": 1.0,
                "sink_flag": True,
                "basin_id": "1",
                "basin_mass": 1.0,
            },
            node_2,
            {
                "node_id": 3,
                "coherence": 1.0,
                "sink_flag": True,
                "basin_id": "3",
                "basin_mass": 1.0,
            },
        ),
        edge_records=tuple(edges),
        family_extensions={"grc9v3": {"contract_version": "test"}},
    )


def _event(kind: str, *, step_index: int, event_index: int, node_id: int) -> EventTelemetryRow:
    return EventTelemetryRow(
        identity=_identity(),
        step_index=step_index,
        event_index=event_index,
        event_kind=kind,
        source_family="GRC9V3",
        payload={"node_id": node_id},
        family_extensions={"grc9v3": {"contract_version": "test", "primary_node_id": node_id}},
    )


def _load_result(
    checkpoints: tuple[GraphCheckpointArtifact, ...],
    events: tuple[EventTelemetryRow, ...] = (),
) -> SimpleNamespace:
    identity = _identity()
    pack = SimpleNamespace(
        run_summary=_summary(identity),
        step_rows=(),
        event_rows=events,
        graph_checkpoints=checkpoints,
        graph_checkpoint_index=None,
    )
    window = LandscapeInferenceWindow(start_step=0, end_step=3, policy="whole_run")
    root = Path("outputs") / "grc9v3" / "landscape_inference" / "sessions" / "S0010"
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


class LandscapeInferencePheromoneTest(unittest.TestCase):
    def test_repeated_flux_path_emits_pheromone_marker_not_identity(self) -> None:
        load_result = _load_result(
            (
                _checkpoint(checkpoint_id="c0", step_index=0, flux=0.25),
                _checkpoint(checkpoint_id="c1", step_index=1, flux=0.35),
                _checkpoint(checkpoint_id="c2", step_index=2, flux=0.45),
                _checkpoint(checkpoint_id="c3", step_index=3, flux=0.55),
            )
        )
        substrate = build_landscape_inference_evidence_substrate(load_result)

        seed = infer_landscape_pheromone_seed(load_result, substrate=substrate)

        validate_landscape_seed(seed)
        validate_landscape_inference_seed_extensions(seed)
        markers = [
            primitive
            for primitive in seed.primitives
            if primitive.type == "valley" and primitive.role == "pheromone_marker"
        ]
        self.assertEqual(1, len(markers))
        self.assertEqual("pheromone_marker", markers[0].channel_role)
        self.assertEqual(0, seed.extensions["landscape_inference_pheromone_summary"]["identity_claim_count"])
        self.assertTrue(
            seed.extensions["landscape_inference_pheromone_summary"][
                "promotion_policy_suggestion_count"
            ]
        )

    def test_pheromone_requires_path_evidence_not_events_alone(self) -> None:
        load_result = _load_result(
            (
                _checkpoint(checkpoint_id="c0", step_index=0, flux=0.0),
                _checkpoint(checkpoint_id="c1", step_index=1, flux=0.0),
                _checkpoint(checkpoint_id="c2", step_index=2, flux=0.0),
                _checkpoint(checkpoint_id="c3", step_index=3, flux=0.0),
            ),
            events=(_event("collapse", step_index=2, event_index=5, node_id=2),),
        )
        substrate = build_landscape_inference_evidence_substrate(load_result)

        candidates = classify_landscape_pheromone_candidates(load_result, substrate=substrate)
        seed = infer_landscape_pheromone_seed(load_result, substrate=substrate)

        self.assertEqual("ambiguous", candidates[0].status)
        self.assertEqual(
            "event_emphasis_without_repeated_path_activity",
            candidates[0].rejection_reason,
        )
        self.assertEqual([], [p for p in seed.primitives if p.type == "valley"])

    def test_pheromone_rejects_ruptured_path(self) -> None:
        load_result = _load_result(
            (
                _checkpoint(checkpoint_id="c0", step_index=0),
                _checkpoint(checkpoint_id="c1", step_index=1, include_edge=False),
                _checkpoint(checkpoint_id="c2", step_index=2),
                _checkpoint(checkpoint_id="c3", step_index=3),
            )
        )
        substrate = build_landscape_inference_evidence_substrate(load_result)

        candidates = classify_landscape_pheromone_candidates(load_result, substrate=substrate)

        self.assertEqual("rejected", candidates[0].status)
        self.assertEqual("path_ruptured_across_window", candidates[0].rejection_reason)

    def test_pheromone_rejects_stable_identity_on_path(self) -> None:
        load_result = _load_result(
            (
                _checkpoint(checkpoint_id="c0", step_index=0, stable_interior=True),
                _checkpoint(checkpoint_id="c1", step_index=1, stable_interior=True),
                _checkpoint(checkpoint_id="c2", step_index=2, stable_interior=True),
                _checkpoint(checkpoint_id="c3", step_index=3, stable_interior=True),
            )
        )
        substrate = build_landscape_inference_evidence_substrate(load_result)

        candidates = classify_landscape_pheromone_candidates(load_result, substrate=substrate)
        candidate = next(item for item in candidates if item.from_basin_id == "1" and item.to_basin_id == "3")

        self.assertEqual("rejected", candidate.status)
        self.assertEqual("stable_identity_basin_on_path", candidate.rejection_reason)

    def test_conductance_reinforcement_can_support_pheromone_when_flux_is_sparse(self) -> None:
        load_result = _load_result(
            (
                _checkpoint(checkpoint_id="c0", step_index=0, flux=0.0, conductance=1.0),
                _checkpoint(checkpoint_id="c1", step_index=1, flux=0.0, conductance=1.2),
                _checkpoint(checkpoint_id="c2", step_index=2, flux=0.0, conductance=1.4),
                _checkpoint(checkpoint_id="c3", step_index=3, flux=0.0, conductance=1.6),
            )
        )
        substrate = build_landscape_inference_evidence_substrate(load_result)

        candidates = classify_landscape_pheromone_candidates(load_result, substrate=substrate)

        self.assertEqual("accepted", candidates[0].status)
        self.assertTrue(candidates[0].conductance_reinforced)
        self.assertEqual("observed_memory_only", candidates[0].promotion_candidate_status)


if __name__ == "__main__":
    unittest.main()
