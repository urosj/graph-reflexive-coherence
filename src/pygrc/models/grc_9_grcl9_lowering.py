"""Deterministic GRCL-9 Revision 1 lowering into GRC9 state."""

from __future__ import annotations

from collections import defaultdict, deque
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from pygrc.core import GRCParams, PortGraphBackend
from pygrc.models.grc_9 import GRC9
from pygrc.models.grc_9_ports import port_id_to_slot
from pygrc.models.grc_9_state import ExpansionRecord, GRC9State, PortEdge

from pygrc.landscapes.extensions.grcl9 import (
    GRCL9ColumnProxyProfile,
    GRCL9ExpansionRefinementRegion,
    GRCL9GrowthLocus,
    GRCL9InstabilityProfile,
    GRCL9PostExpansionFissionGeometry,
    GRCL9SourceConstruct,
    GRCL9SourceDocument,
    GRCL9SparkCandidateRegion,
    grcl9_source_fixture_by_name,
)

from .grc_9_grcl9_provenance import (
    GRCL9_LOWERING_MODE,
    GRCL9_PROJECTOR_REVISION,
    grcl9_edge_payload,
    grcl9_node_payload,
)


@dataclass(frozen=True)
class GRCL9LoweringResult:
    """Result of lowering one GRCL-9 source document."""

    source: GRCL9SourceDocument
    state: GRC9State
    node_id_by_role: Mapping[str, int]
    edge_id_by_role: Mapping[str, int]


def lower_grcl9_fixture_by_name(
    fixture_name: str,
    *,
    params: GRCParams | Mapping[str, Any] | None = None,
) -> GRCL9LoweringResult:
    """Lower one built-in fixture by name."""

    fixtures = grcl9_source_fixture_by_name()
    if fixture_name not in fixtures:
        raise ValueError(f"unknown GRCL-9 source fixture {fixture_name!r}")
    return lower_grcl9_source_to_grc9_state(fixtures[fixture_name], params=params)


def lower_grcl9_source_to_grc9_state(
    source: GRCL9SourceDocument | Mapping[str, Any],
    *,
    params: GRCParams | Mapping[str, Any] | None = None,
) -> GRCL9LoweringResult:
    """Lower one GRCL-9 source document into a connected GRC9State."""

    document = (
        source
        if isinstance(source, GRCL9SourceDocument)
        else GRCL9SourceDocument.from_mapping(source)
    )
    resolved_params = _coerce_params(params)
    builder = _LoweringBuilder(document, resolved_params)
    builder.lower()
    state = builder.to_state()
    GRC9(params=resolved_params, state=state)
    return GRCL9LoweringResult(
        source=document,
        state=state,
        node_id_by_role=dict(builder.node_id_by_role),
        edge_id_by_role=dict(builder.edge_id_by_role),
    )


def _coerce_params(params: GRCParams | Mapping[str, Any] | None) -> GRCParams:
    if isinstance(params, GRCParams):
        return params
    config = {"dt": 0.1} if params is None else dict(params)
    return GRC9.from_config(config).get_params()


def _canonical_port_edge(
    *,
    node_a: int,
    port_a: int,
    node_b: int,
    port_b: int,
    conductance: float,
    flux_uv: float = 0.0,
) -> PortEdge:
    if (node_a, port_a) <= (node_b, port_b):
        return PortEdge(
            node_u=node_a,
            port_u=port_a,
            node_v=node_b,
            port_v=port_b,
            conductance=float(conductance),
            flux_uv=float(flux_uv),
        )
    return PortEdge(
        node_u=node_b,
        port_u=port_b,
        node_v=node_a,
        port_v=port_a,
        conductance=float(conductance),
        flux_uv=float(-flux_uv),
    )


