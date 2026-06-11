# N04 Baseline Inventory

Generated: `2026-05-16T06:56:06.395757+00:00`

Command:

```bash
.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/build_n04_baseline_inventory.py
```

## Boundary

- N04 is experiment-local.
- `src/*` changes are not required for Iteration 1.
- N03/E3 supplies pulse-substrate evidence only.
- Movement claims are not inherited from N03.
- Adaptive topology remains blocked.
- Experiment root: `experiments/2026-05-N04-grc9v3-movement-ladders`

## Source Status

```text
(no src/* status entries)
```

## Environment

- Python executable: `.venv/bin/python`
- Python version: `3.12.3 (main, Mar 23 2026, 19:04:32) [GCC 13.3.0]`
- Platform: `Linux-5.15.167-0515167-generic-x86_64-with-glibc2.39`
- `PYTHONPATH`: ``
- `VIRTUAL_ENV`: ``
- GPU required: `False`

## N03/E3 Handoff

- classification: `n03_native_lgrc9v3_packet_loop_reproduced`
- status: `passed`
- N04 input loop ladder level: `L5`
- loop level interpretation: `Native LGRC9V3 self-rearming packetized pulse substrate; movement remains unopened.`
- native LGRC9V3 execution: `True`
- native packet execution: `True`
- native surplus trigger: `True`
- native self-rearm evidence: `True`
- native D2.3 equivalent: `True`
- movement claim allowed: `False`
- native GRC9V3 proposal-flux loop evidence: `False`
- controls passed: `True`
- snapshot/telemetry replayable: `True`

## E3 Positive Rows

- classification: `native_lgrc9v3_positive_reproduction_passed`
- direction symmetry: `{'cycle_count_delta': 0, 'passed': True, 'self_rearm_count_delta': 0, 'trigger_count_delta': 0}`
- clockwise: `{'cycle_count': 3, 'self_rearm_count': 12, 'trigger_count': 12, 'max_event_budget_error': 0.0, 'topology_changed': False, 'route_aspect_digest': '25ce1cc1550c0a717d4c1bcaa7f4179789024b67c2c22893df1f0fa21d41cb57'}`
- counter-clockwise: `{'cycle_count': 3, 'self_rearm_count': 12, 'trigger_count': 12, 'max_event_budget_error': 0.0, 'topology_changed': False, 'route_aspect_digest': 'a621e96cd477308e0365b1d06f2a80f4a1285c7c7f4680d24cd3715a878ef3c8'}`

## Route Manifest

- manifest id: `e3_native_lgrc9v3_packet_loop_route_manifest_v1`
- execution engine: `native_lgrc9v3`
- minimum cycles: `3`
- packet amount: `0.1`
- route aspects: `{'clockwise': 'n03_e3_native_four_pole_packet_loop_cw', 'counter_clockwise': 'n03_e3_native_four_pole_packet_loop_ccw'}`

## Artifacts

| Name | Exists | SHA-256 | Path |
|---|---:|---|---|
| route_manifest | True | `12c9cd933e3209dca2fdc78eeccad84644477a206c72901bbda9b1858c66cd0f` | `experiments/2026-05-N03-grc9v3-polarized-basin-loops/configs/e3_native_lgrc9v3_packet_loop_route_manifest.json` |
| e3_0_baseline | True | `66449c75c0d2df41b91f0c3b75693967c4eec1d1b595c8c380dc33549f38c7ab` | `experiments/2026-05-N03-grc9v3-polarized-basin-loops/outputs/e3_0_dependency_and_fixture_baseline.json` |
| e3_1_positive | True | `e421e11a15fba7c7df6c7483b5a026b3afe1b3a83f2d948060ba357f24c14dc7` | `experiments/2026-05-N03-grc9v3-polarized-basin-loops/outputs/e3_1_native_positive_reproduction.json` |
| e3_2_controls | True | `4a037ccd1ba375ba1e867d41ce95cdf26f8b780477c95dc090676c24942b889b` | `experiments/2026-05-N03-grc9v3-polarized-basin-loops/outputs/e3_2_native_control_parity.json` |
| e3_3_snapshot_telemetry | True | `e03cc3d813a11d502742e91520cb17d13061201226fa9c1997e08b31ded3fd9a` | `experiments/2026-05-N03-grc9v3-polarized-basin-loops/outputs/e3_3_snapshot_telemetry_reproduction.json` |
| e3_closeout | True | `75e02858f32484a8c4e9a24d9751c0ce98e4ef603fd6e550d8a47f7466e2288e` | `experiments/2026-05-N03-grc9v3-polarized-basin-loops/outputs/e3_native_lgrc9v3_packet_loop_closeout.json` |
| e3_visualization | True | `ab7e955c598dc768fb3ca95fa19b16b58001e19290f154de6bde7fe19eb205ab` | `experiments/2026-05-N03-grc9v3-polarized-basin-loops/reports/e3_native_lgrc9v3_packet_loop_visualization.svg` |
| e3_animation_report | True | `2f6975828e1778bc081267ee2fa503f57246992a42e6e14386a6f612ed9baab4` | `experiments/2026-05-N03-grc9v3-polarized-basin-loops/reports/e3_native_lgrc9v3_packet_loop_animation.md` |

## Baseline Commands

- `.venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/build_n04_baseline_inventory.py`
- `git status --short src`
- `git diff --check`
