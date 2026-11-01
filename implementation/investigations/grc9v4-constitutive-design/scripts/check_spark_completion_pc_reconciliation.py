"""C_PC research accounting, false-completion controls and retained reconciliation."""
from copy import deepcopy
import argparse
import json
import lzma
from fractions import Fraction as F
from flint import arb_mat, ctx, fmpq
import check_spark_completion_applicability_pc as pc
from spark_completion_pc_campaign import distance
from spark_completion_pc import CPCReference
from spark_completion_positive import content_id
from spark_completion_continuation import need, geometric_roster


def read_role(role):
    return json.loads(lzma.decompress((pc.ROOT/pc.BASE/('CPC-'+role+'.json.xz')).read_bytes()))


def account_completion(value, consumed=frozenset()):
    """Pure accounting for this bound research event; never a native receipt."""
    c=value['checks'];d=c['decision'];p=c['proof'];s=c['source']
    need(c['role']==d['role']=='current' and d['scientific_completion'] and d['local_gain']==1,
         'only current completion earns gain')
    need(not d['native_completion'] and not d['accepted_authority'] and
         not d['reset_probe_earns_live_gain'] and d['full_state']==['C','Z_4'],'completion scope')
    entry=d['first_certified_entry'];rows=c['observations']
    need(len(rows)==entry+2==d['target_completion_step'] and d['window_beats']==2 and d['window_elapsed']=='64',
         'two positive beats required')
    need(d['stable_descendants']==p['complete_basins'] and
         s['complete_parent']=={'p':sorted(c['source_graph']['live_node_ids'])},'complete parent/descendant identity')
    history=s['carrier_history']
    need(history['policy_id']=='event_loss_and_zero_target_carrier_v1' and
         history['disposition']=='whole_carrier_reset' and history['information_loss']=='carrier_history_loss' and
         history['target_initializer_id']=='canonical_zero_carrier_v1' and
         not history['native_release'] and history['source_archive_digest']==content_id(history['source_archive']),
         'lawful whole-carrier disposition required')
    need(all(cell==['0','0'] for cell in c['initial_target']['Z']), 'entire target carrier must be initialized to zero')
    with ctx.workprec(512):
        m=CPCReference(c['targets']['1']['graph']);P=arb_mat(m.constants['P'])
        radius=m.q(fmpq(p['resource_radius']))
        for row in rows[entry-1:]:
            C,Z=pc.decode(m,row)
            need(distance(m,C,Z,p,P)[2]<radius, 'window outside full-state trap')
            actual={chi:geometric_roster(t['graph'],C,m.nodes) for chi,t in c['targets'].items()}
            need(actual==p['complete_basins'] and row['complete_basins']==actual,'window spatial identity')
    event=content_id(dict(family='C_PC',declaration=pc.sha(pc.BASE+'CPCDeclaration.json'),
        source_graph=c['source_graph'],prestate=s['current_prestate'],poststate=s['actual_PC_poststate'],
        source_step=s['source_steps'],source_archive_digest=history['source_archive_digest'],
        target_graph=c['targets']['1']['graph'],actual_transfer=c['initial_target'],shares=s['allocation_shares']))
    return dict(research_event_id=event,new_gain=0 if event in consumed else 1,
                new_child=c['targets']['1']['module'][2],target_step=d['target_completion_step'],native_receipt=False)


def reseal(value):
    value['record_digest']=content_id({k:v for k,v in value.items() if k!='record_digest'})
    return value


def checks():
    values={role:read_role(role) for role in ('current','reset')}
    verification={r:pc.check(v) for r,v in values.items()}
    current=values['current'];first=account_completion(current)
    replay=account_completion(current,{first['research_event_id']})
    need(first['new_gain']==1 and replay['new_gain']==0,'at-most-once research gain')
    label=deepcopy(current);label['checks']['proof']['inspection_label']='another inspection'
    need(account_completion(label,{first['research_event_id']})['new_gain']==0,'inspection minted another event')
    rejected=[]
    accounting=[
        ('reset_earns_gain',lambda v:v['checks'].update(role='reset')),
        ('short_window',lambda v:v['checks']['observations'].pop()),
        ('zero_elapsed',lambda v:v['checks']['decision'].update(window_elapsed='0')),
        ('C_only_state',lambda v:v['checks']['decision'].update(full_state=['C'])),
        ('missing_parent',lambda v:v['checks']['source'].update(complete_parent={})),
        ('native_promotion',lambda v:v['checks']['decision'].update(native_completion=True)),
        ('unearned_acceptance',lambda v:v['checks']['decision'].update(accepted_authority=True)),
        ('event_zeroing_called_release',lambda v:v['checks']['source']['carrier_history'].update(native_release=True)),
        ('lost_source_archive',lambda v:v['checks']['source']['carrier_history'].update(source_archive={})),
        ('partial_target_reset',lambda v:v['checks']['initial_target']['Z'].__setitem__(0,['1/1024','1/1024'])),
        ('nonzero_carrier_outside_trap',lambda v:v['checks']['observations'][-1]['Z'].__setitem__(0,['1/1024','1/1024'])),
    ]
    for name,mutate in accounting:
        bad=deepcopy(current);mutate(bad);reseal(bad)
        try: account_completion(bad)
        except ValueError: rejected.append(name)
        else: raise ValueError('false completion accepted: '+name)
    # These rehashed substitutions are checked against fresh source/transfer
    # mathematics and the full new trapping certificate, not just a digest.
    subject_controls=[
        ('wrong_consumed_geometry',lambda v:v['checks']['source']['consumed_current_read']['H'][0].__setitem__(0,['2','2'])),
        ('wrong_carrier_writer',lambda v:v['checks']['source']['actual_PC_poststate']['Z'].__setitem__(0,['0','0'])),
        ('reset_advanced',lambda v:v['checks']['source'].update(reset_advanced=True)),
        ('missing_carrier_directions',lambda v:v['checks']['proof'].update(carrier_dimension=0)),
        ('changed_transfer_resource',lambda v:v['checks']['initial_target']['C'].__setitem__('p',['3','3'])),
    ]
    for name,mutate in subject_controls:
        bad=deepcopy(current);mutate(bad);reseal(bad)
        try: pc.check(bad,transitions=False)
        except ValueError: rejected.append(name)
        else: raise ValueError('wrong physical subject accepted: '+name)
    return dict(schema='spark-completion-cpc-reconciliation-checks-v1',status='passed_bounded_research',
                histories=verification,first_completion=first,replay=replay,rejected_controls=rejected,
                retained_state_count=sum(r['retained_states'] for r in verification.values()),
                independent_long_replay=False,retained_comparisons='overlap_consistency_only',
                proof_source='fresh full C/Z derivative and center certificate',
                accepted_authority=False,native_support_added=[],G4_accepted=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');args=p.parse_args()
    value=checks()
    paths=[pc.BASE+'CPC-'+r+'.json.xz' for r in ('current','reset')]+[
        pc.INV+'scripts/check_spark_completion_pc_reconciliation.py',pc.INV+'scripts/test_spark_completion_pc.py']
    value['sources']=[dict(path=x,sha256=pc.sha(x)) for x in paths];value=pc.sealed(value)
    path=pc.ROOT/pc.BASE/'CPCChecks.json'
    if args.write: pc.write_new(path,value)
    else: need(json.loads(path.read_text())==value,'retained research reconciliation changed')
    print(json.dumps({k:value[k] for k in ('status','first_completion','replay','rejected_controls','retained_state_count')},indent=2))
