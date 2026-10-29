"""Mandatory, bounded compute policy for single-thread C_PC research workers.

These scopes retain successful facts by exact operands. They do not change a
solver, a tolerance, an admission decision, or the public server's cache policy.
"""
from contextlib import contextmanager
from importlib.metadata import version
import os

from p984h_validation_reuse import POLICY, validation_reuse
from pygrc.models import grc_v4_codec as codec
from pygrc.models.grc_v4_exact import ExactBackend, current_exact_backend, exact_backend, exact_number
from pygrc.models.grc_v4_numerics import (
    MatrixReuse, NumericalPolicy, current_numerical_policy, matrix_operation, numerical_policy,
)


def verify_active():
    if any(os.environ.get(k) != "1" for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS")):
        raise ValueError("C_PC workers require single-thread BLAS/OpenMP")
    if current_exact_backend() is not ExactBackend.FLINT or not type(exact_number(1)).__module__.startswith("flint"):
        raise ValueError("FLINT exact arithmetic is not active")
    if current_numerical_policy() is not NumericalPolicy.CERTIFIED_ARB_256:
        raise ValueError("certified Arb 256-bit arithmetic is not active")
    context = codec._OPERATION_CONTEXT.get()
    if context is None or context.matrix_facts is None:
        raise ValueError("operation-scoped matrix reuse is not active")
    if (codec._VALIDATION_LIMIT, codec._VALIDATION_MAX_BYTES) != (8, 4 * 1024 * 1024):
        raise ValueError("bounded exact-content schema memo is not active")
    return dict(exact_backend="flint", python_flint=version("python-flint"),
                numerical_policy="certified_arb_256", matrix_reuse="automatic_exact_operands",
                schema_memo=POLICY, blas_threads=1, tolerances_relaxed=False)


@contextmanager
def worker():
    with validation_reuse(), exact_backend(ExactBackend.FLINT), \
            numerical_policy(NumericalPolicy.CERTIFIED_ARB_256), \
            matrix_operation(reuse=MatrixReuse.AUTOMATIC):
        yield verify_active()
