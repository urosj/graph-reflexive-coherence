# A_OS fifth-realization review

Branch: `work/p9-aos-tranches-8-9`, based on `02528b5d`.
The user selected this work on 2026-10-28 and explicitly requested FLINT and
any necessary improvements for larger graphs. P9-10.2 is deferred.

The machine-readable [review](P9-AOS-Tranches8-9-Review.json) is the completion
record. Its builder consumes each checkpoint's retained evidence before writing
the review. All new results remain pending user acceptance. The accepted
C_OS/C_CI/A_CI/A_PC records and the earlier A_OS P9-8.4b/c decisions are unchanged.

## Scope and evidence

| Checkpoint | Bounded obligation and retained record |
| --- | --- |
| 8.4d | Twenty D59/66/73/94 layouts, forty histories, ten steps per role, independent A_OS predictor/corrector, split, continuity and W-writer checks. `P9-8.4d-AOSOracleResults.json.xz` and `P9-8.4d-AOSResults.json.xz`. |
| 8.4e/f | Five ordering/orientation and three chart transforms; twenty and twenty-four transformed history cells. Each source evolves natively and each event gets fresh bindings. `P9-8.4e/f-AOSResults.json.xz`. |
| 8.4g | Twelve independent original/allocation-only/companion source/target/role calculations, followed by four native prerequisite steps. The original reset exclusion is retained. `P9-8.4g-AOSResults.json.xz` and the large source/prepared-target records. |
| 8.4h | Actual 107-vertex, 407-edge event; ten target steps per role and final reads. Eight larger covariance events each have one target step per role. Individual `P9-8.4h-AOS-*.json.xz` and `P9-8.4h-AOSCovariance-*.json.xz` records retain inputs, independent equations and comparisons. |
| 8.4i | Exact handoff joins current execution to its own source, event, target and predecessors. Accepted history, newly executed work and acceptance are distinct. |
| 8.5 | Six small lifecycle obligations plus actual large-event replay, three readmissions and both-role independent OS checks. `P9-8.5-AOS-small/large.json.xz`. |
| 8.6/end | Bounded numerical and lifecycle review, explicit exclusions, performance measurements and cache policy. No all-ten or arbitrary-graph promotion. |
| 9.1b | Six mandatory operation-owner tests, including source evolution, mixed replay, reset/rebase and atomic failures. `../tranche-9/P9-9.1b-AOS.json.xz`. |
| 9.2/9.3 | Four independently compared native V3 delegate surfaces; matrix successor has sixteen accepted, four passing pending acceptance, and twenty unselected cells. `../tranche-9/P9-9.2-AOS.json.xz` and `P9-9.3-AOSMatrix.json`. |
| 9.4a/b | Four crossing and five public-facade tests; complete identities, independent initialization, migration, rollback and replay. A_OS basin migration remains refused atomically. |
| 9.5 | Three public legacy-conflict tests; rejected work does not enter successful history or substitute a V4 operation. |
| 9.6 | Exact source/expanded-target identity reconciliation, inherited contract provenance and remaining support limits. Included in the machine-readable review. |

## Larger graph mathematics and performance

The original equal-share fixture has a strictly negative reset-role resource
after its first ordinary target step (approximately `-3.72529e-9`). It is an
excluded fixture, not a successful continuation. The independent oracle retains
that result and the allocation-only control.

The separate companion uses the declared dyadic leading-rate selection to obtain
shares `(1/4, 3/8, 3/8)`. It transfers exactly `1/1024` of source resource to the
smallest-ID farthest vertex (distance eight), in both roles, preserving total
resource and the original distinct W histories. This is a separately identified
fixture, not an alteration of historical evidence or a general admissibility
theorem. The fresh evolved source must still satisfy the strict trigger before
the actual event.

The independent large oracle composes the two OS passes with FLINT/Arb at 192
bits and separately emulates binary64 staging. It bounds the exact-real
predictor-generated geometry, corrector, regenerated split, regularity and
resource signs at each saved input. Native execution uses FLINT and the existing
certified Arb 256-bit numerical policy. It does not reuse CI-root or PC
certificates as A_OS evidence, and does not claim a uniform trajectory enclosure.

Workers use one BLAS thread. The existing exact-content schema memo is scoped
to one worker, bounded to eight entries of four MiB, and discarded on exit.
Matrix reuse is scoped to an operation and keyed by exact operands and numerical
policy. No current, W update, OS pass or authority is cached. Profiling identifies
serialization and validation as the dominant source-step cost. The retained
profile and per-segment times distinguish profiled runs from ordinary runs;
wall times also reflect concurrent load. No changed mathematical law or relaxed
tolerance is needed for the declared companion. Step/final caps are 600 seconds
and event caps 1200 seconds.

