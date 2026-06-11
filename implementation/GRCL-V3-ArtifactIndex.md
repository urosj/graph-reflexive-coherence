# GRCL-v3 Artifact Index

This note is a compact evidence index for the current `GRCL-v3` arc.

It exists so later restart work can find the strongest saved runs, traces, and
scripts quickly without rereading the whole checklist first.

## 1. Read-First Saved Evidence

### 1.1 Rich-v4 Spark / Split / Collapse Lane

This is the saved dense artifact lane that established that one rich-v4
direct-translation run can show spark, split, and collapse together:

- `outputs/grcv3-rich-v4-spark-visual/grcv3-rich/seed_baseline/grcv3-rich-v4-transfer-mediation-probe/ddebe3a30b424d3841d447fc0a9e92d9097d18089eb1e8f9233f6f6afd88606a/telemetry/experiment_report.json`

Why it matters:

- this is the strongest saved all-in-one evidence lane for the current
  `GRCV3`/`GRCL-v3` cycle
- it proves that a rich source lane can carry spark, split, and collapse in
  one inspectable run

### 1.1a Dedicated Early-Collapse Example

This is the separate saved collapse-focused seed called out in the later
visualization closeout notes:

- [configs/landscapes/seed/grcv3-rich-collapse-example.seed.yaml](../configs/landscapes/seed/grcv3-rich-collapse-example.seed.yaml)

Why it matters:

- it is not the same lane as the rich-v4 all-in-one artifact run
- it exists specifically to make early collapse behavior and overlay semantics
  legible
- together with the rich-v4 artifact lane, it shows that collapse-capable
  evidence in the repo is already plural rather than a one-seed phenomenon

### 1.2 Settlement-Locus Regime Evidence Bundle

This is the clearest saved evidence for the two-regime settlement-locus result:

- `outputs/grcl-v3-iter38-settlement-locus/settlement_locus_regime_trace.json`
- `outputs/grcl-v3-iter38-settlement-locus/evidence/README.txt`

Why it matters:

- direct lane stays on the carrier-site regime
- mediated path lane first anchors on a path node and later migrates onto
  split children
- this is the richest phenomenology result recorded in the current side-quest

## 2. Key Later Trace Scripts

These scripts are the most useful restart points for the later
`transfer_mediation` / `settlement_regime` work:

- [scripts/trace_grcv3_path_intermediacy_failure.py](../scripts/trace_grcv3_path_intermediacy_failure.py)
  - earliest path-vs-direct divergence under added intermediacy
- [scripts/trace_grcv3_candidate_transition_failure.py](../scripts/trace_grcv3_candidate_transition_failure.py)
  - first failure point between near-correct geometry and actual candidate
    entry
- [scripts/trace_grcv3_settlement_locus_regimes.py](../scripts/trace_grcv3_settlement_locus_regimes.py)
  - stable carrier-site vs path-node regime characterization
- [scripts/trace_grcv3_settlement_reentry_boundary.py](../scripts/trace_grcv3_settlement_reentry_boundary.py)
  - repeating vs one-shot post-split reentry boundary
- [scripts/trace_grcv3_settlement_reentry_neighborhood_boundary.py](../scripts/trace_grcv3_settlement_reentry_neighborhood_boundary.py)
  - descendant neighborhood-role comparison
- [scripts/trace_grcv3_settlement_reentry_support_isolation.py](../scripts/trace_grcv3_settlement_reentry_support_isolation.py)
  - isolation of secondary carrier-neighbor vs ridge-support difference
- [scripts/trace_grcv3_settlement_reentry_secondary_support_counterfactual.py](../scripts/trace_grcv3_settlement_reentry_secondary_support_counterfactual.py)
  - decisive necessity/sufficiency counterfactual
- [scripts/trace_grcv3_secondary_support_authorability.py](../scripts/trace_grcv3_secondary_support_authorability.py)
  - authorability test that closed the extra-field question
