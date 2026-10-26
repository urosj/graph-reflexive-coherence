"""Bounded C_OS internal lifecycle campaign. Retained checks never rerun it."""
import argparse
from contextlib import ExitStack
import json
import lzma
from pathlib import Path
import signal
import time
import unittest
from unittest.mock import patch

from pygrc.models import grc_9_v4_lifecycle as native
from pygrc.models.grc_v4_codec import canonical_json_bytes
from pygrc.models.grc_v4_exact import ExactBackend, exact_backend
from pygrc.models.grc_v4_numerics import NumericalPolicy, numerical_policy, matrix_operation
from p984h_validation_reuse import validation_reuse, POLICY
from p984i_first_group import ROOT, BASE, HERE, SIDE, require, seal, sha, safe

PLAN = BASE + 'P9-8.5-COSPlan.md'
REVIEW = BASE + 'P9-8.5-COSReview.md'
EVENT = BASE + 'P9-8.4h-COSEventSuccessor.json.xz'
HANDOFF = BASE + 'P9-8.4i-FirstGroup.json'
INPUTS = BASE + 'P9-8.5-COSInputs.json'
SELF = HERE + 'p985_cos.py'
TEST = HERE + 'test_p985_cos.py'
CASES = ('frozen_request_failures', 'self_loop', 'reset_only_split',
         'publication_failures', 'event_replay', 'incomplete_reference',
         'continuation_reset', 'reset_rollback')
CAPS = dict(small=300, large=1200)
OBSERVATIONS = {}


def result_path(segment):
    require(segment in CAPS, 'unknown segment')
    return BASE + 'P9-8.5-COS-' + segment + '.json'


def manifest():
    paths = {PLAN, SELF, TEST, EVENT, HANDOFF,
             HERE+'p984h_validation_reuse.py'}
    for pattern in ('src/pygrc/models/grc_v4*.py', 'src/pygrc/models/grc_9_v4*.py',
                    'src/pygrc/models/_grc_v4*.py', 'tests/models/test_grc_v4*.py',
                    'tests/models/test_grc_9_v4*.py', 'specs/grc*v4*.json'):
        paths.update(str(p.relative_to(ROOT)) for p in ROOT.glob(pattern))
    return seal(dict(schema='p985-cos-inputs-v1', family='C_OS', cases=list(CASES),
        caps=CAPS, source_bindings={p:sha((ROOT/p).read_bytes()) for p in sorted(paths)},
        exact_backend='flint', numerical_policy='certified_arb_256_weighted_v1',
        exact_split_controls='legacy_exact_v1; separately declared, no automatic fallback',
        schema_memo=POLICY, public_specialization_facade=False,
        large_new_trajectory_steps=0, raw_budget_per_result=150000))


def scope(*, matrix=False):
    stack=ExitStack()
    stack.enter_context(exact_backend(ExactBackend.FLINT))
    stack.enter_context(numerical_policy(NumericalPolicy.CERTIFIED_ARB_256))
    stack.enter_context(validation_reuse())
    if matrix:stack.enter_context(matrix_operation())
    return stack


def occupancy(graph):
    slots=[(e.tail.node_id,e.tail.port) for e in graph.edges]
    slots += [(e.head.node_id,e.head.port) for e in graph.edges]
    require(len(slots)==len(set(slots)), 'duplicate occupied endpoint')
    return dict(vertices=len(graph.live_node_ids), edges=len(graph.edges), occupied_ports=len(slots))


def large():
    record=json.loads(lzma.decompress((ROOT/EVENT).read_bytes()))
    require(record==seal(record) and record['outcome']=='completed', 'event integrity')
    cp=record['execution']['checkpoint']; raw=canonical_json_bytes(cp)
    reads=[]; original=native._cos_readmit
    def observed(s):
        before=s.to_payload()
        original(s)
        require(s.to_payload()==before, 'readmission mutated state')
        reads.append(dict(scientific_digest=s.scientific_digest, reset_digest=s.reset_digest,
                          roles=['current','reset']))
    with patch.object(native,'_cos_readmit',observed):
        restored=native.GRC9V4COSOperation.replay(raw)
    require(restored.checkpoint()==raw, 'large native replay differs')
    require(len(reads)==3, 'expected source constructor, source event, target admission')
    require(reads[0]==reads[1] and reads[2]['scientific_digest']==cp['state']['scientific_digest'],
            'wrong readmission subject')
    require(len(restored.receipts)==4 and restored.state.inputs.current!=restored.state.inputs.reset,
            'receipt/role coverage')
    require(cp['initial']['inputs']['step_index']==2, 'wrong accepted source beat')
    graph=restored.state.inputs.geometry.reference.graph.port_graph
    return dict(checkpoint_sha256=sha(raw), event_record_digest=record['record_digest'],
        event_id=record['execution']['event_id'], source_vertices=100, **occupancy(graph),
        readmissions=reads, checkpoint_exact=True, receipt_count=len(restored.receipts),
        fresh_native_events=1, fresh_ordinary_steps=0,
        lifecycle_digest=restored.state.lifecycle_digest(restored.receipts))


