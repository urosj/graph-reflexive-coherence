# N07 Iteration 13 Identity-Support Withdrawal Baseline

Status: `passed`

## Why This Iteration Exists

N07 Iteration 12 closed the core identity/compatibility question with an
artifact-only, source-specific ID6 evidence classification for bounded
non-destructive exchange. That closeout intentionally did not test what
happens when the support area is weakened or withdrawn.

N09 then preserved the blocker
`n07_identity_withdrawal_baseline_not_available`. That was the right boundary:
N09 could regulate a proxy, but it could not decide whether a support
weakening disrupted the identity substrate or merely exposed an untested N07
condition.

Iteration 13 supplies that missing baseline for N10. It does not reopen broad
N07 identity theory and does not promote runtime identity acceptance. It gives
N10 a source-backed way to distinguish:

- support-intact bounded exchange;
- mild support weakening that still survives;
- N09-matched partial support withdrawal that disrupts support without
  restoration;
- explicit restoration that recovers support survival.

## Goal

The goal is to make identity/support consumption precise before N10 uses N09
goal-proxy regulation evidence. N10 can now ask whether a regulated proxy is
attached to a surviving support basin, a disrupted support basin, or a basin
that survived only because restoration support was explicitly supplied.

## Source Baseline

- support area id: `n07_support_area_A_v1`
- support area digest: `c0136786bd5288984d19152ff5a201ba91f5102a0f044879fb5be83f0367a3cb`
- source N07 ceiling: `ID6`
- source C3 class: `bounded_non_destructive_exchange`
- reference A support retention:
  `0.9731535762447039`
- support survival threshold:
  `0.85`

## Withdrawal Lanes

| Lane | Withdrawal | Restoration | Final A Support | Survives | Outcome |
|---|---:|---:|---:|---:|---|
| `support_intact_reference` | `0.0` | `0.0` | `0.9731535762447039` | `True` | `support_intact_bounded_exchange_reference` |
| `mild_support_weakening` | `0.1` | `0.0` | `0.8758382186202335` | `True` | `support_withdrawal_survival_baseline` |
| `n09_matched_partial_support_withdrawal` | `0.25` | `0.0` | `0.7298651821835279` | `False` | `support_disrupted_by_withdrawal_without_restoration` |
| `restored_after_n09_partial_withdrawal` | `0.25` | `0.8` | `0.9244958974324687` | `True` | `explicit_restoration_recovers_support_survival_baseline` |

## N09 / N10 Handoff

- prior N09 blocker: `n07_identity_withdrawal_baseline_not_available`
- prior blocker resolved for future consumption:
  `True`
- old N09 artifacts retroactively changed:
  `False`
- N10 can consume baseline:
  `True`
- N10 consumption rule:
  N10 may use this baseline to distinguish proxy regulation attached to surviving support from proxy regulation where identity support is disrupted or explicitly restored.

## Controls

| Control | Passed | Primary blocker if failed |
|---|---:|---|
| `n09_support_digest_match` | `True` | `identity_support_digest_mismatch` |
| `withdrawal_depth_serialized` | `True` | `withdrawal_depth_missing_or_mismatch` |
| `n09_partial_withdrawal_disrupts_support` | `True` | `support_disruption_not_detected` |
| `restoration_is_explicit` | `True` | `hidden_support_restoration_blocked` |
| `budget_exact` | `True` | `budget_discontinuity` |
| `n09_not_retroactively_promoted` | `True` | `retroactive_n09_claim_promotion_blocked` |
| `identity_claim_promotion` | `True` | `identity_claim_promotion` |

## Validation

| Check | Passed |
|---|---:|
| `baseline_available_for_n10` | `True` |
| `budget_exact` | `True` |
| `claim_flags_all_false` | `True` |
| `controls_all_passed` | `True` |
| `explicit_restoration_recovers_support` | `True` |
| `four_lanes_recorded` | `True` |
| `mild_withdrawal_survives` | `True` |
| `n09_partial_withdrawal_disrupts_support` | `True` |
| `n09_prior_blocker_present` | `True` |
| `n09_support_digest_matches_n07` | `True` |
| `old_n09_artifacts_not_retroactively_changed` | `True` |
| `source_11b_passed` | `True` |
| `source_12_id6_artifact_classification_preserved` | `True` |
| `source_12_passed` | `True` |
| `source_n09_i12_passed` | `True` |
| `source_n09_i8_passed` | `True` |

## Claim Boundary

Iteration 13 makes a withdrawal baseline available for N10 consumption. It
does not retroactively change N09 artifacts and does not support runtime
identity acceptance, RC identity collapse, semantic choice, agency, biological
identity, personhood, or unrestricted identity.

## Acceptance

Iteration 13 passes if N07 emits a source-backed identity/support withdrawal baseline for N10 consumption, tied to the N07 Iteration 12 support digest and the N09 withdrawal blocker. The baseline must include support-intact, weakened, N09-matched withdrawn, and explicitly restored lanes; classify survival/disruption without private runtime state; preserve exact budget accounting; avoid retroactively changing N09 closeout artifacts; and keep identity acceptance, RC identity collapse, semantic choice, agency, biological, personhood, and unrestricted identity claims blocked.

Achieved: `True`
