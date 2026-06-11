"""Deterministic GRCL-9V3 Revision 1 lowering into GRC9V3 state."""

from __future__ import annotations

from collections import Counter, defaultdict, deque
from collections.abc import Mapping
from dataclasses import dataclass
import random
from typing import Any

from pygrc.core import GRCParams, PortGraphBackend
from pygrc.landscapes.extensions.grcl9v3 import (
    GRCL9V3AppendixEDivisionRegion,
    GRCL9V3ChoiceCollapseRegion,
    GRCL9V3ColumnProxyFallbackProfile,
    GRCL9V3ExpansionRefinementRegion,
    GRCL9V3GrowthLocus,
    GRCL9V3HybridSparkRegion,
    GRCL9V3HybridTensorProfile,
    GRCL9V3QuiescentHybridRegion,
    GRCL9V3RowBasisHessianProfile,
    GRCL9V3SourceConstruct,
    GRCL9V3SourceDocument,
    GRCL9V3TransportReroutingRegion,
    grcl9v3_source_fixture_by_name,
    validate_grcl9v3_source_document_against_manifest,
)
from pygrc.models.grc_9_ports import port_id_to_slot
from pygrc.models.grc_9_state import ExpansionRecord, PortEdge
from pygrc.models.grc_9_v3 import GRC9V3
from pygrc.models.grc_9_v3_state import GRC9V3NodeState, GRC9V3State

from .grc_9_v3_grcl9v3_provenance import (
    GRCL9V3_LOWERING_MODE,
    GRCL9V3_PROJECTOR_REVISION,
    grcl9v3_edge_payload,
    grcl9v3_node_payload,
)


@dataclass(frozen=True)
class GRCL9V3LoweringResult:
    """Result of lowering one GRCL-9V3 source document."""

    source: GRCL9V3SourceDocument
    state: GRC9V3State
    node_id_by_role: Mapping[str, int]
    edge_id_by_role: Mapping[str, int]


def lower_grcl9v3_fixture_by_name(
    fixture_name: str,
    *,
    params: GRCParams | Mapping[str, Any] | None = None,
) -> GRCL9V3LoweringResult:
    """Lower one built-in GRCL-9V3 fixture by name."""

    fixtures = grcl9v3_source_fixture_by_name()
    if fixture_name not in fixtures:
        raise ValueError(f"unknown GRCL-9V3 source fixture {fixture_name!r}")
    return lower_grcl9v3_source_to_grc9v3_state(fixtures[fixture_name], params=params)


def lower_grcl9v3_source_to_grc9v3_state(
    source: GRCL9V3SourceDocument | Mapping[str, Any],
    *,
    params: GRCParams | Mapping[str, Any] | None = None,
) -> GRCL9V3LoweringResult:
    """Lower one GRCL-9V3 source document into a connected GRC9V3State."""

    document = (
        source
        if isinstance(source, GRCL9V3SourceDocument)
        else GRCL9V3SourceDocument.from_mapping(source)
    )
    validate_grcl9v3_source_document_against_manifest(
        document,
        allow_future_vocabulary=True,
    )
    resolved_params = _coerce_params(params)
    builder = _LoweringBuilder(document, resolved_params)
    builder.lower()
    state = builder.to_state()
    GRC9V3(params=resolved_params, state=state)
    return GRCL9V3LoweringResult(
        source=document,
        state=state,
        node_id_by_role=dict(builder.node_id_by_role),
        edge_id_by_role=dict(builder.edge_id_by_role),
    )


