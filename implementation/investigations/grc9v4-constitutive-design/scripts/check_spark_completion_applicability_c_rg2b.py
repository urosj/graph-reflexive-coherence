"""Frozen C_RG2b campaigns, cache preflight and retained metric-tube checks."""
from pathlib import Path
from fractions import Fraction as F
from copy import deepcopy
import argparse,hashlib,json,lzma,sys,time
ROOT=Path(__file__).resolve().parents[4];INV='implementation/investigations/grc9v4-constitutive-design/';BASE=INV+'evidence/spark-completion/applicability/'
sys.path[:0]=[str(ROOT/'src'),str(ROOT/INV/'research'),str(ROOT/INV/'evidence/spark-completion/review/constructive-candidate')]
from flint import arb,arb_mat,ctx
from spark_completion_c_rg2b import (CRG2bReference,trap_certificate,PARAMETERS,ball,DEPTH,SWEEPS,NEWTON_LIMIT,
    PROPOSAL_BITS,PRECISION,CENTER_BITS,TRAP_RADIUS,RHO,LIP,DT)
from spark_completion_c_rg2b_campaign import (campaign,prepared_values,prepare_source,state_payload,section_payload,decode,distance,
    HORIZON,TIME_LIMIT,exact_bounds)
from spark_completion_positive import fixture,content_id
from spark_completion_continuation import need,geometric_roster
SOURCES=[INV+'research/'+x+'.py' for x in ('spark_completion_c_rg2b','spark_completion_c_rg2b_campaign','spark_completion_ci',
 'spark_completion_ci_campaign','spark_completion_positive','spark_completion_continuation','spark_completion_basins','spark_completion_os_reference')]+[
 INV+'scripts/'+x+'.py' for x in ('check_spark_completion_applicability_c_rg2b','test_spark_completion_c_rg2b')]+[
 INV+'decisions/SparkCompletionCRG2bApplicability.md',BASE+'CRG2bDeclaration.json',
 INV+'evidence/spark-completion/review/constructive-candidate/positive_candidate.py','src/pygrc/models/grc_9_v4_expansion.py',
 'src/pygrc/models/grc_9_v4_topology.py','specs/grc-v4-spec.md','specs/grc-v4-topology-event-spec.md']
def normalized(v):return json.loads(json.dumps(v,default=str))
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def bindings():return [dict(path=p,sha256=sha(p)) for p in SOURCES]
def sealed(v):return {**v,'record_digest':content_id(v)}
def load(p):
    raw=(ROOT/p).read_bytes();return json.loads(lzma.decompress(raw) if p.endswith('.xz') else raw)
def write_new(p,v):
    raw=(json.dumps(v,indent=2,default=str)+'\n').encode();data=lzma.compress(raw,preset=6) if p.endswith('.xz') else raw
    with (ROOT/p).open('xb') as f:f.write(data)
    print('SAVED',p,len(raw),'->',len(data),flush=True)
def policy():return dict(precision_bits=PRECISION,proposal_bits=PROPOSAL_BITS,center_bits=CENTER_BITS,section_depth=DEPTH,
    proposal_sweeps_limit=SWEEPS,maximum_target_steps=HORIZON,time_limit_seconds=TIME_LIMIT,automatic_fallback=False,
    physical_enclosure='charge-tangent metric tubes with full propagated rounding and finite-section error',
    midpoint_only_evolution=False,storage_bits=112,radius_storage='exact dyadic')
def declaration():
    d=load(BASE+'CRG2bDeclaration.json');need(d['record_digest']==content_id({k:v for k,v in d.items() if k!='record_digest'}),'declaration digest')
    need(d['family']=='C_RG2b' and d['full_state']==['C'] and d['parameters']==PARAMETERS and d['arithmetic']==policy() and
        d['section']==dict(geometry_radius=str(RHO),lipschitz=str(LIP),depth=DEPTH,maximum_sweeps=SWEEPS,newton_limit=NEWTON_LIMIT,
            terminal='identity',completion='bounded_increment_argument_retraction_v1',C1_claimed=False) and
        d['prepared_source']==prepared_values() and d['allocation_shares']==['1/64','31/32','1/64'] and
        d['window_beats']==2 and d['window_elapsed']=='16' and d['trap_radius']==str(TRAP_RADIUS) and
        not d['accepted_authority'] and d['native_support_added']==[],'declared C_RG2b scope')
    return d

