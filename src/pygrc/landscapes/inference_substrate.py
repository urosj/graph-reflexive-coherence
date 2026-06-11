"""Checkpoint evidence substrate for landscape inference classifiers."""

from __future__ import annotations

from collections import deque
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import math
from typing import Any

from pygrc.core import canonicalize_json_value

from .inference import LandscapeInferenceWindow


PortMatrix = tuple[tuple[bool, bool, bool], tuple[bool, bool, bool], tuple[bool, bool, bool]]


@dataclass(frozen=True)
class LandscapeInferenceBudgetAudit:
    """Read-only checkpoint budget audit."""

    budget_sum: float | None
    budget_target: float | None
    budget_error: float | None
    quadrature_weight_mode: str
    budget_available: bool
    budget_accountability: str

    def to_mapping(self) -> dict[str, Any]:
        return {
            "budget_sum": self.budget_sum,
            "budget_target": self.budget_target,
            "budget_error": self.budget_error,
            "quadrature_weight_mode": self.quadrature_weight_mode,
            "budget_available": self.budget_available,
            "budget_accountability": self.budget_accountability,
        }


@dataclass(frozen=True)
class LandscapeInferenceEdgeEvidence:
    """Normalized checkpoint edge evidence."""

    edge_id: int
    source_node_id: int
    target_node_id: int
    source_port_id: int | None
    target_port_id: int | None
    conductance: float | None
    signed_flux: float | None
    geometric_length: float | None
    temporal_delay: float | None
    flux_coupling: float | None
    payload: Mapping[str, Any]
    bridge_detection_mode: str
    is_bridge: bool
    provenance: Mapping[str, Any]


@dataclass(frozen=True)
class LandscapeInferenceNodeEvidence:
    """Normalized checkpoint node evidence."""

    node_id: int
    coherence: float | None
    quadrature_weight: float | None
    sink_flag: bool
    basin_id: str | None
    basin_mass: float | None
    parent_id: str | None
    depth: int | None
    gradient_norm: float | None
    min_signed_hessian: float | None
    tensor_trace: float | None
    tensor_anisotropy: float | None
    payload: Mapping[str, Any]
    port_matrix: PortMatrix | None
    provenance: Mapping[str, Any]


@dataclass(frozen=True)
class LandscapeInferencePathEvidence:
    """Deterministic path candidate and aggregate evidence."""

    node_ids: tuple[int, ...]
    edge_ids: tuple[int, ...]
    bottleneck_conductance: float | None
    total_abs_flux: float | None
    mean_abs_flux: float | None
    bridge_edge_ids: tuple[int, ...]
    directionality: str

    def to_mapping(self) -> dict[str, Any]:
        return {
            "node_ids": list(self.node_ids),
            "edge_ids": list(self.edge_ids),
            "bottleneck_conductance": self.bottleneck_conductance,
            "total_abs_flux": self.total_abs_flux,
            "mean_abs_flux": self.mean_abs_flux,
            "bridge_edge_ids": list(self.bridge_edge_ids),
            "directionality": self.directionality,
        }


@dataclass(frozen=True)
class LandscapeInferencePathPersistence:
    """Checkpoint-window persistence for a candidate path."""

    checkpoint_count: int
    present_count: int
    ruptured_count: int
    missing_node_ids: tuple[int, ...]
    missing_edge_pairs: tuple[tuple[int, int], ...]
    diagnostic_only: bool

    def to_mapping(self) -> dict[str, Any]:
        return {
            "checkpoint_count": self.checkpoint_count,
            "present_count": self.present_count,
            "ruptured_count": self.ruptured_count,
            "missing_node_ids": list(self.missing_node_ids),
            "missing_edge_pairs": [list(pair) for pair in self.missing_edge_pairs],
            "diagnostic_only": self.diagnostic_only,
        }


@dataclass(frozen=True)
class LandscapeInferencePathFluxStability:
    """Flux stability for one path across a checkpoint window."""

    checkpoint_count: int
    observed_count: int
    observed_fraction: float
    flux_series: tuple[float | None, ...]
    mean_abs_flux: float | None
    min_abs_flux: float | None
    max_abs_flux: float | None
    coefficient_of_variation: float | None
    stability_score: float
    stability_mode: str

    def to_mapping(self) -> dict[str, Any]:
        return {
            "checkpoint_count": self.checkpoint_count,
            "observed_count": self.observed_count,
            "observed_fraction": self.observed_fraction,
            "flux_series": list(self.flux_series),
            "mean_abs_flux": self.mean_abs_flux,
            "min_abs_flux": self.min_abs_flux,
            "max_abs_flux": self.max_abs_flux,
            "coefficient_of_variation": self.coefficient_of_variation,
            "stability_score": self.stability_score,
            "stability_mode": self.stability_mode,
        }


