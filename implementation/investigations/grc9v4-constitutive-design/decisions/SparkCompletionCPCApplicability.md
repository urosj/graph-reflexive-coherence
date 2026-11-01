# C_PC completion applicability — coupled resource and carrier research

2026-10-31. Bounded positive research under the
[all-ten programme](./SparkCompletionAllTenApplicability.md), on branch
`investigation/grc9v4-spark-completion` from `97470d96`.
Scientific review and claim/debt adjudication remain pending. The accepted
C_OS/C_CI authorities, SC-1 definition and historical execution records remain
unchanged. This work does not register a native evaluator or completed-spark API.

## Declared ordinary map

Use the preceding homogeneous quartic V'(C)=(C-2)^3-(C-2), unit reference
Hodges and transport, zero context, eta=1/1024, kappa_Phi=1/64, duration h=32,
tau_C=1, chi=zeta=kappa_H=1/2 and kappa_M=0. The new, explicit carrier time
is tau_PC=32, so a=exp(-1). This is a declared scientific parameter point,
not an amplitude or timing equivalence with another realization.

Let B be outward incidence, L=B^T B and O_ij the number of shared endpoints.
The independent state is (C,Z), with Z symmetric and supported on vertex stars.
Signed Z entries are lawful. One ordinary beat is

\[
H=I+Z/2,\quad j_0=-\frac1{1024}B^T\left(\frac1{64}BHB^TC-V'(C)\right),
\quad M=\frac34 I+HL,
\]
\[
y=M^{-1}j_0,\quad J=j_0+y/4,\quad f=H^{-1}y/2,
\quad S_{ij}=O_{ij}f_if_j/4,
\]
\[
C^+=C-32BJ,\qquad Z^+=aZ+(1-a)S.
\]

The current consumes old Z. The writer consumes the same pre-continuity
read's S. The fresh final (C+,Z+) read may be reused for the next beat only
when both subjects are identical. A post-continuity replacement source, a CI
root, an OS predictor, or a zeroed old carrier would change this map.

## Uniform admission and stationary carrier

The [declaration](../evidence/spark-completion/applicability/CPCDeclaration.json)
selects C in [0,4]^V and ||Z||_F<=1/64. Therefore
127/128<=lambda(H)<=129/128. M is similar through H^(1/2) to
3I/4+H^(1/2)LH^(1/2), giving
||M^-1||_2 <= (4/3)sqrt((129/128)/(127/128)). Connected-graph nonconstant
spectral lower bounds, multiplied by 127/128, remain above the selector cutoff
1/64 on both actual graphs. The physical current block is regular.

On the resource box, ||B^TC||_2<=4sqrt(m), |V'|<=6 and
||B^TV'||_2<=12sqrt(m). With ell=||L||_infinity, the declared bounds are

\[
j_* = \frac{\sqrt m}{1024}\left(\ell\frac{129/128}{16}+12\right),\quad
f_* = \frac{\|M^{-1}\|j_*}{2(127/128)},\quad
\|S\|_F\le f_*^2/2 < 1/64.
\]

Thus the carrier ball is invariant while C stays in its declared chart.
Resource-chart invariance is not asserted globally; the campaign certifies
its actual resource states, and the local full-state trap proves its own
invariance. Z=0 is a candidate stationary carrier, not a restriction of the
physical state or the continuation.

## Full sixty-dimensional trapping proof

Reuse the exact charge-21 center and P=(A0+11^T/15)^-1 metric from the accepted
construction, where A0=B[I+(3I/4+L)^-1/4]B^T. Reuse only these exact operands
and the spatial definition; prove this PC map independently. The closed set is

\[
\max(\|C-c\|_P,1024\|Z\|_F)\le r=2^{-20},\qquad 1^TC=21.
\]

It contains fourteen independent resource directions and all forty-six
independent symmetric star carrier directions. In particular its carrier
radius is 2^-30 and includes signed nonzero perturbations. Offdiagonal basis
elements are (E_ij+E_ji)/sqrt(2), so the carrier derivative is expressed in an
orthonormal Frobenius basis rather than treating duplicated entries as
independent histories.

For independent C and H, the derivative is obtained directly from

\[
dj_0=-\eta B^T[\kappa B(dH)B^TC+(\kappa BHB^T-V''(C))dC],
\]
\[
dy=M^{-1}(dj_0-dH\,Ly),\quad
df=H^{-1}(dy/2-dH\,f),\quad dJ=dj_0+dy/4,
\]
\[
dS_{ij}=O_{ij}(f_i\,df_j+f_j\,df_i)/4,\quad dH=dZ/2.
\]

These include both H consumers and both physical update blocks. A 512-bit
Arb calculation encloses the derivatives on a coordinate box containing the
whole trap. Let A_max bound ||A0||_2 and t=tr(P)-1. The established symmetric
reference derivative has P-norm bound q0; the new block bounds are

\[
b_{CC}=q_0+\sqrt{A_{max}t}\|T_{CC}-T_{ref}\|_F,\quad
b_{CZ}=\sqrt t\|T_{CZ}\|_F,
\]
\[
b_{ZC}=(1-a)\sqrt{A_{max}}\|S_C\|_F,\quad
b_{ZZ}=a+(1-a)\|S_Z\|_F.
\]

The weighted rows certify
q=max(b_CC+b_CZ/1024,b_ZZ+1024 b_ZC)<0.997358 and
(1-q)r-||T(c,0)-(c,0)||>2.51e-9. This is contraction and strict self-mapping
of the complete physical state. A separate positive reference-submap margin
establishes a stationary reference resource C* in the same ball. At Z=0,
BJ=0 and the positive reference mobility imply B^T Phi=0, hence J=f=S=0.
Thus (C*,0) is a fixed point of the full PC map; full contraction gives its
local uniqueness. This justifies the stationary carrier without suppressing
its perturbations or its actual writes.

The complete qualified domains remain {p,private} and {satellite2,n2,n8}
throughout the same resource box in both chiral charts, including all
unqualified routing terminals. The numerical incidence is identical between
charts; their port-dependent classifications are checked separately.

## Actual source, event and two histories

Reuse the exact source resource prestates from SC2SourceBeat, not the OS or
CI poststate. Declare current source Z=+2^-16 I and reset source Z=-2^-17 I.
Execute one actual current PC beat, including its carrier write, then take
the fresh whole read at (C+,Z+). The resulting source is positive, saturated
at v, trigger-eligible, and has its complete qualified parent. Reset is not
advanced. Both source histories are retained, including their nonzero carriers.

Literal D11 expansion transfers actual current postbeat resources and the
independent reset resources with shares (1/64,31/32,1/64), zero core and copied
exterior. Exact incidence conservation and shares summing to one prove charge
21; interval overlap with 21 alone is not the conservation proof.

The selected persistent-to-persistent event rule is
`event_loss_and_zero_target_carrier_v1`: archive both actual source histories,
record explicit carrier-history loss, and initialize all 256 dense target
carrier entries to zero. This is a lawful event disposition, not native
exponential release or identity transport. Subsequent ordinary beats regenerate
and consume nonzero carrier history.

| History | First observed final basin roster | Certified full C/Z trap entry | Two-beat window end | Live gain |
| --- | ---: | ---: | ---: | ---: |
| Current | 100 | 849 | 851 | 1 |
| Independent reset | 117 | 817 | 819 | 0 |

The two positive beats have elapsed duration 64. The full-map trap proves
subsequent exact persistence. These are sufficient certified entry/completion
times, not earliest mathematical times. Matching the earlier CI step counts
does not establish identical dynamics or equality of trajectories.

Both new histories were executed at fixed 8192-bit Arb precision, with a
1024-step horizon and 3600-second cap per role. Current/reset took about
70.85/68.21 seconds, respectively. No precision switch, projection, clipping,
cached trajectory, tolerance relaxation or previous-family entry reuse occurs.
The [preflight](../evidence/spark-completion/applicability/CPCPreflight.json)
verified cache hits and the single read/write cadence before the long jobs.
Only full-graph-keyed exact constants are cached. Multiple derivative right
hand sides share solves; one fresh final full-state read is reused on its
identical next-step subject.

The [current](../evidence/spark-completion/applicability/CPC-current.json.xz)
and [reset](../evidence/spark-completion/applicability/CPC-reset.json.xz)
archives retain all 1,670 C/Z states, classifications and full read checkpoints.
They compress 20,816,415 JSON bytes to 2,434,380 bytes. Outward 112-bit storage
enclosures are for inspection, never fed back into evolution or called exact
replay checkpoints. Reproduction starts from exact inputs at declared precision.

## Review, claim boundary and continuation

The [repository scientific review](../evidence/spark-completion/applicability/review/CPCScientificReview.md)
and [checks](../evidence/spark-completion/applicability/CPCChecks.json) distinguish
the certified original runs, fresh full-map mathematics and retained consistency
checks. Fresh/saved read or recurrence overlap is consistency only, not an
independent proof that the saved enclosure contains the exact trajectory.
Proof calculations use fresh enclosures. No independent second reviewer or
second full-precision long replay is claimed.

This supplies three proposed bounded conditional claims: lawful full C/Z read
and writer domain, full-state stationary/trapping result, and actual
source/event/approach/positive-window completion. `SC-APP-DEBT-C_PC` remains
open pending scientific review and explicit adjudication. The
[research progress record](../evidence/spark-completion/applicability/CPCResearchProgress.json)
is separate from the immutable accepted C_CI ledger and authority.
After acceptance, propagate authority → proposal/paper → specification and
route native numerical/lifecycle obligations to P9-9.1a. C_CI_PC follows in
the research order. Aggregate P9-10.5/10.6, hierarchy and G4 remain open.

The side-tool exposes `/api/spark-completion/applicability/research`, indexed
sources, a browser research panel and notebook cell `spark-completion-research`.
Refresh checks hashes and scope only; it does not execute scientific trajectories.

```bash
.venv/bin/python implementation/investigations/grc9v4-constitutive-design/scripts/test_spark_completion_pc.py
.venv/bin/python implementation/investigations/grc9v4-constitutive-design/scripts/check_spark_completion_applicability_pc.py --check --role current
.venv/bin/python implementation/investigations/grc9v4-constitutive-design/scripts/check_spark_completion_applicability_pc.py --check --role reset
.venv/bin/python implementation/investigations/grc9v4-constitutive-design/scripts/check_spark_completion_pc_reconciliation.py
```

`--run` refuses to overwrite a retained execution and requires a matching
optimization preflight. Routine restart checks do not repeat the campaign.
