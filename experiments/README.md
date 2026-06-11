# Experiments

This directory contains historical evidence lanes for graph-native and LGRC
Reflexive Coherence work. These lanes are not product demos. They are bounded
research records with explicit claim ceilings, controls, reports, and artifacts.

## Reconstruction Pattern

Use this sequence when inspecting or rerunning a lane:

1. Read the lane `README.md` for its question, claim boundary, and non-claims.
2. Read `implementation/` for the staged plan, checklist, and closeout notes.
3. Inspect `configs/` and `hypotheses/` when present to understand fixtures and
   expected controls.
4. Run or inspect `scripts/` for the reconstruction path.
5. Compare regenerated or committed `outputs/` against `reports/`.
6. Treat `claim_ceiling`, blocked flags, and control results as part of the
   evidence, not as side commentary.

Experiment-local `outputs/` may be committed as historical evidence when they
are selected for public inspection. They must use relative paths and avoid
machine-local state.

## Lane Index

| Lane | Focus | Reconstruction entry |
| --- | --- | --- |
| [N01 GRC9V3 properties](2026-05-N01-grc9v3-properties/README.md) | Port, row, column, routing, refinement, and identity behavior in `GRC9V3`. | README, then `implementation/`, `hypotheses/`, `scripts/`, `reports/`, `outputs/`. |
| [N02 GRC9V3 metric mesh](2026-05-N02-grc9v3-metric-mesh/README.md) | `GRC9V3` as graph-native metric support for field patterns and observer-backed motion. | README, then configs/hypotheses and script/report pairs. |
| [N03 polarized basin loops](2026-05-N03-grc9v3-polarized-basin-loops/README.md) | Conserved source/sink-aspect loops, packetized causal mechanisms, and execution-surface boundaries. | README, then `scripts/`, raw records under `outputs/`, and reports. |
| [N04 movement ladders](2026-05-N04-grc9v3-movement-ladders/README.md) | Movement taxonomy, boundary coupling, support shifts, and bounded movement claim ceilings. | README, then implementation checklist, validator outputs, and reports. |
| [N05 coherence waves and oscillators](2026-05-N05-lgrc-coherence-waves-oscillators/README.md) | LGRC delayed pulses, reflected/amplified returns, repeated cycles, and oscillator candidates. | README, then `scripts/run_n05_iteration_*.py`, `outputs/`, and `reports/`. |
| [N06 semantic route choice](2026-05-N06-lgrc-semantic-route-choice/README.md) | Runtime-visible route alternatives, native arbitration, context-conditioned selection, and controls. | README, then fixture manifest, iteration scripts, outputs, and reports. |
| [N07 RC identity attractor invariance](2026-05-N07-rc-identity-attractor-invariance/README.md) | Identity/support evidence, bounded non-destructive exchange, and withdrawal/restoration baselines. | README, then iteration scripts, output artifacts, and closeout reports. |
| [N08 memory trail affordance](2026-05-N08-lgrc-memory-trail-affordance/README.md) | Route-use memory, trail/affordance surfaces, producer-policy memory, and geometry-mediated alternatives. | README, then scripts, outputs, reports, and hypothesis notes. |
| [N09 goal-proxy regulation](2026-05-N09-lgrc-goal-proxy-regulation/README.md) | Runtime-visible proxy measurement, bounded correction, support dependence, and native-substrate blockers. | README, then iteration scripts, output artifacts, and reports. |
| [N10 agentic-like integration](2026-05-N10-lgrc-agentic-like-integration/README.md) | Bounded composition of route choice, memory-shaped affordance, identity/support baseline, and proxy regulation. | README, then hypothesis closeouts in `outputs/` and matching reports. |
| [N11 general agentic-like integration](2026-05-N11-lgrc-general-agentic-like-integration/README.md) | Transfer across context, support state, proxy condition, and horizon while preserving claim boundaries. | README, then final closeout script/output and reports. |

Roadmap-level context:

- [N05-N11 LGRC Agentic-Like Foundation Roadmap](N05-N11-LGRC-AgenticLikeFoundationRoadmap.md)
- [N12-N18 LGRC Agency Prerequisites Roadmap](N12-N18-LGRC-AgencyPrerequisitesRoadmap.md)
- [N12-N18 LGRC Agency Prerequisites Handoff](N12-N18-LGRC-AgencyPrerequisitesHandoff.md)
