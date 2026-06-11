from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from pygrc.landscapes import (
    IDENTITY_MOTION_CLASSIFIER_ID,
    IdentityMotionInferenceResult,
    infer_identity_motion,
    infer_identity_motion_report,
)
from pygrc.telemetry.io import build_telemetry_artifact_layout, save_telemetry_artifact_pack
from pygrc.telemetry.schema import (
    GraphCheckpointArtifact,
    GraphCheckpointIndex,
    GraphCheckpointReference,
    RunTelemetryIdentity,
    RunTelemetrySummary,
    StepTelemetryRow,
)


def _identity(family: str = "grc9v3") -> RunTelemetryIdentity:
    return RunTelemetryIdentity(
        run_id=f"{family}_identity_motion_run",
        model_family=family,
        params_identity="params",
        seed_name="identity_motion_seed",
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
            family_extensions={family: {}},
        ),
        StepTelemetryRow(
            identity=identity,
            step_index=1,
            time=1.0,
            event_count=0,
            event_counts_by_kind={},
            observables={},
            family_extensions={family: {}},
        ),
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
        checkpoint_reason="identity_motion_test",
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
        selection_policy="identity_motion_test",
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
    family: str = "grc9v3",
) -> Path:
    identity = checkpoints[0].identity
    layout = build_telemetry_artifact_layout(identity.run_id, root_dir=root)
    save_telemetry_artifact_pack(
        layout,
        step_rows=_steps(identity, family),
        event_rows=(),
        run_summary=_summary(identity, family),
        graph_checkpoint_index=_checkpoint_index(identity, checkpoints),
        graph_checkpoints=checkpoints,
    )
    return layout.run_dir


