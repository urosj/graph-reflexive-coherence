"""Execute GRV2 bounded branch search and strong-branch certification."""

from __future__ import annotations

import argparse
from copy import deepcopy
from itertools import product
import json
import math
from pathlib import Path
import subprocess
import sys
from typing import Any, Callable, Iterable

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

SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from pygrc.models import GRC9V3  # noqa: E402

from branch_continuation import BranchCandidate, select_candidate  # noqa: E402
from gate_receipts import (  # noqa: E402
    finalize_receipt,
    prerequisite_is_authorized,
    validate_acceptance_anchor,
    validate_receipt,
)


COMMAND = (
    ".venv/bin/python "
    "experiments/2026-08-B1-GR-grc9v3-continuation-readback-verification/"
    "scripts/run_all.py --gate GRV2"
)
EXPERIMENT_RELATIVE = repo_relative(EXPERIMENT_ROOT)
GRV1_RESULT_REVISION = "3c43918b1051389c5943ae28f505e585a542c621"
GRV1_RECEIPT_SHA256 = (
    "9535c80100c6813b69a327cfa80f0180f2288ee7e87e6e550c3168261353855a"
)
GRV1_ACCEPTANCE_COMMIT = "bc12787e885b9dcc7d939c98a7e2e3ea84f2d213"


def mapping(values: dict[Any, Any]) -> dict[str, Any]:
    return {str(key): values[key] for key in sorted(values)}


def topology_edges(fixture_id: str) -> list[tuple[int, int, int, int]]:
    if fixture_id in {"F1", "F2"}:
        return [(0, 1, 1, 1)]
    if fixture_id == "F3":
        return [(0, 1, 1, 1), (1, 2, 2, 1), (2, 0, 2, 2)]
    raise ValueError(f"unsupported fixture {fixture_id}")


def build_state(
    fixture_id: str,
    coherence: Iterable[float],
    *,
    port_map: dict[int, int] | None = None,
) -> dict[str, Any]:
    values = [float(value) for value in coherence]
    edges = topology_edges(fixture_id)
    ports = port_map or {}
    topology_edge_rows = []
    port_edge_rows: dict[str, Any] = {}
    incidence = {str(node_id): [] for node_id in range(len(values))}
    for edge_id, (node_u, node_v, port_u_raw, port_v_raw) in enumerate(edges):
        port_u = int(ports.get(port_u_raw, port_u_raw))
        port_v = int(ports.get(port_v_raw, port_v_raw))
        endpoint_u = (node_u, port_u)
        endpoint_v = (node_v, port_v)
        if endpoint_v < endpoint_u:
            endpoint_u, endpoint_v = endpoint_v, endpoint_u
        node_u, port_u = endpoint_u
        node_v, port_v = endpoint_v
        topology_edge_rows.append(
            {
                "edge_id": edge_id,
                "endpoint_a": {"node_id": node_u, "slot": port_u - 1},
                "endpoint_b": {"node_id": node_v, "slot": port_v - 1},
                "payload": {},
            }
        )
        incidence[str(node_u)].append(edge_id)
        incidence[str(node_v)].append(edge_id)
        port_edge_rows[str(edge_id)] = {
            "node_u": node_u,
            "port_u": port_u,
            "node_v": node_v,
            "port_v": port_v,
            "conductance": 1.0,
            "flux_uv": 0.0,
        }
    return {
        "topology": {
            "nodes": [
                {"node_id": node_id, "payload": {}}
                for node_id in range(len(values))
            ],
            "edges": topology_edge_rows,
            "incidence": incidence,
            "port_structure": {},
        },
        "nodes": {
            str(node_id): {
                "coherence": value,
                "basin_mass": value,
                "basin_id": node_id,
            }
            for node_id, value in enumerate(values)
        },
        "port_edges": port_edge_rows,
        "budget_target": float(sum(values)),
    }


def build_params(scale: float, dt: float, eta: float, seed: int) -> dict[str, Any]:
    return {
        "dt": float(dt),
        "evolution": {
            "alpha": 1e-12,
            "beta": 1e-12,
            "gamma": 1e-12,
            "eta": float(eta),
            "kappa_c": 1.0,
            "v0": 1.0,
            "rho": 1.0,
            "eps_tau": 1e-12,
            "site_potential_selection": "quadratic",
            "site_potential_params": {"mu": 0.0, "scale": float(scale)},
            "eps_gradient": 0.5,
            "eps_hessian": 0.1,
            "eps_spark": 1e-3,
            "lambda_birth": 0.0,
            "rng_seed": int(seed),
        },
        "constitutive_semantic_modes": {
            "frame_mode": "fixed_port_chart",
            "boundary_mode": "prune",
            "curvature_backend": "none",
            "choice_backend": "disabled",
            "quadrature_mode": "unit_measure",
            "budget_correction_method": "simplex_projection",
            "spark_lane": "current_hybrid_signed_hessian",
            "spark_signed_crossing": False,
        },
    }


def coherence_vector(model: GRC9V3) -> list[float]:
    state = model.get_state()
    return [
        float(state.nodes[node_id].coherence)
        for node_id in sorted(state.topology.iter_live_node_ids())
    ]


def block_projection(model: GRC9V3) -> dict[str, Any]:
    state = model.get_state()
    return {
        "C": mapping(
            {node_id: state.nodes[node_id].coherence for node_id in state.nodes}
        ),
        "W": {
            "base_conductance": mapping(state.base_conductance),
            "port_conductance": mapping(
                {
                    edge_id: state.port_edges[edge_id].conductance
                    for edge_id in state.port_edges
                }
            ),
        },
        "J": mapping(
            {
                edge_id: state.port_edges[edge_id].flux_uv
                for edge_id in state.port_edges
            }
        ),
        "Phi": mapping(state.potential),
        "G": {
            "gradient_row_basis": mapping(
                {
                    node_id: list(state.nodes[node_id].gradient_row_basis)
                    for node_id in state.nodes
                }
            ),
            "signed_hessian_row_basis": mapping(
                {
                    node_id: list(state.nodes[node_id].signed_hessian_row_basis)
                    for node_id in state.nodes
                }
            ),
            "net_flux_summary": mapping(
                {
                    node_id: list(state.nodes[node_id].net_flux_summary)
                    for node_id in state.nodes
                }
            ),
            "geometric_length": mapping(state.geometric_length),
            "temporal_delay": mapping(state.temporal_delay),
            "flux_coupling": mapping(state.flux_coupling),
            "hybrid_node_tensors": deepcopy(
                state.cached_quantities.get("hybrid_node_tensors", {})
            ),
        },
        "identity": {
            "sink_set": sorted(state.sink_set),
            "basins": {
                str(sink): sorted(members)
                for sink, members in sorted(state.basins.items())
            },
            "node_basin_fields": mapping(
                {
                    node_id: {
                        "basin_mass": state.nodes[node_id].basin_mass,
                        "basin_id": state.nodes[node_id].basin_id,
                        "parent_id": state.nodes[node_id].parent_id,
                        "depth": state.nodes[node_id].depth,
                    }
                    for node_id in state.nodes
                }
            ),
            "hierarchy": mapping(state.hierarchy),
            "flux_identity": deepcopy(
                state.cached_quantities.get("flux_identity", {})
            ),
            "geometric_identity": deepcopy(
                state.cached_quantities.get("geometric_identity", {})
            ),
            "successor_map": deepcopy(
                state.cached_quantities.get("successor_map", {})
            ),
        },
        "budget": {
            "budget_target": state.budget_target,
            "coherence_sum": sum(
                node.coherence for node in state.nodes.values()
            ),
            "remainder": state.remainder,
        },
        "topology": {
            "nodes": list(sorted(state.topology.iter_live_node_ids())),
            "edges": list(sorted(state.topology.iter_live_edge_ids())),
            "edge_ports": {
                str(edge_id): [list(endpoint) for endpoint in state.topology.edge_ports(edge_id)]
                for edge_id in sorted(state.topology.iter_live_edge_ids())
            },
        },
    }


