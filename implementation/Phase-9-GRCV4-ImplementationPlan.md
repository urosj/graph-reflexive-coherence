# Phase 9 GRCV4 Implementation Plan

Date: 2026-09-05. Status: P9-G1 accepted; bounded implementation authorized.

Phase 9 implements the accepted graph-generic `GRCV4` substrate, followed by
a gated `GRC9V4` specialization. The accepted V4 specifications are the primary
implementation source, read together with the paper and accepted investigation
claims. P9-1.9 records the user's accepted implementation review. The user's
commit instructions accept P9-2.1's immutable value records and P9-2.2's
profile/identity/installed-asset foundation, including audit corrections.
P9-2.3's generic request decoding/admission prefix and failure evidence were
accepted by the user's commit instruction at `1647d3f`. P9-2.4 extends result,
disposition and receipt comparison records, pending its own review/commit;
no executable profile or runtime conformance is claimed. The companion
[checklist](./Phase-9-GRCV4-ImplementationChecklist.md) records execution;
the [phase opening](./Phase-9-GRCV4-PhaseOpening.json) records authority,
predecessor identities, and the completed specification merge.

## Entry and authority

The specification branch was merged into `main` with `--no-ff` at
`e00a8844c045ac4338fa52afb6ab096420fb6161`. Its second parent is the
acceptance commit `935cc532c9c8e53f4fc26bc43e9e40401cdb2410`.
Phase 9 starts from that merge on `impl/phase-9-grcv4`.

The accepted specification release is:

```text
grcv4-spec-release-sha256:9f4c8fe5b57b1c477d834a3e4dae3f98a2b18c70e6e7f598e3c9652170c8645f
```

The user's phase-opening request authorizes this plan, its checklist, and
implementation-review preparation. Review acceptance and runtime execution
are subsequent gates. The accepted specification is frozen. The old
acceptance records retain their as-recorded state; this phase opening records
the later merge and planning activation without rewriting them.

Source ownership remains:

| Source | Role in Phase 9 |
| --- | --- |
| [Generic V4 specification][generic] | Executable generic family contract. |
| [V4 interface extension][interface] | Construction, immutable authority, input admission, receipts, lifecycle, and errors. |
| [GRC9V4 specification][g9] | Nine-port mechanics and exact legacy compatibility. |
| [GRC-v4 paper][paper] | Mathematical meaning, especially sections 3–12, Appendix A, and Appendices C–E. |
| [D10 claim topology][claims], [D10.2 provenance audit][d10-2], [D11-C resolution][d11-c], and [D11-G9 resolution][d11-g9] | Accepted investigation authority, claim classifications, bounded successor results, and prohibited overclaims. |
| [Proposal][proposal] | Claim links and full provenance crosswalk. |
| [Accepted release][release] and [acceptance gate][acceptance] | Exact accepted artifact bytes and runtime evidence still required. |
| [Fixture catalog][fixtures], [vectors][vectors], and [schema][schema] | Required coverage, existing preimplementation oracles, and machine contracts. |
| [Debt ledger][debts] and [D11 routing][routing] | Inherited debt transformations and verification obligations. |
| [Agentic query guide][guide] | Verification of source-bound claims and provenance; the tool does not replace the specs, paper, or investigation claims. |

Every implementation work item must identify its applicable specification
section and machine contract, the corresponding paper passage, and accepted
claim/contract references where applicable. Neither a claim list alone nor
existing runtime code defines the new V4 implementation requirements.

If implementation exposes a scientific contradiction, record the exact
contract, counterexample, and affected claims. Resolve it through an accepted
investigation, then paper/proposal and specification propagation. A runtime
convenience cannot amend the frozen equations or accepted release.

## Scope and support policy

The generic class is `GRCV4(GRCModel)`; the specialization is
`GRC9V4(GRCV4)`. The unchanged common interface is strengthened through the
V4 extension. All V4 adaptations belong to V4. Existing GRCV2, GRCV3, GRC9,
GRC9V3, and LGRC9V3 behavior and specifications remain baseline contracts.
Legacy expansion deficiencies are handled at the V4 wrapper's defined-domain
boundary, as required by D11-G9.

The admitted population comprises `A_CI`, `C_CI`, `A_OS`, `C_OS`, `A_RG2b`,
`C_RG2b`, `A_PC`, `C_PC`, `A_CI_PC`, and `C_CI_PC`. This plan covers work for
all ten, with independent support decisions. The implementation may release
a declared nonempty subset after all applicable requirements pass; planned
profiles stay unadvertised. A partial release must name its remaining work
and does not close the whole planned population.

The proposed first runtime slice is `C_OS`: it exercises the accepted D11-C
transport through an explicit staged realization and early lifecycle closure.
After `P9-G2[C_OS]`, the next reviewed path may be `A_OS` for retained
authority or `GRC9V4[C_OS]` for mechanical/lifecycle pressure. This is an
engineering order for review, with no claim of scientific preference. Every
profile requires its own common, candidate, realization, lifecycle, and
evidence gates; early scheduling does not reduce the conformance contract.

GRC9V4 follows acceptance of the generic support set it consumes. Synchronous
V4 does not depend on completion of the Phase 8 Lorentzian continuation.
Candidate B, new realization/Hodge profiles, singular continuation, RG2b
classical derivatives, physical attribution, stability, endpoint hysteresis,
and profile ranking require their own evidence or successor authority.
GRCL-V4, new landscape lowering, broad visualization, and phenomenology
campaigns are follow-on tracks; required runtime observables and replay
evidence are part of this phase.

## Execution granularity and dependency rules

Numbered top-level tranches organize related work. Each `P9-N.M` checklist
row is the default independently executable and reviewable iteration, with
its own entry authority, exact scope, source-contract map, changed paths,
tests/oracles, commands/results, retained evidence, new debt/failure,
review disposition, and next permitted step. Completing one row does not
complete or accept its enclosing tranche.

When a row crosses independent candidates, profiles, lifecycle surfaces, or
compatibility cells, split it into stable child IDs such as `P9-6.1a` and
`P9-6.1b`. Record the parent, each child's scope and dependencies, and the
parent's reconciliation criterion before execution. The phase architecture
does not need redesign for such a split. Existing `P9-N.M` IDs remain stable;
parents with registered children are aggregate registers, not executable
iterations. Controlled batches must retain a separate result and review
disposition for every child. Tranche 0 records the completed planning bootstrap.

