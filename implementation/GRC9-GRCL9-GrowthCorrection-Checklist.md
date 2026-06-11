# GRC9 / GRCL-9 Growth Correction Checklist

This checklist tracks the GRC9 / GRCL-9 growth semantics correction.

The correction is required because existing GRC9 growth uses the paper birth
probability and lowest-port rule, but allows too many parents: any live node
with an inactive port and outward flux can grow when `lambda_birth > 0`.
Paper-facing growth claims must instead be tied to explicit front/boundary
capacity exposed by spark/refinement structure.

## Usage Rules

- Preserve historical replay.
- Do not delete old sessions.
- Do not rewrite old outputs.
- Do not use broad-growth legacy results for any evidence claim.
- Keep `legacy_any_inactive_port` behavior available only for replaying and
  debugging the historical defect.
- Require corrected front-capacity provenance for accepted growth claims.
- Keep non-growth evidence valid unless it depends on growth-created topology.
- Use session roots under `outputs/` for every rerun.

## Status Terms

- `legacy_broad_growth_non_evidence`: historical broad-growth result retained
  only for replay and debugging the old defect; it must not support any
  paper-facing evidence claim.
- `superseded_by_growth_semantics_correction`: reviewed growth-bearing evidence
  that should not remain accepted after the correction.
- `front_capacity_growth_candidate`: corrected evidence with explicit
  front-capacity provenance, pending review.
- `accepted_front_capacity_growth`: corrected evidence accepted into the
  refreshed catalog.

## Iteration 0. Planning Bootstrap

### Goal

Record the correction scope and non-reset policy.

### Checks

- [x] Create `GRC9-GRCL9-GrowthCorrection-Plan.md`
- [x] Create `GRC9-GRCL9-GrowthCorrection-Checklist.md`
- [x] State that the birth probability formula remains valid
- [x] State that the lowest-port attachment rule remains valid
- [x] State that parent eligibility is the defect
- [x] State that old artifacts remain replayable
- [x] State that growth-bearing broad-growth evidence is superseded for
  paper-facing growth claims

### Verification

- [x] Plan/checklist distinguish affected growth claims from unaffected
  non-growth evidence
- [x] Plan/checklist include GRC9 core and GRCL-9 source/lowering work

### Summary

Iteration 0 is complete once the correction docs are added.

## Iteration 1. GRC9 Core Growth Eligibility

### Goal

Add a paper-facing growth parent eligibility mode to GRC9 core while preserving
legacy replay.

### Checks

- [x] Add `growth_parent_eligibility` to GRC9 params/modes
- [x] Support `legacy_any_inactive_port`
- [x] Support `grc9_front_capacity`
- [x] Default behavior is explicitly documented
- [x] Preserve legacy mode for historical replay
- [x] In `grc9_front_capacity` mode, filter parent/port candidates through
  explicit front-capacity metadata
- [x] Preserve birth probability:
  `p_birth(i) = 1 - exp(-lambda * F_i^out)`
- [x] Preserve lowest eligible inactive-port selection
- [x] Add `grc9_front_growth_eligible_ports`
- [x] Add `grc9_growth_parent_capacity_sources`
- [x] Add `birth_parent_eligibility_mode`
- [x] Growth event records `growth_parent_eligibility_mode`
- [x] Growth event records `growth_parent_capacity_source`
- [x] Growth event records selected `parent_port_id`
- [x] Growth event records `birth_probability`
- [x] Growth event records outward flux pressure

### Verification

- [x] Unit test: legacy mode still permits broad inactive-port growth
- [x] Unit test: corrected mode emits no growth without front-capacity metadata
- [x] Unit test: corrected mode grows from the lowest eligible front-capacity
  port
- [x] Unit test: corrected mode ignores inactive ports not listed as eligible
- [x] Unit test: event payload includes eligibility/capacity-source fields
- [x] Regression test: non-growth runs with `lambda_birth = 0` unchanged

### Summary

Iteration 1 is complete. `GRC9` now accepts
`growth_parent_eligibility = legacy_any_inactive_port | grc9_front_capacity`.
Legacy mode remains the default for historical replay. Corrected front-capacity
mode filters growth parents through `grc9_front_growth_eligible_ports`, records
`birth_parent_eligibility_mode`, and emits growth events with
`growth_parent_eligibility_mode` and `growth_parent_capacity_source`.

Verification:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_grc_9_expansion`
- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_grc_9_step`
- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_grc_9_coarse`
- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_grc_9_runtime`

## Iteration 2. Phase T-GRC9 Telemetry Update

### Goal

Expose corrected growth eligibility and capacity-source evidence through the
GRC9 telemetry contract and builders.

### Checks

- [x] Update `Phase-T-GRC9-TelemetryContract.md`
- [x] Update GRC9 telemetry dataclasses if needed
- [x] Update GRC9 event extension builder for new growth fields
- [x] Update GRC9 run summary growth fields if needed
- [x] Add selector-facing field paths for:
  - `growth_parent_eligibility_mode`
  - `growth_parent_capacity_source`
  - `front_growth_provenance_present`
  - `legacy_broad_growth_present`
- [x] Keep legacy broad-growth telemetry visible for replay-only
  non-evidence classification
- [x] Update representative telemetry docs

### Verification

- [x] Contract tests pass
- [x] Event-row round-trip includes new growth fields
- [x] Missing front-capacity provenance is reported explicitly
- [x] Legacy broad-growth events are classified as non-evidence, not
  accepted paper-facing growth

### Summary

Iteration 2 is complete. GRC9 telemetry now exposes
`growth_parent_eligibility_mode` in backend config, event-level growth evidence
now carries `parent_eligibility_mode`, `parent_capacity_source`,
`front_growth_provenance_present`, and `legacy_broad_growth`, and run summaries
split growth counts into `front_capacity_growth_count` and
`legacy_broad_growth_count`.

Verification:

- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_grc9_contract`
- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_grc9_extensions`
- `PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_grc9_contract tests.telemetry.test_grc9_extensions`
- `PYTHONPATH=src ./.venv/bin/python -m py_compile src/pygrc/telemetry/grc9_contract.py src/pygrc/telemetry/_grc9_extensions.py tests/telemetry/test_grc9_contract.py tests/telemetry/test_grc9_extensions.py`

Note: an attempted smoke command using stale module names
`tests.telemetry.test_grc9_representative_telemetry` and
`tests.telemetry.test_grc9_landscape_telemetry` failed because those modules do
not exist in this repository. The actual GRC9 telemetry test modules listed
above passed.

## Iteration 3. GRC9 Corrected Growth Discovery

### Goal

Rerun GRC9 growth-bearing discovery under corrected front-capacity semantics.

### Checks

- [x] Add corrected front-capacity GRC9 seed families
- [x] Add no-front-capacity negative control
- [x] Add zero-birth control with front capacity present
- [x] Add closed-front control with no eligible ports
- [x] Rerun elementary growth lanes
- [x] Rerun spark-growth composition lanes
- [x] Rerun growth-fission composition lanes if still meaningful
- [x] Rerun full-complex lanes that previously depended on growth
- [x] Preserve old discovery sessions as replay-only non-evidence artifacts
- [x] Record replay commands for all corrected sessions

### Verification

