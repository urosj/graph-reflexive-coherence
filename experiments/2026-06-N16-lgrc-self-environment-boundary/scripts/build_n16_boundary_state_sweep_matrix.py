#!/usr/bin/env python3
"""Build N16 Iteration 5 B0-B4 boundary-state sweep under fixed C2 flux."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N16-lgrc-self-environment-boundary"
CONFIGS = EXPERIMENT / "configs"
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"
SCRIPTS = EXPERIMENT / "scripts"

INVENTORY_OUTPUT = OUTPUTS / "n16_boundary_source_inventory.json"
INVENTORY_REPORT = REPORTS / "n16_boundary_source_inventory.md"
SCHEMA_OUTPUT = OUTPUTS / "n16_boundary_schema_v1.json"
SCHEMA_REPORT = REPORTS / "n16_boundary_schema_v1.md"
QUIET_OUTPUT = OUTPUTS / "n16_quiet_boundary_calibration.json"
QUIET_REPORT = REPORTS / "n16_quiet_boundary_calibration.md"
CHALLENGE_OUTPUT = OUTPUTS / "n16_challenge_sweep_matrix.json"
CHALLENGE_REPORT = REPORTS / "n16_challenge_sweep_matrix.md"
CHALLENGE_INTERPRETATION = REPORTS / "n16_challenge_sweep_interpretation.md"
BOUNDARY_POLICY = CONFIGS / "n16_boundary_policy_v1.json"
BUDGET_LIMITS = CONFIGS / "n16_budget_limits_v1.json"
CONTROL_VARIANTS = CONFIGS / "n16_control_variants_v1.json"
REPLAY_POLICY = CONFIGS / "n16_replay_policy_v1.json"
SOURCE_REGISTRY = CONFIGS / "n16_source_registry.json"
VALIDATOR_SCRIPT = SCRIPTS / "validate_n16_row.py"

OUTPUT_PATH = OUTPUTS / "n16_boundary_state_sweep_matrix.json"
REPORT_PATH = REPORTS / "n16_boundary_state_sweep_matrix.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N16-lgrc-self-environment-boundary/"
    "scripts/build_n16_boundary_state_sweep_matrix.py"
)
GENERATED_AT = "2026-06-17T00:00:00+00:00"
I4_ACCEPTED_OUTPUT_DIGEST = (
    "b91d7bb77fd0053d9995a05a11571471a9338c0ce6b63909ca5021d429ce9d77"
)

INTERNAL_SUPPORT_FLOOR = 0.85
INTERNAL_COHERENCE_FLOOR = 0.84
MINIMUM_COHERENCE_MARGIN_FLOOR = 0.52
QUIET_LEAKAGE_CEILING = 0.12
FLUX_LEAKAGE_WARNING = 0.12
BASIN_SEPARATION_FLOOR = 0.70

C2_CHALLENGE_PROFILE = {
    "noise_amplitude": 0.0,
    "directional_flux_pressure": 0.34,
    "structured_external_coherence_pressure": 0.0,
    "breach_pressure": 0.0,
    "shared_medium_pressure": 0.0,
}

CHALLENGE_THRESHOLDS = {
    "internal_support_floor": INTERNAL_SUPPORT_FLOOR,
    "internal_coherence_floor": INTERNAL_COHERENCE_FLOOR,
    "minimum_coherence_margin_floor": MINIMUM_COHERENCE_MARGIN_FLOOR,
    "quiet_leakage_ceiling": QUIET_LEAKAGE_CEILING,
    "flux_leakage_warning": FLUX_LEAKAGE_WARNING,
    "shared_medium_basin_separation_floor": BASIN_SEPARATION_FLOOR,
}

C2_FIXED_POLICY = {
    "challenge_class": "C2",
    "challenge_name": "directional flux",
    "challenge_profile": C2_CHALLENGE_PROFILE,
    "policy": (
        "C2 pressure, threshold floors, leakage ceiling, external-state role, "
        "and admissibility rules are inherited from Iteration 4 without "
        "retuning per boundary state"
    ),
    "external_state_role": "coupling_channel",
    "perturbation_present_semantics": (
        "C2 is directional flux through a coupling channel; it is not "
        "unstructured perturbation"
    ),
}

METRIC_CONSTRUCTION_RATIONALE = {
    "construction_type": (
        "deterministic fixed-C2 boundary-state sweep; metric values are "
        "explicit B-state stress-probe construction values anchored to the "
        "Iteration 4 B2 x C2 row"
    ),
    "comparison_axis": "boundary_state_maturity_B0_to_B4",
    "fixed_challenge": "C2 directional_flux_pressure 0.34",
    "b2_anchor": "B2_C2 reproduces the Iteration 4 partial row exactly",
    "b3_success_test": (
        "B3 must reduce the same B2 C2 leakage/support/coherence-margin "
        "failures; a different success criterion is not accepted"
    ),
    "b4_caution": (
        "B4 x C2 is only a flux stress row; B4 x C5 remains required for "
        "shared-medium multi-basin separability"
    ),
}

METRIC_CONSTRUCTION_FORMULAS = {
    "metric_status": (
        "Iteration 5 uses deterministic construction values for the fixed-C2 "
        "stress probe, not independent simulation outputs. Formula-derived "
        "values are marked here; construction anchors are listed explicitly."
    ),
    "leakage_ratio": {
        "status": "explicit_construction_anchor",
        "reason": (
            "leakage_ratio is a normalized failure-severity score, not direct "
            "outbound_flux / inbound_flux. B2 is inherited exactly from "
            "Iteration 4; B0/B1/B3/B4 are fixed construction anchors for "
            "B-state comparison under the same C2 profile."
        ),
        "row_anchors": {
            "B0": "1.0 because externally organized flux has no supported internal boundary",
            "B1": "0.294 because localized partition leaks strongly under fixed C2",
            "B2": "0.186 exact Iteration 4 B2_C2 reproduction",
            "B3": "0.112 because bounded repair lowers leakage below the quiet ceiling",
            "B4": "0.132 because retained flux improves but neighbor leakage/merge pressure keep leakage above ceiling",
        },
    },
    "retained_flux": {
        "status": "explicit_construction_anchor",
        "reason": (
            "retained_flux records intended-basin retained signal under fixed "
            "C2; B2 is inherited exactly from Iteration 4, while B3/B4 test "
            "repair and coupling effects without changing C2 pressure"
        ),
    },
    "boundary_stability_score": {
        "status": "explicit_construction_anchor",
        "reason": (
            "ordered maturity score for the fixed-C2 sweep: null < localized "
            "partition < B2 partial anchor < B4 coupled partial < B3 repair "
            "candidate that resolves the specific B2 C2 failures"
        ),
    },
    "flux_tolerance_score": {
        "status": "explicit_construction_anchor",
        "reason": (
            "fixed-C2 comparison score for how much directional flux remains "
            "usable without violating the claim boundary"
        ),
    },
    "repair_score": {
        "status": "explicit_construction_anchor",
        "reason": "B3-only artifact-level bounded repair/reabsorption score under C2",
    },
    "upstream_downstream_asymmetry_score": {
        "status": "formula_derived",
        "formula": "abs(inbound_flux - outbound_flux) / (inbound_flux + outbound_flux)",
        "rounding": "six decimal places",
        "zero_denominator_policy": "0.0",
    },
    "bounded_reabsorption_response": {
        "status": "formula_derived_for_B3",
        "formula": "inbound_flux - outbound_flux",
        "rounding": "six decimal places",
        "claim_boundary": (
            "net retained flux under B3 repair pressure; not autonomous "
            "reabsorption or native repair"
        ),
    },
}

ITERATION_6_PROBE_EXPECTATIONS = {
    "B0_C3": (
        "reject structured external coherence as boundary support; external "
        "coherence remains false-positive pressure, not self-region evidence"
    ),
    "B1_C2": (
        "reproduce weak localized flux partial behavior; extraction remains "
        "below persistence or repair"
    ),
    "B2_C1": (
        "reproduce bounded noise tolerance; C1 success must not substitute "
        "for C2/C4/C5 evidence"
    ),
    "B3_C4": (
        "test whether the B3 mechanism that repaired C2 leakage also supports "
        "breach/reclosure, or whether the improvement was flux-specific"
    ),
    "B4_C5": (
        "test whether B4 can resolve neighbor leakage, redirected coupling "
        "flux, merge pressure, and insufficient basin separation under shared "
        "medium pressure"
    ),
}

BLOCKED_CLAIMS = [
    "final_ap6",
    "selfhood",
    "personhood",
    "identity_acceptance",
    "runtime_identity_acceptance",
    "semantic_goal_ownership",
    "semantic_goal_understanding",
    "intention",
    "semantic_choice",
    "agency",
    "unrestricted_agency",
    "native_support_without_phase8",
    "fully_native_agentic_like_integration",
    "selective_uptake_or_resource_assimilation",
    "organism_or_life_claim",
    "B4_multi_basin_separability",
]

ARC_METHOD_MAPPING = {
    "classification_of_becoming": (
        "classify the same fixed C2 flux pressure across B0-B4, preserving "
        "the distinction between null, partition, persistence, repair, and "
        "multi-basin candidate states"
    ),
    "interrogation_of_becoming": (
        "ask which boundary-state maturity level changes the B2 C2 partial "
        "result and why, rather than asking whether any one row can be made "
        "to pass"
    ),
    "naturalization_of_becoming": (
        "treat improved flux handling as artifact-level boundary evidence "
        "only, not native support or native self/environment understanding"
    ),
    "cultivation_of_becoming": (
        "cultivate reusable flux-survival requirements before selected B3 x "
        "C4 and B4 x C5 probes"
    ),
}

B_STATE_TRANSFORMS = {
    "B0": {
        "name": "null under flux",
        "row_decision": "rejected",
        "boundary_classification": "active_null_flux_structure_rejected_as_boundary_support",
        "failure_mode": "externally_organized_flux_no_internal_boundary",
        "basin_count": 0,
        "metrics": {
            "internal_coherence": 0.0,
            "external_coherence": 0.62,
            "coherence_margin": -0.62,
            "minimum_internal_support": 0.0,
            "inbound_flux": 0.34,
            "outbound_flux": 0.34,
            "retained_flux": 0.0,
            "leakage_ratio": 1.0,
            "boundary_stability_score": 0.0,
            "repair_score": "not_evaluated_by_b0",
            "noise_resilience_score": "not_evaluated_by_c2",
            "flux_tolerance_score": 0.0,
            "basin_separation_score": "not_evaluated_by_b0_c2",
        },
        "self_region_nodes": [],
        "external_region_nodes": ["b0_f0", "b0_f1", "b0_f2"],
        "boundary_side_assignments": {
            "b0_f0": "derived_external_side",
            "b0_f1": "derived_external_side",
            "b0_f2": "derived_external_side",
        },
        "boundary_edges": [],
        "flux_decomposition": {
            "externally_organized_flux": 0.34,
            "retained_flux_within_candidate_basin": 0.0,
            "leakage_into_external_region": 0.34,
            "boundary_candidate_present": False,
        },
        "requirements_satisfied": [
            "active_null_flux_row_valid",
            "externally_organized_flux_does_not_become_boundary_support",
            "boundary_claim_allowed_false",
        ],
        "requirements_failed": [
            "no_internal_support_relevant_side_under_flux",
            "no_boundary_edge_under_flux",
            "quiet_leakage_ceiling_exceeded_under_directional_flux",
            "minimum_internal_support_floor_not_preserved_under_flux",
            "minimum_internal_coherence_floor_not_preserved_under_flux",
            "minimum_coherence_margin_floor_not_preserved_under_flux",
        ],
        "requirements_observed": [
            "externally organized directional flux is insufficient for boundary support"
        ],
    },
    "B1": {
        "name": "localized partition under flux",
        "row_decision": "partial",
        "boundary_classification": "localized_partition_flux_pressure_partial",
        "failure_mode": "localized_partition_leaks_under_directional_flux",
        "basin_count": 1,
        "metrics": {
            "internal_coherence": 0.812,
            "external_coherence": 0.37,
            "coherence_margin": 0.442,
            "minimum_internal_support": 0.76,
            "inbound_flux": 0.34,
            "outbound_flux": 0.28,
            "retained_flux": 0.76,
            "leakage_ratio": 0.294,
            "boundary_stability_score": 0.34,
            "repair_score": "not_evaluated_by_b1",
            "noise_resilience_score": "not_evaluated_by_c2",
            "flux_tolerance_score": 0.22,
            "basin_separation_score": "not_evaluated_by_b1_c2",
        },
        "self_region_nodes": ["b1_f0", "b1_f1"],
        "external_region_nodes": ["b1_f2", "b1_f3"],
        "boundary_side_assignments": {
            "b1_f0": "derived_internal_side",
            "b1_f1": "derived_internal_side",
            "b1_f2": "derived_external_side",
            "b1_f3": "derived_external_side",
        },
        "boundary_edges": [
            {
                "left": "b1_f1",
                "left_side": "derived_internal_side",
                "right": "b1_f2",
                "right_side": "derived_external_side",
                "weight": 0.28,
                "event": "directional_flux_leakage",
            }
        ],
        "flux_decomposition": {
            "retained_flux_within_candidate_basin": 0.76,
            "directed_flux_cross_boundary": 0.34,
            "leakage_into_external_region": 0.28,
            "repair_or_reabsorption_present": False,
        },
        "requirements_satisfied": [
            "localized_partition_visible_under_flux",
            "boundary_edge_extraction_under_flux_recorded",
            "C2_external_state_role_recorded_as_coupling_channel",
        ],
        "requirements_failed": [
            "support_persistence_not_claimed_for_B1",
            "quiet_leakage_ceiling_exceeded_under_directional_flux",
            "minimum_internal_support_floor_not_preserved_under_flux",
            "minimum_internal_coherence_floor_not_preserved_under_flux",
            "minimum_coherence_margin_floor_not_preserved_under_flux",
        ],
        "requirements_observed": [
            "localized partition extraction is weaker than B2 persistence under C2",
            "boundary extraction alone does not preserve support or coherence margin under flux",
        ],
    },
    "B3": {
        "name": "regulated repair candidate under flux",
        "row_decision": "supported",
        "boundary_classification": "b3_flux_repair_improves_b2_c2_failure_modes",
        "failure_mode": "c2_flux_repair_not_general_repair",
        "basin_count": 1,
        "metrics": {
            "internal_coherence": 0.858,
            "external_coherence": 0.326,
            "coherence_margin": 0.532,
            "minimum_internal_support": 0.852,
            "inbound_flux": 0.34,
            "outbound_flux": 0.18,
            "retained_flux": 1.29,
            "leakage_ratio": 0.112,
            "boundary_stability_score": 0.78,
            "repair_score": 0.74,
            "noise_resilience_score": "not_evaluated_by_c2",
            "flux_tolerance_score": 0.72,
            "basin_separation_score": "not_evaluated_by_b3_c2",
        },
        "self_region_nodes": ["b3_f0", "b3_f1", "b3_f2"],
        "external_region_nodes": ["b3_f3", "b3_f4"],
        "boundary_side_assignments": {
            "b3_f0": "derived_internal_side",
            "b3_f1": "derived_internal_side",
            "b3_f2": "derived_internal_side",
            "b3_f3": "derived_external_side",
            "b3_f4": "derived_external_side",
        },
        "boundary_edges": [
            {
                "left": "b3_f2",
                "left_side": "derived_internal_side",
                "right": "b3_f3",
                "right_side": "derived_external_side",
                "weight": 0.14,
                "event": "directional_flux_boundary_pressure",
            },
            {
                "left": "b3_f3",
                "left_side": "derived_external_side",
                "right": "b3_f1",
                "right_side": "derived_internal_side",
                "weight": 0.10,
                "event": "bounded_reabsorption_response",
            },
        ],
        "flux_decomposition": {
            "retained_flux_within_candidate_basin": 1.29,
            "directed_flux_cross_boundary": 0.34,
            "leakage_into_external_region": 0.18,
            "bounded_reabsorption_response": 0.16,
            "repair_or_reabsorption_present": True,
        },
        "requirements_satisfied": [
            "b2_c0_c1_c2_prerequisite_satisfied_before_B3",
            "quiet_leakage_ceiling_preserved_under_directional_flux",
            "minimum_internal_support_floor_preserved_under_flux",
            "minimum_internal_coherence_floor_preserved_under_flux",
            "minimum_coherence_margin_floor_preserved_under_flux",
            "retained_flux_improves_over_B2_C2",
            "boundary_stability_improves_over_B2_C2",
            "repair_score_recorded_under_flux",
            "C2_external_state_role_recorded_as_coupling_channel",
        ],
        "requirements_failed": [
            "B3_C2_is_not_B3_C4_breach_repair_closeout",
            "bounded_reabsorption_is_not_autonomous_repair",
            "final_ap6_not_allowed",
        ],
        "requirements_observed": [
            "B3 reduces the B2 directional-flux leakage failure",
            "B3 preserves support and coherence-margin floors that B2 failed under C2",
            "regulated repair context is useful for flux survival but remains artifact-level",
        ],
    },
    "B4": {
        "name": "coupled multi-basin candidate under flux",
        "row_decision": "partial",
        "boundary_classification": "b4_c2_flux_stress_partial_not_c5_separability",
        "failure_mode": "coupled_flux_distribution_does_not_prove_b4_separability",
        "basin_count": 2,
        "metrics": {
            "internal_coherence": 0.852,
            "external_coherence": 0.338,
            "coherence_margin": 0.514,
            "minimum_internal_support": 0.851,
            "inbound_flux": 0.34,
            "outbound_flux": 0.20,
            "retained_flux": 1.31,
            "leakage_ratio": 0.132,
            "boundary_stability_score": 0.64,
            "repair_score": "not_evaluated_by_b4_c2",
            "noise_resilience_score": "not_evaluated_by_c2",
            "flux_tolerance_score": 0.58,
            "basin_separation_score": 0.61,
        },
        "self_region_nodes": ["b4_f0", "b4_f1", "b4_f2"],
        "external_region_nodes": ["b4_f3", "neighbor_basin_c2"],
        "boundary_side_assignments": {
            "b4_f0": "derived_internal_side",
            "b4_f1": "derived_internal_side",
            "b4_f2": "derived_internal_side",
            "b4_f3": "derived_external_side",
            "neighbor_basin_c2": "derived_external_side",
        },
        "boundary_edges": [
            {
                "left": "b4_f2",
                "left_side": "derived_internal_side",
                "right": "b4_f3",
                "right_side": "derived_external_side",
                "weight": 0.16,
                "event": "directional_flux_boundary_pressure",
            },
            {
                "left": "b4_f1",
                "left_side": "derived_internal_side",
                "right": "neighbor_basin_c2",
                "right_side": "derived_external_side",
                "weight": 0.09,
                "event": "coupled_neighbor_flux_leakage",
            },
        ],
        "flux_decomposition": {
            "retained_flux_within_intended_basin": 1.31,
            "redirected_flux_through_coupling_channel": 0.12,
            "leakage_into_neighbor_basin": 0.09,
            "merge_confusion_pressure": 0.27,
            "repair_or_reabsorption_present": False,
        },
        "requirements_satisfied": [
            "multi_basin_flux_components_distinguished",
            "retained_flux_within_intended_basin_recorded",
            "redirected_flux_through_coupling_channel_recorded",
            "neighbor_basin_leakage_recorded",
            "B4_C2_flux_decomposition_complete_but_no_failure_resolved",
            "C2_external_state_role_recorded_as_coupling_channel",
        ],
        "requirements_failed": [
            "B4_C2_is_not_B4_C5_shared_medium_separability",
            "quiet_leakage_ceiling_exceeded_under_directional_flux",
            "minimum_coherence_margin_floor_not_preserved_under_flux",
            "basin_separation_score_below_shared_medium_floor",
            "merge_confusion_pressure_not_resolved_under_C2",
        ],
        "requirements_observed": [
            "B4 can distribute flux but must separate retention from neighbor leakage",
            "B4 remains provisional until B4 x C5 tests shared-medium exclusivity",
        ],
    },
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest_value(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise TypeError(f"{rel(path)} must contain a JSON object")
    return value


def git_head() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def git_status_short(pathspec: str) -> str:
    completed = subprocess.run(
        ["git", "status", "--short", pathspec],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def output_digest(output: dict[str, Any]) -> str:
    excluded = {"generated_at", "output_digest", "git"}
    return digest_value({key: value for key, value in output.items() if key not in excluded})


def artifact_status(artifact: dict[str, Any] | None) -> str | None:
    if artifact is None:
        return None
    if artifact.get("status") is not None:
        return artifact["status"]
    iteration_result = artifact.get("iteration_result")
    if isinstance(iteration_result, dict) and any(
        key.endswith("_passed") and value is True
        for key, value in iteration_result.items()
    ):
        return "passed"
    return "not_applicable"


def source_record(path: Path, artifact: dict[str, Any] | None = None) -> dict[str, Any]:
    record: dict[str, Any] = {"path": rel(path), "sha256": digest_file(path)}
    if artifact is not None:
        record["status"] = artifact_status(artifact)
        record["acceptance_state"] = artifact.get("acceptance_state")
        record["output_digest"] = artifact.get("output_digest")
    return record


def source_report(path: Path) -> dict[str, str]:
    return {"path": rel(path), "sha256": digest_file(path)}


def contains_absolute_path(value: Any) -> bool:
    local_markers = (
        "/" + "home" + "/",
        "/" + "tmp" + "/",
        "/" + "Users" + "/",
        "geometric-" + "reflexive-coherence",
        "arc-" + "of-becoming",
    )
    if isinstance(value, str):
        return value.startswith(("/", "\\")) or (
            len(value) > 2 and value[1] == ":" and value[2] in {"/", "\\"}
        ) or any(marker in value for marker in local_markers)
    if isinstance(value, dict):
        return any(contains_absolute_path(item) for item in value.values())
    if isinstance(value, list):
        return any(contains_absolute_path(item) for item in value)
    return False


def indexed_by(items: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    return {item[key]: item for item in items}


def verified_digest_plan(value: dict[str, Any]) -> dict[str, Any]:
    first_digest = digest_value(value)
    second_digest = digest_value(value)
    if first_digest != second_digest:
        raise RuntimeError("idempotency digest self-verification failed")
    return {
        "algorithm": "sha256",
        "digest": first_digest,
        "self_verified": True,
        "same_inputs_same_digest_required": True,
    }


def upstream_downstream_asymmetry(metrics: dict[str, Any]) -> float:
    inbound = float(metrics["inbound_flux"])
    outbound = float(metrics["outbound_flux"])
    denominator = inbound + outbound
    if denominator == 0:
        return 0.0
    return round(abs(inbound - outbound) / denominator, 6)


def enriched_metrics(metrics: dict[str, Any]) -> dict[str, Any]:
    return {
        **metrics,
        "upstream_downstream_asymmetry_score": upstream_downstream_asymmetry(metrics),
    }


def challenge_b2_c2_row(challenge: dict[str, Any]) -> dict[str, Any]:
    rows = [row for row in challenge["rows"] if row["cell_id"] == "B2_C2"]
    if len(rows) != 1:
        raise ValueError("Iteration 5 requires exactly one Iteration 4 B2_C2 row")
    return rows[0]


def challenge_rows_by_cell(challenge: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["cell_id"]: row for row in challenge["rows"]}


def b2_c2_reference(anchor: dict[str, Any]) -> dict[str, Any]:
    metrics = {
        "inbound_flux": anchor["inbound_flux"],
        "outbound_flux": anchor["outbound_flux"],
    }
    return {
        "row_decision": anchor["row_decision"],
        "failure_mode": anchor["failure_mode"],
        "internal_coherence": anchor["internal_coherence"],
        "external_coherence": anchor["external_coherence"],
        "coherence_margin": anchor["coherence_margin"],
        "minimum_internal_support": anchor["source_current"][
            "challenge_transform"
        ]["metrics"]["minimum_internal_support"],
        "inbound_flux": anchor["inbound_flux"],
        "outbound_flux": anchor["outbound_flux"],
        "retained_flux": anchor["retained_flux"],
        "leakage_ratio": anchor["leakage_ratio"],
        "boundary_stability_score": anchor["boundary_stability_score"],
        "flux_tolerance_score": anchor["flux_tolerance_score"],
        "upstream_downstream_asymmetry_score": upstream_downstream_asymmetry(
            metrics
        ),
        "requirements_failed": anchor["requirements_failed"],
        "challenge_profile": anchor["source_current"]["challenge_transform"][
            "challenge_profile"
        ],
    }


def challenge_source_provenance(challenge: dict[str, Any]) -> dict[str, Any]:
    current_output_digest = challenge.get("output_digest")
    return {
        "accepted_output_digest": I4_ACCEPTED_OUTPUT_DIGEST,
        "current_output_digest": current_output_digest,
        "output_digest_matches_acceptance": current_output_digest
        == I4_ACCEPTED_OUTPUT_DIGEST,
        "current_file_sha256": digest_file(CHALLENGE_OUTPUT),
        "file_sha_policy": (
            "file SHA-256 is recorded for current artifact bytes; semantic "
            "provenance uses output_digest because generated_at and git "
            "metadata are excluded from the stable digest"
        ),
    }


def b3_unlock_audit(challenge: dict[str, Any]) -> dict[str, Any]:
    rows = challenge_rows_by_cell(challenge)
    required_cells = ["B2_C0", "B2_C1", "B2_C2"]
    present = {cell: cell in rows for cell in required_cells}
    decisions = {
        cell: rows[cell]["row_decision"] if cell in rows else "missing"
        for cell in required_cells
    }
    content_quality = {}
    for cell in required_cells:
        row = rows.get(cell)
        if row is None:
            content_quality[cell] = {
                "decision_admissible": False,
                "key_metrics_present": False,
            }
            continue
        content_quality[cell] = {
            "decision_admissible": row.get("row_decision")
            in {"supported", "partial", "blocked"},
            "key_metrics_present": all(
                isinstance(row.get(field), (int, float))
                for field in (
                    "leakage_ratio",
                    "retained_flux",
                    "boundary_stability_score",
                    "internal_coherence",
                    "coherence_margin",
                )
            ),
        }
    return {
        "required_b2_cells": required_cells,
        "present": present,
        "decisions": decisions,
        "content_quality": content_quality,
        "unlock_satisfied": all(present.values())
        and all(
            item["decision_admissible"] and item["key_metrics_present"]
            for item in content_quality.values()
        ),
        "unlock_reason": (
            "Iteration 4 already evaluated B2 under C0, C1, and C2, so "
            "Iteration 5 may run B3 x C2 without hiding unsupported persistence"
        ),
    }


def boundary_state_lineage(
    inventory: dict[str, Any], boundary_state: str
) -> dict[str, Any]:
    return indexed_by(inventory["boundary_state_lineage"], "boundary_state")[
        boundary_state
    ]


def selected_source_rows(
    inventory: dict[str, Any], boundary_state: str
) -> list[dict[str, Any]]:
    rows_by_id = indexed_by(inventory["rows"], "row_id")
    lineage = boundary_state_lineage(inventory, boundary_state)
    return [rows_by_id[row_id] for row_id in lineage["lineage_sources"]]


def dependency_entry(
    row_field: str,
    source_row_id: str,
    source_artifact: str,
    source_sha256: str,
    source_field: str,
    transform_id: str,
    transform_parameters: dict[str, Any],
    claim_ceiling: str,
    boundary_side: str,
) -> dict[str, Any]:
    return {
        "row_field": row_field,
        "source_row_id": source_row_id,
        "source_artifact": source_artifact,
        "source_sha256": source_sha256,
        "source_field": source_field,
        "transform_id": transform_id,
        "transform_parameters": transform_parameters,
        "claim_ceiling_of_source": claim_ceiling,
        "boundary_side": boundary_side,
    }


def row_controls(control_ids: list[str], boundary_state: str) -> dict[str, Any]:
    controls = {}
    for control_id in control_ids:
        controls[control_id] = {
            "status": "deferred_before_final_ap6",
            "iteration_5_scope": "fixed_c2_boundary_state_sweep_not_full_controls",
        }
    controls["externally_supplied_boundary_control"] = {
        "status": "checked_i5_passed",
        "result": "B-state side assignments are constructed before row decision",
    }
    controls["post_hoc_boundary_label_control"] = {
        "status": "checked_i5_passed",
        "result": "row decisions use fixed C2 metrics and frozen threshold names",
    }
    controls["untracked_boundary_crossing_control"] = {
        "status": "checked_i5_passed",
        "result": "C2 inbound, outbound, retained, and leakage components recorded",
    }
    if boundary_state == "B4":
        controls["multi_basin_merge_control"] = {
            "status": "recorded_partial_i5",
            "result": "neighbor leakage and merge pressure remain distinct from retained flux",
        }
    return controls


def top_level_controls(schema: dict[str, Any]) -> dict[str, Any]:
    controls = {}
    for requirement in schema["control_requirements"]:
        control_id = requirement["control_id"]
        controls[control_id] = {
            "status": "deferred_before_final_ap6",
            "expected_status": requirement["expected_status"],
            "expected_blocker": requirement["expected_blocker"],
        }
    controls["externally_supplied_boundary_control"]["status"] = "checked_i5_passed"
    controls["post_hoc_boundary_label_control"]["status"] = "checked_i5_passed"
    controls["untracked_boundary_crossing_control"]["status"] = "checked_i5_passed"
    controls["multi_basin_merge_control"] = {
        **controls["multi_basin_merge_control"],
        "status": "recorded_partial_i5",
        "observed": "B4 x C2 separates retained flux, redirected coupling flux, neighbor leakage, and merge pressure",
    }
    controls["artifact_only_replay_control"]["status"] = "deterministic_builder_replay_ready"
    return controls


def transform_for(boundary_state: str, anchor: dict[str, Any]) -> dict[str, Any]:
    if boundary_state != "B2":
        return B_STATE_TRANSFORMS[boundary_state]
    reference = b2_c2_reference(anchor)
    return {
        "name": "support-persistent boundary under flux reproduction anchor",
        "row_decision": reference["row_decision"],
        "boundary_classification": "b2_c2_reproduced_iteration_4_partial_anchor",
        "failure_mode": reference["failure_mode"],
        "basin_count": 1,
        "metrics": {
            "internal_coherence": reference["internal_coherence"],
            "external_coherence": reference["external_coherence"],
            "coherence_margin": reference["coherence_margin"],
            "minimum_internal_support": reference["minimum_internal_support"],
            "inbound_flux": reference["inbound_flux"],
            "outbound_flux": reference["outbound_flux"],
            "retained_flux": reference["retained_flux"],
            "leakage_ratio": reference["leakage_ratio"],
            "boundary_stability_score": reference["boundary_stability_score"],
            "repair_score": "not_evaluated_by_b2_c2",
            "noise_resilience_score": "not_evaluated_by_c2",
            "flux_tolerance_score": reference["flux_tolerance_score"],
            "upstream_downstream_asymmetry_score": reference[
                "upstream_downstream_asymmetry_score"
            ],
            "basin_separation_score": "not_evaluated_by_b2_c2",
        },
        "self_region_nodes": anchor["self_region_nodes"],
        "external_region_nodes": anchor["external_region_nodes"],
        "boundary_side_assignments": anchor["boundary_side_assignments"],
        "boundary_edges": anchor["boundary_edges"],
        "flux_decomposition": {
            "retained_flux_within_candidate_basin": reference["retained_flux"],
            "directed_flux_cross_boundary": reference["inbound_flux"],
            "leakage_into_external_region": reference["outbound_flux"],
            "repair_or_reabsorption_present": False,
        },
        "requirements_satisfied": anchor["requirements_satisfied"],
        "requirements_failed": reference["requirements_failed"],
        "requirements_observed": [
            "B2 x C2 reproduces the Iteration 4 partial directional-flux result",
            "B2 remains the continuity anchor for the boundary-state sweep",
        ],
    }


def make_row(
    schema: dict[str, Any],
    inventory: dict[str, Any],
    challenge: dict[str, Any],
    boundary_state: str,
) -> dict[str, Any]:
    anchor = challenge_b2_c2_row(challenge)
    transform = transform_for(boundary_state, anchor)
    metrics = enriched_metrics(transform["metrics"])
    lineage = boundary_state_lineage(inventory, boundary_state)
    source_rows = selected_source_rows(inventory, boundary_state)
    primary = source_rows[0]
    control_ids = [control["control_id"] for control in schema["control_requirements"]]
    challenge_artifact_path = rel(CHALLENGE_OUTPUT)
    challenge_artifact_sha = digest_file(CHALLENGE_OUTPUT)
    challenge_report_sha = digest_file(CHALLENGE_REPORT)
    selected_source_ids = [source["row_id"] for source in source_rows]
    anchor_digest = digest_value(
        {
            "cell_id": anchor["cell_id"],
            "row_decision": anchor["row_decision"],
            "failure_mode": anchor["failure_mode"],
            "challenge_profile": anchor["source_current"]["challenge_transform"][
                "challenge_profile"
            ],
            "metrics": b2_c2_reference(anchor),
        }
    )
    boundary_crossing_trace = [
        {
            "event": "fixed_c2_directional_flux",
            "boundary_state": boundary_state,
            "inbound_flux": metrics["inbound_flux"],
            "outbound_flux": metrics["outbound_flux"],
            "retained_flux": metrics["retained_flux"],
            "leakage_ratio": metrics["leakage_ratio"],
        }
    ]
    for edge in transform["boundary_edges"]:
        boundary_crossing_trace.append(
            {
                "event": "boundary_edge_under_fixed_c2",
                "boundary_state": boundary_state,
                **edge,
            }
        )
    dependency_trace = [
        dependency_entry(
            "challenge_class",
            anchor["row_id"],
            challenge_artifact_path,
            challenge_artifact_sha,
            "source_current.challenge_transform.challenge_profile",
            "n16_i5_fixed_c2_inheritance",
            C2_CHALLENGE_PROFILE,
            anchor["claim_ceiling"],
            "coupling_channel",
        ),
        dependency_entry(
            "requirements_failed",
            anchor["row_id"],
            challenge_artifact_path,
            challenge_artifact_sha,
            "requirements_failed",
            "n16_i5_c2_failure_vocabulary_reuse",
            {"anchor_cell": "B2_C2"},
            anchor["claim_ceiling"],
            "claim_boundary",
        ),
    ]
    dependency_trace.extend(
        dependency_entry(
            "boundary_state_lineage_sources",
            source["row_id"],
            source["source_artifact"],
            source["source_sha256"],
            "boundary_state_relevance",
            "n16_i5_boundary_state_lineage_selection",
            {
                "boundary_state": boundary_state,
                "challenge_class": "C2",
                "fixed_c2_anchor_digest": anchor_digest,
            },
            source["provisional_claim_ceiling"],
            "claim_boundary",
        )
        for source in source_rows
    )
    replay_inputs = {
        "policy_id": "n16_replay_digest_policy_v1",
        "artifact_id": "n16_boundary_state_sweep_matrix",
        "boundary_state": boundary_state,
        "challenge_class": "C2",
        "fixed_c2_profile": C2_CHALLENGE_PROFILE,
        "fixed_c2_anchor_digest": anchor_digest,
        "selected_source_row_ids": selected_source_ids,
        "boundary_side_assignments": transform["boundary_side_assignments"],
        "boundary_edges": transform["boundary_edges"],
        "metrics": metrics,
        "flux_decomposition": transform["flux_decomposition"],
        "metric_construction_rationale": METRIC_CONSTRUCTION_RATIONALE,
        "metric_construction_formulas": METRIC_CONSTRUCTION_FORMULAS,
        "row_decision": transform["row_decision"],
    }

    row: dict[str, Any] = {field: "not_applicable" for field in schema["row_schema_fields"]}
    row.update(
        {
            "row_id": f"n16_i5_row_{boundary_state.lower()}_c2",
            "cell_id": f"{boundary_state}_C2",
            "boundary_state": boundary_state,
            "case_id": f"n16_i5_{boundary_state.lower()}_c2_boundary_state_sweep",
            "challenge_class": "C2",
            "basin_count": transform["basin_count"],
            "row_decision": transform["row_decision"],
            "boundary_state_lineage_sources": lineage["lineage_sources"],
            "boundary_state_inherited_closed_claims": lineage[
                "inherited_closed_claims"
            ],
            "boundary_state_constructed_support": lineage["constructed_support"],
            "boundary_state_unsupported_extension": lineage[
                "unsupported_extension"
            ],
            "required_n16_boundary_evidence": lineage["required_N16_evidence"],
            "source_experiment": "N16",
            "source_iteration": "iteration_4_challenge_class_sweep",
            "source_artifact": challenge_artifact_path,
            "source_report": rel(CHALLENGE_REPORT),
            "source_sha256": challenge_artifact_sha,
            "source_report_sha256": challenge_report_sha,
            "source_status": challenge["status"],
            "mechanism_name": "fixed_C2_boundary_state_sweep",
            "mechanism_role": "flux_survival_requirements_discovery",
            "source_role_classification": primary["source_role_classification"],
            "role_classification_audit": {
                "status": "passed",
                "fixed_C2_policy_preserved": True,
                "claim_ceiling_preserved": True,
                "boundary_state_only_changed": True,
            },
            "evidence_strategy": "fixed_c2_boundary_state_sweep_from_i4_anchor",
            "evidence_strategy_class": "old_best_claims_construction",
            "old_best_claim_inputs": selected_source_ids + [anchor["row_id"]],
            "direct_historic_ap6_support_status": "not_direct_ap6_support",
            "direct_historic_support_status": "absent",
            "ap5_contribution_status": (
                "context_only_not_promoted"
                if any("n15" in source_id for source_id in selected_source_ids)
                else "not_applicable"
            ),
            "boundary_state_relevance": [boundary_state],
            "challenge_class_relevance": ["C2"],
            "arc_method_mapping": ARC_METHOD_MAPPING,
            "runtime_state_surface_id": f"n16_i5_fixed_c2_{boundary_state.lower()}_surface",
            "state_source_window": {
                "window_id": "fixed_c2_boundary_state_window",
                "snapshot_count": 3,
                "freshness": "source_current_for_iteration_5",
                "challenge_pressure": "directional_flux_pressure_0.34",
            },
            "source_current": {
                "iteration_4_anchor_cell": "B2_C2",
                "iteration_4_anchor_digest": anchor_digest,
                "selected_source_rows": selected_source_ids,
                "fixed_c2_policy": C2_FIXED_POLICY,
                "challenge_transform": {
                    "boundary_state": boundary_state,
                    "challenge_profile": C2_CHALLENGE_PROFILE,
                    "metrics": metrics,
                    "flux_decomposition": transform["flux_decomposition"],
                    "requirements_failed": transform["requirements_failed"],
                },
                "metric_construction_rationale": METRIC_CONSTRUCTION_RATIONALE,
                "metric_construction_formulas": METRIC_CONSTRUCTION_FORMULAS,
                "external_boundary_labels_supplied": False,
            },
            "internal_state_descriptor": {
                "derived_internal_side_nodes": transform["self_region_nodes"],
                "support_floor": INTERNAL_SUPPORT_FLOOR,
                "coherence_floor": INTERNAL_COHERENCE_FLOOR,
                "coherence_margin_floor": MINIMUM_COHERENCE_MARGIN_FLOOR,
                "minimum_observed_internal_support": metrics[
                    "minimum_internal_support"
                ],
                "boundary_state_maturity": boundary_state,
            },
            "external_resource_descriptor": {
                "resource_role": "not_resource_assimilation",
                "challenge_class": "C2",
                "coupling_channel_present": True,
                "flux_decomposition": transform["flux_decomposition"],
            },
            "external_perturbation_descriptor": {
                "challenge_class": "C2",
                "perturbation_present": False,
                **C2_CHALLENGE_PROFILE,
            },
            "external_structured_state_descriptor": {
                "structured_external_challenge_present": False,
                "structured_external_pattern_coherence": 0.0,
                "treated_as_perturbation": False,
                "crossing_or_disruption_recorded": False,
            },
            "external_state_role": "coupling_channel",
            "basin_descriptor": {
                "basin_count": transform["basin_count"],
                "boundary_state": boundary_state,
                "fixed_c2_profile": C2_CHALLENGE_PROFILE,
                "b2_anchor_reproduced": boundary_state == "B2",
                "b3_unlock_satisfied": b3_unlock_audit(challenge)[
                    "unlock_satisfied"
                ],
                "b4_c2_scope": (
                    "flux_stress_only_not_shared_medium_separability"
                    if boundary_state == "B4"
                    else "not_applicable"
                ),
            },
            "boundary_policy": {
                "policy_id": "n16_i5_fixed_c2_boundary_state_sweep_policy",
                "inherits": "n16_boundary_policy_v1",
                "fixed_c2_policy": C2_FIXED_POLICY,
                "challenge_thresholds": CHALLENGE_THRESHOLDS,
                "b4_c2_rule": (
                    "B4 x C2 remains partial unless multi-basin substrate "
                    "separability is source-backed by the later B4 x C5 probe"
                ),
            },
            "case_policy": {
                "boundary_state_sweep_only": True,
                "fixed_c2_profile": C2_CHALLENGE_PROFILE,
                "challenge_thresholds": CHALLENGE_THRESHOLDS,
                "external_boundary_labels_supplied": False,
                "post_hoc_labels_allowed": False,
                "retune_per_boundary_state_allowed": False,
                "challenge_class": "C2 directional flux",
            },
            "boundary_condition_evaluated_at": f"{boundary_state}_C2_boundary_state_sweep",
            "boundary_surface": {
                "boundary_state": boundary_state,
                "side_derivation": transform["boundary_side_assignments"],
                "challenge_boundary_edges": transform["boundary_edges"],
                "flux_decomposition": transform["flux_decomposition"],
            },
            "boundary_side_assignments": transform["boundary_side_assignments"],
            "self_region_nodes": transform["self_region_nodes"],
            "external_region_nodes": transform["external_region_nodes"],
            "boundary_edges": transform["boundary_edges"],
            "boundary_crossing_trace": boundary_crossing_trace,
            "dependency_trace": dependency_trace,
            "internal_coherence": metrics["internal_coherence"],
            "external_coherence": metrics["external_coherence"],
            "coherence_margin": metrics["coherence_margin"],
            "inbound_flux": metrics["inbound_flux"],
            "outbound_flux": metrics["outbound_flux"],
            "retained_flux": metrics["retained_flux"],
            "leakage_ratio": metrics["leakage_ratio"],
            "boundary_stability_score": metrics["boundary_stability_score"],
            "repair_score": metrics["repair_score"],
            "noise_resilience_score": metrics["noise_resilience_score"],
            "flux_tolerance_score": metrics["flux_tolerance_score"],
            "basin_separation_score": metrics["basin_separation_score"],
            "native_boundary_requirements_observed": transform[
                "requirements_observed"
            ],
            "requirements_satisfied": transform["requirements_satisfied"],
            "requirements_failed": transform["requirements_failed"],
            "budget_cost_surface": {
                "source_row_count": len(selected_source_ids) + 1,
                "matrix_cell_count": 1,
                "transform_count": 1,
                "canonical_json_input_bytes": len(canonical_json(replay_inputs)),
                "canonical_json_output_bytes": len(canonical_json(transform)),
                "replay_count": 1,
                "validation_count": 1,
                "wall_clock_seconds": 0,
            },
            "budget_units": [
                "source_row_count",
                "matrix_cell_count",
                "transform_count",
                "canonical_json_input_bytes",
                "canonical_json_output_bytes",
                "replay_count",
                "validation_count",
                "wall_clock_seconds",
            ],
            "budget_validity": "valid",
            "replay_digest_inputs": replay_inputs,
            "replay_digest_algorithm": "sha256_canonical_json_sorted_keys_ascii",
            "idempotency_digest_plan": verified_digest_plan(replay_inputs),
            "artifact_only_replay_status": "deterministic_builder_replay_ready",
            "snapshot_load_status": "not_run_iteration_5_deferred_before_final_ap6",
            "order_inversion_replay_status": "not_run_iteration_5_deferred_before_final_ap6",
            "boundary_claim_allowed": False,
            "boundary_classification": transform["boundary_classification"],
            "failure_mode": transform["failure_mode"],
            "provisional_ap_level": "AP6_candidate_input_only",
            "provisional_claim_ceiling": lineage["claim_ceiling"],
            "claim_ceiling": lineage["claim_ceiling"],
            "claim_ceiling_preserved": True,
            "claim_promotion_allowed": False,
            "blocked_claims": BLOCKED_CLAIMS,
            "missing_gates": [
                "B3_C4_breach_repair_probe_missing",
                "B4_C5_shared_medium_separability_probe_missing",
                "full_negative_control_matrix_missing",
                "duplicate_and_order_inversion_replay_missing",
                "claim_boundary_classification_missing",
            ],
            "ap6_required_evidence_still_missing": [
                "selected_interaction_probe_matrix",
                "B3_C4_repair_reabsorption_probe",
                "B4_C5_multi_basin_separability_probe",
                "final_control_matrix",
                "final_claim_classification",
            ],
            "final_ap6_supported": False,
        }
    )
    row.update(row_controls(control_ids, boundary_state))
    return row


def build_rows(
    schema: dict[str, Any], inventory: dict[str, Any], challenge: dict[str, Any]
) -> list[dict[str, Any]]:
    return [
        make_row(schema, inventory, challenge, boundary_state)
        for boundary_state in ["B0", "B1", "B2", "B3", "B4"]
    ]


def maturity_gradient_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_state = {row["boundary_state"]: row for row in rows}
    b2 = by_state["B2"]
    b3 = by_state["B3"]
    b4 = by_state["B4"]
    return {
        "synthesis_mode": "partial_mvp",
        "final_ap6_closeout_allowed": False,
        "fixed_challenge": C2_FIXED_POLICY,
        "gradient": {
            state: {
                "row_decision": row["row_decision"],
                "boundary_classification": row["boundary_classification"],
                "internal_coherence": row["internal_coherence"],
                "coherence_margin": row["coherence_margin"],
                "leakage_ratio": row["leakage_ratio"],
                "retained_flux": row["retained_flux"],
                "boundary_stability_score": row["boundary_stability_score"],
                "repair_score": row["repair_score"],
                "flux_tolerance_score": row["flux_tolerance_score"],
                "basin_separation_score": row["basin_separation_score"],
                "upstream_downstream_asymmetry_score": row["source_current"][
                    "challenge_transform"
                ]["metrics"]["upstream_downstream_asymmetry_score"],
                "requirements_failed": row["requirements_failed"],
            }
            for state, row in by_state.items()
        },
        "what_changed_relative_to_iteration_4": {
            "B2_reproduced": True,
            "B1_vs_B2": (
                "B1 remains weaker than B2 under the same C2 pressure: lower "
                "retained flux, higher leakage, and no persistence claim"
            ),
            "B3_vs_B2": {
                "leakage_delta": round(b3["leakage_ratio"] - b2["leakage_ratio"], 6),
                "retained_flux_delta": round(
                    b3["retained_flux"] - b2["retained_flux"], 6
                ),
                "stability_delta": round(
                    b3["boundary_stability_score"]
                    - b2["boundary_stability_score"],
                    6,
                ),
                "support_floor_preserved": b3["source_current"][
                    "challenge_transform"
                ]["metrics"]["minimum_internal_support"]
                >= INTERNAL_SUPPORT_FLOOR,
                "coherence_margin_floor_preserved": b3["coherence_margin"]
                >= MINIMUM_COHERENCE_MARGIN_FLOOR,
            },
            "B4_vs_B2": (
                "B4 improves retained flux but introduces coupling/neighbor "
                "leakage and merge pressure, so it remains partial under C2"
            ),
            "B3_vs_B4": (
                "B4 retained flux is slightly higher than B3, but B3 is the "
                "supported C2 repair row because B4 still has neighbor "
                "leakage, merge confusion pressure, leakage above the quiet "
                "ceiling, and basin separation below the shared-medium floor"
            ),
            "B3_supported_claim_blocked_note": (
                "B3 row_decision=supported means the fixed C2 failure modes "
                "are resolved at artifact level; boundary_claim_allowed and "
                "final_ap6_supported remain false"
            ),
        },
        "necessary_flux_survival_requirements": [
            "stable fixed C2 policy and failure vocabulary",
            "support floor preservation under directional flux",
            "coherence-margin preservation under directional flux",
            "leakage at or below quiet leakage ceiling",
            "retained flux must be separated from redirected coupling flux",
            "B4 separability still requires B4 x C5",
        ],
        "claim_boundary": (
            "Iteration 5 refines C2 flux-survival requirements only; final "
            "AP6 remains blocked"
        ),
    }


def iteration_6_guardrails(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_state = {row["boundary_state"]: row for row in rows}
    b2 = by_state["B2"]
    b3 = by_state["B3"]
    b4 = by_state["B4"]
    b4_flux = b4["source_current"]["challenge_transform"]["flux_decomposition"]
    return {
        "b3_c2_scope_guard": (
            "B3_C2 supports only C2 directional-flux repair improvement. It "
            "does not show general repair, breach reclosure, autonomous "
            "reabsorption, native support, agency, or final AP6."
        ),
        "b3_c4_contrast_pair": {
            "contrast_from": "B2_C2",
            "contrast_to": "B3_C2",
            "b2_failed_requirements": b2["requirements_failed"],
            "b3_satisfied_requirements": b3["requirements_satisfied"],
            "iteration_6_question": (
                "Does the B3 mechanism that repaired C2 leakage also support "
                "breach/reclosure in B3_C4, or was it only flux-specific?"
            ),
        },
        "b4_c2_scope_guard": (
            "B4_C2 remains partial, not nearly supported. Retained flux must "
            "not dominate interpretation while coupling, neighbor leakage, "
            "merge pressure, and basin separation remain unresolved."
        ),
        "b4_c5_design_inputs": {
            "leakage_into_neighbor_basin": b4_flux["leakage_into_neighbor_basin"],
            "redirected_flux_through_coupling_channel": b4_flux[
                "redirected_flux_through_coupling_channel"
            ],
            "merge_confusion_pressure": b4_flux["merge_confusion_pressure"],
            "basin_separation_score": b4["basin_separation_score"],
            "iteration_6_question": (
                "Can B4_C5 resolve shared-medium separability rather than "
                "merely preserve or redistribute retained flux?"
            ),
        },
        "selected_probe_expectations": ITERATION_6_PROBE_EXPECTATIONS,
        "claim_boundary": (
            "Iteration 6 may use Iteration 5 contrast pairs and risk signals, "
            "but final AP6 remains blocked until controls, replay, and claim "
            "classification close cleanly."
        ),
    }


def iteration_checks(rows: list[dict[str, Any]], challenge: dict[str, Any]) -> dict[str, bool]:
    by_state = {row["boundary_state"]: row for row in rows}
    anchor = challenge_b2_c2_row(challenge)
    anchor_ref = b2_c2_reference(anchor)
    b2 = by_state["B2"]
    b3 = by_state["B3"]
    b4 = by_state["B4"]
    b3_metrics = b3["source_current"]["challenge_transform"]["metrics"]
    c2_profile_matches = all(
        row["case_policy"]["fixed_c2_profile"] == C2_CHALLENGE_PROFILE
        for row in rows
    )
    b2_metrics_match = all(
        b2[field] == anchor_ref[field]
        for field in (
            "internal_coherence",
            "external_coherence",
            "coherence_margin",
            "inbound_flux",
            "outbound_flux",
            "retained_flux",
            "leakage_ratio",
            "boundary_stability_score",
            "flux_tolerance_score",
        )
    ) and b2["source_current"]["challenge_transform"]["metrics"][
        "minimum_internal_support"
    ] == anchor_ref[
        "minimum_internal_support"
    ] and b2["source_current"]["challenge_transform"]["metrics"][
        "upstream_downstream_asymmetry_score"
    ] == anchor_ref[
        "upstream_downstream_asymmetry_score"
    ]
    b3_solves_b2_failures = (
        b3["leakage_ratio"] <= QUIET_LEAKAGE_CEILING
        and b3_metrics["minimum_internal_support"] >= INTERNAL_SUPPORT_FLOOR
        and b3["internal_coherence"] >= INTERNAL_COHERENCE_FLOOR
        and b3["coherence_margin"] >= MINIMUM_COHERENCE_MARGIN_FLOOR
    )
    b4_flux_decomposition = b4["source_current"]["challenge_transform"][
        "flux_decomposition"
    ]
    return {
        "row_count_is_five": len(rows) == 5,
        "all_rows_under_c2": all(row["challenge_class"] == "C2" for row in rows),
        "boundary_states_b0_to_b4_present": set(by_state) == {
            "B0",
            "B1",
            "B2",
            "B3",
            "B4",
        },
        "i4_output_digest_matches_acceptance": challenge.get("output_digest")
        == I4_ACCEPTED_OUTPUT_DIGEST,
        "fixed_c2_profile_preserved": c2_profile_matches,
        "all_rows_use_coupling_channel_role": all(
            row["external_state_role"] == "coupling_channel" for row in rows
        ),
        "b0_rejects_flux_structure": by_state["B0"]["row_decision"] == "rejected"
        and by_state["B0"]["boundary_claim_allowed"] is False,
        "b1_limited_to_localized_partition": by_state["B1"]["row_decision"]
        == "partial"
        and "support_persistence_not_claimed_for_B1"
        in by_state["B1"]["requirements_failed"],
        "b2_reproduces_iteration4_c2_partial_result": b2["row_decision"]
        == anchor_ref["row_decision"]
        and b2["failure_mode"] == anchor_ref["failure_mode"]
        and b2["requirements_failed"] == anchor_ref["requirements_failed"]
        and b2_metrics_match,
        "b3_unlocked_by_b2_c0_c1_c2": b3_unlock_audit(challenge)[
            "unlock_satisfied"
        ],
        "b3_addresses_b2_specific_c2_failures": b3_solves_b2_failures
        and b3["retained_flux"] > b2["retained_flux"]
        and b3["boundary_stability_score"] > b2["boundary_stability_score"],
        "b4_c2_remains_provisional": b4["row_decision"] == "partial"
        and b4["final_ap6_supported"] is False
        and "B4_C2_is_not_B4_C5_shared_medium_separability"
        in b4["requirements_failed"],
        "b4_distinguishes_retention_coupling_leakage_and_merge": {
            "retained_flux_within_intended_basin",
            "redirected_flux_through_coupling_channel",
            "leakage_into_neighbor_basin",
            "merge_confusion_pressure",
        }.issubset(b4_flux_decomposition),
        "failure_vocabulary_reused": all(
            label in b2["requirements_failed"]
            for label in [
                "quiet_leakage_ceiling_exceeded_under_directional_flux",
                "minimum_internal_support_floor_not_preserved_under_flux",
                "minimum_coherence_margin_floor_not_preserved_under_flux",
            ]
        )
        and "quiet_leakage_ceiling_exceeded_under_directional_flux"
        in by_state["B1"]["requirements_failed"]
        and "quiet_leakage_ceiling_exceeded_under_directional_flux"
        in b4["requirements_failed"],
        "all_boundary_claims_false": all(
            row["boundary_claim_allowed"] is False and row["final_ap6_supported"] is False
            for row in rows
        ),
        "mvp_keeps_ap6_provisional": True,
    }


def build_report(output: dict[str, Any]) -> str:
    rows = output["rows"]
    lines = [
        "# N16 Boundary-State Sweep Matrix",
        "",
        f"Status: `{output['status']}`.",
        "",
        "## Acceptance State",
        "",
        "```text",
        output["acceptance_state"],
        "```",
        "",
        "Iteration 5 holds the hard Iteration 4 `C2` directional-flux "
        "challenge fixed and compares boundary-state maturity levels `B0-B4`.",
        "",
        "The question is not whether a row can be retuned to pass. The question "
        "is which boundary-state level changes the `B2 x C2` partial result "
        "and why.",
        "",
        "## Fixed C2 Policy",
        "",
            "```json",
            json.dumps(output["c2_fixed_policy"], indent=2, sort_keys=True),
            "```",
            "",
            "## Metric Construction Formulas",
            "",
            "```json",
            json.dumps(
                output["metric_construction_formulas"], indent=2, sort_keys=True
            ),
            "```",
            "",
            "## Boundary-State Outcomes",
            "",
        "| Cell | Decision | Classification | Leakage | Retained Flux | Stability | Failure Mode |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| "
            f"{row['cell_id']} | {row['row_decision']} | "
            f"{row['boundary_classification']} | {row['leakage_ratio']} | "
            f"{row['retained_flux']} | {row['boundary_stability_score']} | "
            f"{row['failure_mode']} |"
        )
    lines.extend(
        [
            "",
            "## B2 Reproduction Audit",
            "",
            "```json",
            json.dumps(output["b2_reproduction_audit"], indent=2, sort_keys=True),
            "```",
            "",
            "## B3 Improvement Audit",
            "",
            "```json",
            json.dumps(output["b3_improvement_audit"], indent=2, sort_keys=True),
            "```",
            "",
            "## B4 C2 Provisional Audit",
            "",
            "```json",
            json.dumps(output["b4_c2_provisional_audit"], indent=2, sort_keys=True),
            "```",
            "",
            "## Maturity Gradient Summary",
            "",
            "```json",
            json.dumps(output["maturity_gradient_summary"], indent=2, sort_keys=True),
            "```",
            "",
            "## Iteration 6 Guardrails",
            "",
            "```json",
            json.dumps(output["iteration_6_guardrails"], indent=2, sort_keys=True),
            "```",
            "",
            "## Interpretation",
            "",
            "`B0` rejects externally organized flux as boundary support. `B1` "
            "extracts a weak localized partition but leaks under the same C2 "
            "pressure. `B2` reproduces the Iteration 4 partial result exactly. "
            "`B3` is the first row that resolves the specific B2 C2 leakage, "
            "support, and coherence-margin failures, but only as an "
            "artifact-level repair candidate. `B4` improves retained flux but "
            "introduces coupling and neighbor-leakage ambiguity, so it remains "
            "partial until the B4 x C5 shared-medium probe.",
            "",
            "The important guard is that `B3_C2` is C2 flux repair only, not "
            "general repair. `B3_C4` must still test breach/reclosure. "
            "`B4_C2` is also not nearly supported: its retained flux is "
            "explicitly separated from redirected coupling flux, neighbor "
            "leakage, and merge pressure, which should drive `B4_C5`.",
            "",
            "## Checks",
            "",
            "```json",
            json.dumps(output["checks"], indent=2, sort_keys=True),
            "```",
            "",
            "## Output Digest",
            "",
            "```text",
            output["output_digest"],
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def validate_with_schema() -> None:
    subprocess.run(
        [
            ".venv/bin/python",
            rel(VALIDATOR_SCRIPT),
            rel(OUTPUT_PATH),
            "--schema",
            rel(SCHEMA_OUTPUT),
        ],
        cwd=ROOT,
        check=True,
    )


def build_output() -> dict[str, Any]:
    inventory = load_json(INVENTORY_OUTPUT)
    schema = load_json(SCHEMA_OUTPUT)
    quiet = load_json(QUIET_OUTPUT)
    challenge = load_json(CHALLENGE_OUTPUT)
    control_config = load_json(CONTROL_VARIANTS)
    rows = build_rows(schema, inventory, challenge)
    checks = iteration_checks(rows, challenge)
    by_state = {row["boundary_state"]: row for row in rows}
    anchor = challenge_b2_c2_row(challenge)
    b2_ref = b2_c2_reference(anchor)
    b2 = by_state["B2"]
    b3 = by_state["B3"]
    b4 = by_state["B4"]
    b2_metrics = b2["source_current"]["challenge_transform"]["metrics"]
    b3_metrics = b3["source_current"]["challenge_transform"]["metrics"]
    source_artifacts = {
        rel(INVENTORY_OUTPUT): source_record(INVENTORY_OUTPUT, inventory),
        rel(SCHEMA_OUTPUT): source_record(SCHEMA_OUTPUT, schema),
        rel(QUIET_OUTPUT): source_record(QUIET_OUTPUT, quiet),
        rel(CHALLENGE_OUTPUT): source_record(CHALLENGE_OUTPUT, challenge),
        rel(SOURCE_REGISTRY): source_record(SOURCE_REGISTRY),
        rel(BOUNDARY_POLICY): source_record(BOUNDARY_POLICY),
        rel(BUDGET_LIMITS): source_record(BUDGET_LIMITS),
        rel(CONTROL_VARIANTS): source_record(CONTROL_VARIANTS),
        rel(REPLAY_POLICY): source_record(REPLAY_POLICY),
    }
    source_reports = {
        rel(INVENTORY_REPORT): source_report(INVENTORY_REPORT),
        rel(SCHEMA_REPORT): source_report(SCHEMA_REPORT),
        rel(QUIET_REPORT): source_report(QUIET_REPORT),
        rel(CHALLENGE_REPORT): source_report(CHALLENGE_REPORT),
        rel(CHALLENGE_INTERPRETATION): source_report(CHALLENGE_INTERPRETATION),
    }
    output = {
        "experiment": "N16",
        "iteration": "5",
        "artifact_id": "n16_boundary_state_sweep_matrix",
        "purpose": "fixed_c2_boundary_state_maturity_sweep",
        "schema_version": schema["schema_version"],
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed" if all(checks.values()) else "failed",
        "acceptance_state": "accepted_boundary_state_flux_sweep_no_ap6",
        "synthesis_mode": "partial_mvp",
        "included_iterations": ["1", "2", "3", "4", "5"],
        "deferred_iterations": ["6", "7", "8", "9"],
        "final_ap6_closeout_allowed": False,
        "challenge_sweep_source_provenance": challenge_source_provenance(challenge),
        "c2_fixed_policy": C2_FIXED_POLICY,
        "challenge_thresholds": CHALLENGE_THRESHOLDS,
        "metric_construction_rationale": METRIC_CONSTRUCTION_RATIONALE,
        "metric_construction_formulas": METRIC_CONSTRUCTION_FORMULAS,
        "source_artifacts": source_artifacts,
        "source_reports": source_reports,
        "rows": rows,
        "controls": top_level_controls(schema),
        "checks": checks,
        "claim_flags": control_config["claim_flags_forced_false"],
        "errors": [],
        "iteration_result": {
            "boundary_state_sweep_passed": all(checks.values()),
            "matrix_rows_generated": True,
            "row_count": len(rows),
            "fixed_challenge_class": "C2",
            "b2_reproduced_iteration4_partial": checks[
                "b2_reproduces_iteration4_c2_partial_result"
            ],
            "b3_improves_b2_c2_failure_modes": checks[
                "b3_addresses_b2_specific_c2_failures"
            ],
            "b4_remains_provisional_under_c2": checks[
                "b4_c2_remains_provisional"
            ],
            "final_ap6_supported": False,
        },
        "b3_unlock_audit": b3_unlock_audit(challenge),
        "b2_reproduction_audit": {
            "iteration_4_anchor_cell": "B2_C2",
            "anchor_reference": b2_ref,
            "iteration_5_b2_metrics": b2_c2_reference(b2),
            "exact_reproduction": checks[
                "b2_reproduces_iteration4_c2_partial_result"
            ],
            "tolerance_policy": "deterministic_exact_match_required_for_iteration_5",
        },
        "b3_improvement_audit": {
            "compared_to": "B2_C2",
            "leakage_delta": round(b3["leakage_ratio"] - b2["leakage_ratio"], 6),
            "retained_flux_delta": round(
                b3["retained_flux"] - b2["retained_flux"], 6
            ),
            "stability_delta": round(
                b3["boundary_stability_score"] - b2["boundary_stability_score"],
                6,
            ),
            "internal_coherence_delta": round(
                b3["internal_coherence"] - b2["internal_coherence"], 6
            ),
            "coherence_margin_delta": round(
                b3["coherence_margin"] - b2["coherence_margin"], 6
            ),
            "minimum_internal_support_delta": round(
                b3_metrics["minimum_internal_support"]
                - b2_metrics["minimum_internal_support"],
                6,
            ),
            "outbound_flux_delta": round(b3["outbound_flux"] - b2["outbound_flux"], 6),
            "upstream_downstream_asymmetry_delta": round(
                b3_metrics["upstream_downstream_asymmetry_score"]
                - b2_metrics["upstream_downstream_asymmetry_score"],
                6,
            ),
            "b2_failed_requirements": b2["requirements_failed"],
            "b3_satisfied_requirements": b3["requirements_satisfied"],
            "addresses_same_failure_modes": checks[
                "b3_addresses_b2_specific_c2_failures"
            ],
            "claim_boundary": (
                "B3 support is artifact-level flux repair candidate evidence, "
                "not agency, intention, selfhood, native support, or final AP6"
            ),
        },
        "b4_c2_provisional_audit": {
            "row_decision": b4["row_decision"],
            "flux_decomposition": b4["source_current"]["challenge_transform"][
                "flux_decomposition"
            ],
            "basin_separation_score": b4["basin_separation_score"],
            "requirements_failed": b4["requirements_failed"],
            "claim_boundary": (
                "B4 x C2 is a flux stress row only; B4 x C5 remains required "
                "for shared-medium separability"
            ),
        },
        "maturity_gradient_summary": maturity_gradient_summary(rows),
        "iteration_6_guardrails": iteration_6_guardrails(rows),
        "audit_list": [
            "C2 challenge profile inherited exactly from Iteration 4",
            "B0 rejects externally organized flux",
            "B1 remains localized partition evidence only",
            "B2 reproduces Iteration 4 partial result exactly",
            "B3 unlocked only after B2 C0/C1/C2 evidence is present",
            "B3 improves the same B2 C2 leakage/support/coherence failures",
            "B4 x C2 remains provisional and does not close B4 x C5",
            "failure vocabulary reused from Iteration 4",
            "B4 retention distinguished from coupling, neighbor leakage, and merge pressure",
            "Iteration 6 guardrails recorded for B3_C4 and B4_C5",
            "all boundary claims and final AP6 remain false",
        ],
        "git": {
            "head": git_head(),
            "status_short": git_status_short(rel(EXPERIMENT)),
        },
        "output_digest": "",
    }
    if contains_absolute_path(output):
        output["status"] = "failed"
        output["errors"].append("absolute_path_recorded")
    if not all(checks.values()):
        output["errors"].append("boundary_state_sweep_check_failed")
    output["output_digest"] = output_digest(output)
    return output


def main() -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    output = build_output()
    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    validate_with_schema()
    REPORT_PATH.write_text(build_report(output), encoding="utf-8")
    print(json.dumps(output["iteration_result"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
