from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest

from pygrc.landscapes import (
    LandscapeInferenceWindow,
    build_landscape_inference_evidence_substrate,
    build_minimal_landscape_inference_seed,
    run_landscape_inference_revival_probe,
    write_landscape_inference_revival_probe_report,
)
from pygrc.telemetry.schema import (
    EventTelemetryRow,
    GraphCheckpointArtifact,
    RunTelemetryIdentity,
    RunTelemetrySummary,
)


def _identity() -> RunTelemetryIdentity:
    return RunTelemetryIdentity(
        run_id="revival_probe_run",
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
        total_event_count=1,
        event_counts_by_kind={"collapse": 1},
        initial_observables={},
        final_observables={},
        resolved_params={"evolution": {"dt": 0.1}},
        family_extensions={"grc9v3": {"contract_version": "test"}},
    )


def _checkpoint(*, checkpoint_id: str, step_index: int, node_2_coherence: float) -> GraphCheckpointArtifact:
    return GraphCheckpointArtifact(
        identity=_identity(),
        checkpoint_id=checkpoint_id,
        step_index=step_index,
        time=float(step_index) * 0.1,
        checkpoint_label=f"step_{step_index}",
        checkpoint_reason="revival_probe_test",
        graph_kind="weighted_graph",
        node_count=3,
        edge_count=2,
        node_records=(
            {
                "node_id": 1,
                "coherence": 1.0,
                "sink_flag": True,
                "basin_id": "1",
                "basin_mass": 1.0,
            },
            {"node_id": 2, "coherence": node_2_coherence},
            {
                "node_id": 3,
                "coherence": 1.0,
                "sink_flag": True,
                "basin_id": "3",
                "basin_mass": 1.0,
            },
        ),
        edge_records=(
            {
                "edge_id": 11,
                "source_node_id": 1,
                "target_node_id": 2,
                "conductance": 1.0,
                "signed_flux": 0.3,
            },
            {
                "edge_id": 12,
                "source_node_id": 2,
                "target_node_id": 3,
                "conductance": 1.0,
                "signed_flux": 0.3,
            },
        ),
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
    *,
    events: tuple[EventTelemetryRow, ...],
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
    root = Path("outputs") / "grc9v3" / "landscape_inference" / "sessions" / "S0014"
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


class LandscapeInferenceRevivalProbeTest(unittest.TestCase):
    def test_revived_node_with_path_memory_is_reported(self) -> None:
        load_result = _load_result(
            (
                _checkpoint(checkpoint_id="c0", step_index=0, node_2_coherence=0.4),
                _checkpoint(checkpoint_id="c1", step_index=1, node_2_coherence=0.0),
                _checkpoint(checkpoint_id="c2", step_index=2, node_2_coherence=0.25),
                _checkpoint(checkpoint_id="c3", step_index=3, node_2_coherence=0.7),
            ),
            events=(_event("collapse", step_index=1, event_index=0, node_id=2),),
        )
        substrate = build_landscape_inference_evidence_substrate(load_result)

        report = run_landscape_inference_revival_probe(load_result, substrate=substrate)

        self.assertEqual(1, report.candidate_count)
        self.assertEqual(1, report.revived_candidate_count)
        candidate = report.candidates[0]
        self.assertEqual(2, candidate.node_id)
        self.assertEqual("revived_with_path_memory", candidate.status)
        self.assertTrue(candidate.revived_after_emphasis)
        self.assertGreater(candidate.pheromone_candidate_count, 0)
        self.assertIn(
            "test_path_memory_feedback_to_delay_or_suppress_revival",
            candidate.policy_suggestions,
        )

    def test_no_emphasis_events_produce_no_revival_candidates(self) -> None:
        load_result = _load_result(
            (
                _checkpoint(checkpoint_id="c0", step_index=0, node_2_coherence=0.4),
                _checkpoint(checkpoint_id="c1", step_index=1, node_2_coherence=0.0),
                _checkpoint(checkpoint_id="c2", step_index=2, node_2_coherence=0.25),
                _checkpoint(checkpoint_id="c3", step_index=3, node_2_coherence=0.7),
            ),
            events=(),
        )

        report = run_landscape_inference_revival_probe(load_result)

        self.assertEqual(0, report.candidate_count)
        self.assertEqual(0, report.revived_candidate_count)

    def test_revival_probe_report_writer_persists_json_and_markdown(self) -> None:
        load_result = _load_result(
            (
                _checkpoint(checkpoint_id="c0", step_index=0, node_2_coherence=0.4),
                _checkpoint(checkpoint_id="c1", step_index=1, node_2_coherence=0.0),
                _checkpoint(checkpoint_id="c2", step_index=2, node_2_coherence=0.25),
                _checkpoint(checkpoint_id="c3", step_index=3, node_2_coherence=0.7),
            ),
            events=(_event("choice_detected", step_index=1, event_index=0, node_id=2),),
        )
        report = run_landscape_inference_revival_probe(load_result)

        with tempfile.TemporaryDirectory() as tmpdir:
            json_path, markdown_path = write_landscape_inference_revival_probe_report(report, tmpdir)

            self.assertTrue(json_path.exists())
            self.assertTrue(markdown_path.exists())
            self.assertIn("Pheromone Revival Probe", markdown_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