A failed or bounded result stops only its dependent path unless it exposes a
shared predecessor defect. Tranche numbers are organizational, not a global
barrier sequence. After foundation work, complete `C_OS` dynamics and its
applicable lifecycle cases before expanding through all other realizations.
Tranche 7's profile-specific lifecycle rows may run at that point and are
reused by evidence reference when the tranche later generalizes to other
profiles. RG2b certification, an unimplemented A profile, or a pending PC row
does not block an independently accepted `C_OS` path.

The initial route is `P9-G1 -> foundation -> C_OS dynamics -> C_OS lifecycle
and complete fixture reconciliation -> P9-G2[C_OS]`. It can then continue to
the `A_OS` path or, after `P9-G3[C_OS]`, to the C-only GRC9V4 path. Review the
next row's concrete dependencies and authority each time. Shared machinery
changes must rerun affected accepted-profile checks.

## Claims, debt, and obligations carried forward

The successor forensic API reconstructs 41 current claims, 29 historical
claim nodes, 80 normative objects, and 183 equation contracts. The original
29 D10 debt transformations remain intact. The two additional D11 debts have
bounded design resolutions:

| Debt | Accepted resolution | Phase 9 consequence |
| --- | --- | --- |
| `D11-C-DEBT-BASELINE-TRANSPORT-AUTHORITY` | `D11-C-T3a`; optional claim `D11-C-CL-O-001`. | Implement exact `C-HM-STIFFNESS-BASELINE-v1`, then verify its runtime stage, covariance, serialization, and readmission obligations. |
| `D11-G9-DEBT-CANONICAL-PORT-ALLOCATION` | `D11-G9-P4a`; specialization normative claim `D11-G9-CL-N-001`. | Implement the accepted chiral same-port expansion and V4 legacy-defined-domain boundary, then execute their conformance cases. |

The source graph has 18 verification-obligation nodes: eleven inherited
from D10, three added by D11-C, and four by D11-G9. D10's provenance preclose
was satisfied for its current population; the ten other D10 obligations were
routed forward. The D11 source records retain their historical forward
statuses even though subsequent paper/specification propagation is now
accepted. Record that completion through the downstream propagation and
release gates. Do not relabel the frozen graph or count those propagation
rows as runtime work still missing.

Tranche 1 must map every inherited obligation and debt to its exact source,
claim ceiling, current downstream disposition, and either an implementation
iteration or a named deferred scientific gate. Scheduling or passing a
runtime test does not automatically discharge its full scientific debt.
Endpoint, physical attribution, analysis, units/comparability, and successor
debts retain their original conditions.

The following table routes every current vector coverage hold and all
runtime debt named by the acceptance gate. All execution remains pending.

| Coverage hold in the accepted vectors | Planned evidence owner |
| --- | --- |
| `candidate_a_numeric_vectors` | Tranche 5: independent numerical Candidate A oracles and exact initializer. |
| `candidate_a_GRC9V4_expansion_vectors` | `P9-8.3A`: held until a concrete A target vector is supplied; then A reference/history and reconstruction evidence. |
| `per_realization_step_vectors` | Tranches 4–6: concrete complete-step vectors for each supported profile. |
| `RG2b_vectors` | Tranche 6: admitted deterministic evaluator and Lipschitz section certification. |
| `child_stabilization_vectors` | P9-9.1a: child/completed-spark/hierarchy evidence when the optional capability is advertised or explicitly required for project handoff; unselected scope stays pending/deferred. |
| `disabled_GRC9V3_delegate_vectors` | Tranche 9: forty independently tracked profile/surface contracts. |
| `lifecycle_snapshot_reset_migration_vectors` | `P9-4.6`–`P9-4.8` for early C_OS, then profile-indexed Tranche 7 generalization. |
| `generic_mapped_topology_vectors` | `P9-4.7b` / `P9-7.2b` for C_OS before acceptance; Tranche 7 for other supported profiles. |
| `deep_recursive_expansion_and_covariance_runtime` | Tranche 8: D52/deeper runtime expansion, both chiralities, phases, relabeling, and signed reorientation. |
| `charge_precision_edge_vectors` | Tranches 3 and 10: specified charge conventions and independent precision-edge checks. |
| `deep_immutability_runtime_tests` | Tranche 2 and early C_OS lifecycle, then Tranche 7: nested mutation resistance and duplicate independence. |
| `runtime_execution_receipts` | Tranches 2–10: actual operation results, persistent receipt ownership, and reproducible evidence. |

## Review and verification gates

| Gate | Required decision/evidence | Initial state |
| --- | --- | --- |
| P9-G0: phase opening | Exact accepted release, completed no-ff merge, branch, plan, checklist, and predecessor bindings. | Recorded. |
| P9-G1: implementation review | Support order, module ownership, source-to-test mapping, inherited debt routing, and an accepted successor verification policy. | Accepted; [P9-1.9 successor](./phase-9-grcv4/tranche-1/P9-1.9-G1Acceptance.json). |
| `P9-G2[p]`: generic conformance | All applicable runtime/lifecycle cases for exact profile scope p, with independent evidence. | Pending for each profile; accepted support set empty. |
| `P9-G3[S]`: specialization admission | Accepted `P9-G2[p]` for every p in consumed support set S, plus reviewed V4-only mechanics, legacy boundary, and test matrix. | Pending; no consumed set admitted. |
| P9-G4: release and handoff | Exact advertised support, all applicable evidence, legacy regression results, residual-debt routing, and review acceptance. | Pending. |

The checklist records all ten `P9-G2[p]` rows. The aggregate generic support
set contains only individually accepted profiles. A gate record must bind
complete-profile IDs, parameters/domains, fixture coverage, and evidence;
the family label `C_OS` alone is not an executable identity. Acceptance for
one profile or bounded domain implies no other profile or broader domain.

`P9-G3[C_OS]` is shorthand for singleton support set `{C_OS}` with those
exact accepted identities. New profiles added to a consumed set require
their own G2 acceptance and a reviewed G3 extension. G3 admits specialization
work; full GRC9V4 conformance still requires applicable enabled mechanics,
mandatory specialization lifecycle, and all four disabled compatibility surfaces.
Optional completion evidence is additionally required only for advertised
capabilities or an explicitly stronger project handoff. Generic acceptance may therefore
progress while Tranches 6–9 retain unrelated pending rows.

