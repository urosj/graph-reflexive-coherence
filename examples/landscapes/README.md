# Landscape Examples

These examples focus on landscape source data.

The point is not GRC9V3 itself. GRC9V3 appears here only as one runtime target
that a landscape source can be lowered into.

## Workflow

```text
define landscape seed
  -> save normalized seed
  -> load and validate seed
  -> extract GRCL9V3 landscape extension
  -> compile to GRCL9V3 source document
  -> lower to GRC9V3 runtime state
  -> run model
  -> capture telemetry / render visuals
```

## Examples

Run from the repository root:

```bash
.venv/bin/python examples/landscapes/define_seed.py
.venv/bin/python examples/landscapes/load_seed.py
.venv/bin/python examples/landscapes/run_seed_grc9v3.py
.venv/bin/python examples/landscapes/telemetry_and_visuals.py
```

| Example | Purpose |
|---|---|
| `define_seed.py` | Define a normalized landscape seed in Python and save it. |
| `load_seed.py` | Load and validate a saved seed, then summarize source-side content. |
| `run_seed_grc9v3.py` | Compile/lower a seed-backed GRCL9V3 landscape into `GRC9V3` and run it. |
| `telemetry_and_visuals.py` | Capture telemetry and render behavior visuals for the lowered runtime. |

## Output

The scripts write under:

```text
outputs/examples/landscapes/
```

The seed-definition script writes:

```text
outputs/examples/landscapes/seeds/example-grcl9v3-hybrid-spark.seed.yaml
```

Telemetry and visuals write:

```text
outputs/examples/landscapes/telemetry/
```

## Source Versus Runtime

A landscape seed is source-side data. It can declare basins, valleys, ridges,
junctions, transport intent, geometry hints, and family-specific extensions.
It is not runtime evidence by itself.

In this example family:

```text
LandscapeSeed:
    normalized source document

GRCL9V3 extension:
    source-side terms that can be compiled to a GRCL9V3 source document

GRC9V3:
    runtime target after lowering

telemetry:
    runtime evidence after execution
```

The important discipline is:

```text
source declaration != runtime event
```

The seed can say a critical region is intended to be a hybrid-spark positive
control. Only the lowered runtime and telemetry can show whether a candidate
or expansion event occurred.

## References

- [Landscape Language Reference Guide](../../docs/reference/LandscapeLanguage-ReferenceGuide.md)
- [Landscape Compiler And Lowering Reference Guide](../../docs/reference/LandscapeCompiler-ReferenceGuide.md)
- [GRC Runtime Reference Guide](../../docs/reference/GRC-Runtime-ReferenceGuide.md)
- [Telemetry Reference Guide](../../docs/reference/Telemetry-ReferenceGuide.md)
