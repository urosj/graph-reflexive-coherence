"""Stronger-history successor of the coupled A_PC allocation witness."""

import argparse
from copy import deepcopy
from dataclasses import replace
from fractions import Fraction as Q
import json

import p984d_apc_joint as j

h,f,b,r,o=j.h,j.f,j.b,j.r,j.o
SELF=b.HERE+'p984d_apc_joint_successor.py'
TEST=b.HERE+'test_p984d_apc_joint_successor.py'
PLAN=b.BASE+'P9-8.4d-APCJointSuccessorPlan.md'
INPUTS=b.BASE+'P9-8.4d-APCJointSuccessorInputs.json'
RESULTS=b.BASE+'P9-8.4d-APCJointSuccessorResults.json'
REVIEW=j.REVIEW


def initial():
    before=h.initial()
    return replace(before,current=replace(before.current,
        W_A=tuple(float(Q(w)-Q(1,64)) for w in before.current.W_A)))


def paths():
    return {v['path'] for v in b.read(j.INPUTS)['source_bindings']}|{
        SELF,TEST,PLAN,j.INPUTS,j.RESULTS}


def constraints(runtime,retained=None):
    """Recompute exact stencils; reuse authenticated intervals only in check mode."""
    lower=[];upper=[];represented_lower=[];nominal=[];certs=[]
    for role in r.ROLES:
        ctx=f.context(runtime,role=role)
        for represented in (False,True):
            cert=dict(role=role,represented=represented,constraints=[])
            if retained is None:
                enc=f.enclose(ctx,represented=represented)
                b.require(enc['second_error'] is not None,'second-step chart excluded')
            else:
                saved=retained[len(certs)]
                b.require(saved['role']==role and saved['represented'] is represented,
                    'constraint role/mode drift')
                b.require(len(saved['constraints'])==2*len(ctx['initial']),'constraint count drift')
            for stage,key in ((1,'first'),(2,'second')):
                for i,(node,coeff) in enumerate(zip(ctx['graph']['live_node_ids'],ctx[key],strict=True)):
                    if retained is None:
                        error=enc['first_error' if stage==1 else 'second_error'][i]
                        lo,hi=(f.endpoint(error,k) for k in (0,1))
                    else:lo,hi=map(Q,saved['constraints'][(stage-1)*len(ctx['initial'])+i]['correction'])
                    b.require(lo<=hi,'reversed correction bound')
                    cert['constraints'].append(dict(stage=stage,node=node,
                        affine=list(map(str,coeff)),correction=[str(lo),str(hi)]))
                    (represented_lower if represented else lower).append([coeff[0]+lo,coeff[1],coeff[2]])
                    if represented:upper.append([coeff[0]+hi,coeff[1],coeff[2]])
            certs.append(cert)
        coefficients=ctx['initial']
        for _ in range(10):
            coefficients=ctx['M']@coefficients;nominal.extend(list(v) for v in coefficients)
    if retained is not None:b.require(certs==retained,'constraint equation drift')
    inner=j.polygon(lower);joint=j.polygon(nominal,j.polygon(upper,inner))
    return dict(certificates=certs,two_step_inner_polygon=[list(map(str,p)) for p in inner],
        represented_sufficient_polygon=[list(map(str,p)) for p in j.polygon(represented_lower)],
        represented_necessary_polygon=[list(map(str,p)) for p in j.polygon(upper)],
        selection_polygon=[list(map(str,p)) for p in joint],selection=j.select(joint),
        uniform_native_domain=False)


def runtime_for(seed,shared,independent):
    old=deepcopy(b.read(h.RESULTS)['runtime_manifest'])
    template=next(v for v in old['cases'] if v['case_id']==h.c.PILOT)
    template['request']['operation_id']+='-joint-history31'
    case=h.c.bind_case(seed,template)
    case['changes_from_frozen']=['initial_current_history31','derived_dyadic_allocation']
    return b.seal(dict(initial_inputs=initial().to_payload(),nominal_source=independent['nominal_source'],
        expected_source=seed.to_payload(),shared=shared,cases=[case],user_accepted=False,aggregate_closed=False))


