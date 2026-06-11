"""Runtime helpers for the GRC9V3 hybrid differential layer."""

from __future__ import annotations

from collections.abc import Mapping
import math
from typing import Any

from pygrc.core import EdgeId, NodeId

from .grc_9_ports import port_to_rc, slot_to_port_id
from .grc_9_state import PortEdge
from .grc_9_v3_state import GRC9V3NodeState, GRC9V3State
from .grc_v3_differential import weighted_least_squares_hessian


_ROW_COUNT = 3
_ALLOWED_EDGE_LABELS = {"geometric_length", "temporal_delay", "flux_coupling"}


def rebuild_grc9v3_differential_state(
    state: GRC9V3State,
    *,
    evolution: Mapping[str, Any],
    hessian_backend: str,
) -> None:
    """Rebuild the Phase 7 row-basis differential state in-place."""

    previous_current_min_signed = state.cached_quantities.get(
        "current_min_signed_hessian_by_node",
        {},
    )
    live_node_ids = set(state.topology.iter_live_node_ids())
    gradient_by_node, row_neighborhoods = compute_row_basis_gradient(state)
    unsigned_hessian_by_node = compute_unsigned_row_basis_hessian(
        state,
        row_neighborhoods=row_neighborhoods,
    )
    comparison_hessian_by_node = compute_weighted_least_squares_hessian_rows(
        state,
        gradient_by_node=gradient_by_node,
        regularization=float(evolution.get("hessian_regularization", 0.0)),
    )

    selected_hessian_by_node: dict[NodeId, list[float]]
    if hessian_backend == "row_basis_diagonal":
        selected_hessian_by_node = unsigned_hessian_by_node
    elif hessian_backend == "weighted_least_squares":
        selected_hessian_by_node = {
            node_id: _matrix_diagonal(comparison_hessian_by_node.get(node_id, []))
            for node_id in sorted(state.topology.iter_live_node_ids())
        }
    else:
        raise ValueError(f"unsupported hessian_backend {hessian_backend!r}")

    hessian_sign = _resolve_hessian_sign(
        state,
        selected_hessian_by_node=selected_hessian_by_node,
        gradient_by_node=gradient_by_node,
        gradient_threshold=float(evolution.get("eps_gradient", 1e-3)),
        hessian_threshold=float(evolution.get("eps_hessian", 1e-3)),
    )
    signed_hessian_by_node = {
        node_id: [float(hessian_sign * value) for value in values]
        for node_id, values in selected_hessian_by_node.items()
    }
    net_flux_by_node = compute_net_flux_summary_rows(state)
    row_mismatch_by_node = compute_row_mismatch_sums(
        state,
        row_neighborhoods=row_neighborhoods,
    )
    tensor_by_node = compute_hybrid_node_tensors(
        state,
        row_mismatch_by_node=row_mismatch_by_node,
        net_flux_by_node=net_flux_by_node,
        lambda_c=float(evolution.get("lambda_c", 1.0)),
        xi_c=float(evolution.get("xi_c", 1.0)),
        zeta_c=float(evolution.get("zeta_c", 1.0)),
    )

    rebuilt_nodes: dict[NodeId, GRC9V3NodeState] = {}
    for node_id in sorted(state.topology.iter_live_node_ids()):
        previous = state.nodes.get(node_id)
        coherence = _coherence(state, node_id)
        rebuilt_nodes[node_id] = GRC9V3NodeState(
            coherence=coherence,
            gradient_row_basis=gradient_by_node.get(node_id, [0.0] * _ROW_COUNT),
            signed_hessian_row_basis=signed_hessian_by_node.get(
                node_id,
                [0.0] * _ROW_COUNT,
            ),
            net_flux_summary=net_flux_by_node.get(node_id, [0.0] * _ROW_COUNT),
            basin_mass=(
                previous.basin_mass if previous is not None else float(coherence)
            ),
            basin_id=previous.basin_id if previous is not None else node_id,
            parent_id=previous.parent_id if previous is not None else None,
            depth=previous.depth if previous is not None else 0,
        )

    state.nodes = rebuilt_nodes
    state.cached_quantities["row_neighborhoods"] = {
        str(node_id): {
            str(row): list(edge_ids)
            for row, edge_ids in sorted(row_mapping.items())
        }
        for node_id, row_mapping in sorted(row_neighborhoods.items())
    }
    state.cached_quantities["row_basis_hessian_unsigned"] = {
        str(node_id): list(values)
        for node_id, values in sorted(unsigned_hessian_by_node.items())
    }
    state.cached_quantities["row_mismatch_sums"] = {
        str(node_id): list(values)
        for node_id, values in sorted(row_mismatch_by_node.items())
    }
    state.cached_quantities["weighted_least_squares_hessian"] = {
        str(node_id): matrix
        for node_id, matrix in sorted(comparison_hessian_by_node.items())
    }
    state.cached_quantities["hessian_backend"] = hessian_backend
    state.cached_quantities["hessian_sign"] = hessian_sign
    if isinstance(previous_current_min_signed, Mapping):
        previous_history: dict[str, float] = {}
        pruned_node_ids: list[str] = []
        for node_id, value in previous_current_min_signed.items():
            node_id_int = int(node_id)
            if node_id_int in live_node_ids:
                previous_history[str(node_id_int)] = float(value)
            else:
                pruned_node_ids.append(str(node_id))
        state.cached_quantities["previous_min_signed_hessian_by_node"] = previous_history
        state.cached_quantities["signed_hessian_history_pruned_node_ids"] = pruned_node_ids
    state.cached_quantities["current_min_signed_hessian_by_node"] = {
        str(node_id): min(values) if values else float("inf")
        for node_id, values in sorted(signed_hessian_by_node.items())
    }
    state.cached_quantities["hybrid_node_tensors"] = {
        str(node_id): matrix for node_id, matrix in sorted(tensor_by_node.items())
    }


