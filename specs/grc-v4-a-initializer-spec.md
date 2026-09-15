# GRCV4 Candidate A target-reference-pass specification

Status: **specification candidate awaiting review**. The producer design,
proposal and paper are accepted; this payload binding is not yet a packaged
executable release or a claim of positive C→A migration.

## Authority and applicability

This V4-only supplement implements [paper §12.6][paper] and its
[accepted proposal crosswalk][proposal], following the
[accepted design][design] and [structured authority][authority]. Its claim is
`P9-7.2a-CL-O-INIT-001` (optional); its contract is
`P9-EC-A-INITIALIZER-REFERENCE-PASS` (required for this selected policy).
`D10.2-EC-PARENT-L-A-INITIALIZER-GRC` retains its historical
`indeterminate_requires_review` association. No D10/D11 claim is rewritten.

The policy is common to A_OS, A_CI, A_PC, A_CI_PC and A_RG2b. It adds no eleventh
profile family. The [generic specification](grc-v4-spec.md) owns existing
candidate, realization, charge and lifecycle admission. This supplement owns
only the selected initializer and its construction provenance. It does not
change older families, generic events, or the exact GRC9V3 initializer binding
in [paper Appendix A.9][specialization].

The [closed supplement schema](grc-v4-a-initializer-schema.json) imports the
released base schema without altering its definitions. All **must** and
**must not** requirements below apply when this policy is selected. Unknown
recipes, versions and fields reject; schema acceptance is not semantic or
runtime admission.

## One-pass producer and numerical contract

Inputs are the fixed target graph/order/orientation, complete A profile,
reference geometry, context, differential recipe and target nonnegative $C$.
They must be reconstructible before either current/reset invocation. No source
$W/Z$, source flux, descriptor cache, source solver result or unresolved output
$W$ is an input. Fixed differential/reference weights must not be replaced by
auxiliary or initialized conductance.

With $B$ positive at the tail and negative at the head, rebuild $D(C)$ and use

$$
E_e=-\frac{\alpha}{2}(C_u+C_v)
-\frac{\beta}{2}\lVert D_u-D_v\rVert^2,
\qquad W_e^{\mathrm{base}}=\max(W_{\mathrm{floor}},\exp E_e),
$$

$$
\Phi^{\mathrm{base}}=\kappa_c B\operatorname{Diag}(W^{\mathrm{base}})B^\top C
-V'_{\mathrm{site}}(C;U),
\qquad J_{\mathrm{ref}}=-\eta\operatorname{Diag}(W^{\mathrm{base}})B^\top\Phi^{\mathrm{base}},
$$

$$
W_{A,e}^{\mathrm{init}}=
\max\left(W_{\mathrm{floor}},\exp\left[E_e-\frac{\gamma}{2}J_{\mathrm{ref},e}^2\right]\right).
$$

Exactly one reference pass is permitted. There is no fixed point, root search,
extra beat or reference-neutrality requirement. The auxiliary stage must not
construct `CandidateACurrent`, solve total current/Read-Back or impose a target
realization W chart. Only its prescribed arithmetic must admit. Whole-target
readmission is required on the final initialized states, using actual target
geometry and gains and the existing realization owners.

The initial recipe fixes unit-vertex pairing, closed-no-flux boundary,
unnormalized vertex stiffness, nondimensional reference units, the existing
host-frame WLS backend and constant-zero context/zero site derivative. This is
not arbitrary quadrature, site, boundary or GRC9 differential support. No
conductance coefficient is required to vanish or have a favorable sign.

The binary64 recipe preserves the exact boundaries in paper §12.6.2:

1. Validate finite typed inputs and nonnegative resources; solve the fixed WLS
   normal equations exactly from binary64 inputs, rounding gradient outputs.
2. Accumulate the combined auxiliary exponent exactly from coefficients,
   resources and rounded descriptors, round once, then apply existing `math.exp`
   and the positive floor, including the far-negative floor branch.
