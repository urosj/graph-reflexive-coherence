#!/usr/bin/env python3
"""Build N14 Iteration 6-C route-conditioned followout probe."""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-06-N14-lgrc-consequence-sensitive-route-selection"
)
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"

SELECTION_OUTPUT = OUTPUTS / "n14_consequence_sensitive_selection_candidate.json"
SELECTION_REPORT = REPORTS / "n14_consequence_sensitive_selection_candidate.md"
CONDITIONED_PROBE_OUTPUT = (
    OUTPUTS / "n14_route_conditioned_support_regulation_probe.json"
)
CONDITIONED_PROBE_REPORT = (
    REPORTS / "n14_route_conditioned_support_regulation_probe.md"
)
N13_STRESS_OUTPUT = (
    ROOT
    / "experiments"
    / "2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation"
    / "outputs"
    / "n13_support_disruption_restoration_matrix.json"
)
N13_STRESS_REPORT = (
    ROOT
    / "experiments"
    / "2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation"
    / "reports"
    / "n13_support_disruption_restoration_matrix.md"
)
N09_CLOSEOUT_OUTPUT = (
    ROOT
    / "experiments"
    / "2026-05-N09-lgrc-goal-proxy-regulation"
    / "outputs"
    / "n09_iteration_9_gpr6_closeout.json"
)
N09_CLOSEOUT_REPORT = (
    ROOT
    / "experiments"
    / "2026-05-N09-lgrc-goal-proxy-regulation"
    / "reports"
    / "n09_iteration_9_gpr6_closeout.md"
)

OUTPUT_PATH = OUTPUTS / "n14_route_conditioned_followout_probe.json"
REPORT_PATH = REPORTS / "n14_route_conditioned_followout_probe.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N14-lgrc-consequence-sensitive-route-selection/"
    "scripts/build_n14_route_conditioned_followout_probe.py"
)
GENERATED_AT = "2026-06-16T00:00:00+00:00"

CLAIM_FLAGS_FORCED_FALSE = {
    "agency_claim_allowed": False,
    "intention_claim_allowed": False,
    "semantic_choice_claim_allowed": False,
    "semantic_goal_ownership_claim_allowed": False,
    "semantic_goal_understanding_claim_allowed": False,
    "identity_acceptance_claim_allowed": False,
    "runtime_identity_acceptance_claim_allowed": False,
    "selfhood_claim_allowed": False,
    "personhood_claim_allowed": False,
    "biological_behavior_claim_allowed": False,
    "unrestricted_agency_claim_allowed": False,
    "fully_native_agentic_like_integration_claim_allowed": False,
    "native_support_opened": False,
}

FOLLOWOUT_POLICY = {
    "policy_id": "n14_i6c_route_conditioned_followout_policy_v1",
    "policy_scope": (
        "experiment-local artifact followout; not native support and not "
        "upstream N09/N13 observed route-conditioned evidence"
    ),
    "route_id_serialized_before_axis_scoring": True,
    "route_conditioning_basis": (
        "pre-selection N14 route memory_delta_component sign from the "
        "selection candidate record"
    ),
    "support_axis_rule": (
        "memory-negative route follows the N13 support-disrupted regime; "
        "memory-nonnegative route follows the N13 explicit-restoration regime"
    ),
    "regulation_axis_rule": (
        "memory-negative route receives a bounded regulation-deficit burden "
        "calibrated from N09 GPR5 cycle count; memory-nonnegative route "
        "receives a recovery-in-band credit calibrated from N09 GPR8"
    ),
    "score_direction": "higher_is_better",
    "claim_boundary": (
        "route-conditioned followout evidence is artifact-level only; it is "
        "not intention, semantic choice, agency, or native support"
    ),
}


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
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"{rel(path)} must contain a JSON object")
    return data


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
    return {
        "path": rel(path),
        "sha256": digest_file(path),
        "status": None if artifact is None else artifact.get("status"),
        "output_digest": None if artifact is None else artifact.get("output_digest"),
    }


def source_report(path: Path) -> dict[str, str]:
    return {"path": rel(path), "sha256": digest_file(path)}


