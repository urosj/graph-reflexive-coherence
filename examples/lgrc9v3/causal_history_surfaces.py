"""Compute LGRC-0 and LGRC-1 evidence over a GRC9V3 fixture.

What this example does:
    Builds the same small saturated `GRC9V3` fixture used by the Lane A/Lane B
    examples. It then computes:

    - LGRC-0 derived causal-history annotation;
    - LGRC-1 fixed-topology semi-causal eligibility.

Why it is needed:
    LGRC9V3 currently has helper surfaces, not a full event-driven model class.
    This script shows the exact API shape and the labels that keep the claim
    honest.

Alternatives:
    Use `examples/grc9v3/` for ordinary GRC9V3 runtime stepping, spark lanes,
    telemetry, and visuals. Use future LGRC-2 examples only after packetized
    causal flux exists.

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

from _fixtures import make_model  # noqa: E402
from pygrc.models import (  # noqa: E402
    EDGE_DELAY_POLICY_CONSTANT_DELAY,
    LAPSE_POLICY_UNIT,
    annotate_lgrc9v3_causal_history,
    compute_lgrc9v3_fixed_topology_eligibility,
)


def add_unit_distance_labels(state: object) -> None:
    """Add the minimal geometric labels required by LGRC-0 distance surfaces.

    The shared GRC9V3 fixture is intentionally small and spark-focused. It is a
    valid synchronous runtime state, but it does not need geometric edge-length
    labels for ordinary Lane A/Lane B spark examples.

    LGRC-0 asks a different question: what causal-history and distance
    surfaces can be derived over that state? For that question, every live edge
    needs a geometric length. A richer model or landscape-lowered state may
    provide physical lengths directly; this example uses unit lengths so the
    setup stays focused on the causal-history API.
    """

    topology = getattr(state, "topology")
    geometric_length = getattr(state, "geometric_length")
    for edge_id in topology.iter_live_edge_ids():
        geometric_length.setdefault(edge_id, 1.0)


def print_json(label: str, payload: object) -> None:
    """Print compact deterministic JSON for terminal inspection."""

    print(f"\n{label}:")
    print(json.dumps(payload, indent=2, sort_keys=True))


def main() -> None:
    """Compute current LGRC9V3 evidence without running full LGRC dynamics."""

    model = make_model()
    state = model.get_state()
    state.step_index = 4
    add_unit_distance_labels(state)

    annotation = annotate_lgrc9v3_causal_history(
        state,
        causal_modes={
            "lapse_policy": LAPSE_POLICY_UNIT,
            "edge_delay_policy": EDGE_DELAY_POLICY_CONSTANT_DELAY,
            "event_time_policy": "synchronous_limit",
        },
        event_time_scale=0.25,
        edge_delay_kwargs={"tau_0": 0.25},
    )
    annotation_artifact = annotation.to_artifact()

    eligibility = compute_lgrc9v3_fixed_topology_eligibility(
        state,
        causal_modes={
            "causal_layer_mode": "fixed_topology_semicausal",
            "lgrc_runtime_level": "lgrc1",
            "proper_time_accumulation_policy": "synchronous_limit",
            "lapse_policy": "unit",
            "edge_delay_policy": "constant_delay",
            "event_time_policy": "synchronous_limit",
            "require_fixed_topology_for_lgrc1": True,
        },
        event_time_scale=0.25,
        min_delta_tau=1.0,
        edge_delay_kwargs={"tau_0": 0.25},
    )
    eligibility_artifact = eligibility.to_artifact()

    print("LGRC9V3 causal-history surfaces")
    print_json(
        "lgrc0_annotation",
        {
            "annotation_only": annotation_artifact["annotation_only"],
            "evidence_class": annotation_artifact["evidence_class"],
            "causal_layer_mode": annotation_artifact["causal_layer_mode"],
            "lgrc_runtime_level": annotation_artifact["lgrc_runtime_level"],
            "event_time_key": annotation_artifact["event_time_key"],
            "node_proper_time": annotation_artifact["node_proper_time"],
            "edge_causal_delay": annotation_artifact["edge_causal_delay"],
        },
    )
    print_json(
        "lgrc1_eligibility",
        {
            "evidence_class": eligibility_artifact["evidence_class"],
            "semi_causal": eligibility_artifact["semi_causal"],
            "packetized_flux": eligibility_artifact["packetized_flux"],
            "causal_availability_buffers": eligibility_artifact[
                "causal_availability_buffers"
            ],
            "eligible_node_ids": eligibility_artifact["eligible_node_ids"],
            "node_elapsed_proper_time": eligibility_artifact[
                "node_elapsed_proper_time"
            ],
            "budget_error": eligibility_artifact["budget_error"],
        },
    )

    print(
        "\nInterpretation: this is LGRC-0/LGRC-1 evidence over a synchronous "
        "GRC9V3 state. It does not claim packetized LGRC-2 propagation, "
        "in-flight coherence conservation, topology-changing causal history, "
        "or proper-time identity acceptance."
    )


if __name__ == "__main__":
    main()