3. Round each $\eta W_e^{\mathrm{base}}$ once, nearest/ties-to-even. Nonfinite
   or nonpositive mobility, including underflow to zero, rejects without repair.
4. Accumulate each full potential component exactly from rounded auxiliary W
   and the declared inputs, then round once. No partial edge rounding or new
   gauge projection is permitted.
5. Using rounded potential and mobility, accumulate each incidence difference
   and product exactly, then round flux once. Retain subnormals; signed
   potential/flux underflow may yield canonical positive zero.
6. Recompute the final combined exponent from the **original unfloored**
   alpha/beta channels and rounded reference current, then round once and
   evaluate the unchanged conductance law. Adding to rounded E, taking
   `log(W_base)` or multiplying floored W_base by a current factor is forbidden.
   Validate positive finite final W and mobility before target admission.

Intermediate range failure rejects at its actual stage even if a later
symbolic expression could be finite. No clipping, extra mobility floor,
log-domain substitute or fallback current is admitted. Platform `math.exp`
is not a cross-platform correctly-rounded guarantee; execution evidence must
bind source/environment and exact inputs/outputs, using portable references.
Parallel edges contribute separately; loops have zero flux but both endpoint
occurrences in E. Isolates acquire no artificial transport. Signed reorientation
and permutations follow declared coordinates; frame covariance remains bounded
by the admitted isometric comparison/backend, not bitwise rotation invariance.

## Closed identities and payloads

All payloads use the existing I-JSON/JCS codec rules: reject duplicate keys,
nonfinite numbers, negative zero, unsafe integer values, coercions and unknown
load-bearing fields. Ordered arrays retain declared coordinates. Identifiers
are `prefix + SHA256(JCS(payload))`; none occurs inside its own preimage.

The [wire vectors](grc-v4-a-initializer-vectors.json) provide complete preimages,
canonical UTF-8 strings and expected IDs for policy, both invocations, pair and
receipt. They are shape/identity examples, not producer or migration executions.
The receipt is explicitly synthetic, with placeholder endpoint IDs: it is not
a semantically admitted crossing or retained successful run.

| Schema definition | Exact fields; identity prefix |
| --- | --- |
| `static_policy` | `schema_version`, `policy_id`, `numerical_id`, `history_policy_id`, `differential_recipe_id`, `differential_rounding_id`, `site_potential_id`, `passes`; `grcv4-a-initializer-policy-sha256:` |
| `construction_payload` | `schema_version`, `role`, `policy`, `target_reference`, `differential_reference`, `target_C`, `W_A_init`, `derived`; `grcv4-a-reference-pass-construction-sha256:` |
| `construction_record` | `construction_id`, `payload`; the ID is recomputed from the payload, not this envelope |
| `pair_payload` | `schema_version`, `current`, `reset`; `grcv4-a-reference-pass-pair-sha256:` |
| `pair_record` | `initializer_pair_id`, `payload`; the ID is recomputed from the pair payload |
| `migration_receipt_payload` | `schema_version`, `core`, `history`, `initializer_pair_id`; existing `grc-receipt-sha256:` domain, with new version `grcv4-profile-migration-receipt-v2` |

The schema fixes the static policy to `grcv4-a-target-reference-pass-v1`,
numerics to `grcv4-a-reference-pass-binary64-v1`, and lifecycle history policy to
`candidate_a_target_reference_pass_initialization_log_history_v1`. These names
resolve to exactly the schema's one static preimage; an implementation must not
accept an arbitrary same-name body. The ordinary A log writer is unchanged.

No profile schema change is needed: the existing
`params_resolved.lifecycle.history_policy_id` selects that exact static policy,
the candidate's `descriptor_backend_id` binds the complete differential
preimage, and `site_potential_id` binds the fixed site recipe. The other existing
fields bind boundary, units, normalization, geometry, gains, solver and domain.
The new history value changes params_hash and hence complete_profile_id. The
unchanged lifecycle algorithm ID is not replaced by an invocation/output hash.
An admitted release must bind the static-policy digest and schema bytes; it
must not change the policy's meaning under the same IDs.

