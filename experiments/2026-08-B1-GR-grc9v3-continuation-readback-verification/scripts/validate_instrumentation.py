"""Execute GRV1 instrumentation and source-fidelity validation."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import fields
import json
from pathlib import Path
import sys
import tempfile
from typing import Any, Callable

from artifact_io import (
    EXPERIMENT_ROOT,
    REPO_ROOT,
    artifact_envelope,
    file_manifest,
    git,
    read_json,
    semantic_digest,
    sha256_file,
    write_json,
)

SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from pygrc.models import GRC9V3, PortEdge  # noqa: E402
from pygrc.models.grc_9_v3_state import GRC9V3State  # noqa: E402

from gate_receipts import (  # noqa: E402
    finalize_receipt,
    validate_acceptance_anchor,
    validate_receipt,
)
from interventions import apply_clone_intervention  # noqa: E402
from state_codec import canonical_clone, exact_deep_clone  # noqa: E402


COMMAND = (
    ".venv/bin/python "
    "experiments/2026-08-B1-GR-grc9v3-continuation-readback-verification/"
    "scripts/run_all.py --gate GRV1"
)
SPECIFICATION_ID = "b1_grc9v3_continuation_readback_verification_v3_4_1"
GRV0_RESULT_REVISION = "97a9a6bf9cd20ca6c1adcc0feee26712df9569fb"
GRV0_RECEIPT_SHA256 = "a583d763b2d5e72af3f3e2ad5401aca8c143eff1aa73427404c2f8286e1ed9df"

EXPECTED_STEP_ORDER = (
    "compute_row_basis_gradient_pre_flux",
    "compute_signed_hessian_row_basis_pre_flux",
    "compute_net_flux_summary_pre_flux",
    "compute_node_tensors",
    "compute_base_conductance",
    "compute_edge_labels_pre_flux",
    "compute_potential",
    "compute_flux",
    "compute_edge_labels_post_flux",
    "refresh_differential_summary_post_flux",
    "detect_flux_topology_identities",
    "validate_geometric_basin_seeds",
    "compute_effective_basin_masses",
    "detect_hybrid_spark_candidates",
    "apply_mechanical_expansion",
    "refresh_after_expansion",
    "evaluate_child_basin_stabilization",
    "register_completed_hybrid_sparks",
    "update_hierarchy",
    "update_choice_collapse_learning",
    "apply_growth",
    "apply_boundary_behavior",
    "apply_continuity",
    "enforce_quadrature_budget",
    "refresh_runtime_state_final",
    "refresh_or_invalidate_coarse_cache",
    "compute_observables",
)

EXPECTED_HIGH_LEVEL_CALL_ORDER = (
    "rebuild_differential_state",
    "rebuild_transport_state",
    "rebuild_differential_state",
    "rebuild_identity_state",
    "apply_hybrid_spark_stages",
    "rebuild_choice_state",
    "apply_growth",
    "apply_boundary_behavior",
    "apply_continuity",
    "enforce_quadrature_budget",
    "rebuild_differential_state",
    "rebuild_transport_state",
    "rebuild_differential_state",
    "rebuild_identity_state",
    "refresh_coarse_cache",
    "compute_observables",
)

LOAD_BEARING_PATHS = (
    "src/pygrc/core/serialization.py",
    "src/pygrc/core/storage.py",
    "src/pygrc/core/types.py",
    "src/pygrc/models/grc_9_ports.py",
    "src/pygrc/models/grc_9_state.py",
    "src/pygrc/models/grc_9_v3.py",
    "src/pygrc/models/grc_9_v3_choice.py",
    "src/pygrc/models/grc_9_v3_runtime.py",
    "src/pygrc/models/grc_9_v3_sparks.py",
    "src/pygrc/models/grc_9_v3_state.py",
    "src/pygrc/models/grc_v3_differential.py",
)


class TracingGRC9V3(GRC9V3):
    """Observe public step stages without changing runtime state transitions."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.instrumentation_calls: list[str] = []

    def _record(self, name: str, operation: Callable[[], Any]) -> Any:
        self.instrumentation_calls.append(name)
        return operation()

    def rebuild_differential_state(self) -> None:
        self._record("rebuild_differential_state", super().rebuild_differential_state)

    def rebuild_transport_state(self) -> None:
        self._record("rebuild_transport_state", super().rebuild_transport_state)

    def rebuild_identity_state(self) -> None:
        self._record("rebuild_identity_state", super().rebuild_identity_state)

    def _apply_hybrid_spark_stages(self, trace: list[str] | None = None) -> list[Any]:
        return self._record(
            "apply_hybrid_spark_stages",
            lambda: super(TracingGRC9V3, self)._apply_hybrid_spark_stages(trace),
        )

    def rebuild_choice_state(self) -> list[Any]:
        return self._record("rebuild_choice_state", super().rebuild_choice_state)

    def apply_growth(self) -> list[Any]:
        return self._record("apply_growth", super().apply_growth)

    def apply_boundary_behavior(self) -> None:
        self._record("apply_boundary_behavior", super().apply_boundary_behavior)

    def apply_continuity(self) -> None:
        self._record("apply_continuity", super().apply_continuity)

    def enforce_quadrature_budget(self) -> dict[str, Any]:
        return self._record(
            "enforce_quadrature_budget", super().enforce_quadrature_budget
        )

    def refresh_coarse_cache(self) -> None:
        self._record("refresh_coarse_cache", super().refresh_coarse_cache)

    def compute_observables(self) -> dict[str, Any]:
        return self._record("compute_observables", super().compute_observables)