@dataclass(frozen=True)
class LandscapeInferenceCheckpointGraph:
    """Normalized graph evidence for one checkpoint."""

    checkpoint_id: str
    step_index: int
    time: float | None
    graph_kind: str
    nodes: Mapping[int, LandscapeInferenceNodeEvidence]
    edges: Mapping[int, LandscapeInferenceEdgeEvidence]
    adjacency: Mapping[int, tuple[int, ...]]
    edge_id_by_pair: Mapping[tuple[int, int], int]
    port_matrix_available: bool
    provenance_available: bool
    bridge_edge_ids: tuple[int, ...]
    bridge_detection_modes: tuple[str, ...]
    budget_audit: LandscapeInferenceBudgetAudit

    def to_summary_mapping(self) -> dict[str, Any]:
        return canonicalize_json_value(
            {
                "checkpoint_id": self.checkpoint_id,
                "step_index": self.step_index,
                "time": self.time,
                "graph_kind": self.graph_kind,
                "node_count": len(self.nodes),
                "edge_count": len(self.edges),
                "port_matrix_available": self.port_matrix_available,
                "provenance_available": self.provenance_available,
                "bridge_edge_ids": list(self.bridge_edge_ids),
                "bridge_detection_modes": list(self.bridge_detection_modes),
                "budget_audit": self.budget_audit.to_mapping(),
            }
        )


@dataclass(frozen=True)
class LandscapeInferenceEvidenceSubstrate:
    """Checkpoint series normalized for later landscape classifiers."""

    runtime_family: str
    inference_window: LandscapeInferenceWindow
    checkpoint_graphs: tuple[LandscapeInferenceCheckpointGraph, ...]
    diagnostic_only: bool

    def to_summary_mapping(self) -> dict[str, Any]:
        return canonicalize_json_value(
            {
                "runtime_family": self.runtime_family,
                "inference_window": self.inference_window.to_mapping(),
                "checkpoint_count": len(self.checkpoint_graphs),
                "diagnostic_only": self.diagnostic_only,
                "port_matrix_available": any(
                    graph.port_matrix_available for graph in self.checkpoint_graphs
                ),
                "provenance_available": any(
                    graph.provenance_available for graph in self.checkpoint_graphs
                ),
                "bridge_edge_count": sum(
                    len(graph.bridge_edge_ids) for graph in self.checkpoint_graphs
                ),
                "budget_available": any(
                    graph.budget_audit.budget_available for graph in self.checkpoint_graphs
                ),
            }
        )


def build_landscape_inference_evidence_substrate(
    load_result: Any,
    *,
    allow_short_persistence_window: bool = False,
) -> LandscapeInferenceEvidenceSubstrate:
    """Build a checkpoint evidence substrate from an Iteration 2 load result."""

    pack = load_result.telemetry_pack
    inference_window = load_result.inference_window
    graphs = tuple(
        build_landscape_inference_checkpoint_graph(checkpoint)
        for checkpoint in pack.graph_checkpoints
        if inference_window.start_step <= int(checkpoint.step_index) <= inference_window.end_step
    )
    diagnostic_only = len(graphs) < 3 and not allow_short_persistence_window
    return LandscapeInferenceEvidenceSubstrate(
        runtime_family=str(load_result.source_runtime_family),
        inference_window=inference_window,
        checkpoint_graphs=graphs,
        diagnostic_only=diagnostic_only,
    )


