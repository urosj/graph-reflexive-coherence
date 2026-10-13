"""Coupled A_PC history/share constraints, then one separately bound witness."""

import argparse
from copy import deepcopy
from fractions import Fraction as Q
from itertools import product
import json
import math

import p984d_apc_history as h
import p984d_apc_feasibility as f

b,r,o=h.b,h.r,h.o
SELF=b.HERE+'p984d_apc_joint.py'
TEST=b.HERE+'test_p984d_apc_joint.py'
PLAN=b.BASE+'P9-8.4d-APCJointFeasibility.md'
DERIVATION=b.BASE+'P9-8.4d-APCJointConstraints.json'
INPUTS=b.BASE+'P9-8.4d-APCJointWitnessInputs.json'
RESULTS=b.BASE+'P9-8.4d-APCJointWitnessResults.json'
REVIEW=b.BASE+'P9-8.4d-APCJointWitnessReview.md'


def predecessor():
    manifest,result=b.read(h.INPUTS),b.read(h.RESULTS)
    summary=h.check(manifest,result)
    b.require(summary['source_eligible'] and summary['passed_cases']==0,'history predecessor changed')
    return manifest,result


def paths(manifest):
    return {v['path'] for v in manifest['source_bindings']}|{
        SELF,TEST,PLAN,h.SELF,h.TEST,h.INPUTS,h.RESULTS,f.SELF}


def polygon(rows,poly=None):
    poly=[(Q(0),Q(0)),(Q(1),Q(0)),(Q(0),Q(1))] if poly is None else list(poly)
    for row in rows:
        if not poly:break
        a,x,y=map(Q,row)
        poly=f.clip(poly,(x,y),a)
    return poly


def edges(poly):
    # CCW polygons: these affine functions are positive in the interior.
    return [(ax*by-ay*bx,ay-by,bx-ax)
        for (ax,ay),(bx,by) in zip(poly,poly[1:]+poly[:1])]


def margin(poly,point):
    return min((a+x*point[0]+y*point[1])/(abs(x)+abs(y)) for a,x,y in edges(poly))


def select(poly):
    b.require(len(poly)>=3,'empty joint allocation region')
    center=tuple(sum(p[k] for p in poly)/len(poly) for k in (0,1))
    for power in range(6,13):
        den=2**power
        coordinates=[sorted({Q(math.floor(z*den),den),Q(math.ceil(z*den),den)}) for z in center]
        candidates=[(margin(poly,p),p) for p in product(*coordinates) if margin(poly,p)>0]
        if candidates:
            best=sorted(candidates,key=lambda v:(-v[0],v[1]))[0]
            x,y=best[1]
            return dict(shares=list(map(str,(x,y,1-x-y))),denominator=den,
                centroid=list(map(str,center)),minimum_share_margin=str(best[0]),
                rule='first_dyadic_centroid_neighbors_strictly_inside_then_max_margin_lexicographic')
    raise ValueError('no selected dyadic witness; do not silently broaden search')


def derive():
    manifest,old=predecessor();runtime=old['runtime_manifest']
    certificates=[];lower=[];represented_lower=[];represented_upper=[];baseline=[]
    for role in r.ROLES:
        ctx=f.context(runtime,role=role)
        for represented in (False,True):
            enclosure=f.enclose(ctx,represented=represented)
            b.require(enclosure['second_error'] is not None,'first-step domain excluded')
            rows=[]
            for stage,key in ((1,'first'),(2,'second')):
                for node,coeff,error in zip(ctx['graph']['live_node_ids'],ctx[key],
                        enclosure['first_error' if stage==1 else 'second_error'],strict=True):
                    lo,hi=(f.endpoint(error,i) for i in (0,1))
                    rows.append(dict(stage=stage,node=node,affine=list(map(str,coeff)),
                        correction=[str(lo),str(hi)]))
                    (represented_lower if represented else lower).append([coeff[0]+lo,coeff[1],coeff[2]])
                    if represented:represented_upper.append([coeff[0]+hi,coeff[1],coeff[2]])
            certificates.append(dict(role=role,represented=represented,constraints=rows))
        coefficients=ctx['initial']
        for _ in range(10):
            coefficients=ctx['M']@coefficients
            baseline.extend(list(row) for row in coefficients)
    resource=polygon(lower);joint=polygon(baseline,polygon(represented_upper,resource))
    return b.seal(dict(schema='p984d-apc-joint-constraints-v1',source_bindings=b.bind(sorted(paths(manifest))),
        history_input_digest=manifest['record_digest'],history_result_digest=old['record_digest'],
        source_state_digest=r.state(runtime['expected_source']).scientific_digest,
        case_id=h.c.PILOT,certificates=certificates,
        two_step_inner_polygon=[list(map(str,p)) for p in resource],
        represented_necessary_polygon=[list(map(str,p)) for p in polygon(represented_upper)],
        represented_sufficient_polygon=[list(map(str,p)) for p in polygon(represented_lower)],
        frozen_history_ten_step_intersection=[list(map(str,p)) for p in joint],
        selection=select(joint),source_steps=0,native_target_steps=0,topology_events=0,
        scope='two_step_resource_bounds_on_chart_plus_frozen_history_ten_step_selection_aid',
        uniform_native_domain=False,user_accepted=False,aggregate_closed=False))