class IdentityMotionMatcherTest(unittest.TestCase):
    def test_stationary_identity_preserves_group_and_representative(self) -> None:
        identity = _identity()
        nodes = (
            {"node_id": 1, "coherence": 2.0, "basin_id": "basin_a", "is_sink": True},
            {"node_id": 2, "coherence": 1.0, "basin_id": "basin_a"},
        )
        checkpoints = (
            _checkpoint(identity, "grc9v3", checkpoint_id="checkpoint_0000", step_index=0, nodes=nodes),
            _checkpoint(identity, "grc9v3", checkpoint_id="checkpoint_0001", step_index=1, nodes=nodes),
        )
        with tempfile.TemporaryDirectory() as tmp:
            result = infer_identity_motion(_write_pack(Path(tmp), checkpoints))

        self.assertIsInstance(result, IdentityMotionInferenceResult)
        self.assertEqual(1, len(result.records))
        record = result.records[0]
        self.assertEqual(IDENTITY_MOTION_CLASSIFIER_ID, record.classifier_id)
        self.assertEqual("identity", record.motion_kind)
        self.assertEqual("stationary", record.relationship)
        self.assertEqual((1, 2), record.old_carriers.node_ids)
        self.assertTrue(record.competing_claims)

    def test_identity_walking_changes_basin_label_with_continuity(self) -> None:
        identity = _identity()
        checkpoints = (
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0000",
                step_index=0,
                nodes=({"node_id": 1, "coherence": 2.0, "basin_id": "basin_a", "is_sink": True},),
            ),
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0001",
                step_index=1,
                nodes=({"node_id": 1, "coherence": 2.0, "basin_id": "basin_b", "is_sink": True},),
            ),
        )
        with tempfile.TemporaryDirectory() as tmp:
            result = infer_identity_motion(_write_pack(Path(tmp), checkpoints))

        self.assertEqual(1, len(result.records))
        record = result.records[0]
        self.assertEqual("walked", record.relationship)
        self.assertEqual(("basin_a",), record.old_carriers.basin_ids)
        self.assertEqual(("basin_b",), record.new_carriers.basin_ids)
        self.assertTrue(record.competing_claims)

    def test_split_maps_one_old_identity_to_multiple_new_identities(self) -> None:
        identity = _identity()
        checkpoints = (
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0000",
                step_index=0,
                nodes=(
                    {"node_id": 1, "coherence": 1.0, "basin_id": "basin_a", "is_sink": True},
                    {"node_id": 2, "coherence": 1.0, "basin_id": "basin_a"},
                ),
            ),
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0001",
                step_index=1,
                nodes=(
                    {"node_id": 1, "coherence": 1.0, "basin_id": "basin_left", "is_sink": True},
                    {"node_id": 2, "coherence": 1.0, "basin_id": "basin_right", "is_sink": True},
                ),
            ),
        )
        with tempfile.TemporaryDirectory() as tmp:
            result = infer_identity_motion(_write_pack(Path(tmp), checkpoints))

        relationships = [record.relationship for record in result.records]
        self.assertEqual(["split"], relationships)
        record = result.records[0]
        self.assertEqual(("basin_a",), record.old_carriers.basin_ids)
        self.assertEqual(("basin_left", "basin_right"), record.new_carriers.basin_ids)

    def test_collapse_maps_multiple_old_identities_to_one_compressed_identity(self) -> None:
        identity = _identity()
        checkpoints = (
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0000",
                step_index=0,
                nodes=(
                    {"node_id": 1, "coherence": 2.0, "basin_id": "basin_a", "is_sink": True},
                    {"node_id": 2, "coherence": 2.0, "basin_id": "basin_b", "is_sink": True},
                ),
            ),
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0001",
                step_index=1,
                nodes=(
                    {"node_id": 1, "coherence": 0.5, "basin_id": "basin_c", "is_sink": True},
                    {"node_id": 2, "coherence": 0.5, "basin_id": "basin_c"},
                ),
            ),
        )
        with tempfile.TemporaryDirectory() as tmp:
            result = infer_identity_motion(_write_pack(Path(tmp), checkpoints))

        self.assertEqual(1, len(result.records))
        record = result.records[0]
        self.assertEqual("collapsed", record.relationship)
        self.assertEqual(("basin_a", "basin_b"), record.old_carriers.basin_ids)
        self.assertEqual(("basin_c",), record.new_carriers.basin_ids)

    def test_dissolution_and_emergence_are_recorded_when_no_match_exists(self) -> None:
        identity = _identity()
        checkpoints = (
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0000",
                step_index=0,
                nodes=({"node_id": 1, "coherence": 1.0, "basin_id": "basin_a", "is_sink": True},),
            ),
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0001",
                step_index=1,
                nodes=({"node_id": 2, "coherence": 1.0, "basin_id": "basin_b", "is_sink": True},),
            ),
        )
        with tempfile.TemporaryDirectory() as tmp:
            result = infer_identity_motion(_write_pack(Path(tmp), checkpoints))

        self.assertEqual(["dissolved", "emerged"], [record.relationship for record in result.records])
        dissolved, emerged = result.records
        self.assertEqual(("no_successor",), dissolved.new_carriers.primitive_ids)
        self.assertEqual(("no_predecessor",), emerged.old_carriers.primitive_ids)

    def test_weak_continuity_is_preserved_as_ambiguous(self) -> None:
        identity = _identity()
        checkpoints = (
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0000",
                step_index=0,
                nodes=(
                    {"node_id": 1, "coherence": 10.0, "basin_id": "basin_a", "is_sink": True},
                    {"node_id": 2, "coherence": 1.0, "basin_id": "basin_a"},
                ),
            ),
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0001",
                step_index=1,
                nodes=(
                    {"node_id": 2, "coherence": 1.0, "basin_id": "basin_b", "is_sink": True},
                    {"node_id": 3, "coherence": 10.0, "basin_id": "basin_b"},
                ),
            ),
        )
        with tempfile.TemporaryDirectory() as tmp:
            result = infer_identity_motion(_write_pack(Path(tmp), checkpoints), min_match_score=0.9)

        self.assertEqual(1, len(result.records))
        record = result.records[0]
        self.assertEqual("ambiguous", record.relationship)
        self.assertIn("competing_or_weak_continuity", record.evidence.degradation_reasons)

    def test_successor_flux_and_provenance_support_identity_walk_without_overlap(self) -> None:
        identity = _identity()
        checkpoints = (
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0000",
                step_index=0,
                nodes=(
                    {
                        "node_id": 1,
                        "coherence": 2.0,
                        "basin_id": "basin_a",
                        "is_sink": True,
                        "payload": {
                            "successor_node_id": 2,
                            "hierarchy_parent": "parent_alpha",
                            "source_construct_id": "identity_alpha",
                        },
                    },
                ),
                edges=({"edge_id": 10, "source_node_id": 1, "target_node_id": 2, "signed_flux": 1.0},),
            ),
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0001",
                step_index=1,
                nodes=(
                    {
                        "node_id": 2,
                        "coherence": 2.0,
                        "basin_id": "basin_b",
                        "is_sink": True,
                        "payload": {
                            "hierarchy_parent": "parent_alpha",
                            "source_construct_id": "identity_alpha",
                        },
                    },
                ),
                edges=({"edge_id": 10, "source_node_id": 1, "target_node_id": 2, "signed_flux": 1.0},),
            ),
        )
        with tempfile.TemporaryDirectory() as tmp:
            result = infer_identity_motion(_write_pack(Path(tmp), checkpoints))

        self.assertEqual(1, len(result.records))
        record = result.records[0]
        self.assertEqual("walked", record.relationship)
        self.assertEqual((10,), record.evidence.edge_ids)
        match = result.matches[0]
        self.assertEqual(1.0, match.flux_path_support)
        self.assertEqual(1.0, match.successor_continuity)
        self.assertEqual(1.0, match.hierarchy_provenance_continuity)

    def test_multihop_path_requires_flux_on_every_edge(self) -> None:
        identity = _identity()
        checkpoints = (
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0000",
                step_index=0,
                nodes=(
                    {
                        "node_id": 1,
                        "coherence": 2.0,
                        "basin_id": "basin_a",
                        "is_sink": True,
                        "payload": {"successor_node_id": 2},
                    },
                    {
                        "node_id": 3,
                        "coherence": 0.1,
                        "basin_id": "bridge",
                    },
                ),
                edges=(
                    {"edge_id": 10, "source_node_id": 1, "target_node_id": 3, "signed_flux": 1.0},
                    {"edge_id": 11, "source_node_id": 3, "target_node_id": 2, "signed_flux": 0.0},
                ),
            ),
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0001",
                step_index=1,
                nodes=(
                    {"node_id": 2, "coherence": 2.0, "basin_id": "basin_b", "is_sink": True},
                    {"node_id": 3, "coherence": 0.1, "basin_id": "bridge"},
                ),
                edges=(
                    {"edge_id": 10, "source_node_id": 1, "target_node_id": 3, "signed_flux": 1.0},
                    {"edge_id": 11, "source_node_id": 3, "target_node_id": 2, "signed_flux": 0.0},
                ),
            ),
        )
        with tempfile.TemporaryDirectory() as tmp:
            result = infer_identity_motion(_write_pack(Path(tmp), checkpoints))

        match_by_pair = {
            (match.old_group_id, match.new_group_id): match
            for match in result.matches
        }
        self.assertEqual(0.0, match_by_pair[("basin_a", "basin_b")].flux_path_support)
        self.assertEqual((), match_by_pair[("basin_a", "basin_b")].path_edge_ids)

    def test_successor_and_provenance_scores_are_fractional(self) -> None:
        identity = _identity()
        checkpoints = (
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0000",
                step_index=0,
                nodes=(
                    {
                        "node_id": 1,
                        "coherence": 1.0,
                        "basin_id": "basin_a",
                        "is_sink": True,
                        "payload": {"successor_node_id": 3, "source_construct_id": "shared"},
                    },
                    {
                        "node_id": 2,
                        "coherence": 1.0,
                        "basin_id": "basin_a",
                        "payload": {"successor_node_id": 99, "source_construct_id": "old_only"},
                    },
                ),
            ),
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0001",
                step_index=1,
                nodes=(
                    {
                        "node_id": 3,
                        "coherence": 1.0,
                        "basin_id": "basin_b",
                        "is_sink": True,
                        "payload": {"source_construct_id": "shared"},
                    },
                    {
                        "node_id": 4,
                        "coherence": 1.0,
                        "basin_id": "basin_b",
                        "payload": {"source_construct_id": "new_only"},
                    },
                ),
            ),
        )
        with tempfile.TemporaryDirectory() as tmp:
            result = infer_identity_motion(_write_pack(Path(tmp), checkpoints))

        match = result.matches[0]
        self.assertEqual(0.5, match.successor_continuity)
        self.assertEqual(0.5, match.hierarchy_provenance_continuity)

    def test_dense_same_step_fission_uses_sparse_candidate_index(self) -> None:
        identity = _identity()
        parent_count = 501
        old_nodes: list[dict[str, object]] = []
        new_nodes: list[dict[str, object]] = []
        for index in range(parent_count):
            node_a = index * 10 + 1
            node_b = index * 10 + 2
            parent_id = f"dense_parent_{index:04d}"
            old_nodes.extend(
                (
                    {
                        "node_id": node_a,
                        "coherence": 4.0,
                        "basin_id": parent_id,
                        "is_sink": True,
                        "payload": {"source_construct_id": parent_id},
                    },
                    {
                        "node_id": node_b,
                        "coherence": 2.0,
                        "basin_id": parent_id,
                        "payload": {"source_construct_id": parent_id},
                    },
                )
            )
            new_nodes.extend(
                (
                    {
                        "node_id": node_a,
                        "coherence": 2.0,
                        "basin_id": f"dense_child_{index:04d}_a",
                        "is_sink": True,
                        "payload": {
                            "hierarchy_parent": parent_id,
                            "source_construct_id": parent_id,
                        },
                    },
                    {
                        "node_id": node_b,
                        "coherence": 2.0,
                        "basin_id": f"dense_child_{index:04d}_b",
                        "is_sink": True,
                        "payload": {
                            "hierarchy_parent": parent_id,
                            "source_construct_id": parent_id,
                        },
                    },
                )
            )
        checkpoints = (
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0000",
                step_index=0,
                nodes=tuple(old_nodes),
            ),
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0001",
                step_index=1,
                nodes=tuple(new_nodes),
            ),
        )
        with tempfile.TemporaryDirectory() as tmp:
            result = infer_identity_motion(_write_pack(Path(tmp), checkpoints))

        splits = [record for record in result.records if record.relationship == "split"]
        diagnostics = result.matcher_diagnostics
        self.assertEqual(parent_count, len(splits))
        self.assertEqual("sparse_evidence_index", diagnostics["candidate_generation_mode"])
        self.assertEqual(parent_count * parent_count * 2, diagnostics["all_pair_count_total"])
        self.assertEqual(parent_count * 2, diagnostics["candidate_edge_count_total"])
        self.assertEqual(parent_count * 2, diagnostics["scored_pair_count_total"])
        self.assertGreater(diagnostics["all_pair_count_avoided_total"], 500_000)

    def test_drifted_and_merged_paths_are_explicitly_covered(self) -> None:
        identity = _identity()
        drift_checkpoints = (
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0000",
                step_index=0,
                nodes=(
                    {"node_id": 1, "coherence": 3.0, "basin_id": "basin_a", "payload": {"coordinates": [0.0, 0.0]}},
                    {"node_id": 2, "coherence": 1.0, "basin_id": "basin_a", "payload": {"coordinates": [2.0, 0.0]}},
                ),
            ),
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0001",
                step_index=1,
                nodes=(
                    {"node_id": 1, "coherence": 1.0, "basin_id": "basin_a", "payload": {"coordinates": [0.0, 0.0]}},
                    {"node_id": 2, "coherence": 3.0, "basin_id": "basin_a", "payload": {"coordinates": [2.0, 0.0]}},
                ),
            ),
        )
        with tempfile.TemporaryDirectory() as tmp:
            drift = infer_identity_motion(_write_pack(Path(tmp), drift_checkpoints))
        self.assertEqual("drifted", drift.records[0].relationship)

        merge_checkpoints = (
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0000",
                step_index=0,
                nodes=(
                    {"node_id": 1, "coherence": 2.0, "basin_id": "basin_a", "is_sink": True},
                    {"node_id": 2, "coherence": 2.0, "basin_id": "basin_b", "is_sink": True},
                ),
            ),
            _checkpoint(
                identity,
                "grc9v3",
                checkpoint_id="checkpoint_0001",
                step_index=1,
                nodes=(
                    {"node_id": 1, "coherence": 2.0, "basin_id": "basin_c", "is_sink": True},
                    {"node_id": 2, "coherence": 2.0, "basin_id": "basin_c"},
                ),
            ),
        )
        with tempfile.TemporaryDirectory() as tmp:
            merged = infer_identity_motion(_write_pack(Path(tmp), merge_checkpoints))
        self.assertEqual("merged", merged.records[0].relationship)

    def test_report_serializes_identity_records(self) -> None:
        identity = _identity()
        nodes = ({"node_id": 1, "coherence": 2.0, "basin_id": "basin_a", "is_sink": True},)
        checkpoints = (
            _checkpoint(identity, "grc9v3", checkpoint_id="checkpoint_0000", step_index=0, nodes=nodes),
            _checkpoint(identity, "grc9v3", checkpoint_id="checkpoint_0001", step_index=1, nodes=nodes),
        )
        with tempfile.TemporaryDirectory() as tmp:
            report = infer_identity_motion_report(_write_pack(Path(tmp), checkpoints))

        payload = report.to_mapping()
        self.assertEqual(1, len(payload["records"]))
        self.assertEqual("identity", payload["records"][0]["motion_kind"])


if __name__ == "__main__":
    unittest.main()
