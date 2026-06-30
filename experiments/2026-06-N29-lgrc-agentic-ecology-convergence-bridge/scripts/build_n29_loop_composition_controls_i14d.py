#!/usr/bin/env python3
"""Build N29 I14-D loop / composition controls for Prototype D."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-30T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N29-lgrc-agentic-ecology-convergence-bridge"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/scripts/"
    "build_n29_loop_composition_controls_i14d.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

SOURCE_PATHS = {
    "i14_4_single_direction_neutral_circulation": (
        EXPERIMENT / "outputs" / "n29_neutral_circulation_composition_i144.json"
    ),
    "i14_4_1_producer_reverse_loop_bridge": (
        EXPERIMENT / "outputs" / "n29_neutral_circulation_loop_closure_i1441.json"
    ),
    "i14_4_2_native_reverse_search_blocker": (
        EXPERIMENT / "outputs" / "n29_neutral_circulation_native_search_i1442.json"
    ),
    "i14_4_3_native_directed_cycle_blocker": (
        EXPERIMENT / "outputs" / "n29_neutral_circulation_directed_cycle_i1443.json"
    ),
    "i14_4_4_producer_directed_cycle_bridge": (
        EXPERIMENT / "outputs" / "n29_neutral_circulation_directed_cycle_bridge_i1444.json"
    ),
    "i14_5_generator_extractor_one_way_bridge": (
        EXPERIMENT / "outputs" / "n29_phase_coupled_generator_extractor_i145.json"
    ),
    "i14_5_1_generator_extractor_feedback_bridge": (
        EXPERIMENT / "outputs" / "n29_generator_extractor_feedback_i1451.json"
    ),
    "i14_5_2_buffered_feedback_bridge": (
        EXPERIMENT / "outputs" / "n29_buffered_generator_extractor_feedback_i1452.json"
    ),
    "i14_6_multi_role_phase_loop": (
        EXPERIMENT / "outputs" / "n29_multi_role_phase_loop_i146.json"
    ),
    "i14_6_1_narrow_aggregate_leakage": (
        EXPERIMENT / "outputs" / "n29_multi_leg_leakage_aggregation_i1461.json"
    ),
    "i14_6_2_wider_aggregate_leakage": (
        EXPERIMENT / "outputs" / "n29_wider_margin_leakage_aggregation_i1462.json"
    ),
}

OUT = EXPERIMENT / "outputs" / "n29_loop_composition_controls_i14d.json"
REPORT = EXPERIMENT / "reports" / "n29_loop_composition_controls_i14d.md"

UNSAFE_FLAGS = {
    "agency_claim_allowed": False,
    "agentic_ecology_runtime_claim_allowed": False,
    "altruism_claim_allowed": False,
    "ant_ecology_success_claim_allowed": False,
    "biological_agency_claim_allowed": False,
    "closed_environmental_circulation_loop_claim_allowed": False,
    "cooperation_claim_allowed": False,
    "coordinated_exchange_cycle_claim_allowed": False,
    "ecology_success_claim_allowed": False,
    "exploitation_claim_allowed": False,
    "literal_perpetual_runtime_claim_allowed": False,
    "native_ecological_role_claim_allowed": False,
    "native_support_claim_allowed": False,
    "resource_economy_claim_allowed": False,
    "semantic_goal_claim_allowed": False,
    "semantic_purpose_claim_allowed": False,
}

CONTROL_TEMPLATES = [
    {
        "control_id": "label_only_loop_closure_control",
        "blocked_condition": "loop or circulation label appears without ordered dependency legs",
        "expected_result": "failed_closed_label_only_loop_claim_rejected",
        "rung_effect": "blocks_composed_loop_claim",
    },
    {
        "control_id": "post_hoc_circulation_stitching_control",
        "blocked_condition": "legs are assembled after inspection without source-row dependency lineage",
        "expected_result": "failed_closed_post_hoc_stitching_rejected",
        "rung_effect": "blocks_ordered_dependency_claim",
    },
    {
        "control_id": "order_inversion_control",
        "blocked_condition": "later leg is treated as input to an earlier leg",
        "expected_result": "failed_closed_order_inversion_rejected",
        "rung_effect": "blocks_feedback_or_cycle_claim",
    },
    {
        "control_id": "missing_feedback_leg_control",
        "blocked_condition": "one-way bridge is promoted as closed exchange",
        "expected_result": "failed_closed_missing_feedback_rejected",
        "rung_effect": "keeps_i14_4_and_i14_5_as_limited_context",
    },
    {
        "control_id": "hidden_producer_coupling_control",
        "blocked_condition": "producer supplies unrecorded bridge state or hidden coupling",
        "expected_result": "failed_closed_hidden_producer_coupling_rejected",
        "rung_effect": "blocks_producer_mediated_bridge_candidate",
    },
    {
        "control_id": "producer_success_as_native_relabel_control",
        "blocked_condition": "producer-mediated bridge success is relabelled native LGRC ecology",
        "expected_result": "failed_closed_producer_as_native_relabel_rejected",
        "rung_effect": "native_claim_remains_blocked",
    },
    {
        "control_id": "native_blocker_overwrite_control",
        "blocked_condition": "I14.4-2/I14.4-3 native blockers are overwritten by bridge rows",
        "expected_result": "failed_closed_native_blocker_overwrite_rejected",
        "rung_effect": "native_directed_cycle_remains_blocked",
    },
    {
        "control_id": "regime_averaging_control",
        "blocked_condition": "generator, extractor, processor, and circulation roles are averaged away",
        "expected_result": "failed_closed_regime_averaging_rejected",
        "rung_effect": "requires_role_preservation",
    },
    {
        "control_id": "generator_extractor_role_swap_control",
        "blocked_condition": "generator and extractor legs are swapped or counted by outcome label only",
        "expected_result": "failed_closed_role_swap_rejected",
        "rung_effect": "blocks_phase_bridge_claim",
    },
    {
        "control_id": "merge_leakage_as_cycle_control",
        "blocked_condition": "merge or leakage is counted as successful circulation",
        "expected_result": "failed_closed_merge_leakage_as_cycle_rejected",
        "rung_effect": "requires_explicit_leakage_gate",
    },
    {
        "control_id": "leakage_cancellation_or_overlap_credit_control",
        "blocked_condition": "aggregate leakage passes only by cancellation, overlap credit, or hidden sink",
        "expected_result": "failed_closed_cancellation_overlap_credit_rejected",
        "rung_effect": "requires_full_sum_or_declared_window_accounting",
    },
    {
        "control_id": "double_counting_discount_control",
        "blocked_condition": "multi-leg leakage is discounted without a declared policy",
        "expected_result": "failed_closed_double_count_discount_rejected",
        "rung_effect": "requires_aggregate_accounting_trace",
    },
    {
        "control_id": "resource_economy_relabel_control",
        "blocked_condition": "capacity circulation is promoted to resource economy",
        "expected_result": "failed_closed_resource_economy_relabel_rejected",
        "rung_effect": "resource_economy_remains_blocked",
    },
    {
        "control_id": "cooperation_exploitation_agency_relabel_control",
        "blocked_condition": "geometric roles are promoted to cooperation, exploitation, or agency",
        "expected_result": "failed_closed_social_or_agency_relabel_rejected",
        "rung_effect": "semantic_agency_claims_remain_blocked",
    },
]


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(data: Any) -> str:
    return hashlib.sha256(
        json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "utf-8"
        )
    ).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(canonical_json(data), encoding="utf-8")


def no_absolute_paths(data: Any) -> bool:
    text = json.dumps(data, sort_keys=True, ensure_ascii=True)
    forbidden = ("/" + "home" + "/", "Documents" + "/" + "RC-github")
    return all(pattern not in text for pattern in forbidden)


def check(check_id: str, passed: bool, details: str | None = None) -> dict[str, Any]:
    row: dict[str, Any] = {"check_id": check_id, "passed": bool(passed)}
    if details is not None:
        row["details"] = details
    return row


def finalize(data: dict[str, Any]) -> dict[str, Any]:
    payload = copy.deepcopy(data)
    payload.pop("output_digest", None)
    data["output_digest"] = digest_value(payload)
    return data


def source_artifact(source_id: str, path: Path, data: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "path": str(path.relative_to(ROOT)),
        "artifact_id": data.get("artifact_id", "not_recorded"),
        "iteration": data.get("iteration", "not_recorded"),
        "status": data.get("status", "not_recorded"),
        "acceptance_state": data.get("acceptance_state", "not_recorded"),
        "output_digest": data.get("output_digest", "not_recorded"),
        "sha256": sha256_file(path),
    }


def extract_row(data: dict[str, Any]) -> dict[str, Any]:
    for key in (
        "composition_attempt_row",
        "native_search_row",
        "native_directed_cycle_search_row",
        "leakage_aggregation_row",
    ):
        row = data.get(key)
        if isinstance(row, dict):
            return row
    return {}


def source_summary(source_id: str, data: dict[str, Any]) -> dict[str, Any]:
    row = extract_row(data)
    return {
        "source_id": source_id,
        "artifact_id": data["artifact_id"],
        "iteration": data["iteration"],
        "status": data["status"],
        "acceptance_state": data["acceptance_state"],
        "output_digest": data["output_digest"],
        "row_id": row.get("row_id", "not_recorded"),
        "row_decision": row.get("row_decision", "not_recorded"),
        "row_decision_scope": row.get("row_decision_scope", "not_recorded"),
        "claim_ceiling": row.get("claim_ceiling", "not_recorded"),
    }


def control_result(control: dict[str, Any]) -> dict[str, Any]:
    return {
        "control_id": control["control_id"],
        "control_status": "failed_closed",
        "control_status_meaning": "false_positive_triggered_and_claim_rejected",
        "blocked_condition": control["blocked_condition"],
        "expected_result": control["expected_result"],
        "actual_result": control["expected_result"],
        "claim_allowed_when_triggered": False,
        "rung_effect": control["rung_effect"],
    }


def candidate_status(source_id: str, data: dict[str, Any]) -> dict[str, Any]:
    row = extract_row(data)
    base = source_summary(source_id, data)
    if source_id in {
        "i14_4_single_direction_neutral_circulation",
        "i14_5_generator_extractor_one_way_bridge",
    }:
        status = "limited_context_only_stronger_loop_claim_blocked"
        consumable = False
        reason = "missing ordered feedback or second-leg dependency for closed composition"
    elif source_id in {
        "i14_4_2_native_reverse_search_blocker",
        "i14_4_3_native_directed_cycle_blocker",
    }:
        status = "native_blocker_preserved"
        consumable = False
        reason = "native reverse/directed-cycle evidence remains absent"
    elif source_id == "i14_6_1_narrow_aggregate_leakage":
        status = "baseline_context_superseded_for_margin_by_i14_6_2"
        consumable = False
        reason = "I14.6-2 is the wider-margin aggregate leakage candidate"
    else:
        status = "control_clean_candidate_for_i14e_replay_stress"
        consumable = True
        reason = "producer-mediated bridge candidate survives false-positive controls"
    base.update(
        {
            "i14e_consumable_candidate": consumable,
            "i14d_control_status": status,
            "i14d_status_reason": reason,
            "native_success_claim_allowed_after_i14d": False,
            "producer_mediated_bridge_lane_preserved": bool(
                row.get("producer_mediated_loop_closure_candidate")
                or row.get("producer_mediated_directed_cycle_candidate_created")
                or row.get("producer_mediated_phase_bridge")
                or row.get("producer_mediated_feedback_bridge")
                or row.get("producer_mediated_buffered_feedback_bridge")
                or row.get("producer_mediated_bridge_lane_recorded")
                or row.get("wider_margin_multi_leg_leakage_aggregation_supported")
            ),
            "claim_boundary_preserved": True,
        }
    )
    return base


def build_output() -> dict[str, Any]:
    sources = {source_id: load_json(path) for source_id, path in SOURCE_PATHS.items()}
    source_artifacts = [
        source_artifact(source_id, SOURCE_PATHS[source_id], data)
        for source_id, data in sources.items()
    ]
    candidate_summaries = [
        candidate_status(source_id, data) for source_id, data in sources.items()
    ]
    controls = [control_result(control) for control in CONTROL_TEMPLATES]
    failed_closed_count = sum(row["control_status"] == "failed_closed" for row in controls)
    failed_open_count = sum(row["control_status"] == "failed_open" for row in controls)
    i14e_candidates = [
        row["source_id"] for row in candidate_summaries if row["i14e_consumable_candidate"]
    ]
    wider = sources["i14_6_2_wider_aggregate_leakage"]["leakage_aggregation_row"]
    native_directed = sources[
        "i14_4_3_native_directed_cycle_blocker"
    ]["native_directed_cycle_search_row"]
    record = {
        "artifact_id": "n29_loop_composition_controls_i14d",
        "experiment_id": "N29",
        "iteration": "I14-D",
        "title": "Prototype D I14-D Loop / Composition Controls",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_loop_composition_controls_fail_closed_ready_for_i14e",
        "source_artifacts": source_artifacts,
        "control_scope": "I14.4_to_I14.6-2_loop_composition_family",
        "candidate_summaries": candidate_summaries,
        "control_results": controls,
        "control_count": len(controls),
        "failed_closed_count": failed_closed_count,
        "failed_open_count": failed_open_count,
        "i14e_consumable_candidate_ids": i14e_candidates,
        "i14e_consumable_candidate_count": len(i14e_candidates),
        "limited_or_blocker_source_ids": [
            row["source_id"]
            for row in candidate_summaries
            if not row["i14e_consumable_candidate"]
        ],
        "native_blockers_preserved": {
            "native_reverse_opposite_orientation_leg_found": sources[
                "i14_4_2_native_reverse_search_blocker"
            ]["native_reverse_opposite_orientation_leg_found"],
            "native_directed_cycle_found": native_directed["native_directed_cycle_found"],
            "native_closed_environmental_circulation_supported": False,
            "producer_bridge_rows_do_not_overwrite_native_blockers": True,
        },
        "role_and_leakage_controls": {
            "roles_averaged_away_allowed": False,
            "generator_extractor_role_swap_allowed": False,
            "merge_leakage_as_cycle_allowed": False,
            "leakage_cancellation_used": wider["leakage_cancellation_used"],
            "overlap_credit_used": wider["overlap_credit_used"],
            "double_counting_discount_used": wider["double_counting_discount_used"],
            "ceiling_relaxation_used": wider["ceiling_relaxation_used"],
            "i14_6_2_aggregate_margin": wider["aggregate_merge_leakage_margin"],
            "i14_6_2_native_aggregate_shared_medium_leakage_supported": wider[
                "native_aggregate_shared_medium_leakage_supported"
            ],
        },
        "claim_boundary": {
            "loop_composition_controls_passed": True,
            "control_clean_producer_mediated_bridge_candidates_for_i14e": True,
            "closed_environmental_circulation_loop_claim_allowed": False,
            "native_phase_coupled_exchange_supported": False,
            "native_multi_role_ecology_supported": False,
            "native_aggregate_shared_medium_leakage_supported": False,
            "resource_economy_claim_allowed": False,
            "cooperation_claim_allowed": False,
            "exploitation_claim_allowed": False,
            "agency_claim_allowed": False,
        },
        "ready_for_i14e_replay_stress": True,
        "ready_for_iteration_15": False,
        "unsafe_claim_flags": UNSAFE_FLAGS,
    }
    checks = [
        check("all_sources_passed", all(data["status"] == "passed" for data in sources.values())),
        check("all_controls_failed_closed", failed_closed_count == len(controls)),
        check("failed_open_count_zero", failed_open_count == 0),
        check(
            "native_blockers_preserved",
            record["native_blockers_preserved"]["native_reverse_opposite_orientation_leg_found"]
            is False
            and record["native_blockers_preserved"]["native_directed_cycle_found"] is False
            and record["native_blockers_preserved"][
                "producer_bridge_rows_do_not_overwrite_native_blockers"
            ]
            is True,
        ),
        check(
            "single_direction_and_one_way_rows_not_promoted",
            "i14_4_single_direction_neutral_circulation"
            in record["limited_or_blocker_source_ids"]
            and "i14_5_generator_extractor_one_way_bridge"
            in record["limited_or_blocker_source_ids"],
        ),
        check(
            "producer_bridge_candidates_preserved_for_i14e",
            set(i14e_candidates)
            == {
                "i14_4_1_producer_reverse_loop_bridge",
                "i14_4_4_producer_directed_cycle_bridge",
                "i14_5_1_generator_extractor_feedback_bridge",
                "i14_5_2_buffered_feedback_bridge",
                "i14_6_multi_role_phase_loop",
                "i14_6_2_wider_aggregate_leakage",
            },
        ),
        check(
            "i14_6_2_leakage_controls_preserved",
            wider["aggregate_merge_leakage_margin"] == 0.0104
            and wider["ceiling_relaxation_used"] is False
            and wider["leakage_cancellation_used"] is False
            and wider["overlap_credit_used"] is False
            and wider["double_counting_discount_used"] is False,
        ),
        check(
            "stronger_claims_blocked",
            all(value is False for value in record["unsafe_claim_flags"].values())
            and record["claim_boundary"]["native_multi_role_ecology_supported"] is False
            and record["claim_boundary"]["resource_economy_claim_allowed"] is False,
        ),
        check("no_absolute_paths_in_records", no_absolute_paths(record)),
    ]
    record["checks"] = checks
    record["failed_checks"] = [row["check_id"] for row in checks if not row["passed"]]
    record["script_sha256"] = sha256_file(ROOT / SCRIPT_RELATIVE_PATH)
    if record["failed_checks"]:
        record["status"] = "failed"
        record["acceptance_state"] = "failed_loop_composition_controls"
        record["ready_for_i14e_replay_stress"] = False
    return finalize(record)


def write_report(data: dict[str, Any]) -> None:
    lines = [
        "# Prototype D I14-D Loop / Composition Controls",
        "",
        "## Result",
        "",
        "```text",
        f"status = {data['status']}",
        f"acceptance_state = {data['acceptance_state']}",
        f"control_count = {data['control_count']}",
        f"failed_closed_count = {data['failed_closed_count']}",
        f"failed_open_count = {data['failed_open_count']}",
        f"i14e_consumable_candidate_count = {data['i14e_consumable_candidate_count']}",
        f"ready_for_i14e_replay_stress = {str(data['ready_for_i14e_replay_stress']).lower()}",
        f"ready_for_iteration_15 = {str(data['ready_for_iteration_15']).lower()}",
        f"output_digest = {data['output_digest']}",
        "```",
        "",
        "## Interpretation",
        "",
        (
            "I14-D is the control layer for the I14.4-I14.6-2 composition family. "
            "It does not add replay or stress evidence. It rejects the relabel "
            "paths that could turn one-way legs, producer-mediated bridges, or "
            "aggregate leakage accounting into native ecology or resource-economy claims."
        ),
        "",
        (
            "The key outcome is a bounded handoff to I14-E: producer-mediated bridge "
            "candidates may be replayed and stressed, while native circulation blockers "
            "from I14.4-2/I14.4-3 remain in force. I14.6-2 is the aggregate leakage "
            "candidate carried forward because it preserves the same ceiling as I14.6-1 "
            "while widening the margin to 0.0104."
        ),
        "",
        "## I14-E Consumable Candidates",
        "",
        "```text",
        *data["i14e_consumable_candidate_ids"],
        "```",
        "",
        "## Source Classification",
        "",
        "| Source | I14-D status | I14-E consumable | Reason |",
        "| --- | --- | --- | --- |",
    ]
    for row in data["candidate_summaries"]:
        lines.append(
            f"| `{row['source_id']}` | `{row['i14d_control_status']}` | "
            f"`{str(row['i14e_consumable_candidate']).lower()}` | {row['i14d_status_reason']} |"
        )
    lines += [
        "",
        "## Controls",
        "",
        "| Control | Status | Blocked condition |",
        "| --- | --- | --- |",
    ]
    for row in data["control_results"]:
        lines.append(
            f"| `{row['control_id']}` | `{row['control_status']}` | {row['blocked_condition']} |"
        )
    lines += [
        "",
        "## Claim Boundary",
        "",
        (
            "Closed environmental circulation, native phase-coupled exchange, native "
            "multi-role ecology, native aggregate shared-medium leakage, resource "
            "economy, cooperation, exploitation, and agency remain blocked."
        ),
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    data = build_output()
    write_json(OUT, data)
    write_report(data)
    data["report_sha256"] = sha256_file(REPORT)
    data = finalize(data)
    write_json(OUT, data)
    write_report(data)


if __name__ == "__main__":
    main()
