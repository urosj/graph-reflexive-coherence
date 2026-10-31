"""Run declared C_PC research or check retained subjects without a long rerun."""
from pathlib import Path
from fractions import Fraction as F
import argparse
import hashlib
import json
import lzma
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
INV = 'implementation/investigations/grc9v4-constitutive-design/'
BASE = INV+'evidence/spark-completion/applicability/'
sys.path[:0] = [str(ROOT/'src'),str(ROOT/INV/'research'),
               str(ROOT/INV/'evidence/spark-completion/review/constructive-candidate')]
from flint import arb, arb_mat, fmpq, ctx
from spark_completion_pc import CPCReference, trap_certificate, TAU_PC, TRAP_WEIGHT, CARRIER_RADIUS
from spark_completion_pc_campaign import campaign, prepare_source, state_payload, read_payload, distance
from spark_completion_positive import fixture, content_id, norm_upper
from spark_completion_ci_campaign import retained
from spark_completion_continuation import need, geometric_roster

SOURCES = [INV+'research/'+name+'.py' for name in (
    'spark_completion_pc','spark_completion_pc_campaign','spark_completion_os_reference',
    'spark_completion_positive','spark_completion_ci_campaign','spark_completion_continuation',
    'spark_completion_basins')]+[
    INV+'evidence/spark-completion/SC2SourceBeat.json.xz',
    INV+'evidence/spark-completion/SC2PositiveCandidate.json.xz',
    INV+'decisions/spark-completion/Authority.json',
    INV+'decisions/spark-completion-applicability/Authority.json',BASE+'CPCDeclaration.json',
    INV+'scripts/check_spark_completion_applicability_pc.py',
    INV+'scripts/test_spark_completion_pc.py',
    'specs/grc-v4-spec.md','specs/grc-v4-topology-event-spec.md',
    'src/pygrc/models/grc_9_v4_expansion.py','src/pygrc/models/grc_9_v4_topology.py']


def sha(path): return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def bindings(): return [dict(path=p,sha256=sha(p)) for p in SOURCES]
def normalized(value): return json.loads(json.dumps(value,default=str))
def sealed(value): return {**value,'record_digest':content_id(value)}


def declaration():
    d = json.loads((ROOT/BASE/'CPCDeclaration.json').read_text())
    need(d['record_digest']==content_id({k:v for k,v in d.items() if k!='record_digest'}), 'declaration digest')
    need(d['family']=='C_PC' and d['parameters']==dict(c0='2',a='1',mu='1',eta_C='1/1024',duration='32',
        kappa_Phi_C='1/64',tau_C='1',chi_C='1/2',zeta_C='1/2',kappa_H='1/2',kappa_M_C='0',tau_PC=str(TAU_PC)),
        'declared equation parameters')
    need(d['source_carrier_preparation']==dict(current='diagonal +2^-16',reset='diagonal -2^-17',offdiagonal='zero'),
         'declared source carrier')
    need(d['domain']==dict(C=['0','4'],Z_frobenius_radius=str(CARRIER_RADIUS),symmetry=True,star_support=True,signed_carriers=True),
         'declared full domain')
    need(d['approach_precision_bits']==8192 and d['trapping_precision_bits']==512 and
         d['maximum_target_steps']==1024 and d['time_limit_seconds_per_role']==3600 and
         d['window_beats']==2 and d['window_elapsed']=='64' and d['roles']==['current','reset'] and
         not d['automatic_fallback'] and not d['earlier_family_trajectory_reuse'] and d['native_support_added']==[],
         'declared arithmetic/scope')
    return d


def interval(pair):
    need(isinstance(pair,list) and len(pair)==2,'interval shape')
    lo,hi = map(F,pair)
    need(0<=hi-lo<=F(1,2**110),'retained interval width')
    return arb(fmpq(str((lo+hi)/2)),fmpq(str((hi-lo)/2)))


def decode(m,state):
    need(set(state['C'])==set(m.nodes) and len(state['Z'])==len(m.pairs),'full state coverage')
    C = m.matrix([[interval(state['C'][n])] for n in m.nodes]); Z = m.zero()
    for (i,j),pair in zip(m.pairs,state['Z']):
        Z[i,j] = interval(pair); Z[j,i] = Z[i,j]
    m.validate(C,Z)
    return C,Z


def overlaps(left,right,what):
    need(left.nrows()==right.nrows() and left.ncols()==right.ncols(),what+' dimensions')
    need(all(a.overlaps(b) for a,b in zip(left.entries(),right.entries())),what+' inconsistency')


def check_read(saved,fresh):
    need(set(saved)=={'H','J','flat','S'},'whole read coverage')
    for field,M in [('H',fresh['geometry']),('J',fresh['selected']['current']),
                    ('flat',fresh['selected']['causal_flat']),('S',fresh['source'])]:
        cells=saved[field]
        need(len(cells)==M.nrows() and all(len(row)==M.ncols() for row in cells),'saved read dimensions')
        overlaps(arb_mat([[interval(cell) for cell in row] for row in cells]),M,'saved '+field)


