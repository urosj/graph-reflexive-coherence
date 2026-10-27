"""Bounded first-group conformance review; no numerical execution or support grant."""
import argparse
import json
import lzma
from pathlib import Path
import p984i_first_group as handoff
from pygrc.models.grc_v4_codec import canonical_json_bytes

ROOT=handoff.ROOT
BASE=handoff.BASE
HERE=handoff.HERE
FAMILIES=handoff.FAMILIES
TAGS=dict(zip(FAMILIES,('COS','CCI','ACI','APC')))
SELF=HERE+'p986_first_group.py'
REVIEW=BASE+'P9-8.6-FirstGroupReview.md'
SHARED=BASE+'P9-8.6-Shared.json'
RESULT=BASE+'P9-8.6-FirstGroup.json'
HANDOFF_DIGEST='f48d1cc06f8ffdf02285cb158e7e1f3315c75eed1b70a440400688d1022d5822'
ACCEPTANCE=BASE+'P9-8.5-FirstGroupAcceptance.json'
ACCEPTANCE_DIGEST='64f102670b4a46d0310ac2d2b2f6eca819dafb24203019408fe4e3d2ce42045c'
seal,require,sha,safe=handoff.seal,handoff.require,handoff.sha,handoff.safe

# Scope findings from the accepted family reviews; not new solver assertions.
SCOPES={
 'C_OS':dict(mechanism='predictor/corrector/final-C OS reads and split admission',
   numerical_scope='certified first-step signs; later represented admission and dense comparisons, no ten-step exact-real enclosure',
   exclusion='original phase-one/deep negative-resource and charge controls; larger source uses the admitted second beat',
   limitation='small first-step resources require the saved sign certificate; dense agreement alone does not certify positivity'),
 'C_CI':dict(mechanism='joint current/geometry root, same-root source and final-C reconstruction',
   numerical_scope='local exact-root resource bounds at each represented input; checked first-pass/reference-geometry condition',
   exclusion='original larger targets have negative exact-root first steps; allocation-only companion loses source eligibility',
   limitation='no above-rounding CI feedback separation or uniform trajectory enclosure'),
 'A_CI':dict(mechanism='fixed-row joint root, unsigned W lineage and post-continuity history writer',
   numerical_scope='local exact-root bounds, two consecutive stopping passes and final-C/W readmission',
   exclusion='original larger reset-as-current target is negative; admitted history/allocation and actual reset chronology required',
   limitation='root residuals do not resolve every feedback mechanism; nonzero represented charge uses the unchanged tolerance'),
 'A_PC':dict(mechanism='fixed-carrier point, unsigned W transport/writer, whole-Z archive/loss/zero target, held-source Z writer',
   numerical_scope='local exact-PC resource bounds; carrier effects exceed combined error at baseline steps one and ten',
   exclusion='original D94 and resource-only/history-only companions remain excluded; failed 11/16 history is not the successful 7/8 companion',
   limitation='resolved carrier effects are small and pointwise; no robust parameter-neighborhood or uniform trajectory margin'),
}
LIMITS=dict(arbitrary_graph_numerical_admission=False,uniform_trajectory_enclosure=False,
    exact_stored_resource_conservation=False,public_specialization_facade=False,
    general_ATC=False,new_G2_G3_support=False,all_ten_closed=False,current_runtime_conformance_inferred=False)


def load(root,name):
    value=json.loads(safe(root,name).read_bytes())
    require(value==seal(value),'record digest drift: '+name)
    return value


def path(family):
    require(family in FAMILIES,'unsupported conformance family')
    return BASE+'P9-8.6-'+TAGS[family]+'.json'


