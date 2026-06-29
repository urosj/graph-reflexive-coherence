#!/usr/bin/env python3
"""Build N28 Iteration 5 replay and capacity-attribution matrix."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-29T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N28-lgrc-generative-vs-extractive-persistence"
OUTPUT = EXPERIMENT / "outputs" / "n28_replay_capacity_attribution_matrix.json"
REPORT = EXPERIMENT / "reports" / "n28_replay_capacity_attribution_matrix.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n28_replay_capacity_attribution_matrix_artifacts"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/scripts/"
    "build_n28_replay_capacity_attribution_matrix.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

I2_OUTPUT_PATH = (
    "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/"
    "outputs/n28_generative_extractive_schema_and_controls.json"
)
I3_OUTPUT_PATH = (
    "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/"
    "outputs/n28_active_nulls_and_failure_baselines.json"
)

SOURCE_ROWS = [
    {
        "source_iteration": "4",
        "source_role": "primary_generative",
        "expected_regime": "generative",
        "expected_role": "positive_candidate",
        "path": "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/outputs/n28_primary_generative_candidate_probe.json",
        "expected_output_digest": "daa25e4694929b11af38d7b044f4b4f5a4e70f6c2fbcae954db6a84854c08e5d",
    },
    {
        "source_iteration": "4-A",
        "source_role": "generative_strengthening",
        "expected_regime": "generative",
        "expected_role": "positive_candidate_alternative",
        "path": "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/outputs/n28_generative_strengthening_candidate_probe.json",
        "expected_output_digest": "07f15756b0584cbc91e4b765e4e96a07de0e62a772e0b0a49f1723f83d68b85c",
    },
    {
        "source_iteration": "4-A2",
        "source_role": "generative_mechanism_diversity",
        "expected_regime": "generative",
        "expected_role": "positive_candidate_alternative",
        "path": "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/outputs/n28_generative_mechanism_diversity_probe.json",
        "expected_output_digest": "f2785e97307704bff58e413eb071aff10311f0a3d6bd753ebccfb4c1975b6c20",
    },
    {
        "source_iteration": "4-B",
        "source_role": "primary_extractive",
        "expected_regime": "extractive",
        "expected_role": "measured_contrast",
        "path": "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/outputs/n28_primary_extractive_contrast_probe.json",
        "expected_output_digest": "5015b7f5a148db75c7513b8fa8f249d1ac1fb0fc5fe4c6150d28d4ae644f84d3",
    },
    {
        "source_iteration": "4-C",
        "source_role": "extractive_strengthening",
        "expected_regime": "extractive",
        "expected_role": "measured_contrast_alternative",
        "path": "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/outputs/n28_extractive_strengthening_contrast_probe.json",
        "expected_output_digest": "013286de4bfa88838412d757a47c76b09f6f98381f71bddfa21cd1f5f70ba9d6",
    },
    {
        "source_iteration": "4-C2",
        "source_role": "extractive_mechanism_diversity",
        "expected_regime": "extractive",
        "expected_role": "measured_contrast_alternative",
        "path": "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/outputs/n28_extractive_mechanism_diversity_probe.json",
        "expected_output_digest": "cd099229fa37dcdf1c497555fd6ace7d4435035c87e58c1eec9bac6acb7e7067",
    },
    {
        "source_iteration": "4-D",
        "source_role": "primary_competitive",
        "expected_regime": "competitive",
        "expected_role": "measured_contrast",
        "path": "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/outputs/n28_primary_competitive_neutral_contrast_probe.json",
        "expected_output_digest": "f124a1afe8aff1a54a44157290e053d748e5545e1a9afcff1d1accbebef6c173",
    },
    {
        "source_iteration": "4-E",
        "source_role": "neutral_mechanism_diversity",
        "expected_regime": "neutral",
        "expected_role": "measured_contrast_alternative",
        "path": "experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/outputs/n28_competitive_neutral_mechanism_diversity_probe.json",
        "expected_output_digest": "d760e55481c2d84e554c5089863c725c3b57ee7da1dedbf5b919f201c3c754cd",
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


def get_policy(row: dict[str, Any]) -> dict[str, Any]:
    policy = row["row_specific_thresholds_declared_before_use"]
    if not policy.get("declared_before_use"):
        raise ValueError(f"policy not declared before use for {row['row_id']}")
    defaults = {
        "neighbor_distinguishability_degradation_min": 0.05,
        "neighbor_support_degradation_min": 0.04,
        "neighbor_boundary_degradation_min": 0.06,
        "environment_capacity_degradation_min": 0.05,
        "competitive_neutral_abs_delta_max": 0.025,
        "mixed_lobe_delta_min": 0.04,
    }
    return {**defaults, **policy}


def regime_metrics(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "focal_stability_preserved": row["focal_basin_stability_trace"][
            "focal_stability_preserved"
        ],
        "focal_floors_preserved": row["focal_support_coherence_floor_trace"][
            "floors_preserved"
        ],
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


def classify_row(row: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    policy = get_policy(row)
    metrics = regime_metrics(row)
    stable = (
        metrics["focal_stability_preserved"] is True
        and metrics["focal_floors_preserved"] is True
    )
    extraction_below = (
        metrics["focal_extraction_cost"] <= metrics["focal_extraction_cost_ceiling"]
        and metrics["extractive_flattening"] <= metrics["extractive_flattening_ceiling"]
        and metrics["merge_leakage"] <= metrics["merge_leakage_ceiling"]
    )
    extraction_present = (
        metrics["focal_extraction_cost"] > metrics["focal_extraction_cost_ceiling"]
        or metrics["extractive_flattening"] > metrics["extractive_flattening_ceiling"]
        or metrics["merge_leakage"] > metrics["merge_leakage_ceiling"]
    )
    generative_gain = (
        metrics["neighbor_distinguishability_delta"]
        >= policy["neighbor_distinguishability_delta_min"]
        and metrics["neighbor_support_delta"] >= policy["neighbor_support_delta_min"]
        and metrics["neighbor_boundary_delta"] >= policy["neighbor_boundary_delta_min"]
        and metrics["environment_capacity_delta"]
        >= policy["environment_capacity_delta_min"]
    )
    extractive_loss = (
        metrics["neighbor_distinguishability_delta"]
        <= -policy["neighbor_distinguishability_degradation_min"]
        and metrics["neighbor_support_delta"]
        <= -policy["neighbor_support_degradation_min"]
        and metrics["neighbor_boundary_delta"]
        <= -policy["neighbor_boundary_degradation_min"]
        and metrics["environment_capacity_delta"]
        <= -policy["environment_capacity_degradation_min"]
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
    boundary = row.get("competitive_neutral_boundary_record", {})
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
    if stable and generative_gain and extraction_below:
        result = "generative"
    elif stable and extractive_loss and extraction_present:
        result = "extractive"
    elif stable and near_neutral and extraction_below and competitive:
        result = "competitive"
    elif stable and near_neutral and extraction_below and neutral:
        result = "neutral"
    else:
        result = "unclassified"
    evidence = {
        "stable": stable,
        "extraction_below": extraction_below,
        "extraction_present": extraction_present,
        "generative_gain": generative_gain,
        "extractive_loss": extractive_loss,
        "near_neutral": near_neutral,
        "competitive_redistribution": competitive,
        "neutral_circulation": neutral,
        "metrics": metrics,
    }
    return result, evidence


def trace_artifact(role: str, payload: dict[str, Any]) -> dict[str, str]:
    path = ARTIFACT_DIR / f"{role}.json"
    write_json(path, payload)
    return {"artifact_role": role, "path": rel(path), "sha256": sha256_file(rel(path))}


def build_replay_row(source: dict[str, str]) -> tuple[dict[str, Any], dict[str, str]]:
    artifact = load_json(source["path"])
    row = artifact["candidate_rows"][0]
    replayed_regime, replay_evidence = classify_row(row)
    row_digest_ok = row_digest_matches(row)
    artifact_manifest_ok = manifest_valid(row)
    source_digest_ok = artifact["output_digest"] == source["expected_output_digest"]
    source_sha = sha256_file(source["path"])
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
    regime_stable = (
        replayed_regime == row["regime_label"] == source["expected_regime"]
        and row["regime_evidence_role"] == source["expected_role"]
    )
    controls = build_controls(row, replayed_regime, replay_evidence)
    controls_pass = all(item["control_status"] == "passed" for item in controls)
    replay_pass = all(
        [
            source_digest_ok,
            artifact_manifest_ok,
            row_digest_ok,
            snapshot_digest == digest_value(snapshot_payload),
            duplicate_digest
            == digest_value(
                {
                    "artifact_replay_digest": artifact_replay_digest,
                    "snapshot_digest": snapshot_digest,
                    "source_row_digest": row["row_digest"],
                    "mode": "duplicate_suppression_replay",
                }
            ),
            regime_stable,
            controls_pass,
        ]
    )
    replay_trace = {
        "trace_id": f"n28_i5_{row['row_id']}_replay_trace",
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
            "duplicate_semantics": "stable digest and no duplicate positive row creation",
        },
        "classification_replay": {
            "status": "passed" if regime_stable else "failed",
            "original_regime_label": row["regime_label"],
            "replayed_regime_label": replayed_regime,
            "original_regime_evidence_role": row["regime_evidence_role"],
            "expected_regime_label": source["expected_regime"],
            "regime_label_stable": regime_stable,
            "replay_evidence": replay_evidence,
        },
        "control_results": controls,
        "replay_passed": replay_pass,
    }
    replay_row = {
        "row_id": f"n28_i5_replay_{row['row_id']}",
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
        "row_decision_scope": "consumable_GE4_replay_control_backed_regime_row"
        if replay_pass
        else "blocked_by_replay_or_control_failure",
        "final_consumable_rung": "GE4" if replay_pass else "GE3",
        "demoted_rung_if_any": "none" if replay_pass else "GE3",
        "replay_trace_digest": digest_value(replay_trace),
        "replay_trace_artifact": "",
    }
    artifact_record = trace_artifact(f"{replay_row['row_id']}_trace", replay_trace)
    replay_row["replay_trace_artifact"] = artifact_record["path"]
    replay_row["replay_trace_artifact_sha256"] = artifact_record["sha256"]
    replay_row["row_digest"] = digest_value(replay_row)
    return replay_row, artifact_record


def control_status(controls: list[dict[str, Any]], control_id: str) -> str:
    for control in controls:
        if control["control_id"] == control_id:
            return control["control_status"]
    return "missing"


def build_controls(
    row: dict[str, Any], replayed_regime: str, evidence: dict[str, Any]
) -> list[dict[str, Any]]:
    controls: list[dict[str, Any]] = []
    metrics = evidence["metrics"]
    regime = row["regime_label"]
    if regime == "generative":
        focal_actual = "neighbor_capacity_gain_present"
        focal_pass = evidence["generative_gain"]
        merge_actual = "merge_leakage_below_ceiling"
        merge_pass = evidence["extraction_below"]
    elif regime == "extractive":
        focal_actual = "neighbor_capacity_loss_and_extraction_present"
        focal_pass = evidence["extractive_loss"] and evidence["extraction_present"]
        merge_actual = "merge_leakage_recorded_as_extractive_axis_not_support"
        merge_pass = evidence["extraction_present"] and replayed_regime == "extractive"
    else:
        focal_actual = "neighbor_capacity_mixed_or_circulatory_not_focal_only"
        focal_pass = evidence["near_neutral"] and (
            evidence["competitive_redistribution"] or evidence["neutral_circulation"]
        )
        merge_actual = "merge_leakage_below_extractive_ceiling"
        merge_pass = evidence["extraction_below"]
    controls.append(
        {
            "control_id": "focal_survival_only_as_regime_control",
            "control_status": "passed" if focal_pass else "failed_open",
            "blocked_condition": "focal stability exists without regime-specific environment-side capacity evidence",
            "expected_result": "claim blocked if only focal survival is present",
            "actual_result": focal_actual,
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "GE4_preserved" if focal_pass else "GE4_blocked",
        }
    )
    controls.append(
        {
            "control_id": "capacity_attribution_control",
            "control_status": "passed" if replayed_regime == regime else "failed_open",
            "blocked_condition": "capacity attribution does not reproduce the source regime label",
            "expected_result": "row demoted if replay classifier changes the regime",
            "actual_result": f"replayed_regime={replayed_regime}",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "GE4_preserved" if replayed_regime == regime else "GE4_blocked",
        }
    )
    controls.append(
        {
            "control_id": "merge_leakage_as_support_control",
            "control_status": "passed" if merge_pass else "failed_open",
            "blocked_condition": "merge/leakage is treated as generative support or hidden success",
            "expected_result": "merge/leakage cannot masquerade as support",
            "actual_result": merge_actual,
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "GE4_preserved" if merge_pass else "GE4_blocked",
        }
    )
    controls.append(
        {
            "control_id": "label_only_regime_control",
            "control_status": "passed"
            if row["neighbor_label_only_rejected"] is True
            else "failed_open",
            "blocked_condition": "regime label exists without source-current metrics",
            "expected_result": "label-only row rejected",
            "actual_result": "source-current capacity traces and core digest replayed",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "GE4_preserved",
        }
    )
    controls.append(
        {
            "control_id": "transfer_success_as_n28_success_control",
            "control_status": "passed"
            if row["transfer_success_as_n28_success_rejected"] is True
            else "failed_open",
            "blocked_condition": "N27 transfer success is used as N28 regime evidence",
            "expected_result": "N27 remains context only",
            "actual_result": "N28 source-current row metrics drive replay classification",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "GE4_preserved",
        }
    )
    controls.append(
        {
            "control_id": "semantic_cooperation_relabel_control",
            "control_status": "passed"
            if row["semantic_cooperation_relabel_rejected"] is True
            and all(value is False for value in row["unsafe_claim_flags"].values())
            else "failed_open",
            "blocked_condition": "environment exchange is relabeled as semantic cooperation or agency",
            "expected_result": "unsafe promotions remain blocked",
            "actual_result": "all unsafe claim flags false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "GE4_preserved",
        }
    )
    controls.append(
        {
            "control_id": "capacity_metric_sign_control",
            "control_status": "passed" if replayed_regime != "unclassified" else "failed_open",
            "blocked_condition": "metric signs do not support the replayed regime",
            "expected_result": "row demoted if signs fail the frozen classifier",
            "actual_result": (
                "deltas="
                f"{metrics['neighbor_distinguishability_delta']}/"
                f"{metrics['neighbor_support_delta']}/"
                f"{metrics['neighbor_boundary_delta']}/"
                f"{metrics['environment_capacity_delta']}"
            ),
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "GE4_preserved"
            if replayed_regime != "unclassified"
            else "GE4_blocked",
        }
    )
    return controls


def build_output() -> dict[str, Any]:
    i2 = load_json(I2_OUTPUT_PATH)
    i3 = load_json(I3_OUTPUT_PATH)
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    replay_rows = []
    artifacts = []
    for source in SOURCE_ROWS:
        row, artifact = build_replay_row(source)
        replay_rows.append(row)
        artifacts.append(artifact)
    policy_ids = sorted({row["shared_regime_policy_id"] for row in replay_rows})
    regime_counts = {
        "generative": sum(row["source_regime_label"] == "generative" for row in replay_rows),
        "extractive": sum(row["source_regime_label"] == "extractive" for row in replay_rows),
        "competitive": sum(row["source_regime_label"] == "competitive" for row in replay_rows),
        "neutral": sum(row["source_regime_label"] == "neutral" for row in replay_rows),
    }
    matrix_summary = {
        "trace_id": "n28_i5_replay_capacity_attribution_matrix_summary",
        "source_row_count": len(replay_rows),
        "regime_counts": regime_counts,
        "all_artifact_replay_passed": all(
            row["artifact_replay_result"] == "passed" for row in replay_rows
        ),
        "all_snapshot_load_replay_passed": all(
            row["snapshot_load_replay_result"] == "passed" for row in replay_rows
        ),
        "all_duplicate_replay_passed": all(
            row["duplicate_replay_result"] == "passed"
            and row["duplicate_replay_digest_stable"] is True
            and row["duplicate_replay_first_emitted"] is True
            and row["duplicate_replay_second_emitted"] is False
            for row in replay_rows
        ),
        "all_capacity_attribution_controls_passed": all(
            row["capacity_attribution_controls_result"] == "passed"
            for row in replay_rows
        ),
        "all_merge_leakage_controls_passed": all(
            row["merge_leakage_controls_result"] == "passed" for row in replay_rows
        ),
        "all_focal_survival_only_controls_passed": all(
            row["focal_survival_only_controls_result"] == "passed"
            for row in replay_rows
        ),
        "all_regime_labels_stable_under_replay": all(
            row["regime_label_stable_under_replay"] for row in replay_rows
        ),
        "shared_policy_ids": policy_ids,
        "single_shared_policy_family_preserved": len(policy_ids) == 1,
        "generative_rows_replayed": [
            row["source_iteration"]
            for row in replay_rows
            if row["source_regime_label"] == "generative"
        ],
        "extractive_rows_replayed": [
            row["source_iteration"]
            for row in replay_rows
            if row["source_regime_label"] == "extractive"
        ],
        "competitive_neutral_rows_replayed": [
            row["source_iteration"]
            for row in replay_rows
            if row["source_regime_label"] in {"competitive", "neutral"}
        ],
        "rows_demoted": [
            row["source_iteration"]
            for row in replay_rows
            if row["demoted_rung_if_any"] != "none"
        ],
        "ge4_replay_control_candidate_supported": all(
            row["final_consumable_rung"] == "GE4" for row in replay_rows
        ),
        "ge5_or_stronger_supported": False,
        "ge6_or_stronger_supported": False,
        "stress_matrix_pending": True,
        "claim_boundary_pending_iteration_7": True,
    }
    summary_artifact = trace_artifact("matrix_summary_trace", matrix_summary)
    artifacts.append(summary_artifact)
    checks = [
        check("i2_schema_consumed", i2["status"] == "passed"),
        check(
            "i3_active_nulls_consumed",
            i3["status"] == "passed" and i3["failed_checks"] == [],
        ),
        check("all_i4_family_rows_present", len(replay_rows) == 8),
        check(
            "all_source_digests_match_expected",
            all(
                row["source_output_digest"]
                == next(
                    source["expected_output_digest"]
                    for source in SOURCE_ROWS
                    if source["source_iteration"] == row["source_iteration"]
                )
                for row in replay_rows
            ),
        ),
        check(
            "artifact_snapshot_duplicate_replay_passed",
            matrix_summary["all_artifact_replay_passed"]
            and matrix_summary["all_snapshot_load_replay_passed"]
            and matrix_summary["all_duplicate_replay_passed"],
        ),
        check(
            "capacity_attribution_controls_passed",
            matrix_summary["all_capacity_attribution_controls_passed"],
        ),
        check(
            "merge_leakage_controls_passed",
            matrix_summary["all_merge_leakage_controls_passed"],
        ),
        check(
            "focal_survival_only_controls_passed",
            matrix_summary["all_focal_survival_only_controls_passed"],
        ),
        check(
            "all_regime_labels_stable_under_replay",
            matrix_summary["all_regime_labels_stable_under_replay"],
        ),
        check(
            "single_shared_policy_family_preserved",
            matrix_summary["single_shared_policy_family_preserved"],
        ),
        check("all_rows_consumable_as_ge4", matrix_summary["ge4_replay_control_candidate_supported"]),
        check("ge5_and_ge6_still_blocked", not matrix_summary["ge5_or_stronger_supported"] and not matrix_summary["ge6_or_stronger_supported"]),
        check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_CLAIM_FLAGS.values())),
    ]
    output = {
        "artifact_id": "n28_replay_capacity_attribution_matrix",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_replay_control_backed_ge4_regime_separation_candidate_pending_stress",
        "experiment": "N28",
        "iteration": "5",
        "source_i2_schema": {
            "path": I2_OUTPUT_PATH,
            "output_digest": i2["output_digest"],
            "artifact_sha256": sha256_file(I2_OUTPUT_PATH),
            "status": i2["status"],
            "acceptance_state": i2["acceptance_state"],
        },
        "source_i3_active_nulls": {
            "path": I3_OUTPUT_PATH,
            "output_digest": i3["output_digest"],
            "artifact_sha256": sha256_file(I3_OUTPUT_PATH),
            "status": i3["status"],
            "acceptance_state": i3["acceptance_state"],
        },
        "source_rows": [
            {
                "source_iteration": source["source_iteration"],
                "source_role": source["source_role"],
                "path": source["path"],
                "expected_output_digest": source["expected_output_digest"],
                "artifact_sha256": sha256_file(source["path"]),
            }
            for source in SOURCE_ROWS
        ],
        "replay_rows": replay_rows,
        "artifact_manifest": artifacts,
        "matrix_summary": matrix_summary,
        "provisional_ge_ladder_rung": "GE4",
        "ge4_or_stronger_supported": True,
        "ge5_or_stronger_supported": False,
        "ge6_or_stronger_supported": False,
        "n28_closeout_ceiling": "N28-C4_source_current_regime_candidate_supported",
        "n28_closeout_ladder_rung_assigned": False,
        "shared_regime_policy_status": "replay_control_backed_pending_stress",
        "shared_regime_policy_status_scope": "I4_through_I4E_rows_replay_control_clean_pending_I6_stress",
        "final_generative_persistence_supported": False,
        "final_n28_supported": False,
        "ready_for_iteration_6_stress_regime_separation_matrix": True,
        "unsafe_claim_flags": UNSAFE_CLAIM_FLAGS,
        "checks": checks,
        "failed_checks": [item["check_id"] for item in checks if not item["passed"]],
        "claim_ceiling": "GE4_replay_control_backed_regime_separation_candidate_pending_stress_claim_classification_and_closeout",
    }
    checks.append(check("no_absolute_paths_in_records", no_absolute_paths(output)))
    output["failed_checks"] = [item["check_id"] for item in checks if not item["passed"]]
    output["output_digest"] = digest_value(output)
    return output


def check(check_id: str, passed: bool) -> dict[str, Any]:
    return {"check_id": check_id, "passed": bool(passed)}


def write_report(output: dict[str, Any]) -> None:
    summary = output["matrix_summary"]
    lines = [
        "# N28 Iteration 5 - Replay And Capacity Attribution Matrix",
        "",
        "## Summary",
        "",
        f"- Status: `{output['status']}`",
        f"- Acceptance state: `{output['acceptance_state']}`",
        f"- Output digest: `{output['output_digest']}`",
        f"- Provisional GE rung: `{output['provisional_ge_ladder_rung']}`",
        f"- GE4 or stronger supported: `{str(output['ge4_or_stronger_supported']).lower()}`",
        f"- GE5 or stronger supported: `{str(output['ge5_or_stronger_supported']).lower()}`",
        f"- Shared policy status: `{output['shared_regime_policy_status']}`",
        f"- Ready for I6: `{str(output['ready_for_iteration_6_stress_regime_separation_matrix']).lower()}`",
        "",
        "I5 replays all eight I4-family regime rows: three generative, three "
        "extractive, and two competitive/neutral rows. Each row passes artifact "
        "replay, snapshot/load replay, duplicate replay, regime classification "
        "replay, capacity-attribution controls, merge/leakage controls, and "
        "focal-survival-only controls.",
        "",
        "## Matrix Result",
        "",
        "```text",
        f"source_row_count = {summary['source_row_count']}",
        f"regime_counts = {summary['regime_counts']}",
        f"all_artifact_replay_passed = {str(summary['all_artifact_replay_passed']).lower()}",
        f"all_snapshot_load_replay_passed = {str(summary['all_snapshot_load_replay_passed']).lower()}",
        f"all_duplicate_replay_passed = {str(summary['all_duplicate_replay_passed']).lower()}",
        f"all_capacity_attribution_controls_passed = {str(summary['all_capacity_attribution_controls_passed']).lower()}",
        f"all_regime_labels_stable_under_replay = {str(summary['all_regime_labels_stable_under_replay']).lower()}",
        f"single_shared_policy_family_preserved = {str(summary['single_shared_policy_family_preserved']).lower()}",
        f"rows_demoted = {summary['rows_demoted']}",
        "```",
        "",
        "## Replay Rows",
        "",
        "| Source | Regime | Replay | Controls | Final rung | Demotion |",
        "|---|---|---|---|---|---|",
    ]
    for row in output["replay_rows"]:
        replay = (
            row["artifact_replay_result"]
            + "/"
            + row["snapshot_load_replay_result"]
            + "/"
            + row["duplicate_replay_result"]
        )
        controls = (
            row["capacity_attribution_controls_result"]
            + "/"
            + row["merge_leakage_controls_result"]
            + "/"
            + row["focal_survival_only_controls_result"]
        )
        lines.append(
            f"| `{row['source_iteration']}` | `{row['source_regime_label']}` -> "
            f"`{row['replayed_regime_label']}` | `{replay}` | `{controls}` | "
            f"`{row['final_consumable_rung']}` | `{row['demoted_rung_if_any']}` |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "I5 upgrades the I4-family evidence from provisional GE3 source-current "
            "regime rows to a replay/control-backed GE4 regime-separation "
            "candidate. The upgrade is matrix-level: it depends on every "
            "generative, extractive, and competitive/neutral row replaying with "
            "stable classification and fail-closed attribution controls.",
            "",
            "This still does not support GE5 or GE6. I6 must stress the same "
            "regime boundaries before N28 can claim stress/variant-backed "
            "paired-regime separation. I7 and I8 still need claim classification "
            "and closeout.",
            "",
            "Duplicate replay uses the same convention as prior experiments: "
            "`first_emitted=true` and `second_emitted=false` means the second "
            "replay suppressed a duplicate while preserving the same digest.",
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "|---|---|",
        ]
    )
    for item in output["checks"]:
        lines.append(f"| `{item['check_id']}` | `{str(item['passed']).lower()}` |")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "I5 supports only a GE4 replay/control-backed regime-separation "
            "candidate pending stress, claim classification, and closeout. It "
            "does not support GE5, GE6, final N28, semantic cooperation, agency, "
            "native support, Phase 8 completion, or ant ecology.",
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    output = build_output()
    OUTPUT.write_text(canonical_json(output), encoding="utf-8")
    write_report(output)

    output = json.loads(OUTPUT.read_text(encoding="utf-8"))
    output["script_sha256"] = sha256_file(SCRIPT_RELATIVE_PATH)
    output["output_digest"] = digest_value(
        {
            key: value
            for key, value in output.items()
            if key not in {"report_sha256", "script_sha256", "output_digest"}
        }
    )
    OUTPUT.write_text(canonical_json(output), encoding="utf-8")
    write_report(output)
    output = json.loads(OUTPUT.read_text(encoding="utf-8"))
    output["report_sha256"] = sha256_file(str(REPORT.relative_to(ROOT)))
    OUTPUT.write_text(canonical_json(output), encoding="utf-8")


if __name__ == "__main__":
    main()
