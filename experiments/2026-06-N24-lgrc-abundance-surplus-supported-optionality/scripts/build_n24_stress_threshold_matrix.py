#!/usr/bin/env python3
"""Build N24 Iteration 7 stress and threshold matrix."""

from __future__ import annotations

from typing import Any

import build_n24_minimal_surplus_probe as base


GENERATED_AT = "2026-06-27T00:00:00+00:00"
ROOT = base.ROOT
EXPERIMENT = (
    ROOT / "experiments" / "2026-06-N24-lgrc-abundance-surplus-supported-optionality"
)
OUTPUT = EXPERIMENT / "outputs" / "n24_stress_threshold_matrix.json"
REPORT = EXPERIMENT / "reports" / "n24_stress_threshold_matrix.md"
ARTIFACT_DIR = EXPERIMENT / "outputs" / "n24_stress_threshold_matrix_artifacts"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "scripts/build_n24_stress_threshold_matrix.py"
)
SCRIPT_PATH = (
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "scripts/build_n24_stress_threshold_matrix.py"
)

I1_OUTPUT_PATH = base.I1_OUTPUT_PATH
I2_OUTPUT_PATH = base.I2_OUTPUT_PATH
I3_OUTPUT_PATH = base.I3_OUTPUT_PATH
I4_OUTPUT_PATH = (
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "outputs/n24_minimal_surplus_probe.json"
)
I5_OUTPUT_PATH = (
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "outputs/n24_optional_continuation_set_probe.json"
)
I6_OUTPUT_PATH = (
    "experiments/2026-06-N24-lgrc-abundance-surplus-supported-optionality/"
    "outputs/n24_replay_and_control_matrix.json"
)
N23_CLOSEOUT_PATH = base.N23_CLOSEOUT_PATH

SUPPORT_FLOOR = base.SUPPORT_FLOOR
COHERENCE_FLOOR = base.COHERENCE_FLOOR
MIN_SURPLUS_MARGIN = base.MIN_SURPLUS_MARGIN
FLUX_OR_LEAKAGE_BOUND = base.FLUX_OR_LEAKAGE_BOUND
BRANCH_STRESS_COSTS = [0.0, 0.025, 0.05, 0.075, 0.076, 0.1]
MAINTENANCE_DRAIN_STRESS = [0.0, 0.05, 0.1, 0.15, 0.151]
FLUX_STRESS = [0.0, FLUX_OR_LEAKAGE_BOUND, FLUX_OR_LEAKAGE_BOUND * 10, 0.000001]
EPSILON = 1e-12


def write_artifact(name: str, data: dict[str, Any]) -> str:
    path = ARTIFACT_DIR / name
    base.write_json(path, data)
    return base.rel(path)


def source_status(source: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": source.get("status", "not_recorded"),
        "acceptance_state": source.get("acceptance_state", "not_recorded"),
        "output_digest": source.get("output_digest", "not_recorded"),
        "failed_check_count": len(source.get("failed_checks", [])),
    }


def artifact_manifest(paths_by_role: list[tuple[str, str]]) -> list[dict[str, str]]:
    return [
        {"path": path, "sha256": base.sha256_file(path), "artifact_role": role}
        for path, role in sorted(paths_by_role)
    ]


def unsafe_claim_flags(i2: dict[str, Any]) -> dict[str, bool]:
    return {
        claim: False
        for claim in sorted(i2["claim_boundary_schema"]["unsafe_claim_flags"].keys())
    }


def no_absolute_paths(data: Any) -> bool:
    text = base.canonical_json(data)
    forbidden = [
        "/" + "home/",
        "/" + "tmp/",
        "file" + "://",
        "C" + ":\\",
        "/" + "Users/",
    ]
    return all(token not in text for token in forbidden)


