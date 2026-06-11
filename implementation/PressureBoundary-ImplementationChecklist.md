# Pressure Boundary Implementation Checklist

This checklist tracks the cross-family pressure-boundary extension.

Pressure boundary is a corrected-frontier provenance label. It does not replace
the birth probability rule, lowest-port rule, or existing corrected
front-capacity runtime modes.

## Usage Rules

- Do not use `pressure_boundary` to revive legacy broad inactive-port growth.
- Keep `deg_act < 9` as capacity only, not full frontier eligibility.
- Keep birth probability flux-pressure based.
- Keep selected birth port as the lowest eligible inactive port.
- Keep ridge/membrane, valley/channel, growth frontier, and system boundary
  meanings separate.
- Preserve all historical replay artifacts.
- Only use new pressure-boundary evidence for pressure-boundary claims.

## Status Terms

- `pressure_boundary_defined`: vocabulary and theory boundary are recorded.
- `pressure_boundary_source_validated`: source schema accepts the label.
- `pressure_boundary_runtime_validated`: runtime accepts the label only through
  corrected front-capacity eligibility.
- `pressure_boundary_evidence_candidate`: replayable run with observed
  pressure-boundary-sourced growth.
- `accepted_pressure_boundary_evidence`: reviewed evidence accepted into a
  refreshed catalog.

## Iteration 1. Theory And Vocabulary Definition

### Goal

Define pressure boundary as a frontier/capacity provenance term across GRC9,
GRC9V3, GRCV3, and their GRCL source layers.

### Checks

- [x] Create `PressureBoundary-ImplementationPlan.md`
- [x] Create `PressureBoundary-ImplementationChecklist.md`
- [x] State that pressure boundary is not a new birth law
- [x] State that `deg_act < 9` is a capacity precondition only
- [x] Preserve the birth probability:
  `p_birth(i) = 1 - exp(-lambda * F_i^out)`
- [x] Preserve lowest eligible inactive-port selection
- [x] Distinguish pressure boundary from internal ridge/membrane boundary
- [x] Distinguish pressure boundary from valley/channel structure
- [x] Distinguish pressure boundary from open-system environmental exchange
- [x] Map GRC9 ownership
- [x] Map GRCL-9 ownership
- [x] Map GRC9V3 ownership
- [x] Map GRCL-9V3 ownership
- [x] Map GRCV3 / GRCL-V3 alignment boundary

### Verification

- [x] Plan/checklist do not introduce a new broad-growth runtime mode
- [x] Plan/checklist keep corrected front-capacity migration intact
- [x] Plan/checklist state that existing corrected front-capacity evidence is
  not automatically invalidated

### Summary

Iteration 1 is complete when this planning pair is added and linked from the
main implementation phase index.

## Iteration 2. GRC9 And GRCL-9 Schema/Telemetry Extension

### Goal

Add pressure-boundary provenance to existing corrected GRC9/GRCL-9
front-capacity growth.

### Checks

- [x] Add `pressure_boundary` to GRC9 accepted front-capacity source values
- [x] Add `pressure_boundary` to GRCL-9 source schema validation
- [x] Preserve `growth_parent_eligibility = grc9_front_capacity`
- [x] Keep `legacy_any_inactive_port` replay-only
- [x] Ensure pressure-boundary sources lower into
  `grc9_front_growth_eligible_ports`
- [x] Ensure growth events record `growth_parent_capacity_source =
  pressure_boundary`
- [x] Add telemetry selector for pressure-boundary-sourced growth
- [x] Add tests for positive and no-pressure-boundary controls

### Verification

- [x] Unit test: pressure-boundary source emits corrected growth when pressure
  and eligible capacity are present
- [x] Unit test: pressure-boundary source emits no growth without positive
  outward pressure
- [x] Unit test: non-pressure inactive ports remain ineligible
- [x] Telemetry test: event/run summary distinguish pressure-boundary growth
  from generic front-capacity growth
- [x] Legacy broad-growth replay remains guarded

### Summary

Iteration 2 is complete. The GRC9 runtime now filters capacity-source metadata
through an accepted source set that includes `pressure_boundary`; GRCL-9 schema
round-trips `front_capacity_source = pressure_boundary`; GRCL-9 replay summaries
carry lowered `growth_parent_capacity_sources` and `front_growth_eligible_ports`;
and selector validation exposes `pressure_boundary_growth_provenance` as an
opt-in pressure-boundary evidence selector.

