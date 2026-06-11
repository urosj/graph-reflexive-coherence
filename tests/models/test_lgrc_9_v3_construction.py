"""Tests for LGRC9V3 construction and queue-priming facades."""

from __future__ import annotations

from pathlib import Path
import unittest

from pygrc.models import (
    LGRC9V3,
    LGRC9V3CorrectedCascadeScenarioPolicy,
    build_lgrc9v3_from_landscape_seed,
    lgrc9v3_graph_routes_for_current_topology,
    prepare_lgrc9v3_grc9v3_diagnostics,
    prepare_lgrc9v3_landscape_runtime,
    prime_lgrc9v3_broad_seed_packets,
    prime_lgrc9v3_corrected_cascade_queues,
)
from pygrc.models.lgrc_9_v3_construction import (
    LGRC9V3QueuePrimingResult,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
BOUNDARY_SEED = (
    REPO_ROOT
    / "configs/landscapes/seed/grcl9v3-cell-boundary-membrane-spark.seed.yaml"
)
CORRECTED_SEED = (
    REPO_ROOT
    / "configs/landscapes/seed/"
    "grcl9v3-corrected-appendix-e-cell-division-full-capacity-bounded-growth.seed.yaml"
)


class LGRC9V3ConstructionTest(unittest.TestCase):
    """Validate Iteration 36 construction and queue-priming helpers."""

    def test_prepare_landscape_runtime_preserves_lowering_sequence(self) -> None:
        build = prepare_lgrc9v3_landscape_runtime(BOUNDARY_SEED)

        self.assertIsInstance(build.model, LGRC9V3)
        self.assertEqual(
            "cell_boundary_membrane_spark",
            build.example.example_name,
        )
        self.assertTrue(build.source.constructs)
        self.assertTrue(build.lowering.node_id_by_role)
        self.assertEqual(
            len(tuple(build.model.get_state().base_state.topology.iter_live_node_ids())),
            len(tuple(build.lowering.state.topology.iter_live_node_ids())),
        )

    def test_model_facade_builds_from_landscape_seed(self) -> None:
        model = build_lgrc9v3_from_landscape_seed(BOUNDARY_SEED)
        method_model = LGRC9V3.from_landscape_seed(BOUNDARY_SEED)

        self.assertIsInstance(model, LGRC9V3)
        self.assertIsInstance(method_model, LGRC9V3)
        self.assertEqual(model.MODEL_FAMILY, method_model.MODEL_FAMILY)

    def test_route_generation_and_broad_seed_priming_are_library_owned(self) -> None:
        build = prepare_lgrc9v3_landscape_runtime(BOUNDARY_SEED)
        model = build.model

        routes = lgrc9v3_graph_routes_for_current_topology(model)
        model.set_causal_flux_routes(routes)
        result = prime_lgrc9v3_broad_seed_packets(model)

        edge_count = len(tuple(model.get_state().base_state.topology.iter_live_edge_ids()))
        self.assertEqual(2 * edge_count, result.scheduled_count)
        self.assertEqual(0, result.skipped_zero_or_low_coherence)
        self.assertEqual(result.scheduled_count, len(result.event_ids))
        self.assertIsInstance(result, LGRC9V3QueuePrimingResult)
        self.assertEqual(
            result.scheduled_count,
            len(model.get_state().packet_ledger.event_queue_records),
        )

    def test_corrected_cascade_queue_policy_is_explicit(self) -> None:
        policy = LGRC9V3CorrectedCascadeScenarioPolicy()
        build = prepare_lgrc9v3_landscape_runtime(
            CORRECTED_SEED,
            causal_modes=policy.causal_modes(),
        )
        model = prepare_lgrc9v3_grc9v3_diagnostics(build.model)

        summary = prime_lgrc9v3_corrected_cascade_queues(
            model,
            policy=policy,
        )

        self.assertEqual(1, summary["initial_packets"]["scheduled"])
        self.assertEqual(1, summary["boundary_birth_trials_scheduled"])
        self.assertEqual(1, len(model.get_state().packet_ledger.event_queue_records))
        self.assertEqual(1, len(model.get_state().boundary_birth_trial_queue))


if __name__ == "__main__":
    unittest.main()
