"""Explicit worker-local sizing of the existing exact-content schema memo.

No validator is replaced. The production codec still keys successful validation
by complete schema bytes, definition name and canonical payload bytes, detaches
every input, and checks contract assets normally. This context changes retention
only: up to eight entries of four MiB, discarded on exit. It is for single-thread
research workers, not a new production default or numerical policy.
"""
from collections import OrderedDict
from contextlib import contextmanager
from contextvars import ContextVar
from unittest.mock import patch
from pygrc.models import grc_v4_codec as codec

POLICY='exact_content_schema_memo_8x4MiB_v1'
_ACTIVE=ContextVar('p984h_validation_reuse',default=False)


@contextmanager
def validation_reuse():
    if _ACTIVE.get():
        yield
        return
    token=_ACTIVE.set(True)
    try:
        with patch.object(codec,'_VALIDATION_MAX_BYTES',4*1024*1024), \
                patch.object(codec,'_VALIDATION_LIMIT',8), \
                patch.object(codec,'_VALIDATED_PAYLOADS',OrderedDict()):
            yield
    finally:
        _ACTIVE.reset(token)
