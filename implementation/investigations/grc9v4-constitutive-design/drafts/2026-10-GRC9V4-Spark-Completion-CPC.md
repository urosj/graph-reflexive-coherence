# Geometric spark completion with a persistent carrier

2026-10-31. From the [C_PC proposal](./GRC9V4-spark-completion-CPC-proposal.md)
under [SC-3 authority](../decisions/SparkCompletionCPCSC3Authority.md).

## Full physical dynamics and lawful domain

For the homogeneous quartic V(C)=((C-2)^2-1)^2/4, outward incidence B,
edge Laplacian L=B^TB and endpoint overlap O, define

$$
H=I+Z/2,\quad j_0=-\tfrac1{1024}B^T(\tfrac1{64}BHB^TC-V'(C)),
\quad y=(\tfrac34I+HL)^{-1}j_0,
$$
$$
J=j_0+y/4,\quad f=H^{-1}y/2,\quad S_{ij}=O_{ij}f_if_j/4,
$$
$$
C^+=C-32BJ,\qquad Z^+=e^{-1}Z+(1-e^{-1})S.
$$

Independent state is (C,Z); geometry and current are reconstructed. The
carrier time is tau_PC=32. The remaining parameters are tau_C=1,
chi_C=zeta_C=kappa_H=1/2, kappa_M_C=0, unit weights/measures/reference Hodges
and zero context. The current consumes old Z and the writer consumes that
same read's source, rather than a source recomputed after continuity.

`SC-CPC-EC-DOMAIN` holds for C in [0,4]^V and signed symmetric star-supported
||Z||_F<=1/64 on the actual source and target graphs. The H spectrum is
contained in [127/128,129/128]. Similarity to a positive symmetric matrix
bounds the current inverse, and the connected-graph selector gap remains
above 1/64. The uniform source norm is below 1/64, proving conditional carrier
ball invariance. The resource box is checked along the trajectory rather
than asserted globally invariant.

## Weighted full-state stability

Let A0=B[I+(3I/4+L)^-1/4]B^T and P=(A0+11^T/15)^-1. On the exact charge-21
slice, use the retained rational center c and

$$
K=\{(C,Z):\max(\|C-c\|_P,1024\|Z\|_F)\le2^{-20}\}.
$$

There are 14 resource and 46 symmetric star carrier directions. Offdiagonal
carrier basis elements are normalized by 1/sqrt(2), so the derivative norm
is the Frobenius norm of the actual bilinear history. Differentiate both H
consumers, the physical current, continuity and the same-source writer. The
block bounds b_CC,b_CZ,b_ZC,b_ZZ give

$$
q=\max(b_{CC}+b_{CZ}/1024,\ b_{ZZ}+1024b_{ZC})<0.997358.
$$

The center defect leaves strict image margin >2.51e-9. A separate reference
resource-map certificate yields C*; zero reference current then implies
f*=S*=Z*=0. The full contraction proves local uniqueness and return under
nonzero signed carrier perturbations. Complete domains {p,private} and
{satellite2,n2,n8} hold throughout both charts. This proves
`SC-CPC-EC-FULL-STATE-RETURN`, without asserting global formation or using
a resource-only stability argument.

## Actual source-to-completion witness

One current PC beat starts from exact source resources and Z=+2^-16 I,
writes the carrier and yields a fresh whole event read and qualified parent.
The reset comparison has Z=-2^-17 I and is not advanced before transfer.
Literal D11 uses actual resources, shares (1/64,31/32,1/64), zero core and
unchanged exterior. Exact incidence and shares prove charge conservation.
The lawful P-to-P event archives both source histories, records carrier loss,
and initializes every target carrier entry to zero. Subsequent ordinary beats
regenerate and consume nonzero history; event zeroing is not native release.

The two new, fixed-8192-bit outward histories reach K at 849 and 817. Two
positive duration-32 beats end at 851 and 819. Current yields one stable new
child with local gain one; reset earns no live gain. The trap proves subsequent
exact persistence. This is `SC-CPC-EC-COMPLETION` for the declared subject.
These are sufficient witness times, not earliest completion or native counters.

The repository checks retain 1,670 full C/Z states and 3,340 chart
classifications, exercise all derivative directions at stationary and
nonstationary inputs, and reject sixteen false-completion/subject substitutions.
Saved/fresh recurrence and read overlap checks consistency only. Fresh certified
enclosures drive the proof; the original outward campaigns supply trajectory
provenance. No independent second reviewer or independent long replay is claimed.

## Scientific scope and native obligations

The user accepts three bounded conditional claims and resolves C_PC scientific
applicability. C_OS/C_CI remain accepted independently. Seven remaining families
are open, with C_CI_PC next. The v2 completion schemas and SC-1 criterion are
reused. Whole represented C/Z-map error, exact represented charge, certified
diagnostics, actual carrier disposition, committed windows, occurrence identity,
at-most-once gain and atomic lifecycle/hierarchy publication remain P9-9.1a
obligations. No native completion or aggregate G4 conclusion follows.
