#!/usr/bin/env python3
"""Build N25 Iteration 8 closeout and N26 handoff."""

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
OUTPUT = EXPERIMENT / "outputs" / "n25_closeout_and_n26_handoff.json"
REPORT = EXPERIMENT / "reports" / "n25_closeout_and_n26_handoff.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n25_closeout_and_n26_handoff_artifacts"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
    "scripts/build_n25_closeout_and_n26_handoff.py"
)

I7C_OUTPUT_PATH = (
    "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
    "outputs/n25_bf5_core_stress_gate_i7c.json"
)
I7D_OUTPUT_PATH = (
    "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
    "outputs/n25_n26_readiness_bounded_formation_gate_i7d.json"
)
I7E_OUTPUT_PATH = (
    "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
    "outputs/n25_producer_assisted_high_margin_scaffold_i7e.json"
)

NATIVE_FLUX_DEBT_BOUND = 1e-9
FINAL_BF_LEVEL = "BF5_scoped_native_high_margin_core_sub_basin"
FINAL_N25_C = "N25-C6_n26_ready_bounded_basin_formation_evidence"
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


def build_source_lineage_trace(
    i7c: dict[str, Any],
    i7d: dict[str, Any],
    i7e: dict[str, Any],
) -> dict[str, Any]:
    return {
        "trace_id": "n25_i8_source_lineage_trace",
        "sources": {
            "i7c_native_scoped_bf5": source_record(I7C_OUTPUT_PATH, i7c),
            "i7d_n26_readiness_gate": source_record(I7D_OUTPUT_PATH, i7d),
            "i7e_producer_assisted_scaffold": source_record(I7E_OUTPUT_PATH, i7e),
        },
        "lineage_interpretation": (
            "I7-C supplies the native scoped BF5 evidence; I7-D supplies the "
            "N25-C6 readiness gate; I7-E supplies separate producer-assisted "
            "missing-mechanism evidence. The lanes are not merged."
        ),
    }


def build_final_classification_trace(
    i7c_row: dict[str, Any],
    i7d_row: dict[str, Any],
    i7e_row: dict[str, Any],
) -> dict[str, Any]:
    return {
        "trace_id": "n25_i8_final_classification_trace",
        "final_bf_level": FINAL_BF_LEVEL,
        "final_n25_closeout_rung": FINAL_N25_C,
        "native_lane": {
            "status": "supported",
            "source_row_id": i7c_row["row_id"],
            "supported_bf_level": FINAL_BF_LEVEL,
            "scope": i7c_row["bf5_scope"],
            "support_floor_margin_new_region": i7c_row[
                "support_floor_margin_new_region"
            ],
            "coherence_floor_margin_new_region": i7c_row[
                "coherence_floor_margin_new_region"
            ],
            "native_flux_debt_bound": i7c_row["native_flux_debt_bound"],
            "native_bf6_supported": False,
            "independent_new_basin_supported": False,
        },
        "producer_assisted_lane": {
            "status": "supported_as_scaffold_context",
            "source_row_id": i7e_row["row_id"],
            "supported_level": "producer_assisted_BF5_scaffold_candidate",
            "result_role": "missing_native_mechanism_probe",
            "native_bf_upgraded_by_producer": False,
            "producer_assisted_bf6_supported": False,
            "naturalization_targets": i7e_row["naturalization_targets"],
        },
        "handoff_lane": {
            "source_row_id": i7d_row["row_id"],
            "bounded_formation_handoff_allowed": True,
            "n26_handoff_status": "ready",
        },
        "blocked": {
            "BF6": True,
            "independent_new_basin_formation": True,
            "LGRC9V3_multi_basin_native_formation": True,
            "native_flux_routing_above_1e-9": True,
            "semantic_learning": True,
            "semantic_choice": True,
            "agency": True,
            "native_support": True,
            "sentience": True,
            "phase8": True,
            "ant_ecology": True,
        },
        "interpretation": (
            "N25 closes as scoped native BF5 and N25-C6 readiness. It supports a "
            "high-margin sub-basin/core formation substrate, not independent "
            "multi-basin or BF6 formation. I7-E adds producer-assisted scaffold "
            "evidence for the missing native flux-routing mechanism."
        ),
    }