def build_landscape_inference_checkpoint_graph(
    checkpoint: Any,
) -> LandscapeInferenceCheckpointGraph:
    """Normalize one graph checkpoint into node/edge/adjacency evidence."""

    family_extensions = _mapping(checkpoint.family_extensions)
    bridge_edge_ids, bridge_modes = _bridge_edge_ids_from_family_extensions(family_extensions)
    port_matrices = _port_matrices_from_family_extensions(family_extensions)
    node_overlays = _node_overlays_from_family_extensions(family_extensions)
    edge_overlays = _edge_overlays_from_family_extensions(family_extensions)

    nodes: dict[int, LandscapeInferenceNodeEvidence] = {}
    for record in checkpoint.node_records:
        node_id = _int(record.get("node_id"))
        payload = _mapping(record.get("payload", {}))
        matrix = port_matrices.get(node_id) or _port_matrix_from_node_record(record)
        node_overlay = node_overlays.get(node_id, {})
        nodes[node_id] = LandscapeInferenceNodeEvidence(
            node_id=node_id,
            coherence=_optional_float(record.get("coherence")),
            quadrature_weight=_node_quadrature_weight(record),
            sink_flag=_node_sink_flag(record, payload, node_overlay),
            basin_id=_node_basin_id(record, payload, node_overlay),
            basin_mass=_node_basin_mass(record, payload, node_overlay),
            parent_id=_node_parent_id(record, payload, node_overlay),
            depth=_node_depth(record, payload, node_overlay),
            gradient_norm=_node_gradient_norm(record, payload, node_overlay),
            min_signed_hessian=_node_min_signed_hessian(record, payload, node_overlay),
            tensor_trace=_node_tensor_trace(record, payload, node_overlay),
            tensor_anisotropy=_node_tensor_anisotropy(record, payload, node_overlay),
            payload=payload,
            port_matrix=matrix,
            provenance=_provenance_from_payload(payload),
        )

    edges: dict[int, LandscapeInferenceEdgeEvidence] = {}
    adjacency_sets: dict[int, set[int]] = {node_id: set() for node_id in nodes}
    edge_id_by_pair: dict[tuple[int, int], int] = {}
    detected_bridge_modes: set[str] = set(bridge_modes)
    for record in checkpoint.edge_records:
        edge_id = _int(record.get("edge_id"))
        source_node_id = _int(record.get("source_node_id"))
        target_node_id = _int(record.get("target_node_id"))
        payload = _mapping(record.get("payload", {}))
        edge_overlay = edge_overlays.get(edge_id, {})
        is_bridge, bridge_mode = _detect_bridge_edge(record, payload, bridge_edge_ids)
        if bridge_mode != "unavailable":
            detected_bridge_modes.add(bridge_mode)
        evidence = LandscapeInferenceEdgeEvidence(
            edge_id=edge_id,
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            source_port_id=_optional_int(record.get("source_port_id")),
            target_port_id=_optional_int(record.get("target_port_id")),
            conductance=_edge_conductance(record),
            signed_flux=_edge_signed_flux(record),
            geometric_length=_edge_label(record, payload, edge_overlay, "geometric_length"),
            temporal_delay=_edge_label(record, payload, edge_overlay, "temporal_delay"),
            flux_coupling=_edge_label(record, payload, edge_overlay, "flux_coupling"),
            payload=payload,
            bridge_detection_mode=bridge_mode,
            is_bridge=is_bridge,
            provenance=_provenance_from_payload(payload),
        )
        edges[edge_id] = evidence
        adjacency_sets.setdefault(source_node_id, set()).add(target_node_id)
        adjacency_sets.setdefault(target_node_id, set()).add(source_node_id)
        edge_id_by_pair[_pair_key(source_node_id, target_node_id)] = edge_id

    adjacency = {
        node_id: tuple(sorted(neighbors))
        for node_id, neighbors in sorted(adjacency_sets.items())
    }
    bridge_ids = tuple(sorted(edge_id for edge_id, edge in edges.items() if edge.is_bridge))
    port_matrix_available = any(node.port_matrix is not None for node in nodes.values())
    provenance_available = any(node.provenance for node in nodes.values()) or any(
        edge.provenance for edge in edges.values()
    )
    return LandscapeInferenceCheckpointGraph(
        checkpoint_id=str(checkpoint.checkpoint_id),
        step_index=int(checkpoint.step_index),
        time=None if checkpoint.time is None else float(checkpoint.time),
        graph_kind=str(checkpoint.graph_kind),
        nodes=dict(sorted(nodes.items())),
        edges=dict(sorted(edges.items())),
        adjacency=adjacency,
        edge_id_by_pair=dict(sorted(edge_id_by_pair.items())),
        port_matrix_available=port_matrix_available,
        provenance_available=provenance_available,
        bridge_edge_ids=bridge_ids,
        bridge_detection_modes=tuple(sorted(detected_bridge_modes or {"unavailable"})),
        budget_audit=audit_checkpoint_budget(checkpoint, nodes),
    )


def extract_landscape_inference_candidate_paths(
    graph: LandscapeInferenceCheckpointGraph,
    source_node_ids: Sequence[int],
    target_node_ids: Sequence[int],
    *,
    max_paths: int = 20,
    max_depth: int | None = None,
    include_bridge_paths: bool = True,
) -> tuple[LandscapeInferencePathEvidence, ...]:
    """Enumerate deterministic simple path candidates between endpoint sets."""

    if max_paths <= 0:
        return ()
    sources = tuple(sorted(set(int(item) for item in source_node_ids)))
    targets = set(int(item) for item in target_node_ids)
    results: list[LandscapeInferencePathEvidence] = []
    for source in sources:
        if source not in graph.nodes:
            continue
        queue: deque[tuple[int, tuple[int, ...]]] = deque([(source, (source,))])
        while queue and len(results) < max_paths:
            current, path = queue.popleft()
            if current in targets and current != source:
                evidence = _path_evidence(graph, path)
                if include_bridge_paths or not evidence.bridge_edge_ids:
                    results.append(evidence)
                continue
            if max_depth is not None and len(path) - 1 >= max_depth:
                continue
            for neighbor in graph.adjacency.get(current, ()):
                if neighbor in path:
                    continue
                queue.append((neighbor, (*path, neighbor)))
    return tuple(results)


