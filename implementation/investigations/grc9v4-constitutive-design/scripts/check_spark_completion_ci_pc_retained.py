"""Corrected C_CI_PC retained validation, preserving original execution bindings.

An outward Arb enclosure of a nonnegative residual can have a negative lower
endpoint. Stored scalar root bounds belong to the original input enclosure;
fresh compact-input solves need not have identical residual/error bounds.
Whole selected f/H/J/S comparisons remain overlap consistency only.
"""
from fractions import Fraction as F
import argparse
import json
import lzma
from flint import arb_mat, fmpq, ctx
from check_spark_completion_applicability_ci_pc import (
    ROOT, INV, BASE, sha, sealed, write_new, declaration, bindings, normalized,
    interval, decode, overlaps, CCIPCReference, trap_certificate, CARRIER_RADIUS,
    fixture, content_id, retained, prepare_source, state_payload, distance,
    need, geometric_roster,
)


def check_read(saved,fresh):
    need(set(saved)=={'H','J','flat','S','root_error','root_residual'},'whole read coverage')
    for field in ('root_error','root_residual'):
        cell=interval(saved[field])
        # A negative upper endpoint excludes a nonnegative bound; a negative
        # lower endpoint alone is lawful outward rounding of an enclosure.
        need(F(saved[field][1])>=0 and F(saved[field][1])<=F(1,2**110),
             'saved root diagnostic excludes nonnegative bounded residual')
        need(cell.is_finite(),'nonfinite root diagnostic')
    for field,M in [('H',fresh['geometry']),('J',fresh['selected']['current']),
                    ('flat',fresh['flat']),('S',fresh['source'])]:
        cells=saved[field]
        need(len(cells)==M.nrows() and all(len(row)==M.ncols() for row in cells),'saved read dimensions')
        overlaps(arb_mat([[interval(cell) for cell in row] for row in cells]),M,'saved '+field)


def check(value, *, transitions=True):
    declaration()
    need(value['record_digest']==content_id({k:v for k,v in value.items() if k!='record_digest'}),'execution digest')
    need(value['schema']=='spark-completion-ccipc-applicability-execution-v1' and
         value['claim_class']=='conditional_mathematical_research' and not value['accepted_authority'] and
         value['native_support_added']==[],'execution scope')
    need(value['sources']==bindings(),'execution source drift')
    c=value['checks']; role=c['role']; source,_,targets=fixture()
    need(c['source_graph']==source and c['targets']==normalized(targets),'actual graph/fixture binding')
    need(c['arithmetic']==dict(precision_bits=8192,trapping_precision_bits=512,
        maximum_target_steps=1024,time_limit_seconds=3600,automatic_fallback=False,
        retained_coordinates='outward 112-bit dyadic enclosures; full recurrence starts from exact inputs',
        midpoint_evolution=False,proposal_policy='precision_ladder',
        proposal_minimum_bits=128,proposal_newton_limit_per_stage=16),'execution arithmetic')
    need(not c['earlier_family_trajectory_reused'] and c['native_steps']==0,'evidence attribution')
    with ctx.workprec(512):
        proof,P=trap_certificate({**targets['1'],'charts':targets},retained('SC2PositiveCandidate.json.xz')['checks']['trap'])
        need(c['proof']==normalized(proof),'fresh full-state trap changed')
        m,C,Z,s=prepare_source(source,targets,role)
        need(c['source']==normalized(s),'actual source/read/write/archive/trigger changed')
        need(c['initial_target']==state_payload(m,C,Z),'actual transfer changed')
        need(c['checkpoints']['event']['C']==c['initial_target']['C'] and
             c['checkpoints']['event']['Z']==c['initial_target']['Z'],'event checkpoint binding')
        d=c['decision']; rows=c['observations']; entry=d['first_certified_entry']
        need(type(entry) is int and 1<=entry and len(rows)==entry+2==d['target_completion_step']<=1024,'positive window')
        need(d['role']==role and d['scientific_completion']==(role=='current') and d['local_gain']==int(role=='current')
             and not d['reset_probe_earns_live_gain'] and not d['native_completion'] and not d['accepted_authority']
             and d['full_state']==['C','Z_4'] and d['window_beats']==2 and d['window_elapsed']=='64'
             and d['stable_descendants']==proof['complete_basins'],'completion scope')
        metric=arb_mat(P); radius=m.q(fmpq(proof['resource_radius']))
        previous_C,previous_Z=decode(m,c['initial_target'])
        first_entry=None; first_gain=None
        for index,row in enumerate(rows,1):
            need(row['step']==index,'consecutive state coverage')
            C,Z=decode(m,row)
            need(all(C[i,0]>0 for i in range(m.n)) and sum(C[i,0] for i in range(m.n)).contains(21),'retained positivity/charge')
            need(F(row['minimum_resource'][0])>0 and
                 0 <= F(row['root_error_upper']) <= F(1,2**110) and row['root_iterations']>0 and
                 F(row['carrier_norm_upper'])<=CARRIER_RADIUS and F(row['source_norm_upper'])<=CARRIER_RADIUS,
                 'saved domain bounds')
            actual={chi:geometric_roster(t['graph'],C,m.nodes) for chi,t in targets.items()}
            need(row['complete_basins']==actual,'complete basin roster drift')
            rd,zd,full=distance(m,C,Z,proof,metric)
            if actual==proof['complete_basins'] and first_gain is None: first_gain=index
            if full<radius and first_entry is None: first_entry=index
            if index>=entry:
                need(full<radius and actual==proof['complete_basins'],'full retained C/Z window leaves trap')
            if transitions:
                result=m.ccipc_step(previous_C,previous_Z)
                overlaps(C,result['after'],'retained resource recurrence')
                overlaps(Z,result['carrier_after'],'retained carrier recurrence')
            previous_C,previous_Z=C,Z
        need(first_entry==entry and first_gain==d['first_spatial_gain'],'retained first observation changed')
        for name,index in [('event',None),('entry',entry),('completion',len(rows))]:
            saved=c['checkpoints'][name]
            if index is not None:
                need(saved['C']==rows[index-1]['C'] and saved['Z']==rows[index-1]['Z'],'checkpoint subject changed')
            C,Z=decode(m,saved);check_read(saved['read'],m.ccipc_read(C,Z))
        opt=c['optimization']
        need(opt['target_poststate_reads']==opt['target_carrier_writes']==len(rows)
             and opt['identical_full_state_read_reuse'] and opt['batched_derivative_rhs'] and
             opt['chiral_incidence_verified'] and not opt['trajectory_results_cached'],'read/write optimization cadence')
    return dict(decision=d,retained_states=len(rows),fresh_full_trap=True,
                transition_checks=len(rows) if transitions else 0,
                saved_read_and_transition_comparison='overlap consistency only; original enclosure provenance is the certified campaign',
                trajectory_rerun=False)



if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true',required=True)
    parser.add_argument('--role',choices=['current','reset'],required=True)
    args=parser.parse_args()
    value=json.loads(lzma.decompress((ROOT/BASE/('CCIPC-'+args.role+'.json.xz')).read_bytes()))
    print(json.dumps(check(value),indent=2))
