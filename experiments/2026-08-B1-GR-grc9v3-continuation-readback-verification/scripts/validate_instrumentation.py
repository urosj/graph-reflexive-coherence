"""Execute GRV1 instrumentation and source-fidelity validation."""

from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from dataclasses import fields
import json
import math
from pathlib import Path
import subprocess
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
from pygrc.core import canonicalize_json_value  # noqa: E402
from pygrc.models.grc_9_v3 import _state_payload_from_state  # noqa: E402
from pygrc.models.grc_9_v3_runtime import (  # noqa: E402
    compute_base_conductance,
    compute_edge_labels,
    compute_flux,
    compute_potential,
)
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
SUPERSEDED_GRV1_RECEIPT_SHA256 = (
    "c8f51f4cc1f816726aa65d56e9165809ba54a5d47f4259e4e3f3318712f5b1bf"
)

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
    "src/pygrc/core/__init__.py",
    "src/pygrc/core/backends.py",
    "src/pygrc/core/capabilities.py",
    "src/pygrc/core/errors.py",
    "src/pygrc/core/events.py",
    "src/pygrc/core/graph.py",
    "src/pygrc/core/ids.py",
    "src/pygrc/core/interfaces.py",
    "src/pygrc/core/mutations.py",
    "src/pygrc/core/observables.py",
    "src/pygrc/core/params.py",
    "src/pygrc/core/serialization.py",
    "src/pygrc/core/storage.py",
    "src/pygrc/core/types.py",
    "src/pygrc/models/grc_9_coarse.py",
    "src/pygrc/models/grc_9_ports.py",
    "src/pygrc/models/grc_9_state.py",
    "src/pygrc/models/grc_9_v3.py",
    "src/pygrc/models/grc_9_v3_choice.py",
    "src/pygrc/models/grc_9_v3_runtime.py",
    "src/pygrc/models/grc_9_v3_sparks.py",
    "src/pygrc/models/grc_9_v3_state.py",
    "src/pygrc/models/grc_v3_differential.py",
)

K_COUNTERFACTUAL_AMPLITUDES = (1e-3, 1.0, 100.0)


def runtime_state_payload(model: GRC9V3) -> dict[str, Any]:
    """Return the runtime's complete current-state serialization surface."""

    return _state_payload_from_state(model.get_state())


def changed_top_level_fields(before: dict[str, Any], after: dict[str, Any]) -> list[str]:
    return sorted(
        key for key in set(before) | set(after) if before.get(key) != after.get(key)
    )


