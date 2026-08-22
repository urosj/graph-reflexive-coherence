"""Execute GRV4 fixed-conductance sign and full-recurrence comparisons."""

from __future__ import annotations

from copy import deepcopy
import math
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
from grv4_hardening import (
    build_probe_directions,
    conjugacy_errors,
    finite_difference_potential_audit,
    graph_connectivity,
    metric_subspace_comparison,
    positive_condition_number,
    principal_angle,
    real_invariant_basis,
    relative_matrix_error,
    robust_multiplier_rows,
    structural_temporal_diagnostics,
)
from state_codec import BranchCoordinateChart

SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from pygrc.models import GRC9V3  # noqa: E402
from pygrc.models.grc_9_v3_runtime import compute_flux, compute_potential  # noqa: E402


COMMAND = (
    ".venv/bin/python "
    "experiments/2026-08-B1-GR-grc9v3-continuation-readback-verification/"
    "scripts/run_all.py --gate GRV4"
)
EXPERIMENT_RELATIVE = repo_relative(EXPERIMENT_ROOT)
GRV3_RESULT_REVISION = "0dedbf96f2a067442ec42ab67707aa694a35fdec"
GRV3_RECEIPT_SHA256 = "83a2650f57fe3d1a814155bf6e8621881d01468b36cde0f1b460af02339b92cc"
GRV3_ACCEPTANCE_COMMIT = "8b82df4f077cecf3af780165e71bfb42b6bf5575"


def _linf(left: Iterable[float], right: Iterable[float]) -> float:
    return max(
        (abs(float(a) - float(b)) for a, b in zip(left, right, strict=True)),
        default=0.0,
    )


def _complex_record(value: complex) -> dict[str, float]:
    return {"real": float(value.real), "imag": float(value.imag)}


def _ordered_eigenvalues(matrix: np.ndarray) -> list[complex]:
    return sorted(
        (complex(value) for value in np.linalg.eigvals(matrix)),
        key=lambda value: (abs(value), value.real, value.imag),
    )


def eigenvalue_set_error(left: np.ndarray, right: np.ndarray) -> float | None:
    left_values = list(np.linalg.eigvals(left))
    unmatched = list(np.linalg.eigvals(right))
    if len(left_values) != len(unmatched):
        return None
    maximum = 0.0
    for value in left_values:
        index = min(
            range(len(unmatched)), key=lambda item: abs(value - unmatched[item])
        )
        maximum = max(maximum, float(abs(value - unmatched[index])))
        unmatched.pop(index)
    return maximum


def multiplier_classification(
    matrix: np.ndarray, *, unstable_slack: float, neutral_tolerance: float
) -> dict[str, Any]:
    rows = []
    for index, value in enumerate(_ordered_eigenvalues(matrix)):
        magnitude = abs(value)
        if magnitude > 1.0 + unstable_slack:
            classification = "unstable"
        elif abs(magnitude - 1.0) <= neutral_tolerance:
            classification = "neutral_or_marginal"
        else:
            classification = "stable"
        rows.append(
            {
                "mode_index": index,
                "eigenvalue": _complex_record(value),
                "magnitude": float(magnitude),
                "classification": classification,
            }
        )
    classes = {row["classification"] for row in rows}
    dominant = (
        "unstable"
        if "unstable" in classes
        else (
            "neutral_or_marginal"
            if "neutral_or_marginal" in classes
            else "stable"
        )
    )
    return {
        "modes": rows,
        "dominant_stability_class": dominant,
        "spectral_radius": max((row["magnitude"] for row in rows), default=0.0),
    }


def _slow_subspace(
    matrix: np.ndarray, minimum_magnitude: float
) -> tuple[np.ndarray, list[complex]]:
    values, vectors = np.linalg.eig(matrix)
    indices = [
        index for index, value in enumerate(values) if abs(value) >= minimum_magnitude
    ]
    if not indices:
        return np.zeros((matrix.shape[0], 0), dtype=complex), []
    selected = vectors[:, indices]
    basis, _ = np.linalg.qr(selected)
    return basis[:, : len(indices)], [complex(values[index]) for index in indices]


def principal_subspace_angle(left: np.ndarray, right: np.ndarray) -> float | None:
    if left.shape[1] != right.shape[1] or left.shape[1] == 0:
        return None
    singular_values = np.linalg.svd(left.conj().T @ right, compute_uv=False)
    minimum = float(np.clip(min(singular_values), 0.0, 1.0))
    return float(math.acos(minimum))


def frozen_components(
    model: GRC9V3, hardening_config: dict[str, Any] | None = None
) -> dict[str, Any]:
    chart = BranchCoordinateChart.from_model(model, ("C",))
    state = model.get_state()
    node_index = {node_id: index for index, node_id in enumerate(chart.node_order)}
    incidence = np.zeros((len(chart.node_order), len(chart.edge_order)), dtype=float)
    conductance = np.zeros(len(chart.edge_order), dtype=float)
    for edge_index, edge_id in enumerate(chart.edge_order):
        edge = state.port_edges[edge_id]
        incidence[node_index[edge.node_u], edge_index] = 1.0
        incidence[node_index[edge.node_v], edge_index] = -1.0
        conductance[edge_index] = float(state.base_conductance[edge_id])
    params = chart.params
    evolution = params["evolution"]
    if evolution.get("site_potential_selection") != "quadratic":
        raise ValueError("GRV4 frozen comparator requires the quadratic site potential")
    site = evolution["site_potential_params"]
    kappa = float(evolution["kappa_c"])
    eta = float(evolution["eta"])
    scale = float(site.get("scale", 1.0))
    mu = float(site.get("mu", 0.0))
    dt = float(params["dt"])
    laplacian = incidence @ np.diag(conductance) @ incidence.T
    h_p = kappa * laplacian - 2.0 * scale * np.eye(len(chart.node_order))
    mobility = eta * laplacian
    basis = chart.coherence_basis
    h_p_tangent = basis.T @ h_p @ basis
    mobility_tangent = basis.T @ mobility @ basis
    hardening = hardening_config or {
        "mobility_eigenvalue_floor": 1e-12,
        "structural_classification_tolerance": 1e-10,
    }
    structural = structural_temporal_diagnostics(
        h_p_tangent=h_p_tangent,
        mobility_tangent=mobility_tangent,
        dt=dt,
        eigenvalue_floor=float(hardening["mobility_eigenvalue_floor"]),
        structural_tolerance=float(hardening["structural_classification_tolerance"]),
    )
    coherence = np.asarray(
        [float(state.nodes[node_id].coherence) for node_id in chart.node_order],
        dtype=float,
    )
    gradient = kappa * laplacian @ coherence - (2.0 * scale * coherence + mu)
    return {
        "chart": chart,
        "node_order": list(chart.node_order),
        "edge_order": list(chart.edge_order),
        "coherence": coherence,
        "incidence": incidence,
        "conductance": conductance,
        "laplacian": laplacian,
        "hessian": h_p,
        "h_p": h_p,
        "h_cont": -h_p,
        "mobility": mobility,
        "basis": basis,
        "hessian_tangent": h_p_tangent,
        "h_p_tangent": h_p_tangent,
        "h_cont_tangent": -h_p_tangent,
        "mobility_tangent": mobility_tangent,
        "generator": np.asarray(structural["semidiscrete_generator"], dtype=float),
        "multiplier": np.asarray(structural["explicit_step_multiplier"], dtype=float),
        "structural_temporal_diagnostics": structural,
        "gradient": gradient,
        "branch_velocity": mobility @ gradient,
        "kappa": kappa,
        "eta": eta,
        "scale": scale,
        "mu": mu,
        "dt": dt,
    }


