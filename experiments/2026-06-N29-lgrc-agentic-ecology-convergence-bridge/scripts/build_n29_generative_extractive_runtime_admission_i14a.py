#!/usr/bin/env python3
"""Build N29 I14-A Prototype D runtime admission schema."""

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
    "build_n29_generative_extractive_runtime_admission_i14a.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

SOURCE_PATHS = {
    "n29_i10_prototype_admission_schema": EXPERIMENT
    / "outputs"
    / "n29_prototype_admission_schema_i10.json",
    "n29_i14_prototype_d_motif_synthesis": EXPERIMENT
    / "outputs"
    / "n29_generative_extractive_medium_reshaping_i14.json",
    "n28_closeout_and_n29_handoff": N28 / "outputs" / "n28_closeout_and_n29_handoff.json",
    "n28_replay_capacity_attribution_matrix": N28
    / "outputs"
    / "n28_replay_capacity_attribution_matrix.json",
    "n28_stress_regime_separation_matrix": N28
    / "outputs"
    / "n28_stress_regime_separation_matrix.json",
    "n28_focused_margin_variant_stress_envelope": N28
    / "outputs"
    / "n28_focused_margin_variant_stress_envelope.json",
    "n28_generative_extractive_visualization": N28
    / "outputs"
    / "n28_generative_extractive_visualization.json",
}

OUT = EXPERIMENT / "outputs" / "n29_generative_extractive_runtime_admission_i14a.json"
REPORT = EXPERIMENT / "reports" / "n29_generative_extractive_runtime_admission_i14a.md"

DIRECT_RUNTIME_MOTIFS = [
    {
        "iteration_target": "I14.1",
        "motif_id": "generative_enrichment_motif",
        "runtime_target": "generative_enrichment_runtime_prototype",
        "evidence_lane": "direct_runtime_motif",
        "positive_evidence_shape": (
            "focal basin remains above declared support/coherence/stability floors "
            "while neighboring capacity, support, distinguishability, or boundary "
            "metrics increase in source-current runtime traces"
        ),
        "blocked_overclaims": [
            "resource economy",
            "cooperation",
            "biological agency",
            "semantic construction",
        ],
    },
    {
        "iteration_target": "I14.2",
        "motif_id": "extractive_depletion_motif",
        "runtime_target": "extractive_depletion_runtime_prototype",
        "evidence_lane": "direct_runtime_motif",
        "positive_evidence_shape": (
            "focal basin remains above declared support/coherence/stability floors "
            "while neighboring capacity is depleted, flattened, or made less "
            "basin-forming in source-current runtime traces"
        ),
        "blocked_overclaims": [
            "exploitation",
            "selective uptake",
            "resource consumption",
            "biological agency",
        ],
    },
    {
        "iteration_target": "I14.3",
        "motif_id": "processor_redistribution_motif",
        "runtime_target": "processor_redistribution_runtime_prototype",
        "evidence_lane": "direct_runtime_motif",
        "positive_evidence_shape": (
            "focal basin remains bounded while one local region loses capacity and "
            "another gains capacity under one declared source-current runtime policy"
        ),
        "blocked_overclaims": [
            "intentional processing",
            "tool use",
            "resource routing economy",
            "semantic action",
        ],
    },
]

COMPOSITION_ATTEMPT_MOTIFS = [
    {
        "iteration_target": "I14.4",
        "motif_id": "neutral_circulation_implication",
        "runtime_target": "neutral_circulation_composition_attempt",
        "evidence_lane": "composition_attempt",
        "ordered_dependency_requirements": [
            "leg_a_changes_local_capacity_distribution",
            "leg_b_consumes_leg_a_changed_distribution_as_source_current_input",
            "leg_b_returns_or_redirects_capacity_along_reverse_or_complementary_arc",
            "later_leg_a_side_state_depends_on_leg_b_changed_distribution",
        ],
        "blocked_overclaims": [
            "closed circulation loop before ordered dependency",
            "resource economy",
            "coordinated exchange cycle",
            "cooperation",
        ],
    },
    {
        "iteration_target": "I14.5",
        "motif_id": "phase_coupled_generator_extractor_implication",
        "runtime_target": "phase_coupled_generator_extractor_composition_attempt",
        "evidence_lane": "composition_attempt",
        "ordered_dependency_requirements": [
            "generative_leg_remains_generative",
            "extractive_leg_remains_extractive",
            "phase_relation_is_source_current",
            "gain_loss_timing_or_location_is_conditioned_by_prior_leg_state",
            "neither_leg_is_relabelled_as_the_other",
        ],
        "blocked_overclaims": [
            "coordinated exchange cycle before phase dependency",
            "resource economy",
            "cooperation",
            "exploitation",
        ],
    },
]

