"""All twenty bounded A_PC deep layouts; exact source/pilot reuse, new allocations."""

import argparse
from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
from fractions import Fraction as Q
import json
import numpy as np

import p984d_apc_joint_successor as prior

j,h,f,b,r,o=prior.j,prior.h,prior.f,prior.b,prior.r,prior.o
SELF=b.HERE+'p984d_apc_full.py'
TEST=b.HERE+'test_p984d_apc_full.py'
PLAN=b.BASE+'P9-8.4d-APCFullPlan.md'
INPUTS=b.BASE+'P9-8.4d-APCFullInputs.json'
RESULTS=b.BASE+'P9-8.4d-APCFullResults.json'
REVIEW=b.BASE+'P9-8.4d-APCFullReview.md'


def predecessor():
    m,v=b.read(prior.INPUTS),b.read(prior.RESULTS)
    b.require(prior.check(m,v)['passed_cases']==1,'pilot is not complete')
    return m,v


def context(runtime,case,role):
    """The same exact stencil on each explicitly declared graph, not all graphs."""
    b.require(role in r.ROLES,'unknown history role')
    layouts=h.c.prior.construction.layouts()
    layout=next(v for v in layouts if v['id']==case['fixture_id'])
    b.require(case['request']['target_effective_degree']==layout['degree']
        and layout['degree'] in (59,66,73,94),'undeclared degree/layout')
    seed=r.state(runtime['expected_source']);target=r.independent_target(seed,case)
    graph=case['oracle']['target_graph'];state=getattr(target.inputs,role)
    b.require(not any(state.Z_4),'target carrier is not zero')
    high=o.IntervalRows(o.model_for(graph))
    B=np.array([[Q(int(high.B[i,k])) for k in range(high.B.cols)] for i in range(high.B.rows)],dtype=object)
    w=np.array(list(map(Q,state.W_A)),dtype=object);L=B@np.diag(w)@B.T
    initial=np.array([[Q(v),Q(0),Q(0)] for v in state.C],dtype=object)
    mass=Q(getattr(seed.inputs,role).C[seed.inputs.geometry.reference.graph.live_node_ids.index(case['request']['source_node_id'])])
    sites=[]
    for i,coeff in enumerate(((0,1,0),(0,0,1),(1,-1,-1)),1):
        k=graph['live_node_ids'].index(case['oracle']['event_id']+f'/satellite/{i}')
        sites.append(k);initial[k]=[mass*c for c in coeff]
    M=np.eye(len(initial),dtype=int).astype(object)+Q(b.DT)*(L@L)
    return dict(case=case,graph=graph,high=high,B=B,w=w,L=L,M=M,initial=initial,
        first=M@initial,second=M@M@initial,sites=sites,mass=mass,role=role)


def constraints(runtime,case,retained=None):
    lower=[];upper=[];represented_lower=[];nominal=[];certs=[]
    for role in r.ROLES:
        ctx=context(runtime,case,role)
        for represented in (False,True):
            cert=dict(role=role,represented=represented,constraints=[])
            if retained is None:
                enc=f.enclose(ctx,represented=represented)
                b.require(enc['second_error'] is not None,'second-step chart excluded')
            else:
                saved=retained[len(certs)]
                b.require(saved['role']==role and saved['represented'] is represented
                    and len(saved['constraints'])==2*len(ctx['initial']),'constraint roster drift')
            for stage,key in ((1,'first'),(2,'second')):
                for i,(node,coeff) in enumerate(zip(ctx['graph']['live_node_ids'],ctx[key],strict=True)):
                    if retained is None:
                        error=enc['first_error' if stage==1 else 'second_error'][i]
                        lo,hi=(f.endpoint(error,k) for k in (0,1))
                    else:lo,hi=map(Q,saved['constraints'][(stage-1)*len(ctx['initial'])+i]['correction'])
                    b.require(lo<=hi,'reversed bound')
                    cert['constraints'].append(dict(stage=stage,node=node,affine=list(map(str,coeff)),correction=[str(lo),str(hi)]))
                    (represented_lower if represented else lower).append([coeff[0]+lo,coeff[1],coeff[2]])
                    if represented:upper.append([coeff[0]+hi,coeff[1],coeff[2]])
            certs.append(cert)
        coefficients=ctx['initial']
        for _ in range(10):
            coefficients=ctx['M']@coefficients;nominal.extend(list(v) for v in coefficients)
    if retained is not None:b.require(certs==retained,'exact stencil/interval roster drift')
    inner=j.polygon(lower);joint=j.polygon(nominal,j.polygon(upper,inner))
    return dict(certificates=certs,two_step_inner_polygon=[list(map(str,p)) for p in inner],
        represented_sufficient_polygon=[list(map(str,p)) for p in j.polygon(represented_lower)],
        represented_necessary_polygon=[list(map(str,p)) for p in j.polygon(upper)],
        selection_polygon=[list(map(str,p)) for p in joint],selection=j.select(joint),uniform_native_domain=False)