def run(segment):
    frozen=json.loads((ROOT/INPUTS).read_text())
    require(frozen==manifest(), 'execution source drift; prepare before running')
    destination=ROOT/result_path(segment)
    require(not destination.exists(), 'refuse to overwrite retained execution')
    def timeout(*_): raise TimeoutError('bounded '+segment+' cap exceeded')
    previous=signal.signal(signal.SIGALRM,timeout); signal.alarm(CAPS[segment])
    started=time.monotonic()
    try:
        with scope(matrix=segment=='large'):
            if segment=='large': observations=large()
            else:
                from test_p985_cos import COSLifecycleTests
                OBSERVATIONS.clear()
                suite=unittest.defaultTestLoader.loadTestsFromTestCase(COSLifecycleTests)
                result=unittest.TextTestRunner(verbosity=2).run(suite)
                require(result.wasSuccessful() and result.testsRun==len(CASES) and not result.skipped,
                        'small lifecycle suite failed')
                require(set(OBSERVATIONS)==set(CASES), 'missing case evidence')
                observations=dict(cases=dict(OBSERVATIONS), tests=result.testsRun)
        evidence=seal(dict(schema='p985-cos-execution-v1', segment=segment, family='C_OS',
            manifest_digest=frozen['record_digest'], outcome='passed', observations=observations,
            elapsed_seconds=time.monotonic()-started, user_accepted=False,
            aggregate_closed=False, public_specialization_facade=False, new_G2_support=[],G3_accepted=False))
        raw=(json.dumps(evidence,indent=2,allow_nan=False)+'\n').encode()
        require(len(raw)<=frozen['raw_budget_per_result'], 'evidence budget')
        destination.write_bytes(raw)
        print(json.dumps(dict(segment=segment,seconds=evidence['elapsed_seconds'],record_digest=evidence['record_digest'])))
    finally:
        signal.alarm(0);signal.signal(signal.SIGALRM,previous)


