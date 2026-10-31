"""Execute/check the bounded SC-2 research spark completion, not native support."""
import argparse
import hashlib
import json
import lzma
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
INV = 'implementation/investigations/grc9v4-constitutive-design/'
OUTPUT = INV + 'evidence/spark-completion/SC2CompleteWitness.json'
sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_spark_completion_source_beat as source
from spark_completion_complete import run, content_id


def digest(value):
    return content_id({k:v for k,v in value.items() if k!='record_digest'})


def build():
    current = json.loads(lzma.decompress((ROOT/source.OUTPUT).read_bytes()))
    source.check(current)
    previous = source.predecessor()
    result = run(current,previous)
    paths = [source.OUTPUT,source.PREDECESSOR,
             INV+'research/spark_completion_complete.py',INV+'scripts/check_spark_completion_complete.py',
             INV+'decisions/SparkCompletionSC2CompleteWitness.md',
             INV+'decisions/SparkCompletionSC1Contract.md',INV+'evidence/spark-completion/SC1Adjudication.json',
             INV+'evidence/spark-completion/SC2ClaimDebtLedger.json']
    value = dict(schema='grc9v4-spark-sc2-complete-research-witness-v1',checks=result,
                 completion_criterion='grc9v4-certified-geometric-child-basins-v1',
                 equation_binding=previous['equation_binding'],
                 evidence_reuse=dict(source_record_digest=current['record_digest'],
                                     target_record_digest=previous['record_digest'],
                                     full_approach_rerun=False,reset_rerun=False),
                 claim_debt_progress=dict(
                     predecessor_ledger=INV+'evidence/spark-completion/SC2ClaimDebtLedger.json',
                     claim=dict(id='SC2-CL-C-EXACT-SPARK-COMPLETION',claim_class='conditional_mathematical',
                                status='demonstrated_bounded_research',
                                statement='The actual source/event/positive evolution chain satisfies the selected SC1 exact-equation completion criterion: one stable new child and local gain one.',
                                evidence_pointer='/checks/decision',
                                limits=['one C_OS construction under the proposed quartic binding',
                                        'explicit allocation; no general autonomous selection',
                                        'no native representation, receipt or support claim']),
                     debt_dispositions=[
                         dict(debt_id='SC-DEBT-ORGANIZATION',status='partially_resolved_bounded_scientific',
                              resolved='actual parent/descendant comparison and stable local gain',remaining='authority propagation and native conformance'),
                         dict(debt_id='SC-DEBT-STABILITY',status='partially_resolved_bounded_scientific',
                              resolved='actual full-state trap, entry and positive window under exact equations',remaining='native constraint/full-step/diagnostic error policy'),
                         dict(debt_id='SC-DEBT-NONEMPTY-DOMAIN',status='partially_resolved_bounded_scientific',
                              resolved='constructive full source-to-completion witness',remaining='constitutive admission, propagation and native realization'),
                         dict(debt_id='SC-DEBT-TEMPORAL-LIFECYCLE',status='partially_resolved_research_composition',
                              resolved='positive current window, separate reset, event-bound decision and no second research gain on replay',remaining='native schema, atomic owner, invalidation and replay conformance'),
                         dict(debt_id='SC2-DEBT-NONLINEAR-SITE-BINDING',status='open_for_admission',
                              resolved='bounded exact C_OS feasibility demonstrated for the homogeneous quartic',remaining='scientific selection and authority/paper/spec/native binding')],
                     aggregate_debts_closed=[],accepted_forensic_graph_changed=False),
                 sources=[dict(path=p,sha256=hashlib.sha256((ROOT/p).read_bytes()).hexdigest()) for p in paths],
                 scientific_completion_demonstrated=True,native_completion_support=False,
                 native_steps=0,native_events=0,accepted_authority=False,G4_accepted=False)
    value['record_digest']=digest(value)
    return value


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--write',action='store_true');group.add_argument('--check',action='store_true')
    args=parser.parse_args();expected=build();path=ROOT/OUTPUT
    if args.write:
        with path.open('x') as out:out.write(json.dumps(expected,indent=2)+'\n')
    value=json.loads(path.read_bytes())
    if digest(value)!=value['record_digest'] or value!=expected:
        raise ValueError('completion evidence, mathematics or scope changed')
    d=value['checks']['decision']
    print('PASS: bounded research spark completed; target step',d['target_completion_step'],
          '; one new child, local gain',d['certified_local_gain'],
          '; replay adds',value['checks']['replay_decision']['newly_recorded_gain'])
    print('Two new enclosed current steps; ten false-completion controls; source/transfer and trap checks. No native completion claim.')
