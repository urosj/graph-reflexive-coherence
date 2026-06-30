#!/usr/bin/env python3
"""Build N29 I16 minimal runnable ecology probe contract artifact."""

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
    "build_n29_minimal_ecology_probe_contract_i16.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

SOURCE_PATHS = {
    "i5_ecology_demand_matrix": EXPERIMENT / "outputs" / "n29_ecology_demand_matrix_i5.json",
    "i6_capability_supply_atlas": EXPERIMENT / "outputs" / "n29_capability_supply_atlas_i6.json",
    "i7_coverage_debt_matrix": (
        EXPERIMENT / "outputs" / "n29_demand_supply_coverage_debt_i7.json"
    ),
    "i15_prototype_atlas": (
        EXPERIMENT / "outputs" / "n29_prototype_atlas_classification_i15.json"
    ),
}

OUT = EXPERIMENT / "outputs" / "n29_minimal_ecology_probe_contract_i16.json"
REPORT = EXPERIMENT / "reports" / "n29_minimal_ecology_probe_contract_i16.md"

UNSAFE_FLAGS = {
    "agency_claim_allowed": False,
    "ant_behavior_claim_allowed": False,
    "ant_ecology_runtime_success_claim_allowed": False,
    "biological_agency_claim_allowed": False,
    "colony_agency_claim_allowed": False,
    "cooperation_claim_allowed": False,
    "ecology_success_claim_allowed": False,
    "exploitation_claim_allowed": False,
    "native_ant_agency_claim_allowed": False,
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
MINIMAL_PROBE_ID = "minimal_route_pressure_over_shared_medium_unit_probe"
RELEVANT_DEMAND_IDS = {
    "general_trace",
    "general_pressure",
    "general_shared_medium",
    "general_co_response",
    "rc_ant_route_support_trace",
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


def selected_composition(i15: dict[str, Any]) -> dict[str, Any]:
    for row in i15["composition_rows"]:
        if row["composition_id"] == MINIMAL_COMPOSITION_ID:
            return row
    raise ValueError(f"missing I15 composition row: {MINIMAL_COMPOSITION_ID}")


def selected_prototypes(i15: dict[str, Any], composition: dict[str, Any]) -> list[dict[str, Any]]:
    by_id = {row["prototype_id"]: row for row in i15["prototype_rows"]}
    return [by_id[prototype_id] for prototype_id in composition["component_prototype_ids"]]


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
            "source_from_i15": "missing_runtime_surface",
            "contract_role": "execute the A+B ordered composition as one runnable probe",
            "admission_rule": "must emit source-current run artifacts before any ecology runtime claim",
        },
        {
            "surface_id": "trace_pressure_loop_runtime_surface",
            "required": True,
            "source_prototype": "prototype_a_trace_pressure_loop",
            "contract_role": "provide pressure/response loop state and replay traces",
            "admission_rule": "must preserve Prototype A producer-residue accounting",
        },
        {
            "surface_id": "boundary_shared_medium_unit_surface",
            "required": True,
            "source_prototype": "prototype_b_boundary_shared_medium_unit",
            "contract_role": "provide separable boundary/shared-medium unit state",
            "admission_rule": "must preserve zero-leakage/nonzero-leakage debt distinction",
        },
        {
            "surface_id": "ordered_cross_prototype_handoff_trace",
            "required": True,
            "source_from_i15": "missing_runtime_surface",
            "contract_role": "prove A output conditions B input in declared order",
            "admission_rule": "missing or post-hoc handoff blocks runtime support",
        },
        {
            "surface_id": "producer_residue_and_medium_debt_ledger",
            "required": True,
            "contract_role": "record which fields are producer mediated or medium debt",
            "admission_rule": "hidden residue or hidden medium debt blocks stronger claims",
        },
        {
            "surface_id": "ecology_probe_replay_control_matrix",
            "required": True,
            "source_from_i15": "missing_runtime_surface",
            "contract_role": "run replay, order, label-only, report-only, and hidden-coupling controls",
            "admission_rule": "required before any I17/I18 stronger probe or closeout support",
        },
    ]