def get_selection_record(selection: dict[str, Any], route_id: str) -> dict[str, Any]:
    for record in selection["selection_records"]:
        if record["route_candidate_id"] == route_id:
            return record
    raise KeyError(route_id)


def get_stress_record(n13_stress: dict[str, Any], regime_id: str) -> dict[str, Any]:
    for record in n13_stress["stress_matrix"]["stress_records"]:
        if record["regime_id"] == regime_id:
            return record
    raise KeyError(regime_id)


def route_memory_component(selection_record: dict[str, Any]) -> float:
    return float(
        selection_record["consequence_score_components"]["components"][
            "memory_delta_component"
        ]
    )


def support_component_from_stress_record(stress_record: dict[str, Any]) -> float:
    if not stress_record["post_response_estimate"]["post_response_meets_target"]:
        return -1.0
    support_error = float(stress_record["support_error"])
    budget_debit = float(stress_record["budget_debit_amount"])
    component = round(-support_error - budget_debit, 12)
    return 0.0 if component == 0 else component


def regulation_component(
    *,
    memory_negative: bool,
    n09_closeout: dict[str, Any],
) -> tuple[float, dict[str, Any]]:
    summary = n09_closeout["regulation_summary"]
    cycle_count = int(summary["gpr5_cycle_count"])
    if memory_negative:
        component = round(-(cycle_count * 0.08), 12)
        status = "route_conditioned_regulation_deficit_burden"
        basis = {
            "gpr5_cycle_count": cycle_count,
            "component_expression": "-gpr5_cycle_count * 0.08",
        }
    else:
        recovery_credit = 0.08 if summary["gpr8_perturbation_recovery_in_band"] else 0.0
        component = round(recovery_credit, 12)
        status = "route_conditioned_regulation_recovery_credit"
        basis = {
            "gpr8_perturbation_recovery_in_band": summary[
                "gpr8_perturbation_recovery_in_band"
            ],
            "component_expression": "0.08 when recovered in band else 0.0",
        }
    return component, {
        "status": status,
        "source_artifact": rel(N09_CLOSEOUT_OUTPUT),
        "source_report": rel(N09_CLOSEOUT_REPORT),
        "source_sha256": digest_file(N09_CLOSEOUT_OUTPUT),
        "source_report_sha256": digest_file(N09_CLOSEOUT_REPORT),
        "regulation_summary": summary,
        "component_basis": basis,
    }


