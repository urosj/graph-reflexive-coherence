"""Immutable numerical facts and bounded continuation between owned steps."""

from collections import OrderedDict
from dataclasses import dataclass
from enum import Enum
from typing import TypeAlias, overload

from .grc_v4_exact import ExactBackend, ExactScalar, current_exact_backend
from .grc_v4_certification import NumericalPolicy, current_numerical_policy

_ExactMatrix: TypeAlias = tuple[tuple[ExactScalar, ...], ...]
_MatrixKey: TypeAlias = tuple[_ExactMatrix, ExactScalar | None]
# Primitive callers also use small descriptor and interval blocks. Keep one
# fixed budget for all facts, independent of graph size and trace length.
_MAX_MATRIX_FACTS = 64
# Certified solutions are distinct from exact inverse facts, never continued
# between operations. Bound both count and scalar references (keys + values).
_MAX_ROUNDED_SOLVES = 16
_MAX_ROUNDED_SOLVE_CELLS = 8_000_000


@dataclass(frozen=True, slots=True)
class _RoundedSolveKey:
    matrix: _ExactMatrix
    rhs: _ExactMatrix

    def __hash__(self) -> int:
        # Deliberate dimension buckets: dense FLINT rational hashing costs more
        # than bounded equality scans. Dataclass equality still compares EVERY
        # exact coefficient and RHS; this hash is never proof of a cache hit.
        return hash((len(self.matrix), len(self.matrix[0]) if self.matrix else 0,
                     len(self.rhs), len(self.rhs[0]) if self.rhs else 0))


class MatrixReuse(Enum):
    """Fact calculation policy, independent of scientific solver admission."""

    AUTOMATIC = "automatic"
    FRESH = "fresh"


@dataclass(frozen=True, slots=True)
class _InverseFact:
    """Successful exact elimination of the represented coefficient matrix."""

    matrix: _ExactMatrix
    inverse: _ExactMatrix


@dataclass(frozen=True, slots=True)
class _ConditionFact:
    """Successful exact conditioning proof under this particular limit."""

    matrix: _ExactMatrix
    conditioning_limit: ExactScalar
    condition_upper_squared: ExactScalar


@dataclass(frozen=True, slots=True)
class _RoundedSolveFact:
    """Certified RN(A^-1 B), not an exact inverse or admission decision."""

    matrix: _ExactMatrix
    rhs: _ExactMatrix
    result: tuple[tuple[float, ...], ...]

    @property
    def cells(self) -> int:
        return sum(len(row) for rows in (self.matrix, self.rhs, self.result) for row in rows)


_MatrixFact: TypeAlias = _InverseFact | _ConditionFact


@dataclass(frozen=True, slots=True)
class _MatrixContinuation:
    """At most four facts for the reset and latest committed matrices.

    This is private computation data, never serialized state or admission.
    The cardinality bound does not bound the size of each coefficient matrix.
    """

    facts: tuple[_MatrixFact, ...] = ()
    backend: ExactBackend = ExactBackend.PYTHON
    numerical_policy: NumericalPolicy = NumericalPolicy.LEGACY_EXACT

    def __post_init__(self) -> None:
        if type(self.backend) is not ExactBackend:
            raise TypeError("matrix continuation requires an exact backend")
        if type(self.numerical_policy) is not NumericalPolicy:
            raise TypeError("matrix continuation requires a numerical policy")
        if type(self.facts) is not tuple or len(self.facts) > 4:
            raise ValueError("matrix continuation must hold at most four facts")
        if any(type(fact) not in (_InverseFact, _ConditionFact) for fact in self.facts):
            raise TypeError("matrix continuation requires immutable numerical facts")
        if len({fact.matrix for fact in self.facts}) > 2:
            raise ValueError("matrix continuation must cover at most two matrices")