def functional_value(coherence: np.ndarray, components: dict[str, Any]) -> float:
    return float(
        0.5
        * components["kappa"]
        * coherence.T
        @ components["laplacian"]
        @ coherence
        - np.sum(components["scale"] * coherence**2 + components["mu"] * coherence)
    )


def runtime_compatible_frozen_step(
    components: dict[str, Any], coherence: np.ndarray, dt: float
) -> dict[str, Any]:
    chart: BranchCoordinateChart = components["chart"]
    state = deepcopy(chart.base_state)
    for node_id, value in zip(chart.node_order, coherence, strict=True):
        state.nodes[node_id].coherence = float(value)
    params = dict(chart.params)
    params["dt"] = float(dt)
    evolution = params["evolution"]
    compute_potential(state, evolution=evolution)
    compute_flux(state, evolution=evolution)
    potential = np.asarray(
        [float(state.potential[node_id]) for node_id in chart.node_order], dtype=float
    )
    flux = np.asarray(
        [float(state.port_edges[edge_id].flux_uv) for edge_id in chart.edge_order],
        dtype=float,
    )
    staged = GRC9V3.from_state(state, params)
    staged.apply_continuity()
    result_state = staged.get_state()
    result = np.asarray(
        [float(result_state.nodes[node_id].coherence) for node_id in chart.node_order],
        dtype=float,
    )
    return {
        "potential": potential,
        "flux": flux,
        "coherence": result,
        "minimum_input_coherence": float(np.min(coherence)),
        "minimum_output_coherence": float(np.min(result)),
        "positivity_preserved": bool(np.min(coherence) > 0.0 and np.min(result) > 0.0),
        "budget_projection_stage_present": False,
        "positivity_clipping_stage_present": False,
        "boundary_stage_present": False,
        "complete_C_continuity_update_count": 1,
        "final_transport_refresh_present": False,
    }


def runtime_frozen_potential(
    components: dict[str, Any], coherence: np.ndarray
) -> np.ndarray:
    chart: BranchCoordinateChart = components["chart"]
    state = deepcopy(chart.base_state)
    for node_id, value in zip(chart.node_order, coherence, strict=True):
        state.nodes[node_id].coherence = float(value)
    compute_potential(state, evolution=chart.params["evolution"])
    return np.asarray(
        [float(state.potential[node_id]) for node_id in chart.node_order], dtype=float
    )


def sign_audit_rows(
    branch_id: str, components: dict[str, Any], config: dict[str, Any]
) -> tuple[list[dict[str, Any]], dict[str, float], list[dict[str, Any]]]:
    rows = []
    maxima = {
        "runtime_stage_equivalence_linf": 0.0,
        "potential_identity_linf": 0.0,
        "flux_identity_linf": 0.0,
        "functional_formula_error": 0.0,
    }
    base = components["coherence"]
    directions = build_probe_directions(
        components["basis"],
        components["h_cont_tangent"],
        dedup_tolerance=float(config["hardening"]["direction_dedup_tolerance"]),
    )
    hessian = components["hessian"]
    mobility = components["mobility"]
    sign_config = config["sign_audit"]
    for direction_row in directions:
        direction = np.asarray(direction_row["node_direction"], dtype=float)
        for amplitude in sign_config["tangent_amplitudes"]:
            for direction_sign in (-1.0, 1.0):
                coherence = base + direction_sign * float(amplitude) * direction
                gradient = components["kappa"] * components["laplacian"] @ coherence - (
                    2.0 * components["scale"] * coherence + components["mu"]
                )
                velocity = mobility @ gradient
                semidiscrete_rate = float(gradient.T @ mobility @ gradient)
                expected_flux = (
                    -components["eta"]
                    * np.diag(components["conductance"])
                    @ components["incidence"].T
                    @ gradient
                )
                for dt_multiplier in sign_config["runtime_dt_multipliers"]:
                    dt = components["dt"] * float(dt_multiplier)
                    expected = coherence + dt * velocity
                    staged = runtime_compatible_frozen_step(components, coherence, dt)
                    direct_delta = functional_value(expected, components) - functional_value(
                        coherence, components
                    )
                    formula_delta = float(
                        dt * semidiscrete_rate
                        + 0.5 * dt**2 * velocity.T @ hessian @ velocity
                    )
                    stage_error = _linf(expected, staged["coherence"])
                    potential_error = _linf(gradient, staged["potential"])
                    flux_error = _linf(expected_flux, staged["flux"])
                    formula_error = abs(direct_delta - formula_delta)
                    maxima["runtime_stage_equivalence_linf"] = max(
                        maxima["runtime_stage_equivalence_linf"], stage_error
                    )
                    maxima["potential_identity_linf"] = max(
                        maxima["potential_identity_linf"], potential_error
                    )
                    maxima["flux_identity_linf"] = max(
                        maxima["flux_identity_linf"], flux_error
                    )
                    maxima["functional_formula_error"] = max(
                        maxima["functional_formula_error"], formula_error
                    )
                    rows.append(
                        {
                            "branch_id": branch_id,
                            "direction_id": direction_row["direction_id"],
                            "direction_family": direction_row["direction_family"],
                            "direction_source_index": direction_row["source_index"],
                            "direction_sign": int(direction_sign),
                            "amplitude": float(amplitude),
                            "dt_multiplier": float(dt_multiplier),
                            "dt": float(dt),
                            "semidiscrete_dP_dt": semidiscrete_rate,
                            "finite_step_P_delta_formula": formula_delta,
                            "finite_step_P_delta_direct": direct_delta,
                            "runtime_stage_equivalence_linf": stage_error,
                            "potential_identity_linf": potential_error,
                            "flux_identity_linf": flux_error,
                            "functional_formula_error": formula_error,
                            "positivity_preserved": staged["positivity_preserved"],
                            "budget_projection_stage_present": staged[
                                "budget_projection_stage_present"
                            ],
                            "positivity_clipping_stage_present": staged[
                                "positivity_clipping_stage_present"
                            ],
                            "boundary_stage_present": staged["boundary_stage_present"],
                        }
                    )
    return rows, maxima, directions


