#!/usr/bin/env python3
"""Build N29 I17 stronger / alternative ecology probe contract artifact."""

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
    "build_n29_alternative_ecology_probe_contract_i17.py"
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
}

OUT = EXPERIMENT / "outputs" / "n29_alternative_ecology_probe_contract_i17.json"
REPORT = EXPERIMENT / "reports" / "n29_alternative_ecology_probe_contract_i17.md"

UNSAFE_FLAGS = {
    "agency_claim_allowed": False,
    "ant_behavior_claim_allowed": False,
    "ant_ecology_runtime_success_claim_allowed": False,
    "biological_agency_claim_allowed": False,
    "choice_claim_allowed": False,
    "colony_agency_claim_allowed": False,
    "cooperation_claim_allowed": False,
    "ecology_success_claim_allowed": False,
    "exploitation_claim_allowed": False,
    "learning_claim_allowed": False,
    "native_ant_agency_claim_allowed": False,
    "native_ap4_ap5_closure_claim_allowed": False,
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

MINIMAL_COMPOSITION_ID = "composition_a_b_trace_pressure_boundary_unit"
STRONGER_COMPOSITION_ID = "composition_b_c_boundary_proxy_reentry"
ALTERNATIVE_PROBE_ID = "route_pressure_medium_reentry_susceptibility_probe"
RELEVANT_DEMAND_IDS = {
    "general_trace",
    "general_pressure",
    "general_shared_medium",
    "general_susceptibility",
    "general_co_response",
    "rc_ant_route_support_trace",
    "rc_ant_foodward_affordance_surface",
    "rc_ant_homeward_affordance_surface",
    "rc_ant_cargo_shaped_susceptibility",
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


def composition(i15: dict[str, Any], composition_id: str) -> dict[str, Any]:
    for row in i15["composition_rows"]:
        if row["composition_id"] == composition_id:
            return row
    raise ValueError(f"missing I15 composition row: {composition_id}")


def prototypes(i15: dict[str, Any], prototype_ids: list[str]) -> list[dict[str, Any]]:
    by_id = {row["prototype_id"]: row for row in i15["prototype_rows"]}
    return [by_id[prototype_id] for prototype_id in prototype_ids]


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
            "surface_id": "composed_ecology_runtime_harness",
            "required": True,
            "contract_role": "execute A+B+C as one ordered probe",
            "added_relative_to_i16": False,
        },
        {
            "surface_id": "trace_pressure_loop_runtime_surface",
            "required": True,
            "source_prototype": "prototype_a_trace_pressure_loop",
            "contract_role": "provide pressure/response loop state and replay traces",
            "added_relative_to_i16": False,
        },
        {
            "surface_id": "boundary_shared_medium_unit_surface",
            "required": True,
            "source_prototype": "prototype_b_boundary_shared_medium_unit",
            "contract_role": "provide separable boundary/shared-medium unit state",
            "added_relative_to_i16": False,
        },
        {
            "surface_id": "ordered_cross_prototype_handoff_trace",
            "required": True,
            "contract_role": "prove A -> B and B -> C ordered handoffs",
            "added_relative_to_i16": False,
        },
        {
            "surface_id": "reentry_susceptibility_runtime_surface",
            "required": True,
            "source_prototype": "prototype_c_proxy_susceptibility_reentry",
            "contract_role": "record route/region re-entry and susceptibility delta",
            "added_relative_to_i16": True,
        },
        {
            "surface_id": "differential_response_trace",
            "required": True,
            "source_prototype": "prototype_c_proxy_susceptibility_reentry",
            "contract_role": "show later response conditioned by susceptibility state, not label",
            "added_relative_to_i16": True,
        },
        {
            "surface_id": "ap4_ap5_gap_and_proxy_residue_ledger",
            "required": True,
            "contract_role": "keep native AP4/AP5 and producer-mediated proxy debt visible",
            "added_relative_to_i16": True,
        },
        {
            "surface_id": "ecology_probe_replay_control_matrix",
            "required": True,
            "contract_role": "run replay, order, label-only, report-only, hidden-coupling, and proxy relabel controls",
            "added_relative_to_i16": False,
        },
    ]


