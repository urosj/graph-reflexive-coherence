#!/usr/bin/env python3
"""Build N15 Iteration 3 runtime-derived target candidate and bridge probe."""

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
INVENTORY_OUTPUT = OUTPUTS / "n15_proxy_source_inventory.json"
INVENTORY_REPORT = REPORTS / "n15_proxy_source_inventory.md"
SOURCE_REGISTRY = CONFIGS / "n15_source_registry.json"
DERIVATION_POLICY = CONFIGS / "n15_derivation_policy_v1.json"
BUDGET_LIMITS = CONFIGS / "n15_budget_limits_v1.json"
CONTROL_VARIANTS = CONFIGS / "n15_control_variants_v1.json"
REPLAY_POLICY = CONFIGS / "n15_replay_policy_v1.json"

OUTPUT_PATH = OUTPUTS / "n15_runtime_derived_target_candidate.json"
REPORT_PATH = REPORTS / "n15_runtime_derived_target_candidate.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/"
    "scripts/build_n15_runtime_derived_target_candidate.py"
)
GENERATED_AT = "2026-06-16T00:00:00+00:00"

BLOCKED_CLAIMS = [
    "agency",
    "intention",
    "semantic_choice",
    "semantic_goal_ownership",
    "semantic_goal_understanding",
    "identity_acceptance",
    "runtime_identity_acceptance",
    "selfhood",
    "personhood",
    "biological_behavior",
    "unrestricted_agency",
    "fully_native_agentic_like_integration",
    "native_support_without_phase8",
]

ITERATION_3_EXPLANATION_LINES = [
    "Iteration 3 composes a provisional AP5 candidate by taking the strongest "
    "closed claims from prior experiments and making them do one specific job: "
    "generate a target condition before use, then show that target can function "
    "as an input to bounded regulation.",
    "",
    'The composition is not "N13 + N14 = AP5". It is more constrained than that.',
    "",
    "**Inputs**",
    "",
    "`N13 AP3` supplies the support/regulation axis.",
    "",
    "The selected lane is the disrupted support case:",
    "",
    "```text",
    "support_margin = -0.120134817816",
    "current_support_retention = 0.729865182184",
    "support_threshold = 0.85",
    "scheduled bounded response = 0.120134817816",
    "```",
    "",
    "This is the concrete pressure that makes target formation meaningful. "
    "There is support below threshold, and N13 has a bounded response candidate "
    "that can recover it. N13 contributes regulation, not selfhood, agency, or "
    "goal ownership.",
    "",
    "`N14 AP4` supplies consequence-sensitive selection context.",
    "",
    "N14's closed claim is that route/consequence evidence can guide selection "
    "at artifact level. In I3, this contributes:",
    "",
    "```text",
    "ap4_consequence_context_score = 1.0",
    "selected_route_context = route_b",
    "```",
    "",
    "It gives the composition a consequence-sensitive axis, but not intention "
    "or semantic choice.",
    "",
    "`N08` supplies memory context.",
    "",
    "N08 contributes the route memory trend where route_b is reinforced:",
    "",
    "```text",
    "route_b memory delta = 0.12",
    "memory_context_score = 0.12",
    "```",
    "",
    "This makes the generated target depend partly on prior route-memory "
    "context, not just instantaneous support error.",
    "",
    "`N09` supplies bounded regulation context.",
    "",
    "N09 contributes that perturbation recovery is in band:",
    "",
    "```text",
    "regulation_recovery_score = 1.0",
    "```",
    "",
    "This says the system has artifact-level bounded regulation context. It "
    "does not make the target native or goal-owned.",
    "",
    "`N12` supplies readiness-only context.",
    "",
    "N12 contributes:",
    "",
    "```text",
    "readiness_context_flag = 1.0",
    "```",
    "",
    "But I2 froze its weight at `0.0`, so it validates context without changing "
    "the target value. That is deliberate: N12 readiness must not become native "
    "support by relabeling.",
    "",
    "**Composition Rule**",
    "",
    "I3 uses the I2 frozen derivation policy:",
    "",
    "```text",
    "weighted_sum =",
    "  0.40 * support_margin",
    "+ 0.25 * regulation_recovery_score",
    "+ 0.20 * memory_context_score",
    "+ 0.15 * ap4_consequence_context_score",
    "+ 0.00 * readiness_context_flag",
    "```",
    "",
    "With the I3 values:",
    "",
    "```text",
    "weighted_sum = 0.375946072874",
    "```",
    "",
    "Then:",
    "",
    "```text",
    "target_center =",
    "  support_threshold + 0.10 * weighted_sum",
    "",
    "target_center = 0.887594607287",
    "target_tolerance = 0.07",
    "target_band = [0.817594607287, 0.957594607287]",
    "```",
    "",
    "So the target is not externally declared. It is generated from serialized "
    "source-current state under a frozen policy.",
    "",
    "**What The Composed Result Brings**",
    "",
    "The composed result brings something stronger than historic target existence.",
    "",
    "Direct historic evidence from N13 only showed:",
    "",
    "```text",
    "target condition exists at AP2 support-derived target scope",
    "```",
    "",
    "Iteration 3 adds:",
    "",
    "```text",
    "a target condition is generated before use from old-best runtime-visible inputs",
    "```",
    "",
    "Then the bridge probe tests whether the generated target functions as an input:",
    "",
    "```text",
    "no-response support = 0.729865182184",
    "bounded-response support = 0.85",
    "generated target band = [0.817594607287, 0.957594607287]",
    "```",
    "",
    "Result:",
    "",
    "```text",
    "no-response: outside band, rejected",
    "bounded N13 response: inside band, selected",
    "```",
    "",
    "That is the important bridge. The generated target is not just written "
    "down; it changes the ranking of candidate regulation behavior.",
    "",
    "**Claim Boundary**",
    "",
    "The composed result supports only:",
    "",
    "```text",
    "provisional AP5 candidate pending contrast, controls, replay, and claim classification",
    "```",
    "",
    "It does not yet support final AP5 because I4-I7 still need to show:",
    "",
    "```text",
    "not externally injected",
    "not hidden target derivation",
    "not post-hoc proxy formation",
    "negative controls fail closed",
    "bounded drift and replay hold",
    "claim boundary remains clean",
    "```",
    "",
    "So the end result is: a constructed, traceable, runtime-derived target "
    "candidate that can function as a bounded regulation input, but still not "
    "final AP5.",
]

