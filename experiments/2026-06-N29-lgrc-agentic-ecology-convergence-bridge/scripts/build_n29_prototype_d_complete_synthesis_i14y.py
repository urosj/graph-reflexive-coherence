#!/usr/bin/env python3
"""Build N29 I14Y complete Prototype D synthesis artifact."""

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
    "build_n29_prototype_d_complete_synthesis_i14y.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

SOURCE_PATHS = {
    "i14x_pre_composition_synthesis": (
        EXPERIMENT / "outputs" / "n29_generative_extractive_medium_reshaping_synthesis_i14x.json"
    ),
    "i14_4_single_direction_neutral_circulation": (
        EXPERIMENT / "outputs" / "n29_neutral_circulation_composition_i144.json"
    ),
    "i14_4_1_producer_reverse_loop_bridge": (
        EXPERIMENT / "outputs" / "n29_neutral_circulation_loop_closure_i1441.json"
    ),
    "i14_4_2_native_reverse_search_blocker": (
        EXPERIMENT / "outputs" / "n29_neutral_circulation_native_search_i1442.json"
    ),
    "i14_4_3_native_directed_cycle_blocker": (
        EXPERIMENT / "outputs" / "n29_neutral_circulation_directed_cycle_i1443.json"
    ),
    "i14_4_4_producer_directed_cycle_bridge": (
        EXPERIMENT / "outputs" / "n29_neutral_circulation_directed_cycle_bridge_i1444.json"
    ),
    "i14_5_generator_extractor_one_way_bridge": (
        EXPERIMENT / "outputs" / "n29_phase_coupled_generator_extractor_i145.json"
    ),
    "i14_5_1_generator_extractor_feedback_bridge": (
        EXPERIMENT / "outputs" / "n29_generator_extractor_feedback_i1451.json"
    ),
    "i14_5_2_buffered_feedback_bridge": (
        EXPERIMENT / "outputs" / "n29_buffered_generator_extractor_feedback_i1452.json"
    ),
    "i14_6_multi_role_phase_loop": (
        EXPERIMENT / "outputs" / "n29_multi_role_phase_loop_i146.json"
    ),
    "i14_6_1_narrow_aggregate_leakage": (
        EXPERIMENT / "outputs" / "n29_multi_leg_leakage_aggregation_i1461.json"
    ),
    "i14_6_2_wider_aggregate_leakage": (
        EXPERIMENT / "outputs" / "n29_wider_margin_leakage_aggregation_i1462.json"
    ),
    "i14d_loop_composition_controls": (
        EXPERIMENT / "outputs" / "n29_loop_composition_controls_i14d.json"
    ),
    "i14e_loop_composition_replay_stress": (
        EXPERIMENT / "outputs" / "n29_loop_composition_replay_stress_i14e.json"
    ),
}

OUT = EXPERIMENT / "outputs" / "n29_prototype_d_complete_synthesis_i14y.json"
REPORT = EXPERIMENT / "reports" / "n29_prototype_d_complete_synthesis_i14y.md"

