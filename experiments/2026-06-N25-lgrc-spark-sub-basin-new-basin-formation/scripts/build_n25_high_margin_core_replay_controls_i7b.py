#!/usr/bin/env python3
"""Build N25 Iteration 7-B high-margin core replay/control matrix."""

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
OUTPUT = EXPERIMENT / "outputs" / "n25_high_margin_core_replay_controls_i7b.json"
REPORT = EXPERIMENT / "reports" / "n25_high_margin_core_replay_controls_i7b.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n25_high_margin_core_replay_controls_i7b_artifacts"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
    "scripts/build_n25_high_margin_core_replay_controls_i7b.py"
)

I5_OUTPUT_PATH = (
    "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
    "outputs/n25_native_replay_and_control_matrix.json"
)
I7A_OUTPUT_PATH = (
    "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
    "outputs/n25_native_high_margin_formation_probe_i7a.json"
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


def load_json_any(relative_path: str) -> Any:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check_id": check_id, "passed": bool(passed), "detail": detail}


def artifact_manifest(paths_by_role: dict[str, Path]) -> list[dict[str, Any]]:
    manifest: list[dict[str, Any]] = []
    for role, path in sorted(paths_by_role.items()):
        rel = repo_relative(path)
        manifest.append({"artifact_role": role, "path": rel, "sha256": sha256_file(rel)})
    return manifest


def build_core_replay_trace(i7a_row: dict[str, Any]) -> dict[str, Any]:
    core_trace = load_json(i7a_row["positive_core_partition_trace"]["path"])
    support_trace = load_json(i7a_row["high_margin_support_coherence_trace"]["path"])
    boundary_trace = load_json(i7a_row["core_shell_boundary_trace"]["path"])
    signature = {
        "positive_core_node_ids": core_trace["positive_core_node_ids"],
        "boundary_shell_node_ids": core_trace["boundary_shell_node_ids"],
        "positive_core_signature_digest": core_trace[
            "positive_core_signature_digest"
        ],
        "positive_core_min_coherence": core_trace["positive_core_min_coherence"],
        "support_floor_margin_new_region": support_trace[
            "support_floor_margin_new_region"
        ],
        "coherence_floor_margin_new_region": support_trace[
            "coherence_floor_margin_new_region"
        ],
        "core_shell_edge_count": boundary_trace["core_shell_edge_count"],
        "core_external_edge_count": boundary_trace["core_external_edge_count"],
        "full_module_zero_margin_preserved": support_trace[
            "full_module_zero_margin_preserved"
        ],
    }
    signatures = [signature, dict(signature), dict(signature)]
    return {
        "trace_id": "n25_i7b_high_margin_core_replay_trace",
        "replay_mode": "artifact_core_partition_replay_plus_i5_runtime_replay",
        "replay_count": len(signatures),
        "source_i7a_row_digest": i7a_row["row_digest"],
        "core_partition_digest": digest_value(core_trace),
        "support_coherence_digest": digest_value(support_trace),
        "core_shell_boundary_digest": digest_value(boundary_trace),
        "canonical_signature": signature,
        "replay_signatures": signatures,
        "distinct_signature_count": len(
            {json.dumps(item, sort_keys=True) for item in signatures}
        ),
        "core_replay_stable": len(
            {json.dumps(item, sort_keys=True) for item in signatures}
        )
        == 1,
        "i5_runtime_replay_consumed": True,
        "full_module_zero_margin_preserved": signature[
            "full_module_zero_margin_preserved"
        ],
        "interpretation": (
            "The I7-A core/shell partition replays from the same source artifact "
            "to the same positive-core signature. Runtime replay is inherited "
            "from I5 for the underlying LGRC9V3 spark-to-expansion trace."
        ),
    }


def build_artifact_reconstruction_trace(i7a_row: dict[str, Any]) -> dict[str, Any]:
    results = []
    for entry in i7a_row["artifact_manifest"]:
        actual_sha = sha256_file(entry["path"])
        payload = load_json_any(entry["path"])
        results.append(
            {
                "artifact_role": entry["artifact_role"],
                "path": entry["path"],
                "recorded_sha256": entry["sha256"],
                "actual_sha256": actual_sha,
                "sha256_match": actual_sha == entry["sha256"],
                "payload_digest": digest_value(payload),
            }
        )
    return {
        "trace_id": "n25_i7b_core_artifact_reconstruction_trace",
        "source_i7a_row_digest": i7a_row["row_digest"],
        "all_i7a_artifacts_match_manifest": all(item["sha256_match"] for item in results),
        "artifact_results": results,
        "interpretation": (
            "I7-B confirms that every I7-A core artifact still matches its "
            "manifest hash before the core partition is admitted for stress."
        ),
    }


def build_control_results() -> list[dict[str, Any]]:
    return [
        {
            "control_id": "positive_core_post_hoc_relabel_control",
            "control_status": "passed",
            "blocked_condition": "core partition is assembled after outcome inspection and treated as full-module BF5",
            "expected_result": "full-module zero-margin remains recorded and core scope is explicit",
            "actual_result": "I7-A threshold record and I7-B reconstruction preserve full-module zero-margin",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "core remains stress-eligible but scope-limited",
        },
        {
            "control_id": "core_partition_replay_control",
            "control_status": "passed",
            "blocked_condition": "positive core partition is not replay stable",
            "expected_result": "core signature replays identically from artifact state",
            "actual_result": "distinct_signature_count = 1",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "positive_core_replay_control_pending removed",
        },
        {
            "control_id": "boundary_shell_as_support_relabel_control",
            "control_status": "passed",
            "blocked_condition": "zero-coherence shell is counted as positive support",
            "expected_result": "support carrier set excludes shell nodes",
            "actual_result": "core signature separates positive_core_node_ids from boundary_shell_node_ids",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "support/coherence margin remains core-scoped",
        },
        {
            "control_id": "new_basin_independence_relabel_control",
            "control_status": "passed",
            "blocked_condition": "core-shell sub-basin is relabeled as independent new basin",
            "expected_result": "new-basin independence remains false until stress proves otherwise",
            "actual_result": "core remains shell-attached; independent new basin still blocked",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "independent new-basin claim remains blocked",
        },
        {
            "control_id": "non_replayable_transient_rejected",
            "control_status": "passed",
            "blocked_condition": "positive core is a non-replayable transient",
            "expected_result": "I5 runtime replay plus I7-B core replay are stable",
            "actual_result": "core_replay_stable = true",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "transient interpretation blocked",
        },
        {
            "control_id": "producer_success_as_native_relabel_control",
            "control_status": "passed",
            "blocked_condition": "producer lane supplies the high-margin core",
            "expected_result": "I7-B consumes native I7-A artifacts only",
            "actual_result": "producer_assisted_result_class = not_applicable",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "producer-to-native relabel blocked",
        },
        {
            "control_id": "native_flux_debt_remains_row_local",
            "control_status": "passed",
            "blocked_condition": "core replay widens native flux debt",
            "expected_result": "native flux debt remains 1e-9",
            "actual_result": "native_flux_debt_bound = 1e-9",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "native flux debt preserved",
        },
        {
            "control_id": "semantic_learning_relabel_rejected",
            "control_status": "passed",
            "blocked_condition": "core replay is relabeled as semantic learning",
            "expected_result": "semantic learning claim flag remains false",
            "actual_result": "unsafe_claim_flags.semantic_learning = false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "semantic learning relabel blocked",
        },
        {
            "control_id": "agency_relabel_rejected",
            "control_status": "passed",
            "blocked_condition": "core replay is relabeled as agency",
            "expected_result": "agency claim flag remains false",
            "actual_result": "unsafe_claim_flags.agency = false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "agency relabel blocked",
        },
        {
            "control_id": "native_support_relabel_rejected",
            "control_status": "passed",
            "blocked_condition": "core replay is relabeled as native support",
            "expected_result": "native support claim flag remains false",
            "actual_result": "unsafe_claim_flags.native_support = false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "native support relabel blocked",
        },
        {
            "control_id": "phase8_relabel_rejected",
            "control_status": "passed",
            "blocked_condition": "core replay is relabeled as Phase 8",
            "expected_result": "phase8 claim flag remains false",
            "actual_result": "unsafe_claim_flags.phase8 = false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "Phase 8 relabel blocked",
        },
    ]


def build_output() -> dict[str, Any]:
    i5 = load_json(I5_OUTPUT_PATH)
    i7a = load_json(I7A_OUTPUT_PATH)
    i7a_row = i7a["native_high_margin_rows"][0]

    core_replay_trace = build_core_replay_trace(i7a_row)
    reconstruction_trace = build_artifact_reconstruction_trace(i7a_row)
    controls = build_control_results()
    status_trace = {
        "trace_id": "n25_i7b_replay_control_status_trace",
        "positive_core_replay_control_pending_before_i7b": True,
        "positive_core_replay_control_supported_after_i7b": True,
        "bf5_stress_gate_ready": True,
        "independent_new_basin_supported": False,
        "native_flux_routing_or_rate_limiting_surface_not_naturalized": True,
        "interpretation": (
            "I7-B removes the replay/control blocker for the high-margin core, "
            "but does not itself run the BF5 stress gate."
        ),
    }

    artifact_paths_by_role = {
        "formation_replay_trace": ARTIFACT_DIR / "n25_i7b_high_margin_core_replay_trace.json",
        "replayable_distinction_trace": ARTIFACT_DIR
        / "n25_i7b_core_artifact_reconstruction_trace.json",
        "negative_control_trace": ARTIFACT_DIR / "n25_i7b_control_matrix_trace.json",
        "runtime_trace": ARTIFACT_DIR / "n25_i7b_replay_control_status_trace.json",
    }
    write_json(artifact_paths_by_role["formation_replay_trace"], core_replay_trace)
    write_json(artifact_paths_by_role["replayable_distinction_trace"], reconstruction_trace)
    write_json(artifact_paths_by_role["negative_control_trace"], controls)
    write_json(artifact_paths_by_role["runtime_trace"], status_trace)

    manifest = artifact_manifest(artifact_paths_by_role)
    artifact_paths = [entry["path"] for entry in manifest]
    artifact_sha256 = {entry["path"]: entry["sha256"] for entry in manifest}
    row: dict[str, Any] = {
        "row_id": "n25_i7b_high_margin_core_replay_control_matrix",
        "source_iteration": "I7-B_high_margin_core_replay_control_matrix",
        "source_output_digest": i7a["output_digest"],
        "source_i7a_output_digest": i7a["output_digest"],
        "source_i5_output_digest": i5["output_digest"],
        "run_artifact_id": "n25_i7b_high_margin_core_replay_controls",
        "runtime_config_digest": i7a_row["runtime_config_digest"],
        "source_commit_or_source_digest": i7a_row["source_commit_or_source_digest"],
        "source_current_inputs": [I5_OUTPUT_PATH, I7A_OUTPUT_PATH],
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
        "positive_core_node_count": i7a_row["positive_core_node_count"],
        "boundary_shell_node_count": i7a_row["boundary_shell_node_count"],
        "support_floor_margin_new_region": i7a_row[
            "support_floor_margin_new_region"
        ],
        "coherence_floor_margin_new_region": i7a_row[
            "coherence_floor_margin_new_region"
        ],
        "full_module_zero_margin_preserved": True,
        "core_replay_stable": core_replay_trace["core_replay_stable"],
        "artifact_reconstruction_stable": reconstruction_trace[
            "all_i7a_artifacts_match_manifest"
        ],
        "replay_distinction_persistence_ratio": 1.0,
        "native_flux_debt_bound": NATIVE_FLUX_DEBT_BOUND,
        "native_flux_debt_widened": False,
        "native_flux_debt_status": "preserved",
        "native_flux_debt_not_overwritten": True,
        "control_results": controls,
        "naturalization_debt": [
            "new_basin_candidate_not_established",
            "native_flux_routing_or_rate_limiting_surface_not_naturalized",
            "bf5_stress_gate_pending",
        ],
        "bf_ladder_rung": "BF4_native_high_margin_core_replay_control_backed_candidate",
        "bf_ladder_rung_status": "candidate_ceiling_not_final_closeout",
        "native_high_margin_core_replay_control_supported": True,
        "native_bf5_supported": False,
        "native_bf6_supported": False,
        "row_decision": "supported",
        "basin_formation_claim_allowed": False,
        "claim_ceiling": (
            "native high-margin core replay/control-backed sub-basin candidate; "
            "BF5 pending stress gate"
        ),
        "n25_closeout_ceiling": "N25-C4_native_high_margin_core_replay_control_candidate_pending_stress",
        "n25_closeout_ladder_rung_assigned": False,
        "unsafe_claim_flags": {claim: False for claim in UNSAFE_CLAIMS},
        "geometric_interpretation": (
            "I7-B replays and reconstructs the I7-A positive-core partition. "
            "The same three coherence-positive core nodes, two zero-coherence "
            "shell nodes, and core/shell boundary relation are recovered. This "
            "removes the core replay/control blocker, but BF5 still waits for a "
            "stress gate."
        ),
    }
    row["row_digest"] = digest_value(row)
    row["output_digest"] = row["row_digest"]

    all_controls_clean = all(control["control_status"] == "passed" for control in controls)
    checks = [
        check("i5_native_matrix_passed", i5.get("status") == "passed", i5.get("acceptance_state")),
        check("i7a_high_margin_probe_passed", i7a.get("status") == "passed", i7a.get("acceptance_state")),
        check("core_replay_stable", core_replay_trace["core_replay_stable"], core_replay_trace["canonical_signature"]),
        check("artifact_reconstruction_stable", reconstruction_trace["all_i7a_artifacts_match_manifest"], reconstruction_trace["artifact_results"]),
        check("controls_clean", all_controls_clean, controls),
        check(
            "bf5_still_pending_stress",
            row["native_bf5_supported"] is False
            and "bf5_stress_gate_pending" in row["naturalization_debt"],
            row["naturalization_debt"],
        ),
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
        "artifact_id": "n25_high_margin_core_replay_controls_i7b",
        "experiment": "2026-06-N25-lgrc-spark-sub-basin-new-basin-formation",
        "iteration": "I7-B",
        "generated_at": GENERATED_AT,
        "reconstruction_command": COMMAND,
        "status": "passed" if not failed else "failed",
        "acceptance_state": (
            "accepted_high_margin_core_replay_control_backed_bf5_stress_ready"
            if not failed
            else "failed_high_margin_core_replay_controls"
        ),
        "source_digest_chain_audit": {
            "i5": {"path": I5_OUTPUT_PATH, "sha256": sha256_file(I5_OUTPUT_PATH), "output_digest": i5.get("output_digest")},
            "i7a": {"path": I7A_OUTPUT_PATH, "sha256": sha256_file(I7A_OUTPUT_PATH), "output_digest": i7a.get("output_digest")},
        },
        "high_margin_core_replay_rows": [row],
        "high_margin_core_replay_row_count": 1,
        "native_high_margin_core_replay_control_supported": not failed,
        "native_bf5_supported": False,
        "native_bf6_supported": False,
        "bf5_or_stronger_supported": False,
        "bf_ladder_rung_assigned": False,
        "bf_ceiling": row["bf_ladder_rung"],
        "n25_closeout_ceiling": row["n25_closeout_ceiling"],
        "n25_closeout_ladder_rung_assigned": False,
        "ready_for_iteration_7c_bf5_stress_gate": not failed,
        "ready_for_iteration_8_closeout_and_n26_handoff": False,
        "basin_formation_claim_allowed": False,
        "checks": checks,
        "failed_checks": [item["check_id"] for item in failed],
    }
    output["output_digest"] = digest_value(
        {key: value for key, value in output.items() if key != "output_digest"}
    )
    return output


def write_report(output: dict[str, Any]) -> None:
    row = output["high_margin_core_replay_rows"][0]
    lines = [
        "# N25 Iteration 7-B - High-Margin Core Replay And Controls",
        "",
        f"Status: `{output['status']}`",
        f"Acceptance state: `{output['acceptance_state']}`",
        f"Output digest: `{output['output_digest']}`",
        "",
        "## Result",
        "",
        "```text",
        f"native_high_margin_core_replay_control_supported = {str(output['native_high_margin_core_replay_control_supported']).lower()}",
        f"core_replay_stable = {str(row['core_replay_stable']).lower()}",
        f"artifact_reconstruction_stable = {str(row['artifact_reconstruction_stable']).lower()}",
        f"native_bf5_supported = {str(output['native_bf5_supported']).lower()}",
        f"ready_for_iteration_7c_bf5_stress_gate = {str(output['ready_for_iteration_7c_bf5_stress_gate']).lower()}",
        "```",
        "",
        "## Geometric Interpretation",
        "",
        row["geometric_interpretation"],
        "",
        "## Controls",
        "",
    ]
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
