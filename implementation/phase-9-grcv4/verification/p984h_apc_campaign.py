"""Actual A_PC expansion and both persistent target histories; no source rerun."""
import argparse
from copy import deepcopy
from dataclasses import replace
import json
import lzma
from unittest.mock import patch

import p984h_apc as prep
from pygrc.models import grc_v4_pc as pc
from pygrc.models.grc_9_v4_expansion import GRC9V4APCExpansion

p=prep.p;ROOT,BASE,HERE=prep.ROOT,prep.BASE,prep.HERE
SELF=HERE+'p984h_apc_campaign.py';TEST=HERE+'test_p984h_apc_campaign.py'
INPUTS=BASE+'P9-8.4h-APCCampaignInputs.json'
ROLES,DT=prep.ROLES,prep.DT
require,seal,digest,q=prep.require,prep.seal,prep.digest,prep.q


def path(segment,role='current',step=1):
    require(segment in ('event','step','final') and role in ROLES and 1<=step<=10,'segment roster')
    suffix='event' if segment=='event' else role+'-'+('final' if segment=='final' else str(step))
    return BASE+'P9-8.4h-APC-'+suffix+'.json.xz'


def read(segment,role='current',step=1):return json.loads(lzma.decompress((ROOT/path(segment,role,step)).read_bytes()))


def manifest():
    upstream=json.loads((ROOT/prep.INPUTS).read_text())
    require(upstream==seal(upstream) and all(prep.sha(n)==v for n,v in upstream['source_bindings'].items()),'source input drift')
    names=set(upstream['source_bindings'])|{prep.INPUTS,prep.RESULT,SELF,TEST}
    return seal(dict(schema='p984h-apc-campaign-inputs-v1',source_bindings={n:prep.sha(n) for n in sorted(names)},
        caps=prep.CAPS,exact_backend='flint',numerical_policy='certified_arb_256_weighted_v1',
        native_events=1,target_steps=20,final_reads=2,source_rerun=False,user_accepted=False,aggregate_closed=False))


def state(payload):
    spec=payload['specialization']
    return prep.native.GRC9V4APCState(prep.GeometryStageInputs.from_payload(payload['inputs']),
        prep.native.GRC9V4Specialization(prep.FrozenJSONMap(spec['resolved']),prep.FrozenJSONMap(spec['identity_payload'])))


def subject(before):
    ref=before.geometry.reference
    return dict(graph=ref.graph.port_graph.to_envelope(),profile=ref.profile.to_payload(),
        roles={r:dict(C=list(getattr(before,r).C),W_A=list(getattr(before,r).W_A),Z_4=list(getattr(before,r).Z_4)) for r in ROLES})


def backend(before):return prep.native.GRC9V4CandidateADifferentialReference(before.geometry.reference.graph.port_graph)


def zrows(authority):
    n=len(authority.W_A);require(len(authority.Z_4)==n*n,'full carrier coordinates')
    return [list(authority.Z_4[i*n:(i+1)*n]) for i in range(n)]


def read_capture(native_read,before):
    operand=subject(before)
    with p.ctx.workprec(p.BITS):expected=p.read(p.model(operand,'current'),zrows(before.current))
    actual=prep.prior.point_record(native_read)
    prep.prior.compare_point(actual,expected,list(before.current.C),list(before.current.W_A),p.sparse(zrows(before.current)),operand)
    return dict(actual=actual,oracle=expected,state_digest=digest(operand['roles']['current']),
        scope='full_fixed_Z_PC_point_not_CI_root')


def check_read(value,before):
    operand=subject(before)
    require(value['state_digest']==digest(operand['roles']['current']) and value['scope']=='full_fixed_Z_PC_point_not_CI_root','PC point authority')
    prep.prior.compare_point(value['actual'],value['oracle'],list(before.current.C),list(before.current.W_A),p.sparse(zrows(before.current)),operand)
    require(all(q(x)>=0 for x in value['oracle']['errors'].values()),'negative error enclosure')


def baseline_source():
    v=json.loads(lzma.decompress((ROOT/prep.RESULT).read_bytes()))
    m=json.loads((ROOT/prep.INPUTS).read_text())
    require(v==seal(v) and v['manifest_digest']==m['record_digest'] and v['outcome']=='completed','source predecessor')
    return state(v['execution']['state']),v


