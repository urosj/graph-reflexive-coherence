"""Explicit new CI execution versus retained-integrity and freshly recomputed trap."""
from pathlib import Path
import argparse,hashlib,json,lzma,sys
ROOT=Path(__file__).resolve().parents[4]
INV='implementation/investigations/grc9v4-constitutive-design/'
BASE=INV+'evidence/spark-completion/applicability/'
sys.path[:0]=[str(ROOT/'src'),str(ROOT/INV/'research'),str(ROOT/INV/'evidence/spark-completion/review/constructive-candidate')]
from spark_completion_ci_campaign import run,retained,exact_bounds
from spark_completion_ci import trap_certificate,CCIReference
from spark_completion_positive import fixture,content_id
from spark_completion_continuation import need,geometric_roster
from fractions import Fraction as F
from flint import arb,arb_mat,fmpq,ctx

SOURCES=[INV+'research/'+p+'.py'for p in ['spark_completion_ci','spark_completion_ci_campaign','spark_completion_os_reference','spark_completion_positive','spark_completion_basins','spark_completion_continuation']]+[
    INV+'evidence/spark-completion/SC2SourceBeat.json.xz',INV+'evidence/spark-completion/SC2PositiveCandidate.json.xz',
    INV+'decisions/spark-completion/Authority.json',BASE+'CCIDeclaration.json',
    INV+'scripts/check_spark_completion_applicability_ci.py',
    'src/pygrc/models/grc_9_v4_expansion.py','src/pygrc/models/grc_9_v4_topology.py']


def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def build(role):
    sources=[dict(path=p,sha256=sha(p))for p in SOURCES]
    result=run(role)
    need(all(sha(r['path'])==r['sha256']for r in sources),'inputs changed during run')
    v=dict(schema='spark-completion-cci-applicability-execution-v1',checks=result,sources=sources,
        claim_class='conditional_mathematical_research',accepted_authority=False,native_support_added=[])
    v['record_digest']=content_id(v);return v


def check(v):
    need(v['record_digest']==content_id({k:x for k,x in v.items()if k!='record_digest'}),'record digest')
    need(v['schema']=='spark-completion-cci-applicability-execution-v1' and
         v['claim_class']=='conditional_mathematical_research' and not v['accepted_authority'] and
         v['native_support_added']==[],'scope drift')
    need(v['sources']==[dict(path=p,sha256=sha(p))for p in SOURCES],'execution sources changed')
    c=v['checks'];role=c['role'];need(role in ('current','reset'),'role')
    source,_,targets=fixture()
    need(content_id(c['source_graph'])==content_id(source)and content_id(c['targets'])==content_id(targets),'D11 topology/inputs')
    with ctx.workprec(512):
        old=retained('SC2PositiveCandidate.json.xz');proof,P=trap_certificate({**targets['1'],'charts':targets},old['checks']['trap'])
        need(c['proof']==proof,'full CI trap changed')
        m=CCIReference(targets['1']['graph']);center=m.vector(proof['center'])
        need(c['root_domain']==m.domain,'joint root domain changed')
        rows=c['observations'];d=c['decision'];entry=d['first_certified_entry']
        need(len(rows)==d['target_completion_step']==entry+2<=1024 and d['window_elapsed']=='64' and d['window_beats']==2,'window')
        need(d['scientific_completion']==(role=='current')and d['local_gain']==(1 if role=='current'else 0)
             and not d['reset_probe_earns_live_gain'] and not d['native_completion'] and not d['accepted_authority'],'completion scope')
        need(d['stable_descendants']==proof['complete_basins']and d['full_state']==['C'],'completion subject')
        for i,row in enumerate(rows,1):
            need(row['step']==i and F(row['minimum_resource'][0])>0,'positive consecutive steps')
            cells=row['C'];need(set(cells)==set(m.nodes),'resource coverage')
            C=m.matrix([[arb(fmpq(str((F(cells[n][0])+F(cells[n][1]))/2)),fmpq(str((F(cells[n][1])-F(cells[n][0]))/2)))]for n in m.nodes])
            need(all(C[k,0]>0 and C[k,0]<4 for k in range(m.n)),'declared root domain')
            need(sum(C[k,0]for k in range(m.n)).contains(arb(21)),'charge enclosure')
            actual={chi:geometric_roster(t['graph'],C,m.nodes)for chi,t in targets.items()}
            need(row['complete_basins']==actual,'saved complete basins')
            if i>=entry:
                diff=C-center;distance=(diff.transpose()*arb_mat(P)*diff)[0,0].sqrt()
                need(distance<m.q(fmpq(proof['radius']))and actual==proof['complete_basins'],'saved trap/window coordinates')
        for name,index in [('entry',entry),('completion',len(rows))]:
            need(c['checkpoints'][name]['C']==rows[index-1]['C'],'checkpoint differs from saved state')
        need(not c['OS_trajectory_reused'] and c['native_steps']==0,'wrong evidence attribution')
    return d


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--role',choices=['current','reset'],required=True)
    modes=p.add_mutually_exclusive_group(required=True);modes.add_argument('--run',action='store_true');modes.add_argument('--check',action='store_true')
    args=p.parse_args();path=ROOT/BASE/('CCI-'+args.role+'.json.xz')
    if args.run:
        need(not path.exists(),'refusing to overwrite existing execution')
        v=build(args.role);raw=json.dumps(v,indent=2,default=str).encode()+b'\n'
        path.write_bytes(lzma.compress(raw,preset=6))
        print('SAVED',args.role,len(raw),'bytes ->',path.stat().st_size,flush=True)
    else:v=json.loads(lzma.decompress(path.read_bytes()))
    print(json.dumps(check(v),indent=2),flush=True)
