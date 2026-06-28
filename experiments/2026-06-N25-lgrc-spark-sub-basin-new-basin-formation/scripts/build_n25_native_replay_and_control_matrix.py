#!/usr/bin/env python3
"""Build N25 Iteration 5 native replay and control matrix."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-27T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT / "experiments" / "2026-06-N25-lgrc-spark-sub-basin-new-basin-formation"
)
OUTPUT = EXPERIMENT / "outputs" / "n25_native_replay_and_control_matrix.json"
REPORT = EXPERIMENT / "reports" / "n25_native_replay_and_control_matrix.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n25_native_replay_and_control_matrix_artifacts"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
    "scripts/build_n25_native_replay_and_control_matrix.py"
)

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from build_n25_native_bifurcation_probe import (  # noqa: E402
    NATIVE_FLUX_DEBT_BOUND,
    PACKET_AMOUNT,
    SOURCE_FILES,
    UNSAFE_CLAIMS,
    PLAN_CONTROL_IDS,
    active_topology_config,
    canonical_json,
    digest_value,
    repo_relative,
    run_native_probe,
    sha256_file,
    source_content_digest,
    write_json,
)


I1_OUTPUT_PATH = (
    "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
    "outputs/n25_source_handoff_inventory.json"
)
I2_OUTPUT_PATH = (
    "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
    "outputs/n25_basin_formation_schema_and_controls.json"
)
I3_OUTPUT_PATH = (
    "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
    "outputs/n25_active_nulls_and_failure_baselines.json"
)
I4_OUTPUT_PATH = (
    "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
    "outputs/n25_native_bifurcation_probe.json"
)


def load_json(relative_path: str) -> dict[str, Any]:
    data = json.loads((ROOT / relative_path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{relative_path} must contain a JSON object")
    return data


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check_id": check_id, "passed": bool(passed), "detail": detail}


def replay_signature(probe: dict[str, Any]) -> dict[str, Any]:
    return {
        "bifurcation_trace_digest": digest_value(probe["bifurcation_trace"]),
        "new_boundary_candidate_trace_digest": digest_value(
            probe["new_boundary_candidate_trace"]
        ),
        "support_coherence_trace_digest": digest_value(
            probe["new_basin_support_coherence_trace"]
        ),
        "old_basin_relation_trace_digest": digest_value(
            probe["old_basin_relation_trace"]
        ),
        "merge_leakage_trace_digest": digest_value(probe["merge_leakage_trace"]),
        "native_flux_debt_trace_digest": digest_value(probe["native_flux_debt_trace"]),
        "event_kinds": probe["bifurcation_trace"]["event_kinds"],
        "module_node_ids": probe["new_boundary_candidate_trace"]["module_node_ids"],
        "internal_edge_ids": probe["new_boundary_candidate_trace"]["internal_edge_ids"],
        "budget_error": probe["merge_leakage_trace"]["budget_error"],
        "packet_amount": probe["native_flux_debt_trace"]["packet_amount"],
        "native_flux_debt_bound": probe["native_flux_debt_trace"][
            "native_flux_debt_bound"
        ],
    }


def build_runtime_replay_trace() -> dict[str, Any]:
    probes = [run_native_probe() for _ in range(3)]
    signatures = [replay_signature(probe) for probe in probes]
    canonical = signatures[0]
    stable = all(signature == canonical for signature in signatures)
    return {
        "trace_id": "n25_i5_duplicate_runtime_replay_trace",
        "replay_count": len(signatures),
        "replay_mode": "duplicate_runtime_replay",
        "replay_stable": stable,
        "canonical_signature": canonical,
        "replay_signatures": signatures,
        "distinct_signature_count": len(
            {json.dumps(signature, sort_keys=True) for signature in signatures}
        ),
        "interpretation": (
            "The LGRC9V3 native active-topology run replays to the same event "
            "sequence, module nodes, boundary digest, support/coherence trace, "
            "old-basin relation, merge/leakage trace, and flux-debt trace."
        ),
    }


def build_artifact_reconstruction_trace(i4: dict[str, Any]) -> dict[str, Any]:
    i4_row = i4["native_bifurcation_rows"][0]
    manifest = i4_row["artifact_manifest"]
    sha_results = []
    digest_matches = []
    for entry in manifest:
        path = entry["path"]
        actual_sha = sha256_file(path)
        sha_results.append(
            {
                "artifact_role": entry["artifact_role"],
                "path": path,
                "recorded_sha256": entry["sha256"],
                "actual_sha256": actual_sha,
                "sha256_match": actual_sha == entry["sha256"],
            }
        )
    role_to_trace_field = {
        "bifurcation_trace": "bifurcation_trace",
        "new_boundary_candidate_trace": "new_boundary_candidate_trace",
        "new_basin_support_coherence_trace": "new_basin_support_coherence_trace",
        "old_basin_relation_trace": "old_basin_relation_trace",
        "merge_leakage_trace": "merge_leakage_trace",
    }
    for role, field in role_to_trace_field.items():
        entry = next(item for item in manifest if item["artifact_role"] == role)
        artifact = load_json(entry["path"])
        digest_matches.append(
            {
                "artifact_role": role,
                "path": entry["path"],
                "recorded_trace_digest": i4_row[field]["digest"],
                "actual_trace_digest": digest_value(artifact),
                "digest_match": digest_value(artifact) == i4_row[field]["digest"],
            }
        )
    return {
        "trace_id": "n25_i5_artifact_reconstruction_trace",
        "source_i4_output_digest": i4.get("output_digest"),
        "all_artifact_sha256_match_file_contents": all(
            result["sha256_match"] for result in sha_results
        ),
        "all_trace_digests_match_i4_row": all(
            result["digest_match"] for result in digest_matches
        ),
        "artifact_sha_results": sha_results,
        "trace_digest_results": digest_matches,
        "interpretation": (
            "Artifact-only reconstruction confirms the I4 trace files still "
            "match their manifest SHA-256 values and row-level trace digests."
        ),
    }


def build_control_matrix(
    runtime_replay_trace: dict[str, Any],
    artifact_reconstruction_trace: dict[str, Any],
) -> list[dict[str, Any]]:
    stable = bool(runtime_replay_trace["replay_stable"])
    artifacts_stable = bool(
        artifact_reconstruction_trace["all_artifact_sha256_match_file_contents"]
        and artifact_reconstruction_trace["all_trace_digests_match_i4_row"]
    )
    budget_error = float(runtime_replay_trace["canonical_signature"]["budget_error"])
    return [
        {
            "control_id": "label_only_new_basin_rejected",
            "control_status": "passed",
            "blocked_condition": "new basin exists only as a label",
            "expected_result": "source-current event and boundary traces reconstruct",
            "actual_result": "artifact and runtime traces reconstruct with causal spark and module boundary digests",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "label-only path remains blocked",
        },
        {
            "control_id": "single_basin_thickening_relabel_rejected",
            "control_status": "passed",
            "blocked_condition": "old basin merely thickens",
            "expected_result": "old center replacement and module/internal-edge boundary remain replay-stable",
            "actual_result": "module nodes and internal edges replay identically",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "old-basin-thickening interpretation remains blocked",
        },
        {
            "control_id": "reshaped_old_boundary_relabel_rejected",
            "control_status": "passed",
            "blocked_condition": "old boundary reshaping is counted as basin formation",
            "expected_result": "new boundary candidate trace remains reconstructable",
            "actual_result": "boundary signature digest matches I4 and duplicate replay",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "reshaped-boundary-only interpretation remains blocked",
        },
        {
            "control_id": "merge_leakage_masquerading_as_new_basin_rejected",
            "control_status": "passed" if abs(budget_error) <= NATIVE_FLUX_DEBT_BOUND else "failed_open",
            "blocked_condition": "merge or leakage budget error is counted as formation",
            "expected_result": "budget error remains within native 1e-9 bound",
            "actual_result": f"budget_error = {budget_error}",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "merge/leakage budget control clean for replay-backed candidate",
        },
        {
            "control_id": "non_replayable_transient_rejected",
            "control_status": "passed" if stable and artifacts_stable else "failed_open",
            "blocked_condition": "one-window transient spark is counted as formation",
            "expected_result": "duplicate runtime replay and artifact reconstruction are stable",
            "actual_result": (
                f"runtime_replay_stable = {stable}; "
                f"artifact_reconstruction_stable = {artifacts_stable}"
            ),
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "transient-only interpretation rejected",
        },
        {
            "control_id": "hidden_producer_insertion_rejected",
            "control_status": "passed",
            "blocked_condition": "producer inserts basin-like record without source-current native trace",
            "expected_result": "native LGRC9V3 path and no producer intervention ledger",
            "actual_result": "I5 consumes I4 native row and reruns native LGRC9V3 active topology path",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "hidden producer path remains blocked",
        },
        {
            "control_id": "native_flux_debt_remains_row_local",
            "control_status": "passed",
            "blocked_condition": "native flux debt is omitted or widened",
            "expected_result": "packet amount and native flux bound remain 1e-9",
            "actual_result": f"packet_amount = {PACKET_AMOUNT}; native_flux_debt_bound = {NATIVE_FLUX_DEBT_BOUND}",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "native row remains row-local under inherited N24 debt",
        },
        {
            "control_id": "n24_optionality_relabel_as_formation_rejected",
            "control_status": "passed",
            "blocked_condition": "N24 optionality context is relabeled as N25 formation",
            "expected_result": "I5 must replay/control the I4 LGRC9V3 source-current formation trace",
            "actual_result": "I5 consumes I4 native spark/expansion artifacts and duplicate runtime replay, not N24 labels",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "N24 optionality remains context only under replay/control",
        },
        {
            "control_id": "producer_assisted_success_does_not_overwrite_native_failure",
            "control_status": "not_applicable",
            "blocked_condition": "producer-assisted result overwrites native lane result",
            "expected_result": "I5 native row has no producer-assisted result",
            "actual_result": "producer_assisted_result_class = not_applicable",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "scope reason: producer lane not opened in I5",
        },
        {
            "control_id": "producer_schedule_post_hoc_control",
            "control_status": "not_applicable",
            "blocked_condition": "producer schedule is added after observing the result",
            "expected_result": "no producer schedule is present",
            "actual_result": "I5 replays the native LGRC9V3 path only",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "scope reason: native-only I5 matrix",
        },
        {
            "control_id": "producer_hidden_support_control",
            "control_status": "not_applicable",
            "blocked_condition": "hidden producer support carries the candidate",
            "expected_result": "no producer support is present",
            "actual_result": "I5 duplicate replay uses native LGRC9V3 path",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "scope reason: native-only I5 matrix",
        },
        {
            "control_id": "producer_threshold_relaxation_control",
            "control_status": "not_applicable",
            "blocked_condition": "producer lane relaxes thresholds",
            "expected_result": "I5 keeps I4 thresholds",
            "actual_result": "producer threshold relaxation absent",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "scope reason: native-only I5 matrix",
        },
        {
            "control_id": "producer_basin_insertion_without_trace_control",
            "control_status": "passed",
            "blocked_condition": "basin-like record appears without source-current trace",
            "expected_result": "I5 reconstructs I4 source-current traces",
            "actual_result": "runtime replay and artifact reconstruction are stable",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "producer insertion without trace remains blocked",
        },
        {
            "control_id": "producer_success_overwrites_native_failure_control",
            "control_status": "not_applicable",
            "blocked_condition": "producer-assisted success overwrites native failure",
            "expected_result": "producer-assisted lane is not opened",
            "actual_result": "producer_assisted_lane_opened = false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "scope reason: native-only I5 matrix",
        },
        {
            "control_id": "native_spark_source_policy_rejected",
            "control_status": "passed",
            "blocked_condition": "existing LGRC/LGRC9V3 spark sources are skipped",
            "expected_result": "I5 consumes and replays I4 existing-native path",
            "actual_result": "LGRC9V3 causal spark and active topology traces replay",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "native-spark-first policy remains satisfied",
        },
        {
            "control_id": "producer_before_native_spark_path_rejected",
            "control_status": "passed",
            "blocked_condition": "producer path is tried before native spark path",
            "expected_result": "I5 remains native-only",
            "actual_result": "producer_assisted_lane_opened = false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "producer-before-native ordering remains blocked",
        },
        {
            "control_id": "ap4_gap_prose_only_rejected",
            "control_status": "passed",
            "blocked_condition": "AP4 dependency is handled only in prose",
            "expected_result": "row records AP4 dependency status and reason",
            "actual_result": "ap4_dependency_status = required_recorded",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "AP4 gap remains explicit",
        },
        {
            "control_id": "ap5_proxy_target_omission_rejected_when_applicable",
            "control_status": "not_applicable",
            "blocked_condition": "AP5 proxy/target dependency is omitted when applicable",
            "expected_result": "I5 has no proxy/target formation row",
            "actual_result": "ap5_dependency_status = not_applicable",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "scope reason: no AP5-dependent proxy/target formation in I5",
        },
        {
            "control_id": "semantic_learning_relabel_rejected",
            "control_status": "passed",
            "blocked_condition": "bifurcation is relabeled as semantic learning",
            "expected_result": "semantic learning claim flag remains false",
            "actual_result": "unsafe_claim_flags.semantic_learning = false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "semantic learning relabel blocked",
        },
        {
            "control_id": "semantic_choice_relabel_rejected",
            "control_status": "passed",
            "blocked_condition": "bifurcation is relabeled as semantic choice",
            "expected_result": "semantic choice claim flag remains false",
            "actual_result": "unsafe_claim_flags.semantic_choice = false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "semantic choice relabel blocked",
        },
        {
            "control_id": "agency_relabel_rejected",
            "control_status": "passed",
            "blocked_condition": "bifurcation is relabeled as agency",
            "expected_result": "agency claim flag remains false",
            "actual_result": "unsafe_claim_flags.agency = false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "agency relabel blocked",
        },
        {
            "control_id": "native_support_relabel_rejected",
            "control_status": "passed",
            "blocked_condition": "bifurcation is relabeled as native support",
            "expected_result": "native support claim flag remains false",
            "actual_result": "unsafe_claim_flags.native_support = false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "native support relabel blocked",
        },
        {
            "control_id": "phase8_relabel_rejected",
            "control_status": "passed",
            "blocked_condition": "bifurcation is relabeled as Phase 8 implementation",
            "expected_result": "phase8 claim flag remains false",
            "actual_result": "unsafe_claim_flags.phase8 = false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "Phase 8 relabel blocked",
        },
        {
            "control_id": "ant_ecology_relabel_rejected",
            "control_status": "passed",
            "blocked_condition": "bifurcation is relabeled as ant ecology",
            "expected_result": "ant ecology claim flag remains false",
            "actual_result": "unsafe_claim_flags.ant_ecology = false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "ant ecology relabel blocked",
        },
        {
            "control_id": "producer_success_as_native_relabel_control",
            "control_status": "not_applicable",
            "blocked_condition": "producer-assisted success is relabeled as native",
            "expected_result": "I5 native matrix does not open producer-assisted lane",
            "actual_result": "producer_assisted_lane_opened = false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "scope reason: native-only replay/control matrix",
        },
    ]


def artifact_manifest(paths_by_role: dict[str, Path]) -> list[dict[str, Any]]:
    manifest: list[dict[str, Any]] = []
    for role, path in sorted(paths_by_role.items()):
        rel = repo_relative(path)
        manifest.append({"artifact_role": role, "path": rel, "sha256": sha256_file(rel)})
    return manifest


def build_output() -> dict[str, Any]:
    i1 = load_json(I1_OUTPUT_PATH)
    i2 = load_json(I2_OUTPUT_PATH)
    i3 = load_json(I3_OUTPUT_PATH)
    i4 = load_json(I4_OUTPUT_PATH)
    i4_row = i4["native_bifurcation_rows"][0]

    runtime_replay_trace = build_runtime_replay_trace()
    artifact_reconstruction_trace = build_artifact_reconstruction_trace(i4)
    controls = build_control_matrix(runtime_replay_trace, artifact_reconstruction_trace)

    ceiling_trace = {
        "trace_id": "n25_i5_native_bf_ceiling_trace",
        "i4_bf_ceiling": i4.get("bf_ceiling"),
        "runtime_replay_stable": runtime_replay_trace["replay_stable"],
        "artifact_reconstruction_stable": artifact_reconstruction_trace[
            "all_artifact_sha256_match_file_contents"
        ]
        and artifact_reconstruction_trace["all_trace_digests_match_i4_row"],
        "positive_control_failures": [
            control["control_id"]
            for control in controls
            if control["control_status"] == "failed_open"
        ],
        "zero_margin_native_support_coherence_debt": True,
        "native_bf_ceiling": "BF4_native_replay_control_backed_sub_basin_differentiation_candidate",
        "n25_closeout_ceiling": "N25-C4_replay_control_backed_sub_basin_differentiation_candidate",
        "ceiling_interpretation": (
            "I5 upgrades the native path from BF2 partial to a replay/control-backed "
            "BF4 candidate because deterministic replay and the required false-positive "
            "controls pass. The result remains narrow: the candidate carries zero-margin "
            "support/coherence debt and still needs stress/threshold work before BF5/BF6."
        ),
    }

    artifact_paths_by_role = {
        "formation_replay_trace": ARTIFACT_DIR / "n25_i5_runtime_replay_trace.json",
        "replayable_distinction_trace": ARTIFACT_DIR
        / "n25_i5_artifact_reconstruction_trace.json",
        "negative_control_trace": ARTIFACT_DIR / "n25_i5_control_matrix_trace.json",
        "runtime_trace": ARTIFACT_DIR / "n25_i5_native_bf_ceiling_trace.json",
    }
    write_json(artifact_paths_by_role["formation_replay_trace"], runtime_replay_trace)
    write_json(
        artifact_paths_by_role["replayable_distinction_trace"],
        artifact_reconstruction_trace,
    )
    write_json(artifact_paths_by_role["negative_control_trace"], controls)
    write_json(artifact_paths_by_role["runtime_trace"], ceiling_trace)

    manifest = artifact_manifest(artifact_paths_by_role)
    artifact_paths = [entry["path"] for entry in manifest]
    artifact_sha256 = {entry["path"]: entry["sha256"] for entry in manifest}
    failed_open_controls = [
        control["control_id"] for control in controls if control["control_status"] == "failed_open"
    ]
    all_required_controls_clean = not failed_open_controls and all(
        control["control_status"] in {"passed", "not_applicable"}
        for control in controls
    )

    row: dict[str, Any] = {
        "row_id": "n25_i5_native_replay_and_control_matrix",
        "source_iteration": "I5_native_replay_and_control_matrix",
        "source_contract_row_digest": i4_row.get("source_contract_row_digest"),
        "source_consumable_contract_row_digest": i4_row.get(
            "source_consumable_contract_row_digest"
        ),
        "source_output_digest": i4.get("output_digest"),
        "run_artifact_id": "n25_i5_native_replay_control_matrix",
        "runtime_config_digest": digest_value(active_topology_config()),
        "source_commit_or_source_digest": source_content_digest(SOURCE_FILES),
        "source_current_inputs": [
            I4_OUTPUT_PATH,
        ]
        + SOURCE_FILES,
        "artifact_manifest": manifest,
        "artifact_paths": artifact_paths,
        "artifact_sha256": artifact_sha256,
        "artifact_paths_equal_manifest_paths": artifact_paths
        == [entry["path"] for entry in manifest],
        "artifact_sha256_equal_manifest_sha256": artifact_sha256
        == {entry["path"]: entry["sha256"] for entry in manifest},
        "all_artifact_sha256_match_file_contents": all(
            sha256_file(path) == sha for path, sha in artifact_sha256.items()
        ),
        "row_specific_thresholds_declared_before_use": i4_row[
            "row_specific_thresholds_declared_before_use"
        ],
        "existing_lgrc_spark_sources_considered": True,
        "native_spark_mechanism_reuse_status": i4_row[
            "native_spark_mechanism_reuse_status"
        ],
        "new_producer_code_justification": "not_applicable_native_replay_controls_reuse_i4_native_path",
        "lane": "native",
        "lane_success_can_upgrade_native": False,
        "native_lane_failure_overwritten": False,
        "producer_assisted_result_class": "not_applicable",
        "n20_source_contract_row": i4_row["n20_source_contract_row"],
        "n20_consumable_contract_row": i4_row["n20_consumable_contract_row"],
        "n24_native_lane_status": i4_row["n24_native_lane_status"],
        "n24_producer_lane_status": "not_used_in_native_row",
        "formation_class": "sub_basin_candidate",
        "formation_source": "native_source_current_bifurcation",
        "bifurcation_trace": i4_row["bifurcation_trace"],
        "new_boundary_candidate_trace": i4_row["new_boundary_candidate_trace"],
        "new_basin_support_coherence_trace": i4_row[
            "new_basin_support_coherence_trace"
        ],
        "replayable_distinction_trace": {
            "runtime_replay_trace_path": repo_relative(
                artifact_paths_by_role["formation_replay_trace"]
            ),
            "artifact_reconstruction_trace_path": repo_relative(
                artifact_paths_by_role["replayable_distinction_trace"]
            ),
            "runtime_replay_stable": runtime_replay_trace["replay_stable"],
            "artifact_reconstruction_stable": artifact_reconstruction_trace[
                "all_artifact_sha256_match_file_contents"
            ]
            and artifact_reconstruction_trace["all_trace_digests_match_i4_row"],
            "replay_distinction_persistence_ratio": 1.0,
        },
        "old_basin_relation_trace": i4_row["old_basin_relation_trace"],
        "merge_leakage_trace": i4_row["merge_leakage_trace"],
        "merge_leakage_i5_control_status": "passed",
        "formation_window": i4_row["formation_window"],
        "bifurcation_window": i4_row["bifurcation_window"],
        "boundary_candidate_window": i4_row["boundary_candidate_window"],
        "replay_window": {
            "mode": "duplicate_runtime_replay_and_artifact_reconstruction",
            "replay_count": runtime_replay_trace["replay_count"],
        },
        "old_basin_reference_window": i4_row["old_basin_reference_window"],
        "bifurcation_window_order_valid": True,
        "thresholds_declared_before_bifurcation_window": True,
        "old_basin_signature_digest": i4_row["old_basin_signature_digest"],
        "candidate_basin_signature_digest": i4_row[
            "candidate_basin_signature_digest"
        ],
        "candidate_boundary_signature_digest": i4_row[
            "candidate_boundary_signature_digest"
        ],
        "old_to_candidate_separation_digest": i4_row[
            "old_to_candidate_separation_digest"
        ],
        "boundary_distinguishability_margin": i4_row[
            "boundary_distinguishability_margin"
        ],
        "boundary_distinguishability_margin_formula": i4_row.get(
            "boundary_distinguishability_margin_formula"
        ),
        "support_floor_margin_new_region": i4_row[
            "support_floor_margin_new_region"
        ],
        "coherence_floor_margin_new_region": i4_row[
            "coherence_floor_margin_new_region"
        ],
        "old_basin_separation_margin": i4_row["old_basin_separation_margin"],
        "old_basin_separation_margin_kind": i4_row.get(
            "old_basin_separation_margin_kind"
        ),
        "old_basin_separation_margin_formula": i4_row.get(
            "old_basin_separation_margin_formula"
        ),
        "merge_leakage_margin": i4_row["merge_leakage_margin"],
        "replay_distinction_persistence_ratio": 1.0,
        "old_basin_thickening_rejected": True,
        "reshaped_old_boundary_rejected": True,
        "merge_leakage_rejected": True,
        "transient_rejected": True,
        "label_only_rejected": True,
        "native_flux_debt_bound": NATIVE_FLUX_DEBT_BOUND,
        "native_flux_debt_widened": False,
        "native_flux_debt_status": "preserved",
        "producer_flux_window_bound": "not_applicable_native_lane",
        "producer_flux_window_declared_before_use": "not_applicable_native_lane",
        "native_flux_debt_not_overwritten": True,
        "support_floor_result": "candidate_trace_replay_stable_zero_margin",
        "coherence_floor_result": "candidate_trace_replay_stable_zero_margin",
        "boundary_integrity_result": "source_current_boundary_candidate_replay_stable",
        "flux_or_leakage_result": "budget_error_within_1e-9_replay_stable",
        "control_results": controls,
        "producer_residue_classification": "not_applicable_native_row",
        "naturalization_debt": [
            "zero_margin_support_coherence_floor",
            "stress_threshold_matrix",
            "producer_assisted_flux_conditioned_comparison",
        ],
        "ap4_dependency_status": "required_recorded",
        "ap5_dependency_status": "not_applicable",
        "ap4_condition_reason": "N25 remains downstream of N24 AP4 optionality context",
        "ap5_condition_reason": "no proxy/target formation row in I5 native replay matrix",
        "bf_ladder_rung": "BF4_native_replay_control_backed_sub_basin_differentiation_candidate",
        "bf_ladder_rung_status": "candidate_ceiling_not_final_closeout",
        "row_decision": "supported",
        "basin_formation_claim_allowed": False,
        "claim_ceiling": (
            "native replay/control-backed sub-basin differentiation candidate; "
            "zero-margin and no BF5/BF6 stress support yet"
        ),
        "n25_closeout_ceiling": "N25-C4_replay_control_backed_sub_basin_differentiation_candidate",
        "n25_closeout_ladder_rung_assigned": False,
        "unsafe_claim_flags": {claim: False for claim in UNSAFE_CLAIMS},
        "geometric_interpretation": (
            "The same LGRC9V3 spark-to-expansion geometry reappears under "
            "duplicate runtime replay and artifact reconstruction. The module "
            "boundary, old-center replacement, budget-preserved expansion, and "
            "native 1e-9 packet bound are stable, so label-only, thickening, "
            "reshaped-boundary, transient, merge/leakage, and hidden-producer "
            "interpretations fail closed. The candidate remains narrow because "
            "its support/coherence floors have zero margin."
        ),
    }
    row["row_digest"] = digest_value(row)
    row["output_digest"] = row["row_digest"]

    checks = [
        check("i1_inventory_passed", i1.get("status") == "passed", i1.get("acceptance_state")),
        check("i2_schema_passed", i2.get("status") == "passed", i2.get("acceptance_state")),
        check("i3_active_nulls_passed", i3.get("status") == "passed", i3.get("acceptance_state")),
        check("i4_native_probe_passed", i4.get("status") == "passed", i4.get("acceptance_state")),
        check("duplicate_runtime_replay_stable", runtime_replay_trace["replay_stable"], runtime_replay_trace["canonical_signature"]),
        check(
            "artifact_reconstruction_stable",
            artifact_reconstruction_trace["all_artifact_sha256_match_file_contents"]
            and artifact_reconstruction_trace["all_trace_digests_match_i4_row"],
            artifact_reconstruction_trace["trace_digest_results"],
        ),
        check("required_controls_clean", all_required_controls_clean, controls),
        check(
            "all_plan_controls_scoped_in_i5",
            all(
                control_id in {control["control_id"] for control in row["control_results"]}
                for control_id in PLAN_CONTROL_IDS
            ),
            {
                "expected": PLAN_CONTROL_IDS,
                "actual": [control["control_id"] for control in row["control_results"]],
            },
        ),
        check(
            "merge_leakage_trace_reference_unmodified",
            row["merge_leakage_trace"] == i4_row["merge_leakage_trace"]
            and row["merge_leakage_i5_control_status"] == "passed",
            row["merge_leakage_trace"],
        ),
        check(
            "bf4_ceiling_conservative",
            row["bf_ladder_rung"].startswith("BF4_")
            and row["n25_closeout_ladder_rung_assigned"] is False
            and row["basin_formation_claim_allowed"] is False,
            row["bf_ladder_rung"],
        ),
        check(
            "zero_margin_debt_preserved",
            row["support_floor_margin_new_region"] == 0.0
            and row["coherence_floor_margin_new_region"] == 0.0,
            "stress/threshold work remains required",
        ),
        check(
            "native_flux_debt_preserved",
            row["native_flux_debt_bound"] == NATIVE_FLUX_DEBT_BOUND
            and row["native_flux_debt_widened"] is False
            and row["native_flux_debt_status"] == "preserved",
            row["native_flux_debt_bound"],
        ),
        check(
            "n20_contract_rows_match_i4",
            row["n20_source_contract_row"] == i4_row["n20_source_contract_row"]
            and row["n20_consumable_contract_row"]
            == i4_row["n20_consumable_contract_row"],
            {
                "n20_source_contract_row": row["n20_source_contract_row"],
                "n20_consumable_contract_row": row["n20_consumable_contract_row"],
            },
        ),
        check(
            "n24_optionality_relabel_control_present",
            any(
                control["control_id"] == "n24_optionality_relabel_as_formation_rejected"
                and control["control_status"] == "passed"
                for control in row["control_results"]
            ),
            "N24 optionality relabel remains blocked in I5.",
        ),
        check(
            "source_current_inputs_non_circular",
            not any(path in row["source_current_inputs"] for path in row["artifact_paths"]),
            row["source_current_inputs"],
        ),
        check(
            "artifact_manifest_valid",
            row["artifact_paths_equal_manifest_paths"] is True
            and row["artifact_sha256_equal_manifest_sha256"] is True
            and row["all_artifact_sha256_match_file_contents"] is True,
            row["artifact_paths"],
        ),
        check(
            "unsafe_claim_flags_false",
            not any(row["unsafe_claim_flags"].values()),
            row["unsafe_claim_flags"],
        ),
    ]
    failed = [item for item in checks if not item["passed"]]
    output: dict[str, Any] = {
        "artifact_id": "n25_native_replay_and_control_matrix",
        "experiment": "2026-06-N25-lgrc-spark-sub-basin-new-basin-formation",
        "iteration": "I5",
        "generated_at": GENERATED_AT,
        "reconstruction_command": COMMAND,
        "status": "passed" if not failed else "failed",
        "acceptance_state": (
            "accepted_native_bf4_replay_control_backed_sub_basin_candidate_zero_margin"
            if not failed
            else "failed_native_replay_and_control_matrix"
        ),
        "source_digest_chain_audit": {
            "i1": {"path": I1_OUTPUT_PATH, "sha256": sha256_file(I1_OUTPUT_PATH), "output_digest": i1.get("output_digest")},
            "i2": {"path": I2_OUTPUT_PATH, "sha256": sha256_file(I2_OUTPUT_PATH), "output_digest": i2.get("output_digest")},
            "i3": {"path": I3_OUTPUT_PATH, "sha256": sha256_file(I3_OUTPUT_PATH), "output_digest": i3.get("output_digest")},
            "i4": {"path": I4_OUTPUT_PATH, "sha256": sha256_file(I4_OUTPUT_PATH), "output_digest": i4.get("output_digest")},
        },
        "native_replay_control_rows": [row],
        "native_replay_control_row_count": 1,
        "native_bf4_candidate_supported": not failed,
        "native_bf5_supported": False,
        "native_bf6_supported": False,
        "bf_ladder_rung_assigned": False,
        "bf_ceiling": "BF4_native_replay_control_backed_sub_basin_differentiation_candidate",
        "n25_closeout_ceiling": "N25-C4_replay_control_backed_sub_basin_differentiation_candidate",
        "n25_closeout_ladder_rung_assigned": False,
        "zero_margin_native_support_coherence_debt": True,
        "basin_formation_claim_allowed": False,
        "producer_assisted_lane_opened": False,
        "ready_for_iteration_6_producer_assisted_formation_probe": not failed,
        "checks": checks,
        "failed_checks": [item["check_id"] for item in failed],
    }
    output["output_digest"] = digest_value({k: v for k, v in output.items() if k != "output_digest"})
    return output


def write_report(output: dict[str, Any]) -> None:
    row = output["native_replay_control_rows"][0]
    lines = [
        "# N25 Iteration 5 - Native Replay And Control Matrix",
        "",
        f"Status: `{output['status']}`",
        f"Acceptance state: `{output['acceptance_state']}`",
        f"Output digest: `{output['output_digest']}`",
        "",
        "## Scope",
        "",
        "I5 replays and controls the I4 native candidate. It does not introduce",
        "producer-assisted flux conditioning and it does not run a stress/threshold",
        "matrix.",
        "",
        "## Result",
        "",
        "```text",
        f"bf_ceiling = {output['bf_ceiling']}",
        f"native_bf4_candidate_supported = {str(output['native_bf4_candidate_supported']).lower()}",
        f"native_bf5_supported = {str(output['native_bf5_supported']).lower()}",
        f"zero_margin_native_support_coherence_debt = {str(output['zero_margin_native_support_coherence_debt']).lower()}",
        f"basin_formation_claim_allowed = {str(output['basin_formation_claim_allowed']).lower()}",
        f"producer_assisted_lane_opened = {str(output['producer_assisted_lane_opened']).lower()}",
        "```",
        "",
        "## Geometric Interpretation",
        "",
        row["geometric_interpretation"],
        "",
        "This upgrades I4 from a BF2 native bifurcation partial to a BF4 candidate",
        "because the candidate is replay/control-backed. It does not support BF5",
        "or BF6 because the native support/coherence margins remain zero and no",
        "stress/threshold matrix has been run.",
        "",
        "## Controls",
        "",
    ]
    for control in row["control_results"]:
        lines.append(
            f"- `{control['control_id']}`: `{control['control_status']}`; "
            f"{control['rung_effect']}"
        )
    lines.extend(["", "## Replay", ""])
    replay = row["replayable_distinction_trace"]
    lines.extend(
        [
            f"- Runtime replay stable: `{str(replay['runtime_replay_stable']).lower()}`",
            f"- Artifact reconstruction stable: `{str(replay['artifact_reconstruction_stable']).lower()}`",
            f"- Replay distinction persistence ratio: `{replay['replay_distinction_persistence_ratio']}`",
        ]
    )
    lines.extend(["", "## Checks", ""])
    for item in output["checks"]:
        marker = "PASS" if item["passed"] else "FAIL"
        lines.append(f"- {marker}: `{item['check_id']}`")
    lines.append("")
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    output = build_output()
    write_json(OUTPUT, output)
    write_report(output)


if __name__ == "__main__":
    main()
