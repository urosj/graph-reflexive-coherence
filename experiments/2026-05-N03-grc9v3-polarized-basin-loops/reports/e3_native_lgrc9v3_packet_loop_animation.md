# E3 Native LGRC9V3 Packet-Loop Standard Animation

Command:

```bash
PYTHONPATH=src .venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/animate_e3_native_lgrc9v3_packet_loop.py
```

This animation is rendered through `pygrc.visualization` from saved LGRC9V3 telemetry graph checkpoints. It uses native E3 packet-loop execution and does not use the D2.3 prototype runner as the execution engine.

Generated artifacts:

- Telemetry: `experiments/2026-05-N03-grc9v3-polarized-basin-loops/outputs/e3_native_lgrc9v3_packet_loop_animation/e3-native-lgrc9v3-packet-loop-animation/telemetry`
- Graph animation: `experiments/2026-05-N03-grc9v3-polarized-basin-loops/outputs/e3_native_lgrc9v3_packet_loop_animation/e3-native-lgrc9v3-packet-loop-animation/visualization/graph_animation.gif`
- Graph sequence: `experiments/2026-05-N03-grc9v3-polarized-basin-loops/outputs/e3_native_lgrc9v3_packet_loop_animation/e3-native-lgrc9v3-packet-loop-animation/visualization/graph_sequence.png`
- Final graph HTML: `experiments/2026-05-N03-grc9v3-polarized-basin-loops/outputs/e3_native_lgrc9v3_packet_loop_animation/e3-native-lgrc9v3-packet-loop-animation/visualization/graph_html/final_graph.html`
- Summary JSON: `experiments/2026-05-N03-grc9v3-polarized-basin-loops/outputs/e3_native_lgrc9v3_packet_loop_animation.json`

Summary:

```json
{
  "checkpoint_count": 39,
  "classification": "e3_native_lgrc9v3_packet_loop_standard_animation",
  "command": "PYTHONPATH=src .venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/animate_e3_native_lgrc9v3_packet_loop.py",
  "completed_self_rearm_count": 12,
  "cycle_count": 3,
  "direction": "clockwise",
  "event_count": 64,
  "graph_animation": "experiments/2026-05-N03-grc9v3-polarized-basin-loops/outputs/e3_native_lgrc9v3_packet_loop_animation/e3-native-lgrc9v3-packet-loop-animation/visualization/graph_animation.gif",
  "graph_html": "experiments/2026-05-N03-grc9v3-polarized-basin-loops/outputs/e3_native_lgrc9v3_packet_loop_animation/e3-native-lgrc9v3-packet-loop-animation/visualization/graph_html/final_graph.html",
  "graph_sequence_figure": "experiments/2026-05-N03-grc9v3-polarized-basin-loops/outputs/e3_native_lgrc9v3_packet_loop_animation/e3-native-lgrc9v3-packet-loop-animation/visualization/graph_sequence.png",
  "movement_claim_allowed": false,
  "native_d2_3_equivalent": true,
  "native_grc9v3_proposal_flux_loop_evidence": false,
  "native_lgrc9v3_execution": true,
  "native_packet_execution": true,
  "native_self_rearm_evidence": true,
  "run_id": "e3-native-lgrc9v3-packet-loop-animation",
  "source_command": ".venv/bin/python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/run_e3_native_lgrc9v3_packet_loop_reproduction.py",
  "status": "passed",
  "telemetry_dir": "experiments/2026-05-N03-grc9v3-polarized-basin-loops/outputs/e3_native_lgrc9v3_packet_loop_animation/e3-native-lgrc9v3-packet-loop-animation/telemetry",
  "visualization_dir": "experiments/2026-05-N03-grc9v3-polarized-basin-loops/outputs/e3_native_lgrc9v3_packet_loop_animation/e3-native-lgrc9v3-packet-loop-animation/visualization"
}
```
