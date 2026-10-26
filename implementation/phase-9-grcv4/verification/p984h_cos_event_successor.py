"""Source-bound retry of the unchanged event after exact kernel optimization.

Reuse the original native event procedure, not its stale current-tree manifest.
Only prefix-evidence authentication is adapted; no numerical function is patched.
"""
import argparse
import json
import lzma
import os
import signal
import sys
import time
from unittest.mock import patch

import flint
import p984h_cos_native as native
import p984h_cos_native_compact as compact
import p984h_cos_dyadic_step as prerequisite
import p984h_pre_solve_reuse_sources as history

ROOT, BASE, HERE = native.ROOT, native.BASE, native.HERE
SELF = HERE+'p984h_cos_event_successor.py'
TEST = HERE+'test_p984h_cos_event_successor.py'
PLAN = BASE+'P9-8.4h-COSEventSuccessor.md'
INPUTS = BASE+'P9-8.4h-COSEventSuccessorInputs.json'
RESULTS = BASE+'P9-8.4h-COSEventSuccessor.json.xz'
CAP = 1200
require, seal, digest = native.require, native.seal, native.digest


def manifest():
    old = native.oracle.old.read(native.INPUTS)
    step = json.loads(lzma.decompress((ROOT/prerequisite.OUTPUT).read_bytes()))
    require(step == seal(step) and step['whole_step_parity'], 'changing-step prerequisite')
    for name, sha in step['source_bindings'].items():
        require(native.oracle.sha(name) == sha, 'prerequisite source drift: '+name)
    paths = {SELF, TEST, PLAN, native.SELF, compact.SELF, native.INPUTS,
             native.path('prefix'), prerequisite.SELF,
             prerequisite.OUTPUT, HERE+'p984h_pre_solve_reuse_sources.py',
             history.SCALAR_PREDECESSOR, history.SPEC_PREDECESSOR,
             *old['source_bindings'], *step['source_bindings']}
    return seal(dict(schema='p984h-cos-event-successor-inputs-v1',
        source_bindings={name:native.oracle.sha(name) for name in sorted(paths)},
        original_manifest_digest=old['record_digest'],
        prefix_record_digest=native.read('prefix')['record_digest'],
        step_prerequisite_digest=step['record_digest'],
        event_id=native.oracle.read_result()['event_id'],
        cap_seconds=CAP,backend='flint',numerical_policy='certified_arb_256_weighted_v1',
        serialization='compact_json_xz_all_fields',scientific_inputs_unchanged=True,
        scope='one_event_no_target_steps_or_covariance',user_accepted=False))


def authenticated_prefix():
    old = native.oracle.old.read(native.INPUTS)
    require(old == seal(old) and old['caps']['event'] == CAP, 'original manifest/cap')
    for name, sha in old['source_bindings'].items():
        require(history.historical_binding(name, sha, (ROOT/name).read_bytes()), 'historical prefix source: '+name)
    # All original prefix bindings have just been checked against their actual
    # epochs. Reuse its structural/reconstruction checker under that manifest.
    with patch.object(native, 'manifest', return_value=old):
        return native.checked('prefix')


def prefix_only(prefix):
    def checked(segment):
        require(segment == 'prefix', 'only original prefix lookup is adapted')
        return prefix
    return checked


def read():
    return json.loads(lzma.decompress((ROOT/RESULTS).read_bytes()))


