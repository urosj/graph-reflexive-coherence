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
    activity_write_stage,
    categorical_projection,
    clone_model,
    coherence_vector,
    conductance_vector,
    constitutive_consistency_audit,
    current_vector,
    difference_in_differences,
    direct_conductance_intervention,
    equal_carrier_preserving_reached_state,
    match_C_and_J_preserving_W,
    old_current_intervention,
    pair_separation,
    physical_projection_linf,
    reset_carrier,
    signed_sweep_fit,
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
            "native_activity_write_supported": complete_initial[
                "joint_block_scaled_l2"
            ]
            > tolerance,
        },
    ]
    return pairs, controls


def persistence_states(
    first: GRC9V3, second: GRC9V3, horizons: list[int]
) -> dict[int, tuple[GRC9V3, GRC9V3]]:
    first_live = clone_model(first)
    second_live = clone_model(second)
    records: dict[int, tuple[GRC9V3, GRC9V3]] = {}
    for horizon in range(max(horizons) + 1):
        if horizon in horizons:
            records[horizon] = (clone_model(first_live), clone_model(second_live))
        if horizon < max(horizons):
            first_live.step()
            second_live.step()
    return records


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

    slow = [index for index, value in enumerate(values) if abs(value) >= minimum_magnitude]
    fast = [index for index, value in enumerate(values) if abs(value) < minimum_magnitude]
    clusters = audit["temporal_mode_diagnostics"].get("clusters", [])
    retention_allowed = bool(clusters) and all(
        cluster.get("retention_interpretation_allowed", False)
        for cluster in clusters
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
        values = [activity_amplitude_from_target(model, value) if value else 0.0 for value in targets]
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
            if probe_kind == "external_current_like_analytical_probe" and lane != "frozen_W_probe":
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
            maximum_effect = max(
                row["difference_in_differences_l2"] for row in sweep
            )
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
            equal_result = difference_in_differences(
                equal_pair[0],
                equal_pair[1],
                lane=lane,
                probe_kind=probe_kind,
                amplitude=control_amplitude,
            )
            swapped = swap_carrier(matched_first, matched_second)
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
            rows.append(
                {
                    "lane": lane,
                    "probe_kind": probe_kind,
                    "carrier_pair_provenance": provenance_class,
                    "carrier_pair_state_class": state_class,
                    "constitutive_consistency": consistency,
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
                        "equal_carrier_difference_in_differences_l2": equal_result[
                            "difference_in_differences_l2"
                        ],
                        "equal_carrier_passed": equal_result[
                            "difference_in_differences_l2"
                        ]
                        <= tolerance,
                        "carrier_swap_sign_reversal_error_l2": swap_error,
                        "carrier_swap_passed": swap_error <= tolerance,
                    },
                }
            )
    return rows


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
    horizons = [int(value) for value in config["persistence"]["horizons_complete_steps_after_preparation"]]
    replay_horizons = set(int(value) for value in config["replay"]["required_horizons"])
    tolerance = float(config["persistence"]["absolute_separation_tolerance"])
    branch_rows = []
    causal_rows = []
    for pair in pairs:
        states = persistence_states(pair["models"][0], pair["models"][1], horizons)
        prepared_categorical = [
            categorical_projection(states[0][0]),
            categorical_projection(states[0][1]),
        ]
        prepared_event_counts = [
            len(states[0][0].get_state().event_log),
            len(states[0][1].get_state().event_log),
        ]
        initial = pair_separation(
            states[0][0], states[0][1], branch_scales=scales
        )
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
            horizon_rows.append(
                {
                    "horizon_complete_steps": horizon,
                    "separation": separation,
                    "persistence_ratio": ratio,
                    "slow_fast_projection": projection,
                    "replay": replay,
                    "topology_unchanged_from_prepared_state": topology_unchanged,
                    "event_count_deltas_from_prepared_state": event_count_deltas,
                    "same_branch_persistence_path_clean": topology_unchanged
                    and event_count_deltas == [0, 0],
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
                row["same_branch_persistence_path_clean"]
                for row in horizon_rows
                if row["horizon_complete_steps"] <= required_horizon
            )
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
        row = {
            "branch_id": branch["branch_id"],
            "fixture_id": branch["fixture_id"],
            "preparation_id": pair["preparation_id"],
            "preparation_provenance": pair["provenance_class"],
            "write_status": pair["write_status"],
            "initial_separation": initial,
            "horizon_rows": horizon_rows,
            "matched_probe_rows": read_rows,
            "bounded_persistence_supported": persisted,
            "native_mediation_supported": native_read,
            "substrate_reduced_sensitivity_observed": reduced_read,
            "slow_cluster_retention_interpretation_allowed": slow_allowed,
            "local_evidence_ladder_rung": rung,
            "core_readback_supported": False,
            "closed_loop_supported": False,
        }
        branch_rows.append(row)
        if persisted:
            possibility = "retention_without_read"
            maximum_claim = (
                "bounded_synthetic_old_current_conditioned_joint_state_persistence_without_"
                "isolated_slow_cluster_or_native_read_effect"
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
                    "bounded_persistence_supported" if persisted else "not_supported"
                ),
                "read_effect_status": (
                    "native_mediation_candidate"
                    if native_read
                    else (
                        "substrate_reduced_only"
                        if reduced_read
                        else "not_supported"
                    )
                ),
                "write_effect_status": pair["write_status"],
                "closed_loop_status": "not_supported",
                "causal_possibility_class": possibility,
                "local_evidence_ladder_rung": rung,
                "maximum_claim": maximum_claim,
                "blocked_claims": blocked_claims,
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
        "scientific_acceptance = awaiting_human_review",
        "```",
        "",
        "## Interpretation",
        "",
        "GRV5 resolves the four causal arrows separately. An experiment-authored",
        "old-current state changes conductance at the first exact native transport",
        "reconstruction. The unchanged complete step reconstructs current and",
        "conductance again and erases that conductance inscription, but the transient",
        "write can leave a complete-step reached coherence/joint-state displacement.",
        "GRV5 therefore tests that reached pair separately from the stage-local pair.",
        "Direct authored conductance differences are overwritten by reconstruction.",
        "The old-current forming input is synthetic and not claimed runtime-reached;",
        "its large magnitude follows from the frozen `gamma = 1e-12` branch parameter",
        "and the preregistered 0.01 conductance-attenuation exponent.",
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
        "",
        "## Causal Boundaries",
        "",
        "- `P-W`: producer-authored conductance carrier; synthetic-valid only.",
        "- `P-J`: exact native stage response to a synthetic old-current input.",
        "- `P-J complete`: complete-step reached joint-state consequence of that input.",
        "- `P-J-sign`: confirms the source-current-squared write is sign-even.",
        "- Native complete-step persistence: evaluated after forming input stops.",
        "- Frozen-`W` response: reduced diagnostic; cannot upgrade native evidence.",
        "- External-current-like probe: analytical only; no native external-current input exists.",
        "- Canonical interventions: `grv5_intervention_registry.json`.",
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
        preparation_controls.append(
            {"branch_id": branch["branch_id"], **controls}
        )
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
        "retention_supported": any(
            row["bounded_persistence_supported"] for row in branch_rows
        ),
        "native_readback_supported": False,
        "writeback_supported": False,
        "closed_loop_supported": False,
        "grv_c5_candidate_pending_human_review": True,
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
                "bounded_synthetic_old_current_conditioned_joint_state_persistence_without_"
                "isolated_slow_cluster_or_native_readback"
                if summary["retention_supported"]
                else "stage_local_activity_conditioned_write_without_complete_step_persistence"
            ),
            "frozen_W_sensitivity_does_not_upgrade_native": True,
            "GRV_C5_candidate_pending_human_review": True,
        },
    }
    output_root = EXPERIMENT_ROOT / "outputs"
    result_path = output_root / "conductance_retention_probe.json"
    causal_path = output_root / "causal_role_matrix.json"
    intervention_path = output_root / "grv5_intervention_registry.json"
    write_json(
        result_path,
        artifact_envelope(
            payload,
            schema_version="b1_grv5_conductance_retention_probe_v1",
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
            schema_version="b1_grv5_causal_role_matrix_v1",
            generating_command=COMMAND,
            reproducibility_class="tolerance_reproducible",
        ),
    )
    intervention_payload = intervention_registry(preparation_controls)
    write_json(
        intervention_path,
        artifact_envelope(
            intervention_payload,
            schema_version="b1_grv5_intervention_registry_v1",
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
                "bounded_synthetic_old_current_conditioned_joint_state_persistence_without_"
                "isolated_slow_cluster_or_native_readback_pending_human_review"
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
