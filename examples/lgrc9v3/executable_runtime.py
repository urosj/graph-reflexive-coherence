"""Construct and run the executable LGRC9V3 runtime shell.

What this example does:
    Builds the shared GRC9V3 column-H fixture, wraps it in the executable
    `LGRC9V3` model class, schedules one causal packet, and processes the
    runtime event queue with `LGRC9V3.step()`.

Why it is needed:
    This is the smallest example for the post-Iteration-25 runtime boundary.
    `LGRC9V3` now has a model class and a step loop, but that loop is not
    synchronous `GRC9V3.step()`. It processes queued causal events and records
    scheduler/event-time/proper-time evidence.

Alternatives:
    Use `packetized_causal_flux.py` when you want the older helper-level
    packet API. Use `causal_spark_diagnostics.py` when you specifically want
    Lane A/Lane B candidate evidence at causal boundaries.

References:
    docs/reference/LGRC9V3-CausalHistory-ReferenceGuide.md
    specs/lgrc-9-v3-spec.md
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
GRC9V3_EXAMPLES = REPO_ROOT / "examples" / "grc9v3"
if str(GRC9V3_EXAMPLES) not in sys.path:
    sys.path.insert(0, str(GRC9V3_EXAMPLES))

from _fixtures import LANE_B, fixture_design, make_column_h_state, make_config  # noqa: E402
from pygrc.models import LGRC9V3  # noqa: E402


def print_json(label: str, payload: object) -> None:
    """Print deterministic JSON for terminal inspection."""

    print(f"\n{label}:")
    print(json.dumps(payload, indent=2, sort_keys=True))


def step_summary(result: object) -> dict[str, object]:
    """Return the fields that make LGRC timing distinct from GRC step time."""

    bookkeeping = dict(getattr(result, "bookkeeping"))
    return {
        "step_index": getattr(result, "step_index"),
        "time": getattr(result, "time"),
        "scheduler_event_index": bookkeeping.get("scheduler_event_index"),
        "checkpoint_index": bookkeeping.get("checkpoint_index"),
        "event_time_key": bookkeeping.get("event_time_key"),
        "processed_event_kind": bookkeeping.get("processed_event_kind"),
        "queue_length_after": bookkeeping.get("queue_length_after"),
        "event_kinds": [event.kind for event in getattr(result, "events")],
    }


def main() -> None:
    """Run one packet departure and arrival through `LGRC9V3.step()`."""

    model = LGRC9V3.from_state(
        make_column_h_state(),
        make_config(spark_lane=LANE_B),
    )
    model.schedule_packet_departure(
        source_node_id=1,
        target_node_id=0,
        edge_id=0,
        amount=0.1,
        departure_event_time_key=1.0,
        scheduler_event_index=1,
    )

    results = []
    while model.get_state().packet_ledger.event_queue_records:
        results.append(model.step())

    print("Executable LGRC9V3 runtime shell")
    print_json(
        "fixture",
        {
            "source": "examples/grc9v3/_fixtures.py",
            "center_node_id": fixture_design()["center_node"],
            "spark_lane": LANE_B,
        },
    )
    print_json("steps", [step_summary(result) for result in results])
    print_json(
        "final_runtime_clocks",
        {
            "scheduler_event_index": model.get_state().scheduler_event_index,
            "checkpoint_index": model.get_state().checkpoint_index,
            "event_time_key": model.get_state().event_time_key,
            "node_proper_time": model.get_state().node_proper_time,
        },
    )
    print_json("final_observables", model.compute_observables())

    print(
        "\nInterpretation: `LGRC9V3.step()` processed causal queue events. "
        "Its `step_index` is the scheduler event index in this runtime, not a "
        "synchronous GRC9V3 global slice. This example does not claim general "
        "LGRC, executable LGRC9, or executable LGRCV3 support."
    )


if __name__ == "__main__":
    main()
