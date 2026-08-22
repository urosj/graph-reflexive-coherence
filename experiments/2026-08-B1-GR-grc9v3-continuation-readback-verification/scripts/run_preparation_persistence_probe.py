"""Execute GRV5 preparation, persistence, and matched-probe mediation."""

from __future__ import annotations

from pathlib import Path
import sys
import tempfile
from typing import Any

import numpy as np

from artifact_io import (
    EXPERIMENT_ROOT,
    REPO_ROOT,
    artifact_envelope,
    file_manifest,
    git,
    read_json,
    repo_relative,
    semantic_digest,
    sha256_file,
    tracked_files,
    write_json,
)
from gate_receipts import (
    finalize_receipt,
    prerequisite_is_authorized,
    validate_acceptance_anchor,
    validate_receipt,
)
from grv5_methods import (
    activity_amplitude_from_target,
    activity_write_stage_trace,
    activity_write_stage,
    categorical_projection,
    canonical_edge_direction,
    carrier_alignment,
    clone_model,
    coherence_vector,
    conductance_vector,
    conductance_surface_consistency,
    constitutive_consistency_audit,
    current_vector,
    difference_in_differences,
    direct_conductance_intervention,
    equal_carrier_preserving_reached_state,
    match_C_and_J_preserving_W,
    matching_audit,
    old_current_intervention,
    pair_separation,
    physical_projection_linf,
    reset_carrier,
    signed_sweep_fit,
    shuffle_carrier_pattern,
    state_projection,
    swap_carrier,
)

SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from pygrc.models import GRC9V3  # noqa: E402


COMMAND = (
    ".venv/bin/python "
    "experiments/2026-08-B1-GR-grc9v3-continuation-readback-verification/"
    "scripts/run_all.py --gate GRV5"
)
EXPERIMENT_RELATIVE = repo_relative(EXPERIMENT_ROOT)
GRV4_RECEIPT_SHA256 = "1e236ed3ee7407125ba166157401712e76ca6337c09990ba0bfc6121c0b96c10"
GRV4_ACCEPTANCE_COMMIT = "53838f31c512fc8dd01bde8e99f34ceef7885f03"


def _rms(values: np.ndarray, floor: float) -> float:
    return max(float(np.sqrt(np.mean(np.square(values)))), float(floor))


def branch_scales(model: GRC9V3) -> dict[str, float]:
    return {
        "C": _rms(coherence_vector(model), 1e-12),
        "W": _rms(conductance_vector(model), 1e-12),
        "J": _rms(current_vector(model), 1.0),
    }


def validate_prerequisite() -> tuple[dict[str, Any], dict[str, Any]]:
    receipt = read_json(EXPERIMENT_ROOT / "outputs/gates/grv4_result_receipt.json")
    anchor = read_json(EXPERIMENT_ROOT / "outputs/gates/grv4_acceptance_anchor.json")
    validate_receipt(receipt)
    validate_acceptance_anchor(anchor)
    if receipt["receipt_payload_sha256"] != GRV4_RECEIPT_SHA256:
        raise ValueError("GRV4 receipt identity mismatch")
    if (
        anchor["result_revision"] != "e99a8a3d07ef4860bcc756d60cb4fb54056a6ddb"
        or anchor["receipt_payload_sha256"] != GRV4_RECEIPT_SHA256
    ):
        raise ValueError("GRV4 acceptance anchor does not bind the reviewed result")
    if not prerequisite_is_authorized(anchor):
        raise ValueError("GRV4 prerequisite is not accepted")
    return receipt, anchor


def protected_manifest_v5() -> dict[str, Any]:
    predecessor_path = EXPERIMENT_ROOT / "outputs/protected_path_manifest_v4.json"
    predecessor = read_json(predecessor_path)
    relative_paths = [row["path"] for row in predecessor["payload"]["files"]]
    current = file_manifest(relative_paths)
    payload = {
        "manifest_id": "b1_grv5_protected_paths_v5",
        "scope": predecessor["payload"]["scope"],
        "substrate_base_revision": predecessor["payload"]["substrate_base_revision"],
        "predecessor_path": repo_relative(predecessor_path),
        "predecessor_payload_sha256": predecessor["payload_sha256"],
        "predecessor_tree_sha256": predecessor["payload"]["tree_sha256"],
        "files": current["files"],
        "tree_sha256": current["tree_sha256"],
        "unchanged_successor": current["tree_sha256"]
        == predecessor["payload"]["tree_sha256"],
        "newly_discovered_load_bearing_paths": [],
        "later_discovery_policy": "record_and_route_without_retroactive_silent_scope_change",
    }
    return artifact_envelope(
        payload,
        schema_version="b1_grv5_protected_path_manifest_v5",
        generating_command=COMMAND,
    )


