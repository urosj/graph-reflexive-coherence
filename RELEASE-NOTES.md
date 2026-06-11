# Release Notes

## First public GitHub snapshot - 2026-06-11

This snapshot publishes `graph-reflexive-coherence` as a source-installable
research repository for graph-native Reflexive Coherence work. It is not a
tagged package release and not a black-box product API.

### Scope

- Runnable `pygrc` source package for `GRCV2`, `GRCV3`, `GRC9`, `GRC9V3`, and
  `LGRC9V3` model-family surfaces.
- Graph/LGRC papers, implementation phase records, specs, reference guides,
  examples, tests, and experiment evidence lanes.
- Quickstart path that lowers a landscape-authored `GRCL9V3` seed into
  `GRC9V3`, runs one step, captures telemetry, and renders graph visuals.
- Historical experiment lanes under `experiments/`, including the N05-N11 LGRC
  agentic-like foundation arc with explicit claim ceilings and non-claims.

### Installation

Install from a repository checkout:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

The package metadata remains at `version = "0.1"` for this snapshot.

### Verification

The publication pass verified:

- clean virtual-environment installation from `requirements-dev.txt`;
- `python -m pip check`;
- `python -m unittest discover -s tests -p 'test_*.py'`;
- `tests.smoke.test_quickstart`;
- quickstart telemetry and visual artifact generation;
- README and experiment-index local links;
- experiment-local output audit for machine-local absolute paths.

### Boundaries

- Public imports should prefer package facades documented in `README.md` and
  `pygrc.PUBLIC_API_SURFACES`.
- Deep implementation imports remain research-workspace details unless used by
  examples, specs, or reference guides.
- Positive claims are bounded by papers, specs, tests, telemetry, reports,
  committed artifacts, and explicit claim ceilings.
- Agency, biological identity, personhood, and general-intelligence claims are
  out of scope for this snapshot.
