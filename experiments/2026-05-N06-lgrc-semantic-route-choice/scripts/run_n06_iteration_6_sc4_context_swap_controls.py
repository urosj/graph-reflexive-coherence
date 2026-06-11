#!/usr/bin/env python3
"""Run N06 Iteration 6: SC4 context-swap controls.

This probe reruns the matched context A/B lanes from SC3 as an explicit swap
control. It verifies the same fixture, serialized policy, thresholds, ordering
rule, and replay validator are used, and that route selection swaps only with
serialized runtime-visible context evidence. It does not commit topology,
schedule packets, or promote semantic-choice claims.
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
import run_n06_iteration_5_sc3_context_conditioned_selection as iter5  # noqa: E402


N06 = ROOT / "experiments/2026-05-N06-lgrc-semantic-route-choice"
MANIFEST_PATH = N06 / "configs/n06_fixture_manifest_v1.json"
OUTPUT_PATH = N06 / "outputs/n06_iteration_6_sc4_context_swap_controls.json"
REPORT_PATH = N06 / "reports/n06_iteration_6_sc4_context_swap_controls.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N06-lgrc-semantic-route-choice/scripts/"
    "run_n06_iteration_6_sc4_context_swap_controls.py"
)

DIRECTION_LABEL_PREFIXES = (
    "direction_label",
    "polarity_label",
    "hidden_direction_label",
    "hidden_polarity_label",
)


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


def _control_result(
    control_id: str,
    *,
    passed: bool,
    primary_blocker: str,
    detail: Any = None,
    scope: str = "n06_sc4_validator",
) -> dict[str, Any]:
    return {
        "control_id": control_id,
        "scope": scope,
        "passed": bool(passed),
        "primary_blocker": primary_blocker,
        "detail": detail,
    }


def _route_id_for_digest(
    lane: Mapping[str, Any],
    digest: str,
) -> str:
    for record in lane["candidate_route_records"]:
        if str(record["candidate_route_digest"]) == digest:
            return str(record["candidate_route_id"])
    raise KeyError(digest)


def _sc4_lane(lane: Mapping[str, Any]) -> dict[str, Any]:
    adapted = copy.deepcopy(lane)
    adapted["lane_id"] = str(adapted["lane_id"]).replace("sc3_", "sc4_", 1)
    adapted["selection_only_artifact_validation"]["validator_scope"] = (
        "sc4_context_swap_pre_topology_commit"
    )
    return adapted


def _rejected_route_ids(lane: Mapping[str, Any]) -> list[str]:
    return [
        _route_id_for_digest(lane, str(digest))
        for digest in lane["rejected_candidate_route_digests"]
    ]


def _runtime_inputs_for_lane(lane: Mapping[str, Any]) -> list[str]:
    values: list[str] = []
    for record in lane["candidate_route_records"]:
        values.extend(str(value) for value in record["candidate_runtime_visible_inputs"])
    values.extend(
        str(value)
        for value in lane["route_arbitration_record"][
            "arbitration_runtime_visible_inputs"
        ]
    )
    return sorted(values)


def _direction_or_polarity_labels(lane: Mapping[str, Any]) -> list[str]:
    labels: list[str] = []
    for value in _runtime_inputs_for_lane(lane):
        field_name = value.split(":", 1)[0]
        if field_name in DIRECTION_LABEL_PREFIXES:
            labels.append(value)
    return sorted(set(labels))


def _forbidden_runtime_inputs(lane: Mapping[str, Any]) -> list[str]:
    forbidden_fields = set(iter5.HIDDEN_INPUTS) | set(DIRECTION_LABEL_PREFIXES)
    labels: list[str] = []
    for value in _runtime_inputs_for_lane(lane):
        field_name = value.split(":", 1)[0]
        if field_name in forbidden_fields:
            labels.append(value)
    return sorted(set(labels))


def _candidate_budget_errors(lane: Mapping[str, Any]) -> list[float]:
    return [
        abs(
            float(
                record["candidate_budget_prediction"][
                    "node_plus_packet_budget_error"
                ]
            )
        )
        for record in lane["candidate_route_records"]
    ]


def _matched_settings(
    manifest: Mapping[str, Any],
    context_a: Mapping[str, Any],
    context_b: Mapping[str, Any],
) -> dict[str, Any]:
    a_set = context_a["candidate_set_record"]
    b_set = context_b["candidate_set_record"]
    a_record = context_a["route_arbitration_record"]
    b_record = context_b["route_arbitration_record"]
    budget_tolerance = float(manifest["arbitration_policy"]["budget_tolerance"])
    score_tolerance = float(manifest["arbitration_policy"]["score_tolerance"])
    a_score_tolerance = float(context_a["context_relation_replay"]["score_tolerance"])
    b_score_tolerance = float(context_b["context_relation_replay"]["score_tolerance"])
    a_budget_errors = _candidate_budget_errors(context_a)
    b_budget_errors = _candidate_budget_errors(context_b)
    checks = {
        "same_fixture_id": bool(manifest["fixture"]["fixture_id"]),
        "same_policy_id": (
            a_record["native_route_arbitration_policy_id"]
            == b_record["native_route_arbitration_policy_id"]
        ),
        "same_arbitration_rule": (
            a_record["arbitration_rule"] == b_record["arbitration_rule"]
        ),
        "same_candidate_set_order_key": (
            a_set["candidate_set_order_key"] == b_set["candidate_set_order_key"]
        ),
        "same_unresolved_tie_policy": (
            a_set["unresolved_tie_policy"] == b_set["unresolved_tie_policy"]
        ),
        "same_budget_tolerance": (
            max(a_budget_errors + b_budget_errors) <= budget_tolerance
            and context_a["checks"]["budget_exact"]
            and context_b["checks"]["budget_exact"]
        ),
        "same_score_tolerance": (
            a_score_tolerance == b_score_tolerance == score_tolerance
        ),
        "same_validator_scope": (
            context_a["selection_only_artifact_validation"]["validator_scope"]
            == context_b["selection_only_artifact_validation"]["validator_scope"]
        ),
        "same_source_surface_digest": (
            context_a["source_surface_digest"] == context_b["source_surface_digest"]
        ),
    }
    return {
        "fixture_id": manifest["fixture"]["fixture_id"],
        "policy_id": a_record["native_route_arbitration_policy_id"],
        "arbitration_rule": a_record["arbitration_rule"],
        "candidate_set_order_key": a_set["candidate_set_order_key"],
        "unresolved_tie_policy": a_set["unresolved_tie_policy"],
        "budget_tolerance": budget_tolerance,
        "score_tolerance": score_tolerance,
        "context_a_budget_errors": a_budget_errors,
        "context_b_budget_errors": b_budget_errors,
        "context_a_score_tolerance": a_score_tolerance,
        "context_b_score_tolerance": b_score_tolerance,
        "validator_scope": context_a["selection_only_artifact_validation"][
            "validator_scope"
        ],
        "checks": checks,
        "matched": all(checks.values()),
    }


def _swap_replay(
    context_a: Mapping[str, Any],
    context_b: Mapping[str, Any],
) -> dict[str, Any]:
    checks = {
        "context_a_selected_route_a": (
            context_a["selected_candidate_route_id"] == "route_a"
        ),
        "context_b_selected_route_b": (
            context_b["selected_candidate_route_id"] == "route_b"
        ),
        "selection_swapped": (
            context_a["selected_candidate_route_id"]
            != context_b["selected_candidate_route_id"]
        ),
        "context_a_rejected_route_b": _rejected_route_ids(context_a) == ["route_b"],
        "context_b_rejected_route_a": _rejected_route_ids(context_b) == ["route_a"],
        "selected_candidate_digests_distinct": (
            context_a["selected_candidate_route_digest"]
            != context_b["selected_candidate_route_digest"]
        ),
        "candidate_set_digests_distinct": (
            context_a["candidate_set_digest"] != context_b["candidate_set_digest"]
        ),
        "context_a_relation_replayable": context_a["context_relation_replay"][
            "context_relation_replayable"
        ],
        "context_b_relation_replayable": context_b["context_relation_replay"][
            "context_relation_replayable"
        ],
        "no_direction_or_polarity_labels": (
            not _direction_or_polarity_labels(context_a)
            and not _direction_or_polarity_labels(context_b)
        ),
        "no_forbidden_runtime_inputs": (
            not _forbidden_runtime_inputs(context_a)
            and not _forbidden_runtime_inputs(context_b)
        ),
    }
    return {
        "context_a_selected_route": context_a["selected_candidate_route_id"],
        "context_b_selected_route": context_b["selected_candidate_route_id"],
        "context_a_rejected_routes": _rejected_route_ids(context_a),
        "context_b_rejected_routes": _rejected_route_ids(context_b),
        "context_a_selected_candidate_digest": context_a[
            "selected_candidate_route_digest"
        ],
        "context_b_selected_candidate_digest": context_b[
            "selected_candidate_route_digest"
        ],
        "context_a_rejected_candidate_digests": context_a[
            "rejected_candidate_route_digests"
        ],
        "context_b_rejected_candidate_digests": context_b[
            "rejected_candidate_route_digests"
        ],
        "context_a_direction_labels": _direction_or_polarity_labels(context_a),
        "context_b_direction_labels": _direction_or_polarity_labels(context_b),
        "context_a_forbidden_runtime_inputs": _forbidden_runtime_inputs(context_a),
        "context_b_forbidden_runtime_inputs": _forbidden_runtime_inputs(context_b),
        "checks": checks,
        "swap_replayable": all(checks.values()),
    }


def _sc4_artifact_semantic_validator(lane: Mapping[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    if _forbidden_runtime_inputs(lane):
        reasons.append("n06_hidden_direction_label_rejected")
    validation = iter5._semantic_context_validator(lane)  # noqa: SLF001
    reasons.extend(str(reason) for reason in validation["failure_reasons"])
    return {
        "valid": not reasons,
        "failure_reasons": iter5._dedupe_reasons(reasons),  # noqa: SLF001
    }


def _wrong_polarity_or_context_control(
    manifest: Mapping[str, Any],
    swapped_lane: Mapping[str, Any],
) -> dict[str, Any]:
    artifacts = {"candidate_route_records": swapped_lane["candidate_route_records"]}
    replay = iter5._context_relation_replay(  # noqa: SLF001
        manifest,
        context_state_id="context_a",
        source_surface_digest=swapped_lane["source_surface_digest"],
        artifacts=artifacts,
        arbitration_record=swapped_lane["route_arbitration_record"],
    )
    lane = {
        "context_relation_replay": replay,
        "checks": {"budget_exact": swapped_lane["checks"]["budget_exact"]},
        "route_arbitration_record": swapped_lane["route_arbitration_record"],
        "candidate_set_record": swapped_lane["candidate_set_record"],
    }
    validation = iter5._semantic_context_validator(lane)  # noqa: SLF001
    expected_reasons = [
        "n06_stale_context_surface_blocked",
        "n06_context_relation_mismatch",
        "n06_context_evidence_not_replayable",
    ]
    expected_present = [
        reason
        for reason in expected_reasons
        if reason in validation["failure_reasons"]
    ]
    return _control_result(
        "wrong_polarity",
        passed=validation["valid"] is False
        and sorted(expected_present) == sorted(expected_reasons),
        primary_blocker="n06_wrong_context_or_polarity_blocked",
        detail={
            "wrong_expected_context_state_id": "context_a",
            "actual_lane_context_state_id": swapped_lane["context_state_id"],
            "expected_underlying_reasons": expected_reasons,
            "expected_underlying_reasons_present": expected_present,
            "semantic_validator": validation,
        },
    )


def _unswapped_context_control(
    manifest: Mapping[str, Any],
) -> dict[str, Any]:
    first = _sc4_lane(
        iter5._run_context_lane(manifest, context_state_id="context_a")  # noqa: SLF001
    )
    second = _sc4_lane(
        iter5._run_context_lane(manifest, context_state_id="context_a")  # noqa: SLF001
    )
    paired_swap = _sc4_lane(
        iter5._run_context_lane(manifest, context_state_id="context_b")  # noqa: SLF001
    )
    selection_swapped = (
        first["selected_candidate_route_id"] != second["selected_candidate_route_id"]
    )
    paired_context_changes_route = (
        paired_swap["selected_candidate_route_id"]
        != first["selected_candidate_route_id"]
    )
    checks = {
        "same_context_repeats_same_selection": (
            selection_swapped is False
            and first["selected_candidate_route_id"] == "route_a"
            and second["selected_candidate_route_id"] == "route_a"
        ),
        "paired_context_b_changes_selection": (
            paired_context_changes_route
            and paired_swap["selected_candidate_route_id"] == "route_b"
        ),
    }
    return _control_result(
        "unswapped_context",
        passed=all(checks.values()),
        primary_blocker="n06_unswapped_context_blocked",
        detail={
            "first_context": first["context_state_id"],
            "second_context": second["context_state_id"],
            "paired_swap_context": paired_swap["context_state_id"],
            "first_selected_route": first["selected_candidate_route_id"],
            "second_selected_route": second["selected_candidate_route_id"],
            "paired_swap_selected_route": paired_swap["selected_candidate_route_id"],
            "selection_swapped": selection_swapped,
            "paired_context_changes_route": paired_context_changes_route,
            "checks": checks,
        },
    )


def _hidden_direction_control(lane: Mapping[str, Any]) -> dict[str, Any]:
    corrupted = copy.deepcopy(lane)
    for record in corrupted["candidate_route_records"]:
        record["candidate_runtime_visible_inputs"].append("direction_label:route_a")
    corrupted["route_arbitration_record"]["arbitration_runtime_visible_inputs"].append(
        "direction_label:route_a"
    )
    labels = _direction_or_polarity_labels(corrupted)
    validation = _sc4_artifact_semantic_validator(corrupted)
    return _control_result(
        "hidden_direction",
        passed=bool(labels)
        and validation["valid"] is False
        and "n06_hidden_direction_label_rejected" in validation["failure_reasons"],
        primary_blocker="n06_hidden_direction_label_rejected",
        detail={
            "injected_direction_labels": labels,
            "positive_lane_direction_labels": _direction_or_polarity_labels(lane),
            "artifact_semantic_validator": validation,
        },
        scope="artifact_semantic_replay_control",
    )


def _run_controls(
    manifest: Mapping[str, Any],
    context_a: Mapping[str, Any],
    context_b: Mapping[str, Any],
) -> dict[str, Any]:
    budget = iter5._run_budget_mismatch_control(manifest)  # noqa: SLF001
    order = iter5._run_context_order_control(context_a)  # noqa: SLF001
    claim = iter5._run_claim_promotion_control(context_a)  # noqa: SLF001
    budget["control_id"] = "budget_mismatch"
    order["control_id"] = "order_inversion"
    claim["control_id"] = "claim_promotion"
    return {
        "wrong_polarity": _wrong_polarity_or_context_control(manifest, context_b),
        "unswapped_context": _unswapped_context_control(manifest),
        "hidden_direction": _hidden_direction_control(context_a),
        "budget_mismatch": budget,
        "order_inversion": order,
        "claim_promotion": claim,
    }


def _build_report(data: Mapping[str, Any]) -> str:
    swap = data["swap_replay"]
    lines = [
        "# N06 Iteration 6 SC4 Context-Swap Controls",
        "",
        f"- status: `{data['status']}`",
        f"- generated: `{data['generated_at']}`",
        f"- command: `{COMMAND}`",
        f"- context A selected: `{swap['context_a_selected_route']}`",
        f"- context B selected: `{swap['context_b_selected_route']}`",
        "",
        "## Boundary",
        "",
        "- SC4 confirms matched context-swap behavior using the same serialized native route-arbitration policy and validator.",
        "- The current fixture is context-swap scoped; no independent polarity surface is claimed.",
        "- No topology event is committed, no packet is scheduled, and no semantic-choice/agency/memory/identity/movement claim is promoted.",
        "",
        "## Acceptance",
        "",
        "```json",
        json.dumps(data["acceptance"], indent=2, sort_keys=True),
        "```",
        "",
        "## Matched Settings",
        "",
        "```json",
        json.dumps(data["matched_settings"], indent=2, sort_keys=True),
        "```",
        "",
        "## Swap Replay",
        "",
        "```json",
        json.dumps(data["swap_replay"], indent=2, sort_keys=True),
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
    context_a = _sc4_lane(
        iter5._run_context_lane(manifest, context_state_id="context_a")  # noqa: SLF001
    )
    context_b = _sc4_lane(
        iter5._run_context_lane(manifest, context_state_id="context_b")  # noqa: SLF001
    )
    matched_settings = _matched_settings(manifest, context_a, context_b)
    swap_replay = _swap_replay(context_a, context_b)
    controls = _run_controls(manifest, context_a, context_b)
    checks = {
        "context_a_lane_passed": context_a["passed"],
        "context_b_lane_passed": context_b["passed"],
        "matched_settings_passed": matched_settings["matched"],
        "swap_replayable": swap_replay["swap_replayable"],
        "controls_passed": all(control["passed"] for control in controls.values()),
        "budget_exact": context_a["checks"]["budget_exact"]
        and context_b["checks"]["budget_exact"],
        "no_direction_or_polarity_labels": swap_replay["checks"][
            "no_direction_or_polarity_labels"
        ],
        "no_forbidden_runtime_inputs": swap_replay["checks"][
            "no_forbidden_runtime_inputs"
        ],
        "selected_and_rejected_candidate_digests_recorded": bool(
            swap_replay["context_a_selected_candidate_digest"]
        )
        and bool(swap_replay["context_b_selected_candidate_digest"])
        and bool(swap_replay["context_a_rejected_candidate_digests"])
        and bool(swap_replay["context_b_rejected_candidate_digests"]),
        "no_topology_commit": context_a["checks"]["no_topology_event_committed"]
        and context_b["checks"]["no_topology_event_committed"],
        "claim_flags_remain_false": context_a["checks"]["claim_flags_remain_false"]
        and context_b["checks"]["claim_flags_remain_false"],
    }
    status = "passed" if all(checks.values()) else "failed"
    acceptance = {
        "sc_level": "SC4",
        "claim_ceiling": "context_swap_route_selection_candidate",
        "fixture_scope": "context_swap_only_no_independent_polarity_surface",
        "same_policy_thresholds_and_validator": matched_settings["matched"],
        "context_a_selected_route": context_a["selected_candidate_route_id"],
        "context_b_selected_route": context_b["selected_candidate_route_id"],
        "selection_swapped_by_serialized_context": swap_replay["checks"][
            "selection_swapped"
        ],
        "hidden_direction_labels_absent": checks[
            "no_direction_or_polarity_labels"
        ],
        "forbidden_runtime_inputs_absent": checks["no_forbidden_runtime_inputs"],
        "budget_exact": checks["budget_exact"],
        "semantic_choice_claim_allowed": False,
        "topology_event_committed": False,
        "packet_scheduled_by_arbitration": False,
        "status": status,
    }
    data: dict[str, Any] = {
        "schema": "semantic_route_choice_report_v1",
        "experiment": "2026-05-N06-lgrc-semantic-route-choice",
        "iteration": 6,
        "iteration_name": "SC4 Context-Swap Controls",
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": COMMAND,
        "platform": {
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "manifest": _artifact_record(MANIFEST_PATH),
        "source_iteration": _artifact_record(iter5.OUTPUT_PATH),
        "lanes": {
            "context_a": context_a,
            "context_b": context_b,
        },
        "matched_settings": matched_settings,
        "swap_replay": swap_replay,
        "controls": controls,
        "checks": checks,
        "acceptance": acceptance,
        "claim_flags": {flag: False for flag in iter3.CLAIM_FLAGS},
        "scope_notes": {
            "context_swap_scope": True,
            "independent_polarity_surface_tested": False,
            "reason": "The current N06 fixture serializes context A/B affordance, not a separate polarity surface.",
            "stale_context_and_order_controls": (
                "N06 artifact-level semantic replay controls until a future "
                "Phase 8 native semantic-context validator exists."
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
        "context_a_lane_digest": _digest(context_a),
        "context_b_lane_digest": _digest(context_b),
        "matched_settings_digest": _digest(matched_settings),
        "swap_replay_digest": _digest(swap_replay),
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
                "context_a_selected": context_a["selected_candidate_route_id"],
                "context_b_selected": context_b["selected_candidate_route_id"],
                "swap_replayable": swap_replay["swap_replayable"],
                "controls_passed": checks["controls_passed"],
                "semantic_choice_claim_allowed": False,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
