"""Focused prospective conformance and rule-isolation controls."""

from __future__ import annotations

import copy
import importlib
import importlib.util
import json
import unittest
from pathlib import Path
from typing import Any, ClassVar, cast

from pygrc.causal_pathways import SourceSymbolBinding

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
        *,
        trusted_execution_transcript_digest: str | None = None,
        trusted_candidate_review_digests: tuple[str, ...] = (),
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
                trusted_execution_transcript_digest=(
                    trusted_execution_transcript_digest
                ),
                trusted_candidate_review_digests=(
                    trusted_candidate_review_digests
                ),
            ),
        )

    def _reseal(self, bundle: dict[str, Any]) -> None:
        bundle["lock"]["lock_digest"] = self.checker.digest_without(
            bundle["lock"],
            "lock_digest",
        )
        bundle["receipt"]["binding_lock_digest"] = bundle["lock"]["lock_digest"]
        receipt = bundle["receipt"]
        receipt["execution_transcript_digest"] = (
            self.checker.execution_transcript_digest(
                binding_lock_digest=receipt["binding_lock_digest"],
                stage_invocations=receipt["actual_stage_symbol_invocations"],
                crossing_invocations=receipt[
                    "actual_composition_crossing_invocations"
                ],
                candidate_mechanism_invocations=receipt[
                    "actual_candidate_mechanism_invocations"
                ],
            )
        )
        bundle["receipt"]["receipt_digest"] = self.checker.digest_without(
            bundle["receipt"],
            "receipt_digest",
        )

    def _install_round3_cmp05_noop_claim(
        self,
        bundle: dict[str, Any],
    ) -> str:
        """Coherently reseal the exact synonym/no-op Round 3 falsifier."""

        candidate_id = "experiment.i116.packet_to_snapshot_relation"
        relation = "forensic reconstruction dictates routine packet conduct"
        evidence_path = Path(
            "tests/fixtures/causal_pathway_candidate_cmp05_synonym_noop_evidence.json"
        )
        evidence_artifact = json.loads(
            (ROOT / evidence_path).read_text(encoding="utf-8")
        )
        evidence = {
            "evidence_kind": "executable_candidate_mechanism",
            "mechanism_id": evidence_artifact["mechanism_id"],
            "path": evidence_path.as_posix(),
            "sha256": self.checker.sha256_file(ROOT / evidence_path),
        }
        executable = evidence_artifact["executable_symbol"]
        symbol = SourceSymbolBinding.from_record(executable)
        module = importlib.import_module(executable["module"])
        target = getattr(module, executable["qualified_symbol"])
        mechanism_link = {
            "mechanism_id": evidence["mechanism_id"],
            **executable,
            "callable_identity": symbol.callable_identity(
                target,
                ROOT,
            ).to_record(),
        }
        review: dict[str, Any] = {
            "artifact": "causal-pathway-candidate-relation-review",
            "schema_version": "causal_pathway_candidate_relation_review_v1",
            "review_id": "round3-audit-synonym-noop-review",
            "reviewer": "independent-round3-fixture",
            "review_status": "accepted_structural_distinction",
            "candidate_id": candidate_id,
            "candidate_kind": "composition",
            "proposed_source_pathway_id": (
                "lgrc9v3.diagnostic_grc_reconstruction"
            ),
            "proposed_target_pathway_id": (
                "lgrc9v3.explicit_packet_transport"
            ),
            "proposed_relation": relation,
            "invalid_relabel_conflict_ids": ["CMP-05"],
            "invalid_relabel_blocked_claims": [
                "diagnostic_as_behavior",
                "native packet admission",
            ],
            "mechanism_evidence": {
                field: evidence[field]
                for field in ("mechanism_id", "path", "sha256")
            },
            "structural_distinction": {
                "distinction_kind": "reviewed_external_adapter",
                "source_binding": "candidate_callable_consumes_source_result",
                "mechanism_effect": "distinct_nonempty_mapping_result",
                "target_binding": "candidate_result_supplies_follow_on_request",
            },
        }
        review_digest = str(
            self.checker.digest_without(review, "review_digest")
        )
        review["review_digest"] = review_digest
        declaration = bundle["lock"]["candidate_declarations"][0]
        use = bundle["receipt"]["candidate_relations_exercised"][0]
        for candidate in (declaration, use):
            candidate["consumed_admitted_pathway_ids"] = [
                "lgrc9v3.diagnostic_grc_reconstruction",
                "lgrc9v3.explicit_packet_transport",
            ]
            candidate["proposed_source_pathway_id"] = review[
                "proposed_source_pathway_id"
            ]
            candidate["proposed_target_pathway_id"] = review[
                "proposed_target_pathway_id"
            ]
            candidate["proposed_relation"] = relation
            candidate["mechanism_evidence"] = copy.deepcopy(evidence)
            candidate["candidate_mechanism_link"] = copy.deepcopy(
                mechanism_link
            )
            candidate["invalid_relabel_conflict_ids"] = ["CMP-05"]
            candidate["invalid_relabel_blocked_claims"] = [
                "diagnostic_as_behavior",
                "native packet admission",
            ]
            candidate["blocked_claims"] = list(
                dict.fromkeys(
                    [
                        *candidate["blocked_claims"],
                        "diagnostic_as_behavior",
                        "native packet admission",
                    ]
                )
            )
            candidate["invalid_relabel_relation_review"] = copy.deepcopy(
                review
            )
            candidate[
                "invalid_relabel_relation_review_trust_requirement"
            ] = self.checker.INVALID_RELABEL_CANDIDATE_REVIEW_TRUST_REQUIREMENT
        witness = use["candidate_execution_witness"]
        witness["candidate_mechanism_symbol_id"] = executable["symbol_id"]
        mechanism_invocation = bundle["receipt"][
            "actual_candidate_mechanism_invocations"
        ][0]
        mechanism_invocation.update(
            {
                "mechanism_id": evidence["mechanism_id"],
                "symbol_id": executable["symbol_id"],
                "result_type": "NoneType",
                "callable_identity": copy.deepcopy(
                    mechanism_link["callable_identity"]
                ),
                "relation_review_digest": review_digest,
                "structural_result_observed": True,
            }
        )
        for node in bundle["receipt"]["pathway_use_graph"]["nodes"]:
            if node.get("candidate_id") == candidate_id:
                node["invalid_relabel_conflict_ids"] = ["CMP-05"]
                node["invalid_relabel_blocked_claims"] = [
                    "diagnostic_as_behavior",
                    "native packet admission",
                ]
                node["invalid_relabel_relation_review"] = copy.deepcopy(review)
                node[
                    "invalid_relabel_relation_review_trust_requirement"
                ] = self.checker.INVALID_RELABEL_CANDIDATE_REVIEW_TRUST_REQUIREMENT
                node["blocked_claims"] = copy.deepcopy(use["blocked_claims"])
        for edge in bundle["receipt"]["pathway_use_graph"]["edges"]:
            if edge.get("candidate_id") == candidate_id:
                edge["invalid_relabel_conflict_ids"] = ["CMP-05"]
                edge["invalid_relabel_blocked_claims"] = [
                    "diagnostic_as_behavior",
                    "native packet admission",
                ]
                edge["invalid_relabel_relation_review"] = copy.deepcopy(review)
                edge[
                    "invalid_relabel_relation_review_trust_requirement"
                ] = self.checker.INVALID_RELABEL_CANDIDATE_REVIEW_TRUST_REQUIREMENT
                edge["blocked_claims"] = copy.deepcopy(use["blocked_claims"])
        self._reseal(bundle)
        return review_digest

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

    def test_all_i116_envelopes_match_independent_canonical_derivation(self) -> None:
        i116 = EVIDENCE_DIR / "i116"
        fixture_names = (
            "01-simple-native-pathway",
            "02-producer-mediated-cmp20",
            "03-explicit-adapter-cmp26",
            "04-diagnostic-only-cmp04",
            "05-ambiguous-crossing-not-selected",
            "08-unregistered-candidate",
            "09-dynamic-a-b-choice",
            "10-multi-edge-use-graph",
            "low-context-replay",
        )
        for fixture_name in fixture_names:
            with self.subTest(fixture_name=fixture_name):
                bundle = self.checker.load_bundle(
                    ROOT,
                    lock_path=i116 / f"{fixture_name}.lock.json",
                    receipt_path=i116 / f"{fixture_name}.receipt.json",
                )
                result = self._validate(
                    ROOT,
                    bundle,
                    copy.deepcopy(self.policy),
                    active_rule_ids={"BCF-015"},
                    trusted_execution_transcript_digest=bundle["receipt"].get(
                        "execution_transcript_digest"
                    ),
                )

                self.assertEqual("passed", result["status"])
                self.assertEqual([], result["issues"])

    def test_every_claim_envelope_field_is_canonical_bcf015(self) -> None:
        envelope_locations = (
            ("lock", "pre_execution_claim_envelope"),
            ("receipt", "claim_envelope"),
        )
        for artifact_name, envelope_name in envelope_locations:
            honest_envelope = self.bundle[artifact_name][envelope_name]
            for field, honest_value in honest_envelope.items():
                if field == "required_qualifiers":
                    continue
                with self.subTest(
                    artifact_name=artifact_name,
                    envelope_field=field,
                ):
                    mutated = copy.deepcopy(self.bundle)
                    if isinstance(honest_value, bool):
                        forged_value: Any = not honest_value
                    elif isinstance(honest_value, str):
                        forged_value = "forged_claim_status"
                    elif isinstance(honest_value, list):
                        forged_value = [*honest_value, {"forged": True}]
                    else:
                        self.fail(f"unsupported envelope field type for {field}")
                    mutated[artifact_name][envelope_name][field] = forged_value
                    self._reseal(mutated)

                    result = self._validate(
                        ROOT,
                        mutated,
                        copy.deepcopy(self.policy),
                        active_rule_ids={"BCF-015"},
                    )

                    self.assertEqual("failed_closed", result["status"])
                    self.assertEqual(
                        {"BCF-015"},
                        {item["rule_id"] for item in result["issues"]},
                    )

            qualifiers = honest_envelope["required_qualifiers"]
            for qualifier_name, honest_value in qualifiers.items():
                with self.subTest(
                    artifact_name=artifact_name,
                    qualifier_name=qualifier_name,
                ):
                    mutated = copy.deepcopy(self.bundle)
                    mutated[artifact_name][envelope_name]["required_qualifiers"][
                        qualifier_name
                    ] = [*honest_value, {"forged": True}]
                    self._reseal(mutated)

                    result = self._validate(
                        ROOT,
                        mutated,
                        copy.deepcopy(self.policy),
                        active_rule_ids={"BCF-015"},
                    )

                    self.assertEqual("failed_closed", result["status"])
                    self.assertEqual(
                        {"BCF-015"},
                        {item["rule_id"] for item in result["issues"]},
                    )

    def test_audit_diagnostic_status_and_flag_widening_fails_bcf015(self) -> None:
        i116 = EVIDENCE_DIR / "i116"
        mutated = self.checker.load_bundle(
            ROOT,
            lock_path=i116 / "04-diagnostic-only-cmp04.lock.json",
            receipt_path=i116 / "04-diagnostic-only-cmp04.receipt.json",
        )
        for envelope in (
            mutated["lock"]["pre_execution_claim_envelope"],
            mutated["receipt"]["claim_envelope"],
        ):
            envelope["overall_claim_status"] = "admitted_bounded"
            envelope["contains_diagnostic_only_relation"] = False
        self._reseal(mutated)

        result = self._validate(
            ROOT,
            mutated,
            copy.deepcopy(self.policy),
            active_rule_ids={"BCF-015"},
        )

        self.assertEqual("failed_closed", result["status"])
        self.assertEqual({"BCF-015"}, {item["rule_id"] for item in result["issues"]})

    def test_envelope_projection_and_replay_block_forgery_fails_bcf015(self) -> None:
        i116 = EVIDENCE_DIR / "i116"
        mutation_cases = (
            (
                "02-producer-mediated-cmp20",
                lambda bundle: (
                    bundle["lock"].__setitem__("explicit_producers", []),
                    bundle["receipt"].__setitem__("producer_cuts_used", []),
                ),
            ),
            (
                "03-explicit-adapter-cmp26",
                lambda bundle: (
                    bundle["lock"].__setitem__("explicit_adapters", []),
                    bundle["receipt"].__setitem__("adapters_used", []),
                ),
            ),
            (
                "09-dynamic-a-b-choice",
                lambda bundle: (
                    bundle["lock"]["pre_execution_claim_envelope"].__setitem__(
                        "blocked_claims", []
                    ),
                    bundle["receipt"]["claim_envelope"].__setitem__(
                        "blocked_claims", []
                    ),
                    bundle["lock"].__setitem__("blocked_claims", []),
                    bundle["receipt"].__setitem__("blocked_claims", []),
                ),
            ),
        )
        for fixture_name, mutate in mutation_cases:
            with self.subTest(fixture_name=fixture_name):
                mutated = self.checker.load_bundle(
                    ROOT,
                    lock_path=i116 / f"{fixture_name}.lock.json",
                    receipt_path=i116 / f"{fixture_name}.receipt.json",
                )
                mutate(mutated)
                self._reseal(mutated)

                result = self._validate(
                    ROOT,
                    mutated,
                    copy.deepcopy(self.policy),
                    active_rule_ids={"BCF-015"},
                    trusted_execution_transcript_digest=mutated["receipt"].get(
                        "execution_transcript_digest"
                    ),
                )

                self.assertEqual("failed_closed", result["status"])
                self.assertEqual(
                    {"BCF-015"},
                    {item["rule_id"] for item in result["issues"]},
                )

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
        trusted_transcript_digest = receipt["execution_transcript_digest"]
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
            trusted_execution_transcript_digest=trusted_transcript_digest,
        )

        self.assertEqual("failed_closed", result["status"])
        self.assertEqual({"BCF-019"}, {item["rule_id"] for item in result["issues"]})

    def test_non_adapter_object_flow_forgery_fails_bcf019(self) -> None:
        mutated = self.checker.load_bundle(
            ROOT,
            lock_path=EVIDENCE_DIR / "i116/02-producer-mediated-cmp20.lock.json",
            receipt_path=(
                EVIDENCE_DIR / "i116/02-producer-mediated-cmp20.receipt.json"
            ),
        )
        trusted_transcript_digest = mutated["receipt"][
            "execution_transcript_digest"
        ]
        witness = mutated["receipt"]["composition_crossing_witnesses"][0]
        witness["dataflow_witness"]["runtime_object_id"] = "runtime-object:999"
        mutated["receipt"]["receipt_digest"] = self.checker.digest_without(
            mutated["receipt"],
            "receipt_digest",
        )

        result = self._validate(
            ROOT,
            mutated,
            copy.deepcopy(self.policy),
            active_rule_ids={"BCF-019"},
            trusted_execution_transcript_digest=trusted_transcript_digest,
        )

        self.assertEqual("failed_closed", result["status"])
        self.assertEqual({"BCF-019"}, {item["rule_id"] for item in result["issues"]})

    def test_registered_edge_requires_external_transcript_trust_bcf019(self) -> None:
        bundle = self.checker.load_bundle(
            ROOT,
            lock_path=EVIDENCE_DIR / "i116/02-producer-mediated-cmp20.lock.json",
            receipt_path=(
                EVIDENCE_DIR / "i116/02-producer-mediated-cmp20.receipt.json"
            ),
        )
        trusted_transcript_digest = bundle["receipt"][
            "execution_transcript_digest"
        ]

        trusted_result = self._validate(
            ROOT,
            copy.deepcopy(bundle),
            copy.deepcopy(self.policy),
            trusted_execution_transcript_digest=trusted_transcript_digest,
        )
        untrusted_result = self._validate(
            ROOT,
            copy.deepcopy(bundle),
            copy.deepcopy(self.policy),
            active_rule_ids={"BCF-019"},
        )

        self.assertEqual("passed", trusted_result["status"])
        self.assertEqual("failed_closed", untrusted_result["status"])
        self.assertEqual(
            {"BCF-019"},
            {item["rule_id"] for item in untrusted_result["issues"]},
        )

    def test_round3_coherent_cmp20_rewrite_cannot_reuse_trusted_digest(self) -> None:
        mutated = self.checker.load_bundle(
            ROOT,
            lock_path=EVIDENCE_DIR / "i116/02-producer-mediated-cmp20.lock.json",
            receipt_path=(
                EVIDENCE_DIR / "i116/02-producer-mediated-cmp20.receipt.json"
            ),
        )
        receipt = mutated["receipt"]
        witness = receipt["composition_crossing_witnesses"][0][
            "dataflow_witness"
        ]
        source_invocation = receipt["actual_stage_symbol_invocations"][
            witness["source_invocation_index"]
        ]
        target_invocation = receipt["actual_stage_symbol_invocations"][
            witness["target_invocation_index"]
        ]
        source_descriptor = source_invocation["runtime_object_flow"][
            witness["source_port"]
        ]
        target_flow = target_invocation["runtime_object_flow"]
        target_port = witness["target_port"]

        for artifact_name, binding_field in (
            ("lock", "declared_pathway_bindings"),
            ("receipt", "actual_bound_pathways_used"),
        ):
            for binding in mutated[artifact_name][binding_field]:
                for link in binding["expected_concrete_symbols"]:
                    if link["symbol_id"] == target_invocation["symbol_id"]:
                        link["runtime_instance_binding"] = {
                            "kind": "direct_bound_instance",
                            "instance_id": "session-instance:1",
                        }

        target_flow[target_port] = {
            "object_id": "runtime-object:999",
            "type": source_descriptor["type"],
        }
        self._reseal(mutated)
        trusted_distinct_transcript = receipt["execution_transcript_digest"]

        for artifact_name, binding_field in (
            ("lock", "declared_pathway_bindings"),
            ("receipt", "actual_bound_pathways_used"),
        ):
            for binding in mutated[artifact_name][binding_field]:
                for link in binding["expected_concrete_symbols"]:
                    if link["symbol_id"] == target_invocation["symbol_id"]:
                        link["runtime_instance_binding"] = {
                            "kind": "direct_bound_instance",
                            "instance_id": "session-instance:0",
                        }
        target_flow[target_port] = copy.deepcopy(source_descriptor)
        self._reseal(mutated)

        result = self._validate(
            ROOT,
            mutated,
            copy.deepcopy(self.policy),
            active_rule_ids={"BCF-019"},
            trusted_execution_transcript_digest=trusted_distinct_transcript,
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

    def test_candidate_without_executable_invocation_fails_bcf004(self) -> None:
        mutated = self.checker.load_bundle(
            ROOT,
            lock_path=EVIDENCE_DIR / "i116/08-unregistered-candidate.lock.json",
            receipt_path=(EVIDENCE_DIR / "i116/08-unregistered-candidate.receipt.json"),
        )
        mutated["receipt"]["actual_candidate_mechanism_invocations"] = []
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

    def test_candidate_executable_identity_forgery_fails_bcf004(self) -> None:
        mutated = self.checker.load_bundle(
            ROOT,
            lock_path=EVIDENCE_DIR / "i116/08-unregistered-candidate.lock.json",
            receipt_path=(EVIDENCE_DIR / "i116/08-unregistered-candidate.receipt.json"),
        )
        invocation = mutated["receipt"]["actual_candidate_mechanism_invocations"][0]
        invocation["symbol_id"] = "candidate-mechanism:forged"
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
                "diagnostic reconstruction governs ordinary runtime packet behavior"
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

    def test_round3_synonym_noop_fails_with_trusted_review_and_transcript(
        self,
    ) -> None:
        mutated = self.checker.load_bundle(
            ROOT,
            lock_path=EVIDENCE_DIR / "i116/08-unregistered-candidate.lock.json",
            receipt_path=(EVIDENCE_DIR / "i116/08-unregistered-candidate.receipt.json"),
        )
        review_digest = self._install_round3_cmp05_noop_claim(mutated)

        result = self._validate(
            ROOT,
            mutated,
            copy.deepcopy(self.policy),
            active_rule_ids={"BCF-011"},
            trusted_execution_transcript_digest=mutated["receipt"][
                "execution_transcript_digest"
            ],
            trusted_candidate_review_digests=(review_digest,),
        )

        self.assertEqual("failed_closed", result["status"])
        self.assertEqual({"BCF-011"}, {item["rule_id"] for item in result["issues"]})
        self.assertTrue(
            any(
                "distinct current mechanism" in item["message"]
                for item in result["issues"]
            )
        )

    def test_self_issued_invalid_pair_review_is_not_a_trust_root(self) -> None:
        mutated = self.checker.load_bundle(
            ROOT,
            lock_path=EVIDENCE_DIR / "i116/08-unregistered-candidate.lock.json",
            receipt_path=(EVIDENCE_DIR / "i116/08-unregistered-candidate.receipt.json"),
        )
        self._install_round3_cmp05_noop_claim(mutated)

        result = self._validate(
            ROOT,
            mutated,
            copy.deepcopy(self.policy),
            active_rule_ids={"BCF-011"},
            trusted_execution_transcript_digest=mutated["receipt"][
                "execution_transcript_digest"
            ],
        )

        self.assertEqual("failed_closed", result["status"])
        self.assertTrue(
            any(
                "not independently trusted" in item["message"]
                for item in result["issues"]
            )
        )

    def test_candidate_graph_cannot_omit_invalid_row_fields_bcf011(self) -> None:
        mutated = self.checker.load_bundle(
            ROOT,
            lock_path=EVIDENCE_DIR / "i116/08-unregistered-candidate.lock.json",
            receipt_path=(EVIDENCE_DIR / "i116/08-unregistered-candidate.receipt.json"),
        )
        edge = next(
            item
            for item in mutated["receipt"]["pathway_use_graph"]["edges"]
            if item["edge_kind"] == "experimental_unregistered_candidate"
        )
        edge.pop("invalid_relabel_conflict_ids")
        edge.pop("invalid_relabel_blocked_claims")
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
