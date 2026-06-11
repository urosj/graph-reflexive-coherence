# Fixture Manifest Validation

Experiment:

```text
2026-05-N03-grc9v3-polarized-basin-loops
```

Manifest:

```text
configs/fixture_manifest_v1.json
```

Status:

```text
pass
```

## Reproduction Commands

Run from the repository root:

```bash
python experiments/2026-05-N03-grc9v3-polarized-basin-loops/scripts/validate_fixture_manifest.py
python -m json.tool experiments/2026-05-N03-grc9v3-polarized-basin-loops/outputs/fixture_manifest_validation.json
git diff -- src
```

Observed command result:

```text
{"status": "pass", "errors": []}
```

`git diff -- src` produced no output.

## Checks

The validation checked:

- all node ids exist;
- all edge ids are unique and present;
- every port id is in `1..9`;
- every ring edge follows the declared clockwise `node_u -> node_v` direction;
- every node has active degree `2`;
- every node uses exactly ports `4` and `6`;
- source/sink masks are disjoint;
- source/sink masks are inside the parent basin mask;
- forward and return channel edge sets are disjoint;
- forward and return channel masks reference live edges;
- reversed masks swap source/sink regions coherently;
- reversed masks swap forward/return channels coherently;
- required lane ids are present;
- `n_cycles_min`, `washout_steps`, and `min_eval_steps` are present;
- README control configs are present and typed;
- projection-disabled dry run is diagnostic only;
- topology-disabled control sets `topology_events_enabled = false`;
- topology-disabled control also sets `pruning_enabled = false`;
- `two_equal_canonical_ring_bumps` is explicitly resolvable;
- return-channel sign semantics are explicit;
- channel flux semantics are separated from region boundary export/import;
- edge field aliases are recorded (`u/v` versus `node_u/node_v`);
- uniform-conductance shuffled-control caveat is recorded;
- configured-parent evidence has a candidate-claim ceiling note;
- `dt` and `total_steps` are recorded;
- `total_steps` covers washout plus minimum evaluation window;
- default edge properties include flux coupling and temporal delay defaults;
- S-lane composite initialization is explicitly resolvable;
- K-lane base lane, initialization, kick, and composition are resolvable;
- simple analysis fixture explicitly declares reversal status;
- no `src/*` changes were required;

## Port Orientation

The canonical fixture uses:

```text
clockwise_out_port = 6 = row 2, column 3
clockwise_in_port  = 4 = row 2, column 1
```

Every edge is oriented clockwise:

```text
edge.node_u -> edge.node_v
```

and every `node_v` is the clockwise successor of `node_u`.

## Synthetic Flux Check

The validation injected the interpretation:

```text
flux_uv = +1 on every clockwise edge
```

Expected result:

```text
forward channel flux > 0
return channel flux > 0
```

Observed:

```text
forward_flux_sum = 5.0
return_flux_sum = 5.0
source_region_net_export = 0.0
sink_region_net_export = 0.0
```

The zero net export for the source/sink regions is expected for uniform
clockwise circulation on a closed ring: each two-node aspect has one incoming
and one outgoing boundary edge. Channel flux remains positive in the declared
clockwise direction.

## Fixture Geometry

The canonical masks are:

```text
source_aspect_nodes = [0, 1]
sink_aspect_nodes   = [6, 7]
forward_channel_edges = [1, 2, 3, 4, 5]
return_channel_edges  = [7, 8, 9, 10, 11]
source_internal_edges = [0]
sink_internal_edges   = [6]
```

This gives two-node source/sink aspects, five-edge forward/return channels,
and one internal edge inside each aspect.

## Observable Semantics Tightening

The manifest records that:

```text
J_forward = sum over forward_channel_edges only
J_return  = sum over return_channel_edges only
source_export = boundary export from source_aspect_nodes
sink_import   = boundary import into sink_aspect_nodes
```

These are related but not identical surfaces. Iteration 3 should not use
`J_forward` as a synonym for source export, or `J_return` as a synonym for
sink import.

Return flux is positive in the declared clockwise edge orientation:

```text
7 -> 8 -> 9 -> 10 -> 11 -> 0
```

It is not counterclockwise or opposite-sign flux in this fixture.

The manifest also records:

```text
two_equal_canonical_ring_bumps
```

as `canonical_ring_bump` applied twice with equal parameters at the configured
lane bump centers, followed by conserved simplex projection.

The S lane composite initialization is explicit:

```text
canonical_ring_bump -> small_local_source_sink_modulation -> projection
```

The K lane resolves `base_lane = U2`, initializes the uniform closed
substrate, then applies `zero_sum_kick` at `kick_step`.

The shuffled-conductance control records that shuffling
`initial_fixture_base_conductance` is non-informative for the current uniform
conductance fixture unless conductance heterogeneity is added. The first
informative shuffled control is `channel_mask_assignment`.

## Conclusion

The manifest is ready for Iteration 3 observable implementation.

No `src/*` files were changed.
