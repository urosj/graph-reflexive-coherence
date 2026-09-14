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

The user's 2026-09-10 clarification makes correct execution on larger, complex
graphs an implementation requirement. Small graphs supply independent equation
oracles; they do not replace graph-general implementation and demonstrated
larger-graph execution. Conservative scientific domain and conditioning checks
remain required. Speed, sparse storage and performance optimization may follow
correctness; throughput or memory-efficiency targets are not the current gate.

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
| `P9-G2[p]`: generic conformance | All applicable runtime/lifecycle cases for exact profile scope p, with independent evidence. | P9-4.8B accepted for one exact C_OS profile; all other scopes pending. See the acceptance record below. |
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

Earlier leaf status: P9-4.5 was accepted on `impl/phase-9-grcv4-tranche-4`; successor entry
remains pending. Accepted predecessor:
P9-4.4 including its audit follow-up at `1752426`, with P9-3.5's
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

A post-acceptance audit found a test-only extreme-saturation defect in `39cfe6a`.
The [P9-4.3 follow-up](./phase-9-grcv4/tranche-4/P9-4.3-AuditFollowup.md) carries
widened derivative arithmetic, explicit range limits and five new regressions.
All 148 focused methods passed in a reconstructed checkout with a fresh
interpreter and changed hash seed. The user has accepted the verified follow-up.
Its index and run retain their validation-time dispositions; this plan and the
commit record the later acceptance. Original evidence and acceptance history
remain unchanged. P9-4.4 stays held.

P9-4.4 entry now binds accepted `4a3a7ee` in the separate
[P9-4.3 acceptance record](./phase-9-grcv4/tranche-4/P9-4.3-AcceptanceRecord.json).
Fifteen leaves and 27 paths are dependency-ready. The
[P9-4.4 review](./phase-9-grcv4/tranche-4/P9-4.4-Review.md) maps one-pass OS,
exact reference-relative split admission, fixed-selector-stratum pressure,
one corrector resource write and final-C reconstruction to the preserved
187-method initial run and 188 passing audit-follow-up methods in a reconstructed
checkout. The audit regression forces both pass and step through equal-endpoint
rank/interior crossings and safe mixed paths; endpoint-only and blanket-rejection
mutations are detected. Production source is unchanged by the follow-up.
The numerical pipeline remains provisional;
operation/lifecycle owners still authenticate and commit live state and receipts.
P9-4.4 has closed its confirmed audit gap and is explicitly accepted by the user
for commit, including the follow-up. Review, execution and run records retain
their validation-time dispositions; this plan and the commit record the later
acceptance. A separately authorized P9-4.5 entry can bind the accepted commit;
P9-4.5 and G2 remain held. Before a commit-ready positive vector, P9-4.5 must resolve
complete poststate reference/pre-read current/domain admission under the frozen
complete-step contract. Consumed-corrector admission does not establish that
reference admission. P9-4.5/P9-4.6 must bind actual request and ledger metadata;
`next_inputs` is numerical continuation only. Final-C current remains excluded
from a second geometry, residual or continuity pass.

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
The draft review's remaining obligations are assigned below to P9-4.9.1–P9-4.9.3,
followed by the successor P9-4.8B review under the same full G2 criteria.

P9-4.5 continuation binds accepted `1752426` in the
[P9-4.4 acceptance record](./phase-9-grcv4/tranche-4/P9-4.4-AcceptanceRecord.json).
Sixteen leaves and 29 paths are dependency-ready. The bounded ordinary-operation
owner and actual positive/atomic-negative vectors are implemented, verified and
explicitly accepted by the user for commit, including all six audit corrections.
All 256 scoped methods pass after exact reconstruction. See the
[review](./phase-9-grcv4/tranche-4/P9-4.5-Review.md)
and [execution record](./phase-9-grcv4/tranche-4/P9-4.5-ExecutionRecord.json).
The lifecycle owner publishes C/clock/receipts together only after final-C consumed
and reference admission, receipt construction and actual request/result binding.
Review, execution and run records retain their validation-time dispositions;
this plan and the commit record the later user acceptance. The local receipt-parent
convention remains provisional. A separately authorized P9-4.6 entry can bind
the accepted commit without promoting ordinary-operation evidence to conformance.
P9-4.6 snapshot/load/reset/rebase and later lifecycle product coverage remain held;
no generic-runtime or specialization conformance is accepted.

P9-4.6 continuation: the user authorized this leaf after accepting P9-4.5.
The [P9-4.5 acceptance record](./phase-9-grcv4/tranche-4/P9-4.5-AcceptanceRecord.json)
binds `ec9f8662d08eafc5346837ddbbb74c9a4359a9b4`. Seventeen leaves and 29 paths
are dependency-ready. P9-4.6 implements actual C_OS snapshot/load/reset/rebase,
compatible current assignment and independent duplication. All 76 focused
methods passed in the reconstructed checkout with no failures/errors/skips.
The user authorized the original commit with the full independent audit
pending; the later combined audit and its findings are recorded below. See the
[review](./phase-9-grcv4/tranche-4/P9-4.6-Review.md) and
[execution record](./phase-9-grcv4/tranche-4/P9-4.6-ExecutionRecord.json).
The `P9-7.1-C_OS` child aliases this evidence without duplicate credit. Snapshots
embed resolved reference/profile content, scientific/reset payloads, ordered
receipts and historical commit preimages. Target current and reset are freshly
readmitted; state and commit preimages publish together. Reset preserves live
clock and lineage; assignment changes only C. The review states the explicit
implementation snapshot layout and local receipt-parent conventions. Full
receipt ownership/replay, events/migrations and profile conformance remain with
their later leaves. The bound review and execution record retain their
verification-time pending-review status; this plan records the later commit
authorization. The later supplied audits, correction and closure are recorded
separately below; the original pending-audit records remain unchanged.

P9-4.7 batch accepted: the user authorized acceptance of P9-4.6, P9-4.7a and
P9-4.7b after closing the combined audit findings. The
[batch record](./phase-9-grcv4/tranche-4/P9-4.7ab-AuthorizationRecord.json)
records that disposition. The [P9-4.6 follow-up](./phase-9-grcv4/tranche-4/P9-4.6-AuditFollowup.md)
closes the deferred audit without rewriting its original records.

The [P9-4.7b review](./phase-9-grcv4/tranche-4/P9-4.7b-Review.md) records the
accepted edge/K4 correction, explicit solver tolerances and orientation/reference
preimages. The successor specification release and packaged assets are active;
the exact published mandatory request/event identity passes in the retained
50-method replay. The earlier 135- and 35-method runs remain reproducible through
Git plus compact reverse patches. Mixed lifecycle pressure includes returning
to the original graph/profile and restoring its archive. P9-7.2a/b and 7.3–7.6
have scoped C_OS evidence reconciled; P9-7.1-C_OS retains only bounded snapshot/
continuation credit. Broader GRC9/reference-carrier correction and generic
parent-DAG conformance remain outside these accepted leaves.