def prepare():
    j.check(b.read(j.INPUTS),b.read(j.RESULTS))
    seed,shared,independent,read=h.source(initial())
    trigger=h.eligibility(seed,read)
    b.require(trigger['native_eligible'],'stronger-history source not eligible')
    runtime=runtime_for(seed,shared,independent)
    derived=constraints(runtime)
    case=j.selected_case(derived,dict(runtime_manifest=runtime))
    case['changes_from_frozen']=['initial_current_history31','derived_dyadic_allocation','fresh_event_identity']
    runtime=b.seal(dict(runtime,cases=[case]))
    return b.seal(dict(schema='p984d-apc-joint-successor-inputs-v1',source_bindings=b.bind(sorted(paths())),
        predecessor_digest=b.read(j.RESULTS)['record_digest'],independent_source=independent,
        source_eligibility=trigger,derivation=derived,runtime_manifest=runtime,
        initial_history_mean='31/32',new_source_steps=1,target_steps_per_role=10,
        cases_required=1,whole_family_history_cells_required=40,user_accepted=False,aggregate_closed=False))


def check_manifest(m,*,numerics=False):
    b.check_digest(m);b.check_bindings(m['source_bindings'])
    b.require(m['schema']=='p984d-apc-joint-successor-inputs-v1'
        and m['source_bindings']==b.bind(sorted(paths()))
        and m['predecessor_digest']==b.read(j.RESULTS)['record_digest']
        and m['initial_history_mean']=='31/32' and m['new_source_steps']==1
        and m['target_steps_per_role']==10 and m['cases_required']==1
        and m['whole_family_history_cells_required']==40
        and m['user_accepted'] is False and m['aggregate_closed'] is False,'successor input scope drift')
    runtime=m['runtime_manifest'];b.check_digest(runtime)
    seed=r.state(runtime['expected_source']);shared=runtime['shared']
    b.require(shared['actual_source']==seed.to_payload(),'source image mismatch')
    after=r.check_step(initial(),shared['source_step'],numerics=numerics)
    b.require(seed.inputs==replace(after,dt=0),'source ordinary-step mismatch')
    independent=m['independent_source'];nominal=r.state(independent['nominal_source'])
    b.require(b.authority_payload(nominal.inputs.current)=={k:independent['output'][k] for k in ('C','W_A','Z_4')}
        and nominal.inputs.reset==initial().reset,'independent source authority mismatch')
    for key,limit in (('C',o.RESOURCE_ERROR),('W_A',o.HISTORY_ERROR),('Z_4',o.CARRIER_ERROR)):
        b.require(max(abs(Q(x)-Q(y)) for x,y in zip(getattr(seed.inputs.current,key),
            getattr(nominal.inputs.current,key),strict=True))<limit,'independent source mismatch')
    if numerics:
        before=initial();proof=o.check_step(before.geometry.reference.graph.port_graph.to_payload(),
            before.current.C,before.current.W_A,before.current.Z_4,independent['output'])
        b.require(independent['errors']=={k:str(v) for k,v in proof['errors'].items()},'source proof drift')
    trigger=m['source_eligibility'];r.check_read(seed.inputs,trigger['fresh_read'],numerics=numerics)
    cert={k:trigger[k] for k in ('source_state_digest','gradient_intervals','squared_norm_interval',
        'strict_upper_required','gradient_gate_passes','gradient_gate_excluded')}
    b.require(trigger['native_eligible'] and trigger==h.eligibility(seed,trigger['fresh_read'],
        None if numerics else cert),'source eligibility drift')
    base=runtime_for(seed,shared,independent)
    derived=constraints(base,None if numerics else m['derivation']['certificates'])
    b.require(derived==m['derivation'],'coupled constraints drift')
    selected=j.selected_case(derived,dict(runtime_manifest=base))
    selected['changes_from_frozen']=['initial_current_history31','derived_dyadic_allocation','fresh_event_identity']
    b.require(runtime==b.seal(dict(base,cases=[selected])),'selected target identity drift')