def summarize_landscape_inference_path_persistence(
    substrate: LandscapeInferenceEvidenceSubstrate,
    path_node_ids: Sequence[int],
) -> LandscapeInferencePathPersistence:
    """Summarize whether one path survives across a checkpoint window."""

    nodes = tuple(int(item) for item in path_node_ids)
    pairs = tuple(_pair_key(a, b) for a, b in zip(nodes, nodes[1:]))
    missing_nodes: set[int] = set()
    missing_pairs: set[tuple[int, int]] = set()
    present_count = 0
    for graph in substrate.checkpoint_graphs:
        graph_nodes = set(graph.nodes)
        absent_nodes = set(nodes) - graph_nodes
        if absent_nodes:
            missing_nodes.update(absent_nodes)
            missing_pairs.update(pairs)
            continue
        absent_pairs = tuple(pair for pair in pairs if pair not in graph.edge_id_by_pair)
        if absent_pairs:
            missing_pairs.update(absent_pairs)
            continue
        present_count += 1
    checkpoint_count = len(substrate.checkpoint_graphs)
    return LandscapeInferencePathPersistence(
        checkpoint_count=checkpoint_count,
        present_count=present_count,
        ruptured_count=checkpoint_count - present_count,
        missing_node_ids=tuple(sorted(missing_nodes)),
        missing_edge_pairs=tuple(sorted(missing_pairs)),
        diagnostic_only=substrate.diagnostic_only,
    )


def summarize_landscape_inference_path_flux_stability(
    substrate: LandscapeInferenceEvidenceSubstrate,
    path_node_ids: Sequence[int],
) -> LandscapeInferencePathFluxStability:
    """Summarize repeated path flux across a checkpoint window."""

    series = tuple(
        _path_total_abs_flux(graph, path_node_ids) for graph in substrate.checkpoint_graphs
    )
    finite = tuple(value for value in series if value is not None and value > 0.0)
    checkpoint_count = len(series)
    observed_count = len(finite)
    observed_fraction = 0.0 if checkpoint_count == 0 else float(observed_count / checkpoint_count)
    if not finite:
        return LandscapeInferencePathFluxStability(
            checkpoint_count=checkpoint_count,
            observed_count=0,
            observed_fraction=observed_fraction,
            flux_series=series,
            mean_abs_flux=None,
            min_abs_flux=None,
            max_abs_flux=None,
            coefficient_of_variation=None,
            stability_score=0.0,
            stability_mode="unobserved",
        )
    mean_abs_flux = float(sum(finite) / len(finite))
    min_abs_flux = float(min(finite))
    max_abs_flux = float(max(finite))
    variance = float(sum((value - mean_abs_flux) ** 2 for value in finite) / len(finite))
    coefficient = None if mean_abs_flux <= 0.0 else float(math.sqrt(variance) / mean_abs_flux)
    coefficient_factor = 1.0 if coefficient is None else 1.0 / (1.0 + coefficient)
    stability_score = float(max(0.0, min(1.0, observed_fraction * coefficient_factor)))
    if observed_fraction >= 0.95 and stability_score >= 0.75:
        mode = "stable_repeated_flux"
    elif observed_fraction >= 0.6:
        mode = "repeated_flux"
    else:
        mode = "sparse_flux"
    return LandscapeInferencePathFluxStability(
        checkpoint_count=checkpoint_count,
        observed_count=observed_count,
        observed_fraction=observed_fraction,
        flux_series=series,
        mean_abs_flux=mean_abs_flux,
        min_abs_flux=min_abs_flux,
        max_abs_flux=max_abs_flux,
        coefficient_of_variation=coefficient,
        stability_score=stability_score,
        stability_mode=mode,
    )


def _path_total_abs_flux(
    graph: LandscapeInferenceCheckpointGraph,
    node_ids: Sequence[int],
) -> float | None:
    values: list[float] = []
    nodes = tuple(int(item) for item in node_ids)
    for source, target in zip(nodes, nodes[1:]):
        edge_id = graph.edge_id_by_pair.get(_pair_key(source, target))
        if edge_id is None:
            return None
        signed_flux = graph.edges[edge_id].signed_flux
        if signed_flux is None:
            return None
        values.append(abs(float(signed_flux)))
    return float(sum(values))


