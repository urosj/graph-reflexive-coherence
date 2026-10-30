# A_RG2b connected nine-port completion

This research successor preserves the accepted signed argument-retraction law
and its C/scaled-log-history state. It extends the graph hypotheses and prepares
an explicit numerical policy; it does not itself enable native execution.

The [accepted completion proof](./P9-8.0-RG2bCompletion.md) supplies the global
inverse and graph-transform argument. Its Candidate-A estimates depend on the
incidence, Gram and overlap-mask row sums, positive W, and normalized fixed-port
row averages. They do not use a tree spectral gap, graph size, or a C selector.
For any simple loop-free connected nine-port graph, outward incidence B gives

$$
\|B\|_\infty\le9,\qquad
\|B^TB\|_\infty=\max_{e=(u,v)}(\deg u+\deg v)\le18,\qquad
\||B|^T|B|/2\|_\infty\le9.
$$

Every vertex has three named port rows. Each nonempty row is a positive
W-weighted average. On the unchanged argument chart C in [-1,5] and
Y = 512 log W in [-1,1], its value is bounded by 6 and its joint-state
Lipschitz constant by 2 + 12/512, independently of the number of neighbors.
Empty rows are exactly zero. No row-denominator lower bound depending on graph
size is introduced, and opposing edge orientations do not alter these bounds.

The checker substitutes 9/18/9 for the earlier 9/10/5 graph constants in the
accepted A equations. It preserves the timestep 2^-12, H radius 2^-12,
section Lipschitz limit 2^-10, all scientific coefficients, the W floor, the
fresh-resource writer stage, and the separate C and Y nesting margins.
The auxiliary increment evaluates at the argument retraction; physical state
is never clipped and the outer state is never replaced by its retraction.

Let A_X,A_H bound the joint increment f, and M_S,B_X,B_H bound its structural
source S. For kappa_H = 1/2 and L = 2^-10, the required inequalities remain

$$
\ell=A_X+A_HL<1,\quad M_C<1/4,\quad M_Y<1/8,
$$

$$
V=M_S/2<\rho,\qquad
L'=\frac{B_X+B_HL}{2(1-\ell)}\le L,\qquad
q=\frac12\left(B_H+\frac{(B_X+B_HL)A_H}{1-\ell}\right)<1.
$$

The unchanged four-level terminal-I tail is q^4 V. Its bound is only one
component of the 2^-48 section budget: actual residuals, represented logarithm
input error and physical output error must still be certified. A passing
completion theorem supplies no automatic event, positivity, ordinary-step or
mechanism-separation credit.

Exact FLINT rational bounds and all declared graph hypotheses are computed by
[p9_arg2b_completion.py](../verification/p9_arg2b_completion.py). The uniform
class certificate is stored once; each graph retains its actual norms and
certificate identity. The original 9/10/5 bounds are independently reproduced
as a regression against the accepted research proof.

```sh
PYTHONPATH=src:.:implementation/phase-9-grcv4/verification OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -m unittest test_p9_arg2b_completion
PYTHONPATH=src:.:implementation/phase-9-grcv4/verification OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python implementation/phase-9-grcv4/verification/p9_arg2b_completion.py --run --workers 12
```

This establishes a completion-relative Lipschitz result only. It neither
resolves `GTRS-RG-DEBT-C1-SECTION-REGULARITY` nor grants differentiability,
classical spectrum, arbitrary parameters, physical positivity or a uniform
trajectory tube. No ATC certificate is used.
