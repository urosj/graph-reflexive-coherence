# SC-2 positive target: independent pressure and checker correction

2026-10-31. Summary of the supplied independent review of
[the positive target construction](../../../decisions/SparkCompletionSC2PositiveCandidate.md).
**Bounded mathematical PASS; one retained-consistency checker correction.**
The review does not select the quartic binding, assess the later source-beat
successor, close SC-2 or establish native completed-spark support.

## Independent results reported by the reviewer

The reviewer independently assembled the fifteen-node target incidence and
exact charge-21 metric: $a_{\max}=860128/102741$,
$\operatorname{tr}P-1=617291/52140$, rank 14. Their full OS derivative includes
predictor geometry, corrector potential, physical-current response and continuity,
including $dM$ in $dy=M^{-1}(dJ_0-dM\,y)$.

A separate 100-decimal mpmath interval calculation gives contraction below
0.997285200, center defect below $3.452\times10^{-48}$, strict image margin
above $2.5890\times10^{-9}$ and whole-box split below $8.571\times10^{-16}$.
These tighter outward computations support, and do not replace, the submitted
conservative bounds. Complete domains throughout both chiral boxes are exactly
$\{p,\mathrm{private}\}$ and $\{s_2,n_2,n_8\}$; all strict edge orders and
unqualified routing terminals are included.

Direct saved-entry metric bounds are below $4.228\times10^{-7}$ (current 900)
and $4.221\times10^{-7}$ (reset 867), within radius $2^{-20}$. Steps 900/867
are the first entries certified by the submitted conservative procedure,
not proved earliest mathematical entry times. A separate binary64 literal
physical-similarity recurrence reproduces 900/867 steps and all 3,534 chart
classifications; largest checkpoint-midpoint differences are
$4.663\times10^{-15}$ and $1.422\times10^{-14}$.

**That numerical reproduction is not a second rigorous enclosure of the long
recurrence.** The reviewer did not rerun the submitted 8192-bit Arb engine.
The separate pressure package was not supplied with this message; these are
attributed review results, not local executions of that package.

## Correction and verification boundary

The isolated fast-check block accepted rehashed final-checkpoint shifts
($n_1+1/64,n_2-1/64$), empty chart maps and a missing negative chart. Scalar
summaries and anchor-only comparisons did not bind the claims to saved states.
The charge-preserving altered checkpoint is far outside the trap.

The shared [retained checker](../../../research/spark_completion_retained.py)
requires both chart keys at every observation and recomputes complete basin
dictionaries at every saved checkpoint. It derives entry's metric distance
from coordinate intervals and fresh exact $P$, requires that distance to satisfy
the saved upper bound and trap radius, and compares both complete final domains
with the trap. It also checks the source successor's changed current and reused
reset. Earlier basin membership may change during approach.

[Regression pressure](../../../scripts/test_spark_completion_retained.py)
rehashes mutations before exercising both full checker paths: charge-preserving
shifts, empty/missing/extra charts, wrong membership with unchanged anchors,
missing entry coordinates, nonfinite intervals and understated scalar bounds.
Fresh trap/source calculations are shared within the test run.

`--check` verifies retained consistency and its stated fresh calculations; it
does not prove that checkpoints follow the recurrence. `--rerun` remains the
explicit enclosed-trajectory replay. No equations, allocations, thresholds,
trapping domain or numerical observations change in this correction.

## Source-stage scope

The review's remaining-source paragraph concerns its target-only subject.
The later [ordinary-source result](../../../decisions/SparkCompletionSC2SourceBeat.md)
already supplies the exact forward beat, fresh capture and enclosed continuation
of the actual changed current target, with reset reused by exact identity.
Source-chain review and scoped adjudication remain separate; this target review
is not silently extended to cover them. No SC-1 reopening or new target search
is required by this review.
