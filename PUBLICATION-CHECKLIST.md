# Publication Checklist

This checklist tracks the remaining work to make the repository ready for a
public GitHub publication pass. It is intentionally finite: once the repository
is published, close out completed items and move recurring practices into
maintainer documentation instead of letting this become a general TODO file.

## README

- [x] Add a sharper one-line pitch near the top.
- [x] Add a short status and maturity note near the top.
- [x] Add a theory and implementation map near the top.
- [x] Convert "Current runnable surfaces" into a scannable table.
- [x] Add a real inline minimal example copied from a working public API path.
- [x] Add a simple architecture diagram that reflects actual repository flow.
- [x] Add a quickstart visual only after regenerating it from the documented
      quickstart command and storing the tracked copy under `docs/assets/`.

## Reproducibility

- [x] Regenerate quickstart output from the documented command in the current
      workspace and confirm telemetry and visual files are produced.
- [x] Verify the documented quickstart from a clean virtual environment.
- [x] Add a quickstart smoke check that asserts the expected telemetry and
      visual output files are produced.
- [x] Add a claim-to-evidence table linking major claims to papers, specs,
      tests, scripts, and committed artifacts.
- [x] Document the expected reconstruction path for historical experiment
      lanes that are intended to remain public evidence.

## CI

Deferred for this publication pass. Add these after the repository is public and
the default branch, runner expectations, and first external workflow are clear.

- [ ] Add a GitHub Actions workflow for installation and unit tests.
- [ ] Add CI checks for `ruff` and `mypy`.
- [ ] Add a CI job or targeted smoke step for the quickstart example.
- [ ] Add README badges only after the corresponding CI checks exist: test
      suite status, `ruff`, `mypy`, Python version, and license.

## Artifacts

- [x] Confirm top-level scratch outputs remain ignored and curated top-level
      evidence exceptions are documented.
- [x] Confirm committed experiment-local outputs contain relative paths only
      across current experiment output candidates.
- [x] Document the artifact policy as a short README table.
- [x] Keep generated README screenshots or GIFs in a tracked documentation
      asset directory, not under ignored scratch output paths.

## Packaging

- [x] Decide whether `pygrc` is only source-installable for now or should have
      a tagged package release path: source-installable only for this
      publication pass.
- [x] State which import paths are intended public API surfaces.
- [x] Confirm dependency metadata in `pyproject.toml` matches the documented
      quickstart and test commands.
- [x] Add release notes for the first public GitHub snapshot.

## Known Gaps Accepted For This Publication Pass

- No tagged PyPI release; `pygrc` is source-installable only.
- No CI workflows yet; test, lint, and type-check commands are manual.
- No issue or pull request templates yet.
- GitHub repository metadata is deferred until the public repository exists.
- `pygrc.discovery` and `pygrc.cli` are importable research/tooling surfaces,
  not documented public API facades.
- [RELEASE-NOTES.md](RELEASE-NOTES.md) is the source of truth for first
  snapshot scope and verification; this checklist records publication closure
  evidence.

## GitHub Metadata

Deferred until the repository exists on GitHub and publication metadata can be
set against the actual public repository.

- [ ] Add repository description and topics after publication.
- [ ] Add issue templates for bug reports and reproducibility failures.
- [ ] Add a pull request template focused on scope, tests, and artifacts.
- [ ] Add a social preview image if the quickstart visual is strong enough.

## Final Pre-Publication Pass

- [x] Review `git status --short` before the first commit to avoid committing
      local virtual environments, caches, or scratch output.
  - `git status --short --ignored` shows `.venv/`, `__pycache__/`,
    `src/pygrc.egg-info/`, and generated quickstart scratch outputs under
    `outputs/examples/` are ignored.
  - The visible top-level `outputs/` entry comes from intentionally unignored
    `outputs/grc9v3/...` evidence artifacts listed in `.gitignore`.
- [x] Search for machine-local absolute paths in committed text artifacts.
  - Experiment-local output audit scanned 905 files, including 842
    text/structured files, for `/home/`, `/tmp/`, `/mnt/`, `/Users/`, Windows
    drive paths, and `file://`; no violations were found.
  - Structured JSON/JSONL/CSV/MD/TXT parsing found
    `absolute_path_violations=0`, and no symlinks were present under
    experiment outputs.
- [x] Run the full test suite or record any known test gaps in the publication
      notes.
  - Clean virtual-environment publication pass completed
    `python -m unittest discover -s tests -p 'test_*.py'`: 1135 tests passed.
  - `tests.smoke.test_quickstart` and `python -m pip check` also passed after
    source-install metadata refresh.
- [x] Confirm license and citation wording match the code, papers, and
      narrative documentation.
  - Code/package metadata points to GPL-2.0-only through `LICENSE` and
    `pyproject.toml`.
  - `papers/` contains imported theory papers that declare CC BY-SA 4.0 in
    their headers.
  - README and `CITATION.cff` now state the mixed-license split: `papers/` are
    CC BY-SA 4.0; all other repository content is GPL-2.0-only unless a file
    states otherwise.

## Post-Publication

- [ ] Monitor first issues for broken links, environment mismatches, and
      reproducibility failures.
- [ ] Add CI badges to README once workflows are green.
- [ ] Update `CITATION.cff` with DOI or archive metadata if assigned.
- [ ] Archive this checklist or move durable process notes into
      `implementation/` once the publication pass is closed.
