"""One closed source equivalence for Tranche 8's unused legacy-return helper.

The sole production delta initializes CI+PC's required carrier on legacy
return. These numerical campaigns never enter that branch. Exact Git/source
bytes and a failing call trap enforce this boundary; no numerical producer,
oracle, tolerance, or completed execution is changed or relabelled.
"""
from contextlib import contextmanager
import json
import subprocess
from unittest.mock import patch

import p984b_runtime as b

SELF=b.HERE+'p9_ccipc_execution_epoch.py'
PATH=b.BASE+'P9-CCIPC-ExecutionSourceEpoch.json'
SOURCE='src/pygrc/models/grc_9_v4_crossing.py'
BASE='b41f1f26'
OLD='    if profile.identity_payload.realization == "PC":\n'
NEW='    if profile.identity_payload.realization in ("PC", "CI+PC"):\n'


def manifest():
    old=subprocess.check_output(['git','show',BASE+':'+SOURCE],cwd=b.ROOT)
    current=(b.ROOT/SOURCE).read_bytes()
    b.require(old.count(OLD.encode())==1 and current==old.replace(OLD.encode(),NEW.encode()),
              'execution epoch permits exactly the declared legacy-return carrier fix')
    return b.seal(dict(schema='p9-ccipc-execution-source-epoch-v1',base_commit=BASE,
        source=SOURCE,before_sha256=b.sha(old),after_sha256=b.sha(current),
        checker_sha256=b.sha((b.ROOT/SELF).read_bytes()),
        excluded_function='grc_9_v4_crossing._return_role',excluded_function_trap=True,
        numerical_producer_changed=False,old_execution_relabelled=False))


def checked():
    value=json.loads((b.ROOT/PATH).read_bytes())
    b.require(value==manifest(),'execution source equivalence drift')
    return value


@contextmanager
def numerical_campaign():
    import p984d_ccipc as storage
    import p984h_ccipc as large
    from pygrc.models import grc_9_v4_crossing as crossing
    epoch=checked();bind,check,save=b.bind,b.check_bindings,storage.save
    def old_binding(paths):
        rows=bind(paths)
        return [dict(row,sha256=epoch['before_sha256']) if row['path']==SOURCE else row for row in rows]
    def verify(rows):
        projected=[]
        for row in rows:
            if row['path']==SOURCE and row['sha256']==epoch['before_sha256']:
                row=dict(row,sha256=epoch['after_sha256'])
            projected.append(row)
        check(projected)
    def retained(path,value):
        if value.get('schema') in ('p984d-ccipc-results-v1','p984h-ccipc-segment-v1',
                'p984h-ccipc-covariance-segment-v1','p985-ccipc-execution-v1'):
            value=b.seal(dict(value,source_equivalence=dict(path=PATH,record_digest=epoch['record_digest'])))
        return save(path,value)
    with patch.object(b,'bind',old_binding),patch.object(b,'check_bindings',verify), \
         patch.object(large,'check_bindings',verify),patch.object(storage,'save',retained), \
         patch.object(crossing,'_return_role',side_effect=AssertionError('legacy return outside Tranche 8 numerical campaign')):
        yield epoch


if __name__=='__main__':
    b.write_new(PATH,manifest())
