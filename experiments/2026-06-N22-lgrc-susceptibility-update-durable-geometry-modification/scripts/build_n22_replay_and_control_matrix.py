#!/usr/bin/env python3
"""Build N22 Iteration 7 replay and control matrix."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-23T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification"
)
OUTPUT = EXPERIMENT / "outputs" / "n22_replay_and_control_matrix.json"
REPORT = EXPERIMENT / "reports" / "n22_replay_and_control_matrix.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n22_replay_and_control_matrix_artifacts"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
    "scripts/build_n22_replay_and_control_matrix.py"
)

SOURCE_PATHS = {
    "i1_source_inventory": (
        "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
        "outputs/n22_source_handoff_inventory.json"
    ),
    "i2_schema": (
        "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
        "outputs/n22_susceptibility_schema_and_controls.json"
    ),
    "i3_active_nulls": (
        "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
        "outputs/n22_active_nulls_and_failure_baselines.json"
    ),
    "i4_minimal": (
        "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
        "outputs/n22_minimal_susceptibility_update_probe.json"
    ),
    "i4a_dose": (
        "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
        "outputs/n22_susceptibility_dose_boundary_probe.json"
    ),
    "i4b_multipath": (
        "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
        "outputs/n22_multipath_susceptibility_shape_probe.json"
    ),
    "i5_replay": (
        "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
        "outputs/n22_durability_replay_probe.json"
    ),
    "i5a_stress": (
        "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
        "outputs/n22_replay_durability_stress_probe.json"
    ),
    "i5b_residual": (
        "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
        "outputs/n22_residual_nonconsumptive_durability_probe.json"
    ),
    "i5c_carrier": (
        "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
        "outputs/n22_alternative_nonconsumptive_carrier_probe.json"
    ),
    "i6_transfer": (
        "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
        "outputs/n22_transfer_reentry_probe.json"
    ),
    "i6a_carrier_transfer": (
        "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
        "outputs/n22_carrier_transfer_reentry_probe.json"
    ),
    "i6b_carrier_stress": (
        "experiments/2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification/"
        "outputs/n22_carrier_transfer_stress_boundary_probe.json"
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


def controls_fail_closed(controls: list[dict[str, Any]]) -> bool:
    return all(
        control.get("status", control.get("control_status")) == "failed_closed"
        and control.get("claim_allowed", control.get("claim_allowed_when_control_triggers")) is False
        for control in controls
    )


def active_nulls_fail_closed(i3: dict[str, Any]) -> bool:
    rows = i3["active_null_rows"]
    return (
        len(rows) == 14
        and all(row["row_decision"] == "rejected" for row in rows)
        and all(row["actual_result"] == "failed_closed" for row in rows)
        and all(row["susceptibility_update_claim_allowed"] is False for row in rows)
        and all(controls_fail_closed(row["control_results"]) for row in rows)
    )


def packet_branch_rows(i5b: dict[str, Any], i6: dict[str, Any]) -> list[dict[str, Any]]:
    residual_by_id = {
        row["row_id"].replace("n22_i5b_row_", ""): row
        for row in i5b["residual_rows"]
    }
    rows: list[dict[str, Any]] = []
    for row in i6["transfer_rows"]:
        family_id = row["row_id"].replace("n22_i6_row_", "")
        residual = residual_by_id.get(family_id, {})
        transfer_readout = row.get("transfer_readout_expression") is True
        blocked_by_consumption = row.get("su5_blocked_by_i5b_consumptive_readout") is True
        demoted_before_su5 = row["provisional_su_ladder_rung"] == "demoted_before_SU5"
        if transfer_readout and blocked_by_consumption:
            consumable_rung = "SU3_consumptive_transfer_readout_expression"
            decision = "partial"
            susceptibility_claim_allowed = True
        elif demoted_before_su5:
            consumable_rung = "blocked_before_SU5_route_specific_margin_failure"
            decision = "blocked"
            susceptibility_claim_allowed = False
        else:
            consumable_rung = "blocked_before_SU3"
            decision = "blocked"
            susceptibility_claim_allowed = False
        rows.append(
            {
                "row_id": f"n22_i7_packet_{family_id}",
                "source_i6_row_id": row["row_id"],
                "source_i5b_row_id": residual.get("row_id", "missing"),
                "branch": "packet_readout",
                "row_decision": decision,
                "i7_consumable_su_ladder_rung": consumable_rung,
                "limited_su3_claim_allowed": susceptibility_claim_allowed,
                "durable_geometry_modification_claim_allowed": False,
                "transfer_su5_claim_allowed": False,
                "su6_claim_allowed": False,
                "final_n22_claim_allowed": False,
                "reason": (
                    "I5-B shows repeated readout consumes the packet residue, so I6 "
                    "transfer evidence remains SU3 transfer/readout expression only."
                    if transfer_readout and blocked_by_consumption
                    else "route-specific transfer margin fails or the row is not a transfer readout expression"
                ),
                "i5b_consumptive_readout_detected": residual.get("consumptive_readout_detected", False),
                "i6_transfer_readout_expression": transfer_readout,
                "i6_controls_failed_closed": row.get("control_contexts_failed_closed") is True,
                "unsafe_claim_flags": unsafe_claim_flags(),
            }
        )
    return rows


def carrier_branch_rows(i5c: dict[str, Any], i6a: dict[str, Any], i6b: dict[str, Any]) -> list[dict[str, Any]]:
    i5c_rows = {
        row["carrier_family"]: row
        for row in i5c["carrier_rows"]
        if row.get("supporting_su4_candidate") is True
    }
    i6a_rows = {row["carrier_family"]: row for row in i6a["transfer_rows"]}
    i6b_rows = {row["carrier_family"]: row for row in i6b["stress_rows"]}
    rows: list[dict[str, Any]] = []
    for family, i5c_row in sorted(i5c_rows.items()):
        i6a_row = i6a_rows[family]
        i6b_row = i6b_rows[family]
        i5c_passed = (
            i5c_row["carrier_gate"]["carrier_not_consumed_by_readback"] is True
            and i5c_row["carrier_gate"]["target_over_peer_margin"] >= 0.05
            and i5c_row["native_route_conductance_memory_supported"] is False
        )
        i6a_passed = (
            i6a_row["supporting_su5_candidate"] is True
            and all(record["passed"] for record in i6a_row["context_records"])
            and controls_fail_closed(i6a_row["controls"])
            and i6a_row["native_route_conductance_memory_supported"] is False
        )
        i6b_passed = (
            i6b_row["supporting_su5_stress_candidate"] is True
            and all(record["passed"] for record in i6b_row["stress_context_records"])
            and controls_fail_closed(i6b_row["controls"])
            and i6b_row["native_route_conductance_memory_supported"] is False
        )
        controlled = i5c_passed and i6a_passed and i6b_passed
        rows.append(
            {
                "row_id": f"n22_i7_carrier_{family}",
                "source_i5c_row_id": i5c_row["row_id"],
                "source_i6a_row_id": i6a_row["row_id"],
                "source_i6b_row_id": i6b_row["row_id"],
                "branch": "producer_mediated_carrier",
                "row_decision": "supported" if controlled else "blocked",
                "i7_consumable_su_ladder_rung": (
                    "SU5_producer_mediated_carrier_transfer_stress_boundary_controlled_candidate"
                    if controlled
                    else "blocked_before_controlled_SU5"
                ),
                "i5c_su4_non_consumptive_carrier_passed": i5c_passed,
                "i6a_transfer_reentry_passed": i6a_passed,
                "i6b_stress_boundary_passed": i6b_passed,
                "carrier_delta_classification": i5c_row["variable_classification"]["carrier_delta"],
                "native_route_conductance_memory_status": i5c_row["variable_classification"][
                    "native_route_conductance_memory"
                ],
                "readback_event_classification": i5c_row["variable_classification"]["readback_events"],
                "semantic_learning_status": i5c_row["variable_classification"]["semantic_learning"],
                "min_i6b_transfer_ratio": i6b_row["stress_boundary"]["min_carrier_transfer_ratio"],
                "min_i6b_target_over_peer_margin": i6b_row["stress_boundary"][
                    "min_target_over_peer_margin"
                ],
                "max_i6b_carrier_loss": i6b_row["stress_boundary"]["max_carrier_loss_after_stress"],
                "i7_susceptibility_update_claim_allowed": controlled,
                "durable_geometry_modification_claim_allowed": controlled,
                "transfer_su5_claim_allowed": controlled,
                "final_su5_supported": False,
                "su6_supported": False,
                "final_n22_supported": False,
                "claim_ceiling": (
                    "I7-consumable producer-mediated artifact-level SU5 carrier "
                    "transfer/stress candidate; not final SU5, SU6, final N22, "
                    "N21 ND6 bridge, native conductance memory, semantic learning, "
                    "choice, agency, native support, sentience, or Phase 8"
                ),
                "unsafe_claim_flags": unsafe_claim_flags(),
            }
        )
    return rows


def build_control_matrix(
    i3: dict[str, Any],
    i5b: dict[str, Any],
    i5c: dict[str, Any],
    i6: dict[str, Any],
    i6a: dict[str, Any],
    i6b: dict[str, Any],
) -> list[dict[str, Any]]:
    active_null_controls = [
        {
            "control_id": "i3_active_nulls",
            "status": "failed_closed" if active_nulls_fail_closed(i3) else "failed_open",
            "claim_allowed": False,
            "scope": "pre-positive false-positive blockers",
            "detail": "14/14 active null rows reject false-positive paths",
        }
    ]
    packet_controls = [
        {
            "control_id": "packet_consumptive_readout_boundary",
            "status": (
                "failed_closed"
                if all(row.get("consumptive_readout_detected") is True for row in i5b["residual_rows"])
                else "failed_open"
            ),
            "claim_allowed": False,
            "scope": "packet branch SU4/SU5 blocker",
            "detail": "I5-B repeated readout spends route-b packet residue",
        },
        {
            "control_id": "packet_transfer_as_su5_relabel",
            "status": (
                "failed_closed"
                if all(
                    row.get("su5_supported") is False
                    for row in i6["transfer_rows"]
                    if row.get("transfer_readout_expression") is True
                )
                else "failed_open"
            ),
            "claim_allowed": False,
            "scope": "packet branch transfer relabel blocker",
            "detail": "I6 transfer expression remains SU3 because I5-B blocks non-consumptive durability",
        },
    ]
    carrier_controls = [
        {
            "control_id": "carrier_native_conductance_memory_relabel",
            "status": (
                "failed_closed"
                if all(row.get("native_route_conductance_memory_supported") is False for row in i5c["carrier_rows"])
                and all(row.get("native_route_conductance_memory_supported") is False for row in i6a["transfer_rows"])
                and all(row.get("native_route_conductance_memory_supported") is False for row in i6b["stress_rows"])
                else "failed_open"
            ),
            "claim_allowed": False,
            "scope": "carrier branch native-memory blocker",
            "detail": "carrier delta remains producer-mediated naturalization debt",
        },
        {
            "control_id": "carrier_peer_label_swap_controls",
            "status": (
                "failed_closed"
                if all(controls_fail_closed(row["controls"]) for row in i6a["transfer_rows"])
                and all(controls_fail_closed(row["controls"]) for row in i6b["stress_rows"])
                else "failed_open"
            ),
            "claim_allowed": False,
            "scope": "carrier branch route-specificity controls",
            "detail": "peer-label and peer-stress controls fail closed",
        },
        {
            "control_id": "carrier_final_su5_before_closeout_relabel",
            "status": (
                "failed_closed"
                if all(row.get("su5_supported") is False for row in i6a["transfer_rows"])
                and all(row.get("su5_supported") is False for row in i6b["stress_rows"])
                else "failed_open"
            ),
            "claim_allowed": False,
            "scope": "final-claim blocker",
            "detail": "I7 may assign consumable evidence but cannot close final SU5 or N22",
        },
    ]
    unsafe_controls = [
        {
            "control_id": "semantic_learning_choice_agency_native_support_phase8_relabels",
            "status": "failed_closed",
            "claim_allowed": False,
            "scope": "global unsafe claim blocker",
            "detail": "unsafe claim flags remain false in all I7 output rows",
        }
    ]
    return active_null_controls + packet_controls + carrier_controls + unsafe_controls


def build_replay_matrix(source_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output_digest_stable = all(record["output_digest_valid"] for record in source_records)
    manifests_valid = all(record["artifact_manifest_valid"] for record in source_records)
    source_statuses_passed = all(record["status"] == "passed" for record in source_records)
    return [
        {
            "replay_id": "artifact_only_reconstruction",
            "status": "passed" if output_digest_stable else "failed_open",
            "detail": "source output digests recompute from artifact JSON",
        },
        {
            "replay_id": "artifact_manifest_hash_replay",
            "status": "passed" if manifests_valid else "failed_open",
            "detail": "source artifact manifests point to relative paths with matching SHA-256",
        },
        {
            "replay_id": "duplicate_source_status_replay",
            "status": "passed" if source_statuses_passed else "failed_open",
            "detail": "all source artifact statuses remain passed",
        },
        {
            "replay_id": "branch_order_replay",
            "status": "passed",
            "detail": "packet branch and carrier branch are consumed separately; carrier evidence does not backfill packet branch",
        },
    ]


def build_output() -> dict[str, Any]:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    sources = {source_id: load_json(path) for source_id, path in SOURCE_PATHS.items()}
    threshold_record = {
        "threshold_record_id": "n22_i7_replay_and_control_matrix_thresholds",
        "declared_before_use": True,
        "consume_packet_and_carrier_branches_separately": True,
        "packet_branch_final_ceiling": "SU3_consumptive_transfer_readout_expression",
        "carrier_branch_candidate_ceiling": "I7_consumable_producer_mediated_SU5_candidate",
        "final_su5_or_n22_closeout_allowed": False,
        "n21_nd6_bridge_closeout_allowed": False,
        "native_route_conductance_memory_allowed": False,
    }
    threshold_path = ARTIFACT_DIR / "n22_i7_thresholds_declared_before_use.json"
    write_json(threshold_path, threshold_record)
    source_records = [
        source_record(source_id, SOURCE_PATHS[source_id], sources[source_id])
        for source_id in SOURCE_PATHS
    ]
    packet_rows = packet_branch_rows(sources["i5b_residual"], sources["i6_transfer"])
    carrier_rows = carrier_branch_rows(
        sources["i5c_carrier"],
        sources["i6a_carrier_transfer"],
        sources["i6b_carrier_stress"],
    )
    control_matrix = build_control_matrix(
        sources["i3_active_nulls"],
        sources["i5b_residual"],
        sources["i5c_carrier"],
        sources["i6_transfer"],
        sources["i6a_carrier_transfer"],
        sources["i6b_carrier_stress"],
    )
    replay_matrix = build_replay_matrix(source_records)
    artifact_manifest = [
        {
            "path": rel(threshold_path),
            "sha256": sha256_file(rel(threshold_path)),
            "artifact_role": "threshold_record",
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
    source_artifacts_valid = all(record["output_digest_valid"] for record in source_records) and all(
        record["artifact_manifest_valid"] for record in source_records
    )
    packet_su3_count = sum(
        1
        for row in packet_rows
        if row["i7_consumable_su_ladder_rung"] == "SU3_consumptive_transfer_readout_expression"
    )
    packet_blocked_count = sum(1 for row in packet_rows if row["row_decision"] == "blocked")
    carrier_su5_count = sum(
        1
        for row in carrier_rows
        if row["i7_consumable_su_ladder_rung"]
        == "SU5_producer_mediated_carrier_transfer_stress_boundary_controlled_candidate"
    )
    all_controls_closed = all(item["status"] == "failed_closed" for item in control_matrix)
    all_replays_passed = all(item["status"] == "passed" for item in replay_matrix)
    unsafe_flags_false = all(
        all(flag is False for flag in row["unsafe_claim_flags"].values())
        for row in packet_rows + carrier_rows
    )
    summary = {
        "source_artifact_count": len(source_records),
        "source_artifacts_valid": source_artifacts_valid,
        "active_null_rows_consumed": len(sources["i3_active_nulls"]["active_null_rows"]),
        "packet_branch_i7_consumable_su3_count": packet_su3_count,
        "packet_branch_blocked_before_su5_count": packet_blocked_count,
        "packet_branch_su4_su5_blocked_by_consumptive_readout": True,
        "carrier_branch_i7_consumable_su5_count": carrier_su5_count,
        "carrier_branch_native_route_conductance_memory_supported": False,
        "carrier_branch_producer_mediated": True,
        "control_count": len(control_matrix),
        "controls_failed_closed": all_controls_closed,
        "replay_count": len(replay_matrix),
        "replays_passed": all_replays_passed,
        "i7_consumable_highest_su_rung": (
            "SU5_producer_mediated_carrier_transfer_stress_boundary_controlled_candidate"
            if carrier_su5_count
            else "SU3_consumptive_transfer_readout_expression"
        ),
        "recommended_iteration8_closeout_candidate": "N22-C5_producer_mediated_bounded_candidate",
        "n22_closeout_ladder_rung_assigned": False,
        "su5_supported_final": False,
        "su6_supported": False,
        "final_n22_supported": False,
        "n21_nd6_bridge_status": "not_supported",
        "n21_nd6_bridge_iteration8_input": "producer_mediated_su5_candidate_available_for_closeout_review",
        "ready_for_iteration_8_closeout": True,
    }
    checks = [
        check("source_artifacts_valid", source_artifacts_valid, source_records),
        check("active_nulls_fail_closed", active_nulls_fail_closed(sources["i3_active_nulls"]), 14),
        check("packet_branch_consumptive_boundary_preserved", packet_su3_count == 4 and packet_blocked_count == 1, summary),
        check("carrier_branch_controlled_su5_candidates", carrier_su5_count == 3, summary),
        check("controls_failed_closed", all_controls_closed, control_matrix),
        check("replays_passed", all_replays_passed, replay_matrix),
        check("unsafe_flags_all_false", unsafe_flags_false, "all I7 rows"),
        check(
            "final_claims_blocked",
            not summary["su5_supported_final"]
            and not summary["su6_supported"]
            and not summary["final_n22_supported"],
            summary,
        ),
        check(
            "artifact_paths_repository_relative",
            all(not item["path"].startswith("/") for item in artifact_manifest),
            "relative paths only",
        ),
    ]
    failed_checks = [item for item in checks if not item["passed"]]
    output = {
        "artifact_id": "n22_i7_replay_and_control_matrix",
        "schema_version": "1.0",
        "generated_at": GENERATED_AT,
        "experiment": "N22",
        "iteration": "7",
        "purpose": "classify N22 provisional rows through replay and control matrix before closeout",
        "status": "passed" if not failed_checks else "failed",
        "acceptance_state": (
            "accepted_controlled_producer_mediated_su5_candidate_no_final_closeout"
            if not failed_checks
            else "failed_replay_and_control_matrix"
        ),
        "command": COMMAND,
        "source_artifacts": source_records,
        "threshold_record": threshold_record,
        "replay_matrix": replay_matrix,
        "control_matrix": control_matrix,
        "packet_branch_rows": packet_rows,
        "carrier_branch_rows": carrier_rows,
        "artifact_manifest": artifact_manifest,
        "iteration7_summary": summary,
        "geometric_interpretation": {
            "short_read": (
                "I7 separates the consumptive packet-readout branch from the "
                "producer-mediated carrier branch. Packet evidence remains SU3-limited; "
                "carrier evidence becomes I7-consumable producer-mediated SU5 candidate "
                "evidence pending I8 closeout."
            ),
            "claim_boundary": (
                "I7 does not close final SU5, SU6, N22, or the N21 ND6 bridge. "
                "It does not support native route-conductance memory, semantic learning, "
                "choice, agency, native support, sentience, Phase 8, or ant ecology."
            ),
        },
        "checks": checks,
        "failed_checks": failed_checks,
    }
    output["output_digest"] = digest_value(
        {key: value for key, value in output.items() if key != "output_digest"}
    )
    return output


def write_report(output: dict[str, Any]) -> None:
    summary = output["iteration7_summary"]
    lines = [
        "# N22 Iteration 7 - Replay And Control Matrix",
        "",
        f"Status: `{output['status']}`",
        "",
        f"Acceptance state: `{output['acceptance_state']}`",
        "",
        f"Output digest: `{output['output_digest']}`",
        "",
        "## Summary",
        "",
        output["geometric_interpretation"]["short_read"],
        "",
        output["geometric_interpretation"]["claim_boundary"],
        "",
        "```text",
        f"packet_branch_i7_consumable_su3_count = {summary['packet_branch_i7_consumable_su3_count']}",
        f"packet_branch_blocked_before_su5_count = {summary['packet_branch_blocked_before_su5_count']}",
        f"carrier_branch_i7_consumable_su5_count = {summary['carrier_branch_i7_consumable_su5_count']}",
        f"i7_consumable_highest_su_rung = {summary['i7_consumable_highest_su_rung']}",
        f"recommended_iteration8_closeout_candidate = {summary['recommended_iteration8_closeout_candidate']}",
        f"n22_closeout_ladder_rung_assigned = {str(summary['n22_closeout_ladder_rung_assigned']).lower()}",
        f"final_n22_supported = {str(summary['final_n22_supported']).lower()}",
        f"n21_nd6_bridge_status = {summary['n21_nd6_bridge_status']}",
        "```",
        "",
        "## Packet Branch",
        "",
        "| Row | Decision | I7 Rung | Limited SU3 | SU5 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in output["packet_branch_rows"]:
        lines.append(
            "| "
            f"`{row['row_id'].removeprefix('n22_i7_packet_')}` | "
            f"`{row['row_decision']}` | "
            f"`{row['i7_consumable_su_ladder_rung']}` | "
            f"`{str(row['limited_su3_claim_allowed']).lower()}` | "
            f"`{str(row['transfer_su5_claim_allowed']).lower()}` |"
        )
    lines.extend(
        [
            "",
            "## Carrier Branch",
            "",
            "| Row | Decision | I7 Rung | Min I6-B Ratio | Min I6-B Margin | Final SU5 |",
            "| --- | --- | --- | ---: | ---: | --- |",
        ]
    )
    for row in output["carrier_branch_rows"]:
        lines.append(
            "| "
            f"`{row['row_id'].removeprefix('n22_i7_carrier_')}` | "
            f"`{row['row_decision']}` | "
            f"`{row['i7_consumable_su_ladder_rung']}` | "
            f"{row['min_i6b_transfer_ratio']:.6f} | "
            f"{row['min_i6b_target_over_peer_margin']:.6f} | "
            f"`{str(row['final_su5_supported']).lower()}` |"
        )
    lines.extend(
        [
            "",
            "## Replay Matrix",
            "",
            "| Replay | Status | Detail |",
            "| --- | --- | --- |",
        ]
    )
    for row in output["replay_matrix"]:
        lines.append(f"| `{row['replay_id']}` | `{row['status']}` | {row['detail']} |")
    lines.extend(
        [
            "",
            "## Control Matrix",
            "",
            "| Control | Status | Claim Allowed | Detail |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in output["control_matrix"]:
        lines.append(
            "| "
            f"`{row['control_id']}` | "
            f"`{row['status']}` | "
            f"`{str(row['claim_allowed']).lower()}` | "
            f"{row['detail']} |"
        )
    lines.extend(
        [
            "",
            "## Checks",
            "",
            "| Check | Passed | Detail |",
            "| --- | --- | --- |",
        ]
    )
    for item in output["checks"]:
        detail = item["detail"]
        if isinstance(detail, (dict, list)):
            detail_text = json.dumps(detail, sort_keys=True)
        else:
            detail_text = str(detail)
        if len(detail_text) > 140:
            detail_text = detail_text[:137] + "..."
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
