"""C_CI ordering covariance of full joint roots, not current-only agreement.

Reuses accepted transformation algebra and CI interval equations. Only run
executes native operations; retained checking never reconstructs native roots.
"""
import argparse
from contextlib import ExitStack
from copy import deepcopy
from dataclasses import replace
import json
from unittest.mock import patch

import p984e_cos as algebra
import p984d_cci as prior
from pygrc.models.grc_9_v4_expansion import cci_profile_template

r, b, certificate = prior.r, prior.b, prior.certificate
SELF=b.HERE+'p984e_cci.py'
TEST=b.HERE+'test_p984e_cci.py'
PLAN=b.BASE+'P9-8.4e-CCIPlan.md'
INPUTS=b.BASE+'P9-8.4e-CCIInputs.json'
RESULTS=b.BASE+'P9-8.4e-CCIResults.json'
REVIEW=b.BASE+'P9-8.4e-CCIReview.md'
ROLES, KINDS = algebra.ROLES, algebra.KINDS


def make_manifest():
    deep=b.read(prior.INPUTS);phase=b.read(r.INPUTS)
    for value in (deep,phase):
        b.check_digest(value);b.check_bindings(value['source_bindings'])
    b.require(deep['initial_inputs']==phase['initial_inputs'],'different predecessor sources')
    cases=[next(c for c in phase['cases'] if c['request']['target_effective_degree']==52
                and c['request']['module_chirality']==1 and c['request']['growth_phase']==1),
           next(c for c in deep['cases'] if c['request']['target_effective_degree']==94
                and c['request']['module_chirality']==-1 and c['request']['growth_phase']==3)]
    traces=algebra.authority()
    paths={SELF,TEST,PLAN,algebra.SELF,prior.INPUTS,prior.REVIEW,r.INPUTS,r.REVIEW,
           prior.SELF,prior.previous.SELF,b.HERE+'p984d_cci_certificate.py'}
    paths|={x['path'] for m in (deep,phase) for x in m['source_bindings']}
    paths|={x['source_ref']['path'] for t in traces.values() for x in t['rows']}
    return b.seal(dict(schema='p984e-cci-inputs-v1',family='C_CI',source_bindings=b.bind(paths),
        initial_inputs=deep['initial_inputs'],expected_source=deep['expected_source'],cases=cases,
        transforms=algebra.declarations(),authority=traces,
        comparison=dict(norm='componentwise_abs_plus_relative',atol=2e-13,rtol=2e-13),
        scope=dict(layouts=2,transforms=5,required_history_cells=20,native_events=12,
                   target_steps=48,steps_per_role=2,final_reads=24,source_steps=6,
                   chart_symmetries=False,uniform_domain=False,full_joint_roots=True),
        user_accepted=False,aggregate_closed=False))


def check_manifest(m):
    b.check_digest(m);b.check_bindings(m['source_bindings'])
    b.require(m==make_manifest(),'covariance declaration drift')


def expected_event(source,case,declaration):
    seed=r.state(source);ref=seed.inputs.geometry.reference
    nodes,_=algebra.labels(declaration);request=deepcopy(case['request'])
    request.update(source_state_digest=seed.scientific_digest,source_graph_digest=ref.graph.graph_digest,
        source_node_id=nodes['s'],target_profile_template_id=cci_profile_template(ref).profile_template_id,
        operation_id='p984e-cci-'+str(request['target_effective_degree'])+'-'+declaration['kind'])
    identity=deepcopy(case['oracle']['event_identity'])
    for key in identity:
        if key in request and key!='schema_version':identity[key]=request[key]
    event='grc-event-sha256:'+b.digest(identity)
    graph=algebra.transported_graph(case['oracle']['target_graph'],declaration,case['oracle']['event_id'],event)
    p=deepcopy(source['inputs']);reference=p['reference'];reference['graph']=graph
    weights={e['edge_id']:1 for e in graph['edges']};size=len(weights)
    reference['K4_base']=[[0.0]*size for _ in range(size)]
    reference['reference_hodge']['edge_weights']=weights.copy()
    reference['profile']['params_resolved']['candidate']['W_C_tr']=weights.copy()
    algebra.reidentify(reference)
    p['H1_form']=[[float(i==j) for j in range(size)] for i in range(size)]
    for role in ROLES:
        old=dict(zip(ref.graph.live_node_ids,p[role]['C'],strict=True))
        image={n:old.get(n,0.) for n in graph['live_node_ids']}
        for j,share in enumerate(request['resource_distribution'],1):
            image[event+f'/satellite/{j}']=float(b.Fraction(old[nodes['s']])*b.Fraction(share))
        p[role]['C']=[image[n] for n in graph['live_node_ids']]
    p.update(dt=0,operation_id=request['operation_id'])
    return request,identity,algebra.materialize(source['inputs'],p)