def compute_row_basis_gradient(
    state: GRC9V3State,
) -> tuple[dict[NodeId, list[float]], dict[NodeId, dict[int, tuple[EdgeId, ...]]]]:
    """Compute Eq. G2 row-weighted coherence differences."""

    gradients: dict[NodeId, list[float]] = {}
    row_neighborhoods: dict[NodeId, dict[int, tuple[EdgeId, ...]]] = {}
    for node_id in sorted(state.topology.iter_live_node_ids()):
        row_edges = _row_edges_by_node(state, node_id)
        row_neighborhoods[node_id] = {
            row: tuple(edge_ids) for row, edge_ids in row_edges.items()
        }
        gradients[node_id] = [
            _weighted_row_difference(state, node_id=node_id, edge_ids=row_edges[row])
            for row in range(1, _ROW_COUNT + 1)
        ]
    return gradients, row_neighborhoods


def compute_unsigned_row_basis_hessian(
    state: GRC9V3State,
    *,
    row_neighborhoods: Mapping[NodeId, Mapping[int, tuple[EdgeId, ...]]],
) -> dict[NodeId, list[float]]:
    """Compute Eq. G3 unsigned diagonal row-basis Hessian values."""

    return {
        node_id: [
            _weighted_row_difference(
                state,
                node_id=node_id,
                edge_ids=tuple(row_mapping.get(row, ())),
            )
            for row in range(1, _ROW_COUNT + 1)
        ]
        for node_id, row_mapping in row_neighborhoods.items()
    }


def compute_row_mismatch_sums(
    state: GRC9V3State,
    *,
    row_neighborhoods: Mapping[NodeId, Mapping[int, tuple[EdgeId, ...]]],
) -> dict[NodeId, list[float]]:
    """Compute the Eq. (1) row-local squared mismatch sums."""

    return {
        node_id: [
            _row_squared_mismatch_sum(
                state,
                node_id=node_id,
                edge_ids=tuple(row_mapping.get(row, ())),
            )
            for row in range(1, _ROW_COUNT + 1)
        ]
        for node_id, row_mapping in row_neighborhoods.items()
    }


def compute_weighted_least_squares_hessian_rows(
    state: GRC9V3State,
    *,
    gradient_by_node: Mapping[NodeId, list[float]],
    regularization: float,
) -> dict[NodeId, list[list[float]]]:
    """Compute a GRCV3-style comparison Hessian in the fixed row basis."""

    hessians: dict[NodeId, list[list[float]]] = {}
    for node_id in sorted(state.topology.iter_live_node_ids()):
        displacements: dict[int, list[float]] = {}
        neighbor_values: dict[int, float] = {}
        weights: dict[int, float] = {}
        for edge_id in sorted(state.topology.incident_edge_ids(node_id)):
            row, _ = port_to_rc(_local_port_id(state, edge_id=edge_id, node_id=node_id))
            displacement = [0.0] * _ROW_COUNT
            displacement[row - 1] = 1.0
            sample_id = int(edge_id)
            displacements[sample_id] = displacement
            neighbor_values[sample_id] = _coherence(
                state,
                _neighbor_for_edge(state, edge_id=edge_id, node_id=node_id),
            )
            weights[sample_id] = _edge_conductance(state, edge_id)
        hessians[node_id] = weighted_least_squares_hessian(
            center_value=_coherence(state, node_id),
            gradient=gradient_by_node.get(node_id, [0.0] * _ROW_COUNT),
            displacements=displacements,
            neighbor_values=neighbor_values,
            weights=weights,
            regularization=regularization,
        )
    return hessians


def compute_net_flux_summary_rows(state: GRC9V3State) -> dict[NodeId, list[float]]:
    """Aggregate oriented edge flux by the local GRC9 row."""

    summaries: dict[NodeId, list[float]] = {}
    for node_id in sorted(state.topology.iter_live_node_ids()):
        summary = [0.0] * _ROW_COUNT
        for edge_id in sorted(state.topology.incident_edge_ids(node_id)):
            row, _ = port_to_rc(_local_port_id(state, edge_id=edge_id, node_id=node_id))
            summary[row - 1] += _oriented_flux(state, edge_id=edge_id, node_id=node_id)
        summaries[node_id] = [float(value) for value in summary]
    return summaries


