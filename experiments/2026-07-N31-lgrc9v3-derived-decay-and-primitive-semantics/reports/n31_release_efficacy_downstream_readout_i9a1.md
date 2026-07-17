# N31 Iteration 9-A.1 - Independent Downstream Readout

## Result

```text
status = passed
acceptance_state = accepted_provisional_producer_mediated_DR4_independent_native_receiver_readout_pending_I10
candidate = A release-efficacy attenuation
relation authority = producer-mediated
readout authority = native LGRC9V3 runtime
current rung = DR4
DR5_supported = false
native lane = D0a / DR2 unchanged
```

I9-A.1 does not add a second decay producer. It retains the exact Candidate A
producer from I9-A, waits until its release packet has arrived and the native
queue is empty, and then runs a separate receiver-side native packet-departure
operation. A second producer would be able to manufacture the downstream
difference and would therefore weaken, not strengthen, causal isolation.

## Native Threshold Readout

```text
q probes = [0.25, 0.3, 0.35, 0.4, 0.45]
fresh admissions = [True, True, True, True, False]
aged admissions = [True, True, False, False, False]
```

Both branches admit `0.25` and `0.30`. Fresh alone admits `0.35` and `0.40`;
both reject `0.45`. The split is a later native admission/departure operation,
not the immediate receiver credit already recorded by I9-A.

The native eligibility interval is `aged_C < q_probe <= fresh_C`; `0.35` is the
robust tested interior. The observed `0.30` and `0.40` endpoint behavior is
binary-floating-point runtime behavior, not a theoretical real-number boundary.
Exact `nextafter` endpoint probes remain pending for I10.

Balanced receiver-coherence clamps reverse the `0.35` split: clamping fresh
receiver C down to the aged value blocks departure, while clamping aged C up to
the fresh value admits it. Clamping the destination node to one common value
preserves the original split. Thus receiver C carries the later effect; target
state and a second producer do not.

This establishes `bounded_partial_local_receiver_C` mediation of native
departure admission only. The balanced clamp changes compensator node 0, so
complete continuation state is not matched and complete post-arrival branch
mediation is not claimed. Every rejected native request is atomically
state-neutral: restoration identities, queue, ledger, scheduler/time, packet
records, and budget remain unchanged after refusal.

The original-packet, immediate-credit, and no-second-producer checks are
conformance results and record `passed`. Auxiliary controls remain separate
from the inherited matrix, which stays at `18 / 57` resolved. The recorded
I9/I9-A revision lineage confirms that current corrected artifacts are consumed
without changing the numerical outcome.

## Classification

The combined I9-A/I9-A.1 evidence supports provisional producer-mediated
`DR4`: the registered release phase weakens expression, and the resulting
receiver state changes an independent later native LGRC operation. It remains
expression attenuation rather than field-state decay. `DR5` stays blocked
until I10 builds the formal recursive candidate row and resolves the complete
control matrix.

## Checks

| Check | Passed |
|---|---:|
| `exact_I9_and_I9A_sources_consumed` | true |
| `exact_I9A_final_snapshots_consumed` | true |
| `I9A_is_DR3_with_DR4_readout_pending` | true |
| `same_candidate_A_producer_retained_without_readout_producer` | true |
| `source_release_packets_complete_before_readout` | true |
| `five_point_native_threshold_sweep_matches_preregistration` | true |
| `independent_native_readout_splits_fresh_and_aged_at_q_0_35` | true |
| `receiver_C_clamp_reverses_readout_split` | true |
| `target_C_clamp_preserves_readout_split` | true |
| `balanced_interventions_preserve_total_coherence` | true |
| `successful_native_readouts_conserve_packet_budget` | true |
| `duplicate_readout_and_intervention_replay_exact` | true |
| `rejected_native_readouts_are_atomic_and_state_neutral` | true |
| `mediation_is_bounded_partial_local_receiver_C` | true |
| `floating_point_boundaries_are_observed_not_theoretical` | true |
| `I9_and_I9A_revision_lineage_closed` | true |
| `auxiliary_controls_do_not_inflate_inherited_matrix` | true |
| `new_and_auxiliary_controls_resolve_without_failed_open` | true |
| `composed_I9A_plus_readout_identity_recorded` | true |
| `formal_candidate_row_and_full_control_matrix_remain_pending_I10` | true |
| `artifact_manifest_exact` | true |
| `provisional_DR4_only_pending_I10` | true |
| `native_lane_not_upgraded` | true |
| `unsafe_claim_flags_false` | true |
| `src_diff_empty` | true |
| `protected_runtime_contract_diff_empty` | true |
| `no_absolute_paths_in_records` | true |
