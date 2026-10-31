"""One actual source beat, fresh research capture and D11 target continuation.

Only current advances in the source beat. Reset is the unchanged admitted
baseline. Newton proposes rational initial data; the forward equations, not an
inverse-existence assumption, determine the event input.
"""
from fractions import Fraction as F
from math import floor
from flint import arb, fmpq, ctx
from spark_completion_positive import (
    fixture, COSReference, full_jacobian, norm_upper, compact_box, content_id,
    geometric_roster, spectral_domain, POLICY, need, bound, infnorm,
    NAMESPACE, PRECISION, HORIZON, supplied,
)
import spark_completion_basins as basins


def fraction(q):return F(int(q.p),int(q.q))


def propose_prestate(source,desired):
    with ctx.workprec(512):
        m=COSReference(source,'arb');target=m.vector({n:str(x)for n,x in desired.items()});C=target
        for _ in range(10):
            after=m.step(C,eta=m.q(1,1024),dt=m.q(32))['after']
            full=full_jacobian(m,C)
            J=m.matrix([[full[i,j]-full[i,m.n-1]for j in range(m.n-1)]for i in range(m.n-1)])
            delta=J.solve(m.matrix([[after[i,0]-target[i,0]]for i in range(m.n-1)]))
            values=[(C[i,0]-delta[i,0]).mid()for i in range(m.n-1)]
            C=m.matrix([[x]for x in values]+[[21-sum(values)]])
        # Freeze an executable exact rational point, not an unknown inverse root.
        values=[F(floor(fraction(C[i,0].mid().fmpq())*2**80),2**80)for i in range(m.n-1)]
        values.append(F(21)-sum(values))
        return {n:str(x)for n,x in zip(m.nodes,values)}


def exact_classification(graph,matrix):
    values={n:fraction(matrix[i,0])for i,n in enumerate(graph['live_node_ids'])}
    edges=[(e['tail']['node_id'],e['tail']['port'],e['head']['node_id'],e['head']['port'],F(1))for e in graph['edges']]
    rows=basins.row_intervals(graph['live_node_ids'],edges,values,values)
    result=basins.classify(graph['live_node_ids'],edges,values,POLICY)
    return rows,{a:sorted(v)for a,v in result['basins'].items()}


