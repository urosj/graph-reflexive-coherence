#!/usr/bin/env python3
"""Validate N16 row-bearing artifacts against the Iteration 2 schema."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N16-lgrc-self-environment-boundary"
DEFAULT_SCHEMA = EXPERIMENT / "outputs" / "n16_boundary_schema_v1.json"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
LOCAL_PATH_MARKERS = (
    "/" + "home" + "/",
    "/" + "tmp" + "/",
    "/" + "Users" + "/",
    "geometric-" + "reflexive-coherence",
    "arc-" + "of-becoming",
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest_value(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return value


def output_digest(value: dict[str, Any]) -> str:
    excluded = {"generated_at", "output_digest", "git"}
    return digest_value({key: item for key, item in value.items() if key not in excluded})


def contains_absolute_path(value: Any) -> bool:
    if isinstance(value, str):
        return value.startswith(("/", "\\")) or (
            len(value) > 2 and value[1] == ":" and value[2] in {"/", "\\"}
        ) or any(marker in value for marker in LOCAL_PATH_MARKERS)
    if isinstance(value, dict):
        return any(contains_absolute_path(item) for item in value.values())
    if isinstance(value, list):
        return any(contains_absolute_path(item) for item in value)
    return False


def valid_sha(value: Any) -> bool:
    return isinstance(value, str) and bool(HEX64.match(value))


def approx_equal(left: Any, right: Any, tolerance: float = 1e-9) -> bool:
    return (
        isinstance(left, (int, float))
        and isinstance(right, (int, float))
        and abs(float(left) - float(right)) <= tolerance
    )


def retained_flux_projection(row: dict[str, Any]) -> float | None:
    values = (
        row.get("inbound_flux"),
        row.get("outbound_flux"),
        row.get("internal_coherence"),
    )
    if not all(isinstance(value, (int, float)) for value in values):
        return None
    return round(
        float(row["inbound_flux"])
        - float(row["outbound_flux"])
        + float(row["internal_coherence"]),
        6,
    )


def text_contains(value: Any, tokens: set[str]) -> bool:
    text = json.dumps(value, sort_keys=True).lower()
    return any(token in text for token in tokens)


def missing_or_placeholder(value: Any) -> bool:
    if value is None or value == "" or value == [] or value == {}:
        return True
    if isinstance(value, str):
        lowered = value.lower()
        return lowered in {"not_applicable", "none", "missing"} or lowered.startswith(
            "not_"
        )
    return False


def trace_mentions_multi_basin(trace: Any) -> bool:
    return not missing_or_placeholder(trace) and text_contains(
        trace,
        {
            "multi-basin",
            "multi_basin",
            "shared-medium",
            "shared_medium",
            "basin_separation",
            "coupled neighbor",
        },
    )


def validate_required_fields(
    artifact: dict[str, Any], schema: dict[str, Any], errors: list[str]
) -> None:
    missing_top_level = [
        field
        for field in schema["top_level_output_fields"]
        if field not in artifact
    ]
    if missing_top_level:
        errors.append(f"required_fields_present:missing_top_level={missing_top_level}")

    row_fields = set(schema["row_schema_fields"])
    for index, row in enumerate(artifact.get("rows", [])):
        if not isinstance(row, dict):
            errors.append(f"required_fields_present:row_{index}_not_object")
            continue
        missing = sorted(row_fields - set(row))
        if missing:
            errors.append(f"required_fields_present:row_{index}_missing={missing}")


def validate_enums(
    artifact: dict[str, Any], schema: dict[str, Any], errors: list[str]
) -> None:
    boundary_states = {
        row["boundary_state"] for row in schema["boundary_state_axis"]
    }
    challenge_classes = {
        row["challenge_class"] for row in schema["challenge_class_axis"]
    }
    row_decisions = set(schema["row_decision_policy"]["values"])
    external_roles = set(schema["external_state_role_policy"]["values"])
    synthesis_modes = set(
        schema["native_requirements_synthesis_contract"]["synthesis_mode_values"]
    )

    if artifact.get("synthesis_mode") not in synthesis_modes:
        errors.append(
            f"enum_values_valid:invalid_synthesis_mode={artifact.get('synthesis_mode')}"
        )

    for index, row in enumerate(artifact.get("rows", [])):
        if not isinstance(row, dict):
            continue
        if row.get("boundary_state") not in boundary_states:
            errors.append(
                f"enum_values_valid:row_{index}:boundary_state={row.get('boundary_state')}"
            )
        if row.get("challenge_class") not in challenge_classes:
            errors.append(
                f"enum_values_valid:row_{index}:challenge_class={row.get('challenge_class')}"
            )
        if row.get("row_decision") not in row_decisions:
            errors.append(
                f"enum_values_valid:row_{index}:row_decision={row.get('row_decision')}"
            )
        if row.get("external_state_role") not in external_roles:
            errors.append(
                "enum_values_valid:"
                f"row_{index}:external_state_role={row.get('external_state_role')}"
            )


def validate_c3_external_state_role(artifact: dict[str, Any], errors: list[str]) -> None:
    for index, row in enumerate(artifact.get("rows", [])):
        if not isinstance(row, dict) or row.get("challenge_class") != "C3":
            continue
        role = row.get("external_state_role")
        if role == "structured_external_state":
            continue
        if role == "perturbation" and (
            text_contains(row.get("boundary_crossing_trace"), {"crossing", "disruption"})
            or text_contains(row.get("failure_mode"), {"crossing", "disruption"})
        ):
            continue
        errors.append(
            "c3_external_state_role:"
            f"row_{index}:C3_requires_structured_external_state_without_crossing"
        )


def validate_b3_unlock_rule(artifact: dict[str, Any], errors: list[str]) -> None:
    unlocked_classes = {
        row.get("challenge_class")
        for row in artifact.get("rows", [])
        if isinstance(row, dict)
        and row.get("boundary_state") == "B2"
        and row.get("challenge_class") in {"C0", "C1", "C2"}
        and row.get("row_decision") in {"supported", "partial", "blocked"}
    }
    b3_unlock_audit = artifact.get("b3_unlock_audit")
    external_b3_unlock = (
        isinstance(b3_unlock_audit, dict)
        and (
            b3_unlock_audit.get("unlock_satisfied") is True
            or b3_unlock_audit.get("unlock_allowed") is True
        )
    )
    b3_unlocked = {"C0", "C1", "C2"} <= unlocked_classes or external_b3_unlock
    for index, row in enumerate(artifact.get("rows", [])):
        if not isinstance(row, dict) or row.get("boundary_state") != "B3":
            continue
        if b3_unlocked:
            continue
        if row.get("row_decision") in {"blocked", "not_applicable"} and text_contains(
            row.get("failure_mode"), {"b3_unlock_missing"}
        ):
            continue
        errors.append(
            "b3_unlock_rule:"
            f"row_{index}:B3_requires_B2_C0_C1_C2_or_b3_unlock_missing_blocker"
        )


def validate_b4_provisional_rule(artifact: dict[str, Any], errors: list[str]) -> None:
    for index, row in enumerate(artifact.get("rows", [])):
        if not isinstance(row, dict) or row.get("boundary_state") != "B4":
            continue
        decision = row.get("row_decision")
        constructed_support = row.get("boundary_state_constructed_support")
        has_source_backed_multi_basin = text_contains(
            constructed_support,
            {"source-backed", "source_backed", "multi-basin", "multi_basin"},
        )
        if row.get("challenge_class") == "C2" and not has_source_backed_multi_basin:
            if decision not in {"partial", "not_applicable"}:
                errors.append(
                    "b4_provisional_rule:"
                    f"row_{index}:B4_C2_without_source_backed_substrate_must_be_partial_or_not_applicable"
                )
        if decision == "supported" and not trace_mentions_multi_basin(
            row.get("dependency_trace")
        ):
            errors.append(
                "b4_provisional_rule:"
                f"row_{index}:supported_B4_requires_multi_basin_dependency_trace"
            )


def validate_row_decision_relation(artifact: dict[str, Any], errors: list[str]) -> None:
    for index, row in enumerate(artifact.get("rows", [])):
        if not isinstance(row, dict):
            continue
        decision = row.get("row_decision")
        allowed = row.get("boundary_claim_allowed")
        if decision in {"blocked", "rejected", "not_applicable"} and allowed is not False:
            errors.append(
                "row_decision_boundary_claim_relation:"
                f"row_{index}:{decision}_must_force_false"
            )
        if decision == "partial" and row.get("final_ap6_supported") is True:
            errors.append(
                "row_decision_boundary_claim_relation:"
                f"row_{index}:partial_cannot_final_ap6"
            )
        if allowed is True and row.get("claim_promotion_allowed") is False:
            errors.append(
                "row_decision_boundary_claim_relation:"
                f"row_{index}:allowed_with_promotion_blocked"
            )


def validate_claim_ceiling_preservation(
    artifact: dict[str, Any], errors: list[str]
) -> None:
    for index, row in enumerate(artifact.get("rows", [])):
        if not isinstance(row, dict):
            continue
        if row.get("claim_ceiling_preserved") is not True:
            errors.append(
                "claim_ceiling_preservation:"
                f"row_{index}:claim_ceiling_preserved_not_true"
            )
        if row.get("claim_promotion_allowed") is not False:
            errors.append(
                "claim_ceiling_preservation:"
                f"row_{index}:claim_promotion_allowed_not_false"
            )


def validate_boundary_crossing_trace(
    artifact: dict[str, Any], errors: list[str]
) -> None:
    for index, row in enumerate(artifact.get("rows", [])):
        if not isinstance(row, dict):
            continue
        if row.get("row_decision") in {"supported", "partial"} and row.get(
            "boundary_state"
        ) != "B0":
            if missing_or_placeholder(row.get("boundary_crossing_trace")):
                errors.append(
                    "boundary_crossing_trace_presence:"
                    f"row_{index}:supported_or_partial_non_B0_requires_trace"
                )


def validate_budget(
    artifact: dict[str, Any], schema: dict[str, Any], errors: list[str]
) -> None:
    budget_limits = schema.get("budget_limits", {})
    allowed_units = set(budget_limits.get("units", []))
    numeric_limits = budget_limits.get("limits", {})
    for index, row in enumerate(artifact.get("rows", [])):
        if not isinstance(row, dict):
            continue
        validity = row.get("budget_validity")
        if text_contains(validity, {"exceeded", "invalid", "over_budget"}):
            errors.append(f"budget_validity:row_{index}:budget_invalid")

        units = row.get("budget_units")
        if isinstance(units, list):
            invalid = sorted(unit for unit in units if unit not in allowed_units)
            if invalid:
                errors.append(f"budget_units:row_{index}:invalid_units={invalid}")
        elif isinstance(units, dict):
            invalid = sorted(unit for unit in units if unit not in allowed_units)
            if invalid:
                errors.append(f"budget_units:row_{index}:invalid_units={invalid}")
        elif not missing_or_placeholder(units) and units not in allowed_units:
            errors.append(f"budget_units:row_{index}:invalid_unit={units}")

        surface = row.get("budget_cost_surface")
        if isinstance(surface, dict):
            invalid_surface_units = sorted(
                unit for unit in surface if unit not in allowed_units
            )
            if invalid_surface_units:
                errors.append(
                    "budget_cost_surface:"
                    f"row_{index}:invalid_units={invalid_surface_units}"
                )
            for unit, value in surface.items():
                if unit in numeric_limits and isinstance(value, (int, float)):
                    if value > numeric_limits[unit]:
                        errors.append(
                            "budget_cost_surface:"
                            f"row_{index}:{unit}_exceeds_limit"
                        )


def validate_dependency_trace(
    artifact: dict[str, Any], schema: dict[str, Any], errors: list[str]
) -> None:
    required = set(schema["dependency_trace_format"]["required_fields"])
    for index, row in enumerate(artifact.get("rows", [])):
        if not isinstance(row, dict):
            continue
        trace = row.get("dependency_trace")
        if missing_or_placeholder(trace):
            continue
        if not isinstance(trace, list):
            errors.append(f"dependency_trace_format:row_{index}:trace_not_list")
            continue
        for trace_index, entry in enumerate(trace):
            if not isinstance(entry, dict):
                errors.append(
                    "dependency_trace_format:"
                    f"row_{index}:trace_{trace_index}_not_object"
                )
                continue
            missing = sorted(required - set(entry))
            if missing:
                errors.append(
                    "dependency_trace_format:"
                    f"row_{index}:trace_{trace_index}_missing={missing}"
                )
            if not valid_sha(entry.get("source_sha256")):
                errors.append(
                    "dependency_trace_format:"
                    f"row_{index}:trace_{trace_index}:source_sha256"
                )


def validate_claim_flags(artifact: dict[str, Any], errors: list[str]) -> None:
    claim_flags = artifact.get("claim_flags")
    if not isinstance(claim_flags, dict):
        errors.append("claim_flags_forced_false:missing_or_not_object")
        return
    unsafe_true = sorted(key for key, value in claim_flags.items() if value is not False)
    if unsafe_true:
        errors.append(f"claim_flags_forced_false:true_flags={unsafe_true}")


def validate_control_outcomes(
    artifact: dict[str, Any], schema: dict[str, Any], errors: list[str]
) -> None:
    controls = artifact.get("controls")
    if not isinstance(controls, dict):
        errors.append("control_outcomes_present:missing_or_not_object")
        return
    required = {control["control_id"] for control in schema["control_requirements"]}
    missing = sorted(required - set(controls))
    if missing:
        errors.append(f"control_outcomes_present:missing={missing}")


def validate_source_digest_presence(artifact: dict[str, Any], errors: list[str]) -> None:
    for section_name in ("source_artifacts", "source_reports"):
        section = artifact.get(section_name)
        if not isinstance(section, dict):
            errors.append(f"source_digest_presence:{section_name}_missing")
            continue
        for key, record in section.items():
            if not isinstance(record, dict) or not valid_sha(record.get("sha256")):
                errors.append(f"source_digest_presence:{section_name}:{key}")

    for index, row in enumerate(artifact.get("rows", [])):
        if not isinstance(row, dict):
            continue
        if not valid_sha(row.get("source_sha256")):
            errors.append(f"source_digest_presence:row_{index}:source_sha256")
        if not valid_sha(row.get("source_report_sha256")):
            errors.append(f"source_digest_presence:row_{index}:source_report_sha256")


def validate_digest_reproducibility(artifact: dict[str, Any], errors: list[str]) -> None:
    recorded = artifact.get("output_digest")
    if not valid_sha(recorded):
        errors.append("digest_reproducibility:missing_or_invalid_output_digest")
        return
    recomputed = output_digest(artifact)
    if recorded != recomputed:
        errors.append(
            "digest_reproducibility:"
            f"recorded={recorded}:recomputed={recomputed}"
        )


def validate_absolute_path_absence(artifact: dict[str, Any], errors: list[str]) -> None:
    if contains_absolute_path(artifact):
        errors.append("absolute_path_absence:absolute_path_recorded")


def validate_quiet_calibration(artifact: dict[str, Any], errors: list[str]) -> None:
    if artifact.get("artifact_id") != "n16_quiet_boundary_calibration":
        return

    rows = artifact.get("rows")
    if not isinstance(rows, list):
        errors.append("quiet_calibration_contract:rows_missing_or_not_list")
        return

    if artifact.get("final_ap6_closeout_allowed") is not False:
        errors.append("quiet_calibration_contract:final_ap6_closeout_must_be_false")

    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            continue
        if row.get("challenge_class") != "C0":
            errors.append(
                "quiet_calibration_contract:"
                f"row_{index}:challenge_class_must_be_C0"
            )
        case_policy = row.get("case_policy")
        if not isinstance(case_policy, dict) or case_policy.get(
            "calibration_only"
        ) is not True:
            errors.append(
                "quiet_calibration_contract:"
                f"row_{index}:case_policy_calibration_only_must_be_true"
            )
        if row.get("final_ap6_supported") is not False:
            errors.append(
                "quiet_calibration_contract:"
                f"row_{index}:final_ap6_supported_must_be_false"
            )
        descriptor = row.get("internal_state_descriptor")
        classification_path = (
            descriptor.get("classification_path")
            if isinstance(descriptor, dict)
            else None
        )
        if classification_path not in {
            "primary_floor",
            "fallback_basin_signal_only",
            "none",
        }:
            errors.append(
                "quiet_calibration_contract:"
                f"row_{index}:classification_path_missing_or_invalid"
            )

    by_cell = {
        row.get("cell_id"): row
        for row in rows
        if isinstance(row, dict) and row.get("cell_id") is not None
    }
    b0 = by_cell.get("B0_C0")
    if not isinstance(b0, dict):
        errors.append("quiet_calibration_contract:B0_C0_missing")
    elif b0.get("row_decision") != "rejected" or b0.get(
        "boundary_claim_allowed"
    ) is not False:
        errors.append(
            "quiet_calibration_contract:B0_C0_must_reject_boundary_support"
        )

    b1 = by_cell.get("B1_C0")
    b2 = by_cell.get("B2_C0")
    if isinstance(b1, dict) and isinstance(b2, dict):
        b1_score = b1.get("boundary_stability_score")
        b2_score = b2.get("boundary_stability_score")
        if not isinstance(b1_score, (int, float)) or not isinstance(
            b2_score, (int, float)
        ) or b2_score <= b1_score:
            errors.append(
                "quiet_calibration_contract:"
                "B2_C0_stability_must_exceed_B1_C0_stability"
            )
    else:
        errors.append("quiet_calibration_contract:B1_C0_or_B2_C0_missing")

    if isinstance(b2, dict):
        source_current = b2.get("source_current")
        snapshots = (
            source_current.get("case_snapshots")
            if isinstance(source_current, dict)
            else None
        )
        if not isinstance(snapshots, list) or len(snapshots) <= 1:
            errors.append(
                "quiet_calibration_contract:"
                "B2_C0_requires_multi_snapshot_quiet_window"
            )
        basin_descriptor = b2.get("basin_descriptor")
        if not isinstance(basin_descriptor, dict) or basin_descriptor.get(
            "stable_side_assignments"
        ) is not True or basin_descriptor.get("stable_boundary_edges") is not True:
            errors.append(
                "quiet_calibration_contract:"
                "B2_C0_requires_recorded_stable_side_and_boundary_edges"
            )
        elif basin_descriptor.get("all_snapshots_meet_persistence_floors") is not True:
            errors.append(
                "quiet_calibration_contract:"
                "B2_C0_requires_all_snapshots_to_meet_persistence_floors"
            )


def validate_challenge_sweep(artifact: dict[str, Any], errors: list[str]) -> None:
    if artifact.get("artifact_id") != "n16_challenge_sweep_matrix":
        return

    rows = artifact.get("rows")
    if not isinstance(rows, list):
        errors.append("challenge_sweep_contract:rows_missing_or_not_list")
        return

    if artifact.get("final_ap6_closeout_allowed") is not False:
        errors.append("challenge_sweep_contract:final_ap6_closeout_must_be_false")

    provenance = artifact.get("quiet_calibration_source_provenance")
    if not isinstance(provenance, dict):
        errors.append("challenge_sweep_contract:quiet_calibration_provenance_missing")
    else:
        if provenance.get("output_digest_matches_acceptance") is not True:
            errors.append(
                "challenge_sweep_contract:"
                "quiet_calibration_output_digest_must_match_acceptance"
            )
        for field in (
            "accepted_output_digest",
            "current_output_digest",
            "current_file_sha256",
        ):
            if not valid_sha(provenance.get(field)):
                errors.append(
                    "challenge_sweep_contract:"
                    f"quiet_calibration_provenance_{field}_invalid"
                )

    thresholds = artifact.get("challenge_thresholds")
    required_threshold_fields = {
        "internal_support_floor",
        "internal_coherence_floor",
        "minimum_coherence_margin_floor",
        "quiet_leakage_ceiling",
        "flux_leakage_warning",
        "breach_reclosure_floor",
        "shared_medium_basin_separation_floor",
    }
    if not isinstance(thresholds, dict):
        errors.append("challenge_sweep_contract:challenge_thresholds_missing")
        thresholds = {}
    else:
        missing_thresholds = sorted(required_threshold_fields - set(thresholds))
        if missing_thresholds:
            errors.append(
                "challenge_sweep_contract:"
                f"challenge_thresholds_missing={missing_thresholds}"
            )
        for field in required_threshold_fields & set(thresholds):
            if not isinstance(thresholds.get(field), (int, float)):
                errors.append(
                    "challenge_sweep_contract:"
                    f"challenge_threshold_{field}_must_be_numeric"
                )

    expected_classes = {"C0", "C1", "C2", "C3", "C4", "C5"}
    observed_classes = {
        row.get("challenge_class") for row in rows if isinstance(row, dict)
    }
    if observed_classes != expected_classes:
        errors.append(
            "challenge_sweep_contract:"
            f"challenge_classes_must_be_C0_to_C5={sorted(observed_classes)}"
        )

    canonical_digests = set()
    by_class = {}
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            continue
        by_class[row.get("challenge_class")] = row
        if row.get("boundary_state") != "B2":
            errors.append(
                "challenge_sweep_contract:"
                f"row_{index}:boundary_state_must_be_B2"
            )
        source_current = row.get("source_current")
        digest = (
            source_current.get("canonical_b2_definition_digest")
            if isinstance(source_current, dict)
            else None
        )
        if not valid_sha(digest):
            errors.append(
                "challenge_sweep_contract:"
                f"row_{index}:canonical_b2_definition_digest_missing"
            )
        else:
            canonical_digests.add(digest)
        case_policy = row.get("case_policy")
        if not isinstance(case_policy, dict) or case_policy.get(
            "canonical_b2_held_fixed"
        ) is not True:
            errors.append(
                "challenge_sweep_contract:"
                f"row_{index}:canonical_b2_held_fixed_must_be_true"
            )
        if row.get("boundary_claim_allowed") is not False or row.get(
            "final_ap6_supported"
        ) is not False:
            errors.append(
                "challenge_sweep_contract:"
                f"row_{index}:boundary_and_final_ap6_claims_must_be_false"
            )
        if not row.get("requirements_failed"):
            errors.append(
                "challenge_sweep_contract:"
                f"row_{index}:requirements_failed_must_be_recorded"
            )
        case_policy = row.get("case_policy")
        if isinstance(case_policy, dict) and case_policy.get(
            "challenge_thresholds"
        ) != thresholds:
            errors.append(
                "challenge_sweep_contract:"
                f"row_{index}:case_policy_thresholds_must_match_top_level"
            )
        if not isinstance(source_current, dict) or missing_or_placeholder(
            source_current.get("metric_construction_rationale")
        ):
            errors.append(
                "challenge_sweep_contract:"
                f"row_{index}:metric_construction_rationale_missing"
            )
        if not isinstance(source_current, dict) or missing_or_placeholder(
            source_current.get("challenge_pressure_rationale")
        ):
            errors.append(
                "challenge_sweep_contract:"
                f"row_{index}:challenge_pressure_rationale_missing"
            )
        budget_surface = row.get("budget_cost_surface")
        if not isinstance(budget_surface, dict) or budget_surface.get(
            "transform_count"
        ) != 1:
            errors.append(
                "challenge_sweep_contract:"
                f"row_{index}:transform_count_must_be_one_per_row"
            )

        failed_requirements = row.get("requirements_failed")
        metrics = (
            source_current.get("challenge_transform", {}).get("metrics", {})
            if isinstance(source_current, dict)
            else {}
        )
        leakage = row.get("leakage_ratio")
        if isinstance(leakage, (int, float)) and isinstance(
            thresholds.get("quiet_leakage_ceiling"), (int, float)
        ) and leakage > thresholds["quiet_leakage_ceiling"] and not text_contains(
            failed_requirements, {"quiet_leakage"}
        ):
            errors.append(
                "challenge_sweep_contract:"
                f"row_{index}:quiet_leakage_threshold_failure_not_recorded"
            )
        minimum_internal_support = metrics.get("minimum_internal_support")
        if isinstance(minimum_internal_support, (int, float)) and isinstance(
            thresholds.get("internal_support_floor"), (int, float)
        ) and minimum_internal_support < thresholds[
            "internal_support_floor"
        ] and not text_contains(
            failed_requirements, {"minimum_internal_support_floor"}
        ):
            errors.append(
                "challenge_sweep_contract:"
                f"row_{index}:minimum_internal_support_failure_not_recorded"
            )
        internal_coherence = row.get("internal_coherence")
        if isinstance(internal_coherence, (int, float)) and isinstance(
            thresholds.get("internal_coherence_floor"), (int, float)
        ) and internal_coherence < thresholds[
            "internal_coherence_floor"
        ] and not text_contains(
            failed_requirements, {"minimum_internal_coherence_floor"}
        ):
            errors.append(
                "challenge_sweep_contract:"
                f"row_{index}:minimum_internal_coherence_failure_not_recorded"
            )
        coherence_margin = row.get("coherence_margin")
        if isinstance(coherence_margin, (int, float)) and isinstance(
            thresholds.get("minimum_coherence_margin_floor"), (int, float)
        ) and coherence_margin < thresholds[
            "minimum_coherence_margin_floor"
        ] and not text_contains(
            failed_requirements, {"minimum_coherence_margin_floor"}
        ):
            errors.append(
                "challenge_sweep_contract:"
                f"row_{index}:minimum_coherence_margin_failure_not_recorded"
            )

    if len(canonical_digests) != 1:
        errors.append("challenge_sweep_contract:B2_digest_must_be_identical")

    fixed_b2_audit = artifact.get("fixed_b2_audit")
    reference_metrics = (
        fixed_b2_audit.get("canonical_b2_reference_metrics")
        if isinstance(fixed_b2_audit, dict)
        else None
    )
    c0 = by_class.get("C0")
    if not isinstance(reference_metrics, dict) or not isinstance(c0, dict):
        errors.append("challenge_sweep_contract:C0_reference_metrics_missing")
    else:
        c0_metrics = (
            c0.get("source_current", {})
            .get("challenge_transform", {})
            .get("metrics", {})
        )
        for field, expected_value in reference_metrics.items():
            if field == "minimum_internal_support":
                actual_value = c0_metrics.get(field)
            else:
                actual_value = c0.get(field)
            if actual_value != expected_value:
                errors.append(
                    "challenge_sweep_contract:"
                    f"C0_metric_{field}_must_match_i3_B2_reference"
                )

    c2 = by_class.get("C2")
    if not isinstance(c2, dict):
        errors.append("challenge_sweep_contract:C2_missing")
    else:
        if c2.get("external_state_role") != "coupling_channel":
            errors.append(
                "challenge_sweep_contract:C2_external_role_must_be_coupling_channel"
            )
        c2_perturbation = c2.get("external_perturbation_descriptor")
        if not isinstance(c2_perturbation, dict) or c2_perturbation.get(
            "perturbation_present"
        ) is not False:
            errors.append(
                "challenge_sweep_contract:"
                "C2_perturbation_present_must_remain_false_for_directional_flux"
            )

    c3 = by_class.get("C3")
    if not isinstance(c3, dict) or c3.get(
        "external_state_role"
    ) != "structured_external_state":
        errors.append("challenge_sweep_contract:C3_must_remain_structured_external")

    c4 = by_class.get("C4")
    if isinstance(c4, dict) and text_contains(
        c4.get("boundary_classification"), {"b3"}
    ) and not text_contains(c4.get("requirements_failed"), {"b3"}):
        errors.append(
            "challenge_sweep_contract:C4_b3_reference_requires_extension_blocker"
        )

    c5 = by_class.get("C5")
    if isinstance(c5, dict) and c5.get("row_decision") == "supported":
        errors.append("challenge_sweep_contract:C5_must_not_close_B4_separability")
    if isinstance(c5, dict):
        c5_source_current = c5.get("source_current")
        synthetic_neighbor = (
            c5_source_current.get("synthetic_neighbor_basin")
            if isinstance(c5_source_current, dict)
            else None
        )
        if not isinstance(synthetic_neighbor, dict) or synthetic_neighbor.get(
            "status"
        ) != "synthetic_shared_medium_stressor":
            errors.append(
                "challenge_sweep_contract:"
                "C5_synthetic_neighbor_must_be_documented_as_stressor"
            )


def validate_boundary_state_sweep(
    artifact: dict[str, Any], errors: list[str]
) -> None:
    if artifact.get("artifact_id") != "n16_boundary_state_sweep_matrix":
        return

    rows = artifact.get("rows")
    if not isinstance(rows, list):
        errors.append("boundary_state_sweep_contract:rows_missing_or_not_list")
        return

    if artifact.get("final_ap6_closeout_allowed") is not False:
        errors.append(
            "boundary_state_sweep_contract:final_ap6_closeout_must_be_false"
        )

    provenance = artifact.get("challenge_sweep_source_provenance")
    if not isinstance(provenance, dict):
        errors.append("boundary_state_sweep_contract:challenge_provenance_missing")
    else:
        if provenance.get("output_digest_matches_acceptance") is not True:
            errors.append(
                "boundary_state_sweep_contract:"
                "challenge_output_digest_must_match_acceptance"
            )
        for field in (
            "accepted_output_digest",
            "current_output_digest",
            "current_file_sha256",
        ):
            if not valid_sha(provenance.get(field)):
                errors.append(
                    "boundary_state_sweep_contract:"
                    f"challenge_provenance_{field}_invalid"
                )

    fixed_policy = artifact.get("c2_fixed_policy")
    fixed_profile = (
        fixed_policy.get("challenge_profile")
        if isinstance(fixed_policy, dict)
        else None
    )
    expected_profile = {
        "noise_amplitude": 0.0,
        "directional_flux_pressure": 0.34,
        "structured_external_coherence_pressure": 0.0,
        "breach_pressure": 0.0,
        "shared_medium_pressure": 0.0,
    }
    if fixed_profile != expected_profile:
        errors.append("boundary_state_sweep_contract:fixed_c2_profile_drifted")

    thresholds = artifact.get("challenge_thresholds")
    if not isinstance(thresholds, dict):
        errors.append("boundary_state_sweep_contract:challenge_thresholds_missing")
        thresholds = {}

    formulas = artifact.get("metric_construction_formulas")
    if not isinstance(formulas, dict):
        errors.append("boundary_state_sweep_contract:metric_formulas_missing")
        formulas = {}
    else:
        for field in (
            "leakage_ratio",
            "retained_flux",
            "boundary_stability_score",
            "flux_tolerance_score",
            "repair_score",
            "upstream_downstream_asymmetry_score",
            "bounded_reabsorption_response",
        ):
            if field not in formulas:
                errors.append(
                    "boundary_state_sweep_contract:"
                    f"metric_formula_missing={field}"
                )

    expected_states = {"B0", "B1", "B2", "B3", "B4"}
    observed_states = {
        row.get("boundary_state") for row in rows if isinstance(row, dict)
    }
    if observed_states != expected_states:
        errors.append(
            "boundary_state_sweep_contract:"
            f"boundary_states_must_be_B0_to_B4={sorted(observed_states)}"
        )

    by_state = {}
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            continue
        by_state[row.get("boundary_state")] = row
        if row.get("challenge_class") != "C2":
            errors.append(
                "boundary_state_sweep_contract:"
                f"row_{index}:challenge_class_must_be_C2"
            )
        if row.get("external_state_role") != "coupling_channel":
            errors.append(
                "boundary_state_sweep_contract:"
                f"row_{index}:external_role_must_be_coupling_channel"
            )
        perturbation = row.get("external_perturbation_descriptor")
        if not isinstance(perturbation, dict) or perturbation.get(
            "perturbation_present"
        ) is not False:
            errors.append(
                "boundary_state_sweep_contract:"
                f"row_{index}:C2_perturbation_present_must_be_false"
            )
        case_policy = row.get("case_policy")
        if not isinstance(case_policy, dict) or case_policy.get(
            "fixed_c2_profile"
        ) != expected_profile:
            errors.append(
                "boundary_state_sweep_contract:"
                f"row_{index}:fixed_c2_profile_must_match_top_level"
            )
        if isinstance(case_policy, dict) and case_policy.get(
            "retune_per_boundary_state_allowed"
        ) is not False:
            errors.append(
                "boundary_state_sweep_contract:"
                f"row_{index}:retune_per_boundary_state_must_be_false"
            )
        if row.get("boundary_claim_allowed") is not False or row.get(
            "final_ap6_supported"
        ) is not False:
            errors.append(
                "boundary_state_sweep_contract:"
                f"row_{index}:boundary_and_final_ap6_claims_must_be_false"
            )
        budget_surface = row.get("budget_cost_surface")
        if not isinstance(budget_surface, dict) or budget_surface.get(
            "transform_count"
        ) != 1:
            errors.append(
                "boundary_state_sweep_contract:"
                f"row_{index}:transform_count_must_be_one_per_row"
            )
        source_current = row.get("source_current")
        if not isinstance(source_current, dict) or missing_or_placeholder(
            source_current.get("metric_construction_rationale")
        ):
            errors.append(
                "boundary_state_sweep_contract:"
                f"row_{index}:metric_construction_rationale_missing"
            )
        if not isinstance(source_current, dict) or missing_or_placeholder(
            source_current.get("metric_construction_formulas")
        ):
            errors.append(
                "boundary_state_sweep_contract:"
                f"row_{index}:metric_construction_formulas_missing"
            )
        metrics = (
            source_current.get("challenge_transform", {}).get("metrics", {})
            if isinstance(source_current, dict)
            else {}
        )
        inbound = row.get("inbound_flux")
        outbound = row.get("outbound_flux")
        asymmetry = metrics.get("upstream_downstream_asymmetry_score")
        if isinstance(inbound, (int, float)) and isinstance(
            outbound, (int, float)
        ):
            denominator = inbound + outbound
            expected_asymmetry = (
                0.0
                if denominator == 0
                else round(abs(inbound - outbound) / denominator, 6)
            )
            if not approx_equal(asymmetry, expected_asymmetry):
                errors.append(
                    "boundary_state_sweep_contract:"
                    f"row_{index}:upstream_downstream_asymmetry_formula_mismatch"
                )

    b0 = by_state.get("B0")
    if not isinstance(b0, dict) or b0.get("row_decision") != "rejected":
        errors.append("boundary_state_sweep_contract:B0_must_reject_under_flux")
    elif not text_contains(
        b0.get("requirements_failed"), {"no_internal", "no_boundary"}
    ):
        errors.append(
            "boundary_state_sweep_contract:B0_rejection_requires_null_blocker"
        )

    b1 = by_state.get("B1")
    if not isinstance(b1, dict) or b1.get("row_decision") not in {
        "partial",
        "rejected",
    }:
        errors.append(
            "boundary_state_sweep_contract:B1_must_remain_limited_under_flux"
        )
    elif not text_contains(
        b1.get("requirements_failed"), {"support_persistence_not_claimed"}
    ):
        errors.append(
            "boundary_state_sweep_contract:"
            "B1_must_not_promote_extraction_to_persistence"
        )

    b2 = by_state.get("B2")
    reproduction = artifact.get("b2_reproduction_audit")
    if not isinstance(b2, dict) or not isinstance(reproduction, dict):
        errors.append("boundary_state_sweep_contract:B2_reproduction_audit_missing")
    elif reproduction.get("exact_reproduction") is not True:
        errors.append("boundary_state_sweep_contract:B2_must_reproduce_I4_C2")
    else:
        anchor = reproduction.get("anchor_reference")
        observed = reproduction.get("iteration_5_b2_metrics")
        if anchor != observed:
            errors.append(
                "boundary_state_sweep_contract:"
                "B2_iteration5_metrics_must_equal_I4_anchor"
            )
        required_b2_failures = [
            "quiet_leakage_ceiling_exceeded_under_directional_flux",
            "minimum_internal_support_floor_not_preserved_under_flux",
            "minimum_coherence_margin_floor_not_preserved_under_flux",
        ]
        if not all(
            label in b2.get("requirements_failed", [])
            for label in required_b2_failures
        ):
            errors.append(
                "boundary_state_sweep_contract:"
                "B2_must_reuse_iteration4_c2_failure_vocabulary"
            )

    b3 = by_state.get("B3")
    unlock = artifact.get("b3_unlock_audit")
    if not isinstance(unlock, dict) or unlock.get("unlock_satisfied") is not True:
        errors.append("boundary_state_sweep_contract:B3_unlock_not_satisfied")
    elif not all(
        isinstance(item, dict)
        and item.get("decision_admissible") is True
        and item.get("key_metrics_present") is True
        for item in unlock.get("content_quality", {}).values()
    ):
        errors.append(
            "boundary_state_sweep_contract:"
            "B3_unlock_must_check_prerequisite_content_quality"
        )
    if isinstance(b2, dict) and isinstance(b3, dict):
        b3_metrics = (
            b3.get("source_current", {})
            .get("challenge_transform", {})
            .get("metrics", {})
        )
        if b3.get("leakage_ratio", 1.0) > thresholds.get(
            "quiet_leakage_ceiling", 0.12
        ):
            errors.append(
                "boundary_state_sweep_contract:B3_must_reduce_B2_leakage_failure"
            )
        if b3_metrics.get("minimum_internal_support", 0.0) < thresholds.get(
            "internal_support_floor", 0.85
        ):
            errors.append(
                "boundary_state_sweep_contract:B3_must_preserve_support_floor"
            )
        if b3.get("coherence_margin", 0.0) < thresholds.get(
            "minimum_coherence_margin_floor", 0.52
        ):
            errors.append(
                "boundary_state_sweep_contract:"
                "B3_must_preserve_coherence_margin_floor"
            )
        if b3.get("retained_flux", 0.0) <= b2.get("retained_flux", 0.0):
            errors.append(
                "boundary_state_sweep_contract:B3_must_improve_retained_flux"
            )
        if b3.get("boundary_stability_score", 0.0) <= b2.get(
            "boundary_stability_score", 0.0
        ):
            errors.append(
                "boundary_state_sweep_contract:B3_must_improve_boundary_stability"
            )
        if not text_contains(
            b3.get("requirements_failed"), {"not_autonomous", "final_ap6"}
        ):
            errors.append(
                "boundary_state_sweep_contract:"
                "B3_success_must_preserve_claim_boundary"
            )
        if b3.get("failure_mode") != "c2_flux_repair_not_general_repair":
            errors.append(
                "boundary_state_sweep_contract:"
                "B3_failure_mode_must_be_boundary_specific"
            )

        b3_audit = artifact.get("b3_improvement_audit")
        b2_metrics = (
            b2.get("source_current", {})
            .get("challenge_transform", {})
            .get("metrics", {})
        )
        if not isinstance(b3_audit, dict):
            errors.append("boundary_state_sweep_contract:B3_improvement_audit_missing")
        else:
            expected_deltas = {
                "leakage_delta": round(
                    b3.get("leakage_ratio", 0.0) - b2.get("leakage_ratio", 0.0),
                    6,
                ),
                "retained_flux_delta": round(
                    b3.get("retained_flux", 0.0) - b2.get("retained_flux", 0.0),
                    6,
                ),
                "stability_delta": round(
                    b3.get("boundary_stability_score", 0.0)
                    - b2.get("boundary_stability_score", 0.0),
                    6,
                ),
                "internal_coherence_delta": round(
                    b3.get("internal_coherence", 0.0)
                    - b2.get("internal_coherence", 0.0),
                    6,
                ),
                "coherence_margin_delta": round(
                    b3.get("coherence_margin", 0.0)
                    - b2.get("coherence_margin", 0.0),
                    6,
                ),
                "minimum_internal_support_delta": round(
                    b3_metrics.get("minimum_internal_support", 0.0)
                    - b2_metrics.get("minimum_internal_support", 0.0),
                    6,
                ),
                "outbound_flux_delta": round(
                    b3.get("outbound_flux", 0.0) - b2.get("outbound_flux", 0.0),
                    6,
                ),
                "upstream_downstream_asymmetry_delta": round(
                    b3_metrics.get("upstream_downstream_asymmetry_score", 0.0)
                    - b2_metrics.get("upstream_downstream_asymmetry_score", 0.0),
                    6,
                ),
            }
            for field, expected_value in expected_deltas.items():
                if not approx_equal(b3_audit.get(field), expected_value):
                    errors.append(
                        "boundary_state_sweep_contract:"
                        f"B3_delta_mismatch={field}"
                    )

    b4 = by_state.get("B4")
    if not isinstance(b4, dict):
        errors.append("boundary_state_sweep_contract:B4_missing")
    else:
        if b4.get("row_decision") not in {"partial", "not_applicable"}:
            errors.append("boundary_state_sweep_contract:B4_C2_must_be_provisional")
        if not text_contains(
            b4.get("requirements_failed"), {"b4_c2", "b4_c5", "separability"}
        ):
            errors.append(
                "boundary_state_sweep_contract:"
                "B4_C2_must_not_close_B4_C5_separability"
            )
        decomposition = (
            b4.get("source_current", {})
            .get("challenge_transform", {})
            .get("flux_decomposition", {})
        )
        if not isinstance(decomposition, dict) or not {
            "retained_flux_within_intended_basin",
            "redirected_flux_through_coupling_channel",
            "leakage_into_neighbor_basin",
            "merge_confusion_pressure",
        }.issubset(decomposition):
            errors.append(
                "boundary_state_sweep_contract:"
                "B4_flux_decomposition_must_separate_retention_coupling_leakage_merge"
            )
        if not text_contains(
            b4.get("requirements_satisfied"),
            {"decomposition_complete", "no_failure_resolved"},
        ):
            errors.append(
                "boundary_state_sweep_contract:"
                "B4_satisfied_requirements_must_mark_recording_only"
            )

    gradient = (
        artifact.get("maturity_gradient_summary", {}).get("gradient")
        if isinstance(artifact.get("maturity_gradient_summary"), dict)
        else None
    )
    required_gradient_fields = {
        "row_decision",
        "boundary_classification",
        "internal_coherence",
        "coherence_margin",
        "leakage_ratio",
        "retained_flux",
        "boundary_stability_score",
        "repair_score",
        "flux_tolerance_score",
        "basin_separation_score",
        "upstream_downstream_asymmetry_score",
        "requirements_failed",
    }
    if not isinstance(gradient, dict):
        errors.append("boundary_state_sweep_contract:maturity_gradient_missing")
    else:
        for state in expected_states:
            entry = gradient.get(state)
            if not isinstance(entry, dict) or not required_gradient_fields <= set(
                entry
            ):
                errors.append(
                    "boundary_state_sweep_contract:"
                    f"maturity_gradient_missing_fields_for={state}"
                )

    changed = (
        artifact.get("maturity_gradient_summary", {}).get(
            "what_changed_relative_to_iteration_4"
        )
        if isinstance(artifact.get("maturity_gradient_summary"), dict)
        else None
    )
    if not isinstance(changed, dict) or not text_contains(
        changed.get("B3_vs_B4"), {"retained flux", "neighbor", "merge"}
    ):
        errors.append(
            "boundary_state_sweep_contract:B3_vs_B4_comparison_missing"
        )
    if not isinstance(changed, dict) or not text_contains(
        changed.get("B3_supported_claim_blocked_note"),
        {"boundary_claim_allowed", "final_ap6"},
    ):
        errors.append(
            "boundary_state_sweep_contract:"
            "B3_supported_claim_blocked_note_missing"
        )

    guardrails = artifact.get("iteration_6_guardrails")
    if not isinstance(guardrails, dict):
        errors.append("boundary_state_sweep_contract:iteration6_guardrails_missing")
        return

    if not text_contains(
        guardrails.get("b3_c2_scope_guard"), {"flux", "not general", "final ap6"}
    ):
        errors.append(
            "boundary_state_sweep_contract:"
            "B3_C2_scope_guard_must_block_general_repair"
        )
    b3_contrast = guardrails.get("b3_c4_contrast_pair")
    if not isinstance(b3_contrast, dict) or b3_contrast.get(
        "contrast_from"
    ) != "B2_C2" or b3_contrast.get("contrast_to") != "B3_C2":
        errors.append(
            "boundary_state_sweep_contract:"
            "B3_C4_guardrail_must_use_B2_B3_contrast_pair"
        )
    elif not text_contains(
        b3_contrast.get("iteration_6_question"), {"breach", "reclosure"}
    ):
        errors.append(
            "boundary_state_sweep_contract:"
            "B3_C4_guardrail_must_target_breach_reclosure"
        )

    if not text_contains(
        guardrails.get("b4_c2_scope_guard"), {"partial", "retained flux", "merge"}
    ):
        errors.append(
            "boundary_state_sweep_contract:"
            "B4_C2_scope_guard_must_block_nearly_supported_reading"
        )
    b4_inputs = guardrails.get("b4_c5_design_inputs")
    if not isinstance(b4_inputs, dict) or not {
        "leakage_into_neighbor_basin",
        "redirected_flux_through_coupling_channel",
        "merge_confusion_pressure",
        "basin_separation_score",
    }.issubset(b4_inputs):
        errors.append(
            "boundary_state_sweep_contract:"
            "B4_C5_guardrail_must_preserve_c2_decomposition_inputs"
        )
    elif not text_contains(
        b4_inputs.get("iteration_6_question"), {"shared-medium", "separability"}
    ):
        errors.append(
            "boundary_state_sweep_contract:"
            "B4_C5_guardrail_must_target_shared_medium_separability"
        )

    selected_expectations = guardrails.get("selected_probe_expectations")
    if not isinstance(selected_expectations, dict) or set(selected_expectations) != {
        "B0_C3",
        "B1_C2",
        "B2_C1",
        "B3_C4",
        "B4_C5",
    }:
        errors.append(
            "boundary_state_sweep_contract:"
            "iteration6_selected_probe_expectations_must_cover_planned_cells"
        )


def validate_selected_interaction_probes(
    artifact: dict[str, Any], errors: list[str]
) -> None:
    if artifact.get("artifact_id") != "n16_selected_interaction_probe_matrix":
        return

    expected_cells = ["B0_C3", "B1_C2", "B2_C1", "B3_C4", "B4_C5"]
    rows = artifact.get("rows")
    if not isinstance(rows, list):
        errors.append("selected_interaction_probe_contract:rows_missing_or_not_list")
        return

    if artifact.get("final_ap6_closeout_allowed") is not False:
        errors.append(
            "selected_interaction_probe_contract:"
            "final_ap6_closeout_must_be_false"
        )
    if artifact.get("synthesis_mode") != "partial_mvp":
        errors.append(
            "selected_interaction_probe_contract:synthesis_mode_must_be_partial_mvp"
        )
    if artifact.get("selected_cells") != expected_cells:
        errors.append(
            "selected_interaction_probe_contract:selected_cells_must_match_plan"
        )

    observed_cells = [row.get("cell_id") for row in rows if isinstance(row, dict)]
    if observed_cells != expected_cells:
        errors.append(
            "selected_interaction_probe_contract:"
            f"observed_cells_must_match_plan={observed_cells}"
        )

    provenance = artifact.get("source_provenance")
    if not isinstance(provenance, dict):
        errors.append("selected_interaction_probe_contract:source_provenance_missing")
    else:
        for key in (
            "iteration_4_challenge_sweep",
            "iteration_5_boundary_state_sweep",
        ):
            record = provenance.get(key)
            if not isinstance(record, dict) or record.get(
                "output_digest_matches_acceptance"
            ) is not True:
                errors.append(
                    "selected_interaction_probe_contract:"
                    f"{key}_digest_must_match_acceptance"
                )

    formulas = artifact.get("metric_construction_formulas")
    if not isinstance(formulas, dict):
        errors.append(
            "selected_interaction_probe_contract:metric_construction_formulas_missing"
        )
    else:
        for field in (
            "retained_flux",
            "reclosure_score",
            "basin_separation_score",
            "boundary_exclusivity_score",
            "merge_confusion_pressure",
            "leakage_into_neighbor_basin",
        ):
            if field not in formulas:
                errors.append(
                    "selected_interaction_probe_contract:"
                    f"metric_formula_missing={field}"
                )

    projection_audit = artifact.get("retained_flux_projection_audit")
    if not isinstance(projection_audit, dict):
        errors.append(
            "selected_interaction_probe_contract:"
            "retained_flux_projection_audit_missing"
        )

    by_cell = {}
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            continue
        by_cell[row.get("cell_id")] = row
        if row.get("boundary_claim_allowed") is not False or row.get(
            "final_ap6_supported"
        ) is not False:
            errors.append(
                "selected_interaction_probe_contract:"
                f"row_{index}:boundary_and_final_ap6_claims_must_be_false"
            )
        if not row.get("requirements_satisfied") or not row.get(
            "requirements_failed"
        ):
            errors.append(
                "selected_interaction_probe_contract:"
                f"row_{index}:requirements_satisfied_and_failed_required"
            )
        case_policy = row.get("case_policy")
        if not isinstance(case_policy, dict) or case_policy.get(
            "selected_probe_only"
        ) is not True or case_policy.get("not_full_matrix") is not True:
            errors.append(
                "selected_interaction_probe_contract:"
                f"row_{index}:case_policy_must_mark_selected_probe_only"
            )
        source_current = row.get("source_current")
        if not isinstance(source_current, dict) or not isinstance(
            source_current.get("metric_construction_formulas"), dict
        ):
            errors.append(
                "selected_interaction_probe_contract:"
                f"row_{index}:row_metric_construction_formulas_missing"
            )
        projection = retained_flux_projection(row)
        row_audit = (
            source_current.get("retained_flux_projection_audit")
            if isinstance(source_current, dict)
            else None
        )
        if not isinstance(row_audit, dict) or row_audit.get(
            "diagnostic_projection"
        ) != projection:
            errors.append(
                "selected_interaction_probe_contract:"
                f"row_{index}:retained_flux_projection_audit_mismatch"
            )
        cell_projection = (
            projection_audit.get(row.get("cell_id"))
            if isinstance(projection_audit, dict)
            else None
        )
        if not isinstance(cell_projection, dict) or cell_projection.get(
            "diagnostic_projection"
        ) != projection:
            errors.append(
                "selected_interaction_probe_contract:"
                f"row_{index}:top_level_projection_audit_mismatch"
            )
        for trace_index, trace in enumerate(row.get("boundary_crossing_trace", [])):
            if not isinstance(trace, dict):
                continue
            if trace.get("event") == "selected_probe_challenge":
                continue
            if trace.get("trace_event_type") != "selected_probe_boundary_edge":
                errors.append(
                    "selected_interaction_probe_contract:"
                    f"row_{index}:trace_{trace_index}:event_type_not_explicit"
                )

    b0 = by_cell.get("B0_C3")
    if not isinstance(b0, dict):
        errors.append("selected_interaction_probe_contract:B0_C3_missing")
    else:
        if b0.get("external_state_role") != "structured_external_state":
            errors.append(
                "selected_interaction_probe_contract:"
                "B0_C3_external_role_must_be_structured_external_state"
            )
        if b0.get("row_decision") != "supported" or b0.get(
            "boundary_claim_allowed"
        ) is not False:
            errors.append(
                "selected_interaction_probe_contract:"
                "B0_C3_must_support_active_null_rejection_only"
            )
        if b0.get("self_region_nodes"):
            errors.append(
                "selected_interaction_probe_contract:"
                "B0_C3_must_not_emit_self_region_nodes"
            )
        if not text_contains(
            b0.get("requirements_failed"), {"structured_external", "self_region"}
        ):
            errors.append(
                "selected_interaction_probe_contract:"
                "B0_C3_requires_structured_external_false_positive_blocker"
            )
        if not text_contains(
            b0.get("requirements_satisfied"), {"active_null_rejection_not_boundary"}
        ):
            errors.append(
                "selected_interaction_probe_contract:"
                "B0_C3_supported_semantics_must_be_explicit"
            )

    b1 = by_cell.get("B1_C2")
    if not isinstance(b1, dict):
        errors.append("selected_interaction_probe_contract:B1_C2_missing")
    else:
        if b1.get("row_decision") != "partial":
            errors.append(
                "selected_interaction_probe_contract:"
                "B1_C2_must_remain_partial_under_flux"
            )
        if not text_contains(
            b1.get("requirements_failed"), {"support_persistence_not_claimed"}
        ):
            errors.append(
                "selected_interaction_probe_contract:"
                "B1_C2_must_not_promote_weak_boundary_to_persistence"
            )

    b2 = by_cell.get("B2_C1")
    if not isinstance(b2, dict):
        errors.append("selected_interaction_probe_contract:B2_C1_missing")
    else:
        if b2.get("row_decision") != "supported":
            errors.append(
                "selected_interaction_probe_contract:"
                "B2_C1_noise_replay_must_remain_supported"
            )
        if not text_contains(
            b2.get("requirements_failed"),
            {"noise_tolerance_does_not_substitute"},
        ):
            errors.append(
                "selected_interaction_probe_contract:"
                "B2_C1_must_block_noise_tolerance_promotion"
            )
        b2_decomp = (
            b2.get("source_current", {})
            .get("challenge_transform", {})
            .get("probe_decomposition", {})
        )
        if not isinstance(b2_decomp, dict) or b2_decomp.get(
            "noise_amplitude"
        ) != 0.08:
            errors.append(
                "selected_interaction_probe_contract:"
                "B2_C1_noise_decomposition_required"
            )

    b3 = by_cell.get("B3_C4")
    unlock = artifact.get("b3_unlock_audit")
    if not isinstance(b3, dict):
        errors.append("selected_interaction_probe_contract:B3_C4_missing")
    else:
        if not isinstance(unlock, dict) or unlock.get("unlock_allowed") is not True:
            errors.append("selected_interaction_probe_contract:B3_unlock_not_allowed")
        if b3.get("row_decision") != "supported":
            errors.append(
                "selected_interaction_probe_contract:"
                "B3_C4_must_answer_breach_reclosure"
            )
        decomp = (
            b3.get("source_current", {})
            .get("challenge_transform", {})
            .get("probe_decomposition", {})
        )
        if not isinstance(decomp, dict):
            errors.append(
                "selected_interaction_probe_contract:"
                "B3_C4_probe_decomposition_missing"
            )
        else:
            if decomp.get("generalizes_from_c2_flux_repair") is not True:
                errors.append(
                    "selected_interaction_probe_contract:"
                    "B3_C4_must_record_generalization_from_C2_flux_repair"
                )
            if not isinstance(decomp.get("reclosure_score"), (int, float)) or not isinstance(
                decomp.get("breach_reclosure_floor"), (int, float)
            ) or decomp["reclosure_score"] < decomp["breach_reclosure_floor"]:
                errors.append(
                    "selected_interaction_probe_contract:"
                    "B3_C4_reclosure_score_must_meet_floor"
                )
            if decomp.get("repair_score_relationship") is None or b3.get(
                "reclosure_score"
            ) != b3.get("repair_score"):
                errors.append(
                    "selected_interaction_probe_contract:"
                    "B3_C4_reclosure_repair_alias_must_be_documented"
                )
            if not isinstance(decomp.get("reclosure_latency_steps"), (int, float)):
                errors.append(
                    "selected_interaction_probe_contract:"
                    "B3_C4_reclosure_latency_steps_required"
                )
            for field in (
                "b3_c2_anchor_metrics",
                "b2_c4_baseline_reference",
                "b3_c4_delta_vs_b2_c4",
            ):
                if not isinstance(decomp.get(field), dict):
                    errors.append(
                        "selected_interaction_probe_contract:"
                        f"B3_C4_{field}_missing"
                    )
        if b3.get("leakage_ratio", 1.0) > artifact.get(
            "challenge_thresholds", {}
        ).get("quiet_leakage_ceiling", 0.12):
            errors.append(
                "selected_interaction_probe_contract:"
                "B3_C4_must_preserve_quiet_leakage_ceiling"
            )
        if not text_contains(
            b3.get("requirements_failed"), {"not_autonomous", "final_ap6"}
        ):
            errors.append(
                "selected_interaction_probe_contract:"
                "B3_C4_success_must_preserve_claim_boundary"
            )

    b4 = by_cell.get("B4_C5")
    if not isinstance(b4, dict):
        errors.append("selected_interaction_probe_contract:B4_C5_missing")
    else:
        if b4.get("row_decision") != "supported":
            errors.append(
                "selected_interaction_probe_contract:"
                "B4_C5_must_answer_shared_medium_separability"
            )
        decomp = (
            b4.get("source_current", {})
            .get("challenge_transform", {})
            .get("probe_decomposition", {})
        )
        thresholds = artifact.get("challenge_thresholds", {})
        if not isinstance(decomp, dict):
            errors.append(
                "selected_interaction_probe_contract:"
                "B4_C5_probe_decomposition_missing"
            )
        else:
            if decomp.get("basin_separation_score", 0.0) < thresholds.get(
                "shared_medium_basin_separation_floor", 0.70
            ):
                errors.append(
                    "selected_interaction_probe_contract:"
                    "B4_C5_basin_separation_below_floor"
                )
            if decomp.get("shared_medium_leakage", 1.0) > thresholds.get(
                "quiet_leakage_ceiling", 0.12
            ):
                errors.append(
                    "selected_interaction_probe_contract:"
                    "B4_C5_shared_medium_leakage_above_ceiling"
                )
            if decomp.get("merge_confusion_pressure", 1.0) > thresholds.get(
                "merge_confusion_ceiling", 0.20
            ):
                errors.append(
                    "selected_interaction_probe_contract:"
                    "B4_C5_merge_confusion_above_ceiling"
                )
            if decomp.get("boundary_exclusivity_score", 0.0) < thresholds.get(
                "boundary_exclusivity_floor", 0.70
            ):
                errors.append(
                    "selected_interaction_probe_contract:"
                    "B4_C5_boundary_exclusivity_below_floor"
                )
            for field in (
                "leakage_ratio_relationship",
                "asymmetry_note",
                "coupling_channel_attribution",
            ):
                if field not in decomp:
                    errors.append(
                        "selected_interaction_probe_contract:"
                        f"B4_C5_{field}_missing"
                    )
            if b4.get("leakage_ratio") != decomp.get("shared_medium_leakage"):
                errors.append(
                    "selected_interaction_probe_contract:"
                    "B4_C5_leakage_ratio_must_equal_shared_medium_leakage"
                )
            if decomp.get("basin_a_as_internal_side") is not True or decomp.get(
                "neighbor_basin_treated_as_external_side"
            ) is not True:
                errors.append(
                    "selected_interaction_probe_contract:"
                    "B4_C5_asymmetric_basin_roles_must_be_recorded"
                )
        for field in (
            "boundary_exclusivity_score",
            "leakage_into_neighbor_basin",
            "shared_medium_leakage",
            "redirected_flux_through_coupling_channel",
            "merge_confusion_pressure",
        ):
            if field not in b4:
                errors.append(
                    "selected_interaction_probe_contract:"
                    f"B4_C5_top_level_metric_missing={field}"
                )
        if "B4_C5_separability_measured_not_inherited_from_label" not in b4.get(
            "requirements_satisfied", []
        ):
            errors.append(
                "selected_interaction_probe_contract:"
                "B4_C5_must_measure_not_inherit_separability"
            )
        if not text_contains(
            b4.get("requirements_failed"), {"native", "final_ap6"}
        ):
            errors.append(
                "selected_interaction_probe_contract:"
                "B4_C5_success_must_preserve_claim_boundary"
            )

    summary = artifact.get("selected_probe_summary")
    answered = (
        summary.get("unresolved_questions_answered")
        if isinstance(summary, dict)
        else None
    )
    if not isinstance(answered, dict):
        errors.append(
            "selected_interaction_probe_contract:"
            "selected_probe_summary_answers_missing"
        )
    else:
        if answered.get(
            "did_b3_generalize_from_c2_flux_to_c4_breach_reclosure"
        ) is not True:
            errors.append(
                "selected_interaction_probe_contract:"
                "B3_C4_answer_must_be_true"
            )
        if answered.get("did_b4_resolve_c5_shared_medium_separability") is not True:
            errors.append(
                "selected_interaction_probe_contract:"
                "B4_C5_answer_must_be_true"
            )

    replay_audit = artifact.get("replay_consistency_audit")
    if not isinstance(replay_audit, dict) or replay_audit.get(
        "all_replay_rows_match_sources"
    ) is not True:
        errors.append(
            "selected_interaction_probe_contract:replay_consistency_audit_failed"
        )
    else:
        for cell_id in ("B1_C2", "B2_C1"):
            entry = replay_audit.get(cell_id)
            if not isinstance(entry, dict) or entry.get(
                "all_key_metrics_match"
            ) is not True:
                errors.append(
                    "selected_interaction_probe_contract:"
                    f"replay_metric_consistency_failed={cell_id}"
                )

    comparison = artifact.get("cross_iteration_metric_comparison")
    if not isinstance(comparison, list) or len(comparison) < 4:
        errors.append(
            "selected_interaction_probe_contract:"
            "cross_iteration_metric_comparison_missing"
        )


def validate_basin_boundary_requirements_matrix(
    artifact: dict[str, Any], schema: dict[str, Any], errors: list[str]
) -> None:
    if artifact.get("artifact_id") != "n16_basin_boundary_requirements_matrix":
        return

    rows = artifact.get("rows")
    if not isinstance(rows, list) or not rows:
        errors.append("basin_boundary_requirements_contract:rows_missing_or_empty")
        rows = []

    if artifact.get("synthesis_mode") != "full":
        errors.append(
            "basin_boundary_requirements_contract:synthesis_mode_must_be_full"
        )
    if artifact.get("control_matrix_mode") != "full_control_matrix":
        errors.append(
            "basin_boundary_requirements_contract:"
            "control_matrix_mode_must_be_full_control_matrix"
        )
    if artifact.get("included_iterations") != ["1", "2", "3", "4", "5", "6", "7"]:
        errors.append(
            "basin_boundary_requirements_contract:"
            "included_iterations_must_be_1_to_7"
        )
    if artifact.get("deferred_iterations") != ["8", "9"]:
        errors.append(
            "basin_boundary_requirements_contract:"
            "deferred_iterations_must_be_8_9"
        )
    if artifact.get("final_ap6_closeout_allowed") is not False:
        errors.append(
            "basin_boundary_requirements_contract:"
            "final_ap6_closeout_must_remain_false"
        )

    expected_provenance = {
        "boundary_source_inventory",
        "boundary_schema_v1",
        "quiet_boundary_calibration",
        "challenge_sweep_matrix",
        "boundary_state_sweep_matrix",
        "selected_interaction_probe_matrix",
    }
    provenance = artifact.get("source_provenance")
    if not isinstance(provenance, dict):
        errors.append("basin_boundary_requirements_contract:source_provenance_missing")
    else:
        missing = sorted(expected_provenance - set(provenance))
        if missing:
            errors.append(
                "basin_boundary_requirements_contract:"
                f"source_provenance_missing={missing}"
            )
        for key in expected_provenance & set(provenance):
            record = provenance.get(key)
            if not isinstance(record, dict) or record.get(
                "output_digest_matches_acceptance"
            ) is not True:
                errors.append(
                    "basin_boundary_requirements_contract:"
                    f"source_provenance_digest_mismatch={key}"
                )
            if not isinstance(record, dict) or record.get("provenance_role") not in {
                "contract_artifact",
                "evidence_artifact",
            }:
                errors.append(
                    "basin_boundary_requirements_contract:"
                    f"source_provenance_role_invalid={key}"
                )

    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            continue
        source_current = row.get("source_current")
        case_policy = row.get("case_policy")
        if not isinstance(source_current, dict) or source_current.get(
            "iteration_7_no_new_scientific_cell"
        ) is not True:
            errors.append(
                "basin_boundary_requirements_contract:"
                f"row_{index}:must_mark_no_new_scientific_cell"
            )
        if not isinstance(case_policy, dict) or case_policy.get(
            "new_boundary_behavior_discovery_allowed"
        ) is not False:
            errors.append(
                "basin_boundary_requirements_contract:"
                f"row_{index}:new_boundary_behavior_discovery_must_be_false"
            )
        if row.get("boundary_claim_allowed") is not False or row.get(
            "final_ap6_supported"
        ) is not False or row.get("claim_promotion_allowed") is not False:
            errors.append(
                "basin_boundary_requirements_contract:"
                f"row_{index}:claim_flags_must_remain_false"
            )

    required_requirements = {
        "minimum_coherence_margin_requirement",
        "minimum_internal_support_requirement",
        "maximum_leakage_requirement",
        "flux_balance_requirement",
        "repair_reabsorption_requirement",
        "structured_external_coherence_rejection_requirement",
        "inter_basin_separation_requirement",
    }
    requirements = artifact.get("native_boundary_requirements_observed")
    if not isinstance(requirements, dict):
        errors.append(
            "basin_boundary_requirements_contract:"
            "native_boundary_requirements_missing"
        )
        requirements = {}
    missing_requirements = sorted(required_requirements - set(requirements))
    if missing_requirements:
        errors.append(
            "basin_boundary_requirements_contract:"
            f"requirements_missing={missing_requirements}"
        )
    for key in required_requirements & set(requirements):
        record = requirements.get(key)
        if not isinstance(record, dict):
            errors.append(
                "basin_boundary_requirements_contract:"
                f"requirement_not_object={key}"
            )
            continue
        if not record.get("supported_by"):
            errors.append(
                "basin_boundary_requirements_contract:"
                f"requirement_missing_supported_by={key}"
            )
        if not record.get("failed_or_limited_by") and not record.get(
            "still_limited_by"
        ):
            errors.append(
                "basin_boundary_requirements_contract:"
                f"requirement_missing_failure_or_limit={key}"
            )

    structured_external_requirement = requirements.get(
        "structured_external_coherence_rejection_requirement"
    )
    if isinstance(structured_external_requirement, dict):
        failed_cells = {
            row.get("cell_id")
            for row in structured_external_requirement.get(
                "failed_or_limited_by", []
            )
            if isinstance(row, dict)
        }
        if "B0_C0" in failed_cells:
            errors.append(
                "basin_boundary_requirements_contract:"
                "structured_external_requirement_must_not_use_B0_C0_as_C3_failure"
            )
        if "no_C3_failure_cell_exists_all_C3_cells_correctly_reject" not in (
            structured_external_requirement.get("still_limited_by") or []
        ):
            errors.append(
                "basin_boundary_requirements_contract:"
                "structured_external_requirement_must_record_no_C3_failure_cell"
            )

    controls = artifact.get("negative_control_matrix")
    if not isinstance(controls, dict):
        errors.append(
            "basin_boundary_requirements_contract:negative_control_matrix_missing"
        )
        controls = {}
    required_controls = {control["control_id"] for control in schema["control_requirements"]}
    required_controls.add("duplicate_replay_control")
    missing_controls = sorted(required_controls - set(controls))
    if missing_controls:
        errors.append(
            "basin_boundary_requirements_contract:"
            f"negative_controls_missing={missing_controls}"
        )
    for control_id in required_controls & set(controls):
        control = controls.get(control_id)
        if not isinstance(control, dict):
            errors.append(
                "basin_boundary_requirements_contract:"
                f"negative_control_not_object={control_id}"
            )
            continue
        if control.get("fail_closed") is not True or not control.get("blocker"):
            errors.append(
                "basin_boundary_requirements_contract:"
                f"negative_control_must_fail_closed={control_id}"
            )
        if control.get("ap6_claim_allowed") is not False:
            errors.append(
                "basin_boundary_requirements_contract:"
                f"negative_control_ap6_claim_must_be_false={control_id}"
            )
        if "schema_backed" not in control:
            errors.append(
                "basin_boundary_requirements_contract:"
                f"negative_control_schema_backing_missing={control_id}"
            )

    duplicate_control = controls.get("duplicate_replay_control")
    if not isinstance(duplicate_control, dict):
        errors.append(
            "basin_boundary_requirements_contract:duplicate_replay_control_missing"
        )
    else:
        if duplicate_control.get("schema_backed") is not False:
            errors.append(
                "basin_boundary_requirements_contract:"
                "duplicate_replay_control_must_be_i7_extension"
            )
        if duplicate_control.get("control_family") != "i7_replay_extension":
            errors.append(
                "basin_boundary_requirements_contract:"
                "duplicate_replay_control_family_invalid"
            )

    for control_id in (
        "structured_external_coherence_rejection_control",
        "multi_basin_merge_control",
    ):
        control = controls.get(control_id)
        if not isinstance(control, dict) or control.get("stress_level") != "high":
            errors.append(
                "basin_boundary_requirements_contract:"
                f"dangerous_relabel_control_must_be_high_stress={control_id}"
            )

    replay = artifact.get("replay_matrix")
    if not isinstance(replay, dict):
        errors.append("basin_boundary_requirements_contract:replay_matrix_missing")
        replay = {}
    replay_expectations = {
        "duplicate_replay": ("same_digest", True),
        "artifact_only_replay": ("hidden_runtime_dependency_detected", False),
        "snapshot_load_replay": ("status", "stable"),
        "order_inversion_replay": ("same_digest_after_canonical_ordering", True),
    }
    for replay_id, (field, expected) in replay_expectations.items():
        record = replay.get(replay_id)
        if not isinstance(record, dict):
            errors.append(
                "basin_boundary_requirements_contract:"
                f"replay_record_missing={replay_id}"
            )
            continue
        if record.get("status") != "stable":
            errors.append(
                "basin_boundary_requirements_contract:"
                f"replay_status_must_be_stable={replay_id}"
            )
        if record.get(field) != expected:
            errors.append(
                "basin_boundary_requirements_contract:"
                f"replay_expectation_failed={replay_id}:{field}"
            )

    aggregate_summary = artifact.get("aggregate_metric_summary")
    if not isinstance(aggregate_summary, dict):
        errors.append(
            "basin_boundary_requirements_contract:aggregate_metric_summary_missing"
        )
    else:
        for section in ("global_all_rows", "supported_boundary_candidate_rows"):
            record = aggregate_summary.get(section)
            if not isinstance(record, dict):
                errors.append(
                    "basin_boundary_requirements_contract:"
                    f"aggregate_metric_section_missing={section}"
                )
        if not isinstance(artifact.get("aggregate_metric_scope"), str) or not text_contains(
            artifact.get("aggregate_metric_scope"), {"including null", "rejected", "partial"}
        ):
            errors.append(
                "basin_boundary_requirements_contract:"
                "aggregate_metric_scope_must_explain_global_row_scope"
            )

    cross_iteration_summary = artifact.get("cross_iteration_metric_summary")
    if not isinstance(cross_iteration_summary, list) or len(cross_iteration_summary) < 6:
        errors.append(
            "basin_boundary_requirements_contract:"
            "cross_iteration_metric_summary_missing_or_too_short"
        )

    handoff = artifact.get("iteration_8_classification_handoff")
    if not isinstance(handoff, dict):
        errors.append("basin_boundary_requirements_contract:i8_handoff_missing")
    else:
        if handoff.get("ready_for_iteration_8_classification") is not True:
            errors.append(
                "basin_boundary_requirements_contract:i8_handoff_not_ready"
            )
        if handoff.get("final_ap6_closeout_allowed") is not False:
            errors.append(
                "basin_boundary_requirements_contract:i8_handoff_closeout_not_false"
            )
        if not text_contains(
            handoff.get("control_backing_note"),
            {"duplicate_replay_control", "schema_backed=false", "run-level replay"},
        ):
            errors.append(
                "basin_boundary_requirements_contract:"
                "i8_handoff_must_explain_duplicate_replay_backing"
            )

    unsafe_claim_flags = artifact.get("unsafe_claim_flags_forced_false")
    if not isinstance(unsafe_claim_flags, dict) or any(
        value is not False for value in unsafe_claim_flags.values()
    ):
        errors.append(
            "basin_boundary_requirements_contract:"
            "unsafe_claim_flags_must_all_be_false"
        )

    checks = artifact.get("checks")
    if not isinstance(checks, dict) or not checks:
        errors.append("basin_boundary_requirements_contract:checks_missing")
    else:
        failed = sorted(key for key, value in checks.items() if value is not True)
        if failed:
            errors.append(
                "basin_boundary_requirements_contract:"
                f"checks_failed={failed}"
            )


def validate(artifact: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    validate_required_fields(artifact, schema, errors)
    validate_enums(artifact, schema, errors)
    validate_c3_external_state_role(artifact, errors)
    validate_b3_unlock_rule(artifact, errors)
    validate_b4_provisional_rule(artifact, errors)
    validate_row_decision_relation(artifact, errors)
    validate_claim_ceiling_preservation(artifact, errors)
    validate_boundary_crossing_trace(artifact, errors)
    validate_budget(artifact, schema, errors)
    validate_dependency_trace(artifact, schema, errors)
    validate_claim_flags(artifact, errors)
    validate_control_outcomes(artifact, schema, errors)
    validate_source_digest_presence(artifact, errors)
    validate_digest_reproducibility(artifact, errors)
    validate_absolute_path_absence(artifact, errors)
    validate_quiet_calibration(artifact, errors)
    validate_challenge_sweep(artifact, errors)
    validate_boundary_state_sweep(artifact, errors)
    validate_selected_interaction_probes(artifact, errors)
    validate_basin_boundary_requirements_matrix(artifact, schema, errors)
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "artifact",
        nargs="?",
        default=str(DEFAULT_SCHEMA),
        help="row-bearing N16 artifact to validate",
    )
    parser.add_argument(
        "--schema",
        default=str(DEFAULT_SCHEMA),
        help="N16 Iteration 2 schema artifact",
    )
    args = parser.parse_args()

    artifact = load_json(Path(args.artifact))
    schema = load_json(Path(args.schema))
    errors = validate(artifact, schema)
    result = {
        "artifact": args.artifact,
        "schema": args.schema,
        "status": "passed" if not errors else "failed",
        "errors": errors,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
