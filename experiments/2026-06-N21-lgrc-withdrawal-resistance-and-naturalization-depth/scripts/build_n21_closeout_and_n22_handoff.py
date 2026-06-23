#!/usr/bin/env python3
"""Build N21 Iteration 7 closeout and N22 handoff."""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-23T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth"
)
OUTPUT = EXPERIMENT / "outputs" / "n21_closeout_and_n22_handoff.json"
REPORT = EXPERIMENT / "reports" / "n21_closeout_and_n22_handoff.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/"
    "scripts/build_n21_closeout_and_n22_handoff.py"
)

N20_EXPERIMENT = (
    ROOT / "experiments" / "2026-06-N20-lgrc-becoming-primitive-producer-translation-contract"
)
N20_I5_OUTPUT_PATH = (
    "experiments/2026-06-N20-lgrc-becoming-primitive-producer-translation-contract/"
    "outputs/n20_same_basin_continuation_contract.json"
)

I1_OUTPUT_PATH = (
    "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/"
    "outputs/n21_source_contract_inventory.json"
)
I2_OUTPUT_PATH = (
    "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/"
    "outputs/n21_withdrawal_schema_and_thresholds.json"
)
I3_OUTPUT_PATH = (
    "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/"
    "outputs/n21_withdrawal_active_nulls.json"
)
I4_OUTPUT_PATH = (
    "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/"
    "outputs/n21_withdrawal_resistance_probe.json"
)
I4A_OUTPUT_PATH = (
    "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/"
    "outputs/n21_withdrawal_severity_boundary_probe.json"
)
I4B_OUTPUT_PATH = (
    "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/"
    "outputs/n21_withdrawal_transfer_shape_probe.json"
)
I5_OUTPUT_PATH = (
    "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/"
    "outputs/n21_naturalization_depth_probe.json"
)
I5A_OUTPUT_PATH = (
    "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/"
    "outputs/n21_naturalization_depth_post_probe_derivation.json"
)
I5B_OUTPUT_PATH = (
    "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/"
    "outputs/n21_naturalization_depth_eventful_post_probe.json"
)
I6_OUTPUT_PATH = (
    "experiments/2026-06-N21-lgrc-withdrawal-resistance-and-naturalization-depth/"
    "outputs/n21_replay_and_control_matrix.json"
)

SOURCE_OUTPUTS = [
    (N20_I5_OUTPUT_PATH, "n20_susceptibility_update_contract_source"),
    (I1_OUTPUT_PATH, "source_contract_inventory"),
    (I2_OUTPUT_PATH, "schema_and_threshold_freeze"),
    (I3_OUTPUT_PATH, "active_nulls_and_failure_baselines"),
    (I4_OUTPUT_PATH, "reference_support_weakening_candidate"),
    (I4A_OUTPUT_PATH, "severity_and_removal_boundary_map"),
    (I4B_OUTPUT_PATH, "transfer_and_schedule_shape_candidates"),
    (I5_OUTPUT_PATH, "no_probe_initial_fixture_candidate"),
    (I5A_OUTPUT_PATH, "post_probe_derived_static_candidate"),
    (I5B_OUTPUT_PATH, "eventful_post_probe_derived_candidate"),
    (I6_OUTPUT_PATH, "replay_and_control_matrix"),
]

GLOBAL_UNSAFE_CLAIMS = [
    "agency",
    "semantic_action",
    "semantic_perception",
    "semantic_goal_ownership",
    "semantic_intention",
    "semantic_choice",
    "selfhood",
    "identity_acceptance",
    "native_support",
    "phase8_implementation",
    "fully_native_integration",
    "organism_life",
    "sentience",
    "consciousness",
    "native_ant_agency",
    "native_colony_agency",
    "unrestricted_autonomy",
]

ACCEPTED_WR_STATUSES = {
    "withdrawal_resistance_supported_artifact_level_candidate",
    "withdrawal_resistance_partial_or_blocked",
    "withdrawal_resistance_rejected",
}

ACCEPTED_ND_STATUSES = {
    "naturalization_depth_supported_bounded_N21_candidate",
    "naturalization_depth_rung_limited_candidate",
    "naturalization_depth_partial_or_blocked",
    "naturalization_depth_rejected",
}

