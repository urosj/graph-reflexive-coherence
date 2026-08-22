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
GRR2_branch_relocation_rival_unresolved = 32
specific_transient_W_mediation_supported = False
native_branch_only_reachability_supported = False
review_points_accounted_for = 36/36
P5_3_changed_primary_rung = False
P5_4_changed_primary_rung = False
scientific_acceptance = awaiting_human_review
```

## Interpretation

GRV5 resolves the four causal arrows separately. A synthetic experiment-
authored old-current state changes conductance at the first exact native
transport reconstruction. One unchanged complete step then reconstructs
current and conductance, erases that conductance inscription, and produces
a later coherence-dominated consequence. GRV5 does not isolate transient
`W` from every other state produced by the synthetic old-current preparation,
so it does not establish that transient `W` specifically mediates later `C`.
It tests the unchanged-runtime successor separately from the stage-local pair.
Direct authored conductance differences are overwritten by reconstruction.
The old-current forming input is synthetic and not native-runtime reachable.
The resulting complete-step state is an unchanged-runtime successor of that
synthetic intervention; it is not shown reachable from an accepted branch by
unchanged runtime evolution alone and is never shortened to `runtime-reached`.
Its large magnitude follows from the frozen `gamma = 1e-12` branch parameter
and the preregistered 0.01 amplitude-squared attenuation coordinate.
On multi-edge fixtures the realized per-edge log-conductance change is
that coordinate multiplied by the squared canonical edge direction; it
is not a uniform 0.01 attenuation on every edge.

Frozen-conductance probes can expose carrier-conditioned transport response,
but that lane is substrate-reduced and its carrier states are synthetic or
stage-local off the current constitutive manifold. Native full-step and exact
immediate-stage lanes therefore remain authoritative for native mediation.
A baseline geometry-conditioned current difference is not counted as a read
effect; every candidate row uses the full carrier-by-probe 2x2 contrast.

The maximum bounded result is assigned from the unchanged-runtime successor pair,
its persistence horizons, and the independent slow-cluster/read gates. It
does not establish core Read-Back, orientation retention, or a closed
read/write loop.
The persistent F2/F3 displacement is neutral/marginal within the declared
finite-horizon ratio tolerance and C-dominated after W overwrite. Every
`GRR2` displacement lies in the admitted zero-sum `C` coordinate to numerical
precision and changes negligibly through horizon 10. GRV3 did not separately
identify a branch tangent, so relocation along a neutral branch family remains
an unresolved rival. The result is bounded C-dominated neutral-direction
persistence, not transverse branch-relative retention or stable W retention.
P5.3 and the P5.4 acceptance clarification cannot upgrade the GRR2 rung.

## Causal Boundaries

- `P-W`: producer-authored conductance carrier; synthetic-valid only.
- `P-J`: exact native stage response to a synthetic old-current input.
- `P-J complete`: unchanged-runtime successor of a synthetic old-current intervention; native branch-only reachability is not demonstrated.
- Transient `W` mediation: not established; no stage-matched W-only mediation control was run.
- GRR2 branch relation: neutral-coordinate persistence with branch relocation unresolved.
- `P-J-sign`: confirms the source-current-squared write is sign-even.
- Native complete-step persistence: evaluated after forming input stops.
- Frozen-`W` response: reduced diagnostic; cannot upgrade native evidence.
- External-current-like probe: analytical only; no native external-current input exists.
- Canonical interventions: `grv5_intervention_registry.json`.
- Acceptance hardening: all 36 review points are mapped in
  `grv5_36_point_review_audit.json`.

## Provenance

- Input execution revision: `83c2cbcf002bf5ab82198f6ed9827950ada1af6a`
- GRV4 receipt: `1e236ed3ee7407125ba166157401712e76ca6337c09990ba0bfc6121c0b96c10`
- GRV4 acceptance commit: `53838f31c512fc8dd01bde8e99f34ceef7885f03`
- Runtime source/spec/test paths: unchanged under `protected_path_manifest_v5.json`
