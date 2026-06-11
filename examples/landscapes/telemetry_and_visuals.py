"""Capture telemetry and render behavior visuals for a landscape-backed run.

What this example does:
    Reuses `run_seed_grc9v3.py` to build a GRC9V3 runtime model from the
    landscape seed, captures a one-step runtime telemetry pack, and renders
    behavior trajectories/event timeline.

Why it is needed:
    This closes the source-to-evidence loop for the landscape examples.

Boundary:
    This minimal landscape example renders behavior visuals only. Graph visuals
    require graph checkpoints; the GRC9V3 examples show that separate surface.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pygrc.core import StepResult
from pygrc.telemetry import (
    TelemetryCaptureConfig,
    build_telemetry_artifact_layout,
    capture_run_telemetry,
    load_telemetry_artifact_pack,
)
from pygrc.visualization import (
    DEFAULT_GRC9V3_RUN_OBSERVABLES,
    build_run_visualization_layout,
    render_run_visual_bundle,
)
from run_seed_grc9v3 import build_grc9v3_model_from_seed


OUTPUT_ROOT = Path("outputs/examples/landscapes")
RUN_ID = "landscape_seed_to_grc9v3"


def capture_and_render() -> dict[str, Any]:
    """Capture telemetry for the lowered model and render behavior visuals."""

    model, metadata = build_grc9v3_model_from_seed()
    params = model.get_params()
    initial_observables = dict(model.compute_observables())
    step_result = model.step()
    final_observables = dict(step_result.observables)
    layout = build_telemetry_artifact_layout(RUN_ID, root_dir=OUTPUT_ROOT)
    telemetry = capture_run_telemetry(
        model_family="grc9v3",
        params_identity=params.params_hash,
        seed_name=metadata["seed_name"],
        seed_source_reference="examples/landscapes/define_seed.py",
        seed_path="outputs/examples/landscapes/seeds/example-grcl9v3-hybrid-spark.seed.yaml",
        param_family="landscape_example",
        rng_seed=None,
        requested_steps=1,
        initial_observables=initial_observables,
        step_results=(step_result,),
        final_observables=final_observables,
        resolved_params=params.resolved_config,
        raw_params=params.raw_config,
        artifact_layout=layout,
        config=TelemetryCaptureConfig(root_dir=OUTPUT_ROOT, write_artifacts=True),
    )
    pack = load_telemetry_artifact_pack(layout)
    visual_layout = build_run_visualization_layout(layout)
    render_run_visual_bundle(
        pack,
        layout=visual_layout,
        observables=DEFAULT_GRC9V3_RUN_OBSERVABLES,
    )
    return {
        "run_id": telemetry.identity.run_id,
        "telemetry_dir": str(layout.telemetry_dir),
        "steps_path": str(layout.step_rows_path),
        "events_path": str(layout.event_rows_path),
        "run_summary_path": str(layout.run_summary_path),
        "visualization_dir": str(visual_layout.run_dir),
        "trajectories": str(visual_layout.trajectory_figure_path),
        "events": str(visual_layout.event_timeline_path),
        "event_count": len(telemetry.event_rows),
    }


def main() -> None:
    print("Landscape telemetry and visuals")
    print(json.dumps(capture_and_render(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
