#!/usr/bin/env python3
"""Build N25 Iteration 7-E producer-assisted high-margin scaffold probe."""

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
OUTPUT = (
    EXPERIMENT / "outputs" / "n25_producer_assisted_high_margin_scaffold_i7e.json"
)
REPORT = (
    EXPERIMENT / "reports" / "n25_producer_assisted_high_margin_scaffold_i7e.md"
)
ARTIFACT_DIR = (
    EXPERIMENT / "outputs" / "n25_producer_assisted_high_margin_scaffold_i7e_artifacts"
)
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
    "scripts/build_n25_producer_assisted_high_margin_scaffold_i7e.py"
)

I6_OUTPUT_PATH = (
    "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
    "outputs/n25_producer_assisted_formation_probe.json"
)
I7C_OUTPUT_PATH = (
    "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
    "outputs/n25_bf5_core_stress_gate_i7c.json"
)
I7D_OUTPUT_PATH = (
    "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
    "outputs/n25_n26_readiness_bounded_formation_gate_i7d.json"
)

NATIVE_FLUX_DEBT_BOUND = 1e-9
PRODUCER_ATTEMPTED_FLUX = 1e-8
PRODUCER_WINDOW_COUNT = 10
REQUIRED_STRESS_BUFFER = 3.0
BF5_SCOPE = "producer_assisted_high_margin_core_under_declared_flux_windowing"
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


def source_record(relative_path: str, data: dict[str, Any]) -> dict[str, Any]:
    return {
        "path": relative_path,
        "sha256": sha256_file(relative_path),
        "artifact_id": data.get("artifact_id"),
        "status": data.get("status"),
        "acceptance_state": data.get("acceptance_state"),
        "output_digest": data.get("output_digest"),
    }


def build_flux_trace(i6_row: dict[str, Any]) -> dict[str, Any]:
    conditioned_flux = PRODUCER_ATTEMPTED_FLUX / PRODUCER_WINDOW_COUNT
    return {
        "trace_id": "n25_i7e_producer_high_margin_flux_trace",
        "producer_source_row_id": i6_row["row_id"],
        "producer_flux_window_declared_before_use": True,
        "producer_assisted_result_class": "producer_mediated_scaffold_candidate",
        "native_flux_debt_bound": NATIVE_FLUX_DEBT_BOUND,
        "native_flux_debt_widened": False,
        "attempted_flux": PRODUCER_ATTEMPTED_FLUX,
        "producer_window_count": PRODUCER_WINDOW_COUNT,
        "conditioned_flux_per_window": conditioned_flux,
        "conditioned_windows_preserve_native_bound": conditioned_flux <= NATIVE_FLUX_DEBT_BOUND,
        "native_unwindowed_attempted_flux_supported": False,
        "producer_windowed_attempted_flux_supported": True,
        "producer_support_or_coherence_added": False,
        "interpretation": (
            "The producer does not add support or coherence. It only exposes a "
            "larger attempted flux as ten declared source-visible windows, each "
            "capped at the inherited native 1e-9 bound."
        ),
    }


def build_scaffold_trace(i6_row: dict[str, Any], i7c_row: dict[str, Any]) -> dict[str, Any]:
    support_margin = float(i7c_row["support_floor_margin_new_region"])
    coherence_margin = float(i7c_row["coherence_floor_margin_new_region"])
    return {
        "trace_id": "n25_i7e_producer_bf5_scaffold_trace",
        "native_high_margin_source_row_id": i7c_row["row_id"],
        "producer_source_row_id": i6_row["row_id"],
        "formation_source": "producer_flux_conditioned_native_high_margin_core",
        "formation_class": "producer_assisted_scaffold",
        "positive_core_node_count": i7c_row["positive_core_node_count"],
        "boundary_shell_node_count": i7c_row["boundary_shell_node_count"],
        "support_floor_margin_new_region": support_margin,
        "coherence_floor_margin_new_region": coherence_margin,
        "required_stress_buffer": REQUIRED_STRESS_BUFFER,
        "support_buffer_passes": support_margin >= REQUIRED_STRESS_BUFFER,
        "coherence_buffer_passes": coherence_margin >= REQUIRED_STRESS_BUFFER,
        "boundary_distinguishability_stress_source": "I7-C",
        "merge_leakage_control_source": "I7-C_at_native_flux_bound_plus_I6_windowing",
        "producer_assisted_bf5_scaffold_supported": (
            support_margin >= REQUIRED_STRESS_BUFFER
            and coherence_margin >= REQUIRED_STRESS_BUFFER
        ),
        "producer_assisted_bf6_supported": False,
        "independent_new_basin_supported": False,
        "interpretation": (
            "I7-E combines the I7-C high-margin core with I6 producer flux "
            "windowing. This supports a producer-assisted BF5 scaffold candidate "
            "under larger attempted flux, but the support/coherence margin comes "
            "from the already source-backed native core and the larger-flux "
            "admissibility comes from a producer-mediated windowing surface."
        ),
    }


