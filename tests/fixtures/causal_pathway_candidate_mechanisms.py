"""Executable fixtures for unregistered causal-pathway candidate evidence."""

from __future__ import annotations

from typing import Any


def packet_schedule_to_snapshot_crossing(schedule_result: Any) -> Any:
    """Carry one packet-schedule result across the fixture candidate cut."""

    return schedule_result


def diagnostic_to_packet_candidate_crossing(
    diagnostic_result: Any,
    context: Any = None,
) -> dict[str, Any]:
    """Build a distinct packet request from one diagnostic result."""

    return {
        "packet_schedule_arguments": {
            "source_node_id": 0,
            "target_node_id": 1,
            "edge_id": 0,
            "amount": 0.25,
        },
        "source_result_type": type(diagnostic_result).__name__,
    }


def synonym_noop_candidate_crossing(diagnostic_result: Any) -> None:
    """Represent the Round 3 synonym-renamed no-op falsifier exactly."""

    return None  # noqa: RET501 - exact Round 3 no-op falsifier
