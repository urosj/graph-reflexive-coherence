# P9-7.2a — Candidate A target-only reference-pass initializer proposal

Date: 2026-09-11. Status: **accepted by the user as bounded successor design;
source admission, propagation and runtime verification pending**.
Owner: the outstanding generic C→A initializer-source obligation in P9-7.2a.
Implementation baseline: `924fca9` (accepted six-class migration and audit fixes).

The user accepted the clarified definition by requesting its commit and
continuation on 2026-09-11. This resolves the reference-current producer choice.
Source admission, propagation and runtime evidence remain separate. This
document does not close C→A, P9-7.2a, G2 or G3. It changes neither older families
nor an accepted D10/D11 source. No new runtime behavior is implemented by this
decision. The proposal filename is retained for link continuity.

The supplied design review found no new constitutive blocker and supported this
concrete producer. Its requested executable-domain clarification and additional
auxiliary-singularity regression are incorporated below, together with its
identity-ordering, reset-test and fixed-target-chart cautions. The subsequent
user acceptance applies to that clarified contract. The remaining work is
binding/propagation, implementation and positive migration evidence, not another
search for the producer rule.

## 1. Accepted decision and source boundary

Use one graph-generic, history-free Candidate A initializer: reconstruct target
differentials, evaluate a current-independent auxiliary conductance, perform
exactly one reference-geometry baseline transport evaluation, and evaluate the
unchanged full conductance law with the resulting reference flux. The auxiliary
conductance is construction data, not a retained state coordinate. Target
realization admission follows construction; it is not part of the flux producer.

This selects a new initialization policy. Existing sources determine its
ingredients and lifecycle obligations, but do not uniquely select this order.

