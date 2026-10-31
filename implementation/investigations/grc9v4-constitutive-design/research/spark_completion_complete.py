"""SC-2 executable exact-equation spark completion, investigation only.

Reuse the certified approach. Predeclare two further positive ordinary beats
(duration 64) inside the existing trap, with fixed 512-bit Arb and no fallback.
The interval boxes enclose exact charge-21 states; they are not native states.
"""
import copy
from fractions import Fraction as F
from flint import arb, arb_mat, fmpq, ctx
from spark_completion_positive import content_id, norm_upper, compact_box
from spark_completion_os_reference import COSReference
from spark_completion_source_beat import exact_classification
from spark_completion_continuation import need, bound, infnorm, geometric_roster

WINDOW_BEATS = 2
STEP_DURATION = F(32)
WINDOW_DURATION = F(64)
PRECISION = 512

def source_pressure(prepared, targets):
    """Literal physical-similarity read, port relabeling and local gain controls."""
    target = targets['1']
    graph = prepared['source_graph']
    m = COSReference(graph, 'rational')
    C = m.vector(prepared['current_prestate'])
    step = m.step(C, eta=m.q(1, 1024), dt=m.q(32))
    for name, H in (('predictor', m.I), ('corrector', step['geometry'])):
        current, flat = m.direct_similarity_read(C, H, eta=m.q(1, 1024))
        need(current == step[name]['current'] and flat == step[name]['causal_flat'],
             'literal physical-similarity source mismatch')
    need(step['after'] == m.vector(prepared['capture']['current']), 'actual poststate mismatch')
    need(sum(step['after'].entries()) == 21, 'source exact charge')

    # Rename and reorder actual ports/edges/vertices; no target-success fitting.
    names = {node: 'renamed-' + str(i) for i, node in enumerate(reversed(m.nodes))}
    renamed = copy.deepcopy(graph)
    renamed['live_node_ids'] = [names[n] for n in reversed(m.nodes)]
    renamed['edges'].reverse()
    for i, edge in enumerate(renamed['edges']):
        edge['edge_id'] = 'renamed-edge-' + str(i)
        for end in ('tail', 'head'):
            edge[end]['node_id'] = names[edge[end]['node_id']]
    n = COSReference(renamed, 'rational')
    renamed_before = n.vector({names[k]: v for k, v in prepared['current_prestate'].items()})
    renamed_after = n.step(renamed_before, eta=n.q(1, 1024), dt=n.q(32))['after']
    need(renamed_after == n.vector({names[k]: v for k, v in prepared['capture']['current'].items()}),
         'source relabel/reorder covariance')
    _, basins = exact_classification(renamed, renamed_after)
    need(basins == {names['p']: sorted(names.values())}, 'relabeling changed parent membership')

    module = target['module']
    footprint = set(target['graph']['live_node_ids'])
    need(set(prepared['capture']['parent_members']) == set(m.nodes), 'parent footprint')
    need({('v' if x in module else x) for x in footprint} == set(m.nodes), 'D11 lineage lift')
    for role in ('current', 'reset'):
        after = prepared['transferred_' + role]
        before = prepared['capture'][role]
        need(set(after) == footprint and F(after[module[0]]) == 0, 'target/core roster')
        need(all(F(after[n]) == F(before[n]) for n in m.nodes if n != 'v'), 'exterior transfer')
        need([F(after[n]) for n in module[1:]] ==
             [F(before['v']) * x for x in (F(1, 64), F(31, 32), F(1, 64))], 'satellite transfer')
        need(sum(map(F, after.values())) == 21, 'event exact charge')
        for chi in ('1', '-1'):
            g = targets[chi]['graph']
            e = COSReference(g, 'rational')
            _, initial = exact_classification(g, e.vector(after))
            need(set(initial) == {'p'}, 'allocation alone earns descendant gain')
    need(prepared['reset_prestate'] == prepared['capture']['reset'], 'reset was advanced')
    return dict(literal_predictor_and_corrector_equal=True, exact_source_charge='21',
                relabel_and_order_covariance=True, relabel_does_not_create_gain=True,
                exact_both_role_D11_transfer=True, immediate_allocation_gain=0,
                reset_unchanged=True, native_steps=0, native_events=0,
                verification='exact short source/transfer calculations; no long recurrence rerun')


def lineage_id(event):
    """This event occurrence, independent of later proof/window/review identity."""
    return content_id({key:event[key] for key in (
        'source_state_id','source_step_index','source_time','target_graph_ids',
        'actual_transferred_current_id','unchanged_transferred_reset_id','request_shares','extras')})


