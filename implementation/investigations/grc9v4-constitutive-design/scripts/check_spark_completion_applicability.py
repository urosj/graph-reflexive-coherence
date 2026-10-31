"""Research applicability reconciliation and targeted evidence pressure; no native grant."""
from pathlib import Path
from copy import deepcopy
import hashlib,json,lzma,sys
from fractions import Fraction as F
from flint import arb,fmpq,ctx
import check_spark_completion_applicability_ci as ci
from spark_completion_ci import CCIReference
from spark_completion_ci_campaign import prepare_source,retained,box_payload
from spark_completion_positive import fixture,content_id
from spark_completion_continuation import need

ROOT=ci.ROOT;INV=ci.INV;BASE=ci.BASE


def read_role(role):return json.loads(lzma.decompress((ROOT/BASE/('CCI-'+role+'.json.xz')).read_bytes()))


def decode(m,cells):
    need(set(cells)==set(m.nodes),'state coverage')
    return m.matrix([[arb(fmpq(str((F(cells[n][0])+F(cells[n][1]))/2)),
        fmpq(str((F(cells[n][1])-F(cells[n][0]))/2)))]for n in m.nodes])


def root_agreement(saved,fresh,m):
    """Check retained f/H/J consistency, not saved-enclosure certification.

    Overlap does not establish that the saved interval contains the root.
    Proof calculations must consume the freshly certified root enclosure;
    the original campaign supplies certification of its retained captures.
    """
    for field,M in [('flat',fresh['flat']),('H',fresh['geometry']),('J',fresh['selected']['current'])]:
        cells=saved[field]
        need(len(cells)==M.nrows() and all(len(r)==M.ncols()for r in cells),'root coverage')
        for i in range(M.nrows()):
            for j in range(M.ncols()):
                lo,hi=map(F,cells[i][j]);need(0<=hi-lo<=F(1,2**110),'invalid saved root enclosure width')
                interval=arb(fmpq(str((lo+hi)/2)),fmpq(str((hi-lo)/2)))
                need(interval.overlaps(M[i,j]),'fresh whole-root/geometry disagreement')
    need(F(saved['root_error_upper'])>=0 and F(saved['root_residual_upper'])>=0
         and 1<=saved['proposal_iterations']<=16,'root certificate metadata')


def precise_subjects(value):
    """Recompute source/transfer and check saved roots against fresh enclosures.

    Fresh roots are certified by CCIReference.root; saved-root comparisons
    establish overlap consistency only. No saved root drives a proof here.
    """
    c=value['checks'];role=c['role'];source,_,targets=fixture()
    need(c['arithmetic']==dict(precision_bits=8192,root_proposal_limit=16,maximum_target_steps=1024,
        time_limit_seconds=1800,automatic_fallback=False,
        retained_coordinates='outward 112-bit dyadic enclosures; full recurrence is reproduced from exact inputs',
        midpoint_usage='root proposals only; actual C evolution always uses full outward enclosure'), 'arithmetic declaration')
    with ctx.workprec(512):
        m,C,s=prepare_source(retained('SC2SourceBeat.json.xz'),source,targets,role)
        for key in ('actual_CI_poststate','reset_state','complete_parent','gradient_squared_margin','spark_margin',
                    'root_domain','source_steps','reset_advanced','allocation_shares','charge','charge_argument'):
            need(c['source'][key]==s[key],'source capture/parent/charge changed: '+key)
        need(c['initial_target']==box_payload(m,C),'actual transfer changed')
        sm=CCIReference(source)
        for prefix,state in [('fresh','actual_CI_poststate'),('reset','reset_state')]:
            root_agreement(c['source'][prefix+'_joint_root'],sm.root(decode(sm,c['source'][state])),sm)
        for key in ('event','entry','completion'):
            saved=c['checkpoints'][key];fresh=m.root(decode(m,saved['C']))
            root_agreement(saved['root'],fresh,m)
        need(c['checkpoints']['event']['C']==c['initial_target'],'event checkpoint differs from actual transfer')
    return True


