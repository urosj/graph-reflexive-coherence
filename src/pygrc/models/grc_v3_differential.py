"""Reference differential-summary helpers for the GRCV3 family."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import math

from pygrc.core import NodeId, WeightedGraphBackend

from .grc_v3_state import BasinAttributes, OrientedEdgeId


_EIGENVALUE_ZERO_TOLERANCE = 1e-12


def induced_local_frame_displacements(
    graph: WeightedGraphBackend,
    *,
    node_id: NodeId,
    base_conductance: Mapping[int, float],
    dimension: int,
) -> dict[NodeId, list[float]]:
    """Build canonical graph-intrinsic pseudo-displacements for one node."""

    neighbors = tuple(graph.neighbors(node_id))
    if dimension <= 0:
        return {neighbor_id: [] for neighbor_id in neighbors}
    if not neighbors:
        return {}

    ego_nodes = (node_id, *neighbors)
    weights = _ego_weight_matrix(
        graph,
        ego_nodes=ego_nodes,
        base_conductance=base_conductance,
    )
    laplacian = _normalized_weighted_laplacian(weights)
    eigenpairs = _jacobi_eigenpairs(laplacian)

    coordinate_vectors: list[list[float]] = []
    for eigenvalue, eigenvector in eigenpairs:
        if abs(eigenvalue) <= _EIGENVALUE_ZERO_TOLERANCE:
            continue
        fixed = _fix_eigenvector_sign(eigenvector)
        coordinate_vectors.append(fixed)
        if len(coordinate_vectors) == dimension:
            break

    while len(coordinate_vectors) < dimension:
        coordinate_vectors.append([0.0] * len(ego_nodes))

    center_index = 0
    displacements: dict[NodeId, list[float]] = {}
    for neighbor_index, neighbor_id in enumerate(neighbors, start=1):
        displacements[neighbor_id] = [
            coordinate_vector[neighbor_index] - coordinate_vector[center_index]
            for coordinate_vector in coordinate_vectors
        ]
    return displacements


def weighted_least_squares_gradient(
    *,
    center_value: float,
    displacements: Mapping[NodeId, Sequence[float]],
    neighbor_values: Mapping[NodeId, float],
    weights: Mapping[NodeId, float],
    regularization: float,
) -> list[float]:
    """Compute the canonical weighted least-squares gradient estimate."""

    dimension = _infer_dimension(displacements.values())
    if dimension == 0:
        return []
    moment = _zero_matrix(dimension)
    rhs = [0.0] * dimension

    for neighbor_id, displacement in displacements.items():
        weight = float(weights.get(neighbor_id, 0.0))
        if weight <= 0.0:
            continue
        delta = [float(value) for value in displacement]
        delta_value = float(neighbor_values[neighbor_id]) - float(center_value)
        for row in range(dimension):
            rhs[row] += weight * delta[row] * delta_value
            for column in range(dimension):
                moment[row][column] += weight * delta[row] * delta[column]

    for index in range(dimension):
        moment[index][index] += regularization

    return _solve_linear_system(moment, rhs)


def weighted_least_squares_hessian(
    *,
    center_value: float,
    gradient: Sequence[float],
    displacements: Mapping[NodeId, Sequence[float]],
    neighbor_values: Mapping[NodeId, float],
    weights: Mapping[NodeId, float],
    regularization: float,
) -> list[list[float]]:
    """Compute the canonical weighted least-squares Hessian estimate.

    This is intentionally the Appendix A.3 reference backend from the
    `GRCV3` spec, not the literal raw weighted moment written in Eq. (3) of
    the paper. The paper-level Eq. (3) is treated as the conceptual discrete
    Hessian summary, while the implementation backend subtracts the fitted
    linear term and solves a regularized quadratic least-squares problem so
    the stored Hessian better isolates curvature and remains stable on sparse
    local neighborhoods.
    """

    dimension = _infer_dimension(displacements.values())
    if dimension == 0:
        return []
    feature_dimension = dimension * (dimension + 1) // 2
    normal = _zero_matrix(feature_dimension)
    rhs = [0.0] * feature_dimension

    for neighbor_id, displacement in displacements.items():
        weight = float(weights.get(neighbor_id, 0.0))
        if weight <= 0.0:
            continue
        delta = [float(value) for value in displacement]
        feature = _quadratic_feature(delta)
        predicted_linear = sum(
            float(gradient[index]) * delta[index] for index in range(dimension)
        )
        residual = float(neighbor_values[neighbor_id]) - float(center_value) - predicted_linear
        for row in range(feature_dimension):
            rhs[row] += weight * feature[row] * residual
            for column in range(feature_dimension):
                normal[row][column] += weight * feature[row] * feature[column]

    for index in range(feature_dimension):
        normal[index][index] += regularization

    coefficients = _solve_linear_system(normal, rhs)
    return _reconstruct_symmetric_matrix(coefficients, dimension=dimension)


def net_flux_summary(
    *,
    node_id: NodeId,
    graph: WeightedGraphBackend,
    flux: Mapping[OrientedEdgeId, float],
    displacements: Mapping[NodeId, Sequence[float]],
    dimension: int,
) -> list[float]:
    """Aggregate oriented edge flux into a node-level vector summary."""

    summary = [0.0] * dimension
    if dimension == 0:
        return summary
    for edge_id in graph.incident_edge_ids(node_id):
        node_a, node_b = graph.edge_endpoints(edge_id)
        neighbor_id = node_b if node_a == node_id else node_a
        displacement = displacements.get(neighbor_id)
        if displacement is None:
            continue
        edge_flux = float(flux.get((edge_id, node_id), 0.0))
        for index in range(dimension):
            summary[index] += edge_flux * float(displacement[index])
    return summary


def calibrate_hessian_sign(
    *,
    candidate_seed_ids: Sequence[NodeId],
    basin_attributes: Mapping[NodeId, BasinAttributes],
    gradient_threshold: float,
    hessian_threshold: float,
) -> int:
    """Choose the canonical signed-Hessian convention for one state."""

    candidate_ids = tuple(candidate_seed_ids)
    if not candidate_ids:
        return 1

    sign_scores: dict[int, tuple[int, float, tuple[int, ...]]] = {}
    for sign in (1, -1):
        positive_count = 0
        total_margin = 0.0
        satisfied_ids: list[int] = []
        for node_id in candidate_ids:
            attributes = basin_attributes[node_id]
            gradient_norm = math.sqrt(sum(value * value for value in attributes.gradient))
            if gradient_norm > gradient_threshold:
                continue
            signed_hessian = [
                [sign * float(value) for value in row]
                for row in attributes.hessian
            ]
            eigenvalues = symmetric_eigenvalues(signed_hessian)
            if eigenvalues and min(eigenvalues) > hessian_threshold:
                positive_count += 1
                total_margin += min(eigenvalues)
                satisfied_ids.append(int(node_id))
        sign_scores[sign] = (positive_count, total_margin, tuple(sorted(satisfied_ids)))

    positive_score = sign_scores[1]
    negative_score = sign_scores[-1]
    if positive_score > negative_score:
        return 1
    if negative_score > positive_score:
        return -1
    return 1


def symmetric_eigenvalues(matrix: Sequence[Sequence[float]]) -> list[float]:
    """Return the sorted eigenvalues of one real symmetric matrix."""

    if not matrix:
        return []
    return [eigenvalue for eigenvalue, _ in _jacobi_eigenpairs(matrix)]


def _ego_weight_matrix(
    graph: WeightedGraphBackend,
    *,
    ego_nodes: Sequence[NodeId],
    base_conductance: Mapping[int, float],
) -> list[list[float]]:
    index_by_node = {node_id: index for index, node_id in enumerate(ego_nodes)}
    size = len(ego_nodes)
    weights = _zero_matrix(size)
    for edge_id in graph.iter_live_edge_ids():
        node_a, node_b = graph.edge_endpoints(edge_id)
        if node_a not in index_by_node or node_b not in index_by_node:
            continue
        edge_weight = float(base_conductance.get(edge_id, 1.0))
        i = index_by_node[node_a]
        j = index_by_node[node_b]
        weights[i][j] += edge_weight
        weights[j][i] += edge_weight
    return weights


def _normalized_weighted_laplacian(weights: Sequence[Sequence[float]]) -> list[list[float]]:
    size = len(weights)
    degrees = [sum(float(value) for value in row) for row in weights]
    laplacian = _zero_matrix(size)
    for row in range(size):
        for column in range(size):
            weight = float(weights[row][column])
            if row == column:
                laplacian[row][column] = 1.0 if degrees[row] > 0.0 else 0.0
            elif weight > 0.0 and degrees[row] > 0.0 and degrees[column] > 0.0:
                laplacian[row][column] = -weight / math.sqrt(
                    degrees[row] * degrees[column]
                )
            else:
                laplacian[row][column] = 0.0
    return laplacian


def _fix_eigenvector_sign(vector: Sequence[float]) -> list[float]:
    max_index = max(
        range(len(vector)),
        key=lambda index: (abs(float(vector[index])), -index),
    )
    sign = -1.0 if float(vector[max_index]) < 0.0 else 1.0
    return [sign * float(value) for value in vector]


def _quadratic_feature(delta: Sequence[float]) -> list[float]:
    feature: list[float] = []
    dimension = len(delta)
    for index in range(dimension):
        feature.append(0.5 * float(delta[index]) * float(delta[index]))
    for row in range(dimension):
        for column in range(row + 1, dimension):
            feature.append(float(delta[row]) * float(delta[column]))
    return feature


def _reconstruct_symmetric_matrix(
    coefficients: Sequence[float],
    *,
    dimension: int,
) -> list[list[float]]:
    matrix = _zero_matrix(dimension)
    cursor = 0
    for index in range(dimension):
        matrix[index][index] = float(coefficients[cursor])
        cursor += 1
    for row in range(dimension):
        for column in range(row + 1, dimension):
            value = float(coefficients[cursor])
            matrix[row][column] = value
            matrix[column][row] = value
            cursor += 1
    return matrix


def _solve_linear_system(matrix: Sequence[Sequence[float]], rhs: Sequence[float]) -> list[float]:
    size = len(matrix)
    if size == 0:
        return []
    augmented = [
        [float(matrix[row][column]) for column in range(size)] + [float(rhs[row])]
        for row in range(size)
    ]

    for pivot_index in range(size):
        pivot_row = max(
            range(pivot_index, size),
            key=lambda row: (abs(augmented[row][pivot_index]), -row),
        )
        if abs(augmented[pivot_row][pivot_index]) <= _EIGENVALUE_ZERO_TOLERANCE:
            raise ValueError("singular linear system in GRCV3 differential backend")
        if pivot_row != pivot_index:
            augmented[pivot_index], augmented[pivot_row] = (
                augmented[pivot_row],
                augmented[pivot_index],
            )

        pivot_value = augmented[pivot_index][pivot_index]
        for column in range(pivot_index, size + 1):
            augmented[pivot_index][column] /= pivot_value

        for row in range(size):
            if row == pivot_index:
                continue
            factor = augmented[row][pivot_index]
            if abs(factor) <= _EIGENVALUE_ZERO_TOLERANCE:
                continue
            for column in range(pivot_index, size + 1):
                augmented[row][column] -= factor * augmented[pivot_index][column]

    return [augmented[row][size] for row in range(size)]


def _jacobi_eigenpairs(matrix: Sequence[Sequence[float]]) -> list[tuple[float, list[float]]]:
    size = len(matrix)
    if size == 0:
        return []
    if any(len(row) != size for row in matrix):
        raise ValueError("Jacobi eigen decomposition requires a square matrix")

    working = [[float(value) for value in row] for row in matrix]
    eigenvectors = _identity_matrix(size)
    max_iterations = max(20, size * size * 12)

    for _ in range(max_iterations):
        pivot_row, pivot_column, pivot_value = _largest_off_diagonal(working)
        if abs(pivot_value) <= _EIGENVALUE_ZERO_TOLERANCE:
            break

        diff = working[pivot_column][pivot_column] - working[pivot_row][pivot_row]
        if abs(diff) <= _EIGENVALUE_ZERO_TOLERANCE:
            angle = math.pi / 4.0
        else:
            angle = 0.5 * math.atan2(2.0 * pivot_value, diff)
        cosine = math.cos(angle)
        sine = math.sin(angle)

        for index in range(size):
            if index in (pivot_row, pivot_column):
                continue
            row_value = working[index][pivot_row]
            column_value = working[index][pivot_column]
            working[index][pivot_row] = working[pivot_row][index] = (
                cosine * row_value - sine * column_value
            )
            working[index][pivot_column] = working[pivot_column][index] = (
                sine * row_value + cosine * column_value
            )

        row_diagonal = working[pivot_row][pivot_row]
        column_diagonal = working[pivot_column][pivot_column]
        row_column = working[pivot_row][pivot_column]
        working[pivot_row][pivot_row] = (
            cosine * cosine * row_diagonal
            - 2.0 * sine * cosine * row_column
            + sine * sine * column_diagonal
        )
        working[pivot_column][pivot_column] = (
            sine * sine * row_diagonal
            + 2.0 * sine * cosine * row_column
            + cosine * cosine * column_diagonal
        )
        working[pivot_row][pivot_column] = 0.0
        working[pivot_column][pivot_row] = 0.0

        for index in range(size):
            vector_row = eigenvectors[index][pivot_row]
            vector_column = eigenvectors[index][pivot_column]
            eigenvectors[index][pivot_row] = (
                cosine * vector_row - sine * vector_column
            )
            eigenvectors[index][pivot_column] = (
                sine * vector_row + cosine * vector_column
            )

    eigenpairs = [
        (
            float(working[index][index]),
            [float(eigenvectors[row][index]) for row in range(size)],
        )
        for index in range(size)
    ]
    return sorted(
        eigenpairs,
        key=lambda pair: (
            pair[0],
            [round(component, 15) for component in pair[1]],
        ),
    )


def _largest_off_diagonal(matrix: Sequence[Sequence[float]]) -> tuple[int, int, float]:
    size = len(matrix)
    best_row = 0
    best_column = 1 if size > 1 else 0
    best_value = 0.0
    for row in range(size):
        for column in range(row + 1, size):
            value = float(matrix[row][column])
            if (
                abs(value) > abs(best_value)
                or (
                    math.isclose(abs(value), abs(best_value))
                    and (row, column) < (best_row, best_column)
                )
            ):
                best_row = row
                best_column = column
                best_value = value
    return best_row, best_column, best_value


def _identity_matrix(size: int) -> list[list[float]]:
    return [
        [1.0 if row == column else 0.0 for column in range(size)]
        for row in range(size)
    ]


def _zero_matrix(size: int) -> list[list[float]]:
    return [[0.0 for _ in range(size)] for _ in range(size)]


def _infer_dimension(displacements: Sequence[Sequence[float]]) -> int:
    for displacement in displacements:
        return len(displacement)
    return 0


__all__ = [
    "calibrate_hessian_sign",
    "induced_local_frame_displacements",
    "net_flux_summary",
    "symmetric_eigenvalues",
    "weighted_least_squares_gradient",
    "weighted_least_squares_hessian",
]
