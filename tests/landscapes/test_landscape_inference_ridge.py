from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import unittest

from pygrc.landscapes import (
    LandscapeInferenceWindow,
    build_landscape_inference_evidence_substrate,
    build_minimal_landscape_inference_seed,
    classify_landscape_ridge_candidates,
    infer_landscape_ridge_seed,
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
        run_id="ridge_run",
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
        family_extensions={
            "grc9v3": {
                "contract_version": "test",
                "row_basis_differential": {"gradient_norm_max": 10.0},
            }
        },
    )


def _checkpoint(
    *,
    checkpoint_id: str,
    step_index: int,
    include_ridge_node: bool = True,
    pressure_only: bool = False,
    include_node_2: bool = True,
    gradient_norm: float | None = 2.5,
    tensor_anisotropy: float | None = 1.5,
    signed_flux: float = 0.02,
) -> GraphCheckpointArtifact:
    nodes: list[dict[str, object]] = [
        {
            "node_id": 1,
            "coherence": 1.0,
            "payload": {},
        }
    ]
    if include_node_2:
        payload: dict[str, object] = {}
        node: dict[str, object] = {"node_id": 2, "coherence": 0.8, "payload": payload}
        if include_ridge_node:
            if gradient_norm is not None:
                node["gradient_norm"] = gradient_norm
            if tensor_anisotropy is not None:
                node["tensor_anisotropy"] = tensor_anisotropy
            node["tensor_trace"] = 4.0
            node["occupied_ports"] = [1, 5]
        if pressure_only:
            payload["front_capacity_source"] = "pressure_boundary"
            payload["growth_semantics"] = "front_capacity"
        nodes.append(node)
    nodes.append({"node_id": 3, "coherence": 1.0, "payload": {}})
    edges: list[dict[str, object]] = []
    if include_node_2:
        edges = [
            {
                "edge_id": 11,
                "source_node_id": 1,
                "target_node_id": 2,
                "conductance": 1.0,
                "signed_flux": signed_flux,
            },
            {
                "edge_id": 12,
                "source_node_id": 2,
                "target_node_id": 3,
                "conductance": 1.0,
                "signed_flux": signed_flux,
            },
        ]
    return GraphCheckpointArtifact(
        identity=_identity(),
        checkpoint_id=checkpoint_id,
        step_index=step_index,
        time=float(step_index) * 0.1,
        checkpoint_label=f"step_{step_index}",
        checkpoint_reason="ridge_test",
        graph_kind="weighted_graph",
        node_count=len(nodes),
        edge_count=len(edges),
        node_records=tuple(nodes),
        edge_records=tuple(edges),
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
    root = Path("outputs") / "grc9v3" / "landscape_inference" / "sessions" / "S0008"
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


class LandscapeInferenceRidgeTest(unittest.TestCase):
    def test_ridge_classifier_accepts_persistent_gradient_tensor_boundary_node(self) -> None:
        substrate = _substrate(
            (
                _checkpoint(checkpoint_id="c0", step_index=0),
                _checkpoint(checkpoint_id="c1", step_index=1),
                _checkpoint(checkpoint_id="c2", step_index=2),
            )
        )

        candidates = classify_landscape_ridge_candidates(substrate, runtime_family="grc9v3")

        self.assertEqual(1, len(candidates))
        candidate = candidates[0]
        self.assertEqual("accepted", candidate.status)
        self.assertEqual(2, candidate.node_id)
        self.assertEqual("gradient_tensor_ridge", candidate.evidence_mode)
        self.assertEqual("boundary_ridge", candidate.role)
        self.assertEqual("geometric_ridge", candidate.ridge_kind)
        self.assertEqual(3, candidate.persistence_steps)
        self.assertEqual(2.5, candidate.gradient_norm)
        self.assertEqual(1.5, candidate.tensor_anisotropy)
        self.assertEqual(0.04, candidate.incident_abs_flux)
        self.assertTrue(candidate.boundary_port_evidence)
        self.assertIn("graph_checkpoints.node_records.gradient_norm", candidate.evidence_fields)
        self.assertIn("graph_checkpoints.node_records.port_matrix", candidate.evidence_fields)

    def test_pressure_boundary_label_alone_does_not_create_ridge(self) -> None:
        substrate = _substrate(
            (
                _checkpoint(
                    checkpoint_id="c0",
                    step_index=0,
                    include_ridge_node=False,
                    pressure_only=True,
                ),
                _checkpoint(
                    checkpoint_id="c1",
                    step_index=1,
                    include_ridge_node=False,
                    pressure_only=True,
                ),
                _checkpoint(
                    checkpoint_id="c2",
                    step_index=2,
                    include_ridge_node=False,
                    pressure_only=True,
                ),
            )
        )

        candidates = classify_landscape_ridge_candidates(substrate, runtime_family="grc9v3")

        self.assertEqual(1, len(candidates))
        self.assertEqual("rejected", candidates[0].status)
        self.assertEqual(
            "pressure_boundary_label_without_geometric_ridge_evidence",
            candidates[0].rejection_reason,
        )
        self.assertIn("pressure_boundary_is_frontier_not_ridge", candidates[0].evidence_limitations)

    def test_step_row_aggregates_alone_do_not_create_per_node_ridge_claim(self) -> None:
        load_result = _load_result(
            (
                _checkpoint(
                    checkpoint_id="c0",
                    step_index=0,
                    include_ridge_node=False,
                    include_node_2=False,
                ),
                _checkpoint(
                    checkpoint_id="c1",
                    step_index=1,
                    include_ridge_node=False,
                    include_node_2=False,
                ),
                _checkpoint(
                    checkpoint_id="c2",
                    step_index=2,
                    include_ridge_node=False,
                    include_node_2=False,
                ),
            )
        )
        substrate = build_landscape_inference_evidence_substrate(load_result)

        candidates = classify_landscape_ridge_candidates(substrate, runtime_family="grc9v3")
        seed = infer_landscape_ridge_seed(load_result, substrate=substrate)

        self.assertEqual((), candidates)
        self.assertEqual([], seed.primitives)
        self.assertEqual(0, seed.extensions["landscape_inference_ridge_summary"]["observed_ridge_count"])

    def test_ridge_classifier_records_persistence_limitation(self) -> None:
        substrate = _substrate(
            (
                _checkpoint(checkpoint_id="c0", step_index=0),
                _checkpoint(checkpoint_id="c1", step_index=1, include_node_2=False),
                _checkpoint(checkpoint_id="c2", step_index=2),
            )
        )

        candidates = classify_landscape_ridge_candidates(substrate, runtime_family="grc9v3")

        self.assertEqual(1, len(candidates))
        self.assertEqual("rejected", candidates[0].status)
        self.assertEqual("ridge_node_not_persistent_across_window", candidates[0].rejection_reason)
        self.assertIn("node_removed_or_merged_during_window", candidates[0].evidence_limitations)

    def test_ridge_seed_emission_validates(self) -> None:
        load_result = _load_result(
            (
                _checkpoint(checkpoint_id="c0", step_index=0),
                _checkpoint(checkpoint_id="c1", step_index=1),
                _checkpoint(checkpoint_id="c2", step_index=2),
            )
        )
        substrate = build_landscape_inference_evidence_substrate(load_result)

        seed = infer_landscape_ridge_seed(load_result, substrate=substrate)

        validate_landscape_seed(seed)
        validate_landscape_inference_seed_extensions(seed)
        self.assertEqual(1, len(seed.primitives))
        ridge = seed.primitives[0]
        self.assertEqual("ridge", ridge.type)
        self.assertEqual("boundary_ridge", ridge.role)
        self.assertEqual("geometric_ridge", ridge.ridge_kind)
        self.assertEqual(2.5, ridge.anisotropy_hint["gradient_norm"])
        inference = ridge.extensions["landscape_inference"]
        self.assertEqual("observed", inference["authority"])
        self.assertEqual([2], inference["evidence"]["node_ids"])
        self.assertEqual(1, seed.extensions["landscape_inference_ridge_summary"]["observed_ridge_count"])


if __name__ == "__main__":
    unittest.main()
