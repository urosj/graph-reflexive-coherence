# GRCv4 Exploratory Side Tool User Scenarios

**Date:** 2026-08-28
**Status:** Design coverage validated; Iterations 1-5 accepted; Iteration 6 authorized
**Plan:** [GRCV4ExploratorySideToolImplementationPlan.md](./GRCV4ExploratorySideToolImplementationPlan.md)
**Checklist:** [GRCV4ExploratorySideToolImplementationChecklist.md](./GRCV4ExploratorySideToolImplementationChecklist.md)

## Purpose

This record defines the implementation-facing user and validation scenarios for
the exploratory side tool. It tests whether the plan describes a tool that can
actually be consumed, rather than only a collection of derived artifacts.

The scenarios are not scientific evidence and do not extend accepted source
authority. They exercise only:

```text
forensic_evidence_trace
speculative_structural_counterfactual
```

There are 35 scenarios:

```text
forensic reconstruction       9
navigational exploration      6
structural counterfactuals     9
adversarial/fail-closed        7
onboarding/orientation         4
total                         35
```

## Common UX Contract

- Every forensic trace terminates at committed source IDs and digests.
- Every speculative result is visibly non-proof and stops at the evidence
  frontier.
- The browser reads Python-generated projections and ripple rows; it does not
  compute scientific consequences.
- Forward verification obligations are shown as future work, never as support.
- Historical predecessor blockers remain history and do not masquerade as
  current unresolved debt.
- Dependency reach is not importance, severity, or candidate ranking.
- Source and speculative modes remain distinct without relying on color alone.
- The accepted bundle is presented as a versioned snapshot, not the final state
  of the constitutive investigation; newly observed source is flagged without
  being interpreted or inserted into the graph.

## A. Forensic Reconstruction

### F1. Trace the top normative claim

**Surface:** web triangulation or `reconstruction_path`

Select `D10-CL-N-001`. Show its supporting parent objects, equation/contracts,
accepted `evidence_refs` (`D7G-v2`, `GTRS-COMP`, and D9), and transformed
`bearing_debt_ids`/`debt_edges`. Every path ends at a source identity and exact
edge reference.

**Output:** `forensic_evidence_trace`

### F2. Walk one debt from pressure to transformation

**Surface:** `debt_lifecycle`

Select `GTRS-COMP-DEBT-MATCHED-RUNTIME-DISCRIMINATION`. Show its D9 predecessor
state, D10 transformation verb, supported and blocked claims, activation
condition, and forward verification-obligation routing. Do not describe a
routed or narrowed transformation as simple deletion.

**Output:** `forensic_evidence_trace`

### F3. Explain one gate act

**Surface:** `gate_act` and `gate_contribution`

Select `GRC9V4-CD-D7V2-v1`, digest prefix `f0d355c3`. Separate added, inherited,
narrowed, and routed content. Show A/C eligible-complete dispositions, B as
routed-not-rejected, predecessor identity, and successor branches.

**Output:** `forensic_evidence_trace`

### F4. Follow Candidate A across the lineage DAG

**Surface:** candidate lens or `candidate_career`

Select `V4-A-temporalized-W`. Preserve its bounded dispositions and show CI,
OS, RG, PC, and CI+PC as parallel realization branches. D10.2 promotion remains
limited to the accepted curvature-disabled D7 `G_W` profile.

**Output:** `forensic_evidence_trace`

### F5. Follow Candidate B to its routed boundary

**Surface:** candidate lens or `candidate_career`

Select `V4-B-independent-derived-carrier`. Show admission at early gates,
routing at D7-v2, and D9 status
`routed_not_rejected_no_lifecycle_profile`. Show the source-recorded missing
`U_B` writer/lifecycle work and reopening route without calling B rejected or
instantiated.

**Output:** `forensic_evidence_trace`

### F6. Inspect the V4-D admission slot

