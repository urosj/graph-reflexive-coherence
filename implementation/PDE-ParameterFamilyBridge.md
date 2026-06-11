# PDE Parameter Family Bridge

This document records how the PDE RC simulator can inform parameter selection for
`PyGRC` families so that discrete-family calibration does not start from scratch.

Primary PDE references used for this bridge:

- `rc-sim/simulations/active/simulation-v22-cuda.py`
- `rc-sim/configs/activity_config.py`
- `rc-sim/experiments/papers/25-ConservedIdentity-Collapse-SparkFormation.md`
- `rc-sim/experiments/papers/25A-ConservedIdentity-Collapse-SparkFormation-ImplementationChecklist.md`
- `rc-sim/experiments/papers/25G-ConservedIdentity-FixedSubstrateProjectionBoundary.md`
- `rc-sim/experiments/papers/25H-ConservedIdentity-WorkedExampleSet.md`
- `rc-sim/experiments/papers/25I-ConservedIdentity-24InterpretedThrough25.md`
- `rc-sim/experiments/papers/25J-ConservedIdentity-CollapseAsCommitment-FormalizationNote.md`
- `rc-sim/experiments/papers/25K-ConservedIdentity-SparkHierarchyReferenceCard.md`
- `rc-sim/experiments/papers/25L-ConservedIdentity-MorseToHessian-ComparisonNote.md`
- `rc-sim/experiments/papers/25M-ConservedIdentity-ClosureFunctional-PreSpec.md`
- `rc-sim/experiments/papers/25N-ConservedIdentity-TheoryDeepeningBridge.md`
- `rc-sim/experiments/papers/25O-ConservedIdentity-CounterexamplePreservationLock.md`
- `rc-sim/experiments/papers/25P-ConservedIdentity-UsageGuide.md`

## 1. Main Conclusion

Yes, the PDE program can and should be used to seed `PyGRC` parameter search.

But the correct transfer is **not**:

- direct one-to-one copying of PDE numeric coefficients into discrete-family
  coefficients.

The correct transfer is:

- **regime-family transfer**.

That means:

- take the PDE program's established operating regimes,
- identify the latent semantic axes those regimes actually represent,
- and map those axes into each discrete family's own parameter surface.

This gives `PyGRC` a better starting point than blind search while still
respecting the fact that the PDE and discrete models are not parameterized in
the same mathematical language.

After a broader pass across the `25*` arc, one stronger conclusion should be
added:

- parameter families should be tied to **canonical worked cases, discriminants,
  and retained counterexamples**, not only to broad hot-versus-quiet intuition.

## 2. Why Direct Numeric Transfer Is Unsafe

The PDE simulator and `PyGRC` do not share the same parameter geometry.

The PDE side includes many parameters that are:

- solver-level,
- discretization-level,
- regularization-level,
- or projection-specific.

Examples from `simulation-v22-cuda.py`:

- `nx`, `ny`, `dx`
- `metric_blend`
- `detk-min`
- `detk-reg-mode`
- `eig-min`
- `eig-shift-max`
- `k-iso-eps`
- snapshot/storage/render settings

Those do not map directly onto `GRCV2`/`GRCV3` constitutive parameters such as:

- `alpha`, `beta`, `gamma`, `delta`
- `eta`
- `kappa_c`
- `lambda_c`, `xi_c`, `zeta_c`
- `tau_split`
- `lambda_birth`
- `alpha_seed`
- `eps_prune`

So direct coefficient transfer would produce a false sense of precision.

## 3. What *Does* Transfer Well

What transfers well is the PDE program's regime structure.

The PDE side already expresses meaningful regime control through parameter
families such as:

- `activity`
- `closure_mode`
- `closure_softness`
- `spark_softness`
- `collapse_softness`
- `identity_cap_fraction`
- `identity_birth_gate_fraction`
- `nonlocal_mode`
- `domain_mode`
- `homeostat_mode`

These are not just random knobs. They express latent semantic axes like:

- how much identity budget is available,
- how permissive spark formation is,
- how strongly collapse damps alternatives,
- how exploratory or quiescent the system is,
- whether nonlocal or adaptive support is active.

Those axes are exactly what should seed discrete-family calibration.

## 4. Important Scope Caution From The Paper-25 Arc

The `25*` papers are useful here, but not all in the same way.

The main caution is:

- `25*` is primarily an **interpretive/control layer**, not an empirical
  authority layer.

This means:

- use `simulation-v22-cuda.py` and empirical PDE runs to identify actual regime
  settings,
- use `25*` to interpret and name those regimes safely,
- do **not** treat `25*` alone as proof that a given numeric parameter family is
  empirically validated.

In practical terms:

- the PDE simulator gives us candidate regime settings,
- the Paper-25 arc gives us disciplined language for what those regimes mean.

More specifically:

- `25H` provides canonical worked cases,
- `25I` provides the bounded `24 -> 25` reinterpretation map,
- `25J` and `25K` constrain collapse/spark language,
- `25L` and `25M` constrain what kind of precursor or closure objects are worth
  targeting,
- `25N` says deepening should be discriminant-driven rather than broad search,
- `25O` requires claim-relevant counterexamples to remain attached.

## 5. The Strongest Existing PDE Family Signal

The cleanest existing PDE family abstraction is already present in:

- `rc-sim/configs/activity_config.py`

It defines a one-dimensional regime mapping:

- `activity in [0, 1]`

which expands into:

- `identity_cap_fraction`
- `identity_birth_gate_fraction`
- `closure_softness`
- `spark_softness`
- `collapse_softness`

This is extremely valuable for `PyGRC`, because it means the PDE program already
contains an explicit compressed regime family instead of only loose ad hoc knob
searches.

At the same time, the broader `25*` arc shows that `activity` alone is not
enough. It is a good first axis, but not a complete family definition.

## 6. Recommended Bridge Model

The right bridge is to introduce a family of **latent regime axes** that are
shared conceptually across PDE and discrete implementations.

Recommended shared axes:

- `activity`
- `identity_budget`
- `birth_permissiveness`
- `spark_sensitivity`
- `collapse_damping`
- `closure_softness`
- `nonlocality`
- `adaptivity`
- `homeostasis`
- `regularization_strength`

These should be supplemented by example/discriminant tags such as:

- `robust_closability`
- `boundary_conversion`
- `persistent_holdout`
- `precursor_sensitivity`
- `commitment_sensitivity`

These axes should be treated as:

- PDE-facing interpretable control dimensions,
- and discrete-family seed dimensions.

## 7. Proposed Family Mapping Strategy

Each `PyGRC` family should map the same latent regime axes into its own native
parameters.

### 7.1 PDE Side

Example mapping:

- `activity`
  - drives `identity_cap_fraction`
  - drives `identity_birth_gate_fraction`
  - drives `closure_softness`
  - drives `spark_softness`
  - drives `collapse_softness`

### 7.2 `GRCV2` Side

Example conceptual mapping:

- `identity_budget`
  - influences `alpha_seed`
  - influences `eps_prune`
  - possibly influences target budget policy / initial mass interpretation

- `birth_permissiveness`
  - influences `lambda_birth`
  - possibly influences `alpha_seed`

- `spark_sensitivity`
  - influences `eps_spark` or `h_thr`
  - later possibly selects spark backend

- `collapse_damping`
  - influences how strongly split/birth/continuity correction suppress
    marginal identities
  - possibly influences `tau_split` and pruning sensitivity indirectly

- `closure_softness`
  - likely influences the conductance/potential side more indirectly
  - should bias search ranges for:
    - `alpha`
    - `beta`
    - `gamma`
    - `eta`
    - `kappa_c`

### 7.3 `GRCV3` Side

Example conceptual mapping:

- `spark_sensitivity`
  - influences degeneracy detection thresholds
  - influences Hessian/attractor-change trigger sensitivity

- `closure_softness`
  - influences differential-summary interpretation
  - likely influences hierarchy emergence and collapse gating

- `identity_budget`
  - influences semantic basin persistence thresholds

- `collapse_damping`
  - influences choice/collapse semantics and stabilization thresholds

### 7.4 `GRC9` Side

`GRC9` is mechanically different, but the same latent axes still make sense:

- `identity_budget`
  - maps into expansion/refinement resource limits

- `spark_sensitivity`
  - maps into valence/mechanical spark thresholds

- `closure_softness`
  - maps into row/port conductance or refinement permissiveness

So the common regime family can still exist even though the formulas differ.

### 7.5 Canonical PDE Anchors Should Seed Family Definitions

The `25H` worked-example set and the `25I` mapping memo suggest that the first
family library should be anchored to canonical case roles, not only abstract
slider positions.

Recommended canonical anchor roles:

- `cell1`
  - robust closable-continuation anchor
- `z2c@anchorb`
  - canonical precursor / readback-sensitive boundary anchor
- `s6@anchora`
  - canonical persistent holdout / counterexample anchor
- optional later:
  - `iii1`
    - unresolved/borderline anchor

This matters because `25N` explicitly recommends using canonical worked cases
before broadening into ad hoc search families.

## 8. Recommended Initial Param Families

Rather than starting with many unrelated parameter bundles, start with a small
number of cross-model families.

## Family A. Quiet / Conservative

PDE character:

- low `activity`
- low identity budget
- high collapse damping
- stricter birth gate

Discrete interpretation:

- more conservative birth
- higher spark threshold
- stronger pruning or stabilization bias
- slower split dynamics

Use when:

- testing stability,
- testing whether identities require strong support to persist,
- establishing conservative baselines.

