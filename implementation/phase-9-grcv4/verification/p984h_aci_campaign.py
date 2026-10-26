"""Bounded A_CI actual event and detached continuation; no source rerun."""
import argparse
from copy import deepcopy
from dataclasses import replace
import json
import lzma
import multiprocessing as mp
import os
import time
from unittest.mock import patch

import numpy as np
import p984h_aci_source as source
from pygrc.models import grc_v4_ci as ci
from pygrc.models.grc_9_v4_expansion import GRC9V4ACIExpansion
from pygrc.models.grc_v4_numerics import ExactBackend, NumericalPolicy, exact_backend, numerical_policy, matrix_operation

p = source.prep
ROOT, BASE, HERE = p.ROOT, p.BASE, p.HERE
SELF, TEST = HERE+'p984h_aci_campaign.py', HERE+'test_p984h_aci_campaign.py'
PLAN, INPUTS = BASE+'P9-8.4h-ACICampaignPlan.md', BASE+'P9-8.4h-ACICampaignInputs.json'
ROLES = ('current', 'reset')
DT = 2**-12
require, seal, digest, q, oracle = p.require, p.seal, p.digest, p.q, p.base.oracle


def path(segment, role='current', step=1):
    require(segment in ('event', 'step', 'final') and role in ROLES and 1 <= step <= 10, 'segment roster')
    suffix = 'event' if segment == 'event' else role+'-'+('final' if segment == 'final' else str(step))
    return BASE+'P9-8.4h-ACI-'+suffix+'.json.xz'


def read(segment, role='current', step=1):
    return json.loads(lzma.decompress((ROOT/path(segment, role, step)).read_bytes()))


def manifest():
    upstream = source.bindings()
    require(upstream == json.loads((ROOT/source.INPUTS).read_text()), 'source input drift')
    paths = set(upstream['source_bindings']) | {source.INPUTS, source.RESULT, SELF, TEST, PLAN}
    return seal(dict(schema='p984h-aci-campaign-inputs-v1',
        source_bindings={s:p.sha(s) for s in sorted(paths)}, caps=p.CAPS,
        exact_backend='flint', numerical_policy='certified_arb_256_weighted_v1',
        native_events=1, target_steps=20, final_roots=2, source_rerun=False,
        compressed_total_budget_bytes=20000000, user_accepted=False, aggregate_closed=False))


def state(payload):
    spec = payload['specialization']
    return p.native.GRC9V4ACIState(p.GeometryStageInputs.from_payload(payload['inputs']),
        p.native.GRC9V4Specialization(p.FrozenJSONMap(spec['resolved']), p.FrozenJSONMap(spec['identity_payload'])))


def subject(before):
    ref = before.geometry.reference
    return dict(graph=ref.graph.port_graph.to_envelope(), profile=ref.profile.to_payload(),
        roles={r:dict(C=list(getattr(before,r).C), W_A=list(getattr(before,r).W_A), Z_4=None) for r in ROLES})


def backend(before):
    return p.native.GRC9V4CandidateADifferentialReference(before.geometry.reference.graph.port_graph)


def root_capture(root, before):
    operand = subject(before)
    with oracle.ctx.workprec(oracle.BITS): expected = oracle.analyze(operand, 'current', DT)
    value = p.base.compare_root(root, operand, 'current', expected)
    t = root.selected
    value.update(oracle=expected, joint=dict(H=[list(r) for r in t.inputs.geometry.one_form_hodge.matrix],
        generated=[list(r) for r in t.generated.one_form_hodge.matrix],
        source=[list(r) for r in t.structural_source.increment], recipe=root.to_payload()['numerics'],
        domain_id=before.geometry.reference.profile.params_resolved.realization.contraction_domain_id))
    return value


def generated(before, flat):
    """Independent exact primitive staging, without a native geometry call."""
    b, _, _, _, _ = oracle.prior.operands(subject(before), 'current')
    mask = abs(b).T @ abs(b) / 2
    params = before.geometry.reference.profile.params_resolved.to_payload()
    zeta, kh = q(params['candidate']['zeta_A']), q(params['geometry']['kappa_H'])
    src = np.zeros(mask.shape); h = np.eye(len(flat))
    for i,j in zip(*np.nonzero(mask), strict=True):
        star = float(q(float(mask[i,j]))*q(flat[i])*q(flat[j]))
        src[i,j] = float(zeta*q(star))
        h[i,j] = float(i==j)+float(kh*q(float(src[i,j])))
    return src.tolist(), h.tolist()


