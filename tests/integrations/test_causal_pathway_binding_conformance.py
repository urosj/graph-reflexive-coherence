"""Focused prospective conformance and rule-isolation controls."""

from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path
from typing import Any, ClassVar

ROOT = Path(__file__).resolve().parents[2]
CHECKER_PATH = ROOT / "scripts/check_grc_lgrc_causal_pathway_binding_conformance.py"
BUILDER_PATH = ROOT / "scripts/build_phase8_causal_pathway_binding_i115.py"
POLICY_PATH = ROOT / "specs/grc-lgrc-causal-pathway-binding-conformance.json"
EVIDENCE_DIR = ROOT / "implementation/evidence/causal-pathway-binding"


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

    @classmethod
    def setUpClass(cls) -> None:
        cls.checker = _load_module("binding_conformance_checker", CHECKER_PATH)
        cls.builder = _load_module("binding_conformance_builder", BUILDER_PATH)
        cls.policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
        cls.bundle = cls.checker.load_bundle(
            ROOT,
            lock_path=EVIDENCE_DIR / "i115-native-pathway.lock.json",
            receipt_path=EVIDENCE_DIR / "i115-native-pathway.receipt.json",
        )

    def test_current_lock_and_receipt_pass_all_twenty_rules(self) -> None:
        result = self.checker.validate_bundle(
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
                result = self.checker.validate_bundle(
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
                result = self.checker.validate_bundle(
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

        result = self.checker.validate_bundle(
            ROOT,
            mutated,
            copy.deepcopy(self.policy),
        )

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

        result = self.checker.validate_bundle(
            ROOT,
            mutated,
            copy.deepcopy(self.policy),
            active_rule_ids={"BCF-020"},
        )

        self.assertEqual("failed_closed", result["status"])
        self.assertEqual({"BCF-020"}, {item["rule_id"] for item in result["issues"]})

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

        result = self.checker.validate_bundle(
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

        result = self.checker.validate_bundle(
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

        result = self.checker.validate_bundle(
            ROOT,
            mutated,
            copy.deepcopy(self.policy),
            active_rule_ids={"BCF-006"},
        )

        self.assertEqual("failed_closed", result["status"])
        self.assertEqual({"BCF-006"}, {item["rule_id"] for item in result["issues"]})

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
        self.assertEqual(
            negative["execution_digest"],
            self.checker.digest_without(negative, "execution_digest"),
        )


if __name__ == "__main__":
    unittest.main()