def event_label_image(value,old_event,new_event):
    return new_event+value[len(old_event):] if isinstance(value,str) and value.startswith(old_event+'/') else value


def expected_event(seed,request):
    plan=prep.plan_for(seed,request)
    # Reuse independently assembled accepted layout; only event-local labels change.
    _,oracle=prep.accepted();graph=deepcopy(oracle['subjects']['target']['graph'])
    oldid=next(n.split('/satellite/')[0] for n in graph['live_node_ids'] if isinstance(n,str) and '/satellite/' in n)
    def rename(x):return event_label_image(x,oldid,plan.event_id)
    graph['live_node_ids']=[rename(n) for n in graph['live_node_ids']]
    for e in graph['edges']:
        e['edge_id']=rename(e['edge_id'])
        for end in ('tail','head'):e[end]['node_id']=rename(e[end]['node_id'])
    port=prep.d.GRC9V4PortGraph.from_payload({k:graph[k] for k in ('schema_version','live_node_ids','edges')})
    require(port==plan.target_graph and oldid!=plan.event_id,'fresh target allocation')
    expansion=GRC9V4APCExpansion(plan,seed.inputs.geometry.reference,seed.inputs.current,seed.inputs.reset)
    roles={}
    for role in ROLES:
        incoming=getattr(seed.inputs,role);cs=dict(zip(plan.source_graph.live_node_ids,incoming.C,strict=True))
        values={n:cs.get(n,0.) for n in port.live_node_ids}
        for i,share in enumerate(request['resource_distribution'],1):values[plan.event_id+f'/satellite/{i}']=float(q(cs[request['source_node_id']])*q(share))
        ws=dict(zip(seed.inputs.geometry.reference.graph.live_edge_ids,incoming.W_A,strict=True))
        roles[role]=prep.GRCV4AuthoritativeState(tuple(values[n] for n in port.live_node_ids),
            tuple(ws.get(e.edge_id,plan.policy.bond_seed) for e in port.edges),(0.,)*(len(port.edges)**2))
        require(roles[role]==expansion.transfer(incoming),'independent C/W/whole-Z transfer')
    declaration=p.prior.read(p.prior.PREPARED)
    target=prep.d.make_state(port,prep.d.profile_for(port,'A_PC',declaration['selected_configuration']),seed.specialization,roles,'A_PC')
    require(target.inputs.geometry.reference.profile==expansion.target.profile,'target complete reference')
    target=replace(target.inputs,time=seed.inputs.time,step_index=seed.inputs.step_index,operation_id=request['operation_id'],dt=0,receipt_ids=seed.inputs.receipt_ids)
    return plan,target


def writer_surface(point,C):
    md=p.model(subject(point.inputs),'current')
    with p.ctx.workprec(p.BITS):drive=p.writer_drive(md,list(C),list(point.current.values))
    fresh=p.model(md['subject'],'current',list(C),list(point.inputs.current.W_A))
    return dict(C=list(C),W_A=list(point.inputs.current.W_A),J=list(point.current.values),
        descriptors=[[float(x) for x in row] for row in fresh['desc']],drive=drive)