def compute_hybrid_node_tensors(
    state: GRC9V3State,
    *,
    row_mismatch_by_node: Mapping[NodeId, list[float]],
    net_flux_by_node: Mapping[NodeId, list[float]],
    lambda_c: float,
    xi_c: float,
    zeta_c: float,
) -> dict[NodeId, list[list[float]]]:
    """Materialize the GRC9 Eq. (1) tensor in the GRC9V3 row basis."""

    tensors: dict[NodeId, list[list[float]]] = {}
    for node_id in sorted(state.topology.iter_live_node_ids()):
        coherence = _coherence(state, node_id)
        row_mismatch = _pad_row_vector(row_mismatch_by_node.get(node_id, []))
        net_flux = _pad_row_vector(net_flux_by_node.get(node_id, []))
        flux_feedback = zeta_c * (sum(net_flux) ** 2)
        matrix = _zero_matrix()
        for row in range(_ROW_COUNT):
            matrix[row][row] = (
                lambda_c * coherence
                + xi_c * row_mismatch[row]
                + flux_feedback
            )
        tensors[node_id] = matrix
    return tensors


def rebuild_grc9v3_transport_state(
    state: GRC9V3State,
    *,
    evolution: Mapping[str, Any],
    modes: Mapping[str, Any],
) -> None:
    """Rebuild scalar transport and analytic edge labels."""

    compute_base_conductance(state, evolution=evolution, modes=modes)
    compute_edge_labels(state, evolution=evolution, modes=modes, pre_flux_only=True)
    compute_potential(state, evolution=evolution)
    compute_flux(state, evolution=evolution)
    compute_edge_labels(state, evolution=evolution, modes=modes, pre_flux_only=False)


def rebuild_grc9v3_identity_state(
    state: GRC9V3State,
    *,
    evolution: Mapping[str, Any],
) -> None:
    """Rebuild flux-topology identity and Eq. G7 geometric seed diagnostics."""

    detect_flux_topology_identities(state)
    validate_geometric_basin_seeds(state, evolution=evolution)
    compute_effective_basin_masses(state)


def compute_base_conductance(
    state: GRC9V3State,
    *,
    evolution: Mapping[str, Any],
    modes: Mapping[str, Any],
) -> None:
    """Compute scalar base conductance on occupied port-pairs."""

    curvature_backend = str(modes.get("curvature_backend", "none"))
    if curvature_backend != "none":
        raise NotImplementedError(
            "Phase 7 Iteration 3 implements base conductance only for "
            "curvature_backend='none'"
        )

    alpha = float(evolution.get("alpha", 1.0))
    beta = float(evolution.get("beta", 1.0))
    gamma = float(evolution.get("gamma", 1.0))
    updated_conductance: dict[EdgeId, float] = {}
    updated_port_edges: dict[EdgeId, PortEdge] = {}

    for edge_id in sorted(state.topology.iter_live_edge_ids()):
        port_edge = state.port_edges[edge_id]
        coherence_u = _coherence(state, port_edge.node_u)
        coherence_v = _coherence(state, port_edge.node_v)
        gradient_u = state.nodes.get(port_edge.node_u, GRC9V3NodeState(0.0)).gradient_row_basis
        gradient_v = state.nodes.get(port_edge.node_v, GRC9V3NodeState(0.0)).gradient_row_basis
        gradient_gap_squared = _squared_vector_gap(
            _pad_row_vector(gradient_u),
            _pad_row_vector(gradient_v),
        )
        exponent = (
            -alpha * (coherence_u + coherence_v) / 2.0
            - beta * gradient_gap_squared / 2.0
            - gamma * (port_edge.flux_uv**2) / 2.0
        )
        conductance = max(1e-12, float(math.exp(exponent)))
        updated_conductance[edge_id] = conductance
        updated_port_edges[edge_id] = PortEdge(
            node_u=port_edge.node_u,
            port_u=port_edge.port_u,
            node_v=port_edge.node_v,
            port_v=port_edge.port_v,
            conductance=conductance,
            flux_uv=port_edge.flux_uv,
        )

    state.base_conductance = updated_conductance
    state.port_edges = updated_port_edges
    state.cached_quantities["edge_curvature"] = {
        str(edge_id): 0.0 for edge_id in sorted(updated_conductance)
    }


