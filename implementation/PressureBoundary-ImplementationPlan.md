# Pressure Boundary Implementation Plan

## Purpose

This document defines a cross-family pressure-boundary extension for GRC9,
GRC9V3, GRCV3, and their GRCL source layers.

The extension follows the corrected growth interpretation established in
`GRC9-GRCL9-GrowthCorrection-Plan.md`: birth remains governed by outward flux
pressure, but a node with an inactive port is not automatically a valid growth
parent. Paper-facing growth must occur at an explicit frontier, front, seed, or
boundary-capacity site.

`pressure_boundary` names one such frontier provenance. It is not a new birth
law and it is not a replacement for the corrected front-capacity modes.

## Source Anchors

- `papers/2026-04-GRC-9.md`
  - Section 8.3: spark expansion creates new boundary capacity.
  - Section 8.4: front growth fills inactive ports using outward flux pressure.
  - Section 11: the full loop includes front/seed growth rules.
- `papers/2026-02-GRC-V3.md`
  - active frontier nodes are the sites for birth/front propagation.
  - outward flux pressure controls birth probability.
- `papers/2025-11-FractalReflexiveCoherence.md`
  - system boundary exchange is a separate open-system concept and must not be
    conflated with internal growth-front eligibility.

## Boundary Taxonomy

This track distinguishes four related meanings of boundary.

### Internal Ridge Boundary

An internal ridge or membrane separates basins. It is primarily a semantic or
geometric source-language role. It may be high-gradient, low-leakage, and
persistent, but it does not by itself imply birth eligibility.

### Valley Channel

A valley channel is a conductive passage through or across a separating
boundary. It should be judged by conductance, flux direction, and potential
alignment, not by boundary status alone.

### Growth Frontier / Pressure Boundary

A pressure boundary is a frontier eligibility carrier for growth. It marks an
inactive port on a live node as part of a front, seed, or exposed boundary
capacity. Birth probability still comes from outward flux pressure:

```text
p_birth(i) = 1 - exp(-lambda * F_i^out)
```

Once birth occurs, attachment uses the lowest-indexed eligible inactive port.

### System Boundary

A system boundary is an agent/environment exchange surface. It is associated
with external flux terms such as `Phi_in` and `Phi_out`. This track does not
implement open-system exchange or budget changes through the environment.

## Pressure Boundary Definition

A pressure boundary is valid growth-front provenance when all of the following
hold:

1. The parent node is live.
2. The parent has at least one inactive port.
3. The inactive port is explicitly marked as front-capacity eligible.
4. The capacity source is `pressure_boundary` or a more specific source that
   maps to pressure-boundary semantics.
5. The parent has positive outward flux pressure when the birth rule is
   evaluated.

This makes capacity and pressure separate gates:

```text
eligible_ports(i) = inactive_ports(i) intersect front_capacity_ports(i)

if eligible_ports(i) is empty:
    no birth candidate
else:
    p_birth(i) = 1 - exp(-lambda * F_i^out)
    selected_port = min(eligible_ports(i))
```

The broad condition `deg_act(i) < 9` is only a capacity precondition. It is not
the full boundary/frontier eligibility rule.

## Cross-Family Mapping

### GRC9

GRC9 already has the corrected runtime mode:

```text
growth_parent_eligibility = grc9_front_capacity
```

This track should add `pressure_boundary` as an accepted front-capacity source,
not as a third growth mode. Telemetry should distinguish:

- corrected front-capacity growth,
- pressure-boundary-sourced front growth,
- legacy broad growth.

### GRCL-9

GRCL-9 source documents should allow authored front-capacity declarations to
use:

```text
front_capacity_source = pressure_boundary
```

Legacy `growth_locus` remains replay-only. Paper-facing source examples should
compile to corrected front-capacity metadata and should not enable broad
inactive-port growth.

### GRC9V3

GRC9V3 should mirror GRC9 at the hybrid runtime level:

```text
growth_parent_eligibility = grcl9v3_front_capacity
front_capacity_source = pressure_boundary
```

