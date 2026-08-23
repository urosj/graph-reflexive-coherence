"""Focused tests for the B2-GR Iteration 2 schema freeze."""

from __future__ import annotations

from pathlib import Path
import re
import sys
import unittest


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = EXPERIMENT_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from b2_artifact_io import find_absolute_paths, git, semantic_digest  # noqa: E402
from build_i2_constructibility_schema import (  # noqa: E402
    ACTIVE_NULLS,
    REQUIRED_CANDIDATE_FIELDS,
    build_payload,
    field_schema,
)


class I2ConstructibilitySchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_payload(git("rev-parse", "HEAD"))

    def test_i1_acceptance_and_protected_runtime_are_bound(self) -> None:
        source = self.payload["source_contract"]
        self.assertEqual(source["I1_acceptance_status"], "accepted")
        self.assertEqual(source["I1_assigned_closeout_rung"], "B2-C0")
        self.assertEqual(source["accepted_B1_branch_population_count"], 48)
        self.assertTrue(source["protected_manifest_live_verification"])

    def test_complete_candidate_schema_is_typed(self) -> None:
        fields = field_schema()
        self.assertEqual(set(fields), set(REQUIRED_CANDIDATE_FIELDS))
        self.assertGreaterEqual(len(fields), 120)
        self.assertTrue(all(row["required"] and row["type"] for row in fields.values()))
        self.assertFalse(fields["derived_report_only"]["positive_required_value"])
        self.assertEqual(
            fields["artifact_sha256_status"]["positive_required_value"], "all_match"
        )

    def test_candidate_schema_contains_every_plan_required_field(self) -> None:
        plan = (
            EXPERIMENT_ROOT
            / "implementation/GRC9V3RetentionMediationConstructibilityPlan.md"
        ).read_text(encoding="utf-8")
        section = plan.split("## 7. Required Candidate Record", 1)[1]
        block = re.search(r"```text\n(.*?)```", section, re.DOTALL)
        self.assertIsNotNone(block)
        planned_fields = {
            line.strip() for line in block.group(1).splitlines() if line.strip()
        }
        self.assertEqual(planned_fields - set(REQUIRED_CANDIDATE_FIELDS), set())

    def test_grr_and_closeout_ladders_are_separate_and_complete(self) -> None:
        self.assertEqual(
            list(self.payload["GRR_ladder"]["rungs"]), [f"GRR{i}" for i in range(6)]
        )
        self.assertFalse(self.payload["GRR_ladder"]["redefined_by_B2"])
        self.assertFalse(
            self.payload["GRR_ladder"]["cross_lineage_composition_allowed"]
        )
        self.assertEqual(
            list(self.payload["B2_closeout_ladder"]), [f"B2-C{i}" for i in range(7)]
        )

    def test_carrier_set_is_finite_and_temporally_admissible(self) -> None:
        carriers = self.payload["carrier_schema"]
        self.assertEqual(
            [row["carrier_definition_id"] for row in carriers],
            [
                "C_ZERO_SUM_V1",
                "W_EDGE_CONDUCTANCE_OBSERVATION_V1",
                "JOINT_C_W_BLOCK_V1",
            ],
        )
        self.assertTrue(carriers[0]["independent_causal_coordinate"])
        self.assertFalse(carriers[1]["independent_causal_coordinate"])
        self.assertFalse(carriers[2]["independent_causal_coordinate"])
        temporal = self.payload["temporal_operator_schema"]
        self.assertFalse(temporal["independent_W_or_J_coordinates_allowed"])
        self.assertEqual(temporal["projector_policy"], "fixed_reference_projector")
        self.assertFalse(
            temporal["projector_recomputation_to_follow_candidate_allowed"]
        )

    def test_search_envelope_is_predeclared_and_exhaustive(self) -> None:
        envelope = self.payload["search_envelope"]
        self.assertEqual(envelope["source_branch_count"], 48)
        self.assertEqual(
            envelope["search_algorithm"], "deterministic_lexicographic_exhaustive_grid"
        )
        self.assertEqual(envelope["maximum_discovery_rows"], 9648)
        self.assertEqual(
            envelope["discovery_row_count_breakdown"],
            {
                "native_spontaneous_rows": 48,
                "source_total_oriented_edge_count": 160,
                "base_C_pulse_rows": 1920,
                "temporary_parameter_history_rows": 7680,
                "formula": "48 + (160 * 3 amplitudes * 4 history lengths) + (160 * 3 amplitudes * 4 parameter variants * 4 history lengths)",
                "total": 9648,
            },
        )
        self.assertEqual(envelope["history_lengths_native_steps"], [1, 2, 4, 8])
        self.assertEqual(
            envelope["persistence_horizons_native_steps"], [1, 2, 4, 8, 16, 32]
        )
        self.assertIn("without_ranking", envelope["source_branch_rule"])
        self.assertIn("all_48", envelope["symmetry_rule"])

    def test_driver_carrier_and_branch_rules_fail_closed(self) -> None:
        for carrier in self.payload["carrier_schema"]:
            self.assertIn("driver_carrier_overlap_effect", carrier)
        relation = self.payload["branch_relation_schema"]
        self.assertTrue(relation["parameter_continuation_tangent_recorded_separately"])
        self.assertEqual(
            relation["primary_positive_class"],
            "same_branch_transverse_retention_candidate",
        )
        self.assertFalse(
            self.payload["carrier_lineage_schema"][
                "cross_row_or_lane_rung_composition_allowed"
            ]
        )

    def test_probe_contract_requires_incremental_matched_read_before_rewrite(
        self,
    ) -> None:
        probe = self.payload["probe_schema"]
        self.assertTrue(probe["difference_in_differences_required"])
        self.assertTrue(probe["zero_probe_baseline_required"])
        self.assertFalse(probe["zero_probe_is_core_passive_null"])
        self.assertTrue(probe["read_before_rewrite_required"])
        self.assertGreaterEqual(len(probe["full_noncarrier_state_blocks"]), 10)
        self.assertIn(
            "synthetic_counterfactual_match", probe["pair_provenance_diagnostic_only"]
        )

    def test_control_replay_and_persistence_semantics_are_closed(self) -> None:
        controls = self.payload["control_applicability_schema"]["all_carriers"]
        self.assertIn("specific_mediation_claim_only", controls["bypass"])
        self.assertEqual(
            self.payload["replay_schema"]["required_modes"],
            [
                "artifact_replay",
                "snapshot_load_replay",
                "duplicate_replay",
                "fresh_process_replay",
            ],
        )
        self.assertEqual(
            self.payload["persistence_classes"],
            [
                "passive_retention",
                "activity_maintained_retention",
                "regenerated_carrier_from_retained_state",
                "transferred_retention",
                "externally_maintained_difference",
            ],
        )

    def test_active_null_surface_and_claim_boundary_are_complete(self) -> None:
        nulls = self.payload["active_null_schema"]
        self.assertEqual([row["null_id"] for row in nulls], list(ACTIVE_NULLS))
        self.assertTrue(all(row["required_status"] == "failed_closed" for row in nulls))
        boundary = self.payload["claim_boundary"]
        self.assertFalse(boundary["B2_positive_evidence_opened"])
        self.assertFalse(boundary["GRR_rung_assigned"])
        self.assertFalse(boundary["B2_closeout_rung_assigned"])
        self.assertEqual(boundary["B2_closeout_ceiling"], "B2-C1-ready")
        self.assertFalse(any(self.payload["unsafe_claim_flags"].values()))

    def test_mechanical_checks_and_serializability_pass(self) -> None:
        self.assertEqual(self.payload["status"], "passed")
        self.assertEqual(self.payload["failed_checks"], [])
        self.assertEqual(
            self.payload["passed_check_count"], self.payload["check_count"]
        )
        self.assertEqual(find_absolute_paths(self.payload), [])
        self.assertEqual(
            semantic_digest(self.payload), semantic_digest(dict(self.payload))
        )


if __name__ == "__main__":
    unittest.main()
