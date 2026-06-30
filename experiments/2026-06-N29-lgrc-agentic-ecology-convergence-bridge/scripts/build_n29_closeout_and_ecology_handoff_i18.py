#!/usr/bin/env python3
"""Build N29 I18 closeout and agentic-ecology handoff artifact."""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-30T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N29-lgrc-agentic-ecology-convergence-bridge"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/scripts/"
    "build_n29_closeout_and_ecology_handoff_i18.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

SOURCE_PATHS = {
    "i5_ecology_demand_matrix": EXPERIMENT / "outputs" / "n29_ecology_demand_matrix_i5.json",
    "i6_capability_supply_atlas": (
        EXPERIMENT / "outputs" / "n29_capability_supply_atlas_i6.json"
    ),
    "i7_demand_supply_coverage_debt": (
        EXPERIMENT / "outputs" / "n29_demand_supply_coverage_debt_i7.json"
    ),
    "i8_bridge_motif_library": EXPERIMENT / "outputs" / "n29_bridge_motif_library_i8.json",
    "i9_motif_relabel_nulls": EXPERIMENT / "outputs" / "n29_motif_relabel_nulls_i9.json",
    "i10_prototype_admission_schema": (
        EXPERIMENT / "outputs" / "n29_prototype_admission_schema_i10.json"
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
    "i17a_full_bridge_probe_contract": (
        EXPERIMENT / "outputs" / "n29_full_bridge_probe_contract_i17a.json"
    ),
}

OUT = EXPERIMENT / "outputs" / "n29_closeout_and_ecology_handoff_i18.json"
REPORT = EXPERIMENT / "reports" / "n29_closeout_and_ecology_handoff_i18.md"

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
    "native_colony_agency_claim_allowed": False,
    "native_composition_claim_allowed": False,
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


def check(check_id: str, passed: bool, details: Any | None = None) -> dict[str, Any]:
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


def changed_src_paths() -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", "--", "src"],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        return [f"git_diff_failed:{result.stderr.strip()}"]
    return [line for line in result.stdout.splitlines() if line.strip()]


def output_readiness(sources: dict[str, dict[str, Any]]) -> dict[str, Any]:
    i7 = sources["i7_demand_supply_coverage_debt"]
    i15 = sources["i15_prototype_atlas"]
    i16 = sources["i16_minimal_probe_contract"]
    i17 = sources["i17_alternative_probe_contract"]
    i17a = sources["i17a_full_bridge_probe_contract"]
    return {
        "phase_a_to_b_boundary_supported": True,
        "demand_matrix_supported": sources["i5_ecology_demand_matrix"]["status"] == "passed",
        "capability_supply_atlas_supported": sources["i6_capability_supply_atlas"][
            "status"
        ]
        == "passed",
        "coverage_debt_matrix_supported": i7["coverage_matrix_supported"] is True,
        "bridge_motif_library_supported": sources["i8_bridge_motif_library"][
            "bridge_motif_library_opened"
        ]
        is True,
        "active_nulls_supported": sources["i9_motif_relabel_nulls"]["status"] == "passed",
        "prototype_admission_schema_supported": sources["i10_prototype_admission_schema"][
            "status"
        ]
        == "passed",
        "prototype_atlas_supported": i15["prototype_atlas_supported"] is True,
        "minimal_probe_contract_supported": i16["minimal_probe_contract_supported"] is True,
        "alternative_probe_contract_supported": i17[
            "alternative_probe_contract_supported"
        ]
        is True,
        "full_bridge_probe_contract_supported": i17a[
            "full_bridge_probe_contract_supported"
        ]
        is True,
        "runtime_probe_executed": False,
        "ecology_success_supported": False,
        "native_ecology_supported": False,
        "native_composition_supported": False,
    }


def bridge_ladder_classification() -> list[dict[str, Any]]:
    return [
        {
            "bridge_ladder_rung": "EB0_source_inventory_only",
            "status": "passed",
            "source_iterations": ["I1", "I2", "I3", "I4"],
            "meaning": "ecology demand, method constraints, capability source inventory, and schema boundary recorded",
        },
        {
            "bridge_ladder_rung": "EB1_normalized_demand_supply_matrix",
            "status": "passed",
            "source_iterations": ["I5", "I6", "I7"],
            "meaning": "ecology demands and LGRC/GRC supplies joined with explicit coverage/debt rows",
        },
        {
            "bridge_ladder_rung": "EB2_bridge_motif_library_with_controls",
            "status": "passed",
            "source_iterations": ["I8", "I9"],
            "meaning": "motif library and relabel/null controls are claim-clean",
        },
        {
            "bridge_ladder_rung": "EB3_prototype_admission_schema",
            "status": "passed",
            "source_iterations": ["I10"],
            "meaning": "runtime prototype admission requirements are frozen",
        },
        {
            "bridge_ladder_rung": "EB4_runtime_bridge_prototypes_supported",
            "status": "passed",
            "source_iterations": ["I11", "I12", "I13", "I14"],
            "meaning": "four prototype families have runtime or synthesis evidence with controls and debt",
        },
        {
            "bridge_ladder_rung": "EB5_prototype_atlas_and_composition_map_supported",
            "status": "passed",
            "source_iterations": ["I15"],
            "meaning": "prototype atlas classifies bridge exemplars and composition seeds without ecology-success claims",
        },
        {
            "bridge_ladder_rung": "EB6_first_ecology_probe_contracts_and_handoff_supported",
            "status": "passed",
            "source_iterations": ["I16", "I17", "I17-A", "I18"],
            "meaning": "minimal, stronger, and full A/B/C/D probe contracts are ready for outbound ecology work",
        },
    ]


def n29_closeout_ladder_classification() -> list[dict[str, Any]]:
    return [
        {
            "n29_closeout_ladder_rung": "N29-C0_initialized_bridge_only",
            "status": "passed",
            "meaning": "experiment structure and source scope established",
        },
        {
            "n29_closeout_ladder_rung": "N29-C1_ecology_demands_and_method_constraints_supported",
            "status": "passed",
            "meaning": "ecology-side requirements and agency-of-becoming constraints normalized",
        },
        {
            "n29_closeout_ladder_rung": "N29-C2_capability_supply_and_coverage_supported",
            "status": "passed",
            "meaning": "N05-N28 supply and debt matrix completed from source artifacts",
        },
        {
            "n29_closeout_ladder_rung": "N29-C3_bridge_motif_library_supported",
            "status": "passed",
            "meaning": "motifs and relabel nulls completed",
        },
        {
            "n29_closeout_ladder_rung": "N29-C4_runtime_prototype_families_supported",
            "status": "passed",
            "meaning": "prototype A-D family evidence and controls admitted",
        },
        {
            "n29_closeout_ladder_rung": "N29-C5_prototype_atlas_and_probe_contracts_supported",
            "status": "passed",
            "meaning": "prototype atlas plus I16/I17/I17-A contracts supported",
        },
        {
            "n29_closeout_ladder_rung": "N29-C6_agentic_ecology_probe_handoff_complete",
            "status": "passed",
            "meaning": "outbound ecology and inbound N30+ handoffs are recorded with claim ceilings",
        },
    ]


def deviation_nativity_closeout(sources: dict[str, dict[str, Any]]) -> dict[str, Any]:
    contract_sources = [
        sources["i16_minimal_probe_contract"],
        sources["i17_alternative_probe_contract"],
        sources["i17a_full_bridge_probe_contract"],
    ]
    gate_rows = []
    for source in contract_sources:
        gate = source["contract_deviation_and_nativity_gate"]
        gate_rows.append(
            {
                "source_artifact": source["artifact_id"],
                "output_digest": source["output_digest"],
                "contract_deviation_allowed": gate["contract_deviation_allowed"],
                "deviation_does_not_discharge_producer_debt": gate[
                    "deviation_does_not_discharge_producer_debt"
                ],
                "contract_conformance_does_not_imply_nativity": gate[
                    "contract_conformance_does_not_imply_nativity"
                ],
                "later_core_nativity_does_not_retroactively_upgrade_old_probe": gate[
                    "later_core_nativity_does_not_retroactively_upgrade_old_probe"
                ],
                "nativity_requires_rerun_or_source_backed_discharge": gate[
                    "nativity_requires_rerun_or_source_backed_discharge"
                ],
            }
        )
    return {
        "gate_status": "preserved_across_phase_d_contracts",
        "deviation_allowed": True,
        "deviation_requires_reason_scope_and_affected_surfaces": True,
        "deviation_does_not_discharge_debt": True,
        "contract_conformance_does_not_imply_nativity": True,
        "later_core_nativity_does_not_retroactively_upgrade_old_probe": True,
        "native_discharge_requires": [
            "new native runtime run against native surface",
            "or source-backed discharge record proving producer or medium debt no longer carries result",
        ],
        "gate_rows": gate_rows,
    }


def outbound_agentic_ecology_handoff(sources: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        "handoff_id": "n29_to_reflexive_coherence_agentic_ecology",
        "handoff_status": "supported",
        "target_repository": "reflexive-coherence-agentic-ecology",
        "may_consume_as": [
            "claim-clean ecology demand model",
            "N05-N28 capability/debt atlas",
            "bridge motif library",
            "prototype atlas",
            "minimal A+B probe contract",
            "stronger A+B+C probe contract",
            "full A+B+C+D bridge probe contract",
        ],
        "must_not_consume_as": [
            "executed ant ecology runtime",
            "native ant agency",
            "native colony agency",
            "semantic pheromone or goal evidence",
            "resource economy evidence",
            "cooperation or exploitation evidence",
            "native support or Phase 8 completion",
        ],
        "first_probe_contracts": [
            {
                "contract_id": sources["i16_minimal_probe_contract"]["probe_contract"]["probe_id"],
                "source_artifact": sources["i16_minimal_probe_contract"]["artifact_id"],
                "output_digest": sources["i16_minimal_probe_contract"]["output_digest"],
                "role": "minimal runnable ecology probe contract",
            },
            {
                "contract_id": sources["i17_alternative_probe_contract"]["probe_contract"][
                    "probe_id"
                ],
                "source_artifact": sources["i17_alternative_probe_contract"]["artifact_id"],
                "output_digest": sources["i17_alternative_probe_contract"]["output_digest"],
                "role": "stronger A+B+C probe contract",
            },
            {
                "contract_id": sources["i17a_full_bridge_probe_contract"]["probe_contract"][
                    "probe_id"
                ],
                "source_artifact": sources["i17a_full_bridge_probe_contract"]["artifact_id"],
                "output_digest": sources["i17a_full_bridge_probe_contract"]["output_digest"],
                "role": "full A/B/C/D bridge probe contract",
            },
        ],
        "required_consuming_project_rules": [
            "record any deviation from N29 contracts with reason, scope, and affected surfaces",
            "preserve producer residue and medium debt unless discharged by source-backed evidence",
            "do not treat contract conformance as native ecology",
            "run replay/control matrix before claiming ecology probe support",
            "keep semantic agency, cooperation, exploitation, and ant-behavior labels blocked until directly evidenced",
        ],
    }


def inbound_n30_handoff() -> dict[str, Any]:
    return {
        "handoff_id": "n29_to_n30_plus_core_primitives",
        "handoff_status": "supported",
        "purpose": "continue core LGRC/GRC primitive and agency-component work in this repository",
        "may_consume_as": [
            "catalogue of missing native surfaces",
            "naturalization target list",
            "prototype-composition debt map",
            "candidate primitive/component roadmap",
        ],
        "must_not_consume_as": [
            "proof that ecology runtime exists",
            "proof that producer-mediated compositions are native",
            "proof of semantic agency or life",
        ],
        "candidate_n30_plus_experiment_targets": [
            {
                "target_id": "native_multi_component_medium_coupling",
                "source_debt": "Prototype B/D medium and composition debt",
                "why_needed": "replace producer-mediated medium handoffs with source-current native coupling",
            },
            {
                "target_id": "native_cross_prototype_state_handoff",
                "source_debt": "I16/I17/I17-A composed runtime harness debt",
                "why_needed": "let prototype outputs become native inputs without external bridge assembly",
            },
            {
                "target_id": "native_resource_capacity_semantics_without_semantic_labels",
                "source_debt": "N28/N29 generative/extractive resource-economy blocker",
                "why_needed": "test capacity exchange without importing goal/reward/cooperation language",
            },
            {
                "target_id": "producer_residue_discharge_tests",
                "source_debt": "Phase D deviation/nativity gate",
                "why_needed": "prove when a producer-mediated bridge can be rerun or discharged as native",
            },
        ],
    }


def unresolved_debt_by_direction() -> list[dict[str, Any]]:
    return [
        {
            "debt_id": "composed_ecology_runtime_harness_missing",
            "handoff_direction": "outbound_agentic_ecology",
            "status": "open",
            "blocks": ["ecology_success_supported", "native_ecology_supported"],
        },
        {
            "debt_id": "producer_mediated_cross_prototype_handoff",
            "handoff_direction": "both",
            "status": "open",
            "blocks": ["native_composition_supported", "native_support_supported"],
        },
        {
            "debt_id": "medium_debt_and_nonzero_leakage_policy",
            "handoff_direction": "both",
            "status": "open",
            "blocks": ["native_shared_medium_coordination_supported"],
        },
        {
            "debt_id": "ap4_ap5_gap_propagation",
            "handoff_direction": "inbound_n30_plus",
            "status": "open",
            "blocks": ["native_route_selection_or_proxy_target_closure"],
        },
        {
            "debt_id": "resource_economy_cooperation_exploitation_semantics",
            "handoff_direction": "outbound_agentic_ecology",
            "status": "open",
            "blocks": ["resource_economy_supported", "cooperation_or_exploitation_supported"],
        },
        {
            "debt_id": "deviation_nativity_discharge",
            "handoff_direction": "both",
            "status": "open",
            "blocks": ["retroactive_native_upgrade", "producer_removal_without_rerun"],
        },
    ]


def build_output() -> dict[str, Any]:
    sources = {source_id: load_json(path) for source_id, path in SOURCE_PATHS.items()}
    source_artifacts = [
        source_artifact(source_id, path, sources[source_id])
        for source_id, path in SOURCE_PATHS.items()
    ]
    src_paths = changed_src_paths()
    readiness = output_readiness(sources)
    deviation_gate = deviation_nativity_closeout(sources)
    outbound = outbound_agentic_ecology_handoff(sources)
    inbound = inbound_n30_handoff()
    output: dict[str, Any] = {
        "artifact_id": "n29_closeout_and_ecology_handoff_i18",
        "title": "N29 Iteration 18 - Closeout And Agentic Ecology Handoff",
        "experiment_id": "N29",
        "iteration": "I18",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "source_artifacts": source_artifacts,
        "source_output_digest_map": {
            source_id: sources[source_id].get("output_digest", "not_recorded")
            for source_id in SOURCE_PATHS
        },
        "closeout_scope": "bridge_and_probe_contract_handoff_only",
        "bridge_ladder_rung": "EB6_first_ecology_probe_contracts_and_handoff_supported",
        "n29_closeout_ladder_rung": "N29-C6_agentic_ecology_probe_handoff_complete",
        "bridge_ladder_classification": bridge_ladder_classification(),
        "n29_closeout_ladder_classification": n29_closeout_ladder_classification(),
        "output_readiness": readiness,
        "n29_closeout_supported": True,
        "outbound_agentic_ecology_handoff_supported": True,
        "inbound_n30_plus_continuation_handoff_supported": True,
        "ready_for_reflexive_coherence_agentic_ecology": True,
        "ready_for_n30_plus_core_primitive_work": True,
        "runtime_probe_executed": False,
        "ecology_success_supported": False,
        "native_ecology_supported": False,
        "native_ant_agency_opened": False,
        "native_colony_agency_opened": False,
        "biological_agency_opened": False,
        "organism_life_opened": False,
        "sentience_opened": False,
        "phase8_completion_opened": False,
        "native_support_opened": False,
        "resource_economy_supported": False,
        "cooperation_or_exploitation_supported": False,
        "closed_native_circulation_supported": False,
        "claim_ceiling": (
            "claim-clean prototype atlas and source-backed bridge composition map "
            "with first agentic-ecology probe contracts; not executed ecology "
            "runtime, native ecology, agency, sentience, native support, resource "
            "economy, cooperation, exploitation, or Phase 8 completion"
        ),
        "claim_boundary": {
            "unsafe_claim_flags": UNSAFE_FLAGS,
            "all_unsafe_claim_flags_false": all(flag is False for flag in UNSAFE_FLAGS.values()),
        },
        "contract_deviation_and_nativity_closeout": deviation_gate,
        "outbound_agentic_ecology_handoff": outbound,
        "inbound_n30_plus_continuation_handoff": inbound,
        "unresolved_debt_by_handoff_direction": unresolved_debt_by_direction(),
        "src_diff_empty": src_paths == [],
        "src_diff_paths": src_paths,
    }
    output["checks"] = [
        check(
            "all_required_source_artifacts_passed",
            all(item["status"] == "passed" for item in source_artifacts),
            {item["source_id"]: item["status"] for item in source_artifacts},
        ),
        check(
            "prototype_atlas_ready_for_contracts",
            sources["i15_prototype_atlas"]["prototype_atlas_supported"] is True
            and sources["i15_prototype_atlas"]["ready_for_iteration_16"] is True,
            {
                "prototype_atlas_supported": sources["i15_prototype_atlas"][
                    "prototype_atlas_supported"
                ],
                "ready_for_iteration_16": sources["i15_prototype_atlas"][
                    "ready_for_iteration_16"
                ],
            },
        ),
        check(
            "phase_d_contracts_supported",
            readiness["minimal_probe_contract_supported"]
            and readiness["alternative_probe_contract_supported"]
            and readiness["full_bridge_probe_contract_supported"],
            readiness,
        ),
        check(
            "contracts_remain_non_runtime",
            output["runtime_probe_executed"] is False
            and output["ecology_success_supported"] is False
            and output["native_ecology_supported"] is False,
            {
                "runtime_probe_executed": output["runtime_probe_executed"],
                "ecology_success_supported": output["ecology_success_supported"],
                "native_ecology_supported": output["native_ecology_supported"],
            },
        ),
        check(
            "deviation_nativity_gate_preserved",
            deviation_gate["gate_status"] == "preserved_across_phase_d_contracts"
            and all(
                row["deviation_does_not_discharge_producer_debt"]
                and row["contract_conformance_does_not_imply_nativity"]
                and row["later_core_nativity_does_not_retroactively_upgrade_old_probe"]
                and row["nativity_requires_rerun_or_source_backed_discharge"]
                for row in deviation_gate["gate_rows"]
            ),
            deviation_gate["gate_rows"],
        ),
        check(
            "outbound_and_inbound_handoffs_supported",
            output["outbound_agentic_ecology_handoff_supported"]
            and output["inbound_n30_plus_continuation_handoff_supported"],
            {
                "outbound": outbound["handoff_status"],
                "inbound": inbound["handoff_status"],
            },
        ),
        check(
            "unsafe_claim_flags_false",
            output["claim_boundary"]["all_unsafe_claim_flags_false"],
            output["claim_boundary"]["unsafe_claim_flags"],
        ),
        check(
            "source_digests_present",
            all(item["output_digest"] != "not_recorded" for item in source_artifacts),
            output["source_output_digest_map"],
        ),
        check("src_diff_empty", output["src_diff_empty"], output["src_diff_paths"]),
        check("no_absolute_paths_in_records", no_absolute_paths(output), None),
    ]
    output["failed_checks"] = [row["check_id"] for row in output["checks"] if not row["passed"]]
    output["status"] = "passed" if not output["failed_checks"] else "failed"
    output["acceptance_state"] = (
        "accepted_agentic_ecology_convergence_bridge_handoff"
        if output["status"] == "passed"
        else "blocked_agentic_ecology_convergence_bridge_handoff"
    )
    return finalize(output)


def write_report(data: dict[str, Any]) -> None:
    checks = "\n".join(
        f"| `{row['check_id']}` | `{str(row['passed']).lower()}` |"
        for row in data["checks"]
    )
    contracts = "\n".join(
        f"- `{row['contract_id']}` from `{row['source_artifact']}` "
        f"({row['role']})"
        for row in data["outbound_agentic_ecology_handoff"]["first_probe_contracts"]
    )
    debts = "\n".join(
        f"- `{row['debt_id']}`: {row['status']} ({row['handoff_direction']})"
        for row in data["unresolved_debt_by_handoff_direction"]
    )
    n30_targets = "\n".join(
        f"- `{row['target_id']}`: {row['why_needed']}"
        for row in data["inbound_n30_plus_continuation_handoff"][
            "candidate_n30_plus_experiment_targets"
        ]
    )
    REPORT.write_text(
        f"""# N29 Iteration 18 - Closeout And Agentic Ecology Handoff

Status: `{data['status']}`

Acceptance state: `{data['acceptance_state']}`

```text
bridge_ladder_rung = {data['bridge_ladder_rung']}
n29_closeout_ladder_rung = {data['n29_closeout_ladder_rung']}
outbound_agentic_ecology_handoff_supported = {str(data['outbound_agentic_ecology_handoff_supported']).lower()}
inbound_n30_plus_continuation_handoff_supported = {str(data['inbound_n30_plus_continuation_handoff_supported']).lower()}
runtime_probe_executed = {str(data['runtime_probe_executed']).lower()}
ecology_success_supported = {str(data['ecology_success_supported']).lower()}
native_ecology_supported = {str(data['native_ecology_supported']).lower()}
phase8_completion_opened = {str(data['phase8_completion_opened']).lower()}
src_diff_empty = {str(data['src_diff_empty']).lower()}
```

## Closeout

N29 closes as a bridge experiment. It supports a claim-clean prototype atlas,
source-backed bridge composition map, and first ecology probe contracts. It
does not support executed ecology runtime, native ant agency, native colony
agency, semantic cooperation/exploitation, resource economy, organism/life,
sentience, native support, or Phase 8 completion.

## Probe Contracts

{contracts}

## Deviation And Nativity Gate

The Phase D contracts allow consuming-project deviation only as recorded
scope. Deviation or contract conformance does not discharge producer residue,
medium debt, AP4/AP5 gaps, or Prototype D composition debt. Later native LGRC
support does not retroactively upgrade old producer-mediated contract rows;
native discharge requires a native rerun or source-backed discharge record.

## Outbound Handoff

The outbound handoff to `reflexive-coherence-agentic-ecology` is supported as
probe-contract input. It must not be consumed as executed ant ecology runtime or
native ecology success.

## Inbound Handoff

N30+ work remains open in this repository for primitive and agency-component
naturalization. Candidate directions:

{n30_targets}

## Open Debt

{debts}

## Checks

| Check | Passed |
| --- | --- |
{checks}

Output digest: `{data['output_digest']}`
""",
        encoding="utf-8",
    )


def main() -> None:
    output = build_output()
    write_json(OUT, output)
    write_report(output)


if __name__ == "__main__":
    main()
