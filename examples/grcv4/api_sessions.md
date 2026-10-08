# Debugging, migration and restoration sessions

[api_sessions.py](api_sessions.py) turns the API notes' inline experiments into
six reproducible checkout examples. It uses the existing four-node, three-edge
branch declarations from [compare_five.py](compare_five.py). The strong-signal
two-node debug snippets are represented by the same workflow on this shared
branch, so their numerical values are not copied as expected outputs.

Run from the repository root with the existing V4/FLINT environment:

```bash
.venv/bin/python examples/grcv4/api_sessions.py --list
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python examples/grcv4/api_sessions.py --scenario debug
.venv/bin/python examples/grcv4/api_sessions.py --scenario migration-cycle
.venv/bin/python examples/grcv4/api_sessions.py --scenario os-excursion --steps 1
.venv/bin/python examples/grcv4/api_sessions.py --scenario carrier-excursion --steps 1
.venv/bin/python examples/grcv4/api_sessions.py --scenario carrier-excursion --steps 5
.venv/bin/python examples/grcv4/api_sessions.py --scenario carrier-excursion --steps 10
.venv/bin/python examples/grcv4/api_sessions.py --scenario admission-gates
.venv/bin/python examples/grcv4/api_sessions.py --scenario lifecycle
```

`--scenario all` runs each scenario once, using `--steps` for both excursions
(default 5). Imports are resolved relative to the checkout; no private notes
path, installation of the checkout as a package, or working data from another
machine is needed. Declaration construction follows the existing test-fixture
convention; production classes perform all numerical work.

## Choose a session

| Scenario | What it demonstrates | API layer |
| --- | --- | --- |
| `debug` | Three-step immutable trace for A_CI and C_CI+PC; inspect step 1, transfer 0.05 from node index 1 to 0, compare the next state/read, reject an unbalanced edit, no-op identity, discard fork and reproduce the original successor. | Pure numerical records and provisional steps. |
| `migration-cycle` | A_CI → A_PC → A_OS → A_CI; exact current/reset W transport, zero-initialized Z, explicit Z loss, one physical step per hop, matched three-step CI baseline, wrong-policy rejection, legal identity migration. | Pure migration maps followed by actual target numerical steps. |
| `os-excursion` | Three CI warmup steps; edit and advance two branches in lockstep, one under CI and one under OS; migrate back, continue and compare all read fields. | Pure map/step experiment; agreement is measured. |
| `carrier-excursion` | The same experiment under CI+PC for 1, 5, 10 or another explicit positive number of steps; compare migration back with staying in CI+PC; independently check the ZOH carrier write. | Pure map/step experiment; exposes history loss versus persistent trajectory changes. |
| `admission-gates` | A_OS and C_RG2b from their matched initial resource arrays: a small conserving edit, an unbalanced charge edit, and a larger conserving edit outside the RG resource box. | Production numerical admission; prints typed failure stage/code and exact RG resource margins. |
| `lifecycle` | Actual `GRCV4.step_v4_input`, `migrate_profile`, `snapshot`, `save`, `load`, `duplicate`, `reset`, and profile discovery; verifies receipts, rejected-operation rollback and deterministic continuation from a saved snapshot. | Public lifecycle with real transactions and publication. |

The first five scenarios do **not** call a pure mapping function a committed
transaction. `map_migration` authenticates the current/reset history map but
performs neither a physical beat nor full target readmission. Their following
production step admits and executes the mapped current state. The public
`lifecycle` scenario additionally owns both-role target readmission, receipts,
publication and restoration. It exports actual migration requests/results and
a complete snapshot; it uses no private owner attributes.

There is no public GRC9V4 façade yet. At the user's direction, GRC9V4
counterparts are deferred rather than presenting internal event owners as that
API. These examples add no runtime support, profile registration, topology
expansion evidence or Tranche 8 coverage credit.

## Inspect without repeating the experiment

Each pure step captures its selected read and writer diagnostics once. The
inspector reads that saved record. CI, PC and RG2b continuation diagnostics reuse
the production step's existing final readmission; OS continuation is `null`
when no such read was captured. No missing diagnostic is replaced with zero.
Re-execution occurs only for an explicit replay control or a new scenario.
The shared declaration builder is reused within one session; there is no
persistent numerical-result or admission cache.

Full JSON includes declarations and A differential-reference payloads, exact
state digests, C/W/Z and reset states, J/J0/read-back/causal-flat/potential/H/source,
A read and writer targets, C structural Hodge/mobility/selector diagnostics,
solver or section diagnostics, field deltas, and typed rejection outcomes.
Declarations are labeled separately from executed coverage. The graph positions
used by generic A are the existing differential backend, not native fixed rows.

```bash
.venv/bin/python examples/grcv4/api_sessions.py --scenario carrier-excursion --steps 10 --output outputs/grcv4-sessions/carrier-10.json
.venv/bin/python examples/grcv4/api_sessions.py --render-from outputs/grcv4-sessions/carrier-10.json
.venv/bin/python examples/grcv4/api_sessions.py --render-from outputs/grcv4-sessions/carrier-10.json --json
```

`--output` creates a new file and refuses to overwrite an existing one. Progress
goes to stderr; `--json` writes JSON to stdout. `--render-from` only formats saved
observations; it neither reruns nor authenticates them as scientific acceptance.
Reports are optional local outputs; large redundant traces are not committed.
For intentional retention, apply the repository's
[evidence/storage rules](../../docs/reference/EvidenceStorage.md).

## Interpretation and corrections to the exploratory notes

- **Compare the same physical horizon.** Migration does not advance time. The
  three-hop cycle is compared with three baseline steps, correcting the notes'
  four-versus-three comparison. The comparator refuses unequal step/time pairs.
- **OS is not generally CI.** OS performs its prescribed predictor/corrector
  pass and split-defect test; CI solves to its joint-root criterion. The default
  one-step A excursion happened to give identical retained values in the checked
  run. Different inputs, gains, tolerances or additional CI iterations can
  differ or reject. No general fixed-point equivalence is asserted. A gain sweep
  would need newly admitted declarations and is not disguised as a run-time edit.
- **A zero carrier does not universally make CI+PC identical to CI.** The
  supplied one-step comparison observed identical C/W after migration back.
  This is a result for these admitted inputs and solver settings, not a theorem
  for all profiles. With ten carrier steps the checked run observed C difference
  about `1.22e-12` and W difference about `1.09e-15` before returning. Such tiny
  binary64 differences are not automatically separation certified beyond solver
  error. Full values and comparison stages, rather than rounded printouts, are
  available in JSON.
- **Migration back is a forward map with a declared loss channel.** It preserves
  evolved C/W and drops Z when leaving PC. It does not undo previous physical
  steps. Snapshot restoration returns a full prior publication. `reset()` instead
  restores the owner's declared reset baseline; it is not arbitrary trace
  navigation. Replaying the same request from an identical snapshot checks
  deterministic continuation, including receipts and lifecycle identity.
- **Identity migration is legal.** The rejection control deliberately supplies
  a history policy bound to the wrong hop. It does not label an accepted
  same-profile identity map a failure.
- **Candidate and realization comparisons are distinct.** A_OS versus C_RG2b
  changes the candidate law and parameters too; its differences cannot be
  attributed solely to OS versus RG2b. C has no W history, and an absent Z is
  different from a present zero matrix. Scientific identities include profiles;
  lifecycle identities also distinguish transaction history.

The checks are executable teaching examples, not a replacement for the retained
mathematical reviews. Run focused helper/CLI pressure without repeating all
numerical sessions:

```bash
.venv/bin/python -m unittest examples.grcv4.test_api_sessions -v
```
