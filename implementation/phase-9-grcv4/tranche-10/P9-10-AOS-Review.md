# A_OS — bounded P9-10.1a–c and P9-10.2

Implemented and validated; user acceptance is pending. The work uses branch
`work/p9-tranche10-remaining-families`. Accepted C_OS/C_CI/A_CI/A_PC evidence
remains unchanged. The other five basin extensions are not executed here.

The existing diagnostic law applies: capture a fresh Candidate-A current at
reference geometry, from the selected role's current C/W and fixed-row backend.
This is not an OS predictor/corrector step, history writer or persistent carrier.
The sole production change adds that A branch and A_OS to the explicit basin
capture population. Existing v1 identities retain their meaning; opting into the
v2 basin policy remains an explicit, identity-changing migration.

The [accepted authority](../../investigations/grc9v4-constitutive-design/decisions/p9-basin-interface/Authority.json)
and [specification](../../../specs/grc-9-v4-basin-interface.md) define the law.
Typed forensic `contract_provenance` queries confirm required support for
`P9-EC-GRC9-BASIN-INPUTS`, `P9-EC-GRC9-BASIN-LIFECYCLE` and
`P9-EC-GRC9-BASIN-CEILING`. No new scientific law or debt resolution is inferred
from the additional native coverage. The specification's initial four-family
scope is historical; this is a separately reviewed implementation extension.

## Execution and independent checks

Two independent native jobs ran in parallel: five source-lifecycle/scientific
tests (about 50 seconds) and three exact-target compatibility tests (about 44
seconds). Both use FLINT and the unchanged declared numerical policy. The
native kernels, delegates, lifecycle and replay paths are real; reusable tests
adapt only their fixture/configuration providers.

| Checkpoint | Result and evidence |
| --- | --- |
| 10.1a | Fresh source observations for both roles; public steps, expansion, reset/rebase, exact and state-only replay, assignment/save/load, explicit policy migration, disabled delegation, stale-read rejection and atomic rollback. Independent A equations and a W-only control distinguish retained history, correct stage and full geometry. |
| 10.1b | The exact accepted 17-node/16-edge v1 target and its explicit v2 successor pass transition/state/observable/lifecycle comparisons, using an independently constructed native V3 delegate. Six rejection cases remain distinct from successful compatibility. |
| 10.1c | During that same v2 round trip, capture both roles immediately after policy migration and immediately after disabled return. Reconstruct saved C/W, context, reference/backend and complete read; independently recompute rows, classification and A equations. No duplicate crossing campaign. |
| 10.2 | Reuse this family's actual replay and receipts; independently check four saved charges and 53 receipts in 15 commit groups across v1/v2. Reuse the accepted common charge-edge controls, whose numerical kernel is unchanged. No additional native steps or replay runs. |

The original expanded target has equal resource/history roles. Disabled
execution followed by explicit return produces distinct current/reset C and W,
each checked against its own independent initializer. At both observation
boundaries all 16 represented current signs lie outside the independent
fixed-geometry error enclosure; the geometry equation is exactly the reference
restart. This is pointwise evidence, not a uniform parameter or trajectory bound.

Source pressure changes W alone and observes a changed current/read identity.
It rejects a plausible OS corrector at the wrong stage and a copied read whose J
is unchanged but H is corrupted. Retained mutation checks also reject swapped
subjects/boundaries, history, geometry, rows, widened claims and broken receipts.
The original shared classifier's graph/zero/parallel-route pressure remains
applicable: its implementation is unchanged.

## Retention and reproduction

- [Native source/lifecycle record](P9-10-AOS-Native.json).
- [Exact target execution and boundary captures](P9-10-AOS-Target.json.xz).
- [Consolidated verification](P9-10-AOS-Verification.json).
- [Source-epoch binding](P9-10-AOS-SourceEpochs.json).

The target record is about 77 KB compressed (4.4 MB decoded). The consolidated
record stores references instead of another copy of that payload; reconstruction
must recover the exact recorded digest. Original execution inputs and outcomes
are retained. No machine-local path or external download is required.

From the repository root:

```bash
PYTHONPATH=src:.:implementation/phase-9-grcv4/verification .venv/bin/python implementation/phase-9-grcv4/verification/p910_family_basin.py --check --family A_OS
```

`--check` validates retained identities, source bindings, rows/classification,
charges and receipt chains. It does not rerun trajectories or constitutive
equations. Add `--equations` only when an independent saved-equation recheck is
needed. The two native parts were generated with `--run`; completed parts are
source-bound and reused, and existing output is never silently overwritten.

The finite source successor authenticates both original Git preimages and
current hashes. An exact AST check isolates the A_OS extension from the
unchanged first-four native capture paths. Historical source links retrieve
their original bytes, not current files relabelled as old execution inputs.

The side-tool exposes `/api/tranche10/families?family=A_OS`, indexed source
downloads, a family selector in the browser and notebook cell
`p910-family-basin`. These surfaces perform retained checks only, preserve
pending acceptance and clear stale output on failure.

## Scope and continuation

This proves the bounded declared A_OS subjects and operations. It does not
establish attracting basins, physical identity persistence, arbitrary-graph
conformance, general ATC, new profile support or G4. Original four-family
acceptances and all historical Tranche 8–9 execution flags remain unchanged.

Next: bounded A_OS review/acceptance, then C_PC P9-10.1a–c → P9-10.2. The
remaining order is C_CI_PC, A_CI_PC, C_RG2b and A_RG2b, before consolidated
P9-10.3–10.6.
