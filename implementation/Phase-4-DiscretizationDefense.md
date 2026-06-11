# Phase 4 Discretization Defense

This document records the detailed rationale for the key Phase 4 discretization
choices in `GRCV2`, especially the two areas most likely to face scrutiny in a
thesis-style defense:

- the discrete tensor / metric construction,
- the curvature backend choice.

The purpose of this note is not to claim that the current implementation is the
only mathematically possible realization of `papers/2025-12-GRC-V2.md`. The
purpose is to show that:

- the current realization is deliberate,
- it is consistent with the paper's constitutive intent,
- it is defensible against plausible alternatives,
- and the alternatives have been considered explicitly rather than ignored.

Related cross-family planning note:
[`Common-BackendStrategyPlan.md`](./Common-BackendStrategyPlan.md)

## 1. Framing

### 1.1 What Phase 4 Is Claiming

Phase 4 claims that `GRCV2` is:

- the first executable reference implementation of the paper family,
- a deterministic and reproducible weighted-graph realization,
- paper-aligned on the core constitutive loop,
- and suitable as the baseline from which later families (`GRCV3`, `GRC9`,
  `GRC9V3`) can lift additional semantic or substrate richness.

Phase 4 does **not** claim that the weighted-graph discretization is uniquely
implied by the paper.

### 1.2 The Right Defense Posture

The correct defense posture is:

- the paper gives a constitutive structure,
- a discrete implementation must choose a representation of that structure,
- several choices are mathematically plausible,
- the current choice is one faithful and pragmatic realization,
- and it was selected because it preserves the paper's core semantics while
  remaining executable, deterministic, and testable in the current codebase.

The wrong defense posture would be:

- to claim that no other discretization could possibly fit the paper.

That stronger claim would be difficult to justify and is unnecessary.

## 2. Evaluation Criteria

The current implementation choices were judged against the following criteria.

### 2.1 Paper Fidelity

The discretization should preserve the paper's core constitutive claims:

- node-local tensor structure,
- edge conductance derived from coherence, gradient pressure, flux, and
  curvature,
- directed flux and sink/basin extraction,
- topology change driven by instability,
- and exact budget preservation.

### 2.2 Determinism

The implementation must remain reproducible:

- stable IDs,
- deterministic iteration order,
- deterministic snapshots,
- deterministic replay under the same state and RNG state.

### 2.3 Weighted-Graph Substrate Fit

`GRCV2` is intentionally implemented on the Phase 2 weighted graph substrate.
The discretization should therefore fit:

- node-centered coherence,
- scalar edge conductance,
- local neighborhood queries,
- and shared serialization/state machinery.

### 2.4 Inspectability

The implementation should be understandable enough to:

- test in small graphs,
- inspect in snapshots,
- and defend line by line against the source paper.

### 2.5 Extensibility

The chosen realization should leave room for later lifts:

- richer semantic state in `GRCV3`,
- richer substrate mechanics in `GRC9`,
- and later optimization without reinterpreting the mathematics.

## 3. Tensor / Metric Construction

## 3.1 Paper Requirement

The source paper gives a node tensor of the form:

```text
K_i
= λ_C C_i I
+ ξ_C Σ_j w_ij (C_j - C_i)^2 e_ij ⊗ e_ij
+ ζ_C (Σ_j J_ij)^2 I
```

and then derives the edge conductance through an exponential constitutive law
that depends on:

- mean coherence,
- coherence difference,
- prior flux,
- and discrete Ricci curvature.

This means the implementation must preserve at least four structural ideas:

1. a node-local constitutive object exists,
2. that object has three semantically distinct terms,
3. transport is still carried on edges,
4. conductance is not an arbitrary update weight but the product of a
   constitutive geometry rule.

## 3.2 Current Phase 4 Choice

The current `GRCV2` implementation uses a weighted-graph-local construction:

- per-node tensor bookkeeping is assembled from local edge directions and
  neighbor sums,
