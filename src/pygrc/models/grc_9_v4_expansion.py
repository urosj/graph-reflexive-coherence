"""Pure D11-G9-P4a allocation from a bound source and a closed request.

This mechanical plan is not an admitted numerical target or a committed event.
The lifecycle owner must supply its actual post-beat source identity, resolve
the target profile/history policies, transfer both live and reset authority,
readmit the target and publish atomically. No caller target allocation is used.
"""

from __future__ import annotations

from collections import deque
from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from typing import Any, ClassVar, Literal

from .grc_9_v4_topology import (
    GRC9V4PortEdge,
    GRC9V4PortEndpoint,
    GRC9V4PortGraph,
    port_to_row_column,
    row_column_to_port,
)
from .grc_v4_codec import (
    JSONValue,
    canonical_json_bytes,
    payload_identity,
    validate_payload,
)
from .grc_v4_exact import exact_number
from .grc_v4_geometry import (
    GRCV4Graph,
    GRCV4ReferenceGeometry,
    NodeId,
    _computed,
    _node_id,
)
from .grc_v4_profile import (
    GRCV4ProfileTemplate,
    _Record,
    resolve_profile,
    resolve_profile_template,
)
from .grc_v4_state import FrozenJSONMap, GRCV4AuthoritativeState, _number