def audit_checkpoint_budget(
    checkpoint: Any,
    nodes: Mapping[int, LandscapeInferenceNodeEvidence] | None = None,
) -> LandscapeInferenceBudgetAudit:
    """Compute a read-only checkpoint budget audit."""

    resolved_nodes = nodes
    if resolved_nodes is None:
        resolved_nodes = {
            _int(record.get("node_id")): LandscapeInferenceNodeEvidence(
                node_id=_int(record.get("node_id")),
                coherence=_optional_float(record.get("coherence")),
                quadrature_weight=_node_quadrature_weight(record),
                sink_flag=_node_sink_flag(record, _mapping(record.get("payload", {})), {}),
                basin_id=_node_basin_id(record, _mapping(record.get("payload", {})), {}),
                basin_mass=_node_basin_mass(record, _mapping(record.get("payload", {})), {}),
                parent_id=_node_parent_id(record, _mapping(record.get("payload", {})), {}),
                depth=_node_depth(record, _mapping(record.get("payload", {})), {}),
                gradient_norm=_node_gradient_norm(record, _mapping(record.get("payload", {})), {}),
                min_signed_hessian=_node_min_signed_hessian(record, _mapping(record.get("payload", {})), {}),
                tensor_trace=_node_tensor_trace(record, _mapping(record.get("payload", {})), {}),
                tensor_anisotropy=_node_tensor_anisotropy(record, _mapping(record.get("payload", {})), {}),
                payload=_mapping(record.get("payload", {})),
                port_matrix=None,
                provenance={},
            )
            for record in checkpoint.node_records
        }
    weighted_values: list[float] = []
    any_weight = False
    any_coherence = False
    for node in resolved_nodes.values():
        if node.coherence is None:
            continue
        any_coherence = True
        if node.quadrature_weight is not None:
            any_weight = True
            weighted_values.append(float(node.coherence) * float(node.quadrature_weight))
        else:
            weighted_values.append(float(node.coherence))
    if not any_coherence:
        return LandscapeInferenceBudgetAudit(
            budget_sum=None,
            budget_target=None,
            budget_error=None,
            quadrature_weight_mode="unavailable",
            budget_available=False,
            budget_accountability="unavailable",
        )
    family_extensions = _mapping(checkpoint.family_extensions)
    target = _budget_target_from_family_extensions(family_extensions)
    budget_sum = float(sum(weighted_values))
    budget_error = None if target is None else float(budget_sum - target)
    return LandscapeInferenceBudgetAudit(
        budget_sum=budget_sum,
        budget_target=target,
        budget_error=budget_error,
        quadrature_weight_mode=_quadrature_weight_mode(family_extensions, any_weight),
        budget_available=True,
        budget_accountability="conserved_zero"
        if budget_error is not None and abs(budget_error) <= 1e-9
        else ("leak_error" if budget_error is not None else "unavailable"),
    )


def _path_evidence(
    graph: LandscapeInferenceCheckpointGraph,
    node_ids: tuple[int, ...],
) -> LandscapeInferencePathEvidence:
    edge_ids = tuple(
        graph.edge_id_by_pair[_pair_key(source, target)]
        for source, target in zip(node_ids, node_ids[1:])
    )
    edges = tuple(graph.edges[edge_id] for edge_id in edge_ids)
    conductances = tuple(edge.conductance for edge in edges if edge.conductance is not None)
    fluxes = tuple(edge.signed_flux for edge in edges if edge.signed_flux is not None)
    bridge_edge_ids = tuple(edge.edge_id for edge in edges if edge.is_bridge)
    total_abs_flux = None if not fluxes else float(sum(abs(value) for value in fluxes))
    return LandscapeInferencePathEvidence(
        node_ids=node_ids,
        edge_ids=edge_ids,
        bottleneck_conductance=None if not conductances else float(min(conductances)),
        total_abs_flux=total_abs_flux,
        mean_abs_flux=None if total_abs_flux is None else total_abs_flux / len(fluxes),
        bridge_edge_ids=bridge_edge_ids,
        directionality=_path_directionality(edges),
    )


def _path_directionality(edges: Sequence[LandscapeInferenceEdgeEvidence]) -> str:
    fluxes = tuple(edge.signed_flux for edge in edges if edge.signed_flux is not None)
    if not fluxes:
        return "unavailable"
    positives = sum(1 for value in fluxes if value > 0.0)
    negatives = sum(1 for value in fluxes if value < 0.0)
    if positives and negatives:
        return "mixed"
    if positives:
        return "source_to_target"
    if negatives:
        return "target_to_source"
    return "zero_flux"


