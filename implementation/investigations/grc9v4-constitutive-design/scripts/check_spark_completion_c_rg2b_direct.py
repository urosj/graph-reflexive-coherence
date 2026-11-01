"""Check the continuous domain and optional fresh, strictly 392-step prefixes.

--generate writes the declared direct certificate and two XZ prefix artifacts.
--replay recomputes both prefixes. Neither command opens the superseded tails.
"""
from pathlib import Path
import sys,json,lzma,hashlib,argparse,time
ROOT=Path(__file__).resolve().parents[4]
INV=ROOT/'implementation/investigations/grc9v4-constitutive-design'
sys.path[:0]=[str(ROOT/'src'),str(INV/'research'),str(INV/'evidence/spark-completion/review/constructive-candidate')]
from spark_completion_c_rg2b_direct import *

CERTIFICATE=BASE+'CRG2bDirectCertificate.json'
DOMAIN_DIGEST='38dfef2b0ae531ad14a2d85668930c1adafefef74188704b830460e82eab1476'
DECLARATION_DIGEST='4ad1ef81357fa55cfa389157f24f6fbed316c55121f183bed2a74ba636772b60'
PREFIX=BASE+'CRG2bDirect-'
SOURCES=[DECLARATION,DOMAIN,
    str((INV/'research/spark_completion_c_rg2b_direct.py').relative_to(ROOT)),
    str((INV/'research/spark_completion_c_rg2b_faster.py').relative_to(ROOT)),
    str((INV/'research/spark_completion_c_rg2b.py').relative_to(ROOT)),
    str((INV/'research/spark_completion_c_rg2b_campaign.py').relative_to(ROOT)),
    *[str((INV/('research/'+name+'.py')).relative_to(ROOT)) for name in (
        'spark_completion_positive','spark_completion_a_os_earlier','spark_completion_continuation',
        'spark_completion_basins','spark_completion_ci_campaign','spark_completion_os_reference')],
    str(Path(__file__).relative_to(ROOT))]


def inputs():
    d,domain=load(DECLARATION),load(DOMAIN)
    need(d['record_digest']==DECLARATION_DIGEST and domain['record_digest']==DOMAIN_DIGEST,'direct declared subject changed')
    need(d['domain_digest']==domain['record_digest'] and d['parameters']==PARAMETERS and
         d['entry']==ENTRY and d['completion']==d['horizon']==ENTRY+WINDOW and
         not d['accepted_authority'] and not d['future_trajectory_required'],'direct declaration scope')
    return d,domain


def refs():return [dict(path=p,sha256=hashlib.sha256((ROOT/p).read_bytes()).hexdigest()) for p in SOURCES]


def proposal_inputs(path):
    """Export only fixed graph algebra, reference center and prefix endpoint."""
    _,domain=inputs()
    with ctx.workprec(PRECISION):
        _,_,targets=fixture();m=CRG2bReference(targets['1']['graph'])
        row=load(PREFIX+'current.json.xz')['checks']['observations'][ENTRY-1]
        value=dict(nodes=m.nodes,center=domain['center'],at390=row['center'],
            **{k:[[str(x) for x in row] for row in m.algebra[k].tolist()] for k in ('A','L','P')})
    Path(path).write_text(json.dumps(value,indent=2)+'\n')


def generate():
    d,domain=inputs();cert=seal(direct_certificate(domain))
    (ROOT/CERTIFICATE).write_text(json.dumps(cert,indent=2)+'\n')
    for role in ('current','reset'):
        run=campaign(role,d,domain)
        value=seal(dict(schema='spark-completion-crg2b-direct-execution-v1',declaration_digest=d['record_digest'],
            domain_digest=domain['record_digest'],sources=refs(),checks=run))
        raw=(json.dumps(value,indent=2)+'\n').encode();compressed=lzma.compress(raw,preset=9)
        (ROOT/(PREFIX+role+'.json.xz')).write_bytes(compressed)
        print(json.dumps(dict(role=role,steps=run['last_executed_step'],seconds=run['elapsed_seconds'],
            raw_bytes=len(raw),compressed_bytes=len(compressed))),flush=True)


def check(replay=False):
    start=time.monotonic();d,domain=inputs()
    cert=seal(direct_certificate(domain));need(cert==load(CERTIFICATE),'direct certificate differs')
    with ctx.workprec(PRECISION):
        _,_,targets=fixture();m=CRG2bReference(targets['1']['graph'])
        Q=fmpq_mat([[fmpq(v) for v in row] for row in domain['chebyshev_coefficients']])
        for role in ('current','reset'):
            v=load(PREFIX+role+'.json.xz');run=v['checks']
            need(v['sources']==refs() and v['declaration_digest']==d['record_digest'] and
                 v['domain_digest']==domain['record_digest'],'direct execution source identity')
            need(run['role']==role and run['last_executed_step']==ENTRY+WINDOW and
                 run['arithmetic']['horizon']==ENTRY+WINDOW,'direct execution horizon/role')
            need([r['step'] for r in run['observations']]==list(range(1,ENTRY+WINDOW+1)),'direct prefix is incomplete or contains a tail')
            window=run['observations'][ENTRY-1:]
            need([membership(m,Q,row) for row in window]==run['window_membership'],'direct window membership differs')
            need(all(row['complete_basins']==cert['complete_basins'] for row in window),'direct window roster differs')
            if replay:
                fresh=campaign(role,d,domain)
                same=lambda x:{k:v for k,v in x.items() if k!='elapsed_seconds'}
                need(same(fresh)==same(run),'fresh prefix replay differs: '+role)
    return dict(status='passed',entry=ENTRY,completion=ENTRY+WINDOW,ordinary_duration=str(DT),
        retained_states=2*(ENTRY+WINDOW),last_executed_step=ENTRY+WINDOW,
        supporting_trajectory_steps_after_completion=0,trajectory_inputs_to_domain_checker=0,
        complete_fresh_trajectory_replays=2 if replay else 0,
        certificate_digest=cert['record_digest'],contraction=cert['common_contraction']['contraction'],
        strict_image_margin=cert['strict_image_margin'],same_implementation_replay=True,
        independent_external_review_claimed=False,accepted_authority=False,elapsed_seconds=time.monotonic()-start)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    group=p.add_mutually_exclusive_group()
    group.add_argument('--generate',action='store_true');group.add_argument('--replay',action='store_true')
    group.add_argument('--export-proposal-inputs',metavar='PATH')
    args=p.parse_args()
    if args.generate:generate()
    elif args.export_proposal_inputs:proposal_inputs(args.export_proposal_inputs)
    else:print(json.dumps(check(args.replay),indent=2))
