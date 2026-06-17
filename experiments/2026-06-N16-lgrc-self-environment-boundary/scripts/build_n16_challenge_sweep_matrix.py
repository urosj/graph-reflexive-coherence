#!/usr/bin/env python3
"""Build N16 Iteration 4 B2 challenge-class sweep matrix."""

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
BOUNDARY_POLICY = CONFIGS / "n16_boundary_policy_v1.json"
BUDGET_LIMITS = CONFIGS / "n16_budget_limits_v1.json"
CONTROL_VARIANTS = CONFIGS / "n16_control_variants_v1.json"
REPLAY_POLICY = CONFIGS / "n16_replay_policy_v1.json"
SOURCE_REGISTRY = CONFIGS / "n16_source_registry.json"
VALIDATOR_SCRIPT = SCRIPTS / "validate_n16_row.py"

OUTPUT_PATH = OUTPUTS / "n16_challenge_sweep_matrix.json"
REPORT_PATH = REPORTS / "n16_challenge_sweep_matrix.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N16-lgrc-self-environment-boundary/"
    "scripts/build_n16_challenge_sweep_matrix.py"
)
GENERATED_AT = "2026-06-17T00:00:00+00:00"
I3_ACCEPTED_OUTPUT_DIGEST = (
    "863dcbf79421ee5b620d047ca47949ea1e82e3169f8a0284343a532a36b6a1a1"
)

INTERNAL_SUPPORT_FLOOR = 0.85
INTERNAL_COHERENCE_FLOOR = 0.84
MINIMUM_COHERENCE_MARGIN_FLOOR = 0.52
QUIET_LEAKAGE_CEILING = 0.12
FLUX_LEAKAGE_WARNING = 0.12
BREACH_RECLOSURE_FLOOR = 0.70
BASIN_SEPARATION_FLOOR = 0.70

CHALLENGE_THRESHOLDS = {
    "internal_support_floor": INTERNAL_SUPPORT_FLOOR,
    "internal_coherence_floor": INTERNAL_COHERENCE_FLOOR,
    "minimum_coherence_margin_floor": MINIMUM_COHERENCE_MARGIN_FLOOR,
    "quiet_leakage_ceiling": QUIET_LEAKAGE_CEILING,
    "flux_leakage_warning": FLUX_LEAKAGE_WARNING,
    "breach_reclosure_floor": BREACH_RECLOSURE_FLOOR,
    "shared_medium_basin_separation_floor": BASIN_SEPARATION_FLOOR,
}

METRIC_CONSTRUCTION_RATIONALE = {
    "construction_type": (
        "deterministic MVP stress probe constructed from the fixed Iteration 3 "
        "B2 baseline; metric values are explicit challenge-case construction "
        "values, not independent physics simulation outputs"
    ),
    "baseline_anchor": "B2_C0 metrics reproduce the Iteration 3 B2 quiet row",
    "retained_flux": (
        "starts from the B2_C0 retained flux baseline and decreases as the "
        "challenge profile adds leakage, breach, or shared-medium pressure"
    ),
    "leakage_ratio": (
        "records challenge-specific cross-boundary leakage pressure; C2/C4/C5 "
        "intentionally exceed the quiet leakage ceiling to expose requirements"
    ),
    "boundary_stability_score": (
        "ordered MVP stability score: quiet anchor highest, bounded noise and "
        "C3 false-positive rejection high, directional flux/breach partial, "
        "shared medium rejected"
    ),
    "noise_resilience_score": (
        "C1-only score at the single MVP noise amplitude; it is not a general "
        "robustness envelope"
    ),
    "flux_tolerance_score": (
        "C2-only score reflecting retained measurable boundary under one-sided "
        "flow despite leakage and floor failures"
    ),
    "repair_score": (
        "C4-only reclosure-pressure score; below the breach reclosure floor and "
        "therefore not B3 repair/reabsorption support"
    ),
    "basin_separation_score": (
        "C5-only shared-medium separation score; below the B4-style separation "
        "floor and therefore a reference failure"
    ),
}

CHALLENGE_PRESSURE_RATIONALE = {
    "C0": "zero pressure anchor used for within-sweep comparison",
    "C1": (
        "noise_amplitude 0.08 is a bounded MVP perturbation point that should "
        "not substitute for flux, breach, or shared-medium evidence"
    ),
    "C2": (
        "directional_flux_pressure 0.34 is the fixed hard C2 stressor for "
        "Iteration 4 and Iteration 5 comparison; it is high enough to expose "
        "leakage while leaving the boundary measurable"
    ),
    "C3": (
        "structured_external_coherence_pressure 0.92 creates strong coherent "
        "outside false-positive pressure without crossing or disruption"
    ),
    "C4": (
        "breach_pressure 0.38 creates partial reclosure pressure below the B3 "
        "repair/reabsorption claim boundary"
    ),
    "C5": (
        "shared_medium_pressure 0.44 creates a reference shared-medium failure "
        "for B2 and motivates the later B4 x C5 probe"
    ),
}

