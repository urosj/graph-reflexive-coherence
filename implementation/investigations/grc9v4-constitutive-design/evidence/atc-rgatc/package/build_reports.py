"""Create human-readable summaries from the retained certificate (no experiments)."""
from pathlib import Path
from fractions import Fraction as F
import json
B=Path(__file__).resolve().parent
c=json.loads((B/'RGATC-ER-Certificate.json').read_text())
def value(x):return float((F(x['lo'])+F(x['hi']))/2)
def num(x):return f'{float(F(x)):.12g}'
E=c['E'];R=c['R'];source=E['source'];rows=[]
for name,r in E['roles'].items():
    initial=float(F(r['transferred']['radius2']))**.5
    xs=[value(b['X']) for b in r['beats']]
    rows.append('| '+name+' | '+' | '.join(f'{x:.12f}' for x in (initial,*xs))+' |')
control=[]
for name,x in E['controls'].items():control.append('| '+name+' | '+' | '.join(f"{value(r['ratio']):.15f}" for r in x['beats'])+' |')
representation=[]
for r in R['representation']['roles']:
    maxima={k:max(F(b['errors'][k]) for b in r['beats']) for k in ('C','W','J','H')}
    drift=max(abs(F(b['charge_drift'])) for b in r['beats'])
    representation.append('| '+r['role']+' | '+' | '.join(f'{float(maxima[k]):.5e}' for k in ('C','W','J','H'))+f' | {float(drift):.5e} |')