Verification:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_grc_9_expansion tests.landscapes.test_grcl9_schema tests.telemetry.test_grc9_contract tests.telemetry.test_grcl9_selector_validation
PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_grcl9_replay
PYTHONPATH=src ./.venv/bin/python -m py_compile src/pygrc/models/grc_9.py src/pygrc/landscapes/extensions/grcl9/schema.py src/pygrc/telemetry/grcl9_replay.py src/pygrc/telemetry/grcl9_selector_validation.py tests/models/test_grc_9_expansion.py tests/landscapes/test_grcl9_schema.py tests/telemetry/test_grc9_contract.py tests/telemetry/test_grcl9_selector_validation.py
```

## Iteration 2.1. Telemetry And Selector Cleanup

### Goal

Close the pressure-boundary-specific telemetry and selector gaps before
evidence sessions are generated.

### Checks

- [x] Add `pressure_boundary_growth_count` to `GRC9GrowthSummary`
- [x] Populate `pressure_boundary_growth_count` from growth events whose
  `growth_parent_capacity_source` is `pressure_boundary`
- [x] Keep `front_capacity_growth_count` as the aggregate corrected
  front-capacity count
- [x] Require `growth_parent_eligibility_mode = grc9_front_capacity` in the
  pressure-boundary selector predicate
- [x] Add `growth_parent_eligibility_mode` to pressure-boundary selector
  required field paths
- [x] Add selector test for declared pressure-boundary source without growth
- [x] Keep replayable pressure-boundary seed fixtures in Iteration 3

### Verification

- [x] Contract test covers `pressure_boundary_growth_count`
- [x] Builder test preserves zero pressure-boundary count on legacy growth
- [x] Selector test passes for corrected pressure-boundary growth
- [x] Selector test fails without growth
- [x] Selector test fails outside corrected front-capacity mode

### Summary

Iteration 2.1 is complete. Pressure-boundary growth is now distinguishable from
generic corrected front-capacity growth in GRC9 run summaries, and the GRCL-9
pressure-boundary selector is self-contained enough to reject legacy mode and
declared-but-unobserved pressure-boundary growth.

Verification:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_grc9_contract tests.telemetry.test_grc9_extensions tests.telemetry.test_grcl9_selector_validation tests.telemetry.test_grcl9_replay tests.models.test_grc_9_expansion tests.landscapes.test_grcl9_schema
PYTHONPATH=src ./.venv/bin/python -m py_compile src/pygrc/telemetry/grc9_contract.py src/pygrc/telemetry/_grc9_extensions.py src/pygrc/telemetry/grcl9_selector_validation.py tests/telemetry/test_grc9_contract.py tests/telemetry/test_grc9_extensions.py tests/telemetry/test_grcl9_selector_validation.py
```

## Iteration 3. GRC9 Pressure-Boundary Evidence Runs

### Goal

Produce replayable GRC9 pressure-boundary evidence without broad-growth
semantics.

### Checks

- [x] Add elementary pressure-boundary GRC9 seed
- [x] Add no-pressure-boundary negative control
- [x] Add zero-pressure control with capacity present
- [x] Add composed spark-expansion-pressure-boundary growth lane
- [x] Add GRCL-9 pressure-boundary seed-backed source fixture
- [x] Run sessions under `outputs/`
- [x] Record replay commands
- [x] Update discovery notes and catalog candidates

### Verification

- [x] Positive lane emits growth with `pressure_boundary` provenance
- [x] No-pressure-boundary lane emits no growth
- [x] Zero-pressure lane emits no growth
- [x] Composed lane preserves spark/expansion evidence and adds corrected
  pressure-boundary growth
- [x] Legacy broad-growth sessions remain non-evidence
- [x] GRCL-9 pressure-boundary selector validation passes with no missing
  surfaces

### Summary

Iteration 3 is complete. Direct GRC9 evidence:

- `outputs/grc9/phenomenology_discovery/sessions/S0038`
  - 6 lanes, 18 total steps, 2 growth events
  - `front_capacity_growth_pressure_boundary_positive_control` emitted one
    corrected growth event with `pressure_boundary_growth_count = 1`
  - `front_capacity_growth_pressure_boundary_zero_pressure_control` emitted no
    growth with pressure-boundary capacity present
  - no-front, zero-birth, and closed-front controls emitted no growth
- `outputs/grc9/phenomenology_discovery/sessions/S0039`
  - 4 lanes, 20 total steps, 10 total events
  - `corrected_spark_pressure_boundary_growth_combo` emitted spark, expansion,
    and one corrected pressure-boundary growth event
  - all lanes reported `legacy_broad_growth_count = 0`

GRCL-9 source-backed evidence:

- `outputs/grcl9/lowering/sessions/S0038`
  - fixture `corrected_pressure_boundary_positive_high`
  - event counts: spark 1, expansion 1, growth 1
  - `pressure_boundary_growth_count = 1`
- `outputs/grcl9/lowering/sessions/S0039`
  - selector validation accepted one motif
  - passed `pressure_boundary_growth_provenance`
  - missing surface count: 0

Replay:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_discovery_runner --session-id S0038 --corrected-growth-elementary
PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_discovery_runner --session-id S0039 --corrected-growth-combo
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9_replay --session-id S0038 --source-mode landscape_seed_examples --fixture corrected_pressure_boundary_positive_high --requested-steps 3
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9_selector_validation --session-id S0039 --source-session-id S0038
```

Verification:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.discovery.test_grc9_seed_generator tests.landscapes.test_grcl9_seed_examples tests.telemetry.test_grcl9_replay tests.telemetry.test_grcl9_selector_validation tests.telemetry.test_grc9_contract tests.telemetry.test_grc9_extensions
PYTHONPATH=src ./.venv/bin/python -m py_compile src/pygrc/discovery/grc9_seed_generator.py src/pygrc/discovery/grc9_discovery_runner.py src/pygrc/landscapes/extensions/grcl9/examples.py src/pygrc/telemetry/grcl9_replay.py tests/discovery/test_grc9_seed_generator.py tests/landscapes/test_grcl9_seed_examples.py tests/telemetry/test_grcl9_replay.py
```

## Iteration 4. GRC9V3 And GRCL-9V3 Extension

### Goal

Mirror pressure-boundary provenance in the hybrid runtime and source layer.

### Checks