def envelope(payload: Any, schema_version: str) -> dict[str, Any]:
    return artifact_envelope(
        payload,
        schema_version=schema_version,
        generating_command=COMMAND,
    )


def load_fixture() -> dict[str, Any]:
    return read_json(EXPERIMENT_ROOT / "fixtures/two_node_transport.json")


def mapping(values: dict[Any, Any]) -> dict[str, Any]:
    return {str(key): values[key] for key in sorted(values)}


def port_edge_record(edge: PortEdge) -> dict[str, Any]:
    return {
        "node_u": edge.node_u,
        "port_u": edge.port_u,
        "node_v": edge.node_v,
        "port_v": edge.port_v,
        "conductance": edge.conductance,
        "flux_uv": edge.flux_uv,
    }


def transport_projection(model: GRC9V3) -> dict[str, Any]:
    state = model.get_state()
    return {
        "base_conductance": mapping(state.base_conductance),
        "potential": mapping(state.potential),
        "flux_uv": {
            str(edge_id): state.port_edges[edge_id].flux_uv
            for edge_id in sorted(state.port_edges)
        },
        "geometric_length": mapping(state.geometric_length),
        "flux_coupling": mapping(state.flux_coupling),
        "temporal_delay": mapping(state.temporal_delay),
    }


def physical_projection(model: GRC9V3) -> dict[str, Any]:
    state = model.get_state()
    return {
        "node_ids": list(sorted(state.topology.iter_live_node_ids())),
        "edge_ids": list(sorted(state.topology.iter_live_edge_ids())),
        "nodes": {
            str(node_id): {
                "coherence": node.coherence,
                "gradient_row_basis": list(node.gradient_row_basis),
                "signed_hessian_row_basis": list(node.signed_hessian_row_basis),
                "net_flux_summary": list(node.net_flux_summary),
                "basin_mass": node.basin_mass,
                "basin_id": node.basin_id,
                "parent_id": node.parent_id,
                "depth": node.depth,
            }
            for node_id, node in sorted(state.nodes.items())
        },
        "port_edges": {
            str(edge_id): port_edge_record(edge)
            for edge_id, edge in sorted(state.port_edges.items())
        },
        "base_conductance": mapping(state.base_conductance),
        "geometric_length": mapping(state.geometric_length),
        "temporal_delay": mapping(state.temporal_delay),
        "flux_coupling": mapping(state.flux_coupling),
        "potential": mapping(state.potential),
        "sink_set": sorted(state.sink_set),
        "basins": {
            str(sink): sorted(members) for sink, members in sorted(state.basins.items())
        },
        "hierarchy": mapping(state.hierarchy),
        "budget_target": state.budget_target,
        "remainder": state.remainder,
    }


def max_numeric_delta(left: Any, right: Any) -> float:
    if isinstance(left, bool) or isinstance(right, bool):
        return 0.0 if left == right else float("inf")
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return abs(float(left) - float(right))
    if isinstance(left, dict) and isinstance(right, dict) and set(left) == set(right):
        return max(
            (max_numeric_delta(left[key], right[key]) for key in left), default=0.0
        )
    if isinstance(left, list) and isinstance(right, list) and len(left) == len(right):
        return max(
            (max_numeric_delta(a, b) for a, b in zip(left, right, strict=True)),
            default=0.0,
        )
    return 0.0 if left == right else float("inf")


def replace_flux(state: GRC9V3State, flux: float) -> GRC9V3State:
    changed = deepcopy(state)
    edge = changed.port_edges[0]
    changed.port_edges[0] = PortEdge(
        node_u=edge.node_u,
        port_u=edge.port_u,
        node_v=edge.node_v,
        port_v=edge.port_v,
        conductance=edge.conductance,
        flux_uv=float(flux),
    )
    return changed


def perturb_hybrid_tensors(state: GRC9V3State) -> GRC9V3State:
    changed = deepcopy(state)
    tensors = changed.cached_quantities.get("hybrid_node_tensors")
    if not isinstance(tensors, dict) or not tensors:
        raise RuntimeError("GRV1 K control requires materialized hybrid_node_tensors")
    changed.cached_quantities["hybrid_node_tensors"] = {
        str(node_id): [
            [float(value) + 1_000_000.0 for value in row] for row in matrix
        ]
        for node_id, matrix in tensors.items()
    }
    return changed


