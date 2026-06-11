# Seed Landscapes

This directory contains two kinds of seed fixtures:

- canonical normalized fixtures derived from the PDE landscape DSL
- manual research fixtures used to probe family-specific graph behavior

These files are intended as:

- translator target fixtures,
- documentation anchors for normalization and rich-seed rules,
- executable probes for family-local projector/runtime hypotheses,
- and future implementation references when a fuller translator is written.

## PDE-normalized fixtures

These are the direct normalization targets for the PDE landscape corpus:

- `cell-1.seed.yaml`
- `cell-4.seed.yaml`
- `s6-periodic-seam-ring.seed.yaml`

They use:

- `translation_mode: lossless_source_normalization`

That means:

- explicit PDE primitives are mapped directly,
- source/compiler metadata is preserved under `extensions.source_pde`,
- and source-implied structures such as `saddle` remain annotations unless an
  explicit enrichment pass is requested.

## Manual research fixtures

These are authored directly in the seed language to test GRC-family behavior:

- `spark-probe-cross.seed.yaml`
- `grcv3-rich-junction-probe.seed.yaml`
- `grcv3-rich-basin-boundary-channel-probe.seed.yaml`
- `grcv3-rich-v3-interior-spindle-probe.seed.yaml`
- `grcv3-rich-v3-partitioned-spindle-probe.seed.yaml`
- `grcv3-rich-v3-load-carrier-spindle-probe.seed.yaml`
- `grcv3-rich-v3-load-carrier-weak-to-stable-probe.seed.yaml`
- `grcv3-rich-v4-transfer-mediation-probe.seed.yaml`
- `grcv3-rich-collapse-example.seed.yaml`
- `grcl9-spark-column-proxy-eps-pass.seed.yaml`
- `grcl9-spark-column-proxy-eps-fail.seed.yaml`
- `grcl9-spark-instability-tau-pass.seed.yaml`
- `grcl9-spark-instability-tau-fail.seed.yaml`
- `grcl9-spark-to-expansion-d-eff-low.seed.yaml`
- `grcl9-spark-to-expansion-d-eff-high.seed.yaml`
- `grcl9-corrected-front-growth-positive-high.seed.yaml`
- `grcl9-corrected-front-growth-no-growth-low.seed.yaml`
- `grcl9-corrected-front-growth-no-front-fail.seed.yaml`
- `grcl9-corrected-front-growth-closed-front-fail.seed.yaml`
- `grcl9-post-expansion-fission-min-mass-pass.seed.yaml`
- `grcl9-post-expansion-fission-min-mass-fail.seed.yaml`
- `grcl9-cell-boundary-ridge-membrane-spark-pass.seed.yaml`
- `grcl9-cell-plateau-nested-basins-fission-pass.seed.yaml`
- `grcl9-cell-saddle-branch-instability-pass.seed.yaml`
- `grcl9-cell-refinement-budget-partition-expansion-high.seed.yaml`
- `grcl9-cell-membrane-rupture-structural-probe.seed.yaml`
- `grcl9-cell-basin-merge-before-persistence-probe.seed.yaml`
- `grcl9-cell-saddle-choice-pressure-structural-probe.seed.yaml`
- `grcl9-cell-basin-merge-runtime-collapse-probe.seed.yaml`
- `grcl9-cell-basin-merge-runtime-stability-control.seed.yaml`
- `grcl9-cell-developed-basin-centroid-collapse-long-window.seed.yaml`
- `grcl9-corrected-cell-internal-valley-transport-growth-high.seed.yaml`
- `grcl9-corrected-cell-support-loss-identity-decay-probe.seed.yaml`
- `grcl9-corrected-cell-full-capacity-phenomenology-cascade.seed.yaml`
- `grcl9-corrected-cell-full-capacity-cascade-*.seed.yaml`
- `grcl9-corrected-cell-full-capacity-phase-*.seed.yaml`
- `grcl9v3-hybrid-spark-gate-positive.seed.yaml`
- `grcl9v3-hybrid-spark-gate-negative.seed.yaml`
- `grcl9v3-spark-to-expansion-positive.seed.yaml`
- `grcl9v3-spark-to-expansion-negative.seed.yaml`
- `grcl9v3-appendix-e-cell-division-positive.seed.yaml`
- `grcl9v3-choice-collapse-positive.seed.yaml`
- `grcl9v3-choice-collapse-negative.seed.yaml`
- `grcl9v3-transport-basin-rerouting-positive.seed.yaml`
- `grcl9v3-quiescent-hybrid-control.seed.yaml`
- `grcl9v3-hybrid-choice-transport.seed.yaml`
- `grcl9v3-cell-boundary-membrane-spark.seed.yaml`
- `grcl9v3-cell-nested-basin-hierarchy.seed.yaml`
- `grcl9v3-cell-saddle-tensor-choice.seed.yaml`
- `grcl9v3-cell-refinement-budget-expansion.seed.yaml`
- `grcl9v3-cell-choice-collapse.seed.yaml`
- `grcl9v3-appendix-e-cell-division-composing-cell.seed.yaml`
- `grcl9v3-corrected-front-growth-positive.seed.yaml`
- `grcl9v3-corrected-front-growth-no-growth.seed.yaml`
- `grcl9v3-corrected-hybrid-spark-expansion-growth.seed.yaml`
- `grcl9v3-corrected-hybrid-appendix-e-growth.seed.yaml`
- `grcl9v3-corrected-hybrid-full-composition.seed.yaml`
- `grcl9v3-corrected-cell-internal-valley-growth-transport.seed.yaml`
- `grcl9v3-corrected-appendix-e-cell-division-full-capacity-cascade.seed.yaml`
- `grcl9v3-corrected-appendix-e-cell-division-full-capacity-bounded-growth.seed.yaml`
- `grcl9v3-corrected-appendix-e-cell-division-full-capacity-zero-birth.seed.yaml`
- `grcl9v3-corrected-appendix-e-cell-division-full-capacity-closed-front.seed.yaml`
- `grcl9v3-corrected-appendix-e-cell-division-full-capacity-balanced-choice.seed.yaml`
- `grcl9v3-corrected-multi-center-collapse-learning.seed.yaml`
- `grcl9v3-corrected-multi-center-delayed-collapse-learning.seed.yaml`
- `grcl9v3-corrected-multi-center-relay-attempt.seed.yaml`
- `grcl9v3-corrected-propagated-front-relay.seed.yaml`

