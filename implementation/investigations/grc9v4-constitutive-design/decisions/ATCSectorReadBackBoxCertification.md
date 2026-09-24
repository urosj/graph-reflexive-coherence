> Relocation-only maintenance: repository paths and dependent identities were
> rebuilt before first commit. Scientific statements, numerical results and
> review verdicts are unchanged; the new identities are not an independent
> reviewer rerun. Earlier byte-preservation statements describe the pre-move stage.

# CAN-LSF — source and entry certification over the original Read-Back box

**Status:** new bounded mathematical certificate, pending independent review.
The [second adjudication](./ATCSectorReadBackPointAdjudication.md) accepts only
the previously reviewed enabled point and conditional target theorem. This
new [certificate](../evidence/autonomous-topology-change/ATCSectorReadBackBoxCertificate.json)
does not enlarge accepted scope by itself. The original proposal, point
certifier/certificate and both earlier adjudications remain unchanged.

## 1. Statement and unchanged domain

For every fixed parameter tuple in the original closed box

$$
\chi_A\in[1/32,1/16],\quad\gamma\in[1/2048,1/1024],
\quad\kappa_H,\kappa_{Ah}\in[1/2,1],
$$

retain the same prepared C0,W0, affine potential, exact paired four-star,
unit references, alpha=beta=0, a=19/4, h0=1/8 and tau_A=h0/log(2). The complete
one-pass equations, reference-selected source operand, source guard, dyadic
allocator, funding, binary surgery, role-local edge lineage and new-bridge
seed one are unchanged. No resource scaling, generic initial-state
perturbation, descriptor-channel or other-realization extension is made.

The outward enclosure proof certifies, uniformly over this box:

- Initial inactive guard and an admitted first ordinary beat with actually
  consumed Read-Back, generated geometry and gamma-dependent writing.
- Strict paired-sector separation, source guard, inflow/cone and funding
  margins at that first committed poststate; one eligible parent only.
- Enabled unsplit resource rejection at attempt 10 after nine admitted beats;
  resetting only W at the event state rejects at attempt 7 after six admitted
  beats. OS residuals remain admitted at both rejecting attempts.
- The source's prescribed k belongs to a conservative integer hull
  **30378–31236**. Every potentially reachable bin in it is covered; the proof
  does not assert that every one of those integers actually occurs.
- Every prescribed current/reset target's first beat enters the reviewed
  return domain. Therefore both roles continue positively indefinitely with
  q=9209/10240, resources above 5/6 and W tending to one.

This is a theorem about the fixed prepared source and this parameter box,
not the general implication "old spectral guard positive implies full-feedback
obstruction" for arbitrary states. Native realization/profile/owner admission,
formation and generic ATC-2 closure remain separate.

## 2. Dependency-preserving source coordinates

The reviewed structural symmetry is invariant for all scalar parameter tuples
in the box, not merely its enabled corner. Denote paired resources r_u,r_v,
parent resource s, and paired histories u,v. At charge nine set

$$
x=s-(r_u+r_v)/2,\quad y=(r_u-r_v)/2,\qquad
r_u=(9-x)/5+y,\quad r_v=(9-x)/5-y,\quad s=(9+4x)/5.
$$

This is an exact coordinate reduction on the already-proved invariant
subspace, not a new partition rule or a projection of approximate equalities.
With d_u=y-x and d_v=-y-x, the two reference baseline currents are exactly

$$
b_u=u[(3u+2v-a)x+(-3u+2v+a)y],
$$

$$
b_v=v[(2u+3v-a)x+(-2u+3v-a)y].
$$

Let j_i=F(b_i) be the selected reference current and f_i=chi_A q(b_i)j_i
the reference structural form. The normalized source star gives

$$
t_u=\tfrac32 f_u^2d_u+f_uf_vd_v,\qquad
t_v=f_uf_vd_u+\tfrac32 f_v^2d_v.
$$

Thus the fresh baselines are b_u+delta_u and b_v+delta_v, where

$$
\delta_u=-\kappa_H\kappa_{Ah}u(3t_u+2t_v),\qquad
\delta_v=-\kappa_H\kappa_{Ah}v(2t_u+3t_v).
$$

Select their fresh currents J_u,J_v with the unchanged read equation, then

$$
x^+=x+\tfrac5{16}(J_u+J_v),\qquad
y^+=y+\tfrac1{16}(J_v-J_u),\qquad
W_i^+=\sqrt{W_i\exp(-\gamma J_i^2/2)}.
$$

The enclosure proves floor inactivity on every consumed stage/writer; reject
resource failure before any writer. The source OS residual is bounded using
H>=I and ||H^-1 r||<=||r||:

$$
\|\Delta H\|_F\le
2\kappa_H(f_u^2+f_v^2+r_u^{\rm fresh\,2}+r_v^{\rm fresh\,2}),
$$

where r_fresh is the fresh Read-Back flux, not neighbour resource. This is a
triangle/trace upper bound, not an extra corrector. It proves the stipulated
operator-norm admission. Three exact rational matrix comparisons pressure the
reduction's algebra; the displayed identities establish the general reduction.

The [checker](../scripts/certify_atc_sector_readback_box.py) uses intervals
containing the entire parameter box in each operation, not sampled corners.
Forgetting correlations between uses only enlarges the enclosures. No parameter
subdivision or shrinking is used. The coordinate reduction avoids cancellation
from repeatedly reconstructing and subtracting large dependent vertex terms.