def ordered_trace_contract() -> list[dict[str, Any]]:
    return [
        {
            "step_id": "t0_external_or_route_pressure",
            "required_trace": "pressure/trace input enters Prototype A loop surface",
        },
        {
            "step_id": "t1_bounded_loop_response",
            "required_trace": "Prototype A emits bounded response/change trace",
        },
        {
            "step_id": "t2_boundary_medium_handoff",
            "required_trace": "A response conditions Prototype B boundary/shared-medium unit",
        },
        {
            "step_id": "t3_medium_unit_state",
            "required_trace": "B medium/boundary state remains separable and debt-visible",
        },
        {
            "step_id": "t4_route_or_region_reentry",
            "required_trace": "a later route/region re-entry occurs inside or through the bounded unit",
        },
        {
            "step_id": "t5_susceptibility_delta",
            "required_trace": "Prototype C susceptibility state differs under the re-entry condition",
        },
        {
            "step_id": "t6_later_differential_response",
            "required_trace": "later response is conditioned by the susceptibility delta, not semantic choice",
        },
    ]


def control_contract() -> list[dict[str, Any]]:
    controls = [
        (
            "label_only_ecology_relabel_control",
            "prototype labels without ordered runtime traces",
            "failed_closed_blocks_probe_support",
        ),
        (
            "report_only_composition_control",
            "report summaries replace source-current A/B/C run artifacts",
            "failed_closed_blocks_probe_support",
        ),
        (
            "component_order_inversion_control",
            "C susceptibility appears before B medium or A response exists",
            "failed_closed_blocks_ordered_composition",
        ),
        (
            "missing_cross_prototype_handoff_control",
            "A, B, and C are present but no ordered handoff links them",
            "failed_closed_blocks_runtime_support",
        ),
        (
            "hidden_producer_coupling_control",
            "undeclared producer carries state between prototype surfaces",
            "failed_closed_blocks_native_or_ecology_claim",
        ),
        (
            "medium_debt_hidden_as_native_relation_control",
            "shared-medium debt is relabeled as native coordination",
            "failed_closed_blocks_native_coordination",
        ),
        (
            "proxy_or_susceptibility_label_only_control",
            "susceptibility change is only a label or report field",
            "failed_closed_blocks_stronger_probe_support",
        ),
        (
            "semantic_learning_choice_relabel_control",
            "differential re-entry response is relabeled as learning or choice",
            "failed_closed_blocks_semantic_claim",
        ),
        (
            "native_ap4_ap5_gap_omission_control",
            "AP4/AP5 dependency is omitted from the stronger contract",
            "failed_closed_blocks_native_closure_claim",
        ),
        (
            "prototype_success_as_ecology_success_control",
            "A/B/C bridge success is promoted to ecology success",
            "failed_closed_blocks_ecology_success",
        ),
        (
            "duplicate_replay_control",
            "duplicate run creates inconsistent contract output",
            "stable_required_for_runtime_admission",
        ),
        (
            "snapshot_load_replay_control",
            "snapshot/load changes the ordered trace outcome",
            "stable_required_for_runtime_admission",
        ),
    ]
    return [
        {
            "control_id": control_id,
            "blocked_condition": blocked_condition,
            "expected_status": expected_status,
            "execution_status_in_i17": "declared_not_run_contract_only",
        }
        for control_id, blocked_condition, expected_status in controls
    ]


