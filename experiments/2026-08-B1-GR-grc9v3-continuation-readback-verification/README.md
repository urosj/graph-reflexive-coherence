# B1-GR - GRC9V3 Continuation And Read-Back Verification

B1-GR is a foundational theory-to-substrate verification experiment over the
unchanged `GRC9V3` runtime. It is inside the repository experiment discipline,
but outside the N-series agency/catalog sequence.

The experiment is grounded in the two controlling core papers:

- *The Continuation Spectrum*;
- *Read-Back*.

Its job is not to implement those papers. Its job is to determine what the
current synchronous graph substrate realizes exactly, in a declared reduction,
only analogically, as a measurable diagnostic, or not at all.

## Experiment State

```text
experiment_id = B1-GR
status = grv1_accepted_grv2_P2_prepared
specification_state = draft_3_4_1_pre_execution_mathematical_execution_sealed
controlling_specification_sha256 = 7ad99fb4acc6a7691d184a514f4836ffa3927600fc7cf504eb059134f3948e44
runtime_under_test = unchanged_GRC9V3
runtime_change_authorized = false
src_change_authorized = false
existing_test_change_authorized = false
positive_continuation_evidence_opened = false
positive_retention_evidence_opened = false
positive_readback_evidence_opened = false
positive_writeback_evidence_opened = false
verification_closeout_rung = GRV-C2
verification_closeout_ceiling = GRV-C2
B1_L_execution_authorized = false
N32_selected = false
l04_selected = false
```

The digest above is the SHA-256 of the controlling specification committed in
the documentation scaffold. GRV0 must reproduce it from the clean `P0` input
revision; changing the specification requires protocol readmission.

The first unaccepted GRV0 result revision (`05fc8f6`) exposed one packaging
omission: `baseline_manifest.json` carried the correct specification digest but
not the separately required `specification_id`. The correction is classified
as `bug_fix_preserving_protocol`; it changes no fixture, threshold, method,
runtime, theory contract, or claim envelope. The original result remains in
history and is superseded by replacement result revision `97a9a6b`, generated
from clean P0.2 input revision `5f92973`.

The first replacement attempt from `431dcf8` then failed closed before receipt
emission because the orchestrator included the existing unaccepted receipt in
the replacement receipt's output-artifact set. P0.2 excludes the exact receipt
target from its own digest enumeration and adds a rerun regression test. This
is also packaging-only: no partial P0.1 result was admitted. The complete P0.2
rerun passed mechanically with receipt digest `a583d763b2d5e72af3f3e2ad5401aca8c143eff1aa73427404c2f8286e1ed9df`.
GRV0 scientific acceptance is recorded separately in anchor commit `454b2c5`.
Iteration 1 is closed at GRV-C1; this does not open scientific continuation,
retention, read-back, or write-back evidence.

GRV1 then executed from clean committed P1 revision `cbe52fe`. Its mechanical
source-fidelity checks pass, and result receipt
`c8f51f4cc1f816726aa65d56e9165809ba54a5d47f4259e4e3f3318712f5b1bf`
binds the generated artifacts to that input revision and the accepted GRV0
anchor. GRV1 remains at a `GRV-C2` candidate ceiling until a separate
authorized human acceptance anchor is recorded. It opens no branch,
continuation, retention, read-back, or write-back evidence.

Before acceptance, source-fidelity review identified additional controls needed
to make later stage-local interpretation safer. The unaccepted GRV1 candidate
at `45435c8` is therefore superseded, not rejected, by a P1.1 instrumentation
strengthening. P1.1 preserves the sealed specification and claim ceiling while
adding observation noninterference, clone isolation, W/J/K authority mapping,
valid multi-amplitude K interventions, stagewise sign attribution, public-stage
and fresh-process replay, and explicit transition-environment/RNG accounting.
The strengthened rerun from clean input revision `416f49e` passes mechanically.
Receipt `9535c80100c6813b69a327cfa80f0180f2288ee7e87e6e550c3168261353855a`
binds the new authority map and instrumentation artifacts and explicitly
supersedes the earlier unaccepted receipt. That receipt remained a `GRV-C2`
candidate until the separate acceptance below.

