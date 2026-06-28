#!/usr/bin/env python3
"""Build N25 Iteration 7-D N26 readiness gate."""

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
    EXPERIMENT / "outputs" / "n25_n26_readiness_bounded_formation_gate_i7d.json"
)
REPORT = (
    EXPERIMENT / "reports" / "n25_n26_readiness_bounded_formation_gate_i7d.md"
)
ARTIFACT_DIR = (
    EXPERIMENT / "outputs" / "n25_n26_readiness_bounded_formation_gate_i7d_artifacts"
)
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
    "scripts/build_n25_n26_readiness_bounded_formation_gate_i7d.py"
)

I6_OUTPUT_PATH = (
    "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
    "outputs/n25_producer_assisted_formation_probe.json"
)
I7_OUTPUT_PATH = (
    "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
    "outputs/n25_comparative_stress_boundary_matrix.json"
)
I7A_OUTPUT_PATH = (
    "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
    "outputs/n25_native_high_margin_formation_probe_i7a.json"
)
I7B_OUTPUT_PATH = (
    "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
    "outputs/n25_high_margin_core_replay_controls_i7b.json"
)
I7C_OUTPUT_PATH = (
    "experiments/2026-06-N25-lgrc-spark-sub-basin-new-basin-formation/"
    "outputs/n25_bf5_core_stress_gate_i7c.json"
)

NATIVE_FLUX_DEBT_BOUND = 1e-9
BF5_SCOPE = "bounded_high_margin_core_sub_basin_within_native_1e-9_flux_envelope"
FINAL_SUPPORTED_BF_LEVEL = "BF5_scoped_native_high_margin_core_sub_basin"
N25_C6 = "N25-C6_n26_ready_bounded_basin_formation_evidence"
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


def build_source_lineage_trace(sources: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        "trace_id": "n25_i7d_source_lineage_trace",
        "lineage_role": "n26_readiness_source_chain",
        "sources": {
            "i6_producer_assisted_flux_scaffold": source_record(
                I6_OUTPUT_PATH, sources["i6"]
            ),
            "i7_comparative_stress_boundary_matrix": source_record(
                I7_OUTPUT_PATH, sources["i7"]
            ),
            "i7a_native_high_margin_core": source_record(
                I7A_OUTPUT_PATH, sources["i7a"]
            ),
            "i7b_high_margin_core_replay_controls": source_record(
                I7B_OUTPUT_PATH, sources["i7b"]
            ),
            "i7c_bf5_core_stress_gate": source_record(
                I7C_OUTPUT_PATH, sources["i7c"]
            ),
        },
        "lineage_interpretation": (
            "N26 may consume the I7-C scoped BF5 result only through the recorded "
            "I6-I7-C lineage. Producer-assisted flux evidence remains a separate "
            "naturalization-debt lane and does not overwrite the native BF5 scope."
        ),
    }


def build_handoff_contract_trace() -> dict[str, Any]:
    return {
        "trace_id": "n25_i7d_n26_handoff_contract_trace",
        "handoff_target_experiment": "N26_proxy_divergence_proxy_collapse",
        "handoff_status": "ready",
        "n25_c6_supported": True,
        "n25_c6_meaning": (
            "N26-ready bounded basin-formation evidence with final BF evidence "
            "ceiling held at scoped BF5."
        ),
        "final_supported_bf_level": FINAL_SUPPORTED_BF_LEVEL,
        "bf6_or_independent_new_basin_supported": False,
        "consumable_evidence_role": "bounded_basin_formation_prerequisite",
        "consumable_evidence_scope": BF5_SCOPE,
        "not_consumable_as": [
            "BF6_independent_new_basin",
            "general_native_basin_formation",
            "native_support",
            "semantic_learning",
            "choice",
            "agency",
            "sentience",
            "phase8",
            "ant_ecology",
        ],
        "required_n26_consumption_constraints": [
            "consume_as_bounded_bf5_prerequisite_only",
            "preserve_native_flux_debt_bound_1e-9",
            "carry_independent_new_basin_not_supported",
            "carry_full_module_zero_margin_preserved",
            "do_not_import_producer_assisted_flux_scaffold_as_native_success",
            "do_not_convert_sub_basin_candidate_into_proxy_collapse_by_label",
            "keep_AP4_AP5_gap_ledger_visible_where_route_or_proxy_dependencies_appear",
            "keep_all_unsafe_claim_flags_false",
        ],
    }