def check_root(value, before):
    expected = value['oracle']; operand = subject(before)
    require(value['evaluations'] == 2 and value['native_stopping_matches_oracle']
        and expected['two_consecutive_independent_residual_passes'], 'two-pass stopping')
    require(all(value['actual'][k] == expected['confirming'][k] for k in value['actual']), 'root primitives')
    params = before.geometry.reference.profile.params_resolved.to_payload()
    tol = q(params['realization']['tolerance']); cert = value['certificate']
    radius = q(float.fromhex(params['realization']['contraction_domain_id'].split(':',1)[1]))
    require(q(cert['radius']) == radius and 0 <= q(cert['displacement_upper']) <= radius
        and 0 <= q(cert['contraction_upper']) < 1 and cert['regular_reduced_root'] and cert['reference_connected']
        and cert['norm']=='joint_current_geometry_l2_v1' and cert['scope']=='analytic_local_reference_ball', 'root domain')
    require(0 <= q(value['native_residual_squared']) <= tol**2
        and all(s['analytic_residual_pass'] and 0 <= q(s['analytic_joint_residual_upper']) <= tol
                for s in expected['stages']), 'literal/independent residuals')
    joint = value['joint']; h = joint['H']
    require(joint['domain_id'] == params['realization']['contraction_domain_id']
        and joint['recipe'] == 'grc9v4_ci_fixed_rows_confirmed_joint_residual_v1', 'root domain/recipe identity')
    require(value['identity']==ci._identity('grcv4-ci-root-sha256',dict(schema_version='grcv4-ci-root-recipe-v1',
        numerics=joint['recipe'],inputs=before.to_payload(),differential_reference=backend(before).to_payload())), 'root input identity')
    require(digest(h) == value['represented_geometry_digest'] == expected['represented_geometry_digest'], 'selected H identity')
    require(digest(dict(graph=operand['graph'], profile=operand['profile'], C=list(before.current.C),
        W_A=list(before.current.W_A), H=h, J=value['actual']['current'])) ==
        value['selected_joint_point_digest'] == expected['selected_joint_point_digest'], 'whole selected point')
    require(value['state_digest'] == digest(operand['roles']['current']), 'root authority')
    require(h == generated(before, expected['reference']['flat'])[1], 'confirming H construction')
    src, out = generated(before, value['actual']['flat'])
    require(joint['source'] == src and joint['generated'] == out, 'same-root source/regeneration')


def baseline_source():
    v = json.loads(lzma.decompress((ROOT/source.RESULT).read_bytes()))
    require(v == seal(v) and v['manifest_digest'] == source.bindings()['record_digest'], 'source predecessor')
    return state(v['execution']['state']), v


def expected_event(seed, request):
    """Reuse frozen allocation graph; independently apply actual C/W transfers."""
    plan = source.GRC9V4ExpansionPlan(seed.inputs.geometry.reference.graph.port_graph, seed.scientific_digest,
        source.GRC9V4ExpansionRequestInput.from_payload(request),
        source.GRC9ExpansionPolicy.from_payload(seed.specialization.resolved['expansion']))
    old, prepared, _, declaration = p.base.f.companion(source_deficit=p.base.f.DEFICIT)
    graph = deepcopy(prepared['graph']); old_id = declaration['event_id']
    def rename(x): return plan.event_id+x[len(old_id):] if isinstance(x,str) and x.startswith(old_id+'/') else x
    graph['live_node_ids'] = [rename(n) for n in graph['live_node_ids']]
    for e in graph['edges']:
        e['edge_id'] = rename(e['edge_id'])
        for end in ('tail','head'): e[end]['node_id'] = rename(e[end]['node_id'])
    port = p.base.f.prepared.GRC9V4PortGraph.from_payload({k:graph[k] for k in ('schema_version','live_node_ids','edges')})
    require(port == plan.target_graph and plan.event_id != old_id, 'fresh independent graph allocation')
    expansion = GRC9V4ACIExpansion(plan, seed.inputs.geometry.reference, seed.inputs.current, seed.inputs.reset)
    roles = {}
    for role in ROLES:
        incoming = getattr(seed.inputs,role)
        cs = dict(zip(plan.source_graph.live_node_ids, incoming.C, strict=True))
        image = {n:cs.get(n,0.) for n in port.live_node_ids}
        for i,share in enumerate(request['resource_distribution'],1):
            image[plan.event_id+f'/satellite/{i}'] = float(q(cs[request['source_node_id']])*q(share))
        ws = dict(zip(seed.inputs.geometry.reference.graph.live_edge_ids, incoming.W_A, strict=True))
        roles[role] = p.GRCV4AuthoritativeState(tuple(image[n] for n in port.live_node_ids),
            tuple(ws.get(e.edge_id, plan.policy.bond_seed) for e in port.edges), None)
        require(roles[role] == expansion.transfer(incoming), 'independent C/W transfer')
    target = p.base.f.prepared.make_state(port, p.base.f.prepared.profile_for(port,'A_CI',old['selected_configuration']),
        seed.specialization, roles, 'A_CI')
    require(target.inputs.geometry.reference.profile == expansion.target.profile, 'complete target reference')
    target = replace(target, inputs=replace(target.inputs, time=seed.inputs.time, step_index=seed.inputs.step_index,
        operation_id=request['operation_id'], dt=0, receipt_ids=seed.inputs.receipt_ids))
    return plan, target.inputs