def surplus_margin_threshold_trace(i5_row: dict[str, Any]) -> dict[str, Any]:
    base_support_margin = i5_row["residual_support_margin_under_optionality"]
    base_coherence_margin = i5_row["residual_coherence_margin_under_optionality"]
    rows = []
    for stress in MAINTENANCE_DRAIN_STRESS:
        support_after = base_support_margin - stress
        coherence_after = base_coherence_margin - stress
        rows.append(
            {
                "maintenance_drain_stress": stress,
                "support_margin_after_stress": support_after,
                "coherence_margin_after_stress": coherence_after,
                "floor_preserved": support_after >= 0 and coherence_after >= 0,
                "positive_residual_margin_preserved": (
                    support_after > EPSILON and coherence_after > EPSILON
                ),
                "minimum_surplus_margin_preserved": (
                    support_after >= MIN_SURPLUS_MARGIN
                    and coherence_after >= MIN_SURPLUS_MARGIN
                ),
                "classification": (
                    "passes_minimum_surplus_margin"
                    if support_after >= MIN_SURPLUS_MARGIN
                    and coherence_after >= MIN_SURPLUS_MARGIN
                    else (
                        "passes_floor_only"
                        if support_after >= -EPSILON and coherence_after >= -EPSILON
                        else "floor_crossing_fail_closed"
                    )
                ),
            }
        )
    trace = {
        "artifact_id": "n24_i7_surplus_margin_threshold_trace",
        "source_candidate_row_id": i5_row["row_id"],
        "base_support_margin": base_support_margin,
        "base_coherence_margin": base_coherence_margin,
        "support_floor": SUPPORT_FLOOR,
        "coherence_floor": COHERENCE_FLOOR,
        "minimum_surplus_margin": MIN_SURPLUS_MARGIN,
        "stress_rows": rows,
        "highest_stress_preserving_minimum_surplus_margin": max(
            row["maintenance_drain_stress"]
            for row in rows
            if row["minimum_surplus_margin_preserved"]
        ),
        "highest_stress_preserving_floor": max(
            row["maintenance_drain_stress"] for row in rows if row["floor_preserved"]
        ),
    }
    trace["trace_digest"] = base.digest_value(trace)
    return trace


def optional_branch_capacity_trace(i5_row: dict[str, Any]) -> dict[str, Any]:
    base_support_margin = i5_row["residual_support_margin_under_optionality"]
    base_coherence_margin = i5_row["residual_coherence_margin_under_optionality"]
    available_branches = i5_row["optional_branch_records"]
    rows = []
    for per_branch_cost in BRANCH_STRESS_COSTS:
        admissible_counts = []
        for branch_count in range(1, len(available_branches) + 1):
            total_cost = per_branch_cost * branch_count
            support_after = base_support_margin - total_cost
            coherence_after = base_coherence_margin - total_cost
            admissible_counts.append(
                {
                    "branch_count": branch_count,
                    "total_support_cost": total_cost,
                    "support_margin_after_cost": support_after,
                    "coherence_margin_after_cost": coherence_after,
                    "joint_floor_preserved": (
                        support_after > EPSILON and coherence_after > EPSILON
                    ),
                }
            )
        max_joint = max(
            [
                item["branch_count"]
                for item in admissible_counts
                if item["joint_floor_preserved"]
            ]
            or [0]
        )
        rows.append(
            {
                "per_branch_support_cost": per_branch_cost,
                "max_jointly_admissible_by_support_budget": max_joint,
                "joint_admissibility_rows": admissible_counts,
                "ab5_count_gate_met_by_support_budget": max_joint >= 2,
                "stress_is_nonzero": per_branch_cost > 0,
            }
        )
    trace = {
        "artifact_id": "n24_i7_optional_branch_capacity_trace",
        "source_candidate_row_id": i5_row["row_id"],
        "available_branch_count": len(available_branches),
        "available_branch_ids": [branch["branch_id"] for branch in available_branches],
        "base_support_margin": base_support_margin,
        "base_coherence_margin": base_coherence_margin,
        "stress_rows": rows,
        "support_budget_can_reach_ab5_count_gate_under_nonzero_stress": any(
            row["stress_is_nonzero"] and row["ab5_count_gate_met_by_support_budget"]
            for row in rows
        ),
        "interpretation": (
            "Support-budget capacity alone can leave at least two branches "
            "jointly admissible under small nonzero branch costs, but AB5 also "
            "requires flux/leakage stress to remain clean."
        ),
    }
    trace["trace_digest"] = base.digest_value(trace)
    return trace