- the paper's three tensor terms are preserved explicitly,
- conductance is then computed edge-locally through the paper-facing
  exponential law,
- and the entire construction stays within the weighted graph substrate.

This choice is best described as:

- a **local weighted-graph realization of the paper tensor/metric story**.

It is not best described as:

- the uniquely canonical discretization.

## 3.3 Why This Choice Was Reasonable

This choice was selected because it satisfies all of the Phase 4 constraints at
once:

- it preserves the paper's three-term tensor structure,
- it produces a single scalar `w_ij` per edge as the baseline family requires,
- it is compatible with all three `frame_mode` settings:
  - `host_embedding`
  - `induced_local_frame`
  - `combinatorial`
- it is local enough to remain inspectable and deterministic,
- and it does not require introducing a richer cell complex before `GRCV2`
  exists as a working baseline.

In other words, it is not just mathematically defensible. It is
architecturally aligned with the stated purpose of `GRCV2`.

## 3.4 Important Limitation

The current construction should still be defended as:

- a faithful discrete realization,

not as:

- a proof that the paper mathematically forces this exact edge-local
  construction and no other.

That distinction matters in a thesis defense.

## 3.5 Plausible Alternatives

The main plausible alternatives are listed below.

### A. Symmetric Edge-Tensor Projection

Representative idea:

```text
w_ij derived from e_ij^T ((K_i + K_j) / 2) e_ij
```

This approach would:

- build node tensors first,
- average or otherwise symmetrize endpoint tensors,
- then project the result onto the edge direction.

#### Strengths

- cleaner geometric story,
- more direct use of the node tensor as a constitutive object,
- strong mathematical defensibility in a thesis context,
- potentially clearer connection between `K_i` and actual transport direction.

#### Weaknesses

- still needs a concrete rule for `e_ij` in graph-native modes,
- may require more careful handling of frame-induced asymmetry,
- adds more tensor-to-edge machinery than the current baseline.

#### Assessment

This is the **strongest serious alternative** to the current Phase 4 choice.
If the thesis emphasis were more geometric and less implementation-first, this
option might be preferable.

### B. Variational / Dirichlet-Energy Discretization

Representative idea:

- define a discrete energy functional,
- derive conductances or fluxes from the discrete energy operator,
- let the metric enter indirectly through the energy rather than directly
  through an explicit tensor-to-edge step.

#### Strengths

- strong ties to graph PDE and variational analysis,
- often easier to analyze in stability arguments,
- can produce a cleaner mathematical defense for the update equations.

#### Weaknesses

- less direct alignment with the paper's explicit tensor statement,
- risks shifting the implementation away from the paper's language into a
  derived formalism,
- can obscure the semantics of the named constitutive parameters.

#### Assessment

This would be a valid realization of the same broad theory family, but for
Phase 4 it would weaken the direct paper-to-code correspondence.

### C. Discrete Exterior Calculus / Finite-Volume Realization

Representative idea:

- attach quantities to primal edges and dual cells,
- compute flux using a more geometric primal/dual structure,
- derive conductance and transport through a richer geometric mesh model.

#### Strengths

- strongest geometric fidelity,
- strongest claim to “true” spatial discretization,
- natural home for anisotropy and flux conservation.

#### Weaknesses

- much heavier machinery than a weighted graph,
- poor fit for the declared scope of `GRCV2`,
- would likely force a substrate much closer to `GRC9` or beyond,
- would make Phase 4 larger and less inspectable.

#### Assessment

This may be the most geometrically principled route in the abstract, but it is
not the best fit for the **baseline weighted-graph family**.

### D. Pure Edge Law Without Meaningful Node Tensor

Representative idea:

- skip a real `K_i`,
- compute `w_ij` from edge-local heuristics only.

#### Strengths

- simplest implementation,
- cheapest runtime.

#### Weaknesses

- weak paper fidelity,
- weak thesis defensibility,
- wrong inheritance baseline for later families.

#### Assessment

This was intentionally rejected for Phase 4.

