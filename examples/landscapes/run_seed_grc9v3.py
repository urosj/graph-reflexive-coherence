"""Lower a seed-backed landscape into GRC9V3 and run it.

What this example does:
    Loads the normalized seed, extracts its GRCL9V3 landscape extension,
    compiles it into a GRCL9V3 source document, lowers that source into a
    `GRC9V3State`, constructs `GRC9V3`, and runs one full step.

Why it is needed:
    This is the handoff point where source-side landscape declarations become
    runtime state. Before this step, there are no runtime events.

Boundary:
    The normalized seed is not directly the GRC9V3 graph. The GRCL9V3 extension
    is compiled and lowered first.
"""

from __future__ import annotations

import json
from typing import Any

from load_seed import load_example_seed
from pygrc.landscapes.extensions.grcl9v3 import (
    compile_grcl9v3_landscape_example_to_source,
    extract_grcl9v3_landscape_example_from_seed,
)
from pygrc.models import GRC9V3, lower_grcl9v3_source_to_grc9v3_state


def build_grc9v3_model_from_seed() -> tuple[GRC9V3, dict[str, Any]]:
    """Build a GRC9V3 model from the example landscape seed."""

    seed = load_example_seed()
    example = extract_grcl9v3_landscape_example_from_seed(seed)
    if example is None:
        raise RuntimeError("example seed does not contain a GRCL9V3 extension")
    source = compile_grcl9v3_landscape_example_to_source(example)
    config = {"dt": seed.constitutive_profile.dt}
    lowering = lower_grcl9v3_source_to_grc9v3_state(source, params=config)
    model = GRC9V3.from_state(lowering.state, config)
    metadata = {
        "seed_name": seed.meta.name,
        "example_name": example.example_name,
        "source_construct_kinds": [
            construct.construct_kind for construct in source.constructs
        ],
        "node_id_by_role": dict(lowering.node_id_by_role),
        "edge_id_by_role": dict(lowering.edge_id_by_role),
    }
    return model, metadata


def run_seed_runtime() -> dict[str, Any]:
    """Run the lowered model and summarize runtime events.

    The normal `.step()` path is intentional here: lowering creates source-
    projected state, and the full runtime step rebuilds the diagnostic surfaces
    before spark detection.
    """

    model, metadata = build_grc9v3_model_from_seed()
    step_result = model.step()
    events = step_result.events
    counts: dict[str, int] = {}
    for event in events:
        counts[event.kind] = counts.get(event.kind, 0) + 1
    state = model.get_state()
    return {
        **metadata,
        "runtime_model": "GRC9V3",
        "step_index": step_result.step_index,
        "time": step_result.time,
        "node_count_after_run": len(tuple(state.topology.iter_live_node_ids())),
        "edge_count_after_run": len(tuple(state.topology.iter_live_edge_ids())),
        "event_counts": counts,
        "events": [
            {
                "kind": event.kind,
                "step_index": event.step_index,
                "payload": dict(event.payload),
            }
            for event in events
        ],
    }


def main() -> None:
    print("Landscape seed lowered to GRC9V3")
    print(json.dumps(run_seed_runtime(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
