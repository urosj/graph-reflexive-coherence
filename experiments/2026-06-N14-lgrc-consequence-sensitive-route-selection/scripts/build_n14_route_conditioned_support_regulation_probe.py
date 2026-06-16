#!/usr/bin/env python3
"""Build N14 Iteration 6-B route-conditioned support/regulation probe."""

from __future__ import annotations

import hashlib
import json
import copy
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

OBSERVED_ROUTE_OUTPUT = OUTPUTS / "n14_observed_route_specific_consequence_probe.json"
OBSERVED_ROUTE_REPORT = REPORTS / "n14_observed_route_specific_consequence_probe.md"
N13_SUPPORT_OUTPUT = (
    ROOT
    / "experiments"
    / "2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation"
    / "outputs"
    / "n13_support_seeking_regulation_candidate.json"
)
N13_SUPPORT_REPORT = (
    ROOT
    / "experiments"
    / "2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation"
    / "reports"
    / "n13_support_seeking_regulation_candidate.md"
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

OUTPUT_PATH = OUTPUTS / "n14_route_conditioned_support_regulation_probe.json"
REPORT_PATH = REPORTS / "n14_route_conditioned_support_regulation_probe.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N14-lgrc-consequence-sensitive-route-selection/"
    "scripts/build_n14_route_conditioned_support_regulation_probe.py"
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


def route_ids_from_observed_probe(observed_route_probe: dict[str, Any]) -> list[str]:
    records = observed_route_probe["observed_route_specific_consequence_records"]
    return sorted({record["route_candidate_id"] for record in records})


def summarize_support_lanes(n13_support: dict[str, Any]) -> list[dict[str, Any]]:
    lanes = n13_support["support_seeking_regulation_candidate"][
        "lane_response_records"
    ]
    summaries = []
    for lane in lanes:
        route_candidate_id = lane.get("route_candidate_id")
        summaries.append(
            {
                "lane_id": lane["lane_id"],
                "route_candidate_id": route_candidate_id,
                "route_conditioned": route_candidate_id is not None,
                "bounded_window": lane["bounded_window"],
                "budget_debit_surface": lane["budget_debit_surface"],
                "final_A_support_retention": lane["final_A_support_retention"],
                "support_error_signal": lane["support_error_signal"],
                "support_trend": lane["support_trend"],
                "support_margin": lane["support_margin"],
                "overcorrection_status": lane["overcorrection_status"],
                "response_magnitude_surface": {
                    "scheduled_response_total": lane["response_magnitude_surface"][
                        "scheduled_response_total"
                    ],
                    "out_of_envelope_blocked": lane["response_magnitude_surface"][
                        "out_of_envelope_blocked"
                    ],
                    "bounded_window_count": lane["response_magnitude_surface"][
                        "bounded_window_count"
                    ],
                },
                "lane_digest": lane["lane_digest"],
            }
        )
    return summaries


def summarize_regulation_source(n09_closeout: dict[str, Any]) -> dict[str, Any]:
    summary = n09_closeout["regulation_summary"]
    return {
        "route_candidate_id": None,
        "route_conditioned": False,
        "gpr5_cycle_count": summary["gpr5_cycle_count"],
        "gpr5_regulation_outcome_tag": summary["gpr5_regulation_outcome_tag"],
        "gpr8_perturbation_classification": summary[
            "gpr8_perturbation_classification"
        ],
        "gpr8_perturbation_recovery_in_band": summary[
            "gpr8_perturbation_recovery_in_band"
        ],
        "node_plus_packet_budget_error": summary["node_plus_packet_budget_error"],
    }


def build_route_conditioned_records(
    route_ids: list[str],
    support_lane_summaries: list[dict[str, Any]],
    regulation_summary: dict[str, Any],
) -> list[dict[str, Any]]:
    generic_support_lane_ids = [lane["lane_id"] for lane in support_lane_summaries]
    support_route_ids = {
        lane["route_candidate_id"]
        for lane in support_lane_summaries
        if lane["route_candidate_id"] is not None
    }
    regulation_route_ids: set[str] = set()
    records = []
    for route_id in route_ids:
        support_matches = [
            lane
            for lane in support_lane_summaries
            if lane["route_candidate_id"] == route_id
        ]
        regulation_matches: list[dict[str, Any]] = []
        records.append(
            {
                "row_id": f"n14_i6b_route_conditioned_support_regulation_{route_id}",
                "route_candidate_id": route_id,
                "source_experiment": "N14",
                "source_iteration": (
                    "iteration_6b_route_conditioned_support_regulation_probe"
                ),
                "required_observed_row_shape": {
                    "route_candidate_id": route_id,
                    "axis": "support_or_regulation",
                    "bounded_horizon": "same_as_peer_route",
                    "budget_accounting": "same_as_peer_route",
                    "selection_rule": "same_as_peer_route",
                    "source_row_must_bind_axis_observation_to_route_id": True,
                },
                "observed_support_consequence": {
                    "route_specific": bool(support_matches),
                    "status": (
                        "supported_route_conditioned_observation"
                        if support_matches
                        else "unsupported_no_route_conditioned_support_observation"
                    ),
                    "matching_route_conditioned_source_rows": support_matches,
                    "generic_source_available": bool(support_lane_summaries),
                    "generic_lane_ids": generic_support_lane_ids,
                    "source_route_candidate_ids_observed": sorted(support_route_ids),
                    "generic_reuse_allowed": False,
                    "blocker": (
                        None
                        if support_matches
                        else "generic_support_source_reuse_blocked"
                    ),
                    "reason": (
                        "N13 support response lanes carry lane_id/support state, "
                        "not route_candidate_id observations"
                    ),
                },
                "observed_regulation_consequence": {
                    "route_specific": route_id in regulation_route_ids,
                    "status": "unsupported_no_route_conditioned_regulation_observation",
                    "matching_route_conditioned_source_rows": regulation_matches,
                    "generic_source_available": True,
                    "generic_regulation_summary": regulation_summary,
                    "source_route_candidate_ids_observed": sorted(regulation_route_ids),
                    "generic_reuse_allowed": False,
                    "blocker": "generic_regulation_source_reuse_blocked",
                    "reason": (
                        "N09 GPR6 closeout records bounded regulation summary, "
                        "not route_candidate_id observations"
                    ),
                },
                "same_horizon_requirement": {
                    "required": True,
                    "route_conditioned_support_horizon_supported": bool(
                        support_matches
                    ),
                    "route_conditioned_regulation_horizon_supported": False,
                    "generic_support_bounded_windows_present": all(
                        lane["bounded_window"]["within_bounded_window"]
                        for lane in support_lane_summaries
                    ),
                    "generic_regulation_bounded_window_present": True,
                    "status": "not_validated_without_route_conditioned_rows",
                },
                "same_budget_accounting_requirement": {
                    "required": True,
                    "route_conditioned_support_budget_supported": bool(
                        support_matches
                    ),
                    "route_conditioned_regulation_budget_supported": False,
                    "generic_support_budget_accounting_present": all(
                        "budget_debit_surface" in lane
                        for lane in support_lane_summaries
                    ),
                    "generic_regulation_budget_accounting_present": (
                        regulation_summary["node_plus_packet_budget_error"] == 0.0
                    ),
                    "status": "not_validated_without_route_conditioned_rows",
                },
                "same_selection_rule_requirement": {
                    "required": True,
                    "selection_rule": (
                        "support/regulation components may influence route "
                        "selection only when the source row is route-conditioned"
                    ),
                    "status": "blocked_for_support_and_regulation_axes",
                },
                "route_conditioned_component_status": {
                    "support_component": (
                        "supported"
                        if support_matches
                        else "blocked_missing_route_conditioned_observation"
                    ),
                    "regulation_component": (
                        "blocked_missing_route_conditioned_observation"
                    ),
                    "post_hoc_rank_assigned": False,
                    "hidden_route_conditioning_used": False,
                },
                "claim_flags_forced_false": CLAIM_FLAGS_FORCED_FALSE,
            }
        )
    return records


def blocked(blocker: str) -> dict[str, Any]:
    return {"observed_status": "blocked", "observed_blocker": blocker}


def accepted() -> dict[str, Any]:
    return {"observed_status": "accepted", "observed_blocker": None}


def validate_probe_records(
    records: list[dict[str, Any]], metadata: dict[str, Any]
) -> dict[str, Any]:
    if metadata.get("stale_route_observation") is True:
        return blocked("stale_route_observation_blocked")
    if metadata.get("budget_invalid_consequence") is True:
        return blocked("budget_invalid_consequence_blocked")
    if metadata.get("post_hoc_route_conditioning") is True:
        return blocked("post_hoc_route_conditioning_blocked")
    if {record["route_candidate_id"] for record in records} != {"route_a", "route_b"}:
        return blocked("missing_route_observation_blocked")
    for record in records:
        if (
            record["required_observed_row_shape"]["route_candidate_id"]
            != record["route_candidate_id"]
        ):
            return blocked("route_label_swap_blocked")
        support = record["observed_support_consequence"]
        regulation = record["observed_regulation_consequence"]
        if (
            support["generic_reuse_allowed"]
            or regulation["generic_reuse_allowed"]
            or (
                support["route_specific"]
                and not support["matching_route_conditioned_source_rows"]
            )
            or (
                regulation["route_specific"]
                and not regulation["matching_route_conditioned_source_rows"]
            )
        ):
            return blocked("generic_source_reuse_blocked")
    return accepted()


def swapped_route(route_id: str) -> str:
    return {"route_a": "route_b", "route_b": "route_a"}[route_id]


def build_controls(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    controls: list[dict[str, Any]] = []
    swapped = copy.deepcopy(records)
    for record in swapped:
        record["route_candidate_id"] = swapped_route(record["route_candidate_id"])
    generic_reuse = copy.deepcopy(records)
    for record in generic_reuse:
        record["observed_support_consequence"]["route_specific"] = True
        record["observed_support_consequence"]["generic_reuse_allowed"] = True
        record["observed_regulation_consequence"]["route_specific"] = True
        record["observed_regulation_consequence"]["generic_reuse_allowed"] = True
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
            generic_reuse,
            {},
            "generic_source_reuse_blocked",
        ),
        (
            "missing_route_observation_control",
            "Missing route observation",
            [copy.deepcopy(records[0])],
            {},
            "missing_route_observation_blocked",
        ),
        (
            "stale_route_observation_control",
            "Stale route observation",
            copy.deepcopy(records),
            {"stale_route_observation": True},
            "stale_route_observation_blocked",
        ),
        (
            "budget_invalid_consequence_control",
            "Budget-invalid consequence",
            copy.deepcopy(records),
            {"budget_invalid_consequence": True},
            "budget_invalid_consequence_blocked",
        ),
        (
            "post_hoc_route_conditioning_control",
            "Post-hoc route conditioning",
            copy.deepcopy(records),
            {"post_hoc_route_conditioning": True},
            "post_hoc_route_conditioning_blocked",
        ),
    ]
    for control_id, control_name, variant_records, metadata, expected_blocker in variants:
        observed = validate_probe_records(variant_records, metadata)
        controls.append(
            {
                "control_id": control_id,
                "control_name": control_name,
                "expected_status": "blocked",
                "expected_blocker": expected_blocker,
                "observed_status": observed["observed_status"],
                "observed_blocker": observed["observed_blocker"],
                "passed": observed["observed_blocker"] == expected_blocker,
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
    observed_route_probe = load_json(OBSERVED_ROUTE_OUTPUT)
    n13_support = load_json(N13_SUPPORT_OUTPUT)
    n09_closeout = load_json(N09_CLOSEOUT_OUTPUT)
    route_ids = route_ids_from_observed_probe(observed_route_probe)
    support_lane_summaries = summarize_support_lanes(n13_support)
    regulation_summary = summarize_regulation_source(n09_closeout)
    records = build_route_conditioned_records(
        route_ids, support_lane_summaries, regulation_summary
    )
    controls = build_controls(records)
    support_supported = any(
        record["observed_support_consequence"]["route_specific"]
        for record in records
    )
    regulation_supported = any(
        record["observed_regulation_consequence"]["route_specific"]
        for record in records
    )
    supported_closeout_scope = (
        "artifact_level_ap4_memory_dominant_consequence_sensitive_route_selection_candidate"
    )
    if support_supported and regulation_supported:
        supported_closeout_scope = (
            "artifact_level_ap4_support_memory_regulation_consequence_sensitive_route_selection_candidate"
        )
    elif support_supported:
        supported_closeout_scope = (
            "artifact_level_ap4_support_memory_consequence_sensitive_route_selection_candidate"
        )
    elif regulation_supported:
        supported_closeout_scope = (
            "artifact_level_ap4_memory_regulation_consequence_sensitive_route_selection_candidate"
        )

    route_conditioned_probe_summary = {
        "route_ids_tested": route_ids,
        "observed_route_conditioned_support_supported": support_supported,
        "observed_route_conditioned_regulation_supported": regulation_supported,
        "generic_support_source_available": bool(support_lane_summaries),
        "generic_regulation_source_available": bool(regulation_summary),
        "generic_source_reuse_allowed": False,
        "supported_closeout_scope": supported_closeout_scope,
        "memory_dominant_closeout_still_required": (
            not support_supported and not regulation_supported
        ),
        "stronger_support_or_regulation_closeout_available": (
            support_supported or regulation_supported
        ),
    }
    checks = {
        "observed_route_probe_source_passed": observed_route_probe["status"]
        == "passed",
        "n13_support_source_passed": n13_support["status"] == "passed",
        "n09_regulation_source_passed": n09_closeout["status"] == "passed",
        "route_ids_requested": route_ids == ["route_a", "route_b"],
        "support_route_conditioned_rows_absent": not support_supported,
        "regulation_route_conditioned_rows_absent": not regulation_supported,
        "generic_support_source_available": bool(support_lane_summaries),
        "generic_regulation_source_available": bool(regulation_summary),
        "support_generic_reuse_blocked": all(
            record["observed_support_consequence"]["generic_reuse_allowed"] is False
            and record["observed_support_consequence"]["blocker"]
            == "generic_support_source_reuse_blocked"
            for record in records
        ),
        "regulation_generic_reuse_blocked": all(
            record["observed_regulation_consequence"]["generic_reuse_allowed"]
            is False
            and record["observed_regulation_consequence"]["blocker"]
            == "generic_regulation_source_reuse_blocked"
            for record in records
        ),
        "same_horizon_not_claimed_without_route_rows": all(
            record["same_horizon_requirement"]["status"]
            == "not_validated_without_route_conditioned_rows"
            for record in records
        ),
        "same_budget_not_claimed_without_route_rows": all(
            record["same_budget_accounting_requirement"]["status"]
            == "not_validated_without_route_conditioned_rows"
            for record in records
        ),
        "selection_rule_blocks_unconditioned_axes": all(
            record["same_selection_rule_requirement"]["status"]
            == "blocked_for_support_and_regulation_axes"
            for record in records
        ),
        "controls_passed": all(control["passed"] for control in controls),
        "route_label_swap_blocked": next(
            control
            for control in controls
            if control["control_id"] == "route_label_swap_control"
        )["passed"],
        "generic_source_reuse_blocked": next(
            control
            for control in controls
            if control["control_id"] == "generic_source_reuse_control"
        )["passed"],
        "missing_route_observation_blocked": next(
            control
            for control in controls
            if control["control_id"] == "missing_route_observation_control"
        )["passed"],
        "stale_route_observation_blocked": next(
            control
            for control in controls
            if control["control_id"] == "stale_route_observation_control"
        )["passed"],
        "budget_invalid_consequence_blocked": next(
            control
            for control in controls
            if control["control_id"] == "budget_invalid_consequence_control"
        )["passed"],
        "post_hoc_route_conditioning_blocked": next(
            control
            for control in controls
            if control["control_id"] == "post_hoc_route_conditioning_control"
        )["passed"],
        "memory_dominant_closeout_scope_preserved": (
            supported_closeout_scope
            == "artifact_level_ap4_memory_dominant_consequence_sensitive_route_selection_candidate"
        ),
        "claim_flags_forced_false": all(
            value is False for value in CLAIM_FLAGS_FORCED_FALSE.values()
        ),
        "phase8_opened_false": True,
        "native_support_opened_false": True,
        "final_ap4_not_supported": True,
        "src_diff_empty": git_status_short("src") == "",
    }
    acceptance_state = (
        "accepted_route_conditioned_support_regulation_probe_no_route_specific_support_regulation"
        if all(checks.values())
        else "rejected_route_conditioned_support_regulation_probe"
    )
    interpretation_record = {
        "record_id": (
            "n14_i6b_interpretation_route_conditioned_support_regulation_probe_v1"
        ),
        "acceptance_state": acceptance_state,
        "supported_interpretation": (
            "N14 Iteration 6-B attempts to obtain route-conditioned support "
            "and regulation consequence evidence. Current N13 support lanes "
            "and N09 regulation summaries do not bind observed support or "
            "regulation consequences to route_a or route_b, so support and "
            "regulation remain generic source-compatible axes only."
        ),
        "unsupported_interpretations": [
            "observed route-conditioned support consequence support",
            "observed route-conditioned regulation consequence support",
            "support+memory AP4 closeout from current sources",
            "memory+regulation AP4 closeout from current sources",
            "support+memory+regulation AP4 closeout from current sources",
            "final AP4 support before Iteration 7 classification",
            "intention",
            "agency",
            "semantic choice",
            "semantic goal ownership",
            "identity acceptance",
            "selfhood",
            "personhood",
            "biological behavior",
            "native support",
            "fully native integration",
        ],
        "plain_language_interpretation": (
            "6-B does not find the stronger support/regulation evidence N14 "
            "would need for a broader closeout. The available N09/N13 records "
            "are still useful as generic compatibility evidence, but they must "
            "not be recycled as route-conditioned observations. N14 should "
            "close, if Iteration 7 supports AP4, as memory-dominant."
        ),
        "next_required_step": (
            "Run Iteration 7 claim-boundary and AP4 classification using the "
            "memory-dominant route-specific evidence ceiling unless new "
            "route-conditioned support/regulation artifacts are created."
        ),
    }
    output = {
        "experiment": "N14",
        "iteration": "6-B",
        "purpose": "route_conditioned_support_regulation_consequence_probe",
        "schema": "n14_route_conditioned_support_regulation_probe_v1",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed" if all(checks.values()) else "failed",
        "acceptance_state": acceptance_state,
        "target_ap_ceiling": "AP4",
        "iteration_result": {
            "acceptance_state": acceptance_state,
            "observed_route_conditioned_support_supported": support_supported,
            "observed_route_conditioned_regulation_supported": regulation_supported,
            "supported_closeout_scope": supported_closeout_scope,
            "final_ap4_supported": False,
            "phase8_opened": False,
            "native_support_opened": False,
        },
        "route_conditioned_probe_summary": route_conditioned_probe_summary,
        "generic_support_source_summary": support_lane_summaries,
        "generic_regulation_source_summary": regulation_summary,
        "route_conditioned_support_regulation_records": records,
        "control_records": controls,
        "interpretation_record": interpretation_record,
        "claim_flags_forced_false": CLAIM_FLAGS_FORCED_FALSE,
        "checks": checks,
        "source_artifacts": {
            rel(OBSERVED_ROUTE_OUTPUT): source_artifact(
                OBSERVED_ROUTE_OUTPUT, observed_route_probe
            ),
            rel(N13_SUPPORT_OUTPUT): source_artifact(N13_SUPPORT_OUTPUT, n13_support),
            rel(N09_CLOSEOUT_OUTPUT): source_artifact(
                N09_CLOSEOUT_OUTPUT, n09_closeout
            ),
        },
        "source_reports": {
            rel(OBSERVED_ROUTE_REPORT): source_report(OBSERVED_ROUTE_REPORT),
            rel(N13_SUPPORT_REPORT): source_report(N13_SUPPORT_REPORT),
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
        "# N14 Route-Conditioned Support And Regulation Consequence Probe",
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
        "## Probe Summary",
        "",
        "```json",
        json.dumps(
            output["route_conditioned_probe_summary"], indent=2, sort_keys=True
        ),
        "```",
        "",
        "## Route-Conditioned Axis Records",
        "",
        "| Route | Support status | Regulation status | Support blocker | Regulation blocker |",
        "| --- | --- | --- | --- | --- |",
    ]
    for record in output["route_conditioned_support_regulation_records"]:
        support = record["observed_support_consequence"]
        regulation = record["observed_regulation_consequence"]
        lines.append(
            "| "
            f"`{record['route_candidate_id']}` | "
            f"`{support['status']}` | "
            f"`{regulation['status']}` | "
            f"`{support['blocker']}` | "
            f"`{regulation['blocker']}` |"
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
            "Iteration 6-B does not obtain observed route-conditioned support",
            "or regulation consequence evidence. It blocks generic N09/N13",
            "source reuse as route-specific evidence and preserves the",
            "memory-dominant N14 closeout ceiling.",
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
            "generic support source compatibility != route-conditioned support consequence",
            "generic regulation source compatibility != route-conditioned regulation consequence",
            "route-conditioned support/regulation probe != intention",
            "memory-dominant AP4 candidate != agency",
            "artifact-level route-conditioned probe != native support",
            "N14 Iteration 6-B != final AP4 closeout before Iteration 7",
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
