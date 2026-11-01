"""Reproduce the faster certificate; optional complete fresh trajectory replay."""
from pathlib import Path
import sys,json,argparse,hashlib,time,contextlib,io
ROOT=Path(__file__).resolve().parents[4];INV=ROOT/'implementation/investigations/grc9v4-constitutive-design'
sys.path[:0]=[str(ROOT/'src'),str(INV/'research'),str(INV/'evidence/spark-completion/review/constructive-candidate')]
from spark_completion_c_rg2b_faster import *


def checked_inputs():
    declaration=load(DECLARATION)
    need(declaration['record_digest']=='c506311de72e15c5759805ea77fb53150f2fe9b0369ae5862ba10da89e4453a0','faster declared subject')
    need(declaration['parameters']==PARAMETERS and declaration['entry']==ENTRY and not declaration['accepted_authority'],'faster declaration scope')
    runs={}
    for role in ('current','reset'):
        v=load(BASE+'CRG2bFaster-'+role+'.json.xz')
        need(v['declaration_digest']==declaration['record_digest'],'execution declaration')
        for ref in v['sources']:need(hashlib.sha256((ROOT/ref['path']).read_bytes()).hexdigest()==ref['sha256'],'faster source drift')
        runs[role]=v['checks'];need(runs[role]['role']==role,'execution role')
    return declaration,runs


def check(replay=False):
    start=time.monotonic();declaration,runs=checked_inputs();retained=load(BASE+'CRG2bFasterCertificate.json')
    actual=seal(union_certificate(runs));need(actual==retained,'faster trapping certificate differs')
    if replay:
        for role,run in runs.items():
            with contextlib.redirect_stdout(io.StringIO()):fresh=campaign(role,declaration)
            same=lambda x:{k:v for k,v in x.items()if k!='elapsed_seconds'}
            need(content_id(same(fresh))==content_id(same(run)),'complete fresh replay differs: '+role)
    return dict(status='passed',complete_fresh_trajectory_replays=2 if replay else 0,
        checked_union_components=retained['components'],retained_states=sum(len(r['observations'])for r in runs.values()),
        entry=retained['entry_step'],completion=retained['completion_step'],duration=retained['ordinary_duration'],
        contraction=retained['common_contraction']['contraction'],accepted_authority=False,elapsed_seconds=time.monotonic()-start)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--replay',action='store_true');args=parser.parse_args();print(json.dumps(check(args.replay),indent=2))
