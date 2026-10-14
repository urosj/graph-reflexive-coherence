"""Retained C_CI native checks; never executes roots, trajectories or inverses."""
import argparse
import hashlib
import json
import lzma
import math
from pathlib import PurePosixPath
from copy import deepcopy
import p984g_cci_closure as run

ROOT, BASE, HERE = run.ROOT, run.BASE, run.HERE
SELF=HERE+'p984g_cci_closure_check.py'
q,require,seal=run.q,run.require,run.seal


def pairwise(values):
    values=list(values)
    while len(values)>1:
        values=[values[i]+values[i+1] if i+1<len(values) else values[i]
                for i in range(0,len(values),2)]
    return values[0] if values else 0.0


def normalize_diagnostics():
    """Remove machine-local stack labels only; preserve original record digest."""
    names=[run.setup.PROBE,BASE+'P9-8.4g-CCINativeCertificate.json']
    names += [run.case_path(*case) for case in run.CASES]
    for name in names:
        path=ROOT/name;raw=path.read_bytes();compressed=name.endswith('.xz')
        value=json.loads(lzma.decompress(raw) if compressed else raw)
        require(value==seal(value),'cannot normalize invalid record')
        changed=0
        def walk(obj):
            nonlocal changed
            if isinstance(obj,dict):
                if isinstance(obj.get('file'),str) and obj['file'].startswith('/'):
                    obj['file']='external-runtime/'+PurePosixPath(obj['file']).name
                    changed+=1
                for item in obj.values():walk(item)
            elif isinstance(obj,list):
                for item in obj:walk(item)
        original=value['record_digest'];walk(value)
        if changed:
            value['diagnostic_normalization']=dict(original_record_digest=original,
                policy='external_stack_filenames_to_basename_no_scientific_field_changes',labels_changed=changed)
            data=(json.dumps(seal(value),indent=2)+'\n').encode()
            path.write_bytes(lzma.compress(data,preset=6) if compressed else data)


