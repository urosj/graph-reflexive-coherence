"""Declared C_CI_PC source/event/target histories; exact equations, no native grant."""
from fractions import Fraction as F
import time
from flint import arb, arb_mat, fmpq, ctx
from spark_completion_ci_pc import CCIPCReference, trap_certificate, global_domain, _graph_constants
from spark_completion_positive import fixture, content_id, norm_upper, compact_box
from spark_completion_ci_campaign import retained, exact_bounds, scalar_upper, box_payload, matrix_payload
from spark_completion_continuation import need, geometric_roster
import spark_completion_basins as basins

PRECISION = 8192
HORIZON = 1024
TIME_LIMIT = 3600
WINDOW = 2


def carrier_payload(m, Z):
    return [exact_bounds(Z[i,j]) for i,j in m.pairs]


def state_payload(m, C, Z):
    return dict(C=box_payload(m,C), Z=carrier_payload(m,Z))


def read_payload(read):
    return dict(root_error=exact_bounds(read['error']), root_residual=exact_bounds(read['residual']),
                H=matrix_payload(read['geometry']), J=matrix_payload(read['selected']['current']),
                flat=matrix_payload(read['flat']), S=matrix_payload(read['source']))


def initial_source_carrier(m, role):
    Z = m.zero()
    for i in range(m.m): Z[i,i] = m.q(1,2**16) if role == 'current' else m.q(-1,2**17)
    return Z


def prepare_source(source, targets, role):
    need(role in ('current','reset'), 'role')
    pre = retained('SC2SourceBeat.json.xz')['checks']['prepared']
    m = CCIPCReference(source)
    C0 = m.vector(pre['current_prestate']); Z0 = initial_source_carrier(m,'current')
    step = m.ccipc_step(C0,Z0); post,Zpost = step['after'],step['carrier_after']
    fresh = m.ccipc_read(post,Zpost)
    reset = m.vector(pre['reset_prestate']); Zreset = initial_source_carrier(m,'reset')
    reset_read = m.ccipc_read(reset,Zreset)
    need(all(post[i,0]>0 for i in range(m.n)), 'source poststate positivity')
    roster = geometric_roster(source,post,m.nodes)
    need(roster == {'p':sorted(m.nodes)}, 'actual postbeat source lacks complete parent')
    edges = [(e['tail']['node_id'],e['tail']['port'],e['head']['node_id'],e['head']['port'],F(1))
             for e in source['edges']]
    bounds = {n:tuple(map(F,exact_bounds(post[i,0]))) for i,n in enumerate(m.nodes)}
    rows = basins.row_intervals(m.nodes,edges,{n:v[0] for n,v in bounds.items()},
                               {n:v[1] for n,v in bounds.items()})
    gv = [arb(fmpq(str((l+h)/2)),fmpq(str((h-l)/2))) for l,h in rows['v']]
    gradient = 16-sum(x*x for x in gv); spark = arb(fmpq(1,8))-min(-x for x in gv)
    need(gradient>0 and spark>0, 'actual postbeat source fails trigger')
    ports = [e[end]['port'] for e in source['edges'] for end in ('tail','head') if e[end]['node_id']=='v']
    need(sorted(ports)==list(range(1,10)), 'source saturation')
    need(sum(F(v) for v in pre['current_prestate'].values())==21 and
         sum(F(v) for v in pre['reset_prestate'].values())==21, 'exact source charge')
    need(all(sum(m.B[i,j] for i in range(m.n))==0 for j in range(m.m)), 'incidence conservation')
    shares = ['1/64','31/32','1/64']; need(sum(map(F,shares))==1, 'exact transfer charge')
    target = targets['1']; module = target['module']; t = CCIPCReference(target['graph'])
    operand = post if role=='current' else reset
    values = {n:operand[i,0] for i,n in enumerate(m.nodes) if n!='v'}
    values[module[0]] = m.q(0)
    for n,share in zip(module[1:],shares): values[n] = operand[m.nodes.index('v'),0]*m.q(fmpq(share))
    C = t.matrix([[values[n]] for n in t.nodes]); Z = t.zero()
    need(set(geometric_roster(target['graph'],C,t.nodes))=={'p'}, 'allocation credited as gain')
    archive = {r:state_payload(m,c,z) for r,c,z in [('current',post,Zpost),('reset',reset,Zreset)]}
    history = dict(policy_id='event_loss_and_zero_target_carrier_v1', disposition='whole_carrier_reset',
                   target_initializer_id='canonical_zero_carrier_v1', information_loss='carrier_history_loss',
                   source_carrier_pairs=m.pairs, source_archive=archive,
                   source_archive_digest=content_id(archive), target_carrier_pairs=t.pairs,
                   target_all_dense_entries_zero=True, target_dense_entries=t.m*t.m,
                   native_release=False, source_history_nonzero=True)
    record = dict(initial_prestate_source='SC2SourceBeat.json.xz /checks/prepared',
                  current_prestate=state_payload(m,C0,Z0), actual_CI_PC_poststate=state_payload(m,post,Zpost),
                  consumed_current_read=read_payload(step['read']), fresh_event_read=read_payload(fresh),
                  reset_state=state_payload(m,reset,Zreset), reset_read=read_payload(reset_read),
                  complete_parent=roster, gradient_squared_margin=exact_bounds(gradient), spark_margin=exact_bounds(spark),
                  source_steps=1, reset_advanced=False, allocation_shares=shares, charge='21',
                  charge_argument='Exact incidence identity and shares sum one; intervals enclose this exact trajectory.',
                  carrier_history=history, domain=global_domain(source))
    return t,C,Z,record


