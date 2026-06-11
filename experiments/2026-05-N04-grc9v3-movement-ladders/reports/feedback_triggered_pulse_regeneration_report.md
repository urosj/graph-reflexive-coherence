# N04 Lane C Feedback-Triggered Pulse Regeneration

Status: `passed`
Claim ceiling: `feedback_triggered_pulse_regeneration`

Command:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/run_feedback_coupled_pulse_regeneration.py
```

## Interpretation

Feedback-triggered regeneration passes as an experiment-local candidate: regenerated pulses are authorized from serialized boundary polarity state rather than copied from the original E3 schedule.