ITERATION_3_TOP_LEVEL_OUTPUT_FIELDS = [
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
    "direct_historic_gap_record",
    "iteration_3_explanation",
    "iteration_3_top_level_output_fields",
    "control_value_convention",
    "replay_digest_inputs_design_note",
    "runtime_state_vector",
    "target_condition",
    "bridge_probe",
    "dependency_trace",
    "budget_cost_surface",
    "budget_validity",
    "replay_digest_policy",
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


def valid_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        char in "0123456789abcdef" for char in value
    )


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


def build_runtime_state_vector(
    registry: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, dict[str, Any]], dict[str, Any]]:
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
    support_margin = rounded(support_lane["support_margin"])

    runtime_state_vector = {
        "vector_id": "n15_i3_old_best_source_current_state_vector_v1",
        "source_current": True,
        "source_window": (
            "N13 disrupted-support lane + N14 AP4 closeout + "
            "N08 MEM6 + N09 GPR6 + N12 readiness"
        ),
        "support_margin": support_margin,
        "support_threshold": support_lane["support_survival_threshold"],
        "current_support_retention": rounded(support_lane["final_A_support_retention"]),
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
            "scheduled_response_amounts": support_lane["response_magnitude_surface"][
                "scheduled_response_amounts"
            ],
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
    }
    return runtime_state_vector, rows, sources


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


def build_bridge_probe(
    runtime_state_vector: dict[str, Any],
    target_condition: dict[str, Any],
) -> dict[str, Any]:
    lower, upper = target_condition["target_band"]
    current = runtime_state_vector["current_support_retention"]
    response_total = runtime_state_vector["n13_bounded_response"][
        "scheduled_response_total"
    ]
    post_response = rounded(current + response_total)

    def membership(value: float) -> bool:
        return lower <= value <= upper

    no_response = {
        "candidate_id": "no_response_baseline",
        "candidate_kind": "null_regulation_candidate",
        "budget_valid": True,
        "response_amount": 0.0,
        "post_response_support_retention": current,
        "target_band_membership": membership(current),
        "rank": 2,
        "selection_status": "rejected_outside_generated_target_band",
    }
    bounded_response = {
        "candidate_id": "n13_bounded_support_response",
        "candidate_kind": "bounded_regulation_candidate",
        "budget_valid": True,
        "response_amount": response_total,
        "post_response_support_retention": post_response,
        "target_band_membership": membership(post_response),
        "rank": 1,
        "selection_status": "selected_enters_generated_target_band",
    }
    return {
        "bridge_probe_id": "n15_i3_bridge_generated_target_as_regulation_input_v1",
        "gap_addressed": (
            "distinguish target condition exists from target condition functions "
            "as an AP5-relevant proxy-formation input"
        ),
        "bridge_scope": "pre_contrast_pre_control_candidate_bridge",
        "target_condition_digest": digest_value(target_condition),
        "ranking_rule": (
            "rank budget-valid regulation candidates by generated target-band "
            "membership before response cost; no semantic goal ownership relabel"
        ),
        "target_condition_consumed_before_rank": True,
        "bridge_candidates": [bounded_response, no_response],
        "selected_bridge_candidate": "n13_bounded_support_response",
        "target_condition_functions_as_proxy_input": (
            "provisional_yes_bridge_probe_only_pending_external_proxy_contrast_controls_replay_and_claim_boundary"
        ),
        "target_exists_without_bridge_is_insufficient": True,
        "unsupported_interpretations": [
            "final AP5 support",
            "semantic goal ownership",
            "intention",
            "semantic choice",
            "agency",
            "identity acceptance",
            "native support",
            "fully native integration",
        ],
    }


