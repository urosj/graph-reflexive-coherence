# N04 Lane E Hybrid LGRC Pulse-Substrate Surface Probe

Command:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_hybrid_lgrc_pulse_substrate_surface_probe.py
```

Status: `passed`
Claim ceiling: `hybrid_lgrc_causal_pulse_substrate_surface_contract_supported`

## Native LGRC Input

- Budget surface: `node_plus_packet`
- Native contact count: `13`
- Native self-rearm evidence: `True`
- Native D2.3 equivalent: `True`
- Final native budget error: `0.0`

## Hybrid Surface Driver

- Surface budget: `node_only`
- Surface displacement: `12`
- Width preserved: `True`
- Max surface budget error: `0.0`
- Feedback eligible windows: `10`
- Feedback regeneration candidate: `True`

## Interpretation

Lane E supports the hybrid causal pulse-substrate surface contract:
existing native LGRC9V3 E3 pulse-contact artifacts can drive an
experiment-local surface that reproduces Lane D-style deformation and
represents Lane C-style feedback eligibility. This is a proof of
contract, not native support. Lane F remains blocked until the LGRC paper
extension and Phase 8 native implementation plan are written.