**Surface:** alternative layer and `pruned_choices_at`

Render V4-D as a dashed, uninstantiated fourth admission slot closed on
ontology. Show its source-recorded blocked relabels and negative boundary. Do
not render it as a complete fourth architecture that lost a comparison.

**Output:** `forensic_evidence_trace`

### F7. Audit blocked overreads

**Surface:** claim-ceiling view and `negative_claims`

For each locked overread, show the exact D10.2 hardening key/value or other
source reason, stronger blocked claim, source-linked bearing debt when one
exists, and reopening boundary. Do not invent a debt or imply that debt closure
alone is sufficient when the source does not say so.

**Output:** `forensic_evidence_trace`

### F8. Audit object or contract support

**Surface:** `contract_provenance` or `object_dependents`

Select a parent object or equation/contract. Show accepted claims, profile,
candidate and realization scopes, source lineage, blocked overreads, and exact
edge references. Return `indeterminate_requires_review` when support semantics
are not source-determined.

**Output:** `forensic_evidence_trace`

### F9. Admit and reconstruct the complete bundle

**Surface:** notebook startup/bundle admission report

Load the accepted source bundle and require all 14 kernel invariants, admitted
counts `39/29/29/11/67/152`, source digest checks, and byte-identical rebuild.
Fail before rendering if any invariant fails.

**Output:** `forensic_evidence_trace`

**Iteration 2 accepted evidence:** 14/14 kernel invariants pass over 436 typed
nodes and 2,670 total relationships. The independent raw-source audit matches
every node and relationship exactly, and two rebuilds are byte-identical. This
records accepted F9 execution at the validated-graph ceiling.

## B. Navigational Exploration

### N1. Enter through an accepted family

Select `candidate_A` or `complete_step_lifecycle` from D10.2
`coverage_contract.required_families`. Render the bounded family projection and
verify source object counts. Do not treat family counts as profile counts.

### N2. Triangulate by node family

Select a debt and show debt-specific lenses: historical blocked claims,
accepted transformation, closing/routing gate, and forward obligations. A
claim, gate, profile, object/contract, or source selection gets its own admitted
lenses rather than a generic panel.

### N3. Read dependency reach

Select an object or contract. Show direct and transitive propagation reach by
`required`, `one_of`, `conditional`, and negative-boundary relation. Report
annotation/display reach separately. Never label either count importance,
severity, or priority.

### N4. Scrub the lineage DAG

Move along the readable lineage spine while preserving v2 successors, D7G
corrections, realization fan-out, comparison, hybrid, and provenance branches.
Every position binds an accepted record ID and digest and supports backward
forensic reconstruction.

### N5. Materialize alternatives progressively

Move the ghost slider from zero to full visibility. Routed candidates,
conditional alternatives, blocked relabels, and historical claims fade in with
non-color-only ghost styling. No slider or graph action can promote them.

### N6. Inspect a locked overread

Open one locked claim. Show the stronger blocked relabel, exact hardening
source, any source-linked bearing debt, and the reopening boundary set.

## C. Structural Counterfactuals

### C1. Admit Candidate B at D7-v2

**Authoring:** notebook
**Playback:** web

Use `change_candidate_disposition` against D7-v2 with Candidate B scoped as
`V4-B-independent-derived-carrier`. Open the source-recorded reopening boundary
despite the absence of a B equation/contract path. Return a non-empty earliest
reopening set, named missing B work, and
`unknown_beyond_evidence_frontier`. Do not synthesize B-specific D7G-D10
results. Keep independently supported Candidate C-only claims outside the
frontier.

**Output:** `speculative_structural_counterfactual`

### C2. Remove a Candidate A equation term

Apply `remove_term` to a load-bearing Candidate A-only equation/contract. Emit
profile-local rows only for source-connected profiles, separate direct and
transitive effects, and identify the reopening set and evidence frontier. Emit
no Candidate C row unless an accepted common contract connects it.