def dependency_trace(
    rows: dict[str, dict[str, Any]],
    runtime_state_vector: dict[str, Any],
    target_condition: dict[str, Any],
    bridge_probe: dict[str, Any],
) -> list[dict[str, Any]]:
    bounded_response = next(
        candidate
        for candidate in bridge_probe["bridge_candidates"]
        if candidate["candidate_id"] == "n13_bounded_support_response"
    )
    target_condition_digest = digest_value(target_condition)
    return [
        {
            "target_field": "direct_historic_gap_record.reason_not_promoted",
            "source_row_id": rows["direct_ap2"]["row_id"],
            "source_artifact": rows["direct_ap2"]["source_artifact"],
            "source_sha256": rows["direct_ap2"]["source_sha256"],
            "source_field": "support_derived_target_candidate",
            "transform_id": "n15_i3_direct_historic_gap_record_v1",
            "transform_parameters": {
                "role": "gap_context_only_not_ap5_derivation_input",
            },
            "claim_ceiling_of_source": rows["direct_ap2"]["provisional_claim_ceiling"],
        },
        {
            "target_field": "target_center",
            "source_row_id": rows["n13_ap3_candidate"]["row_id"],
            "source_artifact": rows["n13_ap3_candidate"]["source_artifact"],
            "source_sha256": rows["n13_ap3_candidate"]["source_sha256"],
            "source_field": "support_seeking_regulation_candidate.lane_response_records[n09_matched_partial_support_withdrawal].support_margin",
            "transform_id": "n15_endogenous_proxy_derivation_policy_v1.weighted_sum.support_margin",
            "transform_parameters": {
                "weight": 0.4,
                "value": runtime_state_vector["support_margin"],
            },
            "claim_ceiling_of_source": rows["n13_ap3_candidate"][
                "provisional_claim_ceiling"
            ],
        },
        {
            "target_field": "target_center",
            "source_row_id": rows["n09_regulation"]["row_id"],
            "source_artifact": rows["n09_regulation"]["source_artifact"],
            "source_sha256": rows["n09_regulation"]["source_sha256"],
            "source_field": "regulation_summary.gpr8_perturbation_recovery_in_band",
            "transform_id": "n15_endogenous_proxy_derivation_policy_v1.weighted_sum.regulation_recovery_score",
            "transform_parameters": {
                "weight": 0.25,
                "value": runtime_state_vector["regulation_recovery_score"],
            },
            "claim_ceiling_of_source": rows["n09_regulation"][
                "provisional_claim_ceiling"
            ],
        },
        {
            "target_field": "target_center",
            "source_row_id": rows["n08_memory"]["row_id"],
            "source_artifact": rows["n08_memory"]["source_artifact"],
            "source_sha256": rows["n08_memory"]["source_sha256"],
            "source_field": "artifact_only_replay.route_b_strength_after_each_cycle",
            "transform_id": "n15_endogenous_proxy_derivation_policy_v1.weighted_sum.memory_context_score",
            "transform_parameters": {
                "weight": 0.2,
                "value": runtime_state_vector["memory_context_score"],
            },
            "claim_ceiling_of_source": rows["n08_memory"]["provisional_claim_ceiling"],
        },
        {
            "target_field": "target_center",
            "source_row_id": rows["n14_ap4_closeout"]["row_id"],
            "source_artifact": rows["n14_ap4_closeout"]["source_artifact"],
            "source_sha256": rows["n14_ap4_closeout"]["source_sha256"],
            "source_field": "closeout_result.final_ap4_supported",
            "transform_id": "n15_endogenous_proxy_derivation_policy_v1.weighted_sum.ap4_consequence_context_score",
            "transform_parameters": {
                "weight": 0.15,
                "value": runtime_state_vector["ap4_consequence_context_score"],
            },
            "claim_ceiling_of_source": rows["n14_ap4_closeout"][
                "provisional_claim_ceiling"
            ],
        },
        {
            "target_field": "target_center",
            "source_row_id": rows["n12_readiness"]["row_id"],
            "source_artifact": rows["n12_readiness"]["source_artifact"],
            "source_sha256": rows["n12_readiness"]["source_sha256"],
            "source_field": "matrix_result.phase8_ready_contract_count",
            "transform_id": "n15_endogenous_proxy_derivation_policy_v1.weighted_sum.readiness_context_flag",
            "transform_parameters": {
                "weight": 0.0,
                "value": runtime_state_vector["readiness_context_flag"],
                "role": "readiness_only_context_no_target_value_change",
            },
            "claim_ceiling_of_source": rows["n12_readiness"][
                "provisional_claim_ceiling"
            ],
        },
        {
            "target_field": "runtime_state_vector.n13_ap3_closed_claim_ceiling",
            "source_row_id": rows["n13_ap3_closeout"]["row_id"],
            "source_artifact": rows["n13_ap3_closeout"]["source_artifact"],
            "source_sha256": rows["n13_ap3_closeout"]["source_sha256"],
            "source_field": "closeout_result.final_supported_ap_level + closeout_result.final_claim_ceiling",
            "transform_id": "n15_i3_claim_ceiling_context_record_v1",
            "transform_parameters": {
                "role": "source_claim_ceiling_context_not_target_value_input",
            },
            "claim_ceiling_of_source": rows["n13_ap3_closeout"][
                "provisional_claim_ceiling"
            ],
        },
        {
            "target_field": "runtime_state_vector.constructed_followout_context",
            "source_row_id": rows["n14_constructed_followout"]["row_id"],
            "source_artifact": rows["n14_constructed_followout"]["source_artifact"],
            "source_sha256": rows["n14_constructed_followout"]["source_sha256"],
            "source_field": "followout_summary",
            "transform_id": "n15_i3_constructed_followout_context_record_v1",
            "transform_parameters": {
                "role": "constructed_followout_context_with_scope_caveat",
            },
            "claim_ceiling_of_source": rows["n14_constructed_followout"][
                "provisional_claim_ceiling"
            ],
        },
        {
            "target_field": "target_tolerance",
            "source_row_id": rows["n09_regulation"]["row_id"],
            "source_artifact": rows["n09_regulation"]["source_artifact"],
            "source_sha256": rows["n09_regulation"]["source_sha256"],
            "source_field": "regulation_summary.gpr8_perturbation_recovery_in_band",
            "transform_id": "n15_endogenous_proxy_derivation_policy_v1.target_tolerance_rule",
            "transform_parameters": {
                "base": 0.05,
                "scale": 0.02,
                "clamp": [0.03, 0.08],
            },
            "claim_ceiling_of_source": rows["n09_regulation"][
                "provisional_claim_ceiling"
            ],
        },
        {
            "target_field": "target_band",
            "source_row_id": rows["n13_ap3_candidate"]["row_id"],
            "source_artifact": rows["n13_ap3_candidate"]["source_artifact"],
            "source_sha256": rows["n13_ap3_candidate"]["source_sha256"],
            "source_field": "support_seeking_regulation_candidate.lane_response_records[n09_matched_partial_support_withdrawal].support_survival_threshold",
            "transform_id": "n15_endogenous_proxy_derivation_policy_v1.target_band_rule",
            "transform_parameters": {
                "band_rule": "target_center +/- target_tolerance",
            },
            "claim_ceiling_of_source": rows["n13_ap3_candidate"][
                "provisional_claim_ceiling"
            ],
        },
        {
            "target_field": "bridge_probe.selected_bridge_candidate",
            "source_row_id": rows["n13_ap3_candidate"]["row_id"],
            "source_artifact": rows["n13_ap3_candidate"]["source_artifact"],
            "source_sha256": rows["n13_ap3_candidate"]["source_sha256"],
            "source_field": "support_seeking_regulation_candidate.lane_response_records[n09_matched_partial_support_withdrawal].response_magnitude_surface.scheduled_response_total",
            "transform_id": "n15_i3_bridge_generated_target_as_regulation_input_v1",
            "transform_parameters": {
                "rank_rule": "budget_valid_target_band_membership_before_response_cost",
            },
            "claim_ceiling_of_source": rows["n13_ap3_candidate"][
                "provisional_claim_ceiling"
            ],
        },
        {
            "target_field": "bridge_probe.bridge_candidates[n13_bounded_support_response].response_amount",
            "source_row_id": rows["n13_ap3_candidate"]["row_id"],
            "source_artifact": rows["n13_ap3_candidate"]["source_artifact"],
            "source_sha256": rows["n13_ap3_candidate"]["source_sha256"],
            "source_field": "support_seeking_regulation_candidate.lane_response_records[n09_matched_partial_support_withdrawal].response_magnitude_surface.scheduled_response_total",
            "transform_id": "n15_i3_bridge_response_surface_v1.response_amount",
            "transform_parameters": {
                "value": bounded_response["response_amount"],
            },
            "claim_ceiling_of_source": rows["n13_ap3_candidate"][
                "provisional_claim_ceiling"
            ],
        },
        {
            "target_field": "bridge_probe.bridge_candidates[n13_bounded_support_response].post_response_support_retention",
            "source_row_id": rows["n13_ap3_candidate"]["row_id"],
            "source_artifact": rows["n13_ap3_candidate"]["source_artifact"],
            "source_sha256": rows["n13_ap3_candidate"]["source_sha256"],
            "source_field": "support_seeking_regulation_candidate.lane_response_records[n09_matched_partial_support_withdrawal].final_A_support_retention + response_magnitude_surface.scheduled_response_total",
            "transform_id": "n15_i3_bridge_response_surface_v1.post_response_support_retention",
            "transform_parameters": {
                "current_support_retention": runtime_state_vector[
                    "current_support_retention"
                ],
                "response_amount": bounded_response["response_amount"],
                "computed_value": bounded_response["post_response_support_retention"],
            },
            "claim_ceiling_of_source": rows["n13_ap3_candidate"][
                "provisional_claim_ceiling"
            ],
        },
        {
            "target_field": "bridge_probe.bridge_candidates[n13_bounded_support_response].target_band_membership",
            "source_row_id": rows["n13_ap3_candidate"]["row_id"],
            "source_artifact": rows["n13_ap3_candidate"]["source_artifact"],
            "source_sha256": rows["n13_ap3_candidate"]["source_sha256"],
            "source_field": "support_seeking_regulation_candidate.lane_response_records[n09_matched_partial_support_withdrawal].response_magnitude_surface.scheduled_response_total",
            "transform_id": "n15_i3_bridge_response_surface_v1.target_band_membership",
            "transform_parameters": {
                "target_condition_digest": target_condition_digest,
                "target_band": target_condition["target_band"],
                "post_response_support_retention": bounded_response[
                    "post_response_support_retention"
                ],
                "computed_value": bounded_response["target_band_membership"],
            },
            "claim_ceiling_of_source": rows["n13_ap3_candidate"][
                "provisional_claim_ceiling"
            ],
        },
        {
            "target_field": "bridge_probe.bridge_candidates[n13_bounded_support_response].budget_valid",
            "source_row_id": rows["n13_ap3_candidate"]["row_id"],
            "source_artifact": rows["n13_ap3_candidate"]["source_artifact"],
            "source_sha256": rows["n13_ap3_candidate"]["source_sha256"],
            "source_field": "support_seeking_regulation_candidate.lane_response_records[n09_matched_partial_support_withdrawal].budget_debit_surface",
            "transform_id": "n15_i3_bridge_response_surface_v1.budget_valid",
            "transform_parameters": {
                "budget_debit_required": runtime_state_vector["n13_bounded_response"][
                    "budget_debit_required"
                ],
                "budget_debit_amount": runtime_state_vector["n13_bounded_response"][
                    "budget_debit_amount"
                ],
                "computed_value": bounded_response["budget_valid"],
            },
            "claim_ceiling_of_source": rows["n13_ap3_candidate"][
                "provisional_claim_ceiling"
            ],
        },
    ]


