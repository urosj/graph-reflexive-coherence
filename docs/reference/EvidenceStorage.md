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

From 2026-10-12, **compress every new or changed uncompressed file larger
than 1,000,000 bytes (decimal 1 MB)**, including the current C_CI run.
Compressed files may exceed 1 MB, even if compression does not reduce their
size. This replaces the former 10 MB Git-file cap; it is a compression
threshold, not an archive-size ceiling. Unchanged historical files are not
retroactively migrated, and Git history is not rewritten.

The packer accepts any file type and produces byte-exact `.xz` storage.
The staged-file gate also recognizes valid XZ, gzip, bzip2 and ZIP containers;
renaming an uncompressed file to an archive extension does not exempt it.
Manifest v2 records `compression_threshold_bytes`; v3 adds shared object stores.
The reader remains compatible with historical v1/v2 manifests.

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

### Shared objects for new C_RG2b evidence

The connected C_RG2b continuation stores 67 large records in one compressed,
content-addressed object store. Their original **358,312,645 JSON bytes** and
**28,298,336 XZ bytes** are reconstructible from the
[store and manifest](../../implementation/phase-9-grcv4/tranche-8/crg2b-native/shared/).
The shared archive plus manifest is **10,891,472 bytes**, 61.5% smaller than
the separate archives. Identical JSON subobjects are stored once; recipes preserve literal bytes,
including number spellings, signed zero, key order and the trailing newline.
The writer refuses any input it cannot round-trip exactly. No scientific
record, claim, native producer or original JSON/XZ SHA256 is changed.

Git contains `shared/records.json` and `shared/objects.zip.xz`, not a second
copy of those 67 original archives. Their `.json` and `.json.xz` paths are
ignored local caches. Smaller unregistered evidence keeps its existing storage.
The shared ZIP uses uncompressed content-addressed members inside a single XZ
stream so compression can also exploit repetition across objects.

From a fresh checkout, restore just this campaign before using its frozen
standalone readers:

```sh
.venv/bin/python scripts/evidence_storage.py restore --archives-only --prefix implementation/phase-9-grcv4/tranche-8/crg2b-native/
.venv/bin/python scripts/evidence_storage.py verify --prefix implementation/phase-9-grcv4/tranche-8/crg2b-native/
```

Omit `--archives-only` to restore expanded JSON too. The C_RG2b side-tool and
current phase-boundary check perform the necessary restoration automatically.
The shared archive, object hashes, reconstructed record sizes/hashes and original
transport hashes are checked. Edited local copies are rejected, never overwritten.
Restoration and verification execute no numerical solver. Legacy consumers still
parse the reconstructed originals; reduced parsing time is not claimed.

**Transport compatibility:** JSON reconstruction assembles stored byte fragments
and is independent of the XZ encoder. Reconstructing the original transport SHA
uses stdlib liblzma, XZ/CRC64, preset 6. If another encoder version emits different
bytes, restoration fails explicitly rather than silently changing the transport
identity. The exact JSON remains reconstructible through `Store.raw`; the frozen
legacy checker then needs an encoder reproducing the pinned XZ bytes. The store
does not require any original machine-local paths or external data service.

For future explicit, uncommitted selections, use `deduplicate <logical paths...>
--store-directory <repo-relative directory>` after `pack`. The tool checks every
original JSON and XZ round trip before registering the shared store, retains all
original manifest rows, and ignores the reconstructed transport paths. It refuses
already tracked evidence or repeat migration. This is storage maintenance, not
a new execution or acceptance campaign.

### Ordinary packing

```bash
python scripts/evidence_storage.py pack path/to/new-large-result.json
git rm --cached -- path/to/previously-tracked-large-result.json
git add artifact-storage.json .gitignore path/to/new-large-result.json.xz
python scripts/evidence_storage.py check
```

Use `git rm --cached` only for raw files already tracked; it keeps the local
copy. The pack command refuses to rewrite a registered scientific subject and
allows archives above 1 MB. A new run should use a new subject
path. Refresh current phase/storage bindings when the storage roster changes.

`check` verifies the archives and checks **new/changed staged Git blobs against
HEAD**, so replacing a large work file with a small one cannot hide an
uncompressed oversized staged blob. Unchanged historical blobs are exempt. The
local checks below are required before committing or publishing. This is a
storage limit, not a substitute for deciding whether the data deserves retention.

## Local checks for Tranche 8 and later work

Use this process for every tranche that adds or changes retained evidence.
Before a campaign, apply the retention rules above and identify which checker
consumes each retained operand. Publish completed results only. Minimize
repeated data and use the packing steps above for justified raw files over 1 MB.
Refresh the applicable phase bindings after changing storage or documentation.

After staging the intended changes, run these checks from the repository root:

```bash
python -m unittest tests.test_evidence_storage tests.test_evidence_dedup -q
python scripts/evidence_storage.py check
git diff --cached --check
```

Use the repository's `.venv/bin/python` where available. The first command
checks storage behavior, including corruption rejection and the staged-blob
limit. The second verifies registered archives and their exact restored bytes,
then enforces the 1,000,000-byte compression threshold for new/changed staged
raw blobs, allowing valid compressed files to be larger. Run it
again after changing the staged contents. Scientific checks remain those
required by the affected realization and claim; storage checks do not replace
them. Verify restoration from a fresh directory when introducing a new archive.

On 2026-10-07 the user requested that `/.github/` be ignored for now. These
local commands preserve the evidence-storage process independently of GitHub
configuration. The workflow introduced on the expansion branch was subsequently
removed from Git tracking because the push token lacks GitHub's `workflow`
scope. An ignored local `.github/workflows/artifact-size.yml` copy may remain,
but fresh checkouts use the commands above without depending on that file.
The temporary policy is to run these checks locally; no GitHub automation is
claimed. Future workflow configuration can use the same commands when workflow
publication is enabled.

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
