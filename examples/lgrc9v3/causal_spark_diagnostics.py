"""Show causally scheduled Lane B spark diagnostics in LGRC9V3.

What this example does:
    Uses the same saturated column-H fixture as the GRC9V3 Lane B examples,
    wraps it in executable `LGRC9V3`, schedules a packet arrival at the
    candidate sink, and lets `LGRC9V3.step()` evaluate the Lane B predicate at
    the arrival/local-update causal boundary.

Why it is needed:
    GRC9V3 Lane B is a synchronous spark lane. LGRC9V3 reuses the proven Lane B
    predicate, but evaluates it from causal event snapshots and wraps the
    evidence as `lgrc9v3_causal_spark_candidate`.

Alternatives:
    Call `model.evaluate_causal_spark_diagnostics(...)` directly when you want
    an explicit diagnostic API call without packet arrival.
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
from pygrc.models import LGRC9V3, LGRC9V3_CAUSAL_SPARK_CANDIDATE_EVENT_KIND  # noqa: E402


def print_json(label: str, payload: object) -> None:
    """Print deterministic JSON for terminal inspection."""

    print(f"\n{label}:")
    print(json.dumps(payload, indent=2, sort_keys=True))


def compact_candidate(event: object) -> dict[str, object]:
    """Keep only the candidate fields users usually inspect first."""

    payload = dict(getattr(event, "payload"))
    return {
        "kind": getattr(event, "kind"),
        "candidate_event_id": payload.get("candidate_event_id"),
        "spark_lane": payload.get("spark_lane"),
        "event_time_key": payload.get("event_time_key"),
        "scheduler_event_index": payload.get("scheduler_event_index"),
        "candidate_node_proper_time": payload.get("candidate_node_proper_time"),
        "gate_reasons": payload.get("gate_reasons"),
        "signed_hessian_hit": payload.get("signed_hessian_hit"),
        "column_h_branch_hit": payload.get("column_h_branch_hit"),
        "column_h": payload.get("column_h"),
        "source_grc9v3_candidate_kind": payload.get(
            "source_grc9v3_candidate_kind"
        ),
        "mechanical_expansion_emitted": payload.get(
            "mechanical_expansion_emitted"
        ),
    }


def main() -> None:
    """Run packet-triggered Lane B candidate diagnostics."""

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

    results = model.run_event_queue(max_events=4)
    candidates = [
        event
        for result in results
        for event in result.events
        if event.kind == LGRC9V3_CAUSAL_SPARK_CANDIDATE_EVENT_KIND
    ]

    print("Executable LGRC9V3 causal Lane B spark diagnostics")
    print_json(
        "step_trace",
        [
            {
                "processed_event_kind": result.bookkeeping.get(
                    "processed_event_kind"
                ),
                "event_time_key": result.bookkeeping.get("event_time_key"),
                "causal_spark_diagnostic_events": result.bookkeeping.get(
                    "causal_spark_diagnostic_events"
                ),
                "event_kinds": [event.kind for event in result.events],
            }
            for result in results
        ],
    )
    print_json(
        "causal_spark_candidates",
        [compact_candidate(candidate) for candidate in candidates],
    )

    print(
        "\nInterpretation: the candidate is LGRC9V3 causal event evidence "
        "wrapping the existing GRC9V3 Lane B predicate. It is candidate "
        "evidence only. Mechanical expansion requires explicit active "
        "topology-integration gates."
    )


if __name__ == "__main__":
    main()