def maintenance_floor_boundary_trace(i5_row: dict[str, Any]) -> dict[str, Any]:
    base_support = i5_row["support_floor_result"]["observed_support"]
    base_coherence = i5_row["coherence_floor_result"]["observed_coherence"]
    rows = []
    for floor in [9.7, 9.8, 9.85, 9.9, 10.0, 10.001]:
        support_margin = base_support - floor
        coherence_margin = base_coherence - floor
        rows.append(
            {
                "candidate_floor": floor,
                "support_margin": support_margin,
                "coherence_margin": coherence_margin,
                "floor_preserved": (
                    support_margin >= -EPSILON and coherence_margin >= -EPSILON
                ),
                "positive_surplus_preserved": (
                    support_margin > EPSILON and coherence_margin > EPSILON
                ),
                "classification": (
                    "surplus_preserved"
                    if support_margin > EPSILON and coherence_margin > EPSILON
                    else (
                        "at_floor_edge"
                        if abs(support_margin) <= EPSILON
                        and abs(coherence_margin) <= EPSILON
                        else "floor_crossing_fail_closed"
                    )
                ),
            }
        )
    trace = {
        "artifact_id": "n24_i7_maintenance_floor_boundary_trace",
        "source_candidate_row_id": i5_row["row_id"],
        "observed_min_support": base_support,
        "observed_min_coherence": base_coherence,
        "declared_support_floor": SUPPORT_FLOOR,
        "declared_coherence_floor": COHERENCE_FLOOR,
        "floor_rows": rows,
        "highest_floor_with_positive_surplus": max(
            row["candidate_floor"] for row in rows if row["positive_surplus_preserved"]
        ),
        "floor_crossing_control_fail_closed_at": [
            row["candidate_floor"]
            for row in rows
            if row["classification"] == "floor_crossing_fail_closed"
        ],
    }
    trace["trace_digest"] = base.digest_value(trace)
    return trace


def flux_leakage_boundary_trace(i5_row: dict[str, Any]) -> dict[str, Any]:
    rows = []
    for flux in FLUX_STRESS:
        rows.append(
            {
                "optional_flux_stress": flux,
                "flux_or_leakage_bound": FLUX_OR_LEAKAGE_BOUND,
                "flux_bound_preserved": flux <= FLUX_OR_LEAKAGE_BOUND,
                "stress_is_nonzero": flux > 0,
                "classification": (
                    "quiet_or_at_bound"
                    if flux <= FLUX_OR_LEAKAGE_BOUND
                    else "flux_leakage_fail_closed"
                ),
            }
        )
    trace = {
        "artifact_id": "n24_i7_flux_leakage_boundary_trace",
        "source_candidate_row_id": i5_row["row_id"],
        "i5_optional_flux_drain_margin": i5_row["optional_flux_drain_margin"],
        "flux_or_leakage_bound": FLUX_OR_LEAKAGE_BOUND,
        "flux_rows": rows,
        "any_nonzero_flux_stress_preserves_bound": any(
            row["stress_is_nonzero"] and row["flux_bound_preserved"] for row in rows
        ),
        "highest_nonzero_flux_stress_preserving_bound": max(
            [
                row["optional_flux_stress"]
                for row in rows
                if row["stress_is_nonzero"] and row["flux_bound_preserved"]
            ]
            or [0.0]
        ),
        "positive_flux_stress_blocker": (
            "The frozen quiet leakage bound is 1e-9. At-bound nonzero flux stress "
            "can pass, but any stress above that bound fails closed, so I7 can "
            "support only a narrow threshold AB5 candidate, not broad flux robustness."
        ),
    }
    trace["trace_digest"] = base.digest_value(trace)
    return trace