def _differences(left: Any, right: Any) -> tuple[list[float], bool]:
    if isinstance(left, bool) or isinstance(right, bool):
        return ([], left == right)
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return ([float(right) - float(left)], True)
    if isinstance(left, dict) and isinstance(right, dict):
        if set(left) != set(right):
            return ([], False)
        numbers: list[float] = []
        categorical = True
        for key in sorted(left):
            child_numbers, child_categorical = _differences(left[key], right[key])
            numbers.extend(child_numbers)
            categorical = categorical and child_categorical
        return (numbers, categorical)
    if isinstance(left, (list, tuple)) and isinstance(right, (list, tuple)):
        if len(left) != len(right):
            return ([], False)
        numbers = []
        categorical = True
        for left_item, right_item in zip(left, right, strict=True):
            child_numbers, child_categorical = _differences(left_item, right_item)
            numbers.extend(child_numbers)
            categorical = categorical and child_categorical
        return (numbers, categorical)
    return ([], left == right)


def residual_metrics(reference: Any, observed: Any) -> dict[str, Any]:
    differences, categorical_equal = _differences(reference, observed)
    absolute = [abs(value) for value in differences]
    linf = max(absolute, default=0.0)
    l2 = math.sqrt(sum(value * value for value in differences))
    reference_values = numeric_values(reference)
    reference_l2 = math.sqrt(sum(value * value for value in reference_values))
    return {
        "l_inf": float(linf),
        "l_2": float(l2),
        "relative": float(l2 / max(1.0, reference_l2)),
        "categorical_equal": categorical_equal,
        "numeric_component_count": len(differences),
    }


def numeric_values(value: Any) -> list[float]:
    if isinstance(value, bool):
        return []
    if isinstance(value, (int, float)):
        return [float(value)]
    if isinstance(value, dict):
        result: list[float] = []
        for key in sorted(value):
            result.extend(numeric_values(value[key]))
        return result
    if isinstance(value, (list, tuple)):
        result = []
        for child in value:
            result.extend(numeric_values(child))
        return result
    return []


def max_block_l_inf(rows: dict[str, dict[str, Any]]) -> float:
    return max((float(row["l_inf"]) for row in rows.values()), default=0.0)


def canonicalize_branch(model: GRC9V3) -> dict[str, Any]:
    initial_events = len(model.get_state().event_log)
    model.rebuild_differential_state()
    model.rebuild_transport_state()
    model.rebuild_differential_state()
    model.rebuild_identity_state()
    spark_events = model.apply_hybrid_sparks()
    choice_events = model.rebuild_choice_state()
    growth_events = model.apply_growth()
    model.apply_boundary_behavior()
    pre_continuity = block_projection(model)
    model.apply_continuity()
    post_continuity = block_projection(model)
    pre_budget_coherence = coherence_vector(model)
    budget_summary = model.enforce_quadrature_budget()
    post_budget_coherence = coherence_vector(model)
    model.rebuild_differential_state()
    model.rebuild_transport_state()
    model.rebuild_differential_state()
    model.rebuild_identity_state()
    model.refresh_coarse_cache()
    return {
        "pre_continuity": pre_continuity,
        "post_continuity_pre_budget": post_continuity,
        "budget_correction_vector": [
            after - before
            for before, after in zip(
                pre_budget_coherence, post_budget_coherence, strict=True
            )
        ],
        "budget_summary": budget_summary,
        "events": [
            event.kind for event in [*spark_events, *choice_events, *growth_events]
        ],
        "event_log_delta": len(model.get_state().event_log) - initial_events,
    }


def execute_staged_replay(model: GRC9V3) -> dict[str, Any]:
    reference = block_projection(model)
    stages: list[dict[str, Any]] = []

    def capture(name: str, operation: Callable[[], Any]) -> Any:
        result = operation()
        observed = block_projection(model)
        block_rows = {
            block: residual_metrics(reference[block], observed[block])
            for block in ("C", "W", "J", "Phi", "G", "identity", "budget")
        }
        stages.append(
            {
                "stage": name,
                "block_residuals": block_rows,
                "maximum_block_l_inf": max_block_l_inf(block_rows),
                "all_categorical_equal": all(
                    bool(row["categorical_equal"]) for row in block_rows.values()
                ),
                "state_sha256": semantic_digest(observed),
            }
        )
        return result

    initial_event_count = len(model.get_state().event_log)
    topology_before = reference["topology"]
    capture("initial_differential_reconstruction", model.rebuild_differential_state)
    capture("first_transport_reconstruction", model.rebuild_transport_state)
    capture("post_flux_differential_reconstruction", model.rebuild_differential_state)
    capture("identity_reconstruction", model.rebuild_identity_state)
    spark_events = capture("hybrid_spark_stages", model.apply_hybrid_sparks)
    choice_events = capture("choice_state_reconstruction", model.rebuild_choice_state)
    growth_events = capture("growth_stage", model.apply_growth)
    capture("boundary_stage", model.apply_boundary_behavior)
    pre_continuity = block_projection(model)
    capture("continuity_stage", model.apply_continuity)
    post_continuity = block_projection(model)
    pre_budget_coherence = coherence_vector(model)
    budget_summary = capture("budget_stage", model.enforce_quadrature_budget)
    post_budget = block_projection(model)
    post_budget_coherence = coherence_vector(model)
    capture("final_differential_reconstruction_1", model.rebuild_differential_state)
    capture("final_transport_reconstruction", model.rebuild_transport_state)
    capture("final_differential_reconstruction_2", model.rebuild_differential_state)
    capture("final_identity_reconstruction", model.rebuild_identity_state)
    final_refresh = block_projection(model)
    capture("coarse_cache_refresh", model.refresh_coarse_cache)
    topology_after = block_projection(model)["topology"]
    correction = [
        after - before
        for before, after in zip(
            pre_budget_coherence, post_budget_coherence, strict=True
        )
    ]
    return {
        "reference_state_sha256": semantic_digest(reference),
        "stages": stages,
        "maximum_internal_stage_l_inf": max(
            (float(stage["maximum_block_l_inf"]) for stage in stages),
            default=0.0,
        ),
        "all_stage_categories_equal": all(
            bool(stage["all_categorical_equal"]) for stage in stages
        ),
        "pre_continuity_state": pre_continuity,
        "post_continuity_pre_budget_state": post_continuity,
        "budget_correction_vector": correction,
        "budget_correction_l_inf": max((abs(value) for value in correction), default=0.0),
        "budget_summary": budget_summary,
        "post_budget_state": post_budget,
        "final_refresh_state": final_refresh,
        "events": [event.kind for event in [*spark_events, *choice_events, *growth_events]],
        "event_log_delta": len(model.get_state().event_log) - initial_event_count,
        "topology_before": topology_before,
        "topology_after": topology_after,
    }


