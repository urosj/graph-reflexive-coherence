"""SC-2 source beat: exact fresh capture, explicit reset reuse, target entry."""
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
SIDE=INV+'tools/exploratory-side-tool'
PREDECESSOR=INV+'evidence/spark-completion/SC2PositiveCandidate.json.xz'
OUTPUT=INV+'evidence/spark-completion/SC2SourceBeat.json.xz'
sys.path[:0]=[str(ROOT/'src'),str(ROOT/INV/'research'),
             str(ROOT/INV/'evidence/spark-completion/review/constructive-candidate'),
             str(ROOT/SIDE/'tool/src')]
from spark_completion_source_beat import run,prepare
from spark_completion_positive import content_id,trap
from spark_completion_retained import check_history
from grcv4_explorer.basin import load_basin_forensic_context
from grcv4_explorer.forensic import contract_provenance


def sha(data):return hashlib.sha256(data).hexdigest()


def digest(v):return sha(json.dumps({k:x for k,x in v.items()if k!='record_digest'},sort_keys=True,separators=(',',':')).encode())


def predecessor():
    v=json.loads(lzma.decompress((ROOT/PREDECESSOR).read_bytes()))
    assert digest(v)==v['record_digest'],'predecessor digest'
    for r in v['sources']:assert sha((ROOT/r['path']).read_bytes())==r['sha256'],r['path']
    return v


def build(result=None):
    old=predecessor()
    if result is None:result=run(old)
    context=load_basin_forensic_context(ROOT,ROOT/SIDE)
    ids=('D10.2-EC-PARENT-GRC9-HYBRID-SPARK',
         'D10.2-EC-PARENT-BASE-GRC9-ROW-BASIS-DIFFERENTIAL',
         'D11-G9-EC-RESOURCE-DISTRIBUTION','D11-G9-EC-LIFECYCLE-READMISSION')
    traces={key:contract_provenance(context,key)for key in ids}
    paths=(PREDECESSOR,INV+'research/spark_completion_source_beat.py',INV+'research/spark_completion_retained.py',
           INV+'scripts/check_spark_completion_source_beat.py',INV+'decisions/SparkCompletionSC2SourceBeat.md',
           'specs/grc-9-v4-spec.md','src/pygrc/models/grc_9_v4_lifecycle.py',
           'src/pygrc/models/grc_9_v4_topology.py','src/pygrc/models/grc_9_v4_api_lifecycle.py',
           'src/pygrc/models/grc_9_v4_expansion.py')
    value=dict(schema='grc9v4-spark-sc2-source-beat-v1',checks=result,
        arithmetic=dict(python_flint=flint.__version__,source_beat='exact_rational',
            source_proposal_precision_bits=512,current_prestate_dyadic_bits=80,
            target_precision_bits=8192,automatic_fallback=False,native_rounding_conformance=False),
        sources=[dict(path=p,sha256=sha((ROOT/p).read_bytes()))for p in paths],
        forensic_traces=traces,
        claim_debt_progress=dict(local_claims=[
            dict(id='SC2-CL-C-ORDINARY-SOURCE-LINK',status='conditional_research_ready_for_review',
                 statement='An exact positive ordinary source beat produces a fresh eligible source whose qualified parent contains the expanded vertex; reset is unchanged.'),
            dict(id='SC2-CL-C-SOURCE-EVENT-TRAP-CHAIN',status='conditional_research_ready_for_review',
                 statement='The actual fresh current poststate transfers under the D11 law and reaches the proved organized full-map trap; the unchanged reset subject reuses its pinned entry proof.')],
            organization='selected SC1 criterion met by the bounded exact-equation chain',
            stability='existing full-map trapping certificate applies to actual current entry and unchanged reset entry',
            nonempty_domain='ordinary-source/fresh-capture/event/target chain supplied; ready for scoped scientific adjudication',
            temporal_lifecycle='one research source beat/event chain; native receipts, replay and publication remain downstream',
            nonlinear_site_binding='proposed_not_admitted'),
        SC1_closed=True,SC2_closed=False,accepted_authority=False,completed_spark=False,debts_closed=[],G4_accepted=False)
    value['record_digest']=digest(value);return value


def check(value):
    assert digest(value)==value['record_digest'],'record digest'
    for r in value['sources']:assert sha((ROOT/r['path']).read_bytes())==r['sha256'],r['path']
    assert build(value['checks'])==value,'scope/provenance/claim drift'
    old=predecessor();c=value['checks'];fresh=prepare();targets=fresh.pop('targets')
    proof,metric=trap(targets['1'])
    assert all(old['checks']['trap'][k]==v for k,v in proof.items()),'predecessor trapping certificate changed'
    assert c['prepared']==fresh,'source stage/capture/actual transfer mismatch'
    assert c['source_ordinary_steps']==1 and c['research_event_count']==1
    assert c['native_steps']==c['native_events']==0 and not c['completed_spark'] and not c['accepted_authority']
    assert not c['reset_advanced_by_source_beat']
    assert c['conditional_scientific_completion_witness'] is True and c['SC1_closed'] and not c['SC2_closed']
    reuse=dict(predecessor_role='reset',exact_state_unchanged=True,
        certified_trap_entry_step=old['checks']['roles']['reset']['certified_trap_entry_step'],
        evidence_digest=content_id(old['checks']['roles']['reset']),additional_reset_steps_executed=0)
    assert c['reset_reuse']==reuse,'reset evidence scope changed'
    assert fresh['transferred_reset']==old['checks']['targets']['1']['resources']['reset']
    current=c['actual_current_target'];rows=current['observations']
    assert len(rows)==current['certified_trap_entry_step']==c['current_target_steps']<=1024
    assert F(current['trap_distance_upper'][1])<F(old['checks']['trap']['radius'])
    assert F(current['minimum_resource'][0])>0 and F(current['maximum_split'][1])<F(1,10**11)
    for k,row in enumerate(rows,1):
        assert row['step']==k and F(row['minimum_resource'])>0 and F(row['split_upper'])<F(1,10**11)
    assert F(rows[-1]['trap_distance_upper'])<F(old['checks']['trap']['radius'])
    check_history(current,targets,proof,metric)
    check_history(old['checks']['roles']['reset'],targets,proof,metric)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--write',action='store_true');mode.add_argument('--check',action='store_true');mode.add_argument('--rerun',action='store_true')
    args=parser.parse_args();p=ROOT/OUTPUT
    if args.write:
        v=build()
        with p.open('xb')as out:out.write(lzma.compress((json.dumps(v,indent=2)+'\n').encode()))
    else:
        v=json.loads(lzma.decompress(p.read_bytes()));check(v)
        if args.rerun:assert build()==v,'recomputed actual-target trajectory differs'
    print('PASS: exact ordinary source beat, fresh capture and both-role transfer; '+
          ('changed current trajectory rerun'if args.rerun or args.write else 'trap/entry metric and checkpoint basins recomputed; retained consistency checked, target trajectory not rerun')+
          '; unchanged reset evidence reused. No native completion/admission grant.')
