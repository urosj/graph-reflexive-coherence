"""GRV5 clone-first preparation, persistence, and matched-probe methods."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
import math
import sys
from typing import Any, Iterable

import numpy as np

from artifact_io import REPO_ROOT, semantic_digest
from tangent_basis import zero_sum_basis

SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from pygrc.models import GRC9V3  # noqa: E402
from pygrc.models.grc_9_v3_runtime import (  # noqa: E402
    compute_flux,
    compute_potential,
)


def clone_model(model: GRC9V3) -> GRC9V3:
    return GRC9V3.from_state(
        deepcopy(model.get_state()), dict(model.get_params().raw_config)
    )


def node_order(model: GRC9V3) -> tuple[int, ...]:
    return tuple(sorted(model.get_state().topology.iter_live_node_ids()))


def edge_order(model: GRC9V3) -> tuple[int, ...]:
    return tuple(sorted(model.get_state().topology.iter_live_edge_ids()))


def canonical_edge_direction(model: GRC9V3) -> np.ndarray:
    edges = edge_order(model)
    direction = np.asarray(
        [1.0 if index % 2 == 0 else -1.0 for index in range(len(edges))],
        dtype=float,
    )
    norm = float(np.linalg.norm(direction))
    if norm == 0.0:
        raise ValueError("GRV5 requires at least one live edge")
    return direction / norm


def coherence_vector(model: GRC9V3) -> np.ndarray:
    state = model.get_state()
    return np.asarray(
        [float(state.nodes[node_id].coherence) for node_id in node_order(model)],
        dtype=float,
    )


def conductance_vector(model: GRC9V3) -> np.ndarray:
    state = model.get_state()
    return np.asarray(
        [float(state.base_conductance[edge_id]) for edge_id in edge_order(model)],
        dtype=float,
    )


def current_vector(model: GRC9V3) -> np.ndarray:
    state = model.get_state()
    return np.asarray(
        [float(state.port_edges[edge_id].flux_uv) for edge_id in edge_order(model)],
        dtype=float,
    )


def state_projection(model: GRC9V3) -> dict[str, Any]:
    state = model.get_state()
    coherence = coherence_vector(model)
    conductance = conductance_vector(model)
    current = current_vector(model)
    result = {
        "C": coherence.tolist(),
        "W": conductance.tolist(),
        "J": current.tolist(),
        "step_index": int(state.step_index),
        "time": float(state.time),
        "budget": float(np.sum(coherence)),
        "budget_target": float(state.budget_target),
        "remainder": float(state.remainder),
        "minimum_C": float(np.min(coherence)),
        "minimum_W": float(np.min(conductance)),
        "J_l2": float(np.linalg.norm(current)),
        "rng_state_sha256": semantic_digest(state.rng_state),
        "params_identity": state.params_identity,
        "topology_nodes": list(sorted(state.topology.iter_live_node_ids())),
        "topology_edges": list(sorted(state.topology.iter_live_edge_ids())),
        "event_count": len(state.event_log),
    }
    result["snapshot_semantic_sha256"] = semantic_digest(model.snapshot())
    return result


def probe_carrier_projection(model: GRC9V3) -> dict[str, Any]:
    payload = {
        "C": coherence_vector(model).tolist(),
        "W": conductance_vector(model).tolist(),
        "J": current_vector(model).tolist(),
    }
    return {**payload, "carrier_projection_sha256": semantic_digest(payload)}


def physical_projection_linf(left: GRC9V3, right: GRC9V3) -> float:
    blocks = (
        coherence_vector(left) - coherence_vector(right),
        conductance_vector(left) - conductance_vector(right),
        current_vector(left) - current_vector(right),
    )
    return max(
        (float(np.linalg.norm(block, ord=np.inf)) for block in blocks),
        default=0.0,
    )


def categorical_projection(model: GRC9V3) -> dict[str, Any]:
    state = model.get_state()
    current_sign = {}
    for edge_id, value in zip(edge_order(model), current_vector(model), strict=True):
        current_sign[str(edge_id)] = (
            "zero"
            if abs(float(value)) <= 1e-10
            else ("positive" if value > 0.0 else "negative")
        )
    return {
        "topology_nodes": list(sorted(state.topology.iter_live_node_ids())),
        "topology_edges": list(sorted(state.topology.iter_live_edge_ids())),
        "sink_set": list(sorted(state.sink_set)),
        "basins": {
            str(key): list(sorted(value)) for key, value in sorted(state.basins.items())
        },
        "event_kinds": [event.kind for event in state.event_log],
        "current_sign_class": current_sign,
    }


def _set_conductance(model: GRC9V3, values: Iterable[float]) -> GRC9V3:
    clone = clone_model(model)
    state = deepcopy(clone.get_state())
    for edge_id, value in zip(edge_order(clone), values, strict=True):
        if float(value) <= 0.0:
            raise ValueError("conductance intervention must remain positive")
        state.base_conductance[edge_id] = float(value)
        state.port_edges[edge_id] = replace(
            state.port_edges[edge_id], conductance=float(value)
        )
    clone.set_state(state)
    return clone


def conductance_surface_consistency(model: GRC9V3) -> dict[str, Any]:
    state = model.get_state()
    base = conductance_vector(model)
    duplicate = np.asarray(
        [float(state.port_edges[edge_id].conductance) for edge_id in edge_order(model)],
        dtype=float,
    )
    delta = float(np.linalg.norm(base - duplicate, ord=np.inf))
    return {
        "authoritative_surface": "base_conductance",
        "duplicate_surface": "port_edges.*.conductance",
        "base_conductance": base.tolist(),
        "port_edge_conductance": duplicate.tolist(),
        "surface_consistency_linf": delta,
        "surfaces_consistent": delta == 0.0,
    }


def direct_conductance_intervention(
    model: GRC9V3, *, signed_relative_amplitude: float
) -> GRC9V3:
    base = conductance_vector(model)
    direction = canonical_edge_direction(model)
    return _set_conductance(
        model, base * (1.0 + float(signed_relative_amplitude) * direction)
    )


def old_current_intervention(model: GRC9V3, *, amplitude: float) -> GRC9V3:
    clone = clone_model(model)
    state = deepcopy(clone.get_state())
    values = float(amplitude) * canonical_edge_direction(clone)
    for edge_id, value in zip(edge_order(clone), values, strict=True):
        state.port_edges[edge_id] = replace(
            state.port_edges[edge_id], flux_uv=float(value)
        )
    clone.set_state(state)
    return clone


def activity_write_stage(model: GRC9V3, *, amplitude: float) -> GRC9V3:
    """Execute the exact first native differential/transport stage after old-J input."""

    prepared = old_current_intervention(model, amplitude=amplitude)
    prepared.rebuild_differential_state()
    prepared.rebuild_transport_state()
    return prepared


def activity_write_stage_trace(model: GRC9V3, *, amplitude: float) -> dict[str, Any]:
    """Record the exact public stage boundaries used to identify the write path."""

    after_input = old_current_intervention(model, amplitude=amplitude)
    after_first_transport = clone_model(after_input)
    after_first_transport.rebuild_differential_state()
    after_first_transport.rebuild_transport_state()

    before_continuity = clone_model(after_input)
    before_continuity.rebuild_differential_state()
    before_continuity.rebuild_transport_state()
    before_continuity.rebuild_differential_state()
    before_continuity.rebuild_identity_state()
    before_continuity.apply_hybrid_sparks()
    before_continuity.rebuild_choice_state()
    before_continuity.apply_growth()
    before_continuity.apply_boundary_behavior()
    after_continuity = clone_model(before_continuity)
    after_continuity.apply_continuity()

    after_complete = clone_model(after_input)
    after_complete.step()
    return {
        "before_preparation": state_projection(model),
        "after_direct_old_current_input": state_projection(after_input),
        "after_first_native_transport_write": state_projection(after_first_transport),
        "before_continuity": state_projection(before_continuity),
        "after_continuity_before_budget": state_projection(after_continuity),
        "after_complete_preparation_step": state_projection(after_complete),
        "after_forming_intervention_stopped": state_projection(after_complete),
    }


def coherence_intervention(model: GRC9V3, *, amplitude: float) -> GRC9V3:
    clone = clone_model(model)
    state = deepcopy(clone.get_state())
    nodes = node_order(clone)
    basis = zero_sum_basis(len(nodes))
    if basis.shape[1] == 0:
        raise ValueError("coherence probe requires a nontrivial tangent")
    values = coherence_vector(clone) + float(amplitude) * basis[:, 0]
    if np.any(values <= 0.0):
        raise ValueError("coherence probe left the positive interior")
    for node_id, value in zip(nodes, values, strict=True):
        state.nodes[node_id] = replace(state.nodes[node_id], coherence=float(value))
    clone.set_state(state)
    return clone


def match_C_and_J_preserving_W(
    carrier_a: GRC9V3, carrier_b: GRC9V3
) -> tuple[GRC9V3, GRC9V3]:
    if node_order(carrier_a) != node_order(carrier_b) or edge_order(
        carrier_a
    ) != edge_order(carrier_b):
        raise ValueError("carrier pair topology/order mismatch")
    common_c = 0.5 * (coherence_vector(carrier_a) + coherence_vector(carrier_b))
    common_j = 0.5 * (current_vector(carrier_a) + current_vector(carrier_b))
    result = []
    for source in (carrier_a, carrier_b):
        clone = clone_model(source)
        state = deepcopy(clone.get_state())
        for node_id, value in zip(node_order(clone), common_c, strict=True):
            state.nodes[node_id] = replace(state.nodes[node_id], coherence=float(value))
        for edge_id, value in zip(edge_order(clone), common_j, strict=True):
            state.port_edges[edge_id] = replace(
                state.port_edges[edge_id], flux_uv=float(value)
            )
        clone.set_state(state)
        result.append(clone)
    return result[0], result[1]


def reset_carrier(
    carrier_a: GRC9V3, carrier_b: GRC9V3, baseline: GRC9V3
) -> tuple[GRC9V3, GRC9V3]:
    values = conductance_vector(baseline)
    return _set_conductance(carrier_a, values), _set_conductance(carrier_b, values)


def swap_carrier(carrier_a: GRC9V3, carrier_b: GRC9V3) -> tuple[GRC9V3, GRC9V3]:
    return (
        _set_conductance(carrier_a, conductance_vector(carrier_b)),
        _set_conductance(carrier_b, conductance_vector(carrier_a)),
    )


def equal_carrier_preserving_reached_state(
    state_a: GRC9V3, state_b: GRC9V3
) -> tuple[GRC9V3, GRC9V3]:
    common_w = 0.5 * (conductance_vector(state_a) + conductance_vector(state_b))
    return _set_conductance(state_a, common_w), _set_conductance(state_b, common_w)


def shuffle_carrier_pattern(
    state_a: GRC9V3, state_b: GRC9V3, baseline: GRC9V3
) -> tuple[GRC9V3, GRC9V3] | None:
    if len(edge_order(baseline)) < 2:
        return None
    base = conductance_vector(baseline)
    first = base + np.roll(conductance_vector(state_a) - base, 1)
    second = base + np.roll(conductance_vector(state_b) - base, 1)
    if np.any(first <= 0.0) or np.any(second <= 0.0):
        return None
    return _set_conductance(state_a, first), _set_conductance(state_b, second)


def activity_amplitude_from_target(model: GRC9V3, target_exponent: float) -> float:
    gamma = float(model.get_params().evolution.get("gamma", 0.0))
    if gamma <= 0.0:
        raise ValueError("activity-mediated conductance write requires gamma > 0")
    sign = -1.0 if target_exponent < 0.0 else 1.0
    return sign * math.sqrt(2.0 * abs(float(target_exponent)) / gamma)


def constitutive_consistency_audit(
    model: GRC9V3, *, tolerance: float
) -> dict[str, Any]:
    declared = conductance_vector(model)
    rebuilt = clone_model(model)
    rebuilt.rebuild_differential_state()
    rebuilt.rebuild_transport_state()
    reconstructed = conductance_vector(rebuilt)
    delta = float(np.linalg.norm(declared - reconstructed, ord=np.inf))
    return {
        "declared_W": declared.tolist(),
        "reconstructed_W": reconstructed.tolist(),
        "W_reconstruction_linf": delta,
        "tolerance": float(tolerance),
        "constitutively_consistent": delta <= float(tolerance),
    }


def matching_audit(
    source_a: GRC9V3,
    source_b: GRC9V3,
    matched_a: GRC9V3,
    matched_b: GRC9V3,
    *,
    tolerance: float,
) -> dict[str, Any]:
    w_before = conductance_vector(source_a) - conductance_vector(source_b)
    w_after = conductance_vector(matched_a) - conductance_vector(matched_b)
    pair_noncarrier_errors = {
        "C_linf": float(
            np.linalg.norm(
                coherence_vector(matched_a) - coherence_vector(matched_b), ord=np.inf
            )
        ),
        "J_linf": float(
            np.linalg.norm(
                current_vector(matched_a) - current_vector(matched_b), ord=np.inf
            )
        ),
    }
    source_to_matched_preservation = []
    for source, matched in ((source_a, matched_a), (source_b, matched_b)):
        source_state = source.get_state()
        matched_state = matched.get_state()
        source_categorical = categorical_projection(source)
        matched_categorical = categorical_projection(matched)
        source_structural = {
            key: value
            for key, value in source_categorical.items()
            if key != "current_sign_class"
        }
        matched_structural = {
            key: value
            for key, value in matched_categorical.items()
            if key != "current_sign_class"
        }
        source_to_matched_preservation.append(
            {
                "W_linf": float(
                    np.linalg.norm(
                        conductance_vector(source) - conductance_vector(matched),
                        ord=np.inf,
                    )
                ),
                "step_index_equal": source_state.step_index == matched_state.step_index,
                "time_equal": source_state.time == matched_state.time,
                "budget_target_equal": source_state.budget_target
                == matched_state.budget_target,
                "remainder_equal": source_state.remainder == matched_state.remainder,
                "rng_state_equal": semantic_digest(source_state.rng_state)
                == semantic_digest(matched_state.rng_state),
                "params_identity_equal": source_state.params_identity
                == matched_state.params_identity,
                "structural_categorical_projection_equal": source_structural
                == matched_structural,
                "current_sign_change_is_declared_J_match_effect": True,
                "authoritative_surface_audit": conductance_surface_consistency(matched),
            }
        )
    pair_states = (matched_a.get_state(), matched_b.get_state())
    administrative_pair_equal = {
        "step_index": pair_states[0].step_index == pair_states[1].step_index,
        "time": pair_states[0].time == pair_states[1].time,
        "budget_target": pair_states[0].budget_target == pair_states[1].budget_target,
        "remainder": pair_states[0].remainder == pair_states[1].remainder,
        "rng_state": semantic_digest(pair_states[0].rng_state)
        == semantic_digest(pair_states[1].rng_state),
        "params_identity": pair_states[0].params_identity
        == pair_states[1].params_identity,
        "categorical_projection": categorical_projection(matched_a)
        == categorical_projection(matched_b),
    }
    carrier_error = float(np.linalg.norm(w_before - w_after, ord=np.inf))
    passed = bool(
        max(pair_noncarrier_errors.values(), default=0.0) <= tolerance
        and carrier_error <= tolerance
        and all(administrative_pair_equal.values())
        and all(
            row["W_linf"] <= tolerance
            and row["step_index_equal"]
            and row["time_equal"]
            and row["budget_target_equal"]
            and row["remainder_equal"]
            and row["rng_state_equal"]
            and row["params_identity_equal"]
            and row["structural_categorical_projection_equal"]
            and row["authoritative_surface_audit"]["surfaces_consistent"]
            for row in source_to_matched_preservation
        )
    )
    return {
        "target": "W_only_mediation",
        "pair_noncarrier_errors": pair_noncarrier_errors,
        "carrier_difference_preservation_linf": carrier_error,
        "source_to_matched_preservation": source_to_matched_preservation,
        "administrative_and_categorical_pair_equal": administrative_pair_equal,
        "opaque_derived_cache_policy": "not_promoted_beyond_GRV3_admitted_C_W_J_coordinate_and_categorical_stratum",
        "W_only_null_cannot_reject_joint_C_W_or_transferred_carrier": True,
        "passed": passed,
    }


def pair_separation(
    model_a: GRC9V3, model_b: GRC9V3, *, branch_scales: dict[str, float]
) -> dict[str, Any]:
    deltas = {
        "C": coherence_vector(model_a) - coherence_vector(model_b),
        "W": conductance_vector(model_a) - conductance_vector(model_b),
        "J": current_vector(model_a) - current_vector(model_b),
    }
    block_norms = {key: float(np.linalg.norm(value)) for key, value in deltas.items()}
    scaled = {
        key: block_norms[key] / max(float(branch_scales[key]), 1e-12) for key in deltas
    }
    state_a = model_a.get_state()
    state_b = model_b.get_state()
    return {
        "block_vectors": {key: value.tolist() for key, value in deltas.items()},
        "block_l2": block_norms,
        "block_scaled_l2": scaled,
        "joint_block_scaled_l2": float(np.linalg.norm(list(scaled.values()))),
        "budget_difference": float(
            abs(np.sum(coherence_vector(model_a)) - np.sum(coherence_vector(model_b)))
        ),
        "topology_equal": (
            list(state_a.topology.iter_live_node_ids())
            == list(state_b.topology.iter_live_node_ids())
            and list(state_a.topology.iter_live_edge_ids())
            == list(state_b.topology.iter_live_edge_ids())
        ),
        "event_count_pair": [len(state_a.event_log), len(state_b.event_log)],
    }


def carrier_alignment(
    initial: dict[str, Any],
    current: dict[str, Any],
    *,
    branch_scales: dict[str, float],
) -> dict[str, Any]:
    initial_blocks = {
        key: np.asarray(initial["block_vectors"][key], dtype=float)
        / max(float(branch_scales[key]), 1e-12)
        for key in ("C", "W", "J")
    }
    current_blocks = {
        key: np.asarray(current["block_vectors"][key], dtype=float)
        / max(float(branch_scales[key]), 1e-12)
        for key in ("C", "W", "J")
    }
    initial_vector = np.concatenate(tuple(initial_blocks.values()))
    current_vector_value = np.concatenate(tuple(current_blocks.values()))
    denominator = float(initial_vector @ initial_vector)
    signed_projection = (
        float(current_vector_value @ initial_vector) / denominator
        if denominator > 0.0
        else 0.0
    )
    projected = signed_projection * initial_vector
    orthogonal = current_vector_value - projected
    current_norm = float(np.linalg.norm(current_vector_value))
    return {
        "coordinate": "branch_scaled_joint_C_W_J",
        "signed_projection_on_prepared_pattern": signed_projection,
        "carrier_correlation": (
            float(current_vector_value @ initial_vector)
            / max(
                float(np.linalg.norm(current_vector_value))
                * float(np.linalg.norm(initial_vector)),
                1e-30,
            )
        ),
        "orthogonal_leakage_l2": float(np.linalg.norm(orthogonal)),
        "orthogonal_leakage_fraction": float(np.linalg.norm(orthogonal))
        / max(current_norm, 1e-30),
        "block_vectors_branch_scaled": {
            key: value.tolist() for key, value in current_blocks.items()
        },
    }


def run_probe(
    model: GRC9V3,
    *,
    lane: str,
    probe_kind: str,
    amplitude: float,
) -> dict[str, Any]:
    before_projection = probe_carrier_projection(model)
    if probe_kind == "coherence_or_potential_probe":
        prepared = coherence_intervention(model, amplitude=amplitude)
    elif probe_kind == "old_current_state_injection":
        prepared = old_current_intervention(model, amplitude=amplitude)
    elif probe_kind == "external_current_like_analytical_probe":
        if lane != "frozen_W_probe":
            raise ValueError(
                "external analytical probe is only defined in frozen_W lane"
            )
        direction = canonical_edge_direction(model)
        eta = float(model.get_params().evolution.get("eta", 1.0))
        response = -eta * conductance_vector(model) * float(amplitude) * direction
        return {
            "response": response,
            "readout_stage": "analytical_fixed_W_edge_covector_response",
            "causal_path": "external_edge_covector_times_fixed_W_to_analytical_J",
            "runtime_executed": False,
            "substrate_class": "analysis_only",
            "carrier_before_probe": before_projection,
            "carrier_after_readout": before_projection,
            "carrier_change_during_readout": {
                "C_l2": 0.0,
                "W_l2": 0.0,
                "J_l2": 0.0,
            },
        }
    else:
        raise ValueError(f"unsupported probe kind {probe_kind!r}")

    if lane == "native_full_step_probe":
        prepared.step()
        stage = "post_complete_GRC9V3_step_flux"
        path = "probe_to_complete_native_recurrence_to_post_step_J"
        substrate_class = "substrate_exact"
    elif lane == "native_immediate_transport_stage_probe":
        prepared.rebuild_differential_state()
        prepared.rebuild_transport_state()
        stage = "post_first_native_transport_reconstruction_flux"
        path = "probe_to_differential_rebuild_to_transport_rebuild_to_J"
        substrate_class = "substrate_exact_stage_local"
    elif lane == "frozen_W_probe":
        prepared.rebuild_differential_state()
        evolution = prepared.get_params().evolution
        compute_potential(prepared.get_state(), evolution=evolution)
        compute_flux(prepared.get_state(), evolution=evolution)
        stage = "post_fixed_W_potential_and_flux"
        path = "probe_to_fixed_W_potential_to_fixed_W_J"
        substrate_class = "substrate_reduced"
    else:
        raise ValueError(f"unsupported probe lane {lane!r}")
    after_projection = probe_carrier_projection(prepared)
    return {
        "response": current_vector(prepared),
        "readout_stage": stage,
        "causal_path": path,
        "runtime_executed": True,
        "substrate_class": substrate_class,
        "carrier_before_probe": before_projection,
        "carrier_after_readout": after_projection,
        "carrier_change_during_readout": {
            block: float(
                np.linalg.norm(
                    np.asarray(after_projection[block], dtype=float)
                    - np.asarray(before_projection[block], dtype=float)
                )
            )
            for block in ("C", "W", "J")
        },
    }


def difference_in_differences(
    carrier_a: GRC9V3,
    carrier_b: GRC9V3,
    *,
    lane: str,
    probe_kind: str,
    amplitude: float,
) -> dict[str, Any]:
    a_zero = run_probe(carrier_a, lane=lane, probe_kind=probe_kind, amplitude=0.0)
    b_zero = run_probe(carrier_b, lane=lane, probe_kind=probe_kind, amplitude=0.0)
    a_probe = run_probe(
        carrier_a, lane=lane, probe_kind=probe_kind, amplitude=amplitude
    )
    b_probe = run_probe(
        carrier_b, lane=lane, probe_kind=probe_kind, amplitude=amplitude
    )
    delta_a = a_probe["response"] - a_zero["response"]
    delta_b = b_probe["response"] - b_zero["response"]
    interaction = delta_a - delta_b
    return {
        "amplitude": float(amplitude),
        "baseline_a": a_zero["response"].tolist(),
        "baseline_b": b_zero["response"].tolist(),
        "baseline_difference_l2": float(
            np.linalg.norm(a_zero["response"] - b_zero["response"])
        ),
        "increment_a": delta_a.tolist(),
        "increment_b": delta_b.tolist(),
        "difference_in_differences": interaction.tolist(),
        "difference_in_differences_l2": float(np.linalg.norm(interaction)),
        "readout_stage": a_probe["readout_stage"],
        "causal_path": a_probe["causal_path"],
        "substrate_class": a_probe["substrate_class"],
        "cell_receipts": {
            "a_zero": _probe_receipt(a_zero),
            "a_probe": _probe_receipt(a_probe),
            "b_zero": _probe_receipt(b_zero),
            "b_probe": _probe_receipt(b_probe),
        },
    }


def _probe_receipt(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "response": result["response"].tolist(),
        "readout_stage": result["readout_stage"],
        "causal_path": result["causal_path"],
        "substrate_class": result["substrate_class"],
        "carrier_before_probe": result["carrier_before_probe"],
        "carrier_after_readout": result["carrier_after_readout"],
        "carrier_change_during_readout": result["carrier_change_during_readout"],
    }


def signed_sweep_fit(rows: list[dict[str, Any]], *, tolerance: float) -> dict[str, Any]:
    nonzero = [row for row in rows if row["amplitude"] != 0.0]
    amplitudes = np.asarray([row["amplitude"] for row in nonzero], dtype=float)
    responses = np.asarray(
        [row["difference_in_differences"] for row in nonzero], dtype=float
    )
    denominator = float(amplitudes @ amplitudes)
    slope = (amplitudes[:, None] * responses).sum(axis=0) / denominator
    residual = responses - amplitudes[:, None] * slope
    relative = float(np.linalg.norm(residual) / max(np.linalg.norm(responses), 1e-15))
    by_coordinate = {
        float(row.get("signed_input_coordinate", row["amplitude"])): np.asarray(
            row["difference_in_differences"], dtype=float
        )
        for row in rows
    }
    odd_even = []
    for amplitude in sorted(value for value in by_coordinate if value > 0.0):
        if -amplitude not in by_coordinate:
            continue
        positive = by_coordinate[amplitude]
        negative = by_coordinate[-amplitude]
        odd = 0.5 * (positive - negative)
        even = 0.5 * (positive + negative)
        odd_even.append(
            {
                "absolute_coordinate": amplitude,
                "odd_component": odd.tolist(),
                "odd_component_l2": float(np.linalg.norm(odd)),
                "even_component": even.tolist(),
                "even_component_l2": float(np.linalg.norm(even)),
            }
        )
    return {
        "slope": slope.tolist(),
        "relative_residual": relative,
        "maximum_allowed": float(tolerance),
        "linear_fit_passed": relative <= float(tolerance),
        "odd_even_decomposition": odd_even,
    }