def event_capture(seed,request,expected,progress):
    progress('owner_source_readmission');owner=prep.native.GRC9V4APCOperation(seed)
    published=owner._published;checkpoint=owner.checkpoint()
    stale=dict(request,source_state_digest='grcv4-state-sha256:'+'0'*64)
    rejected=owner.expand(prep.GRC9V4ExpansionRequestInput.from_payload(stale))
    require(not rejected.committed and owner._published is published and owner.checkpoint()==checkpoint,'stale rollback')
    admissions=[];writers=[];real_step=prep.native.ProvisionalCandidatePCStep;real_writer=prep.native.candidate_a_writer_target
    def observed(before,differential):
        progress('event_readmission_pair_'+str(len(admissions)+1));step=real_step(before,differential)
        require(owner._published is published,'early publication')
        admissions.append(dict(current=read_capture(step.read,before),reset=read_capture(step.reset_read,replace(before,current=before.reset)),old_publication_live=True))
        return step
    def written(point,C):
        value=real_writer(point,C);expected_writer=writer_surface(point,C.values)
        require([list(x) for x in value[0]]==expected_writer['descriptors'] and list(value[1])==expected_writer['drive']
            and owner._published is published,'event writer surface')
        writers.append(dict(**expected_writer,old_publication_live=True));return value
    with patch.object(prep.native,'ProvisionalCandidatePCStep',observed),patch.object(prep.native,'candidate_a_writer_target',written):
        outcome=owner.expand(prep.GRC9V4ExpansionRequestInput.from_payload(request))
    require(outcome.committed,'native event failed: '+str(outcome.failure))
    require(prep.canonical_input_payload(owner.state.inputs.to_payload())==prep.canonical_input_payload(expected.to_payload()),'actual target')
    require(len(admissions)==2 and len(writers)==4,'both-role admission count')
    plan=prep.plan_for(seed,request);expansion=GRC9V4APCExpansion(plan,seed.inputs.geometry.reference,seed.inputs.current,seed.inputs.reset)
    archived=expansion.carrier_archive_payload()
    checkpoint=json.loads(owner.checkpoint())
    # The checkpoint/receipt contains the same archive; never manufacture a
    # separate successful archive from a transfer formula alone.
    require(contains(checkpoint,archived),'source carrier archive absent from published checkpoint')
    return dict(checkpoint=checkpoint,admissions=admissions,writer_surfaces=writers,carrier_archive=archived,
        request=request,event_id=plan.event_id,event_identity=plan.event_identity_payload(),stale_failure=rejected.failure.to_payload(),
        rollback_exact=True,native_events=1,native_steps=0)


def contains(value,target):
    if value==target:return True
    if isinstance(value,dict):return any(contains(v,target) for v in value.values())
    if isinstance(value,list):return any(contains(v,target) for v in value)
    return False


def step_oracle(before,initial):
    operand=subject(before);md=p.model(operand,'current');z=zrows(before.current);params=md['params']
    J=initial['oracle']['current'];rates=[sum(float(x)*j for x,j in zip(row,J)) for row in md['bv']]
    C=[float(x)-before.dt*r for x,r in zip(md['c'],rates)]
    with p.ctx.workprec(p.BITS):
        drive=p.writer_drive(md,C,J);W,we=p.write_w(list(before.current.W_A),drive,before.dt,md['p']['tau_A'])
        Z,ze=p.write_z(z,p.unpack(initial['oracle']['source']),before.dt,params['realization']['tau_PC'])
        exact=p.analytic(md,p.hodge(z,params['geometry']['kappa_H'])[1])['current']
        resources=[p.a(x)-p.a(before.dt)*sum((int(b)*j for b,j in zip(row,exact)),p.arb(0)) for x,row in zip(md['c'],md['bv'])]
        bounds=[dict(lower=str(p.lo(x)),upper=str(p.hi(x))) for x in resources]
    require(min(C)>0 and min(q(x['lower']) for x in bounds)>0,'local exact-PC resource signs')
    return dict(C=C,W_A=W,Z=p.sparse(Z),drive=drive,resource_bounds=bounds,
        W_rounding_error_upper=we,Z_rounding_error_upper=ze,
        W_stage='postcontinuity_C_incoming_W_selected_J',Z_stage='incoming_PC_read_held_source')


def charge_check(before,after,receipt):
    charge=prep.prior.charge_helpers.pairwise(after.current.C);params=before.geometry.reference.profile.params_resolved.to_payload()['charge']
    require(receipt==dict(target_charge=before.Q_target,admitted_charge=charge,residual=float(q(charge)-q(before.Q_target))),'charge receipt')
    require(abs(q(charge)-q(before.Q_target))<=q(params['absolute_tolerance'])+q(params['relative_tolerance'])*max(abs(q(before.Q_target)),q(1)),'charge tolerance')