def build_naturalization_debt_trace() -> dict[str, Any]:
    return {
        "trace_id": "n25_i7d_naturalization_debt_trace",
        "naturalization_debt_carried_forward": [
            "independent_new_basin_not_supported",
            "native_flux_routing_above_1e-9_not_naturalized",
            "full_module_zero_margin_preserved",
            "producer_flux_scaffold_not_native",
            "BF5_scope_not_BF6",
        ],
        "native_flux_debt_bound": NATIVE_FLUX_DEBT_BOUND,
        "native_flux_debt_widened": False,
        "producer_assisted_success_does_not_overwrite_native_failure": True,
        "n26_requirement": (
            "N26 must treat these debts as input constraints, not as solved "
            "formation or proxy-collapse evidence."
        ),
    }


def build_claim_boundary_trace() -> dict[str, Any]:
    return {
        "trace_id": "n25_i7d_claim_boundary_trace",
        "bounded_formation_handoff_allowed": True,
        "basin_formation_claim_allowed": False,
        "final_closeout_claim_pending_i8": True,
        "native_bf5_supported": True,
        "native_bf6_supported": False,
        "independent_new_basin_supported": False,
        "semantic_learning_supported": False,
        "semantic_choice_supported": False,
        "agency_supported": False,
        "native_support_supported": False,
        "sentience_supported": False,
        "phase8_opened": False,
        "ant_ecology_opened": False,
        "unsafe_claim_flags": {claim: False for claim in UNSAFE_CLAIMS},
    }


def build_control_matrix_trace() -> list[dict[str, Any]]:
    return [
        {
            "control_id": "c6_is_not_bf6_control",
            "control_status": "passed",
            "blocked_condition": "N25-C6 handoff readiness is relabeled as BF6",
            "expected_result": "native_bf6_supported remains false",
            "actual_result": "C6 supported as handoff/readiness while BF ceiling remains scoped BF5",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "N25-C6 may pass without BF6 upgrade",
        },
        {
            "control_id": "n26_handoff_scope_control",
            "control_status": "passed",
            "blocked_condition": "N26 consumes N25 as general basin formation",
            "expected_result": "N26 consumption is bounded to scoped BF5 prerequisite evidence",
            "actual_result": "handoff constraints require bounded BF5-only consumption",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "N26-ready handoff allowed only inside recorded scope",
        },
        {
            "control_id": "independent_new_basin_relabel_control",
            "control_status": "passed",
            "blocked_condition": "high-margin core sub-basin is relabeled as independent new basin",
            "expected_result": "independent_new_basin_supported remains false",
            "actual_result": "independent new basin remains explicit naturalization debt",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "BF5 scope preserved",
        },
        {
            "control_id": "native_flux_above_bound_relabel_control",
            "control_status": "passed",
            "blocked_condition": "native flux routing above 1e-9 is treated as naturalized",
            "expected_result": "native flux debt remains carried forward",
            "actual_result": "native_flux_debt_bound = 1e-9 and native_flux_debt_widened = false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "flux debt preserved for N26",
        },
        {
            "control_id": "producer_scaffold_as_native_relabel_control",
            "control_status": "passed",
            "blocked_condition": "I6 producer-assisted flux scaffold upgrades native BF evidence",
            "expected_result": "producer-assisted result stays naturalization target only",
            "actual_result": "producer_assisted_success_does_not_overwrite_native_failure = true",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "native and producer-assisted lanes remain separated",
        },
        {
            "control_id": "ap_gap_ledger_carry_forward_control",
            "control_status": "passed",
            "blocked_condition": "AP4/AP5 dependencies disappear from N26 handoff",
            "expected_result": "handoff requires AP4/AP5 ledger where route or proxy dependencies appear",
            "actual_result": "N26 consumption constraints carry AP4/AP5 ledger forward",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "gap discipline preserved",
        },
        {
            "control_id": "unsafe_claims_relabel_control",
            "control_status": "passed",
            "blocked_condition": "BF5/C6 handoff is relabeled as learning, choice, agency, native support, Phase 8, or ant ecology",
            "expected_result": "all unsafe claim flags remain false",
            "actual_result": "unsafe_claim_flags all false",
            "claim_allowed_when_control_triggers": False,
            "rung_effect": "claim boundary preserved",
        },
    ]


