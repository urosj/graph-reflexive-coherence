# C_CI completion applicability — joint root and full physical map

2026-10-31. Research successor to accepted C_OS SC-3, under the
[all-ten applicability programme](./SparkCompletionAllTenApplicability.md).
The shared scientific criterion is unchanged. The bounded result is now
[adjudicated through C_CI SC-3](./SparkCompletionCCISC3Authority.md); it adds no
accepted native support.

## 1. Actual CI equations, not an OS substitution

Keep the declared homogeneous quartic and exact parameter point from C_OS:
eta=1/1024, kappa_Phi=1/64, h=32, chi=zeta=kappa_H=1/2, tau=1,
kappa_M=0, unit reference Hodges/weights and zero context. The source and
D11 target graphs are unchanged. Only the current/geometry timing changes.
Let B be outward incidence, L=B^T B and O_ij the number of shared endpoints.
In causal-flat coordinates f, define

$$
H(f)=I+Q(f),\quad Q_{ij}(f)=\frac{O_{ij}}8 f_i f_j,
\qquad M(H)=\tfrac34 I+HL,
$$

$$
j_0(C,H)=-\eta B^T\left(\kappa BHB^TC-V'(C)\right),\quad
 y=M(H)^{-1}j_0,\quad J=j_0+\tfrac14 y,
$$

$$
F(C,f)=\tfrac12H(f)^{-1}y(C,H(f)),\quad f=F(C,f),\quad
T_{\rm CI}(C)=C-32BJ(C,H(f(C))).
$$

This fixed point is equivalent to the joint current/geometry equation on the
declared invertible domain. The auxiliary f, J and H are reconstructed fields,
not new physical history. At the root the same causal source generates H and
is consumed by the current. OS instead evaluates one reference predictor and
one corrector. The nonlinear quartic is selected as a scientific binding;
its C_CI feasibility is new conditional research, not an existing native evaluator.

## 2. Uniform root existence and selection

On either actual graph let R=1/32, C in [0,4]^V and ||f||_infinity<=R.
Write s=max_i sum_j O_ij/8, ell=||L||_infinity,
b=||B||_infinity, a=||(3I/4+L)^-1||_infinity. These constants are computed exactly
with FLINT rationals. With d=s R^2, require d<1 and a*d*ell<1, and set

$$
u=(1-d)^{-1},\quad N=\frac a{1-a d\ell},\quad
j_* =2\eta(4\kappa b+6)+4\eta\kappa\ell d,\quad
 y_*=Nj_*,\quad f_*=\tfrac12u y_*.
$$

Here ||B^TC||_infinity<=4 and |V'(C)|<=6 on [0,4]. Neumann bounds give
||H^-1||<=u and ||M^-1||<=N. Differentiating at fixed C yields

$$
\|D_H F\|\le u\left[\tfrac12N(4\eta\kappa\ell+\ell y_*)+f_*\right]=L_H,
\qquad q_f=2sR L_H.
$$

The exact checks give f_*<R and q_f<1: approximately 0.026594 on the source
and 0.011467 on the target. Thus every C in the declared box has one selected
root in this ball. This is uniqueness **within the selected domain**, not
absence of all roots elsewhere. H is I plus positive star outer products at
real f. Connected-graph spectral separation and finite inverse bounds keep the
same selector/current domain; no zero mode is dropped or tolerance relaxed.

Newton operates only on midpoint proposals f0. The returned enclosure is
certified on the entire input C enclosure using

$$
\|f(C)-f_0\|_\infty\le
\frac{\sup_{C\text{ in input box}}\|F(C,f_0)-f_0\|_\infty}{1-q_f}.
$$

The proposal and enclosure must remain inside the selected ball. Precision and
iteration limits are explicit; failure is explicit. The physical trajectory
never follows a midpoint state. Batched multiple-right-hand-side solves evaluate
the same analytic partial derivatives without repeatedly factoring each matrix.

## 3. A new physical-map proof on the existing metric ball

Use the accepted target graph, exact charge-21 center c and radius r=2^-20.
Recompute the exact A0 and P=(A0+11^T/15)^-1 used in the C_OS certificate,
restricted to E={x:1^Tx=0}. This is reuse of the norm/domain, not reuse of
C_OS's derivative or trajectory. The ball has fourteen independent dimensions.

With independent C and f, compute all partial derivatives of j0,y,F,J, including
H in both the potential and Read-Back. Then

$$
D_C f=(I-F_f)^{-1}F_C,\qquad
D T_{\rm CI}=I-32B\left(J_C+J_f(I-F_f)^{-1}F_C\right).
$$

The uniform root theorem justifies this implicit derivative. The interval
calculation encloses it on the whole coordinate box containing the metric ball.
It includes the implicit geometry response; frozen-H derivatives are insufficient.
The reference derivative J_ref=I-A0 D_c/32 has the previously justified metric
bound q_ref. A fresh bound is

$$
q_{\rm CI}=q_{\rm ref}+\sqrt{a_{\max}t}\,
\sup\|D T_{\rm CI}-J_{\rm ref}\|_F<0.997296,
$$

where t=tr(P)-1. A fresh center evaluation gives

$$
m_{\rm CI}=(1-q_{\rm CI})r-\|T_{\rm CI}(c)-c\|_P
>2.5789\times10^{-9}.
$$

This proves strict self-mapping and full physical-map contraction. The inner
root contraction q_f is a separate, much smaller number and is not used as
physical stability. Complete domains {p,private} and {satellite2,n2,n8}, including
all unqualified terminals, are checked throughout the same box in both charts.
The theorem concerns exact equations; a represented native map still needs its
own full-step/charge/diagnostic certificate under SC-3.

## 4. Actual source and continuation subjects

Reuse the **exact initial source prestate**, not its OS poststate. Execute the
CI ordinary beat, then reconstruct the entire fresh CI event root at its actual
poststate. The source remains positive and hybrid-trigger eligible; its complete
qualified parent contains the expanded vertex. Apply literal D11 topology and
shares (1/64,31/32,1/64) to those actual postbeat resources. Zero core and copied
exterior remain unchanged. Exact incidence conservation and shares summing to
one establish charge 21. An interval containing 21 alone is not that proof.

Reset is not advanced. Its resource input may match the earlier reset subject,
but its CI root, target trajectory and completion applicability must be checked
anew. Both charts have the same ordered incidence, so numerical evolution is
shared while chart-dependent predicates are checked separately. The geometry
fixture's old resource templates are not event inputs: `initial_target` and
`source.actual_CI_poststate` in each new record identify the actual subjects.

The fixed run uses 8192-bit Arb, at most 1024 target steps per role, a 30-minute
cap per job and two further duration-32 beats after certified entry. Current and
reset run independently in parallel. Completion gain belongs only to current;
reset is an independently admitted comparison, never a second birth. Full
selected roots are captured at event, entry and completion. Per-step C enclosures,
complete basin rosters, root-error and positivity bounds are retained compactly.
Their 112-bit outward encoding is evidence storage, not trajectory rounding.
The initial development run accidentally fed the compact diagnostic box back
into evolution and lost resolvable edge order. The corrected recurrence retains
full-precision state; only the diagnostic/storage view is compacted. No failed
trajectory archive is retained, and no law, threshold or precision was changed.

Entry uses a directly enclosed P quadratic norm. The older OS entry procedure
used a more conservative Euclidean upper bound for the same norm. Different
certified entry counts therefore do not establish faster CI dynamics or earliest
mathematical entry; only each declared sufficient entry test is claimed.

## 5. Disposition

**Bounded positive research result; independent bounded review PASS and scoped
C_CI SC-3 adjudication complete.** The [review record](../evidence/spark-completion/applicability/review/CCIIndependentReview.md)
distinguishes the reviewer's independent checks from the repository's executions.
Joint-root/domain, full physical-map trapping and the actual source-to-window
chain are established on these declared subjects. The parallel runs finished
in approximately eleven minutes each, within their declared caps.

| Actual CI history | First certified trap entry | End of two positive beats | Live completion gain |
| --- | ---: | ---: | ---: |
| Current | 849 | 851 | 1 |
| Reset comparison | 817 | 819 | 0 |

Each observation window has elapsed duration 64. Both chiral charts retain the
complete domains {p,private} and {satellite2,n2,n8}. Event allocation alone has
only the parent basin. The recorded `first_spatial_gain` means the first observed
occurrence of the final complete basin roster (current 100, reset 117), not
certified trapping, completion or the earliest possible positive gain.

The [current](../evidence/spark-completion/applicability/CCI-current.json.xz) and
[reset](../evidence/spark-completion/applicability/CCI-reset.json.xz) records retain
every positive approach/window state and full selected-root checkpoints.
Lossless compression reduces their combined 7.27 MB JSON to 0.84 MB. Full
recurrence reproduction starts from exact inputs at the declared 8192-bit
precision; the compact 112-bit state enclosures suffice for retained subject,
diagnostic and entry/window checks, not bitwise continuation from a checkpoint.

Four focused scientific tests independently compare Picard and Newton roots,
the literal physical-current equation, analytic partials and full-map derivatives,
including zero-current and domain controls. The
[reconciliation checks](../evidence/spark-completion/applicability/CCIChecks.json)
recompute the actual CI source/transfer and entire f/H/J roots at saved event,
entry and completion subjects. Saved-versus-fresh root comparisons establish
**overlap consistency only**: two overlapping intervals need not both contain
the actual root. These comparisons do not independently recertify the saved
enclosures. Their enclosure provenance is the original certified recurrence;
downstream proof calculations use freshly certified root enclosures, as the
full-map trap calculation already does. Eight false-completion/root controls reject;
repeating the same research event produces no additional gain. This is research
accounting, not a native receipt or atomic production transaction.

The current
[applicability ledger](../evidence/spark-completion/applicability/ClaimDebtLedger.json)
records three accepted bounded conditional claims, their review boundaries
and separate forward native obligations.
Other eight families
remain uninvestigated for completion, not presumed compatible or impossible.

```bash
.venv/bin/python implementation/investigations/grc9v4-constitutive-design/scripts/check_spark_completion_applicability_ci.py --check --role current
.venv/bin/python implementation/investigations/grc9v4-constitutive-design/scripts/check_spark_completion_applicability_ci.py --check --role reset
.venv/bin/python implementation/investigations/grc9v4-constitutive-design/scripts/test_spark_completion_ci.py
.venv/bin/python implementation/investigations/grc9v4-constitutive-design/scripts/check_spark_completion_applicability.py
```

`--check` checks retained integrity/subjects and freshly recomputes the CI trap;
it does not replay the long recurrence. `--run` executes the declared recurrence
and refuses to overwrite a retained record. No native or accepted-graph claim
is created by either command.