REQUIRED_RUNTIME_ROW_FIELDS = [
    "runtime_row_id",
    "iteration_target",
    "motif_id",
    "evidence_lane",
    "source_motif_digest",
    "source_schema_digest_validation",
    "source_current_inputs",
    "runtime_artifact_manifest",
    "runtime_config_digest",
    "producer_visibility_record",
    "threshold_record",
    "thresholds_declared_before_use",
    "focal_basin_stability_trace",
    "neighbor_or_medium_capacity_trace",
    "regime_classification_trace",
    "capacity_attribution_trace",
    "merge_leakage_trace",
    "leakage_interpretation_record",
    "visualization_manifest_refs",
    "visualization_caveat",
    "control_results",
    "replay_requirements",
    "stress_requirements",
    "claim_ceiling",
    "unsafe_claim_flags",
    "why_not_stronger",
]

DIRECT_CONTROL_IDS = [
    "prototype_d_label_only_medium_reshaping_control",
    "prototype_d_report_only_as_runtime_control",
    "prototype_d_visual_only_as_runtime_control",
    "prototype_d_focal_survival_only_control",
    "prototype_d_aggregate_only_redistribution_control",
    "prototype_d_hidden_producer_state_control",
    "prototype_d_n28_relabel_as_n29_runtime_control",
    "prototype_d_resource_economy_relabel_control",
    "prototype_d_cooperation_exploitation_relabel_control",
    "prototype_d_total_coherence_visualization_overclaim_control",
]

COMPOSITION_CONTROL_IDS = [
    "prototype_d_order_inversion_control",
    "prototype_d_missing_feedback_leg_control",
    "prototype_d_label_only_circulation_control",
    "prototype_d_hidden_producer_coupling_control",
    "prototype_d_regime_averaging_control",
    "prototype_d_merge_leakage_as_cycle_control",
    "prototype_d_resource_economy_relabel_control",
    "prototype_d_closed_loop_promotion_control",
]