def _coerce_params(params: GRCParams | Mapping[str, Any] | None) -> GRCParams:
    if isinstance(params, GRCParams):
        return params
    config = {"dt": 0.1} if params is None else dict(params)
    return GRC9V3.from_config(config).get_params()


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
    def __init__(self, source: GRCL9V3SourceDocument, params: GRCParams) -> None:
        self.source = source
        self.params = params
        self.topology = PortGraphBackend()
        self.nodes: dict[int, GRC9V3NodeState] = {}
        self.port_edges: dict[int, PortEdge] = {}
        self.base_conductance: dict[int, float] = {}
        self.geometric_length: dict[int, float] = {}
        self.temporal_delay: dict[int, float] = {}
        self.flux_coupling: dict[int, float] = {}
        self.potential: dict[int, float] = {}
        self.node_id_by_role: dict[str, int] = {}
        self.edge_id_by_role: dict[str, int] = {}
        self.node_provenance: dict[str, dict[str, Any]] = {}
        self.edge_provenance: dict[str, dict[str, Any]] = {}
        self.motif_registry: dict[str, dict[str, Any]] = {}
        self.expected_saturated_node_ids: list[int] = []
        self.expected_tensor_hotspot_node_ids: list[int] = []
        self.expected_column_proxy_node_ids: list[int] = []
        self.expected_hessian_profile_node_ids: list[int] = []
        self.expected_expansion_region_ids: list[int] = []
        self.expected_choice_region_ids: list[int] = []
        self.expected_growth_locus_ids: list[int] = []
        self.expected_pressure_boundary_region_ids: list[int] = []
        self.front_growth_eligible_ports: dict[str, list[int]] = {}
        self.growth_parent_capacity_sources: dict[str, dict[str, Any]] = {}
        self.legacy_growth_locus_ids: list[int] = []
        self.expected_transport_region_ids: list[int] = []
        self.expected_quiescent_region_ids: list[int] = []
        self.expected_appendix_e_region_ids: list[int] = []
        self.bridge_edge_ids: list[int] = []
        self.sink_set: set[int] = set()
        self.basins: dict[int, set[int]] = {}
        self.hierarchy: dict[str | int, list[str | int]] = {}
        self.expansion_registry: dict[str, ExpansionRecord] = {}
        self.choice_registry: dict[str, Any] = {}
        self.collapse_registry: dict[str, Any] = {}
        self.anchors: list[tuple[str, GRCL9V3SourceConstruct]] = []

    def lower(self) -> None:
        self._validate_source_lowering_contract()
        spark = self._first(GRCL9V3HybridSparkRegion)
        transport = self._first(GRCL9V3TransportReroutingRegion)
        quiescent = self._first(GRCL9V3QuiescentHybridRegion)

        if spark is not None:
            self._lower_spark_family(spark)
        for choice in self._all(GRCL9V3ChoiceCollapseRegion):
            self._lower_choice(choice)
        for growth in self._all(GRCL9V3GrowthLocus):
            self._lower_growth(growth)
        if transport is not None:
            self._lower_transport(transport)
        if quiescent is not None:
            self._lower_quiescent(quiescent)
        if not self.anchors:
            raise ValueError("source document contains no lowerable Revision 1 construct")

        self._connect_component_anchors()
        self._validate_port_capacity()
        if not self._is_connected():
            raise ValueError("GRCL-9V3 lowering produced a disconnected graph")

    def to_state(self) -> GRC9V3State:
        budget_target = float(sum(node_state.coherence for node_state in self.nodes.values()))
        rng_seed = int(self.params.evolution.get("rng_seed", 0))
        return GRC9V3State(
            topology=self.topology,
            nodes=dict(self.nodes),
            port_edges=dict(self.port_edges),
            base_conductance=dict(self.base_conductance),
            geometric_length=dict(self.geometric_length),
            temporal_delay=dict(self.temporal_delay),
            flux_coupling=dict(self.flux_coupling),
            potential=dict(self.potential),
            sink_set=set(self.sink_set),
            basins={sink_id: set(members) for sink_id, members in self.basins.items()},
            hierarchy={key: list(value) for key, value in self.hierarchy.items()},
            expansion_registry=dict(self.expansion_registry),
            choice_registry=dict(self.choice_registry),
            collapse_registry=dict(self.collapse_registry),
            coarse_cache={},
            edge_label_computation_mode={
                "geometric_length": "grcl9v3_lowering_fixed",
                "temporal_delay": "grcl9v3_lowering_fixed",
                "flux_coupling": "grcl9v3_lowering_fixed",
            },
            edge_label_params={
                "source": "grcl9v3_lowering_v1",
                "hessian_backend": self._hessian_backend(),
            },
            step_index=0,
            time=0.0,
            budget_target=budget_target,
            remainder=0.0,
            rng_state=random.Random(rng_seed).getstate(),
            cached_quantities={
                "budget_target_source": "grcl9v3_lowering_initial_state_sum",
                "rng_seed_source": "grcl9v3_lowering_params",
                "rng_seed": rng_seed,
                "grcl9v3_source_schema_version": self.source.source_schema_version,
                "grcl9v3_source_fixture_name": self.source.fixture_name,
                "grcl9v3_manifest_entry_id": self.source.manifest_entry_id,
                "grcl9v3_projector_revision": GRCL9V3_PROJECTOR_REVISION,
                "grcl9v3_lowering_mode": GRCL9V3_LOWERING_MODE,
                "grcl9v3_provenance": {
                    "nodes": dict(sorted(self.node_provenance.items())),
                    "edges": dict(sorted(self.edge_provenance.items())),
                },
                "grcl9v3_motif_registry": self._final_motif_registry(),
                "grcl9v3_assembly_policy": {
                    "port_assignment_mode": "deterministic_role_ordered_ports",
                    "mass_partition_mode": "source_budget_partition",
                    "budget_preservation_policy": (
                        self.source.budget_policy.budget_preservation_policy
                    ),
                    "bridge_edge_policy": self.source.bridge_policy.edge_kind,
                    "bridge_conductance_hint": self.source.bridge_policy.conductance_hint,
                    "hessian_backend": self._hessian_backend(),
                    "growth_source_semantics": self._growth_semantics_status(),
                    "lowerer_revision": self.source.provenance_policy.lowerer_revision,
                },
                "grcl9v3_expected_saturated_node_ids": list(
                    self.expected_saturated_node_ids
                ),
                "grcl9v3_expected_tensor_hotspot_node_ids": list(
                    self.expected_tensor_hotspot_node_ids
                ),
                "grcl9v3_expected_column_proxy_node_ids": list(
                    self.expected_column_proxy_node_ids
                ),
                "grcl9v3_expected_hessian_profile_node_ids": list(
                    self.expected_hessian_profile_node_ids
                ),
                "grcl9v3_expected_expansion_region_ids": list(
                    self.expected_expansion_region_ids
                ),
                "grcl9v3_expected_choice_region_ids": list(
                    self.expected_choice_region_ids
                ),
                "grcl9v3_expected_growth_locus_ids": list(
                    self.expected_growth_locus_ids
                ),
                "grcl9v3_expected_pressure_boundary_region_ids": list(
                    self.expected_pressure_boundary_region_ids
                ),
                "grcl9v3_front_growth_eligible_ports": dict(
                    sorted(self.front_growth_eligible_ports.items())
                ),
                "grcl9v3_growth_parent_capacity_sources": dict(
                    sorted(self.growth_parent_capacity_sources.items())
                ),
                "grcl9v3_legacy_growth_locus_ids": list(self.legacy_growth_locus_ids),
                "grcl9v3_growth_semantics_status": self._growth_semantics_status(),
                "grcl9v3_expected_transport_region_ids": list(
                    self.expected_transport_region_ids
                ),
                "grcl9v3_expected_quiescent_region_ids": list(
                    self.expected_quiescent_region_ids
                ),
                "grcl9v3_expected_appendix_e_region_ids": list(
                    self.expected_appendix_e_region_ids
                ),
                "grcl9v3_bridge_edge_ids": list(self.bridge_edge_ids),
            },
            params_identity=self.params.params_hash,
        )

    def _lower_spark_family(self, spark: GRCL9V3HybridSparkRegion) -> None:
        active_degree = self._active_degree(spark)
        candidate = self._add_node(
            spark.candidate_region_id,
            spark,
            coherence=10.0 if active_degree >= 9 else 2.0,
            node_state=self._candidate_node_state(active_degree=active_degree),
        )
        if active_degree >= 9:
            self.expected_saturated_node_ids.append(candidate)

        hessian = self._first(GRCL9V3RowBasisHessianProfile)
        tensor = self._first(GRCL9V3HybridTensorProfile)
        column = self._first(GRCL9V3ColumnProxyFallbackProfile)
        for construct in (hessian, tensor, column):
            if construct is not None:
                self._attach_construct_to_node(construct, candidate, spark.candidate_region_id)
        if hessian is not None:
            self.expected_hessian_profile_node_ids.append(candidate)
        if column is not None:
            self.expected_column_proxy_node_ids.append(candidate)
        if tensor is not None and self._tensor_hotspot(tensor):
            self.expected_tensor_hotspot_node_ids.append(candidate)

        for port in range(1, active_degree + 1):
            neighbor = self._add_node(
                f"{spark.candidate_region_id}_port_{port}",
                spark,
                coherence=self._neighbor_coherence(port),
                node_state=GRC9V3NodeState(
                    coherence=self._neighbor_coherence(port),
                    basin_mass=self._neighbor_coherence(port),
                    basin_id=f"{spark.candidate_region_id}_support",
                    parent_id=spark.candidate_region_id,
                    depth=1,
                ),
            )
            self._connect(
                f"{spark.candidate_region_id}_edge_{port}",
                spark,
                candidate,
                port,
                neighbor,
                1,
                conductance=self._candidate_edge_conductance(port),
                motif_role="hybrid_spark_support",
            )
        bridge_anchor_role = (
            f"{spark.candidate_region_id}_port_1"
            if active_degree >= 9
            else spark.candidate_region_id
        )
        self.anchors.append((bridge_anchor_role, spark))

        expansion = self._first(GRCL9V3ExpansionRefinementRegion)
        if expansion is not None:
            self._attach_construct_to_node(expansion, candidate, spark.candidate_region_id)
            self.expected_expansion_region_ids.append(candidate)

        appendix = self._first(GRCL9V3AppendixEDivisionRegion)
        if appendix is not None:
            self._lower_appendix_e(appendix, candidate)

    def _lower_appendix_e(
        self,
        division: GRCL9V3AppendixEDivisionRegion,
        parent_node_id: int,
    ) -> None:
        daughter_a = self.node_id_by_role.get("candidate_port_1")
        daughter_b = self.node_id_by_role.get("candidate_port_2")
        reused_parent_neighbors = False
        if daughter_a is None or daughter_b is None:
            parent_neighbors: list[int] = []
            for edge_id in sorted(self.topology.incident_edge_ids(parent_node_id)):
                edge = self.port_edges[edge_id]
                neighbor_id = edge.node_v if edge.node_u == parent_node_id else edge.node_u
                if neighbor_id not in parent_neighbors:
                    parent_neighbors.append(neighbor_id)
            if len(parent_neighbors) >= 2:
                daughter_a, daughter_b = parent_neighbors[:2]
                reused_parent_neighbors = True
        if daughter_a is None or daughter_b is None:
            daughter_a = self._add_node(
                division.daughter_region_a,
                division,
                coherence=6.0,
            )
            daughter_b = self._add_node(
                division.daughter_region_b,
                division,
                coherence=6.0,
            )
        for node_id, role in (
            (parent_node_id, division.parent_region_id),
            (daughter_a, division.daughter_region_a),
            (daughter_b, division.daughter_region_b),
        ):
            self._attach_construct_to_node(division, node_id, role)
        self.expected_appendix_e_region_ids.extend([parent_node_id, daughter_a, daughter_b])
        self.sink_set.update({daughter_a, daughter_b})
        self.basins[daughter_a] = {daughter_a}
        self.basins[daughter_b] = {daughter_b}
        self.hierarchy[str(parent_node_id)] = [str(daughter_a), str(daughter_b)]

        if not reused_parent_neighbors:
            self._connect(
                f"{division.parent_region_id}_division_bridge",
                division,
                daughter_a,
                self._first_free_port(daughter_a),
                daughter_b,
                self._first_free_port(daughter_b),
                conductance=self._bridge_conductance(),
                motif_role="appendix_e_daughter_separator",
                edge_kind="bridge",
                bridge=True,
                bridge_role=self.source.bridge_policy.bridge_role,
            )

    def _lower_choice(self, choice: GRCL9V3ChoiceCollapseRegion) -> None:
        compatibility = str(
            dict(choice.compatibility_profile or {}).get("compatibility", "")
        )
        if choice.source_role == "negative_control" or compatibility == "low_contrast":
            center = self._add_node(choice.choice_region_id, choice, coherence=1.0)
            basin_a = self._add_node(choice.basin_region_a, choice, coherence=1.0)
            basin_b = self._add_node(choice.basin_region_b, choice, coherence=1.0)
            self._connect(
                f"{choice.choice_region_id}_stable_branch_a",
                choice,
                center,
                1,
                basin_a,
                1,
                conductance=0.25,
                motif_role="choice_negative_balanced_branch_a",
            )
            self._connect(
                f"{choice.choice_region_id}_stable_branch_b",
                choice,
                center,
                2,
                basin_b,
                1,
                conductance=0.25,
                motif_role="choice_negative_balanced_branch_b",
            )
            self.expected_choice_region_ids.append(center)
            self.anchors.append((choice.choice_region_id, choice))
            return

        center = self._add_node(
            choice.choice_region_id,
            choice,
            coherence=10.0,
            node_state=GRC9V3NodeState(
                coherence=10.0,
                gradient_row_basis=[1.0, 0.0, -1.0],
                signed_hessian_row_basis=[0.2, -0.2, 0.1],
                basin_mass=10.0,
                basin_id=choice.choice_region_id,
            ),
        )
        basin_a = self._add_node(choice.basin_region_a, choice, coherence=0.1)
        basin_b = self._add_node(choice.basin_region_b, choice, coherence=1.0)
        self._connect(
            f"{choice.choice_region_id}_to_{choice.basin_region_a}",
            choice,
            center,
            1,
            basin_a,
            1,
            conductance=1.0,
            motif_role="choice_high_compatibility_branch",
        )
        self._connect(
            f"{choice.choice_region_id}_to_{choice.basin_region_b}",
            choice,
            center,
            2,
            basin_b,
            1,
            conductance=1.0,
            motif_role="choice_low_compatibility_branch",
        )
        observer = self._add_node(
            f"{choice.choice_region_id}_detector",
            choice,
            coherence=10.0,
        )
        observer_sink_a = self._add_node(
            f"{choice.choice_region_id}_detector_sink_a",
            choice,
            coherence=1.0,
        )
        observer_sink_b = self._add_node(
            f"{choice.choice_region_id}_detector_sink_b",
            choice,
            coherence=1.0,
        )
        self._connect(
            f"{choice.choice_region_id}_detector_to_sink_a",
            choice,
            observer,
            1,
            observer_sink_a,
            1,
            conductance=1.0,
            motif_role="choice_detection_equal_branch_a",
        )
        self._connect(
            f"{choice.choice_region_id}_detector_to_sink_b",
            choice,
            observer,
            2,
            observer_sink_b,
            1,
            conductance=1.0,
            motif_role="choice_detection_equal_branch_b",
        )
        self._connect(
            f"{choice.choice_region_id}_detector_bridge",
            choice,
            center,
            3,
            observer,
            3,
            conductance=self._bridge_conductance(),
            motif_role="choice_detection_component_bridge",
            edge_kind="bridge",
            bridge=True,
            bridge_role=self.source.bridge_policy.bridge_role,
        )
        self.expected_choice_region_ids.extend([center, observer])
        self.sink_set.add(basin_a)
        self.sink_set.update({observer_sink_a, observer_sink_b})
        self.basins[basin_a] = {center, basin_a}
        self.basins[observer_sink_a] = {observer_sink_a}
        self.basins[observer_sink_b] = {observer_sink_b}
        seed_choice_registry = bool(
            dict(choice.compatibility_profile or {}).get("seed_choice_registry", True)
        )
        if seed_choice_registry:
            self.choice_registry[str(center)] = {
                "source_construct_id": choice.construct_id,
                "node_id": center,
                "viable_sink_ids": [str(basin_a), str(basin_b)],
                "collapse_target_region": choice.collapse_target_region,
                "compatibility_profile": dict(choice.compatibility_profile or {}),
            }
        self.anchors.append((choice.choice_region_id, choice))

    def _lower_growth(self, growth: GRCL9V3GrowthLocus) -> None:
        pressure_profile = dict(growth.outward_pressure_profile or {})
        relay_port = str(pressure_profile.get("geometry", "")) == "relay_port"
        parent_coherence = float(pressure_profile.get("parent_coherence", 3.0))
        support_coherence_high = float(
            pressure_profile.get("support_coherence", 9.0)
        )
        support_conductance_high = float(
            pressure_profile.get("support_conductance", 1.5)
        )
        support_flux_high = float(pressure_profile.get("support_flux", 1.0))
        parent = self._add_node(
            growth.parent_region_id,
            growth,
            coherence=parent_coherence,
            node_payload_extra={
                "grcl9v3_growth_semantics": growth.growth_semantics,
                "grcl9v3_front_capacity_source": growth.front_capacity_source,
                "grcl9v3_inactive_front_port": growth.inactive_parent_port,
            },
        )
        self.expected_growth_locus_ids.append(parent)
        if growth.front_capacity_source == "pressure_boundary":
            self.expected_pressure_boundary_region_ids.append(parent)
        self.growth_parent_capacity_sources[str(parent)] = {
            "construct_id": growth.construct_id,
            "growth_semantics": growth.growth_semantics,
            "front_capacity_source": growth.front_capacity_source,
            "front_source_construct_id": growth.front_source_construct_id,
            "inactive_parent_port": growth.inactive_parent_port,
            "propagate_child_front": bool(
                pressure_profile.get("propagate_child_front", False)
            ),
            "child_front_port": int(pressure_profile.get("child_front_port", 2)),
            "child_front_max_depth": int(
                pressure_profile.get("child_front_max_depth", 0)
            ),
            "child_front_activation_delay_steps": int(
                pressure_profile.get("child_front_activation_delay_steps", 0)
            ),
            "child_front_outlet": bool(
                pressure_profile.get("child_front_outlet", False)
            ),
            "child_front_outlet_port": int(
                pressure_profile.get("child_front_outlet_port", 3)
            ),
            "child_front_outlet_conductance": float(
                pressure_profile.get("child_front_outlet_conductance", 0.25)
            ),
            "child_front_outlet_coherence": float(
                pressure_profile.get("child_front_outlet_coherence", 0.0)
            ),
            "front_generation_depth": 0,
        }
        if growth.growth_semantics == "front_capacity":
            self.front_growth_eligible_ports[str(parent)] = [growth.inactive_parent_port]
        else:
            self.legacy_growth_locus_ids.append(parent)
        high_pressure = growth.lambda_birth >= 1.0 or relay_port
        active_ports = [port for port in (1, 2, 3) if port != growth.inactive_parent_port]
        for index, port in enumerate(active_ports[:2], start=1):
            support = self._add_node(
                f"{growth.parent_region_id}_support_{index}",
                growth,
                coherence=support_coherence_high if high_pressure else 0.5,
            )
            self._connect(
                f"{growth.parent_region_id}_support_edge_{index}",
                growth,
                parent,
                port,
                support,
                1,
                conductance=support_conductance_high if high_pressure else 0.25,
                flux_uv=support_flux_high if high_pressure else 0.0,
                motif_role="growth_outward_pressure_support",
            )
        if relay_port:
            self._add_relay_port_outlet(growth, parent, pressure_profile)
        self.anchors.append((growth.parent_region_id, growth))

    def _add_relay_port_outlet(
        self,
        growth: GRCL9V3GrowthLocus,
        parent: int,
        pressure_profile: Mapping[str, Any],
    ) -> None:
        """Attach a weak relay outlet that biases sink-then-source role flips."""

        outlet_coherence = float(pressure_profile.get("outlet_coherence", 0.25))
        outlet_conductance = float(pressure_profile.get("outlet_conductance", 0.15))
        outlet = self._add_node(
            f"{growth.parent_region_id}_relay_outlet",
            growth,
            coherence=outlet_coherence,
        )
        self._connect(
            f"{growth.parent_region_id}_relay_outlet_edge",
            growth,
            parent,
            self._first_free_port(parent),
            outlet,
            1,
            conductance=outlet_conductance,
            flux_uv=0.0,
            motif_role="relay_port_delayed_outlet",
        )

    def _lower_transport(self, transport: GRCL9V3TransportReroutingRegion) -> None:
        source = self._add_node(transport.source_region_id, transport, coherence=8.0)
        route = self._add_node(transport.route_region_id, transport, coherence=3.0)
        sink = self._add_node(transport.sink_region_id, transport, coherence=1.0)
        self.expected_transport_region_ids.extend([source, route, sink])
        self._connect(
            f"{transport.source_region_id}_to_{transport.route_region_id}",
            transport,
            source,
            1,
            route,
            1,
            conductance=2.5,
            flux_uv=1.0,
            motif_role="transport_preferred_corridor",
        )
        self._connect(
            f"{transport.route_region_id}_to_{transport.sink_region_id}",
            transport,
            route,
            2,
            sink,
            1,
            conductance=2.0,
            flux_uv=1.0,
            motif_role="transport_sink_corridor",
        )
        self.sink_set.add(sink)
        self.basins[sink] = {source, route, sink}
        self.anchors.append((transport.source_region_id, transport))

    def _lower_quiescent(self, quiescent: GRCL9V3QuiescentHybridRegion) -> None:
        center = self._add_node(quiescent.region_id, quiescent, coherence=1.0)
        support_a = self._add_node(f"{quiescent.region_id}_support_a", quiescent, coherence=1.0)
        support_b = self._add_node(f"{quiescent.region_id}_support_b", quiescent, coherence=1.0)
        self.expected_quiescent_region_ids.append(center)
        self._connect(
            f"{quiescent.region_id}_support_a",
            quiescent,
            center,
            1,
            support_a,
            1,
            conductance=0.2,
            motif_role="quiescent_support",
        )
        self._connect(
            f"{quiescent.region_id}_support_b",
            quiescent,
            center,
            2,
            support_b,
            1,
            conductance=0.2,
            motif_role="quiescent_support",
        )
        self.anchors.append((quiescent.region_id, quiescent))

    def _add_node(
        self,
        role: str,
        construct: GRCL9V3SourceConstruct,
        *,
        coherence: float,
        node_state: GRC9V3NodeState | None = None,
        node_payload_extra: Mapping[str, Any] | None = None,
    ) -> int:
        node_id = self.topology.add_node(
            grcl9v3_node_payload(
                construct=construct,
                motif_role=role,
                fixture_name=self.source.fixture_name,
                extra=node_payload_extra,
            )
        )
        self.node_id_by_role[role] = node_id
        state = node_state or GRC9V3NodeState(
            coherence=float(coherence),
            basin_mass=float(coherence),
            basin_id=role,
            depth=0,
        )
        self.nodes[node_id] = state
        self.potential[node_id] = float(state.coherence)
        self.node_provenance[str(node_id)] = {
            "source_construct_ids": [construct.construct_id],
            "source_construct_kinds": [construct.construct_kind],
            "motif_id": construct.motif_id,
            "motif_roles": [role],
            "ownership_tags": [construct.ownership],
            **dict(node_payload_extra or {}),
        }
        self._record_motif_node(construct, node_id, role)
        return node_id

    def _attach_construct_to_node(
        self,
        construct: GRCL9V3SourceConstruct,
        node_id: int,
        role: str,
    ) -> None:
        provenance = self.node_provenance[str(node_id)]
        for key, value in (
            ("source_construct_ids", construct.construct_id),
            ("source_construct_kinds", construct.construct_kind),
            ("motif_roles", role),
            ("ownership_tags", construct.ownership),
        ):
            values = list(provenance[key])
            if value not in values:
                values.append(value)
            provenance[key] = sorted(values)
        self._record_motif_node(construct, node_id, role)

    def _connect(
        self,
        role: str,
        construct: GRCL9V3SourceConstruct,
        node_a: int,
        port_a: int,
        node_b: int,
        port_b: int,
        *,
        conductance: float,
        motif_role: str,
        flux_uv: float = 0.0,
        edge_kind: str = "structural_support",
        bridge: bool = False,
        bridge_role: str | None = None,
    ) -> int:
        edge_id = self.topology.connect_ports(
            node_a,
            port_id_to_slot(port_a),
            node_b,
            port_id_to_slot(port_b),
            grcl9v3_edge_payload(
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
            flux_uv=float(flux_uv),
        )
        self.base_conductance[edge_id] = float(conductance)
        self.geometric_length[edge_id] = 1.0
        self.temporal_delay[edge_id] = 1.0
        self.flux_coupling[edge_id] = abs(float(flux_uv))
        self.edge_id_by_role[role] = edge_id
        self.edge_provenance[str(edge_id)] = {
            "source_construct_id": construct.construct_id,
            "source_construct_kind": construct.construct_kind,
            "motif_id": construct.motif_id,
            "motif_role": motif_role,
            "ownership": construct.ownership,
            "edge_kind": edge_kind,
            "bridge": bridge,
        }
        self._record_motif_edge(construct, edge_id, motif_role)
        if bridge:
            self.bridge_edge_ids.append(edge_id)
        return edge_id

    def _connect_component_anchors(self) -> None:
        if len(self.anchors) <= 1:
            return
        self._preflight_component_bridge_ports()
        for index, ((left_role, _), (right_role, construct)) in enumerate(
            zip(self.anchors, self.anchors[1:], strict=False),
            start=1,
        ):
            left_node = self.node_id_by_role[left_role]
            right_node = self.node_id_by_role[right_role]
            self._connect(
                f"component_bridge_{index}",
                construct,
                left_node,
                self._first_free_port(left_node),
                right_node,
                self._first_free_port(right_node),
                conductance=self._bridge_conductance(),
                motif_role="source_fixture_component_bridge",
                edge_kind="bridge",
                bridge=True,
                bridge_role="source_fixture_component_bridge",
            )

    def _active_degree(self, spark: GRCL9V3HybridSparkRegion) -> int:
        profile = spark.saturation_profile or {}
        value = profile.get("active_degree", 9)
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError("saturation_profile.active_degree must be an integer")
        if value < 1 or value > 9:
            raise ValueError("saturation_profile.active_degree must be in [1, 9]")
        return value

    def _candidate_node_state(self, *, active_degree: int) -> GRC9V3NodeState:
        hessian = self._first(GRCL9V3RowBasisHessianProfile)
        tensor = self._first(GRCL9V3HybridTensorProfile)
        tensor_hot = tensor is not None and self._tensor_hotspot(tensor)
        signed_hessian = [0.02, -0.01, 0.03] if tensor_hot else [0.4, 0.5, 0.6]
        if hessian is not None and hessian.hessian_backend == "weighted_least_squares":
            signed_hessian = [value * 0.75 for value in signed_hessian]
        gradient = [0.0, 1.0, 0.0] if tensor_hot else [0.1, 0.0, -0.1]
        return GRC9V3NodeState(
            coherence=10.0 if active_degree >= 9 else 2.0,
            gradient_row_basis=gradient,
            signed_hessian_row_basis=signed_hessian,
            net_flux_summary=[0.0, 0.0, 0.0],
            basin_mass=10.0 if active_degree >= 9 else 2.0,
            basin_id="candidate",
            depth=0,
        )

    def _candidate_edge_conductance(self, port: int) -> float:
        column = self._first(GRCL9V3ColumnProxyFallbackProfile)
        if column is not None and ((port - 1) % 3) + 1 == column.target_column:
            return 0.75 if column.cancellation_mode == "near_cancellation" else 1.25
        return 1.0

    def _neighbor_coherence(self, port: int) -> float:
        column = self._first(GRCL9V3ColumnProxyFallbackProfile)
        if column is not None and ((port - 1) % 3) + 1 == column.target_column:
            row = ((port - 1) // 3) + 1
            return {1: 9.9999, 2: 10.0, 3: 10.0001}[row]
        if column is not None:
            row = ((port - 1) // 3) + 1
            return {1: 10.00005, 2: 10.0, 3: 9.99995}[row]
        return 10.0

    def _tensor_hotspot(self, tensor: GRCL9V3HybridTensorProfile) -> bool:
        profile = tensor.tensor_profile or {}
        return (
            str(profile.get("row_mismatch", "")) == "high"
            or str(profile.get("tensor_mode", "")) == "anisotropic"
        )

    def _first_free_port(self, node_id: int) -> int:
        for port in range(1, 10):
            if self.topology.port_edge_id(node_id, port_id_to_slot(port)) is None:
                return port
        raise ValueError(f"node {node_id} has no free GRC9V3 ports")

    def _validate_port_capacity(self) -> None:
        for node_id in self.topology.iter_live_node_ids():
            occupied = tuple(self.topology.incident_edge_ids(node_id))
            if len(occupied) > 9:
                raise ValueError(f"node {node_id} exceeds nine-port capacity")
        budget_target = float(sum(node_state.coherence for node_state in self.nodes.values()))
        if budget_target < 0.0:
            raise ValueError("lowered budget target must be non-negative")

    def _preflight_component_bridge_ports(self) -> None:
        for left_role, right_role in zip(
            (role for role, _ in self.anchors),
            (role for role, _ in self.anchors[1:]),
            strict=False,
        ):
            for role in (left_role, right_role):
                node_id = self.node_id_by_role[role]
                if all(
                    self.topology.port_edge_id(node_id, port_id_to_slot(port)) is not None
                    for port in range(1, 10)
                ):
                    raise ValueError(
                        f"component bridge anchor {role!r} has no free GRC9V3 port"
                    )

    def _validate_source_lowering_contract(self) -> None:
        if not self.source.constructs:
            raise ValueError("source document contains no constructs")
        non_executable = [
            construct.construct_id
            for construct in self.source.constructs
            if not construct.executable
        ]
        if non_executable:
            raise ValueError(
                "GRCL-9V3 lowerer rejects non-executable source constructs: "
                + ", ".join(sorted(non_executable))
            )
        kind_counts = Counter(construct.construct_kind for construct in self.source.constructs)
        repeated_allowed = {"choice_collapse_region", "growth_locus"}
        duplicates = sorted(
            kind
            for kind, count in kind_counts.items()
            if count > 1 and kind not in repeated_allowed
        )
        if duplicates:
            raise ValueError(
                "GRCL-9V3 Revision 1 lowerer accepts repeated constructs only for "
                "growth_locus and choice_collapse_region; unsupported repeats: "
                + ", ".join(duplicates)
            )

    def _hessian_backend(self) -> str:
        hessian = self._first(GRCL9V3RowBasisHessianProfile)
        if hessian is not None:
            return hessian.hessian_backend
        return "row_basis_diagonal"

    def _bridge_conductance(self) -> float:
        return float(
            0.01
            if self.source.bridge_policy.conductance_hint is None
            else self.source.bridge_policy.conductance_hint
        )

    def _growth_semantics_status(self) -> str:
        if self.legacy_growth_locus_ids:
            return "legacy_diagnostic"
        if self.front_growth_eligible_ports:
            return "front_capacity"
        return "none"

    def _record_motif_node(
        self,
        construct: GRCL9V3SourceConstruct,
        node_id: int,
        role: str,
    ) -> None:
        record = self.motif_registry.setdefault(
            construct.motif_id,
            {
                "node_ids": set(),
                "edge_ids": set(),
                "source_construct_ids": set(),
                "motif_roles": set(),
                "ownership_tags": set(),
            },
        )
        record["node_ids"].add(node_id)
        record["source_construct_ids"].add(construct.construct_id)
        record["motif_roles"].add(role)
        record["ownership_tags"].add(construct.ownership)

    def _record_motif_edge(
        self,
        construct: GRCL9V3SourceConstruct,
        edge_id: int,
        role: str,
    ) -> None:
        record = self.motif_registry.setdefault(
            construct.motif_id,
            {
                "node_ids": set(),
                "edge_ids": set(),
                "source_construct_ids": set(),
                "motif_roles": set(),
                "ownership_tags": set(),
            },
        )
        record["edge_ids"].add(edge_id)
        record["source_construct_ids"].add(construct.construct_id)
        record["motif_roles"].add(role)
        record["ownership_tags"].add(construct.ownership)

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
                "ownership_tags": sorted(raw["ownership_tags"]),
            }
        return result

    def _first(self, cls: type[Any]) -> Any | None:
        for construct in self.source.constructs:
            if isinstance(construct, cls):
                return construct
        return None

    def _all(self, cls: type[Any]) -> tuple[Any, ...]:
        return tuple(
            construct for construct in self.source.constructs if isinstance(construct, cls)
        )

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
    "GRCL9V3LoweringResult",
    "lower_grcl9v3_fixture_by_name",
    "lower_grcl9v3_source_to_grc9v3_state",
]
