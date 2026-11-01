"""Declared A_CI campaigns, optimization preflight and retained consistency."""
from pathlib import Path
from fractions import Fraction as F
from copy import deepcopy
import argparse,hashlib,json,lzma,sys,time
ROOT=Path(__file__).resolve().parents[4];INV='implementation/investigations/grc9v4-constitutive-design/'
BASE=INV+'evidence/spark-completion/applicability/'
sys.path[:0]=[str(ROOT/'src'),str(ROOT/INV/'research'),str(ROOT/INV/'evidence/spark-completion/review/constructive-candidate')]
from flint import arb,arb_mat,fmpq,ctx
from spark_completion_a_ci import ACIReference,trap_certificate,PARAMETERS
from spark_completion_a_ci_campaign import campaign,prepare_source,state_payload,root_payload,distance,PRECISION,HORIZON,TIME_LIMIT
from spark_completion_a_os import geometric_roster
from spark_completion_a_os_earlier import decode
from spark_completion_positive import fixture,content_id
from spark_completion_continuation import need

SOURCES=[INV+'research/'+x+'.py' for x in ('spark_completion_a_ci','spark_completion_a_ci_campaign','spark_completion_a_os',
 'spark_completion_a_os_campaign','spark_completion_a_os_earlier','spark_completion_positive','spark_completion_ci_campaign',
 'spark_completion_continuation','spark_completion_basins','spark_completion_os_reference')]+[
 INV+'scripts/'+x+'.py' for x in ('check_spark_completion_applicability_a_ci','test_spark_completion_a_ci')]+[
 BASE+'ACIDeclaration.json',BASE+'earlier-closure/AOSAnisotropicDomain.json',BASE+'AOS-current.json.xz',BASE+'AOS-reset.json.xz',
 BASE+'AOSScientificAcceptance.json',INV+'decisions/spark-completion-a-os/Authority.json',
 INV+'evidence/spark-completion/SC2SourceBeat.json.xz',INV+'evidence/spark-completion/review/constructive-candidate/positive_candidate.py',
 'src/pygrc/models/grc_9_v4_expansion.py','src/pygrc/models/grc_9_v4_topology.py','specs/grc-v4-spec.md','specs/grc-v4-topology-event-spec.md']

def normalized(v):return json.loads(json.dumps(v,default=str))
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def bindings():return [dict(path=p,sha256=sha(p)) for p in SOURCES]
def sealed(v):return {**v,'record_digest':content_id(v)}
def load(path):
    raw=(ROOT/path).read_bytes();return json.loads(lzma.decompress(raw) if path.endswith('.xz') else raw)
def write_new(path,value):
    raw=(json.dumps(value,indent=2,default=str)+'\n').encode();out=lzma.compress(raw,preset=6) if path.endswith('.xz') else raw
    with (ROOT/path).open('xb') as stream:stream.write(out)
    print('SAVED',path,len(raw),'->',len(out),flush=True)

def declaration():
    d=load(BASE+'ACIDeclaration.json');need(d['record_digest']==content_id({k:v for k,v in d.items() if k!='record_digest'}),'declaration digest')
    need(d['family']=='A_CI' and d['parameters']==PARAMETERS and d['full_state']==['C','W_A'] and
         d['precision_bits']==PRECISION and d['maximum_target_steps']==HORIZON and d['time_limit_seconds_per_role']==TIME_LIMIT and
         d['allocation_shares']==['1/128','63/64','1/128'] and d['window_beats']==2 and
         d['source_W']==dict(current='4097/4096',reset='8191/8192',new_internal='1') and
         not d['automatic_fallback'] and not d['accepted_authority'] and d['native_support_added']==[],'declared scope')
    domain=d['borrowed_domain'];need(sha(domain['path'])==domain['sha256'] and
        load(domain['path'])['record_digest']==domain['record_digest'],'borrowed domain identity')
    return d

def interval(pair):
    need(isinstance(pair,list) and len(pair)==2,'interval shape');lo,hi=map(F,pair)
    need(0<=hi-lo<=F(1,2**110),'retained width')
    return arb(fmpq(str((lo+hi)/2)),fmpq(str((hi-lo)/2)))

def overlaps(a,b,label):
    need(a.nrows()==b.nrows() and a.ncols()==b.ncols() and all(x.overlaps(y) for x,y in zip(a.entries(),b.entries())),label+' inconsistency')

def check_root(saved,fresh):
    need(set(saved)=={'flat','H','J','selected_flat','root_error_upper','root_residual_upper','proposal_iterations','proposal_precision_stages'},'whole joint-root coverage')
    for k,M in [('flat',fresh['flat']),('H',fresh['geometry']),('J',fresh['selected']['current']),('selected_flat',fresh['selected']['causal_flat'])]:
        overlaps(arb_mat([[interval(x) for x in row] for row in saved[k]]),M,'root '+k)
    need(all(0<=F(saved[k])<F(1,10**11) for k in ('root_error_upper','root_residual_upper')),'saved root enclosure/error')
    need(saved['proposal_precision_stages']==[128,256,512,1024,2048,4096,8192] and
         1<=saved['proposal_iterations']<=84,'fixed root proposal policy')

