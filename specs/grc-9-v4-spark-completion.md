# GRC9V4 certified geometric spark-completion successor

Normative bounded scientific/design successor, 2026-10-31. Source:
[SC-3 authority](../implementation/investigations/grc9v4-constitutive-design/decisions/spark-completion/Authority.json),
[proposal](../implementation/investigations/grc9v4-constitutive-design/drafts/GRC9V4-spark-completion-proposal.md),
[paper](../implementation/investigations/grc9v4-constitutive-design/drafts/2026-10-GRC9V4-Spark-Completion.md).
[Closed schema](grc-9-v4-spark-completion-schema.json) and
[source manifest](grc-9-v4-spark-completion-source-manifest.json).
This adds an optional contract to the unchanged v1 specialization and v2 baseline
basin diagnostic. It does not enable native completion or change older versions.

## Identity and typed binding

The site payload is `grcv4-homogeneous-quartic-site-v1`, with exact rational
c0, a, mu and explicit units. Its static evaluator discriminator is
`homogeneous_quartic_site_v1`, never an alias for the existing zero-derivative ID.
For C opt-in, `grcv4-candidate-c-params-v2` retains the v1 fields, uses that new
`potential_evaluator_id`, and adds `site_binding`. A `grcv4-resolved-params-v2`
payload explicitly contains that successor candidate schema; its complete
params hash covers the full payload. Existing transport authority and generic
identity grammar remain intact. No v1 decoder may guess these additions.
Only C_OS has completion evidence under this binding; other families receive
neither a runtime grant nor a stability theorem from the generic formula.

`grc9v4-resolved-specialization-v3` retains the v2 fields and adds the closed
`completion_policy` (explicit null or the v2 policy below). The corresponding
`grc9v4-specialization-identity-v3` adds the policy ID/null; params hashing covers
all static policy fields. `grc9v4-complete-identity-v3` and
`grc9v4-configuration-v3` preserve v2 fields and contain the new identities.
Existing SHA-256/JCS digest-prefix conventions apply. No event, parent, proof
or observation enters a static profile hash. Opt-in is an explicit migration
with both-role full target reconstruction/readmission. Old v1/v2 payloads and
accepted identities are never reinterpreted. Native codecs are future P9-9.1a work.

## SC-EC-QUARTIC-SITE

Evaluate V=mu*((C-c0)^2-a^2)^2/4, V'=mu*((C-c0)^3-a^2*(C-c0)) and
V''=mu*(3*(C-c0)^2-a^2), with finite global c0>a>0, mu>0, finite C>=0.
Use minus V' in the potential. Units are c0,a:C; mu:Phi/C^3; V:Phi*C;
V':Phi. The same parameters apply at every node, independently of labels,
partitions, graph size, event outcome and time. No resource injection occurs.
Changing coefficients/units/evaluator changes generic profile identity.
Polynomial definition does not certify arbitrary parameter-domain admission.

## SC-EC-GEOMETRIC-IDENTITY

The static completion policy ID is `grc9v4-certified-geometric-child-basins-v1`.
Its schema is `grc9v4-child-completion-policy-v2`. It contains the landscape sign,
positive gradient/Hessian/resource/contrast thresholds, positive beat count,
minimum elapsed time, fixed positive step duration, full-state trap policy and
explicit ASCII numerical policy ID (`[a-zA-Z0-9_.:-]+`). Threshold units follow the resolved resource/row
unit contract; no untyped external scale is permitted.

From one fresh captured state, form the declared exact fixed-row functions.
Qualified anchors satisfy sum(g_a^2)<epsilon_gradient^2, min(s*g_a)>
epsilon_Hessian, C>minimum_resource and every-neighbor landscape barrier greater
than contrast. Use all strict descents of s*C, no tie arcs. Include unqualified
terminals in the all-route terminal set. Assign exactly those nodes whose full
terminal set is the singleton qualified anchor. Each complete domain has at
least two nodes. Ambiguous/unqualified results do not acquire artificial IDs.
This diagnostic differs from existing represented-flow basin membership.

## SC-EC-PARENT-GAIN

Require a unique qualified fresh source parent containing the expanded vertex.
Missing parent returns `not_applicable`, never baseline count zero. Bind the
actual event receipt and ancestry, parent/source capture and module/exterior
lineage. Entire target domains must lie in the lifted parent footprint and be
anchored at the surviving parent or in the module. Require at least two eligible
descendants and a new-module anchor; local gain=descendant count-1. External
domains and relabelled old nodes cannot count. Complete memberships, not anchor
sets alone, are evidence. This is local gain, not counterfactual event causation.

## SC-EC-FULL-STATE-RETURN

The proof binds actual equation/profile/context/references, all independent C/W/Z
channels, genuine constraints, complete relative domain, scaled norm, q<1 and
strict image margin. It must prove the actual physical step maps the domain
strictly into itself and contracts uniformly, with complete basin and edge-order
certificates throughout. The live target trajectory must reach that domain after
positive ordinary evolution. Solver residuals, current-only equality, finite
samples and inner CI/RG2b certificates cannot stand in for this proof.

