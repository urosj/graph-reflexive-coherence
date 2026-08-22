"""Numerical controls for the hardened GRV4 frozen-conductance comparison."""

from __future__ import annotations

import math
from typing import Any, Callable, Iterable

import numpy as np


def relative_matrix_error(left: np.ndarray, right: np.ndarray) -> float:
    denominator = max(float(np.linalg.norm(left)), float(np.linalg.norm(right)), 1e-15)
    return float(np.linalg.norm(left - right) / denominator)


def orthonormal_columns(matrix: np.ndarray, *, tolerance: float = 1e-12) -> np.ndarray:
    if matrix.size == 0:
        return np.zeros((matrix.shape[0], 0), dtype=matrix.dtype)
    left, singular_values, _ = np.linalg.svd(matrix, full_matrices=False)
    rank = int(np.sum(singular_values > tolerance))
    return left[:, :rank]


def principal_angle(left: np.ndarray, right: np.ndarray) -> float | None:
    left = orthonormal_columns(left)
    right = orthonormal_columns(right)
    if left.shape[1] != right.shape[1] or left.shape[1] == 0:
        return None
    singular_values = np.linalg.svd(left.conj().T @ right, compute_uv=False)
    minimum = float(np.clip(min(singular_values), 0.0, 1.0))
    return float(math.acos(minimum))


def symmetric_psd_factors(
    matrix: np.ndarray, *, eigenvalue_floor: float
) -> dict[str, Any]:
    values, vectors = np.linalg.eigh(0.5 * (matrix + matrix.T))
    positive = values > eigenvalue_floor
    square_root = (vectors[:, positive] * np.sqrt(values[positive])) @ vectors[:, positive].T
    inverse_square_root = (
        vectors[:, positive] * (1.0 / np.sqrt(values[positive]))
    ) @ vectors[:, positive].T
    return {
        "eigenvalues": values,
        "positive_rank": int(np.sum(positive)),
        "additional_nullity": int(len(values) - np.sum(positive)),
        "square_root": square_root,
        "inverse_square_root": inverse_square_root,
        "positive_definite": bool(np.all(positive)),
    }


def graph_connectivity(
    incidence: np.ndarray, conductance: np.ndarray, *, conductance_floor: float
) -> dict[str, Any]:
    node_count = incidence.shape[0]
    adjacency = [set() for _ in range(node_count)]
    active_edges = 0
    for edge_index, weight in enumerate(conductance):
        if float(weight) <= conductance_floor:
            continue
        endpoints = np.flatnonzero(np.abs(incidence[:, edge_index]) > 0.5)
        if len(endpoints) != 2:
            continue
        left, right = (int(endpoints[0]), int(endpoints[1]))
        adjacency[left].add(right)
        adjacency[right].add(left)
        active_edges += 1
    unvisited = set(range(node_count))
    components = []
    while unvisited:
        seed = min(unvisited)
        stack = [seed]
        member_set = set()
        while stack:
            node = stack.pop()
            if node in member_set:
                continue
            member_set.add(node)
            unvisited.discard(node)
            stack.extend(sorted(adjacency[node] - member_set))
        components.append(sorted(member_set))
    return {
        "connected_component_count": len(components),
        "connected_components": components,
        "active_edge_count": active_edges,
        "connected": len(components) == 1,
    }


def positive_condition_number(matrix: np.ndarray, *, eigenvalue_floor: float) -> float | None:
    values = np.linalg.eigvalsh(0.5 * (matrix + matrix.T))
    positive = values[values > eigenvalue_floor]
    if len(positive) != len(values) or len(positive) == 0:
        return None
    return float(max(positive) / min(positive))


def build_probe_directions(
    basis: np.ndarray, h_cont_tangent: np.ndarray, *, dedup_tolerance: float
) -> list[dict[str, Any]]:
    candidates: list[tuple[str, int, np.ndarray]] = []
    for index in range(basis.shape[1]):
        candidates.append(("canonical_zero_sum", index, basis[:, index]))
    _, structural_vectors = np.linalg.eigh(0.5 * (h_cont_tangent + h_cont_tangent.T))
    for index in range(structural_vectors.shape[1]):
        candidates.append(
            ("structural_eigenvector", index, basis @ structural_vectors[:, index])
        )
    if basis.shape[1] > 1:
        mixed = np.sum(basis, axis=1)
        candidates.append(("deterministic_mixed", 0, mixed))
        alternating = basis @ np.asarray(
            [1.0 if index % 2 == 0 else -1.0 for index in range(basis.shape[1])]
        )
        candidates.append(("deterministic_mixed", 1, alternating))
    records: list[dict[str, Any]] = []
    accepted: list[np.ndarray] = []
    for family, source_index, raw in candidates:
        norm = float(np.linalg.norm(raw))
        if norm <= dedup_tolerance:
            continue
        direction = np.asarray(raw, dtype=float) / norm
        duplicate = any(
            min(np.linalg.norm(direction - prior), np.linalg.norm(direction + prior))
            <= dedup_tolerance
            for prior in accepted
        )
        if duplicate:
            continue
        accepted.append(direction)
        records.append(
            {
                "direction_id": f"direction-{len(records)}",
                "direction_family": family,
                "source_index": source_index,
                "node_direction": direction.tolist(),
                "zero_sum_error": abs(float(np.sum(direction))),
                "unit_norm_error": abs(float(np.linalg.norm(direction)) - 1.0),
            }
        )
    return records