def template(seed,old):
    case=h.c.bind_case(seed,old)
    case['request']['operation_id']+='-full-joint-history31'
    layout=next(v for v in h.c.prior.construction.layouts() if v['id']==case['fixture_id'])
    case['oracle']=h.c.prior.construction.previous.target_oracle(seed.to_payload(),case,case['request'],layout)
    case['changes_from_frozen']=['retained_initial_current_history31','layout_derived_allocation']
    return case


def selected(seed,case,derived):
    case=deepcopy(case);shares=[float(Q(v)) for v in derived['selection']['shares']]
    case['request'].update(resource_distribution=shares,operation_id=case['request']['operation_id']+'-selected')
    case['oracle']['event_identity']['resource_distribution']=shares
    layout=next(v for v in h.c.prior.construction.layouts() if v['id']==case['fixture_id'])
    case['oracle']=h.c.prior.construction.previous.target_oracle(seed.to_payload(),case,case['request'],layout)
    case['independent_whole_chart']=o.whole_chart(case['oracle']['target_graph'])
    case['subject_kind']='full_deep_joint_history_allocation_witness'
    return case


def derive_job(job):
    runtime,case=job
    derived=constraints(runtime,case)
    print(case['case_id'],'selected',derived['selection']['shares'],flush=True)
    return dict(case_id=case['case_id'],template=case,derivation=derived,
        case=selected(r.state(runtime['expected_source']),case,derived))


def prepare(workers=3):
    old,result=predecessor();base=deepcopy(old['runtime_manifest']);seed=r.state(base['expected_source'])
    templates=[template(seed,c) for c in b.read(h.c.prior.INPUTS)['cases'] if c['case_id']!=h.c.PILOT]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        selections=list(pool.map(derive_job,[(base,c) for c in templates]))
    oldcases=b.read(h.c.prior.INPUTS)['cases']
    by_id={v['case_id']:v['case'] for v in selections};by_id[h.c.PILOT]=base['cases'][0]
    runtime=b.seal(dict(base,cases=[by_id[c['case_id']] for c in oldcases]))
    paths={v['path'] for v in old['source_bindings']}|{SELF,TEST,PLAN,prior.INPUTS,prior.RESULTS,prior.SELF,h.c.prior.INPUTS}
    return b.seal(dict(schema='p984d-apc-full-inputs-v1',source_bindings=b.bind(sorted(paths)),
        pilot_input_digest=old['record_digest'],pilot_result_digest=result['record_digest'],
        runtime_manifest=runtime,selections=selections,reused_case_id=h.c.PILOT,
        cases_required=20,history_cells_required=40,target_steps_per_role=10,new_source_steps=0,
        uniform_native_domain=False,user_accepted=False,aggregate_closed=False))