def validate(record, m, prefix):
    require(record == seal(record) and record['manifest_digest'] == m['record_digest'], 'successor record identity')
    require(record['schema']=='p984h-cos-event-successor-v1'
            and record['outcome'] in ('completed','failed'), 'unsupported successor schema/outcome')
    require(record['cap_seconds'] == CAP and not record['user_accepted']
            and not record['aggregate_closed'] and not record['covariance_executed'], 'scope widened')
    require(prefix['record_digest'] == m['prefix_record_digest'], 'predecessor linkage')
    if 'retention_revision' in record:
        revision=record['retention_revision']
        require(revision['reason']=='remove_failed_attempt_dependency'
                and revision['numerical_rerun'] is False
                and revision['execution_payload_digest']==digest(record['execution']),
                'retention revision changed numerical execution')
    if record['outcome'] != 'completed':
        require(record['native_events'] == 0 and record['native_steps'] == 0
                and 'execution' not in record and 'failure' in record
                and record['publication_observation']=='unknown_on_failure', 'failed result claims success')
        return record
    execution = record['execution']
    # Original event checker authenticates identities, both-role transfers,
    # precommit admissions, chronology and checkpoint history without reruns.
    old_manifest = native.oracle.old.read(native.INPUTS)
    envelope = seal(dict(schema='p984h-cos-native-segment-v1',segment='event',
        manifest_digest=old_manifest['record_digest'],outcome='completed',
        user_accepted=False,aggregate_closed=False,covariance_executed=False,execution=execution))
    original_check = native.checked
    with patch.object(native,'manifest',return_value=old_manifest), \
         patch.object(native,'read',side_effect=lambda name: envelope if name=='event' else prefix), \
         patch.object(native,'checked',side_effect=prefix_only(prefix)):
        original_check('event')
    compact.checkpoint_identity(execution['checkpoint'])
    require(execution['event_id'] == m['event_id'] and record['native_events'] == 1
            and record['native_steps'] == 0 and record['elapsed_seconds'] <= CAP
            and record['publication_observation']=='committed_and_checked', 'event identity/count')
    return record


def check():
    m=native.oracle.old.read(INPUTS)
    require(m == manifest(), 'successor input/source drift')
    return validate(read(), m, authenticated_prefix())


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('prepare','run','check'))
    args=parser.parse_args()
    with native.oracle.exact_backend(native.oracle.ExactBackend.FLINT), native.oracle.numerical_policy(native.oracle.NumericalPolicy.CERTIFIED_ARB_256):
        if args.action=='prepare':
            native.oracle.old.write_new(INPUTS,manifest());return
        if args.action=='check':
            print(json.dumps(dict(outcome=check()['outcome'],native_numerics_rerun=False)));return
        require(not (ROOT/RESULTS).exists(),'refuse overwrite')
        m=native.oracle.old.read(INPUTS);require(m==manifest(),'successor input/source drift')
        require(all(os.environ.get(k)=='1' for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS')),'single thread')
        started=time.monotonic();progress_rows=[]
        def progress(stage):
            row=dict(stage=stage,seconds=time.monotonic()-started)
            progress_rows.append(row);print(json.dumps(row),flush=True)
        def expired(*_):raise TimeoutError('unchanged 1200-second event cap; no fallback')
        signal.signal(signal.SIGALRM,expired);signal.alarm(CAP)
        record=dict(schema='p984h-cos-event-successor-v1',manifest_digest=m['record_digest'],
            cap_seconds=CAP,
            runtime=dict(python=sys.version.split()[0],python_flint=flint.__version__,threads=1),
            user_accepted=False,aggregate_closed=False,covariance_executed=False,
            native_steps=0,native_events=0)
        try:
            with native.matrix_operation():
                prefix=authenticated_prefix();progress('historical_prefix_authenticated')
                with patch.object(native,'checked',side_effect=prefix_only(prefix)):
                    execution=native.execute('event',progress)
                require(time.monotonic()-started <= CAP, 'event exceeded declared cap')
                record.update(execution=execution,outcome='completed',native_events=1,
                              publication_observation='committed_and_checked')
        except Exception as exc:
            record.update(outcome='failed',failure=dict(type=type(exc).__name__,message=str(exc),
                stage=getattr(exc,'stage',None)),rollback_observed=False)
            record['publication_observation']='unknown_on_failure'
        finally:signal.alarm(0)
        record=seal(dict(record,elapsed_seconds=time.monotonic()-started,progress=progress_rows))
        require(m==manifest(),'source changed during event')
        raw=json.dumps(record,separators=(',',':'),allow_nan=False).encode()+b'\n'
        with (ROOT/RESULTS).open('xb') as stream:stream.write(lzma.compress(raw))
        checked=check()
        print(json.dumps(dict(outcome=checked['outcome'],seconds=checked['elapsed_seconds'],
                             native_events=checked['native_events'])),flush=True)


if __name__=='__main__':main()
