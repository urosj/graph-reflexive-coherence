"""Stable ID allocation and tombstoned slot storage primitives."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import Generic, TypeVar, cast


T = TypeVar("T")


class TombstoneMarker:
    """Sentinel for deleted records kept in internally addressable slots."""

    __slots__ = ()

    def __copy__(self) -> "TombstoneMarker":
        return self

    def __deepcopy__(self, memo: object) -> "TombstoneMarker":
        return self

    def __repr__(self) -> str:
        return "TOMBSTONE"


TOMBSTONE = TombstoneMarker()


class MonotoneIdSource:
    """Allocate stable non-negative integer IDs without reuse."""

    def __init__(self, *, next_id: int = 0) -> None:
        if next_id < 0:
            raise ValueError("next_id must be non-negative")
        self._next_id = next_id

    @property
    def next_id(self) -> int:
        """Return the next fresh ID that will be allocated."""

        return self._next_id

    def allocate(self) -> int:
        """Allocate and return one fresh stable ID."""

        allocated_id = self._next_id
        self._next_id += 1
        return allocated_id

    def restore(self, *, next_id: int) -> None:
        """Advance the source to a restored counter value.

        The counter may only move forward; moving backward would re-enable ID
        reuse and violate the Phase 0 determinism policy.
        """

        if next_id < self._next_id:
            raise ValueError("restored next_id cannot move backward")
        self._next_id = next_id


class TombstoneSlotTable(Generic[T]):
    """Deterministic slot table that preserves deleted IDs as tombstones."""

    def __init__(
        self,
        *,
        slots: Iterable[T | TombstoneMarker] | None = None,
        next_id: int | None = None,
    ) -> None:
        self._slots: list[T | TombstoneMarker] = list(slots or ())
        restored_next_id = len(self._slots) if next_id is None else next_id
        if restored_next_id < len(self._slots):
            raise ValueError("next_id cannot be smaller than the slot count")
        self._id_source = MonotoneIdSource(next_id=restored_next_id)

    @property
    def next_id(self) -> int:
        """Return the next fresh slot ID."""

        return self._id_source.next_id

    def __len__(self) -> int:
        return len(self._slots)

    def allocate(self, value: T) -> int:
        """Allocate one fresh stable ID and store its live value."""

        allocated_id = self._id_source.allocate()
        gap = allocated_id - len(self._slots)
        if gap > 0:
            self._slots.extend([TOMBSTONE] * gap)
        self._slots.append(value)
        return allocated_id

    def has_live(self, record_id: int) -> bool:
        """Return whether one slot currently contains a live value."""

        if record_id < 0 or record_id >= len(self._slots):
            return False
        return self._slots[record_id] is not TOMBSTONE

    def is_tombstoned(self, record_id: int) -> bool:
        """Return whether one slot currently exists only as a tombstone."""

        if record_id < 0 or record_id >= len(self._slots):
            return False
        return self._slots[record_id] is TOMBSTONE

    def get_live(self, record_id: int) -> T:
        """Return one live slot value or raise if the slot is dead or missing."""

        if not self.has_live(record_id):
            raise KeyError(record_id)
        return cast(T, self._slots[record_id])

    def inspect_slot(self, record_id: int) -> T | TombstoneMarker:
        """Return the raw slot contents, including tombstones."""

        if record_id < 0 or record_id >= len(self._slots):
            raise KeyError(record_id)
        return self._slots[record_id]

    def tombstone(self, record_id: int) -> T:
        """Convert one live slot into a tombstone and return the former value."""

        value = self.get_live(record_id)
        self._slots[record_id] = TOMBSTONE
        return value

    def iter_live_ids(self) -> Iterator[int]:
        """Iterate live slot IDs in canonical ascending order."""

        for record_id, value in enumerate(self._slots):
            if value is not TOMBSTONE:
                yield record_id

    def iter_live_items(self) -> Iterator[tuple[int, T]]:
        """Iterate live `(id, value)` pairs in canonical ascending order."""

        for record_id in self.iter_live_ids():
            yield record_id, cast(T, self._slots[record_id])

    def raw_slots(self) -> tuple[T | TombstoneMarker, ...]:
        """Return the internal slot representation for restoration-oriented use."""

        return tuple(self._slots)