def finite_difference_potential_audit(
    *,
    coherence: np.ndarray,
    basis: np.ndarray,
    analytic_h_p_tangent: np.ndarray,
    potential: Callable[[np.ndarray], np.ndarray],
    functional: Callable[[np.ndarray], float],
    directions: Iterable[dict[str, Any]],
    step: float,
) -> dict[str, Any]:
    columns = []
    for column in range(basis.shape[1]):
        direction = basis[:, column]
        plus = potential(coherence + step * direction)
        minus = potential(coherence - step * direction)
        columns.append(basis.T @ ((plus - minus) / (2.0 * step)))
    finite_hessian = np.column_stack(columns)
    directional_rows = []
    phi = potential(coherence)
    for row in directions:
        direction = np.asarray(row["node_direction"], dtype=float)
        finite = (
            functional(coherence + step * direction)
            - functional(coherence - step * direction)
        ) / (2.0 * step)
        analytic = float(direction.T @ phi)
        directional_rows.append(
            {
                "direction_id": row["direction_id"],
                "finite_difference_directional_derivative": float(finite),
                "runtime_potential_inner_product": analytic,
                "absolute_error": abs(float(finite) - analytic),
            }
        )
    return {
        "step": step,
        "finite_difference_potential_jacobian_tangent": finite_hessian.tolist(),
        "analytic_h_p_tangent": analytic_h_p_tangent.tolist(),
        "h_p_relative_error": relative_matrix_error(
            finite_hessian, analytic_h_p_tangent
        ),
        "h_p_absolute_linf_error": float(
            np.linalg.norm(finite_hessian - analytic_h_p_tangent, ord=np.inf)
        ),
        "directional_functional_rows": directional_rows,
        "maximum_directional_functional_error": max(
            (row["absolute_error"] for row in directional_rows), default=0.0
        ),
    }