def shared(root):
    h=load(root,handoff.RESULT);a=load(root,ACCEPTANCE)
    require(h['record_digest']==HANDOFF_DIGEST and a['record_digest']==ACCEPTANCE_DIGEST,'unaccepted predecessor')
    require(a['first_group_closed'] and a['user_accepted'] and set(a['families'])==set(FAMILIES),'8.5 prerequisite incomplete')
    return seal(dict(schema='p986-shared-prerequisites-v1',handoff_digest=h['record_digest'],
        lifecycle_acceptance_digest=a['record_digest'],families=list(FAMILIES),
        shared_source_count=len(h['source_refs']),atomic_failure_vectors=h['atomic_failure_vectors'],
        authority_traces=h['authority_traces'],
        mechanical_scope='accepted recursive allocator contract and executed deep/covariance cases; numerical admission remains conditional',
        scientific_ledger_rewritten=False,numerical_trajectories_rerun=False,
        source_refs=[handoff.reference(root,n) for n in (handoff.RESULT,handoff.AUTHORITY,ACCEPTANCE)]))


def check_shared(root):
    v=load(root,SHARED);require(v==shared(root),'shared prerequisite drift')
    return v


def exact_domain(root,row):
    raw=handoff.authenticate(root,row['witness_ref'])
    event=json.loads(lzma.decompress(raw));cp=event['execution']['checkpoint']
    require(event==seal(event) and event['record_digest']==row['event_record_digest'], 'event lineage mismatch')
    profiles={role:cp[role]['inputs']['reference']['profile']['complete_profile_id'] for role in ('initial','state')}
    graphs={role:dict(vertices=len(cp[role]['inputs']['reference']['graph']['live_node_ids']),
        edges=len(cp[role]['inputs']['reference']['graph']['edges'])) for role in ('initial','state')}
    return dict(profiles=profiles,graphs=graphs,event_id=row['event_id'],
        source_state_digest=row['source_state_digest'],target_state_digest=row['target_state_digest'],
        target_reset_digest=row['target_reset_digest'],checkpoint_sha256=sha(canonical_json_bytes(cp)),
        baseline_horizon_per_role=10,mapped_horizon_per_role=1,mapped_events=8,
        domain_is_exact_tested_subjects=True)


def review_family(root,family):
    """One independent worker: actual accepted lifecycle check plus exact 8.4 subjects."""
    from p985_status import view
    s=check_shared(root);h=load(root,handoff.RESULT);row=handoff.one(h['families'],family)
    lifecycle=view(root,family)
    require(lifecycle['user_accepted'] and lifecycle['first_group_closed'],'unaccepted lifecycle')
    domain=exact_domain(root,row)
    large=lifecycle['executions']['large']['observations']
    require(large['checkpoint_sha256']==domain['checkpoint_sha256'],'8.4/8.5 checkpoint mismatch')
    refs=handoff.unique_refs([lifecycle['source_refs'],s['source_refs'],row['witness_ref'],
        handoff.reference(root,SHARED),handoff.reference(root,SELF)])
    return seal(dict(schema='p986-family-conformance-v1',family=family,verdict='bounded_conformance_pass',
        user_accepted=False,shared_digest=s['record_digest'],handoff_row_digest=seal(row)['record_digest'],
        accepted_8_4_cells=row['accepted_history_cells'],larger_8_4=row['larger'],
        lifecycle_8_5=dict(manifest_digest=lifecycle['manifest_digest'],
            execution_digests={k:r['record_digest'] for k,r in lifecycle['executions'].items()},
            small_tests=lifecycle['executions']['small']['observations']['tests'],large_exact_replays=1),
        exact_domain=domain,
        scientific_scope=SCOPES[family],limits=LIMITS,
        evidence_kind='retained accepted execution and authority reconciliation; no new native or independent numerical proof',
        numerical_trajectories_rerun=False,source_refs=refs))


