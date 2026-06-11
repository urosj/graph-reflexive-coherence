"""Schedule autonomous LGRC9V3 work, then consume it with `step()`.

What this example does:
    Builds the standard GRC9V3 column-H fixture as an executable `LGRC9V3`
    model, configures one explicit causal flux route, calls
    `produce_events(...)`, and then calls `step()` once.

Why it is needed:
    This is the smallest example for the Iteration 38-40 autonomy boundary.
    A producer may inspect the current runtime state and enqueue causal work,
    but it does not process packets or mutate topology. `step()` remains the
    executor that consumes queued work.

Alternatives:
    Use `autonomous_run.py` when you want the bounded producer-plus-executor
    loop. Use `executable_packet_queue.py` when you want fully manual queue
    priming without autonomous production.
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


def compact_production(result: object) -> dict[str, object]:
    """Return the producer fields a user usually checks first."""

    artifact = result.to_artifact()
    records = artifact["production_records"]
    return {
        "producer_policy": artifact["producer_policy"],
        "scheduled_event_count": artifact["scheduled_event_count"],
        "state_mutated": artifact["state_mutated"],
        "records": [
            {
                "reason_code": record["reason_code"],
                "scheduled_event_kind": record["scheduled_event_kind"],
                "scheduled_event_time_key": record["scheduled_event_time_key"],
                "observed_evidence": record["observed_evidence"],
            }
            for record in records
        ],
    }


def compact_step(result: object) -> dict[str, object]:
    """Return the executor fields that show what `step()` consumed."""

    return {
        "step_index": result.step_index,
        "time": result.time,
        "processed_event_kind": result.bookkeeping.get("processed_event_kind"),
        "queue_length_after": result.bookkeeping.get("queue_length_after"),
        "event_kinds": [event.kind for event in result.events],
    }


def main() -> None:
    """Run producer scheduling and one executor step."""

    model = LGRC9V3.from_state(
        make_column_h_state(),
        make_config(spark_lane=LANE_B),
    )

    # Route key `1` means "when producer logic starts from node 1, create a
    # packet toward node 0 through edge 0". The route is only a scheduling
    # surface; the packet is not debited until `step()` processes departure.
    model.set_causal_flux_routes(
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

    produced = model.produce_events(
        policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_PACKET_DEPARTURE_FROM_FLUX_ROUTE
    )
    queue_after_producer = model.get_state().packet_ledger.event_queue_records
    step_result = model.step()

    print("LGRC9V3 autonomous producer then step")
    print_json("producer_result", compact_production(produced))
    print_json(
        "queue_after_producer",
        [event.to_record() for event in queue_after_producer],
    )
    print_json("step_result", compact_step(step_result))
    print_json("final_observables", model.compute_observables())

    print(
        "\nInterpretation: `produce_events(...)` scheduled one packet departure. "
        "`step()` then consumed that queued departure and performed the budget "
        "mutation. The producer did not process the packet itself."
    )


if __name__ == "__main__":
    main()