def compute_edge_labels(
    state: GRC9V3State,
    *,
    evolution: Mapping[str, Any],
    modes: Mapping[str, Any],
    pre_flux_only: bool,
) -> None:
    """Compute selected analytic edge labels with explicit modes."""

    selected_labels = _selected_edge_labels(modes)
    live_edge_ids = tuple(sorted(state.topology.iter_live_edge_ids()))
    computation_mode = dict(state.edge_label_computation_mode)
    label_params = dict(state.edge_label_params)
    label_params["selection"] = (
        "all"
        if modes.get("edge_label_selection", "all") == "all"
        else tuple(sorted(selected_labels))
    )

    if pre_flux_only:
        state.geometric_length = {}
        if "geometric_length" in selected_labels:
            computation_mode["geometric_length"] = "inverse_base_conductance"
            label_params["geometric_length"] = {
                "mode": "inverse_base_conductance",
                "source": "fixed_port_chart",
            }
            for edge_id in live_edge_ids:
                state.geometric_length[edge_id] = _geometric_length(state, edge_id)
    else:
        state.flux_coupling = {}
        state.temporal_delay = {}
        if "flux_coupling" in selected_labels:
            computation_mode["flux_coupling"] = "absolute_flux"
            label_params["flux_coupling"] = {"mode": "absolute_flux"}
            for edge_id in live_edge_ids:
                state.flux_coupling[edge_id] = abs(state.port_edges[edge_id].flux_uv)

        if "temporal_delay" in selected_labels:
            v0 = float(evolution.get("v0", 1.0))
            rho = float(evolution.get("rho", 1.0))
            eps_tau = float(evolution.get("eps_tau", 1e-9))
            computation_mode["temporal_delay"] = "transport_ratio"
            label_params["temporal_delay"] = {
                "mode": "transport_ratio",
                "v0": v0,
                "rho": rho,
                "eps_tau": eps_tau,
                "geometric_length_mode": computation_mode.get(
                    "geometric_length",
                    "inverse_base_conductance",
                ),
            }
            for edge_id in live_edge_ids:
                geometric_length = state.geometric_length.get(
                    edge_id,
                    _geometric_length(state, edge_id),
                )
                flux_coupling = state.flux_coupling.get(
                    edge_id,
                    abs(state.port_edges[edge_id].flux_uv),
                )
                state.temporal_delay[edge_id] = geometric_length / (
                    v0 + rho * flux_coupling + eps_tau
                )

    state.edge_label_computation_mode = computation_mode
    state.edge_label_params = label_params
    state.cached_quantities["edge_label_computation_mode"] = dict(computation_mode)
    state.cached_quantities["edge_label_params"] = dict(label_params)


def compute_potential(
    state: GRC9V3State,
    *,
    evolution: Mapping[str, Any],
) -> None:
    """Compute node potential from scalar base conductance and coherence."""

    kappa_c = float(evolution.get("kappa_c", 1.0))
    selection = str(evolution.get("site_potential_selection", "quadratic"))
    params = evolution.get("site_potential_params", {"mu": 0.0, "scale": 1.0})
    if not isinstance(params, Mapping):
        raise TypeError("site_potential_params must be a mapping")
    potential: dict[NodeId, float] = {}

    for node_id in sorted(state.topology.iter_live_node_ids()):
        coherence_i = _coherence(state, node_id)
        interaction_term = 0.0
        for edge_id in sorted(state.topology.incident_edge_ids(node_id)):
            neighbor_id = _neighbor_for_edge(state, edge_id=edge_id, node_id=node_id)
            interaction_term += state.base_conductance.get(edge_id, 1.0) * (
                coherence_i - _coherence(state, neighbor_id)
            )
        potential[node_id] = (
            kappa_c * interaction_term
            - _site_potential_derivative(
                coherence=coherence_i,
                selection=selection,
                params=params,
            )
        )
    state.potential = potential


def compute_flux(
    state: GRC9V3State,
    *,
    evolution: Mapping[str, Any],
) -> None:
    """Compute antisymmetric occupied-port-pair flux."""

    eta = float(evolution.get("eta", 1.0))
    updated_port_edges: dict[EdgeId, PortEdge] = {}
    oriented_flux: dict[str, dict[str, float]] = {}
    for edge_id in sorted(state.topology.iter_live_edge_ids()):
        port_edge = state.port_edges[edge_id]
        potential_u = float(state.potential.get(port_edge.node_u, 0.0))
        potential_v = float(state.potential.get(port_edge.node_v, 0.0))
        conductance = float(state.base_conductance.get(edge_id, port_edge.conductance))
        flux_uv = -eta * conductance * (potential_u - potential_v)
        updated_port_edges[edge_id] = PortEdge(
            node_u=port_edge.node_u,
            port_u=port_edge.port_u,
            node_v=port_edge.node_v,
            port_v=port_edge.port_v,
            conductance=conductance,
            flux_uv=float(flux_uv),
        )
        oriented_flux[str(edge_id)] = {
            str(port_edge.node_u): float(flux_uv),
            str(port_edge.node_v): float(-flux_uv),
        }
    state.port_edges = updated_port_edges
    state.cached_quantities["oriented_flux"] = oriented_flux


