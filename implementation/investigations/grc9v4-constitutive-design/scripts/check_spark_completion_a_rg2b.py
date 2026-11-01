"""Bounded A_RG2b proof, preflight, selected prefix generation and fresh replay."""
from pathlib import Path
import sys,json,lzma,hashlib,argparse,time
ROOT=Path(__file__).resolve().parents[4]
INV=ROOT/'implementation/investigations/grc9v4-constitutive-design'
sys.path[:0]=[str(ROOT/'src'),str(INV/'research'),str(INV/'evidence/spark-completion/review/constructive-candidate')]
from spark_completion_a_rg2b_campaign import *
from spark_completion_a_rg2b_direct import curve_certificate

BASE=INV/'evidence/spark-completion/applicability'
DOMAIN_DIGEST='3ec5fc889813183a74d08258d8d9c913931156d5adde44d03554a81490d35b46'
DECLARATION_DIGEST='a2a6d031cee16617a67042d26dc131f8e7bd3c3f67032007c8079426f7a13cfb'
SOURCES=[str((INV/('research/'+name+'.py')).relative_to(ROOT)) for name in (
    'spark_completion_a_rg2b','spark_completion_a_rg2b_direct','spark_completion_a_rg2b_campaign',
    'spark_completion_a_os','spark_completion_c_rg2b','spark_completion_c_rg2b_direct',
    'spark_completion_a_os_earlier','spark_completion_positive','spark_completion_continuation',
    'spark_completion_ci_campaign','spark_completion_basins','spark_completion_os_reference')]
SOURCES += [str(Path(__file__).relative_to(ROOT)),str((BASE/'ARG2bDeclaration.json').relative_to(ROOT)),
    str((BASE/'ARG2bDirectDomain.json').relative_to(ROOT)),
    str((INV/'evidence/spark-completion/review/constructive-candidate/positive_candidate.py').relative_to(ROOT)),
    'src/pygrc/models/grc_9_v4_expansion.py','src/pygrc/models/grc_9_v4_topology.py']


def seal(value):return {**value,'record_digest':content_id(value)}
def load(name):
    p=BASE/name;raw=p.read_bytes();v=json.loads(lzma.decompress(raw) if p.suffix=='.xz' else raw)
    need(v['record_digest']==content_id({k:x for k,x in v.items() if k!='record_digest'}),'sealed record drift')
    return v
def save(name,value):
    p=BASE/name;need(not p.exists(),'refusing to overwrite retained evidence')
    raw=(json.dumps(value,indent=2,ensure_ascii=False)+'\n').encode()
    p.write_bytes(lzma.compress(raw,preset=9) if p.suffix=='.xz' else raw)
    return dict(path=str(p.relative_to(ROOT)),stored_bytes=p.stat().st_size,raw_bytes=len(raw),
        sha256=hashlib.sha256(p.read_bytes()).hexdigest(),uncompressed_sha256=hashlib.sha256(raw).hexdigest())
def refs():return [dict(path=p,sha256=hashlib.sha256((ROOT/p).read_bytes()).hexdigest()) for p in SOURCES]
def inputs():
    d,q=load('ARG2bDeclaration.json'),load('ARG2bDirectDomain.json')
    need(d['record_digest']==DECLARATION_DIGEST and q['record_digest']==DOMAIN_DIGEST and
        d['domain_digest']==q['record_digest'],'declared inputs changed')
    need(d['parameters']==PARAMETERS and d['horizon']==ENTRY+WINDOW and
        d['completion']==ENTRY+WINDOW and d['entry']==ENTRY and not d['accepted_authority'] and
        not d['future_trajectory_required'],'declaration scope')
    return d,q
def stable(run):return {k:v for k,v in run.items() if k not in ('elapsed_seconds','optimization')}


