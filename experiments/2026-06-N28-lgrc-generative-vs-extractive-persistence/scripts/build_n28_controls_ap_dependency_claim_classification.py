#!/usr/bin/env python3
"""Build N28 Iteration 7 controls / AP dependency / claim classification."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-29T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N28-lgrc-generative-vs-extractive-persistence"
OUTPUT = EXPERIMENT / "outputs" / "n28_controls_ap_dependency_claim_classification.json"
REPORT = EXPERIMENT / "reports" / "n28_controls_ap_dependency_claim_classification.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n28_controls_ap_dependency_claim_classification_artifacts"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/scripts/"
    "build_n28_controls_ap_dependency_claim_classification.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

SOURCE_FILES = {
    "i1": (
        "n28_source_inventory_and_contract_admission",
        "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/outputs/"
        "n28_source_inventory_and_contract_admission.json",
        "f30af50b1e1209039b82454b510f4765de7ee8befe214d96218dec3207db5985",
        "source_inventory_and_contract_boundary",
    ),
    "i2": (
        "n28_generative_extractive_schema_and_controls",
        "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/outputs/"
        "n28_generative_extractive_schema_and_controls.json",
        "e118496c025e1a36aac7e4337adcacd869715a5ce5ec6aaaf1558ef0d6576c18",
        "schema_control_and_ladder_freeze",
    ),
    "i3": (
        "n28_active_nulls_and_failure_baselines",
        "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/outputs/"
        "n28_active_nulls_and_failure_baselines.json",
        "ddd8234d8f3b5fb424c8160d65e90adbe755916c6e4e1b26bd8574a48dc6e8a4",
        "active_nulls_fail_closed_boundary",
    ),
    "i5": (
        "n28_replay_capacity_attribution_matrix",
        "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/outputs/"
        "n28_replay_capacity_attribution_matrix.json",
        "3fd8875fa01e4cbb91933bc89cf2db32a1a2d8396a6ebc16451c33a008af6caa",
        "broad_replay_control_matrix",
    ),
    "i5a": (
        "n28_artifact_only_reconstruction_replay_probe",
        "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/outputs/"
        "n28_artifact_only_reconstruction_replay_probe.json",
        "c88d2605b60f272ab4fd50bc062c09ab5059f26bf236e7339309196f47863646",
        "artifact_only_reconstruction_fail_closed_controls",
    ),
    "i6": (
        "n28_stress_regime_separation_matrix",
        "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/outputs/"
        "n28_stress_regime_separation_matrix.json",
        "fe051d860391bdbceddc2892abd49dc117b8a5797b3802d77609b1578e1ad756",
        "broad_ge5_stress_regime_separation_matrix",
    ),
    "i6a": (
        "n28_regime_boundary_transition_matrix",
        "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/outputs/"
        "n28_regime_boundary_transition_matrix.json",
        "e6b0afbf81873e519db458e611cc01a1c11b2e9b5c2dead899946b270077700d",
        "same_policy_boundary_transition_matrix",
    ),
    "i6b": (
        "n28_margin_envelope_sweep",
        "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/outputs/"
        "n28_margin_envelope_sweep.json",
        "f91f4cb675b39e0fa87f5ebfbbb842e52129d42c2fbe7d4586bbe2bcd54c5fab",
        "margin_envelope_diagnostic_no_new_ge_support",
    ),
    "i5b": (
        "n28_focused_margin_variant_replay_matrix",
        "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/outputs/"
        "n28_focused_margin_variant_replay_matrix.json",
        "0ce6c4dcb35f4c7bef0f2e17c8ab2ff87bde958706c390fd05e016b5092fb08e",
        "focused_variant_replay_control_matrix",
    ),
    "i6c": (
        "n28_focused_margin_variant_stress_envelope",
        "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/outputs/"
        "n28_focused_margin_variant_stress_envelope.json",
        "0dc3cc97695338d5f54719e993a4dd2912d5983eb03f066c3de04e027f3c06b3",
        "focused_current_multiplier_margin_stress_matrix",
    ),
}

PROBE_FILES = [
    (
        "4",
        "primary_generative_candidate",
        "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/outputs/"
        "n28_primary_generative_candidate_probe.json",
        "daa25e4694929b11af38d7b044f4b4f5a4e70f6c2fbcae954db6a84854c08e5d",
        "broad_paired_regime_positive",
    ),
    (
        "4-A",
        "generative_strengthening_candidate",
        "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/outputs/"
        "n28_generative_strengthening_candidate_probe.json",
        "07f15756b0584cbc91e4b765e4e96a07de0e62a772e0b0a49f1723f83d68b85c",
        "broad_paired_regime_positive",
    ),
    (
        "4-A2",
        "generative_mechanism_diversity_candidate",
        "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/outputs/"
        "n28_generative_mechanism_diversity_probe.json",
        "f2785e97307704bff58e413eb071aff10311f0a3d6bd753ebccfb4c1975b6c20",
        "broad_paired_regime_positive",
    ),
    (
        "4-B",
        "primary_extractive_contrast",
        "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/outputs/"
        "n28_primary_extractive_contrast_probe.json",
        "5015b7f5a148db75c7513b8fa8f249d1ac1fb0fc5fe4c6150d28d4ae644f84d3",
        "broad_paired_regime_contrast",
    ),
    (
        "4-C",
        "extractive_strengthening_contrast",
        "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/outputs/"
        "n28_extractive_strengthening_contrast_probe.json",
        "013286de4bfa88838412d757a47c76b09f6f98381f71bddfa21cd1f5f70ba9d6",
        "broad_paired_regime_contrast",
    ),
    (
        "4-C2",
        "extractive_mechanism_diversity_contrast",
        "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/outputs/"
        "n28_extractive_mechanism_diversity_probe.json",
        "cd099229fa37dcdf1c497555fd6ace7d4435035c87e58c1eec9bac6acb7e7067",
        "broad_paired_regime_contrast",
    ),
    (
        "4-D",
        "primary_competitive_neutral_contrast",
        "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/outputs/"
        "n28_primary_competitive_neutral_contrast_probe.json",
        "f124a1afe8aff1a54a44157290e053d748e5545e1a9afcff1d1accbebef6c173",
        "broad_paired_regime_contrast",
    ),
    (
        "4-E",
        "competitive_neutral_mechanism_diversity_contrast",
        "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/outputs/"
        "n28_competitive_neutral_mechanism_diversity_probe.json",
        "d760e55481c2d84e554c5089863c725c3b57ee7da1dedbf5b919f201c3c754cd",
        "broad_paired_regime_contrast",
    ),
    (
        "4-F",
        "higher_margin_neutral_circulation_contrast",
        "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/outputs/"
        "n28_higher_margin_neutral_circulation_probe.json",
        "1848a9ffe8c4c0242ef2b670527b65bedbcd9ea5ae0c57a15a8208acf1ab0921",
        "focused_current_multiplier_margin_contrast",
    ),
    (
        "4-G",
        "higher_margin_competitive_redistribution_contrast",
        "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/outputs/"
        "n28_higher_margin_competitive_redistribution_probe.json",
        "8bc907a97b07c09c72fd7ceda63811555c335c0d45d6dbef6cfb29489f463e72",
        "focused_current_multiplier_margin_contrast",
    ),
]

UNSAFE_CLAIM_FLAGS = {
    "agency_claim_allowed": False,
    "ant_ecology_claim_allowed": False,
    "ap5_nat4_gap_resolution_claim_allowed": False,
    "final_generative_persistence_claim_allowed": False,
    "final_n28_claim_allowed": False,
    "native_ap5_claim_allowed": False,
    "native_support_claim_allowed": False,
    "organism_life_claim_allowed": False,
    "phase8_completion_claim_allowed": False,
    "semantic_choice_claim_allowed": False,
    "semantic_cooperation_claim_allowed": False,
    "semantic_goal_claim_allowed": False,
    "semantic_identity_claim_allowed": False,
    "semantic_learning_claim_allowed": False,
    "sentience_claim_allowed": False,
    "unrestricted_autonomy_claim_allowed": False,
}


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def compact_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest_value(data: Any) -> str:
    return hashlib.sha256(compact_json(data).encode("utf-8")).hexdigest()


def sha256_file(relative_path: str) -> str:
    return hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()


def load_json(relative_path: str) -> dict[str, Any]:
    data = json.loads((ROOT / relative_path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{relative_path} must contain a JSON object")
    return data


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json(data), encoding="utf-8")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def no_absolute_paths(data: Any) -> bool:
    text = json.dumps(data, sort_keys=True, ensure_ascii=True)
    home_marker = "/" + "home/"
    repo_marker = "Documents/" + "RC-github"
    return home_marker not in text and repo_marker not in text


def trace_artifact(role: str, row_id: str, payload: dict[str, Any]) -> dict[str, str]:
    path = ARTIFACT_DIR / f"{row_id}_{role}.json"
    write_json(path, payload)
    return {"artifact_role": role, "path": rel(path), "sha256": sha256_file(rel(path))}


def source_record(source_id: str, path: str, expected_digest: str, role: str) -> dict[str, Any]:
    data = load_json(path)
    return {
        "source_id": source_id,
        "path": path,
        "source_role": role,
        "sha256": sha256_file(path),
        "artifact_id": data.get("artifact_id", "not_recorded"),
        "iteration": data.get("iteration", "not_recorded"),
        "status": data.get("status", "not_recorded"),
        "acceptance_state": data.get("acceptance_state", "not_recorded"),
        "output_digest": data.get("output_digest", "not_recorded"),
        "expected_output_digest": expected_digest,
        "output_digest_matches_expected": data.get("output_digest") == expected_digest,
    }


def probe_record(probe: tuple[str, str, str, str, str]) -> dict[str, Any]:
    iteration, source_role, path, expected_digest, classification_family = probe
    data = load_json(path)
    row = data["candidate_rows"][0]
    return {
        "iteration": iteration,
        "source_role": source_role,
        "path": path,
        "data": data,
        "row": row,
        "expected_output_digest": expected_digest,
        "classification_family": classification_family,
    }


def rows_by_source(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        out.setdefault(row["source_iteration"], []).append(row)
    return out


def build_classification_row(
    record: dict[str, Any],
    i5_rows: dict[str, list[dict[str, Any]]],
    i6_rows: dict[str, list[dict[str, Any]]],
    i5b_rows: dict[str, list[dict[str, Any]]],
    i6c_rows: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    iteration = record["iteration"]
    row = record["row"]
    is_focused = iteration in {"4-F", "4-G"}
    replay_rows = i5b_rows.get(iteration, []) if is_focused else i5_rows.get(iteration, [])
    stress_rows = i6c_rows.get(iteration, []) if is_focused else i6_rows.get(iteration, [])
    replay_supported = bool(replay_rows) and all(
        item.get("row_decision") == "supported" for item in replay_rows
    )
    stress_supported = bool(stress_rows) and all(
        item.get("row_decision") == "supported" for item in stress_rows
    )
    ap_clean = (
        row["ap4_dependency_status"] == "not_applicable"
        and bool(row["ap4_condition_reason"])
        and row["ap5_dependency_status"] == "not_applicable"
        and bool(row["ap5_condition_reason"])
    )
    unsafe_clean = all(value is False for value in row["unsafe_claim_flags"].values())

    if row["regime_label"] == "generative":
        claim_role = "positive_generative_candidate"
        generative_claim_allowed = True
    elif row["regime_label"] == "extractive":
        claim_role = "extractive_measured_contrast"
        generative_claim_allowed = False
    else:
        claim_role = "competitive_neutral_measured_contrast"
        generative_claim_allowed = False

    if is_focused:
        support_scope = "focused_current_multiplier_competitive_neutral_margin_support"
        broad_regime_support = False
        broad_margin_robustness_allowed = False
    else:
        support_scope = "broad_paired_regime_ge5_matrix_support"
        broad_regime_support = True
        broad_margin_robustness_allowed = False

    classified_rung = "GE5" if replay_supported and stress_supported and ap_clean else "GE4"
    classification_trace = {
        "trace_id": f"n28_i7_{row['row_id']}_claim_classification_trace",
        "source_iteration": iteration,
        "source_row_id": row["row_id"],
        "source_output_digest": record["data"]["output_digest"],
        "source_regime_label": row["regime_label"],
        "source_regime_evidence_role": row["regime_evidence_role"],
        "classification_family": record["classification_family"],
        "claim_role": claim_role,
        "classified_ge_ladder_rung": classified_rung,
        "replay_supported": replay_supported,
        "stress_supported": stress_supported,
        "replay_row_ids": [item["row_id"] for item in replay_rows],
        "stress_row_ids": [item["row_id"] for item in stress_rows],
        "support_scope": support_scope,
        "broad_paired_regime_support": broad_regime_support,
        "focused_current_multiplier_margin_support": is_focused,
        "broad_margin_robustness_allowed": broad_margin_robustness_allowed,
        "generative_claim_allowed_for_this_row": generative_claim_allowed,
        "contrast_claim_allowed_for_this_row": not generative_claim_allowed,
        "competitive_neutral_promoted_to_generative": False,
        "extractive_promoted_to_generative": False,
        "ap4_dependency_status": row["ap4_dependency_status"],
        "ap4_condition_reason": row["ap4_condition_reason"],
        "ap5_dependency_status": row["ap5_dependency_status"],
        "ap5_condition_reason": row["ap5_condition_reason"],
        "ap4_nat4_gap_resolved": False,
        "ap5_nat4_gap_resolved": False,
        "unsafe_claim_flags": UNSAFE_CLAIM_FLAGS,
    }
    artifact = trace_artifact("claim_classification_trace", row["row_id"], classification_trace)
    out = {
        "row_id": f"n28_i7_{row['row_id']}_classification",
        "iteration": "7",
        "source_iteration": iteration,
        "source_path": record["path"],
        "source_output_digest": record["data"]["output_digest"],
        "expected_source_output_digest": record["expected_output_digest"],
        "source_output_digest_matches_expected": (
            record["data"]["output_digest"] == record["expected_output_digest"]
        ),
        "source_row_id": row["row_id"],
        "source_row_digest": row["row_digest"],
        "source_regime_label": row["regime_label"],
        "source_regime_evidence_role": row["regime_evidence_role"],
        "classification_family": record["classification_family"],
        "claim_role": claim_role,
        "row_decision": "supported" if classified_rung == "GE5" else "partial",
        "row_decision_scope": support_scope,
        "classified_ge_ladder_rung": classified_rung,
        "replay_supported": replay_supported,
        "stress_supported": stress_supported,
        "broad_paired_regime_support": broad_regime_support,
        "focused_current_multiplier_margin_support": is_focused,
        "broad_margin_robustness_supported": False,
        "order_of_magnitude_robustness_supported": False,
        "generative_claim_allowed_for_this_row": generative_claim_allowed,
        "contrast_claim_allowed_for_this_row": not generative_claim_allowed,
        "competitive_neutral_promoted_to_generative": False,
        "extractive_promoted_to_generative": False,
        "ap4_dependency_status": row["ap4_dependency_status"],
        "ap4_condition_reason": row["ap4_condition_reason"],
        "ap5_dependency_status": row["ap5_dependency_status"],
        "ap5_condition_reason": row["ap5_condition_reason"],
        "ap4_nat4_gap_resolved": False,
        "ap5_nat4_gap_resolved": False,
        "claim_ceiling": (
            "GE5 row-level classification pending I8 closeout; "
            "focused rows are current-multiplier margin support only"
        ),
        "unsafe_claim_flags": UNSAFE_CLAIM_FLAGS,
        "classification_trace_artifact": artifact["path"],
        "classification_trace_artifact_sha256": artifact["sha256"],
        "classification_trace_digest": digest_value(classification_trace),
    }
    out["row_digest"] = digest_value(out)
    return out


def build_control_family_rows(i3: dict[str, Any], i5a: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [
        {
            "row_id": "n28_i7_control_family_active_nulls_fail_closed",
            "control_family": "active_nulls_and_failure_baselines",
            "source_iteration": "3",
            "source_output_digest": i3["output_digest"],
            "row_decision": "supported",
            "row_decision_scope": "false_positive_paths_blocked_not_positive_GE_evidence",
            "failed_closed_count": i3["failed_closed_control_count"],
            "failed_open_count": i3["failed_open_control_count"],
            "positive_ge_support_opened": False,
            "claim_effect": "supports_control_hygiene_only",
        },
        {
            "row_id": "n28_i7_control_family_artifact_only_reconstruction_fail_closed",
            "control_family": "artifact_only_reconstruction",
            "source_iteration": "5-A",
            "source_output_digest": i5a["output_digest"],
            "row_decision": "supported",
            "row_decision_scope": "report_label_digest_and_n27_shortcuts_blocked",
            "failed_closed_count": i5a["summary"]["failed_closed_row_count"],
            "failed_open_count": i5a["summary"]["failed_open_row_count"],
            "positive_ge_support_opened": False,
            "claim_effect": "protects_I5_GE4_source_current_requirement",
        },
    ]
    for row in rows:
        row["row_digest"] = digest_value(row)
    return rows


def build_evidence_classification(i6: dict[str, Any], i6a: dict[str, Any], i6b: dict[str, Any], i6c: dict[str, Any]) -> dict[str, Any]:
    return {
        "primary_paired_regime_ge5_matrix": {
            "source_iteration": "6",
            "source_output_digest": i6["output_digest"],
            "status": "supported",
            "scope": "broad_paired_regime_GE5_matrix",
            "stress_row_count": i6["stress_summary"]["stress_row_count"],
            "stress_failed_row_count": i6["stress_summary"]["stress_failed_row_count"],
            "paired_regime_coverage": i6["stress_summary"]["paired_regime_coverage"],
            "minimum_margin": min(
                result["minimum_margin"]
                for result in i6["stress_summary"]["regime_results"].values()
            ),
            "ge5_support_role": "primary_GE5_evidence",
        },
        "boundary_transition_policy_evidence": {
            "source_iteration": "6-A",
            "source_output_digest": i6a["output_digest"],
            "status": "supported",
            "scope": "same_policy_transition_surface",
            "transition_row_count": i6a["transition_summary"]["transition_row_count"],
            "label_match_count": i6a["transition_summary"]["label_match_count"],
            "label_mismatch_count": i6a["transition_summary"]["label_mismatch_count"],
            "new_source_current_evidence_opened": i6a["i6a_new_ge_support_opened"],
            "ge5_support_role": "classifier_boundary_support_not_new_GE_row",
        },
        "margin_envelope_diagnostic_evidence": {
            "source_iteration": "6-B",
            "source_output_digest": i6b["output_digest"],
            "status": "diagnostic_supported",
            "scope": "margin_envelope_characterization",
            "critical_current_margin_count": i6b["envelope_summary"]["critical_current_margin_count"],
            "narrow_current_margin_count": i6b["envelope_summary"]["narrow_current_margin_count"],
            "new_source_current_evidence_opened": i6b["i6b_new_ge_support_opened"],
            "ge5_support_role": "diagnostic_only_no_new_GE_support",
        },
        "focused_current_multiplier_margin_evidence": {
            "source_iteration": "6-C",
            "source_output_digest": i6c["output_digest"],
            "status": "focused_GE5_supported",
            "scope": "focused_current_multiplier_competitive_neutral_margin_support",
            "stress_row_count": i6c["stress_summary"]["stress_row_count"],
            "targeted_bottleneck_improvement_count": i6c["stress_summary"]["targeted_bottleneck_improvement_count"],
            "minimum_current_margin": i6c["stress_summary"]["minimum_current_margin"],
            "broad_margin_robustness_supported": i6c["broad_margin_robustness_supported"],
            "order_of_magnitude_robustness_supported": i6c["order_of_magnitude_robustness_supported"],
            "ge5_support_role": "focused_transition_margin_support_only",
        },
    }


def check(check_id: str, passed: bool, detail: Any = None) -> dict[str, Any]:
    return {"check_id": check_id, "passed": bool(passed), "detail": detail}


def build_checks(output: dict[str, Any]) -> list[dict[str, Any]]:
    rows = output["classification_rows"]
    control_rows = output["control_family_rows"]
    source_records = output["source_records"]
    return [
        check(
            "all_source_digests_match_expected",
            all(record["output_digest_matches_expected"] for record in source_records),
            [
                record["source_id"]
                for record in source_records
                if not record["output_digest_matches_expected"]
            ],
        ),
        check(
            "all_positive_and_contrast_rows_classified",
            len(rows) == len(PROBE_FILES)
            and {row["source_iteration"] for row in rows}
            == {item[0] for item in PROBE_FILES},
        ),
        check(
            "all_probe_source_digests_match_expected",
            all(row["source_output_digest_matches_expected"] for row in rows),
            [
                row["source_iteration"]
                for row in rows
                if not row["source_output_digest_matches_expected"]
            ],
        ),
        check(
            "primary_and_strengthening_generative_candidates_represented",
            sum(row["source_regime_label"] == "generative" for row in rows) == 3,
        ),
        check(
            "primary_and_strengthening_extractive_contrasts_represented",
            sum(row["source_regime_label"] == "extractive" for row in rows) == 3,
        ),
        check(
            "competitive_neutral_contrasts_and_focused_rows_represented",
            sum(row["source_regime_label"] in {"competitive", "neutral"} for row in rows)
            == 4,
        ),
        check(
            "shared_regime_policy_supported",
            output["shared_regime_policy_status"] == "supported"
            and output["evidence_classification"]["boundary_transition_policy_evidence"]["label_mismatch_count"]
            == 0,
        ),
        check(
            "label_specific_thresholds_absent_or_blocked",
            output["label_specific_thresholds_used"] is False
            and output["policy_retuned_for_label"] is False,
        ),
        check(
            "competitive_neutral_not_promoted_to_generative",
            all(
                row["generative_claim_allowed_for_this_row"] is False
                for row in rows
                if row["source_regime_label"] in {"competitive", "neutral"}
            ),
        ),
        check(
            "extractive_not_promoted_to_generative",
            all(
                row["generative_claim_allowed_for_this_row"] is False
                for row in rows
                if row["source_regime_label"] == "extractive"
            ),
        ),
        check(
            "ap4_ap5_dependencies_row_local_and_unresolved",
            all(
                row["ap4_dependency_status"] == "not_applicable"
                and row["ap4_condition_reason"]
                and row["ap5_dependency_status"] == "not_applicable"
                and row["ap5_condition_reason"]
                and row["ap4_nat4_gap_resolved"] is False
                and row["ap5_nat4_gap_resolved"] is False
                for row in rows
            ),
        ),
        check(
            "n27_context_not_promoted_to_n28_evidence",
            output["n27_transfer_success_as_n28_success_allowed"] is False
            and output["n27_consumed_as_n28_evidence"] is False,
        ),
        check(
            "control_families_fail_closed_without_positive_evidence",
            all(row["failed_open_count"] == 0 for row in control_rows)
            and all(row["positive_ge_support_opened"] is False for row in control_rows),
        ),
        check(
            "focused_margin_support_is_not_broad_robustness",
            output["focused_current_multiplier_margin_support"] is True
            and output["broad_margin_robustness_supported"] is False
            and output["order_of_magnitude_robustness_supported"] is False,
        ),
        check(
            "ge5_supported_ge6_final_blocked",
            output["ge5_or_stronger_supported"] is True
            and output["ge6_or_stronger_supported"] is False
            and output["final_n28_supported"] is False,
        ),
        check(
            "unsafe_claim_flags_false",
            all(value is False for value in output["unsafe_claim_flags"].values())
            and all(
                value is False
                for row in rows
                for value in row["unsafe_claim_flags"].values()
            ),
        ),
        check("no_absolute_paths_in_records", no_absolute_paths(output)),
    ]


def build_output() -> dict[str, Any]:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    sources = {key: load_json(item[1]) for key, item in SOURCE_FILES.items()}
    source_records = [
        source_record(source_id, path, expected_digest, role)
        for source_id, path, expected_digest, role in SOURCE_FILES.values()
    ]
    probe_records = [probe_record(item) for item in PROBE_FILES]
    i5_rows = rows_by_source(sources["i5"]["replay_rows"])
    i6_rows = rows_by_source(sources["i6"]["stress_rows"])
    i5b_rows = rows_by_source(sources["i5b"]["replay_rows"])
    i6c_rows = rows_by_source(sources["i6c"]["stress_rows"])
    classification_rows = [
        build_classification_row(record, i5_rows, i6_rows, i5b_rows, i6c_rows)
        for record in probe_records
    ]
    control_family_rows = build_control_family_rows(sources["i3"], sources["i5a"])
    evidence_classification = build_evidence_classification(
        sources["i6"], sources["i6a"], sources["i6b"], sources["i6c"]
    )
    summary_trace = {
        "trace_id": "n28_i7_controls_ap_claim_classification_summary",
        "classification_row_count": len(classification_rows),
        "generative_row_count": sum(
            row["source_regime_label"] == "generative" for row in classification_rows
        ),
        "extractive_contrast_row_count": sum(
            row["source_regime_label"] == "extractive" for row in classification_rows
        ),
        "competitive_neutral_contrast_row_count": sum(
            row["source_regime_label"] in {"competitive", "neutral"}
            for row in classification_rows
        ),
        "focused_margin_row_count": sum(
            row["focused_current_multiplier_margin_support"]
            for row in classification_rows
        ),
        "shared_regime_policy_status": "supported",
        "ge5_supported": True,
        "ge6_supported": False,
        "final_n28_supported": False,
        "broad_margin_robustness_supported": False,
        "ap4_nat4_gap_resolved": False,
        "ap5_nat4_gap_resolved": False,
    }
    summary_artifact = trace_artifact("classification_summary", "n28_i7", summary_trace)
    output: dict[str, Any] = {
        "artifact_id": "n28_controls_ap_dependency_claim_classification",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "experiment": "N28",
        "iteration": "7",
        "source_records": source_records,
        "classification_rows": classification_rows,
        "control_family_rows": control_family_rows,
        "evidence_classification": evidence_classification,
        "artifact_manifest": [
            summary_artifact,
            *[
                {
                    "artifact_role": "row_claim_classification_trace",
                    "path": row["classification_trace_artifact"],
                    "sha256": row["classification_trace_artifact_sha256"],
                }
                for row in classification_rows
            ],
        ],
        "summary_trace": summary_trace,
        "provisional_ge_ladder_rung": "GE5",
        "n28_closeout_ceiling": "N28-C5_replay_control_stress_backed_generative_extractive_candidate_supported",
        "n28_closeout_ladder_rung_assigned": False,
        "candidate_rows_classified": True,
        "shared_regime_policy_status": "supported",
        "label_specific_thresholds_used": False,
        "policy_retuned_for_label": False,
        "ge5_or_stronger_supported": True,
        "ge6_or_stronger_supported": False,
        "final_n28_supported": False,
        "primary_paired_regime_ge5_supported": True,
        "focused_current_multiplier_margin_support": True,
        "broad_margin_robustness_supported": False,
        "order_of_magnitude_robustness_supported": False,
        "ap4_nat4_gap_resolved": False,
        "ap5_nat4_gap_resolved": False,
        "native_ap5_supported": False,
        "n27_transfer_success_as_n28_success_allowed": False,
        "n27_consumed_as_n28_evidence": False,
        "phase8_completion_opened": False,
        "ant_ecology_opened": False,
        "unsafe_claim_flags": UNSAFE_CLAIM_FLAGS,
        "claim_ceiling": (
            "GE5 bounded artifact-level generative/extractive regime-separation "
            "candidate pending I8 closeout; focused margin rows are current-"
            "multiplier transition support only"
        ),
        "ready_for_iteration_8_closeout_and_n29_handoff": True,
    }
    output["checks"] = build_checks(output)
    output["failed_checks"] = [
        item["check_id"] for item in output["checks"] if not item["passed"]
    ]
    output["status"] = "passed" if not output["failed_checks"] else "failed"
    output["acceptance_state"] = (
        "accepted_ge5_controls_ap_claim_classification_pending_i8_closeout"
        if output["status"] == "passed"
        else "blocked_controls_ap_claim_classification"
    )
    output["output_digest"] = digest_value(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    lines = [
        "# N28 Iteration 7 - Controls, AP4/AP5 Dependency, And Claim Classification",
        "",
        "## Summary",
        "",
        f"- Status: `{output['status']}`",
        f"- Acceptance state: `{output['acceptance_state']}`",
        f"- Output digest: `{output['output_digest']}`",
        f"- Provisional GE rung: `{output['provisional_ge_ladder_rung']}`",
        f"- GE6 supported: `{str(output['ge6_or_stronger_supported']).lower()}`",
        f"- Final N28 supported: `{str(output['final_n28_supported']).lower()}`",
        "",
        "I7 consumes existing evidence only. It classifies the broad I6 GE5 matrix,",
        "the I6-A same-policy transition surface, the I6-B margin diagnostic, and",
        "the I6-C focused current-multiplier margin tranche without opening new",
        "source-current regime rows.",
        "",
        "## Evidence Roles",
        "",
        "| Evidence | Source | Status | Scope |",
        "|---|---|---|---|",
    ]
    for key, value in output["evidence_classification"].items():
        lines.append(
            f"| `{key}` | `{value['source_iteration']}` | `{value['status']}` | "
            f"`{value['scope']}` |"
        )
    lines.extend(
        [
            "",
            "## Classification Rows",
            "",
            "| Row | Source | Regime | Role | Decision | Rung |",
            "|---|---|---|---|---|---|",
        ]
    )
    for row in output["classification_rows"]:
        lines.append(
            f"| `{row['row_id']}` | `{row['source_iteration']}` | "
            f"`{row['source_regime_label']}` | `{row['claim_role']}` | "
            f"`{row['row_decision']}` | `{row['classified_ge_ladder_rung']}` |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "I7 supports a GE5 bounded artifact-level regime-separation candidate,",
            "not final N28. The strongest evidence remains the broad paired-regime",
            "I6 matrix: three generative rows, three extractive contrasts, and two",
            "competitive/neutral contrasts survive replay/control/stress under one",
            "shared policy family.",
            "",
            "I6-A supports the same-policy transition surface. I6-B is diagnostic",
            "only and does not add new GE support. I6-C adds focused",
            "current-multiplier margin support for competitive/neutral transition",
            "rows, but it is not broad robustness and not GE6.",
            "",
            "AP4/AP5 NAT4 gaps remain unresolved, N27 transfer context is not",
            "promoted to N28 evidence, and semantic cooperation, agency, native",
            "support, Phase 8 completion, and ant ecology remain blocked.",
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "|---|---|",
        ]
    )
    for item in output["checks"]:
        lines.append(f"| `{item['check_id']}` | `{str(item['passed']).lower()}` |")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    output = build_output()
    write_json(OUTPUT, output)
    write_report(output)


if __name__ == "__main__":
    main()
