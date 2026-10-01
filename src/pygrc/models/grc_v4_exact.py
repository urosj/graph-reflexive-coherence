"""Operation-bound exact rational backend for V4 numerical work.

The default is the historical Python Fraction implementation. An explicit
scope selects FLINT before declaration; an owner retains that selection for
later operations. Values within a scope use one native scalar representation.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from decimal import Decimal
from enum import Enum
from fractions import Fraction
from functools import lru_cache
from importlib import import_module
from types import ModuleType
from typing import Any, TypeAlias

# python-flint is optional and imported only inside an explicitly selected scope.
# The representation is selected at runtime; arithmetic users must not assume
# that the exact scalar is specifically a Python Fraction. All V4 numerical
# modules construct values here; a source test enforces this boundary.
# This is a role annotation, not a strong nominal or static type guarantee;
# see implementation/corrections/GRCV4-ExactCPUBackend.md.
ExactScalar: TypeAlias = Any


class ExactBackend(Enum):
    PYTHON = "python"
    FLINT = "flint"


_ACTIVE_BACKEND: ContextVar[ExactBackend] = ContextVar(
    "grcv4_exact_backend", default=ExactBackend.PYTHON
)


@lru_cache(maxsize=1)
def _flint_module() -> ModuleType:
    return import_module("flint")


def current_exact_backend() -> ExactBackend:
    return _ACTIVE_BACKEND.get()


@contextmanager
def exact_backend(backend: ExactBackend) -> Iterator[None]:
    """Select exact arithmetic before constructing a V4 declaration and owner.

    The owner captures this choice, so steps remain on the same backend after
    the caller exits this scope. Nested scopes restore the previous choice.
    """
    if type(backend) is not ExactBackend:
        raise TypeError("expected an ExactBackend")
    if backend is ExactBackend.FLINT:
        try:
            _flint_module()
        except ImportError as exc:
            raise RuntimeError("FLINT exact backend requires python-flint") from exc
    token = _ACTIVE_BACKEND.set(backend)
    try:
        yield
    finally:
        _ACTIVE_BACKEND.reset(token)


def _ratio(value: object) -> tuple[int, int]:
    if isinstance(value, Fraction):
        return value.numerator, value.denominator
    if isinstance(value, (int, float, Decimal)):
        return value.as_integer_ratio()
    if isinstance(value, str):
        parsed = Fraction(value)
        return parsed.numerator, parsed.denominator
    if _ACTIVE_BACKEND.get() is ExactBackend.FLINT:
        flint = _flint_module()
        if isinstance(value, flint.fmpz):
            return int(value), 1
    numerator = getattr(value, "numerator", None)
    denominator = getattr(value, "denominator", None)
    if numerator is not None and denominator is not None:
        return int(numerator), int(denominator)
    raise TypeError(f"unsupported exact rational source: {type(value).__name__}")


def exact_number(numerator: Any = 0, denominator: Any = None) -> ExactScalar:
    """Construct the active backend's exact value with Fraction semantics."""
    if _ACTIVE_BACKEND.get() is ExactBackend.PYTHON:
        return Fraction(numerator) if denominator is None else Fraction(numerator, denominator)
    flint = _flint_module()
    if denominator is None and isinstance(numerator, flint.fmpq):
        return numerator
    n, d = _ratio(numerator)
    if denominator is not None:
        other_n, other_d = _ratio(denominator)
        n, d = n * other_d, d * other_n
    return flint.fmpq(n, d)


def is_exact(value: object) -> bool:
    """Recognize the active backend's rational scalar, not arbitrary numerics."""
    if _ACTIVE_BACKEND.get() is ExactBackend.PYTHON:
        return isinstance(value, Fraction)
    return isinstance(value, _flint_module().fmpq)


def integer_ratio(value: object) -> tuple[int, int]:
    """Extract plain integers for exact validators and external conversion."""
    return _ratio(value)
