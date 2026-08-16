"""Focused prospective conformance and rule-isolation controls."""

from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path
from typing import Any, ClassVar, cast

ROOT = Path(__file__).resolve().parents[2]
CHECKER_PATH = ROOT / "scripts/check_grc_lgrc_causal_pathway_binding_conformance.py"
BUILDER_PATH = ROOT / "scripts/build_phase8_causal_pathway_binding_i115.py"
POLICY_PATH = ROOT / "specs/grc-lgrc-causal-pathway-binding-conformance.json"
EVIDENCE_DIR = ROOT / "implementation/evidence/causal-pathway-binding"
ACCEPTANCE_ANCHOR_PATH = EVIDENCE_DIR / "binding-acceptance-anchor.json"
TRUSTED_ACCEPTANCE_ANCHOR_DIGEST = (
    "127382ebd0b8f70a5990971190bec5de614f39f03b47c7ffaffe4f53e5970ae2"
)


def _load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CausalPathwayBindingConformanceTest(unittest.TestCase):
    """Validate current artifacts and every deliberate fail-closed mutation."""

    checker: ClassVar[Any]
    builder: ClassVar[Any]
    policy: ClassVar[dict[str, Any]]
    bundle: ClassVar[dict[str, Any]]
    acceptance_anchor: ClassVar[dict[str, Any]]

    @classmethod
    def setUpClass(cls) -> None:
        cls.checker = _load_module("binding_conformance_checker", CHECKER_PATH)
        cls.builder = _load_module("binding_conformance_builder", BUILDER_PATH)
        cls.policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
        cls.acceptance_anchor = json.loads(
            ACCEPTANCE_ANCHOR_PATH.read_text(encoding="utf-8")
        )
        cls.bundle = cls.checker.load_bundle(
            ROOT,
            lock_path=EVIDENCE_DIR / "i115-native-pathway.lock.json",
            receipt_path=EVIDENCE_DIR / "i115-native-pathway.receipt.json",
        )

    def _validate(
        self,
        root: Path,
        bundle: dict[str, Any],
        policy: dict[str, Any],
        active_rule_ids: set[str] | None = None,
    ) -> dict[str, Any]:
        return cast(
            dict[str, Any],
            self.checker.validate_bundle(
                root,
                bundle,
                policy,
                active_rule_ids=active_rule_ids,
                acceptance_anchor=copy.deepcopy(self.acceptance_anchor),
                trusted_anchor_digest=TRUSTED_ACCEPTANCE_ANCHOR_DIGEST,
            ),
        )

    def test_current_lock_and_receipt_pass_all_twenty_rules(self) -> None:
        result = self._validate(
            ROOT,
            copy.deepcopy(self.bundle),
            copy.deepcopy(self.policy),
        )

        self.assertEqual("passed", result["status"])
        self.assertEqual(20, result["passed_rule_count"])
        self.assertEqual(0, result["failed_rule_count"])
        self.assertEqual("current", result["binding_staleness_state"])
        self.assertFalse(result["claim_qualified_artifacts_blocked"])

    def test_all_twenty_negative_controls_fail_their_target_rule(self) -> None:
        for case_id, _, expected_rule in self.builder.NEGATIVE_CASES:
            with self.subTest(case_id=case_id, expected_rule=expected_rule):
                mutated = copy.deepcopy(self.bundle)
                self.builder.apply_negative_mutation(case_id, mutated)
                result = self._validate(
                    ROOT,
                    mutated,
                    copy.deepcopy(self.policy),
                )
                triggered = {issue["rule_id"] for issue in result["issues"]}
                self.assertEqual("failed_closed", result["status"])
                self.assertIn(expected_rule, triggered)

    def test_all_twenty_controls_reject_under_target_only_isolation(self) -> None:
        for case_id, _, expected_rule in self.builder.NEGATIVE_CASES:
            with self.subTest(case_id=case_id, expected_rule=expected_rule):
                mutated = copy.deepcopy(self.bundle)
                self.builder.apply_negative_mutation(case_id, mutated)
                result = self._validate(
                    ROOT,
                    mutated,
                    copy.deepcopy(self.policy),
                    active_rule_ids={expected_rule},
                )
                triggered = {issue["rule_id"] for issue in result["issues"]}
                self.assertEqual("failed_closed", result["status"])
                self.assertEqual({expected_rule}, triggered)

    def test_binding_source_drift_becomes_stale_pending_review(self) -> None:
        mutated = copy.deepcopy(self.bundle)
        self.builder.apply_negative_mutation("BNC-014", mutated)

        result = self._validate(
            ROOT,
            mutated,
            copy.deepcopy(self.policy),
        )

        self.assertEqual("stale_pending_review", result["binding_staleness_state"])
        self.assertTrue(result["claim_qualified_artifacts_blocked"])

    def test_current_bundle_without_external_anchor_stays_pending_review(self) -> None:
        result = self.checker.validate_bundle(
            ROOT,
            copy.deepcopy(self.bundle),
            copy.deepcopy(self.policy),
        )

        self.assertEqual("failed_closed", result["status"])
        self.assertEqual("stale_pending_review", result["binding_staleness_state"])
        self.assertEqual(
            {"BCF-014"},
            {item["rule_id"] for item in result["issues"]},
        )

    def test_coordinated_p1_to_p2_map_and_policy_edit_stays_pending(self) -> None:
        mutated = copy.deepcopy(self.bundle)
        policy = copy.deepcopy(self.policy)
        stage = next(
            item
            for item in mutated["bindings"]["stage_bindings"]
            if item["pathway_id"] == "lgrc9v3.explicit_packet_transport"
            and item["stage_id"] == "packet_schedule"
        )
        stage["symbols"][0]["qualified_symbol"] = "LGRC9V3.step"
        map_digest = self.checker.digest_without(
            mutated["bindings"],
            "binding_map_digest",
        )
        mutated["bindings"]["binding_map_digest"] = map_digest
        policy["accepted_digests"]["binding_map_digest"] = map_digest
        policy["policy_digest"] = self.checker.digest_without(
            policy,
            "policy_digest",
        )
        for artifact_name in ("lock", "receipt"):
            mutated[artifact_name]["binding_map_digest"] = map_digest

        result = self._validate(
            ROOT,
            mutated,
            policy,
            active_rule_ids={"BCF-014"},
        )

        self.assertEqual("failed_closed", result["status"])
        self.assertEqual("stale_pending_review", result["binding_staleness_state"])
        self.assertTrue(result["claim_qualified_artifacts_blocked"])
        self.assertTrue(
            any(
                item["location"] == "binding_acceptance_anchor"
                and "pending independent review" in item["message"]
                for item in result["issues"]
            )
        )

    def test_coordinated_false_revision_readmission_stays_pending(self) -> None:
        mutated = copy.deepcopy(self.bundle)
        policy = copy.deepcopy(self.policy)
        false_revision = "0" * 40
        mutated["bindings"]["source_revision"] = false_revision
        map_digest = self.checker.digest_without(
            mutated["bindings"],
            "binding_map_digest",
        )
        mutated["bindings"]["binding_map_digest"] = map_digest
        policy["accepted_digests"]["binding_map_digest"] = map_digest
        policy["policy_digest"] = self.checker.digest_without(
            policy,
            "policy_digest",
        )
        for artifact_name in ("lock", "receipt"):
            mutated[artifact_name]["source_revision"] = false_revision
            mutated[artifact_name]["binding_map_digest"] = map_digest

        result = self._validate(
            ROOT,
            mutated,
            policy,
            active_rule_ids={"BCF-014"},
        )

        self.assertEqual("failed_closed", result["status"])
        self.assertEqual("stale_pending_review", result["binding_staleness_state"])
        self.assertTrue(result["claim_qualified_artifacts_blocked"])

    def test_whole_run_claim_scope_fails_bcf020_in_isolation(self) -> None:
        mutated = copy.deepcopy(self.bundle)
        receipt = mutated["receipt"]
        receipt["claim_scope"] = "whole_run"
        receipt["whole_run_causal_closure_claimed"] = True
        receipt["receipt_digest"] = self.checker.digest_without(
            receipt, "receipt_digest"
        )

        result = self._validate(
            ROOT,
            mutated,
            copy.deepcopy(self.policy),
            active_rule_ids={"BCF-020"},
        )

        self.assertEqual("failed_closed", result["status"])
        self.assertEqual({"BCF-020"}, {item["rule_id"] for item in result["issues"]})

    def test_false_noop_and_unknown_effect_forgeries_fail_bcf020(self) -> None:
        for case_id, _ in self.builder.EFFECT_OUTCOME_CASES:
            with self.subTest(case_id=case_id):
                mutated = copy.deepcopy(self.bundle)
                self.builder.apply_effect_outcome_mutation(case_id, mutated)
                result = self._validate(
                    ROOT,
                    mutated,
                    copy.deepcopy(self.policy),
                    active_rule_ids={"BCF-020"},
                )

                self.assertEqual("failed_closed", result["status"])
                self.assertEqual(
                    {"BCF-020"},
                    {item["rule_id"] for item in result["issues"]},
                )

    def test_invocation_callable_identity_drift_fails_bcf016(self) -> None:
        mutated = copy.deepcopy(self.bundle)
        receipt = mutated["receipt"]
        invocation = receipt["actual_stage_symbol_invocations"][0]
        invocation["callable_identity"]["qualified_symbol"] = "LGRC9V3.step"
        invocation["callable_identity"]["callable_identity_digest"] = (
            self.checker.digest_without(
                invocation["callable_identity"], "callable_identity_digest"
            )
        )
        receipt["receipt_digest"] = self.checker.digest_without(
            receipt, "receipt_digest"
        )

        result = self._validate(
            ROOT,
            mutated,
            copy.deepcopy(self.policy),
            active_rule_ids={"BCF-016"},
        )

        self.assertEqual("failed_closed", result["status"])
        self.assertEqual({"BCF-016"}, {item["rule_id"] for item in result["issues"]})

    def test_cmp26_edge_without_crossing_invocation_fails_bcf019(self) -> None:
        mutated = self.checker.load_bundle(
            ROOT,
            lock_path=EVIDENCE_DIR / "i116/03-explicit-adapter-cmp26.lock.json",
            receipt_path=(EVIDENCE_DIR / "i116/03-explicit-adapter-cmp26.receipt.json"),
        )
        receipt = mutated["receipt"]
        receipt["actual_composition_crossing_invocations"] = []
        receipt["receipt_digest"] = self.checker.digest_without(
            receipt,
            "receipt_digest",
        )

        result = self._validate(
            ROOT,
            mutated,
            copy.deepcopy(self.policy),
            active_rule_ids={"BCF-019"},
        )

        self.assertEqual("failed_closed", result["status"])
        self.assertEqual({"BCF-019"}, {item["rule_id"] for item in result["issues"]})

    def test_cmp26_crossing_identity_drift_fails_bcf006(self) -> None:
        mutated = self.checker.load_bundle(
            ROOT,
            lock_path=EVIDENCE_DIR / "i116/03-explicit-adapter-cmp26.lock.json",
            receipt_path=(EVIDENCE_DIR / "i116/03-explicit-adapter-cmp26.receipt.json"),
        )
        crossing = mutated["receipt"]["actual_composition_crossing_invocations"][0]
        crossing["symbol_id"] = "CMP-26:crossing:forged"
        mutated["receipt"]["receipt_digest"] = self.checker.digest_without(
            mutated["receipt"],
            "receipt_digest",
        )

        result = self._validate(
            ROOT,
            mutated,
            copy.deepcopy(self.policy),
            active_rule_ids={"BCF-006"},
        )

        self.assertEqual("failed_closed", result["status"])
        self.assertEqual({"BCF-006"}, {item["rule_id"] for item in result["issues"]})

    def test_candidate_without_scoped_witness_fails_bcf004(self) -> None:
        mutated = self.checker.load_bundle(
            ROOT,
            lock_path=EVIDENCE_DIR / "i116/08-unregistered-candidate.lock.json",
            receipt_path=(EVIDENCE_DIR / "i116/08-unregistered-candidate.receipt.json"),
        )
        candidate = mutated["receipt"]["candidate_relations_exercised"][0]
        candidate.pop("candidate_execution_witness")
        mutated["receipt"]["receipt_digest"] = self.checker.digest_without(
            mutated["receipt"],
            "receipt_digest",
        )

        result = self._validate(
            ROOT,
            mutated,
            copy.deepcopy(self.policy),
            active_rule_ids={"BCF-004"},
        )

        self.assertEqual("failed_closed", result["status"])
        self.assertEqual({"BCF-004"}, {item["rule_id"] for item in result["issues"]})

    def test_renamed_cmp05_candidate_relabel_fails_bcf011(self) -> None:
        mutated = self.checker.load_bundle(
            ROOT,
            lock_path=EVIDENCE_DIR / "i116/08-unregistered-candidate.lock.json",
            receipt_path=(EVIDENCE_DIR / "i116/08-unregistered-candidate.receipt.json"),
        )
        declaration = mutated["lock"]["candidate_declarations"][0]
        use = mutated["receipt"]["candidate_relations_exercised"][0]
        for candidate in (declaration, use):
            candidate["consumed_admitted_pathway_ids"] = [
                "lgrc9v3.diagnostic_grc_reconstruction",
                "lgrc9v3.explicit_packet_transport",
            ]
            candidate["proposed_source_pathway_id"] = (
                "lgrc9v3.diagnostic_grc_reconstruction"
            )
            candidate["proposed_target_pathway_id"] = (
                "lgrc9v3.explicit_packet_transport"
            )
            candidate["proposed_relation"] = (
                "diagnostic_as_behavior and native packet admission"
            )
            candidate["invalid_relabel_conflict_ids"] = ["CMP-05"]
        mutated["lock"]["lock_digest"] = self.checker.digest_without(
            mutated["lock"],
            "lock_digest",
        )
        mutated["receipt"]["binding_lock_digest"] = mutated["lock"]["lock_digest"]
        mutated["receipt"]["receipt_digest"] = self.checker.digest_without(
            mutated["receipt"],
            "receipt_digest",
        )

        result = self._validate(
            ROOT,
            mutated,
            copy.deepcopy(self.policy),
            active_rule_ids={"BCF-011"},
        )

        self.assertEqual("failed_closed", result["status"])
        self.assertEqual({"BCF-011"}, {item["rule_id"] for item in result["issues"]})

    def test_dynamic_c_forged_into_ab_scope_fails_bcf017(self) -> None:
        mutated = self.checker.load_bundle(
            ROOT,
            lock_path=EVIDENCE_DIR / "i116/09-dynamic-a-b-choice.lock.json",
            receipt_path=EVIDENCE_DIR / "i116/09-dynamic-a-b-choice.receipt.json",
        )
        alternative_use = mutated["receipt"]["allowed_pathway_alternatives_actual_use"][
            0
        ]
        c_pathway_id = "grc9v3.synchronous_update_cycle"
        alternative_use["selection_scopes"][0]["selected_pathway_id"] = c_pathway_id
        alternative_use["selected_pathway_ids"] = [c_pathway_id]
        alternative_use["actual_pathway_ids_used"] = [c_pathway_id]
        mutated["receipt"]["receipt_digest"] = self.checker.digest_without(
            mutated["receipt"],
            "receipt_digest",
        )

        result = self._validate(
            ROOT,
            mutated,
            copy.deepcopy(self.policy),
            active_rule_ids={"BCF-017"},
        )

        self.assertEqual("failed_closed", result["status"])
        self.assertEqual({"BCF-017"}, {item["rule_id"] for item in result["issues"]})

    def test_unscoped_dynamic_witness_fails_bcf017(self) -> None:
        mutated = self.checker.load_bundle(
            ROOT,
            lock_path=EVIDENCE_DIR / "i116/09-dynamic-a-b-choice.lock.json",
            receipt_path=EVIDENCE_DIR / "i116/09-dynamic-a-b-choice.receipt.json",
        )
        invocation = next(
            item
            for item in mutated["receipt"]["actual_stage_symbol_invocations"]
            if item["alternative_selection_scope_id"] is not None
        )
        invocation["alternative_selection_scope_id"] = None
        mutated["receipt"]["receipt_digest"] = self.checker.digest_without(
            mutated["receipt"],
            "receipt_digest",
        )

        result = self._validate(
            ROOT,
            mutated,
            copy.deepcopy(self.policy),
            active_rule_ids={"BCF-017"},
        )

        self.assertEqual("failed_closed", result["status"])
        self.assertEqual({"BCF-017"}, {item["rule_id"] for item in result["issues"]})

    def test_frozen_execution_records_are_canonical_and_passed(self) -> None:
        execution = json.loads(
            (EVIDENCE_DIR / "i115-conformance-execution.json").read_text(
                encoding="utf-8"
            )
        )
        negative = json.loads(
            (EVIDENCE_DIR / "i115-negative-control-execution.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual("passed", execution["status"])
        self.assertEqual(
            execution["conformance_digest"],
            self.checker.digest_without(execution, "conformance_digest"),
        )
        self.assertEqual("passed", negative["status"])
        self.assertEqual(20, negative["control_count"])
        self.assertEqual(20, negative["rule_isolation_control_count"])
        self.assertEqual(0, negative["failed_open_count"])
        self.assertEqual(0, negative["rule_isolation_failed_open_count"])
        self.assertEqual(2, negative["independent_anchor_control_count"])
        self.assertEqual(0, negative["independent_anchor_failed_open_count"])
        self.assertEqual(3, negative["effect_outcome_control_count"])
        self.assertEqual(0, negative["effect_outcome_failed_open_count"])
        self.assertEqual(
            negative["execution_digest"],
            self.checker.digest_without(negative, "execution_digest"),
        )


if __name__ == "__main__":
    unittest.main()