def retained(role):
    d,domain=inputs();v=load('ARG2b-'+role+'.json.xz')
    need(v['sources']==refs() and v['domain_digest']==domain['record_digest'] and
        v['declaration_digest']==d['record_digest'],'execution source bindings')
    run=v['checks'];need(run['role']==role and run['entry']==ENTRY and
        run['completion']==run['last_executed_step']==ENTRY+WINDOW,'completion scope')
    need(run['decision']['local_gain']==int(role=='current') and
        run['decision']['supporting_trajectory_steps_after_completion']==0,'live gain/support scope')
    need([r['step'] for r in run['observations']]==list(range(1,ENTRY+WINDOW+1)),'contiguous prefix')
    with ctx.workprec(PRECISION):
        m=ARG2bReference(run['targets']['1']['graph']);metric(m)
        Q=fmpq_mat([[fmpq(x) for x in row] for row in domain['curves'][role]])
        for row in run['observations']:
            X,r=decode(m,row)
            need(F(row['tube']['strict_image_margin'][0])>0,'stored successor gap')
            C,L=m.unpack(m.tube_box(X,r));need(all(x>0 for x in C.entries()) and m.in_agreement(m.tube_box(X,r)),'retained physical state')
            need(all(value==geometric_roster(m,C,L) for value in row['complete_basins'].values()),'retained basin roster')
        checks=[]
        for row in run['observations'][ENTRY-1:]:
            X,r=decode(m,row);checks.append(membership(m,Q,X,r,row['step'],F(d['entry_parameters'][role])))
        need(checks==run['window_membership'],'retained direct membership')
    return v


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--certificate',action='store_true');p.add_argument('--preflight',action='store_true')
    p.add_argument('--run',choices=['current','reset']);p.add_argument('--replay',choices=['current','reset'])
    p.add_argument('--check',action='store_true');args=p.parse_args()
    need(sum(bool(v) for v in vars(args).values())==1,'select exactly one action')
    d,domain=inputs()
    if args.certificate:
        with ctx.workprec(PRECISION):proof=curve_certificate(domain,'current')
        result=seal(dict(schema='spark-completion-arg2b-direct-certificate-record-v1',sources=refs(),
            domain_digest=domain['record_digest'],checks=proof,common_domain_for_both_roles=True))
        print(json.dumps(save('ARG2bDirectCertificate.json.xz',result)),flush=True)
    elif args.preflight:
        result={}
        for role in ('current','reset'):
            run=campaign(role,d,domain,maximum_steps=8)
            need(run['optimization']['graph_cache_hits']>0 and run['optimization']['domain_cache_hits']>0 and
                run['section_reuse']['forward_reuse_steps']==8,'optimization preflight failed')
            result[role]=dict(elapsed_seconds=run['elapsed_seconds'],optimization=run['optimization'],
                source_trigger=run['source']['spark_margin'],last_tube_radius=run['observations'][-1]['radius'],
                fresh_section_consistency=run['fresh_section_checks']['1']['overlap_consistency'])
        print(json.dumps(save('ARG2bPreflight.json',seal(dict(schema='spark-completion-arg2b-preflight-v1',sources=refs(),checks=result,
            full_campaign_started=False,physical_target_steps_per_role=8)))),flush=True)
    elif args.run:
        preflight=load('ARG2bPreflight.json');certificate=load('ARG2bDirectCertificate.json.xz')
        need(preflight['sources']==refs() and certificate['sources']==refs(),'preflight/certificate source drift')
        run=campaign(args.run,d,domain)
        result=seal(dict(schema='spark-completion-arg2b-prefix-v1',sources=refs(),
            declaration_digest=d['record_digest'],domain_digest=domain['record_digest'],
            certificate_digest=certificate['record_digest'],checks=run))
        print(json.dumps(save('ARG2b-'+args.run+'.json.xz',result)),flush=True)
    elif args.replay:
        original=retained(args.replay);run=campaign(args.replay,d,domain)
        need(stable(run)==stable(original['checks']),'fresh full-prefix replay differs')
        print(json.dumps(dict(role=args.replay,fresh_prefix_replay=True,steps=ENTRY+WINDOW,
            supporting_steps_after_completion=0,elapsed_seconds=run['elapsed_seconds'])),flush=True)
    else:
        cert=load('ARG2bDirectCertificate.json.xz');need(cert['sources']==refs(),'certificate bindings')
        for role in ('current','reset'):
            v=retained(role);print(json.dumps(dict(role=role,retained_state_membership_checks=True,
                record_digest=v['record_digest'],entry=ENTRY,completion=ENTRY+WINDOW)),flush=True)


if __name__=='__main__':main()
