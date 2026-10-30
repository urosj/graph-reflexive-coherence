# C_PC — bounded P9-10.1a–c and P9-10.2

Implemented and validated; user acceptance is pending. This extends the
remaining-family branch after accepted A_OS (`59e9f9b9`). The first four and
A_OS acceptance/execution records remain unchanged. The other four remaining
basin extensions and consolidated 10.3–10.6 are separate.

The sole production change admits C_PC to the existing basin capture roster.
Its existing `CandidatePCRead` reconstructs geometry from the selected role's
committed Z, then reads Candidate-C current and the full PC certificate.
Observation does not advance a carrier writer and does not introduce W_A.
The v1 target remains available; opting into the basin policy is an explicit
identity-changing migration to its v2 successor.

The [accepted authority](../../investigations/grc9v4-constitutive-design/decisions/p9-basin-interface/Authority.json)
and [basin specification](../../../specs/grc-9-v4-basin-interface.md) supply the
law. Typed forensic `contract_provenance` queries confirmed required support
for `P9-EC-GRC9-BASIN-INPUTS`, `P9-EC-GRC9-BASIN-LIFECYCLE` and
`P9-EC-GRC9-BASIN-CEILING`. This is additional native conformance evidence,
not a new scientific law or claim/debt closure. The specification's original
four-family implementation scope remains historical.

## Execution and scientific discrimination

Two independent jobs ran in parallel using FLINT and `legacy_exact_v1`:
five source/lifecycle/scientific tests (75 seconds) and three exact-target
compatibility tests (71 seconds). All eight passed without skips.

| Checkpoint | Bounded result |
| --- | --- |
| 10.1a | Fresh both-role capture, public observation, steps, expansion, reset/rebase, explicit policy migration, exact/state-only replay, assignment/save/load, disabled delegation, stale-read rejection and complete rollback. |
| 10.1b | Exact accepted 17-node/16-edge v1 target and explicit v2 successor: independent native V3 transition/state/observable/lifecycle comparisons, both-role return, replay, six rejection cases and late-publication failures. |
| 10.1c | Both roles immediately after policy migration and after disabled return, captured during the same v2 round trip. Saved C/Z, graph/context, complete PC read/certificate, fixed rows, classification and independent equations are checked. |
| 10.2 | Four saved charge checks; 53 receipts in 15 commit groups across v1/v2; emitted delta versus persistent ledger and parent/end-state bindings. Reuse this family's actual replay and the unchanged shared charge controls. Zero added native steps or replays. |

The accepted C_PC fixture uses zeta_C = 2^-30, rather than the earlier C_OS/CI
witness's 2^-37. The independent interval equations explicitly check and use
that coefficient. A wrong-coefficient control fails the current comparison.
No fixture parameter or error tolerance was relaxed.

The source has distinct current/reset carrier histories. Setting only the
current carrier to zero, with its lawful reconstructed geometry, changes J by
about 9.16e-8, above the combined independent error bound (about 5.61e-17).
The test also rejects a read from another Z state and rejects corrupted H even
when J is unchanged. Native geometry construction itself rejects a mismatched
carrier/H pair. A patched ordinary-step entry point confirms observation does
not invoke a step/writer; state and lifecycle identities are unchanged.

At each exact-target boundary all sixteen represented current signs lie outside
the independent fixed-geometry error enclosure. This is a pointwise current
bound and a separate PC geometry residual, not a uniform trajectory enclosure
or exact-real basin/attractor claim. The original expanded target's roles are
equal; disabled evolution/return yields distinct current/reset resources.
Both nonzero pre-crossing carriers are lost under the explicit crossing policy,
and both target carriers are initialized to zero. Zero Z at that boundary is
therefore deliberate initialization, not preserved carrier history.

Ten focused retained-mutation and API/browser/notebook tests pass across C_PC
and accepted A_OS. Pressure covers resealed carrier, certificate, geometry,
coefficient and scope changes, historical source retrieval, failed-view clearing
and separation of execution from acceptance. Fresh execution cannot inherit
historical source labels: those are used only when checking the frozen A_OS
records. A new A_OS run requires its own declared evidence epoch. The common classifier and charge
kernel are unchanged; their already accepted graph/threshold/rounding controls
are reused.

Development note: the first new zero-carrier test changed Z without rebuilding
its required geometry. Native construction correctly rejected that fixture;
the fixture was corrected. Corrupt-H pressure then explicitly tested both the
native constructor rejection and the independent oracle on a forged point.
Only final source-bound execution is retained; no failed-session archive.

## Evidence and reproduction

- [Source/lifecycle execution](P9-10-CPC-Native.json).
- [Exact-target execution and captures](P9-10-CPC-Target.json.xz).
- [Consolidated verification](P9-10-CPC-Verification.json).
- [Finite source-epoch binding](P9-10-CPC-SourceEpochs.json).

The target record is about 80 KB compressed. The consolidated record stores
references to its native parts and must reconstruct the original semantic
digest exactly. No duplicate target payload or machine-local input is needed.
The finite epoch authenticates changed helpers and the one-line production
roster extension, while preserving accepted evidence and original Git sources.

From the repository root:

```bash
PYTHONPATH=src:.:implementation/phase-9-grcv4/verification .venv/bin/python implementation/phase-9-grcv4/verification/p910_family_basin.py --check --family C_PC
```

`--check` verifies retained identities, sources, rows/classification, charge
and receipt checks; it runs no native trajectory or replay. Add `--equations`
to recompute the independent interval equations on the saved target inputs.
`--run --family C_PC` resumes missing native parts in parallel and refuses to
overwrite existing evidence. Fresh native tests can be run without replacing
the retained records:

```bash
PYTHONPATH=src:.:implementation/phase-9-grcv4/verification .venv/bin/python -m unittest test_p910_cpc_basin.CPCNativeBasin test_p910_cpc_basin.CPCTargetCompatibility -v
```

Side-tool: `/api/tranche10/families?family=C_PC`, indexed source downloads,
browser family selector and notebook `p910-cpc-basin`. Pending C_PC acceptance
is separate from accepted A_OS. After acceptance, C_CI_PC is next. Full
conformance, all-ten Tranche 10 closure and G4 remain false.
