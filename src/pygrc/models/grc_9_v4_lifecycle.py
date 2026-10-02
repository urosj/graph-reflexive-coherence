"""P9-8.1c fresh mechanical candidate detection, not a lifecycle owner.

The reviewed module owner also has later transaction/completion duties. Only
the baseline candidate predicate is implemented here. No graph mutation,
event emission, completed spark, hierarchy update or capability is implied.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, replace
from typing import ClassVar, Literal

from .grc_9_v4_topology import (
    PORT_COUNT,
    GRC9V4PostbeatRows,
    GRC9V4RowSummary,
    _coordinate,
)
from .grc_v4_exact import exact_number
from .grc_v4_geometry import NodeId, _identity, _ordered
from .grc_v4_profile import _Record
from .grc_v4_state import _number


@dataclass(frozen=True, slots=True, eq=False)
class GRC9SparkPolicy(_Record):
    """Closed specification policy; schema recognition is not lane support.

    Child stabilization is detached policy content only. Its presence neither
    runs a completion rule nor enables a completed-spark capability.
    """

    SCHEMA: ClassVar[str] = "spark_policy"
    schema_version: Literal["grc9v4-spark-policy-v1"]
    lane: Literal["current_hybrid_signed_hessian", "grc9v3_column_h_assisted"]
    gradient_tolerance: float
    basin_hessian_tolerance: float
    spark_hessian_tolerance: float
    child_stabilization: Mapping[str, object] | None

    def __post_init__(self) -> None:
        _Record.__post_init__(self)
        for name in (
            "gradient_tolerance",
            "basin_hessian_tolerance",
            "spark_hessian_tolerance",
        ):
            object.__setattr__(self, name, _number(getattr(self, name)))


class UnsupportedGRC9SparkLane(ValueError):
    """A declared optional lane has no admitted executable policy here."""


def _baseline_policy(value: GRC9SparkPolicy) -> GRC9SparkPolicy:
    if type(value) is not GRC9SparkPolicy:
        raise TypeError("candidate detection requires GRC9SparkPolicy")
    policy = GRC9SparkPolicy.from_payload(value.to_payload())
    if policy.lane != "current_hybrid_signed_hessian":
        raise UnsupportedGRC9SparkLane(
            "grc9v3_column_h_assisted requires separately bound executable controls"
        )
    return policy


@dataclass(frozen=True, slots=True)
class GRC9V4CandidateAssessment:
    """Immutable derived node diagnostics, not an event or admission token.

    Local construction validates values but cannot establish graph provenance.
    Detection constructs these from the admitted port owner and fresh rows;
    it never consumes externally supplied assessments as candidate evidence.
    """

    row: GRC9V4RowSummary
    occupied_ports: tuple[int, ...]
    policy: GRC9SparkPolicy

    def __post_init__(self) -> None:
        if type(self.row) is not GRC9V4RowSummary:
            raise TypeError("assessment requires a fixed-row summary")
        object.__setattr__(self, "row", replace(self.row))
        ports = tuple(
            _coordinate(p, PORT_COUNT, "port") for p in _ordered(self.occupied_ports)
        )
        if len(set(ports)) != len(ports):
            raise ValueError("duplicate occupied port")
        object.__setattr__(self, "occupied_ports", tuple(sorted(ports)))
        object.__setattr__(self, "policy", _baseline_policy(self.policy))

    @property
    def node_id(self) -> NodeId:
        return self.row.node_id

    @property
    def saturated(self) -> bool:
        return len(self.occupied_ports) == PORT_COUNT

    @property
    def small_gradient(self) -> bool:
        # Compare the norm without rounding a square root, overflowing a square,
        # or underflowing a subnormal. These are the fresh .b row coordinates,
        # not a newly chosen unrounded differential backend.
        squared = sum((exact_number(x) ** 2 for x in self.row.gradient), exact_number())
        return bool(squared < exact_number(self.policy.gradient_tolerance) ** 2)

    @property
    def minimum_signed_hessian(self) -> float:
        value = min(self.row.hessian_sign * x for x in self.row.gradient)
        return 0.0 if value == 0 else value

    @property
    def hessian_degenerate(self) -> bool:
        return self.minimum_signed_hessian < self.policy.spark_hessian_tolerance

    @property
    def basin_seed(self) -> bool:
        return self.small_gradient and (
            self.minimum_signed_hessian > self.policy.basin_hessian_tolerance
        )

    @property
    def is_candidate(self) -> bool:
        return self.saturated and self.small_gradient and self.hessian_degenerate


@dataclass(frozen=True, slots=True)
class GRC9V4CandidateDetection:
    """Baseline detection from detached fresh-postbeat numerical inputs.

    Native lifecycle wiring must supply the actual committed state and current,
    fixing sign and policy through the combined specialization identity. Like
    the row input record, this boundary validates declared content and stage,
    not the caller's chronology. Every assessment recomputes the row backend;
    no supplied summary, cache, previous verdict or candidate list is accepted.
    """

    postbeat: GRC9V4PostbeatRows
    policy: GRC9SparkPolicy

    def __post_init__(self) -> None:
        if type(self.postbeat) is not GRC9V4PostbeatRows:
            raise TypeError("candidate detection requires GRC9V4PostbeatRows")
        object.__setattr__(self, "postbeat", replace(self.postbeat))
        object.__setattr__(self, "policy", _baseline_policy(self.policy))

    @property
    def identity(self) -> str:
        """Input binding for these candidate diagnostics, not scientific state."""
        return _identity(
            "grc9v4-candidate-detection-sha256",
            {
                "descriptor_version": "grc9v4-baseline-candidate-detection-v1",
                "row_inputs_identity": self.postbeat.identity,
                "spark_policy": self.policy.to_payload(),
            },
        )

    def assess(self) -> tuple[GRC9V4CandidateAssessment, ...]:
        graph = self.postbeat.port_graph
        ports: dict[NodeId, list[int]] = {node: [] for node in graph.live_node_ids}
        for edge in graph.edges:
            ports[edge.tail.node_id].append(edge.tail.port)
            ports[edge.head.node_id].append(edge.head.port)
        return tuple(
            GRC9V4CandidateAssessment(row, tuple(ports[row.node_id]), self.policy)
            for row in self.postbeat.evaluate()
        )

    def candidate_node_ids(self) -> tuple[NodeId, ...]:
        return tuple(row.node_id for row in self.assess() if row.is_candidate)