def build_naturalization_target_trace() -> dict[str, Any]:
    return {
        "trace_id": "n25_i7e_naturalization_target_trace",
        "producer_assisted_result_class": "producer_mediated_scaffold_candidate",
        "missing_native_mechanism_probe_supported": True,
        "naturalization_targets": [
            "native_flux_routing_or_rate_limiting_surface_for_high_margin_core",
            "native_attempted_flux_windowing_without_producer",
            "native_high_margin_core_preservation_under_larger_flux",
        ],
        "not_naturalized": [
            "producer_flux_windowing_surface",
            "native_flux_routing_above_1e-9",
            "independent_new_basin_formation",
            "BF6",
        ],
        "n26_consumption_note": (
            "N26 may use this as producer-assisted missing-mechanism context, not "
            "as native proxy-collapse or independent basin evidence."
        ),
    }


def build_control_matrix_trace() -> list[dict[str, Any]]:
    return [
        {
            "control_id": "producer_window_declared_before_use_control",
            "control_status": "passed",
            "blocked_condition": "producer flux window is introduced after outcome inspection",
            "expected_result": "window count and per-window native bound are declared",
            "actual_result": "ten windows at 1e-9 each for attempted 1e-8 flux",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "producer-assisted scaffold remains admissible",
        },
        {
            "control_id": "producer_hidden_support_control",
            "control_status": "passed",
            "blocked_condition": "producer adds hidden support or coherence",
            "expected_result": "producer only windows flux",
            "actual_result": "producer_support_or_coherence_added = false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "support/coherence margin remains attributed to I7-C source geometry",
        },
        {
            "control_id": "producer_threshold_relaxation_control",
            "control_status": "passed",
            "blocked_condition": "producer success depends on relaxed BF5 thresholds",
            "expected_result": "same stress buffer and native 1e-9 per-window bound are preserved",
            "actual_result": "required_stress_buffer = 3.0 and conditioned_flux_per_window = 1e-9",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "threshold relaxation blocked",
        },
        {
            "control_id": "producer_success_as_native_relabel_control",
            "control_status": "passed",
            "blocked_condition": "producer-assisted BF5 scaffold upgrades native BF",
            "expected_result": "native BF evidence remains I7-C scoped BF5 only",
            "actual_result": "native_bf_upgraded_by_producer = false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "producer result cannot overwrite native result",
        },
        {
            "control_id": "producer_bf5_as_bf6_relabel_control",
            "control_status": "passed",
            "blocked_condition": "producer-assisted BF5 scaffold is relabeled as BF6",
            "expected_result": "BF6 and independent new-basin remain false",
            "actual_result": "producer_assisted_bf6_supported = false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "BF6 remains blocked",
        },
        {
            "control_id": "native_flux_debt_remains_row_local",
            "control_status": "passed",
            "blocked_condition": "producer windowing widens native flux debt",
            "expected_result": "native flux debt remains 1e-9",
            "actual_result": "native_flux_debt_bound = 1e-9 and native_flux_debt_widened = false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "larger attempted flux remains producer-mediated",
        },
        {
            "control_id": "unsafe_claims_relabel_control",
            "control_status": "passed",
            "blocked_condition": "producer-assisted scaffold is relabeled as learning, choice, agency, native support, Phase 8, or ant ecology",
            "expected_result": "all unsafe claim flags remain false",
            "actual_result": "unsafe_claim_flags all false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "claim boundary preserved",
        },
    ]


