# GRC9V3 Evidence Profile

## Purpose

This document records the bounded implementation and verification basis for
the causal-state, persistence, retention, and Read-Back boundaries in
[`grc-9-v3-spec.md`](grc-9-v3-spec.md). It is an evidence profile, not a second
normative specification and not an extension proposal.

The separation is deliberate:

```text
grc-9-v3-spec.md
  defines legacy GRC9V3 runtime semantics

grc-9-v3-evidence-profile.md
  records why selected semantic boundaries are justified and how far the
  available evidence reaches
```

Experimental counts, thresholds, and negative searches remain bounded facts.
They must not be promoted into universal substrate semantics.

## Frozen Reconciliation Basis

The reconciliation started from graph repository revision
`40a0b2cb55a62aed3bf29450c6cae8b56ae3880b`. The following source identities
are the frozen pre-reconciliation basis:

| Role | Path | SHA-256 |
| --- | --- | --- |
| GRC9V3 orchestration/runtime shell | `src/pygrc/models/grc_9_v3.py` | `d297def1eddfaf79a7ad3d6b676caaeebb29e6d7235f4fac5c6729bd7e26ca9e` |
| GRC9V3 differential/transport/identity operators | `src/pygrc/models/grc_9_v3_runtime.py` | `f6f12de4e9bf66cd97b4063854ea225ae00874fed7073d4e72775891db54f502` |
| GRC9V3 typed state surface | `src/pygrc/models/grc_9_v3_state.py` | `4ab5ffcb95d69a0767b24d6c95277ba3619a5d477c4865cc0d31735a2377918e` |
| GRC9V3 spark/expansion mechanics | `src/pygrc/models/grc_9_v3_sparks.py` | `fa1db78355e1dba41245da44c9c515ac09820035ca451723873da779420ee820` |
| GRC9V3 choice/collapse mechanics | `src/pygrc/models/grc_9_v3_choice.py` | `ab8be0391a37e71d4610022afe3f64dac6102b929ade4448a59e7f4e02167933` |
| Pre-reconciliation GRC9V3 specification | `specs/grc-9-v3-spec.md` | `c3b26e02ec894649cf43606bada9194b2f5dde8792491ae493aa2e59c7cb68f9` |

The implemented core contract is documented by:

| Role | Path | SHA-256 |
| --- | --- | --- |
| implementation scope and ownership | `implementation/Phase-7-ImplementationPlan.md` | `6d9d215757405e4be19f67cde844af3ac9297389ce730e8a44f9c7b6844067b3` |
| state/operator ownership map | `implementation/Phase-7-EquationMap.md` | `94461cdf43f9fb4bc7bb0996822ea4e6130f7256ac1a041594eea99656c3555c` |
| canonical 27-stage step order | `implementation/Phase-7-StepLoop.md` | `a5d52562e771317b9d669ef62cd337ac98bba8dfd21f7cd521e9ae7c04ad17fb` |
| implementation and correction lifecycle | `implementation/Phase-7-ImplementationChecklist.md` | `a01305300a785e08feb32b33846454dcbd5709ab655d5fd5332dd409adc8d30a` |
| truthful-hybrid and capability boundary review | `implementation/Phase-7-MidGate-Review.md` | `99e69b09c1538ff2c96a236460bf8e42faf238dcbd69dda7fbdbdd9dc33cf6b0` |
| representative spark/expansion/replay evidence | `implementation/Phase-7-RepresentativeRuntime.md` | `51aec1f3b3b512f47634b49f9608ee3a044a21d8c0996ad44dbe0103a915a9f0` |
| accepted core boundary | `implementation/Phase-7-Closeout.md` | `677f4b4689fed54c6c0842481e3d4d61142a23db0148b2c5b3fe11d99cc59d5c` |

Phase 7 remains authoritative for hybrid ownership, the canonical step order,
spark/expansion/stabilization semantics, basin-mass maintenance, quadrature
budget, column coarse-graining, serialization, capability boundaries, and the
representative deterministic runtime/replay lane. B1 and B2 narrow the
interpretation of complete-step causal coordinates and retention; they do not
replace those Phase 7 contracts or reinterpret hybrid topology evidence.

## Current Runtime Reading

The source and Phase 7 records agree on this baseline fixed-topology,
event-free stage order:

```text
incoming C/J
  -> differential reconstruction
  -> W reconstruction using C, gradients, and incoming J^2
  -> potential reconstruction
  -> fresh potential-flow J
  -> post-flux differential and identity reconstruction
  -> semantic/topology/boundary stages
  -> continuity and budget
  -> final differential/transport/identity reconstruction
```