def event_capture(seed, request, expected, progress):
    progress('owner_source_readmission')
    owner = p.native.GRC9V4ACIOperation(seed); published = owner._published; checkpoint = owner.checkpoint()
    stale = dict(request, source_state_digest='grcv4-state-sha256:'+'0'*64)
    rejected = owner.expand(source.GRC9V4ExpansionRequestInput.from_payload(stale))
    require(not rejected.committed and owner._published is published and owner.checkpoint() == checkpoint, 'stale rollback')
    reads, writers = [], []
    real_step, real_writer = p.native.ProvisionalCandidateCIStep, p.native.candidate_a_writer_target
    def observed(before, differential):
        progress('event_readmission_pair_'+str(len(reads)+1))
        step = real_step(before, differential)
        require(owner._published is published, 'early publication')
        reads.append(dict(current=root_capture(step.root,before),
            reset=root_capture(step.reset_root,replace(before,current=before.reset)), old_publication_live=True))
        return step
    def written(point, C):
        actual = real_writer(point,C)
        operand = subject(point.inputs)
        expected_writer = p.base.writer_oracle(operand,'current',C.values,point.current.values,DT)
        require([list(r) for r in actual[0]] == expected_writer['descriptors']
            and list(actual[1]) == expected_writer['drive'] and owner._published is published, 'event writer surface')
        writers.append(dict(C=list(C.values), W_A=list(point.inputs.current.W_A), J=list(point.current.values),
            descriptors=[list(r) for r in actual[0]], drive=list(actual[1]), old_publication_live=True))
        return actual
    with patch.object(p.native,'ProvisionalCandidateCIStep',observed), patch.object(p.native,'candidate_a_writer_target',written):
        outcome = owner.expand(source.GRC9V4ExpansionRequestInput.from_payload(request))
    require(outcome.committed, 'native event failed: '+str(outcome.failure))
    require(p.canonical_input_payload(owner.state.inputs.to_payload()) == p.canonical_input_payload(expected.to_payload()), 'actual target')
    require(len(reads) == 2 and len(writers) == 4 and owner.state.inputs.time == seed.inputs.time
        and owner.state.inputs.step_index == seed.inputs.step_index, 'event admission coverage/clock')
    return dict(checkpoint=json.loads(owner.checkpoint()), admissions=reads, writer_surfaces=writers,
        request=request, event_id=source.GRC9V4ExpansionPlan(seed.inputs.geometry.reference.graph.port_graph,seed.scientific_digest,
            source.GRC9V4ExpansionRequestInput.from_payload(request),source.GRC9ExpansionPolicy.from_payload(seed.specialization.resolved['expansion'])).event_id,
        stale_failure=rejected.failure.to_payload(), rollback_exact=True, native_events=1, native_steps=0)


def observe(before):
    frozen = digest(before.to_payload()); step = ci.ProvisionalCandidateCIStep(before,backend(before)); after = step.next_inputs
    require(digest(before.to_payload()) == frozen and after.reset == before.reset and after.geometry == before.geometry, 'mutation/reset')
    require(after.time == before.time+before.dt and after.step_index == before.step_index+1
        and step.resource.continuity_evaluations == 1 and step.carrier_writes == 0, 'step lifecycle')
    roots = {name:root_capture(root,operand) for name,root,operand in
        (('current',step.root,before),('reset',step.reset_root,replace(before,current=before.reset)),('final',step.restart,replace(after,dt=0)))}
    expected = p.base.writer_oracle(subject(before),'current',after.current.C,step.root.current.values,DT)
    require(list(after.current.W_A) == expected['W_A'] and list(step.writer.W_drv_A) == expected['drive']
        and [list(r) for r in step.writer.descriptors] == expected['descriptors'], 'independent writer')
    resources = roots['current']['oracle']['resources']
    require([r['represented'] for r in resources] == list(after.current.C)
        and min(q(r['lower']) for r in resources) > 0, 'local exact-root resource signs')
    return dict(before_digest=frozen, next_inputs=after.to_payload(), roots=roots,
        writer=dict(C=list(after.current.C),W_A=list(before.current.W_A),J=list(step.root.current.values),
            descriptors=[list(r) for r in step.writer.descriptors],drive=list(step.writer.W_drv_A),written_W_A=list(after.current.W_A)),
        minimum_exact_root_resource_lower=str(min(q(r['lower']) for r in resources)),
        charge=step.resource.charge.receipt_values(), exact_resource_sum_delta=str(sum(map(q,after.current.C),q(0))-sum(map(q,before.current.C),q(0))),
        reset_unchanged=True, native_steps=1, native_events=0, detached_continuation=True)


