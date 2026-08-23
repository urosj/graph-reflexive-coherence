"""Correct GRV4 artifact terminology without recomputing numerical evidence."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from artifact_io import (
    EXPERIMENT_ROOT,
    artifact_envelope,
    assert_payload_digest,
    git,
    read_json,
    sha256_file,
    write_json,
)
from compare_frozen_and_full_dynamics import validate_prerequisite, write_report
from gate_receipts import finalize_receipt, validate_receipt


SOURCE_RESULT_SCHEMA = "b1_grv4_frozen_full_comparison_v1"
SOURCE_RESULT_PAYLOAD_SHA256 = (
    "48f9193407772f34f2aefb113f20461312112255ed7381d370d13e85059c993a"
)
SOURCE_RECEIPT_PAYLOAD_SHA256 = (
    "2554b83c03b89cb7621297af959ef4310836f6944d1f3b7fa9995c96b3b26f6e"
)
TARGET_RESULT_SCHEMA = "b1_grv4_frozen_full_comparison_v2"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-08-B1-GR-grc9v3-continuation-readback-verification/"
    "scripts/clarify_grv4_artifact_semantics.py"
)


_NUMERIC_PATH_ALIASES = {
    "frozen_semidiscrete_rates": "frozen_semidiscrete_generator_eigenvalues",
    "primary_agreement_count": (
        "primary_no_resolved_difference_within_uncertainty_count"
    ),
    "primary_bounded_difference_count": (
        "primary_resolved_bounded_difference_count"
    ),
}


def _numeric_leaf_records(value: Any, path: tuple[str, ...] = ()) -> list[tuple[str, Any]]:
    records: list[tuple[str, Any]] = []
    if isinstance(value, dict):
        for key, child in sorted(
            value.items(), key=lambda item: _NUMERIC_PATH_ALIASES.get(item[0], item[0])
        ):
            if key == "artifact_semantics_correction":
                continue
            canonical_key = _NUMERIC_PATH_ALIASES.get(key, key)
            records.extend(_numeric_leaf_records(child, (*path, canonical_key)))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            records.extend(_numeric_leaf_records(child, (*path, str(index))))
    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        records.append(("/".join(path), value))
    return records


def correct_payload(payload: dict[str, Any]) -> dict[str, Any]:
    corrected = deepcopy(payload)
    for branch in corrected["branch_rows"]:
        if "frozen_semidiscrete_rates" not in branch:
            raise ValueError("source branch is missing frozen_semidiscrete_rates")
        branch["frozen_semidiscrete_generator_eigenvalues"] = branch.pop(
            "frozen_semidiscrete_rates"
        )
        branch["frozen_semidiscrete_generator_definition"] = (
            "-A_W_H_cont_equals_A_W_H_P"
        )
        for comparison_name in (
            "primary_C_full_recurrence_comparison",
            "secondary_C_W_full_recurrence_comparison",
        ):
            comparison = branch[comparison_name]
            relation = comparison.get("bounded_relation")
            if relation == "agreement":
                comparison["bounded_relation"] = (
                    "no_resolved_difference_within_uncertainty"
                )
            elif relation == "bounded_difference":
                comparison["bounded_relation"] = "resolved_bounded_difference"

    summary = corrected["summary"]
    summary["primary_no_resolved_difference_within_uncertainty_count"] = summary.pop(
        "primary_agreement_count"
    )
    summary["primary_resolved_bounded_difference_count"] = summary.pop(
        "primary_bounded_difference_count"
    )
    summary["primary_equivalence_supported"] = False
    corrected["claim_boundary"]["frozen_full_equivalence_supported"] = False
    corrected["artifact_semantics_correction"] = {
        "correction_kind": "artifact_schema_and_interpretation_only",
        "source_result_schema": SOURCE_RESULT_SCHEMA,
        "source_result_payload_sha256": SOURCE_RESULT_PAYLOAD_SHA256,
        "source_receipt_payload_sha256": SOURCE_RECEIPT_PAYLOAD_SHA256,
        "numerical_recomputation_performed": False,
        "classification_algorithm_changed": False,
        "numerical_values_changed": False,
        "corrections": [
            "rename evolution-generator eigenvalue field",
            "replace agreement wording with no-resolved-difference wording",
            "state explicitly that primary equivalence is unsupported",
            "make accepted GRV3 anchor authoritative over historical receipt status",
        ],
    }
    source_numeric = _numeric_leaf_records(payload)
    corrected_numeric = _numeric_leaf_records(corrected)
    if source_numeric != corrected_numeric:
        first_difference = next(
            (
                (left, right)
                for left, right in zip(source_numeric, corrected_numeric)
                if left != right
            ),
            (source_numeric[-1:], corrected_numeric[-1:]),
        )
        raise ValueError(
            "artifact correction changed a numerical leaf or its scope: "
            f"{first_difference!r}"
        )
    return corrected


def main() -> None:
    output_root = EXPERIMENT_ROOT / "outputs"
    result_path = output_root / "frozen_full_comparison.json"
    receipt_path = output_root / "gates/grv4_result_receipt.json"
    protected_path = output_root / "protected_path_manifest_v4.json"

    source_envelope = read_json(result_path)
    assert_payload_digest(source_envelope)
    source_receipt = read_json(receipt_path)
    validate_receipt(source_receipt)
    if source_envelope["schema_version"] == SOURCE_RESULT_SCHEMA:
        if source_envelope["payload_sha256"] != SOURCE_RESULT_PAYLOAD_SHA256:
            raise ValueError("GRV4 source artifact payload does not match reviewed v1")
        if source_receipt["receipt_payload_sha256"] != SOURCE_RECEIPT_PAYLOAD_SHA256:
            raise ValueError("GRV4 source receipt does not match reviewed v1")
        corrected_payload = correct_payload(source_envelope["payload"])
    elif source_envelope["schema_version"] == TARGET_RESULT_SCHEMA:
        corrected_payload = source_envelope["payload"]
        correction = corrected_payload.get("artifact_semantics_correction", {})
        if (
            correction.get("source_result_payload_sha256")
            != SOURCE_RESULT_PAYLOAD_SHA256
            or correction.get("source_receipt_payload_sha256")
            != SOURCE_RECEIPT_PAYLOAD_SHA256
        ):
            raise ValueError("GRV4 v2 artifact is not derived from the reviewed v1")
        if corrected_payload["summary"].get("primary_equivalence_supported") is not False:
            raise ValueError("GRV4 v2 equivalence boundary is missing")
    else:
        raise ValueError("unsupported GRV4 artifact schema")
    if not source_receipt["prerequisite_acceptance_anchors"]:
        raise ValueError("GRV3 acceptance anchor is missing")
    _, prerequisite_anchor = validate_prerequisite()
    correction_revision = git("rev-parse", "HEAD")
    correction_script = Path(__file__).resolve()
    serializer_script = EXPERIMENT_ROOT / "scripts/compare_frozen_and_full_dynamics.py"
    write_json(
        result_path,
        artifact_envelope(
            corrected_payload,
            schema_version=TARGET_RESULT_SCHEMA,
            generating_command=COMMAND,
            reproducibility_class="byte_reproducible_from_reviewed_v1_artifact",
            metadata={
                "numerical_execution_revision": source_receipt[
                    "input_execution_revision"
                ],
                "artifact_correction_base_revision": correction_revision,
                "correction_script_sha256": sha256_file(correction_script),
                "serializer_script_sha256": sha256_file(serializer_script),
                "source_result_payload_sha256": SOURCE_RESULT_PAYLOAD_SHA256,
                "numerical_recomputation_performed": False,
            },
        ),
    )
    report_path = write_report(corrected_payload)

    corrected_receipt = deepcopy(source_receipt)
    corrected_receipt.pop("receipt_payload_sha256", None)
    corrected_receipt.pop("prerequisite_receipt_status", None)
    corrected_receipt["prerequisite_acceptance_status"] = prerequisite_anchor[
        "acceptance_status"
    ]
    corrected_receipt["claim_ceiling"] = (
        "substrate_reduced_frozen_W_comparator_and_no_resolved_difference_"
        "within_admitted_uncertainty_pending_human_review"
    )
    corrected_receipt["grv4_summary"] = corrected_payload["summary"]
    corrected_receipt["artifact_semantics_correction"] = {
        "source_receipt_payload_sha256": SOURCE_RECEIPT_PAYLOAD_SHA256,
        "source_result_payload_sha256": SOURCE_RESULT_PAYLOAD_SHA256,
        "artifact_correction_base_revision": correction_revision,
        "numerical_recomputation_performed": False,
        "classification_algorithm_changed": False,
    }
    corrected_receipt["output_artifact_digests"] = {
        path.relative_to(EXPERIMENT_ROOT).as_posix(): sha256_file(path)
        for path in sorted((result_path, protected_path, report_path))
    }
    corrected_receipt = finalize_receipt(corrected_receipt)
    validate_receipt(corrected_receipt)
    write_json(receipt_path, corrected_receipt)
    print("GRV4 artifact semantics corrected without numerical recomputation.")


if __name__ == "__main__":
    main()
