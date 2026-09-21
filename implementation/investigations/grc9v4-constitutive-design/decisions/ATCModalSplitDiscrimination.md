> Relocation-only maintenance: repository paths and dependent identities were
> rebuilt before first commit. Scientific statements, numerical results and
> review verdicts are unchanged; the new identities are not an independent
> reviewer rerun. Earlier byte-preservation statements describe the pre-move stage.

# ATC — modal discrimination under one fixed supplied split

**Status:** research follow-up to the independent review of
[refinement discrimination](./ATCRefinementDiscrimination.md). No endogenous
fission law, scientific acceptance, capability closure or production change.

## 1. Review correction and retained boundaries

The review correctly identified an explanatory error: every current frame in
the five retained modal trajectories has W_A = (1,1). The writer executes but
does not change that value in the declared zero-exponent control. The event
initializer changes the distinct reset W to ones; this is not current-history
evolution during the ordinary trajectories. The explanatory note is corrected;
the original script and execution record remain byte-identical.

The review also supplied three useful clarifications, now incorporated there:

- Charge conservation and preservation of the same constant field force m = n
  for a linear map between unit-measure coordinate spaces. Increasing dimension
  cannot retain both properties.
- For the restricted exact fixed-W control, the secant is
  eta kappa_c times the squared norm of L_W delta divided by the squared norm
  of delta. Positivity across nonzero charge-zero directions on a connected
  graph therefore does not identify a newly reached fission condition.
- A degree-two locus has one nontrivial unordered partition. Failure of a
  particular sign-based modal lift is not an impossibility of partitioning it.

The review reports independent retained-arithmetic, digest, map and trace
checks, not a production rerun or reconstruction of the accepted forensic graph.
Its linked check archive was not part of the supplied attachment. We do not
claim to have executed that archive. The local follow-up independently checks
the stated matrix identity and tests the new predictions natively.

## 2. Prediction fixed before execution

Keep the same A_OS zero-channel parameters, source path, target reference,
history policy and center partition as the prior supplied split. Use the
source order (a,b,c) and target order (a,c,v0,v1):

$$
TC=(C_a,C_c,C_b/2,C_b/2),\qquad
P(y_a,y_c,y_0,y_1)=(y_a,y_0+y_1,y_c),\qquad PT=I.
$$

Target topology is the path a–v0–v1–c. With all-one target W, eta = 1/4 and
kappa_c = 1/2, the literal control equations give

$$
f_{\mathrm{target}}=\tfrac18 L_{\mathrm{target}}^2 TC,
\qquad
(I-TP)f_{\mathrm{target}}
=\begin{pmatrix}
0\\0\\(C_c-C_a)/4\\(C_a-C_c)/4
\end{pmatrix}.
$$

The script derives and checks this coefficient matrix with exact rational
matrix products, independently of native differential operators or an
eigensolver. These are statements about the stipulated control law, not an
all-product structural Hessian or a new selection mechanism.

At epsilon = 1/64 and dt = 1/64, the predictions are:

| Source resource | Child-fiber tendency | Child resource difference after one target step |
| --- | --- | --- |
| (1,1,1) | (0,0) | 0 |
| (1,1,1) + epsilon (1,-2,1) | (0,0) | 0 |
| (1,1,1) + epsilon (1,0,-1) | (-1/128,1/128) | -1/4096 |
| (1,1,1) - epsilon (1,0,-1) | (1/128,-1/128) | 1/4096 |

All three nonuniform sources have equal incident absolute-current magnitudes
within each source. The existing activity allocator therefore gives the same
equal shares. The fixed partition and target are not selected by trying
possible outcomes, and no allocator parameter is changed to favor a mode.

## 3. Focused native comparison

The [follow-up script](../scripts/probe_atc_modal_split.py) reuses the uniform
control from the exact
[predecessor record](../evidence/autonomous-topology-change/ATCRefinementDiscriminationProbe.json).
Only the higher-growth perturbation and both signs of the lower-growth
perturbation receive new native executions. The source preimages are the
previously declared modal sources, before their ordinary trajectories.

Each execution must:

1. Admit the actual source with its distinct current/reset resources and W.
2. Recompute the source current and compare with independent literal equations.
3. Rebuild the stipulated partition using those currents; verify the complete
   target, backend and resource map match the previously fixed construction.
4. Execute the supplied event with independently mapped current/reset, target
   initialization and whole-target readmission, without changing admission domains.
5. Check the native target tendency, exact child-fiber prediction and decomposition
   into coarse and fiber residuals.
6. Execute one ordinary target step, checking the complete resource update,
   signed child difference, unchanged current W and preservation of actual reset.

The [new execution record](../evidence/autonomous-topology-change/ATCModalSplitProbe.json)
retains sources, the shared complete target/backend, requests, event/ordinary
receipts, numerical reads, independent oracles and source hashes. Its uniform
comparison is explicitly labeled retained evidence, not a fourth fresh run.
The earlier 22-read/12-step campaign is not rerun. Previous typed forensic traces
remain in the bound predecessor with their original dispositions; this follow-up
does not reconstruct or admit a new forensic graph.

**Result: all three predictions passed natively.** The higher-growth case has
zero child-fiber tendency and zero child difference after continuation. The
lower-growth cases have opposite fiber tendencies of magnitude 1/128 and
opposite child differences of magnitude 1/4096. The exact coarse/fiber
decomposition also holds in each case. Current W remains all ones; actual
reset is independently mapped/reinitialized and then unchanged by the step.

The focused run contains three fresh source admissions, nine explicit
present-state reads, three supplied-event commits and three ordinary commits.
Admission can perform additional internal stages. The reused uniform case is
not included in these new-run counts. No broader campaign was executed.

## 4. Interpretation and next scientific question

This comparison discriminates *growth of a source mode* from *expression of a
child-resource distinction under the chosen construction*. It cannot by itself
establish that the lower-growth mode ought to cause fission, that children form
stable identities, or that a source-side prescription has been found.

The causal question remains upstream: what source-only physical condition
justifies fission and determines a covariant partition? The target response is
a test of a proposed interpretation, not a circular input to that condition.
The fixed-unit-measure growth direction remains provisional; no measure-aware
extension, temporal history store or post-event search is introduced.

The inherited obligations remain explicit: physical discrimination (DB-07),
mode/half-edge lift (DB-08), resource/reference/history and target integration
(DB-13–16), and operation meaning (DB-27). Qualified structural-functional
debts (DB-05/06), stronger identity/formation claims (DB-17/20), complete quotient
claims (DB-25), all-product capability closure and the native dispatcher remain
unresolved in their existing scopes. No original claim/debt record is rewritten.

Reproduce just this follow-up from repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python implementation/investigations/grc9v4-constitutive-design/scripts/probe_atc_modal_split.py
```

It prints a fresh record and never replaces retained evidence. No accepted
history, original paper, specification or production source changes.