def structural_temporal_diagnostics(
    *,
    h_p_tangent: np.ndarray,
    mobility_tangent: np.ndarray,
    dt: float,
    eigenvalue_floor: float,
    structural_tolerance: float,
) -> dict[str, Any]:
    h_cont = -0.5 * (h_p_tangent + h_p_tangent.T)
    mobility = 0.5 * (mobility_tangent + mobility_tangent.T)
    factors = symmetric_psd_factors(mobility, eigenvalue_floor=eigenvalue_floor)
    square_root = factors["square_root"]
    inverse_square_root = factors["inverse_square_root"]
    symmetrized = square_root @ h_cont @ square_root
    relaxation = mobility @ h_cont
    generator = -relaxation
    multiplier = np.eye(relaxation.shape[0]) - dt * relaxation
    values_h, vectors_h = np.linalg.eigh(h_cont)
    values_sym, vectors_sym = np.linalg.eigh(0.5 * (symmetrized + symmetrized.T))
    mapped_modes = square_root @ vectors_sym
    mapped_modes = orthonormal_columns(mapped_modes)
    similarity = inverse_square_root @ relaxation @ square_root
    structural_rows = []
    for index, value in enumerate(values_h):
        if value > structural_tolerance:
            classification = "restoring_structural_curvature"
        elif value < -structural_tolerance:
            classification = "structural_instability"
        else:
            classification = "structural_marginality"
        structural_rows.append(
            {
                "mode_index": index,
                "h_cont_eigenvalue": float(value),
                "classification": classification,
            }
        )
    temporal_rows = []
    for index, value in enumerate(values_sym):
        multiplier_value = 1.0 - dt * float(value)
        if value > structural_tolerance:
            semidiscrete = "relaxing"
        elif value < -structural_tolerance:
            semidiscrete = "growing"
        else:
            semidiscrete = "marginal"
        if abs(multiplier_value) < 1.0 - structural_tolerance:
            discrete = "stable"
        elif abs(multiplier_value) > 1.0 + structural_tolerance:
            discrete = "unstable"
        else:
            discrete = "marginal_within_tolerance"
        temporal_rows.append(
            {
                "mode_index": index,
                "relaxation_rate": float(value),
                "semidiscrete_classification": semidiscrete,
                "explicit_multiplier": multiplier_value,
                "discrete_beat_classification": discrete,
            }
        )
    commutator = mobility @ h_cont - h_cont @ mobility
    return {
        "h_p_tangent": h_p_tangent.tolist(),
        "h_cont_tangent": h_cont.tolist(),
        "restoring_sign_relation": "H_cont=-H_P",
        "structural_modes": structural_rows,
        "mobility_tangent": mobility.tolist(),
        "mobility_positive_definite": factors["positive_definite"],
        "additional_mobility_nullity": factors["additional_nullity"],
        "mobility_square_root": square_root.tolist(),
        "mobility_inverse_square_root": inverse_square_root.tolist(),
        "self_adjoint_representative": symmetrized.tolist(),
        "temporal_relaxation_operator": relaxation.tolist(),
        "semidiscrete_generator": generator.tolist(),
        "explicit_step_multiplier": multiplier.tolist(),
        "temporal_modes": temporal_rows,
        "mapped_physical_reduced_mode_basis": mapped_modes.tolist(),
        "mode_mapping_rule": "a=A_W^(1/2)w; u=Q_C*a",
        "projector_mapping_rule": "P_a=A_W^(1/2)P_w*A_W^(-1/2)",
        "similarity_reconstruction_relative_error": relative_matrix_error(
            similarity, symmetrized
        ),
        "commutator_norm_l2": float(np.linalg.norm(commutator, ord=2)),
        "commutator_relative_norm": float(
            np.linalg.norm(commutator)
            / max(np.linalg.norm(mobility) * np.linalg.norm(h_cont), 1e-15)
        ),
        "structural_modes_are_temporal_modes": bool(
            np.linalg.norm(commutator) <= structural_tolerance
        ),
    }


def robust_multiplier_rows(
    matrix: np.ndarray, *, uncertainty: float
) -> dict[str, Any]:
    values = np.linalg.eigvals(matrix)
    rows = []
    for index, value in enumerate(values):
        magnitude = float(abs(value))
        margin = abs(magnitude - 1.0)
        if magnitude > 1.0 + uncertainty:
            classification = "unstable"
        elif magnitude < 1.0 - uncertainty:
            classification = "stable"
        else:
            classification = "marginal_within_uncertainty"
        rows.append(
            {
                "mode_index": index,
                "eigenvalue": {"real": float(value.real), "imag": float(value.imag)},
                "magnitude": magnitude,
                "unit_circle_margin": margin,
                "uncertainty_radius": uncertainty,
                "classification": classification,
            }
        )
    classes = {row["classification"] for row in rows}
    aggregate = (
        "unstable"
        if "unstable" in classes
        else (
            "marginal_within_uncertainty"
            if "marginal_within_uncertainty" in classes
            else "stable"
        )
    )
    return {"modes": rows, "aggregate_classification": aggregate}


def real_invariant_basis(
    matrix: np.ndarray, *, minimum_magnitude: float, complex_tolerance: float
) -> tuple[np.ndarray, list[dict[str, Any]]]:
    values, vectors = np.linalg.eig(matrix)
    columns: list[np.ndarray] = []
    records = []
    consumed: set[int] = set()
    for index, value in enumerate(values):
        if index in consumed or abs(value) < minimum_magnitude:
            continue
        has_conjugate_partner = any(
            candidate != index
            and candidate not in consumed
            and abs(values[candidate] - value.conjugate()) <= max(
                complex_tolerance, 10.0 * abs(value.imag)
            )
            for candidate in range(len(values))
        )
        complex_plane_is_resolved = bool(
            has_conjugate_partner
            and (
                abs(value.imag) > 0.0
                and float(np.linalg.norm(vectors[:, index].imag)) > complex_tolerance
            )
        )
        if complex_plane_is_resolved:
            partner = min(
                (
                    candidate
                    for candidate in range(len(values))
                    if candidate != index and candidate not in consumed
                ),
                key=lambda candidate: abs(values[candidate] - value.conjugate()),
                default=None,
            )
            columns.extend([vectors[:, index].real, vectors[:, index].imag])
            consumed.add(index)
            if partner is not None:
                consumed.add(partner)
            records.append(
                {
                    "kind": "complex_conjugate_real_invariant_plane",
                    "eigenvalues": [
                        {"real": float(value.real), "imag": float(value.imag)},
                        {"real": float(value.real), "imag": float(-value.imag)},
                    ],
                    "dimension": 2,
                }
            )
        else:
            columns.append(vectors[:, index].real)
            consumed.add(index)
            records.append(
                {
                    "kind": "real_invariant_direction",
                    "eigenvalues": [
                        {"real": float(value.real), "imag": float(value.imag)}
                    ],
                    "dimension": 1,
                }
            )
    if not columns:
        return np.zeros((matrix.shape[0], 0)), records
    return orthonormal_columns(np.column_stack(columns)), records