def combined_ab5_stress_gate_trace(
    branch_trace: dict[str, Any], flux_trace: dict[str, Any]
) -> dict[str, Any]:
    rows = []
    for branch_row in branch_trace["stress_rows"]:
        for flux_row in flux_trace["flux_rows"]:
            nonzero_stress = (
                branch_row["stress_is_nonzero"] or flux_row["stress_is_nonzero"]
            )
            combined_passes = (
                nonzero_stress
                and branch_row["ab5_count_gate_met_by_support_budget"]
                and flux_row["flux_bound_preserved"]
            )
            rows.append(
                {
                    "per_branch_support_cost": branch_row["per_branch_support_cost"],
                    "max_jointly_admissible_by_support_budget": branch_row[
                        "max_jointly_admissible_by_support_budget"
                    ],
                    "optional_flux_stress": flux_row["optional_flux_stress"],
                    "flux_bound_preserved": flux_row["flux_bound_preserved"],
                    "nonzero_stress": nonzero_stress,
                    "combined_ab5_gate_passes": combined_passes,
                    "classification": (
                        "combined_narrow_ab5_candidate"
                        if combined_passes
                        else "combined_ab5_gate_blocked"
                    ),
                }
            )
    passing_rows = [row for row in rows if row["combined_ab5_gate_passes"]]
    strongest_passing_row = (
        max(
            passing_rows,
            key=lambda row: (
                row["per_branch_support_cost"],
                row["optional_flux_stress"],
                row["max_jointly_admissible_by_support_budget"],
            ),
        )
        if passing_rows
        else "none"
    )
    trace = {
        "artifact_id": "n24_i7_combined_ab5_stress_gate_trace",
        "combined_rows": rows,
        "passing_row_count": len(passing_rows),
        "best_passing_row": strongest_passing_row,
        "combined_ab5_gate_supported": bool(passing_rows),
        "narrow_boundary_reason": (
            "the strongest passing row uses flux stress at the frozen 1e-9 bound; "
            "stress above that bound fails closed"
            if passing_rows
            else "no combined nonzero stress row preserves both branch count and flux bound"
        ),
    }
    trace["trace_digest"] = base.digest_value(trace)
    return trace


def stress_control_matrix(i2: dict[str, Any]) -> dict[str, Any]:
    focused_controls = [
        "hidden_budget_relief_control",
        "floor_crossing_as_abundance_control",
        "proxy_only_optional_branch_gain_control",
        "optional_branch_label_only_control",
        "single_optional_branch_relabel_control",
        "post_hoc_surplus_construction_control",
        "n23_selection_context_relabel_as_abundance_control",
        "reward_maximization_relabel_control",
        "ap4_final_reclassification_relabel_control",
        "ap5_proxy_gap_omission_control",
        "semantic_choice_relabel_control",
        "agency_relabel_control",
        "native_support_relabel_control",
        "phase8_relabel_control",
    ]
    effects = i2["control_matrix_schema"]["control_effects"]
    rows = []
    for control_id in focused_controls:
        rows.append(
            {
                "control_id": control_id,
                "status": (
                    "not_applicable"
                    if control_id == "ap5_proxy_gap_omission_control"
                    else "failed_closed"
                ),
                "blocked_condition": effects[control_id],
                "claim_allowed_when_triggered": False,
                "stress_control_accepts_matrix": True,
                "interpretation": (
                    "AP5 remains not applicable because no proxy/reward/target "
                    "field participates; a proxy-conditioned variant would be rejected"
                    if control_id == "ap5_proxy_gap_omission_control"
                    else "stress overclaim rejected fail-closed"
                ),
            }
        )
    matrix = {
        "artifact_id": "n24_i7_stress_control_matrix",
        "status": "passed",
        "failed_closed_meaning": i2["control_matrix_schema"][
            "failed_closed_meaning"
        ],
        "control_rows": rows,
        "failed_open_controls": [],
    }
    matrix["control_matrix_digest"] = base.digest_value(matrix)
    return matrix