This supports three type statements:

1. `C` is the admitted independent complete-step coordinate on the verified
   smooth strata.
2. `W` and `J` are load-bearing causal surfaces within a beat but are not
   established independent slow complete-step coordinates.
3. The incoming-current contribution to `W` is sign-even (`J^2`), while fresh
   `J` is reconstructed from scalar conductance and potential difference.

These statements are scoped to the verified smooth fixed-topology profile.
Topology, events, registries, RNG state, and reset-baseline lifecycle state are
not erased by this coordinate classification.

## Accepted B1-GR Evidence

B1-GR closed at `GRV-C6` without changing the runtime. Its accepted closeout
anchor is:

| Path | SHA-256 |
| --- | --- |
| `experiments/2026-08-B1-GR-grc9v3-continuation-readback-verification/outputs/gates/grv8_closeout_acceptance_anchor.json` | `239417d959f92bb3b32f2506b35fc279d8193722e46b8517001d3d29fa272da3` |

Load-bearing B1 records include:

| Evidence | Path | SHA-256 |
| --- | --- | --- |
| formed fixed-branch registry | `experiments/2026-08-B1-GR-grc9v3-continuation-readback-verification/outputs/fixed_branch_registry.json` | `56bd1857f892f187c6b99d6fcbd419ddd68ae0e17133b3a0bf7dda79b197e366` |
| complete-step Jacobian and causal-state audit | `experiments/2026-08-B1-GR-grc9v3-continuation-readback-verification/outputs/complete_step_jacobians.json` | `e4de4b9351ef7258baa88e7b675e8ce82f39ffe9db3ce9df395713e4f610c5ec` |
| preparation/persistence/mediation probe | `experiments/2026-08-B1-GR-grc9v3-continuation-readback-verification/outputs/conductance_retention_probe.json` | `bba1472177a2f182359ad9bc1ade634cd388f55088428fd030e6e32e74ed5766` |
| current recurrence and return-orbit audit | `experiments/2026-08-B1-GR-grc9v3-continuation-readback-verification/outputs/return_orbit_registry.json` | `f9af1524153d31ee2528f2d275b8274d5f65ca4a0c438ce3d15540e9d1c68e9e` |
| final causal-role classification | `experiments/2026-08-B1-GR-grc9v3-continuation-readback-verification/outputs/final_causal_role_classification.json` | `18a881f6d2a13f28dc59246c47ad07c208faa56cf03ebe6134bd868253f2c3e0` |
| final claim classification | `experiments/2026-08-B1-GR-grc9v3-continuation-readback-verification/outputs/final_claim_classification.json` | `f85d474daef7db7597f99d0d4afea2e242b4ca66b08a95b830496ae802f57d38` |

The accepted B1 boundary is:

- 48 formed physical branches were admitted for bounded analysis;
- causal closure passed on all 48 branches;
- no full `C/W/J` complete-step transition Jacobian was admitted;
- 32 branches admitted reduced temporal-coordinate evidence, while 16
  zero-current boundary branches remained blocked for that interpretation;
- synthetic valid incoming current reached the exact native sign-even
  `J^2 -> W` stage on all 48 preparation rows;
- 32 rows showed bounded later `C`-dominated neutral-coordinate persistence,
  with branch relocation unresolved;
- the maximum local retention rung was `GRR2`;
- native mediation specifically through transient `W`, native Read-Back,
  write-back, and a closed read/write loop were unsupported; and
- seeded cycle-current orientation was overwritten at the first native
  potential-flow transport reconstruction in the tested envelope.

The resulting claim is not “GRC9V3 implements retention.” It is:

> B1 established exact immediate-stage recurrence and bounded synthetic-input
> `GRR2` persistence, while leaving native carrier formation, branch-relative
> retention, specific mediation, and Read-Back unresolved or unsupported.

## Accepted B2-GR Evidence

B2-GR tested unchanged-runtime native carrier constructibility before any
extension selection. It closed at `B2-C6` with no new GRR rung.