Validation-only invalid fixture:

- `grcv3-rich-v4-invalid-underdetermined-mediation.seed.yaml`

Quarantined GRCL-9 legacy growth fixtures:

- `legacy/grcl9-overaggressive-growth/`

The quarantined GRCL-9 seeds are historical diagnostics from the pre-correction
standalone growth-locus interpretation. They remain replayable through the
explicit diagnostic source mode `legacy_growth_landscape_seed_examples`, but
they are excluded from normal default seed discovery and must not be used as
paper-facing front-growth evidence.

Quarantined GRCL-9V3 legacy growth fixtures:

- `legacy/grcl9v3-overaggressive-growth/`

The quarantined GRCL-9V3 seeds are historical diagnostics from Iterations
8.2-8.6. They used the earlier standalone growth-locus interpretation, where
authored growth loci could produce node births independently of spark-created
front capacity. They remain replayable through the explicit diagnostic source
mode `legacy_growth_landscape_seed_examples`, but they are excluded from normal
default seed discovery and should not be used as paper-facing growth evidence.

These are not translator targets. They exist to:

- test rich-seed lowering,
- probe spark/collapse behavior,
- and provide reproducible source-side examples for family-specific studies.

The GRCL-9 seeds carry authored Morse/landscape terms under
`extensions.grcl9` and primitive-level `extensions.grcl9` term payloads. They
are extracted into `grcl9.landscape_example.v1`, compiled into
`grcl9.source.v1`, and then lowered to GRC9 for telemetry replay.

