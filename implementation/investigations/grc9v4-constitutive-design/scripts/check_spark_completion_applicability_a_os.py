"""A_OS declared campaign, optimization preflight and retained consistency checks."""
from pathlib import Path
from fractions import Fraction as F
import argparse,hashlib,json,lzma,sys,time
from copy import deepcopy
ROOT=Path(__file__).resolve().parents[4]
INV='implementation/investigations/grc9v4-constitutive-design/'
BASE=INV+'evidence/spark-completion/applicability/'
sys.path[:0]=[str(ROOT/'src'),str(ROOT/INV/'research'),str(ROOT/INV/'evidence/spark-completion/review/constructive-candidate')]
from flint import arb,arb_mat,fmpq,ctx
from spark_completion_a_os import AOSReference,trap_certificate,geometric_roster,PARAMETERS,graph_constants
from spark_completion_a_os_campaign import campaign,prepare_source,state_payload,read_payload,distance,PRECISION,HORIZON,TIME_LIMIT
from spark_completion_positive import fixture,content_id
from spark_completion_continuation import need

SOURCES=[INV+'research/'+x+'.py' for x in ('spark_completion_a_os','spark_completion_a_os_campaign',
    'spark_completion_positive','spark_completion_ci_campaign','spark_completion_continuation','spark_completion_basins',
    'spark_completion_os_reference')]+[INV+'scripts/'+x+'.py' for x in ('check_spark_completion_applicability_a_os','test_spark_completion_a_os')]+[
    BASE+'AOSDeclaration.json',INV+'evidence/spark-completion/SC2SourceBeat.json.xz',
    INV+'evidence/spark-completion/review/constructive-candidate/positive_candidate.py',
    'src/pygrc/models/grc_9_v4_expansion.py','src/pygrc/models/grc_9_v4_topology.py',
    'specs/grc-v4-spec.md','specs/grc-v4-topology-event-spec.md']

def normalized(x):return json.loads(json.dumps(x,default=str))
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def bindings():return [dict(path=p,sha256=sha(p)) for p in SOURCES]
def sealed(x):return {**x,'record_digest':content_id(x)}
def load(path):
    raw=(ROOT/path).read_bytes();return json.loads(lzma.decompress(raw) if str(path).endswith('.xz') else raw)
def write_new(path,x):
    raw=(json.dumps(x,indent=2,default=str)+'\n').encode();out=lzma.compress(raw,preset=6) if path.endswith('.xz') else raw
    with (ROOT/path).open('xb') as f:f.write(out)
    print('SAVED',path,len(raw),'->',len(out),flush=True)

def declaration():
    d=load(BASE+'AOSDeclaration.json');need(d['record_digest']==content_id({k:v for k,v in d.items() if k!='record_digest'}),'declaration digest')
    need(d['family']=='A_OS' and d['parameters']==PARAMETERS and d['full_state']==['C','W_A'] and
        d['precision_bits']==PRECISION and d['maximum_target_steps']==HORIZON and d['time_limit_seconds_per_role']==TIME_LIMIT and
        d['window_beats']==2 and d['allocation_shares']==['1/128','63/64','1/128'] and d['source_W']=={'current':'4097/4096','reset':'8191/8192','new_internal':'1'} and
        d['native_support_added']==[] and not d['accepted_authority'],'declaration scope')
    return d

def interval(pair):
    need(isinstance(pair,list) and len(pair)==2,'interval shape');lo,hi=map(F,pair)
    need(0<=hi-lo<=F(1,2**110),'retained interval width')
    return arb(fmpq(str((lo+hi)/2)),fmpq(str((hi-lo)/2)))

def decode(m,s):
    need(set(s['C'])==set(m.nodes) and len(s['logW'])==m.m,'full C/W coverage')
    return arb_mat([[interval(s['C'][n])] for n in m.nodes]),arb_mat([[interval(x)] for x in s['logW']])

def overlaps(a,b,label):
    need(a.nrows()==b.nrows() and a.ncols()==b.ncols() and all(x.overlaps(y) for x,y in zip(a.entries(),b.entries())),label+' inconsistency')