def one_step_coherence(
    fixture_id: str,
    coherence: list[float],
    params: dict[str, Any],
) -> tuple[list[float], list[str], bool]:
    model = GRC9V3.from_state(build_state(fixture_id, coherence), params)
    topology_before = block_projection(model)["topology"]
    result = model.step()
    topology_after = block_projection(model)["topology"]
    return (
        coherence_vector(model),
        [event.kind for event in result.events],
        topology_before == topology_after,
    )


def reduced_step_residual(
    fixture_id: str,
    coordinates: np.ndarray,
    total: float,
    params: dict[str, Any],
) -> tuple[np.ndarray, list[float], list[str], bool]:
    coherence = [float(value) for value in coordinates]
    coherence.append(float(total - float(np.sum(coordinates))))
    after, events, fixed_topology = one_step_coherence(fixture_id, coherence, params)
    full_residual = np.asarray(after, dtype=float) - np.asarray(coherence, dtype=float)
    return full_residual[:-1], coherence, events, fixed_topology


def solve_seed(
    fixture_id: str,
    seed_values: list[float],
    params: dict[str, Any],
    config: dict[str, Any],
) -> dict[str, Any]:
    solver = config["solver"]
    total = float(sum(seed_values))
    coordinates = np.asarray(seed_values[:-1], dtype=float)
    tolerance = float(solver["root_l_inf_tolerance"])
    finite_step = float(solver["finite_difference_step"])
    minimum_positive = float(solver["minimum_positive_coherence"])
    minimum_factor = float(solver["minimum_backtracking_factor"])
    maximum_iterations = int(solver["maximum_iterations"])
    history: list[dict[str, Any]] = []
    status = "maximum_iterations_reached"
    final_coherence = list(seed_values)
    final_events: list[str] = []
    final_fixed_topology = True

    for iteration in range(maximum_iterations + 1):
        residual, coherence, events, fixed_topology = reduced_step_residual(
            fixture_id, coordinates, total, params
        )
        norm = float(np.max(np.abs(residual))) if residual.size else 0.0
        history.append(
            {
                "iteration": iteration,
                "coherence": coherence,
                "reduced_residual_l_inf": norm,
            }
        )
        final_coherence = coherence
        final_events = events
        final_fixed_topology = fixed_topology
        if events or not fixed_topology:
            status = "event_or_topology_boundary_crossed"
            break
        if min(coherence) <= minimum_positive:
            status = "positivity_boundary_crossed"
            break
        if norm <= tolerance:
            status = "converged"
            break
        if iteration == maximum_iterations:
            break

        jacobian = np.zeros((len(coordinates), len(coordinates)), dtype=float)
        valid_jacobian = True
        for column in range(len(coordinates)):
            plus = coordinates.copy()
            minus = coordinates.copy()
            plus[column] += finite_step
            minus[column] -= finite_step
            plus_residual, plus_coherence, plus_events, plus_fixed = reduced_step_residual(
                fixture_id, plus, total, params
            )
            minus_residual, minus_coherence, minus_events, minus_fixed = reduced_step_residual(
                fixture_id, minus, total, params
            )
            if (
                min(plus_coherence) <= minimum_positive
                or min(minus_coherence) <= minimum_positive
                or plus_events
                or minus_events
                or not plus_fixed
                or not minus_fixed
            ):
                valid_jacobian = False
                break
            jacobian[:, column] = (plus_residual - minus_residual) / (2.0 * finite_step)
        if not valid_jacobian:
            status = "finite_difference_boundary_crossed"
            break
        try:
            update = np.linalg.lstsq(jacobian, -residual, rcond=None)[0]
        except np.linalg.LinAlgError:
            status = "linear_solve_failed"
            break
        if float(np.linalg.norm(update)) == 0.0:
            status = "singular_stationary_search"
            break

        factor = 1.0
        accepted_update = False
        while factor >= minimum_factor:
            trial = coordinates + factor * update
            trial_residual, trial_coherence, trial_events, trial_fixed = reduced_step_residual(
                fixture_id, trial, total, params
            )
            trial_norm = (
                float(np.max(np.abs(trial_residual)))
                if trial_residual.size
                else 0.0
            )
            if (
                min(trial_coherence) > minimum_positive
                and not trial_events
                and trial_fixed
                and trial_norm < norm
            ):
                coordinates = trial
                accepted_update = True
                break
            factor *= 0.5
        if not accepted_update:
            status = "backtracking_failed"
            break

    final_after, final_events, final_fixed_topology = one_step_coherence(
        fixture_id, final_coherence, params
    )
    full_residual = [
        after - before
        for before, after in zip(final_coherence, final_after, strict=True)
    ]
    return {
        "solver": "bounded_damped_newton_reduced_zero_sum_coordinates",
        "initial_seed": list(seed_values),
        "total_coherence": total,
        "final_coherence": final_coherence,
        "iterations": len(history) - 1,
        "convergence_history": history,
        "full_step_coherence_residual": full_residual,
        "full_step_coherence_l_inf": max(
            (abs(value) for value in full_residual), default=0.0
        ),
        "events": final_events,
        "fixed_topology": final_fixed_topology,
        "status": status,
    }


