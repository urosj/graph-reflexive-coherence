#!/usr/bin/env python3
"""Build N29 I14.2-1 clean extractive alternative source search."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-30T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N29-lgrc-agentic-ecology-convergence-bridge"
N28 = ROOT / "experiments" / "2026-06-N28-lgrc-generative-vs-extractive-persistence"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/scripts/"
    "build_n29_extractive_clean_alternative_i1421.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

I14 = EXPERIMENT / "outputs" / "n29_generative_extractive_medium_reshaping_i14.json"
I14A = EXPERIMENT / "outputs" / "n29_generative_extractive_runtime_admission_i14a.json"
I142 = EXPERIMENT / "outputs" / "n29_extractive_depletion_runtime_i142.json"
I14C = EXPERIMENT / "outputs" / "n29_generative_extractive_direct_replay_stress_i14c.json"
OUTPUT = EXPERIMENT / "outputs" / "n29_extractive_clean_alternative_search_i1421.json"
REPORT = EXPERIMENT / "reports" / "n29_extractive_clean_alternative_search_i1421.md"

EXTRACTIVE_SOURCES = [
    {
        "source_id": "n28_i4b_primary_extractive",
        "path": N28 / "outputs" / "n28_primary_extractive_contrast_probe.json",
        "row_id": "n28_i4b_row_primary_extractive_contrast",
        "source_role": "primary_extractive_i14_2_source",
    },
    {
        "source_id": "n28_i4c_extractive_strengthening",
        "path": N28 / "outputs" / "n28_extractive_strengthening_contrast_probe.json",
        "row_id": "n28_i4c_row_extractive_strengthening_contrast",
        "source_role": "stronger_extractive_mechanism_source",
    },
    {
        "source_id": "n28_i4c2_extractive_mechanism_diversity",
        "path": N28 / "outputs" / "n28_extractive_mechanism_diversity_probe.json",
        "row_id": "n28_i4c2_row_extractive_mechanism_diversity_contrast",
        "source_role": "alternative_extractive_mechanism_source",
    },
]

TRANSITION_MATRIX = N28 / "outputs" / "n28_regime_boundary_transition_matrix.json"

UNSAFE_FLAGS = {
    "agency_claim_allowed": False,
    "agentic_ecology_runtime_claim_allowed": False,
    "altruism_claim_allowed": False,
    "ant_ecology_success_claim_allowed": False,
    "biological_agency_claim_allowed": False,
    "closed_environmental_circulation_loop_claim_allowed": False,
    "cooperation_claim_allowed": False,
    "coordinated_exchange_cycle_claim_allowed": False,
    "ecology_success_claim_allowed": False,
    "exploitation_claim_allowed": False,
    "native_ecological_role_claim_allowed": False,
    "native_support_claim_allowed": False,
    "resource_economy_claim_allowed": False,
    "semantic_goal_claim_allowed": False,
    "semantic_purpose_claim_allowed": False,
}


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(data: Any) -> str:
    return hashlib.sha256(
        json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "utf-8"
        )
    ).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(canonical_json(data), encoding="utf-8")


def no_absolute_paths(data: Any) -> bool:
    text = json.dumps(data, sort_keys=True, ensure_ascii=True)
    forbidden = ("/" + "home" + "/", "Documents" + "/" + "RC-github")
    return all(pattern not in text for pattern in forbidden)


def check(check_id: str, passed: bool, details: str | None = None) -> dict[str, Any]:
    row: dict[str, Any] = {"check_id": check_id, "passed": bool(passed)}
    if details is not None:
        row["details"] = details
    return row


def finalize(data: dict[str, Any]) -> dict[str, Any]:
    payload = copy.deepcopy(data)
    payload.pop("output_digest", None)
    data["output_digest"] = digest_value(payload)
    return data


def source_artifact(source_id: str, path: Path, data: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "path": str(path.relative_to(ROOT)),
        "artifact_id": data.get("artifact_id", "not_recorded"),
        "iteration": data.get("iteration", "not_recorded"),
        "status": data.get("status", "not_recorded"),
        "acceptance_state": data.get("acceptance_state", "not_recorded"),
        "output_digest": data.get("output_digest", "not_recorded"),
        "sha256": sha256_file(path),
    }


def row_by_id(data: dict[str, Any], row_id: str) -> dict[str, Any]:
    for row in data.get("candidate_rows", []):
        if row.get("row_id") == row_id:
            return row
    raise KeyError(row_id)


def classification_result(row: dict[str, Any]) -> dict[str, Any]:
    return row.get("regime_classification_result") or row.get("generative_classification_result")


def manifest_paths_match(manifest: list[dict[str, Any]]) -> bool:
    return all((ROOT / row["path"]).exists() for row in manifest)


def manifest_sha_match(manifest: list[dict[str, Any]]) -> bool:
    for row in manifest:
        path = ROOT / row["path"]
        if not path.exists() or sha256_file(path) != row.get("sha256"):
            return False
    return True


def extractive_source_record(spec: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    data = load_json(spec["path"])
    row = row_by_id(data, spec["row_id"])
    merge = row["merge_leakage_trace"]
    classification = classification_result(row)
    below_ceiling = merge["value"] <= merge["ceiling"]
    source_current = row.get("derived_report_only") is False and bool(row.get("source_current_inputs"))
    row_supported = row.get("row_decision") == "supported"
    extractive = classification.get("classification_result") == "extractive"
    clean_candidate = source_current and row_supported and extractive and below_ceiling
    search_row = {
        "source_id": spec["source_id"],
        "source_role": spec["source_role"],
        "source_path": str(spec["path"].relative_to(ROOT)),
        "source_artifact_id": data["artifact_id"],
        "source_output_digest": data["output_digest"],
        "source_row_id": row["row_id"],
        "source_row_digest": row["row_digest"],
        "row_decision": row["row_decision"],
        "classification_result": classification,
        "source_current_inputs_non_empty": bool(row.get("source_current_inputs")),
        "derived_report_only": row.get("derived_report_only"),
        "artifact_manifest_paths_exist": manifest_paths_match(row["artifact_manifest"]),
        "artifact_manifest_sha256_matches": manifest_sha_match(row["artifact_manifest"]),
        "neighbor_capacity_delta_trace": row["neighborhood_capacity_delta_trace"],
        "capacity_attribution_trace": row["capacity_attribution_trace"],
        "merge_leakage_value": merge["value"],
        "merge_leakage_ceiling": merge["ceiling"],
        "merge_leakage_below_ceiling": below_ceiling,
        "clean_bounded_leakage_extractive_candidate": clean_candidate,
        "admission_status": (
            "admissible_clean_candidate"
            if clean_candidate
            else "blocked_by_merge_leakage_ceiling"
        ),
        "why_not_i14_2_1_replacement": (
            "source-current extractive row exists, but merge/leakage remains above "
            "the declared N28 ceiling; consuming it would preserve the I14.2 "
            "extractive-mechanism caveat instead of replacing it."
            if not clean_candidate
            else "not_applicable_clean_candidate_found"
        ),
    }
    return data, search_row


def transition_control_rows() -> list[dict[str, Any]]:
    matrix = load_json(TRANSITION_MATRIX)
    rows: list[dict[str, Any]] = []
    for row in matrix.get("transition_rows", []):
        if row.get("source_regime_label") != "extractive":
            continue
        if row.get("transition_id") != "neutral_gap_without_mixed_lobes":
            continue
        trace_path = ROOT / row["transition_trace_artifact"]
        trace = load_json(trace_path)
        metrics = trace.get("metrics", {})
        rows.append(
            {
                "transition_row_id": row["row_id"],
                "source_row_id": row["source_row_id"],
                "row_decision": row["row_decision"],
                "transition_id": row["transition_id"],
                "expected_label": row["expected_label"],
                "observed_label": row["observed_label"],
                "new_source_current_evidence_opened": row["new_source_current_evidence_opened"],
                "ge5_boundary_preservation_allowed": row["ge5_boundary_preservation_allowed"],
                "transition_trace_artifact": row["transition_trace_artifact"],
                "transition_trace_artifact_sha256": row["transition_trace_artifact_sha256"],
                "transition_trace_sha256_matches": sha256_file(trace_path)
                == row["transition_trace_artifact_sha256"],
                "extractive_flattening": metrics.get("extractive_flattening"),
                "extractive_flattening_ceiling": metrics.get("extractive_flattening_ceiling"),
                "merge_leakage": metrics.get("merge_leakage"),
                "merge_leakage_ceiling": metrics.get("merge_leakage_ceiling"),
                "would_be_below_leakage_ceiling": (
                    metrics.get("merge_leakage", 1.0) <= metrics.get("merge_leakage_ceiling", 0.0)
                ),
                "consumable_as_i14_2_1_replacement": False,
                "nonconsumption_reason": (
                    "This is an unclassified neutral-gap transition/control row, not a "
                    "supported source-current extractive candidate. Lower leakage here "
                    "cannot backfill I14.2."
                ),
            }
        )
    return rows


def write_report(path: Path, data: dict[str, Any]) -> None:
    lines = [
        "# N29 I14.2-1 Clean Extractive Alternative Search",
        "",
        "## Result",
        "",
        "```text",
        f"status = {data['status']}",
        f"acceptance_state = {data['acceptance_state']}",
        f"clean_replacement_candidate_created = {str(data['clean_replacement_candidate_created']).lower()}",
        f"clean_source_candidate_found = {str(data['clean_source_candidate_found']).lower()}",
        f"best_merge_leakage_value = {data['best_source_candidate']['merge_leakage_value']}",
        f"best_merge_leakage_ceiling = {data['best_source_candidate']['merge_leakage_ceiling']}",
        f"should_rerun_i14b_i14c_with_i14_2_1 = {str(data['should_rerun_i14b_i14c_with_i14_2_1']).lower()}",
        f"output_digest = {data['output_digest']}",
        f"failed_checks = {data['failed_checks']}",
        "```",
        "",
        "## Interpretation",
        "",
        "I14.2-1 searched the source-backed N28 extractive portfolio for a cleaner",
        "replacement for I14.2: an extractive source-current row whose merge/leakage",
        "is below the declared N28 ceiling. It did not find one. The best available",
        "positive extractive source remains the original I4-B row, with leakage",
        "0.033 against a 0.025 ceiling. The later I4-C and I4-C2 extractive rows",
        "strengthen extractive mechanism diversity, but their leakage is larger, not",
        "cleaner.",
        "",
        "Lower-leakage rows do exist in the N28 transition matrix, but those rows are",
        "neutral-gap / unclassified control rows. They are not supported extractive",
        "source-current candidates and cannot be used to replace I14.2.",
        "",
        "## Candidate Sources",
        "",
        "| Source row | Leakage | Ceiling | Clean candidate | Status |",
        "| --- | ---: | ---: | --- | --- |",
    ]
    for row in data["candidate_search_rows"]:
        lines.append(
            "| {source_row_id} | {merge_leakage_value:.3f} | {merge_leakage_ceiling:.3f} | {clean} | {status} |".format(
                source_row_id=row["source_row_id"],
                merge_leakage_value=row["merge_leakage_value"],
                merge_leakage_ceiling=row["merge_leakage_ceiling"],
                clean=str(row["clean_bounded_leakage_extractive_candidate"]).lower(),
                status=row["admission_status"],
            )
        )
    lines.extend(
        [
            "",
            "## Consequence For I14-B/C",
            "",
            "Because I14.2-1 did not create a replacement runtime candidate, I14-B and",
            "I14-C should not be rerun just to include this row. A focused I14.2-1-B/C",
            "or expanded I14-B/C rerun becomes necessary only after a future source-current",
            "extractive row satisfies the clean bounded-leakage gate.",
            "",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build() -> dict[str, Any]:
    i14 = load_json(I14)
    i14a = load_json(I14A)
    i142 = load_json(I142)
    i14c = load_json(I14C)

    source_artifacts = [
        source_artifact("n29_i14_prototype_d_motif_synthesis", I14, i14),
        source_artifact("n29_i14a_runtime_admission_schema", I14A, i14a),
        source_artifact("n29_i14_2_original_extractive_candidate", I142, i142),
        source_artifact("n29_i14c_direct_replay_stress", I14C, i14c),
    ]

    candidate_rows: list[dict[str, Any]] = []
    for spec in EXTRACTIVE_SOURCES:
        source_data, row = extractive_source_record(spec)
        candidate_rows.append(row)
        source_artifacts.append(source_artifact(spec["source_id"], spec["path"], source_data))

    clean_rows = [row for row in candidate_rows if row["clean_bounded_leakage_extractive_candidate"]]
    best_source = min(candidate_rows, key=lambda row: row["merge_leakage_value"])
    transition_rows = transition_control_rows()

    original_i14_2 = i142["runtime_candidate_row"]
    i14c_i142 = next(
        row
        for row in i14c["candidate_replay_stress_results"]
        if row["runtime_row_id"] == original_i14_2["runtime_row_id"]
    )

    replacement_created = bool(clean_rows)
    data: dict[str, Any] = {
        "artifact_id": "n29_extractive_clean_alternative_search_i1421",
        "experiment_id": "N29",
        "iteration": "I14.2-1",
        "title": "Prototype D I14.2-1 Clean Extractive Alternative Search",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": (
            "accepted_clean_extractive_alternative_search_no_admissible_replacement_found"
        ),
        "source_artifacts": source_artifacts
        + [source_artifact("n28_i6a_transition_matrix_context", TRANSITION_MATRIX, load_json(TRANSITION_MATRIX))],
        "search_question": (
            "Can the existing source-backed N28 extractive portfolio supply a direct "
            "I14.2 replacement whose merge/leakage is below the declared ceiling?"
        ),
        "source_selection_policy": {
            "must_be_source_current": True,
            "must_be_supported_extractive_candidate": True,
            "must_preserve_negative_neighbor_capacity_delta": True,
            "must_have_merge_leakage_below_declared_ceiling": True,
            "must_not_use_transition_or_null_rows_as_positive_evidence": True,
            "thresholds_retuned_for_n29": False,
        },
        "candidate_search_rows": candidate_rows,
        "nonconsumable_lower_leakage_transition_rows": transition_rows,
        "clean_source_candidate_found": bool(clean_rows),
        "clean_replacement_candidate_created": replacement_created,
        "best_source_candidate": best_source,
        "original_i14_2_status": {
            "source_row_id": original_i14_2["source_n28_row_id"],
            "runtime_row_id": original_i14_2["runtime_row_id"],
            "i14c_final_status": i14c_i142["final_i14c_status"],
            "leakage_record_status": original_i14_2["leakage_interpretation_record"][
                "leakage_record_status"
            ],
            "merge_leakage_value": original_i14_2["merge_leakage_trace"]["value"],
            "merge_leakage_ceiling": original_i14_2["merge_leakage_trace"]["ceiling"],
            "original_i14_2_replaced": False,
        },
        "i14_2_1_result": "blocked_no_clean_source_current_extractive_replacement",
        "replacement_blockers": [
            "all supported source-current N28 extractive rows exceed the merge/leakage ceiling",
            "lower-leakage N28 transition rows are rejected or unclassified controls, not positive extractive candidates",
            "N29 cannot retune N28 thresholds or relabel neutral-gap controls as extractive runtime evidence",
        ],
        "should_rerun_i14b_i14c_with_i14_2_1": False,
        "rerun_policy": {
            "current_result_requires_i14b_i14c_rerun": False,
            "reason": "No replacement runtime candidate was created.",
            "future_clean_candidate_requires_controls": True,
            "future_clean_candidate_requires_replay_stress": True,
            "acceptable_future_rerun_shapes": [
                "focused_i14_2_1_b_controls_and_i14_2_1_c_replay_stress",
                "expanded_i14_b_i14_c_rollup_including_clean_extractive_candidate",
            ],
        },
        "claim_ceiling": (
            "clean_extractive_alternative_search_completed_no_runtime_replacement_"
            "original_i14_2_leakage_caveat_preserved"
        ),
        "prototype_d_runtime_support_claim_allowed": False,
        "clean_bounded_extractive_runtime_claim_allowed": False,
        "unsafe_claim_flags": UNSAFE_FLAGS,
    }

    checks = [
        check("i14_source_passed", i14.get("status") == "passed"),
        check("i14a_schema_passed", i14a.get("status") == "passed"),
        check("i14_2_source_passed", i142.get("status") == "passed"),
        check("i14c_source_passed", i14c.get("status") == "passed"),
        check("source_rows_checked", len(candidate_rows) == len(EXTRACTIVE_SOURCES)),
        check(
            "all_source_rows_are_supported_extractive",
            all(
                row["row_decision"] == "supported"
                and row["classification_result"]["classification_result"] == "extractive"
                for row in candidate_rows
            ),
        ),
        check(
            "all_source_rows_are_source_current",
            all(
                row["derived_report_only"] is False
                and row["source_current_inputs_non_empty"] is True
                for row in candidate_rows
            ),
        ),
        check(
            "all_source_manifests_validate",
            all(
                row["artifact_manifest_paths_exist"] and row["artifact_manifest_sha256_matches"]
                for row in candidate_rows
            ),
        ),
        check("no_clean_source_candidate_found", not clean_rows),
        check(
            "best_source_is_original_i14_2_source",
            best_source["source_row_id"] == "n28_i4b_row_primary_extractive_contrast",
        ),
        check(
            "best_source_still_exceeds_ceiling",
            best_source["merge_leakage_value"] > best_source["merge_leakage_ceiling"],
        ),
        check(
            "lower_leakage_transition_rows_not_consumed",
            transition_rows
            and all(row["consumable_as_i14_2_1_replacement"] is False for row in transition_rows),
        ),
        check(
            "original_i14_2_caveat_preserved",
            data["original_i14_2_status"]["leakage_record_status"]
            == "extractive_mechanism_exceedance_caveat",
        ),
        check("no_replacement_runtime_candidate_created", replacement_created is False),
        check("i14b_i14c_rerun_not_required_without_candidate", data["should_rerun_i14b_i14c_with_i14_2_1"] is False),
        check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_FLAGS.values())),
        check("no_absolute_paths_in_record", no_absolute_paths(data)),
    ]

    data["checks"] = checks
    data["failed_checks"] = [item["check_id"] for item in checks if not item["passed"]]
    data["script_sha256"] = sha256_file(ROOT / SCRIPT_RELATIVE_PATH)
    if data["failed_checks"]:
        data["status"] = "failed"
        data["acceptance_state"] = "failed_clean_extractive_alternative_search_validation"
    return finalize(data)


def main() -> None:
    data = build()
    write_json(OUTPUT, data)
    data = load_json(OUTPUT)
    write_report(REPORT, data)
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    print(f"wrote {REPORT.relative_to(ROOT)}")
    print(f"status = {data['status']}")
    print(f"output_digest = {data['output_digest']}")


if __name__ == "__main__":
    main()