def transport_anchor(fixture: dict[str, Any]) -> dict[str, Any]:
    model = GRC9V3.from_state(fixture["state"], fixture["params"])
    model.rebuild_differential_state()
    model.rebuild_transport_state()
    observed = transport_projection(model)
    expected = fixture["expected_transport"]
    tolerances = read_json(EXPERIMENT_ROOT / "configs/numerical_tolerances.json")
    residuals = {
        "base_conductance": abs(
            observed["base_conductance"]["0"] - expected["base_conductance"]["0"]
        ),
        "potential_0": abs(observed["potential"]["0"] - expected["potential"]["0"]),
        "potential_1": abs(observed["potential"]["1"] - expected["potential"]["1"]),
        "flux_uv": abs(observed["flux_uv"]["0"] - expected["flux_uv"]["0"]),
        "geometric_length": abs(
            observed["geometric_length"]["0"] - expected["geometric_length"]["0"]
        ),
        "flux_coupling": abs(
            observed["flux_coupling"]["0"] - expected["flux_coupling"]["0"]
        ),
        "temporal_delay": abs(
            observed["temporal_delay"]["0"] - expected["temporal_delay"]["0"]
        ),
    }
    maximum = max(residuals.values())
    passed = maximum <= tolerances["absolute_tolerances"]["derived_surface"]
    return {
        "fixture_id": "F0",
        "source_test": fixture["source"],
        "runtime_methods": [
            "GRC9V3.rebuild_differential_state",
            "GRC9V3.rebuild_transport_state",
        ],
        "observed": observed,
        "expected": expected,
        "absolute_residuals": residuals,
        "maximum_absolute_residual": maximum,
        "declared_tolerance": tolerances["absolute_tolerances"]["derived_surface"],
        "status": "passed" if passed else "failed",
        "evidence_role": "canonical_existing_test_anchor_not_new_scientific_evidence",
    }


def step_trace_control(fixture: dict[str, Any]) -> dict[str, Any]:
    traced = TracingGRC9V3.from_state(fixture["state"], fixture["params"])
    ordinary = GRC9V3.from_state(fixture["state"], fixture["params"])
    before_nodes = list(traced.get_state().topology.iter_live_node_ids())
    before_edges = list(traced.get_state().topology.iter_live_edge_ids())
    traced_result = traced.step()
    ordinary.step()
    emitted = tuple(traced_result.bookkeeping["step_order"])
    runtime_expected = tuple(traced_result.bookkeeping["expected_step_order"])
    observed_high_level_calls = tuple(traced.instrumentation_calls)
    full_runtime_snapshot_equal = traced.snapshot() == ordinary.snapshot()
    noninterference_delta = max_numeric_delta(
        physical_projection(traced), physical_projection(ordinary)
    )
    after_nodes = list(traced.get_state().topology.iter_live_node_ids())
    after_edges = list(traced.get_state().topology.iter_live_edge_ids())
    checks = {
        "emitted_trace_matches_frozen_order": emitted == EXPECTED_STEP_ORDER,
        "runtime_expected_trace_matches_frozen_order": runtime_expected == EXPECTED_STEP_ORDER,
        "observed_high_level_calls_match_runtime_structure": observed_high_level_calls
        == EXPECTED_HIGH_LEVEL_CALL_ORDER,
        "instrumented_and_ordinary_runtime_snapshots_equal": full_runtime_snapshot_equal,
        "instrumentation_noninterfering": noninterference_delta == 0.0,
        "fixed_topology": before_nodes == after_nodes and before_edges == after_edges,
        "no_events": not traced_result.events,
        "boundary_noop": traced.get_state().cached_quantities.get(
            "boundary_behavior_mode"
        )
        == "prune_noop",
    }
    return {
        "frozen_step_order": list(EXPECTED_STEP_ORDER),
        "runtime_emitted_step_order": list(emitted),
        "observed_high_level_call_order": list(observed_high_level_calls),
        "events": [event.kind for event in traced_result.events],
        "topology_before": {"nodes": before_nodes, "edges": before_edges},
        "topology_after": {"nodes": after_nodes, "edges": after_edges},
        "instrumented_and_ordinary_runtime_snapshots_equal": full_runtime_snapshot_equal,
        "instrumented_vs_ordinary_max_delta": noninterference_delta,
        "checks": checks,
        "status": "passed" if all(checks.values()) else "failed",
    }


