"""Load and run the default GRC9V3 Lane A baseline on a small fixture.

What this example does:
    Loads a `GRC9V3` model through `GRC9V3.from_state(...)`, prints what was
    loaded, checks spark candidates, and runs one full `.step()`.

Why it is needed:
    This is the baseline usage path. It shows the default lane:
    `current_hybrid_signed_hessian`. It also shows that column-H pressure in
    this fixture is not a Lane A gate.

Alternatives:
    Use `lane_b_column_h.py` to inspect opt-in Lane B evidence. Use
    `lane_a_vs_lane_b.py` to compare both lanes on the same state.

References:
    docs/reference/GRC-Runtime-ReferenceGuide.md
    examples/grc9v3/README.md
"""

from __future__ import annotations

from _fixtures import (
    GRC9V3,
    LANE_A,
    compact_candidate,
    describe_model,
    event_counts,
    fixture_design,
    make_column_h_state,
    make_config,
    print_json,
)


def main() -> None:
    """Run the baseline and print the minimum useful evidence.

    The candidate detection call is intentionally separate from `.step()`.
    `detect_hybrid_spark_candidates()` shows the spark gate surface without
    mutating topology; `.step()` shows the normal full runtime path.
    """

    state = make_column_h_state()
    config = make_config(spark_lane=LANE_A)
    model = GRC9V3.from_state(state, config)
    params = model.get_params()
    modes = params.constitutive_semantic_modes

    print("GRC9V3 Lane A baseline")
    print_json("fixture_design", fixture_design())
    print(f"spark_lane: {modes['spark_lane']}")
    print_json("loaded_model", describe_model(model))

    candidates = model.detect_hybrid_spark_candidates()
    print_json("candidate_events", [compact_candidate(event) for event in candidates])

    step_model = GRC9V3.from_state(make_column_h_state(), make_config(spark_lane=LANE_A))
    result = step_model.step()
    print_json(
        "one_step_summary",
        {
            "step_index": result.step_index,
            "time": result.time,
            "event_counts": event_counts(result.events),
            "observables": result.observables,
        },
    )

    print(
        "\nInterpretation: Lane A is the default signed-Hessian baseline. "
        "This fixture has column-H pressure, but Lane A does not treat "
        "column-H as a gate."
    )


if __name__ == "__main__":
    main()
