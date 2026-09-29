"""Bounded operation-owned matrix preparations; no numerical admission here."""

from collections import OrderedDict
from dataclasses import dataclass
from fractions import Fraction
from typing import TypeAlias

_ExactMatrix: TypeAlias = tuple[tuple[Fraction, ...], ...]
_MatrixKey: TypeAlias = tuple[_ExactMatrix, Fraction]
_MAX_MATRIX_PREPARATIONS = 8


@dataclass(frozen=True, slots=True)
class _MatrixPreparation:
    """Successful exact inverse and condition proof for one coefficient matrix."""

    matrix: _ExactMatrix
    inverse: _ExactMatrix
    conditioning_limit: Fraction
    condition_upper_squared: Fraction


class _MatrixPreparations:
    """Keep at most eight immutable preparations within an existing operation."""

    __slots__ = ("_entries",)

    def __init__(self) -> None:
        self._entries: OrderedDict[_MatrixKey, _MatrixPreparation] = OrderedDict()

    def find(
        self, matrix: _ExactMatrix, conditioning_limit: Fraction
    ) -> _MatrixPreparation | None:
        key = (matrix, conditioning_limit)
        prepared = self._entries.get(key)
        if prepared is not None:
            self._entries.move_to_end(key)
        return prepared

    def remember(self, prepared: _MatrixPreparation) -> None:
        key = (prepared.matrix, prepared.conditioning_limit)
        self._entries[key] = prepared
        self._entries.move_to_end(key)
        if len(self._entries) > _MAX_MATRIX_PREPARATIONS:
            self._entries.popitem(last=False)