The pressure-boundary label should be visible in telemetry and selectors
without changing the GRC9V3 differential, tensor, choice, or collapse
semantics.

### GRCL-9V3

GRCL-9V3 should use the same authored source concept as GRCL-9 while preserving
hybrid-specific evidence:

- source declares pressure-boundary front capacity,
- lowering records expected pressure-boundary regions,
- replay uses corrected front-capacity mode,
- selectors compare expected pressure-boundary regions with observed growth,
  transport, and basin changes.

### GRCV3 / GRCL-V3

GRCV3 already speaks in terms of active frontier nodes. This track should not
force nine-port mechanics into GRCV3. Instead it should align vocabulary and
telemetry so that GRCL-V3 can declare pressure-boundary frontier intent and the
runtime can report active-frontier birth evidence when available.

## Non-Claims

This track does not claim:

- boundary-barrier or ghost-node runtime behavior,
- Lorentzian causal boundary semantics,
- open-system environmental exchange,
- ridge/membrane classification from pressure boundary alone,
- broad inactive-port growth as paper-facing evidence,
- automatic invalidation of corrected front-capacity evidence that does not use
  `pressure_boundary`.

## Iteration Plan

### Iteration 1: Theory And Vocabulary Definition

- Define pressure boundary as a frontier/capacity provenance term.
- Record its relationship to outward flux pressure and lowest-port attachment.
- Distinguish pressure boundary from ridge, valley, and system boundary.
- Record cross-family ownership.

Status: complete in this document.

### Iteration 2: GRC9 And GRCL-9 Schema/Telemetry Extension

- Add `pressure_boundary` to GRC9 front-capacity source validation.
- Add `pressure_boundary` to GRCL-9 source schema validation.
- Preserve corrected `grc9_front_capacity` runtime mode.
- Add telemetry selectors for pressure-boundary-sourced growth.
- Add minimal GRC9/GRCL-9 examples and tests.

Status: complete. GRC9 now recognizes `pressure_boundary` as an accepted
front-capacity source in corrected growth mode. GRCL-9 source documents can use
`front_capacity_source = pressure_boundary` under `growth_semantics =
front_capacity` without requiring a spark/refinement source construct. GRCL-9
replay summaries now expose lowered front-capacity source metadata, and selector
validation includes an opt-in `pressure_boundary_growth_provenance` selector
for pressure-boundary-specific source fixtures.

### Iteration 2.1: Telemetry And Selector Cleanup

- Add run-summary counting for pressure-boundary-sourced growth.
- Require corrected front-capacity mode inside the pressure-boundary selector.
- Add negative selector coverage for declared pressure-boundary sources without
  observed growth.
- Keep replayable pressure-boundary fixture generation in Iteration 3.

Status: complete. `GRC9GrowthSummary` now includes
`pressure_boundary_growth_count`, the GRC9 run-summary builder populates it from
growth events whose capacity source is `pressure_boundary`, and the GRCL-9
selector requires `growth_parent_eligibility_mode = grc9_front_capacity` plus
matching pressure-boundary growth counts.

### Iteration 3: GRC9 Pressure-Boundary Evidence Runs

- Run elementary positive and negative controls.
- Run one composed spark-expansion-pressure-boundary growth lane.
- Record sessions under `outputs/`.
- Compare against corrected front-capacity evidence and legacy broad-growth
  non-evidence.

Status: complete. Direct GRC9 evidence was generated in `S0038` and `S0039`.
`S0038` contains elementary corrected front-capacity controls, including a
pressure-boundary positive lane and a pressure-boundary zero-pressure control.
`S0039` contains composed corrected-growth lanes, including a connected
spark-expansion-pressure-boundary-growth lane. GRCL-9 source-backed evidence was
generated in `outputs/grcl9/lowering/sessions/S0038` and selector-validated in
`S0039`; the pressure-boundary source fixture was accepted with
`pressure_boundary_growth_provenance` and no missing surfaces.

### Iteration 4: GRC9V3 And GRCL-9V3 Extension