def distance(m,C,Z,proof,P):
    diff = C-m.vector(proof['center'])
    resource = (diff.transpose()*P*diff)[0,0].sqrt().upper()
    carrier = norm_upper(Z)*proof['weight']
    return resource,carrier,max(resource.upper(),carrier.upper())


def campaign(role, *, maximum_steps=HORIZON, require_completion=True, progress=True):
    start = time.monotonic(); source,_,targets = fixture()
    with ctx.workprec(512):
        proof,P = trap_certificate({**targets['1'],'charts':targets},
                                   retained('SC2PositiveCandidate.json.xz')['checks']['trap'])
    with ctx.workprec(PRECISION):
        m,C,Z,source_record = prepare_source(source,targets,role)
        metric = arb_mat(P); radius = m.q(fmpq(proof['resource_radius']))
        read = m.ccipc_read(C,Z); initial = state_payload(m,C,Z)
        checkpoints = dict(event=dict(**initial,read=read_payload(read)))
        observations=[]; entry=None; gain=None
        first_read_count = m.read_count
        first_iterations = m.newton_iterations; first_work = m.proposal_bit_work
        for step in range(1,maximum_steps+1):
            need(time.monotonic()-start<TIME_LIMIT, 'explicit campaign wall-time cap reached')
            C,Z = m.advance(C,Z,read)
            need(all(C[i,0]>0 and C[i,0]<4 for i in range(m.n)), 'positive resource domain')
            need(sum(C[i,0] for i in range(m.n)).contains(21), 'charge enclosure excludes invariant')
            read = m.ccipc_read(C,Z)  # exact same full subject consumed by next advance
            rd,zd,total = distance(m,C,Z,proof,metric)
            observed = compact_box(m,C)  # outward inspection view; never fed back into evolution
            roster = {chi:geometric_roster(t['graph'],observed,m.nodes) for chi,t in targets.items()}
            if gain is None and roster==proof['complete_basins']: gain=step
            if entry is None and total<radius:
                need(roster==proof['complete_basins'], 'trap entry basin mismatch')
                entry=step; checkpoints['entry']=dict(**state_payload(m,C,Z),read=read_payload(read))
            if entry is not None:
                need(total<radius and roster==proof['complete_basins'], 'completion window left full-state trap')
            observations.append(dict(step=step,**state_payload(m,C,Z),
                minimum_resource=exact_bounds(min(C[i,0].lower() for i in range(m.n))),
                resource_distance_upper=scalar_upper(rd),weighted_carrier_distance_upper=scalar_upper(zd),
                full_distance_upper=scalar_upper(total),carrier_norm_upper=scalar_upper(norm_upper(Z)),
                source_norm_upper=scalar_upper(norm_upper(read['source'])),
                root_error_upper=scalar_upper(read['error']),root_iterations=read['iterations'],complete_basins=roster))
            if progress and (step%100==0 or entry is not None):
                print(role,step,'seconds',round(time.monotonic()-start,1),'full-distance',total.str(8),flush=True)
            if entry is not None and step==entry+WINDOW:
                checkpoints['completion']=dict(**state_payload(m,C,Z),read=read_payload(read)); break
        complete = entry is not None and observations[-1]['step']==entry+WINDOW
        if require_completion: need(complete, 'no certified full-state completion within declared horizon')
        need(m.read_count-first_read_count==len(observations), 'extra or missing poststate reads')
        need(m.writer_count==len(observations), 'carrier writer cadence')
        decision = dict(role=role, scientific_completion=complete and role=='current',
                        reset_probe_earns_live_gain=False,local_gain=int(complete and role=='current'),
                        first_certified_entry=entry,first_spatial_gain=gain,
                        target_completion_step=observations[-1]['step'] if complete else None,
                        window_beats=WINDOW,window_elapsed='64',stable_descendants=proof['complete_basins'],
                        full_state=['C','Z_4'],native_completion=False,accepted_authority=False)
        return dict(role=role,source_graph=source,targets=targets,source=source_record,proof=proof,
                    initial_target=initial,observations=observations,checkpoints=checkpoints,decision=decision,
                    arithmetic=dict(precision_bits=PRECISION,trapping_precision_bits=512,
                        maximum_target_steps=HORIZON,time_limit_seconds=TIME_LIMIT,automatic_fallback=False,
                        retained_coordinates='outward 112-bit dyadic enclosures; full recurrence starts from exact inputs',
                        midpoint_evolution=False,proposal_policy='precision_ladder',
                        proposal_minimum_bits=128,proposal_newton_limit_per_stage=16),
                    optimization=dict(exact_graph_cache_key='full canonical graph',
                        proposal_policy=m.proposal_policy,newton_iterations=m.newton_iterations-first_iterations,
                        proposal_bit_work=m.proposal_bit_work-first_work,
                        constant_cache_hits=_graph_constants.cache_info().hits,
                        constant_cache_misses=_graph_constants.cache_info().misses,
                        target_poststate_reads=len(observations),target_carrier_writes=m.writer_count,
                        identical_full_state_read_reuse=True,batched_derivative_rhs=True,
                        chiral_incidence_verified=True,trajectory_results_cached=False),
                    elapsed_seconds=time.monotonic()-start,earlier_family_trajectory_reused=False,native_steps=0)