BLOCKED_CURRENT_CLAIMS = [
    "runtime_prototype_supported",
    "closed_environmental_circulation_loop",
    "resource_economy",
    "coordinated_exchange_cycle",
    "agentic_ecology_runtime",
    "cooperation",
    "exploitation",
    "altruism",
    "biological_agency",
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


def control_rows(control_ids: list[str], target_lane: str) -> list[dict[str, Any]]:
    return [
        {
            "control_id": control_id,
            "target_lane": target_lane,
            "control_status": "frozen_required_for_future_rows",
            "expected_result_when_triggered": "failed_closed",
            "claim_allowed_when_triggered": False,
            "rung_effect": "blocks_runtime_support_or_demotes_to_debt_record",
        }
        for control_id in control_ids
    ]


def build_target_rows(i14: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    motif_by_id = {row["motif_id"]: row for row in i14["motif_rows"]}
    direct_rows = []
    for spec in DIRECT_RUNTIME_MOTIFS:
        motif = motif_by_id[spec["motif_id"]]
        direct_rows.append(
            {
                **spec,
                "source_motif_claim_ceiling": motif["claim_ceiling"],
                "source_motif_runtime_status": motif["runtime_or_reconstruction_status"],
                "source_motif_requires_future_runtime_construction": motif[
                    "requires_future_runtime_construction"
                ],
                "runtime_claim_allowed_before_i14b_i14c": False,
                "eligible_for_runtime_candidate_after_schema": True,
                "requires_i14b_controls": True,
                "requires_i14c_replay_stress": True,
                "allowed_current_claim": "runtime_admission_target_only_no_positive_runtime_evidence",
                "claim_ceiling": "direct_runtime_prototype_candidate_pending_controls_replay_stress",
            }
        )
    composition_rows = []
    for spec in COMPOSITION_ATTEMPT_MOTIFS:
        motif = motif_by_id[spec["motif_id"]]
        composition_rows.append(
            {
                **spec,
                "source_motif_claim_ceiling": motif["claim_ceiling"],
                "source_motif_runtime_status": motif["runtime_or_reconstruction_status"],
                "source_motif_requires_future_runtime_construction": motif[
                    "requires_future_runtime_construction"
                ],
                "loop_or_exchange_cycle_claim_allowed_before_i14d_i14e": False,
                "eligible_for_runtime_candidate_after_schema": False,
                "eligible_for_composition_attempt_after_schema": True,
                "requires_i14d_controls": True,
                "requires_i14e_replay_stress": True,
                "allowed_current_claim": "composition_attempt_target_only_no_loop_evidence",
                "claim_ceiling": "composition_attempt_pending_ordered_dependency_controls_replay_stress",
            }
        )
    return direct_rows, composition_rows


def build_schema() -> dict[str, Any]:
    sources = {source_id: load_json(path) for source_id, path in SOURCE_PATHS.items()}
    i10 = sources["n29_i10_prototype_admission_schema"]
    i14 = sources["n29_i14_prototype_d_motif_synthesis"]
    n28_closeout = sources["n28_closeout_and_n29_handoff"]
    n28_visual = sources["n28_generative_extractive_visualization"]
    direct_targets, composition_targets = build_target_rows(i14)
    i14_source_digests = {
        row["source_id"]: row["output_digest"] for row in i14["source_artifacts"]
    }

    runtime_admission_schema = {
        "schema_id": "n29_i14a_prototype_d_runtime_admission_schema",
        "schema_scope": "Prototype D runtime admission only; no runtime evidence opened",
        "source_i10_output_digest": i10["output_digest"],
        "source_i14_output_digest": i14["output_digest"],
        "source_n28_closeout_output_digest": n28_closeout["output_digest"],
        "runtime_evidence_opened": False,
        "positive_runtime_rows_created": False,
        "source_current_runtime_required": True,
        "derived_report_only_blocks_runtime_support": True,
        "n29_i5_i8_orientation_only": True,
        "n28_relabel_as_n29_runtime_blocks_support": True,
        "visualization_caveat": n28_visual["conservation_caveat"],
        "global_total_coherence_invariance_audited": n28_visual[
            "global_total_coherence_invariance_audited"
        ],
        "required_runtime_row_fields": REQUIRED_RUNTIME_ROW_FIELDS,
        "required_field_policy": {
            "missing_required_field_effect": "blocks_runtime_support",
            "missing_artifact_manifest_effect": "blocks_runtime_support",
            "missing_threshold_record_effect": "blocks_runtime_support",
            "thresholds_declared_after_result_effect": "blocks_runtime_support",
            "unsafe_claim_flag_true_effect": "blocks_runtime_support",
            "not_run_control_or_replay_effect": "blocks_dependent_runtime_claim",
            "failed_open_control_effect": "invalidates_runtime_row",
        },
        "threshold_policy": {
            "row_specific_thresholds_required_before_use": True,
            "motif_specific_thresholds_allowed": True,
            "thresholds_may_not_be_retuned_to_make_label_pass": True,
            "thresholds_may_not_widen_n28_claim_ceiling": True,
            "future_threshold_record_required_fields": [
                "threshold_name",
                "threshold_value",
                "declared_before_use",
                "measurement_source",
                "pass_fail_relation",
                "why_threshold_is_motif_specific_not_retuned",
            ],
        },
        "producer_policy": {
            "producer_allowed_if_same_discipline_as_n05_n28": True,
            "producer_visibility_required": True,
            "hidden_producer_state_blocks_support": True,
            "producer_success_cannot_upgrade_native": True,
            "producer_schedule_must_be_declared_before_use": True,
            "future_producer_record_required_fields": [
                "producer_visibility_record",
                "producer_policy_id",
                "producer_declared_before_use",
                "producer_residue",
                "producer_success_can_upgrade_native",
            ],
        },
        "visualization_policy": {
            "visuals_allowed_as_diagnostic_context": True,
            "visuals_cannot_replace_source_current_runtime_trace": True,
            "total_coherence_visualization_caveat_required": True,
            "global_total_coherence_checksum_required_if_claimed": True,
        },
        "replay_policy": {
            "direct_runtime_required_replay_modes": [
                "artifact_replay",
                "snapshot_load_replay",
                "duplicate_replay",
            ],
            "composition_required_replay_modes": [
                "artifact_replay",
                "snapshot_load_replay",
                "duplicate_replay",
                "order_inversion_control",
                "feedback_removed_or_phase_broken_control",
            ],
            "duplicate_second_emit_false_means_duplicate_suppression_when_digest_stable": True,
            "not_run_blocks_dependent_runtime_claim": True,
        },
        "stress_policy": {
            "direct_runtime_stress_required_before_candidate_close": True,
            "composition_stress_required_before_loop_claim": True,
            "broad_margin_robustness_must_not_be_inferred_from_n28": True,
            "order_of_magnitude_robustness_must_not_be_inferred_from_n28": True,
        },
        "direct_runtime_targets": direct_targets,
        "composition_attempt_targets": composition_targets,
        "direct_control_schema": control_rows(DIRECT_CONTROL_IDS, "direct_runtime_motif"),
        "composition_control_schema": control_rows(COMPOSITION_CONTROL_IDS, "composition_attempt"),
        "ready_for_i14_1": True,
        "ready_for_i14_2": True,
        "ready_for_i14_3": True,
        "ready_for_i14_4": True,
        "ready_for_i14_5": True,
        "claim_ceiling": "prototype_d_runtime_admission_schema_only_no_runtime_support",
    }

    checks = [
        check("i10_prototype_schema_passed", i10["status"] == "passed"),
        check("i14_motif_synthesis_passed", i14["status"] == "passed"),
        check("i14_has_five_motifs", i14["prototype_d_summary"]["motif_count"] == 5),
        check("n28_closeout_ready_for_n29", n28_closeout["ready_for_n29"]),
        check(
            "schema_only_no_runtime_support",
            not runtime_admission_schema["runtime_evidence_opened"]
            and not runtime_admission_schema["positive_runtime_rows_created"],
        ),
        check("runtime_evidence_not_opened", not runtime_admission_schema["runtime_evidence_opened"]),
        check("positive_runtime_rows_not_created", not runtime_admission_schema["positive_runtime_rows_created"]),
        check("direct_target_count_is_three", len(direct_targets) == 3),
        check("composition_target_count_is_two", len(composition_targets) == 2),
        check(
            "direct_targets_are_exactly_I14_1_I14_2_I14_3",
            [row["iteration_target"] for row in direct_targets]
            == ["I14.1", "I14.2", "I14.3"],
        ),
        check(
            "composition_targets_are_exactly_I14_4_I14_5",
            [row["iteration_target"] for row in composition_targets]
            == ["I14.4", "I14.5"],
        ),
        check(
            "direct_lane_and_composition_lane_disjoint",
            set(row["motif_id"] for row in direct_targets).isdisjoint(
                row["motif_id"] for row in composition_targets
            ),
        ),
        check(
            "direct_targets_are_not_future_loop_implications",
            all(not row["source_motif_requires_future_runtime_construction"] for row in direct_targets),
        ),
        check(
            "composition_targets_not_eligible_for_runtime_candidate_before_controls",
            all(not row["eligible_for_runtime_candidate_after_schema"] for row in composition_targets),
        ),
        check(
            "composition_targets_keep_loop_claims_blocked",
            all(
                row["source_motif_requires_future_runtime_construction"]
                and not row["loop_or_exchange_cycle_claim_allowed_before_i14d_i14e"]
                for row in composition_targets
            ),
        ),
        check(
            "all_direct_targets_require_i14b_and_i14c",
            all(row["requires_i14b_controls"] and row["requires_i14c_replay_stress"] for row in direct_targets),
        ),
        check(
            "all_composition_targets_require_i14d_and_i14e",
            all(row["requires_i14d_controls"] and row["requires_i14e_replay_stress"] for row in composition_targets),
        ),
        check("required_runtime_fields_complete", len(REQUIRED_RUNTIME_ROW_FIELDS) == 26),
        check(
            "required_runtime_fields_cover_source_current_and_claims",
            all(
                field in REQUIRED_RUNTIME_ROW_FIELDS
                for field in [
                    "source_current_inputs",
                    "runtime_artifact_manifest",
                    "threshold_record",
                    "control_results",
                    "unsafe_claim_flags",
                    "claim_ceiling",
                ]
            ),
        ),
        check(
            "required_field_policy_blocks_missing_fields",
            runtime_admission_schema["required_field_policy"]["missing_required_field_effect"]
            == "blocks_runtime_support"
            and runtime_admission_schema["required_field_policy"]["not_run_control_or_replay_effect"]
            == "blocks_dependent_runtime_claim"
            and runtime_admission_schema["required_field_policy"]["failed_open_control_effect"]
            == "invalidates_runtime_row",
        ),
        check(
            "threshold_policy_blocks_posthoc_thresholds",
            runtime_admission_schema["threshold_policy"]["row_specific_thresholds_required_before_use"]
            and runtime_admission_schema["threshold_policy"][
                "thresholds_may_not_be_retuned_to_make_label_pass"
            ],
        ),
        check(
            "producer_policy_blocks_hidden_producer_state",
            runtime_admission_schema["producer_policy"]["producer_visibility_required"]
            and runtime_admission_schema["producer_policy"]["hidden_producer_state_blocks_support"]
            and runtime_admission_schema["producer_policy"]["producer_success_cannot_upgrade_native"],
        ),
        check(
            "visualization_caveat_blocks_visual_proof",
            runtime_admission_schema["visualization_policy"][
                "visuals_cannot_replace_source_current_runtime_trace"
            ]
            and runtime_admission_schema["visualization_policy"][
                "total_coherence_visualization_caveat_required"
            ],
        ),
        check("direct_controls_count", len(runtime_admission_schema["direct_control_schema"]) == 10),
        check(
            "aggregate_only_redistribution_control_frozen",
            any(
                row["control_id"] == "prototype_d_aggregate_only_redistribution_control"
                for row in runtime_admission_schema["direct_control_schema"]
            ),
        ),
        check(
            "source_schema_digest_validation_field_required",
            "source_schema_digest_validation" in REQUIRED_RUNTIME_ROW_FIELDS,
        ),
        check(
            "leakage_interpretation_record_field_required",
            "leakage_interpretation_record" in REQUIRED_RUNTIME_ROW_FIELDS,
        ),
        check("composition_controls_count", len(runtime_admission_schema["composition_control_schema"]) == 8),
        check(
            "visualization_caveat_preserved",
            "does not plot or audit global total-coherence invariance"
            in runtime_admission_schema["visualization_caveat"],
        ),
        check(
            "claim_boundary_blocks_resource_economy_and_cooperation",
            not UNSAFE_FLAGS["resource_economy_claim_allowed"]
            and not UNSAFE_FLAGS["cooperation_claim_allowed"]
            and "resource_economy" in BLOCKED_CURRENT_CLAIMS
            and "cooperation" in BLOCKED_CURRENT_CLAIMS,
        ),
        check(
            "source_digest_chain_i10_i14_n28_verified",
            i10["output_digest"] == runtime_admission_schema["source_i10_output_digest"]
            and i14["output_digest"] == runtime_admission_schema["source_i14_output_digest"]
            and n28_closeout["output_digest"]
            == runtime_admission_schema["source_n28_closeout_output_digest"]
            and i14_source_digests["n28_closeout_and_n29_handoff"]
            == n28_closeout["output_digest"],
        ),
        check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_FLAGS.values())),
    ]

    data: dict[str, Any] = {
        "artifact_id": "n29_generative_extractive_runtime_admission_i14a",
        "experiment_id": "N29",
        "title": "Prototype D I14-A Runtime Admission Schema",
        "iteration": "I14-A",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_prototype_d_runtime_admission_schema_no_runtime_evidence",
        "source_artifacts": [
            source_artifact(source_id, SOURCE_PATHS[source_id], parsed)
            for source_id, parsed in sources.items()
        ],
        "runtime_admission_schema": runtime_admission_schema,
        "claim_boundary": {
            "unsafe_claim_flags": UNSAFE_FLAGS,
            "maximum_allowed_current_claim": "schema_frozen_ready_for_i14_1_to_i14_5",
            "blocked_current_claims": BLOCKED_CURRENT_CLAIMS,
        },
        "checks": checks,
        "script_sha256": sha256_file(ROOT / SCRIPT_RELATIVE_PATH),
    }
    data["checks"].append(check("no_absolute_paths_in_records", no_absolute_paths(data)))
    data["failed_checks"] = [row["check_id"] for row in data["checks"] if not row["passed"]]
    if data["failed_checks"]:
        data["status"] = "failed"
        data["acceptance_state"] = "failed_prototype_d_runtime_admission_schema"
        data["runtime_admission_schema"]["ready_for_i14_1"] = False
        data["runtime_admission_schema"]["ready_for_i14_2"] = False
        data["runtime_admission_schema"]["ready_for_i14_3"] = False
        data["runtime_admission_schema"]["ready_for_i14_4"] = False
        data["runtime_admission_schema"]["ready_for_i14_5"] = False
    return finalize(data)


