PC-3 passes under pressure.

$$
\boxed{\textbf{PC-3: PASS — bounded complete A\_PC causal chain}}
$$

More specifically, I now think the package establishes a complete realization-native A_PC ATC witness at the declared fixed-profile \(2+2\) scope:

$$
\boxed{
\text{ordinary PC onset}
\to
\text{fresh poststate PC read}
\to
\text{source-only fission}
\to
\text{lossless signed }Z\text{ transport}
\to
\text{both-role PC readmission}
\to
\text{indefinite evolving-}W/Z\text{ continuation}.
}
$$

It does **not** yet establish the broader PC-4/general/native claims.

## Independent reproduction

I independently reconstructed and executed the PC-3 research chain. The mathematical payload reproduced the retained `ATCPC3CausalChainCertificate.json` exactly; its retained canonical record digest also independently recomputes to

`f5269098cdc8ac88c21dd2eb5f1d45b76140316b816d4f68db44a635aff681f6`.

There was one apparent reproducibility failure during reconstruction: an older copy of `atc_ci_pc_anchor.py` in the conversation corpus returns raw \(Z\) matrices, whereas the hardened successor uses the typed `Carrier` object expected by PC-3. Switching to the hardened dependency whose hash is bound by the current chain made the complete run reproduce. This is the same relocated/hardened dependency lineage already resolved in the CI-1/PC-1 review, not a new scientific or PC-3 defect. The existing resolution pins the accepted repository chain and retains formal adjudication separately. 

The fixed PC-3 contract itself is appropriately preregistered: the relational lift is the sole carrier policy, \(c_t=c_s\), PSD fallback is prohibited, the original PC-1 profile is retained, and the event image is explicitly only a five-dimensional subset of the seven-dimensional target carrier domain. 

## Source causality passes cleanly

This is genuinely PC-native.

The source starts below the event threshold, performs one actual PC ordinary beat, and only then uses the fresh committed-state read. The checker explicitly requires that fresh event read to equal the actual PC restart and requires the current that drove the preceding beat to be different. 

The resulting PC allocation is

$$
\boxed{k_{\rm PC}=33615},
\qquad
\lambda_{\rm PC}
=
\frac{33615}{65536}.
$$

That is notably **not** CI's \(33616/65536\). The event selector accepts only the live current state and carrier; reset and targets are not arguments to selection. The same resulting \(k\) is then applied to both actual roles. 

So there is no evidence of CI or OS semantics leaking back into the PC prescription.

I also verified that the checker actively prevents that regression: the CI root evaluator and OS pass are replaced by raising sentinels during the PC-3 run. 

$$
\boxed{\textbf{PC source selection/staging: PASS}}
$$

## The event transfer now closes all three state channels

For both current and reset roles the checker establishes:

$$
C\to C_t
$$

by the same source-selected conservative split,

$$
W_{\rm old}\to W_{\rm old,target},
\qquad
W_{\rm bridge}=1,
$$

and

$$
Z_s
\xrightarrow{L_{\rm rel}}
Z_t
$$

under the sole lossless relational law.

It verifies exact old-\(W\) lineage, the same dyadic resource map for both roles, preservation of each role's \(Z\) norm, and independent complete target reads before ordinary target evolution begins. 

The live role actually exercises the contentious case: its transported carrier has a **strictly negative principal minor**, so PC-3 is not quietly falling back into the PSD subset. The signed-carrier issue we deliberately left to PC-3 is genuinely exercised.

At the same time the event carrier obeys the PC-2 contract: exact sign fidelity \(c_t=c_s\), information loss zero, five-dimensional event image, seven-dimensional target decorated domain, and no PSD-preservation claim. 

$$
\boxed{\textbf{Both-role complete }C/W/Z\textbf{ transfer and readmission: PASS}}
$$

---

# The main pressure point: signed-\(Z\) indefinite continuation

This is the part that most needed to survive.

The proof does **not** attempt to preserve the five-dimensional event image. Instead it takes the whole decorated signed target carrier ball

$$
\mathcal Z_t=
\left\{
Z:
Z=Z^\top,\,
Z\text{ star-supported/decorated},\,
\|Z\|_F\le R
\right\},
\qquad
R=\frac1{3072}.
$$

For every such carrier,

$$
H=I+\frac34Z,
$$