def execute_source(m,d):
    before=b.GeometryStageInputs.from_payload(algebra.transform(m['initial_inputs'],d))
    step=r.ProvisionalCandidateCIStep(before)
    seed=replace(r.state(m['expected_source']),inputs=replace(step.next_inputs,dt=0))
    return dict(kind=d['kind'],step=r.capture_step(step),state=seed.to_payload())


def execute_case(m,source,case,d):
    request,identity,expected=expected_event(source['state'],case,d)
    seed=r.state(source['state']);owner=r.native.GRC9V4CCIOperation(seed);before=owner.checkpoint()
    stale=deepcopy(request);stale['source_state_digest']='grcv4-state-sha256:'+'0'*64
    rejected=owner.expand(b.GRC9V4ExpansionRequestInput.from_payload(stale))
    b.require(not rejected.committed and owner.checkpoint()==before,'stale request rollback')
    owner,outcome,event=r.event_capture(seed,b.GRC9V4ExpansionRequestInput.from_payload(request))
    b.require(outcome.committed,'native event rejected: '+str(outcome.failure))
    b.require(owner.state.to_payload()==replace(seed,inputs=expected).to_payload(),'independent target mismatch')
    roles={}
    for role in ROLES:
        incoming=replace(owner.state.inputs,current=getattr(owner.state.inputs,role),dt=b.DT);steps=[]
        for _ in range(m['scope']['steps_per_role']):
            step=r.ProvisionalCandidateCIStep(incoming);steps.append(r.capture_step(step));incoming=step.next_inputs
        roles[role]=dict(steps=steps,final=r.certified_root(r.CandidateCIRoot(replace(incoming,dt=0))))
    return dict(layout=case['fixture_id'],kind=d['kind'],request=request,event_identity=identity,
        event_id='grc-event-sha256:'+b.digest(identity),event_committed=True,case_passed=True,
        event=event,roles=roles,stale_request_control=dict(committed=False,rollback_exact=True,
            failure=rejected.failure.to_payload()))


def root_pair(base,other,indices,policy):
    _,ei,s=indices;errors=[]
    b.require(base['domain_id']==other['domain_id'] and base['recipe']==other['recipe'],'root contract covariance')
    for field in ('J','read_current','baseline','readback','flat','H','source','generated'):
        a=b.np.array(base[field]);expected=a[b.np.ix_(ei,ei)]*b.np.outer(s,s) if a.ndim==2 else a[ei]*s
        errors.append(b.comparison(other[field],expected,policy,'joint_covariance_'+field)['maximum_error'])
    return max(errors)