def prepare():
    source,old_states,targets=fixture();e=COSReference(source,'rational')
    pre=propose_prestate(source,old_states['current']);C=e.vector(pre)
    reset={n:str(x)for n,x in old_states['reset'].items()}
    need(sum(fmpq(x)for x in pre.values())==21 and min(fmpq(x)for x in pre.values())>0,'prestate charge/resource')
    step=e.step(C,eta=e.q(1,1024),dt=e.q(32));post=step['after']
    need(sum(post[i,0]for i in range(e.n))==21 and min(post[i,0]for i in range(e.n))>0,'ordinary source update')
    actual={n:str(post[i,0])for i,n in enumerate(e.nodes)}
    need(actual!={n:str(x)for n,x in old_states['current'].items()},'actual poststate silently replaced with desired state')
    before_rows,before_basins=exact_classification(source,C)
    after_rows,after_basins=exact_classification(source,post)
    need('v' not in before_basins.get('p',[]),'prebeat parent unexpectedly contains expanded vertex')
    need(after_basins=={'p':sorted(e.nodes)},'fresh source has no qualified parent')
    gv=[x[0]for x in after_rows['v']]
    gradient=F(16)-sum(x*x for x in gv);spark=F(1,8)-min(-x for x in gv)
    need(gradient>0 and spark>0,'fresh postbeat hybrid condition')
    # Saturation and unit W_C_tr are properties of the actual source graph.
    ports=[]
    for edge in source['edges']:
        for side in ('tail','head'):
            if edge[side]['node_id']=='v':ports.append(edge[side]['port'])
    need(sorted(ports)==list(range(1,10)),'source saturation')
    fresh_final=e.read(post,step['geometry'],eta=e.q(1,1024))
    fresh_event=e.read(post,e.I,eta=e.q(1,1024))
    reset_read=e.read(e.vector(reset),e.I,eta=e.q(1,1024))
    need(fresh_event['current']!=step['predictor']['current'],'stale current control')
    wrong=C-e.q(32)*e.B*step['predictor']['current']
    need(wrong!=post,'predictor continuity control')
    advanced_reset=e.step(e.vector(reset),eta=e.q(1,1024),dt=e.q(32))['after']
    need(advanced_reset!=e.vector(reset),'reset-advance control')
    target=targets['1'];event_current={n:x for n,x in actual.items()if n!='v'}
    event_current[target['module'][0]]='0'
    for n,share in zip(target['module'][1:],supplied.SHARES):
        event_current[n]=str(fmpq(str(share))*fmpq(actual['v']))
    target_reset={n:str(x)for n,x in target['states']['reset'].items()}
    need(sum(fmpq(x)for x in event_current.values())==21,'event current charge')
    # The actual current target differs; reset is exactly the old certified subject.
    need(event_current!={n:str(x)for n,x in target['states']['current'].items()},'changed target hidden')
    with ctx.workprec(512):
        b=COSReference(source,'arb');ball=b.step(b.vector(pre),eta=b.q(1,1024),dt=b.q(32))
        need(norm_upper(ball['defect'])<b.q(1,10**11),'source OS split')
        need(all(ball['after'][i,0].contains(arb(post[i,0]))for i in range(e.n)),'source exact/Arb comparison')
        # Generated geometry is I plus positive star outer products. These
        # spectral/conditioning bounds apply at consumed and reference reads.
        hmax=(1+sum(ball['geometry'][i,i]-1 for i in range(e.m))).upper()
        condition=hmax*(1+hmax*infnorm(b.Le))
        need(condition<10**12,'source conditioning')
        source_proof=dict(split_upper=bound(norm_upper(ball['defect'])),
            conditioning_upper=bound(condition),selector_domain=spectral_domain(source),
            positive_resource_lower=bound(min(ball['after'][i,0].lower()for i in range(e.n))),
            desired_poststate_difference=bound(norm_upper(b.vector(actual)-b.vector({n:str(x)for n,x in old_states['current'].items()}))),
            trigger_margin=bound(arb(fmpq(str(spark)))),gradient_squared_margin=bound(arb(fmpq(str(gradient)))))
    # Exact poststate coordinates may have large denominators: retain their
    # exact strings once, compressed in the record, and use identities elsewhere.
    capture=dict(stage='fresh_postbeat_candidate_detection',ordinary_step_index=1,time='32',
        current=actual,reset=reset,graph_identity=content_id(source),
        stable_edge_weights={edge['edge_id']:'1'for edge in source['edges']},
        source_state_identity=content_id(dict(graph=source,current=actual,reset=reset)),
        reference_read_identity=content_id([[str(x)for x in fresh_event[name].entries()]for name in sorted(fresh_event)]),
        final_read_identity=content_id([[str(x)for x in fresh_final[name].entries()]for name in sorted(fresh_final)]),
        reset_read_identity=content_id([[str(x)for x in reset_read[name].entries()]for name in sorted(reset_read)]),
        occupied_ports=ports,qualified_parent='p',parent_members=after_basins['p'])
    return dict(source_graph=source,current_prestate=pre,reset_prestate=reset,
        prebeat_parent_basins=before_basins,
        prebeat_hybrid_already_true=bool(sum(x[0]**2 for x in before_rows['v'])<16 and min(-x[0]for x in before_rows['v'])<F(1,8)),
        source_step=source_proof,capture=capture,targets=targets,
        transferred_current=event_current,transferred_reset=target_reset,
        controls=dict(stale_parent_does_not_contain_v=True,predictor_continuity_differs=True,
                      prebeat_current_is_not_fresh=True,advancing_reset_would_change_it=True))