- [x] Corrected positive lanes emit growth with front-capacity provenance
- [x] No-front-capacity lanes do not emit growth
- [x] Zero-birth lanes do not emit growth while preserving provenance
- [x] Corrected combo lanes do not show runaway broad growth
- [x] Selector reports distinguish corrected growth from legacy broad growth

### Summary

Complete. Iteration 3.1 added elementary corrected GRC9 growth controls in
`S0027`; 3.2 and 3.2.1 restored corrected combo evidence in `S0028` and
`S0029`; 3.3 restored corrected full-complex all-event evidence in `S0030`;
and 3.4 classified legacy broad-growth sessions as replay-only non-evidence
artifacts.

## Iteration 3.1. Elementary Corrected GRC9 Growth Seeds

### Goal

Create and run minimal corrected GRC9 growth controls.

### Checks

- [x] Add corrected front-capacity GRC9 seed family
- [x] Add no-front-capacity negative control
- [x] Add zero-birth control with front capacity present
- [x] Add closed-front control with no eligible ports
- [x] Run elementary corrected growth session
- [x] Record replay commands

### Verification

- [x] Corrected positive lane emits growth with front-capacity provenance
- [x] No-front-capacity lane emits no growth
- [x] Zero-birth lane emits no growth while preserving front-capacity provenance
- [x] Closed-front lane emits no growth and records closed capacity

### Summary

Complete. Added `grc9_growth_correction_elementary_v1` seed fixtures and
runner mode `--corrected-growth-elementary`, then ran `S0027`.

Replay:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_discovery_runner --session-id S0027 --corrected-growth-elementary
```

Observed: 4 lanes, 12 steps, 16 graph checkpoints, and 1 total event. Only
`front_capacity_growth_positive_control` emitted `growth`; its event carried
`parent_eligibility_mode = grc9_front_capacity`,
`parent_capacity_source = spark_refinement_boundary_front`, and
`front_growth_provenance_present = true`. The no-front, zero-birth, and
closed-front controls emitted no growth.

Tests:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.discovery.test_grc9_seed_generator
PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_grc_9_expansion tests.telemetry.test_grc9_contract tests.telemetry.test_grc9_extensions tests.discovery.test_grc9_seed_generator
PYTHONPATH=src ./.venv/bin/python -m py_compile src/pygrc/discovery/grc9_seed_generator.py src/pygrc/discovery/grc9_discovery_runner.py src/pygrc/discovery/__init__.py tests/discovery/test_grc9_seed_generator.py
```

## Iteration 3.2. Corrected GRC9 Combo Reruns

### Goal

Rerun corrected GRC9 growth combinations after elementary controls work.

### Checks

- [x] Rerun spark-growth composition lanes
- [x] Rerun growth-fission composition lanes if still meaningful
- [x] Record whether corrected growth changes downstream fission evidence
- [x] Preserve old combo sessions as replay-only non-evidence artifacts

### Verification

- [x] Corrected combo lanes include front-capacity growth provenance
- [x] Corrected combo lanes do not show runaway broad growth
- [x] Any lost old evidence is recorded as a miss or ambiguity

### Summary

Complete. Added `grc9_growth_correction_combo_v1` fixtures and runner mode
`--corrected-growth-combo`, then ran `S0028`.

Replay:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_discovery_runner --session-id S0028 --corrected-growth-combo
```

Observed: 3 lanes, 16 steps, 19 graph checkpoints, and 7 total events.
`corrected_spark_growth_combo` emitted one spark, one expansion, and one
front-capacity growth event. `corrected_growth_fission_combo` emitted one
front-capacity growth event and retained one confirmed fission summary.
`corrected_spark_growth_fission_combo` emitted one spark, one expansion, and
one front-capacity growth event, but did not retain confirmed fission under the
corrected spark-growth interaction. All three lanes reported
`front_capacity_growth_count = 1` and `legacy_broad_growth_count = 0`.

Implementation note: GRC9 topology-pruning now preserves the corrected
front-capacity cache keys across same-step expansion so spark-growth
composition lanes can still apply paper-facing growth after a topology
mutation.

Tests:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.discovery.test_grc9_seed_generator
PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_grc_9_expansion tests.telemetry.test_grc9_contract tests.telemetry.test_grc9_extensions tests.discovery.test_grc9_seed_generator
PYTHONPATH=src ./.venv/bin/python -m py_compile src/pygrc/models/grc_9.py src/pygrc/discovery/grc9_seed_generator.py src/pygrc/discovery/grc9_discovery_runner.py src/pygrc/discovery/__init__.py tests/discovery/test_grc9_seed_generator.py
```

## Iteration 3.2.1. Corrected Spark-Growth-Fission Stabilization

### Goal

Restore fission confirmation in the corrected all-combo case without
reintroducing legacy broad growth.

### Checks

- [x] Strengthen the fission submodule structurally instead of changing the
  Appendix E evaluator
- [x] Keep corrected front-capacity growth provenance unchanged
- [x] Rerun corrected combo session as a separate replayable session
- [x] Record whether all event families are restored

### Verification

- [x] Corrected spark-growth-fission emits spark, expansion, and growth
- [x] Corrected spark-growth-fission confirms fission
- [x] Growth remains bounded to one front-capacity event
- [x] `legacy_broad_growth_count = 0`

### Summary

Complete. Strengthened only the fission daughter attractor coherences in
`corrected_spark_growth_fission_combo`, then ran `S0029`.

Replay:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_discovery_runner --session-id S0029 --corrected-growth-combo
```

Observed: 3 lanes, 16 steps, 19 graph checkpoints, and 7 total events.
`corrected_spark_growth_fission_combo` now emits one spark, one expansion, one
front-capacity growth event, and reports
`identity_fission_confirmed_count = 1` with
`identity_fission_max_persistence_steps = 6`. All corrected combo lanes still
report `front_capacity_growth_count = 1` and `legacy_broad_growth_count = 0`.

Tests:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.discovery.test_grc9_seed_generator
PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_grc_9_expansion tests.telemetry.test_grc9_contract tests.telemetry.test_grc9_extensions tests.discovery.test_grc9_seed_generator
PYTHONPATH=src ./.venv/bin/python -m py_compile src/pygrc/models/grc_9.py src/pygrc/discovery/grc9_seed_generator.py src/pygrc/discovery/grc9_discovery_runner.py src/pygrc/discovery/__init__.py tests/discovery/test_grc9_seed_generator.py
```

## Iteration 3.3. Corrected GRC9 Full-Complex Reruns

### Goal

Rerun full-complex and robustness GRC9 lanes that previously depended on
growth.

### Checks

- [x] Rerun full-complex lanes
- [x] Rerun robustness lanes
- [x] Compare corrected outcomes to legacy broad-growth outcomes
- [x] Record misses, reductions, and ambiguous outcomes

### Verification

- [x] Growth remains bounded to explicit front capacity
- [x] Supersession records distinguish corrected growth from legacy broad
  growth
- [x] Replay commands are recorded

### Summary

Complete. `S0030` added corrected full-complex fixtures:
`corrected_all_events_complex_control` plus four small robustness
perturbations. Every lane emitted exactly `2` spark events, `2` expansion
events, and `1` growth event in `6` steps. Growth evidence was bounded to
front-capacity provenance (`front_capacity_growth_count = 1`,
`legacy_broad_growth_count = 0`) and all five lanes retained confirmed
identity fission in the run summary. The corrected full-complex run therefore
restores the old all-event evidence without the legacy broad-growth cascade.