def completion_decision(event, proof, observations, *, role='current', invalidated=False,
                        completed_events=frozenset()):
    """Compose freshly certified research observations; not a native receipt API.

    The record checker reconstructs the observations numerically. This function
    checks the composition/lineage/window premises and returns a pure decision.
    """
    need(role == 'current', 'reset probe cannot earn a live completion')
    need(not invalidated, 'completion window invalidated')
    need('v' in event['parent_members'] and event['parent_anchor'] == 'p', 'qualified parent missing')
    need(len(observations) == WINDOW_BEATS, 'positive window incomplete')
    event_id = lineage_id(event)
    need(event['trap_id'] == content_id(proof), 'trap binding mismatch')
    radius = F(proof['radius'])
    footprint = set(event['parent_footprint'])
    module = set(event['module'])
    for offset, row in enumerate(observations, 1):
        need(row['event_id'] == event_id and row['equation_id'] == event['equation_id']
             and row['trap_id'] == event['trap_id']
             and row['graph_ids'] == event['target_graph_ids'], 'observation identity mismatch')
        need(row['target_step'] == event['entry_step'] + offset, 'nonconsecutive positive beats')
        need(F(row['elapsed_after_entry']) == offset * STEP_DURATION, 'wrong positive elapsed time')
        need(F(row['metric_distance_upper']) < radius and F(row['minimum_resource']) > 0
             and F(row['split_upper']) < F(1, 10**11), 'observation outside admitted trap')
        need(set(row['complete_basins']) == {'1', '-1'}, 'both charts required')
        for basins in row['complete_basins'].values():
            need(basins == proof['complete_basins'], 'complete trap domains changed')
            need(all(set(members) <= footprint for members in basins.values()), 'external basin counted')
    need(F(observations[-1]['elapsed_after_entry']) >= WINDOW_DURATION, 'window duration incomplete')
    basins = proof['complete_basins']
    descendants = {a: members for a, members in basins.items()
                   if a == event['parent_anchor'] or a in module}
    children = sorted(a for a in descendants if a in module)
    gain = len(descendants) - 1
    need(gain >= 1 and children, 'no additional qualified descendant organization')
    new = event_id not in completed_events
    return dict(status='completed_under_selected_SC1_exact_equation_criterion', event_id=event_id,
                parent_anchor=event['parent_anchor'], stable_descendants=descendants,
                new_child_anchors=children, certified_local_gain=gain,
                newly_recorded_gain=gain if new else 0,
                replay_of_existing_completion=not new,
                positive_window_beats=len(observations), positive_window_duration=str(WINDOW_DURATION),
                target_completion_step=observations[-1]['target_step'],
                completion_time_from_source_prestate=str(STEP_DURATION * (1 + observations[-1]['target_step'])),
                subsequent_exact_persistence='full-map invariant contraction and uniform complete basin certificate',
                scope='one C_OS research event under the proposed quartic binding',
                native_receipt=False, native_completed_spark_support=False)