def check_read(saved,fresh):
    need(set(saved)=={'H','J','predictor_J','flat','split_upper'},'whole OS read coverage')
    for k,M in [('H',fresh['geometry']),('J',fresh['corrector']['current']),('predictor_J',fresh['predictor']['current']),('flat',fresh['corrector']['causal_flat'])]:
        overlaps(arb_mat([[interval(x) for x in row] for row in saved[k]]),M,'read '+k)
    need(0<=F(saved['split_upper'])<F(1,10**11),'retained split bound')

def check(v,*,transitions=True,complete=True):
    declaration();need(v['record_digest']==content_id({k:x for k,x in v.items() if k!='record_digest'}),'execution digest')
    need(v['schema']=='spark-completion-aos-execution-v1' and v['sources']==bindings(),'execution source binding')
    need(v['accepted_authority'] is False and v['native_support_added']==[],'execution authority')
    c=v['checks'];source,_,targets=fixture();need(c['source_graph']==source and c['targets']==normalized(targets),'graph binding')
    need(c['arithmetic']==dict(precision_bits=PRECISION,trapping_precision_bits=512,maximum_target_steps=HORIZON,
        time_limit_seconds=TIME_LIMIT,automatic_fallback=False,midpoint_evolution=False,storage_bits=112),'arithmetic')
    need(not c['earlier_family_trajectory_reused'] and c['native_steps']==0,'prior evidence attribution')
    proof,P=trap_certificate(targets);need(c['proof']==normalized(proof),'full-state trap changed')
    with ctx.workprec(512):
        m,C,L,s=prepare_source(source,targets,c['role']);need(c['source']==normalized(s),'actual source/transfer changed')
        need(c['initial_target']==state_payload(m,C,L),'transfer subject changed')
        need({k:c['checkpoints']['event'][k] for k in ('C','logW')}==c['initial_target'],'event checkpoint')
        metric=arb_mat(P);radius=arb(fmpq(proof['radius']));prevC,prevL=decode(m,c['initial_target'])
        entry=None;gain=None;charts={chi:AOSReference(t['graph']) for chi,t in targets.items()}
        for index,row in enumerate(c['observations'],1):
            need(row['step']==index,'consecutive retained coverage');C,L=decode(m,row)
            need(all(0<x<4 for x in C.entries()) and sum(C.entries()).contains(21),'retained C domain')
            need(all(m.q(99,100)<w<m.q(101,100) for w in m.exp(L).entries()),'retained W domain')
            rosters={chi:geometric_roster(cm,C,L) for chi,cm in charts.items()};need(row['complete_basins']==rosters,'weighted basin roster')
            _,_,total=distance(m,C,L,proof,metric)
            if gain is None and rosters==proof['complete_basins']:gain=index
            if entry is None and total<radius:entry=index
            if entry is not None:need(total<radius and rosters==proof['complete_basins'],'full-state completion window')
            need(0<=F(row['split_upper'])<F(1,10**11) and F(row['full_distance_upper'])>=0,'saved diagnostic domain')
            if transitions:
                result=m.step(prevC,prevL);overlaps(C,result['after'],'resource recurrence');overlaps(L,result['logW_after'],'writer recurrence')
            prevC,prevL=C,L
        d=c['decision'];is_complete=entry is not None and len(c['observations'])==entry+2
        if complete:need(is_complete,'missing positive completion window')
        expected=dict(role=c['role'],scientific_completion=is_complete and c['role']=='current',local_gain=int(is_complete and c['role']=='current'),
            reset_probe_earns_live_gain=False,first_spatial_gain=gain,first_certified_entry=entry,
            target_completion_step=len(c['observations']) if is_complete else None,window_beats=2,window_elapsed='64',
            full_state=['C','W_A'],stable_descendants=proof['complete_basins'],native_completion=False,accepted_authority=False)
        need(d==expected,'completion accounting')
        for name,index in [('event',None)]+([('entry',entry),('completion',len(c['observations']))] if is_complete else []):
            saved=c['checkpoints'][name]
            if index is not None:need(all(saved[k]==c['observations'][index-1][k] for k in ('C','logW')),'checkpoint binding')
            C,L=decode(m,saved);check_read(saved,m.os_read(C,L)) if 'H' in saved else check_read(saved['read'],m.os_read(C,L))
        opt=c['optimization'];need(opt['target_physical_reads']==2*len(c['observations']) and opt['target_writer_calls']==len(c['observations']) and
            all(opt[k] for k in ('identical_full_state_read_reuse','fixed_row_reuse_between_predictor_corrector','predictor_identity_solve_elided','chiral_incidence_and_row_identity')) and
            not opt['trajectory_results_cached'] and opt['graph_cache_hits']>0,'optimization accounting')
    return dict(status='passed',decision=d,retained_states=len(c['observations']),transition_checks=len(c['observations']) if transitions else 0,
        fresh_full_state_trap=True,trajectory_rerun=False,consistency_only='Saved transition/read overlap does not independently certify the original trajectory; the bound campaign supplies enclosure provenance.')