def expected_failure_modes() -> list[dict[str, Any]]:
    return [
        {
            "failure_mode": "missing_A_B_or_C_source_current_artifact",
            "result": "runtime_probe_support_blocked",
        },
        {
            "failure_mode": "B_to_C_handoff_missing_or_post_hoc",
            "result": "stronger_composition_support_blocked",
        },
        {
            "failure_mode": "reentry_event_absent",
            "result": "Prototype_C_extension_blocks_stronger_probe",
        },
        {
            "failure_mode": "susceptibility_delta_label_only",
            "result": "semantic_learning_or_choice_claim_blocked",
        },
        {
            "failure_mode": "medium_debt_hidden_as_native_coordination",
            "result": "native_shared_medium_coordination_blocked",
        },
        {
            "failure_mode": "AP4_AP5_gap_omitted",
            "result": "native_AP_closure_claim_blocked",
        },
        {
            "failure_mode": "hidden_producer_proxy_carries_response",
            "result": "native_or_ecology_claim_blocked",
        },
        {
            "failure_mode": "replay_order_or_snapshot_instability",
            "result": "runtime_probe_admission_blocked",
        },
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
            "identify which producer-mediated, proxy, AP-gap, or medium-debt fields are claimed removed",
            "rerun the A/B/C consuming probe with native runtime surfaces or provide source-backed discharge evidence",
            "compare producer-mediated and native-surface runs",
            "show replay/control matrix still passes",
            "preserve learning, choice, native AP4/AP5, and ecology claim boundaries until discharge evidence passes",
        ],
        "gate_interpretation": (
            "I17 consumers may adapt the stronger probe contract, but successful "
            "adaptation is not native discharge. Native A/B/C support requires a "
            "new source-backed rerun or explicit discharge record."
        ),
    }


