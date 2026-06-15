#!/usr/bin/env python3
"""Build N12 Iteration 8 closeout and handoff artifact."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-06-N12-lgrc-native-naturalization-and-producer-dissolution"
)
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"

ITERATION_1_OUTPUT = OUTPUTS / "n12_native_naturalization_inventory.json"
ITERATION_1_REPORT = REPORTS / "n12_native_naturalization_inventory.md"
ITERATION_2_OUTPUT = OUTPUTS / "n12_naturalization_schema_v1.json"
ITERATION_2_REPORT = REPORTS / "n12_naturalization_schema_v1.md"
ITERATION_3_OUTPUT = OUTPUTS / "n12_route_conductance_memory_candidate.json"
ITERATION_3_REPORT = REPORTS / "n12_route_conductance_memory_candidate.md"
ITERATION_4_OUTPUT = OUTPUTS / "n12_response_magnitude_candidate.json"
ITERATION_4_REPORT = REPORTS / "n12_response_magnitude_candidate.md"
ITERATION_5_OUTPUT = OUTPUTS / "n12_identity_acceptance_boundary.json"
ITERATION_5_REPORT = REPORTS / "n12_identity_acceptance_boundary.md"
ITERATION_6_OUTPUT = OUTPUTS / "n12_agentic_like_integration_boundary.json"
ITERATION_6_REPORT = REPORTS / "n12_agentic_like_integration_boundary.md"
ITERATION_7_OUTPUT = OUTPUTS / "n12_phase8_readiness_matrix.json"
ITERATION_7_REPORT = REPORTS / "n12_phase8_readiness_matrix.md"

N12_ROADMAP = ROOT / "experiments" / "N12-N18-LGRC-AgencyPrerequisitesRoadmap.md"
N12_HANDOFF = ROOT / "experiments" / "N12-N18-LGRC-AgencyPrerequisitesHandoff.md"

OUTPUT_PATH = OUTPUTS / "n12_closeout_and_handoff.json"
REPORT_PATH = REPORTS / "n12_closeout_and_handoff.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N12-lgrc-native-naturalization-and-producer-dissolution/"
    "scripts/build_n12_closeout_and_handoff.py"
)
GENERATED_AT = "2026-06-15T00:00:00+00:00"

CLAIM_FLAGS_FORCED_FALSE = {
    "agency_claim_allowed": False,
    "intention_claim_allowed": False,
    "semantic_goal_ownership_claim_allowed": False,
    "semantic_goal_understanding_claim_allowed": False,
    "identity_acceptance_claim_allowed": False,
    "runtime_identity_acceptance_claim_allowed": False,
    "rc_identity_collapse_claim_allowed": False,
    "aco_like_claim_allowed": False,
    "ant_colony_claim_allowed": False,
    "biological_claim_allowed": False,
    "personhood_claim_allowed": False,
    "unrestricted_identity_claim_allowed": False,
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


def source_report(path: Path) -> dict[str, Any]:
    return {"path": rel(path), "sha256": digest_file(path)}


def all_claim_flags_false(flags: dict[str, Any]) -> bool:
    return all(value is False for value in flags.values())


def inventory_row_by_native_gap(inventory: dict[str, Any], native_gap: str) -> dict[str, Any]:
    for row in inventory["n12_inventory_rows"]:
        if row["native_gap"] == native_gap:
            return row
    raise ValueError(f"Inventory native gap not found: {native_gap}")


def build_final_classification_rows(
    inventory: dict[str, Any],
    route: dict[str, Any],
    response: dict[str, Any],
    identity: dict[str, Any],
    integration: dict[str, Any],
) -> list[dict[str, Any]]:
    route_context = inventory_row_by_native_gap(
        inventory, "native_route_context_contract_hardening_if_scope_extends"
    )
    route_row = route["route_conductance_memory_candidate"]
    response_row = response["response_magnitude_candidate"]
    identity_row = identity["identity_acceptance_boundary"]
    integration_row = integration["agentic_like_integration_boundary"]
    return [
        {
            "seed_row_id": route_context["row_id"],
            "mechanism_name": route_context["mechanism_name"],
            "native_gap": route_context["native_gap"],
            "final_primary_disposition": "scaffold",
            "final_nat_level": "NAT2",
            "phase8_ready": False,
            "phase8_ready_contract": False,
            "deferred": False,
            "source_artifact": route_context["source_artifact"],
            "rationale": (
                "Inherited route context support remains selection-only. Contract "
                "hardening is experiment-local unless future scope extends beyond "
                "native route arbitration selection."
            ),
            "blockers": [
                "scope_extends_beyond_selection_not_opened",
                "no_phase8_route_context_hardening_requested",
            ],
        },
        {
            "seed_row_id": route_row["source_gap_rows"][0],
            "mechanism_name": route_row["native_policy_name"],
            "native_gap": route_row["native_gap"],
            "final_primary_disposition": route_row["primary_disposition"],
            "final_nat_level": route_row["nat_level"],
            "phase8_ready": route_row["phase8_ready"],
            "phase8_ready_contract": True,
            "deferred": False,
            "source_artifact": rel(ITERATION_3_OUTPUT),
            "rationale": (
                "Route conductance memory has explicit NAT4 gates, default-off "
                "flags, idempotency, telemetry, budget surfaces, replay, controls, "
                "and mutation boundary."
            ),
            "blockers": [],
        },
        {
            "seed_row_id": response_row["source_gap_rows"][0],
            "mechanism_name": response_row["native_policy_name"],
            "native_gap": response_row["native_gap"],
            "final_primary_disposition": response_row["primary_disposition"],
            "final_nat_level": response_row["nat_level"],
            "phase8_ready": response_row["phase8_ready"],
            "phase8_ready_contract": True,
            "deferred": False,
            "source_artifact": rel(ITERATION_4_OUTPUT),
            "rationale": (
                "Bounded/envelope-gated response magnitude has explicit NAT4 gates, "
                "default-off flags, idempotency, telemetry, trend/stability fields, "
                "budget surfaces, replay, controls, and mutation boundary."
            ),
            "blockers": [],
        },
        {
            "seed_row_id": identity_row["source_gap_rows"][0],
            "mechanism_name": identity_row["native_policy_name"],
            "native_gap": identity_row["native_gap"],
            "final_primary_disposition": identity_row["primary_disposition"],
            "final_nat_level": identity_row["nat_level"],
            "phase8_ready": identity_row["phase8_ready"],
            "phase8_ready_contract": False,
            "deferred": True,
            "source_artifact": rel(ITERATION_5_OUTPUT),
            "rationale": (
                "Support survival and restoration evidence is source-backed, but "
                "identity acceptance, runtime acceptance, and RC identity collapse "
                "semantics are not formalized."
            ),
            "blockers": identity_row["missing_gates"],
        },
        {
            "seed_row_id": integration_row["source_gap_rows"][0],
            "mechanism_name": integration_row["native_policy_name"],
            "native_gap": integration_row["native_gap"],
            "final_primary_disposition": integration_row["primary_disposition"],
            "final_nat_level": integration_row["nat_level"],
            "phase8_ready": integration_row["phase8_ready"],
            "phase8_ready_contract": False,
            "deferred": True,
            "source_artifact": rel(ITERATION_6_OUTPUT),
            "rationale": (
                "Native agentic-like integration is a meta-policy gap. NAT4 "
                "component candidates and artifact-only GALI7 replay do not "
                "constitute native integration support."
            ),
            "blockers": integration_row["missing_gates"],
        },
    ]


def build_output() -> dict[str, Any]:
    inventory = load_json(ITERATION_1_OUTPUT)
    schema = load_json(ITERATION_2_OUTPUT)
    route = load_json(ITERATION_3_OUTPUT)
    response = load_json(ITERATION_4_OUTPUT)
    identity = load_json(ITERATION_5_OUTPUT)
    integration = load_json(ITERATION_6_OUTPUT)
    readiness = load_json(ITERATION_7_OUTPUT)

    final_rows = build_final_classification_rows(
        inventory=inventory,
        route=route,
        response=response,
        identity=identity,
        integration=integration,
    )
    phase8_ready_contracts = readiness["matrix_result"]["phase8_ready_contracts"]
    deferred_blockers = readiness["matrix_result"]["deferred_blockers"]
    experiment_local_scaffolds = [
        row["mechanism_name"]
        for row in final_rows
        if row["final_primary_disposition"] == "scaffold"
    ]
    theory_sensitive_blockers = [
        row["mechanism_name"]
        for row in final_rows
        if row["final_primary_disposition"] == "theory_sensitive_blocker"
    ]
    final_nat_levels = {
        row["mechanism_name"]: row["final_nat_level"] for row in final_rows
    }
    hypotheses_closeout = {
        "hypothesis_a": {
            "status": "supported_as_scaffold_boundary",
            "meaning": (
                "Some N05-N11 producer mechanisms remain valid scaffolds or "
                "artifact-local validators only."
            ),
            "supporting_rows": experiment_local_scaffolds,
        },
        "hypothesis_b": {
            "status": "supported_at_nat4_readiness_only",
            "meaning": (
                "Route conductance memory and bounded/envelope-gated response "
                "magnitude can be specified as native LGRC policy surfaces without "
                "adding non-RC quantities, but this is not native support."
            ),
            "supporting_rows": phase8_ready_contracts,
        },
        "hypothesis_c": {
            "status": "supported_as_theory_sensitive_blockers",
            "meaning": (
                "Identity acceptance and full native agentic-like integration "
                "remain blocked until theory and component gates are explicit."
            ),
            "supporting_rows": theory_sensitive_blockers,
        },
    }
    phase8_handoff = {
        "status": "ready_to_open_targeted_phase8_if_requested",
        "phase8_ready_contracts": phase8_ready_contracts,
        "not_phase8_ready": deferred_blockers,
        "shared_prerequisites": [
            "open Phase 8 explicitly before editing src/*",
            "start native surfaces default-off",
            "include telemetry under src/pygrc/telemetry",
            "preserve enabled/validated/supported separation",
            "preserve separated budget and replay contracts",
            "record idempotent digests and snapshot/replay gates",
            "keep native support flags false until native validation passes",
            "keep agency, intention, goal ownership, identity acceptance, and "
            "fully native integration claims false",
        ],
        "implementation_fork": [
            {
                "path": "targeted_phase8_route_conductance_memory",
                "status": "available_after_n12_closeout",
                "source_contract": "native_route_conductance_memory_policy",
            },
            {
                "path": "targeted_phase8_response_magnitude",
                "status": "available_after_n12_closeout",
                "source_contract": "native_response_magnitude_policy",
            },
        ],
    }
    n13_handoff = {
        "status": "available_as_next_experiment_if_phase8_is_not_opened",
        "entry_note": (
            "N13 may consume support-survival, support-disruption, explicit "
            "restoration, route-memory, and bounded response evidence, but it "
            "must not consume identity acceptance. It should begin as "
            "support-seeking regulation, not identity-seeking regulation."
        ),
        "allowed_inputs": [
            "N07 support survival/disruption/restoration evidence",
            "N09 bounded proxy regulation evidence",
            "N10 support-sensitive integration matrix",
            "N11 artifact-only GALI7 generalization envelope",
            "N12 Phase 8 readiness matrix and blocker boundaries",
        ],
        "blocked_inputs": [
            "identity acceptance",
            "runtime identity acceptance",
            "semantic goal ownership",
            "agency",
            "fully native agentic-like integration",
        ],
    }
    roadmap_update_decision = {
        "roadmap_file_update_required": False,
        "reason": (
            "The existing N12-N18 roadmap already places N12 as naturalization "
            "and N13 as support-seeking/self-maintenance. N12 closeout records "
            "the handoff without changing roadmap order."
        ),
        "roadmap_source": rel(N12_ROADMAP),
        "handoff_source": rel(N12_HANDOFF),
    }
    final_claim_boundary = {
        "native_absorption_candidate_is_native_support": False,
        "phase8_readiness_is_phase8_implementation": False,
        "route_conductance_memory_is_intention": False,
        "response_magnitude_policy_is_goal_ownership": False,
        "support_survival_is_identity_acceptance": False,
        "component_nat4_candidate_is_integration_meta_policy": False,
        "agentic_like_integration_is_agency": False,
        "native_support_is_agency": False,
    }
    no_implementation_checks = {
        "src_diff_empty": git_status_short("src") == "",
        "native_supported_flags": False,
        "phase8_opened": False,
        "phase8_implementation_opened": False,
        "src_changes_required_for_n12": False,
    }
    source_artifacts = {
        rel(ITERATION_1_OUTPUT): source_artifact(ITERATION_1_OUTPUT, inventory),
        rel(ITERATION_2_OUTPUT): source_artifact(ITERATION_2_OUTPUT, schema),
        rel(ITERATION_3_OUTPUT): source_artifact(ITERATION_3_OUTPUT, route),
        rel(ITERATION_4_OUTPUT): source_artifact(ITERATION_4_OUTPUT, response),
        rel(ITERATION_5_OUTPUT): source_artifact(ITERATION_5_OUTPUT, identity),
        rel(ITERATION_6_OUTPUT): source_artifact(ITERATION_6_OUTPUT, integration),
        rel(ITERATION_7_OUTPUT): source_artifact(ITERATION_7_OUTPUT, readiness),
    }
    source_reports = {
        rel(ITERATION_1_REPORT): source_report(ITERATION_1_REPORT),
        rel(ITERATION_2_REPORT): source_report(ITERATION_2_REPORT),
        rel(ITERATION_3_REPORT): source_report(ITERATION_3_REPORT),
        rel(ITERATION_4_REPORT): source_report(ITERATION_4_REPORT),
        rel(ITERATION_5_REPORT): source_report(ITERATION_5_REPORT),
        rel(ITERATION_6_REPORT): source_report(ITERATION_6_REPORT),
        rel(ITERATION_7_REPORT): source_report(ITERATION_7_REPORT),
        rel(N12_ROADMAP): source_report(N12_ROADMAP),
        rel(N12_HANDOFF): source_report(N12_HANDOFF),
    }
    checks = {
        "every_seed_row_classified": len(final_rows)
        == len(inventory["n12_inventory_rows"]),
        "every_nat_level_frozen": all(row["final_nat_level"] for row in final_rows),
        "phase8_ready_contracts_match_iteration_7": phase8_ready_contracts
        == [
            "native_route_conductance_memory_policy",
            "native_response_magnitude_policy",
        ],
        "every_phase8_ready_row_has_controls_telemetry_tests": all(
            contract["negative_controls"]
            and contract["telemetry_requirements"]
            and contract["compatibility_tests"]
            for contract in readiness["phase8_ready_contracts"]
        ),
        "every_deferred_row_has_blocker_and_rationale": all(
            row["blockers"] and row["rationale"] for row in final_rows if row["deferred"]
        ),
        "identity_and_integration_blocked": deferred_blockers
        == [
            "native_identity_acceptance_validator",
            "native_agentic_like_integration_policy",
        ],
        "hypotheses_closed": all(
            value["status"] for value in hypotheses_closeout.values()
        ),
        "roadmap_decision_recorded": roadmap_update_decision[
            "roadmap_file_update_required"
        ]
        is False,
        "next_handoff_recorded": bool(phase8_handoff and n13_handoff),
        "claim_flags_all_false": all_claim_flags_false(CLAIM_FLAGS_FORCED_FALSE),
        "src_diff_empty": no_implementation_checks["src_diff_empty"],
        "native_supported_flags_false": no_implementation_checks[
            "native_supported_flags"
        ]
        is False,
        "phase8_opened_false": no_implementation_checks["phase8_opened"] is False,
        "source_file_sha256_all_present": all(
            artifact["sha256"] for artifact in source_artifacts.values()
        ),
    }
    output = {
        "experiment": "N12",
        "iteration": 8,
        "purpose": "closeout_and_handoff",
        "schema": "n12_closeout_and_handoff_v1",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed" if all(checks.values()) else "failed",
        "closeout_result": {
            "n12_closed": True,
            "final_status": "closed_claim_clean_bridge_experiment",
            "target_naturalization_level": "NAT4",
            "strongest_recorded_level": "NAT4",
            "phase8_ready_contracts": phase8_ready_contracts,
            "deferred_blockers": deferred_blockers,
            "native_supported_flags": False,
            "phase8_opened": False,
            "phase8_implementation_opened": False,
            "supported_interpretation": (
                "N12 classifies N05-N11 producer mechanisms into one scaffold, "
                "two Phase 8-ready contracts, and two theory-sensitive blockers "
                "without implementing Phase 8 or opening native support claims."
            ),
        },
        "final_nat_levels": final_nat_levels,
        "final_classification_rows": final_rows,
        "hypotheses_closeout": hypotheses_closeout,
        "phase8_handoff": phase8_handoff,
        "n13_handoff": n13_handoff,
        "roadmap_update_decision": roadmap_update_decision,
        "final_claim_boundary": final_claim_boundary,
        "claim_flags_forced_false": CLAIM_FLAGS_FORCED_FALSE,
        "no_implementation_checks": no_implementation_checks,
        "checks": checks,
        "source_artifacts": source_artifacts,
        "source_reports": source_reports,
        "artifact_reproducibility": {
            "generated_at_fixed": GENERATED_AT,
            "wall_clock_timestamp_in_file": False,
            "output_digest_excludes_generated_at_and_git": True,
        },
        "git": {
            "head": git_head(),
            "src_status_short": git_status_short("src"),
        },
    }
    output["output_digest"] = output_digest(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    result = output["closeout_result"]
    lines = [
        "# N12 Closeout And Handoff",
        "",
        "## Status",
        "",
        f"Status: `{output['status']}`.",
        "",
        "```text",
        f"n12_closed = {str(result['n12_closed']).lower()}",
        f"final_status = {result['final_status']}",
        f"strongest_recorded_level = {result['strongest_recorded_level']}",
        "phase8_ready_contracts = "
        f"{', '.join(result['phase8_ready_contracts'])}",
        "deferred_blockers = "
        f"{', '.join(result['deferred_blockers'])}",
        "native_supported_flags = false",
        "phase8_opened = false",
        "phase8_implementation_opened = false",
        "```",
        "",
        "N12 closes as a bridge experiment. It does not implement Phase 8, does",
        "not edit `src/*`, and does not convert artifact-only or producer-layer",
        "evidence into native support.",
        "",
        "## Final Classification",
        "",
        "| Mechanism | Disposition | NAT | Phase 8-ready | Source |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in output["final_classification_rows"]:
        lines.append(
            "| "
            f"`{row['mechanism_name']}` | "
            f"`{row['final_primary_disposition']}` | "
            f"`{row['final_nat_level']}` | "
            f"`{str(row['phase8_ready']).lower()}` | "
            f"`{row['source_artifact']}` |"
        )
    lines.extend(
        [
            "",
            "## Hypotheses",
            "",
            "```json",
            json.dumps(output["hypotheses_closeout"], indent=2, sort_keys=True),
            "```",
            "",
            "## Phase 8 Handoff",
            "",
            "```json",
            json.dumps(output["phase8_handoff"], indent=2, sort_keys=True),
            "```",
            "",
            "## N13 Handoff",
            "",
            "```json",
            json.dumps(output["n13_handoff"], indent=2, sort_keys=True),
            "```",
            "",
            "## Roadmap Update Decision",
            "",
            "```json",
            json.dumps(output["roadmap_update_decision"], indent=2, sort_keys=True),
            "```",
            "",
            "## Claim Boundary",
            "",
            "```json",
            json.dumps(output["final_claim_boundary"], indent=2, sort_keys=True),
            "```",
            "",
            "## No-Implementation Checks",
            "",
            "```json",
            json.dumps(output["no_implementation_checks"], indent=2, sort_keys=True),
            "```",
            "",
            "## Checks",
            "",
            "```json",
            json.dumps(output["checks"], indent=2, sort_keys=True),
            "```",
            "",
            "## Final Statement",
            "",
            "```text",
            "native absorption candidate != native support",
            "Phase 8 readiness != Phase 8 implementation",
            "route conductance memory != intention",
            "response magnitude policy != goal ownership",
            "support survival != identity acceptance",
            "component NAT4 candidate != integration meta-policy",
            "agentic-like integration != agency",
            "N13 may consume support-survival evidence but not identity acceptance",
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