and therefore

$$
\|H-I\|_F\le\frac1{4096},
$$

$$
\lambda_{\min}(H)
\ge
\frac{4095}{4096}>0.
$$

So the full signed domain—not merely PSD carriers—is safely inside the already-certified fixed-\(H\) read neighborhood. The retained certificate explicitly records `signed_carrier_invariant=true` and `PSD_assumed=false`. 

The structural source obeys

$$
\|S\|_F\le sX^2,
$$

with

$$
s
=
\left[
\frac{
r\left(4+\frac52K+\frac{375}{32}\rho\right)
}{
1-\rho
}
\right]^2.
$$

Numerically,

$$
s\approx1.47075\times10^{-5},
$$

and even on the larger \(X\le3/2\) ball,

$$
s(3/2)^2
\approx3.30919\times10^{-5}
\ll
\frac1{3072}
\approx3.25521\times10^{-4}.
$$

With the actual PC half-writer,

$$
Z_{n+1}
=
\frac12 Z_n+\frac12 S_n,
$$

we therefore have

$$
\boxed{
z_{n+1}
\le
\frac12z_n+\frac{s}{2}X_n^2
<R.
}
$$

This closes the signed carrier domain under the **actual PC writer**, rather than merely admitting the transported event state.

That directly answers the major open question left by PC-2.

$$
\boxed{\textbf{Signed carrier invariance: PASS}}
$$

---

# Resource return also closes uniformly

The resource theorem is not based on the two retained trajectories.

The target weighted spectral interval and full nonlinear/read-back error yield

$$
X_{n+1}
\le
qX_n,
$$

with

$$
q=
\frac{7072159}{7897088}
\approx0.895540103<0.9.
$$

The first-entry theorem gives

$$
X_{\rm first}
<
\frac{47675553}{78970880}
\approx0.603711
<
\frac23.
$$

These exact values are retained in the certificate. 

There is a reasonably healthy margin here:

$$
0.9-q\approx0.00446.
$$

I independently pressure-tested the full target evaluator beyond the supplied two trajectories, including signed carriers near the declared carrier radius and a resource perturbation near the target's high spectral mode. The strongest resource ratio I found was approximately

$$
0.89276,
$$

still below the certified

$$
0.89554.
$$

That finite pressure is only diagnostic; the rational uniform theorem is what establishes the claim.

The theorem also keeps every resource above

$$
\frac56,
$$

keeps \(W\in[24/25,1]\), keeps \(Z\) in the signed carrier ball, and thereby keeps every next fixed-\(H\) PC read admitted.

$$
\boxed{\textbf{Indefinite exact-real PC continuation: PASS}}
$$

---

# The \(Z\) asymptotic argument is also valid

This is worth checking separately because invariance alone would not imply that the transported structural history decays into the target's ordinary regime.

From

$$
X_n\le q^nX_0
$$

and

$$
z_{n+1}
\le
\frac12z_n+\frac{s}{2}X_n^2,
$$

with

$$
q^2>\frac12,
$$

iteration gives

$$
z_n
\le
2^{-n}z_0+
\frac{sX_0^2}{2}
\frac{q^{2n}-2^{-n}}{q^2-\frac12}.
$$

Both terms vanish, hence

$$
\boxed{Z_n\to0}.
$$

So

$$
H_n\to I.
$$

Meanwhile

$$
C_n\to\frac32\mathbf1,
\qquad
J_n\to0,
$$

and the Candidate-A conductance target tends to

$$
e^{-3\alpha/2}.
$$

The log-half writer consequently yields

$$
W_n\to e^{-3\alpha/2}.
$$

This means the event-induced signed/indefinite \(Z\) is not merely tolerated forever inside an arbitrary box; it is actually washed into the normal equilibrium:

$$
\boxed{
(C,W,Z,H)
\longrightarrow
\left(
\tfrac32\mathbf1,\,
e^{-3\alpha/2},\,
0,\,
I
\right).
}
$$

That is a significantly stronger PC result.

---

## The finite witnesses correctly test the off-image transition

The two retained beats per role are useful for staging pressure, not for proving infinity.