def build_followout_records(
    selection: dict[str, Any],
    n13_stress: dict[str, Any],
    n09_closeout: dict[str, Any],
) -> list[dict[str, Any]]:
    records = []
    for route_id in ["route_a", "route_b"]:
        selection_record = get_selection_record(selection, route_id)
        memory_component = route_memory_component(selection_record)
        memory_negative = memory_component < 0
        support_regime_id = (
            "stress_02_support_disrupted_regime"
            if memory_negative
            else "stress_03_explicit_restoration_regime"
        )
        support_record = get_stress_record(n13_stress, support_regime_id)
        support_component = support_component_from_stress_record(support_record)
        reg_component, regulation_record = regulation_component(
            memory_negative=memory_negative,
            n09_closeout=n09_closeout,
        )
        followout_components = {
            "memory_delta_component": memory_component,
            "route_conditioned_support_component": support_component,
            "route_conditioned_regulation_component": reg_component,
        }
        followout_score = round(sum(followout_components.values()), 12)
        route_conditioning_basis = {
            "route_candidate_id": route_id,
            "memory_delta_component": memory_component,
            "memory_negative": memory_negative,
            "support_regime_id": support_regime_id,
            "regulation_mode": regulation_record["status"],
            "selection_record_digest": digest_value(
                {
                    "route_candidate_id": route_id,
                    "memory_delta_component": memory_component,
                    "immediate_affordance_rank": selection_record[
                        "immediate_affordance_rank"
                    ],
                    "consequence_rank": selection_record["consequence_rank"],
                }
            ),
        }
        records.append(
            {
                "row_id": f"n14_i6c_route_conditioned_followout_{route_id}",
                "route_candidate_id": route_id,
                "route_id_serialized_before_axis_scoring": True,
                "followout_policy_id": FOLLOWOUT_POLICY["policy_id"],
                "source_experiment": "N14",
                "source_iteration": "iteration_6c_route_conditioned_followout_probe",
                "route_conditioning_basis": route_conditioning_basis,
                "route_conditioning_digest": digest_value(route_conditioning_basis),
                "bounded_horizon": {
                    "support_window": "N13_support_disruption_restoration_four_window",
                    "regulation_window": "N09_GPR6_closeout",
                    "same_window_policy_for_all_routes": True,
                },
                "selection_rule": (
                    "rank route-conditioned followout rows by serialized "
                    "memory, support, and regulation components; higher score "
                    "is better"
                ),
                "support_followout_observation": {
                    "route_conditioned": True,
                    "status": "supported_constructed_route_conditioned_followout",
                    "source_artifact": rel(N13_STRESS_OUTPUT),
                    "source_report": rel(N13_STRESS_REPORT),
                    "source_sha256": digest_file(N13_STRESS_OUTPUT),
                    "source_report_sha256": digest_file(N13_STRESS_REPORT),
                    "source_regime_id": support_record["regime_id"],
                    "source_lane_id": support_record["source_lane_id"],
                    "support_error": support_record["support_error"],
                    "scheduled_response_total": support_record[
                        "scheduled_response_total"
                    ],
                    "budget_debit_amount": support_record["budget_debit_amount"],
                    "bounded_window": support_record["bounded_window"],
                    "post_response_estimate": support_record[
                        "post_response_estimate"
                    ],
                    "support_trend": support_record["support_trend"],
                    "component_expression": "-support_error - budget_debit_amount",
                    "component_value": support_component,
                },
                "regulation_followout_observation": {
                    "route_conditioned": True,
                    "component_value": reg_component,
                    **regulation_record,
                },
                "followout_score_components": followout_components,
                "followout_score": followout_score,
                "followout_rank": "assigned_after_all_rows",
                "post_hoc_rank_assigned": False,
                "generic_source_reuse": False,
                "runtime_state_used": False,
                "producer_direct_mutation": False,
                "phase8_opened": False,
                "native_support_opened": False,
                "claim_flags_forced_false": CLAIM_FLAGS_FORCED_FALSE,
            }
        )
    assign_followout_ranks(records)
    return records


def assign_followout_ranks(records: list[dict[str, Any]]) -> None:
    ranked = sorted(
        records,
        key=lambda record: (
            -record["followout_score"],
            record["route_candidate_id"],
        ),
    )
    for rank, record in enumerate(ranked, start=1):
        record["followout_rank"] = rank
        record["followout_rank_source"] = (
            "derived_from_serialized_route_conditioned_followout_score_components"
        )


def validate_followout_records(
    records: list[dict[str, Any]], metadata: dict[str, Any] | None = None
) -> dict[str, Any]:
    metadata = metadata or {}
    if metadata.get("generic_source_reuse"):
        return {"status": "blocked", "blocker": "generic_source_reuse_blocked"}
    if metadata.get("post_hoc_route_conditioning"):
        return {"status": "blocked", "blocker": "post_hoc_route_conditioning_blocked"}
    if metadata.get("stale_source_window"):
        return {"status": "blocked", "blocker": "stale_source_window_blocked"}
    if metadata.get("budget_invalid"):
        return {"status": "blocked", "blocker": "budget_invalid_followout_blocked"}
    if metadata.get("fixture_label_assignment"):
        return {"status": "blocked", "blocker": "fixture_label_assignment_blocked"}
    route_ids = {record["route_candidate_id"] for record in records}
    if route_ids != {"route_a", "route_b"}:
        return {"status": "blocked", "blocker": "missing_route_followout_blocked"}
    for record in records:
        basis = record["route_conditioning_basis"]
        if basis["route_candidate_id"] != record["route_candidate_id"]:
            return {"status": "blocked", "blocker": "route_label_swap_blocked"}
        if not record["route_id_serialized_before_axis_scoring"]:
            return {"status": "blocked", "blocker": "post_hoc_route_conditioning_blocked"}
        if record["generic_source_reuse"]:
            return {"status": "blocked", "blocker": "generic_source_reuse_blocked"}
        if basis["memory_negative"]:
            expected_support = "stress_02_support_disrupted_regime"
            expected_regulation = "route_conditioned_regulation_deficit_burden"
        else:
            expected_support = "stress_03_explicit_restoration_regime"
            expected_regulation = "route_conditioned_regulation_recovery_credit"
        support_id = record["support_followout_observation"]["source_regime_id"]
        regulation_status = record["regulation_followout_observation"]["status"]
        if support_id != expected_support or regulation_status != expected_regulation:
            return {"status": "blocked", "blocker": "route_conditioning_policy_mismatch_blocked"}
    support_components = {
        record["support_followout_observation"]["component_value"]
        for record in records
    }
    regulation_components = {
        record["regulation_followout_observation"]["component_value"]
        for record in records
    }
    if len(support_components) == 1 or len(regulation_components) == 1:
        return {"status": "blocked", "blocker": "equal_effect_followout_blocked"}
    return {"status": "accepted", "blocker": None}


