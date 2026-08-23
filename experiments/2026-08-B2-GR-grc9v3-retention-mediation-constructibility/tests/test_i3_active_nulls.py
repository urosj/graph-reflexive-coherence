"""Focused tests for B2-GR Iteration 3 active nulls."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = EXPERIMENT_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from b2_artifact_io import find_absolute_paths, git, semantic_digest  # noqa: E402
from build_i3_active_nulls import build_payload  # noqa: E402


class I3ActiveNullTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload, cls.calibration = build_payload(git("rev-parse", "HEAD"))

    def test_accepted_i2_is_bound(self) -> None:
        source = self.payload["source_schema_contract"]
        self.assertEqual(source["I2_acceptance_status"], "accepted")
        self.assertEqual(source["I2_assigned_closeout_rung"], "B2-C1")
        self.assertEqual(len(source["I2_result_revision"]), 40)
        self.assertEqual(len(source["I2_artifact_payload_sha256"]), 64)
        self.assertEqual(len(source["I2_receipt_payload_sha256"]), 64)

    def test_every_frozen_null_is_instantiated_once_in_source_order(self) -> None:
        required = self.payload["source_schema_contract"]["required_null_ids"]
        rows = self.payload["active_null_rows"]
        self.assertEqual(len(required), 52)
        self.assertEqual([row["null_id"] for row in rows], required)
        self.assertEqual(len({row["null_id"] for row in rows}), 52)
        self.assertEqual(sum(self.payload["control_family_counts"].values()), 52)

    def test_every_null_fails_closed_without_positive_evidence(self) -> None:
        for row in self.payload["active_null_rows"]:
            self.assertEqual(row["control_status"], "failed_closed")
            self.assertFalse(row["failed_open"])
            self.assertFalse(row["positive_evidence_admissible"])
            self.assertTrue(row["schema_instantiation_only"])
            self.assertTrue(row["derived_report_only"])
            self.assertEqual(row["source_current_inputs"], [])
            self.assertEqual(row["artifact_manifest"], [])
            self.assertEqual(row["maximum_GRR_rung"], "not_assigned")
            self.assertFalse(row["GRR_rung_assigned"])
            self.assertTrue(row["target_rule_reached"])
            self.assertEqual(row["unexpected_blockers"], [])
            self.assertEqual(
                row["observed_disposition"],
                row["expected_primary_disposition"],
            )
            self.assertEqual(row["validator_result"], "passed")

    def test_every_rule_has_a_passing_nearby_sentinel(self) -> None:
        required = self.payload["source_schema_contract"]["required_null_ids"]
        sentinels = self.payload["pass_through_sentinel_rows"]
        coverage = self.payload["rule_coverage_matrix"]
        self.assertEqual(len(sentinels), 52)
        self.assertEqual(
            [row["i2_rule_ids_exercised"][0] for row in sentinels], required
        )
        self.assertTrue(
            all(
                row["observed_disposition"] == "pass_through_fixture"
                and row["result"] == "passed"
                and not row["positive_evidence_eligible"]
                for row in sentinels
            )
        )
        self.assertEqual([row["I2_rule_id"] for row in coverage], required)
        self.assertTrue(
            all(
                len(row["atomic_null_case_ids"]) == 1
                and len(row["pass_through_sentinel_case_ids"]) == 1
                for row in coverage
            )
        )

    def test_alternative_classifications_survive_precise_rejection(self) -> None:
        rows = {row["null_id"]: row for row in self.payload["active_null_rows"]}
        expected = {
            "regenerated_W_from_retained_C_relabelled_as_durable_W_carrier": "regenerated_carrier_from_retained_state",
            "event_or_topology_change_relabelled_as_fixed_topology_retention": "eventful_history_persistence",
            "ordinary_slow_C_relaxation_relabelled_as_history_specific_carrier": "ordinary_branch_slow_relaxation",
            "branch_tangent_relocation_as_retained_carrier": "branch_tangent_neutral_displacement",
        }
        for null_id, alternative in expected.items():
            self.assertIn(
                alternative, rows[null_id]["preserved_alternative_classifications"]
            )

    def test_compound_precedence_and_control_truth_table(self) -> None:
        compounds = self.payload["compound_precedence_rows"]
        self.assertEqual(len(compounds), 4)
        self.assertTrue(
            all(
                row["result"] == "passed"
                and row["target_rule_reached"]
                and row["unexpected_blockers"] == []
                for row in compounds
            )
        )
        controls = self.payload["control_truth_table_rows"]
        self.assertEqual(len(controls), 14)
        self.assertTrue(all(row["result"] == "passed" for row in controls))
        by_case = {row["case_id"]: row for row in controls}
        self.assertEqual(
            by_case["b2_i3_control_truth_required_not_identifiable"][
                "observed_disposition"
            ],
            "required_control_not_identifiable",
        )
        self.assertFalse(
            by_case["b2_i3_control_truth_required_not_identifiable"][
                "mechanism_falsified"
            ]
        )

    def test_calibration_and_held_out_threshold_audits_are_distinct(self) -> None:
        audits = self.payload["threshold_boundary_audit_rows"]
        self.assertEqual(len(audits), 12)
        self.assertTrue(
            all(
                row["threshold_calibration_role"]
                == "held_out_boundary_audit_not_calibration"
                and row["result"] == "passed"
                for row in audits
            )
        )
        equality = [
            row for row in audits if row["boundary_variant"] == "exact_equality"
        ]
        self.assertEqual(len(equality), 4)
        self.assertTrue(
            all(
                row["observed_disposition"] == "bounded_negative"
                and row["threshold_equality_is_positive"] is False
                for row in equality
            )
        )

    def test_overlap_lineage_and_numerical_boundaries_are_typed(self) -> None:
        overlap = self.payload["partial_driver_carrier_overlap_rows"]
        self.assertEqual(len(overlap), 3)
        self.assertTrue(
            all(
                row["authored_component_excluded"]
                and not row["full_apparent_carrier_used_for_formation"]
                and row["result"] == "passed"
                for row in overlap
            )
        )
        lineage = self.payload["carrier_lineage_transport_rows"]
        self.assertEqual(len(lineage), 5)
        self.assertTrue(all(row["result"] == "passed" for row in lineage))
        numerical = self.payload["numerical_structural_boundary_rows"]
        self.assertEqual(len(numerical), 11)
        self.assertEqual(
            sum(
                row["observed_disposition"] == "numerical_failure" for row in numerical
            ),
            10,
        )
        self.assertTrue(all(row["result"] == "passed" for row in numerical))

    def test_search_closeout_and_full_history_semantics_stay_bounded(self) -> None:
        rows = self.payload["search_and_closeout_semantic_rows"]
        self.assertEqual(len(rows), 9)
        self.assertTrue(
            all(
                row["result"] == "passed" and row["extension_selected"] is False
                for row in rows
            )
        )
        by_scenario = {row["scenario"]: row for row in rows}
        self.assertEqual(
            by_scenario["preparation_event_disappears_by_k0"]["observed_disposition"],
            "outside_envelope",
        )
        self.assertEqual(
            by_scenario["preparation_clipping_disappears_by_k0"][
                "observed_disposition"
            ],
            "outside_envelope",
        )

    def test_shared_adjudicator_is_bound_for_downstream_reuse(self) -> None:
        binding = self.payload["adjudicator_binding"]
        contract = self.payload["adjudicator_contract"]
        self.assertEqual(binding["schema_version"], contract["required_schema_version"])
        self.assertEqual(len(binding["sha256"]), 64)
        self.assertTrue(contract["later_iterations_must_use_same_adjudicator_digest"])
        self.assertTrue(contract["adjudicator_change_requires_I3_rerun"])
        self.assertTrue(
            contract["scientific_rule_change_requires_I2_revision_and_reacceptance"]
        )

    def test_control_results_use_explicit_failed_closed_semantics(self) -> None:
        expected_fields = {
            "control_id",
            "control_status",
            "blocked_condition",
            "expected_result",
            "actual_result",
            "claim_allowed_when_control_triggers",
            "rung_effect",
        }
        for row in self.payload["active_null_rows"]:
            result = row["control_results"][0]
            self.assertEqual(set(result), expected_fields)
            self.assertEqual(result["control_status"], "failed_closed")
            self.assertEqual(result["expected_result"], "claim_rejected")
            self.assertEqual(result["actual_result"], "claim_rejected")
            self.assertFalse(result["claim_allowed_when_control_triggers"])

    def test_calibration_recipes_are_instantiated_without_runtime_claim(self) -> None:
        calibration = self.payload["threshold_calibration"]
        self.assertFalse(calibration["runtime_measurement_performed"])
        self.assertFalse(calibration["source_current_evidence_opened"])
        self.assertFalse(calibration["positive_search_opened"])
        self.assertTrue(calibration["all_calibrations_usable"])
        self.assertTrue(
            calibration["positive_search_must_also_apply_row_numerical_uncertainty"]
        )
        values = {
            row["threshold_id"]: row["instantiated_value"]
            for row in calibration["records"]
        }
        self.assertEqual(
            values,
            {
                "formation_contrast_floor_v1": 1e-9,
                "formation_specific_occupancy_excess_floor_v1": 1e-4,
                "oriented_interaction_component_floor_v1": 1e-9,
                "control_target_residual_ceiling_v1": 1e-8,
            },
        )
        self.assertTrue(
            all(row["fixture_uncertainty_basis"] for row in calibration["records"])
        )
        occupancy = next(
            row
            for row in calibration["records"]
            if row["threshold_id"] == "formation_specific_occupancy_excess_floor_v1"
        )
        self.assertIn("not_empirical_noise", occupancy["fixture_uncertainty_basis"])

    def test_calibration_artifact_is_semantically_bound(self) -> None:
        self.assertEqual(
            self.payload["threshold_calibration_artifact"]["payload_sha256"],
            self.calibration["payload_sha256"],
        )
        self.assertEqual(
            semantic_digest(self.calibration["payload"]),
            self.calibration["payload_sha256"],
        )

    def test_claim_boundary_stays_closed(self) -> None:
        boundary = self.payload["claim_boundary"]
        self.assertFalse(boundary["B2_positive_evidence_opened"])
        self.assertFalse(boundary["candidate_rows_classified"])
        self.assertFalse(boundary["scientific_transition_executed"])
        self.assertFalse(boundary["GRR_rung_assigned"])
        self.assertFalse(boundary["B2_closeout_rung_assigned"])
        self.assertEqual(boundary["B2_closeout_ceiling"], "B2-C2-ready")
        self.assertTrue(boundary["ready_for_iteration_4_after_acceptance"])
        self.assertFalse(boundary["extension_target_selected"])

    def test_mechanical_checks_and_serialization_pass(self) -> None:
        self.assertEqual(self.payload["validator_case_count"], 162)
        self.assertEqual(self.payload["status"], "passed")
        self.assertEqual(self.payload["failed_checks"], [])
        self.assertEqual(
            self.payload["passed_check_count"], self.payload["check_count"]
        )
        self.assertFalse(any(self.payload["unsafe_claim_flags"].values()))
        self.assertEqual(find_absolute_paths(self.payload), [])


if __name__ == "__main__":
    unittest.main()