class GRC9V4ExpansionError(ValueError):
    """Semantic planner rejection; later lifecycle code owns its receipt."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def canonical_module_node_count(target_effective_degree: int) -> int:
    """Exact capacity arithmetic without floating ceil or graph allocation."""
    if type(target_effective_degree) not in (int, float):
        raise TypeError("target_effective_degree must be a JSON integer")
    number = _number(target_effective_degree)
    if not number.is_integer() or number < 9:
        raise ValueError("target_effective_degree must be an integer at least 9")
    return max(4, (int(number) + 4) // 7)


@dataclass(frozen=True, slots=True, eq=False)
class GRC9ExpansionPolicy(_Record):
    SCHEMA: ClassVar[str] = "expansion_policy"
    schema_version: Literal["grc9v4-expansion-policy-v1"]
    policy_id: Literal["grc9v4_axis_preserving_chiral_same_port_expansion_v1"]
    boundary_policy: Literal["reserve_exact_old_port_map_first"]
    primary_spine_policy: Literal["chiral_latin_same_port_transversal"]
    recursive_tree_policy: Literal["creation_order_bfs_same_port_rotor"]
    stable_id_policy: Literal["grc_event_sha256_role_grammar_v1"]
    bond_seed: float
    resource_distribution_schema: Literal["event_supplied_simplex3"]
    source_self_loop_policy: Literal["reject_before_target_construction"]

    def __post_init__(self) -> None:
        _Record.__post_init__(self)
        object.__setattr__(self, "bond_seed", _number(self.bond_seed))

    @property
    def identity(self) -> str:
        return payload_identity(
            "expansion_policy_identity_payload",
            {
                "schema_version": "grc9v4-expansion-policy-identity-v1",
                "policy": self.to_payload(),
            },
        )


@dataclass(frozen=True, slots=True, eq=False)
class GRC9V4ExpansionRequestInput(_Record):
    """Closed wire input; null chirality remains a named semantic rejection.

    JSON integer-valued floats normalize under the existing V4 convention.
    History digest consistency and exact simplex admission belong to planning,
    so schema-valid but inconsistent inputs can receive semantic failure codes.
    """

    SCHEMA: ClassVar[str] = "expansion_event_request_input"
    INTEGER_FIELDS: ClassVar[tuple[str, ...]] = ("target_effective_degree",)
    schema_version: Literal["grc9v4-expansion-event-request-input-v1"]
    operation_id: str
    source_state_digest: str
    source_graph_digest: str
    source_node_id: NodeId
    target_profile_template_id: str
    target_specialization_id: str
    expansion_policy_id: Literal["grc9v4_axis_preserving_chiral_same_port_expansion_v1"]
    target_effective_degree: int
    module_chirality: Literal[-1, 1] | None
    growth_phase: Literal[1, 2, 3] | None
    resource_distribution: tuple[float, float, float]
    history_policy: Mapping[str, object]
    expected_event_id: str | None
    expected_target_graph_digest: str | None

    def __post_init__(self) -> None:
        _Record.__post_init__(self)
        object.__setattr__(self, "source_node_id", _node_id(self.source_node_id))
        for name in ("module_chirality", "growth_phase"):
            value = getattr(self, name)
            if value is not None:
                object.__setattr__(self, name, int(value))
        object.__setattr__(
            self,
            "resource_distribution",
            tuple(_number(x) for x in self.resource_distribution),
        )


def _admit_request(request: GRC9V4ExpansionRequestInput) -> tuple[int, tuple[int, ...]]:
    count = canonical_module_node_count(request.target_effective_degree)
    quotient, remainder = divmod(count - 4, 3)
    if request.module_chirality is None:
        raise GRC9V4ExpansionError("module_chirality_required")
    if remainder and request.growth_phase is None:
        raise GRC9V4ExpansionError("module_growth_phase_required")
    if not remainder and request.growth_phase is not None:
        raise GRC9V4ExpansionError("reject_noncanonical_inactive_growth_phase")
    if (
        sum((exact_number(x) for x in request.resource_distribution), exact_number())
        != 1
    ):
        raise GRC9V4ExpansionError("invalid_resource_distribution")
    for channel in ("candidate", "carrier"):
        digest = payload_identity(
            "history_channel_policy_identity_payload",
            {
                "schema_version": "grcv4-history-channel-policy-identity-v1",
                "policy": request.history_policy[channel],
            },
        )
        if digest != request.history_policy[channel + "_history_policy_digest"]:
            raise GRC9V4ExpansionError("history_policy_digest_mismatch")
    extras = [quotient] * 3
    if remainder:
        assert request.growth_phase is not None
        for offset in range(remainder):
            extras[
                (request.growth_phase - 1 + offset * request.module_chirality) % 3
            ] += 1
    return count, tuple(extras)


def _identity_payload(
    request: GRC9V4ExpansionRequestInput, policy: GRC9ExpansionPolicy, count: int
) -> dict[str, JSONValue]:
    data = request.to_payload()
    return validate_payload(
        "expansion_event_identity_payload",
        {
            "schema_version": "grc9v4-expansion-event-identity-v1",
            **{
                name: data[name]
                for name in (
                    "source_state_digest",
                    "source_graph_digest",
                    "source_node_id",
                    "target_profile_template_id",
                    "target_specialization_id",
                    "target_effective_degree",
                    "module_chirality",
                    "growth_phase",
                    "expansion_policy_id",
                    "resource_distribution",
                )
            },
            "canonical_module_node_count": count,
            "expansion_policy_digest": policy.identity,
            "bond_seed": policy.bond_seed,
            **{
                channel + "_history_policy_digest": request.history_policy[
                    channel + "_history_policy_digest"
                ]
                for channel in ("candidate", "carrier")
            },
        },
    )


def _allocate(
    source: GRC9V4PortGraph,
    source_node: NodeId,
    event_id: str,
    chirality: int,
    extras: tuple[int, ...],
) -> tuple[GRC9V4PortGraph, tuple[str, ...], tuple[str, ...]]:
    """Reserve first, then consume a FIFO of each branch's free rotor slots.

    Appending a child's slots after all existing slots is exactly the specified
    creation-order parent rule, without rescanning the growing branch. The
    primary satellite has one free slot; every child consumes one and adds two.
    """
    core = event_id + "/core"
    satellites = tuple(event_id + f"/satellite/{b}" for b in (1, 2, 3))
    nodes = [core, *satellites]
    edges = []
    occupied: set[GRC9V4PortEndpoint] = set()
    internal_ids = []
    old_nodes, old_ids = set(source.live_node_ids), {e.edge_id for e in source.edges}

    def add(edge: GRC9V4PortEdge) -> None:
        if edge.tail in occupied or edge.head in occupied or edge.tail == edge.head:
            raise GRC9V4ExpansionError("target_port_occupancy_conflict")
        occupied.update((edge.tail, edge.head))
        edges.append(edge)

    def internal(
        edge_id: str, parent: str, child: str, port: int, kind: Literal["spine", "tree"]
    ) -> None:
        if edge_id in old_ids:
            raise GRC9V4ExpansionError("role_id_collision")
        add(
            GRC9V4PortEdge(
                edge_id,
                kind,
                GRC9V4PortEndpoint(parent, port),
                GRC9V4PortEndpoint(child, port),
            )
        )
        internal_ids.append(edge_id)

    # All nine boundary incidences, including the blocking primary rotor ports,
    # are reserved before a single new internal edge is constructed.
    for edge in source.edges:
        endpoints = []
        for endpoint in (edge.tail, edge.head):
            if endpoint.node_id == source_node:
                column = port_to_row_column(endpoint.port)[1]
                endpoint = GRC9V4PortEndpoint(satellites[column - 1], endpoint.port)
            endpoints.append(endpoint)
        add(GRC9V4PortEdge(edge.edge_id, edge.kind, *endpoints))

    width = max(1, len(str(sum(extras))))
    for branch, satellite in enumerate(satellites, 1):
        incoming_column = 1 + (branch - 1 + chirality) % 3
        incoming_port = row_column_to_port(branch, incoming_column)
        internal(
            event_id + f"/internal/{branch}", core, satellite, incoming_port, "spine"
        )

        def rotor(node: str, column: int, row: int = branch) -> list[tuple[str, int]]:
            ports = [
                row_column_to_port(row, 1 + (column - 1 + turn) % 3)
                for turn in (chirality, -chirality)
            ]
            return [
                (node, port)
                for port in ports
                if GRC9V4PortEndpoint(node, port) not in occupied
            ]

        available = deque(rotor(satellite, incoming_column))
        for ordinal in range(1, extras[branch - 1] + 1):
            parent, port = available.popleft()
            suffix = f"extra/{branch}/{ordinal:0{width}d}"
            child = event_id + "/" + suffix
            nodes.append(child)
            internal(event_id + "/internal/" + suffix, parent, child, port, "tree")
            available.extend(rotor(child, port_to_row_column(port)[1]))
    if any(node in old_nodes for node in nodes):
        raise GRC9V4ExpansionError("role_id_collision")

    # Fixed typed/JCS scalar order for nodes and UTF-16 order for stable edge IDs.
    # Input array order still participates in the source digest and event ID.
    target_nodes = sorted(
        [*(n for n in source.live_node_ids if n != source_node), *nodes],
        key=lambda n: (type(n) is str, canonical_json_bytes(n)),
    )
    target_edges = sorted(edges, key=lambda e: e.edge_id.encode("utf-16-be"))
    target = GRC9V4PortGraph(tuple(target_nodes), tuple(target_edges))
    return target, tuple(nodes), tuple(internal_ids)


@dataclass(frozen=True, slots=True)
class GRC9V4ExpansionPlan:
    """Derived immutable mechanical plan; every construction revalidates inputs.

    source_state_digest is supplied by the future lifecycle receiver, not
    authenticated by this detached record. Target graph, event ID and reference
    seeds are computed here; none is accepted as caller authority. Expected
    digests only reject mismatches. No resource/history/receipt mutation occurs.
    """

    source_graph: GRC9V4PortGraph
    source_state_digest: str
    request: GRC9V4ExpansionRequestInput
    policy: GRC9ExpansionPolicy
    event_id: str = field(init=False)
    target_graph: GRC9V4PortGraph = field(init=False)
    module_node_ids: tuple[str, ...] = field(init=False)
    internal_edge_ids: tuple[str, ...] = field(init=False)
    branch_extra_counts: tuple[int, ...] = field(init=False)

    def __post_init__(self) -> None:
        if type(self.source_graph) is not GRC9V4PortGraph:
            raise TypeError("expected an admitted port graph")
        if type(self.request) is not GRC9V4ExpansionRequestInput:
            raise TypeError("expected a closed expansion request input")
        if type(self.policy) is not GRC9ExpansionPolicy:
            raise TypeError("expected a closed expansion policy")
        graph, request, policy = (
            replace(self.source_graph),
            replace(self.request),
            replace(self.policy),
        )
        if type(self.source_state_digest) is not str:
            raise TypeError("source_state_digest must be a JSON string")
        if self.source_state_digest != request.source_state_digest:
            raise GRC9V4ExpansionError("source_state_digest_mismatch")
        if graph.graph_digest != request.source_graph_digest:
            raise GRC9V4ExpansionError("source_graph_digest_mismatch")
        if request.source_node_id not in graph.live_node_ids:
            raise GRC9V4ExpansionError("source_node_not_live")
        incident = [
            e
            for e in graph.edges
            if request.source_node_id in (e.tail.node_id, e.head.node_id)
        ]
        if any(e.tail.node_id == e.head.node_id for e in incident):
            raise GRC9V4ExpansionError("source_self_loop_unsupported")
        if len(incident) != 9:
            raise GRC9V4ExpansionError("source_not_saturated")
        count, extras = _admit_request(request)
        payload = _identity_payload(request, policy, count)
        event_id = payload_identity("expansion_event_identity_payload", payload)
        if (
            request.expected_event_id is not None
            and request.expected_event_id != event_id
        ):
            raise GRC9V4ExpansionError("expected_event_id_mismatch")
        assert request.module_chirality is not None
        target, nodes, edges = _allocate(
            graph, request.source_node_id, event_id, request.module_chirality, extras
        )
        if (
            request.expected_target_graph_digest is not None
            and request.expected_target_graph_digest != target.graph_digest
        ):
            raise GRC9V4ExpansionError("expected_target_graph_digest_mismatch")
        for name, value in (
            ("source_graph", graph),
            ("request", request),
            ("policy", policy),
            ("event_id", event_id),
            ("target_graph", target),
            ("module_node_ids", nodes),
            ("internal_edge_ids", edges),
            ("branch_extra_counts", extras),
        ):
            object.__setattr__(self, name, value)

    @property
    def canonical_module_node_count(self) -> int:
        return len(self.module_node_ids)

    @property
    def external_capacity(self) -> int:
        return 7 * self.canonical_module_node_count + 2

    def event_identity_payload(self) -> dict[str, JSONValue]:
        return _identity_payload(
            self.request, self.policy, self.canonical_module_node_count
        )

    def admitted_request_payload(self) -> dict[str, JSONValue]:
        data = self.request.to_payload()
        data["schema_version"] = "grc9v4-expansion-event-request-v1"
        return validate_payload("expansion_event_request", data)

    def internal_reference_seeds(self) -> dict[str, tuple[float, float]]:
        """Detached edge -> (positive reference weight, zero reference current)."""
        return {
            edge_id: (self.policy.bond_seed, 0.0) for edge_id in self.internal_edge_ids
        }


def cos_profile_template(reference: GRCV4ReferenceGeometry) -> GRCV4ProfileTemplate:
    """The single C reference rebuild policy, bound to the full source profile."""
    return resolve_profile_template(
        {
            "schema_version": "grcv4-profile-template-v1",
            "source_complete_profile_id": reference.profile.complete_profile_id,
            "profile_family_id": "C_OS",
            "topology_dependent_map_policy_id": "preserve_old_stable_edges_seed_new_internal_edges_v1",
            "geometry_reference_policy_id": "rebuild_reference_hodge_from_target_W_C_tr_v1",
        },
        source=reference.profile,
    )


@dataclass(frozen=True, slots=True)
class GRC9V4COSExpansion:
    """Pure unit-measure C_OS reconstruction with zero structural K4 base.

    The bounded adapter transports no W_A or Z_4. Both resource roles use
    one exact affine map, rounded once per output; numerical charge/current
    admission and publication remain with the transaction owner. Nonzero
    structural bases require their own admitted transport policy.
    """

    plan: GRC9V4ExpansionPlan
    source: GRCV4ReferenceGeometry
    target: GRCV4ReferenceGeometry = field(init=False)

    def __post_init__(self) -> None:
        if (
            type(self.plan) is not GRC9V4ExpansionPlan
            or type(self.source) is not GRCV4ReferenceGeometry
        ):
            raise TypeError("C_OS expansion requires a plan and reference geometry")
        plan, source = replace(self.plan), replace(self.source)
        if source.graph.port_graph != plan.source_graph:
            raise ValueError("reference does not derive from the source port owner")
        if source.profile.identity_payload.profile_family_id != "C_OS":
            raise ValueError("C_OS expansion requires C_OS")
        if any(x != 0 for row in source.K4_base for x in row):
            raise ValueError(
                "C_OS expansion currently requires zero structural K4 base"
            )
        template = cos_profile_template(source)
        if template.profile_template_id != plan.request.target_profile_template_id:
            raise ValueError("target profile template mismatch")
        for subject, policy_id, disposition in (
            ("candidate", "candidate_c_rederive_no_history_v1", "rederived"),
            ("carrier", "carrier_not_applicable_v1", "not_applicable"),
        ):
            expected = {
                "schema_version": "grcv4-history-channel-policy-v1",
                "subject": subject,
                "policy_id": policy_id,
                "disposition": disposition,
                "source_history_digest": None,
                "target_initializer_id": None,
                "information_loss": "none",
            }
            if canonical_json_bytes(
                plan.request.history_policy[subject]
            ) != canonical_json_bytes(expected):
                raise ValueError("C_OS requires rederived C and absent carrier history")
        graph = GRCV4Graph.from_port_graph(plan.target_graph)
        weights = {
            **source.edge_weights.to_dict(),
            **{edge: seed[0] for edge, seed in plan.internal_reference_seeds().items()},
        }
        size = len(graph.live_edge_ids)
        base = tuple((0.0,) * size for _ in range(size))
        params: Any = source.profile.params_resolved.to_payload()
        identity: Any = source.profile.identity_payload.to_payload()
        params["candidate"].update(
            W_C_tr=weights,
            W_C_tr_content_digest=payload_identity(
                "wctr_identity_payload",
                {"schema_version": "grcv4-wctr-identity-v1", "W_C_tr": weights},
            ),
        )
        params["geometry"].update(
            K4_base_digest=payload_identity(
                "k4_identity_payload",
                {
                    "schema_version": "grcv4-k4-identity-v1",
                    "K4_base": [list(row) for row in base],
                },
            ),
            reference_hodge_digest=payload_identity(
                "reference_hodge_identity_payload",
                {
                    "schema_version": "grcv4-reference-hodge-identity-v1",
                    "edge_weights": weights,
                },
            ),
        )
        identity["params_hash"] = payload_identity("resolved_params", params)
        target = GRCV4ReferenceGeometry(
            graph,
            resolve_profile(params, identity),
            source.context,
            base,
            FrozenJSONMap(weights),
        )
        object.__setattr__(self, "plan", plan)
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "target", target)

    def resource_transform_payload(self) -> dict[str, JSONValue]:
        source, target, request = (
            self.plan.source_graph,
            self.plan.target_graph,
            self.plan.request,
        )
        satellites: dict[NodeId, float] = {
            self.plan.event_id + f"/satellite/{b}": request.resource_distribution[b - 1]
            for b in (1, 2, 3)
        }
        coefficients = [
            satellites.get(node, 0.0)
            if old == request.source_node_id
            else float(node == old)
            for node in target.live_node_ids
            for old in source.live_node_ids
        ]
        return validate_payload(
            "resource_event_transform",
            {
                "schema_version": "grcv4-resource-event-transform-v1",
                "policy_id": "grc9v4_source_to_primary_satellite_affine_v1",
                "source_vertex_ids": list(source.live_node_ids),
                "target_vertex_ids": list(target.live_node_ids),
                "row_major_coefficients": coefficients,
                "target_increment": [0.0] * len(target.live_node_ids),
            },
        )

    def transfer(self, state: GRCV4AuthoritativeState) -> GRCV4AuthoritativeState:
        if (
            type(state) is not GRCV4AuthoritativeState
            or state.W_A is not None
            or state.Z_4 is not None
        ):
            raise ValueError("C_OS authority has neither W_A nor Z_4")
        width = len(self.plan.source_graph.live_node_ids)
        if len(state.C) != width:
            raise ValueError("source resource coordinates mismatch")
        transform: Any = self.resource_transform_payload()
        coefficients = transform["row_major_coefficients"]
        values = tuple(
            _computed(
                float(
                    sum(
                        (
                            exact_number(a) * exact_number(c)
                            for a, c in zip(
                                coefficients[i : i + width], state.C, strict=True
                            )
                        ),
                        exact_number(),
                    )
                )
            )
            for i in range(0, len(coefficients), width)
        )
        return GRCV4AuthoritativeState(values, None, None)