def run(positive_record):
    prepared=prepare();targets=prepared['targets'];t=targets['1'];old=positive_record['checks']
    need(t['graph']==old['targets']['1']['graph'],'different target graph requires new trap')
    need(prepared['transferred_reset']==old['targets']['1']['resources']['reset'],'reset evidence subject mismatch')
    need(all(targets[chi]['graph']==old['targets'][chi]['graph']for chi in ('1','-1')),'chiral graph mismatch')
    proof=old['trap'];history=[];snapshots={};first_gain=None
    with ctx.workprec(PRECISION):
        m=COSReference(t['graph'],'arb');C=m.vector(prepared['transferred_current'])
        center=m.vector(proof['center']);trace=arb(fmpq(proof['inverse_trace']))
        initial={chi:geometric_roster(target['graph'],compact_box(m,C),m.nodes)for chi,target in targets.items()}
        need(all(set(r)=={'p'}for r in initial.values()),'event-only gain')
        # Both target role reads are fresh. Reading reset does not advance it.
        for state in (prepared['transferred_current'],prepared['transferred_reset']):
            read=m.read(m.vector(state),m.I,eta=m.q(1,1024))
            need(all(x.is_finite()for x in read['current'].entries()),'target readmission')
        maximum_split=m.q(0);minimum=m.q(100);condition_max=m.q(0)
        for k in range(1,HORIZON+1):
            s=m.step(C,eta=m.q(1,1024),dt=m.q(32));C=s['after']
            split=norm_upper(s['defect']);lower=min(C[i,0].lower()for i in range(m.n))
            need(split<m.q(1,10**11) and lower>0,'target continuation domain')
            need(sum(C[i,0]for i in range(m.n)).contains(21),'charge enclosure')
            for H in (s['geometry'],m.I):
                read=m.read(C,H,eta=m.q(1,1024))
                need(all(x.is_finite()for x in read['current'].entries()),'final/restart read')
            hmax=(1+sum(s['geometry'][i,i]-1 for i in range(m.m))).upper()
            condition=hmax*(1+hmax*infnorm(m.Le));need(condition<10**12,'target conditioning')
            rosters={chi:geometric_roster(target['graph'],compact_box(m,C),m.nodes)for chi,target in targets.items()}
            gains={chi:len({a for a in r if a=='p' or a in t['module']})-1
                   if any(a in t['module']for a in r)else 0 for chi,r in rosters.items()}
            gain=all(x>=1 for x in gains.values())
            if gain and first_gain is None:first_gain=k
            if first_gain is not None:need(gain,'gain lost before entry')
            distance=norm_upper(C-center)*trace.sqrt();entry=distance<m.q(1,2**20)
            history.append(dict(step=k,minimum_resource=bound(lower)[0],split_upper=bound(split)[1],
                                qualified_basins=rosters,trap_distance_upper=bound(distance)[1]))
            if k in (1,42,128,512) or entry:snapshots[str(k)]={n:bound(C[i,0])for i,n in enumerate(m.nodes)}
            minimum=min(minimum,lower);maximum_split=max(maximum_split,split);condition_max=max(condition_max,condition.upper())
            if entry:break
        need(entry,'actual transferred state did not reach the trap within the declared cap')
        result=dict(first_gain_step=first_gain,certified_trap_entry_step=k,
            minimum_resource=bound(minimum),maximum_split=bound(maximum_split),
            maximum_condition=bound(condition_max),trap_distance_upper=bound(distance),
            observations=history,checkpoints=snapshots)
    # Serialize constructor Fractions as exact rationals; keep graphs only once
    # via the predecessor reference and byte-checked graph identities.
    prepared.pop('targets')
    return dict(status='positive_source_beat_to_organized_trap_conditional_research',
        prepared=prepared,actual_current_target=result,
        reset_reuse=dict(predecessor_role='reset',exact_state_unchanged=True,
            certified_trap_entry_step=old['roles']['reset']['certified_trap_entry_step'],
            evidence_digest=content_id(old['roles']['reset']),additional_reset_steps_executed=0),
        source_ordinary_steps=1,current_target_steps=k,research_event_count=1,
        reset_advanced_by_source_beat=False,conditional_scientific_completion_witness=True,
        native_steps=0,native_events=0,completed_spark=False,accepted_authority=False,
        SC1_closed=True,SC2_closed=False,
        SC2_remaining='scientific review and scoped constitutive/claim/debt adjudication; native work downstream')
