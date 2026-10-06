# Evidence value, retention and storage

Large files are not stronger evidence. The useful result is a bounded claim
supported by a reproducible check, with a clear failure condition. A count of
certificates, controls or passing checks is not a count of independent proofs.

## What the current records contribute

- The mathematical construction and its declared hypotheses justify the
  bounds. A finite numerical run cannot replace that argument or establish
  arbitrary-graph, all-time or unreviewed parameter claims.
- Independent residual/error checks can validate a saved native solver proposal
  without trusting or rerunning that solver. For C_RG2b, the inverse-chain
  operands are consumed by `chain`, `level_residuals`, `truth` and
  `check_read(..., numerics=True)` in
  [the retained checker](../../implementation/phase-9-grcv4/verification/p984b_crg2b_runtime.py).
  The [A_RG2b checker](../../implementation/phase-9-grcv4/verification/p984b_arg2b_runtime.py)
  additionally checks scaled-log history, writer operands and the next read.
  The mutation tests check that meaningful corruption is rejected.
- A recheck using the same independent checker is repeatability/integrity work,
  not another independently designed mathematical audit. Hashes authenticate
  the subject; they do not establish scientific correctness.
- Coverage and acceptance records prevent dropped cases and overstated scope.
  They do not turn a bounded pass into a general result.

The C_RG2b completed result is 49.10 MB. About 43.19 MB is continuation data
with repeated full states, reads and certificates. Its numerical payload is
useful to the independent checker, but the schema is expensive and redundant.
Suspended/incomplete run dumps and their tracking records are not retained.

## Retention rule for subsequent work

Keep a short claim/review, frozen inputs, reproducible commands, meaningful
tests, worst bounds and completed coverage as the primary review
material. Retain a large trace only when a named consumer needs its original
operands, rerunning is costly, or it captures a failure that cannot be recreated
reliably. State that reason before a long campaign.

Store shared inputs and identical states once in future formats; reference them
from observations. Keep progress/checkpoints in ignored working data during a
run. Discard suspended/incomplete runs and their tracking records; neither is
required for publication or acceptance. Final evidence must validate without
restoring those files. Reproducible negative tests can document correctness
boundaries without archiving incomplete execution dumps.

Use routine tests and integrity checks for ordinary maintenance. Repeat costly
numerical work when relevant code, oracle, inputs, hypotheses or claims change,
or when investigating a concrete failure. A documentation or byte-exact storage
change alone does not require rerunning native trajectories or interval math.

## Lossless migration

The initial migration stored twelve files over **10,000,000 bytes** as adjacent `.xz` archives.
Their combined payload falls from **389,208,550 to 9,838,636 bytes** (97.47%
smaller); the largest archive is 1,314,672 bytes. C_RG2b's final result falls
from **49,102,617 to 1,242,592 bytes**; the exact size and both SHA256
identities are recorded in the [storage manifest](../../artifact-storage.json).

A_RG2b adds a completed **46,110,769-byte** result stored in **1,680,576 bytes**.
Its compact step schema reconstructs unchanged context and keeps C/W poststates
plus the chains actually consumed by the independent checker. The current
thirteen-file total is **435,319,319 bytes expanded, 11,519,212 bytes stored**;
the largest individual archive is 1,680,576 bytes. No interrupted A run is
part of the evidence set.

The archives preserve the original bytes, including serialization and record
digests. Frozen scientific source and input bindings are unchanged.
The eleven existing subjects are byte-exact storage changes. C_RG2b first
omits administrative recovery/checkpoint metadata from its completed result
and recheck, resealing outer identities and cross-links; its scientific fields
and per-case check identities are unchanged. Neither operation grants acceptance
or implies new scientific validation. Historical Git objects remain in history. This migration reduces
the current and future committed file tree, not past Git history.

Historical reports continue to name logical `.json`/`.jsonl` paths. Those paths
are reconstructed locally and excluded from Git. On GitHub, use the archive
links below; existing historical logical JSON links require local restoration.
The current Phase 9 audit and Tranche 8 CLI/API/browser index restore missing
files automatically. Other standalone historical readers use this explicit
setup step, with no third-party Python dependency:

```bash
python scripts/evidence_storage.py restore
python scripts/evidence_storage.py verify
```

Restoration authenticates compressed and original bytes, writes missing files
atomically, and refuses to overwrite changed local data. `verify` also decodes
every archive and checks the exact original hash and byte count. Nothing executes
a numerical solver. Expanded copies can be regenerated from a fresh checkout;
they must not be added back to Git.

## Before committing or publishing

```bash
python scripts/evidence_storage.py pack path/to/new-large-result.json
git rm --cached -- path/to/previously-tracked-large-result.json
git add artifact-storage.json .gitignore path/to/new-large-result.json.xz
python scripts/evidence_storage.py check
```

Use `git rm --cached` only for raw files already tracked; it keeps the local
copy. The pack command refuses to rewrite a registered scientific subject and
rejects an archive that still exceeds 10 MB. A new run should use a new subject
path. Refresh current phase/storage bindings when the storage roster changes.

`check` verifies the archives and checks **staged Git blob sizes**, so replacing
a large work file with a small one cannot hide an oversized staged blob. The
same check runs in the repository's GitHub workflow. This is a storage limit,
not a substitute for deciding whether the data deserves retention.

## Archive index

The machine-readable manifest records exact original/stored sizes and SHA256s.

| Archive | Original MB | Stored MB |
| --- | ---: | ---: |
| [complete_step_jacobians.json.xz](../../experiments/2026-08-B1-GR-grc9v3-continuation-readback-verification/outputs/complete_step_jacobians.json.xz) | 12.11 | 0.099 |
| [conductance_retention_probe.json.xz](../../experiments/2026-08-B1-GR-grc9v3-continuation-readback-verification/outputs/conductance_retention_probe.json.xz) | 54.11 | 0.572 |
| [return_orbit_registry.json.xz](../../experiments/2026-08-B1-GR-grc9v3-continuation-readback-verification/outputs/return_orbit_registry.json.xz) | 13.24 | 0.360 |
| [P9-8.4b-ACIPCResults.json.xz](../../implementation/phase-9-grcv4/tranche-8/P9-8.4b-ACIPCResults.json.xz) | 31.81 | 1.100 |
| [P9-8.4b-ACIResults.json.xz](../../implementation/phase-9-grcv4/tranche-8/P9-8.4b-ACIResults.json.xz) | 28.70 | 1.215 |
| [P9-8.4b-AOSResults.json.xz](../../implementation/phase-9-grcv4/tranche-8/P9-8.4b-AOSResults.json.xz) | 39.02 | 1.315 |
| [P9-8.4b-APCResults.json.xz](../../implementation/phase-9-grcv4/tranche-8/P9-8.4b-APCResults.json.xz) | 19.19 | 0.611 |
| [P9-8.4b-CCICompletionResults.json.xz](../../implementation/phase-9-grcv4/tranche-8/P9-8.4b-CCICompletionResults.json.xz) | 50.38 | 1.183 |
| [P9-8.4b-CCIPCResults.json.xz](../../implementation/phase-9-grcv4/tranche-8/P9-8.4b-CCIPCResults.json.xz) | 42.96 | 0.912 |
| [P9-8.4b-CCIResults.json.xz](../../implementation/phase-9-grcv4/tranche-8/P9-8.4b-CCIResults.json.xz) | 25.05 | 0.732 |
| [P9-8.4b-CPCResults.json.xz](../../implementation/phase-9-grcv4/tranche-8/P9-8.4b-CPCResults.json.xz) | 23.55 | 0.497 |
| [P9-8.4b-CRG2bResults.json.xz](../../implementation/phase-9-grcv4/tranche-8/P9-8.4b-CRG2bResults.json.xz) | 49.10 | 1.243 |
| [P9-8.4b-ARG2bResults.json.xz](../../implementation/phase-9-grcv4/tranche-8/P9-8.4b-ARG2bResults.json.xz) | 46.11 | 1.681 |