def assess(value,subject,declaration,feasibility):
    require(value==seal(value),'case digest')
    require(value['source_bindings']==run.bindings(),'execution source drift')
    require(value['outcome']=='completed' and value['exit_code']==0 and not value['timed_out']
            and value['error'] is None,'incomplete native case')
    require(value['committed_steps']==value['native_events']==0 and not value['user_accepted']
            and not value['ready_for_8_4h'],'scope inflation')
    require(value['numerical_policy']=='certified_arb_256_weighted_v1' and value['exact_backend']=='flint','policy')
    graph,role=value['graph'],value['role'];result=value['result']
    require((graph,role) in run.CASES and result['declaration']==declaration,'case/declaration')
    before=subject['roles'][role]['C'];after=result['after_C']
    require(result['initial_C']==before and result['reset_C']==subject['roles']['reset']['C'],'role binding')
    b,params=run.f.prior.shared.graph_data(subject)
    dt=run.f.read(run.f.prior.PREPARED)['selected_configuration']['ordinary_dt']
    roots=result['roots'];require(set(roots)=={'current','reset','final'},'root roster')
    tolerance=q(params['realization']['tolerance'])
    reference_digest=run.f.prior.shared.digest([[float(i==j) for j in range(b.shape[1])] for i in range(b.shape[1])])
    for name,root in roots.items():
        cs=after if name=='final' else subject['roles']['reset']['C'] if name=='reset' else before
        require(root['resource_digest']==run.f.prior.shared.digest(cs),'root resource identity')
        require(root['evaluations']==1 and root['consumed_reference_geometry'],'unexpected root selection')
        require(root['identity'].startswith('grcv4-ci-root-sha256:'),'root identity')
        require(root['point']['input_hodge_digest']==reference_digest,'consumed geometry identity')
        cert=root['certificate']
        radius=q(float.fromhex(params['realization']['contraction_domain_id'].split(':',1)[1]))
        require(q(cert['radius'])==radius and 0<=q(cert['displacement_upper'])<=radius
                and 0<=q(cert['contraction_upper'])<1 and q(cert['selector_gap_lower'])>0
                and 0<q(cert['conditioning_upper'])<=q(params['solver']['conditioning_limit'])
                and cert['selector_rank']==1 and cert['reference_connected'] and cert['regular_reduced_root']
                and cert['norm']=='joint_current_geometry_l2_v1' and cert['scope']=='analytic_local_reference_ball',
                'native whole-ball certificate')
        require(0<=q(root['native_residual_squared'])<=tolerance**2 and
                0<=q(root['independent_residual_squared_upper'])<=tolerance**2,'joint residual')
        ej,eh=(q(root[k]) for k in ('independent_current_residual_upper','independent_geometry_residual_upper'))
        require(ej>=0 and eh>=0 and ej*ej+eh*eh==q(root['independent_residual_squared_upper']),'joint components')
        updated=deepcopy(subject);updated['roles']['current']['C']=cs
        bounds=run.f.prior.certificate(updated,'current')['bounds'];p=params['candidate']
        with run.f.staged.ctx.workprec(run.f.iv.BITS):
            bridge=run.f.staged.bridge(bounds,p['chi_C'],q(p['chi_C'])*q(p['zeta_C']),
                q(params['geometry']['kappa_H'])*q(p['zeta_C']),ej,eh)
        require(root['joint_root_error']==bridge,'root-error bridge')
        for key in ('current','baseline','read_flux','causal_flat'):
            require(len(root['point'][key])==b.shape[1] and all(math.isfinite(x) for x in root['point'][key]),'point dimension/finiteness')
        require(root['point']['selector_rank']==1,'selector rank')
    j=roots['current']['point']['current']
    require(result['dt']==dt and after==run.cos.independent_continuity(subject,role,j,dt),'literal continuity')
    require(len(after)==len(before) and min(after)>0,'positive native resources')
    target=pairwise(subject['roles']['current']['C']);charge=pairwise(after)
    require(result['Q_target']==target and result['charge']==dict(target_charge=target,
        admitted_charge=charge,residual=float(q(charge)-q(target))),'pairwise charge')
    cp=params['charge']
    require(abs(q(charge)-q(target))<=q(cp['absolute_tolerance'])+q(cp['relative_tolerance'])*max(abs(q(target)),q(1)), 'charge admission')
    require(q(result['exact_resource_sum_delta'])==sum(map(q,after),q(0))-sum(map(q,before),q(0)),'exact sum drift')
    require(result['reset_unchanged'] and result['final_C_rebuilt'] and result['continuation_reference_geometry']
            and result['continuity_evaluations']==1 and result['carrier_writes']==0,'lifecycle numerical fields')
    require(result['after_step_index']==result['before_step_index']+1 and
            result['after_time']==result['before_time']+dt,'clock/index')
    error=q(roots['current']['joint_root_error']['current_error_upper'])
    exact_bounds=feasibility['source_step' if graph=='source' else 'initial_transfer']['resource_bounds']
    rounding=[];radii=[]
    for i,(c,y,bound) in enumerate(zip(before,after,exact_bounds,strict=True)):
        exact=q(c)-q(dt)*sum((q(int(w))*q(x) for w,x in zip(b[i],j,strict=True)),q(0))
        with run.f.staged.ctx.workprec(run.f.iv.BITS):
            radius=q(dt)*run.f.iv.hi(run.f.iv.a(sum(int(w)**2 for w in b[i])).sqrt())*error
        # Independent exact-root enclosure must intersect this residual-derived
        # enclosure. Do not pretend the rounded step is the exact-root step.
        require(exact+radius>=q(bound['lower']) and exact-radius<=q(bound['upper']), 'independent resource enclosures disjoint')
        rounding.append(abs(q(y)-exact));radii.append(radius)
    if graph=='source':
        # Reuse the already authenticated source subject; no repeated state or
        # expansion materialization just to read its local nine-port rows.
        old=run.f.read(run.f.prior.PREPARED)
        old['source']=subject;old['event_request']=declaration['event_request']
        with run.f.staged.ctx.workprec(run.f.iv.BITS):
            trigger=run.f.trigger_envelope(old,[run.f.iv.a(x) for x in after])
        require(result['poststep_trigger']==trigger and trigger['small_gradient'] and trigger['strict_hessian_condition'],'actual poststep trigger')
    return dict(graph=graph,role=role,seconds=value['seconds'],native_roots=3,native_steps=1,
        minimum_resource=min(after),maximum_continuity_rounding_error=str(max(rounding)),
        maximum_root_resource_radius=str(max(radii)),exact_resource_sum_delta=result['exact_resource_sum_delta'],
        independent_joint_residual_upper=max(float(q(r['independent_residual_squared_upper']))**.5 for r in roots.values()),
        root_evaluations=[roots[k]['evaluations'] for k in ('reset','current','final')])


def check():
    old,target,_,declaration=run.f.companion(run.f.DEFICIT)
    feasible=run.f.check_retained();cases=[]
    for graph,role in run.CASES:
        path=run.case_path(graph,role);raw=(ROOT/path).read_bytes()
        value=json.loads(lzma.decompress(raw))
        require((value['graph'],value['role'])==(graph,role),'case file identity')
        subject=old['source'] if graph=='source' else target
        fcase=next(c for c in feasible['cases'] if c['role']==role)
        cases.append(dict(assess(value,subject,declaration,fcase),path=path,
            sha256=hashlib.sha256(raw).hexdigest(),record_digest=value['record_digest']))
    return seal(dict(schema='p984g-cci-native-closure-v1',family='C_CI',cases=cases,
        native_steps=4,native_roots=12,native_events=0,committed_steps=0,
        native_prerequisites_complete=True,user_accepted=False,ready_for_8_4h=False,
        scope='four_fixed_companion_numerical_steps_not_lifecycle_or_uniform_domain',
        source_bindings={SELF:hashlib.sha256((ROOT/SELF).read_bytes()).hexdigest()},
        retained_check_only=True,numerical_trajectories_rerun=False))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['check','summarize','normalize-diagnostics']);a=p.parse_args()
    if a.mode=='normalize-diagnostics':
        normalize_diagnostics();raise SystemExit(0)
    result=check()
    if a.mode=='summarize':
        path=ROOT/run.RESULTS;require(not path.exists(),'no overwrite')
        path.write_text(json.dumps(result,indent=2)+'\n')
    else:require(result==run.read(run.RESULTS),'summary drift')
    print(json.dumps({k:result[k] for k in ('native_steps','native_roots','native_prerequisites_complete')}))