def run(source_record, target_record):
    c = source_record['checks']; p = c['prepared']; old = target_record['checks']
    targets = old['targets']; t = targets['1']; proof = old['trap']
    pressure = source_pressure(p, targets)
    history = c['actual_current_target']; entry = history['certified_trap_entry_step']
    event = dict(source_state_id=p['capture']['source_state_identity'],
                 source_step_index=p['capture']['ordinary_step_index'],source_time=p['capture']['time'],
                 source_record_digest=source_record['record_digest'],
                 parent_anchor=p['capture']['qualified_parent'], parent_members=p['capture']['parent_members'],
                 parent_footprint=sorted(t['graph']['live_node_ids']), module=t['module'],
                 target_graph_ids={chi:content_id(v['graph']) for chi,v in targets.items()},
                 actual_transferred_current_id=content_id(p['transferred_current']),
                 unchanged_transferred_reset_id=content_id(p['transferred_reset']),
                 equation_id=content_id(target_record['equation_binding']),
                 trap_id=content_id(proof), entry_step=entry,
                 request_shares=['1/64','31/32','1/64'], extras=[0,0,0])
    # Each chart is a representation of the same research event, not a birth.
    rows = []
    with ctx.workprec(PRECISION):
        m = COSReference(t['graph'], 'arb'); e = COSReference(t['graph'], 'rational')
        need(all(sum(e.B[i,j] for i in range(e.n)) == 0 for j in range(e.m)),
             'exact incidence does not conserve charge')
        A = e.B * (e.I + (e.q(3,4)*e.I + e.Le).inv()/4) * e.Bt
        Pi = e.matrix([[e.q(1,e.n) for _ in range(e.n)] for _ in range(e.n)])
        P = arb_mat((A+Pi).inv())
        center = m.vector(proof['center'])
        checkpoint = history['checkpoints'][str(entry)]
        values = []
        for n in m.nodes:
            lo,hi = map(F,checkpoint[n])
            values.append([arb(fmpq(str((lo+hi)/2)),fmpq(str((hi-lo)/2)))])
        C = m.matrix(values)
        start = {n:bound(C[i,0]) for i,n in enumerate(m.nodes)}
        for offset in range(1,WINDOW_BEATS+1):
            step = m.step(C,eta=m.q(1,1024),dt=m.q(32)); C = step['after']
            need(sum(C[i,0] for i in range(m.n)).contains(21), 'exact-charge state not enclosed')
            d = C-center
            metric = ((d.transpose()*P*d)[0,0]).upper().sqrt().upper()
            lower = min(C[i,0].lower() for i in range(m.n))
            split = norm_upper(step['defect'])
            hmax = (1+sum(step['geometry'][i,i]-1 for i in range(m.m))).upper()
            condition = hmax*(1+hmax*infnorm(m.Le))
            need(condition < 10**12, 'window conditioning limit')
            reads = {}
            for label,H in (('consumed_geometry',step['geometry']),('reference_restart',m.I)):
                read = m.read(C,H,eta=m.q(1,1024))
                need(all(x.is_finite() for x in read['current'].entries()), 'window selected read')
                reads[label] = {key:[[bound(read[key][i,j]) for j in range(read[key].ncols())]
                                    for i in range(read[key].nrows())] for key in read}
            rosters = {chi:geometric_roster(v['graph'],compact_box(m,C),m.nodes) for chi,v in targets.items()}
            need(all(r == proof['complete_basins'] for r in rosters.values()), 'window basin persistence')
            rows.append(dict(event_id=lineage_id(event),equation_id=event['equation_id'],trap_id=event['trap_id'],
                             graph_ids=event['target_graph_ids'],target_step=entry+offset,
                             elapsed_after_entry=str(offset*STEP_DURATION),
                             metric_distance_upper=bound(metric)[1], minimum_resource=bound(lower)[0],
                             split_upper=bound(split)[1], conditioning_upper=bound(condition)[1],
                             resources={n:bound(C[i,0]) for i,n in enumerate(m.nodes)},
                             complete_basins=rosters,reads=reads))
    decision = completion_decision(event,proof,rows)
    again = completion_decision(event,proof,rows,completed_events={decision['event_id']})
    need(again['newly_recorded_gain'] == 0, 'replay creates another child gain')
    another_review = dict(event,source_record_digest='another-review-of-the-same-event')
    need(completion_decision(another_review,proof,rows,completed_events={decision['event_id']})['newly_recorded_gain']==0,
         'another evidence identity mints completion gain')
    rejected = []
    cases = (
        ('single_observation', lambda r:r.pop()),
        ('zero_elapsed', lambda r:r[-1].update(elapsed_after_entry='0')),
        ('duplicate_beat', lambda r:r[-1].update(target_step=r[0]['target_step'])),
        ('stale_source', lambda r:r[-1].update(event_id='stale')),
        ('changed_policy', lambda r:r[-1].update(equation_id='different')),
        ('changed_trap', lambda r:r[-1].update(trap_id='different')),
        ('missing_chart', lambda r:r[-1]['complete_basins'].pop('-1')),
        ('wrong_domain_membership', lambda r:r[-1]['complete_basins']['1']['p'].append('external')),
    )
    for name,mutate in cases:
        changed = copy.deepcopy(rows); mutate(changed)
        try:
            completion_decision(event,proof,changed)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('false completion accepted: '+name)
    for name,options in (('reset_role',dict(role='reset')),('invalidated_window',dict(invalidated=True))):
        try:
            completion_decision(event,proof,rows,**options)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('false completion accepted: '+name)
    need(content_id(p['capture']['reset']) == content_id(p['reset_prestate']), 'reset source mutated')
    return dict(status='positive_bounded_research_spark_completion',decision=decision,event=event,
                declared_window=dict(beats=WINDOW_BEATS,duration=str(WINDOW_DURATION),step_duration=str(STEP_DURATION),
                                     precision_bits=PRECISION,automatic_fallback=False,
                                     declaration='fixed before execution; starts at retained certified entry'),
                source_pressure=pressure,entry_enclosure=start,observations=rows,
                negative_controls=rejected,replay_decision=again,
                reused_current_approach_steps=entry,reused_reset_entry_step=c['reset_reuse']['certified_trap_entry_step'],
                new_current_window_steps=WINDOW_BEATS,new_reset_steps=0,
                charge_statement='Each box encloses the connected exact charge-21 trajectory. Incidence conservation is exact; box midpoints are never advanced as states.',
                native_steps=0,native_events=0,native_completion=False,
                quartic_runtime_admission=False,other_realizations_proved=False)

