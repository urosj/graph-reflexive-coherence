# B1-GR GRV5 Retention, Read, Write, And Mediation

## Result

```text
mechanical_status = passed
branch_count = 48
activity_stage_write_count = 48
activity_complete_step_joint_write_count = 32
forming_old_current_amplitude = [141421.35623730952, 141421.35623730952]
bounded_persistence_count = 32
native_mediation_count = 0
substrate_reduced_sensitivity_count = 96
maximum_local_rung = GRR2
scientific_acceptance = awaiting_human_review
```

## Interpretation

GRV5 resolves the four causal arrows separately. An experiment-authored
old-current state changes conductance at the first exact native transport
reconstruction. The unchanged complete step reconstructs current and
conductance again and erases that conductance inscription, but the transient
write can leave a complete-step reached coherence/joint-state displacement.
GRV5 therefore tests that reached pair separately from the stage-local pair.
Direct authored conductance differences are overwritten by reconstruction.
The old-current forming input is synthetic and not claimed runtime-reached;
its large magnitude follows from the frozen `gamma = 1e-12` branch parameter
and the preregistered 0.01 conductance-attenuation exponent.

Frozen-conductance probes can expose carrier-conditioned transport response,
but that lane is substrate-reduced and its carrier states are synthetic or
stage-local off the current constitutive manifold. Native full-step and exact
immediate-stage lanes therefore remain authoritative for native mediation.
A baseline geometry-conditioned current difference is not counted as a read
effect; every candidate row uses the full carrier-by-probe 2x2 contrast.

The maximum bounded result is assigned from the complete-step reached pair,
its persistence horizons, and the independent slow-cluster/read gates. It
does not establish core Read-Back, orientation retention, or a closed
read/write loop.

## Causal Boundaries

- `P-W`: producer-authored conductance carrier; synthetic-valid only.
- `P-J`: exact native stage response to a synthetic old-current input.
- `P-J complete`: complete-step reached joint-state consequence of that input.
- `P-J-sign`: confirms the source-current-squared write is sign-even.
- Native complete-step persistence: evaluated after forming input stops.
- Frozen-`W` response: reduced diagnostic; cannot upgrade native evidence.
- External-current-like probe: analytical only; no native external-current input exists.
- Canonical interventions: `grv5_intervention_registry.json`.

## Provenance

- Input execution revision: `319b523fcc5be379f3b80afd38251e62b07e4764`
- GRV4 receipt: `1e236ed3ee7407125ba166157401712e76ca6337c09990ba0bfc6121c0b96c10`
- GRV4 acceptance commit: `53838f31c512fc8dd01bde8e99f34ceef7885f03`
- Runtime source/spec/test paths: unchanged under `protected_path_manifest_v5.json`