def stage_passes(
    stage_trace: dict[str, Any],
    *,
    absolute_tolerance: float,
    relative_tolerance: float,
    budget_tolerance: float,
) -> bool:
    return bool(
        stage_trace["maximum_internal_stage_l_inf"] <= absolute_tolerance
        and stage_trace["all_stage_categories_equal"]
        and stage_trace["budget_correction_l_inf"] <= budget_tolerance
        and all(
            float(block["relative"]) <= relative_tolerance
            for stage in stage_trace["stages"]
            for block in stage["block_residuals"].values()
        )
    )


def classify_branch(
    full_residual: dict[str, Any],
    stage_trace: dict[str, Any],
    *,
    absolute_tolerance: float,
    relative_tolerance: float,
    budget_tolerance: float,
    no_events: bool,
    fixed_topology: bool,
) -> str:
    full_pass = bool(
        full_residual["l_inf"] <= absolute_tolerance
        and full_residual["relative"] <= relative_tolerance
        and full_residual["categorical_equal"]
        and no_events
        and fixed_topology
    )
    internal_pass = stage_passes(
        stage_trace,
        absolute_tolerance=absolute_tolerance,
        relative_tolerance=relative_tolerance,
        budget_tolerance=budget_tolerance,
    )
    if full_pass and internal_pass:
        return "provisional_physical_strong_branch"
    if full_pass:
        return "step_boundary_only_fixed_point"
    if internal_pass:
        return "projection_supported_fixed_point"
    return "rejected_not_a_strong_fixed_branch"


def boundary_distances(model: GRC9V3, config: dict[str, Any]) -> dict[str, Any]:
    state = model.get_state()
    certification = config["certification"]
    conductances = list(state.base_conductance.values())
    max_degree = max(
        (
            len(tuple(state.topology.incident_edge_ids(node_id)))
            for node_id in state.topology.iter_live_node_ids()
        ),
        default=0,
    )
    gradients = [
        math.sqrt(sum(value * value for value in node.gradient_row_basis))
        for node in state.nodes.values()
    ]
    hessians = [
        min(node.signed_hessian_row_basis)
        for node in state.nodes.values()
        if node.signed_hessian_row_basis
    ]
    currents = [abs(edge.flux_uv) for edge in state.port_edges.values()]
    return {
        "positivity_margin": min(node.coherence for node in state.nodes.values()),
        "conductance_floor": certification["conductance_floor"],
        "conductance_floor_margin": min(conductances)
        - float(certification["conductance_floor"]),
        "spark_saturation_degree_margin": 9 - max_degree,
        "spark_gradient_threshold": float(model.get_params().evolution["eps_gradient"]),
        "minimum_gradient_threshold_distance": min(
            (
                abs(
                    value
                    - float(model.get_params().evolution["eps_gradient"])
                )
                for value in gradients
            ),
            default=0.0,
        ),
        "spark_hessian_threshold": float(model.get_params().evolution["eps_spark"]),
        "minimum_hessian_threshold_distance": min(
            (
                abs(value - float(model.get_params().evolution["eps_spark"]))
                for value in hessians
            ),
            default=0.0,
        ),
        "spark_candidate_count": len(model.detect_hybrid_spark_candidates()),
        "basin_sink_zero_flux_boundary_distance": min(currents, default=0.0),
        "basin_sink_boundary_status": "on_zero_flux_identity_boundary",
        "growth_lambda_birth": float(model.get_params().evolution["lambda_birth"]),
        "growth_status": "disabled_by_declared_zero_lambda_birth",
        "choice_status": "disabled_by_declared_backend",
        "boundary_action_status": "prune_noop",
        "grv3_smooth_stratum_admission": "pending_due_to_zero_flux_identity_boundary",
    }


def certify_branch(
    fixture_id: str,
    coherence: list[float],
    params: dict[str, Any],
    config: dict[str, Any],
    *,
    port_map: dict[int, int] | None = None,
) -> tuple[GRC9V3, dict[str, Any]]:
    model = GRC9V3.from_state(
        build_state(fixture_id, coherence, port_map=port_map), params
    )
    canonicalization = canonicalize_branch(model)
    reference = block_projection(model)
    staged = GRC9V3.from_state(deepcopy(model.get_state()), params)
    stage_trace = execute_staged_replay(staged)
    stepped = GRC9V3.from_state(deepcopy(model.get_state()), params)
    topology_before = block_projection(stepped)["topology"]
    initial_event_count = len(stepped.get_state().event_log)
    result = stepped.step()
    topology_after = block_projection(stepped)["topology"]
    observed = block_projection(stepped)
    full_residual = residual_metrics(reference, observed)
    full_residual["per_block"] = {
        block: residual_metrics(reference[block], observed[block])
        for block in ("C", "W", "J", "Phi", "G", "identity", "budget")
    }
    analytic = fixture_id == "F1"
    certification = config["certification"]
    absolute_tolerance = float(
        certification[
            "analytic_absolute_l_inf_tolerance"
            if analytic
            else "numerical_absolute_l_inf_tolerance"
        ]
    )
    relative_tolerance = float(certification["relative_residual_tolerance"])
    budget_tolerance = float(
        certification["budget_correction_l_inf_tolerance"]
    )
    no_events = bool(
        not canonicalization["events"]
        and canonicalization["event_log_delta"] == 0
        and not stage_trace["events"]
        and stage_trace["event_log_delta"] == 0
        and not result.events
        and len(stepped.get_state().event_log) == initial_event_count
    )
    fixed_topology = topology_before == topology_after
    branch_class = classify_branch(
        full_residual,
        stage_trace,
        absolute_tolerance=absolute_tolerance,
        relative_tolerance=relative_tolerance,
        budget_tolerance=budget_tolerance,
        no_events=no_events,
        fixed_topology=fixed_topology,
    )
    return model, {
        "canonicalization": canonicalization,
        "full_step_residual": full_residual,
        "internal_stage_residuals": stage_trace,
        "event_and_topology_assertions": {
            "canonicalization_no_events": not canonicalization["events"]
            and canonicalization["event_log_delta"] == 0,
            "staged_replay_no_events": not stage_trace["events"]
            and stage_trace["event_log_delta"] == 0,
            "full_step_no_events": not result.events,
            "fixed_topology": fixed_topology,
            "topology_before": topology_before,
            "topology_after": topology_after,
        },
        "declared_tolerances": {
            "absolute_l_inf": absolute_tolerance,
            "relative": relative_tolerance,
            "budget_correction_l_inf": budget_tolerance,
        },
        "branch_class": branch_class,
        "distance_from_non_smooth_boundaries": boundary_distances(model, config),
    }


def parameter_rows(config: dict[str, Any]) -> list[dict[str, float]]:
    grid = config["parameter_grid"]
    return [
        {"site_potential_scale": float(scale), "dt": float(dt), "eta": float(eta)}
        for scale, dt, eta in product(
            grid["site_potential_scales"], grid["dt_values"], grid["eta_values"]
        )
    ]


