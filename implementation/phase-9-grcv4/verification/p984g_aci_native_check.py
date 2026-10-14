"""Retained A_CI native evidence checks; no root or interval-solve replay."""
import argparse
from copy import deepcopy
import hashlib
import json
import lzma
import math
import p984g_aci_native as run

ROOT,BASE,HERE=run.ROOT,run.BASE,run.HERE
SELF=HERE+'p984g_aci_native_check.py'
RESULTS=BASE+'P9-8.4g-ACINativeResults.json'
KNOWN_HOLDS=['analytic_hodge_exact_inverse_bypasses_selected_interval_route',
             'A_nonlinear_baseline_interval_collapsed_to_lower_endpoint']
q,require,digest,seal=run.q,run.require,run.digest,run.seal


def pairwise(xs):
    xs=list(xs)
    while len(xs)>1:xs=[xs[i]+xs[i+1] if i+1<len(xs) else xs[i] for i in range(0,len(xs),2)]
    return xs[0] if xs else 0.0


def root_check(root,subject,role,expected):
    s=run.oracle;state=subject['roles'][role];params=subject['profile']['params_resolved']
    require(root['evaluations']==2 and root['native_stopping_matches_oracle'],'two-pass stopping')
    require(root['identity'].startswith('grcv4-ci-root-sha256:'),'root identity')
    require(root['state_digest']==digest(state),'root C/W state binding')
    for k,values in root['actual'].items():
        require(values==expected['confirming'][k] and all(math.isfinite(x) for x in values),'primitive staging drift')
    require(set(root['actual'])=={'potential','baseline','drive','current','flux','flat'},'primitive roster')
    require(root['selected_joint_point_digest']==expected['selected_joint_point_digest'] and
        root['represented_geometry_digest']==expected['represented_geometry_digest'],'full joint digest drift')
    require(root['independent_stages']==expected['stages'] and len(expected['stages'])==2,'independent stage binding')
    tolerance=q(params['realization']['tolerance']);cert=root['certificate']
    require(0<=q(root['native_residual_squared'])<=tolerance**2,'native residual')
    radius=q(float.fromhex(params['realization']['contraction_domain_id'].split(':',1)[1]))
    require(q(cert['radius'])==radius and 0<=q(cert['displacement_upper'])<=radius and
        0<=q(cert['contraction_upper'])<1 and cert['reference_connected'] and cert['regular_reduced_root']
        and cert['scope']=='analytic_local_reference_ball' and cert['norm']=='joint_current_geometry_l2_v1','certificate domain')
    with s.ctx.workprec(s.BITS):
        bounds=s.prior.certificate(subject,role,1)['bounds'];md=s.model(subject,role)
        for stage in expected['stages']:
            fj,fh=q(stage['analytic_current_residual_upper']),q(stage['analytic_geometry_residual_upper'])
            require(fj>=0 and fh>=0 and stage['analytic_residual_pass'] and
                s.prior.norm([fj,fh])==q(stage['analytic_joint_residual_upper'])<=tolerance,'independent joint residual')
            require(stage['joint_root_bridge']==s.bridge(bounds,params['candidate'],params['geometry']['kappa_H'],fj,fh),'full joint bridge')
        h=s.image(md,expected['reference']['flat'],staged=True)
        rows=[[s.unique(h[i,j]) for j in range(h.ncols())] for i in range(h.nrows())]
        require(digest(rows)==expected['represented_geometry_digest'],'reconstructed geometry')
        require(digest(dict(graph=subject['graph'],profile=subject['profile'],C=state['C'],W_A=state['W_A'],
            H=rows,J=root['actual']['current']))==root['selected_joint_point_digest'],'reconstructed joint point')


