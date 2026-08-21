from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_instrumentation import (  # noqa: E402
    build_grv1_records,
    edge_reorientation_control,
    fresh_process_replay_control,
    k_counterfactual,
    load_fixture,
    observation_noninterference_control,
    public_stage_replay_control,
    state_field_inventory,
    step_trace_control,
    surface_authority_map,
)


class InstrumentationValidationTest(unittest.TestCase):
    def test_step_observer_matches_runtime_without_interference(self) -> None:
        result = step_trace_control(load_fixture())
        self.assertEqual("passed", result["status"])
        self.assertTrue(result["checks"]["instrumentation_noninterfering"])

    def test_K_and_orientation_controls_keep_distinct_semantics(self) -> None:
        fixture = load_fixture()
        K_result = k_counterfactual(fixture)
        orientation = edge_reorientation_control(fixture)
        self.assertEqual("passed", K_result["status"])
        self.assertEqual("passed", orientation["status"])
        self.assertIn("diagnostic_only", K_result["classification"])
        self.assertIn("coordinate_covariance", orientation["classification"])

    def test_observation_and_public_stage_replay_are_noninterfering(self) -> None:
        fixture = load_fixture()
        observation = observation_noninterference_control(fixture)
        public_replay = public_stage_replay_control(fixture)
        self.assertEqual("passed", observation["status"])
        self.assertEqual("passed", public_replay["status"])
        self.assertTrue(
            public_replay["checks"]["final_complete_runtime_state_equal"]
        )

    def test_surface_authority_controls_separate_W_J_and_K(self) -> None:
        fixture = load_fixture()
        K_result = k_counterfactual(fixture)
        authority = surface_authority_map(fixture, K_result)
        self.assertEqual("passed", authority["status"])
        self.assertEqual(
            ["W_base_conductance", "J_signed_edge_current", "K_hybrid_node_tensor"],
            [record["logical_quantity"] for record in authority["records"]],
        )

    def test_fresh_process_replay_is_exact(self) -> None:
        result = fresh_process_replay_control(load_fixture())
        self.assertEqual("passed", result["status"])
        self.assertTrue(result["checks"]["fresh_python_process_equal"])

    def test_every_runtime_state_field_is_classified(self) -> None:
        inventory = state_field_inventory()
        self.assertTrue(inventory["all_runtime_fields_classified"])
        self.assertEqual([], inventory["missing_fields"])
        self.assertEqual([], inventory["extra_fields"])

    def test_complete_grv1_record_set_passes(self) -> None:
        records = build_grv1_records()
        payload = records["instrumentation_validation.json"]["payload"]
        self.assertEqual("passed", payload["status"])
        self.assertFalse(payload["claim_boundary"]["continuation_supported"])
        self.assertFalse(payload["claim_boundary"]["readback_supported"])


if __name__ == "__main__":
    unittest.main()