- [x] Add `pressure_boundary` to GRC9V3 accepted front-capacity source values
- [x] Add `pressure_boundary` to GRCL-9V3 source schema validation
- [x] Preserve `growth_parent_eligibility = grcl9v3_front_capacity`
- [x] Lower pressure-boundary declarations into expected-region caches
- [x] Add step/run telemetry fields or reuse existing source/provenance
  surfaces
- [x] Expose `growth_parent_capacity_sources` in GRCL-9V3 replay summaries
- [x] Expose pressure-boundary expected-region cache names in replay summaries
- [x] Add base selectors for pressure-boundary hybrid growth

### Verification

- [x] Schema round-trip accepts `front_capacity_source = pressure_boundary`
- [x] Lowering preserves pressure-boundary source metadata
- [x] Replay summaries carry source-declared pressure-boundary metadata
- [x] Base selectors report missing surfaces explicitly when telemetry is not
  present
- [x] Tensor, choice, and collapse semantics are unchanged by the label

### Summary

Iteration 4 is complete. GRC9V3 now recognizes `pressure_boundary` as a valid
front-capacity source label, while GRCL-9V3 source documents can author the
same declaration without requiring a spark/refinement source construct id. The
lowerer records `grcl9v3_expected_pressure_boundary_region_ids`, replay
summaries expose both `growth_parent_capacity_sources` and
`growth_parent_eligibility_mode`, and selector validation has a base
`pressure_boundary_growth_provenance_present` selector with explicit
missing-surface reporting.

This iteration intentionally does not add the pressure-specific hybrid run
summary count or replayable evidence sessions; those remain in Iterations 4.1
and 4.2.

Verification:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_grcl9v3_schema tests.models.test_grc_9_v3_grcl9v3_lowering tests.telemetry.test_grcl9v3_replay tests.telemetry.test_grcl9v3_selector_validation
PYTHONPATH=src ./.venv/bin/python -m py_compile src/pygrc/landscapes/extensions/grcl9v3/schema.py src/pygrc/models/grc_9_v3.py src/pygrc/models/grc_9_v3_grcl9v3_lowering.py src/pygrc/telemetry/grcl9v3_replay.py src/pygrc/landscapes/extensions/grcl9v3/selector_expansions.py src/pygrc/telemetry/grcl9v3_selector_validation.py
```

## Iteration 4.1. GRC9V3 Telemetry And Selector Cleanup

### Goal

Mirror Iteration 2.1 for the hybrid stack before evidence sessions are
generated.

### Checks

- [x] Add `pressure_boundary_growth_count` or hybrid-equivalent field to the
  GRC9V3 run-summary growth surface
- [x] Populate pressure-boundary count from growth events whose
  `growth_parent_capacity_source` is `pressure_boundary`
- [x] Keep aggregate `front_capacity_growth_count` separate from
  pressure-boundary-specific count
- [x] Require `growth_parent_eligibility_mode = grcl9v3_front_capacity` in the
  pressure-boundary hybrid selector predicate
- [x] Add corrected-mode field path to pressure-boundary selector required
  fields
- [x] Add selector test for declared pressure-boundary source without growth
- [x] Add selector test for generic front-capacity growth that is not
  pressure-boundary growth
- [x] Keep replayable pressure-boundary fixtures in Iteration 4.2

### Verification

- [x] Contract test covers pressure-boundary growth count
- [x] Builder test preserves zero pressure-boundary count on generic
  front-capacity growth
- [x] Selector test passes for corrected pressure-boundary hybrid growth
- [x] Selector test fails without growth
- [x] Selector test fails outside corrected front-capacity mode
- [x] Selector test fails when growth is generic front-capacity rather than
  pressure-boundary-sourced

### Summary

Iteration 4.1 is complete. GRC9V3 run-summary lifecycle counts now include:

- `front_capacity_growth_count`
- `pressure_boundary_growth_count`
- `legacy_broad_growth_count`

The counts are derived from growth event payloads, with pressure-boundary growth
requiring both `growth_parent_eligibility_mode = grcl9v3_front_capacity` and
`growth_parent_capacity_source = pressure_boundary`. The GRCL-9V3
pressure-boundary selector now requires these run-summary fields and rejects
declared-but-unobserved, legacy-mode, and generic front-capacity growth.

Verification:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_grc9v3_contract tests.telemetry.test_grc9v3_extensions tests.telemetry.test_grcl9v3_selector_validation tests.telemetry.test_grcl9v3_replay tests.models.test_grc_9_v3_grcl9v3_lowering
PYTHONPATH=src ./.venv/bin/python -m py_compile src/pygrc/telemetry/grc9v3_contract.py src/pygrc/telemetry/_grc9v3_extensions.py src/pygrc/telemetry/grcl9v3_selector_validation.py tests/telemetry/test_grc9v3_extensions.py tests/telemetry/test_grcl9v3_selector_validation.py
```

## Iteration 4.2. GRC9V3 / GRCL-9V3 Pressure-Boundary Evidence Runs

### Goal

Produce replayable hybrid pressure-boundary evidence after schema, telemetry,
and selector cleanup are complete.

### Checks

- [x] Add elementary GRC9V3 pressure-boundary positive control
- [x] Add GRC9V3 pressure-boundary no-growth control
- [x] Add GRC9V3 generic-front-capacity comparison lane
- [x] Add GRCL-9V3 pressure-boundary source-backed fixture
- [x] Add authored GRCL-9V3 landscape example for pressure-boundary growth
- [x] Add composed spark-expansion-pressure-boundary-growth hybrid lane if
  current runtime supports it
- [x] Run sessions under `outputs/`
- [x] Record replay commands
- [x] Update reviewed candidates or handoff notes

