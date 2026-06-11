from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from pygrc.landscapes import (
    TOPOLOGICAL_MOTION_CLASSIFIER_ID,
    TopologicalMotionInferenceResult,
    infer_topological_motion,
    infer_topological_motion_report,
)
from pygrc.telemetry.io import build_telemetry_artifact_layout, save_telemetry_artifact_pack
from pygrc.telemetry.schema import (
    EventTelemetryRow,
    GraphCheckpointArtifact,
    GraphCheckpointIndex,
    GraphCheckpointReference,
    RunTelemetryIdentity,
    RunTelemetrySummary,
    StepTelemetryRow,
)


def _identity(family: str = "grc9v3") -> RunTelemetryIdentity:
    return RunTelemetryIdentity(
        run_id=f"{family}_topological_motion_run",
        model_family=family,
        params_identity="params",
        seed_name="topological_motion_seed",
        requested_steps=2,
    )


def _summary(identity: RunTelemetryIdentity, family: str) -> RunTelemetrySummary:
    return RunTelemetrySummary(
        identity=identity,
        completed_steps=2,
        final_step_index=1,
        initial_time=0.0,
        final_time=1.0,
        total_event_count=0,
        event_counts_by_kind={},
        initial_observables={},
        final_observables={},
        resolved_params={},
        raw_params={},
        parameter_overrides={},
        status="completed",
        family_extensions={family: {"contract_version": "test"}},
    )


def _steps(identity: RunTelemetryIdentity, family: str) -> tuple[StepTelemetryRow, ...]:
    return (
        StepTelemetryRow(
            identity=identity,
            step_index=0,
            time=0.0,
            event_count=0,
            event_counts_by_kind={},
            observables={},
            family_extensions={family: {"contract_version": "test"}},
        ),
        StepTelemetryRow(
            identity=identity,
            step_index=1,
            time=1.0,
            event_count=0,
            event_counts_by_kind={},
            observables={},
            family_extensions={family: {"contract_version": "test"}},
        ),
    )


def _event(
    identity: RunTelemetryIdentity,
    family: str,
    kind: str,
    *,
    event_index: int = 0,
    payload: dict[str, object] | None = None,
    topology_mutation: bool = True,
) -> EventTelemetryRow:
    return EventTelemetryRow(
        identity=identity,
        step_index=1,
        event_index=event_index,
        event_kind=kind,
        source_family=family,
        payload={} if payload is None else payload,
        family_extensions={
            family: {
                "event_domain": kind,
                "lifecycle_stage": "completed",
                "topology_mutation": topology_mutation,
                "primary_node_id": ({} if payload is None else payload).get("node_id"),
            }
        },
    )


def _checkpoint(
    identity: RunTelemetryIdentity,
    family: str,
    *,
    checkpoint_id: str,
    step_index: int,
    nodes: tuple[dict[str, object], ...],
    edges: tuple[dict[str, object], ...] = (),
) -> GraphCheckpointArtifact:
    return GraphCheckpointArtifact(
        identity=identity,
        checkpoint_id=checkpoint_id,
        step_index=step_index,
        time=float(step_index),
        checkpoint_label=f"step_{step_index}",
        checkpoint_reason="topological_motion_test",
        graph_kind="weighted_graph",
        node_count=len(nodes),
        edge_count=len(edges),
        node_records=nodes,
        edge_records=edges,
        family_extensions={family: {"contract_version": "test"}},
    )


def _checkpoint_index(
    identity: RunTelemetryIdentity,
    checkpoints: tuple[GraphCheckpointArtifact, ...],
) -> GraphCheckpointIndex:
    return GraphCheckpointIndex(
        identity=identity,
        selection_policy="topological_motion_test",
        selection_params={},
        checkpoints=tuple(
            GraphCheckpointReference(
                checkpoint_id=checkpoint.checkpoint_id,
                step_index=checkpoint.step_index,
                time=checkpoint.time,
                checkpoint_label=checkpoint.checkpoint_label,
                path=f"{checkpoint.checkpoint_id}.json",
            )
            for checkpoint in checkpoints
        ),
    )