| Source | Inherited requirement; limit |
| --- | --- |
| [Generic V4 Candidate A contract](../../../../specs/grc-v4-spec.md#candidate-a-contract) | The curvature-disabled, normalized/nondimensional `G_W`, positive retained mobility, reference potential and baseline flow. No reference-pass initializer is selected there. |
| [D10.2 initializer derivation](D10_2FullSubstrateProvenanceAndPromotionAudit.md#d102-der-a-initializer-general-grc-candidate-a-history-free-initializer) and [paper §12.6](../drafts/2026-09-GRC-V4.md#126-graph-generic-candidate-a-history-free-initializer) | Fresh target differentials, reference-current-stage evaluation, separate current/reset construction and target readmission. Generic and exact GRC9V3 initializer roles are distinct. |
| [P9-5.1](../../../phase-9-grcv4/tranche-5/P9-5.1-Review.md) | Implemented `G_W` evaluation from an explicitly supplied flux. The supplied operand is not an authenticated target-stage solver result. |
| [P9-5.4](../../../phase-9-grcv4/tranche-5/P9-5.4-Review.md) | Initializer-current provenance remains open; construction is not native formation or preserved A history. |
| [P9-7.2a](../../../phase-9-grcv4/tranche-7/P9-7.2a-Review.md) | Whole current/reset migration, directional history policy, restoration and atomicity; six accepted classes do not discharge positive C→A. |

The current forensic `contract_provenance` query for
`D10.2-EC-PARENT-L-A-INITIALIZER-GRC` returns
`source_exact_contract_provenance`, with support disposition and accepted-claim
support semantics `indeterminate_requires_review`. Its source is
`GRC9V4-CD-D10.2-v1`,
`D10_2FullSubstrateProvenanceAndPromotionAudit.json`, pointer
`/normative_equation_contract_registry/47`; trace digest
`537dfbb0815e7a3d3846d972f20f83e4d9c05189022dd1ffac6bc7d436e87b79`.
The full source and edge witnesses are retained under that contract key in
the `authority` object of the existing
[migration record](../../../phase-9-grcv4/tranche-7/P9-7.2a-Migrations.json).
This is predecessor provenance, not acceptance of the construction below.
The neighboring generic migration and specialization initializer contracts
retain their own boundaries; no provenance reference becomes new authority.

## 2. Inputs and authority separation

One invocation consumes the complete target graph/orientation/boundary,
Candidate A profile, declared target context and resource vector $C$, and the
reconstructible target differential and site-potential recipes. The same policy
is applied separately to current and reset, with their own $C$ and applicable
target context. Inputs and outputs are detached provisional values.

- Differential frames, reference weights, units, regularization and evaluation
  policy must be declared and identity-bound before construction. Reconstruct
  $D(C)$ from those inputs, not a caller-supplied descriptor cache.
- Those differential inputs cannot depend on source W/Z/current, the auxiliary
  W, or the final W being initialized. A backend requiring unresolved such data
  is outside this policy's admitted input domain; no fixed point is implied.
- Fixed reference weights and $H_{0,\mathrm{ref}}$, $H_{1,\mathrm{ref}}$ remain
  reference data. Do not replace them with the auxiliary conductance, or replace
  Candidate A mobility by a Hodge/geometry object.
- Source candidate/carrier history, source current caches and source realization
  solver outputs are not inputs to the producer. Target $C$ may reflect the
  source's past; independence is conditional on identical declared target inputs.
- No conductance coefficient is restricted to zero or to a favorable sign.
  Parameters obey the existing finite/positive declarations and target domain.

The mathematical rule is common to OS, CI, PC, CI+PC and RG2b. Its numerical W
depends on candidate/reference inputs, not on the temporal realization's solver
or Read-Back gains. Complete profile identity still binds those realization
parameters, and they still determine whether the constructed target admits.

## 3. Accepted graph-generic construction

Let $B$ be the target incidence matrix, with $+1$ at the oriented tail and $-1$
at the head; $d_0=B^\top$. All vectors follow the target's declared live order.
For $e=(u,v)$, form the unfloored exponent

$$
E_e(C)=-\frac{\alpha}{2}(C_u+C_v)
       -\frac{\beta}{2}\lVert D_u(C)-D_v(C)\rVert^2.
$$

First construct the auxiliary reference conductance:

$$
W^{\mathrm{base}}_e=\max(W_{\mathrm{floor}},\exp E_e(C))
                  =G_{W,e}(C,0).
$$

Next, evaluate the existing A potential and baseline transport at **reference
geometry**, using this auxiliary conductance as the explicitly selected
initializer-stage transport operand:

$$
s_i=V'_{\mathrm{site}}(C_i;U),\qquad
\Phi^{\mathrm{base}}
=\kappa_c B\operatorname{Diag}(W^{\mathrm{base}})B^\top C-s,
$$

$$
J_{\mathrm{ref}}
=-\eta\operatorname{Diag}(W^{\mathrm{base}})B^\top\Phi^{\mathrm{base}}.
$$

Finally construct the retained target conductance with the full original law:

$$
W^{\mathrm{init}}_{A,e}
=G_{W,e}(C,J_{\mathrm{ref}})
=\max\!\left(W_{\mathrm{floor}},
  \exp\!\left[E_e(C)-\frac{\gamma}{2}J_{\mathrm{ref},e}^2\right]\right).
$$

```text
target C and fixed target recipes
  -> fresh D(C)
  -> auxiliary W_base = G_W(C, 0)
  -> reference potential and reference baseline flux
  -> full G_W(C, J_ref)
  -> provisional W_A_init
  -> independent whole-target readmission
```

Exactly one pass is selected. There is no update of $W^{\mathrm{base}}$, repeated
bootstrap, root selection, convergence tolerance or implicit equation for W.
The reference-relative geometry increment is zero here because this stage is
defined at $h_{\mathrm{ref}}$, not because $\kappa_{Ah}$ is disabled. Final target
readmission uses the actual target geometry, gains and realization, unchanged.
The producer must not call a total-current/Read-Back solve and relabel its output
as this baseline flux.

Auxiliary W need only admit the prescribed differential, conductance, mobility,
potential and baseline arithmetic. It need not be a regular retained state of
the full A current equation or lie in a target realization's W chart. In
particular, do not obtain the baseline by constructing `CandidateACurrent` at
W_base: that constructor also imposes total-current admission, which is not a
producer prerequisite. Only the final initialized state receives whole-target
readmission. The adversarial fixture in §7 distinguishes these boundaries.

The first evaluation explicitly uses zero *as the current operand of the
auxiliary conductance*. It does not set $J_{\mathrm{ref}}=0$ or $\gamma=0$.
The final W is not required to equal its instantaneous reference recomputed
using that final W. History-free initialization is not reference neutrality.

## 4. Mathematical domain and generality

On a finite admitted graph, finite declared differential/site outputs and finite
real parameters with $\eta,W_{\mathrm{floor}}>0$ give a finite sequence of real
operations and positive W. No weak-coupling or fixed-point existence assumption
is needed to define that sequence. This is not a binary64 representability or
target-current/geometry/root/section admission guarantee.

Parallel edges enter the incidence sums separately. A self-loop has a zero
incidence column and zero reference flux; its conductance still uses both
endpoint occurrences, giving the resource term $-\alpha C_u$. Isolated vertices
do not acquire artificial transport. Graphs, components and boundaries must
still satisfy the declared differential and target-domain contracts; this rule
does not admit a previously unsupported graph by itself.

Under consistent vertex/edge permutations, all inputs and outputs transform
with their declared coordinates. Reversing an edge changes its reference flux
sign, while its squared-current contribution and scalar W are unchanged.
Frame covariance requires the admitted differential's compared descriptor gaps
to transform isometrically in the declared common/comparable frame. This is
conditional covariance, not a claim that every backend or binary64 frame rotation
has bitwise-identical outputs.

For fixed target graph, candidate/reference inputs and $C$, source-history
changes cannot change the constructed W. Target identities and history receipts
may still differ when the source or complete realization changes. Equal numeric
W alone does not establish equal provenance or native formation.

## 5. Accepted numerical and identity contract

Policy ID: `grcv4-a-target-reference-pass-v1`.
Numerical ID: `grcv4-a-reference-pass-binary64-v1`.
Lifecycle history policy:
`candidate_a_target_reference_pass_initialization_log_history_v1`.
These are accepted design labels, not yet executable profile IDs. The ordinary A log-history
writer is unchanged; the new history-policy identity distinguishes how W is
initialized. Existing explicit-flux policies/records keep their old meanings.

The initial executable scope retains the existing **unit-vertex pairing** and
admitted boundary/normalization contracts, together with the identity-bound
host-frame WLS backend and declared zero-derivative site potential, as scoped in
[P9-5.2](../../../phase-9-grcv4/tranche-5/P9-5.2-Review.md). Graph-generic does not
mean arbitrary quadrature, boundary or differential implementations. The general
equations allow other admitted recipes; an unknown or unimplemented recipe rejects explicitly.
This proposal does not invent implementations for arbitrary site potentials or
claim induced-frame/GRC9 differential compatibility.

The accepted binary64 evaluation boundaries are:

1. Validate typed finite inputs, exact graph/order/context/profile/recipe
   identities and the existing nonnegative-resource domain. Rebuild gradients
   with the existing exact-input WLS recipe and its binary64 output rounding.
2. Evaluate $W^{\mathrm{base}}$ with the existing conductance numerical contract:
   accumulate the exponent from exact rational representations of the supplied
   binary64 coefficients/resources and rounded descriptors, round the combined
   exponent once, apply the existing `math.exp` evaluation and positive floor.
   Its documented far-negative floor branch is retained. Exponential overflow
   rejects; the normative floor is not an emergency numerical repair.
3. Compute each auxiliary mobility product $\eta W^{\mathrm{base}}_e$ with
   binary64 round-to-nearest, ties-to-even, as the existing mobility owner does.
   Overflow/nonfinite values or underflow to nonpositive mobility reject; there
   is no additional floor on mobility. This is a temporary transport factor,
   not an assertion that W_base was incoming retained A authority.
4. Accumulate each full reference-potential sum exactly over those rounded W
   inputs and binary64 $C$, $\kappa_c$ and declared site-derivative output; round
   the full potential component once. Do not round edgewise partial sums or add
   an initializer-specific gauge projection. The formula fixes a representative;
   exact constant shifts have no physical flux effect. The initial site recipe
   returns exact zero. A later recipe must define its own evaluation identity.
5. For each edge, accumulate $B^\top\Phi^{\mathrm{base}}$ and its product with
   the rounded auxiliary mobility exactly, then round the flux once. Use the
   rounded potential components as inputs, matching the existing A baseline
   staging. Potential/flux overflow rejects. Representable subnormals are kept;
   underflow of a signed potential or flux may round to canonical positive zero,
   unlike strictly positive mobility. It is numerical rounding, not missing-input
   defaulting. Self-loop flux is zero algebraically.
6. Evaluate the final full `G_W` with the original coefficients, same rounded
   descriptors and computed rounded reference flux. Accumulate **all** exponent
   terms together before its one exponent rounding, as in P9-5.1. Do not add the
   current term to an already-rounded E, use `log(W_base)`, or multiply floored
   W_base by a current factor. Flooring and rounding make those different laws.
   Validate positive finite final W and final mobility using their existing
   owners; then return the provisional construction for target readmission.

The existing platform `math.exp` contract is not a new correctly rounded
transcendental guarantee across platforms. Exact execution reproduction retains
the implementation/environment and input identities; portability requires no
machine-local paths. Any stronger numerical portability promise needs its own
specified evaluator and evidence, not silent replacement during restoration.
Intermediate range failure remains a declared failure even if a symbolic
combination at a later stage could have been finite. There is no log-domain
substitute, clipping, extra bootstrap pass or fallback flux in this policy.

The admitted V4 release and complete target identity must resolve the policy,
numerical recipe, differential preimage and site recipe unambiguously. A
construction record must bind its role (current or reset), target graph/
orientation/boundary/profile/context, target $C$, policy/numerical IDs and recipe
preimages, and the resulting W. W_base/potential/flux may be retained as derived
evidence, but import must recompute them when present and reject inconsistencies.
A caller-supplied matching-looking flux or claimed policy ID is not provenance.
Use existing canonical content identities and crossing archives, not a new
global registry, signature service or independent authoritative state field.

Keep static policy/recipe identity separate from the output-bearing identity of
a particular invocation. The dependency order is static policy/recipe → complete
target profile → current/reset construction records → migration evidence. The
target profile must be computable before either construction executes; a record
that includes that profile and its resulting W cannot also be a prerequisite for
computing the profile. Current/reset roles distinguish construction-record
identities, not the numerical law or its operands.

The concrete closed payload/codec fields are a V4 specification-propagation
obligation before runtime implementation. Unknown policy/numerical identities
must fail closed. Old snapshots and accepted runs are not rehashed or silently
upgraded; an old explicit-flux record cannot be relabeled as this construction.

## 6. Whole C→A migration and failures

Source admission remains the existing lifecycle owner's responsibility. Apply
the same initializer policy independently to the target current and reset
resource/context inputs. Preserve both resource vectors, charge target and
clock for this same-graph identity-resource crossing; copying current W to reset
is forbidden even when one fixture happens to produce equal values.

Conversely, identical target C/context/recipes must produce identical reference
flux and W for current and reset, despite their different record roles. The old
supplied-flux reset counterexample cannot be relabeled as evidence for this
producer: a genuine reset-only failure must arise from its independently
computed reset construction or actual reset target admission, not manually
different fluxes assigned to otherwise identical target inputs.

Candidate C has no A history to lose or preserve. The candidate channel records
history-free target W construction with its initializer identity. Source C
persistent carrier history is separately archived/dropped and receipted when
present. If the target is A_PC or A_CI+PC, initialize the complete target carrier
to canonical zero for both current and reset. Never reinterpret C's Z as A's Z;
the carrier channel names its actual loss/initialization independently of W.

Rebuild and readmit the whole prospective target using each realization's
existing owner: OS staging, CI root, PC carrier geometry/current, CI+PC composite
root, or RG2b state/section admission. RG2b state admission is not certification
of eligibility for another ordinary beat. Ordinary continuation, when claimed,
requires that next beat's entry admission separately. No source current, stored
root or cached geometry can bypass target reconstruction.

Target PC weight charts, CI domains and RG2b state charts remain fixed declared
inputs. Reject an initialized state outside the requested target's domain; do
not recenter, enlarge or replace the domain in response to the output. A positive
fixture may declare a suitable target domain in advance, but that is not a
runtime repair of a failed requested migration. This requirement does not add a
full-target-domain check to the auxiliary W stage.

Migration performs no continuity, resource correction, clock advance, ordinary
A write, carrier write or formation beat. Publish both states, reference/backend
selection, archives, ordered receipts and commit identity together, only after
all checks. Reset returns to the independently transformed baseline. Restoration
reconstructs the initializer from archived target inputs and checks the map and
current/reset endpoints; it cannot certify unknown external history merely from
internally consistent hashes.

Recomputation authenticates archived crossing inputs and their initialized
endpoints only. Do not require a subsequently ordinarily evolved W to equal a
fresh initializer output: the accepted ordinary A writer can lawfully change it.

Typed declaration/domain/range/readmission failures retain their actual stage
and existing failure disposition and publish nothing. The missing-rule refusal
is replaced only for this admitted/implemented policy, not waived generally.
Programmer `ValueError`, `V4IdentityError`, `RuntimeError` and other unexpected
exceptions must propagate under the corrected P9-7.2a boundary; no blanket
exception-to-scientific-failure conversion or message matching. The F2 checks
for known/archived and repeated scientific-state commitments remain in force,
as does lawful unreceipted assignment without forced trajectory adjacency.

## 7. Alternatives and design pressure

The selected candidate is recommended, not uniquely derived from GRC axioms.
Supplying arbitrary flux leaves the original provenance gap; copying source
current/history violates target-only construction. Requiring $\gamma=0$ merely
hides the missing operand. A declared zero-flux initializer would be a different
explicit policy, not evidence for this nonzero reference pass. Exact GRC9V3
initialization remains a deliberately selected specialization binding.

Self-consistency would impose an additional reference-neutrality condition:

$$
W_A=G_W(C,J_{0,A}(C,W_A,h_{\mathrm{ref}})).
$$

For one edge with $C=(1,0)$, $\eta=1/2$, $\kappa_c=1$, zero site derivative,
$\alpha=\beta=0$, $\gamma=-2$ and $W_{\mathrm{floor}}=1/2$, the baseline is
$J_{0,A}=-W_A^2$, so self-consistency requires $W_A=\exp(W_A^4)$. There is no
positive solution: for $0<W_A\leq1$ the right side exceeds 1, and for $W_A>1$,
$W_A^4>\log W_A$. The proposed explicit pass instead has W_base = 1,
J_ref = -1 and W_init = exp(1). This demonstrates definability, not successful
target readmission. A partial implicit initializer with domain/root/failure
rules remains a possible different policy; this draft does not disprove it.

### Auxiliary total-current singularity must not reject the producer

Retain this adversarial regression for implementation. On one edge, choose

$$
C=(1,0),\quad \eta=\tfrac12,\quad \kappa_c=1,\quad V'_{\mathrm{site}}=0,
\quad \alpha=\beta=0,\quad \gamma=2\log2,\quad
W_{\mathrm{floor}}=\tfrac14,\quad \chi_A=1,\quad \zeta_A=3.
$$

The prescribed pass gives $W^{\mathrm{base}}=1$, $J_{\mathrm{ref}}=-1$ and
$W_A^{\mathrm{init}}=1/2$. An incorrect full-current solve at the auxiliary W
has $\widehat W_A=1/2$, $q_A=1/3$, and denominator $1-3q_A=0$: it is singular.
At the final initialized W, however,

$$
J_{0,A}=-\tfrac14,\qquad \widehat W_A=2^{-1/16}>\tfrac12,
\qquad q_A<0,\qquad 1-3q_A>1.
$$

Thus the final reference current block is regular. This does not establish
complete target-realization or migration admission. The regression must bind
the actual rounded parameter and intermediate values, verify that the producer
does not call the auxiliary full-current constructor, and still require the
final target's ordinary admission. For an admitted whole-target fixture it must
reach that admission instead of returning the spurious auxiliary singularity.
This single-edge architectural counterexample supplements, never replaces, the
nontrivial all-channel/general-graph and five-realization positive coverage.

A read-only fixture check against the unchanged `924fca9` value/current
primitives confirmed the rounded witness with gamma
`float.fromhex("0x1.62e42fefa39efp+0")`: W_base = 1.0, J_ref = -1.0,
W_init = 0.5, auxiliary `CandidateACurrent` disposition `singular`, final
baseline = -0.25, final W_hat = 0.9576032806985737, and exact final denominator
`12747047485120948/6564461591808109` (> 1). This is a bounded fixture check,
not a new producer implementation, whole-target migration execution or retained
conformance run. The future regression must exercise the actual producer/map,
not merely repeat this local arithmetic.

The general argument is the acyclic dependency chain and its declared inputs,
not a handful of successful examples. Runtime evidence must nevertheless
exercise the dependencies and existing lifecycle failure surfaces:

| Required pressure after admission | What it must distinguish |
| --- | --- |
| Nontrivial multi-edge/multi-vertex graph, active alpha/beta/gamma, nonzero descriptor gap and computed current; both gamma signs | Full law versus zero-current/disabled-channel or scalar-only substitution. |
| Parallel edges, self-loop, isolated vertex/disconnected components where admitted; permutation and signed reorientation | Correct graph incidence and coordinate binding; no chart/size shortcut. Frame tests retain the backend's numerical covariance ceiling. |
| Bootstrap floor active; final exponent recomputation; signed-channel cancellation; subnormal and overflow boundaries | Correct formula and staging versus floored-product/log shortcuts, premature exponent rounding and numerical repair. |
| Auxiliary total-current singularity with regular final reference block (fixture above) | No `CandidateACurrent`/Read-Back solve or whole-target chart check at W_base; the producer still reaches final target admission when its own arithmetic admits. |
| Distinct current/reset resource and context where supported, plus identical-input control | Two actual producer executions and separately rebuilt target admission, not copied W; identical operands give identical numeric outputs despite different record roles. |
| Matched target inputs from different admitted C source realizations/carrier histories; stale-cache substitutions | Conditional source-history independence. Malformed authoritative source states still reject at source admission. |
| Positive migration into A_OS, A_CI, A_PC, A_CI+PC and A_RG2b on declared admitted fixtures | One shared initializer path, with five real target admission paths; not every source/target Cartesian combination or parameter choice. |
| Reset-only construction/admission failure; late publication exception; F1/F2 regressions | Genuine independently computed reset failure, not caller-injected unequal fluxes; complete rollback, correct exception semantics and archived commitment consistency. |
| Fixed target PC/CI/RG2b chart rejection | No output-dependent recentering, enlargement or substituted target identity to rescue a requested migration. |
| Static-policy versus invocation identities; save/load, fresh-process restoration, reset, duplication and admissible continuation | Acyclic profile/record binding; recomputed archived construction endpoints without requiring ordinarily evolved W to remain an initializer fixed value; unchanged receipt-parent/trust semantics. |

Previously executed exploratory value checks are not retained migration
acceptance evidence. The checks above are pending, not asserted passes. Use
independent numerical oracles and actual lifecycle consumers where each is
required; a constructor round trip is not a migration test.

## 8. Debt, claim ceiling and ordered follow-through

Debt identifier: `P9-7.2a-DEBT-A-INITIALIZER-SOURCE`.
Object: `P9-O-A-INITIALIZER-REFERENCE-PASS`.
Equation contract: `P9-EC-A-INITIALIZER-REFERENCE-PASS`.
Claim: `P9-7.2a-CL-O-INIT-001`, an optional Candidate A construction
under the stated inputs/domain, not inherited core, formation or conformance.
These identifiers await structured source admission before becoming queryable
graph nodes. The source-rule choice is **resolved at bounded design scope**;
propagation, implementation and positive-migration verification obligations stay
explicitly open. Do not rewrite P9-5.1/P9-5.4 or D10/D11 acceptance histories.

The ordered work stays within P9-7.2a:

1. Completed: design-review PASS, refinements incorporated and explicit user
   acceptance by the commit request. This resolves the producer choice; it is
   not runtime selection, source admission or gate promotion.
2. Record the accepted bounded successor and debt/claim routing; admit it through
   the existing side-tool append-only source mechanism. Preserve predecessor
   support classifications and expose the actual claim/contract/debt traces in
   the existing API, notebook and browser, not docs alone.
3. Update GRCV4-proposal §12.6 and relevant source crosswalks; review that change,
   then propagate into the paper and the V4 specification successor. Specify
   the closed initializer identity/payload and release applicability before code.
   The old-family specs/runtime and exact GRC9V3 binding remain unchanged.
4. Implement the producer and generic C→A map with existing differential,
   conductance, baseline arithmetic, target-admission and publication owners.
   Keep the P9-5.1 explicit-flux constructor distinct, rather than retroactively
   giving its records stronger provenance. Broaden executable realization scope
   only with the corresponding tests and permitted source paths.
5. Execute the focused construction/migration pressure above, retain source/
   input/output-bound evidence, and update the existing scoped verifier and
   affected API/notebook/browser projections. Reuse unchanged accepted evidence;
   rerun only changed numerical paths and necessary integration checks.
6. Review all seven required migration classes and the outstanding shared
   lifecycle obligations for aggregate P9-7.2a acceptance. The original 25-test
   and 17-test records keep their exact subjects and counts. C→A rejection-only
   evidence cannot discharge the positive class. P9-7.2b generic events, wider
   G2/G3, native formation and GRC9V4 specialization remain separate work.

No new tranche, universal gate, handoff archive or failure-tracking process is
required. The goal is one defined and reconstructible initializer whose claims,
paper, specification and implementation agree, with honest admission failures.
