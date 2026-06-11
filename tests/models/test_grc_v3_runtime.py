"""Representative runtime and replay tests for the GRCV3 baseline."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from pygrc.core import (
    BACKEND_SELECTIONS_KEY,
    WeightedGraphBackend,
    build_backend_selection,
    build_backend_selection_payload,
    digest_snapshot,
)
from pygrc.models import GRCV3


def _node_attributes(
    *,
    coherence: float,
    basin_id: str | int,
    parent_id: str | int | None = None,
    depth: int = 0,
) -> dict[str, object]:
    return {
        "coherence": coherence,
        "gradient": [0.0, 0.0],
        "hessian": [[1.0, 0.0], [0.0, 1.0]],
        "net_flux": [0.0, 0.0],
        "basin_mass": coherence,
        "basin_id": basin_id,
        "parent_id": parent_id,
        "depth": depth,
    }


def _serialize_step_result(result: object) -> dict[str, object]:
    from pygrc.core import StepResult

    if not isinstance(result, StepResult):
        raise TypeError("expected StepResult")
    return {
        "step_index": result.step_index,
        "time": result.time,
        "events": [
            {
                "kind": event.kind,
                "step_index": event.step_index,
                "payload": dict(event.payload),
                "source_family": event.source_family,
            }
            for event in result.events
        ],
        "observables": dict(result.observables),
        "bookkeeping": dict(result.bookkeeping),
    }


def _build_representative_model() -> GRCV3:
    graph = WeightedGraphBackend()
    left = graph.add_node({"kind": "representative"})
    center = graph.add_node({"kind": "representative"})
    right = graph.add_node({"kind": "representative"})
    edge_left = graph.add_edge(left, center, {"kind": "representative"})
    edge_right = graph.add_edge(center, right, {"kind": "representative"})

    model = GRCV3.from_state(
        state={
            "nodes": {
                str(left): _node_attributes(coherence=1.2, basin_id=left),
                str(center): _node_attributes(coherence=0.75, basin_id=center),
                str(right): _node_attributes(coherence=0.35, basin_id=right),
            },
            "base_conductance": {
                str(edge_left): 1.0,
                str(edge_right): 1.0,
            },
        },
        params={
            "dt": 0.05,
            "evolution": {
                "eps_gradient": 1e-3,
                "eps_hessian": 1e-3,
                "eps_spark": 1e6,
                "tau_split": 2.0,
            },
            "constitutive_semantic_modes": {
                BACKEND_SELECTIONS_KEY: build_backend_selection_payload(
                    [build_backend_selection(category="choice", name="disabled")]
                )
            },
        },
    )
    model.get_state().topology = graph
    return model


class GRCV3RepresentativeRuntimeTest(unittest.TestCase):
    def test_representative_lane_steps_deterministically(self) -> None:
        def run_lane() -> tuple[list[dict[str, object]], str]:
            model = _build_representative_model()
            results = [_serialize_step_result(model.step()) for _ in range(3)]
            return results, digest_snapshot(model.snapshot())

        left_results, left_digest = run_lane()
        right_results, right_digest = run_lane()

        self.assertEqual(left_results, right_results)
        self.assertEqual(left_digest, right_digest)
        self.assertEqual(3, left_results[-1]["step_index"])
        self.assertAlmostEqual(0.15, float(left_results[-1]["time"]))
        self.assertEqual(
            left_results[-1]["bookkeeping"]["expected_step_order"],
            left_results[-1]["bookkeeping"]["step_order"],
        )

    def test_representative_lane_save_load_replays_identically(self) -> None:
        model = _build_representative_model()
        first = _serialize_step_result(model.step())

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "grcv3-runtime.json"
            model.save(str(path))
            restored = GRCV3.load(str(path))

        continued_results = [
            _serialize_step_result(model.step()),
            _serialize_step_result(model.step()),
        ]
        restored_results = [
            _serialize_step_result(restored.step()),
            _serialize_step_result(restored.step()),
        ]

        self.assertEqual(first["step_index"], 1)
        self.assertEqual(continued_results, restored_results)
        self.assertEqual(
            digest_snapshot(model.snapshot()),
            digest_snapshot(restored.snapshot()),
        )
