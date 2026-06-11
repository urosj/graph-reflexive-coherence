# N12-N18 LGRC Agency Prerequisites Handoff

This handoff is the pickup note for continuing after the N05-N11 foundation arc.
It is meant to let a future conversation restart without rediscovering the claim
boundary, source artifacts, or next branch options.

## Current Position

N05-N11 is closed as an artifact-level foundation for agentic-like LGRC
composition. The strongest current result is from N11:

- Final supported integration ceiling: `GALI7`.
- Final claim ceiling:
  `broader_general_artifact_only_agentic_like_integration_candidate`.
- Artifact-only validation: passed.
- Fully native implementation: false.
- Agency, semantic choice, identity acceptance, biological behavior,
  personhood, and unrestricted agency claims: still blocked.

The current roadmap continuation is:

- `experiments/N12-N18-LGRC-AgencyPrerequisitesRoadmap.md`

That roadmap treats N12-N18 as agency-prerequisite experiments, not agency
claims.

## Primary Source Artifacts

Start future review from these files:

- `experiments/N05-N11-LGRC-AgenticLikeFoundationRoadmap.md`
- `experiments/N12-N18-LGRC-AgencyPrerequisitesRoadmap.md`
- `experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_final_interpretation_and_roadmap_significance.md`
- `experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_12_final_closeout_and_handoff.json`
- `experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_12_final_closeout_and_handoff.md`
- `experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_11_hypothesis_c_native_generalization_gap.json`
- `experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_11_hypothesis_c_native_generalization_gap.md`
- `experiments/2026-05-N11-lgrc-general-agentic-like-integration/outputs/n11_iteration_10_gali7_closeout.json`
- `experiments/2026-05-N11-lgrc-general-agentic-like-integration/reports/n11_iteration_10_gali7_closeout.md`

Known recent output digests:

- N11 Iteration 10:
  `52c4e46ce245024ebcfbac4e6a5c9dd90ea7b7106ceb14f0be0136859edc1831`
- N11 Iteration 11:
  `82d1a3eedc0aebacdceae79e2be37bb96b7fff4cbfacbae00da912f3975c3e52`
- N11 Iteration 12:
  `86d90dbf1cb594ab541440c481fe1a501c0f13d16ccf46a044bd962bca134aa6`

## Native Gaps Carried Forward

N11 Hypothesis C identified these native blockers:

- `native_route_conductance_memory_policy_missing`
- `native_response_magnitude_policy_missing_for_unbounded_perturbations`
- `native_identity_acceptance_validator_missing`
- `native_agentic_like_integration_policy_missing`

The first two are the most concrete Phase 8 candidates. The identity and
integration validators are theory-sensitive and should follow only after their
entry gates are clearer.

## Recommended Next Start

The clean next experiment is N12:

`N12 - LGRC Native Naturalization And Producer Dissolution`

Recommended first actions:

1. Create the N12 experiment root, README, implementation plan, checklist,
   outputs/reports/scripts directories, and initial stubs.
2. Inventory which N05-N11 producer-layer mechanisms are candidates for native
   absorption.
3. Split candidates into:
   - ready for Phase 8 contract work,
   - experiment-local only,
   - theory-sensitive/deferred.
4. Start with the two concrete native candidates:
   - route conductance memory,
   - response magnitude policy.
5. Preserve the existing rule: producer-layer evidence may motivate native
   support, but it does not become a native claim until Phase 8 implements and
   validates it.

## Branch Options

There are three reasonable next branches:

- N12 first, no `src/*`: define naturalization inventory, contracts, and
  acceptance gates before opening Phase 8.
- Phase 8 route-conductance memory first: native absorption of the N08 memory
  trail / route affordance mechanism.
- Phase 8 response-magnitude policy first: native absorption of bounded
  regulation response sizing from N09/N10/N11.

The most conservative route is N12 first, then open targeted Phase 8 work from
N12 results.

## Claim Boundary

Do not relabel the current foundation as agency.

Current supported language:

- `agentic_like_integration_candidate`
- `artifact_only_agentic_like_integration_candidate`
- `agency_prerequisite_foundation`
- `native_absorption_candidate`

Current blocked language:

- agency
- intention
- semantic choice
- selfhood
- personhood
- biological behavior
- identity acceptance
- unrestricted agency
- fully native agentic integration

## Verification Notes

Before this handoff was added, the last checks run were:

- `git diff --check`
- `git diff -- src`

`src/*` was unchanged by the N12-N18 roadmap addition. The new work is
documentation/experiment artifact work only.

Future sessions should rerun:

```bash
git diff --check
git diff -- src
```

before closing any N12 setup or Phase 8 planning turn.

## Open Questions

- Should N12 define its own naturalization ladder, or use the AP0-AP8 ladder
  from the N12-N18 roadmap as the primary continuation axis?
- Should route conductance memory and response magnitude policy be naturalized
  together or split into separate Phase 8 continuations?
- Should identity acceptance remain deferred until after N12-N14, or should N12
  create only a negative/blocked contract for it?

The current recommended answer is: use AP0-AP8 for the roadmap, define a local
N12 native-absorption ladder if needed, split Phase 8 mechanisms if their
contract surfaces diverge, and keep identity acceptance blocked until the theory
entry gates are explicit.