def compare_temporal_operator(
    frozen: np.ndarray,
    full_audit: dict[str, Any],
    config: dict[str, Any],
    *,
    coordinate_name: str,
) -> dict[str, Any]:
    full = np.asarray(full_audit["jacobian"], dtype=float)
    policy = config["full_map_comparison"]
    temporal = full_audit["temporal_mode_diagnostics"]
    finite_difference_uncertainty = max(
        full_audit["finite_difference_convergence"][
            "adjacent_matrix_relative_errors"
        ],
        default=0.0,
    )
    branch_residual_over_h = max(
        (row["branch_residual_over_h"] for row in full_audit["column_audits"]),
        default=0.0,
    )
    matrix_residual = max(
        float(temporal.get("maximum_left_residual_l2", 0.0)),
        float(temporal.get("maximum_right_residual_l2", 0.0)),
    )
    eigenvector_condition = float(temporal.get("eigenvector_condition_number", 1.0))
    condition_uncertainty = eigenvector_condition * np.finfo(float).eps
    cluster_uncertainty = float(
        temporal["spectral_thresholds"]["eigenvalue_cluster_membership_tolerance"]
    )
    uncertainty = max(
        float(policy["unit_circle_uncertainty_floor"]),
        finite_difference_uncertainty,
        branch_residual_over_h,
        matrix_residual,
        condition_uncertainty,
        cluster_uncertainty,
    )
    frozen_class = robust_multiplier_rows(frozen, uncertainty=uncertainty)
    full_class = robust_multiplier_rows(full, uncertainty=uncertainty)
    threshold = float(policy["slow_subspace_minimum_multiplier_magnitude"])
    frozen_basis, frozen_clusters = real_invariant_basis(
        frozen,
        minimum_magnitude=threshold,
        complex_tolerance=float(policy["complex_pair_tolerance"]),
    )
    block_scales = temporal["block_metric"]["branch_characteristic_scales"]
    subspace = metric_subspace_comparison(
        frozen_mode_basis=frozen_basis,
        full_matrix=full,
        c_dimension=frozen.shape[0],
        block_scales=block_scales,
        slow_minimum_magnitude=threshold,
        complex_tolerance=float(policy["complex_pair_tolerance"]),
        uncertainty=uncertainty,
        deadbeat_tolerance=float(policy["deadbeat_multiplier_tolerance"]),
    )
    frozen_values = [value for value in np.linalg.eigvals(frozen) if abs(value) >= threshold]
    full_values = [value for value in np.linalg.eigvals(full) if abs(value) >= threshold]
    value_error = eigenvalue_set_error(
        np.diag(np.asarray(frozen_values, dtype=complex)),
        np.diag(np.asarray(full_values, dtype=complex)),
    )
    stability_agrees = (
        frozen_class["aggregate_classification"]
        == full_class["aggregate_classification"]
    )
    angle = subspace["metric_principal_angle_radians"]
    dimension_agrees = (
        subspace["frozen_embedded_subspace_dimension"]
        == subspace["full_metric_slow_subspace_dimension"]
    )
    subspace_agrees = bool(
        dimension_agrees
        and angle is not None
        and angle <= float(policy["principal_subspace_angle_max_radians"])
    )
    eigenvalues_agree = bool(
        value_error is not None
        and value_error <= float(policy["eigenvalue_set_error_max"])
    )
    return {
        "coordinate_name": coordinate_name,
        "uncertainty_budget": {
            "finite_difference_uncertainty": finite_difference_uncertainty,
            "branch_residual_over_h": branch_residual_over_h,
            "matrix_reconstruction_residual": matrix_residual,
            "eigenvector_condition_estimate": eigenvector_condition,
            "eigenvector_condition_uncertainty": condition_uncertainty,
            "cluster_uncertainty": cluster_uncertainty,
            "combined_unit_circle_uncertainty": uncertainty,
        },
        "frozen_multiplier_classification": frozen_class,
        "full_multiplier_classification": full_class,
        "frozen_real_invariant_clusters": frozen_clusters,
        "frozen_slow_multiplier_values": [_complex_record(v) for v in frozen_values],
        "full_slow_multiplier_values": [_complex_record(v) for v in full_values],
        "slow_subspace_dimension_frozen": frozen_basis.shape[1],
        "slow_subspace_dimension_full": subspace[
            "full_metric_slow_subspace_dimension"
        ],
        "slow_multiplier_set_error": value_error,
        "principal_subspace_angle_radians": angle,
        "metric_and_embedding_audit": subspace,
        "stability_classification_agrees": stability_agrees,
        "slow_multiplier_values_agree": eigenvalues_agree,
        "slow_subspace_agrees": subspace_agrees,
        "verified_stability_or_slow_subspace_disagreement": bool(
            (
                not stability_agrees
                and "marginal_within_uncertainty"
                not in {
                    frozen_class["aggregate_classification"],
                    full_class["aggregate_classification"],
                }
            )
            or (dimension_agrees and angle is not None and not subspace_agrees)
        ),
        "deadbeat_or_overwrite_modes_excluded": True,
        "cluster_and_real_invariant_plane_policy_applied": True,
        "bounded_relation": (
            "agreement"
            if stability_agrees and eigenvalues_agree and subspace_agrees
            else "bounded_difference"
        ),
    }


