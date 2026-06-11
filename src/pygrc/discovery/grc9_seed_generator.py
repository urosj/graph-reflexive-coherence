"""Deterministic GRC9 seed generators for phenomenology discovery."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import math
from typing import Any

from pygrc.models import GRC9

from .grc9_hypothesis_catalog import (
    GRC9HypothesisCatalog,
    GRC9SeedControlSpec,
    GRC9SeedFamilySpec,
    default_grc9_hypothesis_catalog,
)
from .grc9_manifest import generated_lane_name, perturbation_lane_name
from .grc9_mechanism_ledger import RUNTIME_TESTABLE


GRC9_SEED_GENERATOR_VERSION = "grc9_seed_generator_v1"
GRC9_LIFECYCLE_EMITTER_REPAIR_PROFILE = (
    "grc9_discovery_lifecycle_emitter_repair_v1"
)
GRC9_LIFECYCLE_COMBO_PROFILE = "grc9_discovery_lifecycle_combo_v1"
GRC9_TARGETED_DIAGNOSTIC_PROFILE = "grc9_discovery_targeted_diagnostic_v1"
GRC9_COMPLEX_EVENT_STABILITY_PROFILE = (
    "grc9_discovery_complex_event_stability_v1"
)
GRC9_CORRECTED_GROWTH_ELEMENTARY_PROFILE = (
    "grc9_growth_correction_elementary_v1"
)
GRC9_CORRECTED_GROWTH_COMBO_PROFILE = "grc9_growth_correction_combo_v1"
GRC9_CORRECTED_GROWTH_COMPLEX_PROFILE = "grc9_growth_correction_complex_v1"
GRC9_LIFECYCLE_EMITTER_NAMES = (
    "spark_column_proxy_emitter",
    "spark_instability_emitter",
    "spark_to_expansion_emitter",
    "growth_pressure_emitter",
    "post_expansion_fission_emitter",
)
GRC9_LIFECYCLE_EMITTER_PERTURBATION_NAMES = (
    "spark_column_proxy_eps_pass",
    "spark_column_proxy_eps_fail",
    "spark_instability_tau_pass",
    "spark_instability_tau_fail",
    "spark_to_expansion_d_eff_low",
    "spark_to_expansion_d_eff_high",
    "growth_pressure_lambda_high",
    "growth_pressure_lambda_low",
    "post_expansion_fission_min_mass_pass",
    "post_expansion_fission_min_mass_fail",
)
GRC9_LIFECYCLE_COMBO_NAMES = (
    "spark_growth_combo",
    "dual_spark_combo",
    "spark_fission_combo",
    "growth_fission_combo",
    "spark_growth_fission_combo",
)
GRC9_TARGETED_DIAGNOSTIC_NAMES = (
    "row_tensor_strong_anisotropy_control",
    "row_tensor_flat_control",
    "column_proxy_near_zero_control",
    "column_proxy_nonzero_control",
    "coarse_cache_populated_sparse_profile_control",
    "coarse_cache_populated_dense_profile_control",
    "budget_uniform_shift_trigger_control",
    "budget_simplex_projection_trigger_control",
    "transport_short_path_dominant_control",
    "transport_long_path_dominant_control",
)
GRC9_COMPLEX_EVENT_STABILITY_NAMES = (
    "all_events_complex_control",
    "all_events_complex_extra_leaf_perturbation_control",
    "all_events_complex_coherence_jitter_perturbation_control",
    "all_events_complex_soft_threshold_perturbation_control",
    "all_events_complex_high_degree_perturbation_control",
)
GRC9_CORRECTED_GROWTH_ELEMENTARY_NAMES = (
    "front_capacity_growth_positive_control",
    "front_capacity_growth_pressure_boundary_positive_control",
    "front_capacity_growth_no_front_control",
    "front_capacity_growth_zero_birth_control",
    "front_capacity_growth_pressure_boundary_zero_pressure_control",
    "front_capacity_growth_closed_front_control",
)
GRC9_CORRECTED_GROWTH_COMBO_NAMES = (
    "corrected_spark_growth_combo",
    "corrected_spark_pressure_boundary_growth_combo",
    "corrected_growth_fission_combo",
    "corrected_spark_growth_fission_combo",
)
GRC9_CORRECTED_GROWTH_COMPLEX_NAMES = (
    "corrected_all_events_complex_control",
    "corrected_all_events_complex_extra_leaf_perturbation_control",
    "corrected_all_events_complex_coherence_jitter_perturbation_control",
    "corrected_all_events_complex_soft_threshold_perturbation_control",
    "corrected_all_events_complex_high_degree_perturbation_control",
)

_EMITTER_PERTURBATION_SPECS: Mapping[str, tuple[str, Mapping[str, Any], str]] = {
    "spark_column_proxy_eps_pass": (
        "spark_column_proxy_emitter",
        {"eps_spark": 0.1},
        "column proxy remains active because min_abs_column is zero",
    ),
    "spark_column_proxy_eps_fail": (
        "spark_column_proxy_emitter",
        {"eps_spark": 0.0},
        "column proxy is suppressed because runtime uses strict min_abs < eps",
    ),
    "spark_instability_tau_pass": (
        "spark_instability_emitter",
        {"tau_instability": 0.7},
        "instability remains above threshold",
    ),
    "spark_instability_tau_fail": (
        "spark_instability_emitter",
        {"tau_instability": 0.9},
        "instability falls below threshold",
    ),
    "spark_to_expansion_d_eff_low": (
        "spark_to_expansion_emitter",
        {"D_eff_target": 16},
        "expansion still emits with smaller requested effective degree",
    ),
    "spark_to_expansion_d_eff_high": (
        "spark_to_expansion_emitter",
        {"D_eff_target": 44},
        "expansion still emits with larger requested effective degree",
    ),
    "growth_pressure_lambda_high": (
        "growth_pressure_emitter",
        {"lambda_birth": 1e9},
        "birth remains deterministic",
    ),
    "growth_pressure_lambda_low": (
        "growth_pressure_emitter",
        {"lambda_birth": 1e-6},
        "birth should be suppressed by low probability",
    ),
    "post_expansion_fission_min_mass_pass": (
        "post_expansion_fission_emitter",
        {"identity_fission_min_basin_mass": 0.0},
        "fission confirmation remains allowed",
    ),
    "post_expansion_fission_min_mass_fail": (
        "post_expansion_fission_emitter",
        {"identity_fission_min_basin_mass": 100.0},
        "fission confirmation is suppressed by basin mass threshold",
    ),
}


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


def _config_float(value: Any, default: float, *, field_name: str) -> float:
    if value in (None, "nominal"):
        return float(default)
    if value == "low":
        return float(default) * 0.1
    if value == "high":
        return float(default) * 10.0
    return _finite_float(value, field_name=field_name)


def _positive_int(value: Any, *, field_name: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{field_name} must be a positive integer")
    result = int(value)
    if result <= 0:
        raise ValueError(f"{field_name} must be positive")
    return result


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
                raise ValueError("GRC9 seed ports must be in the canonical 1..9 range")
            endpoint = (node_id, port_id)
            if endpoint in self._occupied_ports:
                raise ValueError(f"duplicate port endpoint in generated seed: {endpoint}")
            self._occupied_ports.add(endpoint)
        edge_id = len(self.edges)
        self.edges.append(
            {
                "edge_id": edge_id,
                "endpoint_a": {"node_id": node_a, "slot": port_a - 1},
                "endpoint_b": {"node_id": node_b, "slot": port_b - 1},
                "payload": {
                    "role": role,
                    "conductance": float(conductance),
                    "discovery_generator": GRC9_SEED_GENERATOR_VERSION,
                },
            }
        )
        self.port_edges[str(edge_id)] = _canonical_port_edge(
            node_a=node_a,
            port_a=port_a,
            node_b=node_b,
            port_b=port_b,
            conductance=_finite_float(conductance, field_name="conductance"),
            flux_uv=_finite_float(flux_uv, field_name="flux_uv"),
        )
        return edge_id

    def topology(self) -> dict[str, Any]:
        incidence: dict[str, list[int]] = {str(node_id): [] for node_id in range(self.node_count)}
        for edge in self.edges:
            edge_id = int(edge["edge_id"])
            incidence[str(edge["endpoint_a"]["node_id"])].append(edge_id)
            incidence[str(edge["endpoint_b"]["node_id"])].append(edge_id)
        return {
            "nodes": [
                {
                    "node_id": node_id,
                    "payload": {"discovery_node_index": node_id},
                }
                for node_id in range(self.node_count)
            ],
            "edges": list(self.edges),
            "incidence": {
                node_id: sorted(edge_ids) for node_id, edge_ids in sorted(incidence.items())
            },
            "port_structure": {},
            "edge_roles": {
                str(edge["edge_id"]): str(edge["payload"]["role"])
                for edge in self.edges
            },
        }


@dataclass(frozen=True)
class GRC9GeneratedSeed:
    seed_family: str
    seed_name: str
    control_role: str
    lane_name: str
    profile: str
    generator_version: str
    seed_parameters: Mapping[str, Any]
    expected_runtime_config: Mapping[str, Any]
    graph_preconditions: Mapping[str, Any]
    predicted_signatures: tuple[Mapping[str, Any], ...]
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
            "graph_preconditions": _json_safe(self.graph_preconditions),
            "predicted_signatures": [_json_safe(item) for item in self.predicted_signatures],
            "state_payload": _json_safe(self.state_payload),
            "negative_control_of": self.negative_control_of,
            "perturbation_of": self.perturbation_of,
        }


def _base_runtime_config(parameters: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "dt": 0.1,
        "evolution": {
            "D_eff_target": int(parameters.get("target_effective_degree", parameters.get("D_eff", 30))),
            "w_bond": float(parameters.get("bond_weight", 1.0)),
            "lambda_birth": _config_float(
                parameters.get("birth_lambda", parameters.get("lambda_birth", 1.0)),
                1.0,
                field_name="lambda_birth",
            ),
            "alpha_seed": float(parameters.get("alpha_seed", 0.25)),
            "rng_seed": int(parameters.get("rng_seed", 0)),
            "eps_spark": float(parameters.get("spark_threshold", 0.01)),
            "spark_threshold_mode": str(parameters.get("spark_threshold_mode", "absolute")),
            "adiabatic_expansion_substeps": int(parameters.get("expansion_substeps", 1)),
            "identity_fission_persistence_delta": int(parameters.get("persistence_delta", 5)),
            "identity_fission_min_basin_mass": float(parameters.get("minimum_basin_mass", 0.0)),
            "scale_weighted_abundance_gamma": float(parameters.get("scale_weighted_abundance_gamma", 1.0)),
        },
        "constitutive_semantic_modes": {
            "frame_mode": "fixed_port_chart",
            "curvature_backend": "none",
            "boundary_mode": "prune",
            "expansion_distribution_mode": str(parameters.get("expansion_distribution_mode", "equal")),
            "edge_label_selection": "all",
        },
    }


def _resolved_node_count(family: GRC9SeedFamilySpec, parameters: Mapping[str, Any]) -> int:
    if "node_count" in parameters and isinstance(parameters["node_count"], int):
        return _positive_int(parameters["node_count"], field_name="node_count")
    if isinstance(family.node_count, int):
        return family.node_count
    if family.seed_family in {"expansion_module", "column_reassignment"}:
        return 10
    if family.seed_family == "fission_candidate":
        return 7
    return 6


def _control_by_role(
    family: GRC9SeedFamilySpec,
    control_role: str,
) -> GRC9SeedControlSpec:
    for control in (*family.positive_controls, *family.negative_controls):
        if control.control_role == control_role:
            return control
    raise ValueError(
        f"seed family {family.seed_family!r} does not define control role {control_role!r}"
    )


def _default_negative_parent(
    family: GRC9SeedFamilySpec,
    control_role: str,
) -> str | None:
    if control_role != "negative_control":
        return None
    parent_controls = family.positive_controls or tuple(
        control for control in (*family.positive_controls, *family.negative_controls)
        if control.control_role != "negative_control"
    )
    if not parent_controls:
        return None
    return generated_lane_name(family.seed_family, parent_controls[0].control_role)


def _seed_parameters(
    family: GRC9SeedFamilySpec,
    control: GRC9SeedControlSpec,
    parameter_overrides: Mapping[str, Any] | None,
) -> dict[str, Any]:
    parameters: dict[str, Any] = {
        "node_count": family.node_count,
        "row_column_occupancy": dict(family.row_column_occupancy),
        "active_inactive_port_pattern": dict(family.active_inactive_port_pattern),
        "conductance_assignment": dict(family.conductance_assignment),
        "coherence_placement": dict(family.coherence_placement),
        "boundary_edge_pattern": dict(family.boundary_edge_pattern),
        "expected_lifecycle": list(family.expected_lifecycle),
        "target_effective_degree": 30,
        "coherence_transfer_ratios": [1 / 3, 1 / 3, 1 / 3],
        "bond_weight": 1.0,
        "spark_threshold": 0.01,
        "spark_threshold_mode": "absolute",
        "birth_rule": "outward_flux_pressure",
        "birth_lambda": 1.0,
        "budget_preservation_policy": "uniform_shift",
        "budget_error_magnitude": 0.25,
        "scale_weighted_abundance_gamma": 1.0,
        "persistence_delta": 5,
        "minimum_basin_mass": 0.0,
    }
    parameters.update(dict(control.parameter_overrides))
    parameters.update(dict(parameter_overrides or {}))
    parameters["resolved_node_count"] = _resolved_node_count(family, parameters)
    return parameters


def _star_seed(
    *,
    node_count: int,
    active_degree: int,
    conductance_by_port: Mapping[int, float],
    parent_coherence: float,
    neighbor_coherence: float,
    flux_by_port: Mapping[int, float] | None = None,
) -> tuple[_GraphBuilder, dict[int, float]]:
    graph = _GraphBuilder(node_count)
    active_degree = max(0, min(active_degree, node_count - 1, 9))
    flux_by_port = flux_by_port or {}
    for port in range(1, active_degree + 1):
        graph.connect(
            0,
            port,
            port,
            1,
            conductance=float(conductance_by_port.get(port, 1.0)),
            flux_uv=float(flux_by_port.get(port, 0.0)),
            role="parent_boundary",
        )
    coherence = {node_id: float(neighbor_coherence) for node_id in range(node_count)}
    coherence[0] = float(parent_coherence)
    return graph, coherence


def _spark_like_seed(parameters: Mapping[str, Any]) -> tuple[_GraphBuilder, dict[int, float], dict[str, Any]]:
    active_degree = int(parameters.get("active_degree", 9))
    center_column_weight = 6.0 if active_degree >= 9 else 1.0
    conductance_by_port = {
        port: center_column_weight if port in (2, 5, 8) else 1.5
        for port in range(1, 10)
    }
    graph, coherence = _star_seed(
        node_count=int(parameters["resolved_node_count"]),
        active_degree=active_degree,
        conductance_by_port=conductance_by_port,
        parent_coherence=9.0,
        neighbor_coherence=1.0,
    )
    return graph, coherence, {"sink_set": [0], "basins": {"0": list(range(len(coherence)))}}


def _column_diagnostic_seed(parameters: Mapping[str, Any]) -> tuple[_GraphBuilder, dict[int, float], dict[str, Any]]:
    graph = _GraphBuilder(int(parameters["resolved_node_count"]))
    proxy_column = parameters.get("proxy_column", 2)
    parent_coherence = 5.0
    if proxy_column is None:
        coherence_by_port = {port: 1.0 for port in range(1, 10)}
        conductance_by_port = {port: 1.5 for port in range(1, 10)}
    else:
        # Runtime H_s^(b) sums conductance-weighted coherence differences
        # within each column. Column 2 is constructed as -1 + 0 + 1 = 0.
        coherence_by_port = {
            1: 1.0,
            2: 4.0,
            3: 8.0,
            4: 1.0,
            5: 5.0,
            6: 8.0,
            7: 1.0,
            8: 6.0,
            9: 8.0,
        }
        conductance_by_port = {port: 1.0 for port in range(1, 10)}
    for port in range(1, 10):
        graph.connect(
            0,
            port,
            port,
            1,
            conductance=float(conductance_by_port[port]),
            role="column_diagnostic_proxy" if port in (2, 5, 8) else "column_diagnostic_control",
        )
    coherence = {0: parent_coherence}
    coherence.update(
        {port: float(coherence_by_port[port]) for port in range(1, graph.node_count)}
    )
    return graph, coherence, {"sink_set": [0], "basins": {"0": list(range(graph.node_count))}}


def _growth_seed(parameters: Mapping[str, Any]) -> tuple[_GraphBuilder, dict[int, float], dict[str, Any]]:
    active_degree = 4
    outward_flux = 4.0 if parameters.get("outward_flux", "high") != "low" else 0.05
    conductance = 4.0 if outward_flux > 1.0 else 0.25
    graph, coherence = _star_seed(
        node_count=int(parameters["resolved_node_count"]),
        active_degree=active_degree,
        conductance_by_port={port: conductance for port in range(1, active_degree + 1)},
        parent_coherence=6.0,
        neighbor_coherence=1.0,
        flux_by_port={1: outward_flux},
    )
    return graph, coherence, {"sink_set": [0], "basins": {"0": list(range(len(coherence)))}}


def _row_tensor_seed(parameters: Mapping[str, Any]) -> tuple[_GraphBuilder, dict[int, float], dict[str, Any]]:
    row_bias = int(parameters.get("row_bias", 1))
    weights = {1: 5.0, 2: 4.0, 3: 3.0, 4: 1.5, 5: 1.25, 6: 1.0}
    if row_bias == 0:
        weights = {port: 2.0 for port in weights}
    graph, coherence = _star_seed(
        node_count=int(parameters["resolved_node_count"]),
        active_degree=6,
        conductance_by_port=weights,
        parent_coherence=7.0,
        neighbor_coherence=2.0,
    )
    return graph, coherence, {"sink_set": [0], "basins": {"0": list(range(len(coherence)))}}


def _coarse_seed(parameters: Mapping[str, Any]) -> tuple[_GraphBuilder, dict[int, float], dict[str, Any]]:
    graph = _GraphBuilder(int(parameters["resolved_node_count"]))
    graph.connect(0, 1, 1, 1, conductance=3.0)
    graph.connect(1, 2, 2, 1, conductance=0.2)
    graph.connect(2, 2, 3, 1, conductance=0.2)
    graph.connect(3, 2, 4, 1, conductance=3.0)
    graph.connect(0, 2, 4, 2, conductance=1.0)
    if parameters.get("profile") == "dense":
        coherence = {node_id: 2.0 for node_id in range(graph.node_count)}
    else:
        coherence = {0: 5.0, 1: 0.1, 2: 0.1, 3: 0.1, 4: 4.7}
    return graph, coherence, {"sink_set": [0, 4], "basins": {"0": [0, 1, 2], "4": [3, 4]}}


def _budget_seed(parameters: Mapping[str, Any]) -> tuple[_GraphBuilder, dict[int, float], dict[str, Any]]:
    graph = _GraphBuilder(int(parameters["resolved_node_count"]))
    for node_id in range(graph.node_count - 1):
        left_port = 2 if node_id > 0 else 1
        graph.connect(node_id, left_port, node_id + 1, 1, conductance=1.0)
    coherence = {node_id: 1.0 for node_id in range(graph.node_count)}
    budget_current = float(sum(coherence.values()))
    error = parameters.get("budget_error", "small_positive")
    magnitude = _config_float(
        parameters.get("budget_error_magnitude", 0.25),
        0.25,
        field_name="budget_error_magnitude",
    )
    budget_target = budget_current if error == 0 else budget_current - magnitude
    return graph, coherence, {"budget_target": budget_target}


def _transport_seed(parameters: Mapping[str, Any]) -> tuple[_GraphBuilder, dict[int, float], dict[str, Any]]:
    graph = _GraphBuilder(int(parameters["resolved_node_count"]))
    high_path = parameters.get("high_path", "long")
    short_weight = 1.0 if high_path == "long" else 2.0
    long_weight = 5.0 if high_path == "long" else 2.0
    graph.connect(0, 1, 1, 1, conductance=short_weight, role="short_path")
    graph.connect(1, 2, 7, 1, conductance=short_weight, role="short_path")
    graph.connect(0, 2, 2, 1, conductance=long_weight, role="long_path")
    graph.connect(2, 2, 3, 1, conductance=long_weight, role="long_path")
    graph.connect(3, 2, 4, 1, conductance=long_weight, role="long_path")
    graph.connect(4, 2, 7, 2, conductance=long_weight, role="long_path")
    coherence = {node_id: 2.0 for node_id in range(graph.node_count)}
    coherence[0] = 8.0
    coherence[7] = 0.5
    return graph, coherence, {"sink_set": [7], "basins": {"7": list(range(graph.node_count))}}


def _fission_seed(parameters: Mapping[str, Any]) -> tuple[_GraphBuilder, dict[int, float], dict[str, Any]]:
    graph = _GraphBuilder(int(parameters["resolved_node_count"]))
    bridge = 4.0 if parameters.get("bridge_conductance") == "high" else 0.2
    graph.connect(0, 1, 1, 1, conductance=1.0, role="core_to_pole")
    graph.connect(0, 2, 2, 1, conductance=1.0, role="core_to_pole")
    graph.connect(1, 2, 3, 1, conductance=bridge, role="bridge")
    graph.connect(3, 2, 2, 2, conductance=bridge, role="bridge")
    graph.connect(1, 3, 4, 1, conductance=5.0, role="pole_attractor")
    graph.connect(2, 3, 5, 1, conductance=5.0, role="pole_attractor")
    graph.connect(0, 3, 6, 1, conductance=0.5, role="module_boundary")
    coherence = {0: 1.0, 1: 3.0, 2: 3.0, 3: 0.5, 4: 7.0, 5: 7.0, 6: 0.5}
    return graph, coherence, {"sink_set": [4, 5], "basins": {"4": [1, 4], "5": [2, 5]}}


def _generic_seed(parameters: Mapping[str, Any]) -> tuple[_GraphBuilder, dict[int, float], dict[str, Any]]:
    graph, coherence = _star_seed(
        node_count=int(parameters["resolved_node_count"]),
        active_degree=min(6, int(parameters["resolved_node_count"]) - 1),
        conductance_by_port={port: 2.0 for port in range(1, 10)},
        parent_coherence=5.0,
        neighbor_coherence=1.0,
    )
    return graph, coherence, {"sink_set": [0], "basins": {"0": list(range(len(coherence)))}}


def _build_graph(
    family: GRC9SeedFamilySpec,
    parameters: Mapping[str, Any],
) -> tuple[_GraphBuilder, dict[int, float], dict[str, Any]]:
    if family.seed_family in {"spark_precursor", "expansion_module", "column_reassignment"}:
        return _spark_like_seed(parameters)
    if family.seed_family == "column_diagnostic_regime":
        return _column_diagnostic_seed(parameters)
    if family.seed_family == "growth_pressure":
        return _growth_seed(parameters)
    if family.seed_family == "row_tensor_regime":
        return _row_tensor_seed(parameters)
    if family.seed_family == "coarse_profile_sparsity":
        return _coarse_seed(parameters)
    if family.seed_family == "budget_correction":
        return _budget_seed(parameters)
    if family.seed_family == "quiescent_basin":
        port_pattern = parameters.get("active_inactive_port_pattern", {})
        active_ports = (
            port_pattern.get("active_ports", ())
            if isinstance(port_pattern, Mapping)
            else ()
        )
        active_degree = len(active_ports) if isinstance(active_ports, list) else 5
        graph, coherence = _star_seed(
            node_count=int(parameters["resolved_node_count"]),
            active_degree=active_degree,
            conductance_by_port={port: 1.0 for port in range(1, 6)},
            parent_coherence=3.0,
            neighbor_coherence=2.5,
        )
        return graph, coherence, {"sink_set": [0], "basins": {"0": list(range(len(coherence)))}}
    if family.seed_family == "transport_pathway":
        return _transport_seed(parameters)
    if family.seed_family == "fission_candidate":
        return _fission_seed(parameters)
    return _generic_seed(parameters)


def _state_payload(
    *,
    graph: _GraphBuilder,
    coherence: Mapping[int, float],
    extras: Mapping[str, Any],
    seed_name: str,
    parameters: Mapping[str, Any],
) -> dict[str, Any]:
    budget_target = float(extras.get("budget_target", sum(coherence.values())))
    cached_quantities = {
        "discovery_seed_name": seed_name,
        "discovery_seed_parameters": _json_safe(parameters),
    }
    cached_quantities.update(dict(extras.get("cached_quantities", {})))
    return {
        "topology": graph.topology(),
        "node_coherence": {
            str(node_id): float(coherence.get(node_id, 0.0))
            for node_id in range(graph.node_count)
        },
        "port_edges": graph.port_edges,
        "geometric_length": {str(edge_id): 1.0 for edge_id in range(len(graph.edges))},
        "temporal_delay": {str(edge_id): 1.0 for edge_id in range(len(graph.edges))},
        "flux_coupling": {str(edge_id): 0.0 for edge_id in range(len(graph.edges))},
        "potential": {str(node_id): 0.0 for node_id in range(graph.node_count)},
        "sink_set": list(extras.get("sink_set", [])),
        "basins": dict(extras.get("basins", {})),
        "expansion_registry": dict(extras.get("expansion_registry", {})),
        "prev_column_diagnostic": dict(extras.get("prev_column_diagnostic", {})),
        "budget_target": budget_target,
        "coarse_cache": dict(extras.get("coarse_cache", {})),
        "cached_quantities": cached_quantities,
    }


def _validate_seed(seed: GRC9GeneratedSeed) -> None:
    GRC9.from_state(state=dict(seed.state_payload), params=dict(seed.expected_runtime_config))


def generate_grc9_seed(
    seed_family: str,
    control_role: str = "positive_control",
    *,
    parameter_overrides: Mapping[str, Any] | None = None,
    seed_name: str | None = None,
    catalog: GRC9HypothesisCatalog | None = None,
    validate: bool = True,
    negative_control_of: str | None = None,
    perturbation_of: str | None = None,
    lane_name_override: str | None = None,
) -> GRC9GeneratedSeed:
    """Generate one deterministic GRC9 constructor payload from a seed family."""

    catalog = catalog or default_grc9_hypothesis_catalog()
    family_by_name = {item.seed_family: item for item in catalog.seed_families}
    if seed_family not in family_by_name:
        raise ValueError(f"unknown GRC9 seed family {seed_family!r}")
    family = family_by_name[seed_family]
    if family.runtime_status != RUNTIME_TESTABLE or not family.scheduled_for_generation:
        raise ValueError(f"seed family {seed_family!r} is not currently testable")
    control = _control_by_role(family, control_role)
    parameters = _seed_parameters(family, control, parameter_overrides)
    graph, coherence, extras = _build_graph(family, parameters)
    resolved_seed_name = seed_name or control.seed_name
    state_payload = _state_payload(
        graph=graph,
        coherence=coherence,
        extras=extras,
        seed_name=resolved_seed_name,
        parameters=parameters,
    )
    lane_name = lane_name_override or generated_lane_name(seed_family, control_role)
    seed = GRC9GeneratedSeed(
        seed_family=seed_family,
        seed_name=resolved_seed_name,
        control_role=control_role,
        lane_name=lane_name,
        profile=family.profile,
        generator_version=GRC9_SEED_GENERATOR_VERSION,
        seed_parameters=parameters,
        expected_runtime_config=_base_runtime_config(parameters),
        graph_preconditions={
            "row_column_occupancy": dict(family.row_column_occupancy),
            "active_inactive_port_pattern": dict(family.active_inactive_port_pattern),
            "conductance_assignment": dict(family.conductance_assignment),
            "coherence_placement": dict(family.coherence_placement),
            "boundary_edge_pattern": dict(family.boundary_edge_pattern),
        },
        predicted_signatures=tuple(
            item.to_mapping() for item in family.predicted_signatures
        ),
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
            "GRC9 seed perturbation deltas currently require numeric base "
            f"parameters; got {value!r}"
        )
    if delta.endswith("%"):
        return float(value) * (1.0 + float(delta[:-1]) / 100.0)
    return float(value) + float(delta)


def generate_grc9_seed_perturbation(
    seed_family: str,
    parameter: str,
    delta: str,
    *,
    parent_control_role: str = "positive_control",
    catalog: GRC9HypothesisCatalog | None = None,
    validate: bool = True,
) -> GRC9GeneratedSeed:
    """Generate one deterministic perturbation lane from a scheduled parent seed."""

    parent = generate_grc9_seed(
        seed_family,
        parent_control_role,
        catalog=catalog,
        validate=validate,
    )
    parameters = dict(parent.seed_parameters)
    if parameter not in parameters:
        raise ValueError(
            f"cannot perturb unknown GRC9 seed parameter {parameter!r} for "
            f"{parent.lane_name!r}"
        )
    parameters[parameter] = _apply_delta(parameters[parameter], delta)
    lane = perturbation_lane_name(seed_family, parent_control_role, parameter, delta)
    return generate_grc9_seed(
        seed_family,
        parent_control_role,
        parameter_overrides={parameter: parameters[parameter]},
        seed_name=lane,
        catalog=catalog,
        validate=validate,
        perturbation_of=parent.lane_name,
        lane_name_override=lane,
    )


def generate_grc9_lifecycle_emitter(
    emitter_name: str,
    *,
    validate: bool = True,
) -> GRC9GeneratedSeed:
    """Generate a theory-first lifecycle emitter for Iteration 5.1."""

    if emitter_name not in GRC9_LIFECYCLE_EMITTER_NAMES:
        raise ValueError(f"unknown GRC9 lifecycle emitter {emitter_name!r}")
    graph, coherence, extras, parameters = _build_lifecycle_emitter(emitter_name)
    runtime_config = _emitter_runtime_config(emitter_name, parameters)
    state_payload = _state_payload(
        graph=graph,
        coherence=coherence,
        extras=extras,
        seed_name=emitter_name,
        parameters=parameters,
    )
    seed = GRC9GeneratedSeed(
        seed_family=emitter_name,
        seed_name=emitter_name,
        control_role="positive_control",
        lane_name=emitter_name,
        profile=GRC9_LIFECYCLE_EMITTER_REPAIR_PROFILE,
        generator_version=GRC9_SEED_GENERATOR_VERSION,
        seed_parameters=parameters,
        expected_runtime_config=runtime_config,
        graph_preconditions=dict(parameters["graph_preconditions"]),
        predicted_signatures=tuple(parameters["predicted_signatures"]),
        state_payload=state_payload,
    )
    if validate:
        _validate_seed(seed)
    return seed


def generate_grc9_lifecycle_emitter_perturbation(
    perturbation_name: str,
    *,
    validate: bool = True,
) -> GRC9GeneratedSeed:
    """Generate one named perturbation around a repaired lifecycle emitter."""

    if perturbation_name not in _EMITTER_PERTURBATION_SPECS:
        raise ValueError(f"unknown GRC9 lifecycle emitter perturbation {perturbation_name!r}")
    parent_name, runtime_overrides, expectation = _EMITTER_PERTURBATION_SPECS[
        perturbation_name
    ]
    parent = generate_grc9_lifecycle_emitter(parent_name, validate=validate)
    runtime_config = _json_safe(parent.expected_runtime_config)
    runtime_config["evolution"] = dict(runtime_config["evolution"])
    runtime_config["evolution"].update(dict(runtime_overrides))
    seed_parameters = dict(parent.seed_parameters)
    seed_parameters["perturbation_name"] = perturbation_name
    seed_parameters["perturbation_of"] = parent_name
    seed_parameters["runtime_overrides"] = dict(runtime_overrides)
    seed_parameters["expected_perturbation_effect"] = expectation
    seed = GRC9GeneratedSeed(
        seed_family=parent.seed_family,
        seed_name=perturbation_name,
        control_role="perturbation_control",
        lane_name=perturbation_name,
        profile=parent.profile,
        generator_version=parent.generator_version,
        seed_parameters=seed_parameters,
        expected_runtime_config=runtime_config,
        graph_preconditions=parent.graph_preconditions,
        predicted_signatures=parent.predicted_signatures,
        state_payload=parent.state_payload,
        perturbation_of=parent.lane_name,
    )
    if validate:
        _validate_seed(seed)
    return seed


def generate_grc9_lifecycle_combo(
    combo_name: str,
    *,
    validate: bool = True,
) -> GRC9GeneratedSeed:
    """Generate one composed lifecycle example for selector validation."""

    if combo_name not in GRC9_LIFECYCLE_COMBO_NAMES:
        raise ValueError(f"unknown GRC9 lifecycle combo {combo_name!r}")
    graph, coherence, extras, parameters = _build_lifecycle_combo(combo_name)
    runtime_config = _combo_runtime_config(combo_name)
    state_payload = _state_payload(
        graph=graph,
        coherence=coherence,
        extras=extras,
        seed_name=combo_name,
        parameters=parameters,
    )
    seed = GRC9GeneratedSeed(
        seed_family=combo_name,
        seed_name=combo_name,
        control_role="combo_control",
        lane_name=combo_name,
        profile=GRC9_LIFECYCLE_COMBO_PROFILE,
        generator_version=GRC9_SEED_GENERATOR_VERSION,
        seed_parameters=parameters,
        expected_runtime_config=runtime_config,
        graph_preconditions=dict(parameters["graph_preconditions"]),
        predicted_signatures=tuple(parameters["predicted_signatures"]),
        state_payload=state_payload,
    )
    if validate:
        _validate_seed(seed)
    return seed


def generate_grc9_targeted_diagnostic_fixture(
    fixture_name: str,
    *,
    validate: bool = True,
) -> GRC9GeneratedSeed:
    """Generate one targeted diagnostic fixture for selector ambiguity reduction."""

    if fixture_name not in GRC9_TARGETED_DIAGNOSTIC_NAMES:
        raise ValueError(f"unknown GRC9 targeted diagnostic fixture {fixture_name!r}")
    graph, coherence, extras, parameters = _build_targeted_diagnostic_fixture(
        fixture_name
    )
    runtime_config = _targeted_diagnostic_runtime_config(fixture_name)
    state_payload = _state_payload(
        graph=graph,
        coherence=coherence,
        extras=extras,
        seed_name=fixture_name,
        parameters=parameters,
    )
    seed = GRC9GeneratedSeed(
        seed_family=fixture_name,
        seed_name=fixture_name,
        control_role="diagnostic_control",
        lane_name=fixture_name,
        profile=GRC9_TARGETED_DIAGNOSTIC_PROFILE,
        generator_version=GRC9_SEED_GENERATOR_VERSION,
        seed_parameters=parameters,
        expected_runtime_config=runtime_config,
        graph_preconditions=dict(parameters["graph_preconditions"]),
        predicted_signatures=tuple(parameters["predicted_signatures"]),
        state_payload=state_payload,
    )
    if validate:
        _validate_seed(seed)
    return seed


def generate_grc9_complex_event_stability_fixture(
    fixture_name: str,
    *,
    validate: bool = True,
) -> GRC9GeneratedSeed:
    """Generate one all-event complex graph fixture for Iteration 6.3."""

    if fixture_name not in GRC9_COMPLEX_EVENT_STABILITY_NAMES:
        raise ValueError(f"unknown GRC9 complex event stability fixture {fixture_name!r}")
    graph, coherence, extras, parameters = _build_complex_event_stability_fixture(
        fixture_name
    )
    runtime_config = _complex_event_runtime_config(fixture_name)
    state_payload = _state_payload(
        graph=graph,
        coherence=coherence,
        extras=extras,
        seed_name=fixture_name,
        parameters=parameters,
    )
    seed = GRC9GeneratedSeed(
        seed_family=fixture_name,
        seed_name=fixture_name,
        control_role="complex_control",
        lane_name=fixture_name,
        profile=GRC9_COMPLEX_EVENT_STABILITY_PROFILE,
        generator_version=GRC9_SEED_GENERATOR_VERSION,
        seed_parameters=parameters,
        expected_runtime_config=runtime_config,
        graph_preconditions=dict(parameters["graph_preconditions"]),
        predicted_signatures=tuple(parameters["predicted_signatures"]),
        state_payload=state_payload,
        perturbation_of=(
            "all_events_complex_control"
            if fixture_name != "all_events_complex_control"
            else None
        ),
    )
    if validate:
        _validate_seed(seed)
    return seed


def generate_grc9_corrected_growth_elementary_fixture(
    fixture_name: str,
    *,
    validate: bool = True,
) -> GRC9GeneratedSeed:
    """Generate one elementary corrected front-capacity growth fixture."""

    if fixture_name not in GRC9_CORRECTED_GROWTH_ELEMENTARY_NAMES:
        raise ValueError(f"unknown GRC9 corrected growth fixture {fixture_name!r}")
    graph, coherence, extras, parameters = _build_corrected_growth_elementary_fixture(
        fixture_name
    )
    runtime_config = _corrected_growth_runtime_config(fixture_name)
    state_payload = _state_payload(
        graph=graph,
        coherence=coherence,
        extras=extras,
        seed_name=fixture_name,
        parameters=parameters,
    )
    seed = GRC9GeneratedSeed(
        seed_family=fixture_name,
        seed_name=fixture_name,
        control_role="growth_correction_control",
        lane_name=fixture_name,
        profile=GRC9_CORRECTED_GROWTH_ELEMENTARY_PROFILE,
        generator_version=GRC9_SEED_GENERATOR_VERSION,
        seed_parameters=parameters,
        expected_runtime_config=runtime_config,
        graph_preconditions=dict(parameters["graph_preconditions"]),
        predicted_signatures=tuple(parameters["predicted_signatures"]),
        state_payload=state_payload,
        negative_control_of=(
            (
                "front_capacity_growth_pressure_boundary_positive_control"
                if fixture_name
                == "front_capacity_growth_pressure_boundary_zero_pressure_control"
                else "front_capacity_growth_positive_control"
            )
            if fixture_name
            not in {
                "front_capacity_growth_positive_control",
                "front_capacity_growth_pressure_boundary_positive_control",
            }
            else None
        ),
    )
    if validate:
        _validate_seed(seed)
    return seed


def generate_grc9_corrected_growth_combo_fixture(
    fixture_name: str,
    *,
    validate: bool = True,
) -> GRC9GeneratedSeed:
    """Generate one corrected front-capacity growth composition fixture."""

    if fixture_name not in GRC9_CORRECTED_GROWTH_COMBO_NAMES:
        raise ValueError(f"unknown GRC9 corrected growth combo {fixture_name!r}")
    graph, coherence, extras, parameters = _build_corrected_growth_combo_fixture(
        fixture_name
    )
    runtime_config = _corrected_growth_combo_runtime_config(fixture_name)
    state_payload = _state_payload(
        graph=graph,
        coherence=coherence,
        extras=extras,
        seed_name=fixture_name,
        parameters=parameters,
    )
    seed = GRC9GeneratedSeed(
        seed_family=fixture_name,
        seed_name=fixture_name,
        control_role="growth_correction_combo",
        lane_name=fixture_name,
        profile=GRC9_CORRECTED_GROWTH_COMBO_PROFILE,
        generator_version=GRC9_SEED_GENERATOR_VERSION,
        seed_parameters=parameters,
        expected_runtime_config=runtime_config,
        graph_preconditions=dict(parameters["graph_preconditions"]),
        predicted_signatures=tuple(parameters["predicted_signatures"]),
        state_payload=state_payload,
    )
    if validate:
        _validate_seed(seed)
    return seed


def generate_grc9_corrected_growth_complex_fixture(
    fixture_name: str,
    *,
    validate: bool = True,
) -> GRC9GeneratedSeed:
    """Generate one corrected front-capacity all-event complex fixture."""

    if fixture_name not in GRC9_CORRECTED_GROWTH_COMPLEX_NAMES:
        raise ValueError(f"unknown GRC9 corrected growth complex {fixture_name!r}")
    graph, coherence, extras, parameters = _build_corrected_growth_complex_fixture(
        fixture_name
    )
    runtime_config = _corrected_growth_complex_runtime_config(fixture_name)
    state_payload = _state_payload(
        graph=graph,
        coherence=coherence,
        extras=extras,
        seed_name=fixture_name,
        parameters=parameters,
    )
    seed = GRC9GeneratedSeed(
        seed_family=fixture_name,
        seed_name=fixture_name,
        control_role="growth_correction_complex",
        lane_name=fixture_name,
        profile=GRC9_CORRECTED_GROWTH_COMPLEX_PROFILE,
        generator_version=GRC9_SEED_GENERATOR_VERSION,
        seed_parameters=parameters,
        expected_runtime_config=runtime_config,
        graph_preconditions=dict(parameters["graph_preconditions"]),
        predicted_signatures=tuple(parameters["predicted_signatures"]),
        state_payload=state_payload,
        perturbation_of=(
            "corrected_all_events_complex_control"
            if fixture_name != "corrected_all_events_complex_control"
            else None
        ),
    )
    if validate:
        _validate_seed(seed)
    return seed


def _build_lifecycle_emitter(
    emitter_name: str,
) -> tuple[_GraphBuilder, dict[int, float], dict[str, Any], dict[str, Any]]:
    if emitter_name in {"spark_column_proxy_emitter", "spark_to_expansion_emitter"}:
        return _spark_column_proxy_emitter(emitter_name)
    if emitter_name == "spark_instability_emitter":
        return _spark_instability_emitter()
    if emitter_name == "growth_pressure_emitter":
        return _growth_pressure_emitter()
    if emitter_name == "post_expansion_fission_emitter":
        return _post_expansion_fission_emitter()
    raise ValueError(f"unknown GRC9 lifecycle emitter {emitter_name!r}")


def _build_lifecycle_combo(
    combo_name: str,
) -> tuple[_GraphBuilder, dict[int, float], dict[str, Any], dict[str, Any]]:
    if combo_name == "spark_growth_combo":
        graph = _GraphBuilder(13)
        coherence: dict[int, float] = {}
        _add_column_proxy_component(graph, coherence, offset=0)
        _add_growth_component(graph, coherence, offset=10)
        _connect_lifecycle_combo_components(graph, combo_name)
        parameters = _combo_parameters(
            combo_name,
            components=("spark_column_proxy", "growth_pressure"),
            graph_preconditions={
                "component_layout": "low-conductance bridged spark and growth regions",
                "bridge_edges": ("node 1 to node 11",),
                "spark_sink": 0,
                "growth_parent": 10,
            },
            predicted_signatures=(
                "event_counts.spark >= 1",
                "event_counts.expansion >= 1",
                "event_counts.growth >= 1",
                "identity_fission_confirmed_count >= 1",
            ),
        )
        return graph, coherence, {"sink_set": [0], "basins": {"0": list(range(10))}}, parameters
    if combo_name == "dual_spark_combo":
        graph = _GraphBuilder(47)
        coherence = {}
        _add_column_proxy_component(graph, coherence, offset=0)
        _add_instability_component(graph, coherence, offset=10)
        _connect_lifecycle_combo_components(graph, combo_name)
        parameters = _combo_parameters(
            combo_name,
            components=("spark_column_proxy", "spark_instability"),
            graph_preconditions={
                "component_layout": "low-conductance bridged saturated sink regions",
                "bridge_edges": ("node 1 to node 11",),
                "column_proxy_sink": 0,
                "instability_sink": 10,
            },
            predicted_signatures=(
                "event_counts.spark >= 2",
                "event_counts.expansion >= 2",
                "spark_kinds include saturation_column_proxy and saturation_instability",
                "identity_fission_confirmed_count >= 1",
            ),
        )
        return graph, coherence, {"sink_set": [0, 10], "basins": {"0": list(range(10)), "10": list(range(10, 47))}}, parameters
    if combo_name == "spark_fission_combo":
        graph = _GraphBuilder(15)
        coherence = {}
        _add_column_proxy_component(graph, coherence, offset=0)
        extras = _add_fission_component(graph, coherence, offset=10)
        _connect_lifecycle_combo_components(graph, combo_name)
        extras["sink_set"] = [0, 11, 12]
        extras["basins"] = {
            "0": list(range(10)),
            "11": [11, 13],
            "12": [12, 14],
        }
        parameters = _combo_parameters(
            combo_name,
            components=("spark_column_proxy", "post_expansion_fission"),
            graph_preconditions={
                "component_layout": "low-conductance bridged spark region and pre-registered fission module",
                "bridge_edges": ("node 1 to node 10",),
                "spark_sink": 0,
                "fission_module_offset": 10,
            },
            predicted_signatures=(
                "event_counts.spark >= 1",
                "event_counts.expansion >= 1",
                "identity_fission_confirmed_count >= 1",
            ),
        )
        return graph, coherence, extras, parameters
    if combo_name == "growth_fission_combo":
        graph = _GraphBuilder(8)
        coherence = {}
        _add_growth_component(graph, coherence, offset=0)
        extras = _add_fission_component(graph, coherence, offset=3)
        _connect_lifecycle_combo_components(graph, combo_name)
        extras["sink_set"] = [4, 5]
        extras["basins"] = {"4": [4, 6], "5": [5, 7]}
        parameters = _combo_parameters(
            combo_name,
            components=("growth_pressure", "post_expansion_fission"),
            graph_preconditions={
                "component_layout": "low-conductance bridged growth region and pre-registered fission module",
                "bridge_edges": ("node 1 to node 3",),
                "growth_parent": 0,
                "fission_module_offset": 3,
            },
            predicted_signatures=(
                "event_counts.growth >= 1",
                "identity_fission_confirmed_count >= 1",
            ),
        )
        return graph, coherence, extras, parameters
    if combo_name == "spark_growth_fission_combo":
        graph = _GraphBuilder(18)
        coherence = {}
        _add_column_proxy_component(graph, coherence, offset=0)
        _add_growth_component(graph, coherence, offset=10)
        extras = _add_fission_component(graph, coherence, offset=13)
        _connect_lifecycle_combo_components(graph, combo_name)
        extras["sink_set"] = [0, 14, 15]
        extras["basins"] = {
            "0": list(range(10)),
            "14": [14, 16],
            "15": [15, 17],
        }
        parameters = _combo_parameters(
            combo_name,
            components=("spark_column_proxy", "growth_pressure", "post_expansion_fission"),
            graph_preconditions={
                "component_layout": (
                    "low-conductance bridged spark, growth, and pre-registered "
                    "fission regions"
                ),
                "bridge_edges": ("node 1 to node 11", "node 11 to node 13"),
                "spark_sink": 0,
                "growth_parent": 10,
                "fission_module_offset": 13,
            },
            predicted_signatures=(
                "event_counts.spark >= 1",
                "event_counts.expansion >= 1",
                "event_counts.growth >= 1",
                "identity_fission_confirmed_count >= 1",
            ),
        )
        return graph, coherence, extras, parameters
    raise ValueError(f"unknown GRC9 lifecycle combo {combo_name!r}")


def _connect_lifecycle_combo_components(graph: _GraphBuilder, combo_name: str) -> None:
    if combo_name == "spark_growth_combo":
        graph.connect(
            1,
            2,
            11,
            2,
            conductance=1.0e-6,
            role="combo_component_bridge_spark_to_growth",
        )
        return
    if combo_name == "dual_spark_combo":
        graph.connect(
            1,
            2,
            11,
            5,
            conductance=1.0e-6,
            role="combo_component_bridge_column_proxy_to_instability",
        )
        return
    if combo_name == "spark_fission_combo":
        graph.connect(
            1,
            2,
            10,
            3,
            conductance=1.0e-6,
            role="combo_component_bridge_spark_to_fission",
        )
        return
    if combo_name == "growth_fission_combo":
        graph.connect(
            1,
            2,
            3,
            3,
            conductance=1.0e-6,
            role="combo_component_bridge_growth_to_fission",
        )
        return
    if combo_name == "spark_growth_fission_combo":
        graph.connect(
            1,
            2,
            11,
            2,
            conductance=1.0e-6,
            role="combo_component_bridge_spark_to_growth",
        )
        graph.connect(
            11,
            3,
            13,
            3,
            conductance=1.0e-6,
            role="combo_component_bridge_growth_to_fission",
        )
        return
    raise ValueError(f"unknown GRC9 lifecycle combo {combo_name!r}")


def _build_targeted_diagnostic_fixture(
    fixture_name: str,
) -> tuple[_GraphBuilder, dict[int, float], dict[str, Any], dict[str, Any]]:
    if fixture_name == "row_tensor_strong_anisotropy_control":
        graph = _GraphBuilder(7)
        for port, conductance in {
            1: 12.0,
            2: 10.0,
            3: 8.0,
            4: 0.25,
            5: 0.2,
            6: 0.15,
        }.items():
            graph.connect(0, port, port, 1, conductance=conductance, role="row_tensor_strong_row_bias")
        coherence = {0: 9.0, 1: 1.0, 2: 1.2, 3: 1.4, 4: 8.5, 5: 8.6, 6: 8.7}
        return graph, coherence, {"sink_set": [0], "basins": {"0": list(range(7))}}, _diagnostic_parameters(
            fixture_name,
            graph_preconditions={
                "row_contrast": "row 1 ports carry high conductance and row 2 ports carry low conductance",
                "lifecycle_suppression": "spark and growth predicates disabled",
            },
            predicted_signatures=(
                "final_row_tensor_summary.row_tensor_anisotropy_max is high",
                "final_row_tensor_summary.row_mismatch_hotspots is non-empty",
            ),
        )
    if fixture_name == "row_tensor_flat_control":
        graph = _GraphBuilder(7)
        for port in range(1, 7):
            graph.connect(0, port, port, 1, conductance=1.0, role="row_tensor_flat")
        coherence = {node_id: 5.0 for node_id in range(7)}
        return graph, coherence, {"sink_set": [0], "basins": {"0": list(range(7))}}, _diagnostic_parameters(
            fixture_name,
            graph_preconditions={
                "row_contrast": "uniform conductance and uniform coherence across active ports",
                "lifecycle_suppression": "spark and growth predicates disabled",
            },
            predicted_signatures=(
                "final_row_tensor_summary.row_tensor_anisotropy_max is near zero",
                "final_transport_summary.flux_abs_sum is near zero",
            ),
        )
    if fixture_name == "column_proxy_near_zero_control":
        graph, coherence, extras = _column_diagnostic_seed(
            {"resolved_node_count": 10, "proxy_column": 2}
        )
        return graph, coherence, extras, _diagnostic_parameters(
            fixture_name,
            graph_preconditions={
                "active_degree": 9,
                "column_proxy": "column 2 conductance-weighted diagnostic cancels to zero",
            },
            predicted_signatures=(
                "final_column_diagnostic_summary.column_proxy_candidate_count > 0",
                "final_column_diagnostic_summary.column_diagnostic_min_abs < eps_spark",
            ),
        )
    if fixture_name == "column_proxy_nonzero_control":
        graph = _GraphBuilder(10)
        for port in range(1, 10):
            graph.connect(0, port, port, 1, conductance=1.0, role="column_proxy_nonzero")
        coherence = {0: 10.0}
        coherence.update({port: 1.0 + port for port in range(1, 10)})
        return graph, coherence, {"sink_set": [0], "basins": {"0": list(range(10))}}, _diagnostic_parameters(
            fixture_name,
            graph_preconditions={
                "active_degree": 9,
                "column_proxy": "all three column diagnostics remain above eps_spark",
            },
            predicted_signatures=(
                "final_column_diagnostic_summary.column_proxy_candidate_count == 0",
                "no spark event is emitted by the column proxy gate",
            ),
        )
    if fixture_name in {
        "coarse_cache_populated_sparse_profile_control",
        "coarse_cache_populated_dense_profile_control",
    }:
        sparse = fixture_name == "coarse_cache_populated_sparse_profile_control"
        graph, coherence, extras = _coarse_seed(
            {"resolved_node_count": 5, "profile": "sparse" if sparse else "dense"}
        )
        extras = dict(extras)
        extras["coarse_cache"] = _diagnostic_coarse_cache(sparse=sparse)
        return graph, coherence, extras, _diagnostic_parameters(
            fixture_name,
            graph_preconditions={
                "checkpoint_mode": "zero-step warm-cache fixture",
                "profile_shape": "sparse column totals" if sparse else "dense column totals",
            },
            predicted_signatures=(
                "final_coarse_graining_summary.coarse_cache_state == warm",
                "final_coarse_graining_summary.coarse_fields_list contains conductance",
                (
                    "final_coarse_graining_summary.column_total_sparsity_by_field.conductance is high"
                    if sparse
                    else "final_coarse_graining_summary.column_total_sparsity_by_field.conductance is low"
                ),
            ),
        )
    if fixture_name == "budget_uniform_shift_trigger_control":
        graph, coherence, extras = _budget_seed(
            {
                "resolved_node_count": 5,
                "budget_error": "needs_positive_correction",
                "budget_error_magnitude": 0.5,
            }
        )
        budget_current = float(sum(coherence.values()))
        extras = dict(extras)
        extras["budget_target"] = budget_current + 0.5
        return graph, coherence, extras, _diagnostic_parameters(
            fixture_name,
            graph_preconditions={
                "budget_current": budget_current,
                "budget_target": budget_current + 0.5,
                "correction_direction": "positive uniform shift",
            },
            predicted_signatures=(
                "step budget_correction.last_budget_correction_path == uniform_shift",
                "final_observables.budget_error == 0",
            ),
        )
    if fixture_name == "budget_simplex_projection_trigger_control":
        graph, coherence, extras = _budget_seed(
            {
                "resolved_node_count": 5,
                "budget_error": "needs_negative_correction",
                "budget_error_magnitude": 0.5,
            }
        )
        budget_current = float(sum(coherence.values()))
        extras = dict(extras)
        extras["budget_target"] = budget_current - 0.5
        return graph, coherence, extras, _diagnostic_parameters(
            fixture_name,
            graph_preconditions={
                "budget_current": budget_current,
                "budget_target": budget_current - 0.5,
                "correction_direction": "negative positivity-preserving projection path",
            },
            predicted_signatures=(
                "step budget_correction.last_budget_correction_path is not uniform_shift",
                "final_observables.budget_error == 0",
            ),
        )
    if fixture_name in {
        "transport_short_path_dominant_control",
        "transport_long_path_dominant_control",
    }:
        high_path = (
            "short"
            if fixture_name == "transport_short_path_dominant_control"
            else "long"
        )
        graph, coherence, extras = _transport_seed(
            {"resolved_node_count": 8, "high_path": high_path}
        )
        if high_path == "short":
            coherence[1] = 0.0
        return graph, coherence, extras, _diagnostic_parameters(
            fixture_name,
            graph_preconditions={
                "short_path_edge_ids": [0, 1],
                "long_path_edge_ids": [2, 3, 4, 5],
                "dominant_path": high_path,
            },
            predicted_signatures=(
                f"final_transport_summary.strongest_flux_edges_sample[0] is on {high_path} path",
                "final_transport_summary.flux_abs_sum > 0",
            ),
        )
    raise ValueError(f"unknown GRC9 targeted diagnostic fixture {fixture_name!r}")


def _build_complex_event_stability_fixture(
    fixture_name: str,
) -> tuple[_GraphBuilder, dict[int, float], dict[str, Any], dict[str, Any]]:
    extra_leaf = fixture_name == "all_events_complex_extra_leaf_perturbation_control"
    graph = _GraphBuilder(56 if extra_leaf else 55)
    coherence: dict[int, float] = {}
    _add_column_proxy_component(graph, coherence, offset=0)
    _add_instability_component(graph, coherence, offset=10)
    _add_growth_component(graph, coherence, offset=47)
    extras = _add_fission_component(graph, coherence, offset=50)
    _connect_complex_event_components(graph)
    extras["sink_set"] = [0, 10, 51, 52]
    extras["basins"] = {
        "0": list(range(10)),
        "10": list(range(10, 47)),
        "51": [51, 53],
        "52": [52, 54],
    }
    perturbations: list[str] = []
    if extra_leaf:
        graph.connect(
            47,
            3,
            55,
            1,
            conductance=0.1,
            role="complex_extra_leaf_perturbation",
        )
        coherence[55] = 1.0
        perturbations.append("extra low-conductance leaf on growth component")
    if fixture_name == "all_events_complex_coherence_jitter_perturbation_control":
        coherence[47] = 1.1
        coherence[48] = 9.8
        coherence[49] = 10.2
        coherence[51] = 10.5
        coherence[52] = 9.5
        perturbations.append("small coherence jitter outside spark diagnostic columns")
    if fixture_name == "all_events_complex_soft_threshold_perturbation_control":
        perturbations.append("runtime eps/tau/lambda moved closer to event thresholds")
    if fixture_name == "all_events_complex_high_degree_perturbation_control":
        perturbations.append("runtime D_eff_target increased for larger expansion modules")

    parameters = _complex_event_parameters(
        fixture_name,
        graph_preconditions={
            "component_layout": (
                "low-conductance bridged column-proxy spark, instability spark, "
                "growth, and pre-registered fission regions"
            ),
            "bridge_edges": (
                "node 1 to node 11",
                "node 20 to node 47",
                "node 48 to node 50",
            ),
            "column_proxy_sink": 0,
            "instability_sink": 10,
            "growth_parent": 47,
            "fission_module_offset": 50,
            "perturbations": perturbations,
        },
        predicted_signatures=(
            "event_counts.spark >= 2",
            "event_counts.expansion >= 2",
            "event_counts.growth >= 1",
            "spark_kinds include saturation_column_proxy and saturation_instability",
            "identity_fission_confirmed_count >= 1",
        ),
    )
    return graph, coherence, extras, parameters


def _build_corrected_growth_elementary_fixture(
    fixture_name: str,
) -> tuple[_GraphBuilder, dict[int, float], dict[str, Any], dict[str, Any]]:
    graph = _GraphBuilder(3)
    flux_uv = (
        0.0
        if fixture_name == "front_capacity_growth_pressure_boundary_zero_pressure_control"
        else 3.0
    )
    conductance = (
        0.0
        if fixture_name == "front_capacity_growth_pressure_boundary_zero_pressure_control"
        else 1.0
    )
    graph.connect(
        0,
        1,
        1,
        1,
        conductance=conductance,
        flux_uv=flux_uv,
        role="corrected_front_growth_outward_flux_path",
    )
    graph.connect(
        0,
        2,
        2,
        1,
        conductance=conductance,
        flux_uv=flux_uv,
        role="corrected_front_growth_outward_flux_path",
    )
    coherence = {0: 1.0, 1: 10.0, 2: 10.0}
    extras: dict[str, Any] = {"sink_set": [], "basins": {}}
    front_capacity_source = (
        "pressure_boundary"
        if fixture_name
        in {
            "front_capacity_growth_pressure_boundary_positive_control",
            "front_capacity_growth_pressure_boundary_zero_pressure_control",
        }
        else "spark_refinement_boundary_front"
    )
    capacity_source = {
        "front_capacity_source": front_capacity_source,
        "inactive_parent_port": (
            2
            if fixture_name == "front_capacity_growth_pressure_boundary_zero_pressure_control"
            else 3
        ),
        "source_mechanism": "corrected_grc9_front_capacity_fixture",
    }
    if fixture_name in {
        "front_capacity_growth_positive_control",
        "front_capacity_growth_pressure_boundary_positive_control",
        "front_capacity_growth_zero_birth_control",
        "front_capacity_growth_pressure_boundary_zero_pressure_control",
    }:
        parent_node_id = (
            1
            if fixture_name == "front_capacity_growth_pressure_boundary_zero_pressure_control"
            else 0
        )
        parent_port_id = (
            2
            if fixture_name == "front_capacity_growth_pressure_boundary_zero_pressure_control"
            else 3
        )
        extras["cached_quantities"] = {
            "grc9_front_growth_eligible_ports": {str(parent_node_id): [parent_port_id]},
            "grc9_growth_parent_capacity_sources": {str(parent_node_id): capacity_source},
        }
    elif fixture_name == "front_capacity_growth_closed_front_control":
        extras["cached_quantities"] = {
            "grc9_front_growth_eligible_ports": {"0": [2]},
            "grc9_growth_parent_capacity_sources": {
                "0": {
                    "front_capacity_source": "closed_front_capacity",
                    "inactive_parent_port": 2,
                    "source_mechanism": "corrected_grc9_closed_front_fixture",
                }
            },
        }
    parameters = _corrected_growth_parameters(
        fixture_name,
        graph_preconditions={
            "parent_node_id": (
                1
                if fixture_name
                == "front_capacity_growth_pressure_boundary_zero_pressure_control"
                else 0
            ),
            "occupied_parent_ports": (
                [1]
                if fixture_name
                == "front_capacity_growth_pressure_boundary_zero_pressure_control"
                else [1, 2]
            ),
            "outward_flux_parent": (
                1
                if fixture_name
                == "front_capacity_growth_pressure_boundary_zero_pressure_control"
                else 0
            ),
            "growth_parent_eligibility_mode": "grc9_front_capacity",
            "front_capacity_metadata": bool(extras.get("cached_quantities")),
            "front_capacity_source": (
                capacity_source["front_capacity_source"]
                if fixture_name
                in {
                    "front_capacity_growth_positive_control",
                    "front_capacity_growth_pressure_boundary_positive_control",
                    "front_capacity_growth_zero_birth_control",
                    "front_capacity_growth_pressure_boundary_zero_pressure_control",
                }
                else (
                    "closed_front_capacity"
                    if fixture_name == "front_capacity_growth_closed_front_control"
                    else "none"
                )
            ),
            "eligible_parent_ports": (
                [2]
                if fixture_name
                == "front_capacity_growth_pressure_boundary_zero_pressure_control"
                else [3]
                if fixture_name
                in {
                    "front_capacity_growth_positive_control",
                    "front_capacity_growth_pressure_boundary_positive_control",
                    "front_capacity_growth_zero_birth_control",
                }
                else ([2] if fixture_name == "front_capacity_growth_closed_front_control" else [])
            ),
        },
        predicted_signatures=_corrected_growth_predicted_signatures(fixture_name),
    )
    return graph, coherence, extras, parameters


def _build_corrected_growth_combo_fixture(
    fixture_name: str,
) -> tuple[_GraphBuilder, dict[int, float], dict[str, Any], dict[str, Any]]:
    if fixture_name == "corrected_spark_growth_combo":
        graph = _GraphBuilder(13)
        coherence: dict[int, float] = {}
        _add_column_proxy_component(graph, coherence, offset=0)
        _add_growth_component(graph, coherence, offset=10)
        _connect_lifecycle_combo_components(graph, "spark_growth_combo")
        extras = {
            "sink_set": [0],
            "basins": {"0": list(range(10))},
            "cached_quantities": _front_capacity_cache(
                parent_node_id=10,
                parent_port_id=3,
                source="spark_refinement_boundary_front",
            ),
        }
        parameters = _corrected_growth_combo_parameters(
            fixture_name,
            components=("spark_column_proxy", "front_capacity_growth"),
            graph_preconditions={
                "component_layout": "connected spark region and front-capacity growth region",
                "spark_sink": 0,
                "growth_parent": 10,
                "eligible_growth_port": 3,
                "growth_parent_eligibility_mode": "grc9_front_capacity",
            },
            predicted_signatures=(
                "event_counts.spark >= 1",
                "event_counts.expansion >= 1",
                "event_counts.growth == 1",
                "growth_evidence.front_growth_provenance_present == true",
                "growth_summary.legacy_broad_growth_count == 0",
            ),
        )
        return graph, coherence, extras, parameters
    if fixture_name == "corrected_spark_pressure_boundary_growth_combo":
        graph = _GraphBuilder(13)
        coherence = {}
        _add_column_proxy_component(graph, coherence, offset=0)
        _add_growth_component(graph, coherence, offset=10)
        _connect_lifecycle_combo_components(graph, "spark_growth_combo")
        extras = {
            "sink_set": [0],
            "basins": {"0": list(range(10))},
            "cached_quantities": _front_capacity_cache(
                parent_node_id=10,
                parent_port_id=3,
                source="pressure_boundary",
            ),
        }
        parameters = _corrected_growth_combo_parameters(
            fixture_name,
            components=("spark_column_proxy", "pressure_boundary_growth"),
            graph_preconditions={
                "component_layout": "connected spark region and pressure-boundary growth region",
                "spark_sink": 0,
                "growth_parent": 10,
                "eligible_growth_port": 3,
                "front_capacity_source": "pressure_boundary",
                "growth_parent_eligibility_mode": "grc9_front_capacity",
            },
            predicted_signatures=(
                "event_counts.spark >= 1",
                "event_counts.expansion >= 1",
                "event_counts.growth == 1",
                "growth_evidence.parent_capacity_source == pressure_boundary",
                "growth_summary.pressure_boundary_growth_count == 1",
                "growth_summary.legacy_broad_growth_count == 0",
            ),
        )
        return graph, coherence, extras, parameters
    if fixture_name == "corrected_growth_fission_combo":
        graph = _GraphBuilder(8)
        coherence = {}
        _add_growth_component(graph, coherence, offset=0)
        extras = _add_fission_component(graph, coherence, offset=3)
        _connect_lifecycle_combo_components(graph, "growth_fission_combo")
        extras["sink_set"] = [4, 5]
        extras["basins"] = {"4": [4, 6], "5": [5, 7]}
        extras["cached_quantities"] = _front_capacity_cache(
            parent_node_id=0,
            parent_port_id=3,
            source="spark_refinement_boundary_front",
        )
        parameters = _corrected_growth_combo_parameters(
            fixture_name,
            components=("front_capacity_growth", "post_expansion_fission"),
            graph_preconditions={
                "component_layout": "connected front-capacity growth region and pre-registered fission module",
                "growth_parent": 0,
                "eligible_growth_port": 3,
                "fission_module_offset": 3,
                "growth_parent_eligibility_mode": "grc9_front_capacity",
            },
            predicted_signatures=(
                "event_counts.growth == 1",
                "growth_evidence.front_growth_provenance_present == true",
                "growth_summary.legacy_broad_growth_count == 0",
                "identity_fission_confirmed_count >= 1",
            ),
        )
        return graph, coherence, extras, parameters
    if fixture_name == "corrected_spark_growth_fission_combo":
        graph = _GraphBuilder(18)
        coherence = {}
        _add_column_proxy_component(graph, coherence, offset=0)
        _add_growth_component(graph, coherence, offset=10)
        extras = _add_fission_component(graph, coherence, offset=13)
        coherence[16] = 50.0
        coherence[17] = 50.0
        _connect_lifecycle_combo_components(graph, "spark_growth_fission_combo")
        extras["sink_set"] = [0, 14, 15]
        extras["basins"] = {
            "0": list(range(10)),
            "14": [14, 16],
            "15": [15, 17],
        }
        extras["cached_quantities"] = _front_capacity_cache(
            parent_node_id=10,
            parent_port_id=3,
            source="spark_refinement_boundary_front",
        )
        parameters = _corrected_growth_combo_parameters(
            fixture_name,
            components=(
                "spark_column_proxy",
                "front_capacity_growth",
                "post_expansion_fission",
            ),
            graph_preconditions={
                "component_layout": "connected spark, front-capacity growth, and pre-registered fission regions",
                "spark_sink": 0,
                "growth_parent": 10,
                "eligible_growth_port": 3,
                "fission_module_offset": 13,
                "fission_basin_stabilization": "daughter attractor coherences boosted to preserve Appendix E persistence under corrected growth",
                "growth_parent_eligibility_mode": "grc9_front_capacity",
            },
            predicted_signatures=(
                "event_counts.spark >= 1",
                "event_counts.expansion >= 1",
                "event_counts.growth == 1",
                "growth_evidence.front_growth_provenance_present == true",
                "growth_summary.legacy_broad_growth_count == 0",
                "identity_fission_confirmed_count >= 1",
            ),
        )
        return graph, coherence, extras, parameters
    raise ValueError(f"unknown GRC9 corrected growth combo {fixture_name!r}")


def _build_corrected_growth_complex_fixture(
    fixture_name: str,
) -> tuple[_GraphBuilder, dict[int, float], dict[str, Any], dict[str, Any]]:
    extra_leaf = (
        fixture_name
        == "corrected_all_events_complex_extra_leaf_perturbation_control"
    )
    graph = _GraphBuilder(56 if extra_leaf else 55)
    coherence: dict[int, float] = {}
    _add_column_proxy_component(graph, coherence, offset=0)
    _add_instability_component(graph, coherence, offset=10)
    _add_growth_component(graph, coherence, offset=47)
    extras = _add_fission_component(graph, coherence, offset=50)
    coherence[53] = 50.0
    coherence[54] = 50.0
    _connect_complex_event_components(graph)
    extras["sink_set"] = [0, 10, 51, 52]
    extras["basins"] = {
        "0": list(range(10)),
        "10": list(range(10, 47)),
        "51": [51, 53],
        "52": [52, 54],
    }
    extras["cached_quantities"] = _front_capacity_cache(
        parent_node_id=47,
        parent_port_id=3,
        source="spark_refinement_boundary_front",
    )
    perturbations: list[str] = []
    if extra_leaf:
        graph.connect(
            47,
            5,
            55,
            1,
            conductance=0.1,
            role="corrected_complex_extra_leaf_perturbation",
        )
        coherence[55] = 1.0
        perturbations.append(
            "extra low-conductance leaf on growth component outside eligible front port"
        )
    if fixture_name == "corrected_all_events_complex_coherence_jitter_perturbation_control":
        coherence[47] = 1.1
        coherence[48] = 9.8
        coherence[49] = 10.2
        coherence[51] = 10.5
        coherence[52] = 9.5
        perturbations.append("small coherence jitter outside spark diagnostic columns")
    if fixture_name == "corrected_all_events_complex_soft_threshold_perturbation_control":
        perturbations.append("runtime eps/tau/lambda moved closer to event thresholds")
    if fixture_name == "corrected_all_events_complex_high_degree_perturbation_control":
        perturbations.append("runtime D_eff_target increased for larger expansion modules")

    parameters = _corrected_growth_complex_parameters(
        fixture_name,
        components=(
            "spark_column_proxy",
            "spark_instability",
            "front_capacity_growth",
            "post_expansion_fission",
        ),
        graph_preconditions={
            "component_layout": (
                "low-conductance bridged column-proxy spark, instability spark, "
                "front-capacity growth, and pre-registered fission regions"
            ),
            "bridge_edges": (
                "node 1 to node 11",
                "node 20 to node 47",
                "node 48 to node 50",
            ),
            "column_proxy_sink": 0,
            "instability_sink": 10,
            "growth_parent": 47,
            "eligible_growth_port": 3,
            "fission_module_offset": 50,
            "fission_basin_stabilization": "daughter attractor coherences boosted to preserve Appendix E persistence under corrected growth",
            "growth_parent_eligibility_mode": "grc9_front_capacity",
            "perturbations": perturbations,
        },
        predicted_signatures=(
            "event_counts.spark >= 2",
            "event_counts.expansion >= 2",
            "event_counts.growth == 1",
            "growth_evidence.front_growth_provenance_present == true",
            "growth_summary.legacy_broad_growth_count == 0",
            "spark_kinds include saturation_column_proxy and saturation_instability",
            "identity_fission_confirmed_count >= 1",
        ),
    )
    return graph, coherence, extras, parameters


def _front_capacity_cache(
    *,
    parent_node_id: int,
    parent_port_id: int,
    source: str,
) -> dict[str, Any]:
    return {
        "grc9_front_growth_eligible_ports": {str(parent_node_id): [parent_port_id]},
        "grc9_growth_parent_capacity_sources": {
            str(parent_node_id): {
                "front_capacity_source": source,
                "inactive_parent_port": parent_port_id,
                "source_mechanism": "corrected_grc9_front_capacity_combo_fixture",
            }
        },
    }


def _connect_complex_event_components(graph: _GraphBuilder) -> None:
    graph.connect(
        1,
        2,
        11,
        5,
        conductance=1.0e-6,
        role="complex_component_bridge_column_proxy_to_instability",
    )
    graph.connect(
        20,
        2,
        47,
        4,
        conductance=1.0e-6,
        role="complex_component_bridge_instability_to_growth",
    )
    graph.connect(
        48,
        2,
        50,
        3,
        conductance=1.0e-6,
        role="complex_component_bridge_growth_to_fission",
    )


def _diagnostic_coarse_cache(*, sparse: bool) -> dict[str, Any]:
    if sparse:
        by_node = {
            str(node_id): {
                "column_totals": [9.0, 0.0, 0.0],
                "profiles": [[1.0, 0.0, 0.0], [1 / 3, 1 / 3, 1 / 3], [1 / 3, 1 / 3, 1 / 3]],
            }
            for node_id in range(5)
        }
    else:
        by_node = {
            str(node_id): {
                "column_totals": [3.0, 3.0, 3.0],
                "profiles": [[1 / 3, 1 / 3, 1 / 3], [1 / 3, 1 / 3, 1 / 3], [1 / 3, 1 / 3, 1 / 3]],
            }
            for node_id in range(5)
        }
    return {
        "exact_column_profile:conductance": {
            "mode": "exact_column_profile",
            "field_name": "conductance",
            "by_node": by_node,
        }
    }


def _diagnostic_parameters(
    fixture_name: str,
    *,
    graph_preconditions: Mapping[str, Any],
    predicted_signatures: tuple[str, ...],
) -> dict[str, Any]:
    return {
        "fixture_name": fixture_name,
        "diagnostic_iteration": "I06_2_targeted_diagnostic_fixture_generation",
        "graph_preconditions": dict(graph_preconditions),
        "predicted_signatures": [
            {"field_path": signature, "expected": "match"}
            for signature in predicted_signatures
        ],
    }


def _complex_event_parameters(
    fixture_name: str,
    *,
    graph_preconditions: Mapping[str, Any],
    predicted_signatures: tuple[str, ...],
) -> dict[str, Any]:
    return {
        "fixture_name": fixture_name,
        "complex_iteration": "I06_3_complex_event_stability_probe",
        "graph_preconditions": dict(graph_preconditions),
        "predicted_signatures": [
            {"field_path": signature, "expected": "match"}
            for signature in predicted_signatures
        ],
    }


def _corrected_growth_parameters(
    fixture_name: str,
    *,
    graph_preconditions: Mapping[str, Any],
    predicted_signatures: tuple[str, ...],
) -> dict[str, Any]:
    return {
        "fixture_name": fixture_name,
        "growth_correction_iteration": "I03_1_elementary_corrected_grc9_growth",
        "graph_preconditions": dict(graph_preconditions),
        "predicted_signatures": [
            {"field_path": signature, "expected": "match"}
            for signature in predicted_signatures
        ],
    }


def _corrected_growth_combo_parameters(
    fixture_name: str,
    *,
    components: tuple[str, ...],
    graph_preconditions: Mapping[str, Any],
    predicted_signatures: tuple[str, ...],
) -> dict[str, Any]:
    return {
        "fixture_name": fixture_name,
        "growth_correction_iteration": "I03_2_corrected_grc9_growth_combos",
        "components": list(components),
        "graph_preconditions": dict(graph_preconditions),
        "predicted_signatures": [
            {"field_path": signature, "expected": "match"}
            for signature in predicted_signatures
        ],
    }


def _corrected_growth_complex_parameters(
    fixture_name: str,
    *,
    components: tuple[str, ...],
    graph_preconditions: Mapping[str, Any],
    predicted_signatures: tuple[str, ...],
) -> dict[str, Any]:
    return {
        "fixture_name": fixture_name,
        "growth_correction_iteration": "I03_3_corrected_grc9_full_complex",
        "components": list(components),
        "graph_preconditions": dict(graph_preconditions),
        "predicted_signatures": [
            {"field_path": signature, "expected": "match"}
            for signature in predicted_signatures
        ],
    }


def _corrected_growth_predicted_signatures(fixture_name: str) -> tuple[str, ...]:
    common = (
        "family_extensions.grc9.backend_config.growth_parent_eligibility_mode == grc9_front_capacity",
        "family_extensions.grc9.growth_summary.legacy_broad_growth_count == 0",
    )
    if fixture_name in {
        "front_capacity_growth_positive_control",
        "front_capacity_growth_pressure_boundary_positive_control",
    }:
        pressure_specific = (
            (
                "family_extensions.grc9.growth_evidence.parent_capacity_source == pressure_boundary",
                "family_extensions.grc9.growth_summary.pressure_boundary_growth_count >= 1",
            )
            if fixture_name == "front_capacity_growth_pressure_boundary_positive_control"
            else ()
        )
        return (
            *common,
            "family_extensions.grc9.event_domain == growth",
            "family_extensions.grc9.growth_evidence.front_growth_provenance_present == true",
            "family_extensions.grc9.growth_summary.front_capacity_growth_count >= 1",
            *pressure_specific,
        )
    if fixture_name == "front_capacity_growth_zero_birth_control":
        return (
            *common,
            "no growth event is emitted when lambda_birth == 0",
            "front-capacity metadata is present in cached_quantities",
        )
    if fixture_name == "front_capacity_growth_pressure_boundary_zero_pressure_control":
        return (
            *common,
            "no growth event is emitted when outward flux pressure is zero",
            "pressure-boundary front-capacity metadata is present in cached_quantities",
        )
    if fixture_name == "front_capacity_growth_closed_front_control":
        return (
            *common,
            "no growth event is emitted when the only listed front port is occupied",
            "closed front-capacity metadata is present in cached_quantities",
        )
    return (
        *common,
        "no growth event is emitted without grc9_front_growth_eligible_ports",
    )


def _add_column_proxy_component(
    graph: _GraphBuilder,
    coherence: dict[int, float],
    *,
    offset: int,
) -> None:
    for port in range(1, 10):
        graph.connect(
            offset,
            port,
            offset + port,
            1,
            conductance=1.0,
            role=(
                "combo_column_proxy_cancelling_edge"
                if port in (2, 5, 8)
                else "combo_column_proxy_control_edge"
            ),
        )
    coherence.update(
        {
            offset + 0: 10.0,
            offset + 1: 5.0,
            offset + 2: 9.0,
            offset + 3: 5.0,
            offset + 4: 5.0,
            offset + 5: 10.0,
            offset + 6: 5.0,
            offset + 7: 5.0,
            offset + 8: 11.0,
            offset + 9: 5.0,
        }
    )


def _add_instability_component(
    graph: _GraphBuilder,
    coherence: dict[int, float],
    *,
    offset: int,
) -> None:
    for local_node in range(37):
        coherence[offset + local_node] = 5.0
    coherence[offset] = 10.0
    for port in range(1, 10):
        graph.connect(
            offset,
            port,
            offset + port,
            1,
            conductance=1.0,
            role="combo_instability_support",
        )
    outside_node = offset + 10
    for neighbor_node in range(offset + 1, offset + 10):
        for local_port in (2, 3, 4):
            graph.connect(
                neighbor_node,
                local_port,
                outside_node,
                1,
                conductance=1.0,
                role="combo_instability_cut",
            )
            outside_node += 1


def _add_growth_component(
    graph: _GraphBuilder,
    coherence: dict[int, float],
    *,
    offset: int,
) -> None:
    graph.connect(offset, 1, offset + 1, 1, conductance=1.0, role="combo_outward_flux_path")
    graph.connect(offset, 2, offset + 2, 1, conductance=1.0, role="combo_outward_flux_path")
    coherence[offset] = 1.0
    coherence[offset + 1] = 10.0
    coherence[offset + 2] = 10.0


def _add_fission_component(
    graph: _GraphBuilder,
    coherence: dict[int, float],
    *,
    offset: int,
) -> dict[str, Any]:
    graph.connect(offset + 1, 1, offset + 3, 1, conductance=1.0, role="combo_left_basin_to_sink")
    graph.connect(offset + 2, 1, offset + 4, 1, conductance=1.0, role="combo_right_basin_to_sink")
    graph.connect(offset, 1, offset + 3, 2, conductance=0.1, role="combo_module_core_left")
    graph.connect(offset, 2, offset + 4, 2, conductance=0.1, role="combo_module_core_right")
    coherence[offset + 0] = 1.0
    coherence[offset + 1] = 10.0
    coherence[offset + 2] = 10.0
    coherence[offset + 3] = 5.0
    coherence[offset + 4] = 5.0
    return {
        "expansion_registry": {
            f"combo-fission-module-{offset}": {
                "parent_sink_id": offset,
                "module_node_ids": [
                    offset + 0,
                    offset + 1,
                    offset + 2,
                    offset + 3,
                    offset + 4,
                ],
                "expansion_step": 0,
                "distribution_weights": [0.5, 0.5],
            }
        }
    }


def _spark_column_proxy_emitter(
    emitter_name: str,
) -> tuple[_GraphBuilder, dict[int, float], dict[str, Any], dict[str, Any]]:
    graph = _GraphBuilder(10)
    for port in range(1, 10):
        graph.connect(
            0,
            port,
            port,
            1,
            conductance=1.0,
            role=(
                "column_proxy_cancelling_edge"
                if port in (2, 5, 8)
                else "column_proxy_control_edge"
            ),
        )
    coherence = {
        0: 10.0,
        1: 5.0,
        2: 9.0,
        3: 5.0,
        4: 5.0,
        5: 10.0,
        6: 5.0,
        7: 5.0,
        8: 11.0,
        9: 5.0,
    }
    parameters = _emitter_parameters(
        emitter_name,
        graph_preconditions={
            "runtime_sink": "node 0 remains sink after flux recomputation",
            "active_degree": 9,
            "column_proxy": "column 2 H_s^(b) cancels to zero",
        },
        predicted_signatures=(
            "family_extensions.grc9.event_domain == spark",
            "family_extensions.grc9.spark_evidence.column_proxy_gate_pass == true",
            "family_extensions.grc9.expansion_evidence.internal_edge_count > 0",
        ),
    )
    return graph, coherence, {"sink_set": [0], "basins": {"0": list(range(10))}}, parameters


def _spark_instability_emitter() -> tuple[_GraphBuilder, dict[int, float], dict[str, Any], dict[str, Any]]:
    graph = _GraphBuilder(37)
    for port in range(1, 10):
        graph.connect(0, port, port, 1, conductance=1.0, role="instability_support")
    outside_node = 10
    for neighbor_node in range(1, 10):
        for local_port in (2, 3, 4):
            graph.connect(
                neighbor_node,
                local_port,
                outside_node,
                1,
                conductance=1.0,
                role="instability_cut",
            )
            outside_node += 1
    coherence = {node_id: 5.0 for node_id in range(graph.node_count)}
    coherence[0] = 10.0
    parameters = _emitter_parameters(
        "spark_instability_emitter",
        graph_preconditions={
            "runtime_sink": "node 0 remains sink after flux recomputation",
            "active_degree": 9,
            "cut_ratio": "27 cut edges around 9-edge support patch",
        },
        predicted_signatures=(
            "family_extensions.grc9.event_domain == spark",
            "family_extensions.grc9.spark_evidence.instability_gate_pass == true",
        ),
    )
    return graph, coherence, {"sink_set": [0], "basins": {"0": list(range(10))}}, parameters


def _growth_pressure_emitter() -> tuple[_GraphBuilder, dict[int, float], dict[str, Any], dict[str, Any]]:
    graph = _GraphBuilder(3)
    graph.connect(0, 1, 1, 1, conductance=1.0, role="outward_flux_path")
    graph.connect(0, 2, 2, 1, conductance=1.0, role="outward_flux_path")
    coherence = {0: 1.0, 1: 10.0, 2: 10.0}
    parameters = _emitter_parameters(
        "growth_pressure_emitter",
        graph_preconditions={
            "inactive_parent_ports": [3, 4, 5, 6, 7, 8, 9],
            "outward_flux_parent": 0,
            "birth_probability": "forced high by lambda_birth",
        },
        predicted_signatures=(
            "family_extensions.grc9.event_domain == growth",
            "family_extensions.grc9.growth_evidence.birth_probability > 0",
        ),
    )
    return graph, coherence, {"sink_set": [], "basins": {}}, parameters


def _post_expansion_fission_emitter() -> tuple[_GraphBuilder, dict[int, float], dict[str, Any], dict[str, Any]]:
    graph = _GraphBuilder(5)
    graph.connect(1, 1, 3, 1, conductance=1.0, role="left_basin_to_sink")
    graph.connect(2, 1, 4, 1, conductance=1.0, role="right_basin_to_sink")
    graph.connect(0, 1, 3, 2, conductance=0.1, role="module_core_left")
    graph.connect(0, 2, 4, 2, conductance=0.1, role="module_core_right")
    coherence = {0: 1.0, 1: 10.0, 2: 10.0, 3: 5.0, 4: 5.0}
    parameters = _emitter_parameters(
        "post_expansion_fission_emitter",
        graph_preconditions={
            "post_expansion_context": "initial expansion_registry module",
            "growth_disabled": "lambda_birth == 0",
            "persistent_sink_pair": "two module sinks persist through delta",
        },
        predicted_signatures=(
            "family_extensions.grc9.expansion_summary.identity_fission_candidate_count > 0",
            "family_extensions.grc9.expansion_summary.identity_fission_confirmed_count > 0",
        ),
    )
    extras = {
        "sink_set": [1, 2],
        "basins": {"1": [1, 3], "2": [2, 4]},
        "expansion_registry": {
            "fission-module-0": {
                "parent_sink_id": 0,
                "module_node_ids": [0, 1, 2, 3, 4],
                "expansion_step": 0,
                "distribution_weights": [0.5, 0.5],
            }
        },
    }
    return graph, coherence, extras, parameters


def _emitter_parameters(
    emitter_name: str,
    *,
    graph_preconditions: Mapping[str, Any],
    predicted_signatures: tuple[str, ...],
) -> dict[str, Any]:
    return {
        "emitter_name": emitter_name,
        "repair_iteration": "I05_1_theory_first_lifecycle_emitter_repair",
        "graph_preconditions": dict(graph_preconditions),
        "predicted_signatures": [
            {"field_path": signature, "expected": "match"}
            for signature in predicted_signatures
        ],
    }


def _combo_parameters(
    combo_name: str,
    *,
    components: tuple[str, ...],
    graph_preconditions: Mapping[str, Any],
    predicted_signatures: tuple[str, ...],
) -> dict[str, Any]:
    return {
        "combo_name": combo_name,
        "combo_iteration": "I05_3_lifecycle_combo_examples",
        "components": list(components),
        "graph_preconditions": dict(graph_preconditions),
        "predicted_signatures": [
            {"field_path": signature, "expected": "match"}
            for signature in predicted_signatures
        ],
    }


def _emitter_runtime_config(
    emitter_name: str,
    parameters: Mapping[str, Any],
) -> dict[str, Any]:
    evolution: dict[str, Any] = {
        "alpha": 0.0,
        "beta": 0.0,
        "gamma": 0.0,
        "delta": 0.0,
        "kappa_c": 10.0,
        "eta": 1.0,
        "tau_instability": 999.0,
        "eps_spark": 0.5,
        "D_eff_target": 30,
        "w_bond": 1.0,
        "lambda_birth": 0.0,
        "alpha_seed": 0.25,
        "rng_seed": 0,
        "identity_fission_persistence_delta": 3,
        "identity_fission_min_basin_mass": 0.0,
        "site_potential_selection": "quadratic",
        "site_potential_params": {"scale": 0.0, "mu": 0.0},
    }
    if emitter_name == "spark_instability_emitter":
        evolution["tau_instability"] = 0.5
        evolution["eps_spark"] = 0.0
    elif emitter_name == "growth_pressure_emitter":
        evolution["lambda_birth"] = 1e9
        evolution["tau_instability"] = 999.0
        evolution["eps_spark"] = 0.0
    elif emitter_name == "post_expansion_fission_emitter":
        evolution["lambda_birth"] = 0.0
        evolution["tau_instability"] = 999.0
        evolution["eps_spark"] = 0.0
    return {
        "dt": 0.1,
        "evolution": evolution,
        "constitutive_semantic_modes": {
            "frame_mode": "fixed_port_chart",
            "curvature_backend": "none",
            "boundary_mode": "prune",
            "expansion_distribution_mode": "equal",
            "edge_label_selection": "all",
        },
    }


def _combo_runtime_config(combo_name: str) -> dict[str, Any]:
    config = _emitter_runtime_config("spark_column_proxy_emitter", {})
    evolution = dict(config["evolution"])
    evolution["eps_spark"] = 0.5
    evolution["tau_instability"] = 0.5 if combo_name == "dual_spark_combo" else 999.0
    evolution["lambda_birth"] = (
        1e9
        if combo_name
        in {"spark_growth_combo", "growth_fission_combo", "spark_growth_fission_combo"}
        else 0.0
    )
    evolution["identity_fission_persistence_delta"] = 3
    evolution["identity_fission_min_basin_mass"] = 0.0
    config["evolution"] = evolution
    return config


def _targeted_diagnostic_runtime_config(fixture_name: str) -> dict[str, Any]:
    config = _emitter_runtime_config("post_expansion_fission_emitter", {})
    evolution = dict(config["evolution"])
    evolution["eps_spark"] = 0.5 if fixture_name.startswith("column_proxy_") else 0.0
    evolution["tau_instability"] = 999.0
    evolution["lambda_birth"] = 0.0
    evolution["identity_fission_persistence_delta"] = 3
    evolution["identity_fission_min_basin_mass"] = 0.0
    config["evolution"] = evolution
    return config


def _complex_event_runtime_config(fixture_name: str) -> dict[str, Any]:
    config = _emitter_runtime_config("spark_column_proxy_emitter", {})
    evolution = dict(config["evolution"])
    evolution["eps_spark"] = 0.5
    evolution["tau_instability"] = 0.5
    evolution["lambda_birth"] = 1e9
    evolution["identity_fission_persistence_delta"] = 3
    evolution["identity_fission_min_basin_mass"] = 0.0
    if fixture_name == "all_events_complex_soft_threshold_perturbation_control":
        evolution["eps_spark"] = 0.1
        evolution["tau_instability"] = 0.6
        evolution["lambda_birth"] = 1e6
    if fixture_name == "all_events_complex_high_degree_perturbation_control":
        evolution["D_eff_target"] = 44
    config["evolution"] = evolution
    return config


def _corrected_growth_runtime_config(fixture_name: str) -> dict[str, Any]:
    config = _emitter_runtime_config("growth_pressure_emitter", {})
    evolution = dict(config["evolution"])
    evolution["eps_spark"] = 0.0
    evolution["tau_instability"] = 999.0
    evolution["lambda_birth"] = (
        0.0
        if fixture_name == "front_capacity_growth_zero_birth_control"
        else 1e9
    )
    config["evolution"] = evolution
    modes = dict(config["constitutive_semantic_modes"])
    modes["growth_parent_eligibility"] = "grc9_front_capacity"
    config["constitutive_semantic_modes"] = modes
    return config


def _corrected_growth_combo_runtime_config(fixture_name: str) -> dict[str, Any]:
    config = _combo_runtime_config(
        "spark_growth_fission_combo"
        if fixture_name == "corrected_spark_growth_fission_combo"
        else (
            "growth_fission_combo"
            if fixture_name == "corrected_growth_fission_combo"
            else "spark_growth_combo"
        )
    )
    evolution = dict(config["evolution"])
    evolution["lambda_birth"] = 1e9
    evolution["identity_fission_persistence_delta"] = 3
    evolution["identity_fission_min_basin_mass"] = 0.0
    config["evolution"] = evolution
    modes = dict(config["constitutive_semantic_modes"])
    modes["growth_parent_eligibility"] = "grc9_front_capacity"
    config["constitutive_semantic_modes"] = modes
    return config


def _corrected_growth_complex_runtime_config(fixture_name: str) -> dict[str, Any]:
    legacy_name = fixture_name.removeprefix("corrected_")
    config = _complex_event_runtime_config(legacy_name)
    evolution = dict(config["evolution"])
    evolution["lambda_birth"] = 1e9
    if fixture_name == "corrected_all_events_complex_soft_threshold_perturbation_control":
        evolution["eps_spark"] = 0.1
        evolution["tau_instability"] = 0.6
        evolution["lambda_birth"] = 1e6
    if fixture_name == "corrected_all_events_complex_high_degree_perturbation_control":
        evolution["D_eff_target"] = 44
    evolution["identity_fission_persistence_delta"] = 3
    evolution["identity_fission_min_basin_mass"] = 0.0
    config["evolution"] = evolution
    modes = dict(config["constitutive_semantic_modes"])
    modes["growth_parent_eligibility"] = "grc9_front_capacity"
    config["constitutive_semantic_modes"] = modes
    return config


__all__ = [
    "GRC9_SEED_GENERATOR_VERSION",
    "GRC9_COMPLEX_EVENT_STABILITY_NAMES",
    "GRC9_COMPLEX_EVENT_STABILITY_PROFILE",
    "GRC9_CORRECTED_GROWTH_ELEMENTARY_NAMES",
    "GRC9_CORRECTED_GROWTH_ELEMENTARY_PROFILE",
    "GRC9_CORRECTED_GROWTH_COMBO_NAMES",
    "GRC9_CORRECTED_GROWTH_COMBO_PROFILE",
    "GRC9_CORRECTED_GROWTH_COMPLEX_NAMES",
    "GRC9_CORRECTED_GROWTH_COMPLEX_PROFILE",
    "GRC9_LIFECYCLE_EMITTER_NAMES",
    "GRC9_LIFECYCLE_EMITTER_PERTURBATION_NAMES",
    "GRC9_LIFECYCLE_COMBO_NAMES",
    "GRC9_LIFECYCLE_COMBO_PROFILE",
    "GRC9_LIFECYCLE_EMITTER_REPAIR_PROFILE",
    "GRC9_TARGETED_DIAGNOSTIC_NAMES",
    "GRC9_TARGETED_DIAGNOSTIC_PROFILE",
    "GRC9GeneratedSeed",
    "generate_grc9_corrected_growth_combo_fixture",
    "generate_grc9_corrected_growth_complex_fixture",
    "generate_grc9_corrected_growth_elementary_fixture",
    "generate_grc9_lifecycle_combo",
    "generate_grc9_complex_event_stability_fixture",
    "generate_grc9_lifecycle_emitter",
    "generate_grc9_lifecycle_emitter_perturbation",
    "generate_grc9_seed",
    "generate_grc9_seed_perturbation",
    "generate_grc9_targeted_diagnostic_fixture",
]