The acyclic order is:

```text
fixed policy and recipe preimages -> resolved parameters -> complete A profile
  -> fixed target reference -> separate current/reset construction records
  -> pair identity -> migration receipt -> commit/lifecycle envelope
```

`target_reference` embeds the existing closed reference geometry preimage:
graph (including orientation), complete profile and resolved parameters, context,
K4 reference, structural-coordinate ID and reference-Hodge preimage.
`differential_reference` embeds the existing host-frame WLS preimage. Thus an
invocation needs no ambient registry or machine-local path to recover its inputs.
The reference's graph must equal the differential graph; descriptor digest,
stable-edge reference weights, reference-Hodge/K4 digests, context and profile
identities must all recompute and agree. WLS positions have one dimension-matched
row per live vertex; positive weights cover exactly the stable live edges.

`target_C` follows live vertex order; `W_A_init` follows oriented live edge order.
Their lengths and numerical domains must agree with that graph. The caller may
not supply W or flux as an initializer input. `W_A_init` is an output asserted
by a serialized record and must be recomputed on import. `derived` is required
and is either null or exactly `{W_base, Phi_base, J_ref}` in those same orders;
every retained intermediate must also recompute. A matching hash alone is not
production provenance. Recomputing final W must still execute all prescribed
intermediate admission stages.

The pair contains exactly one `current` and one `reset` record, with matching
roles, static policy, complete target profile, graph and fixed differential/
reference recipes. Each embeds its own context and resource input. Under this
initial constant-zero-context scope their contexts coincide; no nonzero context
implementation is implied. Roles change construction IDs, not numerical laws.
Identical operands must produce identical numerical results. Records with equal
values may not replace the requirement for two actual invocations.

## Migration, receipts and restoration

The request's candidate history channel uses the new lifecycle history policy,
`disposition = target_initializer`, `target_initializer_id =
grcv4-a-target-reference-pass-v1`, `source_history_digest = null`, and
`information_loss = none`. This identifies the algorithm before it runs, not
an output. Candidate C has no A history to lose. The carrier channel separately
receipts any C-carrier archive/drop and initializes a complete canonical-zero
A carrier for current/reset when the target is PC or CI+PC.

After separate construction, readmit both final targets through their existing
OS, CI, PC, CI+PC or RG2b owners. Keep target charts fixed; out-of-domain output
rejects without recentering, enlargement or target substitution. RG2b state/
section admission is not another beat's entry certificate. Same-graph migration
preserves both C vectors, charge target and clock; it performs no continuity,
repair, ordinary writer or formation beat. No state is published until both
construction and final admission succeed.

Successful C→A under this policy uses the v2 migration receipt above. Its new
`initializer_pair_id` must match the archived pair; the existing core/history
fields still bind source/target current/reset, history dispositions, resource
map and successful-parent policy. The commit binds this receipt ID as before.
The pair must match the target reference/profile and initialized W endpoints
of that exact crossing. Changing either invocation, its pair link or endpoint
must reject even when unrelated hashes are coherently recomputed.

Snapshot layout `pygrc-generic-initializer-migration-snapshot-v1` uses exactly
the top-level fields of `pygrc-generic-migration-snapshot-v1`. Each transition
row has exactly the existing `commit_id`, `request`, `source`, `source_reset`,
`target`, `target_reset` plus required `initializer_pair`. That field is a
`pair_record` for this C→A crossing and null for other crossings. There is no
new authoritative state coordinate or global registry. Reject absent, extra,
duplicate or mismatched pair evidence; no dangling pair is silently ignored.
The supplement's `snapshot_payload`, `transition_record` and `receipt_envelope`
definitions close these shapes. Their archived-reference schema permits either
candidate because a later ordinary migration may leave A while retaining the
crossing archive. That does not widen initializer targets beyond A. A digest-
shaped release other than the predecessor is still only syntax; the loader must
resolve an explicitly admitted, packaged successor before construction or replay.

