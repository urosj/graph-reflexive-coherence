"""Execute GRV3 causal-state closure, stratum admission, and gated Jacobians."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys
from typing import Any, Iterable

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
from state_codec import (
    BranchCoordinateChart,
    categorical_signature,
    physical_continuous_blocks,
    runtime_path_signature,
)

SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from pygrc.models import GRC9V3  # noqa: E402


COMMAND = (
    ".venv/bin/python "
    "experiments/2026-08-B1-GR-grc9v3-continuation-readback-verification/"
    "scripts/run_all.py --gate GRV3"
)
EXPERIMENT_RELATIVE = repo_relative(EXPERIMENT_ROOT)
GRV2_RESULT_REVISION = "e1dc01f4948b7791c733eb62c15179d04619cd8e"
GRV2_RECEIPT_SHA256 = "73450d2a445770fc3f4b0f2871d3d10c865e097fdd305d97945e41dd7b707c63"
GRV2_ACCEPTANCE_COMMIT = "b5506d9c5dcab787b602652549bfbf09054d53eb"


def _linf(left: Iterable[float], right: Iterable[float]) -> float:
    return max(
        (abs(float(a) - float(b)) for a, b in zip(left, right, strict=True)),
        default=0.0,
    )


def _block_errors(
    reference: dict[str, list[float]], observed: dict[str, list[float]]
) -> dict[str, float]:
    return {
        block: _linf(reference[block], observed[block]) for block in ("C", "W", "J")
    }


def _block_passes(
    errors: dict[str, float],
    reference: dict[str, list[float]],
    tolerances: dict[str, Any],
    horizon: int,
) -> bool:
    for block, error in errors.items():
        absolute = float(tolerances["absolute_tolerances"][block])
        relative = float(tolerances["relative_tolerances"][block])
        reference_norm = max((abs(value) for value in reference[block]), default=0.0)
        allowed = absolute + horizon * relative * max(1.0, reference_norm)
        if error > allowed:
            return False
    return True


def _variants(
    chart: BranchCoordinateChart,
    config: dict[str, Any],
) -> list[tuple[str, np.ndarray]]:
    base_model = GRC9V3.from_state(chart.base_state, chart.params)
    base = chart.encode_model(base_model)
    rows: list[tuple[str, np.ndarray]] = [("branch", base)]
    c_start, c_end = chart.block_slices["C"]
    if c_end > c_start:
        amplitude = float(config["grv3_b"]["finite_difference_steps"][0])
        for name, sign in (("C_positive", 1.0), ("C_negative", -1.0)):
            value = base.copy()
            value[c_start] += sign * amplitude
            rows.append((name, value))
    if "W" in chart.block_slices:
        value = base.copy()
        value[chart.block_slices["W"][0]] += float(
            config["counterfactuals"]["W_amplitude"]
        )
        rows.append(("W_positive", value))
    if "J" in chart.block_slices:
        for name, sign in (("J_positive", 1.0), ("J_negative", -1.0)):
            value = base.copy()
            value[chart.block_slices["J"][0]] += sign * float(
                config["counterfactuals"]["J_amplitude"]
            )
            rows.append((name, value))
    return rows


def codec_audit(
    model: GRC9V3,
    chart: BranchCoordinateChart,
    config: dict[str, Any],
    tolerances: dict[str, Any],
) -> dict[str, Any]:
    horizons = [int(value) for value in config["grv3_a"]["codec_horizons"]]
    maximum_horizon = max(horizons)
    variant_rows = []
    for variant_id, coordinate in _variants(chart, config):
        decoded = chart.decode_model(coordinate)
        round_trip = chart.encode_model(decoded)
        round_trip_error = _linf(coordinate.tolist(), round_trip.tolist())
        direct = chart.decode_model(coordinate)
        encoded_coordinate = coordinate.copy()
        horizon_rows = []
        for beat in range(1, maximum_horizon + 1):
            direct.step()
            encoded_step = chart.decode_model(encoded_coordinate)
            encoded_step.step()
            encoded_coordinate = chart.encode_model(encoded_step)
            if beat not in horizons:
                continue
            reference = physical_continuous_blocks(
                direct, chart.node_order, chart.edge_order
            )
            observed = physical_continuous_blocks(
                encoded_step, chart.node_order, chart.edge_order
            )
            errors = _block_errors(reference, observed)
            direct_signature = categorical_signature(
                direct,
                current_zero_band=float(config["grv3_b"]["current_zero_band"]),
            )
            encoded_signature = categorical_signature(
                encoded_step,
                current_zero_band=float(config["grv3_b"]["current_zero_band"]),
            )
            canonical = chart.decode_model(chart.encode_model(direct))
            canonical_blocks = physical_continuous_blocks(
                canonical, chart.node_order, chart.edge_order
            )
            canonical_errors = _block_errors(reference, canonical_blocks)
            direct_next = GRC9V3.from_state(
                deepcopy(direct.get_state()), dict(direct.get_params().raw_config)
            )
            canonical_next = GRC9V3.from_state(
                deepcopy(canonical.get_state()), dict(canonical.get_params().raw_config)
            )
            direct_next.step()
            canonical_next.step()
            next_reference = physical_continuous_blocks(
                direct_next, chart.node_order, chart.edge_order
            )
            next_errors = _block_errors(
                next_reference,
                physical_continuous_blocks(
                    canonical_next, chart.node_order, chart.edge_order
                ),
            )
            row_passed = bool(
                _block_passes(errors, reference, tolerances, beat)
                and direct_signature == encoded_signature
                and _block_passes(canonical_errors, reference, tolerances, beat)
                and _block_passes(next_errors, next_reference, tolerances, 1)
            )
            horizon_rows.append(
                {
                    "horizon": beat,
                    "transition_commutation_block_l_inf": errors,
                    "categorical_signature_equal": direct_signature
                    == encoded_signature,
                    "reached_state_canonicalization_block_l_inf": canonical_errors,
                    "canonicalized_next_step_block_l_inf": next_errors,
                    "row_passed": row_passed,
                }
            )
        variant_rows.append(
            {
                "variant_id": variant_id,
                "round_trip_l_inf": round_trip_error,
                "round_trip_passed": round_trip_error <= 1e-12,
                "horizon_rows": horizon_rows,
                "variant_passed": bool(
                    round_trip_error <= 1e-12
                    and len(horizon_rows) == len(horizons)
                    and all(row["row_passed"] for row in horizon_rows)
                ),
            }
        )
    passed = bool(variant_rows and all(row["variant_passed"] for row in variant_rows))
    return {
        **chart.descriptor(),
        "physical_projection": ["C", "W", "J"],
        "causal_projection": list(chart.admitted_blocks),
        "round_trip_status": "passed" if passed else "failed",
        "reached_state_canonicalization_status": "passed" if passed else "failed",
        "transition_commutation_status": "passed" if passed else "failed",
        "horizons": horizons,
        "stratum_policy": "closure_is_separate_from_derivative_stratum_admission",
        "variant_rows": variant_rows,
        "bounded_causal_closure_passed": passed,
        "global_markov_sufficiency_claimed": False,
    }


def _output_delta(
    reference: GRC9V3,
    observed: GRC9V3,
    node_order: tuple[int, ...],
    edge_order: tuple[int, ...],
) -> dict[str, Any]:
    left = physical_continuous_blocks(reference, node_order, edge_order)
    right = physical_continuous_blocks(observed, node_order, edge_order)
    errors = _block_errors(left, right)
    return {
        "block_l_inf": errors,
        "maximum_l_inf": max(errors.values(), default=0.0),
    }


def counterfactual_audit(
    model: GRC9V3,
    chart: BranchCoordinateChart,
    config: dict[str, Any],
    tolerances: dict[str, Any],
    reduction_status: dict[str, bool],
) -> dict[str, Any]:
    base = chart.encode_model(model)
    baseline = chart.decode_model(base)
    baseline.step()
    rows = []
    for intervention_id, block, sign, amplitude in (
        (
            "matched_CJ_different_W",
            "W",
            1.0,
            float(config["counterfactuals"]["W_amplitude"]),
        ),
        (
            "matched_CW_positive_J",
            "J",
            1.0,
            float(config["counterfactuals"]["J_amplitude"]),
        ),
        (
            "matched_CW_sign_reversed_J",
            "J",
            -1.0,
            float(config["counterfactuals"]["J_amplitude"]),
        ),
    ):
        coordinate = base.copy()
        coordinate[chart.block_slices[block][0]] += sign * amplitude
        candidate = chart.decode_model(coordinate)
        candidate.step()
        delta = _output_delta(baseline, candidate, chart.node_order, chart.edge_order)
        threshold = float(tolerances["absolute_tolerances"][block])
        rows.append(
            {
                "intervention_id": intervention_id,
                "block": block,
                "amplitude": sign * amplitude,
                "pair_class": "synthetic_valid_not_runtime_reached_pair",
                "structural_validity": "passed",
                "constitutive_consistency": "not_established",
                "runtime_reachability": "not_established",
                "output_delta": delta,
                "resolved_counterfactual_sensitivity": delta["maximum_l_inf"]
                > threshold,
            }
        )
    derived_state = deepcopy(model.get_state())
    for node_id in chart.node_order:
        derived_state.potential[node_id] = float(
            derived_state.potential.get(node_id, 0.0)
        ) + float(config["counterfactuals"]["derived_surface_amplitude"])
    derived = GRC9V3.from_state(derived_state, dict(model.get_params().raw_config))
    derived.step()
    derived_delta = _output_delta(baseline, derived, chart.node_order, chart.edge_order)
    rows.append(
        {
            "intervention_id": "branch_consistent_vs_perturbed_derived_Phi",
            "block": "Phi",
            "amplitude": float(config["counterfactuals"]["derived_surface_amplitude"]),
            "pair_class": "synthetic_valid_not_runtime_reached_pair",
            "structural_validity": "passed",
            "constitutive_consistency": "failed_overwritten_by_complete_step",
            "runtime_reachability": "not_established",
            "output_delta": derived_delta,
            "resolved_counterfactual_sensitivity": derived_delta["maximum_l_inf"]
            > float(tolerances["absolute_tolerances"]["derived_surface"]),
        }
    )
    decisions = {}
    for block, reduction_key in (("W", "C"), ("J", "C_W")):
        relevant = [row for row in rows if row["block"] == block]
        decisions[block] = {
            "counterfactual_sensitive": any(
                row["resolved_counterfactual_sensitivity"] for row in relevant
            ),
            "constitutively_independent": False,
            "runtime_causal_independent": False,
            "runtime_reached_pair_available": False,
            "eliminable_on_declared_bounded_envelope": bool(
                reduction_status[reduction_key]
            ),
            "global_eliminability_claimed": False,
        }
    return {"rows": rows, "candidate_block_decisions": decisions}


def _stratum_margin(model: GRC9V3) -> dict[str, float]:
    state = model.get_state()
    return {
        "current_sign_identity": min(
            (abs(float(edge.flux_uv)) for edge in state.port_edges.values()),
            default=0.0,
        ),
        "coherence_positivity": min(
            (float(node.coherence) for node in state.nodes.values()), default=0.0
        ),
        "conductance_positivity": min(
            (float(value) for value in state.base_conductance.values()),
            default=0.0,
        ),
    }


def _flatten_numbers(value: Any) -> list[float]:
    if isinstance(value, bool):
        return []
    if isinstance(value, (int, float)):
        return [float(value)]
    if isinstance(value, dict):
        result: list[float] = []
        for key in sorted(value, key=str):
            result.extend(_flatten_numbers(value[key]))
        return result
    if isinstance(value, (list, tuple)):
        result = []
        for child in value:
            result.extend(_flatten_numbers(child))
        return result
    return []


def _smooth_response_surfaces(
    model: GRC9V3, chart: BranchCoordinateChart
) -> dict[str, list[float]]:
    state = model.get_state()
    return {
        "Phi": [float(state.potential[node_id]) for node_id in chart.node_order],
        "G": [
            float(value)
            for node_id in chart.node_order
            for value in state.nodes[node_id].gradient_row_basis
        ],
        "Hs": [
            float(value)
            for node_id in chart.node_order
            for value in state.nodes[node_id].signed_hessian_row_basis
        ],
        "Kcache": _flatten_numbers(
            state.cached_quantities.get("hybrid_node_tensors", {})
        ),
    }


def _matrix_diagnostics(
    matrix: np.ndarray,
    chart: BranchCoordinateChart,
    config: dict[str, Any],
) -> dict[str, Any]:
    eigenvalues, right_vectors = np.linalg.eig(matrix)
    left_values, left_vectors = np.linalg.eig(matrix.T)
    right_residuals = []
    participation = []
    slices = chart.block_slices
    for index, value in enumerate(eigenvalues):
        vector = right_vectors[:, index]
        right_residuals.append(
            float(np.linalg.norm(matrix @ vector - value * vector, ord=2))
        )
        denominator = float(np.vdot(vector, vector).real)
        participation.append(
            {
                block: float(
                    np.vdot(vector[start:end], vector[start:end]).real
                    / max(denominator, 1e-300)
                )
                for block, (start, end) in slices.items()
            }
        )
    left_residuals = [
        float(
            np.linalg.norm(
                matrix.T @ left_vectors[:, index]
                - left_values[index] * left_vectors[:, index],
                ord=2,
            )
        )
        for index in range(len(left_values))
    ]
    mode_rows = []
    for index, value in enumerate(eigenvalues):
        magnitude = abs(value)
        if magnitude > 1.0 + 1e-6:
            classification = "unstable"
        elif abs(magnitude - 1.0) <= 1e-6:
            classification = "neutral_or_marginal"
        elif abs(value.imag) > 1e-8:
            classification = "stable_oscillatory"
        elif magnitude >= 0.9:
            classification = "stable_slow"
        else:
            classification = "stable_fast_or_intermediate"
        mode_rows.append(
            {
                "mode_index": index,
                "eigenvalue": {"real": float(value.real), "imag": float(value.imag)},
                "magnitude": float(magnitude),
                "classification": classification,
                "right_residual_l2": right_residuals[index],
                "block_participation": participation[index],
                "retention_interpretation_allowed": False,
            }
        )
    finite_horizon = []
    for horizon in config["grv3_a"]["codec_horizons"]:
        propagator = np.linalg.matrix_power(matrix, int(horizon))
        singular_values = np.linalg.svd(propagator, compute_uv=False)
        finite_horizon.append(
            {
                "horizon_complete_beats": int(horizon),
                "largest_singular_value": float(max(singular_values, default=0.0)),
                "state_norm": "euclidean_on_declared_tangent_coordinate",
            }
        )
    condition = float(np.linalg.cond(right_vectors))
    clusters = [
        {
            "cluster_id": f"mode-{row['mode_index']}",
            "mode_indices": [row["mode_index"]],
            "classification": row["classification"],
            "retention_interpretation_allowed": False,
        }
        for row in mode_rows
    ]
    return {
        "modes": mode_rows,
        "clusters": clusters,
        "maximum_right_residual_l2": max(right_residuals, default=0.0),
        "maximum_left_residual_l2": max(left_residuals, default=0.0),
        "eigenvector_condition_number": condition,
        "finite_horizon_nonnormal_diagnostics": finite_horizon,
        "nonnormal_primary_mode": "finite_horizon",
        "fast_slow_status": "not_identifiable_without_separate_cluster_separation_review",
        "conservation_mode_policy": "removed_by_zero_sum_C_tangent_basis",
        "gauge_mode_status": "none_declared_in_admitted_coordinate",
        "branch_tangent_status": "not_separately_identified",
    }


def _response_jacobians(
    chart: BranchCoordinateChart,
    base_coordinate: np.ndarray,
    step_size: float,
) -> dict[str, list[list[float]]]:
    matrices: dict[str, np.ndarray] = {}
    for column in range(len(base_coordinate)):
        plus_coordinate = base_coordinate.copy()
        minus_coordinate = base_coordinate.copy()
        plus_coordinate[column] += step_size
        minus_coordinate[column] -= step_size
        plus = chart.decode_model(plus_coordinate)
        minus = chart.decode_model(minus_coordinate)
        plus.step()
        minus.step()
        plus_surfaces = _smooth_response_surfaces(plus, chart)
        minus_surfaces = _smooth_response_surfaces(minus, chart)
        for surface in plus_surfaces:
            if surface not in matrices:
                matrices[surface] = np.zeros(
                    (len(plus_surfaces[surface]), len(base_coordinate)), dtype=float
                )
            matrices[surface][:, column] = (
                np.asarray(plus_surfaces[surface], dtype=float)
                - np.asarray(minus_surfaces[surface], dtype=float)
            ) / (2.0 * step_size)
    return {key: value.tolist() for key, value in matrices.items()}


def stratum_and_jacobian_audit(
    model: GRC9V3,
    chart: BranchCoordinateChart,
    config: dict[str, Any],
    tolerances: dict[str, Any],
) -> dict[str, Any]:
    base_coordinate = chart.encode_model(model)
    baseline_signature = categorical_signature(
        model,
        current_zero_band=float(config["grv3_b"]["current_zero_band"]),
    )
    baseline_margin = _stratum_margin(model)
    minimum_margin = float(config["grv3_b"]["minimum_positive_stratum_margin"])
    column_rows = []
    matrices: list[list[list[float]]] = []
    all_columns_admitted = True
    for step_size in [
        float(value) for value in config["grv3_b"]["finite_difference_steps"]
    ]:
        matrix = np.zeros((len(base_coordinate), len(base_coordinate)), dtype=float)
        step_rows = []
        for column, label in enumerate(chart.coordinate_labels):
            plus_coordinate = base_coordinate.copy()
            minus_coordinate = base_coordinate.copy()
            plus_coordinate[column] += step_size
            minus_coordinate[column] -= step_size
            try:
                plus = chart.decode_model(plus_coordinate)
                minus = chart.decode_model(minus_coordinate)
                pre_plus = categorical_signature(
                    plus,
                    current_zero_band=float(config["grv3_b"]["current_zero_band"]),
                )
                pre_minus = categorical_signature(
                    minus,
                    current_zero_band=float(config["grv3_b"]["current_zero_band"]),
                )
                plus_result = plus.step()
                minus_result = minus.step()
                post_plus = categorical_signature(
                    plus,
                    current_zero_band=float(config["grv3_b"]["current_zero_band"]),
                )
                post_minus = categorical_signature(
                    minus,
                    current_zero_band=float(config["grv3_b"]["current_zero_band"]),
                )
                same_pre = pre_plus == baseline_signature == pre_minus
                same_post = post_plus == post_minus
                same_path = runtime_path_signature(plus) == runtime_path_signature(
                    minus
                )
                positive_margin = (
                    baseline_margin["current_sign_identity"] > minimum_margin
                )
                admitted = bool(
                    same_pre
                    and same_post
                    and same_path
                    and positive_margin
                    and not plus_result.events
                    and not minus_result.events
                )
                reason = (
                    "admitted"
                    if admitted
                    else (
                        "blocked_zero_current_sink_basin_identity_margin"
                        if not positive_margin
                        else "blocked_categorical_or_runtime_path_change"
                    )
                )
                if admitted:
                    matrix[:, column] = (
                        chart.encode_model(plus) - chart.encode_model(minus)
                    ) / (2.0 * step_size)
            except (ValueError, ArithmeticError) as error:
                same_pre = False
                same_post = False
                same_path = False
                positive_margin = False
                admitted = False
                reason = (
                    f"blocked_invalid_two_sided_intervention:{type(error).__name__}"
                )
            row = {
                "column_index": column,
                "column_label": label,
                "step_size": step_size,
                "baseline_stratum_margins": baseline_margin,
                "positive_two_sided_stratum_margin": positive_margin,
                "same_pre_step_signature": same_pre,
                "same_post_step_signature": same_post,
                "same_runtime_path": same_path,
                "derivative_column_admitted": admitted,
                "decision": reason,
            }
            step_rows.append(row)
            all_columns_admitted = all_columns_admitted and admitted
        column_rows.extend(step_rows)
        if all(row["derivative_column_admitted"] for row in step_rows):
            matrices.append(matrix.tolist())
    column_gate_passed = bool(
        all_columns_admitted
        and len(matrices) == len(config["grv3_b"]["finite_difference_steps"])
    )
    convergence_errors = []
    if column_gate_passed:
        for left, right in zip(matrices, matrices[1:], strict=False):
            left_array = np.asarray(left, dtype=float)
            right_array = np.asarray(right, dtype=float)
            convergence_errors.append(
                float(
                    np.linalg.norm(left_array - right_array, ord=2)
                    / max(1.0, float(np.linalg.norm(right_array, ord=2)))
                )
            )
    convergence_passed = bool(
        column_gate_passed
        and all(
            value <= float(tolerances["adjacent_step_relative_column_error_max"])
            for value in convergence_errors
        )
    )
    square_admitted = bool(column_gate_passed and convergence_passed)
    if square_admitted:
        selected = np.asarray(matrices[-1], dtype=float)
        diagnostics = _matrix_diagnostics(selected, chart, config)
        jacobian: list[list[float]] | None = selected.tolist()
        response_jacobians = _response_jacobians(
            chart,
            base_coordinate,
            float(config["grv3_b"]["finite_difference_steps"][-1]),
        )
    else:
        diagnostics = {
            "modes": [],
            "clusters": [],
            "blocked_reason": (
                "non_smooth_stratum"
                if not column_gate_passed
                else "finite_difference_nonconvergence"
            ),
        }
        jacobian = None
        response_jacobians = {}
    if square_admitted:
        status = "admitted"
    elif not column_gate_passed:
        status = "blocked_non_smooth_stratum"
    else:
        status = "blocked_finite_difference_nonconvergence"
    return {
        "causal_coordinate": list(chart.admitted_blocks),
        "coordinate_order": list(chart.coordinate_labels),
        "baseline_categorical_signature": baseline_signature,
        "baseline_stratum_margins": baseline_margin,
        "column_audits": column_rows,
        "all_columns_admitted": all_columns_admitted,
        "column_gate_passed": column_gate_passed,
        "finite_difference_convergence": {
            "adjacent_matrix_relative_errors": convergence_errors,
            "maximum_allowed": float(
                tolerances["adjacent_step_relative_column_error_max"]
            ),
            "passed": convergence_passed,
        },
        "square_transition_jacobian_status": status,
        "jacobian": jacobian,
        "candidate_step_matrices": matrices if square_admitted else [],
        "temporal_mode_diagnostics": diagnostics,
        "smooth_response_jacobians": response_jacobians,
        "slow_cluster_status": (
            "classified_without_retention_promotion"
            if square_admitted
            else "not_computed_derivative_blocked"
        ),
        "response_jacobian_status": (
            "computed" if square_admitted else "blocked_with_input_derivative"
        ),
        "categorical_surface_status": "recorded_separately",
        "stratum_blocked_is_not_unconverged": not column_gate_passed,
    }


def field_inventory() -> list[dict[str, Any]]:
    return [
        {
            "field": "C",
            "classification": "candidate_continuous_causal_coordinate",
            "basis": "zero_sum",
        },
        {
            "field": "W",
            "classification": "candidate_continuous_surface_pending_independence_tests",
        },
        {
            "field": "J",
            "classification": "candidate_continuous_surface_pending_independence_tests",
        },
        {
            "field": "topology_and_port_orientation",
            "classification": "causal_discrete_fixed_stratum",
        },
        {
            "field": "budget_target",
            "classification": "fixed_exogenous_constraint_parameter",
        },
        {
            "field": "params",
            "classification": "fixed_exogenous_transition_identity",
        },
        {
            "field": "step_index_and_time",
            "classification": "deterministic_administrative_advancement_on_tested_envelope",
        },
        {
            "field": "rng_state",
            "classification": "fixed_discrete_state_no_random_path_exercised",
        },
        {
            "field": "hierarchy_and_event_registries",
            "classification": "causal_discrete_fixed_empty_stratum",
        },
        {
            "field": "node_values_edge_values",
            "classification": "excluded_unknown_globally_bounded_by_codec_only_here",
        },
        {
            "field": "cached_quantities",
            "classification": "mixed_reconstructed_and_observer_surfaces_bounded_by_codec_only_here",
        },
        {
            "field": "Phi_G_Hs_Kcache_labels_identity",
            "classification": "reconstructed_or_categorical_response_surfaces",
        },
        {
            "field": "observables_event_log",
            "classification": "observer_history_on_no_event_tested_stratum",
        },
    ]


def validate_prerequisite() -> tuple[dict[str, Any], dict[str, Any]]:
    receipt = read_json(EXPERIMENT_ROOT / "outputs/gates/grv2_result_receipt.json")
    anchor = read_json(EXPERIMENT_ROOT / "outputs/gates/grv2_acceptance_anchor.json")
    validate_receipt(receipt)
    validate_acceptance_anchor(anchor)
    if receipt["receipt_payload_sha256"] != GRV2_RECEIPT_SHA256:
        raise ValueError("GRV2 receipt identity mismatch")
    if (
        anchor["result_revision"] != GRV2_RESULT_REVISION
        or anchor["receipt_payload_sha256"] != GRV2_RECEIPT_SHA256
    ):
        raise ValueError("GRV2 acceptance anchor does not bind the required result")
    if not prerequisite_is_authorized(anchor):
        raise ValueError("GRV2 prerequisite is not accepted")
    return receipt, anchor


def protected_manifest_v3() -> dict[str, Any]:
    predecessor_path = EXPERIMENT_ROOT / "outputs/protected_path_manifest_v2.json"
    predecessor = read_json(predecessor_path)
    relative_paths = [row["path"] for row in predecessor["payload"]["files"]]
    current = file_manifest(relative_paths)
    payload = {
        "manifest_id": "b1_grv3_protected_paths_v3",
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
        schema_version="b1_grv3_protected_path_manifest_v3",
        generating_command=COMMAND,
    )


def write_report(payload: dict[str, Any]) -> Path:
    summary = payload["summary"]
    report = EXPERIMENT_ROOT / "reports/b1_grv3_causal_state_and_transition_jacobian.md"
    lines = [
        "# B1-GR GRV3 Causal State And Transition-Jacobian Gate",
        "",
        "## Result",
        "",
        "```text",
        "gate = GRV3",
        f"mechanical_status = {summary['mechanical_status']}",
        "scientific_acceptance = awaiting_human_review",
        f"branches_audited = {summary['branch_count']}",
        f"bounded_causal_closure_candidates = {summary['causal_closure_pass_count']}",
        f"full_C_W_J_square_jacobians_admitted = {summary['full_C_W_J_jacobian_admitted_count']}",
        f"reduced_coordinate_matrices_admitted = {summary['reduced_coordinate_matrix_count']}",
        f"branches_with_reduced_temporal_coordinates = {summary['branches_with_admitted_reduced_temporal_coordinate']}",
        f"branches_without_admitted_temporal_coordinates = {summary['branches_without_any_admitted_temporal_coordinate']}",
        "continuation = unsupported",
        "retention = unsupported",
        "readback = unsupported",
        "writeback = unsupported",
        "runtime_change_authorized = false",
        "```",
        "",
        "GRV3 begins with causal closure rather than a numerical Jacobian. All 48",
        "accepted GRV2 rows are consumed in committed registry order. The 32 symmetry",
        "orbits remain an interpretation of dependence and do not reduce execution",
        "scope or select branches after outcomes are visible.",
        "",
        "## GRV3-A: Causal Closure",
        "",
        "The branch-relative `(C,W,J)` codec is tested for round trip, reached-state",
        f"canonicalization, and complete-step commutation on `{summary['causal_closure_pass_count']}`",
        f"of `{summary['branch_count']}` branches through horizons `1, 2, 5, 10`.",
        "This is bounded branch-envelope evidence only. It does not establish global",
        "Markov sufficiency or global eliminability of omitted runtime fields.",
        "",
        "## GRV3-B: Classical Derivative Admission",
        "",
        "All accepted rows satisfy the GRV2 authoritative zero-current tolerance;",
        f"`{summary['exact_zero_current_margin_branch_count']}` rows are exactly on the",
        "current-sign boundary, while the remaining rows retain only small numerical",
        "distance from it. Every full `(C,W,J)` chart has at least one blocked column,",
        "so no complete `(C,W,J)` matrix is emitted. A failed stratum column is blocked,",
        "not reported as an unconverged derivative.",
        "",
        f"The frozen reduction audit admits `{summary['reduced_coordinate_matrix_count']}`",
        f"reduced matrices across `{summary['branches_with_admitted_reduced_temporal_coordinate']}`",
        "branches. Both `C-W` and `C` candidates are retained where admitted; GRV3 does",
        "not select one primary coordinate after seeing spectra. These are bounded",
        "branch-envelope reductions, not global elimination of `W` or `J`.",
        "",
        "## GRV3-C: Response And Categorical Surfaces",
        "",
        "Smooth response Jacobians are computed only for admitted reduced-coordinate",
        "matrices and remain blocked for unavailable charts. Current-sign, sink, basin,",
        "event, and budget-active-set behavior is retained as categorical threshold",
        "evidence rather than inserted into an eigensystem.",
        "",
        "## Claim Boundary",
        "",
        "A GRV3-A pass may support a bounded causal-strong-branch candidate after human",
        "review. It does not by itself complete GRV-C4, which also requires admitted",
        "GRV3-B/C evidence and GRV4 frozen/full comparison. A blocked Jacobian is a",
        "scientific boundary result, not stability, continuation, retention, read-back,",
        "or write-back evidence.",
    ]
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report


def run_grv3() -> None:
    if git("status", "--porcelain"):
        raise SystemExit("GRV3 requires a clean committed P3 input revision")
    receipt2, anchor2 = validate_prerequisite()
    config = read_json(EXPERIMENT_ROOT / "configs/grv3_causal_state.json")
    tolerances = read_json(EXPERIMENT_ROOT / "configs/numerical_tolerances.json")
    registry_path = EXPERIMENT_ROOT / config["branch_scope"]["source_registry_path"]
    if sha256_file(registry_path) != config["branch_scope"]["source_registry_sha256"]:
        raise ValueError("GRV2 fixed-branch registry file digest mismatch")
    registry = read_json(registry_path)
    branches = [
        row for row in registry["payload"]["branches"] if row["branch_certified"]
    ]
    if len(branches) != int(config["branch_scope"]["expected_selected_branch_count"]):
        raise ValueError("GRV3 branch scope does not contain exactly 48 accepted rows")
    input_revision = git("rev-parse", "HEAD")
    input_tree = file_manifest(tracked_files([EXPERIMENT_RELATIVE]))
    branch_rows = []
    intervention_rows = []
    slow_rows = []
    for branch in branches:
        snapshot_path = REPO_ROOT / branch["state_snapshot_path"]
        if sha256_file(snapshot_path) != branch["state_snapshot_sha256"]:
            raise ValueError(f"branch snapshot digest mismatch: {branch['branch_id']}")
        model = GRC9V3.load(str(snapshot_path))
        full_chart = BranchCoordinateChart.from_model(model, ("C", "W", "J"))
        codec = codec_audit(model, full_chart, config, tolerances)
        reduction_audits = {}
        reduction_status = {}
        reduction_charts = {}
        for blocks in (("C", "W"), ("C",)):
            chart = BranchCoordinateChart.from_model(model, blocks)
            audit = codec_audit(model, chart, config, tolerances)
            key = "C_W" if blocks == ("C", "W") else "C"
            reduction_audits[key] = audit
            reduction_status[key] = bool(audit["bounded_causal_closure_passed"])
            reduction_charts[key] = chart
        counterfactual = counterfactual_audit(
            model, full_chart, config, tolerances, reduction_status
        )
        coordinate_jacobians = {
            "C_W_J": stratum_and_jacobian_audit(model, full_chart, config, tolerances)
        }
        for key in ("C_W", "C"):
            if reduction_status[key]:
                coordinate_jacobians[key] = stratum_and_jacobian_audit(
                    model, reduction_charts[key], config, tolerances
                )
            else:
                coordinate_jacobians[key] = {
                    "causal_coordinate": list(reduction_charts[key].admitted_blocks),
                    "coordinate_order": list(reduction_charts[key].coordinate_labels),
                    "square_transition_jacobian_status": "blocked_by_codec",
                    "jacobian": None,
                    "temporal_mode_diagnostics": {
                        "modes": [],
                        "clusters": [],
                        "blocked_reason": "reduction_codec_failed",
                    },
                    "smooth_response_jacobians": {},
                    "slow_cluster_status": "not_computed_codec_blocked",
                    "response_jacobian_status": "blocked_with_codec",
                    "categorical_surface_status": "retained_in_full_chart_audit",
                }
        admitted_coordinates = [
            key
            for key, audit in coordinate_jacobians.items()
            if audit["square_transition_jacobian_status"] == "admitted"
        ]
        causal_closure = bool(codec["bounded_causal_closure_passed"])
        row = {
            "branch_id": branch["branch_id"],
            "fixture_id": branch["fixture_id"],
            "symmetry_orbit_id": branch["symmetry_orbit_id"],
            "source_snapshot_path": branch["state_snapshot_path"],
            "source_snapshot_sha256": branch["state_snapshot_sha256"],
            "source_branch_class": branch["branch_class"],
            "causal_codec": codec,
            "candidate_reduction_audits": reduction_audits,
            "counterfactual_closure": counterfactual,
            "coordinate_stratum_and_jacobian_audits": coordinate_jacobians,
            "full_C_W_J_stratum_and_jacobian": coordinate_jacobians["C_W_J"],
            "admitted_temporal_coordinate_candidates": admitted_coordinates,
            "primary_temporal_coordinate_selected": False,
            "causal_strong_branch_candidate": causal_closure,
            "causal_strong_branch_status": (
                "bounded_candidate_pending_human_review"
                if causal_closure
                else "blocked_by_codec"
            ),
            "temporal_mode_evidence_supported": bool(admitted_coordinates),
            "continuation_claim_allowed": False,
            "retention_claim_allowed": False,
            "readback_claim_allowed": False,
            "writeback_claim_allowed": False,
        }
        branch_rows.append(row)
        intervention_rows.append(
            {
                "branch_id": branch["branch_id"],
                "codec_interventions": [
                    variant["variant_id"] for variant in codec["variant_rows"]
                ],
                "counterfactual_rows": counterfactual["rows"],
                "clone_first": True,
                "live_get_state_mutated": False,
            }
        )
        for key, audit in coordinate_jacobians.items():
            diagnostics = audit["temporal_mode_diagnostics"]
            slow_rows.append(
                {
                    "branch_id": branch["branch_id"],
                    "coordinate_candidate": key,
                    "status": audit["slow_cluster_status"],
                    "clusters": diagnostics.get("clusters", []),
                    "modes": diagnostics.get("modes", []),
                    "retention_interpretation_allowed": False,
                }
            )
    causal_count = sum(
        bool(row["causal_strong_branch_candidate"]) for row in branch_rows
    )
    admitted_matrix_count = sum(
        audit["square_transition_jacobian_status"] == "admitted"
        for row in branch_rows
        for audit in row["coordinate_stratum_and_jacobian_audits"].values()
    )
    admitted_branch_count = sum(
        bool(row["admitted_temporal_coordinate_candidates"]) for row in branch_rows
    )
    full_matrix_count = sum(
        row["full_C_W_J_stratum_and_jacobian"]["square_transition_jacobian_status"]
        == "admitted"
        for row in branch_rows
    )
    admitted_column_count = sum(
        bool(column["derivative_column_admitted"])
        for row in branch_rows
        for audit in row["coordinate_stratum_and_jacobian_audits"].values()
        for column in audit.get("column_audits", [])
    )
    blocked_column_count = sum(
        not bool(column["derivative_column_admitted"])
        for row in branch_rows
        for audit in row["coordinate_stratum_and_jacobian_audits"].values()
        for column in audit.get("column_audits", [])
    )
    exact_zero_margin_branch_count = sum(
        row["full_C_W_J_stratum_and_jacobian"]["baseline_stratum_margins"][
            "current_sign_identity"
        ]
        == 0.0
        for row in branch_rows
    )
    summary = {
        "mechanical_status": (
            "passed" if causal_count == len(branch_rows) else "partial"
        ),
        "branch_count": len(branch_rows),
        "unique_symmetry_orbit_count": len(
            {row["symmetry_orbit_id"] for row in branch_rows}
        ),
        "causal_closure_pass_count": causal_count,
        "full_C_W_J_jacobian_admitted_count": full_matrix_count,
        "reduced_coordinate_matrix_count": admitted_matrix_count - full_matrix_count,
        "branches_with_admitted_reduced_temporal_coordinate": admitted_branch_count,
        "branches_without_any_admitted_temporal_coordinate": len(branch_rows)
        - admitted_branch_count,
        "admitted_derivative_column_count": admitted_column_count,
        "blocked_derivative_column_count": blocked_column_count,
        "exact_zero_current_margin_branch_count": exact_zero_margin_branch_count,
        "all_branches_consumed_without_symmetry_reduction": len(branch_rows) == 48,
        "grv3_a_status": (
            "bounded_candidate_passed"
            if causal_count == len(branch_rows)
            else "partial"
        ),
        "grv3_b_status": (
            "partial_reduced_coordinate_temporal_mode_evidence"
            if admitted_matrix_count > 0
            else "blocked_on_non_smooth_stratum"
        ),
        "grv3_c_status": (
            "partial_reduced_coordinate_response_evidence_and_full_categorical_surfaces"
            if admitted_matrix_count > 0
            else "categorical_surfaces_only_smooth_responses_blocked"
        ),
        "grv_c4_supported": False,
    }
    payload = {
        "gate_id": "GRV3",
        "source_contract": {
            "grv2_result_revision": GRV2_RESULT_REVISION,
            "grv2_receipt_payload_sha256": GRV2_RECEIPT_SHA256,
            "grv2_acceptance_commit": GRV2_ACCEPTANCE_COMMIT,
            "fixed_branch_registry_path": repo_relative(registry_path),
            "fixed_branch_registry_sha256": sha256_file(registry_path),
        },
        "branch_selection": {
            **config["branch_scope"],
            "selected_branch_ids": [row["branch_id"] for row in branch_rows],
            "selected_branch_ids_sha256": semantic_digest(
                [row["branch_id"] for row in branch_rows]
            ),
        },
        "causal_field_inventory": field_inventory(),
        "branches": branch_rows,
        "summary": summary,
        "claim_boundary": {
            "causal_strong_branch_candidate": causal_count > 0,
            "full_C_W_J_transition_jacobian_supported": full_matrix_count > 0,
            "bounded_reduced_coordinate_transition_jacobian_supported": admitted_matrix_count
            > 0,
            "bounded_reduced_coordinate_temporal_modes_supported": admitted_matrix_count
            > 0,
            "primary_temporal_coordinate_selected": False,
            "continuation_supported": False,
            "retention_supported": False,
            "readback_supported": False,
            "writeback_supported": False,
            "runtime_changed": False,
            "src_changed": False,
        },
    }
    output_root = EXPERIMENT_ROOT / "outputs"
    result = artifact_envelope(
        payload,
        schema_version="b1_grv3_complete_step_jacobians_v1",
        generating_command=COMMAND,
        reproducibility_class="tolerance_reproducible",
    )
    result_path = output_root / "complete_step_jacobians.json"
    write_json(result_path, result)
    slow_path = output_root / "slow_cluster_registry.json"
    write_json(
        slow_path,
        artifact_envelope(
            {
                "gate_id": "GRV3",
                "rows": slow_rows,
                "cluster_count": sum(len(row["clusters"]) for row in slow_rows),
                "retention_claim_allowed": False,
            },
            schema_version="b1_grv3_slow_cluster_registry_v1",
            generating_command=COMMAND,
            reproducibility_class="tolerance_reproducible",
        ),
    )
    intervention_path = output_root / "grv3_intervention_registry.json"
    write_json(
        intervention_path,
        artifact_envelope(
            {"gate_id": "GRV3", "rows": intervention_rows},
            schema_version="b1_grv3_intervention_registry_v1",
            generating_command=COMMAND,
            reproducibility_class="tolerance_reproducible",
        ),
    )
    protected_path = output_root / "protected_path_manifest_v3.json"
    protected = protected_manifest_v3()
    if not protected["payload"]["unchanged_successor"]:
        raise ValueError("protected source/spec/test paths changed since GRV2")
    write_json(protected_path, protected)
    report_path = write_report(payload)
    artifacts = [
        result_path,
        slow_path,
        intervention_path,
        protected_path,
        report_path,
    ]
    baseline = read_json(output_root / "baseline_manifest.json")["payload"]
    receipt = finalize_receipt(
        {
            "gate_id": "GRV3",
            "input_execution_revision": input_revision,
            "substrate_base_revision": baseline["substrate_base_revision"],
            "input_experiment_tree_sha256": input_tree["tree_sha256"],
            "prerequisite_result_receipt_digests": [GRV2_RECEIPT_SHA256],
            "prerequisite_acceptance_anchors": [
                {
                    "gate_id": "GRV2",
                    "immutable_ref": f"git:{GRV2_ACCEPTANCE_COMMIT}",
                    "anchor_payload_sha256": semantic_digest(anchor2),
                }
            ],
            "output_artifact_digests": {
                path.relative_to(EXPERIMENT_ROOT).as_posix(): sha256_file(path)
                for path in sorted(artifacts)
            },
            "status": "awaiting_scientific_review",
            "blocked_gates": [f"GRV{index}" for index in range(4, 9)],
            "claim_ceiling": "bounded_GRV3_A_causal_strong_branch_candidate_and_only_admitted_GRV3_B_C_temporal_mode_evidence_pending_human_review",
            "prerequisite_receipt_status": receipt2["status"],
            "grv3_summary": summary,
        }
    )
    validate_receipt(receipt)
    write_json(output_root / "gates/grv3_result_receipt.json", receipt)


def main() -> None:
    run_grv3()
    print("GRV3 mechanically validated; scientific acceptance anchor is pending.")


if __name__ == "__main__":
    main()