class TracingGRC9V3(GRC9V3):
    """Observe public step stages without changing runtime state transitions."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.instrumentation_calls: list[str] = []
        self.instrumentation_stage_records: list[dict[str, Any]] = []

    def _record(self, name: str, operation: Callable[[], Any]) -> Any:
        before = runtime_state_payload(self)
        self.instrumentation_calls.append(name)
        result = operation()
        after = runtime_state_payload(self)
        self.instrumentation_stage_records.append(
            {
                "ordinal": len(self.instrumentation_stage_records) + 1,
                "method": name,
                "input_state_sha256": semantic_digest(before),
                "output_state_sha256": semantic_digest(after),
                "changed_top_level_fields": changed_top_level_fields(before, after),
            }
        )
        return result

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


def tensor_structure_valid(tensors: Any) -> bool:
    if not isinstance(tensors, dict) or not tensors:
        return False
    for matrix in tensors.values():
        if not isinstance(matrix, list) or not matrix:
            return False
        size = len(matrix)
        if any(not isinstance(row, list) or len(row) != size for row in matrix):
            return False
        for row in matrix:
            if any(not isinstance(value, (int, float)) or not math.isfinite(value) for value in row):
                return False
        for row_index in range(size):
            for column_index in range(size):
                if matrix[row_index][column_index] != matrix[column_index][row_index]:
                    return False
    return True


def perturb_hybrid_tensors(
    state: GRC9V3State, amplitude: float = 1.0
) -> GRC9V3State:
    changed = deepcopy(state)
    tensors = changed.cached_quantities.get("hybrid_node_tensors")
    if not tensor_structure_valid(tensors):
        raise RuntimeError("GRV1 K control requires materialized hybrid_node_tensors")
    changed.cached_quantities["hybrid_node_tensors"] = {
        str(node_id): [
            [
                float(value) + (float(amplitude) if row_index == column_index else 0.0)
                for column_index, value in enumerate(row)
            ]
            for row_index, row in enumerate(matrix)
        ]
        for node_id, matrix in tensors.items()
    }
    if not tensor_structure_valid(
        changed.cached_quantities["hybrid_node_tensors"]
    ):
        raise RuntimeError("GRV1 K intervention violated tensor structure")
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


def call_and_capture(
    model: GRC9V3,
    records: list[dict[str, Any]],
    method: str,
    operation: Callable[[], Any],
) -> Any:
    before = runtime_state_payload(model)
    result = operation()
    after = runtime_state_payload(model)
    records.append(
        {
            "ordinal": len(records) + 1,
            "method": method,
            "input_state_sha256": semantic_digest(before),
            "output_state_sha256": semantic_digest(after),
            "changed_top_level_fields": changed_top_level_fields(before, after),
        }
    )
    return result


def public_stage_replay_control(fixture: dict[str, Any]) -> dict[str, Any]:
    native = TracingGRC9V3.from_state(fixture["state"], fixture["params"])
    native_result = native.step()
    native_records = deepcopy(native.instrumentation_stage_records)

    replay = GRC9V3.from_state(fixture["state"], fixture["params"])
    replay_records: list[dict[str, Any]] = []
    initial_event_count = len(replay.get_state().event_log)
    call_and_capture(
        replay,
        replay_records,
        "rebuild_differential_state",
        replay.rebuild_differential_state,
    )
    call_and_capture(
        replay,
        replay_records,
        "rebuild_transport_state",
        replay.rebuild_transport_state,
    )
    call_and_capture(
        replay,
        replay_records,
        "rebuild_differential_state",
        replay.rebuild_differential_state,
    )
    call_and_capture(
        replay,
        replay_records,
        "rebuild_identity_state",
        replay.rebuild_identity_state,
    )
    call_and_capture(
        replay,
        replay_records,
        "apply_hybrid_spark_stages",
        replay.apply_hybrid_sparks,
    )
    call_and_capture(
        replay,
        replay_records,
        "rebuild_choice_state",
        replay.rebuild_choice_state,
    )
    call_and_capture(replay, replay_records, "apply_growth", replay.apply_growth)
    call_and_capture(
        replay,
        replay_records,
        "apply_boundary_behavior",
        replay.apply_boundary_behavior,
    )
    call_and_capture(
        replay,
        replay_records,
        "apply_continuity",
        replay.apply_continuity,
    )
    call_and_capture(
        replay,
        replay_records,
        "enforce_quadrature_budget",
        replay.enforce_quadrature_budget,
    )
    call_and_capture(
        replay,
        replay_records,
        "rebuild_differential_state",
        replay.rebuild_differential_state,
    )
    call_and_capture(
        replay,
        replay_records,
        "rebuild_transport_state",
        replay.rebuild_transport_state,
    )
    call_and_capture(
        replay,
        replay_records,
        "rebuild_differential_state",
        replay.rebuild_differential_state,
    )
    call_and_capture(
        replay,
        replay_records,
        "rebuild_identity_state",
        replay.rebuild_identity_state,
    )
    call_and_capture(
        replay,
        replay_records,
        "refresh_coarse_cache",
        replay.refresh_coarse_cache,
    )
    observables = call_and_capture(
        replay,
        replay_records,
        "compute_observables",
        replay.compute_observables,
    )

    state = replay.get_state()
    final_events = list(state.event_log[initial_event_count:])
    state.step_index += 1
    state.time += replay.get_params().dt
    state.observables = dict(observables)
    state.params_identity = replay.get_params().params_hash
    state.cached_quantities["last_step_trace"] = EXPECTED_STEP_ORDER
    state.cached_quantities["current_step_events"] = [
        {
            "kind": event.kind,
            "step_index": event.step_index,
            "payload": dict(event.payload),
            "source_family": event.source_family,
        }
        for event in final_events
    ]

    native_state = runtime_state_payload(native)
    replay_state = runtime_state_payload(replay)
    stage_records_equal = native_records == replay_records
    checks = {
        "public_stage_call_order_and_multiplicity_equal": [
            record["method"] for record in native_records
        ]
        == [record["method"] for record in replay_records],
        "stage_boundary_records_equal": stage_records_equal,
        "final_complete_runtime_state_equal": native_state == replay_state,
        "final_snapshot_equal": native.snapshot() == replay.snapshot(),
        "event_slice_equal": [event.kind for event in native_result.events]
        == [event.kind for event in final_events],
    }
    return {
        "native_stage_records": native_records,
        "public_replay_stage_records": replay_records,
        "native_call_counts": dict(
            sorted(Counter(record["method"] for record in native_records).items())
        ),
        "public_replay_call_counts": dict(
            sorted(Counter(record["method"] for record in replay_records).items())
        ),
        "checks": checks,
        "status": "passed" if all(checks.values()) else "failed",
        "scope": "F0_fixed_topology_no_event_complete_synchronous_beat",
        "transition_stage_policy": "public_model_methods_only",
        "administrative_closeout_fields_reproduced_from_current_step_source": [
            "step_index",
            "time",
            "observables",
            "params_identity",
            "cached_quantities.last_step_trace",
            "cached_quantities.current_step_events",
        ],
        "harness_boundary": "validation_replay_not_replacement_runtime",
    }


def observation_noninterference_control(fixture: dict[str, Any]) -> dict[str, Any]:
    model = GRC9V3.from_state(fixture["state"], fixture["params"])
    model.rebuild_differential_state()
    model.rebuild_transport_state()
    before = runtime_state_payload(model)
    before_digest = semantic_digest(before)
    snapshot = model.snapshot()
    after_snapshot = runtime_state_payload(model)
    model.compute_observables()
    after_observables = runtime_state_payload(model)
    semantic_digest(snapshot)
    after_hash = runtime_state_payload(model)
    with tempfile.TemporaryDirectory() as temporary_directory:
        path = Path(temporary_directory) / "observer_noninterference.json"
        model.save(str(path))
        after_save = runtime_state_payload(model)
        restored = GRC9V3.load(str(path))
    after_load_elsewhere = runtime_state_payload(model)
    checks = {
        "snapshot_capture_nonmutating": before == after_snapshot,
        "diagnostic_read_nonmutating": before == after_observables,
        "artifact_hash_nonmutating": before == after_hash,
        "save_nonmutating": before == after_save,
        "load_into_fresh_model_does_not_mutate_source": before == after_load_elsewhere,
        "restored_current_state_exact": before == runtime_state_payload(restored),
    }
    return {
        "input_runtime_state_sha256": before_digest,
        "post_operation_runtime_state_sha256": {
            "snapshot": semantic_digest(after_snapshot),
            "diagnostic_read": semantic_digest(after_observables),
            "artifact_hash": semantic_digest(after_hash),
            "save": semantic_digest(after_save),
            "load_elsewhere": semantic_digest(after_load_elsewhere),
        },
        "checks": checks,
        "status": "passed" if all(checks.values()) else "failed",
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
    observed_stage_records = deepcopy(traced.instrumentation_stage_records)
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
        "call_multiplicity_recorded": len(observed_stage_records)
        == len(EXPECTED_HIGH_LEVEL_CALL_ORDER),
        "every_call_has_input_output_digest": all(
            record["input_state_sha256"] and record["output_state_sha256"]
            for record in observed_stage_records
        ),
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
        "observed_call_counts": dict(sorted(Counter(observed_high_level_calls).items())),
        "observed_stage_records": observed_stage_records,
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
    base_k_digest = semantic_digest(base_state.cached_quantities["hybrid_node_tensors"])
    amplitude_rows: list[dict[str, Any]] = []
    for amplitude in K_COUNTERFACTUAL_AMPLITUDES:
        changed_state = perturb_hybrid_tensors(base_state, amplitude)
        changed_k = changed_state.cached_quantities["hybrid_node_tensors"]
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
        full_current_state_equal = (
            runtime_state_payload(full_base) == runtime_state_payload(full_changed)
        )
        final_k_equal = (
            full_base.get_state().cached_quantities.get("hybrid_node_tensors")
            == full_changed.get_state().cached_quantities.get("hybrid_node_tensors")
        )
        amplitude_rows.append(
            {
                "amplitude": amplitude,
                "counterfactual_k_sha256": semantic_digest(changed_k),
                "input_tensor_structure_valid": tensor_structure_valid(changed_k),
                "transport_exact_numeric_equal": transport_delta == 0.0,
                "transport_max_delta": transport_delta,
                "full_step_physical_max_delta": full_delta,
                "full_step_current_runtime_state_equal": full_current_state_equal,
                "differential_stage_overwrites_counterfactual_cache": final_k_equal,
            }
        )
    checks = {
        "all_counterfactual_caches_differ": all(
            row["counterfactual_k_sha256"] != base_k_digest for row in amplitude_rows
        ),
        "all_counterfactuals_structurally_valid": all(
            row["input_tensor_structure_valid"] for row in amplitude_rows
        ),
        "all_transport_outputs_exactly_equal": all(
            row["transport_exact_numeric_equal"] for row in amplitude_rows
        ),
        "all_full_step_current_states_equal": all(
            row["full_step_current_runtime_state_equal"] for row in amplitude_rows
        ),
        "differential_stage_overwrites_every_counterfactual_cache": all(
            row["differential_stage_overwrites_counterfactual_cache"]
            for row in amplitude_rows
        ),
    }
    return {
        "intervened_surface": "cached_quantities.hybrid_node_tensors",
        "base_k_digest": base_k_digest,
        "amplitude_rows": amplitude_rows,
        "checks": checks,
        "classification": "diagnostic_only_not_consumed_on_tested_F0_fixed_topology_no_event_transport_path_and_overwritten_before_full_step_use",
        "global_causal_absence_claimed": False,
        "comparison_policy": "exact_numeric_equality_required_for_non_K_transport_outputs",
        "status": "passed" if all(checks.values()) else "failed",
    }


def sign_stage_record(
    stage: str, positive: GRC9V3, negative: GRC9V3
) -> dict[str, Any]:
    positive_state = positive.get_state()
    negative_state = negative.get_state()
    return {
        "stage": stage,
        "positive_state_sha256": semantic_digest(runtime_state_payload(positive)),
        "negative_state_sha256": semantic_digest(runtime_state_payload(negative)),
        "base_conductance_max_delta": max_numeric_delta(
            mapping(positive_state.base_conductance),
            mapping(negative_state.base_conductance),
        ),
        "potential_max_delta": max_numeric_delta(
            mapping(positive_state.potential), mapping(negative_state.potential)
        ),
        "current_pair": [
            positive_state.port_edges[0].flux_uv,
            negative_state.port_edges[0].flux_uv,
        ],
        "net_flux_summary_pair": [
            list(positive_state.nodes[0].net_flux_summary),
            list(negative_state.nodes[0].net_flux_summary),
        ],
        "hybrid_tensor_pair_equal": positive_state.cached_quantities.get(
            "hybrid_node_tensors"
        )
        == negative_state.cached_quantities.get("hybrid_node_tensors"),
    }


def current_sign_control(fixture: dict[str, Any]) -> dict[str, Any]:
    prepared = GRC9V3.from_state(fixture["state"], fixture["params"])
    prepared.rebuild_differential_state()
    positive_state = replace_flux(prepared.get_state(), 4.0)
    negative_state = replace_flux(prepared.get_state(), -4.0)
    zero_state = replace_flux(prepared.get_state(), 0.0)

    positive_stage = GRC9V3.from_state(positive_state, fixture["params"])
    negative_stage = GRC9V3.from_state(negative_state, fixture["params"])
    stagewise = [sign_stage_record("declared_old_current_input", positive_stage, negative_stage)]
    positive_stage.rebuild_differential_state()
    negative_stage.rebuild_differential_state()
    stagewise.append(
        sign_stage_record("after_pre_flux_differential_rebuild", positive_stage, negative_stage)
    )
    evolution = positive_stage.get_params().evolution
    modes = positive_stage.get_params().constitutive_semantic_modes
    compute_base_conductance(positive_stage.get_state(), evolution=evolution, modes=modes)
    compute_base_conductance(negative_stage.get_state(), evolution=evolution, modes=modes)
    stagewise.append(
        sign_stage_record("after_base_conductance_formation", positive_stage, negative_stage)
    )
    compute_edge_labels(
        positive_stage.get_state(), evolution=evolution, modes=modes, pre_flux_only=True
    )
    compute_edge_labels(
        negative_stage.get_state(), evolution=evolution, modes=modes, pre_flux_only=True
    )
    compute_potential(positive_stage.get_state(), evolution=evolution)
    compute_potential(negative_stage.get_state(), evolution=evolution)
    stagewise.append(
        sign_stage_record("after_potential_reconstruction", positive_stage, negative_stage)
    )
    compute_flux(positive_stage.get_state(), evolution=evolution)
    compute_flux(negative_stage.get_state(), evolution=evolution)
    stagewise.append(
        sign_stage_record("after_current_reconstruction", positive_stage, negative_stage)
    )
    compute_edge_labels(
        positive_stage.get_state(), evolution=evolution, modes=modes, pre_flux_only=False
    )
    compute_edge_labels(
        negative_stage.get_state(), evolution=evolution, modes=modes, pre_flux_only=False
    )
    positive_stage.apply_continuity()
    negative_stage.apply_continuity()
    stagewise.append(
        sign_stage_record("after_continuity", positive_stage, negative_stage)
    )

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
    positive_result = positive_full.step()
    negative_result = negative_full.step()
    stagewise.append(sign_stage_record("after_complete_step", positive_full, negative_full))
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
        "old_current_is_nondegenerate": abs(positive_state.port_edges[0].flux_uv) >= 1.0,
        "coherence_fixture_is_asymmetric": positive_state.nodes[0].coherence
        != positive_state.nodes[1].coherence,
        "both_complete_steps_remain_no_event": not positive_result.events
        and not negative_result.events,
        "both_complete_steps_remain_positive": min(
            node.coherence for node in positive_full.get_state().nodes.values()
        )
        > 0.0
        and min(node.coherence for node in negative_full.get_state().nodes.values())
        > 0.0,
        "stagewise_sign_is_visible_before_transport": stagewise[1][
            "net_flux_summary_pair"
        ][0]
        != stagewise[1]["net_flux_summary_pair"][1],
        "stagewise_conductance_is_sign_even": stagewise[2][
            "base_conductance_max_delta"
        ]
        == 0.0,
        "stagewise_potential_is_sign_even": stagewise[3]["potential_max_delta"]
        == 0.0,
        "stagewise_current_is_reconstructed_equal": stagewise[4]["current_pair"][0]
        == stagewise[4]["current_pair"][1],
    }
    return {
        "physical_reversal": "fixed_edge_coordinates_J_to_minus_J",
        "transport_sign_pair_max_delta": sign_delta,
        "full_step_sign_pair_max_delta": full_delta,
        "J4_vs_J0_base_conductance_absolute_delta": magnitude_delta,
        "stagewise_trace": stagewise,
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


def reverse_edge_coordinate_mapping(state: dict[str, Any]) -> dict[str, Any]:
    reversed_state = deepcopy(state)
    edge = reversed_state["topology"]["edges"][0]
    edge["endpoint_a"], edge["endpoint_b"] = edge["endpoint_b"], edge["endpoint_a"]
    port_edge = reversed_state["port_edges"]["0"]
    reversed_state["port_edges"]["0"] = {
        "node_u": port_edge["node_v"],
        "port_u": port_edge["port_v"],
        "node_v": port_edge["node_u"],
        "port_v": port_edge["port_u"],
        "conductance": port_edge["conductance"],
        "flux_uv": -float(port_edge["flux_uv"]),
    }
    return reversed_state


def edge_reorientation_control(fixture: dict[str, Any]) -> dict[str, Any]:
    normal_state = deepcopy(fixture["state"])
    normal_state["port_edges"]["0"]["flux_uv"] = 4.0
    reversed_state = reverse_edge_coordinate_mapping(normal_state)
    twice_reversed_state = reverse_edge_coordinate_mapping(reversed_state)
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
        "coordinate_transform_is_involution": twice_reversed_state == normal_state,
        "raw_coordinate_orientation_changed": raw_endpoint_order_differs,
        "current_coordinate_sign_mapped": canonical_port_edges_equal,
        "physical_transport_covariant": output_delta == 0.0,
        "inverse_identification_restores_raw_state": reverse_edge_coordinate_mapping(
            reversed_state
        )
        == normal_state,
    }
    return {
        "control": "edge_coordinate_reorientation_with_J_sign_map",
        "normal_raw_endpoints": normal_state["topology"]["edges"][0],
        "reoriented_raw_endpoints": reversed_state["topology"]["edges"][0],
        "transport_max_delta": output_delta,
        "orientation_dependent_surfaces_transformed": [
            "topology.edges.0.endpoint_a",
            "topology.edges.0.endpoint_b",
            "port_edges.0.node_u",
            "port_edges.0.port_u",
            "port_edges.0.node_v",
            "port_edges.0.port_v",
            "port_edges.0.flux_uv",
        ],
        "derived_orientation_surfaces_policy": "rebuild_from_consistently_transformed_primary_state_before_comparison",
        "checks": checks,
        "classification": "coordinate_covariance_passed_distinct_from_physical_current_reversal",
        "status": "passed" if all(checks.values()) else "failed",
    }


def clone_isolation_control(fixture: dict[str, Any]) -> dict[str, Any]:
    model = GRC9V3.from_state(fixture["state"], fixture["params"])
    model.rebuild_differential_state()
    model.rebuild_transport_state()
    source = runtime_state_payload(model)
    source_digest = semantic_digest(source)

    def mutate_conductance(value: dict[str, Any], delta: float) -> None:
        value["base_conductance"]["0"] += delta
        value["port_edges"]["0"]["conductance"] += delta

    def mutate_current(value: dict[str, Any], delta: float) -> None:
        value["port_edges"]["0"]["flux_uv"] += delta

    def mutate_cache(value: dict[str, Any], delta: float) -> None:
        value["cached_quantities"]["clone_isolation_probe"] = delta

    def mutate_k(value: dict[str, Any], delta: float) -> None:
        value["cached_quantities"]["hybrid_node_tensors"]["0"][0][0] += delta

    def mutate_rng(value: dict[str, Any], delta: float) -> None:
        value["rng_state"]["state"][1][0] += int(delta)

    mutators: dict[str, Callable[[dict[str, Any], float], None]] = {
        "conductance_surfaces": mutate_conductance,
        "current_flux_surface": mutate_current,
        "cached_quantities": mutate_cache,
        "hybrid_tensor_cache": mutate_k,
        "rng_state": mutate_rng,
    }
    rows: list[dict[str, Any]] = []
    for surface, mutate in mutators.items():
        clone_a = exact_deep_clone(source)
        clone_b = exact_deep_clone(source)
        mutate(clone_a, 1.0)
        clone_a_after_first = semantic_digest(clone_a)
        b_unchanged_after_a = semantic_digest(clone_b) == source_digest
        mutate(clone_b, 2.0)
        rows.append(
            {
                "surface": surface,
                "clone_A_changed": clone_a_after_first != source_digest,
                "clone_B_unchanged_after_A_mutation": b_unchanged_after_a,
                "clone_B_changed": semantic_digest(clone_b) != source_digest,
                "clone_A_unchanged_after_B_mutation": semantic_digest(clone_a)
                == clone_a_after_first,
                "source_unchanged": semantic_digest(source) == source_digest,
            }
        )
    return {
        "source_state_sha256": source_digest,
        "rows": rows,
        "status": "passed"
        if all(
            all(value for key, value in row.items() if key != "surface")
            for row in rows
        )
        else "failed",
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
    clone_isolation = clone_isolation_control(fixture)
    checks = {
        "clone_first_source_unchanged": source_unchanged,
        "declared_path_changed": clone_changed,
        "canonical_json_round_trip_exact": canonical_round_trip,
        "deep_clone_non_aliasing": deep_clone_non_aliasing,
        "runtime_snapshot_replay_physical_projection_exact": replay_delta == 0.0,
        "raw_snapshot_and_derived_projection_separate": raw_snapshot_digest
        != derived_projection_digest,
        "nested_clone_isolation_passed": clone_isolation["status"] == "passed",
    }
    result = {
        "raw_snapshot_committed": False,
        "raw_snapshot_sha256": raw_snapshot_digest,
        "derived_projection_sha256": derived_projection_digest,
        "runtime_snapshot_replay_max_delta": replay_delta,
        "nested_clone_isolation": clone_isolation,
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


def replace_port_conductance(state: GRC9V3State, conductance: float) -> None:
    edge = state.port_edges[0]
    state.port_edges[0] = PortEdge(
        node_u=edge.node_u,
        port_u=edge.port_u,
        node_v=edge.node_v,
        port_v=edge.port_v,
        conductance=float(conductance),
        flux_uv=edge.flux_uv,
    )


def surface_authority_map(
    fixture: dict[str, Any], k_control: dict[str, Any]
) -> dict[str, Any]:
    prepared = GRC9V3.from_state(fixture["state"], fixture["params"])
    prepared.rebuild_differential_state()
    prepared.rebuild_transport_state()
    base_state = deepcopy(prepared.get_state())
    evolution = prepared.get_params().evolution
    modes = prepared.get_params().constitutive_semantic_modes

    w_states: dict[str, GRC9V3State] = {
        lane: deepcopy(base_state)
        for lane in ("control", "base_only", "edge_copy_only", "both_consistent")
    }
    target_w = 0.25
    w_states["base_only"].base_conductance[0] = target_w
    replace_port_conductance(w_states["edge_copy_only"], target_w)
    w_states["both_consistent"].base_conductance[0] = target_w
    replace_port_conductance(w_states["both_consistent"], target_w)
    w_outputs: dict[str, dict[str, Any]] = {}
    for lane, state in w_states.items():
        compute_potential(state, evolution=evolution)
        compute_flux(state, evolution=evolution)
        w_outputs[lane] = {
            "potential": mapping(state.potential),
            "reconstructed_flux_uv": state.port_edges[0].flux_uv,
        }

    j_states: dict[str, GRC9V3State] = {
        lane: deepcopy(base_state)
        for lane in ("control", "port_edge_only", "oriented_cache_only", "both_consistent")
    }
    target_j = 1000.0
    j_states["port_edge_only"] = replace_flux(j_states["port_edge_only"], target_j)
    j_states["both_consistent"] = replace_flux(j_states["both_consistent"], target_j)
    for lane in ("oriented_cache_only", "both_consistent"):
        j_states[lane].cached_quantities["oriented_flux"] = {
            "0": {"0": target_j, "1": -target_j}
        }
    j_outputs: dict[str, float] = {}
    for lane, state in j_states.items():
        compute_base_conductance(state, evolution=evolution, modes=modes)
        j_outputs[lane] = state.base_conductance[0]

    checks = {
        "W_base_only_matches_both_consistent": w_outputs["base_only"]
        == w_outputs["both_consistent"],
        "W_edge_copy_only_matches_control": w_outputs["edge_copy_only"]
        == w_outputs["control"],
        "W_base_only_changes_consumer_output": w_outputs["base_only"]
        != w_outputs["control"],
        "J_port_edge_only_matches_both_consistent": j_outputs["port_edge_only"]
        == j_outputs["both_consistent"],
        "J_oriented_cache_only_matches_control": j_outputs["oriented_cache_only"]
        == j_outputs["control"],
        "J_port_edge_only_changes_conductance": j_outputs["port_edge_only"]
        != j_outputs["control"],
        "K_multi_amplitude_fixed_path_control_passed": k_control["status"] == "passed",
    }
    return {
        "schema_scope": "current_GRC9V3_F0_fixed_topology_no_event_path",
        "records": [
            {
                "logical_quantity": "W_base_conductance",
                "canonical_producer": "grc_9_v3_runtime.compute_base_conductance",
                "canonical_consumers": [
                    "grc_9_v3_runtime.compute_potential",
                    "grc_9_v3_runtime.compute_flux",
                ],
                "authoritative_surface": "state.base_conductance",
                "duplicate_or_fallback_surfaces": ["state.port_edges[*].conductance"],
                "rebuild_stage": "rebuild_transport_state.compute_base_conductance",
                "overwrite_stage": "rebuild_transport_state.compute_base_conductance",
                "serialization_surfaces": [
                    "snapshot.edge_labels.base_conductance",
                    "snapshot.dynamics.state.base_conductance",
                    "snapshot.dynamics.state.port_edges[*].conductance",
                ],
                "mismatch_control_outputs": w_outputs,
                "result": "base_conductance_is_authoritative_for_potential_and_flux_when_present",
            },
            {
                "logical_quantity": "J_signed_edge_current",
                "canonical_producer": "grc_9_v3_runtime.compute_flux",
                "canonical_consumers": [
                    "grc_9_v3_runtime.compute_net_flux_summary_rows",
                    "grc_9_v3_runtime.compute_base_conductance",
                    "GRC9V3.apply_continuity",
                ],
                "authoritative_surface": "state.port_edges[*].flux_uv",
                "duplicate_or_derived_surfaces": [
                    "state.cached_quantities.oriented_flux",
                    "state.nodes[*].net_flux_summary",
                    "state.flux_coupling",
                ],
                "rebuild_stage": "rebuild_transport_state.compute_flux",
                "overwrite_stage": "rebuild_transport_state.compute_flux",
                "serialization_surfaces": [
                    "snapshot.dynamics.state.port_edges[*].flux_uv",
                    "snapshot.dynamics.state.cached_quantities.oriented_flux",
                ],
                "mismatch_control_outputs": j_outputs,
                "result": "port_edge_flux_is_authoritative_old_current_input",
            },
            {
                "logical_quantity": "K_hybrid_node_tensor",
                "canonical_producer": "grc_9_v3_runtime.rebuild_grc9v3_differential_state",
                "canonical_consumers": [],
                "authoritative_surface": "not_identified_as_a_consumer_input_on_tested_path",
                "duplicate_or_derived_surfaces": [
                    "state.cached_quantities.hybrid_node_tensors"
                ],
                "rebuild_stage": "rebuild_differential_state.compute_node_tensors",
                "overwrite_stage": "next_rebuild_differential_state",
                "serialization_surfaces": [
                    "snapshot.dynamics.state.cached_quantities.hybrid_node_tensors"
                ],
                "mismatch_control_outputs": k_control["amplitude_rows"],
                "result": "not_consumed_on_tested_F0_fixed_topology_no_event_path",
                "global_causal_absence_claimed": False,
            },
        ],
        "checks": checks,
        "status": "passed" if all(checks.values()) else "failed",
    }


def transition_environment_and_rng_control(fixture: dict[str, Any]) -> dict[str, Any]:
    model = GRC9V3.from_state(fixture["state"], fixture["params"])
    params = model.get_params()
    before_rng = semantic_digest(model.get_state().rng_state)
    result = model.step()
    after_rng = semantic_digest(model.get_state().rng_state)
    checks = {
        "params_identity_matches_runtime": model.get_state().params_identity
        == params.params_hash,
        "fixed_envelope_rng_does_not_advance": before_rng == after_rng,
        "fixed_envelope_has_no_events": not result.events,
    }
    resolved_config = canonicalize_json_value(params.resolved_config)
    return {
        "serialized_dynamic_state": "complete_GRC9V3State_inventory",
        "fixed_exogenous_transition_environment": {
            "raw_config_sha256": semantic_digest(fixture["params"]),
            "resolved_params_sha256": params.params_hash,
            "resolved_config": resolved_config,
            "dt": params.dt,
            "evolution": resolved_config["evolution"],
            "constitutive_semantic_modes": resolved_config[
                "constitutive_semantic_modes"
            ],
            "capabilities": sorted(model.list_capabilities()),
        },
        "global_runtime_configuration": "repository_revision_and_numerical_environment_recorded_by_GRV0",
        "solver_or_warm_start_state": "not_present_on_GRV1_F0_path",
        "administrative_counters": ["step_index", "time"],
        "observer_only_data": ["event_log", "observables", "coarse_cache"],
        "rng": {
            "classification": "causal_runtime_state_even_when_unchanged_on_F0",
            "before_sha256": before_rng,
            "after_sha256": after_rng,
            "advanced": before_rng != after_rng,
        },
        "transition_claim": "future_is_conditioned_on_complete_state_and_frozen_transition_environment",
        "checks": checks,
        "status": "passed" if all(checks.values()) else "failed",
    }


def fresh_process_probe_payload(fixture: dict[str, Any]) -> dict[str, Any]:
    model = GRC9V3.from_state(fixture["state"], fixture["params"])
    initial_state = deepcopy(model.get_state())
    model.rebuild_differential_state()
    model.rebuild_transport_state()
    transport = transport_projection(model)

    repeated = GRC9V3.from_state(fixture["state"], fixture["params"])
    repeated.step()
    step_state = runtime_state_payload(repeated)
    return {
        "transport_projection": transport,
        "complete_step_state_sha256": semantic_digest(step_state),
        "initial_state_sha256": semantic_digest(_state_payload_from_state(initial_state)),
    }


def fresh_process_replay_control(fixture: dict[str, Any]) -> dict[str, Any]:
    local = fresh_process_probe_payload(fixture)

    same_object = GRC9V3.from_state(fixture["state"], fixture["params"])
    initial_state = deepcopy(same_object.get_state())
    same_object.step()
    first_same_object = semantic_digest(runtime_state_payload(same_object))
    same_object.set_state(initial_state)
    same_object.step()
    second_same_object = semantic_digest(runtime_state_payload(same_object))

    pre_step = GRC9V3.from_state(fixture["state"], fixture["params"])
    with tempfile.TemporaryDirectory() as temporary_directory:
        path = Path(temporary_directory) / "fresh_instance_input.json"
        pre_step.save(str(path))
        loaded = GRC9V3.load(str(path))
    loaded.step()
    loaded_digest = semantic_digest(runtime_state_payload(loaded))

    process = subprocess.run(
        [sys.executable, str(Path(__file__).resolve()), "--fresh-process-probe"],
        cwd=REPO_ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    fresh = json.loads(process.stdout)
    checks = {
        "same_object_exact_input_replay_equal": first_same_object
        == second_same_object,
        "fresh_instance_snapshot_load_replay_equal": loaded_digest
        == local["complete_step_state_sha256"],
        "fresh_python_process_equal": fresh == local,
    }
    return {
        "local_probe": local,
        "fresh_process_probe": fresh,
        "checks": checks,
        "status": "passed" if all(checks.values()) else "failed",
        "scope": "exact_same_declared_F0_input_not_uninterrupted_repeated_dynamics",
    }


def state_field_inventory() -> dict[str, Any]:
    classifications = {
        "topology": ("causal_runtime_state", True, "controls adjacency and port incidence"),
        "node_values": ("unknown", True, "inherited family-neutral placeholder with no current GRC9V3 read; nonuse on F0 does not prove global inertness"),
        "edge_values": ("unknown", True, "inherited family-neutral placeholder with no current GRC9V3 read; nonuse on F0 does not prove global inertness"),
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
            "F4_control_definitions_consumed": [
                "edge_orientation_reversal_with_current_sign_change",
                "sign_reversed_old_current_at_matched_C_W",
            ],
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
    public_replay = public_stage_replay_control(fixture)
    observation = observation_noninterference_control(fixture)
    k_control = k_counterfactual(fixture)
    sign = current_sign_control(fixture)
    orientation = edge_reorientation_control(fixture)
    replay, intervention_payload = clone_and_replay_control(fixture)
    authority = surface_authority_map(fixture, k_control)
    environment = transition_environment_and_rng_control(fixture)
    process_replay = fresh_process_replay_control(fixture)
    inventory = state_field_inventory()
    checks = {
        "transport_anchor_passed": anchor["status"] == "passed",
        "step_trace_and_fixed_topology_passed": step["status"] == "passed",
        "public_stage_replay_passed": public_replay["status"] == "passed",
        "observation_noninterference_passed": observation["status"] == "passed",
        "K_counterfactual_passed": k_control["status"] == "passed",
        "current_sign_control_passed": sign["status"] == "passed",
        "edge_reorientation_control_passed": orientation["status"] == "passed",
        "clone_and_replay_control_passed": replay["status"] == "passed",
        "surface_authority_map_passed": authority["status"] == "passed",
        "transition_environment_and_rng_passed": environment["status"] == "passed",
        "fresh_process_replay_passed": process_replay["status"] == "passed",
        "all_runtime_fields_classified": inventory["all_runtime_fields_classified"],
    }
    instrumentation = envelope(
        {
            "gate_id": "GRV1",
            "specification_id": SPECIFICATION_ID,
            "status": "passed" if all(checks.values()) else "failed",
            "transport_anchor": anchor,
            "step_order_and_fixed_topology": step,
            "public_stage_replay": public_replay,
            "observation_noninterference": observation,
            "K_counterfactual": k_control,
            "current_sign_control": sign,
            "edge_reorientation_control": orientation,
            "clone_serialization_and_replay": replay,
            "transition_environment_and_rng": environment,
            "fresh_process_replay": process_replay,
            "excluded_and_administrative_field_inventory": inventory,
            "load_bearing_source_paths": list(LOAD_BEARING_PATHS),
            "comparison_policy": {
                "K_unread_path": "exact_numeric_equality_required",
                "instrumented_vs_ordinary": "exact_complete_runtime_snapshot_required",
                "public_stage_replay": "exact_stage_boundary_and_final_state_required",
                "fresh_process_replay": "exact_canonical_current_state_digest_required",
                "transport_anchor_literals": "declared_derived_surface_tolerance",
                "categorical_and_identifier_fields": "exact_required",
            },
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
    authority_record = envelope(authority, "b1_grv1_surface_authority_map_v1")
    return {
        "instrumentation_validation.json": instrumentation,
        "fixture_registry.json": fixture_registry(fixture, anchor),
        "intervention_registry.json": interventions,
        "surface_authority_map.json": authority_record,
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
                "## Observation And Replay Integrity",
                "",
                "The instrumented and ordinary steps produce exactly equal complete",
                "runtime snapshots. Every high-level call records its ordinal, input",
                "digest, output digest, and changed top-level fields. An experiment-local",
                "replay of the current public stage sequence matches every captured stage",
                "boundary and the final state. Snapshot capture, diagnostic reads, hashing,",
                "save, and load do not mutate the observed source model. Same-input runs",
                "also agree across reset-to-input reuse, a fresh instance, snapshot/load,",
                "and a fresh Python process.",
                "",
                "## Source-Fidelity Findings",
                "",
                "- Structurally valid small, moderate, and large diagonal K interventions",
                "  produce exact non-K transport equality, and the first differential",
                "  stage overwrites them before full-step use. This is a fixed-topology,",
                "  no-event F0 result; it is not a global K-causality claim.",
                "- Prior current magnitude has a direct sign-even `J^2` path into the next",
                "  conductance. Under F0 its measured effect is below the declared `W`",
                "  tolerance, so GRV1 records the source path without promoting a resolved",
                "  magnitude-retention claim.",
                "- The stagewise `J -> -J` trace shows sign in the pre-transport net-flux",
                "  summary, exact sign-even conductance and potential, equal reconstructed",
                "  current, and final equality after the later differential refresh.",
                "- Reversing the edge coordinate while mapping `J -> -J` preserves physical",
                "  transport exactly; the coordinate transform is explicitly involutive.",
                "  Coordinate covariance is distinct from physical current reversal.",
                "",
                "## Surface Authority",
                "",
                "Mismatch controls identify `state.base_conductance` as authoritative for",
                "potential/flux when present, and `state.port_edges[*].flux_uv` as the",
                "authoritative old-current input. Edge conductance, oriented-flux cache,",
                "net-flux summaries, and flux coupling are duplicate, fallback, or derived",
                "surfaces with separately recorded rebuild and overwrite stages. K has no",
                "identified consumer on the tested path. The full map is emitted as",
                "`outputs/surface_authority_map.json`.",
                "",
                "## Current Classification",
                "",
                "```text",
                f"magnitude = {sign['classification']['magnitude_persistence']}",
                f"axis = {sign['classification']['unoriented_axis_persistence']}",
                f"orientation = {sign['classification']['orientation_persistence']}",
                "current_reconstructed_anew = true",
                "K_cache = not_consumed_on_tested_F0_fixed_topology_no_event_path",
                "```",
                "",
                "## State Closure Handoff",
                "",
                "Every `GRC9V3State` dataclass field is classified. Causal and mixed",
                "runtime fields remain explicit GRV3 closure candidates; exclusion from",
                "the physical projection is not treated as proof of causal irrelevance.",
                "The transition environment is recorded separately from dynamic state,",
                "and RNG remains classified as causal even though it does not advance in",
                "the lambda-birth-zero F0 envelope.",
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
            "supersedes_candidate_receipt_sha256": SUPERSEDED_GRV1_RECEIPT_SHA256,
            "supersession_reason": "pre_acceptance_source_fidelity_review_strengthening",
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--fresh-process-probe", action="store_true")
    args = parser.parse_args()
    if args.fresh_process_probe:
        print(
            json.dumps(
                fresh_process_probe_payload(load_fixture()),
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return
    run_grv1()
    print("GRV1 mechanically validated; scientific acceptance anchor is pending.")


if __name__ == "__main__":
    main()
