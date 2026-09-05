#!/usr/bin/env python3
"""Audit accepted-bounded D11-C within the advancing D11 successor phase."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
INVESTIGATION = ROOT / "implementation/investigations/grc9v4-constitutive-design"
DECISIONS = INVESTIGATION / "decisions"
SIDE_TOOL_ROOT = INVESTIGATION / "tools/exploratory-side-tool"
TOOL_ROOT = SIDE_TOOL_ROOT / "tool"

RESOLUTION = DECISIONS / "D11CCandidateBaselineTransportAndMobilityResolution.json"
RESOLUTION_MD = DECISIONS / "D11CCandidateBaselineTransportAndMobilityResolution.md"
SUPPLEMENT = DECISIONS / "D11CCandidateBaselineTransportProvenanceSupplement.json"
WITNESS = INVESTIGATION / "scripts/witness_d11_c_hm_stiffness_baseline.py"
CHECKLIST = INVESTIGATION / "GRC9V4ConstitutiveDesignChecklist.md"
LEDGER = INVESTIGATION / "GRC9V4ConstitutiveDesignDecisionLedger.md"
README = INVESTIGATION / "README.md"

EXPECTED_RESOLUTION_DIGEST = (
    "82e8008e8edade39db7b5327a31a807031b712dcc86b3fe3e8c0977bda51e797"
)
EXPECTED_RESOLUTION_SHA = (
    "31bd8d3e8163d100d0935870cf7082fb3e393aab4c70018c45354a3a5c54ebd7"
)
EXPECTED_SUPPLEMENT_DIGEST = (
    "57d711d80e648c8ee73401f3a7e76a0076374fc43bd4d2d0f3dbe4bb4ee3acb1"
)
EXPECTED_SUPPLEMENT_SHA = (
    "43bb028c6c7b09952a35dee280067470f2ff5cde4395d39c5b5e7aba6fae29fb"
)
EXPECTED_WITNESS_SHA = (
    "5ec4db289eee2e4d0fdf82e27f3b656d4be35ad594309855a6c402370be6aaa4"
)
EXPECTED_D11_C_PREREG_DIGEST = (
    "c1c22c88fa676705370d01256a34801a364e310c93e4ef85cc5a3208e6e06a78"
)

sys.path.insert(0, str(INVESTIGATION / "scripts"))
sys.path.insert(0, str(TOOL_ROOT / "src"))

import audit_grc9v4_d11_successor_opening as opening_audit  # noqa: E402
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
    require(sha256_file(RESOLUTION) == EXPECTED_RESOLUTION_SHA, "D11-C resolution file identity drift")
    resolution = load_object(RESOLUTION)
    require(resolution.get("decision_record_digest") == EXPECTED_RESOLUTION_DIGEST, "D11-C recorded digest drift")
    require(canonical_digest(resolution, "decision_record_digest") == EXPECTED_RESOLUTION_DIGEST, "D11-C canonical digest mismatch")
    require(resolution.get("status") == "accepted_bounded", "D11-C is not accepted bounded")
    require(resolution.get("predecessor_decision_digest") == EXPECTED_D11_C_PREREG_DIGEST, "D11-C predecessor drift")
    require(resolution.get("supersedes") == "GRC9V4-CD-D11-C-v1", "D11-C supersession drift")

    decision = resolution.get("decision", {})
    require(decision.get("selected_candidate_id") == "D11-C-T3a", "D11-C selected candidate drift")
    require(decision.get("selected_profile_id") == "C-HM-STIFFNESS-BASELINE-v1", "D11-C selected profile drift")
    require(decision.get("graph_scope") == "finite_graph_fixed_topology_closed_no_flux_regular_selector_stratum", "D11-C graph scope drift")
    require(decision.get("authoritative_state_dimension_changed") is False, "D11-C adds hidden state")
    require(decision.get("GRC9_specific_premise_used") is False, "D11-C is not graph generic")
    require(decision.get("GRC9_or_GRC9V3_source_changed") is False, "D11-C changes legacy authority")

    equations = resolution.get("selected_equations", {})
    expected_equations = {
        "retained_Hodge": "H1_form_M=D_C*H1_form(h)*D_C",
        "transport_mobility": "M4_C=eta_C*Diag(W_C_tr)",
        "baseline_potential": "Phi_0_C=kappa_Phi_C*B*H1_form_M*d0*C-Vprime_C_U(C)",
        "baseline_current": "J0_C=-M4_C*d0*Phi_0_C",
        "total_current": "J_C_C=(I-zeta_C*chi_C*Rhat_C_flux)^-1*J0_C",
    }
    for key, expected in expected_equations.items():
        require(equations.get(key) == expected, f"D11-C equation drift: {key}")

    reference = resolution.get("reference_transport_contract", {})
    require(reference.get("codomain") == "strictly_positive_finite_scalars", "D11-C reference positivity drift")
    require(reference.get("ordinary_beat_writer") == "none", "D11-C reference gained an ordinary writer")
    require("entire_exact_W_C_tr_map" in reference.get("migration_rule", ""), "D11-C target-map lifecycle is not exact")
    require("no_implicit_copy_resize_interpolation_or_history_transport" in reference.get("topology_rule", ""), "D11-C lifecycle admits implicit reconstruction")
    require(reference.get("forbidden_authority_arrow") == "H1_form_to_M4_C", "D11-C mobility/Hodge authority boundary drift")

    units = resolution.get("unit_contract", {})
    expected_units = {
        "physical_current_unit": "[J]=[C]/[t]",
        "H1_form_and_W_C_tr_unit": "[H1]",
        "vertex_potential_unit": "[Phi]",
        "kappa_Phi_C_unit": "[Phi]/([H1][C])",
        "M4_C_unit": "[J]/[Phi]=[C]/([t][Phi])",
        "eta_C_unit": "[M4]/[H1]=[C]/([t][Phi][H1])",
    }
    for key, expected in expected_units.items():
        require(units.get(key) == expected, f"D11-C unit drift: {key}")
    require(units.get("hidden_unit_defaults_allowed") is False, "D11-C permits hidden unit defaults")

    controls = resolution.get("control_contract", {})
    for control in ("kappa_M_C_zero", "chi_C_zero", "zeta_C_zero", "tau_C_zero"):
        require(control in controls, f"D11-C control missing: {control}")
    disabled = resolution.get("disabled_compatibility_contract", {})
    require(disabled.get("owner") == "GRC9V4_specialization_dispatch", "disabled-branch owner drift")
    require(disabled.get("substitution_or_approximation_with_T3a_forbidden") is True, "T3a may substitute for disabled GRC9V3")
    require("unchanged_GRC9V3" in disabled.get("disabled_branch", ""), "disabled branch does not delegate to unchanged GRC9V3")

    stages = resolution.get("realization_stage_contract", [])
    require({row.get("profile_id") for row in stages} == {"C_CI", "C_OS", "C_RG2b", "C_PC", "C_CI_PC"}, "D11-C realization-stage roster drift")
    require("recompute_it_from_scratch" in next(row["stage"] for row in stages if row["profile_id"] == "C_OS"), "OS corrector freshness drift")

    dispositions = {row.get("candidate_id"): row for row in resolution.get("candidate_dispositions", [])}
    require(set(dispositions) == {"D11-C-T0", "D11-C-T1", "D11-C-T2", "D11-C-T3", "D11-C-T3a"}, "D11-C candidate disposition roster drift")
    require(dispositions["D11-C-T3a"].get("disposition") == "selected_accepted_bounded", "T3a is not accepted")
    require(dispositions["D11-C-T1"].get("disposition") == "not_selected_preserved_for_comparison", "T1 disposition drift")

    topology = resolution.get("claim_topology_effect", {})
    require(topology.get("D10_current_claims_rewritten") == 0, "D11-C rewrites D10 claims")
    require(topology.get("D10_historical_claims_rewritten") == 0, "D11-C rewrites historical claims")
    require(topology.get("D10_claims_reclassified") == 0, "D11-C reclassifies D10 claims")
    require(topology.get("successor_claim_ids_added") == ["D11-C-CL-O-001"], "D11-C successor claim roster drift")

    debt = resolution.get("debt_transformation", {})
    require(debt.get("predecessor_D10_debt_transformation_count") == 29, "D11-C inherited debt count drift")
    require(debt.get("predecessor_D10_debt_dispositions_changed") == 0, "D11-C rewrites inherited debt")
    require(debt.get("local_debt_successor_status") == "resolved_bounded_by_D11_C_T3a", "D11-C local debt is not resolved")

    obligations = resolution.get("verification_obligation_effect", {})
    require(obligations.get("D10_verification_obligation_count_carried") == 11, "D11-C inherited obligation count drift")
    require(obligations.get("D10_pending_forward_obligations_remaining") == 10, "D11-C pending obligation count drift")
    require(obligations.get("D10_pending_obligations_discharged_by_this_design_result") == 0, "D11-C improperly discharges implementation evidence")

    authorization = resolution.get("authorization_effect", {})
    require(authorization.get("D11_C_closed_accepted_bounded") is True, "D11-C closeout authority missing")
    require(authorization.get("D11_G9_investigation_active") is True, "D11-G9 was not activated")
    require(authorization.get("paper_propagation_authorized_now") is False, "paper propagation opened early")
    require(authorization.get("specification_propagation_authorized_now") is False, "spec propagation opened early")
    require(authorization.get("implementation_authorized") is False, "implementation opened early")
    require(authorization.get("runtime_or_src_tests_change_authorized") is False, "src/tests opened early")
    require(authorization.get("GRC9_or_GRC9V3_change_authorized") is False, "legacy edits opened")
    require(resolution.get("human_acceptance", {}).get("accepted") is True, "D11-C human acceptance missing")

    propagation = resolution.get("propagation_state", {})
    require(propagation.get("paper_updated") is False, "paper was propagated before D11-G9")
    require(propagation.get("specification_updated") is False, "spec was propagated before D11-G9")
    require(propagation.get("source_manifest_updated_with_accepted_result") is False, "source manifest was propagated before D11-G9")

    opening_audit.validate_source_identity_rows(resolution)
    return resolution


def validate_supplement() -> dict[str, Any]:
    require(sha256_file(SUPPLEMENT) == EXPECTED_SUPPLEMENT_SHA, "D11-C supplement file identity drift")
    supplement = load_object(SUPPLEMENT)
    require(supplement.get("artifact_digest") == EXPECTED_SUPPLEMENT_DIGEST, "D11-C supplement recorded digest drift")
    require(canonical_digest(supplement, "artifact_digest") == EXPECTED_SUPPLEMENT_DIGEST, "D11-C supplement canonical digest mismatch")
    require(supplement.get("status") == "accepted_bounded_companion_registry", "D11-C supplement status drift")
    require(supplement.get("normative_object_count") == 3, "D11-C object count drift")
    require(len(supplement.get("normative_objects", [])) == 3, "D11-C object roster drift")
    require(supplement.get("equation_contract_count") == 11, "D11-C contract count drift")
    require(len(supplement.get("equation_contracts", [])) == 11, "D11-C contract roster drift")
    require(len({row["object_id"] for row in supplement["normative_objects"]}) == 3, "duplicate D11-C object ID")
    require(len({row["equation_contract_id"] for row in supplement["equation_contracts"]}) == 11, "duplicate D11-C contract ID")

    claim = supplement.get("accepted_successor_claim", {})
    require(claim.get("claim_id") == "D11-C-CL-O-001", "D11-C successor claim ID drift")
    require(claim.get("claim_class") == "optional_profile_normative", "D11-C claim class drift")
    expected_edges = {"D10-CL-O-002", "D10-CL-N-003", "D10-CL-N-006", "D10-CL-N-008", "D10-CL-C-011"}
    edges = supplement.get("claim_edges", [])
    require({row.get("predecessor_claim_id") for row in edges} == expected_edges, "D11-C reciprocal claim-edge roster drift")
    require(all(row.get("successor_claim_id") == "D11-C-CL-O-001" for row in edges), "D11-C claim edge targets drift")
    require(all(row.get("predecessor_status_changed") is False for row in edges), "D11-C claim edge mutates predecessor")

    counts = supplement.get("successor_population_counts", {})
    require(counts == {
        "D10_2_objects_retained": 67,
        "D11_C_objects_added": 3,
        "combined_current_objects": 70,
        "D10_2_equation_contracts_retained": 152,
        "D11_C_equation_contracts_added": 11,
        "combined_current_equation_contracts": 163,
        "D10_2_claim_nodes_rewritten": 0,
        "D11_C_successor_claims_added": 1,
    }, "D11-C successor population counts drift")
    preservation = supplement.get("predecessor_registry_preservation", {})
    require(preservation.get("D10_2_files_modified") is False, "D11-C supplement mutates D10.2")
    require(preservation.get("D10_2_counts_or_digests_rewritten") is False, "D11-C supplement rewrites D10.2 counts")
    opening_audit.validate_source_identity_rows(supplement)
    return supplement


def validate_witness(resolution: dict[str, Any]) -> None:
    require(sha256_file(WITNESS) == EXPECTED_WITNESS_SHA, "D11-C witness identity drift")
    result = subprocess.run(
        [sys.executable, str(WITNESS)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    require(result.returncode == 0, f"D11-C witness failed: {result.stderr.strip()}")
    observed = json.loads(result.stdout)
    recorded = resolution.get("algebra_witness", {})
    for key in (
        "closure_residual_l2",
        "charge_residual_absolute",
        "baseline_dissipation",
        "retained_geometry_off_effect_l2",
        "orientation_covariance_error_l2",
    ):
        require(abs(float(observed[key]) - float(recorded[key])) < 1e-14, f"D11-C witness result drift: {key}")
    require(observed.get("profile_id") == "C-HM-STIFFNESS-BASELINE-v1", "D11-C witness profile drift")
    require(observed["closure_residual_l2"] < 1e-12, "D11-C closure residual too large")
    require(observed["charge_residual_absolute"] < 1e-12, "D11-C charge residual too large")
    require(observed["retained_geometry_off_effect_l2"] > 0, "D11-C direct Hodge path is inert")
    require(observed["orientation_covariance_error_l2"] < 1e-12, "D11-C orientation covariance failed")


def validate_live_state() -> None:
    checklist = CHECKLIST.read_text(encoding="utf-8")
    for marker in (
        "- [x] Freeze the exact type, domain, codomain, positivity, and authority of",
        "- [x] Freeze the exact equation producing $J_{0,C}$.",
        "- [x] Prove graph-relabel and signed-edge-orientation covariance",
        "- [x] Record a separately accepted or boundedly unresolved D11-C successor",
        "D11-C = accepted_bounded_C_HM_STIFFNESS_BASELINE_v1",
    ):
        require(marker in checklist, f"D11-C checklist transition missing: {marker}")
    require(
        "D11-G9 = accepted_bounded_D11-G9-P4a" in checklist
        or "D11-G9 = active_preregistered_after_accepted_D11-C" in checklist,
        "D11-G9 successor state is not visible",
    )
    for path, markers in (
        (LEDGER, ("### D11-C Accepted-Bounded Successor", EXPECTED_RESOLUTION_DIGEST)),
        (README, ("is accepted bounded as corrected candidate D11-C-T3a",)),
    ):
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            require(marker in text, f"{path}: current D11 state marker missing: {marker}")


def validate_source_observation() -> tuple[str, int, str]:
    contract = load_et_c0_contract(SIDE_TOOL_ROOT / "records/ETC0SourceAndLayoutContract.json")
    observation = discover_sources(ROOT, admitted_rows(contract))
    require(observation.get("state") == "new_unprocessed_source_available", "D11 sources were silently admitted or fail-closed discovery drifted")
    added = observation.get("added_unprocessed", [])
    added_paths = {row.get("path") for row in added}
    expected_paths = {
        "implementation/investigations/grc9v4-constitutive-design/decisions/D11SuccessorInvestigationOpening.json",
        "implementation/investigations/grc9v4-constitutive-design/decisions/D11ClaimDebtAndAuthorityRouting.json",
        "implementation/investigations/grc9v4-constitutive-design/decisions/D11CCandidateCBaselineTransportAndMobilityClosure.json",
        "implementation/investigations/grc9v4-constitutive-design/decisions/D11G9CanonicalExpansionPortAllocationClosure.json",
        "implementation/investigations/grc9v4-constitutive-design/decisions/D11CCandidateBaselineTransportAndMobilityResolution.json",
        "implementation/investigations/grc9v4-constitutive-design/decisions/D11CCandidateBaselineTransportProvenanceSupplement.json",
    }
    require(
        expected_paths <= added_paths,
        f"D11-C source observation is incomplete: {sorted(expected_paths - added_paths)}",
    )
    return observation["state"], len(added), observation["observation_digest"]


def main() -> int:
    require(Path(sys.prefix).resolve() == (ROOT / ".venv").resolve(), "run with the repository .venv Python")
    opening_audit.validate_opening()
    opening_audit.validate_specification_holds()
    resolution = validate_resolution()
    validate_supplement()
    validate_witness(resolution)
    validate_live_state()
    for path in (RESOLUTION_MD, CHECKLIST, LEDGER, README):
        opening_audit.validate_render(path)
    source_state, added_count, observation_digest = validate_source_observation()
    print(
        "D11_C_RESOLUTION_AUDIT_PASS "
        f"resolution_digest={EXPECTED_RESOLUTION_DIGEST} "
        "selected=D11-C-T3a profile=C-HM-STIFFNESS-BASELINE-v1 "
        "claims=39+29+1 inherited_debt=29 pending_obligations=10 "
        "objects=67+3 contracts=152+11 D11-G9=successor_state_valid "
        "paper_spec_propagation=false implementation=false legacy_changes=false "
        f"source_observation_state={source_state} "
        f"unprocessed_source_count={added_count} "
        f"source_observation_digest={observation_digest}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