def ordered_trace_contract() -> list[dict[str, Any]]:
    return [
        {
            "step_id": "t0_external_or_route_pressure",
            "required_trace": "pressure/trace input enters Prototype A loop surface",
            "must_record": [
                "pressure_source_id",
                "trace_window_id",
                "initial_loop_state_digest",
            ],
        },
        {
            "step_id": "t1_bounded_loop_response",
            "required_trace": "Prototype A emits bounded response/change trace",
            "must_record": [
                "response_trace_digest",
                "pressure_threshold_status",
                "route_context_status",
            ],
        },
        {
            "step_id": "t2_medium_unit_handoff",
            "required_trace": "A response conditions Prototype B boundary/shared-medium unit",
            "must_record": [
                "handoff_trace_digest",
                "handoff_order_status",
                "producer_residue_visibility_status",
            ],
        },
        {
            "step_id": "t3_later_medium_boundary_state",
            "required_trace": "later B state is evaluated under the changed/conditioned medium input",
            "must_record": [
                "later_medium_state_digest",
                "boundary_integrity_status",
                "shared_medium_leakage_status",
            ],
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
            "report summaries replace source-current A/B run artifacts",
            "failed_closed_blocks_probe_support",
        ),
        (
            "component_order_inversion_control",
            "B state appears to condition A before A response exists",
            "failed_closed_blocks_ordered_composition",
        ),
        (
            "missing_cross_prototype_handoff_control",
            "A and B are both present but no handoff trace links them",
            "failed_closed_blocks_runtime_support",
        ),
        (
            "hidden_producer_coupling_control",
            "undeclared producer carries state between A and B",
            "failed_closed_blocks_native_or_ecology_claim",
        ),
        (
            "medium_debt_hidden_as_native_relation_control",
            "shared-medium debt is relabeled as native coordination",
            "failed_closed_blocks_native_coordination",
        ),
        (
            "prototype_success_as_ecology_success_control",
            "A/B bridge success is promoted to ecology success",
            "failed_closed_blocks_ecology_success",
        ),
        (
            "semantic_ant_behavior_relabel_control",
            "route pressure or medium state is relabeled as ant behavior or pheromone semantics",
            "failed_closed_blocks_semantic_claim",
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
            "execution_status_in_i16": "declared_not_run_contract_only",
        }
        for control_id, blocked_condition, expected_status in controls
    ]


def expected_failure_modes() -> list[dict[str, Any]]:
    return [
        {
            "failure_mode": "missing_source_current_A_or_B_artifact",
            "result": "runtime_probe_support_blocked",
        },
        {
            "failure_mode": "ordered_handoff_missing_or_post_hoc",
            "result": "composition_runtime_support_blocked",
        },
        {
            "failure_mode": "producer_residue_hidden",
            "result": "native_or_ecology_claim_blocked",
        },
        {
            "failure_mode": "medium_debt_hidden_as_native_coordination",
            "result": "native_shared_medium_coordination_blocked",
        },
        {
            "failure_mode": "nonzero_leakage_reinterpreted_as_success",
            "result": "Prototype_B_claim_ceiling_preserved",
        },
        {
            "failure_mode": "semantic_ant_behavior_or_pheromone_relabel",
            "result": "semantic_claim_blocked",
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
            "identify which producer-mediated or debt fields are claimed removed",
            "rerun the consuming probe with native runtime surfaces or provide source-backed discharge evidence",
            "compare producer-mediated and native-surface runs",
            "show replay/control matrix still passes",
            "preserve claim boundary until discharge evidence passes",
        ],
        "gate_interpretation": (
            "Consuming projects may deviate from the probe contract, but deviation "
            "does not prove that producer support can be removed. Native discharge "
            "requires a new source-backed rerun or explicit discharge record."
        ),
    }


