# Common Backend Strategy Plan

This document defines the recommended architecture for backend and strategy
selection across the `PyGRC` family implementations.

It exists because `GRCV2` already demonstrates that some important model choices
are not single fixed formulas, but selected realizations inside a family:

- curvature backend,
- geometry / frame interpretation,
- spark trigger backend,
- birth rule,
- split distribution rule,
- and later likely metric, tensor, and differential-summary backends.

The purpose of this note is to prevent each family from solving the same problem
independently in slightly incompatible ways.

## 1. Goal

The goal is to create a **shared backend-selection architecture** that:

- is visible at the common layer,
- serializes cleanly,
- supports deterministic replay,
- and still leaves the actual mathematical backend implementations mostly at the
  family layer.

This is not a plan to move all family math into one universal core engine.

## 2. Problem Statement

`GRCV2` already shows the tension clearly:

- some variation points are naturally configurable,
- but the current implementation still carries them as large internal branches in
  one model class,
- and future families (`GRCV3`, `GRC9`, `GRC9V3`) will face similar variation
  points with different state and topology assumptions.

If each family solves this independently, the likely result is:

- duplicated dispatch logic,
- inconsistent naming,
- inconsistent serialization,
- difficulty comparing backends across families,
- and higher risk that “same backend name” means different things in different
  families.

## 3. Principle

The correct architecture is:

- **common layer owns strategy contracts and naming**
- **family layer owns strategy implementations**

That means the common layer should define:

- what a backend selection is,
- how it is named,
- how it is resolved from params,
- how it is serialized,
- how it is validated,
- and how it is compared in tests.

But the family layer should still define:

- the actual formulas,
- the required state assumptions,
- the required topology assumptions,
- and the backend-specific semantics.

## 4. Why Not One Universal Math Layer?

Because the families are not the same.

### `GRCV2`

- weighted graph substrate
- scalar edge conductance
- minimal node state

### `GRCV3`

- weighted graph substrate
- richer semantic state
- differential summaries
- hierarchy and basin attributes

### `GRC9`

- nine-slot mechanical substrate
- port occupancy and rewiring
- local constitutive chart

### `GRC9V3`

- hybrid of semantic and mechanical complexity

These families may share backend **categories**, but they will often not share
the exact backend **implementation**.

So a universal math layer would likely create one of two bad outcomes:

- an abstraction too weak to help,
- or an abstraction so generic that it hides the real mathematical differences.

## 5. What Should Be Common

The following pieces should move or be formalized at the common layer.

## 5.1 Backend Category Vocabulary

The core layer should define stable category names, such as:

- `geometry`
- `metric`
- `curvature`
- `spark`
- `birth`
- `split`
- `boundary`
- later possibly:
  - `differential_summary`
  - `causal`
  - `coarse_graining`

These names should become part of the common implementation vocabulary.

## 5.2 Shared Strategy Contract Pattern

The core layer should define the pattern by which a model advertises and uses a
backend selection.

At minimum, each backend family should have:

- a category name,
- a backend name,
- a backend parameter payload,
- a deterministic identity,
- serialization support.

Representative common-layer shape:

```python
@dataclass(frozen=True)
class BackendSelection:
    category: str
    name: str
    params: Mapping[str, Any]
```

This does not force every backend to share the same call signature. It only
standardizes how the choice is represented.

## 5.3 Resolution And Validation Rules

The common layer should define:

- how backend selections are resolved from `GRCParams`,
- how unknown backend names are rejected,
- how backend params are normalized,
- how backend identity participates in deterministic replay.

Families should still decide:

- which categories they support,
- which backend names are legal in those categories,
- which backend params are required.

## 5.4 Serialization Rules

The common layer should standardize:

- where backend choices appear in snapshot metadata or dynamics state,
- how backend params are preserved,
- how backend identity affects `params_hash`,
- how replay/load verifies compatibility.

This matters because backend comparison only means something if the selected
backend is reproducible from the stored state.

## 5.5 Comparison/Test Discipline

The common layer should also define the expected testing pattern for backend
variation:

- same initial state,
- same params except for backend selection,
- same RNG seed/state where relevant,
- compare:
  - observables,
  - event stream,
  - snapshot digests,
  - runtime cost,
  - invariant preservation.

This does not have to be a code API first. It can start as a planning/testing
discipline, then become helper utilities later.

## 6. What Should Stay Family-Specific

The following should remain with the family implementation unless real reuse
emerges.