## SC-EC-REPRESENTED-COMPLETION

Before native completion, verify a bound on the full represented step in the
declared norm, including all root/section/geometry/writer errors, smaller than
the strict image margin. The current theorem requires the same exact charge
slice, not merely a passing charge tolerance. Bind a constraint-preservation
certificate and separately certify row/seed/resource/barrier/descent agreement,
including excluded anchors, at actual represented states. Equality or unresolved
intervals do not satisfy strict predicates. No implicit clipping, projection,
precision escalation or exact-inverse fallback is permitted. A different drift
theorem needs a separately selected contract.

The numerical policy determines lossless operand encoding and the validator for
the retrievable full-step/constraint/diagnostic certificates. A valid JSON shape
or self-consistent digest is not that validation. Until this obligation passes,
the result is `unresolved` for native completion even when research feasibility
is positive. The research Arb precision is not mandated as production arithmetic.

## SC-EC-WINDOW-LIFECYCLE

Every observation binds current role, actual successful primary receipt, positive
step index/time/duration, one fresh poststate C/W/Z and context, complete selected
read/root/geometry where applicable, full domain membership and numerical proof.
Require consecutive successful positive beats and sufficient elapsed time under
one unchanged binding. Read/replay/duplicate/rejected/zero-duration actions earn
no beat. Failure restores the whole publication and window. Reset, rebase,
graph/profile/context/reference changes or disabled crossings invalidate the
active window. Reset is independently admitted but cannot mint a live birth.

Completion is keyed to actual event receipt/ancestry, independently of policy,
proof, review or window identity. An event can earn at most one gain across
replay/import/duplicates and later comparisons. The same owner atomically
publishes scientific state, window, completion receipt and hierarchy insertion;
no second mutable journal may disagree. A completed record names new child
anchors and complete domains, source parent, event and proof. Insert hierarchy
entries in canonical typed-node order; never insert the surviving parent as new.
This does not select numeric abundance or implement causal subsystem semantics.

## SC-EC-COMPLETION-SCHEMA

The closed evidence discriminator is `grc9v4-child-completion-evidence-v2`.
Every envelope contains policy digest, actual event-lineage ID and a decision:
`not_applicable`, `pending`, `unresolved`, `invalidated` or `completed`.
Noncompleted decisions carry a reason and no gain. Completed evidence carries:

- source capture and event receipt references; typed parent anchor/members and
  expanded vertex; target profile/graph IDs and actual lineage reference;
- a retrievable full-state trap certificate and equation binding, present state
  channels/constraints, domain/center references, norm, q and image margin;
- explicit numerical-policy, full-step-error, exact-constraint and diagnostic
  certificates, with finite bounds and verified validators;
- an ordered positive observation window, each with receipt, exact time/step,
  state/read/operand references and complete typed descendant domains;
- exact local gain and canonical new-child anchors.

Typed node IDs preserve integer/string identity and reject bool-as-integer,
duplicates and absent/mismatched graph coverage. Order follows the existing V4
canonical typed-ID convention, for serialization only. Exact rational strings
are reduced, denominator positive, with no redundant /1 or signed zero. JSON
schema validates shape; semantic admission additionally checks positivity,
q<1, error<margin, time arithmetic, channel/profile compatibility, complete
lineage/membership, actual state inclusion, proof validity and at-most-once gain.
All references must resolve to bound payloads; a digest alone is insufficient.
Self-digests exclude their own field. Policy and dynamic evidence never form a
hash cycle. Checkpoint integration must explicitly version the existing complete
checkpoint and preserve event consumption across reset/replay; absent old fields
are not guessed. This is a design obligation before native enabling.

## SC-EC-SCIENTIFIC-CEILING

The accepted scientific witness is C_OS at c0=2,a=mu=1, eta_C=1/1024, h=32,
kappa_Phi_C=1/64,tau_C=1,chi_C=zeta_C=kappa_H=1/2,kappa_M_C=0,
unit measures/weights/Hodges, zero context and split tolerance 1e-11. Its actual
charge-21 source/event/target chain reaches the fourteen-dimensional full-map
trap and completes a two-beat duration-64 window at target step 902. It has one
new stable child and local gain one. Fixed 8192-bit approach and 512-bit window
enclosures certify exact equations; they do not establish native conformance.
Other parameters, graphs, realizations, W/Z channels and roots/sections require
separate evidence. No general partition chooser or all-ten completion is supplied.

## Required implementation checks at P9-9.1a

Implement the optional typed site binding and completion contracts only through
explicit new schema/model identities. Check exact coefficient/sign and zero-site
compatibility, both-role admission, independently bounded full-map and predicate
errors, charge constraints, source/event/target correspondence, positive windows,
all invalidations, replay/import and atomic failure/hierarchy behavior. Preserve
all ten existing native families' current support; the first new completion
population is bounded C_OS. Expose native completion only after its own accepted
execution evidence. SC-3 and research reconciliation make no such runtime grant.