def check(root=ROOT):
    root=Path(root)
    m=json.loads((root/INPUTS).read_text())
    require(m==seal(m) and m['cases']==list(CASES) and m['caps']==CAPS, 'manifest scope')
    for name,digest in m['source_bindings'].items():
        require(sha(safe(root,name).read_bytes())==digest, 'execution source drift: '+name)
    records={}
    for segment in CAPS:
        r=json.loads((root/result_path(segment)).read_text())
        require(r==seal(r) and r['manifest_digest']==m['record_digest'] and r['segment']==segment
            and r['family']=='C_OS' and r['outcome']=='passed'
            and 0<=r['elapsed_seconds']<=CAPS[segment], 'execution identity/outcome')
        require(not r['user_accepted'] and not r['aggregate_closed'] and not r['G3_accepted']
            and r['new_G2_support']==[] and not r['public_specialization_facade'], 'scope widening')
        records[segment]=r
    small=records['small']['observations']; big=records['large']['observations']
    require(small['tests']==len(CASES) and set(small['cases'])==set(CASES)
        and all(v['passed'] is True for v in small['cases'].values()), 'case coverage')
    cases=small['cases']
    require([(r['fixture_id'],r['code']) for r in cases['frozen_request_failures']['failures']]==[
        ('G9-FAIL-MISSING-CHIRALITY','module_chirality_required'),
        ('G9-FAIL-MISSING-ACTIVE-PHASE','module_growth_phase_required'),
        ('G9-FAIL-NONCANONICAL-INACTIVE-PHASE','reject_noncanonical_inactive_growth_phase')],
        'frozen failure coverage')
    require(cases['self_loop']['fixture_id']=='G9-FAIL-SOURCE-SELF-LOOP'
        and cases['self_loop']['code']=='source_self_loop_unsupported', 'loop coverage')
    split=cases['reset_only_split']
    require(split['fixture_id']=='G9-FAIL-TARGET-READMISSION'
        and split['code']=='target_readmission_failure' and split['stage']=='target_readmission'
        and split['natural_OS_split_failure'] and split['current_control_passes']
        and split['bounded_outcome']=='CertificationInconclusive' and split['bounded_publication_unchanged']
        and split['exact_policy']=='legacy_exact_v1' and split['bounded_policy']==m['numerical_policy'],
        'mathematical rejection versus inconclusive certificate')
    failures=cases['publication_failures']['failures']
    require(len(failures)==3 and [r.get('role') for r in failures[:2]]==['current','reset']
        and failures[-1]['stage']=='commit' and failures[-1]['location']=='after_prospective_publication'
        and cases['publication_failures']['both_source_and_target_admitted'], 'late failure coverage')
    for row in [*cases['frozen_request_failures']['failures'],cases['self_loop'],split,*failures]:
        require(row['whole_publication_unchanged'] and row['failure_receipt_not_persisted'], 'rollback coverage')
    replay=cases['event_replay']
    require(replay['checkpoint_exact'] and replay['receipt_count']==4
        and set(replay['rejected_mutations'])=={'current','reset','receipt','chirality','model_identity','lifecycle_identity'}
        and replay['occupied_ports']==2*replay['edges'], 'replay coverage')
    require(cases['incomplete_reference']['content_and_params_reidentified'], 'reference coverage')
    continuation=cases['continuation_reset']
    require(continuation['native_steps']==continuation['native_resets']==1
        and continuation['fresh_generic_ledger'] and continuation['reset_baseline_preserved']
        and continuation['clock_preserved_on_reset'] and continuation['event_checkpoint_unchanged']
        and not continuation['public_specialization_facade']
        and continuation['event_checkpoint_sha256']==replay['checkpoint_sha256'], 'internal continuation link')
    require(cases['reset_rollback']['whole_publication_unchanged']
        and cases['reset_rollback']['event_checkpoint_unchanged'], 'reset rollback coverage')
    require(big['checkpoint_exact'] and big['receipt_count']==4 and
            (big['vertices'],big['edges'],big['occupied_ports'])==(107,407,814)
            and big['fresh_native_events']==1 and big['fresh_ordinary_steps']==0, 'large scope')
    event=json.loads(lzma.decompress((root/EVENT).read_bytes()))
    cp=event['execution']['checkpoint']
    require(big['checkpoint_sha256']==sha(canonical_json_bytes(cp)) and
            big['event_id']==event['execution']['event_id'] and
            big['event_record_digest']==event['record_digest'] and
            big['lifecycle_digest']==cp['lifecycle_digest'], 'large checkpoint binding')
    require(len(big['readmissions'])==3 and big['readmissions'][0]==big['readmissions'][1]
            and all(x['roles']==['current','reset'] for x in big['readmissions'])
            and big['readmissions'][2]['scientific_digest']==cp['state']['scientific_digest'],
            'large admission coverage')
    return m,records


def status(root=ROOT):
    m,records=check(root)
    paths=set(m['source_bindings'])|{INPUTS,REVIEW,*[result_path(s) for s in CAPS]}
    return dict(schema='phase9_tranche8_lifecycle_v1', checkpoint='8.5', family='C_OS',
        status='verified_pending_acceptance', user_accepted=False, aggregate_closed=False,
        public_specialization_facade=False, native_trajectories_rerun=False,
        retained_integrity_only=True, manifest_digest=m['record_digest'], executions=records,
        source_refs=[dict(path=p,sha256=sha(safe(root,p).read_bytes()),revision=None) for p in sorted(paths)])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('prepare','run-small','run-large','check','status'))
    action=parser.parse_args().action
    if action=='prepare':
        require(not (ROOT/INPUTS).exists(), 'manifest already exists')
        (ROOT/INPUTS).write_text(json.dumps(manifest(),indent=2)+'\n')
    elif action.startswith('run-'):run(action[4:])
    elif action=='check':check();print('P985_COS_RETAINED_PASS (no numerical rerun)')
    else:print(json.dumps(status(),indent=2))


if __name__=='__main__':
    # Tests import this module; retain a single observations dictionary.
    import sys
    sys.modules['p985_cos']=sys.modules[__name__]
    main()