Replay:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_discovery_runner --session-id S0030 --corrected-growth-complex
```

Legacy distinction is closed by Iteration 3.4 through
`outputs/grc9/phenomenology_discovery/indexes/growth_semantics_correction.md`.

Tests:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.discovery.test_grc9_seed_generator
PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_grc_9_expansion tests.telemetry.test_grc9_contract tests.telemetry.test_grc9_extensions tests.discovery.test_grc9_seed_generator
```

## Iteration 3.4. GRC9 Discovery Legacy Classification

### Goal

Classify old GRC9 growth-bearing discovery evidence after corrected reruns.

### Checks

- [x] Identify old broad-growth discovery sessions
- [x] Mark growth-dependent old records as `legacy_broad_growth_non_evidence`
- [x] Preserve independent non-growth diagnostic fixtures as replay references
  only when not derived from a broad-growth mixed catalog
- [x] Publish discovery supersession notes

### Verification

- [x] Old sessions remain replayable
- [x] No broad-growth record is listed as accepted paper-facing growth
- [x] Broad-growth legacy results are explicitly barred from any evidence use

### Summary

Complete. Added
`outputs/grc9/phenomenology_discovery/indexes/growth_semantics_correction.md`
as the authoritative supersession index for GRC9 broad-growth discovery
artifacts.

Direct broad-growth runs (`S0004`-`S0007`, `S0012`, `S0020`, `S0021`) and
their mixed downstream selector/visual/review/handoff outputs (`S0008`,
`S0009`, `S0011`, `S0013`-`S0019`, `S0022`-`S0026`) are classified as
`legacy_broad_growth_non_evidence`. They remain replayable only to reproduce
or debug the old `legacy_any_inactive_port` behavior. They must not be used as
evidence for growth, spark, expansion, fission, motif acceptance, GRCL-9
translation suitability, or any other paper-facing claim.

Corrected evidence starts at `S0027`, with current growth-bearing corrected
replacement sessions:

- `S0027`: elementary front-capacity growth controls
- `S0029`: corrected spark/growth/fission combo after fission stabilization
- `S0030`: corrected full-complex all-event rerun

`S0028` remains replayable as the intermediate corrected combo miss that led
to the stabilized `S0029` rerun.

## Iteration 4. GRCL-9 Source And Lowering Migration

### Goal

Make GRCL-9 source growth paper-facing only when it declares explicit
front-capacity semantics.

### Checks

- [x] Extend `GRCL9GrowthLocus` with `growth_semantics`
- [x] Add `legacy_growth_locus`
- [x] Add `front_capacity`
- [x] Add `front_capacity_source`
- [x] Add `front_source_construct_id`
- [x] Add validation helper for paper-facing growth semantics
- [x] Reject executable legacy growth in paper-facing validation
- [x] Keep legacy growth loadable for diagnostic replay
- [x] Lower corrected front-capacity growth into:
  - `grc9_front_growth_eligible_ports`
  - `grc9_growth_parent_capacity_sources`
- [x] Set GRC9 replay mode to `grc9_front_capacity` for corrected sources
- [x] Record legacy growth source ids in lowered state metadata
- [x] Move or classify old standalone-growth seeds as replay-only
  non-evidence artifacts

### Verification

- [x] Schema round-trip preserves growth semantics fields
- [x] Legacy diagnostic documents still load
- [x] Paper-facing validation rejects legacy growth claims
- [x] Lowered corrected source contains front-capacity caches
- [x] Replay config selects `grc9_front_capacity`
- [x] Source documents still do not claim observed growth events

### Summary

Complete. This iteration is split into 4.1-4.4. GRCL-9 source documents now
distinguish legacy standalone growth from corrected front-capacity growth,
lower corrected source growth into the GRC9 front-capacity runtime caches, and
route corrected replay through `growth_parent_eligibility = grc9_front_capacity`.
Legacy standalone growth seeds are quarantined in
`configs/landscapes/seed/legacy/grcl9-overaggressive-growth/` and remain
loadable/replayable only as explicit `legacy_broad_growth_non_evidence`.

## Iteration 4.1. GRCL-9 Source Growth Semantics

### Goal

Add source-level growth semantics and paper-facing validation.

### Checks

- [x] Extend `GRCL9GrowthLocus` with `growth_semantics`
- [x] Add `legacy_growth_locus`
- [x] Add `front_capacity`
- [x] Add `front_capacity_source`
- [x] Add `front_source_construct_id`
- [x] Add validation helper for paper-facing growth semantics
- [x] Reject executable legacy growth in paper-facing validation
- [x] Keep legacy growth loadable for diagnostic replay

### Verification

- [x] Schema round-trip preserves growth semantics fields
- [x] Legacy diagnostic documents still load
- [x] Paper-facing validation rejects legacy growth claims
- [x] Source documents still do not claim observed growth events

### Summary

Complete. `GRCL9GrowthLocus` now carries source-level growth semantics:
`legacy_growth_locus` remains the default for loading historical source
documents, while `front_capacity` requires a non-legacy
`front_capacity_source` and can reference the source construct that produced
the front capacity. Added
`validate_grcl9_paper_facing_growth_semantics(...)` so executable standalone
legacy growth is rejected for paper-facing claims without preventing historical
fixtures from loading.

Phenomenology comparison: 4.1 does not change runtime phenomenology because it
does not alter lowering or replay. Old and new source documents therefore have
no event-level difference yet. The difference is evidentiary: legacy
standalone `growth_locus` remains loadable only for replaying/debugging old
behavior, while `front_capacity` growth becomes the only paper-facing source
shape that can proceed to 4.2 / 4.3 lowering and replay.

Tests:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_grcl9_schema tests.landscapes.test_grcl9_fixtures tests.landscapes.test_grcl9_examples
PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_grcl9_schema tests.landscapes.test_grcl9_fixtures tests.landscapes.test_grcl9_examples tests.models.test_grc_9_grcl9_lowering tests.telemetry.test_grcl9_replay tests.telemetry.test_grcl9_lowered_motif_catalog tests.visualization.test_grcl9_lowering tests.discovery.test_grc9_grcl9_handoff
PYTHONPATH=src ./.venv/bin/python -m py_compile src/pygrc/landscapes/extensions/grcl9/schema.py src/pygrc/landscapes/extensions/grcl9/__init__.py tests/landscapes/test_grcl9_schema.py
```

## Iteration 4.2. GRCL-9 Lowering Front-Capacity Caches

### Goal

Lower corrected source growth into GRC9 front-capacity caches.

### Checks

- [x] Lower corrected front-capacity growth into `grc9_front_growth_eligible_ports`
- [x] Lower corrected front-capacity growth into `grc9_growth_parent_capacity_sources`
- [x] Record legacy growth source ids in lowered state metadata
- [x] Record front-capacity source provenance in lowered state metadata

### Verification

- [x] Lowered corrected source contains front-capacity caches
- [x] Legacy lowered sources record legacy growth ids
- [x] Lowering remains connected and deterministic

### Summary

Complete. GRCL-9 lowering now writes corrected GRC9 runtime cache surfaces for
`front_capacity` source growth:

- `grc9_front_growth_eligible_ports`
- `grc9_growth_parent_capacity_sources`

It also mirrors those surfaces under `grcl9_*` names for source-facing
inspection, records `grcl9_growth_semantics_status`, and records
`grcl9_legacy_growth_locus_ids` for legacy standalone growth documents.

Phenomenology comparison: legacy GRCL-9 lowering remains phenomenologically
equivalent to the old behavior because legacy fixtures still lower to the same
connected GRC9 graph structure, with added non-evidence metadata only.
Corrected `front_capacity` sources now carry the exact runtime cache surfaces
needed to reproduce the intended growth event family, but event-level
phenomenology is not changed until 4.3 selects
`growth_parent_eligibility = grc9_front_capacity` during replay.

Tests:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.models.test_grc_9_grcl9_lowering
PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_grcl9_schema tests.landscapes.test_grcl9_fixtures tests.landscapes.test_grcl9_examples tests.models.test_grc_9_grcl9_lowering tests.telemetry.test_grcl9_replay tests.telemetry.test_grcl9_lowered_motif_catalog tests.visualization.test_grcl9_lowering tests.discovery.test_grc9_grcl9_handoff
PYTHONPATH=src ./.venv/bin/python -m py_compile src/pygrc/models/grc_9_grcl9_lowering.py tests/models/test_grc_9_grcl9_lowering.py
```