def execution(c):return sealed(dict(schema='spark-completion-aci-execution-v1',accepted_authority=False,native_support_added=[],sources=bindings(),checks=normalized(c)))

def check(value,*,transitions=True,complete=True):
    declaration();need(value['record_digest']==content_id({k:v for k,v in value.items() if k!='record_digest'}),'execution digest')
    need(value['schema']=='spark-completion-aci-execution-v1' and value['sources']==bindings(),'execution binding')
    need(not value['accepted_authority'] and value['native_support_added']==[],'execution authority')
    c=value['checks'];source,_,targets=fixture();need(c['source_graph']==source and c['targets']==normalized(targets),'graph binding')
    d=c['decision'];need(d['role']==c['role'] and d['full_state']==['C','W_A'] and not d['reset_probe_earns_live_gain'] and
         not d['native_completion'] and not d['accepted_authority'],'decision scope')
    need(d['first_certified_entry'] is None or d['first_certified_entry']>=1,'event-only completion')
    need(c['source']['source_steps']==1 and not c['source']['reset_advanced'] and not c['source']['W_transfer']['old_history_discarded'],'source/lineage scope')
    need(not c['earlier_family_trajectory_reused'] and c['native_steps']==0,'prior trajectory attribution')
    need(c['arithmetic']==dict(precision_bits=PRECISION,trapping_precision_bits=512,maximum_target_steps=HORIZON,
        time_limit_seconds=TIME_LIMIT,automatic_fallback=False,midpoint_evolution=False,storage_bits=112,
        root_proposal_precision_policy='128 then powers of two through the fixed full precision; proposals only',root_newton_limit_per_precision=12),'arithmetic')
    proof,U=trap_certificate(targets);need(c['proof']==normalized(proof),'full implicit trap changed')
    with ctx.workprec(PRECISION):
        m,C,L,s=prepare_source(source,targets,c['role'])
        need(c['source']==normalized(s),'actual A_CI source/transfer differs')
        need(c['initial_target']==state_payload(m,C,L),'transfer subject differs')
    with ctx.workprec(512):
        m=ACIReference(targets['1']['graph']);metric=arb_mat(U);previousC,previousL=decode(m,c['initial_target'])
        charts={chi:ACIReference(t['graph']) for chi,t in targets.items()};entry=None;gain=None
        for k,row in enumerate(c['observations'],1):
            need(row['step']==k,'consecutive state coverage');C,L=decode(m,row)
            need(all(0<x<4 for x in C.entries()) and sum(C.entries()).contains(21),'retained C domain')
            need(all(m.q(99,100)<x<m.q(101,100) for x in m.exp(L).entries()),'retained W domain')
            rosters={chi:geometric_roster(chart,C,L) for chi,chart in charts.items()};need(row['complete_basins']==rosters,'complete basin roster')
            total=distance(m,C,L,proof,metric)
            delta=arb_mat((C-m.vector(proof['center'])).tolist()+(L-arb_mat([[arb(fmpq(x))] for x in proof['logW_center']])).tolist())
            lower=max(abs(x).lower() for x in (metric*delta).entries());saved=arb(fmpq(row['full_distance_upper']));eps=arb(fmpq(1,2**112))
            need(lower<=saved+eps and saved<=total+eps,'stored norm inconsistent with all coordinates')
            if gain is None and rosters==proof['complete_basins']:gain=k
            if entry is None and total<1:entry=k
            if entry is not None:need(total<1 and rosters==proof['complete_basins'],'positive window left full trap')
            need(all(0<=F(row[name])<F(1,10**11) for name in ('root_error_upper','root_residual_upper')) and
                 1<=row['root_proposal_iterations']<=84,'retained root convergence policy')
            if transitions:
                step=m.step(previousC,previousL);overlaps(C,step['after'],'C recurrence');overlaps(L,step['logW_after'],'W recurrence')
            previousC,previousL=C,L
        success=entry is not None and len(c['observations'])==entry+2
        if complete:need(success,'missing positive completion window')
        expected=dict(role=c['role'],scientific_completion=success and c['role']=='current',local_gain=int(success and c['role']=='current'),
            reset_probe_earns_live_gain=False,first_spatial_gain=gain,first_certified_entry=entry,
            target_completion_step=len(c['observations']) if success else None,window_beats=2,window_elapsed='64',full_state=['C','W_A'],
            stable_descendants=proof['complete_basins'],native_completion=False,accepted_authority=False)
        need(d==expected,'completion accounting')
        need({k:c['checkpoints']['event'][k] for k in ('C','logW')}==c['initial_target'],'event checkpoint')
        for name,k in [('event',None)]+([('entry',entry),('completion',len(c['observations']))] if success else []):
            saved=c['checkpoints'][name]
            if k is not None:need(all(saved[key]==c['observations'][k-1][key] for key in ('C','logW')),'checkpoint identity')
            C,L=decode(m,saved);check_root(saved['root'],m.root(C,L))
        opt=c['optimization'];need(opt['target_joint_roots']==len(c['observations'])==opt['target_writer_calls'] and
            all(opt[k] for k in ('identical_full_state_root_reuse','weighted_rows_reused_within_root_proposal',
                'multi_RHS_geometry_derivative_solve','staged_root_proposals','chiral_incidence_and_row_identity')) and
            not opt['trajectory_results_cached'] and opt['graph_cache_hits']>0 and opt['root_domain_cache_hits']>0,'optimization accounting')
    return dict(status='passed',decision=d,retained_states=len(c['observations']),transition_checks=len(c['observations']) if transitions else 0,
        fresh_implicit_full_state_trap=True,trajectory_rerun=False,
        consistency_only='Saved transition/root overlap is consistency evidence; the source-bound outward campaign supplies trajectory enclosure provenance.')