def detect_flux_topology_identities(state: GRC9V3State) -> None:
    """Extract sinks and attraction basins from deterministic flux successors."""

    live_node_ids = tuple(sorted(state.topology.iter_live_node_ids()))
    successor_map: dict[NodeId, NodeId] = {}
    sinks: set[NodeId] = set()
    basins: dict[NodeId, set[NodeId]] = {}

    for node_id in live_node_ids:
        outgoing_candidates: list[tuple[float, NodeId, EdgeId]] = []
        positive_inflow = False
        max_outgoing = 0.0
        for edge_id in sorted(state.topology.incident_edge_ids(node_id)):
            neighbor_id = _neighbor_for_edge(state, edge_id=edge_id, node_id=node_id)
            outgoing_flux = _oriented_flux(state, edge_id=edge_id, node_id=node_id)
            incoming_flux = _oriented_flux(state, edge_id=edge_id, node_id=neighbor_id)
            if outgoing_flux > 0.0:
                outgoing_candidates.append((outgoing_flux, neighbor_id, edge_id))
            if incoming_flux > 0.0:
                positive_inflow = True
            max_outgoing = max(max_outgoing, outgoing_flux)
        if outgoing_candidates:
            outgoing_candidates.sort(key=lambda item: (-item[0], item[1], item[2]))
            successor_map[node_id] = outgoing_candidates[0][1]
        else:
            successor_map[node_id] = node_id
        if max_outgoing <= 0.0 and positive_inflow:
            sinks.add(node_id)

    for origin_node_id in live_node_ids:
        reached_sink = _reachable_sink(origin_node_id, successor_map, sinks)
        if reached_sink is not None:
            basins.setdefault(reached_sink, set()).add(origin_node_id)

    state.sink_set = sinks
    state.basins = basins
    state.cached_quantities["successor_map"] = {
        str(node_id): successor_map[node_id] for node_id in sorted(successor_map)
    }
    state.cached_quantities["flux_identity"] = {
        "sink_nodes": sorted(sinks),
        "basins": {
            str(node_id): sorted(members)
            for node_id, members in sorted(basins.items())
        },
        "successor_map": {
            str(node_id): successor_map[node_id] for node_id in sorted(successor_map)
        },
    }


def validate_geometric_basin_seeds(
    state: GRC9V3State,
    *,
    evolution: Mapping[str, Any],
) -> None:
    """Validate Eq. G7 basin seeds from row gradient and signed Hessian."""

    gradient_threshold = float(evolution.get("eps_gradient", 1e-3))
    hessian_threshold = float(evolution.get("eps_hessian", 1e-3))
    seed_nodes: set[NodeId] = set()
    gradient_norm_by_node: dict[NodeId, float] = {}
    min_signed_hessian_by_node: dict[NodeId, float] = {}

    for node_id in sorted(state.topology.iter_live_node_ids()):
        node_state = state.nodes.get(node_id)
        if node_state is None:
            continue
        gradient_norm = math.sqrt(
            sum(value * value for value in node_state.gradient_row_basis)
        )
        signed_hessian = list(node_state.signed_hessian_row_basis)
        min_signed = min(signed_hessian) if signed_hessian else float("-inf")
        gradient_norm_by_node[node_id] = float(gradient_norm)
        min_signed_hessian_by_node[node_id] = float(min_signed)
        if gradient_norm < gradient_threshold and min_signed > hessian_threshold:
            seed_nodes.add(node_id)

    validated_basin_ids: set[str | int] = set()
    basin_seed_nodes: dict[NodeId, list[NodeId]] = {}
    basin_id_by_node: dict[NodeId, str | int] = {}
    geometric_basins: dict[str | int, set[NodeId]] = {}

    for sink_node_id in sorted(state.basins):
        members = set(state.basins[sink_node_id])
        seeds = sorted(member for member in members if member in seed_nodes)
        basin_seed_nodes[sink_node_id] = seeds
        if len(seeds) == 1:
            basin_id: str | int = seeds[0]
            validated_basin_ids.add(basin_id)
        else:
            basin_id = sink_node_id
        geometric_basins[basin_id] = set(members)
        for member in sorted(members):
            basin_id_by_node[member] = basin_id

    for node_id in sorted(seed_nodes):
        if node_id not in basin_id_by_node:
            validated_basin_ids.add(node_id)
            geometric_basins[node_id] = {node_id}
            basin_id_by_node[node_id] = node_id

    for node_id in sorted(state.topology.iter_live_node_ids()):
        basin_id_by_node.setdefault(node_id, node_id)

    state.cached_quantities["geometric_identity"] = {
        "seed_nodes": sorted(seed_nodes),
        "gradient_norm_by_node": {
            str(node_id): gradient_norm_by_node[node_id]
            for node_id in sorted(gradient_norm_by_node)
        },
        "min_signed_hessian_by_node": {
            str(node_id): min_signed_hessian_by_node[node_id]
            for node_id in sorted(min_signed_hessian_by_node)
        },
        "validated_basin_ids": sorted(validated_basin_ids, key=str),
        "basin_seed_nodes": {
            str(sink_node_id): list(seeds)
            for sink_node_id, seeds in sorted(basin_seed_nodes.items())
        },
        "basin_id_by_node": {
            str(node_id): basin_id_by_node[node_id]
            for node_id in sorted(basin_id_by_node)
        },
        "geometric_basins": {
            str(basin_id): sorted(members)
            for basin_id, members in sorted(
                geometric_basins.items(),
                key=lambda item: str(item[0]),
            )
        },
    }