Restoration reconstructs the archived crossing inputs, repeats both producer
invocations and final target admission, checks the v2 receipt linkage, and then
checks existing lifecycle/commit consistency. It must not require subsequently
ordinarily evolved W to equal a fresh initializer output. Preserve F1/F2
known/archived and repeated-state checks and lawful unreceipted assignment;
hash consistency does not certify unobserved external history.

Typed declaration/domain/range/readmission failures preserve their stage and
disposition and publish nothing. Unexpected programmer exceptions propagate;
blanket conversion or exception-message matching is forbidden. A reset-only
failure must arise from actual independent reset construction/admission, not
caller-assigned unequal fluxes. Roll back authority, references, archives,
receipts and commit metadata atomically, including late publication failure.

## Release applicability and remaining verification

The current packaged release
`grcv4-spec-release-sha256:e2acd9df0cc02c5fd4bbed4989ff5d7da3a819adeb2950d922b8a6ef4bf35f24`
does **not** admit this policy, construction/receipt schema or snapshot layout.
Its manifest, source manifest, base schema, assets, codec pins, old snapshots
and accepted executions remain unchanged. Current spec candidates are checked
separately; released document references are read at their original Git subject.

After review, a separately identified successor release must bind the accepted
paper/proposal, P9 authority/admission, this spec/schema and its static-policy
digest, v2 receipt schema and new snapshot layout. Packaging and codec dispatch
must select that release explicitly for new constructions. Unknown release/
policy/layout combinations reject. Merely replacing the current codec release
constant or allowing a policy label in the old release is insufficient.

Old explicit-flux history policy, `grcv4-a-history-free-stage-v1`,
`grcv4-a-history-free-construction-v1`, existing receipt versions and snapshot
layouts retain their original meanings. They cannot be cast, rehashed or
silently upgraded into authenticated reference-pass production. An explicit
crossing may preserve historical records at their original identity while
creating new evidence under the successor. Existing exact C_OS support does
not grow merely because the supplement or a new package is available.

Specification checks must cover closed shapes, JCS/digest recomputation,
policy/recipe/profile coherence, role separation, graph/array dimensions and
negative old-layout/old-policy controls. These checks are not producer execution.
Implementation must separately discharge [paper §12.6.4][pressure]: active
alpha/beta/gamma and both gamma signs on nontrivial graphs; graph/order controls;
source-history independence; floor, rounding, cancellation, subnormal and range
pressure; genuine current/reset failures; fixed-chart rejection; and the
auxiliary-total-current-singular/final-reference-regular regression at the real
producer. Positive C→A must traverse all five actual A admission paths, with
rollback, restoration, reset, duplication and admitted continuation checks.
The old 25/17-test migration records prove none of this new execution.

`P9-7.2a-VO-A-INITIALIZER-INTEGRATION` remains the forward obligation. This
candidate does not close aggregate 7.2a, widen G2/G3, implement generic events,
establish native formation or bind the exact GRC9V3 initializer.

[paper]: ../implementation/investigations/grc9v4-constitutive-design/drafts/2026-09-GRC-V4.md#126-graph-generic-candidate-a-history-free-initializer
[proposal]: ../implementation/investigations/grc9v4-constitutive-design/drafts/GRCV4-proposal.md#126-graph-generic-candidate-a-history-free-initializer
[design]: ../implementation/investigations/grc9v4-constitutive-design/decisions/P9CandidateAInitializerReferencePassProposal.md
[authority]: ../implementation/investigations/grc9v4-constitutive-design/decisions/P9CandidateAInitializerReferencePassAuthority.json
[specialization]: ../implementation/investigations/grc9v4-constitutive-design/drafts/2026-09-GRC-V4.md#a9-exact-grc9v3-candidate-a-initializer-binding
[pressure]: ../implementation/investigations/grc9v4-constitutive-design/drafts/2026-09-GRC-V4.md#1264-design-closure-and-remaining-evidence
