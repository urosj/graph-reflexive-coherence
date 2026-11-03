# Native A_OS numerical policy

Policy `spark_aos_arb256_flux128_conductance192_v1` implements the bounded
[A_OS law](grc-9-v4-spark-completion-a-os.md) and its adopted
[earlier full-state domain](grc-9-v4-spark-completion-earlier.md).
The [native contract](../implementation/phase-9-grcv4/tranche-9/P9-9.1a.6-AOS-Contract.md)
selects steps 1–4. The source-to-completion campaign remains separate.

## State, identities and actual ordinary map

`grcv4-exact-conductance-state-v1` stores canonical rational resources C and
all positive edge conductances W_A. Exact FLINT incidence preserves charge 21
without resource repair. Old binary64 states and C-only profiles are not
silently converted. The quartic A candidate has an explicit resolved-v2 identity
and graph-bound exact weighted-row descriptor; the legacy descriptor's binary64
rounding is not used. Reference H and reference weights are unit, while physical
incoming conductance is a separate state channel.

At fixed Arb256 precision, both predictor and corrector use incoming C/W and
fresh weighted fixed rows. The predictor uses H=I; the generated geometry is
I+diag(f) O diag(f)/8. The corrector recomputes both potential and conductance
drive at this geometry, including its baseline-current term. Its physical
current drives continuity. All constants, split tolerance and smooth inactive
floor branch are those of the accepted law. Admission requires C in [0,4],
W strictly between 0.99 and 1.01, weighted selector separation, positive closure,
flat conditioning and split below the exact binary64 10^-11 declaration.
No precision fallback or tolerance widening is permitted.

Current enclosures must be within 2^-192 of their midpoints. Nearest/even
rounding to the 2^-128 edge-flux lattice supplies the one exact incidence update.
The writer recomputes its fixed rows at the **represented final C with incoming
W**, and consumes the same selected physical current. It evaluates

    log W_ideal = exp(-1) log W + (1-exp(-1)) log G(C_final,W,J_selected).

Its W enclosure must be within 2^-224 of the midpoint, which rounds nearest/even
to 2^-192. The whole C/W state is published atomically after a fresh full returned
OS read. Held-geometry/old-W and reference-H/new-W diagnostics are distinct.
Immutable graph, row, decay and verified-certificate facts may be cached;
changing-state reads and writers are always fresh.

## Full represented-map error, including the writer's final-C dependence

Let epsilon_J=2^-129+2^-192. For outward incidence B,

    epsilon_C[i] = 32 sum_j |B[i,j]| epsilon_J.

The writer uses represented final C rather than the ideal unrounded endpoint.
On C in [0,4], each weighted row has magnitude at most 4 and resource derivative
l1 norm at most 2. A difference of rows has magnitude at most 8 and derivative
norm at most 4. Therefore

    ||partial_C log G||_1 <= (2+3*2*8*4)/65536 = 194/65536.

With (1-exp(-1))<1 and all ideal/represented conductances at least 99/100,
the complete log-conductance error is bounded by

    epsilon_L = (194/65536) max_i epsilon_C[i]
                + (100/99)(2^-193+2^-224).

The first term accounts for resource rounding propagated through the writer;
the second converts the rounded conductance error through log. Both terms are
required. The selected current's enclosure already enters the writer interval;
no rounded flux is substituted for that current.

For the full 30-by-31 C/logW chart U, set e=(epsilon_C,epsilon_L,...,epsilon_L).
The uniform represented-map error is max_i sum_j |U[i,j]| e[j], strictly below
the recomputed image margin. Independent Arb768 checks compare each represented
sample directly against the ideal full map, including both cross-channel errors.
Source-to-entry accuracy is checked per transition; no accumulated orbit-shadow
bound or guaranteed matching entry beat follows from local invariance.

## Domain, predicates, event and lifecycle

The adopted exact S/U matrices span all fourteen charge directions and sixteen
log-conductance directions. The exact rational C/logW center defines a domain,
not an assumed fixed point. Native interval differentiation includes weighted
row ratios, both OS reads, generated geometry, final resources and the complete
writer. The center defect, transformed Jacobian norm and strict inclusion are
recomputed without research evaluator imports or saved verdicts.

Membership encloses log of the exact represented W at Arb256 and returns a
rigorous infinity-norm upper bound. If the interval straddles the boundary,
admission is inconclusive rather than guessed. Geometric classification uses
exact rational weighted row means, strict edge orders, seed/anchor predicates
and every descending route. Its arithmetic error is zero; whole-domain
predicates are checked independently of point classification.

The event archives both actual source roles, with fresh complete reads. Every
old edge retains its own incoming W by literal edge lineage; three new internal
edges are seeded at one. The exact resource allocation is 1/128,63/64,1/128,
with zero core and copied exterior. Current begins at W=4097/4096; independent
reset begins at W=8191/8192. Reset is not advanced to supply event history.

Positive-window, once-only, rollback and checkpoint obligations use the existing
public atomic owner. Synthetic near-domain tests exercise that lifecycle without
claiming a source-to-entry prefix. Expected current 375→377 and reset 372→374
remain unverified until .5. Aggregate native completion support remains false.
