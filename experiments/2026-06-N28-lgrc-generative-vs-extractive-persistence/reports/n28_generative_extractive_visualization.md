# N28 Generative / Extractive Persistence Visualization

Status: `passed`

Output digest: `5d425668e294b37e5561904d0e3ad6f01b1eba2ffecafb68f4343f7aed19c349`

This visualization is a source-backed diagnostic projection over four N28
pattern classes. The plotted deltas are local focal-basin and neighborhood
capacity metrics, not global total-coherence deltas:

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
conservation_caveat = The visualization plots local focal-basin and neighborhood capacity metrics; it does not plot or audit global total-coherence invariance.
global_total_coherence_invariance_audited = false
global_total_coherence_checksum_present = false
local_metric_deltas_are_total_coherence_deltas = false
broad_margin_robustness_supported = false
ap4_nat4_gap_resolved = false
ap5_nat4_gap_resolved = false
```

Conservation caveat:

The plotted before/after bars are local focal-basin and neighborhood capacity
metrics. They should not be read as global total-coherence changes. N28 records
environment-capacity budget compatibility, but it does not compute a global
total-coherence checksum before/after the visualized rows.