def _bridge_edge_ids_from_family_extensions(
    family_extensions: Mapping[str, Any],
) -> tuple[set[int], set[str]]:
    edge_ids: set[int] = set()
    modes: set[str] = set()
    for family_name in ("grcl9", "grcl9v3"):
        family = _mapping(family_extensions.get(family_name, {}))
        for key in ("bridge_edge_ids", "grcl9_bridge_edge_ids", "grcl9v3_bridge_edge_ids"):
            for edge_id in _int_sequence(family.get(key, ())):
                edge_ids.add(edge_id)
                modes.add("family_extension")
    return edge_ids, modes


def _detect_bridge_edge(
    record: Mapping[str, Any],
    payload: Mapping[str, Any],
    bridge_edge_ids: set[int],
) -> tuple[bool, str]:
    edge_id = _int(record.get("edge_id"))
    if edge_id in bridge_edge_ids:
        return True, "family_extension"
    for key in ("grcl9_edge_kind", "grcl9v3_edge_kind"):
        if record.get(key) == "bridge":
            return True, "source_tag"
        if payload.get(key) == "bridge":
            return True, "source_tag"
    return False, "unavailable"


def _port_matrices_from_family_extensions(
    family_extensions: Mapping[str, Any],
) -> dict[int, PortMatrix]:
    matrices: dict[int, PortMatrix] = {}
    grc9 = _mapping(family_extensions.get("grc9", {}))
    for node_id_text, ports in _mapping(grc9.get("port_overlays", {})).items():
        node_id = _int(node_id_text)
        matrices[node_id] = _matrix_from_grc9_port_overlay(ports)
    grc9v3 = _mapping(family_extensions.get("grc9v3", {}))
    port_overlay = _mapping(grc9v3.get("port_overlay", {}))
    by_node = _mapping(port_overlay.get("by_node", {}))
    for node_id_text, record in by_node.items():
        node_id = _int(node_id_text)
        occupied_ports = _int_sequence(_mapping(record).get("occupied_ports", ()))
        matrices[node_id] = _matrix_from_occupied_port_ids(occupied_ports)
    return matrices


def _node_overlays_from_family_extensions(
    family_extensions: Mapping[str, Any],
) -> dict[int, Mapping[str, Any]]:
    overlays: dict[int, Mapping[str, Any]] = {}
    for family_name in ("grc9v3", "grcv3", "grc9"):
        family = _mapping(family_extensions.get(family_name, {}))
        for key in ("node_overlay", "node_overlays"):
            overlay = _mapping(family.get(key, {}))
            for node_id_text, record in overlay.items():
                overlays[_int(node_id_text)] = _mapping(record)
    return overlays


def _edge_overlays_from_family_extensions(
    family_extensions: Mapping[str, Any],
) -> dict[int, Mapping[str, Any]]:
    overlays: dict[int, Mapping[str, Any]] = {}
    for family_name in ("grc9v3", "grcv3", "grc9"):
        family = _mapping(family_extensions.get(family_name, {}))
        for key in ("edge_overlay", "edge_overlays"):
            overlay = _mapping(family.get(key, {}))
            for edge_id_text, record in overlay.items():
                overlays[_int(edge_id_text)] = _mapping(record)
    return overlays


def _node_gradient_norm(
    record: Mapping[str, Any],
    payload: Mapping[str, Any],
    overlay: Mapping[str, Any],
) -> float | None:
    direct = _first_float(
        record,
        payload,
        overlay,
        keys=("gradient_norm", "row_basis_gradient_norm"),
    )
    if direct is not None:
        return direct
    gradient = record.get("gradient", payload.get("gradient"))
    if gradient is None:
        gradient = record.get("gradient_row_basis", payload.get("gradient_row_basis"))
    if not isinstance(gradient, Sequence) or isinstance(gradient, str | bytes):
        return None
    values = tuple(_optional_float(item) for item in gradient)
    finite = tuple(value for value in values if value is not None)
    if not finite:
        return None
    return float(sum(value * value for value in finite) ** 0.5)


def _node_sink_flag(
    record: Mapping[str, Any],
    payload: Mapping[str, Any],
    overlay: Mapping[str, Any],
) -> bool:
    for key in ("sink_flag", "is_sink"):
        for mapping in (record, payload, overlay):
            if key in mapping:
                return bool(mapping.get(key))
    return False


def _node_basin_id(
    record: Mapping[str, Any],
    payload: Mapping[str, Any],
    overlay: Mapping[str, Any],
) -> str | None:
    for key in ("basin_id", "basin_sink_id", "sink_id"):
        for mapping in (record, payload, overlay):
            if mapping.get(key) is not None:
                return str(mapping.get(key))
    return None