def search_space_size(config: dict[str, Any], fixture_id: str) -> int:
    return len(parameter_rows(config)) * len(
        config["fixture_searches"][fixture_id]["coherence_seeds"]
    )


def assert_search_contract(config: dict[str, Any]) -> None:
    budget = int(config["search_budget_per_family"])
    for fixture_id in config["candidate_fixtures"]:
        size = search_space_size(config, fixture_id)
        if size > budget:
            raise ValueError(
                f"{fixture_id} search size {size} exceeds preregistered budget {budget}"
            )
    if config["residual_norm"] != (
        "full_step_and_internal_stage_block_norms_on_admitted_physical_projection"
    ):
        raise ValueError("GRV2 requires the frozen strong residual")


def orbit_id(fixture_id: str, coherence: list[float], parameter_hash: str) -> str:
    normalized = {
        "fixture_id": fixture_id,
        "sorted_coherence": sorted(round(value, 12) for value in coherence),
        "parameter_hash": parameter_hash,
    }
    return f"orbit-{semantic_digest(normalized)[:16]}"


def symmetry_class(fixture_id: str, coherence: list[float]) -> str:
    if max(coherence) - min(coherence) <= 1e-12:
        return "homogeneous_graph_automorphism_invariant"
    if fixture_id == "F2":
        return "S2_node_exchange_orbit"
    return "D3_triangle_node_permutation_orbit"


def replay_saved_branch(
    snapshot_path: Path,
    reference: dict[str, Any],
    tolerances: dict[str, Any],
) -> dict[str, Any]:
    restored = GRC9V3.load(str(snapshot_path))
    loaded_projection = block_projection(restored)
    load_residual = residual_metrics(reference, loaded_projection)
    load_per_block = {
        block: residual_metrics(reference[block], loaded_projection[block])
        for block in ("C", "W", "J", "Phi", "G", "identity", "budget")
    }
    result = restored.step()
    replay_projection = block_projection(restored)
    replay_residual = residual_metrics(reference, replay_projection)
    replay_per_block = {
        block: residual_metrics(reference[block], replay_projection[block])
        for block in ("C", "W", "J", "Phi", "G", "identity", "budget")
    }
    absolute = tolerances["absolute_tolerances"]
    relative = tolerances["relative_tolerances"]
    block_tolerances = {
        "C": (float(absolute["C"]), float(relative["C"])),
        "W": (float(absolute["W"]), float(relative["W"])),
        "J": (float(absolute["J"]), float(relative["J"])),
        "Phi": (
            float(absolute["derived_surface"]),
            float(relative["derived_surface"]),
        ),
        "G": (
            float(absolute["derived_surface"]),
            float(relative["derived_surface"]),
        ),
        "identity": (
            float(absolute["derived_surface"]),
            float(relative["derived_surface"]),
        ),
        "budget": (float(absolute["C"]), float(relative["C"])),
    }

    def blocks_pass(rows: dict[str, dict[str, Any]]) -> bool:
        return all(
            bool(row["categorical_equal"])
            and float(row["l_inf"]) <= block_tolerances[block][0]
            and float(row["relative"]) <= block_tolerances[block][1]
            for block, row in rows.items()
        )

    load_passed = blocks_pass(load_per_block)
    replay_passed = blocks_pass(replay_per_block)
    return {
        "load_projection_residual": load_residual,
        "load_per_block_residuals": load_per_block,
        "one_step_replay_residual": replay_residual,
        "one_step_replay_per_block_residuals": replay_per_block,
        "declared_block_tolerances": {
            block: {"absolute": values[0], "relative": values[1]}
            for block, values in block_tolerances.items()
        },
        "load_projection_exact": load_residual["l_inf"] == 0.0
        and load_residual["categorical_equal"],
        "load_projection_within_declared_tolerance": load_passed,
        "one_step_replay_within_declared_tolerance": replay_passed,
        "representation_normalization_is_not_restoration_failure": load_passed,
        "events": [event.kind for event in result.events],
        "fixed_topology": reference["topology"] == replay_projection["topology"],
        "raw_loaded_snapshot_sha256": semantic_digest(restored.snapshot()),
        "status": "passed"
        if load_passed
        and replay_passed
        and not result.events
        and reference["topology"] == replay_projection["topology"]
        else "failed",
    }


def selected_branch_ids(branches: list[dict[str, Any]]) -> dict[str, str]:
    selected: dict[str, str] = {}
    for fixture_id in sorted({branch["fixture_id"] for branch in branches}):
        eligible = [branch for branch in branches if branch["fixture_id"] == fixture_id]
        chosen = select_candidate(
            BranchCandidate(
                candidate_id=branch["branch_id"],
                residual=float(branch["full_step_residual"]["l_inf"]),
                parameter_identity=branch["parameter_hash"],
            )
            for branch in eligible
        )
        selected[fixture_id] = chosen.candidate_id
    return selected


