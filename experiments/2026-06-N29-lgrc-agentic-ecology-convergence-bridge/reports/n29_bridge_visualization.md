# N29 Bridge Visualization

Status: `passed`

Output digest: `2c5dfc697230a783c564bdefc9db044134cc31b056be051c48336c17f50fb6f2`

These visuals summarize the N29 bridge atlas and probe-contract handoff. They are generated from existing JSON artifacts and do not add evidence.

Visual outputs:

```text
bridge_atlas_graph_static = experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/outputs/n29_bridge_visualization/n29_bridge_atlas_graph.png
bridge_atlas_sequence_static = experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/outputs/n29_bridge_visualization/n29_bridge_atlas_sequence.png
bridge_atlas_sequence_animation = experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/outputs/n29_bridge_visualization/n29_bridge_atlas_animation.gif
prototype_atlas_panel = experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/outputs/n29_bridge_visualization/n29_prototype_atlas_panel.png
probe_contract_expansion_panel = experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/outputs/n29_bridge_visualization/n29_probe_contract_expansion.png
prototype_d_motif_medium_reshaping_panel = experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/outputs/n29_bridge_visualization/n29_prototype_d_motif_panel.png
```

Boundary:

```text
visual_proof_allowed = false
runtime_probe_executed = false
ecology_success_supported = false
native_ecology_supported = false
agency_claim_allowed = false
phase8_completion_opened = false
```

Source artifacts:

| Source | Artifact | Digest |
| --- | --- | --- |
| `i15_prototype_atlas` | `n29_prototype_atlas_classification_i15` | `e139dd61fcd2b0998282033e5fe1a041891291d5db036982063e510be33f7cd2` |
| `i16_minimal_contract` | `n29_minimal_ecology_probe_contract_i16` | `d34e209f2b97aeac6242279f1c887afbf4c2064dcdc6a8fe0dc29cfa1275ac53` |
| `i17_alternative_contract` | `n29_alternative_ecology_probe_contract_i17` | `d2af854a4065351aaed23e74ac7c77dc7ec495765b32cccd69019b20e31c6798` |
| `i17a_full_contract` | `n29_full_bridge_probe_contract_i17a` | `f135650c01d2d74c3eb9c33e8b923542077beb8e7b2e723f36a2f7be1f68d981` |
| `i18_closeout` | `n29_closeout_and_ecology_handoff_i18` | `fa21662f0a69d582bfe574311110f2610a21e6e4e352991823ce47280e0e8ff5` |
| `i14y_prototype_d_synthesis` | `n29_prototype_d_complete_synthesis_i14y` | `aae7a30f8f911cbfb79d32602d7049a1907be3746152844eace7e3aebf29d6be` |

Interpretation:

- `n29_bridge_atlas_graph.png` shows the N05-N28 stack as shared source/claim constraints, then the N29 prototype atlas, I15 bridge dependency seeds, exact I16/I17/I17-A seed consumption, and closeout handoff.
- `n29_prototype_atlas_panel.png` isolates the four prototype families A-D and their evidence/debt ceilings.
- `n29_probe_contract_expansion.png` shows the contract progression from I16 A+B to I17 A+B+C to I17-A A+B+C+D.
- `n29_prototype_d_motif_panel.png` explains the Prototype D lane split: native/source-current rows emit local medium-reshaping motifs, while producer-mediated composition orders multi-leg handoff, phase, and leakage handling as explicit naturalization debt.

The repository index links the graph, sequence, and panels to full-size static images for zooming. The animation is generated as an auxiliary artifact, but it is not the primary inspection path.