def frozen_branch_and_source_audit(
    model: GRC9V3, components: dict[str, Any], config: dict[str, Any]
) -> dict[str, Any]:
    state = model.get_state()
    hardening = config["hardening"]
    staged = runtime_compatible_frozen_step(
        components, components["coherence"], components["dt"]
    )
    residual = staged["coherence"] - components["coherence"]
    base_w = [
        float(state.base_conductance[edge_id]) for edge_id in components["edge_order"]
    ]
    duplicate_w = [
        float(state.port_edges[edge_id].conductance)
        for edge_id in components["edge_order"]
    ]
    connectivity = graph_connectivity(
        components["incidence"],
        components["conductance"],
        conductance_floor=float(hardening["conductance_connectivity_floor"]),
    )
    laplacian_tangent = (
        components["basis"].T @ components["laplacian"] @ components["basis"]
    )
    minimum_w = min(base_w, default=0.0)
    w_floor = float(hardening["conductance_connectivity_floor"])
    return {
        "frozen_W_definition": {
            "comparator": "F_clamp_C_Wstar",
            "clamp_scope": "accepted_branch_W_held_fixed_in_structural_laplacian_and_transport_mobility_for_whole_comparator_beat",
            "conductance_update_law": "omitted",
            "W_dependence_on_perturbed_C": "omitted",
            "W_dependence_on_perturbed_J": "omitted",
            "C_continuity_update_count": 1,
            "final_derived_transport_refresh": "not_present_and_not_a_second_C_update",
            "runtime_step_monkey_patched": False,
        },
        "reduction_classification": "clamped_counterfactual_only",
        "reduction_not_claimed": [
            "algebraic_W_elimination",
            "fast_slaving_W_elimination",
            "full_joint_C_W_dynamics",
        ],
        "authoritative_W": {
            "source": "GRC9V3State.base_conductance_from_accepted_GRV2_snapshot",
            "taken_at": "accepted_branch_before_any_GRV4_perturbation",
            "branch_W_semantic_sha256": semantic_digest(base_w),
            "duplicate_surface": "port_edges[*].conductance",
            "duplicate_surface_consistency_linf": _linf(base_w, duplicate_w),
            "duplicate_surface_consistent": bool(
                _linf(base_w, duplicate_w)
                <= float(hardening["duplicate_W_consistency_linf_max"])
            ),
        },
        "frozen_fixed_point": {
            "map_residual_linf": float(np.linalg.norm(residual, ord=np.inf)),
            "maximum_allowed": float(
                config["frozen_comparator"]["branch_residual_linf_max"]
            ),
            "passed": bool(
                np.linalg.norm(residual, ord=np.inf)
                <= float(config["frozen_comparator"]["branch_residual_linf_max"])
            ),
            "failure_effect": "blocks_frozen_temporal_stability_but_preserves_structural_second_variation",
        },
        "mobility_and_connectivity": {
            **connectivity,
            "minimum_W": minimum_w,
            "maximum_W": max(base_w, default=0.0),
            "conductance_connectivity_floor": w_floor,
            "distance_from_conductance_floor": minimum_w - w_floor,
            "reduced_L_W_condition_number": positive_condition_number(
                laplacian_tangent,
                eigenvalue_floor=float(hardening["mobility_eigenvalue_floor"]),
            ),
            "A_W_condition_number": positive_condition_number(
                components["mobility_tangent"],
                eigenvalue_floor=float(hardening["mobility_eigenvalue_floor"]),
            ),
            "additional_mobility_null_directions": components[
                "structural_temporal_diagnostics"
            ]["additional_mobility_nullity"],
        },
        "runtime_shadow_envelope": {
            "runtime_dt_only": True,
            "full_recurrence_dt_sweep_performed": False,
            "full_recurrence_dt_sweep_not_numerical_convergence_claim": True,
            "positivity_preserved": staged["positivity_preserved"],
            "budget_projection_stage_present": staged[
                "budget_projection_stage_present"
            ],
            "positivity_clipping_stage_present": staged[
                "positivity_clipping_stage_present"
            ],
            "boundary_stage_present": staged["boundary_stage_present"],
        },
    }


def potential_and_site_audit(
    components: dict[str, Any],
    directions: list[dict[str, Any]],
    config: dict[str, Any],
) -> dict[str, Any]:
    step = float(config["hardening"]["potential_finite_difference_step"])
    audit = finite_difference_potential_audit(
        coherence=components["coherence"],
        basis=components["basis"],
        analytic_h_p_tangent=components["h_p_tangent"],
        potential=lambda coherence: runtime_frozen_potential(components, coherence),
        functional=lambda coherence: functional_value(coherence, components),
        directions=directions,
        step=step,
    )
    site_second_derivative = 2.0 * components["scale"]
    site_fd = []
    for value in components["coherence"]:
        derivative_plus = 2.0 * components["scale"] * (value + step) + components["mu"]
        derivative_minus = 2.0 * components["scale"] * (value - step) + components["mu"]
        site_fd.append((derivative_plus - derivative_minus) / (2.0 * step))
    audit["site_potential"] = {
        "backend": "quadratic",
        "V_prime_formula": "2*scale*C+mu",
        "V_second_formula": "2*scale",
        "analytic_V_second": [
            site_second_derivative for _ in components["coherence"]
        ],
        "finite_difference_V_second": [float(value) for value in site_fd],
        "maximum_V_second_error": max(
            (abs(value - site_second_derivative) for value in site_fd), default=0.0
        ),
        "twice_differentiable_in_probe_region": True,
    }
    audit["potential_gauge"] = {
        "additive_potential_constant_is_transport_null": True,
        "separate_potential_gauge_mode_introduced": False,
        "continuation_spectrum_space": "conserved_C_tangent_only",
    }
    return audit


def grv3_uncertainty_upper_bound(audit: dict[str, Any], config: dict[str, Any]) -> float:
    temporal = audit["temporal_mode_diagnostics"]
    return max(
        float(config["full_map_comparison"]["unit_circle_uncertainty_floor"]),
        max(
            audit["finite_difference_convergence"][
                "adjacent_matrix_relative_errors"
            ],
            default=0.0,
        ),
        max(
            (row["branch_residual_over_h"] for row in audit["column_audits"]),
            default=0.0,
        ),
        float(temporal.get("maximum_left_residual_l2", 0.0)),
        float(temporal.get("maximum_right_residual_l2", 0.0)),
        float(
            temporal["spectral_thresholds"][
                "eigenvalue_cluster_membership_tolerance"
            ]
        ),
    )


def validate_prerequisite() -> tuple[dict[str, Any], dict[str, Any]]:
    receipt = read_json(EXPERIMENT_ROOT / "outputs/gates/grv3_result_receipt.json")
    anchor = read_json(EXPERIMENT_ROOT / "outputs/gates/grv3_acceptance_anchor.json")
    validate_receipt(receipt)
    validate_acceptance_anchor(anchor)
    if receipt["receipt_payload_sha256"] != GRV3_RECEIPT_SHA256:
        raise ValueError("GRV3 receipt identity mismatch")
    if (
        anchor["result_revision"] != GRV3_RESULT_REVISION
        or anchor["receipt_payload_sha256"] != GRV3_RECEIPT_SHA256
    ):
        raise ValueError("GRV3 acceptance anchor does not bind the required result")
    if not prerequisite_is_authorized(anchor):
        raise ValueError("GRV3 prerequisite is not accepted")
    return receipt, anchor


def protected_manifest_v4() -> dict[str, Any]:
    predecessor_path = EXPERIMENT_ROOT / "outputs/protected_path_manifest_v3.json"
    predecessor = read_json(predecessor_path)
    relative_paths = [row["path"] for row in predecessor["payload"]["files"]]
    current = file_manifest(relative_paths)
    payload = {
        "manifest_id": "b1_grv4_protected_paths_v4",
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
        schema_version="b1_grv4_protected_path_manifest_v4",
        generating_command=COMMAND,
    )


