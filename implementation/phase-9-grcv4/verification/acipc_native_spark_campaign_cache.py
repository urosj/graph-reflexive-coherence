"""Bounded memoization of independent roots, keyed by the complete input ball.

Witness, residual, writer and represented-output checks still run on every read.
Only the independently computed comparison root is reused; cache values are
detached from callers and never supply native physical evolution.
"""

from collections import OrderedDict
from contextlib import contextmanager
from hashlib import sha256
from unittest.mock import patch

import acipc_native_spark_oracle as oracle
from flint import arb_mat, ctx

from pygrc.models.grc_v4_certification import _ARB_CONTEXT_LOCK
from pygrc.models.grc_v4_codec import canonical_json_bytes

_Reference = oracle.Reference
_ROOTS = OrderedDict()
_HITS = 0
_MISSES = 0
LIMIT = 8


def _ball_key(A):
    # Use exact midpoint and radius, not rounded displays or overlapping bounds.
    return (
        A.nrows(),
        A.ncols(),
        tuple((x.mid().fmpq(), x.rad().fmpq()) for x in A.entries()),
    )


def _copy(value):
    return {
        k: _copy(v) if isinstance(v, dict) else arb_mat(v) for k, v in value.items()
    }


def clear():
    global _HITS, _MISSES
    with _ARB_CONTEXT_LOCK:
        _ROOTS.clear()
        _HITS = _MISSES = 0


def info():
    with _ARB_CONTEXT_LOCK:
        return {
            "hits": _HITS,
            "misses": _MISSES,
            "entries": len(_ROOTS),
            "limit": LIMIT,
        }


class CachedReference(_Reference):
    def __init__(self, graph):
        super().__init__(graph)
        self._cache_graph = sha256(canonical_json_bytes(graph)).hexdigest()

    def selected(self, C, W, Z):
        global _HITS, _MISSES
        key = (
            "acipc-independent-root-v1",
            self._cache_graph,
            ctx.prec,
            _ball_key(C),
            _ball_key(W),
            _ball_key(Z),
        )
        with _ARB_CONTEXT_LOCK:
            if key in _ROOTS:
                _HITS += 1
                _ROOTS.move_to_end(key)
                return _copy(_ROOTS[key])
            _MISSES += 1
            result = super().selected(C, W, Z)
            _ROOTS[key] = _copy(result)
            if len(_ROOTS) > LIMIT:
                _ROOTS.popitem(last=False)
            return result


@contextmanager
def cached_oracle():
    with _ARB_CONTEXT_LOCK, patch.object(oracle, "Reference", CachedReference):
        yield
