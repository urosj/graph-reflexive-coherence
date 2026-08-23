"""Pre-execution checks for the hardened B2-GR Iteration 4 machinery."""

from __future__ import annotations

import inspect
from pathlib import Path
import sys
import unittest

import numpy as np


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = EXPERIMENT_ROOT.parents[1]
SCRIPTS = EXPERIMENT_ROOT / "scripts"
SRC = REPO_ROOT / "src"
sys.path[:0] = [str(SCRIPTS), str(SRC)]

from b2_artifact_io import read_json  # noqa: E402
from b2_i4_methods import (  # noqa: E402
    _authored_projection,
    _paired_path_summary,
    _segment_failure_modes,
    attempt_specs,
    complete_admitted_causal_state_digest,
    evaluate_attempt,
    source_reconstruction_audit,
)
from pygrc.models import GRC9V3  # noqa: E402
from run_i4_discovery_batch import (  # noqa: E402
    CONFIG_PATH,
    _compact_preparation_history,
    batch_registry,
    validate_prerequisites,
)
from build_i4_native_preparation_reachability import (  # noqa: E402
    _continuation_routing,
)


class I4PreExecutionHardeningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = read_json(CONFIG_PATH)
        cls.prerequisites = validate_prerequisites(cls.config)
        i1 = read_json(EXPERIMENT_ROOT / "outputs/b2_i1_source_handoff_inventory.json")
        cls.crosswalk = i1["payload"]["B1_branch_crosswalk"]["rows"]

    def test_contract_freezes_reviewed_causal_boundaries(self) -> None:
        hardening = self.config["pre_execution_hardening"]
        self.assertFalse(
            self.config["execution"]["proposal_clipping_or_projection_allowed"]
        )
        self.assertFalse(hardening["k0_policy"]["unplanned_washout_step_allowed"])
        self.assertTrue(
            hardening["matched_sham_policy"]["same_parameter_switching_schedule"]
        )
        self.assertFalse(
            hardening["ancestry_policy"][
                "internal_stage_carrier_can_enter_candidate_set"
            ]
        )
        self.assertFalse(
            hardening["i5_firewall"]["future_gate_features_used_for_I4_selection"]
        )
        self.assertFalse(
            hardening["ancestry_policy"][
                "observed_nonzero_state_change_can_be_excused_by_magnitude_tolerance"
            ]
        )
        self.assertFalse(
            hardening["ancestry_policy"][
                "categorical_transition_anywhere_in_path_enters_clean_primary_lane"
            ]
        )
        self.assertEqual(
            hardening["delayed_formation_policy"][
                "carrier_absent_at_k0_but_present_after_first_post_driver_transition"
            ],
            "unresolved_delayed_post_driver_formation_not_I4_positive",
        )

    def test_grid_and_batch_step_arithmetic_are_frozen(self) -> None:
        fixture_counts = {}
        fixture_steps = {}
        for fixture_id in ("F1", "F2", "F3"):
            row = next(
                item for item in self.crosswalk if item["fixture_id"] == fixture_id
            )
            model = GRC9V3.load(str(REPO_ROOT / row["source_snapshot_path"]))
            specs = attempt_specs(model, row["branch_id"])
            fixture_counts[fixture_id] = len(specs)
            fixture_steps[fixture_id] = sum(
                item["history_length"]
                + self.config["i4_admission"][
                    "discovery_persistence_horizon_native_steps"
                ]
                for item in specs
            )
            self.assertEqual(len({item["search_row_id"] for item in specs}), len(specs))
            self.assertEqual(
                [item["attempt_index_within_branch"] for item in specs],
                list(range(len(specs))),
            )
        self.assertEqual(fixture_counts, {"F1": 121, "F2": 121, "F3": 361})
        self.assertEqual(fixture_steps, {"F1": 572, "F2": 572, "F3": 1712})
        self.assertEqual(len(batch_registry()), 12)
        self.assertEqual(
            sum(
                self.config["batching"]["expected_batch_primary_search_native_steps"][
                    fixture_id
                ]
                for fixture_id in ("F1", "F2", "F3")
                for _ in range(4)
            ),
            45696,
        )

    def test_authored_direction_is_removed_vectorially(self) -> None:
        authored = np.asarray([-1.0, 1.0, 0.0])
        observed = np.asarray([-1.2, 1.2, 0.5])
        projected, residual = _authored_projection(observed, authored)
        self.assertTrue(np.allclose(projected, [-1.2, 1.2, 0.0]))
        self.assertTrue(np.allclose(residual, [0.0, 0.0, 0.5]))
        self.assertAlmostEqual(float(np.dot(residual, authored)), 0.0)

    def test_tiny_observed_constraint_change_is_load_bearing(self) -> None:
        def path(*, changed: int) -> dict[str, object]:
            return {
                "native_step_count": 1,
                "event_count": 0,
                "fixed_topology": True,
                "budget_stage_executed_count": 1,
                "budget_stage_changed_state_count": changed,
                "maximum_budget_correction_l_inf": 1e-18 if changed else 0.0,
                "boundary_stage_executed_count": 1,
                "boundary_stage_changed_state_count": 0,
                "maximum_boundary_C_change_l_inf": 0.0,
                "conductance_floor_active": False,
                "categorical_signature_changed": False,
            }

        summary = _paired_path_summary(path(changed=1), path(changed=0), 1e-10)
        self.assertTrue(summary["budget_stage_executed"])
        self.assertTrue(summary["budget_stage_changed_state"])
        self.assertTrue(summary["load_bearing_budget_projection"])
        self.assertLess(summary["maximum_budget_correction_l_inf"], 1e-10)

    def test_categorical_transition_is_outside_clean_segment(self) -> None:
        segment = {
            "event_free": True,
            "fixed_topology": True,
            "load_bearing_budget_projection": False,
            "load_bearing_boundary_or_clipping": False,
            "conductance_floor_active": False,
            "categorical_signature_changed": True,
        }
        self.assertEqual(
            _segment_failure_modes(segment, "preparation_history"),
            ["categorical_transition_in_preparation_history"],
        )

    def test_candidate_state_identity_excludes_only_observer_surfaces(self) -> None:
        branch = self.crosswalk[0]
        model = GRC9V3.load(str(REPO_ROOT / branch["source_snapshot_path"]))
        original = complete_admitted_causal_state_digest(model)
        model.get_state().observables["b2_test_observer"] = 1.0
        model.get_state().coarse_cache["b2_test_observer"] = {"value": 1.0}
        self.assertEqual(complete_admitted_causal_state_digest(model), original)
        model.get_state().cached_quantities["b2_test_causal_cache"] = {"value": 1.0}
        self.assertNotEqual(complete_admitted_causal_state_digest(model), original)

    def test_first_source_branch_reconstructs_and_holds(self) -> None:
        branch = self.crosswalk[0]
        model = GRC9V3.load(str(REPO_ROOT / branch["source_snapshot_path"]))
        audit = source_reconstruction_audit(
            model,
            branch,
            self.prerequisites["b1_registry"][branch["branch_id"]],
            coherence_abs_tolerance=self.prerequisites[
                "b1_C_absolute_tolerance"
            ],
        )
        self.assertEqual(audit["status"], "passed")
        self.assertTrue(all(audit["checks"].values()))
        self.assertEqual(audit["fresh_hold_physical_l_inf"], 0.0)

    def test_nonuniform_source_snapshot_uses_frozen_B1_tolerance(self) -> None:
        branch = next(
            row
            for row in self.crosswalk
            if row["branch_id"] == "grv2-f2-017"
        )
        registry = self.prerequisites["b1_registry"][branch["branch_id"]]
        model = GRC9V3.load(str(REPO_ROOT / branch["source_snapshot_path"]))
        audit = source_reconstruction_audit(
            model,
            branch,
            registry,
            coherence_abs_tolerance=self.prerequisites[
                "b1_C_absolute_tolerance"
            ],
        )
        self.assertEqual(audit["status"], "passed")
        self.assertGreater(audit["snapshot_coherence_l_inf_to_registry"], 0.0)
        self.assertLessEqual(
            audit["snapshot_coherence_l_inf_to_registry"],
            audit["frozen_B1_C_absolute_tolerance"],
        )
        self.assertEqual(
            audit["accepted_canonical_branch_signature"],
            registry["canonical_branch_signature"],
        )
        self.assertEqual(
            audit["snapshot_coordinate_signature_role"],
            "diagnostic_only_not_branch_identity",
        )

    def test_source_and_resolved_parameter_identities_are_not_collapsed(self) -> None:
        branch = self.crosswalk[0]
        registry = self.prerequisites["b1_registry"][branch["branch_id"]]
        self.assertEqual(branch["parameter_hash"], registry["parameter_hash"])
        self.assertNotEqual(
            branch["parameter_hash"], branch["runtime_parameter_vector_digest"]
        )
        model = GRC9V3.load(str(REPO_ROOT / branch["source_snapshot_path"]))
        self.assertEqual(
            model.get_params().params_hash,
            branch["runtime_parameter_vector_digest"],
        )

    def test_representative_attempt_matches_full_sham_history(self) -> None:
        branch = self.crosswalk[0]
        registry = self.prerequisites["b1_registry"][branch["branch_id"]]
        model = GRC9V3.load(str(REPO_ROOT / branch["source_snapshot_path"]))
        audit = source_reconstruction_audit(
            model,
            branch,
            registry,
            coherence_abs_tolerance=self.prerequisites[
                "b1_C_absolute_tolerance"
            ],
        )
        spec = next(
            row
            for row in attempt_specs(model, branch["branch_id"])
            if row["preparation_family"]
            == "temporary_parameter_history_after_C_pair_pulse"
        )
        row = evaluate_attempt(
            model,
            branch,
            audit,
            spec,
            formation_floor=self.prerequisites["thresholds"][
                "formation_contrast_floor_v1"
            ],
            numerical_uncertainty=self.config["i4_admission"][
                "numerical_uncertainty_floor"
            ],
            persistence_horizon=self.config["i4_admission"][
                "discovery_persistence_horizon_native_steps"
            ],
            carrier_priority=self.config["candidate_freeze"]["carrier_priority"],
        )
        self.assertTrue(row["matched_sham"]["same_native_step_count_and_timing"])
        self.assertTrue(row["matched_sham"]["same_parameter_switching_schedule"])
        self.assertEqual(
            row["positive_k0_state"]["active_model_parameter_digest"],
            row["sham_k0_state"]["active_model_parameter_digest"],
        )
        self.assertFalse(row["preparation_history"]["unplanned_washout_step_used"])
        self.assertFalse(row["future_gate_features_computed_or_accessed"])

    def test_discovery_evaluator_does_not_access_i5_or_later_features(self) -> None:
        source = inspect.getsource(evaluate_attempt)
        for forbidden in (
            "slow_cluster_isolation_margin",
            "formation_specific_occupancy_excess",
            "GRR4_oriented_interaction_margin",
            "reset_swap_or_bypass_outcome",
            "final_GRR_classification",
        ):
            self.assertNotIn(forbidden, source)

    def test_empty_candidate_set_routes_to_bounded_closeout(self) -> None:
        routing = _continuation_routing(
            execution_complete=True, confirmed_candidate_count=0
        )
        self.assertFalse(routing["ready_for_iteration_5"])
        self.assertTrue(routing["ready_for_iteration_8_bounded_closeout"])
        self.assertTrue(routing["empty_path_semantics_applied"])
        self.assertEqual(
            routing["I5_to_I7_positive_lane_status"],
            "not_applicable_empty_I4_candidate_set",
        )

    def test_nonempty_candidate_set_routes_to_iteration_5(self) -> None:
        routing = _continuation_routing(
            execution_complete=True, confirmed_candidate_count=1
        )
        self.assertTrue(routing["ready_for_iteration_5"])
        self.assertFalse(routing["ready_for_iteration_8_bounded_closeout"])
        self.assertFalse(routing["empty_path_semantics_applied"])

    def test_attempt_history_is_compact_and_digest_bound(self) -> None:
        history = {
            "family": "test",
            "history_length": 1,
            "pulse_amount": 0.1,
            "pulse_edge_id": 0,
            "pulse_source_node": 0,
            "pulse_destination_node": 1,
            "parameter_variant_id": "evaluation_parameters",
            "parameter_name": None,
            "parameter_multiplier": None,
            "state_production_parameter_vector": {"dt": 0.1, "eta": 0.5},
            "current_evaluation_parameter_vector": {"dt": 0.1, "eta": 0.5},
            "driver_exhaustion_boundary": "after_history",
            "first_post_driver_transition": "k0_to_k1",
            "unplanned_washout_step_used": False,
        }
        compact = _compact_preparation_history(history)
        self.assertNotIn("state_production_parameter_vector", compact)
        self.assertNotIn("current_evaluation_parameter_vector", compact)
        self.assertIn("state_production_parameter_vector_digest", compact)
        self.assertIn("current_evaluation_parameter_vector_digest", compact)
        self.assertIn("full_history_digest", compact)

if __name__ == "__main__":
    unittest.main()
