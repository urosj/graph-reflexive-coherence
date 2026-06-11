"""LGRC9V3 proper-time identity persistence evidence helpers."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
import heapq
import math
from typing import Any, Final

from pygrc.core import (
    digest_canonical_data,
    EdgeId,
    GRCEvent,
    InvalidParamsError,
    InvalidStateTransitionError,
    NodeId,
    SnapshotCompatibilityError,
)

from .grc_9_ports import port_to_rc
from .grc_9_v3_state import GRC9V3State

from .lgrc_9_v3_contract import *
from .lgrc_9_v3_topology import *


@dataclass(frozen=True)
class LGRC9V3ProperTimeIdentityPersistenceEvaluation:
    """Sink-local proper-time persistence evidence.

    This is an evaluator artifact, not an identity-acceptance event. A passing
    evaluation may be consumed by a later explicit event emitter, but this
    object itself must not emit identity acceptance.
    """

    evaluation_id: str
    topology_event_id: str
    topology_event_kind: str
    source_topology_event_ids: tuple[str, ...]
    scheduler_event_index: int
    checkpoint_index: int
    event_time_key: float
    sink_node_id: NodeId
    lineage_id: str
    basin_node_ids: tuple[NodeId, ...]
    node_proper_time: dict[NodeId, float]
    window_start_event_time_key: float
    window_end_event_time_key: float
    window_start_sink_proper_time: float
    window_end_sink_proper_time: float
    observed_persistence_duration: float
    proper_time_persistence_threshold: float
    threshold_multiplier: float
    local_median_edge_delay: float
    persistence_passed: bool
    budget_before: float
    budget_after: float
    budget_error: float
    source_basin_evidence_id: str | None = None
    basin_evidence_class: str = "basin_membership_or_causal_basin_core"
    identity_clock_policy: str = LGRC9V3_IDENTITY_CLOCK_POLICY_SINK_LOCAL
    threshold_calibration_policy: str = (
        LGRC9V3_IDENTITY_THRESHOLD_POLICY_LOCAL_MEDIAN_DELAY
    )
    identity_acceptance_allowed: bool = False
    identity_acceptance_emitted: bool = False
    proper_time_identity_processing_implemented: bool = True
    state_mutated: bool = False
    topology_mutated: bool = False
    causal_layer_mode: str = CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY
    lgrc_runtime_level: str = LGRC_RUNTIME_LEVEL_LGRC3
    evidence_class: str = LGRC9V3_PROPER_TIME_IDENTITY_EVALUATION_EVIDENCE_CLASS

    def __post_init__(self) -> None:
        for field_name in ("evaluation_id", "topology_event_id", "topology_event_kind"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value:
                raise ValueError(f"{field_name} must be a non-empty string")
        source_ids = tuple(sorted(str(event_id) for event_id in self.source_topology_event_ids))
        if not source_ids or any(not event_id for event_id in source_ids):
            raise ValueError("source_topology_event_ids must contain non-empty strings")
        if self.topology_event_id not in source_ids:
            raise ValueError("topology_event_id must be one source topology event")
        object.__setattr__(self, "source_topology_event_ids", source_ids)
        for field_name in ("scheduler_event_index", "checkpoint_index"):
            if int(getattr(self, field_name)) < 0:
                raise ValueError(f"{field_name} must be >= 0")
        for field_name in (
            "event_time_key",
            "window_start_event_time_key",
            "window_end_event_time_key",
            "window_start_sink_proper_time",
            "window_end_sink_proper_time",
            "observed_persistence_duration",
            "proper_time_persistence_threshold",
            "threshold_multiplier",
            "local_median_edge_delay",
            "budget_before",
            "budget_after",
        ):
            _nonnegative_float(getattr(self, field_name), context=field_name)
        _positive_float(self.threshold_multiplier, context="threshold_multiplier")
        _positive_float(self.local_median_edge_delay, context="local_median_edge_delay")
        _finite_float(self.budget_error, context="budget_error")
        if self.window_end_event_time_key < self.window_start_event_time_key:
            raise ValueError("window_end_event_time_key must be >= start")
        if self.window_end_sink_proper_time < self.window_start_sink_proper_time:
            raise ValueError("window_end_sink_proper_time must be >= start")
        expected_duration = (
            self.window_end_sink_proper_time - self.window_start_sink_proper_time
        )
        if abs(expected_duration - self.observed_persistence_duration) > 1e-12:
            raise ValueError(
                "observed_persistence_duration must equal sink proper-time delta"
            )
        expected_threshold = self.threshold_multiplier * self.local_median_edge_delay
        if abs(expected_threshold - self.proper_time_persistence_threshold) > 1e-12:
            raise ValueError(
                "proper_time_persistence_threshold must equal multiplier * "
                "local_median_edge_delay"
            )
        expected_pass = (
            self.observed_persistence_duration
            >= self.proper_time_persistence_threshold
        )
        if self.persistence_passed is not expected_pass:
            raise ValueError("persistence_passed must match threshold comparison")
        if abs((self.budget_after - self.budget_before) - self.budget_error) > 1e-12:
            raise ValueError("budget_error must equal budget_after - budget_before")
        if int(self.sink_node_id) < 0:
            raise ValueError("sink_node_id must be >= 0")
        if not isinstance(self.lineage_id, str) or not self.lineage_id:
            raise ValueError("lineage_id must be a non-empty string")
        basin_ids = tuple(sorted({int(node_id) for node_id in self.basin_node_ids}))
        if not basin_ids:
            raise ValueError("basin_node_ids must not be empty")
        if int(self.sink_node_id) not in basin_ids:
            raise ValueError("basin_node_ids must include sink_node_id")
        object.__setattr__(self, "basin_node_ids", basin_ids)
        proper_times = {
            int(node_id): _nonnegative_float(
                value,
                context=f"node_proper_time[{node_id}]",
            )
            for node_id, value in self.node_proper_time.items()
        }
        missing = set(basin_ids) - set(proper_times)
        if missing:
            raise ValueError(
                f"node_proper_time missing basin nodes: {sorted(missing)}"
            )
        if abs(proper_times[int(self.sink_node_id)] - self.window_end_sink_proper_time) > 1e-12:
            raise ValueError("sink node proper time must equal window end")
        object.__setattr__(self, "node_proper_time", dict(sorted(proper_times.items())))
        if self.identity_clock_policy != LGRC9V3_IDENTITY_CLOCK_POLICY_SINK_LOCAL:
            raise ValueError("Iteration 20 supports only sink-local proper time")
        if self.threshold_calibration_policy != (
            LGRC9V3_IDENTITY_THRESHOLD_POLICY_LOCAL_MEDIAN_DELAY
        ):
            raise ValueError("unsupported threshold_calibration_policy")
        if self.identity_acceptance_allowed:
            raise ValueError("persistence evaluator must not enable identity acceptance")
        if self.identity_acceptance_emitted:
            raise ValueError("persistence evaluator must not emit identity acceptance")
        if not self.proper_time_identity_processing_implemented:
            raise ValueError("proper-time identity evaluator must be active")
        if self.state_mutated or self.topology_mutated:
            raise ValueError("persistence evaluator must not mutate state or topology")

    def to_artifact(self) -> dict[str, Any]:
        """Return a JSON-compatible persistence-evaluation artifact."""

        return {
            "artifact_kind": LGRC9V3_LGRC3_PROPER_TIME_IDENTITY_EVALUATION_KIND,
            "artifact_schema_version": (
                LGRC9V3_LGRC3_PROPER_TIME_IDENTITY_EVALUATION_SCHEMA_VERSION
            ),
            "mode_version": LGRC9V3_LGRC3_MODE_VERSION,
            "runtime_family": LGRC9V3_RUNTIME_FAMILY,
            "causal_layer_mode": self.causal_layer_mode,
            "lgrc_runtime_level": self.lgrc_runtime_level,
            "evidence_class": self.evidence_class,
            "evaluation_id": self.evaluation_id,
            "topology_event_id": self.topology_event_id,
            "topology_event_kind": self.topology_event_kind,
            "source_topology_event_ids": list(self.source_topology_event_ids),
            "scheduler_event_index": int(self.scheduler_event_index),
            "checkpoint_index": int(self.checkpoint_index),
            "event_time_key": float(self.event_time_key),
            "sink_node_id": int(self.sink_node_id),
            "lineage_id": self.lineage_id,
            "basin_node_ids": [int(node_id) for node_id in self.basin_node_ids],
            "node_proper_time": _string_keyed_float_map(self.node_proper_time),
            "source_basin_evidence_id": self.source_basin_evidence_id,
            "basin_evidence_class": self.basin_evidence_class,
            "identity_clock_policy": self.identity_clock_policy,
            "threshold_calibration_policy": self.threshold_calibration_policy,
            "proper_time_persistence_threshold": float(
                self.proper_time_persistence_threshold
            ),
            "threshold_multiplier": float(self.threshold_multiplier),
            "local_median_edge_delay": float(self.local_median_edge_delay),
            "window_start_event_time_key": float(self.window_start_event_time_key),
            "window_end_event_time_key": float(self.window_end_event_time_key),
            "window_start_sink_proper_time": float(
                self.window_start_sink_proper_time
            ),
            "window_end_sink_proper_time": float(self.window_end_sink_proper_time),
            "observed_persistence_duration": float(
                self.observed_persistence_duration
            ),
            "persistence_passed": self.persistence_passed,
            "budget_before": float(self.budget_before),
            "budget_after": float(self.budget_after),
            "budget_error": float(self.budget_error),
            "identity_acceptance_allowed": self.identity_acceptance_allowed,
            "identity_acceptance_emitted": self.identity_acceptance_emitted,
            "proper_time_identity_processing_implemented": (
                self.proper_time_identity_processing_implemented
            ),
            "state_mutated": self.state_mutated,
            "topology_mutated": self.topology_mutated,
        }



def build_lgrc9v3_proper_time_identity_evaluation_id(
    *,
    source_topology_event_ids: Sequence[str],
    sink_node_id: NodeId,
    lineage_id: str,
    window_start_event_time_key: float,
    window_end_event_time_key: float,
) -> str:
    """Build a deterministic id for one proper-time identity evaluation."""

    source_ids = tuple(sorted(str(event_id) for event_id in source_topology_event_ids))
    if not source_ids or any(not event_id for event_id in source_ids):
        raise ValueError("source_topology_event_ids must contain non-empty strings")
    if int(sink_node_id) < 0:
        raise ValueError("sink_node_id must be >= 0")
    if not isinstance(lineage_id, str) or not lineage_id:
        raise ValueError("lineage_id must be a non-empty string")
    start_key = _nonnegative_float(
        window_start_event_time_key,
        context="window_start_event_time_key",
    )
    end_key = _nonnegative_float(
        window_end_event_time_key,
        context="window_end_event_time_key",
    )
    if end_key < start_key:
        raise ValueError("window_end_event_time_key must be >= start")
    payload = {
        "runtime_family": LGRC9V3_RUNTIME_FAMILY,
        "kind": "proper_time_identity_persistence_evaluation",
        "source_topology_event_ids": list(source_ids),
        "sink_node_id": int(sink_node_id),
        "lineage_id": lineage_id,
        "window_start_event_time_key": start_key,
        "window_end_event_time_key": end_key,
    }
    return f"lgrc9v3-identity-eval-{digest_canonical_data(payload)[:16]}"


def build_lgrc9v3_identity_acceptance_event_id(
    *,
    source_evaluation_id: str,
    sink_node_id: NodeId,
    lineage_id: str,
    event_time_key: float,
) -> str:
    """Build a deterministic event id for proper-time identity acceptance."""

    if not isinstance(source_evaluation_id, str) or not source_evaluation_id:
        raise ValueError("source_evaluation_id must be a non-empty string")
    if int(sink_node_id) < 0:
        raise ValueError("sink_node_id must be >= 0")
    if not isinstance(lineage_id, str) or not lineage_id:
        raise ValueError("lineage_id must be a non-empty string")
    payload = {
        "runtime_family": LGRC9V3_RUNTIME_FAMILY,
        "kind": LGRC9V3_TOPOLOGY_EVENT_KIND_IDENTITY_ACCEPTANCE,
        "source_evaluation_id": source_evaluation_id,
        "sink_node_id": int(sink_node_id),
        "lineage_id": lineage_id,
        "event_time_key": _nonnegative_float(
            event_time_key,
            context="event_time_key",
        ),
    }
    return f"lgrc9v3-identity-accept-{digest_canonical_data(payload)[:16]}"



def _median_positive(values: Sequence[float], *, context: str) -> float:
    ordered = sorted(_positive_float(value, context=context) for value in values)
    if not ordered:
        raise ValueError(f"{context} must not be empty")
    midpoint = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[midpoint]
    return 0.5 * (ordered[midpoint - 1] + ordered[midpoint])


def evaluate_lgrc9v3_proper_time_identity_persistence(
    *,
    source_topology_event_ids: Sequence[str],
    topology_event_kind: str,
    sink_node_id: NodeId,
    lineage_id: str,
    basin_node_ids: Sequence[NodeId],
    node_proper_time: Mapping[NodeId, float],
    window_start_sink_proper_time: float,
    window_start_event_time_key: float,
    window_end_event_time_key: float,
    scheduler_event_index: int,
    checkpoint_index: int,
    event_time_key: float,
    local_edge_delay: Mapping[EdgeId, float] | Sequence[float] | None = None,
    local_median_edge_delay: float | None = None,
    threshold_multiplier: float = LGRC9V3_DEFAULT_IDENTITY_THRESHOLD_MULTIPLIER,
    source_basin_evidence_id: str | None = None,
    budget_before: float = 0.0,
    budget_after: float | None = None,
) -> LGRC9V3ProperTimeIdentityPersistenceEvaluation:
    """Evaluate sink-local proper-time identity persistence.

    The evaluator consumes topology/lineage ids, basin membership evidence,
    node proper-time surfaces, and a local edge-delay calibration. It returns
    auditable pass/fail evidence only; identity acceptance remains Iteration 21.
    """

    source_ids = tuple(sorted(str(event_id) for event_id in source_topology_event_ids))
    if not source_ids or any(not event_id for event_id in source_ids):
        raise InvalidStateTransitionError(
            "proper-time identity evaluation requires topology/lineage evidence"
        )
    if not isinstance(topology_event_kind, str) or not topology_event_kind:
        raise InvalidStateTransitionError("topology_event_kind must be non-empty")
    sink_id = int(sink_node_id)
    if sink_id < 0:
        raise ValueError("sink_node_id must be >= 0")
    basin_ids = tuple(sorted({int(node_id) for node_id in basin_node_ids}))
    if not basin_ids or sink_id not in basin_ids:
        raise InvalidStateTransitionError(
            "basin membership/core evidence must include the sink"
        )

    proper_times = {
        int(node_id): _nonnegative_float(
            value,
            context=f"node_proper_time[{node_id}]",
        )
        for node_id, value in node_proper_time.items()
    }
    missing_proper_times = set(basin_ids) - set(proper_times)
    if missing_proper_times:
        raise InvalidStateTransitionError(
            f"proper-time surface missing basin nodes: {sorted(missing_proper_times)}"
        )
    window_start_sink_time = _nonnegative_float(
        window_start_sink_proper_time,
        context="window_start_sink_proper_time",
    )
    window_end_sink_time = proper_times[sink_id]
    if window_end_sink_time < window_start_sink_time:
        raise InvalidStateTransitionError(
            "sink-local proper-time window cannot run backwards"
        )

    if local_median_edge_delay is None:
        if local_edge_delay is None:
            raise ValueError(
                "local_edge_delay or local_median_edge_delay is required"
            )
        if isinstance(local_edge_delay, Mapping):
            delay_values = tuple(local_edge_delay.values())
        else:
            delay_values = tuple(local_edge_delay)
        median_delay = _median_positive(
            delay_values,
            context="local_edge_delay",
        )
    else:
        median_delay = _positive_float(
            local_median_edge_delay,
            context="local_median_edge_delay",
        )
    multiplier = _positive_float(
        threshold_multiplier,
        context="threshold_multiplier",
    )
    threshold = multiplier * median_delay
    duration = window_end_sink_time - window_start_sink_time
    resolved_budget_before = _nonnegative_float(
        budget_before,
        context="budget_before",
    )
    resolved_budget_after = (
        resolved_budget_before
        if budget_after is None
        else _nonnegative_float(budget_after, context="budget_after")
    )
    start_key = _nonnegative_float(
        window_start_event_time_key,
        context="window_start_event_time_key",
    )
    end_key = _nonnegative_float(
        window_end_event_time_key,
        context="window_end_event_time_key",
    )
    if end_key < start_key:
        raise InvalidStateTransitionError(
            "proper-time identity event-time window cannot run backwards"
        )

    return LGRC9V3ProperTimeIdentityPersistenceEvaluation(
        evaluation_id=build_lgrc9v3_proper_time_identity_evaluation_id(
            source_topology_event_ids=source_ids,
            sink_node_id=sink_id,
            lineage_id=lineage_id,
            window_start_event_time_key=start_key,
            window_end_event_time_key=end_key,
        ),
        topology_event_id=source_ids[0],
        topology_event_kind=topology_event_kind,
        source_topology_event_ids=source_ids,
        scheduler_event_index=int(scheduler_event_index),
        checkpoint_index=int(checkpoint_index),
        event_time_key=_nonnegative_float(event_time_key, context="event_time_key"),
        sink_node_id=sink_id,
        lineage_id=lineage_id,
        basin_node_ids=basin_ids,
        node_proper_time=proper_times,
        window_start_event_time_key=start_key,
        window_end_event_time_key=end_key,
        window_start_sink_proper_time=window_start_sink_time,
        window_end_sink_proper_time=window_end_sink_time,
        observed_persistence_duration=duration,
        proper_time_persistence_threshold=threshold,
        threshold_multiplier=multiplier,
        local_median_edge_delay=median_delay,
        persistence_passed=duration >= threshold,
        budget_before=resolved_budget_before,
        budget_after=resolved_budget_after,
        budget_error=resolved_budget_after - resolved_budget_before,
        source_basin_evidence_id=source_basin_evidence_id,
    )


def emit_lgrc9v3_proper_time_identity_acceptance(
    evaluation: LGRC9V3ProperTimeIdentityPersistenceEvaluation,
    *,
    identity_acceptance_allowed: bool = False,
    scheduler_event_index: int | None = None,
    checkpoint_index: int | None = None,
    event_time_key: float | None = None,
    budget_before: float | None = None,
    budget_after: float | None = None,
) -> GRCEvent:
    """Emit a proper-time identity-acceptance event after passing evaluation.

    The emitter is the first active identity event surface. It requires a
    passing Iteration 20 evaluator result and explicit policy enablement. It
    records semantic acceptance only: no mechanical expansion, packet
    transport, state mutation, topology mutation, or budget transfer occurs.
    """

    if not identity_acceptance_allowed:
        raise InvalidParamsError(
            "identity acceptance requires explicit policy enablement"
        )
    if not evaluation.persistence_passed:
        raise InvalidStateTransitionError(
            "identity acceptance requires passing persistence evaluation"
        )
    if evaluation.identity_acceptance_emitted:
        raise InvalidStateTransitionError(
            "source evaluator must not already emit identity acceptance"
        )
    resolved_scheduler_event_index = (
        int(evaluation.scheduler_event_index)
        if scheduler_event_index is None
        else int(scheduler_event_index)
    )
    resolved_checkpoint_index = (
        int(evaluation.checkpoint_index)
        if checkpoint_index is None
        else int(checkpoint_index)
    )
    if resolved_scheduler_event_index < 0 or resolved_checkpoint_index < 0:
        raise ValueError("scheduler_event_index and checkpoint_index must be >= 0")
    resolved_event_time_key = (
        evaluation.event_time_key
        if event_time_key is None
        else _nonnegative_float(event_time_key, context="event_time_key")
    )
    resolved_budget_before = (
        evaluation.budget_after
        if budget_before is None
        else _nonnegative_float(budget_before, context="budget_before")
    )
    resolved_budget_after = (
        resolved_budget_before
        if budget_after is None
        else _nonnegative_float(budget_after, context="budget_after")
    )
    budget_error = resolved_budget_after - resolved_budget_before
    if abs(budget_error) > 1e-12:
        raise InvalidStateTransitionError(
            "identity acceptance is semantic and must not change budget"
        )

    identity_event_id = build_lgrc9v3_identity_acceptance_event_id(
        source_evaluation_id=evaluation.evaluation_id,
        sink_node_id=evaluation.sink_node_id,
        lineage_id=evaluation.lineage_id,
        event_time_key=resolved_event_time_key,
    )
    payload: dict[str, Any] = {
        "event_id": identity_event_id,
        "event_schema_version": (
            LGRC9V3_LGRC3_PROPER_TIME_IDENTITY_ACCEPTANCE_EVENT_SCHEMA_VERSION
        ),
        "mode_version": LGRC9V3_LGRC3_MODE_VERSION,
        "runtime_family": LGRC9V3_RUNTIME_FAMILY,
        "causal_layer_mode": CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY,
        "lgrc_runtime_level": LGRC_RUNTIME_LEVEL_LGRC3,
        "evidence_class": LGRC9V3_PROPER_TIME_IDENTITY_ACCEPTANCE_EVIDENCE_CLASS,
        "source_identity_evaluation_id": evaluation.evaluation_id,
        "source_identity_evaluation_artifact_kind": (
            LGRC9V3_LGRC3_PROPER_TIME_IDENTITY_EVALUATION_KIND
        ),
        "source_topology_event_ids": list(evaluation.source_topology_event_ids),
        "source_basin_evidence_id": evaluation.source_basin_evidence_id,
        "topology_event_id": identity_event_id,
        "topology_event_kind": LGRC9V3_TOPOLOGY_EVENT_KIND_IDENTITY_ACCEPTANCE,
        "scheduler_event_index": resolved_scheduler_event_index,
        "checkpoint_index": resolved_checkpoint_index,
        "event_time_key": float(resolved_event_time_key),
        "sink_node_id": int(evaluation.sink_node_id),
        "lineage_id": evaluation.lineage_id,
        "basin_node_ids": [int(node_id) for node_id in evaluation.basin_node_ids],
        "identity_clock_policy": evaluation.identity_clock_policy,
        "threshold_calibration_policy": evaluation.threshold_calibration_policy,
        "proper_time_persistence_threshold": float(
            evaluation.proper_time_persistence_threshold
        ),
        "threshold_multiplier": float(evaluation.threshold_multiplier),
        "local_median_edge_delay": float(evaluation.local_median_edge_delay),
        "window_start_event_time_key": float(evaluation.window_start_event_time_key),
        "window_end_event_time_key": float(evaluation.window_end_event_time_key),
        "window_start_sink_proper_time": float(
            evaluation.window_start_sink_proper_time
        ),
        "window_end_sink_proper_time": float(evaluation.window_end_sink_proper_time),
        "observed_persistence_duration": float(
            evaluation.observed_persistence_duration
        ),
        "persistence_passed": True,
        "budget_before": float(resolved_budget_before),
        "budget_after": float(resolved_budget_after),
        "budget_error": float(budget_error),
        "identity_acceptance_allowed": True,
        "identity_acceptance_emitted": True,
        "mechanical_expansion_emitted": False,
        "packet_transport_emitted": False,
        "mechanical_expansion_is_identity_acceptance": False,
        "refinement_packet_transport_is_identity_transfer": False,
        "state_mutated": False,
        "topology_mutated": False,
    }
    return GRCEvent(
        kind=LGRC9V3_TOPOLOGY_EVENT_KIND_IDENTITY_ACCEPTANCE,
        step_index=resolved_scheduler_event_index,
        payload=payload,
        source_family=LGRC9V3_RUNTIME_FAMILY,
    )



def restore_lgrc9v3_proper_time_identity_evaluation_artifact(
    artifact: Mapping[str, Any],
) -> LGRC9V3ProperTimeIdentityPersistenceEvaluation | None:
    """Restore a proper-time identity persistence-evaluation artifact."""

    mapping = _require_artifact_mapping(
        artifact,
        context="proper_time_identity_evaluation",
    )
    if mapping.get("artifact_kind") != (
        LGRC9V3_LGRC3_PROPER_TIME_IDENTITY_EVALUATION_KIND
    ):
        return None
    schema_version = _artifact_string(
        mapping.get("artifact_schema_version"),
        context="artifact_schema_version",
    )
    if schema_version != (
        LGRC9V3_LGRC3_PROPER_TIME_IDENTITY_EVALUATION_SCHEMA_VERSION
    ):
        raise SnapshotCompatibilityError(
            "unsupported LGRC9V3 proper-time identity evaluation schema version"
        )
    contract_fields = {
        "mode_version": LGRC9V3_LGRC3_MODE_VERSION,
        "runtime_family": LGRC9V3_RUNTIME_FAMILY,
        "causal_layer_mode": CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY,
        "lgrc_runtime_level": LGRC_RUNTIME_LEVEL_LGRC3,
        "evidence_class": LGRC9V3_PROPER_TIME_IDENTITY_EVALUATION_EVIDENCE_CLASS,
        "identity_clock_policy": LGRC9V3_IDENTITY_CLOCK_POLICY_SINK_LOCAL,
        "threshold_calibration_policy": (
            LGRC9V3_IDENTITY_THRESHOLD_POLICY_LOCAL_MEDIAN_DELAY
        ),
    }
    for key, expected in contract_fields.items():
        actual = _artifact_string(mapping.get(key), context=key)
        if actual != expected:
            raise SnapshotCompatibilityError(f"{key} must be {expected!r}")
    for key in (
        "identity_acceptance_allowed",
        "identity_acceptance_emitted",
        "state_mutated",
        "topology_mutated",
    ):
        if _artifact_bool(mapping.get(key), context=key):
            raise SnapshotCompatibilityError(f"{key} must be false")
    if not _artifact_bool(
        mapping.get("proper_time_identity_processing_implemented"),
        context="proper_time_identity_processing_implemented",
    ):
        raise SnapshotCompatibilityError(
            "proper_time_identity_processing_implemented must be true"
        )
    source_ids_raw = mapping.get("source_topology_event_ids", [])
    basin_ids_raw = mapping.get("basin_node_ids", [])
    if not isinstance(source_ids_raw, list):
        raise SnapshotCompatibilityError("source_topology_event_ids must be a list")
    if not isinstance(basin_ids_raw, list):
        raise SnapshotCompatibilityError("basin_node_ids must be a list")
    return LGRC9V3ProperTimeIdentityPersistenceEvaluation(
        evaluation_id=_artifact_string(
            mapping.get("evaluation_id"),
            context="evaluation_id",
        ),
        topology_event_id=_artifact_string(
            mapping.get("topology_event_id"),
            context="topology_event_id",
        ),
        topology_event_kind=_artifact_string(
            mapping.get("topology_event_kind"),
            context="topology_event_kind",
        ),
        source_topology_event_ids=tuple(
            _artifact_string(event_id, context="source_topology_event_ids[]")
            for event_id in source_ids_raw
        ),
        scheduler_event_index=_artifact_int(
            mapping.get("scheduler_event_index"),
            context="scheduler_event_index",
        ),
        checkpoint_index=_artifact_int(
            mapping.get("checkpoint_index"),
            context="checkpoint_index",
        ),
        event_time_key=_artifact_float(
            mapping.get("event_time_key"),
            context="event_time_key",
        ),
        sink_node_id=_artifact_int(
            mapping.get("sink_node_id"),
            context="sink_node_id",
        ),
        lineage_id=_artifact_string(mapping.get("lineage_id"), context="lineage_id"),
        basin_node_ids=tuple(
            _artifact_int(node_id, context="basin_node_ids[]")
            for node_id in basin_ids_raw
        ),
        node_proper_time=_parse_artifact_float_map(
            mapping,
            key="node_proper_time",
        ),
        window_start_event_time_key=_artifact_float(
            mapping.get("window_start_event_time_key"),
            context="window_start_event_time_key",
        ),
        window_end_event_time_key=_artifact_float(
            mapping.get("window_end_event_time_key"),
            context="window_end_event_time_key",
        ),
        window_start_sink_proper_time=_artifact_float(
            mapping.get("window_start_sink_proper_time"),
            context="window_start_sink_proper_time",
        ),
        window_end_sink_proper_time=_artifact_float(
            mapping.get("window_end_sink_proper_time"),
            context="window_end_sink_proper_time",
        ),
        observed_persistence_duration=_artifact_float(
            mapping.get("observed_persistence_duration"),
            context="observed_persistence_duration",
        ),
        proper_time_persistence_threshold=_artifact_float(
            mapping.get("proper_time_persistence_threshold"),
            context="proper_time_persistence_threshold",
        ),
        threshold_multiplier=_artifact_float(
            mapping.get("threshold_multiplier"),
            context="threshold_multiplier",
        ),
        local_median_edge_delay=_artifact_float(
            mapping.get("local_median_edge_delay"),
            context="local_median_edge_delay",
        ),
        persistence_passed=_artifact_bool(
            mapping.get("persistence_passed"),
            context="persistence_passed",
        ),
        budget_before=_artifact_float(
            mapping.get("budget_before"),
            context="budget_before",
        ),
        budget_after=_artifact_float(mapping.get("budget_after"), context="budget_after"),
        budget_error=_artifact_float(mapping.get("budget_error"), context="budget_error"),
        source_basin_evidence_id=_artifact_optional_string(
            mapping.get("source_basin_evidence_id"),
            context="source_basin_evidence_id",
        ),
        basin_evidence_class=_artifact_string(
            mapping.get("basin_evidence_class"),
            context="basin_evidence_class",
        ),
    )


__all__ = [
    'LGRC9V3ProperTimeIdentityFieldNames',
    'LGRC9V3ProperTimeIdentityPersistenceEvaluation',
    'LGRC9V3_LGRC3_PROPER_TIME_IDENTITY_ACCEPTANCE_EVENT_SCHEMA_VERSION',
    'LGRC9V3_LGRC3_PROPER_TIME_IDENTITY_EVALUATION_KIND',
    'LGRC9V3_LGRC3_PROPER_TIME_IDENTITY_EVALUATION_SCHEMA_VERSION',
    'LGRC9V3_PROPER_TIME_IDENTITY_ACCEPTANCE_EVIDENCE_CLASS',
    'LGRC9V3_PROPER_TIME_IDENTITY_EVALUATION_EVIDENCE_CLASS',
    'LGRC9V3_PROPER_TIME_IDENTITY_FIELD_NAMES',
    'LGRC9V3_PROPER_TIME_IDENTITY_REQUIRED_FIELDS',
    '_median_positive',
    'build_lgrc9v3_identity_acceptance_event_id',
    'build_lgrc9v3_proper_time_identity_evaluation_id',
    'emit_lgrc9v3_proper_time_identity_acceptance',
    'evaluate_lgrc9v3_proper_time_identity_persistence',
    'restore_lgrc9v3_proper_time_identity_evaluation_artifact',
]
