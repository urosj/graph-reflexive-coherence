# GRCL-v3 Handoff

This document is the restart handoff for the continuing `GRCL-v3` arc after
the current `GRCV3` closeout work.

Its purpose is to make three things explicit:

- what the post-closeout `GRCL-v3` work already settled cleanly,
- what should **not** be reopened casually,
- and how to resume the next `GRCL-v3` step without mixing runtime,
  translation, and phenomenology questions again.

This is not the `GRCL-v3` plan itself.
Treat it as the clean re-entry note for later continuation.

## 1. Read First

Before resuming `GRCL-v3`, read these documents in order:

1. [GRCV3-Retrospective.md](./GRCV3-Retrospective.md)
2. [GRCL-V3-ImplementationPlan.md](./GRCL-V3-ImplementationPlan.md)
3. [GRCL-V3-Vocabulary.md](./GRCL-V3-Vocabulary.md)
4. [GRCL-V3-LoweringArchitectureDecision.md](./GRCL-V3-LoweringArchitectureDecision.md)
5. [GRCL-V3-FamilyNativeLoweringRefactorPlan.md](./GRCL-V3-FamilyNativeLoweringRefactorPlan.md)
6. [GRCL-V3-ImplementationChecklist.md](./GRCL-V3-ImplementationChecklist.md)

Together these capture:

- the direct-translation rule for rich `GRCV3` source semantics,
- the later `transfer_mediation` and `settlement_regime` discoveries,
- the current closure boundary for those slices,
- and the planning constraints on any next family.

## 2. What `GRCL-v3` Is Now For

The continuing `GRCL-v3` arc should not be read as unfinished baseline
`GRCV3` implementation.

At this point it is a source-language and translation-boundary program:

- how should raw `GRCV3` geometry be named truthfully?
- which distinctions are genuinely source-side and behavior-bearing?
- which ones are only traced runtime consequences of already-authorable
  structure?

The right mental model is:

- `GRCL-v3` is not a solved-state cache
- it is not a way to prescribe spark outcomes directly
- it is a family-specific language for authoring the structural conditions
  under which `GRCV3` phenomenology becomes available

## 2.1 Current Scope Note

The current closure and restart guidance is intentionally **spindle-lane
specific**.

That means:

- the language results recorded here are strong for the currently explored
  spindle spark/split/collapse side-quest
- but they should not yet be generalized automatically to every later
  `GRCV3` motif family or every future `GRCL-v3` source lane

What should generalize safely:

- the direct-translation discipline
- the authorability-before-promotion rule
- the need to separate runtime trace signatures from source-language
  commitments

What should stay lane-local until re-shown elsewhere:

- the exact productive regime split inside `transfer_mediation`
- the exact current `settlement_regime` matrix
- and the closure claim that descendant secondary support is already fully
  authored by existing `transfer_mediation` structure

## 3. What Is Cleanly Closed

### 3.1 `transfer_mediation`

The current spindle side-quest is cleanly characterized enough that
`transfer_mediation` should be treated as close to exhausted.

What is established:

- `path_topology` is behavior-bearing
- `spill_branch_mode` is behavior-bearing
- `lateral_spill_policy` is behavior-bearing
- two productive settlement-locus regimes were made visible:
  - carrier-site regime
  - path-node regime with later migration onto split children
- the productive path-node regime is topology-specific in the current lane:
  - `single_intermediate` works
  - `fan_in` does not

What to preserve:

- do not reopen `transfer_mediation` just because more variants are possible
- reopen it only if a genuinely missing source-side distinction is named more
  directly than opening a new family

### 3.2 `settlement_regime`

`settlement_regime` is also cleanly closed for the current spindle side-quest.

What is established:

- the executable family is useful for:
  - `initial_locus_class`
  - `split_inheritance_mode`
- the regime space is not a free Cartesian product
- only `path_node + split_child_inheriting` currently repeats
- the other productive combinations are one-shot

What was tested and rejected as a new field basis:

- descendant secondary support class was traced carefully
- secondary `basin_load_carrier` support is necessary for the repeating lane
- but Iteration 49 showed that this condition is already authorable through
  existing `transfer_mediation` structure

Closure consequence:

- do **not** add a new `settlement_regime` field for descendant secondary
  support class on the basis of the current spindle lane
- reopen the family only if a later lane exposes a genuine translation gap
  that existing structure still cannot author

## 4. What Must Stay Disciplined

When `GRCL-v3` resumes, preserve these rules:

- one semantic boundary at a time
- always keep a direct control when behavior is being compared
- prefer authorability tests before promoting a new source-side field
- treat traced runtime necessity as insufficient by itself for vocabulary
  promotion
- keep the forbidden solved-state boundary explicit

The architectural question is always:

- is this a source-side distinction the author can declare honestly before the
  run?

If the answer is not yet clear, the next step is usually:

- trace more precisely,
- or test whether existing vocabulary already authors the condition,
- not “add one more field.”

## 5. Best Current Hint For The Next Step

The collapse-side follow-on proposed in this handoff has now been executed
through Iterations 50 to 55 and can be treated as closed for the current
planning window.

What that collapse arc established is:

- collapse-capable lanes are plural
- collapse behavior is heterogeneous across pre-spark and post-spark regimes
- the post-collapse shift away from an initial sink is best read as
  geometry-mediated rerouting of preference
- and the investigated distinctions still close inside existing authored
  structure, especially `transfer_mediation.center_coupling_classes`

So the current restart preference is now:

- keep `transfer_mediation` closed by default for the spindle lane
- keep `settlement_regime` closed by default for the spindle lane
- treat collapse exploration as materially done unless a later artifact exposes
  a genuinely new source-side distinction

That means the next step should no longer be “run the collapse audit.”
That work is already part of the current record.

The previously-recorded interior-shaping follow-on remains the most plausible
later structural direction:

- `primitive.extensions.grcv3.interior_geometry`
  - `probe_mode`
  - `support_profile`
  - `attachment_isolation`
  - `interior_clearance_class`
  - `support_connectivity`
  - `support_role_groups`

But it should now be treated as a later structural hint, not as the default
immediate next step if another narrower source-side question becomes more
compelling first.

## 6. Practical Restart Rule

If resuming after time away, do this first:

1. read the six documents listed above
2. confirm that `transfer_mediation` and `settlement_regime` are still closed
   for the intended lane
3. confirm that the collapse-side closure from Iterations 50 through 55 still
   covers the intended lane
4. decide whether the next honest question is a new source-side family or a
   narrower authoring question outside the closed collapse arc
5. if a new family is still needed after that, state it in source-language
   terms
6. explain why existing vocabulary is insufficient before adding any new field

If those steps are skipped, the project is likely to drift back into
runtime-trace labeling instead of disciplined source-language growth.
