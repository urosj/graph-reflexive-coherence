"""Retained SC-2 checkpoint consistency; no reconstruction of the trajectory.

The caller freshly computes the trap and its exact rational metric. Checking an
endpoint box against that trap does not establish how the trajectory reached it.
"""
from fractions import Fraction as F

from flint import arb, arb_mat, ctx, fmpq

from spark_completion_continuation import geometric_roster, need


def check_history(history, targets, proof, metric):
    """Bind both chart observations and saved entry coordinates to the trap."""
    need(set(targets) == {'1', '-1'}, 'both target charts required')
    order = targets['1']['graph']['live_node_ids']
    nodes = set(order)
    need(len(nodes) == len(order) and set(proof['center']) == nodes,
         'metric/center node roster')
    need(metric.nrows() == metric.ncols() == len(order), 'metric dimension')
    rows = history['observations']
    entry = history['certified_trap_entry_step']
    need(len(rows) == entry and entry > 0, 'entry observation missing')
    need(1 <= history['first_gain_step'] <= entry, 'gain chronology')
    expected = proof['complete_basins']
    for k, row in enumerate(rows, 1):
        need(row['step'] == k, 'observation chronology')
        charts = row['qualified_basins']
        need(set(charts) == {'1', '-1'}, 'both observation charts required')
        for basins in charts.values():
            need(isinstance(basins, dict), 'complete basin dictionary required')
            assigned = set()
            for anchor, members in basins.items():
                need(isinstance(members, list) and members == sorted(set(members))
                     and len(members) > 1 and anchor in members
                     and set(members) <= nodes and assigned.isdisjoint(members),
                     'invalid complete basin membership')
                assigned.update(members)
            if k >= history['first_gain_step']:
                need(set(basins) == set(expected), 'qualified anchor roster changed')

    radius = F(proof['radius'])
    lower, upper = map(F, history['trap_distance_upper'])
    need(0 <= lower <= upper < radius, 'retained entry distance outside trap')
    need(F(rows[-1]['trap_distance_upper']) == upper, 'entry distance summaries differ')
    checkpoints = history['checkpoints']
    need(str(entry) in checkpoints, 'entry checkpoint missing')
    with ctx.workprec(512):
        final = None
        for key, checkpoint in checkpoints.items():
            step = int(key)
            need(str(step) == key and 1 <= step <= entry, 'checkpoint chronology')
            need(set(checkpoint) == nodes, 'checkpoint node roster')
            coordinates = []
            for node in order:
                interval = checkpoint[node]
                need(isinstance(interval, list) and len(interval) == 2,
                     'checkpoint interval pair required')
                lo, hi = map(F, interval)  # Rejects nonfinite entries as well.
                need(0 < lo <= hi, 'invalid positive checkpoint interval')
                coordinates.append([arb(fmpq(str((lo + hi) / 2)),
                                        fmpq(str((hi - lo) / 2)))])
            state = arb_mat(coordinates)
            # Necessary consistency with exact charge conservation; a box does
            # not itself prove that every enclosed vector has charge 21.
            need(sum(state[i, 0] for i in range(len(order))).contains(21),
                 'checkpoint excludes exact charge')
            for chi, target in targets.items():
                need(target['graph']['live_node_ids'] == order, 'chart node order')
                roster = geometric_roster(target['graph'], state, order)
                need(roster == rows[step - 1]['qualified_basins'][chi],
                     'checkpoint complete basin dictionary differs from observation')
                if step == entry:
                    need(roster == expected, 'entry complete basins differ from trap')
            if step == entry:
                final = state
        delta = final - arb_mat([[arb(fmpq(proof['center'][n]))] for n in order])
        squared = (delta.transpose() * arb_mat(metric) * delta)[0, 0]
        # P is positive definite on the full space. Only the upper endpoint is
        # needed; interval dependence may make the lower endpoint negative.
        need(squared.is_finite() and squared.upper() >= 0, 'invalid metric enclosure')
        distance = squared.upper().sqrt().upper()
        need(distance < arb(fmpq(str(radius))), 'checkpoint metric distance outside trap')
        need(distance <= arb(fmpq(str(upper))), 'saved distance does not bound checkpoint')
        return str(distance.fmpq())