def observe(before,*,effects=False):
    frozen=digest(before.to_payload());step=pc.ProvisionalCandidatePCStep(before,backend(before));after=step.next_inputs
    reads={name:read_capture(read,operand) for name,read,operand in
        (('current',step.read,before),('reset',step.reset_read,replace(before,current=before.reset)),('final',step.restart,replace(after,dt=0)))}
    expected=step_oracle(before,reads['current'])
    require(list(after.current.C)==expected['C'] and list(after.current.W_A)==expected['W_A']
        and p.sparse(zrows(after.current))==expected['Z'] and list(step.writer.W_drv_A)==expected['drive'],'independent C/W/Z evolution')
    require(digest(before.to_payload())==frozen and after.reset==before.reset and after.time==before.time+before.dt
        and after.step_index==before.step_index+1 and step.resource.continuity_evaluations==step.carrier_writes==1,'step lifecycle')
    charge=step.resource.charge.receipt_values();charge_check(before,after,charge)
    effect=None
    if effects:
        final=dict(C=list(after.current.C),W_A=list(after.current.W_A),Z=p.sparse(zrows(after.current)),final=reads['final']['oracle'])
        with p.ctx.workprec(p.BITS):effect=prep.h.separation(subject(before),'current',final)
        require(q(effect['margin'])>0 and effect['changed_current_coordinates']>0,'target carrier effect unresolved')
    return dict(before_digest=frozen,next_inputs=after.to_payload(),reads=reads,oracle=expected,
        charge=charge,exact_resource_sum_delta=str(sum(map(q,after.current.C),q(0))-sum(map(q,before.current.C),q(0))),
        carrier_separation=effect,reset_unchanged=True,native_steps=1,native_events=0,detached_continuation=True)


def incoming(segment,role,step):
    if segment=='step' and step==1:
        old=read('event');before=state(old['execution']['checkpoint']['state']).inputs
        before=replace(before,current=getattr(before,role),geometry=pc.carrier_geometry(before,getattr(before,role)),dt=DT)
    else:
        old=read('step',role,10 if segment=='final' else step-1)
        before=prep.GeometryStageInputs.from_payload(old['execution']['next_inputs'])
    require(old==seal(old) and old['outcome']=='completed','predecessor record')
    return before,old['record_digest']


def execute(segment,role,step,progress):
    if segment=='event':
        seed,old=baseline_source();_,expected=expected_event(seed,old['execution']['request'])
        return event_capture(seed,old['execution']['request'],expected,progress),old['record_digest']
    before,predecessor=incoming(segment,role,step)
    if segment=='step':return observe(before,effects=step in (1,10)),predecessor
    final=pc.CandidatePCRead(replace(before,dt=0),backend(before))
    return dict(read=read_capture(final,replace(before,dt=0)),native_steps=0,native_events=0,final_reads=1),predecessor


def worker(pipe,segment,role,step):
    try:
        with prep.validation_reuse(),prep.exact_backend(prep.ExactBackend.FLINT),prep.numerical_policy(prep.NumericalPolicy.CERTIFIED_ARB_256),prep.matrix_operation():
            result=execute(segment,role,step,lambda s:pipe.send(('progress',s)))
        pipe.send(('result',result))
    except Exception as exc:pipe.send(('error',dict(type=type(exc).__name__,message=str(exc))))
    finally:pipe.close()


@prep.in_policy
def check_step(e,before):
    after=prep.GeometryStageInputs.from_payload(e['next_inputs'])
    require(e['before_digest']==digest(before.to_payload()) and after.reset==before.reset and after.time==before.time+before.dt
        and after.step_index==before.step_index+1 and after.geometry==pc.carrier_geometry(after,after.current),'retained lifecycle')
    for name,operand in (('current',before),('reset',replace(before,current=before.reset)),('final',replace(after,dt=0))):check_read(e['reads'][name],operand)
    expected=e['oracle']
    require(list(after.current.C)==expected['C'] and list(after.current.W_A)==expected['W_A'] and p.sparse(zrows(after.current))==expected['Z']
        and expected['W_stage']=='postcontinuity_C_incoming_W_selected_J' and expected['Z_stage']=='incoming_PC_read_held_source'
        and min(q(x['lower']) for x in expected['resource_bounds'])>0,'retained independent evolution')
    charge_check(before,after,e['charge'])
    require(e['exact_resource_sum_delta']==str(sum(map(q,after.current.C),q(0))-sum(map(q,before.current.C),q(0)))
        and e['reset_unchanged'] and e['detached_continuation'] and e['native_steps']==1 and e['native_events']==0,'step scope/drift')
    if e['carrier_separation'] is not None:
        r=e['carrier_separation'];require(q(r['margin'])==q(r['effect_lower'])-q(r['two_read_error_upper'])>0 and r['changed_current_coordinates']>0,'carrier effect')
    return after


