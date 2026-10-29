"""Serialize identical private diagnostic writes across numerical workers.

Only digest-named raw captures are affected. Native roots still execute, failed
or changed captures are never reused, and campaign records remain exclusive.
"""
from contextlib import contextmanager
from contextvars import ContextVar
import fcntl
from pathlib import Path
import re
import unittest
from unittest.mock import patch

import p984d_ccipc as storage

b=storage.b
SELF=b.HERE+'p9_ccipc_raw_store.py'
TEST=b.HERE+'test_p9_ccipc_raw_store.py'
PREFLIGHT=b.BASE+'P9-CCIPC-DiagnosticSavePreflight.json'
FAILURE=b.BASE+'P9-8.4h-CCIPCCharge-step-reset-2-incomplete-1793284331529531984.json.xz'
PRIVATE=b.ROOT/'implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/generated/phase9-verification/ccipc-large-raw'
_ACTIVE=ContextVar('ccipc_private_capture_store',default=None)


@contextmanager
def private_captures(directory=PRIVATE):
    directory=Path(directory).resolve()
    active=_ACTIVE.get()
    if active is not None:
        b.require(active==directory,'private capture scope nesting')
        yield
        return
    original=storage.save
    def save(path,value):
        target=(b.ROOT/path).resolve()
        if target.parent!=directory or not re.fullmatch(r'[0-9a-f]{64}\.json\.xz',target.name):
            return original(path,value)
        b.check_digest(value);b.check_digest(value['read'])
        b.require(value['campaign_credit'] is False
            and value['read']['record_digest']==target.name.removesuffix('.json.xz'),
            'private capture identity/scope')
        # The producer's exists() check and compression happen before its
        # exclusive open; two histories can reach the same reset read together.
        with target.with_suffix(target.suffix+'.lock').open('a+b') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            if target.exists():
                prior=storage.read(target);b.check_digest(prior)
                b.require(b.canonical_json_bytes(prior)==b.canonical_json_bytes(value),
                    'private capture collision changed complete content')
            else:original(path,value)
    token=_ACTIVE.set(directory)
    try:
        with patch.object(storage,'save',save):yield
    finally:_ACTIVE.reset(token)


def checked():
    value=storage.read(PREFLIGHT);b.check_digest(value);b.check_bindings(value['source_bindings'])
    b.require(value['schema']=='p9-ccipc-diagnostic-save-preflight-v1'
        and value['outcome']=='passed' and value['tests']==4
        and value['concurrent_writers']==2 and value['identical_write_idempotent']
        and value['negative_controls']==['changed_capture','corrupt_capture','outside_private_scope']
        and value['native_roots_reused'] is False and value['numerical_behavior_changed'] is False
        and value['failed_attempt_credit'] is False,'diagnostic save preflight scope')
    failure=storage.read(FAILURE);b.check_digest(failure)
    b.require(failure['record_digest']==value['failure_record_digest']
        and failure['outcome']=='incomplete' and failure['campaign_credit'] is False
        and 'FileExistsError' in failure['error']['message'],'diagnostic failure provenance')
    return value


if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromName('test_p9_ccipc_raw_store')
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    b.require(result.wasSuccessful() and result.testsRun==4 and not result.skipped,'diagnostic store regressions')
    failure=storage.read(FAILURE);b.check_digest(failure)
    paths={SELF,TEST,FAILURE,storage.SELF,b.SELF,b.HERE+'p9_ccipc_campaign.py',
        b.HERE+'p9_ccipc_capture.py','src/pygrc/models/grc_v4_codec.py'}
    value=b.seal(dict(schema='p9-ccipc-diagnostic-save-preflight-v1',source_bindings=b.bind(paths),
        outcome='passed',tests=4,concurrent_writers=2,identical_write_idempotent=True,
        negative_controls=['changed_capture','corrupt_capture','outside_private_scope'],
        native_roots_reused=False,numerical_behavior_changed=False,failed_attempt_credit=False,
        failure_record_digest=failure['record_digest']))
    b.write_new(PREFLIGHT,value);checked()
    print('Private diagnostic capture concurrency preflight passed; no native credit inferred')