def _node_basin_mass(
    record: Mapping[str, Any],
    payload: Mapping[str, Any],
    overlay: Mapping[str, Any],
) -> float | None:
    return _first_float(record, payload, overlay, keys=("basin_mass", "module_basin_mass"))


def _node_parent_id(
    record: Mapping[str, Any],
    payload: Mapping[str, Any],
    overlay: Mapping[str, Any],
) -> str | None:
    for key in ("parent_id", "hierarchy_parent"):
        for mapping in (record, payload, overlay):
            if mapping.get(key) is not None:
                return str(mapping.get(key))
    return None


def _node_depth(
    record: Mapping[str, Any],
    payload: Mapping[str, Any],
    overlay: Mapping[str, Any],
) -> int | None:
    for key in ("depth", "hierarchy_depth"):
        for mapping in (record, payload, overlay):
            value = _optional_int(mapping.get(key))
            if value is not None:
                return value
    return None


def _node_min_signed_hessian(
    record: Mapping[str, Any],
    payload: Mapping[str, Any],
    overlay: Mapping[str, Any],
) -> float | None:
    direct = _first_float(
        record,
        payload,
        overlay,
        keys=(
            "min_signed_hessian",
            "signed_hessian_min",
            "hessian_min",
            "lambda_min_signed_hessian",
        ),
    )
    if direct is not None:
        return direct
    values = record.get("signed_hessian_row_basis", payload.get("signed_hessian_row_basis"))
    if values is None:
        values = record.get("signed_hessian", payload.get("signed_hessian"))
    if values is None:
        values = record.get("hessian", payload.get("hessian"))
        diagonal = _matrix_diagonal(values)
        return None if not diagonal else float(min(diagonal))
    if not isinstance(values, Sequence) or isinstance(values, str | bytes):
        return None
    finite = tuple(value for value in (_optional_float(item) for item in values) if value is not None)
    return None if not finite else float(min(finite))


def _node_tensor_trace(
    record: Mapping[str, Any],
    payload: Mapping[str, Any],
    overlay: Mapping[str, Any],
) -> float | None:
    direct = _first_float(record, payload, overlay, keys=("tensor_trace", "coherence_tensor_trace"))
    if direct is not None:
        return direct
    tensor = record.get("tensor", payload.get("tensor"))
    if tensor is None:
        tensor = record.get("coherence_tensor", payload.get("coherence_tensor"))
    return _matrix_trace(tensor)


def _node_tensor_anisotropy(
    record: Mapping[str, Any],
    payload: Mapping[str, Any],
    overlay: Mapping[str, Any],
) -> float | None:
    direct = _first_float(
        record,
        payload,
        overlay,
        keys=("tensor_anisotropy", "coherence_tensor_anisotropy"),
    )
    if direct is not None:
        return direct
    diagonal = _matrix_diagonal(record.get("tensor", payload.get("tensor")))
    if not diagonal:
        diagonal = _matrix_diagonal(record.get("coherence_tensor", payload.get("coherence_tensor")))
    if not diagonal:
        return None
    return float(max(diagonal) - min(diagonal))


def _edge_label(
    record: Mapping[str, Any],
    payload: Mapping[str, Any],
    overlay: Mapping[str, Any],
    key: str,
) -> float | None:
    return _first_float(record, payload, overlay, keys=(key,))


def _first_float(
    *mappings: Mapping[str, Any],
    keys: Sequence[str],
) -> float | None:
    for mapping in mappings:
        for key in keys:
            if key in mapping:
                value = _optional_float(mapping.get(key))
                if value is not None:
                    return value
    return None


def _matrix_trace(value: Any) -> float | None:
    diagonal = _matrix_diagonal(value)
    return None if not diagonal else float(sum(diagonal))


def _matrix_diagonal(value: Any) -> tuple[float, ...]:
    if not isinstance(value, Sequence) or isinstance(value, str | bytes):
        return ()
    diagonal: list[float] = []
    for index, row in enumerate(value):
        if not isinstance(row, Sequence) or isinstance(row, str | bytes):
            return ()
        if index >= len(row):
            return ()
        item = _optional_float(row[index])
        if item is None:
            return ()
        diagonal.append(item)
    return tuple(diagonal)


def _matrix_from_grc9_port_overlay(value: Any) -> PortMatrix:
    grid = [[False, False, False], [False, False, False], [False, False, False]]
    if not isinstance(value, Sequence) or isinstance(value, str | bytes):
        return _freeze_matrix(grid)
    for item in value:
        record = _mapping(item)
        if not bool(record.get("occupied")):
            continue
        row = _optional_int(record.get("row"))
        column = _optional_int(record.get("column"))
        port_id = _optional_int(record.get("port_id"))
        if row is None or column is None:
            if port_id is None:
                continue
            row, column = _port_id_to_row_column(port_id)
        if 1 <= row <= 3 and 1 <= column <= 3:
            grid[row - 1][column - 1] = True
    return _freeze_matrix(grid)


