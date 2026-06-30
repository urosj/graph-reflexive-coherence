#!/usr/bin/env python3
"""Build N29 I14 Prototype D generative/extractive medium-reshaping motifs."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-30T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N29-lgrc-agentic-ecology-convergence-bridge"
N28 = ROOT / "experiments" / "2026-06-N28-lgrc-generative-vs-extractive-persistence"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/scripts/"
    "build_n29_generative_extractive_medium_reshaping_i14.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

SOURCE_PATHS = {
    "n29_i8_bridge_motif_library_index": EXPERIMENT
    / "outputs"
    / "n29_bridge_motif_library_i8.json",
    "n29_i13x_prototype_c_handoff": EXPERIMENT
    / "outputs"
    / "n29_proxy_susceptibility_reentry_synthesis_i13x.json",
    "n28_closeout_and_n29_handoff": N28 / "outputs" / "n28_closeout_and_n29_handoff.json",
    "n28_replay_capacity_attribution_matrix": N28
    / "outputs"
    / "n28_replay_capacity_attribution_matrix.json",
    "n28_stress_regime_separation_matrix": N28
    / "outputs"
    / "n28_stress_regime_separation_matrix.json",
    "n28_regime_boundary_transition_matrix": N28
    / "outputs"
    / "n28_regime_boundary_transition_matrix.json",
    "n28_focused_margin_variant_replay_matrix": N28
    / "outputs"
    / "n28_focused_margin_variant_replay_matrix.json",
    "n28_focused_margin_variant_stress_envelope": N28
    / "outputs"
    / "n28_focused_margin_variant_stress_envelope.json",
    "n28_generative_extractive_visualization": N28
    / "outputs"
    / "n28_generative_extractive_visualization.json",
    "n28_primary_generative_candidate_probe": N28
    / "outputs"
    / "n28_primary_generative_candidate_probe.json",
    "n28_primary_extractive_contrast_probe": N28
    / "outputs"
    / "n28_primary_extractive_contrast_probe.json",
    "n28_primary_competitive_neutral_contrast_probe": N28
    / "outputs"
    / "n28_primary_competitive_neutral_contrast_probe.json",
    "n28_competitive_neutral_mechanism_diversity_probe": N28
    / "outputs"
    / "n28_competitive_neutral_mechanism_diversity_probe.json",
    "n28_higher_margin_neutral_circulation_probe": N28
    / "outputs"
    / "n28_higher_margin_neutral_circulation_probe.json",
    "n28_higher_margin_competitive_redistribution_probe": N28
    / "outputs"
    / "n28_higher_margin_competitive_redistribution_probe.json",
}

OUT = EXPERIMENT / "outputs" / "n29_generative_extractive_medium_reshaping_i14.json"
REPORT = EXPERIMENT / "reports" / "n29_generative_extractive_medium_reshaping_i14.md"

MOTIF_IDS = [
    "generative_enrichment_motif",
    "extractive_depletion_motif",
    "processor_redistribution_motif",
    "neutral_circulation_implication",
    "phase_coupled_generator_extractor_implication",
]

UNSAFE_FLAGS = {
    "agentic_ecology_runtime_claim_allowed": False,
    "agency_claim_allowed": False,
    "altruism_claim_allowed": False,
    "ant_ecology_success_claim_allowed": False,
    "biological_agency_claim_allowed": False,
    "closed_environmental_circulation_loop_claim_allowed": False,
    "cooperation_claim_allowed": False,
    "coordinated_exchange_cycle_claim_allowed": False,
    "ecology_success_claim_allowed": False,
    "exploitation_claim_allowed": False,
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


def source_artifact(source_id: str, path: Path, parsed: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "path": str(path.relative_to(ROOT)),
        "artifact_id": parsed.get("artifact_id", "not_recorded"),
        "iteration": parsed.get("iteration", "not_recorded"),
        "status": parsed.get("status", "not_recorded"),
        "acceptance_state": parsed.get("acceptance_state", "not_recorded"),
        "output_digest": parsed.get("output_digest", "not_recorded"),
        "sha256": sha256_file(path),
    }


def replay_row_by_source_row(replay_rows: list[dict[str, Any]], source_row_id: str) -> dict[str, Any]:
    for row in replay_rows:
        if row.get("source_row_id") == source_row_id:
            return row
    raise KeyError(source_row_id)


def case_summary_by_id(case_summaries: list[dict[str, Any]], case_id: str) -> dict[str, Any]:
    for row in case_summaries:
        if row["case_id"] == case_id:
            return row
    raise KeyError(case_id)


def source_reference(parsed: dict[str, Any], source_id: str, row_id: str | None = None) -> dict[str, Any]:
    path = SOURCE_PATHS[source_id]
    ref = {
        "source_id": source_id,
        "path": str(path.relative_to(ROOT)),
        "output_digest": parsed.get("output_digest", "not_recorded"),
        "sha256": sha256_file(path),
    }
    if row_id is not None:
        ref["row_id"] = row_id
    return ref


def replay_basis(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "row_id": row["row_id"],
        "source_row_id": row["source_row_id"],
        "source_iteration": row["source_iteration"],
        "source_regime_label": row["source_regime_label"],
        "final_consumable_rung": row["final_consumable_rung"],
        "artifact_replay_result": row["artifact_replay_result"],
        "snapshot_load_replay_result": row["snapshot_load_replay_result"],
        "duplicate_replay_result": row["duplicate_replay_result"],
        "duplicate_replay_second_emitted": row["duplicate_replay_second_emitted"],
        "duplicate_replay_meaning": "second_emitted_false_means_duplicate_suppression_worked",
        "capacity_attribution_controls_result": row["capacity_attribution_controls_result"],
        "focal_survival_only_controls_result": row["focal_survival_only_controls_result"],
        "merge_leakage_controls_result": row["merge_leakage_controls_result"],
        "regime_label_stable_under_replay": row["regime_label_stable_under_replay"],
        "replay_trace_digest": row["replay_trace_digest"],
    }


def focused_row(parsed: dict[str, Any]) -> dict[str, Any]:
    return parsed["candidate_rows"][0]


def motif_row(
    motif_id: str,
    motif_classification: str,
    source_basis: list[dict[str, Any]],
    ecology_demand_served: list[str],
    supplied_capability: str,
    bridge_motif: str,
    geometric_read: str,
    downstream_probe_suggested: str,
    status: str,
    claim_ceiling: str,
    remaining_debt: list[str],
    visualization_case: dict[str, Any] | None,
    replay: dict[str, Any] | None,
    stress_basis: dict[str, Any],
    loop_implication: bool,
) -> dict[str, Any]:
    return {
        "motif_id": motif_id,
        "prototype_family": "generative_extractive_medium_reshaping",
        "motif_classification": motif_classification,
        "source_basis": source_basis,
        "ecology_demand_served": ecology_demand_served,
        "supplied_capability": supplied_capability,
        "bridge_motif": bridge_motif,
        "geometric_read": geometric_read,
        "runtime_or_reconstruction_status": status,
        "replay_basis": replay if replay is not None else "future_composition_replay_required",
        "stress_basis": stress_basis,
        "visualization_case": visualization_case if visualization_case is not None else "not_visualized_as_distinct_case",
        "total_coherence_visualization_caveat_preserved": True,
        "source_backed_now": True,
        "requires_future_runtime_construction": loop_implication,
        "closed_loop_or_exchange_cycle_claim_allowed": False,
        "resource_economy_claim_allowed": False,
        "agentic_ecology_runtime_claim_allowed": False,
        "remaining_producer_medium_naturalization_debt": remaining_debt,
        "downstream_ecology_probe_suggested": downstream_probe_suggested,
        "claim_ceiling": claim_ceiling,
    }


def build_motifs() -> dict[str, Any]:
    sources = {source_id: load_json(path) for source_id, path in SOURCE_PATHS.items()}
    closeout = sources["n28_closeout_and_n29_handoff"]
    replay = sources["n28_replay_capacity_attribution_matrix"]
    stress = sources["n28_stress_regime_separation_matrix"]
    transition = sources["n28_regime_boundary_transition_matrix"]
    focused_replay = sources["n28_focused_margin_variant_replay_matrix"]
    focused_stress = sources["n28_focused_margin_variant_stress_envelope"]
    visualization = sources["n28_generative_extractive_visualization"]
    i13x = sources["n29_i13x_prototype_c_handoff"]

    replay_rows = replay["replay_rows"]
    visual_cases = visualization["case_summaries"]
    stress_summary = stress["stress_summary"]
    focused_stress_summary = focused_stress["stress_summary"]

    generative_replay = replay_row_by_source_row(
        replay_rows, "n28_i4_row_primary_generative_candidate"
    )
    extractive_replay = replay_row_by_source_row(
        replay_rows, "n28_i4b_row_primary_extractive_contrast"
    )
    competitive_replay = replay_row_by_source_row(
        replay_rows, "n28_i4d_row_primary_competitive_neutral_contrast"
    )
    neutral_replay = replay_row_by_source_row(
        replay_rows, "n28_i4e_row_competitive_neutral_mechanism_diversity_contrast"
    )
    focused_neutral = focused_row(sources["n28_higher_margin_neutral_circulation_probe"])
    focused_competitive = focused_row(sources["n28_higher_margin_competitive_redistribution_probe"])

    shared_stress = {
        "stress_source": source_reference(stress, "n28_stress_regime_separation_matrix"),
        "ge5_or_stronger_supported": stress["ge5_or_stronger_supported"],
        "ge6_or_stronger_supported": stress["ge6_or_stronger_supported"],
        "stress_passed_row_count": stress_summary["stress_passed_row_count"],
        "stress_failed_row_count": stress_summary["stress_failed_row_count"],
        "thresholds_retuned_for_stress": stress_summary["thresholds_retuned_for_stress"],
        "minimum_margin_by_regime": {
            key: value["minimum_margin"]
            for key, value in stress_summary["regime_results"].items()
        },
    }
    focused_stress_basis = {
        "stress_source": source_reference(focused_stress, "n28_focused_margin_variant_stress_envelope"),
        "focused_variant_ge5_supported": focused_stress["focused_variant_ge5_supported"],
        "focused_optimization_not_generalization": focused_stress_summary[
            "focused_optimization_not_generalization"
        ],
        "broad_margin_robustness_supported": focused_stress_summary[
            "broad_margin_robustness_supported"
        ],
        "order_of_magnitude_robustness_supported": focused_stress_summary[
            "order_of_magnitude_robustness_supported"
        ],
        "minimum_current_margin": focused_stress_summary["minimum_current_margin"],
    }

    motifs = [
        motif_row(
            motif_id="generative_enrichment_motif",
            motif_classification="source_backed_environment_enrichment_motif",
            source_basis=[
                source_reference(
                    sources["n28_primary_generative_candidate_probe"],
                    "n28_primary_generative_candidate_probe",
                    "n28_i4_row_primary_generative_candidate",
                ),
                source_reference(replay, "n28_replay_capacity_attribution_matrix", generative_replay["row_id"]),
                source_reference(stress, "n28_stress_regime_separation_matrix"),
                source_reference(closeout, "n28_closeout_and_n29_handoff"),
            ],
            ecology_demand_served=[
                "environment_capacity_enrichment",
                "constructive_medium_change",
                "future_resource_field_seeding_without_resource_semantics",
            ],
            supplied_capability=(
                "Focal basin persists while neighbor support, boundary, "
                "distinguishability, and environment basin-forming capacity increase."
            ),
            bridge_motif="focal_persistence_plus_neighbor_capacity_gain",
            geometric_read=(
                "The focal basin remains above support/coherence/stability floors while "
                "the adjacent capacity shell becomes more distinguishable, more bounded, "
                "and better supported."
            ),
            downstream_probe_suggested=(
                "Use as a future ecology probe where local persistence enriches an adjacent "
                "medium without claiming cooperation or resource production."
            ),
            status="source_backed_motif_synthesis",
            claim_ceiling="bounded_environment_enrichment_motif_not_resource_economy",
            remaining_debt=[
                "no resource ownership semantics",
                "no coordinated exchange cycle",
                "no agentic ecology runtime",
            ],
            visualization_case=case_summary_by_id(visual_cases, "generative_enrichment"),
            replay=replay_basis(generative_replay),
            stress_basis=shared_stress,
            loop_implication=False,
        ),
        motif_row(
            motif_id="extractive_depletion_motif",
            motif_classification="source_backed_environment_depletion_motif",
            source_basis=[
                source_reference(
                    sources["n28_primary_extractive_contrast_probe"],
                    "n28_primary_extractive_contrast_probe",
                    "n28_i4b_row_primary_extractive_contrast",
                ),
                source_reference(replay, "n28_replay_capacity_attribution_matrix", extractive_replay["row_id"]),
                source_reference(stress, "n28_stress_regime_separation_matrix"),
                source_reference(closeout, "n28_closeout_and_n29_handoff"),
            ],
            ecology_demand_served=[
                "environment_capacity_depletion",
                "bounded_extraction_or_flattening_contrast",
                "future_loss_or_pressure_field_without_exploitation_semantics",
            ],
            supplied_capability=(
                "Focal basin persists while neighbor support, boundary, "
                "distinguishability, and environment capacity decrease or flatten."
            ),
            bridge_motif="focal_persistence_plus_neighbor_capacity_loss",
            geometric_read=(
                "The focal basin remains intact while the surrounding capacity shell is "
                "drained or flattened, so persistence is separated from enrichment."
            ),
            downstream_probe_suggested=(
                "Use as a future ecology probe for depletion pressure or extraction-like "
                "medium change, with exploitation and goal semantics blocked."
            ),
            status="source_backed_motif_synthesis",
            claim_ceiling="bounded_environment_depletion_motif_not_exploitation",
            remaining_debt=[
                "no exploitation semantics",
                "no selective uptake or resource assimilation",
                "no agentic ecology runtime",
            ],
            visualization_case=case_summary_by_id(visual_cases, "extractive_persistence"),
            replay=replay_basis(extractive_replay),
            stress_basis=shared_stress,
            loop_implication=False,
        ),
        motif_row(
            motif_id="processor_redistribution_motif",
            motif_classification="source_backed_capacity_redistribution_motif",
            source_basis=[
                source_reference(
                    sources["n28_primary_competitive_neutral_contrast_probe"],
                    "n28_primary_competitive_neutral_contrast_probe",
                    "n28_i4d_row_primary_competitive_neutral_contrast",
                ),
                source_reference(
                    sources["n28_higher_margin_competitive_redistribution_probe"],
                    "n28_higher_margin_competitive_redistribution_probe",
                    focused_competitive["row_id"],
                ),
                source_reference(replay, "n28_replay_capacity_attribution_matrix", competitive_replay["row_id"]),
                source_reference(focused_replay, "n28_focused_margin_variant_replay_matrix"),
                source_reference(focused_stress, "n28_focused_margin_variant_stress_envelope"),
            ],
            ecology_demand_served=[
                "capacity_redistribution",
                "local_processing_or_reshaping",
                "future_environment_changer_without_intentional_processing_semantics",
            ],
            supplied_capability=(
                "Capacity can increase in one local lobe while decreasing in another "
                "under the same regime-policy family."
            ),
            bridge_motif="one_region_depleted_another_enriched",
            geometric_read=(
                "The pattern behaves like a geometric processor: it preserves focal "
                "persistence while redistributing capacity across local regions, rather "
                "than globally enriching or globally depleting the medium."
            ),
            downstream_probe_suggested=(
                "Use as a future ecology probe for medium reshaping or local route-field "
                "processing, while blocking semantic tool/use readings."
            ),
            status="source_backed_motif_synthesis",
            claim_ceiling="bounded_processor_redistribution_motif_not_intentional_processing",
            remaining_debt=[
                "no semantic processing or tool use",
                "no coordinated exchange cycle",
                "focused margin improvement is not broad robustness",
            ],
            visualization_case=case_summary_by_id(visual_cases, "competitive_redistribution"),
            replay=replay_basis(competitive_replay),
            stress_basis=focused_stress_basis,
            loop_implication=False,
        ),
        motif_row(
            motif_id="neutral_circulation_implication",
            motif_classification="source_backed_neutral_circulation_implication",
            source_basis=[
                source_reference(
                    sources["n28_competitive_neutral_mechanism_diversity_probe"],
                    "n28_competitive_neutral_mechanism_diversity_probe",
                    "n28_i4e_row_competitive_neutral_mechanism_diversity_contrast",
                ),
                source_reference(
                    sources["n28_higher_margin_neutral_circulation_probe"],
                    "n28_higher_margin_neutral_circulation_probe",
                    focused_neutral["row_id"],
                ),
                source_reference(replay, "n28_replay_capacity_attribution_matrix", neutral_replay["row_id"]),
                source_reference(focused_replay, "n28_focused_margin_variant_replay_matrix"),
                source_reference(focused_stress, "n28_focused_margin_variant_stress_envelope"),
            ],
            ecology_demand_served=[
                "balanced_capacity_exchange_implication",
                "future_circulation_design_seed",
                "medium_route_exchange_without_loop_claim",
            ],
            supplied_capability=(
                "Neutral or near-neutral circulation-like capacity routing can be "
                "identified while focal persistence remains bounded."
            ),
            bridge_motif="balanced_or_near_neutral_capacity_circulation_implication",
            geometric_read=(
                "N28 supplies a three-lobe circulation-like pattern with inflow, outflow, "
                "and buffer roles, but I14 does not pair it with an opposite ordered leg."
            ),
            downstream_probe_suggested=(
                "Later compose with an oppositely oriented neutral row and test ordered "
                "dependency before claiming a closed circulation loop."
            ),
            status="source_backed_implication_future_runtime_composition_required",
            claim_ceiling="neutral_circulation_implication_not_closed_loop",
            remaining_debt=[
                "opposite orientation not composed here",
                "ordered dependency not run",
                "closed circulation replay/control matrix not run",
            ],
            visualization_case=case_summary_by_id(visual_cases, "neutral_circulation"),
            replay=replay_basis(neutral_replay),
            stress_basis=focused_stress_basis,
            loop_implication=True,
        ),
        motif_row(
            motif_id="phase_coupled_generator_extractor_implication",
            motif_classification="source_backed_phase_coupling_implication",
            source_basis=[
                source_reference(
                    sources["n28_primary_generative_candidate_probe"],
                    "n28_primary_generative_candidate_probe",
                    "n28_i4_row_primary_generative_candidate",
                ),
                source_reference(
                    sources["n28_primary_extractive_contrast_probe"],
                    "n28_primary_extractive_contrast_probe",
                    "n28_i4b_row_primary_extractive_contrast",
                ),
                source_reference(transition, "n28_regime_boundary_transition_matrix"),
                source_reference(closeout, "n28_closeout_and_n29_handoff"),
            ],
            ecology_demand_served=[
                "future_phase_coupled_exchange_cycle_design",
                "generator_extractor_composition_seed",
                "gain_loss_timing_without_resource_economy_claim",
            ],
            supplied_capability=(
                "Generative and extractive regimes are both source-backed under the same "
                "policy family, and N28 records a same-policy transition surface."
            ),
            bridge_motif="generator_leg_plus_extractor_leg_phase_coupling_implication",
            geometric_read=(
                "The generative leg increases neighboring capacity while the extractive "
                "leg decreases it; I14 records that their contrast can seed a future "
                "phase-coupled exchange probe, but it does not synchronize them here."
            ),
            downstream_probe_suggested=(
                "Later compose a generator and extractor in ordered phase, then verify "
                "that one leg's changed medium state conditions the other without "
                "averaging away the regime distinction."
            ),
            status="source_backed_implication_future_runtime_composition_required",
            claim_ceiling="phase_coupled_generator_extractor_implication_not_resource_economy",
            remaining_debt=[
                "phase relation not run",
                "ordered gain/loss dependency not run",
                "resource economy and coordinated exchange claims blocked",
            ],
            visualization_case=None,
            replay=None,
            stress_basis={
                "transition_source": source_reference(transition, "n28_regime_boundary_transition_matrix"),
                "same_policy_transition_surface_supported": transition["transition_summary"][
                    "boundary_interpretation"
                ],
                "new_source_current_evidence_opened": transition["transition_summary"][
                    "new_source_current_evidence_opened"
                ],
                "label_mismatch_count": transition["transition_summary"]["label_mismatch_count"],
                "thresholds_retuned_for_transition": transition["transition_summary"][
                    "thresholds_retuned_for_transition"
                ],
            },
            loop_implication=True,
        ),
    ]

    prototype_d_summary = {
        "prototype_family": "generative_extractive_medium_reshaping",
        "motif_count": len(motifs),
        "motif_ids": [row["motif_id"] for row in motifs],
        "n28_final_ge_ladder_rung": closeout["final_ge_ladder_rung"],
        "n28_final_closeout_rung": closeout["final_n28_closeout_rung"],
        "n28_ready_for_n29": closeout["ready_for_n29"],
        "n28_ge5_or_stronger_supported": closeout["ge5_or_stronger_supported"],
        "n28_ge6_or_stronger_supported": closeout["ge6_or_stronger_supported"],
        "broad_margin_robustness_supported": closeout["broad_margin_robustness_supported"],
        "order_of_magnitude_robustness_supported": closeout[
            "order_of_magnitude_robustness_supported"
        ],
        "visualization_caveat": visualization["conservation_caveat"],
        "global_total_coherence_invariance_audited": visualization[
            "global_total_coherence_invariance_audited"
        ],
        "n29_i13x_ready_for_iteration_14": i13x["prototype_c_synthesis"][
            "ready_for_iteration_14"
        ],
        "n29_i8_consumption_role": "orientation_index_only",
        "claim_ceiling": "source_backed_environmental_exchange_motif_synthesis_with_loop_debt",
        "ready_for_iteration_15": True,
    }

    checks = [
        check("n29_i13x_ready_for_i14", prototype_d_summary["n29_i13x_ready_for_iteration_14"]),
        check("n28_closeout_ready_for_n29", prototype_d_summary["n28_ready_for_n29"]),
        check("n28_ge6_handoff_present", prototype_d_summary["n28_final_ge_ladder_rung"].startswith("GE6_")),
        check("exactly_five_motifs_recorded", len(motifs) == 5),
        check("expected_motif_ids_recorded", [row["motif_id"] for row in motifs] == MOTIF_IDS),
        check(
            "all_motifs_use_source_backed_n28_basis",
            all(row["source_backed_now"] and row["source_basis"] for row in motifs),
        ),
        check(
            "loop_implications_not_promoted",
            all(
                not row["closed_loop_or_exchange_cycle_claim_allowed"]
                for row in motifs
                if row["requires_future_runtime_construction"]
            ),
        ),
        check(
            "n29_i5_i8_orientation_only",
            prototype_d_summary["n29_i8_consumption_role"] == "orientation_index_only",
        ),
        check(
            "visualization_total_coherence_caveat_preserved",
            "does not plot or audit global total-coherence invariance"
            in prototype_d_summary["visualization_caveat"],
        ),
        check("broad_margin_not_overclaimed", not prototype_d_summary["broad_margin_robustness_supported"]),
        check(
            "order_of_magnitude_margin_not_overclaimed",
            not prototype_d_summary["order_of_magnitude_robustness_supported"],
        ),
        check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_FLAGS.values())),
    ]

    data: dict[str, Any] = {
        "artifact_id": "n29_generative_extractive_medium_reshaping_i14",
        "experiment_id": "N29",
        "title": "Prototype D I14 Generative / Extractive Medium Reshaping Motif Synthesis",
        "iteration": "I14",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_prototype_d_five_motif_synthesis_with_loop_debt",
        "source_artifacts": [
            source_artifact(source_id, SOURCE_PATHS[source_id], parsed)
            for source_id, parsed in sources.items()
        ],
        "prototype_d_summary": prototype_d_summary,
        "motif_rows": motifs,
        "claim_boundary": {
            "unsafe_claim_flags": UNSAFE_FLAGS,
            "n28_may_consume_as": closeout["n29_handoff"]["n29_may_consume_as"],
            "n28_must_not_consume_as": closeout["n29_handoff"]["n29_must_not_consume_as"],
        },
        "checks": checks,
        "script_sha256": sha256_file(ROOT / SCRIPT_RELATIVE_PATH),
    }
    data["checks"].append(check("no_absolute_paths_in_records", no_absolute_paths(data)))
    data["failed_checks"] = [row["check_id"] for row in data["checks"] if not row["passed"]]
    if data["failed_checks"]:
        data["status"] = "failed"
        data["acceptance_state"] = "failed_prototype_d_five_motif_synthesis"
        data["prototype_d_summary"]["ready_for_iteration_15"] = False
    return finalize(data)


def write_report(path: Path, data: dict[str, Any]) -> None:
    summary = data["prototype_d_summary"]
    lines = [
        f"# {data['title']}",
        "",
        f"Status: `{data['status']}`",
        "",
        f"Acceptance state: `{data['acceptance_state']}`",
        "",
        f"Output digest: `{data['output_digest']}`",
        "",
        "## Read",
        "",
        "I14 admits N28 generative/extractive medium-reshaping evidence as five "
        "ecology bridge motifs. It does not run a new environmental loop and it "
        "does not claim a resource economy, coordinated exchange cycle, cooperation, "
        "exploitation, altruism, biological agency, or ecology runtime.",
        "",
        f"Claim ceiling: `{summary['claim_ceiling']}`",
        "",
        f"N28 closeout rung: `{summary['n28_final_closeout_rung']}`",
        "",
        f"N28 GE rung: `{summary['n28_final_ge_ladder_rung']}`",
        "",
        f"Visualization caveat: {summary['visualization_caveat']}",
        "",
        "## Motifs",
        "",
        "| Motif | Classification | Status | Future Runtime Needed | Claim Ceiling |",
        "|---|---|---|---|---|",
    ]
    for row in data["motif_rows"]:
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                row["motif_id"],
                row["motif_classification"],
                row["runtime_or_reconstruction_status"],
                str(row["requires_future_runtime_construction"]).lower(),
                row["claim_ceiling"],
            )
        )
    lines.extend(
        [
            "",
            "## Loop Boundary",
            "",
            "The neutral circulation and phase-coupled generator/extractor rows are "
            "future composition implications. They remain below closed-loop or "
            "resource-economy claims until a later runtime construction proves ordered "
            "source-current dependency and passes replay/order controls.",
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "|---|---|",
        ]
    )
    for row in data["checks"]:
        lines.append(f"| `{row['check_id']}` | `{str(row['passed']).lower()}` |")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    data = build_motifs()
    write_json(OUT, data)
    write_report(REPORT, data)


if __name__ == "__main__":
    main()