def execution(c):return sealed(dict(schema='spark-completion-crg2b-execution-v1',accepted_authority=False,native_support_added=[],sources=bindings(),checks=normalized(c)))
def check(value,*,transitions=True,complete=True):
    decl=declaration();need(value['record_digest']==content_id({k:v for k,v in value.items() if k!='record_digest'}),'execution digest')
    need(value['schema']=='spark-completion-crg2b-execution-v1' and value['sources']==bindings(),'execution source binding')
    need(not value['accepted_authority'] and value['native_support_added']==[],'execution authority')
    c=value['checks'];source,_,targets=fixture();need(c['source_graph']==source and c['targets']==normalized(targets),'graph binding')
    d=c['decision'];need(d['role']==c['role'] and c['role'] in ('current','reset') and d['full_state']==['C'] and
        not d['reset_probe_earns_live_gain'] and not d['native_completion'] and not d['accepted_authority'],'decision scope')
    need(d['first_certified_entry'] is None or d['first_certified_entry']>=1,'event-only completion')
    need(c['arithmetic']==policy() and not c['earlier_family_trajectory_reused'] and c['native_steps']==0,'arithmetic/attribution')
    proof,_=trap_certificate(targets);need(c['proof']==normalized(proof),'full Lipschitz return/trap changed')
    with ctx.workprec(PRECISION):
        m,C,r,record=prepare_source(source,targets,c['role'],decl['prepared_source'])
        need(c['source']==normalized(record),'actual source/section/event differs')
        need(c['section_domain']==m.domain and c['initial_target']==state_payload(m,C,r),'fresh target section/transfer')
        need(set(c['checkpoints'])==({'event','entry','completion'} if complete else {'event'}),'checkpoint coverage')
        previousC,previousR=C,r;previousS=m.section(C) if transitions else None;entry=None;gain=None
        for k,row in enumerate(c['observations'],1):
            need(row['step']==k,'consecutive physical state coverage');C,r=decode(m,row)
            need(0<=r<arb(2)**-64 and sum(C.entries())==21,'physical tube/charge')
            need({key:row[key] for key in ('center','radius','C')}==state_payload(m,C,r),'saved tube coordinate enclosure')
            cb=m.box(C,r);km=list(map(ball,m.domain['K_minus']))
            need(all(0<x and km[0]<x<km[1] for x in cb.entries()),'retained agreement/positive domain')
            rosters={chi:geometric_roster(t['graph'],cb,m.nodes) for chi,t in targets.items()}
            need(row['complete_basins']==rosters,'complete basin roster')
            dist=distance(m,C,r,proof);need(row['trap_distance_upper']==exact_bounds(dist)[1],'stored full trap distance')
            if gain is None and rosters==proof['complete_basins']:gain=k
            if entry is None and dist<ball(proof['radius']):entry=k
            if entry is not None:need(dist<ball(proof['radius']) and rosters==proof['complete_basins'],'positive window left trap')
            if transitions:
                nc,nr,diag=m.advance_tube(previousC,previousR,previousS)
                need(nc==C and nr==r,'validated C/radius recurrence')
                need(row['tube']==dict(lipschitz=exact_bounds(diag['lipschitz']),defect=exact_bounds(diag['defect'],160)),'tube error budget')
                previousS=m.section(C);need(row['section_error']==exact_bounds(previousS['error'],160),'section error budget')
            previousC,previousR=C,r
        success=entry is not None and len(c['observations'])==entry+2
        if complete:need(success,'missing positive completion window')
        expected=dict(role=c['role'],scientific_completion=success and c['role']=='current',local_gain=int(success and c['role']=='current'),
            reset_probe_earns_live_gain=False,first_spatial_gain=gain,first_certified_entry=entry,
            target_completion_step=len(c['observations']) if success else None,window_beats=2,window_elapsed='16',
            full_state=['C'],stable_descendants=proof['complete_basins'],native_completion=False,accepted_authority=False)
        need(d==expected,'completion accounting')
        for name,k in [('event',None)]+([('entry',entry),('completion',len(c['observations']))] if success else []):
            saved=c['checkpoints'][name];original=c['initial_target'] if k is None else c['observations'][k-1]
            need(all(saved[key]==original[key] for key in ('center','radius','C')),'checkpoint identity')
            C,r=decode(m,saved);need(saved['section']==section_payload(m.section(C,retain_chain=True),m,C,r),'finite section chain/read changed')
        opt=c['optimization'];need(opt['target_ordinary_steps']==opt['target_section_calls']==len(c['observations']) and
            all(opt[k] for k in ('immutable_exact_graph_cache','precision_keyed_identity_cache','per_inverse_operator_reuse',
            'certified_proposal_early_stop','validated_metric_tubes','identical_subject_read_reuse','chiral_incidence_identity')) and
            not opt['trajectory_results_cached'] and opt['graph_cache_hits']>0 and opt['domain_cache_hits']>0 and
            len(c['observations'])<=opt['target_proposal_sweeps']<=SWEEPS*len(c['observations']) and
            opt['target_lag_operator_builds']<2*DEPTH*(SWEEPS+1)*len(c['observations']) and opt['target_newton_iterations']>0,'optimization accounting')
    return dict(status='passed',decision=d,retained_states=len(c['observations']),transition_checks=len(c['observations']) if transitions else 0,
        fresh_full_Lipschitz_trap=True,trajectory_rerun=False,
        consistency_only='Deterministic fresh section and tube-step checks establish retained consistency; the bound outward producer supplies enclosure provenance.')