def _port_matrix_from_node_record(record: Mapping[str, Any]) -> PortMatrix | None:
    occupied_ports = record.get("occupied_ports")
    if occupied_ports is not None:
        return _matrix_from_occupied_port_ids(_int_sequence(occupied_ports))
    if "row_occupancy" in record or "column_occupancy" in record:
        # Aggregates indicate port evidence exists, but not the exact matrix.
        return None
    return None


def _matrix_from_occupied_port_ids(port_ids: Sequence[int]) -> PortMatrix:
    grid = [[False, False, False], [False, False, False], [False, False, False]]
    for port_id in port_ids:
        row, column = _port_id_to_row_column(port_id)
        if 1 <= row <= 3 and 1 <= column <= 3:
            grid[row - 1][column - 1] = True
    return _freeze_matrix(grid)


def _freeze_matrix(grid: Sequence[Sequence[bool]]) -> PortMatrix:
    return (
        (bool(grid[0][0]), bool(grid[0][1]), bool(grid[0][2])),
        (bool(grid[1][0]), bool(grid[1][1]), bool(grid[1][2])),
        (bool(grid[2][0]), bool(grid[2][1]), bool(grid[2][2])),
    )


def _port_id_to_row_column(port_id: int) -> tuple[int, int]:
    return ((int(port_id) - 1) // 3 + 1, (int(port_id) - 1) % 3 + 1)


def _provenance_from_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    provenance: dict[str, Any] = {}
    for key, value in payload.items():
        if (
            "source_construct" in key
            or "motif_id" in key
            or "motif_role" in key
            or key.endswith("_provenance")
        ):
            provenance[key] = value
    return provenance


def _node_quadrature_weight(record: Mapping[str, Any]) -> float | None:
    for key in ("quadrature_weight", "mu_i", "measure_weight"):
        if key in record:
            return _optional_float(record.get(key))
    payload = _mapping(record.get("payload", {}))
    for key in ("quadrature_weight", "mu_i", "measure_weight"):
        if key in payload:
            return _optional_float(payload.get(key))
    return None


def _quadrature_weight_mode(family_extensions: Mapping[str, Any], any_weight: bool) -> str:
    if any_weight:
        return "checkpoint_weight"
    for family in family_extensions.values():
        if _mapping(family).get("quadrature_mode") == "unit_measure":
            return "unit_measure"
    if family_extensions:
        return "unit_measure_assumed"
    return "unavailable"


def _budget_target_from_family_extensions(family_extensions: Mapping[str, Any]) -> float | None:
    for family in family_extensions.values():
        mapping = _mapping(family)
        if "budget_target" in mapping:
            return _optional_float(mapping.get("budget_target"))
    return None


def _edge_conductance(record: Mapping[str, Any]) -> float | None:
    for key in ("conductance", "base_conductance"):
        if key in record:
            return _optional_float(record.get(key))
    return None


def _edge_signed_flux(record: Mapping[str, Any]) -> float | None:
    for key in ("signed_flux", "signed_flux_source_to_target", "signed_flux_source", "flux_uv"):
        if key in record:
            return _optional_float(record.get(key))
    return None


def _pair_key(source: int, target: int) -> tuple[int, int]:
    a, b = int(source), int(target)
    return (a, b) if a <= b else (b, a)


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _int(value: Any) -> int:
    if isinstance(value, bool):
        raise ValueError("expected int, got bool")
    return int(value)


def _optional_int(value: Any) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _optional_float(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def _int_sequence(value: Any) -> tuple[int, ...]:
    if not isinstance(value, Sequence) or isinstance(value, str | bytes):
        return ()
    result: list[int] = []
    for item in value:
        parsed = _optional_int(item)
        if parsed is not None:
            result.append(parsed)
    return tuple(result)


__all__ = [
    "LandscapeInferenceBudgetAudit",
    "LandscapeInferenceCheckpointGraph",
    "LandscapeInferenceEdgeEvidence",
    "LandscapeInferenceEvidenceSubstrate",
    "LandscapeInferenceNodeEvidence",
    "LandscapeInferencePathEvidence",
    "LandscapeInferencePathFluxStability",
    "LandscapeInferencePathPersistence",
    "PortMatrix",
    "audit_checkpoint_budget",
    "build_landscape_inference_checkpoint_graph",
    "build_landscape_inference_evidence_substrate",
    "extract_landscape_inference_candidate_paths",
    "summarize_landscape_inference_path_persistence",
    "summarize_landscape_inference_path_flux_stability",
]
