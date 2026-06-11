"""Compare Lane A and Lane B on the same GRC9V3 fixture.

What this example does:
    Runs the same state twice: once with Lane A and once with Lane B. It first
    compares candidate payloads, then applies only the spark layer to show
    whether candidate detection routes into mechanical expansion.

Why it is needed:
    A user should be able to see that Lane B is not just Lane A plus telemetry.
    In this fixture, Lane A emits no candidate, while Lane B emits a
    `column_h_threshold_hit` candidate and one mechanical expansion.

Alternatives:
    Use the full `.step()` path when you want complete runtime dynamics. Use
    this spark-layer comparison when the question is specifically about spark
    gate behavior.

References:
    docs/reference/GRC-Runtime-ReferenceGuide.md
    docs/reference/Telemetry-ReferenceGuide.md
"""

from __future__ import annotations

from _fixtures import (
    GRC9V3,
    LANE_A,
    LANE_B,
    compact_candidate,
    event_counts,
    make_column_h_state,
    make_config,
    print_json,
)


def _candidate_summary(spark_lane: str) -> dict[str, object]:
    """Return non-mutating spark candidate evidence for one lane."""

    model = GRC9V3.from_state(
        make_column_h_state(),
        make_config(spark_lane=spark_lane),
    )
    candidates = model.detect_hybrid_spark_candidates()
    compact = [compact_candidate(event) for event in candidates]
    return {
        "spark_lane": spark_lane,
        "candidate_count": len(candidates),
        "column_h_branch_count": sum(
            1 for event in compact if event["column_h_branch_hit"]
        ),
        "candidates": compact,
    }


def _spark_layer_summary(spark_lane: str) -> dict[str, object]:
    """Apply spark detection/expansion without running a full dynamics step."""

    model = GRC9V3.from_state(
        make_column_h_state(),
        make_config(spark_lane=spark_lane),
    )
    events = model.apply_hybrid_sparks()
    return {
        "spark_lane": spark_lane,
        "event_counts": event_counts(events),
    }


def main() -> None:
    """Print candidate and spark-layer contrasts for Lane A and Lane B."""

    print("GRC9V3 Lane A versus Lane B")

    lane_a_candidates = _candidate_summary(LANE_A)
    lane_b_candidates = _candidate_summary(LANE_B)
    print_json(
        "candidate_comparison",
        {
            "lane_a": lane_a_candidates,
            "lane_b": lane_b_candidates,
        },
    )

    print_json(
        "spark_layer_comparison",
        {
            "lane_a": _spark_layer_summary(LANE_A),
            "lane_b": _spark_layer_summary(LANE_B),
        },
    )

    print(
        "\nInterpretation: the event kind is shared. Read "
        "payload.spark_lane and branch fields to distinguish Lane A from "
        "Lane B and to tell signed-Hessian candidates from column-H branch "
        "candidates. The spark-layer comparison applies only spark detection "
        "and mechanical expansion, not a full transport/dynamics step."
    )


if __name__ == "__main__":
    main()