def metric_subspace_comparison(
    *,
    frozen_mode_basis: np.ndarray,
    full_matrix: np.ndarray,
    c_dimension: int,
    block_scales: dict[str, float],
    slow_minimum_magnitude: float,
    complex_tolerance: float,
    uncertainty: float,
    deadbeat_tolerance: float,
) -> dict[str, Any]:
    full_dimension = full_matrix.shape[0]
    w_dimension = full_dimension - c_dimension
    c_scale = float(block_scales["C"])
    w_scale = float(block_scales.get("W", 1.0))
    metric_sqrt = np.diag(
        [1.0 / c_scale] * c_dimension + [1.0 / w_scale] * w_dimension
    )
    metric_inverse_sqrt = np.diag(
        [c_scale] * c_dimension + [w_scale] * w_dimension
    )
    embedded = np.zeros((full_dimension, frozen_mode_basis.shape[1]))
    embedded[:c_dimension, :] = frozen_mode_basis
    embedded_metric = orthonormal_columns(metric_sqrt @ embedded)
    full_metric_matrix = metric_sqrt @ full_matrix @ metric_inverse_sqrt
    full_slow_metric, cluster_records = real_invariant_basis(
        full_metric_matrix,
        minimum_magnitude=slow_minimum_magnitude,
        complex_tolerance=complex_tolerance,
    )
    angle = principal_angle(embedded_metric, full_slow_metric)
    projector = embedded_metric @ embedded_metric.T
    invariance_defect = float(
        np.linalg.norm((np.eye(full_dimension) - projector) @ full_metric_matrix @ projector)
    )
    full_physical_slow = metric_inverse_sqrt @ full_slow_metric
    c_projection = full_physical_slow[:c_dimension, :]
    c_projection_basis = orthonormal_columns(c_projection)
    c_projection_angle = principal_angle(frozen_mode_basis, c_projection_basis)
    outside = full_slow_metric[c_dimension:, :]
    outside_fraction = float(
        np.linalg.norm(outside) ** 2 / max(np.linalg.norm(full_slow_metric) ** 2, 1e-15)
    )
    values = np.linalg.eigvals(full_matrix)
    return {
        "state_space": {
            "full_dimension": full_dimension,
            "C_dimension": c_dimension,
            "W_or_other_dimension": w_dimension,
            "embedding": "iota_C:u->(u,0)",
            "projection": "pi_C:(u,omega)->u",
            "metric_id": "GRV3_branch_rms_physical_scale_v1",
            "block_scales": block_scales,
        },
        "real_invariant_cluster_records": cluster_records,
        "full_metric_slow_subspace_dimension": full_slow_metric.shape[1],
        "frozen_embedded_subspace_dimension": embedded_metric.shape[1],
        "metric_principal_angle_radians": angle,
        "physical_C_projection_angle_radians": c_projection_angle,
        "full_slow_subspace_fraction_outside_C": outside_fraction,
        "embedded_frozen_subspace_invariance_defect_l2": invariance_defect,
        "deadbeat_or_overwrite_multiplier_count": int(
            np.sum(np.abs(values) <= deadbeat_tolerance)
        ),
        "deadbeat_modes_excluded_from_slow_disagreement": True,
        "uncertainty_radius": uncertainty,
    }


def conjugacy_error(
    source: np.ndarray, target: np.ndarray, transport: np.ndarray
) -> float:
    inverse = np.linalg.inv(transport)
    return relative_matrix_error(target, transport @ source @ inverse)


def conjugacy_errors(
    source: np.ndarray, target: np.ndarray, transport: np.ndarray
) -> dict[str, float]:
    inverse = np.linalg.inv(transport)
    transformed = transport @ source @ inverse
    return {
        "relative": relative_matrix_error(target, transformed),
        "absolute_linf": float(np.linalg.norm(target - transformed, ord=np.inf)),
        "source_norm_linf": float(np.linalg.norm(source, ord=np.inf)),
        "target_norm_linf": float(np.linalg.norm(target, ord=np.inf)),
    }
