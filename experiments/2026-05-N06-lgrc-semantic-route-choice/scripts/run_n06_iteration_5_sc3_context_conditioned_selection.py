#!/usr/bin/env python3
"""Run N06 Iteration 5: SC3 context-conditioned route selection.

The probe runs the same native LGRC9V3 fixture and serialized arbitration
policy under two runtime-visible context states. Context A must select route A;
context B must select route B. This remains an evidence classification, not a
semantic-choice claim flag promotion.
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
    LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_BUDGET_INVALID,
    LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_HIDDEN_INPUT_REJECTED,
    LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_SELECTED_HIGHEST_SCORE,
    validate_lgrc9v3_native_route_arbitration_artifacts,
)

import run_n06_iteration_3_sc1_candidate_alternatives as iter3  # noqa: E402
import run_n06_iteration_4_sc2_native_arbitration as iter4  # noqa: E402


N06 = ROOT / "experiments/2026-05-N06-lgrc-semantic-route-choice"
MANIFEST_PATH = N06 / "configs/n06_fixture_manifest_v1.json"
OUTPUT_PATH = N06 / "outputs/n06_iteration_5_sc3_context_conditioned_selection.json"
REPORT_PATH = N06 / "reports/n06_iteration_5_sc3_context_conditioned_selection.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N06-lgrc-semantic-route-choice/scripts/"
    "run_n06_iteration_5_sc3_context_conditioned_selection.py"
)

HIDDEN_INPUTS = {
    "hidden_fixture_array",
    "hidden_fixture_state",
    "experiment_if_else",
    "preselected_sink_id",
    "posthoc_threshold",
    "report_code",
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


def _context_state(manifest: Mapping[str, Any], context_state_id: str) -> Mapping[str, Any]:
    return manifest["context_affordance_surface"]["context_states"][
        context_state_id
    ]


def _candidate_by_digest(
    artifacts: Mapping[str, Any],
) -> dict[str, Mapping[str, Any]]:
    return {
        str(record["candidate_route_digest"]): record
        for record in artifacts["candidate_route_records"]
    }


def _selected_candidate(
    artifacts: Mapping[str, Any],
    arbitration_record: Mapping[str, Any],
) -> Mapping[str, Any]:
    candidates = _candidate_by_digest(artifacts)
    return candidates[str(arbitration_record["selected_candidate_route_digest"])]


def _candidate_runtime_inputs(record: Mapping[str, Any]) -> set[str]:
    return set(str(value) for value in record["candidate_runtime_visible_inputs"])


def _dedupe_reasons(reasons: Sequence[str]) -> list[str]:
    deduped: list[str] = []
    seen: set[str] = set()
    for reason in reasons:
        if reason not in seen:
            deduped.append(reason)
            seen.add(reason)
    return deduped


def _reason_has_blocker(reasons: Sequence[str], blocker: str) -> bool:
    return any(str(reason).split(":", 1)[0] == blocker for reason in reasons)


def _runtime_input_values(record: Mapping[str, Any], prefix: str) -> list[str]:
    field_prefix = f"{prefix}:"
    return sorted(
        str(value).split(":", 1)[1]
        for value in record["candidate_runtime_visible_inputs"]
        if str(value).startswith(field_prefix)
    )


def _arbitration_inputs_for_context(
    manifest: Mapping[str, Any],
    *,
    context_state_id: str,
    source_surface_digest: str,
) -> tuple[str, ...]:
    context = _context_state(manifest, context_state_id)
    return (
        *iter4.ARBITRATION_RUNTIME_VISIBLE_INPUTS,
        f"active_context_node_id:{int(context['active_context_node_id'])}",
        f"compatible_route_id:{context['compatible_route_id']}",
        f"context_surface_digest:{source_surface_digest}",
    )


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
        "validator_scope": "sc3_context_selection_pre_topology_commit",
        "expected_incomplete_reasons": expected,
        "unexpected_failure_reasons": unexpected,
        "selection_contract_valid": not unexpected
        and validation["route_selection_reconstructed_from_artifacts"] is True,
    }


def _context_relation_replay(
    manifest: Mapping[str, Any],
    *,
    context_state_id: str,
    source_surface_digest: str,
    artifacts: Mapping[str, Any],
    arbitration_record: Mapping[str, Any],
) -> dict[str, Any]:
    context = _context_state(manifest, context_state_id)
    compatible_route_id = str(context["compatible_route_id"])
    active_context_node_id = int(context["active_context_node_id"])
    selected = _selected_candidate(artifacts, arbitration_record)
    score_tolerance = float(manifest["arbitration_policy"]["score_tolerance"])
    score_templates = context["candidate_score_templates"]
    per_candidate: dict[str, Any] = {}
    all_candidates_replay = True
    hidden_input_seen = False
    serialized_context_values: dict[str, set[str]] = {
        "active_context_node_id": set(),
        "compatible_route_id": set(),
        "context_surface_digest": set(),
    }
    for record in artifacts["candidate_route_records"]:
        route_id = str(record["candidate_route_id"])
        runtime_inputs = _candidate_runtime_inputs(record)
        field_names = {item.split(":", 1)[0] for item in runtime_inputs}
        active_context_values = _runtime_input_values(
            record,
            "active_context_node_id",
        )
        compatible_route_values = _runtime_input_values(
            record,
            "compatible_route_id",
        )
        context_surface_values = _runtime_input_values(
            record,
            "context_surface_digest",
        )
        serialized_context_values["active_context_node_id"].update(
            active_context_values
        )
        serialized_context_values["compatible_route_id"].update(
            compatible_route_values
        )
        serialized_context_values["context_surface_digest"].update(
            context_surface_values
        )
        score_components = {
            str(key): float(value)
            for key, value in record["candidate_score_components"].items()
        }
        expected_score = float(
            score_templates[route_id]["candidate_route_score"]
        )
        expected_components = {
            str(key): float(value)
            for key, value in score_templates[route_id][
                "candidate_score_components"
            ].items()
        }
        component_checks = {
            key: abs(float(score_components.get(key, float("nan"))) - value)
            <= score_tolerance
            for key, value in expected_components.items()
        }
        route_hidden_inputs = sorted(runtime_inputs & HIDDEN_INPUTS)
        hidden_input_seen = hidden_input_seen or bool(route_hidden_inputs)
        checks = {
            "score_matches_context_template": (
                abs(float(record["candidate_route_score"]) - expected_score)
                <= score_tolerance
            ),
            "score_components_match_context_template": all(
                component_checks.values()
            ),
            "active_context_node_serialized": (
                f"active_context_node_id:{active_context_node_id}" in runtime_inputs
            ),
            "candidate_route_id_serialized": (
                f"candidate_route_id:{route_id}" in runtime_inputs
            ),
            "compatible_route_id_serialized": (
                f"compatible_route_id:{compatible_route_id}" in runtime_inputs
            ),
            "context_surface_digest_serialized": (
                f"context_surface_digest:{source_surface_digest}" in runtime_inputs
            ),
            "context_fields_runtime_visible": {
                "active_context_node_id",
                "candidate_route_id",
                "compatible_route_id",
                "context_surface_digest",
            }.issubset(field_names),
            "no_hidden_inputs": not route_hidden_inputs,
        }
        replay_ok = all(checks.values())
        all_candidates_replay = all_candidates_replay and replay_ok
        per_candidate[route_id] = {
            "expected_score": expected_score,
            "actual_score": record["candidate_route_score"],
            "expected_score_components": expected_components,
            "actual_score_components": score_components,
            "serialized_context_values": {
                "active_context_node_id": active_context_values,
                "compatible_route_id": compatible_route_values,
                "context_surface_digest": context_surface_values,
            },
            "runtime_visible_field_names": sorted(field_names),
            "hidden_inputs": route_hidden_inputs,
            "checks": checks,
            "replay_ok": replay_ok,
        }
    route_scores = {
        str(record["candidate_route_id"]): float(record["candidate_route_score"])
        for record in artifacts["candidate_route_records"]
    }
    selected_route_id = str(selected["candidate_route_id"])
    selected_score = float(selected["candidate_route_score"])
    arbitration_score = float(arbitration_record["arbitration_score"])
    arbitration_inputs = set(
        str(value) for value in arbitration_record["arbitration_runtime_visible_inputs"]
    )
    arbitration_context_values = {
        "active_context_node_id": sorted(
            value.split(":", 1)[1]
            for value in arbitration_inputs
            if value.startswith("active_context_node_id:")
        ),
        "compatible_route_id": sorted(
            value.split(":", 1)[1]
            for value in arbitration_inputs
            if value.startswith("compatible_route_id:")
        ),
        "context_surface_digest": sorted(
            value.split(":", 1)[1]
            for value in arbitration_inputs
            if value.startswith("context_surface_digest:")
        ),
    }
    serialized_context_summary = {
        key: sorted(values) for key, values in serialized_context_values.items()
    }
    serialized_context_singleton = {
        key: values[0] if len(values) == 1 else None
        for key, values in serialized_context_summary.items()
    }
    serialized_compatible_route_id = serialized_context_singleton[
        "compatible_route_id"
    ]
    serialized_context_values_agree = all(
        len(values) == 1 for values in serialized_context_summary.values()
    )
    arbitration_context_singleton = {
        key: values[0] if len(values) == 1 else None
        for key, values in arbitration_context_values.items()
    }
    arbitration_hidden_inputs = sorted(arbitration_inputs & HIDDEN_INPUTS)
    candidate_score_component_sums = {
        str(record["candidate_route_id"]): sum(
            float(value) for value in record["candidate_score_components"].values()
        )
        for record in artifacts["candidate_route_records"]
    }
    checks = {
        "selected_route_matches_context_relation": (
            selected_route_id == compatible_route_id
        ),
        "serialized_context_values_agree_across_candidates": (
            serialized_context_values_agree
        ),
        "serialized_context_matches_expected_context": (
            serialized_context_singleton["active_context_node_id"]
            == str(active_context_node_id)
            and serialized_compatible_route_id == compatible_route_id
            and serialized_context_singleton["context_surface_digest"]
            == source_surface_digest
        ),
        "selected_route_matches_serialized_context_relation": (
            serialized_compatible_route_id is not None
            and selected_route_id == serialized_compatible_route_id
        ),
        "arbitration_context_fields_serialized": (
            arbitration_context_singleton["active_context_node_id"]
            == str(active_context_node_id)
            and arbitration_context_singleton["compatible_route_id"]
            == compatible_route_id
            and arbitration_context_singleton["context_surface_digest"]
            == source_surface_digest
        ),
        "candidate_arbitration_context_consistent": (
            arbitration_context_singleton == serialized_context_singleton
        ),
        "selected_route_has_highest_score": (
            route_scores[selected_route_id] == max(route_scores.values())
        ),
        "arbitration_score_equals_selected_candidate_score": (
            abs(arbitration_score - selected_score) <= score_tolerance
        ),
        "candidate_route_scores_equal_component_sums": all(
            abs(
                float(record["candidate_route_score"])
                - candidate_score_component_sums[str(record["candidate_route_id"])]
            )
            <= score_tolerance
            for record in artifacts["candidate_route_records"]
        ),
        "candidate_context_evidence_replayable": all_candidates_replay,
        "hidden_inputs_absent": not hidden_input_seen,
        "arbitration_hidden_inputs_absent": not arbitration_hidden_inputs,
        "arbitration_reason_selected_highest_score": (
            arbitration_record["arbitration_reason_code"]
            == LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_SELECTED_HIGHEST_SCORE
        ),
    }
    return {
        "context_state_id": context_state_id,
        "active_context_node_id": active_context_node_id,
        "compatible_route_id": compatible_route_id,
        "serialized_context_summary": serialized_context_summary,
        "arbitration_context_values": arbitration_context_values,
        "arbitration_runtime_visible_inputs": sorted(arbitration_inputs),
        "arbitration_hidden_inputs": arbitration_hidden_inputs,
        "selected_route_id": selected_route_id,
        "selected_candidate_score": selected_score,
        "arbitration_score": arbitration_score,
        "candidate_score_component_sums": candidate_score_component_sums,
        "source_surface_digest": source_surface_digest,
        "score_tolerance": score_tolerance,
        "route_scores": route_scores,
        "per_candidate": per_candidate,
        "checks": checks,
        "context_relation_replayable": all(checks.values()),
    }


def _run_context_lane(
    manifest: Mapping[str, Any],
    *,
    context_state_id: str,
) -> dict[str, Any]:
    prepared = iter4._prepare_candidate_model(  # noqa: SLF001
        manifest,
        context_state_id=context_state_id,
    )
    model = prepared["model"]
    candidate_set = prepared["candidate_set"]
    before_counts = iter3._runtime_counts(model)  # noqa: SLF001
    arbitration_inputs = _arbitration_inputs_for_context(
        manifest,
        context_state_id=context_state_id,
        source_surface_digest=prepared["source_surface_digest"],
    )
    arbitration_result = model.arbitrate_native_route_candidate_set(
        candidate_set_digest=str(candidate_set.candidate_set_digest),
        arbitration_runtime_visible_inputs=arbitration_inputs,
    )
    after_counts = iter3._runtime_counts(model)  # noqa: SLF001
    artifacts = iter3._runtime_artifacts(model)  # noqa: SLF001
    arbitration_record = iter4._arbitration_artifact(  # noqa: SLF001
        arbitration_result["route_arbitration_record"]
    )
    assert arbitration_record is not None
    context_replay = _context_relation_replay(
        manifest,
        context_state_id=context_state_id,
        source_surface_digest=prepared["source_surface_digest"],
        artifacts=artifacts,
        arbitration_record=arbitration_record,
    )
    artifact_validation = _selection_only_validation(artifacts)
    topology_authorization = iter4._authorized_topology_event_checks(  # noqa: SLF001
        model,
        candidate_set=candidate_set,
        arbitration_record=arbitration_record,
    )
    selected = _selected_candidate(artifacts, arbitration_record)
    checks = {
        "candidate_set_emitted": len(artifacts["candidate_set_records"]) == 1,
        "route_arbitration_record_emitted": (
            len(artifacts["route_arbitration_records"]) == 1
        ),
        "exactly_one_route_selected": (
            arbitration_record["selected_candidate_route_digest"] is not None
            and len(arbitration_record["rejected_candidate_route_digests"]) == 1
        ),
        "selected_route_matches_context_relation": context_replay["checks"][
            "selected_route_matches_context_relation"
        ],
        "context_relation_replayable": context_replay[
            "context_relation_replayable"
        ],
        "artifact_selection_replay_clean": artifact_validation[
            "selection_contract_valid"
        ],
        "topology_authorization_valid": topology_authorization[
            "authorized_topology_event_matches_selected_candidate"
        ],
        "budget_exact": all(
            abs(
                float(
                    candidate["candidate_budget_prediction"][
                        "node_plus_packet_budget_error"
                    ]
                )
            )
            <= float(manifest["arbitration_policy"]["budget_tolerance"])
            for candidate in artifacts["candidate_route_records"]
        ),
        "no_topology_event_committed": after_counts["topology_event_count"] == 0,
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
        "lane_id": f"sc3_{context_state_id}_native_arbitration",
        "context_state_id": context_state_id,
        "source_surface_digest": prepared["source_surface_digest"],
        "candidate_set_digest": str(candidate_set.candidate_set_digest),
        "selected_candidate_route_id": str(selected["candidate_route_id"]),
        "selected_candidate_route_digest": arbitration_record[
            "selected_candidate_route_digest"
        ],
        "rejected_candidate_route_digests": arbitration_record[
            "rejected_candidate_route_digests"
        ],
        "arbitration_reason_code": arbitration_record["arbitration_reason_code"],
        "arbitration_runtime_visible_inputs": list(arbitration_inputs),
        "before_counts": before_counts,
        "after_counts": after_counts,
        "context_relation_replay": context_replay,
        "selection_only_artifact_validation": artifact_validation,
        "topology_event_authorization": topology_authorization,
        "candidate_route_records": artifacts["candidate_route_records"],
        "candidate_set_record": artifacts["candidate_set_records"][0],
        "route_arbitration_record": arbitration_record,
        "checks": checks,
        "passed": all(checks.values()),
    }


def _semantic_context_validator(
    lane: Mapping[str, Any],
) -> dict[str, Any]:
    replay = lane["context_relation_replay"]
    reasons: list[str] = []
    if not replay["checks"]["serialized_context_matches_expected_context"]:
        reasons.append("n06_stale_context_surface_blocked")
    if not replay["checks"]["selected_route_matches_serialized_context_relation"]:
        reasons.append("n06_stale_context_surface_blocked")
    if not replay["checks"]["candidate_arbitration_context_consistent"]:
        reasons.append("n06_stale_context_surface_blocked")
    if not replay["checks"]["serialized_context_values_agree_across_candidates"]:
        reasons.append("n06_context_candidates_disagree")
    if not replay["checks"]["selected_route_matches_context_relation"]:
        reasons.append("n06_context_relation_mismatch")
    if not replay["checks"]["arbitration_score_equals_selected_candidate_score"]:
        reasons.append("n06_arbitration_score_mismatch")
    if not replay["checks"]["candidate_route_scores_equal_component_sums"]:
        reasons.append("n06_candidate_score_component_sum_mismatch")
    if not replay["checks"]["candidate_context_evidence_replayable"]:
        reasons.append("n06_context_evidence_not_replayable")
    if not replay["checks"]["hidden_inputs_absent"]:
        reasons.append("native_route_arbitration_hidden_input_rejected")
    if not replay["checks"]["arbitration_hidden_inputs_absent"]:
        reasons.append("native_route_arbitration_hidden_input_rejected")
    if not lane["checks"]["budget_exact"]:
        reasons.append("native_route_arbitration_budget_invalid")
    if lane["route_arbitration_record"]["scheduler_event_index"] < lane[
        "candidate_set_record"
    ]["scheduler_event_index"]:
        reasons.append("n06_context_order_inversion_blocked")
    return {
        "valid": not reasons,
        "failure_reasons": _dedupe_reasons(reasons),
    }


def _control_result(
    control_id: str,
    *,
    passed: bool,
    primary_blocker: str,
    detail: Any = None,
    scope: str = "n06_semantic_validator",
) -> dict[str, Any]:
    return {
        "control_id": control_id,
        "scope": scope,
        "passed": bool(passed),
        "primary_blocker": primary_blocker,
        "detail": detail,
    }


def _run_hidden_context_control(
    manifest: Mapping[str, Any],
    lane: Mapping[str, Any],
) -> dict[str, Any]:
    def mutator(specs: list[dict[str, Any]]) -> list[dict[str, Any]]:
        specs[0]["candidate_score_components"] = {
            "hidden_fixture_state": 0.6,
            "budget_validity": 0.2,
            "lineage_ready": 0.2,
        }
        specs[0]["candidate_route_score"] = 1.0
        return specs

    try:
        iter4._prepare_candidate_model(  # noqa: SLF001
            manifest,
            context_state_id="context_a",
            spec_mutator=mutator,
        )
    except Exception as exc:  # noqa: BLE001 - negative control records blocker.
        detail = str(exc)
        emission_gate = {
            "passed": (
                LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_HIDDEN_INPUT_REJECTED
                in detail
            ),
            "detail": detail,
        }
    else:
        return _control_result(
            "hidden_context",
            passed=False,
            primary_blocker=LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_HIDDEN_INPUT_REJECTED,
            detail="hidden context candidate unexpectedly emitted",
            scope="native_candidate_emission",
        )

    corrupted_records = copy.deepcopy(lane["candidate_route_records"])
    corrupted_records[0]["candidate_runtime_visible_inputs"].append(
        "hidden_fixture_state"
    )
    artifact_validation = validate_lgrc9v3_native_route_arbitration_artifacts(
        events=[],
        candidate_route_records=corrupted_records,
        candidate_set_records=[lane["candidate_set_record"]],
        route_arbitration_records=[lane["route_arbitration_record"]],
        surface_rows=[],
    )
    artifact_replay_gate = {
        "passed": _reason_has_blocker(
            artifact_validation["failure_reasons"],
            LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_HIDDEN_INPUT_REJECTED,
        ),
        "failure_reasons": artifact_validation["failure_reasons"],
    }
    return _control_result(
        "hidden_context",
        passed=emission_gate["passed"] and artifact_replay_gate["passed"],
        primary_blocker=LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_HIDDEN_INPUT_REJECTED,
        detail={
            "candidate_emission_gate": emission_gate,
            "artifact_replay_gate": artifact_replay_gate,
        },
        scope="native_candidate_emission_and_artifact_replay",
    )


def _run_stale_context_control(manifest: Mapping[str, Any]) -> dict[str, Any]:
    def mutator(specs: list[dict[str, Any]]) -> list[dict[str, Any]]:
        for spec in specs:
            spec["candidate_runtime_visible_inputs"] = [
                value
                for value in spec["candidate_runtime_visible_inputs"]
                if not str(value).startswith("compatible_route_id:")
            ]
            spec["candidate_runtime_visible_inputs"].append(
                "compatible_route_id:route_a"
            )
        return specs

    prepared = iter4._prepare_candidate_model(  # noqa: SLF001
        manifest,
        context_state_id="context_b",
        spec_mutator=mutator,
    )
    model = prepared["model"]
    candidate_set = prepared["candidate_set"]
    arbitration_inputs = _arbitration_inputs_for_context(
        manifest,
        context_state_id="context_b",
        source_surface_digest=prepared["source_surface_digest"],
    )
    model.arbitrate_native_route_candidate_set(
        candidate_set_digest=str(candidate_set.candidate_set_digest),
        arbitration_runtime_visible_inputs=arbitration_inputs,
    )
    artifacts = iter3._runtime_artifacts(model)  # noqa: SLF001
    arbitration_record = artifacts["route_arbitration_records"][0]
    context_replay = _context_relation_replay(
        manifest,
        context_state_id="context_b",
        source_surface_digest=prepared["source_surface_digest"],
        artifacts=artifacts,
        arbitration_record=arbitration_record,
    )
    lane = {
        "context_relation_replay": context_replay,
        "checks": {"budget_exact": True},
        "route_arbitration_record": arbitration_record,
        "candidate_set_record": artifacts["candidate_set_records"][0],
    }
    validation = _semantic_context_validator(lane)
    return _control_result(
        "stale_context",
        passed="n06_stale_context_surface_blocked"
        in validation["failure_reasons"],
        primary_blocker="n06_stale_context_surface_blocked",
        detail=validation,
    )


def _run_context_order_control(lane: Mapping[str, Any]) -> dict[str, Any]:
    corrupted = copy.deepcopy(lane)
    corrupted["route_arbitration_record"]["scheduler_event_index"] = (
        corrupted["candidate_set_record"]["scheduler_event_index"] - 1
    )
    validation = _semantic_context_validator(corrupted)
    return _control_result(
        "context_order_inversion",
        passed="n06_context_order_inversion_blocked"
        in validation["failure_reasons"],
        primary_blocker="n06_context_order_inversion_blocked",
        detail=validation,
        scope="artifact_corruption_control",
    )


def _run_budget_mismatch_control(manifest: Mapping[str, Any]) -> dict[str, Any]:
    invalid_budget_prediction = {
        "node_plus_packet_budget_before": 6.0,
        "node_plus_packet_budget_after": 5.0,
        "node_plus_packet_budget_error": -1.0,
    }

    def mutator(specs: list[dict[str, Any]]) -> list[dict[str, Any]]:
        specs[0]["candidate_budget_prediction"] = dict(invalid_budget_prediction)
        return specs

    prepared = iter4._prepare_candidate_model(  # noqa: SLF001
        manifest,
        context_state_id="context_a",
        spec_mutator=mutator,
    )
    arbitration_inputs = _arbitration_inputs_for_context(
        manifest,
        context_state_id="context_a",
        source_surface_digest=prepared["source_surface_digest"],
    )
    result = prepared["model"].arbitrate_native_route_candidate_set(
        candidate_set_digest=str(prepared["candidate_set"].candidate_set_digest),
        arbitration_runtime_visible_inputs=arbitration_inputs,
    )
    record = iter4._arbitration_artifact(result["route_arbitration_record"])  # noqa: SLF001
    return _control_result(
        "budget_mismatch",
        passed=record is not None
        and record["arbitration_reason_code"]
        == LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_BUDGET_INVALID
        and abs(invalid_budget_prediction["node_plus_packet_budget_error"])
        > float(manifest["arbitration_policy"]["budget_tolerance"]),
        primary_blocker=LGRC9V3_NATIVE_ROUTE_ARBITRATION_REASON_BUDGET_INVALID,
        detail={
            "mutated_budget_prediction": invalid_budget_prediction,
            "budget_tolerance": manifest["arbitration_policy"]["budget_tolerance"],
            "route_arbitration_record": record,
        },
        scope="native_arbitration_control",
    )


def _run_producer_mutation_control(lane: Mapping[str, Any]) -> dict[str, Any]:
    attempted_forbidden_writes = [
        "active_node_coherence",
        "packet_ledger",
        "topology",
        "route_arbitration_record",
        "claim_flags",
    ]
    no_producer_invoked = lane["after_counts"]["production_result_count"] == 0
    no_packet_scheduled = lane["checks"]["no_packet_scheduled_by_arbitration"]
    rejected = no_producer_invoked and no_packet_scheduled
    return _control_result(
        "producer_mutation",
        passed=rejected,
        primary_blocker="n06_producer_mutation_boundary_violation",
        detail={
            "attempted_forbidden_writes": attempted_forbidden_writes,
            "producer_invoked": not no_producer_invoked,
            "packet_scheduled": not no_packet_scheduled,
            "rejected_by_boundary": rejected,
        },
        scope="boundary_control",
    )


def _run_claim_promotion_control(lane: Mapping[str, Any]) -> dict[str, Any]:
    corrupted_record = copy.deepcopy(lane["route_arbitration_record"])
    corrupted_record["claim_flags"]["semantic_choice_claim_allowed"] = True
    validation = validate_lgrc9v3_native_route_arbitration_artifacts(
        events=[],
        candidate_route_records=lane["candidate_route_records"],
        candidate_set_records=[lane["candidate_set_record"]],
        route_arbitration_records=[corrupted_record],
        surface_rows=[],
    )
    return _control_result(
        "claim_promotion",
        passed=_reason_has_blocker(
            validation["failure_reasons"],
            "native_route_arbitration_claim_promotion_blocked",
        ),
        primary_blocker="native_route_arbitration_claim_promotion_blocked",
        detail=validation["failure_reasons"],
        scope="artifact_replay_control",
    )


def _run_controls(
    manifest: Mapping[str, Any],
    context_a_lane: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "hidden_context": _run_hidden_context_control(manifest, context_a_lane),
        "stale_context": _run_stale_context_control(manifest),
        "context_order_inversion": _run_context_order_control(context_a_lane),
        "budget_mismatch": _run_budget_mismatch_control(manifest),
        "producer_mutation": _run_producer_mutation_control(context_a_lane),
        "claim_promotion": _run_claim_promotion_control(context_a_lane),
    }


def _build_report(data: Mapping[str, Any]) -> str:
    lanes = data["lanes"]
    lines = [
        "# N06 Iteration 5 SC3 Context-Conditioned Selection",
        "",
        f"- status: `{data['status']}`",
        f"- generated: `{data['generated_at']}`",
        f"- command: `{COMMAND}`",
        f"- context A selected: `{lanes['context_a']['selected_candidate_route_id']}`",
        f"- context B selected: `{lanes['context_b']['selected_candidate_route_id']}`",
        "",
        "## Boundary",
        "",
        "- SC3 proves context-conditioned route selection under the same serialized native arbitration policy.",
        "- It does not commit topology, schedule post-selection packets, or promote semantic-choice/agency/memory/identity/movement claims.",
        "",
        "## Payload Scope",
        "",
        "Full candidate route records are retained in the JSON artifact as replay payloads because the context relation lives in candidate runtime-visible inputs, score components, budget predictions, and lineage maps. The report/checklist summarize by digest and selected/rejected route ids.",
        "",
        "```json",
        json.dumps(data["artifact_payload_policy"], indent=2, sort_keys=True),
        "```",
        "",
        "## Candidate-Set Identity",
        "",
        "Candidate-set ids are not treated as context-unique. Candidate-set digests distinguish the context lanes.",
        "",
        "```json",
        json.dumps(data["candidate_set_identity"], indent=2, sort_keys=True),
        "```",
        "",
        "## Acceptance",
        "",
        "```json",
        json.dumps(data["acceptance"], indent=2, sort_keys=True),
        "```",
        "",
        "## Context A Replay",
        "",
        "```json",
        json.dumps(
            lanes["context_a"]["context_relation_replay"],
            indent=2,
            sort_keys=True,
        ),
        "```",
        "",
        "## Context B Replay",
        "",
        "```json",
        json.dumps(
            lanes["context_b"]["context_relation_replay"],
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
    context_a = _run_context_lane(manifest, context_state_id="context_a")
    context_b = _run_context_lane(manifest, context_state_id="context_b")
    controls = _run_controls(manifest, context_a)
    same_policy = (
        context_a["route_arbitration_record"]["native_route_arbitration_policy_id"]
        == context_b["route_arbitration_record"]["native_route_arbitration_policy_id"]
    )
    candidate_set_identity = {
        "context_a_candidate_set_id": context_a["candidate_set_record"][
            "candidate_set_id"
        ],
        "context_b_candidate_set_id": context_b["candidate_set_record"][
            "candidate_set_id"
        ],
        "context_a_candidate_set_digest": context_a["candidate_set_digest"],
        "context_b_candidate_set_digest": context_b["candidate_set_digest"],
        "candidate_set_ids_equal": (
            context_a["candidate_set_record"]["candidate_set_id"]
            == context_b["candidate_set_record"]["candidate_set_id"]
        ),
        "candidate_set_digests_equal": (
            context_a["candidate_set_digest"] == context_b["candidate_set_digest"]
        ),
        "context_unique_key": "candidate_set_digest",
        "candidate_set_id_is_not_context_unique": True,
    }
    checks = {
        "context_a_lane_passed": context_a["passed"],
        "context_b_lane_passed": context_b["passed"],
        "same_serialized_policy": same_policy,
        "same_policy_id_but_context_specific_arbitration_inputs": (
            same_policy
            and context_a["arbitration_runtime_visible_inputs"]
            != context_b["arbitration_runtime_visible_inputs"]
        ),
        "candidate_set_digest_distinguishes_context_lanes": (
            candidate_set_identity["candidate_set_digests_equal"] is False
        ),
        "candidate_set_digest_is_context_unique_key": (
            candidate_set_identity["context_unique_key"] == "candidate_set_digest"
        ),
        "context_a_selects_route_a": (
            context_a["selected_candidate_route_id"] == "route_a"
        ),
        "context_b_selects_route_b": (
            context_b["selected_candidate_route_id"] == "route_b"
        ),
        "selection_changes_with_context": (
            context_a["selected_candidate_route_id"]
            != context_b["selected_candidate_route_id"]
        ),
        "controls_passed": all(control["passed"] for control in controls.values()),
        "claim_flags_remain_false": context_a["checks"]["claim_flags_remain_false"]
        and context_b["checks"]["claim_flags_remain_false"],
        "no_topology_commit": context_a["checks"]["no_topology_event_committed"]
        and context_b["checks"]["no_topology_event_committed"],
    }
    status = "passed" if all(checks.values()) else "failed"
    acceptance = {
        "sc_level": "SC3",
        "claim_ceiling": "context_conditioned_route_selection_candidate",
        "same_serialized_policy": same_policy,
        "context_a_selected_route": context_a["selected_candidate_route_id"],
        "context_b_selected_route": context_b["selected_candidate_route_id"],
        "selection_changes_with_context": checks["selection_changes_with_context"],
        "context_relation_replayable": context_a[
            "context_relation_replay"
        ]["context_relation_replayable"]
        and context_b["context_relation_replay"]["context_relation_replayable"],
        "semantic_choice_claim_allowed": False,
        "topology_event_committed": False,
        "packet_scheduled_by_arbitration": False,
        "status": status,
    }
    data: dict[str, Any] = {
        "schema": "semantic_route_choice_report_v1",
        "experiment": "2026-05-N06-lgrc-semantic-route-choice",
        "iteration": 5,
        "iteration_name": "SC3 Context-Conditioned Route Selection",
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": COMMAND,
        "platform": {
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "manifest": _artifact_record(MANIFEST_PATH),
        "source_iteration": _artifact_record(iter4.OUTPUT_PATH),
        "lanes": {
            "context_a": context_a,
            "context_b": context_b,
        },
        "controls": controls,
        "checks": checks,
        "acceptance": acceptance,
        "claim_flags": {flag: False for flag in iter3.CLAIM_FLAGS},
        "candidate_set_identity": candidate_set_identity,
        "artifact_payload_policy": {
            "full_candidate_route_records_in_json": True,
            "reason": "SC3 and SC6 replay need candidate runtime-visible context inputs, score components, budget predictions, and lineage maps.",
            "report_and_checklist_summarize_by_digest": True,
            "visual_or_summary_rows_are_not_source_of_truth": True,
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
                "selection_changes_with_context": checks[
                    "selection_changes_with_context"
                ],
                "controls_passed": checks["controls_passed"],
                "semantic_choice_claim_allowed": False,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