## 6.1 Formulas

Examples:

- `GRCV2` edge conductance law
- `GRCV3` differential summary construction
- `GRC9` port-mechanical refinement logic

Same category, different mathematics.

## 6.2 State Assumptions

Examples:

- `GRCV2` curvature sees weighted graph neighborhoods
- `GRCV3` may require richer node summaries
- `GRC9` may require port-local incidence structure

## 6.3 Event Semantics

Examples:

- `GRCV2` spark -> soft split
- `GRCV3` spark may carry richer basin-state implications
- `GRC9` may map instability into expansion/refinement differently

## 6.4 Runtime Helpers

Families may still have different internal helper shapes even if they expose the
same backend category names.

That is acceptable. Shared naming does not require shared call graphs.

## 7. Recommended Layering

## 7.1 Core Layer

Recommended future files:

- `src/pygrc/core/backends.py`
- optionally `src/pygrc/core/backend_types.py`

Responsibilities:

- backend category vocabulary
- selection datatypes
- common validation/resolution helpers
- serialization helpers for backend selections

## 7.2 Family Layer

Recommended future files:

- `src/pygrc/models/grc_v2_backends.py`
- `src/pygrc/models/grc_v3_backends.py`
- `src/pygrc/models/grc_9_backends.py`
- `src/pygrc/models/grc_9_v3_backends.py`

Responsibilities:

- concrete backend implementations
- family-specific dispatch
- family-specific backend validation
- family-specific backend tests

## 7.3 Model Class Layer

The model class should:

- resolve selected backends once,
- orchestrate them,
- store the active backend selections in a testable/serializable way,
- and avoid carrying every backend implementation inline as large internal
  branches forever.

## 8. Example Backend Categories

The table below shows what likely belongs in this architecture.

| Category | Common? | Family-specific implementation? | Notes |
| --- | --- | --- | --- |
| `curvature` | Yes | Yes | Shared naming, family-specific math |
| `spark` | Yes | Yes | Shared selection, family-specific trigger details |
| `birth` | Yes | Yes | Shared category, likely different family semantics |
| `split` | Yes | Yes | Shared category, family-specific topology changes |
| `geometry` | Yes | Yes | Especially important once alternatives multiply |
| `metric` | Yes | Yes | Good comparison target across realizations |
| `boundary` | Yes | Yes | Shared naming around `prune`, `barrier`, `ghost` |
| `differential_summary` | Yes later | Yes | More relevant in `GRCV3` |

## 9. `GRCV2` Readiness Assessment

`GRCV2` is already partially ready for this architecture.

### Already Good

- config-driven backend names exist for:
  - `curvature_backend`
  - `frame_mode`
  - `spark_backend`
  - `split_distribution_mode`
- RNG state/seed already supports deterministic stochastic replay
- snapshots already preserve the relevant constitutive selections

### Not Yet Ideal

- backend logic is still mostly implemented as branches inside
  `src/pygrc/models/grc_v2.py`
- there is not yet a shared backend selection object
- adding a new backend still requires editing model internals
- tests are organized by behavior, not yet by a shared backend comparison matrix

So `GRCV2` is a good starting point, but not yet the final architecture.

## 10. Risks If We Do Nothing

If we do not formalize this before `GRCV3`, the likely outcome is:

- `GRCV3` reintroduces its own private backend naming,
- `GRC9` does the same,
- backend comparison becomes family-specific and ad hoc,
- later commonization becomes harder because names and assumptions have already
  drifted.

## 11. Recommended Next Steps

The next steps should be:

1. add a small common-layer backend selection contract
2. keep actual backend formulas in family-local modules
3. refactor `GRCV2` to use the family-local backend module pattern
4. make `GRCV3` adopt the same pattern from the start
5. only lift a concrete backend implementation upward if at least two families
   truly share the same semantics, not just the same label

## 12. Non-Goals

This plan does **not** recommend:

- forcing all families onto one universal math backend API,
- moving family formulas into `src/pygrc/core/`,
- or blocking Phase 5 until a perfect backend framework exists.

The goal is to establish the right reusable architecture early, not to freeze
all future family work behind a large refactor.

## 13. Final Recommendation

Yes, backend strategy should be addressed at a higher level.

But the correct higher level is:

- shared selection architecture,
- not shared mathematical implementation.

That gives the project:

- common language,
- common reproducibility rules,
- common comparison discipline,
- while preserving the freedom each family needs to realize its own equations
  honestly.