UNSAFE_FLAGS = {
    "agency_claim_allowed": False,
    "agentic_ecology_runtime_claim_allowed": False,
    "altruism_claim_allowed": False,
    "ant_ecology_success_claim_allowed": False,
    "biological_agency_claim_allowed": False,
    "closed_environmental_circulation_loop_claim_allowed": False,
    "cooperation_claim_allowed": False,
    "coordinated_exchange_cycle_claim_allowed": False,
    "ecology_success_claim_allowed": False,
    "exploitation_claim_allowed": False,
    "literal_perpetual_runtime_claim_allowed": False,
    "native_ecological_role_claim_allowed": False,
    "native_support_claim_allowed": False,
    "resource_economy_claim_allowed": False,
    "semantic_goal_claim_allowed": False,
    "semantic_purpose_claim_allowed": False,
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


def build_output() -> dict[str, Any]:
    sources = {source_id: load_json(path) for source_id, path in SOURCE_PATHS.items()}
    i14x = sources["i14x_pre_composition_synthesis"]
    i144 = sources["i14_4_single_direction_neutral_circulation"]
    i1441 = sources["i14_4_1_producer_reverse_loop_bridge"]
    i1442 = sources["i14_4_2_native_reverse_search_blocker"]
    i1443 = sources["i14_4_3_native_directed_cycle_blocker"]
    i1444 = sources["i14_4_4_producer_directed_cycle_bridge"]
    i145 = sources["i14_5_generator_extractor_one_way_bridge"]
    i1451 = sources["i14_5_1_generator_extractor_feedback_bridge"]
    i1452 = sources["i14_5_2_buffered_feedback_bridge"]
    i146 = sources["i14_6_multi_role_phase_loop"]
    i1461 = sources["i14_6_1_narrow_aggregate_leakage"]
    i1462 = sources["i14_6_2_wider_aggregate_leakage"]
    i14d = sources["i14d_loop_composition_controls"]
    i14e = sources["i14e_loop_composition_replay_stress"]

    native_motif_layer = {
        "status": "supported",
        "source": "I14X pre-composition synthesis",
        "direct_runtime_candidate_count": i14x["direct_runtime_candidate_count"],
        "direct_replay_stress_backed_count": i14x["direct_replay_stress_backed_count"],
        "native_source_current_motifs": [
            "I14.1 generative enrichment",
            "I14.2 extractive depletion with leakage caveat",
            "I14.3 processor / redistribution",
            "I14.4 single-direction neutral-circulation leg",
        ],
        "clean_native_extractor_supported": i14x["native_lgrc_clean_extractor_supported"],
        "clean_producer_mediated_extractor_supported": i14x[
            "clean_producer_mediated_extractor_supported"
        ],
        "claim_ceiling": (
            "native/source-current motif runtime evidence with extractor caveat; "
            "not native closed composition"
        ),
    }
    native_composition_layer = {
        "status": "blocked",
        "native_reverse_opposite_orientation_leg_found": i1442[
            "native_reverse_opposite_orientation_leg_found"
        ],
        "native_directed_cycle_found": i1443["native_directed_cycle_found"],
        "native_closed_environmental_circulation_supported": False,
        "native_phase_coupled_exchange_supported": False,
        "native_multi_role_ecology_supported": False,
        "native_aggregate_shared_medium_leakage_supported": False,
        "blocking_sources": [
            "I14.4-2 native reverse search",
            "I14.4-3 native directed-cycle search",
            "I14.5/I14.5-1/I14.5-2 native phase support flags",
            "I14.6/I14.6-2 native multi-role and aggregate leakage flags",
        ],
    }
    producer_composition_layer = {
        "status": "replay_stress_backed_bridge_catalogue_supported",
        "control_gate": i14d["acceptance_state"],
        "replay_stress_gate": i14e["acceptance_state"],
        "candidate_count": i14e["candidate_count"],
        "stable_candidate_count": i14e["stable_candidate_count"],
        "replay_count": i14e["replay_count"],
        "stress_count": i14e["stress_count"],
        "failed_replay_count": i14e["failed_replay_count"],
        "failed_stress_count": i14e["failed_stress_count"],
        "bridge_candidates": i14d["i14e_consumable_candidate_ids"],
        "context_or_blocker_rows": i14d["limited_or_blocker_source_ids"],
        "aggregate_leakage_margin": i14e["aggregate_leakage_replay_record"][
            "aggregate_merge_leakage_margin"
        ],
        "aggregate_leakage_ceiling": i14e["aggregate_leakage_replay_record"][
            "aggregate_merge_leakage_ceiling"
        ],
        "producer_guard_capture_remains_debt": i14e["aggregate_leakage_replay_record"][
            "producer_guard_capture_remains_debt"
        ],
        "claim_ceiling": (
            "replay/stress-backed producer-mediated Prototype D composition "
            "bridge catalogue; not native ecology or resource economy"
        ),
    }
    row_roles = [
        {
            "row_id": "I14X",
            "role": "pre-composition native motif and extractor-side synthesis",
            "status": "consumed",
            "output_digest": i14x["output_digest"],
        },
        {
            "row_id": "I14.4",
            "role": "native/source-current single-direction neutral-circulation leg",
            "status": "context_supported_closed_loop_blocked",
            "output_digest": i144["output_digest"],
        },
        {
            "row_id": "I14.4-1",
            "role": "producer-mediated reverse-loop bridge candidate",
            "status": "replay_stress_backed_via_i14e",
            "output_digest": i1441["output_digest"],
        },
        {
            "row_id": "I14.4-2",
            "role": "native reverse-leg blocker",
            "status": "blocker_preserved",
            "output_digest": i1442["output_digest"],
        },
        {
            "row_id": "I14.4-3",
            "role": "native directed-cycle blocker",
            "status": "blocker_preserved",
            "output_digest": i1443["output_digest"],
        },
        {
            "row_id": "I14.4-4",
            "role": "producer-mediated all-forward directed-cycle bridge",
            "status": "replay_stress_backed_via_i14e",
            "output_digest": i1444["output_digest"],
        },
        {
            "row_id": "I14.5",
            "role": "one-way generator/extractor bridge context",
            "status": "context_supported_stronger_loop_claim_blocked",
            "output_digest": i145["output_digest"],
        },
        {
            "row_id": "I14.5-1",
            "role": "producer-mediated generator/extractor feedback bridge",
            "status": "replay_stress_backed_via_i14e",
            "output_digest": i1451["output_digest"],
        },
        {
            "row_id": "I14.5-2",
            "role": "producer-mediated buffered feedback bridge",
            "status": "replay_stress_backed_via_i14e",
            "output_digest": i1452["output_digest"],
        },
        {
            "row_id": "I14.6",
            "role": "producer-mediated multi-role phase-loop candidate",
            "status": "replay_stress_backed_via_i14e",
            "output_digest": i146["output_digest"],
        },
        {
            "row_id": "I14.6-1",
            "role": "narrow aggregate leakage baseline",
            "status": "baseline_context_superseded_by_i14_6_2_for_margin",
            "output_digest": i1461["output_digest"],
        },
        {
            "row_id": "I14.6-2",
            "role": "wider-margin producer-mediated aggregate leakage candidate",
            "status": "replay_stress_backed_via_i14e",
            "output_digest": i1462["output_digest"],
        },
        {
            "row_id": "I14-D",
            "role": "loop/composition controls",
            "status": "passed",
            "output_digest": i14d["output_digest"],
        },
        {
            "row_id": "I14-E",
            "role": "loop/composition replay and stress",
            "status": "passed",
            "output_digest": i14e["output_digest"],
        },
    ]
    naturalization_targets = [
        {
            "target_id": "native_ordered_multi_leg_dependency",
            "needed_for": "native closed circulation / native directed cycle",
            "current_status": "blocked_by_I14.4-2_and_I14.4-3",
        },
        {
            "target_id": "native_changed_medium_handoff_between_motifs",
            "needed_for": "native generator/extractor feedback and buffered feedback",
            "current_status": "producer_mediated_in_I14.5-1_and_I14.5-2",
        },
        {
            "target_id": "native_multi_leg_leakage_aggregation",
            "needed_for": "native multi-role ecology / aggregate shared-medium leakage",
            "current_status": "producer_mediated_guard_in_I14.6-2",
        },
        {
            "target_id": "native_clean_extractor_without_leakage_gate",
            "needed_for": "native clean extractor lane",
            "current_status": "producer_mediated_in_I14.2-3; native I14.2 and I14.2-2 retain caveat",
        },
    ]
    data: dict[str, Any] = {
        "artifact_id": "n29_prototype_d_complete_synthesis_i14y",
        "experiment_id": "N29",
        "iteration": "I14Y",
        "title": "Prototype D Complete Synthesis",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_complete_prototype_d_synthesis_ready_for_i15",
        "source_artifacts": [
            source_artifact(source_id, SOURCE_PATHS[source_id], parsed)
            for source_id, parsed in sources.items()
        ],
        "prototype_family": "generative_extractive_medium_reshaping_and_composition",
        "synthesis_scope": "I14_through_I14_E",
        "native_motif_layer": native_motif_layer,
        "native_composition_layer": native_composition_layer,
        "producer_composition_layer": producer_composition_layer,
        "row_roles": row_roles,
        "naturalization_targets": naturalization_targets,
        "complete_prototype_d_synthesis_supported": True,
        "prototype_d_native_motif_layer_supported": True,
        "prototype_d_native_composition_layer_supported": False,
        "prototype_d_producer_mediated_composition_bridge_supported": True,
        "prototype_d_final_atlas_classification_allowed": False,
        "ready_for_iteration_15": True,
        "claim_ceiling": (
            "complete Prototype D bridge synthesis with native/source-current "
            "motif layer and replay/stress-backed producer-mediated composition "
            "bridge catalogue; not native ecology, resource economy, cooperation, "
            "exploitation, agency, or final atlas classification"
        ),
        "claim_boundary": {
            "native_ecology_claim_allowed": False,
            "native_multi_role_ecology_supported": False,
            "native_aggregate_shared_medium_leakage_supported": False,
            "resource_economy_claim_allowed": False,
            "cooperation_claim_allowed": False,
            "exploitation_claim_allowed": False,
            "agency_claim_allowed": False,
            "unsafe_claim_flags": UNSAFE_FLAGS,
        },
    }
    checks = [
        check("all_source_artifacts_passed", all(source["status"] == "passed" for source in sources.values())),
        check("i14x_native_motif_layer_supported", i14x["prototype_d_runtime_evidence_supported"] is True),
        check(
            "native_composition_blockers_preserved",
            native_composition_layer["native_reverse_opposite_orientation_leg_found"] is False
            and native_composition_layer["native_directed_cycle_found"] is False
            and native_composition_layer["native_multi_role_ecology_supported"] is False,
        ),
        check(
            "producer_composition_replay_stress_supported",
            i14e["producer_mediated_bridge_catalogue_supported"] is True
            and producer_composition_layer["stable_candidate_count"] == 6
            and producer_composition_layer["failed_replay_count"] == 0
            and producer_composition_layer["failed_stress_count"] == 0,
        ),
        check(
            "aggregate_leakage_margin_carried_forward",
            producer_composition_layer["aggregate_leakage_margin"] == 0.0104
            and i14e["native_aggregate_shared_medium_leakage_supported"] is False,
        ),
        check("row_roles_cover_core_tranche", len(row_roles) == 14),
        check("naturalization_targets_recorded", len(naturalization_targets) == 4),
        check("final_atlas_classification_still_pending", data["prototype_d_final_atlas_classification_allowed"] is False),
        check("ready_for_iteration_15", data["ready_for_iteration_15"] is True),
        check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_FLAGS.values())),
        check("no_absolute_paths_in_records", no_absolute_paths(data)),
    ]
    data["checks"] = checks
    data["failed_checks"] = [row["check_id"] for row in checks if not row["passed"]]
    data["script_sha256"] = sha256_file(ROOT / SCRIPT_RELATIVE_PATH)
    if data["failed_checks"]:
        data["status"] = "failed"
        data["acceptance_state"] = "failed_complete_prototype_d_synthesis"
        data["complete_prototype_d_synthesis_supported"] = False
        data["ready_for_iteration_15"] = False
    return finalize(data)