def compute_effective_basin_masses(state: GRC9V3State) -> None:
    """Compute Appendix G effective basin masses from current basin membership."""

    geometric_identity = state.cached_quantities.get("geometric_identity", {})
    geometric_basins = _geometric_basins_from_cache(geometric_identity)
    basin_id_by_node = _basin_id_by_node_from_cache(geometric_identity)

    if not geometric_basins:
        geometric_basins = {
            sink_node_id: set(members)
            for sink_node_id, members in sorted(state.basins.items())
        }
        basin_id_by_node = {
            member: sink_node_id
            for sink_node_id, members in sorted(
                geometric_basins.items(),
                key=lambda item: str(item[0]),
            )
            for member in members
        }

    live_node_ids = tuple(sorted(state.topology.iter_live_node_ids()))
    for node_id in live_node_ids:
        basin_id_by_node.setdefault(node_id, node_id)
        geometric_basins.setdefault(basin_id_by_node[node_id], {node_id})

    basin_mass_by_basin_id: dict[str, float] = {}
    basin_mass_by_node: dict[str, float] = {}
    representative_node_ids: set[NodeId] = set()

    for basin_id, members in sorted(
        geometric_basins.items(),
        key=lambda item: str(item[0]),
    ):
        live_members = {
            int(member) for member in members if int(member) in state.nodes
        }
        if not live_members:
            continue
        basin_mass = sum(_node_quadrature_mass(state, member) for member in live_members)
        basin_mass_by_basin_id[str(basin_id)] = float(basin_mass)
        for member in sorted(live_members):
            basin_mass_by_node[str(member)] = float(basin_mass)
        if isinstance(basin_id, int) and basin_id in state.nodes:
            representative_node_ids.add(basin_id)
        elif (
            isinstance(basin_id, str)
            and basin_id.isdigit()
            and int(basin_id) in state.nodes
        ):
            representative_node_ids.add(int(basin_id))

    for sink_node_id, members in sorted(state.basins.items()):
        live_members = {
            int(member) for member in members if int(member) in state.nodes
        }
        if not live_members:
            continue
        sink_mass = sum(_node_quadrature_mass(state, member) for member in live_members)
        basin_mass_by_basin_id.setdefault(str(sink_node_id), float(sink_mass))
        basin_mass_by_node[str(sink_node_id)] = float(sink_mass)
        if sink_node_id in state.nodes:
            representative_node_ids.add(sink_node_id)

    for node_id in live_node_ids:
        node_state = state.nodes.get(node_id)
        if node_state is None:
            continue
        if node_id in representative_node_ids:
            mass = basin_mass_by_node.get(
                str(node_id),
                _node_quadrature_mass(state, node_id),
            )
        else:
            mass = _node_quadrature_mass(state, node_id)
        node_state.basin_mass = float(mass)

    if isinstance(geometric_identity, Mapping):
        updated_geometric_identity = dict(geometric_identity)
    else:
        updated_geometric_identity = {}
    updated_geometric_identity["basin_mass_by_basin_id"] = {
        key: basin_mass_by_basin_id[key] for key in sorted(basin_mass_by_basin_id)
    }
    updated_geometric_identity["basin_mass_by_node"] = {
        key: basin_mass_by_node[key]
        for key in sorted(basin_mass_by_node, key=lambda value: int(value))
    }
    updated_geometric_identity["representative_basin_node_ids"] = sorted(
        representative_node_ids
    )
    updated_geometric_identity["basin_mass_source"] = "unit_measure_basin_membership"
    state.cached_quantities["geometric_identity"] = updated_geometric_identity

    flux_identity = state.cached_quantities.get("flux_identity")
    if isinstance(flux_identity, Mapping):
        updated_flux_identity = dict(flux_identity)
        updated_flux_identity["basin_mass_by_sink_id"] = {
            str(sink_node_id): float(
                sum(
                    _node_quadrature_mass(state, member)
                    for member in sorted(members)
                    if member in state.nodes
                )
            )
            for sink_node_id, members in sorted(state.basins.items())
        }
        updated_flux_identity["basin_mass_source"] = "unit_measure_basin_membership"
        state.cached_quantities["flux_identity"] = updated_flux_identity


def _selected_edge_labels(modes: Mapping[str, Any]) -> set[str]:
    selection = modes.get("edge_label_selection", "all")
    if selection == "all":
        return set(_ALLOWED_EDGE_LABELS)
    if isinstance(selection, str):
        raise ValueError("edge_label_selection must be 'all' or iterable")
    return {str(label) for label in selection}


def _geometric_length(state: GRC9V3State, edge_id: EdgeId) -> float:
    return max(1e-12, 1.0 / (_edge_conductance(state, edge_id) + 1e-12))


