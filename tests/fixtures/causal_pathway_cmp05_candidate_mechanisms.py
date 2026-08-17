"""Executable fixtures for reviewed CMP-05 candidate evidence."""

from __future__ import annotations

from typing import Any


def diagnostic_to_packet_candidate_crossing(
    diagnostic_result: Any = None,
    context: Any = None,
) -> dict[str, Any]:
    """Build a source-dependent packet request from one diagnostic result."""

    return {
        "packet_schedule_arguments": {
            "source_node_id": 0,
            "target_node_id": 1,
            "edge_id": 0,
            "amount": 0.25 if diagnostic_result is not None else 0.0,
        },
        "source_result_type": type(diagnostic_result).__name__,
    }


def diagnostic_to_packet_candidate_source_noop(
    diagnostic_result: Any = None,
) -> dict[str, Any]:
    """Mention the source without changing the selected packet request."""

    return {
        "packet_schedule_arguments": {
            "source_node_id": 0,
            "target_node_id": 1,
            "edge_id": 0,
            "amount": (
                0.25 if diagnostic_result is not None else 0.25  # noqa: RUF034
            ),
        },
    }


def diagnostic_to_packet_candidate_nonnull_default(
    diagnostic_result: Any = 1,
) -> dict[str, Any]:
    """Expose the Round 7 non-null-default omission falsifier."""

    return {
        "packet_schedule_arguments": {
            "source_node_id": 0,
            "target_node_id": 1,
            "edge_id": 0,
            "amount": 0.25 if diagnostic_result is not None else 0.0,
        },
    }


def synonym_noop_candidate_crossing(diagnostic_result: Any = None) -> None:
    """Represent the Round 3 synonym-renamed no-op falsifier exactly."""

    return None  # noqa: RET501 - exact Round 3 no-op falsifier
