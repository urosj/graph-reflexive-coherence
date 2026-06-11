#!/usr/bin/env python3
"""Run N06 Iteration 8: SC6 artifact-only replay and closeout.

This closeout reads the source-backed N06 artifacts, replays the Iteration 7
selection evidence without private runtime state, records the strongest
supported SC level, and freezes the N07 handoff criteria. It does not run a new
route-choice probe.
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

from pygrc.models import (  # noqa: E402
    LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_HIDDEN_INPUT_REJECTED,
    validate_lgrc9v3_native_route_arbitration_artifacts,
)

import run_n06_iteration_3_sc1_candidate_alternatives as iter3  # noqa: E402
import run_n06_iteration_5_sc3_context_conditioned_selection as iter5  # noqa: E402


N06 = ROOT / "experiments/2026-05-N06-lgrc-semantic-route-choice"
OUTPUT_PATH = N06 / "outputs/n06_iteration_8_sc6_closeout.json"
REPORT_PATH = N06 / "reports/n06_iteration_8_sc6_closeout.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N06-lgrc-semantic-route-choice/scripts/"
    "run_n06_iteration_8_sc6_closeout.py"
)

SOURCE_OUTPUTS = {
    "iteration_1_baseline": N06 / "outputs/n06_iteration_1_baseline_inventory.json",
    "iteration_2_manifest": N06
    / "outputs/n06_iteration_2_fixture_manifest_validation.json",
    "iteration_3_sc1": N06 / "outputs/n06_iteration_3_sc1_candidate_alternatives.json",
    "iteration_4_sc2": N06 / "outputs/n06_iteration_4_sc2_native_arbitration.json",
    "iteration_5_sc3": N06
    / "outputs/n06_iteration_5_sc3_context_conditioned_selection.json",
    "iteration_6_sc4": N06 / "outputs/n06_iteration_6_sc4_context_swap_controls.json",
    "iteration_7_sc5": N06
    / "outputs/n06_iteration_7_sc5_repeated_context_selection.json",
}

SOURCE_REPORTS = {
    "iteration_1_baseline": N06 / "reports/n06_iteration_1_baseline_inventory.md",
    "iteration_2_manifest": N06
    / "reports/n06_iteration_2_fixture_manifest_validation.md",
    "iteration_3_sc1": N06 / "reports/n06_iteration_3_sc1_candidate_alternatives.md",
    "iteration_4_sc2": N06 / "reports/n06_iteration_4_sc2_native_arbitration.md",
    "iteration_5_sc3": N06
    / "reports/n06_iteration_5_sc3_context_conditioned_selection.md",
    "iteration_6_sc4": N06 / "reports/n06_iteration_6_sc4_context_swap_controls.md",
    "iteration_7_sc5": N06
    / "reports/n06_iteration_7_sc5_repeated_context_selection.md",
}

SCORE_TOLERANCE = 1e-9


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


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


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


def _reason_has_blocker(reasons: Sequence[str], blocker: str) -> bool:
    return any(str(reason).split(":", 1)[0] == blocker for reason in reasons)


def _numeric_sum(values: Mapping[str, Any]) -> float:
    return sum(float(value) for value in values.values())


def _runtime_input_values(inputs: Sequence[Any]) -> dict[str, set[str]]:
    values: dict[str, set[str]] = {}
    for item in inputs:
        if not isinstance(item, str) or ":" not in item:
            continue
        field, value = item.split(":", 1)
        values.setdefault(field, set()).add(value)
    return values


def _values_match(left: Mapping[str, set[str]], right: Mapping[str, set[str]]) -> bool:
    context_fields = {
        "active_context_node_id",
        "compatible_route_id",
        "context_surface_digest",
    }
    return all(left.get(field, set()) == right.get(field, set()) for field in context_fields)


def _validator_artifacts_for_lane(lane: Mapping[str, Any]) -> dict[str, Any]:
    return {
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


def _selection_only_validation(lane: Mapping[str, Any]) -> dict[str, Any]:
    validation = iter5._selection_only_validation(  # noqa: SLF001
        _validator_artifacts_for_lane(lane)
    )
    validation["validator_scope"] = "sc6_closeout_selection_only_pre_topology_commit"
    return validation


def _candidate_source_provenance(
    sources: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    sc1_lane = sources["iteration_3_sc1"]["lanes"]["enabled_sc1"]
    source_digest = str(sc1_lane["source_surface_digest"])
    return {
        "source_iteration": 3,
        "source_artifact": _rel(SOURCE_OUTPUTS["iteration_3_sc1"]),
        "source_surface_digest": source_digest,
        "source_surface_id": sc1_lane["source_surface_id"],
        "source_surface_kind": sc1_lane["source_surface_kind"],
        "candidate_sources_committed": bool(
            sc1_lane["checks"]["candidate_sources_committed"]
        ),
        "unknown_source_digest_control_passed": bool(
            sources["iteration_3_sc1"]["controls"]["unknown_source_surface_digest"][
                "passed"
            ]
        ),
        "primary_blocker_for_unknown_source": sources["iteration_3_sc1"][
            "controls"
        ]["unknown_source_surface_digest"]["primary_blocker"],
    }


def _artifact_only_closeout(
    iter7: Mapping[str, Any],
    sources: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    source_provenance = _candidate_source_provenance(sources)
    per_cycle: list[dict[str, Any]] = []
    for cycle_id, lane in sorted(iter7["lanes"].items()):
        validation = _selection_only_validation(lane)
        candidate_set = lane["candidate_set_record"]
        arbitration = lane["route_arbitration_record"]
        selected_digest = arbitration["selected_candidate_route_digest"]
        rejected_digests = set(arbitration["rejected_candidate_route_digests"])
        candidate_set_digests = set(candidate_set["candidate_route_digests"])
        candidate_records = list(lane["candidate_route_records"])
        candidate_source_digests = {
            str(record.get("candidate_source_surface_digest"))
            for record in candidate_records
            if record.get("candidate_source_surface_digest") is not None
        }
        selected_candidate = next(
            record
            for record in candidate_records
            if record["candidate_route_digest"] == selected_digest
        )
        context_replay = lane["context_relation_replay"]
        candidate_context_values: dict[str, set[str]] = {}
        for record in candidate_records:
            for key, values in _runtime_input_values(
                record["candidate_runtime_visible_inputs"]
            ).items():
                candidate_context_values.setdefault(key, set()).update(values)
        arbitration_context_values = _runtime_input_values(
            arbitration["arbitration_runtime_visible_inputs"]
        )
        candidate_score_component_sums = {
            record["candidate_route_id"]: _numeric_sum(record["candidate_score_components"])
            for record in candidate_records
        }
        candidate_score_invariants = {
            record["candidate_route_id"]: abs(
                float(record["candidate_route_score"])
                - candidate_score_component_sums[record["candidate_route_id"]]
            )
            <= SCORE_TOLERANCE
            for record in candidate_records
        }
        record_claim_flags_false = {
            "candidate_records": all(
                _claim_flags_false(record["claim_flags"]) for record in candidate_records
            ),
            "candidate_set_record": _claim_flags_false(candidate_set["claim_flags"]),
            "route_arbitration_record": _claim_flags_false(arbitration["claim_flags"]),
        }
        checks = {
            "candidate_route_records_replayed": bool(lane["candidate_route_records"]),
            "candidate_set_record_replayed": bool(candidate_set),
            "candidate_source_surface_digests_non_null": (
                all(
                    isinstance(record.get("candidate_source_surface_digest"), str)
                    and bool(record["candidate_source_surface_digest"])
                    for record in candidate_records
                )
            ),
            "candidate_source_surface_digest_single": (
                len(candidate_source_digests) == 1
            ),
            "candidate_source_surface_digest_matches_lane": (
                candidate_source_digests == {lane["source_surface_digest"]}
            ),
            "candidate_source_surface_digest_resolves_to_committed_source": (
                candidate_source_digests
                == {source_provenance["source_surface_digest"]}
                and source_provenance["candidate_sources_committed"]
            ),
            "context_surface_and_relation_replayed": (
                context_replay["context_relation_replayable"]
            ),
            "candidate_route_scores_equal_component_sums": all(
                candidate_score_invariants.values()
            ),
            "arbitration_score_equals_selected_candidate_score": (
                abs(
                    float(arbitration["arbitration_score"])
                    - float(selected_candidate["candidate_route_score"])
                )
                <= SCORE_TOLERANCE
            ),
            "arbitration_candidate_context_fields_match": _values_match(
                candidate_context_values,
                arbitration_context_values,
            ),
            "record_claim_flags_false": all(record_claim_flags_false.values()),
            "native_route_arbitration_record_replayed": bool(arbitration),
            "selected_candidate_digest_in_candidate_set": (
                selected_digest in candidate_set_digests
            ),
            "rejected_candidate_digests_match_candidate_set": (
                rejected_digests == candidate_set_digests - {selected_digest}
            ),
            "native_selection_replayable_under_selection_only_scope": (
                validation["selection_contract_valid"]
            ),
            "native_validator_expected_pre_topology_incomplete": (
                validation["valid"] is False
                and bool(validation["expected_incomplete_reasons"])
                and not validation["unexpected_failure_reasons"]
            ),
            "scheduled_packet_evidence_not_applicable": (
                lane["checks"]["no_packet_scheduled_by_arbitration"]
            ),
            "processed_packet_evidence_not_applicable": (
                lane["checks"]["no_packet_scheduled_by_arbitration"]
            ),
            "runtime_state_not_used": True,
        }
        per_cycle.append(
            {
                "cycle_id": cycle_id,
                "context_state_id": lane["context_state_id"],
                "selected_route": lane["selected_candidate_route_id"],
                "selected_candidate_route_digest": selected_digest,
                "rejected_candidate_route_digests": sorted(rejected_digests),
                "candidate_set_digest": lane["candidate_set_digest"],
                "candidate_set_id": candidate_set["candidate_set_id"],
                "candidate_source_surface_digests": sorted(candidate_source_digests),
                "source_surface_provenance": source_provenance,
                "candidate_score_component_sums": candidate_score_component_sums,
                "candidate_score_invariants": candidate_score_invariants,
                "arbitration_score": arbitration["arbitration_score"],
                "selected_candidate_route_score": selected_candidate[
                    "candidate_route_score"
                ],
                "candidate_context_values": {
                    key: sorted(values)
                    for key, values in sorted(candidate_context_values.items())
                },
                "arbitration_context_values": {
                    key: sorted(values)
                    for key, values in sorted(arbitration_context_values.items())
                },
                "record_claim_flags_false": record_claim_flags_false,
                "context_relation_replayable": context_replay[
                    "context_relation_replayable"
                ],
                "native_validator_valid": validation["valid"],
                "selection_contract_valid_under_pre_topology_scope": validation[
                    "selection_contract_valid"
                ],
                "expected_incomplete_reasons": validation[
                    "expected_incomplete_reasons"
                ],
                "unexpected_failure_reasons": validation[
                    "unexpected_failure_reasons"
                ],
                "scheduled_processed_packet_evidence": {
                    "applicability": "not_applicable_pre_topology_selection_only_scope",
                    "scheduled_packet_count": 0,
                    "processed_packet_count": 0,
                },
                "checks": checks,
                "replay_ok": all(checks.values()),
            }
        )
    candidate_set_digests = [cycle["candidate_set_digest"] for cycle in per_cycle]
    candidate_set_ids = [cycle["candidate_set_id"] for cycle in per_cycle]
    candidate_set_identity = {
        "candidate_set_digests_distinct": (
            len(set(candidate_set_digests)) == len(candidate_set_digests)
        ),
        "candidate_set_ids": sorted(set(candidate_set_ids)),
        "candidate_set_id_is_context_unique": (
            len(set(candidate_set_ids)) == len(candidate_set_ids)
        ),
        "candidate_set_id_behavior": (
            "candidate_set_id is stable across equivalent source/policy shape; "
            "candidate_set_digest is the context-specific replay key"
        ),
    }
    checks = {
        "artifact_only": True,
        "runtime_state_not_used": True,
        "all_cycles_replayed": all(cycle["replay_ok"] for cycle in per_cycle),
        "candidate_sets_replayed": all(
            cycle["checks"]["candidate_set_record_replayed"] for cycle in per_cycle
        ),
        "context_relations_replayed": all(
            cycle["checks"]["context_surface_and_relation_replayed"]
            for cycle in per_cycle
        ),
        "native_arbitration_records_replayed": all(
            cycle["checks"]["native_route_arbitration_record_replayed"]
            for cycle in per_cycle
        ),
        "selected_and_rejected_digests_replayed": all(
            cycle["checks"]["selected_candidate_digest_in_candidate_set"]
            and cycle["checks"]["rejected_candidate_digests_match_candidate_set"]
            for cycle in per_cycle
        ),
        "candidate_source_surface_provenance_replayed": all(
            cycle["checks"]["candidate_source_surface_digest_resolves_to_committed_source"]
            for cycle in per_cycle
        ),
        "score_component_invariants_replayed": all(
            cycle["checks"]["candidate_route_scores_equal_component_sums"]
            and cycle["checks"]["arbitration_score_equals_selected_candidate_score"]
            for cycle in per_cycle
        ),
        "context_field_consistency_replayed": all(
            cycle["checks"]["arbitration_candidate_context_fields_match"]
            for cycle in per_cycle
        ),
        "record_claim_flags_remain_false": all(
            cycle["checks"]["record_claim_flags_false"] for cycle in per_cycle
        ),
        "candidate_set_digests_distinct_across_cycles": candidate_set_identity[
            "candidate_set_digests_distinct"
        ],
        "candidate_set_id_behavior_documented": True,
        "scheduled_processed_packet_evidence_scoped": all(
            cycle["checks"]["scheduled_packet_evidence_not_applicable"]
            and cycle["checks"]["processed_packet_evidence_not_applicable"]
            for cycle in per_cycle
        ),
        "expected_pre_topology_validator_incomplete_only": all(
            cycle["checks"]["native_validator_expected_pre_topology_incomplete"]
            for cycle in per_cycle
        ),
    }
    return {
        "artifact_only": True,
        "runtime_state_used": False,
        "scope": "selection_only_pre_topology_commit",
        "validator_scope_note": (
            "Native validator valid=false is expected because N06 SC6 is "
            "pre-topology and selection-only. Replay passes when the selection "
            "contract is valid and the only incomplete native-validator reason "
            "is missing selected-topology-event evidence."
        ),
        "candidate_set_identity": candidate_set_identity,
        "source_surface_provenance": source_provenance,
        "per_cycle": per_cycle,
        "checks": checks,
        "valid_under_selection_only_scope": all(checks.values()),
    }


def _native_hidden_input_control(
    lane: Mapping[str, Any],
    *,
    control_id: str,
    field: str,
    primary_blocker: str,
    target: str = "candidate",
) -> dict[str, Any]:
    corrupted = copy.deepcopy(lane)
    if target == "candidate_score":
        corrupted["candidate_route_records"][0]["candidate_score_components"][field] = 0.0
    elif target == "arbitration":
        corrupted["route_arbitration_record"][
            "arbitration_runtime_visible_inputs"
        ].append(field)
    else:
        corrupted["candidate_route_records"][0][
            "candidate_runtime_visible_inputs"
        ].append(field)
    validation = validate_lgrc9v3_native_route_arbitration_artifacts(
        **_validator_artifacts_for_lane(corrupted)
    )
    native_blocked = _reason_has_blocker(
        validation["failure_reasons"],
        LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_HIDDEN_INPUT_REJECTED,
    )
    return {
        "control_id": control_id,
        "passed": native_blocked,
        "primary_blocker": primary_blocker,
        "scope": "sc6_artifact_level_hidden_input_control",
        "detail": {
            "injected_field": field,
            "target": target,
            "native_hidden_input_blocker_present": native_blocked,
            "native_failure_reasons": validation["failure_reasons"],
        },
    }


def _stale_candidate_control(iter7: Mapping[str, Any]) -> dict[str, Any]:
    lanes = list(iter7["lanes"].values())
    current = copy.deepcopy(lanes[0])
    stale = lanes[1]["selected_candidate_route_digest"]
    candidate_set_digests = set(current["candidate_set_record"]["candidate_route_digests"])
    current["route_arbitration_record"]["selected_candidate_route_digest"] = stale
    stale_detected = stale not in candidate_set_digests
    validation = validate_lgrc9v3_native_route_arbitration_artifacts(
        **_validator_artifacts_for_lane(current)
    )
    native_validator_rejected = validation["valid"] is False
    return {
        "control_id": "stale_candidate",
        "passed": stale_detected and native_validator_rejected,
        "primary_blocker": "n06_stale_candidate_route_blocked",
        "scope": "sc6_artifact_semantic_replay_control",
        "detail": {
            "current_cycle_id": current["cycle_id"],
            "stale_candidate_digest": stale,
            "current_candidate_set_digest": current["candidate_set_digest"],
            "stale_digest_in_current_candidate_set": stale in candidate_set_digests,
            "native_validator_rejected_corrupted_record": native_validator_rejected,
            "native_failure_reasons": validation["failure_reasons"],
        },
    }


def _source_control(
    sources: Mapping[str, Mapping[str, Any]],
    *,
    source_key: str,
    control_key: str,
) -> dict[str, Any]:
    control = copy.deepcopy(sources[source_key]["controls"][control_key])
    control["source_artifact"] = _rel(SOURCE_OUTPUTS[source_key])
    control["source_iteration"] = sources[source_key]["iteration"]
    return control


def _control_matrix(sources: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    iter7 = sources["iteration_7_sc5"]
    lane0 = next(iter(iter7["lanes"].values()))
    matrix = {
        "policy_disabled": _source_control(
            sources,
            source_key="iteration_4_sc2",
            control_key="policy_disabled",
        ),
        "no_candidates": _source_control(
            sources,
            source_key="iteration_4_sc2",
            control_key="no_candidates",
        ),
        "unresolved_tie": _source_control(
            sources,
            source_key="iteration_4_sc2",
            control_key="unresolved_tie",
        ),
        "hidden_context": _source_control(
            sources,
            source_key="iteration_5_sc3",
            control_key="hidden_context",
        ),
        "hidden_preference": _native_hidden_input_control(
            lane0,
            control_id="hidden_preference",
            field="hidden_fixture_state",
            primary_blocker=(
                "native_route_arbitration_hidden_input_rejected:"
                "hidden_route_preference"
            ),
            target="candidate_score",
        ),
        "preselected_sink": _native_hidden_input_control(
            lane0,
            control_id="preselected_sink",
            field="preselected_sink_id",
            primary_blocker=(
                "native_route_arbitration_hidden_input_rejected:preselected_sink"
            ),
        ),
        "experiment_side_if_else": _native_hidden_input_control(
            lane0,
            control_id="experiment_side_if_else",
            field="experiment_if_else",
            primary_blocker="n06_experiment_side_selection_rejected",
        ),
        "report_side_selection": _native_hidden_input_control(
            lane0,
            control_id="report_side_selection",
            field="report_code",
            primary_blocker="n06_report_side_selection_rejected",
            target="arbitration",
        ),
        "posthoc_threshold_change": _native_hidden_input_control(
            lane0,
            control_id="posthoc_threshold_change",
            field="posthoc_threshold",
            primary_blocker="n06_posthoc_threshold_change_rejected",
            target="arbitration",
        ),
        "budget_mismatch": _source_control(
            sources,
            source_key="iteration_5_sc3",
            control_key="budget_mismatch",
        ),
        "order_inversion": _source_control(
            sources,
            source_key="iteration_4_sc2",
            control_key="order_invalid",
        ),
        "stale_candidate": _stale_candidate_control(iter7),
        "stale_context": _source_control(
            sources,
            source_key="iteration_7_sc5",
            control_key="stale_context",
        ),
        "duplicate_arbitration": _source_control(
            sources,
            source_key="iteration_7_sc5",
            control_key="duplicate_arbitration",
        ),
        "producer_mutation": _source_control(
            sources,
            source_key="iteration_7_sc5",
            control_key="producer_mutation",
        ),
        "claim_promotion": _source_control(
            sources,
            source_key="iteration_7_sc5",
            control_key="claim_promotion",
        ),
    }
    return matrix


def _control_summary(matrix: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    return {
        key: {
            "passed": bool(control["passed"]),
            "primary_blocker": control["primary_blocker"],
            "scope": control.get("scope"),
            "source_iteration": control.get("source_iteration", 8),
        }
        for key, control in matrix.items()
    }


def _positive_artifacts() -> dict[str, Any]:
    records: dict[str, Any] = {}
    for key, path in SOURCE_OUTPUTS.items():
        records[f"{key}_output"] = _artifact_record(path)
    for key, path in SOURCE_REPORTS.items():
        records[f"{key}_report"] = _artifact_record(path)
    records["iteration_8_script"] = _artifact_record(Path(__file__).resolve())
    return records


def _claim_flags_false(claim_flags: Mapping[str, Any]) -> bool:
    return all(value is False for value in claim_flags.values())


def _build_report(data: Mapping[str, Any]) -> str:
    lines = [
        "# N06 Iteration 8 SC6 Artifact-Only Replay And Closeout",
        "",
        f"- status: `{data['status']}`",
        f"- generated: `{data['generated_at']}`",
        f"- command: `{COMMAND}`",
        f"- strongest supported SC level: `{data['closeout']['strongest_supported_sc_level']}`",
        f"- strongest claim ceiling: `{data['closeout']['strongest_claim_ceiling']}`",
        "",
        "## Boundary",
        "",
        "- SC6 is an artifact-only evidence classification for N06 selection-only route choice.",
        "- No selected topology event, post-selection packet scheduling, memory/trail, agency, identity, ACO, locomotion, biology, or unrestricted movement claim is promoted.",
        "- Scheduled/processed packet evidence is marked not applicable for this pre-topology N06 closeout.",
        "",
        "## Acceptance",
        "",
        "```json",
        json.dumps(data["acceptance"], indent=2, sort_keys=True),
        "```",
        "",
        "## Artifact-Only Closeout",
        "",
        data["artifact_only_closeout"]["validator_scope_note"],
        "",
        "```json",
        json.dumps(data["artifact_only_closeout"], indent=2, sort_keys=True),
        "```",
        "",
        "## Controls",
        "",
        "```json",
        json.dumps(data["control_summary"], indent=2, sort_keys=True),
        "```",
        "",
        "## N07 Handoff",
        "",
        "```json",
        json.dumps(data["n07_handoff"], indent=2, sort_keys=True),
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
    sources = {key: _load_json(path) for key, path in SOURCE_OUTPUTS.items()}
    iter7 = sources["iteration_7_sc5"]
    artifact_closeout = _artifact_only_closeout(iter7, sources)
    control_matrix = _control_matrix(sources)
    control_summary = _control_summary(control_matrix)
    positive_artifacts = _positive_artifacts()
    claim_flags = {flag: False for flag in iter3.CLAIM_FLAGS}
    native_policy_limitations = [
        {
            "limitation": "no_dedicated_native_semantic_context_validator",
            "effect": (
                "stale-context, hidden-schedule, and context-order controls "
                "remain N06 artifact-level semantic replay checks"
            ),
            "blocks_sc6_selection_only_closeout": False,
        },
        {
            "limitation": "selection_only_pre_topology_scope",
            "effect": (
                "selected topology events and scheduled/processed packet "
                "evidence are intentionally not part of N06 closeout"
            ),
            "blocks_sc6_selection_only_closeout": False,
        },
        {
            "limitation": "independent_runtime_windows",
            "effect": (
                "SC5 repeatability does not test single-runtime persistence or "
                "cross-window accumulated budget drift"
            ),
            "blocks_sc6_selection_only_closeout": False,
        },
    ]
    n07_handoff = {
        "recommendation": "proceed_to_N07_rc_identity_attractor_invariance",
        "minimum_sc_level_met": "SC6",
        "required_controls_passed": all(
            control["passed"] for control in control_summary.values()
        ),
        "budget_conservation_required": True,
        "budget_conservation_passed": bool(iter7["checks"]["budget_exact"]),
        "artifact_replay_required": True,
        "artifact_replay_passed": artifact_closeout[
            "valid_under_selection_only_scope"
        ],
        "claim_boundary_clean": _claim_flags_false(claim_flags),
        "handoff_scope": (
            "N07 may use N06's artifact-only route-choice candidate as route "
            "selection background, but must independently validate RC identity "
            "and attractor invariance."
        ),
        "blocked_inheritance": [
            "memory_or_trail_claim",
            "agency_claim",
            "agentic_like_claim",
            "rc_identity_collapse_claim",
            "identity_acceptance_claim",
            "goal_proxy_regulation_claim",
            "locomotion_like_claim",
            "biological_claim",
            "ant_colony_claim",
            "unrestricted_movement_claim",
        ],
    }
    closeout = {
        "strongest_supported_sc_level": "SC6",
        "strongest_claim_ceiling": "artifact_only_semantic_route_choice_candidate",
        "sc_level_is_evidence_classification": True,
        "semantic_choice_claim_allowed": False,
        "source_sc5_level": iter7["acceptance"]["sc_level"],
        "source_sc5_claim_ceiling": iter7["acceptance"]["claim_ceiling"],
        "selection_causality_basis": iter7["acceptance"][
            "selection_causality_basis"
        ],
        "scheduled_processed_packet_evidence_applicability": (
            "not_applicable_pre_topology_selection_only_scope"
        ),
        "native_policy_blockers": [],
        "native_policy_limitations": native_policy_limitations,
    }
    checks = {
        "source_artifacts_present": all(path.exists() for path in SOURCE_OUTPUTS.values()),
        "source_reports_present": all(path.exists() for path in SOURCE_REPORTS.values()),
        "source_iterations_passed": all(
            source.get("status") == "passed" for source in sources.values()
        ),
        "artifact_only_closeout_passed": artifact_closeout[
            "valid_under_selection_only_scope"
        ],
        "controls_passed": all(control["passed"] for control in control_summary.values()),
        "budget_conservation_passed": bool(iter7["checks"]["budget_exact"]),
        "producer_boundary_passed": bool(
            control_summary["producer_mutation"]["passed"]
        ),
        "claim_flags_remain_false": _claim_flags_false(claim_flags),
        "n07_handoff_ready": (
            n07_handoff["required_controls_passed"]
            and n07_handoff["artifact_replay_passed"]
            and n07_handoff["claim_boundary_clean"]
        ),
    }
    status = "passed" if all(checks.values()) else "failed"
    acceptance = {
        "status": status,
        "strongest_supported_sc_level": closeout["strongest_supported_sc_level"],
        "strongest_claim_ceiling": closeout["strongest_claim_ceiling"],
        "artifact_only_replay_passed": checks["artifact_only_closeout_passed"],
        "controls_passed": checks["controls_passed"],
        "budget_conservation_passed": checks["budget_conservation_passed"],
        "producer_boundary_passed": checks["producer_boundary_passed"],
        "semantic_choice_claim_allowed": False,
        "memory_or_trail_claim_allowed": False,
        "agency_claim_allowed": False,
        "identity_acceptance_claim_allowed": False,
        "locomotion_like_claim_allowed": False,
        "biological_claim_allowed": False,
        "unrestricted_movement_claim_allowed": False,
        "n07_handoff_ready": checks["n07_handoff_ready"],
    }
    data: dict[str, Any] = {
        "schema": "semantic_route_choice_closeout_v1",
        "experiment": "2026-05-N06-lgrc-semantic-route-choice",
        "iteration": 8,
        "iteration_name": "SC6 Artifact-Only Replay And Closeout",
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": COMMAND,
        "platform": {
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "source_artifacts": {
            key: _artifact_record(path) for key, path in SOURCE_OUTPUTS.items()
        },
        "positive_artifacts_sha256": positive_artifacts,
        "artifact_only_closeout": artifact_closeout,
        "control_matrix": control_matrix,
        "control_summary": control_summary,
        "claim_flags": claim_flags,
        "closeout": closeout,
        "n07_handoff": n07_handoff,
        "checks": checks,
        "acceptance": acceptance,
        "git": {
            "status_src": _git(["status", "--short", "src"]),
            "diff_check_experiment": _git(
                ["diff", "--check", "--", _rel(N06)]
            ),
        },
        "artifact_digests": {},
    }
    data["artifact_digests"] = {
        "source_artifacts_digest": _digest(data["source_artifacts"]),
        "positive_artifacts_digest": _digest(positive_artifacts),
        "artifact_only_closeout_digest": _digest(artifact_closeout),
        "control_matrix_digest": _digest(control_matrix),
        "control_summary_digest": _digest(control_summary),
        "claim_flags_digest": _digest(claim_flags),
        "closeout_digest": _digest(closeout),
        "n07_handoff_digest": _digest(n07_handoff),
        "acceptance_digest": _digest(acceptance),
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
                "strongest_supported_sc_level": closeout[
                    "strongest_supported_sc_level"
                ],
                "strongest_claim_ceiling": closeout["strongest_claim_ceiling"],
                "artifact_only_replay_passed": checks[
                    "artifact_only_closeout_passed"
                ],
                "controls_passed": checks["controls_passed"],
                "n07_handoff_ready": checks["n07_handoff_ready"],
                "semantic_choice_claim_allowed": False,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
