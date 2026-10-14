"""Read-only authentication of evidence predating the A CI residual correction.

No source module or numerical operator is substituted. Only the two explicitly
superseded source identities resolve from the pinned Git commit. Every other
binding must still match current bytes. Never use this to label old executions
as conformance of the corrected runtime.
"""
from contextlib import contextmanager
from functools import lru_cache
import hashlib
import subprocess
from unittest.mock import patch
import p984g_aci_staged as oracle

REVISION='cc7ea94095b3ba16c0db4cdf1300cf90ff9c6874'
CI='src/pygrc/models/grc_v4_ci.py'
SPEC='specs/grc-v4-numerical-policy.md'
_ORACLE_CHECK=oracle.check_retained


@lru_cache(maxsize=2)
def historical_sha(path):
    if path not in (CI,SPEC):raise ValueError('unapproved historical source')
    return hashlib.sha256(subprocess.check_output(['git','show',REVISION+':'+path],cwd=oracle.ROOT)).hexdigest()


def check_staged(value=None):
    value=oracle.read() if value is None else value
    current=oracle.bindings();expected=dict(current,**{CI:historical_sha(CI)})
    oracle.require(value['source_bindings']==expected,'historical staged input drift')
    from tranche8_validation import LOCK
    with LOCK,patch.object(oracle,'bindings',return_value=expected):
        return _ORACLE_CHECK(value)


@contextmanager
def native_sources(module):
    """Validate an old execution's bindings, not execute its old runtime."""
    from tranche8_validation import LOCK
    original=module.bindings
    def bound():
        result=original()
        for path in (CI,SPEC):
            oracle.require(path in result,'historical native roster drift')
            result[path]=historical_sha(path)
        return result
    with LOCK,patch.object(module,'bindings',bound):yield
