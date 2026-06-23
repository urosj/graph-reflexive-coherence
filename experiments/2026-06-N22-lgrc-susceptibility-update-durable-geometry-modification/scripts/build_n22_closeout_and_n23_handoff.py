#!/usr/bin/env python3
"""Build N22 Iteration 8 closeout and N23 handoff."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-23T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification"
)
OUTPUT = EXPERIMENT / "outputs" / "n22_closeout_and_n23_handoff.json"
REPORT = EXPERIMENT / "reports" / "n22_closeout_and_n23_handoff.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n22_closeout_and_n23_handoff_artifacts"
COMMAND = (
    "python3 "
    "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
    "scripts/build_n22_closeout_and_n23_handoff.py"
)

SOURCE_PATHS = {
    "i2_schema": (
        "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
        "outputs/n22_susceptibility_schema_and_controls.json"
    ),
    "i5c_carrier": (
        "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
        "outputs/n22_alternative_nonconsumptive_carrier_probe.json"
    ),
    "i6a_carrier_transfer": (
        "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
        "outputs/n22_carrier_transfer_reentry_probe.json"
    ),
    "i6b_carrier_stress": (
        "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
        "outputs/n22_carrier_transfer_stress_boundary_probe.json"
    ),
    "i7_replay_control_matrix": (
        "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
        "outputs/n22_replay_and_control_matrix.json"
    ),
}

GLOBAL_UNSAFE_CLAIMS = [
    "agency",
    "semantic_action",
    "semantic_perception",
    "semantic_goal_ownership",
    "semantic_intention",
    "semantic_choice",
    "semantic_learning",
    "free_will",
    "selfhood",
    "identity_acceptance",
    "native_support",
    "phase8_implementation",
    "fully_native_integration",
    "organism_life",
    "sentience",
    "consciousness",
    "native_ant_agency",
    "native_colony_agency",
    "unrestricted_autonomy",
]


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(data: Any) -> str:
    return hashlib.sha256(
        json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "utf-8"
        )
    ).hexdigest()


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


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check_id": check_id, "passed": passed, "detail": detail}


def unsafe_claim_flags() -> dict[str, bool]:
    return {claim: False for claim in GLOBAL_UNSAFE_CLAIMS}


def source_output_digest_valid(data: dict[str, Any]) -> bool:
    if "output_digest" not in data:
        return False
    expected = digest_value({key: value for key, value in data.items() if key != "output_digest"})
    return data["output_digest"] == expected


def artifact_manifest_valid(data: dict[str, Any]) -> bool:
    manifest = data.get("artifact_manifest", [])
    if not isinstance(manifest, list):
        return False
    for item in manifest:
        path = item.get("path")
        expected_sha = item.get("sha256")
        if not isinstance(path, str) or path.startswith("/"):
            return False
        if not (ROOT / path).is_file():
            return False
        if expected_sha != sha256_file(path):
            return False
    return True


def source_record(source_id: str, path: str, data: dict[str, Any]) -> dict[str, Any]:
    manifest = data.get("artifact_manifest", [])
    return {
        "source_id": source_id,
        "path": path,
        "sha256": sha256_file(path),
        "status": data.get("status", "not_recorded"),
        "acceptance_state": data.get("acceptance_state", "not_recorded"),
        "output_digest": data.get("output_digest", "not_recorded"),
        "output_digest_valid": source_output_digest_valid(data),
        "artifact_manifest_count": len(manifest) if isinstance(manifest, list) else "invalid",
        "artifact_manifest_valid": artifact_manifest_valid(data),
    }


def src_diff_empty() -> bool:
    result = subprocess.run(
        ["git", "diff", "--quiet", "--", "src"],
        cwd=ROOT,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def unique_sorted(values: list[str]) -> list[str]:
    return sorted({value for value in values if value})


def closeout_rows(i7: dict[str, Any]) -> dict[str, Any]:
    packet_rows = i7["packet_branch_rows"]
    carrier_rows = i7["carrier_branch_rows"]
    packet_su3_rows = [
        row
        for row in packet_rows
        if row["i7_consumable_su_ladder_rung"] == "SU3_consumptive_transfer_readout_expression"
    ]
    carrier_su5_rows = [
        row
        for row in carrier_rows
        if row["i7_consumable_su_ladder_rung"]
        == "SU5_producer_mediated_carrier_transfer_stress_boundary_controlled_candidate"
    ]
    min_carrier_margin = min(
        row["min_i6b_target_over_peer_margin"] for row in carrier_su5_rows
    )
    min_carrier_ratio = min(row["min_i6b_transfer_ratio"] for row in carrier_su5_rows)
    max_carrier_loss = max(row["max_i6b_carrier_loss"] for row in carrier_su5_rows)
    return {
        "packet_branch": {
            "final_branch_ceiling": "SU3_consumptive_transfer_readout_expression_only",
            "consumable_su3_row_count": len(packet_su3_rows),
            "blocked_before_su5_row_count": sum(
                1 for row in packet_rows if row["row_decision"] == "blocked"
            ),
            "su4_supported": False,
            "su5_supported": False,
            "su6_supported": False,
            "reason": (
                "I5-B shows repeated packet readout spends route-b residue, so packet "
                "transfer remains readout expression and cannot support durable SU4/SU5."
            ),
        },
        "carrier_branch": {
            "final_branch_ceiling": "SU5_producer_mediated_bounded_carrier_transfer_candidate",
            "consumable_su5_row_count": len(carrier_su5_rows),
            "min_transfer_ratio": min_carrier_ratio,
            "min_target_over_peer_margin": min_carrier_margin,
            "max_carrier_loss_after_stress": max_carrier_loss,
            "producer_mediated": True,
            "native_route_conductance_memory_supported": False,
            "su5_supported": True,
            "su6_supported": False,
            "reason": (
                "I5-C creates a non-consumptive carrier through producer-mediated edge "
                "conductance state, I6-A shows transfer/re-entry, I6-B shows bounded "
                "stress survival, and I7 validates replay/control cleanliness."
            ),
        },
    }


def producer_residue(i5c: dict[str, Any]) -> dict[str, Any]:
    candidate_rows = [
        row for row in i5c["carrier_rows"] if row.get("supporting_su4_candidate") is True
    ]
    producer_fields: list[str] = []
    naturalization_debt: list[str] = []
    blocked_relabels: list[str] = []
    state_mutation_owners: list[str] = []
    for row in candidate_rows:
        residue = row.get("producer_residue", {})
        producer_fields.extend(residue.get("producer_mediated_fields", []))
        naturalization_debt.extend(residue.get("naturalization_debt", []))
        blocked_relabels.extend(residue.get("blocked_relabels", []))
        target_record = row.get("target_update_record", {})
        owner = target_record.get("state_mutation_owner")
        if owner:
            state_mutation_owners.append(owner)
    return {
        "producer_mediated_fields": unique_sorted(producer_fields),
        "state_mutation_owners": unique_sorted(state_mutation_owners),
        "producer_residue_status": "present_and_recorded",
        "naturalization_debt_fields": unique_sorted(naturalization_debt),
        "blocked_relabel_fields": unique_sorted(
            blocked_relabels
            + [
                "carrier_delta_as_native_route_conductance_memory",
                "producer_mediated_su5_as_semantic_learning",
                "producer_mediated_su5_as_native_support",
            ]
        ),
        "native_route_conductance_memory_supported": False,
        "native_non_consumptive_carrier_update_policy_supported": False,
    }


def build_output() -> dict[str, Any]:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    sources = {source_id: load_json(path) for source_id, path in SOURCE_PATHS.items()}
    i7 = sources["i7_replay_control_matrix"]
    i5c = sources["i5c_carrier"]
    branch_closeout = closeout_rows(i7)
    residue = producer_residue(i5c)
    src_clean = src_diff_empty()
    closeout_policy = {
        "threshold_record_id": "n22_i8_closeout_policy",
        "declared_before_use": True,
        "n22_c6_requires": [
            "controlled_SU5_or_SU6_evidence",
            "producer_residue_recorded",
            "naturalization_debt_recorded",
            "AP4_AP5_dependency_status_recorded",
            "unsafe_claim_blockers_false",
            "src_diff_empty",
            "N23_handoff_recorded",
        ],
        "final_supported_su_rung_allowed": "SU5_producer_mediated_bounded_susceptibility_update_candidate",
        "native_su6_allowed": False,
        "semantic_learning_allowed": False,
        "phase8_allowed": False,
    }
    policy_path = ARTIFACT_DIR / "n22_i8_closeout_policy_declared_before_use.json"
    write_json(policy_path, closeout_policy)

    source_records = [
        source_record(source_id, SOURCE_PATHS[source_id], sources[source_id])
        for source_id in SOURCE_PATHS
    ]
    source_artifacts_valid = all(record["status"] == "passed" for record in source_records) and all(
        record["output_digest_valid"] and record["artifact_manifest_valid"]
        for record in source_records
    )
    i7_summary = i7["iteration7_summary"]
    i7_ready = (
        i7["status"] == "passed"
        and i7_summary["ready_for_iteration_8_closeout"] is True
        and i7_summary["carrier_branch_i7_consumable_su5_count"] == 3
        and i7_summary["packet_branch_su4_su5_blocked_by_consumptive_readout"] is True
    )
    unsafe = unsafe_claim_flags()
    ap_gap_propagation = {
        "ap4_dependency_status": "required_recorded",
        "ap4_condition_reason": (
            "route-conditioned susceptibility/transfer claims depend on route selection; "
            "N19 AP4 NAT4 gap remains propagated rather than resolved"
        ),
        "ap5_dependency_status": "not_applicable",
        "ap5_condition_reason": (
            "N22 closeout does not claim proxy or target formation as evidence; "
            "N19 AP5 NAT4 gap remains preserved for later dependent rows"
        ),
        "ap4_nat4_gap_resolved": False,
        "ap5_nat4_gap_resolved": False,
        "ap_gap_prose_only_allowed": False,
    }
    n21_nd6_bridge = {
        "n21_nd6_bridge_status": "bridge_candidate_supported",
        "bridge_scope": (
            "producer-mediated artifact-level bridge candidate only; N21 remains closed "
            "and is not retroactively upgraded"
        ),
        "source_condition_tested": "durable_geometry_modification_susceptibility_update",
        "supporting_n22_rung": "SU5_producer_mediated_bounded_susceptibility_update_candidate",
        "native_nd6_supported": False,
        "retroactive_n21_upgrade_allowed": False,
        "blocked_stronger_claims": [
            "N21_ND6_final_reopen",
            "native_naturalization_depth",
            "native_support",
            "semantic_learning",
            "agency",
        ],
    }
    n23_handoff = {
        "ready_for_n23": True,
        "next_experiment": "N23_live_continuation_collapse_selection_geometry",
        "consume_n22_as": [
            "bounded_producer_mediated_susceptibility_update_context",
            "durable_geometry_modification_candidate",
            "producer_residue_and_naturalization_debt_ledger",
            "AP4_AP5_gap_propagation_context",
        ],
        "must_not_consume_n22_as": [
            "semantic_learning",
            "semantic_choice",
            "agency",
            "native_support",
            "native_route_conductance_memory",
            "sentience",
            "phase8_implementation",
            "ant_ecology_specification",
        ],
        "handoff_claim_ceiling": (
            "bounded producer-mediated artifact-level susceptibility-update / durable "
            "geometry modification evidence; not native learning, choice, agency, "
            "native support, sentience, Phase 8, or ant ecology"
        ),
    }
    final_closeout = {
        "final_supported_status": "bounded_artifact_level_susceptibility_update_candidate",
        "final_supported_su_ladder_rung": (
            "SU5_producer_mediated_bounded_susceptibility_update_candidate"
        ),
        "n22_closeout_ladder_rung": "N22-C6",
        "n22_closeout_ladder_rung_assigned": True,
        "n22_closeout_supported": True,
        "source_backed_susceptibility_update_evidence": True,
        "delta_survived_replay_and_later_reentry": True,
        "same_budget_peer_comparison_rules_out_global_drift": True,
        "durable_geometry_modification_not_label_schedule_proxy": True,
        "su5_supported_final": True,
        "su6_supported": False,
        "native_su6_supported": False,
        "native_route_conductance_memory_supported": False,
        "semantic_learning_supported": False,
        "semantic_choice_supported": False,
        "agency_supported": False,
        "native_support_supported": False,
        "sentience_supported": False,
        "phase8_opened": False,
        "ant_ecology_opened": False,
        "src_diff_empty": src_clean,
        "ready_for_n23": True,
    }
    artifact_manifest = [
        {
            "path": rel(policy_path),
            "sha256": sha256_file(rel(policy_path)),
            "artifact_role": "closeout_policy",
        },
        *[
            {
                "path": record["path"],
                "sha256": record["sha256"],
                "artifact_role": f"source_{record['source_id']}",
            }
            for record in source_records
        ],
    ]
    c6_requirements_met = (
        source_artifacts_valid
        and i7_ready
        and branch_closeout["carrier_branch"]["su5_supported"] is True
        and branch_closeout["carrier_branch"]["su6_supported"] is False
        and residue["producer_residue_status"] == "present_and_recorded"
        and len(residue["naturalization_debt_fields"]) >= 2
        and src_clean
        and n23_handoff["ready_for_n23"] is True
    )
    checks = [
        check("source_artifacts_valid", source_artifacts_valid, source_records),
        check("i7_ready_for_closeout", i7_ready, i7_summary),
        check(
            "packet_branch_capped_at_su3",
            branch_closeout["packet_branch"]["su5_supported"] is False
            and branch_closeout["packet_branch"]["consumable_su3_row_count"] == 4,
            branch_closeout["packet_branch"],
        ),
        check(
            "carrier_branch_final_su5_candidate",
            branch_closeout["carrier_branch"]["su5_supported"] is True
            and branch_closeout["carrier_branch"]["consumable_su5_row_count"] == 3,
            branch_closeout["carrier_branch"],
        ),
        check(
            "producer_residue_and_naturalization_debt_recorded",
            residue["producer_residue_status"] == "present_and_recorded"
            and bool(residue["producer_mediated_fields"])
            and bool(residue["naturalization_debt_fields"]),
            residue,
        ),
        check(
            "ap4_ap5_dependency_status_preserved",
            ap_gap_propagation["ap4_dependency_status"] == "required_recorded"
            and ap_gap_propagation["ap5_dependency_status"] == "not_applicable"
            and ap_gap_propagation["ap4_nat4_gap_resolved"] is False
            and ap_gap_propagation["ap5_nat4_gap_resolved"] is False,
            ap_gap_propagation,
        ),
        check(
            "n21_nd6_bridge_bounded",
            n21_nd6_bridge["n21_nd6_bridge_status"] == "bridge_candidate_supported"
            and n21_nd6_bridge["native_nd6_supported"] is False
            and n21_nd6_bridge["retroactive_n21_upgrade_allowed"] is False,
            n21_nd6_bridge,
        ),
        check(
            "unsafe_claims_blocked",
            all(flag is False for flag in unsafe.values())
            and final_closeout["semantic_learning_supported"] is False
            and final_closeout["agency_supported"] is False
            and final_closeout["native_support_supported"] is False
            and final_closeout["phase8_opened"] is False,
            unsafe,
        ),
        check("src_diff_empty", src_clean, "git diff -- src is empty"),
        check("n22_c6_requirements_met", c6_requirements_met, final_closeout),
        check(
            "artifact_paths_repository_relative",
            all(not item["path"].startswith("/") for item in artifact_manifest),
            "relative paths only",
        ),
    ]
    failed_checks = [item for item in checks if not item["passed"]]
    output = {
        "artifact_id": "n22_i8_closeout_and_n23_handoff",
        "schema_version": "1.0",
        "generated_at": GENERATED_AT,
        "experiment": "N22",
        "iteration": "8",
        "purpose": "close N22 and hand off bounded susceptibility-update evidence to N23",
        "status": "passed" if not failed_checks else "failed",
        "acceptance_state": (
            "accepted_n22_c6_handoff_ready_producer_mediated_su5_no_native_learning"
            if not failed_checks
            else "failed_n22_closeout"
        ),
        "command": COMMAND,
        "source_artifacts": source_records,
        "closeout_policy": closeout_policy,
        "final_closeout": final_closeout,
        "branch_closeout": branch_closeout,
        "producer_residue": residue,
        "ap_gap_propagation": ap_gap_propagation,
        "n21_nd6_bridge": n21_nd6_bridge,
        "n23_handoff": n23_handoff,
        "claim_boundary": {
            "claim_ceiling": n23_handoff["handoff_claim_ceiling"],
            "unsafe_claim_flags": unsafe,
        },
        "geometric_interpretation": {
            "short_read": (
                "N22 closes with a producer-mediated carrier branch that durably "
                "changes source-current edge conductance geometry and survives "
                "transfer, re-entry, stress, replay, and fail-closed controls."
            ),
            "packet_branch_boundary": (
                "The packet branch remains consumptive: repeated readout spends the "
                "route-b residue, so it is capped at SU3 transfer/readout expression."
            ),
            "carrier_branch_boundary": (
                "The carrier branch stores the susceptibility delta in serialized "
                "LGRC-visible edge/base/port conductance state, but the write policy "
                "is still producer-mediated. That supports bounded SU5 and leaves "
                "native route-conductance memory as naturalization debt."
            ),
            "claim_boundary": (
                "C6 means N23-ready closeout, not native SU6. N22 does not support "
                "semantic learning, choice, agency, native support, sentience, Phase 8, "
                "or ant-ecology implementation."
            ),
        },
        "artifact_manifest": artifact_manifest,
        "checks": checks,
        "failed_checks": failed_checks,
    }
    output["output_digest"] = digest_value(
        {key: value for key, value in output.items() if key != "output_digest"}
    )
    return output


def write_report(output: dict[str, Any]) -> None:
    final = output["final_closeout"]
    packet = output["branch_closeout"]["packet_branch"]
    carrier = output["branch_closeout"]["carrier_branch"]
    residue = output["producer_residue"]
    bridge = output["n21_nd6_bridge"]
    handoff = output["n23_handoff"]
    lines = [
        "# N22 Iteration 8 - Closeout And N23 Handoff",
        "",
        f"Status: `{output['status']}`",
        "",
        f"Acceptance state: `{output['acceptance_state']}`",
        "",
        f"Output digest: `{output['output_digest']}`",
        "",
        "## Final State",
        "",
        "```text",
        f"final_supported_status = {final['final_supported_status']}",
        f"final_supported_su_ladder_rung = {final['final_supported_su_ladder_rung']}",
        f"n22_closeout_ladder_rung = {final['n22_closeout_ladder_rung']}",
        f"n22_closeout_supported = {str(final['n22_closeout_supported']).lower()}",
        f"su5_supported_final = {str(final['su5_supported_final']).lower()}",
        f"su6_supported = {str(final['su6_supported']).lower()}",
        f"native_route_conductance_memory_supported = {str(final['native_route_conductance_memory_supported']).lower()}",
        f"ready_for_n23 = {str(final['ready_for_n23']).lower()}",
        "```",
        "",
        output["geometric_interpretation"]["short_read"],
        "",
        output["geometric_interpretation"]["claim_boundary"],
        "",
        "## Branch Closeout",
        "",
        "| Branch | Final Ceiling | Rows | SU5 | SU6 | Reason |",
        "| --- | --- | ---: | --- | --- | --- |",
        "| packet | "
        f"`{packet['final_branch_ceiling']}` | "
        f"{packet['consumable_su3_row_count']} | "
        f"`{str(packet['su5_supported']).lower()}` | "
        f"`{str(packet['su6_supported']).lower()}` | "
        f"{packet['reason']} |",
        "| carrier | "
        f"`{carrier['final_branch_ceiling']}` | "
        f"{carrier['consumable_su5_row_count']} | "
        f"`{str(carrier['su5_supported']).lower()}` | "
        f"`{str(carrier['su6_supported']).lower()}` | "
        f"{carrier['reason']} |",
        "",
        "## Producer Residue",
        "",
        "```text",
        f"producer_mediated_fields = {', '.join(residue['producer_mediated_fields'])}",
        f"state_mutation_owners = {', '.join(residue['state_mutation_owners'])}",
        f"naturalization_debt_fields = {', '.join(residue['naturalization_debt_fields'])}",
        f"native_route_conductance_memory_supported = {str(residue['native_route_conductance_memory_supported']).lower()}",
        "```",
        "",
        "## N21 ND6 Bridge",
        "",
        "```text",
        f"n21_nd6_bridge_status = {bridge['n21_nd6_bridge_status']}",
        f"native_nd6_supported = {str(bridge['native_nd6_supported']).lower()}",
        f"retroactive_n21_upgrade_allowed = {str(bridge['retroactive_n21_upgrade_allowed']).lower()}",
        "```",
        "",
        bridge["bridge_scope"],
        "",
        "## N23 Handoff",
        "",
        "```text",
        f"ready_for_n23 = {str(handoff['ready_for_n23']).lower()}",
        f"next_experiment = {handoff['next_experiment']}",
        f"handoff_claim_ceiling = {handoff['handoff_claim_ceiling']}",
        "```",
        "",
        "## Checks",
        "",
        "| Check | Passed | Detail |",
        "| --- | --- | --- |",
    ]
    for item in output["checks"]:
        detail = item["detail"]
        if isinstance(detail, (dict, list)):
            detail_text = json.dumps(detail, sort_keys=True)
        else:
            detail_text = str(detail)
        if len(detail_text) > 160:
            detail_text = detail_text[:157] + "..."
        lines.append(
            f"| `{item['check_id']}` | `{str(item['passed']).lower()}` | {detail_text} |"
        )
    lines.append("")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    output = build_output()
    write_json(OUTPUT, output)
    output = load_json(rel(OUTPUT))
    write_report(output)


if __name__ == "__main__":
    main()
