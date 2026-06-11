"""GRCV3 frontier-birth telemetry and selector tests."""

from __future__ import annotations

import unittest

from pygrc import telemetry
from pygrc.core import StepResult, WeightedGraphBackend
from pygrc.models import GRCV3
from pygrc.telemetry._grcv3_extensions import (
    _build_grcv3_run_summary_extension,
    _build_grcv3_step_extension,
)


def _attributes(*, coherence: float, basin_id: int) -> dict[str, object]:
    return {
        "coherence": coherence,
        "gradient": [0.0, 0.0],
        "hessian": [[1.0, 0.0], [0.0, 1.0]],
        "net_flux": [0.0, 0.0],
        "basin_mass": coherence,
        "basin_id": basin_id,
        "parent_id": None,
        "depth": 0,
    }


def _frontier_birth_model(*, mode: str = "active_frontier_pressure") -> GRCV3:
    graph = WeightedGraphBackend()
    parent = graph.add_node({})
    neighbor = graph.add_node({})
    edge_id = graph.add_edge(parent, neighbor, {"base_conductance": 1.0})
    model = GRCV3.from_state(
        state={
            "nodes": {
                str(parent): _attributes(coherence=10.0, basin_id=parent),
                str(neighbor): _attributes(coherence=1.0, basin_id=neighbor),
            },
            "base_conductance": {str(edge_id): 1.0},
            "cached_quantities": {
                "hessian_sign": 1,
                "grcv3_frontier_birth_candidates": {
                    str(parent): {
                        "frontier_source": "pressure_boundary",
                        "frontier_role": "pressure_boundary",
                    }
                },
            },
            "budget_target": 11.0,
        },
        params={
            "dt": 0.1,
            "evolution": {
                "lambda_birth": 100.0,
                "alpha_seed": 0.2,
                "rng_seed": 0,
            },
            "constitutive_semantic_modes": {
                "frontier_birth_mode": mode,
            },
        },
    )
    state = model.get_state()
    state.topology = graph
    state.flux = {
        (edge_id, parent): 2.0,
        (edge_id, neighbor): -2.0,
    }
    return model


class GRCV3FrontierBirthTelemetryTest(unittest.TestCase):
    def test_step_and_run_summary_capture_pressure_boundary_birth(self) -> None:
        model = _frontier_birth_model()
        events = model.apply_frontier_birth()

        step_extension = _build_grcv3_step_extension(model)
        run_extension = _build_grcv3_run_summary_extension(
            model,
            (
                StepResult(
                    step_index=0,
                    time=0.0,
                    events=events,
                    observables={},
                ),
            ),
        )

        step_payload = step_extension.to_mapping()["frontier_birth_state"]
        run_payload = run_extension.to_mapping()

        self.assertEqual("active_frontier_pressure", step_payload["frontier_birth_mode"])
        self.assertEqual(1, step_payload["frontier_candidate_count"])
        self.assertEqual(1, step_payload["pressure_boundary_candidate_count"])
        self.assertEqual(1, step_payload["frontier_birth_count"])
        self.assertEqual(1, step_payload["pressure_boundary_birth_count"])
        self.assertEqual(["pressure_boundary"], step_payload["frontier_sources_observed"])
        self.assertAlmostEqual(2.0, step_payload["outward_flux_pressure_mean"])
        self.assertEqual(
            1,
            run_payload["lifecycle_event_counts"]["frontier_birth_count"],
        )
        self.assertEqual(
            1,
            run_payload["frontier_birth_summary"]["pressure_boundary_birth_count"],
        )

    def test_disabled_mode_reports_surface_without_birth(self) -> None:
        model = _frontier_birth_model(mode="disabled")

        step_extension = _build_grcv3_step_extension(model)
        payload = step_extension.to_mapping()["frontier_birth_state"]

        self.assertEqual("disabled", payload["frontier_birth_mode"])
        self.assertEqual("disabled", payload["frontier_birth_rule"])
        self.assertEqual(1, payload["pressure_boundary_candidate_count"])
        self.assertEqual(0, payload["frontier_birth_count"])
        self.assertEqual(0, payload["pressure_boundary_birth_count"])

    def test_pressure_boundary_selector_pass_fail_and_missing_surface(self) -> None:
        model = _frontier_birth_model()
        events = model.apply_frontier_birth()
        run_extension = _build_grcv3_run_summary_extension(
            model,
            (
                StepResult(
                    step_index=0,
                    time=0.0,
                    events=events,
                    observables={},
                ),
            ),
        )
        passed_payload = {
            "family_extensions": telemetry.grcv3_run_summary_family_extensions(
                run_extension
            )
        }
        failed_payload = {
            "family_extensions": {
                "grcv3": {
                    "frontier_birth_summary": {
                        "frontier_birth_mode": "active_frontier_pressure",
                        "frontier_birth_count": 0,
                        "pressure_boundary_birth_count": 0,
                        "frontier_sources_observed": [],
                    }
                }
            }
        }
        missing_payload = {"family_extensions": {"grcv3": {}}}

        passed = telemetry.validate_grcv3_pressure_boundary_frontier_birth(
            passed_payload
        )
        failed = telemetry.validate_grcv3_pressure_boundary_frontier_birth(
            failed_payload
        )
        missing = telemetry.validate_grcv3_pressure_boundary_frontier_birth(
            missing_payload
        )

        self.assertTrue(passed.passed)
        self.assertEqual("passed", passed.failure_kind)
        self.assertFalse(failed.passed)
        self.assertEqual("predicate_failed", failed.failure_kind)
        self.assertFalse(missing.passed)
        self.assertEqual("missing_surface", missing.failure_kind)


if __name__ == "__main__":
    unittest.main()