Historical P9-4.8 snapshot: draft **HOLD P9-G2[C_OS]**, pending fixture
reconciliation and user review at that stage. Its
[continuation handoff](./phase-9-grcv4/tranche-4/P9-4.8-Handoff.md) is historical.
The successor [P9-4.8B review](./phase-9-grcv4/tranche-4/P9-4.8B-Review.md)
is now covered by [explicit G2 acceptance](./phase-9-grcv4/tranche-4/P9-4.8B-G2Acceptance.json) for its one exact C_OS nomination.
The [gate review](./phase-9-grcv4/tranche-4/P9-4.8-Review.md) and
[33-case evidence index](./phase-9-grcv4/tranche-4/P9-4.8-GateReview.json)
record unfinished public-interface integration and deferred receipt-parent
authority. Fixture reconciliation is P9-4.8 work; its absent consolidated mapping
is not proof of missing behavior. Reassess the stale-cache case using the existing
second-beat reconstruction test before claiming a new gap. The corrected mandatory
mapped-event execution retains its scoped credit. A_OS and P9-G3[C_OS] stay
behind G2. That snapshot had empty runtime support and 26 leaves / 29 eligible
paths. Current support is the user-accepted exact C_OS singleton; closure work
still has 30 leaves / 29 paths. P9-4.8 remains historical; P9-4.8B acceptance
updates discovery and status without authorizing new runtime leaves.

#### P9-4.9. Closure of the P9-4.8 obligations

P9-4.9 is an aggregate register, not an extra execution or acceptance step.
Its three children (including the P9-4.9.1a interface refinement) are accepted
work packages, not new gates or separate full-review cycles. They close the obligations identified in the
[P9-4.8 handoff](./phase-9-grcv4/tranche-4/P9-4.8-Handoff.md). These are not three
demonstrated runtime bugs: interface integration was unfinished, receipt-parent
authority was unresolved, and fixture sufficiency required reconciliation.
The original P9-4.8 draft HOLD and its evidence remain unchanged.

Use one integrated closure sequence; the IDs identify ownership, not execution
order:

1. Begin P9-4.9.3 with a bounded inventory of the existing review/index and runs.
   Record requirement, usable evidence and its limits, remaining change/test,
   and owning work package in a compact gap list. Stop at an actionable scope;
   do not create another audit framework or repeat suites to discover scope.
2. Resolve P9-4.9.2's parent-authority decision and propagate the accepted
   contract before changing the corresponding runtime behavior.
3. Implement P9-4.9.1 and the demonstrated parent/fixture gaps together where
   useful, adding targeted tests alongside each change. Resolve the narrow
   P9-4.9.1a abundance-interface authority gap before declaring public-interface
   closure. Finish P9-4.9.3 against the completed public interface and parent contract. Reuse unaffected evidence
   within its actual scope; run the necessary integrated checks once the result
   is stable, repeating only checks affected by subsequent corrections.
4. Perform one integrated P9-4.8B review of the actual public interface, parent
   contract and complete-profile evidence. G2 is the acceptance decision; the
   work packages supply its evidence, not additional gate decisions.

This planning addition grants no new runtime permission or support. When execution
is authorized, register the scoped work IDs, dependencies and path owners through
the existing boundary/work manifest, batching related work where appropriate.
Update affected tool exposure/tests if permission behavior changes; do not add
another authorization framework. Preserve the accepted specification release
unless an explicitly reviewed V4 successor is required.

Maintain one current verification path as corrections land. Retain the original
P9-4.8 checker only for historical reconstruction of its bound snapshot, not as
a second evolving acceptance system or a veto on authorized source changes.
The current path now reports the separate P9-4.8B singleton acceptance; the
historical HOLD remains unchanged.

##### P9-4.9.1. C_OS public common/V4 interface closure

Own `G2-COS-INTERFACE`: complete the integration deferred from P9-2.6 and the
P9-4.4/P9-4.5/P9-4.7a consumers. Implement the public `GRCV4(GRCModel)` contract from the
[generic spec](../specs/grc-v4-spec.md), inherited
[common interface](../specs/grc-common-interface.md), and
[V4 extension](../specs/grc-common-interface-v4-ext.md), using the existing
`CandidateCOSOperation` sole atomic publication owner. Do not duplicate live
state, receipt ownership, or numerical authority in the facade.

Cover constructors and restored-instance admission, parameter access, common
state/observable projections with stage tags, exact profile/model discovery,
capabilities, and the specified `step_v4`/`run_v4` and common `step`/`run`
signatures. Verify strict request versus input boundaries, serialized immutable
default requests and typed missing-request failures. Method-name overlap is not
signature or lifecycle conformance. Test zero/subnormal/negative/extreme finite
durations, invalid inputs, atomic failures and restored-instance behavior through
the actual public receiver. Reuse existing numerical and lifecycle tests; evolve
the foundation's stage-local no-facade/export assertions only with the real
integration. Discovery must distinguish registered test targets from accepted
public support; do not advertise G2 before review.

Completion evidence: a spec-to-public-method/test mapping and passing focused integration
evidence for the nominated C_OS scope, including actual lifecycle delegation,
request/result projections and truthful discovery. Receipt-parent conformance
remains dependent on P9-4.9.2; interface completion alone cannot open G2.

Implemented on 2026-09-09 after accepted parent commit `d8f26d9`; bounded
implementation accepted by the user's commit instruction in `7905e7e`. See the
[P9-4.9.1 review](./phase-9-grcv4/tranche-4/P9-4.9.1-Review.md) and its method/test
mapping. The interim abundance semantics below are historical to P9-4.9.1;
P9-4.9.1a supersedes them with accepted availability authority. `abundance` was explicitly unavailable (`null`)
because the accepted V4 sources do not define it; no legacy sink semantics or
new numerical diagnostic is inferred. Verification is focused on this facade
and affected regressions, preserving the accepted parent run at its Git subject.
Final fixture reconciliation and P9-4.8B were separate, now accepted below.

##### P9-4.9.1a. Abundance interface authority closure

The user explicitly accepted the audit-refined
[bounded decision](./investigations/grc9v4-constitutive-design/decisions/P9AbundanceInterfaceAuthorityProposal.md)
on 2026-09-09 and authorized implementation. This resolves availability semantics,
not a numeric abundance functional, and does not reopen Candidate C, OS, charge,
lifecycle, migration/event or receipt-parent results.

The structured source is admitted as an append-only P9 forensic extension, then
propagated through proposal/paper §14.2.1 and the V4 interface/family specifications.
The V4 extension retains the required common name with an explicit unavailable
triplet. `observed_state_digest`, totality with typed conformance failure, and
release-bound diagnostic identity separate from model identity are normative.
No generic/GRC9V4 detector or numeric capability is admitted; common/V3/GRC9V3
files remain unchanged. Public receiver projections use the existing atomic
owner, with no new scientific state, history or trajectory parameter.