- [scripts/trace_grcv3_collapse_regimes.py](../scripts/trace_grcv3_collapse_regimes.py)
  - collapse-side audit across the saved direct/path/split-child spindle lanes
- [scripts/trace_grcv3_broad_collapse_survey.py](../scripts/trace_grcv3_broad_collapse_survey.py)
  - broader survey across the separately recorded collapse-capable seed lanes
- [scripts/trace_grcv3_pre_spark_collapse_decomposition.py](../scripts/trace_grcv3_pre_spark_collapse_decomposition.py)
  - controlled comparison of the two recorded pre-spark collapse lanes to test
    whether their sink difference is already authored by existing structure
- [scripts/trace_grcv3_post_spark_collapse_boundary.py](../scripts/trace_grcv3_post_spark_collapse_boundary.py)
  - controlled comparison of the rich-v4 post-spark collapse lane against the
    tight center-coupling direct controls inside `transfer_mediation`
- [scripts/trace_grcv3_post_spark_late_window_stability.py](../scripts/trace_grcv3_post_spark_late_window_stability.py)
  - widened `150`-step rerun of the same post-spark trio to test whether the
    blocked control remains distinct or only converges later
- [scripts/trace_grcv3_post_spark_delay_authorability.py](../scripts/trace_grcv3_post_spark_delay_authorability.py)
  - matched-control authorability check that closes the blocked lane’s late
    delay inside existing `transfer_mediation.center_coupling_classes`
- [scripts/trace_grcv3_post_collapse_geometry_exclusion.py](../scripts/trace_grcv3_post_collapse_geometry_exclusion.py)
  - geometry phenomenology trace showing how the blocked lane is rerouted away
    from its initial collapsed sink without any explicit anti-reentry rule

## 3. Key Seed Fixtures

The most important rich-v4 spindle-lane seeds from the later side-quest are:

- [grcv3-rich-v4-transfer-mediation-probe.seed.yaml](../configs/landscapes/seed/grcv3-rich-v4-transfer-mediation-probe.seed.yaml)
  - saved rich-v4 spark/split/collapse lane
- [grcv3-rich-v4-mediated-spill-branch-probe.seed.yaml](../configs/landscapes/seed/grcv3-rich-v4-mediated-spill-branch-probe.seed.yaml)
  - productive direct control for the later regime work
- [grcv3-rich-v4-mediated-spill-branch-single-intermediate-probe.seed.yaml](../configs/landscapes/seed/grcv3-rich-v4-mediated-spill-branch-single-intermediate-probe.seed.yaml)
  - productive path-node regime lane
- [grcv3-rich-v4-mediated-spill-branch-fan-in-probe.seed.yaml](../configs/landscapes/seed/grcv3-rich-v4-mediated-spill-branch-fan-in-probe.seed.yaml)
  - topology-portability failure control
- [grcv3-rich-v4-center-coupling-probe.seed.yaml](../configs/landscapes/seed/grcv3-rich-v4-center-coupling-probe.seed.yaml)
  - tight post-spark direct control that shifts spark/collapse loci using only
    `transfer_mediation.center_coupling_classes`
- [grcv3-rich-basin-boundary-channel-probe.seed.yaml](../configs/landscapes/seed/grcv3-rich-basin-boundary-channel-probe.seed.yaml)
  - recorded non-spark collapse lane used for Iteration 51 cluster comparison

## 4. Practical Restart Advice

If restarting `GRCL-v3` after time away:

1. read [GRCL-V3-Handoff.md](./GRCL-V3-Handoff.md)
2. inspect the rich-v4 spark/split/collapse lane above
3. inspect the Iteration 38 settlement-locus evidence bundle
4. use the later trace scripts only after those two evidence anchors are clear

That order keeps the restart grounded in the strongest saved phenomenology
first, and only then moves into the narrower later semantic traces.