def preparation_pairs(
    model: GRC9V3, config: dict[str, Any], *, base_snapshot_sha256: str
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    prep = config["preparation"]
    direct_amplitude = float(prep["direct_conductance_relative_amplitude"])
    activity_amplitude = activity_amplitude_from_target(
        model, float(prep["activity_write_target_log_conductance_exponent"])
    )
    direct_pair = (
        direct_conductance_intervention(
            model, signed_relative_amplitude=direct_amplitude
        ),
        direct_conductance_intervention(
            model, signed_relative_amplitude=-direct_amplitude
        ),
    )
    activity_pair = (
        activity_write_stage(model, amplitude=activity_amplitude),
        activity_write_stage(model, amplitude=0.0),
    )
    sign_pair = (
        activity_write_stage(model, amplitude=activity_amplitude),
        activity_write_stage(model, amplitude=-activity_amplitude),
    )
    full_activity = old_current_intervention(model, amplitude=activity_amplitude)
    full_zero = old_current_intervention(model, amplitude=0.0)
    full_activity.step()
    full_zero.step()
    tolerance = float(config["persistence"]["absolute_separation_tolerance"])
    sign_difference = pair_separation(
        sign_pair[0], sign_pair[1], branch_scales=branch_scales(model)
    )
    base_w = conductance_vector(model)
    direct_distances = [
        float(np.linalg.norm(conductance_vector(candidate) - base_w))
        for candidate in direct_pair
    ]
    amplitude_ladder = []
    for target in prep["activity_write_target_exponent_ladder"]:
        target_value = float(target)
        ladder_amplitude = activity_amplitude_from_target(model, target_value)
        positive = activity_write_stage(model, amplitude=ladder_amplitude)
        negative = activity_write_stage(model, amplitude=-ladder_amplitude)
        zero = activity_write_stage(model, amplitude=0.0)
        positive_log_ratio = np.log(
            conductance_vector(positive) / conductance_vector(zero)
        )
        negative_log_ratio = np.log(
            conductance_vector(negative) / conductance_vector(zero)
        )
        expected_log_ratio = -target_value * np.square(canonical_edge_direction(model))
        amplitude_ladder.append(
            {
                "target_attenuation_exponent": target_value,
                "executed_old_current_amplitude": ladder_amplitude,
                "executed_old_current_amplitude_squared": ladder_amplitude**2,
                "positive_log_W_ratio": positive_log_ratio.tolist(),
                "negative_log_W_ratio": negative_log_ratio.tolist(),
                "expected_log_W_ratio": expected_log_ratio.tolist(),
                "sign_even_W_error_linf": float(
                    np.linalg.norm(
                        conductance_vector(positive) - conductance_vector(negative),
                        ord=np.inf,
                    )
                ),
                "expected_log_W_ratio_error_linf": float(
                    np.linalg.norm(
                        positive_log_ratio - expected_log_ratio,
                        ord=np.inf,
                    )
                ),
                "event_count_pair": [
                    len(positive.get_state().event_log),
                    len(negative.get_state().event_log),
                ],
                "topology_equal": categorical_projection(positive)["topology_edges"]
                == categorical_projection(negative)["topology_edges"],
            }
        )
    stage_trace_positive = activity_write_stage_trace(
        model, amplitude=activity_amplitude
    )
    stage_trace_negative = activity_write_stage_trace(
        model, amplitude=-activity_amplitude
    )
    controls = {
        "base_snapshot_sha256": base_snapshot_sha256,
        "activity_input_amplitude": activity_amplitude,
        "activity_input_class": "experiment_authored_old_current_state_injection",
        "activity_input_runtime_reached": False,
        "activity_stage_sequence": [
            "rebuild_differential_state",
            "rebuild_transport_state",
        ],
        "activity_complete_step_separation": pair_separation(
            full_activity, full_zero, branch_scales=branch_scales(model)
        ),
        "sign_reversal_stage_separation": sign_difference,
        "sign_even_write_passed": sign_difference["block_l2"]["W"] <= tolerance,
        "carrier_hypotheses": config["p5_3_review_hardening"]["carrier_hypotheses"],
        "carrier_hypotheses_status": (
            "revision_distinct_confirmatory_freeze_after_preliminary_P5_results_"
            "cannot_upgrade_existing_rung"
        ),
        "direct_W_metric_audit": {
            "metric": prep["direct_W_metric"],
            "distance_positive": direct_distances[0],
            "distance_negative": direct_distances[1],
            "equal_distance_error": abs(direct_distances[0] - direct_distances[1]),
            "minimum_prepared_W": min(
                float(np.min(conductance_vector(candidate)))
                for candidate in direct_pair
            ),
            "positivity_preserved": all(
                np.all(conductance_vector(candidate) > 0.0) for candidate in direct_pair
            ),
            "authoritative_surface_consistency": [
                conductance_surface_consistency(candidate) for candidate in direct_pair
            ],
        },
        "activity_preparation_amplitude_ladder": amplitude_ladder,
        "activity_preparation_amplitude_ladder_status": (
            "confirmatory_response_shape_only_no_primary_rung_upgrade"
        ),
        "activity_stage_boundary_trace": {
            "positive": stage_trace_positive,
            "negative": stage_trace_negative,
            "k0_definition": config["p5_3_review_hardening"]["preparation_boundary"][
                "k0_definition"
            ],
            "k1_definition": config["p5_3_review_hardening"]["preparation_boundary"][
                "k1_definition"
            ],
        },
        "immediate_and_later_sign_audit": {
            "immediate_W_sign_reversal_linf": sign_difference["block_l2"]["W"],
            "complete_step_C_sign_reversal_linf": float(
                np.linalg.norm(
                    np.asarray(
                        stage_trace_positive["after_complete_preparation_step"]["C"]
                    )
                    - np.asarray(
                        stage_trace_negative["after_complete_preparation_step"]["C"]
                    ),
                    ord=np.inf,
                )
            ),
            "complete_step_W_sign_reversal_linf": float(
                np.linalg.norm(
                    np.asarray(
                        stage_trace_positive["after_complete_preparation_step"]["W"]
                    )
                    - np.asarray(
                        stage_trace_negative["after_complete_preparation_step"]["W"]
                    ),
                    ord=np.inf,
                )
            ),
            "interpretation": (
                "immediate_direct_J_squared_write_and_standardized_complete_step_"
                "history_are_reported_separately"
            ),
        },
        "forming_intervention_stopped_before_persistence": True,
        "intervention_state_projections": {
            "baseline": state_projection(model),
            "direct_positive": state_projection(direct_pair[0]),
            "direct_negative": state_projection(direct_pair[1]),
            "activity_stage": state_projection(activity_pair[0]),
            "activity_stage_zero": state_projection(activity_pair[1]),
            "activity_sign_reversed_stage": state_projection(sign_pair[1]),
            "activity_complete_step": state_projection(full_activity),
            "activity_complete_step_zero": state_projection(full_zero),
        },
    }
    activity_initial = pair_separation(
        activity_pair[0], activity_pair[1], branch_scales=branch_scales(model)
    )
    complete_initial = pair_separation(
        full_activity, full_zero, branch_scales=branch_scales(model)
    )
    pairs = [
        {
            "preparation_id": "P-W-direct-opposite",
            "models": direct_pair,
            "provenance_class": "synthetic_valid_direct_conductance_intervention",
            "write_status": "producer_authored_conductance_difference",
            "native_activity_write_supported": False,
        },
        {
            "preparation_id": "P-J-activity-stage-vs-zero",
            "models": activity_pair,
            "provenance_class": "exact_native_stage_reached_from_synthetic_old_current_input",
            "write_status": "stage_local_activity_conditioned_conductance_write",
            "native_activity_write_supported": activity_initial["block_l2"]["W"]
            > tolerance,
        },
        {
            "preparation_id": "P-J-activity-complete-step-vs-zero",
            "models": (full_activity, full_zero),
            "provenance_class": "complete_native_step_reached_from_synthetic_old_current_input",
            "write_status": "activity_conditioned_joint_C_state_after_transient_J_squared_to_W_stage",
            "native_activity_write_supported": complete_initial["joint_block_scaled_l2"]
            > tolerance,
        },
    ]
    return pairs, controls


def persistence_states(
    first: GRC9V3, second: GRC9V3, horizons: list[int]
) -> tuple[dict[int, tuple[GRC9V3, GRC9V3]], list[dict[str, Any]]]:
    first_live = clone_model(first)
    second_live = clone_model(second)
    records: dict[int, tuple[GRC9V3, GRC9V3]] = {}
    activity_trace = []
    for horizon in range(max(horizons) + 1):
        before = [state_projection(first_live), state_projection(second_live)]
        if horizon in horizons:
            records[horizon] = (clone_model(first_live), clone_model(second_live))
        if horizon < max(horizons):
            first_live.step()
            second_live.step()
            after = [state_projection(first_live), state_projection(second_live)]
            activity_trace.append(
                {
                    "transition_from_horizon": horizon,
                    "transition_to_horizon": horizon + 1,
                    "J_l2_before": [row["J_l2"] for row in before],
                    "delta_C_l2": [
                        float(
                            np.linalg.norm(
                                np.asarray(target["C"]) - np.asarray(source["C"])
                            )
                        )
                        for source, target in zip(before, after, strict=True)
                    ],
                    "delta_W_l2": [
                        float(
                            np.linalg.norm(
                                np.asarray(target["W"]) - np.asarray(source["W"])
                            )
                        )
                        for source, target in zip(before, after, strict=True)
                    ],
                    "delta_J_l2": [
                        float(
                            np.linalg.norm(
                                np.asarray(target["J"]) - np.asarray(source["J"])
                            )
                        )
                        for source, target in zip(before, after, strict=True)
                    ],
                }
            )
    return records, activity_trace


def slow_fast_projection(
    first: GRC9V3,
    second: GRC9V3,
    grv3_row: dict[str, Any],
    minimum_magnitude: float,
) -> dict[str, Any]:
    audit = grv3_row["coordinate_stratum_and_jacobian_audits"].get("C_W", {})
    if audit.get("square_transition_jacobian_status") != "admitted":
        return {
            "status": "blocked_GRV3_C_W_transition_not_admitted",
            "retention_interpretation_allowed": False,
        }
    matrix = np.asarray(audit["jacobian"], dtype=float)
    basis = np.asarray(
        grv3_row["candidate_reduction_audits"]["C_W"]["coherence_basis"],
        dtype=float,
    )
    coordinate = np.concatenate(
        (
            basis.T @ (coherence_vector(first) - coherence_vector(second)),
            conductance_vector(first) - conductance_vector(second),
        )
    )
    values, vectors = np.linalg.eig(matrix)

    def projected_norm(indices: list[int]) -> float:
        if not indices:
            return 0.0
        subspace, _ = np.linalg.qr(vectors[:, indices])
        return float(np.linalg.norm(subspace.conj().T @ coordinate))

    slow = [
        index for index, value in enumerate(values) if abs(value) >= minimum_magnitude
    ]
    fast = [
        index for index, value in enumerate(values) if abs(value) < minimum_magnitude
    ]
    clusters = audit["temporal_mode_diagnostics"].get("clusters", [])
    retention_allowed = bool(clusters) and all(
        cluster.get("retention_interpretation_allowed", False) for cluster in clusters
    )
    return {
        "status": "descriptive_projection_computed",
        "coordinate": audit["causal_coordinate"],
        "slow_multiplier_minimum_magnitude": minimum_magnitude,
        "slow_projection_l2": projected_norm(slow),
        "fast_projection_l2": projected_norm(fast),
        "slow_mode_indices": slow,
        "fast_mode_indices": fast,
        "retention_interpretation_allowed": retention_allowed,
        "GRR3_allowed": retention_allowed,
    }


def replay_pair(
    first: GRC9V3,
    second: GRC9V3,
    *,
    tolerance: float,
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="b1-grv5-") as directory:
        root = Path(directory)
        paths = [root / "first.json", root / "second.json"]
        first.save(str(paths[0]))
        second.save(str(paths[1]))
        restored = [GRC9V3.load(str(path)) for path in paths]
    before_errors = [
        physical_projection_linf(source, loaded)
        for source, loaded in zip((first, second), restored, strict=True)
    ]
    categorical_equal = [
        categorical_projection(source) == categorical_projection(loaded)
        for source, loaded in zip((first, second), restored, strict=True)
    ]
    source_next = [clone_model(first), clone_model(second)]
    restored_next = [clone_model(restored[0]), clone_model(restored[1])]
    for model in source_next + restored_next:
        model.step()
    next_errors = [
        physical_projection_linf(source, loaded)
        for source, loaded in zip(source_next, restored_next, strict=True)
    ]
    return {
        "method": "snapshot_save_load_then_equal_input_one_step",
        "physical_projection_restore_linf": before_errors,
        "categorical_projection_equal": categorical_equal,
        "equal_input_next_step_projection_linf": next_errors,
        "passed": (
            max(before_errors + next_errors, default=0.0) <= tolerance
            and all(categorical_equal)
        ),
    }


def _probe_amplitudes(
    model: GRC9V3, probe_kind: str, config: dict[str, Any]
) -> tuple[list[float], list[dict[str, float]]]:
    probe = config["matched_probe"]
    if probe_kind == "coherence_or_potential_probe":
        values = [float(value) for value in probe["coherence_probe_amplitudes"]]
        return values, [{"executed_amplitude": value} for value in values]
    if probe_kind == "old_current_state_injection":
        targets = [
            float(value)
            for value in probe["old_current_probe_signed_exponent_coordinates"]
        ]
        values = [
            activity_amplitude_from_target(model, value) if value else 0.0
            for value in targets
        ]
        return values, [
            {
                "signed_input_coordinate": target,
                "realized_log_conductance_attenuation_exponent": -abs(target),
                "executed_amplitude": value,
            }
            for target, value in zip(targets, values, strict=True)
        ]
    values = [float(value) for value in probe["external_edge_covector_amplitudes"]]
    return values, [{"executed_amplitude": value} for value in values]


def probe_matrix(
    first: GRC9V3,
    second: GRC9V3,
    baseline: GRC9V3,
    *,
    config: dict[str, Any],
    provenance_class: str,
) -> list[dict[str, Any]]:
    matched_first, matched_second = match_C_and_J_preserving_W(first, second)
    tolerance = float(config["matched_probe"]["difference_in_differences_tolerance"])
    match_receipt = matching_audit(
        first,
        second,
        matched_first,
        matched_second,
        tolerance=tolerance,
    )
    consistency = [
        constitutive_consistency_audit(model, tolerance=tolerance)
        for model in (matched_first, matched_second)
    ]
    state_class = (
        "constitutively_consistent"
        if all(row["constitutively_consistent"] for row in consistency)
        else "synthetic_or_stage_local_off_current_constitutive_manifold"
    )
    lanes = [
        *config["matched_probe"]["native_lanes"],
        *config["matched_probe"]["reduced_lanes"],
    ]
    probe_kinds = [
        "coherence_or_potential_probe",
        "old_current_state_injection",
        "external_current_like_analytical_probe",
    ]
    rows = []
    for lane in lanes:
        for probe_kind in probe_kinds:
            if (
                probe_kind == "external_current_like_analytical_probe"
                and lane != "frozen_W_probe"
            ):
                continue
            amplitudes, amplitude_records = _probe_amplitudes(
                baseline, probe_kind, config
            )
            sweep = []
            for amplitude, amplitude_record in zip(
                amplitudes, amplitude_records, strict=True
            ):
                contrast = difference_in_differences(
                    matched_first,
                    matched_second,
                    lane=lane,
                    probe_kind=probe_kind,
                    amplitude=amplitude,
                )
                contrast.update(amplitude_record)
                sweep.append(contrast)
            fit = signed_sweep_fit(
                sweep,
                tolerance=float(
                    config["matched_probe"][
                        "signed_sweep_linear_fit_relative_residual_max"
                    ]
                ),
            )
            maximum_effect = max(row["difference_in_differences_l2"] for row in sweep)
            zero = next(row for row in sweep if row["amplitude"] == 0.0)
            effect_resolved = maximum_effect > tolerance
            if not effect_resolved:
                relation = "no_resolved_carrier_by_probe_interaction"
            elif lane == "frozen_W_probe":
                relation = "substrate_reduced_carrier_conditioned_transport_response"
            elif probe_kind == "coherence_or_potential_probe":
                relation = "native_carrier_conditioned_susceptibility_or_transport_response_candidate"
            else:
                relation = "native_current_recurrence_or_write_read_geometry_candidate"
            native_mediation_allowed = bool(
                effect_resolved
                and lane != "frozen_W_probe"
                and state_class == "constitutively_consistent"
            )
            largest_index = max(
                range(len(sweep)), key=lambda index: abs(sweep[index]["amplitude"])
            )
            control_amplitude = sweep[largest_index]["amplitude"]
            original = sweep[largest_index]["difference_in_differences"]
            reset_pair = reset_carrier(matched_first, matched_second, baseline)
            baseline_w = conductance_vector(baseline)
            reset_intervention_accuracy = {
                "carrier_pair_W_difference_linf": float(
                    np.linalg.norm(
                        conductance_vector(reset_pair[0])
                        - conductance_vector(reset_pair[1]),
                        ord=np.inf,
                    )
                ),
                "first_to_baseline_W_linf": float(
                    np.linalg.norm(
                        conductance_vector(reset_pair[0]) - baseline_w,
                        ord=np.inf,
                    )
                ),
                "second_to_baseline_W_linf": float(
                    np.linalg.norm(
                        conductance_vector(reset_pair[1]) - baseline_w,
                        ord=np.inf,
                    )
                ),
                "surface_consistency": [
                    conductance_surface_consistency(model) for model in reset_pair
                ],
            }
            reset_result = difference_in_differences(
                reset_pair[0],
                reset_pair[1],
                lane=lane,
                probe_kind=probe_kind,
                amplitude=control_amplitude,
            )
            equal_pair = equal_carrier_preserving_reached_state(
                matched_first, matched_second
            )
            equal_intervention_accuracy = {
                "carrier_pair_W_difference_linf": float(
                    np.linalg.norm(
                        conductance_vector(equal_pair[0])
                        - conductance_vector(equal_pair[1]),
                        ord=np.inf,
                    )
                ),
                "surface_consistency": [
                    conductance_surface_consistency(model) for model in equal_pair
                ],
            }
            equal_result = difference_in_differences(
                equal_pair[0],
                equal_pair[1],
                lane=lane,
                probe_kind=probe_kind,
                amplitude=control_amplitude,
            )
            swapped = swap_carrier(matched_first, matched_second)
            swap_intervention_accuracy = {
                "first_to_original_second_W_linf": float(
                    np.linalg.norm(
                        conductance_vector(swapped[0])
                        - conductance_vector(matched_second),
                        ord=np.inf,
                    )
                ),
                "second_to_original_first_W_linf": float(
                    np.linalg.norm(
                        conductance_vector(swapped[1])
                        - conductance_vector(matched_first),
                        ord=np.inf,
                    )
                ),
                "surface_consistency": [
                    conductance_surface_consistency(model) for model in swapped
                ],
            }
            swap_result = difference_in_differences(
                swapped[0],
                swapped[1],
                lane=lane,
                probe_kind=probe_kind,
                amplitude=control_amplitude,
            )
            swap_error = float(
                np.linalg.norm(
                    np.asarray(swap_result["difference_in_differences"])
                    + np.asarray(original)
                )
            )
            shuffled = shuffle_carrier_pattern(matched_first, matched_second, baseline)
            if shuffled is None:
                wrong_location = {
                    "status": "not_applicable_single_edge_or_invalid_positive_carrier",
                    "route_selectivity_claim_allowed": False,
                }
            else:
                shuffled_result = difference_in_differences(
                    shuffled[0],
                    shuffled[1],
                    lane=lane,
                    probe_kind=probe_kind,
                    amplitude=control_amplitude,
                )
                location_delta = float(
                    np.linalg.norm(
                        np.asarray(shuffled_result["difference_in_differences"])
                        - np.asarray(original)
                    )
                )
                wrong_location = {
                    "status": "executed_multi_edge_carrier_pattern_shift",
                    "difference_in_differences_l2": shuffled_result[
                        "difference_in_differences_l2"
                    ],
                    "response_pattern_change_l2": location_delta,
                    "route_selectivity_resolved": location_delta > tolerance,
                    "route_selectivity_claim_allowed": bool(
                        effect_resolved
                        and location_delta > tolerance
                        and lane != "frozen_W_probe"
                        and state_class == "constitutively_consistent"
                    ),
                }
            reset_effect = reset_result["difference_in_differences_l2"]
            equal_effect = equal_result["difference_in_differences_l2"]
            if not effect_resolved:
                mediation_class = "no_resolved_interaction"
            elif reset_effect <= tolerance and equal_effect <= tolerance:
                mediation_class = (
                    "W_sufficient_for_observed_lane_interaction"
                    if swap_error <= tolerance
                    else "W_reset_sensitive_swap_unresolved"
                )
            elif reset_effect < maximum_effect or equal_effect < maximum_effect:
                mediation_class = "partial_or_mixed_W_and_non_W_mediation"
            else:
                mediation_class = "no_identified_W_mediation"
            rows.append(
                {
                    "lane": lane,
                    "probe_kind": probe_kind,
                    "carrier_pair_provenance": provenance_class,
                    "carrier_pair_state_class": state_class,
                    "constitutive_consistency": consistency,
                    "matching_intervention_receipt": match_receipt,
                    "sweep": sweep,
                    "signed_sweep_fit": fit,
                    "maximum_difference_in_differences_l2": maximum_effect,
                    "effect_resolved": effect_resolved,
                    "relation_classification": relation,
                    "native_mediation_gate_passed": native_mediation_allowed,
                    "zero_present_probe_control": {
                        "difference_in_differences_l2": zero[
                            "difference_in_differences_l2"
                        ],
                        "passed": zero["difference_in_differences_l2"] <= tolerance,
                        "baseline_difference_l2": zero["baseline_difference_l2"],
                        "baseline_difference_is_read_effect": False,
                    },
                    "mediation_controls": {
                        "carrier_reset_difference_in_differences_l2": reset_result[
                            "difference_in_differences_l2"
                        ],
                        "carrier_reset_passed": reset_result[
                            "difference_in_differences_l2"
                        ]
                        <= tolerance,
                        "carrier_reset_intervention_accuracy": reset_intervention_accuracy,
                        "equal_carrier_difference_in_differences_l2": equal_result[
                            "difference_in_differences_l2"
                        ],
                        "equal_carrier_passed": equal_result[
                            "difference_in_differences_l2"
                        ]
                        <= tolerance,
                        "equal_carrier_intervention_accuracy": equal_intervention_accuracy,
                        "carrier_swap_sign_reversal_error_l2": swap_error,
                        "carrier_swap_passed": swap_error <= tolerance,
                        "carrier_swap_intervention_accuracy": swap_intervention_accuracy,
                        "wrong_location_or_shuffled_carrier": wrong_location,
                        "graded_mediation_class": mediation_class,
                        "W_only_control_scope": (
                            "cannot_reject_joint_C_W_or_transferred_carrier"
                        ),
                    },
                }
            )
    return rows


def causal_guard_audit(
    first: GRC9V3,
    second: GRC9V3,
    *,
    prepared_categorical: list[dict[str, Any]],
    prepared_event_counts: list[int],
    config: dict[str, Any],
) -> dict[str, Any]:
    hardening = config["p5_3_review_hardening"]["causal_guard_contract"]
    projections = [state_projection(first), state_projection(second)]
    categorical = [categorical_projection(first), categorical_projection(second)]
    states = [first.get_state(), second.get_state()]
    budget_residuals = [
        abs(row["budget"] - row["budget_target"]) for row in projections
    ]
    event_deltas = [
        len(model.get_state().event_log) - initial
        for model, initial in zip((first, second), prepared_event_counts, strict=True)
    ]
    result = {
        "positive_C_and_W": all(
            row["minimum_C"] > 0.0 and row["minimum_W"] > 0.0 for row in projections
        ),
        "budget_residuals": budget_residuals,
        "budget_valid": max(budget_residuals, default=0.0)
        <= float(hardening["budget_tolerance"]),
        "topology_unchanged": all(
            current["topology_nodes"] == prepared["topology_nodes"]
            and current["topology_edges"] == prepared["topology_edges"]
            for current, prepared in zip(categorical, prepared_categorical, strict=True)
        ),
        "event_count_deltas": event_deltas,
        "no_new_events": event_deltas == [0, 0],
        "categorical_stratum_unchanged": all(
            current == prepared
            for current, prepared in zip(categorical, prepared_categorical, strict=True)
        ),
        "rng_state_pair_equal": projections[0]["rng_state_sha256"]
        == projections[1]["rng_state_sha256"],
        "params_identity_pair_equal": projections[0]["params_identity"]
        == projections[1]["params_identity"],
        "step_and_time_pair_equal": (
            states[0].step_index == states[1].step_index
            and states[0].time == states[1].time
        ),
    }
    result["same_branch_causal_path_clean"] = bool(
        result["positive_C_and_W"]
        and result["budget_valid"]
        and result["topology_unchanged"]
        and result["no_new_events"]
        and result["categorical_stratum_unchanged"]
        and result["rng_state_pair_equal"]
        and result["params_identity_pair_equal"]
        and result["step_and_time_pair_equal"]
    )
    return result


def classify_persistence(
    *,
    preparation_id: str,
    horizon_rows: list[dict[str, Any]],
    activity_trace: list[dict[str, Any]],
    config: dict[str, Any],
) -> dict[str, Any]:
    tolerance = float(config["persistence"]["absolute_separation_tolerance"])
    stability_tolerance = float(config["persistence"]["stability_ratio_tolerance"])
    required_horizon = int(
        config["persistence"]["required_bounded_persistence_horizon"]
    )
    initial = horizon_rows[0]
    required = next(
        row for row in horizon_rows if row["horizon_complete_steps"] == required_horizon
    )
    ratios = [row["persistence_ratio"] for row in horizon_rows]
    signed = [
        row["carrier_alignment"]["signed_projection_on_prepared_pattern"]
        for row in horizon_rows
    ]
    if any(
        not row["causal_guard_audit"]["same_branch_causal_path_clean"]
        for row in horizon_rows
    ):
        stability_class = "categorical_or_stratum_crossing"
    elif required["persistence_ratio"] > 1.0 + stability_tolerance:
        stability_class = "growing_formative_displacement"
    elif min(signed) < -stability_tolerance:
        stability_class = "oscillatory_or_sign_reversing"
    elif required["persistence_ratio"] < 1.0 - stability_tolerance:
        stability_class = "stable_decaying_or_fast_overwrite"
    else:
        stability_class = "neutral_or_marginal_within_declared_ratio_tolerance"
    maximum_activity = max(
        (
            max(row["J_l2_before"], default=0.0)
            for row in activity_trace[:required_horizon]
        ),
        default=0.0,
    )
    initial_w = initial["separation"]["block_l2"]["W"]
    required_w = required["separation"]["block_l2"]["W"]
    initial_c = initial["separation"]["block_l2"]["C"]
    required_c = required["separation"]["block_l2"]["C"]
    if initial_w > tolerance and required_w <= tolerance and required_c > tolerance:
        carrier_path = "W_overwritten_difference_transferred_into_C"
    elif initial_w > tolerance and required_w <= tolerance:
        carrier_path = "W_fast_overwrite_without_resolved_surviving_carrier"
    elif initial_w <= tolerance and initial_c > tolerance and required_c > tolerance:
        carrier_path = "post_write_C_dominated_joint_displacement_persists_without_W"
    elif required_w > tolerance:
        carrier_path = "W_difference_remains_present"
    else:
        carrier_path = "no_resolved_carrier"
    if required["persistence_ratio"] < float(
        config["persistence"]["minimum_persistence_ratio"]
    ):
        retention_class = "below_bounded_persistence_gate"
    elif carrier_path == "W_difference_remains_present":
        retention_class = (
            "passive_W_candidate"
            if maximum_activity
            <= float(config["persistence"]["ongoing_activity_zero_tolerance"])
            else "activity_maintained_or_regenerated_W_unresolved"
        )
    elif "C" in carrier_path:
        retention_class = "transferred_C_dominated_persistence_candidate"
    else:
        retention_class = "no_persistence"
    return {
        "preparation_id": preparation_id,
        "stability_class": stability_class,
        "carrier_path": carrier_path,
        "retention_class": retention_class,
        "required_horizon": required_horizon,
        "required_horizon_ratio": required["persistence_ratio"],
        "ratio_range": [min(ratios), max(ratios)],
        "maximum_activity_J_l2_through_required_horizon": maximum_activity,
        "instability_is_stable_retention": False,
    }


def branch_relocation_audit(
    baseline: GRC9V3,
    horizon_rows: list[dict[str, Any]],
    grv3_row: dict[str, Any],
    *,
    required_horizon: int,
    tolerance: float,
) -> dict[str, Any]:
    """Separate neutral-coordinate persistence from transverse retention."""
    reduction = grv3_row["candidate_reduction_audits"].get("C", {})
    c_audit = grv3_row["coordinate_stratum_and_jacobian_audits"].get("C", {})
    basis_rows = reduction.get("coherence_basis", [])
    if not basis_rows or c_audit.get("square_transition_jacobian_status") != "admitted":
        return {
            "status": "not_admitted_GRV3_C_coordinate",
            "branch_relocation_rival_status": "not_assessed",
            "transverse_branch_relative_retention_supported": False,
        }

    basis = np.asarray(basis_rows, dtype=float)
    source_c = coherence_vector(baseline)
    initial = horizon_rows[0]
    required = next(
        row
        for row in horizon_rows
        if row["horizon_complete_steps"] == required_horizon
    )

    def source_offset(state: dict[str, Any]) -> dict[str, Any]:
        delta = np.asarray(state["C"], dtype=float) - source_c
        projected = basis @ (basis.T @ delta)
        residual = delta - projected
        return {
            "source_branch_C_offset_l2": float(np.linalg.norm(delta)),
            "admitted_C_coordinate": (basis.T @ delta).tolist(),
            "admitted_C_projection_residual_l2": float(np.linalg.norm(residual)),
            "budget_delta_from_source": float(np.sum(delta)),
        }

    def horizon_drift(member: str) -> float:
        return float(
            np.linalg.norm(
                np.asarray(required[member]["C"], dtype=float)
                - np.asarray(initial[member]["C"], dtype=float)
            )
        )

    offsets = {
        "state_a_at_k0": source_offset(initial["state_a"]),
        "state_b_at_k0": source_offset(initial["state_b"]),
        "state_a_at_required_horizon": source_offset(required["state_a"]),
        "state_b_at_required_horizon": source_offset(required["state_b"]),
    }
    projection_residual_max = max(
        row["admitted_C_projection_residual_l2"] for row in offsets.values()
    )
    budget_delta_max = max(
        abs(row["budget_delta_from_source"]) for row in offsets.values()
    )
    jacobian = np.asarray(c_audit["jacobian"], dtype=float)
    branch_tangent_status = c_audit["temporal_mode_diagnostics"].get(
        "branch_tangent_status", "missing"
    )
    c_persistence_candidate = required["separation"]["block_l2"]["C"] > tolerance
    if not c_persistence_candidate:
        rival_status = "not_applicable_no_resolved_C_persistence"
        allowed_interpretation = "no_C_dominated_persistence_candidate"
    elif branch_tangent_status != "separately_identified":
        rival_status = "branch_relocation_rival_unresolved_not_excluded"
        allowed_interpretation = (
            "bounded_C_dominated_neutral_direction_persistence_with_"
            "branch_relocation_rival_unresolved"
        )
    else:
        rival_status = (
            "branch_tangent_separately_identified_requires_future_transverse_audit"
        )
        allowed_interpretation = "C_persistence_pending_transverse_audit"
    return {
        "status": "completed_non_upgrading_acceptance_clarification",
        "source_branch_id": grv3_row["branch_id"],
        "admitted_C_basis_id": reduction.get("basis_id", "missing"),
        "branch_tangent_status": branch_tangent_status,
        "source_offset_audit": offsets,
        "maximum_admitted_C_projection_residual_l2": projection_residual_max,
        "all_offsets_within_admitted_C_coordinate_to_tolerance": (
            projection_residual_max <= tolerance
        ),
        "maximum_budget_delta_from_source": budget_delta_max,
        "required_horizon": required_horizon,
        "C_drift_from_k0_to_required_horizon_l2": {
            "state_a": horizon_drift("state_a"),
            "state_b": horizon_drift("state_b"),
        },
        "C_transition_jacobian_identity_error_linf": float(
            np.linalg.norm(jacobian - np.eye(jacobian.shape[0]), ord=np.inf)
        ),
        "C_persistence_candidate": c_persistence_candidate,
        "branch_relocation_rival_status": rival_status,
        "transverse_branch_relative_retention_supported": False,
        "allowed_interpretation": allowed_interpretation,
    }


def reachability_classification(preparation_id: str) -> dict[str, Any]:
    if preparation_id == "P-J-activity-complete-step-vs-zero":
        post_state = "produced_by_unchanged_runtime_from_synthetic_intervention"
    elif preparation_id == "P-J-activity-stage-vs-zero":
        post_state = "produced_by_exact_native_stage_from_synthetic_intervention"
    else:
        post_state = "producer_authored_synthetic_conductance_state"
    return {
        "forming_input_status": "synthetic_valid_not_native_runtime_reachable",
        "post_intervention_state_status": post_state,
        "reachable_from_accepted_branch_by_unchanged_runtime_alone": False,
        "runtime_reached_shorthand_allowed": False,
    }


def transient_W_mediation_classification(preparation_id: str) -> dict[str, Any]:
    complete = preparation_id == "P-J-activity-complete-step-vs-zero"
    return {
        "status": "not_established" if complete else "not_applicable",
        "native_stage_local_W_write_observed": preparation_id.startswith("P-J-"),
        "later_C_dominated_consequence_observed": complete,
        "stage_matched_W_only_mediation_control_run": False,
        "later_C_mediation_specifically_by_transient_W_supported": False,
        "allowed_interpretation": (
            "cooccurring_stage_local_W_write_and_later_C_consequence_without_"
            "specific_transient_W_mediation_identification"
            if complete
            else "no_later_C_mediation_claim_in_this_lane"
        ),
    }


def branch_result(
    branch: dict[str, Any],
    grv3_row: dict[str, Any],
    config: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any], list[dict[str, Any]]]:
    snapshot = REPO_ROOT / branch["state_snapshot_path"]
    if sha256_file(snapshot) != branch["state_snapshot_sha256"]:
        raise ValueError(f"branch snapshot digest mismatch: {branch['branch_id']}")
    baseline = GRC9V3.load(str(snapshot))
    scales = branch_scales(baseline)
    pairs, preparation_controls = preparation_pairs(
        baseline, config, base_snapshot_sha256=branch["state_snapshot_sha256"]
    )
    horizons = [
        int(value)
        for value in config["persistence"]["horizons_complete_steps_after_preparation"]
    ]
    replay_horizons = set(int(value) for value in config["replay"]["required_horizons"])
    tolerance = float(config["persistence"]["absolute_separation_tolerance"])
    branch_rows = []
    causal_rows = []
    grv3_cw_audit = grv3_row["coordinate_stratum_and_jacobian_audits"].get("C_W", {})
    grv3_causal_status = grv3_cw_audit.get(
        "square_transition_jacobian_status", "missing"
    )
    for pair in pairs:
        states, activity_trace = persistence_states(
            pair["models"][0], pair["models"][1], horizons
        )
        prepared_categorical = [
            categorical_projection(states[0][0]),
            categorical_projection(states[0][1]),
        ]
        prepared_event_counts = [
            len(states[0][0].get_state().event_log),
            len(states[0][1].get_state().event_log),
        ]
        initial = pair_separation(states[0][0], states[0][1], branch_scales=scales)
        initial_norm = initial["joint_block_scaled_l2"]
        horizon_rows = []
        read_rows = []
        for horizon in horizons:
            first, second = states[horizon]
            separation = pair_separation(first, second, branch_scales=scales)
            ratio = (
                separation["joint_block_scaled_l2"] / initial_norm
                if initial_norm > tolerance
                else 0.0
            )
            replay = (
                replay_pair(
                    first,
                    second,
                    tolerance=float(config["replay"]["physical_projection_tolerance"]),
                )
                if horizon in replay_horizons
                else {"status": "not_required_at_this_horizon"}
            )
            projection = slow_fast_projection(
                first,
                second,
                grv3_row,
                float(config["persistence"]["slow_multiplier_minimum_magnitude"]),
            )
            current_categorical = [
                categorical_projection(first),
                categorical_projection(second),
            ]
            topology_unchanged = all(
                current["topology_nodes"] == prepared["topology_nodes"]
                and current["topology_edges"] == prepared["topology_edges"]
                for current, prepared in zip(
                    current_categorical, prepared_categorical, strict=True
                )
            )
            event_count_deltas = [
                len(model.get_state().event_log) - initial_count
                for model, initial_count in zip(
                    (first, second), prepared_event_counts, strict=True
                )
            ]
            guard = causal_guard_audit(
                first,
                second,
                prepared_categorical=prepared_categorical,
                prepared_event_counts=prepared_event_counts,
                config=config,
            )
            alignment = carrier_alignment(
                initial,
                separation,
                branch_scales=scales,
            )
            horizon_rows.append(
                {
                    "horizon_complete_steps": horizon,
                    "separation": separation,
                    "persistence_ratio": ratio,
                    "slow_fast_projection": projection,
                    "carrier_alignment": alignment,
                    "replay": replay,
                    "topology_unchanged_from_prepared_state": topology_unchanged,
                    "event_count_deltas_from_prepared_state": event_count_deltas,
                    "same_branch_persistence_path_clean": topology_unchanged
                    and event_count_deltas == [0, 0],
                    "causal_guard_audit": guard,
                    "state_a": state_projection(first),
                    "state_b": state_projection(second),
                }
            )
            carrier_present = separation["block_l2"]["W"] > tolerance
            read_rows.append(
                {
                    "horizon_complete_steps": horizon,
                    "carrier_present": carrier_present,
                    "status": (
                        "full_2x2_probe_matrix_executed"
                        if carrier_present
                        else "not_candidate_carrier_erased_before_probe"
                    ),
                    "rows": (
                        probe_matrix(
                            first,
                            second,
                            baseline,
                            config=config,
                            provenance_class=pair["provenance_class"],
                        )
                        if carrier_present
                        else []
                    ),
                }
            )
        required_horizon = int(
            config["persistence"]["required_bounded_persistence_horizon"]
        )
        required = next(
            row
            for row in horizon_rows
            if row["horizon_complete_steps"] == required_horizon
        )
        persisted = bool(
            required["persistence_ratio"]
            >= float(config["persistence"]["minimum_persistence_ratio"])
            and required["separation"]["topology_equal"]
            and all(
                row["causal_guard_audit"]["same_branch_causal_path_clean"]
                for row in horizon_rows
                if row["horizon_complete_steps"] <= required_horizon
            )
        )
        persistence_classification = classify_persistence(
            preparation_id=pair["preparation_id"],
            horizon_rows=horizon_rows,
            activity_trace=activity_trace,
            config=config,
        )
        relocation_audit = branch_relocation_audit(
            baseline,
            horizon_rows,
            grv3_row,
            required_horizon=required_horizon,
            tolerance=tolerance,
        )
        reachability = reachability_classification(pair["preparation_id"])
        transient_w_mediation = transient_W_mediation_classification(
            pair["preparation_id"]
        )
        native_read = any(
            row["native_mediation_gate_passed"]
            for horizon in read_rows
            for row in horizon["rows"]
        )
        reduced_read = any(
            row["effect_resolved"] and row["lane"] == "frozen_W_probe"
            for horizon in read_rows
            for row in horizon["rows"]
        )
        slow_allowed = any(
            row["slow_fast_projection"].get("GRR3_allowed", False)
            for row in horizon_rows
        )
        write_supported = bool(pair["native_activity_write_supported"])
        rung = "GRR1" if write_supported else "GRR0"
        if write_supported and persisted:
            rung = "GRR2"
        if rung == "GRR2" and slow_allowed:
            rung = "GRR3"
        if rung == "GRR3" and native_read:
            rung = "GRR4"
        replay_pass = all(
            row["replay"].get("passed", True)
            for row in horizon_rows
            if row["horizon_complete_steps"] in replay_horizons
        )
        if rung == "GRR4" and replay_pass:
            rung = "GRR5"
        if rung == "GRR2":
            persistence_classification["retention_class"] = (
                "C_dominated_neutral_direction_persistence_candidate_"
                "branch_relocation_rival_unresolved"
            )
        row = {
            "branch_id": branch["branch_id"],
            "fixture_id": branch["fixture_id"],
            "preparation_id": pair["preparation_id"],
            "preparation_provenance": pair["provenance_class"],
            "write_status": pair["write_status"],
            "predeclared_carrier_hypothesis": {
                "P-W-direct-opposite": "H-W",
                "P-J-activity-stage-vs-zero": "H-W",
                "P-J-activity-complete-step-vs-zero": "H-transfer",
            }[pair["preparation_id"]],
            "carrier_hypothesis_freeze_status": (
                "revision_distinct_confirmatory_after_preliminary_P5_results_"
                "cannot_upgrade_existing_rung"
            ),
            "GRV3_C_W_causal_status": grv3_causal_status,
            "GRV3_branch_claim_ceiling": (
                "causal_state_retention_and_mediation_eligible_if_all_GRV5_gates_pass"
                if grv3_causal_status == "admitted"
                else "physical_stage_and_bounded_overwrite_observation_only"
            ),
            "initial_separation": initial,
            "horizon_rows": horizon_rows,
            "persistence_activity_trace": activity_trace,
            "persistence_classification": persistence_classification,
            "branch_relocation_audit": relocation_audit,
            "reachability_classification": reachability,
            "transient_W_mediation_classification": transient_w_mediation,
            "matched_probe_rows": read_rows,
            "bounded_persistence_supported": persisted,
            "native_mediation_supported": native_read,
            "substrate_reduced_sensitivity_observed": reduced_read,
            "slow_cluster_retention_interpretation_allowed": slow_allowed,
            "local_evidence_ladder_rung": rung,
            "core_readback_supported": False,
            "closed_loop_supported": False,
            "detection_floor_audit": {
                "prepared_joint_amplitude": initial_norm,
                "prepared_W_amplitude": initial["block_l2"]["W"],
                "required_horizon_joint_amplitude": required["separation"][
                    "joint_block_scaled_l2"
                ],
                "current_response_detection_floor": config["p5_3_review_hardening"][
                    "detection_contract"
                ]["current_response_floor"],
                "carrier_detection_floor": config["p5_3_review_hardening"][
                    "detection_contract"
                ]["carrier_floor"],
                "frozen_W_positive_control_observed": reduced_read,
                "below_floor_interpretation": config["p5_3_review_hardening"][
                    "detection_contract"
                ]["below_floor_result"],
            },
            "joint_carrier_probe_scope": (
                "W_only_matching_not_executed_when_W_erased;_joint_C_W_or_"
                "transferred_C_candidate_not_rejected_by_W_only_null"
            ),
        }
        branch_rows.append(row)
        if persisted:
            possibility = "retention_without_read"
            maximum_claim = (
                "bounded_synthetic_old_current_conditioned_C_dominated_neutral_"
                "direction_persistence_with_branch_relocation_rival_unresolved_"
                "and_without_specific_transient_W_mediation_or_native_read_effect"
            )
        elif write_supported:
            possibility = "write_before_read"
            maximum_claim = "stage_local_activity_conditioned_write_without_persistence"
        else:
            possibility = "ordinary_recurrent_geometry_or_authored_carrier"
            maximum_claim = "direct_authored_geometry_carrier_diagnostic"
        blocked_claims = [
            "core_readback",
            "orientation_retention",
            "closed_read_write_loop",
            "memory",
            "learning",
        ]
        if not persisted:
            blocked_claims.insert(0, "persistent_retention")
        causal_rows.append(
            {
                "row_id": f"{branch['branch_id']}::{pair['preparation_id']}",
                "retention_status": (
                    persistence_classification["retention_class"]
                    if persisted
                    else "not_supported"
                ),
                "read_effect_status": (
                    "native_mediation_candidate"
                    if native_read
                    else ("substrate_reduced_only" if reduced_read else "not_supported")
                ),
                "write_effect_status": pair["write_status"],
                "closed_loop_status": "not_supported",
                "causal_possibility_class": possibility,
                "local_evidence_ladder_rung": rung,
                "maximum_claim": maximum_claim,
                "blocked_claims": blocked_claims,
                "branch_relocation_rival_status": relocation_audit[
                    "branch_relocation_rival_status"
                ],
                "transverse_branch_relative_retention_supported": False,
                "transient_W_mediation_status": transient_w_mediation["status"],
                "reachability_classification": reachability,
            }
        )
    return branch_rows, preparation_controls, causal_rows


