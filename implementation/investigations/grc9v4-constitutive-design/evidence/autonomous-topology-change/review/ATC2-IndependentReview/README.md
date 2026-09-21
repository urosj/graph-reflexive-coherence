> Relocation-only maintenance: repository paths and dependent identities were
> rebuilt before first commit. Scientific statements, numerical results and
> review verdicts are unchanged; the new identities are not an independent
> reviewer rerun. Earlier byte-preservation statements describe the pre-move stage.

# ATC-2 independent review and correction

The [original review](./ATC2-IndependentReview.md) and
[original result](./pressure_results.json) report thirteen passing independent
groups, with data-only constructor shims, not a native runtime rerun.
The [subsequent correction](./ReviewCorrection.md) preserves those bounded
results but makes the missing generic capabilities outstanding requirements.
Neither is user acceptance or authority to finalize an incomplete extension.

The five files under `inputs/` are exact reviewed research subjects: proposal
text, proposal record, pressure record, verifier and origin index. Their hashes
are bound by the reviewed records. Unused copies of eight production modules
are omitted, as described below. The Markdown snapshot keeps its original
relative-link context; use the [original-location proposal](../../../../decisions/ATC2CandidateClosureProposal.md)
for navigable links rather than rewriting its reviewed bytes. Production copies
are omitted: the checker never imports them, and the live repository already
contains those subjects. Consequently a fresh checker reports **one**, not
eight, byte-matched execution source in this compact input directory. The
historical result's eight matches describe the reviewer's original input set;
they are not rewritten into native execution evidence.

The retained checker has only portable execution-envelope adjustments:
explicit input/output arguments, refusal to overwrite an existing output
directory, and an accurate compact-input availability note. Its numerical
checks and AST-extracted research functions are unchanged.

To reproduce without writing files or overwriting the historical result, from
repository root (repository Python and Node.js on PATH):

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python - <<'PY'
import contextlib, io, json, runpy
from pathlib import Path
review = Path('implementation/investigations/grc9v4-constitutive-design/evidence/autonomous-topology-change/review/ATC2-IndependentReview')
captured = {}
class Output:
    def __init__(self, name=''): self.name = name
    def __truediv__(self, name): return Output(name)
    def write_text(self, text): captured[self.name] = text
checks = runpy.run_path(str(review / 'independent_checks.py'), run_name='review_readonly')
with contextlib.redirect_stdout(io.StringIO()):
    checks['main'](review / 'inputs', Output())
fresh = json.loads(captured['pressure_results.json'])
original = json.loads((review / 'pressure_results.json').read_text())
expected = original['groups'].copy()
expected['record_bindings'] = dict(expected['record_bindings'], byte_matched_execution_sources=1)
assert fresh['groups'] == expected
assert fresh['status'] == 'passed' and fresh['native_pygrc_executed'] is False
print('PASS: 13 independent groups; compact-input availability difference only; no native rerun')
PY
```

Use this review as evidence for bounded adjudication, together with the
[capability-closure continuation](../../../../decisions/ATCCapabilityClosureContinuation.md).
The correction controls the forward completion recommendation. The original
research artifacts, claimed native runs and accepted predecessor remain
unchanged. No source or output requires a machine-local attachment directory.