def check(m,record,*,numerics=False):
    check_manifest(m);b.check_digest(record)
    b.require(record['schema']=='p984e-cci-results-v1' and record['manifest_digest']==m['record_digest']
              and record['user_accepted'] is False and record['aggregate_closed'] is False,'result scope')
    data=prior.previous.expand(record['execution']);sources=data['sources'];rows=data['cases'];policy=m['comparison']
    b.require([s['kind'] for s in sources]==list(KINDS),'source roster')
    b.require([(x['layout'],x['kind']) for x in rows]==[(c['fixture_id'],d['kind']) for c in m['cases'] for d in m['transforms']],'case roster')
    max_error=0.
    def states_pair(a,c,indices):
        nonlocal max_error
        for role in ROLES:
            max_error=max(max_error,b.comparison(c[role]['C'],b.np.array(a[role]['C'])[indices[0]],policy,'covariance_'+role+'_C')['maximum_error'])
            b.require(c[role]['W_A'] is None and c[role]['Z_4'] is None,'history leakage')
    def roots_pair(a,c,indices):
        nonlocal max_error
        max_error=max(max_error,root_pair(a,c,indices,policy))
    with certificate.checker():
        for source,d in zip(sources,m['transforms'],strict=True):
            before=b.GeometryStageInputs.from_payload(algebra.transform(m['initial_inputs'],d))
            after=r.check_step(before,source['step'],numerics=numerics)
            b.require(replace(after,dt=0).to_payload()==source['state']['inputs'],'source poststate substitution')
            indices=algebra.mapping(m['initial_inputs']['reference']['graph'],before.geometry.reference.graph.to_payload(),d)
            states_pair(sources[0]['state']['inputs'],source['state']['inputs'],indices)
            for key in ('root','reset_root','restart'):roots_pair(sources[0]['step'][key],source['step'][key],indices)
        for case in m['cases']:
            base=next(x for x in rows if x['layout']==case['fixture_id'] and x['kind']=='base')
            for d,source in zip(m['transforms'],sources,strict=True):
                row=next(x for x in rows if x['layout']==case['fixture_id'] and x['kind']==d['kind'])
                request,identity,expected=expected_event(source['state'],case,d)
                b.require(row['request']==request and row['event_identity']==identity
                    and row['event_id']=='grc-event-sha256:'+b.digest(identity),'event/request binding')
                b.require(row['event_committed'] is True and row['case_passed'] is True,'incomplete event')
                seed=r.state(source['state'])
                target=check_event(seed,dict(request=request,oracle=dict(event_id=row['event_id'])),row['event'],expected,numerics=numerics)
                control=row['stale_request_control']
                b.require(control['committed'] is False and control['rollback_exact'] is True and bool(control['failure']),'missing stale request control')
                b.require(set(row['roles'])==set(ROLES),'role coverage')
                bg=base['event']['actual_target']['inputs']['reference']['graph'];tg=target.inputs.geometry.reference.graph.to_payload()
                b.require(algebra.transported_graph(bg,d,base['event_id'],row['event_id'])==tg,'normalized target graph')
                indices=algebra.mapping(bg,tg,d,base['event_id'],row['event_id'])
                states_pair(base['event']['actual_target']['inputs'],target.inputs.to_payload(),indices)
                for key in ('root','reset_root'):
                    roots_pair(base['event']['admission_reads'][1][key],row['event']['admission_reads'][1][key],indices)
                for role in ROLES:
                    rr=row['roles'][role];br=base['roles'][role];incoming=replace(target.inputs,current=getattr(target.inputs,role),dt=b.DT)
                    b.require(len(rr['steps'])==2,'continuation horizon')
                    for k,step in enumerate(rr['steps']):
                        incoming=r.check_step(incoming,step,numerics=numerics)
                        states_pair(br['steps'][k]['poststate'],step['poststate'],indices)
                        for key in ('root','reset_root','restart'):roots_pair(br['steps'][k][key],step[key],indices)
                    r.check_root(replace(incoming,dt=0),rr['final'],numerics=numerics)
                    roots_pair(br['final'],rr['final'],indices)
    return dict(family='C_CI',status='executed_pending_review',required_cells=20,passing_pending_cells=20,
        accepted_cells=0,native_events=12,target_steps=48,source_steps=6,final_reads=24,
        maximum_covariance_error=max_error,transforms=list(KINDS[1:]),degrees=[52,94],full_joint_roots=True,
        native_trajectories_rerun=False,interval_certificates_rerun=numerics,uniform_domain=False,aggregate_closed=False)