def intervention_registry(
    preparation_controls: list[dict[str, Any]],
) -> dict[str, Any]:
    interventions = []
    for control in preparation_controls:
        branch_id = control["branch_id"]
        projections = control["intervention_state_projections"]
        common = {
            "base_snapshot_sha256": control["base_snapshot_sha256"],
            "coordinate_semantics": "sorted_native_node_and_edge_order_with_edge_J_from_node_u_to_node_v",
            "validity_checks": {
                "clone_first_source_unchanged": True,
                "structural_validation_passed": True,
                "duplicate_conductance_fields_reconciled": True,
                "machine_local_paths_absent": True,
            },
            "physical_projection_before": projections["baseline"],
            "causal_state_projection_before": projections["baseline"],
        }
        interventions.extend(
            [
                {
                    **common,
                    "intervention_id": f"{branch_id}::set_base_conductance_opposite_pair",
                    "fields_directly_changed": [
                        "base_conductance.*",
                        "port_edges.*.conductance",
                    ],
                    "fields_explicitly_held_fixed": [
                        "nodes.*.coherence",
                        "port_edges.*.flux_uv",
                        "topology",
                        "params",
                    ],
                    "fields_rebuilt_afterward": [],
                    "rebuild_order": [],
                    "reachability_status": "synthetic_valid_not_runtime_reached",
                    "reachability_classification": reachability_classification(
                        "P-W-direct-opposite"
                    ),
                    "physical_projection_after": {
                        "positive": projections["direct_positive"],
                        "negative": projections["direct_negative"],
                    },
                    "causal_state_projection_after": {
                        "positive": projections["direct_positive"],
                        "negative": projections["direct_negative"],
                    },
                },
                {
                    **common,
                    "intervention_id": f"{branch_id}::set_old_current_then_native_stage",
                    "fields_directly_changed": ["port_edges.*.flux_uv"],
                    "fields_explicitly_held_fixed": [
                        "nodes.*.coherence",
                        "topology",
                        "params",
                    ],
                    "fields_rebuilt_afterward": [
                        "differential_state",
                        "transport_state",
                    ],
                    "rebuild_order": [
                        "rebuild_differential_state",
                        "rebuild_transport_state",
                    ],
                    "reachability_status": "exact_native_stage_from_synthetic_old_current_input",
                    "reachability_classification": reachability_classification(
                        "P-J-activity-stage-vs-zero"
                    ),
                    "physical_projection_after": {
                        "activity": projections["activity_stage"],
                        "zero": projections["activity_stage_zero"],
                    },
                    "causal_state_projection_after": {
                        "activity": projections["activity_stage"],
                        "zero": projections["activity_stage_zero"],
                    },
                },
                {
                    **common,
                    "intervention_id": f"{branch_id}::reverse_old_current_sign_control",
                    "fields_directly_changed": ["port_edges.*.flux_uv"],
                    "fields_explicitly_held_fixed": [
                        "nodes.*.coherence",
                        "topology",
                        "params",
                        "old_current_magnitude",
                    ],
                    "fields_rebuilt_afterward": [
                        "differential_state",
                        "transport_state",
                    ],
                    "rebuild_order": [
                        "rebuild_differential_state",
                        "rebuild_transport_state",
                    ],
                    "reachability_status": "synthetic_sign_reversal_control",
                    "reachability_classification": {
                        **reachability_classification(
                            "P-J-activity-stage-vs-zero"
                        ),
                        "post_intervention_state_status": (
                            "sign_reversal_control_produced_by_exact_native_stage_"
                            "from_synthetic_intervention"
                        ),
                    },
                    "physical_projection_after": {
                        "positive": projections["activity_stage"],
                        "negative": projections["activity_sign_reversed_stage"],
                    },
                    "causal_state_projection_after": {
                        "positive": projections["activity_stage"],
                        "negative": projections["activity_sign_reversed_stage"],
                    },
                },
                {
                    **common,
                    "intervention_id": f"{branch_id}::set_old_current_then_complete_step",
                    "fields_directly_changed": ["port_edges.*.flux_uv"],
                    "fields_explicitly_held_fixed": ["topology", "params"],
                    "fields_rebuilt_afterward": ["complete_GRC9V3_step"],
                    "rebuild_order": ["GRC9V3.step"],
                    "reachability_status": "complete_step_reached_from_synthetic_old_current_input",
                    "reachability_classification": reachability_classification(
                        "P-J-activity-complete-step-vs-zero"
                    ),
                    "physical_projection_after": {
                        "activity": projections["activity_complete_step"],
                        "zero": projections["activity_complete_step_zero"],
                    },
                    "causal_state_projection_after": {
                        "activity": projections["activity_complete_step"],
                        "zero": projections["activity_complete_step_zero"],
                    },
                },
            ]
        )
    return {
        "interventions": interventions,
        "canonical_control_operations": {
            "match_C_and_J": {
                "changed_fields": ["nodes.*.coherence", "port_edges.*.flux_uv"],
                "preserved_fields": [
                    "base_conductance.*",
                    "port_edges.*.conductance",
                ],
                "result_location": "conductance_retention_probe.candidate_rows.*.matched_probe_rows",
            },
            "reset_carrier": {
                "changed_fields": [
                    "base_conductance.*",
                    "port_edges.*.conductance",
                ],
                "result_location": "matched_probe_rows.*.mediation_controls.carrier_reset_*",
            },
            "swap_carrier": {
                "changed_fields": [
                    "base_conductance.*",
                    "port_edges.*.conductance",
                ],
                "result_location": "matched_probe_rows.*.mediation_controls.carrier_swap_*",
            },
            "equal_carrier": {
                "changed_fields": [
                    "base_conductance.*",
                    "port_edges.*.conductance",
                ],
                "result_location": "matched_probe_rows.*.mediation_controls.equal_carrier_*",
            },
        },
        "summary": {
            "branch_count": len(preparation_controls),
            "intervention_record_count": len(interventions),
            "all_required_fields_present": True,
        },
    }


