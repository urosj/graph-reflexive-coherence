"""GRV6 edge-space controls and bounded return-orbit search methods."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import fields, replace
from pathlib import Path
import tempfile
from typing import Any, Iterable

import numpy as np
from numpy.typing import NDArray

from artifact_io import semantic_digest
from edge_space import (
    cycle_basis,
    native_potential_flow_annihilation_error,
    projector_diagnostics,
    weighted_cycle_projector,
)
from grv5_methods import (
    activity_amplitude_from_target,
    categorical_projection,
    clone_model,
    coherence_vector,
    conductance_vector,
    current_vector,
)
from state_codec import BranchCoordinateChart, categorical_signature

from pygrc.models import GRC9V3
from pygrc.models.grc_9_v3_runtime import (
    compute_base_conductance,
    compute_edge_labels,
    compute_flux,
    compute_potential,
)


def oriented_incidence(
    model: GRC9V3,
) -> tuple[NDArray[np.float64], list[int], list[int]]:
    state = model.get_state()
    nodes = sorted(state.topology.iter_live_node_ids())
    edges = sorted(state.topology.iter_live_edge_ids())
    node_index = {node_id: index for index, node_id in enumerate(nodes)}
    incidence = np.zeros((len(nodes), len(edges)), dtype=float)
    for column, edge_id in enumerate(edges):
        edge = state.port_edges[edge_id]
        incidence[node_index[edge.node_u], column] = -1.0
        incidence[node_index[edge.node_v], column] = 1.0
    return incidence, nodes, edges


def set_current(model: GRC9V3, values: Iterable[float]) -> GRC9V3:
    clone = clone_model(model)
    state = deepcopy(clone.get_state())
    edges = sorted(state.topology.iter_live_edge_ids())
    current = list(values)
    if len(current) != len(edges):
        raise ValueError("one current value is required per live edge")
    for edge_id, value in zip(edges, current, strict=True):
        state.port_edges[edge_id] = replace(
            state.port_edges[edge_id], flux_uv=float(value)
        )
    clone.set_state(state)
    return clone


def normalized_direction(values: NDArray[np.float64]) -> NDArray[np.float64]:
    norm = float(np.linalg.norm(values))
    if norm == 0.0:
        return values.copy()
    return values / norm


def canonical_finite_seed(model: GRC9V3) -> NDArray[np.float64]:
    incidence, nodes, _ = oriented_incidence(model)
    if incidence.shape[1] == 0:
        return np.zeros(0, dtype=float)
    node_profile = np.arange(len(nodes), dtype=float)
    node_profile -= float(np.mean(node_profile))
    direction = incidence.T @ node_profile
    if float(np.linalg.norm(direction)) == 0.0:
        direction = np.ones(incidence.shape[1], dtype=float)
    return normalized_direction(direction)


def canonical_cycle_seed(
    model: GRC9V3, *, rank_tolerance: float
) -> NDArray[np.float64] | None:
    incidence, _, _ = oriented_incidence(model)
    basis = cycle_basis(incidence, rank_tolerance=rank_tolerance)
    if basis.shape[1] == 0:
        return None
    vector = basis[:, 0]
    first_nonzero = next((value for value in vector if abs(value) > 1e-15), 1.0)
    if first_nonzero < 0.0:
        vector = -vector
    return normalized_direction(vector)


def edge_space_audit(model: GRC9V3, config: dict[str, Any]) -> dict[str, Any]:
    edge_config = config["edge_space"]
    incidence, nodes, edges = oriented_incidence(model)
    conductance = conductance_vector(model)
    if conductance.size and float(np.min(conductance)) < float(
        edge_config["minimum_positive_conductance"]
    ):
        raise ValueError("branch violates preregistered minimum conductance")
    projector = weighted_cycle_projector(
        incidence,
        conductance,
        condition_limit=float(edge_config["condition_limit"]),
        rank_tolerance=float(edge_config["rank_tolerance"]),
    )
    diagnostics = projector_diagnostics(incidence, conductance, projector)
    basis = cycle_basis(
        incidence, rank_tolerance=float(edge_config["rank_tolerance"])
    )
    metric = np.diag(1.0 / conductance)
    projected_gram = basis.T @ metric @ basis
    incidence_rank = int(incidence.shape[1] - basis.shape[1])
    metric_condition = float(np.linalg.cond(metric)) if metric.size else 1.0
    projected_gram_condition = (
        float(np.linalg.cond(projected_gram)) if projected_gram.size else None
    )
    state = model.get_state()
    potential = np.asarray(
        [float(state.potential[node]) for node in nodes], dtype=float
    )
    eta = float(model.get_params().evolution["eta"])
    potential_error = native_potential_flow_annihilation_error(
        incidence, conductance, projector, potential, eta=eta
    )
    reorientation = np.diag(
        np.asarray([(-1.0 if index % 2 == 0 else 1.0) for index in range(len(edges))])
    )
    reoriented_projector = weighted_cycle_projector(
        incidence @ reorientation,
        conductance,
        condition_limit=float(edge_config["condition_limit"]),
        rank_tolerance=float(edge_config["rank_tolerance"]),
    )
    covariance_error = float(
        np.linalg.norm(
            reoriented_projector - reorientation @ projector @ reorientation,
            ord=2,
        )
    )
    cycle = canonical_cycle_seed(
        model, rank_tolerance=float(edge_config["rank_tolerance"])
    )
    cycle_divergence = (
        0.0 if cycle is None else float(np.linalg.norm(incidence @ cycle, ord=2))
    )
    algebra_tolerance = float(edge_config["algebra_tolerance"])
    return {
        "node_order": nodes,
        "edge_order": edges,
        "edge_orientation": [
            [state.port_edges[edge].node_u, state.port_edges[edge].node_v]
            for edge in edges
        ],
        "incidence": incidence.tolist(),
        "conductance": conductance.tolist(),
        "minimum_conductance": float(np.min(conductance, initial=np.inf)),
        "conductance_floor_margin": float(
            np.min(conductance, initial=np.inf)
            - float(edge_config["minimum_positive_conductance"])
        ),
        "incidence_rank": incidence_rank,
        "cycle_dimension": int(basis.shape[1]),
        "inverse_conductance_metric_condition_number": metric_condition,
        "projected_cycle_gram_condition_number": projected_gram_condition,
        "projected_cycle_gram_status": (
            "admitted_within_condition_limit"
            if projected_gram.size
            else "not_applicable_zero_cycle_dimension"
        ),
        "cycle_projector": projector.tolist(),
        "potential_projector": (np.eye(len(edges)) - projector).tolist(),
        "diagnostics": diagnostics,
        "native_potential_flow_annihilation_error": potential_error,
        "edge_reorientation_covariance_error": covariance_error,
        "canonical_cycle_seed": None if cycle is None else cycle.tolist(),
        "canonical_cycle_seed_divergence_l2": cycle_divergence,
        "all_primary_edge_space_checks_passed": bool(
            all(value <= algebra_tolerance for value in diagnostics.values())
            and potential_error
            <= float(edge_config["native_potential_annihilation_tolerance"])
            and covariance_error <= algebra_tolerance
            and cycle_divergence <= float(edge_config["divergence_tolerance"])
        ),
    }


def current_projection(
    model: GRC9V3,
    projector: NDArray[np.float64],
    incidence: NDArray[np.float64],
) -> dict[str, Any]:
    current = current_vector(model)
    cycle = projector @ current
    potential = current - cycle
    return {
        "J": current.tolist(),
        "J_l2": float(np.linalg.norm(current)),
        "divergence_l2": float(np.linalg.norm(incidence @ current, ord=2)),
        "cycle_component": cycle.tolist(),
        "cycle_component_l2": float(np.linalg.norm(cycle)),
        "potential_component": potential.tolist(),
        "potential_component_l2": float(np.linalg.norm(potential)),
    }


def seeded_trajectory(
    model: GRC9V3,
    seed: NDArray[np.float64],
    *,
    steps: int,
    projector: NDArray[np.float64],
    incidence: NDArray[np.float64],
) -> dict[str, Any]:
    candidate = set_current(model, seed)
    rows = []
    for beat in range(steps + 1):
        rows.append(
            {
                "beat": beat,
                "C": coherence_vector(candidate).tolist(),
                "budget": float(np.sum(coherence_vector(candidate))),
                "budget_target": float(candidate.get_state().budget_target),
                "budget_error": abs(
                    float(np.sum(coherence_vector(candidate)))
                    - float(candidate.get_state().budget_target)
                ),
                "W": conductance_vector(candidate).tolist(),
                **current_projection(candidate, projector, incidence),
                "categorical_state": categorical_projection(candidate),
            }
        )
        if beat < steps:
            candidate.step()
    return {"rows": rows, "final_model": candidate}


def seed_certification(
    model: GRC9V3,
    seed: NDArray[np.float64],
    *,
    projector: NDArray[np.float64],
    incidence: NDArray[np.float64],
    config: dict[str, Any],
    require_cycle_membership: bool,
    require_divergence_free: bool,
) -> dict[str, Any]:
    seeded = set_current(model, seed)
    seed_norm = float(np.linalg.norm(seed, ord=2))
    divergence = float(np.linalg.norm(incidence @ seed, ord=2))
    cycle_reconstruction = float(np.linalg.norm(projector @ seed - seed, ord=2))
    state = model.get_state()
    seeded_state = seeded.get_state()
    baseline_eligibility_model = clone_model(model)
    seeded_eligibility_model = clone_model(seeded)
    baseline_eligibility_model.rebuild_differential_state()
    seeded_eligibility_model.rebuild_differential_state()
    baseline_spark_candidates = baseline_eligibility_model.detect_hybrid_spark_candidates()
    seeded_spark_candidates = seeded_eligibility_model.detect_hybrid_spark_candidates()

    def spark_candidate_digests(candidates: list[Any]) -> list[str]:
        return [
            semantic_digest(
                {
                    "kind": candidate.kind,
                    "step_index": candidate.step_index,
                    "payload": dict(candidate.payload),
                    "source_family": candidate.source_family,
                }
            )
            for candidate in candidates
        ]

    baseline_candidate_digests = spark_candidate_digests(
        baseline_spark_candidates
    )
    seeded_candidate_digests = spark_candidate_digests(
        seeded_spark_candidates
    )
    state_field_names = {field.name for field in fields(type(state))}
    external_boundary_surface_names = {
        "boundary_current",
        "boundary_flux",
        "external_current",
        "external_flux",
        "source_current",
    }
    present_external_boundary_surfaces = sorted(
        state_field_names & external_boundary_surface_names
    )
    params = model.get_params()
    modes = params.constitutive_semantic_modes
    all_nodes_have_incident_edges = all(
        bool(tuple(state.topology.incident_edge_ids(node_id)))
        for node_id in state.topology.iter_live_node_ids()
    )
    no_event_eligibility_crossing = bool(
        baseline_candidate_digests == seeded_candidate_digests
        and str(modes["choice_backend"]) == "disabled"
        and float(params.evolution["lambda_birth"]) == 0.0
        and all_nodes_have_incident_edges
    )
    control = config["current_controls"]
    edge = config["edge_space"]
    divergence_effective_tolerance = float(edge["divergence_tolerance"]) + (
        float(edge["seed_divergence_relative_tolerance"]) * seed_norm
    )
    cycle_reconstruction_effective_tolerance = float(edge["algebra_tolerance"]) + (
        float(edge["seed_algebra_relative_tolerance"]) * seed_norm
    )
    checks = {
        "divergence_gate_satisfied": (
            divergence <= divergence_effective_tolerance
            if require_divergence_free
            else True
        ),
        "cycle_membership_within_tolerance": (
            cycle_reconstruction <= cycle_reconstruction_effective_tolerance
            if require_cycle_membership
            else True
        ),
        "seed_above_current_floor": seed_norm
        > float(control["minimum_certified_seed_current_l2"]),
        "topology_unchanged_by_seed_insertion": categorical_projection(model)[
            "topology_nodes"
        ]
        == categorical_projection(seeded)["topology_nodes"]
        and categorical_projection(model)["topology_edges"]
        == categorical_projection(seeded)["topology_edges"],
        "coherence_matched": np.array_equal(
            coherence_vector(model), coherence_vector(seeded)
        ),
        "conductance_matched": np.array_equal(
            conductance_vector(model), conductance_vector(seeded)
        ),
        "rng_matched": state.rng_state == seeded_state.rng_state,
        "administrative_phase_matched": bool(
            state.step_index == seeded_state.step_index
            and state.time == seeded_state.time
        ),
        "positive_conductance": bool(np.all(conductance_vector(seeded) > 0.0)),
        "no_external_boundary_drive": not present_external_boundary_surfaces,
        "no_event_eligibility_crossing": no_event_eligibility_crossing,
    }
    return {
        "provenance": "experiment_authored_synthetic_structurally_valid_seed",
        "runtime_reached_seed": False,
        "seed_l2": seed_norm,
        "seed_divergence_l2": divergence,
        "seed_divergence_relative_to_l2": divergence / max(seed_norm, 1e-30),
        "seed_divergence_effective_tolerance": divergence_effective_tolerance,
        "measured_divergence_within_cycle_tolerance": divergence
        <= divergence_effective_tolerance,
        "require_divergence_free": require_divergence_free,
        "cycle_membership_reconstruction_l2": cycle_reconstruction,
        "cycle_membership_reconstruction_relative_to_l2": cycle_reconstruction
        / max(seed_norm, 1e-30),
        "cycle_membership_effective_tolerance": cycle_reconstruction_effective_tolerance,
        "require_cycle_membership": require_cycle_membership,
        "event_eligibility_audit": {
            "baseline_hybrid_spark_candidate_digests": baseline_candidate_digests,
            "seeded_hybrid_spark_candidate_digests": seeded_candidate_digests,
            "hybrid_spark_eligibility_matched": baseline_candidate_digests
            == seeded_candidate_digests,
            "choice_backend": str(modes["choice_backend"]),
            "growth_lambda_birth": float(params.evolution["lambda_birth"]),
            "all_nodes_have_incident_edges": all_nodes_have_incident_edges,
            "boundary_mode": str(modes["boundary_mode"]),
            "present_external_boundary_surfaces": present_external_boundary_surfaces,
            "no_event_eligibility_crossing": no_event_eligibility_crossing,
        },
        "checks": checks,
        "certified_before_runtime": all(checks.values()),
    }


def stage_projection(
    model: GRC9V3,
    reference: GRC9V3,
    *,
    stage: str,
    fixed_projector: NDArray[np.float64],
    incidence: NDArray[np.float64],
    config: dict[str, Any],
) -> dict[str, Any]:
    fixed = current_projection(model, fixed_projector, incidence)
    phase_projector = weighted_cycle_projector(
        incidence,
        conductance_vector(model),
        condition_limit=float(config["edge_space"]["condition_limit"]),
        rank_tolerance=float(config["edge_space"]["rank_tolerance"]),
    )
    phase_local = current_projection(model, phase_projector, incidence)
    coherence = coherence_vector(model)
    conductance = conductance_vector(model)
    state = model.get_state()
    return {
        "stage": stage,
        "C": coherence.tolist(),
        "W": conductance.tolist(),
        "fixed_reference_projection": fixed,
        "phase_local_projection": phase_local,
        "delta_C_linf_from_branch": float(
            np.linalg.norm(coherence - coherence_vector(reference), ord=np.inf)
        ),
        "delta_W_linf_from_branch": float(
            np.linalg.norm(conductance - conductance_vector(reference), ord=np.inf)
        ),
        "budget": float(np.sum(coherence)),
        "budget_target": float(state.budget_target),
        "budget_error": abs(float(np.sum(coherence)) - float(state.budget_target)),
        "categorical_state": categorical_projection(model),
    }


def native_seed_stage_trace(
    model: GRC9V3,
    seed: NDArray[np.float64],
    *,
    fixed_projector: NDArray[np.float64],
    incidence: NDArray[np.float64],
    config: dict[str, Any],
) -> dict[str, Any]:
    reference = clone_model(model)
    manual = set_current(model, seed)
    stages = []

    def record(stage: str, candidate: GRC9V3 | None = None) -> None:
        stages.append(
            stage_projection(
                manual if candidate is None else candidate,
                reference,
                stage=stage,
                fixed_projector=fixed_projector,
                incidence=incidence,
                config=config,
            )
        )

    def transport_surface(model_at_stage: GRC9V3) -> dict[str, Any]:
        state_at_stage = model_at_stage.get_state()
        return {
            "base_conductance": {
                str(key): float(value)
                for key, value in sorted(state_at_stage.base_conductance.items())
            },
            "potential": {
                str(key): float(value)
                for key, value in sorted(state_at_stage.potential.items())
            },
            "port_edges": {
                str(key): {
                    "conductance": float(value.conductance),
                    "flux_uv": float(value.flux_uv),
                }
                for key, value in sorted(state_at_stage.port_edges.items())
            },
            "geometric_length": {
                str(key): float(value)
                for key, value in sorted(state_at_stage.geometric_length.items())
            },
            "flux_coupling": {
                str(key): float(value)
                for key, value in sorted(state_at_stage.flux_coupling.items())
            },
            "temporal_delay": {
                str(key): float(value)
                for key, value in sorted(state_at_stage.temporal_delay.items())
            },
        }

    def trace_transport_kernels(prefix: str) -> dict[str, Any]:
        diagnostic = clone_model(manual)
        diagnostic_state = diagnostic.get_state()
        params = diagnostic.get_params()
        compute_base_conductance(
            diagnostic_state,
            evolution=params.evolution,
            modes=params.constitutive_semantic_modes,
        )
        record(f"after_{prefix}_conductance_formation", diagnostic)
        compute_edge_labels(
            diagnostic_state,
            evolution=params.evolution,
            modes=params.constitutive_semantic_modes,
            pre_flux_only=True,
        )
        record(f"after_{prefix}_pre_flux_edge_labels", diagnostic)
        compute_potential(diagnostic_state, evolution=params.evolution)
        record(f"after_{prefix}_potential_reconstruction", diagnostic)
        compute_flux(diagnostic_state, evolution=params.evolution)
        record(f"after_{prefix}_native_current_reconstruction", diagnostic)
        compute_edge_labels(
            diagnostic_state,
            evolution=params.evolution,
            modes=params.constitutive_semantic_modes,
            pre_flux_only=False,
        )
        record(f"after_{prefix}_post_flux_edge_labels", diagnostic)
        diagnostic_surface = transport_surface(diagnostic)

        manual.rebuild_transport_state()
        record(f"after_{prefix}_public_transport_wrapper")
        physical_parity = block_residual(diagnostic, manual)
        surface_equal = diagnostic_surface == transport_surface(manual)
        maximum_physical_parity = max(physical_parity.values(), default=0.0)
        tolerance = float(
            config["current_controls"]["transport_kernel_wrapper_parity_tolerance"]
        )
        return {
            "kernel_stage_order": [
                f"after_{prefix}_conductance_formation",
                f"after_{prefix}_pre_flux_edge_labels",
                f"after_{prefix}_potential_reconstruction",
                f"after_{prefix}_native_current_reconstruction",
                f"after_{prefix}_post_flux_edge_labels",
            ],
            "public_wrapper_stage": f"after_{prefix}_public_transport_wrapper",
            "kernel_vs_public_wrapper_block_linf": physical_parity,
            "kernel_vs_public_wrapper_maximum_linf": maximum_physical_parity,
            "kernel_vs_public_wrapper_transport_surface_equal": surface_equal,
            "kernel_trace_matches_public_wrapper": bool(
                maximum_physical_parity <= tolerance and surface_equal
            ),
        }

    record("after_direct_old_current_input")
    manual.rebuild_differential_state()
    record("after_pre_flux_differential_rebuild")
    first_transport_kernel_audit = trace_transport_kernels("first")
    manual.rebuild_differential_state()
    record("after_post_flux_differential_refresh")
    manual.rebuild_identity_state()
    record("after_identity_rebuild")
    manual.apply_hybrid_sparks()
    record("after_hybrid_spark_stages")
    manual.rebuild_choice_state()
    record("after_choice_rebuild")
    manual.apply_growth()
    record("after_growth")
    manual.apply_boundary_behavior()
    record("after_boundary_behavior")
    manual.apply_continuity()
    record("after_continuity")
    budget_summary = manual.enforce_quadrature_budget()
    record("after_budget_enforcement")
    manual.rebuild_differential_state()
    record("after_final_differential_rebuild_1")
    final_transport_kernel_audit = trace_transport_kernels("final")
    manual.rebuild_differential_state()
    record("after_final_differential_rebuild_2")
    manual.rebuild_identity_state()
    record("after_final_identity_rebuild")

    complete = set_current(model, seed)
    complete.step()
    complete_projection = stage_projection(
        complete,
        reference,
        stage="after_complete_native_step",
        fixed_projector=fixed_projector,
        incidence=incidence,
        config=config,
    )
    parity = block_residual(manual, complete)
    parity_maximum = max(parity.values(), default=0.0)
    return {
        "stage_order": [row["stage"] for row in stages],
        "stages": stages,
        "after_complete_native_step": complete_projection,
        "budget_enforcement_summary": budget_summary,
        "first_transport_kernel_audit": first_transport_kernel_audit,
        "final_transport_kernel_audit": final_transport_kernel_audit,
        "both_transport_kernel_traces_match_public_wrapper": bool(
            first_transport_kernel_audit["kernel_trace_matches_public_wrapper"]
            and final_transport_kernel_audit["kernel_trace_matches_public_wrapper"]
        ),
        "manual_stage_vs_complete_step_block_linf": parity,
        "manual_stage_vs_complete_step_maximum_linf": parity_maximum,
        "manual_stage_vs_complete_step_categorical_equal": bool(
            categorical_projection(manual) == categorical_projection(complete)
        ),
        "manual_stage_trace_matches_complete_step": bool(
            parity_maximum
            <= float(
                config["current_controls"][
                    "stage_trace_complete_step_parity_tolerance"
                ]
            )
            and categorical_projection(manual) == categorical_projection(complete)
        ),
    }


def first_transport_model(model: GRC9V3, seed: NDArray[np.float64]) -> GRC9V3:
    candidate = set_current(model, seed)
    candidate.rebuild_differential_state()
    candidate.rebuild_transport_state()
    return candidate


def activity_amplitude_ladder(
    model: GRC9V3,
    direction: NDArray[np.float64],
    *,
    projector: NDArray[np.float64],
    incidence: NDArray[np.float64],
    config: dict[str, Any],
    require_cycle_membership: bool,
) -> list[dict[str, Any]]:
    control = config["current_controls"]
    gamma = float(model.get_params().evolution["gamma"])
    zero_transport = first_transport_model(model, np.zeros_like(direction))
    zero_w = conductance_vector(zero_transport)
    rows = []
    for target_exponent in control["structural_activity_target_exponent_ladder"]:
        amplitude = abs(activity_amplitude_from_target(model, float(target_exponent)))
        positive_seed = amplitude * direction
        negative_seed = -positive_seed
        positive_transport = first_transport_model(model, positive_seed)
        negative_transport = first_transport_model(model, negative_seed)
        positive_w = conductance_vector(positive_transport)
        negative_w = conductance_vector(negative_transport)
        expected_exponent = 0.5 * gamma * np.square(positive_seed)
        observed_exponent = np.log(zero_w / positive_w)
        response_error = float(
            np.linalg.norm(observed_exponent - expected_exponent, ord=np.inf)
        )
        response_scale = max(
            float(np.linalg.norm(expected_exponent, ord=np.inf)), 1e-30
        )
        relative_error = response_error / response_scale
        positive_complete = seeded_trajectory(
            model,
            positive_seed,
            steps=1,
            projector=projector,
            incidence=incidence,
        )
        negative_complete = seeded_trajectory(
            model,
            negative_seed,
            steps=1,
            projector=projector,
            incidence=incidence,
        )
        positive_state = positive_complete["final_model"].get_state()
        budget = positive_state.cached_quantities.get("last_quadrature_budget", {})
        rows.append(
            {
                "target_activity_exponent": float(target_exponent),
                "derived_seed_amplitude": amplitude,
                "seed_provenance": "experiment_authored_synthetic_activity_ladder",
                "positive_seed_certification": seed_certification(
                    model,
                    positive_seed,
                    projector=projector,
                    incidence=incidence,
                    config=config,
                    require_cycle_membership=require_cycle_membership,
                    require_divergence_free=require_cycle_membership,
                ),
                "negative_seed_certification": seed_certification(
                    model,
                    negative_seed,
                    projector=projector,
                    incidence=incidence,
                    config=config,
                    require_cycle_membership=require_cycle_membership,
                    require_divergence_free=require_cycle_membership,
                ),
                "positive_first_transport_W": positive_w.tolist(),
                "negative_first_transport_W": negative_w.tolist(),
                "sign_even_first_transport_W_linf": float(
                    np.linalg.norm(positive_w - negative_w, ord=np.inf)
                ),
                "observed_activity_exponent_by_edge": observed_exponent.tolist(),
                "expected_quadratic_activity_exponent_by_edge": expected_exponent.tolist(),
                "quadratic_response_relative_error": relative_error,
                "quadratic_response_passed": relative_error
                <= float(control["activity_response_shape_relative_error_max"]),
                "positive_post_step": positive_complete["rows"][-1],
                "negative_post_step": negative_complete["rows"][-1],
                "budget_projection_changed_state": bool(
                    abs(float(budget.get("budget_after", 0.0)) - float(budget.get("budget_before", 0.0)))
                    > float(control["budget_tolerance"])
                    or abs(float(budget.get("negative_mass_correction", 0.0)))
                    > float(control["budget_tolerance"])
                ),
                "conductance_floor_active": bool(
                    min(positive_w.tolist() + negative_w.tolist())
                    <= float(config["edge_space"]["minimum_positive_conductance"])
                ),
                "events_or_topology_changed": bool(
                    categorical_projection(positive_complete["final_model"])["event_kinds"]
                    or categorical_projection(negative_complete["final_model"])["event_kinds"]
                    or categorical_projection(positive_complete["final_model"])["topology_nodes"]
                    != categorical_projection(model)["topology_nodes"]
                    or categorical_projection(negative_complete["final_model"])["topology_nodes"]
                    != categorical_projection(model)["topology_nodes"]
                ),
            }
        )
    return rows


def exact_zero_symmetry_audit(
    model: GRC9V3, fixture_id: str, *, tolerance: float
) -> dict[str, Any]:
    state = model.get_state()
    coherence = coherence_vector(model)
    conductance = conductance_vector(model)
    current = current_vector(model)
    potential = np.asarray(
        [float(state.potential[node]) for node in sorted(state.topology.iter_live_node_ids())],
        dtype=float,
    )
    checks = {
        "fixture_declared_symmetric": fixture_id == "F1",
        "coherence_uniform": float(np.ptp(coherence)) <= tolerance,
        "potential_uniform": float(np.ptp(potential)) <= tolerance,
        "conductance_uniform": float(np.ptp(conductance)) <= tolerance,
        "old_current_exact_zero": bool(np.all(current == 0.0)),
        "two_node_single_edge_swap_topology": bool(
            len(tuple(state.topology.iter_live_node_ids())) == 2
            and len(tuple(state.topology.iter_live_edge_ids())) == 1
        ),
        "event_log_empty": not state.event_log,
    }
    return {
        "checks": checks,
        "full_orientation_relevant_symmetry_certified": all(checks.values()),
        "certification_basis": "F1_two_node_swap_symmetry_plus_numeric_causal_fields",
    }


def branch_current_control(
    model: GRC9V3,
    branch_id: str,
    fixture_id: str,
    config: dict[str, Any],
) -> dict[str, Any]:
    edge_audit = edge_space_audit(model, config)
    projector = np.asarray(edge_audit["cycle_projector"], dtype=float)
    incidence = np.asarray(edge_audit["incidence"], dtype=float)
    control = config["current_controls"]
    finite = canonical_finite_seed(model) * float(control["finite_seed_amplitude"])
    zero = np.zeros_like(finite)
    positive = seeded_trajectory(
        model,
        finite,
        steps=int(control["complete_step_count"]),
        projector=projector,
        incidence=incidence,
    )
    negative = seeded_trajectory(
        model,
        -finite,
        steps=int(control["complete_step_count"]),
        projector=projector,
        incidence=incidence,
    )
    zero_row = seeded_trajectory(
        model,
        zero,
        steps=int(control["complete_step_count"]),
        projector=projector,
        incidence=incidence,
    )
    positive_w = np.asarray(positive["rows"][1]["W"], dtype=float)
    negative_w = np.asarray(negative["rows"][1]["W"], dtype=float)
    post_current_delta = (
        float(
            np.linalg.norm(
                np.asarray(positive["rows"][1]["J"])
                - np.asarray(negative["rows"][1]["J"]),
                ord=np.inf,
            )
        )
        if finite.size
        else 0.0
    )
    cycle_seed = canonical_cycle_seed(
        model, rank_tolerance=float(config["edge_space"]["rank_tolerance"])
    )
    cycle_rows: list[dict[str, Any]] = []
    cycle_activity_ladder: list[dict[str, Any]] = []
    cycle_stage_trace_pair: dict[str, Any] | None = None
    if cycle_seed is not None:
        for sign in (1.0, -1.0):
            seed = sign * float(control["cycle_seed_amplitude"]) * cycle_seed
            divergence = float(
                np.linalg.norm(np.asarray(edge_audit["incidence"]) @ seed, ord=2)
            )
            trace = seeded_trajectory(
                model,
                seed,
                steps=int(control["complete_step_count"]),
                projector=projector,
                incidence=incidence,
            )
            certification = seed_certification(
                model,
                seed,
                projector=projector,
                incidence=incidence,
                config=config,
                require_cycle_membership=True,
                require_divergence_free=True,
            )
            cycle_rows.append(
                {
                    "sign": "positive" if sign > 0.0 else "negative",
                    "seed": seed.tolist(),
                    "seed_divergence_l2": divergence,
                    "seed_certification": certification,
                    "seed_certified_before_runtime": certification[
                        "certified_before_runtime"
                    ],
                    "trajectory": trace["rows"],
                    "classification": (
                        "cycle_seed_overwritten_by_native_potential_flow"
                        if trace["rows"][1]["cycle_component_l2"]
                        <= float(config["edge_space"]["algebra_tolerance"])
                        else "cycle_component_remains_after_one_complete_step"
                    ),
                }
            )
        cycle_activity_ladder = activity_amplitude_ladder(
            model,
            cycle_seed,
            projector=projector,
            incidence=incidence,
            config=config,
            require_cycle_membership=True,
        )
        stage_amplitude = abs(
            activity_amplitude_from_target(
                model, float(control["stage_trace_target_exponent"])
            )
        )
        positive_stage_trace = native_seed_stage_trace(
            model,
            stage_amplitude * cycle_seed,
            fixed_projector=projector,
            incidence=incidence,
            config=config,
        )
        negative_stage_trace = native_seed_stage_trace(
            model,
            -stage_amplitude * cycle_seed,
            fixed_projector=projector,
            incidence=incidence,
            config=config,
        )
        positive_first_conductance = next(
            row
            for row in positive_stage_trace["stages"]
            if row["stage"] == "after_first_conductance_formation"
        )
        negative_first_conductance = next(
            row
            for row in negative_stage_trace["stages"]
            if row["stage"] == "after_first_conductance_formation"
        )
        positive_first_current = next(
            row
            for row in positive_stage_trace["stages"]
            if row["stage"] == "after_first_native_current_reconstruction"
        )
        negative_first_current = next(
            row
            for row in negative_stage_trace["stages"]
            if row["stage"] == "after_first_native_current_reconstruction"
        )
        cycle_stage_trace_pair = {
            "target_activity_exponent": float(control["stage_trace_target_exponent"]),
            "derived_seed_amplitude": stage_amplitude,
            "positive": positive_stage_trace,
            "negative": negative_stage_trace,
            "first_transport_W_sign_even_linf": float(
                np.linalg.norm(
                    np.asarray(positive_first_conductance["W"])
                    - np.asarray(negative_first_conductance["W"]),
                    ord=np.inf,
                )
            ),
            "positive_first_transport_cycle_component_l2": positive_first_current[
                "phase_local_projection"
            ]["cycle_component_l2"],
            "negative_first_transport_cycle_component_l2": negative_first_current[
                "phase_local_projection"
            ]["cycle_component_l2"],
            "orientation_overwritten_at_first_transport": bool(
                positive_first_current["phase_local_projection"][
                    "cycle_component_l2"
                ]
                <= float(config["edge_space"]["algebra_tolerance"])
                and negative_first_current["phase_local_projection"][
                    "cycle_component_l2"
                ]
                <= float(config["edge_space"]["algebra_tolerance"])
            ),
            "both_manual_stage_traces_match_complete_step": bool(
                positive_stage_trace["manual_stage_trace_matches_complete_step"]
                and negative_stage_trace["manual_stage_trace_matches_complete_step"]
            ),
            "both_transport_kernel_traces_match_public_wrapper": bool(
                positive_stage_trace[
                    "both_transport_kernel_traces_match_public_wrapper"
                ]
                and negative_stage_trace[
                    "both_transport_kernel_traces_match_public_wrapper"
                ]
            ),
        }
    finite_activity_ladder = activity_amplitude_ladder(
        model,
        canonical_finite_seed(model),
        projector=projector,
        incidence=incidence,
        config=config,
        require_cycle_membership=False,
    )
    zero_symmetry = exact_zero_symmetry_audit(
        model,
        fixture_id,
        tolerance=float(control["state_symmetry_tolerance"]),
    )
    zero_post_current_maximum = max(
        (float(row["J_l2"]) for row in zero_row["rows"][1:]), default=0.0
    )
    if (
        zero_symmetry["full_orientation_relevant_symmetry_certified"]
        and zero_post_current_maximum <= float(control["current_zero_band"])
    ):
        zero_classification = "exact_zero_invariant"
    elif zero_post_current_maximum > float(control["current_zero_band"]):
        zero_classification = "baseline_potential_flow_generated_from_zero"
    else:
        zero_classification = (
            "nonsymmetric_state_zero_input_with_bounded_potential_flow_residual"
        )
    all_trajectory_rows = [
        *zero_row["rows"],
        *positive["rows"],
        *negative["rows"],
        *(beat for cycle in cycle_rows for beat in cycle["trajectory"]),
        *(
            row[key]
            for row in [*finite_activity_ladder, *cycle_activity_ladder]
            for key in ("positive_post_step", "negative_post_step")
        ),
    ]
    maximum_budget_error = max(
        (float(row["budget_error"]) for row in all_trajectory_rows), default=0.0
    )
    topology_and_events_clean = all(
        row["categorical_state"]
        == {
            **all_trajectory_rows[0]["categorical_state"],
            "current_sign_class": row["categorical_state"]["current_sign_class"],
        }
        for row in all_trajectory_rows
    )
    return {
        "branch_id": branch_id,
        "fixture_id": fixture_id,
        "edge_space": edge_audit,
        "assumption_statuses": {
            "A-CLOSED": "satisfied_closed_fixed_topology_no_boundary_drive",
            "A-MOBILITY": "satisfied_positive_native_conductance",
            "A-CONSERVE": (
                "satisfied_within_declared_budget_tolerance"
                if maximum_budget_error <= float(control["budget_tolerance"])
                else "violated_blocks_row"
            ),
            "A-UNIQUENESS": "connected_positive_conductance_potential_unique_modulo_gauge",
            "A-ORIENTATION": "sorted_edge_node_u_to_node_v_measurement_convention",
        },
        "exact_zero": zero_row["rows"],
        "exact_zero_symmetry_audit": zero_symmetry,
        "exact_zero_classification": zero_classification,
        "finite_positive": positive["rows"],
        "finite_negative": negative["rows"],
        "sign_even_magnitude_matched": {
            "post_first_step_W_linf_difference": float(
                np.linalg.norm(positive_w - negative_w, ord=np.inf)
            )
            if finite.size
            else 0.0,
            "post_first_step_J_linf_difference": post_current_delta,
            "conductance_write_sign_even": bool(
                not finite.size
                or np.linalg.norm(positive_w - negative_w, ord=np.inf)
                <= float(control["sign_even_conductance_tolerance"])
            ),
            "orientation_classification": (
                "input_orientation_erased_by_native_reconstruction"
                if post_current_delta <= float(control["current_zero_band"])
                else "post_reconstruction_orientation_difference_remains"
            ),
        },
        "cycle_seed_rows": cycle_rows,
        "finite_activity_amplitude_ladder": finite_activity_ladder,
        "cycle_activity_amplitude_ladder": cycle_activity_ladder,
        "cycle_seed_stage_trace_pair": cycle_stage_trace_pair,
        "maximum_budget_error": maximum_budget_error,
        "budget_conservation_passed": maximum_budget_error
        <= float(control["budget_tolerance"]),
        "topology_and_noncurrent_categorical_state_clean": topology_and_events_clean,
    }


def proper_divisors(period: int) -> list[int]:
    if period < 2:
        return []
    return [value for value in range(1, period) if period % value == 0]


def block_residual(left: GRC9V3, right: GRC9V3) -> dict[str, float]:
    return {
        "C": float(
            np.linalg.norm(coherence_vector(right) - coherence_vector(left), ord=np.inf)
        ),
        "W": float(
            np.linalg.norm(
                conductance_vector(right) - conductance_vector(left), ord=np.inf
            )
        ),
        "J": float(
            np.linalg.norm(current_vector(right) - current_vector(left), ord=np.inf)
        ),
    }


def normalized_block_residual(
    errors: dict[str, float], model: GRC9V3, floors: dict[str, float]
) -> float:
    scales = {
        "C": max(
            float(np.sqrt(np.mean(np.square(coherence_vector(model))))),
            float(floors["C"]),
        ),
        "W": max(
            float(np.sqrt(np.mean(np.square(conductance_vector(model))))),
            float(floors["W"]),
        ),
        "J": max(
            float(np.sqrt(np.mean(np.square(current_vector(model))))),
            float(floors["J"]),
        ),
    }
    return max(errors[key] / scales[key] for key in errors)


def advance(model: GRC9V3, steps: int) -> list[GRC9V3]:
    current = clone_model(model)
    trajectory = [clone_model(current)]
    for _ in range(steps):
        current.step()
        trajectory.append(clone_model(current))
    return trajectory


def return_residual(
    chart: BranchCoordinateChart, coordinate: NDArray[np.float64], period: int
) -> tuple[NDArray[np.float64], GRC9V3]:
    start = chart.decode_model(coordinate)
    end = clone_model(start)
    for _ in range(period):
        end.step()
    return chart.encode_model(end) - coordinate, end


def minimize_return_residual(
    chart: BranchCoordinateChart,
    seed: NDArray[np.float64],
    period: int,
    config: dict[str, Any],
) -> dict[str, Any]:
    search = config["orbit_search"]
    coordinate = np.asarray(seed, dtype=float).copy()
    history: list[dict[str, Any]] = []
    status = "maximum_iterations_reached"
    for iteration in range(int(search["maximum_solver_iterations"]) + 1):
        try:
            residual, _ = return_residual(chart, coordinate, period)
        except (ValueError, FloatingPointError):
            status = "invalid_coordinate_or_runtime_state"
            break
        norm = float(np.linalg.norm(residual, ord=np.inf))
        history.append({"iteration": iteration, "return_residual_linf": norm})
        if norm <= float(search["return_residual_tolerance"]):
            status = "converged_candidate"
            break
        if iteration == int(search["maximum_solver_iterations"]):
            break
        h = float(search["finite_difference_step"])
        jacobian = np.zeros((coordinate.size, coordinate.size), dtype=float)
        valid = True
        for column in range(coordinate.size):
            plus = coordinate.copy()
            minus = coordinate.copy()
            plus[column] += h
            minus[column] -= h
            try:
                plus_residual, _ = return_residual(chart, plus, period)
                minus_residual, _ = return_residual(chart, minus, period)
            except (ValueError, FloatingPointError):
                valid = False
                break
            jacobian[:, column] = (plus_residual - minus_residual) / (2.0 * h)
        if not valid:
            status = "finite_difference_probe_invalid"
            break
        condition = float(np.linalg.cond(jacobian))
        if not np.isfinite(condition) or condition > float(
            search["jacobian_condition_limit"]
        ):
            status = "return_jacobian_ill_conditioned_no_regularization"
            break
        update = np.linalg.lstsq(jacobian, -residual, rcond=None)[0]
        factor = 1.0
        accepted = False
        while factor >= float(search["minimum_backtracking_factor"]):
            proposal = coordinate + factor * update
            try:
                proposal_residual, _ = return_residual(chart, proposal, period)
            except (ValueError, FloatingPointError):
                factor *= 0.5
                continue
            if float(np.linalg.norm(proposal_residual, ord=np.inf)) < norm:
                coordinate = proposal
                accepted = True
                break
            factor *= 0.5
        if not accepted:
            status = "line_search_stagnated"
            break
    return {
        "status": status,
        "root_coordinate": coordinate.tolist(),
        "root_coordinate_sha256": semantic_digest(coordinate.tolist()),
        "history": history,
        "final_return_residual_linf": history[-1]["return_residual_linf"]
        if history
        else None,
    }


def evaluate_orbit(
    chart: BranchCoordinateChart,
    coordinate: NDArray[np.float64],
    period: int,
    config: dict[str, Any],
) -> dict[str, Any]:
    search = config["orbit_search"]
    zero_band = float(config["current_controls"]["current_zero_band"])
    start = chart.decode_model(coordinate)
    trajectory = advance(start, period)
    final = trajectory[-1]
    errors = block_residual(start, final)
    scaled = normalized_block_residual(
        errors, start, search["physical_block_scale_floors"]
    )
    signatures = [
        categorical_signature(model, current_zero_band=zero_band)
        for model in trajectory
    ]
    divisor_rows = []
    for divisor in proper_divisors(period):
        divisor_errors = block_residual(start, trajectory[divisor])
        divisor_rows.append(
            {
                "divisor": divisor,
                "block_linf": divisor_errors,
                "maximum_linf": max(divisor_errors.values(), default=0.0),
            }
        )
    state0 = start.get_state()
    statep = final.get_state()
    expected_admin = bool(
        statep.step_index == state0.step_index + period
        and abs(statep.time - (state0.time + period * float(start.get_params().dt)))
        <= 1e-12
    )
    physical_return = max(errors.values(), default=0.0) <= float(
        search["return_residual_tolerance"]
    )
    categorical_return = signatures[-1] == signatures[0]
    primitive = all(
        row["maximum_linf"] > float(search["primitive_divisor_separation_tolerance"])
        for row in divisor_rows
    )
    one_stratum = all(signature == signatures[0] for signature in signatures)
    rng_equal = statep.rng_state == state0.rng_state
    if physical_return and not primitive:
        classification = "rejected_proper_divisor_or_period_one_fixed_point"
    elif physical_return and not categorical_return:
        classification = "physical_projection_return"
    elif physical_return and categorical_return and not one_stratum:
        classification = "hybrid_or_categorical_return_orbit"
    elif physical_return and categorical_return and expected_admin and rng_equal:
        classification = "full_causal_state_return_orbit_candidate"
    else:
        classification = "not_a_return_orbit_within_declared_tolerance"
    return {
        "period": period,
        "block_return_residual_linf": errors,
        "maximum_physical_return_residual_linf": max(errors.values(), default=0.0),
        "normalized_physical_return_residual": scaled,
        "physical_return": physical_return,
        "categorical_return": categorical_return,
        "single_continuous_stratum": one_stratum,
        "administrative_advancement_expected_only": expected_admin,
        "rng_state_equal": rng_equal,
        "proper_divisor_rows": divisor_rows,
        "primitive_period_supported": primitive,
        "classification": classification,
        "trajectory_physical_projection": [
            {
                "beat": index,
                "C": coherence_vector(model).tolist(),
                "W": conductance_vector(model).tolist(),
                "J": current_vector(model).tolist(),
                "cycle_component_l2": float(
                    np.linalg.norm(
                        weighted_cycle_projector(
                            oriented_incidence(model)[0], conductance_vector(model)
                        )
                        @ current_vector(model)
                    )
                ),
                "categorical_signature_sha256": semantic_digest(signatures[index]),
            }
            for index, model in enumerate(trajectory)
        ],
    }


def recurrent_current_classification(
    evaluation: dict[str, Any], zero_band: float
) -> str:
    rows = evaluation["trajectory_physical_projection"]
    current_norms = [float(np.linalg.norm(row["J"])) for row in rows]
    cycle_norms = [float(row["cycle_component_l2"]) for row in rows]
    if max(current_norms, default=0.0) <= float(zero_band):
        return "zero_current_return_candidate"
    if max(cycle_norms, default=0.0) <= float(zero_band):
        return (
            "alternating_potential_flow_transport_orbit"
            if int(evaluation["period"]) == 2
            else "higher_period_synchronous_transport_orbit"
        )
    return "quasi_periodic_or_undetermined_recurrent_current"


def floquet_audit(
    chart: BranchCoordinateChart,
    coordinate: NDArray[np.float64],
    period: int,
    config: dict[str, Any],
) -> dict[str, Any]:
    """Differentiate only a full return that remains in one causal stratum."""

    admission = config["return_admission"]
    zero_band = float(config["current_controls"]["current_zero_band"])
    trajectory = advance(chart.decode_model(coordinate), period)
    signatures = [
        categorical_signature(model, current_zero_band=zero_band)
        for model in trajectory
    ]
    if not all(signature == signatures[0] for signature in signatures):
        return {
            "status": "blocked_hybrid_or_categorical_return",
            "ordinary_floquet_spectrum": None,
        }
    monodromy_rows = []
    for step_size in admission["floquet_finite_difference_steps"]:
        h = float(step_size)
        one_step_matrices = []
        blocked_probe = None
        for index, point in enumerate(trajectory[:-1]):
            local = BranchCoordinateChart.from_model(point, ("C", "W"))
            base = local.encode_model(point)
            matrix = np.zeros((base.size, base.size), dtype=float)
            point_signature = signatures[index]
            next_signature = signatures[index + 1]
            for column in range(base.size):
                plus = base.copy()
                minus = base.copy()
                plus[column] += h
                minus[column] -= h
                try:
                    plus_model = local.decode_model(plus)
                    minus_model = local.decode_model(minus)
                except ValueError:
                    blocked_probe = f"decode_blocked_at_point_{index}_column_{column}"
                    break
                if (
                    categorical_signature(plus_model, current_zero_band=zero_band)
                    != point_signature
                    or categorical_signature(minus_model, current_zero_band=zero_band)
                    != point_signature
                ):
                    blocked_probe = (
                        f"pre_step_stratum_crossing_at_point_{index}_column_{column}"
                    )
                    break
                plus_model.step()
                minus_model.step()
                if (
                    categorical_signature(plus_model, current_zero_band=zero_band)
                    != next_signature
                    or categorical_signature(minus_model, current_zero_band=zero_band)
                    != next_signature
                ):
                    blocked_probe = (
                        f"post_step_stratum_crossing_at_point_{index}_column_{column}"
                    )
                    break
                matrix[:, column] = (
                    local.encode_model(plus_model) - local.encode_model(minus_model)
                ) / (2.0 * h)
            if blocked_probe is not None:
                break
            one_step_matrices.append(matrix)
        if blocked_probe is not None:
            return {
                "status": "blocked_derivative_probe_left_continuous_stratum",
                "blocked_probe": blocked_probe,
                "ordinary_floquet_spectrum": None,
            }
        monodromy = np.eye(one_step_matrices[0].shape[0])
        for matrix in one_step_matrices:
            monodromy = matrix @ monodromy
        monodromy_rows.append({"step_size": h, "matrix": monodromy})
    adjacent_errors = []
    for left, right in zip(monodromy_rows, monodromy_rows[1:], strict=False):
        left_matrix = left["matrix"]
        right_matrix = right["matrix"]
        denominator = max(float(np.linalg.norm(right_matrix, ord=2)), 1e-12)
        adjacent_errors.append(
            float(np.linalg.norm(left_matrix - right_matrix, ord=2)) / denominator
        )
    converged = all(
        error <= float(admission["floquet_adjacent_matrix_relative_error_max"])
        for error in adjacent_errors
    )
    selected = monodromy_rows[-1]["matrix"]
    eigenvalues = np.linalg.eigvals(selected)
    return {
        "status": "admitted" if converged else "blocked_numerical_nonconvergence",
        "finite_difference_steps": [row["step_size"] for row in monodromy_rows],
        "adjacent_monodromy_relative_errors": adjacent_errors,
        "monodromy_matrix": selected.tolist() if converged else None,
        "ordinary_floquet_spectrum": (
            [
                {
                    "real": float(value.real),
                    "imag": float(value.imag),
                    "magnitude": float(abs(value)),
                }
                for value in eigenvalues
            ]
            if converged
            else None
        ),
        "conserved_budget_multiplier": {
            "status": "known_exact_budget_direction_quotiented_out_of_zero_sum_chart",
            "expected_multiplier": 1.0,
            "included_in_reported_monodromy": False,
        },
        "stable_orbit_supported": bool(
            converged and all(abs(value) < 1.0 - 1e-8 for value in eigenvalues)
        ),
    }


def deterministic_seed_coordinate(
    chart: BranchCoordinateChart,
    candidate_index: int,
    period: int,
    config: dict[str, Any],
) -> tuple[NDArray[np.float64], dict[str, Any]]:
    search = config["orbit_search"]
    base_model = GRC9V3.from_state(deepcopy(chart.base_state), chart.params)
    base = chart.encode_model(base_model)
    replicate = candidate_index // int(config["source_scope"]["expected_branch_count"])
    c_amplitudes = search["coherence_perturbation_amplitudes"]
    w_amplitudes = search["relative_conductance_perturbation_amplitudes"]
    c_amplitude = float(c_amplitudes[replicate % len(c_amplitudes)])
    w_amplitude = float(w_amplitudes[replicate % len(w_amplitudes)])
    rng = np.random.default_rng(int(search["seed"]) + period * 100000 + candidate_index)
    coordinate = base.copy()
    c_start, c_end = chart.block_slices["C"]
    if c_end > c_start and c_amplitude:
        direction = normalized_direction(rng.normal(size=c_end - c_start))
        c_scale = max(float(np.sqrt(np.mean(np.square(chart.base_coherence)))), 1.0)
        coordinate[c_start:c_end] += c_amplitude * c_scale * direction
    w_start, w_end = chart.block_slices["W"]
    if w_end > w_start and w_amplitude:
        signs = normalized_direction(rng.normal(size=w_end - w_start))
        coordinate[w_start:w_end] *= 1.0 + w_amplitude * signs
    return coordinate, {
        "replicate_index": replicate,
        "coherence_perturbation_amplitude": c_amplitude,
        "relative_conductance_perturbation_amplitude": w_amplitude,
        "seed_coordinate": coordinate.tolist(),
        "seed_coordinate_sha256": semantic_digest(coordinate.tolist()),
    }


def multiplier_continuation_audit(
    grv3_payload: dict[str, Any], config: dict[str, Any]
) -> dict[str, Any]:
    policy = config["multiplier_continuation"]
    rows = []
    for branch in grv3_payload["branches"]:
        for coordinate, audit in branch[
            "coordinate_stratum_and_jacobian_audits"
        ].items():
            if audit.get("square_transition_jacobian_status") != "admitted":
                continue
            modes = audit["temporal_mode_diagnostics"]["modes"]
            values = [
                complex(mode["eigenvalue"]["real"], mode["eigenvalue"]["imag"])
                for mode in modes
            ]
            minus_one_distance = min(
                (abs(value + 1.0) for value in values), default=float("inf")
            )
            eligible_complex_values = [
                value
                for value in values
                if abs(value.imag)
                >= float(policy["minimum_complex_imaginary_magnitude"])
            ]
            complex_unit_distance = (
                min(abs(abs(value) - 1.0) for value in eligible_complex_values)
                if eligible_complex_values
                else None
            )
            rows.append(
                {
                    "branch_id": branch["branch_id"],
                    "fixture_id": branch["fixture_id"],
                    "coordinate": coordinate,
                    "multipliers": [
                        {
                            "real": value.real,
                            "imag": value.imag,
                            "magnitude": abs(value),
                        }
                        for value in values
                    ],
                    "minimum_minus_one_distance": minus_one_distance,
                    "minimum_complex_unit_circle_distance": complex_unit_distance,
                    "complex_multiplier_eligible_count": len(eligible_complex_values),
                    "minus_one_continuation_candidate": minus_one_distance
                    <= float(policy["minus_one_candidate_distance"]),
                    "complex_unit_circle_continuation_candidate": (
                        complex_unit_distance is not None
                        and complex_unit_distance
                        <= float(policy["complex_unit_circle_magnitude_distance"])
                    ),
                }
            )
    return {
        "source": policy["source"],
        "matrix_row_count": len(rows),
        "minus_one_candidate_count": sum(
            row["minus_one_continuation_candidate"] for row in rows
        ),
        "complex_unit_circle_candidate_count": sum(
            row["complex_unit_circle_continuation_candidate"] for row in rows
        ),
        "absence_interpretation": "no_local_multiplier_continuation_seed_not_global_orbit_nonexistence",
        "rows": rows,
    }


def held_out_replay(
    selected: list[dict[str, Any]],
    charts: dict[str, BranchCoordinateChart],
    config: dict[str, Any],
) -> dict[str, Any]:
    if not selected:
        return {
            "status": "not_applicable_no_selected_return_orbits",
            "selected_orbit_count": 0,
            "rows": [],
        }
    rows = []
    for selected_row in selected:
        chart = charts[selected_row["branch_id"]]
        coordinate = np.asarray(selected_row["root_coordinate"], dtype=float)
        original = chart.decode_model(coordinate)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "orbit_start.json"
            original.save(str(path))
            restored = GRC9V3.load(str(path))
        first = advance(original, int(selected_row["period"]))[-1]
        second = advance(restored, int(selected_row["period"]))[-1]
        replay_error = block_residual(first, second)
        rows.append(
            {
                "orbit_id": selected_row["orbit_id"],
                "snapshot_load_replay_block_linf": replay_error,
                "snapshot_load_replay_passed": max(replay_error.values(), default=0.0)
                <= float(config["orbit_search"]["return_residual_tolerance"]),
            }
        )
    return {
        "status": "passed"
        if all(row["snapshot_load_replay_passed"] for row in rows)
        else "failed",
        "selected_orbit_count": len(selected),
        "rows": rows,
    }
