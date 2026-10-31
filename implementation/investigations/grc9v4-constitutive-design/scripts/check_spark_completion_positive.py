"""SC-2 positive candidate: explicit retained checks versus full trajectory rerun."""
import argparse
import hashlib
import json
import lzma
from pathlib import Path
import sys
from fractions import Fraction as F
import flint

ROOT=Path(__file__).resolve().parents[4]
INV='implementation/investigations/grc9v4-constitutive-design/'
REVIEW=INV+'evidence/spark-completion/review/constructive-candidate/'
OUTPUT=INV+'evidence/spark-completion/SC2PositiveCandidate.json.xz'
sys.path[:0]=[str(ROOT/'src'),str(ROOT/INV/'research'),str(ROOT/REVIEW)]
from spark_completion_positive import checks,fixture,trap,content_id,PRECISION,HORIZON
from spark_completion_retained import check_history
import positive_candidate as supplied


def sha(data):return hashlib.sha256(data).hexdigest()


def digest(value):
    return sha(json.dumps({k:v for k,v in value.items()if k!='record_digest'},sort_keys=True,separators=(',',':')).encode())


def build(result=None):
    if result is None:
        result=checks(json.loads(lzma.decompress((ROOT/REVIEW/'positive_candidate_results.json.xz').read_bytes())))
    paths=[INV+'research/'+name+'.py' for name in ('spark_completion_positive','spark_completion_os_reference',
        'spark_completion_continuation','spark_completion_basins','spark_completion_retained')]
    paths += [INV+'scripts/check_spark_completion_positive.py',INV+'decisions/SparkCompletionSC2PositiveCandidate.md',
              INV+'evidence/spark-completion/SC2Continuation.json',INV+'evidence/spark-completion/SC2EventPreflight.json',
              INV+'evidence/spark-completion/SC1Adjudication.json',
              INV+'evidence/spark-completion/review/SC2PositiveScientificPressureReview.md',
              'src/pygrc/models/grc_9_v4_expansion.py','src/pygrc/models/grc_9_v4_topology.py']
    paths += [p.relative_to(ROOT).as_posix()for p in sorted((ROOT/REVIEW).iterdir())if p.is_file()]
    value=dict(schema='grc9v4-spark-sc2-positive-candidate-v1',checks=result,
        arithmetic=dict(python_flint=flint.__version__,target='exact_real_equations',
                        trajectory_precision_bits=8192,trapping_precision_bits=512,
                        automatic_fallback=False,native_rounding_conformance=False),
        equation_binding=dict(family='C_OS',site=dict(c0='2',a='1',mu='1'),
            eta_C='1/1024',duration='32',kappa_Phi_C='1/64',tau_C='1',chi_C='1/2',zeta_C='1/2',
            kappa_H='1/2',kappa_M_C='0',reference_hodges='identity',transport_weights='unit',
            context='constant_zero',selector_cutoff='1/64',split_tolerance='1/100000000000',
            scientific_identity='SC1 selected geometric child policy; exact charge-21 research state, not native profile/event identity'),
        sources=[dict(path=p,sha256=sha((ROOT/p).read_bytes()))for p in paths],
        claim_debt_progress=dict(local_claims=[
            dict(id='SC2-CL-C-POSITIVE-D11-ENTRY',status='conditional_research',
                 statement='Exact supplied source/parent and D11 allocation, followed by rigorously enclosed two-role target evolution, reaches the organized metric ball. Source postbeat formation is not established.'),
            dict(id='SC2-CL-C-FULL-OS-TRAP',status='conditional_research',
                 statement='The actual fifteen-node charge-21 full exact OS map is a strict contraction/self-map on a fourteen-dimensional relative domain with two eligible complete spatial basins.' )],
            organization='SC1 definition unchanged; bounded surviving-parent/new-child gain certified',
            stability='quantitative full-map target trap and two-role entry supplied for review',
            nonempty_domain='target side constructive; actual fresh postbeat source link remains open',
            numerical_lift='exact-equation Arb certification only; native representation/conservation lift remains downstream',
            nonlinear_site_binding='proposed_not_admitted'),
        accepted_authority=False,SC1_closed=True,SC2_closed=False,completed_spark=False,debts_closed=[],G4_accepted=False)
    value['record_digest']=digest(value)
    return value


def check(value):
    assert value['record_digest']==digest(value),'record digest'
    for r in value['sources']:assert sha((ROOT/r['path']).read_bytes())==r['sha256'],r['path']
    expected=build(value['checks'])
    assert value==expected,'scope or local claim/debt semantics changed'
    c=value['checks'];source,states,targets=fixture();fresh,metric=trap(targets['1'])
    assert set(c['roles'])=={'current','reset'},'both role histories required'
    assert c['precision_bits']==PRECISION and c['maximum_steps_per_role']==HORIZON
    assert c['parameters']=={k:str(v)for k,v in supplied.PARAMS.items()},'equation parameters'
    assert source==c['source_graph']
    assert c['source_resources']=={r:{n:str(x)for n,x in v.items()}for r,v in states.items()}
    assert c['targets']=={chi:dict(graph=v['graph'],module=v['module'],
        resources={r:{n:str(x)for n,x in state.items()}for r,state in v['states'].items()},
        research_identity=content_id(v))for chi,v in targets.items()},'actual D11 target binding'
    assert all(c['trap'][k]==v for k,v in fresh.items()),'trapping certificate changed'
    assert min(F(x)-F(fresh['coordinate_radius'])for x in fresh['center'].values())>0,'trap positivity'
    assert c['native_steps']==c['native_events']==0 and c['SC1_closed'] and not c['SC2_closed']
    assert not c['source_postbeat_formation_proved'] and not c['completed_spark'] and not c['native_admission']
    radius=F(fresh['radius'])
    for role,history in c['roles'].items():
        assert history['all_subsequent_exact_steps_certified_by_trap'] is True
        assert history['first_gain_step']=={'current':42,'reset':40}[role]
        assert F(history['trap_distance_upper'][1])<radius
        assert F(history['minimum_resource'][0])>0 and F(history['maximum_split'][1])<F(1,10**11)
        rows=history['observations'];assert len(rows)==history['certified_trap_entry_step']<=c['maximum_steps_per_role']
        for k,row in enumerate(rows,1):
            assert row['step']==k and F(row['minimum_resource'])>0 and F(row['split_upper'])<F(1,10**11)
        assert F(rows[-1]['trap_distance_upper'])<radius
        check_history(history,targets,fresh,metric)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--write',action='store_true');mode.add_argument('--check',action='store_true');mode.add_argument('--rerun',action='store_true')
    args=parser.parse_args();path=ROOT/OUTPUT
    if args.write:
        value=build()
        with path.open('xb')as stream:stream.write(lzma.compress((json.dumps(value,indent=2)+'\n').encode()))
    else:
        value=json.loads(lzma.decompress(path.read_bytes()));check(value)
        if args.rerun:assert build()==value,'recomputed trajectory differs'
    print('PASS: '+('full enclosed trajectory recomputed; ' if args.rerun or args.write else 'retained consistency checked, allocation/trap/entry metric and checkpoint basins recomputed; trajectory not rerun; ')+
          'both roles enter a full-map organized trap. No fresh postbeat source or native completion claim.')
