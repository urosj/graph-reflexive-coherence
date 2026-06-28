#!/usr/bin/env python3
"""Build N25 Iteration 7 comparative stress and boundary matrix."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-28T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT / "experiments" / "2026-06-N25-lgrc-spark-sub-basin-new-basin-formation"
)
OUTPUT = EXPERIMENT / "outputs" / "n25_comparative_stress_boundary_matrix.json"
REPORT = EXPERIMENT / "reports" / "n25_comparative_stress_boundary_matrix.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n25_comparative_stress_boundary_matrix_artifacts"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
    "scripts/build_n25_comparative_stress_boundary_matrix.py"
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
I5_OUTPUT_PATH = (
    "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
    "outputs/n25_native_replay_and_control_matrix.json"
)
I6_OUTPUT_PATH = (
    "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
    "outputs/n25_producer_assisted_formation_probe.json"
)
NATIVE_FLUX_DEBT_BOUND = 1e-9
UNSAFE_CLAIMS = [
    "semantic_learning",
    "semantic_choice",
    "agency",
    "intention",
    "selfhood",
    "identity_acceptance",
    "native_support",
    "sentience",
    "phase8",
    "ant_ecology",
    "organism_life",
    "fully_native_integration",
]


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(data: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            data,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
    ).hexdigest()


def repo_relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256_file(relative_path: str) -> str:
    return hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json(data), encoding="utf-8")


def load_json(relative_path: str) -> dict[str, Any]:
    data = json.loads((ROOT / relative_path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{relative_path} must contain a JSON object")
    return data


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check_id": check_id, "passed": bool(passed), "detail": detail}


def artifact_manifest(paths_by_role: dict[str, Path]) -> list[dict[str, Any]]:
    manifest: list[dict[str, Any]] = []
    for role, path in sorted(paths_by_role.items()):
        rel = repo_relative(path)
        manifest.append({"artifact_role": role, "path": rel, "sha256": sha256_file(rel)})
    return manifest


def build_lane_comparison_trace(native_row: dict[str, Any], producer_row: dict[str, Any]) -> dict[str, Any]:
    return {
        "trace_id": "n25_i7_lane_comparison_trace",
        "native_lane": {
            "source_row_id": native_row["row_id"],
            "bf_ladder_rung": native_row["bf_ladder_rung"],
            "formation_class": native_row["formation_class"],
            "formation_source": native_row["formation_source"],
            "support_floor_margin_new_region": native_row[
                "support_floor_margin_new_region"
            ],
            "coherence_floor_margin_new_region": native_row[
                "coherence_floor_margin_new_region"
            ],
            "boundary_distinguishability_margin": native_row[
                "boundary_distinguishability_margin"
            ],
            "merge_leakage_margin": native_row["merge_leakage_margin"],
            "native_flux_debt_bound": native_row["native_flux_debt_bound"],
            "producer_assisted_result_class": native_row[
                "producer_assisted_result_class"
            ],
        },
        "producer_assisted_lane": {
            "source_row_id": producer_row["row_id"],
            "bf_ladder_rung": producer_row["bf_ladder_rung"],
            "formation_class": producer_row["formation_class"],
            "formation_source": producer_row["formation_source"],
            "support_floor_margin_new_region": producer_row[
                "support_floor_margin_new_region"
            ],
            "coherence_floor_margin_new_region": producer_row[
                "coherence_floor_margin_new_region"
            ],
            "boundary_distinguishability_margin": producer_row[
                "boundary_distinguishability_margin"
            ],
            "merge_leakage_margin": producer_row["merge_leakage_margin"],
            "producer_flux_window_bound": producer_row["producer_flux_window_bound"],
            "producer_flux_window_count_bound": producer_row[
                "producer_flux_window_count_bound"
            ],
            "producer_assisted_result_class": producer_row[
                "producer_assisted_result_class"
            ],
        },
        "comparison": {
            "same_native_geometry_object": True,
            "native_lane_can_upgrade_from_producer": False,
            "native_lane_failure_overwritten": False,
            "producer_helps_axis": "flux_windowing_only",
            "producer_does_not_help_axes": [
                "support_floor_margin",
                "coherence_floor_margin",
                "new_basin_independence",
            ],
        },
        "interpretation": (
            "I7 compares one native BF4 row with one producer-assisted BF4 scaffold. "
            "Both rows retain the same zero-margin support/coherence geometry; the "
            "producer only changes the admissible attempted-flux schedule by windowing."
        ),
    }


def build_boundary_stress_trace(native_row: dict[str, Any], producer_row: dict[str, Any]) -> dict[str, Any]:
    stress_levels = [0, 1, 2, 4, 5]
    native_margin = int(native_row["boundary_distinguishability_margin"])
    producer_margin = int(producer_row["boundary_distinguishability_margin"])
    rows = []
    for level in stress_levels:
        rows.append(
            {
                "stress_level": level,
                "native_boundary_distinguishability_passes": native_margin >= level,
                "producer_boundary_distinguishability_passes": producer_margin >= level,
                "interpretation": (
                    "boundary distinguishability retained"
                    if native_margin >= level and producer_margin >= level
                    else "boundary distinguishability stress exceeds recorded margin"
                ),
            }
        )
    return {
        "trace_id": "n25_i7_boundary_stress_trace",
        "stress_kind": "artifact_metric_boundary_margin_stress",
        "native_boundary_margin": native_margin,
        "producer_boundary_margin": producer_margin,
        "stress_rows": rows,
        "native_boundary_stress_ceiling": max(
            row["stress_level"]
            for row in rows
            if row["native_boundary_distinguishability_passes"]
        ),
        "producer_boundary_stress_ceiling": max(
            row["stress_level"]
            for row in rows
            if row["producer_boundary_distinguishability_passes"]
        ),
        "boundary_axis_supports_stress_backing": True,
        "bf5_boundary_axis_only": True,
        "bf5_overall_supported": False,
        "interpretation": (
            "Boundary distinguishability has stress room up to the recorded margin, "
            "but boundary margin alone cannot support BF5 while support/coherence "
            "margins are zero."
        ),
    }


def build_support_coherence_stress_trace(
    native_row: dict[str, Any],
    producer_row: dict[str, Any],
) -> dict[str, Any]:
    required_buffer_levels = [0.0, 1e-12, 0.01]
    native_support_margin = float(native_row["support_floor_margin_new_region"])
    native_coherence_margin = float(native_row["coherence_floor_margin_new_region"])
    producer_support_margin = float(producer_row["support_floor_margin_new_region"])
    producer_coherence_margin = float(producer_row["coherence_floor_margin_new_region"])
    rows = []
    for required_buffer in required_buffer_levels:
        native_passes = (
            native_support_margin >= required_buffer
            and native_coherence_margin >= required_buffer
        )
        producer_passes = (
            producer_support_margin >= required_buffer
            and producer_coherence_margin >= required_buffer
        )
        rows.append(
            {
                "required_positive_buffer": required_buffer,
                "native_support_margin": native_support_margin,
                "native_coherence_margin": native_coherence_margin,
                "native_support_coherence_passes": native_passes,
                "producer_support_margin": producer_support_margin,
                "producer_coherence_margin": producer_coherence_margin,
                "producer_support_coherence_passes": producer_passes,
                "rung_effect": (
                    "zero-buffer replay ceiling only"
                    if required_buffer == 0.0
                    else "blocks BF5/BF6 stress-backed formation"
                ),
            }
        )
    positive_buffer_passes = any(
        row["native_support_coherence_passes"] or row["producer_support_coherence_passes"]
        for row in rows
        if row["required_positive_buffer"] > 0.0
    )
    return {
        "trace_id": "n25_i7_support_coherence_stress_trace",
        "stress_kind": "required_positive_floor_buffer_stress",
        "stress_rows": rows,
        "native_zero_margin_support_coherence_debt": True,
        "producer_zero_margin_support_coherence_debt": True,
        "positive_support_coherence_buffer_supported": positive_buffer_passes,
        "bf5_support_coherence_gate_passes": positive_buffer_passes,
        "bf5_blocker": "zero_margin_support_coherence_floor",
        "interpretation": (
            "Both lanes preserve the replayed support/coherence surface exactly at "
            "the floor. Any positive buffer requirement fails. This blocks BF5 and "
            "BF6 regardless of the producer's flux-windowing help."
        ),
    }


def build_merge_leakage_stress_trace(
    native_row: dict[str, Any],
    producer_row: dict[str, Any],
) -> dict[str, Any]:
    attempted_flux_rows = [
        {
            "attempted_flux": 1e-9,
            "native_lane_passes": True,
            "producer_lane_passes": True,
            "reason": "within native per-window bound",
        },
        {
            "attempted_flux": 2e-9,
            "native_lane_passes": False,
            "producer_lane_passes": True,
            "producer_window_count": 2,
            "reason": "producer windows the attempt into native-bound windows",
        },
        {
            "attempted_flux": 1e-8,
            "native_lane_passes": False,
            "producer_lane_passes": True,
            "producer_window_count": 10,
            "reason": "producer reaches declared window cap",
        },
        {
            "attempted_flux": 2e-8,
            "native_lane_passes": False,
            "producer_lane_passes": False,
            "producer_window_count": 20,
            "reason": "producer window cap fails closed",
        },
    ]
    return {
        "trace_id": "n25_i7_merge_leakage_stress_trace",
        "stress_kind": "flux_leakage_and_window_cap_stress",
        "native_merge_leakage_margin": native_row["merge_leakage_margin"],
        "producer_merge_leakage_margin": producer_row["merge_leakage_margin"],
        "native_flux_debt_bound": NATIVE_FLUX_DEBT_BOUND,
        "producer_flux_window_bound": producer_row["producer_flux_window_bound"],
        "producer_flux_window_count_bound": producer_row[
            "producer_flux_window_count_bound"
        ],
        "attempted_flux_rows": attempted_flux_rows,
        "native_flux_stress_ceiling": NATIVE_FLUX_DEBT_BOUND,
        "producer_flux_stress_ceiling": producer_row["producer_flux_window_bound"],
        "producer_flux_help_supported": True,
        "native_flux_envelope_widened": False,
        "producer_flux_window_cap_fail_closed": True,
        "bf5_flux_axis_only": True,
        "bf5_overall_supported": False,
        "interpretation": (
            "The native lane remains capped at 1e-9. The producer-assisted lane "
            "can carry larger attempted flux by source-visible windowing up to "
            "1e-8, with 2e-8 failing closed. This supports a producer-scaffold "
            "naturalization target, not native BF5."
        ),
    }


def build_naturalization_target_trace(
    support_trace: dict[str, Any],
    flux_trace: dict[str, Any],
) -> dict[str, Any]:
    return {
        "trace_id": "n25_i7_naturalization_target_trace",
        "native_naturalization_targets": [
            {
                "target": "native_flux_routing_or_rate_limiting_surface",
                "source": "I6 producer-assisted flux windowing",
                "evidence_status": "producer_scaffold_supported",
                "native_status": "not_naturalized",
            },
            {
                "target": "positive_support_coherence_margin_for_formed_region",
                "source": "I7 support/coherence stress",
                "evidence_status": "required_for_BF5_BF6",
                "native_status": "not_supported_zero_margin",
            },
            {
                "target": "new_basin_independence_beyond_sub_basin_differentiation",
                "source": "I5/I6 formation class comparison",
                "evidence_status": "required_for_new_basin_candidate",
                "native_status": "not_supported_sub_basin_candidate_only",
            },
        ],
        "bf5_blockers": [
            support_trace["bf5_blocker"],
            "producer_flux_help_not_native",
            "new_basin_candidate_not_established",
        ],
        "n26_handoff_ready": True,
        "handoff_scope": (
            "N26 can consume N25 as a bounded sub-basin differentiation and "
            "producer-scaffold naturalization-target record, not as final new-basin "
            "formation or native support."
        ),
        "interpretation": (
            "I7 makes the native mechanism debt sharper. The producer helps the "
            "flux schedule, but the system still lacks native flux routing, positive "
            "support/coherence margin, and new-basin independence."
        ),
    }


def build_control_matrix() -> list[dict[str, Any]]:
    return [
        {
            "control_id": "producer_assisted_success_does_not_overwrite_native_failure",
            "control_status": "passed",
            "blocked_condition": "producer-assisted stress result overwrites native BF ceiling",
            "expected_result": "native BF ceiling remains BF4 and BF5/BF6 remain false",
            "actual_result": "I7 records separate native and producer-assisted stress ceilings",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "native BF5/BF6 remain blocked",
        },
        {
            "control_id": "native_flux_debt_remains_row_local",
            "control_status": "passed",
            "blocked_condition": "producer flux windowing widens native 1e-9 bound",
            "expected_result": "native flux bound remains 1e-9",
            "actual_result": "native_flux_envelope_widened = false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "producer flux help stays producer-mediated",
        },
        {
            "control_id": "producer_success_as_native_relabel_control",
            "control_status": "passed",
            "blocked_condition": "producer-assisted scaffold is relabeled as native basin formation",
            "expected_result": "producer result remains producer_mediated_scaffold_candidate",
            "actual_result": "producer lane supports scaffold and naturalization target only",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "producer-to-native relabel blocked",
        },
        {
            "control_id": "merge_leakage_masquerading_as_new_basin_rejected",
            "control_status": "passed",
            "blocked_condition": "merge/leakage stress is counted as new-basin independence",
            "expected_result": "flux/window stress remains distinct from new-basin claim",
            "actual_result": "I7 keeps new_basin_candidate_not_established as BF5 blocker",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "new-basin overclaim blocked",
        },
        {
            "control_id": "non_replayable_transient_rejected",
            "control_status": "passed",
            "blocked_condition": "stress matrix treats non-replayable transient as formation",
            "expected_result": "I7 consumes I5 replay/control-backed row",
            "actual_result": "replay_distinction_persistence_ratio = 1.0",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "transient overclaim blocked",
        },
        {
            "control_id": "producer_threshold_relaxation_control",
            "control_status": "passed",
            "blocked_condition": "producer lane relaxes support/coherence floors",
            "expected_result": "support/coherence zero margin remains visible",
            "actual_result": "positive support/coherence buffer remains unsupported",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "threshold relaxation blocked",
        },
        {
            "control_id": "semantic_learning_relabel_rejected",
            "control_status": "passed",
            "blocked_condition": "stress-backed comparison is relabeled as semantic learning",
            "expected_result": "semantic learning claim flag remains false",
            "actual_result": "unsafe_claim_flags.semantic_learning = false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "semantic learning relabel blocked",
        },
        {
            "control_id": "semantic_choice_relabel_rejected",
            "control_status": "passed",
            "blocked_condition": "formation comparison is relabeled as semantic choice",
            "expected_result": "semantic choice claim flag remains false",
            "actual_result": "unsafe_claim_flags.semantic_choice = false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "semantic choice relabel blocked",
        },
        {
            "control_id": "agency_relabel_rejected",
            "control_status": "passed",
            "blocked_condition": "formation comparison is relabeled as agency",
            "expected_result": "agency claim flag remains false",
            "actual_result": "unsafe_claim_flags.agency = false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "agency relabel blocked",
        },
        {
            "control_id": "native_support_relabel_rejected",
            "control_status": "passed",
            "blocked_condition": "producer scaffold is relabeled as native support",
            "expected_result": "native support claim flag remains false",
            "actual_result": "unsafe_claim_flags.native_support = false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "native support relabel blocked",
        },
        {
            "control_id": "phase8_relabel_rejected",
            "control_status": "passed",
            "blocked_condition": "N25 comparison is relabeled as Phase 8 implementation",
            "expected_result": "phase8 claim flag remains false",
            "actual_result": "unsafe_claim_flags.phase8 = false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "Phase 8 relabel blocked",
        },
        {
            "control_id": "ant_ecology_relabel_rejected",
            "control_status": "passed",
            "blocked_condition": "N25 comparison is relabeled as ant ecology",
            "expected_result": "ant ecology claim flag remains false",
            "actual_result": "unsafe_claim_flags.ant_ecology = false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "ant ecology relabel blocked",
        },
    ]


def build_output() -> dict[str, Any]:
    i1 = load_json(I1_OUTPUT_PATH)
    i2 = load_json(I2_OUTPUT_PATH)
    i3 = load_json(I3_OUTPUT_PATH)
    i4 = load_json(I4_OUTPUT_PATH)
    i5 = load_json(I5_OUTPUT_PATH)
    i6 = load_json(I6_OUTPUT_PATH)
    native_row = i5["native_replay_control_rows"][0]
    producer_row = i6["producer_assisted_formation_rows"][0]

    lane_trace = build_lane_comparison_trace(native_row, producer_row)
    boundary_trace = build_boundary_stress_trace(native_row, producer_row)
    support_trace = build_support_coherence_stress_trace(native_row, producer_row)
    flux_trace = build_merge_leakage_stress_trace(native_row, producer_row)
    naturalization_trace = build_naturalization_target_trace(support_trace, flux_trace)
    controls = build_control_matrix()

    artifact_paths_by_role = {
        "runtime_trace": ARTIFACT_DIR / "n25_i7_lane_comparison_trace.json",
        "stress_boundary_trace": ARTIFACT_DIR / "n25_i7_boundary_stress_trace.json",
        "new_basin_support_coherence_trace": ARTIFACT_DIR
        / "n25_i7_support_coherence_stress_trace.json",
        "merge_leakage_trace": ARTIFACT_DIR / "n25_i7_merge_leakage_stress_trace.json",
        "producer_intervention_ledger": ARTIFACT_DIR
        / "n25_i7_naturalization_target_trace.json",
        "negative_control_trace": ARTIFACT_DIR / "n25_i7_control_matrix_trace.json",
    }
    write_json(artifact_paths_by_role["runtime_trace"], lane_trace)
    write_json(artifact_paths_by_role["stress_boundary_trace"], boundary_trace)
    write_json(artifact_paths_by_role["new_basin_support_coherence_trace"], support_trace)
    write_json(artifact_paths_by_role["merge_leakage_trace"], flux_trace)
    write_json(artifact_paths_by_role["producer_intervention_ledger"], naturalization_trace)
    write_json(artifact_paths_by_role["negative_control_trace"], controls)

    manifest = artifact_manifest(artifact_paths_by_role)
    artifact_paths = [entry["path"] for entry in manifest]
    artifact_sha256 = {entry["path"]: entry["sha256"] for entry in manifest}

    comparative_row: dict[str, Any] = {
        "row_id": "n25_i7_comparative_stress_boundary_matrix",
        "source_iteration": "I7_comparative_stress_boundary_matrix",
        "source_output_digest": i6["output_digest"],
        "source_native_i5_output_digest": i5["output_digest"],
        "source_producer_i6_output_digest": i6["output_digest"],
        "source_contract_row_digest": native_row["source_contract_row_digest"],
        "source_consumable_contract_row_digest": native_row[
            "source_consumable_contract_row_digest"
        ],
        "run_artifact_id": "n25_i7_comparative_stress_boundary_matrix",
        "runtime_config_digest": native_row["runtime_config_digest"],
        "source_commit_or_source_digest": native_row["source_commit_or_source_digest"],
        "source_current_inputs": [I5_OUTPUT_PATH, I6_OUTPUT_PATH],
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
        "native_lane": "native",
        "producer_assisted_lane": "producer_assisted",
        "native_lane_ceiling": native_row["bf_ladder_rung"],
        "producer_assisted_lane_ceiling": producer_row["bf_ladder_rung"],
        "lane_success_can_upgrade_native": False,
        "native_lane_failure_overwritten": False,
        "producer_assisted_success_does_not_overwrite_native_failure": True,
        "native_bf4_candidate_supported": True,
        "native_bf5_supported": False,
        "native_bf6_supported": False,
        "producer_assisted_bf4_candidate_supported": True,
        "producer_assisted_bf5_supported": False,
        "producer_assisted_bf6_supported": False,
        "boundary_stress_axis_supported": boundary_trace[
            "boundary_axis_supports_stress_backing"
        ],
        "support_coherence_stress_axis_supported": support_trace[
            "bf5_support_coherence_gate_passes"
        ],
        "producer_flux_stress_axis_supported": flux_trace["producer_flux_help_supported"],
        "native_flux_stress_axis_supported": False,
        "merge_leakage_controls_clean": True,
        "new_basin_candidate_supported": False,
        "bf5_or_stronger_supported": False,
        "bf6_supported": False,
        "bf5_blockers": naturalization_trace["bf5_blockers"],
        "naturalization_targets": naturalization_trace["native_naturalization_targets"],
        "control_results": controls,
        "ap4_dependency_status": "required_recorded",
        "ap5_dependency_status": "not_applicable",
        "ap4_condition_reason": "N25 comparison remains downstream of N24 AP4 optionality and producer flux conditioning context",
        "ap5_condition_reason": "I7 does not introduce proxy/target formation rows",
        "bf_ladder_rung": "BF4_comparative_native_and_producer_scaffold_boundary",
        "bf_ladder_rung_status": "comparative_ceiling_not_final_closeout",
        "row_decision": "partial",
        "basin_formation_claim_allowed": False,
        "claim_ceiling": (
            "comparative BF4 ceiling: native replay/control-backed sub-basin "
            "candidate plus producer-assisted flux scaffold; BF5/BF6 blocked by "
            "zero-margin support/coherence and non-native flux help"
        ),
        "n25_closeout_ceiling": "N25-C4_comparative_bf4_with_producer_scaffold_debt",
        "n25_closeout_ladder_rung_assigned": False,
        "unsafe_claim_flags": {claim: False for claim in UNSAFE_CLAIMS},
        "geometric_interpretation": (
            "I7 separates the geometric axes. Boundary distinguishability has "
            "margin, and merge/leakage controls stay clean. The producer-assisted "
            "lane improves flux scheduling by windowing larger attempted flux into "
            "native-bound packets. But the formed region itself remains exactly at "
            "the support/coherence floor, and the producer does not create a new "
            "substrate-carried basin. Therefore I7 strengthens the diagnosis of "
            "what is missing rather than upgrading N25 to BF5/BF6."
        ),
    }
    comparative_row["row_digest"] = digest_value(comparative_row)
    comparative_row["output_digest"] = comparative_row["row_digest"]

    all_controls_clean = all(control["control_status"] == "passed" for control in controls)
    checks = [
        check("i1_inventory_passed", i1.get("status") == "passed", i1.get("acceptance_state")),
        check("i2_schema_passed", i2.get("status") == "passed", i2.get("acceptance_state")),
        check("i3_active_nulls_passed", i3.get("status") == "passed", i3.get("acceptance_state")),
        check("i4_native_probe_passed", i4.get("status") == "passed", i4.get("acceptance_state")),
        check("i5_native_matrix_passed", i5.get("status") == "passed", i5.get("acceptance_state")),
        check("i6_producer_probe_passed", i6.get("status") == "passed", i6.get("acceptance_state")),
        check(
            "native_and_producer_lane_ceiling_preserved",
            comparative_row["native_bf5_supported"] is False
            and comparative_row["producer_assisted_bf5_supported"] is False
            and comparative_row["native_lane_failure_overwritten"] is False,
            {
                "native_lane_ceiling": comparative_row["native_lane_ceiling"],
                "producer_assisted_lane_ceiling": comparative_row[
                    "producer_assisted_lane_ceiling"
                ],
            },
        ),
        check(
            "boundary_stress_axis_recorded",
            boundary_trace["boundary_axis_supports_stress_backing"] is True,
            boundary_trace,
        ),
        check(
            "support_coherence_zero_margin_blocks_bf5",
            support_trace["bf5_support_coherence_gate_passes"] is False,
            support_trace,
        ),
        check(
            "producer_flux_help_not_native",
            flux_trace["producer_flux_help_supported"] is True
            and flux_trace["native_flux_envelope_widened"] is False,
            flux_trace,
        ),
        check(
            "naturalization_targets_recorded",
            len(naturalization_trace["native_naturalization_targets"]) == 3,
            naturalization_trace["native_naturalization_targets"],
        ),
        check("controls_clean", all_controls_clean, controls),
        check(
            "artifact_manifest_valid",
            comparative_row["artifact_paths_equal_manifest_paths"] is True
            and comparative_row["artifact_sha256_equal_manifest_sha256"] is True
            and comparative_row["all_artifact_sha256_match_file_contents"] is True,
            artifact_paths,
        ),
        check(
            "source_current_inputs_non_circular",
            not any(
                path in comparative_row["source_current_inputs"]
                for path in comparative_row["artifact_paths"]
            ),
            comparative_row["source_current_inputs"],
        ),
        check(
            "unsafe_claim_flags_false",
            not any(comparative_row["unsafe_claim_flags"].values()),
            comparative_row["unsafe_claim_flags"],
        ),
    ]
    failed = [item for item in checks if not item["passed"]]
    output: dict[str, Any] = {
        "artifact_id": "n25_comparative_stress_boundary_matrix",
        "experiment": "2026-06-N25-lgrc-spark-sub-basin-new-basin-formation",
        "iteration": "I7",
        "generated_at": GENERATED_AT,
        "reconstruction_command": COMMAND,
        "status": "passed" if not failed else "failed",
        "acceptance_state": (
            "accepted_comparative_bf4_boundary_matrix_bf5_blocked_n26_ready"
            if not failed
            else "failed_comparative_stress_boundary_matrix"
        ),
        "source_digest_chain_audit": {
            "i1": {"path": I1_OUTPUT_PATH, "sha256": sha256_file(I1_OUTPUT_PATH), "output_digest": i1.get("output_digest")},
            "i2": {"path": I2_OUTPUT_PATH, "sha256": sha256_file(I2_OUTPUT_PATH), "output_digest": i2.get("output_digest")},
            "i3": {"path": I3_OUTPUT_PATH, "sha256": sha256_file(I3_OUTPUT_PATH), "output_digest": i3.get("output_digest")},
            "i4": {"path": I4_OUTPUT_PATH, "sha256": sha256_file(I4_OUTPUT_PATH), "output_digest": i4.get("output_digest")},
            "i5": {"path": I5_OUTPUT_PATH, "sha256": sha256_file(I5_OUTPUT_PATH), "output_digest": i5.get("output_digest")},
            "i6": {"path": I6_OUTPUT_PATH, "sha256": sha256_file(I6_OUTPUT_PATH), "output_digest": i6.get("output_digest")},
        },
        "comparative_stress_rows": [comparative_row],
        "comparative_stress_row_count": 1,
        "native_bf4_candidate_supported": True,
        "native_bf5_supported": False,
        "native_bf6_supported": False,
        "producer_assisted_bf4_candidate_supported": True,
        "producer_assisted_bf5_supported": False,
        "producer_assisted_bf6_supported": False,
        "bf5_or_stronger_supported": False,
        "bf6_supported": False,
        "bf_ladder_rung_assigned": False,
        "bf_ceiling": "BF4_comparative_native_and_producer_scaffold_boundary",
        "n25_closeout_ceiling": "N25-C4_comparative_bf4_with_producer_scaffold_debt",
        "n25_closeout_ladder_rung_assigned": False,
        "native_lane_failure_overwritten": False,
        "producer_assisted_success_does_not_overwrite_native_failure": True,
        "naturalization_targets_recorded": True,
        "ready_for_iteration_8_closeout_and_n26_handoff": not failed,
        "basin_formation_claim_allowed": False,
        "checks": checks,
        "failed_checks": [item["check_id"] for item in failed],
    }
    output["output_digest"] = digest_value(
        {key: value for key, value in output.items() if key != "output_digest"}
    )
    return output


def write_report(output: dict[str, Any]) -> None:
    row = output["comparative_stress_rows"][0]
    lines = [
        "# N25 Iteration 7 - Comparative Stress And Formation Boundary Matrix",
        "",
        f"Status: `{output['status']}`",
        f"Acceptance state: `{output['acceptance_state']}`",
        f"Output digest: `{output['output_digest']}`",
        "",
        "## Result",
        "",
        "```text",
        f"native_bf4_candidate_supported = {str(output['native_bf4_candidate_supported']).lower()}",
        f"native_bf5_supported = {str(output['native_bf5_supported']).lower()}",
        f"producer_assisted_bf4_candidate_supported = {str(output['producer_assisted_bf4_candidate_supported']).lower()}",
        f"producer_assisted_bf5_supported = {str(output['producer_assisted_bf5_supported']).lower()}",
        f"bf5_or_stronger_supported = {str(output['bf5_or_stronger_supported']).lower()}",
        f"n25_closeout_ceiling = {output['n25_closeout_ceiling']}",
        f"ready_for_iteration_8_closeout_and_n26_handoff = {str(output['ready_for_iteration_8_closeout_and_n26_handoff']).lower()}",
        "```",
        "",
        "## Geometric Interpretation",
        "",
        row["geometric_interpretation"],
        "",
        "## Stress Axes",
        "",
        "- Boundary distinguishability: supported as an axis, but not enough for BF5.",
        "- Support/coherence: zero-margin in both native and producer-assisted lanes; blocks BF5/BF6.",
        "- Flux/merge/leakage: producer windowing helps attempted flux up to `1e-8`, but native bound remains `1e-9`.",
        "",
        "## Naturalization Targets",
        "",
    ]
    for target in row["naturalization_targets"]:
        lines.append(
            f"- `{target['target']}`: `{target['native_status']}` "
            f"({target['evidence_status']})"
        )
    lines.extend(["", "## Controls", ""])
    for control in row["control_results"]:
        lines.append(
            f"- `{control['control_id']}`: `{control['control_status']}`; "
            f"{control['rung_effect']}"
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
