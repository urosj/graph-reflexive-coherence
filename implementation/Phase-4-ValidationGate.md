# Phase 4 Validation Gate

This document records the detailed Iteration 10 validation gate for the executable
`GRCV2` baseline.

It exists to answer one question explicitly:

- is the current `GRCV2` baseline ready for Phase 4 closeout,
- or does it still require constitutive paper-alignment remediation?

## Validation Inputs

The gate was evaluated against:

- `implementation/Phase-4-ImplementationPlan.md`
- `implementation/Phase-0-DeterminismConventions.md`
- `implementation/Phase-0-BoundaryDecisions.md`
- `specs/grc-v2-spec.md`
- `papers/2025-12-GRC-V2.md`
- the current executable implementation in `src/pygrc/models/grc_v2.py`

Validation runs used:

```bash
./.venv/bin/python -m unittest discover -s tests -p 'test_*.py'
./.venv/bin/python tests/smoke/smoke_tests_phase4_grcv2.py
./.venv/bin/python tests/smoke/smoke_tests_phase4_grcv2_paper_alignment.py
```

Observed results at the gate:

- unit suite: `Ran 149 tests ... OK`
- executable smoke: passed
- paper-alignment smoke: passed

## Gate Findings

### 1. Executability

Status: `pass`

The model is executable and no longer a stub:

- `GRCV2.step()` runs through the explicit 14-stage loop
- `from_config(...)`, `from_state(...)`, `get_state()`, `set_state(...)`, `reset()`
  are implemented
- save/load/snapshot resume executable state rather than a stub-only state surface

### 2. Shared Runtime/Substrate Boundary

Status: `pass`

The model remains within the intended Phase 4 substrate boundary:

- weighted substrate: `WeightedGraphBackend`
- shared contracts from `src/pygrc/core/`
- shared Phase 3 serializer/save-load path
- no `GRCV3` or `GRC9` substrate logic is required to execute the family

### 3. Determinism And Persistence

Status: `pass`

The current baseline is strongly validated for deterministic execution:

- deterministic unit suite covers the executable family surface
- `tests/smoke/smoke_tests_phase4_grcv2.py` proves:
  - repeatable multi-step records
  - stable snapshots and digests
  - deterministic save/load resume
  - deterministic reset-to-baseline
- stable integer IDs and monotone backend counters are preserved through the tested
  execution and persistence paths

### 4. Loop-Level Paper Alignment

Status: `partial pass`

The stronger paper-facing smoke confirms that the executable loop now matches several
central paper claims in structure and local equations:

- canonical 14-step order
- Eq. (4) potential form
- Eq. (5) flux sign and antisymmetry
- directed-flux sink/basin extraction
- spark to soft-split progression
- birth, continuity, and budget closure inside one executable loop
- persistence/replay after nontrivial evolution

This smoke also already exposed one real loop issue during implementation:

- split progression could drive parent coherence negative on the following step
- the deterministic budget-correction path was tightened so negative coherence is
  clipped first and rebalanced afterward

So the current smoke surface is materially useful and not just confirmatory.

## Remaining Blockers

The gate still identifies constitutive blockers serious enough to prevent Phase 4
closeout.

### A. Node Tensor Eq. (1)

Status: `blocker`

The paper’s node tensor is not implemented as the actual foundational object of the
geometry stage. The current implementation uses scalar summaries and surrogates rather
than the paper’s three-term tensor construction.

Impact:

- this changes the geometry-generation story of the baseline family
- later family lift work would inherit the wrong constitutive baseline

### B. Conductance Eq. (2)

Status: `blocker`

The current conductance path is still a baseline surrogate, not the paper’s pure
exponential constitutive map.

Impact:

- the executable model is functional, but the metric-generation law is not the paper’s
  baseline law
- this is too central to defer silently if `GRCV2` is meant to be the reference family

### C. `lambda_c`, `xi_c`, `zeta_c` Roles

Status: `blocker`

These parameters are present in the executable family, but not yet wired through the
paper-defined tensor/conductance structure.

Impact:

- parameter semantics differ from the paper
- the current baseline risks baking in the wrong interpretation

### D. Abundance Semantics

Status: `blocker`

The paper’s abundance is the number of identity basins / sinks. The executable model
currently uses `abundance` for total coherence mass and exposes sink-count separately.

Impact:

- this is not just naming; it changes the meaning of a named observable used by the
  paper

### E. Birth Rule

Status: `deviation requiring explicit decision`

The executable model currently uses a deterministic baseline birth threshold rather than
the paper’s probabilistic Bernoulli rule.

Impact:

- this is a real constitutive deviation
- it may be acceptable for Phase 4 if retained explicitly and documented honestly
- but it must not remain implicit

### F. Curvature Backends

Status: `known placeholder`

The current curvature backends are still baseline surrogates rather than full discrete
Ricci implementations.

Impact:

- acceptable only if still treated as an explicit Phase 4 placeholder
- not acceptable if implied to be full paper fidelity

## Gate Decision

Decision: `continue into Iteration 11: Paper-Alignment Remediation`

Reason:

- the executable baseline is now strong on determinism, runtime behavior, persistence,
  and loop-level structure,
- but the constitutive core still differs from the paper too much to call Phase 4
  complete,
- and those differences are central enough that they should be fixed or explicitly
  bounded before later family lift work.

## Remediation Scope For Iteration 11

Iteration 11 should focus on the confirmed constitutive blockers:

1. reconcile the node tensor path against Eq. (1)
2. reconcile the conductance law against Eq. (2)
3. restore `lambda_c`, `xi_c`, and `zeta_c` to paper-defined roles
4. reconcile `abundance` / `weighted_abundance`
5. decide whether the deterministic birth rule remains an explicit baseline deviation
   or is moved closer to the paper’s probabilistic rule

The validation gate therefore does not close Phase 4. It authorizes remediation.