### Verification

- [x] Positive hybrid lane emits growth with pressure-boundary provenance
- [x] No-growth control emits no growth with pressure-boundary capacity present
- [x] Generic front-capacity lane does not increment pressure-boundary count
- [x] GRCL-9V3 selector validation passes with no missing surfaces
- [x] Tensor, choice, collapse, and Appendix E summaries remain interpretable

### Summary

Iteration 4.2 is complete. Direct GRC9V3 evidence:

- `outputs/grc9v3/phenomenology_discovery/sessions/S0015`
  - 4 lanes, 13 total steps, 6 total events
  - `pressure_boundary_growth_positive_control_positive_control` emitted one
    corrected growth event with `front_capacity_growth_count = 1`,
    `pressure_boundary_growth_count = 1`, and `legacy_broad_growth_count = 0`
  - `pressure_boundary_growth_no_growth_control_positive_control` emitted no
    growth with pressure-boundary capacity present
  - `generic_front_capacity_growth_comparison_positive_control` emitted one
    corrected front-capacity growth event with
    `pressure_boundary_growth_count = 0`
  - `complex_spark_expansion_pressure_boundary_growth_positive_control`
    emitted spark candidate, mechanical expansion, completed spark, and one
    pressure-boundary growth event

GRCL-9V3 source-backed evidence:

- `outputs/grcl9v3/lowering/sessions/S0073`
  - fixture `pressure_boundary_growth_positive_control`
  - event counts: `choice_detected = 1`, `growth = 1`
  - `front_capacity_growth_count = 1`, `pressure_boundary_growth_count = 1`,
    `legacy_broad_growth_count = 0`
  - the additional `choice_detected` event is normal GRC9V3 semantics and is
    not used as pressure-boundary evidence
- `outputs/grcl9v3/lowering/sessions/S0074`
  - selector validation accepted one strong candidate
  - passed `pressure_boundary_growth_provenance_present`
  - missing surface count: 0
- `outputs/grcl9v3/lowering/sessions/S0075`
  - authored landscape example `pressure_boundary_positive_control`
  - compiled through `default_grcl9v3_landscape_examples`
  - event counts: `choice_detected = 1`, `growth = 1`
  - `front_capacity_growth_count = 1`, `pressure_boundary_growth_count = 1`,
    `legacy_broad_growth_count = 0`
- `outputs/grcl9v3/lowering/sessions/S0076`
  - selector validation accepted the authored landscape example as one strong
    candidate
  - passed `pressure_boundary_growth_provenance_present`
  - missing surface count: 0

Replay:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9v3_discovery_runner --session-id S0015 --pressure-boundary-examples
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_replay --session-id S0073 --source-mode pressure_boundary_probe --fixture pressure_boundary_growth_positive_control --steps 1
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_selector_validation --session-id S0074 --source-session-ids S0073
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_replay --session-id S0075 --source-mode landscape_examples --fixture pressure_boundary_positive_control --steps 1
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_selector_validation --session-id S0076 --source-session-ids S0075
```

Verification:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.discovery.test_grc9v3_seed_generator tests.discovery.test_grc9v3_discovery_runner tests.telemetry.test_grcl9v3_replay tests.telemetry.test_grcl9v3_selector_validation tests.telemetry.test_grc9v3_extensions
PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_grcl9v3_examples
PYTHONPATH=src ./.venv/bin/python -m py_compile src/pygrc/discovery/grc9v3_seed_generator.py src/pygrc/discovery/grc9v3_discovery_runner.py src/pygrc/telemetry/grcl9v3_replay.py tests/discovery/test_grc9v3_seed_generator.py tests/discovery/test_grc9v3_discovery_runner.py tests/telemetry/test_grcl9v3_replay.py
```

## Iteration 5. GRCV3 And GRCL-V3 Alignment

### Goal

Align pressure-boundary vocabulary with GRCV3 active-frontier birth without
importing nine-port mechanics. This section is a parent heading; implementation
is split into Iterations 5.1-5.5.

## Iteration 5.1. GRCV3 / GRCL-V3 Frontier Audit

### Goal

Determine what pressure boundary can mean in GRCV3/GRCL-V3 before adding
source claims or selectors.

### Checks

- [x] Identify existing GRCV3 active-frontier telemetry fields
- [x] Inspect GRCV3 runtime growth/frontier semantics
- [x] Inspect GRCL-V3 vocabulary, source seeds, and lowering surfaces
- [x] Decide whether pressure boundary is runtime-backed, source-only, or
  reserved in GRCV3
- [x] Record unsupported surfaces as reserved

### Verification

- [x] GRCV3 docs distinguish active frontier from GRC9 port capacity
- [x] Audit identifies all artifact-backed telemetry fields that could support
  pressure-boundary/frontier evidence
- [x] Audit does not introduce a source claim before lowering/telemetry support
  is known

### Summary

Iteration 5.1 is complete. The audit is recorded in
[`PressureBoundary-GRCV3-FrontierAudit.md`](./PressureBoundary-GRCV3-FrontierAudit.md).

Findings:

- GRCV3 theory includes front propagation / birth language, but the current
  `GRCV3.step()` implementation has no growth, birth, or active-frontier birth
  stage.
- Current GRCV3 lifecycle telemetry covers spark, split, choice, collapse, and
  hierarchy-related state, but not growth or birth.
- GRCL-V3 has source/lowering vocabulary that can align with pressure boundary:
  `boundary_roles`, `preferred_attachment_sites`, `boundary_geometry`, and
  `channel_geometry`.