- Add `pressure_boundary` to GRC9V3/GRCL-9V3 source and lowering surfaces.
- Preserve `grcl9v3_front_capacity` as the runtime mode.
- Add expected-region caches for pressure-boundary declarations.
- Expose pressure-boundary capacity-source metadata in replay summaries.
- Add the base pressure-boundary hybrid selector surface without yet requiring
  evidence runs.

Status: complete. The current implementation covers schema acceptance,
lowering provenance, expected-region cache exposure, replay summary metadata,
and base selector missing-surface behavior. Pressure-specific hybrid growth
counts and evidence sessions remain intentionally staged in Iterations 4.1 and
4.2.

### Iteration 4.1: GRC9V3 Telemetry And Selector Cleanup

- Add run-summary counting for pressure-boundary-sourced hybrid growth.
- Keep aggregate corrected front-capacity growth separate from
  pressure-boundary growth.
- Require corrected `grcl9v3_front_capacity` mode inside the pressure-boundary
  selector predicate.
- Add negative selector coverage for declared pressure-boundary sources without
  observed growth.
- Add negative selector coverage for generic front-capacity growth that should
  not count as pressure-boundary growth.
- Keep replayable pressure-boundary fixture generation in Iteration 4.2.

Status: complete. The hybrid run summary now separates aggregate corrected
front-capacity growth, pressure-boundary-sourced growth, and legacy broad
growth, and the pressure-boundary selector rejects no-growth, legacy-mode, and
generic-front-capacity cases before evidence sessions are generated.

### Iteration 4.2: GRC9V3 / GRCL-9V3 Pressure-Boundary Evidence Runs

- Add elementary GRC9V3 pressure-boundary positive and negative controls.
- Add GRCL-9V3 pressure-boundary source-backed fixture.
- Run replayable GRC9V3 and GRCL-9V3 sessions under `outputs/`.
- Validate pressure-boundary hybrid selectors.
- Confirm tensor, choice, collapse, and Appendix E semantics are unchanged by
  the pressure-boundary label.

Status: complete. Direct GRC9V3 evidence was generated in
`outputs/grc9v3/phenomenology_discovery/sessions/S0015`, with elementary
pressure-boundary, no-growth, generic-front-capacity comparison, and composed
spark-expansion-pressure-boundary-growth lanes. GRCL-9V3 source-backed evidence
was generated in `outputs/grcl9v3/lowering/sessions/S0073` and selector
validated in `outputs/grcl9v3/lowering/sessions/S0074`. The standard authored
GRCL-9V3 landscape-example suite now also includes
`pressure_boundary_positive_control`; that authored example was replayed in
`outputs/grcl9v3/lowering/sessions/S0075` and selector-validated in `S0076`.
The selector accepted both pressure-boundary source fixtures with no missing
surfaces; the GRCL replay
also emitted a normal `choice_detected` event, which is recorded as additional
hybrid runtime behavior rather than pressure-boundary evidence.

### Iteration 5: GRCV3 And GRCL-V3 Alignment

Align pressure-boundary vocabulary with GRCV3 active-frontier birth without
importing nine-port mechanics. This is a parent heading; implementation is
split into Iterations 5.1-5.5 because GRCV3 has different primitives from
GRC9/GRC9V3.

### Iteration 5.1: GRCV3 / GRCL-V3 Frontier Audit

- Inspect GRCV3 runtime growth/frontier semantics.
- Inspect GRCL-V3 vocabulary, source seeds, and lowering surfaces.
- Identify artifact-backed telemetry fields for active-frontier birth.
- Decide whether pressure boundary is runtime-backed, source-only, or reserved.
- Do not add source claims before this audit is complete.

Status: complete. See
[`PressureBoundary-GRCV3-FrontierAudit.md`](./PressureBoundary-GRCV3-FrontierAudit.md).
The current GRCV3 implementation has no growth/birth/frontier step, no growth
event domain, and no telemetry surface for birth probability or
pressure-boundary growth. GRCL-V3 does have boundary/interface vocabulary
(`boundary_roles`, `preferred_attachment_sites`, `boundary_geometry`,
`channel_geometry`) that can carry source-side alignment, but replayable
pressure-boundary evidence requires a new opt-in GRCV3 birth/frontier runtime
surface. The absence of that opt-in mode must preserve the existing no-birth
GRCV3 implementation. Concretely, missing `frontier_birth_mode` is equivalent
to `frontier_birth_mode = disabled`; only explicit
`frontier_birth_mode = active_frontier_pressure` may activate new birth code.

