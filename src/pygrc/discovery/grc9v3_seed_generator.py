"""Deterministic GRC9V3 runtime seed generators for discovery."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import math
from typing import Any

from pygrc.models import GRC9V3

from .grc9_manifest import generated_lane_name, perturbation_lane_name
from .grc9v3_hypothesis_catalog import (
    GRC9V3HypothesisCatalog,
    GRC9V3SeedControlSpec,
    GRC9V3SeedFamilySpec,
    default_grc9v3_hypothesis_catalog,
)
from .grc9v3_mechanism_ledger import GRC9V3_RUNTIME_TESTABLE


GRC9V3_SEED_GENERATOR_VERSION = "grc9v3_seed_generator_v1"
GRC9V3_COMPLEX_HYBRID_PROFILE = "grc9v3_discovery_complex_hybrid_examples_v1"
GRC9V3_COMPLEX_HYBRID_NAMES: tuple[str, ...] = (
    "complex_spark_expansion_hierarchy",
    "complex_spark_expansion_choice_collapse",
    "complex_expansion_growth_budget_coarse",
    "complex_hessian_row_basis",
    "complex_hessian_weighted_least_squares",
    "complex_spark_choice_no_saturation_perturbation",
    "complex_growth_low_birth_perturbation",
)
GRC9V3_PRESSURE_BOUNDARY_PROFILE = "grc9v3_pressure_boundary_examples_v1"
GRC9V3_PRESSURE_BOUNDARY_NAMES: tuple[str, ...] = (
    "pressure_boundary_growth_positive_control",
    "pressure_boundary_growth_no_growth_control",
    "generic_front_capacity_growth_comparison",
    "complex_spark_expansion_pressure_boundary_growth",
)


def _json_safe(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            str(key): _json_safe(item)
            for key, item in sorted(value.items(), key=lambda item: str(item[0]))
        }
    if isinstance(value, tuple | list):
        return [_json_safe(item) for item in value]
    return value


def _finite_float(value: Any, *, field_name: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{field_name} must be a finite float")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{field_name} must be finite")
    return result


def _positive_int(value: Any, *, field_name: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{field_name} must be a positive integer")
    result = int(value)
    if result <= 0:
        raise ValueError(f"{field_name} must be positive")
    return result


def _config_float(value: Any, default: float, *, field_name: str) -> float:
    if value in (None, "nominal"):
        return float(default)
    if value == "low":
        return float(default) * 0.1
    if value == "high":
        return float(default) * 10.0
    if value == "below_epsilon":
        return 1e-7
    if value == "far_from_epsilon":
        return 1.0
    return _finite_float(value, field_name=field_name)


def _canonical_port_edge(
    *,
    node_a: int,
    port_a: int,
    node_b: int,
    port_b: int,
    conductance: float,
    flux_uv: float,
) -> dict[str, float | int]:
    if (node_a, port_a) <= (node_b, port_b):
        return {
            "node_u": node_a,
            "port_u": port_a,
            "node_v": node_b,
            "port_v": port_b,
            "conductance": float(conductance),
            "flux_uv": float(flux_uv),
        }
    return {
        "node_u": node_b,
        "port_u": port_b,
        "node_v": node_a,
        "port_v": port_a,
        "conductance": float(conductance),
        "flux_uv": float(-flux_uv),
    }


class _GraphBuilder:
    def __init__(self, node_count: int) -> None:
        self.node_count = _positive_int(node_count, field_name="node_count")
        self.edges: list[dict[str, Any]] = []
        self.port_edges: dict[str, dict[str, float | int]] = {}
        self._occupied_ports: set[tuple[int, int]] = set()

    def connect(
        self,
        node_a: int,
        port_a: int,
        node_b: int,
        port_b: int,
        *,
        conductance: float = 1.0,
        flux_uv: float = 0.0,
        role: str = "discovery_edge",
    ) -> int:
        if node_a not in range(self.node_count) or node_b not in range(self.node_count):
            raise ValueError("edge endpoints must reference generated nodes")
        for node_id, port_id in ((node_a, port_a), (node_b, port_b)):
            if port_id not in range(1, 10):
                raise ValueError("GRC9V3 seed ports must be in the canonical 1..9 range")
            endpoint = (node_id, port_id)
            if endpoint in self._occupied_ports:
                raise ValueError(f"duplicate port endpoint in generated seed: {endpoint}")
            self._occupied_ports.add(endpoint)
        edge_id = len(self.edges)
        conductance_value = _finite_float(conductance, field_name="conductance")
        flux_value = _finite_float(flux_uv, field_name="flux_uv")
        self.edges.append(
            {
                "edge_id": edge_id,
                "endpoint_a": {"node_id": node_a, "slot": port_a - 1},
                "endpoint_b": {"node_id": node_b, "slot": port_b - 1},
                "payload": {
                    "role": role,
                    "conductance": conductance_value,
                    "discovery_generator": GRC9V3_SEED_GENERATOR_VERSION,
                },
            }
        )
        self.port_edges[str(edge_id)] = _canonical_port_edge(
            node_a=node_a,
            port_a=port_a,
            node_b=node_b,
            port_b=port_b,
            conductance=conductance_value,
            flux_uv=flux_value,
        )
        return edge_id

    def topology(self) -> dict[str, Any]:
        incidence: dict[str, list[int]] = {
            str(node_id): [] for node_id in range(self.node_count)
        }
        port_to_edge: dict[str, int] = {}
        node_port_occupancy: dict[str, list[int]] = {
            str(node_id): [] for node_id in range(self.node_count)
        }
        for edge in self.edges:
            edge_id = int(edge["edge_id"])
            node_a = int(edge["endpoint_a"]["node_id"])
            port_a = int(edge["endpoint_a"]["slot"]) + 1
            node_b = int(edge["endpoint_b"]["node_id"])
            port_b = int(edge["endpoint_b"]["slot"]) + 1
            incidence[str(node_a)].append(edge_id)
            incidence[str(node_b)].append(edge_id)
            port_to_edge[f"{node_a}:{port_a}"] = edge_id
            port_to_edge[f"{node_b}:{port_b}"] = edge_id
            node_port_occupancy[str(node_a)].append(port_a)
            node_port_occupancy[str(node_b)].append(port_b)
        return {
            "nodes": [
                {"node_id": node_id, "payload": {"discovery_node_index": node_id}}
                for node_id in range(self.node_count)
            ],
            "edges": list(self.edges),
            "incidence": {
                node_id: sorted(edge_ids) for node_id, edge_ids in sorted(incidence.items())
            },
            "port_structure": {
                "port_count": 9,
                "port_to_edge": dict(sorted(port_to_edge.items())),
                "node_port_occupancy": {
                    node_id: sorted(ports)
                    for node_id, ports in sorted(node_port_occupancy.items())
                },
            },
            "edge_roles": {
                str(edge["edge_id"]): str(edge["payload"]["role"])
                for edge in self.edges
            },
        }


@dataclass(frozen=True)
class GRC9V3GeneratedSeed:
    seed_family: str
    seed_name: str
    control_role: str
    lane_name: str
    profile: str
    generator_version: str
    seed_parameters: Mapping[str, Any]
    expected_runtime_config: Mapping[str, Any]
    ownership_tags: tuple[str, ...]
    graph_preconditions: Mapping[str, Any]
    state_preconditions: Mapping[str, Any]
    predicted_signatures: tuple[Mapping[str, Any], ...]
    predicted_event_sequence: tuple[str, ...]
    required_checkpoint_overlays: tuple[str, ...]
    state_payload: Mapping[str, Any]
    negative_control_of: str | None = None
    perturbation_of: str | None = None

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "seed_family": self.seed_family,
            "seed_name": self.seed_name,
            "control_role": self.control_role,
            "lane_name": self.lane_name,
            "profile": self.profile,
            "generator_version": self.generator_version,
            "seed_parameters": _json_safe(self.seed_parameters),
            "expected_runtime_config": _json_safe(self.expected_runtime_config),
            "ownership_tags": list(self.ownership_tags),
            "graph_preconditions": _json_safe(self.graph_preconditions),
            "state_preconditions": _json_safe(self.state_preconditions),
            "predicted_signatures": [_json_safe(item) for item in self.predicted_signatures],
            "predicted_event_sequence": list(self.predicted_event_sequence),
            "required_checkpoint_overlays": list(self.required_checkpoint_overlays),
            "state_payload": _json_safe(self.state_payload),
            "negative_control_of": self.negative_control_of,
            "perturbation_of": self.perturbation_of,
        }


def _control_by_role(
    family: GRC9V3SeedFamilySpec,
    control_role: str,
) -> GRC9V3SeedControlSpec:
    for control in (*family.positive_controls, *family.negative_controls):
        if control.control_role == control_role:
            return control
    raise ValueError(
        f"seed family {family.seed_family!r} has no control role {control_role!r}"
    )


def _seed_parameters(
    family: GRC9V3SeedFamilySpec,
    control: GRC9V3SeedControlSpec,
    parameter_overrides: Mapping[str, Any] | None,
) -> dict[str, Any]:
    parameters: dict[str, Any] = {
        "seed_family": family.seed_family,
        "control_role": control.control_role,
        "expected_outcome": control.expected_outcome,
    }
    parameters.update(dict(control.parameter_overrides))
    parameters.update(dict(parameter_overrides or {}))
    return parameters


def _node_count_for_family(family: GRC9V3SeedFamilySpec, parameters: Mapping[str, Any]) -> int:
    if "resolved_node_count" in parameters:
        return _positive_int(parameters["resolved_node_count"], field_name="resolved_node_count")
    if isinstance(family.node_count, int):
        return family.node_count
    defaults = {
        "spark_to_expansion": 12,
        "appendix_e_cell_division": 12,
    }
    return defaults.get(family.seed_family, 8)


def _star_graph(
    *,
    node_count: int,
    active_degree: int,
    conductance: float = 1.0,
    flux_uv: float = 0.0,
    role: str = "candidate_port_edge",
) -> _GraphBuilder:
    graph = _GraphBuilder(node_count)
    degree = min(active_degree, node_count - 1, 9)
    for port_id in range(1, degree + 1):
        graph.connect(
            0,
            port_id,
            port_id,
            1,
            conductance=conductance,
            flux_uv=flux_uv,
            role=role,
        )
    for node_id in range(degree + 1, node_count):
        graph.connect(
            node_id - 1,
            2,
            node_id,
            1,
            conductance=max(conductance * 0.5, 0.01),
            flux_uv=0.0,
            role="connectivity_chain",
        )
    return graph


def _appendix_e_graph(parameters: Mapping[str, Any]) -> _GraphBuilder:
    graph = _GraphBuilder(12)
    active_degree = 8 if parameters.get("appendix_e_no_completion_control") else 9
    for port_id in range(1, active_degree + 1):
        graph.connect(
            0,
            port_id,
            port_id,
            1,
            conductance=1.0,
            flux_uv=0.0,
            role="saturating_parent_boundary",
        )
    for support_port, node_id in enumerate((1, 2, 4, 5, 7, 8), start=1):
        graph.connect(
            node_id,
            2,
            10,
            support_port,
            conductance=1.0,
            flux_uv=0.0,
            role="daughter_a_support",
        )
    for support_port, node_id in enumerate((3, 6, 9), start=1):
        graph.connect(
            node_id,
            2,
            11,
            support_port,
            conductance=1.0,
            flux_uv=0.0,
            role="daughter_b_support",
        )
    return graph


def _complex_growth_appendix_graph(parameters: Mapping[str, Any]) -> _GraphBuilder:
    graph = _appendix_e_graph(parameters)
    if graph.node_count != 12:
        raise ValueError("complex Appendix E growth graph expects base node count 12")
    graph.node_count = 15
    graph.connect(10, 7, 12, 1, conductance=0.5, role="growth_lobe_bridge")
    graph.connect(12, 2, 13, 1, conductance=1.0, role="growth_pressure_path_a")
    graph.connect(12, 3, 14, 1, conductance=1.0, role="growth_pressure_path_b")
    return graph


def _choice_graph(parameters: Mapping[str, Any]) -> _GraphBuilder:
    if parameters.get("refined_fixture"):
        graph = _GraphBuilder(3)
        graph.connect(0, 1, 1, 1, conductance=1.0, flux_uv=1.0, role="choice_winner_path")
        graph.connect(0, 2, 2, 1, conductance=1.0, flux_uv=0.1, role="choice_loser_path")
        return graph
    graph = _GraphBuilder(12)
    for port_id in range(1, 5):
        graph.connect(0, port_id, port_id, 1, conductance=1.0, role="choice_spoke")
    graph.connect(0, 5, 10, 1, conductance=2.0, flux_uv=1.0, role="winner_path")
    graph.connect(0, 6, 11, 1, conductance=0.5, flux_uv=0.2, role="loser_path")
    for node_id in range(5, 10):
        graph.connect(node_id - 1, 2, node_id, 1, conductance=0.5, role="basin_support")
    return graph


def _graph_for_family(
    family: GRC9V3SeedFamilySpec,
    parameters: Mapping[str, Any],
) -> _GraphBuilder:
    if family.seed_family == "appendix_e_cell_division":
        return _appendix_e_graph(parameters)
    if family.seed_family == "choice_collapse":
        return _choice_graph(parameters)
    if parameters.get("refined_fixture") and family.seed_family in {
        "growth_pressure",
        "transport_basin_rerouting",
    }:
        graph = _GraphBuilder(3)
        graph.connect(0, 1, 1, 1, conductance=1.0, flux_uv=1.0, role=f"{family.seed_family}_path_a")
        graph.connect(0, 2, 2, 1, conductance=1.0, flux_uv=0.95, role=f"{family.seed_family}_path_b")
        return graph
    node_count = _node_count_for_family(family, parameters)
    active_degree = int(parameters.get("active_degree", parameters.get("active_degree_max", 6)))
    if family.seed_family in {"hybrid_spark_gate", "spark_to_expansion"}:
        active_degree = int(parameters.get("active_degree", 9))
    if family.seed_family == "quiescent_hybrid_control":
        active_degree = int(parameters.get("active_degree_max", 5))
    conductance = _config_float(
        parameters.get("conductance", parameters.get("path_conductance_ratio", 1.0)),
        1.0,
        field_name="conductance",
    )
    flux_uv = 0.0
    if family.seed_family in {"growth_pressure", "transport_basin_rerouting"}:
        flux_uv = _config_float(parameters.get("flux_gap", 1.0), 1.0, field_name="flux_gap")
    return _star_graph(
        node_count=node_count,
        active_degree=active_degree,
        conductance=conductance,
        flux_uv=flux_uv,
        role=f"{family.seed_family}_edge",
    )


def _node_states(
    *,
    node_count: int,
    parameters: Mapping[str, Any],
    seed_family: str,
) -> dict[str, dict[str, Any]]:
    coherence_base = _config_float(parameters.get("coherence", 9.0), 9.0, field_name="coherence")
    signed_hessian = -1e-6 if parameters.get("signed_hessian_min") == "below_epsilon" else 1e-2
    nodes: dict[str, dict[str, Any]] = {}
    for node_id in range(node_count):
        coherence = float(coherence_base)
        if parameters.get("refined_fixture") and seed_family == "choice_collapse":
            if parameters.get("control_role") == "positive_control":
                coherence = {0: 10.0, 1: 0.1, 2: 1.0}.get(node_id, 1.0)
            else:
                coherence = {0: 1.0, 1: 0.1, 2: 0.1}.get(node_id, 1.0)
        elif parameters.get("refined_fixture") and seed_family == "growth_pressure":
            coherence = {0: 2.0, 1: 1.0, 2: 1.0}.get(node_id, 1.0)
        elif parameters.get("refined_fixture") and seed_family == "transport_basin_rerouting":
            if parameters.get("control_role") == "positive_control":
                coherence = {0: 2.0, 1: 0.1, 2: 1.0}.get(node_id, 1.0)
            else:
                coherence = {0: 1.0, 1: 0.1, 2: 0.1}.get(node_id, 1.0)
        basin_id: str | int = "root" if node_id == 0 else node_id
        parent_id = None
        depth = 0
        if seed_family == "appendix_e_cell_division" and node_id in {10, 11}:
            basin_id = f"daughter_{node_id}"
            parent_id = "root"
            depth = 1
        nodes[str(node_id)] = {
            "coherence": coherence,
            "gradient_row_basis": [0.0, 0.0, 0.0],
            "signed_hessian_row_basis": [signed_hessian, 0.01, 0.02],
            "net_flux_summary": [0.0, 0.0, 0.0],
            "basin_mass": coherence,
            "basin_id": basin_id,
            "parent_id": parent_id,
            "depth": depth,
        }
    return nodes


def _base_runtime_config(parameters: Mapping[str, Any]) -> dict[str, Any]:
    hessian_backend = str(parameters.get("hessian_backend", "row_basis_diagonal"))
    raw_lambda_birth = parameters.get("lambda_birth", parameters.get("birth_lambda", 0.0))
    lambda_birth_default = 10.0 if raw_lambda_birth in {"high", "low"} else 0.0
    lambda_birth = _config_float(
        raw_lambda_birth,
        lambda_birth_default,
        field_name="lambda_birth",
    )
    compatibility_score_params = None
    if parameters.get("refined_fixture") and parameters.get("seed_family") == "choice_collapse":
        compatibility_score_params = {
            "epsilon_choice": 0.01,
            "epsilon_collapse": 0.02,
        }
    evolution: dict[str, Any] = {
        "eps_spark": _config_float(
            parameters.get("epsilon_spark", parameters.get("eps_spark", 1e-6)),
            1e-6,
            field_name="eps_spark",
        ),
        "D_eff_target": int(
            parameters.get("target_effective_degree", parameters.get("D_eff_target", 16))
        ),
        "w_bond": _config_float(parameters.get("w_bond", 0.05), 0.05, field_name="w_bond"),
        "lambda_birth": lambda_birth,
        "rng_seed": int(parameters.get("rng_seed", 0)),
    }
    if compatibility_score_params is not None:
        evolution["compatibility_score_params"] = compatibility_score_params
    modes: dict[str, Any] = {
        "hessian_backend": hessian_backend,
        "boundary_mode": str(parameters.get("boundary_mode", "prune")),
        "expansion_distribution_mode": str(
            parameters.get("expansion_distribution_mode", "equal")
        ),
        "budget_correction_method": str(
            parameters.get("budget_correction_method", "simplex_projection")
        ),
        "choice_backend": str(
            parameters.get(
                "choice_backend",
                "disabled"
                if parameters.get("refined_fixture")
                and parameters.get("seed_family")
                in {"growth_pressure", "transport_basin_rerouting"}
                else "sink_compatibility",
            )
        ),
        "spark_signed_crossing": bool(parameters.get("spark_signed_crossing", False)),
    }
    if "growth_parent_eligibility" in parameters:
        modes["growth_parent_eligibility"] = str(parameters["growth_parent_eligibility"])
    return {
        "dt": 0.05,
        "evolution": evolution,
        "constitutive_semantic_modes": modes,
    }


def _state_payload(
    *,
    graph: _GraphBuilder,
    parameters: Mapping[str, Any],
    seed_name: str,
    family: GRC9V3SeedFamilySpec,
) -> dict[str, Any]:
    node_states = _node_states(
        node_count=graph.node_count,
        parameters=parameters,
        seed_family=family.seed_family,
    )
    coherence_sum = sum(float(node["coherence"]) for node in node_states.values())
    budget_error = _config_float(
        parameters.get("budget_error", 0.0),
        0.0,
        field_name="budget_error",
    )
    budget_target = coherence_sum - budget_error
    sink_set = [0]
    basins: dict[str, list[int]] = {"0": list(range(graph.node_count))}
    hierarchy: dict[str, list[str]] = {}
    if family.seed_family == "appendix_e_cell_division":
        sink_set = [0, 10, 11]
        basins = {
            "0": list(range(10)),
            "10": [1, 2, 4, 5, 7, 8, 10],
            "11": [3, 6, 9, 11],
        }
        hierarchy = {"root": ["daughter_10", "daughter_11"]}
    elif parameters.get("refined_fixture") and family.seed_family in {
        "choice_collapse",
        "growth_pressure",
        "transport_basin_rerouting",
    }:
        sink_set = [1, 2]
        basins = {"1": [1], "2": [2]}
    cached_quantities = {
        "discovery_seed_name": seed_name,
        "discovery_seed_family": family.seed_family,
        "discovery_seed_parameters": _json_safe(parameters),
        "required_checkpoint_overlays": list(family.required_checkpoint_overlays),
        "initial_budget_error": coherence_sum - budget_target,
    }
    choice_registry: dict[str, Any] = {}
    if (
        parameters.get("refined_fixture")
        and family.seed_family == "choice_collapse"
        and parameters.get("control_role") == "positive_control"
    ):
        choice_registry = {
            "0": {
                "backend": "sink_compatibility",
                "node_id": 0,
                "viable_sink_ids": ["1", "2"],
                "seeded_for": "refined_collapse_fixture",
            }
        }
    if family.seed_family == "coarse_cache_invalidation":
        if (
            parameters.get("refined_fixture")
            and parameters.get("control_role") == "negative_control"
        ):
            coarse_cache = {}
        else:
            coarse_cache = {
                "coarse_cache_state": "warm",
                "coarse_cache_invalidation_reason": None,
            }
    else:
        coarse_cache = {}
    return {
        "topology": graph.topology(),
        "nodes": node_states,
        "port_edges": graph.port_edges,
        "base_conductance": {
            edge_id: edge["conductance"] for edge_id, edge in graph.port_edges.items()
        },
        "geometric_length": {str(edge_id): 1.0 for edge_id in range(len(graph.edges))},
        "temporal_delay": {str(edge_id): 1.0 for edge_id in range(len(graph.edges))},
        "flux_coupling": {
            edge_id: abs(float(edge["flux_uv"])) for edge_id, edge in graph.port_edges.items()
        },
        "potential": {str(node_id): 0.0 for node_id in range(graph.node_count)},
        "sink_set": sink_set,
        "basins": basins,
        "hierarchy": hierarchy,
        "choice_registry": choice_registry,
        "collapse_registry": {},
        "coarse_cache": coarse_cache,
        "budget_target": budget_target,
        "cached_quantities": cached_quantities,
    }


def _live_nodes(state_payload: Mapping[str, Any]) -> set[int]:
    topology = state_payload["topology"]
    return {int(node["node_id"]) for node in topology["nodes"]}


def _live_edges(state_payload: Mapping[str, Any]) -> set[int]:
    topology = state_payload["topology"]
    return {int(edge["edge_id"]) for edge in topology["edges"]}


def _validate_graph_connectivity(state_payload: Mapping[str, Any]) -> None:
    live_nodes = _live_nodes(state_payload)
    if not live_nodes:
        raise ValueError("GRC9V3 seed graph must contain at least one node")
    adjacency: dict[int, set[int]] = {node_id: set() for node_id in live_nodes}
    for edge in state_payload["topology"]["edges"]:
        node_a = int(edge["endpoint_a"]["node_id"])
        node_b = int(edge["endpoint_b"]["node_id"])
        adjacency[node_a].add(node_b)
        adjacency[node_b].add(node_a)
    seen: set[int] = set()
    stack = [min(live_nodes)]
    while stack:
        node_id = stack.pop()
        if node_id in seen:
            continue
        seen.add(node_id)
        stack.extend(sorted(adjacency[node_id] - seen))
    if seen != live_nodes:
        raise ValueError("GRC9V3 seed graph must be connected")


def _validate_port_structure(state_payload: Mapping[str, Any]) -> None:
    topology = state_payload["topology"]
    live_edges = _live_edges(state_payload)
    port_structure = topology.get("port_structure")
    if not isinstance(port_structure, Mapping) or not port_structure:
        raise ValueError("GRC9V3 seed topology must include port_structure metadata")
    port_to_edge = port_structure.get("port_to_edge")
    if not isinstance(port_to_edge, Mapping) or not port_to_edge:
        raise ValueError("GRC9V3 seed port_structure.port_to_edge must not be empty")
    for endpoint, edge_id in port_to_edge.items():
        node_text, port_text = str(endpoint).split(":", maxsplit=1)
        node_id = int(node_text)
        port_id = int(port_text)
        if node_id not in _live_nodes(state_payload):
            raise ValueError("GRC9V3 seed port_structure references unknown node")
        if port_id not in range(1, 10):
            raise ValueError("GRC9V3 seed port_structure ports must be 1..9")
        if int(edge_id) not in live_edges:
            raise ValueError("GRC9V3 seed port_structure references unknown edge")


def _validate_sink_basin_consistency(state_payload: Mapping[str, Any]) -> None:
    live_nodes = _live_nodes(state_payload)
    sink_set = {int(node_id) for node_id in state_payload.get("sink_set", [])}
    if sink_set - live_nodes:
        raise ValueError("GRC9V3 seed sink_set references unknown nodes")
    basins = state_payload.get("basins", {})
    if not isinstance(basins, Mapping):
        raise ValueError("GRC9V3 seed basins must be a mapping")
    for sink_id, members in basins.items():
        if int(sink_id) not in live_nodes:
            raise ValueError("GRC9V3 seed basin key references unknown sink")
        member_set = {int(member) for member in members}
        if member_set - live_nodes:
            raise ValueError("GRC9V3 seed basin membership references unknown nodes")
    basin_keys = {int(sink_id) for sink_id in basins}
    if sink_set and not basin_keys:
        raise ValueError("GRC9V3 seed with sinks must include basin mappings")
    if basin_keys - sink_set:
        raise ValueError("GRC9V3 seed basin keys must be listed in sink_set")
    if sink_set - basin_keys:
        raise ValueError("GRC9V3 seed sink_set nodes must have basin mappings")


def _validate_hierarchy_consistency(state_payload: Mapping[str, Any]) -> None:
    nodes = state_payload.get("nodes", {})
    basin_ids = {str(node.get("basin_id")) for node in nodes.values()}
    hierarchy = state_payload.get("hierarchy", {})
    if not isinstance(hierarchy, Mapping):
        raise ValueError("GRC9V3 seed hierarchy must be a mapping")
    for parent_id, children in hierarchy.items():
        if str(parent_id) not in basin_ids:
            raise ValueError("GRC9V3 seed hierarchy parent must match a basin id")
        for child_id in children:
            if str(child_id) not in basin_ids:
                raise ValueError("GRC9V3 seed hierarchy child must match a basin id")


def _validate_budget_target(state_payload: Mapping[str, Any]) -> None:
    nodes = state_payload.get("nodes", {})
    coherence_sum = sum(float(node["coherence"]) for node in nodes.values())
    budget_target = _finite_float(
        state_payload.get("budget_target"),
        field_name="budget_target",
    )
    if budget_target < 0.0:
        raise ValueError("GRC9V3 seed budget_target must be non-negative")
    cached = state_payload.get("cached_quantities", {})
    budget_error = float(cached.get("initial_budget_error", coherence_sum - budget_target))
    if not math.isclose(coherence_sum - budget_target, budget_error, rel_tol=1e-9, abs_tol=1e-9):
        raise ValueError("GRC9V3 seed initial budget error metadata is inconsistent")


def _validate_capability_requirements(seed: GRC9V3GeneratedSeed) -> None:
    modes = seed.expected_runtime_config.get("constitutive_semantic_modes", {})
    if modes.get("boundary_mode", "prune") != "prune":
        raise ValueError("GRC9V3 discovery seeds currently require boundary_mode='prune'")
    if bool(modes.get("spark_signed_crossing", False)):
        raise ValueError(
            "GRC9V3 discovery seeds cannot enable spark_signed_crossing until "
            "the catalog schedules that capability"
        )


def _validate_seed(seed: GRC9V3GeneratedSeed) -> None:
    _validate_graph_connectivity(seed.state_payload)
    _validate_port_structure(seed.state_payload)
    _validate_sink_basin_consistency(seed.state_payload)
    _validate_hierarchy_consistency(seed.state_payload)
    _validate_budget_target(seed.state_payload)
    _validate_capability_requirements(seed)
    GRC9V3.from_state(
        state=dict(seed.state_payload),
        params=dict(seed.expected_runtime_config),
    )


def _appendix_e_family(catalog: GRC9V3HypothesisCatalog) -> GRC9V3SeedFamilySpec:
    for family in catalog.seed_families:
        if family.seed_family == "appendix_e_cell_division":
            return family
    raise ValueError("default GRC9V3 catalog is missing appendix_e_cell_division")


def _hessian_family(catalog: GRC9V3HypothesisCatalog) -> GRC9V3SeedFamilySpec:
    for family in catalog.seed_families:
        if family.seed_family == "hessian_backend_comparison":
            return family
    raise ValueError("default GRC9V3 catalog is missing hessian_backend_comparison")


def _complex_seed(
    *,
    example_name: str,
    state_payload: Mapping[str, Any],
    parameters: Mapping[str, Any],
    expected_runtime_config: Mapping[str, Any],
    predicted_event_sequence: tuple[str, ...],
    overlays: tuple[str, ...],
    validate: bool,
) -> GRC9V3GeneratedSeed:
    control_role = (
        "perturbation_control"
        if str(parameters.get("control_role")) == "perturbation_control"
        else "complex_control"
    )
    lane_name = generated_lane_name(example_name, control_role)
    seed = GRC9V3GeneratedSeed(
        seed_family=example_name,
        seed_name=lane_name,
        control_role=control_role,
        lane_name=lane_name,
        profile=GRC9V3_COMPLEX_HYBRID_PROFILE,
        generator_version=GRC9V3_SEED_GENERATOR_VERSION,
        seed_parameters=parameters,
        expected_runtime_config=expected_runtime_config,
        ownership_tags=("grc9_mechanical", "grcv3_semantic", "grc9v3_hybrid"),
        graph_preconditions={
            "connected_graph": True,
            "pure_runtime_fixture": True,
            "complex_example": example_name,
        },
        state_preconditions={
            "single_connected_component": True,
            "source_language_claims": False,
        },
        predicted_signatures=(),
        predicted_event_sequence=predicted_event_sequence,
        required_checkpoint_overlays=overlays,
        state_payload=state_payload,
    )
    if validate:
        _validate_seed(seed)
    return seed


def _complex_appendix_state(
    *,
    family: GRC9V3SeedFamilySpec,
    graph: _GraphBuilder,
    parameters: Mapping[str, Any],
    seed_name: str,
) -> dict[str, Any]:
    state_payload = _state_payload(
        graph=graph,
        parameters=parameters,
        seed_name=seed_name,
        family=family,
    )
    state_payload["cached_quantities"]["discovery_seed_family"] = parameters[
        "seed_family"
    ]
    state_payload["cached_quantities"]["discovery_seed_name"] = seed_name
    return state_payload


def generate_grc9v3_complex_hybrid_example(
    example_name: str,
    *,
    catalog: GRC9V3HypothesisCatalog | None = None,
    validate: bool = True,
) -> GRC9V3GeneratedSeed:
    """Generate one connected Iteration 7 complex GRC9V3 runtime example."""

    if example_name not in GRC9V3_COMPLEX_HYBRID_NAMES:
        raise ValueError(f"unknown GRC9V3 complex hybrid example {example_name!r}")
    active_catalog = catalog or default_grc9v3_hypothesis_catalog()
    appendix_family = _appendix_e_family(active_catalog)
    overlays = ("node_overlay", "port_overlay", "module_overlay", "flow_overlay")
    parameters: dict[str, Any] = {
        "seed_family": example_name,
        "control_role": "complex_control",
        "refined_fixture": True,
        "expected_outcome": "connected complex hybrid runtime example",
    }

    if example_name == "complex_spark_expansion_hierarchy":
        graph = _appendix_e_graph(parameters)
        state_payload = _complex_appendix_state(
            family=appendix_family,
            graph=graph,
            parameters=parameters,
            seed_name=f"{example_name}_complex_control",
        )
        return _complex_seed(
            example_name=example_name,
            state_payload=state_payload,
            parameters=parameters,
            expected_runtime_config=_base_runtime_config(parameters),
            predicted_event_sequence=(
                "hybrid_spark_candidate",
                "hybrid_mechanical_expansion",
                "hybrid_spark_completed",
            ),
            overlays=overlays,
            validate=validate,
        )

    if example_name == "complex_spark_expansion_choice_collapse":
        graph = _appendix_e_graph(parameters)
        state_payload = _complex_appendix_state(
            family=appendix_family,
            graph=graph,
            parameters=parameters,
            seed_name=f"{example_name}_complex_control",
        )
        state_payload["choice_registry"] = {
            "1": {
                "backend": "sink_compatibility",
                "node_id": 1,
                "viable_sink_ids": ["10", "11"],
                "seeded_for": "complex_spark_expansion_choice_collapse",
            }
        }
        return _complex_seed(
            example_name=example_name,
            state_payload=state_payload,
            parameters={
                **parameters,
                "expected_outcome": (
                    "spark expansion is followed by a seeded choice collapse "
                    "on the same connected graph"
                ),
            },
            expected_runtime_config=_base_runtime_config(parameters),
            predicted_event_sequence=(
                "hybrid_spark_candidate",
                "hybrid_mechanical_expansion",
                "hybrid_spark_completed",
                "collapse",
            ),
            overlays=(*overlays, "choice_overlay"),
            validate=validate,
        )

    if example_name in {
        "complex_expansion_growth_budget_coarse",
        "complex_growth_low_birth_perturbation",
    }:
        parameters.update(
            {
                "lambda_birth": 1000.0,
                "budget_error": 0.25,
                "coarse_warm": True,
                "expected_outcome": (
                    "expansion and connected growth lobe exercise budget and "
                    "coarse-cache telemetry"
                ),
            }
        )
        if example_name == "complex_growth_low_birth_perturbation":
            parameters["control_role"] = "perturbation_control"
            parameters["lambda_birth"] = 0.01
            parameters["expected_outcome"] = (
                "low birth-rate perturbation preserves expansion but suppresses "
                "the connected growth lobe"
            )
        graph = _complex_growth_appendix_graph(parameters)
        seed_name = generated_lane_name(example_name, str(parameters["control_role"]))
        state_payload = _complex_appendix_state(
            family=appendix_family,
            graph=graph,
            parameters=parameters,
            seed_name=seed_name,
        )
        for node_id, coherence in {"12": 2.0, "13": 1.0, "14": 1.0}.items():
            state_payload["nodes"][node_id]["coherence"] = coherence
        coherence_sum = sum(
            float(node["coherence"]) for node in state_payload["nodes"].values()
        )
        state_payload["budget_target"] = coherence_sum - float(parameters["budget_error"])
        state_payload["cached_quantities"]["initial_budget_error"] = float(
            parameters["budget_error"]
        )
        state_payload["coarse_cache"] = {"seeded": "warm"}
        predicted = (
            "hybrid_spark_candidate",
            "hybrid_mechanical_expansion",
            "hybrid_spark_completed",
            "growth",
        )
        if example_name == "complex_growth_low_birth_perturbation":
            predicted = (
                "hybrid_spark_candidate",
                "hybrid_mechanical_expansion",
                "hybrid_spark_completed",
            )
        return _complex_seed(
            example_name=example_name,
            state_payload=state_payload,
            parameters=parameters,
            expected_runtime_config=_base_runtime_config(parameters),
            predicted_event_sequence=predicted,
            overlays=overlays,
            validate=validate,
        )

    if example_name == "complex_spark_choice_no_saturation_perturbation":
        parameters.update(
            {
                "control_role": "perturbation_control",
                "appendix_e_no_completion_control": True,
                "expected_outcome": (
                    "connected perturbation removes saturation and suppresses "
                    "spark/expansion/choice cascade"
                ),
            }
        )
        graph = _appendix_e_graph(parameters)
        state_payload = _complex_appendix_state(
            family=appendix_family,
            graph=graph,
            parameters=parameters,
            seed_name=f"{example_name}_perturbation_control",
        )
        state_payload["choice_registry"] = {
            "1": {
                "backend": "sink_compatibility",
                "node_id": 1,
                "viable_sink_ids": ["10", "11"],
                "seeded_for": "complex_spark_choice_no_saturation_perturbation",
            }
        }
        return _complex_seed(
            example_name=example_name,
            state_payload=state_payload,
            parameters=parameters,
            expected_runtime_config=_base_runtime_config(parameters),
            predicted_event_sequence=(),
            overlays=(*overlays, "choice_overlay"),
            validate=validate,
        )

    hessian_family = _hessian_family(active_catalog)
    hessian_backend = (
        "weighted_least_squares"
        if example_name == "complex_hessian_weighted_least_squares"
        else "row_basis_diagonal"
    )
    parameters.update(
        {
            "seed_family": "hessian_backend_comparison",
            "control_role": (
                "positive_control"
                if hessian_backend == "weighted_least_squares"
                else "baseline_control"
            ),
            "hessian_backend": hessian_backend,
            "expected_outcome": "same connected graph under paired Hessian backend",
        }
    )
    graph = _graph_for_family(hessian_family, parameters)
    state_payload = _state_payload(
        graph=graph,
        parameters=parameters,
        seed_name=f"{example_name}_complex_control",
        family=hessian_family,
    )
    state_payload["cached_quantities"]["discovery_seed_family"] = example_name
    state_payload["cached_quantities"]["discovery_seed_name"] = (
        f"{example_name}_complex_control"
    )
    return _complex_seed(
        example_name=example_name,
        state_payload=state_payload,
        parameters={**parameters, "seed_family": example_name},
        expected_runtime_config=_base_runtime_config(parameters),
        predicted_event_sequence=(),
        overlays=("node_overlay", "flow_overlay"),
        validate=validate,
    )


def _pressure_boundary_graph() -> _GraphBuilder:
    graph = _GraphBuilder(3)
    graph.connect(0, 1, 1, 1, conductance=1.0, role="pressure_boundary_support_a")
    graph.connect(0, 2, 2, 1, conductance=1.0, role="pressure_boundary_support_b")
    return graph


def _pressure_boundary_node_state(
    coherence: float,
    *,
    basin_id: str | int,
) -> dict[str, Any]:
    return {
        "coherence": float(coherence),
        "gradient_row_basis": [0.0, 0.0, 0.0],
        "signed_hessian_row_basis": [0.1, 0.1, 0.1],
        "net_flux_summary": [0.0, 0.0, 0.0],
        "basin_mass": float(coherence),
        "basin_id": basin_id,
        "parent_id": None,
        "depth": 0,
    }


def _pressure_boundary_state_payload(
    *,
    example_name: str,
    front_capacity_source: str,
    parameters: Mapping[str, Any],
) -> dict[str, Any]:
    graph = _pressure_boundary_graph()
    lane_name = generated_lane_name(example_name, "positive_control")
    return {
        "topology": graph.topology(),
        "nodes": {
            "0": _pressure_boundary_node_state(2.0, basin_id="root"),
            "1": _pressure_boundary_node_state(1.0, basin_id=1),
            "2": _pressure_boundary_node_state(1.0, basin_id=2),
        },
        "port_edges": graph.port_edges,
        "base_conductance": {
            edge_id: edge["conductance"] for edge_id, edge in graph.port_edges.items()
        },
        "geometric_length": {str(edge_id): 1.0 for edge_id in range(len(graph.edges))},
        "temporal_delay": {str(edge_id): 1.0 for edge_id in range(len(graph.edges))},
        "flux_coupling": {
            edge_id: abs(float(edge["flux_uv"])) for edge_id, edge in graph.port_edges.items()
        },
        "potential": {"0": 0.0, "1": 0.0, "2": 0.0},
        "sink_set": [0],
        "basins": {"0": [0, 1, 2]},
        "hierarchy": {},
        "choice_registry": {},
        "collapse_registry": {},
        "coarse_cache": {},
        "budget_target": 4.0,
        "cached_quantities": {
            "discovery_seed_name": lane_name,
            "discovery_seed_family": example_name,
            "discovery_seed_parameters": _json_safe(parameters),
            "required_checkpoint_overlays": ["node_overlay", "port_overlay", "flow_overlay"],
            "initial_budget_error": 0.0,
            "grcl9v3_front_growth_eligible_ports": {"0": [6]},
            "grcl9v3_growth_parent_capacity_sources": {
                "0": {
                    "construct_id": f"{example_name}_front",
                    "growth_semantics": "front_capacity",
                    "front_capacity_source": front_capacity_source,
                    "front_source_construct_id": None,
                    "inactive_parent_port": 6,
                }
            },
            "grcl9v3_expected_pressure_boundary_region_ids": (
                [0] if front_capacity_source == "pressure_boundary" else []
            ),
        },
    }


def _pressure_boundary_seed(
    *,
    example_name: str,
    state_payload: Mapping[str, Any],
    parameters: Mapping[str, Any],
    predicted_event_sequence: tuple[str, ...],
    validate: bool,
) -> GRC9V3GeneratedSeed:
    lane_name = generated_lane_name(example_name, "positive_control")
    seed = GRC9V3GeneratedSeed(
        seed_family=example_name,
        seed_name=lane_name,
        control_role="positive_control",
        lane_name=lane_name,
        profile=GRC9V3_PRESSURE_BOUNDARY_PROFILE,
        generator_version=GRC9V3_SEED_GENERATOR_VERSION,
        seed_parameters=parameters,
        expected_runtime_config=_base_runtime_config(parameters),
        ownership_tags=("grc9_mechanical", "grc9v3_hybrid"),
        graph_preconditions={
            "connected_graph": True,
            "front_capacity_source": parameters.get("front_capacity_source"),
            "pressure_boundary_evidence": (
                parameters.get("front_capacity_source") == "pressure_boundary"
            ),
        },
        state_preconditions={
            "growth_parent_eligibility": "grcl9v3_front_capacity",
            "source_language_claims": False,
        },
        predicted_signatures=(),
        predicted_event_sequence=predicted_event_sequence,
        required_checkpoint_overlays=("node_overlay", "port_overlay", "flow_overlay"),
        state_payload=state_payload,
    )
    if validate:
        _validate_seed(seed)
    return seed


def generate_grc9v3_pressure_boundary_example(
    example_name: str,
    *,
    catalog: GRC9V3HypothesisCatalog | None = None,
    validate: bool = True,
) -> GRC9V3GeneratedSeed:
    """Generate one pressure-boundary GRC9V3 runtime evidence example."""

    if example_name not in GRC9V3_PRESSURE_BOUNDARY_NAMES:
        raise ValueError(f"unknown GRC9V3 pressure-boundary example {example_name!r}")
    active_catalog = catalog or default_grc9v3_hypothesis_catalog()
    parameters: dict[str, Any] = {
        "seed_family": example_name,
        "control_role": "positive_control",
        "growth_parent_eligibility": "grcl9v3_front_capacity",
        "front_capacity_source": "pressure_boundary",
        "lambda_birth": 1000.0,
        "choice_backend": "disabled",
        "expected_outcome": "corrected pressure-boundary front growth",
    }
    if example_name == "pressure_boundary_growth_no_growth_control":
        parameters.update(
            {
                "lambda_birth": 0.0,
                "expected_outcome": (
                    "pressure-boundary front capacity is declared, but zero birth "
                    "rate suppresses growth"
                ),
            }
        )
    if example_name == "generic_front_capacity_growth_comparison":
        parameters.update(
            {
                "front_capacity_source": "spark_expansion_front",
                "expected_outcome": (
                    "generic corrected front-capacity growth should not count as "
                    "pressure-boundary growth"
                ),
            }
        )
    if example_name == "complex_spark_expansion_pressure_boundary_growth":
        appendix_family = _appendix_e_family(active_catalog)
        parameters.update(
            {
                "refined_fixture": True,
                "budget_error": 0.25,
                "coarse_warm": True,
                "expected_outcome": (
                    "spark expansion and completed hybrid spark occur on the "
                    "same graph as pressure-boundary front growth"
                ),
            }
        )
        graph = _complex_growth_appendix_graph(parameters)
        seed_name = generated_lane_name(example_name, "positive_control")
        state_payload = _complex_appendix_state(
            family=appendix_family,
            graph=graph,
            parameters=parameters,
            seed_name=seed_name,
        )
        for node_id, coherence in {"12": 2.0, "13": 1.0, "14": 1.0}.items():
            state_payload["nodes"][node_id]["coherence"] = coherence
        coherence_sum = sum(
            float(node["coherence"]) for node in state_payload["nodes"].values()
        )
        state_payload["budget_target"] = coherence_sum - float(parameters["budget_error"])
        state_payload["cached_quantities"]["initial_budget_error"] = float(
            parameters["budget_error"]
        )
        state_payload["coarse_cache"] = {"seeded": "warm"}
        state_payload["cached_quantities"]["grcl9v3_front_growth_eligible_ports"] = {
            "12": [4]
        }
        state_payload["cached_quantities"]["grcl9v3_growth_parent_capacity_sources"] = {
            "12": {
                "construct_id": "complex_pressure_boundary_front",
                "growth_semantics": "front_capacity",
                "front_capacity_source": "pressure_boundary",
                "front_source_construct_id": None,
                "inactive_parent_port": 4,
            }
        }
        state_payload["cached_quantities"][
            "grcl9v3_expected_pressure_boundary_region_ids"
        ] = [12]
        return _pressure_boundary_seed(
            example_name=example_name,
            state_payload=state_payload,
            parameters=parameters,
            predicted_event_sequence=(
                "hybrid_spark_candidate",
                "hybrid_mechanical_expansion",
                "hybrid_spark_completed",
                "growth",
            ),
            validate=validate,
        )

    state_payload = _pressure_boundary_state_payload(
        example_name=example_name,
        front_capacity_source=str(parameters["front_capacity_source"]),
        parameters=parameters,
    )
    predicted = () if float(parameters["lambda_birth"]) <= 0.0 else ("growth",)
    return _pressure_boundary_seed(
        example_name=example_name,
        state_payload=state_payload,
        parameters=parameters,
        predicted_event_sequence=predicted,
        validate=validate,
    )


def _default_negative_parent(
    family: GRC9V3SeedFamilySpec,
    control_role: str,
) -> str | None:
    if control_role != "negative_control":
        return None
    if family.positive_controls:
        return family.positive_controls[0].seed_name
    return None


def generate_grc9v3_seed(
    seed_family: str,
    control_role: str = "positive_control",
    *,
    parameter_overrides: Mapping[str, Any] | None = None,
    seed_name: str | None = None,
    catalog: GRC9V3HypothesisCatalog | None = None,
    validate: bool = True,
    negative_control_of: str | None = None,
    perturbation_of: str | None = None,
    lane_name_override: str | None = None,
) -> GRC9V3GeneratedSeed:
    """Generate one deterministic pure-runtime GRC9V3 constructor payload."""

    catalog = catalog or default_grc9v3_hypothesis_catalog()
    family_by_name = {item.seed_family: item for item in catalog.seed_families}
    if seed_family not in family_by_name:
        raise ValueError(f"unknown GRC9V3 seed family {seed_family!r}")
    family = family_by_name[seed_family]
    if family.runtime_status != GRC9V3_RUNTIME_TESTABLE or not family.scheduled_for_generation:
        raise ValueError(f"seed family {seed_family!r} is not currently testable")
    control = _control_by_role(family, control_role)
    parameters = _seed_parameters(family, control, parameter_overrides)
    graph = _graph_for_family(family, parameters)
    resolved_seed_name = seed_name or control.seed_name
    state_payload = _state_payload(
        graph=graph,
        parameters=parameters,
        seed_name=resolved_seed_name,
        family=family,
    )
    lane_name = lane_name_override or generated_lane_name(seed_family, control_role)
    seed = GRC9V3GeneratedSeed(
        seed_family=seed_family,
        seed_name=resolved_seed_name,
        control_role=control_role,
        lane_name=lane_name,
        profile=family.profile,
        generator_version=GRC9V3_SEED_GENERATOR_VERSION,
        seed_parameters=parameters,
        expected_runtime_config=_base_runtime_config(parameters),
        ownership_tags=family.ownership,
        graph_preconditions=dict(family.graph_preconditions),
        state_preconditions=dict(family.state_preconditions),
        predicted_signatures=tuple(
            item.to_mapping() for item in family.predicted_signatures
        ),
        predicted_event_sequence=family.predicted_event_sequence,
        required_checkpoint_overlays=family.required_checkpoint_overlays,
        state_payload=state_payload,
        negative_control_of=negative_control_of
        if negative_control_of is not None
        else _default_negative_parent(family, control_role),
        perturbation_of=perturbation_of,
    )
    if validate:
        _validate_seed(seed)
    return seed


def _apply_delta(value: Any, delta: str) -> Any:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise ValueError(
            "GRC9V3 seed perturbation deltas require numeric base parameters; "
            f"got {value!r}"
        )
    if delta.endswith("%"):
        return float(value) * (1.0 + float(delta[:-1]) / 100.0)
    return float(value) + float(delta)


def generate_grc9v3_seed_perturbation(
    seed_family: str,
    parameter: str,
    delta: str,
    *,
    parent_control_role: str = "positive_control",
    catalog: GRC9V3HypothesisCatalog | None = None,
    validate: bool = True,
) -> GRC9V3GeneratedSeed:
    """Generate one deterministic perturbation lane from a scheduled parent seed."""

    parent = generate_grc9v3_seed(
        seed_family,
        parent_control_role,
        catalog=catalog,
        validate=validate,
    )
    if parameter not in parent.seed_parameters:
        raise ValueError(
            f"cannot perturb missing GRC9V3 seed parameter {parameter!r}"
        )
    parameters = dict(parent.seed_parameters)
    parameters[parameter] = _apply_delta(parameters[parameter], delta)
    lane_name = perturbation_lane_name(seed_family, parent_control_role, parameter, delta)
    return generate_grc9v3_seed(
        seed_family,
        parent_control_role,
        catalog=catalog,
        parameter_overrides=parameters,
        seed_name=f"{parent.seed_name}_{parameter}_{delta}",
        validate=validate,
        perturbation_of=parent.seed_name,
        lane_name_override=lane_name,
    )


__all__ = [
    "GRC9V3_COMPLEX_HYBRID_NAMES",
    "GRC9V3_COMPLEX_HYBRID_PROFILE",
    "GRC9V3_PRESSURE_BOUNDARY_NAMES",
    "GRC9V3_PRESSURE_BOUNDARY_PROFILE",
    "GRC9V3_SEED_GENERATOR_VERSION",
    "GRC9V3GeneratedSeed",
    "generate_grc9v3_seed",
    "generate_grc9v3_complex_hybrid_example",
    "generate_grc9v3_pressure_boundary_example",
    "generate_grc9v3_seed_perturbation",
]
