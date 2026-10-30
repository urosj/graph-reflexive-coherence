# C_RG2b connected native continuation

The user selected continuation from P9-8.4d through bounded Tranche 9 on
2026-10-30. The [research plan](./P9-CRG2b-Tranches8-9-Plan.md) remains an
immutable input of the initial mathematical certificate. This successor records
its adoption and the native work; its pending-adoption wording is historical.

Authority is the conditional [connected completion contract](./P9-CRG2b-ConnectedCompletionContract.json),
propagated through a separate paper addendum and spec, pinned by the
[release](./P9-CRG2b-ConnectedCompletionRelease.json). Native policy:
`grc9v4_c_rg2b_connected_signed_argument_completion_v1`, with six inverse
levels, eighteen sweeps and a fixed 192-bit Arb residual certificate. Binary64
vertex solves only propose operands. Full residuals, coupled state/geometry
errors and the finite-section tail must pass before a section is admitted.
There is no numerical fallback, authoritative-resource clipping, relaxed tolerance
or tree17 rewrite. The signed auxiliary-argument retraction remains part of
the explicitly selected completion.

Large physical reads use `certified_arb_256` with FLINT. The small Tranche 9
integration harness explicitly selects FLINT with `legacy_exact_v1` physical
reads. Both use the same fixed 192-bit connected-section certificate. These
are recorded selections, not automatic solver fallbacks.

The graph-specific completion checks cover the full declared signed argument
and geometry charts. The finite native trajectories remain bounded named cases,
not an enclosure of every future trajectory or graph. The regularity claim is
Lipschitz, not C1 or spectral stability. LG-RG-COMPLETION is resolved only where
the explicit graph/parameter inequalities pass. C1 regularity remains narrowed
and unresolved. No ATC result supplies a nine-port proof.

Native execution currently establishes:

- [x] 8.4d: twenty deeper layouts, both histories, 400 target steps, forty final sections.
- [x] 8.4e/f: all 44 required small covariance history cells, 28 events and 112 steps.
- [x] 8.4g: four native large prepared steps, full section/current/Read-Back/continuity checks.
- [x] Six small lifecycle obligations and eighteen source/deep mechanism subjects.
- [x] All 22 applicable Tranche 9 native integration tests.
- [x] Actual large second-beat event and exact native replay (1726 seconds).
- [x] Three large combined/reflection/rotation events, native replays and six
  mapped target steps. The other five transforms remain explicitly deferred
  as for the eighth-realization bounded scope.
- [x] 8.4h: both baseline ten-step histories and fresh final sections.
- [x] Large native event replay and all four first/final mechanism subjects.
- [x] Final retained reconciliation: all sixteen applicable 8.4d–9.6 checkpoints.
  The phase boundary binds the exact finite maintenance/runtime roster.
- [x] Scoped user acceptance on 2026-10-30; aggregate ten-family closure remains open.

The independent checker retains every native inverse-chain operand and checks
it using the reviewed research equations. Physical reads are cross-checked
using unreduced edge equations, independently of the native vertex-reduced
section kernel. The resource sign bound includes native arithmetic error and
the infinite-section error contribution. Covariance checks compare complete
selected geometry, current, baseline, Read-Back, flat, structural source and
both authoritative histories. This is stronger than comparing only a current.

The 67 large records use [shared objects](./crg2b-native/shared/records.json).
They retain all 358,312,645 original JSON bytes and their original XZ transport
hashes through exact reconstruction. Git stores the shared archive and manifest (10,891,472 bytes, versus
28,298,336 bytes of separate XZ files);
expanded JSON and original XZ copies are ignored caches. Before standalone
readers on a fresh checkout, run:

```sh
.venv/bin/python scripts/evidence_storage.py restore --archives-only --prefix implementation/phase-9-grcv4/tranche-8/crg2b-native/
```