- GRCV3 must not import GRC9/GRC9V3 nine-port fields, inactive-port fields, or
  `front_capacity_source`.
- GRCV3 remains no-birth by default: missing `frontier_birth_mode` is
  equivalent to `frontier_birth_mode = disabled`.
- Vocabulary alone does not activate birth. A GRCL-V3 seed/lowering path must
  explicitly write `frontier_birth_mode = active_frontier_pressure` before the
  runtime may create frontier births.
- GRCV3 pressure-boundary provenance must use family-native active-frontier
  language such as `frontier_source = pressure_boundary`, not GRC9/GRC9V3
  `front_capacity_source`.
- Replayable GRCV3 pressure-boundary evidence is allowed only for new
  seed/config lanes that explicitly set
  `frontier_birth_mode = active_frontier_pressure` and have matching telemetry.

Verification:

```bash
rg -n "def step|growth|birth|frontier" src/pygrc/models/grc_v3.py
rg -n "growth|front|boundary|event_domain|lifecycle" implementation/Phase-T-GRCV3-TelemetryContract.md src/pygrc/telemetry/grcv3_contract.py
rg -n "boundary_roles|preferred_attachment_sites|boundary_geometry|channel_geometry" implementation/GRCL-V3-Vocabulary.md src/pygrc/landscapes/extensions/grcv3.py src/pygrc/models/grc_v3_landscape.py
```

## Iteration 5.2. GRCL-V3 Vocabulary Alignment

### Goal

Add pressure-boundary language to GRCL-V3 only where it maps cleanly to
active-frontier semantics.

### Checks

- [x] Add pressure-boundary vocabulary note to GRCL-V3 docs
- [x] Map pressure boundary to active-frontier language where supported
- [x] Explicitly state that GRCV3 does not use `front_capacity_source`
- [x] Explicitly state that GRCV3 does not use nine-port eligibility
- [x] Define the opt-in mode contract:
  `frontier_birth_mode = disabled | active_frontier_pressure`
- [x] State that missing `frontier_birth_mode` means `disabled`
- [x] Define `frontier_birth_strict = warn | error | allow`
- [x] State that authored pressure-boundary/frontier seeds should prefer
  `frontier_birth_mode = active_frontier_pressure`
- [x] State that vocabulary/lowering intent alone does not activate runtime
  birth
- [x] Reserve unsupported source/runtime surfaces

### Verification

- [x] No GRCL-V3 vocabulary entry depends on GRC9-specific port fields
- [x] Boundary, ridge, valley, and active frontier remain distinct
- [x] Source-facing wording does not imply runtime evidence when telemetry is
  unavailable
- [x] No GRCL-V3 vocabulary entry uses GRC9/GRC9V3
  `front_capacity_source`

### Summary

Iteration 5.2 is complete. The vocabulary update is recorded in
[`GRCL-V3-Vocabulary.md`](./GRCL-V3-Vocabulary.md), Section 5.4.1.

The accepted `GRCV3` language is active-frontier/interface intent:

- source may mark a boundary role such as `pressure_boundary`,
- lowering may preserve that role through preferred attachment and boundary
  geometry,
- future runtime telemetry should use family-native fields such as
  `frontier_source = pressure_boundary`,
- missing `frontier_birth_mode` remains `disabled`,
- `front_capacity_source` and nine-port eligibility remain GRC9/GRC9V3-only.

Verification:

```bash
rg -n "Pressure-Boundary|frontier_birth_mode|front_capacity_source|frontier_source|nine-port|active frontier|system boundary" implementation/GRCL-V3-Vocabulary.md implementation/PressureBoundary-ImplementationChecklist.md implementation/PressureBoundary-ImplementationPlan.md
```

## Iteration 5.3. GRCV3 Opt-In Frontier Birth Runtime

### Goal

Add default-off GRCV3 frontier-birth behavior without changing existing seeds
or replay results.

### Checks

- [x] Add `frontier_birth_mode = active_frontier_pressure`
- [x] Treat missing `frontier_birth_mode` as `disabled`
- [x] Treat explicit `frontier_birth_mode = disabled` as current no-birth
  behavior
- [x] Add regression coverage proving missing mode and explicit `disabled`
  mode produce the same step outputs as the current no-birth implementation
- [x] Validate unknown `frontier_birth_mode` values as errors
- [x] Validate unknown `frontier_birth_strict` values as errors
- [x] Add strict error mode for source/evidence runs that declare
  frontier-birth candidates while leaving birth disabled
- [x] Keep explicit allow mode for legacy/no-birth controls
- [x] Select eligible parents from explicit frontier metadata, not generic
  graph-boundary guesses
- [x] Compute outward flux pressure only for eligible active-frontier parents
- [x] Create newborn nodes only under the opt-in mode
- [x] Preserve GRCV3 budget invariants during birth
- [x] Emit family-native birth/frontier events without importing GRC9 port
  fields

### Verification

- [x] Existing GRCV3 seeds without `frontier_birth_mode` produce identical
  no-birth behavior
- [x] Explicit `disabled` mode matches missing-mode behavior
- [x] Compatibility tests compare observed events and telemetry summaries
  against pre-change no-birth expectations
- [x] Opt-in mode can create a birth only from declared frontier metadata
- [x] Non-frontier nodes cannot grow by pressure alone
- [x] Unknown mode values fail before stepping
- [x] No implementation field depends on GRC9/GRC9V3 inactive ports