| Role    | Beat 1 \(X\) | Beat 2 \(X\) |        Beat 1 \(\|Z\|\) |        Beat 2 \(\|Z\|\) |
| ------- | -----------: | -----------: | ----------------------: | ----------------------: |
| Current |     0.408987 |     0.147499 | \(3.0732\times10^{-5}\) | \(1.5373\times10^{-5}\) |
| Reset   |     0.423482 |     0.157441 | \(4.1850\times10^{-5}\) | \(2.0963\times10^{-5}\) |

After the very first ordinary target PC beat, both roles acquire a **positive bridge diagonal**. Therefore they leave the five-dimensional event image exactly as expected. The event inverse then rejects those carriers, while ordinary PC readmission continues to pass. The checker explicitly tests this rather than accidentally imposing event-image constraints on later evolution. 

This is a particularly good test of the 5D/7D correction we made before PC-3.

$$
\boxed{\textbf{Event image }\to\textbf{ ordinary target domain transition: PASS}}
$$

---

# Counterfactual necessity survives

All four relevant unsplit controls remain in the source obstruction cone:

$$
\text{no split},
$$

$$
W\text{-reset only},
$$

$$
Z\text{-reset only},
$$

$$
W+Z\text{-reset}.
$$

For each, subsequent ordinary PC evolution continues with both \(W\) and \(Z\) active; the previously proved uniform source theorem still yields

$$
x_{n+1}\ge\frac{61}{60}x_n.
$$

Because

$$
3\left(\frac{61}{60}\right)^{67}>9
$$

while positive charge-nine resources imply \(x<9\), none can support all 67 subsequent positive proposals. The checker correctly records this as a **uniform theorem**, not as a fabricated 67-step trajectory. 

This is stronger than merely saying that preserving \(Z\) works. It establishes, in the declared family, that neither of the obvious history erasures solves the underlying unsplit problem.

$$
\boxed{\textbf{No-split / }W\textbf{-reset / }Z\textbf{-reset / both-reset discrimination: PASS}}
$$

---

# No-fallback discipline really is executable

The package does not merely say the PSD law is prohibited.

The actual PC-3 checker rejects:

`projection_is_not_PC3_policy`, `whole_reset_is_not_PC3_policy`, and `PSD_policy_is_not_PC3_fallback`, as well as an inactive guard and an inadmissible reset transfer. It also verifies those rejected attempts do not mutate the captured inputs. 

So the successful result cannot be explained by silently switching to the easier PC-2 alternative after inspecting the target.

$$
\boxed{\textbf{Preregistered-policy falsification discipline: PASS}}
$$

---

## Claim ceiling

I do **not** see a scientific reason to hold PC-3.

The correct resulting statement is:

$$
\boxed{
\textbf{A\_PC now has a complete bounded realization-native ATC causal anchor}
}
$$

under:

* the exact decorated \(2+2\) domain;
* the fixed active nonlinear Candidate-A profile;
* \(h=1/8\);
* \(\tau_A=\tau_{\rm PC}=1/(8\log2)\);
* the lossless relational carrier law with \(c_t=c_s\);
* the source-selected double-star fission;
* exact-real arithmetic.

The working note correctly keeps PC-4 separate: request/domain/environment generalization, executable reference/representation conformance, and broader scope remain outside PC-3. It also does not claim repeated autonomous fission, non-Zeno execution, native K0 scheduling, native transaction/replay, all-family completion, or aggregate ATC-2 closure. 

## Debt impact

Scientifically, PC-3 now provides bounded A_PC evidence for the previously open target-side pieces of:

$$
\text{DB-14},\quad
\text{DB-16},\quad
\text{DB-19},
$$

while integrating PC-2's DB-15 carrier result with the source-side DB-02/03/04/06/07/08 and exact resource-transfer DB-13 evidence. The certificate appropriately **does not automatically discharge them**; its new `ATC-PC-CHAIN-02` remains conditional and routes broader/reference/representation work to PC-4. 

I would therefore record the scientific review as:

$$
\boxed{\textbf{PC-3 PASS}}
$$

with **no corrective rerun required** before proceeding to PC-4/scoped adjudication.

The notable scientific outcome is stronger than merely “PC tolerates the fission”: the source's persistent structural memory can cross the topology event **losslessly**, temporarily enter a signed carrier representation unavailable through ordinary pre-event PC history, and then evolve lawfully back toward \(Z=0\) under the ordinary target PC dynamics.