## 3.6 Overall Judgment On The Metric Choice

The current Phase 4 tensor/metric construction should be defended as:

- not uniquely forced,
- but a strong and reasonable reference realization.

If an examiner asks whether another choice could also fit the paper, the right
answer is:

- **yes**,
- especially a symmetric edge-tensor projection,
- but the current choice was selected because it best balances paper fidelity,
  weighted-graph fit, determinism, inspectability, and implementation scope.

## 4. Curvature Backends

## 4.1 Paper Requirement

The paper names discrete Ricci curvature and allows a graph-discrete reading
such as:

- Ollivier-Ricci,
- Forman-Ricci.

That creates two obligations:

1. the implementation must not silently pretend curvature is absent,
2. if it exposes `curvature_backend="forman"` or `"ollivier"`, those names
   should refer to real backends rather than mislabeled placeholders.

## 4.2 Current Phase 4 Choice

Phase 4 now implements three explicit modes:

- `none`
- `forman`
- `ollivier`

The key design choice is that both `forman` and `ollivier` are implemented
in-house on the weighted graph substrate, rather than delegated to an external
graph library or left as stubs.

This was the correct choice for Phase 4 because it preserves:

- determinism,
- backend ownership,
- serializer compatibility,
- and paper-facing honesty.

## 4.3 Why Both Backends Were Worth Keeping

The two backends serve different purposes.

### Forman-Ricci

Best defended as:

- the computationally pragmatic backend.

#### Strengths

- local,
- inexpensive,
- deterministic,
- scales better,
- easier to reason about on larger graphs,
- suitable as a default or baseline backend in many practical runs.

#### Weaknesses

- more combinatorial than transport-geometric,
- may not capture metric transport structure as faithfully as Ollivier.

### Ollivier-Ricci

Best defended as:

- the more geometrically faithful transport backend.

#### Strengths

- closer to transport-based geometric intuition,
- better theoretical story when curvature is supposed to modulate
  conductance through neighborhood transport structure,
- more directly aligned with a metric interpretation.

#### Weaknesses

- more expensive,
- more sensitive to implementation details,
- more likely to become the bottleneck on larger graphs.

## 4.4 Plausible Alternatives

### A. Forman Only

This would reduce complexity and improve runtime.

#### Why It Was Not Chosen

Because the paper explicitly names a transport-geometric curvature option, and
removing Ollivier would weaken the geometric defense of the implementation.

### B. Ollivier Only

This would maximize geometric fidelity.

#### Why It Was Not Chosen

Because Phase 4 also needs a practical deterministic baseline that remains
cheap enough to use as the first executable family.

### C. Lin-Lu-Yau Or Lazy Ollivier Variants

This family of variants may provide:

- better numerical stability on irregular graphs,
- better scaling/performance tradeoffs than plain Ollivier,
- a potentially stronger practical backend for future phases.

#### Assessment

This is the strongest future refinement candidate if later evaluation shows that
plain Ollivier is too expensive or too fragile on larger graphs.

It is not clearly the right Phase 4 baseline because:

- it adds another design layer,
- it is not the most direct reading of the paper's named curvature choices,
- and Phase 4 already needed to close the placeholder gap without exploding the
  implementation surface further.

### D. No Explicit Curvature In `GRCV2`

This would make `GRCV2` simpler.

#### Why It Was Rejected

Because the paper includes discrete Ricci curvature explicitly in the
constitutive story. Eliminating it from the baseline family would weaken paper
alignment too much.

## 4.5 Overall Judgment On The Curvature Choice

The current choice to support both:

- `forman`
- `ollivier`

is the right Phase 4 compromise:

- Forman covers the pragmatic baseline,
- Ollivier covers the stronger geometric interpretation.

The main caveat is not conceptual but empirical:

- larger and less regular graphs may still reveal meaningful differences in
  stability, sensitivity, or runtime cost between the two.

That is a reason for future benchmarking, not a reason to treat the current
choice as wrong.