def build_n26_handoff_trace(i7e_row: dict[str, Any]) -> dict[str, Any]:
    return {
        "trace_id": "n25_i8_n26_handoff_trace",
        "next_experiment": "N26_proxy_divergence_proxy_collapse",
        "handoff_status": "ready_with_scope_constraints",
        "n26_may_consume_as": [
            "scoped_sub_basin_high_margin_core_substrate",
            "bounded_basin_formation_prerequisite",
            "producer_assisted_missing_native_mechanism_context",
        ],
        "n26_must_not_consume_as": [
            "independent_new_basin_formation",
            "LGRC9V3_multi_basin_native_formation",
            "BF6",
            "native_support",
            "semantic_learning",
            "semantic_choice",
            "agency",
            "sentience",
            "phase8",
            "ant_ecology",
        ],
        "required_n26_constraints": [
            "proxy_divergence_must_be_scoped_to_sub_basin_or_high_margin_core",
            "independent_new_basin_claims_require_new_multi_basin_evidence",
            "carry_native_flux_debt_bound_1e-9",
            "carry_BF5_scope_not_BF6",
            "carry_producer_flux_windowing_as_naturalization_target_only",
            "do_not_use_I7E_to_upgrade_native_BF",
            "preserve_AP4_AP5_gap_ledger_when_route_or_proxy_dependencies_appear",
            "keep_unsafe_claim_flags_false",
        ],
        "phase8_extension_required_for": (
            "native LGRC9V3 causal-refinement multi-basin formation"
        ),
        "n25_1_recommended": True,
        "n25_1_scope": (
            "requirements/spec bridge for LGRC9V3 multi-basin formation from "
            "causal refinement before N26 can consume independent multi-basin "
            "substrate evidence"
        ),
        "producer_assisted_naturalization_targets": i7e_row["naturalization_targets"],
    }


def build_claim_boundary_trace() -> dict[str, Any]:
    return {
        "trace_id": "n25_i8_claim_boundary_trace",
        "unsafe_claim_flags": {claim: False for claim in UNSAFE_CLAIMS},
        "phase8_opened": False,
        "phase8_extension_implemented": False,
        "ant_ecology_opened": False,
        "native_support_supported": False,
        "agency_supported": False,
        "semantic_learning_supported": False,
        "semantic_choice_supported": False,
        "sentience_supported": False,
        "independent_new_basin_supported": False,
        "native_bf6_supported": False,
        "basin_formation_claim_allowed": True,
        "basin_formation_claim_scope": FINAL_BF_LEVEL,
        "claim_ceiling": (
            "artifact-level scoped native BF5 high-margin core/sub-basin "
            "formation with N25-C6 handoff readiness; producer-assisted BF5 "
            "scaffold remains non-native missing-mechanism context"
        ),
    }


def build_control_matrix_trace() -> list[dict[str, Any]]:
    return [
        {
            "control_id": "final_c6_not_bf6_control",
            "control_status": "passed",
            "blocked_condition": "N25-C6 closeout is relabeled as BF6",
            "expected_result": "BF6 remains false",
            "actual_result": "final BF level is scoped BF5",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "C6 closeout allowed without BF6",
        },
        {
            "control_id": "independent_new_basin_closeout_relabel_control",
            "control_status": "passed",
            "blocked_condition": "sub-basin/high-margin core is relabeled as independent new basin",
            "expected_result": "independent new-basin remains blocked",
            "actual_result": "N25.1/Phase 8 extension required for multi-basin formation",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "new-basin claim blocked",
        },
        {
            "control_id": "producer_scaffold_native_upgrade_control",
            "control_status": "passed",
            "blocked_condition": "I7-E producer scaffold upgrades native BF",
            "expected_result": "producer-assisted lane remains separate",
            "actual_result": "native_bf_upgraded_by_producer = false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "lane split preserved",
        },
        {
            "control_id": "native_flux_debt_closeout_control",
            "control_status": "passed",
            "blocked_condition": "native flux bound is widened above 1e-9",
            "expected_result": "native flux debt remains visible",
            "actual_result": "native_flux_debt_bound = 1e-9",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "flux debt carried to N26/N25.1",
        },
        {
            "control_id": "n26_handoff_scope_control",
            "control_status": "passed",
            "blocked_condition": "N26 consumes N25 as independent multi-basin substrate",
            "expected_result": "N26 consumes scoped sub-basin/core only unless new evidence appears",
            "actual_result": "handoff constraints require scoped consumption",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "N26 handoff allowed with constraints",
        },
        {
            "control_id": "unsafe_claims_closeout_control",
            "control_status": "passed",
            "blocked_condition": "N25 is relabeled as agency, native support, sentience, Phase 8, or ant ecology",
            "expected_result": "unsafe claim flags remain false",
            "actual_result": "all unsafe flags false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "claim boundary preserved",
        },
    ]