The side-tool restores those caches automatically. See the
[storage contract](../../../docs/reference/EvidenceStorage.md#shared-objects-for-new-crg2b-evidence)
for verification and encoder compatibility. Storage migration reruns no native
trajectory and does not change any scientific input, checker or result identity.

All commands run from the repository root, with `.venv`, `PYTHONPATH=src:.:implementation/phase-9-grcv4/verification`,
`OPENBLAS_NUM_THREADS=1`, and `OMP_NUM_THREADS=1`. Examples:

```sh
.venv/bin/python implementation/phase-9-grcv4/verification/p9_crg2b_campaign.py check
.venv/bin/python implementation/phase-9-grcv4/verification/p9_crg2b_large_successor.py event
.venv/bin/python implementation/phase-9-grcv4/verification/p9_crg2b_large_successor.py continue
.venv/bin/python implementation/phase-9-grcv4/verification/p9_crg2b_large_covariance.py events
.venv/bin/python implementation/phase-9-grcv4/verification/p9_crg2b_large_covariance.py steps
```

Successful segments are resumed by exact manifest identity; each large segment
has a 3600-second cap. Independent jobs run in parallel, at most twelve workers.
XZ evidence is read directly. Retained checks do not rerun native trajectories.

For a fresh numerical reproduction, use a separate checkout of these exact
sources. Restore prerequisite archives first, then move that checkout's entire
`crg2b-native/` directory aside. Keep the original evidence in its original
checkout. Generate fresh manifests and outputs in dependency order below;
calling a resumable command against existing outputs is not a numerical rerun.
Elapsed times and run digests will change, so a rerun does not replace or inherit
the original execution's acceptance. Do not run archive restoration over the
new outputs using the original storage manifest.

Each script below is in `implementation/phase-9-grcv4/verification/` and runs
with the environment above. Parallelism is internal to the numerical commands;
limit the combined worker population to twelve.

| Order | Script and arguments | Dependency/result |
| --- | --- | --- |
| 1 | `p9_crg2b_campaign.py prepare` | Fresh frozen small/deep inputs and native source beat. |
| 2 | `p9_crg2b_campaign.py deep --workers 12` | Twenty deeper events and both histories. |
| 3 | `p9_crg2b_covariance.py run --workers 6` | Small ordering and full-chart covariance. |
| 4 | `p9_crg2b_large.py prepare`, then `prepared` | Large inputs and four prerequisite native steps. |
| 5 | `p9_crg2b_large_successor.py prepare`, then `source` | Record first-beat exclusion and execute the second beat. |
| 6 | `p9_crg2b_large_preflight.py` | Independent screen; no native or sign-certificate credit. |
| 7 | `p9_crg2b_large_successor.py event`, then `continue` | Actual event/replay, twenty target steps and two final reads. |
| 8 | `p9_crg2b_large_covariance.py events`, then `steps` | Three mapped events and six mapped steps. |
| 9 | `p9_crg2b_lifecycle.py`; `p9_crg2b_science.py`; `p9_crg2b_large_science.py` | Lifecycle and mechanism checks on their declared subjects. |
| 10 | `p9_crg2b_integration.py run --workers 5` | Twenty-two native Tranche 9 tests. |
| 11 | `p9_crg2b_support.py`; `p9_crg2b_close.py` | Exact compatibility subjects and authority dispositions. |
| 12 | `p9_crg2b_native_review.py`; `p9_crg2b_final_review.py` | Retained coverage/integrity join, without another trajectory run. |

After the baseline first target steps exist, the mapped steps may overlap the
remaining two baseline histories (six plus two workers). The large mechanism
check requires both tenth steps. Mathematical research records outside this
directory retain their own reproduction commands and are not native-run credit.

Development correction: the inherited public test expects a D52/17-node
expansion. Its first fixture selection was D24/13-node; selecting the declared
D52 fixture fixed that mismatch. All 22 integration tests were rerun against
the corrected fixture. No production law was changed. A separate diagnostic
using cProfile together with a timed traceback crashed while inspecting schema
validation; it supplied no campaign credit or retained numerical result.

The first large source beat leaves all three candidate row gradients exactly
zero. It is correctly excluded by the strict Hessian-sign condition. The
second-beat successor keeps the original law, timestep, shares and thresholds;
it executes another ordinary beat before attempting the actual event. The
first-beat prepared records remain intact. A prepared target is not credited
as a committed event.

The four earlier public-family scope regressions pass with the ninth execution
family, without granting its acceptance or enabling A_RG2b. Eight focused API/browser/
notebook/source-integrity and historical-identity tests cover the checked view,
including rejection of resealed scope widening. The four disabled authority traces retain `indeterminate_requires_review`.

The second native source beat passed in 535 seconds and confirmed row
gradients `(0, 3.104408582051595e-10, -3.104408582051595e-10)`. The actual
event/replay then passed; both source split operands remain exactly 2. The
independent ten-step screen is positive for both roles but grants no native
trajectory or rounding-certification credit. Exact combined/reflection/rotation
allocation, event identities and charge maps also pass before numerical work.
Immutable event-input loading is memoized once per mapping worker; selected
sections and admission results are not memoized.

Both large histories pass all ten native target steps. Their pointwise
exact-real next-resource lower bounds start at 3.32608e-13 (current) and
1.05252e-13 (reset), and finish above 1.15098e-4. The largest associated
resource error is below 2.43e-16. Each bound includes physical arithmetic and
infinite-section error at that saved represented input; these bounds do not
compose into a uniform enclosure of an exact-real ten-step trajectory.
Native target segments took 547–636 seconds. The six mapped target steps
have a maximum complete-point covariance discrepancy of 6.62e-24.

All eighteen small/deep and four large first/final subjects distinguish
geometry, feedback and modulation at the declared fixed inputs, including
their section-uncertainty allowance. These controls do not claim separately
reconstructed counterfactual trajectories. Reset execution/rollback is tested
on the small native lifecycle subjects; the large lifecycle evidence is fresh
event replay. A large post-continuation reset is not claimed.

The [consolidated review](./crg2b-native/Review.json) is
historically `bounded_native_pass_pending_acceptance`. The separate
[acceptance](../tranche-9/P9-CRG2b-Acceptance.json) now closes the bounded scope,
including the lossless shared storage. Its projected compatibility matrix has
36 accepted cells and four unexecuted A_RG2b cells; original execution counts,
record bytes and source identities are unchanged. Check retained surfaces with
`PYTHONPATH=src:.:implementation/phase-9-grcv4/verification .venv/bin/python -m unittest test_p9_crg2b_review -v`;
the current-tree audit is `phase9_implementation_policy.current_boundary`.
Neither command produces a new native numerical campaign.
