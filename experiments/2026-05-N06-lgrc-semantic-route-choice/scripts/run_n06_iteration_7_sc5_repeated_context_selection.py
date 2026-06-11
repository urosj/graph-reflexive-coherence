#!/usr/bin/env python3
"""Run N06 Iteration 7: SC5 repeated context-conditioned selection.

This probe repeats context-conditioned native route arbitration across distinct
arbitration windows. Each window serializes its current context state and the
selected route must be reconstructed from that context evidence, not from a
hidden schedule or preauthored route list.
"""

from __future__ import annotations

import copy
import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import run_n06_iteration_3_sc1_candidate_alternatives as iter3  # noqa: E402
import run_n06_iteration_4_sc2_native_arbitration as iter4  # noqa: E402
import run_n06_iteration_5_sc3_context_conditioned_selection as iter5  # noqa: E402
import run_n06_iteration_6_sc4_context_swap_controls as iter6  # noqa: E402


N06 = ROOT / "experiments/2026-05-N06-lgrc-semantic-route-choice"
MANIFEST_PATH = N06 / "configs/n06_fixture_manifest_v1.json"
OUTPUT_PATH = N06 / "outputs/n06_iteration_7_sc5_repeated_context_selection.json"
REPORT_PATH = N06 / "reports/n06_iteration_7_sc5_repeated_context_selection.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N06-lgrc-semantic-route-choice/scripts/"
    "run_n06_iteration_7_sc5_repeated_context_selection.py"
)

CONTEXT_SEQUENCE = (
    ("cycle_0", "context_a"),
    ("cycle_1", "context_b"),
    ("cycle_2", "context_a"),
    ("cycle_3", "context_b"),
)

SCHEDULE_FORBIDDEN_FIELDS = {
    "hidden_schedule",
    "preauthored_selection_list",
    "preauthored_route_sequence",
    "preauthored_context_sequence",
    "report_side_schedule",
}

TRAIL_FORBIDDEN_FIELDS = {
    "memory_trail",
    "persistent_score_update",
    "trail_accumulation",
    "route_conductance_memory",
}


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _digest(data: Any) -> str:
    return hashlib.sha256(_canonical_json(data).encode("utf-8")).hexdigest()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _artifact_record(path: Path) -> dict[str, str]:
    return {"path": _rel(path), "sha256": _sha256(path)}