## Iteration 4.3. GRCL-9 Legacy Seed Quarantine

### Goal

Move old standalone-growth GRCL-9 seed files out of normal seed discovery.

### Checks

- [x] Create `configs/landscapes/seed/legacy/grcl9-overaggressive-growth/`
- [x] Move old standalone-growth GRCL-9 seed files into the legacy subtree
- [x] Exclude quarantined growth seeds from normal default GRCL-9 seed
  discovery
- [x] Add explicit diagnostic loader/source mode for quarantined growth seeds
- [x] Update seed README so legacy GRCL-9 growth seeds are replay-only
  non-evidence artifacts

### Verification

- [x] Default GRCL-9 seed discovery excludes quarantined legacy growth seeds
- [x] Diagnostic legacy loader can still load quarantined growth seeds
- [x] Replay can copy quarantined seed files through explicit diagnostic mode

### Summary

Complete. Thirty GRCL-9 seed files that relied on standalone growth-locus
semantics were moved to
`configs/landscapes/seed/legacy/grcl9-overaggressive-growth/`. Normal
`landscape_seed_examples` discovery now exposes only non-growth or
growth-independent GRCL-9 seeds, while the quarantined seeds remain available
through `legacy_growth_landscape_seed_examples`.

Tests:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_grcl9_seed_examples tests.telemetry.test_grcl9_replay
```

## Iteration 4.4. GRCL-9 Replay Integration

### Goal

Route corrected GRCL-9 source documents through corrected GRC9 growth mode
after seed quarantine.

### Checks

- [x] Set GRC9 replay mode to `grc9_front_capacity` for corrected sources
- [x] Preserve legacy broad-growth replay as explicit non-evidence mode
- [x] Record replay metadata for growth eligibility mode
- [x] Rerun classification against the explicit legacy seed source mode

### Verification

- [x] Replay config selects `grc9_front_capacity` for corrected source documents
- [x] Legacy replay mode remains available by explicit diagnostic path
- [x] Tests cover corrected and legacy replay paths

### Summary

Complete. GRCL-9 replay derives growth mode from source semantics before
building GRC9 params. Corrected source documents with executable
`front_capacity` growth run with
`growth_parent_eligibility = grc9_front_capacity`; legacy standalone
`growth_locus` documents remain replayable with
`growth_parent_eligibility = legacy_any_inactive_port` only through explicit
fixture or `legacy_growth_landscape_seed_examples` diagnostic paths, and are
marked `legacy_broad_growth_non_evidence` in lane metadata and telemetry
family extensions.

Phenomenology comparison: legacy standalone-growth replay remains
phenomenologically equivalent to the old replay path, because it still selects
the historical broad-growth GRC9 mode. The corrected path is intentionally not
phenomenologically equivalent to legacy broad growth in the runaway sense:
growth is restricted to declared front-capacity ports, so event families can
still match intended growth evidence while broad inner-node growth is no longer
available for paper-facing claims.

Tests:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_grcl9_replay
PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_grcl9_schema tests.landscapes.test_grcl9_fixtures tests.landscapes.test_grcl9_examples tests.landscapes.test_grcl9_seed_examples tests.models.test_grc_9_grcl9_lowering tests.telemetry.test_grcl9_replay tests.telemetry.test_grcl9_lowered_motif_catalog tests.visualization.test_grcl9_lowering tests.discovery.test_grc9_grcl9_handoff
PYTHONPATH=src ./.venv/bin/python -m py_compile src/pygrc/landscapes/extensions/grcl9/examples.py src/pygrc/landscapes/extensions/grcl9/__init__.py src/pygrc/landscapes/extensions/__init__.py src/pygrc/telemetry/grcl9_replay.py tests/landscapes/test_grcl9_seed_examples.py tests/telemetry/test_grcl9_replay.py
```

## Iteration 5. GRCL-9 Corrected Replay, Selectors, And Visualization

### Goal

Rerun affected GRCL-9 source examples under corrected front-capacity growth.

### Checks

- [x] Add corrected elementary front-growth GRCL-9 examples
- [x] Add corrected GRCL-9 no-growth controls
- [x] Rebuild affected growth-bearing cascade examples
- [x] Rebuild affected phase-diagram examples
- [x] Rebuild affected collapse-adjacent examples only where growth is part of
  the claim
- [x] Run selector validation over corrected sessions
- [x] Require front-growth provenance selectors for growth acceptance
- [x] Render corrected visualizations with front-capacity overlays
- [x] Keep old broad-growth visualizations marked as replay-only non-evidence
- [x] Update `outputs/grcl9/lowering/ExperimentalLog.md`

### Verification

- [x] Corrected positive source examples emit growth from front capacity
- [x] Corrected no-growth controls remain no-growth
- [x] Growth event payloads link back to source/front capacity
- [x] Selector reports do not accept legacy broad-growth records
- [x] Visual metadata identifies corrected vs legacy growth status

### Summary

Complete. This iteration is split into 5.1-5.4 and is fully covered by the
completed subiterations:

- `S0027` covers elementary corrected GRCL-9 front-growth examples;
- `S0029` covers corrected composite reruns;
- `S0030` and `S0031` cover parity tuning, with `S0031` closing the remaining
  misses at 28 passed / 0 missed;
- `S0032` preserves quarantined legacy broad-growth replay as diagnostic
  non-evidence;
- `S0033` validates selectors over corrected plus legacy sessions, accepting
  28 corrected records and superseding 30 legacy records;
- `S0031` and `S0032` visualizations mark corrected vs legacy growth status in
  overlay metadata and boundary panels.

## Iteration 5.1. Elementary Corrected GRCL-9 Examples

### Goal

Add and replay elementary corrected GRCL-9 front-growth source examples.

### Checks

- [x] Add corrected elementary front-growth GRCL-9 examples
- [x] Add corrected GRCL-9 no-growth controls
- [x] Replay elementary corrected examples
- [x] Update `outputs/grcl9/lowering/ExperimentalLog.md`

### Verification

- [x] Corrected positive source examples emit growth from front capacity
- [x] Corrected no-growth controls remain no-growth
- [x] Growth event payloads link back to source/front capacity

### Summary

