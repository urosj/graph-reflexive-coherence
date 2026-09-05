#!/usr/bin/env python3
"""Audit the bounded D11 opening and preregistered successor state."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
INVESTIGATION = ROOT / "implementation/investigations/grc9v4-constitutive-design"
DECISIONS = INVESTIGATION / "decisions"
TOOL_ROOT = INVESTIGATION / "tools/exploratory-side-tool/tool"
SIDE_TOOL_ROOT = TOOL_ROOT.parent

OPENING = DECISIONS / "D11SuccessorInvestigationOpening.json"
ROUTING = DECISIONS / "D11ClaimDebtAndAuthorityRouting.json"
D11_C = DECISIONS / "D11CCandidateCBaselineTransportAndMobilityClosure.json"
D11_G9 = DECISIONS / "D11G9CanonicalExpansionPortAllocationClosure.json"
D10_CLAIMS = DECISIONS / "D10NormativeClaimTopology.json"
D10_DEBT = DECISIONS / "D10DebtClaimTransformationLedger.json"
D10_AUTHORIZATION = DECISIONS / "D10SpecificationAuthorizationProfile.json"
D10_2 = DECISIONS / "D10_2FullSubstrateProvenanceAndPromotionAudit.json"
D10_2_MD = DECISIONS / "D10_2FullSubstrateProvenanceAndPromotionAudit.md"
SOURCE_MANIFEST = ROOT / "specs/grc-v4-source-manifest.json"
FIXTURES = ROOT / "specs/grc-v4-conformance-fixtures.json"
GRCV4_SPEC = ROOT / "specs/grc-v4-spec.md"
GRC9V4_SPEC = ROOT / "specs/grc-9-v4-spec.md"
CHECKLIST = INVESTIGATION / "GRC9V4ConstitutiveDesignChecklist.md"

sys.path.insert(0, str(TOOL_ROOT / "src"))

from grcv4_explorer.discovery import discover_sources  # noqa: E402
from grcv4_explorer.source_contract import (  # noqa: E402
    admitted_rows,
    load_et_c0_contract,
)


EXPECTED_D10_2_SHA = (
    "59c2b956cec7d258b1db09d43d6df44deb8c0be0453a5d741f7e2733d6881a33"
)
EXPECTED_D10_2_MD_SHA = (
    "70fc8e1ce126e159b651e3ee71690b7238ae8c6f659913e7d2b4323bc1e30c8d"
)
EXPECTED_D10_2_DIGEST = (
    "28343064e85065b7f18227cf429e8cd8f33b414d7a19d5f3e9090a318adcb32c"
)
EXPECTED_D10_CLAIMS_SHA = (
    "f516fe696a55dd3f77f42b0d539e211689640f3ce8d3dd1134283cd47a06a94f"
)
EXPECTED_D10_CLAIMS_DIGEST = (
    "2bd78fc5d9a075d0958813dd199a8a57a8c23565e10b68fce89c967d4b3ee373"
)
EXPECTED_D10_DEBT_SHA = (
    "68190c133d8bda7067dfb4cb9b55980e578ce02051bc5d24066b0349f6f8a23a"
)
EXPECTED_D10_DEBT_DIGEST = (
    "da3cb887be1c256666e74c7bb01da5b038d06f88484b91b24ec25954f1ab3e82"
)
EXPECTED_D10_AUTHORIZATION_SHA = (
    "ab723c35aaaa971662d3f3c21742d8d99c943661cb8e93ef2e46a54ccce6cd0b"
)
EXPECTED_D10_AUTHORIZATION_DIGEST = (
    "3adafb4703b88ce7faf48b9c4e6b3bcb3c359224066df9d084c2a2f2b9bac159"
)
EXPECTED_OPENING_DIGEST = (
    "51ba66d5404dee29f7b2a7dcd9501b43711fce0d47d466118945b5a0f71ac23a"
)
EXPECTED_ROUTING_DIGEST = (
    "63cc407bffefef85602c28ead6c3da6b846778d3be9f78952db11cb10275c78d"
)
EXPECTED_ROUTING_SHA = (
    "f34bff656cc4e231bb8db81a9d69498c2b9a1e57accc4ecaec6642cd3e4422df"
)
EXPECTED_D11_C_DIGEST = (
    "c1c22c88fa676705370d01256a34801a364e310c93e4ef85cc5a3208e6e06a78"
)
EXPECTED_D11_G9_DIGEST = (
    "856e3db9ffa6a09080f7af0b9753be222ab986599855168a4fe9d218490c1635"
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


def canonical_record_digest(record: dict[str, Any]) -> str:
    payload = {key: value for key, value in record.items() if key != "decision_record_digest"}
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validate_record_digest(path: Path, expected: str) -> dict[str, Any]:
    record = load_object(path)
    require(
        record.get("decision_record_digest") == expected,
        f"{path}: recorded digest drift",
    )
    require(
        canonical_record_digest(record) == expected,
        f"{path}: canonical digest mismatch",
    )
    return record


def validate_render(path: Path) -> None:
    pandoc = shutil.which("pandoc")
    require(pandoc is not None, "pandoc is required for the D11 render audit")
    result = subprocess.run(
        [
            pandoc,
            "--from=gfm+tex_math_dollars",
            "--to=html5",
            "--mathjax",
            str(path),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    require(result.returncode == 0, f"pandoc failed for {path}: {result.stderr.strip()}")


def validate_source_identity_rows(record: dict[str, Any]) -> None:
    for row in record.get("source_identities", []):
        path_text = row.get("path")
        expected = row.get("file_sha256")
        if not path_text or not expected:
            continue
        path = ROOT / path_text
        require(path.is_file(), f"missing D11 source identity: {path_text}")
        require(
            sha256_file(path) == expected,
            f"D11 accepted source identity drift: {path_text}",
        )


def validate_routing() -> dict[str, Any]:
    require(sha256_file(D10_CLAIMS) == EXPECTED_D10_CLAIMS_SHA, "accepted D10 claim topology changed")
    require(sha256_file(D10_DEBT) == EXPECTED_D10_DEBT_SHA, "accepted D10 debt ledger changed")
    require(
        sha256_file(D10_AUTHORIZATION) == EXPECTED_D10_AUTHORIZATION_SHA,
        "accepted D10 authorization profile changed",
    )

    claims = load_object(D10_CLAIMS)
    debt = load_object(D10_DEBT)
    authorization = load_object(D10_AUTHORIZATION)
    d10_2 = load_object(D10_2)
    require(claims.get("artifact_digest") == EXPECTED_D10_CLAIMS_DIGEST, "D10 claim digest drift")
    require(debt.get("artifact_digest") == EXPECTED_D10_DEBT_DIGEST, "D10 debt digest drift")
    require(
        authorization.get("artifact_digest") == EXPECTED_D10_AUTHORIZATION_DIGEST,
        "D10 authorization digest drift",
    )

    routing = validate_record_digest(ROUTING, EXPECTED_ROUTING_DIGEST)
    require(sha256_file(ROUTING) == EXPECTED_ROUTING_SHA, "D11 routing file identity drift")
    require(
        routing.get("status") == "accepted_bounded_routing_contract",
        "D11 routing status drift",
    )
    require(
        routing.get("predecessor_decision_digest") == EXPECTED_OPENING_DIGEST,
        "D11 routing predecessor drift",
    )
    validate_source_identity_rows(routing)

    carried_claims = routing.get("carried_forward_claim_topology", {})
    require(claims.get("claim_count") == 39, "accepted D10 current-claim count drift")
    require(claims.get("historical_claim_count") == 29, "accepted D10 historical-claim count drift")
    require(claims.get("total_claim_node_count") == 68, "accepted D10 total-claim count drift")
    require(carried_claims.get("current_claim_count") == 39, "D11 current-claim count drift")
    require(carried_claims.get("historical_claim_count") == 29, "D11 historical-claim count drift")
    require(carried_claims.get("total_claim_node_count") == 68, "D11 total-claim count drift")
    require(
        carried_claims.get("class_counts") == claims.get("category_counts"),
        "D11 claim-class counts do not equal accepted D10",
    )

    accepted_by_class: dict[str, set[str]] = {}
    for row in claims.get("claims", []):
        accepted_by_class.setdefault(row["claim_class"], set()).add(row["claim_id"])
    carried_by_class = {
        claim_class: set(ids)
        for claim_class, ids in carried_claims.get("current_claim_ids_by_class", {}).items()
    }
    require(carried_by_class == accepted_by_class, "D11 current claim inventory is not exact")
    current_claim_ids = set().union(*accepted_by_class.values())
    historical_claim_ids = {row["claim_id"] for row in claims.get("historical_claim_nodes", [])}
    require(
        set(carried_claims.get("historical_claim_ids", [])) == historical_claim_ids,
        "D11 historical claim inventory is not exact",
    )
    require(
        carried_claims.get("opening_effect")
        == {
            "accepted_claims_added": 0,
            "accepted_claims_removed": 0,
            "accepted_claims_reclassified": 0,
            "historical_claims_rewritten": 0,
        },
        "D11 opening changes inherited claim topology",
    )

    carried_debt = routing.get("carried_forward_debt_transformation_topology", {})
    accepted_debt_ids = {row["debt_id"] for row in debt.get("debt_transformations", [])}
    require(debt.get("debt_count") == 29, "accepted D10 debt count drift")
    require(carried_debt.get("debt_count") == 29, "D11 debt count drift")
    require(set(carried_debt.get("debt_ids", [])) == accepted_debt_ids, "D11 debt inventory is not exact")
    require(
        carried_debt.get("transformation_counts") == debt.get("transformation_counts"),
        "D11 debt transformation counts drift",
    )

    carried_obligations = routing.get("carried_forward_verification_obligations", {})
    accepted_obligation_ids = {row["obligation_id"] for row in debt.get("verification_obligations", [])}
    pending_obligation_ids = set(carried_obligations.get("pending_after_D10_2_ids", []))
    preclose = carried_obligations.get("satisfied_for_current_population_only", {})
    require(debt.get("verification_obligation_count") == 11, "accepted D10 obligation count drift")
    require(carried_obligations.get("obligation_count") == 11, "D11 obligation count drift")
    require(len(pending_obligation_ids) == 10, "D11 must retain ten pending obligations")
    require(
        pending_obligation_ids | {preclose.get("obligation_id")} == accepted_obligation_ids,
        "D11 verification-obligation inventory is not exact",
    )
    require(
        preclose.get("obligation_id") == "D10-PRECLOSE-SUBSTRATE-PROVENANCE-AUDIT",
        "D10 preclose obligation disposition drift",
    )
    require(
        "current_D10_initial_specification_population_only" in preclose.get("disposition", ""),
        "D10.2 provenance closure lost its current-population bound",
    )

    population = routing.get("carried_forward_D10_2_population", {})
    equation_coverage = d10_2.get("equation_contract_coverage", {})
    require(len(d10_2.get("normatively_load_bearing_objects", [])) == 67, "D10.2 object count drift")
    require(len(d10_2.get("normative_equation_contract_registry", [])) == 152, "D10.2 contract count drift")
    require(population.get("normatively_load_bearing_object_count") == 67, "D11 object count drift")
    require(population.get("normative_equation_contract_count") == 152, "D11 contract count drift")
    require(population.get("parent_atomic_contract_count") == 67, "D11 parent-contract count drift")
    require(population.get("explicit_equation_contract_count") == 85, "D11 explicit-contract count drift")
    require(population.get("disabled_reduction_contract_count") == 40, "D11 disabled-row count drift")
    require(population.get("independent_GRC_derivation_count") == 12, "D11 derivation count drift")
    require(equation_coverage.get("parent_atomic_contract_count") == 67, "D10.2 parent count drift")
    require(equation_coverage.get("explicit_equation_contract_count") == 85, "D10.2 explicit count drift")
    require(equation_coverage.get("disabled_reduction_contract_count") == 40, "D10.2 disabled count drift")
    require(
        population.get("accepted_provenance_successor_reference", {}).get("reference_id")
        == "D10.2-CL-N-001",
        "D10.2 successor reference was dropped",
    )

    d11_debts = {row.get("debt_id"): row for row in routing.get("newly_exposed_D11_debts", [])}
    require(
        set(d11_debts)
        == {
            "D11-C-DEBT-BASELINE-TRANSPORT-AUTHORITY",
            "D11-G9-DEBT-CANONICAL-PORT-ALLOCATION",
        },
        "D11 additive debt roster drift",
    )
    require(d11_debts["D11-C-DEBT-BASELINE-TRANSPORT-AUTHORITY"].get("status") == "open_preregistered", "D11-C debt is not active")
    require(
        d11_debts["D11-G9-DEBT-CANONICAL-PORT-ALLOCATION"].get("status")
        == "queued_preregistered_requires_accepted_D11_C",
        "D11-G9 debt activated early",
    )
    for debt_row in d11_debts.values():
        require(
            set(debt_row.get("directly_bearing_claim_ids", [])) <= current_claim_ids,
            f"{debt_row.get('debt_id')}: unknown claim bearing",
        )
        require(
            "no_claim_is_reclassified" in debt_row.get("claim_bearing_semantics", ""),
            f"{debt_row.get('debt_id')}: claim-bearing boundary missing",
        )

    routing_auth = routing.get("authorization_effect", {})
    require(routing_auth.get("claim_transformation_authorized_without_accepted_successor") is False, "D11 routing authorizes claim transformation")
    require(routing_auth.get("prior_debt_disposition_change_authorized") is False, "D11 routing authorizes prior debt changes")
    require(routing_auth.get("verification_obligation_discharge_authorized") is False, "D11 routing discharges verification")
    require(routing_auth.get("implementation_authorized") is False, "D11 routing authorizes implementation")
    return routing


def validate_opening() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    require(sha256_file(D10_2) == EXPECTED_D10_2_SHA, "accepted D10.2 JSON changed")
    require(sha256_file(D10_2_MD) == EXPECTED_D10_2_MD_SHA, "accepted D10.2 Markdown changed")
    d10_2 = load_object(D10_2)
    require(d10_2.get("decision_record_digest") == EXPECTED_D10_2_DIGEST, "D10.2 digest drift")

    opening = validate_record_digest(OPENING, EXPECTED_OPENING_DIGEST)
    require(opening.get("status") == "accepted_bounded_successor_opening", "D11 opening status drift")
    require(opening.get("predecessor_decision_digest") == EXPECTED_D10_2_DIGEST, "D11 opening predecessor drift")
    require(opening.get("decision", {}).get("scientific_result_accepted") is False, "D11 opening claims a scientific result")
    opening_auth = opening.get("authorization_effect", {})
    require(opening_auth.get("D11_C_authorized") is True, "D11-C is not authorized")
    require(opening_auth.get("D11_G9_authorized_now") is False, "D11-G9 activated too early")
    require(opening_auth.get("D11_G9_authorized_after_D11_C_acceptance") is True, "D11-G9 sequence drift")
    require(opening_auth.get("implementation_authorized") is False, "D11 opening authorizes implementation")
    require(opening_auth.get("runtime_or_src_change_authorized") is False, "D11 opening authorizes src")
    require(opening_auth.get("tests_change_authorized") is False, "D11 opening authorizes tests")
    require(opening_auth.get("older_version_change_authorized") is False, "D11 opening authorizes legacy edits")

    routing = validate_routing()

    d11_c = validate_record_digest(D11_C, EXPECTED_D11_C_DIGEST)
    require(d11_c.get("status") == "open_preregistered", "D11-C is not open preregistered")
    require(d11_c.get("predecessor_decision_digest") == EXPECTED_OPENING_DIGEST, "D11-C predecessor drift")
    require(d11_c.get("decision") is None, "D11-C prematurely selects a result")
    require(d11_c.get("human_acceptance", {}).get("accepted") is False, "D11-C prematurely accepted")
    require(d11_c.get("authorization_effect", {}).get("investigation_active") is True, "D11-C is not active")
    c_candidates = d11_c.get("preregistered_candidates", [])
    require({row.get("candidate_id") for row in c_candidates} == {"D11-C-T0", "D11-C-T1", "D11-C-T2", "D11-C-T3"}, "D11-C candidate roster drift")
    require(all(row.get("accepted_authority") is False for row in c_candidates), "D11-C candidate marked accepted")
    require(d11_c.get("authority_routing_record", {}).get("decision_digest") == EXPECTED_ROUTING_DIGEST, "D11-C routing digest drift")
    require(d11_c.get("authority_routing_record", {}).get("file_sha256") == EXPECTED_ROUTING_SHA, "D11-C routing identity drift")
    require(d11_c.get("authority_routing_record", {}).get("local_debt_id") == "D11-C-DEBT-BASELINE-TRANSPORT-AUTHORITY", "D11-C local debt drift")

    d11_g9 = validate_record_digest(D11_G9, EXPECTED_D11_G9_DIGEST)
    require(d11_g9.get("status") == "queued_preregistered", "D11-G9 is not queued")
    require(d11_g9.get("predecessor_decision_digest") == EXPECTED_OPENING_DIGEST, "D11-G9 predecessor drift")
    require(d11_g9.get("decision") is None, "D11-G9 prematurely selects a result")
    require(d11_g9.get("human_acceptance", {}).get("accepted") is False, "D11-G9 prematurely accepted")
    require(d11_g9.get("scientific_activation_precondition", {}).get("satisfied") is False, "D11-G9 activation bypassed D11-C")
    require(d11_g9.get("authorization_effect", {}).get("GRC9_or_GRC9V3_change_authorized") is False, "D11-G9 authorizes legacy edits")
    g9_candidates = d11_g9.get("preregistered_candidates", [])
    require({row.get("candidate_id") for row in g9_candidates} == {"D11-G9-P0", "D11-G9-P1", "D11-G9-P2", "D11-G9-P3"}, "D11-G9 candidate roster drift")
    require(all(row.get("accepted_authority") is False for row in g9_candidates), "D11-G9 candidate marked accepted")
    require(d11_g9.get("authority_routing_record", {}).get("decision_digest") == EXPECTED_ROUTING_DIGEST, "D11-G9 routing digest drift")
    require(d11_g9.get("authority_routing_record", {}).get("file_sha256") == EXPECTED_ROUTING_SHA, "D11-G9 routing identity drift")
    require(d11_g9.get("authority_routing_record", {}).get("local_debt_id") == "D11-G9-DEBT-CANONICAL-PORT-ALLOCATION", "D11-G9 local debt drift")

    validate_source_identity_rows(d11_c)
    validate_source_identity_rows(d11_g9)
    require(routing.get("authorization_effect", {}).get("D11_C_investigation_active") is True, "D11 routing lost active C gate")
    return opening, d11_c, d11_g9


def validate_specification_holds() -> None:
    grcv4 = GRCV4_SPEC.read_text(encoding="utf-8")
    grc9v4 = GRC9V4_SPEC.read_text(encoding="utf-8")
    for marker in (
        "Candidate C implementation conformance is on",
        "Candidate C V4 baseline transport candidate D11-C-T1",
        "Preregistered, non-normative candidate.",
        "candidate_c_log_sector_potential_flow_v1",
        "not yet normative",
    ):
        require(marker in grcv4, f"GRCV4 D11-C hold marker missing: {marker}")
    for marker in (
        "Mechanical-expansion conformance is on bounded hold",
        "Preregistered D11-G9 candidate G9-P1",
        "grc9v4_collision_free_v1",
        "not yet normative",
    ):
        require(marker in grc9v4, f"GRC9V4 D11-G9 hold marker missing: {marker}")

    manifest = load_object(SOURCE_MANIFEST)
    require(manifest.get("status") == "normative_source_identity_with_pending_d11_candidates", "source manifest D11 status drift")
    pending = {row.get("role"): row for row in manifest.get("pending_successor_sources", [])}
    expected_pending = {
        "accepted_bounded_D11_successor_opening": (OPENING, EXPECTED_OPENING_DIGEST),
        "accepted_bounded_D11_claim_debt_authority_routing": (ROUTING, EXPECTED_ROUTING_DIGEST),
        "D11_C_open_preregistration": (D11_C, EXPECTED_D11_C_DIGEST),
        "D11_G9_queued_preregistration": (D11_G9, EXPECTED_D11_G9_DIGEST),
    }
    require(set(pending) == set(expected_pending), "source manifest pending D11 roster drift")
    for role, (path, digest) in expected_pending.items():
        row = pending[role]
        require(row.get("file_sha256") == sha256_file(path), f"source manifest hash drift: {role}")
        require(row.get("record_digest") == digest, f"source manifest record digest drift: {role}")
    closures = {row.get("closure_id"): row for row in manifest.get("post_d10_v4_closures", [])}
    require(all(row.get("accepted_by_D11") is False for row in closures.values()), "source manifest prematurely accepts a D11 closure")
    require(all(str(row.get("authority_status", "")).startswith("provisional_preregistered") for row in closures.values()), "source manifest loses provisional closure status")

    fixtures = load_object(FIXTURES)
    require(fixtures.get("status") == "mixed_normative_and_D11_preregistered_preimplementation_fixture_contract", "fixture D11 status drift")
    boundary = fixtures.get("authority_boundary", {})
    require(boundary.get("D11_dependent_rows_are_conformance_authority") is False, "D11 fixtures marked authoritative")
    require(boundary.get("candidate_c_runtime_execution_blocked_pending_D11_C") is True, "Candidate C runtime hold missing")
    require(boundary.get("GRC9V4_full_conformance_blocked_pending_D11_G9") is True, "GRC9V4 conformance hold missing")
    c_rows = {row.get("id"): row for row in fixtures.get("candidate_c_cases", []) if isinstance(row, dict)}
    require(c_rows["C-BASELINE-EXACT"].get("authority_status") == "preregistered_D11-C-T1_not_normative", "C baseline fixture authority drift")
    require(fixtures.get("grc9_expansion_fixture", {}).get("authority_status") == "preregistered_D11-G9-P1_not_normative", "GRC9 expansion fixture authority drift")

    require(sha256_file(ROOT / "papers/2026-04-GRC-9.md") == "cefc33e91e496c236660dad5c1e009a720ca908488db460d47322118dd7c3e08", "historical GRC9 paper changed")
    require(sha256_file(ROOT / "specs/grc-9-v3-spec.md") == "7b1f0c03988be7dbe3feb8ba926d43d891d70daa0dbbae9804fc70f2a4950f2f", "GRC9V3 spec changed")


def validate_checklist_state() -> None:
    checklist = CHECKLIST.read_text(encoding="utf-8")
    completed_markers = (
        "- [x] Carry all 39 current D10 claims",
        "- [x] Carry all 29 historical claim nodes",
        "- [x] Carry all 29 D10 debt transformations",
        "- [x] Carry all 11 verification obligations",
        "- [x] Bind D11-C to the exact claim/debt/verification carry-forward record.",
        "- [x] Preregister D11-C-T1, D11-C-T2, D11-C-T3, and bounded-unresolved D11-C-T0",
    )
    unresolved_markers = (
        "- [ ] Freeze the exact type, domain, codomain, positivity, and authority of",
        "- [ ] Freeze the exact equation producing $J_{0,C}$.",
        "- [ ] Prove graph-relabel and signed-edge-orientation covariance",
        "- [ ] Pressure D11-C-T1, D11-C-T2, D11-C-T3, and D11-C-T0",
        "- [ ] Record a separately accepted or boundedly unresolved D11-C successor",
    )
    for marker in completed_markers:
        require(marker in checklist, f"completed D11 checklist marker missing: {marker}")
    if "D11-C = accepted_bounded_C_HM_STIFFNESS_BASELINE_v1" not in checklist:
        for marker in unresolved_markers:
            require(marker in checklist, f"open D11-C checklist marker missing: {marker}")


def validate_source_observation() -> tuple[str, int, str]:
    contract = load_et_c0_contract(SIDE_TOOL_ROOT / "records/ETC0SourceAndLayoutContract.json")
    observation = discover_sources(ROOT, admitted_rows(contract))
    require(observation.get("state") == "new_unprocessed_source_available", "D11 records were silently admitted or source observation is not fail-closed")
    added = observation.get("added_unprocessed", [])
    added_paths = {row.get("path") for row in added}
    expected_paths = {
        "implementation/investigations/grc9v4-constitutive-design/decisions/D11SuccessorInvestigationOpening.json",
        "implementation/investigations/grc9v4-constitutive-design/decisions/D11ClaimDebtAndAuthorityRouting.json",
        "implementation/investigations/grc9v4-constitutive-design/decisions/D11CCandidateCBaselineTransportAndMobilityClosure.json",
        "implementation/investigations/grc9v4-constitutive-design/decisions/D11G9CanonicalExpansionPortAllocationClosure.json",
    }
    require(
        expected_paths <= added_paths,
        f"D11 opening source observation is incomplete: {sorted(expected_paths - added_paths)}",
    )
    return observation["state"], len(added), observation["observation_digest"]


def main() -> int:
    require(Path(sys.prefix).resolve() == (ROOT / ".venv").resolve(), "run with the repository .venv Python")
    validate_opening()
    validate_specification_holds()
    validate_checklist_state()
    for path in (
        DECISIONS / "D11SuccessorInvestigationOpening.md",
        DECISIONS / "D11ClaimDebtAndAuthorityRouting.md",
        DECISIONS / "D11CCandidateCBaselineTransportAndMobilityClosure.md",
        DECISIONS / "D11G9CanonicalExpansionPortAllocationClosure.md",
        GRCV4_SPEC,
        GRC9V4_SPEC,
    ):
        validate_render(path)
    source_state, added_count, observation_digest = validate_source_observation()
    print(
        "D11_SUCCESSOR_OPENING_AUDIT_PASS "
        "D10.2=immutable claims=39+29 debt=29 obligations=11 contracts=152 "
        "opening_snapshot_D11-C=open_preregistered "
        "opening_snapshot_D11-G9=queued_preregistered "
        "implementation=false legacy_changes=false "
        f"source_observation_state={source_state} "
        f"unprocessed_source_count={added_count} "
        f"source_observation_digest={observation_digest}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