def _symmetry_audit(
    branch_rows: list[dict[str, Any]],
    grv3_symmetry: dict[str, Any],
    tolerance: float,
    *,
    near_zero_threshold: float,
    near_zero_absolute_max: float,
) -> dict[str, Any]:
    by_id = {row["branch_id"]: row for row in branch_rows}
    pair_rows = []
    for source_pair in grv3_symmetry["pair_rows"]:
        if source_pair["coordinate_candidate"] != "C":
            continue
        source = by_id[source_pair["source_branch_id"]]
        target = by_id[source_pair["target_branch_id"]]
        transport = np.asarray(source_pair["coordinate_transport"], dtype=float)
        errors = {
            "H_cont": conjugacy_errors(
                np.asarray(source["H_cont_tangent"], dtype=float),
                np.asarray(target["H_cont_tangent"], dtype=float),
                transport,
            ),
            "mobility": conjugacy_errors(
                np.asarray(source["fixed_W_mobility"], dtype=float),
                np.asarray(target["fixed_W_mobility"], dtype=float),
                transport,
            ),
            "frozen_multiplier": conjugacy_errors(
                np.asarray(source["frozen_explicit_multiplier"], dtype=float),
                np.asarray(target["frozen_explicit_multiplier"], dtype=float),
                transport,
            ),
        }
        source_primary = source["primary_C_full_recurrence_comparison"]
        target_primary = target["primary_C_full_recurrence_comparison"]
        if source_primary["status"] == "compared" and target_primary["status"] == "compared":
            errors["full_C"] = conjugacy_errors(
                np.asarray(source_primary["full_transition_matrix"], dtype=float),
                np.asarray(target_primary["full_transition_matrix"], dtype=float),
                transport,
            )
        else:
            errors["full_C"] = None
        component_pass = {}
        for component, error in errors.items():
            if error is None:
                component_pass[component] = True
                continue
            near_zero = max(
                error["source_norm_linf"], error["target_norm_linf"]
            ) <= near_zero_threshold
            component_pass[component] = bool(
                error["relative"] <= tolerance
                or (
                    near_zero
                    and error["absolute_linf"] <= near_zero_absolute_max
                )
            )
            error["near_zero_absolute_policy_applied"] = near_zero
            error["relative_maximum_allowed"] = tolerance
            error["absolute_linf_maximum_allowed_when_near_zero"] = (
                near_zero_absolute_max
            )
        passed = all(component_pass.values())
        pair_rows.append(
            {
                "symmetry_orbit_id": source_pair["orbit_id"],
                "source_branch_id": source_pair["source_branch_id"],
                "target_branch_id": source_pair["target_branch_id"],
                "coordinate_transport": source_pair["coordinate_transport"],
                "matrix_conjugacy_errors": errors,
                "component_pass": component_pass,
                "maximum_allowed": tolerance,
                "passed": passed,
            }
        )
    orbit_ids = {row["symmetry_orbit_id"] for row in branch_rows}
    multirow_orbits = {row["symmetry_orbit_id"] for row in pair_rows}
    return {
        "mapping_rule": grv3_symmetry["mapping_rule"],
        "audit_kind": "matrix_level_conjugacy_not_spectrum_only",
        "pair_rows": pair_rows,
        "orbit_count": len(orbit_ids),
        "multirow_orbit_count": len(multirow_orbits),
        "singleton_orbit_count": len(orbit_ids - multirow_orbits),
        "failed_pair_count": sum(not row["passed"] for row in pair_rows),
        "failed_orbit_count": len(
            {row["symmetry_orbit_id"] for row in pair_rows if not row["passed"]}
        ),
    }


def write_report(payload: dict[str, Any]):
    summary = payload["summary"]
    report = EXPERIMENT_ROOT / "reports/b1_grv4_frozen_conductance_full_recurrence.md"
    lines = [
        "# B1-GR GRV4 Frozen-Conductance Versus Full Recurrence",
        "",
        "## Result",
        "",
        "```text",
        "gate = GRV4",
        f"mechanical_status = {summary['mechanical_status']}",
        "scientific_acceptance = awaiting_human_review",
        f"branches_audited = {summary['branch_count']}",
        f"standalone_frozen_comparators = {summary['standalone_frozen_comparator_count']}",
        f"primary_full_map_comparisons = {summary['primary_full_comparison_count']}",
        f"full_map_comparisons_blocked_by_GRV3 = {summary['full_comparison_blocked_count']}",
        f"primary_agreement_count = {summary['primary_agreement_count']}",
        f"primary_bounded_difference_count = {summary['primary_bounded_difference_count']}",
        f"verified_strong_disagreement_count = {summary['verified_strong_disagreement_count']}",
        f"runtime_sign_classification = {summary['runtime_sign_classification']}",
        f"GRV_C4_candidate = {str(summary['grv_c4_candidate']).lower()}",
        "continuation = unsupported",
        "retention = unsupported",
        "readback = unsupported",
        "writeback = unsupported",
        "runtime_change_authorized = false",
        "```",
        "",
        "GRV4 constructs an experiment-local fixed-conductance comparator. It does",
        "not alter `GRC9V3.step()` and does not treat the comparator as native runtime",
        "state. The runtime sign follows directly from the implemented equations:",
        "`Phi = gradient(P_G)`, `J = -eta W grad(Phi)`, and continuity therefore",
        "gives `dC/dt = eta L_W gradient(P_G)`. Thus `P_G` is weakly",
        "nondecreasing in the semidiscrete fixed-`W` reduction and `-P_G` is weakly",
        "nonincreasing. Stationary rows count as equality, not strict increase.",
        "",
        "## Discrete And Runtime-Stage Audit",
        "",
        f"The preregistered amplitude/timestep matrix contains {summary['sign_audit_row_count']} rows.",
        f"The maximum staged-runtime versus explicit-map error is `{summary['maximum_runtime_stage_equivalence_linf']:.6g}`.",
        f"The minimum finite-step functional delta is `{summary['minimum_finite_step_P_delta']:.6g}`.",
        "The audit calls the existing potential, flux, and continuity stages while",
        "holding the accepted branch conductance fixed; it excludes conductance",
        "reconstruction and every semantic/topology stage by declaration.",
        "",
        "## Frozen/Full Boundary",
        "",
        "All 48 accepted branches receive a frozen structural comparator. Only the",
        "32 branches with a GRV3-admitted `C` transition matrix receive the primary",
        "full-recurrence comparison. The 16 exact-zero-current boundary branches are",
        "retained as blocked comparisons rather than silently removed. `C-W` is a",
        "secondary diagnostic of evolving-conductance recurrence and never supports",
        "a joint mode or conductance-eliminability claim.",
        "",
        "## Interpretation",
        "",
        (
            "At least one verified branch changes stability class or slow-subspace identity between the two operators."
            if summary["verified_strong_disagreement_count"]
            else "No verified branch changes stability class or slow-subspace identity within the admitted comparison envelope."
        ),
        "Agreement is a bounded result, not proof that frozen conductance is the full",
        "core continuation operator. GRV4 opens no continuation, retention, read-back,",
        "or write-back claim and does not establish global `W` eliminability.",
        "",
        "## Provenance",
        "",
        f"- Input execution revision: `{payload['source_contract']['input_execution_revision']}`",
        f"- GRV3 result revision: `{GRV3_RESULT_REVISION}`",
        f"- GRV3 receipt: `{GRV3_RECEIPT_SHA256}`",
        f"- GRV3 acceptance anchor commit: `{GRV3_ACCEPTANCE_COMMIT}`",
        "- Runtime source/spec/test paths: unchanged under `protected_path_manifest_v4.json`",
    ]
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report


