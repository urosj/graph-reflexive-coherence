"""Immutable numerical facts in one bounded, operation-owned store."""

from collections import OrderedDict
from dataclasses import dataclass
from fractions import Fraction
from typing import TypeAlias, overload

_ExactMatrix: TypeAlias = tuple[tuple[Fraction, ...], ...]
_MatrixKey: TypeAlias = tuple[_ExactMatrix, Fraction | None]
# Primitive callers also use small descriptor and interval blocks. Keep one
# fixed budget for all facts, independent of graph size and trace length.
_MAX_MATRIX_FACTS = 64


@dataclass(frozen=True, slots=True)
class _InverseFact:
    """Successful exact elimination of the represented coefficient matrix."""

    matrix: _ExactMatrix
    inverse: _ExactMatrix


@dataclass(frozen=True, slots=True)
class _ConditionFact:
    """Successful exact conditioning proof under this particular limit."""

    matrix: _ExactMatrix
    conditioning_limit: Fraction
    condition_upper_squared: Fraction


_MatrixFact: TypeAlias = _InverseFact | _ConditionFact


class _MatrixFacts:
    """Keep at most 64 immutable inverse/conditioning facts in one operation."""

    __slots__ = ("_entries",)

    def __init__(self) -> None:
        self._entries: OrderedDict[_MatrixKey, _MatrixFact] = OrderedDict()

    @overload
    def find(
        self, matrix: _ExactMatrix, conditioning_limit: None = None
    ) -> _InverseFact | None: ...

    @overload
    def find(
        self, matrix: _ExactMatrix, conditioning_limit: Fraction
    ) -> _ConditionFact | None: ...

    def find(
        self, matrix: _ExactMatrix, conditioning_limit: Fraction | None = None
    ) -> _MatrixFact | None:
        key = (matrix, conditioning_limit)
        fact = self._entries.get(key)
        if fact is not None:
            self._entries.move_to_end(key)
        return fact

    def remember(self, fact: _MatrixFact) -> None:
        key = (
            fact.matrix,
            None if isinstance(fact, _InverseFact) else fact.conditioning_limit,
        )
        self._entries[key] = fact
        self._entries.move_to_end(key)
        if len(self._entries) > _MAX_MATRIX_FACTS:
            self._entries.popitem(last=False)
