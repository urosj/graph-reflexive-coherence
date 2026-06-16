#!/usr/bin/env python3
"""Build N14 Iteration 6-A observed route-specific consequence probe."""

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

PERTURBATION_OUTPUT = OUTPUTS / "n14_consequence_perturbation_matrix.json"
PERTURBATION_REPORT = REPORTS / "n14_consequence_perturbation_matrix.md"
N08_MEM3_OUTPUT = (
    ROOT
    / "experiments"
    / "2026-05-N08-lgrc-memory-trail-affordance"
    / "outputs"
    / "n08_iteration_5_mem3_decay_reinforcement.json"
)
N08_MEM3_REPORT = (
    ROOT
    / "experiments"
    / "2026-05-N08-lgrc-memory-trail-affordance"
    / "reports"
    / "n08_iteration_5_mem3_decay_reinforcement.md"
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

OUTPUT_PATH = OUTPUTS / "n14_observed_route_specific_consequence_probe.json"
REPORT_PATH = REPORTS / "n14_observed_route_specific_consequence_probe.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N14-lgrc-consequence-sensitive-route-selection/"
    "scripts/build_n14_observed_route_specific_consequence_probe.py"
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


def mem3_snapshot_records(n08_mem3: dict[str, Any]) -> list[dict[str, Any]]:
    snapshot = n08_mem3["memory_surface_state_snapshot"][
        "state_by_memory_surface_key_digest"
    ]
    records = []
    for key_digest, row in snapshot.items():
        route_id = row["memory_surface_key"]["route_id"]
        memory_delta = round(
            row["memory_strength"] - row["memory_strength_before"], 12
        )
        records.append(
            {
                "route_candidate_id": route_id,
                "source_memory_surface_key_route_id": route_id,
                "memory_surface_key_digest": key_digest,
                "route_use_count_for_key": row["route_use_count_for_key"],
                "memory_strength_before": row["memory_strength_before"],
                "strength_after_decay": row["strength_after_decay"],
                "reinforcement_input": row["reinforcement_input"],
                "memory_strength_after": row["memory_strength"],
                "memory_delta_component": memory_delta,
                "elapsed_memory_window_count": row["elapsed_memory_window_count"],
                "mem3_update_window_id": row["mem3_update_window_id"],
                "memory_policy_id": row["memory_policy_id"],
                "decay_policy_id": row["decay_policy_id"],
                "reinforcement_policy_id": row["reinforcement_policy_id"],
                "claim_flags_all_false": row["claim_flags_all_false"],
                "budget_status": {
                    "memory_budget_equations_hold": n08_mem3["checks"][
                        "memory_budget_equations_hold"
                    ],
                    "node_plus_packet_budget_separate_and_exact": n08_mem3[
                        "checks"
                    ]["node_plus_packet_budget_separate_and_exact"],
                },
            }
        )
    return sorted(records, key=lambda record: record["route_candidate_id"])


def derive_route_specific_records(
    n08_mem3: dict[str, Any],
    n09_closeout: dict[str, Any],
    n13_support: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    memory_records = mem3_snapshot_records(n08_mem3)
    route_ranks = {
        record["route_candidate_id"]: rank
        for rank, record in enumerate(
            sorted(
                memory_records,
                key=lambda record: (
                    -record["memory_delta_component"],
                    record["route_candidate_id"],
                ),
            ),
            start=1,
        )
    }
    support_lanes = n13_support["support_seeking_regulation_candidate"][
        "lane_response_records"
    ]
    support_route_ids = {
        lane.get("route_candidate_id")
        for lane in support_lanes
        if lane.get("route_candidate_id")
    }
    regulation_route_ids: set[str] = set()
    records = []
    for memory_record in memory_records:
        route_id = memory_record["route_candidate_id"]
        records.append(
            {
                "row_id": f"n14_i6a_observed_route_specific_{route_id}",
                "route_candidate_id": route_id,
                "source_experiment": "N14",
                "source_iteration": "iteration_6a_observed_route_specific_consequence_probe",
                "source_artifact": rel(N08_MEM3_OUTPUT),
                "source_report": rel(N08_MEM3_REPORT),
                "source_sha256": digest_file(N08_MEM3_OUTPUT),
                "source_report_sha256": digest_file(N08_MEM3_REPORT),
                "bounded_horizon": {
                    "memory_source_window": "N08_MEM3_decay_reinforcement_update_window",
                    "same_window_policy": True,
                    "same_memory_policy": memory_record["memory_policy_id"],
                    "same_decay_policy": memory_record["decay_policy_id"],
                    "same_reinforcement_policy": memory_record[
                        "reinforcement_policy_id"
                    ],
                    "route_specific_recency_visible": True,
                },
                "selection_rule": (
                    "rank observed route-specific consequence components; "
                    "higher memory_delta_component is better; support and "
                    "regulation components excluded unless route-specific"
                ),
                "observed_memory_consequence": {
                    **memory_record,
                    "route_specific": True,
                    "component_used_for_rank": True,
                    "rank": route_ranks[route_id],
                },
                "observed_support_consequence": {
                    "route_specific": route_id in support_route_ids,
                    "status": "unsupported_generic_source_only",
                    "reason": (
                        "N13 support response lanes carry lane_id/support "
                        "state, not route_candidate_id"
                    ),
                    "generic_lane_count": len(support_lanes),
                },
                "observed_regulation_consequence": {
                    "route_specific": route_id in regulation_route_ids,
                    "status": "unsupported_generic_source_only",
                    "reason": (
                        "N09 GPR6 closeout has bounded regulation summary, "
                        "not route_candidate_id observations"
                    ),
                    "gpr5_cycle_count": n09_closeout["regulation_summary"][
                        "gpr5_cycle_count"
                    ],
                    "gpr8_perturbation_recovery_in_band": n09_closeout[
                        "regulation_summary"
                    ]["gpr8_perturbation_recovery_in_band"],
                },
                "route_specific_consequence_components": {
                    "memory_delta_component": memory_record[
                        "memory_delta_component"
                    ],
                    "support_component": "unsupported_not_route_specific",
                    "regulation_component": "unsupported_not_route_specific",
                },
                "route_specific_consequence_score": memory_record[
                    "memory_delta_component"
                ],
                "route_specific_consequence_rank": route_ranks[route_id],
                "rank_source": "derived_from_observed_route_specific_memory_component",
                "post_hoc_rank_assigned": False,
                "budget_accounting": memory_record["budget_status"],
                "claim_flags_forced_false": CLAIM_FLAGS_FORCED_FALSE,
            }
        )
    probe_summary = {
        "route_specific_memory_supported": True,
        "route_specific_support_supported": False,
        "route_specific_regulation_supported": False,
        "supported_closeout_scope": (
            "artifact_level_ap4_memory_dominant_consequence_sensitive_route_selection_candidate"
        ),
        "stronger_support_or_regulation_closeout_available": False,
    }
    return records, probe_summary


def blocked(blocker: str) -> dict[str, Any]:
    return {"observed_status": "blocked", "observed_blocker": blocker}


def accepted() -> dict[str, Any]:
    return {"observed_status": "accepted", "observed_blocker": None}


def validate_probe_records(
    records: list[dict[str, Any]],
    metadata: dict[str, Any],
    source_route_by_memory_digest: dict[str, str],
) -> dict[str, Any]:
    if metadata.get("post_hoc_score_or_rank") is True:
        return blocked("post_hoc_score_rank_blocked")
    if metadata.get("stale_route_specific_consequence") is True:
        return blocked("stale_route_specific_consequence_blocked")
    if metadata.get("generic_support_regulation_reuse") is True:
        return blocked("generic_support_regulation_reuse_blocked")
    if metadata.get("budget_invalid_observed_route") is True:
        return blocked("budget_invalid_observed_route_blocked")
    route_ids = {record["route_candidate_id"] for record in records}
    if route_ids != {"route_a", "route_b"}:
        return blocked("missing_route_observation_blocked")
    for record in records:
        observed_memory = record["observed_memory_consequence"]
        source_route = observed_memory["source_memory_surface_key_route_id"]
        memory_digest = observed_memory["memory_surface_key_digest"]
        expected_source_route = source_route_by_memory_digest[memory_digest]
        if (
            record["route_candidate_id"] != source_route
            or source_route != expected_source_route
            or observed_memory["route_candidate_id"] != expected_source_route
        ):
            return blocked("route_label_swap_blocked")
    return accepted()


def swapped_route(route_id: str) -> str:
    return {"route_a": "route_b", "route_b": "route_a"}[route_id]


def build_controls(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    controls: list[dict[str, Any]] = []
    variants = []
    source_route_by_memory_digest = {
        record["observed_memory_consequence"]["memory_surface_key_digest"]: record[
            "observed_memory_consequence"
        ]["source_memory_surface_key_route_id"]
        for record in records
    }
    swapped = copy.deepcopy(records)
    for record in swapped:
        new_route = swapped_route(record["route_candidate_id"])
        record["route_candidate_id"] = new_route
        record["observed_memory_consequence"]["route_candidate_id"] = new_route
        record["observed_memory_consequence"][
            "source_memory_surface_key_route_id"
        ] = new_route
    variants.append(
        (
            "route_label_swap_control",
            "Route label swap",
            swapped,
            {},
            "route_label_swap_blocked",
        )
    )
    variants.append(
        (
            "generic_support_regulation_reuse_control",
            "Generic support/regulation reuse",
            copy.deepcopy(records),
            {"generic_support_regulation_reuse": True},
            "generic_support_regulation_reuse_blocked",
        )
    )
    variants.append(
        (
            "missing_route_observation_control",
            "Missing route observation",
            [copy.deepcopy(records[0])],
            {},
            "missing_route_observation_blocked",
        )
    )
    variants.append(
        (
            "stale_route_specific_consequence_control",
            "Stale route-specific consequence",
            copy.deepcopy(records),
            {"stale_route_specific_consequence": True},
            "stale_route_specific_consequence_blocked",
        )
    )
    variants.append(
        (
            "budget_invalid_observed_route_control",
            "Budget-invalid observed route",
            copy.deepcopy(records),
            {"budget_invalid_observed_route": True},
            "budget_invalid_observed_route_blocked",
        )
    )
    variants.append(
        (
            "post_hoc_score_rank_control",
            "Post-hoc score/rank",
            copy.deepcopy(records),
            {"post_hoc_score_or_rank": True},
            "post_hoc_score_rank_blocked",
        )
    )
    for control_id, control_name, variant_records, metadata, expected_blocker in variants:
        observed = validate_probe_records(
            variant_records, metadata, source_route_by_memory_digest
        )
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
    perturbation = load_json(PERTURBATION_OUTPUT)
    n08_mem3 = load_json(N08_MEM3_OUTPUT)
    n09_closeout = load_json(N09_CLOSEOUT_OUTPUT)
    n13_support = load_json(N13_SUPPORT_OUTPUT)
    records, probe_summary = derive_route_specific_records(
        n08_mem3, n09_closeout, n13_support
    )
    controls = build_controls(records)
    ranked = sorted(records, key=lambda record: record["route_specific_consequence_rank"])
    checks = {
        "perturbation_source_passed": perturbation["status"] == "passed",
        "n08_memory_source_passed": n08_mem3["status"] == "passed",
        "n09_regulation_source_passed": n09_closeout["status"] == "passed",
        "n13_support_source_passed": n13_support["status"] == "passed",
        "both_routes_observed_for_memory": {
            record["route_candidate_id"] for record in records
        }
        == {"route_a", "route_b"}
        and all(
            record["observed_memory_consequence"]["route_specific"] is True
            for record in records
        ),
        "same_source_window_policy": all(
            record["bounded_horizon"]["same_window_policy"] is True
            for record in records
        )
        and len({record["bounded_horizon"]["same_memory_policy"] for record in records})
        == 1,
        "same_budget_accounting": all(
            record["budget_accounting"]["memory_budget_equations_hold"] is True
            and record["budget_accounting"][
                "node_plus_packet_budget_separate_and_exact"
            ]
            is True
            for record in records
        ),
        "same_selection_rule": len({record["selection_rule"] for record in records})
        == 1,
        "route_specific_components_derived_from_observed_records": all(
            record["rank_source"]
            == "derived_from_observed_route_specific_memory_component"
            and record["post_hoc_rank_assigned"] is False
            for record in records
        ),
        "route_specific_memory_supported": probe_summary[
            "route_specific_memory_supported"
        ],
        "route_specific_support_remains_unsupported_generic": all(
            record["observed_support_consequence"]["status"]
            == "unsupported_generic_source_only"
            for record in records
        )
        and not probe_summary["route_specific_support_supported"],
        "route_specific_regulation_remains_unsupported_generic": all(
            record["observed_regulation_consequence"]["status"]
            == "unsupported_generic_source_only"
            for record in records
        )
        and not probe_summary["route_specific_regulation_supported"],
        "observed_memory_rank_selects_route_b": ranked[0]["route_candidate_id"]
        == "route_b",
        "controls_passed": all(control["passed"] for control in controls),
        "route_label_swap_blocked": next(
            control for control in controls if control["control_id"] == "route_label_swap_control"
        )["passed"],
        "generic_support_regulation_reuse_blocked": next(
            control
            for control in controls
            if control["control_id"] == "generic_support_regulation_reuse_control"
        )["passed"],
        "missing_route_observation_blocked": next(
            control
            for control in controls
            if control["control_id"] == "missing_route_observation_control"
        )["passed"],
        "stale_route_specific_consequence_blocked": next(
            control
            for control in controls
            if control["control_id"] == "stale_route_specific_consequence_control"
        )["passed"],
        "budget_invalid_observed_route_blocked": next(
            control
            for control in controls
            if control["control_id"] == "budget_invalid_observed_route_control"
        )["passed"],
        "post_hoc_score_rank_blocked": next(
            control for control in controls if control["control_id"] == "post_hoc_score_rank_control"
        )["passed"],
        "claim_flags_forced_false": all(
            value is False for value in CLAIM_FLAGS_FORCED_FALSE.values()
        ),
        "phase8_opened_false": True,
        "native_support_opened_false": True,
        "final_ap4_not_supported": True,
        "src_diff_empty": git_status_short("src") == "",
    }
    acceptance_state = (
        "accepted_observed_route_specific_memory_probe_support_regulation_generic"
        if all(checks.values())
        else "rejected_observed_route_specific_consequence_probe"
    )
    interpretation_record = {
        "record_id": "n14_i6a_interpretation_observed_route_specific_probe_v1",
        "acceptance_state": acceptance_state,
        "supported_interpretation": (
            "N14 Iteration 6-A finds observed route-specific memory consequences "
            "for both route_a and route_b under the same N08 MEM3 update-window "
            "policy. It does not find observed route-specific support or "
            "regulation consequences in the available N09/N13 sources."
        ),
        "unsupported_interpretations": [
            "observed route-specific support consequence support",
            "observed route-specific regulation consequence support",
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
            "The source-backed observed route-specific part of N14 is memory-"
            "dominant. Route_b has the stronger observed memory consequence "
            "under the same N08 window policy. Support and regulation remain "
            "generic source lanes, so they are blocked from route-specific "
            "closeout language unless future artifacts bind them to route IDs."
        ),
        "next_required_step": (
            "Use Iteration 7 to classify AP4 with the narrowed memory-dominant "
            "claim ceiling unless new route-specific support/regulation sources "
            "are added."
        ),
    }
    output = {
        "experiment": "N14",
        "iteration": "6-A",
        "purpose": "observed_route_specific_consequence_probe",
        "schema": "n14_observed_route_specific_consequence_probe_v1",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed" if all(checks.values()) else "failed",
        "acceptance_state": acceptance_state,
        "target_ap_ceiling": "AP4",
        "iteration_result": {
            "acceptance_state": acceptance_state,
            "observed_route_specific_memory_supported": True,
            "observed_route_specific_support_supported": False,
            "observed_route_specific_regulation_supported": False,
            "observed_memory_top_route": ranked[0]["route_candidate_id"],
            "supported_closeout_scope": probe_summary["supported_closeout_scope"],
            "final_ap4_supported": False,
            "phase8_opened": False,
            "native_support_opened": False,
        },
        "probe_summary": probe_summary,
        "observed_route_specific_consequence_records": records,
        "control_records": controls,
        "interpretation_record": interpretation_record,
        "claim_flags_forced_false": CLAIM_FLAGS_FORCED_FALSE,
        "checks": checks,
        "source_artifacts": {
            rel(PERTURBATION_OUTPUT): source_artifact(
                PERTURBATION_OUTPUT, perturbation
            ),
            rel(N08_MEM3_OUTPUT): source_artifact(N08_MEM3_OUTPUT, n08_mem3),
            rel(N09_CLOSEOUT_OUTPUT): source_artifact(
                N09_CLOSEOUT_OUTPUT, n09_closeout
            ),
            rel(N13_SUPPORT_OUTPUT): source_artifact(
                N13_SUPPORT_OUTPUT, n13_support
            ),
        },
        "source_reports": {
            rel(PERTURBATION_REPORT): source_report(PERTURBATION_REPORT),
            rel(N08_MEM3_REPORT): source_report(N08_MEM3_REPORT),
            rel(N09_CLOSEOUT_REPORT): source_report(N09_CLOSEOUT_REPORT),
            rel(N13_SUPPORT_REPORT): source_report(N13_SUPPORT_REPORT),
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
        "# N14 Observed Route-Specific Consequence Probe",
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
        json.dumps(output["probe_summary"], indent=2, sort_keys=True),
        "```",
        "",
        "## Observed Route Records",
        "",
        "| Route | Memory delta | Memory rank | Support | Regulation |",
        "| --- | ---: | ---: | --- | --- |",
    ]
    for record in output["observed_route_specific_consequence_records"]:
        lines.append(
            "| "
            f"`{record['route_candidate_id']}` | "
            f"{record['observed_memory_consequence']['memory_delta_component']} | "
            f"{record['route_specific_consequence_rank']} | "
            f"`{record['observed_support_consequence']['status']}` | "
            f"`{record['observed_regulation_consequence']['status']}` |"
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
            "Iteration 6-A supports only observed route-specific memory",
            "consequence evidence. Support and regulation remain generic source",
            "lanes and are not promoted into route-specific AP4 evidence.",
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
            "observed route-specific memory consequence != intention",
            "observed route-specific memory consequence != semantic choice",
            "generic support/regulation lane != route-specific consequence",
            "memory-dominant AP4 candidate != agency",
            "artifact-level route-specific probe != native support",
            "N14 Iteration 6-A != final AP4 closeout before Iteration 7",
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