The `grcl9-cell-*` seeds are ComposingCells-aligned probes. They retain the
same GRCL-9 lowering boundary, but their neutral primitive layout foregrounds
basins, ridges/membranes, valleys/channels, plateaus, and saddles before the
family-specific GRCL-9 terms are compiled into GRC9 mechanical preconditions.

The collapse-adjacent `grcl9-cell-*structural-probe` seeds are the next GRCL-9
batch after the first reviewed lowered motif catalog. They are structural
probes only: they may expose membrane/ridge weakening, basin-merge pressure,
support loss, failed fission persistence, or saddle pressure through existing
GRC9 telemetry/checkpoints, but they do not claim a GRC9 runtime collapse
event or import GRCV3 choice/collapse semantics.

The Iteration 8.2 `grcl9-cell-basin-merge-runtime-*` seeds are the first
collapse-producing discovery pair. The collapse probe intensifies asymmetric
post-refinement basin mass and saddle conductance; the stability control keeps
the two source-declared sink regions balanced. Classification still comes from
runtime GRC9 telemetry/checkpoints, not from the source seed.

`grcl9-cell-developed-basin-centroid-collapse-long-window.seed.yaml` is the
third, larger collapse-adjacent example. It runs over a longer window, lowers
two developed multi-node basin regions, and uses the GRCL-V3-style
`group_centroid` target-selection policy for the receiving basin. It remains a
diagnostic collapse-like observation: no GRC9 `collapse` event is claimed.

`grcl9-cell-full-capacity-phenomenology-cascade.seed.yaml` is the most complex
GRCL-9 seed in this batch. It composes membrane/ridge spark structure,
refinement, valley-driven growth pressure, developed fission basins, and
collapse-like target selection into one connected source. The accepted replay
is `outputs/grcl9/lowering/sessions/S0020/`.

The `grcl9-cell-full-capacity-cascade-*` robustness variants perturb S0020.
They are intentionally not all expected to pass the same selectors. S0021 and
S0022 record which signatures survive low/high growth, bridge
removal/weakening/isolation, larger basin support, no-refinement, and
no-growth controls.

The basin-asymmetry ladder variants keep the full-capacity cascade fixed and
vary only the post-refinement basin mass/stability profile. S0023 records the
threshold behavior: balanced basins become ambiguous by losing the A anchor,
mild asymmetry already loses B, and threshold/deep/isolated-threshold variants
produce collapse-like B-loss.

The `grcl9-cell-full-capacity-phase-*` variants extend the ladder into a small
phase diagram: four basin regimes crossed with no-growth, low-growth, and
nominal-growth settings. S0024 records all twelve lanes with classification
selectors so the result is a measured regime map rather than a preselected
pass/fail claim.

The first `grcl9v3-*` seeds are seed-backed GRCL-9V3 source examples anchored
in the GRC9V3 discovery handoff at
`outputs/grc9v3/phenomenology_discovery/sessions/S0014/source_language_handoff.json`.
They carry authored Morse/landscape terms under `extensions.grcl9v3` and
primitive-level `extensions.grcl9v3` payloads. They are extracted into
`grcl9v3.landscape_example.v1`, compiled into `grcl9v3.source.v1`, and lowered
to GRC9V3. These seeds are source declarations only: spark, expansion, growth,
choice/collapse, and quiescent evidence must still come from replay telemetry.

The Iteration 8.2.2 `grcl9v3-*` elementary completeness batch has replayable
evidence in `outputs/grcl9v3/lowering/sessions/S0010`, selector validation in
`S0011`, and visual review in `S0012`. It includes positive and negative
controls for spark, expansion, choice/collapse, and growth, plus transport,
quiescent, and Appendix E division evidence. The Appendix E seed uses
`target_effective_degree=51` because that runtime size is the first checked
setting in this batch that satisfies the daughter/hierarchy selectors.

Iteration 8.2.3 adds a Hessian backend diagnostic replay mode rather than new
seed files. `S0013` pairs existing seed-backed sources under
`row_basis_diagonal` and `weighted_least_squares`, `S0014` validates the ten
diagnostic lanes, and `S0015` renders the visuals. The probe found metric
divergence in row-basis differential fields, but no lifecycle event-count
delta, so hybrid composition continues with `row_basis_diagonal` as the default.

