# Changelog

This changelog records notable repository-level research, runtime, evidence,
compatibility, and project-structure milestones. Detailed experiment iterations
remain in their experiment checklists, reports, and closeout artifacts.

The repository does not yet publish tagged package releases. Until a package
release policy is established, dated entries below are research-repository
milestones rather than semantic-version releases. The package metadata remains
at `version = "0.1"`.

## Unreleased

No repository-level milestone has been recorded after 2026-07-12.

## Research Repository Milestone - 2026-07-12

### Runtime And Substrate

- Expanded the executable `LGRC9V3` causal-history substrate with native packet
  loops, causal-pulse surfaces, topology-state reabsorption, time-scoped lineage
  replay, route arbitration, and associated replay/control surfaces. The
  [Phase 8 handoff](implementation/Phase-8-LGRC9-Handoff.md) indexes the
  individual implementation closeouts and their bounded claims.
- Added default-off native multi-basin formation support, including causal
  boundary birth, flow-window and child-basin extraction, replay validation,
  merge/leakage controls, telemetry, and visual examples. See the
  [multi-basin closeout](implementation/Phase-8-LGRC9-MultiBasinFormationCloseout.md).
- Added the versioned public
  `lgrc9v3_restoration_identity_v1` contract over canonical embedded GRC9V3
  state, native LGRC runtime state, events, and observables. Raw snapshot
  representation remains separately observable; snapshot schema and runtime
  behavior remain unchanged. See the
  [restoration-identity closeout](implementation/Phase-8-LGRC9-RestorationIdentityCloseout.md).

### Experiments And Evidence

- **N12-N19: agency-prerequisite and native-readiness review.** Extended the
  N05-N11 foundation into an AP3-AP8 artifact-evidence and native-readiness
  review. N19 records that AP4/AP5 NAT4 gaps remain explicit blockers rather
  than being hidden by later artifact-level evidence. See the
  [N19 closeout](experiments/2026-06-N19-lgrc-native-naturalization-review-ap3-ap8/reports/n19_closeout_and_handoff.md).
- **N20-N28: becoming primitives and composition evidence.** Added bounded
  contracts and source-current evidence for withdrawal resistance,
  naturalization depth, susceptibility update, live-continuation collapse,
  abundance/optionality, basin formation, participant divergence,
  configuration transfer, and generative/extractive persistence. The arc ends
  with replay- and stress-backed persistence regimes and an explicit handoff
  toward composition rather than semantic agency. See the
  [N20-N29 roadmap](experiments/N20-N29-LGRC-BecomingAgencyEcologyRoadmap.md)
  and [N28 closeout](experiments/2026-06-N28-lgrc-generative-vs-extractive-persistence/reports/n28_closeout_and_n29_handoff.md).
- **N25/N25.1/N25.2: multi-basin formation resolution.** Distinguished existing
  sparks and sub-basin refinements from missing native multi-basin formation,
  specified the Phase 8 extension from theory-backed sources, and validated the
  implemented runtime through the MB6 bridge. This supports scoped N26-ready
  multi-basin substrate evidence, not unrestricted basin formation or agency.
  See the [N25.2 closeout](experiments/2026-06-N25.2-lgrc9v3-mb6-validation-bridge/reports/n25_2_closeout_and_n26_handoff.md).
- **N29: agentic-ecology convergence bridge.** Closed at `EB6` / `N29-C6` with
  an evidence-backed prototype atlas, ecology demand/supply mapping, runnable
  bridge compositions, consumption contracts, and explicit producer/nativity
  debt. N29 establishes how downstream projects can consume the runtime and
  pattern library without turning producer-mediated results into native
  support. See the
  [N29 closeout](experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/reports/n29_closeout_and_ecology_handoff_i18.md).
- **N30: minimal shared-medium participation.** Closed at `N30-C6` with
  source-current evidence for participant continuity, perturbation of a
  declared non-private medium surface, persistent medium traces, and later
  eligibility/susceptibility dependence. N30 establishes a grounded minimum
  shared-medium relation and an alternating LGRC/ecology development spiral;
  it does not establish communication, coordination, cooperation, agency, or
  native ecology. See the
  [N30 closeout](experiments/2026-07-N30-lgrc-minimal-shared-medium-participation/reports/n30_closeout_and_spiral_handoff_i8.md).

### Project Structure And Documentation

- Reframed the repository as a core runtime plus a reusable pattern and
  contract library. Experiments remain the incubation and evidence layer;
  downstream projects can consume admitted patterns while retaining explicit
  extension and nativity debt.
- Added the [Claim Boundary Index](docs/reference/ClaimBoundaryIndex.md) as the
  detailed evidence map behind the compact top-level README claim table.
- Added the [N30+ catalog roadmap](experiments/N30_plus_experiment_catalog_roadmap.md)
  and [candidate directions](experiments/N30_plus_candidate_directions.md),
  distinguishing primitives, building blocks, motifs, and regimes while
  preserving bidirectional discovery between substrate evidence and ecology
  demand.
- Expanded experiment reconstruction indexes, handoff records, visual evidence
  galleries, contribution guidance, and source-artifact consumption rules.

### Compatibility And Claim Boundaries

- Preserved existing snapshot schemas and old supported snapshots while adding
  an additive LGRC9V3 restoration identity. Canonical serialization does not
  imply raw re-snapshot byte equality after legitimate loader normalization.
- Kept experiment-side producers, medium state, and naturalization debt
  explicit. Producer-assisted success does not silently upgrade native runtime
  support.
- Continued to block claims of native agency, native ant/colony agency,
  semantic goal ownership, sentience, organism/life, general cooperation or
  exploitation, unrestricted autonomy, and completion of Phase 8 as a whole.

## First Public GitHub Snapshot - 2026-06-11

The first public snapshot published the repository as a source-installable
research workspace rather than a tagged package release. Full narrative notes
are retained in [RELEASE-NOTES.md](RELEASE-NOTES.md).

### Added

- Public contribution, citation, code-of-conduct, changelog, and repository
  orientation metadata.
- Runnable `pygrc` source surfaces for `GRCV2`, `GRCV3`, `GRC9`, `GRC9V3`, and
  `LGRC9V3`, together with papers, specs, implementation records, examples,
  tests, telemetry, and visualization packages.
- A quickstart path from landscape-authored `GRCL9V3` seed through runtime,
  telemetry, and graph rendering.
- The N05-N11 LGRC agentic-like foundation arc with explicit claim ceilings.
- Experiment reconstruction and publication-readiness indexes.

### Changed

- Clarified that top-level outputs are scratch artifacts while selected
  experiment-local outputs may be retained as historical evidence.
- Clarified mixed license and citation boundaries across the repository.
- Established package-facade guidance and explicit limits on deep implementation
  imports and black-box API stability.

### Boundaries

- The snapshot did not constitute a tagged package release.
- Agency, biological identity, personhood, and general-intelligence claims
  remained outside the supported evidence boundary.