class _LoweringBuilder:
    def __init__(self, source: GRCL9SourceDocument, params: GRCParams) -> None:
        self.source = source
        self.params = params
        self.topology = PortGraphBackend()
        self.node_coherence: dict[int, float] = {}
        self.port_edges: dict[int, PortEdge] = {}
        self.potential: dict[int, float] = {}
        self.node_id_by_role: dict[str, int] = {}
        self.edge_id_by_role: dict[str, int] = {}
        self.node_provenance: dict[str, dict[str, Any]] = {}
        self.edge_provenance: dict[str, dict[str, Any]] = {}
        self.motif_registry: dict[str, dict[str, Any]] = {}
        self.expected_saturated_node_ids: list[int] = []
        self.expected_column_proxy_candidate_ids: list[int] = []
        self.front_growth_eligible_ports: dict[str, list[int]] = {}
        self.growth_parent_capacity_sources: dict[str, dict[str, Any]] = {}
        self.legacy_growth_locus_ids: list[int] = []
        self.bridge_edge_ids: list[int] = []
        self.initial_sink_set: set[int] = set()
        self.initial_basins: dict[int, set[int]] = {}
        self.initial_expansion_registry: dict[str, ExpansionRecord] = {}

    def lower(self) -> None:
        spark = self._first(GRCL9SparkCandidateRegion)
        growth = self._first(GRCL9GrowthLocus)
        fission = self._first(GRCL9PostExpansionFissionGeometry)
        component_anchors: list[tuple[str, GRCL9SourceConstruct]] = []
        if spark is not None:
            self._lower_spark_family(spark)
            component_anchors.append(("neighbor_port_9", spark))
        if growth is not None:
            self._lower_growth(growth)
            component_anchors.append(("growth_parent", growth))
        if fission is not None:
            self._lower_fission(fission)
            component_anchors.append(("fission_module", fission))
        if not component_anchors:
            raise ValueError("source document contains no lowerable Revision 1 construct")
        self._connect_component_anchors(component_anchors)
        if not self._is_connected():
            raise ValueError("GRCL-9 lowering produced a disconnected graph")

    def to_state(self) -> GRC9State:
        budget_target = float(sum(self.node_coherence.values()))
        return GRC9State(
            topology=self.topology,
            node_coherence=dict(self.node_coherence),
            port_edges=dict(self.port_edges),
            geometric_length={edge_id: 1.0 for edge_id in self.port_edges},
            temporal_delay={},
            flux_coupling={edge_id: abs(port_edge.flux_uv) for edge_id, port_edge in self.port_edges.items()},
            potential=dict(self.potential),
            sink_set=set(self.initial_sink_set),
            basins={sink_id: set(members) for sink_id, members in self.initial_basins.items()},
            expansion_registry=dict(self.initial_expansion_registry),
            coarse_cache={},
            rng_state=None,
            prev_column_diagnostic={},
            edge_label_computation_mode={"geometric_length": "grcl9_lowering_fixed"},
            edge_label_params={"source": "grcl9_lowering_v1"},
            step_index=0,
            time=0.0,
            budget_target=budget_target,
            remainder=0.0,
            cached_quantities={
                "grcl9_source_schema_version": self.source.source_schema_version,
                "grcl9_source_fixture_name": self.source.fixture_name,
                "grcl9_manifest_entry_id": self.source.manifest_entry_id,
                "grcl9_projector_revision": GRCL9_PROJECTOR_REVISION,
                "grcl9_lowering_mode": GRCL9_LOWERING_MODE,
                "grcl9_provenance": {
                    "nodes": dict(sorted(self.node_provenance.items())),
                    "edges": dict(sorted(self.edge_provenance.items())),
                },
                "grcl9_motif_registry": self._final_motif_registry(),
                "grcl9_assembly_policy": {
                    "port_assignment_mode": "deterministic_role_ordered_ports",
                    "mass_partition_mode": self.source.budget_policy.mass_partition_mode,
                    "bridge_edge_policy": self.source.bridge_policy.edge_kind,
                    "module_size_formula": self._module_size_formula(),
                    "distribution_weight_mode": self._distribution_weight_mode(),
                    "budget_preservation_policy": self.source.budget_policy.budget_preservation_policy,
                },
                "grcl9_expected_saturated_node_ids": list(self.expected_saturated_node_ids),
                "grcl9_expected_column_proxy_candidate_ids": list(
                    self.expected_column_proxy_candidate_ids
                ),
                "grc9_front_growth_eligible_ports": dict(
                    sorted(self.front_growth_eligible_ports.items())
                ),
                "grc9_growth_parent_capacity_sources": dict(
                    sorted(self.growth_parent_capacity_sources.items())
                ),
                "grcl9_front_growth_eligible_ports": dict(
                    sorted(self.front_growth_eligible_ports.items())
                ),
                "grcl9_growth_parent_capacity_sources": dict(
                    sorted(self.growth_parent_capacity_sources.items())
                ),
                "grcl9_legacy_growth_locus_ids": list(self.legacy_growth_locus_ids),
                "grcl9_growth_semantics_status": self._growth_semantics_status(),
                "grcl9_bridge_edge_ids": list(self.bridge_edge_ids),
            },
            params_identity=self.params.params_hash,
        )

    def _lower_spark_family(self, spark: GRCL9SparkCandidateRegion) -> None:
        center = self._add_node("candidate", spark, coherence=self._candidate_coherence())
        self.expected_saturated_node_ids.append(center)
        column = self._first(GRCL9ColumnProxyProfile)
        if column is not None:
            self.expected_column_proxy_candidate_ids.append(center)
        neighbor_ids: dict[int, int] = {}
        for port in range(1, 10):
            neighbor = self._add_node(
                f"neighbor_port_{port}",
                spark,
                coherence=self._neighbor_coherence(port),
            )
            neighbor_ids[port] = neighbor
            self._connect(
                f"candidate_port_{port}",
                spark,
                center,
                port,
                neighbor,
                1,
                conductance=self._candidate_edge_conductance(port),
                motif_role="saturated_candidate_boundary",
            )
        instability = self._first(GRCL9InstabilityProfile)
        if (
            instability is not None
            and str((instability.support_cut_profile or {}).get("cut_class", ""))
            == "high_cut"
        ):
            cut_index = 1
            for port in range(1, 10):
                neighbor = neighbor_ids[port]
                for local_port in (2, 3, 4):
                    cut_node = self._add_node(
                        f"instability_cut_{cut_index}",
                        instability,
                        coherence=5.0,
                    )
                    self._connect(
                        f"instability_cut_{cut_index}",
                        instability,
                        neighbor,
                        local_port,
                        cut_node,
                        1,
                        conductance=1.0,
                        motif_role="instability_cut",
                    )
                    cut_index += 1

    def _lower_growth(self, growth: GRCL9GrowthLocus) -> None:
        high_pressure = growth.lambda_birth >= 1.0
        parent = self._add_node("growth_parent", growth, coherence=1.0)
        capacity_source = {
            "construct_id": growth.construct_id,
            "growth_semantics": growth.growth_semantics,
            "front_capacity_source": growth.front_capacity_source,
            "front_source_construct_id": growth.front_source_construct_id,
            "inactive_parent_port": growth.inactive_parent_port,
            "source_mechanism": "grcl9_growth_locus",
        }
        if growth.growth_semantics == "front_capacity":
            closed_front = (
                str((growth.pressure_profile or {}).get("class", ""))
                in {"closed_front", "no_front_capacity"}
                or str((growth.pressure_profile or {}).get("boundary", ""))
                in {"closed_front", "closed_spark_refinement_front", "no_front_capacity"}
            )
            self.front_growth_eligible_ports[str(parent)] = (
                [] if closed_front else [growth.inactive_parent_port]
            )
            self.growth_parent_capacity_sources[str(parent)] = capacity_source
        else:
            self.legacy_growth_locus_ids.append(parent)
            self.growth_parent_capacity_sources[str(parent)] = capacity_source
        active_ports = tuple(port for port in (1, 2) if port != growth.inactive_parent_port)
        if not active_ports:
            active_ports = (1,)
        for index, port in enumerate(active_ports, start=1):
            support = self._add_node(
                f"growth_support_{index}",
                growth,
                coherence=10.0 if high_pressure else 0.35,
            )
            self._connect(
                f"growth_parent_port_{port}",
                growth,
                parent,
                port,
                support,
                1,
                conductance=1.0 if high_pressure else 0.25,
                motif_role="growth_pressure_support",
            )

    def _lower_fission(self, fission: GRCL9PostExpansionFissionGeometry) -> None:
        sink_a_mass = self._stable_basin_mass_hint(fission.sink_region_a, default=0.75)
        sink_b_mass = self._stable_basin_mass_hint(fission.sink_region_b, default=0.75)
        sink_a_stability = self._stable_basin_stability(fission.sink_region_a)
        sink_b_stability = self._stable_basin_stability(fission.sink_region_b)
        sink_a_support_count = self._stable_basin_support_count(fission.sink_region_a)
        sink_b_support_count = self._stable_basin_support_count(fission.sink_region_b)
        bridge_class = self._saddle_bridge_class(default="weak_saddle_bridge")
        module = self._add_node("fission_module", fission, coherence=1.0)
        sink_a = self._add_node(
            "fission_sink_a",
            fission,
            coherence=self._fission_sink_coherence(
                mass_hint=sink_a_mass,
                stability_class=sink_a_stability,
            ),
        )
        sink_b = self._add_node(
            "fission_sink_b",
            fission,
            coherence=self._fission_sink_coherence(
                mass_hint=sink_b_mass,
                stability_class=sink_b_stability,
            ),
        )
        support_a_nodes = self._add_fission_support_nodes(
            fission,
            sink_node_id=sink_a,
            basin_label="a",
            support_count=sink_a_support_count,
            mass_hint=sink_a_mass,
            stability_class=sink_a_stability,
        )
        support_b_nodes = self._add_fission_support_nodes(
            fission,
            sink_node_id=sink_b,
            basin_label="b",
            support_count=sink_b_support_count,
            mass_hint=sink_b_mass,
            stability_class=sink_b_stability,
        )
        support_a = support_a_nodes[0]
        support_b = support_b_nodes[0]
        self._connect(
            "fission_module_to_support_a",
            fission,
            module,
            1,
            support_a,
            2,
            conductance=self._fission_bridge_conductance(bridge_class),
            motif_role="fission_separable_bridge",
            edge_kind="bridge",
            bridge=True,
            bridge_role=self.source.bridge_policy.bridge_role,
        )
        self._connect(
            "fission_module_to_support_b",
            fission,
            module,
            2,
            support_b,
            2,
            conductance=self._fission_bridge_conductance(bridge_class),
            motif_role="fission_pole_support",
        )
        if bridge_class in {"merge_saddle_bridge", "strong_saddle_bridge"}:
            self._connect(
                "fission_sink_b_to_sink_a_merge_bridge",
                fission,
                sink_b,
                9,
                sink_a,
                9,
                conductance=8.0,
                motif_role="fission_merge_bridge",
                edge_kind="bridge",
                bridge=True,
                bridge_role="merge_saddle_bridge",
            )
            for index, (source_support, target_support) in enumerate(
                zip(support_b_nodes, support_a_nodes, strict=False),
                start=1,
            ):
                self._connect(
                    f"fission_support_b_to_support_a_merge_bridge_{index}",
                    fission,
                    source_support,
                    3,
                    target_support,
                    3,
                    conductance=4.0,
                    motif_role="fission_merge_bridge",
                    edge_kind="bridge",
                    bridge=True,
                    bridge_role="merge_saddle_bridge",
                )
        self.initial_sink_set = {sink_a, sink_b}
        self.initial_basins = {
            sink_a: {sink_a, *support_a_nodes},
            sink_b: {sink_b, *support_b_nodes},
        }
        module_node_ids = (module, sink_a, sink_b, *support_a_nodes, *support_b_nodes)
        self.initial_expansion_registry = {
            "grcl9-fission-module-0": ExpansionRecord(
                parent_sink_id=module,
                module_node_ids=module_node_ids,
                expansion_step=0,
                distribution_weights=(0.5, 0.5),
            )
        }

    def _connect_component_anchors(
        self,
        anchors: list[tuple[str, GRCL9SourceConstruct]],
    ) -> None:
        if len(anchors) <= 1:
            return
        for index, ((left_role, _), (right_role, construct)) in enumerate(
            zip(anchors, anchors[1:], strict=False),
            start=1,
        ):
            left_node = self.node_id_by_role[left_role]
            right_node = self.node_id_by_role[right_role]
            self._connect(
                f"cascade_component_bridge_{index}",
                construct,
                left_node,
                self._first_free_port(left_node),
                right_node,
                self._first_free_port(right_node),
                conductance=0.001,
                motif_role="cascade_component_bridge",
                edge_kind="bridge",
                bridge=True,
                bridge_role="cascade_component_bridge",
            )

    def _first_free_port(self, node_id: int) -> int:
        for port in range(1, 10):
            if self.topology.port_edge_id(node_id, port_id_to_slot(port)) is None:
                return port
        raise ValueError(f"node {node_id} has no free GRC9 ports for cascade bridge")

    def _add_fission_support_nodes(
        self,
        construct: GRCL9SourceConstruct,
        *,
        sink_node_id: int,
        basin_label: str,
        support_count: int,
        mass_hint: float,
        stability_class: str,
    ) -> tuple[int, ...]:
        support_nodes: list[int] = []
        for index in range(1, support_count + 1):
            role = f"fission_support_{basin_label}" if index == 1 else f"fission_support_{basin_label}_{index}"
            support = self._add_node(
                role,
                construct,
                coherence=self._fission_support_coherence(
                    mass_hint=mass_hint,
                    stability_class=stability_class,
                )
                / max(1, support_count),
            )
            self._connect(
                f"fission_sink_{basin_label}_to_support_{index}",
                construct,
                sink_node_id,
                index,
                support,
                1,
                conductance=self._fission_support_conductance(stability_class),
                motif_role="fission_pole_support",
            )
            support_nodes.append(support)
        return tuple(support_nodes)

    def _stable_basin_mass_hint(self, basin_id: str, *, default: float) -> float:
        for term in self._source_terms_by_kind("stable_basin"):
            if str(term.get("basin_id", "")) == basin_id:
                value = term.get("mass_hint", default)
                if isinstance(value, int | float):
                    return max(0.0, float(value))
        return float(default)

    def _stable_basin_stability(self, basin_id: str) -> str:
        for term in self._source_terms_by_kind("stable_basin"):
            if str(term.get("basin_id", "")) == basin_id:
                return str(term.get("stability_class", "stable"))
        return "stable"

    def _stable_basin_support_count(self, basin_id: str) -> int:
        for term in self._source_terms_by_kind("stable_basin"):
            if str(term.get("basin_id", "")) == basin_id:
                value = term.get("support_node_count", 1)
                if isinstance(value, int) and not isinstance(value, bool):
                    return max(1, value)
        return 1

    def _saddle_bridge_class(self, *, default: str) -> str:
        for term in self._source_terms_by_kind("saddle_bridge"):
            bridge_class = term.get("bridge_class")
            if bridge_class is not None:
                return str(bridge_class)
        return default

    def _source_terms_by_kind(self, term_kind: str) -> tuple[Mapping[str, Any], ...]:
        provenance = self.source.compiled_source_provenance or {}
        raw_terms = provenance.get("source_terms", ())
        if not isinstance(raw_terms, tuple | list):
            return ()
        return tuple(
            term
            for term in raw_terms
            if isinstance(term, Mapping) and str(term.get("term_kind", "")) == term_kind
        )

    def _fission_sink_coherence(self, *, mass_hint: float, stability_class: str) -> float:
        if stability_class in {"collapsing", "decaying", "weak"}:
            return max(0.05, 2.0 * mass_hint)
        return max(0.25, 12.0 * mass_hint)

    def _fission_support_coherence(self, *, mass_hint: float, stability_class: str) -> float:
        if stability_class in {"collapsing", "decaying", "weak"}:
            return max(1.0, 8.0 * max(mass_hint, 0.25))
        return max(0.25, 6.0 * mass_hint)

    def _fission_support_conductance(self, stability_class: str) -> float:
        if stability_class in {"collapsing", "decaying", "weak"}:
            return 0.35
        return 1.0

    def _fission_bridge_conductance(self, bridge_class: str) -> float:
        if bridge_class in {"isolated_saddle_bridge", "negligible_saddle_bridge"}:
            return 0.001
        if bridge_class in {"merge_saddle_bridge", "strong_saddle_bridge"}:
            return 2.0
        if bridge_class == "moderate_saddle_bridge":
            return 0.5
        return 0.1

    def _add_node(
        self,
        role: str,
        construct: GRCL9SourceConstruct,
        *,
        coherence: float,
    ) -> int:
        node_id = self.topology.add_node(
            grcl9_node_payload(
                construct=construct,
                motif_role=role,
                fixture_name=self.source.fixture_name,
            )
        )
        self.node_id_by_role[role] = node_id
        self.node_coherence[node_id] = float(coherence)
        self.potential[node_id] = 0.0
        self.node_provenance[str(node_id)] = {
            "source_construct_id": construct.construct_id,
            "source_construct_kind": construct.construct_kind,
            "motif_id": construct.motif_id,
            "motif_role": role,
        }
        self._record_motif_node(construct, node_id, role)
        return node_id

    def _connect(
        self,
        role: str,
        construct: GRCL9SourceConstruct,
        node_a: int,
        port_a: int,
        node_b: int,
        port_b: int,
        *,
        conductance: float,
        motif_role: str,
        edge_kind: str = "structural_support",
        bridge: bool = False,
        bridge_role: str | None = None,
    ) -> int:
        edge_id = self.topology.connect_ports(
            node_a,
            port_id_to_slot(port_a),
            node_b,
            port_id_to_slot(port_b),
            grcl9_edge_payload(
                construct=construct,
                motif_role=motif_role,
                fixture_name=self.source.fixture_name,
                edge_kind=edge_kind,
                bridge=bridge,
                bridge_role=bridge_role,
            ),
        )
        self.port_edges[edge_id] = _canonical_port_edge(
            node_a=node_a,
            port_a=port_a,
            node_b=node_b,
            port_b=port_b,
            conductance=float(conductance),
        )
        self.edge_id_by_role[role] = edge_id
        self.edge_provenance[str(edge_id)] = {
            "source_construct_id": construct.construct_id,
            "source_construct_kind": construct.construct_kind,
            "motif_id": construct.motif_id,
            "motif_role": motif_role,
            "edge_kind": edge_kind,
            "bridge": bridge,
        }
        self._record_motif_edge(construct, edge_id, motif_role)
        if bridge:
            self.bridge_edge_ids.append(edge_id)
        return edge_id

    def _candidate_edge_conductance(self, port: int) -> float:
        column = self._first(GRCL9ColumnProxyProfile)
        if column is not None and ((port - 1) % 3) + 1 == column.target_column:
            return 1.0 if column.cancellation_mode == "cancellation" else 1.5
        instability = self._first(GRCL9InstabilityProfile)
        if instability is not None and port in (1, 2, 3):
            return 1.0
        return 1.0

    def _candidate_coherence(self) -> float:
        return 10.0

    def _neighbor_coherence(self, port: int) -> float:
        column = self._first(GRCL9ColumnProxyProfile)
        if column is not None and ((port - 1) % 3) + 1 == column.target_column:
            if column.cancellation_mode == "cancellation":
                row = ((port - 1) // 3) + 1
                return {1: 9.0, 2: 10.0, 3: 11.0}[row]
            return 5.0
        return 5.0

    def _record_motif_node(
        self,
        construct: GRCL9SourceConstruct,
        node_id: int,
        role: str,
    ) -> None:
        record = self.motif_registry.setdefault(
            construct.motif_id,
            {"node_ids": [], "edge_ids": [], "source_construct_ids": set(), "motif_roles": set()},
        )
        record["node_ids"].append(node_id)
        record["source_construct_ids"].add(construct.construct_id)
        record["motif_roles"].add(role)

    def _record_motif_edge(
        self,
        construct: GRCL9SourceConstruct,
        edge_id: int,
        role: str,
    ) -> None:
        record = self.motif_registry.setdefault(
            construct.motif_id,
            {"node_ids": [], "edge_ids": [], "source_construct_ids": set(), "motif_roles": set()},
        )
        record["edge_ids"].append(edge_id)
        record["source_construct_ids"].add(construct.construct_id)
        record["motif_roles"].add(role)

    def _final_motif_registry(self) -> dict[str, dict[str, Any]]:
        construct_ids_by_motif: dict[str, set[str]] = defaultdict(set)
        for construct in self.source.constructs:
            construct_ids_by_motif[construct.motif_id].add(construct.construct_id)
        result: dict[str, dict[str, Any]] = {}
        for motif_id, raw in sorted(self.motif_registry.items()):
            source_construct_ids = set(raw["source_construct_ids"]) | construct_ids_by_motif[motif_id]
            result[motif_id] = {
                "node_ids": sorted(raw["node_ids"]),
                "edge_ids": sorted(raw["edge_ids"]),
                "source_construct_ids": sorted(source_construct_ids),
                "motif_roles": sorted(raw["motif_roles"]),
            }
        return result

    def _module_size_formula(self) -> str:
        expansion = self._first(GRCL9ExpansionRefinementRegion)
        if expansion is None:
            return ""
        return expansion.module_size_formula

    def _distribution_weight_mode(self) -> str:
        expansion = self._first(GRCL9ExpansionRefinementRegion)
        if expansion is None:
            return ""
        return expansion.coherence_transfer_mode

    def _growth_semantics_status(self) -> str:
        if self.front_growth_eligible_ports:
            return "front_capacity"
        if self.legacy_growth_locus_ids:
            return "legacy_growth_locus"
        return "none"

    def _first(self, cls: type[Any]) -> Any | None:
        for construct in self.source.constructs:
            if isinstance(construct, cls):
                return construct
        return None

    def _is_connected(self) -> bool:
        node_ids = tuple(self.topology.iter_live_node_ids())
        if not node_ids:
            return False
        seen = {node_ids[0]}
        queue: deque[int] = deque([node_ids[0]])
        while queue:
            node_id = queue.popleft()
            for neighbor in self.topology.neighbors(node_id):
                if neighbor not in seen:
                    seen.add(neighbor)
                    queue.append(neighbor)
        return seen == set(node_ids)


__all__ = [
    "GRCL9LoweringResult",
    "lower_grcl9_fixture_by_name",
    "lower_grcl9_source_to_grc9_state",
]