### Iteration 5.2: GRCL-V3 Vocabulary Alignment

- Map pressure boundary to active-frontier language where supported.
- Add GRCL-V3 vocabulary/doc notes without adding GRC9 port concepts.
- Explicitly state that GRCV3 does not use `front_capacity_source` or
  nine-port eligibility.
- Define the opt-in runtime switch contract:
  `frontier_birth_mode = disabled | active_frontier_pressure`.
- State that missing `frontier_birth_mode` means `disabled`.
- Define the strictness switch:
  `frontier_birth_strict = warn | error | allow`.
- State that authored pressure-boundary/frontier seeds should prefer
  `frontier_birth_mode = active_frontier_pressure`; disabled or missing mode is
  for legacy compatibility and explicit no-birth controls.
- Reserve unsupported source/runtime surfaces outside the opt-in mode.

Status: complete. `GRCL-V3-Vocabulary.md` now defines pressure boundary as
`GRCV3` active-frontier/interface intent, keeps it separate from ridge,
valley, and system-boundary meanings, reserves runtime evidence until the
opt-in mode exists, and explicitly rejects GRC9/GRC9V3
`front_capacity_source` and nine-port eligibility.

### Iteration 5.3: GRCV3 Opt-In Frontier Birth Runtime

- Add a default-off GRCV3 runtime mode:
  `frontier_birth_mode = active_frontier_pressure`.
- Preserve current behavior when `frontier_birth_mode` is absent or
  `disabled`.
- Add regression coverage showing that missing mode and explicit `disabled`
  mode produce the same step outputs as the current no-birth implementation.
- Validate unknown `frontier_birth_mode` values as errors.
- Validate unknown `frontier_birth_strict` values as errors.
- Use `frontier_birth_strict = error` to stop source/evidence runs that declare
  frontier-birth candidates while leaving birth disabled.
- Use `frontier_birth_strict = allow` only for explicit no-birth controls and
  legacy compatibility lanes.
- Select eligible parents from explicit frontier metadata, not generic graph
  boundary guesses.
- Compute outward flux pressure and create neutral-basin newborn nodes only in
  the opt-in mode.
- Preserve GRCV3 budget invariants during birth.
- Emit family-native birth/frontier events without importing GRC9 port fields.

Status: complete. `GRCV3` now accepts the opt-in
`frontier_birth_mode = active_frontier_pressure` mode while leaving missing
mode absent from resolved defaults. Missing mode and explicit
`frontier_birth_mode = disabled` both preserve no-birth behavior. The opt-in
path reads explicit `GRCV3` frontier metadata, computes outward flux pressure
from runtime flux, emits `frontier_birth` events, transfers coherence from
parent to child, and uses `frontier_source = pressure_boundary` style
provenance without importing GRC9/GRC9V3 port fields.
When frontier-birth candidate metadata is present but
`frontier_birth_mode` is missing or disabled, `GRCV3.step()` emits a one-time
runtime warning explaining that node birth is disabled and
`frontier_birth_mode = active_frontier_pressure` is required to enable
pressure-boundary node birth.
`frontier_birth_strict = error` stops source/evidence runs that declare
frontier-birth candidates while leaving birth disabled. Explicit disabled or
missing-mode compatibility lanes should use `frontier_birth_strict = allow`
when they intentionally test no-birth behavior.

### Iteration 5.4: GRCV3 Telemetry And Selector Mapping

- Add GRCV3 telemetry for opt-in frontier birth:
  birth counts, frontier source, birth rule, and pressure summary.
- Add GRCL-V3 source/lowering telemetry for pressure-boundary frontier intent.
- Add selectors only for artifact-backed fields.
- Report missing surfaces explicitly when opt-in runtime telemetry is absent.
- Keep selector names distinct from GRC9/GRC9V3 pressure-boundary selectors
  when the underlying fields differ.