def validate_family(v,h,s,a,root=ROOT):
    f=v['family'];require(f in FAMILIES,'unsupported family')
    row=handoff.one(h['families'],f)
    require(v==seal(v) and v['verdict']=='bounded_conformance_pass' and not v['user_accepted']
        and v['shared_digest']==s['record_digest'] and v['handoff_row_digest']==seal(row)['record_digest'],'family review drift')
    require(v['limits']==LIMITS and v['scientific_scope']==SCOPES[f] and not v['numerical_trajectories_rerun'],'conformance scope widening')
    require(v['accepted_8_4_cells']==row['accepted_history_cells'] and v['larger_8_4']==row['larger'],'coverage drift')
    d=v['exact_domain']
    require(d==exact_domain(root,row),'exact conformance domain drift')
    require(d['domain_is_exact_tested_subjects'] and (d['baseline_horizon_per_role'],d['mapped_horizon_per_role'],d['mapped_events'])==(10,1,8),'horizon widening')
    require(d['event_id']==row['event_id'] and d['source_state_digest']==row['source_state_digest']
        and d['target_state_digest']==row['target_state_digest'] and d['target_reset_digest']==row['target_reset_digest'],'subject lineage drift')
    q=v['lifecycle_8_5'];expected=a['families'][f]
    require(q['manifest_digest']==expected['manifest_digest'] and q['execution_digests']==expected['execution_digests']
        and q['small_tests']==(8 if f=='C_OS' else 6) and q['large_exact_replays']==1,'lifecycle coverage drift')


def assemble(root,authenticate=True):
    s=check_shared(root);h=load(root,handoff.RESULT);a=load(root,ACCEPTANCE);rows=[]
    for f in FAMILIES:
        v=load(root,path(f));validate_family(v,h,s,a,root);rows.append(v)
    refs=handoff.unique_refs([h['source_refs'],*[r['source_refs'] for r in rows]]+[
        [handoff.reference(root,n) for n in (REVIEW,SELF,SHARED,*[path(f) for f in FAMILIES])]])
    if authenticate:
        for r in refs:handoff.authenticate(root,r)
    return seal(dict(schema='p986-first-group-decision-v1',checkpoint='P9-8.6[first-group]',
        status='bounded_conformance_pass_pending_acceptance',user_accepted=False,first_group_closed=False,
        aggregate_closed=False,families=rows,limits=LIMITS,remaining_families=list(handoff.OTHERS),
        numerical_trajectories_rerun=False,scientific_ledger_rewritten=False,
        counts=dict(families=4,prior_8_4_events=36,prior_8_4_target_steps=144,prior_8_4_final_reads=8,
            prior_8_5_small_tests=26,prior_8_5_large_replays=4,new_native_events=0,new_native_steps=0),
        source_refs=refs))


def check(root=ROOT):
    v=load(root,RESULT);require(v==assemble(root),'retained conformance decision drift');return v


def status(root=ROOT,family='first_group'):
    require(family in ('first_group',*FAMILIES),'unsupported conformance scope')
    v=check(root)
    return dict(schema='phase9_tranche8_conformance_v1',checkpoint='8.6',family=family,
        decision=v if family=='first_group' else handoff.one(v['families'],family),
        group_record_digest=v['record_digest'],user_accepted=False,first_group_closed=False,aggregate_closed=False,
        numerical_trajectories_rerun=False,source_refs=handoff.unique_refs([v['source_refs'],handoff.reference(root,RESULT)]))


def write(name,value):
    raw=json.dumps(value,indent=2)+'\n';require(len(raw.encode())<1_000_000,'compress evidence over 1 MB')
    with safe(ROOT,name).open('x') as f:f.write(raw)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=('shared','record','check','status'))
    p.add_argument('--family',choices=('first_group',*FAMILIES),default='first_group');args=p.parse_args()
    if args.action=='shared':write(SHARED,shared(ROOT));print('shared prerequisites recorded')
    elif args.action=='record':
        v=assemble(ROOT) if args.family=='first_group' else review_family(ROOT,args.family)
        write(RESULT if args.family=='first_group' else path(args.family),v)
        print(args.family+': bounded conformance PASS, pending acceptance; no numerics')
    elif args.action=='status':print(json.dumps(status(ROOT,args.family)))
    else:check();print('P9-8.6 retained decision PASS; no numerics')
