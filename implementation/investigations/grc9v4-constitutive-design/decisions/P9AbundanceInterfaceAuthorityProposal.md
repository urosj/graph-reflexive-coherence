# P9-4.9.1a — Abundance interface authority proposal

Date: 2026-09-09. Status: **accepted by the user for implementation**.
Owner: P9-4.9.1a, the abundance sub-obligation of `G2-COS-INTERFACE`.
Implementation baseline: `7905e7e22bb2fb37f09d0de01f3f161b83332618`.

The user accepted the bounded P9-4.9.1 implementation by requesting its commit,
not its interim null diagnostic as final interface semantics. This document
records the missing rule, explicitly accepted after the three audit refinements.
The [structured authority](P9AbundanceInterfaceAuthority.json) owns the claim/debt
admission. Design acceptance is not runtime conformance, numeric abundance
authority, support-set promotion or G2 acceptance.

## Accepted decision

Keep the common `abundance` **key required**, but make its **numeric availability
family/capability-owned** for enabled V4. An available value requires an admitted,
versioned definition, detector and evaluation stage. A family without one must
explicitly report unavailable; it must not invent a number or silently omit the
common field. This decision selects no numeric abundance functional for generic
GRCV4 or enabled GRC9V4.

This separates an instantaneous operational diagnostic from the theoretical
long-horizon idea of identity multiplicity. Neither the presence of a field nor
a diagnostic count proves increasing abundance, basin formation or an RC theorem.
No generic basin detector, new trajectory parameter or scientific state is added.
This proposal defines the semantics of availability, not a numeric meaning of
abundance itself.

## Source gap at the implementation baseline