BLOCKED_CLOSEOUT_CLAIMS = [
    "agency",
    "choice",
    "willpower",
    "semantic action",
    "semantic perception",
    "semantic goal ownership",
    "semantic intention",
    "selfhood",
    "identity acceptance",
    "native support",
    "Phase 8 implementation",
    "sentience",
    "consciousness",
    "organism/life",
    "native ant agency",
    "native colony agency",
    "unrestricted autonomy",
    "ant ecology implementation",
    "support-removal resistance",
    "robust withdrawal resistance",
    "general naturalization depth",
    "ND6 naturalization closeout",
]


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json(data), encoding="utf-8")


def load_json(relative_path: str) -> dict[str, Any]:
    data = json.loads((ROOT / relative_path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{relative_path} must contain a JSON object")
    return data


def sha256_file(relative_path: str) -> str:
    return hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()


def digest_value(data: dict[str, Any]) -> str:
    payload = copy.deepcopy(data)
    payload.pop("generated_at", None)
    payload.pop("output_digest", None)
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "utf-8"
        )
    ).hexdigest()


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check_id": check_id, "passed": passed, "detail": detail}


def git_status_short(pathspec: str) -> list[str]:
    result = subprocess.run(
        ["git", "status", "--short", "--", pathspec],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line.strip()]


def src_diff_empty() -> bool:
    result = subprocess.run(
        ["git", "diff", "--quiet", "--", "src"],
        cwd=ROOT,
        check=False,
    )
    return result.returncode == 0 and not git_status_short("src")


def contains_absolute_path(value: Any) -> bool:
    if isinstance(value, str):
        markers = (
            "/" + "home" + "/",
            "/" + "tmp" + "/",
            "/" + "Users" + "/",
            "file" + "://",
            "vscode" + "://",
            "C:" + "\\",
            "\\Users\\",
        )
        return value.startswith(("/", "\\")) or any(marker in value for marker in markers)
    if isinstance(value, dict):
        return any(contains_absolute_path(item) for item in value.values())
    if isinstance(value, list):
        return any(contains_absolute_path(item) for item in value)
    return False


def source_record(path: str, role: str) -> dict[str, Any]:
    data = load_json(path)
    return {
        "path": path,
        "sha256": sha256_file(path),
        "source_role": role,
        "artifact_id": data.get("artifact_id", "not_recorded"),
        "status": data.get("status", "not_recorded"),
        "acceptance_state": data.get("acceptance_state", "not_recorded"),
        "output_digest": data.get("output_digest", "not_recorded"),
        "failed_checks": data.get("failed_checks", "not_recorded"),
    }


