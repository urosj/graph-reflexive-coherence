# A_RG2b marginal-frontier certificate

The original D94 shares failed exact represented charge for the new source
history. Denominator-64 allocation screens found no positive ten-step companion
on the original below-one history or the uniform above-one history. A finer
predeclared 2^-20 neighborhood around the original shares supplies
139263/524288, 188417/524288, 3/8 (transported by branch role). It preserves
exact current/reset charge with old W=1025/1024 and unit new bonds. The native
source beat, transfer and both continuations are independently checked.

Its first remote frontier is positive but only about 7.34e-22 (current) and
4.06e-22 (reset). Subtracting a global resource error of order 1e-16 cannot
prove this sign. This is an enclosure limitation, not permission to clip the
state, loosen a tolerance or call a floating sign a proof.

Let x_i,h_i be the four saved inverse levels, x_0 the represented query and
h_4=I. Let X_i,H_i be the corresponding exact infinite-section inverse history.
The completion theorem guarantees existence and boundedness. With the same
joint C/Y increment and source slope bounds, their errors obey

$$
e^x_i\le e^x_{i-1}+A_Xe^x_i+A_He^h_i+r^x_i,
\qquad
e^h_{i-1}\le\tfrac12(B_Xe^x_i+B_He^h_i)+r^h_i.
$$

Here e^x_0 is the certified represented-log input error and e^h_4<=rho,
since the terminal exact section is in the proved H ball around I. Keep all
four resource/history residuals and all four geometry residuals. Solve the
resulting eight-variable nonnegative comparison system exactly with FLINT.
A positive vector w satisfying (I-M)w=1 proves spectral radius(M)<1; verify
both this witness and (I-M)e=r exactly. No terminal uncertainty is discarded.

Use these uniform errors to enclose X_1 and H_1, retaining exact star zeros,
then evaluate the full outward source expression

$$
H_0=I+\tfrac12 S(X_1,H_1)
$$

at fixed 192-bit Arb precision. Intersect that entrywise enclosure with the
independently proved ball around h_0. Evaluate the physical current and next
resources at the exact represented C/W and this H_0 enclosure. This keeps the
small causal products in remote rows, whereas a global norm subtraction loses
them. It certifies strict positivity for both first frontiers without changing
any native operation or numerical policy.

The [checker](../verification/p9_arg2b_positive.py) authenticates the complete
joint residual certificate before refinement. Tests check every comparison
inequality, nonzero terminal uncertainty, rejection of altered residuals, and
sign resolution on the actual marginal subject. The campaign explicitly uses
this certificate for D94; it does not claim a uniform trajectory enclosure.
