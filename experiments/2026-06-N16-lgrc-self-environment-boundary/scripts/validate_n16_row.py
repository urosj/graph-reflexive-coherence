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
