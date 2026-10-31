# A_CI_PC — bounded P9-10.1a–c and P9-10.2

Implemented and validated on 2026-10-31; user acceptance is pending. Same branch `work/p9-tranche10-remaining-families`, after accepted
C_CI_PC `b994fabe`. Original accepted evidence and decisions remain unchanged.
C_RG2b, A_RG2b and consolidated 10.3–10.6 are separate.

## Contract and implementation

The [basin specification](../../../specs/grc-9-v4-basin-interface.md) and
[accepted authority](../../investigations/grc9v4-constitutive-design/decisions/p9-basin-interface/Authority.json)
require fresh realization-specific observations and complete role/root binding.
Typed contract queries confirm the existing input, lifecycle and claim-ceiling
authority. This is native conformance work, not new scientific authority.

Production only adds A_CI_PC to the explicit capture roster. Its existing
`CandidateCIRoot` path consumes the fixed-row Candidate-A backend, W_A and
committed Z, retaining the complete selected J/H, generated H, residual,
domain/certificate and recipe. Observation runs no ordinary step or writer.

The unchanged selected composite law is

$$
H = H_{\mathrm{ref}} + \kappa_H\bigl(Z_{\mathrm{old}} + S(J,H)\bigr).
$$

Here rho_inst=1 and composition gain 2 bounds the composite envelope; the gain
does not double the instantaneous source. The retained parameter set uses
kappa_H=2^-15, joint tolerance 2^-44, 60 iterations, domain radius 1/8 and
carrier radius 2048. Candidate-A coefficients and inactive-floor assumptions
match the existing independent equation oracle. No numerical policy, fixture,
kernel, law, tolerance or accepted domain is changed.

## Execution and pressure

All eight tests passed in two parallel FLINT jobs using `legacy_exact_v1`: five
source/lifecycle/scientific tests in 277.9 seconds and three exact-target
compatibility tests in 142.8 seconds. The source
preflight passes full fresh-root equality and separate lawful W-only and Z-only
changes. Both affect selected current beyond combined fixed-geometry error.
Old-history reads and corrupted geometry with unchanged current are rejected.
The complete scientific/lifecycle payload remains unchanged during observation.

The native suites exercise public capture, explicit basin-policy migration,
ordinary evolution, mechanical expansion, reset/rebase, exact/state-only replay,
save/load/assignment, stale reads and complete rollback. The exact retained
17-node/16-edge v1 target and explicit v2 basin successor are compared with an
independently constructed V3 delegate on transition/state/observable/lifecycle
surfaces, including negative and late-publication pressure.

At return from disabled execution, W_A is initialized independently for each
role using the accepted reference pass; Z is initialized to zero. Both losses
are explicit. This is not preservation of either incoming history. The same
round trip captures both roles at policy migration and disabled return for
10.1c, then reuses saved charges, receipts and executed replay for 10.2. Four
charges are admitted; all 53 receipts in 15 commit groups satisfy parent,
endpoint and emitted-delta checks. Zero added native steps or replays.

Twenty retained-evidence and family API/browser/notebook checks pass, including
history/backend/root/domain mutations, source preservation, scope widening and
stale-view clearing. The focused public explicit-policy test also passes.
Eight additional retained checks preserve the accepted first-four views and
Tranches 8–9 closeout. Earlier-family numerical campaigns are not rerun.

## Numerical scope

On the source, changing Z alone separates selected currents by about 1.75e-4,
against 5.09e-17 combined fixed-geometry error. The W-only change separates
them by 1.67e-4, against 4.02e-17 combined error. Carrier omission gives about
3.91e-3 residual in both roles; instantaneous omission gives at least 1.21e-12,
also above solver tolerance. These selected-point controls do not estimate
full implicit-root effect uncertainty.

The completed target execution passes the independent A current/geometry
equations at both captured boundaries. All sixteen represented signs per role
are certified at each saved geometry. The A denominator lower bound stays
above 0.99999997.
At policy migration, current error is about 5.96e-16 and geometry residual
1.04e-16 or smaller. Omitting old Z produces a residual lower bound about
1.05e-12; omitting the instantaneous term gives about 4.37e-9. Both exceed
the selected joint tolerance 2^-44 (5.68e-14).

These are checks at the saved represented geometry. A fixed-H current error,
positive denominator and separate geometry residual do not establish exact
implicit-root signs/effect bounds, a uniform trajectory enclosure, basin
attraction, general ATC or family-wide conformance. After disabled return the
declared carrier is zero, so no nonzero carrier effect is claimed there. The
instantaneous omission residual after return is also below tolerance (about
1.46e-27 or smaller); its mechanism effect is not resolved at that boundary.
Maximum current error across all four target observations is below 1.22e-15.

## Retention and access

The finite source successor preserves earlier execution/review bytes and
authenticates their Git preimages. Original pending-at-execution flags are not
rewritten. Native parts over 1 MB are compressed; the consolidated record
references those parts and checks exact semantic reconstruction. The target
part is 88,588 compressed bytes for 5,150,023 decoded bytes; the source/lifecycle
part is 239,712 bytes.

- [Source/lifecycle execution](P9-10-ACIPC-Native.json).
- [Exact-target execution and both-role captures](P9-10-ACIPC-Target.json.xz).
- [Consolidated verification](P9-10-ACIPC-Verification.json).
- [Source-epoch binding](P9-10-ACIPC-SourceEpochs.json).

From the repository root:

```bash
PYTHONPATH=src:.:implementation/phase-9-grcv4/verification .venv/bin/python implementation/phase-9-grcv4/verification/p910_family_basin.py --check --family A_CI_PC
```

This verifies retained source/part bindings, full roots, rows/classification,
charges and receipts without native trajectories/replay. `--equations` adds
independent interval recomputation on saved target operands. `--run` resumes
missing native parts in parallel and refuses to overwrite retained evidence.
Fresh native checks can run without replacing the retained records:

```bash
PYTHONPATH=src:.:implementation/phase-9-grcv4/verification .venv/bin/python -m unittest test_p910_acipc_basin.ACIPCNativeBasin test_p910_acipc_basin.ACIPCTargetCompatibility -v
```

Side-tool access: `/api/tranche10/families?family=A_CI_PC`, existing browser
family selector, indexed sources and notebook `p910-acipc-basin`. Acceptance is
separate; no remaining-family, full-conformance or G4 decision is inferred.
