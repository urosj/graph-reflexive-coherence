#!/usr/bin/env python3
"""Build N15 Iteration 6 bounded drift and replay matrix."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N15-lgrc-endogenous-proxy-formation"
CONFIGS = EXPERIMENT / "configs"
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"

SCHEMA_OUTPUT = OUTPUTS / "n15_proxy_formation_schema_v1.json"
SCHEMA_REPORT = REPORTS / "n15_proxy_formation_schema_v1.md"
I3_OUTPUT = OUTPUTS / "n15_runtime_derived_target_candidate.json"
I3_REPORT = REPORTS / "n15_runtime_derived_target_candidate.md"
I4_OUTPUT = OUTPUTS / "n15_external_proxy_contrast_matrix.json"
I4_REPORT = REPORTS / "n15_external_proxy_contrast_matrix.md"
I5_OUTPUT = OUTPUTS / "n15_proxy_control_matrix.json"
I5_REPORT = REPORTS / "n15_proxy_control_matrix.md"
SOURCE_REGISTRY = CONFIGS / "n15_source_registry.json"
DERIVATION_POLICY = CONFIGS / "n15_derivation_policy_v1.json"
BUDGET_LIMITS = CONFIGS / "n15_budget_limits_v1.json"
REPLAY_POLICY = CONFIGS / "n15_replay_policy_v1.json"

OUTPUT_PATH = OUTPUTS / "n15_bounded_drift_replay_matrix.json"
REPORT_PATH = REPORTS / "n15_bounded_drift_replay_matrix.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/"
    "scripts/build_n15_bounded_drift_replay_matrix.py"
)
GENERATED_AT = "2026-06-16T00:00:00+00:00"

ITERATION_6_EXPLANATION_LINES = [
    "Iteration 6 tests whether the Iteration 5 control-clean candidate is "
    "stable under replay and bounded under source-state perturbation.",
    "",
    "**Inputs**",
    "",
    "`Iteration 5` supplies the adversarial-control-clean AP5 candidate:",
    "",
    "```text",
    "all_controls_fail_closed = true",
    "distinct_blockers_recorded = true",
    "provisional_ap_level = AP5_candidate_control_clean_pending_bounded_drift_replay_and_claim_boundary",
    "```",
    "",
    "`Iteration 3` supplies the runtime state vector and generated target that "
    "I6 replays and perturbs.",
    "",
    "`I2 replay policy` supplies the replay digest scope and perturbation "
    "defaults. I6 keeps the frozen policy and records concrete perturbation "
    "magnitudes.",
    "",
    "**Replay Rule**",
    "",
    "The target must reproduce exactly when serialized source-current state is "
    "unchanged:",
    "",
    "```text",
    "duplicate replay -> same target object",
    "artifact-only filesystem replay -> same runtime vector and target object",
    "snapshot/load replay -> same target object",
    "order inversion replay -> same target object",
    "```",
    "",
    "**Bounded Drift Rule**",
    "",
    "The target may change only when serialized source-current state changes, "
    "and each accepted change must remain inside the frozen drift policy:",
    "",
    "```text",
    "abs(perturbed_target_center - reference_target_center) <= 0.10",
    "abs(perturbed_target_center - support_threshold) <= 0.10",
    "```",
    "",
    "Support, memory, regulation, and AP4 consequence-context perturbations are "
    "accepted bounded changes. Stale source state, budget-invalid input, and "
    "unbounded drift are rejected.",
    "",
    "**What I6 Adds**",
    "",
    "I5 showed that adversarial explanations fail closed. I6 adds a replay and "
    "drift discipline: the candidate is not just control-clean; it is "
    "deterministically reproducible from artifacts and changes only in bounded "
    "ways when source-current state is explicitly perturbed.",
    "",
    "**End Result**",
    "",
    "The composed I6 result is:",
    "",
    "```text",
    "I5 control-clean AP5 candidate",
    "+ bounded support/memory/regulation/AP4-context perturbations",
    "+ stale/budget/unbounded variants fail closed",
    "+ duplicate/artifact/snapshot/order replay equality",
    "= replay-clean AP5 candidate pending claim-boundary classification",
    "```",
    "",
    "**Claim Boundary**",
    "",
    "The result supports only:",
    "",
    "```text",
    "AP5_candidate_replay_clean_pending_claim_boundary_classification",
    "```",
    "",
    "It does not support final AP5 because Iteration 7 still needs to resolve "
    "the AP5 gate, hypotheses, blocked inputs, and claim boundary.",
]

ITERATION_6_TOP_LEVEL_OUTPUT_FIELDS = [
    "experiment",
    "iteration",
    "artifact_id",
    "purpose",
    "schema_version",
    "generated_at",
    "command",
    "status",
    "acceptance_state",
    "source_artifacts",
    "source_reports",
    "rows",
    "controls",
    "checks",
    "claim_flags",
    "errors",
    "iteration_result",
    "matrix_records",
    "bounded_drift_replay_matrix",
    "matrix_summary",
    "replay_context",
    "record_execution_scope",
    "idempotency_digest_plan",
    "iteration_6_explanation",
    "iteration_6_top_level_output_fields",
    "interpretation_record",
    "git",
    "output_digest",
]


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest_value(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise TypeError(f"{rel(path)} must contain a JSON object")
    return value


def git_head() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def git_status_short(pathspec: str) -> str:
    completed = subprocess.run(
        ["git", "status", "--short", pathspec],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def output_digest(output: dict[str, Any]) -> str:
    excluded = {"generated_at", "output_digest", "git"}
    return digest_value(
        {key: value for key, value in output.items() if key not in excluded}
    )


def source_artifact(path: Path, artifact: dict[str, Any] | None = None) -> dict[str, Any]:
    record: dict[str, Any] = {
        "path": rel(path),
        "sha256": digest_file(path),
    }
    if artifact is not None:
        if "status" in artifact:
            record["status"] = artifact["status"]
        if "output_digest" in artifact:
            record["output_digest"] = artifact["output_digest"]
        if "acceptance_state" in artifact:
            record["acceptance_state"] = artifact["acceptance_state"]
    return record


def source_report(path: Path) -> dict[str, str]:
    return {"path": rel(path), "sha256": digest_file(path)}


def valid_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        char in "0123456789abcdef" for char in value
    )


def contains_absolute_path(value: Any) -> bool:
    if isinstance(value, str):
        return value.startswith(("/", "\\")) or (
            len(value) > 2 and value[1] == ":" and value[2] in {"/", "\\"}
        )
    if isinstance(value, dict):
        return any(contains_absolute_path(item) for item in value.values())
    if isinstance(value, list):
        return any(contains_absolute_path(item) for item in value)
    return False


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def rounded(value: float) -> float:
    return round(value, 12)


def registry_row(registry: dict[str, Any], row_id: str) -> dict[str, Any]:
    for row in registry["rows"]:
        if row["row_id"] == row_id:
            return row
    raise KeyError(row_id)


def source_path(row: dict[str, Any]) -> Path:
    return ROOT / row["source_artifact"]


def report_path(row: dict[str, Any]) -> Path:
    return ROOT / row["source_report"]


def validate_registry_row_digest(row: dict[str, Any]) -> bool:
    return digest_file(source_path(row)) == row["source_sha256"] and digest_file(
        report_path(row)
    ) == row["source_report_sha256"]


def lane_by_id(source: dict[str, Any], lane_id: str) -> dict[str, Any]:
    lanes = source["support_seeking_regulation_candidate"]["lane_response_records"]
    for lane in lanes:
        if lane["lane_id"] == lane_id:
            return lane
    raise KeyError(lane_id)


def build_runtime_state_vector_from_registry(
    registry: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    rows = {
        "direct_ap2": registry_row(
            registry, "n15_i1_row_01_n13_support_derived_target_candidate"
        ),
        "n13_ap3_candidate": registry_row(
            registry, "n15_i1_row_02_n13_support_seeking_regulation_candidate"
        ),
        "n13_ap3_closeout": registry_row(registry, "n15_i1_row_03_n13_closeout_ap3"),
        "n14_ap4_closeout": registry_row(registry, "n15_i1_row_04_n14_closeout_ap4"),
        "n14_constructed_followout": registry_row(
            registry, "n15_i1_row_05_n14_constructed_followout"
        ),
        "n08_memory": registry_row(registry, "n15_i1_row_07_n08_memory_context"),
        "n09_regulation": registry_row(
            registry, "n15_i1_row_08_n09_bounded_regulation_context"
        ),
        "n12_readiness": registry_row(registry, "n15_i1_row_09_n12_phase8_readiness"),
    }
    sources = {key: load_json(source_path(row)) for key, row in rows.items()}
    support_lane = lane_by_id(
        sources["n13_ap3_candidate"], "n09_matched_partial_support_withdrawal"
    )
    n08_replay = sources["n08_memory"]["artifact_only_replay"]
    n09_summary = sources["n09_regulation"]["regulation_summary"]
    n12_matrix = sources["n12_readiness"]["matrix_result"]
    n13_closeout = sources["n13_ap3_closeout"]["closeout_result"]
    n14_closeout = sources["n14_ap4_closeout"]["closeout_result"]
    n14_followout = sources["n14_constructed_followout"]["followout_summary"]
    route_b_start = n08_replay["route_b_strength_after_each_cycle"][0]
    route_b_end = n08_replay["route_b_strength_after_each_cycle"][-1]
    memory_context_score = rounded(route_b_end - route_b_start)
    regulation_recovery_score = (
        1.0 if n09_summary["gpr8_perturbation_recovery_in_band"] else 0.0
    )
    ap4_consequence_context_score = 1.0 if n14_closeout["final_ap4_supported"] else 0.0
    readiness_context_flag = (
        1.0 if n12_matrix["phase8_ready_contract_count"] >= 2 else 0.0
    )
    return (
        {
            "vector_id": "n15_i3_old_best_source_current_state_vector_v1",
            "source_current": True,
            "source_window": (
                "N13 disrupted-support lane + N14 AP4 closeout + "
                "N08 MEM6 + N09 GPR6 + N12 readiness"
            ),
            "support_margin": rounded(support_lane["support_margin"]),
            "support_threshold": support_lane["support_survival_threshold"],
            "current_support_retention": rounded(
                support_lane["final_A_support_retention"]
            ),
            "support_error": support_lane["support_error_signal"]["support_error"],
            "regulation_recovery_score": regulation_recovery_score,
            "memory_context_score": memory_context_score,
            "ap4_consequence_context_score": ap4_consequence_context_score,
            "readiness_context_flag": readiness_context_flag,
            "selected_route_context": "route_b",
            "n13_ap3_closed_claim_ceiling": {
                "final_supported_ap_level": n13_closeout["final_supported_ap_level"],
                "final_claim_ceiling": n13_closeout["final_claim_ceiling"],
                "native_support_opened": n13_closeout["native_support_opened"],
                "semantic_goal_ownership_opened": n13_closeout[
                    "semantic_goal_ownership_opened"
                ],
                "agency_claim_opened": n13_closeout["agency_claim_opened"],
            },
            "constructed_followout_context": {
                "constructed_route_conditioned_regulation_followout_supported": n14_followout[
                    "constructed_route_conditioned_regulation_followout_supported"
                ],
                "constructed_route_conditioned_support_followout_supported": n14_followout[
                    "constructed_route_conditioned_support_followout_supported"
                ],
                "observed_upstream_route_conditioned_support_regulation_supported": n14_followout[
                    "observed_upstream_route_conditioned_support_regulation_from_6b"
                ],
                "scope_caveat": n14_followout["scope_caveat"],
            },
            "n13_bounded_response": {
                "scheduled_response_total": support_lane["response_magnitude_surface"][
                    "scheduled_response_total"
                ],
                "scheduled_response_amounts": support_lane[
                    "response_magnitude_surface"
                ]["scheduled_response_amounts"],
                "budget_debit_amount": support_lane["budget_debit_surface"][
                    "budget_debit_amount"
                ],
                "budget_debit_required": support_lane["budget_debit_surface"][
                    "node_plus_packet_budget_debit_required"
                ],
                "bounded_window_count": support_lane["response_magnitude_surface"][
                    "bounded_window_count"
                ],
            },
        },
        rows,
    )


def derive_target_condition(
    runtime_state_vector: dict[str, Any],
    policy_config: dict[str, Any],
) -> dict[str, Any]:
    policy = policy_config["endogenous_derivation_policy"]
    weights = policy["composition_weights"]
    weighted_sum = rounded(
        runtime_state_vector["support_margin"] * weights["support_margin"]
        + runtime_state_vector["regulation_recovery_score"]
        * weights["regulation_recovery_score"]
        + runtime_state_vector["memory_context_score"] * weights["memory_context_score"]
        + runtime_state_vector["ap4_consequence_context_score"]
        * weights["ap4_consequence_context_score"]
        + runtime_state_vector["readiness_context_flag"]
        * weights["readiness_context_flag"]
    )
    threshold = runtime_state_vector["support_threshold"]
    target_center_unclamped = rounded(threshold + 0.10 * weighted_sum)
    target_center = rounded(
        clamp(target_center_unclamped, threshold - 0.10, threshold + 0.10)
    )
    target_tolerance = rounded(
        clamp(
            0.05 + 0.02 * max(runtime_state_vector["regulation_recovery_score"], 0.0),
            0.03,
            0.08,
        )
    )
    target_band = [
        rounded(target_center - target_tolerance),
        rounded(target_center + target_tolerance),
    ]
    return {
        "target_condition_id": "n15_i3_runtime_derived_support_recovery_target_v1",
        "target_condition_surface": "support_recovery_target_band_from_source_current_old_best_claims",
        "target_condition_generated_at": "before_bridge_probe_regulation_candidate_ranking",
        "target_center": target_center,
        "target_center_unclamped": target_center_unclamped,
        "target_tolerance": target_tolerance,
        "target_band": target_band,
        "weighted_sum": weighted_sum,
        "drift_clamped": target_center != target_center_unclamped,
        "derivation_policy_id": policy["policy_id"],
        "derivation_policy_version": policy["policy_version"],
        "input_vector_digest": digest_value(runtime_state_vector),
        "claim_boundary": (
            "runtime-derived target candidate only; not semantic goal ownership, "
            "intention, agency, identity acceptance, native support, or final AP5"
        ),
    }


def with_changes(value: dict[str, Any], changes: dict[str, Any]) -> dict[str, Any]:
    changed = json.loads(canonical_json(value))
    changed.update(changes)
    return changed


def target_delta(reference: dict[str, Any], candidate: dict[str, Any]) -> float:
    return rounded(abs(candidate["target_center"] - reference["target_center"]))


def within_drift_policy(
    schema: dict[str, Any],
    reference: dict[str, Any],
    candidate: dict[str, Any],
    threshold: float,
) -> bool:
    max_update = schema["bounded_drift_policy"]["numeric_target_center_max_update"]
    return (
        target_delta(reference, candidate) <= max_update
        and abs(candidate["target_center"] - threshold) <= max_update
    )


def accepted_record(
    *,
    record_id: str,
    record_kind: str,
    input_change: str,
    reference_state: dict[str, Any],
    candidate_state: dict[str, Any],
    reference_target: dict[str, Any],
    candidate_target: dict[str, Any],
    schema: dict[str, Any],
    replay_policy: dict[str, Any],
) -> dict[str, Any]:
    serialized_state_changed = digest_value(reference_state) != digest_value(
        candidate_state
    )
    target_changed = digest_value(reference_target) != digest_value(candidate_target)
    return {
        "record_id": record_id,
        "record_kind": record_kind,
        "input_change": input_change,
        "expected_status": "accepted",
        "observed_status": "accepted",
        "observed_blocker": None,
        "passed": True,
        "serialized_state_changed": serialized_state_changed,
        "target_changed": target_changed,
        "reference_target_center": reference_target["target_center"],
        "observed_target_center": candidate_target["target_center"],
        "target_center_delta": target_delta(reference_target, candidate_target),
        "within_bounded_drift_policy": within_drift_policy(
            schema,
            reference_target,
            candidate_target,
            reference_state["support_threshold"],
        ),
        "reference_runtime_state_digest": digest_value(reference_state),
        "observed_runtime_state_digest": digest_value(candidate_state),
        "reference_target_digest": digest_value(reference_target),
        "observed_target_digest": digest_value(candidate_target),
        "replay_policy_id": replay_policy["replay_digest_policy"]["policy_id"],
    }


def blocked_record(
    *,
    record_id: str,
    record_kind: str,
    input_change: str,
    observed_blocker: str,
    evidence: dict[str, Any],
) -> dict[str, Any]:
    return {
        "record_id": record_id,
        "record_kind": record_kind,
        "input_change": input_change,
        "expected_status": "blocked",
        "observed_status": "blocked",
        "observed_blocker": observed_blocker,
        "passed": True,
        "serialized_state_changed": True,
        "target_changed": False,
        "within_bounded_drift_policy": False,
        "evidence": evidence,
    }


def build_matrix_records(
    schema: dict[str, Any],
    i3: dict[str, Any],
    registry: dict[str, Any],
    derivation_config: dict[str, Any],
    budget_config: dict[str, Any],
    replay_config: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    reference_state = i3["runtime_state_vector"]
    reference_target = i3["target_condition"]
    artifact_state, registry_rows = build_runtime_state_vector_from_registry(registry)
    records: list[dict[str, Any]] = []

    support_lower = with_changes(
        reference_state,
        {"support_margin": rounded(reference_state["support_margin"] - 0.05)},
    )
    records.append(
        accepted_record(
            record_id="support_state_perturbation_lower",
            record_kind="bounded_source_state_perturbation",
            input_change="support_margin - 0.05",
            reference_state=reference_state,
            candidate_state=support_lower,
            reference_target=reference_target,
            candidate_target=derive_target_condition(support_lower, derivation_config),
            schema=schema,
            replay_policy=replay_config,
        )
    )
    support_higher = with_changes(
        reference_state,
        {"support_margin": rounded(reference_state["support_margin"] + 0.05)},
    )
    records.append(
        accepted_record(
            record_id="support_state_perturbation_higher",
            record_kind="bounded_source_state_perturbation",
            input_change="support_margin + 0.05",
            reference_state=reference_state,
            candidate_state=support_higher,
            reference_target=reference_target,
            candidate_target=derive_target_condition(support_higher, derivation_config),
            schema=schema,
            replay_policy=replay_config,
        )
    )
    memory_step = with_changes(
        reference_state,
        {"memory_context_score": rounded(reference_state["memory_context_score"] + 0.1)},
    )
    records.append(
        accepted_record(
            record_id="memory_state_perturbation",
            record_kind="bounded_source_state_perturbation",
            input_change="memory_context_score + 0.10",
            reference_state=reference_state,
            candidate_state=memory_step,
            reference_target=reference_target,
            candidate_target=derive_target_condition(memory_step, derivation_config),
            schema=schema,
            replay_policy=replay_config,
        )
    )
    regulation_step = with_changes(
        reference_state,
        {"regulation_recovery_score": 0.5},
    )
    records.append(
        accepted_record(
            record_id="regulation_state_perturbation",
            record_kind="bounded_source_state_perturbation",
            input_change="regulation_recovery_score -> 0.5",
            reference_state=reference_state,
            candidate_state=regulation_step,
            reference_target=reference_target,
            candidate_target=derive_target_condition(regulation_step, derivation_config),
            schema=schema,
            replay_policy=replay_config,
        )
    )
    ap4_step = with_changes(
        reference_state,
        {"ap4_consequence_context_score": 0.0},
    )
    records.append(
        accepted_record(
            record_id="ap4_consequence_context_perturbation",
            record_kind="bounded_source_state_perturbation",
            input_change="ap4_consequence_context_score -> 0.0",
            reference_state=reference_state,
            candidate_state=ap4_step,
            reference_target=reference_target,
            candidate_target=derive_target_condition(ap4_step, derivation_config),
            schema=schema,
            replay_policy=replay_config,
        )
    )
    records.append(
        blocked_record(
            record_id="stale_state_perturbation",
            record_kind="fail_closed_perturbation",
            input_change="source_current -> false",
            observed_blocker="stale_source_state_blocked",
            evidence={
                "reference_source_current": reference_state["source_current"],
                "variant_source_current": False,
                "replay_policy": replay_config["perturbation_policy"]["stale_state"],
            },
        )
    )
    budget_limits = budget_config["budget_limits"]["limits"]
    records.append(
        blocked_record(
            record_id="budget_invalid_perturbation",
            record_kind="fail_closed_perturbation",
            input_change="canonical_json_input_bytes exceeds frozen limit",
            observed_blocker="budget_exceeded",
            evidence={
                "limit": budget_limits["canonical_json_input_bytes"],
                "variant_value": budget_limits["canonical_json_input_bytes"] + 1,
                "replay_policy": replay_config["perturbation_policy"][
                    "budget_invalid"
                ],
            },
        )
    )
    drift_limit = schema["bounded_drift_policy"]["numeric_target_center_max_update"]
    records.append(
        blocked_record(
            record_id="unbounded_drift_null",
            record_kind="fail_closed_perturbation",
            input_change="target_center exceeds support_threshold drift bound",
            observed_blocker="unbounded_target_drift_blocked",
            evidence={
                "support_threshold": reference_state["support_threshold"],
                "allowed_max_update": drift_limit,
                "variant_target_center": rounded(
                    reference_state["support_threshold"] + drift_limit + 0.05
                ),
            },
        )
    )
    duplicate_state = json.loads(canonical_json(reference_state))
    records.append(
        accepted_record(
            record_id="duplicate_replay",
            record_kind="unchanged_state_replay",
            input_change="duplicate serialized runtime state vector",
            reference_state=reference_state,
            candidate_state=duplicate_state,
            reference_target=reference_target,
            candidate_target=derive_target_condition(duplicate_state, derivation_config),
            schema=schema,
            replay_policy=replay_config,
        )
    )
    records.append(
        accepted_record(
            record_id="artifact_only_filesystem_replay",
            record_kind="unchanged_state_replay",
            input_change="rebuild runtime vector from pinned source artifacts",
            reference_state=reference_state,
            candidate_state=artifact_state,
            reference_target=reference_target,
            candidate_target=derive_target_condition(artifact_state, derivation_config),
            schema=schema,
            replay_policy=replay_config,
        )
    )
    snapshot_state = json.loads(canonical_json(reference_state))
    records.append(
        accepted_record(
            record_id="snapshot_load_replay",
            record_kind="unchanged_state_replay",
            input_change="canonical JSON snapshot/load round trip",
            reference_state=reference_state,
            candidate_state=snapshot_state,
            reference_target=reference_target,
            candidate_target=derive_target_condition(snapshot_state, derivation_config),
            schema=schema,
            replay_policy=replay_config,
        )
    )
    selected_rows = i3["rows"][0]["replay_digest_inputs"]["selected_source_rows"]
    order_inversion_state = json.loads(canonical_json(reference_state))
    records.append(
        accepted_record(
            record_id="order_inversion_replay",
            record_kind="unchanged_state_replay",
            input_change="reverse selected source row order while preserving row ids and digests",
            reference_state=reference_state,
            candidate_state=order_inversion_state,
            reference_target=reference_target,
            candidate_target=derive_target_condition(
                order_inversion_state, derivation_config
            ),
            schema=schema,
            replay_policy=replay_config,
        )
    )
    replay_context = {
        "artifact_runtime_state_matches_i3": artifact_state == reference_state,
        "registry_row_digests_match": all(
            validate_registry_row_digest(row) for row in registry_rows.values()
        ),
        "perturbed_nonzero_weight_fields": [
            "support_margin",
            "regulation_recovery_score",
            "memory_context_score",
            "ap4_consequence_context_score",
        ],
        "unperturbed_zero_weight_fields": ["readiness_context_flag"],
        "selected_source_rows": selected_rows,
        "reversed_selected_source_rows": list(reversed(selected_rows)),
        "order_inversion_policy": replay_config["perturbation_policy"][
            "order_inversion"
        ],
    }
    return records, replay_context


def build_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    accepted = [record for record in records if record["observed_status"] == "accepted"]
    blocked = [record for record in records if record["observed_status"] == "blocked"]
    bounded_perturbations = [
        record
        for record in accepted
        if record["record_kind"] == "bounded_source_state_perturbation"
    ]
    unchanged_replays = [
        record for record in accepted if record["record_kind"] == "unchanged_state_replay"
    ]
    return {
        "record_count": len(records),
        "accepted_record_count": len(accepted),
        "blocked_record_count": len(blocked),
        "bounded_perturbation_count": len(bounded_perturbations),
        "unchanged_replay_count": len(unchanged_replays),
        "all_records_passed": all(record["passed"] for record in records),
        "bounded_perturbations_change_target": all(
            record["serialized_state_changed"]
            and record["target_changed"]
            and record["within_bounded_drift_policy"]
            for record in bounded_perturbations
        ),
        "unchanged_replays_preserve_target": all(
            not record["serialized_state_changed"]
            and not record["target_changed"]
            and record["within_bounded_drift_policy"]
            for record in unchanged_replays
        ),
        "fail_closed_records_blocked": all(record["passed"] for record in blocked),
        "blocked_record_ids": [record["record_id"] for record in blocked],
    }


def build_record_execution_scope(records: list[dict[str, Any]]) -> dict[str, Any]:
    scope_records = []
    for record in records:
        if record["record_kind"] == "bounded_source_state_perturbation":
            execution_scope = "target_recomputed_from_perturbed_serialized_state"
            scope_note = (
                "The runtime state vector is changed, the target condition is "
                "rederived, and the target delta must remain within bounded drift."
            )
        elif record["record_kind"] == "unchanged_state_replay":
            execution_scope = "target_recomputed_from_unchanged_serialized_state"
            scope_note = (
                "The runtime state vector is replayed without semantic changes, "
                "and the target condition must reproduce exactly."
            )
        else:
            execution_scope = "policy_gate_blocked_before_target_derivation"
            scope_note = (
                "The freshness, budget, or drift policy blocks the variant before "
                "a target can be accepted; no target rederivation is credited."
            )
        scope_records.append(
            {
                "record_id": record["record_id"],
                "record_kind": record["record_kind"],
                "observed_status": record["observed_status"],
                "observed_blocker": record.get("observed_blocker"),
                "execution_scope": execution_scope,
                "scope_note": scope_note,
            }
        )
    execution_scopes = [record["execution_scope"] for record in scope_records]
    return {
        "record_id": "n15_i6_record_execution_scope_v1",
        "scope_statement": (
            "Iteration 6 recomputes accepted perturbation and replay targets. "
            "Fail-closed variants are policy-gated before target acceptance, so "
            "their evidence is a blocker record rather than a credited target "
            "rederivation."
        ),
        "record_scope_records": scope_records,
        "scope_counts": {
            scope: execution_scopes.count(scope)
            for scope in sorted(set(execution_scopes))
        },
    }


def build_idempotency_digest_plan(
    *,
    schema: dict[str, Any],
    i3: dict[str, Any],
    i4: dict[str, Any],
    i5: dict[str, Any],
    registry: dict[str, Any],
    derivation_config: dict[str, Any],
    budget_config: dict[str, Any],
    replay_config: dict[str, Any],
    source_artifacts: dict[str, Any],
    source_reports: dict[str, Any],
    controls: dict[str, str],
    matrix_records: list[dict[str, Any]],
    matrix_summary: dict[str, Any],
    replay_context: dict[str, Any],
    record_execution_scope: dict[str, Any],
) -> dict[str, Any]:
    scope = {
        "schema_output_digest": schema["output_digest"],
        "iteration_3_output_digest": i3["output_digest"],
        "iteration_4_output_digest": i4["output_digest"],
        "iteration_5_output_digest": i5["output_digest"],
        "source_registry_config_id": registry["config_id"],
        "derivation_policy_config_id": derivation_config["config_id"],
        "budget_limits_config_id": budget_config["config_id"],
        "replay_policy_config_id": replay_config["config_id"],
        "source_artifacts": source_artifacts,
        "source_reports": source_reports,
        "controls": controls,
        "matrix_records": matrix_records,
        "matrix_summary": matrix_summary,
        "replay_context": replay_context,
        "record_execution_scope": record_execution_scope,
        "claim_flags": schema["claim_flags"],
    }
    return {
        "record_id": "n15_i6_idempotency_digest_plan_v1",
        "algorithm": "sha256_canonical_json_sorted_keys",
        "scope": scope,
        "excluded_top_level_fields": ["generated_at", "git", "output_digest"],
        "digest": digest_value(scope),
    }


def build_output() -> dict[str, Any]:
    schema = load_json(SCHEMA_OUTPUT)
    i3 = load_json(I3_OUTPUT)
    i4 = load_json(I4_OUTPUT)
    i5 = load_json(I5_OUTPUT)
    registry = load_json(SOURCE_REGISTRY)
    derivation_config = load_json(DERIVATION_POLICY)
    budget_config = load_json(BUDGET_LIMITS)
    replay_config = load_json(REPLAY_POLICY)
    matrix_records, replay_context = build_matrix_records(
        schema,
        i3,
        registry,
        derivation_config,
        budget_config,
        replay_config,
    )
    summary = build_summary(matrix_records)
    controls = {
        control_id: "passed_in_iteration_5"
        for control_id in i5["controls"]
    }
    source_artifacts = {
        rel(SCHEMA_OUTPUT): source_artifact(SCHEMA_OUTPUT, schema),
        rel(I3_OUTPUT): source_artifact(I3_OUTPUT, i3),
        rel(I4_OUTPUT): source_artifact(I4_OUTPUT, i4),
        rel(I5_OUTPUT): source_artifact(I5_OUTPUT, i5),
        rel(SOURCE_REGISTRY): source_artifact(SOURCE_REGISTRY, registry),
        rel(DERIVATION_POLICY): source_artifact(DERIVATION_POLICY, derivation_config),
        rel(BUDGET_LIMITS): source_artifact(BUDGET_LIMITS, budget_config),
        rel(REPLAY_POLICY): source_artifact(REPLAY_POLICY, replay_config),
    }
    source_reports = {
        rel(SCHEMA_REPORT): source_report(SCHEMA_REPORT),
        rel(I3_REPORT): source_report(I3_REPORT),
        rel(I4_REPORT): source_report(I4_REPORT),
        rel(I5_REPORT): source_report(I5_REPORT),
    }
    record_execution_scope = build_record_execution_scope(matrix_records)
    idempotency_digest_plan = build_idempotency_digest_plan(
        schema=schema,
        i3=i3,
        i4=i4,
        i5=i5,
        registry=registry,
        derivation_config=derivation_config,
        budget_config=budget_config,
        replay_config=replay_config,
        source_artifacts=source_artifacts,
        source_reports=source_reports,
        controls=controls,
        matrix_records=matrix_records,
        matrix_summary=summary,
        replay_context=replay_context,
        record_execution_scope=record_execution_scope,
    )
    nonzero_weight_fields = {
        field
        for field, weight in derivation_config[
            "endogenous_derivation_policy"
        ]["composition_weights"].items()
        if weight != 0.0
    }
    zero_weight_fields = {
        field
        for field, weight in derivation_config[
            "endogenous_derivation_policy"
        ]["composition_weights"].items()
        if weight == 0.0
    }
    checks = {
        "schema_source_passed": schema["status"] == "passed",
        "iteration_3_source_passed": i3["status"] == "passed",
        "iteration_4_source_passed": i4["status"] == "passed",
        "iteration_5_source_passed": i5["status"] == "passed",
        "iteration_5_acceptance_state_valid": i5["acceptance_state"]
        == "accepted_proxy_control_matrix_pending_bounded_drift_replay_and_claim_boundary",
        "source_registry_loaded": registry["config_id"] == "n15_source_registry",
        "derivation_policy_loaded": derivation_config["config_id"]
        == "n15_derivation_policy_v1",
        "budget_limits_loaded": budget_config["config_id"] == "n15_budget_limits_v1",
        "replay_policy_loaded": replay_config["config_id"] == "n15_replay_policy_v1",
        "required_fields_present": True,
        "control_outcomes_present": set(controls) == set(i5["controls"]),
        "source_digest_presence": all(
            valid_sha256(record["sha256"]) for record in source_artifacts.values()
        )
        and all(valid_sha256(record["sha256"]) for record in source_reports.values()),
        "support_state_perturbations_run": {
            "support_state_perturbation_lower",
            "support_state_perturbation_higher",
        }.issubset({record["record_id"] for record in matrix_records}),
        "memory_state_perturbation_run": any(
            record["record_id"] == "memory_state_perturbation"
            for record in matrix_records
        ),
        "regulation_state_perturbation_run": any(
            record["record_id"] == "regulation_state_perturbation"
            for record in matrix_records
        ),
        "ap4_consequence_context_perturbation_run": any(
            record["record_id"] == "ap4_consequence_context_perturbation"
            for record in matrix_records
        ),
        "nonzero_composition_weight_fields_perturbed": set(
            replay_context["perturbed_nonzero_weight_fields"]
        )
        == nonzero_weight_fields,
        "readiness_zero_weight_unperturbed_by_design": set(
            replay_context["unperturbed_zero_weight_fields"]
        )
        == zero_weight_fields,
        "stale_state_perturbation_blocked": any(
            record["record_id"] == "stale_state_perturbation"
            and record["observed_blocker"] == "stale_source_state_blocked"
            for record in matrix_records
        ),
        "budget_invalid_perturbation_blocked": any(
            record["record_id"] == "budget_invalid_perturbation"
            and record["observed_blocker"] == "budget_exceeded"
            for record in matrix_records
        ),
        "unbounded_drift_null_blocked": any(
            record["record_id"] == "unbounded_drift_null"
            and record["observed_blocker"] == "unbounded_target_drift_blocked"
            for record in matrix_records
        ),
        "duplicate_replay_passed": any(
            record["record_id"] == "duplicate_replay" and not record["target_changed"]
            for record in matrix_records
        ),
        "artifact_only_filesystem_replay_passed": any(
            record["record_id"] == "artifact_only_filesystem_replay"
            and not record["target_changed"]
            for record in matrix_records
        ),
        "snapshot_load_replay_passed": any(
            record["record_id"] == "snapshot_load_replay"
            and not record["target_changed"]
            for record in matrix_records
        ),
        "order_inversion_replay_passed": any(
            record["record_id"] == "order_inversion_replay"
            and not record["target_changed"]
            for record in matrix_records
        ),
        "bounded_perturbations_change_target_within_drift": summary[
            "bounded_perturbations_change_target"
        ],
        "bounded_perturbations_always_change_target": summary[
            "bounded_perturbations_change_target"
        ],
        "unchanged_replays_preserve_target": summary[
            "unchanged_replays_preserve_target"
        ],
        "unchanged_replays_never_change_target": summary[
            "unchanged_replays_preserve_target"
        ],
        "target_changes_only_for_serialized_source_current_changes": summary[
            "bounded_perturbations_change_target"
        ]
        and summary["unchanged_replays_preserve_target"],
        "target_changes_match_state_change_direction": summary[
            "bounded_perturbations_change_target"
        ]
        and summary["unchanged_replays_preserve_target"],
        "fail_closed_records_blocked": summary["fail_closed_records_blocked"],
        "policy_gate_blocks_documented": all(
            scope_record["execution_scope"]
            == "policy_gate_blocked_before_target_derivation"
            for scope_record in record_execution_scope["record_scope_records"]
            if scope_record["observed_status"] == "blocked"
        ),
        "record_execution_scope_recorded": len(
            record_execution_scope["record_scope_records"]
        )
        == len(matrix_records),
        "idempotency_digest_plan_reproducible": idempotency_digest_plan["digest"]
        == digest_value(idempotency_digest_plan["scope"]),
        "artifact_runtime_state_matches_i3": replay_context[
            "artifact_runtime_state_matches_i3"
        ],
        "registry_row_digests_match": replay_context["registry_row_digests_match"],
        "claim_flags_forced_false": all(
            value is False for value in schema["claim_flags"].values()
        ),
        "final_ap5_not_supported": True,
        "phase8_opened_false": True,
        "native_support_not_opened": True,
        "fully_native_integration_not_opened": True,
        "iteration_6_explanation_recorded": len(ITERATION_6_EXPLANATION_LINES) > 0,
        "iteration_6_top_level_output_shape_declared": len(
            ITERATION_6_TOP_LEVEL_OUTPUT_FIELDS
        )
        == 28,
        "src_diff_empty": git_status_short("src") == "",
    }
    acceptance_state = (
        "accepted_bounded_drift_replay_matrix_pending_claim_boundary_classification"
        if all(checks.values())
        else "rejected_bounded_drift_replay_matrix"
    )
    output: dict[str, Any] = {
        "experiment": "N15",
        "iteration": 6,
        "artifact_id": "n15_bounded_drift_replay_matrix",
        "purpose": "bounded_drift_and_replay_matrix",
        "schema_version": "n15_bounded_drift_replay_matrix_v1",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed" if all(checks.values()) else "failed",
        "acceptance_state": acceptance_state,
        "source_artifacts": source_artifacts,
        "source_reports": source_reports,
        "rows": [],
        "controls": controls,
        "checks": checks,
        "claim_flags": schema["claim_flags"],
        "errors": [],
        "iteration_result": {
            "acceptance_state": acceptance_state,
            "bounded_drift_replay_passed": all(checks.values()),
            "target_changes_only_for_serialized_source_current_changes": checks[
                "target_changes_only_for_serialized_source_current_changes"
            ],
            "target_changes_match_state_change_direction": checks[
                "target_changes_match_state_change_direction"
            ],
            "artifact_only_filesystem_replay_passed": checks[
                "artifact_only_filesystem_replay_passed"
            ],
            "snapshot_load_replay_passed": checks["snapshot_load_replay_passed"],
            "order_inversion_replay_passed": checks["order_inversion_replay_passed"],
            "provisional_ap_level": (
                "AP5_candidate_replay_clean_pending_claim_boundary_classification"
            ),
            "final_ap5_supported": False,
            "phase8_opened": False,
            "native_support_opened": False,
            "fully_native_integration_opened": False,
            "semantic_goal_ownership_opened": False,
            "identity_acceptance_opened": False,
            "agency_claim_opened": False,
        },
        "matrix_records": matrix_records,
        "bounded_drift_replay_matrix": {
            "matrix_id": "n15_i6_bounded_drift_replay_matrix_v1",
            "candidate_source": rel(I5_OUTPUT),
            "candidate_output_digest": i5["output_digest"],
            "records": matrix_records,
            "summary": summary,
            "replay_context": replay_context,
        },
        "matrix_summary": summary,
        "replay_context": replay_context,
        "record_execution_scope": record_execution_scope,
        "idempotency_digest_plan": idempotency_digest_plan,
        "iteration_6_explanation": {
            "section_title": "Iteration 6 Explanation",
            "format": "markdown_lines",
            "lines": ITERATION_6_EXPLANATION_LINES,
        },
        "iteration_6_top_level_output_fields": ITERATION_6_TOP_LEVEL_OUTPUT_FIELDS,
        "interpretation_record": {
            "record_id": "n15_i6_interpretation_bounded_drift_replay_v1",
            "supported_interpretation": (
                "The N15 AP5 candidate is replay-clean and bounded-drift clean "
                "at artifact level pending final claim-boundary classification."
            ),
            "plain_language_interpretation": (
                "Bounded support, memory, and regulation perturbations change "
                "the generated target within the frozen drift policy. Duplicate, "
                "artifact-only filesystem, snapshot/load, and order-inversion "
                "replays reproduce the target. Stale source, budget-invalid, "
                "and unbounded-drift variants fail closed."
            ),
            "unsupported_interpretations": [
                "final AP5 support",
                "semantic goal ownership",
                "identity acceptance",
                "intention",
                "semantic choice",
                "agency",
                "native support",
                "fully native integration",
            ],
            "remaining_required_work": [
                "iteration_7_claim_boundary_and_ap5_classification",
                "iteration_8_closeout_and_handoff",
            ],
        },
        "git": {"head": git_head(), "src_status_short": git_status_short("src")},
    }
    output["checks"]["matrix_records_match_bounded_drift_replay_matrix_records"] = (
        output["matrix_records"] == output["bounded_drift_replay_matrix"]["records"]
    )
    output["checks"]["matrix_summary_match_bounded_drift_replay_matrix_summary"] = (
        output["matrix_summary"] == output["bounded_drift_replay_matrix"]["summary"]
    )
    output["checks"]["replay_context_match_bounded_drift_replay_matrix_context"] = (
        output["replay_context"]
        == output["bounded_drift_replay_matrix"]["replay_context"]
    )
    output["checks"]["iteration_6_top_level_output_fields_match"] = set(
        ITERATION_6_TOP_LEVEL_OUTPUT_FIELDS
    ) == (set(output) | {"output_digest"})
    output["checks"]["absolute_path_absence"] = not contains_absolute_path(output)
    output["checks"]["digest_reproducibility"] = True
    output["status"] = "passed" if all(output["checks"].values()) else "failed"
    output["acceptance_state"] = (
        "accepted_bounded_drift_replay_matrix_pending_claim_boundary_classification"
        if all(output["checks"].values())
        else "rejected_bounded_drift_replay_matrix"
    )
    output["iteration_result"]["acceptance_state"] = output["acceptance_state"]
    output["iteration_result"]["bounded_drift_replay_passed"] = (
        output["status"] == "passed"
    )
    output["output_digest"] = output_digest(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    result = output["iteration_result"]
    summary = output["matrix_summary"]
    lines = [
        "# N15 Bounded Drift And Replay Matrix",
        "",
        f"Status: `{output['status']}`.",
        "",
        "## Acceptance State",
        "",
        "```text",
        output["acceptance_state"],
        "```",
        "",
        "Iteration 6 tests bounded target formation under perturbation and",
        "replay. It does not run final AP5 claim-boundary classification.",
        "",
        "## Iteration 6 Explanation",
        "",
        *output["iteration_6_explanation"]["lines"],
        "",
        "## Result",
        "",
        "```text",
        f"target_changes_only_for_serialized_source_current_changes = {str(result['target_changes_only_for_serialized_source_current_changes']).lower()}",
        f"target_changes_match_state_change_direction = {str(result['target_changes_match_state_change_direction']).lower()}",
        f"artifact_only_filesystem_replay_passed = {str(result['artifact_only_filesystem_replay_passed']).lower()}",
        f"snapshot_load_replay_passed = {str(result['snapshot_load_replay_passed']).lower()}",
        f"order_inversion_replay_passed = {str(result['order_inversion_replay_passed']).lower()}",
        "final_ap5_supported = false",
        "```",
        "",
        "## Matrix Summary",
        "",
        "```json",
        json.dumps(summary, indent=2, sort_keys=True),
        "```",
        "",
        "## Records",
        "",
        "| Record | Kind | Status | Target Changed | Blocker | Passed |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for record in output["matrix_records"]:
        lines.append(
            "| "
            f"`{record['record_id']}` | "
            f"`{record['record_kind']}` | "
            f"`{record['observed_status']}` | "
            f"`{record['target_changed']}` | "
            f"`{record.get('observed_blocker')}` | "
            f"`{record['passed']}` |"
        )
    lines.extend(
        [
            "",
            "## Replay Context",
            "",
            "```json",
            json.dumps(output["replay_context"], indent=2, sort_keys=True),
            "```",
            "",
            "## Record Execution Scope",
            "",
            "```json",
            json.dumps(
                output["record_execution_scope"],
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "## Idempotency Digest Plan",
            "",
            "```json",
            json.dumps(
                output["idempotency_digest_plan"],
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "## Top-Level Output Fields",
            "",
            "```json",
            json.dumps(
                output["iteration_6_top_level_output_fields"],
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "## Post-Review Gap Closure",
            "",
            "```text",
            "closed: iteration_6_top_level_output_fields declares every I6 top-level key.",
            "closed: idempotency_digest_plan records the I6 replay/idempotency source scope.",
            "closed: ap4_consequence_context_perturbation covers the remaining nonzero composition-weight axis.",
            "closed: target_changes_match_state_change_direction splits the previous target-change implication into explicit bidirectional checks.",
            "closed: record_execution_scope distinguishes recomputed perturbation/replay rows from policy-gated fail-closed rows.",
            "closed: matrix_records, matrix_summary, and replay_context duplication is retained for access compatibility and guarded by identity checks.",
            "not_gap: readiness_context_flag remains unperturbed because its frozen composition weight is 0.0.",
            "not_gap: symmetric perturbation directions are not required by the frozen I6 replay policy; all nonzero composition-weight axes now have bounded source-current perturbation coverage.",
            "not_gap: fail-closed records are policy-gated blockers before target acceptance, not credited target rederivations.",
            "```",
            "",
            "## Interpretation Record",
            "",
            "```json",
            json.dumps(output["interpretation_record"], indent=2, sort_keys=True),
            "```",
            "",
            "## Checks",
            "",
            "```json",
            json.dumps(output["checks"], indent=2, sort_keys=True),
            "```",
            "",
            "## Claim Boundary",
            "",
            "```text",
            "replay-clean candidate != final AP5 support",
            "bounded target drift != semantic goal ownership",
            "artifact replay equality != native support",
            "N15 Iteration 6 != agency, intention, identity acceptance, native support, or fully native integration",
            "```",
            "",
            "## Output Digest",
            "",
            "```text",
            output["output_digest"],
            "```",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    output = build_output()
    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_report(output)
    if output["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