Status: complete. GRCV3 telemetry now exposes a compact
`frontier_birth_state` step-row group and `frontier_birth_summary` run-summary
group. These surfaces report the opt-in mode, birth rule, explicit frontier
candidate counts, pressure-boundary birth counts, observed frontier sources,
outward flux pressure summaries, and birth-probability summaries. Event
classification maps `frontier_birth` to the family-native `birth/created`
domain/stage. A focused pressure-boundary selector validates
`frontier_source = pressure_boundary` evidence and distinguishes
`missing_surface` from `predicate_failed`.

### Iteration 5.5: GRCV3 / GRCL-V3 Evidence Run

- Add a GRCL-V3 source example that explicitly lowers into
  `frontier_birth_mode = active_frontier_pressure`.
- Run replayable GRCV3 / GRCL-V3 pressure-boundary/frontier evidence under
  `outputs/`.
- Verify that old seeds without `frontier_birth_mode` remain no-birth.
- Rerun representative old output sessions and compare observed telemetry/event
  results against the recorded artifacts before accepting compatibility.
- Store any produced sessions under `outputs/` with replay commands.

Status: complete for pressure-boundary birth evidence. Session
`outputs/grcv3/pressure_boundary/sessions/S0001` records:

- a source-facing GRCL-V3 pressure-boundary frontier fixture,
- two compatibility lanes where missing or disabled `frontier_birth_mode`
  remains no-birth,
- one opt-in pressure-boundary lane with `frontier_birth_count = 1` and
  `pressure_boundary_birth_count = 1`,
- a replayed old GRCV3 rich seed under
  `compatibility_replay_choice_smoke`.

The compatibility replay confirms the pressure-boundary invariant: old
no-mode runs and replayed no-mode lanes do not emit `frontier_birth`. It also
records the legacy `choice_detected` counts separately. The old reference is a
single aggregate run with `choice_detected = 6`; the replay stores two matched
lanes with `choice_detected = 3` each, so aggregate event-count parity is true.

### Iteration 6: Cross-Family Comparison Runs

- Run comparable GRC9, GRC9V3, and GRCV3 examples when possible.
- Report what is shared: frontier pressure birth.
- Report what is family-specific: ports, hybrid tensors, or semantic basin
  state.

Status: complete. Session `outputs/pressure_boundary/cross_family/S0001`
compares the replay-backed pressure-boundary evidence from GRC9, GRCL-9,
GRC9V3, GRCL-9V3, and GRCV3. The shared observable is positive
pressure-boundary-sourced birth/growth with zero legacy broad-growth count.
All five rows pass. The report keeps family-specific surfaces separate:
GRC9/GRCL-9 use nine-port front-capacity growth, GRC9V3/GRCL-9V3 add hybrid
differential and choice/collapse surfaces, and GRCV3 uses opt-in
`frontier_birth` without nine-port claims.

Interpretation note: iteration 6 is a positive-evidence comparison, not a
legacy-vs-disabled compatibility replay. Legacy/missing/disabled no-birth
compatibility is checked in GRCV3 session `S0001`. The positive rows grow
because they explicitly provide pressure-boundary/front-capacity provenance and
enable the outward-flux birth rule
`p_birth = 1 - exp(-lambda_birth * F_out)`.

### Iteration 7: Catalog And Closeout

- Refresh reviewed catalogs with pressure-boundary evidence.
- Keep legacy broad-growth artifacts quarantined.
- Record which existing corrected front-capacity claims remain valid without
  pressure-boundary reruns.
- Add a handoff note for future boundary-barrier / ghost-node work.

Status: complete. The closeout evidence is the refreshed cross-family session
`outputs/pressure_boundary/cross_family/S0001`, regenerated after the GRCV3
strict-mode refinement. Accepted pressure-boundary evidence now comes from:

- GRC9: `outputs/grc9/phenomenology_discovery/sessions/S0038`
- GRCL-9: `outputs/grcl9/lowering/sessions/S0038` and selector session
  `S0039`
