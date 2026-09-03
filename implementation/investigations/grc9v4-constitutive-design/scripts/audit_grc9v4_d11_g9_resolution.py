#!/usr/bin/env python3
"""Audit accepted-bounded D11-G9 and the paper-first propagation boundary."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
INVESTIGATION = ROOT / "implementation/investigations/grc9v4-constitutive-design"
DECISIONS = INVESTIGATION / "decisions"
SIDE_TOOL_ROOT = INVESTIGATION / "tools/exploratory-side-tool"
TOOL_ROOT = SIDE_TOOL_ROOT / "tool"

RESOLUTION = DECISIONS / "D11G9CanonicalExpansionPortAllocationResolution.json"
RESOLUTION_MD = DECISIONS / "D11G9CanonicalExpansionPortAllocationResolution.md"
SUPPLEMENT = DECISIONS / "D11G9AxisPreservingExpansionProvenanceSupplement.json"
PREREGISTRATION = DECISIONS / "D11G9CanonicalExpansionPortAllocationClosure.json"
D10_CLAIMS = DECISIONS / "D10NormativeClaimTopology.json"
D10_2 = DECISIONS / "D10_2FullSubstrateProvenanceAndPromotionAudit.json"
D11_C_SUPPLEMENT = DECISIONS / "D11CCandidateBaselineTransportProvenanceSupplement.json"
WITNESS = INVESTIGATION / "scripts/witness_d11_g9_canonical_expansion.py"
CHECKLIST = INVESTIGATION / "GRC9V4ConstitutiveDesignChecklist.md"
LEDGER = INVESTIGATION / "GRC9V4ConstitutiveDesignDecisionLedger.md"
PLAN = INVESTIGATION / "GRC9V4ConstitutiveDesignPlan.md"
README = INVESTIGATION / "README.md"
PAPER = INVESTIGATION / "drafts/2026-09-GRC-V4.md"
SPEC = ROOT / "specs/grc-9-v4-spec.md"
LEGACY_PAPER = ROOT / "papers/2026-04-GRC-9.md"
LEGACY_SPEC = ROOT / "specs/grc-9-v3-spec.md"

EXPECTED_RESOLUTION_DIGEST = (
    "a0813ceead2c992ec197790abd8a0ceea167ae2d952f853cf48f1db4d8001615"
)
EXPECTED_RESOLUTION_SHA = (
    "2b894abe80fed23455b7c37edc889aad48a27a1f8ae02d8c61752416a3eefc52"
)
EXPECTED_SUPPLEMENT_DIGEST = (
    "f39d82405a2a92b198289d71554ed907e18ac9183da4dfa07fc4f4944418ca4a"
)
EXPECTED_SUPPLEMENT_SHA = (
    "3a7f7c7bb11c291b7e5f082002a374dc95bfaab4917944f526da0ec58f15748f"
)
EXPECTED_WITNESS_SHA = (
    "cf53cf31af8d0e71c92100d4a6751c9c0db8fa8e60cdfe11ce76e23a8f05e4a5"
)
EXPECTED_PREREGISTRATION_DIGEST = (
    "856e3db9ffa6a09080f7af0b9753be222ab986599855168a4fe9d218490c1635"
)
EXPECTED_D11_C_DIGEST = (
    "82e8008e8edade39db7b5327a31a807031b712dcc86b3fe3e8c0977bda51e797"
)
EXPECTED_PAPER_SHA = "e009c5651842dea6636057a9639a79e42eb5c03b20c4812fb9ee5173705258e5"
EXPECTED_SPEC_SHA = "cd5661c31473b2d8dc42f0fe1e241aea4cbb76f07ea8db2e500244d70b196342"
EXPECTED_LEGACY_PAPER_SHA = (
    "cefc33e91e496c236660dad5c1e009a720ca908488db460d47322118dd7c3e08"
)
EXPECTED_LEGACY_SPEC_SHA = (
    "7b1f0c03988be7dbe3feb8ba926d43d891d70daa0dbbae9804fc70f2a4950f2f"
)

sys.path.insert(0, str(INVESTIGATION / "scripts"))
sys.path.insert(0, str(TOOL_ROOT / "src"))

import audit_grc9v4_d11_c_resolution as d11_c_audit  # noqa: E402
from grcv4_explorer.discovery import discover_sources  # noqa: E402
from grcv4_explorer.source_contract import (  # noqa: E402
    admitted_rows,
    load_et_c0_contract,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"{path}: expected JSON object")
    return value


def canonical_digest(record: dict[str, Any], digest_key: str) -> str:
    payload = {key: value for key, value in record.items() if key != digest_key}
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validate_resolution() -> dict[str, Any]:
    require(
        sha256_file(RESOLUTION) == EXPECTED_RESOLUTION_SHA,
        "D11-G9 resolution file identity drift",
    )
    resolution = load_object(RESOLUTION)
    require(
        resolution.get("decision_record_digest") == EXPECTED_RESOLUTION_DIGEST,
        "D11-G9 recorded digest drift",
    )
    require(
        canonical_digest(resolution, "decision_record_digest")
        == EXPECTED_RESOLUTION_DIGEST,
        "D11-G9 canonical digest mismatch",
    )
    require(
        resolution.get("status") == "accepted_bounded", "D11-G9 is not accepted bounded"
    )
    require(
        resolution.get("predecessor_decision_digest")
        == EXPECTED_PREREGISTRATION_DIGEST,
        "D11-G9 predecessor drift",
    )

    activation = resolution.get("scientific_activation", {})
    require(
        activation.get("required_decision_digest") == EXPECTED_D11_C_DIGEST,
        "D11-G9 activation lost D11-C identity",
    )
    require(activation.get("satisfied") is True, "D11-G9 activation is not satisfied")

    decision = resolution.get("decision", {})
    require(
        decision.get("selected_candidate_id") == "D11-G9-P4a",
        "selected candidate drift",
    )
    require(
        decision.get("selected_profile_id")
        == "grc9v4_axis_preserving_chiral_same_port_expansion_v1",
        "selected expansion profile drift",
    )
    require(
        decision.get("graph_generic_GRCV4_changed") is False, "GRCV4 changed at D11-G9"
    )
    require(
        decision.get("GRC9_or_GRC9V3_source_changed") is False, "legacy source changed"
    )

    chart = resolution.get("port_chart_contract", {})
    require(chart.get("port_set") == list(range(1, 10)), "port roster drift")
    require(
        chart.get("row_families") == {"1": [1, 2, 3], "2": [4, 5, 6], "3": [7, 8, 9]},
        "row chart drift",
    )
    require(
        chart.get("column_families")
        == {"1": [1, 4, 7], "2": [2, 5, 8], "3": [3, 6, 9]},
        "column chart drift",
    )
    require(
        "preserved" in chart.get("old_boundary_redirect_rule", ""),
        "old boundary identity drift",
    )
    require(
        "at_most_one" in chart.get("local_endpoint_capacity", ""),
        "endpoint capacity drift",
    )

    spine = resolution.get("primary_spine_contract", {})
    require(spine.get("chirality_domain") == [-1, 1], "chirality domain drift")
    require(spine.get("positive_spine_ports") == [2, 6, 7], "positive spine drift")
    require(spine.get("negative_spine_ports") == [3, 4, 8], "negative spine drift")
    require(spine.get("same_port_typing") is True, "same-port typing lost")
    require(spine.get("primary_row_counts") == [1, 1, 1], "primary row balance drift")
    require(
        spine.get("primary_column_counts") == [1, 1, 1], "primary column balance drift"
    )

    growth = resolution.get("capacity_and_growth_contract", {})
    require(
        growth.get("canonical_module_size") == "n_canonical=max(4,n_cap)",
        "module size drift",
    )
    require(
        growth.get("tree_external_capacity") == "D_ext_max(n)=9*n-2*(n-1)=7*n+2",
        "capacity identity drift",
    )
    require(
        "none_iff_rho_equals_zero" in growth.get("growth_phase_rule", ""),
        "growth phase is not canonical",
    )

    recursive = resolution.get("recursive_tree_contract", {})
    require(
        recursive.get("branch_row") == "every_internal_edge_in_branch_b_uses_row_b",
        "branch row drift",
    )
    require(
        "breadth_first" in recursive.get("parent_rule", ""), "BFS parent rule drift"
    )
    require(
        "identical" in recursive.get("edge_port_rule", ""),
        "recursive same-port rule drift",
    )
    require(
        recursive.get("row_balance").endswith("at_most_one"), "row balance bound drift"
    )
    require(
        recursive.get("column_balance").endswith("at_most_one"),
        "column balance bound drift",
    )

    phases = resolution.get("phase_and_covariance_contract", {})
    require(
        phases.get("chirality_is_explicit_event_identity") is True,
        "chirality is hidden",
    )
    require(
        phases.get("missing_chirality_disposition") == "module_chirality_required",
        "chirality fail-closed drift",
    )
    require(
        phases.get("missing_active_growth_phase_disposition")
        == "module_growth_phase_required",
        "phase fail-closed drift",
    )
    require(
        phases.get("inactive_growth_phase_disposition")
        == "reject_noncanonical_inactive_growth_phase",
        "inactive phase is admitted",
    )

    identity = resolution.get("stable_identity_contract", {})
    require(
        identity.get("event_id_grammar")
        == "grc-event-sha256_followed_by_colon_and_exactly_64_lowercase_hex_digits",
        "event ID grammar drift",
    )
    require(
        identity.get("extra_ordinal_width") == "w=max(1,len(decimal(m)))",
        "ID padding drift",
    )
    require(
        "local_ordinal_zero_padded_to_w" in identity.get("extra_node_id", ""),
        "extra node ID drift",
    )
    require(
        "canonical_growth_phase" in identity.get("event_digest_payload", []),
        "phase absent from event identity",
    )

    bond = resolution.get("bond_and_resource_contract", {})
    require(
        bond.get("bond_seed_policy_id") == "fixed_positive_chart_neutral_v1",
        "bond policy drift",
    )
    require(
        "strictly_greater_than_zero" in bond.get("bond_seed", ""),
        "bond positivity drift",
    )
    require(
        bond.get("new_edge_incoming_reference_current") == 0,
        "new-edge current seed drift",
    )
    require(
        "same_typed_resource_map" in bond.get("reset_rule", ""),
        "reset resource map drift",
    )

    lifecycle = resolution.get("lifecycle_contract", {})
    require(
        "entire_exact_W_C_tr" in lifecycle.get("Candidate_C", ""),
        "D11-C target authority lost",
    )
    require(
        lifecycle.get("Candidate_C_forbidden_relabel")
        == "W_C_tr_is_not_mobility_state_and_is_not_rebuilt_from_C_plus",
        "Candidate C mobility relabel returned",
    )
    require(
        "whole_target_carrier" in lifecycle.get("persistent_K4", ""),
        "K4 history is not whole-carrier",
    )
    require(
        "zero_filling_new_components"
        in lifecycle.get("persistent_K4_forbidden_hybrid", ""),
        "partial K4 embedding is not forbidden",
    )
    require(
        "complete_source_state_is_preserved" in lifecycle.get("atomicity", ""),
        "failure atomicity drift",
    )

    legacy = resolution.get("legacy_compatibility_contract", {})
    require(legacy.get("GRC9_or_GRC9V3_modified") is False, "legacy authority changed")
    require(
        "port_five" in legacy.get("saturated_conflicting_event", ""),
        "legacy conflict boundary missing",
    )
    require(
        "commit_no_graph_resource_state_history_reset_or_receipt_mutation"
        in legacy.get("disabled_disposition", ""),
        "legacy undefined event is not atomic",
    )
    require(
        legacy.get("enabled_V4_not_exact_V3") is True,
        "enabled V4 may be mislabeled exact V3",
    )

    dispositions = {
        row.get("candidate_id"): row
        for row in resolution.get("candidate_dispositions", [])
    }
    require(
        set(dispositions)
        == {
            "D11-G9-P0",
            "D11-G9-P1",
            "D11-G9-P1a",
            "D11-G9-P2",
            "D11-G9-P3",
            "D11-G9-P4",
            "D11-G9-P4a",
        },
        "candidate disposition roster drift",
    )
    require(
        dispositions["D11-G9-P4a"].get("disposition") == "selected_accepted_bounded",
        "P4a is not accepted",
    )
    require(
        dispositions["D11-G9-P1a"].get("disposition")
        == "superseded_preserved_for_comparison",
        "P1a comparison status drift",
    )

    topology = resolution.get("claim_topology_effect", {})
    require(topology.get("D10_current_claims_rewritten") == 0, "D10 claims rewritten")
    require(
        topology.get("D10_historical_claims_rewritten") == 0,
        "historical claims rewritten",
    )
    require(topology.get("D11_C_claims_rewritten") == 0, "D11-C claim rewritten")
    require(
        topology.get("successor_claim_ids_added") == ["D11-G9-CL-N-001"],
        "successor claim drift",
    )

    debt = resolution.get("debt_transformation", {})
    require(
        debt.get("predecessor_D10_debt_transformation_count") == 29,
        "inherited debt count drift",
    )
    require(
        debt.get("predecessor_D10_debt_dispositions_changed") == 0,
        "inherited debt rewritten",
    )
    require(
        debt.get("local_debt_successor_status") == "resolved_bounded_by_D11_G9_P4a",
        "D11-G9 debt not resolved",
    )

    population = resolution.get("successor_population_effect", {})
    require(
        population.get("combined_current_objects") == 80, "combined object count drift"
    )
    require(
        population.get("combined_current_equation_contracts") == 183,
        "combined contract count drift",
    )
    require(
        population.get("D11_G9_objects_added") == 10, "D11-G9 object increment drift"
    )
    require(
        population.get("D11_G9_equation_contracts_added") == 20,
        "D11-G9 contract increment drift",
    )

    obligations = resolution.get("verification_obligation_effect", {})
    require(
        obligations.get("D10_pending_forward_obligations_remaining") == 10,
        "D10 pending obligations drift",
    )
    require(
        obligations.get("D11_C_pending_forward_obligations_carried") == 3,
        "D11-C obligations lost",
    )
    require(
        len(obligations.get("new_forward_obligations", [])) == 4,
        "D11-G9 obligation roster drift",
    )
    require(
        obligations.get("total_pending_forward_obligations") == 17,
        "total pending obligation count drift",
    )

    acceptance = resolution.get("human_acceptance", {})
    require(acceptance.get("accepted") is True, "human acceptance missing")
    authorization = resolution.get("authorization_effect", {})
    require(
        authorization.get("D11_G9_closed_accepted_bounded") is True,
        "D11-G9 closeout missing",
    )
    require(
        authorization.get("paper_propagation_authorized_now") is True,
        "paper propagation not opened",
    )
    for key in (
        "specification_propagation_authorized_now",
        "implementation_plan_authorized",
        "implementation_authorized",
        "runtime_or_src_tests_change_authorized",
        "GRC9_or_GRC9V3_change_authorized",
    ):
        require(authorization.get(key) is False, f"D11-G9 over-authorizes {key}")

    propagation = resolution.get("propagation_state", {})
    require(
        propagation.get("paper_updated") is False,
        "paper propagated in the D11 record step",
    )
    require(
        propagation.get("specification_updated") is False,
        "spec propagated before paper",
    )
    require(propagation.get("next_gate") == "D11-paper-propagation", "next gate drift")

    d11_c_audit.opening_audit.validate_source_identity_rows(resolution)
    return resolution


def validate_supplement() -> dict[str, Any]:
    require(
        sha256_file(SUPPLEMENT) == EXPECTED_SUPPLEMENT_SHA,
        "D11-G9 supplement file identity drift",
    )
    supplement = load_object(SUPPLEMENT)
    require(
        supplement.get("artifact_digest") == EXPECTED_SUPPLEMENT_DIGEST,
        "supplement recorded digest drift",
    )
    require(
        canonical_digest(supplement, "artifact_digest") == EXPECTED_SUPPLEMENT_DIGEST,
        "supplement canonical digest mismatch",
    )
    require(
        supplement.get("status") == "accepted_bounded_companion_registry",
        "supplement status drift",
    )
    require(supplement.get("normative_object_count") == 10, "D11-G9 object count drift")
    require(
        len(supplement.get("normative_objects", [])) == 10,
        "D11-G9 object roster length drift",
    )
    require(
        supplement.get("equation_contract_count") == 20, "D11-G9 contract count drift"
    )
    require(
        len(supplement.get("equation_contracts", [])) == 20,
        "D11-G9 contract roster length drift",
    )

    object_ids = {row["object_id"] for row in supplement["normative_objects"]}
    require(len(object_ids) == 10, "duplicate D11-G9 object ID")
    contract_ids = {
        row["equation_contract_id"] for row in supplement["equation_contracts"]
    }
    require(len(contract_ids) == 20, "duplicate D11-G9 contract ID")
    require(
        all(
            set(row["parent_object_ids"]) <= object_ids
            for row in supplement["equation_contracts"]
        ),
        "D11-G9 contract references an unknown D11-G9 object",
    )

    claim = supplement.get("accepted_successor_claim", {})
    require(claim.get("claim_id") == "D11-G9-CL-N-001", "successor claim ID drift")
    require(
        claim.get("claim_class") == "GRC9V4_specialization_normative",
        "successor claim class drift",
    )
    edges = supplement.get("claim_edges", [])
    require(len(edges) == 9, "reciprocal claim-edge count drift")
    d10_claim_ids = {row["claim_id"] for row in load_object(D10_CLAIMS)["claims"]}
    require(
        all(row["predecessor_claim_id"] in d10_claim_ids for row in edges),
        "claim edge references unknown D10 claim",
    )
    require(
        all(row["successor_claim_id"] == "D11-G9-CL-N-001" for row in edges),
        "claim edge target drift",
    )
    require(
        all(row["predecessor_status_changed"] is False for row in edges),
        "claim edge mutates predecessor",
    )

    counts = supplement.get("successor_population_counts", {})
    require(
        counts.get("combined_current_objects") == 80, "supplement object total drift"
    )
    require(
        counts.get("combined_current_equation_contracts") == 183,
        "supplement contract total drift",
    )
    require(
        counts.get("D10_2_or_D11_C_claim_nodes_rewritten") == 0,
        "supplement rewrites predecessor claims",
    )
    preservation = supplement.get("predecessor_registry_preservation", {})
    require(
        preservation.get("D10_2_files_modified") is False, "supplement mutates D10.2"
    )
    require(
        preservation.get("D10_2_or_D11_C_counts_or_digests_rewritten") is False,
        "supplement rewrites predecessor registries",
    )

    d10_object_ids = {
        row["object_id"]
        for row in load_object(D10_2)["normatively_load_bearing_objects"]
    }
    d11_c_object_ids = {
        row["object_id"] for row in load_object(D11_C_SUPPLEMENT)["normative_objects"]
    }
    require(not object_ids & d10_object_ids, "D11-G9 duplicates a D10 object ID")
    require(not object_ids & d11_c_object_ids, "D11-G9 duplicates a D11-C object ID")
    d11_c_audit.opening_audit.validate_source_identity_rows(supplement)
    return supplement


def validate_witness(resolution: dict[str, Any]) -> None:
    require(
        sha256_file(WITNESS) == EXPECTED_WITNESS_SHA, "D11-G9 witness identity drift"
    )
    result = subprocess.run(
        [sys.executable, str(WITNESS)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    require(result.returncode == 0, f"D11-G9 witness failed: {result.stderr.strip()}")
    observed = json.loads(result.stdout)
    recorded = resolution.get("combinatorial_witness", {})
    for key in (
        "target_effective_degree_range",
        "target_effective_degree_case_count",
        "admitted_plan_case_count",
        "checked_chiralities",
        "checked_active_growth_phases",
        "input_order_shuffle_count",
        "covariance_case_count",
        "positive_primary_spine",
        "negative_primary_spine",
        "unique_local_endpoint_occupancy",
        "exact_old_boundary_ports",
        "same_port_internal_edges",
        "connected_acyclic_tree",
        "row_and_column_imbalance_at_most_one",
        "capacity_identity",
        "inactive_phase_rejected",
        "missing_active_phase_rejected",
        "large_plan_digest",
    ):
        require(observed.get(key) == recorded.get(key), f"witness result drift: {key}")


def validate_current_state() -> None:
    checklist = CHECKLIST.read_text(encoding="utf-8")
    for marker in (
        "### D11-G9 Accepted-Bounded Gate",
        "- [x] Record human acceptance of corrected D11-G9-P4a.",
        "D11-G9 = accepted_bounded_D11-G9-P4a",
        EXPECTED_RESOLUTION_DIGEST,
    ):
        require(marker in checklist, f"checklist D11-G9 marker missing: {marker}")
    for path, markers in (
        (
            LEDGER,
            (
                "### D11-G9 Accepted-Bounded Axis-Preserving Expansion",
                EXPECTED_RESOLUTION_DIGEST,
                "scientific_result_accepted = true",
            ),
        ),
        (PLAN, ("D11-G9 accepted", "propagation is next")),
        (
            README,
            ("accepted bounded as corrected candidate D11-G9-P4a", "paper is now the"),
        ),
    ):
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            require(
                marker in text, f"{path}: current D11-G9 state marker missing: {marker}"
            )

    require(
        sha256_file(PAPER) == EXPECTED_PAPER_SHA,
        "GRC-v4 paper changed before propagation gate",
    )
    require(
        sha256_file(SPEC) == EXPECTED_SPEC_SHA,
        "GRC9V4 spec changed before paper propagation",
    )
    require(
        sha256_file(LEGACY_PAPER) == EXPECTED_LEGACY_PAPER_SHA, "GRC9 source changed"
    )
    require(sha256_file(LEGACY_SPEC) == EXPECTED_LEGACY_SPEC_SHA, "GRC9V3 spec changed")


def validate_source_observation() -> tuple[str, int, str]:
    contract = load_et_c0_contract(
        SIDE_TOOL_ROOT / "records/ETC0SourceAndLayoutContract.json"
    )
    observation = discover_sources(ROOT, admitted_rows(contract))
    require(
        observation.get("state") == "new_unprocessed_source_available",
        "D11-G9 sources were silently admitted",
    )
    added = observation.get("added_unprocessed", [])
    added_paths = {row.get("path") for row in added}
    expected_paths = {
        "implementation/investigations/grc9v4-constitutive-design/decisions/D11SuccessorInvestigationOpening.json",
        "implementation/investigations/grc9v4-constitutive-design/decisions/D11ClaimDebtAndAuthorityRouting.json",
        "implementation/investigations/grc9v4-constitutive-design/decisions/D11CCandidateCBaselineTransportAndMobilityClosure.json",
        "implementation/investigations/grc9v4-constitutive-design/decisions/D11G9CanonicalExpansionPortAllocationClosure.json",
        "implementation/investigations/grc9v4-constitutive-design/decisions/D11CCandidateBaselineTransportAndMobilityResolution.json",
        "implementation/investigations/grc9v4-constitutive-design/decisions/D11CCandidateBaselineTransportProvenanceSupplement.json",
        "implementation/investigations/grc9v4-constitutive-design/decisions/D11G9CanonicalExpansionPortAllocationResolution.json",
        "implementation/investigations/grc9v4-constitutive-design/decisions/D11G9AxisPreservingExpansionProvenanceSupplement.json",
    }
    require(
        added_paths == expected_paths,
        f"D11-G9 source observation roster drift: {sorted(added_paths ^ expected_paths)}",
    )
    return observation["state"], len(added), observation["observation_digest"]


def main() -> int:
    require(
        Path(sys.prefix).resolve() == (ROOT / ".venv").resolve(),
        "run with repository .venv Python",
    )
    d11_c_audit.opening_audit.validate_opening()
    d11_c_audit.opening_audit.validate_specification_holds()
    d11_c = d11_c_audit.validate_resolution()
    d11_c_audit.validate_supplement()
    d11_c_audit.validate_witness(d11_c)
    resolution = validate_resolution()
    validate_supplement()
    validate_witness(resolution)
    validate_current_state()
    for path in (RESOLUTION_MD, CHECKLIST, LEDGER, PLAN, README):
        d11_c_audit.opening_audit.validate_render(path)
    require(
        not re.search(r"(?m)[ \t]+$", RESOLUTION_MD.read_text(encoding="utf-8")),
        "D11-G9 resolution Markdown has trailing whitespace",
    )
    source_state, added_count, observation_digest = validate_source_observation()
    print(
        "D11_G9_RESOLUTION_AUDIT_PASS "
        f"resolution_digest={EXPECTED_RESOLUTION_DIGEST} "
        "selected=D11-G9-P4a "
        "profile=grc9v4_axis_preserving_chiral_same_port_expansion_v1 "
        "endpoint_occupancy=true same_port=true capacity=true covariance=true "
        "claims=39+29+1+1 objects=67+3+10 contracts=152+11+20 "
        "pending_obligations=17 paper_propagation=authorized_not_applied "
        "specification=false implementation=false legacy_changes=false "
        f"source_observation_state={source_state} "
        f"unprocessed_source_count={added_count} "
        f"source_observation_digest={observation_digest}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
