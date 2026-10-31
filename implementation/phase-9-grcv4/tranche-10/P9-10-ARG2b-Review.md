# A_RG2b — bounded P9-10.1a–c and P9-10.2

Implemented and validated on 2026-10-31; user acceptance is pending.
Branch `work/p9-tranche10-remaining-families`, after C_RG2b acceptance
`35dc5a48`. This is the last family in the declared rollout. All-ten
reconciliation and consolidated P9-10.3–10.6 remain separate.

## Contract and implementation

The [basin specification](../../../specs/grc-9-v4-basin-interface.md) and
[accepted basin authority](../../investigations/grc9v4-constitutive-design/decisions/p9-basin-interface/Authority.json)
require a fresh realization-specific read from one captured role. The accepted
[connected A completion](../../../specs/grc-9-v4-connected-a-rg2b-spec.md)
already supplies the section, fixed-row backend and numerical domain. No new
scientific authority, debt adjudication, constitutive law or tolerance is added.

A_RG2b capture reconstructs `CandidateRG2bSection` on the joint query
C and Y=512 log W_A, then Candidate-A current at the section geometry using the
fixed-row backend. It binds full H/current, C/W, backend, completion recipe,
domain certificate, approximation count and enclosure. Backend substitutions
are rejected even with unchanged point inputs. Z_4 stays absent. Observation
advances no resource/history writer, clock or journal. Its dt=0 stage retains
the frozen beat used inside the completion law.

The existing public numeric projection consumes the section's selected point.
Earlier C_RG2b and all other capture paths retain their prior behavior, checked
by the finite AST/source successor. Numerical kernels, fixtures, parameters and
policies are unchanged: four section levels, eighteen sweeps, 148 evaluations,
Arb 192-bit certification, FLINT and section tolerance 2^-48.

## Independent mathematics and pressure

Reuse the [joint section certificate](../verification/p9_arg2b_section.py) and
[connected A runtime checker](../verification/p9_arg2b_runtime.py). The native
chain is observed during the actual read. Independent unreduced edge equations
check the joint inverse residuals, geometry residuals, completion tail and
represented-to-exact scaled-log query error. This is not an instantaneous CI
geometry equation or an OS reference restart.

The [basin adapter](../verification/p910_arg2b_basin_oracle.py) explicitly checks
the connected proof's A coefficients, reference/base, context and completion
policy. It retains both native and independent section error estimates, whose
outward widths can differ, and uses their maximum to propagate the existing
current H-Lipschitz bound:

$$
e_H = \max(e_H^{\mathrm{native}}, e_H^{\mathrm{independent}}),
\qquad e_J^{\mathrm{section}} = e_J^{\mathrm{fixed\ H}} + L_{J,H}e_H.
$$

The independent section error includes its scaled-log input term as well as
the finite-chain and tail contributions. On the four target captures, the
maximum fixed-H current error is below 1.60e-15; the maximum section-aware
current error is below 7.75e-15. Section error is below 1.20e-16, compared with
tolerance 2^-48. All sixteen represented nonzero currents in each capture exceed
both current-error bounds. At policy migration the log-coordinate error is
about 2.76e-17, contributing about 2.69e-20 to the section error. These terms
remain retained after disabled return, where they are smaller but nonzero.

Source pressure changes W alone inside the signed-log chart. Selected currents
separate by about 2.98e-6, against a combined section-aware error of 1.06e-14.
Wrong-history reads, a valid but differently oriented backend, and changed H
with unchanged J are rejected. Retained mutations cover query, history, backend,
completion, geometry, enclosure, certificate, log error and widened claims.
The native section still rejects a classical Jacobian: C1 remains unresolved.

These are bounds on the exact saved subjects, not a uniform trajectory
certificate, general graph theorem, basin-attraction claim, general ATC or
full-family/G4 conformance. The basin law still classifies represented flow.
The existing `exact_root_signs_claimed=false` ceiling is retained; section sign
counts report only the separately declared error comparison on these subjects.

## Native execution and reuse

All eight tests pass in two parallel FLINT jobs using `legacy_exact_v1`:
five source/lifecycle/scientific tests in 77.6 seconds and three exact-target
compatibility tests in 52.4 seconds. Coverage includes explicit policy migration,
ordinary steps, mechanical expansion, reset/rebase, exact/state-only replay,
save/load/assignment, stale reads and complete-publication rollback.

The exact retained 17-node/16-edge v1 target and its explicit v2 basin successor
are compared with independently constructed V3 delegates on transition, state,
observable and lifecycle surfaces. Disabled return archives/drops prior A
history and initializes W independently for each role with the accepted
reference pass. Current/reset resources and W remain distinct. No carrier
channel is introduced, and W initialization is not history preservation.

Both roles are captured at policy migration and disabled return during that
same compatibility execution. P9-10.2 reuses four admitted saved-charge checks
and 53 receipts in fifteen commit groups. Parent, endpoint and emitted-delta
checks pass. No extra native steps or replay runs are added for 10.2.

Seventeen focused retained-evidence, real API/browser/notebook and public-policy
checks pass for A_RG2b,
accepted C_RG2b source preservation, the accepted first-four views, and the
public explicit-policy successor. Five Tranches 8–9 closeout checks verify the
refreshed maintenance bindings. Earlier-family numerical campaigns are
not rerun.

## Retention and access

Accepted execution, review and decision bytes are unchanged; original sources
remain authenticated through their Git preimages. Execution-time pending flags
are preserved, with any later acceptance recorded separately.

- [Source/lifecycle execution](P9-10-ARG2b-Native.json): 539,579 bytes.
- [Exact-target execution](P9-10-ARG2b-Target.json.xz): 112,540 compressed bytes
  for 4,979,690 decoded bytes, including observed joint chains.
- [Consolidated verification](P9-10-ARG2b-Verification.json): references the
  parts and reconstructs the original semantic record without payload duplication.
- [Source epochs](P9-10-ARG2b-SourceEpochs.json).

From the repository root:

```bash
PYTHONPATH=src:.:implementation/phase-9-grcv4/verification .venv/bin/python implementation/phase-9-grcv4/verification/p910_family_basin.py --check --family A_RG2b
```

The retained check authenticates bindings, selected sections, rows/classification,
charges and receipts without running native sections, trajectories or replay.
`--equations` recomputes the independent checks from saved chains. `--run` executes
missing parts in parallel and never overwrites retained evidence. The checker
uses the declared FLINT context when inspecting a captured native A point;
standalone callers need not inherit a live native arithmetic context.

Side-tool access: `/api/tranche10/families?family=A_RG2b`, the shared browser
selector, indexed sources and notebook `p910-arg2b-basin`. Compact error summaries
are exposed in the view; complete chains remain in the compressed evidence.
An empty remaining-family list means this is the last rollout row, not that
all-ten acceptance, consolidated conformance or G4 has been granted.
