# C_RG2b — bounded P9-10.1a–c and P9-10.2

Implemented and validated on 2026-10-31; user acceptance is pending.
Branch `work/p9-tranche10-remaining-families`, after A_CI_PC acceptance
`a8be36c7`. A_RG2b and consolidated P9-10.3–10.6 remain separate.

## Contract and implementation

The [basin specification](../../../specs/grc-9-v4-basin-interface.md) and
[accepted authority](../../investigations/grc9v4-constitutive-design/decisions/p9-basin-interface/Authority.json)
require one fresh realization read per captured role. Typed forensic queries
of `P9-EC-GRC9-BASIN-INPUTS` and `P9-EC-GRC9-BASIN-LIFECYCLE` confirm the
existing contract. This work adds native conformance, not scientific authority.

C_RG2b capture reconstructs `CandidateRG2bSection`, then Candidate-C current at
that section's geometry. It binds the query C, full selected H/current, completion
recipe, domain/certificate, six-level approximation, evaluation count, error and
enclosure. Both roles are reconstructed independently. W_A and Z_4 remain absent.
Observation advances no writer, resource state, clock or lifecycle journal.
Diagnostic dt=0 does not replace the frozen beat inside the completion law.

Public numeric observables project the selected current point; the separately
bound section supplies its certificate. An initial development run caught this
projection missing from the new integration. The existing lifecycle tests now
pass after the correction. No failed-session payload is retained.

The numerical producer, completion, tolerances, fixture and arithmetic policy
are unchanged. The selected connected signed-argument completion uses six
levels, eighteen sweeps, 222 evaluations, Arb 192-bit certification and FLINT,
with section tolerance 2^-48. It admits reads on its declared K domain; this
diagnostic does not add an ordinary-entry K-minus requirement.

## Independent checks and scope

Reuse [connected runtime checks](../verification/p9_crg2b_runtime.py) and the
[independent section certificate](../verification/p9_crg2b_section.py). The
native finite chain is observed during the actual read. The independent checker
uses unreduced edge equations, including state/geometry residuals, finite tail,
completion and graph hypotheses. It does not substitute an instantaneous
H = I + kappa_H S equation for the nonlocal section.

The [basin adapter](../verification/p910_crg2b_basin_oracle.py) keeps two errors
separate: the current error at represented H, and the total current error after
propagating the certified section error through the existing H-Lipschitz bound:

$$
e_J^{\mathrm{section}} = e_J^{\mathrm{fixed\ H}} + L_{J,H} e_H,
\qquad L_{J,H} = \frac{A_H}{\Delta t\,\lVert B\rVert_\infty}.
$$

Here A_H and the frozen beat belong to the existing connected completion proof.
At both exact target boundaries, all sixteen represented nonzero currents per
role exceed both reported error bounds. Maximum fixed-H error is 1.57e-15;
maximum section-aware current error is 6.87e-15. Section error is at most
1.11e-16, below 2^-48. These are exact-subject bounds, not a uniform trajectory
certificate or a new graph/domain theorem.

The source pressure conserves charge while redistributing resources between
two vertices. Selected currents separate by about 2.93e-3, above the combined
section-aware error 1.18e-14. Wrong-query reads and corrupted H with unchanged
J are rejected. Completion/enclosure/certificate and claim-scope mutations fail.
The native section still rejects a classical Jacobian: C1 remains unresolved.
There is no new exact-root, basin-attraction, general ATC, family-wide conformance
or G4 claim. Classification remains the accepted represented-flow diagnostic.

## Native execution and P9-10.2 reuse

All eight tests pass in two parallel FLINT jobs using `legacy_exact_v1`:
five source/lifecycle/scientific tests in 133.0 seconds, and three exact-target
compatibility tests in 87.6 seconds. These exercise policy migration, ordinary
steps, mechanical expansion, reset/rebase, exact/state-only replay, save/load,
assignment, stale-read rejection and full-publication rollback.

Both retained 17-node/16-edge target variants are compared against independently
constructed V3 delegates on transition, state, observable and lifecycle surfaces.
Disabled return preserves the declared resource transfer and reconstructs the
C section; it invents no W or carrier history. Current/reset resources are
still distinct after disabled return.

The compatibility execution captures both roles at policy migration and disabled
return, once, for 10.1c. P9-10.2 reuses its executed replay, four saved charge
checks and 53 receipts across fifteen commit groups. Parent, endpoint and
emitted-delta checks pass; no added native steps or replay runs are needed.

Twenty-six focused retained-evidence and family API/browser/notebook checks
pass. They include section/query/enclosure/scope mutations, no native section
solve during retained checking, historical source preservation and stale-view
clearing. The public explicit-policy test also passes. The three retained first-group
checks pass; five Tranches 8–9 checks verify the refreshed maintenance bindings.
Earlier-family numerical campaigns are not rerun.

## Retention and access

Earlier accepted execution/review/decision bytes remain unchanged. The finite
source-epoch adapter authenticates original Git preimages; AST checks establish
that the added C_RG2b capture and numeric projection leave earlier paths intact.

- [Source/lifecycle execution](P9-10-CRG2b-Native.json): 528,708 bytes.
- [Exact-target execution](P9-10-CRG2b-Target.json.xz): 98,428 compressed bytes,
  4,931,870 decoded bytes, including the observed chains.
- [Consolidated verification](P9-10-CRG2b-Verification.json): references the parts
  and reconstructs the semantic record exactly, without repeating payloads.
- [Source epochs](P9-10-CRG2b-SourceEpochs.json).

From the repository root:

```bash
PYTHONPATH=src:.:implementation/phase-9-grcv4/verification .venv/bin/python implementation/phase-9-grcv4/verification/p910_family_basin.py --check --family C_RG2b
```

The check authenticates saved evidence, section bindings, rows/classification,
charges and receipts; it does not run native trajectories, replay or sections.
`--equations` additionally rechecks the saved chains and independent equations.
`--run` executes missing parts in parallel and never overwrites retained evidence.

Side-tool access is `/api/tranche10/families?family=C_RG2b`, the existing browser
family selector and notebook cell `p910-crg2b-basin`. The view exposes compact
error summaries and indexed source links; full chains remain in the compressed
target evidence. Bounded acceptance is a separate decision.