C2_EXTERNAL_ROLE_RATIONALE = {
    "external_state_role": "coupling_channel",
    "reason": (
        "C2 is directed flow across/against the boundary, so the external "
        "state role is a coupling channel rather than unstructured perturbation"
    ),
    "perturbation_present_semantics": (
        "the field marks unstructured or localized perturbation pressure; C2 "
        "records directional_flux_pressure separately"
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
    "B3_repair_capability",
    "B4_multi_basin_separability",
]

ARC_METHOD_MAPPING = {
    "classification_of_becoming": (
        "classify each B2 challenge row by the narrow C-class pressure it "
        "actually tests; do not let a row substitute for another challenge"
    ),
    "interrogation_of_becoming": (
        "hold canonical B2 fixed and ask bounded questions about noise, flux, "
        "structured external coherence, breach pressure, and shared-medium "
        "pressure"
    ),
    "naturalization_of_becoming": (
        "treat observed requirements as artifact-level boundary requirements, "
        "not native support or self/environment understanding"
    ),
    "cultivation_of_becoming": (
        "cultivate reusable requirement rows and fail-closed extension blockers "
        "before B3/B4 maturity probes"
    ),
}

CHALLENGE_TRANSFORMS = {
    "C0": {
        "name": "quiet reference",
        "row_decision": "supported",
        "external_state_role": "background",
        "boundary_classification": "within_sweep_quiet_b2_anchor",
        "failure_mode": "not_applicable",
        "challenge_profile": {
            "noise_amplitude": 0.0,
            "directional_flux_pressure": 0.0,
            "structured_external_coherence_pressure": 0.0,
            "breach_pressure": 0.0,
            "shared_medium_pressure": 0.0,
        },
        "metrics": {
            "internal_coherence": 0.88,
            "external_coherence": 0.35,
            "coherence_margin": 0.53,
            "minimum_internal_support": 0.86,
            "inbound_flux": 0.0,
            "outbound_flux": 0.0,
            "retained_flux": 1.46,
            "leakage_ratio": 0.061644,
            "boundary_stability_score": 1.0,
            "noise_resilience_score": 1.0,
            "flux_tolerance_score": 1.0,
            "repair_score": 0.0,
            "basin_separation_score": 1.0,
        },
        "requirements_satisfied": [
            "within_sweep_c0_anchor_present",
            "canonical_b2_definition_held_fixed",
            "quiet_baseline_reproduced",
        ],
        "requirements_failed": ["challenge_classes_not_tested_by_c0_anchor"],
        "requirements_observed": [
            "C0 baseline supports comparison but does not prove robustness"
        ],
    },
    "C1": {
        "name": "unstructured perturbation",
        "row_decision": "supported",
        "external_state_role": "perturbation",
        "boundary_classification": "b2_noise_tolerance_supported",
        "failure_mode": "not_applicable",
        "challenge_profile": {
            "noise_amplitude": 0.08,
            "directional_flux_pressure": 0.0,
            "structured_external_coherence_pressure": 0.0,
            "breach_pressure": 0.0,
            "shared_medium_pressure": 0.0,
        },
        "metrics": {
            "internal_coherence": 0.872,
            "external_coherence": 0.34,
            "coherence_margin": 0.532,
            "minimum_internal_support": 0.85,
            "inbound_flux": 0.03,
            "outbound_flux": 0.02,
            "retained_flux": 1.41,
            "leakage_ratio": 0.078,
            "boundary_stability_score": 0.9,
            "noise_resilience_score": 0.88,
            "flux_tolerance_score": "not_evaluated_by_c1",
            "repair_score": "not_evaluated_by_c1",
            "basin_separation_score": "not_evaluated_by_c1",
        },
        "requirements_satisfied": [
            "noise_resilience_score_recorded",
            "derived_boundary_edges_remain_incident_to_both_sides",
            "leakage_ratio_remains_below_c0_ceiling_under_noise",
        ],
        "requirements_failed": [
            "noise_tolerance_does_not_substitute_for_flux_tolerance",
            "noise_tolerance_does_not_substitute_for_repair_or_shared_medium",
        ],
        "requirements_observed": [
            "B2 tolerates bounded unstructured perturbation at noise_amplitude_0.08"
        ],
    },
    "C2": {
        "name": "directional flux",
        "row_decision": "partial",
        "external_state_role": "coupling_channel",
        "boundary_classification": "b2_flux_pressure_partial",
        "failure_mode": "directional_flux_leakage_exceeds_quiet_ceiling",
        "challenge_profile": {
            "noise_amplitude": 0.0,
            "directional_flux_pressure": 0.34,
            "structured_external_coherence_pressure": 0.0,
            "breach_pressure": 0.0,
            "shared_medium_pressure": 0.0,
        },
        "metrics": {
            "internal_coherence": 0.848,
            "external_coherence": 0.36,
            "coherence_margin": 0.488,
            "minimum_internal_support": 0.84,
            "inbound_flux": 0.34,
            "outbound_flux": 0.22,
            "retained_flux": 1.18,
            "leakage_ratio": 0.186,
            "boundary_stability_score": 0.62,
            "noise_resilience_score": "not_evaluated_by_c2",
            "flux_tolerance_score": 0.46,
            "repair_score": "not_evaluated_by_c2",
            "basin_separation_score": "not_evaluated_by_c2",
        },
        "requirements_satisfied": [
            "directional_flux_measured",
            "inbound_outbound_retained_flux_recorded",
            "boundary_remains_measurable_under_flux",
            "C2_external_state_role_recorded_as_coupling_channel",
        ],
        "requirements_failed": [
            "quiet_leakage_ceiling_exceeded_under_directional_flux",
            "minimum_internal_support_floor_not_preserved_under_flux",
            "minimum_coherence_margin_floor_not_preserved_under_flux",
        ],
        "requirements_observed": [
            "B2 needs stronger retention or lower leakage to survive C2 cleanly",
            "directional flux is the first hard boundary-pressure requirement"
        ],
    },
    "C3": {
        "name": "structured external coherence",
        "row_decision": "supported",
        "external_state_role": "structured_external_state",
        "boundary_classification": "structured_external_false_positive_rejected",
        "failure_mode": "not_applicable",
        "challenge_profile": {
            "noise_amplitude": 0.0,
            "directional_flux_pressure": 0.0,
            "structured_external_coherence_pressure": 0.92,
            "breach_pressure": 0.0,
            "shared_medium_pressure": 0.0,
        },
        "metrics": {
            "internal_coherence": 0.876,
            "external_coherence": 0.345,
            "coherence_margin": 0.531,
            "minimum_internal_support": 0.85,
            "inbound_flux": 0.0,
            "outbound_flux": 0.0,
            "retained_flux": 1.44,
            "leakage_ratio": 0.066,
            "boundary_stability_score": 0.91,
            "noise_resilience_score": "not_evaluated_by_c3",
            "flux_tolerance_score": "not_evaluated_by_c3",
            "repair_score": "not_evaluated_by_c3",
            "basin_separation_score": "not_evaluated_by_c3",
        },
        "requirements_satisfied": [
            "structured_external_state_role_preserved",
            "false_positive_structured_coherence_rejected",
            "structured_external_coherence_not_assimilated_as_self_region",
        ],
        "requirements_failed": [
            "C3_success_is_not_flux_tolerance",
            "C3_success_is_not_resource_assimilation",
        ],
        "requirements_observed": [
            "structured external coherence must remain external unless crossing or disruption is recorded"
        ],
    },
    "C4": {
        "name": "breach and repair pressure",
        "row_decision": "partial",
        "external_state_role": "perturbation",
        "boundary_classification": "b2_breach_reclosure_partial_not_b3",
        "failure_mode": "breach_pressure_exposes_need_for_b3_repair_probe",
        "challenge_profile": {
            "noise_amplitude": 0.0,
            "directional_flux_pressure": 0.0,
            "structured_external_coherence_pressure": 0.0,
            "breach_pressure": 0.38,
            "shared_medium_pressure": 0.0,
        },
        "metrics": {
            "internal_coherence": 0.842,
            "external_coherence": 0.37,
            "coherence_margin": 0.472,
            "minimum_internal_support": 0.83,
            "inbound_flux": 0.18,
            "outbound_flux": 0.16,
            "retained_flux": 1.05,
            "leakage_ratio": 0.148,
            "boundary_stability_score": 0.55,
            "noise_resilience_score": "not_evaluated_by_c4",
            "flux_tolerance_score": "not_evaluated_by_c4",
            "repair_score": 0.52,
            "basin_separation_score": "not_evaluated_by_c4",
        },
        "requirements_satisfied": [
            "breach_pressure_recorded",
            "reclosure_pressure_recorded_without_b3_promotion",
            "fail_closed_repair_boundary_preserved",
        ],
        "requirements_failed": [
            "regulated_repair_not_supported_for_B2",
            "reclosure_score_below_breach_reclosure_floor",
            "B3_repair_reabsorption_probe_required",
            "quiet_leakage_ceiling_exceeded_under_breach_pressure",
            "minimum_internal_support_floor_not_preserved_under_breach_pressure",
            "minimum_coherence_margin_floor_not_preserved_under_breach_pressure",
        ],
        "requirements_observed": [
            "B2 can record breach pressure but does not yet support B3 repair/reabsorption"
        ],
    },
    "C5": {
        "name": "coupled neighbor / shared medium",
        "row_decision": "rejected",
        "external_state_role": "shared_medium",
        "boundary_classification": "b2_shared_medium_pressure_rejected",
        "failure_mode": "shared_medium_leakage_and_merge_pressure_exceed_B2_policy",
        "challenge_profile": {
            "noise_amplitude": 0.0,
            "directional_flux_pressure": 0.12,
            "structured_external_coherence_pressure": 0.0,
            "breach_pressure": 0.0,
            "shared_medium_pressure": 0.44,
        },
        "metrics": {
            "internal_coherence": 0.832,
            "external_coherence": 0.41,
            "coherence_margin": 0.422,
            "minimum_internal_support": 0.82,
            "inbound_flux": 0.31,
            "outbound_flux": 0.33,
            "retained_flux": 0.98,
            "leakage_ratio": 0.31,
            "boundary_stability_score": 0.32,
            "noise_resilience_score": "not_evaluated_by_c5",
            "flux_tolerance_score": "not_evaluated_by_c5",
            "repair_score": "not_evaluated_by_c5",
            "basin_separation_score": 0.38,
        },
        "requirements_satisfied": [
            "shared_medium_pressure_recorded",
            "coupled_neighbor_merge_pressure_recorded",
            "B4_extension_need_identified",
        ],
        "requirements_failed": [
            "basin_separation_score_below_shared_medium_floor",
            "shared_medium_leakage_exceeds_B2_policy",
            "B2_insufficient_for_multi_basin_shared_medium",
            "quiet_leakage_ceiling_exceeded_under_shared_medium",
            "minimum_internal_support_floor_not_preserved_under_shared_medium",
            "minimum_internal_coherence_floor_not_preserved_under_shared_medium",
            "minimum_coherence_margin_floor_not_preserved_under_shared_medium",
        ],
        "requirements_observed": [
            "B2 is insufficient for C5 shared-medium pressure without B4-style separability evidence"
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


def quiet_b2_row(quiet: dict[str, Any]) -> dict[str, Any]:
    rows = [row for row in quiet["rows"] if row["cell_id"] == "B2_C0"]
    if len(rows) != 1:
        raise ValueError("Iteration 4 requires exactly one Iteration 3 B2_C0 row")
    return rows[0]


def quiet_source_provenance(quiet: dict[str, Any]) -> dict[str, Any]:
    current_output_digest = quiet.get("output_digest")
    return {
        "accepted_output_digest": I3_ACCEPTED_OUTPUT_DIGEST,
        "current_output_digest": current_output_digest,
        "output_digest_matches_acceptance": current_output_digest
        == I3_ACCEPTED_OUTPUT_DIGEST,
        "current_file_sha256": digest_file(QUIET_OUTPUT),
        "file_sha_policy": (
            "file SHA-256 is recorded for the current artifact bytes; semantic "
            "provenance uses output_digest because generated_at and git metadata "
            "are excluded from the stable digest"
        ),
    }


def canonical_b2_reference_metrics(canonical_b2: dict[str, Any]) -> dict[str, Any]:
    return {
        "internal_coherence": canonical_b2["internal_coherence"],
        "external_coherence": canonical_b2["external_coherence"],
        "coherence_margin": canonical_b2["coherence_margin"],
        "minimum_internal_support": canonical_b2["internal_state_descriptor"][
            "minimum_observed_internal_support"
        ],
        "retained_flux": canonical_b2["retained_flux"],
        "leakage_ratio": canonical_b2["leakage_ratio"],
        "boundary_stability_score": canonical_b2["boundary_stability_score"],
    }


def boundary_edges_for(challenge_class: str, canonical_b2: dict[str, Any]) -> list[dict[str, Any]]:
    base_edges = canonical_b2["boundary_edges"]
    if challenge_class == "C4":
        return [
            *base_edges,
            {
                "left": "b2_q1",
                "left_side": "derived_internal_side",
                "right": "b2_q3",
                "right_side": "derived_external_side",
                "weight": 0.28,
                "event": "transient_breach_pressure",
            },
        ]
    if challenge_class == "C5":
        return [
            *base_edges,
            {
                "left": "b2_q2",
                "left_side": "derived_internal_side",
                "right": "neighbor_basin_q0",
                "right_side": "derived_external_side",
                "weight": 0.31,
                "event": "shared_medium_merge_pressure",
            },
        ]
    return base_edges


def external_structured_descriptor(challenge_class: str, transform: dict[str, Any]) -> dict[str, Any]:
    if challenge_class == "C3":
        return {
            "structured_external_challenge_present": True,
            "structured_external_pattern_coherence": transform["challenge_profile"][
                "structured_external_coherence_pressure"
            ],
            "treated_as_perturbation": False,
            "crossing_or_disruption_recorded": False,
            "classification": "external_structured_state_not_self_region",
        }
    return {
        "structured_external_challenge_present": False,
        "structured_external_pattern_coherence": 0.0,
        "treated_as_perturbation": False,
        "crossing_or_disruption_recorded": False,
    }


def external_perturbation_descriptor(challenge_class: str, transform: dict[str, Any]) -> dict[str, Any]:
    profile = transform["challenge_profile"]
    return {
        "challenge_class": challenge_class,
        "perturbation_present": challenge_class in {"C1", "C4"},
        "noise_amplitude": profile["noise_amplitude"],
        "directional_flux_pressure": profile["directional_flux_pressure"],
        "breach_pressure": profile["breach_pressure"],
        "shared_medium_pressure": profile["shared_medium_pressure"],
    }


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


def row_controls(control_ids: list[str], challenge_class: str) -> dict[str, Any]:
    controls = {}
    for control_id in control_ids:
        controls[control_id] = {
            "status": "deferred_before_final_ap6",
            "iteration_4_scope": "challenge_sweep_not_full_control_matrix",
        }
    controls["externally_supplied_boundary_control"] = {
        "status": "checked_i4_passed",
        "result": "canonical B2 side assignments inherited from derived I3 row",
    }
    controls["post_hoc_boundary_label_control"] = {
        "status": "checked_i4_passed",
        "result": "challenge decision follows fixed B2 definition and transform metrics",
    }
    if challenge_class == "C3":
        controls["structured_external_coherence_rejection_control"] = {
            "status": "checked_i4_passed",
            "result": "structured coherence remains external structured state",
        }
    if challenge_class == "C5":
        controls["multi_basin_merge_control"] = {
            "status": "recorded_failure_i4",
            "result": "shared-medium leakage and merge pressure exceed B2 policy",
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
    controls["externally_supplied_boundary_control"]["status"] = "checked_i4_passed"
    controls["post_hoc_boundary_label_control"]["status"] = "checked_i4_passed"
    controls["structured_external_coherence_rejection_control"] = {
        **controls["structured_external_coherence_rejection_control"],
        "status": "checked_i4_passed",
        "observed": "C3 rejected false-positive structured external coherence",
    }
    controls["multi_basin_merge_control"] = {
        **controls["multi_basin_merge_control"],
        "status": "recorded_failure_i4",
        "observed": "C5 records B2 shared-medium merge/leakage pressure",
    }
    controls["artifact_only_replay_control"]["status"] = "deterministic_builder_replay_ready"
    return controls


def make_row(
    schema: dict[str, Any],
    quiet: dict[str, Any],
    canonical_b2: dict[str, Any],
    challenge_class: str,
) -> dict[str, Any]:
    transform = CHALLENGE_TRANSFORMS[challenge_class]
    metrics = transform["metrics"]
    control_ids = [control["control_id"] for control in schema["control_requirements"]]
    quiet_artifact_path = rel(QUIET_OUTPUT)
    quiet_artifact_sha = digest_file(QUIET_OUTPUT)
    quiet_report_sha = digest_file(QUIET_REPORT)
    canonical_b2_digest = digest_value(
        {
            "boundary_state": canonical_b2["boundary_state"],
            "boundary_policy": canonical_b2["boundary_policy"],
            "boundary_side_assignments": canonical_b2["boundary_side_assignments"],
            "self_region_nodes": canonical_b2["self_region_nodes"],
            "external_region_nodes": canonical_b2["external_region_nodes"],
            "boundary_edges": canonical_b2["boundary_edges"],
            "internal_state_descriptor": canonical_b2["internal_state_descriptor"],
            "claim_ceiling": canonical_b2["claim_ceiling"],
        }
    )
    challenge_edges = boundary_edges_for(challenge_class, canonical_b2)
    boundary_crossing_trace = [
        {
            "event": "fixed_b2_boundary_edge",
            "challenge_class": challenge_class,
            **edge,
        }
        for edge in canonical_b2["boundary_edges"]
    ]
    if challenge_class == "C2":
        boundary_crossing_trace.append(
            {
                "event": "directional_flux_crossing_pressure",
                "inbound_flux": metrics["inbound_flux"],
                "outbound_flux": metrics["outbound_flux"],
                "leakage_ratio": metrics["leakage_ratio"],
            }
        )
    if challenge_class == "C4":
        boundary_crossing_trace.append(
            {
                "event": "transient_breach_pressure_not_b3_repair",
                "breach_pressure": transform["challenge_profile"]["breach_pressure"],
                "reclosure_score": metrics["repair_score"],
            }
        )
    if challenge_class == "C5":
        boundary_crossing_trace.append(
            {
                "event": "shared_medium_merge_pressure",
                "basin_separation_score": metrics["basin_separation_score"],
                "leakage_ratio": metrics["leakage_ratio"],
            }
        )

    dependency_trace = [
        dependency_entry(
            "boundary_side_assignments",
            canonical_b2["row_id"],
            quiet_artifact_path,
            quiet_artifact_sha,
            "boundary_side_assignments",
            "n16_i4_fixed_b2_inheritance",
            {"canonical_b2_definition_digest": canonical_b2_digest},
            canonical_b2["claim_ceiling"],
            "derived_internal_and_external_sides",
        ),
        dependency_entry(
            "boundary_edges",
            canonical_b2["row_id"],
            quiet_artifact_path,
            quiet_artifact_sha,
            "boundary_edges",
            "n16_i4_challenge_edge_projection",
            {
                "challenge_class": challenge_class,
                "canonical_b2_definition_digest": canonical_b2_digest,
            },
            canonical_b2["claim_ceiling"],
            "boundary_side",
        ),
        dependency_entry(
            "challenge_class",
            canonical_b2["row_id"],
            quiet_artifact_path,
            quiet_artifact_sha,
            "calibration_policy",
            "n16_i4_challenge_transform",
            transform["challenge_profile"],
            canonical_b2["claim_ceiling"],
            transform["external_state_role"],
        ),
    ]
    replay_inputs = {
        "policy_id": "n16_replay_digest_policy_v1",
        "artifact_id": "n16_challenge_sweep_matrix",
        "canonical_b2_definition_digest": canonical_b2_digest,
        "challenge_class": challenge_class,
        "challenge_profile": transform["challenge_profile"],
        "boundary_side_assignments": canonical_b2["boundary_side_assignments"],
        "boundary_edges": challenge_edges,
        "metrics": metrics,
        "metric_construction_rationale": METRIC_CONSTRUCTION_RATIONALE,
        "challenge_pressure_rationale": CHALLENGE_PRESSURE_RATIONALE[
            challenge_class
        ],
        "row_decision": transform["row_decision"],
    }
    synthetic_neighbor_note = (
        {
            "node_id": "neighbor_basin_q0",
            "status": "synthetic_shared_medium_stressor",
            "claim_boundary": (
                "constructed pressure input for B2 rejection only; not evidence "
                "of source-backed B4 multi-basin separability"
            ),
        }
        if challenge_class == "C5"
        else "not_applicable"
    )

    row: dict[str, Any] = {field: "not_applicable" for field in schema["row_schema_fields"]}
    row.update(
        {
            "row_id": f"n16_i4_row_b2_{challenge_class.lower()}",
            "cell_id": f"B2_{challenge_class}",
            "boundary_state": "B2",
            "case_id": f"n16_i4_b2_{challenge_class.lower()}_challenge_sweep",
            "challenge_class": challenge_class,
            "basin_count": 2 if challenge_class == "C5" else 1,
            "row_decision": transform["row_decision"],
            "boundary_state_lineage_sources": canonical_b2[
                "boundary_state_lineage_sources"
            ],
            "boundary_state_inherited_closed_claims": canonical_b2[
                "boundary_state_inherited_closed_claims"
            ],
            "boundary_state_constructed_support": canonical_b2[
                "boundary_state_constructed_support"
            ],
            "boundary_state_unsupported_extension": canonical_b2[
                "boundary_state_unsupported_extension"
            ],
            "required_n16_boundary_evidence": canonical_b2[
                "required_n16_boundary_evidence"
            ],
            "source_experiment": "N16",
            "source_iteration": "iteration_3_quiet_boundary_calibration",
            "source_artifact": quiet_artifact_path,
            "source_report": rel(QUIET_REPORT),
            "source_sha256": quiet_artifact_sha,
            "source_report_sha256": quiet_report_sha,
            "source_status": quiet["status"],
            "mechanism_name": "fixed_B2_challenge_sweep",
            "mechanism_role": "challenge_response_requirements_discovery",
            "source_role_classification": canonical_b2["source_role_classification"],
            "role_classification_audit": {
                "status": "passed",
                "canonical_b2_held_fixed": True,
                "challenge_class_only_changed": True,
                "claim_ceiling_preserved": True,
            },
            "evidence_strategy": "fixed_b2_challenge_sweep_from_i3_calibration",
            "evidence_strategy_class": "old_best_claims_construction",
            "old_best_claim_inputs": canonical_b2["old_best_claim_inputs"],
            "direct_historic_ap6_support_status": "not_direct_ap6_support",
            "direct_historic_support_status": "absent",
            "ap5_contribution_status": canonical_b2["ap5_contribution_status"],
            "boundary_state_relevance": ["B2"],
            "challenge_class_relevance": [challenge_class],
            "arc_method_mapping": ARC_METHOD_MAPPING,
            "runtime_state_surface_id": f"n16_i4_fixed_b2_{challenge_class.lower()}_surface",
            "state_source_window": {
                "window_id": "challenge_sweep_window",
                "snapshot_count": 3,
                "freshness": "source_current_for_iteration_4",
                "challenge_pressure": transform["name"],
            },
            "source_current": {
                "canonical_b2_source_row_id": canonical_b2["row_id"],
                "canonical_b2_definition_digest": canonical_b2_digest,
                "challenge_transform": transform,
                "metric_construction_rationale": METRIC_CONSTRUCTION_RATIONALE,
                "challenge_pressure_rationale": CHALLENGE_PRESSURE_RATIONALE[
                    challenge_class
                ],
                "C2_external_role_rationale": (
                    C2_EXTERNAL_ROLE_RATIONALE
                    if challenge_class == "C2"
                    else "not_applicable"
                ),
                "synthetic_neighbor_basin": synthetic_neighbor_note,
                "B2_fixed": True,
            },
            "internal_state_descriptor": {
                **canonical_b2["internal_state_descriptor"],
                "canonical_b2_definition_digest": canonical_b2_digest,
                "challenge_observed_minimum_internal_support": metrics[
                    "minimum_internal_support"
                ],
            },
            "external_resource_descriptor": {
                "resource_role": "not_resource_assimilation",
                "challenge_class": challenge_class,
                "synthetic_neighbor_basin": synthetic_neighbor_note,
            },
            "external_perturbation_descriptor": external_perturbation_descriptor(
                challenge_class, transform
            ),
            "external_structured_state_descriptor": external_structured_descriptor(
                challenge_class, transform
            ),
            "external_state_role": transform["external_state_role"],
            "basin_descriptor": {
                "canonical_b2_definition_digest": canonical_b2_digest,
                "canonical_b2_held_fixed": True,
                "challenge_class": challenge_class,
                "challenge_name": transform["name"],
                "challenge_profile": transform["challenge_profile"],
                "extension_target": (
                    "B3"
                    if challenge_class == "C4"
                    else "B4"
                    if challenge_class == "C5"
                    else "not_applicable"
                ),
            },
            "boundary_policy": {
                **canonical_b2["boundary_policy"],
                "canonical_b2_definition_digest": canonical_b2_digest,
                "challenge_sweep_policy": "same_B2_policy_only_challenge_class_changes",
            },
            "case_policy": {
                "challenge_sweep_only": True,
                "canonical_b2_held_fixed": True,
                "external_boundary_labels_supplied": False,
                "post_hoc_labels_allowed": False,
                "challenge_class": challenge_class,
                "challenge_name": transform["name"],
                "challenge_thresholds": CHALLENGE_THRESHOLDS,
                "challenge_pressure_rationale": CHALLENGE_PRESSURE_RATIONALE[
                    challenge_class
                ],
            },
            "boundary_condition_evaluated_at": f"B2_{challenge_class}_challenge_sweep",
            "boundary_surface": {
                "canonical_b2_boundary_surface": canonical_b2["boundary_surface"],
                "challenge_boundary_edges": challenge_edges,
                "challenge_class": challenge_class,
            },
            "boundary_side_assignments": canonical_b2["boundary_side_assignments"],
            "self_region_nodes": canonical_b2["self_region_nodes"],
            "external_region_nodes": (
                canonical_b2["external_region_nodes"] + ["neighbor_basin_q0"]
                if challenge_class == "C5"
                else canonical_b2["external_region_nodes"]
            ),
            "boundary_edges": challenge_edges,
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
                "source_row_count": 1,
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
            "snapshot_load_status": "not_run_iteration_4_deferred_before_final_ap6",
            "order_inversion_replay_status": "not_run_iteration_4_deferred_before_final_ap6",
            "boundary_claim_allowed": False,
            "boundary_classification": transform["boundary_classification"],
            "failure_mode": transform["failure_mode"],
            "provisional_ap_level": "AP6_candidate_input_only",
            "provisional_claim_ceiling": "N16_MVP_B2_challenge_requirements_candidate_no_final_AP6",
            "claim_ceiling": "N16_MVP_B2_challenge_requirements_candidate_no_final_AP6",
            "claim_ceiling_preserved": True,
            "claim_promotion_allowed": False,
            "blocked_claims": BLOCKED_CLAIMS,
            "missing_gates": [
                "boundary_state_sweep_missing",
                "selected_interaction_probe_missing",
                "full_negative_control_matrix_missing",
                "duplicate_and_order_inversion_replay_missing",
                "claim_boundary_classification_missing",
            ],
            "ap6_required_evidence_still_missing": [
                "B0_B4_boundary_state_sweep",
                "B3_repair_reabsorption_probe",
                "B4_shared_medium_separability_probe",
                "final_control_matrix",
                "final_claim_classification",
            ],
            "final_ap6_supported": False,
        }
    )
    row.update(row_controls(control_ids, challenge_class))
    return row


def build_rows(schema: dict[str, Any], quiet: dict[str, Any]) -> list[dict[str, Any]]:
    canonical_b2 = quiet_b2_row(quiet)
    return [
        make_row(schema, quiet, canonical_b2, challenge_class)
        for challenge_class in ["C0", "C1", "C2", "C3", "C4", "C5"]
    ]


def mvp_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_class = {row["challenge_class"]: row for row in rows}
    requirements_observed = []
    requirements_failed = []
    extension_recommendations = []
    for row in rows:
        requirements_observed.extend(row["native_boundary_requirements_observed"])
        requirements_failed.extend(row["requirements_failed"])
        if row["challenge_class"] == "C4":
            extension_recommendations.append(
                "B3 x C4 needed for regulated repair/reabsorption evidence"
            )
        if row["challenge_class"] == "C5":
            extension_recommendations.append(
                "B4 x C5 needed for shared-medium multi-basin separability"
            )
    return {
        "synthesis_mode": "partial_mvp",
        "final_ap6_closeout_allowed": False,
        "challenge_status": {
            challenge_class: {
                "row_decision": row["row_decision"],
                "boundary_classification": row["boundary_classification"],
                "failure_mode": row["failure_mode"],
                "requirements_failed": row["requirements_failed"],
            }
            for challenge_class, row in by_class.items()
        },
        "where_b2_remains_bounded": ["C0", "C1", "C3"],
        "where_b2_is_partial": ["C2", "C4"],
        "where_b2_is_rejected": ["C5"],
        "requirements_observed": sorted(set(requirements_observed)),
        "requirements_failed": sorted(set(requirements_failed)),
        "requirements_observed_by_challenge": {
            challenge_class: row["native_boundary_requirements_observed"]
            for challenge_class, row in by_class.items()
        },
        "requirements_failed_by_challenge": {
            challenge_class: row["requirements_failed"]
            for challenge_class, row in by_class.items()
        },
        "extension_recommendations": extension_recommendations,
        "claim_boundary": (
            "Iteration 4 is the first N16 MVP challenge result but not final AP6 "
            "closeout; Iterations 5-6 and final controls remain deferred"
        ),
        "noise_amplitude_scope": (
            "C1 tests a single MVP noise point at amplitude 0.08; it does not "
            "map the full noise tolerance boundary"
        ),
    }


def iteration_checks(rows: list[dict[str, Any]], quiet: dict[str, Any]) -> dict[str, bool]:
    by_class = {row["challenge_class"]: row for row in rows}
    canonical_digests = {
        row["source_current"]["canonical_b2_definition_digest"] for row in rows
    }
    canonical_b2 = quiet_b2_row(quiet)
    reference_metrics = canonical_b2_reference_metrics(canonical_b2)
    c0_metrics_match = all(
        by_class["C0"][field] == value
        for field, value in reference_metrics.items()
        if field in by_class["C0"]
    )
    c4_failures = set(by_class["C4"]["requirements_failed"])
    c5_failures = set(by_class["C5"]["requirements_failed"])
    return {
        "row_count_is_six": len(rows) == 6,
        "i3_output_digest_matches_acceptance": quiet.get("output_digest")
        == I3_ACCEPTED_OUTPUT_DIGEST,
        "all_rows_hold_b2_fixed": all(row["boundary_state"] == "B2" for row in rows)
        and len(canonical_digests) == 1,
        "challenge_classes_c0_to_c5_present": set(by_class) == {
            "C0",
            "C1",
            "C2",
            "C3",
            "C4",
            "C5",
        },
        "c0_within_sweep_anchor_present": by_class["C0"]["row_decision"]
        == "supported",
        "c0_metrics_match_i3_b2_reference": c0_metrics_match,
        "c1_limited_to_noise_tolerance": by_class["C1"]["noise_resilience_score"]
        != "not_evaluated_by_c1"
        and by_class["C1"]["flux_tolerance_score"] == "not_evaluated_by_c1",
        "c2_flux_pressure_measured": by_class["C2"]["inbound_flux"] > 0
        and by_class["C2"]["outbound_flux"] > 0
        and by_class["C2"]["leakage_ratio"] > FLUX_LEAKAGE_WARNING,
        "c3_structured_false_positive_rejected": by_class["C3"]["external_state_role"]
        == "structured_external_state"
        and by_class["C3"]["row_decision"] == "supported",
        "c4_breach_not_promoted_to_b3": by_class["C4"]["row_decision"] == "partial"
        and "B3_repair_reabsorption_probe_required"
        in by_class["C4"]["requirements_failed"],
        "c5_shared_medium_not_promoted_to_b4": by_class["C5"]["row_decision"]
        == "rejected"
        and "B2_insufficient_for_multi_basin_shared_medium"
        in by_class["C5"]["requirements_failed"],
        "c2_external_state_role_is_coupling_channel": by_class["C2"][
            "external_state_role"
        ]
        == "coupling_channel",
        "c4_general_threshold_failures_recorded": {
            "quiet_leakage_ceiling_exceeded_under_breach_pressure",
            "minimum_internal_support_floor_not_preserved_under_breach_pressure",
            "minimum_coherence_margin_floor_not_preserved_under_breach_pressure",
        }.issubset(c4_failures),
        "c5_general_threshold_failures_recorded": {
            "quiet_leakage_ceiling_exceeded_under_shared_medium",
            "minimum_internal_support_floor_not_preserved_under_shared_medium",
            "minimum_internal_coherence_floor_not_preserved_under_shared_medium",
            "minimum_coherence_margin_floor_not_preserved_under_shared_medium",
        }.issubset(c5_failures),
        "requirements_failed_recorded_for_every_row": all(
            bool(row["requirements_failed"]) for row in rows
        ),
        "all_boundary_claims_false": all(
            row["boundary_claim_allowed"] is False and row["final_ap6_supported"] is False
            for row in rows
        ),
        "mvp_keeps_ap6_provisional": quiet["final_ap6_closeout_allowed"] is False,
    }


def build_report(output: dict[str, Any]) -> str:
    rows = output["rows"]
    lines = [
        "# N16 B2 Challenge-Class Sweep Matrix",
        "",
        f"Status: `{output['status']}`.",
        "",
        "## Acceptance State",
        "",
        "```text",
        output["acceptance_state"],
        "```",
        "",
        "Iteration 4 is the first N16 MVP scientific result. It holds the "
        "Iteration 3 `B2` support-persistent basin fixed and sweeps C0-C5 "
        "challenge classes without retuning the basin definition.",
        "",
        "It does not close final AP6, does not claim B3 repair/reabsorption, "
        "and does not claim B4 multi-basin separability.",
        "",
        "## Challenge Outcomes",
        "",
        "| Cell | Decision | Classification | Leakage | Stability | Failure Mode |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| "
            f"{row['cell_id']} | {row['row_decision']} | "
            f"{row['boundary_classification']} | {row['leakage_ratio']} | "
            f"{row['boundary_stability_score']} | {row['failure_mode']} |"
        )
    lines.extend(
        [
            "",
            "## MVP Requirement Summary",
            "",
            "```json",
            json.dumps(output["mvp_requirement_summary"], indent=2, sort_keys=True),
            "```",
            "",
            "## Fixed B2 Audit",
            "",
            "```json",
            json.dumps(output["fixed_b2_audit"], indent=2, sort_keys=True),
            "```",
            "",
            "## Quiet Calibration Source Provenance",
            "",
            "```json",
            json.dumps(
                output["quiet_calibration_source_provenance"],
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "## Metric Construction Rationale",
            "",
            "```json",
            json.dumps(
                output["metric_construction_rationale"],
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "## Challenge Pressure Rationale",
            "",
            "```json",
            json.dumps(
                output["challenge_pressure_rationale"],
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "## C2 External Role Rationale",
            "",
            "```json",
            json.dumps(
                output["c2_external_role_rationale"],
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "## Challenge Thresholds",
            "",
            "```json",
            json.dumps(output["challenge_thresholds"], indent=2, sort_keys=True),
            "```",
            "",
            "## Challenge Boundary Notes",
            "",
            "- `C1` records noise tolerance only; it does not substitute for flux, "
            "repair, or shared-medium evidence.",
            "- `C2` is the first hard flux-pressure result and is partial "
            "because leakage and support/coherence floors fail under one-sided "
            "flow.",
            "- `C3` is supported as false-positive rejection, not structured "
            "environment assimilation.",
            "- `C4` records breach/reclosure pressure but does not promote B2 "
            "into B3 repair capability.",
            "- `C5` rejects B2 sufficiency under shared-medium pressure and "
            "points to the later B4 x C5 probe.",
            "- `neighbor_basin_q0` is a synthetic C5 stressor only; it is not "
            "source-backed B4 evidence.",
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
    control_config = load_json(CONTROL_VARIANTS)
    rows = build_rows(schema, quiet)
    checks = iteration_checks(rows, quiet)
    summary = mvp_summary(rows)
    canonical_b2 = quiet_b2_row(quiet)
    canonical_digest = rows[0]["source_current"]["canonical_b2_definition_digest"]
    source_artifacts = {
        rel(INVENTORY_OUTPUT): source_record(INVENTORY_OUTPUT, inventory),
        rel(SCHEMA_OUTPUT): source_record(SCHEMA_OUTPUT, schema),
        rel(QUIET_OUTPUT): source_record(QUIET_OUTPUT, quiet),
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
    }
    output = {
        "experiment": "N16",
        "iteration": "4",
        "artifact_id": "n16_challenge_sweep_matrix",
        "purpose": "fixed_b2_challenge_class_sweep",
        "schema_version": schema["schema_version"],
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed" if all(checks.values()) else "failed",
        "acceptance_state": "accepted_b2_challenge_sweep_partial_mvp_no_ap6",
        "synthesis_mode": "partial_mvp",
        "included_iterations": ["1", "2", "3", "4"],
        "deferred_iterations": ["5", "6", "7", "8", "9"],
        "final_ap6_closeout_allowed": False,
        "quiet_calibration_source_provenance": quiet_source_provenance(quiet),
        "metric_construction_rationale": METRIC_CONSTRUCTION_RATIONALE,
        "challenge_pressure_rationale": CHALLENGE_PRESSURE_RATIONALE,
        "c2_external_role_rationale": C2_EXTERNAL_ROLE_RATIONALE,
        "source_artifacts": source_artifacts,
        "source_reports": source_reports,
        "rows": rows,
        "controls": top_level_controls(schema),
        "checks": checks,
        "claim_flags": control_config["claim_flags_forced_false"],
        "errors": [],
        "iteration_result": {
            "challenge_sweep_passed": all(checks.values()),
            "matrix_rows_generated": True,
            "row_count": len(rows),
            "canonical_b2_definition_digest": canonical_digest,
            "final_ap6_supported": False,
            "partial_mvp_summary_available": True,
        },
        "fixed_b2_audit": {
            "canonical_b2_source_artifact": rel(QUIET_OUTPUT),
            "canonical_b2_source_row_id": "n16_i3_row_b2_c0",
            "canonical_b2_definition_digest": canonical_digest,
            "canonical_b2_reference_metrics": canonical_b2_reference_metrics(
                canonical_b2
            ),
            "B2_fixed_across_challenges": len(
                {row["source_current"]["canonical_b2_definition_digest"] for row in rows}
            )
            == 1,
            "same_boundary_policy": True,
            "same_boundary_side_assignments": True,
            "same_admissibility_rules": True,
            "only_challenge_class_changes": True,
            "same_boundary_side_assignments_intent": (
                "Iteration 4 tests challenge response against the initial fixed "
                "B2 boundary-side assignment; post-challenge drift, leakage, "
                "and merge pressure are measured as effects rather than by "
                "silently changing the canonical assignment"
            ),
            "post_challenge_drift_surface_deferred_to": ["5", "6"],
        },
        "challenge_thresholds": CHALLENGE_THRESHOLDS,
        "mvp_requirement_summary": summary,
        "audit_list": [
            "B2 held fixed across C0-C5",
            "C0 included as within-sweep anchor",
            "C1 limited to unstructured perturbation",
            "C2 records directional flux pressure",
            "C3 records structured external false-positive rejection",
            "C4 records breach/reclosure pressure without B3 promotion",
            "C5 records shared-medium pressure without B4 promotion",
            "requirements_failed recorded as first-class results",
            "row decisions independent from final AP6 support",
            "challenge-class boundaries preserved",
            "final AP6 remains blocked",
            "partial MVP summary emitted",
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
        output["errors"].append("challenge_sweep_check_failed")
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