def preflight():
    declaration();start=time.monotonic();c=campaign('current',8,False);result=check(execution(c),complete=False)
    return sealed(dict(schema='spark-completion-aci-preflight-v1',family='A_CI',sources=bindings(),pilot_steps=8,
        optimization=c['optimization'],validation=result,elapsed_seconds=time.monotonic()-start,
        long_run_authorized_only_after_preflight=True,trajectory_result_reused=False))

def controls(value):
    cases={
        'missing_W_direction':lambda c:c['proof'].__setitem__('conductance_dimension',15),
        'OS_derivative_substitution':lambda c:c['proof'].__setitem__('OS_derivative_reused',True),
        'missing_implicit_feedback':lambda c:c['proof'].__setitem__('implicit_geometry_derivative',False),
        'frozen_stationary_writer':lambda c:c['proof'].__setitem__('stationary_writer_self_consistent',False),
        'C_only_state':lambda c:c['decision'].__setitem__('full_state',['C']),
        'event_only_completion':lambda c:c['decision'].__setitem__('first_certified_entry',0),
        'reset_mints_gain':lambda c:c['decision'].__setitem__('reset_probe_earns_live_gain',True),
        'missing_positive_window':lambda c:c['observations'].pop(),
        'rewritten_old_W':lambda c:c['source']['W_transfer'].__setitem__('old_history_discarded',True),
        'source_beat_omitted':lambda c:c['source'].__setitem__('source_steps',0),
        'reset_advanced':lambda c:c['source'].__setitem__('reset_advanced',True),
        'stale_event_trigger':lambda c:c['source'].__setitem__('spark_margin',['1','1']),
        'missing_saved_W':lambda c:c['observations'][0]['logW'].pop(),
        'frozen_saved_W':lambda c:c['observations'][0].__setitem__('logW',c['initial_target']['logW']),
        'altered_roster':lambda c:c['observations'][0].__setitem__('complete_basins',{}),
        'forged_scalar_entry':lambda c:c['observations'][0].__setitem__('full_distance_upper','0'),
        'wrong_joint_current':lambda c:c['checkpoints']['event']['root']['J'][0].__setitem__(0,['1','1']),
        'unverified_cache_claim':lambda c:c['optimization'].__setitem__('staged_root_proposals',False),
    };out=[]
    for name,mutate in cases.items():
        bad=deepcopy(value);mutate(bad['checks']);bad=sealed({k:v for k,v in bad.items() if k!='record_digest'})
        try:check(bad,transitions=(name=='frozen_saved_W'))
        except (ValueError,KeyError,IndexError):out.append(name)
        else:raise ValueError('negative control survived: '+name)
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--preflight',action='store_true');g.add_argument('--role',choices=['current','reset']);g.add_argument('--check',action='store_true');args=p.parse_args()
    if args.preflight:write_new(BASE+'ACIPreflight.json',preflight())
    elif args.role:
        pf=load(BASE+'ACIPreflight.json');need(pf['sources']==bindings() and pf['record_digest']==content_id({k:v for k,v in pf.items() if k!='record_digest'}),'preflight drift')
        value=execution(campaign(args.role));check(value);write_new(BASE+'ACI-'+args.role+'.json.xz',value)
    else:
        current=load(BASE+'ACI-current.json.xz');reset=load(BASE+'ACI-reset.json.xz')
        result={role:check(value) for role,value in [('current',current),('reset',reset)]}
        value=sealed(dict(schema='spark-completion-aci-retained-checks-v1',sources=bindings(),checks=result,
            rejected_controls=controls(current),replay=dict(new_gain=0,mutation=False),trajectory_reruns=0))
        path=BASE+'ACIChecks.json'
        if (ROOT/path).exists():need(load(path)==value,'retained check record differs');print(json.dumps(value,indent=2))
        else:write_new(path,value)
