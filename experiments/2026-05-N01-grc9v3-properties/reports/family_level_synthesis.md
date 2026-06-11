# Family-Level Synthesis

Status: complete.

## Scope

This report synthesizes Experiments A-G under the Lane A
`current_hybrid_signed_hessian` baseline. It promotes only claims backed
by generated experiment artifacts and keeps source-intent-only or
unsupported observations out of the supported bucket.

## Conclusion

The O-style A-G pass partially weakens the anonymous-port null across controlled artifact classes while preserving Lane A and clean-fixture boundaries.

The result is not a global proof of GRC9V3 semantics. It is a controlled
O-style witness set that prepares the D-style falsification pass.

## Experiment Summary

| Experiment | Theme | Classification | Summary |
| --- | --- | --- | --- |
| A | row evidence | supported | Row-local stress produces expected row signatures in clean fixtures. |
| B | derived column evidence | supported_with_lane_a_boundary | Column-local cancellation/pressure proxy is observable and transforms correctly; direct column-H gating is blocked. |
| E | multiscale evidence | supported | G/Split reconstructs eligible nonnegative fields; signed flux is exact through J+/J-. |
| C | saturation evidence | supported | Degree-9 saturation plus signed-Hessian degeneracy gates mechanical expansion under Lane A. |
| D | refinement and child-basin evidence | supported_with_identity_boundary | Column-preserving mechanical refinement is supported; configured-window child-basin persistence is thresholded. |
| F | path-label evidence | supported | Metric, delay, and strongest flux/coupling paths disagree and remain edge-auditable. |
| G | motion-observer evidence | supported_with_observer_local_boundary | Observer-local row/column motion classification is supported in clean checkpoint-overlay fixtures. |

## Hypothesis Status

| Hypothesis | Classification | Scope | Boundary |
| --- | --- | --- | --- |
| H0 anonymous-port null | weakened | partially weakened across controlled artifact classes | Generic graph activity, landscape generality, and discriminator baselines remain for D-style tests. |
| O1 rows behave as local differential modes | supported | supported in clean row-stress fixtures | Isotropic terms can dominate magnitude; result is fixture-level, not landscape-general. |
| O2 columns behave as interface/refinement/multiscale families | supported | partially supported; strongest for derived column proxy, refinement, and G/Split | Direct column-H proxy-branch spark evidence is blocked under Lane A and available only in explicit Lane B/Lane C artifacts; dynamic routing and landscape-general column behavior are not established. |
| O3 ports carry row-column intersection behavior | supported | partially supported by observer-local mixed motion and port-level refinement/mapping | Non-additive row x column interaction is not quantified; stronger D6 tests are still needed. |
| O4 metric, delay, and strongest-flux paths can disagree | supported | supported in controlled three-corridor fixture | Edge-label result, not row/column semantic evidence by itself. |
| D1 factorization discriminator | supported | early O-style support only | Formal D1 should score semantic error across more artifacts and baselines. |
| D2 predictive separation discriminator | inconclusive | not run as a predictive scoring discriminator | Needs row-vs-column-vs-port feature scoring against held-out artifact targets. |
| D3 transpose discriminator | supported | partial support from transform controls | Formal D3 should report transpose-specific deltas across all applicable artifact classes. |
| D4 saturation discriminator | supported | supported under Lane A active-degree-9 signed-Hessian gate | Near-saturation degree-8 policy remains blocked under Lane A. |
| D5 interface-memory discriminator | supported | mechanical column-preserving lineage supported; longer interface memory not established | Post-refinement long-window interface memory and checkpoint-window identity persistence remain for later work. |
| D6 port-interaction discriminator | inconclusive | qualitative port-intersection witnesses exist, but no interaction model was fit | Needs row-only + column-only additive baseline versus row x column interaction terms. |
| D7 multiscale discriminator | supported | supported for eligible fields and signed flux J+/J- split | Semantic grouping superiority over row/random triples is deferred to formal D7. |
| D8 identity-emergence discriminator | inconclusive | configured-window child-basin persistence supported, stronger identity emergence not established | Identity fission from expansion alone is not claimed; checkpoint-window and landscape-general persistence remain inconclusive. |
| Motion observer | supported | observer-local support in clean checkpoint-overlay fixtures | Reusable motion-loader full port history, basin-assignment motion, and landscape-general motion remain inconclusive. |