**Output:** `speculative_structural_counterfactual`

### C3. Replace an operator in a common charge contract

Apply `replace_operator` to a D9 common-charge equation/contract. Scope affected
profiles from accepted profile links and record forward
`verification_obligations_at_risk` separately from claims and debts. An
obligation at risk is not accepted evidence or reopened scientific debt.

**Output:** `speculative_structural_counterfactual`

### C4. Change a normalization that guards a claim ceiling

Apply `change_normalization` to a source surface carrying a blocked-overread
reason. List the exact overread and hardening statement in
`blocked_overreads_at_risk`. This means the scenario has neutralized a lock
premise; it does not activate or validate the stronger claim.

**Output:** `speculative_structural_counterfactual`

### C5. Remove a bounded-contraction term

Apply `remove_term` to a Candidate A contraction condition such as the accepted
`abs(rho) * epsilon_H * (L_S_h + L_S_J * L_C) < 1` surface. Produce exact
invalidation only where the accepted support predicate determines it and
`requires_reexecution_from_gate` for unconditional transformations whose new
outcome is unknown.

**Output:** `speculative_structural_counterfactual`

### C6. Exercise a valid non-load-bearing existing surface

Use an investigation-local conformance fixture containing a valid
equation/contract or parent-object target with no propagation-bearing path.
Return `no_propagation_bearing_effect` and no ripple row. This fixture tests the
kernel classification; current accepted D10.2 equation/contracts all carry
claim links, so the accepted bundle need not expose this as a selectable user
target. Annotation nodes remain outside the mutation algebra.

**Output:** `speculative_structural_counterfactual`

### C7. Contain a profile-local parameter change

Apply `change_profile_parameterization` to a Candidate A-only parameter whose
accepted lifecycle cell requires migration. Emit no Candidate C row unless a
source-recorded common contract connects it.

**Output:** `speculative_structural_counterfactual`

### C8. Animate a fork in time

Freeze the scrubber at D7-v2 and play C1. Keep unaffected accepted history
solid, label minimal invalidation roots and the frontier, and fade unresolved
descendants. The browser uses only the precomputed row.

**Output:** `speculative_structural_counterfactual`

### C9. Round-trip a scenario

Load a canonical C1-C8 scenario in the browser, select its precomputed row,
serialize it for notebook read-back, and require byte equality with the input.
No edit or browser-side recomputation is permitted.

**Output:** `speculative_structural_counterfactual`

**Iteration 5 accepted evidence:** 25 canonical C1-C7 scenarios compile to 24
profile-local rows; C6 remains a canonical no-ripple result. All 24 selected
rows reproduce their input scenario bytes exactly, while stale, malformed,
scope-leaking, and browser-authored scenarios fail closed.

## D. Adversarial And Fail-Closed Validation

### D1. Detect source evolution and reject stale admission

An exact admitted inventory reports `current_bundle_exact`. An additional
unadmitted record reports `new_unprocessed_source_available` with discovery
metadata only. A changed or missing admitted source blocks live reconstruction,
and a scenario with the wrong `source_bundle_digest` fails before rendering.
No case auto-selects an adapter, parses new scientific content, or mixes the new
record into the accepted graph. The receipt names the required successor
adapter/readmission, processing, rebuild, and audit cycle.

### D2. Reject a missing required scope

A valid `remove_term` mutation without `profile_scope` fails closed for the one
declared reason: missing scope.

### D3. Reject an arbitrary graph-state patch

A scenario that attempts a mutation outside the typed algebra returns
`invalid_mutation`.

### D4. Reject false closure past the frontier

A scenario that asserts a positive result beyond the evidence frontier remains
`unknown_beyond_evidence_frontier`, and the iteration gate fails.

### D5. Reject fabricated successors

Candidate B and V4-D scenarios cannot create absent positive successor claims.

### D6. Reject numeric effect injection

