"""Authenticate pre-CI-interval evidence without rebinding it to new runtime.

This context is for retained/independent research checking only, never execution.
Only the two explicitly superseded files resolve from Git; every other input
continues to be checked against local bytes. Missing Git history fails closed.
"""
from contextlib import contextmanager
import hashlib
import subprocess
from unittest.mock import patch

REVISION = 'e1d61021'
CI = 'src/pygrc/models/grc_v4_ci.py'
SPEC = 'specs/grc-v4-numerical-policy.md'
ADDED = 'src/pygrc/models/grc_v4_interval.py'


@contextmanager
def historical_sources():
    import p984g_cci_investigation as research
    import p984g_cci_staged as staged
    import p984g_cos_native as native
    from tranche8_validation import LOCK
    original_calculate, original_bindings = research.calculate, staged.bindings
    native_bindings = native.bindings
    old = {p: hashlib.sha256(subprocess.check_output(
        ['git', 'show', REVISION+':'+p], cwd=research.ROOT)).hexdigest() for p in (CI,SPEC)}
    research.require(research.read(research.RESULTS)['source_bindings'][CI]==old[CI],
                     'historical CI source mismatch')
    pinned = native.read(native.INPUTS)['source_bindings']
    research.require(all(pinned[p]==old[p] for p in old), 'historical native source mismatch')

    def calculate():
        value=original_calculate()
        value['source_bindings'][CI]=old[CI]
        return research.seal(value)

    def staged_bindings():
        value=original_bindings();value[CI]=old[CI]
        return value

    def cos_bindings():
        value=native_bindings()
        research.require(set(value)==set(pinned)|{ADDED}, 'unexpected runtime roster change')
        value.pop(ADDED)
        value.update(old)
        research.require(value==pinned, 'unrelated historical input drift')
        return value

    with LOCK, patch.object(research,'calculate',calculate), \
            patch.object(staged,'bindings',staged_bindings), \
            patch.object(native,'bindings',cos_bindings):
        yield