The [abundance review](./phase-9-grcv4/tranche-4/P9-4.9.1a-Review.md) maps the focused
checks: real C_OS availability across construction/step/assignment/restore/reset/
profile and graph crossings, detached outputs and failure rollback; explicitly
synthetic numeric-protocol controls; and actual forensic API/notebook/HTTP-handler/
browser-validator identity. Do not describe these as a numeric detector or full
browser/numerical campaign. Reuse the original 14-test facade and parent runs
at their accepted Git subjects; new execution binds the successor release.

Only existing lifecycle/codec/test/packaged-release paths gain P9-4.9.1a work
permission. After focused implementation verification, continue with final
P9-4.9.3 fixture reconciliation and one P9-4.8B G2 review. Neither design acceptance
nor passing scoped tests promotes an accepted runtime support set or G2.

##### P9-4.9.2. Receipt-parent authority and conformance closure

The user accepted the [bounded authority decision](./investigations/grc9v4-constitutive-design/decisions/P9ReceiptParentAuthorityProposal.md)
on 2026-09-09: uniform previous-successful-primary parents, with shared auxiliary
parents and no intra-commit edges. Nine valid symbolic cases and 16 malformed
controls pass; these are design checks, not runtime evidence. The structured
authority/debt record is now admitted by the append-only P9 forensic overlay,
available through API and actual Phase 9 notebook/browser views, and propagated
through proposal/paper §12.5.1 into the V4 successor release. Runtime enforcement
and explicit C_OS v3 snapshot admission are implemented; the
[P9-4.9.2 review](./phase-9-grcv4/tranche-4/P9-4.9.2-Review.md) records validation.
No historical acceptance is rewritten. Facade and final fixture closure remain
P9-4.9.1/P9-4.9.3, followed by the single P9-4.8B review; its later
exact-scope acceptance is recorded below.

Own `G2-COS-PARENTS`: close the P9-2.4 obligation assigned to parent P9-7.6,
beyond the accepted C_OS child's narrower ledger/duplication evidence. Use the forensic API to
establish accepted scope and provenance. In particular,
`D10.2-EC-PARENT-L-ORDERED-RECEIPTS` binds ordered source/target profile identities;
it does not select receipt-parent scope/order. Acyclic receipt/commit/envelope
hash construction is also not a parent-DAG contract.

Resolve the missing convention through the existing investigation/design review,
then propagate accepted authority through proposal/paper and V4 specs before
claiming runtime conformance. Use a reviewed successor release if frozen assets
must change; do not repair older family versions or invent authority in code.
Define historical versus intra-commit scope, roots, ordering and duplicate rules,
including ordinary, administrative and crossing operations. Do not silently
promote or replace the tested local convention merely to make tests pass.

After the authority decision, implement the accepted convention alongside the
facade/gap corrections and convert differences into tests. Exercise
valid roots and interleaved operations, missing/foreign/forward/self/cyclic
references, duplicates and reordered parents, including coherently rehashed
malformed records and snapshot/restoration. Preserve the distinction between
restore plus identical future inputs and authenticated historical execution:
lawful unreceipted `set_state` prevents conflating the two.

Completion evidence: an accepted, source-linked V4 authority decision with aligned paper/spec
and runtime tests, and explicit discharge of the C_OS share of P9-7.6's parent
obligation. Reuse valid local-convention evidence without claiming it previously
proved the missing authority. Other profiles' parent obligations remain scoped.

##### P9-4.9.3. Complete-profile fixture and evidence closure

The initial [gap list](./phase-9-grcv4/tranche-4/P9-4.9.3-EvidenceInventory.md)
is retained as history. The [final reconciliation](./phase-9-grcv4/tranche-4/P9-4.9.3-Review.md)
was accepted in `c01526c`: 33 catalog rows for one exact nominated complete profile, plus the
published dimension negative and mapped event. It follows accepted parent,
facade and abundance implementation (`d8f26d9`, `7905e7e`, `1f5f5e9`).
Control and target identities remain separate. Focused captured execution and
nonnumerical integrity checks replace repeated broad campaigns. This is fixture
closure for review; P9-4.8B alone owns the integrated G2 decision below.

Own `G2-COS-FIXTURES`: reconcile all 33 indexed catalog cases (8 common,
14 Candidate C, 1 OS and 10 lifecycle) against the
[catalog](../specs/grc-v4-conformance-fixtures.json),
[vectors](../specs/grc-v4-conformance-vectors.json) and current public contract.
Nominate a nonempty set of actual complete-profile IDs with their resolved
parameters, graph/reference/context/domain and ordered migration pairs. A family
label or an empty population cannot establish the mandatory fixture product.
Parameter/control variants retain their own identities and evidence scopes.

Map retained executions to the exact inputs, source/release, environment,
command/results and limits they establish. Preserve original run identities;
label any rerun as new evidence. Fill required per-execution result fields,
including fixture/profile/model/parameter identities, pre/poststate digests,
operation/solver dispositions, commit status and emitted receipt IDs. Missing
index credit is not a demonstrated runtime defect: add tests only for actual
uncovered obligations with independently justified expectations, then run the
affected shared/integration checks once the closure surfaces are stable.
Keep commands and retained references portable.

