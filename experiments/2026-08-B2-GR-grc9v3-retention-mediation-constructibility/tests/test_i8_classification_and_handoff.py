from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from b2_artifact_io import (  # noqa: E402
    assert_envelope_digest,
    read_json,
    receipt_digest,
    sha256_file,
)
from build_i8_classification_and_handoff import (  # noqa: E402
    CONFIG_PATH,
    LIFECYCLE_PATHS,
    OUTPUT_PATH,
    RECEIPT_PATH,
    REPORT_PATH,
    build_payload,
)


def test_i8_consumes_the_accepted_empty_i4_set() -> None:
    payload, _ = build_payload()
    assert payload["source_i4_candidate_set_status"] == (
        "accepted_empty_no_runtime_reached_candidate"
    )
    assert payload["causal_role_classification"]["maximum_new_GRR_rung"] == "none"
    assert payload["causal_role_classification"]["row_local_max_GRR"] == []
    assert payload["causal_role_classification"]["global_max_GRR"] == "none_new_in_B2"
    assert payload["causal_role_classification"]["branch_relation"] == (
        "not_testable_no_runtime_reached_I4_candidate"
    )
    assert payload["B2_closeout_ceiling"] == "B2-C6-ready"
    assert payload["B2_closeout_rung_assigned"] is False


def test_i5_i7_are_accounting_records_not_scientific_gates() -> None:
    payload, records = build_payload()
    assert [row["execution_status"] for row in payload["downstream_gate_lifecycle"]] == [
        "not_applicable_empty_I4_candidate_set",
        "not_applicable_no_GRR3_lineage",
        "not_applicable_no_GRR4_lineage",
    ]
    for record in records:
        assert_envelope_digest(record)
        row = record["payload"]
        assert row["status"] == "not_applicable"
        assert row["eligible_candidate_count"] == 0
        assert row["scientific_gate_executed"] is False
        assert row["positive_evidence_generated"] is False
        assert row["failure_status"] is False


def test_search_coverage_is_complete_and_typed() -> None:
    payload, _ = build_payload()
    coverage = payload["search_coverage"]
    assert coverage["allocated_attempt_count"] == 9648
    assert coverage["attempted_count"] == 9648
    assert coverage["resolved_attempt_count"] == 9648
    assert coverage["resolved_candidate_count"] == 0
    assert coverage["unresolved_candidate_count"] == 0
    assert coverage["numerical_failure_count"] == 0
    assert coverage["bounded_negative_count"] == 27
    assert coverage["formation_entirely_authored_or_unidentifiable_count"] == 1706
    assert coverage["outside_envelope_count"] == 7915
    assert sum(
        coverage["preparation_families_eligible_and_searched"].values()
    ) == 9648
    assert coverage["branches_eligible_and_attempted"] == 48
    assert coverage["branches_with_nontrivial_resolved_clean_primary_lane_attempt"] == 26
    assert coverage["branches_inaccessible_under_frozen_preparation_family"] == 22
    assert coverage["inaccessible_branch_is_negative_constructibility_evidence"] is False


def test_closeout_selects_no_extension_or_impossibility_claim() -> None:
    payload, _ = build_payload()
    decision = payload["closeout_decision"]
    boundary = payload["claim_boundary"]
    assert decision["primary_route"] == "unchanged_GRC9V3_search_remains_open"
    assert decision["extension_route"] == "no_extension_route_selected"
    assert decision["extension_selected"] is False
    assert decision["global_impossibility_established"] is False
    assert decision["localized_missing_causal_role_established"] is False
    assert boundary["extension_necessity"] is False
    assert boundary["global_impossibility"] is False
    assert payload["protected_src_spec_test_tree_unchanged"] is True


def test_generated_i8_artifacts_are_self_consistent_when_present() -> None:
    if not OUTPUT_PATH.exists():
        return
    artifact = read_json(OUTPUT_PATH)
    receipt = read_json(RECEIPT_PATH)
    assert_envelope_digest(artifact)
    assert receipt["receipt_payload_sha256"] == receipt_digest(receipt)
    assert receipt["output_payload_sha256"] == artifact["payload_sha256"]
    expected_paths = {OUTPUT_PATH, REPORT_PATH, *LIFECYCLE_PATHS.values()}
    expected = {
        str(path.resolve().relative_to(ROOT.parents[1].resolve())).replace("\\", "/")
        for path in expected_paths
    }
    assert set(receipt["output_artifact_digests"]) == expected
    for relative, digest in receipt["output_artifact_digests"].items():
        path = ROOT.parents[1] / relative
        assert sha256_file(path) == digest


def test_closeout_contract_is_json_and_uses_no_absolute_paths() -> None:
    contract = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    assert contract["schema_version"] == "b2_i8_closeout_contract_v1"
    assert contract["closeout_decision"]["extension_selected"] is False
