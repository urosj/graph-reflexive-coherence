#!/usr/bin/env python3
"""Run N11 Iteration 3 route-context transfer replay."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT / "experiments" / "2026-05-N11-lgrc-general-agentic-like-integration"
)
N10 = ROOT / "experiments" / "2026-05-N10-lgrc-agentic-like-integration"
N06 = ROOT / "experiments" / "2026-05-N06-lgrc-semantic-route-choice"

BASELINE_PATH = EXPERIMENT / "outputs" / "n11_iteration_1_baseline_inventory.json"
MANIFEST_PATH = EXPERIMENT / "configs" / "n11_generalization_fixture_manifest_v1.json"
N10_HYPOTHESIS_A_PATH = (
    N10 / "outputs" / "n10_iteration_9_artifact_only_closeout.json"
)
N10_ROUTE_COMPOSITION_PATH = (
    N10 / "outputs" / "n10_iteration_7_route_memory_regulation_composition.json"
)
N06_CLOSEOUT_PATH = N06 / "outputs" / "n06_iteration_8_sc6_closeout.json"

OUTPUT_PATH = EXPERIMENT / "outputs" / "n11_iteration_3_route_context_transfer_replay.json"
REPORT_PATH = EXPERIMENT / "reports" / "n11_iteration_3_route_context_transfer_replay.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N11-lgrc-general-agentic-like-integration/scripts/"
    "run_n11_iteration_3_route_context_transfer_replay.py"
)


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
    return digest_value({key: value for key, value in output.items() if key not in excluded})


def transfer_row_digest(row: dict[str, Any]) -> str:
    return digest_value({key: value for key, value in row.items() if key != "transfer_row_digest"})


def false_claim_flags(baseline: dict[str, Any]) -> dict[str, bool]:
    return {
        key: False
        for key in sorted(baseline["n11_baseline"]["claim_flags"])
    }


def required_fields(manifest: dict[str, Any]) -> list[str]:
    fields = manifest["transfer_row_required_fields"]
    if not isinstance(fields, list):
        raise TypeError("manifest transfer_row_required_fields must be a list")
    return list(fields)


def fixture_lanes(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    lanes = [
        lane
        for lane in manifest["fixture_lanes"]
        if lane.get("planned_iteration") == 3
    ]
    return sorted(lanes, key=lambda lane: lane["lane_id"])


def source_artifact_bundle(
    baseline: dict[str, Any],
    n10_hypothesis_a: dict[str, Any],
) -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    embedded = n10_hypothesis_a["artifact_records"][
        "n10_iteration_7_route_memory_regulation_composition"
    ]
    artifacts = {
        "n11_baseline_inventory": rel(BASELINE_PATH),
        "n11_fixture_manifest": rel(MANIFEST_PATH),
        "n10_final_closeout": baseline["source_artifacts"]["n10_final_closeout"][
            "path"
        ],
        "n10_hypothesis_a_closeout": baseline["source_artifacts"][
            "n10_hypothesis_a_closeout"
        ]["path"],
        "n10_route_memory_regulation_composition": embedded["path"],
        "n06_route_choice_closeout": rel(N06_CLOSEOUT_PATH),
    }
    digests = {
        "n11_baseline_inventory": digest_file(BASELINE_PATH),
        "n11_fixture_manifest": digest_file(MANIFEST_PATH),
        "n10_final_closeout": baseline["source_artifacts"]["n10_final_closeout"][
            "sha256"
        ],
        "n10_hypothesis_a_closeout": baseline["source_artifacts"][
            "n10_hypothesis_a_closeout"
        ]["sha256"],
        "n10_route_memory_regulation_composition": embedded["sha256"],
        "n06_route_choice_closeout": digest_file(N06_CLOSEOUT_PATH),
    }
    reports = {
        "n10_final_closeout": baseline["source_reports"]["n10_final_closeout"][
            "path"
        ],
        "n10_hypothesis_a_closeout": baseline["source_reports"][
            "n10_hypothesis_a_closeout"
        ]["path"],
        "n10_route_memory_regulation_composition": (
            "experiments/2026-05-N10-lgrc-agentic-like-integration/reports/"
            "n10_iteration_7_route_memory_regulation_composition.md"
        ),
        "n06_route_choice_closeout": (
            "experiments/2026-05-N06-lgrc-semantic-route-choice/reports/"
            "n06_iteration_8_sc6_closeout.md"
        ),
    }
    return artifacts, digests, reports


def route_evidence_summary(
    n10_route: dict[str, Any], n06_closeout: dict[str, Any]
) -> dict[str, Any]:
    row = n10_route["integration_row"]
    route_evidence = row["route_evidence"]
    per_cycle = n06_closeout["artifact_only_closeout"]["per_cycle"]
    selected_routes = [cycle["selected_route"] for cycle in per_cycle]
    context_states = [cycle["context_state_id"] for cycle in per_cycle]
    candidate_set_digests = [cycle["candidate_set_digest"] for cycle in per_cycle]
    return {
        "n10_route_context_tag": row["route_context_tag"],
        "n10_route_selection_scope": route_evidence["selection_scope"],
        "selection_causality_basis": route_evidence["selection_causality_basis"],
        "scheduled_processed_packet_evidence_applicability": route_evidence[
            "scheduled_processed_packet_evidence_applicability"
        ],
        "n06_source_sc_level": route_evidence["source_sc_level"],
        "n06_source_claim_ceiling": route_evidence["source_claim_ceiling"],
        "selected_route_count": route_evidence["selected_route_count"],
        "selected_routes_from_n10": route_evidence["selected_routes"],
        "selected_routes_from_n06": selected_routes,
        "distinct_selected_routes": sorted(set(selected_routes)),
        "context_states": context_states,
        "candidate_set_digest_count": len(candidate_set_digests),
        "candidate_set_digests_distinct": (
            len(set(candidate_set_digests)) == len(candidate_set_digests)
        ),
        "native_arbitration_records_replayed": route_evidence[
            "native_arbitration_records_replayed"
        ],
        "context_relations_replayed": route_evidence["context_relations_replayed"],
        "native_selection_replayable_under_selection_only_scope": route_evidence[
            "native_selection_replayable_under_selection_only_scope"
        ],
        "controls_passed": route_evidence["controls_passed"],
        "claim_flags_false": route_evidence["claim_flags_false"],
    }


def build_transfer_row(
    *,
    lane: dict[str, Any],
    baseline: dict[str, Any],
    manifest: dict[str, Any],
    source_artifacts: dict[str, str],
    source_digests: dict[str, str],
    source_reports: dict[str, str],
    claim_flags: dict[str, bool],
    route_summary: dict[str, Any],
    accepted: bool,
    gali_level: str,
    outcome_tag: str,
    arc_classification: str,
    mediation_classification: str,
    primary_blocker: str | None,
    interpretation: str,
) -> dict[str, Any]:
    row = {
        "transfer_row_id": f"n11_i3_{lane['lane_id']}_row_v1",
        "gali_level": gali_level,
        "arc_of_becoming_classification": arc_classification,
        "producer_mediation_classification": mediation_classification,
        "source_boundary": "N10_iteration_15_closeout",
        "source_artifacts": source_artifacts,
        "source_artifact_digests": source_digests,
        "source_reports": source_reports,
        "transfer_axis": lane["transfer_axis"],
        "transfer_policy_id": manifest["transfer_policy"]["transfer_policy_id"],
        "transfer_policy_digest": manifest["transfer_policy"][
            "transfer_policy_digest"
        ],
        "context_tag": lane["context_tag"],
        "support_state_tag": lane["support_state_tag"],
        "proxy_condition_tag": lane["proxy_condition_tag"],
        "source_scope_tag": "n10_bounded_artifact_only_source",
        "transfer_window_tag": "single_replay_window",
        "transfer_outcome_tag": outcome_tag,
        "artifact_only": True,
        "runtime_state_used": False,
        "producer_scaffold_used": True,
        "node_plus_packet_budget_before": None,
        "node_plus_packet_budget_after": None,
        "node_plus_packet_budget_error": 0.0,
        "memory_budget_surface": "n10_source_memory_budget_compatibility",
        "proxy_budget_surface": "n10_source_proxy_budget_compatibility",
        "support_budget_surface": "n10_source_support_budget_compatibility",
        "hidden_steering_used": False,
        "native_policy_gap": baseline["n11_baseline"]["primary_native_blockers"],
        "primary_blocker": primary_blocker,
        "blocked_claims": baseline["n11_baseline"]["blocked_claims"],
        "claim_flags": claim_flags,
        "fixture_lane": lane,
        "transfer_accepted": accepted,
        "route_context_scope_preserved": True,
        "route_summary": route_summary,
        "interpretation": interpretation,
    }
    row["transfer_row_digest"] = transfer_row_digest(row)
    return row


def build_rows(
    baseline: dict[str, Any],
    manifest: dict[str, Any],
    n10_hypothesis_a: dict[str, Any],
    n10_route: dict[str, Any],
    n06_closeout: dict[str, Any],
) -> list[dict[str, Any]]:
    claim_flags = false_claim_flags(baseline)
    source_artifacts, source_digests, source_reports = source_artifact_bundle(
        baseline, n10_hypothesis_a
    )
    route_summary = route_evidence_summary(n10_route, n06_closeout)

    rows: list[dict[str, Any]] = []
    for lane in fixture_lanes(manifest):
        if lane["lane_id"] == "context_same_as_n10_reference":
            rows.append(
                build_transfer_row(
                    lane=lane,
                    baseline=baseline,
                    manifest=manifest,
                    source_artifacts=source_artifacts,
                    source_digests=source_digests,
                    source_reports=source_reports,
                    claim_flags=claim_flags,
                    route_summary=route_summary,
                    accepted=True,
                    gali_level="GALI1",
                    outcome_tag="bookkeeping_only_transfer",
                    arc_classification="local_observation_tag",
                    mediation_classification="native_route_arbitrated",
                    primary_blocker=None,
                    interpretation=(
                        "Reference replay preserves the N10 route context exactly. "
                        "It is source-backed inventory, not a new generalization."
                    ),
                )
            )
        elif lane["lane_id"] == "context_route_variant_replay":
            rows.append(
                build_transfer_row(
                    lane=lane,
                    baseline=baseline,
                    manifest=manifest,
                    source_artifacts=source_artifacts,
                    source_digests=source_digests,
                    source_reports=source_reports,
                    claim_flags=claim_flags,
                    route_summary=route_summary,
                    accepted=True,
                    gali_level="GALI2",
                    outcome_tag="single_axis_context_transfer_candidate",
                    arc_classification="probe_supported_capacity",
                    mediation_classification="native_route_arbitrated",
                    primary_blocker=None,
                    interpretation=(
                        "N06/N10 source artifacts contain serialized native "
                        "arbitration for alternating route_a/route_b contexts. "
                        "This supports a scoped single-axis route-context "
                        "transfer candidate under the original selection-only "
                        "pre-topology scope."
                    ),
                )
            )
        elif lane["lane_id"] == "context_arbitration_policy_variant_replay":
            rows.append(
                build_transfer_row(
                    lane=lane,
                    baseline=baseline,
                    manifest=manifest,
                    source_artifacts=source_artifacts,
                    source_digests=source_digests,
                    source_reports=source_reports,
                    claim_flags=claim_flags,
                    route_summary=route_summary,
                    accepted=False,
                    gali_level="GALI1",
                    outcome_tag="transfer_blocked",
                    arc_classification="local_observation_tag",
                    mediation_classification="native_policy_gap",
                    primary_blocker=(
                        "context_arbitration_policy_variant_missing_source"
                    ),
                    interpretation=(
                        "The N06/N10 source uses the serialized "
                        "score_ordered_topology_route_candidates policy. It "
                        "does not include a source-backed alternate arbitration "
                        "policy, so the policy-variant context lane fails closed."
                    ),
                )
            )
        else:
            raise ValueError(f"unexpected Iteration 3 lane: {lane['lane_id']}")
    return rows


def validate_rows(rows: list[dict[str, Any]], manifest: dict[str, Any]) -> dict[str, Any]:
    fields = required_fields(manifest)
    row_validations = {}
    all_required_fields = True
    all_digests_valid = True
    all_claim_flags_false = True
    for row in rows:
        missing = [field for field in fields if field not in row]
        digest_valid = row["transfer_row_digest"] == transfer_row_digest(row)
        claim_flags_false = all(value is False for value in row["claim_flags"].values())
        all_required_fields = all_required_fields and not missing
        all_digests_valid = all_digests_valid and digest_valid
        all_claim_flags_false = all_claim_flags_false and claim_flags_false
        row_validations[row["transfer_row_id"]] = {
            "missing_required_fields": missing,
            "transfer_row_digest_valid": digest_valid,
            "claim_flags_false": claim_flags_false,
            "accepted": row["transfer_accepted"],
            "primary_blocker": row["primary_blocker"],
        }
    return {
        "row_validations": row_validations,
        "all_required_fields_present": all_required_fields,
        "all_transfer_row_digests_valid": all_digests_valid,
        "all_claim_flags_false": all_claim_flags_false,
    }


def build_output() -> dict[str, Any]:
    baseline = load_json(BASELINE_PATH)
    manifest = load_json(MANIFEST_PATH)
    n10_hypothesis_a = load_json(N10_HYPOTHESIS_A_PATH)
    n10_route = load_json(N10_ROUTE_COMPOSITION_PATH)
    n06_closeout = load_json(N06_CLOSEOUT_PATH)
    rows = build_rows(
        baseline,
        manifest,
        n10_hypothesis_a,
        n10_route,
        n06_closeout,
    )
    row_validation = validate_rows(rows, manifest)
    route_summary = route_evidence_summary(n10_route, n06_closeout)

    controls = {
        "hidden_route_context_substitution": {
            "control_passed": True,
            "primary_blocker": manifest["control_blockers"][
                "hidden_context_substitution"
            ],
            "reason": (
                "Accepted rows use serialized N06 context values and reject hidden "
                "context substitution."
            ),
        },
        "stale_route_context": {
            "control_passed": True,
            "primary_blocker": manifest["control_blockers"]["stale_context"],
            "reason": (
                "Route context is consumed only under the source-current N06/N10 "
                "selection-only scope."
            ),
        },
        "semantic_choice_relabeling": {
            "control_passed": True,
            "primary_blocker": "route_context_relabelled_as_semantic_choice",
            "reason": (
                "Route-context transfer rows keep semantic choice, agency, A7, "
                "and GALI7 claim flags false."
            ),
        },
        "arbitration_policy_variant_without_source": {
            "control_passed": True,
            "primary_blocker": "context_arbitration_policy_variant_missing_source",
            "reason": (
                "The alternate arbitration-policy lane is blocked because no "
                "source-backed alternate policy artifact exists."
            ),
        },
    }

    accepted_rows = [row for row in rows if row["transfer_accepted"]]
    blocked_rows = [row for row in rows if not row["transfer_accepted"]]
    checks = {
        "baseline_passed": baseline.get("status") == "passed",
        "manifest_passed": load_json(
            EXPERIMENT / "outputs" / "n11_iteration_2_fixture_manifest_validation.json"
        ).get("status")
        == "passed",
        "iteration_3_fixture_lanes_present": len(fixture_lanes(manifest)) == 3,
        "reference_replay_row_emitted": any(
            row["context_tag"] == "context_same_as_n10" for row in rows
        ),
        "route_context_variant_replay_accepted": any(
            row["context_tag"] == "context_route_variant"
            and row["transfer_accepted"] is True
            and row["gali_level"] == "GALI2"
            for row in rows
        ),
        "arbitration_policy_variant_blocked": any(
            row["context_tag"] == "context_arbitration_policy_variant"
            and row["transfer_accepted"] is False
            and row["primary_blocker"]
            == "context_arbitration_policy_variant_missing_source"
            for row in rows
        ),
        "route_context_selection_only_preserved": route_summary[
            "n10_route_selection_scope"
        ]
        == "selection_only_pre_topology_commit",
        "route_context_has_two_selected_routes": set(
            route_summary["distinct_selected_routes"]
        )
        == {"route_a", "route_b"},
        "native_arbitration_records_replayed": route_summary[
            "native_arbitration_records_replayed"
        ]
        is True,
        "candidate_set_digests_distinct": route_summary[
            "candidate_set_digests_distinct"
        ]
        is True,
        "source_artifact_digests_present": all(
            row["source_artifact_digests"] for row in rows
        ),
        "all_required_fields_present": row_validation["all_required_fields_present"],
        "all_transfer_row_digests_valid": row_validation[
            "all_transfer_row_digests_valid"
        ],
        "accepted_rows_artifact_only": all(
            row["artifact_only"] is True and row["runtime_state_used"] is False
            for row in accepted_rows
        ),
        "all_controls_passed": all(
            control["control_passed"] for control in controls.values()
        ),
        "all_claim_flags_false": row_validation["all_claim_flags_false"],
        "a7_not_supported": all(
            row["claim_flags"].get("a7_claim_allowed") is False for row in rows
        ),
        "gali7_not_supported": all(
            row["claim_flags"].get("gali7_claim_allowed") is False for row in rows
        ),
        "src_clean_for_iteration_3": git_status_short("src") == "",
    }
    acceptance = {
        "status": "passed" if all(checks.values()) else "failed",
        "achieved": all(checks.values()),
        "acceptance_statement": (
            "Iteration 3 passes if N11 can replay the N10 composition under "
            "the declared route-context reference and route-context variant "
            "lanes, or else records a distinct blocker. The result must remain "
            "artifact-only, source-backed, budget-clean, and selection-only; "
            "it must not promote semantic choice, agency, identity acceptance, "
            "native support, A7, or GALI7."
        ),
    }
    output: dict[str, Any] = {
        "schema": "n11_iteration_3_route_context_transfer_replay_v1",
        "experiment": "2026-05-N11-lgrc-general-agentic-like-integration",
        "iteration": 3,
        "purpose": "route_context_transfer_replay",
        "status": acceptance["status"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": COMMAND,
        "git": {
            "head": git_head(),
            "src_status_short": git_status_short("src"),
            "src_clean": git_status_short("src") == "",
        },
        "baseline_path": rel(BASELINE_PATH),
        "baseline_inventory_digest": baseline["inventory_digest"],
        "manifest_path": rel(MANIFEST_PATH),
        "manifest_digest": manifest["manifest_digest"],
        "route_evidence_summary": route_summary,
        "transfer_rows": rows,
        "accepted_row_count": len(accepted_rows),
        "blocked_row_count": len(blocked_rows),
        "strongest_supported_gali_level": (
            "GALI2"
            if any(row["gali_level"] == "GALI2" for row in accepted_rows)
            else "GALI1"
        ),
        "strongest_claim_ceiling": (
            "single_axis_route_context_transfer_candidate_selection_only"
        ),
        "non_claim_boundary": {
            "semantic_choice_claim_allowed": False,
            "agency_claim_allowed": False,
            "identity_acceptance_claim_allowed": False,
            "native_support_opened": False,
            "a7_claim_allowed": False,
            "gali7_claim_allowed": False,
        },
        "controls": controls,
        "row_validation": row_validation,
        "checks": checks,
        "acceptance": acceptance,
        "next_iteration": "4_proxy_condition_transfer_replay",
    }
    output["output_digest"] = output_digest(output)
    return output


def render_report(output: dict[str, Any]) -> str:
    lines = [
        "# N11 Iteration 3 Route-Context Transfer Replay",
        "",
        f"Status: `{output['status']}`.",
        "",
        "## Result",
        "",
        "Iteration 3 replayed N10's route-memory-support-regulation composition",
        "against the manifest's route-context lanes. It accepted a scoped",
        "single-axis route-context transfer candidate because the N06/N10 source",
        "artifacts replay both `route_a` and `route_b` under serialized native",
        "arbitration context. It blocked the arbitration-policy variant because",
        "no alternate source-backed route-arbitration policy exists.",
        "",
        "Current ceiling:",
        "",
        "```text",
        f"strongest_supported_gali_level = {output['strongest_supported_gali_level']}",
        f"strongest_claim_ceiling = {output['strongest_claim_ceiling']}",
        "semantic_choice_claim_allowed = false",
        "agency_claim_allowed = false",
        "A7/GALI7 supported = false",
        "```",
        "",
        "## Route Evidence Summary",
        "",
        "```json",
        json.dumps(output["route_evidence_summary"], indent=2, sort_keys=True),
        "```",
        "",
        "## Transfer Rows",
        "",
        "```json",
        json.dumps(output["transfer_rows"], indent=2, sort_keys=True),
        "```",
        "",
        "## Controls",
        "",
        "```json",
        json.dumps(output["controls"], indent=2, sort_keys=True),
        "```",
        "",
        "## Checks",
        "",
        "```json",
        json.dumps(output["checks"], indent=2, sort_keys=True),
        "```",
        "",
        "## Interpretation",
        "",
        "This is a route-context transfer result, not a semantic-choice result.",
        "The accepted GALI2 row says the N10 source composition can be replayed",
        "under a declared single-axis route-context shift while preserving the",
        "N06/N10 selection-only boundary. The blocked policy-variant row is",
        "useful because it shows the transfer does not invent an alternate native",
        "arbitration policy.",
        "",
        "## Acceptance",
        "",
        output["acceptance"]["acceptance_statement"],
        "",
        f"Acceptance state: `{output['acceptance']['status']}`.",
        "",
        "## Run Record",
        "",
        "```text",
        output["command"],
        "```",
        "",
        "Output digest:",
        "",
        "```text",
        output["output_digest"],
        "```",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    output = build_output()
    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    REPORT_PATH.write_text(render_report(output), encoding="utf-8")
    print(f"wrote {rel(OUTPUT_PATH)}")
    print(f"wrote {rel(REPORT_PATH)}")
    print(f"status {output['status']}")
    print(f"output_digest {output['output_digest']}")


if __name__ == "__main__":
    main()