Carry forward the [review's](./phase-9-grcv4/tranche-4/P9-4.8-Review.md)
row-by-row dispositions for all seven schema/semantic negatives, the three-node
algebra witness, canonicalization/identity/subdigest and result/failure vectors.
Keep algebra and schema/codec/comparator credit distinct from live lifecycle
execution. Interpret historical `coverage_holds` against later evidence rather
than copying them as current failures or deleting them wholesale. Preserve
independent candidate/carrier-history decisions, distinct live/reset resources,
reset-only target failures, mixed graph/profile round trips and numerical
charge/increment edge cases in the final evidence mapping.

Resolve both outstanding exact-credit questions explicitly:

- `COMMON-STALE-CACHE`: reconcile the existing second-beat reconstruction test,
  detached/no-cache observations and geometry/stage stale-provenance pressure
  with the nominated public receiver. Establish the allowed rebuild-before-use
  or typed-rejection outcome and that stale values are never consumed; do not
  invent a persistent cache to satisfy a presumed gap.
- `SEMANTIC-REJECT-RESOURCE-TRANSFORM-DIMENSIONS`: execute or identify execution
  of the exact published semantic input at its required validation layer and
  check `resource_transform_dimension_mismatch`. Synthetic crossing shape tests
  and schema validity alone cannot supply that exact semantic-row credit.

Retain the corrected mandatory mapped-event row's exact-input credit and all
seven migration-class dispositions. Unsupported-target negatives and unavailable
source/target positives remain distinct; unavailable sources are not executed
tests. Do not import Candidate A/other-realization positives, GRC9 expansion or
recursive/metamorphic work, the 40 disabled-compatibility cells, or separately
inventoried broader GRC9/K4 builder defects as generic C_OS blockers. Conversely,
none of those deferrals waives an applicable mandatory C_OS case.

Completion evidence: a complete, non-vacuous exact-profile fixture/evidence product, reconciled
against the final P9-4.9.1/P9-4.9.2 surfaces, with demonstrated gaps closed and
remaining out-of-scope dispositions explicit. Passing test counts alone do not
establish this product.

#### P9-4.8B. Successor G2 closure review

**Accepted by the user on 2026-09-09; Tranche 4 is closed.** The
[explicit G2 acceptance](./phase-9-grcv4/tranche-4/P9-4.8B-G2Acceptance.json) binds the unchanged
[integrated review](./phase-9-grcv4/tranche-4/P9-4.8B-Review.md), original
execution, current release and all three satisfied closure obligations.
The accepted generic support set is exactly:

`grcv4-profile-sha256:a6b853ee382895eb78b1a7955a0df22f95d68b27cb0f762503e8c424c2f59b6d`

Global discovery returns that lossless declaration. Locally configured migration
targets are not additional accepted profiles. `P9-7.7-C_OS` is the same gate
result, not duplicate credit. G3, all other profiles and specialization remain
closed; no new implementation leaf is authorized by this decision.
The normal verifier checks the acceptance link and reuses the retained 22-test
run: numerical implementation and evidence remain unchanged, while exact
acceptance/discovery/status changes are separately bound and tested.

Once the integrated corrections and exact-profile evidence are ready, reassess
the original P9-4.8 obligations under the unchanged full `P9-G2[C_OS]` criteria.
Review the three work packages together; do not require three preceding full
acceptance reviews. The parent-authority decision must still be accepted before
its implementation. Preserve the original draft HOLD review/checker and source
bindings. Record a successor review using the single current verification path;
do not turn the old HOLD or historical run into a pass. Reuse the final integrated
execution evidence rather than automatically rerunning it for the review.

Verify exact nominated profile coverage, the public interface, receipt authority,
active release and reproducible execution bindings. Recheck the implementation
boundary and affected tool surfaces, including rejection of incomplete or
misleading acceptance records: missing/duplicate fixture rows, family-label
substitution, vacuous empty-population passes, unreviewed support, borrowed
mapped identities and silently closed lineage debt. Include a valid complete
review control so rejection is not merely a hard-coded HOLD. Mechanical checker
success is not scientific or user acceptance. Record PASS, HOLD or rejection
with reasons; unresolved or newly
demonstrated blockers return to their owning closure child and keep G2 closed.

Only an accepted positive review may update the exact G2 support/discovery scope
and checklist/gate state. `P9-7.7-C_OS` aliases this successor result without
duplicate execution credit; P9-4.8's obligation is discharged by a link to that
result, not rewritten history. A_OS and `P9-G3[C_OS]` still require their separate
continuation/entry review. No broader profile, specialization or release gate
opens merely because the three closure rows or this review have been completed.

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

The user revised the RG2b sequence on 2026-09-10. P9-6.4a/b retain their
two-vertex/one-edge reference constructions and candidate-specific evidence.
New **P9-6.4c** generalizes evaluation and certification to variable-size finite
graphs for both A and C. It must extend the scalar bounds and finite evaluator
to matrix geometry, preserve the complete candidate laws and prove the same
inverse, self-map, contraction, containment and approximation-error obligations.
Removing a size guard alone does not discharge this work. Pressure must include
nonzero A descriptor contrast, C matrix coupling and selector behavior, rich
graph structures, relabeling/reorientation and repeated ordinary beats on
declared admissible larger graphs. Retain the scalar case as a reference oracle
and reuse existing current, writer and validation owners. Record exact graph
sizes, parameters, commands and outcomes; optimization is deferred.

The former unexecuted P9-6.4c shared audit becomes **P9-6.4d**, following the
a/b foundations and c generalization. It reviews A and C separately within one
shared audit, including the generalization's graph coverage and Lipschitz-only
ceiling. P9-6.5 and subsequent RG2b lifecycle/G2 routing must distinguish the
scalar reference result from the generalized result and its d review.
Earlier source crosswalks, debt routing and a/b execution artifacts retain
their execution-time numbering: their shared-audit `P9-6.4c` now routes to d.
The [current checklist](./Phase-9-GRCV4-ImplementationChecklist.md#tranche-6-ci-pc-cipc-and-rg2b)
records this scheduling amendment without changing the scientific sources,
historical evidence or the separate C1-regularity debt.

### Tranche 7. Generic lifecycle generalization and conformance

The [P9-6.5 routing review](./phase-9-grcv4/tranche-6/P9-6.5-Review.md) and
[current record](./phase-9-grcv4/tranche-6/P9-6.5-RealizationRouting.json) reconcile
the eight accepted Tranche 6 numerical results. P9-6.5 was accepted by the user
on 2026-09-10, closing Tranche 6. The user subsequently authorized the complete
P9-7.1 parent on branch `impl/phase-9-grcv4-tranche-7`, not only the handoff's
first suggested A_OS child.
The records supply concrete seed
identities and pending family routes, preserving the historical P9-1.4 register.
Exact lifecycle/profile-pair/event scope must be bound before child execution;
the routes themselves add no runtime permission or generic support.

P9-7.1 binds ten concrete family children: A/C × OS, CI, RG2b, PC, CI+PC.
Use one shared lifecycle/commit owner and the already accepted provisional
numerical owners. Reuse C_OS acceptance as historical exact-scope evidence,
and check compatibility of its existing v3 snapshot route. The other nine
children bind their exact graph/profile/reference, explicit A backend where
applicable, distinct live/reset C/W/Z and deterministic fixture recipe in the
[7.1 record](./phase-9-grcv4/tranche-7/P9-7.1-Lifecycle.json).
Save/load/replay, ordinary-step reset, rebase, independent duplication and
fresh current/reset readmission belong to this batch. No stored CI root,
RG2b section, PC geometry or derived C sector becomes authoritative history.
Migration/event reset tests belong to 7.2–7.5; they are not silently counted
as 7.1 work. Each new child requires its own reviewed evidence; the ten concrete
children below are now accepted. No all-parameter/graph conformance or G2 promotion.

Implementation status: all ten concrete children are implemented and verified
in the [7.1 review](./phase-9-grcv4/tranche-7/P9-7.1-Review.md): 26 focused tests,
retained source-exact evidence, and API/notebook/browser checks passed. The user
accepted this batch and its audit corrections on 2026-09-11 by authorizing the
commit; no later lifecycle or support gate was opened.

The independent 7.1 audit requires separating RG2b state readmission on K
from ordinary entry on K_minus, validating zero-step own-operation identity
and exact frozen RG2b historical clocks, and correcting non-OS reconstruction
labels. Include the native A post-writer rollback witness with a populated
ledger, lawful assignment/zero-step controls, large-clock rounding and rejection
outside the core domain. Nine focused audit methods plus six compatibility
methods bind a new [correction record](./phase-9-grcv4/tranche-7/P9-7.1-AuditFollowup.json);
preserve the original run and recover its source bytes with compact reverse
edits. All 15 correction/compatibility methods passed with source stability;
no numerical realization or scope/gate change. User acceptance includes these
corrections; execution records retain their original pre-acceptance flags.

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

**Current disposition: P9-7.2a accepted and closed on 2026-09-11.** The
[acceptance](./phase-9-grcv4/tranche-7/P9-7.2a-InitializerRuntimeReview.md)
covers the seven reviewed migration classes, including all five C→A target
realizations and the final codec-reference correction. Historical execution
records remain unchanged. P9-7.2b is next planned work, not started by closure;
no broader G2/G3 or specialization support is granted.

**P9-7.2b contract preparation:** the user authorized the narrow
[mapped-event fallback binding](./phase-9-grcv4/tranche-7/P9-7.2b-ContractExtension.md).
The additive [specification](../specs/grc-v4-topology-event-spec.md) reuses the
accepted A initializer on independently mapped current/reset inputs, separates
fresh initialization from W/Z loss, and versions event receipts/snapshot
applicability without changing 7.2a. The user accepted the corrected contract
and separate representation-operation scope on 2026-09-12. Closed fallback
schema/wire checks pass; successor packaging remains before runtime execution. The
paper already permits this fallback; no new scientific claim, lossless history
map, specialization grant or numerical execution is inferred. P9-7.2b remains
open, with exact execution children and pressure listed in the binding review.

The subsequent user-approved scope update includes **pure representation
transport now**, as a separate operation from reconstruction. Its coordinate
law, source/target correspondence and no-loss boundary are specified in the
[representation contract](../specs/grc-v4-topology-event-spec.md#pure-representation-transport-current-contract-scope).
Complete its own closed wire/release binding before implementation; require
inverse/covariance/current-reset/rollback/replay checks separately from fallback
tests. Current schema examples prove neither this operation nor full 7.2b
closure. Genuine topology-history transport stays deferred, with isolated
zero-resource vertex addition and explicit existing-edge lineage identified
as the next bounded contract candidate, not silently admitted support.

The subsequent [wire/package follow-through](./phase-9-grcv4/tranche-7/P9-7.2b-PackageBinding.md)
completes representation request/receipt/archive shapes and jointly packages
both contracts. The additive decoder checks installed assets, explicit release
selection and graph-map declarations; it is not a numerical/lifecycle owner.
Next instantiate the exact execution children and implement operation-specific
dispatch/readmission/replay. No old release, initializer run or G2/G3 support
is reclassified by contract packaging.

The package audit's R1/R2 clarifications now bind exact coordinate-action zero
delta (not equality of rounded charges) and a singleton representation primary
with embedded charge/history evidence. Runtime tests must separately establish
inverse scientific/reset recovery without ledger rollback, identity transport
versus identity reconstruction on nontrivial histories, and preserving migration
→ representation → evolution → lossy event → restore/reset. Include the
charge-order witness, signed-zero controls and incompatible reference/backend/
context/chart targets despite valid graph maps. Contract tests are not runtime
acceptance. The user accepted the corrected contract package on 2026-09-12
through “commit changes”; runtime implementation and aggregate closure remain open.

The subsequent user request authorizes the full two-operation implementation.
[P9-7.2b runtime review](./phase-9-grcv4/tranche-7/P9-7.2b-RuntimeReview.md)
records explicit reconstruction and representation APIs, versioned replay,
variable-size receipt groups and the finite execution roster. Runtime code is
implemented; retained verification and independent review remain separate from
user acceptance and aggregate closure. No additional support gate is opened.
The runtime audit's F1/F2 corrections preserve continued joint-archive admission
and the declaration/programmer-error boundary. Eight native audit regression
methods join the ten original runtime tests; a separate correction capture
retains the original source subject instead of relabeling its evidence.
The user accepted and closed P9-7.2b on 2026-09-12 through “accept and commit
7.2b”, including those corrections and the 18-test run. The runtime review
records acceptance separately from historical execution flags. P9-7.3 onward
and wider G2/G3 support remain outside this closure.

P9-7.3 is a separate verification of candidate/carrier policy independence,
directional losses and whole-current/reset resource/charge accounting. Its
[bounded review](./phase-9-grcv4/tranche-7/P9-7.3-Review.md) distinguishes 32
discrete declaration cells from five native crossing witnesses and separate
representation, hostile-history and charge pressure. Reuse accepted 7.2
numerical owners without changing their evidence or claiming all-pair admission.
The user accepted and closed P9-7.3 on 2026-09-12 following two passing audits,
including a separately reported independent native rerun. The user then asked
to execute the three suggested stronger regressions before commit; all three
passed in a separate record with no runtime changes. The original six-test
run is unchanged; 7.4–7.6 and G2/G3 stay separate.

P9-7.4 adds [bounded target-reference verification](./phase-9-grcv4/tranche-7/P9-7.4-Review.md)
over the accepted runtime: malformed stable-edge C maps at reference construction,
both-role numerical admission before publication for all five C realizations,
a changed-graph target checked against independent dense equations, and
reset-only domain/late-publication rollback. The user accepted and closed this
bounded scope on 2026-09-12 following a passing independent audit and reported
native rerun. Acceptance is projected over the unchanged original execution,
not a new transport law or runtime permission.
The broader failure-sequence and receipt-lineage tasks stay with 7.5 and 7.6;
all earlier evidence, public support and G2/G3 boundaries remain unchanged.

P9-7.5 adds [mixed-prefix failure/reset verification](./phase-9-grcv4/tranche-7/P9-7.5-Review.md)
over the accepted numerical owners. It exercises distinct live/reset authority
after ordinary evolution, migration and events; literal transported targets;
persistent ledger versus emitted receipt delta; absent crossing/receipt evidence;
invalid runtime maps/history; and reset-only readmission rejection after a
successful mixed prefix. Invalid C reference construction remains covered by
7.4: no fabricated invalid typed registry entry is needed to exercise rejected
target selection or invalid operation maps. The user accepted and closed P9-7.5
on 2026-09-12 after the passing independent audit and reported native rerun.
Acceptance is projected over the unchanged execution; no parent-DAG or arbitrary
profile/graph conformance is inferred.

P9-7.6 adds [receipt-lineage and duplicate-ownership verification](./phase-9-grcv4/tranche-7/P9-7.6-Review.md)
under the already accepted P9-4.9.2 uniform previous-successful-primary rule.
Exercise mixed four-receipt and singleton representation groups, coherently
rehashed invalid parents, ledger partition rejection, prospective crossing
publication rejection, unreceipted assignment and independent mutable forks.
Keep symbolic self/cycle pressure distinct from real content-hashed executions;
shared fork content IDs do not imply shared mutable ownership or authenticated
uninterrupted history. The user accepted and closed this bounded scope on
2026-09-12 following the passing independent audit and reported native rerun.
Project acceptance over the unchanged source/authority-bound execution through
existing status surfaces. P9-7.7/G2 and P9-7.8/G3 remain separate; no runtime,
scientific authority or accepted execution evidence is rewritten.

The following records the historical implementation and acceptance sequence.
The user authorized **P9-7.2a** after accepting 7.1 at `5d8dbe2`. Its
[scoped review](./phase-9-grcv4/tranche-7/P9-7.2a-Review.md) binds 13 concrete
source/target pairs in six source-backed classes, not a Cartesian family-wide
claim. Same-candidate nonhistory changes preserve W where present; entry to
persistent history initializes Z to canonical zero; exit archives/drops Z;
PC↔CI+PC preserves Z only under identical carrier contracts. A→C explicitly
drops W, rederives C authority and drops/zeros incompatible carrier history.
Each map applies independently to current and reset with unchanged resource,
charge target and clock; the existing target numerical owner readmits both.
Bind actual before/after/reset/continuation endpoints, channel-specific history
digests/losses, seeded lineage, snapshot/backend reconstruction and atomic failure.

The seventh class, **C→A**, has no admitted target reference-current initializer
source in the accepted [P9-5.4 review](./phase-9-grcv4/tranche-5/P9-5.4-Review.md).
Record real-consumer rejection pressure as `P9-7.2a-C_TO_A_UNRESOLVED`, not as
positive completion. Do not choose a flux source, supplied W or zero seed
editorially. At that six-class execution subject, positive C→A and aggregate
7.2a closure remained pending a source-backed
resolution for both current and reset; acceptance of six classes cannot waive it.
The scoped successor checks the new run and Git-preserved 7.1 evidence without
replaying historical numerical campaigns. Generic events, wider G2 and G3 remain
separate; no paper/spec/claim authority is changed by this implementation.

Scoped verification completed: 25 focused tests (13 positive pairs, nine
negative/rollback methods, three legacy checks), five read-only evidence
controls, 35 browser-validator tests and actual API/notebook/browser checks
passed. The user accepted this finite scope and its audit corrections by the
commit request recorded at `924fca9`; positive C→A and aggregate closure remain
pending. Capture-time acceptance flags stay unchanged in historical records.

The subsequent independent audit requires two bounded lifecycle corrections:
typed semantic exception classification (F1) and consistent commitments for a
known/repeated scientific identity (F2). Apply the same temporary lookup to
import and prospective publication, including archived endpoints and known
target clocks; do not impose uninterrupted adjacency or attest external
history. Add distinct-A-backend migration/restoration/continuation pressure.
Preserve the original 25-test subject with exact source recovery and bind a
separate focused correction capture. No migration law, numerical owner,
scientific authority, C→A obligation or G2/G3 scope is changed.
The seventeen-method correction capture passed. Stop at the bounded fixes and
minimal record consistency; defer aggregate 7.2 closure while C→A remains open.

The user subsequently authorized a concrete
[C→A initializer-source proposal](./investigations/grc9v4-constitutive-design/decisions/P9CandidateAInitializerReferencePassProposal.md).
It is a bounded successor definition inside P9-7.2a, not a new tranche or an
accepted reinterpretation of D10. Select for review one target-only reference
pass: fixed target differential recipe → auxiliary `G_W(C, 0)` → reference
potential/baseline flux → unchanged full `G_W(C, J_ref)`. Keep auxiliary W,
retained W and reference geometry separately typed; specify numerical rounding,
floor/range failures and identity before implementation. No implicit fixed-point
solve, supplied-flux provenance shortcut, source history or extra ordinary beat.

The initial draft registered source-rule debt and an optional Candidate A
construction claim; the user accepted the clarified policy at `49b83ba`.
Its [structured admission](./phase-9-grcv4/tranche-7/P9-7.2a-InitializerAuthority.md)
now exposes that optional claim, design-resolved debt and still-forward
obligations through the side tool. The user accepted the GRCV4-proposal revision
at `448e420`, then accepted the paper through the commit-and-continue request
on 2026-09-11 (`7d45218`). The V4 specification supplement is now prepared for
accepted implementation, beginning with its successor release. Generic and exact GRC9V3 initializer
bindings remain separate; no older family changes. Preserve P9-5.1/P9-5.4's
accepted conditional-constructor scope and the existing migration records.

Implementation follow-through must use one graph-generic producer with distinct
current/reset executions and real target admission for A_OS, A_CI, A_PC,
A_CI+PC and A_RG2b. Exercise active descriptor/current channels, both gamma
signs, graph/order controls, source-history independence, floor/rounding/range
edges, reset-only failures, restoration and F1/F2 publication consistency.
No all-parameter guarantee or Cartesian source/target campaign is required.
Use focused changed-path evidence and the existing verifier/API/notebook/browser
surfaces; review aggregate 7.2a only after the positive seventh class exists.
Design preparation/review and structured authority admission are complete.
GRCV4-proposal §12.6 and its related crosswalks are accepted by the user.
The paper now incorporates that content and is user-accepted. The
[specification supplement](../specs/grc-v4-a-initializer-spec.md), closed schema
and wire examples are user-accepted at `f7962e4`. The additive successor package,
shared producer and five-target C→A integration are now implemented; see the
[runtime review](./phase-9-grcv4/tranche-7/P9-7.2a-InitializerRuntimeReview.md).
Its own focused record binds the new execution. Aggregate acceptance remains separate.
The user accepted this runtime implementation through the accept-and-commit
request on 2026-09-11, authorizing the final aggregate review next. Its runtime
review records acceptance separately from the immutable capture-time flags.
The same review-stage validator retains released proposal/paper bytes at
`f36b3ba`, checks the accepted proposal at `448e420` and paper at `7d45218`,
and separately binds the exact six-file spec candidate. Released generic and
interface specs/registry retain their historical bytes; the base schema, other source
members, old generators, predecessor runtime assets and old codec pins remain unchanged; the old
release builder is reconstructed only on its original source subject. No draft
revision grants a new executable release or retroactive runtime evidence.

The existing migration `--check` now also validates the additive initializer
package and source-bound runtime record, without executing numerical tests.
Only explicit initializer runtime paths evolve past the historical migration
subject; the new record binds their exact current bytes. API/notebook/browser
status presents the later aggregate acceptance separately from the unchanged
execution records and design-stage forensic projection. The scoped checker
preserves exact source identities across the codec-reference correction;
closure is not a wider support grant or an event implementation.

The supplied design review passed with refinements now incorporated: retain the
existing unit-vertex pairing and admitted boundary/normalization scope; forbid
auxiliary total-current admission even when `CandidateACurrent` is a convenient
baseline source; keep static policy/profile identity upstream of output-bearing
construction records; derive reset-only failures from actual reset inputs; and
keep target PC/CI/RG2b charts fixed. Restore initialized crossing endpoints,
not a fictitious initializer constraint on ordinarily evolved W. Retain the
auxiliary-singular/final-reference-regular fixture as an explicit regression;
one native primitive check confirmed its rounded operands but is not migration
evidence. The user subsequently accepted the clarified design by requesting its
commit and continuation on 2026-09-11. Producer choice is now resolved; binding,
propagation and runtime evidence remain, not another mathematical source-rule
search. Source admission is now complete, with actual API/notebook/browser
access and no runtime permission change. The current scoped checker preserves
the 25/17-test subjects and their 7.1 predecessor using batched Git reads;
those are historical executions, not new producer evidence.

P9-7.7's [exact-profile review](./phase-9-grcv4/tranche-7/P9-7.7-Review.md)
reconciles all ten rows against the 305-cell catalog product. C_OS preserves
its 33-cell accepted alias. That original review held nine new exact 7.1 seed nominations
for result/endpoint reconciliation, not rejected numerical implementations:
272 cells were then uncredited as a full exact product. In particular, all five
A reconstruction targets and C_RG2b's target differ from their lifecycle seed
IDs. Retain each identity and ordered pair instead of joining family labels.
The bounded checker links existing witnesses, preserves original run identities
and reports zero new execution credit. Close `G2-EXACT-PRODUCT`,
`G2-ORDERED-ENDPOINTS` and `G2-INTEGRATED-REVIEW` separately for each held child;
recover exact retained assertions first and execute only genuinely uncovered
cases. A_OS may be the first continuation. Do not automatically rerun the
entire numerical campaign or widen public support. Review acceptance and
P9-7.7 closure remain pending; G3 is separate.

The first continuation, [A_OS local reconciliation](./phase-9-grcv4/tranche-7/P9-7.7-A_OS-LocalReview.md),
captures 21 local cells for the unchanged 7.1 nomination using three focused
methods and existing scalar/logarithmic oracles. Preserve required result fields,
actual stage outputs, labeled fault controls and distinct chi/zeta control IDs.
The initial 305-cell review remains a historical snapshot; the local execution
is a separate progress record, not a replacement or new G2 acceptance. Seven
crossing cells remain. The event/initializer target changes writer coefficients
and history policy, so bind its exact identity rather than joining on A_OS.
Next reconcile those ordered endpoint/history/reset/readmission cases; no broad
numerical rerun or public support promotion follows from local verification.

The [A_OS crossing continuation](./phase-9-grcv4/tranche-7/P9-7.7-A_OS-CrossingReview.md)
now links the seven remaining obligations: five unchanged retained aliases and
six focused execution cases in three methods. Preserve the literal seven-class
disposition matrix: positive exact nominated endpoints, separate PC↔CI+PC pairs,
and negative C→nominated-A admission versus positive differently identified
initializer targets. All seven obligations have evidence/dispositions, not an
all-pairs execution claim. Integrated applicability review must decide the
supported endpoint scope before G2 acceptance; no mandatory positive row is
silently waived. Existing records and the 21-cell local capture remain unchanged.
The user accepted this bounded A_OS local/crossing reconciliation on 2026-09-13
through “accept and commit.” Record that decision separately from captured
execution flags; integrated G2 review and aggregate P9-7.7 closure remain open.

The [integrated A_OS G2 review](./phase-9-grcv4/tranche-7/P9-7.7-A_OS-G2Review.md)
now proposes PASS for the original exact nomination. Its 28-case index joins
unchanged local/crossing evidence and one focused zero-duration facade method;
no numerical campaign is rerun. The seven-class applicability decision retains
unselected incoming C→A rejection and separate PC/initializer endpoints without
all-pairs support. The user separately accepted this exact G2 scope on
2026-09-13 through “accept and commit”; see the [acceptance record](./phase-9-grcv4/tranche-7/P9-7.7-A_OS-G2Acceptance.json).
Discovery now exposes exact C_OS and A_OS declarations. Original review/run
records remain unchanged, with a finite byte-bound discovery source-reuse
record. Eight profile gates and aggregate P9-7.7 remain open; A_CI reconciliation
is next. No all-pairs or G3 acceptance follows.

Exercise missing lineage, invalid reference maps, readmission failure, and
receipt ownership. `P9-G2[p]` is available only for profiles whose full
applicable fixture product has executed. Keep other planned profiles pending.

The [A_CI local continuation](./phase-9-grcv4/tranche-7/P9-7.7-A_CI-LocalReview.md)
now captures 21 of its 28 catalog cells for the original exact nomination,
pending review. Three methods cover native common/lifecycle operations and
independent implicit-root/writer equations; the local contraction certificate
does not grant global root uniqueness. The subsequent
[crossing reconciliation](./phase-9-grcv4/tranche-7/P9-7.7-A_CI-CrossingReview.md)
links all seven crossing rows through five retained aliases and six new cases
from three focused methods. Preserve exact incoming versus outgoing scope,
the separate initializer/event target and the negative incoming C boundary.
Review the combined bounded reconciliation before integrated applicability/
public-facade G2 review and separate acceptance. Public discovery remains the
exact C_OS/A_OS pair; neither all-pairs nor G3 support is inferred. Status
exposes `a_ci_crossings` without changing the historical local coverage snapshot.

The user accepted the bounded A_CI local/crossing reconciliation on 2026-09-14,
explicitly reserving A_CI G2 review for later. Project that decision separately
over the unchanged execution records. Next is integrated applicability and
public-facade review, not a discovery/support update or another numerical rerun.

The [integrated A_CI G2 review](./phase-9-grcv4/tranche-7/P9-7.7-A_CI-G2Review.md)
is now a PASS proposal for the exact 28-cell product and declared finite
crossings, supplemented by one zero-duration interface method. Preserve CI
local-root/contraction scope, separate initializer targets and non-applicable
PC-pair dispositions. Independent review and explicit G2 acceptance remain.

Alongside that review, [ProfileG2Registry.json](./phase-9-grcv4/tranche-7/ProfileG2Registry.json)
introduces shared acceptance plumbing: immutable historical C_OS/A_OS adapters,
one common new-profile acceptance schema, pinned review/declaration identities,
stable predecessor support and discovery equality for every accepted entry.
Only accepted records contribute public support. API/notebook/browser expose
both accepted and proposed records using the same roster; the browser renders
exact IDs and decision states. Scientific checks remain profile-specific;
runtime leaf permissions, old evidence and production numerical code do not
change. Validate scoped record/authority mutations and the current surfaces,
without repeating the accepted local/crossing numerical campaigns.

The user then accepted exact A_CI G2 on 2026-09-14. The common acceptance record
binds reviewed checkpoint `fa94cd2`; exact public support is now C_OS/A_OS/A_CI.
Preserve all original records and use a finite source-reuse successor for the
discovery/assertion changes. No runtime permissions, initializer endpoints,
global CI branches or arbitrary ordered pairs follow. Seven profile decisions
and aggregate P9-7.7/G3 remain open. At the next matching profile, evaluate
sharing bounded local/crossing presentation checks as the review suggested;
this does not reopen the accepted scientific product or block A_CI G2.

The next [C_CI local reconciliation](./phase-9-grcv4/tranche-7/P9-7.7-C_CI-LocalReview.md)
captures 26 of its 33 obligations through four focused methods. Keep the
nomination's zero mobility deformation distinct from a separately declared
nonzero-deformation, noncommuting derivative control. C baseline, selector,
potential and read-back are checked against independent equations; CI current,
reset and post-continuity restart are independently admitted without A history
or a writer. The local certificate is not global root uniqueness. Seven
crossing obligations and integrated G2 remain separate; review the bounded
local result first. C_CI adds no public support at this stage.

Local/crossing presentation now uses pinned expected views in the existing
profile registry, shared by Python and the browser. This removes repeated
profile-specific display branches, not the scientific checkers or historical
record shapes. Missing, altered, unsupported and unverified views fail closed.

The [C_CI crossing continuation](./phase-9-grcv4/tranche-7/P9-7.7-C_CI-CrossingReview.md)
now reconciles the remaining seven rows through five retained migration aliases
and five new cases in three methods. Explicitly distinguish nomination source
from nomination target, separate PC-pair applicability, and newly declared
initializer/event target identities. The renamed C target supplies its complete
reference map before independent live/reset numerical admission. The combined
26+7 bounded reconciliation was accepted by the user on 2026-09-14; integrated G2 review and
its explicit acceptance are still separate. The original local snapshot is
unchanged; `c_ci_crossings` reports the continuation through the shared registry.

After committing bounded acceptance as `565418a`, the
[integrated C_CI G2 review](./phase-9-grcv4/tranche-7/P9-7.7-C_CI-G2Review.md)
is a PASS proposal for all 33 obligations and the declared ordered endpoints.
One zero-duration public-facade supplement adds no positive-step numerical
credit. Original local/crossing runs and all earlier acceptances remain intact.
The user accepted exact C_CI G2 on 2026-09-14, binding reviewed checkpoint
`8ec744e` in the [acceptance](./phase-9-grcv4/tranche-7/P9-7.7-C_CI-G2Acceptance.json).
Discovery now publishes exactly C_OS/A_OS/A_CI/C_CI. Original proposal and
execution bytes remain unchanged; finite source comparisons account for
discovery/assertion changes only. Six other profile gates, all-pairs, aggregate
P9-7.7 and G3 remain open; no numerical law or runtime permission changes.

This fourth G2 profile also closes the remaining Python dispatch seam. Pinned
registry materializers define the ordered local/crossing/G2 calls and required
dependencies. The entry point publishes their complete checked result and tracks
its keys for generic late-failure cleanup. Module names never come from status
input; source bindings and import origins are checked. Scientific equations and
historical record schemas stay in their separate checkers. Validate orchestration
with focused mutations and one actual cross-surface check, not numerical reruns.

The user selected persistence-first reconciliation: A_PC → C_PC → A_CI+PC →
C_CI+PC → A_RG2b → C_RG2b. This reuses carrier ownership/transport checks before
coupled implicit history, leaving the distinct frozen-completion/finite-section
work last. It changes no scientific gate or evidence requirement.

The [A_PC local continuation](./phase-9-grcv4/tranche-7/P9-7.7-A_PC-LocalReview.md)
now verifies 21 exact local cells in four passing methods. Distinguish supplied W from formation, old Z from
prospective Z, held-source carrier writing from post-continuity A writing, and
native release from reset/drop. Use a same-profile signed-history companion and
independently declared zero controls; retain exact current/reset readmission and
whole-publication rollback. Reuse accepted numerical owners and capture only the
missing exact product. The subsequent
[crossing reconciliation](./phase-9-grcv4/tranche-7/P9-7.7-A_PC-CrossingReview.md)
closes the remaining seven evidence cells through seven retained aliases and
five new cases in three methods. Exact PC↔CI+PC pairs preserve both histories;
changed carrier contracts reject. Independent event current/reset initialization
and readmission distinguish explicit W/Z loss from native release. Incoming
C→A nomination evidence is negative, with the positive initializer target kept
separate. All 28 cells are reconciled, not all ordered pairs executed. Combined
review/acceptance and integrated G2 remain separate; public support stays
C_OS/A_OS/A_CI/C_CI. On 2026-09-14 the user accepted the combined bounded
local/crossing result and requested its commit before integrated G2 review.
Project that acceptance separately without rewriting the original run flags.
The [integrated A_PC G2 review](./phase-9-grcv4/tranche-7/P9-7.7-A_PC-G2Review.md)
then reconciles all 28 cells, exact ordered carrier/history contracts, typed
contract/debt ceilings and one zero-duration facade supplement. Add a proposed
registry row/materializer only; four existing accepted declarations remain
unchanged. Native release, explicit loss and independent current/reset admission
stay distinct; no matched-forcing contraction or base-chart invariance is inferred.
G2 acceptance is still a separate decision.
The user then accepted exact A_PC G2 on 2026-09-14. The common acceptance
record binds checkpoint `b4909a3`; discovery now publishes exactly
C_OS/A_OS/A_CI/C_CI/A_PC. Preserve proposal and execution bytes and use finite
source comparisons for discovery-only changes. Controls and initializer/event
targets do not become supported. C_PC is next; five other G2 decisions,
all-pairs, aggregate P9-7.7 and G3 remain open.

The next [C_PC local reconciliation](./phase-9-grcv4/tranche-7/P9-7.7-C_PC-LocalReview.md)
verifies 26 local cells in five native methods. Rebuild the full C baseline
at old-Z geometry and both independent readmission targets; forbid A-history
state/writers and post-continuity source refresh into the held ZOH write.
Separate native release from reset/drop, fixed-stage dense derivative controls
from nomination execution, and carrier envelopes from stronger trajectory claims.
Expose the local product through the shared registry only. The subsequent
[C_PC crossing reconciliation](./phase-9-grcv4/tranche-7/P9-7.7-C_PC-CrossingReview.md)
addresses the remaining seven cells through seven retained aliases and four new
cases in three methods. Preserve exact carrier transport for PC↔CI+PC, explicit
loss/drop/reset channels, and the distinct C→A initializer target. A changed-edge
C event independently rederives both target baselines before publication; changed
carrier contracts and reset-only resource admission failures reject atomically.
All 33 cells are reconciled, not every ordered pair executed. Bounded acceptance
and integrated G2 remain separate; public support stays five. On 2026-09-14 the
user accepted the combined bounded result and requested its commit before G2.
Preserve original execution identities and project this decision separately.

The [integrated C_PC G2 proposal](./phase-9-grcv4/tranche-7/P9-7.7-C_PC-G2Review.md)
uses accepted checkpoint `b90bb9e`: 33 unique catalog cells, exact ordered
contracts, optional initializer and D11-C/PC authority, plus one zero-duration
facade supplement. The complete C baseline is rederived at each target role;
no A-history state/writer or mobility transfer from structural Hodge is inferred.
Register one proposed common-adapter row, not a sixth accepted declaration.
G2 acceptance, all-pairs and G3 remain separate; old numerical campaigns are reused.
The user subsequently accepted exact C_PC G2 on 2026-09-14. The acceptance binds
review checkpoint `06475b2`; discovery publishes C_OS/A_OS/A_CI/C_CI/A_PC/C_PC.
Preserve original records and finite source comparisons. Controls and other
targets are not support additions; four other G2 decisions, all-pairs and G3
remain separate.

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
