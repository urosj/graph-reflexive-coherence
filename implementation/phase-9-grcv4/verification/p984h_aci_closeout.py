"""Lean retained A_CI coverage/checkpoint review; no native reruns."""
import argparse
import json
from pathlib import Path
import p984h_aci_campaign as c
import p984h_aci_covariance as cov

SELF=c.HERE+'p984h_aci_closeout.py'
TEST=c.HERE+'test_p984h_aci_closeout.py'
RESULTS=c.BASE+'P9-8.4h-ACICloseout.json'


def checkpoint(execution):
    cp=execution['checkpoint']; before,after=c.state(cp['initial']),c.state(cp['state'])
    request=execution['request']
    for label,obj in (('initial',before),('state',after)):
        materialized=obj.to_payload()
        c.require(c.p.canonical_input_payload(cp[label]['inputs'])==c.p.canonical_input_payload(materialized['inputs'])
            and all(cp[label][key]==materialized[key] for key in ('scientific_digest','reset_digest','model_identity','specialization')),
            'checkpoint state identity')
    c.require(cp['requests']==[request] and request['source_state_digest']==before.scientific_digest
        and after.inputs.time==before.inputs.time and after.inputs.step_index==before.inputs.step_index,'checkpoint request/clock')
    payloads=[r['identity_payload'] for r in cp['receipts']]
    commit,receipts=c.p.native.make_commit_receipts(payloads,operation_id=request['operation_id'],
        source_state_digest=before.scientific_digest,target_state_digest=after.scientific_digest,
        target_step_index=after.inputs.step_index,target_time=after.inputs.time)
    c.require(len(receipts)==4 and [r.to_payload() for r in receipts]==cp['receipts']
        and after.lifecycle_digest(receipts)==cp['lifecycle_digest'],'checkpoint commit/ledger identity')
    for payload in payloads:
        core=payload['core']
        c.require(core['source_state_digest']==before.scientific_digest and core['target_state_digest']==after.scientific_digest
            and core['source_reset_digest']==before.reset_digest and core['target_reset_digest']==after.reset_digest
            and core['operation_id']==request['operation_id'] and core['parent_receipt_ids']==[]
            and core['disposition']=='committed' and core['information_losses']==[],'receipt actual-state binding')
    c.require(payloads[0]['event_id']==execution['event_id']
        and payloads[0]['history']['candidate']['disposition']=='exact_transport'
        and payloads[0]['history']['candidate']['information_loss']=='none','candidate history receipt')
    c.require(len(cp['reference_currents'])==1,'reference-current roster')
    ref=cp['reference_currents'][0]
    c.require(ref['event_id']==execution['event_id']
        and ref['source_graph_digest']==before.inputs.geometry.reference.graph.graph_digest
        and ref['target_graph_digest']==after.inputs.geometry.reference.graph.graph_digest,'reference-current identity')
    for role in c.ROLES:
        source_current=execution['admissions'][0][role]['actual']['current']
        old=dict(zip(before.inputs.geometry.reference.graph.live_edge_ids,source_current,strict=True))
        expected=[old.get(edge,0.) for edge in after.inputs.geometry.reference.graph.live_edge_ids]
        c.require(ref['roles'][role]==dict(source=source_current,target=expected),'reference-current lineage')
    return dict(event_id=execution['event_id'],receipts=len(receipts),commit_id=receipts[0].commit_id,
        lifecycle_digest=cp['lifecycle_digest'],both_role_reference_lineage=True)


def review():
    # The per-segment execution already ran its scientific comparator before
    # retention. This final review authenticates those bytes and linked coverage.
    import tranche8_evidence as index
    # Recheck execution coverage independently of later user acceptance.
    from p984h_aci_status import view
    status=view(index.Sources(index.ROOT),index.LARGER_RUNTIME_ACI_SOURCES)
    c.require(status['continuation']['baseline_complete'] and status['covariance']['covariance_complete']
        and (status['native_steps'],status['total_native_events'],status['total_target_steps'],status['final_reads'])==(1,9,36,2)
        and not status['user_accepted'] and not status['aggregate_closed'],'complete bounded roster')
    cases=[checkpoint(c.read('event')['execution'])]
    cases.extend(checkpoint(cov.read(kind,'event')['execution']) for kind in cov.KINDS)
    names=[c.source.RESULT,c.path('event'),*(c.path('step',r,k) for r in c.ROLES for k in range(1,11)),
        *(c.path('final',r,10) for r in c.ROLES),*(cov.path(k,s) for k in cov.KINDS for s in ('event',*c.ROLES))]
    total=sum((c.ROOT/n).stat().st_size for n in names)
    c.require(total<=20000000,'A_CI total compressed evidence budget')
    return c.seal(dict(schema='p984h-aci-closeout-v1',family='A_CI',native_source_steps=1,native_events=9,target_steps=36,
        final_roots=2,event_checkpoints=cases,compressed_bytes=total,
        record_bindings={n:c.p.sha(n) for n in names},
        checker_bindings={n:c.p.sha(n) for n in (SELF,TEST,c.HERE+'p984h_aci_status.py')},
        numerical_trajectories_rerun=False,interval_oracles_rerun=False,
        bounded_coverage_complete=True,uniform_trajectory_enclosure=False,user_accepted=False,aggregate_closed=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=('record','check'));a=parser.parse_args()
    result=review()
    if a.action=='record':
        with (c.ROOT/RESULTS).open('x') as stream:json.dump(result,stream,indent=2);stream.write('\n')
    else:c.require(result==json.loads((c.ROOT/RESULTS).read_text()),'closeout drift')
    print(json.dumps({k:result[k] for k in ('native_events','target_steps','final_roots','compressed_bytes','bounded_coverage_complete','user_accepted')}))
