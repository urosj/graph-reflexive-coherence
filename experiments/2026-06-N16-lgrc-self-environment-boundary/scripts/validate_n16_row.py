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
    b3_unlocked = {"C0", "C1", "C2"} <= unlocked_classes
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