def _git(args: list[str]) -> dict[str, Any]:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return {
        "command": "git " + " ".join(args),
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def _cycle_manifest(
    manifest: Mapping[str, Any],
    *,
    cycle_id: str,
) -> dict[str, Any]:
    cycle_manifest = copy.deepcopy(manifest)
    base_window_id = str(manifest["arbitration_window"]["arbitration_window_id"])
    cycle_manifest["arbitration_window"]["arbitration_window_id"] = (
        f"{base_window_id}:{cycle_id}"
    )
    return cycle_manifest


def _context_compatible_route(
    manifest: Mapping[str, Any],
    context_state_id: str,
) -> str:
    return str(
        manifest["context_affordance_surface"]["context_states"][context_state_id][
            "compatible_route_id"
        ]
    )


def _sc5_lane(
    manifest: Mapping[str, Any],
    *,
    cycle_index: int,
    cycle_id: str,
    context_state_id: str,
) -> dict[str, Any]:
    cycle_manifest = _cycle_manifest(manifest, cycle_id=cycle_id)
    lane = iter5._run_context_lane(  # noqa: SLF001
        cycle_manifest,
        context_state_id=context_state_id,
    )
    lane = copy.deepcopy(lane)
    lane["lane_id"] = f"sc5_{cycle_id}_{context_state_id}_native_arbitration"
    lane["cycle_id"] = cycle_id
    lane["cycle_index"] = cycle_index
    lane["context_state_id"] = context_state_id
    lane["arbitration_window_id"] = cycle_manifest["arbitration_window"][
        "arbitration_window_id"
    ]
    lane["expected_compatible_route"] = _context_compatible_route(
        manifest,
        context_state_id,
    )
    lane["selection_only_artifact_validation"]["validator_scope"] = (
        "sc5_repeated_context_selection_pre_topology_commit"
    )
    return lane


def _runtime_inputs_for_lanes(lanes: Sequence[Mapping[str, Any]]) -> list[str]:
    values: list[str] = []
    for lane in lanes:
        values.extend(iter6._runtime_inputs_for_lane(lane))  # noqa: SLF001
    return sorted(values)


def _forbidden_runtime_inputs(
    lanes: Sequence[Mapping[str, Any]],
    forbidden_fields: set[str],
) -> list[str]:
    found: list[str] = []
    for value in _runtime_inputs_for_lanes(lanes):
        field_name = value.split(":", 1)[0]
        if field_name in forbidden_fields:
            found.append(value)
    return sorted(set(found))


def _schedule_forbidden_inputs(lanes: Sequence[Mapping[str, Any]]) -> list[str]:
    forbidden_fields = (
        set(iter5.HIDDEN_INPUTS)
        | set(iter6.DIRECTION_LABEL_PREFIXES)
        | SCHEDULE_FORBIDDEN_FIELDS
    )
    return _forbidden_runtime_inputs(lanes, forbidden_fields)


def _trail_like_inputs(lanes: Sequence[Mapping[str, Any]]) -> list[str]:
    return _forbidden_runtime_inputs(lanes, TRAIL_FORBIDDEN_FIELDS)


def _context_input_signature(lane: Mapping[str, Any]) -> list[str]:
    context_fields = {
        "active_context_node_id",
        "compatible_route_id",
        "context_surface_digest",
    }
    return sorted(
        str(value)
        for value in lane["route_arbitration_record"][
            "arbitration_runtime_visible_inputs"
        ]
        if str(value).split(":", 1)[0] in context_fields
    )


def _cycle_replay(lanes: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    per_cycle: list[dict[str, Any]] = []
    for lane in lanes:
        replay_checks = lane["context_relation_replay"]["checks"]
        selected = lane["selected_candidate_route_id"]
        compatible = lane["expected_compatible_route"]
        candidate_set = lane["candidate_set_record"]
        arbitration = lane["route_arbitration_record"]
        checks = {
            "cycle_id_present": bool(lane["cycle_id"]),
            "arbitration_window_id_present": bool(lane["arbitration_window_id"]),
            "candidate_set_window_matches_cycle": (
                candidate_set["arbitration_window_id"] == lane["arbitration_window_id"]
            ),
            "selected_route_matches_current_context": selected == compatible,
            "serialized_context_replayable": lane["context_relation_replay"][
                "context_relation_replayable"
            ],
            "uses_committed_current_context_evidence": (
                replay_checks["serialized_context_matches_expected_context"]
                and replay_checks["candidate_arbitration_context_consistent"]
                and replay_checks["arbitration_context_fields_serialized"]
            ),
            "route_arbitration_consumes_candidate_set": (
                arbitration["candidate_set_digest"] == lane["candidate_set_digest"]
            ),
            "selected_and_rejected_digests_present": bool(
                lane["selected_candidate_route_digest"]
            )
            and bool(lane["rejected_candidate_route_digests"]),
            "artifact_selection_replay_clean": lane[
                "selection_only_artifact_validation"
            ]["selection_contract_valid"],
            "budget_exact": lane["checks"]["budget_exact"],
            "no_topology_commit": lane["checks"]["no_topology_event_committed"],
            "no_packet_scheduled": lane["checks"]["no_packet_scheduled_by_arbitration"],
            "claim_flags_remain_false": lane["checks"]["claim_flags_remain_false"],
            "no_forbidden_runtime_inputs": not _schedule_forbidden_inputs([lane]),
        }
        per_cycle.append(
            {
                "cycle_id": lane["cycle_id"],
                "cycle_index": lane["cycle_index"],
                "arbitration_window_id": lane["arbitration_window_id"],
                "context_state_id": lane["context_state_id"],
                "selected_route": selected,
                "expected_compatible_route": compatible,
                "selected_candidate_route_digest": lane[
                    "selected_candidate_route_digest"
                ],
                "rejected_candidate_route_digests": lane[
                    "rejected_candidate_route_digests"
                ],
                "candidate_set_digest": lane["candidate_set_digest"],
                "context_input_signature": _context_input_signature(lane),
                "checks": checks,
                "replay_ok": all(checks.values()),
            }
        )
    window_ids = [cycle["arbitration_window_id"] for cycle in per_cycle]
    selected_routes = [cycle["selected_route"] for cycle in per_cycle]
    expected_routes = [cycle["expected_compatible_route"] for cycle in per_cycle]
    signatures_by_context: dict[str, list[list[str]]] = {}
    for cycle in per_cycle:
        signatures_by_context.setdefault(cycle["context_state_id"], []).append(
            cycle["context_input_signature"]
        )
    repeated_context_signatures_stable = all(
        len({tuple(signature) for signature in signatures}) == 1
        for signatures in signatures_by_context.values()
    )
    context_signatures = {
        context_state: tuple(signatures[0])
        for context_state, signatures in signatures_by_context.items()
        if signatures
    }
    distinct_context_signatures = (
        len(set(context_signatures.values())) == len(context_signatures)
    )
    context_relation_replayable_all_cycles = all(
        cycle["checks"]["serialized_context_replayable"]
        and cycle["checks"]["uses_committed_current_context_evidence"]
        and cycle["checks"]["selected_route_matches_current_context"]
        for cycle in per_cycle
    )
    checks = {
        "cycle_count_is_four": len(per_cycle) == 4,
        "cycle_ids_distinct": len({cycle["cycle_id"] for cycle in per_cycle})
        == len(per_cycle),
        "arbitration_window_ids_distinct": len(set(window_ids)) == len(window_ids),
        "candidate_set_digests_distinct": (
            len({cycle["candidate_set_digest"] for cycle in per_cycle})
            == len(per_cycle)
        ),
        "selected_route_sequence_matches_context_sequence": (
            selected_routes == expected_routes
        ),
        "serialized_context_causality_replayable_all_cycles": (
            context_relation_replayable_all_cycles
        ),
        "repeated_context_input_signatures_stable": (
            repeated_context_signatures_stable
        ),
        "distinct_context_input_signatures": distinct_context_signatures,
        "every_cycle_replayable": all(cycle["replay_ok"] for cycle in per_cycle),
        "no_forbidden_runtime_inputs": not _schedule_forbidden_inputs(lanes),
        "no_trail_like_runtime_inputs": not _trail_like_inputs(lanes),
    }
    return {
        "context_sequence": [lane["context_state_id"] for lane in lanes],
        "selected_route_sequence": selected_routes,
        "expected_route_sequence_from_context": expected_routes,
        "arbitration_window_ids": window_ids,
        "context_input_signatures_by_context": {
            context: signatures
            for context, signatures in sorted(signatures_by_context.items())
        },
        "forbidden_runtime_inputs": _schedule_forbidden_inputs(lanes),
        "trail_like_runtime_inputs": _trail_like_inputs(lanes),
        "per_cycle": per_cycle,
        "checks": checks,
        "replay_ok": all(checks.values()),
    }


def _selection_only_validation_from_lane(lane: Mapping[str, Any]) -> dict[str, Any]:
    artifacts = {
        "events": [],
        "candidate_route_records": lane["candidate_route_records"],
        "candidate_set_records": [lane["candidate_set_record"]],
        "route_arbitration_records": [lane["route_arbitration_record"]],
        "surface_rows": [],
        "surface_lineage_records": [],
        "topology_events": [],
        "topology_state_reabsorption_records": [],
        "production_results": [],
    }
    validation = iter5._selection_only_validation(artifacts)  # noqa: SLF001
    validation["validator_scope"] = (
        "sc5_aggregate_revalidation_pre_topology_commit"
    )
    return validation


def _artifact_only_replay(lanes: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    per_cycle = []
    for lane in lanes:
        validation = _selection_only_validation_from_lane(lane)
        lane_validation = lane["selection_only_artifact_validation"]
        per_cycle.append(
            {
                "cycle_id": lane["cycle_id"],
                "artifact_only": True,
                "runtime_state_used": False,
                "independent_native_validator_invoked": True,
                "native_validator_valid": validation["valid"],
                "selection_contract_valid_under_pre_topology_scope": validation[
                    "selection_contract_valid"
                ],
                "matches_lane_selection_contract": (
                    validation["selection_contract_valid"]
                    == lane_validation["selection_contract_valid"]
                ),
                "context_relation_replayable": lane["context_relation_replay"][
                    "context_relation_replayable"
                ],
                "route_selection_reconstructed_from_artifacts": validation[
                    "route_selection_reconstructed_from_artifacts"
                ],
                "unexpected_failure_reasons": validation[
                    "unexpected_failure_reasons"
                ],
                "expected_incomplete_reasons": validation[
                    "expected_incomplete_reasons"
                ],
                "replay_ok": lane["context_relation_replay"][
                    "context_relation_replayable"
                ]
                and validation["selection_contract_valid"],
            }
        )
    return {
        "artifact_only": True,
        "runtime_state_used": False,
        "independent_native_validator_invoked_per_cycle": True,
        "cycle_count": len(per_cycle),
        "per_cycle": per_cycle,
        "all_cycles_reconstructed": all(cycle["replay_ok"] for cycle in per_cycle),
        "validator_scope": "sc5_repeated_context_selection_pre_topology_commit",
    }


def _control_result(
    control_id: str,
    *,
    passed: bool,
    primary_blocker: str,
    detail: Any = None,
    scope: str = "n06_sc5_validator",
) -> dict[str, Any]:
    return {
        "control_id": control_id,
        "scope": scope,
        "passed": bool(passed),
        "primary_blocker": primary_blocker,
        "detail": detail,
    }


def _sc5_artifact_semantic_validator(lane: Mapping[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    forbidden = _schedule_forbidden_inputs([lane])
    if forbidden:
        reasons.append("n06_hidden_schedule_rejected")
    validation = iter5._semantic_context_validator(lane)  # noqa: SLF001
    reasons.extend(str(reason) for reason in validation["failure_reasons"])
    return {
        "valid": not reasons,
        "failure_reasons": iter5._dedupe_reasons(reasons),  # noqa: SLF001
        "forbidden_runtime_inputs": forbidden,
    }


def _hidden_schedule_control(lanes: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    per_cycle: list[dict[str, Any]] = []
    for lane in lanes:
        corrupted = copy.deepcopy(lane)
        for record in corrupted["candidate_route_records"]:
            record["candidate_runtime_visible_inputs"].append(
                "preauthored_route_sequence:route_a,route_b,route_a,route_b"
            )
        corrupted["route_arbitration_record"][
            "arbitration_runtime_visible_inputs"
        ].append("hidden_schedule:cycle_index_to_route")
        validation = _sc5_artifact_semantic_validator(corrupted)
        per_cycle.append(
            {
                "cycle_id": lane["cycle_id"],
                "valid": validation["valid"],
                "failure_reasons": validation["failure_reasons"],
                "forbidden_runtime_inputs": validation["forbidden_runtime_inputs"],
                "passed": validation["valid"] is False
                and "n06_hidden_schedule_rejected"
                in validation["failure_reasons"],
            }
        )
    return _control_result(
        "hidden_schedule",
        passed=all(cycle["passed"] for cycle in per_cycle),
        primary_blocker="n06_hidden_schedule_rejected",
        detail={
            "scope_note": (
                "N06 experiment-level semantic artifact replay control; "
                "native LGRC has no dedicated hidden-schedule validator yet."
            ),
            "per_cycle": per_cycle,
        },
        scope="artifact_semantic_replay_control_all_cycles",
    )


def _stale_context_control(manifest: Mapping[str, Any]) -> dict[str, Any]:
    control = iter5._run_stale_context_control(manifest)  # noqa: SLF001
    control["control_id"] = "stale_context"
    control["scope"] = "n06_sc5_validator"
    return control


def _duplicate_arbitration_control(manifest: Mapping[str, Any]) -> dict[str, Any]:
    cycle_manifest = _cycle_manifest(manifest, cycle_id="duplicate_control")
    prepared = iter4._prepare_candidate_model(  # noqa: SLF001
        cycle_manifest,
        context_state_id="context_a",
    )
    candidate_set = prepared["candidate_set"]
    arbitration_inputs = iter5._arbitration_inputs_for_context(  # noqa: SLF001
        cycle_manifest,
        context_state_id="context_a",
        source_surface_digest=prepared["source_surface_digest"],
    )
    first = prepared["model"].arbitrate_native_route_candidate_set(
        candidate_set_digest=str(candidate_set.candidate_set_digest),
        arbitration_runtime_visible_inputs=arbitration_inputs,
    )
    count_after_first = iter3._runtime_counts(prepared["model"])[  # noqa: SLF001
        "route_arbitration_count"
    ]
    second = prepared["model"].arbitrate_native_route_candidate_set(
        candidate_set_digest=str(candidate_set.candidate_set_digest),
        arbitration_runtime_visible_inputs=arbitration_inputs,
    )
    count_after_second = iter3._runtime_counts(prepared["model"])[  # noqa: SLF001
        "route_arbitration_count"
    ]
    same_record = (
        first["route_arbitration_record"].to_artifact()
        == second["route_arbitration_record"].to_artifact()
    )
    first_artifact = first["route_arbitration_record"].to_artifact()
    reconstructed_idempotency_key = (
        iter4.build_lgrc9v3_native_route_arbitration_idempotency_key(  # noqa: SLF001
            native_route_arbitration_policy_id=str(
                first_artifact["native_route_arbitration_policy_id"]
            ),
            candidate_set_digest=str(first_artifact["candidate_set_digest"]),
            selected_candidate_route_digest=first_artifact[
                "selected_candidate_route_digest"
            ],
            arbitration_reason_code=str(first_artifact["arbitration_reason_code"]),
            arbitration_rule=str(first_artifact["arbitration_rule"]),
            selected_topology_event_id=first_artifact["selected_topology_event_id"],
        )
    )
    idempotency_reconstructable = (
        reconstructed_idempotency_key == first_artifact["idempotency_key"]
    )
    return _control_result(
        "duplicate_arbitration",
        passed=(
            count_after_first == 1
            and count_after_second == 1
            and same_record
            and idempotency_reconstructable
        ),
        primary_blocker="duplicate_native_route_arbitration_suppressed",
        detail={
            "count_after_first": count_after_first,
            "count_after_second": count_after_second,
            "same_route_arbitration_artifact": same_record,
            "same_idempotency_key": (
                first["route_arbitration_record"].idempotency_key
                == second["route_arbitration_record"].idempotency_key
            ),
            "same_arbitration_digest": (
                first["route_arbitration_record"].native_route_arbitration_digest
                == second["route_arbitration_record"].native_route_arbitration_digest
            ),
            "recorded_idempotency_key": first_artifact["idempotency_key"],
            "reconstructed_idempotency_key": reconstructed_idempotency_key,
            "idempotency_key_reconstructable": idempotency_reconstructable,
        },
        scope="native_runtime_duplicate_suppression",
    )


def _budget_drift_control(manifest: Mapping[str, Any]) -> dict[str, Any]:
    control = iter5._run_budget_mismatch_control(manifest)  # noqa: SLF001
    control["control_id"] = "budget_drift"
    control["primary_blocker"] = "native_route_arbitration_budget_invalid"
    control["detail"] = {
        "scope_note": (
            "Single-candidate budget-mismatch control reused as the SC5 "
            "budget guard. Cross-cycle accumulated budget drift is not tested "
            "because SC5 uses independent runtime windows."
        ),
        "cross_cycle_budget_accumulation_tested": False,
        "source_control": control["detail"],
    }
    return control


def _producer_mutation_control(lanes: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    per_cycle: list[dict[str, Any]] = []
    for lane in lanes:
        control = iter5._run_producer_mutation_control(lane)  # noqa: SLF001
        per_cycle.append(
            {
                "cycle_id": lane["cycle_id"],
                "passed": control["passed"],
                "primary_blocker": control["primary_blocker"],
                "detail": control["detail"],
            }
        )
    return _control_result(
        "producer_mutation",
        passed=all(cycle["passed"] for cycle in per_cycle),
        primary_blocker="n06_producer_mutation_boundary_violation",
        detail={"per_cycle": per_cycle},
        scope="boundary_control_all_cycles",
    )


def _claim_promotion_control(lanes: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    per_cycle: list[dict[str, Any]] = []
    for lane in lanes:
        control = iter5._run_claim_promotion_control(lane)  # noqa: SLF001
        per_cycle.append(
            {
                "cycle_id": lane["cycle_id"],
                "passed": control["passed"],
                "primary_blocker": control["primary_blocker"],
                "detail": control["detail"],
            }
        )
    return _control_result(
        "claim_promotion",
        passed=all(cycle["passed"] for cycle in per_cycle),
        primary_blocker="native_route_arbitration_claim_promotion_blocked",
        detail={"per_cycle": per_cycle},
        scope="artifact_replay_control_all_cycles",
    )


def _run_controls(
    manifest: Mapping[str, Any],
    lanes: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    return {
        "hidden_schedule": _hidden_schedule_control(lanes),
        "stale_context": _stale_context_control(manifest),
        "duplicate_arbitration": _duplicate_arbitration_control(manifest),
        "budget_drift": _budget_drift_control(manifest),
        "producer_mutation": _producer_mutation_control(lanes),
        "claim_promotion": _claim_promotion_control(lanes),
    }


def _build_report(data: Mapping[str, Any]) -> str:
    replay = data["cycle_replay"]
    lines = [
        "# N06 Iteration 7 SC5 Repeated Context-Conditioned Selection",
        "",
        f"- status: `{data['status']}`",
        f"- generated: `{data['generated_at']}`",
        f"- command: `{COMMAND}`",
        f"- context sequence: `{replay['context_sequence']}`",
        f"- selected route sequence: `{replay['selected_route_sequence']}`",
        "",
        "## Boundary",
        "",
        "- SC5 repeats context-conditioned native route arbitration across distinct independent runtime windows.",
        "- This is not a single-runtime persistence or accumulated budget-drift test.",
        "- Each selected route is reconstructed from serialized context evidence in its own window.",
        "- No topology event is committed, no packet is scheduled, and no semantic-choice/agency/memory/identity/movement claim is promoted.",
        "",
        "## Scope Notes",
        "",
        "```json",
        json.dumps(data["scope_notes"], indent=2, sort_keys=True),
        "```",
        "",
        "## Acceptance",
        "",
        "```json",
        json.dumps(data["acceptance"], indent=2, sort_keys=True),
        "```",
        "",
        "## Cycle Replay",
        "",
        "```json",
        json.dumps(data["cycle_replay"], indent=2, sort_keys=True),
        "```",
        "",
        "## Artifact-Only Replay",
        "",
        "```json",
        json.dumps(data["artifact_only_replay"], indent=2, sort_keys=True),
        "```",
        "",
        "## Controls",
        "",
        "```json",
        json.dumps(data["controls"], indent=2, sort_keys=True),
        "```",
        "",
        "## Artifact Digests",
        "",
        "```json",
        json.dumps(data["artifact_digests"], indent=2, sort_keys=True),
        "```",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    manifest = iter3._load_manifest()  # noqa: SLF001
    lanes = [
        _sc5_lane(
            manifest,
            cycle_index=index,
            cycle_id=cycle_id,
            context_state_id=context_state_id,
        )
        for index, (cycle_id, context_state_id) in enumerate(CONTEXT_SEQUENCE)
    ]
    cycle_replay = _cycle_replay(lanes)
    artifact_replay = _artifact_only_replay(lanes)
    controls = _run_controls(manifest, lanes)
    checks = {
        "cycle_replay_passed": cycle_replay["replay_ok"],
        "artifact_only_replay_passed": artifact_replay["all_cycles_reconstructed"],
        "controls_passed": all(control["passed"] for control in controls.values()),
        "distinct_cycle_ids": cycle_replay["checks"]["cycle_ids_distinct"],
        "distinct_window_ids": cycle_replay["checks"][
            "arbitration_window_ids_distinct"
        ],
        "selected_route_sequence_matches_context_sequence": cycle_replay["checks"][
            "selected_route_sequence_matches_context_sequence"
        ],
        "no_hidden_schedule_or_preauthored_selection": cycle_replay["checks"][
            "no_forbidden_runtime_inputs"
        ],
        "serialized_context_causality_replayable": cycle_replay["checks"][
            "serialized_context_causality_replayable_all_cycles"
        ],
        "distinct_context_input_signatures": cycle_replay["checks"][
            "distinct_context_input_signatures"
        ],
        "no_trail_like_runtime_inputs": cycle_replay["checks"][
            "no_trail_like_runtime_inputs"
        ],
        "budget_exact": all(lane["checks"]["budget_exact"] for lane in lanes),
        "no_topology_commit": all(
            lane["checks"]["no_topology_event_committed"] for lane in lanes
        ),
        "claim_flags_remain_false": all(
            lane["checks"]["claim_flags_remain_false"] for lane in lanes
        ),
    }
    status = "passed" if all(checks.values()) else "failed"
    acceptance = {
        "sc_level": "SC5",
        "claim_ceiling": "repeated_context_conditioned_route_selection_candidate",
        "cycle_count": len(lanes),
        "context_sequence": cycle_replay["context_sequence"],
        "selected_route_sequence": cycle_replay["selected_route_sequence"],
        "selected_route_sequence_matches_context_sequence": checks[
            "selected_route_sequence_matches_context_sequence"
        ],
        "distinct_window_ids": checks["distinct_window_ids"],
        "artifact_only_replay_reconstructs_every_selection": checks[
            "artifact_only_replay_passed"
        ],
        "hidden_schedule_or_preauthored_selection_used": False,
        "selection_causality_basis": (
            "serialized_context_relation_replay_and_native_selection_replay"
        ),
        "independent_runtime_instances_per_cycle": True,
        "single_runtime_multi_window_persistence_tested": False,
        "cross_window_budget_accumulation_tested": False,
        "trail_like_state_created": False,
        "budget_exact": checks["budget_exact"],
        "semantic_choice_claim_allowed": False,
        "topology_event_committed": False,
        "packet_scheduled_by_arbitration": False,
        "status": status,
    }
    data: dict[str, Any] = {
        "schema": "semantic_route_choice_report_v1",
        "experiment": "2026-05-N06-lgrc-semantic-route-choice",
        "iteration": 7,
        "iteration_name": "SC5 Repeated Context-Conditioned Selection",
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": COMMAND,
        "platform": {
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "manifest": _artifact_record(MANIFEST_PATH),
        "source_iteration": _artifact_record(iter6.OUTPUT_PATH),
        "cycle_plan": {
            "context_sequence_declared": [context for _cycle, context in CONTEXT_SEQUENCE],
            "route_sequence_preauthored": False,
            "expected_routes_derived_from_serialized_context": True,
            "cycle_ids": [cycle for cycle, _context in CONTEXT_SEQUENCE],
        },
        "lanes": {lane["cycle_id"]: lane for lane in lanes},
        "cycle_replay": cycle_replay,
        "artifact_only_replay": artifact_replay,
        "controls": controls,
        "checks": checks,
        "acceptance": acceptance,
        "claim_flags": {flag: False for flag in iter3.CLAIM_FLAGS},
        "scope_notes": {
            "independent_runtime_instances_per_cycle": True,
            "single_runtime_multi_window_persistence_tested": False,
            "cross_window_state_persistence_tested": False,
            "cross_window_budget_accumulation_tested": False,
            "repeated_windows_not_long_lived_memory": True,
            "memory_or_trail_deferred_to": "N08",
            "selection_sequence_alone_is_not_causality_proof": True,
            "selection_causality_basis": (
                "artifact replay checks serialized context fields, context "
                "score components, selected/rejected digests, and native "
                "arbitration records for each independent cycle."
            ),
            "stale_context_and_order_controls": (
                "N06 artifact-level semantic replay controls until a future "
                "Phase 8 native semantic-context validator exists."
            ),
            "hidden_schedule_control_scope": (
                "N06 experiment-level semantic artifact replay control; "
                "native LGRC route arbitration only rejects the hidden-input "
                "fields in its current contract."
            ),
        },
        "artifact_digests": {},
        "git": {
            "status_src": _git(["status", "--short", "src"]),
            "diff_check_experiment": _git(
                ["diff", "--check", "--", _rel(N06)]
            ),
        },
    }
    data["artifact_digests"] = {
        "lanes_digest": _digest(data["lanes"]),
        "cycle_replay_digest": _digest(cycle_replay),
        "artifact_only_replay_digest": _digest(artifact_replay),
        "controls_digest": _digest(controls),
        "acceptance_digest": _digest(acceptance),
        "claim_flags_digest": _digest(data["claim_flags"]),
    }
    OUTPUT_PATH.write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    REPORT_PATH.write_text(_build_report(data), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": status,
                "output": _rel(OUTPUT_PATH),
                "report": _rel(REPORT_PATH),
                "cycle_count": len(lanes),
                "selected_route_sequence": cycle_replay["selected_route_sequence"],
                "controls_passed": checks["controls_passed"],
                "semantic_choice_claim_allowed": False,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