def write_report(path: Path, data: dict[str, Any]) -> None:
    schema = data["runtime_admission_schema"]
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
        "I14-A freezes the Prototype D runtime admission rules. It opens no runtime "
        "evidence and creates no positive runtime rows. I14.1-I14.3 are direct "
        "runtime motif targets; I14.4-I14.5 are composition attempts with stricter "
        "ordered-dependency requirements.",
        "",
        f"Claim ceiling: `{schema['claim_ceiling']}`",
        "",
        f"Runtime evidence opened: `{str(schema['runtime_evidence_opened']).lower()}`",
        "",
        "## Direct Runtime Targets",
        "",
        "| Iteration | Motif | Runtime Target | Candidate Allowed Now |",
        "|---|---|---|---|",
    ]
    for row in schema["direct_runtime_targets"]:
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` |".format(
                row["iteration_target"],
                row["motif_id"],
                row["runtime_target"],
                str(row["eligible_for_runtime_candidate_after_schema"]).lower(),
            )
        )
    lines.extend(
        [
            "",
            "## Composition Attempts",
            "",
            "| Iteration | Motif | Runtime Target | Loop/Exchange Claim Allowed Now |",
            "|---|---|---|---|",
        ]
    )
    for row in schema["composition_attempt_targets"]:
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` |".format(
                row["iteration_target"],
                row["motif_id"],
                row["runtime_target"],
                str(row["loop_or_exchange_cycle_claim_allowed_before_i14d_i14e"]).lower(),
            )
        )
    lines.extend(
        [
            "",
            "## Controls",
            "",
            f"Direct controls frozen: `{len(schema['direct_control_schema'])}`",
            "",
            f"Composition controls frozen: `{len(schema['composition_control_schema'])}`",
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
    data = build_schema()
    write_json(OUT, data)
    write_report(REPORT, data)


if __name__ == "__main__":
    main()