## 5. Would Another Choice Fit Better?

The most honest answer is:

- **possibly, depending on what “better” means**.

### 5.1 If “Better” Means Stronger Geometric Defense

Then the strongest alternatives are:

- symmetric edge-tensor projection for the metric,
- Ollivier or a lazy-transport variant for curvature.

### 5.2 If “Better” Means Faster And Easier To Maintain

Then the strongest alternatives are:

- keep the current tensor realization,
- favor Forman as the practical default,
- treat Ollivier as the more expensive comparison backend.

### 5.3 If “Better” Means Better Fit To The Purpose Of `GRCV2`

Then the current design remains strong:

- weighted graph,
- explicit node tensor bookkeeping,
- scalar conductance edge law,
- real curvature backends,
- deterministic replay,
- and clean inheritance for later families.

That is why the current implementation is best defended as:

- **not uniquely canonical, but well chosen for the role `GRCV2` is supposed
  to play**.

## 6. Thesis-Defense Position

If challenged directly, the defense should be:

1. The paper does not uniquely determine one graph discretization.
2. A discrete implementation must therefore choose a realization.
3. The current realization was selected against explicit engineering and
   semantic criteria:
   - paper fidelity,
   - weighted-substrate fit,
   - determinism,
   - inspectability,
   - and extensibility.
4. Alternative realizations were considered and remain plausible.
5. The strongest near-neighbor alternative is a symmetric edge-tensor
   projection.
6. The strongest curvature refinement candidate is a lazy-transport
   Ollivier-family variant if future benchmarking warrants it.

This framing is strong because it is both rigorous and honest.

## 7. Likely Examiner Questions

### Q1. Is the current tensor/metric discretization uniquely justified by the paper?

Recommended answer:

- No.
- It is one faithful weighted-graph realization of the paper's constitutive
  structure.
- A symmetric edge-tensor projection would also be a plausible realization.
- The current choice was selected because it best fits the Phase 4 goals of
  executability, determinism, and inspectability while preserving the paper's
  three-term tensor structure and exponential conductance law.

### Q2. Why not use a more geometric method such as DEC or finite volume?

Recommended answer:

- Because `GRCV2` is the baseline weighted-graph family.
- A richer geometric substrate would be defensible in principle, but it would
  exceed the intended complexity and likely blur the boundary between `GRCV2`
  and the more structured later families.

### Q3. Why keep both Forman and Ollivier?

Recommended answer:

- Because they serve different roles:
  - Forman is the practical local baseline,
  - Ollivier is the stronger transport-geometric backend.
- Keeping both makes the implementation more honest and more useful for later
  comparison.

### Q4. Could another curvature backend be better?

Recommended answer:

- Yes.
- A lazy-Ollivier or Lin-Lu-Yau-style variant is a plausible future candidate
  if larger-graph experiments show that plain Ollivier is too costly or too
  sensitive.
- That is a benchmarking question, not a reason to treat the current choice as
  incorrect.

## 8. Recommended Future Benchmarking

The following benchmarking work would strengthen the defense further:

### 8.1 Metric Realization Comparison

Compare:

- current local weighted-graph realization,
- symmetric edge-tensor projection.

Measure:

- conductance distribution,
- sink/basin stability,
- spark trigger location and frequency,
- abundance trajectories,
- sensitivity to parameter changes.

### 8.2 Curvature Backend Comparison

Compare:

- `none`
- `forman`
- `ollivier`
- possible lazy-Ollivier / Lin-Lu-Yau variant later

Measure:

- runtime cost,
- determinism and replay stability,
- sensitivity on irregular graphs,
- conductance modulation behavior,
- downstream topology-event effects.

## 9. Final Position

The current `GRCV2` discretization should therefore be defended as:

- faithful to the paper's constitutive intent,
- not uniquely forced by the paper,
- but well chosen for the role of the baseline executable family,
- and strong enough to support later semantic and mechanical lifts.

That is the strongest credible claim.