def run(m):
    check_manifest(m);runtime=m['runtime_manifest']
    with b.exact_backend(b.ExactBackend.FLINT),h.prior.previous.data_adapter(runtime):
        row=r.execute_case(r.state(runtime['expected_source']),runtime['cases'][0])
    print(row['outcome'],row['first_failure'],flush=True)
    execution=b.seal(dict(manifest_digest=runtime['record_digest'],shared=runtime['shared'],cases=[row],
        native_runtime_executed=True,user_accepted=False,aggregate_closed=False))
    return b.seal(dict(schema='p984d-apc-joint-successor-results-v1',manifest_digest=m['record_digest'],
        execution=h.prior.previous.compact(execution),user_accepted=False,aggregate_closed=False))


def check(m,result,*,numerics=False):
    check_manifest(m,numerics=numerics);b.check_digest(result)
    b.require(result['schema']=='p984d-apc-joint-successor-results-v1'
        and result['manifest_digest']==m['record_digest'] and result['user_accepted'] is False
        and result['aggregate_closed'] is False,'successor result drift')
    runtime=m['runtime_manifest'];exe=h.prior.previous.expand(result['execution'])
    b.require(exe['shared']==runtime['shared'] and len(exe['cases'])==1,'successor execution roster')
    row=exe['cases'][0];b.require(row['actual_case']==runtime['cases'][0],'successor actual case drift')
    with h.prior.previous.data_adapter(runtime):r.validate(runtime,exe,numerics=numerics)
    # Frozen runtime validator skips incomplete rows. Authenticate their actual
    # event and each retained step before granting even partial native credit.
    if not row['case_passed']:
        b.require(not row['final_reads'] and not row['final_effects'],'unvalidated partial final reads')
        if 'event' not in row:
            b.require(not row['event_committed'] and not row['continuation'],'false native credit')
        else:
            b.require(row['event_committed'] is True,'failed event needs separate rejection checker')
            target=r.check_event(r.state(runtime['expected_source']),row['actual_case'],row['event'],numerics=numerics)
            schedule=[(role,i) for role in r.ROLES for i in range(1,11)]
            b.require([(v['role'],v['index']) for v in row['continuation']]==schedule[:len(row['continuation'])],
                'partial schedule drift')
            for role in r.ROLES:
                before=r.role_input(target.inputs,role,dt=b.DT)
                for record in (v for v in row['continuation'] if v['role']==role):
                    before=r.check_step(before,record['step'],numerics=numerics)
    return dict(family='A_PC',status='positive_joint_witness_pending_acceptance' if row['case_passed'] else 'joint_successor_held',
        source_eligible=True,new_source_steps=1,attempted_cases=1,native_cases=int('event' in row),
        committed_events=int(row['event_committed']),passed_cases=int(row['case_passed']),target_steps=len(row['continuation']),
        final_reads=len(row['final_reads']),passing_pending_cells=2*int(row['case_passed']),accepted_cells=0,
        required_cells=40,unattempted_cases=19,first_failure=row['first_failure'],native_trajectories_rerun=False,
        interval_equations_recomputed=numerics,uniform_native_domain=False,user_accepted=False,aggregate_closed=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('prepare','run','check'))
    parser.add_argument('--recheck-numerics',action='store_true');args=parser.parse_args()
    b.require(not args.recheck_numerics or args.action=='check','recheck requires check')
    path={'prepare':INPUTS,'run':RESULTS}.get(args.action)
    if path:b.require(not (b.ROOT/path).exists(),'refuse to overwrite retained evidence')
    if args.action=='prepare':
        m=prepare();b.write_new(INPUTS,m);summary=dict(source_eligible=True,selection=m['derivation']['selection'])
    else:
        m=b.read(INPUTS);value=run(m) if args.action=='run' else b.read(RESULTS)
        if path:b.write_new(path,value)
        summary=check(m,value,numerics=args.recheck_numerics)
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