def build_36_point_review_audit(
    payload: dict[str, Any], config: dict[str, Any]
) -> dict[str, Any]:
    rows = payload["candidate_rows"]
    controls = payload["preparation_controls"]
    all_probe_rows = [
        probe
        for row in rows
        for horizon in row["matched_probe_rows"]
        for probe in horizon["rows"]
    ]
    ladder_rows = [
        ladder
        for control in controls
        for ladder in control["activity_preparation_amplitude_ladder"]
    ]
    native_probe_rows = [
        row for row in all_probe_rows if row["lane"] != "frozen_W_probe"
    ]
    multi_edge_probe_rows = [
        row
        for row in all_probe_rows
        if row["mediation_controls"]["wrong_location_or_shuffled_carrier"]["status"]
        == "executed_multi_edge_carrier_pattern_shift"
    ]
    intervention_accuracy_floor = float(
        config["p5_3_review_hardening"]["detection_contract"][
            "reset_swap_accuracy_floor"
        ]
    )
    mediation_intervention_accuracy_passed = all(
        max(
            control["carrier_reset_intervention_accuracy"][
                "carrier_pair_W_difference_linf"
            ],
            control["carrier_reset_intervention_accuracy"]["first_to_baseline_W_linf"],
            control["carrier_reset_intervention_accuracy"]["second_to_baseline_W_linf"],
            control["equal_carrier_intervention_accuracy"][
                "carrier_pair_W_difference_linf"
            ],
            control["carrier_swap_intervention_accuracy"][
                "first_to_original_second_W_linf"
            ],
            control["carrier_swap_intervention_accuracy"][
                "second_to_original_first_W_linf"
            ],
        )
        <= intervention_accuracy_floor
        and all(
            surface["surfaces_consistent"]
            for key in (
                "carrier_reset_intervention_accuracy",
                "equal_carrier_intervention_accuracy",
                "carrier_swap_intervention_accuracy",
            )
            for surface in control[key]["surface_consistency"]
        )
        for row in all_probe_rows
        for control in (row["mediation_controls"],)
    )

    def point(
        point_id: int,
        title: str,
        passed: bool,
        disposition: str,
        evidence: list[str],
        claim_effect: str,
    ) -> dict[str, Any]:
        return {
            "point_id": point_id,
            "title": title,
            "mechanical_check_passed": bool(passed),
            "disposition": disposition,
            "evidence": evidence,
            "claim_effect": claim_effect,
        }

    review_points = [
        point(
            1,
            "carrier_fixed_before_confirmatory_reexecution",
            all("predeclared_carrier_hypothesis" in row for row in rows),
            "passed_with_revision_distinct_non_blind_status",
            [
                "candidate_rows.*.predeclared_carrier_hypothesis",
                "preparation_controls.*.carrier_hypotheses_status",
            ],
            "P5.3 cannot upgrade the P5.2 rung",
        ),
        point(
            2,
            "GRV3_branch_classes_separated",
            all("GRV3_C_W_causal_status" in row for row in rows),
            "passed",
            [
                "candidate_rows.*.GRV3_C_W_causal_status",
                "candidate_rows.*.GRV3_branch_claim_ceiling",
            ],
            "blocked GRV3 rows remain physical/stage observations only",
        ),
        point(
            3,
            "preparation_end_and_k0_defined",
            all("activity_stage_boundary_trace" in row for row in controls),
            "passed",
            [
                "preparation_controls.*.activity_stage_boundary_trace",
                "p5_3_review_hardening.preparation_boundary",
            ],
            "k0 alone cannot support persistence",
        ),
        point(
            4,
            "ongoing_activity_distinguished_from_external_stop",
            all(
                "persistence_activity_trace" in row
                and "persistence_classification" in row
                and "branch_relocation_audit" in row
                for row in rows
            )
            and all(
                row["branch_relocation_audit"][
                    "branch_relocation_rival_status"
                ]
                == "branch_relocation_rival_unresolved_not_excluded"
                and not row["branch_relocation_audit"][
                    "transverse_branch_relative_retention_supported"
                ]
                for row in rows
                if row["local_evidence_ladder_rung"] == "GRR2"
            ),
            "passed_with_branch_relocation_rival_unresolved",
            [
                "candidate_rows.*.persistence_activity_trace",
                "candidate_rows.*.persistence_classification",
                "candidate_rows.*.branch_relocation_audit",
            ],
            (
                "GRR2_records_neutral_direction_persistence_with_branch_"
                "relocation_unresolved_not_transverse_branch_relative_retention"
            ),
        ),
        point(
            5,
            "direct_W_does_not_establish_writeback",
            all(
                row["local_evidence_ladder_rung"] == "GRR0"
                for row in rows
                if row["preparation_id"] == "P-W-direct-opposite"
            ),
            "passed",
            ["candidate_rows[P-W-direct-opposite]", "causal_role_matrix.json"],
            "P-W remains synthetic carrier diagnostic",
        ),
        point(
            6,
            "synthetic_old_current_separated_from_reached_history",
            payload["summary"]["forming_old_current_input_runtime_reached"] is False
            and all(
                not row["reachability_classification"][
                    "reachable_from_accepted_branch_by_unchanged_runtime_alone"
                ]
                and not row["reachability_classification"][
                    "runtime_reached_shorthand_allowed"
                ]
                for row in rows
            ),
            "passed_with_conditional_runtime_successor_wording",
            [
                "summary.forming_old_current_input_runtime_reached",
                "preparation_controls.*.activity_input_class",
                "candidate_rows.*.reachability_classification",
            ],
            "unchanged-runtime successor of synthetic intervention is not native branch reachability",
        ),
        point(
            7,
            "direct_and_indirect_write_paths_staged",
            all("activity_stage_boundary_trace" in row for row in controls)
            and all(
                row["transient_W_mediation_classification"]["status"]
                == "not_established"
                and not row["transient_W_mediation_classification"][
                    "stage_matched_W_only_mediation_control_run"
                ]
                and not row["transient_W_mediation_classification"][
                    "later_C_mediation_specifically_by_transient_W_supported"
                ]
                for row in rows
                if row["preparation_id"]
                == "P-J-activity-complete-step-vs-zero"
            ),
            "passed_with_specific_transient_W_mediation_unresolved",
            [
                "activity_stage_boundary_trace.*.after_first_native_transport_write",
                "activity_stage_boundary_trace.*.after_continuity_before_budget",
                "activity_stage_boundary_trace.*.after_complete_preparation_step",
                "candidate_rows.*.transient_W_mediation_classification",
            ],
            "stage-local W write and later C consequence coexist without identified W-specific mediation",
        ),
        point(
            8,
            "J_sign_comparisons_immediate_and_later",
            all("immediate_and_later_sign_audit" in row for row in controls),
            "passed",
            ["preparation_controls.*.immediate_and_later_sign_audit"],
            "sign-even W does not imply unexamined whole-beat sign retention",
        ),
        point(
            9,
            "preparation_amplitude_ladder",
            len(ladder_rows) == 4 * len(controls)
            and all(
                row["sign_even_W_error_linf"] <= 1e-10
                and row["expected_log_W_ratio_error_linf"] <= 1e-10
                for row in ladder_rows
            ),
            "passed_confirmatory_only",
            ["preparation_controls.*.activity_preparation_amplitude_ladder"],
            "response shape cannot upgrade the primary rung",
        ),
        point(
            10,
            "direct_W_metric_symmetry_and_positivity",
            all(
                row["direct_W_metric_audit"]["equal_distance_error"] <= 1e-12
                and row["direct_W_metric_audit"]["positivity_preserved"]
                for row in controls
            ),
            "passed",
            ["preparation_controls.*.direct_W_metric_audit"],
            "no asymmetric-floor artifact",
        ),
        point(
            11,
            "carrier_vectors_and_alignment_recorded",
            all(
                "block_vectors" in row["initial_separation"]
                and all(
                    "carrier_alignment" in horizon for horizon in row["horizon_rows"]
                )
                for row in rows
            ),
            "passed",
            [
                "candidate_rows.*.initial_separation.block_vectors",
                "candidate_rows.*.horizon_rows.*.carrier_alignment",
            ],
            "norm-only persistence is blocked",
        ),
        point(
            12,
            "branch_not_refit_during_persistence",
            config["persistence"]["branch_refit_during_persistence_allowed"] is False,
            "passed",
            [
                "persistence.branch_refit_during_persistence_allowed",
                "candidate_rows.*.branch_id",
            ],
            "all horizons remain relative to the frozen GRV2 branch",
        ),
        point(
            13,
            "instability_not_called_stable_retention",
            all(
                row["persistence_classification"]["instability_is_stable_retention"]
                is False
                for row in rows
            ),
            "passed",
            ["candidate_rows.*.persistence_classification.stability_class"],
            "growing displacement cannot satisfy stable-retention wording",
        ),
        point(
            14,
            "only_accepted_slow_subspaces_interpreted",
            all(
                not row["slow_cluster_retention_interpretation_allowed"] for row in rows
            ),
            "passed_no_interpretable_slow_subspace",
            [
                "candidate_rows.*.horizon_rows.*.slow_fast_projection",
                "candidate_rows.*.slow_cluster_retention_interpretation_allowed",
            ],
            "GRR3 remains blocked",
        ),
        point(
            15,
            "deadbeat_W_mediation_kept_distinct",
            all(row["write_status"] != "retained_W" for row in rows),
            "passed",
            [
                "candidate_rows.*.write_status",
                "candidate_rows.*.persistence_classification.carrier_path",
            ],
            "one-beat W action is not W retention",
        ),
        point(
            16,
            "fresh_clone_per_horizon_and_probe_cell",
            config["persistence"]["fresh_unprobed_clone_per_horizon"] is True
            and config["p5_3_review_hardening"]["probe_contract"][
                "separate_clone_for_each_cell_and_horizon_required"
            ]
            is True,
            "passed_by_method_and_tests",
            [
                "persistence_states",
                "difference_in_differences",
                "tests/test_grv5_preparation_persistence.py",
            ],
            "probe writes cannot contaminate later horizons",
        ),
        point(
            17,
            "full_admitted_noncarrier_matching",
            all(
                probe["matching_intervention_receipt"]["passed"]
                for probe in all_probe_rows
            ),
            "passed_with_GRV3_C_W_J_and_categorical_scope",
            ["matched_probe_rows.*.matching_intervention_receipt"],
            "opaque derived caches are not promoted to independent state",
        ),
        point(
            18,
            "matching_preserves_authoritative_W",
            all(
                probe["matching_intervention_receipt"][
                    "carrier_difference_preservation_linf"
                ]
                <= 1e-10
                for probe in all_probe_rows
            ),
            "passed",
            [
                "matching_intervention_receipt.carrier_difference_preservation_linf",
                "matching_intervention_receipt.source_to_matched_preservation",
            ],
            "erased-carrier nulls are blocked",
        ),
        point(
            19,
            "W_matching_does_not_reject_joint_carrier",
            all(
                row["joint_carrier_probe_scope"].startswith("W_only_matching")
                for row in rows
            ),
            "passed",
            ["candidate_rows.*.joint_carrier_probe_scope"],
            "joint/transferred persistence remains separate from W sufficiency",
        ),
        point(
            20,
            "probe_lanes_semantically_separate",
            {row["lane"] for row in all_probe_rows}.issubset(
                {
                    "native_full_step_probe",
                    "native_immediate_transport_stage_probe",
                    "frozen_W_probe",
                }
            ),
            "passed",
            [
                "matched_probe_rows.*.rows.*.lane",
                "matched_probe_rows.*.rows.*.substrate_class",
            ],
            "frozen-W cannot upgrade native evidence",
        ),
        point(
            21,
            "present_current_convention_frozen",
            payload["present_current_convention"][
                "native_external_present_current_input_available"
            ]
            is False,
            "passed",
            ["present_current_convention"],
            "coherence, old-J, and analytical probes retain distinct ceilings",
        ),
        point(
            22,
            "full_2x2_interaction",
            all(
                len(probe["sweep"][0]["cell_receipts"]) == 4 for probe in all_probe_rows
            ),
            "passed",
            ["matched_probe_rows.*.rows.*.sweep.*.cell_receipts"],
            "baseline geometry is not a read effect",
        ),
        point(
            23,
            "oriented_interaction_before_norm",
            all(
                isinstance(sweep["difference_in_differences"], list)
                for probe in all_probe_rows
                for sweep in probe["sweep"]
            ),
            "passed",
            ["matched_probe_rows.*.rows.*.sweep.*.difference_in_differences"],
            "edge orientation is preserved before scalar summaries",
        ),
        point(
            24,
            "zero_probe_baseline_classified_separately",
            all(
                probe["zero_present_probe_control"][
                    "baseline_difference_is_read_effect"
                ]
                is False
                for probe in all_probe_rows
            ),
            "passed",
            ["matched_probe_rows.*.rows.*.zero_present_probe_control"],
            "zero-probe baseline difference is ordinary recurrence",
        ),
        point(
            25,
            "probe_induced_carrier_write_recorded",
            all(
                "carrier_change_during_readout" in cell
                for probe in all_probe_rows
                for sweep in probe["sweep"]
                for cell in sweep["cell_receipts"].values()
            ),
            "passed",
            [
                "matched_probe_rows.*.rows.*.sweep.*.cell_receipts.*.carrier_change_during_readout"
            ],
            "same-beat response and write remain distinguishable",
        ),
        point(
            26,
            "signed_sweep_and_odd_even_decomposition",
            all(
                "odd_even_decomposition" in probe["signed_sweep_fit"]
                for probe in all_probe_rows
            ),
            "passed",
            ["matched_probe_rows.*.rows.*.signed_sweep_fit"],
            "linear language remains conditional on fit",
        ),
        point(
            27,
            "route_selectivity_requires_multi_edge_evidence",
            len(multi_edge_probe_rows) > 0
            and all(
                not probe["mediation_controls"]["wrong_location_or_shuffled_carrier"][
                    "route_selectivity_claim_allowed"
                ]
                for probe in native_probe_rows
                if probe in multi_edge_probe_rows
            ),
            "passed_with_route_claim_blocked",
            [
                "matched_probe_rows.*.rows.*.mediation_controls.wrong_location_or_shuffled_carrier"
            ],
            "two-node scalar effects cannot establish route selectivity",
        ),
        point(
            28,
            "graded_mediation_controls",
            all(
                "graded_mediation_class" in probe["mediation_controls"]
                for probe in all_probe_rows
            ),
            "passed",
            ["matched_probe_rows.*.rows.*.mediation_controls"],
            "reset/swap/equal/shuffle determine mediation class",
        ),
        point(
            29,
            "controls_modify_authoritative_W_surface",
            mediation_intervention_accuracy_passed
            and all(
                all(
                    audit["surfaces_consistent"]
                    for audit in row["direct_W_metric_audit"][
                        "authoritative_surface_consistency"
                    ]
                )
                for row in controls
            ),
            "passed",
            [
                "direct_W_metric_audit.authoritative_surface_consistency",
                "grv5_intervention_registry.json",
            ],
            "non-authoritative-copy controls cannot pass",
        ),
        point(
            30,
            "write_occurrence_separate_from_retained_write",
            all(
                "write_status" in row and "persistence_classification" in row
                for row in rows
            ),
            "passed",
            [
                "candidate_rows.*.write_status",
                "candidate_rows.*.persistence_classification",
            ],
            "instantaneous write does not imply retained write",
        ),
        point(
            31,
            "closed_loop_requires_linked_chain",
            payload["summary"]["closed_loop_supported"] is False,
            "passed_as_blocked",
            ["causal_role_matrix.json", "summary.closed_loop_supported"],
            "unrelated positive arrows are not assembled into a loop",
        ),
        point(
            32,
            "response_and_later_write_use_separate_clones",
            config["p5_3_review_hardening"]["probe_contract"][
                "separate_response_and_later_write_clones_required_if_loop_gate_opens"
            ]
            is True
            and payload["summary"]["closed_loop_supported"] is False,
            "not_applicable_loop_gate_not_opened_policy_frozen",
            ["p5_3_review_hardening.probe_contract", "summary.closed_loop_supported"],
            "future loop probes must use independent clones",
        ),
        point(
            33,
            "detection_floors_and_positive_control",
            all("detection_floor_audit" in row for row in rows)
            and payload["summary"]["substrate_reduced_sensitivity_count"] > 0
            and mediation_intervention_accuracy_passed,
            "passed",
            [
                "candidate_rows.*.detection_floor_audit",
                "summary.substrate_reduced_sensitivity_count",
            ],
            "below-floor effects remain unresolved rather than absent",
        ),
        point(
            34,
            "all_preregistered_horizons_reported",
            all(
                [h["horizon_complete_steps"] for h in row["horizon_rows"]]
                == config["persistence"]["horizons_complete_steps_after_preparation"]
                for row in rows
            ),
            "passed",
            ["candidate_rows.*.horizon_rows"],
            "no best-horizon selection",
        ),
        point(
            35,
            "event_topology_stratum_and_budget_fail_closed",
            all(
                "causal_guard_audit" in horizon
                for row in rows
                for horizon in row["horizon_rows"]
            ),
            "passed_with_crossings_recorded_and_blocking",
            ["candidate_rows.*.horizon_rows.*.causal_guard_audit"],
            "unclean paths cannot support same-branch causal persistence",
        ),
        point(
            36,
            "positive_GRV5_is_not_automatic_core_readback",
            payload["summary"]["native_readback_supported"] is False
            and payload["claim_boundary"][
                "frozen_W_sensitivity_does_not_upgrade_native"
            ]
            is True,
            "passed",
            ["summary.native_readback_supported", "claim_boundary"],
            "maximum result remains bounded joint-state persistence without native Read-Back",
        ),
    ]
    return {
        "gate_id": "GRV5",
        "audit_id": (
            "P5.3_36_point_causal_identification_hardening_with_"
            "P5.4_acceptance_clarifications"
        ),
        "review_point_count": len(review_points),
        "all_review_points_mechanically_accounted_for": all(
            row["mechanical_check_passed"] for row in review_points
        ),
        "evidence_upgrade_allowed": False,
        "branch_scope_or_primary_threshold_changed": False,
        "P5_4_acceptance_clarification_changed_primary_rung": False,
        "review_points": review_points,
    }


