"""Run opt-in GRC9V3 Lane B and inspect column-H branch evidence.

What this example does:
    Loads the same saturated fixture as the Lane A baseline, but selects
    `spark_lane="grc9v3_column_h_assisted"`. It then prints the candidate
    payload fields that prove the column-H proxy branch fired.

Why it is needed:
    Lane B is not inferred from graph shape or event kind. It is explicit in
    config and in event payload evidence. This script shows the minimal fields
    a user should inspect before making a Lane B claim.

Alternatives:
    Use `lane_a_baseline.py` to see the default non-gating Lane A behavior.
    Use `lane_a_vs_lane_b.py` to compare the two lanes side by side.

References:
    docs/reference/GRC-Runtime-ReferenceGuide.md
    docs/reference/Telemetry-ReferenceGuide.md
"""

from __future__ import annotations

from _fixtures import (
    GRC9V3,
    LANE_B,
    compact_candidate,
    fixture_design,
    make_column_h_state,
    make_config,
    print_json,
)


def main() -> None:
    """Detect a Lane B candidate without mutating topology."""

    state = make_column_h_state()
    config = make_config(spark_lane=LANE_B)
    model = GRC9V3.from_state(state, config)
    params = model.get_params()
    modes = params.constitutive_semantic_modes

    print("GRC9V3 Lane B column-H-assisted candidate")
    print_json("fixture_design", fixture_design())
    print(f"spark_lane: {modes['spark_lane']}")

    candidates = model.detect_hybrid_spark_candidates()
    compact = [compact_candidate(event) for event in candidates]
    print_json("candidate_events", compact)

    if not compact:
        raise RuntimeError("expected one Lane B candidate in the example fixture")

    first = compact[0]
    print_json(
        "column_h_evidence",
        {
            "column_h": first["column_h"],
            "min_abs_column_h": first["min_abs_column_h"],
            "min_abs_column_h_column": first["min_abs_column_h_column"],
            "column_h_branch_hit": first["column_h_branch_hit"],
            "gate_reasons": first["gate_reasons"],
        },
    )

    print(
        "\nInterpretation: Lane B v1 still requires the GRC9V3 saturation "
        "and small-gradient envelope. Inside that envelope, this candidate "
        "fires through the direct runtime-computed column-H proxy branch."
    )


if __name__ == "__main__":
    main()