def k_counterfactual(fixture: dict[str, Any]) -> dict[str, Any]:
    prepared = GRC9V3.from_state(fixture["state"], fixture["params"])
    prepared.rebuild_differential_state()
    base_state = deepcopy(prepared.get_state())
    changed_state = perturb_hybrid_tensors(base_state)
    base_k_digest = semantic_digest(base_state.cached_quantities["hybrid_node_tensors"])
    changed_k_digest = semantic_digest(
        changed_state.cached_quantities["hybrid_node_tensors"]
    )

    transport_base = GRC9V3.from_state(base_state, fixture["params"])
    transport_changed = GRC9V3.from_state(changed_state, fixture["params"])
    transport_base.rebuild_transport_state()
    transport_changed.rebuild_transport_state()
    transport_delta = max_numeric_delta(
        transport_projection(transport_base), transport_projection(transport_changed)
    )

    full_base = GRC9V3.from_state(base_state, fixture["params"])
    full_changed = GRC9V3.from_state(changed_state, fixture["params"])
    full_base.step()
    full_changed.step()
    full_delta = max_numeric_delta(
        physical_projection(full_base), physical_projection(full_changed)
    )
    final_k_equal = (
        full_base.get_state().cached_quantities.get("hybrid_node_tensors")
        == full_changed.get_state().cached_quantities.get("hybrid_node_tensors")
    )
    checks = {
        "counterfactual_cache_differs": base_k_digest != changed_k_digest,
        "transport_outputs_equal": transport_delta == 0.0,
        "full_step_physical_outputs_equal": full_delta == 0.0,
        "differential_stage_overwrites_counterfactual_cache": final_k_equal,
    }
    return {
        "intervened_surface": "cached_quantities.hybrid_node_tensors",
        "base_k_digest": base_k_digest,
        "counterfactual_k_digest": changed_k_digest,
        "transport_max_delta": transport_delta,
        "full_step_physical_max_delta": full_delta,
        "checks": checks,
        "classification": "diagnostic_only_not_transport_input_overwritten_before_full_step_use",
        "status": "passed" if all(checks.values()) else "failed",
    }


def current_sign_control(fixture: dict[str, Any]) -> dict[str, Any]:
    prepared = GRC9V3.from_state(fixture["state"], fixture["params"])
    prepared.rebuild_differential_state()
    positive_state = replace_flux(prepared.get_state(), 4.0)
    negative_state = replace_flux(prepared.get_state(), -4.0)
    zero_state = replace_flux(prepared.get_state(), 0.0)

    positive_transport = GRC9V3.from_state(positive_state, fixture["params"])
    negative_transport = GRC9V3.from_state(negative_state, fixture["params"])
    zero_transport = GRC9V3.from_state(zero_state, fixture["params"])
    positive_transport.rebuild_transport_state()
    negative_transport.rebuild_transport_state()
    zero_transport.rebuild_transport_state()
    sign_delta = max_numeric_delta(
        transport_projection(positive_transport),
        transport_projection(negative_transport),
    )
    magnitude_delta = abs(
        positive_transport.get_state().base_conductance[0]
        - zero_transport.get_state().base_conductance[0]
    )

    positive_full = GRC9V3.from_state(positive_state, fixture["params"])
    negative_full = GRC9V3.from_state(negative_state, fixture["params"])
    positive_full.step()
    negative_full.step()
    full_delta = max_numeric_delta(
        physical_projection(positive_full), physical_projection(negative_full)
    )

    positive_differential = GRC9V3.from_state(positive_state, fixture["params"])
    negative_differential = GRC9V3.from_state(negative_state, fixture["params"])
    positive_differential.rebuild_differential_state()
    negative_differential.rebuild_differential_state()
    pre_transport_summary_sign_changes = (
        positive_differential.get_state().nodes[0].net_flux_summary
        != negative_differential.get_state().nodes[0].net_flux_summary
    )
    tensor_sign_even = (
        positive_differential.get_state().cached_quantities["hybrid_node_tensors"]
        == negative_differential.get_state().cached_quantities["hybrid_node_tensors"]
    )
    checks = {
        "matched_sign_reversal_transport_outputs_equal": sign_delta == 0.0,
        "matched_sign_reversal_full_step_outputs_equal": full_delta == 0.0,
        "pre_transport_net_flux_summary_tracks_sign": pre_transport_summary_sign_changes,
        "hybrid_tensor_channel_is_sign_even": tensor_sign_even,
        "old_current_magnitude_enters_conductance_exactly": magnitude_delta > 0.0,
    }
    return {
        "physical_reversal": "fixed_edge_coordinates_J_to_minus_J",
        "transport_sign_pair_max_delta": sign_delta,
        "full_step_sign_pair_max_delta": full_delta,
        "J4_vs_J0_base_conductance_absolute_delta": magnitude_delta,
        "declared_W_absolute_tolerance": 1e-10,
        "magnitude_effect_resolved_at_declared_tolerance": magnitude_delta > 1e-10,
        "checks": checks,
        "classification": {
            "magnitude_persistence": "direct_sign_even_input_to_next_conductance_but_F0_effect_below_declared_W_tolerance",
            "unoriented_axis_persistence": "single_edge_sign_even_channel_only_not_distinct_from_magnitude",
            "orientation_persistence": "not_retained_across_transport_or_complete_step",
            "current_reconstructed_anew": True,
            "transient_sign_summary": "reconstructed_pre_transport_then_overwritten_after_new_flux",
        },
        "status": "passed" if all(checks.values()) else "failed",
    }