## Prediction Check

| Prediction | Observed Result | Evidence |
| --- | --- | --- |
| H0 partially rejected, not uniformly | matched | A-G weaken H0 across controlled artifact classes while generic dynamics and landscape generality remain untested. |
| Rows show clean geometry/differential evidence | matched | Experiment A supports row-local signatures with transform controls. |
| Columns show strongest support in refinement/coarse-graining | matched | Experiments D and E support column-preserving refinement and exact G/Split reconstruction. |
| Direct and dynamic column claims may be caveated | matched | Experiment B direct column-H proxy-branch evidence remains blocked under Lane A; Lane C later shows it is available in explicit Lane B rows. |
| Port evidence likely partial and D6 needed | matched | Experiment G supports mixed motion classification, while D6 interaction scoring remains inconclusive. |
| O4 path disagreement depends on exposed labels | supported_more_cleanly_than_risk | Experiment F exposes fixed edge-label surfaces and demonstrates path disagreement with equalized controls. |
| Identity fission is uncertain | matched | Experiment D supports configured-window child-basin persistence only; stronger D8 identity emergence remains inconclusive. |

## Lane C Comparison

Lane C was run as an analysis pass over selected clean fixtures. It is not a
runtime lane and does not change Lane A or Lane B.

Classification:
    `lane_c_comparison_complete_direct_column_h_branch_delta_observed_with_boundaries`

Result:

- comparison rows: `60`
- Lane A candidates/refinements: `25 / 25`
- Lane B candidates/refinements: `40 / 40`
- direct Lane B column-H proxy-branch rows: `15`
- candidate/refinement delta rows: `15 / 15`
- degree-8 near-saturation remains blocked

## Follow-Up Surfaces

| Surface Or Suite | Status | Reason | Guardrail |
| --- | --- | --- | --- |
| grc9v3_column_h_assisted Lane B / Lane C | completed post-pass comparison | Direct column-H proxy-branch spark evidence is blocked under Lane A but observed in explicit Lane B rows. | Do not reinterpret Experiment B Lane A rows as direct gate evidence. |
| near-saturation degree-8 policy | future implementation candidate | Lane A has no active-degree-8 near-saturation policy. | Degree-9 saturation support. |
| inflow-weighted transfer lane | future implementation candidate | GRC9V3 exposes equal/custom expansion weights, not a true inflow-weighted transfer lane. | Custom column-skewed runtime weights. |
| checkpoint-window identity persistence | small addendum or D8 prep | Experiment D uses experiment-local runtime-state windows. | Expansion event alone. |
| reusable motion-loader full port histories | future implementation candidate | Experiment G uses checkpoint-overlay analysis because current motion loader does not normalize full port histories. | Observer-local clean fixture support. |
| landscape/seed robustness suite | future experiment suite | A-G are clean controlled fixtures, not landscape-general studies. | Any single clean fixture witness. |
| D-style discriminator pass D1-D8 | next experiment layer | O-style pass provides witnesses but not all falsification baselines. | O-style fixture support alone. |

## Guardrails

- Direct column-H proxy-branch spark evidence remains blocked under Lane A and
  available only in explicit `grc9v3_column_h_assisted` Lane B/Lane C artifacts.
- Near-saturation degree-8 policy remains blocked under Lane A.
- Mechanical refinement is not identity fission.
- Configured-window child-basin persistence is not landscape-general identity.
- Exact G/Split reconstruction is not semantic column superiority over arbitrary groupings.
- Edge-label path disagreement is not direct row/column semantic evidence.
- Observer-local motion classification is not reusable motion-loader port-history support.

## Next Layer

Proceed to the D-style discriminator pass. D1-D8 should convert these
fixture witnesses into falsification tests against arbitrary S9 relabels,
degree/adjacency baselines, row-only and column-only predictors,
random triples, additive row+column explanations, and stricter identity
persistence windows.