def check_event(seed, case, value, expected, *, numerics=False):
    """Accepted CI event checks, with independently label-transported target."""
    target = replace(seed, inputs=expected)
    initial = value["source_checkpoint"]
    b.require(initial["initial"] == seed.to_payload() and initial["state"] == seed.to_payload()
              and initial["requests"] == [] and initial["receipts"] == [], "source checkpoint drift")
    b.require(
        value["actual_target"] == target.to_payload(),
        "independent graph/reference/resource transfer drift",
    )
    b.require(len(value["admission_reads"]) == 2, "missing source/target admission")
    for parent, observed in zip((seed, target), value["admission_reads"], strict=True):
        b.require(
            observed["inputs"] == parent.inputs.to_payload()
            and observed["published_state"] == seed.scientific_digest,
            "admission operand/publication drift",
        )
        r.check_root(parent.inputs, observed["root"], numerics=numerics)
        r.check_root(
            replace(parent.inputs, current=parent.inputs.reset),
            observed["reset_root"],
            numerics=numerics,
        )
    detection = value["detections"]
    b.require(
        len(detection) == 1
        and detection[0]["current"] == value["admission_reads"][0]["root"]["J"]
        and case["request"]["source_node_id"] in detection[0]["candidate_node_ids"]
        and detection[0]["published_state"] == seed.scientific_digest,
        "fresh trigger/current binding drift",
    )
    b.require(
        value["publication"]
        == [dict(admission_pairs=2, published_state=seed.scientific_digest)],
        "publication preceded both-role admission",
    )
    cp = value["checkpoint"]
    b.require(
        cp["initial"] == seed.to_payload()
        and cp["state"] == target.to_payload()
        and cp["requests"] == [case["request"]]
        and cp["receipts"] == value["receipts"],
        "checkpoint drift",
    )
    refs = cp["reference_currents"]
    source_ref, target_ref = (
        seed.inputs.geometry.reference,
        target.inputs.geometry.reference,
    )
    b.require(
        len(refs) == 1
        and refs[0]["event_id"] == case["oracle"]["event_id"]
        and refs[0]["source_graph_digest"] == source_ref.graph.graph_digest
        and refs[0]["target_graph_digest"] == target_ref.graph.graph_digest,
        "reference lineage identity drift",
    )
    for role, key in (("current", "root"), ("reset", "reset_root")):
        old = value["admission_reads"][0][key]["J"]
        currents = dict(zip(source_ref.graph.live_edge_ids, old, strict=True))
        expected_j = [currents.get(e, 0.0) for e in target_ref.graph.live_edge_ids]
        b.require(
            refs[0]["roles"][role] == dict(source=old, target=expected_j),
            "reference current map drift",
        )
        b.require(
            sum(map(b.Fraction, getattr(seed.inputs, role).C))
            == sum(map(b.Fraction, getattr(target.inputs, role).C)),
            "exact event charge changed",
        )
    receipts = value["receipts"]
    b.require(len(receipts) == 4, "event receipt count drift")
    _, checked = r.native.make_commit_receipts(
        [r["identity_payload"] for r in receipts],
        operation_id=case["request"]["operation_id"],
        source_state_digest=seed.scientific_digest,
        target_state_digest=target.scientific_digest,
        target_step_index=target.inputs.step_index,
        target_time=target.inputs.time,
    )
    b.require(
        [r.to_payload() for r in checked] == receipts
        and cp["lifecycle_digest"] == target.lifecycle_digest(checked),
        "receipt/commit digest drift",
    )
    first = receipts[0]["identity_payload"]
    b.require(
        first["event_id"] == case["oracle"]["event_id"]
        and first["core"]["information_losses"] == [],
        "event/loss drift",
    )
    for channel, disposition in (
        ("candidate", "rederived"),
        ("carrier", "not_applicable"),
    ):
        b.require(
            first["history"][channel]
            == dict(
                subject=channel,
                disposition=disposition,
                source_history_digest=None,
                target_history_digest=None,
                information_loss="none",
            ),
            "C_CI history receipt drift",
        )
    b.require(
        value["failure"] is None and value["replay_identical"] is True,
        "event/replay incomplete",
    )
    return target



def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=('prepare','run','check'))
    parser.add_argument('--recheck-numerics',action='store_true');args=parser.parse_args()
    if args.mode=='prepare':b.write_new(INPUTS,make_manifest());return
    m=b.read(INPUTS);check_manifest(m)
    if args.mode=='check':
        with ExitStack() as stack:
            for module,name in ((r,'ProvisionalCandidateCIStep'),(r,'CandidateCIRoot'),(r.native,'GRC9V4CCIOperation')):
                stack.enter_context(patch.object(module,name,side_effect=AssertionError('native producer forbidden')))
            print(json.dumps(check(m,b.read(RESULTS),numerics=args.recheck_numerics),indent=2))
        return
    b.require(not (b.ROOT/RESULTS).exists(),'refuse overwrite')
    with b.exact_backend(b.ExactBackend.FLINT),certificate.checker():
        sources=[execute_source(m,d) for d in m['transforms']];rows=[]
        for case in m['cases']:
            for source,d in zip(sources,m['transforms'],strict=True):
                rows.append(execute_case(m,source,case,d));print(case['fixture_id'],d['kind'],'passed',flush=True)
    record=b.seal(dict(schema='p984e-cci-results-v1',manifest_digest=m['record_digest'],
        execution=prior.previous.compact(dict(sources=sources,cases=rows)),user_accepted=False,aggregate_closed=False))
    summary=check(m,record,numerics=True);b.write_new(RESULTS,record);print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