def write_report(data: dict[str, Any]) -> None:
    lines = [
        "# Prototype D Complete Synthesis",
        "",
        "## Result",
        "",
        "```text",
        f"status = {data['status']}",
        f"acceptance_state = {data['acceptance_state']}",
        f"synthesis_scope = {data['synthesis_scope']}",
        f"prototype_d_native_motif_layer_supported = {str(data['prototype_d_native_motif_layer_supported']).lower()}",
        f"prototype_d_native_composition_layer_supported = {str(data['prototype_d_native_composition_layer_supported']).lower()}",
        f"prototype_d_producer_mediated_composition_bridge_supported = {str(data['prototype_d_producer_mediated_composition_bridge_supported']).lower()}",
        f"producer_bridge_stable_candidate_count = {data['producer_composition_layer']['stable_candidate_count']}",
        f"aggregate_leakage_margin = {data['producer_composition_layer']['aggregate_leakage_margin']}",
        f"ready_for_iteration_15 = {str(data['ready_for_iteration_15']).lower()}",
        f"output_digest = {data['output_digest']}",
        "```",
        "",
        "## Interpretation",
        "",
        (
            "This is the complete Prototype D synthesis before I15 atlas classification. "
            "The native/source-current motif layer is supported: generative enrichment, "
            "extractive depletion with leakage caveat, processor redistribution, and "
            "a single-direction neutral-circulation leg. The native composition layer "
            "remains blocked: native reverse/directed-cycle closure, native phase-coupled "
            "exchange, native multi-role ecology, and native aggregate shared-medium "
            "leakage are not supported by the current artifacts."
        ),
        "",
        (
            "The producer-mediated composition layer is now strong enough to carry "
            "forward as a bridge catalogue: I14-D controls passed, I14-E replay/stress "
            "passed, six bridge candidates are stable, and I14.6-2 preserves aggregate "
            "leakage margin 0.0104. This is bridge evidence, not native ecology or "
            "agency evidence."
        ),
        "",
        "## Layer Summary",
        "",
        "| Layer | Status | Claim Ceiling |",
        "| --- | --- | --- |",
        f"| Native motif layer | `{data['native_motif_layer']['status']}` | {data['native_motif_layer']['claim_ceiling']} |",
        f"| Native composition layer | `{data['native_composition_layer']['status']}` | native composition remains blocked |",
        f"| Producer composition layer | `{data['producer_composition_layer']['status']}` | {data['producer_composition_layer']['claim_ceiling']} |",
        "",
        "## Row Roles",
        "",
        "| Row | Role | Status |",
        "| --- | --- | --- |",
    ]
    for row in data["row_roles"]:
        lines.append(f"| `{row['row_id']}` | {row['role']} | `{row['status']}` |")
    lines += [
        "",
        "## Naturalization Targets",
        "",
        "| Target | Needed For | Current Status |",
        "| --- | --- | --- |",
    ]
    for row in data["naturalization_targets"]:
        lines.append(
            f"| `{row['target_id']}` | {row['needed_for']} | {row['current_status']} |"
        )
    lines += [
        "",
        "## Claim Boundary",
        "",
        (
            "Final atlas classification remains pending I15. Native ecology, native "
            "aggregate shared-medium leakage, resource economy, cooperation, "
            "exploitation, biological agency, semantic goal, and agency claims remain blocked."
        ),
        "",
        "## Checks",
        "",
        "| Check | Passed |",
        "| --- | --- |",
    ]
    for row in data["checks"]:
        lines.append(f"| `{row['check_id']}` | `{str(row['passed']).lower()}` |")
    lines.append("")
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    data = build_output()
    write_json(OUT, data)
    write_report(data)
    data["report_sha256"] = sha256_file(REPORT)
    data = finalize(data)
    write_json(OUT, data)
    write_report(data)
    print(f"wrote {OUT.relative_to(ROOT)}")
    print(f"wrote {REPORT.relative_to(ROOT)}")
    print(f"status = {data['status']}")
    print(f"output_digest = {data['output_digest']}")


if __name__ == "__main__":
    main()