def assess(value,companion,oracle):
    require(value==seal(value) and value['source_bindings']==run.bindings(),'native source/record drift')
    require(value['schema']=='p984g-aci-native-prerequisite-v1','native schema')
    graph,role=value['graph'],value['role'];require((graph,role) in run.CASES,'case roster')
    require(value['cap_seconds']==600 and math.isfinite(value['seconds']) and value['seconds']>=0,'bounded execution metadata')
    require(value['committed_steps']==value['native_events']==0 and not value['user_accepted'] and
        not value['ready_for_8_4h'],'scope inflation')
    require(value['numerical_policy']=='certified_arb_256_weighted_v1' and value['exact_backend']=='flint','policy')
    if value['outcome']!='completed':
        require(value['outcome']=='incomplete','unknown outcome')
        require(value['timed_out'] or value['error'] is not None or value['exit_code']!=0,'unexplained incomplete execution')
        return dict(graph=graph,role=role,outcome='incomplete',native_steps=0,native_roots=0,
                    seconds=value['seconds'],error=value['error'],timed_out=value['timed_out'])
    require(value['exit_code']==0 and not value['timed_out'] and value['error'] is None,'incomplete success claim')
    r=value['result'];subject=companion[graph];state=subject['roles'][role];params=subject['profile']['params_resolved']
    require(r['initial_C']==state['C'] and r['initial_W_A']==state['W_A'] and
        r['reset_C']==subject['roles']['reset']['C'] and r['reset_W_A']==subject['roles']['reset']['W_A'],'role inputs')
    require(set(r['roots'])=={'reset','current','final'},'root roster')
    for key,which in (('reset','reset'),('current',role)):
        expected=next(c['result'] for c in oracle['cases'] if c['graph']==graph and c['role']==which)
        root_check(r['roots'][key],subject,which,expected)
    final=deepcopy(subject);final['roles']['current']=dict(C=r['after_C'],W_A=r['after_W_A'],Z_4=None)
    root_check(r['roots']['final'],final,'current',r['final_oracle'])
    dt=run.f.prior.read(run.f.prior.PREPARED)['selected_configuration']['ordinary_dt']
    bv=run.oracle.model(subject,role)['bv'];j=r['roots']['current']['actual']['current']
    expected_c=[float(c)-dt*sum(float(x)*v for x,v in zip(row,j)) for c,row in zip(state['C'],bv)]
    require(r['dt']==dt and r['after_C']==expected_c and min(expected_c)>0,'literal continuity/resources')
    charge=pairwise(expected_c);target=pairwise(state['C']);cp=params['charge']
    require(r['Q_target']==target and r['charge']==dict(target_charge=target,admitted_charge=charge,
        residual=float(q(charge)-q(target))),'represented charge receipt')
    require(abs(q(charge)-q(target))<=q(cp['absolute_tolerance'])+
        q(cp['relative_tolerance'])*max(abs(q(target)),q(1)),'charge admission')
    require(q(r['exact_resource_sum_delta'])==sum(map(q,expected_c),q(0))-sum(map(q,state['C']),q(0)),'exact stored sum')
    writer=run.writer_oracle(subject,role,expected_c,j,dt)
    require(r['writer']==writer and r['after_W_A']==writer['W_A'],'final-C/selected-J writer')
    wrong=run.writer_oracle(subject,role,state['C'],j,dt)
    base=run.writer_oracle(subject,role,expected_c,r['roots']['current']['actual']['baseline'],dt)
    require(r['writer_wrong_prestate_drive_changed']==sum(x!=y for x,y in zip(wrong['drive'],writer['drive'])) and
        r['writer_wrong_baseline_drive_changed']==sum(x!=y for x,y in zip(base['drive'],writer['drive'])),'wrong writer stage evidence')
    require(r['reset_unchanged'] and r['final_C_and_W_rebuilt'] and r['continuity_evaluations']==1 and
        r['carrier_writes']==0 and r['history_writes']==1,'authority/writer scope')
    require(r['after_step_index']==r['before_step_index']+1 and r['after_time']==r['before_time']+dt,'clock/index')
    if graph=='source':
        old=run.f.prior.read(run.f.prior.PREPARED);old['source']=subject
        with run.oracle.ctx.workprec(run.oracle.BITS):
            trigger=run.f.trigger(old,list(map(run.a,r['after_C'])),list(map(run.a,r['after_W_A'])))
        require(trigger==r['poststep_trigger'] and trigger['small_gradient'] and trigger['strict_hessian_condition'],'poststep trigger')
    return dict(graph=graph,role=role,outcome='completed',seconds=value['seconds'],native_roots=3,native_steps=1,
        minimum_resource=min(expected_c),exact_resource_sum_delta=r['exact_resource_sum_delta'],
        represented_charge=r['charge'],root_evaluations=[r['roots'][k]['evaluations'] for k in ('reset','current','final')],
        writer_wrong_prestate_drive_changed=r['writer_wrong_prestate_drive_changed'],
        writer_wrong_baseline_drive_changed=r['writer_wrong_baseline_drive_changed'])


def check():
    companion=run.f.check_retained();oracle=run.oracle.check_retained();cases=[]
    for graph,role in run.CASES:
        path=run.case_path(graph,role)
        if not (ROOT/path).exists():
            cases.append(dict(graph=graph,role=role,outcome='not_run',native_steps=0,native_roots=0));continue
        raw=(ROOT/path).read_bytes();value=json.loads(lzma.decompress(raw))
        require((value['graph'],value['role'])==(graph,role),'case filename')
        cases.append(dict(assess(value,companion,oracle),path=path,sha256=hashlib.sha256(raw).hexdigest(),record_digest=value['record_digest']))
    return seal(dict(schema='p984g-aci-native-summary-v1',family='A_CI',cases=cases,
        native_steps=sum(c['native_steps'] for c in cases),native_roots=sum(c['native_roots'] for c in cases),
        native_events=0,committed_steps=0,user_accepted=False,ready_for_8_4h=False,
        known_implementation_holds=KNOWN_HOLDS,
        native_prerequisites_complete=all(c['outcome']=='completed' for c in cases) and not KNOWN_HOLDS,
        scope='prepared_role_controls_not_postbeat_event_or_uniform_domain',
        retained_check_only=True,numerical_trajectories_rerun=False,
        source_bindings={SELF:hashlib.sha256((ROOT/SELF).read_bytes()).hexdigest()}))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['check','summarize']);args=p.parse_args()
    value=check()
    if args.mode=='summarize':
        require(not (ROOT/RESULTS).exists(),'no overwrite');(ROOT/RESULTS).write_text(json.dumps(value,indent=2)+'\n')
    else:require(value==json.loads((ROOT/RESULTS).read_text()),'summary drift')
    print(json.dumps({k:value[k] for k in ('native_steps','native_roots','native_prerequisites_complete')}))
