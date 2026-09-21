> Relocation-only maintenance: repository paths and dependent identities were
> rebuilt before first commit. Scientific statements, numerical results and
> review verdicts are unchanged; the new identities are not an independent
> reviewer rerun. Earlier byte-preservation statements describe the pre-move stage.

# ATC-CAN-F2 — resource-supported accumulation fission

**Status:** new, bounded constitutive hypothesis for review. Not an accepted
law, enabled ATC profile, replacement for CAN-B, or all-product closure.
The [modal discrimination result](./ATCModalSplitDiscrimination.md) remains a
positive supplied-construction result. Its follow-up review found no correction
needed and asked that the next proposal move upstream to a source-only rule.

## 1. What is established, and what must be chosen

For the restricted all-one-W, zero-channel A_OS path, the review's source-side
identity is confirmed directly against the retained native reads. At parent b,
with source orientation a to b to c, let

$$
q_0=-J_{ab},\qquad q_1=J_{bc},\qquad f_b=-(q_0+q_1).
$$

Then the fixed-split result satisfies

$$
q_1-q_0=\frac{C_c-C_a}{8},\qquad
(d_{\mathrm{fiber},0},d_{\mathrm{fiber},1})
=\bigl(2(q_1-q_0),-2(q_1-q_0)\bigr),
$$

and the first child difference is 4 dt (q1 - q0). The sign is physical: reversing
an edge reverses both its oriented current and incidence sign, leaving q intact.
The identity is conditional on this control and construction, not a formula for
arbitrary V4 currents or their rounded evaluations.

The lower mode is a balanced through-flow at b. Its nonzero q difference
therefore cannot, by itself, distinguish a parent needing fission from a
functioning mediator. Equal-activity algebra likewise separates arrangement
from magnitude: the larger lower-mode control with amplitude 9/64 is still
through-flow, despite matching the higher mode's absolute edge currents.

**The new choice proposed here is accumulation-driven physical growth.** A
parent with two strict inward participations may seed two sites only once its
resource can fund each activity-allocated child above the resource level of
the exterior site to which that child remains connected.

This is a new physical postulate, not a discovered upper capacity of one vertex,
not a proof that continued mediation is impossible, and not derived from the
core paper or accepted V4 contracts. The adjacent-resource benchmark needs
scientific review. Other benchmarks or meanings of fission remain alternatives.
The present choice intentionally allows symmetric fission; expressing a
pre-existing antisymmetric child distinction is not its claimed purpose.

Its rationale is specific: distinguish one site accumulating resource from a
route merely passing it through, and require that the proposed two sites be
individually resourced relative to their continuing exterior contacts. This is
a sufficient condition *within the proposed law*, not a necessary condition
for every possible lawful fission.

## 2. Causal inputs and deliberately narrow first domain

Use ATC-K0's already-admitted current-state projection and profile-correct
present read. The proposed evaluator consumes only graph incidence, current C
and the resulting authoritative J. The complete profile, reference, context
and current W/Z participate through that read; none is replaced by a proxy.
No reset, receipt, elapsed time, requested duration, event history, target read,
or future target performance enters the prescription.

This first executable proposal is restricted to the existing unit-measure
resource chart and finite simple graphs of maximum degree two, with at most
16 vertices and 32 edges. Only degree-two vertices are fission candidates.
Loops, parallel edges and higher-degree sources are outside this candidate's
domain and return `uncertified`, not a certified lack of fission. Leaves and
isolates in the graph do not supply a degree-two locus. These bounds and the
scope restriction are explicit; this does not complete generic graph support.

For an eligible vertex v, each of its two incident endpoint roles determines
one half-edge block. The unordered binary partition is unique. Let n_i be its
corresponding exterior neighbor, and define

$$
q_i=B_{v e_i}J_{e_i},\qquad i=0,1.
$$

The formula has a well-typed source-read interface across the ten families, but
nonempty scientific/native domains must still be demonstrated family by family.
Only the declared A_OS control has a fresh native onset test here. In particular,
this is not evidence for a nine-port partition or an all-ten event contract.

## 3. Proposed guard and physical prescription

First require **two strict inflows**:

$$
q_0<0,\qquad q_1<0.
$$

This implies positive parent resource tendency. Net accumulation alone is not
enough: one inflow and one outflow is excluded even if the net is positive.

For that case only, use the existing activity allocation convention. With
N = 2^16 and nearest-even rounding,

$$
k=\operatorname{round}_{\mathrm{even}}
  \left(N\frac{-q_0}{-q_0-q_1}\right),\qquad
\lambda_0=k/N,\qquad \lambda_1=1-\lambda_0.
$$

There is no zero-activity fallback: both activities must already be positive.
Swapping the half-edge blocks complements the share on this even grid.
Compute the same once-rounded resource values that the local linear map would
assign, without constructing or reading a target:

$$
\widehat c_i=\operatorname{RN}_{64}(\lambda_i C_v),\qquad
m_i=\widehat c_i-C_{n_i}.
$$

The **funding guard** is m0 > 0 and m1 > 0. All comparisons are exact rational
comparisons of the stipulated represented values. Equality is `no_event` at
that locus; there is no hidden epsilon, clipping or changed allocation after
a failed comparison. A rounded zero share cannot pass this guard against a
nonnegative neighbor. This arithmetic recipe does not prove unrounded sign
robustness or conservation of every rounded current/reset target sum.

Resolution over the whole admitted source domain is deliberately complete but
conservative:

| Active loci | Proposed result |
| --- | --- |
| None | `no_event` |
| Exactly one | `resolved`, with that parent, its unordered singleton blocks and shares |
| More than one | `unresolved`; no ranking by IDs, activity, hash or enumeration |
| Missing/invalid read, out-of-domain input or exhausted declared bound | `uncertified` |

This single-law rule does not select a runner-up after target rejection, choose
between growth and coarsening, or resolve simultaneous-event composition.

## 4. Relation to the existing construction

A later construction test would feed the resolved parent and the same two
half-edge blocks into ATC-2's binary builder: old-edge identities preserved,
one child added net, one child connector, declared reference seeding/KMASK,
context/backend reconstruction and explicit history reinitialization. The
source activities already determine the same shares, so the allocator must not
be adjusted after selection.

That is a proposed constructor binding, not a newly admitted target here. The
resource map still applies independently to actual current and reset; whole-
target charge, initializer and numerical admission can reject it. Failure must
preserve K0's committed ordinary poststate and cannot choose another locus or
weaken the source/target domains. No claim is made that this funding guard
guarantees target admission, persistence, burden reduction or a stable child.

The postulate describes physical growth at fixed unit measure. It is not neutral
field subdivision. It also is not CAN-B's missing negative structural mode:
functional, branch, tangent and mode-to-partition obligations for that route
remain unchanged.

## 5. Discrimination and bounded observed onset

The [research evaluator](../scripts/probe_atc_source_fission.py) checks the
review's signed-half-edge identity against the retained native source reads,
then applies the candidate to existing controls without rerunning them:

| Source control | F2 outcome | Reason |
| --- | --- | --- |
| Homogeneous | `no_event` | No strict inflows. |
| Higher-growth positive perturbation | `no_event` | Both participations are outward. |
| Lower-growth perturbation and its reversal | `no_event` | Balanced through-flow, not two inflows. |
| Small higher-mode reversal | `no_event` | Inward accumulation, but insufficient child funding. |
| Equal-activity larger lower mode, amplitude 9/64 | `no_event` | Still through-flow despite matching magnitudes. |
| Exact funding equality | `no_event` | Strict guard excludes equality. |

The last two rows use literal source equations, not new native admissions. A
separate literal funded-accumulation input passes. Ninety-six algebraic
vertex/edge-order/orientation checks include unequal activity shares. A source
with two active loci stays unresolved; higher degree and nonfinite inputs stay
uncertified. These are tests of the proposed rule, not native reachability
proofs for all synthetic inputs or a complete adversarial conformance suite.

For one deliberately chosen new A_OS source, let

$$
C(a)=(1-a,1+2a,1-a),\qquad a_0=127/512.
$$

The exact control equations give q0 = q1 = -9a/8, equal shares, and funding
margin 2a - 1/2. Thus the guard activates for a > 1/4. One ordinary step with
dt = 1/64 gives a1 = (521/512) a0 = 66167/262144. The native owner, actual
currents and independent literal equations agree:

| Observation | Each funding margin | Source prescription |
| --- | --- | --- |
| Before the ordinary step | -1/256 | `no_event` |
| After the ordinary step | 631/131072 | `resolved` at b |

The parent and unique unordered partition are therefore selected from the
ordinary poststate without consulting any target. Current W remains all-one;
the deliberately distinct reset remains unchanged. Pure reads/prescriptions
preserve their publication snapshots. **No topology event is attempted.**

This is one constructed, bounded onset observation. The evaluator does not
store a crossing flag, and the two observations do not establish a universal
historical detector, time-subdivision invariance or a natural occurrence rate.
The postulate and boundary were fixed before testing this near-boundary subject;
this is not a general parameter survey or proof of spontaneous formation.

The [source-bound result](../evidence/autonomous-topology-change/ATCSourceFissionProbe.json)
retains one fresh source admission, two explicit present reads, one ordinary
commit and zero events. Other controls reuse retained data or exact algebra.
No preceding native split campaign, browser suite or aggregate tooling rerun
was needed. Prior typed forensic traces and their original authority limits
remain in the bound predecessor; no new accepted graph node is introduced.

## 6. What requires review next

The central scientific choice is the **adjacent-resource funding benchmark**.
It expresses a new accumulation-to-growth hypothesis, not an accepted capacity
limit. Review should challenge whether it has an adequate physical meaning,
whether different edge/reference scales expose counterexamples, and whether
its selected constructions actually express that meaning beyond history-only
and allocation-induced effects. A successful predicate or admissible event
cannot validate this postulate by itself.

If the hypothesis merits continuation, next test the selected target and the
counterexamples, without changing the source rule to rescue a failed target.
Then establish profile-specific operative domains and decide whether/how to
generalize the partition beyond degree two. Combined birth/fission/coarsening,
repeated autonomy and native policy transport still require closure.

F2 is an additive research alternative, not a transformation or discharge of
the 35 origin claims or 28 debts. It bears on source-law/resolution DB-02/04,
physical discrimination DB-07/27, bounded lift DB-08 and eventual construction/
resource/history/integration DB-12–16. Structural DB-05/06 and stronger core/
formation/quotient DB-17/20/25 retain their prior activation conditions. All
thirty capability/family cells and native ATC implementation remain open.

The supplied follow-up review reports retained arithmetic/content checks, not
a production rerun; its linked external archive was not attached. This work
does not claim to reproduce that archive or infer user acceptance from its PASS.

Reproduce this source-only experiment from repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python implementation/investigations/grc9v4-constitutive-design/scripts/probe_atc_source_fission.py
```

The command prints a fresh record. Retained predecessors, accepted claims,
paper, specifications and production code are unchanged. No commit is made.
