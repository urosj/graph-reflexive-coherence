# Phase 6 Closeout

## Purpose

This note records the closeout-facing state of the Phase 6 `GRC9` mechanical
baseline after Iteration 11.

Post-closeout note: the implemented GRC9 growth rule preserves the Section 8.4
birth probability and lowest-port attachment behavior. The later growth
correction has now separated historical broad inactive-port parent eligibility
from paper-facing front-capacity growth. The completed migration is recorded in
[GRC9-GRCL9-GrowthCorrection-Plan.md](./GRC9-GRCL9-GrowthCorrection-Plan.md)
and
[GRC9-GRCL9-GrowthCorrection-Checklist.md](./GRC9-GRCL9-GrowthCorrection-Checklist.md),
with closeout handoff in
[GRC9-GRCL9-GrowthCorrection-Handoff.md](./GRC9-GRCL9-GrowthCorrection-Handoff.md).
Historical broad-growth outputs remain replayable only to reproduce or debug
the old behavior; they are not evidence for any paper-facing claim. Corrected
growth evidence must come from `grc9_front_capacity` runs and the corrected
catalogs `S0035` / `S0036`.

Post-closeout budget robustness note: pure GRC9 does not carry the GRC9V3
`M_i` basin-mass semantic field, so it does not need the Phase 7 basin-mass
repair. It does carry the mechanical scalar budget invariant `B = sum_i C_i`.
Iteration 12 now locks `budget_target` during construction / `from_state(...)`
normalization when no explicit target is supplied and records
`budget_target_source` for replay. The former lazy inference path remains only
as a compatibility fallback, so existing normal-path Phase 6 results are not
automatically invalidated.

The point of this closeout is not to claim that every later-family extension is
already present. The point is to state clearly what is now justified for core
`GRC9` itself, what evidence supports that claim, and what remains explicitly
outside the Phase 6 mechanical closure boundary.

## What Was Implemented

Phase 6 now provides:

- an executable end-to-end `GRC9` step loop with deterministic spark,
  expansion, growth, budget closure, and coarse-grain / Split support
- a representative artifact-backed `GRC9` telemetry lane:
  - `telemetry.run_grc9_representative_experiment(...)`
- a seed-driven structural bridge from `LandscapeSeed` into `GRC9`:
  - `build_grc9_from_landscape_seed(...)`
  - `project_landscape_seed_to_grc9_state(...)`
  - `run_grc9_landscape_seed(...)`
- a canonical seed-driven telemetry lane on the real `cell-1` / `cell-4` seed
  pair:
  - `telemetry.run_grc9_landscape_experiment(...)`
- reconstruction scripts for both closeout-facing artifact lanes:
  - [run_grc9_representative_telemetry.py](../scripts/run_grc9_representative_telemetry.py)
  - [run_grc9_landscape_telemetry.py](../scripts/run_grc9_landscape_telemetry.py)

The seed-driven lowering is intentionally structural and mechanical:

- it reuses the validated `GRCV2` landscape blueprint boundary
- it lowers node priors and edge carriers into a nine-slot port graph
- it preserves source metadata and transport-intent multipliers where they are
  mechanically meaningful
- it should be read as a bridge/evidence lane, not as a full family-native
  source implementation
- it does not open `GRC9V3` semantic lowering, projector semantics, or rich
  collapse/choice semantics inside Phase 6

## Validated Evidence

### Representative Artifact Lane

The representative lane was executed with:

- lane name: `phase6_mechanical_baseline`
- steps: `4`
- comparison surface: `primary` vs `replay`

The reconstruction command used was:

```bash
./.venv/bin/python scripts/run_grc9_representative_telemetry.py \
  --outputs-root outputs \
  --lane-name phase6_mechanical_baseline \
  --steps 4
```

The run produced:

- primary run id:
  - `a687ba31354425cd1ec463e8b7837b5c6cc226cbec527cbd691c9e82ebcdbdc7`
- replay run id:
  - `4c690bc4046fb0c595d41cd515189f9b67899a75895b54411614dc3fab672a89`
- matching final snapshot digest on both sides:
  - `bb74921e588c5eac480771af29ee7ef830b267004a4bbbe937263f760e7f1a6d`

The concrete saved artifact lane is:

- `outputs/representative/grc9/phase6_mechanical_baseline/primary/.../telemetry/`
- `outputs/representative/grc9/phase6_mechanical_baseline/replay/.../telemetry/`

This remains the event-rich mechanical lane for saved evidence:

- spark is visible
- expansion is visible
- later growth is visible
- replay agreement is artifact-backed, not just in-memory

### Real-Seed Artifact Lane

The first seed-driven structural lane was executed with:

- profile name: `phase6_seed_baseline`
- seeds:
  - `configs/landscapes/seed/cell-1.seed.yaml`
  - `configs/landscapes/seed/cell-4.seed.yaml`
- steps: `3`

The reconstruction command used was:

```bash
./.venv/bin/python scripts/run_grc9_landscape_telemetry.py \
  --outputs-root outputs \
  --profile phase6_seed_baseline \
  --steps 3
```

The run produced:

- `cell-1` run id:
  - `d3a9436c2531247e99a91ce5993b4651ea0c26929b0b03c31904e81e997a3147`
- `cell-4` run id:
  - `6b79c2b7fdba7f7632fda65c4b6e92de3d5b0dafc6bb8154e5fdf06777d2df71`
- `cell-1` final snapshot digest:
  - `fb1a4785512993d771b2ca671a808726982b830287514cebbeb524424f41cfbb`
- `cell-4` final snapshot digest:
  - `b26397cb1beac83322f1c104212219e51fe737c082d24f68a3b7bc86e94d83af`

The concrete saved artifact lane is:

- `outputs/representative/grc9_landscape/phase6_seed_baseline/cell-1/.../telemetry/`
- `outputs/representative/grc9_landscape/phase6_seed_baseline/cell-4/.../telemetry/`

This seed lane should be read carefully:

- it proves that `GRC9` can ingest nontrivial in-house seed inputs without any
  `GRCV3` semantic dependency
- it does so through the existing `GRCV2` landscape blueprint boundary rather
  than through a family-native `GRCL-9` lowering layer
- it proves that the seed-lowered structural graph is deterministic enough for
  saved telemetry/report artifacts
- it does not claim that Phase 6 already supports the richer semantic source
  surfaces that later `GRC9V3` work may introduce

## What This Validates

This closeout justifies the following claims:

1. Core `GRC9` now runs end to end as an executable mechanical family without
   any `GRCV3` semantic dependency.
2. The rows/columns, spark trigger, expansion, growth, and coarse-grain /
   Split surfaces are now strong enough to support artifact-backed evidence,
   not only unit tests.
3. The representative eventful lane and the seed-driven structural lane answer
   different validation questions and now both exist in saved form.
4. The seed-driven `GRC9` lane is honest about its scope:
   it is a structural graph graft onto the mechanical nine-slot substrate via
   the existing `GRCV2` landscape blueprint boundary, not a hidden `GRC9V3`
   semantic projector and not a full `GRCL-9` implementation.

## Deferred Boundary

The following remain explicitly outside the Phase 6 closeout:

- `boundary_mode = barrier`
- `boundary_mode = ghost`
- a true family-native `GRCL-9` source/lowering layer analogous in role to the
  later `GRCL-v3` path
- dense rich-source artifact lanes that require family-local source semantics
  beyond structural graph lowering
- `GRC9V3` semantic lifts such as richer projector/source semantics,
  choice/collapse semantics, or hybrid source-conditioned observability

These are not hidden gaps in the Phase 6 mechanical claim. They are the
declared next boundary.

For the rich-source lane specifically, the correct decision at Phase 6 closeout
is deferment:

- the real-seed structural lane now exists
- but Phase 6 still does not open a family-local rich source semantics surface
- so a dense rich-source lane would over-claim what the family currently means

That denser lane belongs only after the semantic/source boundary is opened
explicitly in later `GRC9V3` work.

## Closeout Result

Phase 6 can now be treated as the authoritative mechanical `GRC9` substrate:

- executable
- replay-stable
- artifact-backed
- seed-driven at the structural level
- corrected for paper-facing front-capacity growth evidence through the
  post-closeout growth migration
- corrected for construction-time scalar budget target locking without adding
  GRC9V3 basin semantics
- explicit about the remaining boundary to `GRC9V3`

That is enough for honest Phase 6 closeout. It is not a claim that the later
hybrid/source-conditioned work is already done.
