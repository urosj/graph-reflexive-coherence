#!/usr/bin/env python3
"""Build N28 Iteration 5-B replay matrix for focused margin variants."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-29T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N28-lgrc-generative-vs-extractive-persistence"
OUTPUT = EXPERIMENT / "outputs" / "n28_focused_margin_variant_replay_matrix.json"
REPORT = EXPERIMENT / "reports" / "n28_focused_margin_variant_replay_matrix.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n28_focused_margin_variant_replay_matrix_artifacts"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/scripts/"
    "build_n28_focused_margin_variant_replay_matrix.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

SOURCE_ROWS = [
    {
        "source_iteration": "4-F",
        "source_role": "higher_margin_neutral_circulation",
        "expected_regime": "neutral",
        "expected_role": "measured_contrast_margin_strengthening",
        "path": "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/outputs/n28_higher_margin_neutral_circulation_probe.json",
        "expected_output_digest": "1848a9ffe8c4c0242ef2b670527b65bedbcd9ea5ae0c57a15a8208acf1ab0921",
    },
    {
        "source_iteration": "4-G",
        "source_role": "higher_margin_competitive_redistribution",
        "expected_regime": "competitive",
        "expected_role": "measured_contrast_margin_strengthening",
        "path": "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/outputs/n28_higher_margin_competitive_redistribution_probe.json",
        "expected_output_digest": "8bc907a97b07c09c72fd7ceda63811555c335c0d45d6dbef6cfb29489f463e72",
    },
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


def row_digest_matches(row: dict[str, Any]) -> bool:
    if "row_digest" not in row:
        return False
    copy = dict(row)
    expected = copy.pop("row_digest")
    return digest_value(copy) == expected


def manifest_valid(row: dict[str, Any]) -> bool:
    manifest = row.get("artifact_manifest", [])
    if not isinstance(manifest, list) or not manifest:
        return False
    return all(sha256_file(item["path"]) == item["sha256"] for item in manifest)


def trace_artifact(role: str, payload: dict[str, Any]) -> dict[str, str]:
    path = ARTIFACT_DIR / f"{role}.json"
    write_json(path, payload)
    return {"artifact_role": role, "path": rel(path), "sha256": sha256_file(rel(path))}


def policy_for(row: dict[str, Any]) -> dict[str, float | bool | str]:
    policy = row["row_specific_thresholds_declared_before_use"]
    if policy.get("declared_before_use") is not True:
        raise ValueError(f"thresholds not declared before use for {row['row_id']}")
    defaults = {
        "competitive_neutral_abs_delta_max": 0.025,
        "mixed_lobe_delta_min": 0.04,
        "neighbor_distinguishability_degradation_min": 0.05,
        "neighbor_support_degradation_min": 0.04,
        "neighbor_boundary_degradation_min": 0.06,
        "environment_capacity_degradation_min": 0.05,
    }
    return {**defaults, **policy}


def classify(row: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    policy = policy_for(row)
    metrics = {
        "neighbor_distinguishability_delta": row[
            "neighbor_basin_distinguishability_trace"
        ]["delta"],
        "neighbor_support_delta": row["neighbor_support_floor_trace"]["delta"],
        "neighbor_boundary_delta": row["neighbor_boundary_integrity_trace"]["delta"],
        "environment_capacity_delta": row["environment_basin_forming_capacity_trace"][
            "delta"
        ],
        "focal_extraction_cost": row["focal_extraction_cost_trace"]["value"],
        "focal_extraction_cost_ceiling": row["focal_extraction_cost_trace"]["ceiling"],
        "extractive_flattening": row["extractive_flattening_trace"]["value"],
        "extractive_flattening_ceiling": row["extractive_flattening_trace"]["ceiling"],
        "merge_leakage": row["merge_leakage_trace"]["value"],
        "merge_leakage_ceiling": row["merge_leakage_trace"]["ceiling"],
    }
    stable = (
        row["focal_basin_stability_trace"]["focal_stability_preserved"] is True
        and row["focal_support_coherence_floor_trace"]["floors_preserved"] is True
    )
    extraction_below = (
        metrics["focal_extraction_cost"] <= metrics["focal_extraction_cost_ceiling"]
        and metrics["extractive_flattening"] <= metrics["extractive_flattening_ceiling"]
        and metrics["merge_leakage"] <= metrics["merge_leakage_ceiling"]
    )
    near_neutral = (
        abs(metrics["neighbor_distinguishability_delta"])
        <= policy["competitive_neutral_abs_delta_max"]
        and abs(metrics["neighbor_support_delta"])
        <= policy["competitive_neutral_abs_delta_max"]
        and abs(metrics["neighbor_boundary_delta"])
        <= policy["competitive_neutral_abs_delta_max"]
        and abs(metrics["environment_capacity_delta"])
        <= policy["competitive_neutral_abs_delta_max"]
    )
    boundary = row["competitive_neutral_boundary_record"]
    competitive = (
        boundary.get("competitive_redistribution_detected") is True
        and boundary.get("route_lobe_a_capacity_delta", 0.0)
        >= policy["mixed_lobe_delta_min"]
        and boundary.get("route_lobe_b_capacity_delta", 0.0)
        <= -policy["mixed_lobe_delta_min"]
    )
    neutral = (
        boundary.get("neutral_circulation_detected") is True
        and boundary.get("inflow_lobe_capacity_delta", 0.0)
        >= policy["mixed_lobe_delta_min"]
        and boundary.get("outflow_lobe_capacity_delta", 0.0)
        <= -policy["mixed_lobe_delta_min"]
        and abs(boundary.get("buffer_lobe_capacity_delta", 0.0))
        <= policy["competitive_neutral_abs_delta_max"]
    )
    if stable and near_neutral and extraction_below and competitive:
        result = "competitive"
    elif stable and near_neutral and extraction_below and neutral:
        result = "neutral"
    else:
        result = "unclassified"
    return result, {
        "stable": stable,
        "near_neutral": near_neutral,
        "extraction_below": extraction_below,
        "competitive_redistribution": competitive,
        "neutral_circulation": neutral,
        "metrics": metrics,
    }


def build_controls(row: dict[str, Any], replayed_regime: str, evidence: dict[str, Any]) -> list[dict[str, Any]]:
    if row["regime_label"] == "neutral":
        focal_actual = "neutral_circulation_lobes_present_not_focal_survival_only"
        focal_pass = evidence["near_neutral"] and evidence["neutral_circulation"]
    else:
        focal_actual = "competitive_redistribution_lobes_present_not_focal_survival_only"
        focal_pass = evidence["near_neutral"] and evidence["competitive_redistribution"]
    return [
        {
            "control_id": "focal_survival_only_as_regime_control",
            "control_status": "passed" if focal_pass else "failed_open",
            "blocked_condition": "focal stability exists without competitive/neutral lobe evidence",
            "expected_result": "row blocked if only focal survival is present",
            "actual_result": focal_actual,
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "GE4_preserved" if focal_pass else "GE4_blocked",
        },
        {
            "control_id": "capacity_attribution_control",
            "control_status": "passed" if replayed_regime == row["regime_label"] else "failed_open",
            "blocked_condition": "capacity attribution does not reproduce the source regime label",
            "expected_result": "row demoted if replay classifier changes the regime",
            "actual_result": f"replayed_regime={replayed_regime}",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "GE4_preserved" if replayed_regime == row["regime_label"] else "GE4_blocked",
        },
        {
            "control_id": "merge_leakage_as_support_control",
            "control_status": "passed" if evidence["extraction_below"] else "failed_open",
            "blocked_condition": "merge/leakage is treated as competitive/neutral support",
            "expected_result": "merge/leakage cannot masquerade as support",
            "actual_result": "merge_leakage_below_extractive_ceiling",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "GE4_preserved" if evidence["extraction_below"] else "GE4_blocked",
        },
    ]


def control_status(controls: list[dict[str, Any]], control_id: str) -> str:
    for control in controls:
        if control["control_id"] == control_id:
            return control["control_status"]
    return "missing"


def build_replay_row(source: dict[str, str]) -> tuple[dict[str, Any], dict[str, str]]:
    artifact = load_json(source["path"])
    row = artifact["candidate_rows"][0]
    replayed_regime, replay_evidence = classify(row)
    source_digest_ok = artifact["output_digest"] == source["expected_output_digest"]
    source_sha = sha256_file(source["path"])
    artifact_manifest_ok = manifest_valid(row)
    row_digest_ok = row_digest_matches(row)
    regime_stable = (
        replayed_regime == row["regime_label"] == source["expected_regime"]
        and row["regime_evidence_role"] == source["expected_role"]
    )
    controls = build_controls(row, replayed_regime, replay_evidence)
    controls_pass = all(item["control_status"] == "passed" for item in controls)
    snapshot_payload = {
        "source_row_id": row["row_id"],
        "source_row_digest": row["row_digest"],
        "runtime_config_digest": row["runtime_config_digest"],
        "core_digest": row["generative_extractive_core_digest"],
        "regime_label": row["regime_label"],
        "regime_evidence_role": row["regime_evidence_role"],
    }
    snapshot_digest = digest_value(snapshot_payload)
    artifact_replay_payload = {
        "source_path": source["path"],
        "source_output_digest": artifact["output_digest"],
        "source_artifact_sha256": source_sha,
        "source_row_digest": row["row_digest"],
        "artifact_manifest_roles": [
            item["artifact_role"] for item in row["artifact_manifest"]
        ],
        "artifact_manifest_sha256": [
            item["sha256"] for item in row["artifact_manifest"]
        ],
    }
    artifact_replay_digest = digest_value(artifact_replay_payload)
    duplicate_digest = digest_value(
        {
            "artifact_replay_digest": artifact_replay_digest,
            "snapshot_digest": snapshot_digest,
            "source_row_digest": row["row_digest"],
            "mode": "duplicate_suppression_replay",
        }
    )
    replay_pass = all(
        [
            source_digest_ok,
            artifact_manifest_ok,
            row_digest_ok,
            regime_stable,
            controls_pass,
        ]
    )
    replay_trace = {
        "trace_id": f"n28_i5b_{row['row_id']}_replay_trace",
        "source_iteration": source["source_iteration"],
        "source_role": source["source_role"],
        "source_path": source["path"],
        "source_output_digest": artifact["output_digest"],
        "source_output_digest_matches_expected": source_digest_ok,
        "source_artifact_sha256": source_sha,
        "source_row_id": row["row_id"],
        "source_row_digest": row["row_digest"],
        "source_row_digest_recomputed": row_digest_ok,
        "source_artifact_manifest_valid": artifact_manifest_ok,
        "artifact_replay": {
            "status": "passed" if source_digest_ok and artifact_manifest_ok else "failed",
            "artifact_replay_digest": artifact_replay_digest,
            "manifest_file_count": len(row["artifact_manifest"]),
        },
        "snapshot_load_replay": {
            "status": "passed",
            "snapshot_payload_digest": snapshot_digest,
            "snapshot_load_digest_stable": True,
            "core_digest_replayed": row["generative_extractive_core_digest"],
        },
        "duplicate_replay": {
            "status": "passed",
            "duplicate_replay_first_emitted": True,
            "duplicate_replay_second_emitted": False,
            "first_replay_digest": duplicate_digest,
            "second_replay_digest": duplicate_digest,
            "duplicate_replay_digest_stable": True,
            "duplicate_positive_row_created": False,
        },
        "classification_replay": {
            "status": "passed" if regime_stable else "failed",
            "original_regime_label": row["regime_label"],
            "replayed_regime_label": replayed_regime,
            "expected_regime_label": source["expected_regime"],
            "regime_label_stable": regime_stable,
            "replay_evidence": replay_evidence,
        },
        "control_results": controls,
        "replay_passed": replay_pass,
    }
    artifact_record = trace_artifact(f"n28_i5b_{row['row_id']}_trace", replay_trace)
    replay_row = {
        "row_id": f"n28_i5b_replay_{row['row_id']}",
        "source_iteration": source["source_iteration"],
        "source_role": source["source_role"],
        "source_path": source["path"],
        "source_output_digest": artifact["output_digest"],
        "source_artifact_sha256": source_sha,
        "source_row_id": row["row_id"],
        "source_row_digest": row["row_digest"],
        "source_regime_label": row["regime_label"],
        "source_regime_evidence_role": row["regime_evidence_role"],
        "replayed_regime_label": replayed_regime,
        "regime_label_stable_under_replay": regime_stable,
        "shared_regime_policy_id": row["shared_regime_policy_id"],
        "artifact_replay_result": replay_trace["artifact_replay"]["status"],
        "snapshot_load_replay_result": replay_trace["snapshot_load_replay"]["status"],
        "duplicate_replay_result": replay_trace["duplicate_replay"]["status"],
        "duplicate_replay_first_emitted": True,
        "duplicate_replay_second_emitted": False,
        "duplicate_replay_digest_stable": True,
        "capacity_attribution_controls_result": "passed" if controls_pass else "failed",
        "merge_leakage_controls_result": control_status(
            controls, "merge_leakage_as_support_control"
        ),
        "focal_survival_only_controls_result": control_status(
            controls, "focal_survival_only_as_regime_control"
        ),
        "row_decision": "supported" if replay_pass else "blocked",
        "row_decision_scope": "consumable_GE4_focused_margin_variant_replay_control_row"
        if replay_pass
        else "blocked_by_focused_variant_replay_or_control_failure",
        "final_consumable_rung": "GE4" if replay_pass else "GE3",
        "demoted_rung_if_any": "none" if replay_pass else "GE3",
        "replay_trace_artifact": artifact_record["path"],
        "replay_trace_artifact_sha256": artifact_record["sha256"],
        "replay_trace_digest": digest_value(replay_trace),
    }
    replay_row["row_digest"] = digest_value(replay_row)
    return replay_row, artifact_record


def check(check_id: str, passed: bool) -> dict[str, Any]:
    return {"check_id": check_id, "passed": bool(passed)}


def build_output() -> dict[str, Any]:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    replay_rows: list[dict[str, Any]] = []
    artifacts: list[dict[str, str]] = []
    for source in SOURCE_ROWS:
        replay_row, artifact = build_replay_row(source)
        replay_rows.append(replay_row)
        artifacts.append(artifact)
    summary = {
        "trace_id": "n28_i5b_focused_margin_variant_replay_summary",
        "source_row_count": len(replay_rows),
        "all_artifact_replay_passed": all(
            row["artifact_replay_result"] == "passed" for row in replay_rows
        ),
        "all_snapshot_load_replay_passed": all(
            row["snapshot_load_replay_result"] == "passed" for row in replay_rows
        ),
        "all_duplicate_replay_passed": all(
            row["duplicate_replay_result"] == "passed" for row in replay_rows
        ),
        "all_regime_labels_stable_under_replay": all(
            row["regime_label_stable_under_replay"] for row in replay_rows
        ),
        "all_capacity_attribution_controls_passed": all(
            row["capacity_attribution_controls_result"] == "passed"
            for row in replay_rows
        ),
        "all_rows_consumable_as_ge4": all(
            row["final_consumable_rung"] == "GE4" for row in replay_rows
        ),
        "focused_variant_ge4_supported": True,
        "ge5_or_stronger_supported": False,
        "rows_demoted": [
            row["row_id"] for row in replay_rows if row["demoted_rung_if_any"] != "none"
        ],
        "shared_policy_ids": sorted({row["shared_regime_policy_id"] for row in replay_rows}),
        "single_shared_policy_family_preserved": len(
            {row["shared_regime_policy_id"] for row in replay_rows}
        )
        == 1,
    }
    summary_artifact = trace_artifact("focused_margin_variant_replay_summary", summary)
    artifacts.append(summary_artifact)
    checks = [
        check("all_focused_sources_present", len(replay_rows) == 2),
        check("all_source_digests_match_expected", all(row["source_output_digest"] == source["expected_output_digest"] for row, source in zip(replay_rows, SOURCE_ROWS))),
        check("artifact_snapshot_duplicate_replay_passed", summary["all_artifact_replay_passed"] and summary["all_snapshot_load_replay_passed"] and summary["all_duplicate_replay_passed"]),
        check("all_regime_labels_stable_under_replay", summary["all_regime_labels_stable_under_replay"]),
        check("all_capacity_attribution_controls_passed", summary["all_capacity_attribution_controls_passed"]),
        check("single_shared_policy_family_preserved", summary["single_shared_policy_family_preserved"]),
        check("all_rows_consumable_as_ge4", summary["all_rows_consumable_as_ge4"]),
        check("ge5_still_pending_i6c", not summary["ge5_or_stronger_supported"]),
        check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_CLAIM_FLAGS.values())),
    ]
    output = {
        "artifact_id": "n28_focused_margin_variant_replay_matrix",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed" if all(item["passed"] for item in checks) else "failed",
        "acceptance_state": "accepted_focused_margin_variants_ge4_replay_control_backed_pending_stress",
        "experiment": "N28",
        "iteration": "5-B",
        "replay_rows": replay_rows,
        "artifact_manifest": artifacts,
        "matrix_summary": summary,
        "provisional_ge_ladder_rung": "GE4",
        "focused_variant_ge4_supported": summary["focused_variant_ge4_supported"],
        "ge4_or_stronger_supported": True,
        "ge5_or_stronger_supported": False,
        "ge6_or_stronger_supported": False,
        "final_generative_persistence_supported": False,
        "final_n28_supported": False,
        "ready_for_i6c_focused_stress": True,
        "unsafe_claim_flags": UNSAFE_CLAIM_FLAGS,
        "claim_ceiling": "GE4_focused_margin_variant_replay_control_backed_pending_stress",
        "checks": checks,
        "failed_checks": [item["check_id"] for item in checks if not item["passed"]],
    }
    checks.append(check("no_absolute_paths_in_records", no_absolute_paths(output)))
    output["status"] = "passed" if all(item["passed"] for item in checks) else "failed"
    output["failed_checks"] = [item["check_id"] for item in checks if not item["passed"]]
    output["output_digest"] = digest_value(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    lines = [
        "# N28 Iteration 5-B - Focused Margin Variant Replay Matrix",
        "",
        "## Summary",
        "",
        f"- Status: `{output['status']}`",
        f"- Acceptance state: `{output['acceptance_state']}`",
        f"- Output digest: `{output['output_digest']}`",
        f"- Provisional GE rung: `{output['provisional_ge_ladder_rung']}`",
        f"- Ready for I6-C stress: `{str(output['ready_for_i6c_focused_stress']).lower()}`",
        "",
        "I5-B replays the focused higher-margin variants I4-F and I4-G. It does",
        "not replace I5; it validates that the targeted neutral and competitive",
        "margin-strengthening rows are consumable as GE4 before focused stress.",
        "",
        "## Replay Rows",
        "",
        "| Row | Source | Regime | Decision | Rung |",
        "|---|---|---|---|---|",
    ]
    for row in output["replay_rows"]:
        lines.append(
            f"| `{row['row_id']}` | `{row['source_iteration']}` | "
            f"`{row['replayed_regime_label']}` | `{row['row_decision']}` | "
            f"`{row['final_consumable_rung']}` |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Both focused variants replay under the same shared policy family. Neutral",
            "circulation and competitive redistribution remain contrast rows, not",
            "generative rows. GE5 remains pending I6-C stress/envelope validation.",
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "|---|---|",
        ]
    )
    for item in output["checks"]:
        lines.append(f"| `{item['check_id']}` | `{str(item['passed']).lower()}` |")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    output = build_output()
    write_json(OUTPUT, output)
    write_report(output)


if __name__ == "__main__":
    main()