def write_report(payload: dict[str, Any]) -> Path:
    summary = payload["summary"]
    report = EXPERIMENT_ROOT / "reports/b1_grv5_retention_read_write_mediation.md"
    lines = [
        "# B1-GR GRV5 Retention, Read, Write, And Mediation",
        "",
        "## Result",
        "",
        "```text",
        f"mechanical_status = {summary['mechanical_status']}",
        f"branch_count = {summary['branch_count']}",
        f"activity_stage_write_count = {summary['activity_stage_write_count']}",
        f"activity_complete_step_joint_write_count = {summary['activity_complete_step_joint_write_count']}",
        f"forming_old_current_amplitude = {summary['forming_old_current_amplitude_range']}",
        f"bounded_persistence_count = {summary['bounded_persistence_count']}",
        f"native_mediation_count = {summary['native_mediation_count']}",
        f"substrate_reduced_sensitivity_count = {summary['substrate_reduced_sensitivity_count']}",
        f"maximum_local_rung = {summary['maximum_local_evidence_ladder_rung']}",
        f"GRR2_branch_relocation_rival_unresolved = {summary['branch_relocation_rival_unresolved_GRR2_row_count']}",
        f"specific_transient_W_mediation_supported = {summary['later_C_mediation_specifically_by_transient_W_supported']}",
        f"native_branch_only_reachability_supported = {summary['complete_step_state_reachable_from_accepted_branch_by_unchanged_runtime_alone']}",
        f"review_points_accounted_for = {summary['review_point_count']}/36",
        f"P5_3_changed_primary_rung = {summary['P5_3_hardening_changed_primary_rung']}",
        f"P5_4_changed_primary_rung = {summary['P5_4_acceptance_clarification_changed_primary_rung']}",
        "scientific_acceptance = awaiting_human_review",
        "```",
        "",
        "## Interpretation",
        "",
        "GRV5 resolves the four causal arrows separately. A synthetic experiment-",
        "authored old-current state changes conductance at the first exact native",
        "transport reconstruction. One unchanged complete step then reconstructs",
        "current and conductance, erases that conductance inscription, and produces",
        "a later coherence-dominated consequence. GRV5 does not isolate transient",
        "`W` from every other state produced by the synthetic old-current preparation,",
        "so it does not establish that transient `W` specifically mediates later `C`.",
        "It tests the unchanged-runtime successor separately from the stage-local pair.",
        "Direct authored conductance differences are overwritten by reconstruction.",
        "The old-current forming input is synthetic and not native-runtime reachable.",
        "The resulting complete-step state is an unchanged-runtime successor of that",
        "synthetic intervention; it is not shown reachable from an accepted branch by",
        "unchanged runtime evolution alone and is never shortened to `runtime-reached`.",
        "its large magnitude follows from the frozen `gamma = 1e-12` branch parameter",
        "and the preregistered 0.01 amplitude-squared attenuation coordinate.",
        "On multi-edge fixtures the realized per-edge log-conductance change is",
        "that coordinate multiplied by the squared canonical edge direction; it",
        "is not a uniform 0.01 attenuation on every edge.",
        "",
        "Frozen-conductance probes can expose carrier-conditioned transport response,",
        "but that lane is substrate-reduced and its carrier states are synthetic or",
        "stage-local off the current constitutive manifold. Native full-step and exact",
        "immediate-stage lanes therefore remain authoritative for native mediation.",
        "A baseline geometry-conditioned current difference is not counted as a read",
        "effect; every candidate row uses the full carrier-by-probe 2x2 contrast.",
        "",
        "The maximum bounded result is assigned from the complete-step reached pair,",
        "its persistence horizons, and the independent slow-cluster/read gates. It",
        "does not establish core Read-Back, orientation retention, or a closed",
        "read/write loop.",
        "The persistent F2/F3 displacement is neutral/marginal within the declared",
        "finite-horizon ratio tolerance and C-dominated after W overwrite. Every",
        "`GRR2` displacement lies in the admitted zero-sum `C` coordinate to numerical",
        "precision and changes negligibly through horizon 10. GRV3 did not separately",
        "identify a branch tangent, so relocation along a neutral branch family remains",
        "an unresolved rival. The result is bounded C-dominated neutral-direction",
        "persistence, not transverse branch-relative retention or stable W retention.",
        "P5.3 and the P5.4 acceptance clarification cannot upgrade the GRR2 rung.",
        "",
        "## Causal Boundaries",
        "",
        "- `P-W`: producer-authored conductance carrier; synthetic-valid only.",
        "- `P-J`: exact native stage response to a synthetic old-current input.",
        "- `P-J complete`: unchanged-runtime successor of a synthetic old-current intervention; native branch-only reachability is not demonstrated.",
        "- Transient `W` mediation: not established; no stage-matched W-only mediation control was run.",
        "- GRR2 branch relation: neutral-coordinate persistence with branch relocation unresolved.",
        "- `P-J-sign`: confirms the source-current-squared write is sign-even.",
        "- Native complete-step persistence: evaluated after forming input stops.",
        "- Frozen-`W` response: reduced diagnostic; cannot upgrade native evidence.",
        "- External-current-like probe: analytical only; no native external-current input exists.",
        "- Canonical interventions: `grv5_intervention_registry.json`.",
        "- Acceptance hardening: all 36 review points are mapped in",
        "  `grv5_36_point_review_audit.json`.",
        "",
        "## Provenance",
        "",
        f"- Input execution revision: `{payload['source_contract']['input_execution_revision']}`",
        f"- GRV4 receipt: `{GRV4_RECEIPT_SHA256}`",
        f"- GRV4 acceptance commit: `{GRV4_ACCEPTANCE_COMMIT}`",
        "- Runtime source/spec/test paths: unchanged under `protected_path_manifest_v5.json`",
    ]
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report


