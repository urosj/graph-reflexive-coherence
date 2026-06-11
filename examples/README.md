# PyGRC Examples

This directory is for runnable usage paths.

Reference guides explain the runtime, telemetry, landscape, and visualization
surfaces. Examples prove that those surfaces compose into workflows a user can
run without knowing the implementation history.

The rule for examples is:

```text
small,
executable,
linked to reference docs,
and focused on real usage friction.
```

Examples are not experiment reports. They should not duplicate the detailed
evidence reports under `experiments/` or the implementation checklists under
`implementation/`. Their job is to answer practical questions:

- What do I import?
- What config do I pass?
- What does `.step()` or `.run()` return?
- Where does evidence live?
- How do telemetry and visuals connect?
- Which workflow feels stable enough to document as a public path?

## Current Focus

The current example focus has these entry points:

- [Quickstart](quickstart/README.md)
- [GRC9V3 Examples](grc9v3/README.md)
- [LGRC9V3 Examples](lgrc9v3/README.md)
- [Landscape Examples](landscapes/README.md)

GRC9V3 is the best current synchronous runtime target because it now has:

- a default Lane A runtime baseline;
- an opt-in Lane B column-H-assisted spark lane;
- telemetry evidence for lane and branch attribution;
- visualization support for Lane A/Lane B candidate classes;
- landscape/lowering routes into `GRC9V3State`.

LGRC9V3 is the current executable causal-history target. Use it when you want
packet event queues, causal event-time/proper-time evidence, causally scheduled
Lane A/Lane B diagnostics, or LGRC9V3 telemetry/visual overlays.

## Scripts Versus Notebooks

Start with plain Python scripts. They are easier to run, diff, test, and reuse
as smoke tests.

Notebooks can be added later for narrative walkthroughs, but they should follow
stable scripts rather than replace them.

Preferred shape:

```text
examples/
  README.md
  quickstart/
    README.md
    spark_a_cell.py
  grc9v3/
    README.md
    lane_a_baseline.py
    lane_b_column_h.py
    lane_a_vs_lane_b.py
    telemetry_capture.py
    visual_bundle.py
  lgrc9v3/
    README.md
    executable_runtime.py
    executable_packet_queue.py
    causal_spark_diagnostics.py
    telemetry_visual_bundle.py
    causal_history_surfaces.py
    packetized_causal_flux.py
    refinement_packet_transport.py
    active_lgrc3_causal_history.py
  landscapes/
    README.md
    define_seed.py
    load_seed.py
    run_seed_grc9v3.py
    telemetry_and_visuals.py
```

The files listed above are the intended usage map. They may be added
incrementally as each workflow is made runnable.

## Running Examples

Run examples from the repository root with the local environment:

```bash
PYTHONPATH=src ./.venv/bin/python examples/grc9v3/lane_a_baseline.py
```

When examples write artifacts, they should use `outputs/examples/` unless the
README for that example says otherwise.

## Reference Guides

Use these guides while reading examples:

- [GRC Runtime Reference Guide](../docs/reference/GRC-Runtime-ReferenceGuide.md)
- [Telemetry Reference Guide](../docs/reference/Telemetry-ReferenceGuide.md)
- [Graph Visualization Reference Guide](../docs/reference/GraphVisualization-ReferenceGuide.md)
- [Landscape Language Reference Guide](../docs/reference/LandscapeLanguage-ReferenceGuide.md)
- [Landscape Compiler And Lowering Reference Guide](../docs/reference/LandscapeCompiler-ReferenceGuide.md)