The retained baseline target steps took 181.52–352.82 seconds; final reads took
102.08–104.06 seconds. The baseline event took 349.51 seconds. Eight covariance
events took 834.40–1161.72 seconds under concurrent load, with their target steps
taking 104.06–178.40 seconds. All declared caps passed, although the slowest
concurrent event leaves limited headroom; these are observed timings for the
declared workload, not a performance guarantee for arbitrary graphs.

## Integration, source epochs and limits

Production changes register A_OS in the existing enabled owner, native disabled
delegate and public execution selector. The mathematical kernels remain the
existing A_OS implementations. The new tests adapt fixture providers while
executing the real native handlers and independent legacy comparisons.

The source-epoch registry authenticates the earlier four-family executions
against their committed bytes at `02528b5d`; it does not reinterpret those runs
as executions of the new selector. The runtime work manifest and current
maintenance boundary bind the new source, tests and evidence separately.

The four A_OS disabled contracts retain their forensic support disposition
`indeterminate_requires_review`. Runtime comparisons do not promote scientific
authority. Source-profile compatibility does not automatically establish the
four surfaces for a different expanded-target identity. A_OS Tranche 10 basin
support, optional completion/hierarchy, twenty remaining compatibility cells,
umbrella compatibility, G4 and full GRC9V4 conformance remain outside this work.

Development corrections included preserving IEEE negative zero in legacy
evidence with the established compatibility serializer, accepting the native
typed rejection of an empty receipt sequence, and moving lifecycle failure
injection to the publication boundary required by the current concrete-type
transition contract. Small and large numerical policies use separate matrix
cache scopes. Corrected declarations and affected execution records are
regenerated; no accepted record is overwritten.

## Side-tool and reproduction

`/api/aos`, its indexed source endpoint, the A_OS browser table and notebook cell
show the fifth realization and distinguish passing execution from acceptance.
The current next-work guidance follows A_OS; historical four-family Tranche 10
support remains available. Status reads check exact retained hashes without
launching numerical trajectories. A failed refresh clears stale browser and
notebook output.

Use the repository `.venv`, `OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1`, and
`PYTHONPATH=src:.:implementation/phase-9-grcv4/verification`. Execute declared
campaign segments only into absent result paths; producers refuse overwrites.
Existing raw evidence above 1 MB is restored by `scripts/evidence_storage.py`.

```bash
.venv/bin/python scripts/evidence_storage.py restore
.venv/bin/python implementation/phase-9-grcv4/verification/p9_aos_review.py check
.venv/bin/python -m unittest test_p9_aos_review -v
.venv/bin/python implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/scripts/run_phase9_notebook.py --aos-only
```

For a full retained scientific recheck, call `p9_aos_review.build()` under FLINT
and compare its returned record with the saved review. It validates saved
operands and relationships; it does not grant acceptance or rerun native
trajectories. Mutation tests exercise omitted roles, changed histories,
receipt/clock errors, signed transport, source drift and false scope promotion.

## Validation

The [source-bound validation record](../tranche-9/P9-AOS-Validation.json)
retains 22 passing A_OS integration tests, 13 passing retained
scientific/cache tests, 93 existing integration tests, and
13 review/API/browser/notebook tests. The existing suite's
4 skips are abstract base classes; their concrete family suites ran.
All groups have zero failures and errors. The side-tool tests include verified
restoration of the packed A_OS input on a fresh checkout and refusal to
overwrite a changed expanded file. Sixteen storage tests also passed.

The full dashboard additionally exposed an inherited G2 source-bridge gap
following the earlier performance work and Tranches 9–10. Its bounded repair
authenticates seventeen named source epochs and explicitly excludes thirty-nine
later source/test additions from the historical roster. Changed live bytes and
unlisted additions remain rejected. The initializer reader checks the unchanged
accepted package and every original package input at its accepted Git revision,
instead of rebuilding that historical release from today's documentation.
No numerical kernel or accepted execution record changes in this repair.
Eight additional [provenance/package/index tests](../tranche-9/P9-AOS-G2SourceValidation.json)
pass, and the original profile-review consumer passes. Together with the main
validation, this is 149 passing tests, plus the sixteen storage tests.

The G3 and Tranche 8 index readers also resolve the previously registered
document epochs through the exact historical-source lookup, including the
original boundary declaration and mechanical record. All 587 retained
Tranche 8 index references remain byte-identical; changed live documents reject.

The historical overview now authenticates the exact committed projection at
`02528b5d` and all 587 referenced sources on every request, including an end-of-read
content check. This avoids repeated canonical serialization and deep copies of
large historical records. It retains no live-file or successful-validation cache
between requests. A forged projection, source drift or concurrent mutation
rejects; no current-code conformance follows. `tranche8_evidence.py check` and
`checked(rebuild=True)` retain the explicit full reconstruction path.

The authenticated historical overview took 13.49 seconds in the final selected
view check. Two exact metadata-reader successors preserve the earlier Tranche 8
end-review references; their live hashes and original Git bytes are checked,
including existing predecessor epochs. Tranche 9 support and the historical
Tranche 10 support views also passed.