- The [common interface](../../../../specs/grc-common-interface.md#observables)
  unconditionally requires `abundance` but does not define its meaning or numeric
  type. Its `dict[str, Any]` signature is not a scientific definition.
- The [V4 extension](../../../../specs/grc-common-interface-v4-ext.md#status-and-applicability)
  inherits that interface unchanged; its observable and interoperability clauses
  do not yet define V4 abundance availability. The
  [generic spec](../../../../specs/grc-v4-spec.md#observables) adds V4 quantities
  without resolving this inherited name. Profile parameters contain no abundance
  definition or detector policy.
- The [paper §14.2–14.3](../drafts/2026-09-GRC-V4.md#143-grc9v4-as-a-substantive-nine-port-specialization)
  separates graph-generic contracts from nine-port basin/spark mechanics.
  [GRC9V4 capabilities](../../../../specs/grc-9-v4-spec.md#capabilities) include
  `basin_attributes`, but that does not specify a universal abundance count.
- The [legacy V3 observable](../../../../specs/grc-v3-spec.md#observables)
  and [GRC9V3 observable](../../../../specs/grc-9-v3-spec.md#observables) clauses
  supply historical context only. They are not permission to change those
  versions or import their identity detector into every generic V4 profile.

This is a cross-layer interface gap. The sources do not establish an accepted
decision to defer abundance to the facade, nor prove the omission was intentional.
Existing C/OS and lifecycle results remain valid within their recorded scope.

### Forensic source check

Using `load_current_forensic_context` and `contract_provenance` from the
[agentic guide](../tools/exploratory-side-tool/docs/AgenticQueryGuide.md), all
five queries below returned `source_exact_contract_provenance` and retained
`support_disposition=indeterminate_requires_review`. These are constraints and
lineage, **not previously accepted abundance authority**.

All source references are to [D10.2](D10_2FullSubstrateProvenanceAndPromotionAudit.json),
record `GRC9V4-CD-D10.2-v1`, digest
`28343064e85065b7f18227cf429e8cd8f33b414d7a19d5f3e9090a318adcb32c`.
Pointers below are under `/normative_equation_contract_registry`.

| Contract after `D10.2-EC-` | Pointer | Constraint / trace digest |
| --- | --- | --- |
| `PARENT-SPEC-COMPOSITION-PROFILE-IDENTITY` | `/65` | Composition/gain identity cannot be silently altered. `ebb96a7651983aa5d66bca54146c05f035b1ee8328bda86babeb78cc7ca9e6aa` |
| `PARENT-L-SNAPSHOT-RESET` | `/45` | Derived diagnostics are not authoritative snapshot/reset coordinates. `3233c579fdd8ad5e9e8bccbe086144bb6796fa2389c4bf8e8edee67aadbddc95` |
| `PARENT-GRC9-CHILD-BASIN-STABILIZATION` | `/58` | Specialization-only completion is not generic identity counting. `deb7a476b6f9168cfda1aa0961b1fd5844e99d6a2604d6f18d45fcc85c4f80de` |
| `PARENT-BASE-DISABLED-OBSERVABLE` | `/14` | Observable equivalence has its own legacy-target scope. `61390106e02918fa3a25dba1fe114168fa701ef7c728ef40fdb6323e6c10465f` |
| `DISABLED-C_OS-OBSERVABLE` | `/86` | C_OS's disabled observable relation does not prove other reduction surfaces. `e74fd13d774d79f6849484860d28541f46178b5bbe7ed1db120d8cf73a1eccbf` |

The query context has source bundle
`c9fbcabacf22bb554e82dae80f8cc79da811b94baf1350dac5c488aff0503f64`, graph
`a624af16396dfa5eccaede2f5ee9edc378f7bd8bd8f66fd4d7da00f97b8e2eaf` and P9
extension `3715d198eb15564ea459fcd0fdf9d7f185ddce4800cc9b66c31fed41b3f129a0`.
The exact queries reproduce each trace, including its `source_ref` and full
`edge_refs`, at the implementation baseline above. Scanning the admitted graph's
node payloads case-insensitively for `abundance` returned no matches. That is an
inventory observation, not an accepted negative claim or proof that every
possible identity-related source has been ruled out.

## Accepted V4 interface contract

Protocol label: `grcv4-family-abundance-diagnostic-v1` (accepted, not a new
resolved trajectory parameter). The following rules apply to enabled V4's
`compute_observables()` and successful ordinary-step observable maps. They do
not require adding observables to failed results or lifecycle methods whose
existing contract returns none.

1. **Required projection, conditional value.** Always expose these three fields:

   ```json
   {
     "abundance": null,
     "abundance_status": "unavailable_no_admitted_definition",
     "abundance_observation": null
   }
   ```

   This is the lawful result for C_OS and other enabled V4 profiles
   without an admitted numeric definition. It replaces the interim status string
   through the ordered source propagation below. It does not claim a
   detector was run, failed or found zero identities.

2. **Available mode.** `abundance_status="available"` requires a nonnegative,
   finite I-JSON number (not bool; integer counts must be safe integers). The
   family definition owns its exact units, domain, counting/reduction rule,
   classifier thresholds and deterministic ordering. `abundance_observation`
   must then be a closed object with exactly `definition_id`, `detector_id`,
   `stage`, `observed_state_digest` and `model_identity`. `definition_id` must
   uniquely resolve to an admitted versioned definition under the applicable
   V4 interface/specification release; detector and stage identifiers must resolve
   within that definition, not act as arbitrary caller labels. Interpretation
   requires the release, complete model identity, definition ID and detector ID
   together: `model_identity` alone must not determine or imply abundance
   semantics. The observed state digest binds the state actually evaluated.
   Zero is permitted only as a computed available value under that definition.
   This proposal admits **no** such definition, including no automatic GRC9V4 count.

3. **Truthful capability.** Reserve the V4-only flag
   `v4_abundance_diagnostic` for executable numeric support of the exact active
   model identity under the admitted interface/specification release and named
   definition/detector. It is absent for unavailable mode. A registry name, candidate,
   realization, `basin_attributes`, expansion or `completed_spark` capability
   does not imply this flag. Conversely, an implementation advertising the flag
   cannot publish an unavailable result to hide a missing implementation, stale
   detector, unsupported input or evaluation failure.

4. **Failure is not unavailability.** Unavailable means no admitted definition
   applies to that model under the admitted interface/specification release.
   If a declared numeric definition exists but its required implementation/domain
   is unsupported, reject that support/admission
   claim rather than downgrade it to unavailable. Any numeric detector proposal
   must close its typed error/domain contract and be total over the entire domain
   for which `v4_abundance_diagnostic` is advertised. Detector failure on an
   otherwise admitted state is a conformance/programmer failure, not a scientific
   or diagnostic outcome. It raises the declared error; it must not publish
   null/zero/old values as success. For a step result, all diagnostic work remains
   provisional before the sole lifecycle publication, so an exception preserves
   the full prestate. Failure to satisfy the advertised API contract may therefore
   abort publication; this is an atomicity guarantee, not a scientific selection
   rule. Read-only evaluation never publishes state. This proposal does not create
   a solver disposition or insert diagnostic failures into the scientific receipt
   ledger.

5. **Fresh observed state and stage.** Successful step diagnostics describe the
   fully reconstructed prospective target that is published with that result, not an
   OS predictor or previous step's detector. Read-only diagnostics describe one
   captured committed state. Available metadata identifies the actual producing
   stage and evaluated state: `observed_state_digest` is the scientific state
   digest of that prospective target for a successful step, or of the captured
   committed state for `compute_observables()`. It is not the operation's
   pre-operation `source_state_digest`. Unavailable metadata is null because no
   detector ran. A cached value may not survive an incompatible resource/profile/graph/context
   change. Reset, assignment, migration, events and restoration cannot retain a
   source profile's availability or detector by accident.

6. **No scientific feedback; reproducible diagnostics.** Neither abundance nor its
   status/metadata is scientific state, a charge repair, a writer, a spark trigger, or a selection
   control. Its value must never influence constitutive evolution, admission
   choice, solver disposition, spark formation or selection. This does not deny
   that failure of the advertised API contract can abort publication under Rule 4.
   No new snapshot coordinate, mutable callback, hidden history or trajectory
   parameter is introduced. Diagnostic definition/detector identity is not added
   to the complete scientific model/profile identity. A separately admitted
   diagnostic revision may change the definition/detector and interface release
   without changing otherwise identical substrate physics or its model identity.
   Reproducibility records must retain the applicable V4 interface/specification
   release, resolved definition/detector identity and source, observation stage,
   and observed model/state identity together. The closed observation object
   inherits its release context from the producing interface; an exported record
   must retain that context alongside it, never infer it from `model_identity`
   or substitute the currently installed release. A detector that feeds into
   scientific evolution or needs new authoritative history requires separate
   scientific authority and cannot use this read-only exception.

7. **Consumers and legacy boundary.** V4 numeric consumers check both capability
   and status and use the named definition; common-only consumers may access the
   required key but must not assume every model returns a number. The V4
   extension must say this explicitly, rather than hiding it behind “inherits
   unchanged.” Do not edit the common, V3 or GRC9V3 specifications/runtime. The
   exact disabled GRC9V4 branch still delegates to its declared legacy target;
   do not overwrite its native observable values with V4 nulls or metadata.
   V4-only diagnostic fields remain outside the legacy observable projection.
   Enabled GRC9V4 does not gain a numeric abundance definition from that delegate.

## Alternatives and scope of acceptance

| Alternative | Disposition |
| --- | --- |
| Drop `abundance` when capability is absent | Not recommended: changes unconditional common key presence and breaks existing consumers unnecessarily. |
| Always provide a basin count | Not recommended: adds an unselected generic detector and conflates specialization with substrate authority. |
| Use charge, node count, positive-resource count or silent zero/null | Reject as a definition; those values do not establish identity multiplicity. |
| Keep the key; explicitly gate numeric availability | Recommended: closes interface semantics without claiming a new abundance functional. |

The user has selected this rule. Source propagation and conformance tests remain
distinct implementation obligations. Acceptance permits
the unavailable branch for C_OS; it does **not** certify numeric abundance,
other profile implementations, disabled compatibility, or G2.

## Debt, propagation and lean follow-through

Accepted authority routing identifiers: debt
`P9-4.9.1a-DEBT-ABUNDANCE`, object `P9-O-ABUNDANCE-INTERFACE`, contract
`P9-EC-ABUNDANCE-INTERFACE`, claim `P9-4.9.1a-CL-N-001`. The debt is a newly
exposed inherited-interface semantic gap, not a correction to an accepted
D10/D11 abundance claim. Keep existing provenance classifications unchanged.

Use the existing investigation claim/debt and side-tool
admission route, then proposal → paper → V4 extension/specs → runtime/tests.
The proposal and paper need a narrow observable/claim-ceiling note, not new
constitutive equations. The V4 extension owns the exact public fields and
consumer rule; generic/specialization specs own applicability and the disabled
projection boundary. Update the admitted release and affected conformance
mapping; do not create extra gates or a new evidence system.

No scientific/reset/event digest preimage changes for identical scientific
operations are proposed. Derived observable bytes and the specification release
will change; preserve previous runs and their source/release identities. The
existing snapshot release-admission rule remains controlling: do not silently
rewrite old snapshots, infer an old release is current, or promise a new legacy
reader. No new snapshot layout is required merely by this diagnostic proposal.

The necessary runtime follow-through is limited to affected projection/tests:

- verify the exact unavailable triplet through construction, read-only access,
  successful zero/positive steps, restore/reset and existing profile/graph crossings;
- reject contradictory status/value/metadata/capability combinations; distinguish
  available zero from unavailable, using explicitly synthetic protocol controls
  without advertising a production detector;
- bind `observed_state_digest` to the committed read-only state or reconstructed
  step target, not the pre-operation source; reject the old metadata field name
  and stale state/stage bindings;
- check release-bound definition/detector resolution, including an unchanged
  scientific model identity with distinct admitted diagnostic versions; missing,
  mismatched or unresolved release context must not imply a current definition;
- cover the advertised detector's totality obligation and typed conformance
  failure with synthetic controls; retain immutable outputs and prepublication
  rollback without treating a failure as unavailable, zero or scientific selection;
  compare unchanged scientific/reset state and receipt ownership;
- confirm disabled-target projection remains unchanged at its existing source
  boundary; no old-family repair or new GRC9V4 implementation is authorized;
- update only affected interface/catalog expectations, keeping unaffected
  P9-4.9.1 evidence and original run identities. Reconcile final profile evidence
  in P9-4.9.3 and decide G2 once in P9-4.8B.

The original drafting step performed source/forensic inspection only. It ran no new
numerical or browser campaign and does not mark any proposed contract accepted.

Proposal audit disposition, 2026-09-09: all three requested refinements are
incorporated above and in the targeted follow-through: observed-state naming
(Rules 2/5), totality and conformance-failure semantics (Rules 4/6), and explicit
release-bound definition identity (Rules 2/3/6). The audit conditionally supports
this availability contract; that audit itself was not user acceptance, claim
admission or G2 closure. The user subsequently explicitly accepted the refined
proposal and authorized continuation on 2026-09-09.