def edge_reorientation_control(fixture: dict[str, Any]) -> dict[str, Any]:
    normal_state = deepcopy(fixture["state"])
    normal_state["port_edges"]["0"]["flux_uv"] = 4.0
    reversed_state = deepcopy(normal_state)
    edge = reversed_state["topology"]["edges"][0]
    edge["endpoint_a"], edge["endpoint_b"] = edge["endpoint_b"], edge["endpoint_a"]
    reversed_state["port_edges"]["0"] = {
        "node_u": 1,
        "port_u": 1,
        "node_v": 0,
        "port_v": 1,
        "conductance": 0.5,
        "flux_uv": -4.0,
    }
    normal = GRC9V3.from_state(normal_state, fixture["params"])
    reversed_model = GRC9V3.from_state(reversed_state, fixture["params"])
    canonical_port_edges_equal = (
        normal.get_state().port_edges == reversed_model.get_state().port_edges
    )
    raw_endpoint_order_differs = (
        normal.get_state().topology.edge_ports(0)
        != reversed_model.get_state().topology.edge_ports(0)
    )
    normal.rebuild_differential_state()
    reversed_model.rebuild_differential_state()
    normal.rebuild_transport_state()
    reversed_model.rebuild_transport_state()
    output_delta = max_numeric_delta(
        transport_projection(normal), transport_projection(reversed_model)
    )
    checks = {
        "raw_coordinate_orientation_changed": raw_endpoint_order_differs,
        "current_coordinate_sign_mapped": canonical_port_edges_equal,
        "physical_transport_covariant": output_delta == 0.0,
    }
    return {
        "control": "edge_coordinate_reorientation_with_J_sign_map",
        "normal_raw_endpoints": normal_state["topology"]["edges"][0],
        "reoriented_raw_endpoints": reversed_state["topology"]["edges"][0],
        "transport_max_delta": output_delta,
        "checks": checks,
        "classification": "coordinate_covariance_passed_distinct_from_physical_current_reversal",
        "status": "passed" if all(checks.values()) else "failed",
    }