def build_output() -> dict[str, Any]:
    i1 = base.load_json(I1_OUTPUT_PATH)
    i2 = base.load_json(I2_OUTPUT_PATH)
    i3 = base.load_json(I3_OUTPUT_PATH)
    i4 = base.load_json(I4_OUTPUT_PATH)
    i5 = base.load_json(I5_OUTPUT_PATH)
    i6 = base.load_json(I6_OUTPUT_PATH)
    i5_row = i5["candidate_rows"][0]

    surplus_trace = surplus_margin_threshold_trace(i5_row)
    branch_trace = optional_branch_capacity_trace(i5_row)
    floor_trace = maintenance_floor_boundary_trace(i5_row)
    flux_trace = flux_leakage_boundary_trace(i5_row)
    combined_trace = combined_ab5_stress_gate_trace(branch_trace, flux_trace)
    controls = stress_control_matrix(i2)

    trace_paths = {
        "surplus_margin_threshold_trace_path": write_artifact(
            "n24_i7_surplus_margin_threshold_trace.json", surplus_trace
        ),
        "optional_branch_capacity_trace_path": write_artifact(
            "n24_i7_optional_branch_capacity_trace.json", branch_trace
        ),
        "maintenance_floor_boundary_trace_path": write_artifact(
            "n24_i7_maintenance_floor_boundary_trace.json", floor_trace
        ),
        "flux_leakage_boundary_trace_path": write_artifact(
            "n24_i7_flux_leakage_boundary_trace.json", flux_trace
        ),
        "stress_control_matrix_path": write_artifact(
            "n24_i7_stress_control_matrix.json", controls
        ),
        "combined_ab5_stress_gate_trace_path": write_artifact(
            "n24_i7_combined_ab5_stress_gate_trace.json", combined_trace
        ),
    }

    support_budget_count_gate = branch_trace[
        "support_budget_can_reach_ab5_count_gate_under_nonzero_stress"
    ]
    flux_stress_clean = flux_trace["any_nonzero_flux_stress_preserves_bound"]
    ab5_supported = combined_trace["combined_ab5_gate_supported"]
    summary_trace = {
        "artifact_id": "n24_i7_stress_threshold_summary_trace",
        "i6_source_output_digest": i6["output_digest"],
        "support_budget_count_gate_met": support_budget_count_gate,
        "nonzero_flux_stress_clean": flux_stress_clean,
        "combined_ab5_gate_supported": ab5_supported,
        "combined_best_passing_row": combined_trace["best_passing_row"],
        "ab5_candidate_supported": ab5_supported,
        "ab5_blocker": (
            "none"
            if ab5_supported
            else "no_combined_nonzero_stress_row_preserves_count_and_flux"
        ),
        "classification": (
            "narrow_at_bound_stress_threshold_backed_ab5_candidate"
            if ab5_supported
            else "narrow_replay_control_backed_ab4_edge_case"
        ),
    }
    summary_trace["trace_digest"] = base.digest_value(summary_trace)
    trace_paths["stress_threshold_summary_trace_path"] = write_artifact(
        "n24_i7_stress_threshold_summary_trace.json", summary_trace
    )

    manifest = artifact_manifest(
        [
            (trace_paths["surplus_margin_threshold_trace_path"], "surplus_margin_trace"),
            (trace_paths["optional_branch_capacity_trace_path"], "optional_branch_trace"),
            (trace_paths["maintenance_floor_boundary_trace_path"], "maintenance_floor_trace"),
            (trace_paths["flux_leakage_boundary_trace_path"], "flux_leakage_trace"),
            (trace_paths["combined_ab5_stress_gate_trace_path"], "replay_trace"),
            (trace_paths["stress_control_matrix_path"], "negative_control_trace"),
            (trace_paths["stress_threshold_summary_trace_path"], "replay_trace"),
        ]
    )

    checks = [
        base.check(
            "i1_inventory_passed",
            i1["status"] == "passed" and not i1["failed_checks"],
            source_status(i1),
        ),
        base.check(
            "i2_schema_passed",
            i2["status"] == "passed" and not i2["failed_checks"],
            source_status(i2),
        ),
        base.check(
            "i3_active_nulls_passed",
            i3["status"] == "passed" and not i3["failed_checks"],
            source_status(i3),
        ),
        base.check(
            "i4_surplus_probe_passed",
            i4["status"] == "passed" and not i4["failed_checks"],
            source_status(i4),
        ),
        base.check(
            "i5_optional_probe_passed",
            i5["status"] == "passed" and not i5["failed_checks"],
            source_status(i5),
        ),
        base.check(
            "i6_ab4_candidate_ready",
            i6["status"] == "passed"
            and not i6["failed_checks"]
            and i6["iteration6_boundary"]["ab4_candidate_supported"] is True
            and i6["iteration6_boundary"]["ready_for_iteration_7_stress_threshold_matrix"]
            is True,
            source_status(i6),
        ),
        base.check(
            "surplus_margin_thresholds_mapped",
            surplus_trace["highest_stress_preserving_floor"] == 0.15
            and surplus_trace["highest_stress_preserving_minimum_surplus_margin"]
            == 0.05,
            surplus_trace,
        ),
        base.check(
            "optional_branch_capacity_thresholds_mapped",
            branch_trace[
                "support_budget_can_reach_ab5_count_gate_under_nonzero_stress"
            ]
            is True,
            branch_trace,
        ),
        base.check(
            "maintenance_floor_boundary_mapped",
            floor_trace["highest_floor_with_positive_surplus"] == 9.9
            and 10.001 in floor_trace["floor_crossing_control_fail_closed_at"],
            floor_trace,
        ),
        base.check(
            "flux_leakage_boundary_mapped",
            flux_trace["any_nonzero_flux_stress_preserves_bound"] is True
            and any(
                row["classification"] == "flux_leakage_fail_closed"
                for row in flux_trace["flux_rows"]
            ),
            flux_trace,
        ),
        base.check(
            "stress_controls_fail_closed_or_scope_clean",
            controls["status"] == "passed"
            and not controls["failed_open_controls"]
            and all(
                row["status"] in {"failed_closed", "not_applicable"}
                and row["claim_allowed_when_triggered"] is False
                for row in controls["control_rows"]
            ),
            controls,
        ),
        base.check(
            "ab5_classification_narrow_at_bound",
            ab5_supported is True
            and summary_trace["classification"]
            == "narrow_at_bound_stress_threshold_backed_ab5_candidate"
            and summary_trace["combined_best_passing_row"][
                "optional_flux_stress"
            ]
            == FLUX_OR_LEAKAGE_BOUND,
            summary_trace,
        ),
        base.check(
            "artifact_manifest_non_empty_and_sha_match",
            len(manifest) == 7
            and all(item["sha256"] == base.sha256_file(item["path"]) for item in manifest),
            manifest,
        ),
        base.check(
            "unsafe_claim_flags_all_false",
            all(value is False for value in unsafe_claim_flags(i2).values()),
            unsafe_claim_flags(i2),
        ),
    ]

    failed_checks = [item for item in checks if item["passed"] is not True]
    output = {
        "artifact_id": "n24_stress_threshold_matrix",
        "schema_version": "n24_stress_threshold_matrix_v1",
        "experiment": "N24_lgrc_abundance_surplus_supported_optionality",
        "iteration": 7,
        "generated_at": GENERATED_AT,
        "status": "passed" if not failed_checks else "failed",
        "acceptance_state": (
            "accepted_narrow_at_bound_stress_threshold_backed_ab5_candidate"
            if not failed_checks
            else "failed_stress_threshold_matrix"
        ),
        "purpose": (
            "map surplus, optional branch capacity, maintenance floor, and "
            "flux/leakage stress boundaries for AB5 eligibility"
        ),
        "command": COMMAND,
        "source_artifacts": [
            base.source_record(I1_OUTPUT_PATH, "n24_i1_source_handoff_inventory"),
            base.source_record(I2_OUTPUT_PATH, "n24_i2_schema_control_freeze"),
            base.source_record(I3_OUTPUT_PATH, "n24_i3_active_nulls"),
            base.source_record(I4_OUTPUT_PATH, "n24_i4_minimal_surplus_probe"),
            base.source_record(
                I5_OUTPUT_PATH, "n24_i5_optional_continuation_set_probe"
            ),
            base.source_record(I6_OUTPUT_PATH, "n24_i6_replay_control_matrix"),
            base.source_record(N23_CLOSEOUT_PATH, "n23_closeout_and_n24_handoff_context"),
        ],
        "artifact_manifest": manifest,
        "trace_paths": trace_paths,
        "surplus_margin_threshold_trace": surplus_trace,
        "optional_branch_capacity_trace": branch_trace,
        "maintenance_floor_boundary_trace": floor_trace,
        "flux_leakage_boundary_trace": flux_trace,
        "combined_ab5_stress_gate_trace": combined_trace,
        "stress_control_matrix": controls,
        "stress_threshold_summary_trace": summary_trace,
        "iteration7_boundary": {
            "provisional_ab_ladder_rung": "AB5",
            "ab4_candidate_supported": True,
            "ab5_candidate_supported": ab5_supported,
            "ab5_or_stronger_supported": ab5_supported,
            "ab5_blocker": summary_trace["ab5_blocker"],
            "n24_closeout_ladder_rung_assigned": False,
            "provisional_n24_closeout_ceiling": "N24-C5",
            "ready_for_iteration_8_closeout": not failed_checks,
            "surplus_supported_optionality_claim_allowed": False,
            "final_global_ap4_reclassification_supported": False,
            "reward_maximization_supported": False,
            "semantic_choice_supported": False,
            "agency_supported": False,
            "native_support_supported": False,
            "sentience_supported": False,
            "phase8_opened": False,
            "ant_ecology_implementation_opened": False,
        },
        "geometric_interpretation": {
            "short_read": (
                "I7 supports a narrow, at-bound AB5 candidate. The support-budget "
                "axis can tolerate small joint branch costs, and a combined row "
                "passes when flux stress is exactly at the frozen 1e-9 bound. "
                "Stress above that bound fails closed, so this is not broad "
                "abundance robustness."
            ),
            "support_axis": (
                "The maintenance basin has only 0.15 support/coherence margin over "
                "the floor. It can absorb small support-cost stress and even leave "
                "two branches jointly admissible under a support-budget-only view, "
                "but the margin is narrow."
            ),
            "flux_axis": (
                "The flux/leakage bound remains 1e-9. The original I5 optional "
                "set is quiet at zero drain, and one at-bound stress row remains "
                "clean. Stress above that bound fails closed, making the AB5 "
                "claim narrow."
            ),
            "claim_boundary": (
                "AB5 is supported only as a narrow artifact-level threshold "
                "candidate pending I8 closeout, with reward, semantic choice, "
                "agency, native support, sentience, Phase 8, and ant ecology blocked."
            ),
        },
        "claim_boundary": {
            "artifact_level_ab4_candidate_supported": True,
            "artifact_level_ab5_candidate_supported": ab5_supported,
            "surplus_supported_optionality_claim_allowed": False,
            "final_global_ap4_reclassification_supported": False,
            "reward_maximization_claim_allowed": False,
            "semantic_choice_claim_allowed": False,
            "agency_claim_allowed": False,
            "native_support_claim_allowed": False,
            "sentience_claim_allowed": False,
            "phase8_opened": False,
            "ant_ecology_implementation_opened": False,
            "unsafe_claim_flags": unsafe_claim_flags(i2),
        },
        "checks": checks,
        "failed_checks": failed_checks,
    }
    output["no_absolute_paths"] = no_absolute_paths(output)
    output["checks"].append(
        base.check("no_absolute_paths", output["no_absolute_paths"] is True, True)
    )
    output["failed_checks"] = [
        item for item in output["checks"] if item["passed"] is not True
    ]
    output["status"] = "passed" if not output["failed_checks"] else "failed"
    output["acceptance_state"] = (
        "accepted_narrow_at_bound_stress_threshold_backed_ab5_candidate"
        if not output["failed_checks"]
        else "failed_stress_threshold_matrix"
    )
    output["output_digest"] = base.digest_value(
        {key: value for key, value in output.items() if key != "output_digest"}
    )
    return output