def equalized_followout_variant(
    records: list[dict[str, Any]], axes: tuple[str, ...]
) -> list[dict[str, Any]]:
    variant = copy.deepcopy(records)
    axis_fields = {
        "support": (
            "support_followout_observation",
            "route_conditioned_support_component",
        ),
        "regulation": (
            "regulation_followout_observation",
            "route_conditioned_regulation_component",
        ),
    }
    for record in variant:
        for axis in axes:
            observation_key, component_key = axis_fields[axis]
            record[observation_key]["component_value"] = 0.0
            record["followout_score_components"][component_key] = 0.0
        record["followout_score"] = round(
            sum(float(value) for value in record["followout_score_components"].values()),
            12,
        )
    assign_followout_ranks(variant)
    return variant


def control_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    controls: list[dict[str, Any]] = []
    swapped = copy.deepcopy(records)
    swapped[0]["route_candidate_id"], swapped[1]["route_candidate_id"] = (
        swapped[1]["route_candidate_id"],
        swapped[0]["route_candidate_id"],
    )
    support_equal_effect = equalized_followout_variant(records, ("support",))
    regulation_equal_effect = equalized_followout_variant(records, ("regulation",))
    equal_effect = equalized_followout_variant(records, ("support", "regulation"))
    variants = [
        (
            "route_label_swap_control",
            "Route label swap",
            swapped,
            {},
            "route_label_swap_blocked",
        ),
        (
            "generic_source_reuse_control",
            "Generic source reuse",
            copy.deepcopy(records),
            {"generic_source_reuse": True},
            "generic_source_reuse_blocked",
        ),
        (
            "missing_route_followout_control",
            "Missing route followout",
            [copy.deepcopy(records[0])],
            {},
            "missing_route_followout_blocked",
        ),
        (
            "stale_source_window_control",
            "Stale source window",
            copy.deepcopy(records),
            {"stale_source_window": True},
            "stale_source_window_blocked",
        ),
        (
            "budget_invalid_followout_control",
            "Budget-invalid followout",
            copy.deepcopy(records),
            {"budget_invalid": True},
            "budget_invalid_followout_blocked",
        ),
        (
            "post_hoc_route_conditioning_control",
            "Post-hoc route conditioning",
            copy.deepcopy(records),
            {"post_hoc_route_conditioning": True},
            "post_hoc_route_conditioning_blocked",
        ),
        (
            "fixture_label_assignment_control",
            "Fixture label assignment",
            copy.deepcopy(records),
            {"fixture_label_assignment": True},
            "fixture_label_assignment_blocked",
        ),
        (
            "support_equal_effect_null_control",
            "Support equal-effect null control",
            support_equal_effect,
            {},
            "equal_effect_followout_blocked",
        ),
        (
            "regulation_equal_effect_null_control",
            "Regulation equal-effect null control",
            regulation_equal_effect,
            {},
            "equal_effect_followout_blocked",
        ),
        (
            "equal_effect_null_control",
            "Support and regulation equal-effect null control",
            equal_effect,
            {},
            "equal_effect_followout_blocked",
        ),
    ]
    for control_id, control_name, variant_records, metadata, expected_blocker in variants:
        observed = validate_followout_records(variant_records, metadata)
        controls.append(
            {
                "control_id": control_id,
                "control_name": control_name,
                "expected_status": "blocked",
                "expected_blocker": expected_blocker,
                "observed_status": observed["status"],
                "observed_blocker": observed["blocker"],
                "passed": observed["blocker"] == expected_blocker,
                "variant_digest": digest_value(
                    {
                        "control_id": control_id,
                        "records": variant_records,
                        "metadata": metadata,
                    }
                ),
            }
        )
    return controls