## 3. Source bounds and enabled counterfactuals

The following are deliberately widened rational consequences of the retained
dyadic endpoints; terminating decimals denote exact rational bounds.

| Quantity throughout the original box | Certified range |
| --- | --- |
| Event-state sector separation | (0.01246, 0.01257) |
| Old/source spectral guard margin | (0.03075, 0.03101) |
| Smallest selected reference inflow | (0.09912, 0.10057) |
| x | (3.59460, 3.59528) |
| y | (0.00430, 0.00444) |
| First child funding | (1.0818, 1.1436) |
| Second child funding | (1.3703, 1.4322) |
| No-split ninth-beat minimum resource | (0.00336, 0.05058) |
| No-split tenth proposed minimum | (-0.28553, -0.20014) |
| Reset-only sixth-beat minimum | (0.07764, 0.10644) |
| Reset-only seventh proposed minimum | (-0.19655, -0.14203) |

The maximum certified source OS residual upper bound is below 0.00002771,
far below 1/512. The counterfactuals therefore certify resource obstruction,
not an OS tolerance failure. Neither counterfactual is a physical selector
input. The committed-state reference read determines the one prescription.

## 4. All possible prescribed bins, not one favored target

The source enclosure gives

$$
30377.91<2^{16}\frac{A_u}{A_u+A_v}<31235.56.
$$

Outward tie-aware integer bounds produce the conservative k hull 30378–31236.
Ties are not resolved by choosing a target: all possible round-even outputs
are retained. This is broader than the exact reachable set, which is not
computed or claimed.

The first direct interval attempt across the entire share hull gave a
current-target squared-distance upper bound about 0.54014, above 4/9. That
was an inconclusive enclosure, not evidence of physical failure. The final
proof divides the **integer outcome hull**, not the parameter box, into eight
consecutive cells. Every cell must pass both roles:

| Inclusive k cell | Current squared-distance upper bound | Reset upper bound |
| --- | --- | --- |
| 30378–30485 | 0.29683 | 0.37700 |
| 30486–30593 | 0.29324 | 0.37317 |
| 30594–30701 | 0.28982 | 0.36950 |
| 30702–30809 | 0.28655 | 0.36599 |
| 30810–30917 | 0.28344 | 0.36264 |
| 30918–31025 | 0.28049 | 0.35946 |
| 31026–31133 | 0.27770 | 0.35643 |
| 31134–31236 | 0.27374 | 0.35199 |

Each cell encloses even the continuous shares between its integer endpoints.
These are universal proof cells, not physical alternative targets: each actual
source still produces exactly one k. The certificate checks that the cells
cover every integer in the hull exactly once. No successful cell can replace
a failing prescribed cell, and no result feeds back into the allocator.

All first target resources are positive. All squared deviations are below
0.37700<4/9; all target histories lie strictly above exp(-1/8) and at most one.
The largest target OS residual upper bound is below 0.00047609<1/512.
Charge is exactly nine by incidence and transfer column identities, not by
summing independent interval endpoints. The passed uniform target theorem
therefore supplies the infinite tail for every actual source parameter tuple.

## 5. Uniform nonvacuity and exponential regression hardening

At the initial beat the reference forms have strict positive lower bounds,
and both fresh-baseline changes delta_i have strict positive lower bounds.
Where the floor is inactive,

$$
q'(b)=\tfrac{\gamma b}{2}(1-q(b)^2),\qquad
F'(b)=\frac1{1-\chi_A q(b)}+
\frac{\chi_A bq'(b)}{(1-\chi_A q(b))^2}\ge\frac{16}{17}.
$$

Floor inactivity holds also between the two baselines: b^2 cannot exceed
the larger endpoint square. Thus the positive baseline change implies a
uniform selected-current gap greater than 0.00000867 per contact. Nonzero
reference form, positive geometry gains and the nonzero consumed baseline
change certify generated/consumed geometry; strict writer targets below one
certify the gamma-dependent write. These statements concern the relevant
initial beat, not nonzero currents forever at the eventual equilibrium.

The reviewer suggested deterministic nonzero exp probes. The successor checks
-1/2048, -1/8, -3/2, -10 and -100 against **independent exact rational** brackets:
for t>0, a positive Taylor sum S_N(t) is a lower bound for exp(t), and

$$
\exp(t)\le S_N(t)+\frac{t^{N+1}/(N+1)!}{1-t/(N+2)}
\quad(N+2>t).
$$

Reciprocation brackets exp(-t). Each entire independent bracket lies inside
the reviewed kernel's outward interval. No libm/Decimal oracle or edits to
the accepted point certifier are needed. All five probes pass. This is evidence
hardening, not a new debt or a change in scientific scope.

## 6. Reproduction and review boundary

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python implementation/investigations/grc9v4-constitutive-design/scripts/certify_atc_sector_readback_box.py
```

The command prints the new record; it does not overwrite prior evidence or
rerun the original point trajectory. Its identity checks preserve the accepted
point/adjudication inputs. This box theorem still requires independent review
before a further scope enlargement. It does not close formation, native/source
admission, other families, the general guard implication or aggregate ATC-2.
