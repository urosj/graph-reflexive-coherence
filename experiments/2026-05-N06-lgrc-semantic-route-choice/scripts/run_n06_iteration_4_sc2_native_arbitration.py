#!/usr/bin/env python3
"""Run N06 Iteration 4: SC2 native arbitration selection.

This probe consumes a committed native route candidate set and emits exactly
one native route-arbitration record. It intentionally stops before committing
the selected topology event, scheduling post-selection packets, or promoting
semantic choice claims.
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
from typing import Any, Callable, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from pygrc.models import (  # noqa: E402
    LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_BUDGET_INVALID,
    LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_HIDDEN_INPUT_REJECTED,
    LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_NO_CANDIDATES,
    LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_ORDER_INVALID,
    LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_POLICY_DISABLED,
    LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_SELECTED_HIGHEST_SCORE,
    LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_UNRESOLVED_TIE,
    LGRC9V3_NATIVE_ROUTE_CANDIDATE_SET_ORDER_SCORE_DESC_THEN_CANDIDATE_ID,
    LGRC9V3_NATIVE_ROUTE_UNRESOLVED_TIE_POLICY_FAIL_CLOSED,
    LGRC9V3NativeRouteCandidateSetRecord,
    build_lgrc9v3_native_route_arbitration_idempotency_key,
    validate_lgrc9v3_native_route_arbitration_artifacts,
)

import run_n06_iteration_3_sc1_candidate_alternatives as iter3  # noqa: E402


N06 = ROOT / "experiments/2026-05-N06-lgrc-semantic-route-choice"
MANIFEST_PATH = N06 / "configs/n06_fixture_manifest_v1.json"
OUTPUT_PATH = N06 / "outputs/n06_iteration_4_sc2_native_arbitration.json"
REPORT_PATH = N06 / "reports/n06_iteration_4_sc2_native_arbitration.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N06-lgrc-semantic-route-choice/scripts/"
    "run_n06_iteration_4_sc2_native_arbitration.py"
)
ARBITRATION_RUNTIME_VISIBLE_INPUTS = (
    "candidate_route_score",
    "candidate_order_key",
    "candidate_set_order_key",
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


def _prepare_candidate_model(
    manifest: Mapping[str, Any],
    *,
    context_state_id: str = "context_a",
    spec_mutator: Callable[[list[dict[str, Any]]], list[dict[str, Any]]] | None = None,
    unresolved_tie_policy: str = LGRC9V3_NATIVE_ROUTE_UNRESOLVED_TIE_POLICY_FAIL_CLOSED,
) -> dict[str, Any]:
    model, source_row = iter3._seed_model(  # noqa: SLF001
        manifest,
        native_route_arbitration_enabled=True,
    )
    source_surface_digest = str(source_row.surface_digest)
    specs = iter3._candidate_specs(  # noqa: SLF001
        manifest,
        source_surface_digest=source_surface_digest,
        context_state_id=context_state_id,
    )
    if spec_mutator is not None:
        specs = spec_mutator(copy.deepcopy(specs))
    before_counts = iter3._runtime_counts(model)  # noqa: SLF001
    result = model.emit_native_route_candidate_set(
        arbitration_window_id=str(
            manifest["arbitration_window"]["arbitration_window_id"]
        ),
        source_surface_digest=source_surface_digest,
        candidate_routes=specs,
        candidate_set_order_key=(
            LGRC9V3_NATIVE_ROUTE_CANDIDATE_SET_ORDER_SCORE_DESC_THEN_CANDIDATE_ID
        ),
        unresolved_tie_policy=unresolved_tie_policy,
    )
    candidate_set = result["candidate_set_record"]
    if candidate_set is None:
        raise RuntimeError("enabled SC2 lane must emit a candidate set")
    return {
        "model": model,
        "source_row": source_row,
        "source_surface_digest": source_surface_digest,
        "candidate_result": result,
        "candidate_set": candidate_set,
        "candidate_before_counts": before_counts,
    }


def _arbitration_artifact(record: Any | None) -> dict[str, Any] | None:
    if record is None:
        return None
    return record.to_artifact()


def _arbitration_idempotency_check(record: Mapping[str, Any]) -> dict[str, Any]:
    reconstructed = build_lgrc9v3_native_route_arbitration_idempotency_key(
        native_route_arbitration_policy_id=str(
            record["native_route_arbitration_policy_id"]
        ),
        candidate_set_digest=str(record["candidate_set_digest"]),
        selected_candidate_route_digest=record["selected_candidate_route_digest"],
        arbitration_reason_code=str(record["arbitration_reason_code"]),
        arbitration_rule=str(record["arbitration_rule"]),
        selected_topology_event_id=record["selected_topology_event_id"],
    )
    return {
        "recorded_idempotency_key": record["idempotency_key"],
        "reconstructed_idempotency_key": reconstructed,
        "reconstructable": reconstructed == record["idempotency_key"],
    }


def _selection_only_validation(artifacts: Mapping[str, Any]) -> dict[str, Any]:
    validation = validate_lgrc9v3_native_route_arbitration_artifacts(
        events=artifacts["events"],
        candidate_route_records=artifacts["candidate_route_records"],
        candidate_set_records=artifacts["candidate_set_records"],
        route_arbitration_records=artifacts["route_arbitration_records"],
        surface_rows=artifacts["surface_rows"],
        surface_lineage_records=artifacts["surface_lineage_records"],
        topology_events=artifacts["topology_events"],
        topology_state_reabsorption_records=artifacts[
            "topology_state_reabsorption_records"
        ],
        production_results=artifacts["production_results"],
    )
    expected_prefixes = ("selected_topology_event_count_mismatch:",)
    unexpected = [
        reason
        for reason in validation["failure_reasons"]
        if not any(str(reason).startswith(prefix) for prefix in expected_prefixes)
    ]
    expected = [
        reason
        for reason in validation["failure_reasons"]
        if any(str(reason).startswith(prefix) for prefix in expected_prefixes)
    ]
    return {
        **validation,
        "validator_scope": "selection_only_pre_topology_commit",
        "expected_incomplete_reasons": expected,
        "unexpected_failure_reasons": unexpected,
        "selection_contract_valid": not unexpected
        and validation["route_selection_reconstructed_from_artifacts"] is True,
    }


def _selection_replay_checks(
    manifest: Mapping[str, Any],
    artifacts: Mapping[str, Any],
    arbitration_record: Mapping[str, Any],
) -> dict[str, Any]:
    score_tolerance = float(manifest["arbitration_policy"]["score_tolerance"])
    candidates = {
        record["candidate_route_digest"]: record
        for record in artifacts["candidate_route_records"]
    }
    candidate_set = artifacts["candidate_set_records"][0]
    selected_digest = arbitration_record["selected_candidate_route_digest"]
    selected = candidates[selected_digest]
    scores = {
        digest: float(record["candidate_route_score"])
        for digest, record in candidates.items()
    }
    max_score = max(scores.values())
    expected_rejected = sorted(
        digest
        for digest in candidate_set["candidate_route_digests"]
        if digest != selected_digest
    )
    hidden_inputs = {
        "hidden_fixture_array",
        "hidden_fixture_state",
        "experiment_if_else",
        "preselected_sink_id",
        "posthoc_threshold",
        "report_code",
    }
    arbitration_inputs = set(
        str(value) for value in arbitration_record["arbitration_runtime_visible_inputs"]
    )
    checks = {
        "selected_candidate_in_candidate_set": (
            selected_digest in candidate_set["candidate_route_digests"]
        ),
        "selected_candidate_has_highest_score": (
            abs(float(selected["candidate_route_score"]) - max_score)
            <= score_tolerance
        ),
        "arbitration_score_equals_selected_candidate_score": (
            abs(
                float(arbitration_record["arbitration_score"])
                - float(selected["candidate_route_score"])
            )
            <= score_tolerance
        ),
        "rejected_candidates_are_all_nonselected": (
            sorted(arbitration_record["rejected_candidate_route_digests"])
            == expected_rejected
        ),
        "reason_code_selected_highest_score": (
            arbitration_record["arbitration_reason_code"]
            == LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_SELECTED_HIGHEST_SCORE
        ),
        "arbitration_inputs_runtime_visible": not (
            arbitration_inputs & hidden_inputs
        ),
        "selected_route_is_context_a_route_a": (
            selected["candidate_route_id"] == "route_a"
        ),
    }
    return {
        "selected_candidate_route_digest": selected_digest,
        "selected_candidate_route_id": selected["candidate_route_id"],
        "selected_candidate_score": selected["candidate_route_score"],
        "arbitration_score": arbitration_record["arbitration_score"],
        "score_tolerance": score_tolerance,
        "candidate_scores": scores,
        "expected_rejected_candidate_route_digests": expected_rejected,
        "arbitration_runtime_visible_inputs": sorted(arbitration_inputs),
        "checks": checks,
        "selection_replayable_from_serialized_scores": all(checks.values()),
    }


def _authorized_topology_event_checks(
    model: Any,
    *,
    candidate_set: Any,
    arbitration_record: Mapping[str, Any],
) -> dict[str, Any]:
    selected_digest = str(arbitration_record["selected_candidate_route_digest"])
    selected_candidates = [
        candidate
        for candidate in model.get_state().native_route_candidate_log
        if str(candidate.candidate_route_digest) == selected_digest
    ]
    if len(selected_candidates) != 1:
        return {
            "selected_candidate_found": False,
            "derived_topology_event_id": None,
            "derived_topology_event_digest": None,
            "checks": {
                "selected_candidate_found": False,
                "authorized_topology_event_id_matches_candidate": False,
                "authorized_topology_event_digest_matches_candidate": False,
                "candidate_lineage_targets_selected_sink": False,
            },
            "authorized_topology_event_matches_selected_candidate": False,
        }
    selected_candidate = selected_candidates[0]
    expected_event_id, expected_event_digest = model._selected_topology_event_for_candidate(  # noqa: SLF001
        selected_candidate,
        native_route_arbitration_record_id=str(
            arbitration_record["native_route_arbitration_record_id"]
        ),
        native_route_arbitration_digest=None,
        candidate_set_digest=str(candidate_set.candidate_set_digest),
    )
    selected_sink_lineage = str(selected_candidate.candidate_selected_sink_id)
    lineage_targets_selected_sink = all(
        str(value) == selected_sink_lineage
        for value in selected_candidate.candidate_lineage_transfer_map.values()
    )
    checks = {
        "selected_candidate_found": True,
        "authorized_topology_event_id_matches_candidate": (
            expected_event_id == arbitration_record["selected_topology_event_id"]
        ),
        "authorized_topology_event_digest_matches_candidate": (
            expected_event_digest
            == arbitration_record["selected_topology_event_digest"]
        ),
        "candidate_lineage_targets_selected_sink": lineage_targets_selected_sink,
    }
    return {
        "selected_candidate_found": True,
        "selected_candidate_route_id": selected_candidate.candidate_route_id,
        "selected_candidate_route_digest": selected_digest,
        "candidate_topology_event_kind": (
            selected_candidate.candidate_topology_event_kind
        ),
        "candidate_selected_sink_id": int(
            selected_candidate.candidate_selected_sink_id
        ),
        "candidate_lineage_transfer_map": dict(
            selected_candidate.candidate_lineage_transfer_map
        ),
        "derived_topology_event_id": expected_event_id,
        "derived_topology_event_digest": expected_event_digest,
        "recorded_topology_event_id": arbitration_record[
            "selected_topology_event_id"
        ],
        "recorded_topology_event_digest": arbitration_record[
            "selected_topology_event_digest"
        ],
        "checks": checks,
        "authorized_topology_event_matches_selected_candidate": all(checks.values()),
    }


def _run_positive_lane(manifest: Mapping[str, Any]) -> dict[str, Any]:
    prepared = _prepare_candidate_model(manifest)
    model = prepared["model"]
    candidate_set = prepared["candidate_set"]
    before_counts = iter3._runtime_counts(model)  # noqa: SLF001
    arbitration_result = model.arbitrate_native_route_candidate_set(
        candidate_set_digest=str(candidate_set.candidate_set_digest),
        arbitration_runtime_visible_inputs=ARBITRATION_RUNTIME_VISIBLE_INPUTS,
    )
    after_counts = iter3._runtime_counts(model)  # noqa: SLF001
    artifacts = iter3._runtime_artifacts(model)  # noqa: SLF001
    arbitration_record = arbitration_result["route_arbitration_record"]
    arbitration_artifact = _arbitration_artifact(arbitration_record)
    assert arbitration_artifact is not None
    replay_checks = _selection_replay_checks(
        manifest,
        artifacts,
        arbitration_artifact,
    )
    validation = _selection_only_validation(artifacts)
    idempotency = _arbitration_idempotency_check(arbitration_artifact)
    topology_authorization = _authorized_topology_event_checks(
        model,
        candidate_set=candidate_set,
        arbitration_record=arbitration_artifact,
    )
    checks = {
        "candidate_set_consumed": (
            arbitration_artifact["candidate_set_digest"]
            == str(candidate_set.candidate_set_digest)
        ),
        "one_route_arbitration_record_emitted": (
            after_counts["route_arbitration_count"] == 1
        ),
        "exactly_one_selected_candidate": (
            arbitration_artifact["selected_candidate_route_digest"] is not None
            and len(arbitration_artifact["rejected_candidate_route_digests"]) == 1
        ),
        "selected_candidate_is_route_a": (
            replay_checks["selected_candidate_route_id"] == "route_a"
        ),
        "rejected_candidate_recorded": (
            bool(arbitration_artifact["rejected_candidate_route_digests"])
        ),
        "arbitration_rule_and_reason_recorded": (
            bool(arbitration_artifact["arbitration_rule"])
            and arbitration_artifact["arbitration_reason_code"]
            == LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_SELECTED_HIGHEST_SCORE
        ),
        "selection_replayable_from_serialized_scores": replay_checks[
            "selection_replayable_from_serialized_scores"
        ],
        "arbitration_idempotency_reconstructable": idempotency["reconstructable"],
        "authorized_topology_event_matches_selected_candidate": (
            topology_authorization[
                "authorized_topology_event_matches_selected_candidate"
            ]
        ),
        "selection_only_artifact_validation_scope_clean": validation[
            "selection_contract_valid"
        ],
        "no_selected_topology_event_committed": (
            after_counts["topology_event_count"] == 0
        ),
        "no_packet_scheduled_by_arbitration": (
            after_counts["event_count"] == before_counts["event_count"]
            and after_counts["production_result_count"]
            == before_counts["production_result_count"]
        ),
        "claim_flags_remain_false": iter3._claim_flags_false_in_records(  # noqa: SLF001
            [
                *artifacts["candidate_route_records"],
                *artifacts["candidate_set_records"],
                *artifacts["route_arbitration_records"],
            ]
        ),
    }
    return {
        "lane_id": "enabled_sc2_native_arbitration_selection",
        "source_surface_digest": prepared["source_surface_digest"],
        "candidate_set_digest": str(candidate_set.candidate_set_digest),
        "candidate_route_count": len(artifacts["candidate_route_records"]),
        "candidate_set_count": len(artifacts["candidate_set_records"]),
        "route_arbitration_count": len(artifacts["route_arbitration_records"]),
        "selected_candidate_route_digest": arbitration_artifact[
            "selected_candidate_route_digest"
        ],
        "selected_candidate_route_id": replay_checks["selected_candidate_route_id"],
        "selected_topology_event_id_authorized": arbitration_artifact[
            "selected_topology_event_id"
        ],
        "selected_topology_event_digest_authorized": arbitration_artifact[
            "selected_topology_event_digest"
        ],
        "rejected_candidate_route_digests": arbitration_artifact[
            "rejected_candidate_route_digests"
        ],
        "arbitration_reason_code": arbitration_artifact["arbitration_reason_code"],
        "arbitration_rule": arbitration_artifact["arbitration_rule"],
        "before_counts": before_counts,
        "after_counts": after_counts,
        "selection_replay": replay_checks,
        "topology_event_authorization": topology_authorization,
        "selection_only_artifact_validation": validation,
        "arbitration_idempotency_check": idempotency,
        "candidate_route_records": artifacts["candidate_route_records"],
        "candidate_set_record": artifacts["candidate_set_records"][0],
        "route_arbitration_record": arbitration_artifact,
        "checks": checks,
        "passed": all(checks.values()),
    }


def _control_result(
    control_id: str,
    *,
    passed: bool,
    primary_blocker: str,
    detail: Any = None,
    scope: str = "native_runtime",
) -> dict[str, Any]:
    return {
        "control_id": control_id,
        "scope": scope,
        "passed": bool(passed),
        "primary_blocker": primary_blocker,
        "detail": detail,
    }


def _record_reason(record: Any | None) -> str | None:
    if record is None:
        return None
    return str(record.arbitration_reason_code)


def _append_candidate_set(model: Any, record: LGRC9V3NativeRouteCandidateSetRecord) -> None:
    model.get_state().native_route_candidate_set_log.append(record)


def _empty_candidate_set_from(candidate_set: Any) -> LGRC9V3NativeRouteCandidateSetRecord:
    return LGRC9V3NativeRouteCandidateSetRecord(
        candidate_set_id=f"{candidate_set.candidate_set_id}:empty",
        native_route_arbitration_policy_id=candidate_set.native_route_arbitration_policy_id,
        native_route_arbitration_enabled=True,
        arbitration_window_id=candidate_set.arbitration_window_id,
        event_time_key=float(candidate_set.event_time_key),
        scheduler_event_index=int(candidate_set.scheduler_event_index),
        candidate_route_digests=(),
        candidate_set_order_key=candidate_set.candidate_set_order_key,
        unresolved_tie_policy=candidate_set.unresolved_tie_policy,
        lgrc_runtime_level=candidate_set.lgrc_runtime_level,
        causal_layer_mode=candidate_set.causal_layer_mode,
        claim_flags=candidate_set.claim_flags,
    )


def _order_invalid_candidate_set_from(
    candidate_set: Any,
) -> LGRC9V3NativeRouteCandidateSetRecord:
    return LGRC9V3NativeRouteCandidateSetRecord(
        candidate_set_id=f"{candidate_set.candidate_set_id}:order-invalid",
        native_route_arbitration_policy_id=candidate_set.native_route_arbitration_policy_id,
        native_route_arbitration_enabled=True,
        arbitration_window_id=candidate_set.arbitration_window_id,
        event_time_key=float(candidate_set.event_time_key),
        scheduler_event_index=int(candidate_set.scheduler_event_index),
        candidate_route_digests=tuple(reversed(candidate_set.candidate_route_digests)),
        candidate_set_order_key=candidate_set.candidate_set_order_key,
        unresolved_tie_policy=candidate_set.unresolved_tie_policy,
        lgrc_runtime_level=candidate_set.lgrc_runtime_level,
        causal_layer_mode=candidate_set.causal_layer_mode,
        claim_flags=candidate_set.claim_flags,
    )


def _run_controls(
    manifest: Mapping[str, Any],
    positive_lane: Mapping[str, Any],
) -> dict[str, Any]:
    controls: dict[str, dict[str, Any]] = {}

    disabled_model, _source_row = iter3._seed_model(  # noqa: SLF001
        manifest,
        native_route_arbitration_enabled=False,
    )
    disabled_result = disabled_model.arbitrate_native_route_candidate_set(
        candidate_set_digest="disabled-policy-no-candidate-set-needed"
    )
    controls["policy_disabled"] = _control_result(
        "policy_disabled",
        passed=disabled_result["emitted"] is False
        and disabled_result["reason_code"]
        == LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_POLICY_DISABLED,
        primary_blocker=LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_POLICY_DISABLED,
        detail=disabled_result,
    )

    no_candidate = _prepare_candidate_model(manifest)
    empty_set = _empty_candidate_set_from(no_candidate["candidate_set"])
    _append_candidate_set(no_candidate["model"], empty_set)
    no_candidate_result = no_candidate["model"].arbitrate_native_route_candidate_set(
        candidate_set_digest=str(empty_set.candidate_set_digest)
    )
    controls["no_candidates"] = _control_result(
        "no_candidates",
        passed=_record_reason(no_candidate_result["route_arbitration_record"])
        == LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_NO_CANDIDATES,
        primary_blocker=LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_NO_CANDIDATES,
        detail=_arbitration_artifact(no_candidate_result["route_arbitration_record"]),
        scope="native_runtime_with_experiment_injected_empty_candidate_set",
    )

    def tie_mutator(specs: list[dict[str, Any]]) -> list[dict[str, Any]]:
        for spec in specs:
            spec["candidate_score_components"] = {
                "context_match": 0.1,
                "budget_validity": 0.2,
                "lineage_ready": 0.2,
            }
            spec["candidate_route_score"] = 0.5
        return specs

    tie = _prepare_candidate_model(manifest, spec_mutator=tie_mutator)
    tie_result = tie["model"].arbitrate_native_route_candidate_set(
        candidate_set_digest=str(tie["candidate_set"].candidate_set_digest)
    )
    controls["unresolved_tie"] = _control_result(
        "unresolved_tie",
        passed=_record_reason(tie_result["route_arbitration_record"])
        == LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_UNRESOLVED_TIE,
        primary_blocker=LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_UNRESOLVED_TIE,
        detail=_arbitration_artifact(tie_result["route_arbitration_record"]),
    )

    invalid_budget_prediction = {
        "node_plus_packet_budget_before": 6.0,
        "node_plus_packet_budget_after": 5.0,
        "node_plus_packet_budget_error": -1.0,
    }

    def budget_invalid_mutator(specs: list[dict[str, Any]]) -> list[dict[str, Any]]:
        specs[0]["candidate_budget_prediction"] = dict(invalid_budget_prediction)
        return specs

    budget_invalid = _prepare_candidate_model(
        manifest,
        spec_mutator=budget_invalid_mutator,
    )
    budget_result = budget_invalid["model"].arbitrate_native_route_candidate_set(
        candidate_set_digest=str(budget_invalid["candidate_set"].candidate_set_digest)
    )
    controls["budget_invalid"] = _control_result(
        "budget_invalid",
        passed=_record_reason(budget_result["route_arbitration_record"])
        == LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_BUDGET_INVALID,
        primary_blocker=LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_BUDGET_INVALID,
        detail={
            "mutated_budget_prediction": invalid_budget_prediction,
            "budget_tolerance": manifest["arbitration_policy"]["budget_tolerance"],
            "budget_error_exceeds_manifest_tolerance": (
                abs(invalid_budget_prediction["node_plus_packet_budget_error"])
                > float(manifest["arbitration_policy"]["budget_tolerance"])
            ),
            "route_arbitration_record": _arbitration_artifact(
                budget_result["route_arbitration_record"]
            ),
        },
    )

    order_invalid = _prepare_candidate_model(manifest)
    invalid_set = _order_invalid_candidate_set_from(order_invalid["candidate_set"])
    _append_candidate_set(order_invalid["model"], invalid_set)
    order_result = order_invalid["model"].arbitrate_native_route_candidate_set(
        candidate_set_digest=str(invalid_set.candidate_set_digest)
    )
    controls["order_invalid"] = _control_result(
        "order_invalid",
        passed=_record_reason(order_result["route_arbitration_record"])
        == LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_ORDER_INVALID,
        primary_blocker=LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_ORDER_INVALID,
        detail=_arbitration_artifact(order_result["route_arbitration_record"]),
        scope="native_runtime_with_experiment_injected_order_invalid_candidate_set",
    )

    hidden = _prepare_candidate_model(manifest)
    hidden_attempted_inputs = ("candidate_route_score", "report_code")
    hidden_result = hidden["model"].arbitrate_native_route_candidate_set(
        candidate_set_digest=str(hidden["candidate_set"].candidate_set_digest),
        arbitration_runtime_visible_inputs=hidden_attempted_inputs,
    )
    hidden_artifact = _arbitration_artifact(hidden_result["route_arbitration_record"])
    controls["hidden_input"] = _control_result(
        "hidden_input",
        passed=_record_reason(hidden_result["route_arbitration_record"])
        == LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_HIDDEN_INPUT_REJECTED,
        primary_blocker=LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_HIDDEN_INPUT_REJECTED,
        detail={
            "attempted_arbitration_runtime_visible_inputs": list(
                hidden_attempted_inputs
            ),
            "native_record_arbitration_runtime_visible_inputs": []
            if hidden_artifact is None
            else hidden_artifact["arbitration_runtime_visible_inputs"],
            "route_arbitration_record": hidden_artifact,
        },
    )

    duplicate = _prepare_candidate_model(manifest)
    first = duplicate["model"].arbitrate_native_route_candidate_set(
        candidate_set_digest=str(duplicate["candidate_set"].candidate_set_digest)
    )
    count_after_first = iter3._runtime_counts(duplicate["model"])[  # noqa: SLF001
        "route_arbitration_count"
    ]
    second = duplicate["model"].arbitrate_native_route_candidate_set(
        candidate_set_digest=str(duplicate["candidate_set"].candidate_set_digest)
    )
    count_after_second = iter3._runtime_counts(duplicate["model"])[  # noqa: SLF001
        "route_arbitration_count"
    ]
    controls["duplicate_arbitration"] = _control_result(
        "duplicate_arbitration",
        passed=count_after_first == 1
        and count_after_second == 1
        and first["route_arbitration_record"].idempotency_key
        == second["route_arbitration_record"].idempotency_key
        and first["route_arbitration_record"].native_route_arbitration_digest
        == second["route_arbitration_record"].native_route_arbitration_digest
        and first["route_arbitration_record"].to_artifact()
        == second["route_arbitration_record"].to_artifact(),
        primary_blocker="duplicate_native_route_arbitration_suppressed",
        detail={
            "count_after_first": count_after_first,
            "count_after_second": count_after_second,
            "same_idempotency_key": (
                first["route_arbitration_record"].idempotency_key
                == second["route_arbitration_record"].idempotency_key
            ),
            "same_native_route_arbitration_digest": (
                first[
                    "route_arbitration_record"
                ].native_route_arbitration_digest
                == second[
                    "route_arbitration_record"
                ].native_route_arbitration_digest
            ),
            "same_route_arbitration_artifact": (
                first["route_arbitration_record"].to_artifact()
                == second["route_arbitration_record"].to_artifact()
            ),
        },
    )

    corrupted_record = copy.deepcopy(positive_lane["route_arbitration_record"])
    corrupted_record["claim_flags"]["semantic_choice_claim_allowed"] = True
    claim_validation = validate_lgrc9v3_native_route_arbitration_artifacts(
        events=[],
        candidate_route_records=positive_lane["candidate_route_records"],
        candidate_set_records=[positive_lane["candidate_set_record"]],
        route_arbitration_records=[corrupted_record],
        surface_rows=[],
    )
    controls["claim_promotion"] = _control_result(
        "claim_promotion",
        passed=any(
            "native_route_arbitration_claim_promotion_blocked" in reason
            for reason in claim_validation["failure_reasons"]
        ),
        primary_blocker="native_route_arbitration_claim_promotion_blocked",
        detail={
            "specific_claim_promotion_blocker_present": any(
                "native_route_arbitration_claim_promotion_blocked" in reason
                for reason in claim_validation["failure_reasons"]
            ),
            "failure_reasons": claim_validation["failure_reasons"],
        },
        scope="artifact_replay_control",
    )

    return controls


def _build_report(data: Mapping[str, Any]) -> str:
    lane = data["lanes"]["enabled_sc2"]
    lines = [
        "# N06 Iteration 4 SC2 Native Arbitration",
        "",
        f"- status: `{data['status']}`",
        f"- generated: `{data['generated_at']}`",
        f"- command: `{COMMAND}`",
        f"- selected candidate route: `{lane['selected_candidate_route_id']}`",
        f"- selected candidate digest: `{lane['selected_candidate_route_digest']}`",
        f"- arbitration reason: `{lane['arbitration_reason_code']}`",
        f"- authorized topology event digest: `{lane['selected_topology_event_digest_authorized']}`",
        "",
        "## Boundary",
        "",
        "- SC2 emits one native route-arbitration record.",
        "- The selected topology event id/digest is authorized by the arbitration record, but no topology event is committed in this iteration.",
        "- No post-selection packet is scheduled and no claim flag is promoted.",
        "",
        "## Acceptance",
        "",
        "```json",
        json.dumps(data["acceptance"], indent=2, sort_keys=True),
        "```",
        "",
        "## Selection Replay",
        "",
        "```json",
        json.dumps(lane["selection_replay"], indent=2, sort_keys=True),
        "```",
        "",
        "## Selection-Only Artifact Replay Scope",
        "",
        "The full native route-arbitration validator expects a committed selected topology event. Iteration 4 records the expected pre-commit limitation and treats any other replay failure as a blocker.",
        "",
        "```json",
        json.dumps(
            lane["selection_only_artifact_validation"],
            indent=2,
            sort_keys=True,
        ),
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
    positive_lane = _run_positive_lane(manifest)
    controls = _run_controls(manifest, positive_lane)
    checks = {
        "enabled_sc2_lane_passed": positive_lane["passed"],
        "controls_passed": all(control["passed"] for control in controls.values()),
        "no_selected_topology_event_committed": positive_lane["checks"][
            "no_selected_topology_event_committed"
        ],
        "no_packet_scheduled_by_arbitration": positive_lane["checks"][
            "no_packet_scheduled_by_arbitration"
        ],
        "claim_flags_remain_false": positive_lane["checks"][
            "claim_flags_remain_false"
        ],
    }
    status = "passed" if all(checks.values()) else "failed"
    acceptance = {
        "sc_level": "SC2",
        "claim_ceiling": "native_route_arbitration_selection_no_context_swap",
        "candidate_set_consumed": positive_lane["checks"]["candidate_set_consumed"],
        "route_arbitration_record_emitted": positive_lane["checks"][
            "one_route_arbitration_record_emitted"
        ],
        "exactly_one_route_selected": positive_lane["checks"][
            "exactly_one_selected_candidate"
        ],
        "selected_route": positive_lane["selected_candidate_route_id"],
        "selection_replayable_from_serialized_scores": positive_lane[
            "checks"
        ]["selection_replayable_from_serialized_scores"],
        "topology_event_committed": False,
        "packet_scheduled_by_arbitration": False,
        "semantic_choice_claim_allowed": False,
        "context_swap_evidence_available": False,
        "status": status,
    }
    data: dict[str, Any] = {
        "schema": "semantic_route_choice_report_v1",
        "experiment": "2026-05-N06-lgrc-semantic-route-choice",
        "iteration": 4,
        "iteration_name": "SC2 Native Arbitration Selection",
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": COMMAND,
        "platform": {
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "manifest": _artifact_record(MANIFEST_PATH),
        "source_iteration": _artifact_record(iter3.OUTPUT_PATH),
        "lanes": {"enabled_sc2": positive_lane},
        "controls": controls,
        "checks": checks,
        "acceptance": acceptance,
        "claim_flags": {flag: False for flag in iter3.CLAIM_FLAGS},
        "artifact_digests": {},
        "git": {
            "status_src": _git(["status", "--short", "src"]),
            "diff_check_experiment": _git(
                ["diff", "--check", "--", _rel(N06)]
            ),
        },
    }
    data["artifact_digests"] = {
        "enabled_lane_digest": _digest(positive_lane),
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
                "selected_route": positive_lane["selected_candidate_route_id"],
                "route_arbitration_count": positive_lane[
                    "route_arbitration_count"
                ],
                "controls_passed": checks["controls_passed"],
                "topology_event_committed": False,
                "semantic_choice_claim_allowed": False,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