def schema_rows(i2: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = i2["schema_freeze"]["primitive_schema_rows"]
    return {row["primitive_id"]: row for row in rows}


def susceptibility_contract(n20_i5: dict[str, Any]) -> dict[str, Any]:
    for row in n20_i5["contract_rows"]:
        if row["primitive_id"] == "susceptibility_update":
            return row
    raise KeyError("susceptibility_update row not found in N20 I5")


def unsafe_claim_flags() -> dict[str, bool]:
    return {claim: False for claim in GLOBAL_UNSAFE_CLAIMS}


def i6_rows_by_primitive(i6: dict[str, Any], primitive_id: str) -> list[dict[str, Any]]:
    return [
        row for row in i6["candidate_rows"] if row["primitive_id"] == primitive_id
    ]


def hypothesis_closeout(i6: dict[str, Any]) -> list[dict[str, Any]]:
    summary = i6["matrix_summary"]
    return [
        {
            "hypothesis_id": "hypothesis_a_withdrawal_resistance",
            "closeout_decision": "supported_bounded_artifact_level_candidate",
            "supported_by": ["I4", "I4-A", "I4-B", "I6"],
            "basis": (
                "Eight WR rows are I6-consumable at WR5, with I4-A mapping "
                "the floor/removal boundary and no failed-open controls."
            ),
            "claim_ceiling": "bounded artifact-level withdrawal-resistance candidate",
            "unsafe_promotions_blocked": True,
            "supporting_metric": summary["wr5_consumable_rows"],
        },
        {
            "hypothesis_id": "hypothesis_b_naturalization_depth",
            "closeout_decision": "supported_bounded_N21_candidate",
            "supported_by": ["I5", "I5-A", "I5-B", "I6"],
            "basis": (
                "I5 supplies ND3 no-probe baseline evidence; I5-A and I5-B "
                "supply I6-consumable ND4 post-probe-derived evidence."
            ),
            "claim_ceiling": "bounded N21 naturalization-depth candidate, not general naturalization depth",
            "unsafe_promotions_blocked": True,
            "supporting_metric": summary["nd4_consumable_rows"],
        },
        {
            "hypothesis_id": "hypothesis_c_claim_boundary_and_producer_residue",
            "closeout_decision": "supported_as_claim_boundary_and_residue_guard",
            "supported_by": ["I1", "I2", "I3", "I6", "I7"],
            "basis": (
                "All unsafe claim flags remain false, failed-open controls are "
                "zero, source artifacts are repository-relative, and producer "
                "residue/debt fields are recorded rather than promoted."
            ),
            "claim_ceiling": "claim hygiene condition for A/B support",
            "unsafe_promotions_blocked": True,
            "supporting_metric": summary["failed_open_controls"],
        },
    ]


def build_payload() -> dict[str, Any]:
    sources = {path: load_json(path) for path, _role in SOURCE_OUTPUTS}
    i2 = sources[I2_OUTPUT_PATH]
    i6 = sources[I6_OUTPUT_PATH]
    n20_susceptibility = susceptibility_contract(sources[N20_I5_OUTPUT_PATH])
    primitive_schema = schema_rows(i2)
    wr_schema = primitive_schema["withdrawal_resistance"]
    nd_schema = primitive_schema["naturalization_depth"]
    wr_rows = i6_rows_by_primitive(i6, "withdrawal_resistance")
    nd_rows = i6_rows_by_primitive(i6, "naturalization_depth")
    wr5_rows = [row for row in wr_rows if row["i6_consumable_rung"] == "WR5"]
    wr_boundary_rows = [
        row
        for row in wr_rows
        if row["candidate_input_role"]
        == "i4a_floor_boundary_or_fail_closed_boundary_evidence"
    ]
    nd3_rows = [
        row
        for row in nd_rows
        if row["i6_consumable_rung"]
        == "ND3_initial_fixture_no_probe_replay_candidate"
    ]
    nd4_rows = [row for row in nd_rows if row["i6_consumable_rung"] == "ND4"]

    closeout = {
        "artifact_id": "n21_closeout_and_n22_handoff",
        "schema_version": "1.0",
        "experiment": "N21",
        "iteration": "7",
        "generated_at": GENERATED_AT,
        "status": "pending",
        "acceptance_state": "pending",
        "purpose": (
            "Close N21 withdrawal resistance and naturalization depth, record "
            "claim ceiling and remaining producer debt, and hand bounded "
            "primitive evidence to N22 susceptibility update."
        ),
        "command": COMMAND,
        "source_artifacts": [
            source_record(path, role) for path, role in SOURCE_OUTPUTS
        ],
        "source_i6_output_digest": i6["output_digest"],
        "withdrawal_resistance_closeout": {
            "withdrawal_resistance_status": (
                "withdrawal_resistance_supported_artifact_level_candidate"
            ),
            "withdrawal_resistance_ladder_rung": "WR6",
            "source_backed_i6_consumable_rung": "WR5",
            "support_basis": {
                "wr5_consumable_row_count": len(wr5_rows),
                "supporting_rows": [row["candidate_id"] for row in wr5_rows],
                "boundary_rows": [row["candidate_id"] for row in wr_boundary_rows],
                "floor_boundary_row": "n21_i4a_row_amount_0_06",
                "below_floor_or_removal_rejections": [
                    "n21_i4a_row_amount_0_05",
                    "n21_i4a_row_amount_0_03",
                    "n21_i4a_row_amount_0_00",
                ],
            },
            "claim_scope": (
                "artifact-level bounded withdrawal-resistance candidate under "
                "declared support weakening and transfer/schedule-shape probes"
            ),
            "not_supported": [
                "support-removal resistance",
                "robust withdrawal resistance",
                "native support",
                "agency",
                "Phase 8",
                "sentience",
            ],
        },
        "naturalization_depth_closeout": {
            "naturalization_depth_status": (
                "naturalization_depth_supported_bounded_N21_candidate"
            ),
            "naturalization_depth_ladder_rung": "ND5",
            "source_backed_i6_consumable_rungs": {
                "initial_fixture_baseline": [row["candidate_id"] for row in nd3_rows],
                "post_probe_derived_rows": [row["candidate_id"] for row in nd4_rows],
            },
            "support_basis": {
                "nd3_consumable_row_count": len(nd3_rows),
                "nd4_consumable_row_count": len(nd4_rows),
                "static_post_probe_row": "n21_i5a_row_01_post_probe_derived_state_persistence",
                "eventful_post_probe_row": "n21_i5b_row_01_eventful_post_probe_continuation",
            },
            "claim_scope": (
                "bounded N21-local post-probe-derived naturalization-depth "
                "candidate with producer/debt boundedness recorded"
            ),
            "not_supported": [
                "ND6 general artifact-level naturalization depth",
                "general naturalization-depth ladder",
                "native support",
                "agency",
                "Phase 8",
                "sentience",
            ],
        },
        "combined_closeout": {
            "n21_closeout_ladder_rung": "N21-C6",
            "n21_closeout_status": "n22_ready_bounded_primitive_evidence",
            "final_supported_status": (
                "bounded_artifact_level_withdrawal_and_naturalization_candidate"
            ),
            "final_claim_ceiling": (
                "bounded artifact-level WR6 withdrawal candidate plus bounded "
                "N21-local ND5 naturalization-depth candidate; no agency, "
                "native support, sentience, Phase 8, or ant-ecology implementation"
            ),
            "ready_for_n22": True,
        },
        "producer_residue_remaining": {
            "withdrawal_resistance": wr_schema["producer_mediated_fields"],
            "naturalization_depth": nd_schema["producer_mediated_fields"],
            "n22_susceptibility_update": n20_susceptibility[
                "producer_mediated_fields"
            ],
        },
        "naturalization_debt_remaining": {
            "withdrawal_resistance": wr_schema["naturalization_debt_fields"],
            "naturalization_depth": nd_schema["naturalization_debt_fields"],
            "n22_susceptibility_update": n20_susceptibility[
                "naturalization_debt_fields"
            ],
        },
        "claim_boundary": {
            "unsafe_claim_flags": unsafe_claim_flags(),
            "blocked_closeout_claims": BLOCKED_CLOSEOUT_CLAIMS,
            "agency_supported": False,
            "native_support_supported": False,
            "sentience_supported": False,
            "phase8_opened": False,
            "ant_ecology_implementation_opened": False,
            "source_mutation_supported": False,
        },
        "hypothesis_closeout": hypothesis_closeout(i6),
        "n22_handoff": {
            "ready_for_n22": True,
            "target_experiment": "N22",
            "target_primitive": "susceptibility_update",
            "handoff_scope": (
                "durable geometry modification / susceptibility update after "
                "withdrawal and post-probe persistence evidence"
            ),
            "source_contract_row": n20_susceptibility["row_id"],
            "source_contract_status": n20_susceptibility["contract_status"],
            "required_n22_inputs": n20_susceptibility[
                "primitive_specific_consumption_inputs"
            ],
            "source_current_fields": n20_susceptibility["LGRC_visible_fields"],
            "same_basin_continuation_rule": n20_susceptibility[
                "same_basin_continuation_rule"
            ],
            "ap_gap_contract": n20_susceptibility["ap_gap_contract"],
            "minimum_controls": n20_susceptibility["minimum_controls"],
            "n21_consumable_inputs": {
                "withdrawal_resistance_status": (
                    "withdrawal_resistance_supported_artifact_level_candidate"
                ),
                "withdrawal_resistance_ladder_rung": "WR6",
                "naturalization_depth_status": (
                    "naturalization_depth_supported_bounded_N21_candidate"
                ),
                "naturalization_depth_ladder_rung": "ND5",
            },
            "handoff_blockers": [
                "N22 must produce new source-backed durable geometry deltas",
                "N22 may not treat N21 WR/ND closeout as susceptibility evidence",
                "N22 must keep AP4 dependency row-local when route-conditioned selection participates",
                "N22 must carry conditional AP5 dependency if proxy or target formation participates",
                "N22 must keep producer route update / reinforcement / learning labels out of native support",
            ],
        },
        "src_diff_empty": src_diff_empty(),
        "output_digest": "pending",
    }

    closeout["checks"] = build_checks(closeout, i6)
    closeout["failed_checks"] = [
        item["check_id"] for item in closeout["checks"] if not item["passed"]
    ]
    closeout["status"] = "passed" if not closeout["failed_checks"] else "failed"
    closeout["acceptance_state"] = (
        "closed_n21_bounded_wr_nd_candidate_and_n22_handoff"
        if closeout["status"] == "passed"
        else "failed_n21_closeout_and_n22_handoff"
    )
    closeout["output_digest"] = digest_value(closeout)
    return closeout


def build_checks(closeout: dict[str, Any], i6: dict[str, Any]) -> list[dict[str, Any]]:
    wr = closeout["withdrawal_resistance_closeout"]
    nd = closeout["naturalization_depth_closeout"]
    combined = closeout["combined_closeout"]
    boundary = closeout["claim_boundary"]
    handoff = closeout["n22_handoff"]
    i6_summary = i6["matrix_summary"]

    return [
        check(
            "source_artifacts_present_and_clean",
            all(source["failed_checks"] == [] for source in closeout["source_artifacts"]),
            {source["path"]: source["output_digest"] for source in closeout["source_artifacts"]},
        ),
        check(
            "i6_ready_for_closeout",
            i6["status"] == "passed"
            and i6_summary["ready_for_iteration7_closeout"] is True
            and i6_summary["failed_open_controls"] == 0
            and i6_summary["not_run_controls"] == 0
            and i6_summary["failed_open_replays"] == 0
            and i6_summary["not_run_replays"] == 0,
            i6_summary,
        ),
        check(
            "withdrawal_resistance_status_enum_valid",
            wr["withdrawal_resistance_status"] in ACCEPTED_WR_STATUSES,
            wr["withdrawal_resistance_status"],
        ),
        check(
            "withdrawal_resistance_wr6_closeout_supported",
            wr["withdrawal_resistance_ladder_rung"] == "WR6"
            and wr["support_basis"]["wr5_consumable_row_count"] == 8
            and len(wr["support_basis"]["boundary_rows"]) == 4,
            wr["support_basis"],
        ),
        check(
            "naturalization_depth_status_enum_valid",
            nd["naturalization_depth_status"] in ACCEPTED_ND_STATUSES,
            nd["naturalization_depth_status"],
        ),
        check(
            "naturalization_depth_nd5_closeout_supported",
            nd["naturalization_depth_ladder_rung"] == "ND5"
            and nd["support_basis"]["nd3_consumable_row_count"] == 1
            and nd["support_basis"]["nd4_consumable_row_count"] == 2,
            nd["support_basis"],
        ),
        check(
            "n21_c6_handoff_supported",
            combined["n21_closeout_ladder_rung"] == "N21-C6"
            and combined["ready_for_n22"] is True
            and handoff["ready_for_n22"] is True,
            combined,
        ),
        check(
            "producer_residue_and_debt_recorded",
            all(closeout["producer_residue_remaining"].values())
            and all(closeout["naturalization_debt_remaining"].values()),
            {
                "producer_residue_remaining": closeout["producer_residue_remaining"],
                "naturalization_debt_remaining": closeout[
                    "naturalization_debt_remaining"
                ],
            },
        ),
        check(
            "unsafe_claims_blocked",
            all(value is False for value in boundary["unsafe_claim_flags"].values())
            and boundary["agency_supported"] is False
            and boundary["native_support_supported"] is False
            and boundary["sentience_supported"] is False
            and boundary["phase8_opened"] is False
            and boundary["ant_ecology_implementation_opened"] is False,
            boundary,
        ),
        check(
            "n22_handoff_contract_complete",
            handoff["source_contract_status"] == "complete"
            and handoff["target_primitive"] == "susceptibility_update"
            and "durable_geometry_modification_controls"
            in handoff["required_n22_inputs"],
            handoff["required_n22_inputs"],
        ),
        check(
            "src_diff_empty",
            closeout["src_diff_empty"] is True,
            closeout["src_diff_empty"],
        ),
        check(
            "no_absolute_paths",
            not contains_absolute_path(closeout),
            "all closeout paths are repository-relative",
        ),
    ]


def write_report(data: dict[str, Any]) -> None:
    wr = data["withdrawal_resistance_closeout"]
    nd = data["naturalization_depth_closeout"]
    combined = data["combined_closeout"]
    lines = [
        "# N21 Iteration 7 - Closeout And N22 Handoff",
        "",
        "## Summary",
        "",
        f"Status: `{data['status']}`",
        "",
        f"Acceptance state: `{data['acceptance_state']}`",
        "",
        f"Output digest: `{data['output_digest']}`",
        "",
        "```text",
        f"withdrawal_resistance_status = {wr['withdrawal_resistance_status']}",
        f"withdrawal_resistance_ladder_rung = {wr['withdrawal_resistance_ladder_rung']}",
        f"naturalization_depth_status = {nd['naturalization_depth_status']}",
        f"naturalization_depth_ladder_rung = {nd['naturalization_depth_ladder_rung']}",
        f"n21_closeout_ladder_rung = {combined['n21_closeout_ladder_rung']}",
        f"final_supported_status = {combined['final_supported_status']}",
        f"ready_for_n22 = {str(combined['ready_for_n22']).lower()}",
        "agency_supported = false",
        "native_support_supported = false",
        "sentience_supported = false",
        "phase8_opened = false",
        "ant_ecology_implementation_opened = false",
        "```",
        "",
        "## Withdrawal Resistance",
        "",
        "N21 closes withdrawal resistance as a bounded artifact-level candidate.",
        "I6 provided eight WR5-consumable rows and I7 records the remaining",
        "producer residue, naturalization debt, and claim boundary, allowing the",
        "final WR rung to close as `WR6` without promoting support removal,",
        "robust withdrawal resistance, native support, or agency.",
        "",
        "```text",
        f"wr5_consumable_row_count = {wr['support_basis']['wr5_consumable_row_count']}",
        f"floor_boundary_row = {wr['support_basis']['floor_boundary_row']}",
        f"below_floor_or_removal_rejections = {wr['support_basis']['below_floor_or_removal_rejections']}",
        "```",
        "",
        "## Naturalization Depth",
        "",
        "N21 closes naturalization depth as a bounded N21-local candidate. I5",
        "remains an ND3 initial-fixture no-probe baseline. I5-A and I5-B are",
        "post-probe-derived rows and become ND4-consumable through I6 controls.",
        "I7 records producer/debt boundedness, so the closeout rung is `ND5`.",
        "`ND6` and general naturalization depth remain blocked.",
        "",
        "```text",
        f"nd3_consumable_row_count = {nd['support_basis']['nd3_consumable_row_count']}",
        f"nd4_consumable_row_count = {nd['support_basis']['nd4_consumable_row_count']}",
        f"static_post_probe_row = {nd['support_basis']['static_post_probe_row']}",
        f"eventful_post_probe_row = {nd['support_basis']['eventful_post_probe_row']}",
        "```",
        "",
        "## Remaining Producer Residue And Debt",
        "",
        "```text",
        f"producer_residue_remaining = {data['producer_residue_remaining']}",
        f"naturalization_debt_remaining = {data['naturalization_debt_remaining']}",
        "```",
        "",
        "## N22 Handoff",
        "",
        "N22 should test susceptibility update / durable geometry modification.",
        "It must produce new source-backed durable geometry deltas; N21 evidence",
        "is only prerequisite context. Route-conditioned susceptibility carries",
        "the AP4 dependency, and proxy/target-conditioned susceptibility carries",
        "the conditional AP5 dependency.",
        "",
        "```text",
        f"target_primitive = {data['n22_handoff']['target_primitive']}",
        f"source_contract_row = {data['n22_handoff']['source_contract_row']}",
        f"required_n22_inputs = {data['n22_handoff']['required_n22_inputs']}",
        "```",
        "",
        "## Checks",
        "",
        "| Check | Passed | Detail |",
        "| --- | --- | --- |",
    ]
    for item in data["checks"]:
        detail = item["detail"]
        if not isinstance(detail, str):
            detail = json.dumps(detail, sort_keys=True)
        lines.append(
            f"| `{item['check_id']}` | `{str(item['passed']).lower()}` | {detail} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "N21 closes as bounded primitive evidence for withdrawal resistance and",
            "naturalization depth. It does not close agency, native support,",
            "sentience, Phase 8, ant ecology, general naturalization depth, or",
            "support-removal resistance. The result is N22-ready because the",
            "first two becoming primitives now have controlled source-backed",
            "evidence and clean claim boundaries.",
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    data = build_payload()
    write_json(OUTPUT, data)
    write_report(data)
    if data["failed_checks"]:
        raise SystemExit(f"Failed checks: {data['failed_checks']}")


if __name__ == "__main__":
    main()