- GRC9V3: `outputs/grc9v3/phenomenology_discovery/sessions/S0015`
- GRCL-9V3: `outputs/grcl9v3/lowering/sessions/S0075`
- GRCV3: `outputs/grcv3/pressure_boundary/sessions/S0001`
- cross-family comparison:
  `outputs/pressure_boundary/cross_family/S0001`

The accepted catalog interpretation is narrow: pressure-boundary motifs are
accepted only when source/runtime metadata records pressure-boundary or
active-frontier provenance, the relevant corrected front-capacity or frontier
mode is active, and telemetry reports positive pressure-boundary-sourced
birth/growth with legacy broad-growth count `0`.

Legacy broad-growth runs, over-aggressive growth-locus runs, and no-birth
compatibility lanes are retained as historical controls only. They should not
be used as pressure-boundary evidence. Existing corrected front-capacity
evidence that does not use the `pressure_boundary` label remains valid for
generic corrected-front claims, but it should not be cited as
pressure-boundary-specific evidence.

Future scope remains separate: boundary-barrier behavior, ghost-node boundary
modes, Lorentzian causal boundary semantics, and open-system environmental
exchange are not implemented by this pressure-boundary track.

## Completion Criteria

The track is complete when:

- pressure boundary is a validated source/runtime provenance label,
- pressure-boundary growth runs only under corrected front-capacity modes,
- telemetry distinguishes pressure-boundary growth from generic front-capacity
  growth and legacy broad growth,
- at least one replayable evidence session exists for GRC9 and GRC9V3,
- GRCL-9 and GRCL-9V3 can author pressure-boundary examples without runtime
  smuggling,
- GRCV3/GRCL-V3 alignment is documented without over-claiming nine-port
  behavior,
- closeout docs state that this is an additive refinement, not a wholesale
  invalidation of corrected growth evidence.

Status: complete as of Iteration 7.

### Iteration 8: Complex Source Comparison Probe

This is an exploratory add-on, not a replacement for the Iteration 7 closeout.
The goal is to understand how complex GRC9 and GRC9V3 examples behave when the
same connected runtime shape is run under:

- legacy broad growth,
- corrected front-capacity growth for each accepted `front_capacity_source`,
- pressure-boundary-specific corrected growth.

The comparison should preserve the narrow closeout interpretation:

- legacy broad-growth rows are diagnostic controls only,
- front-capacity source variants are source-label sensitivity probes,
- only rows with explicit `pressure_boundary` provenance are
  pressure-boundary-specific,
- generic corrected-front rows remain valid only for generic corrected-front
  claims.

Expected output:

- replayable session under `outputs/pressure_boundary/complex_source_comparison`,
- one GRC9 complex comparison family,
- one GRC9V3 complex comparison family,
- summary table of event counts, growth counts, pressure-boundary counts,
  legacy-broad counts, and family-specific side effects.

Status: complete. Session
`outputs/pressure_boundary/complex_source_comparison/S0001` compares one
connected GRC9 complex example and one connected GRC9V3 complex example across
legacy broad growth and all accepted front-capacity sources.

Observed pattern:

- GRC9 legacy broad growth produced `38` growth events over the comparison
  window, all counted as `legacy_broad_growth_count`.
- GRC9V3 legacy broad growth produced `4` growth events over the comparison
  window, all counted as `legacy_broad_growth_count`.
- Every corrected GRC9 source variant produced one controlled growth event
  with `front_capacity_growth_count = 1` and
  `legacy_broad_growth_count = 0`.
- Every corrected GRC9V3 source variant produced one controlled growth event
  with `front_capacity_growth_count = 1` and
  `legacy_broad_growth_count = 0`.
- Only the `pressure_boundary` source variants produced
  `pressure_boundary_growth_count = 1`.

Interpretation: at current runtime level, accepted front-capacity sources are
provenance labels over the same corrected eligibility mechanism. They do not
change the birth law by themselves. The major behavioral difference is between
legacy broad parent eligibility and corrected front-capacity eligibility;
`pressure_boundary` is distinguished by telemetry provenance, not by a separate
growth equation.
