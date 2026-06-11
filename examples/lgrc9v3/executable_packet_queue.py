"""Run packetized causal flux with explicit LGRC9V3 local-update routes.

What this example does:
    Creates an executable `LGRC9V3` model, schedules one packet into the center
    node, and configures the arrival local-update surface to emit an outbound
    packet route. The queue then processes departure, arrival, local update,
    routed departure, and routed arrival.

Why it is needed:
    This shows the active LGRC-2/LGRC9V3 runtime path rather than the older
    helper-only packet functions. Packetized coherence movement is explicit
    and budget-auditable; delayed-evaluation continuity remains disabled.

Alternatives:
    Use `executable_runtime.py` for the smallest queue run. Use
    `packetized_causal_flux.py` if you need the lower-level helper functions
    rather than the model class.
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
from pygrc.models import LGRC9V3  # noqa: E402


def print_json(label: str, payload: object) -> None:
    """Print deterministic JSON for terminal inspection."""

    print(f"\n{label}:")
    print(json.dumps(payload, indent=2, sort_keys=True))


def main() -> None:
    """Run a routed packetized causal-flux queue."""

    model = LGRC9V3.from_state(
        make_column_h_state(),
        make_config(spark_lane=LANE_B),
    )
    initial_budget = model.compute_observables()["conserved_budget_total"]

    model.set_causal_flux_routes(
        {
            0: (
                {
                    "target_node_id": 2,
                    "edge_id": 1,
                    "amount_fraction": 0.5,
                },
            )
        }
    )
    model.schedule_packet_departure(
        source_node_id=1,
        target_node_id=0,
        edge_id=0,
        amount=0.2,
        departure_event_time_key=1.0,
        scheduler_event_index=1,
    )

    results = model.run_event_queue(max_events=8)
    event_kinds = [event.kind for result in results for event in result.events]

    print("Executable LGRC9V3 packetized causal-flux queue")
    print_json(
        "queue_trace",
        [
            {
                "processed_event_kind": result.bookkeeping.get(
                    "processed_event_kind"
                ),
                "event_time_key": result.bookkeeping.get("event_time_key"),
                "queue_length_after": result.bookkeeping.get("queue_length_after"),
                "local_update_events": result.bookkeeping.get("local_update_events"),
                "event_kinds": [event.kind for event in result.events],
            }
            for result in results
        ],
    )
    print_json(
        "budget",
        {
            "initial_conserved_budget_total": initial_budget,
            "final_conserved_budget_total": model.compute_observables()[
                "conserved_budget_total"
            ],
            "in_flight_packet_total": model.compute_observables()[
                "in_flight_packet_total"
            ],
        },
    )
    print_json(
        "evidence_counts",
        {
            "processed_steps": len(results),
            "event_kinds": event_kinds,
            "arrival_eligibility_count": len(
                model.get_state().arrival_eligibility_log
            ),
            "local_update_count": len(model.get_state().local_update_log),
        },
    )

    print(
        "\nInterpretation: packetized local updates can schedule additional "
        "causal packet routes. The runtime keeps packet movement explicit and "
        "does not also apply a delayed-evaluation continuity formula."
    )


if __name__ == "__main__":
    main()