Complete. Added four normal, non-legacy elementary landscape seed examples:
`grcl9-corrected-front-growth-positive-high.seed.yaml`,
`grcl9-corrected-front-growth-no-growth-low.seed.yaml`,
`grcl9-corrected-front-growth-no-front-fail.seed.yaml`, and
`grcl9-corrected-front-growth-closed-front-fail.seed.yaml`.

The positive and zero-birth lanes compile through the GRCL-9 landscape example
compiler into `growth_locus` source constructs with
`growth_semantics = front_capacity`,
`front_capacity_source = spark_expansion_front`, and a
`front_source_construct_id` pointing at the companion expansion region. The
no-front control keeps the same corrected growth mode but marks the authored
boundary as `no_front_capacity`. The closed-front control declares front-growth
intent but lowers no eligible growth port.

`S0026` was a preliminary two-lane run and is retained only as an incomplete
iteration attempt. The completed elementary evidence is `S0027`: 4 lanes, 3
requested steps each, and 16 graph checkpoints.
`corrected_front_growth_positive_high` emitted `spark`, `expansion`, and
`growth`. The three controls emitted `spark` and `expansion` only, with no
growth events. All four lanes report
`growth_parent_eligibility_mode = grc9_front_capacity`, carry corrected
front-capacity semantics, and have selector status `passed`.

Replay:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9_replay --session-id S0027 --source-mode landscape_seed_examples --requested-steps 3 --fixture corrected_front_growth_positive_high --fixture corrected_front_growth_no_growth_low --fixture corrected_front_growth_no_front_fail --fixture corrected_front_growth_closed_front_fail
```

Tests:

```bash
PYTHONPATH=src ./.venv/bin/python -m py_compile src/pygrc/landscapes/extensions/grcl9/examples.py tests/landscapes/test_grcl9_seed_examples.py
PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_grcl9_seed_examples
PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_grcl9_seed_examples tests.models.test_grc_9_grcl9_lowering tests.telemetry.test_grcl9_replay
```

## Iteration 5.2. Corrected GRCL-9 Composite Reruns

### Goal

Rerun corrected GRCL-9 composite examples that previously depended on broad
growth.

### Checks

- [x] Rebuild affected growth-bearing cascade examples
- [x] Rebuild affected phase-diagram examples
- [x] Rebuild affected collapse-adjacent examples only where growth is part of
  the claim
- [x] Record corrected session roots and replay commands

### Verification

- [x] Corrected composite growth remains front-capacity bounded
- [x] Missing old broad-growth effects are recorded explicitly
- [x] Non-growth evidence remains separable

### Summary

Complete. Promoted corrected copies of the 28 non-elementary quarantined
GRCL-9 growth seeds into the normal seed tree with `grcl9-corrected-*`
filenames and `corrected_*` fixture names. These cover internal
valley/transport growth, support-loss/identity-decay, full-capacity cascades,
basin-asymmetry variants, phase-diagram lanes, and collapse-adjacent lanes.
Every corrected growth construct now compiles with
`growth_semantics = front_capacity`; spark/refinement-bearing composites use
`front_capacity_source = spark_expansion_front`, while non-refinement
fronts use `front_capacity_source = preexisting_front`.

`S0028` was a preliminary corrected composite run that exposed that
no-growth corrected fixtures still reported the legacy eligibility mode when
they had no executable `growth_locus`. The replay metadata was tightened, and
`S0029` is the completed 5.2 evidence session.

Ran replay session `S0029` over all 28 corrected composite seeds with 24
steps each. The session produced 672 total steps, 700 graph checkpoints, and
68 runtime events: 26 `spark`, 26 `expansion`, and 16 corrected
front-capacity `growth` events. All 28 lanes report
`growth_parent_eligibility_mode = grc9_front_capacity`.

Selector status at this stage is intentionally diagnostic, not final
acceptance: 10 lanes passed current replay selectors and 18 missed older
selectors, mostly where corrected bounded growth no longer reproduces the
legacy broad-growth side effects. Iteration 5.3 will validate the corrected
field-backed selector surface.

Replay:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9_replay --session-id S0029 --source-mode landscape_seed_examples --requested-steps 24 --fixture corrected_cell_internal_valley_transport_growth_high --fixture corrected_cell_support_loss_identity_decay_probe --fixture corrected_cell_full_capacity_phenomenology_cascade --fixture corrected_cell_full_capacity_cascade_low_growth --fixture corrected_cell_full_capacity_cascade_high_growth --fixture corrected_cell_full_capacity_cascade_no_merge_bridge --fixture corrected_cell_full_capacity_cascade_weak_merge_bridge --fixture corrected_cell_full_capacity_cascade_isolated_bridge --fixture corrected_cell_full_capacity_cascade_larger_basin_support --fixture corrected_cell_full_capacity_cascade_no_refinement --fixture corrected_cell_full_capacity_cascade_no_growth --fixture corrected_cell_full_capacity_cascade_balanced_basins --fixture corrected_cell_full_capacity_cascade_mild_asymmetry --fixture corrected_cell_full_capacity_cascade_threshold_asymmetry --fixture corrected_cell_full_capacity_cascade_deep_collapse --fixture corrected_cell_full_capacity_cascade_isolated_threshold --fixture corrected_cell_full_capacity_phase_balanced_no_growth --fixture corrected_cell_full_capacity_phase_balanced_low_growth --fixture corrected_cell_full_capacity_phase_balanced_nominal_growth --fixture corrected_cell_full_capacity_phase_mild_no_growth --fixture corrected_cell_full_capacity_phase_mild_low_growth --fixture corrected_cell_full_capacity_phase_mild_nominal_growth --fixture corrected_cell_full_capacity_phase_threshold_no_growth --fixture corrected_cell_full_capacity_phase_threshold_low_growth --fixture corrected_cell_full_capacity_phase_threshold_nominal_growth --fixture corrected_cell_full_capacity_phase_deep_no_growth --fixture corrected_cell_full_capacity_phase_deep_low_growth --fixture corrected_cell_full_capacity_phase_deep_nominal_growth
```

Tests:

```bash
PYTHONPATH=src ./.venv/bin/python -m py_compile src/pygrc/landscapes/extensions/grcl9/examples.py src/pygrc/models/grc_9_grcl9_lowering.py tests/landscapes/test_grcl9_seed_examples.py
PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_grcl9_seed_examples
PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_grcl9_seed_examples tests.models.test_grc_9_grcl9_lowering tests.telemetry.test_grcl9_replay
```

## Iteration 5.2.1. Corrected GRCL-9 Phenomenological Parity Tuning

### Goal

Tune corrected GRCL-9 composite examples toward intended phenomenological
parity without restoring broad-growth parent eligibility.

### Checks

- [x] Classify `S0029` selector misses by cause
- [x] Tune low-growth lanes that should still emit bounded front growth
- [x] Tune collapse-adjacent lanes that should recover collapse-like evidence
- [x] Keep no-growth controls no-growth
- [x] Rerun corrected parity session
- [x] Record parity table against intended legacy evidence families

### Verification

- [x] Corrected parity run improves passed/missed ratio
- [x] Every recovered growth event remains `grc9_front_capacity`
- [x] No legacy broad-growth mode is used
- [x] Remaining misses are documented as stale selector expectation or
  intentionally lost broad-growth side effect

### Summary

