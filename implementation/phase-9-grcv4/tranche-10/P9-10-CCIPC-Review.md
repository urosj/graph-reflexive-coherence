# C_CI_PC — bounded P9-10.1a–c and P9-10.2

Implemented and validated; user acceptance is pending. Work
continues on `work/p9-tranche10-remaining-families` after accepted C_PC
(`9fb469c8`). Earlier accepted native evidence and decisions remain unchanged.
The remaining A_CI_PC, C_RG2b, A_RG2b and consolidated 10.3–10.6 are separate.

## Contract and selected observation

The [basin specification](../../../specs/grc-9-v4-basin-interface.md) and
[accepted authority](../../investigations/grc9v4-constitutive-design/decisions/p9-basin-interface/Authority.json)
require a fresh realization read for each captured role, with complete joint
root/geometry and certificate identity. Typed forensic queries confirm required
support for the INPUTS, LIFECYCLE and CEILING contracts. This extends native
coverage of that law; it does not create new scientific authority or close debt.

The production extension admits C_CI_PC and uses the existing `CandidateCIRoot`
path for CI+PC, including its joint-root binding. No constitutive kernel, solver,
tolerance, writer or graph is changed. Observation uses fixed committed Z and
the same root's instantaneous source together:

$$
H = H_{\mathrm{ref}} + \kappa_H\bigl(Z_{\mathrm{old}} + S(J,H)\bigr).
$$

The selected contract has rho_inst=1 and composition gain 2. The latter is the
composite envelope bound, not a multiplier that doubles the source in this
equation. The C transport coefficient is the actual retained value zeta_C=2^-30.
The root recipe, selected J/H, generated H, residual, certificate/domain and
both-role C/Z are bound. There is no Candidate-A W history or observation writer.

## Bounded execution and pressure

Two independent jobs use FLINT and `legacy_exact_v1`: five source/lifecycle and
scientific tests (734.8 seconds), and three exact-target compatibility tests
(419.8 seconds). All eight passed. They use the exact accepted 17-node/16-edge v1
target and its explicit basin-policy v2 successor. Both-role observations at
policy migration and disabled return are captured during that same round trip
for reuse in 10.1c/10.2; no duplicate trajectory campaign.

10.2 validates 53 receipts in 15 commit groups, including parent/endpoint and
emitted-delta bindings, plus four admitted saved-charge checks. It adds zero
native steps and zero native replays.

The focused source pressure checks full fresh-root equality, including selected
geometry and certificate, rather than current alone. It independently checks
the composite equation and two omission controls; changes only Z with lawful
reconstruction; rejects the older C coefficient, a read from another carrier
state, and corrupted H with unchanged J. Observation cannot invoke the ordinary
step/writers and leaves scientific state and lifecycle unchanged.

The native lifecycle suite covers explicit policy migration, public observation,
steps, expansion, reset/rebase, exact/state-only replay, assignment/save/load,
disabled delegation, stale reads and atomic failures. Exact-target compatibility
uses an independently constructed native V3 delegate on all four surfaces,
both-role return, full replay, six rejection cases and late-publication pressure.
Disabled execution retains V3 behavior. On return, each carrier is initialized
to zero under the explicit loss policy; it is not preserved carrier history.

Fourteen retained-evidence and API/browser/notebook tests pass, including
resealed root/carrier/domain mutations, false acceptance, scope widening,
historical-source retrieval and stale-view clearing. The focused public C_CI_PC
contract check also passes. These checks do not rerun native trajectories.

## Numerical limits

On the source, carrier omission leaves about 9.54e-7 geometry residual in each
role. The lawful zero-current-carrier control separates selected currents by
9.16e-8, versus 6.70e-17 combined fixed-geometry current error. Instantaneous
omission is much smaller for current (6.68e-16) than reset (3.87e-12); only the
reset value exceeds the solver tolerance. Full-root uncertainty is not inferred
from any of these fixed-geometry comparisons.

At both exact-target boundaries, all sixteen represented current signs per role
lie outside the independent fixed-geometry error enclosure. Maximum current
error is about 2.93e-15; geometry residuals are about 1.11e-16 or smaller.
These are pointwise results at the selected represented H, with a separate
geometry residual. They are not exact implicit-root signs, a uniform trajectory
bound, basin attraction/stability, or family-wide conformance.

At policy migration, omitting the instantaneous term gives a geometry-residual
lower bound about 1.29e-11, above the joint solver tolerance 2^-44 (5.68e-14).
Omitting the transferred carrier gives about 3.06e-15: above the observed full
equation residual, but below that solver tolerance. The target carrier is bound
and independently accounted for; this does not certify its effect against the
entire implicit-root uncertainty. After disabled return, Z is explicitly zero,
so a nonzero carrier effect at that boundary is neither expected nor claimed.

## Retention and reproduction

The source/lifecycle record is about 235 KB. The exact-target record is about
88 KB compressed (5.13 MB decoded). The final
consolidated view references bound native parts and requires exact semantic
digest reconstruction. Accepted first-four/A_OS/C_PC evidence is unchanged;
the finite successor authenticates changed helpers and serves original Git
source bytes. Fresh execution never inherits historical source labels.

- [Source/lifecycle execution](P9-10-CCIPC-Native.json).
- [Exact target execution and captures](P9-10-CCIPC-Target.json.xz).
- [Consolidated verification](P9-10-CCIPC-Verification.json).
- [Source-epoch binding](P9-10-CCIPC-SourceEpochs.json).

From the repository root:

```bash
PYTHONPATH=src:.:implementation/phase-9-grcv4/verification .venv/bin/python implementation/phase-9-grcv4/verification/p910_family_basin.py --check --family C_CI_PC
```

This checks retained bindings, full selected reads, rows/classification, saved
charges and receipt chains without native trajectories/replay. `--equations`
adds independent interval recomputation on the saved target inputs. `--run`
resumes missing native parts in parallel and refuses to overwrite evidence.
Fresh native checks can run without replacing retained records:

```bash
PYTHONPATH=src:.:implementation/phase-9-grcv4/verification .venv/bin/python -m unittest test_p910_ccipc_basin.CCIPCNativeBasin test_p910_ccipc_basin.CCIPCTargetCompatibility -v
```

Side-tool access uses `/api/tranche10/families?family=C_CI_PC`, the existing
browser family selector and notebook `p910-ccipc-basin`. Acceptance is separate;
after it, A_CI_PC is next. No all-ten Tranche 10 closure or G4 grant is inferred.