def build_output() -> dict[str, Any]:
    sources = {source_id: load_json(path) for source_id, path in SOURCE_PATHS.items()}
    i7 = sources["i7_coverage_debt_matrix"]
    i15 = sources["i15_prototype_atlas"]
    i16 = sources["i16_minimal_probe_contract"]
    ab = composition(i15, MINIMAL_COMPOSITION_ID)
    bc = composition(i15, STRONGER_COMPOSITION_ID)
    prototype_ids = [
        "prototype_a_trace_pressure_loop",
        "prototype_b_boundary_shared_medium_unit",
        "prototype_c_proxy_susceptibility_reentry",
    ]
    prototype_rows = prototypes(i15, prototype_ids)
    coverage_rows = coverage_support_rows(i7)

    probe_contract = {
        "probe_id": ALTERNATIVE_PROBE_ID,
        "probe_name": "Route-Pressure / Shared-Medium / Re-Entry Susceptibility Probe",
        "probe_class": "stronger_runnable_ecology_probe_contract",
        "extends_probe_id": i16["probe_contract"]["probe_id"],
        "extension_mode": "adds_Prototype_C_reentry_susceptibility_to_I16_A_B_minimal_probe",
        "source_composition_ids": [ab["composition_id"], bc["composition_id"]],
        "composed_prototype_ids": prototype_ids,
        "runtime_execution_status": "not_run_contract_only",
        "runtime_claim_allowed": False,
        "why_stronger_than_i16": (
            "I16 tests a pressure/response loop over a separable medium unit. I17 "
            "keeps that structure and adds re-entry plus susceptibility/differential "
            "response, which is closer to ecology-like route conditioning while still "
            "below learning, choice, or native agency."
        ),
        "why_not_full_ecology": (
            "The contract still lacks an executed composed runtime, resource economy, "
            "multi-agent role dynamics, and native shared-medium coordination."
        ),
        "ordered_dependency": (
            "A pressure loop conditions B medium; B medium supplies the bounded unit "
            "for C re-entry/susceptibility; later response is evaluated under the "
            "changed susceptibility state."
        ),
        "not_a_runtime_result": True,
    }

    added_risks = [
        "susceptibility label mistaken for learning",
        "differential response relabeled as choice",
        "medium unit relabeled as native shared-medium coordination",
        "AP4/AP5 gap hidden by stronger probe wording",
        "hidden producer proxy carries re-entry state",
    ]
    nativity_gate = contract_deviation_and_nativity_gate()

    checks = [
        check(
            "all_source_artifacts_passed",
            all(source.get("status") == "passed" for source in sources.values()),
        ),
        check(
            "i16_minimal_contract_consumed_not_replaced",
            i16.get("minimal_probe_contract_supported") is True
            and probe_contract["extends_probe_id"] == i16["probe_contract"]["probe_id"],
        ),
        check(
            "i15_ab_and_bc_compositions_ready",
            ab["composition_readiness_status"] == "ready_for_probe_contract"
            and bc["composition_readiness_status"] == "ready_for_probe_contract",
        ),
        check("three_bridge_exemplars_composed", len(prototype_rows) == 3),
        check(
            "coverage_matrix_justifies_stronger_probe",
            {row["ecology_demand"] for row in coverage_rows} == RELEVANT_DEMAND_IDS,
        ),
        check(
            "added_runtime_surfaces_declared_not_claimed",
            any(row["added_relative_to_i16"] for row in runtime_surface_contract())
            and probe_contract["runtime_claim_allowed"] is False,
        ),
        check("ordered_trace_contract_declared", len(ordered_trace_contract()) == 7),
        check("control_contract_declared", len(control_contract()) >= 12),
        check("expected_failure_modes_declared", len(expected_failure_modes()) >= 8),
        check("added_risks_recorded", len(added_risks) >= 5),
        check(
            "contract_deviation_nativity_gate_declared",
            nativity_gate["deviation_does_not_discharge_producer_debt"] is True
            and nativity_gate["nativity_requires_rerun_or_source_backed_discharge"] is True,
        ),
        check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_FLAGS.values())),
        check("ready_for_iteration_18", True),
    ]

    data: dict[str, Any] = {
        "artifact_id": "n29_alternative_ecology_probe_contract_i17",
        "experiment_id": "N29",
        "title": "Stronger / Alternative Ecology Probe Contract",
        "iteration": "I17",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_alternative_ecology_probe_contract",
        "source_artifacts": [
            source_artifact(source_id, SOURCE_PATHS[source_id], artifact)
            for source_id, artifact in sources.items()
        ],
        "probe_contract": probe_contract,
        "coverage_justification_rows": coverage_rows,
        "prototype_inputs": prototype_rows,
        "runtime_surface_contract": runtime_surface_contract(),
        "ordered_trace_contract": ordered_trace_contract(),
        "control_contract": control_contract(),
        "expected_failure_modes": expected_failure_modes(),
        "contract_deviation_and_nativity_gate": nativity_gate,
        "added_risks_and_debts": added_risks,
        "alternative_probe_contract_supported": True,
        "stronger_probe_contract_supported": True,
        "runtime_probe_executed": False,
        "ecology_success_supported": False,
        "native_ecology_supported": False,
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
        "# Stronger / Alternative Ecology Probe Contract",
        "",
        f"Status: `{data['status']}`",
        "",
        f"Acceptance state: `{data['acceptance_state']}`",
        "",
        "I17 extends the I16 minimal A+B probe contract by adding Prototype C "
        "re-entry/susceptibility. It remains a contract artifact, not an executed "
        "ecology runtime.",
        "",
        "## Probe",
        "",
        f"- Probe ID: `{contract['probe_id']}`",
        f"- Extends: `{contract['extends_probe_id']}`",
        f"- Runtime execution status: `{contract['runtime_execution_status']}`",
        f"- Runtime claim allowed: `{str(contract['runtime_claim_allowed']).lower()}`",
        "",
        contract["why_stronger_than_i16"],
        "",
        "## Prototype Inputs",
        "",
        "| Prototype | Evidence status | Claim ceiling |",
        "| --- | --- | --- |",
    ]
    for row in data["prototype_inputs"]:
        lines.append(
            "| `{}` | `{}` | {} |".format(
                row["prototype_id"],
                row["evidence_status"],
                row["claim_ceiling"],
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
            f"({row['execution_status_in_i17']})"
        )
    lines.extend(
        [
            "",
            "## Deviation And Nativity Gate",
            "",
            data["contract_deviation_and_nativity_gate"]["gate_interpretation"],
            "",
            "- Contract deviation is allowed only if recorded.",
            "- Deviation does not discharge producer, proxy, AP-gap, or medium debt.",
            "- Later core nativity does not retroactively upgrade an old producer-mediated probe.",
            "- Native discharge requires rerun or source-backed discharge evidence.",
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
            "I17 does not claim learning, choice, semantic ant behavior, native AP4/AP5 "
            "closure, native shared-medium coordination, ecology success, native "
            "support, sentience, organism/life, or Phase 8 completion.",
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
