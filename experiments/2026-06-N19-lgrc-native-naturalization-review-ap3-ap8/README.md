# N19 - LGRC Native Naturalization Review Of AP3-AP8

N19 is a bridge/review experiment. It takes the N13-N18
agency-prerequisite stack and asks which parts can be classified using the
same native-naturalization discipline introduced in N12.

The core question is:

```text
Can the N13-N18 AP3-AP8 agency-prerequisite artifacts be classified into
native contract candidates, Phase 8-ready candidates, implementation-gap
blockers, theory-sensitive blockers, and experiment-local scaffolds while
preserving claim boundaries?
```

N19 does not prove AP9. It does not implement Phase 8. It does not open native
support. It decides what a later native implementation task would actually
have to implement, validate, and keep blocked.

## Boundary

N13-N18 closed a staged artifact-level AP3-AP8 prerequisite stack:

```text
N13 = AP3 artifact-level support-seeking regulation candidate
N14 = AP4 artifact-level consequence-sensitive route selection candidate
N15 = AP5 artifact-level endogenous proxy formation candidate
N16 = AP6 artifact-level self/environment boundary candidate
N17 = AP7 artifact-level closed boundary engagement loop candidate
N18 = AP8_limited_artifact_candidate over a narrow h4/L5 envelope
```

All of these results remain artifact-level unless a separate Phase 8 task
implements native runtime state, telemetry, replay, controls, and validation.

N19 may identify:

```text
native contract candidates
Phase 8-ready native policy candidates
experiment-local scaffolds
implementation-gap blockers
theory-sensitive blockers
unsafe relabel controls
```

N19 must not claim:

```text
native support
Phase 8 implementation
fully native agentic-like integration
agency
semantic action or semantic perception
semantic goal ownership
selfhood
identity acceptance
organism/life behavior
unrestricted autonomy
```

Do not change `src/*` for N19. If implementation work is needed, N19 should
record it as future Phase 8 producer/runtime work, not perform it.

## N12 Method Reuse

N19 reuses the N12 naturalization ladder:

```text
NAT0 = producer-only artifact scaffold
NAT1 = source-backed producer pattern
NAT2 = replayable producer pattern with controls
NAT3 = native contract candidate
NAT4 = Phase 8-ready native policy candidate, no native implementation
NAT5 = native implementation exists but is not integrated
NAT6 = native implementation validates within composition replay
```

N19 aims only for classification up to `NAT4`. `NAT5` and `NAT6` require a
separate Phase 8 implementation branch.

`phase8_ready` must be derived from `nat_level = NAT4`. It is not an
independent flag and it is not native support.

## Primary Sources

N19 starts from these source records:

```text
experiments/2026-06-N12-lgrc-native-naturalization-and-producer-dissolution/reports/n12_closeout_and_handoff.md
experiments/2026-06-N12-lgrc-native-naturalization-and-producer-dissolution/outputs/n12_phase8_readiness_matrix.json
experiments/2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation/reports/n13_closeout_and_handoff.md
experiments/2026-06-N14-lgrc-consequence-sensitive-route-selection/reports/n14_closeout_and_handoff.md
experiments/2026-06-N15-lgrc-endogenous-proxy-formation/reports/n15_closeout_and_handoff.md
experiments/2026-06-N16-lgrc-self-environment-boundary/reports/n16_closeout_and_handoff.md
experiments/2026-06-N17-lgrc-closed-boundary-engagement-loop/reports/n17_closeout_and_handoff.md
experiments/2026-06-N18-lgrc-long-horizon-agentic-like-closure-stress-test/reports/n18_closeout_and_handoff.md
experiments/N12-N18-LGRC-AgencyPrerequisitesRoadmap.md
experiments/N12-N18-LGRC-AgencyPrerequisitesHandoff.md
```

Source artifacts must be consumed by relative path and digest. No absolute
local paths may appear in generated records.

## Hypotheses

Hypothesis A:

```text
The N13-N18 AP3-AP8 artifacts can be partitioned using the N12 NAT ladder
without promoting artifact evidence into native support.
```

Hypothesis B:

```text
Some N13-N18 components can be specified as native contract candidates or
Phase 8-ready native policy candidates, but only where runtime-visible inputs,
mutation ownership, telemetry, replay, budget, and controls are explicit.
```

Hypothesis C:

```text
Semantic agency, selfhood, identity acceptance, native support, organism/life,
and unrestricted autonomy remain blocked after classification.
```

## Expected Output Shape

Initial expected artifacts:

```text
outputs/n19_ap3_ap8_source_inventory.json
outputs/n19_naturalization_schema_v1.json
outputs/n19_lower_stack_candidate_classification.json
outputs/n19_ap6_boundary_native_readiness_classification.json
outputs/n19_ap7_loop_native_readiness_classification.json
outputs/n19_ap8_horizon_budget_native_readiness_classification.json
outputs/n19_candidate_classification_matrix.json
outputs/n19_phase8_readiness_matrix.json
outputs/n19_closeout_and_handoff.json
```

Initial expected reports:

```text
reports/n19_ap3_ap8_source_inventory.md
reports/n19_naturalization_schema_v1.md
reports/n19_lower_stack_candidate_classification.md
reports/n19_ap6_boundary_native_readiness_classification.md
reports/n19_ap7_loop_native_readiness_classification.md
reports/n19_ap8_horizon_budget_native_readiness_classification.md
reports/n19_candidate_classification_matrix.md
reports/n19_phase8_readiness_matrix.md
reports/n19_closeout_and_handoff.md
```

The strongest allowed closeout is:

```text
N19 = native naturalization review and Phase 8 readiness classification
phase8_opened = false
native_support_opened = false
final_claim_ceiling = artifact_level_phase8_readiness_review_for_ap3_ap8
```

## Closeout

N19 is closed as a native-readiness review, not a native implementation:

```text
status = passed
final_claim_ceiling = artifact_level_phase8_readiness_review_for_ap3_ap8
phase8_ready_surface_count = 12
full_ap3_ap8_nat4_ladder_generation_supported = false
current_implementation_can_generate_claimed_ap_ladder = false
claimed_ladder_generation_status = blocked_by_ap4_ap5_nat4_evidence_gaps
phase8_opened = false
native_support_opened = false
ap9_opened = false
```

AP-level NAT4 coverage:

```text
AP3 = NAT4 evidence present
AP4 = NAT4 evidence absent; best current level is NAT3
AP5 = NAT4 evidence absent; best current level is NAT3
AP6 = NAT4 evidence present
AP7 = NAT4 evidence present
AP8 = NAT4 evidence present for limited h4/L5 claim only
```

The important closeout result is that local NAT4 readiness surfaces do not make
the full AP3-AP8 ladder natively generatable. AP4/N14 lacks source-current
route-conditioned support/regulation evidence and native route-selection
telemetry; AP5/N15 depends on that AP4 gap and lacks native lower-stack input
capture plus a default-off native proxy derivation policy.

N19 therefore closes the current review stack with required handoff tasks:

```text
phase8_upgrade_ap4_to_nat4
phase8_upgrade_ap5_to_nat4
```

No new N20+ or Phase 8 implementation series is defined by N19.
