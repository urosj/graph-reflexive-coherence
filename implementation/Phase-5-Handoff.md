# Phase 5 Handoff

Phase 5 is now complete. Treat this file as the historical start-of-phase
handoff, and use [GRCV3-Closeout.md](./GRCV3-Closeout.md) as the authoritative
end-of-phase baseline statement for any later work that inherits `GRCV3`.

This document is the handoff from Phase 4 (`GRCV2`) into Phase 5 (`GRCV3`).

Its purpose is to make Phase 5 start from the right implementation context rather
than from scattered notes, memory, or implicit assumptions.

## 1. Read First

Before writing Phase 5 code, read these documents in this order:

1. [`../specs/grc-v3-spec.md`](../specs/grc-v3-spec.md)
2. [`Phase-5-ImplementationPlan.md`](./Phase-5-ImplementationPlan.md)
3. [`Phase-5-ImplementationChecklist.md`](./Phase-5-ImplementationChecklist.md)
4. [`Phase-5-EquationMap.md`](./Phase-5-EquationMap.md)
5. [`Common-BackendStrategyPlan.md`](./Common-BackendStrategyPlan.md)
6. [`GRCL-Landscape-DSL-TranslationGuide.md`](./GRCL-Landscape-DSL-TranslationGuide.md)
7. [`LandscapeSeedSchema.md`](./LandscapeSeedSchema.md)
8. [`PDELandscapeToSeedTranslation.md`](./PDELandscapeToSeedTranslation.md)
9. [`PDEToGRCLMathematicalEquivalenceChecklist.md`](./PDEToGRCLMathematicalEquivalenceChecklist.md)
10. [`Phase-L-ImplementationPlan.md`](./Phase-L-ImplementationPlan.md)
11. [`Phase-L-ImplementationChecklist.md`](./Phase-L-ImplementationChecklist.md)
12. [`Phase-L-ProjectorBoundary.md`](./Phase-L-ProjectorBoundary.md)
13. [`Phase-4-Retrospective.md`](./Phase-4-Retrospective.md)
14. [`Phase-4-DiscretizationDefense.md`](./Phase-4-DiscretizationDefense.md)
15. [`GRCV2-Closeout.md`](./GRCV2-Closeout.md)
16. [`Phase-4-ImplementationPlan.md`](./Phase-4-ImplementationPlan.md)
17. [`Phase-4-ImplementationChecklist.md`](./Phase-4-ImplementationChecklist.md)

These together provide:

- the Phase 5 contract,
- the Phase 5 execution order,
- the paper-to-code operator map,
- the landscape bridge contract that later seed/projector work must reuse,
- the common backend-selection architecture,
- the explicit statement that `GRCV2` is now a closed baseline rather than an
  open provisional family,
- the main failure modes from Phase 4,
- and the final state of the executable baseline family that `GRCV3` will lift.

## 2. What Phase 4 Now Guarantees

`GRCV2` is now the executable reference baseline with:

- a working deterministic weighted-graph family,
- explicit 14-step loop structure,
- stable snapshot and replay behavior,
- Bernoulli birth with deterministic replay through `rng_seed` / `rng_state`,
- real in-house `forman` and `ollivier` curvature backends,
- paper-aligned tensor/metric/potential/flux/sink/basin baseline,
- and a full persistence/test/smoke surface.

This means Phase 5 does **not** need to solve:

- first executable family shape,
- first persistence story,
- first determinism story,
- or first backend-selection pressure.

Those lessons already exist and must be reused.

## 3. What Phase 5 Must Reuse

Phase 5 should explicitly inherit:

- the shared core contracts from `src/pygrc/core/`
- the weighted substrate from Phase 2
- the shared serializer and digest layer from Phase 3
- the backend-selection direction from `Common-BackendStrategyPlan.md`
- the process lessons from `Phase-4-Retrospective.md`

Phase 5 should **not** silently reinvent:

- backend naming,
- backend serialization,
- deterministic replay semantics,
- or paper-facing validation structure.

## 4. What Phase 5 Must Not Silently Reinterpret

`GRCV3` is a semantic lift, not a license to obscure the baseline.

Phase 5 must not silently reinterpret:

- `GRCV2` observables that remain shared,
- shared snapshot semantics,
- backend identity and params hashing,
- weighted-substrate identity/order guarantees,
- or the meaning of common capability names.

