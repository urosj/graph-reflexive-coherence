"""Tests for monotone ID allocation and tombstoned slot storage."""

from __future__ import annotations

import unittest

from pygrc.core import TOMBSTONE, MonotoneIdSource, TombstoneSlotTable


class IdSourceAndTombstoneTableTest(unittest.TestCase):
    """Validate the Phase 2 shared ID/tombstone primitives."""

    def test_monotone_id_source_rejects_negative_start(self) -> None:
        with self.assertRaises(ValueError):
            MonotoneIdSource(next_id=-1)

    def test_monotone_id_source_allocates_non_reused_ids(self) -> None:
        source = MonotoneIdSource()

        self.assertEqual(0, source.allocate())
        self.assertEqual(1, source.allocate())
        self.assertEqual(2, source.next_id)

    def test_monotone_id_source_rejects_backward_restore(self) -> None:
        source = MonotoneIdSource(next_id=3)

        with self.assertRaises(ValueError):
            source.restore(next_id=2)

    def test_monotone_id_source_allows_forward_restore(self) -> None:
        source = MonotoneIdSource(next_id=1)

        source.restore(next_id=4)

        self.assertEqual(4, source.allocate())
        self.assertEqual(5, source.next_id)

    def test_tombstone_slot_table_skips_deleted_ids_in_live_iteration(self) -> None:
        table = TombstoneSlotTable[str]()

        first_id = table.allocate("a")
        second_id = table.allocate("b")
        removed = table.tombstone(first_id)

        self.assertEqual("a", removed)
        self.assertEqual((second_id,), tuple(table.iter_live_ids()))
        self.assertFalse(table.has_live(first_id))
        self.assertTrue(table.is_tombstoned(first_id))
        self.assertIs(TOMBSTONE, table.inspect_slot(first_id))

    def test_tombstone_slot_table_preserves_next_id_after_restore_gap(self) -> None:
        table = TombstoneSlotTable[str](slots=("node-0", TOMBSTONE), next_id=4)

        allocated_id = table.allocate("node-4")

        self.assertEqual(4, allocated_id)
        self.assertEqual(5, table.next_id)
        self.assertEqual(
            ("node-0", TOMBSTONE, TOMBSTONE, TOMBSTONE, "node-4"),
            table.raw_slots(),
        )

    def test_tombstone_slot_table_get_live_rejects_dead_or_missing_slots(self) -> None:
        table = TombstoneSlotTable[str]()
        record_id = table.allocate("value")
        table.tombstone(record_id)

        with self.assertRaises(KeyError):
            table.get_live(record_id)

        with self.assertRaises(KeyError):
            table.inspect_slot(99)

    def test_tombstone_slot_table_iter_live_items_and_raw_slots_are_stable(self) -> None:
        table = TombstoneSlotTable[str]()
        first_id = table.allocate("alpha")
        second_id = table.allocate("beta")
        table.tombstone(first_id)

        self.assertEqual(((second_id, "beta"),), tuple(table.iter_live_items()))
        self.assertEqual((TOMBSTONE, "beta"), table.raw_slots())

    def test_tombstone_slot_table_rejects_invalid_restoration_shape(self) -> None:
        with self.assertRaises(ValueError):
            TombstoneSlotTable[str](slots=("x",), next_id=0)