@prep.in_policy
def check(segment,role='current',step=1,value=None):
    m=manifest();require(m==json.loads((ROOT/INPUTS).read_text()),'campaign manifest drift')
    v=read(segment,role,step) if value is None else value
    cap=prep.CAPS['event' if segment=='event' else 'target_step' if segment=='step' else 'final_read']
    require(v==seal(v) and v['manifest_digest']==m['record_digest'] and v['outcome']=='completed' and 0<v['seconds']<=cap
        and (v['segment'],v['role'],v['step'])==(segment,role,step) and v['user_accepted'] is False and v['aggregate_closed'] is False,'segment identity/scope')
    e=v['execution']
    if segment=='event':
        seed,old=baseline_source();plan,target=expected_event(seed,e['request'])
        require(e['request']==old['execution']['request'] and v['predecessor_digest']==old['record_digest']
            and e['event_id']==plan.event_id and e['event_identity']==plan.event_identity_payload(),'event source identity')
        require(prep.canonical_input_payload(e['checkpoint']['state']['inputs'])==prep.canonical_input_payload(target.to_payload())
            and len(e['admissions'])==2 and len(e['writer_surfaces'])==4 and e['rollback_exact'] and bool(e['stale_failure'])
            and e['native_events']==1 and e['native_steps']==0,'event scope/target')
        archive=GRC9V4APCExpansion(plan,seed.inputs.geometry.reference,seed.inputs.current,seed.inputs.reset).carrier_archive_payload()
        require(e['carrier_archive']==archive and contains(e['checkpoint'],archive),'whole carrier archive')
        for i,operand in enumerate((seed.inputs,target)):
            require(e['admissions'][i]['old_publication_live'],'publication order')
            for j,r in enumerate(ROLES):
                before=replace(operand,current=getattr(operand,r));check_read(e['admissions'][i][r],before)
                w=e['writer_surfaces'][2*i+j]
                require(w['C']==list(before.current.C) and w['W_A']==list(before.current.W_A)
                    and w['J']==e['admissions'][i][r]['actual']['current'] and w['old_publication_live'],'event writer operand')
    else:
        before,old=incoming(segment,role,step);require(v['predecessor_digest']==old,'segment chain')
        if segment=='step':
            check_step(e,before)
            require((e['carrier_separation'] is not None)==(step in (1,10)),'declared effect pressure')
        else:
            check_read(e['read'],replace(before,dt=0));require(e['native_steps']==e['native_events']==0 and e['final_reads']==1,'final read scope')
    return v


def run(segment,role='current',step=1):
    if (ROOT/path(segment,role,step)).exists():check(segment,role,step);print('retained, no rerun');return
    m=manifest();require(m==json.loads((ROOT/INPUTS).read_text()),'campaign manifest drift')
    cap=prep.CAPS['event' if segment=='event' else 'target_step' if segment=='step' else 'final_read']
    (result,predecessor),seconds=prep.capped(worker,(segment,role,step),cap)
    require(m==manifest(),'sources changed during run')
    v=seal(dict(schema='p984h-apc-segment-v1',manifest_digest=m['record_digest'],segment=segment,role=role,step=step,
        execution=result,predecessor_digest=predecessor,seconds=seconds,outcome='completed',user_accepted=False,aggregate_closed=False))
    check(segment,role,step,v);prep.save(path(segment,role,step),v)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=('prepare','run','check','chain'))
    parser.add_argument('--segment',choices=('event','step','final'),default='event');parser.add_argument('--role',choices=ROLES,default='current')
    parser.add_argument('--step',type=int,default=1);args=parser.parse_args()
    if args.action=='prepare':
        with (ROOT/INPUTS).open('x') as stream:json.dump(manifest(),stream,indent=2);stream.write('\n')
    elif args.action=='chain':
        for k in range(1,11):run('step',args.role,k)
        run('final',args.role,10)
    elif args.action=='run':run(args.segment,args.role,args.step)
    else:check(args.segment,args.role,args.step);print('retained check passes; no native rerun')