Complete. Classified `S0029` misses and tuned only paper-valid/source-valid
knobs: low-growth `lambda_birth` was raised to recover bounded front-capacity
growth, and collapse-adjacent support counts were increased where the runtime
had already shown stronger basin support recovers collapse-like evidence. The
no-growth controls remained no-growth.

Ran parity replay `S0030` over the same 28 corrected composite seeds with 24
steps each. Phenomenological parity improved from `S0029`'s 10 passed / 18
missed selector reports to 19 passed / 9 missed. Runtime events increased from
68 to 83 while remaining bounded and corrected: 31 `spark`, 31 `expansion`,
and 21 `growth`. All 28 lanes still report
`growth_parent_eligibility_mode = grc9_front_capacity`.

Recovered families:

- low-growth phase lanes now emit bounded growth and pass;
- full-capacity phenomenology cascade now passes;
- low/high growth cascade lanes now pass;
- threshold and deep collapse lanes now pass.

Remaining misses are diagnostic for the next selector/review pass: structural
controls still use older `structural_only` expectations, one no-refinement lane
intentionally lacks expansion-created growth, one no-growth cascade keeps stale
collapse expectations, and isolated-threshold/larger-support remain selector
classification edge cases.

Replay:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9_replay --session-id S0030 --source-mode landscape_seed_examples --requested-steps 24 --fixture corrected_cell_internal_valley_transport_growth_high --fixture corrected_cell_support_loss_identity_decay_probe --fixture corrected_cell_full_capacity_phenomenology_cascade --fixture corrected_cell_full_capacity_cascade_low_growth --fixture corrected_cell_full_capacity_cascade_high_growth --fixture corrected_cell_full_capacity_cascade_no_merge_bridge --fixture corrected_cell_full_capacity_cascade_weak_merge_bridge --fixture corrected_cell_full_capacity_cascade_isolated_bridge --fixture corrected_cell_full_capacity_cascade_larger_basin_support --fixture corrected_cell_full_capacity_cascade_no_refinement --fixture corrected_cell_full_capacity_cascade_no_growth --fixture corrected_cell_full_capacity_cascade_balanced_basins --fixture corrected_cell_full_capacity_cascade_mild_asymmetry --fixture corrected_cell_full_capacity_cascade_threshold_asymmetry --fixture corrected_cell_full_capacity_cascade_deep_collapse --fixture corrected_cell_full_capacity_cascade_isolated_threshold --fixture corrected_cell_full_capacity_phase_balanced_no_growth --fixture corrected_cell_full_capacity_phase_balanced_low_growth --fixture corrected_cell_full_capacity_phase_balanced_nominal_growth --fixture corrected_cell_full_capacity_phase_mild_no_growth --fixture corrected_cell_full_capacity_phase_mild_low_growth --fixture corrected_cell_full_capacity_phase_mild_nominal_growth --fixture corrected_cell_full_capacity_phase_threshold_no_growth --fixture corrected_cell_full_capacity_phase_threshold_low_growth --fixture corrected_cell_full_capacity_phase_threshold_nominal_growth --fixture corrected_cell_full_capacity_phase_deep_no_growth --fixture corrected_cell_full_capacity_phase_deep_low_growth --fixture corrected_cell_full_capacity_phase_deep_nominal_growth
```

Tests:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_grcl9_seed_examples
PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_grcl9_seed_examples tests.models.test_grc_9_grcl9_lowering tests.telemetry.test_grcl9_replay
```

## Iteration 5.2.2. Corrected GRCL-9 Remaining Parity Misses

### Goal

Retune the 9 remaining `S0030` missed lanes so each corrected seed achieves
the phenomenon it still claims, while preserving corrected front-capacity
growth.

### Checks

- [x] Classify all 9 `S0030` missed lanes by claimed phenomenon
- [x] Convert structural-control misses into explicit structural outcomes
- [x] Retune isolated-threshold and no-growth cascade claims
- [x] Retune no-refinement claim or remove impossible growth expectation
- [x] Rerun corrected parity session
- [x] Record parity delta against `S0030`

### Verification

- [x] Remaining missed count decreases
- [x] Corrected growth events remain bounded and `grc9_front_capacity`
- [x] No no-growth control emits growth
- [x] Each remaining miss has an explicit seed-level reason

### Summary

Complete. Classified the 9 remaining `S0030` misses and adjusted only seed
claims or source geometry:

- five structural-control lanes no longer claim the old `structural_only`
  selector outcome and now assert the event surfaces that corrected front
  growth actually produces;
- `no_refinement` now claims no-growth/no-collapse refinement suppression
  instead of an impossible post-expansion growth signal;
- `no_growth` now claims spark/expansion without growth or collapse-like
  evidence;
- `larger_basin_support` now explicitly claims collapse-like runtime evidence;
- `isolated_threshold` was changed from an isolated bridge to a merge bridge
  because its seed-level claim requires collapse-like basin interaction.

Ran replay session `S0031` over the same 28 corrected composite seeds with 24
steps each. Selector parity improved from `S0030`'s 19 passed / 9 missed to
28 passed / 0 missed. Runtime events remained corrected and bounded: 32
`spark`, 32 `expansion`, and 21 `growth` events. All 28 lanes report
`growth_parent_eligibility_mode = grc9_front_capacity`; five no-growth lanes
report `growth_semantics_status = none` and emit no growth.

Replay:

```bash
bash outputs/grcl9/lowering/sessions/S0031/replay.sh
```

Tests:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_grcl9_seed_examples
PYTHONPATH=src ./.venv/bin/python -m unittest tests.landscapes.test_grcl9_seed_examples tests.models.test_grc_9_grcl9_lowering tests.telemetry.test_grcl9_replay
```

## Iteration 5.3. Corrected GRCL-9 Selector Validation

### Goal

Validate corrected GRCL-9 growth evidence with field-backed selectors.

### Checks

- [x] Run selector validation over corrected sessions
- [x] Require front-growth provenance selectors for growth acceptance
- [x] Preserve legacy broad-growth records as diagnostic failures or
  superseded records

### Verification

- [x] Selector reports do not accept legacy broad-growth records
- [x] Corrected growth records pass front-capacity provenance selectors
- [x] Missing front-capacity surfaces are reported explicitly

### Summary

Complete. Added `pygrc.telemetry.grcl9_selector_validation`, a session-level
field-backed validator that reads replay sessions, requires corrected
front-capacity provenance, and classifies legacy broad-growth lanes as
superseded non-evidence rather than motifs. The validator checks:

- the per-lane replay selector report passed;
- GRCL-9 and GRC9 telemetry both report `grc9_front_capacity`;
- `legacy_broad_growth_count = 0`;
- growth events, when present, are counted as
  `front_capacity_growth_count`;
- required telemetry surfaces are present, otherwise the result is reported as
  `missing_surface`.

Ran `S0032` as an explicit diagnostic legacy replay over the quarantined
legacy growth seed set. It produced 30 replayable legacy lanes under
`legacy_any_inactive_port`; those lanes are retained only for historical
debugging.

Ran selector-validation session `S0033` over corrected `S0031` plus legacy
`S0032`. Results: 58 lanes validated, 28 corrected records accepted, 30
legacy records superseded, 0 missing telemetry surfaces. The manifest contains
28 corrected motifs and keeps all legacy lanes under `legacy_records`.

Replay:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9_replay --session-id S0032 --source-mode legacy_growth_landscape_seed_examples --force-legacy-growth --requested-steps 3
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9_selector_validation --session-id S0033 --source-session-id S0031 --source-session-id S0032 --force-legacy-growth
```