If `GRCV3` extends a concept, that extension must be explicit.

## 5. Main Risks To Avoid

Phase 4 exposed several process risks that must be treated as known traps.

## 5.1 Theory Drift Behind Passing Tests

Passing tests are not enough if the tests only verify implemented behavior.

Phase 5 must add theory-facing checks early for:

- gradient construction,
- Hessian construction,
- Hessian sign handling,
- basin attribute semantics,
- hierarchy updates,
- and collapse/choice semantics.

## 5.2 Inline Backend Accumulation

Do not let `src/pygrc/models/grc_v3.py` become one giant branch-heavy file that
contains every backend variant inline.

Phase 5 should use the common backend-strategy direction from the start.

## 5.3 Placeholder Names That Sound Final

Do not publish names that imply complete implementations if the backend is still
a placeholder.

If a backend name is public:

- it should refer to a real implementation,
- or the placeholder status must remain explicit in plan, checklist, code, and
  tests.

## 5.4 Semantic Name Drift

Do not overload paper terms in:

- observables,
- state fields,
- event names,
- or hierarchy labels.

If a quantity differs from the paper term, rename it rather than silently
borrowing the paper's name.

## 5.5 Late Validation Only

Do not wait until the family feels nearly complete before checking whether the
central paper semantics still hold.

Phase 5 should have:

- theory-facing tests early,
- and an earlier constitutive review before final closeout.

## 6. Suggested Phase 5 Backend Categories

Phase 5 should likely define backend categories such as:

- `geometry`
- `differential_summary`
- `spark`
- `metric`
- `hierarchy_update`

These names should be aligned with `Common-BackendStrategyPlan.md`.

The common layer should own:

- category vocabulary,
- selection representation,
- serialization rules,
- validation pattern.

The family layer should own:

- actual gradient/Hessian formulas,
- hierarchy update logic,
- spark semantics,
- and any `GRCV3`-specific state transformations.

## 7. First Phase 5 Actions

The Phase 5 setup documents now exist. The next work should continue from them
in this order:

1. use `Phase-5-ImplementationPlan.md` as the authoritative execution plan
2. use `Phase-5-ImplementationChecklist.md` as the iteration tracker
3. use `Phase-5-EquationMap.md` as the paper-to-code anchor
4. keep the `GRCV3` backend categories and public names fixed unless a real
   contradiction is found
5. define theory-facing test classes before implementation expands
6. define an earlier mid-phase validation gate for constitutive review

This ordering matters:

- plan first,
- checklist second,
- equation map third,
- then code.

## 8. What The Equation Map Should Cover

Before substantial implementation begins, `Phase-5-EquationMap.md` should answer:

- where the gradient backend lives,
- where the Hessian backend lives,
- how `induced_local_frame` is realized in `GRCV3`,
- how signed Hessian state is fixed and serialized,
- where basin attributes are materialized,
- where attractor-count change is computed,
- where hierarchy updates happen,
- how choice/collapse state is represented,
- how those pieces are tested directly.

This document should exist before the implementation becomes large.

## 9. What The Phase 5 Checklist Should Enforce

`Phase-5-ImplementationChecklist.md` should make these explicit:

- backend-selection architecture adopted before backend proliferation
- direct paper-to-code checks for central `GRCV3` mathematics
- serialization of backend selections and backend params
- deterministic replay for any stochastic semantics
- an explicit mid-phase constitutive validation step
- a final paper-facing validation gate before closeout

## 10. Final Handoff Statement

Phase 5 should start from a stronger position than Phase 4 did.

Because of Phase 4, the project already knows:

- how theory drift can happen,
- how passing tests can still miss constitutive mismatches,
- how important explicit backend strategy is,
- and how valuable a paper-facing validation gate is.

If Phase 5 uses those lessons deliberately, `GRCV3` should develop:

- faster,
- with less semantic drift,
- with cleaner backend boundaries,
- and with fewer late-stage corrections.

## 11. Closeout Link

Phase 5 did complete with those goals materially realized.

For the closed baseline, read:

1. [GRCV3-Closeout.md](./GRCV3-Closeout.md)
2. [Phase-5-StepLoop.md](./Phase-5-StepLoop.md)
3. [Phase-5-ConstitutiveReview.md](./Phase-5-ConstitutiveReview.md)
4. [Phase-5-RepresentativeRuntime.md](./Phase-5-RepresentativeRuntime.md)
