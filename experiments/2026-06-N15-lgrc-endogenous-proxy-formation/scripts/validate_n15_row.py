#!/usr/bin/env python3
"""Validate N15 row-bearing artifacts against the Iteration 2 schema."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N15-lgrc-endogenous-proxy-formation"
DEFAULT_SCHEMA = EXPERIMENT / "outputs" / "n15_proxy_formation_schema_v1.json"
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
        return value.startswith(("/", "\\")) or any(
            marker in value for marker in LOCAL_PATH_MARKERS
        )
    if isinstance(value, dict):
        return any(contains_absolute_path(item) for item in value.values())
    if isinstance(value, list):
        return any(contains_absolute_path(item) for item in value)
    return False


def valid_sha(value: Any) -> bool:
    return isinstance(value, str) and bool(HEX64.match(value))


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
        help="row-bearing N15 artifact to validate",
    )
    parser.add_argument(
        "--schema",
        default=str(DEFAULT_SCHEMA),
        help="N15 Iteration 2 schema artifact",
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