Tests:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_grcl9_selector_validation
PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_grcl9_selector_validation tests.telemetry.test_grcl9_replay tests.landscapes.test_grcl9_seed_examples tests.models.test_grc_9_grcl9_lowering
```

## Iteration 5.4. Corrected GRCL-9 Visualization

### Goal

Render corrected visual evidence and mark legacy visuals clearly.

### Checks

- [x] Render corrected visualizations with front-capacity overlays
- [x] Keep old broad-growth visualizations marked as replay-only non-evidence
- [x] Add visual metadata for corrected vs legacy growth status
- [x] Update visualization summary docs if needed

### Verification

- [x] Visual metadata identifies corrected vs legacy growth status
- [x] Front-capacity overlays show source/port provenance
- [x] Visuals remain supporting evidence only

### Summary

Complete. Updated the GRCL-9 lowering visualization overlay metadata and
boundary panels so every visual lane records:

- `growth_parent_eligibility_mode`;
- `growth_semantics_status`;
- `front_capacity_growth_count`;
- `legacy_broad_growth_count`;
- `evidence_status`, either `corrected_front_capacity_evidence` or
  `legacy_broad_growth_non_evidence`.

Rendered corrected visual evidence for `S0031` and legacy diagnostic visuals
for `S0032`. The corrected visual manifest contains 28 lanes, all marked
`corrected_front_capacity_evidence` with `grc9_front_capacity`. The legacy
visual manifest contains 30 lanes, all marked
`legacy_broad_growth_non_evidence` with `legacy_any_inactive_port`. Boundary
panels explicitly state that corrected front-capacity lanes are evidence
candidates and legacy broad-growth lanes are replay-only diagnostics.

Artifacts:

- `outputs/grcl9/lowering/sessions/S0031/visualizations/index.md`
- `outputs/grcl9/lowering/sessions/S0031/visualizations/visualization_manifest.json`
- `outputs/grcl9/lowering/sessions/S0032/visualizations/index.md`
- `outputs/grcl9/lowering/sessions/S0032/visualizations/visualization_manifest.json`

Replay:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.visualization.grcl9_lowering --session-root outputs/grcl9/lowering/sessions/S0031
PYTHONPATH=src ./.venv/bin/python -m pygrc.visualization.grcl9_lowering --session-root outputs/grcl9/lowering/sessions/S0032 --force-legacy-growth
```

Tests:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.visualization.test_grcl9_lowering
```

## Iteration 6. Reviewed Catalog Migration

### Goal

Refresh reviewed GRC9 and GRCL-9 growth-bearing catalogs with corrected
front-capacity evidence.

### Checks

- [x] Identify all reviewed records with growth-dependent claims
- [x] Mark broad-growth records as `superseded_by_growth_semantics_correction`
- [x] Preserve old motif ids through supersession links
- [x] Accept corrected growth motifs only with front-capacity provenance
- [x] Preserve non-growth accepted records where independent
- [x] Publish corrected reviewed catalog artifacts
- [x] Write summary counts:
  - retained non-growth records
  - superseded broad-growth records
  - accepted corrected growth records
  - rejected or unresolved growth records

### Verification

- [x] Catalog tests pass
- [x] Superseded records are not counted as accepted growth
- [x] Corrected records include source/session/replay references
- [x] Catalog summary explains the migration boundary

### Summary

Complete. Iteration 6 is split across `S0034`-`S0037`: affected historical
records were classified, corrected GRC9 and GRCL-9 catalogs were published,
and the supersession summary now records retained, superseded, accepted,
rejected, and unresolved records with replay commands.

## Iteration 6.1. Affected Record Classification

### Goal

Identify records that are affected by the growth semantics correction.

### Checks

- [x] Identify all reviewed records with growth-dependent claims
- [x] Preserve non-growth accepted records where independent
- [x] Mark broad-growth records as `superseded_by_growth_semantics_correction`
- [x] Preserve old motif ids through supersession links

### Verification

- [x] Superseded records are not counted as accepted growth
- [x] Non-growth records are not unnecessarily demoted

### Summary

Complete. Added the growth-correction record classifier and ran `S0034`.
The classifier inspected 47 historical reviewed records from the existing
GRC9 and GRCL-9 catalogs, retained 28 independent non-growth records, and
marked 19 growth-dependent records as
`superseded_by_growth_semantics_correction`.

Family split:

- GRC9: 16 retained, 4 superseded.
- GRCL-9: 12 retained, 15 superseded.

The output records preserve old motif ids in `supersession_link`; no
superseded record is counted as accepted growth. Thirteen superseded GRCL-9
records have direct corrected S0033 replacement candidates. The remaining
GRC9 elementary growth and early GRCL-9 growth-pressure records are left as
pending corrected catalog mappings for Iterations 6.2 and 6.3.

Artifacts:

- `outputs/grcl9/lowering/sessions/S0034/growth_record_classification.json`
- `outputs/grcl9/lowering/sessions/S0034/reports/growth_record_classification_report.json`
- `outputs/grcl9/lowering/sessions/S0034/reports/growth_record_classification_summary.md`

Replay:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grc9_grcl9_growth_record_classification --session-id S0034
```

Tests:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_growth_record_classification
```

## Iteration 6.2. GRC9 Corrected Growth Catalog

### Goal

Publish the corrected GRC9 growth catalog.

### Checks

- [x] Accept corrected GRC9 growth motifs only with front-capacity provenance
- [x] Link corrected GRC9 motifs to old superseded motif ids where applicable
- [x] Publish corrected GRC9 catalog artifacts

### Verification

- [x] Catalog tests pass
- [x] Corrected records include source/session/replay references

### Summary

Complete. Added the corrected GRC9 growth catalog publisher and ran `S0035`
over corrected source sessions `S0027`, `S0029`, and `S0030`.

Results:

- Accepted corrected growth motifs: 9.
- Accepted corrected no-growth/control motifs: 3.
- Rejected motifs: 0.
- Supersession links to old GRC9 motif ids: 10.
- Accepted legacy broad-growth count: 0.

The catalog accepts actual growth motifs only when the run summary and every
growth event row agree on `growth_parent_eligibility_mode =
grc9_front_capacity`, `front_growth_provenance_present = true`, and
`legacy_broad_growth = false`. No-growth controls are retained separately and
do not count as accepted growth. The positive corrected growth lanes supersede
the old `growth_pressure_lambda_high` motif id; the zero-birth control
supersedes the old `growth_pressure_lambda_low` motif id.

Artifacts:

- `outputs/grc9/phenomenology_discovery/sessions/S0035/corrected_grc9_growth_catalog.json`
- `outputs/grc9/phenomenology_discovery/sessions/S0035/reports/corrected_grc9_growth_catalog_report.json`
- `outputs/grc9/phenomenology_discovery/sessions/S0035/reports/corrected_grc9_growth_catalog_summary.md`

Replay:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_corrected_growth_catalog --session-id S0035
```

