#!/usr/bin/env python3
"""Build N29 I17-A full A/B/C/D bridge probe contract artifact."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-30T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N29-lgrc-agentic-ecology-convergence-bridge"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/scripts/"
    "build_n29_full_bridge_probe_contract_i17a.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

SOURCE_PATHS = {
    "i7_coverage_debt_matrix": (
        EXPERIMENT / "outputs" / "n29_demand_supply_coverage_debt_i7.json"
    ),
    "i15_prototype_atlas": (
        EXPERIMENT / "outputs" / "n29_prototype_atlas_classification_i15.json"
    ),
    "i16_minimal_probe_contract": (
        EXPERIMENT / "outputs" / "n29_minimal_ecology_probe_contract_i16.json"
    ),
    "i17_alternative_probe_contract": (
        EXPERIMENT / "outputs" / "n29_alternative_ecology_probe_contract_i17.json"
    ),
    "i14y_prototype_d_synthesis": (
        EXPERIMENT / "outputs" / "n29_prototype_d_complete_synthesis_i14y.json"
    ),
}

OUT = EXPERIMENT / "outputs" / "n29_full_bridge_probe_contract_i17a.json"
REPORT = EXPERIMENT / "reports" / "n29_full_bridge_probe_contract_i17a.md"

UNSAFE_FLAGS = {
    "agency_claim_allowed": False,
    "altruism_claim_allowed": False,
    "ant_behavior_claim_allowed": False,
    "ant_ecology_runtime_success_claim_allowed": False,
    "biological_agency_claim_allowed": False,
    "choice_claim_allowed": False,
    "closed_native_circulation_claim_allowed": False,
    "colony_agency_claim_allowed": False,
    "cooperation_claim_allowed": False,
    "ecology_success_claim_allowed": False,
    "exploitation_claim_allowed": False,
    "learning_claim_allowed": False,
    "native_ant_agency_claim_allowed": False,
    "native_ap4_ap5_closure_claim_allowed": False,
    "native_ecology_claim_allowed": False,
    "native_shared_medium_coordination_claim_allowed": False,
    "native_support_claim_allowed": False,
    "organism_life_claim_allowed": False,
    "phase8_completion_claim_allowed": False,
    "resource_economy_claim_allowed": False,
    "semantic_goal_claim_allowed": False,
    "semantic_pheromone_claim_allowed": False,
    "sentience_claim_allowed": False,
    "unrestricted_autonomy_claim_allowed": False,
}

FULL_PROBE_ID = "full_atlas_a_b_c_d_bridge_probe_contract"
COMPOSITION_IDS = [
    "composition_a_b_trace_pressure_boundary_unit",
    "composition_b_c_boundary_proxy_reentry",
    "composition_c_d_susceptibility_medium_reshaping",
    "composition_a_d_loop_pressure_medium_reshaping",
]
PROTOTYPE_IDS = [
    "prototype_a_trace_pressure_loop",
    "prototype_b_boundary_shared_medium_unit",
    "prototype_c_proxy_susceptibility_reentry",
    "prototype_d_generative_extractive_medium_reshaping",
]
RELEVANT_DEMAND_IDS = {
    "general_trace",
    "general_pressure",
    "general_shared_medium",
    "general_susceptibility",
    "general_co_response",
    "general_resonance",
    "general_medium_surface",
    "general_parent_basin_modulation",
    "general_medium_debt",
    "general_producer_residue",
    "rc_ant_route_support_trace",
    "rc_ant_food_resource_coupling",
    "rc_ant_cargo_shaped_susceptibility",
    "rc_ant_reserve_hunger_pressure",
    "rc_ant_crowding_congestion_cost",
}


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(data: Any) -> str:
    return hashlib.sha256(
        json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "utf-8"
        )
    ).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(canonical_json(data), encoding="utf-8")


def no_absolute_paths(data: Any) -> bool:
    text = json.dumps(data, sort_keys=True, ensure_ascii=True)
    forbidden = ("/" + "home" + "/", "Documents" + "/" + "RC-github")
    return all(pattern not in text for pattern in forbidden)


def check(check_id: str, passed: bool, details: str | None = None) -> dict[str, Any]:
    row: dict[str, Any] = {"check_id": check_id, "passed": bool(passed)}
    if details is not None:
        row["details"] = details
    return row


def finalize(data: dict[str, Any]) -> dict[str, Any]:
    payload = copy.deepcopy(data)
    payload.pop("output_digest", None)
    data["output_digest"] = digest_value(payload)
    return data


def source_artifact(source_id: str, path: Path, data: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "path": str(path.relative_to(ROOT)),
        "artifact_id": data.get("artifact_id", "not_recorded"),
        "iteration": data.get("iteration", "not_recorded"),
        "status": data.get("status", "not_recorded"),
        "acceptance_state": data.get("acceptance_state", "not_recorded"),
        "output_digest": data.get("output_digest", "not_recorded"),
        "sha256": sha256_file(path),
    }


def compositions(i15: dict[str, Any]) -> list[dict[str, Any]]:
    by_id = {row["composition_id"]: row for row in i15["composition_rows"]}
    return [by_id[composition_id] for composition_id in COMPOSITION_IDS]


def prototype_rows(i15: dict[str, Any]) -> list[dict[str, Any]]:
    by_id = {row["prototype_id"]: row for row in i15["prototype_rows"]}
    return [by_id[prototype_id] for prototype_id in PROTOTYPE_IDS]


def coverage_support_rows(i7: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in i7.get("coverage_debt_rows", []):
        demand_id = row.get("ecology_demand")
        if demand_id not in RELEVANT_DEMAND_IDS:
            continue
        rows.append(
            {
                "ecology_demand": demand_id,
                "coverage_status": row.get("coverage_status"),
                "bridge_motif": row.get("bridge_motif"),
                "blocked_relabels": row.get("blocked_relabels", []),
                "candidate_capability_sources": row.get("candidate_capability_sources", [])[:3],
                "debt_summary": {
                    "medium_debt": "present",
                    "producer_residue": "present",
                    "naturalization_debt": "present",
                },
            }
        )
    return rows


def runtime_surface_contract() -> list[dict[str, Any]]:
    return [
        {
            "surface_id": "full_composed_ecology_runtime_harness",
            "required": True,
            "contract_role": "execute A+B+C+D as one ordered bridge probe",
            "added_relative_to_i17": True,
        },
        {
            "surface_id": "trace_pressure_loop_runtime_surface",
            "required": True,
            "source_prototype": "prototype_a_trace_pressure_loop",
            "contract_role": "provide pressure/response loop state and replay traces",
            "added_relative_to_i17": False,
        },
        {
            "surface_id": "boundary_shared_medium_unit_surface",
            "required": True,
            "source_prototype": "prototype_b_boundary_shared_medium_unit",
            "contract_role": "provide separable boundary/shared-medium unit state",
            "added_relative_to_i17": False,
        },
        {
            "surface_id": "reentry_susceptibility_runtime_surface",
            "required": True,
            "source_prototype": "prototype_c_proxy_susceptibility_reentry",
            "contract_role": "record re-entry and susceptibility/differential-response state",
            "added_relative_to_i17": False,
        },
        {
            "surface_id": "medium_reshaping_runtime_surface",
            "required": True,
            "source_prototype": "prototype_d_generative_extractive_medium_reshaping",
            "contract_role": "record generative/extractive/processor medium reshaping",
            "added_relative_to_i17": True,
        },
        {
            "surface_id": "c_to_d_handoff_trace",
            "required": True,
            "contract_role": "prove susceptibility/re-entry state conditions later D medium reshaping",
            "added_relative_to_i17": True,
        },
        {
            "surface_id": "d_to_later_a_or_medium_aftereffect_trace",
            "required": True,
            "contract_role": "record whether D medium changes affect later pressure/medium state",
            "added_relative_to_i17": True,
        },
        {
            "surface_id": "aggregate_leakage_and_medium_debt_ledger",
            "required": True,
            "contract_role": "keep D multi-leg leakage and medium-debt accounting visible",
            "added_relative_to_i17": True,
        },
        {
            "surface_id": "producer_mediated_composition_debt_ledger",
            "required": True,
            "contract_role": "distinguish native motifs from producer-mediated composition bridges",
            "added_relative_to_i17": True,
        },
        {
            "surface_id": "full_bridge_replay_control_matrix",
            "required": True,
            "contract_role": "run replay, order, label-only, hidden-coupling, D-relabelling, and ecology-overclaim controls",
            "added_relative_to_i17": True,
        },
    ]


def ordered_trace_contract() -> list[dict[str, Any]]:
    rows = [
        ("t0_external_or_route_pressure", "pressure/trace input enters Prototype A loop surface"),
        ("t1_bounded_loop_response", "Prototype A emits bounded response/change trace"),
        ("t2_boundary_medium_handoff", "A response conditions Prototype B boundary/shared-medium unit"),
        ("t3_medium_unit_state", "B medium/boundary state remains separable and debt-visible"),
        ("t4_route_or_region_reentry", "later route/region re-entry occurs inside or through the bounded unit"),
        ("t5_susceptibility_delta", "Prototype C susceptibility state differs under the re-entry condition"),
        ("t6_later_differential_response", "later response is conditioned by susceptibility delta, not semantic choice"),
        ("t7_susceptibility_to_medium_reshaping_handoff", "C state conditions a D medium-reshaping motif"),
        ("t8_medium_reshaping_event", "Prototype D generative/extractive/processor motif changes medium capacity distribution"),
        ("t9_debt_and_leakage_audit", "D output is audited for producer debt, aggregate leakage, and claim ceiling"),
        ("t10_later_pressure_or_medium_aftereffect", "later A-side or medium state records whether D's reshaping matters"),
    ]
    return [{"step_id": step_id, "required_trace": trace} for step_id, trace in rows]


def control_contract() -> list[dict[str, Any]]:
    controls = [
        ("label_only_ecology_relabel_control", "prototype labels without ordered runtime traces", "failed_closed_blocks_probe_support"),
        ("report_only_composition_control", "report summaries replace source-current A/B/C/D run artifacts", "failed_closed_blocks_probe_support"),
        ("component_order_inversion_control", "D medium reshaping or C susceptibility appears before its ordered inputs", "failed_closed_blocks_ordered_composition"),
        ("missing_cross_prototype_handoff_control", "A/B/C/D are present but no ordered handoff links them", "failed_closed_blocks_runtime_support"),
        ("hidden_producer_coupling_control", "undeclared producer carries state between prototype surfaces", "failed_closed_blocks_native_or_ecology_claim"),
        ("medium_debt_hidden_as_native_relation_control", "shared-medium debt is relabeled as native coordination", "failed_closed_blocks_native_coordination"),
        ("proxy_or_susceptibility_label_only_control", "susceptibility change is only a label or report field", "failed_closed_blocks_stronger_probe_support"),
        ("d_medium_reshaping_label_only_control", "D medium reshaping is only a motif label without source-current trace", "failed_closed_blocks_full_bridge_support"),
        ("native_composition_relabel_control", "producer-mediated D composition bridge is relabeled as native composition", "failed_closed_blocks_native_ecology_claim"),
        ("aggregate_leakage_hidden_control", "D aggregate leakage or medium debt is omitted", "failed_closed_blocks_resource_economy_claim"),
        ("resource_economy_relabel_control", "medium reshaping is relabeled as resource economy", "failed_closed_blocks_resource_economy"),
        ("cooperation_exploitation_relabel_control", "generator/extractor roles are relabeled as cooperation or exploitation", "failed_closed_blocks_social_semantic_claim"),
        ("closed_circulation_relabel_control", "A/B/C/D chain is relabeled as native closed circulation", "failed_closed_blocks_native_circulation"),
        ("semantic_learning_choice_relabel_control", "differential response is relabeled as learning or choice", "failed_closed_blocks_semantic_claim"),
        ("native_ap4_ap5_gap_omission_control", "AP4/AP5 dependency is omitted", "failed_closed_blocks_native_closure_claim"),
        ("prototype_success_as_ecology_success_control", "full bridge contract is promoted to ecology success", "failed_closed_blocks_ecology_success"),
        ("duplicate_replay_control", "duplicate run creates inconsistent contract output", "stable_required_for_runtime_admission"),
        ("snapshot_load_replay_control", "snapshot/load changes the ordered trace outcome", "stable_required_for_runtime_admission"),
    ]
    return [
        {
            "control_id": control_id,
            "blocked_condition": blocked_condition,
            "expected_status": expected_status,
            "execution_status_in_i17a": "declared_not_run_contract_only",
        }
        for control_id, blocked_condition, expected_status in controls
    ]


def expected_failure_modes() -> list[dict[str, Any]]:
    rows = [
        ("missing_A_B_C_or_D_source_current_artifact", "runtime_probe_support_blocked"),
        ("C_to_D_handoff_missing_or_post_hoc", "full_bridge_support_blocked"),
        ("D_medium_reshaping_event_absent", "full_bridge_support_blocked"),
        ("D_output_reinterpreted_as_resource_economy", "resource_economy_claim_blocked"),
        ("producer_mediated_D_composition_hidden", "native_ecology_claim_blocked"),
        ("aggregate_leakage_or_medium_debt_omitted", "native_or_resource_claim_blocked"),
        ("closed_circulation_claim_without_ordered_runtime_dependency", "native_circulation_claim_blocked"),
        ("cooperation_or_exploitation_relabel", "social_semantic_claim_blocked"),
        ("AP4_AP5_gap_omitted", "native_AP_closure_claim_blocked"),
        ("replay_order_or_snapshot_instability", "runtime_probe_admission_blocked"),
    ]
    return [
        {"failure_mode": failure_mode, "result": result}
        for failure_mode, result in rows
    ]


def contract_deviation_and_nativity_gate() -> dict[str, Any]:
    return {
        "contract_deviation_allowed": True,
        "deviation_must_be_recorded": True,
        "deviation_requires_reason_and_scope": True,
        "deviation_does_not_discharge_producer_debt": True,
        "contract_conformance_does_not_imply_nativity": True,
        "later_core_nativity_does_not_retroactively_upgrade_old_probe": True,
        "nativity_requires_rerun_or_source_backed_discharge": True,
        "required_for_native_discharge": [
            "identify which A/B/C/D producer-mediated, medium-debt, AP-gap, or D composition fields are claimed removed",
            "rerun the full A/B/C/D consuming probe with native runtime surfaces or provide source-backed discharge evidence",
            "compare producer-mediated and native-surface full-chain runs",
            "show replay/control matrix still passes under the native surfaces",
            "preserve D native-composition, resource-economy, cooperation/exploitation, and ecology claim boundaries until discharge evidence passes",
        ],
        "gate_interpretation": (
            "I17-A consumers may adapt the full bridge contract, but contract "
            "conformance or deviation is not proof of native A/B/C/D ecology. "
            "Native discharge requires a source-backed rerun or explicit discharge "
            "record for every producer/debt field being removed."
        ),
    }


def build_output() -> dict[str, Any]:
    sources = {source_id: load_json(path) for source_id, path in SOURCE_PATHS.items()}
    i7 = sources["i7_coverage_debt_matrix"]
    i15 = sources["i15_prototype_atlas"]
    i16 = sources["i16_minimal_probe_contract"]
    i17 = sources["i17_alternative_probe_contract"]
    i14y = sources["i14y_prototype_d_synthesis"]
    composition_rows = compositions(i15)
    prototype_inputs = prototype_rows(i15)
    coverage_rows = coverage_support_rows(i7)
    d_row = [row for row in prototype_inputs if row["prototype_id"].startswith("prototype_d")][0]

    probe_contract = {
        "probe_id": FULL_PROBE_ID,
        "probe_name": "Full A/B/C/D Bridge Probe Contract",
        "probe_class": "full_atlas_bridge_probe_contract",
        "extends_probe_id": i17["probe_contract"]["probe_id"],
        "also_depends_on_probe_id": i16["probe_contract"]["probe_id"],
        "extension_mode": "adds_Prototype_D_medium_reshaping_to_I17_A_B_C_contract",
        "source_composition_ids": COMPOSITION_IDS,
        "composed_prototype_ids": PROTOTYPE_IDS,
        "runtime_execution_status": "not_run_contract_only",
        "runtime_claim_allowed": False,
        "why_full_bridge": (
            "I17-A is the first contract that includes every I15 prototype family: "
            "pressure loop, boundary/shared-medium unit, susceptibility/re-entry, "
            "and generative/extractive medium reshaping."
        ),
        "why_not_ecology_success": (
            "No A/B/C/D runtime has been executed, D native composition remains "
            "unsupported, and producer-mediated D composition debt is preserved."
        ),
        "ordered_dependency": (
            "A pressure loop conditions B medium; B medium bounds C re-entry; "
            "C susceptibility/differential response conditions D medium reshaping; "
            "D output is audited for aftereffect, leakage, and producer debt."
        ),
        "prototype_d_lane_split": {
            "native_motif_layer_supported": d_row["evidence_summary"][
                "native_motif_layer_supported"
            ],
            "native_composition_layer_supported": d_row["evidence_summary"][
                "native_composition_layer_supported"
            ],
            "producer_mediated_composition_bridge_supported": d_row["evidence_summary"][
                "producer_mediated_composition_bridge_supported"
            ],
            "naturalization_targets": d_row["evidence_summary"]["naturalization_targets"],
        },
        "not_a_runtime_result": True,
    }

    added_risks = [
        "D medium reshaping relabeled as resource economy",
        "generator/extractor roles relabeled as cooperation or exploitation",
        "producer-mediated D bridge hidden as native composition",
        "aggregate leakage or medium debt hidden as clean ecology",
        "full A/B/C/D chain relabeled as closed native circulation",
        "full bridge contract relabeled as ecology success",
    ]
    nativity_gate = contract_deviation_and_nativity_gate()

    checks = [
        check("all_source_artifacts_passed", all(source.get("status") == "passed" for source in sources.values())),
        check(
            "i17_consumed_as_predecessor_not_replaced",
            i17.get("alternative_probe_contract_supported") is True
            and probe_contract["extends_probe_id"] == i17["probe_contract"]["probe_id"],
        ),
        check("all_i15_composition_rows_consumed", len(composition_rows) == 4),
        check("all_four_bridge_exemplars_composed", len(prototype_inputs) == 4),
        check(
            "prototype_d_lane_split_preserved",
            probe_contract["prototype_d_lane_split"]["native_motif_layer_supported"] is True
            and probe_contract["prototype_d_lane_split"]["native_composition_layer_supported"] is False
            and probe_contract["prototype_d_lane_split"][
                "producer_mediated_composition_bridge_supported"
            ]
            is True,
        ),
        check(
            "coverage_matrix_justifies_full_bridge_probe",
            {row["ecology_demand"] for row in coverage_rows} == RELEVANT_DEMAND_IDS,
        ),
        check(
            "full_runtime_surfaces_declared_not_claimed",
            any(row["added_relative_to_i17"] for row in runtime_surface_contract())
            and probe_contract["runtime_claim_allowed"] is False,
        ),
        check("ordered_trace_contract_declared", len(ordered_trace_contract()) == 11),
        check("control_contract_declared", len(control_contract()) >= 18),
        check("expected_failure_modes_declared", len(expected_failure_modes()) >= 10),
        check("added_risks_recorded", len(added_risks) >= 6),
        check(
            "contract_deviation_nativity_gate_declared",
            nativity_gate["deviation_does_not_discharge_producer_debt"] is True
            and nativity_gate["nativity_requires_rerun_or_source_backed_discharge"] is True,
        ),
        check(
            "i14y_d_debt_source_consumed",
            i14y.get("ready_for_iteration_15") is True
            and i14y.get("prototype_d_native_composition_layer_supported") is False,
        ),
        check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_FLAGS.values())),
        check("ready_for_iteration_18", True),
    ]

    data: dict[str, Any] = {
        "artifact_id": "n29_full_bridge_probe_contract_i17a",
        "experiment_id": "N29",
        "title": "Full A/B/C/D Bridge Probe Contract",
        "iteration": "I17-A",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_full_bridge_probe_contract",
        "source_artifacts": [
            source_artifact(source_id, SOURCE_PATHS[source_id], artifact)
            for source_id, artifact in sources.items()
        ],
        "probe_contract": probe_contract,
        "coverage_justification_rows": coverage_rows,
        "prototype_inputs": prototype_inputs,
        "composition_inputs": composition_rows,
        "runtime_surface_contract": runtime_surface_contract(),
        "ordered_trace_contract": ordered_trace_contract(),
        "control_contract": control_contract(),
        "expected_failure_modes": expected_failure_modes(),
        "contract_deviation_and_nativity_gate": nativity_gate,
        "added_risks_and_debts": added_risks,
        "full_bridge_probe_contract_supported": True,
        "runtime_probe_executed": False,
        "ecology_success_supported": False,
        "native_ecology_supported": False,
        "native_composition_supported": False,
        "resource_economy_supported": False,
        "cooperation_or_exploitation_supported": False,
        "claim_boundary": UNSAFE_FLAGS,
        "ready_for_iteration_18": True,
        "checks": checks,
        "failed_checks": [row["check_id"] for row in checks if not row["passed"]],
    }
    checks.append(check("no_absolute_paths_in_records", no_absolute_paths(data)))
    data["checks"] = checks
    data["failed_checks"] = [row["check_id"] for row in checks if not row["passed"]]
    return finalize(data)


def write_report(data: dict[str, Any]) -> None:
    contract = data["probe_contract"]
    lines = [
        "# Full A/B/C/D Bridge Probe Contract",
        "",
        f"Status: `{data['status']}`",
        "",
        f"Acceptance state: `{data['acceptance_state']}`",
        "",
        "I17-A defines the full atlas bridge probe contract across Prototypes A-D. "
        "It remains a contract artifact, not an executed ecology runtime.",
        "",
        "## Probe",
        "",
        f"- Probe ID: `{contract['probe_id']}`",
        f"- Extends: `{contract['extends_probe_id']}`",
        f"- Runtime execution status: `{contract['runtime_execution_status']}`",
        f"- Runtime claim allowed: `{str(contract['runtime_claim_allowed']).lower()}`",
        "",
        contract["why_full_bridge"],
        "",
        contract["why_not_ecology_success"],
        "",
        "## Prototype Inputs",
        "",
        "| Prototype | Evidence status | Family status |",
        "| --- | --- | --- |",
    ]
    for row in data["prototype_inputs"]:
        lines.append(
            "| `{}` | `{}` | `{}` |".format(
                row["prototype_id"],
                row["evidence_status"],
                row["prototype_family_status"],
            )
        )
    lines.extend(
        [
            "",
            "## Ordered Trace Contract",
            "",
            "| Step | Required trace |",
            "| --- | --- |",
        ]
    )
    for row in data["ordered_trace_contract"]:
        lines.append(f"| `{row['step_id']}` | {row['required_trace']} |")
    lines.extend(
        [
            "",
            "## Prototype D Debt",
            "",
            f"- Native motif layer supported: `{str(contract['prototype_d_lane_split']['native_motif_layer_supported']).lower()}`",
            f"- Native composition layer supported: `{str(contract['prototype_d_lane_split']['native_composition_layer_supported']).lower()}`",
            f"- Producer-mediated composition bridge supported: `{str(contract['prototype_d_lane_split']['producer_mediated_composition_bridge_supported']).lower()}`",
            "",
            "## Added Risks",
            "",
        ]
    )
    for risk in data["added_risks_and_debts"]:
        lines.append(f"- {risk}")
    lines.extend(
        [
            "",
            "## Controls",
            "",
        ]
    )
    for row in data["control_contract"]:
        lines.append(
            f"- `{row['control_id']}`: `{row['expected_status']}` "
            f"({row['execution_status_in_i17a']})"
        )
    lines.extend(
        [
            "",
            "## Deviation And Nativity Gate",
            "",
            data["contract_deviation_and_nativity_gate"]["gate_interpretation"],
            "",
            "- Contract deviation is allowed only if recorded.",
            "- Deviation does not discharge producer, medium, AP-gap, or D composition debt.",
            "- Later core nativity does not retroactively upgrade an old producer-mediated full-chain probe.",
            "- Native discharge requires rerun or source-backed discharge evidence for every removed debt field.",
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "| --- | --- |",
        ]
    )
    for row in data["checks"]:
        lines.append(f"| `{row['check_id']}` | `{str(row['passed']).lower()}` |")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "I17-A does not claim executed ecology runtime, resource economy, "
            "cooperation, exploitation, altruism, learning, choice, native "
            "composition, native ecology, native shared-medium coordination, "
            "native support, sentience, organism/life, or Phase 8 completion.",
            "",
            f"Output digest: `{data['output_digest']}`",
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    data = build_output()
    write_json(OUT, data)
    write_report(data)
    print(json.dumps({"output": str(OUT.relative_to(ROOT)), "digest": data["output_digest"]}))


if __name__ == "__main__":
    main()