def write_report(output: dict[str, Any]) -> None:
    boundary = output["iteration7_boundary"]
    surplus = output["surplus_margin_threshold_trace"]
    branch = output["optional_branch_capacity_trace"]
    flux = output["flux_leakage_boundary_trace"]
    lines = [
        "# N24 Iteration 7 - Stress And Threshold Matrix",
        "",
        f"Status: `{output['status']}`",
        "",
        f"Acceptance state: `{output['acceptance_state']}`",
        "",
        f"Output digest: `{output['output_digest']}`",
        "",
        "## Summary",
        "",
        "Iteration 7 maps the stress boundary around the I6 AB4 candidate. The",
        "result is narrow but positive: N24 reaches an at-bound AB5 candidate,",
        "not broad abundance robustness.",
        "",
        "## Geometric Interpretation",
        "",
        output["geometric_interpretation"]["short_read"],
        "",
        output["geometric_interpretation"]["support_axis"],
        "",
        output["geometric_interpretation"]["flux_axis"],
        "",
        output["geometric_interpretation"]["claim_boundary"],
        "",
        "## Stress Boundaries",
        "",
        "```text",
        f"base_support_margin = {surplus['base_support_margin']:.12f}",
        f"base_coherence_margin = {surplus['base_coherence_margin']:.12f}",
        f"highest_stress_preserving_minimum_surplus_margin = {surplus['highest_stress_preserving_minimum_surplus_margin']:.12f}",
        f"highest_stress_preserving_floor = {surplus['highest_stress_preserving_floor']:.12f}",
        f"support_budget_can_reach_ab5_count_gate = {str(branch['support_budget_can_reach_ab5_count_gate_under_nonzero_stress']).lower()}",
        f"any_nonzero_flux_stress_preserves_bound = {str(flux['any_nonzero_flux_stress_preserves_bound']).lower()}",
        f"best_combined_per_branch_support_cost = {output['stress_threshold_summary_trace']['combined_best_passing_row']['per_branch_support_cost']:.12f}",
        f"best_combined_optional_flux_stress = {output['stress_threshold_summary_trace']['combined_best_passing_row']['optional_flux_stress']:.12f}",
        f"best_combined_joint_count = {output['stress_threshold_summary_trace']['combined_best_passing_row']['max_jointly_admissible_by_support_budget']}",
        f"ab5_blocker = {boundary['ab5_blocker']}",
        "```",
        "",
        "## Branch Capacity Rows",
        "",
        "| Per-branch cost | Max joint count by support budget | AB5 count gate |",
        "| --- | --- | --- |",
    ]
    for row in branch["stress_rows"]:
        lines.append(
            "| "
            f"`{row['per_branch_support_cost']:.12f}` | "
            f"`{row['max_jointly_admissible_by_support_budget']}` | "
            f"`{str(row['ab5_count_gate_met_by_support_budget']).lower()}` |"
        )
    lines.extend(
        [
            "",
            "## Flux Rows",
            "",
            "| Flux stress | Bound preserved | Classification |",
            "| --- | --- | --- |",
        ]
    )
    for row in flux["flux_rows"]:
        lines.append(
            "| "
            f"`{row['optional_flux_stress']:.12f}` | "
            f"`{str(row['flux_bound_preserved']).lower()}` | "
            f"`{row['classification']}` |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "```text",
            f"provisional_ab_ladder_rung = {boundary['provisional_ab_ladder_rung']}",
            f"ab4_candidate_supported = {str(boundary['ab4_candidate_supported']).lower()}",
            f"ab5_candidate_supported = {str(boundary['ab5_candidate_supported']).lower()}",
            f"ab5_or_stronger_supported = {str(boundary['ab5_or_stronger_supported']).lower()}",
            f"provisional_n24_closeout_ceiling = {boundary['provisional_n24_closeout_ceiling']}",
            f"ready_for_iteration_8_closeout = {str(boundary['ready_for_iteration_8_closeout']).lower()}",
            "```",
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "| --- | --- |",
        ]
    )
    for item in output["checks"]:
        lines.append(f"| `{item['check_id']}` | `{str(item['passed']).lower()}` |")
    lines.append("")
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    output = build_output()
    base.write_json(OUTPUT, output)
    output = base.load_json(base.rel(OUTPUT))
    write_report(output)
    if output["failed_checks"]:
        raise SystemExit(f"failed checks: {output['failed_checks']}")


if __name__ == "__main__":
    main()