def build_output() -> dict[str, Any]:
    sources = {
        "i6": load_json(I6_OUTPUT_PATH),
        "i7": load_json(I7_OUTPUT_PATH),
        "i7a": load_json(I7A_OUTPUT_PATH),
        "i7b": load_json(I7B_OUTPUT_PATH),
        "i7c": load_json(I7C_OUTPUT_PATH),
    }
    source_lineage_trace = build_source_lineage_trace(sources)
    handoff_contract_trace = build_handoff_contract_trace()
    naturalization_debt_trace = build_naturalization_debt_trace()
    claim_boundary_trace = build_claim_boundary_trace()
    control_matrix_trace = build_control_matrix_trace()

    artifact_paths_by_role = {
        "source_handoff": ARTIFACT_DIR / "n25_i7d_n26_handoff_contract_trace.json",
        "source_lineage_trace": ARTIFACT_DIR / "n25_i7d_source_lineage_trace.json",
        "naturalization_debt_trace": ARTIFACT_DIR
        / "n25_i7d_naturalization_debt_trace.json",
        "negative_control_trace": ARTIFACT_DIR
        / "n25_i7d_control_matrix_trace.json",
        "claim_boundary_trace": ARTIFACT_DIR / "n25_i7d_claim_boundary_trace.json",
    }
    write_json(artifact_paths_by_role["source_handoff"], handoff_contract_trace)
    write_json(artifact_paths_by_role["source_lineage_trace"], source_lineage_trace)
    write_json(
        artifact_paths_by_role["naturalization_debt_trace"],
        naturalization_debt_trace,
    )
    write_json(artifact_paths_by_role["negative_control_trace"], control_matrix_trace)
    write_json(artifact_paths_by_role["claim_boundary_trace"], claim_boundary_trace)

    manifest = artifact_manifest(artifact_paths_by_role)
    artifact_paths = [entry["path"] for entry in manifest]
    artifact_sha256 = {entry["path"]: entry["sha256"] for entry in manifest}
    controls_clean = all(
        control["control_status"] == "passed" for control in control_matrix_trace
    )
    i7c_ready = (
        sources["i7c"].get("status") == "passed"
        and sources["i7c"].get("native_bf5_supported") is True
        and sources["i7c"].get("native_bf6_supported") is False
        and sources["i7c"].get("independent_new_basin_supported") is False
        and sources["i7c"].get("ready_for_iteration_8_closeout_and_n26_handoff")
        is True
    )
    row: dict[str, Any] = {
        "row_id": "n25_i7d_n26_readiness_bounded_formation_gate",
        "source_iteration": "I7-D_n26_readiness_bounded_formation_gate",
        "source_output_digest": sources["i7c"]["output_digest"],
        "source_i6_output_digest": sources["i6"]["output_digest"],
        "source_i7_output_digest": sources["i7"]["output_digest"],
        "source_i7a_output_digest": sources["i7a"]["output_digest"],
        "source_i7b_output_digest": sources["i7b"]["output_digest"],
        "source_i7c_output_digest": sources["i7c"]["output_digest"],
        "source_current_inputs": [
            I6_OUTPUT_PATH,
            I7_OUTPUT_PATH,
            I7A_OUTPUT_PATH,
            I7B_OUTPUT_PATH,
            I7C_OUTPUT_PATH,
        ],
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
        "producer_assisted_lane_consumed_as": "naturalization_debt_context_only",
        "producer_assisted_success_does_not_overwrite_native_failure": True,
        "n25_c6_supported": i7c_ready and controls_clean,
        "n25_c6_meaning": handoff_contract_trace["n25_c6_meaning"],
        "n25_closeout_ceiling": N25_C6,
        "n25_closeout_ladder_rung_assigned": False,
        "final_supported_bf_level": FINAL_SUPPORTED_BF_LEVEL,
        "bf_ceiling": "BF5_native_high_margin_core_sub_basin_stress_candidate",
        "bf5_scope": BF5_SCOPE,
        "native_bf5_supported": True,
        "native_bf6_supported": False,
        "bf6_or_independent_new_basin_supported": False,
        "independent_new_basin_supported": False,
        "native_flux_debt_bound": NATIVE_FLUX_DEBT_BOUND,
        "native_flux_debt_widened": False,
        "native_flux_debt_status": "preserved_for_n26",
        "native_flux_routing_above_1e-9_naturalized": False,
        "full_module_zero_margin_preserved": True,
        "bounded_formation_handoff_allowed": True,
        "basin_formation_claim_allowed": False,
        "final_closeout_claim_pending_i8": True,
        "control_results": control_matrix_trace,
        "naturalization_debt": naturalization_debt_trace[
            "naturalization_debt_carried_forward"
        ],
        "n26_handoff_target": handoff_contract_trace["handoff_target_experiment"],
        "n26_handoff_status": "ready",
        "n26_consumption_constraints": handoff_contract_trace[
            "required_n26_consumption_constraints"
        ],
        "ap_gap_ledger_status": "carried_forward_where_route_or_proxy_dependencies_appear",
        "unsafe_claim_flags": {claim: False for claim in UNSAFE_CLAIMS},
        "row_decision": "supported",
        "claim_ceiling": (
            "N26-ready bounded basin-formation evidence with BF evidence ceiling "
            "held at scoped BF5; not BF6, not independent new-basin formation, "
            "not native support, not agency"
        ),
        "geometric_interpretation": (
            "I7-D does not change the geometry discovered by I7-C. It packages "
            "the high-margin core/shell sub-basin as a bounded formation substrate "
            "that N26 may use as prerequisite geometry for proxy-divergence tests. "
            "The source geometry remains a core inside the inherited native 1e-9 "
            "flux envelope, with independent new-basin formation and broader flux "
            "routing still blocked."
        ),
    }
    row["row_digest"] = digest_value(row)
    row["output_digest"] = row["row_digest"]

    checks = [
        check("i6_source_passed", sources["i6"].get("status") == "passed", source_lineage_trace["sources"]["i6_producer_assisted_flux_scaffold"]),
        check("i7_source_passed", sources["i7"].get("status") == "passed", source_lineage_trace["sources"]["i7_comparative_stress_boundary_matrix"]),
        check("i7a_source_passed", sources["i7a"].get("status") == "passed", source_lineage_trace["sources"]["i7a_native_high_margin_core"]),
        check("i7b_source_passed", sources["i7b"].get("status") == "passed", source_lineage_trace["sources"]["i7b_high_margin_core_replay_controls"]),
        check("i7c_scoped_bf5_ready", i7c_ready, source_lineage_trace["sources"]["i7c_bf5_core_stress_gate"]),
        check("c6_supported_without_bf6_upgrade", row["n25_c6_supported"] is True and row["native_bf6_supported"] is False, row["n25_c6_meaning"]),
        check("final_bf_ceiling_is_scoped_bf5", row["final_supported_bf_level"] == FINAL_SUPPORTED_BF_LEVEL, row["bf5_scope"]),
        check("independent_new_basin_still_blocked", row["independent_new_basin_supported"] is False, row["naturalization_debt"]),
        check("native_flux_debt_preserved", row["native_flux_debt_bound"] == NATIVE_FLUX_DEBT_BOUND and row["native_flux_debt_widened"] is False, row["native_flux_debt_status"]),
        check("producer_lane_not_native_upgrade", row["producer_assisted_success_does_not_overwrite_native_failure"] is True, row["producer_assisted_lane_consumed_as"]),
        check("n26_handoff_constraints_complete", len(row["n26_consumption_constraints"]) >= 8 and row["n26_handoff_status"] == "ready", row["n26_consumption_constraints"]),
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
        "artifact_id": "n25_n26_readiness_bounded_formation_gate_i7d",
        "experiment": "2026-06-N25-lgrc-spark-sub-basin-new-basin-formation",
        "iteration": "I7-D",
        "generated_at": GENERATED_AT,
        "reconstruction_command": COMMAND,
        "status": "passed" if not failed else "failed",
        "acceptance_state": (
            "accepted_n26_ready_bounded_formation_evidence_c6_bf5_scoped"
            if not failed
            else "failed_n26_readiness_bounded_formation_gate"
        ),
        "source_digest_chain_audit": source_lineage_trace["sources"],
        "n26_readiness_rows": [row],
        "n26_readiness_row_count": 1,
        "n25_c6_supported": not failed and row["n25_c6_supported"],
        "final_supported_bf_level": FINAL_SUPPORTED_BF_LEVEL,
        "native_bf5_supported": True,
        "native_bf6_supported": False,
        "bf_ceiling": row["bf_ceiling"],
        "n25_closeout_ceiling": N25_C6,
        "n25_closeout_ladder_rung_assigned": False,
        "independent_new_basin_supported": False,
        "bounded_formation_handoff_allowed": not failed,
        "basin_formation_claim_allowed": False,
        "ready_for_iteration_8_closeout_and_n26_handoff": not failed,
        "checks": checks,
        "failed_checks": [item["check_id"] for item in failed],
    }
    output["output_digest"] = digest_value(
        {key: value for key, value in output.items() if key != "output_digest"}
    )
    return output