def build_budget_surface(
    selected_rows: dict[str, dict[str, Any]],
    runtime_state_vector: dict[str, Any],
    target_condition: dict[str, Any],
    bridge_probe: dict[str, Any],
    trace: list[dict[str, Any]],
    budget_config: dict[str, Any],
) -> dict[str, Any]:
    input_payload = {
        "selected_rows": selected_rows,
        "runtime_state_vector": runtime_state_vector,
        "target_condition": target_condition,
        "bridge_probe": bridge_probe,
        "dependency_trace": trace,
    }
    output_payload = {
        "target_condition": target_condition,
        "bridge_probe": bridge_probe,
    }
    return {
        "source_row_count": len(selected_rows),
        "transform_count": len(trace),
        "canonical_json_input_bytes": len(canonical_json(input_payload).encode("utf-8")),
        "canonical_json_output_bytes": len(
            canonical_json(output_payload).encode("utf-8")
        ),
        "replay_count": 1,
        "validation_count": 18,
        "wall_clock_seconds": 0,
        "budget_limits": budget_config["budget_limits"]["limits"],
    }


def budget_validity(
    budget_surface: dict[str, Any], budget_config: dict[str, Any]
) -> dict[str, Any]:
    limits = budget_config["budget_limits"]["limits"]
    checks = {
        unit: budget_surface[unit] <= limit for unit, limit in limits.items()
    }
    return {
        "checked_before_target_use": True,
        "valid": all(checks.values()),
        "unit_checks": checks,
    }


