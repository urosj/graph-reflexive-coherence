# Quickstart

These examples are first-contact scripts.

They should be more exciting than minimal API smoke tests, but less detailed
than the focused workflow examples under `examples/grc9v3/` and
`examples/landscapes/`.

## Start Here

```bash
.venv/bin/python examples/quickstart/spark_a_cell.py
```

This loads a rich landscape seed, lowers it into `GRC9V3`, runs one step,
captures telemetry, and renders visual outputs.

Open the files printed at the end:

```text
events.png
trajectories.png
graph_sequence.png
graph_html/final_graph.html
graph_animation.gif
```

## What It Shows

The quickstart is intentionally narrative:

```text
landscape seed
  -> GRC9V3 runtime model
  -> spark / expansion / choice events
  -> telemetry artifacts
  -> visible graph and event outputs
```

When you want to understand the details, continue with:

- [GRC9V3 Examples](../grc9v3/README.md)
- [Landscape Examples](../landscapes/README.md)