P9-G1 records runtime authority in a new, hash-bound successor. It must
permit the concrete V4 `src/` and `tests/` additions and necessary additive
integration paths while continuing to protect old semantics and the accepted
release. It must distinguish planning/review, implementation, and conformance
states. A branch name, a flag alone, or the old D10.2 acceptance is not proof
of implementation authorization.

At opening, the dedicated release-acceptance audit passes all twelve release
members. The existing `verify-post-d10-specifications` entry point fails on
the merged baseline because its historical phase envelope rejects the three
later acceptance files. This failure predates the Phase 9 documents.

Tranche 1 must provide successor verification and connect it to the normal
entry point. Preserve the release-bound historical auditor and boundary
bytes; use the accepted historical revision for their historical assertions
and a successor audit for the present tree. The successor must validate this
opening and later runtime authority without inferring that every new file is
permitted. Include adversarial checks for unauthorized source/test changes,
modified legacy/specification bytes, and forged or stale authority. Keep
tool plan/checklist and any affected API, notebook, and browser verification
surfaces consistent. This integration is planned work, not completed by
creating the phase documents.

## Implementation tranches

### Tranche 0. Planning bootstrap

Register Phase 9, create the branch and companion documents, record the
specification merge, validate the accepted release, and inspect the current
forensic authority. This bootstrap supplies planning evidence only.

### Tranche 1. Implementation review and successor verification

Current disposition: the user accepted P9-1.4–P9-1.8 and the reviewed V4-only
implementation scope through [P9-1.9](./phase-9-grcv4/tranche-1/P9-1.9-G1Review.md).
P9-G1 is accepted. The implementation verifier checks that separate approval,
exact target roster, additive integration and per-iteration content bindings.
The earlier preparation states below remain historical descriptions, not the
current gate state. All G2/G3/G4 gates, fifteen source obligations and five
implementation follow-ups remain pending; no runtime profile is advertised.
The [foundation acceptance](./phase-9-grcv4/tranche-2/P9-2.1-2.2-AcceptanceRecord.json)
makes P9-2.3 dependency-ready alongside P9-2.1/P9-2.2. Later generic
paths cannot borrow those leaf IDs; their own accepted prerequisites remain
required. P9-1.9 creates no runtime code.

The [evidence handoff addendum](./phase-9-grcv4/tranche-1/P9-1.9-EvidenceHandoff.md)
preserves path-normalized copies of selected supporting outputs in a repository
bundle, with original hashes retained for citation and separate published hashes.
For current work, relevant development failures need concise cause/correction/
limitation summaries, not permanent raw archives of every attempt. Preserve raw
failure evidence only when material to a result or its limits. Published
supporting evidence remains immutable; no new gate or per-attempt process is
introduced. Historical blanket retention wording remains as-recorded and is
superseded by this clarification.