text=r'''# RGATC-E — executed section-based fission and continuation

**Date:** 2026-09-24  
**Status:** execution and internal pressure completed; independent scientific review and source admission are still open.  
**Basis:** unchanged proposed RGATC-T/A completion and physical profile. This is not a native implementation claim.

## 1. From a section-envelope theorem to actual section evaluation

T/A supplied a sufficient invariant-section theorem and a complete bounded ATC implication using a whole-section envelope. It performed no numerical section queries. E now evaluates the actual completion-relative RG2b section and executes the frozen witness through ordinary evolution, a source-only event, both target reconstructions, and finite target continuation.

The physical profile is unchanged:

\[
\Delta=2^{-25},\qquad \kappa_H=2^{-32},\qquad
\tau_A=1/(8\log2),
\]

\[
\alpha=\beta=3/8192,\quad\gamma=3/4096,\quad
\chi=3/64,\quad\kappa_{Ah}=3/4,
\]

\[
p(c)=\frac{19}{4}c+\frac{c^2}{2\cdot65536}.
\]

The source and target remain the paired four-star and double-star with the same predeclared cutoff, unit references, and host positions. Neither the state witness nor the physical coefficients were retuned for E.

## 2. What the evaluator actually computes

A finite forward ladder from identity represents an iterated graph transform. Its inverse-output residual, interval arithmetic radius, input-box width, and global Banach tail provide a certified enclosure of Gamma at the requested state. See `RGATC-R-SectionEvaluator.md` for the proof and full error formula.

The default query uses 24 graph-transform levels and at most 16 inverse corrections. The maximum certified section radius across the retained E selected/restart reads was **MAXERROR**, against a required tolerance of 10^-34. The largest observed inverse count in those reads was **MAXSHOOTS**. Existence and uniqueness still come from T/A; numerical convergence is not substituted for that theorem.

Each query starts again at identity. Its auxiliary ladder is not a persistent geometry state and does not advance the physical clock. A query does not use the source section as a target section, a same-state CI root, or the last physical geometry as authority.

## 3. Actual ordinary onset and source-only selection

The frozen source is

\[
x_0=3-\Delta,\quad y_0=2^{-24},\quad
u_0=99/100-2^{-30},\quad v_0=99/100+2^{-30}.
\]

Here u and v are the two edge-weight values; the scalar u_0 is not the nonlinear-potential coefficient nu. Source resources are the paired charge-nine coordinates of T/A.

One successful ordinary RG step gives approximately

\[
x_1=ONSETX,\qquad y_1=ONSETY.
\]

The current read at the freshly reconstructed poststate section gives

\[
2^{16}\frac{J_0+J_1}{J_0+J_1+J_2+J_3}=RAWINDEX\quad\text{approximately}.
\]

Its certified interval lies strictly inside the round-even cell selecting

\[
\boxed{k=32768,\qquad\lambda=1/2.}
\]

The executed intervals refine the original T/A onset and allocation envelopes. The reset role and all target values are absent from selection. The E checker compares the fresh event read to an independent new query at the actual poststate, not to the root/section that drove continuity.

## 4. RG2b is numerically distinguished from CI

The initial source section has

\[
(\Gamma_s(X_0)-I)_{00}\approx 3.479096496200432\times10^{-18},
\]

whereas the source event section has

\[
(\Gamma_s(X_1)-I)_{00}\approx 3.479095783579768\times10^{-18}.
\]

The independent fresh-section and generated-geometry enclosures agree with the lagged identity

\[
\Gamma(X^+)=I+\kappa_HS(X,\Gamma(X)).
\]

The same-state CI residual is instead nonzero. Its source (0,0) entry is approximately

\[
7.126206646516572\times10^{-25}.
\]

At the first current-target and reset-target states, the corresponding entries are approximately 1.3461305213654645e-23 and 2.310059747045977e-22. All are resolved by intervals that exclude zero, far above the section-error radius. The full signed residual arrays are retained.

This is a realization discriminator, not merely a nonzero-H flag. It does not claim a quantified long-run separation from every separately initialized CI trajectory.

## 5. Both-role topology continuation

The live poststate and the independent reset source receive the same selected share. Surviving leaf resources are unchanged; parent resource is split conservatively; old W follows exact edge lineage; only the bridge receives W=1.

Each target then reconstructs Gamma on the new graph independently. No source geometry is transported. The two initial target (0,0) increments are approximately 2.3348156009551738e-17 for current and 3.7210388131961985e-16 for reset. Their complete selected currents and structural sources are checked as well.

Three ordinary target beats per role were executed. The radius X=||C-(3/2)1|| is approximately:

| Role | At transfer | Beat 1 | Beat 2 | Beat 3 |
|---|---:|---:|---:|---:|
TARGETROWS

Each observed interval ratio satisfies the frozen-duration theorem's bound

\[
X^+/X<1-\frac34\Delta.
\]

At this tiny duration, the target does not jump below 2/3 in its first beat. That larger-step assertion is neither used nor claimed. The positive invariant 3/2 ball supplies the correct target domain.

## 6. Counterfactual controls

The no-split and one-time W-reset-only controls are taken from the live post-onset source. Each executes two further actual RG beats. Their contrast ratios are approximately:

| Control | First further beat x^+/x | Second further beat x^+/x |
|---|---:|---:|
CONTROLROWS

Both satisfy the duration-dependent source-growth lower bound. The existing T/A theorem supplies the finite impossibility horizon of 536,870,912 further positive proposals. Those proposals were **not** executed. Likewise, indefinite target continuation and its asymptotic limit remain theorem conclusions, not inferences from three observed beats.

There is no state-level H-reset or Gamma-reset control because neither is authoritative state. Replacing the section by identity would be a different profile, not a history intervention.

## 7. Independent numerical evidence and internal pressure

The separate 110-digit Decimal implementation uses its own edge-local current equations, dense solve, floor/cutoff, writer, and a deeper 28-level graph transform. Across onset, both transfers, and target steps, **ECOMP** scalar values are checked inside the reference enclosures.

An additional complete transformed-coordinate campaign supplies **CCOMP** scalar checks. Elementary-function and auxiliary-completion comparisons supply **ACOMP** more. These are numerical consistency checks, not statistical samples establishing the global theorem.

Wrong-stage writer alternatives are numerically distinguishable: a stale descriptor and a poststate current do not reproduce the actual W writer. H-only corruption with unchanged J is rejected. Both exact-boundary and numerical-error-budget failures are retained in R.

## 8. Finite represented publication

Four fixed-Delta steps per actual target role compare exact-profile reference continuation with binary64 C/W publication. The section continues to target the original exact-tau completion; the numerical writer uses the declared rounded tau. A local Lipschitz bridge bounds the resulting RG invariance defect rather than pretending it is zero.

Maximum errors over those four steps are:

| Role | C | W | J | Reconstructed H | Absolute charge drift |
|---|---:|---:|---:|---:|---:|
REPROWS

The budget is 10^-10 separately in C/W/J/H. Charge drift is retained, not repaired, and rounded states never acquire the exact-charge-nine return theorem. Internal scientific stages are not all binary64, and H is not serialized as state.

## 9. Disposition

RGATC-E is executed at the frozen proposed T/A scope. The bounded reference portions of R described in `RGATC-R-Scope.md` are implemented and internally tested. The program has progressed from a theorem about an unknown section to a reproducible finite section-based execution with numerical error accounting.

The scope remains one conservative completion and profile, paired graphs, one event, and bounded numerical continuations. Independent review of the completion/theory/evaluator, formal source/profile admission, native implementation, long-horizon numerical guarantees, practical larger domains, active environments, repeated events, and aggregate ATC-2 are not claimed.

No debt ledger was modified. See `RGATC-ER-Certificate.json` for complete data and code bindings; its record digest is `DIGEST`.
'''
# Source weights are conventionally u_0 and v_0; avoid the nu naming ambiguity.
text=text.replace('\\nu_0=99/100-2^{-30}', '\\quad u_0=99/100-2^{-30}')
text=text.replace('Here u and v are the two edge-weight values; the scalar u_0 is not the nonlinear-potential coefficient nu. ', 'Here u and v denote edge weights, distinct from the potential coefficient. ')
replacements={'MAXERROR':num(c['proof_constants']['max_E_section_error']),'MAXSHOOTS':str(c['proof_constants']['max_E_inverse_shoots']),
 'ONSETX':f"{value(source['x_after']):.15f}",'ONSETY':f"{value(source['y_after']):.15g}",'RAWINDEX':f"{value(source['raw_index']):.14f}",
 'TARGETROWS':'\n'.join(rows),'CONTROLROWS':'\n'.join(control),'REPROWS':'\n'.join(representation),
 'ECOMP':str(E['independent_scalar_comparisons']),'CCOMP':str(R['covariance']['comparisons']),
 'ACOMP':str(R['boundaries']['arithmetic_and_auxiliary_oracle_comparisons']),'DIGEST':c['record_digest']}
for a,b in replacements.items():text=text.replace(a,b)
(B/'RGATC-E.md').write_text(text)
status=dict(schema='rgatc_er_scope_disposition_v1',record_digest=c['record_digest'],
 independent_acceptance=False,origin_debts_modified=False,realization_local_debts_modified=False,
 implemented=['certified finite invariant-section evaluator','exact frozen witness onset and source-only selection',
 'both-role target reconstruction','finite target and unsplit controls','independent Decimal checks',
 'one full coordinate-covariance transformation','atomic research owner and physical replay','bounded conditional research dispatcher',
 'finite binary64 publication bridge','local represented RG-invariance defect bound'],
 open=['independent review of T/A and E/R','formal source/profile admission','native completion/current/solver/transaction implementation',
 'uniform finite-work success on the full theoretical domain','all-binary64 internal conformance','indefinite numerical conservation and continuation',
 'practical larger positive beat/gain domains','active exterior graphs','repeated-event/non-Zeno results','aggregate ATC-2 closure'])
(B/'RGATC-ER-Disposition.json').write_text(json.dumps(status,indent=2)+'\n')