def check_manifest(m,*,numerics=False):
    b.check_digest(m);b.check_bindings(m['source_bindings']);old,result=predecessor()
    wanted={v['path'] for v in old['source_bindings']}|{SELF,TEST,PLAN,prior.INPUTS,prior.RESULTS,prior.SELF,h.c.prior.INPUTS}
    b.require(m['schema']=='p984d-apc-full-inputs-v1' and m['source_bindings']==b.bind(sorted(wanted))
        and m['pilot_input_digest']==old['record_digest'] and m['pilot_result_digest']==result['record_digest']
        and m['reused_case_id']==h.c.PILOT and m['cases_required']==20 and m['history_cells_required']==40
        and m['target_steps_per_role']==10 and m['new_source_steps']==0
        and all(m[k] is False for k in ('uniform_native_domain','user_accepted','aggregate_closed')),'full input scope drift')
    base=old['runtime_manifest'];seed=r.state(base['expected_source']);oldcases=b.read(h.c.prior.INPUTS)['cases']
    b.require([v['case_id'] for v in m['selections']]==[v['case_id'] for v in oldcases if v['case_id']!=h.c.PILOT],
        'full selection roster drift')
    by_id={h.c.PILOT:base['cases'][0]}
    for v,oldcase in zip(m['selections'],[v for v in oldcases if v['case_id']!=h.c.PILOT],strict=True):
        case=template(seed,oldcase);b.require(v['template']==case,'template identity drift')
        derived=constraints(base,case,None if numerics else v['derivation']['certificates'])
        b.require(derived==v['derivation'] and v['case']==selected(seed,case,derived),'derived target drift')
        by_id[v['case_id']]=v['case']
    b.require(m['runtime_manifest']==b.seal(dict(base,cases=[by_id[c['case_id']] for c in oldcases])),
        'full source, pilot reuse or runtime drift')


def run_case(job):
    runtime,case=job
    with b.exact_backend(b.ExactBackend.FLINT),h.prior.previous.data_adapter(runtime):
        row=r.execute_case(r.state(runtime['expected_source']),case)
    print(case['case_id'],row['outcome'],row['first_failure'],flush=True)
    return row


def run(m,workers=3):
    check_manifest(m);runtime=m['runtime_manifest']
    jobs=[(runtime,c) for c in runtime['cases'] if c['case_id']!=h.c.PILOT]
    with ProcessPoolExecutor(max_workers=workers) as pool:rows=list(pool.map(run_case,jobs))
    exe=b.seal(dict(manifest_digest=runtime['record_digest'],shared=runtime['shared'],cases=rows,
        native_runtime_executed=True,user_accepted=False,aggregate_closed=False))
    old=b.read(prior.RESULTS);pilot=h.prior.previous.expand(old['execution'])['cases'][0]
    return b.seal(dict(schema='p984d-apc-full-results-v1',manifest_digest=m['record_digest'],
        execution=h.prior.previous.compact(exe),reuse=dict(path=prior.RESULTS,record_digest=old['record_digest'],
            case_id=h.c.PILOT,case_digest=b.digest(pilot)),user_accepted=False,aggregate_closed=False))


def materialize(m,v):
    exe=h.prior.previous.expand(v['execution']);b.check_digest(exe)
    old=b.read(prior.RESULTS);pilot=h.prior.previous.expand(old['execution'])['cases'][0]
    b.require(v['reuse']==dict(path=prior.RESULTS,record_digest=old['record_digest'],case_id=h.c.PILOT,
        case_digest=b.digest(pilot)),'pilot provenance drift')
    expected=[c['case_id'] for c in m['runtime_manifest']['cases'] if c['case_id']!=h.c.PILOT]
    b.require([c['case_id'] for c in exe['cases']]==expected,'new execution roster drift')
    rows={c['case_id']:c for c in exe['cases']};rows[h.c.PILOT]=pilot
    return b.seal(dict(exe,cases=[rows[c['case_id']] for c in m['runtime_manifest']['cases']]))