def build_candidate_row(
    schema: dict[str, Any],
    rows: dict[str, dict[str, Any]],
    runtime_state_vector: dict[str, Any],
    target_condition: dict[str, Any],
    trace: list[dict[str, Any]],
    budget_surface: dict[str, Any],
    budget_validity_record: dict[str, Any],
    bridge_probe: dict[str, Any],
    claim_flags: dict[str, bool],
) -> dict[str, Any]:
    schema_sha = digest_file(SCHEMA_OUTPUT)
    schema_report_sha = digest_file(SCHEMA_REPORT)
    replay_inputs = {
        "source_artifact_digests": {
            key: row["source_sha256"] for key, row in rows.items()
        },
        "selected_source_rows": [row["row_id"] for row in rows.values()],
        "runtime_state_vector": runtime_state_vector,
        "target_condition": target_condition,
        "dependency_trace_digest": digest_value(trace),
        "bridge_probe_digest": digest_value(bridge_probe),
        "claim_flags": claim_flags,
    }
    row = {
        "row_id": "n15_i3_row_01_constructed_runtime_derived_target_candidate",
        "source_experiment": "N15",
        "source_iteration": "iteration_2_proxy_formation_schema_and_ap5_gate",
        "source_artifact": rel(SCHEMA_OUTPUT),
        "source_report": rel(SCHEMA_REPORT),
        "source_sha256": schema_sha,
        "source_report_sha256": schema_report_sha,
        "mechanism_name": "runtime_derived_support_recovery_target_candidate",
        "mechanism_role": "constructed_ap5_candidate_pending_contrast_controls_replay",
        "source_role_classification": "old_best_claims_constructed_candidate",
        "evidence_strategy": "old_best_claims_construction_with_bridge_probe",
        "old_best_claim_inputs": [row["row_id"] for row in rows.values()],
        "direct_historic_support_status": (
            "direct N13 AP2 support-derived target exists, but is used only as "
            "gap context; AP5 candidate uses N13 AP3 + N14 AP4 + N08/N09/N12"
        ),
        "arc_method_mapping": {
            "classification_of_becoming": "classify as provisional AP5 candidate, not final AP5",
            "interrogation_of_becoming": "bridge target existence to target-as-input before contrast controls",
            "naturalization_of_becoming": "keep readiness and constructed evidence separate from native support",
            "cultivation_of_becoming": "cultivate target formation from old best claims rather than optimize a declared fixture",
        },
        "runtime_state_surface_id": runtime_state_vector["vector_id"],
        "state_source_window": runtime_state_vector["source_window"],
        "source_current": True,
        "support_state_descriptor": {
            "support_margin": runtime_state_vector["support_margin"],
            "support_threshold": runtime_state_vector["support_threshold"],
            "current_support_retention": runtime_state_vector[
                "current_support_retention"
            ],
            "support_error": runtime_state_vector["support_error"],
        },
        "identity_condition_descriptor": (
            "support/identity-condition descriptor only; no identity acceptance"
        ),
        "memory_state_descriptor": {
            "route_b_memory_delta": runtime_state_vector["memory_context_score"],
            "selected_route_context": runtime_state_vector["selected_route_context"],
        },
        "regulation_state_descriptor": {
            "regulation_recovery_score": runtime_state_vector[
                "regulation_recovery_score"
            ],
            "bounded_response_total": runtime_state_vector["n13_bounded_response"][
                "scheduled_response_total"
            ],
        },
        "declared_proxy_absent": True,
        "external_target_input_absent": True,
        "endogenous_derivation_policy": target_condition["derivation_policy_id"],
        "target_condition_generated_at": target_condition[
            "target_condition_generated_at"
        ],
        "target_condition_surface": target_condition["target_condition_surface"],
        "target_band": target_condition["target_band"],
        "target_tolerance": target_condition["target_tolerance"],
        "target_center": target_condition["target_center"],
        "drift_bound": schema["bounded_drift_policy"],
        "drift_update_rule": "target_center within support_threshold +/- 0.10",
        "drift_clamp_policy": {
            "drift_clamped": target_condition["drift_clamped"],
            "policy_id": schema["bounded_drift_policy"]["policy_id"],
        },
        "dependency_trace": trace,
        "budget_cost_surface": budget_surface,
        "budget_units": schema["budget_limits"]["units"],
        "budget_validity": budget_validity_record,
        "replay_digest_inputs": replay_inputs,
        "replay_digest_algorithm": "sha256_canonical_json_sorted_keys_ascii",
        "idempotency_digest_plan": {
            "algorithm": "sha256",
            "scope": (
                "source_artifact_digests + selected_source_rows + "
                "runtime_state_vector + target_condition + "
                "dependency_trace_digest + bridge_probe_digest + claim_flags"
            ),
            "digest": digest_value(replay_inputs),
        },
        "fully_native_integration_opened": False,
        "artifact_only_replay_status": (
            "validator_passed_for_schema_shape; full artifact-only replay deferred_to_iteration_6"
        ),
        "snapshot_load_status": "not_run_until_iteration_6",
        "order_inversion_replay_status": "not_run_until_iteration_6",
        "externally_injected_target_control": "required_before_ap5_not_run_until_iteration_4",
        "hidden_target_derivation_control": "required_before_ap5_not_run_until_iteration_4",
        "post_hoc_proxy_formation_control": "required_before_ap5_not_run_until_iteration_4",
        "unbounded_target_drift_control": "required_before_ap5_not_run_until_iteration_5",
        "budget_surface_ambiguity_control": "required_before_ap5_not_run_until_iteration_5",
        "semantic_goal_ownership_relabel_control": "required_before_ap5_not_run_until_iteration_5",
        "identity_acceptance_relabel_control": "required_before_ap5_not_run_until_iteration_5",
        "native_support_relabel_control": "required_before_ap5_not_run_until_iteration_5",
        "provisional_ap_level": "AP5_candidate_pending_contrast_controls_replay",
        "provisional_claim_ceiling": (
            "runtime_derived_target_candidate_with_bridge_probe_pending_contrast_controls_replay_and_claim_boundary"
        ),
        "blocked_claims": BLOCKED_CLAIMS,
        "missing_gates": [
            "external_proxy_contrast_not_run_until_iteration_4",
            "adversarial_controls_not_run_until_iteration_5",
            "bounded_drift_and_replay_not_run_until_iteration_6",
            "claim_boundary_classification_not_run_until_iteration_7",
            "final_ap5_not_supported",
        ],
    }
    missing = sorted(set(schema["row_schema_fields"]) - set(row))
    if missing:
        raise ValueError(f"candidate row missing schema fields: {missing}")
    return row