def _write_pack(
    root: Path,
    checkpoints: tuple[GraphCheckpointArtifact, ...],
    *,
    events: tuple[EventTelemetryRow, ...] = (),
    family: str = "grc9v3",
) -> Path:
    identity = checkpoints[0].identity
    layout = build_telemetry_artifact_layout(identity.run_id, root_dir=root)
    save_telemetry_artifact_pack(
        layout,
        step_rows=_steps(identity, family),
        event_rows=events,
        run_summary=_summary(identity, family),
        graph_checkpoint_index=_checkpoint_index(identity, checkpoints),
        graph_checkpoints=checkpoints,
    )
    return layout.run_dir


class TopologicalMotionObserverTest(unittest.TestCase):
    def test_growth_example_records_event_backed_topological_motion(self) -> None:
        identity = _identity()
        checkpoints = (
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0000",
                step_index=0,
                nodes=({"node_id": 1},),
            ),
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0001",
                step_index=1,
                nodes=({"node_id": 1}, {"node_id": 2}),
                edges=({"edge_id": 12, "source_node_id": 1, "target_node_id": 2},),
            ),
        )
        event = _event(identity, "grc9v3", "growth", payload={"node_id": 2})
        with tempfile.TemporaryDirectory() as tmp:
            result = infer_topological_motion(_write_pack(Path(tmp), checkpoints, events=(event,)))

        self.assertIsInstance(result, TopologicalMotionInferenceResult)
        self.assertEqual(1, len(result.records))
        record = result.records[0]
        self.assertEqual(TOPOLOGICAL_MOTION_CLASSIFIER_ID, record.classifier_id)
        self.assertEqual("topological", record.motion_kind)
        self.assertEqual("emerged", record.relationship)
        self.assertEqual("growth_support_birth", result.deltas[0].motion_event)
        self.assertEqual("event_backed_topology_delta", result.deltas[0].evidence_mode)
        self.assertEqual((2,), result.deltas[0].born_node_ids)
        self.assertEqual((12,), result.deltas[0].born_edge_ids)
        self.assertIn("step0001_event0000_growth", record.evidence.event_ids)

    def test_spark_expansion_records_support_refinement(self) -> None:
        identity = _identity()
        checkpoints = (
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0000",
                step_index=0,
                nodes=({"node_id": 1},),
            ),
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0001",
                step_index=1,
                nodes=({"node_id": 1}, {"node_id": 2}, {"node_id": 3}),
                edges=(
                    {"edge_id": 12, "source_node_id": 1, "target_node_id": 2},
                    {"edge_id": 13, "source_node_id": 1, "target_node_id": 3},
                ),
            ),
        )
        event = _event(
            identity,
            "grc9v3",
            "hybrid_mechanical_expansion",
            payload={"node_id": 1},
        )
        with tempfile.TemporaryDirectory() as tmp:
            result = infer_topological_motion(_write_pack(Path(tmp), checkpoints, events=(event,)))

        self.assertEqual("support_refinement", result.deltas[0].motion_event)
        self.assertEqual("emerged", result.records[0].relationship)
        self.assertEqual("strong", result.records[0].evidence_quality)

    def test_collapse_event_records_support_contraction_without_identity_claim(self) -> None:
        identity = _identity()
        checkpoints = (
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0000",
                step_index=0,
                nodes=({"node_id": 1}, {"node_id": 2}),
                edges=({"edge_id": 12, "source_node_id": 1, "target_node_id": 2},),
            ),
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0001",
                step_index=1,
                nodes=({"node_id": 1},),
            ),
        )
        event = _event(identity, "grc9v3", "collapse", payload={"node_id": 2})
        with tempfile.TemporaryDirectory() as tmp:
            result = infer_topological_motion(_write_pack(Path(tmp), checkpoints, events=(event,)))

        record = result.records[0]
        self.assertEqual("support_contraction", result.deltas[0].motion_event)
        self.assertEqual("collapsed", record.relationship)
        self.assertEqual((2,), result.deltas[0].removed_node_ids)
        self.assertIn("no_identity_motion_claim", record.non_claims)
        self.assertIn("topology_change_not_identity_walking", record.non_claims)
        self.assertNotEqual("walked", record.relationship)

    def test_topology_only_mutation_is_degraded_without_matching_event_row(self) -> None:
        identity = _identity()
        checkpoints = (
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0000",
                step_index=0,
                nodes=({"node_id": 1},),
            ),
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0001",
                step_index=1,
                nodes=({"node_id": 1}, {"node_id": 2}),
            ),
        )
        with tempfile.TemporaryDirectory() as tmp:
            result = infer_topological_motion(_write_pack(Path(tmp), checkpoints))

        self.assertEqual(1, len(result.records))
        self.assertEqual("topology_only", result.deltas[0].evidence_mode)
        self.assertEqual("degraded", result.records[0].evidence_quality)
        self.assertIn(
            "topology_only_no_matching_event_row",
            result.records[0].evidence.degradation_reasons,
        )

    def test_event_only_collapse_records_carrier_reassignment(self) -> None:
        identity = _identity()
        checkpoints = (
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0000",
                step_index=0,
                nodes=({"node_id": 1}, {"node_id": 2}),
            ),
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0001",
                step_index=1,
                nodes=({"node_id": 1}, {"node_id": 2}),
            ),
        )
        event = _event(identity, "grc9v3", "collapse", payload={"node_id": 2})
        with tempfile.TemporaryDirectory() as tmp:
            result = infer_topological_motion(_write_pack(Path(tmp), checkpoints, events=(event,)))

        self.assertEqual(1, len(result.records))
        self.assertEqual("event_only_topology_mutation", result.deltas[0].evidence_mode)
        self.assertEqual("support_contraction", result.deltas[0].motion_event)
        self.assertEqual("collapsed", result.records[0].relationship)
        self.assertIn(
            "event_only_no_checkpoint_topology_delta",
            result.records[0].evidence.degradation_reasons,
        )

    def test_split_merge_and_prune_event_tokens_are_classified(self) -> None:
        cases = (
            ("identity_fission", "support_split", "split"),
            ("merge", "support_merge", "merged"),
            ("prune", "support_prune", "dissolved"),
        )
        for event_kind, expected_motion_event, expected_relationship in cases:
            with self.subTest(event_kind=event_kind):
                identity = _identity()
                checkpoints = (
                    _checkpoint(
                        identity,
                        "grc9v3",
                        checkpoint_id="checkpoint_0000",
                        step_index=0,
                        nodes=({"node_id": 1}, {"node_id": 2}),
                    ),
                    _checkpoint(
                        identity,
                        "grc9v3",
                        checkpoint_id="checkpoint_0001",
                        step_index=1,
                        nodes=({"node_id": 1}, {"node_id": 2}),
                    ),
                )
                event = _event(identity, "grc9v3", event_kind, payload={"node_id": 2})
                with tempfile.TemporaryDirectory() as tmp:
                    result = infer_topological_motion(
                        _write_pack(Path(tmp), checkpoints, events=(event,))
                    )

                self.assertEqual(1, len(result.records))
                self.assertEqual(expected_motion_event, result.deltas[0].motion_event)
                self.assertEqual(expected_relationship, result.records[0].relationship)

    def test_generic_topology_reassignment_does_not_use_drifted_label(self) -> None:
        identity = _identity()
        checkpoints = (
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0000",
                step_index=0,
                nodes=({"node_id": 1}, {"node_id": 2}),
            ),
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0001",
                step_index=1,
                nodes=({"node_id": 1}, {"node_id": 2}),
            ),
        )
        event = _event(identity, "grc9v3", "topology_mutation", payload={"node_id": 2})
        with tempfile.TemporaryDirectory() as tmp:
            result = infer_topological_motion(_write_pack(Path(tmp), checkpoints, events=(event,)))

        self.assertEqual("support_reassignment", result.deltas[0].motion_event)
        self.assertEqual("stationary", result.records[0].relationship)
        self.assertNotEqual("drifted", result.records[0].relationship)

    def test_report_serializes_topological_records(self) -> None:
        identity = _identity()
        checkpoints = (
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0000",
                step_index=0,
                nodes=({"node_id": 1},),
            ),
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0001",
                step_index=1,
                nodes=({"node_id": 1}, {"node_id": 2}),
            ),
        )
        with tempfile.TemporaryDirectory() as tmp:
            report = infer_topological_motion_report(_write_pack(Path(tmp), checkpoints))

        payload = report.to_mapping()
        self.assertEqual(1, len(payload["records"]))
        self.assertEqual("topological", payload["records"][0]["motion_kind"])


if __name__ == "__main__":
    unittest.main()