Iteration 8.3 adds the first GRCL-9V3 hybrid compositions:
`legacy/grcl9v3-overaggressive-growth/grcl9v3-hybrid-spark-expansion-growth.seed.yaml`,
`grcl9v3-hybrid-choice-transport.seed.yaml`,
`legacy/grcl9v3-overaggressive-growth/grcl9v3-hybrid-appendix-e-growth.seed.yaml`,
and
`legacy/grcl9v3-overaggressive-growth/grcl9v3-hybrid-full-composition.seed.yaml`.
Each seed records
`composed_source_ancestry` in `extensions.grcl9v3.notes`. `S0016` replays the
four composed seeds, `S0017` validates all four as strong candidates with zero
missing surfaces, and `S0018` renders the visual review. The full composition
emits spark, expansion, completed spark, growth, choice, and collapse events
from one connected lowered graph. Composed Appendix E ingredients use generic
`hybrid_expansion_events` selectors here because the
`representative_appendix_e_summary` surface is reserved for the standalone
representative Appendix E fixture. These growth-bearing Iteration 8.3 seeds are
now legacy diagnostic evidence only; corrected front-capacity replacements are
the `grcl9v3-corrected-hybrid-*` seeds in the main directory.

Iteration 8.4 adds ComposingCells-aligned GRCL-9V3 seeds. These use neutral
landscape primitives first - basins, plateaus, ridges/membranes, valleys,
saddles, and junctions - and carry the family-specific meaning in
`extensions.grcl9v3`. `S0019` replays the seven cell-style seeds, `S0020`
validates all seven as strong candidates, and `S0021` renders the visuals. The
batch covers membrane spark, internal valley growth/transport, nested
basin/hierarchy, saddle tensor choice, refinement with budget-partition
intent, choice/collapse, and Appendix E cell division. Budget partition remains
a source intent observed through runtime telemetry, not a solved source claim.
The original `grcl9v3-cell-internal-valley-growth-transport.seed.yaml` is now
quarantined under `legacy/grcl9v3-overaggressive-growth/`; the corrected
front-capacity replacement is
`grcl9v3-corrected-cell-internal-valley-growth-transport.seed.yaml`.

Iteration 8.5 adds the full-capacity GRCL-9V3 cascade family:

- `legacy/grcl9v3-overaggressive-growth/grcl9v3-appendix-e-cell-division-full-capacity-cascade.seed.yaml`
- `legacy/grcl9v3-overaggressive-growth/grcl9v3-appendix-e-cell-division-full-capacity-low-growth.seed.yaml`
- `legacy/grcl9v3-overaggressive-growth/grcl9v3-appendix-e-cell-division-full-capacity-balanced-choice.seed.yaml`
- `legacy/grcl9v3-overaggressive-growth/grcl9v3-appendix-e-cell-division-full-capacity-low-growth-balanced-choice.seed.yaml`

`S0022` runs the four lanes for 20 steps, `S0023` validates selectors, and
`S0024` renders visuals. The baseline composes Appendix E cell division,
hybrid spark/expansion, tensor/Hessian support, growth, transport, and
choice/collapse in one connected lowered graph. The balanced-choice
perturbation suppresses choice/collapse while preserving the rest of the
signature. The low-growth perturbations reduce growth sharply but do not
eliminate it over 20 steps, so they are recorded as candidates rather than
strong no-growth controls. These original 8.5 growth-bearing seeds are legacy
diagnostics after the Iteration 9 growth correction. Corrected replacements are
the `grcl9v3-corrected-appendix-e-cell-division-full-capacity-*` seeds in the
main directory.

Iteration 8.5.1 adds calibrated growth robustness probes:

- `legacy/grcl9v3-overaggressive-growth/grcl9v3-appendix-e-cell-division-full-capacity-ultra-low-growth.seed.yaml`
- `legacy/grcl9v3-overaggressive-growth/grcl9v3-appendix-e-cell-division-full-capacity-zero-birth.seed.yaml`
- `legacy/grcl9v3-overaggressive-growth/grcl9v3-appendix-e-cell-division-full-capacity-closed-growth-port.seed.yaml`
- `legacy/grcl9v3-overaggressive-growth/grcl9v3-appendix-e-cell-division-full-capacity-zero-birth-balanced-choice.seed.yaml`

These reuse the 8.5 full-capacity context. Ultra-low birth is scored as
bounded-growth evidence rather than no-growth. Exact zero birth and the
structural closed-growth-port probe are scored as no-growth controls.
`S0025` replays the probes, `S0026` validates all four as strong candidates,
and `S0027` renders visuals. The result separates residual bounded growth
(`lambda_birth=0.002`, two growth events) from true no-growth (`lambda_birth=0`
or omitted growth locus).
They are retained for comparison with the corrected no-birth and closed-front
seeds, not as current paper-facing front-growth evidence.

Iteration 8.6 adds multi-center collapse-learning probes:

- `legacy/grcl9v3-overaggressive-growth/grcl9v3-multi-center-collapse-learning.seed.yaml`
- `legacy/grcl9v3-overaggressive-growth/grcl9v3-multi-center-delayed-collapse-learning.seed.yaml`
- `legacy/grcl9v3-overaggressive-growth/grcl9v3-multi-center-balanced-no-collapse.seed.yaml`

These seeds exercise repeated growth loci and repeated choice/collapse regions
from one source-authored GRCL-9V3 example. The accepted replay keeps growth
pressure high and bounds the window to 20 steps. `S0030` replays the seeds,
`S0031` validates selectors, and `S0032` renders visuals. The main
multi-center collapse-learning seed is a strong candidate with growth before
later collapse and nonzero basin-assignment learning state. The delayed variant
is preserved as a candidate: it records growth, collapse, and learning, but not
collapse after first growth in the 20-step selector window. The balanced seed is
a strong no-collapse control.
These 8.6 seeds are now quarantined as over-aggressive standalone-growth
diagnostics. Corrected multi-center evidence uses
`grcl9v3-corrected-multi-center-*` seeds and the propagated-front relay probe.

Iteration 8.6.1 adds a runtime diagnostic sweep over the delayed multi-center
seed rather than new source seed files. `S0035` replays four `lambda_birth`
variants (`0.05`, `0.10`, `0.20`, `0.40`) for 50 steps, and `S0036` validates
selectors. The first strong growth-before-collapse threshold in this sweep is
`lambda_birth=0.20`. Every final collapsed sink in the sweep is runtime-grown,
not source-declared, which is recorded as basin-assignment-learning evidence
within the GRCL-9V3 source/runtime boundary.

Iteration 8.6.2 adds a recurrent relay diagnostic over the delayed
multi-center seed. It does not add new source seed files. `S0038` runs a
100-step `lambda_birth=0.20` replay and `S0039` validates relay selectors. The
probe records partial relay evidence (`growth child -> later collapsed sink`
and `collapsed sink -> later growth parent`) but no full same-node
`growth child -> collapsed sink -> growth parent` relay. The full recurrent
relay remains a future target.

Iteration 9.2 corrects the GRCL-9V3 growth interpretation. Paper-facing growth
now requires spark-created or explicitly source-front capacity before the
probabilistic birth rule can attach a child at the lowest available front port.
Corrected seeds stay in this directory with a `grcl9v3-corrected-*` prefix.
Legacy standalone-growth seeds moved to
`legacy/grcl9v3-overaggressive-growth/` in Iteration 9.2.6 and can be replayed
only through the diagnostic source mode. `S0071` is the replay smoke for that
path:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9v3_replay --session-id S0071 --steps 1 --source-mode legacy_growth_landscape_seed_examples --fixture multi_center_delayed_collapse_learning
```

Fixture verification rule:

- semantic comparison uses normalized runtime objects or normalized dict-like
  data derived from them
- raw YAML text equality is not the correctness criterion
- any intentional fixture change should be accompanied by a matching
  translator/test/doc update
