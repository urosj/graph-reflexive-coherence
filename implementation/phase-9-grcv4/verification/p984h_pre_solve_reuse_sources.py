"""Read-only binding adapter for evidence preceding certified-solve reuse.

Only the named files resolve from the pre-change Git subject. Numerical
functions and runtime modules are never replaced. This is historical evidence
authentication, not conformance of current code or permission to execute it.
"""
from contextlib import contextmanager, ExitStack
from functools import lru_cache, wraps
import hashlib
import importlib
import lzma
import subprocess
from unittest.mock import patch

REVISION='718f95be'
PATHS=('src/pygrc/models/grc_v4_linear.py','src/pygrc/models/grc_v4_numerics.py',
       'src/pygrc/models/grc_v4_exact.py','src/pygrc/models/_grc_v4_matrix.py',
       'src/pygrc/models/grc_v4_certification.py',
       'specs/grc-v4-numerical-policy.md')
MODULES=('p984g_cos_native','p984g_cci_staged','p984g_cci_native',
    'p984g_cci_native_admission','p984g_cci_closure','p984g_aci_staged',
    'p984g_aci_native','p984g_aci_native_successor','p984g_apc_investigation',
    'p984g_apc_staged','p984g_apc_feasibility','p984g_apc_hardening',
    'p984g_apc_native','p984g_apc_native_targets')

# An uncommitted, measured predecessor cannot be recovered from a Git commit.
# Preserve its exact source bytes as evidence, never import/execute this archive.
SCALAR_PREDECESSOR = 'implementation/phase-9-grcv4/tranche-8/kernel-predecessors/grc_v4_certification-scalar-reuse.py.xz'
SCALAR_PREDECESSOR_ARCHIVE_SHA = '6dc00b344ddbbfd15bf404b1597de8797d418770d3acaef22b3dd509fef52905'
SCALAR_PREDECESSOR_SOURCE_SHA = 'e14c1809e36ce6adad73f9a002c7a2c8701c13a2d46926ee39407fa9b22c9a46'
SPEC_PREDECESSOR = 'implementation/phase-9-grcv4/tranche-8/kernel-predecessors/grc-v4-numerical-policy-scalar-reuse.md.xz'
SPEC_PREDECESSOR_ARCHIVE_SHA = '718b3ee30829f56dbb3d00c5c97887b64095071c1eb4186989982c1c6a388618'
SPEC_PREDECESSOR_SOURCE_SHA = '1c53927b7fb4687dd2bf865f488926f8d64cd1d3c382e1abf519178521511c98'


@lru_cache(maxsize=6)
def historical_sha(path):
    from tranche8_validation import ROOT
    if path not in PATHS:raise ValueError('unapproved historical source')
    return hashlib.sha256(subprocess.check_output(['git','show',REVISION+':'+path],cwd=ROOT)).hexdigest()


def historical_binding(path,expected,current):
    """Named epoch only; unrelated source drift is never waived."""
    snapshots = {
        ('src/pygrc/models/grc_v4_certification.py', SCALAR_PREDECESSOR_SOURCE_SHA):
            (SCALAR_PREDECESSOR, SCALAR_PREDECESSOR_ARCHIVE_SHA),
        ('specs/grc-v4-numerical-policy.md', SPEC_PREDECESSOR_SOURCE_SHA):
            (SPEC_PREDECESSOR, SPEC_PREDECESSOR_ARCHIVE_SHA),
    }
    if (path, expected) in snapshots:
        from tranche8_validation import ROOT
        snapshot, archive_sha = snapshots[path, expected]
        raw = (ROOT / snapshot).read_bytes()
        return (hashlib.sha256(raw).hexdigest() == archive_sha
                and hashlib.sha256(lzma.decompress(raw)).hexdigest() == expected)
    return (expected == hashlib.sha256(current).hexdigest()
            or (path in PATHS and expected == historical_sha(path)))


@contextmanager
def historical_sources():
    from tranche8_validation import LOCK
    def adapt(original):
        @wraps(original)
        def bindings():
            value=original()
            for path in PATHS:
                if path in value:value[path]=historical_sha(path)
            return value
        return bindings
    with LOCK,ExitStack() as stack:
        for name in MODULES:
            module=importlib.import_module(name)
            stack.enter_context(patch.object(module,'bindings',adapt(module.bindings)))
        yield


def historical_view(function):
    @wraps(function)
    def call(*args,**kwargs):
        with historical_sources():return function(*args,**kwargs)
    return call
