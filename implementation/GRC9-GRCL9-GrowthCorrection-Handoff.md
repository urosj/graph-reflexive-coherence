# GRC9 / GRCL-9 Growth Correction Handoff

Status: completed

This handoff closes the post-closeout correction that separated historical
`legacy_any_inactive_port` broad growth from paper-facing
`grc9_front_capacity` growth.

## Boundary

The GRC9 paper-facing rule is now:

- the Section 8.4 birth probability remains probabilistic,
- the created child attaches to the lowest-indexed inactive parent port,
- and paper-facing parent eligibility requires explicit front-capacity
  provenance created by spark/refinement or authored as a bounded preexisting
  front.

Historical broad inactive-port growth is still reproducible, but only through
guarded diagnostic paths. It is not accepted evidence for corrected GRC9 or
GRCL-9 growth claims.

## Accepted Evidence

Corrected evidence is recorded in:

- `outputs/grc9/phenomenology_discovery/sessions/S0035/corrected_grc9_growth_catalog.json`
- `outputs/grcl9/lowering/sessions/S0036/corrected_grcl9_growth_catalog.json`
- `outputs/grcl9/lowering/sessions/S0037/growth_correction_supersession_summary.json`

Summary counts from `S0037`:

- retained non-growth records: 28
- superseded broad-growth records: 19
- accepted corrected growth records: 30
- accepted corrected controls: 10
- rejected corrected records: 0
- accepted legacy broad-growth records: 0

The only unresolved superseded records are the early GRCL-9 growth-pressure
probes:

- `grcl9_lowered_s0006_growth_pressure_lambda_high`
- `grcl9_lowered_s0006_growth_pressure_lambda_low`

They remain superseded and replayable, but have no direct one-to-one corrected
catalog replacement.

## Guarded Legacy Replay

Legacy broad-growth replay now requires `--force-legacy-growth` on replay-only
or diagnostic paths:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9_replay --session-id S0032 --source-mode legacy_growth_landscape_seed_examples --force-legacy-growth --requested-steps 3
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9_selector_validation --session-id S0033 --source-session-id S0031 --source-session-id S0032 --force-legacy-growth
PYTHONPATH=src ./.venv/bin/python -m pygrc.visualization.grcl9_lowering --session-root outputs/grcl9/lowering/sessions/S0032 --force-legacy-growth
```

The old reviewed GRCL-9 catalog builder also refuses legacy broad-growth
sessions by default. Supplying `--force-legacy-growth` rebuilds only historical
diagnostic artifacts; it does not create corrected evidence.

## Replacement Commands

Corrected catalog and migration commands:

```bash
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grc9_grcl9_growth_record_classification --session-id S0034
PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_corrected_growth_catalog --session-id S0035
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grcl9_corrected_growth_catalog --session-id S0036
PYTHONPATH=src ./.venv/bin/python -m pygrc.telemetry.grc9_grcl9_growth_supersession_summary --session-id S0037
```

## Non-Claims

This correction does not add:

- GRCV3 hierarchy semantics,
- GRCL-9 execution semantics,
- native GRC9 collapse events,
- observer-local semantics,
- Lorentzian causal structure,
- barrier or ghost boundary runtime.

It only corrects growth parent eligibility, telemetry provenance, source
semantics, replay guards, and reviewed growth catalog acceptance.
