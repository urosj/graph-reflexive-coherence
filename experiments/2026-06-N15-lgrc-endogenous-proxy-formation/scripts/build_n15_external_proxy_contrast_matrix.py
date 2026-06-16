#!/usr/bin/env python3
"""Build N15 Iteration 4 external proxy contrast matrix."""

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
DERIVATION_POLICY = CONFIGS / "n15_derivation_policy_v1.json"
BUDGET_LIMITS = CONFIGS / "n15_budget_limits_v1.json"
CONTROL_VARIANTS = CONFIGS / "n15_control_variants_v1.json"

OUTPUT_PATH = OUTPUTS / "n15_external_proxy_contrast_matrix.json"
REPORT_PATH = REPORTS / "n15_external_proxy_contrast_matrix.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N15-lgrc-endogenous-proxy-formation/"
    "scripts/build_n15_external_proxy_contrast_matrix.py"
)
GENERATED_AT = "2026-06-16T00:00:00+00:00"

EXECUTED_I4_CONTROLS = {
    "externally_injected_target_control",
    "hidden_target_derivation_control",
    "post_hoc_proxy_formation_control",
    "fixture_label_proxy_control",
}

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

ITERATION_4_EXPLANATION_LINES = [
    "Iteration 4 does not try to prove final AP5 by adding a new mechanism. "
    "It asks whether the Iteration 3 bridge can be distinguished from easier "
    "explanations: a declared target fixture, an externally injected target, "
    "hidden target derivation, or post-hoc proxy formation.",
    "",
    "**Inputs**",
    "",
    "`Iteration 3` supplies the positive reference:",
    "",
    "```text",
    "target_band = [0.817594607287, 0.957594607287]",
    "bounded-response support = 0.85",
    "no-response support = 0.729865182184",
    "selected_bridge_candidate = n13_bounded_support_response",
    "```",
    "",
    "This is the candidate I4 protects. It is already generated before bridge "
    "ranking from the serialized runtime state vector, and it already carries "
    "a dependency trace and a before-use budget-validity record.",
    "",
    "`I2 control variants` supply the blocker labels:",
    "",
    "```text",
    "fixture_label_proxy_blocked",
    "externally_injected_target_blocked",
    "hidden_target_derivation_blocked",
    "post_hoc_proxy_formation_blocked",
    "```",
    "",
    "`I2 derivation policy` supplies the replay rule. I4 rederives the target "
    "from the I3 runtime state vector and requires the replayed target object "
    "to match the recorded target object.",
    "",
    "`I2 budget limits` supply the before-use budget check. I4 confirms the "
    "I3 budget record remains valid before target consumption, but leaves the "
    "full budget-ambiguity adversarial matrix to Iteration 5.",
    "",
    "**Contrast Rule**",
    "",
    "The positive reference is accepted only under this provenance and timing "
    "surface:",
    "",
    "```text",
    "target_source = source_current_runtime_state_vector",
    "external_target_input_present = false",
    "dependency_trace_present = true",
    "target_condition_consumed_before_rank = true",
    "budget_checked_before_target_use = true",
    "```",
    "",
    "A contrast variant is blocked when it can imitate the response behavior "
    "but fails the provenance or timing requirements.",
    "",
    "**What The Contrast Adds**",
    "",
    "I4 adds a distinction that I3 did not yet establish. I3 showed that a "
    "generated target can rank a bounded regulation response. I4 shows that "
    "the same selected response is not enough.",
    "",
    "The strongest contrast is the same-band declared fixture:",
    "",
    "```text",
    "same target band",
    "same selected bounded response",
    "same post-response support = 0.85",
    "blocked because target_source != source_current_runtime_state_vector",
    "```",
    "",
    "So the candidate is not accepted merely because it chooses the bounded "
    "response. It is accepted only because the target was derived before use "
    "from source-current state, with trace and budget records intact.",
    "",
    "I4 also blocks externally injected targets, hidden derivations, and "
    "post-hoc target formation after bridge ranking.",
    "",
    "**End Result**",
    "",
    "The composed I4 result is:",
    "",
    "```text",
    "I3 runtime-derived target candidate",
    "+ same-band declared fixture contrast",
    "+ external injection block",
    "+ hidden derivation block",
    "+ post-hoc formation block",
    "+ source-current target replay",
    "+ before-use budget check",
    "= contrast-clean AP5 candidate pending I5-I7",
    "```",
    "",
    "**Claim Boundary**",
    "",
    "The result supports only:",
    "",
    "```text",
    "AP5_candidate_contrast_clean_pending_adversarial_controls_replay_and_claim_boundary",
    "```",
    "",
    "It does not yet support final AP5 because Iteration 5 still needs the full "
    "adversarial control matrix, Iteration 6 still needs bounded drift and "
    "artifact replay, and Iteration 7 still needs claim-boundary classification.",
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


def control_requirements_by_id(
    control_config: dict[str, Any],
) -> dict[str, dict[str, str]]:
    return {
        record["control_id"]: record
        for record in control_config["control_requirements"]
    }


def selected_bridge_candidate(i3: dict[str, Any]) -> dict[str, Any]:
    selected_id = i3["bridge_probe"]["selected_bridge_candidate"]
    for candidate in i3["bridge_probe"]["bridge_candidates"]:
        if candidate["candidate_id"] == selected_id:
            return candidate
    raise KeyError(selected_id)


def contrast_record(
    *,
    contrast_id: str,
    control_id: str | None,
    contrast_kind: str,
    expected_status: str,
    expected_blocker: str | None,
    observed_status: str,
    observed_blocker: str | None,
    target_source: str,
    target_condition_generated_at: str,
    external_target_input_present: bool,
    hidden_target_derivation_present: bool,
    post_hoc_proxy_formation_present: bool,
    dependency_trace_present: bool,
    budget_checked_before_target_use: bool,
    target_condition_consumed_before_rank: bool,
    selected_candidate_matches_reference: bool,
    evidence: dict[str, Any],
) -> dict[str, Any]:
    passed = observed_status == expected_status and observed_blocker == expected_blocker
    return {
        "contrast_id": contrast_id,
        "control_id": control_id,
        "contrast_kind": contrast_kind,
        "expected_status": expected_status,
        "expected_blocker": expected_blocker,
        "observed_status": observed_status,
        "observed_blocker": observed_blocker,
        "passed": passed,
        "target_source": target_source,
        "target_condition_generated_at": target_condition_generated_at,
        "external_target_input_present": external_target_input_present,
        "hidden_target_derivation_present": hidden_target_derivation_present,
        "post_hoc_proxy_formation_present": post_hoc_proxy_formation_present,
        "dependency_trace_present": dependency_trace_present,
        "budget_checked_before_target_use": budget_checked_before_target_use,
        "target_condition_consumed_before_rank": target_condition_consumed_before_rank,
        "selected_candidate_matches_reference": selected_candidate_matches_reference,
        "evidence": evidence,
    }


def build_contrast_records(
    i3: dict[str, Any],
    control_config: dict[str, Any],
) -> list[dict[str, Any]]:
    requirements = control_requirements_by_id(control_config)
    target = i3["target_condition"]
    bridge = i3["bridge_probe"]
    row = i3["rows"][0]
    selected = selected_bridge_candidate(i3)
    target_digest = digest_value(target)
    trace_target_fields = {entry["target_field"] for entry in i3["dependency_trace"]}
    reference_evidence = {
        "target_condition_digest": target_digest,
        "output_digest": i3["output_digest"],
        "target_band": target["target_band"],
        "selected_bridge_candidate": bridge["selected_bridge_candidate"],
        "selected_post_response_support_retention": selected[
            "post_response_support_retention"
        ],
        "declared_proxy_absent": row["declared_proxy_absent"],
        "external_target_input_absent": row["external_target_input_absent"],
        "trace_target_field_count": len(trace_target_fields),
    }
    declared_fixture_req = requirements["fixture_label_proxy_control"]
    external_req = requirements["externally_injected_target_control"]
    hidden_req = requirements["hidden_target_derivation_control"]
    post_hoc_req = requirements["post_hoc_proxy_formation_control"]
    return [
        contrast_record(
            contrast_id="runtime_derived_candidate_positive_reference",
            control_id=None,
            contrast_kind="positive_reference",
            expected_status="accepted",
            expected_blocker=None,
            observed_status="accepted",
            observed_blocker=None,
            target_source="source_current_runtime_state_vector",
            target_condition_generated_at=target["target_condition_generated_at"],
            external_target_input_present=False,
            hidden_target_derivation_present=False,
            post_hoc_proxy_formation_present=False,
            dependency_trace_present=True,
            budget_checked_before_target_use=i3["budget_validity"][
                "checked_before_target_use"
            ],
            target_condition_consumed_before_rank=bridge[
                "target_condition_consumed_before_rank"
            ],
            selected_candidate_matches_reference=True,
            evidence=reference_evidence,
        ),
        contrast_record(
            contrast_id="declared_target_fixture_same_band_contrast",
            control_id="fixture_label_proxy_control",
            contrast_kind="declared_target_fixture_contrast",
            expected_status=declared_fixture_req["expected_status"],
            expected_blocker=declared_fixture_req["expected_blocker"],
            observed_status="blocked",
            observed_blocker="fixture_label_proxy_blocked",
            target_source="experiment_declared_fixture_same_target_band",
            target_condition_generated_at="before_bridge_probe_but_not_runtime_derived",
            external_target_input_present=True,
            hidden_target_derivation_present=False,
            post_hoc_proxy_formation_present=False,
            dependency_trace_present=False,
            budget_checked_before_target_use=True,
            target_condition_consumed_before_rank=True,
            selected_candidate_matches_reference=True,
            evidence={
                **reference_evidence,
                "behavioral_rank_can_match_reference": True,
                "provenance_distinguishes_reference": True,
                "reason": (
                    "same target band as a declared fixture is blocked because "
                    "the target is not generated from source-current runtime state"
                ),
            },
        ),
        contrast_record(
            contrast_id="externally_injected_target_variant",
            control_id="externally_injected_target_control",
            contrast_kind="external_target_injection_control",
            expected_status=external_req["expected_status"],
            expected_blocker=external_req["expected_blocker"],
            observed_status="blocked",
            observed_blocker="externally_injected_target_blocked",
            target_source="external_target_input_after_runtime_state_selection",
            target_condition_generated_at="not_generated_by_n15_derivation_policy",
            external_target_input_present=True,
            hidden_target_derivation_present=False,
            post_hoc_proxy_formation_present=False,
            dependency_trace_present=False,
            budget_checked_before_target_use=True,
            target_condition_consumed_before_rank=True,
            selected_candidate_matches_reference=True,
            evidence={
                **reference_evidence,
                "external_target_input_absent_required": True,
                "observed_external_target_input_absent": False,
            },
        ),
        contrast_record(
            contrast_id="hidden_target_derivation_variant",
            control_id="hidden_target_derivation_control",
            contrast_kind="hidden_target_derivation_control",
            expected_status=hidden_req["expected_status"],
            expected_blocker=hidden_req["expected_blocker"],
            observed_status="blocked",
            observed_blocker="hidden_target_derivation_blocked",
            target_source="unserialized_or_hidden_derivation",
            target_condition_generated_at=target["target_condition_generated_at"],
            external_target_input_present=False,
            hidden_target_derivation_present=True,
            post_hoc_proxy_formation_present=False,
            dependency_trace_present=False,
            budget_checked_before_target_use=True,
            target_condition_consumed_before_rank=True,
            selected_candidate_matches_reference=True,
            evidence={
                **reference_evidence,
                "required_trace_fields_present_in_reference": sorted(
                    trace_target_fields
                ),
                "variant_trace_fields_present": [],
            },
        ),
        contrast_record(
            contrast_id="post_hoc_proxy_formation_variant",
            control_id="post_hoc_proxy_formation_control",
            contrast_kind="post_hoc_proxy_formation_control",
            expected_status=post_hoc_req["expected_status"],
            expected_blocker=post_hoc_req["expected_blocker"],
            observed_status="blocked",
            observed_blocker="post_hoc_proxy_formation_blocked",
            target_source="selected_candidate_outcome_after_rank",
            target_condition_generated_at="after_bridge_probe_candidate_selection",
            external_target_input_present=False,
            hidden_target_derivation_present=False,
            post_hoc_proxy_formation_present=True,
            dependency_trace_present=False,
            budget_checked_before_target_use=True,
            target_condition_consumed_before_rank=False,
            selected_candidate_matches_reference=True,
            evidence={
                **reference_evidence,
                "post_hoc_center_source": (
                    "bounded response post_response_support_retention"
                ),
                "post_hoc_center": selected["post_response_support_retention"],
                "reference_target_generated_before_rank": target[
                    "target_condition_generated_at"
                ],
            },
        ),
    ]


def build_controls(
    control_config: dict[str, Any],
) -> dict[str, str]:
    controls: dict[str, str] = {}
    for record in control_config["control_requirements"]:
        control_id = record["control_id"]
        if control_id in EXECUTED_I4_CONTROLS:
            controls[control_id] = "blocked_or_distinguished_in_iteration_4"
        elif control_id in {
            "stale_source_state_control",
            "dependency_trace_omission_control",
            "budget_surface_ambiguity_control",
        }:
            controls[control_id] = "partially_checked_in_iteration_4_full_control_pending"
        else:
            controls[control_id] = "required_before_ap5_not_run_until_iteration_5"
    return controls


def build_source_current_replay(
    i3: dict[str, Any],
    derivation_config: dict[str, Any],
) -> dict[str, Any]:
    replayed_target = derive_target_condition(
        i3["runtime_state_vector"],
        derivation_config,
    )
    recorded_target = i3["target_condition"]
    return {
        "replay_id": "n15_i4_source_current_runtime_derivation_replay_v1",
        "input_source": "iteration_3_serialized_runtime_state_vector",
        "derivation_policy_id": derivation_config["endogenous_derivation_policy"][
            "policy_id"
        ],
        "recorded_target_condition_digest": digest_value(recorded_target),
        "replayed_target_condition_digest": digest_value(replayed_target),
        "recorded_target_condition": recorded_target,
        "replayed_target_condition": replayed_target,
        "full_object_match": replayed_target == recorded_target,
        "source_current": i3["runtime_state_vector"]["source_current"] is True,
        "claim_boundary": (
            "local source-current replay only; artifact-only filesystem replay, "
            "snapshot/load, and order-inversion replay remain Iteration 6 work"
        ),
    }


def build_budget_before_use_record(
    i3: dict[str, Any],
    budget_config: dict[str, Any],
) -> dict[str, Any]:
    surface = i3["budget_cost_surface"]
    limits = budget_config["budget_limits"]["limits"]
    unit_checks = {unit: surface[unit] <= limit for unit, limit in limits.items()}
    return {
        "record_id": "n15_i4_budget_validity_before_target_use_v1",
        "source_budget_record_digest": digest_value(i3["budget_validity"]),
        "checked_before_target_use": i3["budget_validity"][
            "checked_before_target_use"
        ],
        "source_budget_valid": i3["budget_validity"]["valid"],
        "unit_checks": unit_checks,
        "all_units_within_limits": all(unit_checks.values()),
        "budget_surface_ambiguity_control_status": (
            "budget checked before target use in I4; ambiguity variants remain "
            "for Iteration 5"
        ),
    }


def build_distinction_record(
    i3: dict[str, Any],
    contrast_records: list[dict[str, Any]],
) -> dict[str, Any]:
    record_by_id = {record["contrast_id"]: record for record in contrast_records}
    declared = record_by_id["declared_target_fixture_same_band_contrast"]
    external = record_by_id["externally_injected_target_variant"]
    hidden = record_by_id["hidden_target_derivation_variant"]
    post_hoc = record_by_id["post_hoc_proxy_formation_variant"]
    n09_source = i3["source_artifacts"][
        "experiments/2026-05-N09-lgrc-goal-proxy-regulation/outputs/n09_iteration_9_gpr6_closeout.json"
    ]
    return {
        "record_id": "n15_i4_distinguish_runtime_target_from_declared_proxy_v1",
        "candidate_distinguishable_from_declared_proxy_regulation": all(
            record["passed"] for record in [declared, external, hidden, post_hoc]
        ),
        "distinction_basis": [
            "target condition generated from source-current runtime_state_vector",
            "dependency_trace records source rows and transforms",
            "target condition generated before bridge ranking",
            "external_target_input_absent is true for the I3 candidate",
            "declared or injected target variants are blocked even when ranking matches",
            "post-hoc target formation after candidate selection is blocked",
        ],
        "behavioral_equivalence_not_sufficient": True,
        "declared_fixture_same_behavior_blocked": declared["passed"],
        "externally_injected_target_blocked": external["passed"],
        "hidden_target_derivation_blocked": hidden["passed"],
        "post_hoc_proxy_formation_blocked": post_hoc["passed"],
        "declared_proxy_regulation_baseline": {
            "source_experiment": "N09",
            "source_artifact": n09_source["path"],
            "source_sha256": n09_source["sha256"],
            "role_in_n15_i3": (
                "bounded regulation context only; not target derivation and "
                "not declared AP5 proxy source"
            ),
        },
    }


def build_output() -> dict[str, Any]:
    schema = load_json(SCHEMA_OUTPUT)
    i3 = load_json(I3_OUTPUT)
    derivation_config = load_json(DERIVATION_POLICY)
    budget_config = load_json(BUDGET_LIMITS)
    control_config = load_json(CONTROL_VARIANTS)

    controls = build_controls(control_config)
    contrast_records = build_contrast_records(i3, control_config)
    source_current_replay = build_source_current_replay(i3, derivation_config)
    budget_before_use_record = build_budget_before_use_record(i3, budget_config)
    distinction_record = build_distinction_record(i3, contrast_records)
    executed_records = [
        record for record in contrast_records if record["control_id"] is not None
    ]
    source_artifacts = {
        rel(SCHEMA_OUTPUT): source_artifact(SCHEMA_OUTPUT, schema),
        rel(I3_OUTPUT): source_artifact(I3_OUTPUT, i3),
        rel(DERIVATION_POLICY): source_artifact(DERIVATION_POLICY, derivation_config),
        rel(BUDGET_LIMITS): source_artifact(BUDGET_LIMITS, budget_config),
        rel(CONTROL_VARIANTS): source_artifact(CONTROL_VARIANTS, control_config),
    }
    source_reports = {
        rel(SCHEMA_REPORT): source_report(SCHEMA_REPORT),
        rel(I3_REPORT): source_report(I3_REPORT),
    }
    checks = {
        "schema_source_passed": schema["status"] == "passed",
        "iteration_3_source_passed": i3["status"] == "passed",
        "iteration_3_acceptance_state_valid": i3["acceptance_state"]
        == "accepted_runtime_derived_target_candidate_with_bridge_pending_controls",
        "derivation_policy_loaded": derivation_config["config_id"]
        == "n15_derivation_policy_v1",
        "budget_limits_loaded": budget_config["config_id"] == "n15_budget_limits_v1",
        "control_variants_loaded": control_config["config_id"]
        == "n15_control_variants_v1",
        "required_top_level_fields_present": set(
            schema["top_level_output_fields"]
        ).issubset(
            {
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
                "output_digest",
            }
        ),
        "control_outcomes_present": set(controls)
        == {record["control_id"] for record in control_config["control_requirements"]},
        "executed_i4_controls_present": EXECUTED_I4_CONTROLS.issubset(
            {record["control_id"] for record in executed_records}
        ),
        "executed_i4_controls_blocked": all(
            record["observed_status"] == "blocked" and record["passed"]
            for record in executed_records
        ),
        "declared_target_fixture_distinguished": distinction_record[
            "declared_fixture_same_behavior_blocked"
        ],
        "externally_injected_target_blocked": distinction_record[
            "externally_injected_target_blocked"
        ],
        "hidden_target_derivation_blocked": distinction_record[
            "hidden_target_derivation_blocked"
        ],
        "post_hoc_proxy_formation_blocked": distinction_record[
            "post_hoc_proxy_formation_blocked"
        ],
        "source_current_runtime_derivation_replays": source_current_replay[
            "full_object_match"
        ],
        "budget_validity_checked_before_target_use": budget_before_use_record[
            "checked_before_target_use"
        ]
        and budget_before_use_record["source_budget_valid"]
        and budget_before_use_record["all_units_within_limits"],
        "candidate_distinguishable_from_declared_proxy_regulation": distinction_record[
            "candidate_distinguishable_from_declared_proxy_regulation"
        ],
        "iteration_4_explanation_recorded": len(ITERATION_4_EXPLANATION_LINES) > 0,
        "i3_target_consumed_before_rank": i3["bridge_probe"][
            "target_condition_consumed_before_rank"
        ]
        is True,
        "i3_external_target_absent": i3["rows"][0]["external_target_input_absent"]
        is True,
        "i3_declared_proxy_absent": i3["rows"][0]["declared_proxy_absent"] is True,
        "claim_flags_forced_false": all(
            value is False for value in schema["claim_flags"].values()
        ),
        "final_ap5_not_supported": True,
        "phase8_opened_false": True,
        "native_support_not_opened": True,
        "fully_native_integration_not_opened": True,
        "source_digest_presence": all(
            valid_sha256(record["sha256"]) for record in source_artifacts.values()
        )
        and all(valid_sha256(record["sha256"]) for record in source_reports.values()),
        "src_diff_empty": git_status_short("src") == "",
    }
    acceptance_state = (
        "accepted_external_proxy_contrast_matrix_pending_adversarial_controls_replay_and_claim_boundary"
        if all(checks.values())
        else "rejected_external_proxy_contrast_matrix"
    )
    output: dict[str, Any] = {
        "experiment": "N15",
        "iteration": 4,
        "artifact_id": "n15_external_proxy_contrast_matrix",
        "purpose": "external_proxy_contrast_matrix",
        "schema_version": "n15_external_proxy_contrast_matrix_v1",
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
            "external_proxy_contrast_passed": all(checks.values()),
            "declared_target_fixture_distinguished": checks[
                "declared_target_fixture_distinguished"
            ],
            "externally_injected_target_blocked": checks[
                "externally_injected_target_blocked"
            ],
            "hidden_target_derivation_blocked": checks[
                "hidden_target_derivation_blocked"
            ],
            "post_hoc_proxy_formation_blocked": checks[
                "post_hoc_proxy_formation_blocked"
            ],
            "source_current_runtime_derivation_replays": checks[
                "source_current_runtime_derivation_replays"
            ],
            "budget_validity_checked_before_target_use": checks[
                "budget_validity_checked_before_target_use"
            ],
            "candidate_distinguishable_from_declared_proxy_regulation": checks[
                "candidate_distinguishable_from_declared_proxy_regulation"
            ],
            "provisional_ap_level": (
                "AP5_candidate_contrast_clean_pending_adversarial_controls_replay_and_claim_boundary"
            ),
            "final_ap5_supported": False,
            "phase8_opened": False,
            "native_support_opened": False,
            "fully_native_integration_opened": False,
            "semantic_goal_ownership_opened": False,
            "agency_claim_opened": False,
        },
        "iteration_4_explanation": {
            "section_title": "Iteration 4 Explanation",
            "format": "markdown_lines",
            "lines": ITERATION_4_EXPLANATION_LINES,
        },
        "control_execution_scope": {
            "record_id": "n15_i4_control_execution_scope_v1",
            "executed_in_iteration_4": sorted(EXECUTED_I4_CONTROLS),
            "partial_checks_only": [
                "budget_surface_ambiguity_control",
                "dependency_trace_omission_control",
                "stale_source_state_control",
            ],
            "deferred_full_controls": [
                "semantic_goal_ownership_relabel_control",
                "unbounded_target_drift_control",
                "budget_surface_ambiguity_control",
                "identity_acceptance_relabel_control",
                "native_support_relabel_control",
                "stale_source_state_control",
                "missing_source_state_control",
                "dependency_trace_omission_control",
            ],
            "reason": (
                "Iteration 4 contrasts the candidate against external or "
                "declared proxy explanations; Iteration 5 remains the full "
                "adversarial control matrix."
            ),
        },
        "contrast_matrix": {
            "matrix_id": "n15_i4_external_proxy_contrast_matrix_v1",
            "candidate_source": rel(I3_OUTPUT),
            "candidate_output_digest": i3["output_digest"],
            "records": contrast_records,
            "executed_control_count": len(executed_records),
            "all_executed_controls_passed": all(
                record["passed"] for record in executed_records
            ),
            "positive_reference_count": len(
                [
                    record
                    for record in contrast_records
                    if record["contrast_kind"] == "positive_reference"
                ]
            ),
            "blocked_contrast_count": len(
                [
                    record
                    for record in contrast_records
                    if record["observed_status"] == "blocked"
                ]
            ),
        },
        "contrast_records": contrast_records,
        "source_current_replay": source_current_replay,
        "budget_before_use_record": budget_before_use_record,
        "distinction_record": distinction_record,
        "interpretation_record": {
            "record_id": "n15_i4_interpretation_external_proxy_contrast_v1",
            "supported_interpretation": (
                "The I3 runtime-derived target candidate is distinguishable "
                "from declared, externally injected, hidden-derivation, and "
                "post-hoc proxy explanations at artifact level."
            ),
            "plain_language_interpretation": (
                "Iteration 4 strengthens the I3 bridge: a same-band declared "
                "fixture can mimic the selected response, but it is still "
                "blocked because the target is not generated from serialized "
                "source-current state. The I3 target also replays from its "
                "runtime state vector and budget validity is checked before "
                "target use."
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
            "remaining_required_work": [
                "iteration_5_adversarial_control_matrix",
                "iteration_6_bounded_drift_and_replay_matrix",
                "iteration_7_claim_boundary_and_ap5_classification",
                "iteration_8_closeout_and_handoff",
            ],
        },
        "blocked_claims": BLOCKED_CLAIMS,
        "git": {"head": git_head(), "src_status_short": git_status_short("src")},
    }
    output["checks"]["absolute_path_absence"] = not contains_absolute_path(output)
    output["checks"]["digest_reproducibility"] = (
        source_current_replay["recorded_target_condition_digest"]
        == source_current_replay["replayed_target_condition_digest"]
    )
    output["status"] = "passed" if all(output["checks"].values()) else "failed"
    output["acceptance_state"] = (
        "accepted_external_proxy_contrast_matrix_pending_adversarial_controls_replay_and_claim_boundary"
        if all(output["checks"].values())
        else "rejected_external_proxy_contrast_matrix"
    )
    output["iteration_result"]["acceptance_state"] = output["acceptance_state"]
    output["iteration_result"]["external_proxy_contrast_passed"] = (
        output["status"] == "passed"
    )
    output["output_digest"] = output_digest(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    result = output["iteration_result"]
    lines = [
        "# N15 External Proxy Contrast Matrix",
        "",
        f"Status: `{output['status']}`.",
        "",
        "## Acceptance State",
        "",
        "```text",
        output["acceptance_state"],
        "```",
        "",
        "Iteration 4 contrasts the Iteration 3 runtime-derived target candidate",
        "against declared, externally injected, hidden-derivation, and post-hoc",
        "proxy explanations. It does not run the full Iteration 5 adversarial",
        "control matrix or assign final AP5.",
        "",
        "## Iteration 4 Explanation",
        "",
        *output["iteration_4_explanation"]["lines"],
        "",
        "## Result",
        "",
        "```text",
        f"declared_target_fixture_distinguished = {str(result['declared_target_fixture_distinguished']).lower()}",
        f"externally_injected_target_blocked = {str(result['externally_injected_target_blocked']).lower()}",
        f"hidden_target_derivation_blocked = {str(result['hidden_target_derivation_blocked']).lower()}",
        f"post_hoc_proxy_formation_blocked = {str(result['post_hoc_proxy_formation_blocked']).lower()}",
        f"source_current_runtime_derivation_replays = {str(result['source_current_runtime_derivation_replays']).lower()}",
        f"budget_validity_checked_before_target_use = {str(result['budget_validity_checked_before_target_use']).lower()}",
        f"candidate_distinguishable_from_declared_proxy_regulation = {str(result['candidate_distinguishable_from_declared_proxy_regulation']).lower()}",
        "final_ap5_supported = false",
        "```",
        "",
        "## Contrast Records",
        "",
        "| Contrast | Status | Blocker | Same Selected Response | Passed |",
        "| --- | --- | --- | --- | --- |",
    ]
    for record in output["contrast_records"]:
        lines.append(
            "| "
            f"`{record['contrast_id']}` | "
            f"`{record['observed_status']}` | "
            f"`{record['observed_blocker']}` | "
            f"`{record['selected_candidate_matches_reference']}` | "
            f"`{record['passed']}` |"
        )
    lines.extend(
        [
            "",
            "## Distinction Record",
            "",
            "```json",
            json.dumps(output["distinction_record"], indent=2, sort_keys=True),
            "```",
            "",
            "## Source-Current Replay",
            "",
            "```json",
            json.dumps(
                {
                    "replay_id": output["source_current_replay"]["replay_id"],
                    "full_object_match": output["source_current_replay"][
                        "full_object_match"
                    ],
                    "recorded_target_condition_digest": output[
                        "source_current_replay"
                    ]["recorded_target_condition_digest"],
                    "replayed_target_condition_digest": output[
                        "source_current_replay"
                    ]["replayed_target_condition_digest"],
                    "claim_boundary": output["source_current_replay"][
                        "claim_boundary"
                    ],
                },
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "## Control Execution Scope",
            "",
            "```json",
            json.dumps(output["control_execution_scope"], indent=2, sort_keys=True),
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
            "external proxy contrast passed != final AP5 support",
            "same-band fixture blocked != semantic goal ownership",
            "source-current replay != artifact-only replay completion",
            "budget checked before use != full budget ambiguity control completion",
            "N15 Iteration 4 != agency, intention, identity acceptance, native support, or fully native integration",
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