def incoming(segment, role, step):
    if step == 1 and segment == 'step':
        old = read('event'); before = state(old['execution']['checkpoint']['state']).inputs
        before = replace(before,current=getattr(before,role),dt=DT)
    else:
        old = read('step',role,10 if segment == 'final' else step-1)
        before = p.GeometryStageInputs.from_payload(old['execution']['next_inputs'])
    require(old == seal(old) and old['outcome'] == 'completed', 'predecessor seal/outcome')
    return before, old['record_digest']


def execute(segment, role, step, progress):
    if segment == 'event':
        seed, old = baseline_source(); request = old['execution']['request']; plan, expected = expected_event(seed,request)
        result = event_capture(seed,request,expected,progress); result['event_identity'] = plan.event_identity_payload()
        return result, old['record_digest']
    before, predecessor = incoming(segment,role,step)
    if segment == 'step': return observe(before), predecessor
    before = replace(before,dt=0)
    root = ci.CandidateCIRoot(before,backend(before))
    return dict(root=root_capture(root,before),native_steps=0,native_events=0,final_roots=1), predecessor


def worker(pipe, segment, role, step):
    try:
        with exact_backend(ExactBackend.FLINT), numerical_policy(NumericalPolicy.CERTIFIED_ARB_256), matrix_operation():
            result = execute(segment,role,step,lambda s:pipe.send(('progress',s)))
        pipe.send(('result', result))
    except Exception as exc: pipe.send(('error',dict(type=type(exc).__name__,message=str(exc))))
    finally: pipe.close()