The user-requested [prospective evidence workflow](./phase-9-grcv4/tranche-1/P9-1.9-EvidenceHandoff.md#prospective-evidence-workflow)
records the direction for subsequent leaves: one readable claim-to-check index,
one manifest per retained execution, small runnable reproducers, selective
supporting outputs, Git references for committed source and capture alongside
execution. Preserve published evidence and simplify future collection. Shared
capture automation remains follow-through work; this note does not claim it
has been implemented or add a new acceptance gate.

P9-1.1–P9-1.3 are prepared as the first controlled
[review package](./phase-9-grcv4/tranche-1/P9-1.1-1.3-Review.md), with separate
iteration results, a reproducible source crosswalk, all 31 debt records, and
all 18 obligation routes. The user accepted P9-1.1–P9-1.3 on 2026-09-05;
the later [acceptance record](./phase-9-grcv4/tranche-1/P9-1.1-1.3-AcceptanceRecord.json)
binds the unchanged preparation evidence. Module names in that crosswalk
remain proposals for P9-1.5, not separately accepted ownership. P9-G1 and
runtime authority are unchanged; the original record retains its as-prepared
state without invalidating downstream evidence bindings.

P9-1.4's [support/dependency review](./phase-9-grcv4/tranche-1/P9-1.4-SupportReview.md)
and P9-1.5's [ownership/oracle/legacy review](./phase-9-grcv4/tranche-1/P9-1.5-OwnershipReview.md)
are now completed engineering recommendations, pending user acceptance.
They retain C_OS's complete generic/lifecycle gate, independent A_OS or
singleton GRC9V4 follow-on routes, exact planned lifecycle children, and all
ten support rows. Seventeen V4-owned modules refine the initial crosswalk;
135 explicit legacy baseline paths and 868 passing existing tests establish
the starting regression boundary, not V4 conformance. Existing core contracts
remain unchanged; only two existing files are proposed for later reviewed
additive integration. No runtime or dependency edits are authorized by these
reviews. At that checkpoint, P9-1.6–P9-1.9 and P9-G1 remained pending.

The independent P9-1.4/P9-1.5 review corrections are now applied: canonical
`CI+PC` realization values (unchanged composite family IDs) and the P9-9.1
optional-completion/mandatory-lifecycle split below. All five implementation
follow-ups and six successor-verification pressure checks are registered with
existing leaf owners in the checklist and ownership review; none is runtime
evidence. Registration itself did not complete P9-1.6–P9-1.8. The supplied independent review
and raw static checks are retained separately from our corrected validation.

P9-1.6 now supplies a [successor verification candidate](./phase-9-grcv4/tranche-1/P9-1.6-SuccessorVerification.md).
The normal entry points dispatch to the validated planning boundary; the
unchanged historical auditors run in the exact accepted release checkout.
This resolves the implementation-planning routing defect without changing
the release, predecessor reviews, or their as-recorded states. Its later
[P9-1.7/P9-1.8 successor](./phase-9-grcv4/tranche-1/P9-1.7-1.8-VerificationReview.md)
now verifies all six review pressures and supplies accessible, consistent
API/notebook/browser/scenario surfaces. The separate leaf results and exact
predecessor snapshot retain the distinction between engineering completion
and user acceptance. The five runtime implementation follow-ups remain
pending; no source obligation or scientific debt is discharged. P9-1.9/P9-G1
and candidate user acceptance remain pending. Later runtime states require a separately accepted policy; no flag
or planning pass authorizes source, tests, or dependencies.

The supplied P9-1.6–P9-1.8 pressure guides are reconciled in the
[bounded audit closure](./phase-9-grcv4/tranche-1/P9-1.6-1.8-AuditClosure.json).
This includes attributable per-case evidence, combined and broken-checker
controls, source-admitted semantic mutations and real negative-result
projection through API/notebook/browser/export. Raw execution archives and
three batch results supplement the stable tracked coverage index; they do not
accept a leaf, expand runtime scope or rewrite historical authority.

Produce an equation/contract-to-module-and-test map using the paper and
specifications. Preserve source references, classifications, edge witnesses,
and trace digests when using the forensic API. Use direct JSON for literal
registry/locator questions outside the graph; an unknown claim must remain
unknown. Map all carried debts and obligations, including the downstream
completion of D11 paper/spec propagation.

Review proposed V4-local modules under `src/pygrc/models/`, V4 tests, shared
interface adapters, dependency needs, and artifact storage. Freeze exact
legacy regression targets and define an independent conformance harness.
Complete successor verification routing, then record P9-G1 acceptance before
runtime changes. The detailed map and selected implementation set are review
deliverables; this plan does not invent their acceptance.

### Tranche 2. Interface, identity, and evidence foundation

P9-2.1's [review](./phase-9-grcv4/tranche-2/P9-2.1-Review.md) and
[execution record](./phase-9-grcv4/tranche-2/P9-2.1-ExecutionRecord.json) document
the first V4-owned records and common read-only projections. Focused ownership,
legacy core and typing checks pass. Identity/semantic admission, actual lifecycle
execution and installed-distribution verification remain with their existing
leaf owners; all conformance gates remain pending.

P9-2.1's independent stress audit exposed and now verifies corrections to
integral-adapter range checking and ordered-coordinate input handling. Original
audit/subject bytes and corrected execution are retained separately. Equality
authority, wide-map scaling and explicit codec projections are recorded with
P9-2.2/P9-2.3/P9-2.6; those advisories do not become new scientific debt or gates.

P9-2.2's [review](./phase-9-grcv4/tranche-2/P9-2.2-Review.md) and
[execution record](./phase-9-grcv4/tranche-2/P9-2.2-ExecutionRecord.json) record
typed complete declarations for all ten shapes, exact published JCS identities,
Candidate C reference-map checks and installed release-bound schema assets.
Declared profile resolution is not executable algorithm/domain admission:
the runtime support set remains empty. H1 is enforced through typed/JCS
comparison, and H2's immutable item traversal is corrected and scale-tested.
Clean wheel/sdist baseline and optional-extra installs are verified without a
checkout; later lifecycle/facade integration remains with P9-2.3/P9-2.6.
The current checker routes only the already-constrained `pyproject.toml`
dependency/package-data additions to P9-2.2 as well as P9-2.6; model exports
and all other leaf prerequisites retain their existing gates.

The P9-2.2 independent audit corrections normalize schema-admitted count fields
on both constructor paths (R1), provide an explicit exact-canonical binary64
reconstruction route distinct from strict configuration decoding (R2), and
check C/reference-Hodge values by stable edge ID without mobility substitution
(F1). These have 79 focused regressions and 357 passing stress probes, including
the recorded two-callsite selection of the new reconstruction API. Original
audit/subject bytes and execution remain separate from the corrected run.
Native safe-integer rejection, frozen vectors and empty support sets are
unchanged. P9-2.3 still owns operation-specific decoding/admission composition;
P9-3.1/P9-4.1 retain actual graph/SPD/domain admission. Engineering completion
did not itself infer user acceptance. The subsequent commit instructions,
clarified by the user as acceptance, establish the separate foundation decision.
Historical execution records keep their original bytes and preparation status.

P9-2.3's [review](./phase-9-grcv4/tranche-2/P9-2.3-Review.md) and
[execution](./phase-9-grcv4/tranche-2/P9-2.3-ExecutionRecord.json) cover distinct
transport-shape errors, strict step requests, noncommitting negative-duration
failure receipts and typed migration declarations. The latter do not execute
or admit a crossing. New outlier regressions reject trailing-newline identity
suffixes and nonzero wire values that would underflow to zero; native numeric
limits, exact-canonical reconstruction and all frozen preimages remain intact.
The generic request surface has no fault hooks, pickle restoration, model
facade or executable profile. Later state/domain admission and full transaction
atomicity remain assigned to their existing owners. A user instruction to
commit accepts the reviewed work being committed, not unrelated future work
or any stronger runtime-support claim.

P9-2.3's two independent reviews retain the implementation and clarify its
consumer boundary. Configuration decoding stays the default for external JSON:
finite decimal/exponent tokens (including subnormals) are supported, while
integer-shaped tokens must be safe integers. Exact JCS restoration is the
explicit canonical route; neither route silently retries the other. A strict
request certifies shape and duration sign only. Content-checked receipt identity
is neither a signature nor proof of a live state, an executed failure, full
request equality or replay authority. The frozen receipt preimage is unchanged.

Carry the following tests into their existing owners; these are implementation
follow-through, not additional gates or work performed by P9-2.3:

- P9-2.4: negative duration composes a rejected operation with
  `solver_disposition=None`, no commit ID and no persistent-ledger append.
  Keep returned failure evidence separate from the persistent receipt ledger.
  A later charge rejection after a successful solve retains `valid_root` while
  rejecting the operation; enum membership alone is not an executed stage.
- P9-2.4/P9-2.5 and full-step/lifecycle consumers: bind the actual prestate and
  exact request separately; compare scientific and lifecycle payloads as well
  as their digests on failure. Reject a grammar-valid wrong source or rehashed
  foreign operation/stage/code receipt at the owner with the real execution.
  Receipt equality must not authorize replay or substitute another request.
- P9-2.6/P9-4.4/P9-4.5/P9-4.7a and Tranche 7 consumers: strict zero, smallest positive
  subnormal and extreme finite durations still need full graph/profile/context/
  domain admission. No state or admission may be inferred from a request type.
  Migration declaration decoding proves neither history nor supported targets,
  mappings or lawful crossings. Enforce these tests when the real consumer
  exists; no placeholder model/admission capability is introduced in this leaf.

Implement immutable lifecycle-owned records, read-only common projections,
profile/parameter resolution, deep immutability, and canonical IDs against
the versioned schema and preimage vectors. Separate wire decoding, semantic
admission, and strict admitted requests. Implement typed operation/solver
dispositions, failure results, receipt deltas, and persistent ledger ownership.
Keep test fault injection outside production inputs and scientific identity.

Start the runtime conformance harness here. Compare independent expected
values with actual operations; a vector builder, schema pass, or captured
constant cannot serve as evidence that the model executed the equations.

P9-2.4's [review](./phase-9-grcv4/tranche-2/P9-2.4-Review.md) and
[execution](./phase-9-grcv4/tranche-2/P9-2.4-ExecutionRecord.json) extend the
existing state-module result records with closed payload reconstruction, typed
failure/envelope ownership and cross-field disposition checks. The step module
owns pure receipt/commit construction and comparisons against exact captured
request, scientific payloads, observed outcomes and ordered ledgers. It does
not own a model commit, graph admission, numerical solver, rollback engine or
replay authorization. A successful receipt is content-valid, not causal proof.
The checked result boundary uses generic profile/model identity; specialization
profile binding is fail-closed until its owner exists. Closed GRC9-labelled
published result fixtures may still be reconstructed as records.

The separate [P9-2.3 acceptance](./phase-9-grcv4/tranche-2/P9-2.3-AcceptanceRecord.json)
binds that reviewed commit without changing historical runs. The current
ownership adapter adds the checklist's P9-2.4 responsibility to the existing
state and step module/test pairs, omitted from the coarse frozen source-group
iteration lists. It grants no lifecycle-module, facade or harness ownership.
The subsequent [P9-2.4 acceptance](./phase-9-grcv4/tranche-2/P9-2.4-AcceptanceRecord.json)
records the user's commit instruction at `3845c41`. It enables P9-2.5's two
reviewed test paths; all runtime conformance gates remain pending.

P9-2.4's two-audit follow-up guards original index representations and ordered
event containers before conversion, accepts revalidated typed or primitive
commit preimages, and restricts evidence storage to immutable bytes without
granting those bytes authority. Eleven added regression/characterization tests
preserve numeric, ownership, observation and receipt-content boundaries.
The frozen receipt core does not settle parent-reference scope/order. P9-7.6
must resolve that contract and verify lineage; the current builder/comparator
does not certify a parent DAG or impose an editorial intra-commit-only rule.
P9-2.5/P9-4.7a carry the four retained invalid-transition characterizations into
independent live-operation oracles, not content-matching fixtures.

P9-2.5's [review](./phase-9-grcv4/tranche-2/P9-2.5-Review.md) separates actual
negative-duration prefix execution from supplied-observation and mutation
controls. Independent restricted-ASCII identity calculations and rational
binary64 charge/clock comparisons do not use production algorithms to choose
expected results. Concrete graph, profile, parameter, K4/Hodge, context, reset,
live state and ordered ledger payloads accompany exact requests and results.
The run binds source bytes and environment and can be inspected without a
rerun. A new run never overwrites an original record.

The four invalid-transition cases now fail independent fixture-clock/zero-time
controls; they are not yet live numerical-step negatives. P9-4.7a must apply
them to the actual step. Positive clock progression is an explicitly declared
fixture convention, not newly invented specification authority. Near-admitted
conditioning and repeated-eigenvalue projector pressure stay with P9-3.4/
P9-4.5. Full rollback, profile/domain admission and parent lineage remain open
under their existing owners. P9-2.6 is not started or unlocked by this work.

The P9-2.5 independent-audit correction narrows only the reference writer's
fractional identity envelope and the default CLI retention recipe. Malformed
captures now produce diagnostic-only evidence; failed comparison records are
rechecked; inspection retains evidence class and non-conformance limits.
Harness/oracle origin and import-time source hashes are bound without claiming
bytecode attestation. Original runs are preserved, with separate corrected
evidence. Production binary64 rules and frozen scientific authority are unchanged.

P9-2.6 follows the user's P9-2.5 commit acceptance (`2075f47`), recorded
separately from the original execution. Its
[review](./phase-9-grcv4/tranche-2/P9-2.6-Review.md) verifies current foundation
integration without introducing a facade: declarations remain unsupported,
record/common-field ownership stays immutable, installed distributions fail
closed without dependencies or intact assets, and older behavior is unchanged.
The symbol-level record binds exact baseline files and current consumption.
The sole direct legacy symbol consumed is `GRCEvent`, defensively copied;
mutable legacy state/storage and non-JCS serialization are not reused.
Before P9-3.1, choose V4-local immutable canonical-ID lookup for its pure graph
maps rather than wrapping mutation journals, integer allocators or mutable
slot records as scientific authority. P9-3.1 must implement/test that decision;
future topology allocation and exact legacy delegation keep their own owners.
API/notebook/browser expose six ready leaves and nineteen eligible paths, not
acceptance of P9-2.6 or runtime support. The optional export path is eligible
but unchanged until an actual authorized facade exists. P9-3.1 remains held.

P9-2.6's self-check hardening adds installed foundation/representation consumers,
fresh import orders, actual module/archive bindings and mixed-use comparisons
for the five older concrete families. A separate final-source combined run
replaces no historical execution. The unchanged default-prefix CLI is replayed
under its existing P9-2.5 vocabulary solely as P9-2.6 verification follow-through;
matching deterministic contents do not grant new evidence credit or acceptance.
The review reconciles every guide section with a current check or its precise
later owner. Production, older families, accepted claims and release stay fixed.

### Tranche 3. Typed graph, geometry, transport, and charge

P9-3.1 now follows the separately recorded P9-2.6 acceptance at committed
subject `5307343`; the user explicitly requested this entry. Historical
P9-2.6 review states above remain evidence of their original review time.
The [P9-3.1 review](./phase-9-grcv4/tranche-3/P9-3.1-Review.md) binds the
source/spec/paper/forensic map, immutable stable-ID lookup decision, typed
pairings and flat/sharp maps, candidate-owned factors and reconstruction
checks. Its implementation is pending user review. Only P9-3.1 is newly
eligible (seven dependency-ready leaves, twenty-three runtime paths);
P9-3.2 and numerical support remain gated.

The first independent audit's local positivity finding is corrected by exact
dyadic Sylvester/Bareiss validation in both Hodge constructors. Native NumPy
2.4.6 runs preserve the original 25 exposures and the corrected 876/876 stress
result; 67 primitive tests pass, including clean wheel/source installations.
The review records the proof, independent multidimensional/scale/permutation
pressure, reconstruction inputs and exact remaining stage/conditioning gates.
This correction does not accept P9-3.1 or change frozen mathematical policy.

P9-3.2 follows the explicit P9-3.1 acceptance at committed subject `dccb1ca`,
recorded separately in [P9-3.1 acceptance](./phase-9-grcv4/tranche-3/P9-3.1-AcceptanceRecord.json).
The historical preparation states above remain unchanged in their original
records. The [P9-3.2 review](./phase-9-grcv4/tranche-3/P9-3.2-Review.md) and
[execution](./phase-9-grcv4/tranche-3/P9-3.2-ExecutionRecord.json) cover the bound
reference/context geometry, affine domain, exact stage inputs and closed derived
cache reconstruction. P9-3.2 is implemented pending user review; eight leaves
are dependency-ready and twenty-three runtime paths eligible. P9-3.3 and
numerical runtime support remain held. Candidate current regularity, full
persistent-carrier invariant domains and complete-step admission keep their
existing later owners.

The independent P9-3.2 audit's mixed-scale star-assembly witness is retained
as concrete P9-3.4 numerical-envelope work: `(5e-324, 1e150)` on adjacent
ordinary edges loses a representable coupling in one edge order. The review
distinguishes this componentwise loss from small normwise error and records
native audit/package confirmation separately from the external qualified run.
Additional CI/PC/CI+PC/RG2b realization work remains in Tranche 6 and does not
become a new prerequisite of the immediate P9-3.3 charge step.

P9-3.3 follows explicit acceptance of P9-3.2 at `77286b2`, preserved in
[the P9-3.2 acceptance record](./phase-9-grcv4/tranche-3/P9-3.2-AcceptanceRecord.json).
Earlier pending states above describe their original executions. The
[P9-3.3 review](./phase-9-grcv4/tranche-3/P9-3.3-Review.md) maps the charge,
continuity and selected-current boundary to exact spec/paper/tool sources and
independent tests. Its [execution](./phase-9-grcv4/tranche-3/P9-3.3-ExecutionRecord.json)
retains automated numerical/package and permission/surface validation.
One provisional resource evaluation follows a full bound supplied current;
nonnegative/finite/charge admission precedes final-consumer exposure. The
prescribed binary64 tree and exact tolerance inequality retain the unchanged
resource and no remainder. Root execution, final reconstruction, writers and
atomic lifecycle commit retain their later owners. The user explicitly accepted
P9-3.3 for commit after audit follow-up and evidence cleanup. The current
permission adapter still has nine dependency-ready leaves and 23 eligible
runtime paths; a later transition can bind the accepted commit for P9-3.4.
Runtime support remains empty. The mixed-scale star witness and broader
numerical-envelope work remain open. The next separately requested maintenance
task is to remove P9-3.1's dependency on Downloads paths using repository-local
evidence while preserving audit provenance, after the P9-3.3 commit.

The P9-3.3 independent audit adds a paired conservation limit to that handoff:
zero rounded residual can hide exact stored-coordinate sum growth, while an
exact-conservative transfer can fail the prescribed rounded charge gate.
The [leaf review](./phase-9-grcv4/tranche-3/P9-3.3-Review.md#independent-audit-follow-up)
binds literal witnesses, native audit replay and mutation controls. P9-3.4 must
characterize cancellation-heavy divergence and the charge/dynamic-range
envelope; later experiments must distinguish rounded-policy compliance from
exact conservation and primitive compositions from complete executed beats.
No numerical repair or alternate charge rule is introduced by this audit.

P9-3.4 follows the committed P9-3.3 acceptance at `ce83d7a`, preserved in
[its separate record](./phase-9-grcv4/tranche-3/P9-3.3-AcceptanceRecord.json).
The P9-3.1 repository-reference maintenance mentioned above was completed in
`9409252`. The [P9-3.4 review](./phase-9-grcv4/tranche-3/P9-3.4-Review.md) maps
nonidentity SPD solves, conditioning, repeated-cluster projectors, signed
coordinates, domain/cache failures and charge precision to independent checks.
The star witness is corrected by an exact represented product with one final
binary64 rounding and a new derived-assembly identity; true final underflow,
rounded PSD loss and aggregation overflow remain explicit numerical limits.
The original full run passes 1,653 tests with no skips; a separate test-only
follow-up adds 288 dense near-gap projector actions. The audit follow-up passes
the full current 1,662-method roster with no failures, errors or skips and all
568 native independent scenarios. Permission/surface checks pass
137 authority, 20 JavaScript and 18 browser tests. Ten leaves and 23 runtime
paths are dependency-ready; P9-3.5 and runtime support remain held. The leaf
is implemented, verified and explicitly accepted by the user for commit after
audit follow-up and evidence consolidation. This accepts the bounded P9-3.4
implementation; runtime profile support remains empty. P9-3.5's separate
permission transition can bind the accepted commit.
The [independent audit follow-up](./phase-9-grcv4/tranche-3/P9-3.4-Review.md#independent-audit-follow-up)
closes the capture-coverage gap with a reviewed exact test roster, structured
outcomes, run-local diagnostics, loaded-source checks and validated provenance.
It retains the exact-SPD/nonpositive-computed-pairing witness for both Hodge
types. P9-4.2/P9-4.5 and later norm/energy consumers must execute their numerical
validity policy against it; no clipping or positivity repair is authorized.
Actual selector coverage must test both sides of the cutoff, its exact boundary,
strict-gap loss and physical-versus-retained conditioning.

P9-3.5 entry now binds P9-3.4's accepted commit `12611fe` in
[its acceptance record](./phase-9-grcv4/tranche-3/P9-3.4-AcceptanceRecord.json),
advancing the earlier ten-leaf permission state to eleven ready leaves with
the same 23 eligible runtime paths. The
[P9-3.5 review](./phase-9-grcv4/tranche-3/P9-3.5-Review.md) maps complete captured
prestate preservation to implemented local rejection boundaries, pre-operation
reconstruction failures and independent observer controls. The original full
capture passed all 1,675 regression methods and the permission/surface checks.
The limited audit follow-up corrected skip-name reporting and expanded observer
pressure; all 20 focused methods passed. Implementation and validation are
complete, and the user explicitly accepted P9-3.5 for commit after that follow-up.
The bound review and execution record preserve their pre-acceptance state.
The external audit's primary-source review remains incomplete; this acceptance
does not extend its findings. Tranche 3's five leaves are accepted within their
recorded scopes. At that Tranche 3 handoff, the later entry still needed to bind
P9-3.5's accepted commit and P9-4.1 had not started; the current Tranche 4 status
is recorded below. Runtime support remains empty, and real complete-step
and lifecycle rollback remain later obligations.

Implement deterministic graph order/orientation, differential identity,
one-form versus physical-flux maps, Hodge pairings, candidate-local mobility,
geometry profiles, and stage-aware derived caches. Implement one authoritative
resource write and the exact admitted charge gate without an unearned repair
coordinate. Test nonidentity SPD cases, signed reorientation, stale-cache
handling, domain failures, and precision edges.

### Tranche 4. Candidate C with OS

Current leaf: P9-4.3 on `impl/phase-9-grcv4-tranche-4`. Accepted predecessor:
P9-4.2 at `ac3a7cf`, with P9-3.5's
accepted `155c728` subject separately authenticated. The
[P9-4.1 review](./phase-9-grcv4/tranche-4/P9-4.1-Review.md) covers the implemented
complete-profile reference binding, exact stable-edge admission, separate
constructor identities (including declared units), and reconstruction.
The user's commit instruction accepts this leaf after the capture audit
correction and execution-record reconciliation. The focused follow-up passed
51 methods and seven relocated checks; both source revisions reconstruct.
Review/execution records retain their validation-time dispositions and historical
attribution limits. P9-4.2 entry binds accepted `94a079d` in the separate
[P9-4.1 acceptance record](./phase-9-grcv4/tranche-4/P9-4.1-AcceptanceRecord.json),
opening thirteen leaves with the same 25 paths. P9-4.2 is implemented, verified and
explicitly accepted by the user for commit after the user reported that both
reviews found no defects: see its [review](./phase-9-grcv4/tranche-4/P9-4.2-Review.md)
and [execution record](./phase-9-grcv4/tranche-4/P9-4.2-ExecutionRecord.json).
All 123 focused methods passed; reconstruction verifies the source manifest and
17 relocated methods pass under each of two hash seeds. Exact mathematical
current regularity precedes rounding, and conditioning is checked on the actual
physical block. Selector ties/gap loss, the earlier pairing audit witness,
dense SPD multigraphs, numerical extremes, stage provenance and typed Read-Back
receive executable pressure. Review/execution records retain their validation-time
dispositions. P9-4.3 entry binds accepted `ac3a7cf` in the separate
[P9-4.2 acceptance record](./phase-9-grcv4/tranche-4/P9-4.2-AcceptanceRecord.json),
opening fourteen leaves and the same 25 paths. P9-4.3 is implemented, verified and
explicitly accepted by the user for commit: its
[review](./phase-9-grcv4/tranche-4/P9-4.3-Review.md) and
[execution record](./phase-9-grcv4/tranche-4/P9-4.3-ExecutionRecord.json) bind
143 passing focused methods and 27 passing reconstructed derivative/capture
methods with a changed hash seed. Complete supported-profile baseline derivatives,
all four separate zero controls, covariance, literal oracles, term-omission
controls, repeated/closing gaps, resource boundaries and saturation are covered.
Production source is unchanged. Review, execution and run records retain their
validation-time dispositions; this plan and the commit record the later user
acceptance. A separately authorized P9-4.4 entry can bind the accepted commit;
P9-4.4 and profile conformance remain held. The reviewed owner combines Candidate C
work in `grc_v4_candidate_c.py` rather than the earlier proposed split transport module.

Implement the positive stable-edge reference map and separate Hodge/mobility
constructors, the exact D11-C potential and baseline flux, strict-gap selector,
Read-Back typing, and the regular total-current solve. Preserve the three
independent zero controls. Implement one OS predictor/geometry/corrector pass,
its split residual, post-continuity rederivation, and atomic failure. Record
concrete `C_OS` operation evidence with its complete profile identity.

Run `P9-4.6` snapshot/load/reset/rebase/duplication work and `P9-4.7a`
failure/receipt/replay pressure immediately after the dynamics rows. In
`P9-4.7b`, execute the remaining applicable C_OS lifecycle and mapped-event
cases through early profile-specific Tranche 7 rows. Include migration
admission/rejection and reset after events/migrations as required by the
declared support and catalog. Unsupported targets must fail explicitly;
excluding an operation cannot waive a mandatory C_OS fixture.

`P9-4.8` reviews the full fixture product and accepts, rejects, or holds
`P9-G2[C_OS]`. A successful state-to-step-to-receipt-to-snapshot-to-replay
cycle is valuable early evidence, but cannot alone earn generic conformance.
Each remaining mandatory case keeps G2 pending until it is executed.

### Tranche 5. Candidate A with OS

Implement exact history-free initialization, authoritative positive retained
mobility, log-space writer, the accepted direct current and Read-Back, and
the old/new retained-state stage separation. Produce numerical and stage
oracles for `A_OS`. Initialization, retention, and observed formation remain
distinct claims.

The `A_OS` path may follow the early `C_OS` acceptance or a reviewed C-only
specialization pressure slice. Execute A's lifecycle rows from Tranche 7
before `P9-G2[A_OS]`; other realizations need not be complete first.

### Tranche 6. Additional complete realizations

Add CI with declared root selection and exact domain/conditioning failures;
PC with old-history read and one scalar-ZOH carrier update; and CI+PC with
the exact same-source gain-two composition. Add RG2b only with its admitted
deterministic invariant-section evaluator and certification. Its Lipschitz
contract does not authorize a classical Jacobian. Track A and C separately
for every realization; publish no implicit fallback or unsupported profile.

CI, PC, CI+PC, and RG2b each have separate C, A, and shared-realization audit
children in the checklist. Numerical/failure oracles accompany each child's
implementation. `P9-6.5` reconciles those results; it does not defer all
testing to the end of Tranche 6. A profile can proceed to its lifecycle and
G2 review while other children remain pending. RG2b evaluator/certification
work has its own dependency path and no automatic hold on CI, OS, or PC.

### Tranche 7. Generic lifecycle generalization and conformance

Generalize the early C_OS lifecycle through profile-indexed iterations.
Complete save/load/replay, reset after ordinary/migration/event operations,
rebase, independent duplication, profile migration, and caller-mapped generic
topology events. Map both live and reset authority. Keep candidate-history
and carrier-history dispositions separate, require explicit charge/resource
policies, and rebuild/readmit the entire target before atomic commit.

Profile migrations (`P9-7.2a`) and caller-mapped topology events (`P9-7.2b`)
are separate execution surfaces. Instantiate children by exact source/target
profile or event scope before execution. Link previously accepted C_OS
evidence rather than reinterpreting it as all-profile coverage.

Exercise missing lineage, invalid reference maps, readmission failure, and
receipt ownership. `P9-G2[p]` is available only for profiles whose full
applicable fixture product has executed. Keep other planned profiles pending.
`P9-7.8` may review `P9-G3[C_OS]` immediately after its G2 acceptance;
completion of the other Tranche 7 or Tranche 6 rows is not a prerequisite.

### Tranche 8. GRC9V4 mechanical specialization

Enter for an explicitly admitted `P9-G3[S]` support set, potentially `{C_OS}`.
Separate chart/port graph, row differential/weights, mechanical candidate
trigger, and coarse-graining/Split into `P9-8.1a`–`P9-8.1d` iterations.
Implement D11-G9-P4a's exact
boundary reservations, primary spine, both chiralities, conditional phase,
arbitrary-size tree, capacity accounting, stable IDs, and initialization.
Use the normative port map, without deriving a repair from legacy code.

The accepted concrete expansion vectors cover C profiles. `P9-8.3C-OS`
executes C_OS identity/resource/reference-map and absent-carrier semantics;
`P9-8.3C-PC` separately executes the nonnull carrier reset/loss vector only
after C_PC's generic and specialization entry gates. `P9-8.3A` remains held
until a concrete Candidate A target/history vector exists and its A profile
entry gates pass. An A template identity is not expansion evidence. Create
that new oracle as V4 runtime evidence outside the frozen release. The A
and C_PC dependencies do not hold the C_OS path.

Execute runtime counterparts of every applicable accepted D30, D31, D45,
and D52 vector, including the exact chirality/phase cases. D37 and D44 are
additional capacity-shell boundary probes, never substitutes for those
normative vectors. Keep any deeper declared probes separately labeled.
Execute accepted edge-order permutation, cyclic chart rotation, reflection/
chirality conjugacy vectors, signed-edge reorientation, phase-boundary,
and target occupancy/resource/history/readmission cases. Existing D52
construction vectors remain preimplementation evidence; runtime D52 and
covariance execution are required before arbitrary-size conformance claims.

### Tranche 9. Hybrid completion and disabled compatibility

Keep P9-9.1 as an aggregate with two separately reviewed children:
P9-9.1a covers optional child-basin stabilization, completed-spark registration,
and hierarchy; P9-9.1b covers mandatory specialization lifecycle semantics.
Both follow P9-8.6, but the aggregate is not a universal dependency.
P9-9.4 depends on P9-9.1b and the applicable disabled lifecycle delegate;
P9-9.6 conditionally requires P9-9.1a only where completion/hierarchy is
advertised or explicitly required by a stronger project handoff. Neither
optional capability nor a stronger handoff target is selected by this review.
Completion-off never waives trigger, topology, charge, reset, receipts,
target readmission, crossings, or compatibility. Completion-on without its
scoped child evidence holds that review; unselected completion is not marked
executed. Execute the four independent
disabled transition/state/observable/lifecycle surfaces per supported profile;
retain all forty slots for the ten-profile population.

`P9-9.2` is the parent compatibility register. Each
`P9-9.2-<profile>-<surface>` cell has its own fixture/oracle, exact delegate
identity, execution result, and review disposition. Controlled batching may
share a command but cannot share or infer a cell's acceptance. Unselected
profiles retain pending cells and do not block other fully tested profiles.

Exercise both migration directions and exact legacy delegate execution on
the defined domain. The saturated port-5 conflict must return
`legacy_expansion_target_undefined` atomically in the V4 wrapper. Preserve
GRC9V3 source behavior. An enabled-only implementation cannot claim full
GRC9V4 conformance.

### Tranche 10. Conformance, evidence, and handoff

Close the declared support matrix using actual runtime results with exact
release, code, complete-profile, fixture, pre/poststate, and receipt identities.
Run the relevant existing-family regressions and deterministic replay checks.
Store new runtime vectors and evidence outside the frozen specification
release; link them to its fixture IDs and state any independent oracle method.

Publish capability discovery and a minimal API/replay example for supported
profiles, plus a closeout and handoff. Review every inherited debt and coverage
hold against the claim actually demonstrated. Record outstanding profiles,
analysis, phenomenology, and integration work explicitly. P9-G4 acceptance
requires review of the evidence and support boundary.

## Verification at the planning boundary

Run from the repository root:

```bash
.venv/bin/python implementation/investigations/grc9v4-constitutive-design/scripts/audit_grcv4_specification_release_acceptance.py --audit-file implementation/phase-9-grcv4/verification/inputs/GRCV4-final-narrow-specification-acceptance-audit.md
git diff --check
```

The audit input is the committed byte-identical acceptance evidence with its
original gate-bound SHA-256; all required input bytes are in the repository. That audit
verifies historical release acceptance; its printed implementation flag is
the historical gate's flag. Phase 9's current state comes from its opening
and subsequent accepted records. Until Tranche 1 closes, report the normal
post-D10 verification failure explicitly alongside the passing release audit.

[paper]: ./investigations/grc9v4-constitutive-design/drafts/2026-09-GRC-V4.md
[proposal]: ./investigations/grc9v4-constitutive-design/drafts/GRCV4-proposal.md
[generic]: ../specs/grc-v4-spec.md
[interface]: ../specs/grc-common-interface-v4-ext.md
[g9]: ../specs/grc-9-v4-spec.md
[release]: ../specs/grc-v4-specification-release.json
[acceptance]: ./investigations/grc9v4-constitutive-design/specification/GRCV4SpecificationReleaseAcceptanceGate.json
[fixtures]: ../specs/grc-v4-conformance-fixtures.json
[vectors]: ../specs/grc-v4-conformance-vectors.json
[schema]: ../specs/grc-v4-contract-schema.json
[claims]: ./investigations/grc9v4-constitutive-design/decisions/D10NormativeClaimTopology.json
[d10-2]: ./investigations/grc9v4-constitutive-design/decisions/D10_2FullSubstrateProvenanceAndPromotionAudit.json
[d11-c]: ./investigations/grc9v4-constitutive-design/decisions/D11CCandidateBaselineTransportAndMobilityResolution.json
[d11-g9]: ./investigations/grc9v4-constitutive-design/decisions/D11G9CanonicalExpansionPortAllocationResolution.json
[debts]: ./investigations/grc9v4-constitutive-design/decisions/D10DebtClaimTransformationLedger.json
[routing]: ./investigations/grc9v4-constitutive-design/decisions/D11ClaimDebtAndAuthorityRouting.json
[guide]: ./investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/docs/AgenticQueryGuide.md
