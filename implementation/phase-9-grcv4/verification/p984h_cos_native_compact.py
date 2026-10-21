"""Same bound native segments, compact JSON transport within the raw budget.

The original indented writer would exceed 12 MB for the two-state checkpoint.
This explicitly selected driver changes serialization only. Scientific execution
and validation delegate to the unchanged source-bound native harness. Its own
identity is retained too; no numerical fallback, omitted fields or matrix loss.
"""
import argparse
import json
import lzma
import os
import signal
import sys
import time
import flint
import p984h_cos_native as native

SELF = native.HERE + 'p984h_cos_native_compact.py'


def checkpoint_identity(cp):
    from pygrc.models.grc_v4_step import SuccessfulReceiptEnvelope, CommitPayload
    from pygrc.models.grc_v4_codec import payload_identity
    target=native.state(cp['state']); initial=native.state(cp['initial'])
    native.require(target.to_payload()==cp['state'] and initial.to_payload()==cp['initial'], 'checkpoint state identity')
    receipts=tuple(SuccessfulReceiptEnvelope.from_payload(r) for r in cp['receipts'])
    native.require(target.lifecycle_digest(receipts)==cp['lifecycle_digest'],'checkpoint ledger identity')
    commit=CommitPayload(schema_version='grcv4-commit-payload-v1',operation_id=cp['requests'][0]['operation_id'],
        source_state_digest=initial.scientific_digest,target_state_digest=target.scientific_digest,
        emitted_receipt_ids=tuple(r.receipt_id for r in receipts),
        target_step_index=target.inputs.step_index,target_time=target.inputs.time)
    expected=payload_identity('commit_payload',commit.to_payload())
    native.require(all(r.commit_id==expected for r in receipts),'checkpoint commit identity')


def check(segment):
    r=native.checked(segment)
    native.require(r['execution_driver']==dict(path=SELF,sha256=native.oracle.sha(SELF),serialization='compact_json_xz'),
                   'compact driver binding drift')
    event=r if segment=='event' else native.read('event') if segment in ('current','reset') else None
    if event is not None:checkpoint_identity(event['execution']['checkpoint'])
    return r


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=('run','check'));p.add_argument('segment',choices=tuple(native.CAPS))
    args=p.parse_args()
    with native.oracle.exact_backend(native.oracle.ExactBackend.FLINT), native.oracle.numerical_policy(native.oracle.NumericalPolicy.CERTIFIED_ARB_256):
        if args.action=='check':check(args.segment);print('retained integrity passed; no native rerun');return
        m=native.oracle.old.read(native.INPUTS)
        native.require(m==native.manifest(),'native input drift')
        native.require(not (native.ROOT/native.path(args.segment)).exists(),'refuse overwrite')
        native.require(all(os.environ.get(k)=='1' for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS')),'single thread required')
        started=time.monotonic()
        def progress(stage):print(json.dumps(dict(segment=args.segment,stage=stage,seconds=time.monotonic()-started)),flush=True)
        def expired(*_):raise TimeoutError('explicit native segment cap exceeded')
        signal.signal(signal.SIGALRM,expired);signal.alarm(native.CAPS[args.segment])
        r=dict(schema='p984h-cos-native-segment-v1',segment=args.segment,manifest_digest=m['record_digest'],
               execution_driver=dict(path=SELF,sha256=native.oracle.sha(SELF),serialization='compact_json_xz'),
               runtime=dict(python=sys.version.split()[0],python_flint=flint.__version__,numpy=native.np.__version__,
                            OPENBLAS_NUM_THREADS=1,OMP_NUM_THREADS=1),
               user_accepted=False,aggregate_closed=False,covariance_executed=False)
        try:
            with native.matrix_operation():r.update(execution=native.execute(args.segment,progress),outcome='completed')
        except Exception as error:r.update(outcome='failed',failure=dict(type=type(error).__name__,message=str(error),stage=getattr(error,'stage',None)))
        finally:signal.alarm(0)
        r=native.seal(dict(r,elapsed_seconds=time.monotonic()-started))
        raw=json.dumps(r,separators=(',',':'),allow_nan=False).encode()+b'\n';packed=lzma.compress(raw)
        native.require(len(raw)<=m['raw_budget'] and len(packed)<=m['compressed_budget'],'retention budget')
        with (native.ROOT/native.path(args.segment)).open('xb') as stream:stream.write(packed)
        native.require(r['outcome']=='completed','native segment failed: '+str(r.get('failure')))
        check(args.segment);progress('retained_integrity_passed')


if __name__=='__main__':main()