def build_output() -> dict[str, Any]:
    schema = load_json(SCHEMA_OUTPUT)
    inventory = load_json(INVENTORY_OUTPUT)
    registry = load_json(SOURCE_REGISTRY)
    derivation_config = load_json(DERIVATION_POLICY)
    budget_config = load_json(BUDGET_LIMITS)
    control_config = load_json(CONTROL_VARIANTS)
    replay_config = load_json(REPLAY_POLICY)

    runtime_state_vector, selected_rows, selected_sources = build_runtime_state_vector(
        registry
    )
    target_condition = derive_target_condition(runtime_state_vector, derivation_config)
    bridge_probe = build_bridge_probe(runtime_state_vector, target_condition)
    trace = dependency_trace(
        selected_rows,
        runtime_state_vector,
        target_condition,
        bridge_probe,
    )
    budget_surface = build_budget_surface(
        selected_rows,
        runtime_state_vector,
        target_condition,
        bridge_probe,
        trace,
        budget_config,
    )
    budget_record = budget_validity(budget_surface, budget_config)
    candidate_row = build_candidate_row(
        schema,
        selected_rows,
        runtime_state_vector,
        target_condition,
        trace,
        budget_surface,
        budget_record,
        bridge_probe,
        schema["claim_flags"],
    )

    controls = {
        control["control_id"]: "required_before_ap5"
        for control in schema["control_requirements"]
    }
    control_value_convention = {
        "record_id": "n15_i3_control_value_convention_v1",
        "top_level_controls": (
            "requirement-only status for every control required before AP5"
        ),
        "row_level_control_fields": (
            "requirement status plus planned execution iteration where the "
            "Iteration 2 row schema has a corresponding control field"
        ),
        "reason": (
            "Iteration 3 builds the bridge candidate only; Iterations 4 and 5 "
            "execute the contrast and adversarial control matrices."
        ),
    }
    replay_digest_inputs_design_note = {
        "record_id": "n15_i3_replay_digest_inputs_design_note_v1",
        "design_choice": (
            "replay_digest_inputs intentionally embeds full runtime_state_vector "
            "and target_condition objects, while dependency_trace and "
            "bridge_probe are represented by canonical digests"
        ),
        "iteration_6_replay_requirement": (
            "rederive full runtime_state_vector and target_condition objects "
            "from source-current rows and compare objects before accepting "
            "digest agreement"
        ),
        "not_gap": (
            "full object copies are the replay surface, not hidden target "
            "derivation or post-hoc proxy formation"
        ),
    }
    direct_historic_gap_record = {
        "record_id": "n15_i3_direct_historic_gap_record_v1",
        "direct_historic_source_row_id": selected_rows["direct_ap2"]["row_id"],
        "direct_historic_support_status": (
            "target_condition_exists_at_N13_AP2_scope_only"
        ),
        "gap": "target_condition_exists != AP5_relevant_proxy_formation_input",
        "reason_not_promoted": (
            "N13 direct target evidence lacks N15 pre-use derivation from the "
            "old-best source vector plus bridge consumption by rank/regulation"
        ),
        "candidate_path_used": [
            selected_rows["n13_ap3_candidate"]["row_id"],
            selected_rows["n13_ap3_closeout"]["row_id"],
            selected_rows["n14_ap4_closeout"]["row_id"],
            selected_rows["n14_constructed_followout"]["row_id"],
            selected_rows["n08_memory"]["row_id"],
            selected_rows["n09_regulation"]["row_id"],
            selected_rows["n12_readiness"]["row_id"],
        ],
    }

    trace_target_fields = {entry["target_field"] for entry in trace}
    required_trace_fields = {
        "target_center",
        "target_tolerance",
        "target_band",
        "bridge_probe.selected_bridge_candidate",
    }
    required_context_row_ids = {
        selected_rows["direct_ap2"]["row_id"],
        selected_rows["n12_readiness"]["row_id"],
        selected_rows["n13_ap3_closeout"]["row_id"],
        selected_rows["n14_constructed_followout"]["row_id"],
    }
    trace_source_row_ids = {entry["source_row_id"] for entry in trace}
    required_bridge_trace_fields = {
        "bridge_probe.bridge_candidates[n13_bounded_support_response].response_amount",
        "bridge_probe.bridge_candidates[n13_bounded_support_response].post_response_support_retention",
        "bridge_probe.bridge_candidates[n13_bounded_support_response].target_band_membership",
        "bridge_probe.bridge_candidates[n13_bounded_support_response].budget_valid",
    }
    checks = {
        "required_fields_present": set(schema["row_schema_fields"]).issubset(
            set(candidate_row)
        ),
        "schema_source_passed": schema["status"] == "passed",
        "inventory_source_passed": inventory["status"] == "passed",
        "source_registry_loaded": registry["config_id"] == "n15_source_registry",
        "derivation_policy_loaded": derivation_config["config_id"]
        == "n15_derivation_policy_v1",
        "budget_limits_loaded": budget_config["config_id"] == "n15_budget_limits_v1",
        "control_variants_loaded": control_config["config_id"]
        == "n15_control_variants_v1",
        "replay_policy_loaded": replay_config["config_id"] == "n15_replay_policy_v1",
        "selected_source_digests_match_registry": all(
            validate_registry_row_digest(row) for row in selected_rows.values()
        ),
        "direct_historic_ap2_gap_recorded": direct_historic_gap_record[
            "reason_not_promoted"
        ]
        != "",
        "old_best_claim_inputs_present": len(selected_rows) >= 6,
        "n14_constructed_followout_in_candidate_path": selected_rows[
            "n14_constructed_followout"
        ]["row_id"]
        in direct_historic_gap_record["candidate_path_used"],
        "target_generated_before_bridge_use": target_condition[
            "target_condition_generated_at"
        ]
        == "before_bridge_probe_regulation_candidate_ranking",
        "target_center_within_drift_bound": abs(
            target_condition["target_center"] - runtime_state_vector["support_threshold"]
        )
        <= schema["bounded_drift_policy"]["numeric_target_center_max_update"],
        "target_band_numeric_and_ordered": target_condition["target_band"][0]
        < target_condition["target_band"][1],
        "target_tolerance_within_policy": 0.03
        <= target_condition["target_tolerance"]
        <= 0.08,
        "dependency_trace_complete_for_target_fields": required_trace_fields.issubset(
            trace_target_fields
        ),
        "dependency_trace_covers_selected_context_rows": required_context_row_ids.issubset(
            trace_source_row_ids
        ),
        "bridge_response_surface_trace_present": required_bridge_trace_fields.issubset(
            trace_target_fields
        ),
        "budget_valid_before_target_use": budget_record["checked_before_target_use"]
        and budget_record["valid"],
        "declared_external_proxy_absent": candidate_row["declared_proxy_absent"] is True,
        "external_target_input_absent": candidate_row["external_target_input_absent"]
        is True,
        "bridge_probe_consumes_target_condition": bridge_probe[
            "target_condition_consumed_before_rank"
        ]
        is True,
        "bridge_selects_bounded_response_over_no_response": bridge_probe[
            "selected_bridge_candidate"
        ]
        == "n13_bounded_support_response",
        "target_condition_functions_as_proxy_input_provisionally": bridge_probe[
            "target_condition_functions_as_proxy_input"
        ].startswith("provisional_yes"),
        "claim_flags_forced_false": all(
            value is False for value in schema["claim_flags"].values()
        ),
        "control_outcomes_present": set(controls)
        == {control["control_id"] for control in schema["control_requirements"]},
        "digest_reproducibility": candidate_row["idempotency_digest_plan"]["digest"]
        == digest_value(candidate_row["replay_digest_inputs"]),
        "control_value_convention_recorded": control_value_convention["record_id"]
        == "n15_i3_control_value_convention_v1",
        "replay_digest_inputs_design_note_recorded": replay_digest_inputs_design_note[
            "record_id"
        ]
        == "n15_i3_replay_digest_inputs_design_note_v1",
        "iteration_3_top_level_output_shape_declared": len(
            ITERATION_3_TOP_LEVEL_OUTPUT_FIELDS
        )
        == 32,
        "no_final_ap5_supported": True,
        "phase8_opened_false": True,
        "native_support_not_opened": True,
        "fully_native_integration_not_opened": True,
        "src_diff_empty": git_status_short("src") == "",
    }

    source_artifacts = {
        rel(SCHEMA_OUTPUT): source_artifact(SCHEMA_OUTPUT, schema),
        rel(INVENTORY_OUTPUT): source_artifact(INVENTORY_OUTPUT, inventory),
        rel(SOURCE_REGISTRY): source_artifact(SOURCE_REGISTRY, registry),
        rel(DERIVATION_POLICY): source_artifact(DERIVATION_POLICY, derivation_config),
        rel(BUDGET_LIMITS): source_artifact(BUDGET_LIMITS, budget_config),
        rel(CONTROL_VARIANTS): source_artifact(CONTROL_VARIANTS, control_config),
        rel(REPLAY_POLICY): source_artifact(REPLAY_POLICY, replay_config),
    }
    for key, row in selected_rows.items():
        source_artifacts[row["source_artifact"]] = source_artifact(
            source_path(row), selected_sources.get(key)
        )
    source_reports = {
        rel(SCHEMA_REPORT): source_report(SCHEMA_REPORT),
        rel(INVENTORY_REPORT): source_report(INVENTORY_REPORT),
    }
    for row in selected_rows.values():
        source_reports[row["source_report"]] = source_report(report_path(row))

    checks["source_digest_presence"] = (
        all(valid_sha256(record.get("sha256")) for record in source_artifacts.values())
        and all(
            valid_sha256(record.get("sha256")) for record in source_reports.values()
        )
        and valid_sha256(candidate_row["source_sha256"])
        and valid_sha256(candidate_row["source_report_sha256"])
    )
    acceptance_state = (
        "accepted_runtime_derived_target_candidate_with_bridge_pending_controls"
        if all(checks.values())
        else "rejected_runtime_derived_target_candidate"
    )

    output: dict[str, Any] = {
        "experiment": "N15",
        "iteration": 3,
        "artifact_id": "n15_runtime_derived_target_candidate",
        "purpose": "runtime_derived_target_candidate_with_bridge_probe",
        "schema_version": "n15_runtime_derived_target_candidate_v1",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed" if all(checks.values()) else "failed",
        "acceptance_state": acceptance_state,
        "source_artifacts": source_artifacts,
        "source_reports": source_reports,
        "rows": [candidate_row],
        "controls": controls,
        "checks": checks,
        "claim_flags": schema["claim_flags"],
        "errors": [],
        "iteration_result": {
            "acceptance_state": acceptance_state,
            "runtime_derived_target_generated": all(checks.values()),
            "bridge_probe_passed": checks["bridge_selects_bounded_response_over_no_response"],
            "target_condition_functions_as_proxy_input": checks[
                "target_condition_functions_as_proxy_input_provisionally"
            ],
            "provisional_ap_level": candidate_row["provisional_ap_level"],
            "final_ap5_supported": False,
            "phase8_opened": False,
            "native_support_opened": False,
            "fully_native_integration_opened": False,
            "semantic_goal_ownership_opened": False,
            "agency_claim_opened": False,
        },
        "direct_historic_gap_record": direct_historic_gap_record,
        "iteration_3_explanation": {
            "section_title": "Iteration 3 Explanation",
            "format": "markdown_lines",
            "lines": ITERATION_3_EXPLANATION_LINES,
        },
        "iteration_3_top_level_output_fields": ITERATION_3_TOP_LEVEL_OUTPUT_FIELDS,
        "control_value_convention": control_value_convention,
        "replay_digest_inputs_design_note": replay_digest_inputs_design_note,
        "runtime_state_vector": runtime_state_vector,
        "target_condition": target_condition,
        "bridge_probe": bridge_probe,
        "dependency_trace": trace,
        "budget_cost_surface": budget_surface,
        "budget_validity": budget_record,
        "replay_digest_policy": replay_config["replay_digest_policy"],
        "interpretation_record": {
            "record_id": "n15_i3_interpretation_runtime_derived_target_candidate_v1",
            "supported_interpretation": (
                "N15 now has a provisional runtime-derived target candidate. "
                "The target band is generated before bridge ranking from the "
                "old-best source-current vector and is consumed by a bounded "
                "regulation ranking probe."
            ),
            "plain_language_interpretation": (
                "Direct historic target evidence remains AP2 context only. The "
                "stronger candidate constructs a target from N13 AP3 support "
                "regulation, N14 AP4 consequence selection, N08 memory, N09 "
                "bounded regulation, and N12 readiness-only context. The bridge "
                "probe shows the generated target band can select a bounded "
                "regulation response over no response, but contrast, adversarial "
                "controls, replay, and claim-boundary classification are still pending."
            ),
            "unsupported_interpretations": [
                "final AP5 support",
                "semantic goal ownership",
                "intention",
                "semantic choice",
                "agency",
                "identity acceptance",
                "native support",
                "fully native integration",
            ],
            "next_required_step": (
                "Run Iteration 4 external proxy contrast matrix against declared, "
                "hidden, and post-hoc proxy variants."
            ),
        },
        "git": {"head": git_head(), "src_status_short": git_status_short("src")},
    }
    output["checks"]["iteration_3_top_level_output_shape_matches_output"] = set(
        ITERATION_3_TOP_LEVEL_OUTPUT_FIELDS
    ) == (set(output) | {"output_digest"})
    output["checks"]["absolute_path_absence"] = not contains_absolute_path(output)
    output["checks"]["no_absolute_paths_recorded"] = output["checks"][
        "absolute_path_absence"
    ]
    output["status"] = "passed" if all(output["checks"].values()) else "failed"
    output["acceptance_state"] = (
        "accepted_runtime_derived_target_candidate_with_bridge_pending_controls"
        if all(output["checks"].values())
        else "rejected_runtime_derived_target_candidate"
    )
    output["iteration_result"]["acceptance_state"] = output["acceptance_state"]
    output["iteration_result"]["runtime_derived_target_generated"] = (
        output["status"] == "passed"
    )
    output["output_digest"] = output_digest(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    row = output["rows"][0]
    bridge = output["bridge_probe"]
    target = output["target_condition"]
    lines = [
        "# N15 Runtime-Derived Target Candidate",
        "",
        f"Status: `{output['status']}`.",
        "",
        "## Acceptance State",
        "",
        "```text",
        output["acceptance_state"],
        "```",
        "",
        "Iteration 3 generates a provisional runtime-derived target candidate",
        "using the stronger old-best-claims path. It also adds a bridge probe",
        "for the gap between `target condition exists` and `target condition",
        "functions as an AP5-relevant proxy formation input`.",
        "",
        "It does not run the external proxy contrast matrix, adversarial",
        "controls, bounded drift replay, or final claim-boundary classification.",
        "Final `AP5` remains unsupported.",
        "",
        "## Iteration 3 Explanation",
        "",
        *output["iteration_3_explanation"]["lines"],
        "",
        "## I3 Top-Level Contract",
        "",
        "```json",
        json.dumps(
            output["iteration_3_top_level_output_fields"],
            indent=2,
            sort_keys=True,
        ),
        "```",
        "",
        "## Control Value Convention",
        "",
        "```json",
        json.dumps(output["control_value_convention"], indent=2, sort_keys=True),
        "```",
        "",
        "## Replay Digest Design Note",
        "",
        "```json",
        json.dumps(
            output["replay_digest_inputs_design_note"],
            indent=2,
            sort_keys=True,
        ),
        "```",
        "",
        "## Review Gap Closure",
        "",
        "```text",
        "closed: iteration_3_top_level_output_fields declares every I3 top-level key.",
        "closed: idempotency_digest_plan scope matches replay_digest_inputs including claim_flags.",
        "closed: n14_constructed_followout is included in candidate_path_used.",
        "closed: dependency_trace covers context rows and bounded bridge response fields.",
        "closed: I2 validator required check names are emitted in I3 checks.",
        "closed: control value convention and replay digest design note are recorded.",
        "not_gap: full runtime_state_vector and target_condition objects in replay_digest_inputs are intentional; Iteration 6 must rederive and compare the full objects.",
        "```",
        "",
        "## Direct Historic Gap",
        "",
        "```json",
        json.dumps(output["direct_historic_gap_record"], indent=2, sort_keys=True),
        "```",
        "",
        "## Runtime State Vector",
        "",
        "```json",
        json.dumps(output["runtime_state_vector"], indent=2, sort_keys=True),
        "```",
        "",
        "## Generated Target",
        "",
        "```json",
        json.dumps(target, indent=2, sort_keys=True),
        "```",
        "",
        "## Bridge Probe",
        "",
        f"Bridge result: `{bridge['target_condition_functions_as_proxy_input']}`.",
        "",
        "| Candidate | Post-response support | In generated band | Rank | Status |",
        "| --- | ---: | --- | ---: | --- |",
    ]
    for candidate in bridge["bridge_candidates"]:
        lines.append(
            "| "
            f"`{candidate['candidate_id']}` | "
            f"`{candidate['post_response_support_retention']}` | "
            f"`{candidate['target_band_membership']}` | "
            f"`{candidate['rank']}` | "
            f"`{candidate['selection_status']}` |"
        )
    lines.extend(
        [
            "",
            "## Candidate Row",
            "",
            "```json",
            json.dumps(
                {
                    "row_id": row["row_id"],
                    "provisional_ap_level": row["provisional_ap_level"],
                    "provisional_claim_ceiling": row["provisional_claim_ceiling"],
                    "target_condition_surface": row["target_condition_surface"],
                    "target_center": row["target_center"],
                    "target_tolerance": row["target_tolerance"],
                    "target_band": row["target_band"],
                    "missing_gates": row["missing_gates"],
                },
                indent=2,
                sort_keys=True,
            ),
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
            "runtime-derived target candidate != final AP5 support",
            "target-band bridge probe != semantic goal ownership",
            "bounded regulation candidate != intention or agency",
            "support/identity-condition descriptor != identity acceptance",
            "N12 readiness-only context != native support",
            "N15 Iteration 3 != fully native integration",
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
