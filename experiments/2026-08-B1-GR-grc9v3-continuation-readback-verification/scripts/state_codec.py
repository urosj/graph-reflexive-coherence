"""Experiment-local canonical state and branch-coordinate codecs for GRV3."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, replace
import json
import sys
from typing import Any, Iterable

import numpy as np
from numpy.typing import NDArray

from artifact_io import REPO_ROOT, canonical_json_bytes
from tangent_basis import zero_sum_basis

SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from pygrc.models import GRC9V3  # noqa: E402


FIRST_SCIENTIFIC_GATE = "GRV3"


def encode_json_state(state: Any) -> bytes:
    return canonical_json_bytes(state)


def decode_json_state(encoded: bytes) -> Any:
    return json.loads(encoded.decode("utf-8"))


def canonical_clone(state: Any) -> Any:
    return decode_json_state(encode_json_state(state))


def exact_deep_clone(state: Any) -> Any:
    return deepcopy(state)


@dataclass(frozen=True)
class BranchCoordinateChart:
    """A fixed-branch chart whose omitted state is reset by the decoder."""

    base_state: Any
    params: dict[str, Any]
    node_order: tuple[int, ...]
    edge_order: tuple[int, ...]
    base_coherence: NDArray[np.float64]
    coherence_basis: NDArray[np.float64]
    admitted_blocks: tuple[str, ...]

    @classmethod
    def from_model(
        cls,
        model: GRC9V3,
        admitted_blocks: Iterable[str] = ("C", "W", "J"),
    ) -> "BranchCoordinateChart":
        blocks = tuple(admitted_blocks)
        if (
            not blocks
            or blocks[0] != "C"
            or any(block not in {"C", "W", "J"} for block in blocks)
        ):
            raise ValueError("admitted blocks must start with C and use only C/W/J")
        state = model.get_state()
        node_order = tuple(sorted(state.topology.iter_live_node_ids()))
        edge_order = tuple(sorted(state.topology.iter_live_edge_ids()))
        coherence = np.asarray(
            [float(state.nodes[node_id].coherence) for node_id in node_order],
            dtype=float,
        )
        return cls(
            base_state=deepcopy(state),
            params=dict(model.get_params().raw_config),
            node_order=node_order,
            edge_order=edge_order,
            base_coherence=coherence,
            coherence_basis=zero_sum_basis(len(node_order)),
            admitted_blocks=blocks,
        )

    @property
    def coordinate_labels(self) -> tuple[str, ...]:
        labels = [
            f"C_tangent[{index}]" for index in range(self.coherence_basis.shape[1])
        ]
        if "W" in self.admitted_blocks:
            labels.extend(f"W[{edge_id}]" for edge_id in self.edge_order)
        if "J" in self.admitted_blocks:
            labels.extend(f"J[{edge_id}]" for edge_id in self.edge_order)
        return tuple(labels)

    @property
    def block_slices(self) -> dict[str, tuple[int, int]]:
        start = 0
        result: dict[str, tuple[int, int]] = {}
        for block, size in (
            ("C", self.coherence_basis.shape[1]),
            ("W", len(self.edge_order)),
            ("J", len(self.edge_order)),
        ):
            if block in self.admitted_blocks:
                result[block] = (start, start + size)
                start += size
        return result

    def encode_model(self, model: GRC9V3) -> NDArray[np.float64]:
        state = model.get_state()
        coherence = np.asarray(
            [float(state.nodes[node_id].coherence) for node_id in self.node_order],
            dtype=float,
        )
        values = list(self.coherence_basis.T @ (coherence - self.base_coherence))
        if "W" in self.admitted_blocks:
            values.extend(
                float(state.base_conductance[edge_id]) for edge_id in self.edge_order
            )
        if "J" in self.admitted_blocks:
            values.extend(
                float(state.port_edges[edge_id].flux_uv) for edge_id in self.edge_order
            )
        return np.asarray(values, dtype=float)

    def decode_model(self, coordinate: NDArray[np.float64]) -> GRC9V3:
        values = np.asarray(coordinate, dtype=float)
        if values.shape != (len(self.coordinate_labels),):
            raise ValueError("coordinate shape does not match chart")
        state = deepcopy(self.base_state)
        c_start, c_end = self.block_slices["C"]
        coherence = self.base_coherence + self.coherence_basis @ values[c_start:c_end]
        if np.any(coherence <= 0.0):
            raise ValueError("decoded coherence must remain interior-positive")
        for node_id, value in zip(self.node_order, coherence, strict=True):
            state.nodes[node_id].coherence = float(value)
        if "W" in self.admitted_blocks:
            start, end = self.block_slices["W"]
            conductance = values[start:end]
            if np.any(conductance <= 0.0):
                raise ValueError("decoded conductance must remain interior-positive")
            for edge_id, value in zip(self.edge_order, conductance, strict=True):
                state.base_conductance[edge_id] = float(value)
                state.port_edges[edge_id] = replace(
                    state.port_edges[edge_id], conductance=float(value)
                )
        if "J" in self.admitted_blocks:
            start, end = self.block_slices["J"]
            for edge_id, value in zip(self.edge_order, values[start:end], strict=True):
                state.port_edges[edge_id] = replace(
                    state.port_edges[edge_id], flux_uv=float(value)
                )
        return GRC9V3.from_state(state, self.params)

    def descriptor(self) -> dict[str, Any]:
        return {
            "codec_id": "grv3_branch_relative_cwj_codec_v1",
            "admitted_blocks": list(self.admitted_blocks),
            "node_order": list(self.node_order),
            "edge_order": list(self.edge_order),
            "coordinate_order": list(self.coordinate_labels),
            "block_slices": {
                key: list(value) for key, value in self.block_slices.items()
            },
            "coherence_basis": self.coherence_basis.tolist(),
            "decoder_omitted_state_policy": "reset_to_exact_branch_snapshot_then_apply_declared_coordinate",
        }


def physical_continuous_blocks(
    model: GRC9V3, node_order: Iterable[int], edge_order: Iterable[int]
) -> dict[str, list[float]]:
    state = model.get_state()
    nodes = tuple(node_order)
    edges = tuple(edge_order)
    return {
        "C": [float(state.nodes[node_id].coherence) for node_id in nodes],
        "W": [float(state.base_conductance[edge_id]) for edge_id in edges],
        "J": [float(state.port_edges[edge_id].flux_uv) for edge_id in edges],
    }


def categorical_signature(model: GRC9V3, *, current_zero_band: float) -> dict[str, Any]:
    state = model.get_state()
    current_sign = {}
    for edge_id in sorted(state.port_edges):
        value = float(state.port_edges[edge_id].flux_uv)
        current_sign[str(edge_id)] = (
            "zero"
            if abs(value) <= current_zero_band
            else ("positive" if value > 0.0 else "negative")
        )
    return {
        "topology_nodes": list(sorted(state.topology.iter_live_node_ids())),
        "topology_edges": list(sorted(state.topology.iter_live_edge_ids())),
        "edge_ports": {
            str(edge_id): [
                list(endpoint) for endpoint in state.topology.edge_ports(edge_id)
            ]
            for edge_id in sorted(state.topology.iter_live_edge_ids())
        },
        "current_sign_class": current_sign,
        "sink_set": list(sorted(state.sink_set)),
        "basins": {
            str(key): list(sorted(value)) for key, value in sorted(state.basins.items())
        },
        "hierarchy": {
            str(key): list(value)
            for key, value in sorted(
                state.hierarchy.items(), key=lambda item: str(item[0])
            )
        },
        "expansion_registry_keys": list(sorted(state.expansion_registry)),
        "choice_registry_keys": list(sorted(state.choice_registry)),
        "collapse_registry_keys": list(sorted(state.collapse_registry)),
        "event_kinds": [event.kind for event in state.event_log],
        "budget_clipped_nodes": [
            node_id
            for node_id in sorted(state.nodes)
            if float(state.nodes[node_id].coherence) <= 0.0
        ],
    }


def runtime_path_signature(model: GRC9V3) -> list[str]:
    return list(model.get_state().cached_quantities.get("last_step_trace", ()))
