"""Build LGRC9V3 directly from a landscape seed and run queued events.

What this example does:
    Loads a GRCL9V3 landscape seed, lowers it through the library-owned
    `LandscapeSeed -> GRCL9V3 source -> GRC9V3State -> LGRC9V3RuntimeState`
    path, primes broad packet traffic from the current topology, and processes
    a few native LGRC9V3 queue events.

Why it is needed:
    Earlier examples had to spell out the lowering chain and queue-priming
    policy themselves. Iteration 36 moves that wiring into library helpers so
    examples can demonstrate the path without owning it.

Boundary:
    This is still an LGRC9V3 runtime over a GRC9V3 substrate state. It does not
    call synchronous `GRC9V3.step()` and it does not claim a general LGRCV3 or
    non-nine-port LGRC runtime.
"""

from __future__ import annotations

import json
from pathlib import Path

from pygrc.models import (
    build_lgrc9v3_from_landscape_seed,
    lgrc9v3_graph_routes_for_current_topology,
    prepare_lgrc9v3_landscape_runtime,
    prime_lgrc9v3_broad_seed_packets,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
SEED_PATH = (
    REPO_ROOT
    / "configs/landscapes/seed/grcl9v3-cell-boundary-membrane-spark.seed.yaml"
)


def print_json(label: str, payload: object) -> None:
    """Print deterministic JSON for terminal inspection."""

    print(f"\n{label}:")
    print(json.dumps(payload, indent=2, sort_keys=True))


def main() -> None:
    """Run a short landscape-backed LGRC9V3 queue."""

    build = prepare_lgrc9v3_landscape_runtime(SEED_PATH)
    model = build.model

    # The shorter facade returns only the model when metadata is not needed.
    facade_model = build_lgrc9v3_from_landscape_seed(SEED_PATH)
    assert facade_model.MODEL_FAMILY == model.MODEL_FAMILY

    model.set_causal_flux_routes(lgrc9v3_graph_routes_for_current_topology(model))
    priming = prime_lgrc9v3_broad_seed_packets(model)
    results = model.run_event_queue(max_events=6)

    print("Landscape-backed executable LGRC9V3")
    print_json("build_metadata", build.metadata())
    print_json("queue_priming", priming.to_summary())
    print_json(
        "queue_trace",
        [
            {
                "processed_event_kind": result.bookkeeping.get(
                    "processed_event_kind"
                ),
                "event_time_key": result.bookkeeping.get("event_time_key"),
                "queue_length_after": result.bookkeeping.get("queue_length_after"),
                "event_kinds": [event.kind for event in result.events],
            }
            for result in results
        ],
    )
    print_json("final_observables", model.compute_observables())


if __name__ == "__main__":
    main()