def clone_and_replay_control(
    fixture: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    base_state = deepcopy(fixture["state"])
    intervention = apply_clone_intervention(
        base_state, [(('port_edges', '0', 'flux_uv'), 4.0)]
    )
    source_unchanged = base_state["port_edges"]["0"]["flux_uv"] == 0.0
    clone_changed = intervention.state["port_edges"]["0"]["flux_uv"] == 4.0
    canonical_round_trip = canonical_clone(base_state) == base_state
    deep_clone = exact_deep_clone(base_state)
    deep_clone["nodes"]["0"]["coherence"] = 999.0
    deep_clone_non_aliasing = base_state["nodes"]["0"]["coherence"] == 1.0

    model = GRC9V3.from_state(intervention.state, fixture["params"])
    model.rebuild_differential_state()
    model.rebuild_transport_state()
    before_projection = physical_projection(model)
    snapshot = model.snapshot()
    raw_snapshot_digest = semantic_digest(snapshot)
    derived_projection_digest = semantic_digest(before_projection)
    with tempfile.TemporaryDirectory() as temporary_directory:
        snapshot_path = Path(temporary_directory) / "grv1_replay.json"
        model.save(str(snapshot_path))
        restored = GRC9V3.load(str(snapshot_path))
    after_projection = physical_projection(restored)
    replay_delta = max_numeric_delta(before_projection, after_projection)
    checks = {
        "clone_first_source_unchanged": source_unchanged,
        "declared_path_changed": clone_changed,
        "canonical_json_round_trip_exact": canonical_round_trip,
        "deep_clone_non_aliasing": deep_clone_non_aliasing,
        "runtime_snapshot_replay_physical_projection_exact": replay_delta == 0.0,
        "raw_snapshot_and_derived_projection_separate": raw_snapshot_digest
        != derived_projection_digest,
    }
    result = {
        "raw_snapshot_committed": False,
        "raw_snapshot_sha256": raw_snapshot_digest,
        "derived_projection_sha256": derived_projection_digest,
        "runtime_snapshot_replay_max_delta": replay_delta,
        "checks": checks,
        "status": "passed" if all(checks.values()) else "failed",
    }
    registry = {
        "interventions": [
            {
                "intervention_id": "GRV1-INT-J-POSITIVE",
                "base_snapshot_sha256": semantic_digest(base_state),
                "coordinate_semantics": "canonical_edge_0_u_to_v_flux_uv",
                "fields_directly_changed": ["port_edges.0.flux_uv"],
                "fields_explicitly_held_fixed": ["topology", "nodes", "params"],
                "fields_rebuilt_afterward": ["differential_state", "transport_state"],
                "rebuild_order": [
                    "rebuild_differential_state",
                    "rebuild_transport_state",
                ],
                "validity_checks": checks,
                "reachability_status": "synthetic_valid_counterfactual_not_claimed_reached",
                "physical_projection_before": {
                    "coherence": [1.0, 3.0],
                    "flux_uv": [0.0],
                },
                "physical_projection_after": {
                    "coherence": [1.0, 3.0],
                    "flux_uv_before_rebuild": [4.0],
                    "flux_uv_after_rebuild": [
                        model.get_state().port_edges[0].flux_uv
                    ],
                },
                "causal_state_projection_before": "F0_declared_state",
                "causal_state_projection_after": "F0_with_declared_old_J_intervention",
            }
        ]
    }
    return result, registry


def state_field_inventory() -> dict[str, Any]:
    classifications = {
        "topology": ("causal_runtime_state", True, "controls adjacency and port incidence"),
        "node_values": ("reconstructed_state", False, "unused family-neutral placeholder in GRC9V3"),
        "edge_values": ("reconstructed_state", False, "unused family-neutral placeholder in GRC9V3"),
        "step_index": ("causal_runtime_state", True, "administratively advances and keys spark, growth, choice, and event state"),
        "time": ("deterministic_administrative_advancement", False, "advances by dt and is not read by current transition decisions"),
        "budget_target": ("causal_runtime_state", True, "sets the quadrature correction target"),
        "remainder": ("reconstructed_state", False, "recomputed by quadrature-budget enforcement"),
        "cached_quantities": ("causal_runtime_state", True, "mixed cache; hessian history and growth-front records are read later while K is diagnostic-only"),
        "event_log": ("observer_only_state", False, "append-only event history and current-step slicing surface"),
        "observables": ("observer_only_state", False, "reported observer surface; no physical transition reads found"),
        "rng_state": ("causal_runtime_state", True, "restores deterministic growth sampling state"),
        "params_identity": ("reconstructed_state", False, "restored from current parameter hash"),
        "nodes": ("causal_runtime_state", True, "coherence is causal; differential and basin subfields are rebuilt or maintained"),
        "port_edges": ("causal_runtime_state", True, "old flux enters next conductance through J squared; edge carrier is canonical"),
        "base_conductance": ("reconstructed_state", False, "rebuilt before potential and flux"),
        "geometric_length": ("reconstructed_state", False, "rebuilt analytic pre-flux edge label"),
        "temporal_delay": ("reconstructed_state", False, "rebuilt analytic post-flux edge label"),
        "flux_coupling": ("reconstructed_state", False, "rebuilt absolute-flux edge label"),
        "potential": ("reconstructed_state", False, "rebuilt from coherence and conductance"),
        "sink_set": ("reconstructed_state", False, "rebuilt from current flux topology"),
        "basins": ("reconstructed_state", False, "rebuilt from current flux topology"),
        "hierarchy": ("causal_runtime_state", True, "persists completed child relations across steps"),
        "expansion_registry": ("causal_runtime_state", True, "persists expansion schedules and topology-growth history"),
        "choice_registry": ("causal_runtime_state", True, "previous choice state is read by choice/collapse update"),
        "collapse_registry": ("causal_runtime_state", True, "persists collapse records"),
        "coarse_cache": ("observer_only_state", False, "operator output cache invalidated on transport or topology change"),
        "edge_label_computation_mode": ("reconstructed_state", False, "derived from declared constitutive modes"),
        "edge_label_params": ("reconstructed_state", False, "derived from declared parameters and label selection"),
    }
    runtime_fields = [field.name for field in fields(GRC9V3State)]
    missing = sorted(set(runtime_fields) - set(classifications))
    extra = sorted(set(classifications) - set(runtime_fields))
    records = [
        {
            "field": name,
            "classification": classifications[name][0],
            "grv3_closure_candidate": classifications[name][1],
            "reason": classifications[name][2],
            "administratively_advancing": name
            in {"step_index", "time", "event_log", "observables"},
        }
        for name in runtime_fields
    ]
    return {
        "runtime_dataclass": "pygrc.models.grc_9_v3_state.GRC9V3State",
        "records": records,
        "all_runtime_fields_classified": not missing and not extra,
        "missing_fields": missing,
        "extra_fields": extra,
        "grv3_closure_candidates": [
            record["field"]
            for record in records
            if record["grv3_closure_candidate"]
        ],
    }


def protected_manifest_v1() -> dict[str, Any]:
    predecessor = read_json(EXPERIMENT_ROOT / "outputs/protected_path_manifest_v0.json")
    payload = predecessor["payload"]
    base_revision = payload["substrate_base_revision"]
    if git("diff", "--name-only", base_revision, "--", "src/pygrc", "tests", "specs"):
        raise RuntimeError("GRV1 protected source/spec/test paths differ from substrate base")
    manifest_paths = {entry["path"] for entry in payload["files"]}
    missing_load_bearing = sorted(set(LOAD_BEARING_PATHS) - manifest_paths)
    if missing_load_bearing:
        raise RuntimeError(
            f"protected v0 omitted load-bearing paths: {missing_load_bearing}"
        )
    current = file_manifest(manifest_paths)
    if current["tree_sha256"] != payload["tree_sha256"]:
        raise RuntimeError("protected tree digest changed before GRV1")
    successor = {
        **current,
        "manifest_id": "protected_path_manifest_v1",
        "scope": payload["scope"],
        "substrate_base_revision": base_revision,
        "predecessor_path": "outputs/protected_path_manifest_v0.json",
        "predecessor_payload_sha256": predecessor["payload_sha256"],
        "predecessor_tree_sha256": payload["tree_sha256"],
        "newly_discovered_load_bearing_paths": [],
        "load_bearing_paths_confirmed": list(LOAD_BEARING_PATHS),
        "later_discovery_policy": "source_or_specification_mismatch_blocks_dependent_work_v1_never_silently_amended",
        "unchanged_successor": True,
    }
    return envelope(successor, "b1_protected_path_manifest_v1")


def fixture_registry(
    fixture: dict[str, Any], anchor_result: dict[str, Any]
) -> dict[str, Any]:
    configured = read_json(EXPERIMENT_ROOT / "configs/fixture_registry.json")
    return envelope(
        {
            "source_registry_path": "configs/fixture_registry.json",
            "source_registry_sha256": sha256_file(
                EXPERIMENT_ROOT / "configs/fixture_registry.json"
            ),
            "fixtures": configured["fixtures"],
            "grv1_consumed_fixture_ids": ["F0"],
            "F0_source_path": "fixtures/two_node_transport.json",
            "F0_source_sha256": sha256_file(
                EXPERIMENT_ROOT / "fixtures/two_node_transport.json"
            ),
            "F0_anchor_status": anchor_result["status"],
            "F4_consumption_status": "not_consumed_full_triangle_control_family_deferred",
            "orientation_control_scope": "F0_derived_two_node_edge_coordinate_control_required_by_GRV1_D",
            "F3_scientific_candidate_consumed": False,
            "new_scientific_evidence_opened": False,
        },
        "b1_grv1_fixture_registry_v1",
    )


def input_experiment_manifest() -> dict[str, Any]:
    relative = EXPERIMENT_ROOT.relative_to(REPO_ROOT).as_posix()
    tracked = git("ls-files", "--", relative).splitlines()
    files = [
        path
        for path in tracked
        if path
        and not path.startswith(f"{relative}/outputs/")
        and not path.startswith(f"{relative}/reports/")
    ]
    return file_manifest(files)


def accepted_grv0_anchor() -> tuple[dict[str, Any], str, str]:
    relative = "outputs/gates/grv0_acceptance_anchor.json"
    path = EXPERIMENT_ROOT / relative
    anchor = read_json(path)
    validate_acceptance_anchor(anchor)
    if anchor["acceptance_status"] != "accepted":
        raise RuntimeError("GRV1 requires accepted GRV0 anchor")
    if anchor["result_revision"] != GRV0_RESULT_REVISION:
        raise RuntimeError("GRV0 anchor result revision mismatch")
    if anchor["receipt_payload_sha256"] != GRV0_RECEIPT_SHA256:
        raise RuntimeError("GRV0 anchor receipt digest mismatch")
    repository_relative = path.relative_to(REPO_ROOT).as_posix()
    anchor_commit = git("log", "-1", "--format=%H", "--", repository_relative)
    committed = git("show", f"{anchor_commit}:{repository_relative}")
    if json.loads(committed) != anchor:
        raise RuntimeError("working GRV0 anchor differs from immutable anchor commit")
    return anchor, semantic_digest(anchor), anchor_commit


def build_grv1_records() -> dict[str, Any]:
    fixture = load_fixture()
    anchor = transport_anchor(fixture)
    step = step_trace_control(fixture)
    k_control = k_counterfactual(fixture)
    sign = current_sign_control(fixture)
    orientation = edge_reorientation_control(fixture)
    replay, intervention_payload = clone_and_replay_control(fixture)
    inventory = state_field_inventory()
    checks = {
        "transport_anchor_passed": anchor["status"] == "passed",
        "step_trace_and_fixed_topology_passed": step["status"] == "passed",
        "K_counterfactual_passed": k_control["status"] == "passed",
        "current_sign_control_passed": sign["status"] == "passed",
        "edge_reorientation_control_passed": orientation["status"] == "passed",
        "clone_and_replay_control_passed": replay["status"] == "passed",
        "all_runtime_fields_classified": inventory["all_runtime_fields_classified"],
    }
    instrumentation = envelope(
        {
            "gate_id": "GRV1",
            "specification_id": SPECIFICATION_ID,
            "status": "passed" if all(checks.values()) else "failed",
            "transport_anchor": anchor,
            "step_order_and_fixed_topology": step,
            "K_counterfactual": k_control,
            "current_sign_control": sign,
            "edge_reorientation_control": orientation,
            "clone_serialization_and_replay": replay,
            "excluded_and_administrative_field_inventory": inventory,
            "load_bearing_source_paths": list(LOAD_BEARING_PATHS),
            "checks": checks,
            "claim_boundary": {
                "exact_runtime_dependency_semantics_supported": all(checks.values()),
                "exact_orientation_semantics_supported": all(checks.values()),
                "formed_branch_supported": False,
                "continuation_supported": False,
                "retention_supported": False,
                "readback_supported": False,
                "writeback_supported": False,
                "runtime_change": False,
            },
        },
        "b1_grv1_instrumentation_validation_v1",
    )
    interventions = envelope(
        intervention_payload, "b1_grv1_intervention_registry_v1"
    )
    return {
        "instrumentation_validation.json": instrumentation,
        "fixture_registry.json": fixture_registry(fixture, anchor),
        "intervention_registry.json": interventions,
        "protected_path_manifest_v1.json": protected_manifest_v1(),
    }


def write_report(instrumentation: dict[str, Any]) -> Path:
    payload = instrumentation["payload"]
    sign = payload["current_sign_control"]
    report = EXPERIMENT_ROOT / "reports/b1_grv1_instrumentation_and_source_fidelity.md"
    report.write_text(
        "\n".join(
            [
                "# B1-GR GRV1 Instrumentation And Source Fidelity",
                "",
                "## Result",
                "",
                "```text",
                f"mechanical_status = {payload['status']}",
                "scientific_acceptance = awaiting_human_review",
                "candidate_closeout_ceiling = GRV-C2",
                "runtime_change = false",
                "positive_evidence_opened = false",
                "```",
                "",
                "GRV1 reproduces the canonical F0 transport anchor through current",
                "runtime methods and independently observes the high-level call sequence",
                "without changing the resulting physical projection. The emitted step",
                "trace matches the frozen canonical order, topology remains fixed, and no",
                "events occur.",
                "",
                "## Source-Fidelity Findings",
                "",
                "- The materialized hybrid tensor cache is diagnostic for transport:",
                "  changing it does not alter transport, and the first differential stage",
                "  overwrites it before a full step can consume the counterfactual value.",
                "- Prior current magnitude has a direct sign-even `J^2` path into the next",
                "  conductance. Under F0 its measured effect is below the declared `W`",
                "  tolerance, so GRV1 records the source path without promoting a resolved",
                "  magnitude-retention claim.",
                "- Physical `J -> -J` leaves transport and complete-step projections equal.",
                "  A pre-transport net-flux summary tracks sign, but transport reconstructs",
                "  current and the later refresh overwrites that transient summary.",
                "- Reversing the edge coordinate while mapping `J -> -J` preserves physical",
                "  transport exactly. Coordinate covariance is therefore distinct from the",
                "  negative old-current orientation result.",
                "",
                "## Current Classification",
                "",
                "```text",
                f"magnitude = {sign['classification']['magnitude_persistence']}",
                f"axis = {sign['classification']['unoriented_axis_persistence']}",
                f"orientation = {sign['classification']['orientation_persistence']}",
                "current_reconstructed_anew = true",
                "K_cache = diagnostic_only_not_transport_input",
                "```",
                "",
                "## State Closure Handoff",
                "",
                "Every `GRC9V3State` dataclass field is classified. Causal and mixed",
                "runtime fields remain explicit GRV3 closure candidates; exclusion from",
                "the physical projection is not treated as proof of causal irrelevance.",
                "The protected-path v1 manifest is an unchanged successor to v0. Any later",
                "load-bearing-path discovery must route through",
                "`source_or_specification_mismatch`; v1 cannot be amended silently.",
                "",
                "## Claim Boundary",
                "",
                "GRV1 supports exact bounded runtime dependency and coordinate/orientation",
                "semantics only. It does not establish a formed branch, continuation,",
                "retention, read-back, or write-back.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return report


def run_grv1() -> dict[str, Any]:
    if git("status", "--porcelain"):
        raise RuntimeError("GRV1 requires a clean committed P1 input revision")
    anchor, anchor_digest, anchor_commit = accepted_grv0_anchor()
    records = build_grv1_records()
    output_root = EXPERIMENT_ROOT / "outputs"
    output_paths: list[Path] = []
    for name, record in records.items():
        path = output_root / name
        write_json(path, record)
        output_paths.append(path)
    instrumentation = records["instrumentation_validation.json"]
    if instrumentation["payload"]["status"] != "passed":
        raise RuntimeError("GRV1 source-fidelity checks failed closed")
    report = write_report(instrumentation)
    output_paths.append(report)

    baseline = read_json(output_root / "baseline_manifest.json")["payload"]
    experiment = input_experiment_manifest()
    receipt = finalize_receipt(
        {
            "gate_id": "GRV1",
            "input_execution_revision": git("rev-parse", "HEAD"),
            "substrate_base_revision": baseline["substrate_base_revision"],
            "input_experiment_tree_sha256": experiment["tree_sha256"],
            "prerequisite_result_receipt_digests": [GRV0_RECEIPT_SHA256],
            "prerequisite_acceptance_anchors": [
                {
                    "gate_id": "GRV0",
                    "anchor_payload_sha256": anchor_digest,
                    "immutable_ref": f"git:{anchor_commit}",
                }
            ],
            "output_artifact_digests": {
                path.relative_to(EXPERIMENT_ROOT).as_posix(): sha256_file(path)
                for path in sorted(output_paths)
            },
            "status": "awaiting_scientific_review",
            "blocked_gates": [f"GRV{index}" for index in range(2, 9)],
            "claim_ceiling": "GRV-C2_candidate_exact_runtime_dependency_and_orientation_semantics_only_pending_authorized_human_acceptance",
        }
    )
    validate_receipt(receipt)
    write_json(output_root / "gates/grv1_result_receipt.json", receipt)
    return {
        "anchor": anchor,
        "anchor_commit": anchor_commit,
        "records": records,
        "receipt": receipt,
        "report": report,
    }


def main() -> None:
    run_grv1()
    print("GRV1 mechanically validated; scientific acceptance anchor is pending.")


if __name__ == "__main__":
    main()
