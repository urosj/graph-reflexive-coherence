from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from artifact_io import read_json  # noqa: E402
from classify_claims_and_extensions import (  # noqa: E402
    CORRESPONDENCE_LEVEL_DEFINITIONS,
    IMPLEMENTATION_STATUSES,
    REQUIRED_OBJECT_IDS,
    accepted_evidence_index,
    assumption_matrix,
    bind_evidence,
    claim_classification,
    completed_traceability,
    envelope_payload,
    equivalence_classification,
    evidence_pointers_for_ids,
    final_causal_role_classification,
    final_debt_register,
    ids_in,
    protected_manifest_v8,
    source_id_map,
    validate_accepted_chain,
    validate_policy,
    validate_prerequisite,
)
from route_contradictions_and_theory_reopening import (  # noqa: E402
    contradiction_entries,
    extension_decisions,
    superseded_exploratory_claims,
    theory_reopening_decision,
)


class GRV8ClassificationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.policy = read_json(ROOT / "configs/grv8_classification_policy.json")
        cls.sources = validate_policy(cls.policy)
        cls.scope = cls.sources["scope_policy"]
        cls.evidence_index = accepted_evidence_index()
        cls.proof_ids = {
            row["proof_note_id"]
            for row in envelope_payload("proof_note_registry")["records"]
        }
        cls.assumptions = assumption_matrix(
            cls.policy, cls.sources["claim_source"]["records"]
        )
        cls.claims = claim_classification(
            cls.policy,
            cls.sources["claim_source"]["records"],
            cls.proof_ids,
            cls.scope,
            cls.evidence_index,
        )
        cls.equivalence = equivalence_classification(
            cls.policy, cls.claims["rows"], cls.scope, cls.evidence_index
        )
        cls.causal_roles = final_causal_role_classification(
            cls.scope, cls.evidence_index
        )
        cls.debts = final_debt_register(
            cls.policy,
            cls.sources["debt_source"]["records"],
            cls.scope,
            cls.evidence_index,
        )
        cls.traceability = completed_traceability(
            envelope_payload("theory_test_traceability")["records"],
            {row["claim_id"]: row for row in cls.claims["rows"]},
            cls.policy,
        )

    def test_prerequisite_and_complete_accepted_chain_are_valid(self) -> None:
        receipt, anchor = validate_prerequisite()
        self.assertEqual(receipt["receipt_payload_sha256"], anchor["receipt_payload_sha256"])
        self.assertEqual([f"GRV{index}" for index in range(8)], [row["gate_id"] for row in validate_accepted_chain()])

    def test_every_assumption_and_claim_is_classified_once(self) -> None:
        source_assumptions = self.sources["assumption_source"]["records"]
        source_claims = self.sources["claim_source"]["records"]
        self.assertEqual(len(source_assumptions), len(self.assumptions["rows"]))
        self.assertEqual(len(source_claims), len(self.claims["rows"]))
        self.assertTrue(self.claims["all_source_claim_ids_classified"])
        self.assertEqual(13, len(self.debts["rows"]))
        self.assertEqual(17, len(self.traceability["rows"]))
        self.assertTrue(
            all(row["accepted_evidence_records"] for row in self.debts["rows"])
        )

    def test_id_parser_does_not_extract_suffixes_from_other_ids(self) -> None:
        self.assertEqual([], ids_in("A-FAST-SLOW", "T"))
        self.assertEqual(["T-A01", "T-A02"], ids_in("`T-A01`, `T-A02`, `D-A01`", "T"))

    def test_failed_or_unidentifiable_assumptions_do_not_support_positive_claims(self) -> None:
        for row in self.claims["rows"]:
            if any(status in {"failed", "not_identifiable"} for status in row["assumption_statuses"].values()):
                self.assertNotEqual("bounded_supported_distinction", row["disposition"])

    def test_required_objects_and_all_six_statuses_are_present(self) -> None:
        rows = self.equivalence["rows"]
        self.assertEqual(REQUIRED_OBJECT_IDS, {row["object_id"] for row in rows})
        self.assertEqual(IMPLEMENTATION_STATUSES, {row["implementation_status"] for row in rows})
        for row in rows:
            self.assertTrue(row["maximum_supported_claim"])
            self.assertTrue(row["blocked_claims"])
            self.assertTrue(row["source_ids"])
            self.assertEqual(
                "bounded_B1_GR_unchanged_GRC9V3_evidence_envelope",
                row["classification_scope"],
            )
            self.assertTrue(row["fixture_branch_envelope"])
            self.assertTrue(row["runtime_stage"])
            self.assertTrue(row["continuous_stratum"])
            self.assertTrue(row["secondary_qualifiers"])
            self.assertTrue(row["accepted_evidence_records"])
            for evidence in row["accepted_evidence_records"]:
                self.assertRegex(evidence["source_gate"], r"^GRV[0-7]$")
                self.assertEqual(64, len(evidence["artifact_sha256"]))
                self.assertTrue(evidence["exact_field_or_row"].startswith("/payload/"))

    def test_source_ids_bind_the_controlling_files_and_digests(self) -> None:
        mapping = source_id_map()
        self.assertEqual(set(mapping), set(self.claims["source_id_map"]))
        self.assertEqual(set(mapping), set(self.equivalence["source_id_map"]))
        for record in mapping.values():
            self.assertEqual(64, len(record["sha256"]))
            self.assertTrue(record["path"].startswith("core/"))

    def test_native_readback_and_closeout_are_not_manufactured(self) -> None:
        summary = self.equivalence["summary"]
        self.assertFalse(summary["native_readback_supported"])
        self.assertFalse(summary["native_writeback_supported"])
        self.assertFalse(summary["closed_read_write_loop_supported"])
        self.assertFalse(summary["geometry_mobility_extension_opened"])
        self.assertFalse(summary["retained_carrier_extension_opened"])
        self.assertFalse(summary["oriented_current_extension_selected"])
        self.assertEqual(
            "exact_native_mechanism_distinct_from_core_readback",
            summary["current_recurrence_classification"],
        )
        self.assertEqual(
            "analogy_only_candidate_mapping_rejected",
            summary["j_equals_J_C_runtime_mapping"],
        )
        self.assertTrue(summary["reduced_spatial_continuation_non_equivalence_supported"])
        self.assertTrue(summary["reduced_structural_discrete_threshold_non_equivalence_supported"])
        self.assertFalse(summary["runtime_spatial_vs_full_temporal_non_equivalence_supported"])
        self.assertFalse(summary["full_map_non_equivalence_supported"])

    def test_j_equals_J_C_is_not_promoted_from_variable_reuse(self) -> None:
        rows = {row["object_id"]: row for row in self.equivalence["rows"]}
        self.assertEqual(
            "already_implemented_exactly",
            rows["native_current_recurrence"]["implementation_status"],
        )
        self.assertEqual(
            "implemented_only_analogically",
            rows["j_equals_J_C_limit"]["implementation_status"],
        )
        self.assertIn(
            "candidate_mapping_rejected",
            rows["j_equals_J_C_limit"]["secondary_qualifiers"],
        )

    def test_correspondence_level_wording_is_frozen_exactly(self) -> None:
        self.assertEqual(
            CORRESPONDENCE_LEVEL_DEFINITIONS,
            self.equivalence["correspondence_level_definitions"],
        )
        object_rows = {
            row["object_id"]: row for row in self.equivalence["rows"]
        }
        for claim in self.claims["rows"]:
            for binding in claim["object_correspondences"]:
                source = object_rows[binding["object_id"]]
                self.assertEqual(
                    source["correspondence_level"], binding["correspondence_level"]
                )
                self.assertEqual(
                    source["implementation_status"], binding["implementation_status"]
                )

    def test_arrow_by_arrow_roles_preserve_GRR2_ceiling(self) -> None:
        rows = {row["role_id"]: row for row in self.causal_roles["rows"]}
        self.assertEqual(9, len(rows))
        self.assertEqual("supported_bounded_GRR2", rows["post_activity_persistence"]["status"])
        self.assertEqual(
            "unsupported_in_tested_native_path",
            rows["W_mediated_later_response"]["status"],
        )
        self.assertFalse(self.causal_roles["summary"]["native_readback_supported"])
        self.assertTrue(self.causal_roles["summary"]["branch_relocation_rival_unresolved"])
        self.assertFalse(
            self.causal_roles["summary"]["cross_gate_synthesis_creates_positive_arrow"]
        )

    def test_extension_and_theory_routes_preserve_the_boundary(self) -> None:
        decisions = {row["decision_id"]: row for row in extension_decisions(self.policy)}
        self.assertEqual("remain_explicitly_diagnostic", decisions["EXT-K"]["route"])
        self.assertTrue(decisions["EXT-GEOMETRY-MOBILITY"]["route"].startswith("not_opened"))
        self.assertTrue(decisions["EXT-RETAINED-CARRIER"]["route"].startswith("not_opened"))
        self.assertTrue(decisions["EXT-ORIENTED-CURRENT"]["route"].startswith("conditionally_selectable"))
        self.assertTrue(decisions["EXT-CURRENT-TEMPORALIZATION"]["route"].startswith("conditionally_selectable"))
        self.assertEqual(
            "unchanged_runtime_constructibility_search_before_extension",
            decisions["EXT-UNCHANGED-CONSTRUCTIBILITY"]["route"],
        )
        self.assertFalse(decisions["EXT-GEOMETRY-MOBILITY"]["verified_observable_blocked_by_conflation"])
        self.assertEqual(
            "temporalized_W_versus_new_M_theoretically_underdetermined",
            decisions["EXT-RETAINED-CARRIER"]["realization_choice"],
        )
        self.assertEqual("no_theory_reopening_required", theory_reopening_decision(self.policy)["route"])
        self.assertTrue(all(not row["theory_contradicted"] for row in contradiction_entries()))
        for row in contradiction_entries():
            self.assertTrue(row["assumption_statuses"])
            self.assertTrue(row["rejected_routes"])
            self.assertTrue(row["required_next_action"])

    def test_contradiction_and_extension_rows_bind_exact_accepted_fields(self) -> None:
        for row in contradiction_entries():
            records = bind_evidence(
                evidence_pointers_for_ids(
                    self.policy, self.scope, claim_ids=row["claim_ids"]
                ),
                self.evidence_index,
            )
            self.assertTrue(records)
        for row in extension_decisions(self.policy):
            records = bind_evidence(
                evidence_pointers_for_ids(
                    self.policy, self.scope, debt_ids=row["debt_ids"]
                ),
                self.evidence_index,
            )
            self.assertTrue(records)

    def test_lgrc_boundary_is_two_sided_and_does_not_authorize_execution(self) -> None:
        boundary = self.scope["lgrc_boundary_candidate"]
        partition = self.scope["lgrc_route_partition"]
        self.assertTrue(boundary["positive_inherited_grc_base"])
        self.assertTrue(boundary["negative_or_blocked_grc_boundaries"])
        self.assertTrue(boundary["lgrc_only_questions"])
        self.assertFalse(boundary["final_handoff_emitted"])
        self.assertFalse(partition["same_question"])
        self.assertFalse(partition["B1_L_execution_authorized"])
        self.assertEqual(6, len(self.scope["forbidden_lgrc_relabels"]))

    def test_superseded_claims_preserve_reason_and_disposition(self) -> None:
        rows = superseded_exploratory_claims()
        self.assertTrue(any(row["exploratory_claim_id"] == "SX-GRV8-001" for row in rows))
        for row in rows:
            self.assertTrue(row["reason_superseded"])
            self.assertTrue(row["disposition"])
            self.assertTrue(row["supporting_gate_artifacts"])

    def test_protected_manifest_is_an_unchanged_successor(self) -> None:
        manifest = protected_manifest_v8()
        self.assertTrue(manifest["payload"]["unchanged_successor"])
        self.assertEqual(
            "b1_grv8_protected_paths_v8", manifest["payload"]["manifest_id"]
        )

    def test_grv8_schema_exposes_the_exact_status_enums(self) -> None:
        schema = json.loads((ROOT / "schemas/grv8_classification.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(IMPLEMENTATION_STATUSES, set(schema["$defs"]["implementationStatus"]["enum"]))


if __name__ == "__main__":
    unittest.main()