### Summary

Iteration 5.3 is complete. `GRCV3` now has a default-off frontier-birth runtime
surface:

- missing `frontier_birth_mode` is not injected into defaults and behaves as
  disabled,
- explicit `frontier_birth_mode = disabled` preserves current no-birth
  behavior,
- `frontier_birth_strict = warn` warns once when candidates exist but birth is
  disabled,
- `frontier_birth_strict = error` stops source/evidence runs with candidates
  and disabled birth,
- `frontier_birth_strict = allow` is reserved for explicit no-birth controls
  and legacy compatibility lanes,
- explicit `frontier_birth_mode = active_frontier_pressure` enables
  `apply_frontier_birth`,
- authored pressure-boundary/frontier seeds should prefer
  `frontier_birth_mode = active_frontier_pressure`,
- eligible parents must be declared through `GRCV3` frontier metadata such as
  `grcv3_frontier_birth_candidates`,
- birth probability is computed from outward flux pressure,
- emitted events use `kind = frontier_birth` and family-native
  `frontier_source` provenance,
- no GRC9/GRC9V3 port-capacity or `front_capacity_source` fields are used.

Verification:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_grc_v3_frontier_birth tests.models.test_grc_v3_state
PYTHONPATH=src ./.venv/bin/python -m py_compile src/pygrc/models/grc_v3.py tests/models/test_grc_v3_frontier_birth.py
```

## Iteration 5.4. GRCV3 Telemetry And Selector Mapping

### Goal

Map pressure-boundary/frontier evidence to GRCV3 telemetry fields introduced by
the opt-in runtime surface.

### Checks

- [x] Add GRCV3 telemetry for opt-in frontier birth counts
- [x] Add telemetry for frontier source/provenance
- [x] Add telemetry for birth rule and outward-pressure summary
- [x] Add GRCL-V3 source/lowering telemetry for pressure-boundary frontier
  intent
- [x] Add selectors only for artifact-backed fields
- [x] Report missing surfaces explicitly when opt-in telemetry is absent
- [x] Keep GRCV3 selector names distinct from GRC9/GRC9V3 selectors where
  fields differ
- [x] Add tests for selector pass/fail/missing-surface behavior

### Verification

- [x] Selector field paths match the actual GRCV3 telemetry contract
- [x] Missing unsupported fields are reported as missing surfaces, not weak
  evidence
- [x] No selector queries GRC9/GRC9V3-only port-capacity fields
- [x] Telemetry distinguishes opt-in pressure-boundary frontier birth from
  default no-birth runs

### Summary

Iteration 5.4 is complete. GRCV3 telemetry now includes:

- step-row `frontier_birth_state`,
- run-summary `frontier_birth_summary`,
- `lifecycle_event_counts.frontier_birth_count`,
- event-row classification of `frontier_birth` as `birth/created`,
- family-native selector
  `grcv3_pressure_boundary_frontier_birth`.

The selector requires artifact-backed GRCV3 paths under
`family_extensions.grcv3.frontier_birth_summary` and reports:

- `passed` for pressure-boundary frontier births,
- `predicate_failed` when the surface exists but no pressure-boundary birth is
  observed,
- `missing_surface` when the telemetry group is absent.

Verification:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_grcv3_contract tests.telemetry.test_grcv3_frontier_birth_telemetry tests.models.test_grc_v3_frontier_birth
PYTHONPATH=src ./.venv/bin/python -m py_compile src/pygrc/telemetry/grcv3_contract.py src/pygrc/telemetry/_grcv3_extensions.py src/pygrc/telemetry/grcv3_pressure_boundary_selectors.py tests/telemetry/test_grcv3_frontier_birth_telemetry.py tests/telemetry/test_grcv3_contract.py
```

## Iteration 5.5. GRCV3 / GRCL-V3 Evidence Run

### Goal

Run replayable GRCV3/GRCL-V3 pressure-boundary/frontier evidence using only
explicit opt-in seeds/configs.

### Checks

- [x] Add a GRCL-V3 source example that explicitly lowers into
  `frontier_birth_mode = active_frontier_pressure`
- [x] Select representative old GRCV3/GRCL-V3 output sessions for compatibility
  replay
- [x] Rerun the selected old sessions with the new `.step()` implementation
- [x] Compare observed events, lifecycle counts, and run-summary signatures
  against the recorded artifacts
- [x] Run replayable GRCV3 or GRCL-V3 pressure-boundary/frontier session
- [x] Verify old seeds without `frontier_birth_mode` remain no-birth
- [x] Store produced sessions under `outputs/`
- [x] Record replay commands
- [x] If evidence is not feasible, record reserved status and blocker instead
  of fabricating a weak example

### Verification

- [x] Replayed GRCV3 pressure-boundary examples use opt-in active-frontier
  semantics
- [x] No GRCV3 claim depends on GRC9-specific port fields
- [x] Default/missing-mode replay remains behaviorally equivalent to legacy
  no-birth GRCV3
- [x] Compatibility replay records any mismatch as a blocker before accepting
  opt-in pressure-boundary evidence
- [x] Evidence status is replay-backed or explicitly reserved with a blocker

### Result

Implemented `src/pygrc/telemetry/grcv3_pressure_boundary_evidence.py` and
recorded session `outputs/grcv3/pressure_boundary/sessions/S0001`.

Lanes:

- `compat_missing_frontier_birth_mode`: `frontier_birth_count = 0`
- `compat_disabled_frontier_birth_mode`: `frontier_birth_count = 0`
- `pressure_boundary_frontier_birth_positive`: `frontier_birth_count = 1`,
  `pressure_boundary_birth_count = 1`, selector passed

The session includes:

- `source_fixtures/pressure_boundary_frontier.json`
- per-lane `telemetry/steps.jsonl`, `events.jsonl`, `run_summary.json`, graph
  checkpoint index, and snapshots
- `compatibility_replay_choice_smoke` replay of
  `grcv3-rich-basin-boundary-channel-probe.seed.yaml`
- `compatibility_replay_summary.json`
- replay commands in `session_manifest.json` and `README.md`

Compatibility note: the legacy reference and the replayed no-mode GRCV3 rich
seed both have `frontier_birth_count = 0`. The compatibility summary also
records `choice_detected` parity at the correct granularity: the old reference
is a single aggregate run with `choice_detected = 6`; the replay stores two
matched lanes with `choice_detected = 3` each, so aggregate event-count parity
is true.

Verification commands:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_grcv3_pressure_boundary_evidence tests.telemetry.test_grcv3_frontier_birth_telemetry tests.models.test_grc_v3_frontier_birth
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcv3_pressure_boundary_evidence --session-id S0001
PYTHONPATH=src ./.venv/bin/python -c "from pygrc.telemetry.experiments import run_grcv3_landscape_experiment; overrides={'constitutive_semantic_modes': {'backend_selections': {'choice': {'name': 'sink_compatibility', 'params': {'epsilon_choice': 0.15, 'epsilon_collapse': 0.14}}}}}; run_grcv3_landscape_experiment(telemetry_experiment_path='grcv3/pressure_boundary/sessions/S0001/compatibility_replay_choice_smoke', profile_name='seed_baseline', num_steps=3, cell1_seed_path='configs/landscapes/seed/grcv3-rich-basin-boundary-channel-probe.seed.yaml', cell4_seed_path='configs/landscapes/seed/grcv3-rich-basin-boundary-channel-probe.seed.yaml', overrides=overrides, record_graph_checkpoints=False)"
```

## Iteration 6. Cross-Family Comparison Runs

### Goal

Compare pressure-boundary behavior across GRC9, GRC9V3, and GRCV3 where current
runtimes allow it.

### Checks

- [x] Produce comparable GRC9 and GRC9V3 examples
- [x] Produce GRCV3 comparison example if feasible
- [x] Record family-specific differences
- [x] Record shared frontier-pressure birth behavior
- [x] Store all sessions under `outputs/`

### Verification

- [x] Comparison report names shared observables
- [x] Comparison report names family-specific observables
- [x] Replay commands reproduce all comparison sessions

### Result

Implemented `src/pygrc/telemetry/pressure_boundary_cross_family.py` and
recorded session `outputs/pressure_boundary/cross_family/S0001`.

Compared evidence artifacts:

- GRC9:
  `outputs/grc9/phenomenology_discovery/sessions/S0038/generated_lanes/front_capacity_growth_pressure_boundary_positive_control/telemetry/run_summary.json`
- GRCL-9:
  `outputs/grcl9/lowering/sessions/S0038/lanes/corrected_pressure_boundary_positive_high/telemetry/run_summary.json`
- GRC9V3:
  `outputs/grc9v3/phenomenology_discovery/sessions/S0015/generated_lanes/pressure_boundary_growth_positive_control_positive_control/telemetry/run_summary.json`
- GRCL-9V3:
  `outputs/grcl9v3/lowering/sessions/S0075/lanes/pressure_boundary_positive_control/telemetry/run_summary.json`
- GRCV3:
  `outputs/grcv3/pressure_boundary/sessions/S0001/lanes/pressure_boundary_frontier_birth_positive/telemetry/run_summary.json`

Shared result:

- each family has pressure-boundary-sourced birth/growth count `1`,
- each family has generic front-capacity/frontier count `1`,
- each family has legacy broad-growth count `0`.

Interpretation:

- iteration 6 is a positive pressure-boundary comparison, not the
  legacy-vs-disabled compatibility replay,
- compatibility means legacy/missing/disabled birth modes remain no-birth; that
  is recorded in GRCV3 session `S0001`,
- the positive rows grow because they explicitly provide
  pressure-boundary/front-capacity provenance and enable the outward-flux birth
  rule `p_birth = 1 - exp(-lambda_birth * F_out)`,
- these positive rows are not chance-only legacy growth; they require explicit
  pressure-boundary/frontier eligibility.

Family distinction:

- GRC9 and GRCL-9 claim nine-port front-capacity growth,
- GRC9V3 and GRCL-9V3 claim hybrid GRC9/GRCV3 pressure-boundary growth and
  preserve differential/choice surfaces,
- GRCV3 claims only opt-in active-frontier pressure birth, without nine-port
  semantics.

Verification commands:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_pressure_boundary_cross_family
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.pressure_boundary_cross_family --session-id S0001
```

## Iteration 8. Complex Source Comparison Probe

### Goal

Run an exploratory complex-example comparison for GRC9 and GRC9V3 across legacy
growth and every accepted front-capacity source.

### Checks

- [x] Reuse a connected complex GRC9 example
- [x] Reuse a connected complex GRC9V3 example
- [x] Generate one legacy broad-growth diagnostic row per family
- [x] Generate one corrected front-capacity row per accepted source per family
- [x] Keep source-label variants on the same base topology per family
- [x] Record event counts and growth summaries per row
- [x] Distinguish pressure-boundary-specific rows from generic corrected-front
  rows