def account_completion(value,consumed=frozenset(),*,role='current'):
    """Pure research accounting; actual native receipt identity remains downstream."""
    c=value['checks'];d=c['decision']
    need(c['role']=='current' and role=='current','reset cannot earn live completion')
    need(d['scientific_completion'] and not d['native_completion'] and not d['accepted_authority'],'decision scope')
    entry=d['first_certified_entry'];rows=c['observations']
    need(len(rows)==entry+2==d['target_completion_step'] and d['window_beats']==2 and d['window_elapsed']=='64','positive window')
    need(d['stable_descendants']==c['proof']['complete_basins'] and d['full_state']==['C'] and d['local_gain']==1,'complete child identity')
    need(c['source']['complete_parent']=={'p':sorted(c['source_graph']['live_node_ids'])},'parent missing')
    for row in rows[entry:]:
        need(row['complete_basins']==c['proof']['complete_basins']
             and F(row['trap_distance_upper'])<F(c['proof']['radius']), 'window/trap premise missing')
    # The occurrence preimage excludes proof, window and review identity. This
    # fixed research event is not a universal native occurrence-id scheme.
    event=content_id(dict(family='C_CI',declaration='CCIDeclaration.json',
        source_graph=c['source_graph'],source_step=1,source_prestate=retained('SC2SourceBeat.json.xz')['checks']['prepared']['current_prestate'],
        source_poststate=c['source']['actual_CI_poststate'],target_graph=c['targets']['1']['graph'],
        actual_transfer=c['initial_target'],shares=c['source']['allocation_shares']))
    return dict(research_event_id=event,new_gain=0 if event in consumed else 1,
        target_step=d['target_completion_step'],new_child=c['targets']['1']['module'][2],native_receipt=False)


def checks():
    values={r:read_role(r)for r in ('current','reset')}
    for value in values.values():ci.check(value);precise_subjects(value)
    value=values['current'];first=account_completion(value)
    repeated=account_completion(value,{first['research_event_id']})
    need(first['new_gain']==1 and repeated['new_gain']==0,'duplicate gain')
    altered=deepcopy(value);altered['checks']['proof']['review_label']='different inspection'
    need(account_completion(altered,{first['research_event_id']})['new_gain']==0,'review minted another event')
    mutations=[('missing_parent',lambda x:x['checks']['source'].update(complete_parent={})),
        ('reset_role',lambda x:x['checks'].update(role='reset')),
        ('short_window',lambda x:x['checks']['observations'].pop()),
        ('native_claim',lambda x:x['checks']['decision'].update(native_completion=True)),
        ('wrong_domains',lambda x:x['checks']['decision'].update(stable_descendants={})),
        ('zero_duration',lambda x:x['checks']['decision'].update(window_elapsed='0')),
        ('omitted_physical_state',lambda x:x['checks']['decision'].update(full_state=[]))]
    rejected=[]
    for name,edit in mutations:
        bad=deepcopy(value);edit(bad)
        try:account_completion(bad)
        except ValueError:rejected.append(name)
        else:raise ValueError('false completion accepted: '+name)
    with ctx.workprec(512):
        m=CCIReference(value['checks']['targets']['1']['graph']);saved=value['checks']['checkpoints']['completion']
        root=m.root(decode(m,saved['C']));bad=deepcopy(saved['root']);bad['H'][0][0]=['2','2']
        try:root_agreement(bad,root,m)
        except ValueError:rejected.append('wrong_geometry_with_unchanged_J')
        else:raise ValueError('changed geometry accepted')
    need(len(rejected)==8,'pressure coverage')
    return dict(schema='spark-completion-cci-reconciliation-checks-v1',scientific_status='bounded_positive_research',
        current=values['current']['checks']['decision'],reset=values['reset']['checks']['decision'],
        first_completion=first,replay=repeated,rejected_controls=rejected,
        fresh_subject_checks='actual source/parent/transfer and whole CI roots at event/entry/completion',
        retained_root_comparison='overlap_consistency_only',
        retained_root_enclosure_independently_recertified=False,
        proof_root_source='fresh certified CCIReference.root enclosure, never saved-root overlap',
        check_mode='retained consistency and fresh short mathematics, not long recurrence replay',
        accepted_authority=False,native_support_added=[],G4_accepted=False)


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');args=p.parse_args()
    value=checks()
    paths=[BASE+'CCI-current.json.xz',BASE+'CCI-reset.json.xz',INV+'scripts/check_spark_completion_applicability.py',INV+'scripts/test_spark_completion_ci.py']
    value['sources']=[dict(path=x,sha256=hashlib.sha256((ROOT/x).read_bytes()).hexdigest())for x in paths]
    value['record_digest']=content_id(value)
    path=ROOT/BASE/'CCIChecks.json'
    if args.write:
        with path.open('x') as out:out.write(json.dumps(value,indent=2)+'\n')
    else:need(json.loads(path.read_bytes())==value,'CI reconciliation no longer matches')
    print(json.dumps({k:value[k]for k in ('scientific_status','first_completion','replay','rejected_controls','native_support_added')},indent=2))