def check(value, *, transitions=True):
    declaration()
    need(value['record_digest']==content_id({k:v for k,v in value.items() if k!='record_digest'}),'execution digest')
    need(value['schema']=='spark-completion-cpc-applicability-execution-v1' and
         value['claim_class']=='conditional_mathematical_research' and not value['accepted_authority'] and
         value['native_support_added']==[],'execution scope')
    need(value['sources']==bindings(),'execution source drift')
    c=value['checks']; role=c['role']; source,_,targets=fixture()
    need(c['source_graph']==source and c['targets']==normalized(targets),'actual graph/fixture binding')
    need(c['arithmetic']==dict(precision_bits=8192,trapping_precision_bits=512,
        maximum_target_steps=1024,time_limit_seconds=3600,automatic_fallback=False,
        retained_coordinates='outward 112-bit dyadic enclosures; full recurrence starts from exact inputs',
        midpoint_evolution=False),'execution arithmetic')
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
                result=m.pc_step(previous_C,previous_Z)
                overlaps(C,result['after'],'retained resource recurrence')
                overlaps(Z,result['carrier_after'],'retained carrier recurrence')
            previous_C,previous_Z=C,Z
        need(first_entry==entry and first_gain==d['first_spatial_gain'],'retained first observation changed')
        for name,index in [('event',None),('entry',entry),('completion',len(rows))]:
            saved=c['checkpoints'][name]
            if index is not None:
                need(saved['C']==rows[index-1]['C'] and saved['Z']==rows[index-1]['Z'],'checkpoint subject changed')
            C,Z=decode(m,saved);check_read(saved['read'],m.pc_read(C,Z))
        opt=c['optimization']
        need(opt['target_poststate_reads']==opt['target_carrier_writes']==len(rows)
             and opt['identical_full_state_read_reuse'] and opt['batched_derivative_rhs'] and
             opt['chiral_incidence_verified'] and not opt['trajectory_results_cached'],'read/write optimization cadence')
    return dict(decision=d,retained_states=len(rows),fresh_full_trap=True,
                transition_checks=len(rows) if transitions else 0,
                saved_read_and_transition_comparison='overlap consistency only; original enclosure provenance is the certified campaign',
                trajectory_rerun=False)


def write_new(path,value):
    raw=(json.dumps(value,indent=2,default=str)+'\n').encode()
    data=lzma.compress(raw,preset=6) if path.suffix=='.xz' else raw
    with path.open('xb') as out: out.write(data)
    print('SAVED',path.name,len(raw),'->',len(data),'bytes',flush=True)


def preflight():
    declaration(); before=bindings(); roles={}
    for role in ('current','reset'):
        run=campaign(role,maximum_steps=12,require_completion=False,progress=False)
        roles[role]=dict(steps=12,elapsed_seconds=run['elapsed_seconds'],optimization=run['optimization'],
                         actual_source_digest=content_id(run['source']),
                         final_full_state_digest=content_id({k:run['observations'][-1][k] for k in ('C','Z')}))
        need(run['optimization']['constant_cache_hits']>0,'exact operand cache not active')
    need(before==bindings(),'preflight sources changed')
    return sealed(dict(schema='spark-completion-cpc-preflight-v1',status='passed',
                       declared_precision=8192,roles=roles,sources=before,long_campaign_started=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--preflight',action='store_true');mode.add_argument('--run',action='store_true')
    mode.add_argument('--check',action='store_true');parser.add_argument('--role',choices=['current','reset'])
    args=parser.parse_args()
    if args.preflight:
        write_new(ROOT/BASE/'CPCPreflight.json',preflight())
    else:
        need(args.role is not None,'role required')
        path=ROOT/BASE/('CPC-'+args.role+'.json.xz')
        if args.run:
            need(not path.exists(),'refusing to overwrite retained campaign')
            declaration(); pf=json.loads((ROOT/BASE/'CPCPreflight.json').read_text())
            need(pf['record_digest']==content_id({k:v for k,v in pf.items() if k!='record_digest'}) and
                 pf['status']=='passed' and pf['sources']==bindings(),'verified optimization preflight required')
            before=bindings(); result=campaign(args.role)
            need(before==bindings(),'campaign sources changed during execution')
            value=sealed(dict(schema='spark-completion-cpc-applicability-execution-v1',checks=result,
                sources=before,claim_class='conditional_mathematical_research',accepted_authority=False,native_support_added=[]))
            write_new(path,value)
        else: value=json.loads(lzma.decompress(path.read_bytes()))
        print(json.dumps(check(normalized(value)),indent=2),flush=True)