The strengthened GRV1 result is accepted by the experiment owner in separate
anchor commit `bc12787`. Iteration 2 is therefore closed at `GRV-C2`, still
without branch, continuation, retention, read-back, or write-back evidence.
GRV2 is prepared as the first gate eligible to produce a source-current formed-
branch candidate; its output remains provisional until separately accepted.

The first GRV2 execution from P2 commit `5bf082d` failed closed before receipt
emission. A triangle snapshot reload re-canonicalized one closing-edge current
whose theoretical branch value is zero; the observed load delta was about
`3.22e-11`, below the already frozen `J` tolerance of `1e-10`, but the P2
replay check had incorrectly required exact numeric equality. P2.1 applies the
accepted per-block tolerances while continuing to report raw representation
normalization separately. No partial snapshot is evidence, and the complete
gate must be rerun from clean committed input.

The P2.1 rerun from `050639a` passed the first triangle rows but failed closed on
a more asymmetric row. That exposed the underlying experiment-builder defect:
the undirected closing edge retained topology endpoint order `2 -> 0` while the
runtime current coordinate had already been canonicalized to `0 -> 2`. P2.2
canonicalizes the topology endpoint and `PortEdge` orientation together, as
required by the frozen orientation convention. The graph, parameter grid,
thresholds, runtime, and claim ceiling are unchanged; all partial outputs remain
unadmitted and a complete clean rerun is required.

## Central Question

```text
What do the current GRC9V3 equations and complete synchronous runtime actually
realize from continuation, temporal persistence, retention, read-back, and
write-back; which correspondences are reduced, analogical, diagnostic, absent,
or theory-open; and what next route is justified by unchanged-runtime evidence?
```

## Required Distinctions

B1-GR must keep these objects separate throughout execution:

```text
continuation stiffness alpha
temporal relaxation gamma
read-back gain beta

retention
read effect
write effect
closed read/write loop

spatial Hessian
frozen-conductance comparator
complete transition Jacobian

temporal marginality
continuation marginality
spark / basin birth
collapse
```

Branch existence, a slow observable, persistent conductance, nonzero current,
or a useful diagnostic cannot by itself establish Read-Back.

## Serial Gate Order

```text
GRV0 baseline admission
  -> GRV1 instrumentation and source fidelity
  -> GRV2 strong formed branches
  -> GRV3 causal state and complete transition Jacobian
  -> GRV4 frozen-conductance versus full recurrence
  -> GRV5 conductance preparation, persistence, and mediation
  -> GRV6 current recurrence and return orbits
  -> GRV7 spatial versus temporal/continuation thresholds
  -> GRV8 claim classification and route decision
```

The gates are serial. A blocked prerequisite limits or stops dependent work;
later iterations cannot repair an earlier missing source identity by relabeling
or interpretation.

## Claim Boundary

B1-GR may establish bounded causal arrows and implementation correspondence
levels for unchanged `GRC9V3`. It may end with a positive, negative, blocked,
mixed, or theory-reopening result.

It does not initially authorize:

```text
new GRC runtime behavior
new read-back state or current
LGRC execution
N32 selection
unique retained projector
unified alpha/gamma/beta spectrum
memory, learning, agency, organism, or life claims
```

Only GRV8 may recommend a revision-distinct selectable GRC extension, an
analysis-only route, theory reopening, no extension, or the deferred B1-L
investigation.

## B1-L Relationship

[B1-L](../2026-08-B1-L-lgrc9v3-continuation-readback-delta/README.md) is a
deferred downstream experiment identity only. It originates in Part III of the
B1-GR specification and cannot begin before accepted `GRV-C6` evidence and an
accepted `lgrc_handoff.json`.

## Documents

- [Controlling verification specification](implementation/GRC9V3ContinuationReadBackVerificationSpecification.md)
- [Preserved Draft 3.2 intake](implementation/GRC9V3ContinuationReadBackVerificationSpecification_Draft3_2.md)
- [Preserved Draft 3.3 implementation-hardening revision](implementation/GRC9V3ContinuationReadBackVerificationSpecification_Draft3_3.md)
- [Preserved Draft 3.4 identification/lifecycle revision](implementation/GRC9V3ContinuationReadBackVerificationSpecification_Draft3_4.md)
- [Implementation plan](implementation/GRC9V3ContinuationReadBackVerificationImplementationPlan.md)
- [Implementation checklist](implementation/GRC9V3ContinuationReadBackVerificationImplementationChecklist.md)