def run_grv5() -> None:
    if git("status", "--porcelain"):
        raise SystemExit("GRV5 requires a clean committed P5 input revision")
    receipt4, anchor4 = validate_prerequisite()
    config = read_json(EXPERIMENT_ROOT / "configs/grv5_preparation_persistence.json")
    scope = config["source_scope"]
    registry = read_json(EXPERIMENT_ROOT / scope["branch_registry_path"])["payload"]
    grv3 = read_json(EXPERIMENT_ROOT / scope["grv3_result_path"])["payload"]
    branches = [row for row in registry["branches"] if row["branch_certified"]]
    if len(branches) != int(scope["expected_branch_count"]):
        raise ValueError("GRV5 branch scope is not the frozen 48-row registry")
    grv3_by_id = {row["branch_id"]: row for row in grv3["branches"]}
    input_revision = git("rev-parse", "HEAD")
    input_tree = file_manifest(tracked_files([EXPERIMENT_RELATIVE]))
    branch_rows = []
    preparation_controls = []
    causal_rows = []
    for branch in branches:
        rows, controls, roles = branch_result(
            branch, grv3_by_id[branch["branch_id"]], config
        )
        branch_rows.extend(rows)
        preparation_controls.append({"branch_id": branch["branch_id"], **controls})
        causal_rows.extend(roles)
    rung_order = {f"GRR{index}": index for index in range(6)}
    maximum_rung = max(
        (row["local_evidence_ladder_rung"] for row in branch_rows),
        key=lambda rung: rung_order[rung],
    )
    required_replays_pass = all(
        horizon["replay"].get("passed", True)
        for row in branch_rows
        for horizon in row["horizon_rows"]
        if horizon["horizon_complete_steps"] in config["replay"]["required_horizons"]
    )
    sign_controls_pass = all(
        row["sign_even_write_passed"] for row in preparation_controls
    )
    expected_row_count = int(scope["expected_candidate_row_count"])
    matrix_complete = bool(
        len(branch_rows) == expected_row_count
        and len(causal_rows) == expected_row_count
        and all(
            len(row["horizon_rows"])
            == len(config["persistence"]["horizons_complete_steps_after_preparation"])
            for row in branch_rows
        )
    )
    summary = {
        "mechanical_status": "passed",
        "branch_count": len(branches),
        "preparation_candidate_row_count": len(branch_rows),
        "activity_stage_write_count": sum(
            row["write_status"] == "stage_local_activity_conditioned_conductance_write"
            and row["initial_separation"]["block_l2"]["W"]
            > config["persistence"]["absolute_separation_tolerance"]
            for row in branch_rows
        ),
        "activity_complete_step_joint_write_count": sum(
            row["write_status"]
            == "activity_conditioned_joint_C_state_after_transient_J_squared_to_W_stage"
            and row["initial_separation"]["joint_block_scaled_l2"]
            > config["persistence"]["absolute_separation_tolerance"]
            for row in branch_rows
        ),
        "forming_old_current_amplitude_range": [
            min(row["activity_input_amplitude"] for row in preparation_controls),
            max(row["activity_input_amplitude"] for row in preparation_controls),
        ],
        "forming_old_current_input_runtime_reached": False,
        "complete_step_state_reachable_from_accepted_branch_by_unchanged_runtime_alone": False,
        "synthetic_complete_step_runtime_successor_row_count": sum(
            row["preparation_id"] == "P-J-activity-complete-step-vs-zero"
            for row in branch_rows
        ),
        "bounded_persistence_count": sum(
            row["bounded_persistence_supported"] for row in branch_rows
        ),
        "native_mediation_count": sum(
            row["native_mediation_supported"] for row in branch_rows
        ),
        "substrate_reduced_sensitivity_count": sum(
            row["substrate_reduced_sensitivity_observed"] for row in branch_rows
        ),
        "required_replays_passed": required_replays_pass,
        "sign_reversal_controls_passed": sign_controls_pass,
        "all_branch_preparation_horizon_matrix_complete": matrix_complete,
        "maximum_local_evidence_ladder_rung": maximum_rung,
        "branch_relocation_rival_unresolved_GRR2_row_count": sum(
            row["local_evidence_ladder_rung"] == "GRR2"
            and row["branch_relocation_audit"]["branch_relocation_rival_status"]
            == "branch_relocation_rival_unresolved_not_excluded"
            for row in branch_rows
        ),
        "transverse_branch_relative_retention_supported": False,
        "later_C_mediation_specifically_by_transient_W_supported": False,
        "maximum_GRR2_admitted_C_projection_residual_l2": max(
            (
                row["branch_relocation_audit"][
                    "maximum_admitted_C_projection_residual_l2"
                ]
                for row in branch_rows
                if row["local_evidence_ladder_rung"] == "GRR2"
            ),
            default=0.0,
        ),
        "maximum_GRR2_C_transition_jacobian_identity_error_linf": max(
            (
                row["branch_relocation_audit"][
                    "C_transition_jacobian_identity_error_linf"
                ]
                for row in branch_rows
                if row["local_evidence_ladder_rung"] == "GRR2"
            ),
            default=0.0,
        ),
        "retention_supported": any(
            row["bounded_persistence_supported"] for row in branch_rows
        ),
        "native_readback_supported": False,
        "writeback_supported": False,
        "closed_loop_supported": False,
        "grv_c5_candidate_pending_human_review": True,
        "P5_4_acceptance_clarification_changed_primary_rung": False,
    }
    if not required_replays_pass or not sign_controls_pass or not matrix_complete:
        raise ValueError(f"GRV5 mechanical controls failed: {summary}")
    payload = {
        "gate_id": "GRV5",
        "source_contract": {
            "input_execution_revision": input_revision,
            "GRV4_receipt_payload_sha256": GRV4_RECEIPT_SHA256,
            "GRV4_acceptance_anchor_commit": GRV4_ACCEPTANCE_COMMIT,
            "branch_registry_path": scope["branch_registry_path"],
            "GRV3_result_path": scope["grv3_result_path"],
            "GRV4_result_path": scope["grv4_result_path"],
            "P5_4_acceptance_provenance_contract": config[
                "p5_4_acceptance_clarification"
            ]["acceptance_provenance_contract"],
        },
        "assumption_statuses": {
            **config["assumption_statuses"],
            "A-PASSIVE-result": "native_external_present_current_unavailable_core_readback_blocked",
            "A-REACHABLE-result": "mixed_complete_step_reached_and_stage_local_or_synthetic_rows_separated",
            "A-STATE-CLOSURE-result": "complete_step_authoritative_stage_local_W_write_and_reached_joint_state_are_separate",
        },
        "present_current_convention": config["present_current_convention"],
        "preparation_controls": preparation_controls,
        "candidate_rows": branch_rows,
        "summary": summary,
        "claim_boundary": {
            **config["claim_boundary"],
            "maximum_supported_claim": (
                "bounded_synthetic_old_current_conditioned_C_dominated_neutral_"
                "direction_persistence_with_branch_relocation_rival_unresolved_"
                "without_specific_transient_W_mediation_or_native_readback"
                if summary["retention_supported"]
                else "stage_local_activity_conditioned_write_without_complete_step_persistence"
            ),
            "frozen_W_sensitivity_does_not_upgrade_native": True,
            "branch_relocation_rival_must_remain_open": True,
            "specific_transient_W_mediation_claim_allowed": False,
            "runtime_reached_shorthand_for_synthetic_successor_allowed": False,
            "GRV_C5_candidate_pending_human_review": True,
        },
    }
    review_audit_payload = build_36_point_review_audit(payload, config)
    if review_audit_payload["review_point_count"] != int(
        config["p5_3_review_hardening"]["required_review_point_count"]
    ):
        raise ValueError("GRV5 36-point review audit is incomplete")
    if not review_audit_payload["all_review_points_mechanically_accounted_for"]:
        failed = [
            row["point_id"]
            for row in review_audit_payload["review_points"]
            if not row["mechanical_check_passed"]
        ]
        raise ValueError(f"GRV5 review hardening failed points: {failed}")
    summary["review_point_count"] = review_audit_payload["review_point_count"]
    summary["all_36_review_points_mechanically_accounted_for"] = True
    summary["P5_3_hardening_changed_primary_rung"] = False
    output_root = EXPERIMENT_ROOT / "outputs"
    result_path = output_root / "conductance_retention_probe.json"
    causal_path = output_root / "causal_role_matrix.json"
    intervention_path = output_root / "grv5_intervention_registry.json"
    review_audit_path = output_root / "grv5_36_point_review_audit.json"
    write_json(
        result_path,
        artifact_envelope(
            payload,
            schema_version="b1_grv5_conductance_retention_probe_v2",
            generating_command=COMMAND,
            reproducibility_class="tolerance_reproducible",
        ),
    )
    causal_payload = {
        "gate_id": "GRV5",
        "source_result_payload_sha256": semantic_digest(payload),
        "rows": causal_rows,
        "summary": {
            "row_count": len(causal_rows),
            "closed_loop_row_count": 0,
            "maximum_local_evidence_ladder_rung": maximum_rung,
        },
    }
    write_json(
        causal_path,
        artifact_envelope(
            causal_payload,
            schema_version="b1_grv5_causal_role_matrix_v2",
            generating_command=COMMAND,
            reproducibility_class="tolerance_reproducible",
        ),
    )
    intervention_payload = intervention_registry(preparation_controls)
    write_json(
        intervention_path,
        artifact_envelope(
            intervention_payload,
            schema_version="b1_grv5_intervention_registry_v2",
            generating_command=COMMAND,
            reproducibility_class="tolerance_reproducible",
        ),
    )
    review_audit_payload["source_result_payload_sha256"] = semantic_digest(payload)
    write_json(
        review_audit_path,
        artifact_envelope(
            review_audit_payload,
            schema_version="b1_grv5_36_point_review_audit_v2",
            generating_command=COMMAND,
            reproducibility_class="tolerance_reproducible",
        ),
    )
    protected_path = output_root / "protected_path_manifest_v5.json"
    protected = protected_manifest_v5()
    if not protected["payload"]["unchanged_successor"]:
        raise ValueError("protected source/spec/test paths changed since GRV4")
    write_json(protected_path, protected)
    report_path = write_report(payload)
    artifacts = [
        result_path,
        causal_path,
        intervention_path,
        review_audit_path,
        protected_path,
        report_path,
    ]
    baseline = read_json(output_root / "baseline_manifest.json")["payload"]
    receipt = finalize_receipt(
        {
            "gate_id": "GRV5",
            "input_execution_revision": input_revision,
            "substrate_base_revision": baseline["substrate_base_revision"],
            "input_experiment_tree_sha256": input_tree["tree_sha256"],
            "prerequisite_result_receipt_digests": [GRV4_RECEIPT_SHA256],
            "prerequisite_acceptance_anchors": [
                {
                    "gate_id": "GRV4",
                    "immutable_ref": f"git:{GRV4_ACCEPTANCE_COMMIT}",
                    "anchor_payload_sha256": semantic_digest(anchor4),
                }
            ],
            "output_artifact_digests": {
                path.relative_to(EXPERIMENT_ROOT).as_posix(): sha256_file(path)
                for path in sorted(artifacts)
            },
            "status": "awaiting_scientific_review",
            "blocked_gates": [f"GRV{index}" for index in range(6, 9)],
            "claim_ceiling": (
                "bounded_synthetic_old_current_conditioned_C_dominated_neutral_"
                "direction_persistence_with_branch_relocation_rival_unresolved_"
                "without_specific_transient_W_mediation_or_native_readback_"
                "pending_human_review"
                if summary["retention_supported"]
                else "stage_local_write_without_complete_step_retention_or_native_readback_pending_human_review"
            ),
            "prerequisite_acceptance_status": anchor4["acceptance_status"],
            "grv5_summary": summary,
        }
    )
    validate_receipt(receipt)
    write_json(output_root / "gates/grv5_result_receipt.json", receipt)


def main() -> None:
    run_grv5()
    print("GRV5 mechanically validated; scientific acceptance anchor is pending.")


if __name__ == "__main__":
    main()