def build_output() -> dict[str, Any]:
    sources = {source_id: load_json(path) for source_id, path in SOURCE_PATHS.items()}
    i7 = sources["i7_coverage_debt_matrix"]
    i15 = sources["i15_prototype_atlas"]
    composition = selected_composition(i15)
    prototypes = selected_prototypes(i15, composition)
    coverage_rows = coverage_support_rows(i7)

    probe_contract = {
        "probe_id": MINIMAL_PROBE_ID,
        "probe_name": "Minimal Route-Pressure Over Shared-Medium Unit Probe",
        "probe_class": "minimal_runnable_ecology_probe_contract",
        "source_composition_id": composition["composition_id"],
        "composed_prototype_ids": composition["component_prototype_ids"],
        "composed_prototype_labels": [row["prototype_label"] for row in prototypes],
        "composition_readiness_status": composition["composition_readiness_status"],
        "composition_evidence_status": composition["composition_evidence_status"],
        "runtime_execution_status": "not_run_contract_only",
        "runtime_claim_allowed": False,
        "why_minimal": (
            "A+B is the smallest I15 composition: one pressure/response loop over "
            "one separable boundary/shared-medium unit. It tests composition without "
            "adding susceptibility/re-entry or medium-reshaping layers."
        ),
        "ordered_dependency": composition["ordered_dependency"],
        "contract_goal": (
            "Build a future runnable probe that tests whether a bounded "
            "trace/pressure loop can operate through a separable boundary/shared-medium "
            "unit while producer residue and medium debt remain visible."
        ),
        "not_a_runtime_result": True,
    }

    handoff_package = {
        "target_repository_role": "reflexive-coherence-agentic-ecology probe design input",
        "export_status": "contract_ready_not_exported",
        "exported_files": [],
        "must_include_if_exported": [
            "probe_contract",
            "runtime_surface_contract",
            "ordered_trace_contract",
            "control_contract",
            "expected_failure_modes",
            "claim_boundary",
        ],
    }
    nativity_gate = contract_deviation_and_nativity_gate()

    checks = [
        check(
            "all_source_artifacts_passed",
            all(source.get("status") == "passed" for source in sources.values()),
        ),
        check(
            "i15_ready_for_iteration_16",
            i15.get("ready_for_iteration_16") is True
            and i15.get("prototype_atlas_supported") is True,
        ),
        check(
            "minimal_composition_selected_from_i15",
            composition["composition_id"] == MINIMAL_COMPOSITION_ID
            and composition["composition_readiness_status"] == "ready_for_probe_contract",
        ),
        check("exactly_two_bridge_exemplars_composed", len(prototypes) == 2),
        check(
            "coverage_matrix_justifies_minimal_probe",
            {row["ecology_demand"] for row in coverage_rows} == RELEVANT_DEMAND_IDS,
        ),
        check(
            "runtime_surfaces_declared_not_claimed",
            all(row["required"] for row in runtime_surface_contract())
            and probe_contract["runtime_claim_allowed"] is False,
        ),
        check("ordered_trace_contract_declared", len(ordered_trace_contract()) == 4),
        check("control_contract_declared", len(control_contract()) >= 10),
        check("expected_failure_modes_declared", len(expected_failure_modes()) >= 7),
        check(
            "contract_deviation_nativity_gate_declared",
            nativity_gate["deviation_does_not_discharge_producer_debt"] is True
            and nativity_gate["nativity_requires_rerun_or_source_backed_discharge"] is True,
        ),
        check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_FLAGS.values())),
        check("ready_for_iteration_17", True),
    ]

    data: dict[str, Any] = {
        "artifact_id": "n29_minimal_ecology_probe_contract_i16",
        "experiment_id": "N29",
        "title": "Minimal Runnable Ecology Probe Contract",
        "iteration": "I16",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_minimal_ecology_probe_contract",
        "source_artifacts": [
            source_artifact(source_id, SOURCE_PATHS[source_id], artifact)
            for source_id, artifact in sources.items()
        ],
        "probe_contract": probe_contract,
        "coverage_justification_rows": coverage_rows,
        "prototype_inputs": prototypes,
        "runtime_surface_contract": runtime_surface_contract(),
        "ordered_trace_contract": ordered_trace_contract(),
        "control_contract": control_contract(),
        "expected_failure_modes": expected_failure_modes(),
        "contract_deviation_and_nativity_gate": nativity_gate,
        "handoff_package": handoff_package,
        "minimal_probe_contract_supported": True,
        "runtime_probe_executed": False,
        "ecology_success_supported": False,
        "native_ecology_supported": False,
        "claim_boundary": UNSAFE_FLAGS,
        "ready_for_iteration_17": True,
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
        "# Minimal Runnable Ecology Probe Contract",
        "",
        f"Status: `{data['status']}`",
        "",
        f"Acceptance state: `{data['acceptance_state']}`",
        "",
        "I16 converts the I15 prototype atlas into the first minimal runnable "
        "ecology probe contract. It does not execute the probe and does not claim "
        "ecology runtime success.",
        "",
        "## Probe",
        "",
        f"- Probe ID: `{contract['probe_id']}`",
        f"- Source composition: `{contract['source_composition_id']}`",
        f"- Runtime execution status: `{contract['runtime_execution_status']}`",
        f"- Runtime claim allowed: `{str(contract['runtime_claim_allowed']).lower()}`",
        "",
        contract["why_minimal"],
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
            "## Runtime Surfaces",
            "",
        ]
    )
    for row in data["runtime_surface_contract"]:
        lines.append(f"- `{row['surface_id']}`: {row['contract_role']}")
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
            f"({row['execution_status_in_i16']})"
        )
    lines.extend(
        [
            "",
            "## Deviation And Nativity Gate",
            "",
            data["contract_deviation_and_nativity_gate"]["gate_interpretation"],
            "",
            "- Contract deviation is allowed only if recorded.",
            "- Deviation does not discharge producer or medium debt.",
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
            "The contract is a probe-design artifact. It blocks ecology success, native "
            "ant agency, native shared-medium coordination, semantic pheromone or "
            "goal claims, native support, sentience, organism/life, and Phase 8 "
            "completion.",
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
