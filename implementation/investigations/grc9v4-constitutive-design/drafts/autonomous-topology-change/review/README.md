# ATC-1 retained independent review

The [review](./ATC1-IndependentReview/ATC1-Review.md), original reproducer,
results, manifest and exact inputs are retained unchanged as readable files.
The input copies identify the reviewed subject even if later research changes
the active documents. They are evidence inputs, not another source of authority.
The [acceptance addendum](../../../decisions/ATC1Acceptance.md) records the
user's decision, separate opening/reconstruction review and scope limits.

To rerun the eleven independent groups from the repository root without
overwriting the retained result, use the original script's read-only function:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python - <<'PY'
import json, runpy
from pathlib import Path
review = Path('implementation/investigations/grc9v4-constitutive-design/drafts/autonomous-topology-change/review/ATC1-IndependentReview')
checks = runpy.run_path(str(review / 'pressure_checks.py'), run_name='review_readonly')
result = checks['run'](review / 'inputs')
retained = json.loads((review / 'pressure_results.json').read_text())
assert json.loads(json.dumps(result['results'])) == retained['results']
print(json.dumps(result, indent=2))
PY
```

This prints a fresh result; it does not reproduce native ATC execution or
replace the original review's environment and input identities. The CLI
example inside the frozen review writes its output path; do not point that
example at the retained result when reproducing it here.