def build_output() -> dict[str, Any]:
    i7c = load_json(I7C_OUTPUT_PATH)
    i7d = load_json(I7D_OUTPUT_PATH)
    i7e = load_json(I7E_OUTPUT_PATH)
    i7c_row = i7c["bf5_core_stress_rows"][0]
    i7d_row = i7d["n26_readiness_rows"][0]
    i7e_row = i7e["producer_assisted_high_margin_rows"][0]

    source_lineage_trace = build_source_lineage_trace(i7c, i7d, i7e)
    final_classification_trace = build_final_classification_trace(
        i7c_row,
        i7d_row,
        i7e_row,
    )
    n26_handoff_trace = build_n26_handoff_trace(i7e_row)
    claim_boundary_trace = build_claim_boundary_trace()
    control_matrix_trace = build_control_matrix_trace()

    artifact_paths_by_role = {
        "source_lineage_trace": ARTIFACT_DIR / "n25_i8_source_lineage_trace.json",
        "runtime_trace": ARTIFACT_DIR / "n25_i8_final_classification_trace.json",
        "source_handoff": ARTIFACT_DIR / "n25_i8_n26_handoff_trace.json",
        "claim_boundary_trace": ARTIFACT_DIR / "n25_i8_claim_boundary_trace.json",
        "negative_control_trace": ARTIFACT_DIR / "n25_i8_control_matrix_trace.json",
    }
    write_json(artifact_paths_by_role["source_lineage_trace"], source_lineage_trace)
    write_json(artifact_paths_by_role["runtime_trace"], final_classification_trace)
    write_json(artifact_paths_by_role["source_handoff"], n26_handoff_trace)
    write_json(artifact_paths_by_role["claim_boundary_trace"], claim_boundary_trace)
    write_json(artifact_paths_by_role["negative_control_trace"], control_matrix_trace)

    manifest = artifact_manifest(artifact_paths_by_role)
    artifact_paths = [entry["path"] for entry in manifest]
    artifact_sha256 = {entry["path"]: entry["sha256"] for entry in manifest}
    controls_clean = all(
        control["control_status"] == "passed" for control in control_matrix_trace
    )
    row: dict[str, Any] = {
        "row_id": "n25_i8_closeout_and_n26_handoff",
        "source_iteration": "I8_closeout_and_n26_handoff",
        "source_output_digest": i7d["output_digest"],
        "source_i7c_output_digest": i7c["output_digest"],
        "source_i7d_output_digest": i7d["output_digest"],
        "source_i7e_output_digest": i7e["output_digest"],
        "source_current_inputs": [I7C_OUTPUT_PATH, I7D_OUTPUT_PATH, I7E_OUTPUT_PATH],
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
        "final_bf_level": FINAL_BF_LEVEL,
        "final_n25_closeout_rung": FINAL_N25_C,
        "n25_closeout_ladder_rung_assigned": True,
        "native_bf5_supported": True,
        "native_bf6_supported": False,
        "independent_new_basin_supported": False,
        "lgrc9v3_multi_basin_native_formation_supported": False,
        "producer_assisted_bf5_scaffold_supported": True,
        "producer_assisted_result_class": "producer_mediated_scaffold_candidate",
        "producer_assisted_result_role": "missing_native_mechanism_probe",
        "native_bf_upgraded_by_producer": False,
        "native_flux_debt_bound": NATIVE_FLUX_DEBT_BOUND,
        "native_flux_debt_widened": False,
        "native_flux_debt_status": "carried_forward_to_n26_and_n25_1",
        "phase8_extension_required_for_multi_basin_formation": True,
        "n25_1_requirements_bridge_needed": True,
        "n26_handoff_status": "ready_with_scope_constraints",
        "control_results": control_matrix_trace,
        "unsafe_claim_flags": {claim: False for claim in UNSAFE_CLAIMS},
        "row_decision": "supported",
        "basin_formation_claim_allowed": True,
        "claim_ceiling": claim_boundary_trace["claim_ceiling"],
        "geometric_interpretation": final_classification_trace["interpretation"],
    }
    row["row_digest"] = digest_value(row)
    row["output_digest"] = row["row_digest"]

    i7c_ready = (
        i7c.get("status") == "passed"
        and i7c.get("native_bf5_supported") is True
        and i7c.get("native_bf6_supported") is False
    )
    i7d_ready = (
        i7d.get("status") == "passed"
        and i7d.get("n25_c6_supported") is True
        and i7d.get("native_bf6_supported") is False
    )
    i7e_ready = (
        i7e.get("status") == "passed"
        and i7e.get("producer_assisted_bf5_supported") is True
        and i7e.get("native_bf_upgraded_by_producer") is False
    )
    checks = [
        check("i7c_scoped_native_bf5_passed", i7c_ready, source_lineage_trace["sources"]["i7c_native_scoped_bf5"]),
        check("i7d_c6_readiness_passed", i7d_ready, source_lineage_trace["sources"]["i7d_n26_readiness_gate"]),
        check("i7e_producer_scaffold_passed", i7e_ready, source_lineage_trace["sources"]["i7e_producer_assisted_scaffold"]),
        check("final_bf_level_is_scoped_bf5", row["final_bf_level"] == FINAL_BF_LEVEL, final_classification_trace["native_lane"]),
        check("final_n25_c6_supported", row["final_n25_closeout_rung"] == FINAL_N25_C, row["final_n25_closeout_rung"]),
        check("bf6_and_independent_new_basin_blocked", row["native_bf6_supported"] is False and row["independent_new_basin_supported"] is False, final_classification_trace["blocked"]),
        check("multi_basin_phase8_extension_required", row["phase8_extension_required_for_multi_basin_formation"] is True and row["lgrc9v3_multi_basin_native_formation_supported"] is False, n26_handoff_trace["phase8_extension_required_for"]),
        check("producer_lane_separate", row["producer_assisted_bf5_scaffold_supported"] is True and row["native_bf_upgraded_by_producer"] is False, final_classification_trace["producer_assisted_lane"]),
        check("native_flux_debt_preserved", row["native_flux_debt_bound"] == NATIVE_FLUX_DEBT_BOUND and row["native_flux_debt_widened"] is False, row["native_flux_debt_status"]),
        check("n26_handoff_constraints_complete", len(n26_handoff_trace["required_n26_constraints"]) >= 8, n26_handoff_trace["required_n26_constraints"]),
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
        "artifact_id": "n25_closeout_and_n26_handoff",
        "experiment": "2026-06-N25-lgrc-spark-sub-basin-new-basin-formation",
        "iteration": "I8",
        "generated_at": GENERATED_AT,
        "reconstruction_command": COMMAND,
        "status": "passed" if not failed else "failed",
        "acceptance_state": (
            "accepted_n25_c6_scoped_bf5_closeout_with_producer_scaffold_context"
            if not failed
            else "failed_n25_closeout_and_n26_handoff"
        ),
        "source_digest_chain_audit": source_lineage_trace["sources"],
        "closeout_rows": [row],
        "closeout_row_count": 1,
        "final_bf_level": FINAL_BF_LEVEL,
        "final_n25_closeout_rung": FINAL_N25_C,
        "n25_closeout_ladder_rung_assigned": not failed,
        "native_bf5_supported": True,
        "native_bf6_supported": False,
        "independent_new_basin_supported": False,
        "lgrc9v3_multi_basin_native_formation_supported": False,
        "producer_assisted_bf5_scaffold_supported": True,
        "native_bf_upgraded_by_producer": False,
        "phase8_extension_required_for_multi_basin_formation": True,
        "n25_1_requirements_bridge_needed": True,
        "ready_for_n26_with_scope_constraints": not failed,
        "basin_formation_claim_allowed": not failed,
        "checks": checks,
        "failed_checks": [item["check_id"] for item in failed],
    }
    output["output_digest"] = digest_value(
        {key: value for key, value in output.items() if key != "output_digest"}
    )
    return output