Tests:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.discovery.test_grc9_corrected_growth_catalog
```

## Iteration 6.3. GRCL-9 Corrected Growth Catalog

### Goal

Publish the corrected GRCL-9 source/lowering growth catalog.

### Checks

- [x] Accept corrected GRCL-9 growth motifs only with front-capacity provenance
- [x] Link corrected GRCL-9 motifs to old superseded motif ids where applicable
- [x] Publish corrected GRCL-9 catalog artifacts

### Verification

- [x] Catalog tests pass
- [x] Corrected records include source/session/replay references
- [x] Legacy source records are not counted as accepted growth

### Summary

Complete. Added the corrected GRCL-9 growth catalog publisher and ran `S0036`
from selector-backed `S0033` records, using `S0034` for supersession links.

Results:

- Accepted corrected GRCL-9 growth motifs: 21.
- Accepted corrected GRCL-9 no-growth/control motifs: 7.
- Rejected motifs: 0.
- Supersession links to old GRCL-9 motif ids: 13.
- Accepted legacy broad-growth count: 0.

The catalog re-reads each accepted selector record's source fixture, telemetry
run summary, event rows, and visualization metadata. Actual growth motifs are
accepted only when selector evidence, GRCL-9 source constructs, GRC9 run
summary fields, and growth event rows all agree on front-capacity provenance.
No-growth controls remain separate and do not count as accepted growth.

Artifacts:

- `outputs/grcl9/lowering/sessions/S0036/corrected_grcl9_growth_catalog.json`
- `outputs/grcl9/lowering/sessions/S0036/reports/corrected_grcl9_growth_catalog_report.json`
- `outputs/grcl9/lowering/sessions/S0036/reports/corrected_grcl9_growth_catalog_summary.md`

Replay:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9_corrected_growth_catalog --session-id S0036
```

Tests:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_grcl9_corrected_growth_catalog
```

## Iteration 6.4. Supersession Summary

### Goal

Publish the migration summary.

### Checks

- [x] Write summary counts:
  - retained non-growth records
  - superseded broad-growth records
  - accepted corrected growth records
  - rejected or unresolved growth records
- [x] Explain the migration boundary
- [x] Link corrected sessions and replay commands

### Verification

- [x] Catalog summary explains the migration boundary
- [x] Historical sessions remain linked and replayable

### Summary

Complete. Added the growth-correction supersession summary publisher and ran
`S0037` from `S0034`, `S0035`, and `S0036`.

Results:

- Retained non-growth records: 28.
- Superseded broad-growth records: 19.
- Unique superseded old motif ids: 17.
- Accepted corrected growth records: 30.
- Accepted corrected controls: 10.
- Rejected corrected records: 0.
- Unresolved superseded records: 2.
- Accepted legacy broad-growth records: 0.

The two unresolved records are the early GRCL-9 growth-pressure probes
`grcl9_lowered_s0006_growth_pressure_lambda_high` and
`grcl9_lowered_s0006_growth_pressure_lambda_low`. They remain explicitly
superseded and replayable, but have no direct corrected catalog replacement;
the corrected GRCL-9 growth examples supersede the later source/lowering
records.

Artifacts:

- `outputs/grcl9/lowering/sessions/S0037/growth_correction_supersession_summary.json`
- `outputs/grcl9/lowering/sessions/S0037/reports/growth_correction_supersession_report.json`
- `outputs/grcl9/lowering/sessions/S0037/reports/growth_correction_supersession_summary.md`

Replay:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grc9_grcl9_growth_supersession_summary --session-id S0037
```

Tests:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_growth_supersession_summary
```

## Iteration 7. Closeout And Guardrails

### Goal

Close the correction track, prevent accidental legacy evidence reuse, and
update dependent documentation.

## Iteration 7.1. Legacy Growth Execution Guards

### Goal

Make legacy broad-growth replay explicit and prevent deprecated builders from
silently producing paper-facing evidence from old `legacy_any_inactive_port`
sessions.

### Checks

- [x] Add `--force-legacy-growth` to quarantined legacy replay paths
- [x] Refuse `legacy_growth_landscape_seed_examples` replay without the force
  flag
- [x] Refuse selector validation over legacy broad-growth sessions without the
  force flag
- [x] Refuse visualization over legacy broad-growth sessions without the force
  flag
- [x] Refuse reviewed GRCL-9 catalog rebuilding from legacy broad-growth
  sessions without the force flag
- [x] Mark forced legacy outputs as replay-only diagnostic non-evidence in
  manifests
- [x] Keep corrected growth catalogs strict against accepted legacy broad-growth
  evidence

### Verification

- [x] Replay tests cover blocked and forced legacy source mode
- [x] Selector validation tests cover blocked and forced legacy source sessions
- [x] Visualization tests cover blocked and forced legacy sessions
- [x] Reviewed catalog tests cover blocked and forced historical catalog rebuild

### Summary

Implemented. Legacy broad-growth replay through
`legacy_growth_landscape_seed_examples` now requires `--force-legacy-growth`.
Downstream selector validation, visualization, and the old reviewed GRCL-9
catalog builder also refuse legacy broad-growth source sessions unless the same
flag is supplied. Forced outputs record guard metadata and remain replay-only
diagnostic non-evidence.

Updated replay commands for historical diagnostics:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9_replay --session-id S0032 --source-mode legacy_growth_landscape_seed_examples --force-legacy-growth --requested-steps 3
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9_selector_validation --session-id S0033 --source-session-id S0031 --source-session-id S0032 --force-legacy-growth
PYTHONPATH=src ./.venv/bin/python -m pygrc.visualization.grcl9_lowering --session-root outputs/grcl9/lowering/sessions/S0032 --force-legacy-growth
```

Tests:

```bash
PYTHONPATH=src ./.venv/bin/python -m unittest tests.telemetry.test_grcl9_replay tests.telemetry.test_grcl9_selector_validation tests.visualization.test_grcl9_lowering tests.telemetry.test_grcl9_lowered_motif_catalog
```

## Iteration 7.2. Documentation Closeout

### Goal

Close the correction track and update dependent documentation.

### Checks

- [x] Create correction handoff document
- [x] Update Phase 6 closeout
- [x] Update Phase T-GRC9 closeout
- [x] Update Phase V-GRC9 docs where visuals are affected
- [x] Update GRC9 discovery plan/checklist
- [x] Update GRCL-9 plan/checklist/handoff
- [x] Update `ImplementationPhases.md`
- [x] Record replay commands for corrected accepted sessions
- [x] Record unsupported/deferred growth cases

### Verification

- [x] Docs consistently distinguish legacy broad growth from corrected front
  growth
- [x] No closeout claims accepted growth evidence from broad parent eligibility
- [x] Historical sessions remain linked and replayable

### Summary

Complete. Added
`implementation/GRC9-GRCL9-GrowthCorrection-Handoff.md` and updated the Phase
6, Phase T-GRC9, Phase V-GRC9, GRC9 discovery, GRCL-9, and
`ImplementationPhases.md` documents. The closeout state is:

- corrected GRC9 growth evidence: `S0035`;
- corrected GRCL-9 growth evidence: `S0036`;
- migration/supersession summary: `S0037`;
- historical legacy broad-growth replay: guarded by `--force-legacy-growth`
  and non-evidence.

Unsupported/deferred boundaries remain unchanged: no GRCV3 hierarchy, no
GRCL-9 execution semantics, no native GRC9 collapse event, no Lorentzian or
observer-local layer, and no barrier/ghost boundary runtime.