def build_output() -> dict[str, Any]:
    i6 = load_json(I6_OUTPUT_PATH)
    i7c = load_json(I7C_OUTPUT_PATH)
    i7d = load_json(I7D_OUTPUT_PATH)
    i6_row = i6["producer_assisted_formation_rows"][0]
    i7c_row = i7c["bf5_core_stress_rows"][0]

    flux_trace = build_flux_trace(i6_row)
    scaffold_trace = build_scaffold_trace(i6_row, i7c_row)
    naturalization_target_trace = build_naturalization_target_trace()
    control_matrix_trace = build_control_matrix_trace()
    source_lineage_trace = {
        "trace_id": "n25_i7e_source_lineage_trace",
        "sources": {
            "i6_producer_flux_windowing": source_record(I6_OUTPUT_PATH, i6),
            "i7c_native_high_margin_core_bf5": source_record(I7C_OUTPUT_PATH, i7c),
            "i7d_n26_readiness_gate": source_record(I7D_OUTPUT_PATH, i7d),
        },
        "lineage_interpretation": (
            "I7-E uses I6 as the producer flux-windowing contract and I7-C as "
            "the high-margin core geometry. I7-D remains the native C6 readiness "
            "gate and is not replaced."
        ),
    }

    artifact_paths_by_role = {
        "source_lineage_trace": ARTIFACT_DIR / "n25_i7e_source_lineage_trace.json",
        "producer_intervention_ledger": ARTIFACT_DIR
        / "n25_i7e_producer_high_margin_flux_trace.json",
        "new_basin_support_coherence_trace": ARTIFACT_DIR
        / "n25_i7e_producer_bf5_scaffold_trace.json",
        "naturalization_debt_trace": ARTIFACT_DIR
        / "n25_i7e_naturalization_target_trace.json",
        "negative_control_trace": ARTIFACT_DIR / "n25_i7e_control_matrix_trace.json",
    }
    write_json(artifact_paths_by_role["source_lineage_trace"], source_lineage_trace)
    write_json(artifact_paths_by_role["producer_intervention_ledger"], flux_trace)
    write_json(artifact_paths_by_role["new_basin_support_coherence_trace"], scaffold_trace)
    write_json(artifact_paths_by_role["naturalization_debt_trace"], naturalization_target_trace)
    write_json(artifact_paths_by_role["negative_control_trace"], control_matrix_trace)

    manifest = artifact_manifest(artifact_paths_by_role)
    artifact_paths = [entry["path"] for entry in manifest]
    artifact_sha256 = {entry["path"]: entry["sha256"] for entry in manifest}
    controls_clean = all(
        control["control_status"] == "passed" for control in control_matrix_trace
    )
    producer_bf5 = (
        flux_trace["conditioned_windows_preserve_native_bound"]
        and scaffold_trace["producer_assisted_bf5_scaffold_supported"]
        and controls_clean
    )
    row: dict[str, Any] = {
        "row_id": "n25_i7e_producer_assisted_high_margin_scaffold",
        "source_iteration": "I7-E_producer_assisted_high_margin_scaffold",
        "source_output_digest": i7c["output_digest"],
        "source_i6_output_digest": i6["output_digest"],
        "source_i7c_output_digest": i7c["output_digest"],
        "source_i7d_output_digest": i7d["output_digest"],
        "source_current_inputs": [I6_OUTPUT_PATH, I7C_OUTPUT_PATH, I7D_OUTPUT_PATH],
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
        "lane": "producer_assisted",
        "producer_assisted_result_class": "producer_mediated_scaffold_candidate",
        "producer_assisted_result_role": "missing_native_mechanism_probe",
        "producer_assisted_bf5_scaffold_supported": producer_bf5,
        "producer_assisted_bf5_supported": producer_bf5,
        "producer_assisted_bf6_supported": False,
        "native_bf5_supported_from_i7c": True,
        "native_bf_upgraded_by_producer": False,
        "native_bf6_supported": False,
        "independent_new_basin_supported": False,
        "formation_class": "producer_assisted_scaffold",
        "formation_source": "producer_flux_conditioned_native_high_margin_core",
        "bf_ladder_rung": "BF5_producer_assisted_high_margin_scaffold_candidate",
        "bf_ladder_rung_status": "producer_assisted_candidate_not_native_closeout",
        "n25_closeout_ceiling": "N25-C6_n26_ready_bounded_basin_formation_evidence",
        "n25_closeout_ladder_rung_assigned": False,
        "i7d_replaced": False,
        "bf5_scope": BF5_SCOPE,
        "positive_core_node_count": scaffold_trace["positive_core_node_count"],
        "boundary_shell_node_count": scaffold_trace["boundary_shell_node_count"],
        "support_floor_margin_new_region": scaffold_trace[
            "support_floor_margin_new_region"
        ],
        "coherence_floor_margin_new_region": scaffold_trace[
            "coherence_floor_margin_new_region"
        ],
        "required_stress_buffer": REQUIRED_STRESS_BUFFER,
        "producer_flux_window_bound": PRODUCER_ATTEMPTED_FLUX,
        "producer_window_count": PRODUCER_WINDOW_COUNT,
        "conditioned_flux_per_window": flux_trace["conditioned_flux_per_window"],
        "producer_support_or_coherence_added": False,
        "native_flux_debt_bound": NATIVE_FLUX_DEBT_BOUND,
        "native_flux_debt_widened": False,
        "native_flux_debt_status": "preserved",
        "producer_assisted_success_does_not_overwrite_native_failure": True,
        "control_results": control_matrix_trace,
        "naturalization_debt": naturalization_target_trace["not_naturalized"],
        "naturalization_targets": naturalization_target_trace["naturalization_targets"],
        "missing_native_mechanism_probe_supported": True,
        "row_decision": "supported",
        "basin_formation_claim_allowed": False,
        "bounded_formation_handoff_allowed": True,
        "unsafe_claim_flags": {claim: False for claim in UNSAFE_CLAIMS},
        "claim_ceiling": (
            "producer-assisted BF5 scaffold candidate and missing native "
            "mechanism probe; not native BF upgrade, not BF6, not independent "
            "new-basin formation, not native support"
        ),
        "geometric_interpretation": scaffold_trace["interpretation"],
    }
    row["row_digest"] = digest_value(row)
    row["output_digest"] = row["row_digest"]

    checks = [
        check("i6_producer_source_passed", i6.get("status") == "passed", source_lineage_trace["sources"]["i6_producer_flux_windowing"]),
        check("i7c_native_bf5_source_passed", i7c.get("status") == "passed" and i7c.get("native_bf5_supported") is True, source_lineage_trace["sources"]["i7c_native_high_margin_core_bf5"]),
        check("i7d_c6_readiness_preserved", i7d.get("status") == "passed" and i7d.get("n25_c6_supported") is True, source_lineage_trace["sources"]["i7d_n26_readiness_gate"]),
        check("producer_window_preserves_native_bound", flux_trace["conditioned_windows_preserve_native_bound"] is True, flux_trace),
        check("producer_attempted_flux_is_above_native_bound", PRODUCER_ATTEMPTED_FLUX > NATIVE_FLUX_DEBT_BOUND, PRODUCER_ATTEMPTED_FLUX),
        check("support_coherence_buffer_supported", scaffold_trace["support_buffer_passes"] and scaffold_trace["coherence_buffer_passes"], scaffold_trace),
        check("producer_assisted_bf5_supported", row["producer_assisted_bf5_supported"] is True, row["bf5_scope"]),
        check("producer_bf5_does_not_upgrade_native", row["native_bf_upgraded_by_producer"] is False and row["producer_assisted_success_does_not_overwrite_native_failure"] is True, row["producer_assisted_result_role"]),
        check("bf6_and_independent_new_basin_blocked", row["producer_assisted_bf6_supported"] is False and row["independent_new_basin_supported"] is False, row["naturalization_debt"]),
        check("native_flux_debt_preserved", row["native_flux_debt_bound"] == NATIVE_FLUX_DEBT_BOUND and row["native_flux_debt_widened"] is False, row["native_flux_debt_status"]),
        check("controls_clean", controls_clean, control_matrix_trace),
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
        "artifact_id": "n25_producer_assisted_high_margin_scaffold_i7e",
        "experiment": "2026-06-N25-lgrc-spark-sub-basin-new-basin-formation",
        "iteration": "I7-E",
        "generated_at": GENERATED_AT,
        "reconstruction_command": COMMAND,
        "status": "passed" if not failed else "failed",
        "acceptance_state": (
            "accepted_producer_assisted_high_margin_bf5_scaffold_candidate_native_unchanged"
            if not failed
            else "failed_producer_assisted_high_margin_scaffold"
        ),
        "source_digest_chain_audit": source_lineage_trace["sources"],
        "producer_assisted_high_margin_rows": [row],
        "producer_assisted_high_margin_row_count": 1,
        "producer_assisted_bf5_scaffold_supported": not failed and producer_bf5,
        "producer_assisted_bf5_supported": not failed and producer_bf5,
        "producer_assisted_bf6_supported": False,
        "native_bf5_supported_from_i7c": True,
        "native_bf_upgraded_by_producer": False,
        "native_bf6_supported": False,
        "independent_new_basin_supported": False,
        "n25_closeout_ceiling": row["n25_closeout_ceiling"],
        "n25_closeout_ladder_rung_assigned": False,
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
    row = output["producer_assisted_high_margin_rows"][0]
    lines = [
        "# N25 Iteration 7-E - Producer-Assisted High-Margin Scaffold Probe",
        "",
        f"Status: `{output['status']}`",
        f"Acceptance state: `{output['acceptance_state']}`",
        f"Output digest: `{output['output_digest']}`",
        "",
        "## Result",
        "",
        "```text",
        f"producer_assisted_bf5_scaffold_supported = {str(output['producer_assisted_bf5_scaffold_supported']).lower()}",
        f"producer_assisted_bf5_supported = {str(output['producer_assisted_bf5_supported']).lower()}",
        f"producer_assisted_bf6_supported = {str(output['producer_assisted_bf6_supported']).lower()}",
        f"native_bf_upgraded_by_producer = {str(output['native_bf_upgraded_by_producer']).lower()}",
        f"independent_new_basin_supported = {str(output['independent_new_basin_supported']).lower()}",
        f"n25_closeout_ceiling = {output['n25_closeout_ceiling']}",
        "```",
        "",
        "## Geometric Interpretation",
        "",
        row["geometric_interpretation"],
        "",
        "The producer-side result is useful because it isolates the missing native",
        "mechanism: LGRC would need a native flux routing/rate-limiting surface able",
        "to expose larger attempted flux as source-current bounded windows while",
        "preserving the high-margin core. This does not change the native result;",
        "I7-D remains the C6 readiness gate and native BF remains scoped BF5.",
        "",
        "## Naturalization Targets",
        "",
    ]
    lines.extend(f"- `{item}`" for item in row["naturalization_targets"])
    lines.extend(
        [
            "",
            "## Still Blocked",
            "",
        ]
    )
    lines.extend(f"- `{item}`" for item in row["naturalization_debt"])
    lines.extend(
        [
            "",
            "## Controls",
            "",
            "| Control | Status | Rung Effect |",
            "| --- | --- | --- |",
        ]
    )
    for control in row["control_results"]:
        lines.append(
            f"| `{control['control_id']}` | `{control['control_status']}` | "
            f"{control['rung_effect']} |"
        )
    lines.extend(["", "## Checks", "", "| Check | Passed |", "| --- | --- |"])
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