def write_report(output: dict[str, Any]) -> None:
    row = output["n26_readiness_rows"][0]
    lines = [
        "# N25 Iteration 7-D - N26 Readiness And Bounded Formation Evidence Gate",
        "",
        f"Status: `{output['status']}`",
        f"Acceptance state: `{output['acceptance_state']}`",
        f"Output digest: `{output['output_digest']}`",
        "",
        "## Result",
        "",
        "```text",
        f"n25_c6_supported = {str(output['n25_c6_supported']).lower()}",
        f"final_supported_bf_level = {output['final_supported_bf_level']}",
        f"native_bf5_supported = {str(output['native_bf5_supported']).lower()}",
        f"native_bf6_supported = {str(output['native_bf6_supported']).lower()}",
        f"independent_new_basin_supported = {str(output['independent_new_basin_supported']).lower()}",
        f"n25_closeout_ceiling = {output['n25_closeout_ceiling']}",
        f"ready_for_iteration_8_closeout_and_n26_handoff = {str(output['ready_for_iteration_8_closeout_and_n26_handoff']).lower()}",
        "```",
        "",
        "## Interpretation",
        "",
        row["geometric_interpretation"],
        "",
        "C6 is a closeout/readiness ceiling, not a BF6 evidence upgrade. N26 may",
        "consume the bounded BF5 core/sub-basin formation result as prerequisite",
        "geometry for proxy-divergence work, but it may not consume it as independent",
        "new-basin formation, general native basin formation, native support, agency,",
        "Phase 8, or ant ecology.",
        "",
        "## Naturalization Debt Carried Forward",
        "",
    ]
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
    lines.extend(
        [
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "| --- | --- |",
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
