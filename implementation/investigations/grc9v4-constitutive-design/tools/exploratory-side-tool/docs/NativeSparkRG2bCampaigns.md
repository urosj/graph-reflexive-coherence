# RG2b native completion campaigns

The two campaign views are distinct from the accepted bounded preflight and
pressure records. They expose the actual source beat, D11 expansion, current and
reset target histories, certified positive windows and cold journal replay.
The user accepted both bounded campaigns on 2026-11-03 through the commit
request, recorded in their reviews and the Phase 9 plan/checklist/handoff.
The views preserve the sealed records' original execution-time acceptance flags.
They do not confer aggregate native support; P9-9.1a.7 remains separate.

Python/notebook:

```python
from grcv4_explorer.spark_native_rg2b_campaign import native_rg2b_campaign
native_rg2b_campaign(repo_root, "C_RG2b")
native_rg2b_campaign(repo_root, "A_RG2b")
```

The Phase 9 notebook cell `spark-native-rg2b-campaigns` clears its old value before
loading. The web page has separate C_RG2b and A_RG2b campaign buttons. JSON routes:

- `/api/native-spark/c-rg2b/campaign` and `/campaign/source`
- `/api/native-spark/a-rg2b/campaign` and `/campaign/source`

Each view checks a locally pinned campaign identity and the bound sources and
compact streams. It rejects widened scope, changed data and unrecognized query
parameters. No trajectory is executed by reading the view.

Every compact row retains exact physical state/flux, represented error, finite
chain proof summaries and the full diagnostic hash. Selected full diagnostics
are retained. Independent finite-chain proofs ran on **every** transition during
the campaign; the compact archive does not contain every omitted chain operand.
`--check` verifies identity, connectivity, exact incidence/charge/positivity and
coverage. `--check --numerical-samples` also rechecks the full retained samples.
`--reconstruct --role current --beat 100` explicitly executes the native step
from its saved exact input, requires identical complete diagnostic hash, and
independently rechecks it. Reconstruction is an explicit new numerical execution,
not evidence that an integrity-only check reran the original campaign.

From the repository root, with the existing `.venv`:

```sh
PYTHONPATH=.:src:implementation/phase-9-grcv4/verification .venv/bin/python implementation/phase-9-grcv4/verification/p991a6_rg2b_campaign.py C_RG2b --check
PYTHONPATH=.:src:implementation/phase-9-grcv4/verification .venv/bin/python implementation/phase-9-grcv4/verification/p991a6_rg2b_campaign.py A_RG2b --check --numerical-samples
PYTHONPATH=.:src:implementation/phase-9-grcv4/verification .venv/bin/python implementation/phase-9-grcv4/verification/p991a6_rg2b_campaign.py C_RG2b --reconstruct --role current --beat 100
```

For a new authorized primary campaign, C uses the common runner's
`C_RG2b --profile` / `C_RG2b --run`; A uses
`p991a6_arg2b_campaign.py --profile` / `--run`. The A adapter keeps the
independent C metric exactly rational and bounds only the log-W term with Arb.
The common reader and reconstruction commands above work for both. Primary
files are never silently overwritten.

These are the declared 15-vertex targets at durations 8 and 16. Their geometry
is a derived Lipschitz section, not physical geometry history or a differentiable
section claim. C_RG2b has physical C; A_RG2b has C/W and audits the writer inside
the inverse chain as well as the actual fresh-resource writer. A selected curve
parameter proves membership when its metric bound passes; an unsuccessful
parameter search is not a global impossibility certificate.