def _site_potential_derivative(
    *,
    coherence: float,
    selection: str,
    params: Mapping[str, Any],
) -> float:
    if selection == "quadratic":
        mu = float(params.get("mu", 0.0))
        scale = float(params.get("scale", 1.0))
        return 2.0 * scale * coherence + mu
    if selection == "linear":
        bias = float(params.get("bias", 0.0))
        scale = float(params.get("scale", 1.0))
        return scale + bias
    raise ValueError(f"unsupported site_potential_selection {selection!r}")


def _squared_vector_gap(left: list[float], right: list[float]) -> float:
    dimension = max(len(left), len(right))
    left_padded = list(left[:dimension])
    right_padded = list(right[:dimension])
    while len(left_padded) < dimension:
        left_padded.append(0.0)
    while len(right_padded) < dimension:
        right_padded.append(0.0)
    return float(
        sum((left_padded[index] - right_padded[index]) ** 2 for index in range(dimension))
    )


def _reachable_sink(
    origin_node_id: NodeId,
    successor_map: Mapping[NodeId, NodeId],
    sinks: set[NodeId],
) -> NodeId | None:
    visited: set[NodeId] = set()
    current = origin_node_id
    while current not in visited:
        visited.add(current)
        if current in sinks:
            return current
        next_node = successor_map.get(current)
        if next_node is None or next_node == current:
            return current if current in sinks else None
        current = next_node
    return None


def _resolve_hessian_sign(
    state: GRC9V3State,
    *,
    selected_hessian_by_node: Mapping[NodeId, list[float]],
    gradient_by_node: Mapping[NodeId, list[float]],
    gradient_threshold: float,
    hessian_threshold: float,
) -> int:
    cached = state.cached_quantities.get("hessian_sign")
    if isinstance(cached, int) and not isinstance(cached, bool) and cached in (-1, 1):
        return int(cached)

    candidate_node_ids = (
        tuple(sorted(state.sink_set))
        if state.sink_set
        else tuple(sorted(state.topology.iter_live_node_ids()))
    )
    scores: dict[int, tuple[int, float, tuple[int, ...]]] = {}
    for sign in (1, -1):
        satisfied: list[int] = []
        margin = 0.0
        for node_id in candidate_node_ids:
            gradient = gradient_by_node.get(node_id, [0.0] * _ROW_COUNT)
            gradient_norm = math.sqrt(sum(value * value for value in gradient))
            if gradient_norm > gradient_threshold:
                continue
            signed_values = [
                sign * value
                for value in selected_hessian_by_node.get(node_id, [0.0] * _ROW_COUNT)
            ]
            if signed_values and min(signed_values) > hessian_threshold:
                satisfied.append(int(node_id))
                margin += min(signed_values)
        scores[sign] = (len(satisfied), margin, tuple(sorted(satisfied)))

    if scores[-1] > scores[1]:
        return -1
    return 1


def _row_edges_by_node(state: GRC9V3State, node_id: NodeId) -> dict[int, list[EdgeId]]:
    row_edges: dict[int, list[EdgeId]] = {1: [], 2: [], 3: []}
    for edge_id in sorted(state.topology.incident_edge_ids(node_id)):
        row, _ = port_to_rc(_local_port_id(state, edge_id=edge_id, node_id=node_id))
        row_edges[row].append(edge_id)
    return row_edges


def _weighted_row_difference(
    state: GRC9V3State,
    *,
    node_id: NodeId,
    edge_ids: tuple[EdgeId, ...] | list[EdgeId],
) -> float:
    total_weight = 0.0
    weighted_difference = 0.0
    coherence_i = _coherence(state, node_id)
    for edge_id in edge_ids:
        conductance = _edge_conductance(state, edge_id)
        neighbor_id = _neighbor_for_edge(state, edge_id=edge_id, node_id=node_id)
        total_weight += conductance
        weighted_difference += conductance * (_coherence(state, neighbor_id) - coherence_i)
    if total_weight <= 0.0:
        return 0.0
    return float(weighted_difference / total_weight)


def _row_squared_mismatch_sum(
    state: GRC9V3State,
    *,
    node_id: NodeId,
    edge_ids: tuple[EdgeId, ...] | list[EdgeId],
) -> float:
    mismatch_sum = 0.0
    coherence_i = _coherence(state, node_id)
    for edge_id in edge_ids:
        conductance = _edge_conductance(state, edge_id)
        neighbor_id = _neighbor_for_edge(state, edge_id=edge_id, node_id=node_id)
        coherence_delta = _coherence(state, neighbor_id) - coherence_i
        mismatch_sum += conductance * (coherence_delta**2)
    return float(mismatch_sum)


def _coherence(state: GRC9V3State, node_id: NodeId) -> float:
    node_state = state.nodes.get(node_id)
    if node_state is not None:
        return float(node_state.coherence)
    payload = state.topology.node_payload(node_id)
    raw_value = payload.get("coherence", 0.0)
    return float(raw_value)


def _node_quadrature_mass(state: GRC9V3State, node_id: NodeId) -> float:
    return float(_quadrature_weight(state, node_id) * _coherence(state, node_id))