| Evidence | Path | SHA-256 |
| --- | --- | --- |
| closeout acceptance anchor | `experiments/2026-08-B2-GR-grc9v3-retention-mediation-constructibility/outputs/gates/b2_closeout_acceptance_anchor.json` | `2a4b6b3220eae0fe0b3e3e4a698d47ab893841a3be15bafea0bf3755cac1143c` |
| full empty-path reconstruction audit | `experiments/2026-08-B2-GR-grc9v3-retention-mediation-constructibility/outputs/b2_i8_empty_path_audit.json` | `7caa0369b90f83d57495798fbbdff1d6051b45fe3588b13244c8b8101681dd74` |
| final classification and handoff | `experiments/2026-08-B2-GR-grc9v3-retention-mediation-constructibility/outputs/b2_i8_classification_and_handoff.json` | `138ee93667181f0a73012636ad90ee2919f0999d1c47a75d0e800079035af370` |

The bounded search classified 9,648 preparation attempts over 48 accepted B1
branches:

- no confirmed runtime-reached retained-carrier candidate was admitted;
- 1,705 of 1,706 apparent-carrier rows were attributable to authored
  preparation within numerical uncertainty;
- the remaining row had a runtime residual above uncertainty but below the
  carrier-separation and formation floors, reaching about `0.001027` of the
  formation floor;
- 27 resolved clean no-driver baseline controls were distinct baselines from
  one preparation family; they show that the baseline did not spontaneously
  produce a formation signal and are not failed active native-formation
  attempts;
- 7,915 rows were categorical, constraint-supported, or positive-interior
  failures outside the clean primary evidence lane;
- none of those 7,915 rows was eventful or topology-mutating;
- 26 of 48 branches admitted a nontrivial resolved clean-primary-lane attempt,
  while 22 remained inaccessible under the frozen preparation contract; and
- without a confirmed I4 lineage, `GRR3`, `GRR4`, and `GRR5` were not testable,
  not disproved.

The accepted B2 claim is therefore:

> No resolved native carrier-formation signal was found in the accessible
> resolved portion of the preregistered unchanged-GRC9V3 fixed-topology,
> event-free clean lane.

It is not a global nonexistence theorem. Unchanged-runtime constructibility
remains open beyond the resolved accessible strata, including branches and
preparation directions not made accessible by the frozen B2 preparation
contract.

## Normative Consequences

The combined evidence supports these legacy-profile boundaries:

| Boundary | Normative consequence |
| --- | --- |
| immediate stage recurrence is real | document `J^2 -> W -> potential -> J -> C` as native constitutive recurrence |
| `W/J` are reconstructed stage surfaces | do not advertise either as an independent slow complete-step coordinate |
| current-squared write is sign-even | do not claim historical current orientation retention |
| bounded `C` persistence is branch-compatible | do not equate ordinary `C` persistence with a separate retained historical sector |
| no retained-state contract exists | state that legacy GRC9V3 specifies no retained-state primitive, constitutive projector, or update law; analysis-only projectors remain non-constitutive |
| B2 found no clean native formation witness | record the bounded negative in this profile, not as universal runtime impossibility |
| B1/B2 selected no extension | require any later extension to be target-specific and revision-distinct |

## Claims Not Established

Neither B1 nor B2 establishes:

- that GRC9V3 can never form a retained carrier;
- that GRC9V3 has no retention under every topology, event lane, or preparation;
- that retention exists only through events or topology change;
- that a new `M` field is required;
- that `W` must be temporalized;
- that current must become independently relaxing;
- that one particular GRC9V4 mechanism is selected;
- native Read-Back, memory, learning, or agency; or
- automatic inheritance of any result by LGRC9V3.

## Verification Qualification

B2's full repository suite recorded 26 failed test node ids. The failure audit
identifies 12 locally absent, git-ignored GRC9/GRC9V3 phenomenology artifacts
consumed by discovery and pressure-evidence tests. It separately identifies a
GRCV3 representative-telemetry test with unequal primary/replay snapshot
digests. The exact node ids and absent paths are recorded in
`experiments/2026-08-B2-GR-grc9v3-retention-mediation-constructibility/outputs/gates/b2_i8_full_suite_failure_audit.json`.
B2 changed no `src/`, `specs/`, or existing `tests/` files relative to its
`main` baseline and established no B2 regression. The experiment owner accepted
a bounded environment exception for B2 closeout only. The exception does not
relabel the full suite as passing or resolve that repository debt.

This qualification remains part of the evidence profile. It does not alter the
normative semantics independently confirmed by source inspection and the
accepted B1/B2 records.

## Change Control

Changes to the legacy specification should update this profile when they alter
the interpretation of current source or accepted evidence. Runtime changes to
independent causal coordinates, retention, current relaxation, conductance
relaxation, or Read-Back require a revision-distinct specification and their
own evidence profile; they must not silently widen legacy `GRC9V3`.
