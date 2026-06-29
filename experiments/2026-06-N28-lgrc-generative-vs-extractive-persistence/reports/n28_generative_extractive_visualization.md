# N28 Generative / Extractive Persistence Visualization

Status: `passed`

Output digest: `18947ccd7b1c5bacc7c7a7e80c84332d602a8076c95b7d2a8a6e9e00ec138817`

This visualization is a source-backed diagnostic projection over four N28
pattern classes:

| Class | Source row | Env delta | Support delta | Boundary delta | Classification |
| --- | --- | --- | --- | --- | --- |
| `generative_enrichment` | `n28_i4_row_primary_generative_candidate` | `+0.123` | `+0.082` | `+0.126` | `generative` |
| `extractive_persistence` | `n28_i4b_row_primary_extractive_contrast` | `-0.069` | `-0.063` | `-0.081` | `extractive` |
| `competitive_redistribution` | `n28_i4d_row_primary_competitive_neutral_contrast` | `+0.004` | `+0.006` | `-0.012` | `competitive` |
| `neutral_circulation` | `n28_i4e_row_competitive_neutral_mechanism_diversity_contrast` | `-0.002` | `-0.006` | `+0.007` | `neutral` |

Visual outputs:

```text
graph_png = experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/outputs/n28_generative_extractive_visualization/n28_generative_extractive_pattern_graph.png
sequence_png = experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/outputs/n28_generative_extractive_visualization/n28_generative_extractive_pattern_sequence.png
animation_gif = experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/outputs/n28_generative_extractive_visualization/n28_generative_extractive_pattern_animation.gif
```

Boundary:

```text
visual_proof_allowed = false
renderer_boundary = source-backed diagnostic projection from recorded N28 row metrics; not a new proof layer and not a full runtime geometry replay
broad_margin_robustness_supported = false
ap4_nat4_gap_resolved = false
ap5_nat4_gap_resolved = false
```