def run_fresh_process_replay(branch: dict[str, Any]) -> dict[str, Any]:
    path = REPO_ROOT / branch["state_snapshot_path"]
    result = subprocess.run(
        [sys.executable, str(Path(__file__).resolve()), "--validate-snapshot", str(path)],
        cwd=REPO_ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    record = json.loads(result.stdout)
    record["branch_id"] = branch["branch_id"]
    record["fresh_process"] = True
    return record


def symmetry_controls(
    selected: dict[str, str],
    branches: list[dict[str, Any]],
    config: dict[str, Any],
) -> dict[str, Any]:
    by_id = {branch["branch_id"]: branch for branch in branches}
    rows: list[dict[str, Any]] = []
    for fixture_id, branch_id in sorted(selected.items()):
        branch = by_id[branch_id]
        coherence = list(branch["coherence"])
        params = deepcopy(branch["params"])
        variants: list[tuple[str, list[float], dict[int, int] | None]] = []
        if fixture_id in {"F1", "F2"}:
            variants.append(("node_exchange", list(reversed(coherence)), None))
        else:
            variants.append(("cyclic_node_relabel", coherence[1:] + coherence[:1], None))
        variants.extend(
            (
                ("row_preserving_column_relabel", coherence, {1: 2, 2: 3}),
                ("row_changing_column_preserving_relabel", coherence, {1: 4, 2: 5}),
            )
        )
        for control_id, variant_coherence, port_map in variants:
            _, certification = certify_branch(
                fixture_id,
                variant_coherence,
                params,
                config,
                port_map=port_map,
            )
            rows.append(
                {
                    "fixture_id": fixture_id,
                    "source_branch_id": branch_id,
                    "control_id": control_id,
                    "coherence": variant_coherence,
                    "port_map": mapping(port_map) if port_map else None,
                    "branch_class": certification["branch_class"],
                    "full_step_l_inf": certification["full_step_residual"]["l_inf"],
                    "internal_stage_l_inf": certification["internal_stage_residuals"]["maximum_internal_stage_l_inf"],
                    "no_events": certification["event_and_topology_assertions"]["full_step_no_events"],
                    "fixed_topology": certification["event_and_topology_assertions"]["fixed_topology"],
                    "status": "passed"
                    if certification["branch_class"]
                    == "provisional_physical_strong_branch"
                    else "failed",
                }
            )
    return {
        "rows": rows,
        "all_controls_passed": all(row["status"] == "passed" for row in rows),
        "interpretation": "symmetry-related rows are retained and port relabels are tested as coordinate controls, not deduplicated by Euclidean distance alone",
    }


def protected_manifest_v2() -> dict[str, Any]:
    predecessor_path = EXPERIMENT_ROOT / "outputs/protected_path_manifest_v1.json"
    predecessor = read_json(predecessor_path)
    payload = predecessor["payload"]
    paths = [entry["path"] for entry in payload["files"]]
    current = file_manifest(paths)
    unchanged = current["tree_sha256"] == payload["tree_sha256"]
    if not unchanged:
        raise RuntimeError("GRV2 protected source/spec/root-test paths changed")
    result = {
        **current,
        "manifest_id": "protected_path_manifest_v2",
        "scope": payload["scope"],
        "substrate_base_revision": payload["substrate_base_revision"],
        "predecessor_path": "outputs/protected_path_manifest_v1.json",
        "predecessor_payload_sha256": predecessor["payload_sha256"],
        "predecessor_tree_sha256": payload["tree_sha256"],
        "newly_discovered_load_bearing_paths": [],
        "later_discovery_policy": payload["later_discovery_policy"],
        "unchanged_successor": unchanged,
    }
    return artifact_envelope(
        result,
        schema_version="b1_protected_path_manifest_v2",
        generating_command=COMMAND,
    )


def validate_prerequisite() -> tuple[dict[str, Any], dict[str, Any]]:
    receipt = read_json(EXPERIMENT_ROOT / "outputs/gates/grv1_result_receipt.json")
    anchor = read_json(EXPERIMENT_ROOT / "outputs/gates/grv1_acceptance_anchor.json")
    validate_receipt(receipt)
    validate_acceptance_anchor(anchor)
    if receipt["receipt_payload_sha256"] != GRV1_RECEIPT_SHA256:
        raise RuntimeError("GRV2 prerequisite GRV1 receipt does not match P2 manifest")
    if anchor["receipt_payload_sha256"] != GRV1_RECEIPT_SHA256:
        raise RuntimeError("GRV2 prerequisite anchor targets another receipt")
    if anchor["result_revision"] != GRV1_RESULT_REVISION:
        raise RuntimeError("GRV2 prerequisite anchor targets another result revision")
    if not prerequisite_is_authorized(anchor):
        raise RuntimeError("GRV1 acceptance anchor is not authorized")
    anchor_commit = git(
        "log",
        "-1",
        "--format=%H",
        "--",
        f"{EXPERIMENT_RELATIVE}/outputs/gates/grv1_acceptance_anchor.json",
    )
    if anchor_commit != GRV1_ACCEPTANCE_COMMIT:
        raise RuntimeError("GRV1 acceptance anchor immutable ref mismatch")
    return receipt, anchor


def search_and_certify(output_root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    config = read_json(EXPERIMENT_ROOT / "configs/branch_search.json")
    numerical_tolerances = read_json(
        EXPERIMENT_ROOT / "configs/numerical_tolerances.json"
    )
    assert_search_contract(config)
    snapshots_root = output_root / "branches"
    snapshots_root.mkdir(parents=True, exist_ok=True)
    for stale in snapshots_root.glob("grv2-*.json"):
        stale.unlink()

    rows: list[dict[str, Any]] = []
    branches: list[dict[str, Any]] = []
    branch_index = 0
    parameter_grid = parameter_rows(config)
    for fixture_id in config["candidate_fixtures"]:
        fixture = config["fixture_searches"][fixture_id]
        for parameter_index, parameter in enumerate(parameter_grid):
            params = build_params(
                parameter["site_potential_scale"],
                parameter["dt"],
                parameter["eta"],
                int(config["seed"]),
            )
            parameter_hash = semantic_digest(params)
            for seed_index, seed_values_raw in enumerate(fixture["coherence_seeds"]):
                seed_values = [float(value) for value in seed_values_raw]
                candidate_id = (
                    f"GRV2-{fixture_id}-P{parameter_index:02d}-S{seed_index:02d}"
                )
                if fixture_id == "F1":
                    solver_record = {
                        "solver": "analytic_homogeneous_family_certification",
                        "initial_seed": seed_values,
                        "total_coherence": sum(seed_values),
                        "final_coherence": seed_values,
                        "iterations": 0,
                        "convergence_history": [],
                        "full_step_coherence_l_inf": 0.0,
                        "events": [],
                        "fixed_topology": True,
                        "status": "analytic_candidate",
                    }
                else:
                    solver_record = solve_seed(
                        fixture_id, seed_values, params, config
                    )
                coherence = list(solver_record["final_coherence"])
                contrast = max(coherence) - min(coherence)
                nonuniform_required = fixture_id in {"F2", "F3"}
                row = {
                    "candidate_id": candidate_id,
                    "fixture_id": fixture_id,
                    "parameter_index": parameter_index,
                    "parameter_values": parameter,
                    "parameter_hash": parameter_hash,
                    "seed_index": seed_index,
                    "solver_record": solver_record,
                    "coherence_contrast": contrast,
                    "nonuniform_required": nonuniform_required,
                    "continuation_lineage": "none_independent_bounded_seed_parameter_row",
                }
                if solver_record["status"] not in {"converged", "analytic_candidate"}:
                    row["decision"] = "rejected_solver_did_not_converge"
                    rows.append(row)
                    continue
                if nonuniform_required and contrast < float(
                    config["solver"]["nonuniform_contrast_minimum"]
                ):
                    row["decision"] = "rejected_homogeneous_root_outside_nonuniform_target"
                    rows.append(row)
                    continue
                model, certification = certify_branch(
                    fixture_id, coherence, params, config
                )
                row["certification_summary"] = {
                    "branch_class": certification["branch_class"],
                    "full_step_l_inf": certification["full_step_residual"]["l_inf"],
                    "internal_stage_l_inf": certification["internal_stage_residuals"]["maximum_internal_stage_l_inf"],
                    "budget_correction_l_inf": certification["internal_stage_residuals"]["budget_correction_l_inf"],
                }
                if certification["branch_class"] != "provisional_physical_strong_branch":
                    row["decision"] = "rejected_strong_certification_failed"
                    rows.append(row)
                    continue

                branch_index += 1
                branch_id = f"grv2-{fixture_id.lower()}-{branch_index:03d}"
                model.rebase_reset_baseline()
                snapshot_path = snapshots_root / f"{branch_id}.json"
                model.save(str(snapshot_path))
                reference = block_projection(model)
                replay = replay_saved_branch(
                    snapshot_path, reference, numerical_tolerances
                )
                if replay["status"] != "passed":
                    raise RuntimeError(f"accepted branch replay failed: {branch_id}")
                branch = {
                    "branch_id": branch_id,
                    "source_candidate_id": candidate_id,
                    "fixture_id": fixture_id,
                    "parameter_hash": parameter_hash,
                    "params": params,
                    "coherence": coherence,
                    "state_snapshot_path": repo_relative(snapshot_path),
                    "state_snapshot_sha256": sha256_file(snapshot_path),
                    "state_snapshot_semantic_sha256": semantic_digest(model.snapshot()),
                    "full_step_residual": certification["full_step_residual"],
                    "internal_stage_residuals": certification["internal_stage_residuals"],
                    "budget_residual": {
                        "budget_error": certification["internal_stage_residuals"]["budget_summary"]["budget_error"],
                        "correction_vector": certification["internal_stage_residuals"]["budget_correction_vector"],
                        "correction_l_inf": certification["internal_stage_residuals"]["budget_correction_l_inf"],
                        "numerical_noop": certification["internal_stage_residuals"]["budget_correction_l_inf"]
                        <= float(config["certification"]["budget_correction_l_inf_tolerance"]),
                    },
                    "event_and_topology_assertions": certification["event_and_topology_assertions"],
                    "symmetry_class": symmetry_class(fixture_id, coherence),
                    "symmetry_orbit_id": orbit_id(fixture_id, coherence, parameter_hash),
                    "solver_record": solver_record,
                    "continuity_and_budget_states": {
                        "pre_continuity_state": certification["internal_stage_residuals"]["pre_continuity_state"],
                        "post_continuity_pre_budget_state": certification["internal_stage_residuals"]["post_continuity_pre_budget_state"],
                        "budget_correction_vector": certification["internal_stage_residuals"]["budget_correction_vector"],
                        "post_budget_state": certification["internal_stage_residuals"]["post_budget_state"],
                        "final_refresh_state": certification["internal_stage_residuals"]["final_refresh_state"],
                    },
                    "branch_class": certification["branch_class"],
                    "distance_from_non_smooth_boundaries": certification["distance_from_non_smooth_boundaries"],
                    "grv3_causal_branch_upgrade_status": "deferred_pending_causal_state_closure_audit",
                    "replay_validation": replay,
                    "continuation_lineage": "none_independent_bounded_seed_parameter_row",
                    "continuation_claim_allowed": False,
                    "retention_claim_allowed": False,
                }
                branches.append(branch)
                row["decision"] = "accepted_provisional_physical_strong_branch"
                row["branch_id"] = branch_id
                rows.append(row)

    selected = selected_branch_ids(branches)
    selected_rows = {
        fixture_id: next(
            branch for branch in branches if branch["branch_id"] == branch_id
        )
        for fixture_id, branch_id in selected.items()
    }
    held_out_rows = [
        run_fresh_process_replay(selected_rows[fixture_id])
        for fixture_id in sorted(selected_rows)
    ]
    controls = symmetry_controls(selected, branches, config)
    per_fixture = {}
    for fixture_id in config["candidate_fixtures"]:
        fixture_rows = [row for row in rows if row["fixture_id"] == fixture_id]
        accepted = [
            row
            for row in fixture_rows
            if row["decision"] == "accepted_provisional_physical_strong_branch"
        ]
        per_fixture[fixture_id] = {
            "declared_budget": config["search_budget_per_family"],
            "search_rows_executed": len(fixture_rows),
            "accepted_branch_rows": len(accepted),
            "rejected_search_rows": len(fixture_rows) - len(accepted),
            "nonuniform_branch_found": any(
                row["coherence_contrast"]
                >= float(config["solver"]["nonuniform_contrast_minimum"])
                for row in accepted
            ),
            "negative_scope_when_not_found": config["negative_search_scope"],
        }
    if not branches or not any(branch["fixture_id"] == "F1" for branch in branches):
        raise RuntimeError("GRV2 requires at least one homogeneous strong branch")
    if not controls["all_controls_passed"]:
        raise RuntimeError("GRV2 symmetry or port controls failed")
    if not all(row["status"] == "passed" for row in held_out_rows):
        raise RuntimeError("GRV2 held-out replay failed")

    ledger_payload = {
        "gate_id": "GRV2",
        "search_config_sha256": semantic_digest(config),
        "search_rows": rows,
        "per_fixture": per_fixture,
        "complete_search_accounting": len(rows)
        == sum(search_space_size(config, fixture_id) for fixture_id in config["candidate_fixtures"]),
        "global_nonexistence_claim_allowed": False,
    }
    registry_payload = {
        "gate_id": "GRV2",
        "branches": branches,
        "selection_accounting": {
            "selection_rule": config["selection_rule"],
            "deduplication_rule": config["deduplication_rule"],
            "all_symmetry_related_rows_retained": True,
            "selected_branch_ids": selected,
            "accepted_branch_count": len(branches),
            "search_ledger_path": "outputs/grv2_branch_search_ledger.json",
            "search_ledger_payload_sha256": semantic_digest(ledger_payload),
        },
        "held_out_validation": {
            "rows": held_out_rows,
            "all_passed": all(row["status"] == "passed" for row in held_out_rows),
            "selection_independent_from_held_out_results": True,
        },
        "bounded_search_evidence": {
            "per_fixture": per_fixture,
            "search_budget_respected": all(
                row["search_rows_executed"] <= row["declared_budget"]
                for row in per_fixture.values()
            ),
            "negative_evidence_scope": config["negative_search_scope"],
            "global_nonexistence_claim_allowed": False,
        },
        "symmetry_and_port_controls": controls,
        "claim_boundary": {
            "positive_branch_evidence_candidate": True,
            "positive_evidence_opened": False,
            "positive_evidence_opened_status": "pending_authorized_human_acceptance",
            "provisional_physical_strong_branch_supported": True,
            "causal_strong_branch_supported": False,
            "continuation_supported": False,
            "retention_supported": False,
            "readback_supported": False,
            "writeback_supported": False,
            "claim_ceiling": "existence_and_local_source_identity_of_GRC_formed_fixed_branches_only",
        },
    }
    return (
        artifact_envelope(
            registry_payload,
            schema_version="b1_grv2_fixed_branch_registry_v1",
            generating_command=COMMAND,
        ),
        artifact_envelope(
            ledger_payload,
            schema_version="b1_grv2_branch_search_ledger_v1",
            generating_command=COMMAND,
        ),
    )


def write_report(registry: dict[str, Any], ledger: dict[str, Any]) -> Path:
    payload = registry["payload"]
    per_fixture = ledger["payload"]["per_fixture"]
    report = EXPERIMENT_ROOT / "reports/b1_grv2_strong_formed_branches.md"
    lines = [
        "# B1-GR GRV2 Strong Formed Branches",
        "",
        "## Result",
        "",
        "```text",
        "gate = GRV2",
        "mechanical_status = passed",
        "scientific_acceptance = awaiting_human_review",
        "candidate_closeout_ceiling = GRV-C3",
        "positive_branch_evidence_candidate = true",
        "positive_evidence_opened = false_pending_human_acceptance",
        "causal_strong_branch = deferred_to_GRV3",
        "continuation = unsupported",
        "retention = unsupported",
        "readback = unsupported",
        "writeback = unsupported",
        "runtime_change_authorized = false",
        "```",
        "",
        "GRV2 certifies formed fixed-branch candidates against the unchanged public",
        "`GRC9V3.step()` and a fresh staged replay of every load-bearing runtime stage.",
        "A formed branch is a state that remains physically fixed under this bounded",
        "runtime envelope. Its existence does not show that a perturbation continues,",
        "is retained, is read later, or writes back into the substrate.",
        "",
        "## Search Accounting",
        "",
    ]
    for fixture_id in sorted(per_fixture):
        row = per_fixture[fixture_id]
        lines.append(
            f"- `{fixture_id}`: {row['search_rows_executed']} rows, "
            f"{row['accepted_branch_rows']} accepted branch rows, "
            f"{row['rejected_search_rows']} rejected rows, "
            f"nonuniform found = `{str(row['nonuniform_branch_found']).lower()}`."
        )
    lines.extend(
        [
            "",
            "The nonuniform search is bounded to the committed seed, parameter, solver,",
            "and compute envelope. Rejected rows and an absent family would not establish",
            "global nonexistence.",
            "",
            "## Certification",
            "",
            f"- Accepted branch rows: `{len(payload['branches'])}`",
            f"- Held-out fresh-process rows: `{len(payload['held_out_validation']['rows'])}` (all passed)",
            f"- Symmetry/port controls: `{len(payload['symmetry_and_port_controls']['rows'])}` (all passed)",
            "- Budget correction is a numerical no-op on every accepted branch.",
            "- Every accepted branch emits no event and preserves topology.",
            "- Every accepted branch passes save/load and one-step replay.",
            "- Zero-current branches lie on a basin/sink identity boundary; GRV3 must",
            "  admit a causal stratum before any causal-branch upgrade or derivative claim.",
            "",
            "## Claim Boundary",
            "",
            "This result supports only a provisional candidate for the existence and local",
            "source identity of GRC formed fixed branches. `causal_strong_branch` remains",
            "deferred to GRV3. No continuation, retention, read-back, write-back, memory,",
            "learning, agency, organism, or life claim follows from GRV2.",
        ]
    )
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report


def run_grv2() -> None:
    if git("status", "--porcelain"):
        raise SystemExit("GRV2 requires a clean committed P2 input revision")
    receipt1, anchor1 = validate_prerequisite()
    input_revision = git("rev-parse", "HEAD")
    input_paths = tracked_files([EXPERIMENT_RELATIVE])
    input_tree = file_manifest(input_paths)
    baseline = read_json(EXPERIMENT_ROOT / "outputs/baseline_manifest.json")["payload"]
    output_root = EXPERIMENT_ROOT / "outputs"
    registry, ledger = search_and_certify(output_root)
    registry_path = output_root / "fixed_branch_registry.json"
    ledger_path = output_root / "grv2_branch_search_ledger.json"
    write_json(registry_path, registry)
    write_json(ledger_path, ledger)
    protected_path = output_root / "protected_path_manifest_v2.json"
    write_json(protected_path, protected_manifest_v2())
    report_path = write_report(registry, ledger)
    snapshot_paths = sorted((output_root / "branches").glob("grv2-*.json"))
    artifacts = [registry_path, ledger_path, protected_path, report_path, *snapshot_paths]
    receipt = finalize_receipt(
        {
            "gate_id": "GRV2",
            "input_execution_revision": input_revision,
            "substrate_base_revision": baseline["substrate_base_revision"],
            "input_experiment_tree_sha256": input_tree["tree_sha256"],
            "prerequisite_result_receipt_digests": [GRV1_RECEIPT_SHA256],
            "prerequisite_acceptance_anchors": [
                {
                    "gate_id": "GRV1",
                    "immutable_ref": f"git:{GRV1_ACCEPTANCE_COMMIT}",
                    "anchor_payload_sha256": semantic_digest(anchor1),
                }
            ],
            "output_artifact_digests": {
                path.relative_to(EXPERIMENT_ROOT).as_posix(): sha256_file(path)
                for path in sorted(artifacts)
            },
            "status": "awaiting_scientific_review",
            "blocked_gates": [f"GRV{index}" for index in range(3, 9)],
            "claim_ceiling": "GRV-C3_candidate_formed_branch_existence_and_local_source_identity_only_pending_authorized_human_acceptance",
            "prerequisite_receipt_status": receipt1["status"],
        }
    )
    validate_receipt(receipt)
    write_json(output_root / "gates/grv2_result_receipt.json", receipt)


def validate_snapshot_cli(path: Path) -> None:
    model = GRC9V3.load(str(path))
    before = block_projection(model)
    result = model.step()
    after = block_projection(model)
    residual = residual_metrics(before, after)
    record = {
        "snapshot_sha256": sha256_file(path),
        "before_projection_sha256": semantic_digest(before),
        "after_projection_sha256": semantic_digest(after),
        "full_step_residual": residual,
        "events": [event.kind for event in result.events],
        "fixed_topology": before["topology"] == after["topology"],
        "status": "passed"
        if residual["l_inf"] <= 1e-9
        and residual["categorical_equal"]
        and not result.events
        and before["topology"] == after["topology"]
        else "failed",
    }
    print(json.dumps(record, sort_keys=True, allow_nan=False))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-snapshot", type=Path)
    args = parser.parse_args()
    if args.validate_snapshot is not None:
        validate_snapshot_cli(args.validate_snapshot)
        return
    run_grv2()
    print("GRV2 mechanically validated; scientific acceptance anchor is pending.")


if __name__ == "__main__":
    main()