## Family B. Balanced Baseline

PDE character:

- mid `activity`
- moderate identity budget
- moderate closure softness
- moderate collapse damping

Discrete interpretation:

- default reference family for first comparisons
- neither overly quiescent nor overly explosive

Use when:

- building the first comparable baseline across families.

Recommended canonical PDE anchor:

- `cell1`

## Family C. Hot / Exploratory

PDE character:

- high `activity`
- high identity budget
- more permissive birth
- weaker collapse damping

Discrete interpretation:

- lower spark threshold
- higher birth permissiveness
- higher split/birth activity
- greater abundance growth pressure

Use when:

- testing emergence,
- testing topology-event richness,
- comparing spark and birth backends.

## Family D. Precursor-Sensitive

PDE character:

- emphasizes soft precursor organization rather than only hard structural events
- stronger sensitivity to near-threshold softness and closure structure

Discrete interpretation:

- lower degeneracy threshold
- more sensitive spark backend
- especially relevant for `GRCV3`

Use when:

- studying precursor vs spark semantics,
- comparing Hessian-style or degeneracy-style backends.

Recommended canonical PDE anchor:

- `z2c@anchorb`

## Family E. Commitment / Collapse-Dominant

PDE character:

- stronger collapse damping
- tighter conversion from ambiguity to committed continuation

Discrete interpretation:

- stronger suppression of marginal branches
- more aggressive continuation commitment behavior

Use when:

- studying collapse / commitment semantics,
- comparing stable identity selection against exploratory regimes.

Recommended canonical PDE anchors:

- `z2c@anchorb` for positive ambiguity-to-selection pressure
- `s6@anchora` as the retained counterexample / non-conversion anchor

## Family F. Holdout / Counterexample-Locked

PDE character:

- preserves non-conversion under apparently promising local structure
- emphasizes closure discrimination rather than positive emergence

Discrete interpretation:

- intentionally conservative spark/birth settings
- used to test whether the discrete family can preserve meaningful negatives
- especially important when comparing backend variants to avoid success-only
  narratives

Use when:

- validating that stronger language is not being over-issued
- preserving claim-relevant negative cases during backend comparisons
- following the `25O` counterexample-preservation discipline

Recommended canonical PDE anchor:

- `s6@anchora`

## 9. What Should Be Recorded For Each Family

Each parameter family should be recorded at two levels.

### 9.1 Latent Family Definition

Example:

```text
family_name = "balanced_baseline"
activity = 0.50
identity_budget = medium
birth_permissiveness = medium
spark_sensitivity = medium
collapse_damping = medium
closure_softness = medium
```

### 9.2 Family-Specific Resolved Params

Then each model gets its own resolved projection:

- PDE CLI/config projection
- `GRCV2` param projection
- later `GRCV3` param projection
- later `GRC9` param projection

This is the right place to allow numeric differences while preserving the same
family identity.

Each family record should also carry:

- canonical PDE source anchors or worked examples,
- declared interpretation scope,
- expected positive cases,
- expected retained counterexamples,
- and the discriminant question the family is meant to probe.

That structure is important because `25N` and `25O` both push the program toward
discriminant-driven deepening with retained negatives, not unconstrained preset
expansion.

## 10. What Not To Do

Do not:

- copy PDE coefficients directly into discrete-family coefficients and call that
  calibrated,
- treat solver/grid regularization knobs as if they were discrete constitutive
  parameters,
- let each `PyGRC` family invent unrelated family names for the same regime idea,
- use the Paper-25 interpretive layer as if it replaced empirical PDE evidence,
- define families only by hot/cold intuition without canonical anchors or
  discriminant roles,
- or build success-only preset libraries that drop the holdout/counterexample
  side of the PDE evidence base.

## 11. Recommended Implementation Direction

The cleanest next step would be to add a small family-registry document and then
later a code-level registry.

Recommended planning artifact:

- `implementation/ParameterFamiliesPlan.md`

That note should define:

- the canonical family names,
- the latent axes,
- the PDE source settings,
- the canonical PDE worked-example anchors,
- the discriminant role of each family,
- the retained counterexample expectations where applicable,
- and the per-family projections into `GRCV2`, `GRCV3`, and `GRC9`.

Later, this could become code such as:

```python
get_param_family("balanced_baseline", target="grc_v2")
get_param_family("hot_exploratory", target="grc_v3")
get_param_family("precursor_sensitive", target="pde")
```

## 12. Final Recommendation

Yes, `PyGRC` should use the PDE program to avoid starting parameter search from
scratch.

But the bridge should be:

- **family/regime based**

not:

- **coefficient copied**.

The best current seed is the PDE-side `activity` family plus the surrounding
closure/identity controls, interpreted through the full Paper-25 control stack,
anchored to canonical worked examples and retained counterexamples, and then
projected into each discrete family's own parameter surface.
