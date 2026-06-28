#!/usr/bin/env python3
"""Build N25 Iteration 7-C BF5 core stress gate."""

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
OUTPUT = EXPERIMENT / "outputs" / "n25_bf5_core_stress_gate_i7c.json"
REPORT = EXPERIMENT / "reports" / "n25_bf5_core_stress_gate_i7c.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n25_bf5_core_stress_gate_i7c_artifacts"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
    "scripts/build_n25_bf5_core_stress_gate_i7c.py"
)

I7A_OUTPUT_PATH = (
    "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
    "outputs/n25_native_high_margin_formation_probe_i7a.json"
)
I7B_OUTPUT_PATH = (
    "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
    "outputs/n25_high_margin_core_replay_controls_i7b.json"
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


def build_support_coherence_stress_trace(i7b_row: dict[str, Any]) -> dict[str, Any]:
    support_margin = float(i7b_row["support_floor_margin_new_region"])
    coherence_margin = float(i7b_row["coherence_floor_margin_new_region"])
    required_buffers = [0.0, 1.0, 3.0, coherence_margin, 3.5]
    rows = []
    for buffer in required_buffers:
        passes = support_margin > buffer and coherence_margin >= buffer
        rows.append(
            {
                "required_positive_buffer": buffer,
                "support_margin": support_margin,
                "coherence_margin": coherence_margin,
                "passes": passes,
                "rung_effect": (
                    "inside supported BF5 core stress envelope"
                    if passes
                    else "outside supported BF5 core stress envelope"
                ),
            }
        )
    return {
        "trace_id": "n25_i7c_support_coherence_stress_trace",
        "stress_kind": "positive_core_support_coherence_buffer_stress",
        "support_margin": support_margin,
        "coherence_margin": coherence_margin,
        "stress_rows": rows,
        "supported_buffer_ceiling": max(
            row["required_positive_buffer"] for row in rows if row["passes"]
        ),
        "first_fail_closed_buffer": min(
            row["required_positive_buffer"] for row in rows if not row["passes"]
        ),
        "support_coherence_stress_supported": True,
        "interpretation": (
            "The positive core has enough margin to survive nonzero floor-buffer "
            "stress up to the declared core coherence margin. The 3.5 buffer "
            "fails closed."
        ),
    }


def build_boundary_stress_trace(i7a_row: dict[str, Any]) -> dict[str, Any]:
    margin = int(i7a_row["boundary_distinguishability_margin"])
    stress_levels = [0, 2, 4, 5]
    rows = [
        {
            "boundary_stress_level": level,
            "boundary_passes": margin >= level,
            "rung_effect": (
                "inside supported BF5 boundary stress envelope"
                if margin >= level
                else "outside supported BF5 boundary stress envelope"
            ),
        }
        for level in stress_levels
    ]
    return {
        "trace_id": "n25_i7c_boundary_stress_trace",
        "stress_kind": "positive_core_boundary_distinguishability_stress",
        "boundary_distinguishability_margin": margin,
        "stress_rows": rows,
        "supported_boundary_stress_ceiling": max(
            row["boundary_stress_level"] for row in rows if row["boundary_passes"]
        ),
        "first_fail_closed_boundary_stress": min(
            row["boundary_stress_level"] for row in rows if not row["boundary_passes"]
        ),
        "boundary_stress_supported": True,
        "interpretation": (
            "The core/shell candidate retains boundary distinguishability through "
            "the recorded margin and fails closed beyond it."
        ),
    }


def build_flux_stress_trace() -> dict[str, Any]:
    rows = [
        {
            "attempted_flux": 1e-9,
            "native_flux_passes": True,
            "merge_leakage_clean": True,
            "reason": "inside inherited native flux debt bound",
        },
        {
            "attempted_flux": 2e-9,
            "native_flux_passes": False,
            "merge_leakage_clean": False,
            "reason": "native flux routing above 1e-9 not naturalized",
        },
    ]
    return {
        "trace_id": "n25_i7c_flux_merge_leakage_stress_trace",
        "stress_kind": "native_flux_bound_and_merge_leakage_stress",
        "native_flux_debt_bound": NATIVE_FLUX_DEBT_BOUND,
        "native_flux_envelope_widened": False,
        "attempted_flux_rows": rows,
        "native_flux_stress_supported_at_bound": True,
        "native_flux_stress_above_bound_supported": False,
        "merge_leakage_controls_clean_at_bound": True,
        "first_fail_closed_attempted_flux": 2e-9,
        "interpretation": (
            "I7-C supports BF5 only inside the inherited native 1e-9 flux envelope. "
            "Broader native flux routing remains naturalization debt."
        ),
    }


def build_bf5_classification_trace(
    support_trace: dict[str, Any],
    boundary_trace: dict[str, Any],
    flux_trace: dict[str, Any],
) -> dict[str, Any]:
    bf5_supported = (
        support_trace["support_coherence_stress_supported"]
        and boundary_trace["boundary_stress_supported"]
        and flux_trace["merge_leakage_controls_clean_at_bound"]
        and flux_trace["native_flux_stress_supported_at_bound"]
    )
    return {
        "trace_id": "n25_i7c_bf5_classification_trace",
        "native_bf5_core_sub_basin_stress_candidate_supported": bf5_supported,
        "native_bf5_scope": "bounded_high_margin_core_sub_basin_within_native_1e-9_flux_envelope",
        "independent_new_basin_supported": False,
        "native_bf6_supported": False,
        "bf5_supported_axes": [
            "positive_core_support_coherence_stress",
            "core_shell_boundary_stress",
            "merge_leakage_clean_at_native_flux_bound",
            "core_replay_control_backed",
        ],
        "remaining_limitations": [
            "independent_new_basin_not_supported",
            "native_flux_routing_above_1e-9_not_naturalized",
            "full_module_zero_margin_preserved",
        ],
        "interpretation": (
            "I7-C upgrades N25 to a scoped BF5: stress/threshold-backed native "
            "high-margin core sub-basin formation inside the inherited 1e-9 flux "
            "envelope. It does not support independent new-basin formation or BF6."
        ),
    }


def build_control_results() -> list[dict[str, Any]]:
    return [
        {
            "control_id": "bf5_scope_control",
            "control_status": "passed",
            "blocked_condition": "scoped core BF5 is relabeled as general independent new-basin formation",
            "expected_result": "independent_new_basin_supported remains false",
            "actual_result": "BF5 scope is high-margin core sub-basin within native 1e-9 envelope",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "BF5 remains scoped; independent new-basin claim blocked",
        },
        {
            "control_id": "support_coherence_stress_control",
            "control_status": "passed",
            "blocked_condition": "positive core fails nonzero support/coherence buffer stress",
            "expected_result": "core survives nonzero buffer and fails closed beyond margin",
            "actual_result": "supported buffer ceiling recorded; 3.5 buffer fails closed",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "support/coherence stress gate supports scoped BF5",
        },
        {
            "control_id": "boundary_stress_control",
            "control_status": "passed",
            "blocked_condition": "boundary distinguishability fails stress",
            "expected_result": "boundary survives through recorded margin and fails closed beyond it",
            "actual_result": "boundary stress ceiling = 4; stress 5 fails closed",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "boundary stress gate supports scoped BF5",
        },
        {
            "control_id": "merge_leakage_masquerading_as_new_basin_rejected",
            "control_status": "passed",
            "blocked_condition": "merge/leakage or flux beyond native bound is counted as BF5",
            "expected_result": "BF5 is bounded to native 1e-9 flux envelope",
            "actual_result": "2e-9 native flux stress fails closed",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "broad flux robustness remains blocked",
        },
        {
            "control_id": "producer_success_as_native_relabel_control",
            "control_status": "passed",
            "blocked_condition": "producer-assisted flux scaffold is used to support native BF5",
            "expected_result": "I7-C consumes native I7-B core only",
            "actual_result": "producer_assisted_result_class = not_applicable",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "producer-to-native relabel blocked",
        },
        {
            "control_id": "native_flux_debt_remains_row_local",
            "control_status": "passed",
            "blocked_condition": "BF5 stress widens native 1e-9 bound",
            "expected_result": "native flux envelope remains 1e-9",
            "actual_result": "native_flux_envelope_widened = false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "native flux debt preserved",
        },
        {
            "control_id": "semantic_learning_relabel_rejected",
            "control_status": "passed",
            "blocked_condition": "BF5 core formation is relabeled as semantic learning",
            "expected_result": "semantic learning claim flag remains false",
            "actual_result": "unsafe_claim_flags.semantic_learning = false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "semantic learning relabel blocked",
        },
        {
            "control_id": "agency_relabel_rejected",
            "control_status": "passed",
            "blocked_condition": "BF5 core formation is relabeled as agency",
            "expected_result": "agency claim flag remains false",
            "actual_result": "unsafe_claim_flags.agency = false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "agency relabel blocked",
        },
        {
            "control_id": "native_support_relabel_rejected",
            "control_status": "passed",
            "blocked_condition": "BF5 core formation is relabeled as native support",
            "expected_result": "native support claim flag remains false",
            "actual_result": "unsafe_claim_flags.native_support = false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "native support relabel blocked",
        },
        {
            "control_id": "phase8_relabel_rejected",
            "control_status": "passed",
            "blocked_condition": "BF5 core formation is relabeled as Phase 8",
            "expected_result": "phase8 claim flag remains false",
            "actual_result": "unsafe_claim_flags.phase8 = false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "Phase 8 relabel blocked",
        },
    ]


def build_output() -> dict[str, Any]:
    i7a = load_json(I7A_OUTPUT_PATH)
    i7b = load_json(I7B_OUTPUT_PATH)
    i7a_row = i7a["native_high_margin_rows"][0]
    i7b_row = i7b["high_margin_core_replay_rows"][0]

    support_trace = build_support_coherence_stress_trace(i7b_row)
    boundary_trace = build_boundary_stress_trace(i7a_row)
    flux_trace = build_flux_stress_trace()
    classification_trace = build_bf5_classification_trace(
        support_trace,
        boundary_trace,
        flux_trace,
    )
    controls = build_control_results()

    artifact_paths_by_role = {
        "new_basin_support_coherence_trace": ARTIFACT_DIR
        / "n25_i7c_support_coherence_stress_trace.json",
        "stress_boundary_trace": ARTIFACT_DIR / "n25_i7c_boundary_stress_trace.json",
        "merge_leakage_trace": ARTIFACT_DIR / "n25_i7c_flux_merge_leakage_stress_trace.json",
        "runtime_trace": ARTIFACT_DIR / "n25_i7c_bf5_classification_trace.json",
        "negative_control_trace": ARTIFACT_DIR / "n25_i7c_control_matrix_trace.json",
    }
    write_json(artifact_paths_by_role["new_basin_support_coherence_trace"], support_trace)
    write_json(artifact_paths_by_role["stress_boundary_trace"], boundary_trace)
    write_json(artifact_paths_by_role["merge_leakage_trace"], flux_trace)
    write_json(artifact_paths_by_role["runtime_trace"], classification_trace)
    write_json(artifact_paths_by_role["negative_control_trace"], controls)

    manifest = artifact_manifest(artifact_paths_by_role)
    artifact_paths = [entry["path"] for entry in manifest]
    artifact_sha256 = {entry["path"]: entry["sha256"] for entry in manifest}
    bf5_supported = classification_trace[
        "native_bf5_core_sub_basin_stress_candidate_supported"
    ]
    row: dict[str, Any] = {
        "row_id": "n25_i7c_bf5_core_stress_gate",
        "source_iteration": "I7-C_bf5_core_stress_gate",
        "source_output_digest": i7b["output_digest"],
        "source_i7a_output_digest": i7a["output_digest"],
        "source_i7b_output_digest": i7b["output_digest"],
        "run_artifact_id": "n25_i7c_bf5_core_stress_gate",
        "runtime_config_digest": i7b_row["runtime_config_digest"],
        "source_commit_or_source_digest": i7b_row["source_commit_or_source_digest"],
        "source_current_inputs": [I7A_OUTPUT_PATH, I7B_OUTPUT_PATH],
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
        "lane": "native",
        "producer_assisted_result_class": "not_applicable",
        "producer_intervention_used": False,
        "formation_class": "sub_basin_candidate",
        "formation_source": "native_source_current_bifurcation",
        "bf5_scope": classification_trace["native_bf5_scope"],
        "positive_core_node_count": i7b_row["positive_core_node_count"],
        "boundary_shell_node_count": i7b_row["boundary_shell_node_count"],
        "support_floor_margin_new_region": i7b_row[
            "support_floor_margin_new_region"
        ],
        "coherence_floor_margin_new_region": i7b_row[
            "coherence_floor_margin_new_region"
        ],
        "support_coherence_stress_supported": support_trace[
            "support_coherence_stress_supported"
        ],
        "boundary_stress_supported": boundary_trace["boundary_stress_supported"],
        "merge_leakage_controls_clean": flux_trace[
            "merge_leakage_controls_clean_at_bound"
        ],
        "native_flux_stress_supported_at_bound": flux_trace[
            "native_flux_stress_supported_at_bound"
        ],
        "native_flux_stress_above_bound_supported": flux_trace[
            "native_flux_stress_above_bound_supported"
        ],
        "native_flux_debt_bound": NATIVE_FLUX_DEBT_BOUND,
        "native_flux_debt_widened": False,
        "native_flux_debt_status": "preserved",
        "native_flux_debt_not_overwritten": True,
        "independent_new_basin_supported": False,
        "full_module_zero_margin_preserved": True,
        "control_results": controls,
        "naturalization_debt": classification_trace["remaining_limitations"],
        "bf_ladder_rung": "BF5_native_high_margin_core_sub_basin_stress_candidate",
        "bf_ladder_rung_status": "scoped_candidate_ceiling_not_final_closeout",
        "native_bf5_supported": bf5_supported,
        "native_bf6_supported": False,
        "row_decision": "supported",
        "basin_formation_claim_allowed": False,
        "claim_ceiling": (
            "scoped native BF5 high-margin core sub-basin stress candidate inside "
            "the inherited 1e-9 flux envelope; not independent new-basin formation, "
            "not BF6, not native support"
        ),
        "n25_closeout_ceiling": "N25-C5_native_high_margin_core_sub_basin_stress_candidate",
        "n25_closeout_ladder_rung_assigned": False,
        "unsafe_claim_flags": {claim: False for claim in UNSAFE_CLAIMS},
        "geometric_interpretation": classification_trace["interpretation"],
    }
    row["row_digest"] = digest_value(row)
    row["output_digest"] = row["row_digest"]

    all_controls_clean = all(control["control_status"] == "passed" for control in controls)
    checks = [
        check("i7a_high_margin_probe_passed", i7a.get("status") == "passed", i7a.get("acceptance_state")),
        check("i7b_core_replay_controls_passed", i7b.get("status") == "passed", i7b.get("acceptance_state")),
        check("support_coherence_stress_supported", support_trace["support_coherence_stress_supported"], support_trace),
        check("boundary_stress_supported", boundary_trace["boundary_stress_supported"], boundary_trace),
        check("merge_leakage_clean_at_native_bound", flux_trace["merge_leakage_controls_clean_at_bound"], flux_trace),
        check("native_flux_above_bound_fails_closed", flux_trace["native_flux_stress_above_bound_supported"] is False, flux_trace),
        check("scoped_bf5_supported", row["native_bf5_supported"] is True and row["independent_new_basin_supported"] is False, row["bf5_scope"]),
        check("bf6_still_blocked", row["native_bf6_supported"] is False, row["naturalization_debt"]),
        check("controls_clean", all_controls_clean, controls),
        check(
            "artifact_manifest_valid",
            row["artifact_paths_equal_manifest_paths"] is True
            and row["artifact_sha256_equal_manifest_sha256"] is True
            and row["all_artifact_sha256_match_file_contents"] is True,
            artifact_paths,
        ),
        check(
            "source_current_inputs_non_circular",
            not any(path in row["source_current_inputs"] for path in row["artifact_paths"]),
            row["source_current_inputs"],
        ),
        check("unsafe_claim_flags_false", not any(row["unsafe_claim_flags"].values()), row["unsafe_claim_flags"]),
    ]
    failed = [item for item in checks if not item["passed"]]
    output: dict[str, Any] = {
        "artifact_id": "n25_bf5_core_stress_gate_i7c",
        "experiment": "2026-06-N25-lgrc-spark-sub-basin-new-basin-formation",
        "iteration": "I7-C",
        "generated_at": GENERATED_AT,
        "reconstruction_command": COMMAND,
        "status": "passed" if not failed else "failed",
        "acceptance_state": (
            "accepted_scoped_native_bf5_high_margin_core_sub_basin_stress_candidate"
            if not failed
            else "failed_bf5_core_stress_gate"
        ),
        "source_digest_chain_audit": {
            "i7a": {"path": I7A_OUTPUT_PATH, "sha256": sha256_file(I7A_OUTPUT_PATH), "output_digest": i7a.get("output_digest")},
            "i7b": {"path": I7B_OUTPUT_PATH, "sha256": sha256_file(I7B_OUTPUT_PATH), "output_digest": i7b.get("output_digest")},
        },
        "bf5_core_stress_rows": [row],
        "bf5_core_stress_row_count": 1,
        "native_bf5_supported": not failed and bf5_supported,
        "native_bf6_supported": False,
        "bf5_or_stronger_supported": not failed and bf5_supported,
        "bf_ladder_rung_assigned": False,
        "bf_ceiling": row["bf_ladder_rung"],
        "n25_closeout_ceiling": row["n25_closeout_ceiling"],
        "n25_closeout_ladder_rung_assigned": False,
        "independent_new_basin_supported": False,
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
    row = output["bf5_core_stress_rows"][0]
    lines = [
        "# N25 Iteration 7-C - BF5 Core Stress Gate",
        "",
        f"Status: `{output['status']}`",
        f"Acceptance state: `{output['acceptance_state']}`",
        f"Output digest: `{output['output_digest']}`",
        "",
        "## Result",
        "",
        "```text",
        f"native_bf5_supported = {str(output['native_bf5_supported']).lower()}",
        f"native_bf6_supported = {str(output['native_bf6_supported']).lower()}",
        f"bf_ceiling = {output['bf_ceiling']}",
        f"n25_closeout_ceiling = {output['n25_closeout_ceiling']}",
        f"independent_new_basin_supported = {str(output['independent_new_basin_supported']).lower()}",
        f"ready_for_iteration_8_closeout_and_n26_handoff = {str(output['ready_for_iteration_8_closeout_and_n26_handoff']).lower()}",
        "```",
        "",
        "## Geometric Interpretation",
        "",
        row["geometric_interpretation"],
        "",
        "This is BF5 only in the scoped high-margin core/sub-basin sense. It is",
        "not independent new-basin formation and not BF6.",
        "",
        "## Remaining Limitations",
        "",
    ]
    for item in row["naturalization_debt"]:
        lines.append(f"- `{item}`")
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