def _check(m,v,*,numerics=False,consumers=True):
    check_manifest(m,numerics=numerics);b.check_digest(v)
    b.require(v['schema']=='p984d-apc-full-results-v1' and v['manifest_digest']==m['record_digest']
        and v['user_accepted'] is False and v['aggregate_closed'] is False,'full result scope drift')
    runtime=m['runtime_manifest'];exe=materialize(m,v)
    b.require(exe['shared']==runtime['shared'],'full source execution drift')
    for case,row in zip(runtime['cases'],exe['cases'],strict=True):
        b.require(row['actual_case']==case and row['input_digest']==b.digest(case)
            and row['coverage_binding']==case['coverage_binding'] and type(row['case_passed']) is bool
            and type(row['event_committed']) is bool and row['user_accepted'] is False
            and row['aggregate_closed'] is False,'actual case/scope drift')
        if row['case_passed']:
            b.require(row['event_committed'] and row['first_failure'] is None
                and row['outcome']=='passed_named_case'
                and [(v['role'],v['index']) for v in row['continuation']]==[(role,i) for role in r.ROLES for i in range(1,11)]
                and set(row['final_reads'])==set(r.ROLES),'incomplete success schedule')
            for stage,count in (('entry_effects',8),('final_effects',2)):
                b.require(set(row[stage])==set(r.ROLES) and all(len(controls)==count
                    and all(v['minimum_margin_ratio']>1 and v['exact_effect_lower']>0 for v in controls.values())
                    for controls in row[stage].values()),'effect separation scope drift')
        else:
            b.require(row['first_failure'] is not None,'missing failure')
            if 'event' not in row:
                b.require(not row['event_committed'] and not row['continuation'],'false native credit')
            elif row['event_committed'] and consumers:
                target=r.check_event(r.state(runtime['expected_source']),case,row['event'],numerics=numerics)
                schedule=[(role,i) for role in r.ROLES for i in range(1,11)]
                b.require([(v['role'],v['index']) for v in row['continuation']]==schedule[:len(row['continuation'])],'partial step roster')
                for role in r.ROLES:
                    before=r.role_input(target.inputs,role,dt=b.DT)
                    for record in (v for v in row['continuation'] if v['role']==role):
                        before=r.check_step(before,record['step'],numerics=numerics)
            elif not row['event_committed']:b.require(not row['continuation'],'rejected event with continuation')
    if consumers:
        with h.prior.previous.data_adapter(runtime):r.validate(runtime,exe,numerics=numerics)
    rows=exe['cases'];passed=sum(v['case_passed'] for v in rows)
    return dict(family='A_PC',status='full_coupled_execution_pending_acceptance' if passed==20 else 'incomplete_full_coupled_campaign',
        cases_required=20,attempted_cases=20,unattempted_cases=0,passed_cases=passed,
        native_cases=sum('event' in v for v in rows),committed_events=sum(v['event_committed'] for v in rows),
        target_steps=sum(len(v['continuation']) for v in rows),final_reads=sum(len(v['final_reads']) for v in rows),
        required_cells=40,passing_pending_cells=2*passed,accepted_cells=0,new_source_steps=0,
        newly_executed_cases=19,reused_cases=1,reused_target_steps=20,
        native_trajectories_rerun=False,interval_equations_recomputed=numerics,
        verification_level='retained_consumer_integrity' if consumers else 'authenticated_structure',
        failures=[dict(case_id=v['case_id'],first_failure=v['first_failure']) for v in rows if not v['case_passed']],
        uniform_native_domain=False,user_accepted=False,aggregate_closed=False)


def status(m,v):
    """Pinned structure/counts for display; not another 400-step consumer audit."""
    return _check(m,v,consumers=False)


def check(m,v,*,numerics=False):
    return _check(m,v,numerics=numerics)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=('prepare','run','check'))
    parser.add_argument('--workers',type=int,default=3);parser.add_argument('--recheck-numerics',action='store_true');args=parser.parse_args()
    b.require(1<=args.workers<=4 and (not args.recheck_numerics or args.action=='check'),'invalid run/check options')
    path={'prepare':INPUTS,'run':RESULTS}.get(args.action)
    if path:b.require(not (b.ROOT/path).exists(),'refuse overwrite of retained record')
    if args.action=='prepare':
        m=prepare(args.workers);b.write_new(INPUTS,m);print('Prepared 19 new layouts and exact pilot reuse')
    else:
        m=b.read(INPUTS);v=run(m,args.workers) if args.action=='run' else b.read(RESULTS)
        if path:b.write_new(path,v)
        print(json.dumps(check(m,v,numerics=args.recheck_numerics),indent=2))


if __name__=='__main__':main()
