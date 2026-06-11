"""Contract tests for shared events, observables, and errors."""

from __future__ import annotations

import unittest

from pygrc.core import (
    GRCError,
    GRCEvent,
    InvalidParamsError,
    InvalidStateTransitionError,
    ObservableSnapshot,
    SnapshotCompatibilityError,
    UnsupportedCapabilityError,
)


class EventsObservablesErrorsContractTest(unittest.TestCase):
    """Validate the shared event/observable/error contract surface."""

    def test_grc_event_exposes_required_shared_fields(self) -> None:
        event = GRCEvent(
            kind="spark",
            step_index=3,
            payload={"node_id": 7},
            source_family="GRCV3",
        )

        self.assertEqual("spark", event.kind)
        self.assertEqual(3, event.step_index)
        self.assertEqual({"node_id": 7}, event.payload)
        self.assertEqual("GRCV3", event.source_family)

    def test_observable_snapshot_wraps_mapping(self) -> None:
        observables = ObservableSnapshot(values={"mass": 1.0, "spark_count": 2})

        self.assertEqual({"mass": 1.0, "spark_count": 2}, observables.values)

    def test_error_types_are_explicit_and_stable(self) -> None:
        self.assertTrue(issubclass(InvalidParamsError, GRCError))
        self.assertTrue(issubclass(UnsupportedCapabilityError, GRCError))
        self.assertTrue(issubclass(SnapshotCompatibilityError, GRCError))
        self.assertTrue(issubclass(InvalidStateTransitionError, GRCError))