def check_derivation(value,*,numerics=False):
    b.check_digest(value);b.check_bindings(value['source_bindings'])
    manifest,old=predecessor();runtime=old['runtime_manifest']
    b.require(value['schema']=='p984d-apc-joint-constraints-v1'
        and value['source_bindings']==b.bind(sorted(paths(manifest)))
        and value['history_input_digest']==manifest['record_digest']
        and value['history_result_digest']==old['record_digest']
        and value['source_state_digest']==r.state(runtime['expected_source']).scientific_digest
        and value['case_id']==h.c.PILOT and value['scope']=='two_step_resource_bounds_on_chart_plus_frozen_history_ten_step_selection_aid'
        and all(value[k] is False for k in ('uniform_native_domain','user_accepted','aggregate_closed'))
        and all(type(value[k]) is int and value[k]==0 for k in ('source_steps','native_target_steps','topology_events')),
        'joint derivation source/scope drift')
    b.require([(v['role'],v['represented']) for v in value['certificates']]==
        [(role,mode) for role in r.ROLES for mode in (False,True)],'joint role/certificate roster')
    lower=[];represented_lower=[];represented_upper=[];baseline=[]
    for role in r.ROLES:
        ctx=f.context(runtime,role=role)
        for cert in (v for v in value['certificates'] if v['role']==role):
            wanted=[(stage,i) for stage in (1,2) for i in range(len(ctx['initial']))]
            b.require(len(cert['constraints'])==len(wanted),'joint constraint roster')
            for row,(stage,i) in zip(cert['constraints'],wanted,strict=True):
                coeff=ctx['first' if stage==1 else 'second'][i];lo,hi=map(Q,row['correction'])
                b.require(row['stage']==stage and row['node']==ctx['graph']['live_node_ids'][i]
                    and row['affine']==list(map(str,coeff)) and lo<=hi,'joint coefficient/interval drift')
                (represented_lower if cert['represented'] else lower).append([coeff[0]+lo,coeff[1],coeff[2]])
                if cert['represented']:represented_upper.append([coeff[0]+hi,coeff[1],coeff[2]])
        coefficients=ctx['initial']
        for _ in range(10):
            coefficients=ctx['M']@coefficients;baseline.extend(list(row) for row in coefficients)
    resource=polygon(lower);joint=polygon(baseline,polygon(represented_upper,resource))
    b.require(value['two_step_inner_polygon']==[list(map(str,p)) for p in resource]
        and value['represented_necessary_polygon']==[list(map(str,p)) for p in polygon(represented_upper)]
        and value['represented_sufficient_polygon']==[list(map(str,p)) for p in polygon(represented_lower)]
        and value['frozen_history_ten_step_intersection']==[list(map(str,p)) for p in joint]
        and value['selection']==select(joint),'joint polygon/selection drift')
    if numerics:b.require(value==derive(),'joint interval equations drift')
    return dict(selection=value['selection'],inner_vertices=len(resource),native_events=0,
        interval_equations_recomputed=numerics,uniform_native_domain=False)


def selected_case(derivation,old):
    runtime=old['runtime_manifest'];seed=r.state(runtime['expected_source'])
    case=deepcopy(next(v for v in runtime['cases'] if v['case_id']==h.c.PILOT))
    shares=[float(Q(x)) for x in derivation['selection']['shares']]
    case['request'].update(resource_distribution=shares,operation_id=case['request']['operation_id']+'-joint-allocation')
    case['oracle']['event_identity']['resource_distribution']=shares
    case['oracle']=h.c.prior.construction.previous.target_oracle(seed.to_payload(),case,case['request'],
        next(v for v in h.c.prior.construction.layouts() if v['id']==case['fixture_id']))
    case['independent_whole_chart']=o.whole_chart(case['oracle']['target_graph'])
    case['changes_from_frozen']=['retained_history63_source','derived_dyadic_resource_allocation','fresh_event_identity']
    case['subject_kind']='joint_history_allocation_pilot_not_all_layouts'
    return case


def prepare():
    derivation=b.read(DERIVATION);check_derivation(derivation)
    manifest,old=predecessor();runtime=deepcopy(old['runtime_manifest'])
    runtime['cases']=[selected_case(derivation,old)];runtime=b.seal(runtime)
    return b.seal(dict(schema='p984d-apc-joint-inputs-v1',derivation_digest=derivation['record_digest'],
        source_bindings=b.bind(sorted(paths(manifest)|{DERIVATION})),runtime_manifest=runtime,
        source_reused=True,new_source_steps=0,target_steps_per_role=10,cases_required=1,
        whole_family_cases_required=20,whole_family_history_cells_required=40,
        history_roles=list(r.ROLES),user_accepted=False,aggregate_closed=False))


