# A_RG2b ATC research — reviewed package and scoped admission

[Fit assessment and next steps](../../decisions/ATCRGATCProgram.md) ·
[Original direction](RGATC-Direction.md) · [Pending claim/debt routes](RGATC-Intake.json)

[Audit PASS reported by the user](RGATC-Review.md), 2026-09-24.

[Scoped adjudication and source admission](../../decisions/ATCRGATCClaimDebtAdjudication.md)
are complete. The intake and package retain their historical pending flags;
the [successor ledger](../atc-rgatc-admission/ATCRGATCClaimDebtLedger.json) is
the current acceptance authority.

## Read the existing work

| Stage | Supplied material | Current status |
| --- | --- | --- |
| RGATC-T | [Section and reconstructive-continuation theorem](package/predecessor/RGATC-T.md) | Reported audit PASS; local T/A checks pass |
| RGATC-A | [Explicit completion and positive existence profile](package/predecessor/RGATC-A.md) | Reported audit PASS; exact certificate regenerated |
| RGATC-E | [Executed witness](package/RGATC-E.md) | Reported audit PASS; full execution remains supplied evidence |
| RGATC-R | [Section evaluator proof](package/RGATC-R-SectionEvaluator.md), [reference scope](package/RGATC-R-Scope.md) | Reported audit PASS for bounded finite conformance |

The self-contained [package](package/README.md) includes the original code,
oracle and certificates, with one copy of its T/A predecessor. Paths inside
package records are relative to the package root (T/A records to predecessor);
repository correspondences in the source map are repository-root-relative.
No extraction archive or machine-local input directory is needed after cloning.

Proof/code/scientific certificate bytes are preserved. Packaging metadata alone
was normalized and its manifests refreshed. `REPRODUCTION.json` is the
supplier's report, not a new local full run. The subsequent audit PASS is
recorded separately; historical pending flags in the intake/package remain
unchanged. The separate successor supplies source admission and local debt
decisions, never native support or global debt discharge.

## Reproduce from repository root

```sh
RGATC=implementation/investigations/grc9v4-constitutive-design/evidence/atc-rgatc/package
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python "$RGATC/predecessor/pressure_rgatc_ta.py"
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python "$RGATC/check_rgatc_er.py" --check
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python "$RGATC/pressure_rgatc_er.py"
```

These checks passed locally at intake. The first regenerates T/A twice; the
other two only check retained E/R evidence. For the separate full E/R rerun:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python "$RGATC/check_rgatc_er.py" --compare
```

That last command executes the full reference suite and checks exact equality;
it was not run during this quick intake. Supplied E/R pressure records include
19 boundary, 14 lifecycle and three representation negative cases. Those counts
are retained results, not newly executed lifecycle tests.

All 28 A_RG2b debt routes are adjudicated: 14 locally closed, six partial,
eight inactive. Earlier accepted admissions and global origin debts are
unchanged. All five Candidate-A bounded research programs are now closed;
see the [closeout](../../decisions/ATCCandidateAResearchClosure.md).
