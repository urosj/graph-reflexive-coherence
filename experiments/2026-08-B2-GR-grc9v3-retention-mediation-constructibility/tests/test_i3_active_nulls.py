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
        self.assertEqual(self.payload["status"], "passed")
        self.assertEqual(self.payload["failed_checks"], [])
        self.assertEqual(
            self.payload["passed_check_count"], self.payload["check_count"]
        )
        self.assertFalse(any(self.payload["unsafe_claim_flags"].values()))
        self.assertEqual(find_absolute_paths(self.payload), [])


if __name__ == "__main__":
    unittest.main()