def execution(c):return sealed(dict(schema='spark-completion-aos-execution-v1',accepted_authority=False,native_support_added=[],sources=bindings(),checks=normalized(c)))

def preflight():
    declaration();start=time.monotonic();c=campaign('current',maximum_steps=8,require_completion=False)
    result=check(execution(c),complete=False)
    return sealed(dict(schema='spark-completion-aos-preflight-v1',family='A_OS',sources=bindings(),
        pilot_steps=8,optimization=c['optimization'],validation=result,elapsed_seconds=time.monotonic()-start,
        long_run_authorized_only_after_preflight=True,trajectory_result_reused=False))

def controls(v):
    cases={
        'missing_W_direction':lambda c:c['proof'].__setitem__('conductance_dimension',15),
        'frozen_stationary_writer':lambda c:c['proof'].__setitem__('stationary_writer_self_consistent',False),
        'altered_stationary_center':lambda c:c['proof']['logW_center'].__setitem__(0,'0'),
        'C_only_full_state':lambda c:c['decision'].__setitem__('full_state',['C']),
        'event_only_completion':lambda c:c['decision'].__setitem__('first_certified_entry',0),
        'reset_mints_gain':lambda c:c['decision'].__setitem__('reset_probe_earns_live_gain',True),
        'missing_positive_window':lambda c:c['observations'].pop(),
        'rewritten_old_W':lambda c:c['source']['W_transfer'].__setitem__('old_history_discarded',True),
        'source_beat_omitted':lambda c:c['source'].__setitem__('source_steps',0),
        'reset_advanced':lambda c:c['source'].__setitem__('reset_advanced',True),
        'stale_trigger':lambda c:c['source'].__setitem__('spark_margin',['1','1']),
        'missing_saved_W':lambda c:c['observations'][0]['logW'].pop(),
        'frozen_saved_W':lambda c:c['observations'][0].__setitem__('logW',c['initial_target']['logW']),
        'altered_complete_basin':lambda c:c['observations'][0].__setitem__('complete_basins',{}),
        'wrong_read_current':lambda c:c['checkpoints']['event']['read']['J'][0].__setitem__(0,['1','1']),
        'unverified_cache_claim':lambda c:c['optimization'].__setitem__('chiral_incidence_and_row_identity',False),
    };out=[]
    for name,mutate in cases.items():
        bad=deepcopy(v);mutate(bad['checks']);bad=sealed({k:x for k,x in bad.items() if k!='record_digest'})
        try:check(bad,transitions=(name=='frozen_saved_W'))
        except (ValueError,KeyError,IndexError):out.append(name)
        else:raise ValueError('negative control survived: '+name)
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--preflight',action='store_true');g.add_argument('--role',choices=['current','reset']);g.add_argument('--check',action='store_true');args=p.parse_args()
    if args.preflight:write_new(BASE+'AOSPreflight.json',preflight())
    elif args.role:
        pf=load(BASE+'AOSPreflight.json');need(pf['sources']==bindings() and pf['record_digest']==content_id({k:v for k,v in pf.items() if k!='record_digest'}),'preflight drift')
        value=execution(campaign(args.role));check(value);write_new(BASE+'AOS-'+args.role+'.json.xz',value)
    else:
        current=load(BASE+'AOS-current.json.xz');reset=load(BASE+'AOS-reset.json.xz')
        result={role:check(v) for role,v in [('current',current),('reset',reset)]}
        # Read-only replay has no mutation or gain-producing operation.
        write_new(BASE+'AOSChecks.json',sealed(dict(schema='spark-completion-aos-retained-checks-v1',sources=bindings(),checks=result,
            rejected_controls=controls(current),replay=dict(new_gain=0,mutation=False),trajectory_reruns=0)))
