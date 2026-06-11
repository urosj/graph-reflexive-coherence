from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import unittest

from pygrc.landscapes import (
    LandscapeInferenceWindow,
    build_landscape_inference_evidence_substrate,
    build_minimal_landscape_inference_seed,
    classify_landscape_junction_candidates,
    infer_landscape_junction_seed,
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
        run_id="junction_run",
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
                "port_chart": {"saturated_node_count": 1},
            }
        },
    )


def _checkpoint(
    *,
    checkpoint_id: str,
    step_index: int,
    mode: str = "router",
    min_signed_hessian: float | None = None,
) -> GraphCheckpointArtifact:
    nodes: list[dict[str, object]] = [
        {"node_id": 1, "coherence": 1.0, "payload": {}},
        {
            "node_id": 2,
            "coherence": 1.0,
            "occupied_ports": [1, 2, 5, 8] if mode == "router" else [1, 5],
            "payload": {},
        },
        {"node_id": 3, "coherence": 1.0, "payload": {}},
    ]
    if mode == "router":
        nodes.append({"node_id": 4, "coherence": 1.0, "payload": {}})
    if min_signed_hessian is not None:
        nodes[1]["min_signed_hessian"] = min_signed_hessian
    edges: list[dict[str, object]] = [
        {
            "edge_id": 11,
            "source_node_id": 1,
            "target_node_id": 2,
            "conductance": 1.0,
            "signed_flux": 0.4,
        },
        {
            "edge_id": 12,
            "source_node_id": 2,
            "target_node_id": 3,
            "conductance": 1.0,
            "signed_flux": 0.3 if mode == "router" else 0.0,
        },
    ]
    if mode == "router":
        edges.append(
            {
                "edge_id": 13,
                "source_node_id": 2,
                "target_node_id": 4,
                "conductance": 1.0,
                "signed_flux": -0.2,
            }
        )
    return GraphCheckpointArtifact(
        identity=_identity(),
        checkpoint_id=checkpoint_id,
        step_index=step_index,
        time=float(step_index) * 0.1,
        checkpoint_label=f"step_{step_index}",
        checkpoint_reason="junction_test",
        graph_kind="weighted_graph",
        node_count=len(nodes),
        edge_count=len(edges),
        node_records=tuple(nodes),
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
        payload={"node_id": node_id, "candidate_node_id": node_id},
        family_extensions={
            "grc9v3": {
                "contract_version": "test",
                "primary_node_id": node_id,
                "event_domain": "collapse" if kind == "collapse" else "spark",
            }
        },
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
    window = LandscapeInferenceWindow(start_step=0, end_step=2, policy="whole_run")
    root = Path("outputs") / "grc9v3" / "landscape_inference" / "sessions" / "S0009"
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


class LandscapeInferenceJunctionTest(unittest.TestCase):
    def test_router_requires_checkpoint_port_matrix_and_multi_output_flux(self) -> None:
        load_result = _load_result(
            (
                _checkpoint(checkpoint_id="c0", step_index=0, mode="router"),
                _checkpoint(checkpoint_id="c1", step_index=1, mode="router"),
                _checkpoint(checkpoint_id="c2", step_index=2, mode="router"),
            )
        )
        substrate = build_landscape_inference_evidence_substrate(load_result)

        candidates = classify_landscape_junction_candidates(load_result, substrate=substrate)

        router = next(candidate for candidate in candidates if candidate.role == "router")
        self.assertEqual("accepted", router.status)
        self.assertEqual("junction", router.primitive_type)
        self.assertEqual(2, router.node_id)
        self.assertEqual(3, router.incident_edge_count)
        self.assertEqual(3, router.active_flux_edge_count)
        self.assertEqual((1, 3, 4), router.branch_node_ids)
        self.assertIn("graph_checkpoints.node_records.port_matrix", router.evidence_fields)

    def test_gate_uses_port_pattern_without_promoting_to_router(self) -> None:
        load_result = _load_result(
            (
                _checkpoint(checkpoint_id="c0", step_index=0, mode="gate"),
                _checkpoint(checkpoint_id="c1", step_index=1, mode="gate"),
                _checkpoint(checkpoint_id="c2", step_index=2, mode="gate"),
            )
        )
        substrate = build_landscape_inference_evidence_substrate(load_result)

        candidates = classify_landscape_junction_candidates(load_result, substrate=substrate)

        self.assertTrue(any(candidate.role == "gate" for candidate in candidates))
        self.assertFalse(any(candidate.role == "router" for candidate in candidates))

    def test_collapse_event_creates_event_backed_collapse_site(self) -> None:
        load_result = _load_result(
            (
                _checkpoint(checkpoint_id="c0", step_index=0, mode="gate"),
                _checkpoint(checkpoint_id="c1", step_index=1, mode="gate"),
                _checkpoint(checkpoint_id="c2", step_index=2, mode="gate"),
            ),
            events=(_event("collapse", step_index=1, event_index=4, node_id=2),),
        )
        substrate = build_landscape_inference_evidence_substrate(load_result)

        candidates = classify_landscape_junction_candidates(load_result, substrate=substrate)

        collapse_site = next(candidate for candidate in candidates if candidate.role == "collapse_site")
        self.assertEqual("junction", collapse_site.primitive_type)
        self.assertEqual("event_backed", collapse_site.evidence_mode)
        self.assertEqual(("step_1:event_4:collapse",), collapse_site.event_refs)
        self.assertIn("events.event_kind", collapse_site.evidence_fields)

    def test_spark_candidate_event_creates_saddle_not_basin(self) -> None:
        load_result = _load_result(
            (
                _checkpoint(checkpoint_id="c0", step_index=0, mode="gate"),
                _checkpoint(checkpoint_id="c1", step_index=1, mode="gate"),
                _checkpoint(checkpoint_id="c2", step_index=2, mode="gate"),
            ),
            events=(
                _event("hybrid_spark_candidate", step_index=0, event_index=0, node_id=2),
            ),
        )
        substrate = build_landscape_inference_evidence_substrate(load_result)

        seed = infer_landscape_junction_seed(load_result, substrate=substrate)

        validate_landscape_seed(seed)
        validate_landscape_inference_seed_extensions(seed)
        saddle = next(primitive for primitive in seed.primitives if primitive.type == "saddle")
        self.assertEqual("spark_candidate", saddle.role)
        self.assertEqual("spark_candidate", saddle.junction_role)
        self.assertNotEqual("basin", saddle.type)

    def test_curvature_degeneracy_creates_checkpoint_backed_saddle(self) -> None:
        load_result = _load_result(
            (
                _checkpoint(checkpoint_id="c0", step_index=0, mode="gate", min_signed_hessian=0.0),
                _checkpoint(checkpoint_id="c1", step_index=1, mode="gate", min_signed_hessian=0.0),
                _checkpoint(checkpoint_id="c2", step_index=2, mode="gate", min_signed_hessian=0.0),
            )
        )
        substrate = build_landscape_inference_evidence_substrate(load_result)

        candidates = classify_landscape_junction_candidates(load_result, substrate=substrate)

        saddle = next(candidate for candidate in candidates if candidate.role == "curvature_degeneracy")
        self.assertEqual("saddle", saddle.primitive_type)
        self.assertEqual("checkpoint_curvature_degeneracy", saddle.evidence_mode)
        self.assertIn("graph_checkpoints.node_records.min_signed_hessian", saddle.evidence_fields)

    def test_step_row_port_aggregates_alone_do_not_create_junction(self) -> None:
        checkpoint = _checkpoint(checkpoint_id="c0", step_index=0, mode="gate")
        checkpoint = GraphCheckpointArtifact(
            identity=checkpoint.identity,
            checkpoint_id=checkpoint.checkpoint_id,
            step_index=checkpoint.step_index,
            time=checkpoint.time,
            checkpoint_label=checkpoint.checkpoint_label,
            checkpoint_reason=checkpoint.checkpoint_reason,
            graph_kind=checkpoint.graph_kind,
            node_count=checkpoint.node_count,
            edge_count=checkpoint.edge_count,
            node_records=tuple(
                {key: value for key, value in record.items() if key != "occupied_ports"}
                for record in checkpoint.node_records
            ),
            edge_records=checkpoint.edge_records,
            family_extensions=checkpoint.family_extensions,
        )
        load_result = _load_result((checkpoint,))
        substrate = build_landscape_inference_evidence_substrate(
            load_result,
            allow_short_persistence_window=True,
        )

        candidates = classify_landscape_junction_candidates(load_result, substrate=substrate)

        self.assertEqual((), candidates)


if __name__ == "__main__":
    unittest.main()