def check_manifest(manifest):
    b.check_digest(manifest);b.check_bindings(manifest['source_bindings'])
    b.require(manifest==prepare(),'joint witness declaration drift')


def run(manifest):
    check_manifest(manifest);runtime=manifest['runtime_manifest']
    with b.exact_backend(b.ExactBackend.FLINT),h.prior.previous.data_adapter(runtime):
        row=r.execute_case(r.state(runtime['expected_source']),runtime['cases'][0])
    print(row['outcome'],row['first_failure'],flush=True)
    execution=b.seal(dict(manifest_digest=runtime['record_digest'],shared=runtime['shared'],cases=[row],
        native_runtime_executed=True,user_accepted=False,aggregate_closed=False))
    return b.seal(dict(schema='p984d-apc-joint-results-v1',manifest_digest=manifest['record_digest'],
        execution=h.prior.previous.compact(execution),user_accepted=False,aggregate_closed=False))


def check(manifest,result,*,numerics=False):
    check_manifest(manifest);b.check_digest(result)
    b.require(result['schema']=='p984d-apc-joint-results-v1' and result['manifest_digest']==manifest['record_digest']
        and result['user_accepted'] is False and result['aggregate_closed'] is False,'joint result scope drift')
    runtime=manifest['runtime_manifest'];execution=h.prior.previous.expand(result['execution'])
    b.require(execution['shared']==runtime['shared'] and len(execution['cases'])==1,'joint source/case drift')
    row=execution['cases'][0]
    b.require(row['actual_case']==runtime['cases'][0],'joint actual subject drift')
    if row['first_failure'] and row['first_failure']['stage']=='independent_preflight':
        b.require('event' not in row and not row['event_committed'] and row['continuation']==[],'false native credit')
    with h.prior.previous.data_adapter(runtime):r.validate(runtime,execution,numerics=numerics)
    if not row['case_passed'] and 'event' in row:
        # The frozen validator skips incomplete rows. Verify partial execution
        # before reporting a committed event or a successful native step.
        b.require(row['event_committed'] is True and not row['final_reads']
            and not row['final_effects'],'unsupported partial execution claim')
        target=r.check_event(r.state(runtime['expected_source']),row['actual_case'],row['event'],numerics=numerics)
        schedule=[(role,i) for role in r.ROLES for i in range(1,11)]
        b.require([(v['role'],v['index']) for v in row['continuation']]==schedule[:len(row['continuation'])],
            'partial continuation schedule drift')
        for role in r.ROLES:
            before=r.role_input(target.inputs,role,dt=b.DT)
            for record in (v for v in row['continuation'] if v['role']==role):
                before=r.check_step(before,record['step'],numerics=numerics)
    if numerics and row['case_passed']:
        b.require(row['predictions']==r.preflight(r.independent_target(r.state(runtime['expected_source']),runtime['cases'][0])),
            'joint independent preflight drift')
    return dict(status='positive_joint_witness_pending_acceptance' if row['case_passed'] else 'joint_witness_held',
        family='A_PC',source_reused=True,new_source_steps=0,attempted_cases=1,native_cases=int('event' in row),
        committed_events=int(row['event_committed']),passed_cases=int(row['case_passed']),
        target_steps=len(row['continuation']),final_reads=len(row['final_reads']),
        passing_pending_cells=2*int(row['case_passed']),accepted_cells=0,required_cells=40,
        unattempted_cases=19,first_failure=row['first_failure'],
        native_trajectories_rerun=False,interval_equations_recomputed=numerics,
        uniform_native_domain=False,aggregate_closed=False,user_accepted=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('derive','check-derivation','prepare','run','check'))
    parser.add_argument('--recheck-numerics',action='store_true');args=parser.parse_args()
    b.require(not args.recheck_numerics or args.action.startswith('check'),'recheck requires check')
    destination={'derive':DERIVATION,'prepare':INPUTS,'run':RESULTS}.get(args.action)
    if destination:b.require(not (b.ROOT/destination).exists(),'refuse to overwrite retained evidence')
    if args.action in ('derive','check-derivation'):
        value=derive() if args.action=='derive' else b.read(DERIVATION)
        if destination:b.write_new(destination,value)
        summary=check_derivation(value,numerics=args.recheck_numerics)
    elif args.action=='prepare':
        value=prepare();b.write_new(INPUTS,value);summary=dict(preregistered=True,selection=b.read(DERIVATION)['selection'])
    else:
        manifest=b.read(INPUTS);value=run(manifest) if args.action=='run' else b.read(RESULTS)
        if destination:b.write_new(destination,value)
        summary=check(manifest,value,numerics=args.recheck_numerics)
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