A structural counterfactual cannot emit invented magnitudes, performance
numbers, or physical outcomes.

### D7. Reject ghost promotion

Selection, dragging, filtering, slider changes, and playback cannot change a
ghost or historical node into accepted state.

## E. Onboarding And Orientation

### E1. How did GRCv3 lead to GRC9v4?

Use family navigation and the lineage scrubber to follow the accepted bounded
factorization from GRCv4 through its GRC9v4 nine-port specialization to the
disabled GRC9v3 compatibility target. Preserve the distinction between generic
GRC and nine-port-specific content.

### E2. What remains unresolved or unverified?

Use dependency reach and claim ceilings to inspect current transformations,
open/conditional claims, and forward verification obligations. Historical
`must_close_before_D10` metadata may be sorted by reach but remains visibly
historical; it does not glow as a current blocker or imply priority.

### E3. What would it take to readmit Candidate B?

Follow B to its routed D9 boundary and show the source-recorded requirement for
a named B theory/constitutive successor with an exact `U_B` writer/lifecycle,
followed by reopening the named B gates. Present this as open work, not a
promise that B will pass.

### E4. Show all accepted negative claims

Run `negative_claims()` and list each accepted negative claim with the exact
stronger relabel it blocks and source identity.

## Forensic API Coverage

| API | Scenario coverage |
| --- | --- |
| `gate_act` | F3 |
| `debt_lifecycle` | F2 |
| `reconstruction_path` | F1, N4 |
| `candidate_career` | F4, F5 |
| `pruned_choices_at` | F6, F7 |
| `negative_claims` | F7, E4 |
| `object_dependents` | F8 |
| `contract_provenance` | F8 |
| `gate_contribution` | F3 |

All nine planned forensic functions are exercised. F9 additionally exercises
source-bundle admission and the 14 kernel invariants.

## Plan Coverage Validation

| Iteration | Owned scenarios | Supporting/integration scenarios | Plan surface | Coverage |
| --- | --- | --- | --- | --- |
| I1 | D1 | - | Source adapters, bundle identity, immutability | covered |
| I2 | F9 | - | Full admitted graph and 14 kernel invariants | covered |
| I3 | F1-F8, E3-E4 | - | Forensic API and notebook recipes | covered |
| I4 | C1, C4-C6, D2-D6 | C2-C3, C7 semantic classification | Mutation algebra, reopening, support predicates, frontier | covered |
| I5 | C2-C3, C7, C9 | C4-C6 serialization | Ripple compiler, profile scope, scenario identity | covered |
| I6 | N1-N3 | F1, F4-F5, F8 browser projections | Family navigation, triangulation, dependency reach | covered |
| I7 | N5-N6, D7, E2 | F6-F7, E3 browser projections | Claim ceilings and alternatives | covered |
| I8 | N4, C8, E1 | C1-C2 and C9 playback | Lineage and precomputed playback | covered |
| I9 | full suite | all prior scenarios | Acceptance and usability closeout | covered |

Each scenario has exactly one owning iteration. Supporting rows may exercise it
again after another surface becomes available, and I9 reruns all 35.

## Validation Findings

The plan covers all 35 scenarios after one explicit addition:

- C3 required `verification_obligations_at_risk` in the ripple contract. It is
  now a forward-work-only field with no evidence authority.

The scenario normalization also closes five inconsistencies in the proposed
draft:

1. The correct scenario count is 35, not 29.
2. The forensic API contains nine functions, not eight.
3. Bundle admission checks 14 current kernel invariants, not 12.
4. C6 uses a non-load-bearing existing-surface conformance fixture; annotation
   nodes remain outside the mutation algebra.
5. D2 isolates missing scope by using a valid mutation type rather than the
   unsupported generic `weaken` label.

No scenario requires browser-side propagation, a new scientific authority,
runtime implementation, specification changes, or prediction beyond accepted
evidence.
