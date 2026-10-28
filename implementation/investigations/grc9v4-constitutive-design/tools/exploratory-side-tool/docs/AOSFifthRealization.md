# A_OS fifth-realization evidence

The current work returns from P9-10.1 to A_OS, from P9-8.4d through the end of
Tranche 9. Its earlier P9-8.4b/c evidence is already accepted. The new bounded
implementation and user acceptance are reported separately.

From the repository root, start the existing read-only side-tool:

```bash
.venv/bin/python implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/scripts/serve_phase9.py
```

Open `http://127.0.0.1:4174` and use the first **A_OS** panel. It shows all sixteen
checkpoints, evidence counts, the original large reset exclusion, and indexed
source downloads. The accepted four-family Tranche 10 views remain historical;
P9-10.2 is deferred for this branch.

The matching endpoints are `GET /api/aos` and
`GET /api/aos/source?path=<indexed repository path>`. No family selector or
arbitrary file access is accepted. Source drift fails the check. Status reads
authenticate retained source/result bytes without starting solvers.

The notebook's `query-aos` cell calls the same Python view:

```python
from grcv4_explorer.aos import aos_status
status = aos_status(repo_root)
```

Execute just that notebook query from the repository root with:

```bash
.venv/bin/python implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/scripts/run_phase9_notebook.py --aos-only
```

The compatibility matrix distinguishes sixteen accepted cells, four new A_OS
cells pending acceptance, and twenty unselected cells. The larger graph view
distinguishes four prerequisite steps, one baseline event with twenty target
steps, and eight covariance events with sixteen target steps. Successful
execution is bounded to these exact subjects; it does not establish A_OS basin
support, optional completion, umbrella compatibility or full GRC9V4 conformance.