class _MatrixFacts:
    """Keep at most 64 immutable inverse/conditioning facts in one operation."""

    __slots__ = ("_entries", "_reuse", "_backend", "_numerical_policy",
                 "_solves", "_solve_cells")

    def __init__(self, *, reuse: MatrixReuse = MatrixReuse.AUTOMATIC) -> None:
        if type(reuse) is not MatrixReuse:
            raise TypeError("expected a MatrixReuse policy")
        self._reuse = reuse
        self._backend = current_exact_backend()
        self._numerical_policy = current_numerical_policy()
        self._entries: OrderedDict[_MatrixKey, _MatrixFact] = OrderedDict()
        self._solves: OrderedDict[_RoundedSolveKey, _RoundedSolveFact] = OrderedDict()
        self._solve_cells = 0

    def _check_execution(self) -> None:
        if self._backend is not current_exact_backend():
            raise TypeError("matrix facts belong to another exact backend")
        if self._numerical_policy is not current_numerical_policy():
            raise TypeError("matrix facts belong to another numerical policy")

    def find_solve(self, matrix: _ExactMatrix, rhs: _ExactMatrix) -> _RoundedSolveFact | None:
        self._check_execution()
        if self._reuse is MatrixReuse.FRESH:
            return None
        key = _RoundedSolveKey(matrix, rhs)
        fact = self._solves.get(key)
        if fact is not None:
            self._solves.move_to_end(key)
        return fact

    def remember_solve(self, fact: _RoundedSolveFact) -> None:
        self._check_execution()
        if self._reuse is MatrixReuse.FRESH or fact.cells > _MAX_ROUNDED_SOLVE_CELLS:
            return
        key = _RoundedSolveKey(fact.matrix, fact.rhs)
        previous = self._solves.pop(key, None)
        if previous is not None:
            self._solve_cells -= previous.cells
        self._solves[key] = fact
        self._solve_cells += fact.cells
        while len(self._solves) > _MAX_ROUNDED_SOLVES or self._solve_cells > _MAX_ROUNDED_SOLVE_CELLS:
            _, evicted = self._solves.popitem(last=False)
            self._solve_cells -= evicted.cells

    @property
    def reuse(self) -> MatrixReuse:
        return self._reuse

    @overload
    def find(
        self, matrix: _ExactMatrix, conditioning_limit: None = None
    ) -> _InverseFact | None: ...

    @overload
    def find(
        self, matrix: _ExactMatrix, conditioning_limit: ExactScalar
    ) -> _ConditionFact | None: ...

    def find(
        self, matrix: _ExactMatrix, conditioning_limit: ExactScalar | None = None
    ) -> _MatrixFact | None:
        if self._numerical_policy is not current_numerical_policy():
            raise TypeError("matrix facts belong to another numerical policy")
        if self._reuse is MatrixReuse.FRESH:
            return None
        key = (matrix, conditioning_limit)
        fact = self._entries.get(key)
        if fact is not None:
            self._entries.move_to_end(key)
        return fact

    def remember(self, fact: _MatrixFact) -> None:
        if self._reuse is MatrixReuse.FRESH:
            return
        key = (
            fact.matrix,
            None if isinstance(fact, _InverseFact) else fact.conditioning_limit,
        )
        self._entries[key] = fact
        self._entries.move_to_end(key)
        if len(self._entries) > _MAX_MATRIX_FACTS:
            self._entries.popitem(last=False)

    def seed(self, continuation: _MatrixContinuation) -> None:
        """Copy immutable committed facts into this operation's private store."""
        if continuation.facts and continuation.backend is not self._backend:
            raise TypeError("matrix continuation belongs to another exact backend")
        if continuation.facts and continuation.numerical_policy is not self._numerical_policy:
            raise TypeError("matrix continuation belongs to another numerical policy")
        for fact in continuation.facts:
            self.remember(fact)

    def retain(
        self,
        reset: _ExactMatrix,
        current: _ExactMatrix,
        conditioning_limit: ExactScalar,
    ) -> _MatrixContinuation:
        """Keep only available facts for the two named committed matrices.

        Missing or evicted facts stay missing; selecting a continuation performs
        no numerical calculation and does not mutate the operation's LRU.
        """
        facts = tuple(
            fact
            for matrix in dict.fromkeys((reset, current))
            for limit in (None, conditioning_limit)
            if (fact := self._entries.get((matrix, limit))) is not None
        )
        return _MatrixContinuation(facts, self._backend, self._numerical_policy)