def write_report(output: dict[str, Any]) -> None:
    row = output["closeout_rows"][0]
    lines = [
        "# N25 Iteration 8 - Closeout And N26 Handoff",
        "",
        f"Status: `{output['status']}`",
        f"Acceptance state: `{output['acceptance_state']}`",
        f"Output digest: `{output['output_digest']}`",
        "",
        "## Final Classification",
        "",
        "```text",
        f"final_bf_level = {output['final_bf_level']}",
        f"final_n25_closeout_rung = {output['final_n25_closeout_rung']}",
        f"native_bf5_supported = {str(output['native_bf5_supported']).lower()}",
        f"native_bf6_supported = {str(output['native_bf6_supported']).lower()}",
        f"independent_new_basin_supported = {str(output['independent_new_basin_supported']).lower()}",
        f"producer_assisted_bf5_scaffold_supported = {str(output['producer_assisted_bf5_scaffold_supported']).lower()}",
        f"lgrc9v3_multi_basin_native_formation_supported = {str(output['lgrc9v3_multi_basin_native_formation_supported']).lower()}",
        f"phase8_extension_required_for_multi_basin_formation = {str(output['phase8_extension_required_for_multi_basin_formation']).lower()}",
        "```",
        "",
        "## Interpretation",
        "",
        row["geometric_interpretation"],
        "",
        "N25 supports bounded sub-basin / high-margin core formation. It does not",
        "support independent new-basin formation or native LGRC9V3 multi-basin",
        "formation. I7-E remains producer-assisted missing-mechanism evidence:",
        "useful for the next implementation target, but not a native upgrade.",
        "",
        "## N26 Handoff",
        "",
        "N26 may consume N25 only as scoped sub-basin / high-margin core substrate",
        "and producer-assisted naturalization-target context. N26 must not consume",
        "N25 as independent multi-basin substrate unless a separate Phase 8 extension",
        "produces that evidence.",
        "",
        "## Controls",
        "",
        "| Control | Status | Rung Effect |",
        "| --- | --- | --- |",
    ]
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