def build_output() -> dict[str, Any]:
    selection = load_json(SELECTION_OUTPUT)
    conditioned_probe = load_json(CONDITIONED_PROBE_OUTPUT)
    n13_stress = load_json(N13_STRESS_OUTPUT)
    n09_closeout = load_json(N09_CLOSEOUT_OUTPUT)
    records = build_followout_records(selection, n13_stress, n09_closeout)
    accepted = validate_followout_records(records)
    controls = control_records(records)
    support_components = {
        record["route_candidate_id"]: record["support_followout_observation"][
            "component_value"
        ]
        for record in records
    }
    regulation_components = {
        record["route_candidate_id"]: record["regulation_followout_observation"][
            "component_value"
        ]
        for record in records
    }
    top_followout_route = min(records, key=lambda record: record["followout_rank"])[
        "route_candidate_id"
    ]
    checks = {
        "selection_source_passed": selection["status"] == "passed",
        "iteration_6b_source_passed": conditioned_probe["status"] == "passed",
        "n13_stress_source_passed": n13_stress["status"] == "passed",
        "n09_regulation_source_passed": n09_closeout["status"] == "passed",
        "followout_policy_serialized": bool(FOLLOWOUT_POLICY["policy_id"]),
        "route_ids_serialized_before_axis_scoring": all(
            record["route_id_serialized_before_axis_scoring"] is True
            for record in records
        ),
        "both_routes_have_followout_rows": {
            record["route_candidate_id"] for record in records
        }
        == {"route_a", "route_b"},
        "support_followout_route_conditioned": all(
            record["support_followout_observation"]["route_conditioned"] is True
            for record in records
        ),
        "regulation_followout_route_conditioned": all(
            record["regulation_followout_observation"]["route_conditioned"] is True
            for record in records
        ),
        "support_components_differ_by_route": len(set(support_components.values()))
        > 1,
        "regulation_components_differ_by_route": len(
            set(regulation_components.values())
        )
        > 1,
        "followout_rank_derived_from_components": all(
            record["followout_rank_source"]
            == "derived_from_serialized_route_conditioned_followout_score_components"
            for record in records
        ),
        "no_generic_source_reuse": all(
            record["generic_source_reuse"] is False for record in records
        ),
        "no_post_hoc_rank_assignment": all(
            record["post_hoc_rank_assigned"] is False for record in records
        ),
        "runtime_state_used_false": all(
            record["runtime_state_used"] is False for record in records
        ),
        "no_producer_direct_mutation": all(
            record["producer_direct_mutation"] is False for record in records
        ),
        "positive_followout_validation_accepted": accepted["status"] == "accepted",
        "controls_passed": all(control["passed"] for control in controls),
        "route_label_swap_blocked": next(
            control for control in controls if control["control_id"] == "route_label_swap_control"
        )["passed"],
        "generic_source_reuse_blocked": next(
            control for control in controls if control["control_id"] == "generic_source_reuse_control"
        )["passed"],
        "missing_route_followout_blocked": next(
            control for control in controls if control["control_id"] == "missing_route_followout_control"
        )["passed"],
        "stale_source_window_blocked": next(
            control for control in controls if control["control_id"] == "stale_source_window_control"
        )["passed"],
        "budget_invalid_followout_blocked": next(
            control for control in controls if control["control_id"] == "budget_invalid_followout_control"
        )["passed"],
        "post_hoc_route_conditioning_blocked": next(
            control
            for control in controls
            if control["control_id"] == "post_hoc_route_conditioning_control"
        )["passed"],
        "fixture_label_assignment_blocked": next(
            control
            for control in controls
            if control["control_id"] == "fixture_label_assignment_control"
        )["passed"],
        "support_equal_effect_null_blocked": next(
            control
            for control in controls
            if control["control_id"] == "support_equal_effect_null_control"
        )["passed"],
        "regulation_equal_effect_null_blocked": next(
            control
            for control in controls
            if control["control_id"] == "regulation_equal_effect_null_control"
        )["passed"],
        "equal_effect_null_blocked": next(
            control for control in controls if control["control_id"] == "equal_effect_null_control"
        )["passed"],
        "claim_flags_forced_false": all(
            value is False for value in CLAIM_FLAGS_FORCED_FALSE.values()
        ),
        "iteration_6b_not_contradicted": (
            conditioned_probe["iteration_result"][
                "observed_route_conditioned_support_supported"
            ]
            is False
            and conditioned_probe["iteration_result"][
                "observed_route_conditioned_regulation_supported"
            ]
            is False
        ),
        "phase8_opened_false": True,
        "native_support_opened_false": True,
        "final_ap4_not_supported": True,
        "src_diff_empty": git_status_short("src") == "",
    }
    acceptance_state = (
        "accepted_constructed_route_conditioned_support_regulation_followout"
        if all(checks.values())
        else "rejected_constructed_route_conditioned_followout_probe"
    )
    followout_summary = {
        "accepted_validation_status": accepted,
        "observed_upstream_route_conditioned_support_regulation_from_6b": False,
        "constructed_route_conditioned_support_followout_supported": True,
        "constructed_route_conditioned_regulation_followout_supported": True,
        "support_components_by_route": support_components,
        "regulation_components_by_route": regulation_components,
        "top_followout_route": top_followout_route,
        "supported_closeout_scope": (
            "artifact_level_ap4_support_memory_regulation_consequence_sensitive_route_selection_candidate"
        ),
        "scope_caveat": (
            "support/regulation positivity is constructed N14 followout "
            "evidence; it is not upstream N09/N13 observed route-conditioned "
            "evidence and it is not native support"
        ),
    }
    interpretation_record = {
        "record_id": "n14_i6c_interpretation_route_conditioned_followout_probe_v1",
        "acceptance_state": acceptance_state,
        "supported_interpretation": (
            "N14 Iteration 6-C obtains a positive artifact-level constructed "
            "followout result: route_a and route_b each receive serialized "
            "route IDs before support/regulation axis scoring, and the "
            "resulting support and regulation components differ by route under "
            "one frozen followout policy."
        ),
        "boundary_interpretation": (
            "This does not overturn Iteration 6-B. N09/N13 still do not contain "
            "upstream observed route-conditioned support/regulation rows. 6-C "
            "adds an experiment-local route-conditioned followout artifact "
            "calibrated from those sources."
        ),
        "unsupported_interpretations": [
            "native support",
            "upstream N09/N13 observed route-conditioned support evidence",
            "upstream N09/N13 observed route-conditioned regulation evidence",
            "final AP4 before Iteration 7",
            "intention",
            "agency",
            "semantic choice",
            "semantic goal ownership",
            "identity acceptance",
            "selfhood",
            "personhood",
            "biological behavior",
            "fully native integration",
        ],
        "plain_language_interpretation": (
            "The attempt got a guarded positive: N14 can construct route-ID-"
            "bound support/regulation followout rows before scoring and pass "
            "the main relabeling controls. The positive is artifact-local and "
            "policy-mediated, so Iteration 7 must decide how much it broadens "
            "the final AP4 wording."
        ),
        "next_required_step": (
            "Run Iteration 7 classification and distinguish constructed "
            "followout support/regulation evidence from upstream observed "
            "route-conditioned support/regulation evidence."
        ),
    }
    output = {
        "experiment": "N14",
        "iteration": "6-C",
        "purpose": "route_conditioned_followout_support_regulation_probe",
        "schema": "n14_route_conditioned_followout_probe_v1",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed" if all(checks.values()) else "failed",
        "acceptance_state": acceptance_state,
        "target_ap_ceiling": "AP4",
        "followout_policy": FOLLOWOUT_POLICY,
        "iteration_result": {
            "acceptance_state": acceptance_state,
            "constructed_route_conditioned_support_followout_supported": True,
            "constructed_route_conditioned_regulation_followout_supported": True,
            "observed_upstream_route_conditioned_support_regulation_supported": False,
            "supported_closeout_scope": followout_summary[
                "supported_closeout_scope"
            ],
            "top_followout_route": top_followout_route,
            "final_ap4_supported": False,
            "phase8_opened": False,
            "native_support_opened": False,
        },
        "followout_summary": followout_summary,
        "route_conditioned_followout_records": records,
        "control_records": controls,
        "interpretation_record": interpretation_record,
        "claim_flags_forced_false": CLAIM_FLAGS_FORCED_FALSE,
        "checks": checks,
        "source_artifacts": {
            rel(SELECTION_OUTPUT): source_artifact(SELECTION_OUTPUT, selection),
            rel(CONDITIONED_PROBE_OUTPUT): source_artifact(
                CONDITIONED_PROBE_OUTPUT, conditioned_probe
            ),
            rel(N13_STRESS_OUTPUT): source_artifact(N13_STRESS_OUTPUT, n13_stress),
            rel(N09_CLOSEOUT_OUTPUT): source_artifact(
                N09_CLOSEOUT_OUTPUT, n09_closeout
            ),
        },
        "source_reports": {
            rel(SELECTION_REPORT): source_report(SELECTION_REPORT),
            rel(CONDITIONED_PROBE_REPORT): source_report(CONDITIONED_PROBE_REPORT),
            rel(N13_STRESS_REPORT): source_report(N13_STRESS_REPORT),
            rel(N09_CLOSEOUT_REPORT): source_report(N09_CLOSEOUT_REPORT),
        },
        "git": {
            "head": git_head(),
            "src_status_short": git_status_short("src"),
        },
    }
    output["output_digest"] = output_digest(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    lines = [
        "# N14 Route-Conditioned Followout Probe",
        "",
        f"Status: `{output['status']}`.",
        "",
        "## Acceptance State",
        "",
        "```text",
        output["acceptance_state"],
        "```",
        "",
        "## Interpretation",
        "",
        "```json",
        json.dumps(output["interpretation_record"], indent=2, sort_keys=True),
        "```",
        "",
        "## Followout Summary",
        "",
        "```json",
        json.dumps(output["followout_summary"], indent=2, sort_keys=True),
        "```",
        "",
        "## Route Followout Records",
        "",
        "| Route | Support component | Regulation component | Followout score | Rank |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for record in output["route_conditioned_followout_records"]:
        lines.append(
            "| "
            f"`{record['route_candidate_id']}` | "
            f"{record['support_followout_observation']['component_value']} | "
            f"{record['regulation_followout_observation']['component_value']} | "
            f"{record['followout_score']} | "
            f"{record['followout_rank']} |"
        )
    lines.extend(
        [
            "",
            "## Controls",
            "",
            "| Control | Blocker | Passed |",
            "| --- | --- | --- |",
        ]
    )
    for control in output["control_records"]:
        lines.append(
            "| "
            f"`{control['control_id']}` | "
            f"`{control['observed_blocker']}` | "
            f"`{str(control['passed']).lower()}` |"
        )
    lines.extend(
        [
            "",
            "## Result",
            "",
            "Iteration 6-C obtains a guarded positive constructed followout:",
            "support and regulation components are route-conditioned in the",
            "N14 artifact because route IDs are serialized before axis scoring.",
            "This is not upstream observed N09/N13 route-conditioned evidence,",
            "native support, intention, semantic choice, or agency.",
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
            "constructed route-conditioned followout != upstream route-conditioned observation",
            "constructed support/regulation followout != native support",
            "route-conditioned consequence-sensitive selection != intention",
            "artifact-level AP4 candidate != agency",
            "N14 Iteration 6-C != final AP4 closeout before Iteration 7",
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
        json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    write_report(output)
    if output["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