def run(segment, role='current', step=1):
    m = manifest(); require(m == json.loads((ROOT/INPUTS).read_text()), 'manifest drift')
    if (ROOT/path(segment,role,step)).exists():
        check(segment,role,step); print('retained, no rerun',segment,role,step,flush=True); return
    require(all(os.environ.get(k)=='1' for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS')), 'single-thread policy')
    cap = p.CAPS['event' if segment=='event' else 'target_step' if segment=='step' else 'final_root']
    context = mp.get_context('spawn'); receive, send = context.Pipe(False)
    child = context.Process(target=worker,args=(send,segment,role,step)); start=time.monotonic(); child.start(); send.close(); result=None
    try:
        while time.monotonic()-start < cap:
            if receive.poll(.25):
                try: kind,value=receive.recv()
                except EOFError: break
                if kind=='progress': print(json.dumps(dict(segment=segment,role=role,step=step,stage=value,seconds=time.monotonic()-start)),flush=True)
                elif kind=='error': raise RuntimeError(str(value))
                else: result=value; break
            elif not child.is_alive(): break
        child.join(timeout=max(0,min(3,cap-(time.monotonic()-start))))
        elapsed=time.monotonic()-start
        require(result is not None and child.exitcode==0 and elapsed<=cap,'segment incomplete/cap; no retry')
    finally:
        if child.is_alive(): child.terminate(); child.join(timeout=3)
        if child.is_alive(): child.kill(); child.join(timeout=3)
        receive.close()
    require(m==manifest(),'source changed during execution')
    execution, predecessor=result
    record=seal(dict(schema='p984h-aci-campaign-segment-v1',manifest_digest=m['record_digest'],segment=segment,role=role,step=step,
        predecessor_digest=predecessor,execution=execution,seconds=elapsed,outcome='completed',user_accepted=False,aggregate_closed=False))
    check(segment,role,step,record)
    raw=lzma.compress(json.dumps(record,separators=(',',':'),allow_nan=False).encode()+b'\n')
    require(len(raw)<=2000000,'segment compressed budget')
    with (ROOT/path(segment,role,step)).open('xb') as stream: stream.write(raw)
    print(json.dumps(dict(segment=segment,role=role,step=step,outcome='completed',seconds=elapsed,compressed_bytes=len(raw))),flush=True)


def check_step(e,before):
    after=p.GeometryStageInputs.from_payload(e['next_inputs'])
    require(e['before_digest']==digest(before.to_payload()) and after.reset==before.reset and after.geometry==before.geometry
        and after.time==before.time+DT and after.step_index==before.step_index+1,'retained step lifecycle')
    for name,operand in (('current',before),('reset',replace(before,current=before.reset)),('final',replace(after,dt=0))): check_root(e['roots'][name],operand)
    expected=p.base.writer_oracle(subject(before),'current',after.current.C,e['roots']['current']['actual']['current'],DT)
    writer=e['writer']
    require(writer==dict(C=list(after.current.C),W_A=list(before.current.W_A),J=e['roots']['current']['actual']['current'],
        descriptors=expected['descriptors'],drive=expected['drive'],written_W_A=expected['W_A'])
        and list(after.current.W_A)==expected['W_A'],'retained writer operands')
    resources=e['roots']['current']['oracle']['resources']; lower=min(q(r['lower']) for r in resources)
    require(lower>0 and str(lower)==e['minimum_exact_root_resource_lower']
        and list(after.current.C)==[r['represented'] for r in resources], 'retained local sign/continuity')
    from p984g_cci_closure_check import pairwise
    charge=pairwise(after.current.C)
    require(e['charge']==dict(target_charge=before.Q_target,admitted_charge=charge,residual=charge-before.Q_target)
        and charge==before.Q_target and e['exact_resource_sum_delta']==str(sum(map(q,after.current.C),q(0))-sum(map(q,before.current.C),q(0))), 'charge distinctions')
    require(e['reset_unchanged'] and e['detached_continuation'] and e['native_steps']==1 and e['native_events']==0,'step credit')
    return after


def check(segment, role='current', step=1, value=None):
    m=manifest(); require(m==json.loads((ROOT/INPUTS).read_text()),'campaign drift')
    v=read(segment,role,step) if value is None else value
    cap=p.CAPS['event' if segment=='event' else 'target_step' if segment=='step' else 'final_root']
    require(v==seal(v) and v['manifest_digest']==m['record_digest'] and v['outcome']=='completed'
        and (v['segment'],v['role'],v['step'])==(segment,role,step) and 0<v['seconds']<=cap
        and v['user_accepted'] is False and v['aggregate_closed'] is False,'record identity/scope')
    e=v['execution']
    if segment=='event':
        seed,old=baseline_source(); plan,expected=expected_event(seed,e['request'])
        require(e['request']==old['execution']['request'] and v['predecessor_digest']==old['record_digest']
            and e['event_id']==plan.event_id and e['event_identity']==plan.event_identity_payload(), 'event identity')
        require(p.canonical_input_payload(e['checkpoint']['state']['inputs'])==p.canonical_input_payload(expected.to_payload())
            and e['native_events']==1 and e['native_steps']==0 and e['rollback_exact'] and bool(e['stale_failure'])
            and len(e['admissions'])==2 and len(e['writer_surfaces'])==4,'event target/coverage')
        for i,operand in enumerate((seed.inputs,expected)):
            require(e['admissions'][i]['old_publication_live'],'admission ordering')
            for j,r in enumerate(ROLES):
                before=replace(operand,current=getattr(operand,r)); root=e['admissions'][i][r]; check_root(root,before)
                writer=e['writer_surfaces'][2*i+j]; expected_writer=p.base.writer_oracle(subject(before),'current',before.current.C,root['actual']['current'],DT)
                require(writer==dict(C=list(before.current.C),W_A=list(before.current.W_A),J=root['actual']['current'],
                    descriptors=expected_writer['descriptors'],drive=expected_writer['drive'],old_publication_live=True),'event writer binding')
    else:
        before, predecessor=incoming(segment,role,step); require(v['predecessor_digest']==predecessor,'chain link')
        if segment=='step': check_step(e,before)
        else:
            check_root(e['root'],replace(before,dt=0))
            require(e['native_steps']==e['native_events']==0 and e['final_roots']==1,'final root credit')
    return v


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('action',choices=('prepare','run','check','chain'))
    parser.add_argument('--segment',choices=('event','step','final'),default='event'); parser.add_argument('--role',choices=ROLES,default='current')
    parser.add_argument('--step',type=int,default=1); args=parser.parse_args()
    if args.action=='prepare':
        with (ROOT/INPUTS).open('x') as stream: json.dump(manifest(),stream,indent=2); stream.write('\n')
    elif args.action=='run': run(args.segment,args.role,args.step)
    elif args.action=='chain':
        for k in range(1,11): run('step',args.role,k)
        run('final',args.role,10)
    else: check(args.segment,args.role,args.step); print('retained check passed; no native rerun')