- [x] Store replayable artifacts under `outputs/`

### Verification

- [x] Report includes GRC9 and GRC9V3 rows
- [x] Report includes all accepted GRC9 front-capacity sources
- [x] Report includes all accepted GRC9V3 front-capacity sources
- [x] Report includes a legacy diagnostic row for each family
- [x] Pressure-boundary rows are not conflated with generic front-capacity rows
- [x] Legacy rows are explicitly marked diagnostic-only

### Summary

Iteration 8 is complete. Implemented
`src/pygrc/telemetry/pressure_boundary_complex_source_comparison.py` and
recorded `outputs/pressure_boundary/complex_source_comparison/S0001`.

Rows:

- GRC9: one legacy diagnostic row plus 9 accepted front-capacity source rows.
- GRC9V3: one legacy diagnostic row plus 8 accepted front-capacity source rows.

Observed result:

- GRC9 legacy broad growth: `growth_count = 38`,
  `legacy_broad_growth_count = 38`.
- GRC9 corrected source variants: `growth_count = 1`,
  `front_capacity_growth_count = 1`, `legacy_broad_growth_count = 0`.
- GRC9V3 legacy broad growth: `growth_count = 4`,
  `legacy_broad_growth_count = 4`.
- GRC9V3 corrected source variants: `growth_count = 1`,
  `front_capacity_growth_count = 1`, `legacy_broad_growth_count = 0`.
- Only `pressure_boundary` rows have `pressure_boundary_growth_count = 1`.

Interpretation:

- The large behavioral difference is legacy broad eligibility versus corrected
  front-capacity eligibility.
- Accepted front-capacity sources currently behave as provenance labels over
  the same corrected eligibility mechanism on these base graphs.
- `pressure_boundary` is distinguished as pressure-boundary-specific by source
  provenance and telemetry counts, not by a separate birth equation.
- Legacy rows remain diagnostic only.

Replay:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.pressure_boundary_complex_source_comparison --session-id S0001
```

Verification:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_pressure_boundary_complex_source_comparison
PYTHONPATH=src ./.venv/bin/python -m py_compile src/pygrc/telemetry/pressure_boundary_complex_source_comparison.py tests/telemetry/test_pressure_boundary_complex_source_comparison.py
```

## Iteration 7. Catalog And Closeout

### Goal

Close the pressure-boundary track and refresh evidence status.

### Checks

- [x] Refresh reviewed catalogs with pressure-boundary candidates
- [x] Keep legacy broad-growth evidence quarantined
- [x] State which corrected front-capacity evidence remains valid unchanged
- [x] Add closeout/handoff note
- [x] Link closeout from the main implementation phase index

### Verification

- [x] Accepted pressure-boundary motifs have source/runtime/telemetry evidence
- [x] No accepted pressure-boundary motif uses legacy broad-growth mode
- [x] Closeout states remaining boundary-barrier / ghost-node work as future
  scope

### Summary

Iteration 7 is complete. The refreshed closeout comparison is
`outputs/pressure_boundary/cross_family/S0001`, regenerated after the GRCV3
strict-mode update. Accepted pressure-boundary evidence is:

- GRC9 direct runtime:
  `outputs/grc9/phenomenology_discovery/sessions/S0038/generated_lanes/front_capacity_growth_pressure_boundary_positive_control/telemetry/run_summary.json`
- GRCL-9 source-backed runtime:
  `outputs/grcl9/lowering/sessions/S0038/lanes/corrected_pressure_boundary_positive_high/telemetry/run_summary.json`
- GRC9V3 direct runtime:
  `outputs/grc9v3/phenomenology_discovery/sessions/S0015/generated_lanes/pressure_boundary_growth_positive_control_positive_control/telemetry/run_summary.json`
- GRCL-9V3 source-backed runtime:
  `outputs/grcl9v3/lowering/sessions/S0075/lanes/pressure_boundary_positive_control/telemetry/run_summary.json`
- GRCV3 opt-in active-frontier runtime:
  `outputs/grcv3/pressure_boundary/sessions/S0001/lanes/pressure_boundary_frontier_birth_positive/telemetry/run_summary.json`

Shared closeout result:

- pressure-boundary-sourced birth/growth count is `1` in each accepted row,
- generic front-capacity/frontier count is `1` in each accepted row,
- legacy broad-growth count is `0` in each accepted row,
- GRCV3 positive evidence uses
  `frontier_birth_mode = active_frontier_pressure` and
  `frontier_birth_strict = error`.

Historical controls:

- legacy broad-growth and over-aggressive growth-locus artifacts remain
  historical only,
- GRCV3 missing-mode and disabled-mode lanes remain no-birth compatibility
  controls,
- corrected front-capacity evidence without `pressure_boundary` remains valid
  for generic corrected-front claims but is not pressure-boundary-specific.

Future scope:

- boundary-barrier and ghost-node runtime behavior,
- Lorentzian causal boundary semantics,
- open-system environmental exchange.

Verification:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_grcv3_pressure_boundary_evidence tests.telemetry.test_grcv3_frontier_birth_telemetry tests.models.test_grc_v3_frontier_birth
PYTHONPATH=src ./.venv/bin/python -m py_compile src/pygrc/telemetry/grcv3_pressure_boundary_evidence.py
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcv3_pressure_boundary_evidence --session-id S0001
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.pressure_boundary_cross_family --session-id S0001
```