def _quadrature_weight(state: GRC9V3State, node_id: NodeId) -> float:
    payload = state.topology.node_payload(node_id)
    for key in ("quadrature_weight", "mu_i", "node_measure"):
        if key not in payload:
            continue
        try:
            value = float(payload[key])
        except (TypeError, ValueError):
            continue
        if math.isfinite(value) and value > 0.0:
            return value
    return 1.0


def _geometric_basins_from_cache(value: Any) -> dict[str | int, set[NodeId]]:
    if not isinstance(value, Mapping):
        return {}
    raw_basins = value.get("geometric_basins", {})
    if not isinstance(raw_basins, Mapping):
        return {}
    basins: dict[str | int, set[NodeId]] = {}
    for basin_id, raw_members in raw_basins.items():
        if not isinstance(raw_members, (tuple, list, set)):
            continue
        normalized_basin_id: str | int
        if isinstance(basin_id, int):
            normalized_basin_id = basin_id
        elif isinstance(basin_id, str) and basin_id.isdigit():
            normalized_basin_id = int(basin_id)
        else:
            normalized_basin_id = str(basin_id)
        members: set[NodeId] = set()
        for raw_member in raw_members:
            try:
                members.add(int(raw_member))
            except (TypeError, ValueError):
                continue
        if members:
            basins[normalized_basin_id] = members
    return basins


def _basin_id_by_node_from_cache(value: Any) -> dict[NodeId, str | int]:
    if not isinstance(value, Mapping):
        return {}
    raw_mapping = value.get("basin_id_by_node", {})
    if not isinstance(raw_mapping, Mapping):
        return {}
    basin_id_by_node: dict[NodeId, str | int] = {}
    for raw_node_id, raw_basin_id in raw_mapping.items():
        try:
            node_id = int(raw_node_id)
        except (TypeError, ValueError):
            continue
        if isinstance(raw_basin_id, int):
            basin_id_by_node[node_id] = raw_basin_id
        elif isinstance(raw_basin_id, str) and raw_basin_id.isdigit():
            basin_id_by_node[node_id] = int(raw_basin_id)
        else:
            basin_id_by_node[node_id] = str(raw_basin_id)
    return basin_id_by_node


def _edge_conductance(state: GRC9V3State, edge_id: EdgeId) -> float:
    if edge_id in state.base_conductance:
        return float(state.base_conductance[edge_id])
    return float(state.port_edges[edge_id].conductance)


def _neighbor_for_edge(
    state: GRC9V3State,
    *,
    edge_id: EdgeId,
    node_id: NodeId,
) -> NodeId:
    endpoint_a, endpoint_b = state.topology.edge_ports(edge_id)
    if endpoint_a[0] == node_id:
        return endpoint_b[0]
    if endpoint_b[0] == node_id:
        return endpoint_a[0]
    raise ValueError("edge is not incident to node_id")


def _local_port_id(
    state: GRC9V3State,
    *,
    edge_id: EdgeId,
    node_id: NodeId,
) -> int:
    endpoint_a, endpoint_b = state.topology.edge_ports(edge_id)
    if endpoint_a[0] == node_id:
        return slot_to_port_id(endpoint_a[1])
    if endpoint_b[0] == node_id:
        return slot_to_port_id(endpoint_b[1])
    raise ValueError("edge is not incident to node_id")


def _oriented_flux(
    state: GRC9V3State,
    *,
    edge_id: EdgeId,
    node_id: NodeId,
) -> float:
    port_edge = state.port_edges[edge_id]
    if port_edge.node_u == node_id:
        return float(port_edge.flux_uv)
    if port_edge.node_v == node_id:
        return float(-port_edge.flux_uv)
    raise ValueError("edge is not incident to node_id")


def _matrix_diagonal(matrix: list[list[float]]) -> list[float]:
    return [
        float(matrix[index][index]) if index < len(matrix) and index < len(matrix[index]) else 0.0
        for index in range(_ROW_COUNT)
    ]


def _pad_row_vector(values: list[float]) -> list[float]:
    padded = list(values[:_ROW_COUNT])
    while len(padded) < _ROW_COUNT:
        padded.append(0.0)
    return [float(value) for value in padded]


def _zero_matrix() -> list[list[float]]:
    return [[0.0 for _ in range(_ROW_COUNT)] for _ in range(_ROW_COUNT)]


__all__ = [
    "compute_hybrid_node_tensors",
    "compute_base_conductance",
    "compute_edge_labels",
    "compute_effective_basin_masses",
    "compute_flux",
    "compute_net_flux_summary_rows",
    "compute_potential",
    "compute_row_basis_gradient",
    "compute_row_mismatch_sums",
    "compute_unsigned_row_basis_hessian",
    "compute_weighted_least_squares_hessian_rows",
    "detect_flux_topology_identities",
    "rebuild_grc9v3_identity_state",
    "rebuild_grc9v3_differential_state",
    "rebuild_grc9v3_transport_state",
    "validate_geometric_basin_seeds",
]