def preflight():
    d=declaration();start=time.monotonic();c=campaign('current',d['prepared_source'],8,False);result=check(execution(c),complete=False)
    return sealed(dict(schema='spark-completion-crg2b-preflight-v1',family='C_RG2b',sources=bindings(),pilot_steps=8,
        optimization=c['optimization'],validation=result,elapsed_seconds=time.monotonic()-start,
        long_run_authorized_only_after_preflight=True,trajectory_result_reused=False))
def controls(value):
    cases={
        'section_C1_invented':lambda c:c['proof'].__setitem__('section_C1_claimed',True),
        'quartic_inverse_replaced':lambda c:c['proof']['section_domain'].__setitem__('reference_zero_site_bounds_reused',True),
        'completion_changed':lambda c:c['section_domain'].__setitem__('completion','none'),
        'ordinary_map_bound_omitted':lambda c:c['proof'].__setitem__('full_return_difference_bound',False),
        'geometry_history_transported':lambda c:c['source'].__setitem__('geometry_history_transported',True),
        'stale_target_section':lambda c:c['source'].__setitem__('target_section_rebuilt',False),
        'source_beat_omitted':lambda c:c['source'].__setitem__('source_steps',0),
        'stale_trigger':lambda c:c['source'].__setitem__('spark_margin',['1','1']),
        'reset_advanced':lambda c:c['source'].__setitem__('reset_advanced',True),
        'event_only_completion':lambda c:c['decision'].__setitem__('first_certified_entry',0),
        'reset_mints_gain':lambda c:c['decision'].__setitem__('reset_probe_earns_live_gain',True),
        'physical_state_widened':lambda c:c['decision'].__setitem__('full_state',['C','H']),
        'old_trajectory_relabelled':lambda c:c.__setitem__('earlier_family_trajectory_reused',True),
        'shortened_window':lambda c:c['observations'].pop(),
        'wrong_elapsed_time':lambda c:c['decision'].__setitem__('window_elapsed','64'),
        'missing_resource_coordinate':lambda c:c['observations'][0]['center'].pop(next(iter(c['observations'][0]['center']))),
        'forged_trap_entry':lambda c:c['observations'][0].__setitem__('trap_distance_upper','0'),
        'incomplete_basins':lambda c:c['observations'][0].__setitem__('complete_basins',{}),
        'erased_tube_radius':lambda c:c['observations'][0].__setitem__('radius','0'),
        'missing_error_budget':lambda c:c['observations'][0]['tube'].__setitem__('defect',['0','0']),
        'section_tail_erased':lambda c:c['checkpoints']['event']['section'].__setitem__('tail',['0','0']),
        'wrong_inverse_chain':lambda c:c['checkpoints']['event']['section']['chain'][0]['X'].__setitem__(0,'1'),
        'wrong_selected_current':lambda c:c['checkpoints']['event']['section']['J'][0].__setitem__(0,['1','1']),
        'uncached_long_run':lambda c:c['optimization'].__setitem__('per_inverse_operator_reuse',False),
        'midpoint_only_evolution':lambda c:c['arithmetic'].__setitem__('midpoint_only_evolution',True),
    };out=[]
    for name,mutate in cases.items():
        bad=deepcopy(value);mutate(bad['checks']);bad=sealed({k:v for k,v in bad.items() if k!='record_digest'})
        try:check(bad,transitions=name=='missing_error_budget')
        except (ValueError,KeyError,IndexError):out.append(name)
        else:raise ValueError('negative control survived: '+name)
    return out
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--preflight',action='store_true');g.add_argument('--role',choices=['current','reset']);g.add_argument('--check',action='store_true');args=p.parse_args()
    if args.preflight:write_new(BASE+'CRG2bPreflight.json',preflight())
    elif args.role:
        pf=load(BASE+'CRG2bPreflight.json');need(pf['sources']==bindings() and pf['record_digest']==content_id({k:v for k,v in pf.items() if k!='record_digest'}),'preflight drift')
        d=declaration();v=execution(campaign(args.role,d['prepared_source']));check(v,transitions=False);write_new(BASE+'CRG2b-'+args.role+'.json.xz',v)
    else:
        values={role:load(BASE+'CRG2b-'+role+'.json.xz') for role in ('current','reset')}
        results={role:check(v) for role,v in values.items()}
        write_new(BASE+'CRG2bChecks.json',sealed(dict(schema='spark-completion-crg2b-retained-checks-v1',sources=bindings(),
            checks=results,rejected_controls=controls(values['current']),replay=dict(new_gain=0,mutation=False))))
