"""Compare manual LGRC9V3 queue seeding with autonomous execution.

What this example does:
    Builds two identical executable `LGRC9V3` models. The manual model gets an
    explicit scheduled packet departure. The autonomous model gets only a
    causal flux route and then calls `run_autonomous(...)`.

Why it is needed:
    `run_autonomous(...)` is the first bounded producer-plus-executor loop. It
    should make common runs less error-prone without hiding the runtime split:
    producers enqueue work, and `step()` consumes it.

Alternatives:
    Use `autonomous_produce_then_step.py` when you want to inspect the producer
    result before execution. Use `corrected_cascade_comparison.py` for the
    larger GRC9V3/LGRC9V3 comparison fixture.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
GRC9V3_EXAMPLES = REPO_ROOT / "examples" / "grc9v3"
if str(GRC9V3_EXAMPLES) not in sys.path:
    sys.path.insert(0, str(GRC9V3_EXAMPLES))

from _fixtures import LANE_B, make_column_h_state, make_config  # noqa: E402
from pygrc.models import (  # noqa: E402
    LGRC9V3,
    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FLUX_ROUTE,
)


def print_json(label: str, payload: object) -> None:
    """Print deterministic JSON for terminal inspection."""

    print(f"\n{label}:")
    print(json.dumps(payload, indent=2, sort_keys=True))


def run_trace(results: list[object]) -> list[dict[str, object]]:
    """Return a compact queue trace from StepResult objects."""

    return [
        {
            "step_index": result.step_index,
            "time": result.time,
            "processed_event_kind": result.bookkeeping.get("processed_event_kind"),
            "queue_length_after": result.bookkeeping.get("queue_length_after"),
            "event_kinds": [event.kind for event in result.events],
        }
        for result in results
    ]


def node_coherence(model: LGRC9V3, node_ids: tuple[int, ...]) -> dict[str, float]:
    """Return selected node coherence values after a run."""

    return {
        str(node_id): float(model.get_state().base_state.nodes[node_id].coherence)
        for node_id in node_ids
    }


def main() -> None:
    """Run manual and autonomous versions of the same packet route."""

    manual = LGRC9V3.from_state(
        make_column_h_state(),
        make_config(spark_lane=LANE_B),
    )
    autonomous = LGRC9V3.from_state(
        make_column_h_state(),
        make_config(spark_lane=LANE_B),
    )

    manual.schedule_packet_departure(
        source_node_id=1,
        target_node_id=0,
        edge_id=0,
        amount=0.2,
        departure_event_time_key=0.0,
        scheduler_event_index=1,
    )
    manual_results = manual.run_event_queue(max_events=2)

    autonomous.set_causal_flux_routes(
        {
            1: [
                {
                    "target_node_id": 0,
                    "edge_id": 0,
                    "amount": 0.2,
                }
            ]
        }
    )
    autonomous_results = autonomous.run_autonomous(
        max_events=2,
        producer_policies=(
            LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FLUX_ROUTE,
        ),
    )
    autonomous_summary = autonomous.get_state().cached_quantities[
        "last_lgrc9v3_autonomous_run"
    ]

    print("LGRC9V3 bounded autonomous run")
    print_json("manual_trace", run_trace(manual_results))
    print_json("autonomous_trace", run_trace(autonomous_results))
    print_json(
        "selected_node_coherence",
        {
            "manual": node_coherence(manual, (0, 1)),
            "autonomous": node_coherence(autonomous, (0, 1)),
        },
    )
    print_json(
        "autonomous_run_summary",
        {
            "producer_invocation_count": autonomous_summary[
                "producer_invocation_count"
            ],
            "producer_scheduled_event_count": autonomous_summary[
                "producer_scheduled_event_count"
            ],
            "consumed_step_count": autonomous_summary["consumed_step_count"],
            "consumed_event_count": autonomous_summary["consumed_event_count"],
            "stop_condition": autonomous_summary["stop_condition"],
        },
    )

    print(
        "\nInterpretation: the two runs consume the same packet lifecycle. "
        "The manual run schedules the departure directly. The autonomous run "
        "derives that scheduled work from `causal_flux_routes`, then consumes "
        "it through the same `step()` executor."
    )


if __name__ == "__main__":
    main()