def run_grv4() -> None:
    if git("status", "--porcelain"):
        raise SystemExit("GRV4 requires a clean committed P4 input revision")
    receipt3, anchor3 = validate_prerequisite()
    config = read_json(EXPERIMENT_ROOT / "configs/grv4_frozen_full_comparison.json")
    scope = config["branch_scope"]
    registry_path = EXPERIMENT_ROOT / scope["source_registry_path"]
    grv3_path = EXPERIMENT_ROOT / scope["grv3_result_path"]
    if sha256_file(registry_path) != scope["source_registry_sha256"]:
        raise ValueError("GRV2 fixed-branch registry file digest mismatch")
    if sha256_file(grv3_path) != scope["grv3_result_sha256"]:
        raise ValueError("GRV3 result file digest mismatch")
    registry = read_json(registry_path)["payload"]
    grv3 = read_json(grv3_path)["payload"]
    branches = [row for row in registry["branches"] if row["branch_certified"]]
    if len(branches) != int(scope["expected_branch_count"]):
        raise ValueError("GRV4 branch scope is not the frozen 48-row registry")
    grv3_by_id = {row["branch_id"]: row for row in grv3["branches"]}
    input_revision = git("rev-parse", "HEAD")
    input_tree = file_manifest(tracked_files([EXPERIMENT_RELATIVE]))
    branch_rows = []
    all_sign_rows = []
    global_maxima = {
        "runtime_stage_equivalence_linf": 0.0,
        "potential_identity_linf": 0.0,
        "flux_identity_linf": 0.0,
        "functional_formula_error": 0.0,
        "h_p_finite_difference_relative_error": 0.0,
        "h_p_finite_difference_absolute_linf_error": 0.0,
        "directional_functional_error": 0.0,
        "site_V_second_error": 0.0,
    }
    policy = config["full_map_comparison"]
    for branch in branches:
        snapshot_path = REPO_ROOT / branch["state_snapshot_path"]
        if sha256_file(snapshot_path) != branch["state_snapshot_sha256"]:
            raise ValueError(f"branch snapshot digest mismatch: {branch['branch_id']}")
        model = GRC9V3.load(str(snapshot_path))
        components = frozen_components(model, config["hardening"])
        sign_rows, maxima, directions = sign_audit_rows(
            branch["branch_id"], components, config
        )
        source_audit = frozen_branch_and_source_audit(model, components, config)
        potential_audit = potential_and_site_audit(components, directions, config)
        maxima["h_p_finite_difference_relative_error"] = potential_audit[
            "h_p_relative_error"
        ]
        maxima["h_p_finite_difference_absolute_linf_error"] = potential_audit[
            "h_p_absolute_linf_error"
        ]
        maxima["directional_functional_error"] = potential_audit[
            "maximum_directional_functional_error"
        ]
        maxima["site_V_second_error"] = potential_audit["site_potential"][
            "maximum_V_second_error"
        ]
        all_sign_rows.extend(sign_rows)
        for key in global_maxima:
            global_maxima[key] = max(global_maxima[key], maxima[key])
        grv3_row = grv3_by_id[branch["branch_id"]]
        full_audits = grv3_row["coordinate_stratum_and_jacobian_audits"]
        primary_audit = full_audits["C"]
        primary_temporal_allowed = "C" in grv3_row[
            "convergence_and_nonnormal_admitted_temporal_coordinates"
        ]
        if (
            primary_audit["square_transition_jacobian_status"] == "admitted"
            and primary_temporal_allowed
        ):
            primary = {
                "status": "compared",
                "branch_admission_status": "causal_branch_accepted_and_square_transition_accepted",
                "GRV3_temporal_interpretation_allowed": True,
                "full_transition_matrix": primary_audit["jacobian"],
                **compare_temporal_operator(
                    components["multiplier"],
                    primary_audit,
                    config,
                    coordinate_name="C",
                ),
            }
        else:
            primary = {
                "status": "blocked_by_GRV3_C_coordinate_admission",
                "branch_admission_status": (
                    "classical_jacobian_blocked"
                    if primary_audit["square_transition_jacobian_status"] != "admitted"
                    else "square_transition_accepted_temporal_interpretation_blocked"
                ),
                "blocked_reason": primary_audit["square_transition_jacobian_status"],
                "GRV3_temporal_interpretation_allowed": False,
                "verified_stability_or_slow_subspace_disagreement": False,
            }
        secondary_audit = full_audits["C_W"]
        secondary_temporal_allowed = "C_W" in grv3_row[
            "convergence_and_nonnormal_admitted_temporal_coordinates"
        ]
        if (
            secondary_audit["square_transition_jacobian_status"] == "admitted"
            and secondary_temporal_allowed
        ):
            secondary = {
                "status": "compared_as_diagnostic_evolving_conductance_coordinate",
                "GRV3_temporal_interpretation_allowed": True,
                "full_transition_matrix": secondary_audit["jacobian"],
                **compare_temporal_operator(
                    components["multiplier"],
                    secondary_audit,
                    config,
                    coordinate_name="C_W",
                ),
                "joint_C_W_mode_claim_allowed": False,
            }
        elif secondary_audit["square_transition_jacobian_status"] == "admitted":
            secondary = {
                "status": "diagnostic_matrix_only_GRV3_temporal_interpretation_blocked",
                "GRV3_temporal_interpretation_allowed": False,
                "blocked_reason": secondary_audit["slow_cluster_status"],
                "verified_stability_or_slow_subspace_disagreement": False,
                "joint_C_W_mode_claim_allowed": False,
            }
        else:
            secondary = {
                "status": "blocked_by_GRV3_C_W_coordinate_admission",
                "GRV3_temporal_interpretation_allowed": False,
                "blocked_reason": secondary_audit["square_transition_jacobian_status"],
                "verified_stability_or_slow_subspace_disagreement": False,
                "joint_C_W_mode_claim_allowed": False,
            }
        structural_values = np.linalg.eigvalsh(components["h_cont_tangent"])
        branch_rows.append(
            {
                "branch_id": branch["branch_id"],
                "fixture_id": branch["fixture_id"],
                "symmetry_orbit_id": branch["symmetry_orbit_id"],
                "source_snapshot_path": branch["state_snapshot_path"],
                "source_snapshot_sha256": branch["state_snapshot_sha256"],
                "node_order": components["node_order"],
                "edge_order": components["edge_order"],
                "basis_id": config["frozen_comparator"]["basis_id"],
                "coherence_basis": components["basis"].tolist(),
                "fixed_conductance": components["conductance"].tolist(),
                "graph_laplacian": components["laplacian"].tolist(),
                "H_P_tangent": components["h_p_tangent"].tolist(),
                "H_cont_tangent": components["h_cont_tangent"].tolist(),
                "constrained_second_variation": components["h_cont_tangent"].tolist(),
                "fixed_W_mobility": components["mobility_tangent"].tolist(),
                "semidiscrete_generator": components["generator"].tolist(),
                "frozen_explicit_multiplier": components["multiplier"].tolist(),
                "frozen_restoring_structural_eigenvalues": [
                    float(value) for value in structural_values
                ],
                "frozen_semidiscrete_rates": [
                    _complex_record(value)
                    for value in _ordered_eigenvalues(components["generator"])
                ],
                "frozen_branch_velocity_linf": float(
                    np.linalg.norm(components["branch_velocity"], ord=np.inf)
                ),
                "frozen_branch_map_residual": source_audit["frozen_fixed_point"],
                "frozen_branch_residual_passed": source_audit["frozen_fixed_point"][
                    "passed"
                ],
                "authoritative_W_and_reduction_audit": source_audit,
                "potential_functional_and_site_audit": potential_audit,
                "structural_temporal_separation": components[
                    "structural_temporal_diagnostics"
                ],
                "probe_direction_registry": directions,
                "sign_audit_row_count": len(sign_rows),
                "sign_audit_maxima": maxima,
                "primary_C_full_recurrence_comparison": primary,
                "secondary_C_W_full_recurrence_comparison": secondary,
                "reduction_and_elimination_assumptions": {
                    "fixed_topology": "satisfied_on_GRV2_branch",
                    "fixed_W": "experiment_local_whole_beat_counterfactual_clamp",
                    "quadratic_site_potential": "satisfied",
                    "conserved_zero_sum_C_tangent": "same_basis_as_GRV3",
                    "identity_spark_choice_growth_boundary_budget_stages": "excluded_from_frozen_comparator",
                    "full_runtime_recurrence_source": "unchanged_GRV3_complete_step_matrix",
                    "W_elimination": "not_verified_and_not_claimed",
                    "fast_slaving": "not_verified_and_not_claimed",
                    "joint_C_W_mode": "not_claimed"
                },
                "frozen_operator_class": "substrate_reduced",
                "frozen_comparator_reduction_classification": "clamped_counterfactual_only",
                "first_order_local_gate_only": True,
                "J_squared_nonlinear_conductance_effects_remain_open": True,
                "full_core_continuation_operator_claim_allowed": False,
            }
        )
    symmetry = _symmetry_audit(
        branch_rows,
        grv3["symmetry_covariance_audit"],
        float(policy["symmetry_matrix_conjugacy_error_max"]),
        near_zero_threshold=float(config["hardening"]["h_p_near_zero_norm_threshold"]),
        near_zero_absolute_max=float(
            config["hardening"]["h_p_finite_difference_absolute_linf_error_max"]
        ),
    )
    sign_tolerance = float(config["sign_audit"]["functional_delta_tolerance"])
    minimum_delta = min(
        (row["finite_step_P_delta_formula"] for row in all_sign_rows), default=0.0
    )
    positive_delta_count = sum(
        row["finite_step_P_delta_formula"] > sign_tolerance for row in all_sign_rows
    )
    negative_delta_count = sum(
        row["finite_step_P_delta_formula"] < -sign_tolerance for row in all_sign_rows
    )
    if negative_delta_count == 0:
        sign_classification = "P_G_increases_and_negative_P_G_decreases_weakly_over_tested_discrete_sweep"
    else:
        runtime_rows = [row for row in all_sign_rows if row["dt_multiplier"] == 1.0]
        sign_classification = (
            "neither_is_monotone_at_runtime_timestep"
            if any(
                row["finite_step_P_delta_formula"] < -sign_tolerance
                for row in runtime_rows
            )
            else "monotonicity_holds_only_in_small_step_limit"
        )
    primary_rows = [
        row["primary_C_full_recurrence_comparison"]
        for row in branch_rows
        if row["primary_C_full_recurrence_comparison"]["status"] == "compared"
    ]
    disagreements = sum(
        row["verified_stability_or_slow_subspace_disagreement"] for row in primary_rows
    )
    agreements = sum(row["bounded_relation"] == "agreement" for row in primary_rows)
    source_stage_pass = bool(
        global_maxima["runtime_stage_equivalence_linf"]
        <= float(config["sign_audit"]["runtime_stage_equivalence_linf_max"])
        and global_maxima["functional_formula_error"]
        <= float(config["sign_audit"]["functional_formula_consistency_max"])
    )
    hardening = config["hardening"]
    hessian_fd_pass = all(
        (
            row["potential_functional_and_site_audit"]["h_p_relative_error"]
            <= float(hardening["h_p_finite_difference_relative_error_max"])
        )
        or (
            np.linalg.norm(np.asarray(row["H_P_tangent"], dtype=float), ord=np.inf)
            <= float(hardening["h_p_near_zero_norm_threshold"])
            and row["potential_functional_and_site_audit"][
                "h_p_absolute_linf_error"
            ]
            <= float(hardening["h_p_finite_difference_absolute_linf_error_max"])
        )
        for row in branch_rows
    )
    derivative_audit_pass = bool(
        hessian_fd_pass
        and global_maxima["directional_functional_error"]
        <= float(hardening["directional_functional_error_max"])
        and global_maxima["site_V_second_error"]
        <= float(hardening["site_V_second_error_max"])
    )
    clamp_and_mobility_pass = all(
        row["frozen_comparator_reduction_classification"]
        == "clamped_counterfactual_only"
        and row["authoritative_W_and_reduction_audit"]["authoritative_W"][
            "duplicate_surface_consistent"
        ]
        and row["authoritative_W_and_reduction_audit"]["mobility_and_connectivity"][
            "connected"
        ]
        and row["structural_temporal_separation"]["mobility_positive_definite"]
        for row in branch_rows
    )
    projection_noop_pass = all(
        row["positivity_preserved"]
        and not row["budget_projection_stage_present"]
        and not row["positivity_clipping_stage_present"]
        and not row["boundary_stage_present"]
        for row in all_sign_rows
    )
    primary_count = len(primary_rows)
    blocked_count = len(branch_rows) - primary_count
    mechanical_pass = bool(
        source_stage_pass
        and derivative_audit_pass
        and clamp_and_mobility_pass
        and projection_noop_pass
        and negative_delta_count == 0
        and all(row["frozen_branch_residual_passed"] for row in branch_rows)
        and primary_count == int(scope["expected_primary_full_comparison_count"])
        and symmetry["failed_orbit_count"] == 0
    )
    summary = {
        "mechanical_status": "passed" if mechanical_pass else "failed",
        "branch_count": len(branch_rows),
        "standalone_frozen_comparator_count": len(branch_rows),
        "primary_full_comparison_count": primary_count,
        "full_comparison_blocked_count": blocked_count,
        "primary_agreement_count": agreements,
        "primary_bounded_difference_count": primary_count - agreements,
        "verified_strong_disagreement_count": disagreements,
        "strong_result_supported": disagreements > 0,
        "runtime_sign_classification": sign_classification,
        "sign_audit_row_count": len(all_sign_rows),
        "positive_functional_delta_row_count": positive_delta_count,
        "stationary_within_tolerance_row_count": len(all_sign_rows)
        - positive_delta_count
        - negative_delta_count,
        "negative_functional_delta_row_count": negative_delta_count,
        "minimum_finite_step_P_delta": minimum_delta,
        "maximum_runtime_stage_equivalence_linf": global_maxima[
            "runtime_stage_equivalence_linf"
        ],
        "maximum_potential_identity_linf": global_maxima["potential_identity_linf"],
        "maximum_flux_identity_linf": global_maxima["flux_identity_linf"],
        "maximum_functional_formula_error": global_maxima["functional_formula_error"],
        "maximum_H_P_finite_difference_relative_error": global_maxima[
            "h_p_finite_difference_relative_error"
        ],
        "maximum_H_P_finite_difference_absolute_linf_error": global_maxima[
            "h_p_finite_difference_absolute_linf_error"
        ],
        "maximum_directional_functional_error": global_maxima[
            "directional_functional_error"
        ],
        "maximum_site_V_second_error": global_maxima["site_V_second_error"],
        "derivative_audit_passed": derivative_audit_pass,
        "clamp_and_mobility_audit_passed": clamp_and_mobility_pass,
        "projection_clipping_boundary_noop_audit_passed": projection_noop_pass,
        "symmetry_orbit_count": symmetry["orbit_count"],
        "symmetry_failed_orbit_count": symmetry["failed_orbit_count"],
        "grv_c4_candidate": mechanical_pass,
        "continuation_supported": False,
        "retention_supported": False,
        "readback_supported": False,
        "writeback_supported": False,
        "grv4_result_scope": "first_order_local_clamped_W_counterfactual_relation_only",
        "nonlinear_J_squared_conductance_effects_resolved": False,
    }
    if not mechanical_pass:
        raise ValueError(f"GRV4 mechanical gates failed: {summary}")
    payload = {
        "gate_id": "GRV4",
        "source_contract": {
            "input_execution_revision": input_revision,
            "GRV3_result_revision": GRV3_RESULT_REVISION,
            "GRV3_receipt_payload_sha256": GRV3_RECEIPT_SHA256,
            "GRV3_acceptance_anchor_commit": GRV3_ACCEPTANCE_COMMIT,
            "branch_registry_path": scope["source_registry_path"],
            "GRV3_result_path": scope["grv3_result_path"],
        },
        "sign_contract": config["sign_audit"],
        "frozen_comparator_contract": config["frozen_comparator"],
        "full_map_comparison_contract": config["full_map_comparison"],
        "branch_rows": branch_rows,
        "sign_audit_rows": all_sign_rows,
        "symmetry_covariance_audit": symmetry,
        "summary": summary,
        "claim_boundary": {
            **config["claim_boundary"],
            "GRV_C4_candidate_pending_human_review": mechanical_pass,
            "full_core_continuation_operator_supported": False,
        },
    }
    output_root = EXPERIMENT_ROOT / "outputs"
    result_path = output_root / "frozen_full_comparison.json"
    write_json(
        result_path,
        artifact_envelope(
            payload,
            schema_version="b1_grv4_frozen_full_comparison_v1",
            generating_command=COMMAND,
            reproducibility_class="tolerance_reproducible",
        ),
    )
    protected_path = output_root / "protected_path_manifest_v4.json"
    protected = protected_manifest_v4()
    if not protected["payload"]["unchanged_successor"]:
        raise ValueError("protected source/spec/test paths changed since GRV3")
    write_json(protected_path, protected)
    report_path = write_report(payload)
    artifacts = [result_path, protected_path, report_path]
    baseline = read_json(output_root / "baseline_manifest.json")["payload"]
    receipt = finalize_receipt(
        {
            "gate_id": "GRV4",
            "input_execution_revision": input_revision,
            "substrate_base_revision": baseline["substrate_base_revision"],
            "input_experiment_tree_sha256": input_tree["tree_sha256"],
            "prerequisite_result_receipt_digests": [GRV3_RECEIPT_SHA256],
            "prerequisite_acceptance_anchors": [
                {
                    "gate_id": "GRV3",
                    "immutable_ref": f"git:{GRV3_ACCEPTANCE_COMMIT}",
                    "anchor_payload_sha256": semantic_digest(anchor3),
                }
            ],
            "output_artifact_digests": {
                path.relative_to(EXPERIMENT_ROOT).as_posix(): sha256_file(path)
                for path in sorted(artifacts)
            },
            "status": "awaiting_scientific_review",
            "blocked_gates": [f"GRV{index}" for index in range(5, 9)],
            "claim_ceiling": "substrate_reduced_frozen_W_comparator_and_bounded_full_recurrence_relation_pending_human_review",
            "prerequisite_receipt_status": receipt3["status"],
            "grv4_summary": summary,
        }
    )
    validate_receipt(receipt)
    write_json(output_root / "gates/grv4_result_receipt.json", receipt)


def main() -> None:
    run_grv4()
    print("GRV4 mechanically validated; scientific acceptance anchor is pending.")


if __name__ == "__main__":
    main()
